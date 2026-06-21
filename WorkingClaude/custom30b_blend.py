# -*- coding: utf-8 -*-
"""custom30b_blend.py — full-system estimate of the BULL sleeve (custom30B) vs custom30V-in-bull.
Returns-overlay on the LIVE R3 NAV (NEUTRAL-only parking): on BULL/EXBULL days, deploy a fraction
f of NAV (= park_frac x idle-in-bull, ~0.22) of the otherwise-idle cash into the bull basket. Compare
the two candidate bull vehicles. This is the deployed-uplift estimate; the deploy fraction is the only
approximation (faithful dual-vehicle wiring deferred until bull-park is enabled). Reports FULL/IS/OOS +
signature, so we see the real full-system gain, not just the bull-days basket return."""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket

END = os.environ.get("AUDIT_END", "2026-06-19"); START = "2014-01-01"
R3 = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv"

# state (DT5G)
st = bq(f"SELECT time,state FROM tav2_bq.vnindex_5state_dt5g_live WHERE time>='{START}' AND time<='{END}'")
st["time"] = pd.to_datetime(st["time"]); state = st.set_index("time")["state"]
state = state[~state.index.duplicated(keep="last")].sort_index()

# prod R3 NAV
df = pd.read_csv(R3, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce"); d = d.dropna(subset=["ymd"]).sort_values("ymd")
prod = d.groupby("ymd")["combined_nav"].last().astype(float)
idx = prod.index; pr = prod.pct_change()
bmask = state.reindex(idx).isin([4, 5]).values   # bull/exbull day mask aligned to prod

def basket_ret(env):
    for k, v in env.items(): os.environ[k] = str(v)
    lvl, *_ = custom_basket.build_pit(bq, START, END, top_n=30, gate_rating=3, rebal="q2m5", weight_scheme="namecap")
    for k in env: os.environ.pop(k, None)
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index); s = s.sort_index()
    return s.reindex(idx).pct_change()

rb_v = basket_ret({"BASKET_SELECT": "yieldcombo"})                                              # custom30V
rb_b = basket_ret({"BASKET_SELECT": "pemom", "BASKET_LIQ_FLOOR_B": 10, "BASKET_MOM_W": 1.0})     # custom30B

def met(r):
    r = r.dropna(); nav = (1 + r).cumprod(); yrs = (r.index[-1] - r.index[0]).days / 365.25
    cg = nav.iloc[-1] ** (1 / yrs) - 1; dd = (nav / nav.cummax() - 1).min()
    return dict(c=cg * 100, sh=r.mean() / r.std() * np.sqrt(252), dd=dd * 100, cal=cg / abs(dd))
def win(r, lo, hi): return r[(r.index >= lo) & (r.index <= hi)]
def line(lbl, r):
    f = met(r); i = met(win(r, "2014-01-01", "2019-12-31")); o = met(win(r, "2020-01-01", "2026-12-31"))
    sig = "PASS" if i["c"] > 0 and o["c"] > 0 else "fail"
    print(f"  {lbl:30s} FULL {f['c']:5.2f}%/Sh{f['sh']:.2f}/DD{f['dd']:5.1f}/Cal{f['cal']:.2f}  IS {i['c']:5.2f}% OOS {o['c']:5.2f}% [{sig}]")

print(f"{START} -> {END} | bull/exbull days in window = {int(np.nansum(bmask))}\n")
line("R3 live (no bull-park)", pr)
for f in (0.15, 0.22, 0.30):
    ov_v = pr.to_numpy(copy=True); ov_b = pr.to_numpy(copy=True)
    bm = bmask & ~np.isnan(rb_v.values) & ~np.isnan(rb_b.values)
    ov_v[bm] = ov_v[bm] + f * rb_v.values[bm]
    ov_b[bm] = ov_b[bm] + f * rb_b.values[bm]
    print(f"\n--- deploy fraction f={f:.2f} of NAV into bull basket on bull days ---")
    line(f"  + bull-park custom30V", pd.Series(ov_v, index=idx))
    line(f"  + bull-park custom30B", pd.Series(ov_b, index=idx))
print("\nREAD: custom30B vs custom30V row at same f = the vehicle-choice gain; vs R3 = the whole bull-park gain.")
