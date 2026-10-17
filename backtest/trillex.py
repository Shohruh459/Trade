"""Tick-level Python port of TRILLEX_10S_BASIC.mq5 (NadirAliOfficial/trillex-10s-ea) on Dukascopy XAUUSD ticks.

Ported (default inputs): M1/M5 closed-bar trend (EMA5>EMA20>EMA40 + PSAR side), 10-second synthetic MID bars built from ticks with the EA's
own EMA/PSAR code, Insane Mode entries (fresh 10s PSAR flip held InpPSARConfirmBars=1 bar + EMA stack + M1/M5 agreement), exits on the
10s PSAR reversal (this runs in BOTH modes in the EA), close on opposite signal, SL 200 points, spread cap 30 points (ticks above the cap
are ignored entirely, as in OnTick), one position, dynamic lot tiers lots = 1 * 10^floor(log10(balance/1000)).
Execution: market orders at the first tick of the next 10s bucket (buy at ask, sell at bid); SL is checked against bid (buy) / ask (sell)
extremes of each 10s bucket. Approximations: PSAR/EMA are computed continuously over the sample instead of on the EA's sliding 800-bar window;
no latency or slippage; SL fills at the SL price.
spread_mode "real" = the data's real Dukascopy bid/ask (EA's 30-pt cap applies); "fixed" = mid +- $0.125 (a $0.25 spread broker).
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class P:
    insane: bool = True
    require_m5: bool = True
    fresh_psar: bool = True
    confirm_bars: int = 1
    exit_mode: str = "psar"       # "psar" or "ema5"
    sl_usd: float = 2.0           # 200 points * 0.01
    max_spread: float = 0.30      # 30 points
    spread_mode: str = "real"     # "real" | "fixed"
    fixed_spread: float = 0.25
    sizing: str = "coded"         # "coded" (lot tiers) | "unit" (1 oz, R-based view only)
    start_balance: float = 10_000.0
    ema_f: int = 5
    ema_m: int = 20
    ema_s: int = 40


def psar(h, l, c, step=0.02, mx=0.2):
    """Exact port of the EA's CalcPSAR."""
    n = len(c)
    sar = [0.0] * n
    if n == 0:
        return np.array(sar)
    if n == 1:
        sar[0] = l[0]
        return np.array(sar)
    up = c[1] >= c[0]
    af = step
    ep = max(h[0], h[1]) if up else min(l[0], l[1])
    sar[0] = l[0] if up else h[0]
    sar[1] = sar[0]
    for i in range(2, n):
        s = sar[i - 1] + af * (ep - sar[i - 1])
        if up:
            s = min(s, l[i - 1], l[i - 2])
            if l[i] < s:
                up, s, ep, af = False, ep, l[i], step
            elif h[i] > ep:
                ep, af = h[i], min(af + step, mx)
        else:
            s = max(s, h[i - 1], h[i - 2])
            if h[i] > s:
                up, s, ep, af = True, ep, h[i], step
            elif l[i] < ep:
                ep, af = l[i], min(af + step, mx)
        sar[i] = s
    return np.array(sar)


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


def bars(sec, price_hi, price_lo, price_cl, price_op, step):
    b = sec // step
    st = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    return st, dict(start=b[st] * step, o=price_op[st], h=np.maximum.reduceat(price_hi, st), l=np.minimum.reduceat(price_lo, st),
                    c=price_cl[np.r_[st[1:] - 1, len(b) - 1]])


def trend_arrays(bd, p: P):
    ef, em, es = ema(bd["c"], p.ema_f), ema(bd["c"], p.ema_m), ema(bd["c"], p.ema_s)
    sar = psar(bd["h"], bd["l"], bd["c"])
    up = (ef > em) & (em > es) & (sar < bd["c"])
    dn = (ef < em) & (em < es) & (sar > bd["c"])
    return np.where(up, 1, np.where(dn, -1, 0))


