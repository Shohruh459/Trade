"""Exploration on a short sample: many strategy/exit variants, monthly profit table.

WARNING: every variant tried on the same few months raises the chance that the best one is just
lucky. Variants are chosen on the exploration months and only then looked at on the holdout months.
Usage: python -m backtest.explore data/EURUSD_H1_2023_2023.csv [--holdout-from 2023-05-01]
"""
import argparse
from dataclasses import replace

import pandas as pd

from .engine import Config, metrics, run
from .strategies import EXTRA, STRATEGIES

ALL = {**STRATEGIES, **EXTRA}
EXITS = {
    "fix 1:2": dict(rr=2.0),
    "fix 1:1": dict(rr=1.0),
    "BE+1:2": dict(rr=2.0, be_r=1.0),
    "trail": dict(rr=None, trail_atr=1.5, trail_start_r=1.0),
    "BE+trail": dict(rr=None, be_r=1.0, trail_atr=2.0, trail_start_r=1.5),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--holdout-from", default="2023-05-01")
    ap.add_argument("--out", default="reports/explore_2023H1.md")
    a = ap.parse_args()
    df = pd.read_csv(a.csv, index_col=0, parse_dates=True)
    base = Config()
    hold = pd.Timestamp(a.holdout_from, tz="UTC")
    rows, trade_logs = [], {}
    for sname, fn in ALL.items():
        sig, atr = fn(df)
        for ename, over in EXITS.items():
            cfg = replace(base, **over)
            tr, halted = run(df, sig, atr, cfg)
            name = f"{sname} {ename}"
            if tr.empty:
                rows.append({"variant": name, "trades": 0}); continue
            tr["m"] = tr.exit_time.dt.strftime("%m")
            mon = tr.groupby("m").pnl.sum()
            row = {"variant": name, "trades": len(tr), "win%": round((tr.pnl > 0).mean() * 100),
                   "PF": metrics(tr, cfg.start_balance)["profit_factor"],
                   "explore_$": round(tr[tr.exit_time < hold].pnl.sum()), "holdout_$": round(tr[tr.exit_time >= hold].pnl.sum()),
                   "total_$": round(tr.pnl.sum()), "maxDD%": metrics(tr, cfg.start_balance)["max_dd_pct"],
                   "DD-stop": "ha" if halted else ""}
            for m in ["01", "02", "03", "04", "05", "06", "07"]:
                row[m] = round(mon.get(m, 0))
            row["+oylar"] = int(sum(mon.get(m, 0) > 0 for m in ["01", "02", "03", "04", "05", "06", "07"]))
            rows.append(row)
    res = pd.DataFrame(rows).sort_values("total_$", ascending=False)
    out = [f"# Tajriba: {len(res)} ta variant, bitta {df.index.min():%Y-%m-%d}…{df.index.max():%Y-%m-%d} namunada\n",
           "Oylik ustunlar: 01…07 = oy bo'yicha foyda ($). `+oylar` = foydali oylar soni (7 tadan). "
           f"explore = {df.index.min():%b}–{hold - pd.Timedelta(days=1):%b}, holdout = {hold:%b}dan keyin.\n",
           res.to_markdown(index=False)]
    open(a.out, "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
