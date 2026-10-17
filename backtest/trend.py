"""Daily trend/momentum research per STRATEGY_TREND.md (pre-registered, commit ac9c18a). Nothing here is tuned.

Usage: python -m backtest.trend      -> reports/trend_results.md
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

GOLD_JSONL = "/tmp/claude-0/daily/XAU_1d.jsonl"
FX_CSV = "/home/user/datasets/exchange-rates/data/daily.csv"
BRENT_CSV = "/home/user/datasets/oil-prices/data/brent-daily.csv"
FX_COUNTRIES = ["Euro", "United Kingdom", "Japan", "Switzerland", "Canada", "Australia", "New Zealand", "Sweden"]
WARM = 260
LBS = (21, 63, 126, 252)


# ---------------------------------------------------------------- data
def load_gold():
    g = pd.read_json(GOLD_JSONL, lines=True)
    g["Date"] = pd.to_datetime(g["Date"], format="%Y.%m.%d")
    s = g.set_index("Date").sort_index()["Close"]
    return s[(s.index >= "2004-06-11") & (s.index < "2025-03-01")].astype(float)


def load_confirm():
    out = {}
    fx = pd.read_csv(FX_CSV, parse_dates=["Date"])
    for c in FX_COUNTRIES:
        s = fx[fx.Country == c].dropna(subset=["Exchange rate"]).set_index("Date")["Exchange rate"].sort_index().astype(float)
        out[c] = s[s.index <= "2025-12-31"]
    b = pd.read_csv(BRENT_CSV, parse_dates=["Date"]).dropna().set_index("Date")["Price"].sort_index().astype(float)
    out["Brent"] = b[b.index <= "2025-12-31"]
    return out


# ---------------------------------------------------------------- signals
def sgn(P, L):
    return np.sign(P / P.shift(L) - 1.0)


def s1(P):
    return sgn(P, 252)


def s2(P):
    return sum(sgn(P, L) for L in LBS) / 4.0


def s3(P):
    return np.sign(P.rolling(50).mean() - P.rolling(200).mean())


def s4(P):
    hi55, lo55 = P.shift(1).rolling(55).max().to_numpy(), P.shift(1).rolling(55).min().to_numpy()
    hi20, lo20 = P.shift(1).rolling(20).max().to_numpy(), P.shift(1).rolling(20).min().to_numpy()
    x, u, out = P.to_numpy(), 0, np.full(len(P), np.nan)
    for t in range(len(x)):
        if np.isnan(hi55[t]):
            continue
        if u == 1 and x[t] < lo20[t]:
            u = 0
        if u == -1 and x[t] > hi20[t]:
            u = 0
        if x[t] > hi55[t]:
            u = 1
        elif x[t] < lo55[t]:
            u = -1
        out[t] = u
    return pd.Series(out, index=P.index)


SIGNALS = {"S1 TSMOM-252": s1, "S2 Ansambl": s2, "S3 MA50/200": s3, "S4 Donchian 55/20": s4}


# ---------------------------------------------------------------- simulation
@dataclass
class Cost:
    c_frac: float | None = None      # fraction of notional per unit turnover (None -> use c_usd / price)
    c_usd: float = 0.0
    fin: float = 0.0                 # annual financing on |position|


GOLD_COST, FX_COST, BRENT_COST = Cost(c_usd=0.50, fin=0.03), Cost(c_frac=1.5e-4), Cost(c_frac=5e-4)


def positions(P, s, target=0.10, cap=3.0, db=0.10, long_only=False):
    r = P.pct_change().to_numpy()
    n = len(P)
    v = np.full(n, np.nan)
    v[60] = np.var(r[1:61], ddof=1)
    for t in range(61, n):
        v[t] = 0.94 * v[t - 1] + 0.06 * r[t] ** 2
    sig = np.sqrt(252 * v)
    sv = s.to_numpy()
    w = np.zeros(n)
    for t in range(WARM, n):
        if np.isnan(sv[t]) or np.isnan(sig[t]):
            w[t] = w[t - 1]
            continue
        st = max(sv[t], 0.0) if long_only else sv[t]
        wstar = st * min(cap, target / sig[t])
        w[t] = wstar if abs(wstar - w[t - 1]) >= db else w[t - 1]
    return r, w


def pnl_arrays(P, r, w, cost: Cost, c_mult=1.0, fin=None):
    n = len(P)
    pos, turn = np.zeros(n), np.zeros(n)
    pos[1:] = w[:-1]
    turn[2:] = np.abs(w[1:-1] - w[:-2])
    price_prev = np.r_[np.nan, P.to_numpy()[:-1]]
    cf = (cost.c_frac if cost.c_frac is not None else cost.c_usd / price_prev) * c_mult
    f = cost.fin if fin is None else fin
    return pos, turn, cf, f


def net_series(pos, turn, cf, f, r):
    return pos * np.nan_to_num(r) - turn * np.nan_to_num(cf) - np.abs(pos) * f / 252


def sharpe(x):
    sd = x.std(ddof=1)
    return x.mean() / sd * np.sqrt(252) if sd > 0 else np.nan


def nw_t(x, lags=10):
    x = np.asarray(x, float)
    n, mu = len(x), x.mean()
    e = x - mu
    lrv = e @ e / n
    for l in range(1, lags + 1):
        lrv += 2 * (1 - l / (lags + 1)) * (e[l:] @ e[:-l] / n)
    return mu / np.sqrt(lrv / n)


def maxdd(x):
    eq = np.cumprod(1 + x)
    pk = np.maximum.accumulate(eq)
    return float(((pk - eq) / pk).max())


def window_mask(idx, start, end):
    return (idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))


def timing_p(pos, turn, cf, f, r, mask, draws=5000, seed=1):
    p0, t0, c0, r0 = pos[mask], turn[mask], cf[mask], np.nan_to_num(r[mask])
    obs = sharpe(net_series(p0, t0, c0, f, r0))
    rng = np.random.default_rng(seed)
    T, cnt = len(p0), 0
    for _ in range(draws):
        d = int(rng.integers(252, T - 252))
        cnt += sharpe(net_series(np.roll(p0, d), np.roll(t0, d), c0, f, r0)) >= obs
    return obs, (cnt + 1) / (draws + 1)


# ---------------------------------------------------------------- stage 1 (gold)
def stage1(P, name, fn):
    s = fn(P)
    r, w = positions(P, s)
    pos, turn, cf, f = pnl_arrays(P, r, w, GOLD_COST)
    idx = P.index
    start = idx[WARM + 1]
    full = window_mask(idx, start, "2025-02-28")
    net = net_series(pos, turn, cf, f, r)[full]
    obs, p = timing_p(pos, turn, cf, f, r, full)
    eras = {}
    for k, (a, b) in {"A": (start, "2011-12-31"), "B": ("2012-01-01", "2018-12-31"), "C": ("2019-01-01", "2025-02-28")}.items():
        m = window_mask(idx, a, b)
        eras[k] = sharpe(net_series(pos, turn, cf, f, r)[m])
    # stress: costs x2 and financing 5%
    pos2, turn2, cf2, f2 = pnl_arrays(P, r, w, GOLD_COST, c_mult=2.0, fin=0.05)
    stress = sharpe(net_series(pos2, turn2, cf2, f2, r)[full])
    # alpha/beta vs gold
    X = sm.add_constant(np.nan_to_num(r[full]))
    ols = sm.OLS(net, X).fit(cov_type="HAC", cov_kwds={"maxlags": 10})
    changes = int((np.diff(np.sign(w[WARM:])) != 0).sum())
    # long/flat descriptive
    rl, wl = positions(P, s, long_only=True)
    pl, tl, cl, fl = pnl_arrays(P, rl, wl, GOLD_COST)
    netl = net_series(pl, tl, cl, fl, rl)[full]
    # buy&hold benchmark at the same 10% vol target is meaningless; use raw gold returns
    bh = np.nan_to_num(r[full])
    row = dict(cell=name, net_sharpe=round(sharpe(net), 3), nw_t=round(nw_t(net), 2), timing_p=round(p, 4), eraA=round(eras["A"], 2), eraB=round(eras["B"], 2),
               eraC=round(eras["C"], 2), maxDD_pct=round(100 * maxdd(net), 1), stress_sharpe=round(stress, 3), changes=changes, ann_ret_pct=round(100 * net.mean() * 252, 2),
               avg_abs_pos=round(float(np.abs(pos[full]).mean()), 2), alpha_pct_yr=round(float(ols.params[0]) * 252 * 100, 2), alpha_t=round(float(ols.tvalues[0]), 2),
               beta=round(float(ols.params[1]), 3), LF_sharpe=round(sharpe(netl), 3), LF_maxDD_pct=round(100 * maxdd(netl), 1))
    c = dict(a=row["net_sharpe"] >= 0.30, b=row["nw_t"] >= 2.0, c=row["timing_p"] <= 0.10,
             d=(sum(v > 0 for v in eras.values()) >= 2 and min(eras.values()) >= -0.30), e=row["maxDD_pct"] <= 25.0, f=row["stress_sharpe"] > 0, g=changes >= 20)
    return row, c, dict(net=net, start=start, bh_sharpe=sharpe(bh), bh_dd=maxdd(bh))


# ---------------------------------------------------------------- stage 2 (confirmation)
def stage2(series, name, fn):
    cal = pd.bdate_range("2000-01-03", "2025-12-31")
    per, POS, TURN, CF, R = {}, [], [], [], []
    for k, P in series.items():
        s = fn(P)
        r, w = positions(P, s)
        cost = BRENT_COST if k == "Brent" else FX_COST
        pos, turn, cf, f = pnl_arrays(P, r, w, cost)
        idx = P.index
        start = max(idx[WARM + 1], pd.Timestamp("2000-01-03"))
        m = window_mask(idx, start, "2025-12-31")
        net = net_series(pos, turn, cf, f, r)[m]
        per[k] = dict(sharpe=sharpe(net), t=nw_t(net), start=str(start.date()))
        # common calendar arrays (flat return on missing days; position carried)
        ser = lambda a: pd.Series(a, index=idx).reindex(cal).ffill() if False else pd.Series(a, index=idx)
        rr = pd.Series(np.nan_to_num(r), index=idx).reindex(cal).fillna(0.0).to_numpy()
        pp = pd.Series(pos, index=idx).reindex(cal).ffill().fillna(0.0).to_numpy()
        tt = pd.Series(turn, index=idx).reindex(cal).fillna(0.0).to_numpy()
        cc = (pd.Series(np.nan_to_num(cf), index=idx).reindex(cal).ffill().fillna(0.0).to_numpy())
        POS.append(pp), TURN.append(tt), CF.append(cc), R.append(rr)
    POS, TURN, CF, R = map(np.array, (POS, TURN, CF, R))
    port = (POS * R - TURN * CF).mean(axis=0)
    rng, T, cnt = np.random.default_rng(2), len(cal), 0
    obs = sharpe(port)
    for _ in range(3000):
        acc = np.zeros(T)
        for i in range(len(POS)):
            d = int(rng.integers(252, T - 252))
            acc += np.roll(POS[i], d) * R[i] - np.roll(TURN[i], d) * CF[i]
        cnt += sharpe(acc / len(POS)) >= obs
    p = (cnt + 1) / 3001
    npos = sum(v["sharpe"] > 0 for v in per.values())
    return dict(cell=name, port_sharpe=round(obs, 3), port_t=round(nw_t(port), 2), timing_p=round(p, 4), positive=f"{npos}/{len(per)}",
                maxDD_pct=round(100 * maxdd(port), 1)), dict(h=obs >= 0.20 and nw_t(port) >= 1.65, i=npos >= 6, j=p <= 0.10), per


def main():
    gold = load_gold()
    conf = load_confirm()
    out = ["# Kunlik trend/momentum — natijalar (reja: STRATEGY_TREND.md, commit ac9c18a)\n",
           f"Oltin: {gold.index.min().date()} … {gold.index.max().date()}, {len(gold)} kun. Tasdiqlash: {', '.join(conf)} (2000-01-03 … 2025-12-31). "
           "Hamma parametrlar rejadagidek, sozlanmagan.\n",
           "Ma'lumot sifati: kunlik oltin yopilishi mustaqil manba (alshahri BID H1) bilan solishtirildi; to'liq kunlarda (≥20 bar) kunlik daromadlar korrelyatsiyasi **0.998** "
           "(talab ≥0.99, bajarildi). Barcha kunlar bo'yicha 0.987: farq mustaqil manbaning to'liq bo'lmagan kunlaridan. M1 bilan solishtirish mustaqil emas (bir manba).\n"]
    rows, c1, extra, st2, c2, per2 = [], {}, {}, [], {}, {}
    for name, fn in SIGNALS.items():
        row, c, ex = stage1(gold, name, fn)
        rows.append(row), c1.__setitem__(name, c), extra.__setitem__(name, ex)
        r2, cc, per = stage2(conf, name, fn)
        st2.append(r2), c2.__setitem__(name, cc), per2.__setitem__(name, per)
    df1 = pd.DataFrame(rows).set_index("cell")
    out += ["\n## Stage 1: oltin (sof, 10% vol maqsad, $0.50 xarajat, 3% moliyalashtirish)\n",
            df1[["net_sharpe", "nw_t", "timing_p", "eraA", "eraB", "eraC", "maxDD_pct", "stress_sharpe", "changes", "ann_ret_pct", "avg_abs_pos"]].to_markdown() + "\n",
            "\nTavsif (qarorga ta'sir qilmaydi): oltinga nisbatan alfa/beta va long/flat varianti:\n",
            df1[["alpha_pct_yr", "alpha_t", "beta", "LF_sharpe", "LF_maxDD_pct"]].to_markdown() + "\n"]
    e0 = extra["S1 TSMOM-252"]
    out.append(f"\nBenchmark: oltin buy&hold (shu davr, {e0['start'].date()} dan) Sharpe {e0['bh_sharpe']:.2f}, maksimal drawdown {100*e0['bh_dd']:.1f}%.\n")
    df2 = pd.DataFrame(st2).set_index("cell")
    out += ["\n## Stage 2: mustaqil aktivlar portfeli (8 valyuta + Brent, faqat narx)\n", df2.to_markdown() + "\n"]
    pa = pd.DataFrame({k: {i: round(v["sharpe"], 2) for i, v in per.items()} for k, per in per2.items()})
    out += ["\nAktivlar bo'yicha sof Sharpe:\n", pa.to_markdown() + "\n"]
    verd = []
    for name in SIGNALS:
        a, b = c1[name], c2[name]
        verd.append({"cell": name, **{k: bool(v) for k, v in {**a, **b}.items()}, "PASS": bool(all(a.values()) and all(b.values()))})
    dv = pd.DataFrame(verd).set_index("cell")
    out += ["\n## Oldindan belgilangan mezon bo'yicha qaror\n",
            "(a) Sharpe≥0.30, (b) t≥2.0, (c) timing p≤0.10, (d) davrlar, (e) DD≤25%, (f) stress, (g) ≥20 almashtirish | (h) portfel Sharpe≥0.20 & t≥1.65, (i) ≥6/9 aktiv>0, (j) portfel timing p≤0.10\n",
            dv.to_markdown() + "\n"]
    open("reports/trend_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
