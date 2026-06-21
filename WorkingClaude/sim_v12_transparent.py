# -*- coding: utf-8 -*-
"""V12 'AM DUONG' transparent simulation 2025-06-09 -> 2026-05-15, 50B NAV.

Architecture (per ba_v12_am_duong_spec.md):
  - 25B BAL leg: BA v11 stack (SV_TIGHT + P3 + RE_BACKLOG + V6 ETF parking)
  - 25B LAGGED leg: HL_3y earnings-drift book

Outputs (analyze_portfolio.py compatible):
  data/v12_transparent_logs.csv          - daily NAV + cash + n_pos + n_tx
  data/v12_transparent_transactions.csv  - every buy/sell + ETF rebalance + MTM phantoms
  data/v12_transparent_open_positions.csv - unrealized P&L snapshot at end
  data/v12_transparent_report.md         - analyze_portfolio.py output + reconciliation
"""
import os, sys, io, pickle, bisect
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2025-06-09"
END_DATE   = "2026-05-15"  # data cache end
TOTAL_NAV  = 50e9
BAL_NAV    = 25e9
LAG_NAV    = 25e9
POSITION_VND = 1.25e9
FILL_CAP = 0.20
T1_TOP_ADV = 50e9

INTRADAY_PKL = os.path.join(WORKDIR, "intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                  "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}

print("="*100)
print(f"  V12 'AM DUONG' TRANSPARENT SIM   period={START_DATE} -> {END_DATE}   NAV={TOTAL_NAV/1e9:.0f}B")
print(f"  Architecture: 25B BAL (BA v11 + V6 ETF) + 25B LAGGED (HL_3y)")
print("="*100)

# ============================================================================
# 1. Intraday cache for v4 HYBRID BUY fill
# ============================================================================
print("\n[1] Building v4 HYBRID alt-fill prices...")
with open(INTRADAY_PKL,"rb") as f: intraday = pickle.load(f)
adv_by_ticker = {}
slot_price_atc, slot_vol_atc, slot_price_t1115, slot_vol_t1115 = {},{},{},{}
for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"]); b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M"); b["close_vnd"] = b["close"].astype(float)*1000.0
    b["vnd_traded"] = b["close_vnd"]*b["volume"].astype(float)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    adv_by_ticker[tk] = float(sess.mean())
    for label, hm, pd_, vd_ in [("atc","14:45",slot_price_atc,slot_vol_atc),
                                  ("t1115","11:15",slot_price_t1115,slot_vol_t1115)]:
        sub = b[b["hm"]==hm]
        for _, row in sub.iterrows():
            d_ts = row["date_ts"]
            pd_.setdefault(tk,{})[d_ts] = float(row["close_vnd"])
            vd_.setdefault(tk,{})[d_ts] = float(row["vnd_traded"])
alt_hybrid = {}
for tk in set(slot_price_atc.keys()) | set(slot_price_t1115.keys()):
    adv = adv_by_ticker.get(tk,0)
    is_top = adv >= T1_TOP_ADV
    src_p = slot_price_atc.get(tk,{}) if is_top else slot_price_t1115.get(tk,{})
    src_v = slot_vol_atc.get(tk,{}) if is_top else slot_vol_t1115.get(tk,{})
    for d_ts, p in src_p.items():
        v = src_v.get(d_ts)
        if v is not None and v*FILL_CAP >= POSITION_VND:
            alt_hybrid.setdefault(tk,{})[d_ts] = p

# ============================================================================
# 2. Load BA v11 signals + filters
# ============================================================================
print("\n[2] Loading v10 signals + Release_Date + 5-state + overheat + D1 override...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  signals: {len(sig):,} rows")

rel = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
rel["Release_Date"] = pd.to_datetime(rel["Release_Date"])
rel_by_tk = rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds_arr = np.empty(len(sig))
for i,(tk,t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = rel_by_tk.get(tk)
    if not arr: ds_arr[i]=np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    ds_arr[i] = np.nan if idx==0 else (pd.Timestamp(t)-arr[idx-1]).days
sig["days_since_release"] = ds_arr

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"]/vni_full["MA200"]
vni_full["state"] = vni_full["time"].map(state_by_date)
vni_full["overheat"] = (vni_full["ratio"]>1.30) & ((vni_full["state"]==5)|(vni_full["D_RSI"]>0.75))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])

