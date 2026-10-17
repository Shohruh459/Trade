"""Run the pre-registered MTF2 test on Final (gold), FX and Dev; write reports/mtf2_results.md.  Usage: python -m backtest.mtf2_report"""
import glob

import numpy as np
import pandas as pd

from .mtf import build, load_gold_B
from .mtf2 import control_p, entry_index, net_r, prep_arrays, run_trades, signals, summarize, trade_path

FINAL = ("2023-01-01", "2025-02-28")
DEV = ("2018-01-22", "2022-12-31")
G_SPREAD, G_FIN, G_SPREAD_S, G_FIN_S = 0.30, 0.03, 0.50, 0.05


def fx_B(pair):
    fs = sorted(glob.glob(f"/tmp/claude-0/fx_m1/{pair}/*.parquet"))
    m1 = pd.concat(pd.read_parquet(f) for f in fs).sort_index()
    m1.columns = [c.lower() for c in m1.columns]
    m1 = m1[~m1.index.duplicated()]
    if m1.index.tz is not None:
        m1.index = m1.index.tz_convert("UTC").tz_localize(None)
    return build(m1[["open", "high", "low", "close"]])


def sub(sig, lo, hi, **flags):
    s = sig[(sig.t >= pd.Timestamp(lo)) & (sig.t <= pd.Timestamp(hi) + pd.Timedelta(days=1))]
    for k, v in flags.items():
        s = s[s[k] == v]
    return s


def control_table(B, a, lo, hi):
    h1 = B["H1"]
    ends, atr = h1["end"].to_numpy(), h1["atr"].to_numpy()
    rows = []
    for j in range(60, len(h1)):
        ts = pd.Timestamp(ends[j])
        if not (pd.Timestamp(lo) <= ts <= pd.Timestamp(hi) + pd.Timedelta(days=1)) or not (7 <= ts.hour < 20) or not np.isfinite(atr[j]) or atr[j] <= 0:
            continue
        i0 = entry_index(a, ts)
        if i0 is None:
            continue
        rdist, rec = 2.0 * atr[j], dict(t_ns=int(np.datetime64(ts).astype("datetime64[ns]").astype("int64")))
        for D, nm in ((1, "long"), (-1, "short")):
            px, tx, why, done = trade_path(i0, D, rdist, a)
            entry = a["m15_o"][i0]
            days = (tx - a["m15_start"][i0]) / np.timedelta64(1, "D")
            rec[f"r_{nm}"] = ((px - entry) * D - G_SPREAD - G_FIN * entry * days / 365.0) / rdist
            rec[f"x_{nm}"] = int(np.datetime64(tx).astype("datetime64[ns]").astype("int64"))
        rows.append(rec)
    return pd.DataFrame(rows)


def row(name, tr, spread, fin):
    return {"variant": name, **summarize(tr, spread, fin)}


