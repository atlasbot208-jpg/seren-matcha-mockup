"""Pull SN25 revenue data straight from Bittensor archive state, epoch by epoch.

Why per epoch: on dTAO the chain credits nothing between epochs. The owner cut
and validator dividends accrue in Pending* storage every block and are paid in
one go when the subnet's epoch fires (run_coinbase.rs -> drain_pending ->
distribute_dividends_and_incentives). So for every epoch block E we read:

  * the state just before (E-1) and just after (E) for every tracked coldkey's
    stake positions and free TAO, which gives *measured* income at E;
  * PendingOwnerCut at E-1 plus the cut added at E, which is the owner cut paid;
  * AlphaDividendsPerSubnet / RootAlphaDividendsPerSubnet at E, which hold each
    hotkey's post-take nominator dividends for that epoch (cleared every epoch);
  * each paying hotkey's take rate, owner coldkey and pool size before E, which
    lets us rebuild the take vs nominator split from first principles;
  * the alpha price in TAO at E.

Between epochs any change in a tracked coldkey's stake or free balance must be a
flow (stake add/remove/move/transfer, TAO transfer, fee). Those intervals are
bisected down to the exact block and that block's events are saved.

Outputs (CSV / JSONL) go to data/raw/. Re-running resumes from the last epoch.
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
U16 = 65535
RAO = 1_000_000_000

LOG_FH = open(os.path.join(RAW, "extract_log.txt"), "a")


def log(*a):
    msg = " ".join(str(x) for x in a)
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG_FH.write(line + "\n")
    LOG_FH.flush()


def num(v) -> int:
    """Best-effort conversion of a decoded SCALE value to int (rao / raw units)."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int,)):
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
        for k in ("value", "bits", "rao", "0"):
            if k in v:
                return num(v[k])
        if len(v) == 1:
            return num(next(iter(v.values())))
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return num(v[0])
    raise TypeError(f"cannot convert {type(v)} {v!r} to int")


def jdump(o) -> str:
    return json.dumps(o, default=str, sort_keys=True)


class Chain:
    def __init__(self, client, concurrency: int = 12):
        self.c = client
        self.sem = asyncio.Semaphore(concurrency)
        self.ts_cache: dict[int, int] = {}
        self.owner_cache: dict[str, str] = {}

    async def _retry(self, fn, *args, tries=5, **kw):
        for i in range(tries):
            try:
                async with self.sem:
                    return await fn(*args, **kw)
            except Exception as e:  # noqa: BLE001
                if i == tries - 1:
                    raise
                await asyncio.sleep(1.5 * (i + 1))
                log(f"retry {fn.__name__} {args[:2]} after {type(e).__name__}: {e}")

    async def q(self, item, params=None, block=None):
        return await self._retry(self.c.query, item, params, block=block)

    async def qmap(self, item, params=None, block=None):
        return await self._retry(self.c.query_map, item, params, block=block)

    async def qbatch(self, item, param_sets, block=None):
        if not param_sets:
            return []
        return await self._retry(self.c.query_batch, item, param_sets, block=block)

    async def rt(self, method, params, block=None):
        return await self._retry(self.c.runtime, method, params, block=block)

    async def ts(self, block: int) -> int:
        if block not in self.ts_cache:
            self.ts_cache[block] = num(await self.q(st.Timestamp.Now, block=block))
        return self.ts_cache[block]

    async def head(self) -> int:
        return await self.c.block()

    async def block_for_time(self, unix_ms: int, lo: int, hi: int) -> int:
        """First block with timestamp >= unix_ms (binary search)."""
        while lo < hi:
            mid = (lo + hi) // 2
            if await self.ts(mid) < unix_ms:
                lo = mid + 1
            else:
                hi = mid
        return lo

    async def since_step(self, netuid: int, block: int) -> int:
        return num(await self.q(st.SubtensorModule.BlocksSinceLastStep, [netuid], block=block))

    async def hotkey_owner(self, hotkey: str, block: int) -> str:
        if hotkey not in self.owner_cache:
            self.owner_cache[hotkey] = str(await self.q(st.SubtensorModule.Owner, [hotkey], block=block))
        return self.owner_cache[hotkey]

    async def positions(self, coldkeys: list[str], block: int) -> dict:
        """{(coldkey, hotkey, netuid): stake_rao} plus {(coldkey,'FREE',-1): free_rao}."""
        recs = await self.rt(api.StakeInfoRuntimeApi.get_stake_info_for_coldkeys, [coldkeys], block=block)
        out = {}
        for ck, plist in recs or []:
            for r in plist or []:
                out[(str(r["coldkey"]), str(r["hotkey"]), int(r["netuid"]))] = num(r["stake"])
        accts = await self.qbatch(st.System.Account, [[ck] for ck in coldkeys], block=block)
        for ck, a in zip(coldkeys, accts):
            data = (a or {}).get("data", {}) if isinstance(a, dict) else {}
            out[(ck, "FREE", -1)] = num(data.get("free", 0))
            out[(ck, "RESERVED", -1)] = num(data.get("reserved", 0))
        return out

    async def alpha_price(self, netuid: int, block: int) -> float:
        try:
            p = await self.rt(api.SwapRuntimeApi.current_alpha_price, [netuid], block=block)
            return num(p) / RAO
        except Exception as e:  # noqa: BLE001
            tao, ain = await asyncio.gather(
                self.q(st.SubtensorModule.SubnetTAO, [netuid], block=block),
                self.q(st.SubtensorModule.SubnetAlphaIn, [netuid], block=block),
            )
            log(f"price fallback at {block}: {e}")
            return num(tao) / max(num(ain), 1)

    async def events_for(self, block: int, needles: list[str]) -> list:
        h = await self._retry(self.c._substrate.block_hash, block)
        evs = await self._retry(self.c._substrate.events, h)
        keep = []
        for e in evs or []:
            s = jdump(e)
            if any(n in s for n in needles):
                keep.append(e)
        return keep


