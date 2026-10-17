"""MTF2 rule test (STRATEGY_MTF2.md, pre-registered, commit 1bce2b0). One rule, nothing tuned.

Entry: H1 EMA20/50 flip (07-20 UTC) with Lfull (M1,M5,M15 agree) and T (ER_H1>=0.30); next M15 open; R = 2*ATR_H1; initial stop 2 ATR;
trailing stop (best H1 extreme since entry -/+ 2 ATR) updated after each completed H1 bar; exits: stop, opposite H1 flip (next M15 open),
96 completed H1 bars (next M15 open). Cost: spread + 3% p.a. financing on entry price (gold); FX: spread only.
Usage: python -m backtest.mtf2
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from .mtf import cluster_mean_test, last_idx

NS_DAY = 86_400 * 10 ** 9
H1_MAX = 96


def trade_path(i0, D, rdist, a, trail=None, tp_r=None, max_h1=H1_MAX):
    """a: dict of numpy arrays: m15_start,m15_end (datetime64[ns]), m15_o,h,l; h1_start,h1_end,h1_h,h1_l,h1_d; end2h1 (dict m15 end ns -> h1 index).
    Returns (exit_price, exit_time(ns), reason, n_h1_done)."""
    trail = rdist if trail is None else trail
    ms, me, mo, mh, ml = a["m15_start"], a["m15_end"], a["m15_o"], a["m15_h"], a["m15_l"]
    entry, t0 = mo[i0], ms[i0]
    stop = entry - D * rdist
    tp = entry + D * tp_r * rdist if tp_r else None
    best = -np.inf if D == 1 else np.inf
    done, pending = 0, None
    n = len(mo)
    for k in range(i0, n):
        if pending:
            return mo[k], ms[k], pending, done
        if D == 1:
            if k > i0 and mo[k] <= stop:
                return mo[k], ms[k], "stop_gap", done
            if ml[k] <= stop:
                return stop, ms[k], "stop", done
            if tp is not None and mh[k] >= tp:
                return tp, ms[k], "tp", done
        else:
            if k > i0 and mo[k] >= stop:
                return mo[k], ms[k], "stop_gap", done
            if mh[k] >= stop:
                return stop, ms[k], "stop", done
            if tp is not None and ml[k] <= tp:
                return tp, ms[k], "tp", done
        j = a["end2h1"].get(int(me[k].astype("int64")), -1)
        if j >= 0 and a["h1_start"][j] >= t0:
            done += 1
            if D == 1:
                best = max(best, a["h1_h"][j])
                stop = max(stop, best - trail)
            else:
                best = min(best, a["h1_l"][j])
                stop = min(stop, best + trail)
            if a["h1_d"][j] == -D:
                pending = "flip"
            elif done >= max_h1:
                pending = "time"
    return mo[n - 1], ms[n - 1], "end", done


def prep_arrays(B):
    m15, h1 = B["M15"], B["H1"]
    end2h1 = {int(e.astype("int64")): j for j, e in enumerate(h1["end"].to_numpy())}
    return dict(m15_start=m15.index.to_numpy(), m15_end=m15["end"].to_numpy(), m15_o=m15["open"].to_numpy(float), m15_h=m15["high"].to_numpy(float),
                m15_l=m15["low"].to_numpy(float), h1_start=h1.index.to_numpy(), h1_end=h1["end"].to_numpy(), h1_h=h1["high"].to_numpy(float),
                h1_l=h1["low"].to_numpy(float), h1_d=h1["d"].to_numpy(), end2h1=end2h1)


def signals(B, lo, hi):
    """All F1 flips (07-20 UTC) with Lfull / T / H4ok flags (filters applied by the caller)."""
    h1 = B["H1"]
    d, er, atr, ends = h1["d"].to_numpy(), h1["er"].to_numpy(), h1["atr"].to_numpy(), h1["end"].to_numpy()
    rows = []
    for j in range(60, len(h1)):
        ts = pd.Timestamp(ends[j])
        if not (pd.Timestamp(lo) <= ts <= pd.Timestamp(hi) + pd.Timedelta(days=1)) or not (7 <= ts.hour < 20):
            continue
        if d[j] == 0 or d[j - 1] == 0 or d[j] == d[j - 1]:
            continue
        D = int(d[j])
        ds = {x: int(B[x]["d"].iloc[last_idx(B[x], ts)]) for x in ("M1", "M5", "M15", "H4")}
        if not (np.isfinite(er[j]) and np.isfinite(atr[j]) and atr[j] > 0):
            continue
        rows.append(dict(t=ts, D=D, Lfull=int(ds["M1"] == D and ds["M5"] == D and ds["M15"] == D), T=int(er[j] >= 0.30), H4ok=int(ds["H4"] == D), atr=float(atr[j]), j=j))
    return pd.DataFrame(rows)


def entry_index(a, t):
    i0 = int(np.searchsorted(a["m15_start"], np.datetime64(t), side="left"))
    if i0 >= len(a["m15_start"]) - 2 or (a["m15_start"][i0] - np.datetime64(t)) > np.timedelta64(30, "m"):
        return None
    return i0


def run_trades(sig, a, **kw):
    rows, busy = [], None
    for e in sig.sort_values("t").itertuples():
        if busy is not None and np.datetime64(e.t) < busy:
            continue
        i0 = entry_index(a, e.t)
        if i0 is None:
            continue
        rdist = 2.0 * e.atr
        px, tx, why, done = trade_path(i0, e.D, rdist, a, **kw)
        entry = a["m15_o"][i0]
        rows.append(dict(t=e.t, D=e.D, entry=entry, exit=px, rdist=rdist, gross=(px - entry) * e.D, days=(tx - a["m15_start"][i0]) / np.timedelta64(1, "D"), reason=why,
                         h1_bars=done, exit_time=tx))
        busy = tx
    return pd.DataFrame(rows)


def net_r(tr, spread, fin_rate):
    if tr.empty:
        return pd.Series(dtype=float)
    return (tr.gross - spread - fin_rate * tr.entry * tr.days / 365.0) / tr.rdist


def summarize(tr, spread, fin_rate, risk=0.005):
    if tr.empty:
        return dict(N=0)
    r = net_r(tr, spread, fin_rate).to_numpy()
    mu, t, p = cluster_mean_test(r, tr.t.dt.to_period("W").astype(str))
    eq = np.cumprod(1 + risk * r)
    pk = np.maximum.accumulate(np.r_[1.0, eq])[1:]
    w, ls = r[r > 0].sum(), -r[r <= 0].sum()
    return dict(N=len(r), win_pct=round(100 * (r > 0).mean(), 1), mean_netR=round(mu, 3), t=round(t, 2), p_one_sided=round(p, 4), PF=round(w / ls, 2) if ls > 0 else np.inf,
                maxDD_pct=round(100 * ((pk - eq) / pk).max(), 1), net_pct_at_0p5_risk=round((eq[-1] - 1) * 100, 1), median_hold_h=round(float(np.median(tr.days) * 24), 1))


def control_p(table, obs_mean, n_trades, p_long, draws=2000, seed=7):
    """Random-entry control: sample non-overlapping random H1-close entries (random direction) and apply the same exit rule."""
    rng = np.random.default_rng(seed)
    t_ns = table["t_ns"].to_numpy()
    order = np.argsort(t_ns)
    idxs = np.arange(len(table))
    cnt = 0
    means = []
    for _ in range(draws):
        sub = np.sort(rng.choice(idxs, size=min(5 * n_trades, len(idxs)), replace=False))
        busy, got = -1, []
        for k in sub:
            if t_ns[k] < busy:
                continue
            dsel = 1 if rng.random() < p_long else -1
            got.append(table["r_long" if dsel == 1 else "r_short"].iat[k])
            busy = table["x_long" if dsel == 1 else "x_short"].iat[k]
            if len(got) >= n_trades:
                break
        m = float(np.mean(got)) if got else np.nan
        means.append(m)
        cnt += (m >= obs_mean)
    return (cnt + 1) / (draws + 1), float(np.nanmean(means))
