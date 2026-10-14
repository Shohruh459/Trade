"""Bar-based single-position backtest engine for EUR/USD (bid candles).

Conventions (kept deliberately conservative):
- Signals are computed on a closed bar i-1 and executed at the open of bar i.
- Candles are BID. Longs enter at ask (= bid + spread) and exit at bid;
  shorts enter at bid and exit at ask.
- If SL and TP are both reachable inside one bar, SL is assumed to hit first.
- If a bar opens beyond the SL, the exit is at the open (gap), not at the SL.
- Equity is realized-only (updated on trade close).
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

PIP = 0.0001


@dataclass
class Config:
    start_balance: float = 10_000.0
    risk_pct: float = 0.01            # risk per trade
    spread_pips: float = 0.8          # constant spread
    commission_per_lot: float = 7.0   # USD per 100k units, round turn
    slippage_pips: float = 0.2        # per side, applied against us
    sl_atr: float = 1.5
    rr: Optional[float] = 2.0         # take-profit in R; None = no fixed TP
    be_r: Optional[float] = None      # move SL to entry after +be_r R
    trail_atr: Optional[float] = None  # trailing distance in ATRs (of entry bar)
    trail_start_r: float = 1.0        # start trailing after +R
    session_start: int = 7            # UTC hour, inclusive
    session_end: int = 20             # UTC hour, exclusive
    friday_no_entry_hour: int = 18
    friday_close_hour: int = 21
    max_spread_pips: float = 2.0
    daily_loss_limit: float = 0.03
    max_drawdown: float = 0.15
    max_leverage: float = 30.0


def run(df: pd.DataFrame, signal: np.ndarray, atr: np.ndarray, cfg: Config = Config()):
    """df: columns open/high/low/close with UTC DatetimeIndex.
    signal[i] in {-1,0,1} is known at the close of bar i; atr[i] likewise."""
    o, h, l = df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy()
    c = df["close"].to_numpy()
    idx = df.index
    hours, wdays, days = idx.hour.to_numpy(), idx.dayofweek.to_numpy(), idx.normalize().to_numpy()
    s = cfg.spread_pips * PIP
    slip = cfg.slippage_pips * PIP

    equity = cfg.start_balance
    peak = equity
    halted = False
    day_key, day_start_eq = None, equity
    pos = None
    trades = []

    def close_trade(i, price, reason):
        nonlocal equity, peak, pos
        d = pos["dir"]
        gross = (price - pos["entry"]) * d * pos["units"]
        comm = cfg.commission_per_lot * pos["units"] / 100_000
        pnl = gross - comm
        equity += pnl
        peak = max(peak, equity)
        trades.append({
            "entry_time": pos["time"], "exit_time": idx[i], "dir": d,
            "entry": pos["entry"], "exit": price, "units": pos["units"],
            "pnl": pnl, "r": pnl / pos["risk"], "reason": reason, "equity": equity,
        })
        pos = None

    def update_stops(i):
        """Tighten the stop using bar i's favourable extreme; takes effect from bar i+1."""
        d, e, a0, sl_dist = pos["dir"], pos["entry"], pos["atr0"], pos["sl_dist"]
        fav = h[i] if d == 1 else l[i] + s            # best price reached (bid high / ask low)
        gain = (fav - e) * d
        new_sl = pos["sl"]
        if cfg.be_r is not None and gain >= cfg.be_r * sl_dist:
            new_sl = max(new_sl, e) if d == 1 else min(new_sl, e)
        if cfg.trail_atr is not None and gain >= cfg.trail_start_r * sl_dist:
            cand = fav - cfg.trail_atr * a0 if d == 1 else fav + cfg.trail_atr * a0
            new_sl = max(new_sl, cand) if d == 1 else min(new_sl, cand)
        pos["sl"] = new_sl

    def check_exit(i):
        d, sl, tp = pos["dir"], pos["sl"], pos["tp"]
        if d == 1:  # exit on bid
            if o[i] <= sl:
                return o[i] - slip, "sl_gap"
            if l[i] <= sl:
                return sl - slip, "sl"
            if h[i] >= tp:
                return tp, "tp"
        else:       # exit on ask
            if o[i] + s >= sl:
                return o[i] + s + slip, "sl_gap"
            if h[i] + s >= sl:
                return sl + slip, "sl"
            if l[i] + s <= tp:
                return tp, "tp"
        return None

    for i in range(1, len(df)):
        if days[i] != day_key:
            day_key, day_start_eq = days[i], equity

        if pos is not None:
            res = check_exit(i)
            if res:
                close_trade(i, *res)
            elif wdays[i] == 4 and hours[i] >= cfg.friday_close_hour:
                px = o[i] - slip if pos["dir"] == 1 else o[i] + s + slip
                close_trade(i, px, "friday_close")
            else:
                update_stops(i)

        if equity <= peak * (1 - cfg.max_drawdown):
            halted = True

        if pos is None and not halted:
            sig, a = signal[i - 1], atr[i - 1]
            ok = (
                sig != 0 and np.isfinite(a) and a > 0
                and cfg.session_start <= hours[i] < cfg.session_end
                and not (wdays[i] == 4 and hours[i] >= cfg.friday_no_entry_hour)
                and wdays[i] < 5
                and cfg.spread_pips <= cfg.max_spread_pips
                and (equity - day_start_eq) > -cfg.daily_loss_limit * day_start_eq
            )
            if ok:
                sl_dist = cfg.sl_atr * a
                entry = o[i] + s + slip if sig == 1 else o[i] - slip
                risk_amt = equity * cfg.risk_pct
                units = min(risk_amt / sl_dist, equity * cfg.max_leverage / entry)
                if units >= 1000:
                    pos = {
                        "dir": int(sig), "entry": entry, "units": units, "time": idx[i],
                        "sl": entry - sig * sl_dist,
                        "tp": entry + sig * sl_dist * cfg.rr if cfg.rr is not None else sig * np.inf,
                        "risk": units * sl_dist, "atr0": a, "sl_dist": sl_dist,
                    }
                    res = check_exit(i)
                    if res:
                        close_trade(i, *res)
                    else:
                        update_stops(i)

    if pos is not None:  # mark-to-market at the last close
        close_trade(len(df) - 1, c[-1] - slip if pos["dir"] == 1 else c[-1] + s + slip, "end")
    return pd.DataFrame(trades), halted


def metrics(trades: pd.DataFrame, start_balance: float) -> dict:
    if trades.empty:
        return {"trades": 0}
    eq = np.concatenate([[start_balance], trades["equity"].to_numpy()])
    dd = (np.maximum.accumulate(eq) - eq) / np.maximum.accumulate(eq)
    wins, losses = trades.loc[trades.pnl > 0, "pnl"].sum(), -trades.loc[trades.pnl <= 0, "pnl"].sum()
    return {
        "trades": len(trades),
        "win_rate": round(float((trades.pnl > 0).mean()), 3),
        "profit_factor": round(float(wins / losses), 2) if losses > 0 else float("inf"),
        "net_pct": round(float(eq[-1] / start_balance - 1) * 100, 1),
        "max_dd_pct": round(float(dd.max()) * 100, 1),
        "avg_r": round(float(trades.r.mean()), 3),
    }
