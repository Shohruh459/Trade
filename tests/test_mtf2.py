"""Unit tests for the MTF2 trade path on hand-made arrays (fixtures only, not market data)."""
import numpy as np

from backtest.mtf2 import trade_path


def make(prices, h1_d=None, quarter=15):
    """prices: list of (o,h,l,c) per M15 bar; every 4th bar completes an H1 bar."""
    n = len(prices)
    start = (np.datetime64("2024-01-02T00:00") + np.arange(n) * np.timedelta64(quarter, "m")).astype("datetime64[ns]")
    end = start + np.timedelta64(quarter, "m")
    o, h, l, c = (np.array([p[i] for p in prices], float) for i in range(4))
    nh = n // 4
    h1s = start[::4][:nh]
    h1e = h1s + np.timedelta64(1, "h")
    h1h = np.array([h[4 * k:4 * k + 4].max() for k in range(nh)])
    h1l = np.array([l[4 * k:4 * k + 4].min() for k in range(nh)])
    d = np.array(h1_d if h1_d is not None else [1] * nh)
    e2 = {int(e.astype("int64")): j for j, e in enumerate(h1e)}
    return dict(m15_start=start, m15_end=end, m15_o=o, m15_h=h, m15_l=l, h1_start=h1s, h1_end=h1e, h1_h=h1h, h1_l=h1l, h1_d=d, end2h1=e2)


def bar(o, h=None, l=None):
    return (o, o + 0.1 if h is None else h, o - 0.1 if l is None else l, o)


def test_trailing_stop_exit():
    # long from 100, R=2: price drifts to 110, trailing stop = 110.x-2, then a drop hits it
    p = [bar(100.0)] * 4 + [bar(105.0, 105.5, 104.5)] * 4 + [bar(110.0, 110.5, 109.5)] * 4 + [bar(109.0, 109.5, 107.0)] * 4
    a = make(p)
    px, tx, why, done = trade_path(0, 1, 2.0, a)
    assert why == "stop" and abs(px - 108.5) < 1e-9 and done == 3      # best high 110.5 - 2.0 = 108.5, hit in the 4th H1 bar


def test_initial_stop():
    p = [bar(100.0)] + [bar(99.0, 99.2, 97.5)] + [bar(97.0)] * 10
    a = make(p)
    px, tx, why, done = trade_path(0, 1, 2.0, a)
    assert why == "stop" and abs(px - 98.0) < 1e-9


def test_gap_through_stop_exits_at_open():
    p = [bar(100.0)] * 4 + [bar(95.0, 95.2, 94.8)] + [bar(95.0)] * 7
    a = make(p)
    px, tx, why, done = trade_path(0, 1, 2.0, a)
    assert why == "stop_gap" and abs(px - 95.0) < 1e-9


def test_opposite_flip_exits_next_open():
    p = [bar(100.0, 100.3, 99.9)] * 4 + [bar(100.2, 100.4, 100.0)] * 4 + [bar(100.3, 100.5, 100.1)] * 8
    a = make(p, h1_d=[1, -1, 1, 1])             # 2nd H1 bar completes with d=-1 -> exit at the next M15 open
    px, tx, why, done = trade_path(0, 1, 5.0, a)
    assert why == "flip" and done == 2 and abs(px - 100.3) < 1e-9


def test_time_stop():
    p = [bar(100.0, 100.05, 99.95)] * 40
    a = make(p)
    px, tx, why, done = trade_path(0, 1, 5.0, a, max_h1=5)
    assert why == "time" and done == 5


def test_short_mirrors_long():
    p = [bar(100.0)] * 4 + [bar(95.0, 95.5, 94.5)] * 4 + [bar(90.0, 90.5, 89.5)] * 4 + [bar(91.0, 93.0, 90.5)] * 4
    a = make(p, h1_d=[-1, -1, -1, -1])
    px, tx, why, done = trade_path(0, -1, 2.0, a)
    assert why == "stop" and abs(px - 91.5) < 1e-9                      # best low 89.5 + 2.0
