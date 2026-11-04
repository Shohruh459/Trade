"""Python port of shahmeetk/grid-scalper-ea with Gold_Optimized.set (STRATEGY_GRIDEA.md, pre-registered). Nothing is tuned.

Usage: python -m backtest.gridea      -> reports/gridea_results.md
"""
import numpy as np
import pandas as pd
from numba import njit

from backtest.ldn import load

LOTS = np.array([0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04, 0.06, 0.10])
MAXO = 12
OZ = 100.0


@njit(cache=True)
def sim(o, h, l, c, i0, i1, bal0, sides, spr, fin, lots, maxdd, grid, add, incr_after, tpd, trail_profit, trail_start, trail_step, cool_bars):
    """sides: 0 sell only, 1 buy only, 2 both. Returns eq_close, eq_min, n_ddstop, ddloss, maxoz, blown_idx, bal_end."""
    n = i1 - i0
    eqc = np.empty(n); eqm = np.empty(n)
    op = np.zeros((2, 12)); lt = np.zeros((2, 12)); sl = np.zeros((2, 12)); cnt = np.zeros(2, np.int64)
    bal = bal0
    nd = 0; ddloss = 0.0; maxoz = 0.0
    cool_until = -1
    blown = -1
    for bi in range(n):
        b = i0 + bi
        pts = np.empty(4)
        pts[0] = o[b]
        pts[1] = h[b] if sides != 1 else l[b]
        pts[2] = l[b] if sides != 1 else h[b]
        pts[3] = c[b]
        emin = 1e18
        for q in range(4):
            p = pts[q]
            ask = p + spr
            for s in range(2):
                if (sides == 0 and s == 1) or (sides == 1 and s == 0):
                    continue
                dr = -1.0 if s == 0 else 1.0
                px_open = p if s == 0 else ask       # price at which we open
                if cnt[s] == 0:
                    if q == 0 and bi > cool_until:
                        op[s, 0] = px_open; lt[s, 0] = lots[0] * OZ; sl[s, 0] = 0.0; cnt[s] = 1
                    continue
                # SL (trailing) hit on last order
                k = cnt[s] - 1
                if sl[s, k] > 0:
                    hit = (s == 0 and ask >= sl[s, k]) or (s == 1 and p <= sl[s, k])
                    if hit:
                        fill = sl[s, k] if q != 0 else (ask if s == 0 else p)
                        if s == 0:
                            bal += lt[s, k] * (op[s, k] - max(fill, sl[s, k]) if q == 0 and False else op[s, k] - fill)
                        else:
                            bal += lt[s, k] * (fill - op[s, k])
                        cnt[s] -= 1
                        k = cnt[s] - 1
                        if cnt[s] == 0:
                            continue
                # grid expansion (may trigger several levels in one move)
                while cnt[s] < MAXO:
                    worst = op[s, 0]
                    for j in range(cnt[s]):
                        if s == 0 and op[s, j] > worst: worst = op[s, j]
                        if s == 1 and op[s, j] < worst: worst = op[s, j]
                    req = grid + (add if cnt[s] >= incr_after else 0.0)
                    if s == 0:
                        lvl = worst + req
                        if p >= lvl:
                            fill = p if q == 0 else lvl
                        else:
                            break
                    else:
                        lvl = worst - req
                        if ask <= lvl:
                            fill = ask if q == 0 else lvl
                        else:
                            break
                    li = cnt[s] if cnt[s] < len(lots) else len(lots) - 1
                    op[s, cnt[s]] = fill; lt[s, cnt[s]] = lots[li] * OZ; sl[s, cnt[s]] = 0.0; cnt[s] += 1
                # basket TP
                sv = 0.0; sp_ = 0.0
                for j in range(cnt[s]):
                    sv += lt[s, j]; sp_ += lt[s, j] * op[s, j]
                avg = sp_ / sv
                if s == 0:
                    tp = avg - tpd
                    if ask <= tp:
                        fill = ask if q == 0 else tp
                        for j in range(cnt[s]): bal += lt[s, j] * (op[s, j] - fill)
                        cnt[s] = 0
                        continue
                else:
                    tp = avg + tpd
                    if p >= tp:
                        fill = p if q == 0 else tp
                        for j in range(cnt[s]): bal += lt[s, j] * (fill - op[s, j])
                        cnt[s] = 0
                        continue
                # trailing on last order when basket profit >= threshold
                fl = 0.0
                for j in range(cnt[s]):
                    fl += lt[s, j] * ((op[s, j] - ask) if s == 0 else (p - op[s, j]))
                if fl >= trail_profit:
                    k = cnt[s] - 1
                    if s == 0 and ask < op[s, k] - trail_start:
                        prop = ask + trail_step
                        if prop < op[s, k] and (sl[s, k] == 0 or prop < sl[s, k]): sl[s, k] = prop
                    if s == 1 and p > op[s, k] + trail_start:
                        prop = p - trail_step
                        if prop > op[s, k] and prop > sl[s, k]: sl[s, k] = prop
            # equity and DD protection
            fl = 0.0; oz = 0.0
            for s in range(2):
                for j in range(cnt[s]):
                    fl += lt[s, j] * ((op[s, j] - ask) if s == 0 else (p - op[s, j]))
                    oz += lt[s, j]
            if oz > maxoz: maxoz = oz
            eq = bal + fl
            if eq < emin: emin = eq
            if bal - eq > maxdd:
                bal = eq
                ddloss += bal0 * 0 + (fl)   # negative floating realised
                nd += 1
                cnt[0] = 0; cnt[1] = 0
                cool_until = bi + cool_bars
            if eq <= 0:
                blown = bi
                break
        if blown >= 0:
            for k2 in range(bi, n):
                eqc[k2] = 0.0; eqm[k2] = 0.0
            return eqc, eqm, nd, ddloss, maxoz, blown, 0.0
        # financing on open notional
        oz = 0.0
        for s in range(2):
            for j in range(cnt[s]): oz += lt[s, j]
        bal -= oz * c[b] * fin / 365.0 / 1440.0
        fl = 0.0
        a = c[b] + spr
        for s in range(2):
            for j in range(cnt[s]):
                fl += lt[s, j] * ((op[s, j] - a) if s == 0 else (c[b] - op[s, j]))
        eqc[bi] = bal + fl
        eqm[bi] = emin
    return eqc, eqm, nd, ddloss, maxoz, blown, bal


