# -*- coding: utf-8 -*-
"""Q-SLEEVE diagnostics (job Taylor_20260712_080114): concentration, turnover, capacity.
Run on the relative winner (q12neu) vs control — informational for the audit record
(verdict already NO-GO on IS/LOO/tail gates)."""
import numpy as np
import pandas as pd

BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
F_CTL = BASE + "wtnamecap_exp_qsleeve_control.csv"
F_Q12 = BASE + "wtew_n12_cap10_exp_qsleeve_q12neu.csv"


def load(fp):
    df = pd.read_csv(fp, low_memory=False)
    d = df[(df.record_type == "DAILY") & df.combined_nav.notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("ymd")
    mem = df[df.record_type == "CUSTOM_MEMBERS"].copy()
    return d, mem


ctl_d, ctl_m = load(F_CTL)
q_d, q_m = load(F_Q12)

# ---- capacity: achieved park weight on NEUTRAL days (state==3) --------------------------------
for name, d in (("control", ctl_d), ("q12neu", q_d)):
    n3 = d[d.state == 3.0]
    pw = (n3.bal_etf_ref.fillna(0) + n3.lag_etf_ref.fillna(0)) / n3.combined_nav
    print(f"[capacity] {name}: NEUTRAL days={len(n3)}, park weight mean={pw.mean():.3f} "
          f"p50={pw.median():.3f} p10={pw.quantile(0.10):.3f} max={pw.max():.3f}")

# ---- turnover: membership churn per rebal ------------------------------------------------------
def churn(mem):
    mem = mem.copy()
    mem["rd"] = pd.to_datetime(mem["reason"], errors="coerce")  # rebal_date column mapping unknown
    # CUSTOM_MEMBERS rows: columns quarter/rebal_date/ticker packed into generic cols; find them
    return None


# CUSTOM_MEMBERS rows use: key=quarter?, ticker column holds ticker. Inspect actual mapping:
print("\n[members] control cols sample:")
print(ctl_m.head(2).dropna(axis=1, how="all").to_string())
print("[members] q12 cols sample:")
print(q_m.head(2).dropna(axis=1, how="all").to_string())


def churn2(mem):
    # after inspection: 'value'=qmult?, use ymd as rebal date if present; fallback: key
    dcol = "ymd" if mem["ymd"].notna().any() else "key"
    m = mem[[dcol, "ticker"]].dropna()
    m[dcol] = pd.to_datetime(m[dcol], errors="coerce")
    m = m.dropna()
    sets = {d: set(g["ticker"]) for d, g in m.groupby(dcol)}
    ds = sorted(sets)
    ch = []
    for a, b in zip(ds, ds[1:]):
        u = sets[a] | sets[b]
        ch.append(len(sets[b] - sets[a]) / max(1, len(sets[b])))
    return np.mean(ch), len(ds), np.mean([len(sets[d]) for d in ds])


for name, mem in (("control", ctl_m), ("q12neu", q_m)):
    try:
        c, nreb, avg_n = churn2(mem)
        print(f"[turnover] {name}: rebals={nreb}, avg members={avg_n:.1f}, "
              f"mean new-name share per rebal={c:.2%}")
    except Exception as e:
        print(f"[turnover] {name}: FAILED ({e})")

# ---- concentration: max single-name weight %NAV + per-name park-PnL share ---------------------
# equal-weight sleeve: name weight %NAV on day t = park_w_t / n_active. For control (namecap 0.10):
# upper bound = park_w_t * 0.10.
for name, d, mem, ew in (("control", ctl_d, ctl_m, False), ("q12neu", q_d, q_m, True)):
    pw = (d.bal_etf_ref.fillna(0) + d.lag_etf_ref.fillna(0)) / d.combined_nav
    if ew:
        dcol = "ymd" if mem["ymd"].notna().any() else "key"
        m = mem[[dcol, "ticker"]].dropna()
        m[dcol] = pd.to_datetime(m[dcol], errors="coerce")
        n_by_reb = m.groupby(dcol)["ticker"].nunique().sort_index()
        # per-day n_active = members at latest rebal <= t
        rebs = n_by_reb.index
        idx = np.searchsorted(rebs, d["ymd"].values, side="right") - 1
        n_act = np.where(idx >= 0, n_by_reb.values[np.maximum(idx, 0)], np.nan)
        nw = pw.values / n_act
        print(f"[concentration] {name}: max single-name %NAV = {np.nanmax(nw):.2%}, "
              f"p99 = {np.nanpercentile(nw, 99):.2%} (ew 1/n)")
    else:
        print(f"[concentration] {name}: max single-name %NAV <= {(pw * 0.10).max():.2%} (namecap 0.10)")
