"""M1 bar-level ports of two more gold-pro-scalper variants (n30dyn4m1c/gold-pro-scalper):
 - Classic MR  (XAU_Quant_Reversion_m1_OLHC.mq5): closed-bar Z beyond +-2.0 (+0.5 if ATR ratio>1.5) AND live Z >= 90% of it, H1 SMA50 alignment,
   ADX<=25, ATR-relative spread gate (spread <= 12% of M1 ATR), 10-20 broker hour window, SL 800 pts / hard TP 1500 pts, gravity Z-exit
   (0.5 decaying to 0 after 15 min), 30 min max hold, breakeven at 1.5*ATR+50 pts, ATR trail (2.0x, halved after 15 min), 10 min loss cooldown,
   Friday 20:00 close, dynamic risk tiers, daily loss limit.
 - Trend Breakout (the TB half of XAU_Quant_Reversion_Breakout.mq5): new-bar entry when price breaks the 30-bar Donchian extreme with ADX>=30,
   DI spread>=5, EMA50 side, ATR(14)/ATR(50)>=0.5; SL 1000 pts / hard TP 2000 pts; ATR x2.0 trail on new bars; 10-bar cooldown; risk = 0.3 x tier.
Approximations: decisions use the first tick of a bar ~ bar open; 'live' indicators of the forming bar are replaced by closed-bar values (live Z is
rebuilt from the bar open); the 3-tick/2-second entry confirmation and tick velocity block are ignored; SL before TP inside a bar; BE/trail changes apply
from the next bar; no news filter (no data); spread constant. Broker time = Europe/Athens.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


def tiers(eq):
    for lim, r, dl in ((500, 10.0, 25.0), (2000, 7.0, 20.0), (5000, 5.0, 15.0), (20000, 3.0, 10.0)):
        if eq < lim:
            return r, dl
    return 1.5, 7.0


def wilder(x, n=14):
    return pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def prepare(df):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr14 = pd.Series(tr).rolling(14).mean().to_numpy()
    atr50 = pd.Series(tr).rolling(50).mean().to_numpy()
    up, dn = np.r_[0, np.diff(h)], -np.r_[0, np.diff(l)]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = wilder(tr)
    pdi, mdi = 100 * wilder(pdm) / a, 100 * wilder(mdm) / a
    dx = 100 * np.abs(pdi - mdi) / np.where(pdi + mdi == 0, np.nan, pdi + mdi)
    adx = wilder(np.nan_to_num(dx))
    cs = pd.Series(c)
    ma, sd = cs.rolling(20).mean().to_numpy(), cs.rolling(20).std(ddof=0).to_numpy()
    s19, q19 = cs.rolling(19).sum().to_numpy(), (cs ** 2).rolling(19).sum().to_numpy()
    h1 = df["close"].resample("1h").last().dropna()
    pos = np.clip(h1.index.searchsorted(df.index.floor("1h"), side="left") - 1, 0, len(h1) - 1)
    h1sma = h1.rolling(50).mean().to_numpy()[pos]
    ema50 = cs.ewm(span=50, adjust=False).mean().to_numpy()
    loc = df.index.tz_convert("Europe/Athens")
    return dict(o=o, h=h, l=l, c=c, atr14=atr14, atr50=atr50, adx=adx, pdi=pdi, mdi=mdi, ma=ma, sd=sd, s19=s19, q19=q19, h1sma=h1sma, ema50=ema50,
                hour=loc.hour.to_numpy(), wday=loc.dayofweek.to_numpy(), day=loc.normalize().to_numpy(), ts=df.index.to_numpy())


@dataclass
class MR:
    entry_z: float = 2.0
    exit_z: float = 0.5
    sl_usd: float = 8.0
    tp_usd: float = 15.0
    max_hold: int = 30
    cooldown_min: int = 10
    adx_max: float = 25.0
    spread: float = 0.25
    atr_gate: float = 0.12
    start_balance: float = 10_000.0


@dataclass
class TB:
    donchian: int = 30
    adx_min: float = 30.0
    di_spread: float = 5.0
    sl_usd: float = 10.0
    tp_usd: float = 20.0
    trail_atr: float = 2.0
    cooldown_bars: int = 10
    spread: float = 0.25
    risk_scale: float = 0.3
    start_balance: float = 10_000.0


def sim(d, p, kind):
    o, h, l, ts, hour, wday, day = d["o"], d["h"], d["l"], d["ts"], d["hour"], d["wday"], d["day"]
    n, sp = len(o), p.spread
    atr, ma, sd, adx = d["atr14"], d["ma"], d["sd"], d["adx"]
    sh = lambda a, k=1: np.r_[np.full(k, np.nan), a[:-k]]
    c1, atr1, adx1, ma1, sd1 = sh(d["c"]), sh(atr), sh(adx), sh(ma), sh(sd)
    win = (hour >= 10) & (hour < 20) & (wday < 5)
    if kind == "mr":
        z1 = (c1 - ma1) / sd1
        ravg = sh(pd.Series(atr).rolling(100).mean().to_numpy())
        ez = p.entry_z + np.where(atr1 / ravg > 1.5, 0.5, 0.0)
        ma0 = (sh(d["s19"]) + o) / 20
        sd0 = np.sqrt(np.maximum((sh(d["q19"]) + o ** 2) / 20 - ma0 ** 2, 1e-12))
        live = (o - ma0) / sd0
        gate = (sp / 0.01 <= p.atr_gate * atr1 / 0.01) & (sp / 0.01 <= 50)
        ok = win & gate & (adx1 <= p.adx_max) & np.isfinite(z1) & np.isfinite(d["h1sma"])
        cand = np.where(ok & (z1 < -ez) & (live <= -0.9 * ez) & (o > d["h1sma"]), 1, np.where(ok & (z1 > ez) & (live >= 0.9 * ez) & (o < d["h1sma"]), -1, 0))
        gate_share = float(np.nanmean(((sp / 0.01 <= p.atr_gate * atr1 / 0.01) & win)[win]))
    else:
        hi, lo = pd.Series(d["h"]).rolling(p.donchian).max().to_numpy(), pd.Series(d["l"]).rolling(p.donchian).min().to_numpy()
        dh, dl = sh(hi), sh(lo)
        pdi1, mdi1, e1 = sh(d["pdi"]), sh(d["mdi"]), sh(d["ema50"])
        vol = atr1 / sh(d["atr50"]) >= 0.5
        ok = win & (adx1 >= p.adx_min) & vol & (np.abs(pdi1 - mdi1) >= p.di_spread) & np.isfinite(dh)
        cand = np.where(ok & (o + sp > dh) & (pdi1 > mdi1) & (o > e1), 1, np.where(ok & (o < dl) & (mdi1 > pdi1) & (o + sp < e1), -1, 0))
        z1 = np.zeros(n)
        gate_share = float("nan")
    eq, pos, trades, cool_until, dkey, dstart, halted, last_close_i = p.start_balance, None, [], None, None, p.start_balance, False, -10 ** 9

    def close(i, px, reason):
        nonlocal eq, pos, cool_until, last_close_i
        pnl_oz = (px - pos["entry"]) * pos["dir"]
        eq += pnl_oz * pos["units"]
        trades.append(dict(entry_time=pos["t"], exit_time=ts[i], dir=pos["dir"], entry=pos["entry"], exit=px, units=pos["units"], pnl=pnl_oz * pos["units"],
                           r=pnl_oz / p.sl_usd, reason=reason, bars=i - pos["i0"]))
        if pnl_oz < 0 and kind == "mr":
            cool_until = ts[i] + np.timedelta64(p.cooldown_min, "m")
        last_close_i = i
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

    for i in range(120, n):
        if day[i] != dkey:
            dkey, dstart, halted = day[i], eq, False
        if pos is not None:
            px = o[i] if pos["dir"] == 1 else o[i] + sp
            unreal = (px - pos["entry"]) * pos["dir"] * pos["units"]
            lim = tiers(eq)[1]
            if (dstart - (eq + unreal)) / dstart * 100 >= lim:
                halted = True
                close(i, px, "daily_limit")
                continue
            if kind == "mr" and (wday[i] >= 5 or (wday[i] == 4 and hour[i] >= 20)):
                close(i, px, "friday")
                continue
            held = i - pos["i0"]
            a = atr1[i]
            if kind == "mr":
                if held >= p.max_hold:
                    close(i, px, "time")
                    continue
                gz = 0.0 if held >= 15 else max(0.0, p.exit_z - (held // 5) * 0.1)
                if (pos["dir"] == 1 and z1[i] >= -gz) or (pos["dir"] == -1 and z1[i] <= gz):
                    close(i, px, "gravity")
                    continue
                if pos["be_hit"] and ((pos["dir"] == 1 and pos["be"] > pos["sl"]) or (pos["dir"] == -1 and pos["be"] < pos["sl"])):
                    pos["sl"] = pos["be"]
                mult = 2.0 * (0.5 if held * 60 > 900 else 1.0)
                if pos["dir"] == 1:
                    ns = o[i] - a * mult
                    if ns > pos["sl"] + 0.3 * a:
                        pos["sl"] = ns
                else:
                    ns = o[i] + sp + a * mult
                    if ns < pos["sl"] - 0.3 * a:
                        pos["sl"] = ns
            else:
                if pos["dir"] == 1:
                    ns = o[i] - a * p.trail_atr
                    if ns > pos["sl"] + 0.2 * a:
                        pos["sl"] = ns
                else:
                    ns = o[i] + sp + a * p.trail_atr
                    if ns < pos["sl"] - 0.2 * a:
                        pos["sl"] = ns
            res = intrabar(i)
            if res:
                close(i, *res)
            elif kind == "mr":                                         # breakeven trigger from this bar's extreme (applies next bar)
                trig = 1.5 * atr1[i] + 0.5
                if pos["dir"] == 1 and h[i] - pos["entry"] >= trig:
                    pos["be_hit"], pos["be"] = True, pos["entry"] + 0.10
                elif pos["dir"] == -1 and pos["entry"] - (l[i] + sp) >= trig:
                    pos["be_hit"], pos["be"] = True, pos["entry"] - 0.10
        elif cand[i] != 0 and not halted:
            if kind == "mr" and cool_until is not None and ts[i] < cool_until:
                continue
            if kind == "tb" and i - last_close_i <= p.cooldown_bars:
                continue
            dr = int(cand[i])
            entry = o[i] + sp if dr == 1 else o[i]
            risk_pct = tiers(eq)[0] * (p.risk_scale if kind == "tb" else 1.0)
            units = np.floor(eq * risk_pct / 100 / p.sl_usd)
            units = min(units, np.floor(eq * 200 / entry))
            if units < 1:
                continue
            pos = dict(dir=dr, entry=entry, units=units, i0=i, t=ts[i], sl=entry - dr * p.sl_usd, tp=entry + dr * p.tp_usd, be_hit=False, be=0.0)
            res = intrabar(i)
            if res:
                close(i, *res)
    if pos is not None:
        close(n - 1, o[-1] if pos["dir"] == 1 else o[-1] + sp, "end")
    return pd.DataFrame(trades), gate_share
