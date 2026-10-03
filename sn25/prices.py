"""Daily TAO/USD closes for valuing alpha flows. Tries Kraken, then CoinGecko."""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "tao_usd_daily.csv")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sn25-actuals/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def kraken(since_unix: int):
    d = get(f"https://api.kraken.com/0/public/OHLC?pair=TAOUSD&interval=1440&since={since_unix}")
    if d.get("error"):
        raise RuntimeError(d["error"])
    rows = next(v for k, v in d["result"].items() if k != "last")
    out = {}
    for r in rows:
        day = datetime.fromtimestamp(int(r[0]), tz=timezone.utc).strftime("%Y-%m-%d")
        out[day] = {"open": float(r[1]), "close": float(r[4]), "vwap": float(r[5])}
    return out, "kraken TAOUSD daily OHLC"


def coingecko(since_unix: int):
    now = int(time.time())
    d = get(
        "https://api.coingecko.com/api/v3/coins/bittensor/market_chart/range"
        f"?vs_currency=usd&from={since_unix}&to={now}"
    )
    out = {}
    for ms, p in d["prices"]:
        day = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        out.setdefault(day, {"open": p, "close": p, "vwap": p})
        out[day]["close"] = p
    return out, "coingecko market_chart"


def main(start="2026-07-25"):
    since = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
    for fn in (kraken, coingecko):
        try:
            data, src = fn(since)
            break
        except Exception as e:  # noqa: BLE001
            print(f"{fn.__name__} failed: {e}", file=sys.stderr)
    else:
        raise SystemExit("no price source reachable")
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "close", "vwap", "source"])
        for day in sorted(data):
            v = data[day]
            w.writerow([day, v["open"], v["close"], v["vwap"], src])
    print(f"wrote {len(data)} days from {src}")


if __name__ == "__main__":
    main(*sys.argv[1:])