# ---------------------------------------------------------------------------


async def probe(ch: Chain, cfg: dict, block: int, tag: str):
    """Snapshot of who's who on the subnet at one block (for orientation)."""
    n = cfg["netuid"]
    out: dict = {"block": block, "ts": await ch.ts(block)}

    async def safe(name, coro):
        try:
            out[name] = await coro
        except Exception as e:  # noqa: BLE001
            out[name] = f"ERROR {type(e).__name__}: {e}"

    await safe("subnet_owner", ch.q(st.SubtensorModule.SubnetOwner, [n], block=block))
    await safe("subnet_owner_hotkey", ch.q(st.SubtensorModule.SubnetOwnerHotkey, [n], block=block))
    await safe("subnet_owner_cut_u16", ch.q(st.SubtensorModule.SubnetOwnerCut, None, block=block))
    await safe("owner_cut_enabled", ch.q(st.SubtensorModule.OwnerCutEnabled, [n], block=block))
    await safe("owner_cut_auto_lock", ch.q(st.SubtensorModule.OwnerCutAutoLockEnabled, [n], block=block))
    await safe("recycle_or_burn", ch.q(st.SubtensorModule.RecycleOrBurn, [n], block=block))
    await safe("tempo", ch.q(st.SubtensorModule.Tempo, [n], block=block))
    await safe("alpha_out_emission", ch.q(st.SubtensorModule.SubnetAlphaOutEmission, [n], block=block))
    await safe("miner_burned", ch.q(st.SubtensorModule.MinerBurned, [n], block=block))
    await safe("alpha_price_tau", ch.alpha_price(n, block))
    await safe("subnet_lease", ch.q(st.SubtensorModule.SubnetUidToLeaseId, [n], block=block))
    owned = {}
    for ck in cfg["coldkeys"]:
        try:
            owned[ck] = [str(h) for h in (await ch.q(st.SubtensorModule.OwnedHotkeys, [ck], block=block)) or []]
        except Exception as e:  # noqa: BLE001
            owned[ck] = f"ERROR {e}"
    out["owned_hotkeys"] = owned
    try:
        pos = await ch.positions(list(cfg["coldkeys"]), block)
        out["positions"] = [
            {"coldkey": k[0], "hotkey": k[1], "netuid": k[2], "amount": v / RAO} for k, v in sorted(pos.items())
        ]
    except Exception as e:  # noqa: BLE001
        out["positions"] = f"ERROR {e}"
    # neurons on the subnet
    try:
        neurons = await ch.rt(api.NeuronInfoRuntimeApi.get_neurons_lite, [n], block=block)
        rows = []
        for x in neurons or []:
            rows.append(
                {
                    k: (str(x[k]) if k in ("hotkey", "coldkey") else x[k])
                    for k in x
                    if k
                    in (
                        "uid", "hotkey", "coldkey", "validator_permit", "dividends", "incentive",
                        "emission", "trust", "validator_trust", "consensus", "rank", "active",
                    )
                }
                | {"stake_raw": x.get("stake")}
            )
        out["neurons"] = rows
        hks = sorted({r["hotkey"] for r in rows if r.get("validator_permit")})
    except Exception as e:  # noqa: BLE001
        out["neurons"] = f"ERROR {type(e).__name__}: {e}"
        hks = []
    # take, children and parents for validators and tracked-owned hotkeys
    extra = set(hks)
    for v in owned.values():
        if isinstance(v, list):
            extra.update(v)
    info = {}
    for hk in sorted(extra):
        d = {}
        for name, coro in (
            ("take_u16", ch.q(st.SubtensorModule.Delegates, [hk], block=block)),
            ("owner", ch.q(st.SubtensorModule.Owner, [hk], block=block)),
            ("children", ch.q(st.SubtensorModule.ChildKeys, [hk, n], block=block)),
            ("parents", ch.q(st.SubtensorModule.ParentKeys, [hk, n], block=block)),
            ("childkey_take", ch.q(st.SubtensorModule.ChildkeyTake, [hk, n], block=block)),
            ("total_alpha", ch.q(st.SubtensorModule.TotalHotkeyAlpha, [hk, n], block=block)),
            ("root_stake", ch.q(st.SubtensorModule.TotalHotkeyAlpha, [hk, 0], block=block)),
        ):
            try:
                d[name] = await coro
            except Exception as e:  # noqa: BLE001
                d[name] = f"ERROR {e}"
        info[hk] = d
    out["hotkeys"] = info
    try:
        out["alpha_divs"] = [(str(k), v) for k, v in await ch.qmap(st.SubtensorModule.AlphaDividendsPerSubnet, [n], block=block)]
    except Exception as e:  # noqa: BLE001
        out["alpha_divs"] = f"ERROR {e}"
    with open(os.path.join(RAW, f"probe_{tag}.json"), "w") as f:
        f.write(json.dumps(out, default=str, indent=1))
    log(f"probe {tag} written at block {block}")
    return out


