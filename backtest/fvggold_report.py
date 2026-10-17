"""Run the FvgGold port on XAUUSD M15 2018-01 .. 2025-02 (data NOT used by the author) and write reports/fvggold.md.

Usage: python -m backtest.fvggold_report
"""
from dataclasses import replace

import numpy as np
import pandas as pd

from .fvggold import P, run

CSV = "data/XAUUSD_M15_2018_2025.csv"


def stats(tr, start=10_000.0):
    if tr.empty:
        return dict(trades=0)
    w, ls = tr.pnl[tr.pnl > 0].sum(), -tr.pnl[tr.pnl <= 0].sum()
    eq1 = np.cumprod(1 + 0.01 * tr.r.to_numpy())               # same trades at 1% risk per trade (scale-free view)
    pk = np.maximum.accumulate(np.r_[1.0, eq1])[1:]
    return dict(trades=len(tr), win_pct=round(100 * (tr.pnl > 0).mean(), 1), PF=round(w / ls, 2) if ls > 0 else np.inf,
                avg_R=round(tr.r.mean(), 3), net_usd=round(tr.pnl.sum(), 1), at_1pct_risk_net_pct=round((eq1[-1] - 1) * 100, 1),
                at_1pct_risk_maxDD_pct=round(((pk - eq1) / pk).max() * 100, 1))


def yearly(tr):
    g = tr.groupby(tr.exit_time.dt.year)
    return pd.DataFrame({y: stats(x) for y, x in g}).T[["trades", "win_pct", "PF", "avg_R", "net_usd", "at_1pct_risk_net_pct"]]


def monthly_summary(tr, a, b):
    m = pd.period_range(a, b, freq="M")
    s = tr.groupby(tr.exit_time.dt.tz_localize(None).dt.to_period("M")).r.sum().reindex(m).fillna(0.0)
    return int((s > 0).sum()), int((s < 0).sum()), int((s == 0).sum()), len(m)


def main():
    df = pd.read_csv(CSV, index_col=0, parse_dates=True)
    df = df[(df.index >= "2018-01-01") & (df.index < "2025-03-01")]
    out = ["# FvgGold (foeed/FvgGold-EA) — mustaqil sinov, XAUUSD M15, 2018-01 → 2025-02\n",
           "Muallif parametrlarini 2026-yil (Yan–Iyul) ma'lumotiga optimallashtirgan; bu davr ma'lumotimizda yo'q. "
           "Biz EA'ning standart sozlamalarini (`FvgGold.set`) o'zgartirmasdan, 2018–2025-fevral davrida sinaymiz: bu muallif ko'rmagan ma'lumot. "
           "Port Python'da bar-darajasida, taxminiy (MT5 tick sinovi emas). Spred $0.25/oz, komissiya $7/100 oz.\n"]
    scen = {
        "S1 EA standarti (CloseAtEOD=false)": dict(),
        "S2 EA'ning CloseAtEOD=true opsiyasi": dict(close_eod=True),
        "S3 S2 + break-even o'chiq": dict(close_eod=True, be_atr=1e9),
        "S4 bizning o'zgartirish: pending 20 baradan keyin bekor": dict(pend_expire=20),
        "S5 S4 + break-even o'chiq": dict(pend_expire=20, be_atr=1e9),
    }
    res = {k: run(df, replace(P(), **kw)) for k, kw in scen.items()}
    out += ["\n## Stsenariylar (pessimistic fill, 0.01 lot)\n", pd.DataFrame({k: stats(v) for k, v in res.items()}).T.to_markdown() + "\n",
            "`at_1pct_risk_*`: shu bitimlar har birida 1% risk bilan bo'lganda (miqyosdan mustaqil). Mezonimiz: PF>1.3, DD<15%, 200+ bitim. "
            "S1 - EA qanday e'lon qilingan bo'lsa shunday. S2-S3 - EA'ning o'z sozlamalari. S4-S5 - bizning o'zgartirishimiz (EA'da yo'q).\n"]
    first = res["S1 EA standarti (CloseAtEOD=false)"]
    last_t = first.exit_time.max()
    out += [f"\nS1: oxirgi bitim {last_t:%Y-%m-%d}. Undan keyingi ~{(pd.Timestamp('2025-03-01', tz='UTC') - last_t).days // 365} yil davomida EA bitta ham bitim ochmadi: "
            "2019-05-31 da qo'yilgan buy-limit (1293.74) narx 1294 dan 2950 ga ko'tarilib qaytmagani uchun hech qachon bajarilmadi, "
            "buyurtma GTC va MaxTrades=1 uni hisoblagani uchun EA to'xtab qoldi (kodda kutilayotgan buyurtmani o'chiradigan joy faqat CloseEOD, u standartda o'chiq).\n"]
    for k in list(res)[1:]:
        tr = res[k]
        if tr.empty:
            continue
        up, dn, fl, tot = monthly_summary(tr, "2018-01", "2025-02")
        out += [f"\n### {k}: yillar bo'yicha\n", yearly(tr).to_markdown() + "\n",
                f"Oylar: {tot} oydan **{up} foydali, {dn} zararli, {fl} bitimsiz** (R bo'yicha). Chiqishlar: {tr.reason.value_counts().to_dict()}\n"]
    # README arithmetic sanity check
    sl, tpv, wr, n = 4.5, 4.5 * 1.5, 0.453, 64
    out += ["\n## README da'vosini arifmetik tekshiruv\n",
            f"Kod bo'yicha SL masofasi = FVGBuffer×1.5 = ${sl}/oz, TP = ×1.5 = ${tpv:.2f}/oz. 0.01 lot = 1 oz. "
            f"README: {n} bitim, yutuq ulushi {wr:.1%}: kutilgan foyda = {n}×({wr}×{tpv:.2f} − {1-wr:.3f}×{sl}) = ${n*(wr*tpv-(1-wr)*sl):.0f}. "
            f"Hatto 64 ta bitimning hammasi yutsa ham = ${n*tpv:.0f} (+{n*tpv/100:.1f}%). README'dagi +$4 874 (+48.7%) ushbu kod va 0.01 lot bilan "
            f"mos kelmaydi (≈{4874/(n*(wr*tpv-(1-wr)*sl)):.0f} baravar katta).\n"]
    open("reports/fvggold.md", "w").write("\n".join(out))
    res["S2 EA'ning CloseAtEOD=true opsiyasi"].to_csv("reports/fvggold_trades_S2.csv", index=False)
    print("\n".join(out))


if __name__ == "__main__":
    main()
