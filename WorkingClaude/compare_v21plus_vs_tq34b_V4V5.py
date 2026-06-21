# -*- coding: utf-8 -*-
"""
compare_v21plus_vs_tq34b_V4V5.py
=================================
Test: v2.1+ vs TQ34b trong V4/V5 integrated test.

v2.1+ = BQ LIVE + US override (bypassed khi BTC=True) + RSI gate + mode3+ms2
TQ34b = v3 staging + US override (bypassed khi BTC=True) + RSI gate + mode3+ms2

Chi khac nhau o upstream: BQ LIVE (v2g_pe3c_s3) vs v3 staging (rebuilt from scratch).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"
END_B   = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}
ETF_KELLY = {3: 1.0}
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B  = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"
STATE_CSV_V21P   = "data/vnindex_5state_v21_plus.csv"
SWITCH_COST = 0.005

print("="*90)
print(f"  V4/V5: TQ34b vs v2.1+  |  {START_B} -> {END_B}")
print("="*90)

# ---- 1. Load signals --------------------------------------------------------
print("\n[1] Loading signals + prices...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# ---- 2. Load state series ---------------------------------------------------
print("\n[2] Loading states: TQ34b + v2.1+...")
def load_state_ff(csv_path, vni_dates):
    df = pd.read_csv(csv_path); df["time"] = pd.to_datetime(df["time"])
    sbd = dict(zip(df["time"], df["state"])); state_ff = {}; last = None
    for d in vni_dates:
        s = sbd.get(d)
        if s is not None: last = s
        state_ff[d] = last
    return state_ff, df

state_ff_tq,  df_tq  = load_state_ff(STATE_CSV_TQ34B, vni_dates_B)
state_ff_v21p, df_v21p = load_state_ff(STATE_CSV_V21P,  vni_dates_B)

# Agreement
agree = sum(state_ff_tq[d] == state_ff_v21p[d] for d in vni_dates_B)
diff_dates = [d for d in vni_dates_B if state_ff_tq.get(d) != state_ff_v21p.get(d)]
print(f"  Agreement TQ34b vs v2.1+: {agree}/{len(vni_dates_B)} = {agree/len(vni_dates_B)*100:.1f}%")
print(f"  Diff days: {len(diff_dates)} | v2.1+ more bullish: {sum(state_ff_v21p[d]>state_ff_tq[d] for d in diff_dates)} | TQ34b more bullish: {sum(state_ff_tq[d]>state_ff_v21p[d] for d in diff_dates)}")

# ---- 3. D1 RE_BACKLOG -------------------------------------------------------
print("\n[3] D1 RE_BACKLOG_BUY...")
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
print(f"  RE_BACKLOG_BUY: {int(omask.sum()):,}")

# ---- 4. SV_TIGHT ------------------------------------------------------------
def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS_V11)
keep_mask = (~mb_buy) | sig_B.apply(sv_tight_keep, axis=1)
sig_B = sig_B[keep_mask].copy()
print(f"  After SV_TIGHT: {len(sig_B):,} rows")

# ---- 5. Overheat filter (2 versions) ----------------------------------------
def make_overheat_sig(state_df, vni_full):
    v = vni_full.merge(state_df[["time","state"]], on="time", how="left")
    v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    return set(v[v["overheat"]]["time"])

oh_tq   = make_overheat_sig(df_tq,   vni_full)
oh_v21p = make_overheat_sig(df_v21p, vni_full)

sig_v_tq = sig_B.copy()
sig_v_tq.loc[sig_v_tq["time"].isin(oh_tq) & sig_v_tq["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
sig_v_v21p = sig_B.copy()
sig_v_v21p.loc[sig_v_v21p["time"].isin(oh_v21p) & sig_v_v21p["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
print(f"\n[5] Overheat -- TQ34b: {len(oh_tq)} | v2.1+: {len(oh_v21p)} | diff: {len(oh_tq)-len(oh_v21p):+d}")

# ---- 6. Universe + sector ---------------------------------------------------
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ---- 7. Simulation runners --------------------------------------------------
def run_bal(sig_use, state_ff, etf_states, label):
    nav, _ = simulate(sig_use, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True, **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"  {label:<28} final: {s.iloc[-1]/1e9:.3f}B"); return s

def run_vn30(sig_use, state_ff, etf_states, label):
    sig30 = sig_use[sig_use["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map, tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **{"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq30,"exit_slippage_tiered":True},
        name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"  {label:<28} final: {s.iloc[-1]/1e9:.3f}B"); return s

# ---- 8. Run all legs --------------------------------------------------------
print("\n[8] Running all legs...")
bal_tq_base   = run_bal(sig_v_tq,   state_ff_tq,   ETF_BASE,  "BAL_TQ_base")
bal_tq_kelly  = run_bal(sig_v_tq,   state_ff_tq,   ETF_KELLY, "BAL_TQ_kelly")
vn30_tq_base  = run_vn30(sig_v_tq,  state_ff_tq,   ETF_BASE,  "VN30_TQ_base")
vn30_tq_kelly = run_vn30(sig_v_tq,  state_ff_tq,   ETF_KELLY, "VN30_TQ_kelly")
bal_v21p_base   = run_bal(sig_v_v21p,   state_ff_v21p, ETF_BASE,  "BAL_V21P_base")
bal_v21p_kelly  = run_bal(sig_v_v21p,   state_ff_v21p, ETF_KELLY, "BAL_V21P_kelly")
vn30_v21p_base  = run_vn30(sig_v_v21p,  state_ff_v21p, ETF_BASE,  "VN30_V21P_base")
vn30_v21p_kelly = run_vn30(sig_v_v21p,  state_ff_v21p, ETF_KELLY, "VN30_V21P_kelly")

# ---- 9. LAGGED -------------------------------------------------------------
print("\n[9] LAGGED v12.1...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]], on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]; cur_date = row["Release_Date"]; n_good = len(good_history)
        ev.at[row_idx,"prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date-dates_arr).days.values/365.25
            w = np.exp(-LN2*age_yrs/HL)
            ev.at[row_idx,"pa_HL3"] = (posts_arr*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date,row["post_ret"]))
e_hl3 = ev[(ev["NP_R"]>=15) & (ev["prior_n_good"]>=4) & (ev["pa_HL3"]>=5)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right")-1
    if pos<0: return None
    tgt = pos+offset
    if tgt>=len(all_dates) or tgt<0: return None
    return pd.Timestamp(all_dates[tgt])
ENTRY_OFFSET, HOLD_DAYS, LAG_MAX_POS, LIQ_MIN = 5, 25, 12, 2e9
schedule=[]
for _, row in e_hl3.iterrows():
    tk=row["ticker"]; rdt=row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt=offset_date(rdt,ENTRY_OFFSET); exit_dt=offset_date(rdt,ENTRY_OFFSET+HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged(init_nav, use_s2, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days=[d for d in master_idx if sw<=d<=ew]
    cash=init_nav; positions={}; nav_history=[]
    SLIP_IN,SLIP_OUT,TAX = 0.001,0.0015,0.001; LIQ_CAP,MAX_FILL = 0.20,5
    for dt in sim_days:
        if dt in exits_by_day.groups:
            for _,ex_row in exits_by_day.get_group(dt).iterrows():
                tk=ex_row["ticker"]
                if tk not in positions: continue
                pos=positions[tk]
                if pos["exit_dt"]!=dt: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0:
                    fpx=px_close.at[dt,tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx<=0: continue
                gross=pos["shares"]*fpx*(1-SLIP_OUT); cash+=gross*(1-TAX); del positions[tk]
        if dt in entries_by_day.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm
            for _,en_row in entries_by_day.get_group(dt).iterrows():
                tk=en_row["ticker"]
                if tk in positions or len(positions)>=LAG_MAX_POS: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                adv=liq_l.at[dt,tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx<LIQ_MIN: continue
                pos_pct=(0.10 if en_row["surprise"]>0.5 else 0.08) if use_s2 else 0.08
                target=pos_pct*nav_now; cap=LIQ_CAP*adv*MAX_FILL*fpx
                alloc=min(target,cap)
                if alloc<1e6 or alloc>cash: continue
                eff_px=fpx*(1+SLIP_IN); shares=alloc/eff_px; cost=shares*eff_px
                cash-=cost
                positions[tk]={"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nav_history.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

nav_lag_v121 = run_lagged(BOOK_NAV, use_s2=True)
print(f"  LAG v121: {nav_lag_v121.iloc[-1]/1e9:.3f}B")

# ---- 10. M1+M3r -------------------------------------------------------------
print("\n[10] M1+M3r ensemble...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
),
ranked AS (
  SELECT time, ticker, ret_6m, adv_1y,
    ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL
)
SELECT time, AVG(IF(rnk<=10, ret_6m, NULL)) AS top10_ret, AVG(ret_6m) AS all_ret
FROM ranked GROUP BY time ORDER BY time"""
m3r_df = bq(m3r_q); m3r_df["time"] = pd.to_datetime(m3r_df["time"])
m3r_df["M3r"] = m3r_df["top10_ret"] - m3r_df["all_ret"]
m3r = m3r_df.set_index("time")["M3r"]
def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index()
    em = s.expanding(min_periods=min_history).median()
    raw = (s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m3r = make_signal(m3r)

# ---- 11. Build systems ------------------------------------------------------
print("\n[11] Building system variants...")
common = (bal_tq_base.index.intersection(vn30_tq_base.index)
          .intersection(nav_lag_v121.index)
          .intersection(bal_v21p_base.index).intersection(vn30_v21p_base.index)
          .intersection(bal_tq_kelly.index).intersection(vn30_tq_kelly.index)
          .intersection(bal_v21p_kelly.index).intersection(vn30_v21p_kelly.index))
m1    = sig_m1.reindex(common).ffill().fillna(1).astype(int)
m3r_a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ensemble_AND_hold(m1, m3):
    out=np.zeros(len(m1),dtype=int); cur=int(m1.iloc[0])
    for i,(a,b) in enumerate(zip(m1.values,m3.values)):
        if a==b: cur=int(a)
        out[i]=cur
    return pd.Series(out,index=m1.index)
sig_AH = ensemble_AND_hold(m1, m3r_a)
vni_n = vni_B.set_index("time")["Close"].reindex(common).ffill(); vni_n = vni_n/vni_n.iloc[0]

def switched_nav(bal_s, vn30_s, lag_s, signal, switch_cost=SWITCH_COST):
    bal_ret=bal_s.pct_change().fillna(0); vn30_ret=vn30_s.pct_change().fillna(0)
    lag_ret=lag_s.pct_change().fillna(0); nav_bal=(1+bal_ret).cumprod()*BOOK_NAV
    second=np.full(len(common),BOOK_NAV,dtype=float); prev_sig=int(signal.iloc[0])
    for i in range(1,len(common)):
        cur_sig=int(signal.iloc[i])
        if cur_sig!=prev_sig: second[i]=second[i-1]*(1-switch_cost)
        else: second[i]=second[i-1]
        r=vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
        second[i]=second[i]*(1+r); prev_sig=cur_sig
    return pd.Series((nav_bal.values+second)/TOTAL_NAV,index=common)

nav_V4_TQ   = switched_nav(bal_tq_base.loc[common],   vn30_tq_base.loc[common],   nav_lag_v121.loc[common], sig_AH)
nav_V5_TQ   = switched_nav(bal_tq_kelly.loc[common],  vn30_tq_kelly.loc[common],  nav_lag_v121.loc[common], sig_AH)
nav_V4_V21P = switched_nav(bal_v21p_base.loc[common],  vn30_v21p_base.loc[common],  nav_lag_v121.loc[common], sig_AH)
nav_V5_V21P = switched_nav(bal_v21p_kelly.loc[common], vn30_v21p_kelly.loc[common], nav_lag_v121.loc[common], sig_AH)

# ---- 12. Results ------------------------------------------------------------
def metrics(nav, start, end):
    s=nav[(nav.index>=start)&(nav.index<=end)].dropna()
    if len(s)<30: return None
    rets=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    spy=len(rets)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    sh=rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd=((s-s.cummax())/s.cummax()).min()
    cal=cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sh":sh,"DD":dd*100,"Cal":cal,"W":s.iloc[-1]/s.iloc[0]}

print("\n"+"="*90)
print("  RESULTS: TQ34b vs v2.1+")
print("="*90)
for period,s,e in [("FULL 2014-2026","2014-01-01","2099-01-01"),
                   ("OOS  2020-2026","2020-01-01","2099-01-01"),
                   ("OOS  2024-2026","2024-01-01","2099-01-01")]:
    print(f"\n--- {period} ---")
    print(f"  {'System':<38}  {'CAGR':>9}  {'Sharpe':>7}  {'MaxDD':>8}  {'Calmar':>7}  {'Wealth':>7}")
    print("  "+"-"*82)
    for label,nav in [
        ("V4  TQ34b [canonical]",  nav_V4_TQ),
        ("V4  v2.1+ [new]",        nav_V4_V21P),
        ("V5  TQ34b [canonical]",  nav_V5_TQ),
        ("V5  v2.1+ [new]",        nav_V5_V21P),
        ("VNI B&H",                vni_n),
    ]:
        m=metrics(nav,s,e)
        if m:
            print(f"  {label:<40}  {m['CAGR']:>+8.2f}%  {m['Sh']:>7.2f}  {m['DD']:>+7.1f}%  {m['Cal']:>7.2f}  {m['W']:>7.2f}x")

# Annual breakdown
print("\n"+"="*90)
print("  ANNUAL BREAKDOWN: V4 TQ34b vs V4 v2.1+  |  V5 TQ34b vs V5 v2.1+")
print("="*90)
print(f"  {'Year':<6}  {'V4-TQ':>8}  {'V4-V21+':>8}  {'dV4':>7}  |  {'V5-TQ':>8}  {'V5-V21+':>8}  {'dV5':>7}  |  {'VNI':>8}")
print("  "+"-"*78)
vni_yr = vni_B.set_index("time")["Close"]
for yr in range(2014,2027):
    s=f"{yr}-01-01"; e=f"{yr}-12-31"
    def yr_cagr(nav):
        x=nav[(nav.index>=s)&(nav.index<=e)].dropna()
        if len(x)<5: return None
        yrs2=(x.index[-1]-x.index[0]).days/365.25
        if yrs2<=0: return None
        return ((x.iloc[-1]/x.iloc[0])**(1/yrs2)-1)*100
    v4t=yr_cagr(nav_V4_TQ); v4v=yr_cagr(nav_V4_V21P)
    v5t=yr_cagr(nav_V5_TQ); v5v=yr_cagr(nav_V5_V21P)
    vni_c=yr_cagr(vni_yr.reindex(nav_V4_TQ.index).ffill())
    if v4t is None: continue
    dv4=v4v-v4t if v4v else 0; dv5=v5v-v5t if v5v else 0
    print(f"  {yr:<6}  {v4t:>+7.1f}%  {v4v:>+7.1f}%  {dv4:>+6.1f}pp  |  {v5t:>+7.1f}%  {v5v:>+7.1f}%  {dv5:>+6.1f}pp  |  {vni_c:>+7.1f}%")

# Delta summary
print("\n"+"="*90)
print("  DELTA SUMMARY: v2.1+ vs TQ34b")
print("="*90)
for period,s,e in [("FULL","2014-01-01","2099-01-01"),
                   ("OOS2020","2020-01-01","2099-01-01"),
                   ("OOS2024","2024-01-01","2099-01-01")]:
    m4t=metrics(nav_V4_TQ,s,e); m4v=metrics(nav_V4_V21P,s,e)
    m5t=metrics(nav_V5_TQ,s,e); m5v=metrics(nav_V5_V21P,s,e)
    if not (m4t and m4v and m5t and m5v): continue
    d4c=m4v["CAGR"]-m4t["CAGR"]; d4d=m4v["DD"]-m4t["DD"]; d4s=m4v["Sh"]-m4t["Sh"]
    d5c=m5v["CAGR"]-m5t["CAGR"]; d5d=m5v["DD"]-m5t["DD"]; d5s=m5v["Sh"]-m5t["Sh"]
    sign4 = "WIN" if d4c>0.10 else ("LOSS" if d4c<-0.10 else "~TIE")
    sign5 = "WIN" if d5c>0.10 else ("LOSS" if d5c<-0.10 else "~TIE")
    print(f"  {period:<10} V4 v2.1+ vs TQ34b: CAGR {d4c:>+.2f}pp  Sh {d4s:>+.2f}  DD {d4d:>+.1f}pp  [{sign4}]")
    print(f"  {'':<10} V5 v2.1+ vs TQ34b: CAGR {d5c:>+.2f}pp  Sh {d5s:>+.2f}  DD {d5d:>+.1f}pp  [{sign5}]")

print("\nDONE.")
