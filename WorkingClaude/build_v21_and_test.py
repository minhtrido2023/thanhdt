# -*- coding: utf-8 -*-
"""
build_v21_and_test.py
=====================
1. Xây dựng v2.1 = v2 canonical + US emergency override + SBV circuit breaker
   Smoothing: mode(3) + min_stay(7) → match v2 stability, 0 stays ≤5d
2. So sánh transition stats v2 / v2.1 / v3.4b
3. Integrated test V4/V5 với v2.1 state vs TQ34b (v3.4b) state
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re, json, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ─── 1. Build v2.1 state series ───────────────────────────────────────────────
print("="*80)
print("  STEP 1: Build v2.1 = v2 + US circuit breaker + SBV circuit breaker")
print("="*80)

v2 = pd.read_csv("data/vnindex_5state_history.csv"); v2["time"] = pd.to_datetime(v2["time"])
us = pd.read_csv("deploy_v3_4b_package/us_market_history.csv"); us["time"] = pd.to_datetime(us["time"])
with open("sbv_refi_events.json") as f: sbv_raw = json.load(f)

# US cap
def us_shock_cap(spx_dd, vix):
    if pd.isna(spx_dd) or pd.isna(vix): return 5
    if spx_dd < -0.25 or vix > 35: return 1
    if spx_dd < -0.15 or vix > 30: return 2
    if spx_dd < -0.10 or vix > 25: return 3
    return 5

us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    idx = bisect.bisect_right(us_dates, t - pd.Timedelta(days=1))
    return us_dates[idx-1] if idx > 0 else None
v2["us_date"] = v2["time"].apply(nearest_us)
v2 = v2.merge(us[["time","vix","spx_dd_1y"]], left_on="us_date", right_on="time",
              how="left", suffixes=("","_us"))
v2["us_cap"] = v2.apply(lambda r: us_shock_cap(r["spx_dd_1y"], r["vix"]), axis=1)

# SBV cap
sbv_events = sbv_raw["events"]
sbv_df = pd.DataFrame(sbv_events, columns=["date","rate"])
sbv_df["date"] = pd.to_datetime(sbv_df["date"])
sbv_dates2 = sorted(sbv_df["date"].tolist()); sbv_map = dict(zip(sbv_df["date"], sbv_df["rate"]))
def get_refi(t):
    idx = bisect.bisect_right(sbv_dates2, t) - 1
    return sbv_map[sbv_dates2[idx]] if idx >= 0 else np.nan
v2["refi"] = v2["time"].apply(get_refi)
v2["refi_chg_90d"] = v2["refi"] - v2["refi"].shift(63)
def sbv_cap_fn(refi, chg):
    if pd.isna(refi): return 5
    if refi >= 13: return 2
    if not pd.isna(chg) and chg >= 3: return 3
    return 5
v2["sbv_cap"] = v2.apply(lambda r: sbv_cap_fn(r["refi"], r["refi_chg_90d"]), axis=1)

# Apply caps
raw_cap = np.minimum(np.minimum(v2["state"].values, v2["us_cap"].values),
                     v2["sbv_cap"].values).astype(int)

# Smoothing: mode(3) + min_stay(7) — same strength as v2's own pipeline
def rolling_mode(states, w=3):
    out = states.copy()
    for t in range(w-1, len(states)):
        win = states[t-w+1:t+1]; vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out

def min_stay_filter(states, m):
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if j - i < m:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

s_21 = rolling_mode(raw_cap, 3)
s_21 = min_stay_filter(s_21, 7)   # ← 0 stays ≤5d
v2["state_v21"] = s_21

# Save v2.1
out_v21 = v2[["time","state_v21"]].rename(columns={"state_v21":"state"})
out_v21["time"] = out_v21["time"].dt.strftime("%Y-%m-%d")
out_v21.to_csv("data/vnindex_5state_v21.csv", index=False)
print(f"  Saved: vnindex_5state_v21.csv ({len(out_v21)} rows)")

# Segment stats helper
def seg_stats(arr):
    segs = []; i = 0; sv = np.array(arr)
    while i < len(sv):
        j = i+1
        while j < len(sv) and sv[j] == sv[i]: j += 1
        segs.append(j-i); i = j
    return {"n": len(segs), "trans": len(segs)-1,
            "med": float(np.median(segs)), "min": min(segs), "max": max(segs),
            "le5": sum(1 for x in segs if x <= 5),
            "le7": sum(1 for x in segs if x <= 7)}

v34b = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
v34b["time"] = pd.to_datetime(v34b["time"])

# Filter to same period
mask2 = v2["time"] >= "2007-01-01"
mask34 = v34b["time"] >= "2007-01-01"
st_v2  = v2.loc[mask2, "state"].values
st_v21 = v2.loc[mask2, "state_v21"].values
st_v34 = v34b.loc[mask34, "state"].values[:len(st_v2)]  # align length

print("\n=== Segment stability (2007-2026) ===")
print(f"  {'System':<22}  {'Trans':>6}  {'Med':>6}  {'Min':>5}  {'Stays<=5d':>10}  {'Stays<=7d':>10}")
print("  " + "-"*72)
for label, arr in [("v2 (LIVE)",st_v2),("v2.1 (proposed)",st_v21),("v3.4b (TQ34b)",st_v34)]:
    sg = seg_stats(arr)
    print(f"  {label:<22}  {sg['trans']:>6d}  {sg['med']:>5.0f}d  {sg['min']:>5d}  {sg['le5']:>10d}  {sg['le7']:>10d}")

# Current state
cur_v21  = int(v2["state_v21"].iloc[-1])
cur_v2   = int(v2["state"].iloc[-1])
cur_date = str(v2["time"].iloc[-1].date())
print(f"\n  Current state ({cur_date}): v2={STATE_NAMES[cur_v2]}  v2.1={STATE_NAMES[cur_v21]}")

# ─── 2. Integrated V4/V5 test ─────────────────────────────────────────────────
print("\n" + "="*80)
print("  STEP 2: Integrated V4/V5 test: TQ34b vs LIVE vs v2.1")
print("="*80)

from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}; ETF_KELLY = {3: 1.0}
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12; SWITCH_COST = 0.005

print("\n[1] Loading signals + prices...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_Q = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map  = {(r["ticker"],r["time"]): r["liq"] for _,r in sig_B.iterrows()}
vni_B = bq(VNI_Q.format(start=START_B, end=END_B)); vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates = sorted(vni_B["time"].unique())
vn30_und  = dict(zip(vni_B["time"], vni_B["Close"]))
opens_df  = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
print(f"  Opens: {len(opens_df):,} rows")

print("\n[2] Loading 3 state series: TQ34b / LIVE / v2.1...")
def make_state_ff(df_state, dates):
    sbd = dict(zip(df_state["time"], df_state["state"])); ff = {}; last = None
    for d in dates:
        s = sbd.get(d);
        if s is not None: last = s
        ff[d] = last
    return ff

# TQ34b
state_tq_df = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
state_tq_df["time"] = pd.to_datetime(state_tq_df["time"])
state_tq_df = state_tq_df[(state_tq_df["time"]>=START_B)&(state_tq_df["time"]<=END_B)]
state_ff_tq = make_state_ff(state_tq_df, vni_dates)

# LIVE (v2 from BQ)
state_live_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
state_live_df["time"] = pd.to_datetime(state_live_df["time"])
state_ff_live = make_state_ff(state_live_df, vni_dates)

# v2.1 (local)
v21_df = pd.read_csv("data/vnindex_5state_v21.csv"); v21_df["time"] = pd.to_datetime(v21_df["time"])
v21_df = v21_df[(v21_df["time"]>=START_B)&(v21_df["time"]<=END_B)]
state_ff_v21 = make_state_ff(v21_df, vni_dates)

# Agreement stats
agree_v21_tq = sum(state_ff_v21[d]==state_ff_tq[d] for d in vni_dates if state_ff_v21.get(d) and state_ff_tq.get(d))
agree_v21_lv = sum(state_ff_v21[d]==state_ff_live[d] for d in vni_dates if state_ff_v21.get(d) and state_ff_live.get(d))
n = len(vni_dates)
print(f"  v2.1 vs TQ34b agreement: {agree_v21_tq}/{n} = {agree_v21_tq/n*100:.1f}%")
print(f"  v2.1 vs LIVE  agreement: {agree_v21_lv}/{n} = {agree_v21_lv/n*100:.1f}%")

print("\n[3] D1 RE_BACKLOG reclassification...")
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])

def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS)
sig_B = sig_B[(~mb_buy) | sig_B.apply(sv_tight_keep, axis=1)].copy()
print(f"  After SV_TIGHT + D1: {len(sig_B):,} rows")

# Overheat filter per state
def make_sig_overheat(state_ff, sig_src):
    sv = vni_full.copy()
    sv["state"] = sv["time"].map(state_ff).ffill()
    sv["overheat"] = ((sv["Close"]/sv["MA200"]>1.30) & ((sv["state"]==5)|(sv["D_RSI"]>0.75)))
    oh = set(sv[sv["overheat"]]["time"])
    s = sig_src.copy()
    s.loc[s["time"].isin(oh) & s["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"
    return s

sig_tq  = make_sig_overheat(state_ff_tq,  sig_B)
sig_v21 = make_sig_overheat(state_ff_v21, sig_B)
print(f"  Overheat: TQ34b={len(sig_B)-len(sig_tq[sig_tq.play_type!='AVOID_overheated'])} | v2.1={len(sig_B)-len(sig_v21[sig_v21.play_type!='AVOID_overheated'])}")

print("\n[4] Universe + sector...")
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map,"exit_slippage_tiered":True}

def run_bal(sig, sff, etf, label):
    nav,_ = simulate(sig, prices_B, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=etf, vn30_underlying=vn30_und,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True, **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"    {label:<32} {s.iloc[-1]/1e9:.3f}B"); return s

def run_vn30(sig, sff, etf, label):
    sig30 = sig[sig["ticker"].isin(top30)].copy()
    p30 = {tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30 = {k:v for k,v in liq_map.items() if k[0] in top30}
    L30 = {**LIQ,"liquidity_lookup":l30}
    nav,_ = simulate(sig30, p30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV, ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS, deposit_annual=DEPOSIT, borrow_annual=BORROW,
        state_by_date=sff, cash_etf_states=etf, vn30_underlying=vn30_und,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True, **L30, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"    {label:<32} {s.iloc[-1]/1e9:.3f}B"); return s

print("\n[5] Running legs...")
bal_tq_b  = run_bal(sig_tq,  state_ff_tq,  {3:0.7}, "BAL_TQ_base")
bal_tq_k  = run_bal(sig_tq,  state_ff_tq,  {3:1.0}, "BAL_TQ_kelly")
vn_tq_b   = run_vn30(sig_tq, state_ff_tq,  {3:0.7}, "VN30_TQ_base")
vn_tq_k   = run_vn30(sig_tq, state_ff_tq,  {3:1.0}, "VN30_TQ_kelly")
bal_v21_b = run_bal(sig_v21, state_ff_v21, {3:0.7}, "BAL_v21_base")
bal_v21_k = run_bal(sig_v21, state_ff_v21, {3:1.0}, "BAL_v21_kelly")
vn_v21_b  = run_vn30(sig_v21,state_ff_v21, {3:0.7}, "VN30_v21_base")
vn_v21_k  = run_vn30(sig_v21,state_ff_v21, {3:1.0}, "VN30_v21_kelly")

print("\n[6] LAGGED v121...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
midx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = midx; all_dt = np.array(midx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time",columns="ticker",values="Open",aggfunc="first").sort_index().reindex(midx).ffill(limit=5)
liq_l = ov.pivot_table(index="time",columns="ticker",values="Volume_3M_P50",aggfunc="first").sort_index().reindex(midx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),1e9)).clip(-5,5)
ev = pd.read_csv("data/earnings_events_classified.csv",parse_dates=["Release_Date"])
ev = ev.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    good_history=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cd=row["Release_Date"]; ng=len(good_history)
        ev.at[ri,"prior_n_good"]=ng
        if ng>=1:
            da=pd.to_datetime([d for d,_ in good_history]); pa=np.array([p for _,p in good_history])
            ay=(cd-da).days.values/365.25; w=np.exp(-LN2*ay/HL)
            ev.at[ri,"pa_HL3"]=(pa*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]):
            good_history.append((cd,row["post_ret"]))
e_hl3 = ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
def off(rdt,k):
    r=np.datetime64(rdt); p=np.searchsorted(all_dt,r,side="right")-1
    if p<0: return None
    t=p+k; return pd.Timestamp(all_dt[t]) if 0<=t<len(all_dt) else None
sched=[{"ticker":r["ticker"],"entry_dt":off(r["Release_Date"],5),"exit_dt":off(r["Release_Date"],30),"surprise":r["surprise_B_MA"]}
       for _,r in e_hl3.iterrows() if r["ticker"] in px_open.columns and off(r["Release_Date"],5) and off(r["Release_Date"],30)]
sched_df=pd.DataFrame(sched).sort_values("entry_dt").reset_index(drop=True)
en_by=sched_df.groupby("entry_dt"); ex_by=sched_df.groupby("exit_dt")
def run_lag(init_nav,sw=pd.Timestamp(START_B),ew=pd.Timestamp(END_B)):
    sim_d=[d for d in midx if sw<=d<=ew]; cash=init_nav; pos={}; hist=[]
    for dt in sim_d:
        if dt in ex_by.groups:
            for _,ex in ex_by.get_group(dt).iterrows():
                tk=ex["ticker"]
                if tk not in pos or pos[tk]["exit_dt"]!=dt: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: fpx=px_close.at[dt,tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                cash+=pos[tk]["shares"]*fpx*0.9985*(1-0.001); del pos[tk]
        if dt in en_by.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm
            for _,en in en_by.get_group(dt).iterrows():
                tk=en["ticker"]
                if tk in pos or len(pos)>=12: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                adv=liq_l.at[dt,tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx<2e9: continue
                pp=0.10 if en["surprise"]>0.5 else 0.08
                alloc=min(pp*nav_now, 0.20*adv*5*fpx)
                if alloc<1e6 or alloc>cash: continue
                ep=fpx*1.001; sh=alloc/ep; cash-=sh*ep
                pos[tk]={"entry_dt":dt,"exit_dt":en["exit_dt"],"shares":sh,"entry_px":fpx}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        hist.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(hist).set_index("time")["nav"]
nav_lag = run_lag(BOOK_NAV); print(f"    LAG v121: {nav_lag.iloc[-1]/1e9:.3f}B")

print("\n[7] M1+M3r ensemble...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv",index_col=0,parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_q = """WITH base AS (SELECT t.time, t.ticker,
  SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS ret_6m,
  AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,ticker,ret_6m,adv_1y,ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL)