def main():
    Bg = load_gold_B()
    ag = prep_arrays(Bg)
    sig = signals(Bg, DEV[0], FINAL[1])
    out = ["# MTF2 natijalari (reja: STRATEGY_MTF2.md, commit 1bce2b0)\n",
           "Qoida bitta, parametrlar rejadagidek, sozlanmagan. Final va FX bu qoida bilan birinchi marta sinaldi.\n"]
    # ---------------- Final (decision)
    main_sig = sub(sig, *FINAL, Lfull=1, T=1)
    trF = run_trades(main_sig, ag)
    sF = summarize(trF, G_SPREAD, G_FIN)
    sFs = summarize(trF, G_SPREAD_S, G_FIN_S)
    # ---------------- Dev (consistency)
    trD = run_trades(sub(sig, *DEV, Lfull=1, T=1), ag)
    sD = summarize(trD, G_SPREAD, G_FIN)
    # ---------------- timing control (Final)
    tab = control_table(Bg, ag, *FINAL)
    p_ctrl, ctrl_mean = control_p(tab, sF.get("mean_netR", 0.0), sF.get("N", 0), p_long=float((trF.D == 1).mean()) if len(trF) else 0.5)
    # ---------------- FX pooled
    fx_tr, fx_rows = [], {}
    for pair in ("eur_usd", "gbp_usd", "aud_usd"):
        B = fx_B(pair)
        a = prep_arrays(B)
        s = signals(B, "2020-04-22", "2025-12-31")
        tr = run_trades(sub(s, "2020-04-22", "2025-12-31", Lfull=1, T=1), a)
        tr = tr.assign(pair=pair)
        fx_tr.append(tr)
        fx_rows[pair] = summarize(tr, 0.0001, 0.0)
    trX = pd.concat(fx_tr, ignore_index=True)
    sX = summarize(trX, 0.0001, 0.0)
    sXs = summarize(trX, 0.00015, 0.0)
    out += ["\n## Asosiy qoida: natijalar\n",
            pd.DataFrame([{"set": "Final oltin 2023-01…2025-02 (QAROR)", **sF}, {"set": "Final, stress ($0.50, 5%)", **sFs}, {"set": "FX 3 juft birlashgan (QAROR)", **sX},
                          {"set": "FX, stress (1.5 pip)", **sXs}, {"set": "Dev oltin 2018-01…2022-12 (izchillik)", **sD}]).set_index("set").to_markdown() + "\n",
            "\nFX juftlar bo'yicha:\n", pd.DataFrame(fx_rows).T.to_markdown() + "\n",
            f"\nTasodifiy kirish nazorati (Final, shu chiqish qoidasi, 2000 marta): nazorat o'rtacha net R = {ctrl_mean:+.3f}; p (nazorat ≥ haqiqiy) = {p_ctrl:.4f}\n"]
    # ---------------- criteria
    pneg_dev = 1 - sD.get("p_one_sided", 0.5) if sD.get("N", 0) > 0 else np.nan
    C = {
        "C1 Final: o'rtacha net R>0, p<=0.10, N>=25": sF.get("N", 0) >= 25 and sF.get("mean_netR", -1) > 0 and sF.get("p_one_sided", 1) <= 0.10,
        "C2 Final stress: o'rtacha net R>0": sFs.get("mean_netR", -1) > 0,
        "C3 FX: o'rtacha net R>0, p<=0.10, N>=60": sX.get("N", 0) >= 60 and sX.get("mean_netR", -1) > 0 and sX.get("p_one_sided", 1) <= 0.10,
        "C4 Dev: ishonchli manfiy emas": not (sD.get("mean_netR", 0) < 0 and pneg_dev <= 0.10),
        "C5 Final: o'rtacha net R>=0.10, PF>=1.2, DD<=15%": sF.get("mean_netR", -1) >= 0.10 and sF.get("PF", 0) >= 1.2 and sF.get("maxDD_pct", 100) <= 15,
        "C6 Final: tasodifiy kirish nazoratida p<=0.10": p_ctrl <= 0.10,
    }
    out += ["\n## Oldindan belgilangan mezonlar\n", pd.DataFrame({"bajarildi": C}).to_markdown() + "\n", f"\n**Qaror: {'PASS' if all(C.values()) else 'FAIL'}**\n"]
    # ---------------- sensitivity (information only)
    sens = []
    for name, flt in (("filtrsiz F1", {}), ("faqat Lfull", {"Lfull": 1}), ("faqat T", {"T": 1}), ("Lfull+T+H4ok", {"Lfull": 1, "T": 1, "H4ok": 1})):
        sens.append(row(f"Final: {name}", run_trades(sub(sig, *FINAL, **flt), ag), G_SPREAD, G_FIN))
    # trailing distance 3 ATR (R unit stays 2 ATR): need per-trade trail -> run via loop
    rows3 = []
    busy = None
    for e in main_sig.sort_values("t").itertuples():
        if busy is not None and np.datetime64(e.t) < busy:
            continue
        i0 = entry_index(ag, e.t)
        if i0 is None:
            continue
        rd = 2.0 * e.atr
        px, tx, why, done = trade_path(i0, e.D, rd, ag, trail=3.0 * e.atr)
        entry = ag["m15_o"][i0]
        rows3.append(dict(t=e.t, D=e.D, entry=entry, exit=px, rdist=rd, gross=(px - entry) * e.D, days=(tx - ag["m15_start"][i0]) / np.timedelta64(1, "D"), reason=why, h1_bars=done, exit_time=tx))
        busy = tx
    sens.append(row("Final: asosiy, trailing 3 ATR", pd.DataFrame(rows3), G_SPREAD, G_FIN))
    sens.append(row("Final: asosiy, long", trF[trF.D == 1], G_SPREAD, G_FIN))
    sens.append(row("Final: asosiy, short", trF[trF.D == -1], G_SPREAD, G_FIN))
    out += ["\n## Sezgirlik (faqat ma'lumot uchun, qarorga ta'sir qilmaydi)\n", pd.DataFrame(sens).set_index("variant").to_markdown() + "\n"]
    if len(trF):
        yr = trF.assign(net=net_r(trF, G_SPREAD, G_FIN)).groupby(trF.t.dt.year).net.agg(["count", "mean"]).round(3)
        out += ["\nFinal: yillar bo'yicha (bitimlar soni, o'rtacha net R):\n", yr.to_markdown() + "\n",
                f"\nChiqish turlari (Final): {trF.reason.value_counts().to_dict()}; o'rtacha ushlab turish {trF.days.mean()*24:.0f} soat.\n"]
    open("reports/mtf2_results.md", "w").write("\n".join(out))
    trF.assign(net_R=net_r(trF, G_SPREAD, G_FIN)).to_csv("reports/mtf2_trades_final.csv", index=False)
    trX.assign(net_R=net_r(trX, 0.0001, 0.0)).to_csv("reports/mtf2_trades_fx.csv", index=False)
    print("\n".join(out))


if __name__ == "__main__":
    main()
