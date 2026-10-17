"""Tests for the monthly gold check (hand-made data, temp files)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("gmc", Path(__file__).resolve().parent.parent / "tools" / "gold_monthly_check.py")
gmc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gmc)


def series(vals, start="2025-01"):
    return pd.Series(vals, index=pd.period_range(start, periods=len(vals), freq="M"), dtype=float)


def test_signal_long_above_sma_and_cash_below():
    up = series(list(range(100, 125)))
    t = gmc.state_table(up)
    assert t.signal.dropna().iloc[-1] == 1.0
    down = series(list(range(125, 100, -1)))
    assert gmc.state_table(down).signal.dropna().iloc[-1] == 0.0


def test_season_flag_is_for_next_month():
    t = gmc.state_table(series([100.0] * 12, start="2025-08"))
    assert t.loc[pd.Period("2025-08", "M"), "season_next"] == 1      # next = September
    assert t.loc[pd.Period("2026-02", "M"), "season_next"] == 0      # next = March


def test_log_is_locked_and_idempotent(tmp_path):
    gmc.FORWARD_START = pd.Period("2025-10", "M")
    P = series(list(np.linspace(100, 130, 14)), start="2025-01")
    t = gmc.state_table(P.iloc[:-1])
    lp = tmp_path / "log.csv"
    gmc.update_log(t, lp)
    first = pd.read_csv(lp)
    gmc.update_log(t, lp)                                             # same data again: no duplicates, file unchanged
    second = pd.read_csv(lp)
    assert second.equals(first)
    t2 = gmc.state_table(P)                                           # one more month arrives: new row + realized return for previous row
    gmc.update_log(t2, lp)
    third = pd.read_csv(lp)
    assert len(third) == len(first) + 1
    assert not np.isnan(third.next_ret_pct.iloc[-2])
    assert third.loc[0, ["price", "sma10", "signal"]].equals(first.loc[0, ["price", "sma10", "signal"]])   # snapshot never rewritten
