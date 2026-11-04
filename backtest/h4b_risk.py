"""H4 breakout on a $100 micro account: monthly balance outcomes at different risk per trade, with daily limits
(day stops at -30%, at +100%, or when profit falls back below +50% after reaching it). Descriptive scenario analysis on the frozen model trades.

Usage: python -m backtest.h4b_risk      -> reports/h4b_risk_results.md
"""
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


def month_balance(trades, risk, bal0=100.0, loss_lim=-0.30, target=1.00, keep=0.50):
    """trades: DataFrame with date, t, R for ONE month. Returns end balance and min balance."""
    bal, mn = bal0, bal0
    for d, g in trades.sort_values("t").groupby("date"):
        start, peak, stop = bal, 0.0, False
        for r in g.R.to_numpy():
            if stop:
                break
            bal = bal * (1 + risk * r) if bal > 0 else 0.0
            mn = min(mn, bal)
            pnl = bal / start - 1
            peak = max(peak, pnl)
            if pnl <= loss_lim or pnl >= target or (peak >= keep and pnl < keep):
                stop = True
    return bal, mn


def scenario(tr, risks, a, b):
    months = pd.period_range(a, b, freq="M")
    rows = []
    for risk in risks:
        ends, mins = [], []
        for m in months:
            x = tr[tr.t.dt.to_period("M") == m]
            e, mn = month_balance(x, risk)
            ends.append(e); mins.append(mn)
        ends, mins = np.array(ends), np.array(mins)
        # full compounded path (no monthly reset) for drawdown
        bal, peak, dd = 100.0, 100.0, 0.0
        for d, g in tr.sort_values("t").groupby("date"):
            start, pk, stop = bal, 0.0, False
            for r in g.R.to_numpy():
                if stop: break
                bal *= (1 + risk * r)
                peak = max(peak, bal); dd = max(dd, 1 - bal / peak)
                pnl = bal / start - 1; pk = max(pk, pnl)
                if pnl <= -0.30 or pnl >= 1.0 or (pk >= 0.5 and pnl < 0.5): stop = True
        rows.append(dict(risk_pct=int(round(100 * risk)), oy=len(ends), median=round(float(np.median(ends)), 1), mean=round(float(ends.mean()), 1), p10=round(float(np.percentile(ends, 10)), 1), p90=round(float(np.percentile(ends, 90)), 1),
                         eng_yomon=round(float(ends.min()), 1), eng_yaxshi=round(float(ends.max()), 1), foydali_oy_pct=round(100 * float((ends > 100.0).mean()), 1),
                         oy_ichida_min_50dan_past_pct=round(100 * float((mins < 50).mean()), 1), butun_yol_maxdd_pct=round(100 * dd, 1), butun_yol_final=round(bal, 0)))
    return pd.DataFrame(rows)


def main():
    from backtest.h4 import Data
    from backtest.h4b import chan_arrays, run, sl

    D = Data()
    U, L = chan_arrays(D)
    tr = sl(run(D, U, L), ("2019-01-01", "2025-03-01"))
    risks = [0.01, 0.02, 0.05, 0.10]
    tab = scenario(tr, risks, "2019-01", "2025-02")
    ntr = tr.groupby(tr.t.dt.to_period("M")).size().reindex(pd.period_range("2019-01", "2025-02", freq="M"), fill_value=0)
    out = ["# H4 breakout, $100 micro hisob: bir oylik balans (risk foizlariga ko'ra)\n",
           f"Model savdolari 2019-01 → 2025-02 ({len(tr)} savdo; oyiga o'rtacha {ntr.mean():.1f}, 0 savdoli oylar {int((ntr==0).sum())}/{len(ntr)}). Har oy $100 dan boshlanadi; kunlik qoida: −30% yoki +100% yoki +50% dan keyin pastga tushsa kun yopiladi. Spred $0.30, swap 3%.\n",
           tab.to_markdown(index=False) + "\n"]
    # Sept/Oct 2026 on MetaQuotes data
    import backtest.oos2026 as O
    import backtest.h4 as H4
    import backtest.h4b as H4B
    m1, d1 = O.load_m1(), O.load_d1()
    D2 = H4.Data(m1, d1)
    U2, L2 = H4B.chan_arrays(D2)
    t2 = H4B.run(D2, U2, L2)
    rows = []
    for mo in ("2026-09", "2026-10"):
        x = t2[t2.t.dt.to_period("M") == pd.Period(mo)]
        for risk in risks:
            e, mn = month_balance(x, risk)
            rows.append(dict(oy=mo, risk_pct=int(round(100 * risk)), savdolar=len(x), R_ketma_ket=", ".join(f"{r:+.2f}" for r in x.sort_values("t").R), balans=round(e, 1), oy_ichida_min=round(mn, 1)))
    out.append("## 2026-09 va 2026-10 (MetaQuotes demo ma'lumoti, $100 dan har oy)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
    open("reports/h4b_risk_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
