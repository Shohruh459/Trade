"""Monthly report for strategies A and B on an EUR/USD H1 CSV (default parameters, nothing optimized).

Usage: python -m backtest.monthly data/EURUSD_H1_2023_2023.csv [--out reports/monthly.md]
"""
import argparse

import pandas as pd

from .engine import Config, metrics, run
from .strategies import STRATEGIES


def monthly_table(trades, cfg):
    rows = []
    if trades.empty:
        return pd.DataFrame()
    t = trades.copy()
    t["month"] = t.exit_time.dt.strftime("%Y-%m")
    for m, g in t.groupby("month"):
        rows.append({
            "oy": m, "bitimlar": len(g), "yutuq": int((g.pnl > 0).sum()), "zarar": int((g.pnl <= 0).sum()),
            "foyda_$": round(g.pnl.sum(), 2), "o'rtacha_R": round(g.r.mean(), 2),
            "eng_yaxshi_$": round(g.pnl.max(), 2), "eng_yomon_$": round(g.pnl.min(), 2),
        })
    return pd.DataFrame(rows)


def md(df):
    return df.to_markdown(index=False) if not df.empty else "_bitim yo'q_"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default="reports/monthly.md")
    a = ap.parse_args()
    df = pd.read_csv(a.csv, index_col=0, parse_dates=True)
    cfg = Config()
    lines = [f"# Oylik hisobot: EUR/USD H1\n",
             f"Ma'lumot: {df.index.min()} … {df.index.max()}, {len(df)} ta shamdan. Boshlang'ich balans ${cfg.start_balance:,.0f}, "
             f"risk {cfg.risk_pct:.0%}, spred {cfg.spread_pips} pip, slippage {cfg.slippage_pips} pip/tomon, komissiya ${cfg.commission_per_lot}/lot.\n",
             "Standart parametrlar, hech narsa optimallashtirilmagan. Daromad realizatsiya qilingan bitimlar bo'yicha, oyga bitim yopilgan sanasi bo'yicha.\n"]
    summary = []
    for name, fn in STRATEGIES.items():
        sig, atr = fn(df)
        trades, halted = run(df, sig, atr, cfg)
        m = metrics(trades, cfg.start_balance)
        summary.append({"strategiya": name, **m, "dd_bilan_to'xtagan": halted})
        lines += [f"\n## Strategiya {name}\n", md(monthly_table(trades, cfg)), ""]
        if not trades.empty:
            lines.append(f"Jami: {m['trades']} bitim, yutuq ulushi {m['win_rate']:.0%}, profit factor {m['profit_factor']}, "
                         f"sof natija {m['net_pct']}%, maksimal drawdown {m['max_dd_pct']}%, o'rtacha R {m['avg_r']}.\n")
            trades.to_csv(f"reports/trades_{name}.csv", index=False)
    lines = lines[:3] + ["\n## Umumiy taqqoslash\n", md(pd.DataFrame(summary))] + lines[3:]
    open(a.out, "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
