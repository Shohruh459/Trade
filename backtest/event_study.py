"""Event study H1 (see STRATEGY_GOLD.md, pre-registered): what does gold do after an extreme 1-minute bar in 12-16 UTC?

Event: 1-min MID bar (from ticks) starting 12:00-16:00 UTC with range >= K x ATR14 (previous 14 bars), dir = sign(close-open), 10-min de-duplication.
Entry 1 s after the event bar closes at the real ask/bid, fixed-time exit after H minutes at the real bid/ask. Cells: {continuation, fade} x {3,5,10} min.
Usage: python -m backtest.event_study
"""
from pathlib import Path

import numpy as np
import pandas as pd

TICKS = Path("/tmp/claude-0/ticks")


def events_from_file(path, k=4.0, hours=(12, 16), hs=(3, 5, 10), dedup=10, latency_s=1.0):
    d = pd.read_parquet(path)
    ts, ask, bid = d["timestamp"].to_numpy(), d["askPrice"].to_numpy(float), d["bidPrice"].to_numpy(float)
    o_ = np.argsort(ts, kind="stable")
    ts, ask, bid = ts[o_], ask[o_], bid[o_]
    mid = (ask + bid) / 2
    m = ts // 60_000
    st = np.flatnonzero(np.r_[True, m[1:] != m[:-1]])
    bm = m[st]
    o, c = mid[st], mid[np.r_[st[1:] - 1, len(m) - 1]]
    h, l = np.maximum.reduceat(mid, st), np.minimum.reduceat(mid, st)
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().shift(1).to_numpy()
    hour = (bm * 60 % 86400) // 3600
    ev = np.flatnonzero((hour >= hours[0]) & (hour < hours[1]) & (atr > 0) & ((h - l) >= k * atr) & (c != o))
    rows, last = [], -10 ** 12
    for j in ev:
        if bm[j] - last < dedup:
            continue
        last = bm[j]
        t_entry = ((bm[j] + 1) * 60 + latency_s) * 1000
        ie = np.searchsorted(ts, t_entry, side="left")
        if ie >= len(ts) or ts[ie] - t_entry > 30_000:
            continue
        de = int(np.sign(c[j] - o[j]))
        for hh in hs:
            tx = t_entry + hh * 60_000
            ix = np.searchsorted(ts, tx, side="left")
            if ix >= len(ts) or ts[ix] - tx > 30_000 or ix <= ie:
                continue
            for mode, dr in (("cont", de), ("fade", -de)):
                if dr == 1:
                    net, gross = bid[ix] - ask[ie], mid[ix] - mid[ie]
                else:
                    net, gross = bid[ie] - ask[ix], -(mid[ix] - mid[ie])
                rows.append(dict(date=str(pd.Timestamp(t_entry, unit="ms").date()), year=pd.Timestamp(t_entry, unit="ms").year, mode=mode, h=hh,
                                 net=net, gross=gross, spr_in=ask[ie] - bid[ie], spr_out=ask[ix] - bid[ix], atr=atr[j], rng=h[j] - l[j], ev_dir=de, trade_dir=dr))
    return pd.DataFrame(rows)


def collect(files, **kw):
    return pd.concat([events_from_file(TICKS / f, **kw).assign(file=f) for f in files], ignore_index=True)


def cluster_t(x, g):
    x = np.asarray(x, float)
    mu = x.mean()
    s = pd.Series(x - mu).groupby(np.asarray(g)).sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / len(x)
    return mu / se if se > 0 else np.nan


def table(df, stress=0.10):
    rows = {}
    for (mode, h), g in df.groupby(["mode", "h"]):
        rows[(mode, h)] = dict(N=len(g), gross=round(g.gross.mean(), 3), net=round(g.net.mean(), 3), net_stress=round(g.net.mean() - stress, 3),
                               t_net=round(cluster_t(g.net, g.date), 2), win_pct=round(100 * (g.net > 0).mean(), 1), spread_in=round(g.spr_in.mean(), 2),
                               yrs_pos=f"{int((g.groupby('year').net.mean()[g.groupby('year').size() >= 10] > 0).sum())}/{int((g.groupby('year').size() >= 10).sum())}")
    return pd.DataFrame(rows).T


