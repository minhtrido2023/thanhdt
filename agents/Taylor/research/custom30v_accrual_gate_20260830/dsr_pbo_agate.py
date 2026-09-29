"""DSR/PBO for the custom30V accrual-gate family (job Taylor_20260830_014429).
Reuses the exact formulas from dsr_pbo_annex.py (Bailey & Lopez de Prado 2014/2017), applied to
the 4-config family actually run this job: ctrl(0%), agate20, agate33(PRE-REGISTERED), agate50.
Only agate33 is the pre-registered claim; 20/50 are robustness/sensitivity points, NOT candidates
to cherry-pick from — PBO here measures how likely picking the apparent-best of this family (by
IS Sharpe) would have been overfitting, which is exactly the risk of NOT pre-registering.
"""
import sys, os, math
import numpy as np, pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, dsr, cscv_pbo, expected_max_sr, ANN, load_nav, daily_logret

D = "/home/trido/thanhdt/WorkingClaude/data"
FILES = {
    "ctrl_0pct":  f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_ctrl_univpit_exp_ctrl.csv",
    "agate20":    f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate20_univpit_exp_selyieldcombo_agate_exp_agate20.csv",
    "agate33_PREREG": f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate33_univpit_exp_selyieldcombo_agate_exp_agate33.csv",
    "agate50":    f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate50_univpit_exp_selyieldcombo_agate_exp_agate50.csv",
}

def main():
    series = {}
    for name, path in FILES.items():
        s = load_nav(path)
        if s is None:
            print(f"  SKIP {name}: no combined_nav")
            continue
        series[name] = s
        print(f"  loaded {name}: {len(s)} daily obs, {s.index.min().date()}->{s.index.max().date()}")

    # ---- DSR on the pre-registered leg vs the R3(ctrl) anchor ----
    print("\n" + "="*70)
    print("DSR (agate33 PRE-REGISTERED, N trials = 1 for this specific axis)")
    print("="*70)
    r_treat = daily_logret(series["agate33_PREREG"])
    T = len(r_treat)
    sr_hat, g3, g4 = moments(r_treat)
    # SR0 = the pre-registered null: R3 anchor's own per-obs Sharpe (does the gate beat baseline
    # after deflating for having looked at *some* number of trials). N=1 pre-registered trial ->
    # expected_max_sr degenerates (single trial has no multiple-testing inflation); report DSR
    # against SR0=0 (skill vs no-skill) as the headline, and vs SR0=ctrl's realized SR as the
    # "beats baseline" check.
    r_ctrl = daily_logret(series["ctrl_0pct"])
    sr_ctrl, _, _ = moments(r_ctrl)
    p_vs_zero, z0 = dsr(sr_hat, 0.0, g3, g4, T)
    p_vs_ctrl, zc = dsr(sr_hat, sr_ctrl, g3, g4, T)
    print(f"  agate33 per-obs SR={sr_hat:.5f} (ann {sr_hat*math.sqrt(ANN):.3f}) vs "
          f"ctrl per-obs SR={sr_ctrl:.5f} (ann {sr_ctrl*math.sqrt(ANN):.3f})")
    print(f"  DSR vs SR0=0 (any skill):        P={p_vs_zero:.4f}  (z={z0:.3f})")
    print(f"  DSR vs SR0=ctrl (beats baseline): P={p_vs_ctrl:.4f}  (z={zc:.3f})")
    print(f"  Read: P(true SR > SR0) — {'<0.95 => RED FLAG per coding_guidelines' if p_vs_ctrl<0.95 else '>=0.95'}")

    # ---- PBO across the exploratory 4-config family (0/20/33/50%) ----
    print("\n" + "="*70)
    print("CSCV/PBO across family {0%, 20%, 33%(prereg), 50%} — overfit-if-cherry-picked check")
    print("="*70)
    names = list(series.keys())
    common_idx = None
    for s in series.values():
        common_idx = s.index if common_idx is None else common_idx.intersection(s.index)
    common_idx = common_idx.sort_values()
    R = np.column_stack([daily_logret(series[n].reindex(common_idx).ffill()) for n in names])
    pbo, logits, n_combos, ncfg, T2 = cscv_pbo(R, S=16)
    print(f"  configs={names}")
    print(f"  N_combos={n_combos}  T_used={T2}  PBO={pbo:.3f} "
          f"(share of IS/OOS splits where the IS-best config ranks BELOW OOS median)")
    print(f"  Read: PBO>=0.5 => per coding_guidelines, treat family as prone to overfitting; "
          f"pick the PRE-REGISTERED config (agate33), never the apparent-best of this family.")

if __name__ == "__main__":
    main()
