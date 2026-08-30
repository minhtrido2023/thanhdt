import pandas as pd, numpy as np

# Round2 fix for quant-skeptic REFUTED point 1: persist the CAP_SIGNAL (composite) N x H grid.
# Round1 built this grid ad-hoc in /tmp/diverge_strategy_test.py-style code but never saved the
# script or the CAP_SIGNAL CSV (only DIVERGE-only grid was persisted, in
# exp_insider/diverge_strategy_impact_grid.csv). This script reuses the EXACT same full-path
# compounding methodology as that persisted DIVERGE-only script, applied to the composite
# cap_signal episode set instead. Non-canonical filename by design (§8 coding_guidelines).

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WC}/mike/agents/Taylor/exp_insider"

mp = pd.read_csv(f"{WC}/data/tier2_macro_panel.csv", usecols=["time", "VNI", "EEM", "DXY", "TNX"])
mp["time"] = pd.to_datetime(mp["time"])
mp = mp.sort_values("time").reset_index(drop=True)

W = 60
mp["EM_dd60"] = mp["EEM"] / mp["EEM"].rolling(W, min_periods=W).max() - 1
mp["VNI_dd60"] = mp["VNI"] / mp["VNI"].rolling(W, min_periods=W).max() - 1
mp["DXY_mom60"] = mp["DXY"] / mp["DXY"].shift(W) - 1

# PRE-REGISTERED thresholds (production_mechanism_2009_2018_20260830.md §B.2, reused verbatim,
# same composite definition as /tmp/diverge_attrib.py used for the round1 per-episode diagnostic)
mp["diverge"] = (mp["EM_dd60"] <= -0.08) & (mp["VNI_dd60"] >= -0.03)
mp["cap_signal"] = mp["diverge"] & ((mp["DXY_mom60"] >= 0.05) | (mp["TNX"] >= 3.0))

def episodes_from(mask_col):
    fire_idx = mp.index[mp[mask_col]].tolist()
    eps = []
    if fire_idx:
        start = prev = fire_idx[0]
        for i in fire_idx[1:]:
            if i - prev > 10:
                eps.append((start, prev))
                start = i
            prev = i
        eps.append((start, prev))
    rows = [{"episode_start_idx": s, "fire_date": mp.loc[s, "time"]} for s, e in eps]
    return pd.DataFrame(rows)

ep_df = episodes_from("cap_signal")
print(f"CAP_SIGNAL composite episodes (re-derived, should = 8 per round1): {len(ep_df)}")
print(ep_df.to_string(index=False))
ep_df.to_csv(f"{OUT}/cap_signal_episodes_recheck.csv", index=False)

# ---- Load V2.4 audited full-window daily NAV (same audited source as round1, quant-skeptic
# CONFIRMED job 08-25) ----
audit = pd.read_csv(
    f"{WC}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_scenarioB_production_univpit_from20080101.csv"
)
daily = audit[audit["record_type"] == "DAILY"].copy()
daily["ymd"] = pd.to_datetime(daily["ymd"])
daily = daily.sort_values("ymd").reset_index(drop=True)
daily["ret"] = daily["combined_nav"].pct_change()
print(f"Daily NAV rows: {len(daily)}, range {daily['ymd'].min().date()} -> {daily['ymd'].max().date()}")

recon = daily["combined_nav"].iloc[0] * (1 + daily["ret"].fillna(0)).cumprod()
diff_vnd = (recon - daily["combined_nav"]).abs().max()
print(f"SELF-CHECK reconstruct-from-ret max abs diff vs source combined_nav: {diff_vnd:.6f} VND")

nav0 = daily["combined_nav"].iloc[0]
years = (daily["ymd"].iloc[-1] - daily["ymd"].iloc[0]).days / 365.25
baseline_cagr = (daily["combined_nav"].iloc[-1] / nav0) ** (1 / years) - 1
print(f"Baseline (no cap): CAGR={baseline_cagr*100:.2f}%, final NAV={daily['combined_nav'].iloc[-1]/1e9:.1f}B, years={years:.2f}")


def build_cap_mask(fire_dates, n_sessions):
    """N-session cap window starting at each episode's first fire date."""
    mask = pd.Series(False, index=daily.index)
    ymd_list = daily["ymd"].tolist()
    ymd_pos = {d: i for i, d in enumerate(ymd_list)}
    for fd in fire_dates:
        if fd not in ymd_pos:
            later = daily[daily["ymd"] >= fd]
            if later.empty:
                continue
            pos = later.index[0]
        else:
            pos = ymd_pos[fd]
        end = min(pos + n_sessions, len(daily))
        mask.iloc[pos:end] = True
    return mask


def window_impact(nav_capped, nav_baseline, m):
    idx = daily.index[m]
    if len(idx) < 2:
        return np.nan
    i0, i1 = idx[0], idx[-1]
    base = nav_baseline.iloc[i1] / nav_baseline.iloc[i0] - 1
    cap = nav_capped.iloc[i1] / nav_capped.iloc[i0] - 1
    return (cap - base) * 100


