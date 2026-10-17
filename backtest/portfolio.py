"""Gold portfolio role / risk overlays / fundamentals (STRATEGY_PORTFOLIO.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.portfolio      -> reports/portfolio_results.md
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

D = "/home/user/datasets"
START, END = "1973-01", "2026-06"
E1, E2, FULL = ("1976-01", "1999-12"), ("2000-01", "2026-06"), ("1976-01", "2026-06")
DUR = 7.5


# ------------------------------------------------------------------ data
def load():
    idx = pd.period_range(START, END, freq="M")
    g = pd.read_csv(f"{D}/gold-prices/data/monthly.csv")
    g.index = pd.to_datetime(g.Date).dt.to_period("M")
    P = g.Price.reindex(idx).astype(float)
    sp = pd.read_csv(f"{D}/s-and-p-500/data/data.csv", parse_dates=["Date"])
    sp.index = sp.Date.dt.to_period("M")
    S = sp.SP500.reindex(idx).astype(float)
    Dv = sp.Dividend.where(sp.Dividend > 0).ffill().reindex(idx)
    b = pd.read_csv(f"{D}/bond-yields-us-10y/data/monthly.csv", parse_dates=["Date"])
    b.index = b.Date.dt.to_period("M")
    y = b.Rate.reindex(idx).astype(float)
    c = pd.read_csv(f"{D}/cpi-us/data/cpiai.csv", parse_dates=["Date"])
    c.index = c.Date.dt.to_period("M")
    cpi = c.Index.reindex(idx).astype(float)
    fx = pd.read_csv(f"{D}/exchange-rates/data/daily.csv", parse_dates=["Date"])
    cols = {}
    for k in ["United Kingdom", "Japan", "Switzerland", "Canada", "Australia", "New Zealand", "Sweden", "Norway", "Denmark"]:
        s = fx[fx.Country == k].dropna(subset=["Exchange rate"]).set_index("Date")["Exchange rate"]
        m = s.groupby(s.index.to_period("M")).last()
        cols[k] = m.reindex(idx)
    return dict(idx=idx, P=P, S=S, Dv=Dv, y=y, cpi=cpi, fx=pd.DataFrame(cols))


def returns(d):
    P, S, Dv, y = d["P"], d["S"], d["Dv"], d["y"]
    r_g = P / P.shift(1) - 1
    dy = Dv / S
    r_e = S / S.shift(1) - 1 + dy / 12
    r_b = y.shift(1) / 1200 - DUR * (y - y.shift(1)) / 100
    return pd.DataFrame({"gold": r_g, "equity": r_e, "bond": r_b})


# ------------------------------------------------------------------ metrics
def metrics(r):
    r = np.asarray(r, float)
    eq = np.cumprod(1 + r)
    pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
    dd = float(((pk - eq) / pk).max())
    n = len(r)
    cagr = eq[-1] ** (12 / n) - 1
    w12 = pd.Series(r).add(1).rolling(12).apply(np.prod, raw=True).sub(1).min() if n >= 12 else np.nan
    sd = r.std(ddof=1)
    return dict(CAGR_pct=round(100 * cagr, 2), vol_pct=round(100 * sd * np.sqrt(12), 2), Sharpe=round(r.mean() / sd * np.sqrt(12), 3) if sd > 0 else np.nan,
                maxDD_pct=round(100 * dd, 1), worst12m_pct=round(100 * w12, 1), Calmar=round(cagr / dd, 2) if dd > 0 else np.nan)


def sharpe(r):
    r = np.asarray(r, float)
    sd = r.std(ddof=1)
    return r.mean() / sd * np.sqrt(12) if sd > 0 else np.nan


def block_boot_delta(r1, r0, block=12, draws=5000, seed=3):
    rng = np.random.default_rng(seed)
    n = len(r1)
    nb = int(np.ceil(n / block))
    out = np.empty(draws)
    for i in range(draws):
        starts = rng.integers(0, n - block + 1, size=nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        out[i] = sharpe(r1[idx]) - sharpe(r0[idx])
    return out


def sl(s, era):
    return s[(s.index >= pd.Period(era[0], "M")) & (s.index <= pd.Period(era[1], "M"))]


# ------------------------------------------------------------------ study A
def portfolio_returns(R, w, cost=0.0005):
    """Monthly rebalanced fixed weights; cost = 5bp of traded notional (sum of |trades|)."""
    cols = list(R.columns)
    out, prev = [], None
    for t in range(len(R)):
        r = R.iloc[t].to_numpy(float)
        wt = np.asarray(w[t] if hasattr(w, "__len__") and not isinstance(w, np.ndarray) else w, float)
        if np.any(np.isnan(r)):
            out.append(np.nan)
            continue
        if prev is None:
            turn = 1.0
        else:
            drift = prev["w"] * (1 + prev["r"])
            drift = drift / drift.sum()
            turn = np.abs(wt - drift).sum()
        out.append(float(wt @ r) - cost * turn)
        prev = dict(w=wt, r=r)
    return pd.Series(out, index=R.index)


def study_a(R):
    base = R[["equity", "bond", "gold"]]
    ports = {}
    ports["P0 60/40"] = portfolio_returns(base, np.array([0.6, 0.4, 0.0]))
    ports["P1 54/36/10"] = portfolio_returns(base, np.array([0.54, 0.36, 0.10]))
    ports["P2 48/32/20"] = portfolio_returns(base, np.array([0.48, 0.32, 0.20]))
    vol = base.rolling(36).std().shift(1)
    wrp = (1 / vol).div((1 / vol).sum(axis=1), axis=0)
    ports["P3 risk parity"] = portfolio_returns(base, [wrp.iloc[t].to_numpy() for t in range(len(base))])
    ports["P4 faqat oltin"] = base["gold"]
    return pd.DataFrame(ports)


# ------------------------------------------------------------------ study B
def overlay_returns(rg, P, kind, skip=0, cost_sma=0.0010, cost_vol=0.0005):
    r = rg.to_numpy(float)
    px = P.to_numpy(float)
    n = len(r)
    pos = np.full(n, np.nan)
    for t in range(12 + skip, n - 1):
        u = t - skip
        if kind == "sma":
            pos[t + 1] = 1.0 if px[u] > np.mean(px[u - 9:u + 1]) else 0.0
        else:
            sig = np.std(r[u - 11:u + 1], ddof=1) * np.sqrt(12)
            pos[t + 1] = min(1.5, 0.10 / sig) if sig > 0 else 1.0
    out = np.full(n, np.nan)
    prev = np.nan
    for t in range(n):
        if np.isnan(pos[t]) or np.isnan(r[t]):
            continue
        ch = abs(pos[t] - (prev if not np.isnan(prev) else pos[t]))
        out[t] = pos[t] * r[t] - (cost_sma if kind == "sma" else cost_vol) * ch
        prev = pos[t]
    sw = int(np.nansum(np.abs(np.diff(pos[~np.isnan(pos)])) > 0.5)) if kind == "sma" else None
    return pd.Series(out, index=rg.index), sw


# ------------------------------------------------------------------ study C
def build_predictors(d):
    P, cpi, y, fx = d["P"], d["cpi"], d["y"], d["fx"]
    infl12 = 100 * (cpi.shift(1) / cpi.shift(13) - 1)
    real = y - infl12
    x1 = real - real.shift(12)
    x2 = np.log(fx / fx.shift(12)).mean(axis=1)
    x3 = np.log(P / P.shift(12))
    rp = np.log(P / cpi.shift(1))
    x4 = rp - sum(rp.shift(k) for k in range(1, 121)) / 120
    x5 = infl12
    return pd.DataFrame({"x1 real foiz o'zg.": x1, "x2 dollar 12m": x2, "x3 oltin momentum": x3, "x4 qiymat": x4, "x5 inflyatsiya": x5})


def cw_stat(e_b, e_m, yhat_b, yhat_m, lags):
    f = e_b ** 2 - e_m ** 2 + (yhat_b - yhat_m) ** 2
    res = sm.OLS(f, np.ones_like(f)).fit(cov_type="HAC", cov_kwds={"maxlags": max(lags, 0)})
    t = float(res.tvalues[0])
    return t, float(norm.sf(t))


def oos(P, X, h, skip=0, oos_start="1990-01", end=END):
    """Expanding-window one-predictor OLS vs expanding mean. Origin t uses only y_s with s+h(+skip) <= t."""
    idx = P.index
    lp = np.log(P.to_numpy(float))
    n = len(idx)
    y = np.full(n, np.nan)
    for t in range(n - h - skip):
        y[t] = lp[t + skip + h] - lp[t + skip]
    x = X.to_numpy(float)
    o0 = int(np.where(idx >= pd.Period(oos_start, "M"))[0][0])
    rows = []
    for t in range(o0, n - h - skip):
        tr = [s for s in range(n) if s + h + skip <= t and not np.isnan(x[s]) and not np.isnan(y[s])]
        if len(tr) < 36 or np.isnan(x[t]):
            continue
        xs, ys = x[tr], y[tr]
        b = np.cov(xs, ys, ddof=1)[0, 1] / np.var(xs, ddof=1)
        a = ys.mean() - b * xs.mean()
        rows.append((idx[t], y[t], a + b * x[t], ys.mean()))
    return pd.DataFrame(rows, columns=["t", "y", "yhat_m", "yhat_b"]).set_index("t")


def oos_stats(df, h):
    e_m, e_b = (df.y - df.yhat_m).to_numpy(), (df.y - df.yhat_b).to_numpy()
    r2 = 1 - (e_m ** 2).sum() / (e_b ** 2).sum()
    t, p = cw_stat(e_b, e_m, df.yhat_b.to_numpy(), df.yhat_m.to_numpy(), h - 1)
    return r2, t, p


def holm(ps, alpha=0.05):
    m = len(ps)
    order = np.argsort(ps)
    rej = np.zeros(m, bool)
    for k, ix in enumerate(order):
        if ps[ix] <= alpha / (m - k):
            rej[ix] = True
        else:
            break
    return rej


def seasonality(rg):
    r = rg.dropna()
    dum = np.array([1.0 if p.month in (9, 10, 11, 12, 1, 2) else 0.0 for p in r.index])
    res = sm.OLS(r.to_numpy(), sm.add_constant(dum)).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    t = float(res.tvalues[1])
    beta = float(res.params[1])
    eras = {}
    for nm, era in (("E1", E1), ("E2", E2)):
        s = sl(r, era)
        dm = np.array([1.0 if p.month in (9, 10, 11, 12, 1, 2) else 0.0 for p in s.index])
        eras[nm] = float(s[dm == 1].mean() - s[dm == 0].mean())
    return beta, t, float(norm.sf(t)), eras


def fmt(df, **kw):
    return df.to_markdown(**kw)


def main():
    d = load()
    R = returns(d)
    out = ["# Portfel/risk/fundamental tadqiqot — natijalar (reja: STRATEGY_PORTFOLIO.md)\n",
           "Hamma ta'rif va mezonlar rejadagidek, sozlanmagan. 1 oy kechiktirilgan variant — rejaga natijadan oldin qo'shilgan qo'shimcha tekshiruv (vaqt artefaktini aniqlash uchun).\n"]
    # ---------------- A
    ports = study_a(R)
    out.append("\n## A. Oltinning portfeldagi roli\n")
    rows = {}
    for nm, era in (("E1 1976-1999", E1), ("E2 2000-2026", E2), ("To'liq 1976-2026", FULL)):
        for pn in ports.columns:
            rows[(nm, pn)] = metrics(sl(ports[pn], era).dropna())
    out += [pd.DataFrame(rows).T.to_markdown() + "\n"]
    verdictA = {}
    boot_rows = {}
    for pn in ("P1 54/36/10", "P2 48/32/20", "P3 risk parity"):
        ok_eras = []
        for nm, era in (("E1", E1), ("E2", E2)):
            a, b = sl(ports[pn], era).dropna(), sl(ports["P0 60/40"], era).dropna()
            m1, m0 = metrics(a), metrics(b)
            ok_eras.append(m1["Sharpe"] > m0["Sharpe"] and m1["maxDD_pct"] <= m0["maxDD_pct"] + 1e-9)
        a, b = sl(ports[pn], FULL).dropna().to_numpy(), sl(ports["P0 60/40"], FULL).dropna().to_numpy()
        bd = block_boot_delta(a, b)
        p_boot = float((bd <= 0).mean())
        boot_rows[pn] = dict(dSharpe=round(sharpe(a) - sharpe(b), 3), CI90_lo=round(float(np.percentile(bd, 5)), 3), CI90_hi=round(float(np.percentile(bd, 95)), 3), p_dSharpe_le0=round(p_boot, 4),
                             E1_ok=ok_eras[0], E2_ok=ok_eras[1])
        verdictA[pn] = bool(all(ok_eras) and p_boot <= 0.10)
    out += ["\nSharpe farqi (P0 60/40 ga nisbatan), harakatlanuvchi blok bootstrap (12 oy, 5000):\n", pd.DataFrame(boot_rows).T.to_markdown() + "\n",
            f"\n**Mezon bo'yicha foydali (oltin vazni):** {verdictA}  (P3 risk parity — ma'lumot uchun; mezon P1, P2 uchun)\n"]
    # descriptive
    desc = {}
    for nm, era in (("E1", E1), ("E2", E2)):
        s = sl(R, era).dropna()
        desc[nm] = dict(corr_gold_equity=round(s.gold.corr(s.equity), 2), corr_gold_bond=round(s.gold.corr(s.bond), 2),
                        gold_avg_ret_in_equity_down5_pct=round(100 * s[s.equity < -0.05].gold.mean(), 2), n_months_equity_down5=int((s.equity < -0.05).sum()))
    out += ["\nTavsif (qarorga ta'sir qilmaydi):\n", pd.DataFrame(desc).T.to_markdown() + "\n"]
    # ---------------- B
    out.append("\n## B. Oltinga trend filtri va vol nazorati\n")
    rg, P = R["gold"], d["P"]
    bh = rg
    resB, verB = {}, {}
    for skip, lab in ((0, "asosiy"), (1, "1 oy kechiktirilgan")):
        for kind, nm in (("sma", "O1 SMA10"), ("vol", "O2 vol-maqsad")):
            ov, sw = overlay_returns(rg, P, kind, skip=skip)
            ok = []
            for en, era in (("E1", E1), ("E2", E2), ("To'liq", FULL)):
                a = sl(ov, era).dropna()
                b = sl(bh, era).reindex(a.index)
                ma, mb = metrics(a), metrics(b)
                resB[(f"{nm} ({lab})", en)] = dict(Sharpe=ma["Sharpe"], BH_Sharpe=mb["Sharpe"], maxDD_pct=ma["maxDD_pct"], BH_maxDD_pct=mb["maxDD_pct"], CAGR_pct=ma["CAGR_pct"],
                                                    BH_CAGR_pct=mb["CAGR_pct"], worst12m_pct=ma["worst12m_pct"], BH_worst12m_pct=mb["worst12m_pct"], switches=sw if en == "To'liq" else None)
                if en in ("E1", "E2"):
                    ok.append((mb["maxDD_pct"] - ma["maxDD_pct"]) / mb["maxDD_pct"] >= 0.20 and ma["Sharpe"] >= mb["Sharpe"] - 0.05)
            verB[f"{nm} ({lab})"] = bool(all(ok))
    out += [pd.DataFrame(resB).T.to_markdown() + "\n", f"\n**Mezon bo'yicha qimmatli overlay (ikkala davrda DD ≥20% kam va Sharpe ≥ BH−0.05):** {verB}\n"]
    # ---------------- C
    out.append("\n## C. Fundamental omillar (OOS 1990-01 →, kengayuvchi oyna, Clark–West, Holm)\n")
    X = build_predictors(d)
    rows, pvals, keys, store = [], [], [], {}
    for skip, lab in ((0, "asosiy"), (1, "1 oy kechiktirilgan")):
        for h in (3, 12):
            for col in X.columns:
                df = oos(P, X[col], h, skip=skip)
                r2, t, p = oos_stats(df, h)
                half1 = df[df.index < pd.Period("2008-01", "M")]
                half2 = df[df.index >= pd.Period("2008-01", "M")]
                r2a, r2b = oos_stats(half1, h)[0], oos_stats(half2, h)[0]
                rows.append(dict(variant=lab, h=h, predictor=col, N=len(df), OOS_R2=round(r2, 4), CW_t=round(t, 2), CW_p=round(p, 4), R2_1990_2007=round(r2a, 4), R2_2008_=round(r2b, 4)))
                store[(lab, h, col)] = df
    T = pd.DataFrame(rows)
    sea = seasonality(rg)
    out += [T.to_markdown(index=False) + "\n", f"\nMavsumiylik H_S (sentyabr–fevral − qolgan oylar): farq/oy = {sea[0]*100:.2f}% , t = {sea[1]:.2f}, bir tomonlama p = {sea[2]:.4f}; davrlar bo'yicha farq: E1 {sea[3]['E1']*100:+.2f}%, E2 {sea[3]['E2']*100:+.2f}%\n"]
    # Holm over the 10 main-variant tests + seasonality
    main = T[T.variant == "asosiy"]
    ps = list(main.CW_p) + [sea[2]]
    keys = [f"{r.predictor} h={r.h}" for r in main.itertuples()] + ["mavsumiylik"]
    rej = holm(np.array(ps))
    hm = pd.DataFrame({"test": keys, "p": np.round(ps, 4), "Holm_rad_etildi(5%)": rej})
    out += ["\nHolm tuzatmasi (11 test, asosiy variant):\n", hm.to_markdown(index=False) + "\n"]
    # economic test for Holm-significant predictors with R2>0 in both halves
    accepted = []
    for i, r in enumerate(main.itertuples()):
        if rej[i] and r.OOS_R2 > 0 and r.R2_1990_2007 > 0 and r.R2_2008_ > 0:
            df = store[("asosiy", r.h, r.predictor)]
            pos = (df.yhat_m > 0).astype(float)
            nxt = rg.shift(-1).reindex(df.index)
            ret = (pos * nxt).dropna()
            bhr = nxt.reindex(ret.index)
            okk = []
            for nm, a, b in (("1990-2007", None, "2007-12"), ("2008-", "2008-01", None)):
                s0, s1 = (pd.Period(a, "M") if a else ret.index.min()), (pd.Period(b, "M") if b else ret.index.max())
                x, y2 = ret[(ret.index >= s0) & (ret.index <= s1)], bhr[(bhr.index >= s0) & (bhr.index <= s1)]
                mx, my = metrics(x), metrics(y2)
                okk.append(mx["Sharpe"] >= my["Sharpe"] - 0.05 and (my["maxDD_pct"] - mx["maxDD_pct"]) / my["maxDD_pct"] >= 0.20)
            if all(okk):
                accepted.append(f"{r.predictor} h={r.h}")
    out += [f"\n**Qabul qilingan predikatorlar (Holm + ikki yarim + iqtisodiy sinov):** {accepted if accepted else 'yo`q'}\n"]
    open("reports/portfolio_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
