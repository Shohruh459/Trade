"""Signal generators. Each returns (signal, atr) arrays aligned with df.

signal[i] is decided from data up to and including bar i (no look-ahead);
the engine executes it at the open of bar i+1.
"""
import numpy as np
import pandas as pd


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    pc = df["close"].shift()
    tr = pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def adx(df, n=14):
    up, dn = df.high.diff(), -df.low.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n)
    pdi = 100 * pd.Series(plus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * pd.Series(minus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def strategy_a(df, fast=20, slow=50, trend=200, adx_min=20, rsi_lo=40, rsi_hi=70, cross_window=3):
    """EMA fast/slow crossover (within last `cross_window` bars) with trend, ADX and RSI filters."""
    c = df["close"]
    f, s, t = ema(c, fast), ema(c, slow), ema(c, trend)
    up = (f > s) & (f.shift() <= s.shift())
    dn = (f < s) & (f.shift() >= s.shift())
    up = up.rolling(cross_window).max().fillna(0).astype(bool) & (f > s)
    dn = dn.rolling(cross_window).max().fillna(0).astype(bool) & (f < s)
    r, ax = rsi(c), adx(df)
    long = up & (c > t) & (ax > adx_min) & (r > rsi_lo) & (r < rsi_hi)
    short = dn & (c < t) & (ax > adx_min) & (r < 100 - rsi_lo) & (r > 100 - rsi_hi)
    sig = np.where(long, 1, np.where(short, -1, 0))
    return sig, atr(df).to_numpy()


def strategy_b(df, channel=20, trend=200):
    """Breakout with confirmation (own implementation of the idea in STRATEGY.md section 2B).

    Bar i-1 closes beyond the prior `channel`-bar high/low (bias). Bar i confirms by
    closing beyond the extreme of the breakout bar (requiring the open too is almost
    never true on H1, where open ~ previous close). Trend filter: EMA(trend).
    """
    c, o = df["close"], df["open"]
    hi = df["high"].rolling(channel).max().shift(2)
    lo = df["low"].rolling(channel).min().shift(2)
    t = ema(c, trend)
    brk_up = c.shift() > hi
    brk_dn = c.shift() < lo
    conf_up = brk_up & (c > df["high"].shift()) & (c > t)
    conf_dn = brk_dn & (c < df["low"].shift()) & (c < t)
    sig = np.where(conf_up, 1, np.where(conf_dn, -1, 0))
    return sig, atr(df).to_numpy()


def strategy_c(df, rsi_lo=30, rsi_hi=70, adx_max=20):
    """RSI mean reversion in range markets (ADX low)."""
    r, ax = rsi(df["close"]), adx(df)
    sig = np.where((r < rsi_lo) & (ax < adx_max), 1, np.where((r > rsi_hi) & (ax < adx_max), -1, 0))
    return sig, atr(df).to_numpy()


def strategy_d(df, n=20, k=2.0, adx_max=25):
    """Bollinger band reversion in range markets."""
    c = df["close"]
    m, sd = c.rolling(n).mean(), c.rolling(n).std()
    ax = adx(df)
    sig = np.where((c < m - k * sd) & (ax < adx_max), 1, np.where((c > m + k * sd) & (ax < adx_max), -1, 0))
    return sig, atr(df).to_numpy()


def strategy_e(df, range_end=7, window_end=11):
    """Asian-range breakout at the London open: first close beyond the 00:00-07:00 UTC range, once per day."""
    day = df.index.normalize()
    hr = df.index.hour
    asia = df[hr < range_end]
    hi = asia.groupby(asia.index.normalize())["high"].max().reindex(day).to_numpy()
    lo = asia.groupby(asia.index.normalize())["low"].min().reindex(day).to_numpy()
    c = df["close"].to_numpy()
    win = (hr >= range_end) & (hr < window_end)
    raw = np.where(win & (c > hi), 1, np.where(win & (c < lo), -1, 0))
    sig = np.zeros(len(df), dtype=int)
    done = None
    for i in range(len(df)):
        if raw[i] != 0 and day[i] != done:
            sig[i] = raw[i]
            done = day[i]
    return sig, atr(df).to_numpy()


def strategy_g(df):
    """Regime switch: trend signal (A) when trending, mean reversion (C) when ranging."""
    sa, a = strategy_a(df)
    sc, _ = strategy_c(df)
    return np.where(sa != 0, sa, sc), a


STRATEGIES = {"A": strategy_a, "B": strategy_b}
EXTRA = {"C": strategy_c, "D": strategy_d, "E": strategy_e, "G": strategy_g}