results = []
for N in (10, 20):
    cap_mask = build_cap_mask(ep_df["fire_date"], N)
    for H in (0.30, 0.50, 0.70):
        capped_ret = daily["ret"].copy()
        capped_ret[cap_mask.values] = capped_ret[cap_mask.values] * (1 - H)
        capped_ret = capped_ret.fillna(0)
        nav_capped = nav0 * (1 + capped_ret).cumprod()
        nav_baseline = daily["combined_nav"]

        cagr_capped = (nav_capped.iloc[-1] / nav0) ** (1 / years) - 1
        delta_cagr_pp = (cagr_capped - baseline_cagr) * 100
        total_impact_pp = (nav_capped.iloc[-1] / nav0 - 1) * 100 - (nav_baseline.iloc[-1] / nav0 - 1) * 100

        is_mask = (daily["ymd"] >= "2014-01-01") & (daily["ymd"] <= "2019-12-31")
        oos_mask = daily["ymd"] >= "2020-01-01"
        is_impact = window_impact(nav_capped, nav_baseline, is_mask)
        oos_impact = window_impact(nav_capped, nav_baseline, oos_mask)

        results.append({
            "N_sessions": N, "haircut_H": H,
            "n_flagged_days": int(cap_mask.sum()),
            "delta_CAGR_pp": delta_cagr_pp,
            "final_NAV_B": nav_capped.iloc[-1] / 1e9,
            "full_window_impact_pp": total_impact_pp,
            "IS_2014_19_impact_pp": is_impact,
            "OOS_2020_now_impact_pp": oos_impact,
        })

res_df = pd.DataFrame(results)
print("\n=== CAP_SIGNAL composite grid (round2, persisted) ===")
print(res_df.to_string(index=False))
res_df.to_csv(f"{OUT}/cap_signal_impact_grid_round2.csv", index=False)

# ---- Leave-one-episode-out at the diagnostic reference point N=20,H=50 (same point round1's
# per-episode table used), plus a robustness cross-check at N=10,H=30 ----
print("\n=== Leave-one-episode-out (delta_CAGR_pp, full path) ===")
loo_rows = []
fire_dates_all = list(ep_df["fire_date"])
for N, H in ((20, 0.50), (10, 0.30)):
    # full set baseline for this (N,H)
    full_mask = build_cap_mask(fire_dates_all, N)
    capped_ret = daily["ret"].copy()
    capped_ret[full_mask.values] = capped_ret[full_mask.values] * (1 - H)
    capped_ret = capped_ret.fillna(0)
    nav_capped = nav0 * (1 + capped_ret).cumprod()
    full_cagr = (nav_capped.iloc[-1] / nav0) ** (1 / years) - 1
    full_delta_pp = (full_cagr - baseline_cagr) * 100
    loo_rows.append({"N": N, "H": H, "excluded": "NONE (full 8-episode set)", "delta_CAGR_pp": full_delta_pp})

    for excl_fd in fire_dates_all:
        subset = [fd for fd in fire_dates_all if fd != excl_fd]
        m = build_cap_mask(subset, N)
        cr = daily["ret"].copy()
        cr[m.values] = cr[m.values] * (1 - H)
        cr = cr.fillna(0)
        nc = nav0 * (1 + cr).cumprod()
        cagr = (nc.iloc[-1] / nav0) ** (1 / years) - 1
        delta_pp = (cagr - baseline_cagr) * 100
        loo_rows.append({"N": N, "H": H, "excluded": excl_fd.date().isoformat(), "delta_CAGR_pp": delta_pp})

    # combo pairs: 2023-08-16+2023-09-21 (~5wk apart, flagged round2) AND the structurally
    # identical 2016-11-14+2016-12-19 pair (~5wk apart too, quant-skeptic round2-verify flagged
    # this as an inconsistent/asymmetric robustness sweep in round2 v1 -> added here)
    for pair, tag in (
        ([pd.Timestamp("2023-08-16"), pd.Timestamp("2023-09-21")], "PAIR 2023-08-16+2023-09-21 (N->6)"),
        ([pd.Timestamp("2016-11-14"), pd.Timestamp("2016-12-19")], "PAIR 2016-11-14+2016-12-19 (N->6)"),
    ):
        subset = [fd for fd in fire_dates_all if fd not in pair]
        m = build_cap_mask(subset, N)
        cr = daily["ret"].copy()
        cr[m.values] = cr[m.values] * (1 - H)
        cr = cr.fillna(0)
        nc = nav0 * (1 + cr).cumprod()
        cagr = (nc.iloc[-1] / nav0) ** (1 / years) - 1
        delta_pp = (cagr - baseline_cagr) * 100
        loo_rows.append({"N": N, "H": H, "excluded": tag, "delta_CAGR_pp": delta_pp})

loo_df = pd.DataFrame(loo_rows)
print(loo_df.to_string(index=False))
loo_df.to_csv(f"{OUT}/cap_signal_leave_one_out_round2.csv", index=False)
