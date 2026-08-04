# -*- coding: utf-8 -*-
"""DSR + PBO(CSCV) cho HO 5 nguong gate ADV cua book LAG — job Taylor_20260804_080547.
Tai dung ham cua dsr_pbo_annex.py (khong viet lai cong thuc). Ho bien the = 5 nguong
{0, 0.5, 1, 2, 5} ty VND/phien. Kiem tra khoi rong/ suy bien truoc khi chay CSCV
(bai hoc CAPIT navsize 2026-07-31: khoi khong co su kien lam PBO vo nghia)."""
import sys, math, numpy as np
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import dsr_pbo_annex as A

P = "/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice"
LEGS = [("0 (control)",   P + "_exp_ctrl0804_univpit.csv"),
        ("0,5 ty",        P + "_advmin500m_exp_gate500m_univpit.csv"),
        ("1 ty",          P + "_advmin1000m_exp_gate1000m_univpit.csv"),
        ("2 ty",          P + "_advmin2000m_exp_gate2000m_univpit.csv"),
        ("5 ty",          P + "_advmin5000m_exp_gate5000m_univpit.csv")]

navs, rets, names = [], [], []
for nm, f in LEGS:
    s = A.load_nav(f)
    r = A.daily_logret(s)
    navs.append(s); rets.append(r); names.append(nm)
    print(f"{nm:12s} T={len(r):5d}  final NAV={s.iloc[-1]/1e9:9.2f}B  SR/obs={r.mean()/r.std(ddof=1):.5f}")

T = min(len(r) for r in rets)
M = np.column_stack([r[-T:] for r in rets])
print(f"\nma tran CSCV: T={T} phien x Ncfg={M.shape[1]}")

# --- kiem tra khoi suy bien (bai hoc CAPIT navsize) ---
S = 16
T2 = (T // S) * S
blocks = np.array_split(M[:T2], S, axis=0)
bad = [(i, float(np.nanmin(b.std(axis=0, ddof=1)))) for i, b in enumerate(blocks)
       if np.nanmin(b.std(axis=0, ddof=1)) <= 1e-12 or np.isnan(b).any()]
print(f"khoi suy bien (sd~0 hoac NaN) trong {S} khoi: {len(bad)} -> {bad}")

# --- DSR cho cau hinh IS-best cua ho ---
for i, nm in enumerate(names):
    r = rets[i]
    sr = r.mean() / r.std(ddof=1)
    g3, g4 = A.moments(r)[2:4] if len(A.moments(r)) >= 4 else (0.0, 3.0)
    sr0 = A.expected_max_sr(np.var([x.mean()/x.std(ddof=1) for x in rets], ddof=1), len(names))
    d, stat = A.dsr(sr, sr0, g3, g4, len(r))
    print(f"DSR {nm:12s} SR/obs={sr:.5f} sr0(exp max cua ho, N={len(names)})={sr0:.5f} -> DSR={d:.4f}")

pbo, logits, ncombo, ncfg, t2 = A.cscv_pbo(M, S=S)
print(f"\nPBO(CSCV, S={S}, {ncombo} to hop, Ncfg={ncfg}, T={t2}) = {pbo:.3f}  "
      f"median logit={np.median(logits):+.3f}")
