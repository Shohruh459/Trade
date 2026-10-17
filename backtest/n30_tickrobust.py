"""Python port of XAU_Quant_Reversion_TickRobust.mq5 (n30dyn4m1c/gold-pro-scalper) for an independent M1 test on XAUUSD.

The EA decides once per bar from CLOSED-bar values, so a bar-level port is close to the EA's own logic:
- entry at a bar open: closed-bar Z (SMA20/StdDev20) beyond +-2.2, turn confirmation, ADX<=22, ATR(14)/avg(50) in [0.4, 2.0],
  cost gate (StdDev >= 3x cost, distance to mean >= 4x cost), H1 SMA50 alignment, 10:00-20:00 broker time, loss cooldown 15 min.
- server-side SL = max(800 pts, 2.5*ATR) and a limit TP at the mean (re-targeted every bar, "gravity"); exits at a bar open:
  closed-bar |Z| <= 0.2, 40 bars max hold, Friday 20:00 close, breakeven after 1*ATR; dynamic risk tiers and daily loss limit.
NOT ported (no data): the MQL5 economic-calendar news filter (red-folder USD events). Spread is a constant (data has none).
Approximations: MT5 ATR = SMA(TR,14); ADX = Wilder; SL before TP when both are inside one M1 bar; stop level assumed 0.
Broker time = Europe/Athens (the data source's server time), which is what the EA's 10-20 window refers to.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .strategies import adx as adx_fn


@dataclass
class P:
    entry_z: float = 2.2
    require_turn: bool = True
    exit_z: float = 0.2
    max_hold: int = 40
    sl_pts: float = 800.0
    sl_atr: float = 2.5
    be_atr: float = 1.0
    start_hour: int = 10
    end_hour: int = 20
    friday_close_hour: int = 20
    cooldown_min: int = 15
    point: float = 0.01
    spread: float = 0.25               # USD/oz (25 points)
    commission_per_oz: float = 0.0     # XM-style micro: spread only; use 0.07 for $7/lot
    min_sd_cost: float = 3.0
    min_tp_cost: float = 4.0
    max_spread_pts: float = 50.0
    ma_period: int = 20
    adx_max: float = 22.0
    h1_sma: int = 50
    atr_avg: int = 50
    max_atr_ratio: float = 2.0
    min_atr_ratio: float = 0.4
    dynamic_risk: bool = True
    risk_pct: float = 2.0
    daily_loss_pct_fixed: float = 15.0
    start_balance: float = 10_000.0
    max_leverage: float = 200.0


def tiers(eq):
    for lim, r, dl in ((500, 10.0, 25.0), (2000, 7.0, 20.0), (5000, 5.0, 15.0), (20000, 3.0, 10.0)):
        if eq < lim:
            return r, dl
    return 1.5, 7.0


def prepare(df, p: P):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    cs = df["close"]
    ma = cs.rolling(p.ma_period).mean().to_numpy()
    sd = cs.rolling(p.ma_period).std(ddof=0).to_numpy()
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    ratio = atr / pd.Series(atr).rolling(p.atr_avg).mean().to_numpy()
    adx = adx_fn(df).to_numpy()
    h1 = df["close"].resample("1h").last().dropna()
    sma = h1.rolling(p.h1_sma).mean()
    pos = np.clip(h1.index.searchsorted(df.index.floor("1h"), side="left") - 1, 0, len(h1) - 1)
    h1sma = sma.to_numpy()[pos]
    loc = df.index.tz_convert("Europe/Athens")
    return dict(o=o, h=h, l=l, c=c, ma=ma, sd=sd, atr=atr, ratio=ratio, adx=adx, h1sma=h1sma,
                hour=loc.hour.to_numpy(), wday=loc.dayofweek.to_numpy(), day=loc.normalize().to_numpy(), ts=df.index.to_numpy())


def candidates(d, p: P):
    """Vectorised entry conditions evaluated at bar i from bars <= i-1 and the open of bar i."""
    n = len(d["o"])
    sh = lambda a, k=1: np.r_[np.full(k, np.nan), a[:-k]]
    z1 = sh((d["c"] - d["ma"]) / d["sd"])
    c1, c2, ma1, sd1, atr1, ratio1, adx1 = sh(d["c"]), sh(d["c"], 2), sh(d["ma"]), sh(d["sd"]), sh(d["atr"]), sh(d["ratio"]), sh(d["adx"])
    o, sp, pt = d["o"], p.spread, p.point
    dirn = np.where(z1 <= -p.entry_z, 1, np.where(z1 >= p.entry_z, -1, 0))
    ok = dirn != 0
    if p.require_turn:
        ok &= ~((dirn == 1) & (c1 < c2)) & ~((dirn == -1) & (c1 > c2))
    ok &= (adx1 <= p.adx_max) & (ratio1 <= p.max_atr_ratio) & (ratio1 >= p.min_atr_ratio) & (atr1 > 0)
    cost = sp / pt
    ok &= (sp / pt <= p.max_spread_pts) & (sd1 / pt >= p.min_sd_cost * cost)
    tpd = np.where(dirn == 1, (ma1 - (o + sp)) / pt, ((o) - ma1) / pt)
    ok &= tpd >= p.min_tp_cost * cost
    ok &= np.where(dirn == 1, o > d["h1sma"], o < d["h1sma"])
    ok &= (d["hour"] >= p.start_hour) & (d["hour"] < p.end_hour) & (d["wday"] < 5)
    ok &= np.isfinite(z1) & np.isfinite(d["h1sma"])
    return np.where(ok, dirn, 0), z1, ma1, atr1


def run(df, p: P = P()):
    d = prepare(df, p)
    cand, z1, ma1, atr1 = candidates(d, p)
    o, h, l, ts, hour, wday, day = d["o"], d["h"], d["l"], d["ts"], d["hour"], d["wday"], d["day"]
    sp, pt = p.spread, p.point
    n = len(o)
    eq, pos, trades = p.start_balance, None, []
    cool_until, day_key, day_start, halted = None, None, eq, False

    def close(i, px, reason):
        nonlocal eq, pos, cool_until
        pnl = (px - pos["entry"]) * pos["dir"] * pos["units"] - p.commission_per_oz * pos["units"]
        eq += pnl
        trades.append(dict(entry_time=pos["t"], exit_time=ts[i], dir=pos["dir"], entry=pos["entry"], exit=px, units=pos["units"], pnl=pnl,
                           r=pnl / (pos["units"] * pos["sl0"]), reason=reason, equity=eq, bars=i - pos["i0"]))
        if pnl < 0 and p.cooldown_min > 0:
            cool_until = ts[i] + np.timedelta64(p.cooldown_min, "m")
        pos = None

    def intrabar(i):
        dr, sl, tp = pos["dir"], pos["sl"], pos["tp"]
        if dr == 1:
            if o[i] <= sl:
                return o[i], "sl_gap"
            if l[i] <= sl:
                return sl, "sl"
            if h[i] >= tp:
                return tp, "tp"
        else:
            if o[i] + sp >= sl:
                return o[i] + sp, "sl_gap"
            if h[i] + sp >= sl:
                return sl, "sl"
            if l[i] + sp <= tp:
                return tp, "tp"
        return None

    for i in range(100, n):
        if day[i] != day_key:
            day_key, day_start, halted = day[i], eq, False
        if pos is not None:
            px_close = o[i] if pos["dir"] == 1 else o[i] + sp          # market exit price at this bar open
            unreal = (px_close - pos["entry"]) * pos["dir"] * pos["units"]
            lim = tiers(eq)[1] if p.dynamic_risk else p.daily_loss_pct_fixed
            if (day_start - (eq + unreal)) / day_start * 100 >= lim:
                halted = True
                close(i, px_close, "daily_limit")
                continue
            if wday[i] >= 5 or (wday[i] == 4 and hour[i] >= p.friday_close_hour):
                close(i, px_close, "friday")
                continue
            if (pos["dir"] == 1 and z1[i] >= -p.exit_z) or (pos["dir"] == -1 and z1[i] <= p.exit_z):
                close(i, px_close, "z_revert")
                continue
            if i - pos["i0"] >= p.max_hold:
                close(i, px_close, "time")
                continue
            a1, m1, e, spp = atr1[i], ma1[i], pos["entry"], sp / pt
            if p.be_atr > 0:
                if pos["dir"] == 1 and o[i] - e >= p.be_atr * a1:
                    be = e + (spp + 2) * pt
                    if be > pos["sl"] + 10 * pt:
                        pos["sl"] = be
                elif pos["dir"] == -1 and e - (o[i] + sp) >= p.be_atr * a1:
                    be = e - (spp + 2) * pt
                    if be < pos["sl"] - 10 * pt:
                        pos["sl"] = be
            if pos["dir"] == 1:
                tgt = max(m1, e + (spp + 5) * pt)
                if tgt < pos["tp"] - 20 * pt and tgt - o[i] > 0:
                    pos["tp"] = tgt
            else:
                tgt = min(m1, e - (spp + 5) * pt)
                if tgt > pos["tp"] + 20 * pt and (o[i] + sp) - tgt > 0:
                    pos["tp"] = tgt
            res = intrabar(i)
            if res:
                close(i, *res)
        elif cand[i] != 0 and not halted and (cool_until is None or ts[i] >= cool_until):
            dr = int(cand[i])
            entry = o[i] + sp if dr == 1 else o[i]
            sl_dist = max(p.sl_pts * pt, p.sl_atr * atr1[i])
            risk_pct = tiers(eq)[0] if p.dynamic_risk else p.risk_pct
            units = np.floor(eq * risk_pct / 100 / sl_dist)               # 0.01 lot steps = 1 oz
            units = min(units, np.floor(eq * p.max_leverage / entry))
            if units < 1:
                continue
            pos = dict(dir=dr, entry=entry, units=units, i0=i, t=ts[i], sl=entry - dr * sl_dist, sl0=sl_dist, tp=ma1[i])
            res = intrabar(i)
            if res:
                close(i, *res)
    if pos is not None:
        close(n - 1, o[-1] if pos["dir"] == 1 else o[-1] + sp, "end")
    return pd.DataFrame(trades)
