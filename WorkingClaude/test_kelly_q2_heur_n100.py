# -*- coding: utf-8 -*-
"""Shadow backtest — Kelly Q2: HEUR_N100 vs current HEURISTIC (BA v11 full stack).

Per kelly_sizing_q2q3_spec.md Section 1, we shadow-test the only Kelly-derived
change worth deploying: lift NEUTRAL ETF deployment 70% -> 100%, everything else
unchanged.

  BASELINE (current heuristic):  cash_etf_states = {1:0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}
  HEUR_N100  (proposed):         cash_etf_states = {1:0, 2:0.2, 3:1.0, 4:1.0, 5:1.3}

Stack: full BA v11 (SV_TIGHT + P3 + D1 RE_BACKLOG_BUY + 50/50 BAL+VN30 +
V6 ETF overlay) on 12-year window 2014-01-02 -> 2026-04-03, 50B init,
T+1 Open exec, slot12 (max_pos=12, 10% fixed sizing).

Real E1VFVN30 ETF prices are used where available (2016-01-07 -> 2026-05-18);
pre-2016 falls back to VNINDEX-proxy for the ETF leg (identical in both arms,
so cancels out of the diff).

Outputs:
  kelly_q2_out/<arm>_logs.csv             — daily NAV (combined + per-book)
  kelly_q2_out/<arm>_transactions.csv     — every buy/sell + ETF rebalance
  kelly_q2_out/<arm>_open_positions.csv   — unrealised P&L at end
  kelly_q2_heur_n100_results.md           — side-by-side verdict table
"""
import os, sys, io, pickle, bisect
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_q2_out")
os.makedirs(OUTDIR, exist_ok=True)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

# ==============================================================================
# Canonical production config (v11)
# ==============================================================================
START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9                # 50/50 BAL + VN30
POSITION_VND = BOOK_NAV * 0.10   # 10% per slot
FILL_CAP = 0.20
T1_TOP_ADV = 50e9

INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY",
                 "S_PRO","RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}

# Q2 weight maps
W_BASELINE = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
W_HEUR_N100 = {1: 0.0, 2: 0.2, 3: 1.0, 4: 1.0, 5: 1.3}

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
    ("Y2022",           "2022-01-01", "2022-12-31"),
    ("Y2024",           "2024-01-01", "2024-12-31"),
    ("Y2025",           "2025-01-01", "2025-12-31"),
    ("Y2026 partial",   "2026-01-01", "2026-04-03"),
]

print("=" * 100)
print("  KELLY Q2 SHADOW BACKTEST — HEUR_N100 vs BASELINE (full BA v11 stack)")
print(f"  Period: {START_DATE} -> {END_DATE}, NAV={TOTAL_NAV/1e9:.0f}B (50/50 BAL+VN30)")
print(f"  BASELINE  ETF weights: {W_BASELINE}")
print(f"  HEUR_N100 ETF weights: {W_HEUR_N100}")
print("=" * 100)

