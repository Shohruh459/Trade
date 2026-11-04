"""Evaluate the demo log written by mt5/H4_Breakout_Daily.mq5 (MQL5/Files/H4BO_log.csv, ';' separated) against STRATEGY_DEMO_H4.md.

Usage: python tools/h4_demo_eval.py path/to/H4BO_log.csv [--balance 100]
Columns: close_time;dir;entry;stop_dist;risk_money;profit;R
"""
import argparse

import numpy as np
import pandas as pd

BACKTEST = dict(mean_R=0.09, win_pct=37.1, pf=1.2, trades_per_year=32)


def load(path):
    d = pd.read_csv(path, sep=";")
    d["close_time"] = pd.to_datetime(d["close_time"])
    return d.sort_values("close_time").reset_index(drop=True)


def evaluate(d, balance=100.0):
    n = len(d)
    if n == 0:
        return dict(n=0)
    eq = balance + d.profit.cumsum().to_numpy()
    pk = np.maximum.accumulate(np.r_[balance, eq])[1:]
    dd = float(((pk - eq) / pk).max())
    wins, losses = d.profit[d.profit > 0].sum(), -d.profit[d.profit < 0].sum()
    months = (d.close_time.iloc[-1] - d.close_time.iloc[0]).days / 30.4 if n > 1 else 0
    return dict(n=n, months=round(months, 1), mean_R=round(float(d.R.mean()), 3), win_pct=round(100 * float((d.profit > 0).mean()), 1), pf=round(float(wins / losses), 2) if losses > 0 else np.nan,
                total=round(float(d.profit.sum()), 2), maxdd_pct=round(100 * dd, 1), worst_R=round(float(d.R.min()), 2))


def verdict(ev, months_running):
    """Pre-registered demo rules (STRATEGY_DEMO_H4.md section 5)."""
    if ev.get("n", 0) == 0:
        return "Savdo yo'q: kutish."
    if ev["maxdd_pct"] > 20:
        return "TO'XTATISH: demo drawdown > 20% (qat'iy chegara)."
    if months_running >= 12:
        if ev["mean_R"] > -0.25:
            return "Davom etish (12 oylik tekshiruv o'tdi: o'rtacha R > -0.25). Statistik xulosa uchun hali kam savdo."
        return "TO'XTATISH: 12 oyda o'rtacha R <= -0.25."
    return "Davom etish (ijro tekshiruvi bosqichi; statistik xulosa yo'q)."


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--balance", type=float, default=100.0)
    a = ap.parse_args()
    d = load(a.log)
    ev = evaluate(d, a.balance)
    print("Demo:", ev)
    print("Backtest taxmini:", BACKTEST)
    print(verdict(ev, ev.get("months", 0)))