async def owner_history(ch: Chain, cfg: dict, start: int, end: int):
    """SubnetOwner / SubnetOwnerHotkey sampled every ~6h, plus exact change blocks."""
    n = cfg["netuid"]
    step = 1800

    async def state(b):
        o, h = await asyncio.gather(
            ch.q(st.SubtensorModule.SubnetOwner, [n], block=b),
            ch.q(st.SubtensorModule.SubnetOwnerHotkey, [n], block=b),
        )
        return (str(o), str(h))

    samples = list(range(start, end, step)) + [end]
    states = await asyncio.gather(*(state(b) for b in samples))
    rows = []
    for i, (b, s) in enumerate(zip(samples, states)):
        if i == 0 or s != states[i - 1]:
            lo, hi = (samples[i - 1], b) if i else (b, b)
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if await state(mid) == s:
                    hi = mid
                else:
                    lo = mid
            rows.append({"from_block": hi, "ts": await ch.ts(hi), "owner_coldkey": s[0], "owner_hotkey": s[1]})
    with open(os.path.join(RAW, "owner_history.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from_block", "ts", "owner_coldkey", "owner_hotkey"])
        w.writeheader()
        w.writerows(rows)
    log(f"owner history: {len(rows)} segments")
    return rows


async def find_epochs(ch: Chain, netuid: int, start: int, end: int, known: list[int]) -> list[int]:
    """Exact epoch blocks in [start, end] using BlocksSinceLastStep (0 at the epoch block)."""
    tempo = num(await ch.q(st.SubtensorModule.Tempo, [netuid], block=end)) or 360
    epochs = [e for e in known if start <= e <= end]
    if epochs:
        e = epochs[-1]
    else:
        e = start - await ch.since_step(netuid, start)
        if e >= start:
            epochs.append(e)
    t0 = time.time()
    while True:
        b = e + tempo + 1
        if b > end:
            break
        nxt = None
        while b <= end:
            s = await ch.since_step(netuid, b)
            cand = b - s
            if cand > e:
                nxt = cand
                break
            b += 1 if s == 0 else 2
        if nxt is None:
            break
        epochs.append(nxt)
        e = nxt
        if len(epochs) % 50 == 0:
            log(f"  epochs found: {len(epochs)} (at {e}, {time.time() - t0:.0f}s)")
    return epochs


