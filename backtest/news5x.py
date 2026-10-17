"""News full-margin 5x gold test (STRATEGY_NEWS_FULLMARGIN_5X.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.news5x      -> reports/news5x_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.ldn import load

CAL = "/tmp/claude-0/cal/ff.csv"
STD = {"Non-Farm Employment Change": "08:30", "CPI m/m": "08:30", "Core CPI m/m": "08:30", "CPI y/y": "08:30", "Advance GDP q/q": "08:30", "Prelim GDP q/q": "08:30",
       "Second Estimate GDP q/q": "08:30", "Final GDP q/q": "08:30", "FOMC Statement": "14:00", "Federal Funds Rate": "14:00"}
SPREAD, STOPOUT = 0.80, 0.5


def events():
    d = pd.read_csv(CAL, usecols=["DateTime", "Currency", "Impact", "Event"])
    d = d[(d.Currency == "USD") & (d.Impact == "High Impact Expected") & d.Event.isin(STD)]
    ts = sorted({pd.Timestamp(f"{r.DateTime[:10]} {STD[r.Event]}", tz="America/New_York").tz_convert("UTC").tz_localize(None) for r in d.itertuples()})
    return pd.DatetimeIndex(ts)


@njit(cache=True)
def sim(o, h, l, c, i0, i1, dr, lev, spread, target, floor):
    """Entry at close[i0]; run bars i0+1..i1 (inclusive). Returns (code, end_equity, minutes)."""
    ent = c[i0]
    size = lev / ent               # E0 = 1, margin = size*ent/lev = 1
    for b in range(i0 + 1, i1 + 1):
        pts = np.empty(4)
        pts[0] = o[b]
        pts[1] = h[b] if dr == -1 else l[b]
        pts[2] = l[b] if dr == -1 else h[b]
        pts[3] = c[b]
        for q in range(4):
            p = pts[q]
            eq = 1.0 + dr * size * (p - ent) - spread * size
            marg = size * p / lev
            if q != 2 and (eq <= floor or eq / marg <= STOPOUT):
                return 2, max(eq, 0.0), float(b - i0)
            if eq >= target:
                return 1, eq, float(b - i0)
    p = c[i1]
    eq = 1.0 + dr * size * (p - ent) - spread * size
    return 0, max(eq, 0.0), float(i1 - i0)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    r = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - r, c + r


def build(m1, ev):
    idx = m1.index.to_numpy()
    def bar(ts):
        k = np.searchsorted(idx, np.datetime64(ts))
        return k if k < len(idx) and idx[k] == np.datetime64(ts) else -1
    rows = []
    for t in ev:
        b = {m: bar(t + pd.Timedelta(minutes=m)) for m in (-61, -31, -1, 1, 30)}
        if min(b.values()) < 0:
            continue
        rows.append(dict(t=t, b61=b[-61], b31=b[-31], b0=b[-1], b1=b[1], b30=b[30]))
    return pd.DataFrame(rows)


def summarize(r):
    n = len(r)
    s, f = int((r.code == 1).sum()), int((r.code == 2).sum())
    lo, hi = wilson(s, n)
    m = lambda x: round(float(x.mean()), 1) if len(x) else np.nan
    return dict(oynalar=n, yetdi=s, yetdi_pct=round(100 * s / n, 1), wilson95=f"{100*lo:.1f}–{100*hi:.1f}", sliv=f, sliv_pct=round(100 * f / n, 1), hech=n - s - f,
                min_yetdi=m(r[r.code == 1]["min"]), min_sliv=m(r[r.code == 2]["min"]), mean_end=round(float(r.end.mean()), 3), best=round(float(r.end.max()), 2), worst=round(float(r.end.min()), 2))


def run(m1, arrs, E, mode="pre60", lev=500.0, spread=SPREAD, force_dir=None):
    o, h, l, c = arrs
    out = []
    for r in E.itertuples():
        if mode == "pre60":
            i0, d = r.b0, np.sign(c[r.b0] - c[r.b61])
        elif mode == "pre30":
            i0, d = r.b0, np.sign(c[r.b0] - c[r.b31])
        else:   # impulse: enter at t+2 minutes in direction of the first 2-minute reaction
            i0, d = r.b1, np.sign(c[r.b1] - c[r.b0])
        if force_dir is not None:
            d = force_dir
        if d == 0:
            continue
        code, eq, mins = sim(o, h, l, c, i0, r.b30, int(d), lev, spread, 5.0, 0.10)
        out.append((r.t, int(d), code, eq, mins))
    return pd.DataFrame(out, columns=["t", "dir", "code", "end", "min"])


def main():
    m1 = load()
    arrs = tuple(m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    E = build(m1, events())
    out = ["# Yangilik + full margin 5x (oltin): natijalar (STRATEGY_NEWS_FULLMARGIN_5X.md)\n", f"AQSh yuqori ta'sirli yangilik oynalari (M1 to'liq): {len(E)} (2018-01 … 2025-02). Spred $0.80, leverage 1:500, 30 daqiqa.\n"]
    base = run(m1, arrs, E)
    rows = [{"variant": "asosiy (60 min trend, kirish t)", **summarize(base)}]
    for name, kw in [("30 min trend", dict(mode="pre30")), ("birinchi impuls (kirish t+2)", dict(mode="imp")), ("spred $0.30", dict(spread=0.30)), ("leverage 1:200", dict(lev=200.0)), ("leverage 1:1000", dict(lev=1000.0))]:
        rows.append({"variant": name, **summarize(run(m1, arrs, E, **kw))})
    bu, se = run(m1, arrs, E, force_dir=1), run(m1, arrs, E, force_dir=-1)
    rows += [{"variant": "har doim Buy", **summarize(bu)}, {"variant": "har doim Sell", **summarize(se)}]
    out.append("## Hamma yangilik oynalari\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
    # random-direction control (per-event direction chosen at random), using matched events (non-zero trend)
    mb, ms = bu.set_index("t"), se.set_index("t")
    common = mb.index.intersection(ms.index)
    rng = np.random.default_rng(1)
    pick = rng.integers(0, 2, size=(1000, len(common)))
    eb, es = mb.loc[common].end.to_numpy(), ms.loc[common].end.to_numpy()
    cb, cs = (mb.loc[common].code == 1).to_numpy(), (ms.loc[common].code == 1).to_numpy()
    ends = np.where(pick == 1, eb, es).mean(axis=1)
    succ = np.where(pick == 1, cb, cs).mean(axis=1) * 100
    bm = base.set_index("t").loc[base.set_index("t").index.intersection(common)]
    p_end = float((ends >= bm.end.mean()).mean())
    p_succ = float((succ >= 100 * (bm.code == 1).mean()).mean())
    out.append(f"## Tasodifiy yo'nalish nazorati (1000)\nReal (asosiy) o'rtacha yakuniy balans {bm.end.mean():.3f}; tasodifiy {ends.mean():.3f} (5–95%: {np.percentile(ends,5):.3f} … {np.percentile(ends,95):.3f}); p = {p_end:.3f}. "
               f"5x ulushi: real {100*(bm.code==1).mean():.1f}%, tasodifiy {succ.mean():.1f}%; p = {p_succ:.3f}.\n")
    yr = base.assign(y=base.t.dt.year).groupby("y").apply(lambda g: pd.Series(dict(n=len(g), yetdi=int((g.code == 1).sum()), sliv=int((g.code == 2).sum()), hech=int((g.code == 0).sum()), mean_end=round(float(g.end.mean()), 3))), include_groups=False)
    out.append("## Yillar bo'yicha (asosiy)\n" + yr.to_markdown() + "\n")
    verdict = "USTUNLIK YO'Q" if not (base.end.mean() > 1.0 and p_end <= 0.10) else "USTUNLIK BELGISI (dastlabki)"
    out.append(f"## Qaror\n(a) o'rtacha yakuniy balans > 1.00: {'ha' if base.end.mean() > 1 else 'yo`q'}; (b) tasodifiy nazorat p ≤ 0.10: {'ha' if p_end <= 0.10 else 'yo`q'}. **{verdict}**\n")
    open("reports/news5x_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
