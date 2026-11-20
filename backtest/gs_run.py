"""GoldStructureEA: the single confirmatory run (STRATEGY_GOLDSTRUCTURE.md v3, frozen) + descriptive extras.

Usage:
  python -m backtest.gs_run --smoke    # development smoke test on 2018-04..2018-07 only (prints funnel; no files; no parameter changes allowed)
  python -m backtest.gs_run            # confirmatory run -> reports/goldstructure_results.md (refuses to overwrite an existing report)
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from backtest.goldstructure import CFG, S_VARIANTS, Ctx, load_news, random_control, run_sim
from backtest.ldn import load

REPORT = Path("reports/goldstructure_results.md")
START, END = "2018-04-01", "2025-03-01"
PERIODS = {"Dev 2018-04..2021-12": ("2018-04-01", "2022-01-01"), "Val 2022-01..2023-12": ("2022-01-01", "2024-01-01"), "Final 2024-01..2025-02": ("2024-01-01", "2025-03-01"), "Hammasi 2018-04..2025-02": (START, END)}


def clustered(x: pd.DataFrame):
    n = len(x)
    if n < 3:
        return np.nan, np.nan
    m = x.R.mean()
    wk = x.entry.dt.strftime("%G-%V")
    se = np.sqrt(((x.R - m).groupby(wk).sum() ** 2).sum()) / n
    return m, (float(1 - norm.cdf(m / se)) if se > 0 else np.nan)


def metrics(x: pd.DataFrame, risk=0.01):
    if len(x) == 0:
        return dict(N=0)
    m, p = clustered(x)
    pf = x.R[x.R > 0].sum() / -x.R[x.R < 0].sum() if (x.R < 0).any() else np.nan
    eq = np.cumprod(1 + risk * x.sort_values("entry").R.to_numpy())
    pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
    mo = x.assign(mo=x.entry.dt.to_period("M")).groupby("mo").R.apply(lambda r: float(np.prod(1 + risk * r.to_numpy()) - 1))
    yrs = max((x.entry.max() - x.entry.min()).days / 365.25, 1e-9)
    return dict(N=len(x), per_year=round(len(x) / yrs, 1), win_pct=round(100 * float((x.R > 0).mean()), 1), meanR=round(float(m), 4), PF=round(float(pf), 3) if pf == pf else np.nan, p_one=round(p, 3) if p == p else np.nan,
                ret_pct=round(100 * (eq[-1] - 1), 1), maxDD_pct=round(100 * float(((pk - eq) / pk).max()), 1), pos_months_pct=round(100 * float((mo > 0).mean()), 1), worst_month_pct=round(100 * float(mo.min()), 1),
                hold_med_min=round(float(x.hold_min.median()), 0))


def period_table(tr):
    rows = []
    for name, (a, b) in PERIODS.items():
        x = tr[(tr.entry >= pd.Timestamp(a)) & (tr.entry < pd.Timestamp(b))] if len(tr) else tr
        rows.append({"davr": name, **metrics(x)})
    return pd.DataFrame(rows)


def run_cfg(m1, cfg, news, a=START, b=END):
    t0 = time.time()
    ctx = Ctx(m1, cfg, news)
    tr, f = run_sim(ctx, a, b)
    return ctx, tr, f, round(time.time() - t0, 0)


def smoke():
    m1 = load()
    m1 = m1[(m1.index >= "2018-01-02") & (m1.index < "2018-08-01")]
    cfg = dict(CFG)
    ctx, tr, f, sec = run_cfg(m1, cfg, load_news(), "2018-04-01", "2018-08-01")
    print("smoke funnel:", f, f"({sec}s)")
    print(tr[["entry", "d", "R", "reason", "s", "atr", "hold_min"]].head(12).to_string() if len(tr) else "no trades")
    print("zone statuses over slice:", np.bincount(ctx.st15, minlength=5))


def main():
    if "--smoke" in sys.argv:
        smoke()
        return
    if REPORT.exists():
        sys.exit(f"{REPORT} already exists: the confirmatory run is performed ONCE (test plan section 6). Aborting.")
    t_all = time.time()
    m1 = load()
    news_all = load_news()
    out = ["# GoldStructureEA: tasdiqlovchi sinov natijalari (STRATEGY_GOLDSTRUCTURE.md v3, muzlatilgan)\n",
           "Bitta tasdiqlovchi ishga tushirish; parametrlar muzlatilgan SPEC (v3) bo'yicha, hech biri o'zgartirilmagan. Ishlab chiqish davrida faqat 2018-04..2018-07 kesimida smoke test (kod xatolarini tuzatish uchun) o'tkazilgan.\n",
           "Birliklar: narx $/oz; spred to'liq aylanma ($/oz); 1 lot = 100 oz. Risk 1% hisob equity; net R = (foyda − xarajatlar)/s.\n"]
    # ---- ASOSIY
    ctx, tr, f, sec = run_cfg(m1, CFG, news_all)
    out.append(f"## 1. ASOSIY ssenariy (spred $0.30, komissiya 0, slippage 0) — hisoblash {sec}s\n")
    pt = period_table(tr)
    out.append(pt.to_markdown(index=False) + "\n")
    out.append("### Filtrlar voronkasi (hamma davr)\n" + pd.DataFrame([f]).T.rename(columns={0: "soni"}).to_markdown() + "\n")
    if len(tr):
        out.append("### Chiqish sabablari\n" + tr.reason.map({1: "TP", 2: "SL", 3: "kunlik limit (−4%)", 4: "NY 16:30 majburiy yopish", 5: "ma'lumot tugadi"}).value_counts().to_frame("soni").to_markdown() + "\n")
        yr = tr.groupby(tr.entry.dt.year).R.agg(["count", "mean"]).round(3)
        out.append("### Yillar bo'yicha\n" + yr.to_markdown() + "\n")
        # news-filter completeness slices (test plan section 3)
        sl = {"F1: filtr to'liq (2018-04..2018-12 va 2023-01..2025-02)": tr[((tr.entry >= "2018-04-01") & (tr.entry < "2019-01-01")) | (tr.entry >= "2023-01-01")],
              "F2: filtr to'liq emas (GDP bo'shliqlari, 2019-01..2022-12)": tr[(tr.entry >= "2019-01-01") & (tr.entry < "2023-01-01")]}
        out.append("### Yangilik filtri qismlari\n" + pd.DataFrame([{"qism": k, **metrics(v)} for k, v in sl.items()]).to_markdown(index=False) + "\n")
    # ---- STRESS & COMMISSION
    cfg_s = dict(CFG, spread=0.50, slip_entry=0.10, slip_sl=0.10)
    _, tr_s, f_s, _ = run_cfg(m1, cfg_s, news_all)
    out.append("## 2. STRESS ssenariy (spred $0.50, slippage kirish $0.10 + SL $0.10)\n" + period_table(tr_s).to_markdown(index=False) + "\n")
    cfg_c = dict(CFG, commission=0.07)
    _, tr_c, _, _ = run_cfg(m1, cfg_c, news_all)
    out.append("## 3. KOMISSIYA sezgirligi (asosiy + $0.07/oz = $7/lot)\n" + period_table(tr_c).to_markdown(index=False) + "\n")
    # ---- RANDOM CONTROL
    n_draws = 1000
    rc, n_elig = random_control(ctx, tr, START, END, n_draws)
    real_mean = tr.R.mean() if len(tr) else np.nan
    if len(rc):
        p_rc = float((rc >= real_mean).mean())
        out.append(f"## 4. Tasodifiy kirish nazorati ({len(rc)}/{n_draws} to'plam; eligible M5 barlar {n_elig})\nReal o'rtacha net R {real_mean:.4f}; tasodifiy o'rtacha {rc.mean():.4f} (5–95%: {np.percentile(rc,5):.4f} … {np.percentile(rc,95):.4f}); **p = {p_rc:.3f}**\n")
    else:
        p_rc = np.nan
        out.append(f"## 4. Tasodifiy kirish nazorati: o'tkazib bo'lmadi (real N={len(tr)}, eligible={n_elig})\n")
    # ---- CRITERIA
    allp = pt[pt.davr.str.startswith("Hammasi")].iloc[0]
    N = int(allp.N) if "N" in allp else 0
    g1 = N >= 100 and allp.meanR > 0 and allp.p_one <= 0.10 if N else False
    ps = period_table(tr_s)
    g2 = bool(len(tr_s) and ps[ps.davr.str.startswith("Hammasi")].iloc[0].meanR > 0)
    per3 = pt[~pt.davr.str.startswith("Hammasi")]
    eval_rows = per3[per3.N >= 15]
    g3 = len(eval_rows) >= 2 and bool((eval_rows.meanR > 0).all())
    g4 = bool(N and allp.PF >= 1.2)
    g5 = bool(p_rc == p_rc and p_rc <= 0.10)
    g6 = bool(N and allp.maxDD_pct <= 20)
    crit = {"G1 N>=100, meanR>0, p<=0.10": g1, "G2 stress meanR>0": g2, "G3 Dev/Val/Final meanR>0 (N>=15, kamida 2 davr)": g3, "G4 profit factor >= 1.2": g4, "G5 tasodifiy nazorat p<=0.10": g5, "G6 maxDD <= 20%": g6}
    if N < 100:
        verdict = f"XULOSASIZ (N={N} < 100): qoida o'tmagan hisoblanadi; parametr o'zgartirilmaydi"
    else:
        verdict = "PASS (dastlabki)" if all(crit.values()) else "FAIL"
    out.append("## 5. Qaror mezonlari (oltin, qaror davri 2018-04..2025-02)\n" + "\n".join(f"- {k}: {'OK' if v else 'YO`Q'}" for k, v in crit.items()) + f"\n\n**Xulosa: {verdict}**\n")
    # ---- SENSITIVITY (descriptive only)
    sens = []
    variants = [("A8 (a): diapazon >= 1.0 ATR", dict(impulse_mode="range")), ("A8 (c): tana >= 0.7 ATR", dict(impulse_mult=0.7)), ("sessiya S2", dict(sessions=S_VARIANTS["S2"])), ("sessiya S3", dict(sessions=S_VARIANTS["S3"])),
                ("sessiya S4", dict(sessions=S_VARIANTS["S4"])), ("NY 16:30 yopishsiz (swap bilan)", dict(force_close=False)), ("zona = tana", dict(zone_body=True)), ("M15 swing k=2", dict(kM15=2)), ("M15 swing k=4", dict(kM15=4)),
                ("P-M oynasi 1 bar", dict(confirm_gap=0)), ("A1 stop filtrisiz", dict(use_a1=False)), ("MSS episodni tugatuvchi barda ham (spec talqini)", dict(mss_on_exit=True)), ("zona muddati 48", dict(zone_age_bars=48)), ("zona muddati 192", dict(zone_age_bars=192)), ("faqat BUY", dict(side=1)), ("faqat SELL", dict(side=-1))]
    for name, kw in variants:
        try:
            _, trv, fv, _ = run_cfg(m1, dict(CFG, **kw), news_all)
            sens.append({"variant": name, **{k: v for k, v in metrics(trv).items() if k in ("N", "per_year", "win_pct", "meanR", "PF", "p_one", "ret_pct", "maxDD_pct")}})
        except Exception as e:  # keep the report going; record the failure
            sens.append({"variant": name, "N": f"xato: {e}"})
    news_nogdp = load_news(families=("NFP", "CPI", "FOMC"))
    _, trg, _, _ = run_cfg(m1, CFG, news_nogdp)
    sens.append({"variant": "yangilik filtri GDP siz", **{k: v for k, v in metrics(trg).items() if k in ("N", "per_year", "win_pct", "meanR", "PF", "p_one", "ret_pct", "maxDD_pct")}})
    _, trn, _, _ = run_cfg(m1, CFG, None)
    sens.append({"variant": "yangilik filtrisiz", **{k: v for k, v in metrics(trn).items() if k in ("N", "per_year", "win_pct", "meanR", "PF", "p_one", "ret_pct", "maxDD_pct")}})
    out.append("## 6. Sezgirlik (faqat tavsifiy, qarorga ta'sir qilmaydi)\n" + pd.DataFrame(sens).to_markdown(index=False) + "\n")
    # ---- DESCRIPTIVE 2026-09/10 (MetaQuotes demo M1; news filter off)
    try:
        import backtest.oos2026 as O
        mq = O.load_m1()
        _, t26, f26, _ = run_cfg(mq, CFG, None, "2026-09-01", "2026-11-01")
        out.append("## 7. Tavsifiy: 2026-09 va 2026-10 (MetaQuotes demo M1, yangilik filtri yo'q; qarorga kirmaydi)\n" + (pd.DataFrame([metrics(t26)]).to_markdown(index=False) if len(t26) else "Savdo yo'q.") + f"\n\nVoronka: {f26}\n")
    except Exception as e:
        out.append(f"## 7. Tavsifiy 2026: bajarilmadi ({e})\n")
    out.append(f"\nJami hisoblash vaqti: {round(time.time()-t_all)} s. Kod: backtest/goldstructure.py, backtest/gs_run.py.\n")
    REPORT.write_text("\n".join(out))
    if len(tr):
        tr.to_csv("reports/goldstructure_trades.csv", index=False)
    print("\n".join(out))


if __name__ == "__main__":
    main()
