"""User's Daily-bias / H4 EMA20 pullback-reclaim gold strategy (STRATEGY_H4.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.h4      -> reports/h4_results.md
"""
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import norm

from backtest.ldn import ema, load

CAL = "/tmp/claude-0/cal/ff.csv"
DEC = ("2019-01-01", "2025-03-01")
HALF = {"2019-21": ("2019-01-01", "2022-01-01"), "2022-25": ("2022-01-01", "2025-03-01")}
P = dict(cost=0.30, fin=0.03, risk=0.0075, news=1, xover=1, smax=1.8, side=0)


def news_windows():
    d = pd.read_csv(CAL, usecols=["DateTime", "Currency", "Impact", "Event"])
    d = d[(d.Currency == "USD") & (d.Impact == "High Impact Expected")]
    std = {"Non-Farm Employment Change": "08:30", "CPI m/m": "08:30", "Core CPI m/m": "08:30", "CPI y/y": "08:30", "FOMC Statement": "14:00", "Federal Funds Rate": "14:00", "FOMC Press Conference": "14:30"}
    out = []
    for r in d.itertuples():
        if r.Event in std:
            t = pd.Timestamp(f"{r.DateTime[:10]} {std[r.Event]}", tz="America/New_York").tz_convert("UTC").tz_localize(None)
            out.append((t - pd.Timedelta(minutes=60), t + pd.Timedelta(minutes=30)))
    return out


