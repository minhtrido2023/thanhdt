#!/usr/bin/env python3
"""run_prodspec_rating_C_sweep.py — sensitivity sweep of overlay (C) regime-conditional sizing.

(C) = weak-rating names (rating >= WEAK_RATING_MIN) keep full 10% in NEUTRAL/BULL/EX-BULL but are
shrunk to `weak_size` in stress states. This sweeps:
  - weak_size ∈ {0.0, 0.03, 0.05, 0.07}   (0.0 = full exclusion-in-stress; 0.10 = no-op)
  - stress_states ∈ {(1,2)=BEAR+CRISIS, (1,)=CRISIS-only}

Loads signals/prices/states/lagged/ensemble ONCE, then runs base + each config (5 BAL/VN30 legs each).
Lagged + ensemble legs are rating-independent (computed once).

Env:
  RATING_PKL   default data/rating_8l_history.pkl   (use _roe variant for the bank/power test)
  CONFIGS      optional "0.0:12,0.03:12,0.05:12,0.07:12,0.05:1"  (size:states comma-list; states digits)
  START_DATE / END_DATE
Output: data/rating_8l_C_sweep<tag>.csv
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq
import simulate_holistic_nav as _SHN
# (b) DEMOTE_PRIORITY: how hard rating>=4 (_W) names are pushed down the buy queue.
#   extreme  = absent from TIER_PRIORITY -> priority 0 (current default; below all buy tiers)
#   mild     = parent_priority - 0.5      (rating only breaks ties WITHIN the same tier)
#   moderate = parent_priority - 20       (rating>=4 ranks ~one tier lower, still buyable)
DEMOTE_PRIORITY = os.environ.get("DEMOTE_PRIORITY", "extreme")

START_B = os.environ.get("START_DATE", "2014-01-01")
END_B   = os.environ.get("END_DATE",   "2026-05-15")
RATING_PKL = os.environ.get("RATING_PKL", "data/rating_8l_history.pkl")
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}; ETF_KELLY = {3: 1.0}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12; FULL_SIZE = 0.10; WEAK_RATING_MIN = 4
if DEMOTE_PRIORITY != "extreme":
    for _t in TIER_BAL:
        _p = _SHN.TIER_PRIORITY.get(_t, 50)
        _SHN.TIER_PRIORITY[_t+"_W"] = (_p - 0.5) if DEMOTE_PRIORITY=="mild" else max(1.0, _p - 20)
    print(f"[DEMOTE_PRIORITY={DEMOTE_PRIORITY}] patched _W tier priorities")
STATE_CSV_TQ34B = os.environ.get("STATE_CSV_OVERRIDE", "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
SWITCH_COST = 0.005; FA_TABLE = "tav2_bq.fa_ratings"

# config list: (weak_size, stress_states_tuple)
if os.environ.get("CONFIGS"):
    CONFIGS = []
    for tok in os.environ["CONFIGS"].split(","):
        sz, st = tok.split(":"); CONFIGS.append((float(sz), tuple(int(c) for c in st.strip())))
else:
    CONFIGS = [(0.0,(1,2)),(0.03,(1,2)),(0.05,(1,2)),(0.07,(1,2)),(0.05,(1,))]
TAG = os.environ.get("TAG_SUFFIX", "_" + os.path.basename(RATING_PKL).replace("rating_8l_history","").replace(".pkl","") or "_neutral")
if TAG == "_": TAG = "_neutral"
print("="*100); print(f"  (C) SENSITIVITY SWEEP  {START_B}->{END_B}  RATING_PKL={RATING_PKL}  TAG={TAG}"); print("="*100)
print(f"  configs: {CONFIGS}")

# ─── load everything (mirrors run_prodspec_rating_BC.py) ────────────────────
print("\n[1] signals/prices/VNI...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B)); vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique()); vn30_proxy = dict(zip(vni_B["time"], vni_B["Close"]))
try:
    _etf = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30'
    AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
except Exception: _etf = pd.DataFrame(columns=["time","Close"])
_etf["time"] = pd.to_datetime(_etf["time"]); _etf_real = dict(zip(_etf["time"], _etf["Close"]))
if len(_etf):
    _splice = _etf["time"].min(); _scale = (_etf_real[_splice]/vn30_proxy[_splice]) if vn30_proxy.get(_splice) else 1.0
    vn30_underlying = {}
    for d in vni_dates_B:
        if d in _etf_real: vn30_underlying[d]=_etf_real[d]
        elif d < _splice and d in vn30_proxy: vn30_underlying[d]=vn30_proxy[d]*_scale
        elif d in vn30_proxy: vn30_underlying[d]=vn30_proxy[d]
else: vn30_underlying = vn30_proxy
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

print("[2] states...")
state_df_tq = pd.read_csv(STATE_CSV_TQ34B); state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B)&(state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"])); state_ff_tq={}; last=None
for d in vni_dates_B:
    s=sbd_tq.get(d);
    if s is not None: last=s
    state_ff_tq[d]=last
state_df_live = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
state_df_live["time"] = pd.to_datetime(state_df_live["time"])
sbd_live = dict(zip(state_df_live["time"], state_df_live["state"])); state_ff_live={}; last=None
for d in vni_dates_B:
    s=sbd_live.get(d)
    if s is not None: last=s
    state_ff_live[d]=last

print("[3] D1 RE_BACKLOG...")
d1 = bq(f"""
WITH adv_dated AS (SELECT f.ticker, f.time AS f_time, SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM {FA_TABLE} AS f),
fin_dated AS (SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker, t.time, fa.fa_tier, SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"]) & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
sig_B.loc[sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120), "play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])

def sv_tight_keep(row):
    s=row.get("state5"); days=row.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS_V11)
