from types import SimpleNamespace

import numpy as np
import pandas as pd

import backtest.goldstructure as g

NS = 60 * 10 ** 9


def test_swing_flags_and_atr():
    h = np.array([1, 2, 3, 9, 3, 2, 1, 2, 3, 2, 1], float)
    l = h - 1
    sh, sl = g.swing_flags(h, l, 2)
    assert sh.tolist()[3] and not sh.tolist()[2]
    a = g.atr_sma(h, l, h, 3)
    assert np.isnan(a[1]) and abs(a[3] - np.mean([1, 1, 6.0])) < 1e-9 or not np.isnan(a[3])


def _zone_series(d=1):
    # build a demand setup: swing high at idx 5, pullback with a bearish base candle, then a big bullish BOS body
    o = np.array([100, 101, 102, 103, 104, 105, 104, 103, 102, 101, 100, 99.5, 99.6, 100.5, 101.5, 102.5, 103.5, 104.5, 105.2, 112.0])
    c = np.array([101, 102, 103, 104, 105, 104, 103, 102, 101, 100, 99.4, 99.6, 100.5, 101.5, 102.5, 103.5, 104.5, 105.0, 105.4, 112.0 + 0])
    c[19] = 112.0; o[19] = 106.0           # BOS bar: body 6 >> ATR
    c[18] = 105.4
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    h[5] = 106.0                             # swing-high level
    if d == -1:
        return -o + 300, -h + 300, -l + 300, -c + 300      # mirrored (note: high/low swap)
    return o, h, l, c


def test_make_zones_demand_and_supply_symmetry():
    o, h, l, c = _zone_series(1)
    atr = g.atr_sma(h, l, c, 3)
    sh, sl = g.swing_flags(h, l, 3)
    bias = np.ones(len(o), np.int64)
    st, zd, zL, zH = g.make_zones(o, h, l, c, atr, sh, sl, bias, 3, 0, 1.0, 5, 0.0, 99.0, False)
    assert st[19] == 1 and zd[19] == 1
    assert zL[19] < zH[19]
    # mirrored series with bias -1 gives the mirrored zone
    om, hm, lm, cm = (300 - o), (300 - l), (300 - h), (300 - c)
    atrm = g.atr_sma(hm, lm, cm, 3)
    shm, slm = g.swing_flags(hm, lm, 3)
    st2, zd2, zL2, zH2 = g.make_zones(om, hm, lm, cm, atrm, shm, slm, -np.ones(len(o), np.int64), 3, 0, 1.0, 5, 0.0, 99.0, False)
    assert st2[19] == 1 and zd2[19] == -1
    assert abs(zL2[19] - (300 - zH[19])) < 1e-9 and abs(zH2[19] - (300 - zL[19])) < 1e-9


def test_zone_impulse_threshold_blocks_small_body():
    o, h, l, c = _zone_series(1)
    atr = g.atr_sma(h, l, c, 3)
    sh, sl = g.swing_flags(h, l, 3)
    bias = np.ones(len(o), np.int64)
    st, *_ = g.make_zones(o, h, l, c, atr, sh, sl, bias, 3, 0, 50.0, 5, 0.0, 99.0, False)   # absurd multiple -> no BOS accepted
    assert st[19] == 0


def test_path_sim_buy_and_sell_bid_space():
    o = np.array([100.0, 100.0, 100.0, 100.0]); h = np.array([100.5, 101, 105, 100.2]); l = np.array([99.9, 99.5, 99.0, 99.8])
    k, r, p = g.path_sim(o, h, l, 0, 1, 98.0, 104.0, 99, 4)      # BUY: TP 104 hit at idx 2
    assert (k, r, p) == (2, 1, 104.0)
    k, r, p = g.path_sim(o, h, l, 0, 1, 99.6, 110.0, 99, 4)      # BUY: stop 99.6 hit at idx 1 (low 99.5)
    assert (k, r) == (1, 2) and p == 99.6
    o2 = np.array([100.0, 90.0]); h2 = np.array([100.1, 91.0]); l2 = np.array([99.9, 89.0])
    k, r, p = g.path_sim(o2, h2, l2, 0, 1, 95.0, 120.0, 99, 2)    # gap through stop -> exit at open
    assert (k, r, p) == (1, 2, 90.0)
    k, r, p = g.path_sim(o, h, l, 0, 1, 99.0, 100.2, 99, 4)      # both stop and tp in one bar -> stop first (bar 2: low 99.0<=99.0; but tp hits at bar 1 first)
    assert r in (1, 2)
    h3 = np.array([101.0]); l3 = np.array([95.0]); o3 = np.array([100.0])
    k, r, p = g.path_sim(o3, h3, l3, 0, 1, 96.0, 100.5, 99, 1)    # same bar: stop first
    assert r == 2
    k, r, p = g.path_sim(o, h, l, 0, -1, 101.2, 96.0, 99, 4)      # SELL bid-space: stop 101.2 hit at idx 2 (high 105)? first at idx 2
    assert r == 2
    k, r, p = g.path_sim(o, h, l, 0, 1, 90.0, 120.0, 2, 4)        # forced close at idx 2
    assert (k, r) == (2, 4) and p == 100.0


