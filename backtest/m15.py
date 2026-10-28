"""Daily/H4 bias + M15 breakout cost-aware rule (STRATEGY_M15.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.m15      -> reports/m15_results.md
"""
import glob

import numpy as np
import pandas as pd
from numba import njit

from backtest.h4 import clustered, equity, news_windows, row
from backtest.ldn import ema, load

DEC = ("2019-01-01", "2025-03-01")
HALF = {"2019-21": ("2019-01-01", "2022-01-01"), "2022-25": ("2022-01-01", "2025-03-01")}
P = dict(minmult=8.0, tp=2.0, risk=0.005, side=0, news=1, sess="both", stressmult=1.0)


class Data:
    def __init__(self, m1, spread, stress_spread, block_news=True):
        self.spread, self.stress = spread, stress_spread
        agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
        m15 = m1.resample("15min").agg(agg).dropna()
        h1 = m1.resample("1h").agg(agg).dropna()
        h4 = m1.resample("4h").agg(agg).dropna()
        dly = m1.resample("1D").agg(agg).dropna()
        self.t = m15.index
        self.o, self.h, self.l, self.c = (m15[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        close_t = (self.t + pd.Timedelta("15min")).to_numpy()
        # H1 ATR
        pc = h1.close.shift()
        tr = pd.concat([h1.high - h1.low, (h1.high - pc).abs(), (h1.low - pc).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().to_numpy()
        k = np.searchsorted((h1.index + pd.Timedelta("1h")).to_numpy(), close_t, side="right") - 1
        self.atr = np.where(k >= 14, atr[np.maximum(k, 0)], np.nan)
        # Daily bias
        d50, d200 = ema(dly.close, 50), ema(dly.close, 200)
        dbias = np.where((dly.close > d50) & (dly.close > d200) & (d50 > d200), 1, np.where((dly.close < d50) & (dly.close < d200) & (d50 < d200), -1, 0))
        drel = np.sign(d50 - d200).to_numpy()
        kd = np.searchsorted((dly.index + pd.Timedelta("1D")).to_numpy(), close_t, side="right") - 1
        okd = kd >= 200
        dbias = np.where(okd, dbias[np.maximum(kd, 0)], 0)
        self.rel = np.where(okd, drel[np.maximum(kd, 0)], 0)
        # H4 EMA20/50
        e20, e50 = ema(h4.close, 20), ema(h4.close, 50)
        h4b = np.sign(e20 - e50).to_numpy()
        k4 = np.searchsorted((h4.index + pd.Timedelta("4h")).to_numpy(), close_t, side="right") - 1
        h4b = np.where(k4 >= 50, h4b[np.maximum(k4, 0)], 0)
        self.bias = np.where(dbias == h4b, dbias, 0).astype(np.int64)
        self.U = pd.Series(self.h).rolling(16).max().shift(1).to_numpy()
        self.L = pd.Series(self.l).rolling(16).min().shift(1).to_numpy()
        self.mod = (self.t.hour * 60 + self.t.minute).to_numpy()
        self.dow = self.t.dayofweek.to_numpy()
        self.dayid = pd.factorize(self.t.normalize())[0].astype(np.int64)
        tv = self.t.to_numpy()
        self.tns = tv.astype("datetime64[ns]").astype(np.int64)
        self.contig = np.r_[False, np.diff(tv) == np.timedelta64(15, "m")]
        blocked = np.zeros(len(tv), bool)
        if block_news:
            for a, b in news_windows():
                blocked[np.searchsorted(tv, np.datetime64(a), side="left"):np.searchsorted(tv, np.datetime64(b), side="right")] = True
        self.blocked = blocked


@njit(cache=True)
def trade(e, dr, s, tpm, o, h, l, c, rel, contig, cost):
    n = len(o)
    ent = o[e]
    stop = ent - dr * s
    tp = ent + dr * tpm * s
    rel0 = rel[e - 1]
    flag = False
    last = min(e + 47, n - 1)
    x = c[last]
    xb = last
    for b in range(e, last + 1):
        if b > e and (flag or not contig[b]):
            x = o[b]; xb = b; break
        if dr == 1:
            if o[b] <= stop:
                x = o[b]; xb = b; break
            if l[b] <= stop:
                x = stop; xb = b; break
            if h[b] >= tp:
                x = tp; xb = b; break
        else:
            if o[b] >= stop:
                x = o[b]; xb = b; break
            if h[b] >= stop:
                x = stop; xb = b; break
            if l[b] <= tp:
                x = tp; xb = b; break
        if rel[b] != rel0 and rel[b] != 0:
            flag = True
    return ((x - ent) * dr - cost) / s, xb


@njit(cache=True)
def run_signals(o, h, l, c, U, L, atr, bias, rel, tns, dayid, dow, mod, contig, blocked, cost, minatr, tpm, news, side, s0, s1):
    n = len(o)
    ti = np.empty(n, np.int64); td = np.empty(n, np.int64); tr = np.empty(n); tx = np.empty(n, np.int64); ts = np.empty(n)
    nt = 0
    cd_until = -1
    losses = 0
    cur_day = -1
    cnt = 0
    j = 300
    while j < n - 2:
        e = j + 1
        if dayid[e] != cur_day:
            cur_day = dayid[e]; cnt = 0
        m = mod[e]
        if m < s0 or m >= s1 or dow[e] > 4 or (not contig[e]) or (news == 1 and blocked[e]) or bias[j] == 0 or cnt >= 2 or tns[e] < cd_until or atr[j] != atr[j] or atr[j] < minatr or U[j] != U[j]:
            j += 1
            continue
        d = 0
        if bias[j] == 1 and c[j] > U[j]:
            d = 1
        elif bias[j] == -1 and c[j] < L[j]:
            d = -1
        if d == 0 or (side != 0 and d != side):
            j += 1
            continue
        r, xb = trade(e, d, atr[j], tpm, o, h, l, c, rel, contig, cost)
        ti[nt] = e; td[nt] = d; tr[nt] = r; tx[nt] = xb; ts[nt] = atr[j]; nt += 1
        cnt += 1
        if r < 0:
            losses += 1
            if losses >= 3:
                cd_until = tns[xb] + 24 * 3600 * 10 ** 9 + 15 * 60 * 10 ** 9
                losses = 0
        else:
            losses = 0
        j = xb
    return ti[:nt], td[:nt], tr[:nt], tx[:nt], ts[:nt]


@njit(cache=True)
def rand_ctrl(elig, N, o, h, l, c, atr, bias, rel, contig, cost, tpm, draws, seed):
    np.random.seed(seed)
    idx = np.where(elig)[0]
    out = np.empty(draws)
    for it in range(draws):
        tot = 0.0
        for _ in range(N):
            j = idx[np.random.randint(0, len(idx))]
            r, _x = trade(j + 1, bias[j], atr[j], tpm, o, h, l, c, rel, contig, cost)
            tot += r
        out[it] = tot / N
    return out


def run(D, stress=False, **kw):
    p = {**P, **kw}
    cost = D.stress if stress else D.spread
    s0, s1 = {"both": (420, 960), "london": (420, 660), "overlap": (720, 960)}[p["sess"]]
    ti, td, tr, tx, ts = run_signals(D.o, D.h, D.l, D.c, D.U, D.L, D.atr, D.bias, D.rel, D.tns, D.dayid, D.dow, D.mod, D.contig, D.blocked, cost, p["minmult"] * D.spread, p["tp"], p["news"], p["side"], s0, s1)
    df = pd.DataFrame({"i": ti, "dir": td, "R": tr, "x": tx, "s": ts})
    df["t"] = D.t[df.i.to_numpy()]
    df["date"] = df.t.dt.normalize()
    df["cost_R"] = cost / df.s
    df["hold_d"] = (D.tns[df.x.to_numpy()] - D.tns[df.i.to_numpy()]) / 86400e9
    return df


def sl(df, per):
    return df[(df.date >= pd.Timestamp(per[0])) & (df.date < pd.Timestamp(per[1]))]


def load_fx(pair):
    fs = sorted(glob.glob(f"/tmp/claude-0/fx_m1/{pair}/*.parquet"))
    d = pd.concat([pd.read_parquet(f) for f in fs])
    d.columns = [c.lower() for c in d.columns]
    d.index = pd.to_datetime(d.index)
    return d[["open", "high", "low", "close"]].sort_index()


def main():
    G = Data(load(), 0.30, 0.50)
    tr = run(G)
    dec = sl(tr, DEC)
    rows = [{"davr": k, **row(sl(tr, v), P["risk"]), "cost_R": round(float(sl(tr, v).cost_R.mean()), 3)} for k, v in {"Qaror 2019-25": DEC, **HALF}.items()]
    out = ["# Daily/H4 bias + M15 breakout (oltin): natijalar (STRATEGY_M15.md)\n", "## Oltin, asosiy qoida (spred $0.30, risk 0.5%)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    rs = row(sl(run(G, stress=True), DEC), P["risk"])
    out.append(f"## Stress ($0.50), qaror davri: meanR {rs['meanR']}, p {rs['p_one']}, maxDD {rs['maxDD_pct']}%\n")
    elig = (G.bias != 0) & ~G.blocked & (G.mod >= 420) & (G.mod < 960) & (G.dow <= 4) & G.contig & (G.atr >= P["minmult"] * G.spread) & (G.t >= pd.Timestamp(DEC[0])) & (G.t < pd.Timestamp(DEC[1]))
    elig[:300] = False
    elig[-60:] = False
    ctrl = rand_ctrl(elig, len(dec), G.o, G.h, G.l, G.c, np.nan_to_num(G.atr), G.bias, G.rel, G.contig, G.spread, P["tp"], 1000, 3)
    pc = float((ctrl >= dec.R.mean()).mean())
    out.append(f"## Tasodifiy kirish nazorati (1000): real meanR {dec.R.mean():.4f}; tasodifiy o'rtacha {ctrl.mean():.4f} (5–95%: {np.percentile(ctrl,5):.4f} … {np.percentile(ctrl,95):.4f}); p = {pc:.3f}\n")
    # FX confirmation
    fx_rows, fx_all, fx_all_s = [], [], []
    for pair in ["eur_usd", "gbp_usd", "aud_usd"]:
        F = Data(load_fx(pair), 0.0001, 0.00015)
        t_ = run(F)
        ts_ = run(F, stress=True)
        fx_all.append(t_); fx_all_s.append(ts_)
        fx_rows.append({"juft": pair, **{k: row(t_, P["risk"])[k] for k in ["N", "meanR", "win_pct", "PF", "p_one"]}})
    fx = pd.concat(fx_all)
    fxs = pd.concat(fx_all_s)
    rf, rfs = row(fx, P["risk"]), row(fxs, P["risk"])
    fx_rows.append({"juft": "birlashtirilgan", **{k: rf[k] for k in ["N", "meanR", "win_pct", "PF", "p_one"]}})
    out.append("## FX tasdiqlash (spred 1.0 pip)\n" + pd.DataFrame(fx_rows).to_markdown(index=False) + f"\n\nStress (1.5 pip): meanR {rfs['meanR']}, p {rfs['p_one']}\n")
    r1, r2, dc = row(sl(tr, HALF["2019-21"]), P["risk"]), row(sl(tr, HALF["2022-25"]), P["risk"]), row(dec, P["risk"])
    crit = {"C1 oltin meanR>0, p<=0.10, N>=150": dc["meanR"] > 0 and dc["p_one"] <= 0.10 and dc["N"] >= 150,
            "C2 stress meanR>0": rs["meanR"] > 0,
            "C3 ikki yarimda meanR>0": r1["meanR"] > 0 and r2["meanR"] > 0,
            "C4 PF>=1.15": dc["PF"] >= 1.15,
            "C5 random control p<=0.10": pc <= 0.10,
            "C6 maxDD<=20%": dc["maxDD_pct"] <= 20,
            "C7 FX: meanR>0, p<=0.10, N>=300, stress>0": rf["meanR"] > 0 and rf["p_one"] <= 0.10 and rf["N"] >= 300 and rfs["meanR"] > 0}
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    sens = []
    for name, kw in [("xarajat-nisbati filtrisiz", dict(minmult=0.0)), ("filtr 5x", dict(minmult=5.0)), ("filtr 12x", dict(minmult=12.0)), ("risk 0.25%", dict(risk=0.0025)), ("risk 1%", dict(risk=0.01)),
                     ("faqat Long", dict(side=1)), ("faqat Short", dict(side=-1)), ("faqat London", dict(sess="london")), ("faqat overlap", dict(sess="overlap")), ("TP 1.5x", dict(tp=1.5)), ("TP 3x", dict(tp=3.0)),
                     ("yangilik filtrisiz", dict(news=0))]:
        x = sl(run(G, **kw), DEC)
        rr = row(x, kw.get("risk", P["risk"]))
        sens.append({"variant": name, **{k: rr[k] for k in ["N", "meanR", "win_pct", "PF", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct"]}})
    x0 = sl(run(G), DEC)
    sens.append({"variant": "xarajatsiz", **{k: v for k, v in row(sl(run(G, ), DEC).assign(R=lambda d: d.R + d.cost_R), P["risk"]).items() if k in ["N", "meanR", "win_pct", "PF", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct"]}})
    out.append("## Sezgirlik (qaror davri, faqat ma'lumot)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    yr = dec.groupby(dec.date.dt.year).R.agg(["count", "mean"]).round(4)
    out.append("## Yillar bo'yicha (oltin)\n" + yr.to_markdown() + "\n")
    open("reports/m15_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
