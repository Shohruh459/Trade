import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location("h4e", Path(__file__).resolve().parent.parent / "tools" / "h4_demo_eval.py")
h4e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h4e)


def mk(profits):
    t = pd.date_range("2026-11-01", periods=len(profits), freq="7D")
    return pd.DataFrame({"close_time": t, "dir": 1, "entry": 4000, "stop_dist": 10, "risk_money": 1.0, "profit": profits, "R": profits})


def test_metrics_and_drawdown():
    ev = h4e.evaluate(mk([1.0, -1.0, 2.0, -1.0]), 100.0)
    assert ev["n"] == 4 and ev["total"] == 1.0
    assert abs(ev["pf"] - 1.5) < 1e-9
    assert ev["maxdd_pct"] > 0


def test_hard_stop_on_drawdown():
    ev = h4e.evaluate(mk([-5.0] * 6), 100.0)
    assert "TO'XTATISH" in h4e.verdict(ev, 3)


def test_twelve_month_rule():
    ev = dict(n=30, mean_R=-0.4, maxdd_pct=10.0)
    assert "TO'XTATISH" in h4e.verdict(ev, 12)
    ev["mean_R"] = 0.0
    assert "Davom" in h4e.verdict(ev, 12)
