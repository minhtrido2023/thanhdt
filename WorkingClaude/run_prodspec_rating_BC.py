#!/usr/bin/env python3
"""run_prodspec_rating_BC.py — prod-spec backtest of the 8L-rating overlays B & C.

Tests two ways the 8L quality rating (1-5) could participate in the production paper-trade
systems (V1-V5), on the CANONICAL prod spec (run_5systems_prodspec.py), all 3 variants in
one process (signals/prices/states/lagged/ensemble loaded once):

  base          — no rating overlay (must reproduce canonical numbers = control)
  (B) exclude5  — distress exclusion: a buy signal on a rating-5 (impaired: full-year loss
                  or extreme real-leverage) name is suppressed (-> AVOID_rating5). Cut tail
                  risk without touching the rest of the book.
  (C) regime_sz — regime-conditional sizing: weak-rating names (rating>=4) keep full 10%
                  weight in NEUTRAL/BULL/EX-BULL, but are HALVED (5%) in BEAR/CRISIS (state<=2)
                  via the simulator's tier_weights_by_state hook. Rating modulates SIZE only
                  when the regime is risky (per the horizon×state finding: FA matters in stress).

Point-in-time rating from build_rating_8l_history.py (Release_Date stamped, no look-ahead;
banks/power = neutral 3 -> never excluded/down-weighted).

Env: START_DATE (default 2014-01-01), END_DATE (default 2026-05-15).
Output: data/rating_8l_BC_prodspec.csv + console headline table per mode.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = os.environ.get("START_DATE", "2014-01-01")
END_B   = os.environ.get("END_DATE",   "2026-05-15")
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}
ETF_KELLY = {3: 1.0}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = os.environ.get("STATE_CSV_OVERRIDE", "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
SWITCH_COST = 0.005
WEAK_SIZE_STRESS = 0.05   # (C) halved weight for rating>=4 names in BEAR/CRISIS
FULL_SIZE = 0.10

print("="*100); print(f"  8L-RATING B/C OVERLAY PROD-SPEC  {START_B} -> {END_B}  (50B/system)"); print("="*100)

# ─── 1. Signals/prices/VNI ──────────────────────────────────────────────────
print("\n[1] Loading signals + prices + VNI + Open...")
PKL_PATH = os.environ.get("PKL_PATH", "data/ba_v11_unified_12y_sig.pkl")
FA_TABLE = "tav2_bq.fa_ratings"
with open(PKL_PATH,"rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_proxy = dict(zip(vni_B["time"], vni_B["Close"]))
try:
    _etf = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30'
    AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
except Exception:
    _etf = pd.DataFrame(columns=["time", "Close"])
_etf["time"] = pd.to_datetime(_etf["time"]); _etf_real = dict(zip(_etf["time"], _etf["Close"]))
if len(_etf):
    _splice = _etf["time"].min()
    _scale = (_etf_real[_splice] / vn30_proxy[_splice]) if vn30_proxy.get(_splice) else 1.0
    vn30_underlying = {}
    for d in vni_dates_B:
        if d in _etf_real: vn30_underlying[d] = _etf_real[d]
        elif d < _splice and d in vn30_proxy: vn30_underlying[d] = vn30_proxy[d] * _scale
        elif d in vn30_proxy: vn30_underlying[d] = vn30_proxy[d]
    print(f"  ETF underlying: REAL E1VFVN30 from {_splice.date()}")
else:
    vn30_underlying = vn30_proxy; print("  ETF underlying: VNINDEX proxy")

opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# ─── 2. States ──────────────────────────────────────────────────────────────
print("[2] States (TQ34b + LIVE)...")
state_df_tq = pd.read_csv(STATE_CSV_TQ34B); state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
state_ff_tq = {}; last=None
for d in vni_dates_B:
    s = sbd_tq.get(d);
    if s is not None: last = s
    state_ff_tq[d] = last
state_df_live = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
state_df_live["time"] = pd.to_datetime(state_df_live["time"])
sbd_live = dict(zip(state_df_live["time"], state_df_live["state"]))
state_ff_live = {}; last=None
for d in vni_dates_B:
    s = sbd_live.get(d)
    if s is not None: last = s
    state_ff_live[d] = last

# ─── 3. D1 RE_BACKLOG ───────────────────────────────────────────────────────
print("[3] D1 RE_BACKLOG_BUY reclassification...")
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time, SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM {FA_TABLE} AS f),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker, t.time, fa.fa_tier, SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5]) & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])

# ─── 4. SV_TIGHT ────────────────────────────────────────────────────────────
def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS_V11)
sig_B = sig_B[(~mb_buy) | sig_B.apply(sv_tight_keep, axis=1)].copy()
print(f"  After SV_TIGHT: {len(sig_B):,} rows")

# ─── 4b. ATTACH POINT-IN-TIME 8L RATING (as-of merge by eff_time) ───────────
print("[4b] Attaching point-in-time 8L rating...")
rh = pd.read_pickle("data/rating_8l_history.pkl")
rh["eff_time"] = pd.to_datetime(rh["eff_time"])
rh = rh.sort_values("eff_time")[["ticker","eff_time","rating"]]
sig_B = sig_B.sort_values("time")
sig_B = pd.merge_asof(sig_B, rh.rename(columns={"eff_time":"time","rating":"rating8l"}),
                      on="time", by="ticker", direction="backward")
cov = sig_B["rating8l"].notna().mean()
buy_cov = sig_B.loc[sig_B["play_type"].isin(BUY_TIERS_V11), "rating8l"].notna().mean()
print(f"  rating coverage: all={cov:.1%}  buy-signals={buy_cov:.1%}")
print("  buy-signal rating dist:")
print(sig_B.loc[sig_B["play_type"].isin(BUY_TIERS_V11),"rating8l"].value_counts(dropna=False).sort_index().to_string())

# ─── 5. Overheat AVOID (per state series) ───────────────────────────────────
def add_overheat(state_df):
    v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    return set(v[v["overheat"]]["time"])
oh_tq = add_overheat(state_df_tq); oh_live = add_overheat(state_df_live)

# ─── 6. Universe + sector ───────────────────────────────────────────────────
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── 7. Mode transform: produce (sig_tq, sig_live, tiercfg) for a given mode ─
def apply_overheat(sig, oh):
    s = sig.copy()
    s.loc[s["time"].isin(oh) & s["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return s

def build_mode(mode):
    """returns dict with sig_tq, sig_live, allowed_tiers, tier_weights, tier_weights_by_state, sector_cap_exempt"""
    base_tiers = list(TIER_BAL)
    cfg = dict(allowed_tiers=base_tiers,
               tier_weights={t:FULL_SIZE for t in base_tiers},
               tier_weights_by_state=None,
               sector_cap_exempt={"RE_BACKLOG_BUY"})
    s_tq = apply_overheat(sig_B, oh_tq)
    s_live = apply_overheat(sig_B, oh_live)
    if mode == "base":
        pass
    elif mode == "exclude5":
        for s in (s_tq, s_live):
            m = (s["rating8l"]==5) & s["play_type"].isin(BUY_TIERS_V11)
            s.loc[m, "play_type"] = "AVOID_rating5"
        print(f"    [exclude5] tq suppressed: {int(((s_tq['play_type']=='AVOID_rating5')).sum()):,}")
    elif mode == "regime_size":
        # split weak-rating (>=4) buy rows into '<tier>_W'; full weight everywhere EXCEPT state<=2 (halved)
        weak_tiers = [t+"_W" for t in base_tiers]
        all_tiers = base_tiers + weak_tiers
        for s in (s_tq, s_live):
            m = (s["rating8l"]>=4) & s["play_type"].isin(set(base_tiers))   # only BAL tiers carry weights
            s.loc[m, "play_type"] = s.loc[m, "play_type"] + "_W"
        twbs = {}
        for st in (1, 2):  # CRISIS, BEAR: weak names halved
            twbs[st] = {**{t:FULL_SIZE for t in base_tiers}, **{t:WEAK_SIZE_STRESS for t in weak_tiers}}
        cfg = dict(allowed_tiers=all_tiers,
                   tier_weights={t:FULL_SIZE for t in all_tiers},       # states 3/4/5: weak = full size
                   tier_weights_by_state=twbs,
                   sector_cap_exempt={"RE_BACKLOG_BUY","RE_BACKLOG_BUY_W"})
        print(f"    [regime_size] tq weak-split: {int(s_tq['play_type'].astype(str).str.endswith('_W').sum()):,}")
    return dict(sig_tq=s_tq, sig_live=s_live, **cfg)

# ─── 8. Leg runners (parametrized by tier cfg) ──────────────────────────────
def run_bal(sig_use, state_ff, etf_states, cfg, label):
    nav, _ = simulate(sig_use, prices_B, vni_dates_B,
        allowed_tiers=cfg["allowed_tiers"], max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=cfg["sector_cap_exempt"],
        tier_weights=cfg["tier_weights"], tier_weights_by_state=cfg["tier_weights_by_state"],
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True, **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]

def run_vn30(sig_use, state_ff, etf_states, cfg, label):
    sig30 = sig_use[sig_use["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=cfg["allowed_tiers"], max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV, ticker_sector_map=sec_map,
        tier_weights=cfg["tier_weights"], tier_weights_by_state=cfg["tier_weights_by_state"],
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True, **LIQ30, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]

# ─── 9. LAGGED schedule (rating-independent, compute ONCE) ───────────────────
print("\n[9] LAGGED schedule (computed once)...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
_liqr = bq(f"""SELECT t.time, t.ticker, t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq_real
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Volume_3M_P50 IS NOT NULL""")
_liqr["time"] = pd.to_datetime(_liqr["time"])
liq_real_l = _liqr.pivot_table(index="time", columns="ticker", values="liq_real", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]], on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0; ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]; cur_date = row["Release_Date"]; n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history]); posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25; w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
e_hl3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])
ENTRY_OFFSET, HOLD_DAYS, LAG_MAX_POS, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")
def run_lagged(init_nav, use_s2, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001; LIQ_CAP, MAX_FILL = 0.20, 5
    for dt in sim_days:
        if dt in exits_by_day.groups:
            for _, ex_row in exits_by_day.get_group(dt).iterrows():
                tk = ex_row["ticker"]
                if tk not in positions: continue
                pos = positions[tk]
                if pos["exit_dt"] != dt: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                gross = pos["shares"]*fpx*(1-SLIP_OUT); cash += gross*(1-TAX); del positions[tk]
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= LAG_MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                liq_real = liq_real_l.at[dt, tk] if tk in liq_real_l.columns else 0
                if pd.isna(liq_real) or liq_real < LIQ_MIN: continue
                pos_pct = (0.10 if en_row["surprise"] > 0.5 else 0.08) if use_s2 else 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * liq_real * MAX_FILL; alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px; cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm,"cash":cash})
    return pd.DataFrame(nav_history).set_index("time")["nav"]
nav_lag_v12  = run_lagged(BOOK_NAV, use_s2=False); print(f"  LAG v12 : {nav_lag_v12.iloc[-1]/1e9:.3f}B")
nav_lag_v121 = run_lagged(BOOK_NAV, use_s2=True);  print(f"  LAG v121: {nav_lag_v121.iloc[-1]/1e9:.3f}B")

# ─── 10. M1+M3r ensemble (rating-independent, once) ─────────────────────────
print("[10] Ensemble signal...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time, ticker, ret_6m, adv_1y, ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL)
SELECT time, AVG(IF(rnk<=10, ret_6m, NULL)) AS top10_ret, AVG(ret_6m) AS all_ret FROM ranked GROUP BY time ORDER BY time"""
m3r_df = bq(m3r_q); m3r_df["time"] = pd.to_datetime(m3r_df["time"])
m3r_df["M3r"] = m3r_df["top10_ret"] - m3r_df["all_ret"]; m3r = m3r_df.set_index("time")["M3r"]
def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index(); em = s.expanding(min_periods=min_history).median()
    raw = (s > em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m3r = make_signal(m3r)

# ─── 11. Run all 3 modes ────────────────────────────────────────────────────
def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)].dropna()
    if len(s)<30: return None
    rets = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s-s.cummax())/s.cummax()).min(); cal = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal}