def run(m1, arrs, i0, i1, bal0=5000.0, sides=0, spr=0.30, fin=0.03):
    o, h, l, c = arrs
    return sim(o, h, l, c, i0, i1, bal0, sides, spr, fin, LOTS, 2000.0, 4.0, 2.0, 3, 10.0, 30.0, 5.0, 1.0, 5)


def stats(m1, i0, i1, res, bal0):
    eqc, eqm, nd, ddloss, maxoz, blown, bal = res
    idx = m1.index[i0:i1]
    peak = np.maximum.accumulate(np.maximum(eqc, bal0))
    dd = ((peak - eqm) / peak).max() if blown < 0 else 1.0
    s = pd.Series(eqc, index=idx)
    me = s.resample("ME").last()
    mr = me.pct_change().dropna()
    mr = pd.concat([pd.Series([me.iloc[0] / bal0 - 1], index=[me.index[0]]), mr]) if len(me) else mr
    yr = s.resample("YE").last().diff().fillna(s.resample("YE").last().iloc[0] - bal0)
    last = eqc[-1]
    # longest underwater run (days) on daily equity
    dly = s.resample("1D").last().dropna()
    under = (dly < dly.cummax()).astype(int)
    longest = 0; cur = 0
    for v in under.to_numpy():
        cur = cur + 1 if v else 0
        longest = max(longest, cur)
    return dict(final=round(float(last), 0), profit_pct=round(100 * (last / bal0 - 1), 1), maxdd_pct=round(100 * float(dd), 1), dd_stops=int(nd), blown=int(blown >= 0), max_oz=round(float(maxoz), 1),
                pos_months_pct=round(100 * float((mr > 0).mean()), 1), worst_month_pct=round(100 * float(mr.min()), 1), longest_under_d=int(longest)), yr