# ==============================================================================
# 1) Build intraday alt-fill dict (BUY only; SELL stays T+1 Open canonical)
# ==============================================================================
print("\n[1/8] Building v4 HYBRID alt-fill price dict...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)
print(f"  Loaded {len(intraday)} tickers from intraday cache")

adv_by_ticker = {}
slot_price_atc, slot_vol_atc = {}, {}
slot_price_t1115, slot_vol_t1115 = {}, {}
for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M")
    b["close_vnd"] = b["close"].astype(float) * 1000.0
    b["vnd_traded"] = b["close_vnd"] * b["volume"].astype(float)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    adv_by_ticker[tk] = float(sess.mean())
    for hm, p_dict, v_dict in [
        ("14:45", slot_price_atc, slot_vol_atc),
        ("11:15", slot_price_t1115, slot_vol_t1115),
    ]:
        sub = b[b["hm"] == hm]
        if sub.empty: continue
        for _, row in sub.iterrows():
            d_ts = row["date_ts"]
            p_dict.setdefault(tk, {})[d_ts] = float(row["close_vnd"])
            v_dict.setdefault(tk, {})[d_ts] = float(row["vnd_traded"])

alt_hybrid = {}
n_atc_full = n_t1115_full = n_skipped = 0
for tk in set(slot_price_atc.keys()) | set(slot_price_t1115.keys()):
    adv = adv_by_ticker.get(tk, 0)
    is_t1_top = adv >= T1_TOP_ADV
    src_p = slot_price_atc.get(tk, {}) if is_t1_top else slot_price_t1115.get(tk, {})
    src_v = slot_vol_atc.get(tk, {}) if is_t1_top else slot_vol_t1115.get(tk, {})
    for d_ts, p in src_p.items():
        v = src_v.get(d_ts)
        if v is not None and v * FILL_CAP >= POSITION_VND:
            alt_hybrid.setdefault(tk, {})[d_ts] = p
            if is_t1_top: n_atc_full += 1
            else: n_t1115_full += 1
        else:
            n_skipped += 1
print(f"  Hybrid alt-fill: ATC {n_atc_full:,} / T1115 {n_t1115_full:,} / "
      f"gated->OPEN {n_skipped:,}")

# ==============================================================================
# 2) Load signals + Release_Date + 5-state + overheat (V11 stack)
# ==============================================================================
print("\n[2/8] Loading v10 signals + filters (12y)...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = (releases.sort_values(["ticker","Release_Date"])
                     .groupby("ticker")["Release_Date"].apply(list).to_dict())
ds = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = release_by_ticker.get(tk)
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_full["state"] = vni_full["time"].map(state_by_date)
vni_full["overheat"] = ((vni_full["ratio"] > 1.30)
                       & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

sig["state"] = sig["time"].map(state_by_date)

# D1 RE_BACKLOG_BUY override (production logic, ported)
print("\n[2b/8] D1 RE_BACKLOG_BUY tier override...")
d1_sql = f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated_d1 AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated_d1 AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
LEFT JOIN fa_dated_d1 AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
LEFT JOIN fin_dated_d1 AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
   AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker = t.ticker AND t.time >= adv.f_time
   AND (adv.next_f_time IS NULL OR t.time < adv.next_f_time)
WHERE t.ICB_Code = 8633
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
d1 = bq(d1_sql)
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (
    d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5)
    & d1["fa_tier"].isin(["C", "D"])
    & d1["state5"].isin([3, 4, 5])
    & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0))
)
d1_qual = d1.loc[d1_mask, ["ticker", "time"]].assign(_d1_ok=True)
sig = sig.merge(d1_qual, on=["ticker", "time"], how="left")
override_mask = sig["_d1_ok"].fillna(False) & (sig["ta"] >= 120)
sig.loc[override_mask, "play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])
print(f"  D1 override: {int(override_mask.sum()):,} signal rows")

def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mask_bacore = sig["play_type"].isin(BUY_TIERS_V11)
mask_keep = (~mask_bacore) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mask_keep].copy()
n_filt = (mask_bacore & ~sig.apply(sv_tight_keep, axis=1)).sum()
mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"
print(f"  SV_TIGHT filtered {n_filt:,}; P3 blocked {int(mask_p3.sum()):,}")

