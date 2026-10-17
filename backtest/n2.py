"""N2: gold reaction to scheduled USD news (STRATEGY_NEXT.md section 4, pre-registered). Nothing is tuned.

Usage: python -m backtest.n2 discovery|validation|final
Each stage reads the candidate list written by the previous stage (committed in between).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

PARQ = "/tmp/claude-0/gold1m/XAU_M1_2018_2025.parquet"
CAL = "/tmp/claude-0/cal/ff.csv"
PERIODS = {"discovery": ("2018-01-01", "2022-01-01"), "validation": ("2022-01-01", "2024-01-01"), "final": ("2024-01-01", "2025-03-01")}
FAM = {"Non-Farm Employment Change": ("08:30", 1), "Unemployment Rate": ("08:30", -1), "CPI m/m": ("08:30", 1), "Core CPI m/m": ("08:30", 1), "Retail Sales m/m": ("08:30", 1),
       "Core Retail Sales m/m": ("08:30", 1), "ISM Manufacturing PMI": ("10:00", 1), "ISM Services PMI": ("10:00", 1), "Average Hourly Earnings m/m": ("08:30", 1), "Federal Funds Rate": ("14:00", 1)}
COST, STRESS = 0.80, 1.50
HOLDS = (5, 15, 30)
CELLS = [(m, h) for m in ("cont", "fade") for h in HOLDS]
CAND = Path("reports/n2_candidates.json")


def num(x):
    if not isinstance(x, str):
        return np.nan
    s = x.strip().replace("%", "").replace(",", "")
    mult = 1.0
    if s and s[-1] in "KMB":
        mult = {"K": 1e3, "M": 1e6, "B": 1e9}[s[-1]]
        s = s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return np.nan


def events():
    d = pd.read_csv(CAL, usecols=["DateTime", "Currency", "Impact", "Event", "Actual", "Forecast"])
    d = d[(d.Currency == "USD") & (d.Impact == "High Impact Expected") & d.Event.isin(FAM)].copy()
    d["date"] = pd.to_datetime(d.DateTime.str[:10])
    d["A"], d["F"] = d.Actual.map(num), d.Forecast.map(num)
    d = d.dropna(subset=["A", "F"]).sort_values(["Event", "date"])
    rows = []
    for ev, g in d.groupby("Event"):
        sgn = FAM[ev][1]
        s = (g.A - g.F).to_numpy()
        sd = pd.Series(s).shift(1).expanding(min_periods=12).std().to_numpy()
        g = g.assign(z=sgn * s / sd)
        rows.append(g[np.isfinite(g.z)])
    e = pd.concat(rows)
    loc = [pd.Timestamp(f"{r.date.date()} {FAM[r.Event][0]}", tz="America/New_York").tz_convert("UTC").tz_localize(None) for r in e.itertuples()]
    e["t"] = loc
    e = e[e.z.abs() >= 1.0]
    e = e.loc[e.groupby("t").z.apply(lambda s: s.abs().idxmax())] if e.t.duplicated().any() else e
    return e.sort_values("t").reset_index(drop=True)


class Gold:
    def __init__(self):
        m1 = pd.read_parquet(PARQ)
        m1 = m1[(m1.index >= "2018-01-01") & (m1.index < "2025-03-01")]
        m1.index = m1.index.tz_localize(None)
        self.m1 = m1
        self.idx = m1.index.to_numpy()
        self.o, self.h, self.l, self.c = (m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        pc = h1.close.shift()
        tr = pd.concat([h1.high - h1.low, (h1.high - pc).abs(), (h1.low - pc).abs()], axis=1).max(axis=1)
        self.atr = tr.rolling(14).mean()
        self.h1end = (h1.index + pd.Timedelta("1h")).to_numpy()

    def bar(self, ts):
        k = np.searchsorted(self.idx, np.datetime64(ts))
        return k if k < len(self.idx) and self.idx[k] == np.datetime64(ts) else -1


def trades(G, E):
    out = []
    for r in E.itertuples():
        t = r.t
        b0, b1 = G.bar(t - pd.Timedelta(minutes=1)), G.bar(t + pd.Timedelta(minutes=1))
        if b0 < 0 or b1 < 0:
            continue
        k = np.searchsorted(G.h1end, np.datetime64(t), side="right") - 1
        atr = G.atr.iloc[k] if k >= 0 else np.nan
        if not np.isfinite(atr) or atr <= 0:
            continue
        react = G.c[b1] - G.c[b0]
        if react == 0:
            continue
        d0 = 1 if react > 0 else -1
        entry = G.c[b1]
        for mode in ("cont", "fade"):
            dr = d0 if mode == "cont" else -d0
            stop = entry - dr * atr
            for h in HOLDS:
                xb = G.bar(t + pd.Timedelta(minutes=1 + h))
                if xb < 0:
                    continue
                x = G.c[xb]
                for b in range(b1 + 1, xb + 1):
                    if G.idx[b] - G.idx[b1] > np.timedelta64(h + 1, "m"):
                        break
                    if dr == 1 and G.l[b] <= stop:
                        x = stop; break
                    if dr == -1 and G.h[b] >= stop:
                        x = stop; break
                g = (x - entry) * dr
                out.append(dict(t=t, date=t.normalize(), fam=r.Event, z=r.z, mode=mode, h=h, dir=dr, atr=atr, R=(g - COST) / atr, R_stress=(g - STRESS) / atr))
    return pd.DataFrame(out)


def clustered(x):
    n = len(x)
    if n < 3:
        return np.nan, np.nan
    m = x.R.mean()
    se = np.sqrt(((x.R - m).groupby(x.date).sum() ** 2).sum()) / n
    return m, float(1 - norm.cdf(m / se)) if se > 0 else np.nan


def equity(x, risk=0.005):
    r = x.sort_values("t").R.to_numpy() * risk
    eq = np.cumprod(1 + r)
    pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
    mo = pd.Series(r, index=pd.DatetimeIndex(x.sort_values("t").t)).groupby(lambda i: (i.year, i.month)).apply(lambda s: (1 + s).prod() - 1)
    return dict(ret_pct=round(100 * (eq[-1] - 1), 1), maxDD_pct=round(100 * float(((pk - eq) / pk).max()), 1), pos_months_pct=round(float((mo > 0).mean() * 100), 1), worst_month_pct=round(100 * mo.min(), 1))


def holm(ps, alpha=0.05):
    o = np.argsort(ps)
    ok = np.zeros(len(ps), bool)
    for rank, i in enumerate(o):
        if ps[i] <= alpha / (len(ps) - rank):
            ok[i] = True
        else:
            break
    return ok


def main():
    stage = sys.argv[1]
    lo, hi = PERIODS[stage]
    E = events()
    G = Gold()
    T = trades(G, E)
    T = T[(T.date >= lo) & (T.date < hi)]
    lines = [f"# N2 {stage} ({lo} … {hi})\n", f"Hodisalar (|z|≥1, vaqti M1 da bor): {T.groupby('t').ngroups}; xarajat $0.80.\n"]
    rows = []
    for mode, h in CELLS:
        x = T[(T["mode"] == mode) & (T.h == h)]
        m, p = clustered(x)
        s = x.assign(R=x.R_stress)
        rows.append(dict(cell=f"{mode}/{h}m", N=len(x), meanR=round(m, 4), win_pct=round(100 * (x.R > 0).mean(), 1), p_one=round(p, 3), stress_meanR=round(s.R.mean(), 4)))
    tab = pd.DataFrame(rows)
    lines.append(tab.to_markdown(index=False) + "\n")
    if stage == "discovery":
        ok = holm(tab.p_one.fillna(1).to_numpy())
        cand = [r.cell for r, o in zip(tab.itertuples(), ok) if o and r.meanR >= 0.05 and r.N >= 60]
        lines.append(f"Holm (6 test, 5%) + N≥60 + meanR≥0.05: nomzodlar = {cand}\n")
        CAND.write_text(json.dumps({"discovery": cand}))
    else:
        cand = json.loads(CAND.read_text())["validation" if stage == "final" else "discovery"]
        res = []
        for c in cand:
            r = tab[tab.cell == c].iloc[0]
            if stage == "validation":
                good = r.meanR > 0 and r.p_one <= 0.10 and r.N >= 40
            else:
                mode, h = c.split("/")
                x = T[(T["mode"] == mode) & (T.h == int(h[:-1]))]
                eq = equity(x)
                lines.append(f"{c}: equity (0.5% risk) {eq}\n")
                good = r.meanR > 0 and r.p_one <= 0.10 and r.stress_meanR > 0 and r.N >= 20 and eq["maxDD_pct"] <= 30
            res.append(c) if good else None
        lines.append(f"Bosqich mezonidan o'tgan: {res}\n")
        CAND.write_text(json.dumps({**json.loads(CAND.read_text()), stage: res}))
    Path(f"reports/n2_{stage}.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