sig["state"] = sig["time"].map(state_by_date)

# D1 RE_BACKLOG_BUY override
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
LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig = sig.merge(d1_q, on=["ticker","time"], how="left")
omask = sig["_d1_ok"].fillna(False) & (sig["ta"]>=120)
sig.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])

def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb = sig["play_type"].isin(BUY_TIERS_V11)
mk = (~mb) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mk].copy()
mp3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mp3,"play_type"] = "AVOID_overheated"
print(f"  D1 reclassified: {int(omask.sum())}; SV_TIGHT filtered: {int((mb & ~sig.apply(sv_tight_keep,axis=1)).sum())}; P3 blocked: {int(mp3.sum())}")

# ============================================================================
# 3. Common data (prices, opens, sec_map, ETF prices, state ff)
# ============================================================================
print("\n[3] Loading prices/Open/sector/E1VFVN30...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
prices = {tk: dict(zip(g["time"], g["Close"])) for tk,g in sig_f.groupby("ticker")}
liq_map = {(r["ticker"],r["time"]): r["liq"] for _,r in sig_f.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
etf_real["time"] = pd.to_datetime(etf_real["time"])
vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

state_ff = {}; last_s=None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct":0.20,"max_fill_days":5,
            "liquidity_lookup":liq_map,"exit_slippage_tiered":True}

# ============================================================================
# 4. Run BAL book @ 25B (with transparent event_log + etf_log)
# ============================================================================
print("\n[4] Running BAL book @ 25B...")
events_bal = []; etf_bal = []
nav_bal, trades_bal = simulate(sig_f, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BAL_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=0.0, state_by_date=state_ff,
    cash_etf_states={3:0.7}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    event_log=events_bal, etf_log=etf_bal,
    force_close_eod=False,
    **LIQ_FULL, name="v12_BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  BAL events: {len(events_bal)} stock + {len(etf_bal)} ETF; closed_trades={len(trades_bal)}")
print(f"  BAL final: {nav_bal.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 5. Run LAGGED book @ 25B (transparent loop with event emission)
# ============================================================================
print("\n[5] Running LAGGED book @ 25B (transparent)...")
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

ev = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
LN2 = np.log(2); HL = 3.0
ev["pa_HL3"] = np.nan; ev["prior_n_good"] = 0
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        ev.at[row_idx,"prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2*age_yrs/HL)
            ev.at[row_idx,"pa_HL3"] = (posts_arr*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS, POS_PCT = 5.0, 4, 0.15, 5, 25, 12, 0.08
e = ev[(ev["NP_R"]>=NPR_MIN*100) & (ev["prior_n_good"]>=N_MIN) & (ev["pa_HL3"]>=POST_MIN)].copy()

sw = pd.Timestamp(START_DATE); ew = pd.Timestamp(END_DATE)
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right")-1
    if pos<0: return None
    tgt = pos+offset
    if tgt>=len(all_dates) or tgt<0: return None
    return pd.Timestamp(all_dates[tgt])

schedule = []
for _, row in e.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY); exit_dt = offset_date(rdt, ENTRY+HOLD)
    if entry_dt is None or exit_dt is None: continue
    if entry_dt < sw or entry_dt > ew: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"release_dt":rdt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
print(f"  LAGGED signals in window: {len(sched_lag)}")
entries_by_day = sched_lag.groupby("entry_dt")
exits_by_day = sched_lag.groupby("exit_dt")

sim_days_lag = [d for d in master_idx if sw <= d <= ew]
cash_l = LAG_NAV
positions_l = {}
nav_history_l = []
events_lag = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
hid_seq = 0

for dt in sim_days_lag:
    # 1. EXITS first
    if dt in exits_by_day.groups:
        for _, ex_row in exits_by_day.get_group(dt).iterrows():
            tk = ex_row["ticker"]
            if tk not in positions_l: continue
            pos = positions_l[tk]
            if pos["exit_dt"] != dt: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx<=0:
                fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
            gross = pos["shares"]*fpx          # CLEAN gross
            slip = gross*SLIP_OUT
            tax = (gross-slip)*TAX
            fee_total = slip + tax
            proceeds = gross - fee_total
            cash_l += proceeds
            events_lag.append({
                "ymd": dt, "ticker": tk, "action": "sell",
                "buy_amount": 0.0,
                "sell_amount": float(gross),
                "fee": float(fee_total),
                "adj_price": float(fpx),
                "shares": float(pos["shares"]),
                "holding_id": pos["holding_id"],
                "play_type": "LAGGED_HL3",
                "cash_after": float(cash_l),
                "reason": "LAGGED_EXIT_T30",
                "book": "LAGGED",
            })
            del positions_l[tk]
    # 2. ENTRIES
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*(px_close.at[dt,tk] if tk in px_close.columns and pd.notna(px_close.at[dt,tk]) else p["entry_px"]) for tk,p in positions_l.items())
        nav_now = cash_l + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions_l or len(positions_l)>=MAX_POS: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx<=0: continue
            adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            target = POS_PCT*nav_now
            cap = LIQ_CAP*adv*MAX_FILL*fpx
            alloc = min(target, cap)
            if alloc<1e6 or alloc>cash_l: continue
            eff_px = fpx*(1+SLIP_IN)
            shares = alloc/eff_px
            share_cost = shares*fpx           # CLEAN
            slip_cost = shares*fpx*SLIP_IN
            cash_l -= (share_cost + slip_cost)
            hid_seq += 1
            hid = f"{tk}_{dt.strftime('%Y%m%d')}_LAG{hid_seq:03d}"
            positions_l[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],
                               "shares":shares,"entry_px":fpx,"holding_id":hid}
            events_lag.append({
                "ymd": dt, "ticker": tk, "action": "buy",
                "buy_amount": float(share_cost),
                "sell_amount": 0.0,
                "fee": float(slip_cost),
                "adj_price": float(fpx),
                "shares": float(shares),
                "holding_id": hid,
                "play_type": "LAGGED_HL3",
                "cash_after": float(cash_l),
                "reason": "LAGGED_ENTRY_T5",
                "book": "LAGGED",
            })
    # 3. EOD NAV
    mtm = 0.0
    for tk, p in positions_l.items():
        px = px_close.at[dt, tk] if tk in px_close.columns else np.nan
        if pd.isna(px): px = p["entry_px"]
        mtm += p["shares"]*px
    nav_history_l.append({"time":dt, "cash":cash_l, "positions_mv":mtm, "nav":cash_l+mtm, "n_pos":len(positions_l)})

nav_lag = pd.DataFrame(nav_history_l)
nav_lag["time"] = pd.to_datetime(nav_lag["time"])
print(f"  LAGGED events: {len(events_lag)} (entries+exits)   final NAV: {nav_lag['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 6. Merge BAL + LAGGED into combined transparent log
# ============================================================================
print("\n[6] Merging logs + transactions...")
nav_b_s = nav_bal.set_index("time")["nav"]
nav_l_s = nav_lag.set_index("time")["nav"]
common = nav_b_s.index.intersection(nav_l_s.index)
combined_nav = nav_b_s.loc[common] + nav_l_s.loc[common]

cash_b = nav_bal.set_index("time")["cash"].loc[common]
etf_b = nav_bal.set_index("time")["cash_etf"].loc[common]
stk_b = (nav_bal.set_index("time")["positions_mv"] + nav_bal.set_index("time")["pending_mv"]).loc[common]
n_pos_b = nav_bal.set_index("time")["n_pos"].loc[common]

cash_l = nav_lag.set_index("time")["cash"].loc[common]
stk_l = nav_lag.set_index("time")["positions_mv"].loc[common]
n_pos_l = nav_lag.set_index("time")["n_pos"].loc[common]

def annot(events, book):
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events)
    if "book" not in df.columns: df["book"] = book
    return df

events_all = pd.concat([annot(events_bal,"BAL")], ignore_index=True) if events_bal else pd.DataFrame()
if not events_all.empty: events_all["ymd"] = pd.to_datetime(events_all["ymd"])
etf_all = annot(etf_bal,"BAL")

if not etf_all.empty:
    etf_tx = pd.DataFrame({
        "ymd": pd.to_datetime(etf_all["ymd"]),
        "ticker": "E1VFVN30",
        "action": etf_all["action"].apply(lambda a: "buy" if a=="buy_etf" else "sell"),
        "buy_amount": np.where(etf_all["action"]=="buy_etf", etf_all["amount_vnd"], 0.0),
        "sell_amount": np.where(etf_all["action"]=="sell_etf", etf_all["amount_vnd"], 0.0),
        "fee": etf_all["friction_cost"],
        "adj_price": etf_all["price_vn30"],
        "shares": etf_all["shares"],
        "holding_id": etf_all["holding_id"],
        "play_type": "ETF_PARK",
        "cash_after": etf_all["cash_after"],
        "reason": "ETF_REBAL_state" + etf_all["state"].astype(str),
        "book": "BAL",
    })
else:
    etf_tx = pd.DataFrame()

lag_tx = annot(events_lag, "LAGGED")
if not lag_tx.empty: lag_tx["ymd"] = pd.to_datetime(lag_tx["ymd"])

all_tx = pd.concat([events_all, etf_tx, lag_tx], ignore_index=True)
all_tx["ymd"] = pd.to_datetime(all_tx["ymd"])
all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

tx_counts = all_tx.groupby(all_tx["ymd"]).size().cumsum()
n_tx_series = pd.Series(0, index=common, dtype=int)
for d, n in tx_counts.items():
    n_tx_series.loc[n_tx_series.index >= d] = int(n)

combined_logs = pd.DataFrame({
    "ymd": common,
    "nav": combined_nav.values,
    "BAL_cash": cash_b.values, "BAL_stocks": stk_b.values, "BAL_etf": etf_b.values,
    "LAGGED_cash": cash_l.values, "LAGGED_stocks": stk_l.values,
    "cash": (cash_b + cash_l).values,
    "cash_etf": etf_b.values,
    "stocks_mv": (stk_b + stk_l).values,
    "num_holdings": (n_pos_b + n_pos_l).values,
    "num_transactions": n_tx_series.values,
    "state": pd.Series(common).map(state_ff).values,
})
print(f"  Combined: {len(combined_logs)} days, {len(all_tx)} transactions")

# ============================================================================
# 7. Save CSVs + open positions snapshot + MTM phantoms
# ============================================================================
print("\n[7] Saving CSVs + open positions...")
os.makedirs(os.path.join(WORKDIR,"data"), exist_ok=True)

def safe_to_csv(df, path):
    try:
        df.to_csv(path, index=False)
        return path
    except PermissionError:
        alt = path.replace(".csv",".new.csv"); df.to_csv(alt, index=False); return alt

logs_path = safe_to_csv(combined_logs, os.path.join(WORKDIR,"data","v12_transparent_logs.csv"))

# Open positions: BAL stocks + BAL ETF lots + LAGGED stocks
open_bal = nav_bal.attrs.get("open_positions_final") if hasattr(nav_bal,"attrs") else None
etf_lots_bal = nav_bal.attrs.get("etf_lots_final") if hasattr(nav_bal,"attrs") else None
open_lag_rows = []
last_day = common[-1]
for tk, p in positions_l.items():
    last_px = px_close.at[last_day, tk] if tk in px_close.columns and pd.notna(px_close.at[last_day, tk]) else p["entry_px"]
    cost = p["shares"]*p["entry_px"]
    mark = p["shares"]*last_px
    open_lag_rows.append({"ticker":tk,"holding_id":p["holding_id"],"entry_date":p["entry_dt"],
                          "days_held":(last_day-p["entry_dt"]).days,"shares":p["shares"],
                          "last_price":last_px,"cost_basis":cost,"mark_value":mark,
                          "unrealised_pnl":mark-cost,
                          "unrealised_ret_pct":(mark/cost-1)*100 if cost>0 else 0,
                          "play_type":"LAGGED_HL3","book":"LAGGED"})
open_lag = pd.DataFrame(open_lag_rows)

open_df = pd.concat([
    (open_bal.assign(book="BAL") if open_bal is not None and not open_bal.empty else pd.DataFrame()),
    (etf_lots_bal.assign(book="BAL") if etf_lots_bal is not None and not etf_lots_bal.empty else pd.DataFrame()),
    open_lag,
], ignore_index=True)

# MTM phantom rows
mtm_rows = []
if open_bal is not None and not open_bal.empty:
    for _, p in open_bal.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":p["ticker"],"action":"sell",
            "buy_amount":0.0,"sell_amount":float(p["mark_value"]),"fee":0.0,
            "adj_price":float(p["last_price"]),"shares":float(p["shares"]),
            "holding_id":p["holding_id"],"play_type":p["play_type"],"cash_after":None,
            "reason":"MTM_UNREALIZED","book":"BAL"})
