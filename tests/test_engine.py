"""Engine unit tests on tiny hand-made bars (test fixtures only, not market data)."""
import numpy as np
import pandas as pd

from backtest.engine import Config, run


def bars(rows, start="2024-01-02 08:00"):
    idx = pd.date_range(start, periods=len(rows), freq="1h", tz="UTC")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


CFG = Config(spread_pips=0, slippage_pips=0, commission_per_lot=0, session_start=0, session_end=24)


def test_long_hits_tp():
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1040, 1.0998, 1.1030), (1.1030, 1.1030, 1.1030, 1.1030)])
    sig, atr = np.array([1, 0, 0]), np.array([0.0020, 0.0020, 0.0020])  # SL=30 pips, TP=60 pips
    t, _ = run(df, sig, atr, CFG)
    assert len(t) == 1 and t.reason[0] == "end"  # TP 1.1060 not reached, closed at last bar
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1070, 1.0998, 1.1060), (1.1060, 1.1060, 1.1060, 1.1060)])
    t, _ = run(df, sig, atr, CFG)
    assert t.reason[0] == "tp" and abs(t.r[0] - 2.0) < 1e-6


def test_sl_first_when_both_reachable():
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1100, 1.0950, 1.1000), (1.1, 1.1, 1.1, 1.1)])
    t, _ = run(df, np.array([1, 0, 0]), np.full(3, 0.0020), CFG)
    assert t.reason[0] == "sl" and abs(t.r[0] + 1.0) < 1e-6


def test_short_pays_spread():
    cfg = Config(spread_pips=1.0, slippage_pips=0, commission_per_lot=0, session_start=0, session_end=24)
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1000, 1.0900, 1.0910), (1.09, 1.09, 1.09, 1.09)])
    t, _ = run(df, np.array([-1, 0, 0]), np.full(3, 0.0020), cfg)
    # short entry at bid 1.1000, SL=1.1030, TP=1.0940; exit on ask => TP when low+0.0001<=1.0940
    assert t.reason[0] == "tp" and abs(t.exit[0] - 1.0940) < 1e-9


def test_no_entry_outside_session_and_no_lookahead():
    cfg = Config(spread_pips=0, slippage_pips=0, commission_per_lot=0, session_start=10, session_end=12)
    df = bars([(1.1, 1.1, 1.1, 1.1)] * 6)  # hours 8..13
    t, _ = run(df, np.array([1, 1, 1, 0, 0, 0]), np.full(6, 0.002), cfg)
    assert all(10 <= ts.hour < 12 for ts in t.entry_time)


def test_trailing_stop_locks_profit():
    cfg = Config(spread_pips=0, slippage_pips=0, commission_per_lot=0, session_start=0, session_end=24,
                 rr=None, trail_atr=1.0, trail_start_r=1.0)
    # ATR=20 pips, SL=30 pips. Price runs +50 pips (>1R) then falls back.
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1050, 1.1000, 1.1045),
               (1.1045, 1.1046, 1.1000, 1.1005), (1.1005, 1.1005, 1.1005, 1.1005)])
    t, _ = run(df, np.array([1, 0, 0, 0]), np.full(4, 0.0020), cfg)
    # trail after bar1: 1.1050 - 0.0020 = 1.1030 > entry, so exit by stop at 1.1030 (profit)
    assert t.reason[0] == "sl" and abs(t.exit[0] - 1.1030) < 1e-9 and t.pnl[0] > 0


def test_breakeven():
    cfg = Config(spread_pips=0, slippage_pips=0, commission_per_lot=0, session_start=0, session_end=24, rr=None, be_r=1.0)
    df = bars([(1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1035, 1.1000, 1.1030),
               (1.1030, 1.1030, 1.0990, 1.1000), (1.1, 1.1, 1.1, 1.1)])
    t, _ = run(df, np.array([1, 0, 0, 0]), np.full(4, 0.0020), cfg)
    assert abs(t.exit[0] - 1.1000) < 1e-9 and abs(t.pnl[0]) < 1e-6
