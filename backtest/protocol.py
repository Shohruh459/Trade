"""Pre-committed in-sample / out-of-sample protocol for EURUSD and XAUUSD (see STRATEGY.md sections 5-6).

Rules fixed BEFORE looking at results:
- 8 strategies x 5 exit styles = 40 fixed-parameter variants per instrument (nothing is tuned).
- Selection uses ONLY the in-sample period: PF > 1.1, >= 200 trades, max drawdown < 15%, not halted.
- Selected variants are run ONCE on the out-of-sample period (fresh $10k balance, indicators warmed up before the start).
- Pass criteria on out-of-sample: PF > 1.3, max DD < 15%, >= 200 trades, net > 0 after costs, OOS PF >= 0.8 x IS PF.

Usage: python -m backtest.protocol
"""
from dataclasses import replace

import numpy as np
import pandas as pd

from .engine import Config, metrics, run
from .explore import ALL, EXITS

INSTRUMENTS = {
    "EURUSD": dict(csv="data/EURUSD_H1_202004_202604.csv", is_range=("2020-04-01", "2024-01-01"), oos_range=("2024-01-01", "2026-04-07"),
                   cfg=Config()),
    "XAUUSD": dict(csv="data/XAUUSD_H1_2018_2025.csv", is_range=("2018-01-01", "2023-01-01"), oos_range=("2023-01-01", "2025-03-31"),
                   cfg=Config(pip=0.01, spread_pips=25, slippage_pips=5, lot_units=100, min_units=1, max_spread_pips=1e9)),
}
WARMUP = 300


def segment(df, sig, atr, cfg, rng):
    i0, i1 = df.index.searchsorted(pd.Timestamp(rng[0], tz="UTC")), df.index.searchsorted(pd.Timestamp(rng[1], tz="UTC"))
    a = max(0, i0 - WARMUP)
    s = np.array(sig[a:i1]).copy()
    s[: i0 - a] = 0
    tr, halted = run(df.iloc[a:i1], s, np.asarray(atr)[a:i1], cfg)
    return tr, halted


def month_stats(tr, rng):
    months = pd.period_range(rng[0], pd.Timestamp(rng[1]) - pd.Timedelta(days=1), freq="M")
    pnl = tr.groupby(tr.exit_time.dt.tz_localize(None).dt.to_period("M")).pnl.sum().reindex(months).fillna(0.0) if not tr.empty else pd.Series(0.0, index=months)
    return pnl


def main():
    out = ["# Yig'ma hisobot: EUR/USD va XAU/USD (oldindan belgilangan protokol)\n",
           "Protokol: 8 strategiya × 5 chiqish = 40 variant, parametrlar sozlanmagan. Tanlov faqat in-sample bo'yicha "
           "(PF>1.1, ≥200 bitim, DD<15%, to'xtamagan). Tanlanganlar out-of-sample'da **bir marta** sinaldi. "
           "O'tish mezoni (OOS): PF>1.3, DD<15%, ≥200 bitim, xarajatdan keyin foyda, OOS PF ≥ 0.8×IS PF. "
           "Har bir davr $10 000 dan, risk 1%.\n"]
    verdict = []
    for name, c in INSTRUMENTS.items():
        df = pd.read_csv(c["csv"], index_col=0, parse_dates=True)
        cfg0 = c["cfg"]
        rows, keep = [], {}
        for sname, fn in ALL.items():
            sig, atr = fn(df)
            for ename, over in EXITS.items():
                cfg = replace(cfg0, **over)
                tis, his = segment(df, sig, atr, cfg, c["is_range"])
                tos, hos = segment(df, sig, atr, cfg, c["oos_range"])
                mi, mo = metrics(tis, cfg.start_balance), metrics(tos, cfg.start_balance)
                key = f"{sname} {ename}"
                keep[key] = (tis, tos)
                rows.append({"variant": key, "IS_tr": mi.get("trades", 0), "IS_PF": mi.get("profit_factor"), "IS_net%": mi.get("net_pct"),
                             "IS_DD%": mi.get("max_dd_pct"), "IS_halt": his, "OOS_tr": mo.get("trades", 0), "OOS_PF": mo.get("profit_factor"),
                             "OOS_net%": mo.get("net_pct"), "OOS_DD%": mo.get("max_dd_pct"), "OOS_halt": hos})
        r = pd.DataFrame(rows)
        sel = r[(r.IS_PF > 1.1) & (r.IS_tr >= 200) & (r["IS_DD%"] < 15) & (~r.IS_halt)].copy()
        sel["pass"] = ((sel.OOS_PF > 1.3) & (sel["OOS_DD%"] < 15) & (sel.OOS_tr >= 200) & (sel["OOS_net%"] > 0)
                       & (sel.OOS_PF >= 0.8 * sel.IS_PF) & (~sel.OOS_halt))
        r.to_csv(f"reports/protocol_{name}_all40.csv", index=False)
        out += [f"\n## {name}\n",
                f"Ma'lumot: {c['csv']}. In-sample {c['is_range'][0]} → {c['is_range'][1]}, out-of-sample {c['oos_range'][0]} → {c['oos_range'][1]}. "
                f"Xarajat: spred {cfg0.spread_pips} pip, slippage {cfg0.slippage_pips} pip, komissiya ${cfg0.commission_per_lot}/lot.\n",
                f"40 variantdan in-sample mezonidan o'tgani: **{len(sel)}**. Mezondan o'tmaganlar OOS'da ko'rib chiqilmaydi (to'liq jadval: `reports/protocol_{name}_all40.csv`, shaffoflik uchun).\n"]
        if sel.empty:
            out.append("_In-sample'da tanlov mezonidan o'tgan variant yo'q._\n")
            n_pass = 0
        else:
            out.append(sel.drop(columns=["IS_halt", "OOS_halt"]).to_markdown(index=False) + "\n")
            n_pass = int(sel["pass"].sum())
            best = sel.sort_values("IS_PF", ascending=False).iloc[0].variant
            tis, tos = keep[best]
            mo = month_stats(tos, c["oos_range"])
            out += [f"\nIn-sample bo'yicha eng yaxshi tanlangan variant: **{best}**. OOS oylik foyda ($):\n",
                    pd.DataFrame({"oy": mo.index.astype(str), "foyda_$": mo.round(0).astype(int).to_numpy()}).T.to_markdown(header=False) + "\n",
                    f"OOS: {int((mo > 0).sum())} oy foydali, {int((mo < 0).sum())} oy zararli, {int((mo == 0).sum())} oy bitimsiz (jami {len(mo)} oy).\n"]
        verdict.append((name, len(sel), n_pass))
    out += ["\n## Xulosa\n", "| Instrument | IS'dan o'tgan | OOS mezonidan o'tgan |", "|---|---|---|"]
    out += [f"| {n} | {a} | {b} |" for n, a, b in verdict]
    open("reports/final_summary.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