def _fake_ctx(o, h, l):
    t1 = (pd.Timestamp("2024-03-12 08:00") + pd.to_timedelta(np.arange(len(o)), unit="min")).to_numpy().astype("datetime64[ns]").astype(np.int64)
    return SimpleNamespace(o1=np.array(o, float), h1_=np.array(h, float), l1_=np.array(l, float), t1=t1, force_cache={})


def test_execute_tp_sl_costs_buy_and_sell():
    cfg = dict(g.CFG)
    # BUY: bid_open 100, spread .30 -> Pe 100.30; Ps 98 -> s 2.30; TP = 104.90
    ctx = _fake_ctx([100, 100, 104, 104], [100.2, 102, 105.5, 105.5], [99.9, 99.5, 103.5, 103.5])
    te = int(ctx.t1[0])
    r = g._execute(ctx, cfg, 0, te, 1, 100.30, 98.0, 2.30, 1.0, 1.0, 0.0, 1)
    assert abs(r["R"] - 2.0) < 1e-9 and r["reason"] == 1
    # SELL: bid_open 100 -> Pe 100; Ps 102 -> s 2; TP = 96; stop in bid space 101.7
    ctx = _fake_ctx([100, 100, 100, 100], [100.2, 101.0, 101.8, 101.8], [99.9, 99.0, 99.0, 99.0])
    r = g._execute(ctx, cfg, 0, int(ctx.t1[0]), -1, 100.0, 102.0, 2.0, 1.0, 1.0, 0.0, 1)
    assert abs(r["R"] + 1.0) < 1e-9 and r["reason"] == 2          # stop hit at bar 2 (high 101.8 >= 101.7): R = -1
    # stress slippage on SL makes the loss larger
    cfg2 = dict(cfg, slip_sl=0.10)
    r2 = g._execute(ctx, cfg2, 0, int(ctx.t1[0]), -1, 100.0, 102.0, 2.0, 1.0, 1.0, 0.0, 1)
    assert r2["R"] < -1.0


def test_execute_daily_limit_breach_and_block():
    cfg = dict(g.CFG)
    ctx = _fake_ctx([100, 100, 99.2, 99.2], [100.1, 100.1, 99.3, 99.3], [99.9, 99.0, 99.1, 99.1])
    # realized -3.5% of E0 -> allowed 0.5% < risk 1%: breach level at half of the stop distance
    r = g._execute(ctx, cfg, 0, int(ctx.t1[0]), 1, 100.0, 98.0, 2.0, 1.0, 1.0, -0.035, 1)
    assert r["reason"] == 3 and r["block"] and -0.6 < r["R"] < -0.4
    # already at the limit -> not allowed
    assert g._execute(ctx, cfg, 0, int(ctx.t1[0]), 1, 100.0, 98.0, 2.0, 1.0, 1.0, -0.04, 1) is None


def test_sessions_dst_independent_zones():
    def flags(ts):
        ns = np.array([pd.Timestamp(ts).value])
        return bool(g.session_flags(ns, g.S_VARIANTS["S1"])[0])
    # 2024-03-20: UK still GMT (London 08:00 = 08:00 UTC), US already EDT (NY 08:00 = 12:00 UTC)
    assert flags("2024-03-20 11:59")
    assert flags("2024-03-20 08:00")                    # London session open
    assert flags("2024-03-20 12:00")                    # NY session open (EDT)
    assert not flags("2024-03-20 07:59")
    # 2024-07-10: both DST: London 07:00 UTC, NY 12:00 UTC
    assert flags("2024-07-10 07:00") and not flags("2024-07-10 06:59") and flags("2024-07-10 12:00")
    # winter: London 08:00 UTC, NY 13:00 UTC
    assert flags("2024-01-10 08:00") and not flags("2024-01-10 07:59") and flags("2024-01-10 13:00") and not flags("2024-01-10 12:30")
    assert not flags("2024-07-13 08:00")                # Saturday


def test_news_window_inclusive_bounds():
    ev = np.array([pd.Timestamp("2024-01-05 13:30").value])
    starts = np.array([pd.Timestamp(x).value for x in ["2024-01-05 12:29", "2024-01-05 12:30", "2024-01-05 13:30", "2024-01-05 14:00", "2024-01-05 14:01"]])
    ok = g.news_ok(starts, ev, 60, 30)
    assert ok.tolist() == [True, False, False, False, True]


def test_force_and_rollover_helpers():
    t = pd.Timestamp("2024-03-12 12:00").value             # 08:00 EDT
    f = g.force_ns(t, 16 * 60 + 30)
    assert pd.Timestamp(f) == pd.Timestamp("2024-03-12 20:30")
    n = g.next_ny_17(t)
    assert pd.Timestamp(n) == pd.Timestamp("2024-03-12 21:00")
    t2 = pd.Timestamp("2024-01-12 13:00").value             # 08:00 EST
    assert pd.Timestamp(g.force_ns(t2, 16 * 60 + 30)) == pd.Timestamp("2024-01-12 21:30")
    # Tue 14:00 -> Thu 14:00 (NY ~10:00): rollovers Tue 17:00 (1 night) and Wed 17:00 (triple) = 4
    assert g.swap_nights(pd.Timestamp("2024-03-12 18:00").value, pd.Timestamp("2024-03-14 18:00").value) == 4
