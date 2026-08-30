"""DSR/PBO for the custom30V SECTOR-NEUTRAL accrual-gate family (job Taylor_20260830_035832).
Fork of dsr_pbo_agate.py (job _014429, pooled gate) — identical formulas, points at the sector-
neutral family {ctrl(0%, shared w/ pooled — SECNEUTRAL doesn't touch this path), agate20sec,
agate33sec(PRE-REGISTERED), agate50sec}.
"""
import sys, os, math
import numpy as np, pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, dsr, cscv_pbo, expected_max_sr, ANN, load_nav, daily_logret

D = "/home/trido/thanhdt/WorkingClaude/data"
FILES = {
    "ctrl_0pct":  f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_ctrl_univpit_exp_ctrl.csv",
    "agate20sec":    f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate20sec_univpit_exp_selyieldcombo_agate_exp_agate20sec.csv",
    "agate33sec_PREREG": f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate33sec_univpit_exp_selyieldcombo_agate_exp_agate33sec.csv",
    "agate50sec":    f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_agate50sec_univpit_exp_selyieldcombo_agate_exp_agate50sec.csv",
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

    print("\n" + "="*70)
    print("DSR (agate33sec PRE-REGISTERED, N trials = 1 for this specific axis)")
    print("="*70)
    r_treat = daily_logret(series["agate33sec_PREREG"])
    T = len(r_treat)
    sr_hat, g3, g4 = moments(r_treat)
    r_ctrl = daily_logret(series["ctrl_0pct"])
    sr_ctrl, _, _ = moments(r_ctrl)
    p_vs_zero, z0 = dsr(sr_hat, 0.0, g3, g4, T)
    p_vs_ctrl, zc = dsr(sr_hat, sr_ctrl, g3, g4, T)
    print(f"  agate33sec per-obs SR={sr_hat:.5f} (ann {sr_hat*math.sqrt(ANN):.3f}) vs "
          f"ctrl per-obs SR={sr_ctrl:.5f} (ann {sr_ctrl*math.sqrt(ANN):.3f})")
    print(f"  DSR vs SR0=0 (any skill):        P={p_vs_zero:.4f}  (z={z0:.3f})")
    print(f"  DSR vs SR0=ctrl (beats baseline): P={p_vs_ctrl:.4f}  (z={zc:.3f})")
    print(f"  Read: P(true SR > SR0) — {'<0.95 => RED FLAG per coding_guidelines' if p_vs_ctrl<0.95 else '>=0.95'}")

    print("\n" + "="*70)
    print("CSCV/PBO across sector-neutral family {0%, 20%, 33%(prereg), 50%} — overfit-if-cherry-picked check")
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
          f"pick the PRE-REGISTERED config (agate33sec), never the apparent-best of this family.")

if __name__ == "__main__":
    main()
