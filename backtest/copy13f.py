"""Berkshire 13F copy backtest (STRATEGY_13F_COPY.md, pre-registered). Nothing is tuned.

Data (not committed, downloaded from Hugging Face): /tmp/claude-0/n13/holdings.csv  (eagle0504/sec-13f-holdings)
Usage: python -m backtest.copy13f      -> reports/copy13f_results.md
"""
import numpy as np
import pandas as pd

HOLD = "/tmp/claude-0/n13/holdings.csv"
SP = "/home/user/datasets/s-and-p-500/data/data.csv"
COST, STRESS = 0.0010, 0.0025


def load_raw():
    h = pd.read_csv(HOLD, low_memory=False)
    h = h[(h.share_type == "SH") & h.put_call.isna() & (h.shares > 0) & (h.value_usd > 0)].copy()
    h["period"] = pd.to_datetime(h.period)
    h["filed"] = pd.to_datetime(h.filed)
    h["px"] = h.value_usd / h.shares
    return h


def load():
    h = pd.read_csv(HOLD, low_memory=False)
    h = h[(h.share_type == "SH") & h.put_call.isna() & (h.shares > 0) & (h.value_usd > 0)].copy()
    h["period"] = pd.to_datetime(h.period)
    h["filed"] = pd.to_datetime(h.filed)
    h["px"] = h.value_usd / h.shares
    px = h.groupby(["cusip", "period"]).px.median()
    b = h[h.fund_slug.str.contains("berkshire")]
    return px, b


def sp_level():
    s = pd.read_csv(SP, parse_dates=["Date"])
    s = s.set_index(s.Date + pd.Timedelta(days=14)).SP500.astype(float)
    return s


def interp_sp(s, d):
    return float(np.interp(pd.Timestamp(d).value, s.index.values.astype("datetime64[ns]").astype("int64"), s.values))


def portfolios(b, topn):
    out = {}
    for per, g in b.groupby("period"):
        g = g.groupby("cusip").agg(v=("value_usd", "sum"), filed=("filed", "max"))
        g = g.sort_values("v", ascending=False)
        if topn:
            g = g.head(topn)
        w = g.v / g.v.sum()
        out[per] = (w, g.filed.max())
    return out


def growth_table(h, per, adjust=True):
    """Gross price growth per (cusip, interval k: per[k] -> per[k+1]) from 13F implied prices, split-adjusted via median share-count ratio across funds."""
    px = h.groupby(["cusip", "period"]).px.median().unstack("period")
    sh = h.groupby(["fund_slug", "cusip", "period"]).shares.sum().unstack("period")
    G = {}
    for k in range(len(per) - 1):
        p0, p1 = px.get(per[k]), px.get(per[k + 1])
        g = (p1 / p0)
        if adjust:
            ratio = (sh[per[k + 1]] / sh[per[k]]).replace([np.inf, -np.inf], np.nan).groupby("cusip").median()
            ratio = ratio.reindex(g.index)
            split = ((ratio >= 1.8) & (g < 0.7)) | ((ratio <= 1 / 1.8) & (g > 1.4))
            adj = g * ratio
            ok = split & (adj > 0.5) & (adj < 2.0)
            g = g.where(~ok, adj)
        G[k] = g
    return G


def run(G, b, sp, per, topn, scen, cost):
    pf = portfolios(b, topn)
    rows, prev = [], None
    for k, q in enumerate(per):
        w, filed = pf[q]
        if scen == "A":
            if k + 1 >= len(per): break
            d0, d1 = per[k], per[k + 1]
            gr = lambda c: G[k].get(c, np.nan)
        elif scen == "C":
            if k + 2 >= len(per): break
            d0, d1 = per[k + 1], per[k + 2]
            gr = lambda c: G[k + 1].get(c, np.nan)
        else:
            if k + 2 >= len(per): break
            d0, d1 = filed, pf[per[k + 1]][1]
            fr0 = (d0 - per[k]).days / (per[k + 1] - per[k]).days
            fr1 = (d1 - per[k + 1]).days / (per[k + 2] - per[k + 1]).days
            gr = lambda c: G[k].get(c, np.nan) ** (1 - fr0) * G[k + 1].get(c, np.nan) ** fr1
        rs, ws = [], []
        for c, wt in w.items():
            g = gr(c)
            if np.isfinite(g) and g > 0:
                rs.append(g - 1); ws.append(wt)
        if not ws:
            continue
        r = float(np.dot(np.array(ws) / sum(ws), rs))
        cov = float(sum(ws))
        turn = 1.0 if prev is None else float(w.sub(prev, fill_value=0).abs().sum())
        prev = w
        rows.append(dict(start=d0, end=d1, r=r - cost * turn, spx=interp_sp(sp, d1) / interp_sp(sp, d0) - 1, cov=cov))
    return pd.DataFrame(rows)