if etf_lots_bal is not None and not etf_lots_bal.empty:
    for _, lot in etf_lots_bal.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":"E1VFVN30","action":"sell",
            "buy_amount":0.0,"sell_amount":float(lot["mark_value"]),"fee":0.0,
            "adj_price":float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
            "shares":float(lot["shares"]),"holding_id":lot["holding_id"],
            "play_type":"ETF_PARK","cash_after":None,"reason":"MTM_UNREALIZED","book":"BAL"})
for r in open_lag_rows:
    mtm_rows.append({"ymd":last_day,"ticker":r["ticker"],"action":"sell",
        "buy_amount":0.0,"sell_amount":float(r["mark_value"]),"fee":0.0,
        "adj_price":float(r["last_price"]),"shares":float(r["shares"]),
        "holding_id":r["holding_id"],"play_type":"LAGGED_HL3","cash_after":None,
        "reason":"MTM_UNREALIZED","book":"LAGGED"})
if mtm_rows:
    mtm_df = pd.DataFrame(mtm_rows)
    all_tx = pd.concat([all_tx, mtm_df], ignore_index=True)
    all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

tx_path = safe_to_csv(all_tx, os.path.join(WORKDIR,"data","v12_transparent_transactions.csv"))
open_path = safe_to_csv(open_df, os.path.join(WORKDIR,"data","v12_transparent_open_positions.csv"))
print(f"  {logs_path}")
print(f"  {tx_path}  (incl {len(mtm_rows)} MTM phantoms)")
print(f"  {open_path}: {len(open_df)} open positions")

