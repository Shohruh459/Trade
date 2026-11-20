"""Build data/news/usd_high_impact.csv (UTC) from the Forex Factory calendar cache (STRATEGY_SPEC.md section 11.5).

Source: Hugging Face `Ehsanrs2/Forex_Factory_Calendar`, file forex_factory_cache.csv (2007-01 .. 2025-04-04).
Date comes from the file; time comes from the standard US release schedule (the file's times are unreliable: ~49% are 00:00 placeholders,
the rest carry DST offset errors): NFP/CPI/GDP 08:30 America/New_York, FOMC Statement / Federal Funds Rate 14:00 America/New_York.

Usage: python tools/build_news_calendar.py [path/to/forex_factory_cache.csv]
Writes data/news/usd_high_impact.csv and reports/news_calendar_coverage.md.
"""
import sys
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
URL = "https://huggingface.co/datasets/Ehsanrs2/Forex_Factory_Calendar/resolve/main/forex_factory_cache.csv"
DEFAULT_SRC = Path("/tmp/claude-0/cal/ff.csv")
FAMILIES = {
    "NFP": (["Non-Farm Employment Change"], "08:30"),
    "CPI": (["CPI m/m", "Core CPI m/m", "CPI y/y"], "08:30"),
    "GDP": (["Advance GDP q/q", "Prelim GDP q/q", "Second Estimate GDP q/q", "Final GDP q/q"], "08:30"),
    "FOMC": (["FOMC Statement", "Federal Funds Rate"], "14:00"),
}
OUT = ROOT / "data/news/usd_high_impact.csv"
COV = ROOT / "reports/news_calendar_coverage.md"


def build(src: Path) -> pd.DataFrame:
    d = pd.read_csv(src, usecols=["DateTime", "Currency", "Impact", "Event"])
    d = d[(d.Currency == "USD") & (d.Impact == "High Impact Expected")]
    rows = []
    for fam, (names, hhmm) in FAMILIES.items():
        x = d[d.Event.isin(names)]
        for r in x.itertuples():
            local = pd.Timestamp(f"{r.DateTime[:10]} {hhmm}", tz="America/New_York")
            rows.append(dict(event_utc=local.tz_convert("UTC").tz_localize(None), family=fam, event_name=r.Event, date_source="ff_date", time_source="standard_et", ff_datetime_raw=r.DateTime))
    cols = ["event_utc", "family", "event_name", "date_source", "time_source", "ff_datetime_raw"]
    out = pd.DataFrame(rows, columns=cols).drop_duplicates(["event_utc", "family", "event_name"]).sort_values("event_utc").reset_index(drop=True)
    return out


def coverage(df: pd.DataFrame) -> str:
    df = df.assign(year=df.event_utc.dt.year, day=df.event_utc.dt.normalize())
    tab = df.groupby(["family", "year"]).day.nunique().unstack("year").fillna(0).astype(int)
    lines = ["# Yangilik kalendari qamrovi (data/news/usd_high_impact.csv)\n", f"Qatorlar: {len(df)}; oraliq: {df.event_utc.min()} … {df.event_utc.max()}\n",
             "Noyob sanalar soni (oila × yil):\n", tab.to_markdown() + "\n"]
    miss = {}
    for fam in ("NFP", "CPI"):
        months = df[df.family == fam].event_utc.dt.to_period("M").unique()
        allm = pd.period_range("2018-04", "2025-02", freq="M")
        miss[fam] = [str(m) for m in allm if m not in months]
    lines.append(f"2018-04 → 2025-02 da NFP yo'q oylar: {miss['NFP'] or 'yo`q'}; CPI yo'q oylar: {miss['CPI'] or 'yo`q'}\n")
    return "\n".join(lines)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, src)
    df = build(src)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    COV.write_text(coverage(df))
    print(len(df), df.event_utc.min(), df.event_utc.max())
    print(COV.read_text())


if __name__ == "__main__":
    main()