SELECT time,AVG(IF(rnk<=10,ret_6m,NULL)) AS top10_ret,AVG(ret_6m) AS all_ret FROM ranked GROUP BY time ORDER BY time"""
m3r_df=bq(m3r_q); m3r_df["time"]=pd.to_datetime(m3r_df["time"])
m3r_df["M3r"]=m3r_df["top10_ret"]-m3r_df["all_ret"]; m3r=m3r_df.set_index("time")["M3r"]
def mksig(metric,min_h=252):
    s=metric.dropna().sort_index(); em=s.expanding(min_periods=min_h).median()
    raw=(s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m3r=mksig(m3r)

print("\n[8] Building V4/V5 variants...")
common = (bal_tq_b.index.intersection(vn_tq_b.index).intersection(nav_lag.index)
          .intersection(bal_v21_b.index).intersection(vn_v21_b.index)
          .intersection(bal_tq_k.index).intersection(vn_tq_k.index)
          .intersection(bal_v21_k.index).intersection(vn_v21_k.index))
m1  = sig_m1.reindex(common).ffill().fillna(1).astype(int)
m3r_a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def AND_hold(a,b):
    out=np.zeros(len(a),dtype=int); cur=int(a.iloc[0])
    for i,(x,y) in enumerate(zip(a.values,b.values)):
        if x==y: cur=int(x)
        out[i]=cur
    return pd.Series(out,index=a.index)
sig_AH = AND_hold(m1,m3r_a)

def sw_nav(bal,vn30,lag,sig,sc=SWITCH_COST):
    br=bal.pct_change().fillna(0); vr=vn30.pct_change().fillna(0); lr=lag.pct_change().fillna(0)
    nb=(1+br).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,dtype=float); ps=int(sig.iloc[0])
    for i in range(1,len(common)):
        cs=int(sig.iloc[i])
        sec[i]=sec[i-1]*(1-sc) if cs!=ps else sec[i-1]
        sec[i]*=(1+(vr.iloc[i] if cs==1 else lr.iloc[i])); ps=cs
    return pd.Series((nb.values+sec)/TOTAL_NAV,index=common)

nav_V4_TQ  = sw_nav(bal_tq_b.loc[common],  vn_tq_b.loc[common],  nav_lag.loc[common], sig_AH)
nav_V5_TQ  = sw_nav(bal_tq_k.loc[common],  vn_tq_k.loc[common],  nav_lag.loc[common], sig_AH)
nav_V4_v21 = sw_nav(bal_v21_b.loc[common], vn_v21_b.loc[common], nav_lag.loc[common], sig_AH)
nav_V5_v21 = sw_nav(bal_v21_k.loc[common], vn_v21_k.loc[common], nav_lag.loc[common], sig_AH)
vni_n = vni_B.set_index("time")["Close"].reindex(common).ffill(); vni_n/=vni_n.iloc[0]

def metrics(nav,s,e):
    sv=nav[(nav.index>=s)&(nav.index<=e)].dropna()
    if len(sv)<30: return None
    r=sv.pct_change().dropna(); yrs=(sv.index[-1]-sv.index[0]).days/365.25
    spy=len(r)/yrs if yrs>0 else 252
    cagr=(sv.iloc[-1]/sv.iloc[0])**(1/yrs)-1
    sh=r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0
    dd=((sv-sv.cummax())/sv.cummax()).min(); cal=cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sh":sh,"DD":dd*100,"Cal":cal,"W":sv.iloc[-1]/sv.iloc[0]}

# ─── 9. Results ───────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("  RESULTS: TQ34b vs v2.1 trong V4/V5")
print("="*80)
for period,s,e in [
    ("FULL 2014-2026","2014-01-01","2099-01-01"),
    ("OOS  2020-2026","2020-01-01","2099-01-01"),
    ("OOS  2024-2026","2024-01-01","2099-01-01"),
]:
    print(f"\n--- {period} ---")
    print(f"  {'System':<30}  {'CAGR':>9}  {'Sharpe':>7}  {'MaxDD':>8}  {'Calmar':>7}  {'Wealth':>7}")
    print("  "+"-"*78)
    for label, nav in [
        ("V4  TQ34b (current)",  nav_V4_TQ),
        ("V4  v2.1  (proposed)", nav_V4_v21),
        ("V5  TQ34b (current)",  nav_V5_TQ),
        ("V5  v2.1  (proposed)", nav_V5_v21),
        ("VNI B&H",              vni_n),
    ]:
        m=metrics(nav,s,e)
        if m: print(f"  {label:<30}  {m['CAGR']:>+8.2f}%  {m['Sh']:>7.2f}  {m['DD']:>+7.1f}%  {m['Cal']:>7.2f}  {m['W']:>7.2f}x")

print("\n=== DELTA SUMMARY: v2.1 vs TQ34b ===")
for period,s,e in [("FULL","2014-01-01","2099-01-01"),("OOS2020","2020-01-01","2099-01-01"),("OOS2024","2024-01-01","2099-01-01")]:
    m4t=metrics(nav_V4_TQ,s,e); m4v=metrics(nav_V4_v21,s,e)
    m5t=metrics(nav_V5_TQ,s,e); m5v=metrics(nav_V5_v21,s,e)
    if not all([m4t,m4v,m5t,m5v]): continue
    d4c=m4v["CAGR"]-m4t["CAGR"]; d4d=m4v["DD"]-m4t["DD"]
    d5c=m5v["CAGR"]-m5t["CAGR"]; d5d=m5v["DD"]-m5t["DD"]
    s4=("+" if d4c>0.05 else ("-" if d4c<-0.05 else "~"))
    s5=("+" if d5c>0.05 else ("-" if d5c<-0.05 else "~"))
    print(f"  {period:<10} V4: {d4c:+.2f}pp CAGR  DD{d4d:+.1f}pp [{s4}]  |  V5: {d5c:+.2f}pp CAGR  DD{d5d:+.1f}pp [{s5}]")

print("\nDONE.")
