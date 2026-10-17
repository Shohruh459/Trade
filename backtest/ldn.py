"""User's H1-bias / M5 EMA9 pullback-reclaim gold strategy (STRATEGY_LDN.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.ldn      -> reports/ldn_results.md
"""
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import norm

PARQ = "/tmp/claude-0/gold1m/XAU_M1_2018_2025.parquet"
CAL = "/tmp/claude-0/cal/ff.csv"
PER = {"Dev 2018-21": ("2018-01-01", "2022-01-01"), "Val 2022-23": ("2022-01-01", "2024-01-01"), "Final 2024-25": ("2024-01-01", "2025-03-01"), "Qaror 2022-25": ("2022-01-01", "2025-03-01")}
DEC = PER["Qaror 2022-25"]
P = dict(cost=0.30, risk=0.0075, max_trades=5, max_losses=3, slmult=1.5, tp1=1.0, tp2=2.0, rsi_lo=40, rsi_hi=70, bothside=1, win3=1, news=1, sess="both")


def load():
    m1 = pd.read_parquet(PARQ)
    m1 = m1[(m1.index >= "2018-01-01") & (m1.index < "2025-03-01")]
    m1.index = m1.index.tz_localize(None)
    return m1


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(c, n=14):
    d = c.diff()
    up, dn = d.clip(lower=0), (-d).clip(lower=0)
    au, ad = up.ewm(alpha=1 / n, adjust=False).mean(), dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + au / ad.replace(0, np.nan))


def news_windows():
    d = pd.read_csv(CAL, usecols=["DateTime", "Currency", "Impact", "Event"])
    d = d[(d.Currency == "USD") & (d.Impact == "High Impact Expected")].copy()
    out = []
    std = {"Non-Farm Employment Change": "08:30", "CPI m/m": "08:30", "Core CPI m/m": "08:30", "CPI y/y": "08:30", "FOMC Statement": "14:00", "Federal Funds Rate": "14:00", "FOMC Press Conference": "14:30"}
    for r in d.itertuples():
        if r.Event in std:
            t = pd.Timestamp(f"{r.DateTime[:10]} {std[r.Event]}", tz="America/New_York").tz_convert("UTC").tz_localize(None)
            out.append((t - pd.Timedelta(minutes=30), t + pd.Timedelta(minutes=15)))
        elif ("Speaks" in r.Event or "Testifies" in r.Event) and ("Fed Chair" in r.Event or "FOMC Member" in r.Event or "Fed Chairman" in r.Event) and r.DateTime[11:19] != "00:00:00":
            t = pd.Timestamp(r.DateTime).tz_convert("UTC").tz_localize(None)
            out.append((t - pd.Timedelta(minutes=60), t + pd.Timedelta(minutes=75)))
    return out


class Data:
    def __init__(self):
        m1 = load()
        m5 = m1.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        self.t = m5.index
        c = m5.close
        pc = c.shift()
        tr = pd.concat([m5.high - m5.low, (m5.high - pc).abs(), (m5.low - pc).abs()], axis=1).max(axis=1)
        self.o, self.h, self.l, self.c = (m5[x].to_numpy(float) for x in ("open", "high", "low", "close"))
        self.e9, self.e21, self.rsi, self.atr = ema(c, 9).to_numpy(), ema(c, 21).to_numpy(), rsi(c).to_numpy(), tr.rolling(14).mean().to_numpy()
        e50, e200 = ema(h1.close, 50), ema(h1.close, 200)
        rel = np.sign(e50 - e200)
        bias = np.where((h1.close > e50) & (h1.close > e200) & (e50 > e200), 1, np.where((h1.close < e50) & (h1.close < e200) & (e50 < e200), -1, 0))
        h1end = (h1.index + pd.Timedelta("1h")).to_numpy()
        k = np.searchsorted(h1end, (self.t + pd.Timedelta("5min")).to_numpy(), side="right") - 1
        ok = k >= 200
        self.bias = np.where(ok, bias[np.maximum(k, 0)], 0)
        self.rel = np.where(ok, rel.to_numpy()[np.maximum(k, 0)], 0)
        self.mod = (self.t.hour * 60 + self.t.minute).to_numpy()
        self.dow = self.t.dayofweek.to_numpy()
        self.day = self.t.normalize()
        self.dayid = pd.factorize(self.day)[0]
        n = len(self.t)
        blocked = np.zeros(n, bool)
        tv = self.t.to_numpy()
        for a, b in news_windows():
            i0, i1 = np.searchsorted(tv, np.datetime64(a)), np.searchsorted(tv, np.datetime64(b), side="right")
            blocked[i0:i1] = True
        self.blocked = blocked
        self.contig = np.r_[False, (np.diff(tv) == np.timedelta64(5, "m"))]   # bar j is exactly 5 min after j-1


