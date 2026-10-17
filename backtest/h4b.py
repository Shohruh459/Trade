"""User's Daily-bias / H4 Donchian(20) breakout gold strategy (STRATEGY_H4_BREAKOUT.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.h4b      -> reports/h4b_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.h4 import DEC, HALF, Data, clustered, equity, row, sl

P = dict(cost=0.30, fin=0.03, risk=0.0075, news=1, chan=1, smax=2.0, side=0)


@njit(cache=True)
def trade(e, dr, s, lvl, o, h, l, c, rel, tns, cost, fin, chan):
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
        if chan == 1 and ((dr == 1 and c[b] <= lvl) or (dr == -1 and c[b] >= lvl)):
            flag = True
        if rel[b] != rel0 and rel[b] != 0:
            flag = True
    if rem > 0:
        pnl += rem * (c[xb] - ent) * dr
    days = (tns[xb] + 4 * 3600 * 10 ** 9 - tns[e]) / (86400.0 * 10 ** 9)
    return (pnl - cost - fin * ent * days / 365.0) / s, xb


@njit(cache=True)
def run_signals(o, h, l, c, U, L, atr, bias, rel, tns, dayid, blocked, cost, fin, chan, smax, news, side):
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
        if bias[j] == 0 or cnt >= 2 or tns[e] < cd_until or (news == 1 and blocked[e]) or atr[j] != atr[j] or U[j] != U[j]:
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
        stop = l[j] - 0.3 * atr[j] if d == 1 else h[j] + 0.3 * atr[j]
        s = (o[e] - stop) * d
        if s <= 0 or s > smax * atr[j]:
            j += 1
            continue
        lvl = U[j] if d == 1 else L[j]
        r, xb = trade(e, d, s, lvl, o, h, l, c, rel, tns, cost, fin, chan)
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
def rand_ctrl(elig, N, pool, o, h, l, c, U, L, bias, rel, tns, cost, fin, chan, draws, seed):
    np.random.seed(seed)
    idx = np.where(elig)[0]
    out = np.empty(draws)
    for it in range(draws):
        tot = 0.0
        for _ in range(N):
            j = idx[np.random.randint(0, len(idx))]
            s = pool[np.random.randint(0, len(pool))]
            lvl = U[j] if bias[j] == 1 else L[j]
            r, _x = trade(j + 1, bias[j], s, lvl, o, h, l, c, rel, tns, cost, fin, chan)
            tot += r
        out[it] = tot / N
    return out


def chan_arrays(D):
    hi = pd.Series(D.h).rolling(20).max().shift(1).to_numpy()
    lo = pd.Series(D.l).rolling(20).min().shift(1).to_numpy()
    return hi, lo


def run(D, U, L, **kw):
    p = {**P, **kw}
    ti, td, tr, tx, ts = run_signals(D.o, D.h, D.l, D.c, U, L, D.atr, D.bias, D.rel, D.tns, D.dayid, D.blocked, p["cost"], p["fin"], p["chan"], p["smax"], p["news"], p["side"])
    df = pd.DataFrame({"i": ti, "dir": td, "R": tr, "x": tx, "s": ts})
    df["t"] = D.t[df.i.to_numpy()]
    df["date"] = df.t.dt.normalize()
    df["hold_d"] = (D.tns[df.x.to_numpy()] - D.tns[df.i.to_numpy()]) / 86400e9
    return df


def main():
    D = Data()
    U, L = chan_arrays(D)
    tr = run(D, U, L)
    dec = sl(tr, DEC)
    rows = [{"davr": k, **row(sl(tr, v))} for k, v in {"Qaror 2019-25": DEC, **HALF}.items()]
    out = ["# Foydalanuvchi qoidasi (Daily bias + H4 Donchian breakout): natijalar (STRATEGY_H4_BREAKOUT.md)\n", "## Asosiy qoida (xarajat $0.30 + 3% moliyalashtirish, risk 0.75%)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    rs = row(sl(run(D, U, L, cost=0.50, fin=0.05), DEC))
    out.append(f"## Stress ($0.50, 5%), qaror davri: meanR {rs['meanR']}, p {rs['p_one']}, maxDD {rs['maxDD_pct']}%\n")
    elig = (D.bias != 0) & ~D.blocked & (D.t >= pd.Timestamp(DEC[0])) & (D.t < pd.Timestamp(DEC[1])) & ~np.isnan(U)
    elig[:250] = False
    elig[-3:] = False
    ctrl = rand_ctrl(elig, len(dec), dec.s.to_numpy(), D.o, D.h, D.l, D.c, U, L, D.bias, D.rel, D.tns, P["cost"], P["fin"], P["chan"], 1000, 3)
    pc = float((ctrl >= dec.R.mean()).mean())
    out.append(f"## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR {dec.R.mean():.4f}; tasodifiy o'rtacha {ctrl.mean():.4f} (5–95%: {np.percentile(ctrl,5):.4f} … {np.percentile(ctrl,95):.4f}); p = {pc:.3f}\n")
    r1, r2, dc = row(sl(tr, HALF["2019-21"])), row(sl(tr, HALF["2022-25"])), row(dec)
    crit = {"C1 meanR>0, p<=0.10, N>=60": dc["meanR"] > 0 and dc["p_one"] <= 0.10 and dc["N"] >= 60,
            "C2 stress meanR>0": rs["meanR"] > 0,
            "C3 ikki yarimda meanR>0": r1["meanR"] > 0 and r2["meanR"] > 0,
            "C4 profit factor>=1.2": dc["PF"] >= 1.2,
            "C5 random control p<=0.10": pc <= 0.10,
            "C6 maxDD<=20%": dc["maxDD_pct"] <= 20}
    verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## Mezonlar\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    sens = []
    for name, kw in [("yangilik filtrisiz", dict(news=0)), ("risk 1%", dict(risk=0.01)), ("faqat Buy", dict(side=1)), ("faqat Sell", dict(side=-1)), ("kanal-chiqishsiz", dict(chan=0)),
                     ("stop filtri (2.0 ATR) siz", dict(smax=100.0)), ("xarajatsiz", dict(cost=0.0, fin=0.0))]:
        x = sl(run(D, U, L, **kw), DEC)
        sens.append({"variant": name, **{k: row(x, kw.get("risk", P["risk"]))[k] for k in ["N", "meanR", "win_pct", "PF", "p_one", "ret_pct", "maxDD_pct", "pos_months_pct"]}})
    out.append("## Sezgirlik (qaror davri, faqat ma'lumot)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    yr = dec.groupby(dec.date.dt.year).R.agg(["count", "mean"]).round(4)
    out.append("## Yillar bo'yicha\n" + yr.to_markdown() + "\n")
    open("reports/h4b_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