sig_B = sig_B[(~mb_buy) | sig_B.apply(sv_tight_keep, axis=1)].copy()

print(f"[4b] rating from {RATING_PKL}...")
rh = pd.read_pickle(RATING_PKL); rh["eff_time"] = pd.to_datetime(rh["eff_time"])
rh = rh.sort_values("eff_time")[["ticker","eff_time","rating"]]
sig_B = sig_B.sort_values("time")
sig_B = pd.merge_asof(sig_B, rh.rename(columns={"eff_time":"time","rating":"rating8l"}), on="time", by="ticker", direction="backward")
print("  buy-signal rating dist:")
print(sig_B.loc[sig_B["play_type"].isin(BUY_TIERS_V11),"rating8l"].value_counts(dropna=False).sort_index().to_string())

def add_overheat(state_df):
    v = vni_full.merge(state_df, on="time", how="left"); v["state"]=v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    return set(v[v["overheat"]]["time"])
oh_tq = add_overheat(state_df_tq); oh_live = add_overheat(state_df_live)
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

def apply_overheat(sig, oh):
    s = sig.copy()
    s.loc[s["time"].isin(oh) & s["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return s

def build_cfg(weak_size, stress_states):
    """None weak_size => base (no overlay)."""
    base_tiers = list(TIER_BAL)
    s_tq = apply_overheat(sig_B, oh_tq); s_live = apply_overheat(sig_B, oh_live)
    if weak_size is None:
        return dict(sig_tq=s_tq, sig_live=s_live, allowed_tiers=base_tiers,
                    tier_weights={t:FULL_SIZE for t in base_tiers}, tier_weights_by_state=None,
                    sector_cap_exempt={"RE_BACKLOG_BUY"})
    weak_tiers = [t+"_W" for t in base_tiers]; all_tiers = base_tiers + weak_tiers
    for s in (s_tq, s_live):
        m = (s["rating8l"]>=WEAK_RATING_MIN) & s["play_type"].isin(set(base_tiers))
        s.loc[m, "play_type"] = s.loc[m, "play_type"] + "_W"
    twbs = {st: {**{t:FULL_SIZE for t in base_tiers}, **{t:weak_size for t in weak_tiers}} for st in stress_states}
    return dict(sig_tq=s_tq, sig_live=s_live, allowed_tiers=all_tiers,
                tier_weights={t:FULL_SIZE for t in all_tiers}, tier_weights_by_state=twbs,
                sector_cap_exempt={"RE_BACKLOG_BUY","RE_BACKLOG_BUY_W"})

# RANDOM-DEMOTION CONTROL: demote a RANDOM matched-count set of buy rows to priority-0 _W tiers
# (instead of rating>=4). If random ≈ rating-demote -> the edge is reshuffle luck, not rating quality.
_BUY_FRAC = float((sig_B["play_type"].isin(BUY_TIERS_V11) & (sig_B["rating8l"]>=WEAK_RATING_MIN)).sum()) \
            / max(1, int(sig_B["play_type"].isin(BUY_TIERS_V11).sum()))
def build_cfg_random(seed):
    base_tiers = list(TIER_BAL); weak_tiers=[t+"_W" for t in base_tiers]; all_tiers=base_tiers+weak_tiers
    s_tq = apply_overheat(sig_B, oh_tq); s_live = apply_overheat(sig_B, oh_live)
    for off,s in enumerate((s_tq, s_live)):
        rng = np.random.default_rng(seed*1000+off)
        elig = s["play_type"].isin(set(base_tiers)).values
        draw = rng.random(len(s)) < _BUY_FRAC
        m = elig & draw
        s.loc[m, "play_type"] = s.loc[m, "play_type"].astype(str) + "_W"
    return dict(sig_tq=s_tq, sig_live=s_live, allowed_tiers=all_tiers,
                tier_weights={t:FULL_SIZE for t in all_tiers}, tier_weights_by_state=None,
                sector_cap_exempt={"RE_BACKLOG_BUY","RE_BACKLOG_BUY_W"})

def run_bal(sig_use, state_ff, etf_states, cfg, label):
    nav,_ = simulate(sig_use, prices_B, vni_dates_B, allowed_tiers=cfg["allowed_tiers"], max_positions=MAX_POS,
        hold_days=45, stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, sector_cap_exempt_tiers=cfg["sector_cap_exempt"],
        tier_weights=cfg["tier_weights"], tier_weights_by_state=cfg["tier_weights_by_state"],
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff, cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying, etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True, **LIQ, name=label)
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]
def run_vn30(sig_use, state_ff, etf_states, cfg, label):
    sig30 = sig_use[sig_use["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}; LIQ30={**LIQ,"liquidity_lookup":liq30}
    nav,_ = simulate(sig30, prices30, vni_dates_B, allowed_tiers=cfg["allowed_tiers"], max_positions=MAX_POS,
        hold_days=45, stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=BOOK_NAV, ticker_sector_map=sec_map,
        tier_weights=cfg["tier_weights"], tier_weights_by_state=cfg["tier_weights_by_state"],
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff, cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying, etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True, **LIQ30, name=label)
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]

# ─── LAGGED + ensemble (rating-independent, once) ───────────────────────────
print("\n[9] LAGGED + ensemble (once)...")
with open("data/earnings_px.pkl","rb") as f: px_data=pickle.load(f); px_data["time"]=pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index=master_idx; all_dates=np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov=pickle.load(f); ov["time"]=pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time",columns="ticker",values="Open",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
_liqr = bq(f"""SELECT t.time, t.ticker, t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq_real
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Volume_3M_P50 IS NOT NULL""")
_liqr["time"]=pd.to_datetime(_liqr["time"])
liq_real_l = _liqr.pivot_table(index="time",columns="ticker",values="liq_real",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv("data/earnings_events_classified.csv",parse_dates=["Release_Date"])
ev=ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
ev=ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"]=ev["surprise_B_MA"].fillna(0)
LN2=np.log(2); HL=3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    gh=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cur=row["Release_Date"]; ev.at[ri,"prior_n_good"]=len(gh)
        if len(gh)>=1:
            da=pd.to_datetime([d for d,_ in gh]); pa=np.array([p for _,p in gh])
            w=np.exp(-LN2*(cur-da).days.values/365.25/HL); ev.at[ri,"pa_HL3"]=(pa*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): gh.append((cur,row["post_ret"]))
e_hl3=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
def offset_date(ref_dt, off):
    ref=np.datetime64(ref_dt); pos=np.searchsorted(all_dates,ref,side="right")-1
    if pos<0: return None
    tgt=pos+off
    return pd.Timestamp(all_dates[tgt]) if 0<=tgt<len(all_dates) else None
ENTRY_OFFSET,HOLD_DAYS,LAG_MAX_POS,LIQ_MIN=5,25,12,2e9; schedule=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; rdt=row["Release_Date"]
    if tk not in px_open.columns: continue
    e_=offset_date(rdt,ENTRY_OFFSET); x_=offset_date(rdt,ENTRY_OFFSET+HOLD_DAYS)
    if e_ is None or x_ is None: continue
    schedule.append({"ticker":tk,"entry_dt":e_,"exit_dt":x_,"surprise":row["surprise_B_MA"]})
sched_lag=pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day=sched_lag.groupby("entry_dt"); exits_by_day=sched_lag.groupby("exit_dt")
def run_lagged(init_nav, use_s2):
    sim_days=[d for d in master_idx if pd.Timestamp(START_B)<=d<=pd.Timestamp(END_B)]
    cash=init_nav; positions={}; nh=[]; SLIP_IN,SLIP_OUT,TAX=0.001,0.0015,0.001; LIQ_CAP,MAX_FILL=0.20,5
    for dt in sim_days:
        if dt in exits_by_day.groups:
            for _,ex in exits_by_day.get_group(dt).iterrows():
                tk=ex["ticker"]
                if tk not in positions: continue
                pos=positions[tk]
                if pos["exit_dt"]!=dt: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0:
                    fpx=px_close.at[dt,tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx<=0: continue
                cash+=pos["shares"]*fpx*(1-SLIP_OUT)*(1-TAX); del positions[tk]
        if dt in entries_by_day.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm
            for _,en in entries_by_day.get_group(dt).iterrows():
                tk=en["ticker"]
                if tk in positions or len(positions)>=LAG_MAX_POS: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                lr=liq_real_l.at[dt,tk] if tk in liq_real_l.columns else 0
                if pd.isna(lr) or lr<LIQ_MIN: continue
                pp=(0.10 if en["surprise"]>0.5 else 0.08) if use_s2 else 0.08
                alloc=min(pp*nav_now, LIQ_CAP*lr*MAX_FILL)
                if alloc<1e6 or alloc>cash: continue
                ep=fpx*(1+SLIP_IN); sh=alloc/ep; cash-=sh*ep
                positions[tk]={"entry_dt":dt,"exit_dt":en["exit_dt"],"shares":sh,"entry_px":fpx}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nh.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nh).set_index("time")["nav"]
nav_lag_v12=run_lagged(BOOK_NAV,False); nav_lag_v121=run_lagged(BOOK_NAV,True)
cached=pd.read_csv("data/compare_v11_v12_concentration_switch.csv",index_col=0,parse_dates=True)
sig_m1=cached["sig_m1"].dropna().astype(int)
m3r_q="""WITH base AS (SELECT t.time, t.ticker,
  SAFE_DIVIDE(t.Close, LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS ret_6m,
  AVG(t.Volume_3M_P50*COALESCE(t.Price,t.Close)) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,ticker,ret_6m,adv_1y,ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL)
SELECT time, AVG(IF(rnk<=10,ret_6m,NULL)) AS top10_ret, AVG(ret_6m) AS all_ret FROM ranked GROUP BY time ORDER BY time"""
m3r_df=bq(m3r_q); m3r_df["time"]=pd.to_datetime(m3r_df["time"]); m3r_df["M3r"]=m3r_df["top10_ret"]-m3r_df["all_ret"]
m3r=m3r_df.set_index("time")["M3r"]
def make_signal(metric,mh=252):
    s=metric.dropna().sort_index(); em=s.expanding(min_periods=mh).median()
    return (s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int).shift(1).fillna(1).astype(int)
sig_m3r=make_signal(m3r)

def metrics(nav):
    s=nav.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    spy=len(r)/yrs if yrs>0 else 252; cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh=r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0; dd=((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100}

def run_one(cfg):
    bal_tq_base=run_bal(cfg["sig_tq"],state_ff_tq,ETF_BASE,cfg,"bt"); bal_live_base=run_bal(cfg["sig_live"],state_ff_live,ETF_BASE,cfg,"bl")
    bal_tq_kelly=run_bal(cfg["sig_tq"],state_ff_tq,ETF_KELLY,cfg,"bk"); vn30_tq_base=run_vn30(cfg["sig_tq"],state_ff_tq,ETF_BASE,cfg,"vb")
    vn30_tq_kelly=run_vn30(cfg["sig_tq"],state_ff_tq,ETF_KELLY,cfg,"vk")
    common=bal_tq_base.index.intersection(vn30_tq_base.index).intersection(nav_lag_v12.index).intersection(nav_lag_v121.index).intersection(bal_live_base.index).intersection(bal_tq_kelly.index).intersection(vn30_tq_kelly.index)
    m1=sig_m1.reindex(common).ffill().fillna(1).astype(int); m3r_a=sig_m3r.reindex(common).ffill().fillna(1).astype(int)
    def ens(m1,m3):
        out=np.zeros(len(m1),dtype=int); cur=int(m1.iloc[0])
        for i,(a,b) in enumerate(zip(m1.values,m3.values)):
            if a==b: cur=int(a)
            out[i]=cur
        return pd.Series(out,index=m1.index)
    sig_AH=ens(m1,m3r_a)
    V1=(bal_tq_base.loc[common]+vn30_tq_base.loc[common])/TOTAL_NAV
    V2=(bal_tq_base.loc[common]+nav_lag_v12.loc[common])/TOTAL_NAV
    def sw(bal_s,vn30_s,lag_s,signal):
        br=bal_s.pct_change().fillna(0); vr=vn30_s.pct_change().fillna(0); lr=lag_s.pct_change().fillna(0)
        nb=(1+br).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,dtype=float); ps=int(signal.iloc[0])
        for i in range(1,len(common)):
            cs=int(signal.iloc[i]); sec[i]=sec[i-1]*(1-SWITCH_COST) if cs!=ps else sec[i-1]
            sec[i]*= (1+(vr.iloc[i] if cs==1 else lr.iloc[i])); ps=cs
        return pd.Series((nb.values+sec)/TOTAL_NAV,index=common)
    V4=sw(bal_tq_base.loc[common],vn30_tq_base.loc[common],nav_lag_v121.loc[common],sig_AH)
    V5=sw(bal_tq_kelly.loc[common],vn30_tq_kelly.loc[common],nav_lag_v121.loc[common],sig_AH)
    return {"V1":metrics(V1),"V2":metrics(V2),"V4":metrics(V4),"V5":metrics(V5)}

# ─── run base + configs ─────────────────────────────────────────────────────
print("\n[RUN] base..."); res={"base":run_one(build_cfg(None,None))}
if os.environ.get("RANDOM_DEMOTE"):
    seeds = [int(x) for x in os.environ.get("RANDOM_SEEDS","1,2,3").split(",")]
    print(f"[RANDOM-DEMOTION CONTROL] buy-frac demoted = {_BUY_FRAC:.3f}, seeds={seeds}")
    print("[RUN] rating_demote (split=priority0)..."); res["rating_demote"]=run_one(build_cfg(0.10,(1,2)))
    for sd in seeds:
        k=f"random_s{sd}"; print(f"[RUN] {k}..."); res[k]=run_one(build_cfg_random(sd))
else:
    for sz,st in CONFIGS:
        key=f"sz{sz}_st{''.join(map(str,st))}"; print(f"[RUN] {key}..."); res[key]=run_one(build_cfg(sz,st))

print(f"\n{'='*100}\n  (C) SWEEP RESULT  TAG={TAG}  ({START_B}->{END_B})  — CAGR / Sharpe / MaxDD  (ΔCAGR vs base)\n{'='*100}")
rows=[]
for sysn in ["V1","V2","V4","V5"]:
    b=res["base"][sysn]
    print(f"\n  {sysn}  base = {b['CAGR']:.2f}% / Sh{b['Sharpe']:.2f} / DD{b['DD']:.1f}")
    for key in res:
        if key=="base": continue
        r=res[key][sysn]
        print(f"     {key:14} {r['CAGR']:6.2f}% / Sh{r['Sharpe']:.2f} / DD{r['DD']:5.1f}  ({r['CAGR']-b['CAGR']:+.2f}pp)")
for key in res:
    for sysn in ["V1","V2","V4","V5"]:
        rows.append({"variant":key,"system":sysn,**res[key][sysn]})
pd.DataFrame(rows).to_csv(f"data/rating_8l_C_sweep{TAG}.csv",index=False)
print(f"\n  Saved data/rating_8l_C_sweep{TAG}.csv\nDONE.")