# ==============================================================================
# 3) Load prices / Open / liq / sector / top30 / VNINDEX dates / ETF
# ==============================================================================
print("\n[3/8] Loading prices, Open, liquidity, sector, top30, ETF...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_f.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

# Real E1VFVN30 prices (2016-01-07 onwards). For 2014-2015 we have no real ETF;
# fall back to VNINDEX-proxy so the ETF leg can still run (matches what the
# prior 12y test_v11_12y_t1open.py did; effect identical across both arms).
etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
etf_real["time"] = pd.to_datetime(etf_real["time"])
vn30_underlying = dict(zip(vni["time"], vni["Close"]))   # baseline: VNINDEX everywhere
for t, p in zip(etf_real["time"], etf_real["Close"]):
    vn30_underlying[t] = p                                # overlay real E1VFVN30 where available
print(f"  ETF underlying: real E1VFVN30 {len(etf_real):,} days; "
      f"VNINDEX proxy for pre-{etf_real['time'].min().date()}")

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_ff = {}; last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
print(f"  Trading days: {len(vni_dates)}; top30 size: {len(top30)}")

# ==============================================================================
# 4) Run BOTH arms (BASELINE + HEUR_N100) — same code path, only weights differ
# ==============================================================================
def run_arm(arm_label, weights):
    print(f"\n[RUN] arm={arm_label}  weights={weights}")
    events_bal, etf_bal_log = [], []
    nav_b, _trades_b = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=weights, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_bal, etf_log=etf_bal_log,
        force_close_eod=False,
        **LIQ_FULL, name=f"{arm_label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    events_v30, etf_v30_log = [], []
    nav_v, _trades_v = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=weights, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_v30, etf_log=etf_v30_log,
        force_close_eod=False,
        **LIQ_V30, name=f"{arm_label}_VN30")

    # Combine BAL + VN30 NAVs
    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time")
    nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    nav_combined = (nb.loc[common, "nav"] + nv.loc[common, "nav"]).rename("nav").reset_index()
    nav_combined.columns = ["time", "nav"]

    # Per-book breakdown for inspection
    combined_logs = pd.DataFrame({
        "ymd": common,
        "nav": (nb.loc[common,"nav"] + nv.loc[common,"nav"]).values,
        "BAL_cash":   nb.loc[common,"cash"].values,
        "BAL_stocks": (nb.loc[common,"positions_mv"] + nb.loc[common,"pending_mv"]).values,
        "BAL_etf":    nb.loc[common,"cash_etf"].values,
        "VN30_cash":   nv.loc[common,"cash"].values,
        "VN30_stocks": (nv.loc[common,"positions_mv"] + nv.loc[common,"pending_mv"]).values,
        "VN30_etf":    nv.loc[common,"cash_etf"].values,
        "n_pos":       (nb.loc[common,"n_pos"] + nv.loc[common,"n_pos"]).values,
        "state":       pd.Series(common).map(state_ff).values,
    })

    # Transactions
    def df_events(evs, book):
        if not evs: return pd.DataFrame()
        df = pd.DataFrame(evs); df["book"] = book; return df
    tx_stock = pd.concat([df_events(events_bal,"BAL"), df_events(events_v30,"VN30")],
                        ignore_index=True)
    etf_all = pd.concat([df_events(etf_bal_log,"BAL"), df_events(etf_v30_log,"VN30")],
                        ignore_index=True)
    if not etf_all.empty:
        etf_tx = pd.DataFrame({
            "ymd": pd.to_datetime(etf_all["ymd"]),
            "ticker": "E1VFVN30",
            "action": etf_all["action"].apply(lambda a: "buy" if a=="buy_etf" else "sell"),
            "buy_amount":  np.where(etf_all["action"]=="buy_etf",  etf_all["amount_vnd"], 0.0),
            "sell_amount": np.where(etf_all["action"]=="sell_etf", etf_all["amount_vnd"], 0.0),
            "fee": etf_all["friction_cost"], "adj_price": etf_all["price_vn30"],
            "shares": etf_all["shares"], "holding_id": etf_all["holding_id"],
            "play_type": "ETF_PARK", "cash_after": etf_all["cash_after"],
            "reason": "ETF_REBAL_state"+etf_all["state"].astype(str),
            "book": etf_all["book"],
        })
    else:
        etf_tx = pd.DataFrame()
    if not tx_stock.empty:
        tx_stock["ymd"] = pd.to_datetime(tx_stock["ymd"])
    all_tx = pd.concat([tx_stock, etf_tx], ignore_index=True)
    if not all_tx.empty:
        all_tx["ymd"] = pd.to_datetime(all_tx["ymd"])
        all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

    # Open positions snapshot
    open_b = nav_b.attrs.get("open_positions_final") if hasattr(nav_b,"attrs") else None
    open_v = nav_v.attrs.get("open_positions_final") if hasattr(nav_v,"attrs") else None
    open_df = pd.concat([
        open_b.assign(book="BAL") if open_b is not None and not open_b.empty else pd.DataFrame(),
        open_v.assign(book="VN30") if open_v is not None and not open_v.empty else pd.DataFrame(),
    ], ignore_index=True)

    # Save
    combined_logs.to_csv(os.path.join(OUTDIR, f"{arm_label}_logs.csv"), index=False)
    all_tx.to_csv(os.path.join(OUTDIR, f"{arm_label}_transactions.csv"), index=False)
    open_df.to_csv(os.path.join(OUTDIR, f"{arm_label}_open_positions.csv"), index=False)

    return nav_combined.set_index("time")["nav"], all_tx, open_df


