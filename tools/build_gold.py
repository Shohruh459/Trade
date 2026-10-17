"""Build data/XAUUSD_H1_2018_2025.csv (UTC) from ZombitX64/xauusd-gold-price-historical-data-2004-2025 (XAU_1h_data.jsonl).

The source timestamps are Europe/Athens (EET/EEST) server time; verified against alshahri/xauusd-h1-bid-2019-01-01-2023-05-30
(UTC BID candles): after conversion the close differs by ~0.09 USD on average (std 0.19).
Usage: python tools/build_gold.py path/to/XAU_1h_data.jsonl [out_csv_name]  (works for 15m/5m files too)
"""
import sys
from pathlib import Path

import pandas as pd

d = pd.read_json(sys.argv[1], lines=True)
d["time"] = pd.to_datetime(d["Date"], format="%Y.%m.%d %H:%M")
d = d.drop(columns="Date").set_index("time").sort_index()
d.columns = [c.lower() for c in d.columns]
d.index = d.index.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
d = d[d.index.notna()]
d = d[~d.index.duplicated()].sort_index()
d.index.name = "time"
d = d[d.index >= "2018-01-01"]
out = Path(__file__).resolve().parent.parent / "data" / (sys.argv[2] if len(sys.argv) > 2 else "XAUUSD_H1_2018_2025.csv")
d.to_csv(out)
print(out.name, len(d), d.index.min(), d.index.max())
