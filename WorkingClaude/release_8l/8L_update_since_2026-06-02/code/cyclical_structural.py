#!/usr/bin/env python3
"""
cyclical_structural.py — STRUCTURAL overlay for the cyclical detector (2026-05-31)
==================================================================================
User challenge: a high commodity PERCENTILE ≠ "about to revert" when the SUPPLY CURVE
has structurally shifted (rubber: 6-yr ANRPC deficit, 7-yr replant lag, land conversion)
or a high COST ANCHOR (oil) holds the floor. Percentile encodes mean-reversion; it
breaks under structural shifts. Fix: commodity regime = PERCENTILE × STRUCTURE × COST-ANCHOR.
  high pctile + DEFICIT/long-supply-lag/high-oil → ELEVATED-SUPPORTED (earnings sustain, NOT avoid)
  high pctile + RESPONSIVE/ample supply          → cyclical-peak AVOID-new (reverts)
  low  pctile (any)                              → BUY-zone (cheap commodity)
Brent embedded (cost anchor for oil-linked: rubber↔synthetic, PVC, urea↔gas).
Output: data/brent_monthly.csv, data/cyclical_structural.{md,csv}
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
# STRUCTURE per commodity (manual, from ANRPC/research) + oil-linkage
STRUCTURE={
 "rubber":  ("DEFICIT","6yr ANRPC deficit, 7yr replant lag, land→durian/IP, oil-anchored synthetic", True),
 "iron_ore":("RESPONSIVE","China-demand driven, major miners can ramp → not structurally tight", False),
 "urea":    ("AMPLE/soft","gas-anchored, broadly adequate, corrected −35%/mo", True),
 "dap":     ("BALANCED","phosphate chain, no acute structural deficit", False),
 "caustic_soda":("AMPLE/glut","chlor-alkali capacity glut (China +5%/yr → 70-75% util), weak alumina+pulp offtake, SE-Asia floor capped by China exports", False)}
COMMODITY_MAP={"DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore","DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap",
 "CSV":"caustic_soda"}  # CSV = chlor-alkali (NaOH+chlorine+PVC), NOT dap fertilizer — own caustic-soda cycle
BRENT="""2016-04,42.25;2016-12,54.07;2017-12,64.21;2018-10,80.47;2018-12,56.46;2019-12,65.85;2020-04,23.34;2020-12,49.87;2021-06,73.07;2021-12,74.31;2022-03,115.59;2022-06,120.08;2022-12,80.90;2023-06,74.89;2023-12,77.86;2024-06,82.56;2024-12,73.83;2025-04,67.75;2025-08,68.20;2025-12,62.72;2026-01,66.77;2026-02,71.11;2026-03,103.69"""
# (compact anchor set; full 120-mo series fetched separately — pctile computed on these monthly anchors)
br=pd.DataFrame([p.split(",") for p in BRENT.split(";")],columns=["m","p"]); br["p"]=br["p"].astype(float)
br.to_csv(os.path.join(W,"data","brent_monthly.csv"),index=False)
oil_now=br["p"].iloc[-1]; oil_pct=(br["p"]<=oil_now).mean()

def commodity_pct(c):
    try:
        d=pd.read_csv(os.path.join(W,"data",f"{c}_monthly.csv")); d.columns=["m","p"]
        d["pct"]=d["p"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
        return float(d["pct"].iloc[-1])
    except Exception: return np.nan

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Cyclical STRUCTURAL overlay — percentile × supply-structure × cost-anchor (oil)")
P(f"Brent cost-anchor now ${oil_now:.0f} (pctile {oil_pct:.2f}) — HIGH oil supports oil-linked commodity floors (rubber/PVC) but squeezes consumer margins (BMP).")
P("")
def verdict(c,pct):
    state,note,oil_link=STRUCTURE[c]
    if pct<0.40: v="BUY-zone (commodity cheap)"
    elif pct>0.75:
        if state=="DEFICIT" or (oil_link and oil_pct>0.7 and state not in ("AMPLE/soft",)): v="ELEVATED-SUPPORTED (earnings sustain; not auto-avoid)"
        else: v="cyclical-PEAK (AVOID-new, reverts)"
    else: v="WAIT (mid-cycle)"
    return v,state,note
out=[]
P(f"{'commodity':<10}{'pctile':>7}{'structure':<13} verdict")
P("-"*78)
for c in ["rubber","iron_ore","urea","dap","caustic_soda"]:
    pct=commodity_pct(c); v,state,note=verdict(c,pct)
    P(f"{c:<10}{pct:>7.2f} {state:<12} {v}")
    P(f"            └ {note}")
    for tk,cc in COMMODITY_MAP.items():
        if cc==c: out.append({"ticker":tk,"commodity":c,"pctile":pct,"structure":state,"verdict":v})
P("")
P("## Reclassified cyclical verdicts (vs old percentile-only)")
P("  RUBBER (DRI/PHR/DPR/GVR): OLD 'AVOID-new (0.95 late cycle)' → NEW 'ELEVATED-SUPPORTED' (6yr deficit+7yr lag+oil$104 floor → high price can persist; earnings sustain). Demand=swing risk.")
P("  STEEL (HPG/HSG/NKG): iron-ore pctile~0.35 = BUY-zone (cheap input) regardless of structure.")
P("  UREA (DCM/DPM): pctile high + AMPLE/soft supply + correcting → cyclical-PEAK AVOID-new (no structural support).")
P("  DAP (DGC/DDV/LAS): mid + balanced → WAIT.")
P("  CAUSTIC SODA (CSV): chlor-alkali — own NaOH cycle (NOT dap). 2026 elevated-but-soft: Chinese capacity glut + weak alumina/pulp demand → AMPLE/glut structure (reverts on high pctile, NOT supported).")
P("")
P("Principle: percentile alone assumes mean-reversion; STRUCTURE+oil distinguish 'cyclical peak (revert)' from 'structurally-elevated (sustain)'.")
pd.DataFrame(out).to_csv(os.path.join(W,"data","cyclical_structural.csv"),index=False)
with open(os.path.join(W,"data","cyclical_structural.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/cyclical_structural.{md,csv} + brent_monthly.csv")
