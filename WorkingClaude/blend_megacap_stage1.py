# -*- coding: utf-8 -*-
"""blend_megacap_stage1.py — STAGE 1 fast blend test of a small megacap/beta sleeve (plan: parallel-puzzling-boole).
Megacap vehicle = cap-weighted basket (build_pit capwt, gate<=3, q2m5) = index leaders by mcap.
Narrow signal = capwt-basket trailing-63d return > ew-basket trailing-63d return (megacaps leading).
Triggers: state-only {BULL,EXBULL} | narrow-gated {BULL,EXBULL AND narrow}.
Funding: A=carve from books (1-w)*prod+w*mega on trigger ; B=idle-cash additive prod+min(w,idle)*mega.
Measure each cell: FULL/IS/OOS CAGR/Sharpe/DD/Calmar + 2025 regret vs VNI + corr-to-prod + chu-ky (IS vs OOS).
NO harness change; returns-based. Kill-early per plan success criteria."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude"); os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket as cb
from pt_dates import detect_end_date

START, END = "2014-01-02", detect_end_date()
PRODF = "data/v23_golive_audit_2014_now_etfliqcustompitg_wtnamecap.csv"

# --- 1. megacap (capwt) + ew baskets (same membership, gate<=3, q2m5) ---
print("[1] building capwt + ew baskets ...")
lvl_cap,_,_,_ = cb.build_pit(bq, START, END, quality="none", rebal="q2m5", gate_rating=3, weight_scheme="capwt")
lvl_ew,_,_,_  = cb.build_pit(bq, START, END, quality="none", rebal="q2m5", gate_rating=3, weight_scheme="ew")
cap = pd.Series(lvl_cap); cap.index = pd.to_datetime(cap.index); cap = cap.sort_index().astype(float)
ew  = pd.Series(lvl_ew);  ew.index  = pd.to_datetime(ew.index);  ew  = ew.sort_index().astype(float)
mega_ret = cap.pct_change()
narrow = (cap.pct_change(63) - ew.pct_change(63)) > 0.0   # megacaps leading EW over 3mo

# --- 2. production NAV + idle-cash fraction ---
df = pd.read_csv(PRODF, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce"); d = d.dropna(subset=["ymd"]).sort_values("ymd")
g = d.groupby("ymd")
prod = g["combined_nav"].last().astype(float); prod_ret = prod.pct_change()
def col(c): return g[c].last().astype(float) if c in d.columns else pd.Series(0.0, index=prod.index)
idle = (col("bal_cash_ref") + col("lag_cash_ref"))
tot  = sum(col(c) for c in ["bal_cash_ref","bal_stocks_ref","bal_etf_ref","lag_cash_ref","lag_stocks_ref","lag_etf_ref"])
idle_frac = (idle / tot.replace(0, np.nan)).clip(0, 1).fillna(0.30)
vni = col("vni_close")

# --- 3. state ---
st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s")
st["time"] = pd.to_datetime(st["time"]); state = st.set_index("time")["state"]
state = state[~state.index.duplicated(keep="last")].sort_index()

# align
idx = prod_ret.index.intersection(mega_ret.index)
prod_ret, mega_ret, narrow = prod_ret.reindex(idx), mega_ret.reindex(idx).fillna(0), narrow.reindex(idx).fillna(False)
idle_frac, vni = idle_frac.reindex(idx).fillna(0.30), vni.reindex(idx)
state_d = state.reindex(idx, method="ffill").fillna(3)
in_bull = state_d.isin([4,5])
print(f"[2] aligned {len(idx)} days {idx[0].date()}->{idx[-1].date()} | bull/exbull days {int(in_bull.sum())} "
      f"| narrow&bull days {int((in_bull&narrow).sum())} | corr(prod,mega)={prod_ret.corr(mega_ret):+.2f}")

def met(r, lo=None, hi=None):
    r = r.dropna()
    if lo: r = r[(r.index>=lo)&(r.index<=hi)]
    if len(r) < 20: return None
    nav=(1+r).cumprod(); yrs=(r.index[-1]-r.index[0]).days/365.25
    cg=nav.iloc[-1]**(1/yrs)-1; dd=(nav/nav.cummax()-1).min()
    return dict(cg=cg*100, sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0, dd=dd*100, cal=cg/abs(dd) if dd<0 else 0)
def y2025(r):
    r=r[(r.index>='2025-06-01')&(r.index<='2026-06-18')].dropna()
    return ((1+r).prod()-1)*100 if len(r) else np.nan

vni_2025 = (vni[vni.index>='2025-06-01'].dropna().iloc[-1]/vni[vni.index>='2025-06-01'].dropna().iloc[0]-1)*100
base=met(prod_ret); print(f"\n[3] PROD baseline: FULL {base['cg']:.1f}%/Sh{base['sh']:.2f}/DD{base['dd']:.1f}/Cal{base['cal']:.2f}"
      f"  | 2025win prod {y2025(prod_ret):+.1f}% vs VNI {vni_2025:+.1f}% (regret {y2025(prod_ret)-vni_2025:+.1f}pp)")
print(f"\n{'cell':34s} {'FULL':>20s} {'IS':>14s} {'OOS':>14s}  {'2025':>7s} {'regret':>7s}")
def row(lbl, pr):
    f=met(pr); i=met(pr,'2014-01-01','2019-12-31'); o=met(pr,'2020-01-01','2026-12-31'); r25=y2025(pr)
    print(f"{lbl:34s} {f['cg']:5.1f}%/Sh{f['sh']:.2f}/DD{f['dd']:5.1f}/C{f['cal']:.2f}  "
          f"{i['cg']:4.1f}%/C{i['cal']:.2f}  {o['cg']:4.1f}%/C{o['cal']:.2f}  {r25:+5.1f}% {r25-vni_2025:+6.1f}")
row("PROD (w=0)", prod_ret)
# CEILING TEST: vehicle {mega capwt gate3 | VNINDEX direct (incl VIC)} x trigger {bull&narrow |
# (NEU+bull)&narrow | narrow-only any state} x funding {A carve}.  w=0.20 (max small).
vni_ret = vni.pct_change().reindex(idx).fillna(0)
in_neu_bull = state_d.isin([3,4,5])
vehicles = {"mega(gate3)": mega_ret, "VNINDEX(incl VIC)": vni_ret}
trigs = {"bull&narrow": in_bull & narrow, "neu+bull&narrow": in_neu_bull & narrow, "narrow-only": narrow}
for vnm, veh in vehicles.items():
    for tnm, trig in trigs.items():
        w = 0.20
        a = np.where(trig, (1-w)*prod_ret + w*veh, prod_ret)
        row(f"A {vnm} {tnm} w20", pd.Series(a, index=idx))
print("\n(success: regret cut >=+5-8pp AND Calmar not materially worse AND IS/OOS not extreme-skewed)")
print(f"(diag: bull&narrow {int((in_bull&narrow).sum())}d | neu+bull&narrow {int((in_neu_bull&narrow).sum())}d | "
      f"narrow-only {int(narrow.sum())}d  of {len(idx)})")
