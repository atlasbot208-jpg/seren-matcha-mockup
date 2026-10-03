"""Lean, rate-limited epoch pull for the SN25 actuals audit.

Same first-principles method as extract.py, cut down to fit the public archive
nodes' historical-query budget:

  * epoch blocks are computed, not searched: on SN25 they fall every 360 blocks
    from block 8,745,562 (confirmed across 1,270 epochs in the first run);
    PendingOwnerCut at E-1 is recorded so any drift is visible;
  * only the tracked coldkeys and the hotkeys they stake to are read per epoch;
    the full dividend map is read once a day for the validator landscape;
  * price and take rates are read once per UTC day;
  * calls are spread over both public archive endpoints with a pacing limit,
    and back off when the node reports its budget is exhausted.

Writes to data/raw/: epochs.csv, epoch_hotkeys.csv, epoch_positions.csv,
daily.csv, daily_divs.csv, flows.csv, flow_events.jsonl. Resumes from epochs.csv.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import bittensor as bt
from bittensor._generated import runtime_apis as api
from bittensor._generated import storage as st
from bittensor.sp_core import ss58_decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)
LOG = open(os.path.join(RAW, "audit_log.txt"), "a")
RAO = 1_000_000_000
EPOCH_ANCHOR, EPOCH_STEP = 8_745_562, 360
ENDPOINTS = ["wss://archive.chain.opentensor.ai:443", "wss://archive.sub.latent.to:443"]


def log(*a):
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] " + " ".join(str(x) for x in a)
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def num(v) -> int:
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if isinstance(v, str):
        try:
            return int(v, 0)
        except ValueError:
            return int(float(v))
    if hasattr(v, "rao"):
        return int(v.rao)
    if hasattr(v, "value"):
        return num(v.value)
    if isinstance(v, dict):
        for k in ("value", "bits", "rao"):
            if k in v:
                return num(v[k])
        if len(v) == 1:
            return num(next(iter(v.values())))
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return num(v[0])
    raise TypeError(f"cannot convert {type(v)} {v!r}")


class Pool:
    """Round-robin over archive clients, each paced, with budget back-off."""

    def __init__(self, clients, min_interval: float):
        self.clients = clients
        self.locks = [asyncio.Lock() for _ in clients]
        self.last = [0.0 for _ in clients]
        self.min_interval = min_interval
        self.i = 0
        self.calls = 0
        self.backoffs = 0

    async def call(self, method: str, *args, **kw):
        for attempt in range(40):
            idx = self.i % len(self.clients)
            self.i += 1
            async with self.locks[idx]:
                wait = self.last[idx] + self.min_interval - time.monotonic()
                if wait > 0:
                    await asyncio.sleep(wait)
                self.last[idx] = time.monotonic()
            try:
                self.calls += 1
                return await getattr(self.clients[idx], method)(*args, **kw)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "budget" in msg or "rate limit" in msg.lower() or "traffic policy" in msg:
                    self.backoffs += 1
                    self.last[idx] = time.monotonic() + 20  # rest this endpoint
                    await asyncio.sleep(2)
                    continue
                if attempt >= 6:
                    raise
                await asyncio.sleep(2 * (attempt + 1))
        raise RuntimeError(f"gave up on {method} {args[:2]}")

    async def q(self, item, params=None, block=None):
        return await self.call("query", item, params, block=block)

    async def qmap(self, item, params=None, block=None):
        return await self.call("query_map", item, params, block=block)

    async def qbatch(self, item, sets, block=None):
        return await self.call("query_batch", item, sets, block=block) if sets else []

    async def rt(self, m, params, block=None):
        return await self.call("runtime", m, params, block=block)


async def positions(p: Pool, cks, block):
    recs, accts = await asyncio.gather(
        p.rt(api.StakeInfoRuntimeApi.get_stake_info_for_coldkeys, [cks], block=block),
        p.qbatch(st.System.Account, [[c] for c in cks], block=block),
    )
    out = {}
    for _ck, plist in recs or []:
        for r in plist or []:
            out[(str(r["coldkey"]), str(r["hotkey"]), int(r["netuid"]))] = num(r["stake"])
    for c, a in zip(cks, accts):
        data = (a or {}).get("data", {}) if isinstance(a, dict) else {}
        out[(c, "FREE", -1)] = num(data.get("free", 0))
    return out


def key(pos):
    return tuple(sorted(pos.items()))


async def locate(p, cks, lo, hi, plo, phi, out, depth=0):
    if key(plo) == key(phi):
        return
    if hi - lo == 1:
        out.append((hi, plo, phi))
        return
    mid = (lo + hi) // 2
    pmid = await positions(p, cks, mid)
    await locate(p, cks, lo, mid, plo, pmid, out, depth + 1)
    await locate(p, cks, mid, hi, pmid, phi, out, depth + 1)


def ts_of(block, anchors):
    (b0, t0), (b1, t1) = anchors
    return int(t0 + (block - b0) * (t1 - t0) / (b1 - b0))


def append(path, rows, fields):
    if not rows:
        return
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-block", type=int, required=True)
    ap.add_argument("--end-block", type=int, default=0)
    ap.add_argument("--interval", type=float, default=0.55, help="min seconds between calls per endpoint")
    ap.add_argument("--max-epochs", type=int, default=0)
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(ROOT, "wallets.json")))
    n = cfg["netuid"]
    cks = list(cfg["coldkeys"])
    needles = cks + ["0x" + bytes(ss58_decode(c)).hex() for c in cks]

    clients = []
    for ep in ENDPOINTS:
        try:
            c = bt.Client(ep, fallback_endpoints=[], archive_endpoints=[])
            await c.connect()
            await c.block()
            clients.append(c)
            log("connected", ep)
        except Exception as e:  # noqa: BLE001
            log("endpoint unavailable", ep, e)
    if not clients:
        raise SystemExit("no archive endpoint reachable")
    p = Pool(clients, args.interval)

    head = await clients[0].block()
    end = args.end_block or head - 10
    t_head = num(await p.q(st.Timestamp.Now, block=end))
    t_start = num(await p.q(st.Timestamp.Now, block=args.start_block))
    anchors = ((args.start_block, t_start), (end, t_head))

    ep_path = os.path.join(RAW, "epochs.csv")
    done = set()
    if os.path.exists(ep_path):
        done = {int(r["epoch_block"]) for r in csv.DictReader(open(ep_path))}
    first = EPOCH_ANCHOR + max(0, -(-(args.start_block - EPOCH_ANCHOR) // EPOCH_STEP)) * EPOCH_STEP
    epochs = [e for e in range(first, end + 1, EPOCH_STEP) if e not in done]
    if args.max_epochs:
        epochs = epochs[: args.max_epochs]
    log(f"head {head}, range {args.start_block}..{end}, epochs to fetch {len(epochs)}, endpoints {len(clients)}")

    # hotkeys to track: everything the tracked coldkeys stake to at either end
    pos_start, pos_end = await asyncio.gather(positions(p, cks, args.start_block), positions(p, cks, end))
    hks = sorted({k[1] for k in list(pos_start) + list(pos_end) if k[2] == n})
    for ck in cks:
        hks += [str(h) for h in (await p.q(st.SubtensorModule.OwnedHotkeys, [ck], block=end)) or [] if str(h) not in hks]
    log("tracked hotkeys:", hks)
    owners = dict(zip(hks, [str(x) for x in await asyncio.gather(*(p.q(st.SubtensorModule.Owner, [h], block=end) for h in hks))]))

    # daily: price, takes, total divs map (landscape), timestamps
    days_done = set()
    dpath = os.path.join(RAW, "daily.csv")
    if os.path.exists(dpath):
        days_done = {r["date"] for r in csv.DictReader(open(dpath))}
    day_blocks = {}
    for e in range(first, end + 1, EPOCH_STEP):
        d = datetime.fromtimestamp(ts_of(e, anchors) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        day_blocks.setdefault(d, e)
    drows, ddivs = [], []
    for d, b in sorted(day_blocks.items()):
        if d in days_done:
            continue
        try:
            price, takes, dmap, ts = await asyncio.gather(
                p.rt(api.SwapRuntimeApi.current_alpha_price, [n], block=b),
                p.qbatch(st.SubtensorModule.Delegates, [[h] for h in hks], block=b),
                p.qmap(st.SubtensorModule.AlphaDividendsPerSubnet, [n], block=b),
                p.q(st.Timestamp.Now, block=b),
            )
            drows.append({"date": d, "block": b, "ts": num(ts), "alpha_price_tau": num(price) / RAO,
                          "takes": json.dumps(dict(zip(hks, [num(t) for t in takes])))})
            for hk, v in dmap or []:
                ddivs.append({"date": d, "block": b, "hotkey": str(hk), "nominator_divs_rao": num(v)})
        except Exception as e:  # noqa: BLE001
            log(f"daily {d} failed: {e}")
    append(dpath, drows, ["date", "block", "ts", "alpha_price_tau", "takes"])
    append(os.path.join(RAW, "daily_divs.csv"), ddivs, ["date", "block", "hotkey", "nominator_divs_rao"])
    log(f"daily rows: {len(drows)}; calls so far {p.calls}, backoffs {p.backoffs}")

    ep_f = ["epoch_block", "ts", "owner_cut_paid_rao", "pending_owner_cut_prev_rao", "subnet_owner", "subnet_owner_hotkey"]
    h_f = ["epoch_block", "hotkey", "owner_coldkey", "nominator_divs_rao", "root_divs_rao",
           "total_alpha_before_rao", "total_alpha_after_rao"]
    p_f = ["epoch_block", "coldkey", "hotkey", "netuid", "before_rao", "after_rao"]
    f_f = ["block", "ts", "coldkey", "hotkey", "netuid", "before_rao", "after_rao"]

    prev_E, prev_after = None, None
    t0 = time.time()
    batch = 6
    for i in range(0, len(epochs), batch):
        chunk = epochs[i: i + batch]

        async def one(E):
            pend, so, soh, divs, rdivs, tb, ta, pb, pa = await asyncio.gather(
                p.q(st.SubtensorModule.PendingOwnerCut, [n], block=E - 1),
                p.q(st.SubtensorModule.SubnetOwner, [n], block=E),
                p.q(st.SubtensorModule.SubnetOwnerHotkey, [n], block=E),
                p.qbatch(st.SubtensorModule.AlphaDividendsPerSubnet, [[n, h] for h in hks], block=E),
                p.qbatch(st.SubtensorModule.RootAlphaDividendsPerSubnet, [[n, h] for h in hks], block=E),
                p.qbatch(st.SubtensorModule.TotalHotkeyAlpha, [[h, n] for h in hks], block=E - 1),
                p.qbatch(st.SubtensorModule.TotalHotkeyAlpha, [[h, n] for h in hks], block=E),
                positions(p, cks, E - 1),
                positions(p, cks, E),
            )
            # owner cut paid at E = pending before E plus the cut added in block E (0.18 alpha/block)
            paid = num(pend) + int(num(pend) / max(EPOCH_STEP - 1, 1)) if num(pend) else 0
            ep = {"epoch_block": E, "ts": ts_of(E, anchors), "owner_cut_paid_rao": paid,
                  "pending_owner_cut_prev_rao": num(pend), "subnet_owner": str(so), "subnet_owner_hotkey": str(soh)}
            hr = [{"epoch_block": E, "hotkey": h, "owner_coldkey": owners.get(h, ""), "nominator_divs_rao": num(a),
                   "root_divs_rao": num(r), "total_alpha_before_rao": num(b), "total_alpha_after_rao": num(c)}
                  for h, a, r, b, c in zip(hks, divs, rdivs, tb, ta)]
            pr = [{"epoch_block": E, "coldkey": k[0], "hotkey": k[1], "netuid": k[2],
                   "before_rao": pb.get(k, 0), "after_rao": pa.get(k, 0)} for k in sorted(set(pb) | set(pa))]
            return ep, hr, pr, pb, pa

        res = await asyncio.gather(*(one(E) for E in chunk), return_exceptions=True)
        eps, hs, ps, fl, evs = [], [], [], [], []
        for E, r in zip(chunk, res):
            if isinstance(r, Exception):
                log(f"epoch {E} failed: {type(r).__name__}: {r}")
                prev_E, prev_after = None, None
                continue
            ep, hr, pr, pb, pa = r
            eps.append(ep)
            hs.extend(hr)
            ps.extend(pr)
            if prev_after is not None and key(prev_after) != key(pb):
                found = []
                try:
                    await locate(p, cks, prev_E, E - 1, prev_after, pb, found)
                except Exception as e:  # noqa: BLE001
                    log(f"locate {prev_E}..{E - 1} failed: {e}")
                for b, plo, phi in found:
                    tsb = ts_of(b, anchors)
                    for k in sorted(set(plo) | set(phi)):
                        if plo.get(k, 0) != phi.get(k, 0):
                            fl.append({"block": b, "ts": tsb, "coldkey": k[0], "hotkey": k[1], "netuid": k[2],
                                       "before_rao": plo.get(k, 0), "after_rao": phi.get(k, 0)})
                    try:
                        h = await p.call("_block_hash", b)
                        raw = await clients[0]._substrate.events(h)
                        keep = [e for e in raw or [] if any(nd in json.dumps(e, default=str) for nd in needles)]
                    except Exception as e:  # noqa: BLE001
                        keep = [f"ERROR {e}"]
                    evs.append({"block": b, "ts": tsb, "events": keep})
            # flows inside the epoch block itself show up as a residual in build_audit.py
            prev_E, prev_after = E, pa
        append(ep_path, eps, ep_f)
        append(os.path.join(RAW, "epoch_hotkeys.csv"), hs, h_f)
        append(os.path.join(RAW, "epoch_positions.csv"), ps, p_f)
        append(os.path.join(RAW, "flows.csv"), fl, f_f)
        if evs:
            with open(os.path.join(RAW, "flow_events.jsonl"), "a") as f:
                for e in evs:
                    f.write(json.dumps(e, default=str) + "\n")
        done_n = i + len(chunk)
        el = time.time() - t0
        log(f"epochs {done_n}/{len(epochs)} in {el:.0f}s, calls {p.calls}, backoffs {p.backoffs}, flows+{len(fl)}")
    for c in clients:
        await c.close()
    log("=== audit pull complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:  # noqa: BLE001
        log(f"FATAL {type(e).__name__}: {e}\n{traceback.format_exc()}")
        sys.exit(1)