results = {}
for mode in ["base","exclude5","regime_size"]:
    print(f"\n{'='*100}\n  MODE = {mode}\n{'='*100}")
    M = build_mode(mode)
    bal_tq_base   = run_bal(M["sig_tq"],   state_ff_tq,   ETF_BASE,  M, "BAL_TQ_base")
    bal_live_base = run_bal(M["sig_live"], state_ff_live, ETF_BASE,  M, "BAL_LIVE_base")
    bal_tq_kelly  = run_bal(M["sig_tq"],   state_ff_tq,   ETF_KELLY, M, "BAL_TQ_kelly")
    vn30_tq_base  = run_vn30(M["sig_tq"],  state_ff_tq,   ETF_BASE,  M, "VN30_TQ_base")
    vn30_tq_kelly = run_vn30(M["sig_tq"],  state_ff_tq,   ETF_KELLY, M, "VN30_TQ_kelly")
    common = bal_tq_base.index.intersection(vn30_tq_base.index).intersection(nav_lag_v12.index).intersection(nav_lag_v121.index).intersection(bal_live_base.index).intersection(bal_tq_kelly.index).intersection(vn30_tq_kelly.index)
    m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int); m3r_a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
    def ensemble_AND_hold(m1, m3):
        out = np.zeros(len(m1), dtype=int); cur = int(m1.iloc[0])
        for i, (a, b) in enumerate(zip(m1.values, m3.values)):
            if a == b: cur = int(a)
            out[i] = cur
        return pd.Series(out, index=m1.index)
    sig_AH = ensemble_AND_hold(m1, m3r_a)
    nav_V1 = (bal_tq_base.loc[common] + vn30_tq_base.loc[common]) / TOTAL_NAV
    nav_V2 = (bal_tq_base.loc[common] + nav_lag_v12.loc[common]) / TOTAL_NAV
    nav_V3 = (bal_live_base.loc[common] + nav_lag_v12.loc[common]) / TOTAL_NAV
    def switched_nav(bal_s, vn30_s, lag_s, signal, switch_cost=SWITCH_COST):
        bal_ret = bal_s.pct_change().fillna(0); vn30_ret = vn30_s.pct_change().fillna(0); lag_ret = lag_s.pct_change().fillna(0)
        nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
        second = np.full(len(common), BOOK_NAV, dtype=float); prev_sig = int(signal.iloc[0])
        for i in range(1, len(common)):
            cur_sig = int(signal.iloc[i])
            second[i] = second[i-1]*(1-switch_cost) if cur_sig != prev_sig else second[i-1]
            r = vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
            second[i] = second[i]*(1+r); prev_sig = cur_sig
        return pd.Series((nav_bal_path.values + second) / TOTAL_NAV, index=common)
    nav_V4 = switched_nav(bal_tq_base.loc[common],  vn30_tq_base.loc[common],  nav_lag_v121.loc[common], sig_AH)
    nav_V5 = switched_nav(bal_tq_kelly.loc[common], vn30_tq_kelly.loc[common], nav_lag_v121.loc[common], sig_AH)
    cmin, cmax = common.min(), common.max()
    results[mode] = {nm: metrics(nav, cmin, cmax) for nm, nav in
                     [("V1",nav_V1),("V2",nav_V2),("V3",nav_V3),("V4",nav_V4),("V5",nav_V5)]}
    results[mode]["_navs"] = {"V1":nav_V1,"V2":nav_V2,"V3":nav_V3,"V4":nav_V4,"V5":nav_V5}