# ============================================================================
# 8. Summary + reconciliation
# ============================================================================
print("\n[8] Reconciliation")
final_nav = combined_nav.iloc[-1]
final_cash = (cash_b + cash_l).iloc[-1]
final_etf = etf_b.iloc[-1]
final_pos = stk_b.iloc[-1] + stk_l.iloc[-1]
years = (common[-1]-common[0]).days/365.25
cagr = (final_nav/TOTAL_NAV)**(1/years)-1
total_ret = (final_nav/TOTAL_NAV-1)*100
peak = combined_nav.cummax()
dd = ((combined_nav-peak)/peak).min()*100

print(f"  Period: {common[0].date()} -> {common[-1].date()} ({years:.3f} years)")
print(f"  Init: {TOTAL_NAV/1e9:.2f}B   Final: {final_nav/1e9:.4f}B   ret={total_ret:+.2f}%   CAGR={cagr*100:+.2f}%   DD={dd:+.2f}%")
print(f"    cash {final_cash/1e9:.4f}B + ETF {final_etf/1e9:.4f}B + positions {final_pos/1e9:.4f}B")

real_tx = all_tx[all_tx["reason"]!="MTM_UNREALIZED"]
stock_real = real_tx[real_tx["ticker"]!="E1VFVN30"]
etf_real_tx = real_tx[real_tx["ticker"]=="E1VFVN30"]

