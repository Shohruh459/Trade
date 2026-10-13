"""Download EUR/USD 1-minute BID candles from Dukascopy and build H1 CSV (UTC).

Usage: python tools/download_dukascopy.py [START_YEAR] [END_YEAR]
Raw daily files go to data/raw/ (git-ignored); resumable.
"""
import datetime as dt
import lzma
import struct
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
URL = "https://datafeed.dukascopy.com/datafeed/EURUSD/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5"


def fetch(day):
    path = RAW / f"{day:%Y%m%d}.bi5"
    if path.exists():
        return day, True
    url = URL.format(y=day.year, m=day.month - 1, d=day.day)  # month is 0-indexed
    for attempt in range(6):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=30) as r:
                path.write_bytes(r.read())
            time.sleep(0.4)
            return day, True
        except Exception as e:
            code = getattr(e, "code", None)
            if code == 404:
                path.write_bytes(b"")
                return day, True
            time.sleep(2 * (attempt + 1))
    return day, False


def decode(day):
    raw = (RAW / f"{day:%Y%m%d}.bi5").read_bytes()
    if not raw:
        return []
    b = lzma.decompress(raw)
    base = dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc)
    rows = []
    for i in range(len(b) // 24):
        t, o, c, l, h, v = struct.unpack(">IIIIIf", b[i * 24:i * 24 + 24])
        rows.append((base + dt.timedelta(seconds=t), o / 1e5, h / 1e5, l / 1e5, c / 1e5, v))
    return rows


def main():
    y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
    y1 = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    RAW.mkdir(parents=True, exist_ok=True)
    days = [d.date() for d in pd.date_range(f"{y0}-01-01", f"{y1}-12-31")]
    with ThreadPoolExecutor(2) as ex:
        failed = [d for d, ok in ex.map(fetch, days) if not ok]
    print("failed days:", len(failed), failed[:10])
    rows = []
    for d in days:
        if (RAW / f"{d:%Y%m%d}.bi5").exists():
            rows += decode(d)
    m1 = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"]).set_index("time")
    h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()
    h1.to_csv(ROOT / "data" / f"EURUSD_H1_{y0}_{y1}.csv")
    print("M1 rows:", len(m1), "H1 rows:", len(h1), h1.index.min(), h1.index.max())


if __name__ == "__main__":
    main()
