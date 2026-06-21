#!/usr/bin/env python3
"""
Portfolio manual review + comprehensive metrics for sim_v11_jun2025 trades.
Applies BA picks manual review rules (ba_picks_manual_review_rules.md).
Uses ticker_1m fallback when ticker missing latest data.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

def bq(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); p = f.name
    try:
        cmd = f'type "{p}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, shell=True)
    finally:
        os.unlink(p)
    if r.returncode != 0: raise RuntimeError(r.stdout[:500])
    return pd.read_csv(StringIO(r.stdout))

# ─── Sector classification (per ba_picks_manual_review_rules.md) ──────
COMMODITY_CYCLICAL = {
    # STEEL
    "HPG","HSG","NKG","POM","TLH","SMC",
    # OIL_GAS
    "BSR","PVD","PVS","GAS","PVC","PVB","PVT","PET","PLX","OIL",
    # CHEMICAL (fertilizer + chem)
    "DGC","DCM","DPM","BFC","CSV","AAA","DDV","LAS","PSW",
    # RUBBER
    "GVR","PHR","DPR","TRC","RTB",
    # AQUACULTURE
    "VHC","ANV","MPC","IDI","AAM","ABT","ACL","AGF","ASM","FMC","CMX","TS4",
    # SHIPPING
    "HAH","VOS","GMD","VSC","MVN","PVT","VTO","VST",
    # COAL
    "KSB","TVD","NBC","HLC","TC6","MDC","TDN",
    # CEMENT
    "HT1","BCC","BTS","HOM","BCE","XMC",
    # PAPER_PULP
    "AAA","DHC",
    # AVIATION
    "ACV","HVN","VJC",
    # SUGAR
    "SBT","SLS","KTS","LSS",
}
NON_CYCLICAL = {
    # BANK
    "ACB","BID","CTG","EIB","HDB","MBB","MSB","NAB","OCB","SHB","STB","TCB","VCB","VPB","BAB","BVB","KLB","TPB","VIB","LPB","SGB","ABB","NVB",
    # REIT
    "VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC","TIG","QCG","DIG","DXS","HQC","VPI","CEO","TCH","NTL","CRC","HPX","ITC","SCR",
    "SIP","KBC","IDC","NTC","TIP","BCM","SZB","SZC","LHG","SZL","D2D","IDV","BAX","ITA","SNZ","VRG","VGC","HPI","MH3","TID","LHC","DXP","SZG",
    # INSURANCE
    "BMI","ABI","BIC","PVI","MIG","PGI","BHI","AIC","BLI",
    # SECURITIES
    "SSI","VND","HCM","SHS","VCI","AAS","MBS","BVS","CTS","FTS","AGR","BSI","APS",
    # TEXTILE
    "TCM","GIL","MSH","STK",
    # RETAIL
    "MWG","FRT","DGW","PNJ",
    # DAIRY
    "VNM","MCH","HNM",
    # BEVERAGE
    "SAB","BHN",
}
# Anything else → DEFAULT industrial (not commodity, not strict non-cyclical)

def classify_sector(ticker):
    if ticker in COMMODITY_CYCLICAL: return "COMMODITY"
    if ticker in NON_CYCLICAL:       return "NON_CYCLICAL"
    return "OTHER"

# ─── Load trades ─────────────────────────────────────────────────────
trades = pd.read_csv("sim_v11_jun2025_trades.csv")
trades["entry_date"] = pd.to_datetime(trades["entry_date"])
trades["exit_date"] = pd.to_datetime(trades["exit_date"])
trades["sec_group"] = trades["ticker"].apply(classify_sector)
print(f"Loaded {len(trades)} trades. Sector groups:")
print(trades["sec_group"].value_counts().to_string())

unique_tickers = sorted(trades["ticker"].unique())
print(f"\nUnique tickers: {len(unique_tickers)}")

# ─── Fetch per-ticker FA + price context at entry ────────────────────
# Use UNION ALL fallback to ticker_1m for fresh data per the rule
print("\nFetching per-ticker entry context (FA + 12M ret + MA200 + Cash/MktCap) ...")

tk_list = ",".join(f'"{t}"' for t in unique_tickers)
# Get most recent FA snapshot per ticker before each entry date
fa_q = f"""
WITH ranked AS (
  SELECT f.ticker, f.time, f.quarter, f.Release_Date,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
    f.GPM_P0, f.GPM_P4, f.OShares, f.Close AS close_at_release,
    f.Cash_P0, f.PE, f.PE_MA5Y, f.PE_SD5Y, f.ROE_Min5Y,
    ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) AS rn
  FROM tav2_bq.ticker_financial AS f
  WHERE f.ticker IN ({tk_list}) AND f.time <= "2026-01-31"
)
SELECT * FROM ranked WHERE rn <= 3
"""
fa = bq(fa_q)
fa["time"] = pd.to_datetime(fa["time"])
print(f"  FA snapshots: {len(fa)} rows")

# Pull price history from ticker + ticker_1m fallback (data freshness rule)
print("Fetching price history (ticker + ticker_1m fallback) ...")
price_q = f"""
SELECT t.ticker, t.time, t.Close, t.MA200, 'ticker' AS src
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tk_list}) AND t.time BETWEEN "2024-05-01" AND "2026-05-31"
UNION ALL
SELECT t.ticker, t.time, t.Close, t.MA200, 'ticker_1m' AS src
FROM tav2_bq.ticker_1m AS t
WHERE t.ticker IN ({tk_list}) AND t.time BETWEEN "2024-05-01" AND "2026-05-31"
  AND NOT EXISTS (
    SELECT 1 FROM tav2_bq.ticker AS t2
    WHERE t2.ticker = t.ticker AND t2.time = t.time AND t2.Close IS NOT NULL
  )
