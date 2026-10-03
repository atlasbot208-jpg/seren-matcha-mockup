"""Turn raw epoch pulls into SN25 revenue lines, reconciliations and flows.

Revenue is built two ways and both must agree:

  MODELLED (from the chain's own payout rule, run_coinbase.rs):
    owner cut        -> PendingOwnerCut drained at the epoch, credited to
                        (subnet owner hotkey, subnet owner coldkey)
    validator take   -> take_rate x alpha dividends on every hotkey the tracked
                        coldkeys own (AlphaDividendsPerSubnet stores the
                        post-take nominator amount, so gross = nom / (1 - take));
                        also take on root dividends paid on this subnet
    nominator yield  -> each tracked position's pro-rata share of the hotkey's
                        nominator dividends: nom x (stake + credits already
                        landed this epoch) / (pool after - nom)

  MEASURED: stake after the epoch block minus stake just before it.

The residual (measured - modelled) is reported per epoch; anything material
means a transfer landed in the epoch block itself or the model is missing a term.

Two presentations of the same total are produced:
  protocol view  : how the chain credits it (take vs nominator share)
  economic view  : take earned on *other people's* stake is the validator
                   business; take on our own stake is just our own staking
                   return routed through our validator, so it sits in yield.
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


def day_of(ts_ms) -> str:
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def write(name, data, fields=None):
    if not data:
        return
    fields = fields or list(data[0].keys())
    with open(os.path.join(DER, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)


def main():
    cfg = json.load(open(os.path.join(ROOT, "wallets.json")))
    netuid = cfg["netuid"]
    tracked = set(cfg["coldkeys"])
    labels = {**cfg.get("labels", {}), **cfg["coldkeys"]}

    epochs = {int(r["epoch_block"]): r for r in rows("epochs.csv")}
    hk_rows = defaultdict(dict)
    for r in rows("epoch_hotkeys.csv"):
        hk_rows[int(r["epoch_block"])][r["hotkey"]] = r
    pos_rows = defaultdict(list)
    for r in rows("epoch_positions.csv"):
        pos_rows[int(r["epoch_block"])].append(r)

    usd = {r["date"]: float(r["close"]) for r in rows("tao_usd_daily.csv")}

    per_epoch = []
    landscape = defaultdict(lambda: defaultdict(float))
    for E in sorted(epochs):
        ep = epochs[E]
        price = float(ep["alpha_price_tau"])
        d = day_of(ep["ts"])
        tao_usd = usd.get(d)
        owner_ck, owner_hk = ep["subnet_owner"], ep["subnet_owner_hotkey"]
        owner_cut = int(ep["owner_cut_paid_rao"])
        hks = hk_rows.get(E, {})

        for h, r in hks.items():
            nom = int(r["nominator_divs_rao"])
            rdiv = int(r["root_divs_rao"])
            tf = int(r["take_u16"]) / U16
            gross = nom / (1 - tf) if tf < 1 else nom
            L = landscape[h]
            L["epochs_paid"] += 1 if (nom or rdiv) else 0
            L["gross_alpha_divs"] += gross / RAO
            L["take_alpha"] += (gross - nom) / RAO
            L["root_divs"] += rdiv / RAO
            L["take_on_root"] += (rdiv / (1 - tf) - rdiv) / RAO if tf < 1 else 0
            L["take_rate"] = tf
            L["pool_alpha_last"] = int(r["total_alpha_after_rao"]) / RAO
            L["owner_coldkey"] = r["owner_coldkey"]

        rec = defaultdict(float)
        rec.update({"epoch_block": E, "ts": int(ep["ts"]), "date": d, "alpha_price_tau": price,
                    "tao_usd": tao_usd or ""})
        for p in pos_rows.get(E, []):
            ck, h, n = p["coldkey"], p["hotkey"], int(p["netuid"])
            if ck not in tracked:
                continue
            before, after = int(p["before_rao"]), int(p["after_rao"])
            if h == "FREE":
                rec["free_tao_after"] += after / RAO
                rec["free_tao_delta"] += (after - before) / RAO
                continue
            if h == "RESERVED" or n != netuid:
                if n not in (-1, netuid):
                    rec["other_subnet_delta_rao"] += after - before
                continue
            rec["stake_before"] += before / RAO
            rec["stake_after"] += after / RAO
            measured = after - before
            r = hks.get(h)
            oc = owner_cut if (h == owner_hk and ck == owner_ck) else 0
            tk_a = tk_r = nom_share = 0.0
            take_own = take_ext = 0.0
            if r:
                nom = int(r["nominator_divs_rao"])
                rdiv = int(r["root_divs_rao"])
                tf = int(r["take_u16"]) / U16
                gross = nom / (1 - tf) if tf < 1 else nom
                owns = r["owner_coldkey"] == ck
                tk_a = (gross - nom) if owns else 0.0
                tk_r = (rdiv / (1 - tf) - rdiv) if (owns and tf < 1) else 0.0
                t_after = int(r["total_alpha_after_rao"])
                denom = t_after - nom
                if nom and denom > 0:
                    nom_share = nom * (before + oc + tk_a) / denom
                # economic split of take on our own validator
                t_before = int(r["total_alpha_before_rao"])
                own_frac = before / t_before if t_before else 0.0
                take_own = tk_a * own_frac
                take_ext = tk_a * (1 - own_frac) + tk_r
            modelled = oc + tk_a + tk_r + nom_share
            rec["measured"] += measured / RAO
            rec["owner_cut"] += oc / RAO
            rec["take_alpha"] += tk_a / RAO
            rec["take_root"] += tk_r / RAO
            rec["nominator_yield"] += nom_share / RAO
            rec["take_on_own_stake"] += take_own / RAO
            rec["take_on_external"] += take_ext / RAO
            rec["residual"] += (measured - modelled) / RAO
        rec["validator_take"] = rec["take_alpha"] + rec["take_root"]
        rec["total_income"] = rec["owner_cut"] + rec["validator_take"] + rec["nominator_yield"]
        rec["econ_validator"] = rec["take_on_external"]
        rec["econ_staking_yield"] = rec["nominator_yield"] + rec["take_on_own_stake"]
        per_epoch.append(dict(rec))

    lines = ["owner_cut", "validator_take", "nominator_yield", "take_on_own_stake", "take_on_external",
             "econ_validator", "econ_staking_yield", "total_income", "measured", "residual"]
    write("epoch_income.csv", per_epoch,
          ["epoch_block", "ts", "date", "alpha_price_tau", "tao_usd", "stake_before", "stake_after",
           "free_tao_after", "free_tao_delta", *lines])

    # daily roll-up, each epoch valued at its own alpha price and that day's TAO/USD
    daily = {}
    for r in per_epoch:
        D = daily.setdefault(r["date"], defaultdict(float))
        D["date"] = r["date"]
        D["epochs"] += 1
        for k in lines:
            D[k] += r.get(k, 0.0)
            D[k + "_tau"] += r.get(k, 0.0) * r["alpha_price_tau"]
            if r["tao_usd"] != "":
                D[k + "_usd"] += r.get(k, 0.0) * r["alpha_price_tau"] * float(r["tao_usd"])
        D["alpha_price_tau_close"] = r["alpha_price_tau"]
        D["tao_usd"] = r["tao_usd"]
        D["alpha_usd_close"] = r["alpha_price_tau"] * float(r["tao_usd"]) if r["tao_usd"] != "" else ""
        D["stake_close"] = r["stake_after"]
        D.setdefault("stake_open", r["stake_before"])
    dlist = [dict(daily[k]) for k in sorted(daily)]
    write("daily_income.csv", dlist,
          ["date", "epochs", "alpha_price_tau_close", "tao_usd", "alpha_usd_close", "stake_open", "stake_close",
           *lines, *[k + "_usd" for k in lines], *[k + "_tau" for k in lines]])

    # monthly
    monthly = {}
    for r in dlist:
        m = r["date"][:7]
        M = monthly.setdefault(m, defaultdict(float))
        M["month"] = m
        M["days"] += 1
        for k in lines:
            M[k] += r[k]
            M[k + "_usd"] += r.get(k + "_usd", 0.0)
        M.setdefault("stake_open", r["stake_open"])
        M["stake_close"] = r["stake_close"]
    write("monthly_income.csv", [dict(monthly[k]) for k in sorted(monthly)],
          ["month", "days", "stake_open", "stake_close", *lines, *[k + "_usd" for k in lines]])

    # validator landscape on the subnet over the whole window
    land = []
    for h, L in landscape.items():
        land.append({"hotkey": h, "label": labels.get(h, ""), "owner_coldkey": L["owner_coldkey"],
                     "owner_label": labels.get(L["owner_coldkey"], ""), **{k: v for k, v in L.items() if k != "owner_coldkey"}})
    land.sort(key=lambda x: -x["gross_alpha_divs"])
    write("validator_landscape.csv", land)

    # flows
    flows = rows("flows.csv")
    evmap = {}
    p = os.path.join(RAW, "flow_events.jsonl")
    if os.path.exists(p):
        for line in open(p):
            e = json.loads(line)
            evmap[int(e["block"])] = e["events"]
    fl = []
    for f in flows:
        b = int(f["block"])
        delta = (int(f["after_rao"]) - int(f["before_rao"])) / RAO
        fl.append({"block": b, "date": day_of(f["ts"]), "coldkey": f["coldkey"], "label": labels.get(f["coldkey"], ""),
                   "hotkey": f["hotkey"], "netuid": f["netuid"], "delta": delta,
                   "events": summarise_events(evmap.get(b, []), tracked)})
    write("flows_detail.csv", fl)

    summary = {"epochs": len(per_epoch), "first": per_epoch[0]["date"] if per_epoch else None,
               "last": per_epoch[-1]["date"] if per_epoch else None,
               "max_abs_residual_alpha": max((abs(r["residual"]) for r in per_epoch), default=0),
               "monthly": [dict(monthly[k]) for k in sorted(monthly)]}
    json.dump(summary, open(os.path.join(DER, "summary.json"), "w"), indent=1, default=str)
    print(json.dumps({k: summary[k] for k in ("epochs", "first", "last", "max_abs_residual_alpha")}))


def summarise_events(evs, tracked) -> str:
    out = []
    for e in evs or []:
        if isinstance(e, str):
            out.append(e)
            continue
        ev = e.get("event", e) if isinstance(e, dict) else e
        mod = ev.get("module_id") or ev.get("module") or ev.get("pallet") or ""
        name = ev.get("event_id") or ev.get("name") or ev.get("event") or ""
        attrs = ev.get("attributes") or ev.get("params") or ev.get("data") or {}
        if mod in ("TransactionPayment", "System") and name in ("TransactionFeePaid", "ExtrinsicSuccess", "NewAccount"):
            continue
        out.append(f"{mod}.{name} {json.dumps(attrs, default=str)[:400]}")
    return " | ".join(out)


if __name__ == "__main__":
    main()