async def epoch_record(ch: Chain, cfg: dict, E: int, tracked_hotkeys: set[str]):
    n = cfg["netuid"]
    cks = list(cfg["coldkeys"])
    (
        ts, price, pend_cut, out_em, cut_u16, cut_enabled, so, soh,
        divs, rdivs, pos_b, pos_a, miner_burned,
    ) = await asyncio.gather(
        ch.ts(E),
        ch.alpha_price(n, E),
        ch.q(st.SubtensorModule.PendingOwnerCut, [n], block=E - 1),
        ch.q(st.SubtensorModule.SubnetAlphaOutEmission, [n], block=E),
        ch.q(st.SubtensorModule.SubnetOwnerCut, None, block=E),
        ch.q(st.SubtensorModule.OwnerCutEnabled, [n], block=E),
        ch.q(st.SubtensorModule.SubnetOwner, [n], block=E),
        ch.q(st.SubtensorModule.SubnetOwnerHotkey, [n], block=E),
        ch.qmap(st.SubtensorModule.AlphaDividendsPerSubnet, [n], block=E),
        ch.qmap(st.SubtensorModule.RootAlphaDividendsPerSubnet, [n], block=E),
        ch.positions(cks, E - 1),
        ch.positions(cks, E),
        ch.q(st.SubtensorModule.MinerBurned, [n], block=E),
    )
    out_em = num(out_em)
    cut_frac = num(cut_u16) / U16
    owner_cut_paid = num(pend_cut) + (int(out_em * cut_frac) if cut_enabled is not False else 0)
    div_map = {str(k): num(v) for k, v in divs or []}
    rdiv_map = {str(k): num(v) for k, v in rdivs or []}
    hks = sorted(set(div_map) | set(rdiv_map) | tracked_hotkeys | {k[1] for k in pos_b if k[2] == n} | {str(soh)})
    takes, tot_b, tot_a = await asyncio.gather(
        ch.qbatch(st.SubtensorModule.Delegates, [[h] for h in hks], block=E),
        ch.qbatch(st.SubtensorModule.TotalHotkeyAlpha, [[h, n] for h in hks], block=E - 1),
        ch.qbatch(st.SubtensorModule.TotalHotkeyAlpha, [[h, n] for h in hks], block=E),
    )
    owners = await asyncio.gather(*(ch.hotkey_owner(h, E) for h in hks))
    ep = {
        "epoch_block": E,
        "ts": ts,
        "alpha_price_tau": price,
        "owner_cut_paid_rao": owner_cut_paid,
        "pending_owner_cut_prev_rao": num(pend_cut),
        "alpha_out_emission_rao": out_em,
        "owner_cut_frac": cut_frac,
        "subnet_owner": str(so),
        "subnet_owner_hotkey": str(soh),
        "miner_burned": str(miner_burned),
        "total_nominator_divs_rao": sum(div_map.values()),
        "total_root_divs_rao": sum(rdiv_map.values()),
    }
    hrows = []
    for h, tk, tb, ta, ow in zip(hks, takes, tot_b, tot_a, owners):
        hrows.append(
            {
                "epoch_block": E,
                "hotkey": h,
                "owner_coldkey": ow,
                "take_u16": num(tk),
                "nominator_divs_rao": div_map.get(h, 0),
                "root_divs_rao": rdiv_map.get(h, 0),
                "total_alpha_before_rao": num(tb),
                "total_alpha_after_rao": num(ta),
            }
        )
    prow = []
    for k in sorted(set(pos_b) | set(pos_a)):
        prow.append(
            {
                "epoch_block": E,
                "coldkey": k[0],
                "hotkey": k[1],
                "netuid": k[2],
                "before_rao": pos_b.get(k, 0),
                "after_rao": pos_a.get(k, 0),
            }
        )
    return ep, hrows, prow, pos_b, pos_a


