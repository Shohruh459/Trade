import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location("bnc", Path(__file__).resolve().parent.parent / "tools" / "build_news_calendar.py")
bnc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bnc)


def test_standard_et_to_utc_with_dst(tmp_path):
    src = tmp_path / "ff.csv"
    pd.DataFrame({
        "DateTime": ["2024-01-05T00:00:00+03:30", "2024-07-05T00:00:00+04:30", "2024-01-31T22:00:00+03:30"],
        "Currency": ["USD", "USD", "USD"], "Impact": ["High Impact Expected"] * 3,
        "Event": ["Non-Farm Employment Change", "Non-Farm Employment Change", "FOMC Statement"]}).to_csv(src, index=False)
    out = bnc.build(src)
    assert out.event_utc.tolist() == [pd.Timestamp("2024-01-05 13:30"), pd.Timestamp("2024-01-31 19:00"), pd.Timestamp("2024-07-05 12:30")]


def test_non_matching_rows_dropped(tmp_path):
    src = tmp_path / "ff.csv"
    pd.DataFrame({"DateTime": ["2024-01-05T00:00:00+03:30"] * 3, "Currency": ["EUR", "USD", "USD"], "Impact": ["High Impact Expected", "Low Impact Expected", "High Impact Expected"],
                  "Event": ["CPI m/m", "CPI m/m", "Retail Sales m/m"]}).to_csv(src, index=False)
    assert len(bnc.build(src)) == 0
