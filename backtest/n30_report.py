"""Run the TickRobust port on XAUUSD M1 2018-01 .. 2025-02 and write reports/n30_tickrobust.md.  Usage: python -m backtest.n30_report"""
from dataclasses import replace

import numpy as np
import pandas as pd

from .fvggold_report import monthly_summary, stats, yearly
from .n30_tickrobust import P, run

PARQ = "/tmp/claude-0/gold1m/XAU_M1_2018_2025.parquet"


def ci(tr):
    if len(tr) < 3:
        return "n/a"
    m, s = tr.r.mean(), tr.r.std(ddof=1)
    e = 1.96 * s / np.sqrt(len(tr))
    return f"{m:+.3f} R (95% CI {m - e:+.3f} … {m + e:+.3f})"


def main():
    df = pd.read_parquet(PARQ)
    df = df[(df.index >= "2018-01-01") & (df.index < "2025-03-01")]
    out = ["# N30 Gold Reversion TickRobust (n30dyn4m1c/gold-pro-scalper) — mustaqil sinov, XAUUSD M1, 2018-01 → 2025-02\n",
           "Qoidalar EA'ning standart `Inp*` qiymatlari bilan, parametrlar o'zgartirilmagan. Bar-darajasidagi port: EA qarorni faqat yangi bar ochilishida, "
           "yopilgan bar ma'lumotlari bilan qabul qiladi, shuning uchun port EA mantiqiga yaqin. Ko'chirilmagan: MQL5 yangiliklar kalendari filtri (ma'lumot yo'q). "
           "Spred doimiy (ma'lumotda yo'q). Broker vaqti = Yevropa/Afina (ma'lumot manbai serveri vaqti). Boshlang'ich balans $10 000.\n"]
    scen = {
        "T1 standart (spred $0.25, dinamik risk)": dict(),
        "T2 spred $0.15": dict(spread=0.15),
        "T3 spred $0.40": dict(spread=0.40),
        "T4 doimiy 2% risk (InpUseDynamicRisk=false)": dict(dynamic_risk=False),
        "T5 spred $0.25 + komissiya $7/lot": dict(commission_per_oz=0.07),
    }
    res = {k: run(df, replace(P(), **kw)) for k, kw in scen.items()}
    tab = pd.DataFrame({k: stats(v) for k, v in res.items()}).T
    tab["avg_R (95% CI)"] = [ci(v) for v in res.values()]
    out += ["\n## Stsenariylar\n", tab.to_markdown() + "\n",
            "`at_1pct_risk_*`: shu bitimlar har birida 1% risk bilan bo'lganda. Mezonimiz: PF>1.3, DD<15%, 200+ bitim.\n"]
    for k, tr in res.items():
        if tr.empty:
            continue
        up, dn, fl, tot = monthly_summary(tr, "2018-01", "2025-02")
        out += [f"\n### {k}\n", yearly(tr).to_markdown() + "\n",
                f"Oylar: {tot} oydan **{up} foydali, {dn} zararli, {fl} bitimsiz** (R bo'yicha). Chiqishlar: {tr.reason.value_counts().to_dict()}. "
                f"Yo'nalish: buy {int((tr.dir == 1).sum())}, sell {int((tr.dir == -1).sum())}. O'rtacha ushlab turish: {tr.bars.mean():.1f} bar (M1).\n"]
        if k.startswith("T1"):
            tr.to_csv("reports/n30_trades_T1.csv", index=False)
    open("reports/n30_tickrobust.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