print("\n[4/8] Running BASELINE arm (current heuristic state weights)...")
nav_base, tx_base, open_base = run_arm("baseline", W_BASELINE)
print(f"  baseline: end NAV {nav_base.iloc[-1]/1e9:.2f}B  trades {len(tx_base):,}")

print("\n[5/8] Running HEUR_N100 arm (NEUTRAL 70%->100%)...")
nav_n100, tx_n100, open_n100 = run_arm("heur_n100", W_HEUR_N100)
print(f"  heur_n100: end NAV {nav_n100.iloc[-1]/1e9:.2f}B  trades {len(tx_n100):,}")

# ==============================================================================
# 6) Window metrics — full / pre-OOS / OOS + per-year (2022,2024,2025,2026)
# ==============================================================================
def window_metrics(nav, name):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    if yrs <= 0 or len(rets) == 0:
        return {"name":name,"cagr_pct":0,"sharpe":0,"max_dd_pct":0,"calmar":0,
                "dd_dur_days":0,"final_nav_bn":nav.iloc[-1]/1e9,"wealth_x":1.0,
                "n_trades":0}
    spy = len(rets) / yrs
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    peak = nav.cummax()
    dd = (nav - peak)/peak
    max_dd = dd.min()
    # DD duration: longest stretch nav < peak
    underwater = (nav < peak)
    grp = (underwater != underwater.shift()).cumsum()
    dd_dur = 0
    if underwater.any():
        for _, sub in nav[underwater].groupby(grp[underwater]):
            dur = (sub.index[-1] - sub.index[0]).days
            if dur > dd_dur: dd_dur = dur
    cal = cagr / abs(max_dd) if max_dd < 0 else 0
    return {"name":name, "cagr_pct":cagr*100, "sharpe":sh,
            "max_dd_pct":max_dd*100, "calmar":cal, "dd_dur_days":dd_dur,
            "final_nav_bn":nav.iloc[-1]/1e9, "wealth_x":nav.iloc[-1]/nav.iloc[0]}


def count_trades(tx, ps, pe):
    if tx.empty: return 0
    real = tx[tx["reason"].astype(str) != "MTM_UNREALIZED"]
    real = real[(real["ymd"] >= pd.Timestamp(ps)) & (real["ymd"] <= pd.Timestamp(pe))]
    return len(real)


print("\n[6/8] Computing window metrics...")
rows = []
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub_b = nav_base[(nav_base.index >= ps_ts) & (nav_base.index <= pe_ts)]
    sub_n = nav_n100[(nav_n100.index >= ps_ts) & (nav_n100.index <= pe_ts)]
    if len(sub_b) < 30 or len(sub_n) < 30:
        continue
    mB = window_metrics(sub_b, f"{label} baseline")
    mN = window_metrics(sub_n, f"{label} heur_n100")
    mB["n_trades"] = count_trades(tx_base, ps, pe)
    mN["n_trades"] = count_trades(tx_n100, ps, pe)
    rows.append({"period":label, "B":mB, "N":mN})

# Pretty print
print("\n" + "="*100)
print("  KELLY Q2 RESULTS — full BA v11 stack, 12y, 50B NAV")
print("="*100)
print(f"\n{'Period':<22} {'Arm':<10} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} "
      f"{'Calmar':>7} {'DDdur':>6} {'NAV_B':>8} {'Trades':>7}")
