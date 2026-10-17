"""Post-hoc supplementary check (NOT used for selection): same 40 variants with the 15% drawdown stop disabled,
to see whether truncation by the stop hid an edge. Usage: python -m backtest.supplement
"""
from dataclasses import replace

import pandas as pd

from .engine import metrics
from .explore import ALL, EXITS
from .protocol import INSTRUMENTS, segment


def main():
    lines = ["\n## Qo'shimcha (post-hoc) tekshiruv: drawdown stop o'chirilgan\n",
             "Bu tanlov uchun ishlatilmaydi. Maqsad: 15% to'xtash qoidasi namunani qisqartirib, foydali strategiyani yashirib qo'ymaganini tekshirish.\n"]
    for name, c in INSTRUMENTS.items():
        df = pd.read_csv(c["csv"], index_col=0, parse_dates=True)
        rows = []
        for sname, fn in ALL.items():
            sig, atr = fn(df)
            for ename, over in EXITS.items():
                cfg = replace(c["cfg"], max_drawdown=1.0, **over)
                mi = metrics(segment(df, sig, atr, cfg, c["is_range"])[0], cfg.start_balance)
                mo = metrics(segment(df, sig, atr, cfg, c["oos_range"])[0], cfg.start_balance)
                rows.append({"variant": f"{sname} {ename}", "IS_tr": mi.get("trades", 0), "IS_PF": mi.get("profit_factor"), "IS_net%": mi.get("net_pct"),
                             "IS_DD%": mi.get("max_dd_pct"), "OOS_tr": mo.get("trades", 0), "OOS_PF": mo.get("profit_factor"),
                             "OOS_net%": mo.get("net_pct"), "OOS_DD%": mo.get("max_dd_pct")})
        r = pd.DataFrame(rows)
        r.to_csv(f"reports/supplement_{name}_nostop.csv", index=False)
        is_ok = r[(r.IS_PF > 1.1) & (r.IS_tr >= 200)]
        lines += [f"\n### {name}\n", f"- IS PF>1.1 va ≥200 bitim: **{len(is_ok)}** variant; IS PF>1.0: {int((r.IS_PF > 1.0).sum())} / 40; "
                  f"OOS PF>1.0: {int((r.OOS_PF > 1.0).sum())} / 40; OOS PF>1.3: {int((r.OOS_PF > 1.3).sum())} / 40.\n",
                  "Eng yaxshi 5 ta (IS PF bo'yicha):\n", r.sort_values("IS_PF", ascending=False).head(5).to_markdown(index=False) + "\n"]
    open("reports/final_summary.md", "a").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
