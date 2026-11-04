"""Descriptive check of frozen gold rules on 2026-09 and 2026-10 (STRATEGY_OOS2026.md). Nothing is tuned.

Data: bnq-ii/MT5_MetaQuotes-Demo_XAUUSD (Hugging Face) in /tmp/claude-0/mq (1m/2026-07..11.parquet, 1D/2020-2029.parquet).
Usage: python -m backtest.oos2026      -> reports/oos2026_results.md
"""
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
MQ = "/tmp/claude-0/mq"
MONTHS = {"2026-09": ("2026-09-01", "2026-10-01"), "2026-10": ("2026-10-01", "2026-11-01")}


def load_m1():
    d = pd.concat([pd.read_parquet(f"{MQ}/1m/2026-{m:02d}.parquet") for m in (7, 8, 9, 10, 11)])
    d.index = pd.to_datetime(d.time, unit="s") - pd.Timedelta(hours=1)
    d = d[["open", "high", "low", "close"]].sort_index()
    d = d[~d.index.duplicated()]
    return d[d.index < "2026-11-01"]


def load_d1():
    d = pd.read_parquet(f"{MQ}/1D/2020-2029.parquet")
    d.index = pd.to_datetime(d.time, unit="s") - pd.Timedelta(hours=1)
    return d[["open", "high", "low", "close"]].sort_index()


def month_rows(name, tr, risk, mcol="date"):
    out = []
    for mo, (a, b) in MONTHS.items():
        x = tr[(tr[mcol] >= pd.Timestamp(a)) & (tr[mcol] < pd.Timestamp(b))]
        eq = float(np.prod(1 + x.R.to_numpy() * risk) - 1) if len(x) else 0.0
        out.append(dict(qoida=name, oy=mo, savdolar=len(x), yutuq_pct=round(100 * float((x.R > 0).mean()), 1) if len(x) else np.nan, jami_R=round(float(x.R.sum()), 2),
                        o_rtacha_R=round(float(x.R.mean()), 3) if len(x) else np.nan, hisob_pct=round(100 * eq, 2), risk_pct=round(100 * risk, 2)))
    return out


def main():
    import backtest.h4 as H4
    import backtest.h4b as H4B
    import backtest.ldn as LDN
    import backtest.m15 as M15
    import backtest.n3 as N3

    m1, d1 = load_m1(), load_d1()
    rows = []
    # H4 breakout (candidate) and H4 EMA20 reclaim
    D = H4.Data(m1, d1)
    U, L = H4B.chan_arrays(D)
    rows += month_rows("H4 breakout (nomzod)", H4B.run(D, U, L), 0.0075)
    rows += month_rows("H4 EMA20 reclaim", H4.run(D), 0.0075)
    # M15 breakout
    G = M15.Data(m1, 0.30, 0.50, dly=d1)
    rows += month_rows("M15 breakout (xarajat filtri)", M15.run(G), 0.005)
    # M5 London (needs M1 only)
    LDN.load = lambda: m1
    rows += month_rows("M5 London EMA9 reclaim", LDN.run(LDN.Data()), 0.0075)
    # N3 M1 swing + daily +-10%
    N3.load = lambda: m1
    DN = N3.Data()
    trn, ddn, pn = N3.run(DN)
    for mo, (a, b) in MONTHS.items():
        x = trn[(trn.date >= pd.Timestamp(a)) & (trn.date < pd.Timestamp(b))]
        dd = ddn[(ddn.index >= pd.Timestamp(a)) & (ddn.index < pd.Timestamp(b))]
        rows.append(dict(qoida="M1 swing + kunlik ±10% (N3)", oy=mo, savdolar=len(x), yutuq_pct=round(100 * float((x.R > 0).mean()), 1) if len(x) else np.nan, jami_R=round(float(x.R.sum()), 2),
                         o_rtacha_R=round(float(x.R.mean()), 3) if len(x) else np.nan, hisob_pct=round(100 * float((1 + dd).prod() - 1), 2), risk_pct=1.0))
    tab = pd.DataFrame(rows)
    # gold buy&hold on this data
    c = m1.close
    bh = {}
    prev = float(c[:"2026-08-31 23:59"].iloc[-1])
    for mo, (a, b) in MONTHS.items():
        last = float(c[:pd.Timestamp(b) - pd.Timedelta(minutes=1)].iloc[-1])
        bh[mo] = round(100 * (last / prev - 1), 2); prev = last
    out = ["# Oltin: bizning qoidalar 2026-09 va 2026-10 da (STRATEGY_OOS2026.md)\n",
           f"Ma'lumot: MT5 MetaQuotes-Demo XAUUSD M1 (UTC ga o'tkazilgan), D1 bias. Spred $0.30, yangilik filtri yo'q (2026 kalendari yo'q). **Tavsifiy; savdolar kam.**\n",
           f"Oltin buy&hold (shu ma'lumotda): 2026-09 {bh['2026-09']}%, 2026-10 {bh['2026-10']}% (Yahoo GC=F oy oxiri: −6.58% va −6.87%).\n",
           tab.to_markdown(index=False) + "\n"]
    out.append("Oylik oltin SMA10 overlay (N1 oltin qismi): ikkala oyda NAQD (SMA10 dan −0.6% va −7.0% pastda oy oxirida), natija 0% (oltin buy&hold −6.6% / −6.9%).\n")
    open("reports/oos2026_results.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
