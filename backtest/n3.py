"""N3: gold M1 swing-trend + ATR day filter + daily +-10% limit (STRATEGY_N3.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.n3      -> reports/n3_results.md
"""
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import norm

from backtest.mtf import PARQ, tf_bars

DEC = ("2022-01-01", "2025-03-01")
PER = {"Dev 2018-21": ("2018-01-01", "2022-01-01"), "Val 2022-23": ("2022-01-01", "2024-01-01"), "Final 2024-25": ("2024-01-01", "2025-03-01"), "Qaror 2022-25": DEC}
BASE = dict(k=5, risk=0.01, tp=1.5, hold=60, cost=0.30, gate=True, smin=0.15, smax=1.0, max_trades=20, limit=0.10, side=0)


def load():
    m1 = pd.read_parquet(PARQ)
    m1 = m1[(m1.index >= "2018-01-01") & (m1.index < "2025-03-01")]
    m1.index = m1.index.tz_localize(None)
    return m1


@njit(cache=True)
def swings(h, l, k):
    n = len(h)
    sh1 = np.full(n, np.nan); sh2 = np.full(n, np.nan); sl1 = np.full(n, np.nan); sl2 = np.full(n, np.nan)
    a1 = a2 = b1 = b2 = np.nan
    for j in range(n):
        i = j - k
        if i >= k:
            ok = True
            for q in range(1, k + 1):
                if not (h[i] > h[i - q] and h[i] > h[i + q]):
                    ok = False
                    break
            if ok:
                a2 = a1; a1 = h[i]
            ok = True
            for q in range(1, k + 1):
                if not (l[i] < l[i - q] and l[i] < l[i + q]):
                    ok = False
                    break
            if ok:
                b2 = b1; b1 = l[i]
        sh1[j] = a1; sh2[j] = a2; sl1[j] = b1; sl2[j] = b2
    return sh1, sh2, sl1, sl2


@njit(cache=True)
def sim(o, h, l, c, sh1, sh2, sl1, sl2, ds, de, Aok, A, risk, tp, hold, cost, smin, smax, max_trades, limit, side):
    nd = len(ds)
    cap = nd * max_trades
    t_idx = np.empty(cap, np.int64); t_dir = np.empty(cap, np.int64); t_s = np.empty(cap); t_r = np.empty(cap); t_day = np.empty(cap, np.int64); t_ex = np.empty(cap, np.int64)
    day_pnl = np.zeros(nd)
    nt = 0
    for d in range(nd):
        if not Aok[d]:
            continue
        realized = 0.0
        ntd = 0
        j = ds[d]
        while j < de[d] - 1 and ntd < max_trades:
            direction = 0
            if not np.isnan(sh2[j]) and not np.isnan(sl2[j]):
                if sh1[j] > sh2[j] and sl1[j] > sl2[j] and c[j] > sh1[j]:
                    direction = 1
                elif sh1[j] < sh2[j] and sl1[j] < sl2[j] and c[j] < sl1[j]:
                    direction = -1
            if direction == 0 or (side != 0 and direction != side):
                j += 1
                continue
            e = o[j + 1]
            stop0 = sl1[j] if direction == 1 else sh1[j]
            s = (e - stop0) * direction
            if s < smin * A[d] or s > smax * A[d]:
                j += 1
                continue
            tpR = min(tp, (limit - realized) / risk)
            slR = min(1.0, (limit + realized) / risk)
            if tpR <= 0 or slR <= 0:
                break
            stop = e - direction * slR * s
            target = e + direction * tpR * s
            lastb = min(j + hold, de[d] - 1)
            xb = lastb
            x = c[lastb]
            for b in range(j + 1, lastb + 1):
                if direction == 1:
                    if b > j + 1 and o[b] <= stop:
                        x = o[b]; xb = b; break
                    if l[b] <= stop:
                        x = stop; xb = b; break
                    if h[b] >= target:
                        x = target; xb = b; break
                else:
                    if b > j + 1 and o[b] >= stop:
                        x = o[b]; xb = b; break
                    if h[b] >= stop:
                        x = stop; xb = b; break
                    if l[b] <= target:
                        x = target; xb = b; break
            r = ((x - e) * direction - cost) / s
            realized += risk * r
            day_pnl[d] += risk * r
            t_idx[nt] = j + 1; t_dir[nt] = direction; t_s[nt] = s; t_r[nt] = r; t_day[nt] = d; t_ex[nt] = xb
            nt += 1; ntd += 1
            j = xb
            if realized >= limit - 1e-9 or realized <= -limit + 1e-9:
                break
    return t_idx[:nt], t_dir[:nt], t_s[:nt], t_r[:nt], t_day[:nt], t_ex[:nt], day_pnl


