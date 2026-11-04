"""News straddle with big TP, fixed $10 risk per event, $100 -> $1000 or bust (STRATEGY_STRADDLE_10X.md). Nothing is tuned.

Usage: python -m backtest.straddle10x      -> reports/straddle10x_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.ldn import load
from backtest.news5x import build, events
from backtest.straddle import run_events

START, TARGET, FLOOR = 100.0, 1000.0, 10.0


def dollars(d, risk, sl=3.0, slip=0.5, spread=0.80):
    oz = risk / (sl + slip + spread)
    return (d.pnl * oz).to_numpy()


@njit(cache=True)
def walk(x, s, start, target, floor):
    bal = start
    for i in range(s, len(x)):
        bal += x[i]
        if bal >= target:
            return 1, i - s + 1, bal
        if bal < floor:
            return 2, i - s + 1, bal
    return 0, len(x) - s, bal


@njit(cache=True)
def mc(x, n_paths, n_ev, start, target, floor, seed):
    np.random.seed(seed)
    res = np.zeros(3)
    for _ in range(n_paths):
        bal = start
        code = 0
        for i in range(n_ev):
            bal += x[np.random.randint(0, len(x))]
            if bal >= target:
                code = 1; break
            if bal < floor:
                code = 2; break
        res[code] += 1
    return res / n_paths


def analyze(x, risk):
    hist = np.array([walk(x, s, START, TARGET, FLOOR) for s in range(len(x))])
    codes = hist[:, 0]
    succ, sliv, none = [(codes == k).mean() * 100 for k in (1, 2, 0)]
    med_s = float(np.median(hist[codes == 2, 1])) if (codes == 2).any() else np.nan
    mc_res = mc(x, 20000, len(x), START, TARGET, FLOOR, 7) * 100
    fair = 100 * (START - FLOOR) / ((TARGET - START) + (START - FLOOR))
    return dict(risk_usd=risk, tarixiy_yetdi_pct=round(succ, 1), tarixiy_sliv_pct=round(sliv, 1), tarixiy_ikkalasi_emas_pct=round(none, 1), median_sliv_hodisa=med_s,
                mc_yetdi_pct=round(mc_res[1], 2), mc_sliv_pct=round(mc_res[2], 1), mc_ikkalasi_emas_pct=round(mc_res[0], 1), mean_event_usd=round(float(x.mean()), 3), fair_pct=round(fair, 1))


def main():
    m1 = load()
    arrs = tuple(m1[c].to_numpy(float) for c in ("open", "high", "low", "close"))
    E = build(m1, events())
    E = E[(E.t >= "2018-01-02") & (E.t < "2025-03-01")]
    rows = []
    base_kw = dict(pt=15.0, hold=30)
    d0 = run_events(arrs, E, **base_kw)
    rows.append({"variant": "asosiy (TP $15, 30 daq, risk $10)", **analyze(dollars(d0, 10.0), 10.0)})
    for name, kw, risk in [("stress (spred 1.50, sirpanish 1.00)", dict(pt=15.0, hold=30, spread=1.5, slip=1.0), 10.0), ("TP $9", dict(pt=9.0, hold=30), 10.0), ("TP $30", dict(pt=30.0, hold=30), 10.0),
                           ("TP $60", dict(pt=60.0, hold=30), 10.0), ("ushlash 10 daq", dict(pt=15.0, hold=10), 10.0), ("ushlash 60 daq", dict(pt=15.0, hold=60), 10.0),
                           ("risk $5", dict(pt=15.0, hold=30), 5.0), ("risk $20", dict(pt=15.0, hold=30), 20.0)]:
        d = run_events(arrs, E, **kw)
        sp = kw.get("spread", 0.80); sl_ = kw.get("slip", 0.50)
        rows.append({"variant": name, **analyze(dollars(d, risk, slip=sl_, spread=sp), risk)})
    ev = d0
    out = ["# Straddle, katta TP, $10 risk, $100 → $1000 yoki sliv: natijalar (STRATEGY_STRADDLE_10X.md)\n",
           f"Hodisalar: {len(E)} (2018-01 → 2025-02). Orderlar ±$2.50, stop $3.00, spred $0.80, sirpanish $0.50. Muvaffaqiyat: balans ≥ $1,000; sliv: balans < $10 (keyingi $10 riskni ko'tara olmaydi).\n",
           f"Asosiy: to'lgan {100*(ev.code==1).mean():.1f}%, whipsaw {100*(ev.code==2).mean():.1f}%, yutuq {100*(ev.pnl>0).mean():.1f}%, o'rtacha sof natija {ev.pnl.mean():.3f} $/oz.\n",
           pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    x = dollars(d0, 10.0)
    big = np.sort(x)[::-1][:5]
    out.append(f"Eng katta 5 ta foydali hodisa ($, $10 risk bilan): {', '.join(f'{v:.0f}' for v in big)}; eng katta zarar ${x.min():.1f}. Yig'indi (293 hodisa): ${x.sum():.0f}.\n")
    open("reports/straddle10x_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