# ─── 12. Compare + save ─────────────────────────────────────────────────────
print(f"\n{'='*100}\n  COMPARISON ({START_B} -> {END_B})  —  Δ vs base in (pp CAGR / Sharpe / pp DD)\n{'='*100}")
hdr = f"  {'Sys':<5}" + "".join(f"{m:>30}" for m in ["base","exclude5 (B)","regime_size (C)"])
print(hdr)
for sysn in ["V1","V2","V3","V4","V5"]:
    b = results["base"][sysn]
    cells = [f"{b['CAGR']:.2f}% Sh{b['Sharpe']:.2f} DD{b['DD']:.1f}"]
    for mode in ["exclude5","regime_size"]:
        r = results[mode][sysn]
        cells.append(f"{r['CAGR']:.2f}%({r['CAGR']-b['CAGR']:+.2f}) Sh{r['Sharpe']:.2f} DD{r['DD']:.1f}")
    print(f"  {sysn:<5}" + "".join(f"{c:>30}" for c in cells))

rows = []
for mode in ["base","exclude5","regime_size"]:
    for sysn in ["V1","V2","V3","V4","V5"]:
        r = results[mode][sysn]
        rows.append({"mode":mode,"system":sysn,**r})
pd.DataFrame(rows).to_csv("data/rating_8l_BC_prodspec.csv", index=False)
# save NAV series of the best variant for inspection
allnav = {}
for mode in ["base","exclude5","regime_size"]:
    for sysn in ["V1","V2","V3","V4","V5"]:
        allnav[f"{mode}_{sysn}"] = results[mode]["_navs"][sysn]
pd.DataFrame(allnav).to_csv("data/rating_8l_BC_prodspec_navs.csv")
print("\n  Saved: data/rating_8l_BC_prodspec.csv + _navs.csv")
print("DONE.")
