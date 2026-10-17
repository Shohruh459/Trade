"""N1: multi-asset monthly SMA10 trend portfolio (STRATEGY_NEXT.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.n1      -> reports/n1_results.md
"""
import numpy as np
import pandas as pd

from backtest.portfolio import D, END, E1, E2, FULL, load, metrics, returns, sharpe, sl

COST = 0.0010


def load_assets():
    d = load()
    idx = d["idx"]
    R = returns(d)
    out = {"equity": R["equity"], "bond": R["bond"], "gold": R["gold"]}
    w = pd.read_csv(f"{D}/oil-prices/data/wti-monthly.csv", parse_dates=["Date"])
    w.index = w.Date.dt.to_period("M")
    out["oil"] = w.Price.reindex(idx).astype(float).pct_change()
    g = pd.read_csv(f"{D}/natural-gas/data/monthly.csv")
    g.index = pd.PeriodIndex(g.Month, freq="M")
    out["natgas"] = g.Price.reindex(idx).astype(float).pct_change()
    return pd.DataFrame(out)


def signals(R):
    """1 if index_t > SMA10(index) at month end t (known at t, applies to t+1 return)."""
    sig = {}
    for c in R:
        r = R[c]
        lvl = (1 + r.fillna(0)).cumprod().where(r.notna())
        sig[c] = (lvl > lvl.rolling(10).mean()).astype(float).where(lvl.rolling(10).count() == 10)
    return pd.DataFrame(sig)


def weights(sig_hold, avail):
    n = avail.sum(axis=1)
    return sig_hold.fillna(0).where(avail, 0).div(n, axis=0)


def pnl(R, W, cost=COST):
    r = R.fillna(0)
    gross = (W * r).sum(axis=1)
    turn = W.diff().abs().sum(axis=1)
    turn.iloc[0] = W.iloc[0].abs().sum()
    return gross - cost * turn


def run_variant(R, sig, lag):
    hold = sig.shift(1 + lag)  # signal at t-1-lag applies to return t
    avail = R.notna() & hold.notna()
    return pnl(R, weights(hold, avail)), avail


def stats_row(r):
    r = pd.Series(np.asarray(r, float))
    n = len(r)
    m = metrics(r.to_numpy())
    m["pos_months_pct"] = round(100 * (r > 0).mean(), 1)
    m["worst_month_pct"] = round(100 * r.min(), 1)
    m["pos_3m_pct"] = round(100 * (r.add(1).rolling(3).apply(np.prod, raw=True) > 1)[2:].mean(), 1)
    m["n"] = n
    return m


def timing_p(R, sig, avail, actual_sharpe, draws=5000, seed=7):
    rng = np.random.default_rng(seed)
    base = sig.shift(1)
    cols = list(R.columns)
    Rv = R.fillna(0).to_numpy()
    av = avail.to_numpy()
    n = av.sum(axis=1).astype(float)
    idx = np.where(avail.index >= pd.Period(FULL[0], "M"))[0]
    sv = base.fillna(0).to_numpy()
    out = np.empty(draws)
    for i in range(draws):
        S = np.column_stack([np.roll(sv[:, j], rng.integers(1, len(sv))) for j in range(len(cols))])
        W = np.where(av, S, 0) / np.maximum(n, 1)[:, None]
        g = (W * Rv).sum(axis=1)
        t = np.abs(np.diff(W, axis=0, prepend=0)).sum(axis=1)
        out[i] = sharpe((g - COST * t)[idx])
    return float((out >= actual_sharpe).mean())


def main():
    R = load_assets()
    sig = signals(R)
    s0, av0 = run_variant(R, sig, 0)
    s1, _ = run_variant(R, sig, 1)
    hold0 = sig.shift(1)
    b1 = pnl(R, weights(pd.DataFrame(1.0, index=R.index, columns=R.columns), R.notna() & hold0.notna()))
    eq_bd = pd.DataFrame({c: R[c] for c in ["equity", "bond"]}).fillna(0)
    b2 = pnl(R[["equity", "bond"]], pd.DataFrame({"equity": 0.6, "bond": 0.4}, index=R.index))
    series = {"N1 SMA10": s0, "N1 lag-1": s1, "B1 EW buy&hold": b1, "B2 60/40": b2}
    rows, res = [], {}
    for nm, s in series.items():
        for era, nme in [(FULL, "full"), (E1, "E1"), (E2, "E2")]:
            x = sl(s, era).dropna()
            m = stats_row(x.to_numpy())
            res[(nm, nme)] = m
            rows.append({"series": nm, "era": nme, **m})
    tab = pd.DataFrame(rows)
    ps = timing_p(R, sig, av0, res[("N1 SMA10", "full")]["Sharpe"])
    g = lambda nm, e, k: res[(nm, e)][k]
    crit = {
        "a Sharpe>=0.50 (full)": g("N1 SMA10", "full", "Sharpe") >= 0.5,
        "b maxDD<=20% full, <=25% eras": g("N1 SMA10", "full", "maxDD_pct") <= 20 and all(g("N1 SMA10", e, "maxDD_pct") <= 25 for e in ["E1", "E2"]),
        "c eras CAGR>0 & Sharpe>=0.30": all(g("N1 SMA10", e, "CAGR_pct") > 0 and g("N1 SMA10", e, "Sharpe") >= 0.3 for e in ["E1", "E2"]),
        "d DD<=0.6*B1 DD & Sharpe>=B1-0.05 (full)": g("N1 SMA10", "full", "maxDD_pct") <= 0.6 * g("B1 EW buy&hold", "full", "maxDD_pct") and g("N1 SMA10", "full", "Sharpe") >= g("B1 EW buy&hold", "full", "Sharpe") - 0.05,
        "e timing p<=0.10": ps <= 0.10,
        "f lag-1 Sharpe>=0.40 & DD<=25%": g("N1 lag-1", "full", "Sharpe") >= 0.4 and g("N1 lag-1", "full", "maxDD_pct") <= 25,
    }
    verdict = "PASS" if all(crit.values()) else "FAIL"
    yrs = pd.Series(s0).groupby(s0.index.year).apply(lambda x: (1 + x).prod() - 1)
    npos = int((yrs.loc[1976:2025] > 0).sum())
    with open("reports/n1_results.md", "w") as f:
        f.write("# N1: ko'p aktivli SMA10 portfel (STRATEGY_NEXT.md)\n\n")
        f.write(f"Aktivlar: aksiya, obligatsiya, oltin, WTI (1986+), tabiiy gaz (1997+). Davr {FULL[0]} → {END}. Xarajat 10 b.p.\n\n")
        f.write(tab.to_markdown(index=False) + "\n\n")
        f.write(f"Timing (aylana siljitish, 5000): p = {ps:.3f}\n\n## Mezonlar\n")
        for k, v in crit.items():
            f.write(f"- {k}: {'OK' if v else 'YO`Q'}\n")
        f.write(f"\n**Xulosa: {verdict}**\n\nYillik foydali yillar (1976–2025, N1): {npos}/50\n")
    print(tab.to_string()); print("timing p", ps); print(crit); print(verdict, npos)


if __name__ == "__main__":
    main()
