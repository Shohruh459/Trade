"""GoldStructureEA backtest: implements the FROZEN Documentation/GoldStructureEA/STRATEGY_SPEC.md (v3) and STRATEGY_GOLDSTRUCTURE.md (v3).

Nothing here is tuned; every parameter is in CFG and comes from the spec (section 13). Section numbers below refer to STRATEGY_SPEC.md.
The module only builds the simulator; the single confirmatory run is `python -m backtest.gs_run`.
"""
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from numba import njit

NS_MIN = 60 * 10 ** 9
LON, NYC = ZoneInfo("Europe/London"), ZoneInfo("America/New_York")

CFG = dict(
    kH1=3, kM15=3, kM5=2, ema_fast=50, ema_slow=200, atr_n=14,            # sections 1, 2, 13#1-3
    impulse_mode="body", impulse_mult=1.0,                                # A8 (b)
    zone_lookback=5, zone_hmin=0.3, zone_hmax=1.5, zone_age_bars=96, zone_body=False,
    max_retests=2, pin_wick_body=2.0, pin_wick_range=0.60, pin_opp=0.25,
    confirm_gap=2, signal_bars=12,                                        # |ind(M)-ind(P)| <= 2 ; signal bar <= j0+11
    stop_buf=0.2, smin=0.5, smax=2.0, rr=2.0, risk=0.01, daily_loss=0.04,
    sessions=[("London", 8 * 60, 12 * 60), ("New York", 8 * 60, 12 * 60)],  # S1 (local time)
    force_close=True, force_min=16 * 60 + 30,                              # NY 16:30
    news_before=60, news_after=30, news_families=("NFP", "CPI", "GDP", "FOMC"),
    spread=0.30, commission=0.0, slip_entry=0.0, slip_sl=0.0, swap_annual=0.03,
    side=0, use_a1=True,
    mss_on_exit=False,    # literal spec reading: the bar that ends the retest episode (fully outside the zone) is NOT an episode bar; True = descriptive sensitivity only
)
TZ = {"London": LON, "New York": NYC}
S_VARIANTS = {
    "S1": [("London", 480, 720), ("New York", 480, 720)],
    "S2": [("London", 480, 990), ("New York", 480, 1020)],
    "S3": [("London", 780, 1020), ("New York", 480, 720)],
    "S4": [("London", 480, 660), ("New York", 500, 690)],
}


