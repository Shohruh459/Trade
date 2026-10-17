"""Build H1 CSV (UTC) from the Hugging Face dataset qleap/dukascopy-ticks-ohlcv (1-minute candles, Dukascopy-derived).

Usage: python tools/build_h1_from_hf.py eur_usd [2020_04 2026_04]
Downloads monthly parquet files, resamples M1 -> H1, writes data/<PAIR>_H1_<first>_<last>.csv.
Note: candle side is ~mid (about +0.2 pip above Dukascopy BID in liquid hours, measured on 2023-01..06).
"""
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

BASE = "https://huggingface.co/datasets/qleap/dukascopy-ticks-ohlcv/resolve/main/1min/{pair}/{ym}.parquet"
ROOT = Path(__file__).resolve().parent.parent


def months(a, b):
    y, m = map(int, a.split("_"))
    y1, m1 = map(int, b.split("_"))
    while (y, m) <= (y1, m1):
        yield f"{y}_{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main():
    pair = sys.argv[1]
    first = sys.argv[2] if len(sys.argv) > 2 else "2020_04"
    last = sys.argv[3] if len(sys.argv) > 3 else "2026_04"
    tmp = Path(tempfile.mkdtemp(prefix=f"hf_{pair}_"))

    def get(ym):
        out = tmp / f"{ym}.parquet"
        subprocess.run(["curl", "-sfL", "--max-time", "120", "-o", str(out), BASE.format(pair=pair, ym=ym)], check=True)
        return out

    with ThreadPoolExecutor(6) as ex:
        files = list(ex.map(get, list(months(first, last))))
    m1 = pd.concat(pd.read_parquet(f) for f in files).sort_index()
    m1 = m1[~m1.index.duplicated()]
    m1.index = pd.to_datetime(m1.index).tz_localize("UTC") if m1.index.tz is None else m1.index
    m1.columns = [c.lower() for c in m1.columns]
    h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()
    out = ROOT / "data" / f"{pair.replace('_', '').upper()}_H1_{first.replace('_', '')}_{last.replace('_', '')}.csv"
    h1.to_csv(out)
    print(out.name, "M1 rows:", len(m1), "H1 rows:", len(h1), h1.index.min(), h1.index.max())


if __name__ == "__main__":
    main()
