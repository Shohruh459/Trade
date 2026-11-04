"""News straddle (OCO stop orders) on gold (STRATEGY_STRADDLE.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.straddle      -> reports/straddle_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.ldn import load
from backtest.news5x import build, events

LEV = 500.0
BASE = dict(dist=2.5, sl=3.0, pt=5.0, hold=10, expiry=3, spread=0.80, slip=0.50, use_sl=1)


@njit(cache=True)
def straddle(o, h, l, c, bref, dist, sl, pt, hold, expiry, spread, slip, use_sl):
    """bref = index of the bar starting at t-1min. Returns (code, pnl per oz, entry_ref, dir). code: 0 no fill, 1 filled, 2 whipsaw."""
    ref = c[bref]
    buy, sell = ref + dist, ref - dist
    for k in range(1, expiry + 1):
        b = bref + k
        hb, hs = h[b] >= buy, l[b] <= sell
        if hb and hs:
            return 2, -(sl + slip) - slip - spread, ref, 0
        if hb or hs:
            dr = 1 if hb else -1
            ent = (buy + slip) if dr == 1 else (sell - slip)
            sl_px = ent - dr * sl
            tp_px = ent + dr * pt
            # fill bar: close only
            cl = c[b]
            if use_sl == 1 and (cl - sl_px) * dr <= 0:
                return 1, -(sl + slip) - spread, ref, dr
            if (cl - tp_px) * dr >= 0:
                return 1, pt - spread, ref, dr
            for j in range(b + 1, b + hold + 1):
                if dr == 1:
                    if use_sl == 1 and l[j] <= sl_px:
                        x = min(o[j], sl_px) - slip
                        return 1, (x - ent) - spread, ref, dr
                    if h[j] >= tp_px:
                        x = max(o[j], tp_px)
                        return 1, (x - ent) - spread, ref, dr
                else:
                    if use_sl == 1 and h[j] >= sl_px:
                        x = max(o[j], sl_px) + slip
                        return 1, (ent - x) - spread, ref, dr
                    if l[j] <= tp_px:
                        x = min(o[j], tp_px)
                        return 1, (ent - x) - spread, ref, dr
            x = c[b + hold]
            return 1, (x - ent) * dr - spread, ref, dr
    return 0, 0.0, ref, 0


def run_events(arrs, E, **kw):
    p = {**BASE, **kw}
    o, h, l, c = arrs
    out = []
    for r in E.itertuples():
        code, pnl, ref, dr = straddle(o, h, l, c, r.b0, p["dist"], p["sl"], p["pt"], p["hold"], p["expiry"], p["spread"], p["slip"], p["use_sl"])
        out.append((r.t, code, pnl, ref))
    d = pd.DataFrame(out, columns=["t", "code", "pnl", "ref"])
    d["R"] = d.pnl / p["sl"]                      # R-multiples w.r.t. stop distance
    d["ret_F"] = np.maximum(LEV * d.pnl / d.ref, -1.0)  # full margin: fraction of equity (floored at -100%)
    d["ret_R"] = 0.02 * d.R                       # 2% risk per event
    return d


def path(ret, bal0=1.0):
    eq = bal0 * np.cumprod(1 + ret.to_numpy())
    pk = np.maximum.accumulate(np.r_[bal0, eq])[1:]
    return float(eq[-1]), float(((pk - eq) / pk).max()), bool((eq <= 0.1).any())


def random_pnls(m1, arrs, n=20000, seed=5, **kw):
    p = {**BASE, **kw}
    o, h, l, c = arrs
    t = m1.index
    mod = (t.hour * 60 + t.minute).to_numpy()
    dow = t.dayofweek.to_numpy()
    ev = events()
    tv = t.to_numpy()
    blk = np.zeros(len(t), bool)
    for e in ev:
        blk[np.searchsorted(tv, np.datetime64(e - pd.Timedelta(minutes=30))):np.searchsorted(tv, np.datetime64(e + pd.Timedelta(minutes=30)))] = True
    elig = np.where((mod >= 420) & (mod < 1200) & (dow < 5) & ~blk)[0]
    elig = elig[(elig > 1000) & (elig < len(t) - 100)]
    rng = np.random.default_rng(seed)
    pick = rng.choice(elig, size=n, replace=False)
    res = np.empty(n); refs = np.empty(n)
    for i, b in enumerate(pick):
        code, pnl, ref, dr = straddle(o, h, l, c, int(b), p["dist"], p["sl"], p["pt"], p["hold"], p["expiry"], p["spread"], p["slip"], p["use_sl"])
        res[i], refs[i] = pnl, ref
    return res / p["sl"], np.maximum(LEV * res / refs, -1.0)


def summarize(d):
    n = len(d)
    fil, wh = int((d.code == 1).sum()), int((d.code == 2).sum())
    eqR, ddR, ruinR = path(d.ret_R)
    eqF, ddF, ruinF = path(d.ret_F)
    return dict(hodisalar=n, tolgan_pct=round(100 * fil / n, 1), whipsaw_pct=round(100 * wh / n, 1), tolmagan_pct=round(100 * (n - fil - wh) / n, 1),
                yutuq_pct=round(100 * float((d.pnl > 0).mean()), 1), mean_R=round(float(d.R.mean()), 3), mean_R_pct_hisob=round(100 * float(d.ret_R.mean()), 3), mean_F_pct=round(100 * float(d.ret_F.mean()), 2),
                R_final=round(eqR, 2), R_maxdd_pct=round(100 * ddR, 1), F_final=round(eqF, 3), F_maxdd_pct=round(100 * ddF, 1), F_yoqolgan=int(ruinF))


def main():
    m1 = load()
    arrs = tuple(m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    E = build(m1, events())
    E = E[(E.t >= "2018-01-02") & (E.t < "2025-03-01")]
    base = run_events(arrs, E)
    rows = [{"variant": "asosiy", **summarize(base)}]
    sens = [("stress (spred 1.50, sirpanish 1.00)", dict(spread=1.5, slip=1.0)), ("spred 0.30, sirpanish 0.25", dict(spread=0.3, slip=0.25)), ("masofa 1.50", dict(dist=1.5)), ("masofa 4.00", dict(dist=4.0)),
            ("stop 2.00", dict(sl=2.0)), ("stop 5.00", dict(sl=5.0)), ("ushlash 5 daq", dict(hold=5)), ("ushlash 20 daq", dict(hold=20)), ("stopsiz", dict(use_sl=0)), ("maqsad 8.00", dict(pt=8.0))]
    for name, kw in sens:
        rows.append({"variant": name, **summarize(run_events(arrs, E, **kw))})
    out = ["# Yangilik straddle (oltin): natijalar (STRATEGY_STRADDLE.md)\n", f"AQSh yuqori ta'sirli yangilik hodisalari (M1 to'liq): {len(E)}, 2018-01 → 2025-02. Asosiy: masofa $2.50, stop $3.00, maqsad $5.00, ushlash 10 daq, spred $0.80, sirpanish $0.50.\n",
           "R = 2% risk/hodisa (stop masofasiga nisbatan); F = full margin (1:500). final: 1.00 dan boshlab; maxdd: butun yo'l.\n", pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    # halves
    h1, h2 = base[base.t < "2022-01-01"], base[base.t >= "2022-01-01"]
    out.append(f"## Yarmlar (asosiy): 2018–2021: n={len(h1)}, mean_R={h1.R.mean():.3f}; 2022–2025: n={len(h2)}, mean_R={h2.R.mean():.3f}\n")
    yr = base.groupby(base.t.dt.year).agg(n=("pnl", "size"), mean_R=("R", "mean"), tolgan=("code", lambda x: int((x == 1).sum())), whipsaw=("code", lambda x: int((x == 2).sum()))).round(3)
    out.append("## Yillar bo'yicha (asosiy)\n" + yr.to_markdown() + "\n")
    # random control
    rR, rF = random_pnls(m1, arrs)
    n = len(base)
    rng = np.random.default_rng(9)
    means = np.array([rng.choice(rR, size=n).mean() for _ in range(5000)])
    meansF = np.array([rng.choice(rF, size=n).mean() for _ in range(5000)])
    pR = float((means >= base.R.mean()).mean()); pF = float((meansF >= base.ret_F.mean()).mean())
    out.append(f"## Tasodifiy vaqt nazorati (20,000 tasodifiy daqiqa, yangilik bo'lmagan): tasodifiy mean_R {rR.mean():.3f} (5–95% bootstrap: {np.percentile(means,5):.3f} … {np.percentile(means,95):.3f}); real {base.R.mean():.3f}; p = {pR:.3f}. F: tasodifiy {100*rF.mean():.2f}% / hodisa, real {100*base.ret_F.mean():.2f}%; p = {pF:.3f}\n")
    s = summarize(base)
    st = [r for r in rows if r["variant"].startswith("stress")][0]
    crit = {"S1 mean>0 va tasodifiy nazorat p<=0.10": base.R.mean() > 0 and pR <= 0.10,
            "S2 stress mean>0": st["mean_R"] > 0,
            "S3 ikki yarimda mean>0": h1.R.mean() > 0 and h2.R.mean() > 0,
            "S4 maxDD<=30% va hisob yo'qolmaydi (R varianti)": s["R_maxdd_pct"] <= 30 and s["R_final"] > 0.1,
            "S5 hodisalar>=150": len(base) >= 150}
    verdict = "NOMZOD (dastlabki)" if all(crit.values()) else "O'TMADI"
    out.append("## Mezonlar (R varianti)\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    open("reports/straddle_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
