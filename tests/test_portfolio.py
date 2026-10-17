"""Unit tests for the portfolio study building blocks (hand-made inputs)."""
import numpy as np
import pandas as pd

from backtest.portfolio import block_boot_delta, cw_stat, holm, metrics, overlay_returns, portfolio_returns


def test_metrics_known_drawdown():
    r = np.r_[0.10, -0.20, np.zeros(10)]
    m = metrics(r)
    assert abs(m["maxDD_pct"] - 20.0) < 1e-6            # peak 1.10 -> trough 0.88
    assert abs(m["worst12m_pct"] - (-12.0)) < 1e-6      # 1.10 * 0.80 - 1


def test_portfolio_fixed_weights_no_cost():
    R = pd.DataFrame({"a": [0.1, 0.0], "b": [0.0, 0.1]}, index=pd.period_range("2000-01", periods=2, freq="M"))
    out = portfolio_returns(R, np.array([0.5, 0.5]), cost=0.0)
    assert abs(out.iloc[0] - 0.05) < 1e-12 and abs(out.iloc[1] - 0.05) < 1e-12


def test_block_bootstrap_identical_series_gives_zero_delta():
    r = np.random.default_rng(0).normal(0.005, 0.03, 120)
    d = block_boot_delta(r, r, draws=50)
    assert np.allclose(d, 0.0)


def test_sma_overlay_signal_uses_past_only():
    idx = pd.period_range("2000-01", periods=40, freq="M")
    px = pd.Series(np.r_[np.linspace(100, 50, 20), np.linspace(50, 150, 20)], index=idx)
    rg = px / px.shift(1) - 1
    ov, sw = overlay_returns(rg, px, "sma", skip=0, cost_sma=0.0)
    # in the long decline the filter is flat (0) -> overlay return ~ 0 there; after the turn it follows the price up
    assert abs(ov.iloc[15]) < 1e-12 and ov.iloc[-1] > 0


def test_cw_zero_when_forecasts_equal():
    e = np.random.default_rng(1).normal(size=60)
    t, p = cw_stat(e, e, np.zeros(60), np.zeros(60), 2)
    assert abs(t) < 1e-9 or np.isnan(t) or p > 0.4


def test_holm_monotone():
    rej = holm(np.array([0.001, 0.01, 0.04, 0.5]))
    assert rej.tolist() == [True, True, False, False]       # 0.001<=0.05/4, 0.01<=0.05/3, 0.04>0.05/2