stk_buy_amt = stock_real[stock_real["action"]=="buy"]["buy_amount"].sum()
stk_buy_fee = stock_real[stock_real["action"]=="buy"]["fee"].sum()
stk_sell_amt = stock_real[stock_real["action"]=="sell"]["sell_amount"].sum()
stk_sell_fee = stock_real[stock_real["action"]=="sell"]["fee"].sum()
etf_buy_amt = etf_real_tx[etf_real_tx["action"]=="buy"]["buy_amount"].sum()
etf_buy_fee = etf_real_tx[etf_real_tx["action"]=="buy"]["fee"].sum()
etf_sell_amt = etf_real_tx[etf_real_tx["action"]=="sell"]["sell_amount"].sum()
etf_sell_fee = etf_real_tx[etf_real_tx["action"]=="sell"]["fee"].sum()

stk_out = stk_buy_amt + stk_buy_fee
stk_in  = stk_sell_amt - stk_sell_fee
etf_out = etf_buy_amt + etf_buy_fee
etf_in  = etf_sell_amt - etf_sell_fee

mtm_sells = all_tx[all_tx["reason"]=="MTM_UNREALIZED"]
mtm_stocks = mtm_sells[mtm_sells["ticker"]!="E1VFVN30"]["sell_amount"].sum()
mtm_etf = mtm_sells[mtm_sells["ticker"]=="E1VFVN30"]["sell_amount"].sum()

