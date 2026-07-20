# -*- coding: utf-8 -*-
"""dc_overlap_cap_narrow_exp.py (job Taylor_20260720_095235) — RESEARCH ONLY, EXPERIMENT.
Paper sleeve + production KHONG dong den (§8: ten file non-canonical, output rieng).

CAU HOI 2 — tran 0.15/ma trong sleeve waterfall:
  A. BROAD (dang wired, `apply_overlap_cap` trong dc_book_waterfall_paper.py):
     0.15 ap cho trong so CONG DON cua MOI ten (DC-only, c30V-only, va ten trung).
  B. NARROW (y do goc ghi trong finding _042827 "chong trung ma DC<->custom30V"):
     0.15 CHI ap cho ten TRUNG (W_dc>0 AND leg c30V>0); ten DC-only giu tran rieng 0.20;
     ten c30V-only khong bi tran rieng (tu nhien <= ~0.10 do cap 0.10 trong ro).
     Phan cat redistribute cho thanh vien ro c30V con headroom (den 0.15) — cung vong lap
     iterate-until-placed nhu ban BROAD, de chenh lech DUY NHAT la pham vi ap tran.

Tai su dung nguyen harness job _042827 (import module => dung lai Wp / W_dc_lag / pk_lag /
blk_tc / run() / overlay() / metrics()), khong build lai panel.
"""
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
import numpy as np, pandas as pd
import dc_overlap_cap_backtest as B   # module-level: builds Wp, W_dc_lag, prints self-checks A/B

cal, NAMES = B.cal, B.NAMES
X = 0.15
CAP_DC = B.CAP_DC          # 0.20 — tran rieng chan DC-only o ban NARROW


def eff_cap_narrow(x=X, dc_cap=CAP_DC, passes=12):
    """Tran x CHI ap cho ten TRUNG. DC-only bi chan boi dc_cap (0.20), c30V-only tu do.
    Redistribute phan cat cho thanh vien ro c30V con headroom (tran x) — giong ban BROAD."""
    park_leg = B.Wp.mul(B.pk_lag, axis=0)
    base = B.W_dc_lag.add(park_leg, fill_value=0.0)
    overlap = ((B.W_dc_lag.values > 1e-12) & (park_leg.reindex_like(B.W_dc_lag).values > 1e-12))
    dc_only = ((B.W_dc_lag.values > 1e-12) & ~overlap)
    mem = (B.Wp.values > 0)
    # tran hieu luc theo ngay x ten
    ceil = np.full(base.shape, np.inf)
    ceil[overlap] = x
    ceil[dc_only] = dc_cap
    arr = base.values.copy()
    resid = np.zeros(len(cal))
    for i in range(len(cal)):
        row, cl = arr[i], ceil[i]
        for _ in range(passes):
            over = np.where(np.isfinite(cl), row - cl, 0.0)
            over[over < 0] = 0.0
            F = over.sum()
            if F <= 1e-12:
                break
            row = np.where(np.isfinite(cl), np.minimum(row, cl), row)
            head = np.where(mem[i], np.maximum(x - row, 0.0), 0.0)
            H = head.sum()
            if H <= 1e-12:
                resid[i] += F
                break
            add = np.minimum(head, head / H * F)
            row = row + add
            F -= add.sum()
            if F > 1e-12:
                resid[i] += F
                break
        arr[i] = row
    return pd.DataFrame(arr, index=cal, columns=NAMES), pd.Series(resid, index=cal)


def main():
    E_ctrl, res0 = B.eff_control()
    E_broad, res_b = B.eff_cap(X)
    E_narrow, res_n = eff_cap_narrow(X)

    # --- SELF-CHECK D: NARROW phai KHONG cham ten DC-only duoi 0.20, va phai chan ten trung <=0.15
    park_leg = B.Wp.mul(B.pk_lag, axis=0)
    ov = ((B.W_dc_lag.values > 1e-12) & (park_leg.reindex_like(B.W_dc_lag).values > 1e-12))
    ov_max = np.nanmax(np.where(ov, E_narrow.values, np.nan))
    print(f"\nSELF-CHECK D: NARROW max weight tren ten TRUNG = {ov_max*100:.3f}% (phai <= 15.000%)")
    dv = (E_narrow.values - E_broad.values)
    print(f"SELF-CHECK D': so ngay NARROW != BROAD = {int((np.abs(dv).sum(axis=1) > 1e-9).sum())}"
          f" / {len(cal)}  | max |dw| = {np.abs(dv).max()*100:.2f}pp")
    print(f"SELF-CHECK E: sum weight — BROAD {E_broad.sum(axis=1).max():.6f} / "
          f"NARROW {E_narrow.sum(axis=1).max():.6f} (phai <= 1.0)")

    variants = [
        ("Q2 control — khong cap (tham chieu)", E_ctrl, res0, None),
        ("Q2-A BROAD 0.15 moi ten (dang wired)", E_broad, res_b, E_ctrl),
        ("Q2-B NARROW 0.15 chi ten trung", E_narrow, res_n, E_ctrl),
    ]
    hdr = f"{'variant':<40}{'win':<5}{'CAGR':>8}{'Sharpe':>7}{'MaxDD':>9}{'Calmar':>7}"
    print("\n=== CAU 2 — pham vi tran 0.15: BROAD vs NARROW (full-NAV overlay len R3) ===")
    print(hdr); print("-" * len(hdr))
    for label, E, resid, Ec in variants:
        rv, xtc = B.run(E, resid, label, Ec)
        rr = B.overlay(rv)
        for tag, xx in [("FULL", rr), ("IS", rr[rr.index <= B.IS_END]), ("OOS", rr[rr.index > B.IS_END])]:
            c, sh, dd, ca = B.metrics(xx)
            print(f"{label:<40}{tag:<5}{c:>7.2f}%{sh:>7.2f}{dd:>8.1f}%{ca:>7.2f}")
        mx = E.max(axis=1)
        print(f"    max eff name-weight: max {mx.max()*100:.1f}%  p99 {mx.quantile(0.99)*100:.1f}%"
              f"  | residual-days {(resid>1e-6).sum()}  extraTC {xtc*100:.3f}pp/yr sleeve")
        print()

    # diagnostic: tran BROAD cham vao ai
    binds_dconly = ((B.W_dc_lag.values > 1e-12) & ~ov & (E_ctrl.values > X)).sum()
    binds_overlap = (ov & (E_ctrl.values > X)).sum()
    binds_c30only = ((B.W_dc_lag.values <= 1e-12) & (E_ctrl.values > X)).sum()
    print(f"diagnostic — name-days control vuot 0.15: DC-only {binds_dconly}, "
          f"TRUNG {binds_overlap}, c30V-only {binds_c30only}")


if __name__ == "__main__":
    main()