def stats(df):
    yrs = (df.end.iloc[-1] - df.start.iloc[0]).days / 365.25
    def one(r):
        eq = (1 + r).cumprod()
        pk = np.maximum.accumulate(np.r_[1.0, eq.to_numpy()])[1:]
        n_per = len(r) / yrs
        return (eq.iloc[-1] ** (1 / yrs) - 1, r.std(ddof=1) * np.sqrt(n_per), r.mean() / r.std(ddof=1) * np.sqrt(n_per), float(((pk - eq.to_numpy()) / pk).max()))
    c, v, s, d = one(df.r)
    c2, v2, s2, d2 = one(df.spx)
    ex = df.r - df.spx
    t = ex.mean() / (ex.std(ddof=1) / np.sqrt(len(ex)))
    return dict(n=len(df), cagr_pct=round(100 * c, 2), vol_pct=round(100 * v, 1), sharpe=round(s, 2), maxdd_pct=round(100 * d, 1), spx_cagr_pct=round(100 * c2, 2), spx_sharpe=round(s2, 2),
                spx_maxdd_pct=round(100 * d2, 1), excess_pct=round(100 * (c - c2), 2), t_excess=round(float(t), 2), beat_pct=round(100 * float((ex > 0).mean()), 1), coverage_pct=round(100 * df["cov"].mean(), 1))


def main():
    px, b = load()
    sp = sp_level()
    h = load_raw()
    per = sorted(b.period.unique())
    per = [pd.Timestamp(x) for x in per]
    G = growth_table(h, per)
    G0 = growth_table(h, per, adjust=False)
    rows = []
    res = {}
    for name, topn in [("C5", 5), ("C10", 10), ("CALL", 0)]:
        for scen in "ABC":
            df = run(G, b, sp, per, topn, scen, COST)
            res[(name, scen)] = stats(df)
            rows.append({"portfel": name, "stsenariy": scen, **res[(name, scen)]})
        res[(name, "Bs")] = stats(run(G, b, sp, per, topn, "B", STRESS))
        res[(name, "B_nosplit")] = stats(run(G0, b, sp, per, topn, "B", COST))
    out = ["# Berkshire 13F portfelini ko'chirish: natijalar (STRATEGY_13F_COPY.md)\n", "Narx: 13F implied (value/shares, 9 fond medianasi), faqat narx; benchmark S&P 500 narx (Shiller). Xarajat 10 b.p.\n"]
    out.append(pd.DataFrame(rows).to_markdown(index=False) + "\n")
    out.append("## Split tuzatmasiz (xato variant, faqat ma'lumot; birinchi ishga tushirish shunday edi)\n" + pd.DataFrame([{"portfel": n, "cagr_pct": res[(n, "B_nosplit")]["cagr_pct"], "excess_pct": res[(n, "B_nosplit")]["excess_pct"]} for n in ["C5", "C10", "CALL"]]).to_markdown(index=False) + "\n")
    crit_rows = []
    for name in ["C5", "C10"]:
        B, C, Bs = res[(name, "B")], res[(name, "C")], res[(name, "Bs")]
        crit = {"a B: ortiqcha>=1.0% va t>=1.65": B["excess_pct"] >= 1.0 and B["t_excess"] >= 1.65, "b C: ortiqcha>0": C["excess_pct"] > 0, "c B: Sharpe>=S&P": B["sharpe"] >= B["spx_sharpe"],
                "d B: DD<=1.1xS&P DD": B["maxdd_pct"] <= 1.1 * B["spx_maxdd_pct"], "e stress ortiqcha>0": Bs["excess_pct"] > 0}
        out.append(f"## Mezonlar {name}\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**{name}: {'USTUNLIK BELGISI (dastlabki)' if all(crit.values()) else 'USTUNLIK TOPILMADI'}**\n")
    open("reports/copy13f_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