@njit(cache=True)
def trade(e, dr, a, o, h, l, c, e9, e21, rs, rel, mod, slm, t1m, t2m, cost, contig):
    """Run one trade entered at open of bar e. Returns (netR, exit bar)."""
    n = len(o)
    ent = o[e]
    stop = ent - dr * slm * a
    tp1 = ent + dr * t1m * a
    tp2 = ent + dr * t2m * a
    rem = 1.0
    pnl = 0.0
    hit1 = False
    flag = False
    rel0 = rel[e - 1]
    xb = e
    for b in range(e, n):
        xb = b
        if b > e and (flag or mod[b] >= 1200 or not contig[b]):
            pnl += rem * (o[b] - ent) * dr
            rem = 0.0
            break
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
        if (not hit1) and ((dr == 1 and e9[b] < e21[b]) or (dr == -1 and e9[b] > e21[b])):
            flag = True
        if rel[b] != rel0 and rel[b] != 0:
            flag = True
        if (dr == 1 and rs[b] > 75) or (dr == -1 and rs[b] < 25):
            flag = True
    if rem > 0:
        pnl += rem * (c[xb] - ent) * dr
    return (pnl - cost) / (slm * a), xb


@njit(cache=True)
def run_signals(o, h, l, c, e9, e21, rs, atr, bias, rel, mod, dow, dayid, blocked, contig, cost, max_trades, max_losses, rlo, rhi, slm, t1m, t2m, win3, news, sess):
    n = len(o)
    cap = n // 20
    ti = np.empty(cap, np.int64); td = np.empty(cap, np.int64); tr = np.empty(cap); tx = np.empty(cap, np.int64)
    nt = 0
    last_up = -1
    last_dn = -1
    cur_day = -1
    cnt = 0
    losses = 0
    j = 210
    while j < n - 2:
        if dayid[j] != cur_day:
            cur_day = dayid[j]; cnt = 0; losses = 0
        k1 = j + 1
        m1 = mod[k1]
        inwin = ((m1 >= 420 and m1 < 660) or (m1 >= 720 and m1 < 960))
        if sess == 1:
            inwin = (m1 >= 420 and m1 < 660)
        elif sess == 2:
            inwin = (m1 >= 720 and m1 < 960)
        if (not inwin) or dow[k1] > 4 or (not contig[k1]) or (news == 1 and blocked[k1]) or bias[j] == 0 or cnt >= max_trades or losses >= max_losses or atr[j] != atr[j] or rs[j] != rs[j]:
            j += 1
            continue
        d = 0
        kk = -1
        lo = j - 2 if win3 == 1 else j
        if bias[j] == 1 and e9[j] > e21[j] and c[j] > e9[j] and rs[j] > rlo and rs[j] < rhi:
            for k in range(j, lo - 1, -1):
                if l[k] < e9[k] and c[k] > e9[k] and k > last_up:
                    d = 1; kk = k; break
        elif bias[j] == -1 and e9[j] < e21[j] and c[j] < e9[j] and rs[j] < 100 - rlo and rs[j] > 100 - rhi:
            for k in range(j, lo - 1, -1):
                if h[k] > e9[k] and c[k] < e9[k] and k > last_dn:
                    d = -1; kk = k; break
        if d == 0:
            j += 1
            continue
        if d == 1:
            last_up = kk
        else:
            last_dn = kk
        r, xb = trade(j + 1, d, atr[j], o, h, l, c, e9, e21, rs, rel, mod, slm, t1m, t2m, cost, contig)
        ti[nt] = j + 1; td[nt] = d; tr[nt] = r; tx[nt] = xb; nt += 1
        cnt += 1
        if r < 0:
            losses += 1
        else:
            losses = 0
        j = xb
    return ti[:nt], td[:nt], tr[:nt], tx[:nt]


@njit(cache=True)
def rand_ctrl(elig, cntday, firstbar, o, h, l, c, e9, e21, rs, atr, bias, rel, mod, contig, cost, slm, t1m, t2m, draws, seed):
    np.random.seed(seed)
    out = np.empty(draws)
    nd = len(cntday)
    for it in range(draws):
        tot = 0.0; n = 0
        for d in range(nd):
            if cntday[d] == 0:
                continue
            lo, hi = firstbar[d], firstbar[d + 1]
            m = 0
            for b in range(lo, hi):
                if elig[b]:
                    m += 1
            if m == 0:
                continue
            for _ in range(cntday[d]):
                pick = np.random.randint(0, m)
                q = 0
                for b in range(lo, hi):
                    if elig[b]:
                        if q == pick:
                            r, _x = trade(b + 1, bias[b], atr[b], o, h, l, c, e9, e21, rs, rel, mod, slm, t1m, t2m, cost, contig)
                            tot += r; n += 1
                            break
                        q += 1
        out[it] = tot / max(n, 1)
    return out


def run(D, **kw):
    p = {**P, **kw}
    sess = {"both": 0, "london": 1, "overlap": 2}[p["sess"]]
    ti, td, tr, tx = run_signals(D.o, D.h, D.l, D.c, D.e9, D.e21, D.rsi, D.atr, D.bias, D.rel, D.mod, D.dow, D.dayid, D.blocked, D.contig, p["cost"], p["max_trades"], p["max_losses"], p["rsi_lo"], p["rsi_hi"], p["slmult"], p["tp1"], p["tp2"], p["win3"], p["news"], sess)
    df = pd.DataFrame({"i": ti, "dir": td, "R": tr, "x": tx})
    df["t"] = D.t[df.i.to_numpy()]
    df["date"] = df.t.dt.normalize()
    if p.get("side"):
        df = df[df["dir"] == p["side"]]
    return df.reset_index(drop=True)


