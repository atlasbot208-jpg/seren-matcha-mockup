"""Monthly SN25 actuals for the JV audit, from the lean epoch pull.

Income per epoch follows the chain's payout rule (run_coinbase.rs):
  owner cut       credited to (owner hotkey, owner coldkey) at the epoch
  validator take  take x gross alpha dividends on hotkeys the JV owns
                  (AlphaDividendsPerSubnet stores the post-take amount)
  staking yield   the JV's pro-rata share of each hotkey's post-take dividends
and is reconciled every epoch against the measured change in the JV's stake.
"""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DER = os.path.join(ROOT, "data", "derived")
os.makedirs(DER, exist_ok=True)
RAO = 1e9
U16 = 65535


def rows(name):
    p = os.path.join(RAW, name)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def day(ts):
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def write(name, data, fields=None):
    if not data:
        return
    fields = fields or list(data[0])
    with open(os.path.join(DER, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)


def main():
    cfg = json.load(open(os.path.join(ROOT, "wallets.json")))
    netuid, tracked = cfg["netuid"], set(cfg["coldkeys"])

    daily = {r["date"]: r for r in rows("daily.csv")}
    takes_by_day = {d: json.loads(r["takes"]) for d, r in daily.items()}
    price_by_day = {d: float(r["alpha_price_tau"]) for d, r in daily.items()}
    usd = {r["date"]: float(r["close"]) for r in rows("tao_usd_daily.csv")}

    epochs = {int(r["epoch_block"]): r for r in rows("epochs.csv")}
    hk = defaultdict(dict)
    for r in rows("epoch_hotkeys.csv"):
        hk[int(r["epoch_block"])][r["hotkey"]] = r
    pos = defaultdict(list)
    for r in rows("epoch_positions.csv"):
        pos[int(r["epoch_block"])].append(r)

    def take_frac(d, h):
        t = takes_by_day.get(d, {})
        if h in t:
            return t[h] / U16
        # nearest earlier day
        for dd in sorted(takes_by_day, reverse=True):
            if dd <= d and h in takes_by_day[dd]:
                return takes_by_day[dd][h] / U16
        return 11796 / U16

    out = []
    for E in sorted(epochs):
        ep = epochs[E]
        d = day(ep["ts"])
        rec = defaultdict(float)
        rec.update({"epoch_block": E, "date": d, "price_tau": price_by_day.get(d, ""), "tao_usd": usd.get(d, "")})
        owner_ck, owner_hk, oc_paid = ep["subnet_owner"], ep["subnet_owner_hotkey"], int(ep["owner_cut_paid_rao"])
        for p in pos.get(E, []):
            ck, h, n = p["coldkey"], p["hotkey"], int(p["netuid"])
            if ck not in tracked:
                continue
            b, a = int(p["before_rao"]), int(p["after_rao"])
            if h == "FREE":
                rec["free_tao"] += a / RAO
                continue
            if n != netuid:
                rec["other_subnets_alpha"] += a / RAO
                continue
            rec["stake_before"] += b / RAO
            rec["stake_after"] += a / RAO
            r = hk.get(E, {}).get(h)
            oc = oc_paid if (h == owner_hk and ck == owner_ck) else 0
            tk_a = tk_r = share = own_take = ext_take = 0.0
            if r:
                nom, rdiv = int(r["nominator_divs_rao"]), int(r["root_divs_rao"])
                tf = take_frac(d, h)
                owns = r["owner_coldkey"] == ck
                gross = nom / (1 - tf)
                tk_a = gross - nom if owns else 0.0
                tk_r = (rdiv / (1 - tf) - rdiv) if owns else 0.0
                denom = int(r["total_alpha_after_rao"]) - nom
                share = nom * (b + oc + tk_a) / denom if (nom and denom > 0) else 0.0
                tb = int(r["total_alpha_before_rao"])
                own_frac = b / tb if tb else 0.0
                own_take, ext_take = tk_a * own_frac, tk_a * (1 - own_frac) + tk_r
            rec["owner_emissions"] += oc / RAO
            rec["validator_take"] += (tk_a + tk_r) / RAO
            rec["staking_yield"] += share / RAO
            rec["take_on_own_stake"] += own_take / RAO
            rec["take_on_external_stake"] += ext_take / RAO
            rec["measured"] += (a - b) / RAO
        rec["total_income"] = rec["owner_emissions"] + rec["validator_take"] + rec["staking_yield"]
        rec["residual"] = rec["measured"] - rec["total_income"]
        out.append(dict(rec))

    lines = ["owner_emissions", "staking_yield", "validator_take", "take_on_own_stake", "take_on_external_stake",
             "total_income", "measured", "residual"]
    write("audit_epochs.csv", out, ["epoch_block", "date", "price_tau", "tao_usd", "stake_before", "stake_after",
                                    "free_tao", *lines])

    # flows between epochs
    flows = rows("flows.csv")
    ev = {}
    p = os.path.join(RAW, "flow_events.jsonl")
    if os.path.exists(p):
        for line in open(p):
            e = json.loads(line)
            ev[int(e["block"])] = e["events"]
    fl = []
    for f in flows:
        if f["coldkey"] not in tracked:
            continue
        b = int(f["block"])
        delta = (int(f["after_rao"]) - int(f["before_rao"])) / RAO
        fl.append({"block": b, "date": day(f["ts"]), "hotkey": f["hotkey"], "netuid": f["netuid"],
                   "unit": "TAO" if f["hotkey"] == "FREE" else "alpha", "delta": delta,
                   "events": summarise(ev.get(b, []), tracked)})
    write("audit_flows.csv", fl)

    # monthly
    monthly = {}
    for r in out:
        m = r["date"][:7]
        M = monthly.setdefault(m, defaultdict(float))
        M["month"] = m
        M["epochs"] += 1
        M.setdefault("first_date", r["date"])
        M["last_date"] = r["date"]
        M.setdefault("opening_stake", r["stake_before"])
        M["closing_stake"] = r["stake_after"]
        for k in lines:
            M[k] += r[k]
        if r["price_tau"] != "" and r["tao_usd"] != "":
            px = float(r["price_tau"]) * float(r["tao_usd"])
            M["_px_sum"] += px
            M["_px_n"] += 1
            M["total_income_usd"] += r["total_income"] * px
    for f in fl:
        m = f["date"][:7]
        if m in monthly:
            key = "alpha_flows" if f["unit"] == "alpha" and str(f["netuid"]) == str(netuid) else "other_flows"
            monthly[m][key] += f["delta"]
    mlist = []
    for m in sorted(monthly):
        M = monthly[m]
        M["avg_alpha_usd"] = M["_px_sum"] / M["_px_n"] if M["_px_n"] else ""
        M["unexplained"] = M["closing_stake"] - M["opening_stake"] - M["total_income"] - M["alpha_flows"]
        mlist.append({k: v for k, v in M.items() if not k.startswith("_")})
    write("audit_monthly.csv", mlist)
    json.dump(mlist, open(os.path.join(DER, "audit_monthly.json"), "w"), indent=1, default=str)
    for M in mlist:
        print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in M.items()}))
    print("max |residual| per epoch:", max((abs(r["residual"]) for r in out), default=0))


def summarise(evs, tracked):
    parts = []
    for e in evs or []:
        if isinstance(e, str):
            parts.append(e)
            continue
        ev = e.get("event", e) if isinstance(e, dict) else e
        mod = ev.get("module_id") or ev.get("module") or ""
        name = ev.get("event_id") or ev.get("name") or ""
        attrs = ev.get("attributes") or ev.get("params") or {}
        if (mod, name) in (("TransactionPayment", "TransactionFeePaid"), ("System", "ExtrinsicSuccess")):
            continue
        parts.append(f"{mod}.{name} {json.dumps(attrs, default=str)[:500]}")
    return " | ".join(parts)


if __name__ == "__main__":
    main()
