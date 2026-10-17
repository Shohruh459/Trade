"""Monthly gold check: SMA10 overlay state, 10% allocation reminder, seasonality and momentum, plus a locked forward-test log.

Rules are the pre-registered ones from STRATEGY_PORTFOLIO.md / STRATEGY_FORWARD.md. Nothing here is tuned.
Usage:
  python tools/gold_monthly_check.py                      # print report, update forward_test/log.csv and forward_test/latest.md
  python tools/gold_monthly_check.py --add 2026-10 4350   # add/replace a month-end close price (source 'user'), then report
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PRICES, LOG, LATEST = ROOT / "forward_test/gold_prices.csv", ROOT / "forward_test/log.csv", ROOT / "forward_test/latest.md"
FORWARD_START = pd.Period("2026-09", "M")      # first month-end snapshot that counts for the forward test
SWITCH_COST = 0.001
SEASON = (9, 10, 11, 12, 1, 2)


def load_prices(path=PRICES):
    df = pd.read_csv(path)
    df.index = pd.PeriodIndex(df["month"], freq="M")
    return df.sort_index()


def state_table(P: pd.Series) -> pd.DataFrame:
    sma = P.rolling(10).mean()
    sig = (P > sma).astype(float).where(sma.notna())
    t = pd.DataFrame({"price": P, "sma10": sma, "signal": sig})
    t["dist_pct"] = (P / sma - 1) * 100
    t["mom12_pct"] = (P / P.shift(12) - 1) * 100
    t["season_next"] = [int((p + 1).month in SEASON) for p in P.index]
    chg = t.signal.diff().abs() > 0
    last = None
    since = []
    for i, p in enumerate(t.index):
        if chg.iloc[i]:
            last = i
        since.append(i - last if last is not None else np.nan)
    t["months_since_switch"] = since
    return t


def update_log(t: pd.DataFrame, log_path=LOG) -> pd.DataFrame:
    """Append locked snapshots for months >= FORWARD_START (never overwritten); fill realized next-month returns when available."""
    cols = ["month", "price", "sma10", "signal", "dist_pct", "mom12_pct", "season_next"]
    log = pd.read_csv(log_path) if Path(log_path).exists() else pd.DataFrame(columns=cols + ["next_ret_pct", "overlay_ret_pct"])
    have = set(log["month"].astype(str))
    for p, r in t.iterrows():
        if p >= FORWARD_START and str(p) not in have and not np.isnan(r.signal):
            log.loc[len(log)] = [str(p), r.price, round(r.sma10, 2), int(r.signal), round(r.dist_pct, 2), round(r.mom12_pct, 2) if not np.isnan(r.mom12_pct) else np.nan, int(r.season_next), np.nan, np.nan]
    log["month"] = log["month"].astype(str)
    log = log.sort_values("month").reset_index(drop=True)
    for i in range(len(log)):
        m = pd.Period(log.month[i], "M")
        if (m + 1) in t.index and np.isnan(log.next_ret_pct[i]):
            r = t.price[m + 1] / t.price[m] - 1
            prev_sig = log.signal[i - 1] if i > 0 else log.signal[i]
            log.loc[i, "next_ret_pct"] = round(r * 100, 3)
            log.loc[i, "overlay_ret_pct"] = round((log.signal[i] * r - SWITCH_COST * abs(log.signal[i] - prev_sig)) * 100, 3)
    log.to_csv(log_path, index=False)
    return log


def forward_summary(log: pd.DataFrame) -> dict:
    done = log.dropna(subset=["next_ret_pct"])
    out = {"n_months": len(done)}
    if len(done) == 0:
        return out
    bh, ov = done.next_ret_pct / 100, done.overlay_ret_pct / 100
    def dd(r):
        eq = np.cumprod(1 + r.to_numpy()); pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
        return float(((pk - eq) / pk).max() * 100)
    out.update(bh_total_pct=round(((1 + bh).prod() - 1) * 100, 1), overlay_total_pct=round(((1 + ov).prod() - 1) * 100, 1), bh_maxdd_pct=round(dd(bh), 1), overlay_maxdd_pct=round(dd(ov), 1))
    s, o = done[done.season_next == 1].next_ret_pct, done[done.season_next == 0].next_ret_pct
    out.update(season_months=len(s), nonseason_months=len(o), season_mean_pct=round(float(s.mean()), 2) if len(s) else None, nonseason_mean_pct=round(float(o.mean()), 2) if len(o) else None)
    return out


def report(t: pd.DataFrame, log: pd.DataFrame) -> str:
    cur = t.dropna(subset=["signal"]).iloc[-1]
    m = t.dropna(subset=["signal"]).index[-1]
    state = "LONG (oltin ushlanadi)" if cur.signal == 1 else "NAQD (oltin sleeve naqdga o'tgan)"
    fs = forward_summary(log)
    lines = [f"# Oltin oylik tekshiruv: {m}", "",
             f"- Oxirgi narx: ${cur.price:,.0f}; SMA10: ${cur.sma10:,.0f}; narx SMA10 dan {cur.dist_pct:+.1f}%.",
             f"- **SMA10 holati: {state}**; oxirgi o'zgarishdan beri {int(cur.months_since_switch) if not np.isnan(cur.months_since_switch) else '?'} oy.",
             f"- 12 oylik momentum: {cur.mom12_pct:+.1f}%. Keyingi oy mavsumiy oyga ({'sentyabr–fevral' if cur.season_next else 'mart–avgust'}) to'g'ri keladi.",
             "- Portfel eslatmasi: diversifikatsiya uchun oltin ulushi ~10% (60/40 portfelda, mezondan o'tgan); 20% emas.",
             "- Qoida: faqat OY OXIRIDA tekshiring, oy oxirgi yopilish narxi bilan. Oraliq kunlarda qaror qilmang.",
             f"- Forward kuzatuv (2026-09 dan): {fs if fs['n_months'] else 'hali realizatsiya qilingan oy yo`q'}",
             "", "Ogohlantirish: moliyaviy maslahat emas. Qoida oylik O'RTACHA narxlar ma'lumotida sinalgan, oy oxiri yopilishida natija biroz farq qilishi mumkin; avval qog'ozda/demo kuzating."]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", nargs=2, metavar=("YYYY-MM", "PRICE"))
    a = ap.parse_args()
    df = load_prices()
    if a.add:
        m = pd.Period(a.add[0], "M")
        df.loc[m, ["month", "price", "source"]] = [str(m), float(a.add[1]), "user"]
        df = df.sort_index()
        df.reset_index(drop=True).to_csv(PRICES, index=False)
    P = df["price"].astype(float)
    t = state_table(P)
    log = update_log(t)
    txt = report(t, log)
    LATEST.write_text(txt)
    print(txt)


if __name__ == "__main__":
    main()