def sl(df, per):
    return df[(df.date >= pd.Timestamp(per[0])) & (df.date < pd.Timestamp(per[1]))]


def clustered(x):
    n = len(x)
    if n < 3:
        return np.nan, np.nan
    m = x.R.mean()
    se = np.sqrt(((x.R - m).groupby(x.date).sum() ** 2).sum()) / n
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


def row(x, risk):
    m, p = clustered(x)
    pf = x.R[x.R > 0].sum() / -x.R[x.R < 0].sum() if (x.R < 0).any() else np.nan
    return dict(N=len(x), meanR=round(m, 4) if len(x) else np.nan, win_pct=round(100 * (x.R > 0).mean(), 1) if len(x) else np.nan, PF=round(pf, 3), p_one=round(p, 3) if p == p else np.nan, **equity(x, risk))


def main():
    D = Data()
    tr = run(D)
    rows = [{"davr": k, **row(sl(tr, v), P["risk"])} for k, v in PER.items()]
    out = ["# Foydalanuvchi qoidasi (H1 bias + M5 EMA9 reclaim): natijalar (STRATEGY_LDN.md)\n", "## Asosiy qoida (xarajat $0.30, risk 0.75%)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    trs = run(D, cost=0.50)
    rs = row(sl(trs, DEC), P["risk"])
    out.append(f"## Stress ($0.50), qaror davri: meanR {rs['meanR']}, p {rs['p_one']}, maxDD {rs['maxDD_pct']}%\n")
    # random control
    dec = sl(tr, DEC)
    d0 = D.dayid
    elig = np.zeros(len(D.t), bool)
    for j in range(210, len(D.t) - 2):
        m1 = D.mod[j + 1]
        elig[j] = ((420 <= m1 < 660) or (720 <= m1 < 960)) and D.dow[j + 1] <= 4 and D.contig[j + 1] and not D.blocked[j + 1] and D.bias[j] != 0 and D.atr[j] == D.atr[j]
    nd = d0.max() + 1
    firstbar = np.searchsorted(d0, np.arange(nd + 1))
    cnt = np.zeros(nd, np.int64)
    dayid_of = dict(zip(D.day, d0))
    for dt, c_ in dec.groupby("date").size().items():
        cnt[dayid_of[dt]] = c_
    ctrl = rand_ctrl(elig, cnt, firstbar, D.o, D.h, D.l, D.c, D.e9, D.e21, D.rsi, D.atr, D.bias.astype(np.int64), D.rel, D.mod, D.contig, P["cost"], P["slmult"], P["tp1"], P["tp2"], 1000, 5)
    pc = float((ctrl >= dec.R.mean()).mean())
    out.append(f"## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR {dec.R.mean():.4f}; tasodifiy o'rtacha {ctrl.mean():.4f} (5–95%: {np.percentile(ctrl,5):.4f} … {np.percentile(ctrl,95):.4f}); p = {pc:.3f}\n")
    r = {k: row(sl(tr, v), P["risk"]) for k, v in PER.items()}
    dv = r["Dev 2018-21"]; dc = r["Qaror 2022-25"]
    crit = {"C1 meanR>0, p<=0.10, N>=200": dc["meanR"] > 0 and dc["p_one"] <= 0.10 and dc["N"] >= 200,
            "C2 stress meanR>0": rs["meanR"] > 0,
            "C3 Val va Final alohida meanR>0": r["Val 2022-23"]["meanR"] > 0 and r["Final 2024-25"]["meanR"] > 0,
            "C4 Dev ishonchli manfiy emas": not (dv["meanR"] < 0 and (1 - dv["p_one"]) <= 0.10),
            "C5 random control p<=0.10": pc <= 0.10,
            "C6 maxDD<=30% (qaror)": dc["maxDD_pct"] <= 30}
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    sens = []
    for name, kw in [("yangilik filtrisiz", dict(news=0)), ("risk 0.5%", dict(risk=0.005)), ("risk 1%", dict(risk=0.01)), ("faqat Buy", dict(side=1)), ("faqat Sell", dict(side=-1)),
                     ("faqat London", dict(sess="london")), ("faqat overlap", dict(sess="overlap")), ("reclaim faqat oxirgi bar", dict(win3=0)), ("xarajatsiz", dict(cost=0.0))]:
        x = sl(run(D, **kw), DEC)
        sens.append({"variant": name, **{k: row(x, kw.get("risk", P["risk"]))[k] for k in ["N", "meanR", "win_pct", "PF", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct"]}})
    out.append("## Sezgirlik (qaror davri, faqat ma'lumot)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    yr = dec.groupby(dec.date.dt.year).R.agg(["count", "mean"]).round(4)
    out.append("## Yillar bo'yicha (qaror davri)\n" + yr.to_markdown() + "\n")
    open("reports/ldn_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
