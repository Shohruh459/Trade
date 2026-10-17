"""Python port of the rules in foeed/FvgGold-EA (FvgGold.mq5 v2.01) for an independent bar-based test on XAUUSD M15.

Faithfulness notes (what was ported, what is approximated):
- FVG detection (3-candle gap >= MinGapSize), age 2..20 bars, quality score (gap/disp/HTF/fresh/premium-discount + OB bonus),
  H1 EMA50/200 bias (last completed H1 bar), killzone (07-10, 12-21 UTC), buy/sell LIMIT at edge +/- buffer/2,
  SL beyond edge by buffer, TP = 1.5R, break-even at 0.5*ATR, one trade or pending at a time, $5 daily loss limit.
- Pending orders are GTC (never cancelled), exactly as in the EA, so a stale pending order blocks new ones until it fills.
- Bar-level approximations: decisions at the open of bar i from bars <= i-1; zone mitigation judged at the bar open;
  break-even takes effect from the next bar; MT5 ATR = SMA(TR,14). Candles are BID; spread is added where the ask matters.
- Same-bar fill + TP/SL ambiguity: mode "pessimistic" credits no TP on the fill bar, "optimistic" credits it when reachable.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class P:
    min_gap: float = 0.25        # MinGapSize 25 points * 0.01
    max_age: int = 20
    min_age: int = 2
    buffer: float = 3.0
    min_score: float = 50.0
    w_gap: float = 30.0
    w_disp: float = 30.0
    w_htf: float = 20.0
    w_fresh: float = 10.0
    w_pd: float = 10.0
    use_ob: bool = True
    ob_imp_atr: float = 1.5
    ob_lookback: int = 50
    ob_min: float = 0.10         # 10 points
    ob_bonus: float = 20.0
    ob_maxdist: float = 2.0      # 200 points
    ema_fast: int = 50
    ema_slow: int = 200
    sizing: str = "fixed"        # "fixed" = FixedLot 0.01 (1 oz); "risk" = RiskPercent 0.5 with EA cap of 10 oz
    fixed_oz: float = 1.0
    risk_pct: float = 0.5
    max_oz: float = 10.0
    daily_loss: float = 5.0      # USD, as in the EA (not scaled with size)
    rr: float = 1.5
    be_atr: float = 0.5
    be_offset: float = 0.02
    kz_london: tuple = (7, 10)
    kz_overlap_start: int = 12
    kz_ny_end: int = 21
    spread: float = 0.25         # USD per oz (25 cents)
    commission_per_oz: float = 0.07   # $7 per 100 oz round turn
    start_balance: float = 10_000.0
    fill_bar_mode: str = "pessimistic"
    close_eod: bool = False      # the EA's own CloseAtEOD option (closes positions, deletes pendings at 21:55 GMT)
    pend_expire: int = 0         # OUR modification (not in the EA): cancel a pending order after N bars (0 = never, as published)


def prepare(df: pd.DataFrame, p: P):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(df)
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()          # MT5 iATR = SMA of TR
    h1 = df["close"].resample("1h").last().dropna()
    ef, es = h1.ewm(span=p.ema_fast, adjust=False).mean(), h1.ewm(span=p.ema_slow, adjust=False).mean()
    bias_h1 = np.sign((ef - es).to_numpy())
    # last COMPLETED H1 bar for each M15 bar
    pos = h1.index.searchsorted(df.index.floor("1h"), side="left") - 1
    pos = np.clip(pos, 0, len(h1) - 1)
    bias, ema_f = bias_h1[pos], ef.to_numpy()[pos]
    # FVG candidates keyed by the middle candle j
    ftype, ftop, fbot = np.zeros(n, int), np.zeros(n), np.zeros(n)
    bull = l[2:] > h[:-2]
    bear = h[2:] < l[:-2]
    j = np.arange(1, n - 1)
    gb, gr = l[2:] - h[:-2], l[:-2] - h[2:]
    mb, mr = bull & (gb >= p.min_gap), bear & (gr >= p.min_gap)
    ftype[j[mb]], ftop[j[mb]], fbot[j[mb]] = 1, l[2:][mb], h[:-2][mb]
    ftype[j[mr]], ftop[j[mr]], fbot[j[mr]] = -1, l[:-2][mr], h[2:][mr]
    rng = h - l
    disp = np.where(rng > 0, np.abs(c - o) / np.where(rng > 0, rng, 1), 0.0)
    return dict(o=o, h=h, l=l, c=c, atr=atr, bias=bias, ema_f=ema_f, ftype=ftype, ftop=ftop, fbot=fbot, disp=disp)


def ob_confluence(d, i, ftype, ftop, fbot, p: P):
    o, c, atr = d["o"], d["c"], d["atr"][i - 1]
    if not np.isfinite(atr) or atr <= 0:
        return False
    s = np.arange(2, p.ob_lookback)                 # shift of the impulse candle (0 = forming bar i)
    k = i - s
    k = k[k - 1 >= 0]
    s = i - k
    o2, c2, o1, c1 = o[k], c[k], o[k - 1], c[k - 1]
    big = np.abs(c2 - o2) >= atr * p.ob_imp_atr
    bullob = big & (c2 > o2) & (c1 < o1) & (ftype == 1)
    bearob = big & (c2 < o2) & (c1 > o1) & (ftype == -1)
    m = bullob | bearob
    if not m.any():
        return False
    top, bot = np.maximum(o1, c1)[m], np.minimum(o1, c1)[m]
    ok = (top - bot) >= p.ob_min
    bid = o[i]
    ask = bid + p.spread
    alive = (bid >= bot) if ftype == 1 else (ask <= top)
    sel = ok & alive
    if not sel.any():
        return False
    top, bot = top[sel], bot[sel]
    overlap = (ftop >= bot) & (fbot <= top)
    dist = (fbot - top) if ftype == 1 else (bot - ftop)
    return bool((overlap | ((dist >= 0) & (dist <= p.ob_maxdist))).any())


def score_zone(d, i, j, p: P, allow_ob=True):
    t, top, bot = d["ftype"][j], d["ftop"][j], d["fbot"][j]
    atr = d["atr"][i - 1]
    if not np.isfinite(atr) or atr <= 0:
        return None
    sc = min((top - bot) / atr, 1.0) * p.w_gap + d["disp"][j] * p.w_disp
    if t == d["bias"][i]:
        sc += p.w_htf
    sc += (1.0 - (i - j) / p.max_age) * p.w_fresh
    dist = d["o"][i] - d["ema_f"][i]
    if (t == 1 and dist < 0) or (t == -1 and dist > 0):
        sc += p.w_pd
    if p.use_ob and sc < p.min_score and sc + p.ob_bonus >= p.min_score and allow_ob:
        if ob_confluence(d, i, t, top, bot, p):
            sc += p.ob_bonus
    elif p.use_ob and sc >= p.min_score:
        if ob_confluence(d, i, t, top, bot, p):
            sc += p.ob_bonus
    return sc


def run(df: pd.DataFrame, p: P = P(), trace=None):
    d = prepare(df, p)
    o, h, l, c, atr, bias = d["o"], d["h"], d["l"], d["c"], d["atr"], d["bias"]
    idx = df.index
    hours, days = idx.hour.to_numpy(), idx.normalize().to_numpy()
    n = len(df)
    sp = p.spread
    equity, pend, pos = p.start_balance, None, None
    zones: dict = {}
    trades, day_key, day_pnl = [], None, 0.0

    def finish(i, px, reason):
        nonlocal equity, pos, day_pnl
        dr = pos["dir"]
        pnl = (px - pos["fill"]) * dr * pos["units"] - p.commission_per_oz * pos["units"]
        equity += pnl
        day_pnl += pnl
        trades.append(dict(entry_time=pos["time"], exit_time=idx[i], dir=dr, entry=pos["fill"], exit=px, units=pos["units"],
                           pnl=pnl, r=pnl / (pos["units"] * pos["sl_dist"]), reason=reason, equity=equity, score=pos["score"]))
        pos = None

    def exit_check(i, fresh):
        dr, sl, tp = pos["dir"], pos["sl"], pos["tp"]
        if dr == 1:
            if not fresh and o[i] <= sl:
                return o[i], "sl_gap"
            if l[i] <= sl:
                return sl, "sl"
            if h[i] >= tp and (not fresh or p.fill_bar_mode == "optimistic"):
                return tp, "tp"
        else:
            if not fresh and o[i] + sp >= sl:
                return o[i] + sp, "sl_gap"
            if h[i] + sp >= sl:
                return sl, "sl"
            if l[i] + sp <= tp and (not fresh or p.fill_bar_mode == "optimistic"):
                return tp, "tp"
        return None

    def update_be(i):
        trig = p.be_atr * atr[i - 1]
        if not np.isfinite(trig):
            return
        if pos["dir"] == 1 and h[i] - pos["fill"] >= trig and pos["sl"] < pos["fill"]:
            pos["sl"] = pos["fill"] + p.be_offset
        elif pos["dir"] == -1 and pos["fill"] - (l[i] + sp) >= trig and pos["sl"] > pos["fill"]:
            pos["sl"] = pos["fill"] - p.be_offset

    for i in range(300, n):
        if days[i] != day_key:
            day_key, day_pnl = days[i], 0.0
        if pos is not None:                                           # 1. manage open position
            res = exit_check(i, fresh=False)
            if res:
                finish(i, *res)
            else:
                update_be(i)
        # 2. zone maintenance
        for j in [j for j in zones if (i - j) > p.max_age or (zones[j]["t"] == 1 and o[i] < zones[j]["mid"]) or (zones[j]["t"] == -1 and o[i] + sp > zones[j]["mid"])]:
            del zones[j]
        for j in range(i - p.max_age, i - p.min_age + 1):
            if j < 1 or j in zones or d["ftype"][j] == 0:
                continue
            t = d["ftype"][j]
            mid = (d["ftop"][j] + d["fbot"][j]) / 2
            if (t == 1 and o[i] < mid) or (t == -1 and o[i] + sp > mid):
                continue
            sc = score_zone(d, i, j, p)
            if sc is not None and sc >= p.min_score:
                zones[j] = dict(t=t, top=d["ftop"][j], bot=d["fbot"][j], mid=mid, score=sc, placed=False)
        if pend is not None and p.pend_expire and i - pend["i0"] >= p.pend_expire:
            pend = None
        # 3/4. placement
        in_kz = (p.kz_london[0] <= hours[i] < p.kz_london[1]) or (p.kz_overlap_start <= hours[i] < p.kz_ny_end)
        if pos is None and pend is None and bias[i] != 0 and in_kz and day_pnl > -p.daily_loss:
            for j, z in zones.items():
                if z["t"] != bias[i] or z["placed"]:
                    continue
                if z["t"] == 1:
                    entry, sl = z["bot"] + p.buffer * 0.5, z["bot"] - p.buffer
                    if (o[i] + sp) - entry < sp or sl >= entry:
                        continue
                else:
                    entry, sl = z["top"] - p.buffer * 0.5, z["top"] + p.buffer
                    if entry - o[i] < sp or sl <= entry:
                        continue
                sl_dist = abs(entry - sl)
                units = p.fixed_oz if p.sizing == "fixed" else min(equity * p.risk_pct / 100 / sl_dist, p.max_oz)
                units = max(np.floor(units * 100) / 100, 0.01 * 1)
                tp = entry + z["t"] * sl_dist * p.rr
                pend = dict(dir=z["t"], entry=entry, sl=sl, tp=tp, units=units, sl_dist=sl_dist, score=z["score"], i0=i)
                z["placed"] = True
                if trace is not None:
                    trace.append((idx[i], "place", z["t"], round(entry, 2), round(o[i], 2)))
                break
        # 5. pending fill
        if pos is None and pend is not None:
            if pend["dir"] == 1 and l[i] + sp <= pend["entry"]:
                fill = min(pend["entry"], o[i] + sp)
            elif pend["dir"] == -1 and h[i] >= pend["entry"]:
                fill = max(pend["entry"], o[i])
            else:
                fill = None
            if fill is not None:
                pos = dict(pend, fill=fill, time=idx[i])
                pend = None
                if trace is not None:
                    trace.append((idx[i], "fill", pos["dir"], round(fill, 2), round(o[i], 2)))
                res = exit_check(i, fresh=True)
                if res:
                    finish(i, *res)
                else:
                    update_be(i)
        if p.close_eod and hours[i] == 21 and idx[i].minute == 45:
            if pos is not None:
                finish(i, c[i] if pos["dir"] == 1 else c[i] + sp, "eod")
            pend = None
    return pd.DataFrame(trades)
