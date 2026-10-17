"""Multi-timeframe trend formation study (STRATEGY_MTF.md, pre-registered, commit c4eeeab). Nothing is tuned.

Usage: python -m backtest.mtf discovery|validation|final|fx
Stages are run in order; each stage reads the candidate list written by the previous stage (committed in between).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, mannwhitneyu

PARQ = "/tmp/claude-0/gold1m/XAU_M1_2018_2025.parquet"
PERIODS = {"discovery": ("2018-01-22", "2020-12-31"), "validation": ("2021-01-01", "2022-12-31"), "final": ("2023-01-01", "2025-02-28")}
TFS = {"M1": "1min", "M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h"}
COST = {"gold": (0.30, 0.50), "fx": (0.0001, 0.00015)}
HOLD_BARS = 96            # 24 hours of M15 bars
CELLS = [(l, h, t) for l in (0, 1) for h in (0, 1) for t in (0, 1)]


# ------------------------------------------------------------------ bars and trend states
def tf_bars(m1: pd.DataFrame, rule: str) -> pd.DataFrame:
    b = m1.resample(rule).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    c = b["close"]
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    d = np.sign(e20 - e50).replace(0, np.nan).ffill().fillna(0).astype(int)
    er = (c - c.shift(20)).abs() / c.diff().abs().rolling(20).sum()
    grp = (d != d.shift()).cumsum()
    age = d.groupby(grp).cumcount()
    pc = c.shift()
    tr = pd.concat([b.high - b.low, (b.high - pc).abs(), (b.low - pc).abs()], axis=1).max(axis=1)
    out = b.assign(d=d, er=er, age=age, atr=tr.rolling(14).mean())
    out["end"] = out.index + pd.Timedelta(rule if rule != "1h" else "1h")
    return out


def build(m1):
    return {k: tf_bars(m1, r) for k, r in TFS.items()}


def last_idx(bars, t):
    return np.searchsorted(bars["end"].to_numpy(), np.datetime64(t), side="right") - 1


def state_at(B, t, tf):
    k = last_idx(B[tf], t)
    return k


# ------------------------------------------------------------------ events
def make_events(B, lo, hi):
    h1, m15 = B["H1"], B["M15"]
    ev = []
    ends15 = m15["end"].to_numpy()
    for tfx, bars in (("F1", h1), ("F2", m15)):
        d = bars["d"].to_numpy()
        ends = bars["end"].to_numpy()
        for j in range(60, len(bars)):
            t = ends[j]
            ts = pd.Timestamp(t)
            if not (pd.Timestamp(lo) <= ts <= pd.Timestamp(hi) + pd.Timedelta(days=1)):
                continue
            if not (7 <= ts.hour < 20):
                continue
            if tfx == "F1":
                if d[j] == 0 or d[j - 1] == 0 or d[j] == d[j - 1]:
                    continue
                D, jh = int(d[j]), j
            else:
                jh = last_idx(B["H1"], t)
                if jh < 60:
                    continue
                D = int(h1["d"].iloc[jh])
                if D == 0 or int(h1["age"].iloc[jh]) < 6 or not (d[j] == D and d[j - 1] == -D):
                    continue
            ds = {x: int(B[x]["d"].iloc[last_idx(B[x], t)]) for x in ("M1", "M5", "M15", "H4")}
            lower = [ds["M1"], ds["M5"], ds["M15"]] if tfx == "F1" else [ds["M1"], ds["M5"]]
            er_h1 = float(h1["er"].iloc[jh])
            atr_h1 = float(h1["atr"].iloc[jh])
            if not np.isfinite(er_h1) or not np.isfinite(atr_h1) or atr_h1 <= 0:
                continue
            ev.append(dict(fam=tfx, t=ts, D=D, Lfull=int(all(x == D for x in lower)), H4ok=int(ds["H4"] == D), T=int(er_h1 >= 0.30), atr=atr_h1, jh=jh,
                           dM1=ds["M1"], dM5=ds["M5"], dM15=ds["M15"], dH4=ds["H4"], dH1=int(h1["d"].iloc[jh]),
                           vol_hi=int(atr_h1 / h1["atr"].iloc[max(0, jh - 250):jh].median() >= 1.2) if jh > 260 else 0))
    return pd.DataFrame(ev)


def outcomes(ev, B, cost_base, cost_stress):
    m15 = B["M15"]
    o, h, l, c = (m15[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    st = m15.index.to_numpy()
    rows = []
    for e in ev.itertuples():
        i0 = np.searchsorted(st, np.datetime64(e.t), side="left")
        if i0 >= len(st) or (st[i0] - np.datetime64(e.t)) > np.timedelta64(30, "m") or i0 + 2 >= len(st):
            rows.append((np.nan,) * 6)
            continue
        entry = o[i0]
        res = {}
        for name, dr in (("cont", e.D), ("fade", -e.D)):
            tp, sl = entry + dr * 2 * e.atr, entry - dr * e.atr
            R, nb = None, 0
            for k in range(i0, min(i0 + HOLD_BARS, len(st))):
                nb = k - i0 + 1
                if dr == 1:
                    if o[k] <= sl and k > i0:
                        R = (o[k] - entry) / e.atr
                    elif l[k] <= sl:
                        R = -1.0
                    elif o[k] >= tp and k > i0:
                        R = (o[k] - entry) / e.atr
                    elif h[k] >= tp:
                        R = 2.0
                else:
                    if o[k] >= sl and k > i0:
                        R = (entry - o[k]) / e.atr
                    elif h[k] >= sl:
                        R = -1.0
                    elif o[k] <= tp and k > i0:
                        R = (entry - o[k]) / e.atr
                    elif l[k] <= tp:
                        R = 2.0
                if R is not None:
                    break
            if R is None:
                R = (c[min(i0 + HOLD_BARS, len(st)) - 1] - entry) * dr / e.atr
            res[name] = R
        rows.append((res["cont"] - cost_base / e.atr, res["fade"] - cost_base / e.atr, res["cont"] - cost_stress / e.atr, res["fade"] - cost_stress / e.atr, res["cont"], res["fade"]))
    r = pd.DataFrame(rows, columns=["net_cont", "net_fade", "str_cont", "str_fade", "g_cont", "g_fade"], index=ev.index)
    return pd.concat([ev, r], axis=1).dropna(subset=["net_cont"])


# ------------------------------------------------------------------ statistics
def cluster_mean_test(x, groups):
    x = np.asarray(x, float)
    n, mu = len(x), x.mean()
    s = pd.Series(x - mu).groupby(np.asarray(groups)).sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / n
    t = mu / se if se > 0 else np.nan
    return mu, t, float(norm.sf(t))


def bh(pvals, q=0.10):
    m = len(pvals)
    order = np.argsort(pvals)
    thr = [(i + 1) / m * q for i in range(m)]
    k = max([i for i, ix in enumerate(order) if pvals[ix] <= thr[i]], default=-1)
    keep = np.zeros(m, bool)
    if k >= 0:
        keep[order[:k + 1]] = True
    return keep


def cell_table(E, col_c="net_cont", col_f="net_fade", min_n=1):
    rows = []
    for fam in ("F1", "F2"):
        for dirn, col in (("continue", col_c), ("fade", col_f)):
            for (l, h, t) in CELLS:
                g = E[(E.fam == fam) & (E.Lfull == l) & (E.H4ok == h) & (E["T"] == t)]
                if len(g) < min_n:
                    rows.append(dict(fam=fam, dir=dirn, Lfull=l, H4ok=h, T=t, N=len(g), mean_netR=np.nan, t=np.nan, p=np.nan))
                    continue
                mu, tt, p = cluster_mean_test(g[col], g.t.dt.to_period("W").astype(str))
                rows.append(dict(fam=fam, dir=dirn, Lfull=l, H4ok=h, T=t, N=len(g), mean_netR=round(mu, 3), t=round(tt, 2), p=round(p, 4)))
    return pd.DataFrame(rows)


def regression(B, lo, hi):
    h1 = B["H1"]
    ends = h1["end"]
    rows = []
    for j in range(60, len(h1) - 12):
        ts = ends.iloc[j]
        if not (pd.Timestamp(lo) <= ts <= pd.Timestamp(hi) + pd.Timedelta(days=1)) or not (7 <= ts.hour < 20):
            continue
        a = h1["atr"].iloc[j]
        if not np.isfinite(a) or a <= 0:
            continue
        rows.append(dict(y=(h1["close"].iloc[j + 12] - h1["close"].iloc[j]) / a, **{f"d_{x}": int(B[x]["d"].iloc[last_idx(B[x], ts)]) for x in TFS}))
    D = pd.DataFrame(rows).dropna()
    X = sm.add_constant(D[[f"d_{x}" for x in TFS]].astype(float))
    ols = sm.OLS(D.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 24})
    uni = {x: sm.OLS(D.y, sm.add_constant(D[f"d_{x}"].astype(float))).fit(cov_type="HAC", cov_kwds={"maxlags": 24}) for x in TFS}
    tab = pd.DataFrame({"joint_beta": ols.params.drop("const").round(3).to_numpy(), "joint_t": ols.tvalues.drop("const").round(2).to_numpy(),
                        "uni_beta": [round(uni[x].params.iloc[1], 3) for x in TFS], "uni_t": [round(uni[x].tvalues.iloc[1], 2) for x in TFS]}, index=list(TFS))
    return tab, len(D)


def descriptive(E, B):
    out = []
    f1 = E[E.fam == "F1"]
    rows = {}
    for x in ("M1", "M5", "M15", "H4"):
        al = f1[f1[f"d{x}"] == f1.D]
        na = f1[f1[f"d{x}"] != f1.D]
        rows[x] = dict(share_aligned=round(len(al) / len(f1), 2), cont_netR_aligned=round(al.net_cont.mean(), 3), cont_netR_not=round(na.net_cont.mean(), 3),
                       TP_first_aligned=round(100 * (al.g_cont >= 1.99).mean(), 1), TP_first_not=round(100 * (na.g_cont >= 1.99).mean(), 1))
    out.append(("F1: har bir vaqt oralig'i H1 yo'nalishiga mos kelganda (descriptive)", pd.DataFrame(rows).T))
    # trend duration after F1 flips: bars to next H1 flip and favourable excursion
    h1 = B["H1"]
    d = h1["d"].to_numpy()
    c = h1["close"].to_numpy()
    dur, ext = [], []
    for e in f1.itertuples():
        j = e.jh
        k = j + 1
        while k < len(d) and d[k] == d[j]:
            k += 1
        dur.append(k - j)
        ext.append(max(((c[j:k + 1] - c[j]) * e.D).max(), 0) / e.atr)
    f1 = f1.assign(dur=dur, ext=ext)
    rows = {}
    for col in ("Lfull", "H4ok", "T"):
        a, b = f1[f1[col] == 1], f1[f1[col] == 0]
        p_dur = mannwhitneyu(a.dur, b.dur).pvalue if len(a) > 5 and len(b) > 5 else np.nan
        p_ext = mannwhitneyu(a.ext, b.ext).pvalue if len(a) > 5 and len(b) > 5 else np.nan
        rows[col] = dict(N1=len(a), N0=len(b), med_dur_1=a.dur.median(), med_dur_0=b.dur.median(), p_dur=round(p_dur, 3), med_ext_1=round(a.ext.median(), 2),
                         med_ext_0=round(b.ext.median(), 2), p_ext=round(p_ext, 3))
    out.append(("F1: trend davomiyligi (H1 barlar) va maksimal harakat (ATR) — belgi=1 va belgi=0", pd.DataFrame(rows).T))
    out.append(("F1: umumiy", pd.DataFrame({"events": [len(f1)], "median_duration_bars": [f1.dur.median()], "share_dur_ge_24": [round((f1.dur >= 24).mean(), 2)],
                                          "median_extent_ATR": [round(f1.ext.median(), 2)]})))
    return out


def fmt(df, **kw):
    return df.to_markdown(**kw) if len(df) else "_yo'q_"


# ------------------------------------------------------------------ stages
def load_gold_B():
    m1 = pd.read_parquet(PARQ)
    m1 = m1[(m1.index >= "2018-01-01") & (m1.index < "2025-03-01")]
    m1.index = m1.index.tz_localize(None)       # UTC, tz-naive
    return build(m1)


def stage_report(stage, B, ev_all):
    lo, hi = PERIODS[stage]
    E = ev_all[(ev_all.t >= pd.Timestamp(lo)) & (ev_all.t <= pd.Timestamp(hi) + pd.Timedelta(days=1))]
    out = [f"# MTF tadqiqot: {stage} ({lo} … {hi})\n", f"Hodisalar: F1 {int((E.fam=='F1').sum())}, F2 {int((E.fam=='F2').sum())}. Natija: TP=2×ATR(H1), SL=1×ATR(H1), 24 soat, xarajat $0.30.\n"]
    tab = cell_table(E)
    return E, tab, out


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "discovery"
    Path("reports").mkdir(exist_ok=True)
    cache = Path("/tmp/claude-0/mtf_events.parquet")
    B = load_gold_B()
    if cache.exists():
        ev_all = pd.read_parquet(cache)
    else:
        ev = make_events(B, "2018-01-22", "2025-02-28")
        ev_all = outcomes(ev, B, *COST["gold"])
        ev_all.to_parquet(cache)
    lo, hi = PERIODS[stage] if stage in PERIODS else PERIODS["final"]
    if stage == "discovery":
        E, tab, out = stage_report(stage, B, ev_all)
        reg, nreg = regression(B, lo, hi)
        testable = tab[tab.N >= 40].copy()
        testable["keep_fdr"] = bh(testable.p.to_numpy(), 0.10) if len(testable) else []
        cand = testable[(testable.mean_netR >= 0.10) & testable.keep_fdr & (testable.mean_netR > 0)]
        out += ["\n## 6A.1 Bog'liqlik regressiyasi (y = 12 soatlik keyingi harakat / ATR_H1, HAC 24)\n", f"N = {nreg}\n", fmt(reg) + "\n"]
        for title, d in descriptive(E, B):
            out += [f"\n## 6A. {title}\n", fmt(d) + "\n"]
        out += ["\n## 6B. 32 ta asosiy test (Discovery)\n", fmt(tab, index=False) + "\n",
                f"\nSinalgan (N≥40): {len(testable)} ta; BH-FDR (q=0.10) dan o'tgan va o'rtacha net R ≥ +0.10: **{len(cand)}** ta.\n"]
        Path("reports/mtf_candidates_discovery.json").write_text(json.dumps(cand.to_dict("records"), indent=1))
        Path("reports/mtf_discovery.md").write_text("\n".join(out))
        print("\n".join(out))


def validation_descriptive():
    """Stage 2 with an empty candidate list: only replicate the descriptive findings (6A); the 32-cell table is deliberately NOT shown."""
    B = load_gold_B()
    ev_all = pd.read_parquet("/tmp/claude-0/mtf_events.parquet")
    lo, hi = PERIODS["validation"]
    E = ev_all[(ev_all.t >= pd.Timestamp(lo)) & (ev_all.t <= pd.Timestamp(hi) + pd.Timedelta(days=1))]
    out = [f"# MTF tadqiqot: validation ({lo} … {hi}), faqat tavsifiy takrorlash\n",
           f"Discovery'da nomzod qoida chiqmadi (reports/mtf_candidates_discovery.json = []), shuning uchun Validation'da qoida sinalmaydi. "
           f"Faqat tavsifiy topilmalar takrorlanadi (6A). Hodisalar: F1 {int((E.fam=='F1').sum())}, F2 {int((E.fam=='F2').sum())}.\n"]
    reg, nreg = regression(B, lo, hi)
    out += ["\n## 6A.1 Bog'liqlik regressiyasi (Validation)\n", f"N = {nreg}\n", fmt(reg) + "\n"]
    for title, d in descriptive(E, B):
        out += [f"\n## 6A. {title}\n", fmt(d) + "\n"]
    Path("reports/mtf_validation.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validation":
        validation_descriptive()
    else:
        main()
