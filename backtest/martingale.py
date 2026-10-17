"""Martingale 1 -> 10 USD gold test (STRATEGY_MARTINGALE_1to10.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.martingale      -> reports/martingale_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.ldn import load

LEV, SPREAD, STOPOUT = 500.0, 0.30, 0.5


@njit(cache=True)
def sim(o, h, l, c, i0, i1, dr, lot0, step, maxpos, start_bal, target, floor):
    """dr = -1 sell, +1 buy. Returns (code, end_balance, minutes, npos). code 1 target, 2 fail, 0 window end."""
    sumL = 0.0
    sumLE = 0.0
    n = 0
    last = 0.0
    lot = lot0
    for b in range(i0, i1):
        pts = np.empty(4)
        pts[0] = o[b]
        pts[1] = h[b] if dr == -1 else l[b]
        pts[2] = l[b] if dr == -1 else h[b]
        pts[3] = c[b]
        for q in range(4):
            p = pts[q]
            if n == 0:
                fill = p
                sumL += lot; sumLE += lot * fill; n = 1; last = fill; lot = lot * 2.0
            # adds on adverse moves
            while n < maxpos and (p - last) * (-dr) >= step - 1e-12 and q in (0, 1, 3):
                trig = last - dr * step
                fill = p if q == 0 and (p - last) * (-dr) > step else trig
                if q == 3 and (p - last) * (-dr) < step:
                    break
                eq = start_bal + dr * (sumL * fill - sumLE) - SPREAD * sumL
                used = sumL * fill / LEV
                need = lot * fill / LEV
                if eq - used < need:
                    break
                sumL += lot; sumLE += lot * fill; n += 1; last = fill; lot = lot * 2.0
            fl = dr * (sumL * p - sumLE) - SPREAD * sumL
            eq = start_bal + fl
            marg = sumL * p / LEV
            if q != 2 and (eq <= floor or (marg > 0 and eq / marg <= STOPOUT)):
                return 2, max(eq, 0.0), float(b - i0), n
            if eq >= target:
                return 1, eq, float(b - i0), n
    p = c[i1 - 1]
    eq = start_bal + dr * (sumL * p - sumLE) - SPREAD * sumL
    return 0, max(eq, 0.0), float(i1 - i0), n


def windows(m1):
    dates = m1.index.normalize()
    ud = pd.Index(pd.unique(dates))
    first = np.searchsorted(dates, ud)
    wins = []
    for k in range(0, len(ud) - 4, 5):
        i0 = first[k]
        i1 = first[k + 5] if k + 5 < len(ud) else len(m1)
        wins.append((i0, i1))
    return wins


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    r = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - r, c + r


def evaluate(m1, arrs, wins, dr, lot0, step, maxpos):
    o, h, l, c = arrs
    res = [sim(o, h, l, c, i0, i1, dr, lot0, step, maxpos, 1.0, 10.0, 0.10) for i0, i1 in wins]
    r = pd.DataFrame(res, columns=["code", "end", "min", "npos"])
    r["start"] = [m1.index[i0] for i0, _ in wins]
    return r


def summarize(r):
    n = len(r)
    s = (r.code == 1).sum()
    f = (r.code == 2).sum()
    z = n - s - f
    lo, hi = wilson(s, n)
    d = lambda x: round(float(x.mean() / 1440), 2) if len(x) else np.nan
    mid = r[r.code == 0].end
    return dict(oynalar=n, yetdi_pct=round(100 * s / n, 1), wilson95=f"{100*lo:.1f}–{100*hi:.1f}", sliv_pct=round(100 * f / n, 1), hech_pct=round(100 * z / n, 1),
                kun_yetdi=d(r[r.code == 1]["min"]), kun_sliv=d(r[r.code == 2]["min"]), hech_end_avg=round(float(mid.mean()), 2) if len(mid) else np.nan,
                hech_min=round(float(mid.min()), 2) if len(mid) else np.nan, hech_max=round(float(mid.max()), 2) if len(mid) else np.nan,
                mean_end=round(float(r.end.mean()), 3), best=round(float(r.end.max()), 2), worst=round(float(r.end.min()), 2), mean_npos=round(float(r.npos.mean()), 1))


def main():
    m1 = load()
    arrs = tuple(m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    wins = windows(m1)
    out = ["# Martingale 1$ → 10$ (oltin): natijalar (STRATEGY_MARTINGALE_1to10.md)\n", f"5 savdo kunlik kesishmaydigan oynalar: {len(wins)} (2018-01 … 2025-02).\n"]
    base = dict(lot0=0.01, step=0.65, maxpos=9)
    rows = []
    for name, dr, kw in [("Sell (asosiy)", -1, {}), ("Buy", 1, {}), ("Sell, step 0.50", -1, dict(step=0.50)), ("Sell, step 0.80", -1, dict(step=0.80)), ("Sell, lot 0.1 oz", -1, dict(lot0=0.1)),
                         ("Buy, lot 0.1 oz", 1, dict(lot0=0.1)), ("Sell, 10 pog'ona", -1, dict(maxpos=10)), ("Sell, 8 pog'ona", -1, dict(maxpos=8))]:
        r = evaluate(m1, arrs, wins, dr, **{**base, **kw})
        rows.append({"variant": name, **summarize(r)})
        if name == "Sell (asosiy)":
            r0 = r
        if name == "Buy":
            r1 = r
    out.append("## Hamma oynalar\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
    for nm, r in [("Sell (asosiy)", r0), ("Buy", r1)]:
        last = r.tail(30)
        out.append(f"## Oxirgi 30 oyna, {nm}\n" + pd.DataFrame([summarize(last)]).to_markdown(index=False) + "\n")
    yr = r0.assign(y=r0.start.dt.year).groupby("y").apply(lambda g: pd.Series(dict(n=len(g), yetdi=int((g.code == 1).sum()), sliv=int((g.code == 2).sum()), mean_end=round(float(g.end.mean()), 3))), include_groups=False)
    out.append("## Yillar bo'yicha (Sell)\n" + yr.to_markdown() + "\n")
    bw = r0.loc[r0.end.idxmax()]
    ww = r0.loc[r0.end.idxmin()]
    out.append(f"Eng yaxshi oyna (Sell): boshlanishi {bw.start}, natija {bw.end:.2f}$ (kod {int(bw.code)}). Eng yomon: {ww.start}, {ww.end:.2f}$ (kod {int(ww.code)}).\n")
    open("reports/martingale_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
