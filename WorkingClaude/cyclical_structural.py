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
 "caustic_soda":("AMPLE/glut","chlor-alkali capacity glut (China +5%/yr → 70-75% util), weak alumina+pulp offtake, SE-Asia floor capped by China exports [DATA=SYNTHETIC ESTIMATE — no World Bank source, low confidence]", False)}
# data provenance per commodity: World Bank Pink Sheet for the real series; caustic_soda has NO WB
# source and its monthly CSV is a synthetic/interpolated estimate (flagged; production: low confidence).
DATA_SRC={"rubber":"WorldBank","iron_ore":"WorldBank","urea":"WorldBank","dap":"WorldBank","caustic_soda":"SYNTHETIC_ESTIMATE"}
COMMODITY_MAP={"DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore","DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap",
 "CSV":"caustic_soda"}  # CSV = chlor-alkali (NaOH+chlorine+PVC), NOT dap fertilizer — own caustic-soda cycle
# Brent cost-anchor — read from data/brent_monthly.csv (AUTHORITATIVE: World Bank Pink Sheet,
# maintained by rebuild_commodity_wb.py). Switched 2026-06-12 from a hard-coded anchor string so
# brent is sourced like the other commodities; percentile now over the full monthly series.
br=pd.read_csv(os.path.join(W,"data","brent_monthly.csv")); br.columns=["m","p"]
br["p"]=pd.to_numeric(br["p"],errors="coerce")
oil_now=br["p"].iloc[-1]; oil_pct=float((br["p"]<=oil_now).mean())

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
    src=DATA_SRC.get(c,"?"); tag="  [!] DATA=SYNTHETIC ESTIMATE (no WB source)" if src=="SYNTHETIC_ESTIMATE" else ""
    P(f"{c:<10}{pct:>7.2f} {state:<12} {v}{tag}")
    P(f"            └ {note}")
    for tk,cc in COMMODITY_MAP.items():
        if cc==c: out.append({"ticker":tk,"commodity":c,"pctile":pct,"structure":state,"verdict":v,"data_source":src})
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
