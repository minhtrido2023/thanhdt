#!/usr/bin/env python3
"""H2 (b) — DCF cho ro dang giu (SpaceX + ZaloPay, doc tu dnse_raw moi nhat, LOC accountNo §12)
voi CPI cu (cpi_vn.py T2/T3 noi suy) vs CPI that FiinPro. KHONG sua cpi_vn.py."""
import sys, os, csv, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from pathlib import Path
D = Path(__file__).resolve().parent
import cpi_vn, dcf_valuation as dv

ASOF = "2026-09-26"
TK = open("/tmp/h2_held.txt").read().split()

_orig = cpi_vn.cpi_monthly_df
def blended(end="2026-06-01"):
    o = _orig(end=end)
    fp = pd.read_csv("mike/data/fiinprox_cpi_monthly_20260914.csv")
    fp["time"] = pd.to_datetime(fp["month"].astype(str) + "-01")
    mp = dict(zip(fp["time"], fp["cpi_yoy_pct"]))
    o = o.copy()
    o["cpi_yoy"] = np.where(o["is_real_nso"], o["cpi_yoy"],
                            o["time"].map(mp).fillna(o["cpi_yoy"]))
    o["cpi_yoy_chg3"] = o["cpi_yoy"].diff(3)
    return o

def run(label):
    dv._CPI_DF = None; dv._TG_CACHE.clear()
    tg, frac = dv.terminal_growth(ASOF, with_frac=True)
    g = dv.terminal_growth_mode(ASOF)
    print(f"[{label}] terminal_growth (5y-avg CPI) = {tg*100:.4f}%  frac_real={frac:.2f}  "
          f"-> g_term mode={dv.DEFAULT_TERM_MODE}: {g*100:.4f}%")
    out = {}
    for t in TK:
        try:
            r = dv.fair_value(t, ASOF)
            fv = r.get("fair_value_ps") if isinstance(r, dict) else None
            out[t] = (float(fv) if fv is not None else None,
                      r.get("reason") or r.get("note") or "" if isinstance(r, dict) else "")
        except Exception as e:
            out[t] = (None, f"{type(e).__name__}: {e}")
    return (tg, g), out

a_s, a = run("CPI CU  (cpi_vn T2/T3)")
cpi_vn.cpi_monthly_df = blended; dv._cpi.cpi_monthly_df = blended
b_s, b = run("CPI THAT (FiinPro)")

rows = []; d = []
for t in TK:
    x, y = a[t][0], b[t][0]
    if x and y:
        pct = 100.0 * (y / x - 1.0); d.append(pct)
    else:
        pct = None
    rows.append([t, round(x, 1) if x else "", round(y, 1) if y else "",
                 round(pct, 4) if pct is not None else "", a[t][1][:60] or b[t][1][:60]])
print(f"\n[ket qua] {len(d)}/{len(TK)} ma tinh duoc DCF ca 2 chan")
if d:
    print(f"  Delta gia tri hop ly: median {np.median(d):+.3f}%  mean {np.mean(d):+.3f}%  "
          f"min {min(d):+.3f}%  max {max(d):+.3f}%  |Delta|>1%: {sum(1 for x in d if abs(x)>1)}")
print(f"  terminal_growth: {a_s[0]*100:.4f}% -> {b_s[0]*100:.4f}% "
      f"(Delta {100*(b_s[0]-a_s[0]):+.4f}pp) | g_term: {a_s[1]*100:.4f}% -> {b_s[1]*100:.4f}% "
      f"(Delta {100*(b_s[1]-a_s[1]):+.4f}pp)")
with open(D/"h2_dcf_delta.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["ticker","fv_cpi_old","fv_cpi_fiinpro","delta_pct","note"]); w.writerows(rows)
print(f"-> {D/'h2_dcf_delta.csv'}")
for r in rows: print("   ", r)
