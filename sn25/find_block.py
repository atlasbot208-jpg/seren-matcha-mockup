"""Find the exact block(s) in (lo, hi] where tracked coldkeys' holdings changed, and dump those blocks' events."""
import argparse, asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import bittensor as bt
from audit_extract import Pool, positions, locate, ENDPOINTS, RAW, log
from bittensor._generated import storage as st

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lo", type=int, required=True); ap.add_argument("--hi", type=int, required=True)
    ap.add_argument("--coldkeys", default="")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(os.path.dirname(os.path.dirname(RAW)), "wallets.json")))
    cks = a.coldkeys.split(",") if a.coldkeys else list(cfg["coldkeys"])
    clients = []
    for ep in ENDPOINTS:
        try:
            c = bt.Client(ep, fallback_endpoints=[], archive_endpoints=[]); await c.connect(); clients.append(c)
        except Exception as e:
            log("endpoint unavailable", ep, e)
    p = Pool(clients, 0.6)
    plo, phi = await asyncio.gather(positions(p, cks, a.lo), positions(p, cks, a.hi))
    found = []
    await locate(p, cks, a.lo, a.hi, plo, phi, found)
    out = []
    for b, x, y in found:
        h = await p.call("_block_hash", b)
        evs = await clients[0]._substrate.events(h)
        blk = await clients[0]._substrate.get_block(block_hash=h)
        exts = []
        for ex in (blk or {}).get("extrinsics") or []:
            s = json.dumps(ex, default=str)
            if any(ck in s for ck in cks) or "swap" in s.lower():
                exts.append(s[:4000])
        diffs = {f"{k[0]}|{k[1]}|{k[2]}": [x.get(k, 0), y.get(k, 0)] for k in set(x) | set(y) if x.get(k, 0) != y.get(k, 0)}
        out.append({"block": b, "diffs": diffs,
                    "events": [e for e in evs or [] if e.get("module_id") not in ("Timestamp",)][:80],
                    "extrinsics": exts})
        log(f"change at {b}: {diffs}")
    json.dump(out, open(os.path.join(RAW, f"find_{a.lo}_{a.hi}.json"), "w"), default=str, indent=1)
    for c in clients: await c.close()

asyncio.run(main())