# ------------------------------------------------------------------ bars and indicators
def make_bars(m1: pd.DataFrame, rule: str) -> pd.DataFrame:
    return m1.resample(rule).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def atr_sma(h, l, c, n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    tr[0] = h[0] - l[0]
    out = np.full(len(c), np.nan)
    cs = np.cumsum(np.r_[0.0, tr])
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


@njit(cache=True)
def swing_flags(h, l, k):
    n = len(h)
    sh = np.zeros(n, np.bool_); sl = np.zeros(n, np.bool_)
    for i in range(k, n - k):
        a = True
        b = True
        for q in range(1, k + 1):
            if not (h[i] > h[i - q] and h[i] > h[i + q]):
                a = False
            if not (l[i] < l[i - q] and l[i] < l[i + q]):
                b = False
        sh[i] = a; sl[i] = b
    return sh, sl


@njit(cache=True)
def h1_structure(sh, sl, h, l, k):
    """dS[j] as of close of bar j (swings confirmed: p + k <= j). +1 HH&HL, -1 LH&LL, else 0."""
    n = len(h)
    out = np.zeros(n, np.int64)
    h1 = h2 = l1 = l2 = np.nan
    nh = nl = 0
    for j in range(n):
        p = j - k
        if p >= k:
            if sh[p]:
                h2 = h1; h1 = h[p]; nh += 1
            if sl[p]:
                l2 = l1; l1 = l[p]; nl += 1
        if nh >= 2 and nl >= 2:
            if h1 > h2 and l1 > l2:
                out[j] = 1
            elif h1 < h2 and l1 < l2:
                out[j] = -1
    return out


@njit(cache=True)
def m5_ref_levels(sh, sl, h, l, k):
    """last confirmed M5 swing-high/low value usable at bar m (confirmed with p + k <= m - 1)."""
    n = len(h)
    rh = np.full(n, np.nan); rl = np.full(n, np.nan)
    cur_h = cur_l = np.nan
    for m in range(n):
        p = m - 1 - k
        if p >= k:
            if sh[p]:
                cur_h = h[p]
            if sl[p]:
                cur_l = l[p]
        rh[m] = cur_h; rl[m] = cur_l
    return rh, rl


@njit(cache=True)
def make_zones(o, h, l, c, atr, sh, sl, bias, k, body_mode, mult, lookback, hmin, hmax, zone_body):
    """Section 3-4. Returns status[B] (0 no BOS, 1 zone created, 2 no_zone, 3 pre_violated, 4 bad_height), zd, zL, zH, bos_count."""
    n = len(o)
    st = np.zeros(n, np.int64); zd = np.zeros(n, np.int64); zL = np.full(n, np.nan); zH = np.full(n, np.nan)
    for B in range(k + 3, n):
        d = bias[B]
        if d == 0 or np.isnan(atr[B - 1]):
            continue
        p = -1
        for q in range(B - 1 - k, -1, -1):
            if (d == 1 and sh[q]) or (d == -1 and sl[q]):
                p = q
                break
        if p < 0:
            continue
        lev = h[p] if d == 1 else l[p]
        if not (d * (c[B] - lev) > 0 and d * (c[B - 1] - lev) <= 0):
            continue
        if not (d * (c[B] - o[B]) > 0):
            continue
        meas = abs(c[B] - o[B]) if body_mode == 0 else (h[B] - l[B])
        if meas < mult * atr[B - 1]:
            continue
        # BOS accepted
        S = p + 1
        for q in range(p + 1, B):
            if d == 1 and l[q] <= l[S]:
                S = q
            if d == -1 and h[q] >= h[S]:
                S = q
        Z = -1
        q = S
        while q >= max(S - lookback, p + 1):
            if (d == 1 and c[q] < o[q]) or (d == -1 and c[q] > o[q]):
                Z = q
                break
            q -= 1
        if Z < 0:
            st[B] = 2
            continue
        if zone_body:
            Lz = min(o[Z], c[Z]); Hz = max(o[Z], c[Z])
        else:
            Lz = l[Z]; Hz = h[Z]
        viol = False
        for q in range(Z, B):
            if (d == 1 and c[q] < Lz) or (d == -1 and c[q] > Hz):
                viol = True
                break
        if viol:
            st[B] = 3
            continue
        ht = (Hz - Lz) / atr[B - 1]
        if ht < hmin or ht > hmax:
            st[B] = 4
            continue
        st[B] = 1; zd[B] = d; zL[B] = Lz; zH[B] = Hz
    return st, zd, zL, zH


@njit(cache=True)
def path_sim(o, h, l, i0, d, stop_bid, tp_bid, i_force, n):
    """M1 path in BID space. BUY (d=1): stop when low<=stop, tp when high>=tp. SELL (d=-1): stop when high>=stop, tp when low<=tp.
    Gap -> open price. Same bar: stop first. Returns (exit_idx, reason 1 tp/2 stop/4 force/5 end, exit_bid_price)."""
    for k in range(i0, n):
        if k >= i_force:
            return k, 4, o[k]
        if d == 1:
            if o[k] <= stop_bid:
                return k, 2, o[k]
            if l[k] <= stop_bid:
                return k, 2, stop_bid
            if o[k] >= tp_bid:
                return k, 1, o[k]
            if h[k] >= tp_bid:
                return k, 1, tp_bid
        else:
            if o[k] >= stop_bid:
                return k, 2, o[k]
            if h[k] >= stop_bid:
                return k, 2, stop_bid
            if o[k] <= tp_bid:
                return k, 1, o[k]
            if l[k] <= tp_bid:
                return k, 1, tp_bid
    return n - 1, 5, o[n - 1]


# ------------------------------------------------------------------ calendar / time helpers
def load_news(path="data/news/usd_high_impact.csv", families=("NFP", "CPI", "GDP", "FOMC")):
    d = pd.read_csv(path, parse_dates=["event_utc"])
    d = d[d.family.isin(families)]
    return np.sort(d.event_utc.to_numpy().astype("datetime64[ns]").astype(np.int64))


def news_ok(start_ns, events_ns, before_min, after_min):
    if events_ns is None or len(events_ns) == 0:
        return np.ones(len(start_ns), bool)
    lo = start_ns - after_min * NS_MIN
    i = np.searchsorted(events_ns, lo, side="left")
    ok = np.ones(len(start_ns), bool)
    has = i < len(events_ns)
    nxt = np.where(has, events_ns[np.minimum(i, len(events_ns) - 1)], np.iinfo(np.int64).max)
    ok[has & (nxt <= start_ns + before_min * NS_MIN)] = False
    return ok


def session_flags(start_ns, sessions):
    ts = pd.to_datetime(start_ns, unit="ns", utc=True)
    ok = np.zeros(len(start_ns), bool)
    for tzname, a, b in sessions:
        loc = ts.tz_convert(TZ[tzname])
        minute = loc.hour * 60 + loc.minute
        ok |= (loc.dayofweek < 5) & (minute >= a) & (minute < b)
    return ok


def ny_day_key(ns):
    ts = pd.to_datetime(ns, unit="ns", utc=True).tz_convert(NYC) - pd.Timedelta(hours=17)
    return (ts.year * 10000 + ts.month * 100 + ts.day).to_numpy().astype(np.int64) if hasattr(ts, "to_numpy") else int(ts.year * 10000 + ts.month * 100 + ts.day)


def next_ny_17(ts_ns):
    t = pd.Timestamp(ts_ns, unit="ns", tz="UTC").tz_convert(NYC)
    c = pd.Timestamp(year=t.year, month=t.month, day=t.day, hour=17, tz=NYC)
    if t >= c:
        c = pd.Timestamp(year=(t + pd.Timedelta(days=1)).year, month=(t + pd.Timedelta(days=1)).month, day=(t + pd.Timedelta(days=1)).day, hour=17, tz=NYC)
    return int(c.tz_convert("UTC").tz_localize(None).value)


def force_ns(ts_ns, minute_of_day):
    t = pd.Timestamp(ts_ns, unit="ns", tz="UTC").tz_convert(NYC)
    c = pd.Timestamp(year=t.year, month=t.month, day=t.day, hour=minute_of_day // 60, minute=minute_of_day % 60, tz=NYC)
    if t >= c:
        n = t + pd.Timedelta(days=1)
        c = pd.Timestamp(year=n.year, month=n.month, day=n.day, hour=minute_of_day // 60, minute=minute_of_day % 60, tz=NYC)
    return int(c.tz_convert("UTC").tz_localize(None).value)


def swap_nights(entry_ns, exit_ns):
    """Rollover (NY 17:00) crossings between entry and exit; Wednesday counts 3."""
    t0 = pd.Timestamp(entry_ns, unit="ns", tz="UTC").tz_convert(NYC)
    t1 = pd.Timestamp(exit_ns, unit="ns", tz="UTC").tz_convert(NYC)
    nights = 0
    day = t0.normalize()
    while day <= t1.normalize():
        roll = pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=17, tz=NYC)
        if t0 < roll <= t1:
            nights += 3 if day.weekday() == 2 else 1
        day += pd.Timedelta(days=1)
    return nights


# ------------------------------------------------------------------ context (all precomputed arrays, no look-ahead)
class Ctx:
    def __init__(self, m1: pd.DataFrame, cfg: dict, news_events=None):
        self.cfg = cfg
        self.m1 = m1
        self.o1, self.h1_, self.l1_, self.c1 = (m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        self.t1 = m1.index.to_numpy().astype("datetime64[ns]").astype(np.int64)
        b5, b15, bh = make_bars(m1, "5min"), make_bars(m1, "15min"), make_bars(m1, "1h")
        self.b5 = b5
        self.s5 = b5.index.to_numpy().astype("datetime64[ns]").astype(np.int64)
        self.e5 = self.s5 + 5 * NS_MIN
        self.o5, self.h5, self.l5, self.c5 = (b5[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        s15 = b15.index.to_numpy().astype("datetime64[ns]").astype(np.int64)
        self.e15 = s15 + 15 * NS_MIN
        self.o15, self.h15, self.l15, self.c15 = (b15[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        sH = bh.index.to_numpy().astype("datetime64[ns]").astype(np.int64)
        eH = sH + 60 * NS_MIN
        cH, hH, lH = bh["close"].to_numpy(float), bh["high"].to_numpy(float), bh["low"].to_numpy(float)
        # H1 bias (section 2)
        e50 = pd.Series(cH).ewm(span=cfg["ema_fast"], adjust=False).mean().to_numpy()
        e200 = pd.Series(cH).ewm(span=cfg["ema_slow"], adjust=False).mean().to_numpy()
        dE = np.where((cH > e50) & (e50 > e200), 1, np.where((cH < e50) & (e50 < e200), -1, 0))
        shH, slH = swing_flags(hH, lH, cfg["kH1"])
        dS = h1_structure(shH, slH, hH, lH, cfg["kH1"])
        biasH = np.where((dE == dS) & (dE != 0), dE, 0)
        biasH[:cfg["ema_slow"] + 50] = 0
        self.biasH = biasH
        # M15
        self.atr15 = atr_sma(self.h15, self.l15, self.c15, cfg["atr_n"])
        sh15, sl15 = swing_flags(self.h15, self.l15, cfg["kM15"])
        kH = np.searchsorted(eH, self.e15, side="right") - 1
        bias15 = np.where(kH >= 0, biasH[np.maximum(kH, 0)], 0)
        self.st15, self.zd15, self.zL15, self.zH15 = make_zones(self.o15, self.h15, self.l15, self.c15, self.atr15, sh15, sl15, bias15, cfg["kM15"],
                                                                0 if cfg["impulse_mode"] == "body" else 1, cfg["impulse_mult"], cfg["zone_lookback"], cfg["zone_hmin"], cfg["zone_hmax"], cfg["zone_body"])
        # M5
        sh5, sl5 = swing_flags(self.h5, self.l5, cfg["kM5"])
        self.ref_h5, self.ref_l5 = m5_ref_levels(sh5, sl5, self.h5, self.l5, cfg["kM5"])
        k5H = np.searchsorted(eH, self.e5, side="right") - 1
        self.bias5 = np.where(k5H >= 0, biasH[np.maximum(k5H, 0)], 0)
        self.k15_5 = np.searchsorted(self.e15, self.e5, side="right") - 1          # last closed M15 at M5 close
        pos = np.searchsorted(self.e15, self.e5, side="left")
        self.b15_5 = np.where((pos < len(self.e15)) & (self.e15[np.minimum(pos, len(self.e15) - 1)] == self.e5), pos, -1)  # M15 closing exactly at this M5 close
        self.sess5 = session_flags(self.s5, cfg["sessions"])
        self.news5 = news_ok(self.s5, news_events, cfg["news_before"], cfg["news_after"])
        self.dk5 = ny_day_key(self.s5)
        self.i0_5 = np.searchsorted(self.t1, self.s5)                                # first M1 index at/after M5 start
        self.force_cache = {}


def _overlap(h, l, Lz, Hz):
    return l <= Hz and h >= Lz


def run_sim(ctx: Ctx, trade_start, trade_end):
    """Main state machine over M5 bars (sections 3-10)."""
    cfg = ctx.cfg
    S = cfg["spread"]
    n5 = len(ctx.s5)
    ts0, ts1 = pd.Timestamp(trade_start).value, pd.Timestamp(trade_end).value
    trades = []
    f = dict(bos_ok=int((ctx.st15 > 0).sum()), z_created=int((ctx.st15 == 1).sum()), z_no_zone=int((ctx.st15 == 2).sum()), z_pre_violated=int((ctx.st15 == 3).sum()), z_bad_height=int((ctx.st15 == 4).sum()),
             episodes=0, episodes_P=0, episodes_M=0, signals=0, retest3_cancel=0, zone_expired=0, zone_replaced=0, zone_invalid_close=0,
             exp_window=0, exp_session=0, exp_news=0, exp_busy=0, exp_block=0, exp_bias=0, exp_zone=0, exp_a1=0, exp_gap=0, exp_pre_start=0, exp_noroom=0, trades=0, breach_exits=0, force_exits=0)
    bal = 1.0
    day_key = None
    E0 = 1.0
    realized = 0.0
    block_until = 0
    busy_until = 0
    zone = None
    side = cfg["side"]
    b15_5, st15 = ctx.b15_5, ctx.st15
    for m in range(n5 - 1):
        if zone is None:
            Bq = b15_5[m]
            if Bq < 0 or st15[Bq] != 1:
                continue
        # ---------- M5-level zone logic
        sig = None
        ending = False
        if zone is not None:
            if ctx.e5[m] >= zone["expire"]:
                zone = None
                f["zone_expired"] += 1
        if zone is not None and m > zone["cm"]:
            Lz, Hz, d = zone["Lz"], zone["Hz"], zone["d"]
            ov = _overlap(ctx.h5[m], ctx.l5[m], Lz, Hz)
            outside = (ctx.l5[m] > Hz) if d == 1 else (ctx.h5[m] < Lz)
            if not zone["in_ep"]:
                if ov:
                    zone["retests"] += 1
                    if zone["retests"] > cfg["max_retests"]:
                        zone = None
                        f["retest3_cancel"] += 1
                    else:
                        zone.update(in_ep=True, pre=False, j0=m, P=[], M=-1, signaled=False)
                        f["episodes"] += 1
            ending = zone is not None and zone["in_ep"] and outside
            if ending and not (cfg["mss_on_exit"] and not zone["pre"]):
                zone.update(in_ep=False, pre=False)
                ending = False
            if zone is not None and zone["in_ep"] and not zone["pre"] and not zone["signaled"] and m <= zone["j0"] + cfg["signal_bars"] - 1:
                o, h, l, c = ctx.o5[m], ctx.h5[m], ctx.l5[m], ctx.c5[m]
                rng_ = h - l
                body = abs(c - o)
                contact = ov and d * (c - zone["Fz"]) > 0
                isP = False
                if contact and rng_ > 0 and m > 0:
                    po, pc, ph, pl = ctx.o5[m - 1], ctx.c5[m - 1], ctx.h5[m - 1], ctx.l5[m - 1]
                    eng = (d * (c - o) > 0 and d * (pc - po) < 0 and ((o <= pc and c >= po) if d == 1 else (o >= pc and c <= po)) and d * (c - (ph if d == 1 else pl)) > 0)
                    rej = (min(o, c) - l) if d == 1 else (h - max(o, c))
                    opp = (h - max(o, c)) if d == 1 else (min(o, c) - l)
                    pin = rej >= cfg["pin_wick_body"] * body and rej >= cfg["pin_wick_range"] * rng_ and opp <= cfg["pin_opp"] * rng_
                    isP = bool(eng or pin)
                if isP:
                    if not zone["P"]:
                        f["episodes_P"] += 1
                    zone["P"].append(m)
                if zone["M"] < 0:
                    f["m_checks"] = f.get("m_checks", 0) + 1
                    lvl = ctx.ref_h5[m] if d == 1 else ctx.ref_l5[m]
                    if not np.isnan(lvl) and d * (c - lvl) > 0:
                        zone["M"] = m
                        f["episodes_M"] += 1
                if zone["M"] >= 0:
                    mm = zone["M"]
                    for p in zone["P"]:
                        if abs(p - mm) <= cfg["confirm_gap"] and max(p, mm) == m:
                            sig = (m, d)
                            zone["signaled"] = True
                            f["signals"] += 1
                            break
        if zone is not None and zone["in_ep"] and ending:
            zone.update(in_ep=False, pre=False)
        ending = False
        # ---------- M15 events closing at this M5 close (invalidation first, then new zone)
        B = ctx.b15_5[m]
        zone_before = zone
        if B >= 0:
            if zone is not None:
                if (zone["d"] == 1 and ctx.c15[B] < zone["Lz"]) or (zone["d"] == -1 and ctx.c15[B] > zone["Hz"]):
                    zone = None
                    f["zone_invalid_close"] += 1
            if ctx.st15[B] == 1:
                if zone is not None:
                    f["zone_replaced"] += 1
                d = int(ctx.zd15[B]); Lz, Hz = float(ctx.zL15[B]), float(ctx.zH15[B])
                zone = dict(d=d, Lz=Lz, Hz=Hz, Fz=Lz if d == 1 else Hz, cm=m, expire=int(ctx.e15[B] + cfg["zone_age_bars"] * 15 * NS_MIN), retests=0, in_ep=False, pre=False, j0=-1, P=[], M=-1, signaled=True)
                if _overlap(ctx.h5[m], ctx.l5[m], Lz, Hz):
                    zone.update(in_ep=True, pre=True)
        # ---------- execution of a signal at next M5 open
        if sig is None:
            continue
        sm, d = sig
        if zone is None or zone is not zone_before:
            f["exp_zone"] += 1
            continue
        te = int(ctx.s5[m + 1])
        if te != int(ctx.e5[m]):
            f["exp_gap"] += 1
            continue
        if te < ts0 or te >= ts1:
            f["exp_pre_start"] += 1
            continue
        if side != 0 and d != side:
            continue
        if not ctx.sess5[m + 1]:
            f["exp_session"] += 1
            continue
        if not ctx.news5[m + 1]:
            f["exp_news"] += 1
            continue
        if te < busy_until:
            f["exp_busy"] += 1
            continue
        dk = int(ctx.dk5[m + 1])
        if dk != day_key:
            day_key, E0, realized = dk, bal, 0.0
        if te < block_until:
            f["exp_block"] += 1
            continue
        if ctx.bias5[m] != d:
            f["exp_bias"] += 1
            continue
        k15 = ctx.k15_5[m]
        atr = ctx.atr15[k15]
        if np.isnan(atr):
            continue
        i0 = int(ctx.i0_5[m + 1])
        if i0 >= len(ctx.t1) or ctx.t1[i0] >= te + 5 * NS_MIN:
            f["exp_noroom"] += 1
            continue
        bid_open = ctx.o1[i0]
        Pe = bid_open + S + cfg["slip_entry"] if d == 1 else bid_open - cfg["slip_entry"]
        Ps = zone["Fz"] - d * cfg["stop_buf"] * atr
        s = d * (Pe - Ps)
        if cfg["use_a1"] and (s < cfg["smin"] * atr or s > cfg["smax"] * atr):
            f["exp_a1"] += 1
            continue
        if s <= 0:
            f["exp_a1"] += 1
            continue
        res = _execute(ctx, cfg, i0, te, d, Pe, Ps, s, bal, E0, realized, dk)
        if res is None:
            f["exp_block"] += 1
            continue
        f["trades"] += 1
        bal = res["bal"]
        realized = res["realized"]
        busy_until = res["exit_ns"]
        if res["block"]:
            block_until = next_ny_17(res["exit_ns"])
        if res["reason"] == 3:
            f["breach_exits"] += 1
        if res["reason"] == 4:
            f["force_exits"] += 1
        res.update(entry=pd.Timestamp(te), d=d, zone_L=zone["Lz"], zone_H=zone["Hz"], atr=atr)
        trades.append(res)
        zone = None
    return pd.DataFrame(trades), f


def _execute(ctx, cfg, i0, te, d, Pe, Ps, s, bal, E0, realized, dk):
    """Open a trade at M1 index i0 (entry price Pe in the executed-price space), run the M1 path, return result dict or None if blocked."""
    S = cfg["spread"]
    risk_usd = cfg["risk"] * bal
    oz = risk_usd / s
    comm = cfg["commission"] * oz
    allowed = cfg["daily_loss"] * E0 + realized - comm
    if allowed <= 0:
        return None
    ap = allowed / oz                                   # price distance to the daily-limit breach
    Pt = Pe + d * cfg["rr"] * s
    if d == 1:
        sl_bid, tp_bid, br_bid = Ps, Pt, Pe - ap
        use_br = br_bid > sl_bid
        stop_bid = br_bid if use_br else sl_bid
    else:
        sl_bid, tp_bid, br_bid = Ps - S, Pt - S, Pe + ap - S
        use_br = br_bid < sl_bid
        stop_bid = br_bid if use_br else sl_bid
    if cfg["force_close"]:
        fk = (dk, cfg["force_min"])
        if fk not in ctx.force_cache:
            ctx.force_cache[fk] = int(np.searchsorted(ctx.t1, force_ns(te, cfg["force_min"])))
        i_force = ctx.force_cache[fk]
    else:
        i_force = len(ctx.t1)
    xi, reason, xp = path_sim(ctx.o1, ctx.h1_, ctx.l1_, i0, d, stop_bid, tp_bid, i_force, len(ctx.t1))
    if reason == 2 and use_br:
        reason = 3
    exit_ns = int(ctx.t1[xi]) + NS_MIN
    slip = cfg["slip_sl"] if reason == 2 else 0.0
    if d == 1:
        pnl_oz = (xp - slip) - Pe
    else:
        pnl_oz = Pe - (xp + S + slip)
    swap = 0.0
    if not cfg["force_close"]:
        swap = cfg["swap_annual"] * Pe / 365.0 * swap_nights(te, exit_ns)
    net_oz = pnl_oz - cfg["commission"] - swap
    pnl_usd = net_oz * oz
    R = net_oz / s
    bal2 = bal + pnl_usd
    realized2 = realized + pnl_usd
    block = reason == 3 or realized2 <= -cfg["daily_loss"] * E0 + 1e-12
    return dict(R=R, reason=reason, exit_ns=exit_ns, exit=pd.Timestamp(exit_ns), bal=bal2, realized=realized2, block=block, s=s, Pe=Pe, Ps=Ps, Pt=Pt, hold_min=(exit_ns - te) / NS_MIN)


# ------------------------------------------------------------------ random-entry control (test plan section 6)
def random_control(ctx: Ctx, real: pd.DataFrame, trade_start, trade_end, n_draws=1000, seed=11):
    """Same period/bias/session/news/risk/costs/limits/forced close/TP 2R; direction = bias; stop distance (in ATR units) sampled from real trades."""
    cfg = ctx.cfg
    S = cfg["spread"]
    rng = np.random.default_rng(seed)
    n5 = len(ctx.s5)
    ts0, ts1 = pd.Timestamp(trade_start).value, pd.Timestamp(trade_end).value
    k15 = ctx.k15_5
    ok = np.zeros(n5, bool)
    m_idx = np.arange(n5 - 1)
    nxt_ok = (ctx.s5[1:] == ctx.e5[:-1])
    valid = (ctx.bias5[:-1] != 0) & ctx.sess5[1:] & ctx.news5[1:] & nxt_ok & (ctx.s5[1:] >= ts0) & (ctx.s5[1:] < ts1) & (k15[:-1] >= 0)
    valid &= ~np.isnan(ctx.atr15[np.maximum(k15[:-1], 0)])
    elig = m_idx[valid]
    rho = (real.s / real.atr).to_numpy()
    N = len(real)
    means = []
    if N == 0 or len(elig) < N:
        return np.array([]), len(elig)
    for _ in range(n_draws):
        cand = np.sort(rng.choice(elig, size=min(len(elig), max(6 * N, N + 100)), replace=False))
        bal, day_key, E0, realized, block_until, busy_until = 1.0, None, 1.0, 0.0, 0, 0
        Rs = []
        for m in cand:
            te = int(ctx.s5[m + 1])
            if te < busy_until:
                continue
            dk = int(ctx.dk5[m + 1])
            if dk != day_key:
                day_key, E0, realized = dk, bal, 0.0
            if te < block_until:
                continue
            i0 = int(ctx.i0_5[m + 1])
            if i0 >= len(ctx.t1) or ctx.t1[i0] >= te + 5 * NS_MIN:
                continue
            d = int(ctx.bias5[m])
            atr = ctx.atr15[k15[m]]
            bid_open = ctx.o1[i0]
            Pe = bid_open + S + cfg["slip_entry"] if d == 1 else bid_open - cfg["slip_entry"]
            s = rho[rng.integers(0, len(rho))] * atr
            Ps = Pe - d * s
            res = _execute(ctx, cfg, i0, te, d, Pe, Ps, s, bal, E0, realized, dk)
            if res is None:
                continue
            bal, realized, busy_until = res["bal"], res["realized"], res["exit_ns"]
            if res["block"]:
                block_until = next_ny_17(res["exit_ns"])
            Rs.append(res["R"])
            if len(Rs) >= N:
                break
        if len(Rs) == N:
            means.append(float(np.mean(Rs)))
    return np.array(means), len(elig)