expected_cash = TOTAL_NAV - stk_out + stk_in - etf_out + etf_in
print()
print(f"  CASH-FLOW RECONCILIATION (from transactions CSV, excludes MTM_UNREALIZED):")
print(f"    STOCK: buys clean={stk_buy_amt/1e9:+.4f}B  buy_fee={stk_buy_fee/1e9:+.4f}B  sells clean={stk_sell_amt/1e9:+.4f}B  sell_fee={stk_sell_fee/1e9:+.4f}B")
print(f"      cash_out={stk_out/1e9:+.4f}B  cash_in={stk_in/1e9:+.4f}B  net realized P&L={(stk_in-stk_out)/1e9:+.4f}B")
print(f"    ETF:   buys clean={etf_buy_amt/1e9:+.4f}B  fee={etf_buy_fee/1e9:+.4f}B  sells clean={etf_sell_amt/1e9:+.4f}B  fee={etf_sell_fee/1e9:+.4f}B")
print(f"      cash_out={etf_out/1e9:+.4f}B  cash_in={etf_in/1e9:+.4f}B  net cash_flow={(etf_in-etf_out)/1e9:+.4f}B")
print(f"    MTM: open stock value={mtm_stocks/1e9:+.4f}B   open ETF value={mtm_etf/1e9:+.4f}B")
print()
print(f"  EXPECTED end cash = init - stk_out + stk_in - etf_out + etf_in = {expected_cash/1e9:+.4f}B")
print(f"  ACTUAL   end cash = {final_cash/1e9:+.4f}B")
print(f"  DIFF (ETF appreciation rebalanced into cash): {(final_cash-expected_cash)/1e9:+.4f}B")
print()
print(f"  FINAL NAV CHECK:")
print(f"    actual_cash {final_cash/1e9:+.4f}B + actual_ETF {final_etf/1e9:+.4f}B + open_stock_MTM {mtm_stocks/1e9:+.4f}B")
print(f"    = {(final_cash+final_etf+mtm_stocks)/1e9:+.4f}B   vs   sim NAV {final_nav/1e9:+.4f}B")
print(f"    delta: {(final_cash+final_etf+mtm_stocks - final_nav)/1e6:+.4f}M  (should be ~0)")

print("\nDone. Now run analyze_portfolio.py to generate the full report.")
