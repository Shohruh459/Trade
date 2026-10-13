"""Run strategies on an EUR/USD H1 CSV and print in-sample / out-of-sample results.

Usage: python -m backtest.run data/EURUSD_H1_2023_2025.csv [--split 2024-07-01]
Default parameters only; nothing is optimized here.
"""
import argparse
import json

import pandas as pd

from .engine import Config, metrics, run
from .strategies import STRATEGIES


def evaluate(df, name, cfg, split):
    sig, atr = STRATEGIES[name](df)
    trades, halted = run(df, sig, atr, cfg)
    out = {"strategy": name, "halted_by_dd": halted, "all": metrics(trades, cfg.start_balance)}
    if split and not trades.empty:
        s = pd.Timestamp(split, tz="UTC")
        for label, part in (("in_sample", trades[trades.entry_time < s]), ("out_of_sample", trades[trades.entry_time >= s])):
            out[label] = metrics(part.reset_index(drop=True).assign(equity=part.pnl.cumsum().to_numpy() + cfg.start_balance), cfg.start_balance)
        out["by_year"] = {
            str(y): metrics(g.reset_index(drop=True).assign(equity=g.pnl.cumsum().to_numpy() + cfg.start_balance), cfg.start_balance)
            for y, g in trades.groupby(trades.entry_time.dt.year)
        }
    return out, trades


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--split", default=None, help="in/out-of-sample split date, e.g. 2023-01-01")
    ap.add_argument("--spread", type=float, default=Config.spread_pips)
    ap.add_argument("--trades-out", default=None)
    a = ap.parse_args()
    df = pd.read_csv(a.csv, index_col=0, parse_dates=True)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    print(f"data: {df.index.min()} .. {df.index.max()}  bars={len(df)}")
    cfg = Config(spread_pips=a.spread)
    for name in STRATEGIES:
        res, trades = evaluate(df, name, cfg, a.split)
        print(json.dumps(res, indent=2))
        if a.trades_out:
            trades.to_csv(f"{a.trades_out}_{name}.csv", index=False)


if __name__ == "__main__":
    main()