print("-"*100)
for r in rows:
    p = r["period"]; B = r["B"]; N = r["N"]
    print(f"{p:<22} {'BASELINE':<10} {B['cagr_pct']:>+7.2f}% {B['sharpe']:>+7.2f} "
          f"{B['max_dd_pct']:>+7.2f}% {B['calmar']:>+7.2f} {B['dd_dur_days']:>6d} "
          f"{B['final_nav_bn']:>+7.2f}B {B['n_trades']:>7d}")
    print(f"{'':<22} {'HEUR_N100':<10} {N['cagr_pct']:>+7.2f}% {N['sharpe']:>+7.2f} "
          f"{N['max_dd_pct']:>+7.2f}% {N['calmar']:>+7.2f} {N['dd_dur_days']:>6d} "
          f"{N['final_nav_bn']:>+7.2f}B {N['n_trades']:>7d}")
    dC = N['cagr_pct'] - B['cagr_pct']; dS = N['sharpe'] - B['sharpe']
    dD = N['max_dd_pct'] - B['max_dd_pct']; dCal = N['calmar'] - B['calmar']
    print(f"{'':<22} {'Δ N100-B':<10} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp "
          f"{dCal:>+7.2f}")
    print()

# ==============================================================================
# 7) Verdict per spec: OOS 2024-2026 needs ΔCAGR>=+1.0pp AND ΔMaxDD<=+3pp
# ==============================================================================
oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
verdict = "RED"; verdict_reason = ""
if oos is not None:
    dC = oos["N"]["cagr_pct"] - oos["B"]["cagr_pct"]
    dD = oos["N"]["max_dd_pct"] - oos["B"]["max_dd_pct"]  # negative = worse DD
    # MaxDD is negative; "worse" = more negative, so Δ<0 means worse.
    # Spec says "≤ +3 pp MaxDD"; interpret as DD allowed to worsen by max 3pp.
    if dC >= 1.0 and dD >= -3.0:
        verdict = "GREEN"
        verdict_reason = f"ΔCAGR={dC:+.2f}pp ≥ +1.0pp AND ΔMaxDD={dD:+.2f}pp ≥ -3.0pp"
    elif dC >= 0.5 or (dC >= 0 and dD >= -1.0):
        verdict = "YELLOW"
        verdict_reason = f"ΔCAGR={dC:+.2f}pp / ΔMaxDD={dD:+.2f}pp — marginal"
    else:
        verdict = "RED"
        verdict_reason = f"ΔCAGR={dC:+.2f}pp / ΔMaxDD={dD:+.2f}pp — fails gate"

print("\n" + "="*100)
print(f"  VERDICT (OOS 2024-2026 gate): {verdict}")
print(f"  Reason: {verdict_reason}")
print("="*100)

# ==============================================================================
# 8) Write results markdown
# ==============================================================================
print("\n[8/8] Writing kelly_q2_heur_n100_results.md...")

md = []
md.append("# Kelly Q2 — HEUR_N100 vs BASELINE Shadow Backtest Results\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full (SV_TIGHT + P3 + D1 RE_BACKLOG_BUY + 50/50 BAL+VN30 + V6 ETF)")
md.append(f"**Period**: {START_DATE} → {END_DATE}")
md.append(f"**Init NAV**: {TOTAL_NAV/1e9:.0f}B (25B BAL + 25B VN30)")
md.append(f"**Exec**: T+1 Open + Layer 3 v4 HYBRID intraday | slot12 (max_pos=12, 10% fixed)")
md.append(f"**Costs**: TC=0.1% buy/sell, deposit=0%, borrow=0%, ETF friction=0.15%/side")
md.append(f"**ETF underlying**: real E1VFVN30 from 2016-01-07; VNINDEX-proxy 2014-2015 (same in both arms)\n")
md.append("## Variants compared\n")
md.append(f"- **BASELINE** (current heuristic): `cash_etf_states = {W_BASELINE}`")
md.append(f"- **HEUR_N100** (proposed): `cash_etf_states = {W_HEUR_N100}` — NEUTRAL goes 70% → 100%\n")