"""
px = bq(price_q)
px["time"] = pd.to_datetime(px["time"])
px = px.sort_values(["ticker","time"]).reset_index(drop=True)
print(f"  Price rows: {len(px):,} (sources: {px['src'].value_counts().to_dict()})")

# ─── Build context per trade ─────────────────────────────────────────
def context_at_entry(row):
    """Get review context for one trade at entry_date."""
    tk = row["ticker"]; ed = row["entry_date"]
    ctx = {"ticker":tk, "entry_date":ed, "sec_group":row["sec_group"]}

    # Most recent FA snapshot before entry
    fa_t = fa[(fa["ticker"]==tk) & (fa["time"] <= ed)].sort_values("time").tail(1)
    if len(fa_t) > 0:
        f = fa_t.iloc[0]
        ttm_now = sum(f.get(f"NP_P{i}", np.nan) for i in range(4))
        ttm_prv = sum(f.get(f"NP_P{i}", np.nan) for i in range(4,8))
        ctx["NP_TTM_growth"] = (ttm_now - ttm_prv)/abs(ttm_prv) if abs(ttm_prv) > 1e3 else np.nan
        ctx["GPM_chg"] = f.get("GPM_P0", np.nan) - f.get("GPM_P4", np.nan)
        mc = f.get("close_at_release", np.nan) * f.get("OShares", np.nan)
        ctx["MktCap_at_rel"] = mc
        ctx["Cash_MktCap"] = f.get("Cash_P0", np.nan) / mc if mc > 0 else np.nan
        ctx["PE_z"] = (f.get("PE", np.nan) - f.get("PE_MA5Y", np.nan)) / f.get("PE_SD5Y", 1) if f.get("PE_SD5Y", 0) > 0 else np.nan
        ctx["ROE_Min5Y"] = f.get("ROE_Min5Y", np.nan)
    else:
        for k in ["NP_TTM_growth","GPM_chg","Cash_MktCap","PE_z","ROE_Min5Y","MktCap_at_rel"]:
            ctx[k] = np.nan

    # 12M prior return + MA200 ratio
    px_t = px[px["ticker"]==tk].sort_values("time")
    if len(px_t) > 0:
        at_entry = px_t[px_t["time"] <= ed].tail(1)
        yr_ago = px_t[px_t["time"] <= (ed - pd.Timedelta(days=365))].tail(1)
        if len(at_entry) > 0 and len(yr_ago) > 0:
            ctx["ret_12M"] = at_entry["Close"].iloc[0] / yr_ago["Close"].iloc[0] - 1
            ma200 = at_entry["MA200"].iloc[0]
            close_e = at_entry["Close"].iloc[0]
            ctx["close_ma200"] = close_e / ma200 if ma200 and ma200 > 0 else np.nan
        else:
            ctx["ret_12M"] = np.nan; ctx["close_ma200"] = np.nan
    else:
        ctx["ret_12M"] = np.nan; ctx["close_ma200"] = np.nan
    return ctx

contexts = pd.DataFrame([context_at_entry(r) for _, r in trades.iterrows()])
review = trades.merge(contexts, on=["ticker","entry_date","sec_group"], how="left")

# ─── Apply manual review rules ───────────────────────────────────────
def apply_rules(r):
    flags = []
    tk = r["ticker"]; sec = r["sec_group"]
    np_ttm = r.get("NP_TTM_growth"); gpm = r.get("GPM_chg"); ret_12m = r.get("ret_12M")
    cm200 = r.get("close_ma200"); cash_mc = r.get("Cash_MktCap"); pe_z = r.get("PE_z")

    # Rule 4: Commodity peak warning
    if sec == "COMMODITY":
        peak_indicators = 0
        if pd.notna(np_ttm) and np_ttm > 0.30: peak_indicators += 1
        if pd.notna(ret_12m) and ret_12m > 0.40: peak_indicators += 1
        if pd.notna(gpm) and gpm > 5.0: peak_indicators += 1
        if pd.notna(cm200) and cm200 > 1.30: peak_indicators += 1
        if peak_indicators >= 2:
            flags.append(f"R4 PEAK ({peak_indicators}/4 indicators)")

        # Rule 7: Commodity trough buy
        trough_ok = (pd.notna(np_ttm) and np_ttm < -0.20 and
                     pd.notna(ret_12m) and ret_12m < -0.25 and
                     pd.notna(cm200) and cm200 > 1.0 and
                     pd.notna(cash_mc) and cash_mc > 0.15)
        if trough_ok:
            flags.append("R7 TROUGH BUY ✓")

    # Rule 6: Non-cyclical NP decline
    if sec == "NON_CYCLICAL" and pd.notna(np_ttm) and np_ttm < -0.10:
        flags.append(f"R6 NP_decline {np_ttm*100:.0f}%")

    # Rule 1: Cash buffer bonus
    if pd.notna(cash_mc) and cash_mc >= 0.20:
        flags.append(f"R1 cash {cash_mc*100:.0f}%")

    # Rule 2: Value confirmation
    if pd.notna(pe_z) and pe_z < -1.0:
        flags.append(f"R2 PE_z {pe_z:.2f}")

    # Rule 3: Non-cyclical strong NP growth
    if sec == "NON_CYCLICAL" and pd.notna(np_ttm) and np_ttm > 0.15:
        flags.append(f"R3 NP+{np_ttm*100:.0f}%")

    return " | ".join(flags) if flags else ""

review["review_flags"] = review.apply(apply_rules, axis=1)
review["red_flag"] = review["review_flags"].str.contains("R4 PEAK|R6 NP_decline", na=False)
review["green_flag"] = review["review_flags"].str.contains("R1 cash|R2 PE_z|R3 NP\\+|R7 TROUGH", na=False)

# ─── Print trade-by-trade review ─────────────────────────────────────
print("\n" + "="*135)
print(f"  MANUAL REVIEW — {len(trades)} trades from {trades['entry_date'].min().date()} to {trades['exit_date'].max().date()}")
print("="*135)
print(f"\n{'#':<3}{'Ticker':<7}{'Entry':<12}{'Sec':<14}{'Ret%':>8}{'NP_TTM':>9}{'12M':>8}"
      f"{'Cash%':>7}{'PE_z':>7}  Flags")
print("-"*135)
for i, r in review.iterrows():
    np_str = f"{r['NP_TTM_growth']*100:+.0f}%" if pd.notna(r['NP_TTM_growth']) else "n/a"
    r12_str = f"{r['ret_12M']*100:+.0f}%" if pd.notna(r['ret_12M']) else "n/a"
    cash_str = f"{r['Cash_MktCap']*100:.0f}%" if pd.notna(r['Cash_MktCap']) else "n/a"
    pez_str = f"{r['PE_z']:+.2f}" if pd.notna(r['PE_z']) else "n/a"
    icon = "🔴" if r["red_flag"] else ("🟢" if r["green_flag"] else "  ")
    print(f"{icon}{i+1:<3}{r['ticker']:<7}{str(r['entry_date'].date()):<12}{r['sec_group']:<14}"
          f"{r['ret_net']*100:>+7.2f}%{np_str:>9}{r12_str:>8}{cash_str:>7}{pez_str:>7}  {r['review_flags']}")

# ─── Rule effectiveness analysis ─────────────────────────────────────
print("\n" + "="*100)
print("  RULE EFFECTIVENESS — what if we had applied these rules?")
print("="*100)
print()

red = review[review["red_flag"]]
green = review[review["green_flag"]]
neutral = review[~review["red_flag"] & ~review["green_flag"]]

def stat_group(df, label):
    if len(df) == 0:
        print(f"  {label}: N=0"); return
    avg = df["ret_net"].mean()*100
    wr = (df["ret_net"]>0).mean()*100
    stops = (df["reason"]=="STOP").sum()
    print(f"  {label:<35}: N={len(df):3d}  Avg={avg:+.2f}%  WR={wr:.1f}%  Stops={stops}")

stat_group(red, "🔴 RED flagged (R4/R6)")
stat_group(green, "🟢 GREEN flagged (R1/R2/R3/R7)")
stat_group(neutral, "   Neutral")
stat_group(review, "TOTAL")

# Sector group performance
print(f"\n  By sector group:")
for sec in ["COMMODITY","NON_CYCLICAL","OTHER"]:
    stat_group(review[review["sec_group"]==sec], f"  {sec}")

# Sim if we skipped RED-flagged
print(f"\n  Counterfactual: skip RED-flagged picks")
non_red = review[~review["red_flag"]]
if len(non_red) > 0:
    stat_group(non_red, "  After skip-RED")

# ─── Portfolio summary metrics ───────────────────────────────────────
print("\n" + "="*100)
print("  📊 COMPREHENSIVE PORTFOLIO METRICS — Jun 2025 → Mar 2026")
print("="*100)

# Load NAV
nav = pd.read_csv("sim_v11_jun2025_nav.csv")
nav["time"] = pd.to_datetime(nav["time"])
START = pd.Timestamp("2025-06-09"); END = pd.Timestamp("2026-05-14")
nav_w = nav[(nav["time"]>=START) & (nav["time"]<=END)].copy()

# Load VNI for comparison
vni = bq(f"""
SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN '{START.date()}' AND '{END.date()}'
UNION ALL
SELECT t.time, t.Close FROM tav2_bq.ticker_1m AS t WHERE t.ticker='VNI' AND t.time BETWEEN '{START.date()}' AND '{END.date()}'
AND NOT EXISTS (SELECT 1 FROM tav2_bq.ticker AS t2 WHERE t2.ticker='VNINDEX' AND t2.time=t.time)
ORDER BY time
""")
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni["ret"] = vni["Close"].pct_change()

INIT_NAV = 50e9
final_nav = nav_w["nav"].iloc[-1]
total_ret = final_nav/INIT_NAV - 1
n_days = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days
yrs = n_days / 365.25
cagr = (final_nav/INIT_NAV)**(1/yrs) - 1
rets = nav_w["nav"].pct_change().dropna()
sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
downside = rets[rets<0]
sortino = rets.mean()/downside.std() * np.sqrt(252) if len(downside) and downside.std() > 0 else 0
peak = nav_w["nav"].cummax(); dd_series = (nav_w["nav"] - peak) / peak
max_dd = dd_series.min()
# DD duration
in_dd = dd_series < 0
dd_dur = 0; cur_dur = 0
for v in in_dd:
    if v: cur_dur += 1; dd_dur = max(dd_dur, cur_dur)
    else: cur_dur = 0
calmar = cagr/abs(max_dd) if max_dd<0 else 0
vol_annual = rets.std() * np.sqrt(252)

# VNI alignment
vni_w = vni[(vni["time"]>=START) & (vni["time"]<=END)].copy()
if len(vni_w) > 1:
    vni_total = vni_w["Close"].iloc[-1]/vni_w["Close"].iloc[0] - 1
    vni_cagr = (1+vni_total)**(1/yrs) - 1
    vni_rets = vni_w["ret"].dropna()
    vni_sharpe = vni_rets.mean()/vni_rets.std()*np.sqrt(252) if vni_rets.std() > 0 else 0
    vni_vol = vni_rets.std() * np.sqrt(252)
else:
    vni_total = vni_cagr = vni_sharpe = vni_vol = np.nan

# Alpha vs VNI
alpha_total = (total_ret - vni_total) * 100 if pd.notna(vni_total) else np.nan
alpha_cagr = (cagr - vni_cagr) * 100 if pd.notna(vni_cagr) else np.nan

# Trade-level metrics
ret_col = trades["ret_net"]
winners = trades[ret_col>0]; losers = trades[ret_col<=0]
gross_profit = winners["ret_net"].sum() * 5e9  # ~5B per trade
gross_loss = abs(losers["ret_net"].sum()) * 5e9
profit_factor = gross_profit/gross_loss if gross_loss > 0 else np.nan
avg_win = winners["ret_net"].mean()*100 if len(winners) > 0 else 0
avg_loss = losers["ret_net"].mean()*100 if len(losers) > 0 else 0
expectancy = (avg_win * len(winners) + avg_loss * len(losers)) / len(trades)
max_win = ret_col.max()*100
max_loss = ret_col.min()*100

# Time in market vs cash
deployed_avg = (nav_w["deployed_pct"]).mean()
cash_avg = (nav_w["cash_pct"]).mean()
days_full = (nav_w["deployed_pct"] >= 90).sum()
days_cash = (nav_w["cash_pct"] >= 50).sum()

print(f"\n  📅 Period: {START.date()} → {nav_w['time'].iloc[-1].date()} ({n_days} days, {yrs:.2f} yrs)")
print(f"\n  💰 RETURNS")
print(f"     Total Return:    {total_ret*100:>+10.2f}%  ({final_nav/1e9:.3f}B from {INIT_NAV/1e9:.0f}B)")
print(f"     CAGR:            {cagr*100:>+10.2f}%")
print(f"     VNI Total Ret:   {vni_total*100:>+10.2f}%")
print(f"     VNI CAGR:        {vni_cagr*100:>+10.2f}%")
print(f"     Alpha vs VNI:    {alpha_cagr:>+10.2f}pp CAGR  ({alpha_total:+.2f}pp total)")
print(f"\n  ⚖ RISK-ADJUSTED")
print(f"     Sharpe:          {sharpe:>10.2f}")
print(f"     Sortino:         {sortino:>10.2f}")
print(f"     Calmar:          {calmar:>10.2f}")
print(f"     Annual Volatility:{vol_annual*100:>+9.2f}%   (vs VNI: {vni_vol*100:.2f}%)")
print(f"\n  📉 DRAWDOWN")
print(f"     Max DD:          {max_dd*100:>+10.2f}%")
print(f"     DD Duration:     {dd_dur:>10d} days")
print(f"\n  🎯 TRADE QUALITY")
print(f"     Trades:          {len(trades):>10d}  (Winners {len(winners)} | Losers {len(losers)})")
print(f"     Win Rate:        {len(winners)/len(trades)*100:>+10.1f}%")
print(f"     Avg Win:         {avg_win:>+10.2f}%")
print(f"     Avg Loss:        {avg_loss:>+10.2f}%")
print(f"     Win/Loss Ratio:  {abs(avg_win/avg_loss):>10.2f}x")
print(f"     Profit Factor:   {profit_factor:>10.2f}")
print(f"     Expectancy/trade:{expectancy:>+10.2f}%")
print(f"     Max Win:         {max_win:>+10.2f}%")
print(f"     Max Loss:        {max_loss:>+10.2f}%")
print(f"     STOP exits:      {(trades['reason']=='STOP').sum():>10d}  ({(trades['reason']=='STOP').mean()*100:.1f}%)")
print(f"     TIME exits:      {(trades['reason']=='TIME').sum():>10d}  ({(trades['reason']=='TIME').mean()*100:.1f}%)")
print(f"     Avg Hold:        {trades['days_held'].mean():>10.1f} days")
print(f"\n  📊 CAPITAL UTILIZATION")
print(f"     Avg Deployed%:   {deployed_avg:>+10.1f}%")
print(f"     Avg Cash%:       {cash_avg:>+10.1f}%")
print(f"     Days fully deployed (≥90%):{days_full:>5d}/{len(nav_w)}  ({days_full/len(nav_w)*100:.1f}%)")
print(f"     Days mostly cash (≥50%):   {days_cash:>5d}/{len(nav_w)}  ({days_cash/len(nav_w)*100:.1f}%)")

# Sector exposure
print(f"\n  🏛 SECTOR EXPOSURE (by # trades)")
sec_summary = trades.groupby(trades["ticker"].apply(classify_sector)).agg(
    n=("ticker","count"),
    avg_ret=("ret_net", lambda x: x.mean()*100),
    wr=("ret_net", lambda x: (x>0).mean()*100),
    stops=("reason", lambda x: (x=="STOP").sum()),
).reset_index()
sec_summary.columns = ["Sector","N","Avg%","WR%","Stops"]
print(sec_summary.to_string(index=False, float_format="%.2f"))

# Save outputs
review[["ticker","entry_date","exit_date","ret_net","sec_group","NP_TTM_growth","ret_12M",
        "Cash_MktCap","PE_z","close_ma200","review_flags"]].to_csv("portfolio_review_jun2025.csv", index=False)
print("\n💾 Saved portfolio_review_jun2025.csv")
