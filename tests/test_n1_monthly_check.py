"""Tests for the N1 monthly check (hand-made data, temp files)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("n1c", Path(__file__).resolve().parent.parent / "tools" / "n1_monthly_check.py")
n1c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n1c)


def prices(n=14, start="2025-01"):
    idx = pd.period_range(start, periods=n, freq="M")
    up = np.linspace(100, 130, n)
    dn = np.linspace(130, 100, n)
    df = pd.DataFrame({"month": idx.astype(str), "spx": up, "y10": 4.0, "gold": dn, "wti": up, "natgas": dn, "source": "t"}, index=idx)
    return df


def test_weights_are_one_over_n_and_rest_cash():
    t = n1c.state_table(n1c.levels(prices()))
    last = t.iloc[-1]
    assert last.complete
    assert abs(last.w_equity - 0.2) < 1e-9 and abs(last.w_oil - 0.2) < 1e-9
    assert last.w_gold == 0 and last.w_natgas == 0
    assert abs(last.w_cash - 0.4 + (last.w_bond)) < 1e-9 or abs(last.w_cash - (1 - 0.4 - last.w_bond)) < 1e-9


def test_log_locked_idempotent_and_realized(tmp_path):
    n1c.FORWARD_START = pd.Period("2025-11", "M")
    df = prices()
    L = n1c.levels(df)
    t = n1c.state_table(L)
    lp = tmp_path / "log.csv"
    log = n1c.update_log(t, L, lp)
    first = pd.read_csv(lp)
    n1c.update_log(t, L, lp)
    assert pd.read_csv(lp).equals(first)
    assert log.port_ret_pct.notna().sum() >= 1
    assert log.month.iloc[0] == "2025-11"