md.append("## Verdict\n")
md.append(f"### **{verdict}** — {verdict_reason}\n")
md.append("Gate (per spec §1.5 / §4.1): OOS 2024-2026 ΔCAGR ≥ +1.0pp AND ΔMaxDD ≤ +3pp vs BASELINE.\n")

md.append("## Results — all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | DDdur | NAV (B) | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]; B = r["B"]; N = r["N"]
    md.append(f"| **{p}** | BASELINE | {B['cagr_pct']:+.2f}% | {B['sharpe']:+.2f} | "
              f"{B['max_dd_pct']:+.2f}% | {B['calmar']:+.2f} | {B['dd_dur_days']} | "
              f"{B['final_nav_bn']:+.2f} | {B['n_trades']} |")
    md.append(f"|        | HEUR_N100 | {N['cagr_pct']:+.2f}% | {N['sharpe']:+.2f} | "
              f"{N['max_dd_pct']:+.2f}% | {N['calmar']:+.2f} | {N['dd_dur_days']} | "
              f"{N['final_nav_bn']:+.2f} | {N['n_trades']} |")
    dC = N['cagr_pct']-B['cagr_pct']; dS = N['sharpe']-B['sharpe']
    dD = N['max_dd_pct']-B['max_dd_pct']; dCal = N['calmar']-B['calmar']
    md.append(f"|        | **Δ N100−B** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
              f"**{dD:+.2f}pp** | **{dCal:+.2f}** | — | — | — |")

md.append("\n## Per-year breakdown\n")
md.append("(see same table above for Y2022/Y2024/Y2025/Y2026)\n")

md.append("\n## Files\n")
md.append("- `kelly_q2_out/baseline_logs.csv` / `_transactions.csv` / `_open_positions.csv`")
md.append("- `kelly_q2_out/heur_n100_logs.csv` / `_transactions.csv` / `_open_positions.csv`")

md.append("\n## Notes\n")
md.append("- Both arms run with identical signal stream, intraday alt-fill, sector caps,")
md.append("  liquidity gates, and ETF underlying — only the `cash_etf_states` dict differs.")
md.append("- Real E1VFVN30 prices used 2016-01-07 → end. Pre-2016 the ETF leg uses VNINDEX")
md.append("  proxy (identical effect on both arms, cancels in the diff).")
md.append("- 50/50 BAL + VN30 NAVs summed; per-book breakdown in the logs CSVs.")
md.append("- DDdur = longest underwater stretch in calendar days inside the window.")
md.append("- Verdict gate applied to OOS 2024-2026 window per spec §1.5 / §4.1.")

md_path = os.path.join(WORKDIR, "kelly_q2_heur_n100_results.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"  Wrote: {md_path}")

# Save numeric table
df_out = pd.DataFrame([{
    "period": r["period"],
    "baseline_cagr": r["B"]["cagr_pct"], "baseline_sharpe": r["B"]["sharpe"],
    "baseline_dd": r["B"]["max_dd_pct"], "baseline_calmar": r["B"]["calmar"],
    "baseline_nav_bn": r["B"]["final_nav_bn"], "baseline_trades": r["B"]["n_trades"],
    "n100_cagr": r["N"]["cagr_pct"], "n100_sharpe": r["N"]["sharpe"],
    "n100_dd": r["N"]["max_dd_pct"], "n100_calmar": r["N"]["calmar"],
    "n100_nav_bn": r["N"]["final_nav_bn"], "n100_trades": r["N"]["n_trades"],
    "delta_cagr_pp": r["N"]["cagr_pct"]-r["B"]["cagr_pct"],
    "delta_sharpe": r["N"]["sharpe"]-r["B"]["sharpe"],
    "delta_dd_pp": r["N"]["max_dd_pct"]-r["B"]["max_dd_pct"],
    "delta_calmar": r["N"]["calmar"]-r["B"]["calmar"],
} for r in rows])
df_out.to_csv(os.path.join(OUTDIR, "kelly_q2_summary.csv"), index=False)
print(f"  Wrote: {os.path.join(OUTDIR, 'kelly_q2_summary.csv')}")

print("\nDONE.")
