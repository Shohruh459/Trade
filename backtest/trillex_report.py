"""Run the Trillex tick port over the pre-committed sample (Mar/Sep of 2019-2026) and write reports/trillex.md.  Usage: python -m backtest.trillex_report"""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .trillex import P, run_file

TICKS = Path("/tmp/claude-0/ticks")


def agg(trs):
    t = pd.concat([x.assign(file=k) for k, x in trs.items() if len(x)], ignore_index=True)
    r = t.r.to_numpy()
    w, ls = r[r > 0].sum(), -r[r <= 0].sum()
    e = 1.96 * r.std(ddof=1) / np.sqrt(len(r))
    per = {k: x.r.sum() for k, x in trs.items() if len(x)}
    return dict(trades=len(t), win_pct=round(100 * (r > 0).mean(), 1), PF_R=round(w / ls, 2), avg_R=round(r.mean(), 3),
                avgR_CI=f"{r.mean() - e:+.3f}…{r.mean() + e:+.3f}", gross_avg_R=round(t.gross_r.mean(), 3),
                med_hold_s=int(t.hold_s.median()), files_pos=f"{sum(v > 0 for v in per.values())}/{len(per)}"), t


def main():
    files = [f for f in open("/tmp/claude-0/tick_sample.txt").read().split("\n") if f]
    scen = {
        "S1 Insane, haqiqiy spred (EA 30-pt cheklovi bilan)": P(spread_mode="real", sizing="unit"),
        "S2 Insane, spred $0.25 (doimiy)": P(spread_mode="fixed", sizing="unit"),
        "S3 Insane, spred $0.10 (juda arzon)": P(spread_mode="fixed", fixed_spread=0.10, sizing="unit"),
        "S4 Normal rejim (InpUseInsaneMode=false), spred $0.25": P(insane=False, spread_mode="fixed", sizing="unit"),
        "S5 Insane, spred $0.25, chiqish EMA5 bo'yicha": P(spread_mode="fixed", exit_mode="ema5", sizing="unit"),
    }
    out = ["# TRILLEX 10S BASIC (NadirAliOfficial/trillex-10s-ea) — tick sinovi, XAUUSD, Dukascopy tick ma'lumoti\n",
           f"Namuna oldindan belgilangan qoida bilan tanlangan: har yil (2019–2026) mart va sentyabr oyining boshidan boshlanadigan birinchi fayl, jami {len(files)} fayl "
           "(15 kunlik yoki 30 kunlik oynalar). EA'ning 10 soniyalik sintetik bar mexanizmi tick darajasida ko'chirilgan; parametrlar standart, o'zgartirilmagan. "
           "R = bitim foydasi / SL masofasi ($2.00/oz); xarajatdan oldingi (gross) R — o'rta narxdan o'rta narxga.\n"]
    res, per_file = {}, {}
    for name, p in scen.items():
        trs = {f: run_file(TICKS / f, p) for f in files}
        res[name], tr_all = agg(trs)
        per_file[name] = trs
    out += ["\n## Stsenariylar (R bo'yicha, 1 uns/bitim)\n", pd.DataFrame(res).T.to_markdown() + "\n",
            "`gross_avg_R` — spred hisobga olinmagan o'rtacha R; `avg_R` — xarajatdan keyin. `files_pos` — namunalardan nechtasida jami R musbat.\n"]
    # per-file view for S2
    k = "S2 Insane, spred $0.25 (doimiy)"
    rows = {f[:7]: dict(trades=len(x), avg_R=round(x.r.mean(), 3) if len(x) else None, gross_R=round(x.gross_r.mean(), 3) if len(x) else None,
                         win_pct=round(100 * (x.r > 0).mean(), 1) if len(x) else None) for f, x in per_file[k].items()}
    out += [f"\n## {k}: namunalar bo'yicha\n", pd.DataFrame(rows).T.to_markdown() + "\n"]
    # spread gate share in real mode
    gate = {}
    for f in files:
        d = pd.read_parquet(TICKS / f, columns=["askPrice", "bidPrice"])
        s = (d.askPrice - d.bidPrice)
        gate[f[:7]] = dict(median_spread_usd=round(float(s.median()), 2), pct_ticks_le_30pt=round(float((s <= 0.30).mean() * 100), 1))
    out += ["\n## Haqiqiy Dukascopy spredi va EA'ning 30-punkt cheklovi\n", pd.DataFrame(gate).T.to_markdown() + "\n"]
    # as-coded sizing: lots = 1 * 10^floor(log10(balance/1000)), SL $2 => risk per trade
    out += ["\n## EA'ning o'z lot qoidasi (kodda): lot = 1 × 10^floor(log10(balans/1000))\n",
            "| Balans | Lot | 100 uns/lot, SL $2 | Bitta SL zarari | Balansga nisbatan |", "|---|---|---|---|---|"]
    for b in (500, 1000, 5000, 9999, 10000, 50000, 100000):
        tier = int(np.floor(np.log10(b / 1000) + 1e-9)) if b >= 1000 else 0
        lots = 10 ** tier
        out.append(f"| ${b:,} | {lots} | {lots*100:.0f} oz | ${lots*200:,.0f} | {lots*200/b:.0%} |")
    s2 = per_file[k]
    ruin = {}
    for start in (1000.0, 10000.0):
        died = 0
        for f in files:
            tr = run_file(TICKS / f, replace(scen[k], sizing="coded", start_balance=start))
            died += int(len(tr) > 0 and tr.bal.iloc[-1] <= start * 0.5)
        ruin[f"${start:,.0f}"] = f"{died}/{len(files)} namunada balans yarmidan pastga tushdi"
    out += ["\nS2 stsenariysi EA'ning o'z lot qoidasi bilan (har namuna alohida boshlangan):\n", pd.DataFrame([ruin]).T.to_markdown(headers=[]) + "\n"]
    open("reports/trillex.md", "w").write("\n".join(out))
    pd.concat([x.assign(file=f) for f, x in per_file[k].items() if len(x)]).to_csv("reports/trillex_trades_S2.csv", index=False)
    print("\n".join(out))


if __name__ == "__main__":
    main()