@njit(cache=True)
def rand_ctrl(o, h, l, c, ds, de, cnt, pool, tp, hold, cost, draws, seed, lo_day):
    np.random.seed(seed)
    out = np.empty(draws)
    for it in range(draws):
        tot = 0.0; n = 0
        for d in range(lo_day, len(ds)):
            for _ in range(cnt[d]):
                j = np.random.randint(ds[d], de[d] - 2)
                direction = 1 if np.random.random() < 0.5 else -1
                s = pool[np.random.randint(0, len(pool))]
                e = o[j + 1]
                stop = e - direction * s
                target = e + direction * tp * s
                lastb = min(j + hold, de[d] - 1)
                x = c[lastb]
                for b in range(j + 1, lastb + 1):
                    if direction == 1:
                        if b > j + 1 and o[b] <= stop:
                            x = o[b]; break
                        if l[b] <= stop:
                            x = stop; break
                        if h[b] >= target:
                            x = target; break
                    else:
                        if b > j + 1 and o[b] >= stop:
                            x = o[b]; break
                        if h[b] >= stop:
                            x = stop; break
                        if l[b] <= target:
                            x = target; break
                tot += ((x - e) * direction - cost) / s
                n += 1
        out[it] = tot / max(n, 1)
    return out


class Data:
    def __init__(self):
        m1 = load()
        self.m1 = m1
        self.o, self.h, self.l, self.c = (m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        t = m1.index
        mod = t.hour * 60 + t.minute
        ok = (mod >= 420) & (mod < 1200) & (t.dayofweek < 5)
        date = t.normalize()
        df = pd.DataFrame({"i": np.arange(len(t)), "date": date})[ok]
        g = df.groupby("date").i.agg(["min", "max", "count"])
        g = g[g["count"] >= 60]
        self.days = g.index
        self.ds = g["min"].to_numpy(np.int64)
        self.de = (g["max"].to_numpy() + 1).astype(np.int64)
        h1 = tf_bars(m1, "1h")
        A = []
        for d in self.days:
            k = np.searchsorted(h1["end"].to_numpy(), np.datetime64(d + pd.Timedelta(hours=7)), side="right") - 1
            A.append(h1["atr"].iloc[k] if k >= 0 else np.nan)
        self.A = np.array(A)
        med = pd.Series(self.A).shift(1).rolling(60).median().to_numpy()
        self.gate = (self.A >= med) & ~np.isnan(med)
        self.sw = {}

    def swings(self, k):
        if k not in self.sw:
            self.sw[k] = swings(self.h, self.l, k)
        return self.sw[k]


def run(D, **kw):
    p = {**BASE, **kw}
    sh1, sh2, sl1, sl2 = D.swings(p["k"])
    Aok = D.gate.copy() if p["gate"] else ~np.isnan(D.A)
    Aok &= ~np.isnan(D.A)
    ti, td, ts, tr, tday, tex, dpnl = sim(D.o, D.h, D.l, D.c, sh1, sh2, sl1, sl2, D.ds, D.de, Aok, np.nan_to_num(D.A), p["risk"], p["tp"], p["hold"], p["cost"], p["smin"], p["smax"], p["max_trades"], p["limit"], p["side"])
    tr_df = pd.DataFrame({"i": ti, "dir": td, "s": ts, "R": tr, "day": tday, "date": D.days[tday]})
    dd = pd.Series(dpnl, index=D.days)
    return tr_df, dd, p


def slice_(tr, dd, per):
    lo, hi = pd.Timestamp(per[0]), pd.Timestamp(per[1])
    return tr[(tr.date >= lo) & (tr.date < hi)], dd[(dd.index >= lo) & (dd.index < hi)]


def clustered(tr):
    n = len(tr)
    if n < 3:
        return np.nan, np.nan, np.nan
    m = tr.R.mean()
    cl = (tr.R - m).groupby(tr.date).sum()
    se = np.sqrt((cl ** 2).sum()) / n
    z = m / se if se > 0 else np.nan
    return m, z, float(1 - norm.cdf(z))


def equity_stats(dd, limit):
    eq = (1 + dd).cumprod()
    pk = np.maximum.accumulate(eq)
    maxdd = float(((pk - eq) / pk).max()) if len(eq) else np.nan
    mo = dd.add(1).groupby([dd.index.year, dd.index.month]).prod() - 1
    streak = cur = 0
    for v in mo:
        cur = cur + 1 if v < 0 else 0
        streak = max(streak, cur)
    return dict(ret_pct=round(100 * (eq.iloc[-1] - 1), 1) if len(eq) else np.nan, maxDD_pct=round(100 * maxdd, 1), pos_months_pct=round(100 * (mo > 0).mean(), 1),
                worst_month_pct=round(100 * mo.min(), 1), max_loss_streak_m=streak, days_hit_up=int((dd >= limit - 1e-6).sum()), days_hit_dn=int((dd <= -limit + 1e-6).sum()),
                traded_days=int((dd != 0).sum()), days=len(dd))


def row(D, tr, dd, per, limit):
    t, d = slice_(tr, dd, per)
    m, z, p = clustered(t)
    gross = t.R.sum()
    pf = t.R[t.R > 0].sum() / -t.R[t.R < 0].sum() if (t.R < 0).any() else np.nan
    lev = (0.01 * D.c[t.i.to_numpy()] / t.s.to_numpy()).max() if len(t) else np.nan
    return dict(N=len(t), meanR=round(m, 4) if len(t) else np.nan, win_pct=round(100 * (t.R > 0).mean(), 1) if len(t) else np.nan, PF=round(pf, 3), p_one=round(p, 3) if p == p else np.nan,
                maxlev=round(lev, 0) if len(t) else np.nan, **equity_stats(d, limit))


def main():
    D = Data()
    tr, dd, p = run(D)
    out = ["# N3: oltin M1 swing-trend, ATR kun filtri, kunlik ±10% (STRATEGY_N3.md)\n"]
    out.append(f"Savdoli kunlar ulushi / ATR filtri o'tkazib yuborgan kunlar: gate o'tgan {100*D.gate.mean():.1f}% kun (jami {len(D.days)} kun).\n")
    rows = [{"davr": k, **row(D, tr, dd, v, p["limit"])} for k, v in PER.items()]
    out.append("## Asosiy qoida (xarajat $0.30, risk 1%)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
    trs, dds, _ = run(D, cost=0.50)
    rs = row(D, trs, dds, DEC, p["limit"])
    out.append(f"## Stress ($0.50), qaror davri: meanR {rs['meanR']}, p {rs['p_one']}, maxDD {rs['maxDD_pct']}%\n")
    # random control
    t_dec, _ = slice_(tr, dd, DEC)
    cnt = np.zeros(len(D.days), np.int64)
    for d_, c_ in t_dec.groupby("day").size().items():
        cnt[d_] = c_
    lo_day = int(np.searchsorted(D.days.to_numpy(), np.datetime64(DEC[0])))
    ctrl = rand_ctrl(D.o, D.h, D.l, D.c, D.ds, D.de, cnt, t_dec.s.to_numpy(), p["tp"], p["hold"], p["cost"], 1000, 11, lo_day)
    p_ctrl = float((ctrl >= t_dec.R.mean()).mean())
    out.append(f"## Tasodifiy kirish nazorati (1000): real meanR {t_dec.R.mean():.4f}; tasodifiy o'rtacha {ctrl.mean():.4f} (5–95%: {np.percentile(ctrl,5):.4f} … {np.percentile(ctrl,95):.4f}); p = {p_ctrl:.3f}\n")
    # criteria
    r = {k: row(D, tr, dd, v, p["limit"]) for k, v in PER.items()}
    dec = r["Qaror 2022-25"]
    dev = r["Dev 2018-21"]
    crit = {
        "C1 meanR>0, p<=0.10, N>=200": dec["meanR"] > 0 and dec["p_one"] <= 0.10 and dec["N"] >= 200,
        "C2 stress meanR>0": rs["meanR"] > 0,
        "C3 Val va Final alohida meanR>0": r["Val 2022-23"]["meanR"] > 0 and r["Final 2024-25"]["meanR"] > 0,
        "C4 Dev ishonchli manfiy emas": not (dev["meanR"] < 0 and (1 - dev["p_one"]) <= 0.10),
        "C5 random control p<=0.10": p_ctrl <= 0.10,
        "C6 maxDD<=30% (qaror)": dec["maxDD_pct"] <= 30,
    }
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    # sensitivities (descriptive)
    sens = []
    for name, kw in [("ATR filtrisiz", dict(gate=False)), ("risk 0.5%", dict(risk=0.005)), ("risk 2%", dict(risk=0.02)), ("TP 1.0R", dict(tp=1.0)), ("TP 2.0R", dict(tp=2.0)),
                     ("fractal k=3", dict(k=3)), ("fractal k=8", dict(k=8)), ("faqat long", dict(side=1)), ("faqat short", dict(side=-1)), ("kunlik chegarasiz", dict(limit=10.0, max_trades=200))]:
        t_, d_, p_ = run(D, **kw)
        x = row(D, t_, d_, DEC, p_["limit"])
        sens.append({"variant": name, **{k: x[k] for k in ["N", "meanR", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct", "days_hit_up", "days_hit_dn"]}})
    out.append("## Sezgirlik (qaror davri, faqat ma'lumot)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    yr = t_dec.groupby(t_dec.date.dt.year).R.agg(["count", "mean"]).round(4)
    out.append("## Yillar bo'yicha (qaror davri)\n" + yr.to_markdown() + "\n")
    open("reports/n3_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