class Data:
    def __init__(self):
        m1 = load()
        agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
        h4 = m1.resample("4h").agg(agg).dropna()
        dly = m1.resample("1D").agg(agg).dropna()
        self.t = h4.index
        c = h4.close
        pc = c.shift()
        tr = pd.concat([h4.high - h4.low, (h4.high - pc).abs(), (h4.low - pc).abs()], axis=1).max(axis=1)
        self.o, self.h, self.l, self.c = (h4[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        self.e20, self.e50, self.atr = ema(c, 20).to_numpy(), ema(c, 50).to_numpy(), tr.rolling(14).mean().to_numpy()
        d50, d200 = ema(dly.close, 50), ema(dly.close, 200)
        rel = np.sign(d50 - d200).to_numpy()
        bias = np.where((dly.close > d50) & (dly.close > d200) & (d50 > d200), 1, np.where((dly.close < d50) & (dly.close < d200) & (d50 < d200), -1, 0))
        dend = (dly.index + pd.Timedelta("1D")).to_numpy()
        k = np.searchsorted(dend, (self.t + pd.Timedelta("4h")).to_numpy(), side="right") - 1
        ok = k >= 200
        self.bias = np.where(ok, bias[np.maximum(k, 0)], 0).astype(np.int64)
        self.rel = np.where(ok, rel[np.maximum(k, 0)], 0)
        self.tns = self.t.to_numpy().astype("datetime64[ns]").astype(np.int64)
        self.dayid = pd.factorize(self.t.normalize())[0].astype(np.int64)
        tv = self.t.to_numpy()
        blocked = np.zeros(len(tv), bool)
        for a, b in news_windows():
            blocked[np.searchsorted(tv, np.datetime64(a), side="left"):np.searchsorted(tv, np.datetime64(b), side="right")] = True
        self.blocked = blocked


@njit(cache=True)
def trade(e, dr, s, o, h, l, c, e20, e50, rel, tns, cost, fin, xover):
    n = len(o)
    ent = o[e]
    stop = ent - dr * s
    tp1 = ent + dr * 1.5 * s
    tp2 = ent + dr * 3.0 * s
    rem, pnl, hit1, flag = 1.0, 0.0, False, False
    rel0 = rel[e - 1]
    xb = e
    for b in range(e, n):
        xb = b
        if b > e and flag:
            pnl += rem * (o[b] - ent) * dr; rem = 0.0; break
        if dr == 1:
            if o[b] <= stop:
                pnl += rem * (o[b] - ent); rem = 0.0; break
            if l[b] <= stop:
                pnl += rem * (stop - ent); rem = 0.0; break
            if (not hit1) and h[b] >= tp1:
                pnl += 0.5 * (tp1 - ent); rem -= 0.5; hit1 = True
            if h[b] >= tp2:
                pnl += rem * (tp2 - ent); rem = 0.0; break
        else:
            if o[b] >= stop:
                pnl += rem * (ent - o[b]); rem = 0.0; break
            if h[b] >= stop:
                pnl += rem * (ent - stop); rem = 0.0; break
            if (not hit1) and l[b] <= tp1:
                pnl += 0.5 * (ent - tp1); rem -= 0.5; hit1 = True
            if l[b] <= tp2:
                pnl += rem * (ent - tp2); rem = 0.0; break
        if xover == 1 and ((dr == 1 and e20[b] < e50[b]) or (dr == -1 and e20[b] > e50[b])):
            flag = True
        if rel[b] != rel0 and rel[b] != 0:
            flag = True
    if rem > 0:
        pnl += rem * (c[xb] - ent) * dr
    ex_t = tns[xb] + 4 * 3600 * 10 ** 9 if rem == 0.0 else tns[xb] + 4 * 3600 * 10 ** 9
    days = (ex_t - tns[e]) / (86400.0 * 10 ** 9)
    return (pnl - cost - fin * ent * days / 365.0) / s, xb


@njit(cache=True)
def run_signals(o, h, l, c, e20, e50, atr, bias, rel, tns, dayid, blocked, cost, fin, xover, smax, news, side):
    n = len(o)
    ti = np.empty(n, np.int64); td = np.empty(n, np.int64); tr = np.empty(n); tx = np.empty(n, np.int64); ts = np.empty(n)
    nt = 0
    cd_until = -1
    losses = 0
    cur_day = -1
    cnt = 0
    j = 250
    while j < n - 2:
        e = j + 1
        if dayid[e] != cur_day:
            cur_day = dayid[e]; cnt = 0
        if bias[j] == 0 or cnt >= 2 or tns[e] < cd_until or (news == 1 and blocked[e]) or atr[j] != atr[j]:
            j += 1
            continue
        d = 0
        if bias[j] == 1 and e20[j] > e50[j] and c[j] > e20[j] and l[j] <= e20[j]:
            d = 1
        elif bias[j] == -1 and e20[j] < e50[j] and c[j] < e20[j] and h[j] >= e20[j]:
            d = -1
        if d == 0 or (side != 0 and d != side):
            j += 1
            continue
        if d == 1:
            stop = min(l[j], l[j - 1], l[j - 2]) - 0.5 * atr[j]
        else:
            stop = max(h[j], h[j - 1], h[j - 2]) + 0.5 * atr[j]
        s = (o[e] - stop) * d
        if s <= 0 or s > smax * atr[j]:
            j += 1
            continue
        r, xb = trade(e, d, s, o, h, l, c, e20, e50, rel, tns, cost, fin, xover)
        ti[nt] = e; td[nt] = d; tr[nt] = r; tx[nt] = xb; ts[nt] = s; nt += 1
        cnt += 1
        if r < 0:
            losses += 1
            if losses >= 3:
                cd_until = tns[xb] + 28 * 3600 * 10 ** 9
                losses = 0
        else:
            losses = 0
        j = xb
    return ti[:nt], td[:nt], tr[:nt], tx[:nt], ts[:nt]


@njit(cache=True)
def rand_ctrl(elig, N, pool, o, h, l, c, e20, e50, bias, rel, tns, cost, fin, xover, draws, seed):
    np.random.seed(seed)
    idx = np.where(elig)[0]
    out = np.empty(draws)
    for it in range(draws):
        tot = 0.0
        for _ in range(N):
            j = idx[np.random.randint(0, len(idx))]
            s = pool[np.random.randint(0, len(pool))]
            r, _x = trade(j + 1, bias[j], s, o, h, l, c, e20, e50, rel, tns, cost, fin, xover)
            tot += r
        out[it] = tot / N
    return out


def run(D, **kw):
    p = {**P, **kw}
    ti, td, tr, tx, ts = run_signals(D.o, D.h, D.l, D.c, D.e20, D.e50, D.atr, D.bias, D.rel, D.tns, D.dayid, D.blocked, p["cost"], p["fin"], p["xover"], p["smax"], p["news"], p["side"])
    df = pd.DataFrame({"i": ti, "dir": td, "R": tr, "x": tx, "s": ts})
    df["t"] = D.t[df.i.to_numpy()]
    df["date"] = df.t.dt.normalize()
    df["hold_d"] = (D.tns[df.x.to_numpy()] - D.tns[df.i.to_numpy()]) / 86400e9
    return df


def sl(df, per):
    return df[(df.date >= pd.Timestamp(per[0])) & (df.date < pd.Timestamp(per[1]))]


def clustered(x):
    n = len(x)
    if n < 3:
        return np.nan, np.nan
    m = x.R.mean()
    wk = x.t.dt.strftime("%G-%V")
    se = np.sqrt(((x.R - m).groupby(wk).sum() ** 2).sum()) / n
    return m, (float(1 - norm.cdf(m / se)) if se > 0 else np.nan)


def equity(x, risk):
    x = x.sort_values("t")
    r = x.R.to_numpy() * risk
    if len(r) == 0:
        return dict(ret_pct=np.nan, maxDD_pct=np.nan, pos_months_pct=np.nan, worst_month_pct=np.nan)
    eq = np.cumprod(1 + r)
    pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
    mo = pd.Series(r, index=pd.DatetimeIndex(x.t)).groupby([x.t.dt.year.to_numpy(), x.t.dt.month.to_numpy()]).apply(lambda s: (1 + s).prod() - 1)
    return dict(ret_pct=round(100 * (eq[-1] - 1), 1), maxDD_pct=round(100 * float(((pk - eq) / pk).max()), 1), pos_months_pct=round(float((mo > 0).mean() * 100), 1), worst_month_pct=round(100 * mo.min(), 1))


def row(x, risk=P["risk"]):
    m, p = clustered(x)
    pf = x.R[x.R > 0].sum() / -x.R[x.R < 0].sum() if (x.R < 0).any() else np.nan
    return dict(N=len(x), meanR=round(m, 4) if len(x) else np.nan, win_pct=round(100 * (x.R > 0).mean(), 1) if len(x) else np.nan, PF=round(pf, 3), p_one=round(p, 3) if p == p else np.nan,
                hold_med_d=round(float(x.hold_d.median()), 1) if len(x) else np.nan, **equity(x, risk))


def main():
    D = Data()
    tr = run(D)
    dec = sl(tr, DEC)
    rows = [{"davr": k, **row(sl(tr, v))} for k, v in {"Qaror 2019-25": DEC, **HALF}.items()]
    out = ["# Foydalanuvchi qoidasi (Daily bias + H4 EMA20 reclaim): natijalar (STRATEGY_H4.md)\n", "## Asosiy qoida (xarajat $0.30 + 3% moliyalashtirish, risk 0.75%)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    trs = run(D, cost=0.50, fin=0.05)
    rs = row(sl(trs, DEC))
    out.append(f"## Stress ($0.50, 5%), qaror davri: meanR {rs['meanR']}, p {rs['p_one']}, maxDD {rs['maxDD_pct']}%\n")
    elig = (D.bias != 0) & ~D.blocked & (D.t >= pd.Timestamp(DEC[0])) & (D.t < pd.Timestamp(DEC[1]))
    elig[:250] = False
    elig[-3:] = False
    ctrl = rand_ctrl(elig, len(dec), dec.s.to_numpy(), D.o, D.h, D.l, D.c, D.e20, D.e50, D.bias, D.rel, D.tns, P["cost"], P["fin"], P["xover"], 1000, 3)
    pc = float((ctrl >= dec.R.mean()).mean())
    out.append(f"## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR {dec.R.mean():.4f}; tasodifiy o'rtacha {ctrl.mean():.4f} (5–95%: {np.percentile(ctrl,5):.4f} … {np.percentile(ctrl,95):.4f}); p = {pc:.3f}\n")
    r1, r2 = row(sl(tr, HALF["2019-21"])), row(sl(tr, HALF["2022-25"]))
    dc = row(dec)
    crit = {"C1 meanR>0, p<=0.10, N>=60": dc["meanR"] > 0 and dc["p_one"] <= 0.10 and dc["N"] >= 60,
            "C2 stress meanR>0": rs["meanR"] > 0,
            "C3 ikki yarimda meanR>0": r1["meanR"] > 0 and r2["meanR"] > 0,
            "C4 profit factor>=1.2": dc["PF"] >= 1.2,
            "C5 random control p<=0.10": pc <= 0.10,
            "C6 maxDD<=20%": dc["maxDD_pct"] <= 20}
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    sens = []
    for name, kw in [("yangilik filtrisiz", dict(news=0)), ("risk 1%", dict(risk=0.01)), ("faqat Buy", dict(side=1)), ("faqat Sell", dict(side=-1)), ("H4 kesishuv chiqishisiz", dict(xover=0)),
                     ("stop filtri (1.8 ATR) siz", dict(smax=100.0)), ("xarajatsiz", dict(cost=0.0, fin=0.0))]:
        x = sl(run(D, **kw), DEC)
        sens.append({"variant": name, **{k: row(x, kw.get("risk", P["risk"]))[k] for k in ["N", "meanR", "win_pct", "PF", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct"]}})
    out.append("## Sezgirlik (qaror davri, faqat ma'lumot)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    yr = dec.groupby(dec.date.dt.year).R.agg(["count", "mean"]).round(4)
    out.append("## Yillar bo'yicha\n" + yr.to_markdown() + "\n")
    open("reports/h4_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
