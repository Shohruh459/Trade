"""Run the Classic-MR and Trend-Breakout ports on XAUUSD M1 2018-01..2025-02; write reports/n30_variants.md.  Usage: python -m backtest.n30_variants_report"""
from dataclasses import replace

import numpy as np
import pandas as pd

from .fvggold_report import monthly_summary, yearly
from .n30_variants import MR, TB, prepare, sim

PARQ = "/tmp/claude-0/gold1m/XAU_M1_2018_2025.parquet"


def summ(tr):
    if tr.empty:
        return dict(trades=0)
    r = tr.r.to_numpy()
    w, ls = r[r > 0].sum(), -r[r <= 0].sum()
    e = 1.96 * r.std(ddof=1) / np.sqrt(len(r)) if len(r) > 2 else float("nan")
    eq1 = np.cumprod(1 + 0.01 * r)
    pk = np.maximum.accumulate(np.r_[1.0, eq1])[1:]
    return dict(trades=len(tr), win_pct=round(100 * (r > 0).mean(), 1), PF=round(w / ls, 2) if ls > 0 else float("inf"), avg_R=round(r.mean(), 3),
                avgR_CI=f"{r.mean() - e:+.3f}…{r.mean() + e:+.3f}", at_1pct_net_pct=round((eq1[-1] - 1) * 100, 1), at_1pct_maxDD_pct=round(((pk - eq1) / pk).max() * 100, 1))


def main():
    df = pd.read_parquet(PARQ)
    df = df[(df.index >= "2018-01-01") & (df.index < "2025-03-01")]
    d = prepare(df)
    out = ["# gold-pro-scalper: klassik MR va Trend Breakout — mustaqil sinov, XAUUSD M1, 2018-01 → 2025-02\n",
           "Parametrlar EA standarti, o'zgartirilmagan. M1 bar-darajasidagi port (tick-darajali mantiqning bir qismi taxminiy: 3-tick tasdiq, tezlik bloki, jonli "
           "indikatorlar). Yangiliklar filtri yo'q (ma'lumot yo'q). R = foyda / SL masofasi. Mezon: PF>1.3, DD<15%, 200+ bitim.\n"]
    scen = {"Klassik MR, spred $0.25": ("mr", MR()), "Klassik MR, spred $0.15": ("mr", MR(spread=0.15)), "Klassik MR, spred $0.40": ("mr", MR(spread=0.40)),
            "Trend Breakout, spred $0.25": ("tb", TB()), "Trend Breakout, spred $0.15": ("tb", TB(spread=0.15)), "Trend Breakout, spred $0.40": ("tb", TB(spread=0.40))}
    res, gates = {}, {}
    for k, (kind, p) in scen.items():
        tr, g = sim(d, p, kind)
        res[k] = tr
        gates[k] = g
    out += ["\n## Umumiy\n", pd.DataFrame({k: summ(v) for k, v in res.items()}).T.to_markdown() + "\n"]
    for k in ("Klassik MR, spred $0.25", "Klassik MR, spred $0.15", "Klassik MR, spred $0.40"):
        out.append(f"- {k}: ATR-nisbiy spred cheklovi (spred ≤ M1 ATR × 12%) savdo oynasi vaqtining **{gates[k]*100:.1f}%** da o'tadi.\n")
    for k, tr in res.items():
        if tr.empty or len(tr) < 5:
            continue
        up, dn, fl, tot = monthly_summary(tr.assign(r=tr.r), "2018-01", "2025-02")
        t2 = tr.assign(pnl=tr.pnl)
        out += [f"\n### {k}\n", yearly(t2).to_markdown() + "\n",
                f"Oylar: {tot} oydan **{up} foydali, {dn} zararli, {fl} bitimsiz**. Chiqishlar: {tr.reason.value_counts().to_dict()}. O'rtacha ushlab turish: {tr.bars.mean():.0f} min.\n"]
    open("reports/n30_variants.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