def run_file(path, p: P):
    d = pd.read_parquet(path)
    ts, ask, bid = d["timestamp"].to_numpy(), d["askPrice"].to_numpy(float), d["bidPrice"].to_numpy(float)
    order = np.argsort(ts, kind="stable")
    ts, ask, bid = ts[order], ask[order], bid[order]
    sec = ts // 1000
    if p.spread_mode == "fixed":
        mid = (ask + bid) / 2
        ask, bid = mid + p.fixed_spread / 2, mid - p.fixed_spread / 2
    # M1 / M5 trend from ALL ticks (bid chart), like the terminal
    trends = {}
    for name, step in (("m1", 60), ("m5", 300)):
        st, bd = bars(sec, bid, bid, bid, bid, step)
        trends[name] = (bd["start"], trend_arrays(bd, p))
    # EA ignores ticks with too wide a spread: no synthetic-bar update, no decisions
    keep = (ask - bid) <= p.max_spread + 1e-9
    sec, ask, bid = sec[keep], ask[keep], bid[keep]
    mid = (ask + bid) / 2
    st, b10 = bars(sec, mid, mid, mid, mid, 10)
    nb = len(st)
    if nb < 100:
        return pd.DataFrame()
    ends = np.r_[st[1:], len(sec)]
    bid_lo = np.minimum.reduceat(bid, st)
    ask_hi = np.maximum.reduceat(ask, st)
    sar = psar(b10["h"], b10["l"], b10["c"])
    c10 = b10["c"]
    ef, em, es = ema(c10, p.ema_f), ema(c10, p.ema_m), ema(c10, p.ema_s)
    bull = (ef > em) & (em > es)
    bear = (ef < em) & (em < es)
    below = sar < c10
    cb = p.confirm_bars
    # fresh PSAR signal at bar i (flip at i-cb, held through i)
    fresh = np.zeros(nb, int)
    for i in range(cb + 1, nb):
        f, pv = i - cb, i - cb - 1
        buy = (not below[pv]) and below[f] and below[f:i + 1].all() and bull[i]
        sell = below[pv] and (not below[f]) and (~below[f:i + 1]).all() and bear[i]
        fresh[i] = 1 if buy else (-1 if sell else 0)
    minbars = max(p.ema_s + 10 + cb, 25 + cb)

    def tf_trend(name, T, step):
        starts, tr = trends[name]
        k = np.searchsorted(starts, (T // step) * step, side="left") - 1
        return tr[k] if k >= 0 else 0

    bal, pos, trades = p.start_balance, None, []

    def close(k, px, T, reason):
        nonlocal bal, pos
        dr = pos["dir"]
        pnl_oz = (px - pos["entry"]) * dr
        mid_x = px + dr * pos["spr"] / 2
        gross_oz = (mid_x - (pos["entry"] - dr * pos["spr"] / 2)) * dr
        units = pos["units"]
        bal += pnl_oz * units
        trades.append(dict(t_entry=pos["T"], t_exit=T, dir=dr, entry=pos["entry"], exit=px, units=units, pnl=pnl_oz * units, r=pnl_oz / p.sl_usd,
                           gross_r=gross_oz / p.sl_usd, reason=reason, hold_s=T - pos["T"], bal=bal))
        pos = None

    for k in range(nb - 1):
        nxt = st[k + 1]                                   # first tick of the next bucket = decision tick
        T, bT, aT = sec[nxt], bid[nxt], ask[nxt]
        if pos is not None:
            hit = (pos["dir"] == 1 and bid_lo[k] <= pos["sl"]) or (pos["dir"] == -1 and ask_hi[k] >= pos["sl"])
            if hit:
                close(k, pos["sl"], T, "sl")
            elif bal <= 0:
                pass
        if bal <= 0:
            break
        if k + 1 < 6:
            continue
        if pos is not None:                                # exits on the new 10s bar
            ex = (sar[k] > c10[k]) if pos["dir"] == 1 else (sar[k] < c10[k])
            if p.exit_mode == "ema5":
                ex = (c10[k] < ef[k]) if pos["dir"] == 1 else (c10[k] > ef[k])
            if ex:
                close(k, bT if pos["dir"] == 1 else aT, T, "psar")
        sig = 0
        if p.insane:
            if k + 1 > minbars:
                m1t = tf_trend("m1", T, 60)
                base = m1t if (m1t != 0 and (not p.require_m5 or tf_trend("m5", T, 300) == m1t)) else 0
                if base != 0 and (fresh[k] == base if p.fresh_psar else ((bull[k] and base == 1) or (bear[k] and base == -1))):
                    sig = base
        else:
            if sec[nxt - 1] // 60 != T // 60 if nxt > 0 else False:
                m1t = tf_trend("m1", T, 60)
                sig = m1t if (m1t != 0 and tf_trend("m5", T, 300) == m1t) else 0
        if sig == 0:
            continue
        if pos is not None:
            if pos["dir"] != sig:
                close(k, bT if pos["dir"] == 1 else aT, T, "opposite")
            continue
        entry = aT if sig == 1 else bT
        tier = int(np.floor(np.log10(bal / 1000.0) + 1e-9)) if bal >= 1000 else 0
        units = 100.0 * 10 ** tier if p.sizing == "coded" else 1.0
        pos = dict(dir=sig, entry=entry, units=units, sl=entry - sig * p.sl_usd, T=T, spr=aT - bT)
    if pos is not None:
        close(nb - 1, bid[-1] if pos["dir"] == 1 else ask[-1], sec[-1], "end")
    return pd.DataFrame(trades)
