"""GoldStructureEA frozen rules on FX majors (supplementary evidence, STRATEGY_GOLDSTRUCTURE.md v3 section 2: does NOT enter the decision).

EURUSD, GBPUSD, AUDUSD M1 (qleap/dukascopy-ticks-ohlcv, 2020-04 -> 2025-12). Rules and parameters unchanged (ATR-based, scale-free);
only the costs are FX units: spread 1.0 pip = 0.0001 (stress 1.5 pip = 0.00015), no commission, no slippage (plan did not define FX slippage).
Entries from 2020-07-01 (3 months of warm-up, as 2018-01..04 for gold). Single run; refuses to overwrite an existing report.

Usage: python -m backtest.gs_fx   -> reports/goldstructure_fx.md
"""
import glob
import sys
from pathlib import Path

import pandas as pd

from backtest.goldstructure import CFG, Ctx, load_news, run_sim
from backtest.gs_run import metrics, period_table

REPORT = Path("reports/goldstructure_fx.md")
START, END = "2020-07-01", "2026-01-01"


def load_fx(pair):
    fs = sorted(glob.glob(f"/tmp/claude-0/fx_m1/{pair}/*.parquet"))
    d = pd.concat([pd.read_parquet(f) for f in fs])
    d.columns = [c.lower() for c in d.columns]
    d.index = pd.to_datetime(d.index)
    return d[["open", "high", "low", "close"]].sort_index()


def main():
    if REPORT.exists():
        sys.exit(f"{REPORT} already exists: the FX supplementary run is performed ONCE. Aborting.")
    news = load_news()
    out = ["# GoldStructureEA muzlatilgan qoida: FX qo'shimcha dalil (qarorga kirmaydi)\n",
           "EURUSD, GBPUSD, AUDUSD M1 (Dukascopy, 2020-04 → 2025-12), entry 2020-07-01 → 2025-12-31. Qoida va parametrlar oltindagi bilan bir xil; xarajat: spred 1.0 pip (0.0001), stress 1.5 pip; komissiya va slippage yo'q. Bir marta ishga tushirildi.\n"]
    res = {}
    for scen, spread in [("ASOSIY (spred 1.0 pip)", 0.0001), ("STRESS (spred 1.5 pip)", 0.00015)]:
        allt, rows = [], []
        for pair in ("eur_usd", "gbp_usd", "aud_usd"):
            m1 = load_fx(pair)
            ctx = Ctx(m1, dict(CFG, spread=spread, slip_entry=0.0, slip_sl=0.0), news)
            tr, f = run_sim(ctx, START, END)
            tr = tr.assign(pair=pair) if len(tr) else tr
            allt.append(tr)
            rows.append({"juft": pair, **metrics(tr)})
            if scen.startswith("ASOSIY"):
                res[pair] = f
        pooled = pd.concat([t for t in allt if len(t)], ignore_index=True)
        rows.append({"juft": "birlashtirilgan", **metrics(pooled)})
        out.append(f"## {scen}\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
        if scen.startswith("ASOSIY"):
            out.append("### Birlashtirilgan, davrlar bo'yicha\n" + pd.DataFrame([{"davr": n, **metrics(pooled[(pooled.entry >= a) & (pooled.entry < b)])} for n, (a, b) in
                       {"2020-07..2022-12": ("2020-07-01", "2023-01-01"), "2023-01..2025-12": ("2023-01-01", "2026-01-01")}.items()]).to_markdown(index=False) + "\n")
            yr = pooled.groupby(pooled.entry.dt.year).R.agg(["count", "mean"]).round(3)
            out.append("### Yillar bo'yicha (birlashtirilgan)\n" + yr.to_markdown() + "\n")
            pooled.to_csv("reports/goldstructure_fx_trades.csv", index=False)
    out.append("### Voronka (asosiy ssenariy)\n" + pd.DataFrame(res).to_markdown() + "\n")
    REPORT.write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