def state_key(pos: dict, ignore_free: bool = False) -> tuple:
    return tuple(sorted((k, v) for k, v in pos.items() if not (ignore_free and k[1] in ("FREE", "RESERVED"))))


async def locate_changes(ch: Chain, cks: list[str], lo: int, hi: int, pos_lo: dict, pos_hi: dict, out: list):
    """Find every block b in (lo, hi] where tracked state differs from b-1."""
    if state_key(pos_lo) == state_key(pos_hi):
        return
    if hi - lo == 1:
        diffs = []
        for k in sorted(set(pos_lo) | set(pos_hi)):
            a, b = pos_lo.get(k, 0), pos_hi.get(k, 0)
            if a != b:
                diffs.append({"coldkey": k[0], "hotkey": k[1], "netuid": k[2], "before_rao": a, "after_rao": b})
        out.append((hi, diffs))
        return
    mid = (lo + hi) // 2
    pos_mid = await ch.positions(cks, mid)
    await asyncio.gather(
        locate_changes(ch, cks, lo, mid, pos_lo, pos_mid, out),
        locate_changes(ch, cks, mid, hi, pos_mid, pos_hi, out),
    )


def append_csv(path, rows, fields):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-08-01T00:00:00Z")
    ap.add_argument("--end", default="")
    ap.add_argument("--network", default="archive")
    ap.add_argument("--max-epochs", type=int, default=0, help="cap for a smoke test")
    ap.add_argument("--skip-flows", action="store_true")
    ap.add_argument("--concurrency", type=int, default=12)
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(ROOT, "wallets.json")))
    n = cfg["netuid"]
    cks = list(cfg["coldkeys"])
    needles = cks + ["0x" + bytes(ss58_decode(c)).hex() for c in cks]

    log(f"=== run start, bittensor {getattr(bt, '__version__', '?')}, network={args.network}")
    client = bt.Client(args.network)
    await client.connect()
    ch = Chain(client, args.concurrency)
    head = await ch.head()
    log(f"head block {head}, spec {await client.spec_version()}")

    start_ms = int(datetime.fromisoformat(args.start.replace("Z", "+00:00")).timestamp() * 1000)
    head_ts = await ch.ts(head)
    lo_guess = max(1, head - int((head_ts - start_ms) / 12000) - 20000)
    start = await ch.block_for_time(start_ms, lo_guess, head)
    if args.end:
        end_ms = int(datetime.fromisoformat(args.end.replace("Z", "+00:00")).timestamp() * 1000)
        end = await ch.block_for_time(end_ms, start, head)
    else:
        end = head - 10
    log(f"range blocks {start}..{end}")

    meta = {"run_at": datetime.now(timezone.utc).isoformat(), "head": head, "start_block": start,
            "end_block": end, "start": args.start, "netuid": n, "coldkeys": cfg["coldkeys"]}
    json.dump(meta, open(os.path.join(RAW, "meta.json"), "w"), indent=1)

    for tag, b in (("head", end), ("start", start)):
        try:
            await probe(ch, cfg, b, tag)
        except Exception as e:  # noqa: BLE001
            log(f"probe {tag} failed: {e}\n{traceback.format_exc()}")

    try:
        await owner_history(ch, cfg, start, end)
    except Exception as e:  # noqa: BLE001
        log(f"owner history failed: {e}\n{traceback.format_exc()}")

    ep_path = os.path.join(RAW, "epochs.csv")
    known = []
    if os.path.exists(ep_path):
        known = sorted({int(r["epoch_block"]) for r in csv.DictReader(open(ep_path))})
        log(f"resuming: {len(known)} epochs already recorded (last {known[-1] if known else None})")
    epochs = await find_epochs(ch, n, start, end, known)
    todo = [e for e in epochs if e not in set(known)]
    if args.max_epochs:
        todo = todo[: args.max_epochs]
    log(f"epochs in range: {len(epochs)}, to fetch: {len(todo)}")

    tracked_hotkeys: set[str] = set()
    for ck in cks:
        try:
            tracked_hotkeys.update(str(h) for h in (await ch.q(st.SubtensorModule.OwnedHotkeys, [ck], block=end)) or [])
        except Exception:  # noqa: BLE001
            pass

    ep_fields = ["epoch_block", "ts", "alpha_price_tau", "owner_cut_paid_rao", "pending_owner_cut_prev_rao",
                 "alpha_out_emission_rao", "owner_cut_frac", "subnet_owner", "subnet_owner_hotkey",
                 "miner_burned", "total_nominator_divs_rao", "total_root_divs_rao"]
    h_fields = ["epoch_block", "hotkey", "owner_coldkey", "take_u16", "nominator_divs_rao", "root_divs_rao",
                "total_alpha_before_rao", "total_alpha_after_rao"]
    p_fields = ["epoch_block", "coldkey", "hotkey", "netuid", "before_rao", "after_rao"]
    f_fields = ["block", "ts", "coldkey", "hotkey", "netuid", "before_rao", "after_rao"]

    prev_after = None
    prev_E = None
    if known and todo and todo[0] > known[-1]:
        prev_E = known[-1]
        prev_after = await ch.positions(cks, prev_E)
    t0 = time.time()
    batch = 24
    for i in range(0, len(todo), batch):
        chunk = todo[i: i + batch]
        res = await asyncio.gather(*(epoch_record(ch, cfg, E, tracked_hotkeys) for E in chunk), return_exceptions=True)
        eps, hs, ps = [], [], []
        flow_rows, events_out = [], []
        for E, r in zip(chunk, res):
            if isinstance(r, Exception):
                log(f"epoch {E} failed: {type(r).__name__}: {r}")
                prev_after, prev_E = None, None
                continue
            ep, hrows, prow, pos_b, pos_a = r
            eps.append(ep)
            hs.extend(hrows)
            ps.extend(prow)
            # flows between previous epoch and this one
            if not args.skip_flows and prev_after is not None and prev_E is not None and E - 1 > prev_E:
                found: list = []
                try:
                    await locate_changes(ch, cks, prev_E, E - 1, prev_after, pos_b, found)
                except Exception as e:  # noqa: BLE001
                    log(f"flow locate {prev_E}-{E} failed: {e}")
                for b, diffs in sorted(found):
                    tsb = await ch.ts(b)
                    for d in diffs:
                        flow_rows.append({"block": b, "ts": tsb, **d})
                    try:
                        evs = await ch.events_for(b, needles)
                    except Exception as e:  # noqa: BLE001
                        evs = [f"ERROR {e}"]
                    events_out.append({"block": b, "ts": tsb, "events": evs})
            prev_after, prev_E = pos_a, E
        append_csv(ep_path, eps, ep_fields)
        append_csv(os.path.join(RAW, "epoch_hotkeys.csv"), hs, h_fields)
        append_csv(os.path.join(RAW, "epoch_positions.csv"), ps, p_fields)
        if flow_rows:
            append_csv(os.path.join(RAW, "flows.csv"), flow_rows, f_fields)
        if events_out:
            with open(os.path.join(RAW, "flow_events.jsonl"), "a") as f:
                for e in events_out:
                    f.write(jdump(e) + "\n")
        done = i + len(chunk)
        rate = done / max(time.time() - t0, 1)
        log(f"epochs {done}/{len(todo)} ({rate:.2f}/s), flows so far this chunk {len(flow_rows)}")

    # Flows that happen inside the epoch block itself are caught in build.py by
    # comparing measured vs modelled income; save events for epoch blocks where
    # the tracked coldkeys' free balance changed (fees => a tx in that block).
    await client.close()
    log("=== run complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:  # noqa: BLE001
        log(f"FATAL {type(e).__name__}: {e}\n{traceback.format_exc()}")
        sys.exit(1)
