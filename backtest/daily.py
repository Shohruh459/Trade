"""Daily-limit layer (-3 losses / +$10 / keep >= +$5) on the M15 entry rule (STRATEGY_DAILY.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.daily      -> reports/daily_results.md
"""
import numpy as np
import pandas as pd

from backtest.ldn import load
from backtest.m15 import DEC, Data, run, sl

BAL0 = 100.0
HALF = {"2019-21": ("2019-01-01", "2022-01-01"), "2022-25": ("2022-01-01", "2025-03-01")}


def layer(R, max_loss=3, target=10.0, keep=5.0):
    """R: array of trade results ($) of ONE day in time order. Returns taken trades' results."""
    out, pnl, losses, peak = [], 0.0, 0, 0.0
    for r in R:
        out.append(r); pnl += r; peak = max(peak, pnl)
        if r < 0: losses += 1
        if losses >= max_loss or pnl >= target or (peak >= keep and pnl < keep):
            break
    return out


def apply(tr, on=True, **kw):
    rows = []
    for d, g in tr.sort_values("t").groupby("date"):
        taken = layer(g.R.to_numpy(), **kw) if on else list(g.R.to_numpy())
        for k, r in enumerate(taken):
            rows.append((d, g.t.iloc[k], r))
    return pd.DataFrame(rows, columns=["date", "t", "R"])


def metrics(x, bal0=BAL0):
    if len(x) == 0:
        return {}
    x = x.sort_values("t")
    eq = bal0 + x.R.cumsum().to_numpy()
    pk = np.maximum.accumulate(np.r_[bal0, eq])[1:]
    dd = float(((pk - eq) / pk).max())
    day = x.groupby("date").R.sum()
    mo = x.groupby(x.t.dt.to_period("M")).R.sum()
    allm = pd.period_range(mo.index.min(), mo.index.max(), freq="M")
    mo = mo.reindex(allm, fill_value=0.0)
    streak = cur = 0
    for v in mo:
        cur = cur + 1 if v < 0 else 0
        streak = max(streak, cur)
    return dict(N=len(x), meanR=round(float(x.R.mean()), 4), total_usd=round(float(x.R.sum()), 1), final=round(float(eq[-1]), 1), maxdd_pct=round(100 * dd, 1),
                win_days_pct=round(100 * float((day > 0).mean()), 1), days_traded=len(day), hit_10=int((day >= 10).sum()), hit_m3=int((day <= -3 + 1e-9).sum()),
                pos_months_pct=round(100 * float((mo > 0).mean()), 1), worst_month=round(float(mo.min()), 1), best_month=round(float(mo.max()), 1), max_loss_streak_m=streak)


def main():
    G = Data(load(), 0.30, 0.50)
    base = sl(run(G, maxtr=20, losscd=99), DEC)
    stress = sl(run(G, stress=True, maxtr=20, losscd=99), DEC)
    L = apply(base)
    L0 = apply(base, on=False)
    Ls = apply(stress)
    rows = [{"variant": "qatlamsiz (baza)", **metrics(L0)}, {"variant": "kunlik qatlam bilan", **metrics(L)}, {"variant": "qatlam + stress $0.50", **metrics(Ls)}]
    for k, v in HALF.items():
        x = L[(L.date >= pd.Timestamp(v[0])) & (L.date < pd.Timestamp(v[1]))]
        rows.append({"variant": f"qatlam, {k}", **metrics(x)})
    out = ["# Kunlik qatlam (−3 zarar / +10$ / +5$ saqlash) + M15 kirish: natijalar (STRATEGY_DAILY.md)\n", "$1 = 1R, balans $100, 2019-01 → 2025-02, spred $0.30\n", pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    # shuffle control: random order inside each day
    rng = np.random.default_rng(1)
    groups = [g.R.to_numpy() for _, g in base.sort_values("t").groupby("date")]
    real = L.R.sum()
    tot = np.empty(1000)
    for i in range(1000):
        s = 0.0
        for g in groups:
            s += sum(layer(rng.permutation(g)))
        tot[i] = s
    out.append(f"## Tartib nazorati (kun ichida savdolar tasodifiy aralashtirilgan, 1000): real jami ${real:.1f}; aralashtirilgan o'rtacha ${tot.mean():.1f} (5–95%: {np.percentile(tot,5):.1f} … {np.percentile(tot,95):.1f}); p = {float((tot >= real).mean()):.3f}\n")
    # 12-month windows
    wr = []
    for sd in pd.date_range("2019-01-01", "2024-02-28", freq="QS"):
        ed = sd + pd.DateOffset(months=12)
        x = L[(L.date >= sd) & (L.date < ed)]
        if len(x): wr.append(float(x.R.sum()))
    wr = np.array(wr)
    out.append(f"## 12 oylik oynalar (har chorak boshi): {len(wr)} ta; foydali {100*float((wr>0).mean()):.0f}%; eng yomon ${wr.min():.1f}; median ${np.median(wr):.1f}; eng yaxshi ${wr.max():.1f}\n")
    yr = L.groupby(L.t.dt.year).R.agg(["count", "sum"]).round(1)
    out.append("## Yillar bo'yicha (qatlam bilan, $)\n" + yr.to_markdown() + "\n")
    m, ms = metrics(L), metrics(Ls)
    h1 = metrics(L[(L.date >= "2019-01-01") & (L.date < "2022-01-01")])
    h2 = metrics(L[(L.date >= "2022-01-01") & (L.date < "2025-03-01")])
    crit = {"D1 foyda>0 (butun va ikki yarim)": m["total_usd"] > 0 and h1["total_usd"] > 0 and h2["total_usd"] > 0,
            "D2 maxDD<=30%": m["maxdd_pct"] <= 30,
            "D3 foydali oylar>=60% va eng yomon oy>=-$10": m["pos_months_pct"] >= 60 and m["worst_month"] >= -10,
            "D4 stress foyda>0": ms["total_usd"] > 0,
            "D5 12 oylik oynalar>=70% foydali": float((wr > 0).mean()) >= 0.7}
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    open("reports/daily_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
