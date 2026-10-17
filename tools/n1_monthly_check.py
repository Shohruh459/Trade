"""Monthly N1 check: 5-asset SMA10 trend portfolio (STRATEGY_NEXT.md section 3) with a locked forward-test log.

Rules are the pre-registered ones; nothing is tuned. Each asset: long if month-end level > mean of last 10 month-end levels, else cash.
Weight 1/N per asset held (N = number of assets in the universe); the rest is cash. Cost 10 bp x sum|weight change|.
Equity uses the S&P 500 PRICE index (backtest used total return; dividends ignored here), bond uses a total-return index built from the 10y yield
(duration 7.5), gold/WTI/natgas use prices.
Usage:
  python tools/n1_monthly_check.py
  python tools/n1_monthly_check.py --add 2026-10 --spx 7800 --y10 4.5 --gold 4350 --wti 90 --gas 3.1   # any subset of fields
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PRICES, LOG, LATEST = ROOT / "forward_test/n1_prices.csv", ROOT / "forward_test/n1_log.csv", ROOT / "forward_test/n1_latest.md"
FORWARD_START = pd.Period("2026-09", "M")
COST = 0.001
DUR = 7.5
ASSETS = ["equity", "bond", "gold", "oil", "natgas"]
COLS = {"spx": "equity", "y10": "bond", "gold": "gold", "wti": "oil", "natgas": "natgas"}


def load_prices(path=PRICES):
    df = pd.read_csv(path)
    df.index = pd.PeriodIndex(df["month"], freq="M")
    return df.sort_index()


def levels(df: pd.DataFrame) -> pd.DataFrame:
    y = df["y10"].astype(float)
    r_b = y.shift(1) / 1200 - DUR * (y - y.shift(1)) / 100
    bond = (1 + r_b.fillna(0)).cumprod().where(y.notna())
    L = pd.DataFrame({"equity": df["spx"].astype(float), "bond": bond, "gold": df["gold"].astype(float), "oil": df["wti"].astype(float), "natgas": df["natgas"].astype(float)})
    return L


def state_table(L: pd.DataFrame) -> pd.DataFrame:
    sma = L.rolling(10).mean()
    sig = (L > sma).astype(float).where(sma.notna() & L.notna())
    out = {}
    for a in ASSETS:
        out[f"sig_{a}"] = sig[a]
        out[f"dist_{a}"] = (L[a] / sma[a] - 1) * 100
    t = pd.DataFrame(out)
    # N = assets with a defined signal (all five once histories are long enough)
    n = sig.notna().sum(axis=1)
    for a in ASSETS:
        t[f"w_{a}"] = (sig[a].fillna(0) / n.replace(0, np.nan))
    t["w_cash"] = 1 - t[[f"w_{a}" for a in ASSETS]].sum(axis=1)
    t["complete"] = n == len(ASSETS)
    return t


def update_log(t: pd.DataFrame, L: pd.DataFrame, log_path=LOG) -> pd.DataFrame:
    """Locked snapshots for complete months >= FORWARD_START (never overwritten); realized next-month returns filled when known."""
    wcols = [f"w_{a}" for a in ASSETS]
    cols = ["month"] + [f"sig_{a}" for a in ASSETS] + wcols + ["port_ret_pct", "ew_ret_pct"]
    log = pd.read_csv(log_path) if Path(log_path).exists() else pd.DataFrame(columns=cols)
    have = set(log["month"].astype(str))
    for p, r in t.iterrows():
        if p >= FORWARD_START and str(p) not in have and r.complete:
            log.loc[len(log)] = [str(p)] + [int(r[f"sig_{a}"]) for a in ASSETS] + [round(r[c], 4) for c in wcols] + [np.nan, np.nan]
    log["month"] = log["month"].astype(str)
    log = log.sort_values("month").reset_index(drop=True)
    for i in range(len(log)):
        m = pd.Period(log.month[i], "M")
        if (m + 1) in L.index and np.isnan(log.port_ret_pct[i]) and L.loc[m + 1].notna().all():
            r = (L.loc[m + 1] / L.loc[m] - 1).to_numpy()
            w = log.loc[i, wcols].to_numpy(float)
            prev = log.loc[i - 1, wcols].to_numpy(float) if i > 0 else np.zeros(len(ASSETS))
            log.loc[i, "port_ret_pct"] = round((float(w @ r) - COST * np.abs(w - prev).sum()) * 100, 3)
            log.loc[i, "ew_ret_pct"] = round(float(r.mean()) * 100, 3)
    log.to_csv(log_path, index=False)
    return log


def forward_summary(log: pd.DataFrame) -> dict:
    done = log.dropna(subset=["port_ret_pct"])
    if len(done) == 0:
        return {"n_months": 0}
    def dd(r):
        eq = np.cumprod(1 + r.to_numpy()); pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
        return round(float(((pk - eq) / pk).max() * 100), 1)
    p, b = done.port_ret_pct / 100, done.ew_ret_pct / 100
    return dict(n_months=len(done), port_total_pct=round(((1 + p).prod() - 1) * 100, 1), ew_total_pct=round(((1 + b).prod() - 1) * 100, 1), port_maxdd_pct=dd(p), ew_maxdd_pct=dd(b),
                pos_months_pct=round(float((p > 0).mean() * 100), 1))


def report(t: pd.DataFrame, log: pd.DataFrame) -> str:
    ok = t[t.complete]
    if ok.empty:
        return "Ma'lumot yetarli emas (har aktiv uchun kamida 10 oy kerak)."
    m, cur = ok.index[-1], ok.iloc[-1]
    prev = ok.iloc[-2] if len(ok) > 1 else None
    names = {"equity": "Aksiya (S&P 500)", "bond": "Obligatsiya (10y)", "gold": "Oltin", "oil": "Neft (WTI)", "natgas": "Tabiiy gaz"}
    lines = [f"# N1 oylik tekshiruv: {m}", "", "| Aktiv | Holat | SMA10 dan % | Vazn | O'zgarish |", "|---|---|---|---|---|"]
    changes = []
    for a in ASSETS:
        s = int(cur[f"sig_{a}"])
        chg = "" if prev is None else ("" if int(prev[f"sig_{a}"]) == s else ("NAQDDAN → LONG" if s else "LONG → NAQD"))
        if chg:
            changes.append(f"{names[a]}: {chg}")
        lines.append(f"| {names[a]} | {'LONG' if s else 'NAQD'} | {cur[f'dist_{a}']:+.1f} | {cur[f'w_{a}']*100:.0f}% | {chg} |")
    lines += [f"| Naqd | | | {cur['w_cash']*100:.0f}% | |", "",
              f"- **Harakat kerak bo'lgan o'zgarishlar:** {'; '.join(changes) if changes else 'yo`q (oldingi oy holati saqlanadi)'}.",
              "- Qoida: faqat OY OXIRIDA tekshiring; har aktiv uchun oy oxirgi yopilish narxi. Oraliq kunlarda qaror qilmang.",
              f"- Forward kuzatuv (2026-09 dan): {forward_summary(log) if forward_summary(log)['n_months'] else 'hali realizatsiya qilingan oy yo`q'}", "",
              "Ogohlantirish: moliyaviy maslahat emas. Tarixiy qism oylik o'rtacha narxlar; oy oxiri yopilishida natija biroz farq qiladi. Neft/gaz uchun spot narx (fyuchers/ETF roll xarajati hisobda yo'q). Avval qog'ozda kuzating."]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", metavar="YYYY-MM")
    for k in COLS:
        ap.add_argument(f"--{k}", type=float)
    a = ap.parse_args()
    df = load_prices()
    if a.add:
        m = pd.Period(a.add, "M")
        if m not in df.index:
            df.loc[m] = [str(m)] + [np.nan] * (len(df.columns) - 1)
        for k in COLS:
            v = getattr(a, k)
            if v is not None:
                df.loc[m, k] = v
        df.loc[m, "source"] = "user"
        df = df.sort_index()
        df.reset_index(drop=True).to_csv(PRICES, index=False)
    L = levels(df)
    t = state_table(L)
    log = update_log(t, L)
    txt = report(t, log)
    LATEST.write_text(txt)
    print(txt)


if __name__ == "__main__":
    main()