def main():
    disc = [f for f in open("/tmp/claude-0/tick_sample.txt").read().split("\n") if f]
    conf = [f for f in open("/tmp/claude-0/tick_confirm.txt").read().split("\n") if f]
    D, C = collect(disc), collect(conf)
    td, tc = table(D), table(C)
    out = ["# H1 hodisa tadqiqoti: 12–16 UTC dagi o'ta katta 1 daqiqalik shamdan keyin oltin (XAUUSD tick, Dukascopy)\n",
           "Reja: `STRATEGY_GOLD.md` (natijadan oldin commit qilingan). $ / uns hisobida; `gross` = o'rta narxdan o'rta narxga, `net` = real bid/ask bilan, "
           "`t_net` = kun bo'yicha klasterlangan t. Cont = hodisa yo'nalishida, fade = teskari.\n",
           f"\n## Discovery ({len(disc)} fayl, {D.date.nunique()} kun, {D[D.h==3].shape[0]//2} hodisa)\n", td.to_markdown() + "\n",
           f"\n## Confirmation ({len(conf)} fayl, {C.date.nunique()} kun, {C[C.h==3].shape[0]//2} hodisa)\n", tc.to_markdown() + "\n"]
    # pre-registered decision rule
    out.append("\n## Oldindan belgilangan mezon bo'yicha qaror\n")
    verdict = []
    for cell in td.index:
        a, b = td.loc[cell], tc.loc[cell] if cell in tc.index else None
        c1 = a.net > 0 and abs(a.t_net) >= 2.6 and a.N >= 300
        c2 = b is not None and b.net > 0 and b.t_net >= 1.65
        c3 = a.net_stress > 0 and (b is not None and b.net_stress > 0)
        both = pd.concat([D[(D["mode"] == cell[0]) & (D.h == cell[1])], C[(C["mode"] == cell[0]) & (C.h == cell[1])]])
        yy = both.groupby("year").net.mean()[both.groupby("year").size() >= 10]
        c4 = len(yy) > 0 and (yy > 0).mean() >= 0.7
        verdict.append(dict(cell=f"{cell[0]} {cell[1]}min", disc_ok=c1, conf_ok=c2, stress_ok=c3, years_ok=c4, PASS=bool(c1 and c2 and c3 and c4)))
    out += [pd.DataFrame(verdict).to_markdown(index=False) + "\n"]
    # sensitivity (information only)
    out.append("\n## Sezgirlik (faqat ma'lumot uchun; discovery+confirmation birga, net $/uns, t)\n")
    allf = disc + conf
    sens = {}
    for k in (3.0, 4.0, 5.0, 6.0):
        S = collect(allf, k=k)
        for key, g in S.groupby(["mode", "h"]):
            if key[1] == 5:
                sens[f"k={k:g} {key[0]} 5min"] = dict(N=len(g), gross=round(g.gross.mean(), 3), net=round(g.net.mean(), 3), t_net=round(cluster_t(g.net, g.date), 2))
    S = collect(allf, hours=(7, 10))
    for key, g in S.groupby(["mode", "h"]):
        if key[1] == 5:
            sens[f"07-10 UTC k=4 {key[0]} 5min"] = dict(N=len(g), gross=round(g.gross.mean(), 3), net=round(g.net.mean(), 3), t_net=round(cluster_t(g.net, g.date), 2))
    out += [pd.DataFrame(sens).T.to_markdown() + "\n"]
    # cost context
    allv = pd.concat([D, C])
    e = allv[(allv["mode"] == "cont") & (allv.h == 5)]
    out += [f"\nKontekst: hodisada o'rtacha kirish spredi ${e.spr_in.mean():.2f} (oddiy paytda ~$0.3–0.5), 5 daqiqada o'rtacha |harakat| ${e.gross.abs().mean():.2f}, "
            f"hodisa shamining o'rtacha diapazoni ${e.rng.mean():.2f}.\n"]
    open("reports/event_study_H1.md", "w").write("\n".join(out))
    pd.concat([D.assign(set="discovery"), C.assign(set="confirmation")]).to_csv("reports/event_study_H1_events.csv", index=False)
    print("\n".join(out))


if __name__ == "__main__":
    main()
