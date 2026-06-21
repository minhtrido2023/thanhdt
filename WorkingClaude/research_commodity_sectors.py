#!/usr/bin/env python3
"""
research_commodity_sectors.py
=============================
Research sector-cycle factors for Vietnamese commodity-sensitive industries.

Steps:
  1) Manually tag commodity groups (Rubber, Shipping, Chemical, Steel, Oil_Gas, Aquaculture, etc.)
  2) Compute group-level metrics per quarter:
     - sector_momentum_6M (avg 6M return of group leaders)
     - sector_NP_peak_ratio (median group NP_P0/max ratio)
     - sector_GPM_trend (median group GPM change)
     - sector_PE_dispersion (group avg PE_z)
  3) Test if these sector factors generate alpha vs forward returns
  4) Build "cycle-position" composite and test against v8c baseline
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

# ─── COMMODITY GROUP DEFINITIONS ─────────────────────────────────────────
COMMODITY_GROUPS = {
    "RUBBER":       ["GVR","PHR","DPR","DRI","DRC","SRC","TRC","TNC","HRC","RTB"],
    "SHIPPING":     ["HAH","GMD","VSC","VOS","VTO","VIP","PVT","VNL","TNP","STG","DVP","SGP","HMH"],
    "CHEMICAL":     ["DGC","DCM","DPM","LAS","CSV","BFC","RDP","PLP","PLC","HVT","NET","DGW"],
    "STEEL":        ["HPG","HSG","NKG","POM","TLH","VGS","SMC","TVN","TIS","HMC","DTL","KKC"],
    "OIL_GAS":      ["BSR","PVD","PVS","PVT","GAS","OIL","PVC","PVB","PXT","PVG","PXS","CNG","PGD","PGS"],
    "AQUACULTURE":  ["VHC","ANV","MPC","IDI","FMC","ACL","CMX","ABT","ASM","TS4"],
    "TEXTILE":      ["TCM","TNG","GIL","MSH","STK","VGT","TET","ADS","PPH","HTG"],
    "CEMENT":       ["HT1","BCC","HOM","BTS","HVX","CCM","QNC"],
    "SUGAR":        ["SBT","LSS","KTS","SLS"],
    "COAL":         ["KSB","TVD","NBC","TC6","HLC","THT","MDC","CST","TDN","TCS"],
    "AVIATION":     ["HVN","VJC","ACV"],
    "PAPER_PULP":   ["DHC","DHP","BST","HHP"],
    "REIT_RES":     ["VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC","TIG","QCG","DIG","DXS","HQC","ITC","SCR","VPI","CEO","TCH","NTL"],
    "REIT_KCN":     ["KBC","ITA","IDC","SZL","SZC","D2D","NTC","SIP","BCM","LHG","TIP","TIX"],
    "BANK":         ["VCB","BID","CTG","TCB","MBB","ACB","STB","VPB","HDB","TPB","SHB","EIB","LPB","VIB","MSB","OCB","SSB","ABB","KLB","NAB","SGB","NVB","BVB","BAB","PGB","VAB","VBB"],
    "SECURITIES":   ["SSI","VND","HCM","VCI","SHS","MBS","BVS","AGR","BSI","ORS","CTS","FTS","TVS","TCI"],
    "REAL_ESTATE_DIVERSIFIED": ["VIC","NLG","KDH","DXG"],  # holding companies
    "RETAIL":       ["MWG","PNJ","DGW","FRT","PNJ","CTF"],
    "INSURANCE":    ["BVH","BMI","PVI","ABI","MIG","BIC","PGI"],
    "DAIRY":        ["VNM","SVD","HNM"],
    "BEVERAGE":     ["SAB","BHN","HAD","BSP","BVL"],
}

# Reverse mapping: ticker -> group
TICKER_GROUP = {}
for grp, tks in COMMODITY_GROUPS.items():
    for tk in tks:
        if tk not in TICKER_GROUP:  # avoid overwriting (e.g., PVT)
            TICKER_GROUP[tk] = grp

# ─── LOAD PANEL ──────────────────────────────────────────────────────────
df = pd.read_csv("lh_v3_factor_panel_v2.csv", parse_dates=["time"])
df["cmd_group"] = df["ticker"].map(TICKER_GROUP).fillna("OTHER")
print(f"Loaded {len(df):,} rows")
print(f"Ticker coverage in commodity groups: {(df['cmd_group']!='OTHER').sum() / len(df) * 100:.1f}%")
print(f"\nGroup distribution:")
print(df.groupby("cmd_group").agg(n_rows=("ticker","size"), n_tickers=("ticker","nunique")).sort_values("n_rows", ascending=False).head(15).to_string())

# ─── COMPUTE SECTOR-LEVEL FACTORS PER QUARTER ───────────────────────────
print("\nComputing sector-level metrics per quarter ...")
sector_metrics = []
for (q, grp), g in df.groupby(["quarter","cmd_group"]):
    if grp == "OTHER" or len(g) < 2: continue
    sector_metrics.append({
        "quarter": q,
        "cmd_group": grp,
        "n_tickers": len(g),
        "S_ret_6m_med":       g["F_ret_6m"].median(),       # sector momentum 6M
        "S_ret_12m_med":      g["F_ret_12m"].median(),      # sector momentum 12M
        "S_NP_peak_ratio_med": g["F_NP_peak_ratio"].median(),  # peak detection
        "S_GPM_change_med":   g["F_GPM_change"].median(),
        "S_NP_yoy_med":       g["F_NP_TTM_growth"].median(),
        "S_PE_z_med":         g["F_PE_z"].median(),
        "S_smoothed_EY_med":  g["F_smoothed_EY"].median(),
        "S_FCF_yield_med":    g["F_FCF_yield"].median(),
        "S_ret_3m_med":       g["F_ret_3m"].median(),
    })
sec_df = pd.DataFrame(sector_metrics)
print(f"  Built {len(sec_df)} (quarter,group) sector aggregate rows")

# Cycle position indicator: positive (upcycle/recovery) vs negative (peak/downcycle)
# Upcycle: NP_yoy improving, GPM improving, PE low → CHEAP and recovering
# Downcycle: NP at peak, PE extended → EXPENSIVE and topping

# Z-score sector metrics within each quarter (cross-sector comparison)
for col in ["S_ret_6m_med","S_ret_12m_med","S_NP_peak_ratio_med","S_GPM_change_med",
            "S_NP_yoy_med","S_PE_z_med","S_smoothed_EY_med","S_ret_3m_med"]:
    sec_df[f"{col}_z"] = sec_df.groupby("quarter")[col].transform(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0)

# Cycle composite: high = recovery/early upcycle (buy), low = peak/late upcycle (sell)
# Bullish factors: NP recovering (NP_yoy_z high), GPM improving, low PE (cheap)
# Bearish factors: NP at peak (peak_ratio_z high = at peak = sell signal), recent strong momentum (overheated)
sec_df["cycle_recovery"] = (sec_df["S_NP_yoy_med_z"] + sec_df["S_GPM_change_med_z"]
                              + sec_df["S_smoothed_EY_med_z"] - sec_df["S_NP_peak_ratio_med_z"]) / 4
sec_df["cycle_overheat"] = (sec_df["S_ret_12m_med_z"] + sec_df["S_NP_peak_ratio_med_z"]) / 2

# Merge back to panel
df = df.merge(sec_df[["quarter","cmd_group","S_ret_6m_med","S_ret_12m_med","S_NP_yoy_med",
                       "S_NP_peak_ratio_med","S_GPM_change_med","S_smoothed_EY_med",
                       "cycle_recovery","cycle_overheat","S_ret_6m_med_z","S_NP_yoy_med_z",
                       "S_NP_peak_ratio_med_z","S_GPM_change_med_z","S_smoothed_EY_med_z",
                       "S_ret_3m_med_z","S_ret_12m_med_z","S_PE_z_med_z"]],
              on=["quarter","cmd_group"], how="left")

# Diagnostic: cycle_recovery for key groups across history
print("\n--- Cycle recovery indicator history (selected groups) ---")
pivot = sec_df.pivot_table(index="quarter", columns="cmd_group", values="cycle_recovery")
key_groups = ["RUBBER","SHIPPING","CHEMICAL","STEEL","OIL_GAS","AQUACULTURE","REIT_KCN"]
print(pivot[[g for g in key_groups if g in pivot.columns]].tail(20).round(2).to_string())

# ─── IC ANALYSIS: SECTOR FACTORS ─────────────────────────────────────────
def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 100: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

print("\n" + "="*120)
print("  SECTOR-LEVEL FACTOR IC vs forward returns (only commodity groups)")
print("="*120)

cmd_only = df[df["cmd_group"] != "OTHER"].copy()
sector_factors = [
    "S_ret_6m_med", "S_ret_12m_med", "S_ret_3m_med",
    "S_NP_peak_ratio_med", "S_GPM_change_med", "S_NP_yoy_med",
    "S_smoothed_EY_med", "cycle_recovery", "cycle_overheat",
]
print(f"\n  {'Factor':<26}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'N':>10}")
for f in sector_factors:
    if f not in cmd_only.columns: continue
    row = [f]
    for hzn in ["O3M_ret","O6M_ret","O1Y_ret","O2Y_ret"]:
        ic, n = spearman_ic(cmd_only[f], cmd_only[hzn])
        row.append(ic)
    n = cmd_only.dropna(subset=[f,"O1Y_ret"]).shape[0]
    print(f"  {row[0]:<26}{row[1]:>+8.4f}{row[2]:>+8.4f}{row[3]:>+8.4f}{row[4]:>+8.4f}{n:>10}")

# ─── PER-GROUP CYCLE PERFORMANCE ─────────────────────────────────────────
print("\n" + "="*120)
print("  PER-GROUP: HIGH vs LOW cycle_recovery → forward 1Y return")
print("="*120)

print(f"\n  {'Group':<25}{'N':>6}{'high_cyc_med':>16}{'low_cyc_med':>16}{'spread':>10}{'IC':>8}")
for grp in sorted(df["cmd_group"].unique()):
    if grp == "OTHER": continue
    g = df[(df["cmd_group"]==grp) & df["O1Y_ret"].notna() & df["cycle_recovery"].notna()]
    if len(g) < 50: continue
    high = g[g["cycle_recovery"] > g["cycle_recovery"].quantile(0.7)]
    low = g[g["cycle_recovery"] < g["cycle_recovery"].quantile(0.3)]
    if len(high) < 5 or len(low) < 5: continue
    high_m = high["O1Y_ret"].median(); low_m = low["O1Y_ret"].median()
    ic, _ = spearman_ic(g["cycle_recovery"], g["O1Y_ret"])
    print(f"  {grp:<25}{len(g):>6}{high_m:>+15.2f}%{low_m:>+15.2f}%{high_m-low_m:>+9.2f}pp{ic:>+8.3f}")

# ─── COMBINED FACTOR: v8c + cycle_recovery ───────────────────────────────
print("\n" + "="*120)
print("  COMBINED v8c + cycle_recovery composite vs v8c alone")
print("="*120)

if "v8c_score" not in df.columns:
    fa = pd.read_csv("fa_ratings_lh.csv", usecols=["ticker","quarter","score"]).rename(columns={"score":"v8c_score"})
    df_c = df.merge(fa, on=["ticker","quarter"], how="left")
else:
    df_c = df.copy()

# Build C11: v8c + sector cycle overlay
# Rank both within quarter, weighted
df_c["v8c_rank"] = df_c.groupby("quarter")["v8c_score"].rank(pct=True)
# For cycle_recovery, only use within commodity groups; for OTHER, use neutral 0.5
df_c["cycle_rank"] = df_c.groupby("quarter")["cycle_recovery"].rank(pct=True)
df_c.loc[df_c["cmd_group"]=="OTHER", "cycle_rank"] = 0.5

df_c["C11_v8c_cycle"] = 0.70 * df_c["v8c_rank"] + 0.30 * df_c["cycle_rank"]
df_c["C12_v8c_anticyc"] = 0.70 * df_c["v8c_rank"] - 0.30 * df_c.groupby("quarter")["cycle_overheat"].rank(pct=True).fillna(0.5)

print(f"\n  {'Composite':<22}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'top10_1Y':>12}{'spread':>10}")
for name in ["v8c_score","C11_v8c_cycle","C12_v8c_anticyc"]:
    ic_3m, _ = spearman_ic(df_c[name], df_c["O3M_ret"])
    ic_6m, _ = spearman_ic(df_c[name], df_c["O6M_ret"])
    ic_1y, _ = spearman_ic(df_c[name], df_c["O1Y_ret"])
    ic_2y, _ = spearman_ic(df_c[name], df_c["O2Y_ret"])
    df_v = df_c.dropna(subset=[name,"O1Y_ret"]).copy()
    df_v["dec"] = df_v.groupby("quarter")[name].rank(pct=True)
    top10 = df_v[df_v["dec"] >= 0.90]
    print(f"  {name:<22}{ic_3m:>+8.4f}{ic_6m:>+8.4f}{ic_1y:>+8.4f}{ic_2y:>+8.4f}{top10['O1Y_ret'].median():>+11.2f}%{(top10['O1Y_ret'].median() - df_v['O1Y_ret'].median()):>+9.2f}pp")

# ─── 5 KEY GROUP DEEP-DIVE: when to buy/sell each ────────────────────────
print("\n" + "="*120)
print("  KEY GROUP DEEP-DIVE: cycle history + best entry/exit signals")
print("="*120)

KEY = {
    "RUBBER":      "Giá cao su tự nhiên",
    "SHIPPING":    "Container/bulk freight",
    "CHEMICAL":    "Yellow phosphorus / fertilizer chemical",
    "STEEL":       "Steel/iron ore",
    "OIL_GAS":     "Brent / natural gas",
    "AQUACULTURE": "Shrimp / cá tra prices, USD/VND",
}

for grp, driver in KEY.items():
    print(f"\n--- {grp} (driver: {driver}) ---")
    g = sec_df[sec_df["cmd_group"]==grp].sort_values("quarter")
    if len(g) == 0: continue
    # Show last 12 quarters
    recent = g.tail(12)
    print(f"  {'quarter':<10}{'avg_ret_6m':>12}{'NP_peak':>10}{'GPM_chg':>10}{'NP_yoy':>10}{'cycle_recovery':>17}{'cycle_overheat':>16}")
    for _, r in recent.iterrows():
        print(f"  {r['quarter']:<10}{r['S_ret_6m_med']*100:>+11.1f}%{r['S_NP_peak_ratio_med']:>+10.2f}{r['S_GPM_change_med']*100:>+9.1f}%{r['S_NP_yoy_med']*100:>+9.1f}%{r['cycle_recovery']:>+16.2f}{r['cycle_overheat']:>+15.2f}")

# Save
df_c.to_csv("lh_v3_factor_panel_cycle.csv", index=False)
sec_df.to_csv("lh_v3_sector_cycle.csv", index=False)
print("\nSaved: lh_v3_factor_panel_cycle.csv, lh_v3_sector_cycle.csv")
print("DONE")