def main():
    m1 = load()
    arrs = tuple(m1[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    n = len(m1)
    names = {0: "Sell-only (.set)", 1: "Buy-only", 2: "Both (EA default)"}
    rows, yrs = [], {}
    for sides in (0, 1, 2):
        r = run(m1, arrs, 0, n, 5000.0, sides)
        st, yr = stats(m1, 0, n, r, 5000.0)
        rows.append({"variant": names[sides], **st}); yrs[names[sides]] = yr
    out = ["# grid-scalper-ea (Python port, Gold_Optimized.set): natijalar (STRATEGY_GRIDEA.md)\n", "## Butun davr 2018-01 → 2025-02, balans $5,000, spred $0.30, swap 3%\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n"]
    out.append("## Yillik foyda ($, asosiy Sell-only)\n" + yrs["Sell-only (.set)"].round(0).to_frame("pnl").to_markdown() + "\n")
    # stress and $3000
    r2 = run(m1, arrs, 0, n, 5000.0, 0, 0.50, 0.05)
    st2, _ = stats(m1, 0, n, r2, 5000.0)
    r3 = run(m1, arrs, 0, n, 3000.0, 0, 0.30, 0.03)
    st3, _ = stats(m1, 0, n, r3, 3000.0)
    out.append(f"## Stress ($0.50 / swap 5%), Sell-only: {st2}\n\n## Balans $3,000, Sell-only: {st3}\n")
    # halves
    cut = int(np.searchsorted(m1.index.to_numpy(), np.datetime64("2022-01-01")))
    h1, h2 = run(m1, arrs, 0, cut, 5000.0, 0), run(m1, arrs, cut, n, 5000.0, 0)
    s1, _ = stats(m1, 0, cut, h1, 5000.0); s2, _ = stats(m1, cut, n, h2, 5000.0)
    out.append(f"## Yarmlar (Sell-only): 2018–2021: {s1}\n\n2022–2025: {s2}\n")
    # rolling 12-month windows, quarterly starts
    wrows = []
    starts = pd.date_range("2018-01-01", "2024-02-28", freq="QS")
    for sd in starts:
        i0 = int(np.searchsorted(m1.index.to_numpy(), np.datetime64(sd)))
        ed = sd + pd.DateOffset(months=12)
        i1 = int(np.searchsorted(m1.index.to_numpy(), np.datetime64(ed)))
        if i1 - i0 < 200000: continue
        for sides in (0, 2):
            rr = run(m1, arrs, i0, i1, 5000.0, sides)
            s_, _ = stats(m1, i0, i1, rr, 5000.0)
            wrows.append(dict(start=sd.date(), variant=names[sides], profit_pct=s_["profit_pct"], maxdd_pct=s_["maxdd_pct"], dd_stops=s_["dd_stops"]))
    W = pd.DataFrame(wrows)
    summ = W.groupby("variant").agg(oynalar=("profit_pct", "size"), foydali_pct=("profit_pct", lambda x: round(100 * float((x > 0).mean()), 1)), eng_yomon=("profit_pct", "min"), median=("profit_pct", "median"), eng_yaxshi=("profit_pct", "max"), dd_stops_jami=("dd_stops", "sum")).reset_index()
    out.append("## 12 oylik oynalar (har chorak boshlanishidan, $5,000 dan qayta)\n" + summ.to_markdown(index=False) + "\n")
    base = rows[0]
    wins = W[W.variant == names[0]]
    crit = {"G1 sof foyda>0": base["final"] > 5000,
            "G2 maxDD<=30%": base["maxdd_pct"] <= 30,
            "G3 DD-stop<=5 va bankrot yo'q": base["dd_stops"] <= 5 and base["blown"] == 0,
            "G4 12 oylik: >=70% foydali va eng yomon>=-20%": float((wins.profit_pct > 0).mean()) >= 0.7 and wins.profit_pct.min() >= -20,
            "G5 stress foyda>0": st2["final"] > 5000,
            "G6 ikki yarim foydali": s1["final"] > 5000 and s2["final"] > 5000}
    verdict = "O'TDI (dastlabki, simulyatsiya)" if all(crit.values()) else "O'TMADI"
    out.append("## Mezonlar (asosiy Sell-only)\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    open("reports/gridea_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
