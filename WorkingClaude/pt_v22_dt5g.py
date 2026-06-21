# -*- coding: utf-8 -*-
"""pt_v22_dt5g.py — V2.2 paper-trade: BAL 25B | LAG 25B (static, no switching)
+ ETF parking {3:0.7} on BOTH books + committed CAPIT sleeve per playbook v2.
Fresh 50B from START_DATE (created 2026-06-10; START 2026-06-11 = pure forward,
zero hindsight sessions). Runs alongside pt_v4_dt5g.py — the OOS showdown that
decides whether real capital rotates from V4 (switched) to V2.2 (static).

V2.2 = the faithful champion (2026-06-10 research):
  faithful 2014->now: 25.48% CAGR / MaxDD -20.6% / Sharpe 1.63 / Calmar 1.24
  (vs V4 faithful 14.20%/Sh1.10 — the ensemble switch never survived a real ledger)

Architecture (both books REAL single ledgers via simulate()):
  BOOK A — BAL 25B   : BA-v11 stack (SIGNAL_V11 + SV_TIGHT + overheat + D1 +
                       regime_size), tier 10%/name, max 12, hold 45d, stop -20%,
                       DT5G parking {3:0.7} in E1VFVN30, v4-HYBRID fills.
  BOOK B — LAG 25B   : earnings-surprise schedule (NP_R>=15 & prior_n_good>=4 &
                       pa_HL3>=5), T+5 entry, 25td hold, 10%/8% S2 sizing, NO stop,
                       ALWAYS ON (no ensemble switch) + parking {3:0.7} (the +2pp
                       DD-neutral fix vs prodspec LAG which never parked).
  CAPIT sleeves      : playbook v2 (crisis_playbook.md §0b/§1, chot 2026-06-10):
                       gate = oversold breadth >= 30%; base 1.0 CRISIS / 0.75
                       NEUTRAL / 0.5 BULL / BEAR 0.5 only if (dd52w > -25% or VIX
                       cooling) else 0; grind x0.5; committed VND = size x book's
                       own free cash; hold 60td, stop-exempt, slot-exempt.
                       (Margin valve = MANUAL decision per playbook §1 — not here.)

DEPLOY UPGRADE 2026-06-13 (audit-validated, walk-forward PASS — see [[v23_audit_2014_now_deliverable]]
+ [[audited_versions_tally_2026]]):
  + POSTBULL GATE on CAPIT: hard-block (size 0) any washout in a post-strong-prolonged-bull +
    shallow-decline setup (VNINDEX trailing-2yr return >= 60% AND dd-from-1yr-peak > -15%).
    Avoids falling-knife capitulation buys (2007/2018/2022 signature). Faithful audit: lifts
    V2.3A 21.94% -> 24.04% CAGR AND MaxDD -23.7% -> -20.6%.
  + EDGE-CONDITIONAL ALLOCATOR: tilt LAG->0.65 in NEUTRAL/BULL/EXBULL ONLY when LAG edge-health
    mean12 (data/lag_edge_health.csv, trailing-12M LAG post-return) >= 4%; else hold 0.50.
    Avoids over-weighting LAG in its edge-cycle trough. Faithful: 24.04% -> 24.64% CAGR, Sh 1.79->1.82.
  Combined deploy V2.3A+postbull+edge = 24.64% / Sharpe 1.82 / MaxDD -20.6% / Calmar 1.22 (BQ-auditable,
  T+1 Open, FULL 2014-now). Min-DD alt = drop allocator (V2.3C+postbull = 23.35% / DD -19.0% / Cal 1.23).
  + STRICT ETF LIQUIDITY CAP (user 2026-06-13): E1VFVN30 parking capped at 20% of its 60d secondary ADV/
    day (multi-day fill) — the prior uncapped parking over-deployed at scale. With strict cap: 23.68% /
    Sh 1.96 / MaxDD -17.2% / Calmar 1.37 (LESS VN30 beta -> better risk-adjusted, ~1pp less CAGR). At
    AUM beyond secondary-ETF capacity, migrate parking to a self-managed VN30 basket (primary-creation eqv).

5-state source: tav2_bq.vnindex_5state_dt5g_live (DT5G gated live)
Outputs (analyze_portfolio.py compatible):
  data/pt_v22_dt5g_logs.csv / _transactions.csv / _open_positions.csv / _report.md
"""
import os, sys, io, pickle, bisect
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date

START_DATE = "2026-06-11"     # pure forward (track created 2026-06-10)
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
END_DATE = detect_end_date()
TOTAL_NAV = float(os.environ.get("NAV_TOTAL_B", "50")) * 1e9   # current account NAV (env-driven for live)
BAL_NAV   = TOTAL_NAV / 2
LAG_NAV   = TOTAL_NAV / 2
# Park-BULL trigger (user 2026-06-17): switch custom30 into BULL parking (state 4 @0.7) when the
# CURRENT NAV reaches 150B, REGARDLESS of starting NAV (dynamic per-run check — each daily live run
# reads the current account NAV). Below 150B, idle cash in BULL is dry-powder (measured @50B: bull-park
# 0.7 = -1.7pp CAGR / Sharpe 1.84->1.61 / worse DD = you ride the index basket down through post-bull
# corrections); at >=150B the books are capacity-constrained so parking deploys trapped idle (+1.1-1.4pp,
# audited). NEUTRAL parking (state 3 @0.7) is always on. EX-BULL (state 5) never parked.
PARK_DICT = {3: 0.7, 4: 0.7} if TOTAL_NAV >= 150e9 else {3: 0.7}
# Conditional BULL-PARK (mechanism test item 21, wired LIVE 2026-06-20; default OFF = byte-identical).
# When BULL_PARK_COND=1: bull deployment becomes breadth-gated + extension-tapered (deploy custom30V in
# BULL/EXBULL ONLY when breadth broad >= thr, soft-taper as index stretches above MA200) — REPLACES the
# static PARK_DICT bull entry with the conditional one. Robust but MARGINAL (+0.49pp CAGR / -0.03 Sharpe
# @50B vs NEUTRAL-only). OFF by default -> static PARK_DICT. Re-measure live conditional-vs-neutral next bull.
BULL_PARK_COND    = os.environ.get("BULL_PARK_COND", "0") == "1"
BULL_PARK_BREADTH = float(os.environ.get("BULL_PARK_BREADTH", "0.60"))
BULL_PARK_FRAC    = float(os.environ.get("BULL_PARK_FRAC", "0.70"))
BULL_PARK_EXT_LO  = float(os.environ.get("BULL_PARK_EXT_LO", "0.10"))
BULL_PARK_EXT_HI  = float(os.environ.get("BULL_PARK_EXT_HI", "0.30"))
POSITION_VND = 1.25e9
FILL_CAP = 0.20
T1_TOP_ADV = 50e9
INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                 "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
MAX_POS_V11 = 12

# === State-conditional LAG/BAL capital allocator (2026-06-11, deep-dive Finding #3) ===
# Faithful two-book validation: FULL 24.8->26.1% CAGR, MaxDD -20.5->-18.6, Sharpe 1.62->1.79,
# 2025+ 13.7->16.1%. Rationale: LAG (PEAD) >> BAL (momentum) risk-adjusted in every state
# EXCEPT BEAR, where LAG LOSES money (-14%/yr; good earnings get sold) -> BEAR weight = 0.
# Applied as a rebalancing overlay on the two real ledgers (rebalance only at DT5G state
# transitions; capital sizing approximation noted -> books still simulated at 25B ref each).
# w=0.65 good-states (user decision 2026-06-11): LAG edge-trough is CYCLICAL not structural —
# 5/5 prior troughs (mean12M<+1.5%) recovered to >=+3.9% within 6M; deepest (2020 COVID −4.4%)
# was followed by the strongest edge ever (+16-18%). PEAD is fundamentals-anchored (earnings
# yield doesn't die), unlike momentum (IC flipped 2025-26). Faithful physical check at
# BAL17.5B/LAG32.5B+bear-drop: FULL 26.58%/Sh1.68 (+0.8pp vs champion) at −1.6pp full-DD cost.
USE_LAG_ALLOCATOR = True
STATE_LAG_WEIGHT  = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}  # w_LAG by DT5G state (1..5)
ALLOC_REBAL_TC    = 0.001   # friction charged on capital moved at a rebalance
# BAND-only trigger (user 2026-06-11): rebalance ONLY when |current w_LAG - state target| > band —
# NOT at every state change. Lets the winner run (LAG drifts to 75% in good states before a
# disciplined trim) while BEAR (tgt 0) / CRISIS (tgt .50) entries still exceed the band -> protection
# fires. Backtest vs snap-at-state-change: FULL 26.29%/DD-18.3/Cal1.43/2025+ 16.43% with 32 rebal/12y
# (snap: 26.32%/-18.7/1.41/16.18%, 49 rebal) — band wins DD/Calmar/recent with 35% fewer rebalances.
# ±15pp too loose (CRISIS 65->50 = exactly 15pp sits on the edge, de-risk often skipped -> worse).
ALLOC_REBAL_BAND  = 0.10

# CAPIT playbook v2 constants (v2.1 2026-06-10: BEAR guard uses DOMESTIC vol-cooling,
# not VIX — user: VIX is a US thermometer, VN decoupling episodes + domestic shocks
# make it unreliable as a decision threshold; VN rv10-cooling reproduced the key
# separations AND fixed VIX's 2022-04-20 error. VIX = advisory only.)
WASHOUT_GATE = 0.30
CAPIT_HOLD   = 60
def capit_base(state, dd52w, vn_cooling):
    if state == 1: return 1.0
    if state == 3: return 0.75
    if state in (4, 5): return 0.5
    if state == 2: return 0.5 if (dd52w > -25 or vn_cooling) else 0.0
    return 0.5

print("=" * 100)
print(f"  V2.3 = V2.2 (BAL | LAG static, parked) + CAPIT v2 — TRANSPARENT PAPER-TRADE")
print(f"  period={START_DATE} -> {END_DATE}   NAV={TOTAL_NAV/1e9:.0f}B (25B+25B)   state={STATE_TABLE}")
print(f"  LAG/BAL allocator={'ON '+str(STATE_LAG_WEIGHT) if USE_LAG_ALLOCATOR else 'OFF (static 50/50)'}")
print("=" * 100)


def _seed_empty_track(reason: str):
    os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
    seed_ts = pd.Timestamp(START_DATE)
    pd.DataFrame([{
        "ymd": seed_ts, "nav": TOTAL_NAV,
        "BAL_cash": BAL_NAV, "BAL_stocks": 0.0, "BAL_etf": 0.0,
        "SECOND_cash": LAG_NAV, "SECOND_stocks": 0.0, "SECOND_etf": 0.0,
        "cash": TOTAL_NAV, "cash_etf": 0.0, "stocks_mv": 0.0,
        "num_holdings": 0, "num_transactions": 0,
        "state": np.nan, "active_leg": "LAG_ALWAYS", "ens_signal": 0,
    }]).to_csv(os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv"), index=False)
    pd.DataFrame(columns=["ymd","ticker","action","buy_amount","sell_amount","fee",
                          "adj_price","shares","holding_id","play_type","cash_after",
                          "reason","book"]).to_csv(
        os.path.join(WORKDIR, "data", "pt_v22_dt5g_transactions.csv"), index=False)
    pd.DataFrame(columns=["ticker","holding_id","shares","book"]).to_csv(
        os.path.join(WORKDIR, "data", "pt_v22_dt5g_open_positions.csv"), index=False)
    with open(os.path.join(WORKDIR, "data", "pt_v22_dt5g_report.md"), "w", encoding="utf-8") as f:
        f.write("# pt_v22_dt5g — V2.3 = V2.2 (BAL | LAG static + park) + CAPIT v2 on DT5G\n\n")
        f.write(f"*Start*: {START_DATE} (fresh 50B)  |  *Status*: **seeded, awaiting data**\n\n{reason}\n\n")
        f.write(f"*Init NAV*: 50B  |  *Final NAV*: 50.0000B  |  *Total ret*: +0.00%  |  0 sessions elapsed\n")
    print(f"\n[SEED] {reason}")
    print(f"[SEED] Wrote 50B seed row for {START_DATE}. Track compounds once data >= {START_DATE} lands.")


if pd.Timestamp(END_DATE) < pd.Timestamp(START_DATE):
    _seed_empty_track(f"No trading data yet in window (latest BQ data = {END_DATE} < start {START_DATE}).")
    sys.exit(0)

# ============================================================================
# 1. Intraday cache for v4-HYBRID BUY fills (same execution realism as pt_v4)
# ============================================================================
print("\n[1] Building HYBRID alt-fill prices...")
alt_hybrid = {}
try:
    with open(INTRADAY_PKL, "rb") as f: intraday = pickle.load(f)
    adv_by_ticker = {}
    slot_price_atc, slot_vol_atc, slot_price_t1115, slot_vol_t1115 = {}, {}, {}, {}
    for tk, bars in intraday.items():
        if bars is None or bars.empty: continue
        b = bars.copy()
        b["time"] = pd.to_datetime(b["time"]); b["date_ts"] = b["time"].dt.normalize()
        b["hm"] = b["time"].dt.strftime("%H:%M"); b["close_vnd"] = b["close"].astype(float) * 1000.0
        b["vnd_traded"] = b["close_vnd"] * b["volume"].astype(float)
        adv_by_ticker[tk] = float(b.groupby("date_ts", sort=False)["vnd_traded"].sum().mean())
        for hm, pd_, vd_ in [("14:45", slot_price_atc, slot_vol_atc), ("11:15", slot_price_t1115, slot_vol_t1115)]:
            for _, row in b[b["hm"] == hm].iterrows():
                pd_.setdefault(tk, {})[row["date_ts"]] = float(row["close_vnd"])
                vd_.setdefault(tk, {})[row["date_ts"]] = float(row["vnd_traded"])
    for tk in set(slot_price_atc) | set(slot_price_t1115):
        is_top = adv_by_ticker.get(tk, 0) >= T1_TOP_ADV
        src_p = slot_price_atc.get(tk, {}) if is_top else slot_price_t1115.get(tk, {})
        src_v = slot_vol_atc.get(tk, {}) if is_top else slot_vol_t1115.get(tk, {})
        for d_ts, p in src_p.items():
            v = src_v.get(d_ts)
            if v is not None and v * FILL_CAP >= POSITION_VND:
                alt_hybrid.setdefault(tk, {})[d_ts] = p
except Exception as ex:
    print(f"  (intraday cache unavailable — fall back to T+1 Open fills: {ex})")

# ============================================================================
# 2. BA v11 signals + filters (identical layering to pt_v4_dt5g)
# ============================================================================
print("\n[2] Loading v11 signals + Release_Date + 5-state + overheat + D1...")
sig = bq(SIGNAL_V11.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  signals: {len(sig):,} rows")

# Releases must look back BEFORE the window start: SV_TIGHT needs days_since_release <= 60,
# so a fresh track starting mid-quarter would otherwise see no releases at all (NaN -> all
# buys dropped in states 1-3) and a zero-row result crashed the daily run (fixed 2026-06-12).
rel = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE_SUB(DATE '{START_DATE}', INTERVAL 120 DAY) AND DATE '{END_DATE}'""")
if rel.empty: rel = pd.DataFrame(columns=["ticker", "Release_Date"])
rel["Release_Date"] = pd.to_datetime(rel["Release_Date"])
rel_by_tk = rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds_arr = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = rel_by_tk.get(tk)
    if not arr: ds_arr[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    ds_arr[i] = np.nan if idx == 0 else (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds_arr

state_df = bq(f"""SELECT s.time, s.state FROM {STATE_TABLE} AS s WHERE s.time <= DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["overheat"] = (vni_full["Close"]/vni_full["MA200"] > 1.30) & \
                       ((vni_full["time"].map(state_by_date) == 5) | (vni_full["D_RSI"] > 0.75))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
sig["state"] = sig["time"].map(state_by_date)

# D1 RE_BACKLOG_BUY override (same as pt_v4)
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
  adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN {STATE_TABLE} AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
d1_q = d1.loc[d1_mask, ["ticker","time"]].assign(_d1_ok=True)
sig = sig.merge(d1_q, on=["ticker","time"], how="left")
omask = sig["_d1_ok"].fillna(False) & (sig["ta"] >= 120)
sig.loc[omask, "play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])

def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mb = sig["play_type"].isin(BUY_TIERS_V11)
mk = (~mb) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mk].copy()
mp3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mp3, "play_type"] = "AVOID_overheated"

# EXBULL momentum suppression (research 2026-06-12, GO-LIVE 2026-06-11 user-approved
# after edge-health showed mom_200 FLIPPED 12M): BAL momentum IC inverts in DT5G
# EX-BULL (pooled -0.31, 3/3 episodes negative: 2020/2021/2025); the overheat guard
# (VNINDEX>1.30xMA200) never fired in the Aug-Sep 2025 EX-BULL. Backtest on V2.3C:
# FULL 25.77->26.09%, 2025+ 18.30->19.85%/DD-17.4, BAL-leg MaxDD -25.4->-20.6.
EXB_MOM = {"MEGA", "MOMENTUM", "MOMENTUM_S", "MOMENTUM_QUALITY", "MOMENTUM_A", "S_PRO"}
mp4 = (sig_f["state"] == 5) & sig_f["play_type"].isin(EXB_MOM)
sig_f.loc[mp4, "play_type"] = "AVOID_exbull"
print(f"  [EXBULL fix] suppressed {int(mp4.sum())} momentum signals in EX-BULL (state==5)")

from regime_size_overlay import apply_regime_size
sig_f, RS = apply_regime_size(sig_f, START_DATE, END_DATE, bq, base_tiers=TIER_BAL)

# ============================================================================
# 3. Common data
# ============================================================================
print("\n[3] Loading prices/Open/sector/E1VFVN30...")
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

# PARKING VEHICLE (DEPLOY 2026-06-14, user): self-managed RULE-BASED liquid VN-equity basket
# ("custompitg") replaces E1VFVN30 as where NEUTRAL-state idle cash is parked. Rationale + audit in
# memory capacity-ceiling-custom-vn30-2026. Design principles (NO hardcoded exceptions):
#   universe  = ticker_prune ∩ ICB_Code IS NOT NULL  (real listed cos; indices/ETFs have NULL ICB -> out)
#   rebalance = first trading day on/after 05-Feb/05-May/05-Aug/05-Nov (post-earnings -> fresh gate)
#   members   = top-30 by PRIOR-completed-quarter AVG(Volume_3M_P50*Close)  (PIT, no look-ahead)
#   GATE      = only as-of 8L rating<=3 (investment-grade) may enter -> excludes manipulation/distress
#               (e.g. VIC is admitted ONLY when it earns rating<=3, i.e. 2014-18; gated out 2020+ incl
#               the 2025 VIC-led rally). 'ex-VIC' is a CONSEQUENCE of the rule, not a special case.
#   capacity  = 20% of the basket's own 60d-ADV (~100x E1VFVN30 secondary) -> ONE mechanism self-scales
#               across ALL NAV (no NAV threshold). Own the underlyings -> NO fund mgmt fee.
# Rollback: set env PARK_VEHICLE=etf to restore the legacy E1VFVN30 parking.
PARK_VEHICLE = os.environ.get("PARK_VEHICLE", "custompitg").lower()
ETF_LIQ_PCT = 0.20
if PARK_VEHICLE == "etf":
    etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
    etf_real["time"] = pd.to_datetime(etf_real["time"])
    vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))
    _adv = bq(f"""SELECT t.time, COALESCE(t.Price,t.Close)*t.Volume AS tv FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time >= DATE_SUB(DATE '{START_DATE}', INTERVAL 200 DAY)
  AND t.time <= DATE '{END_DATE}' ORDER BY t.time""")
    _adv["time"] = pd.to_datetime(_adv["time"]); _adv["adv"] = _adv["tv"].rolling(60, min_periods=20).mean()
    etf_adv_lookup = {t: float(v) for t, v in zip(_adv["time"], _adv["adv"]) if pd.notna(v)}
    PARK_TICKER = "E1VFVN30"
    _med = np.median(list(etf_adv_lookup.values())) if etf_adv_lookup else 0
    print(f"  [PARK etf] E1VFVN30 strict cap {ETF_LIQ_PCT:.0%} ADV; ~{_med*ETF_LIQ_PCT/1e9:.1f}B/day parkable")
else:
    import custom_basket as cb
    # custom30V (yield-combo selection) PAPER-GATE (2026-06-17): liquidity = GATE only, rank PURELY by
    # rank(1/PE)+rank(1/PCF). Validated +2.46pp full / +3.65 IS / +2.42 OOS @50B NEUTRAL-only, walk-forward
    # robust, audit 0 VND, per-year broad; financials-concentrated value sleeve (settled_decisions item 13).
    # Gated to GO-LIVE 2026-06-30 (same window as 8L v2): until then live keeps the liquidity basket
    # ("blend") and paper-diff tracks the swap; on/after go-live it switches to "yieldcombo". Env
    # BASKET_SELECT overrides the date gate (e.g. for backtests / forced cutover).
    CUSTOM30V_GOLIVE = "2026-06-30"
    if "BASKET_SELECT" not in os.environ:
        os.environ["BASKET_SELECT"] = "yieldcombo" if str(END_DATE) >= CUSTOM30V_GOLIVE else "blend"
    print(f"  [PARK select] BASKET_SELECT={os.environ['BASKET_SELECT']} (custom30V go-live {CUSTOM30V_GOLIVE}; yield-combo 1/PE+1/PCF, liq=gate)")
    vn30_underlying, etf_adv_lookup, _memdf, _ = cb.build_pit(
        bq, START_DATE, END_DATE, quality="none", rebal="q2m5", gate_rating=3,
        weight_scheme="namecap")   # 2026-06-15 review: cap each name <=10% (idiosyncratic risk);
        # sector weight left = market structure (VN30 also ~financials-heavy) — data-chosen (best CAGR
        # +1.27pp@500B & DD −17.9→−15.2 vs legacy cap-weight; sectorcap rejected: same idea, lower return).
    PARK_TICKER = "CUSTOM_VN30G"
    _lq = _memdf["rebal_date"].max()
    _cur = _memdf[_memdf["rebal_date"] == _lq].sort_values("liq_rank")
    _med = np.median(list(etf_adv_lookup.values())) if etf_adv_lookup else 0
    print(f"  [PARK custompitg/namecap10] rule-based basket: {_memdf['rebal_date'].nunique()} rebals, "
          f"~{_med*ETF_LIQ_PCT/1e9:.0f}B/day parkable. Current ({_lq}) {len(_cur)} holdings:")
    print("    " + ", ".join(_cur["ticker"].tolist()))
ETF_LIQ_KW = dict(etf_adv_lookup=etf_adv_lookup, etf_liquidity_pct=ETF_LIQ_PCT)

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

state_ff = {}; last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ============================================================================
# 4. LAGGED V12.1 schedule + panels (engine-run, always-on)
# ============================================================================
print("\n[4] Building LAGGED schedule + price panels...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open_l = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                    on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))
# --- LAG forensic gate (2026-06-20, validated lag_forensic_audit + A/B re-sim) ---
# Drop human-flagged related-party/fraud names from LAG (date-aware, no hindsight) so the momentum book
# never rides a confirmed fraud into its blow-up (PC1 arrest, L40 -12%, KSF -10%). Backtest-neutral
# (flags current) = pure forward insurance. NON-OP filter left OFF (env LAG_NONOP_FILTER=1 to enable):
# A/B showed +0.44pp CAGR but -2.2pp MaxDD / Calmar 0.83->0.77 (concentration eats the per-entry edge).
# Peak-earnings NOT filtered: LAG monetizes peak via drift (audit: peak median higher NEUTRAL/BULL/EXBULL).
_LAG_NONOP = os.environ.get("LAG_NONOP_FILTER", "0") == "1"
_LAG_FOR   = os.environ.get("LAG_FORENSIC_GATE", "1") == "1"
if _LAG_NONOP:
    _qm = bq("SELECT f.ticker,f.quarter,f.NPM_P0,f.EBITM_P0 FROM tav2_bq.ticker_financial f WHERE f.quarter IS NOT NULL")
    ev = ev.merge(_qm, on=["ticker","quarter"], how="left")
    ev["_nonop"] = (ev["NPM_P0"] > 1.2 * ev["EBITM_P0"]) & ev["EBITM_P0"].notna()
else:
    ev["_nonop"] = False
_forx = {}
try:
    _ff = pd.read_csv("data/forensic_flags.csv")
    _forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows() if str(r["severity"]).strip() == "exclude"}
except Exception: pass
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]
_m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
if _LAG_NONOP: _m &= ~ev["_nonop"]
if _LAG_FOR:   _m &= ~ev["_forbid"]
e_hl3 = ev[_m].copy()
print(f"  [LAG gate] forensic={_LAG_FOR} non_op={_LAG_NONOP} -> {len(e_hl3)} entries "
      f"(forensic-excluded {int(ev['_forbid'].sum())})")

sw, ewd = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
def offset_date(ref, off):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(all_dates[tgt]) if 0 <= tgt < len(all_dates) else None

lag_rows = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]
    entry = offset_date(row["Release_Date"], 5)
    if entry is None or entry < sw or entry > ewd: continue
    sd = offset_date(entry, -1)            # engine buys T+1 Open => signal the session before entry
    if sd is None or tk not in px_close.columns: continue
    px_sd = px_close.at[sd, tk] if sd in px_close.index else np.nan
    if pd.isna(px_sd) or px_sd <= 0: continue
    lag_rows.append({"time": sd, "ticker": tk,
                     "play_type": "LAG_HI" if row["surprise_B_MA"] > 0.5 else "LAG_LO",
                     "ta": 400.0, "Close": float(px_sd)})
sig_lag = pd.DataFrame(lag_rows, columns=["time","ticker","play_type","ta","Close"])
print(f"  LAG signals in window: {len(sig_lag)}")
shn.TIER_PRIORITY.update({"LAG_HI": 88, "LAG_LO": 82})
LAG_TW = {"LAG_HI": 0.10, "LAG_LO": 0.08}

# LAG book price/open/liq lookups (hole-free pkl panels, window only)
win_idx = [d for d in master_idx if sw <= d <= ewd]
prices_lag = {tk: {d: float(px_close.at[d, tk]) for d in win_idx
                   if pd.notna(px_close.at[d, tk])} for tk in px_close.columns}
opens_lag = {tk: {d: float(px_open_l.at[d, tk]) for d in win_idx
                  if tk in px_open_l.columns and pd.notna(px_open_l.at[d, tk])} for tk in px_close.columns}
liq_lag = {}
for tk in liq_l.columns:
    for d in win_idx:
        adv = liq_l.at[d, tk]; px = px_close.at[d, tk] if tk in px_close.columns else np.nan
        if pd.notna(adv) and pd.notna(px):
            liq_lag[(tk, d)] = float(adv) * float(px)
LIQ_LAG = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_lag, "exit_slippage_tiered": True}

# ============================================================================
# 5. CAPIT v2 events (gate 30%, state routing, BEAR guard) + baskets
# ============================================================================
print("\n[5] CAPIT v2 washout events...")
br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
# dd52w needs 260d history; postbull gate needs 504-session (2yr) lookback for ret2y
vni_hist = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time >= DATE_SUB(DATE '{START_DATE}', INTERVAL 1100 DAY)
  AND t.time <= DATE '{END_DATE}' ORDER BY t.time""")
vni_hist["time"] = pd.to_datetime(vni_hist["time"])
vni_hist = vni_hist.set_index("time")
vni_hist["dd52"] = (vni_hist["Close"] / vni_hist["Close"].rolling(252, min_periods=60).max() - 1) * 100
vni_hist["ret2y"] = vni_hist["Close"] / vni_hist["Close"].shift(504) - 1   # trailing 2yr (postbull gate)
def postbull_block(d0):
    """user 2026-06-13 (walk-forward + generalize 2007/2018): DON'T buy a washout that fires right after
    a strong PROLONGED bull while the decline is still shallow (mean-reversion pending). Block (size 0)
    if trailing-2yr VNINDEX return >= 60% AND decline-from-1yr-peak still shallow (> -15%)."""
    r = vni_hist["ret2y"].reindex([d0], method="ffill"); dd = vni_hist["dd52"].reindex([d0], method="ffill")
    r2 = float(r.iloc[0]) if len(r) and pd.notna(r.iloc[0]) else np.nan
    d1 = float(dd.iloc[0]) if len(dd) and pd.notna(dd.iloc[0]) else np.nan
    if np.isnan(r2) or np.isnan(d1): return False
    return (r2 >= 0.60) and (d1 > -15.0)
# DOMESTIC shock thermometer: VNINDEX 10d realized vol, "cooled" = >=15% off its 30d peak
_r = vni_hist["Close"].pct_change()
vni_hist["rv10"] = _r.rolling(10).std() * np.sqrt(252) * 100
vni_hist["vn_cooling"] = vni_hist["rv10"] <= vni_hist["rv10"].rolling(30).max() * 0.85
def vn_cool_at(d):
    s = vni_hist["vn_cooling"].reindex([d], method="ffill")
    return bool(s.iloc[0]) if len(s) and pd.notna(s.iloc[0]) else False

ws = br[br["oversold"] >= WASHOUT_GATE].copy().sort_values("time")
capit_events = []
if len(ws):
    ws["g"] = ws["time"].diff().dt.days.fillna(999)
    ws["c"] = (ws["g"] >= 30).cumsum()
    for _, grp in ws.groupby("c"):
        d0 = grp.iloc[0]["time"]
        st = int(state_ff.get(d0) or state_by_date.get(d0, 3) or 3)
        # ex-ante grind: prior washout day 20..90 sessions before d0 (within window history)
        di = {dd: i for i, dd in enumerate(vni_dates)}
        i0 = di.get(d0, None)
        grind = False
        if i0 is not None:
            wdays = set(br[br["oversold"] >= WASHOUT_GATE]["time"])
            for back in range(20, 91):
                j = i0 - back
                if j >= 0 and vni_dates[j] in wdays: grind = True; break
        dd_now = float(vni_hist["dd52"].reindex([d0], method="ffill").iloc[0]) if len(vni_hist) else -99.0
        base = capit_base(st, dd_now, vn_cool_at(d0))
        size = base * (0.5 if grind else 1.0)
        # postbull gate (DEPLOY 2026-06-13): hard-block washouts in a post-strong-bull, shallow-decline setup
        if postbull_block(d0):
            _r2 = float(vni_hist["ret2y"].reindex([d0], method="ffill").iloc[0])
            print(f"  [postbull] {d0.date()} ret2y={_r2*100:+.0f}% dd1y={dd_now:.0f}% -> post-strong-bull+shallow -> BLOCKED (size 0)")
            size = 0.0
        capit_events.append({"date": d0, "state": st, "grind": grind, "size": size, "dd": dd_now})
        print(f"  washout {d0.date()}: state={st} grind={grind} dd52={dd_now:.1f}% vn_cool={vn_cool_at(d0)} -> size={size:.2f}")
if not capit_events:
    print("  (no washout events in window yet — sleeves dormant)")

# ============================================================================
# C — GATED-OVERFLOW (settled_decisions item 15, wired LIVE 2026-06-18). In a SAFE bear washout (state 2,
# not-postbull) where the golden basket is thin (deal-scarcity -> capit capital would otherwise sit at 0%
# since BEAR isn't parked), AUGMENT golden with liquid custom30V under ONE pb_z scale — BUT only when the
# washout is a MATURE capitulation (TWO HARD GATES): (G1) deep-dd: VNINDEX >=20% off 52w high AND breadth-
# broken (ew2d maturity) ; (G2) not-postbull. Walk-forward @20B: IS +0.00 (cannot hurt in-sample — no
# 2014-19 bear passes the deep-dd gate) / OOS +1.17pp -> robust insurance. Depth-sizing stays OFF (the
# non-robust half: IS -1.60 / OOS flat). PAPER-GATED to the same 2026-06-30 cutover as custom30V so they go
# live together; before then C is DORMANT (golden-only, byte-identical to prior production).
CAPIT_OVERFLOW_GOLIVE = "2026-06-30"
CAPIT_BEAR_OVERFLOW   = os.environ.get(
    "CAPIT_BEAR_OVERFLOW", "1" if str(END_DATE) >= CAPIT_OVERFLOW_GOLIVE else "0") == "1"
CAPIT_OVERFLOW_MIN    = int(os.environ.get("CAPIT_OVERFLOW_MIN", "8"))    # golden < this -> consider overflow
CAPIT_OVERFLOW_N      = int(os.environ.get("CAPIT_OVERFLOW_N", "15"))     # cap total names after overflow
CAPIT_OVERFLOW_DD     = float(os.environ.get("CAPIT_OVERFLOW_DD", "-20.0"))  # G1a: VNINDEX dd52w floor (deep)
CAPIT_OVERFLOW_MATURE = os.environ.get("CAPIT_OVERFLOW_MATURE", "1") == "1"  # G1b: require breadth-broken
EW2D_P25_THR = -20.0; EW2D_BREADTH_THR = 0.48   # mature = weak-half p25 dd <= -20% AND >=48% below MA200
print(f"  [C overflow] CAPIT_BEAR_OVERFLOW={CAPIT_BEAR_OVERFLOW} (go-live {CAPIT_OVERFLOW_GOLIVE}; "
      f"gates: dd52<={CAPIT_OVERFLOW_DD:.0f}% + breadth-broken + not-postbull; depth-sizing OFF)")
_c30v_iv = None
def _c30v_asof(d):
    """As-of members of the shadow custom30V basket (tav2_bq.custom30v_8l), point-in-time by effective dates."""
    global _c30v_iv
    if _c30v_iv is None:
        _v = bq("SELECT ticker, effective_from, effective_to FROM tav2_bq.custom30v_8l")
        _v["effective_from"] = pd.to_datetime(_v["effective_from"])
        _v["effective_to"]   = pd.to_datetime(_v["effective_to"]).fillna(pd.Timestamp("2100-01-01"))
        _c30v_iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in _v.groupby("ticker")}
    dd = np.datetime64(d)
    return [tk for tk, ivs in _c30v_iv.items() if any(f <= dd < t for f, t in ivs)]
_ew_cache = {}
def ew_mature(d0):
    """G1b breadth-broken: weak-half stock dd-from-52w-high <= EW2D_P25_THR AND >= EW2D_BREADTH_THR below
    MA200 (trend reverted to mean, not a fresh post-euphoria first leg). Causal 1y window on ticker_prune.
    Fail-safe: missing/thin data -> NOT mature (no overflow)."""
    if d0 in _ew_cache: return _ew_cache[d0]
    q = f"""
    WITH win AS (
      SELECT ticker, time, Close, MA200,
        MAX(Close) OVER (PARTITION BY ticker ORDER BY time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi52,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
      FROM tav2_bq.ticker_prune
      WHERE time BETWEEN DATE_SUB(DATE '{d0.date()}', INTERVAL 365 DAY) AND DATE '{d0.date()}')
    SELECT APPROX_QUANTILES(SAFE_DIVIDE(Close,hi52)-1,100)[OFFSET(25)] AS p25_dd,
           AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 1.0 ELSE 0 END) AS pct_below
    FROM win WHERE rn=1 AND Close>0 AND hi52>0"""
    r = bq(q)
    if r.empty or pd.isna(r["p25_dd"][0]) or pd.isna(r["pct_below"][0]):
        _ew_cache[d0] = False; return False
    p25 = float(r["p25_dd"][0]) * 100; below = float(r["pct_below"][0])
    out = (p25 <= EW2D_P25_THR) and (below >= EW2D_BREADTH_THR)
    _ew_cache[d0] = out; return out

def capit_basket(d):
    """Playbook §2 basket at signal date d (point-in-time BQ). Golden first; C-overflow augments with
    custom30V only when the two hard gates pass (see CAPIT_BEAR_OVERFLOW block above)."""
    e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    if e.empty: return []
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    golden = list(pick["ticker"])
    # C — gated-overflow: thin golden in a MATURE safe bear -> merge golden + custom30V under one pb_z scale
    if CAPIT_BEAR_OVERFLOW and len(golden) < CAPIT_OVERFLOW_MIN:
        st = int(state_ff.get(d) or state_by_date.get(d, 3) or 3)
        _ddx = float(vni_hist["dd52"].reindex([d], method="ffill").iloc[0]) if len(vni_hist) else 0.0
        _deep = _ddx <= CAPIT_OVERFLOW_DD
        _mature = ew_mature(d) if CAPIT_OVERFLOW_MATURE else True
        if st == 2 and (not postbull_block(d)) and _deep and _mature:
            vmems = _c30v_asof(d)
            if vmems:
                in_v = ",".join(f"'{t}'" for t in vmems)
                ev = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p WHERE p.time = DATE '{d.date()}' AND p.ticker IN ({in_v})""")
                ev = ev[ev["pbz"] < 0]                                   # liquid join only if genuinely cheap
                merged = pd.concat([pick[["ticker", "pbz"]], ev[["ticker", "pbz"]]]).drop_duplicates("ticker")
                merged = merged.nsmallest(CAPIT_OVERFLOW_N, "pbz")       # one unified pb_z scale
                golden = list(merged["ticker"])
                print(f"  [C-overflow] {d.date()} GATES PASS: dd52={_ddx:.0f}% (<= {CAPIT_OVERFLOW_DD:.0f}) "
                      f"mature=True postbull_ok=True -> golden+custom30V = {len(golden)} names")
    return golden

def add_capit_arm(sig_book, base_nav_df, tw_base, tag, book_prices):
    """Two-pass: size each event sleeve from the BASE run's free cash; returns (sig2, tw2, extra)."""
    rows, tw2, tiers = [], dict(tw_base), []
    if not capit_events:
        return sig_book, tw2, {}
    basecash = (base_nav_df.set_index("time")["cash_pct"] / 100.0).clip(lower=0)
    for i, e in enumerate(capit_events):
        if e["size"] <= 0.005: continue
        d = e["date"]
        names = [t for t in capit_basket(d) if t in book_prices and d in book_prices[t]]
        if len(names) < 3: continue
        pos = basecash.index.searchsorted(d)
        cf = float(basecash.iloc[max(0, pos-2):pos+1].mean()) if len(basecash) else 0.0
        wt = e["size"] * max(cf, 0.0)
        if wt <= 0.005: continue
        pt = f"CAPIT{tag}_E{i}"
        shn.TIER_PRIORITY[pt] = 95
        tw2[pt] = wt / len(names); tiers.append(pt)
        for t in names:
            rows.append({"time": d, "ticker": t, "play_type": pt, "ta": 500.0,
                         "Close": book_prices[t][d]})
    if not tiers:
        return sig_book, tw2, {}
    extra = dict(hold_days_by_tier={t: CAPIT_HOLD for t in tiers},
                 stop_exempt_tiers=set(tiers), slot_exempt_tiers=set(tiers),
                 tier_position_limit={t: 15 for t in tiers})
    return pd.concat([sig_book, pd.DataFrame(rows)], ignore_index=True), tw2, extra

def merge_extra(base_extra, cap_extra):
    if not cap_extra: return dict(base_extra)
    out = dict(base_extra)
    out["hold_days_by_tier"] = {**base_extra.get("hold_days_by_tier", {}), **cap_extra["hold_days_by_tier"]}
    out["stop_exempt_tiers"] = set(base_extra.get("stop_exempt_tiers", set())) | cap_extra["stop_exempt_tiers"]
    out["slot_exempt_tiers"] = cap_extra["slot_exempt_tiers"]
    out["tier_position_limit"] = {**base_extra.get("tier_position_limit", {}), **cap_extra["tier_position_limit"]}
    return out

# ============================================================================
# 6. BOOK A — BAL 25B (base pass for capit sizing, then final with capit)
# ============================================================================
print("\n[6] BOOK A — BAL 25B...")
# Conditional bull-park per-date parking override (None when OFF -> identical to static PARK_DICT)
BULL_PARK_BY_DATE = None
if BULL_PARK_COND:
    _bd = bq(f"""SELECT t.time, AVG(CASE WHEN t.MA200>0 AND t.Close<t.MA200 THEN 0.0 ELSE 1.0 END) AS bd
FROM tav2_bq.ticker_prune AS t WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.MA200>0
GROUP BY t.time""")
    _bd["time"] = pd.to_datetime(_bd["time"]); _breadth = _bd.set_index("time")["bd"].sort_index()
    _vf = vni_full.set_index("time"); _ext = (_vf["Close"] / _vf["MA200"] - 1.0).sort_index()
    _nbase = {s: f for s, f in PARK_DICT.items() if s == 3}   # neutral base; bull = conditional override
    BULL_PARK_BY_DATE = {}; _nfire = 0
    for d in vni_dates:
        base = dict(_nbase); st = int(state_ff.get(d) or 3)
        if st in (4, 5):
            _b = _breadth.reindex([d], method="ffill"); bb = float(_b.iloc[0]) if len(_b) and pd.notna(_b.iloc[0]) else 0.0
            if bb >= BULL_PARK_BREADTH:
                _e = _ext.reindex([d], method="ffill"); ee = float(_e.iloc[0]) if len(_e) and pd.notna(_e.iloc[0]) else 0.0
                taper = float(np.clip((BULL_PARK_EXT_HI - ee) / (BULL_PARK_EXT_HI - BULL_PARK_EXT_LO), 0.0, 1.0))
                frac = BULL_PARK_FRAC * taper
                if frac > 0.01: base[st] = frac; _nfire += 1
        BULL_PARK_BY_DATE[d] = base
    print(f"  [bull-park] CONDITIONAL ON breadth>={BULL_PARK_BREADTH} frac{BULL_PARK_FRAC} ext-taper[{BULL_PARK_EXT_LO},{BULL_PARK_EXT_HI}] -> {_nfire} bull-days deploy")
BAL_KW = dict(allowed_tiers=RS["allowed_tiers"], max_positions=MAX_POS_V11,
              hold_days=45, stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BAL_NAV,
              sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers=RS["sector_cap_exempt"],
              tier_weights_by_state=RS["tier_weights_by_state"],
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,
              cash_etf_states=PARK_DICT, cash_etf_states_by_date=BULL_PARK_BY_DATE, vn30_underlying=vn30_underlying,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=open_prices, t1_open_exec=True,
              entry_alt_prices=alt_hybrid or None, entry_fill_mode="v4_hybrid",
              force_close_eod=False, **ETF_LIQ_KW)
if capit_events:
    nav_bal0, _ = simulate(sig_f, prices, vni_dates, tier_weights=RS["tier_weights"],
                           name="pt_v22_BAL_base", **BAL_KW, **LIQ_FULL)
    nav_bal0["time"] = pd.to_datetime(nav_bal0["time"])
    sig_balC, tw_balC, ex_balC = add_capit_arm(sig_f, nav_bal0, RS["tier_weights"], "B", prices)
else:
    sig_balC, tw_balC, ex_balC = sig_f, RS["tier_weights"], {}
events_bal, etf_bal = [], []
kwA = dict(BAL_KW); kwA["allowed_tiers"] = list(RS["allowed_tiers"]) + [t for t in tw_balC if t.startswith("CAPIT")]
nav_bal, _ = simulate(sig_balC, prices, vni_dates, tier_weights=tw_balC,
                      event_log=events_bal, etf_log=etf_bal,
                      name="pt_v22_BAL", **merge_extra(kwA, ex_balC), **LIQ_FULL)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  BAL events: {len(events_bal)} stock + {len(etf_bal)} ETF; final {nav_bal.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 7. BOOK B — LAG 25B always-on + parking (base pass, then final with capit)
# ============================================================================
print("\n[7] BOOK B — LAG 25B (always-on, parked)...")
LAG_KW = dict(allowed_tiers=["LAG_HI","LAG_LO"], max_positions=12,
              hold_days=25, stop_loss=-0.99, min_hold=2, slippage=0.001, init_nav=LAG_NAV,
              stop_exempt_tiers={"LAG_HI","LAG_LO"},
              hold_days_by_tier={"LAG_HI": 25, "LAG_LO": 25},
              tier_position_limit={"LAG_HI": 12, "LAG_LO": 12},
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,
              cash_etf_states=PARK_DICT, cash_etf_states_by_date=BULL_PARK_BY_DATE, vn30_underlying=vn30_underlying,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=opens_lag, t1_open_exec=True, force_close_eod=False, **ETF_LIQ_KW)
if capit_events:
    nav_lag0, _ = simulate(sig_lag, prices_lag, vni_dates, tier_weights=LAG_TW,
                           name="pt_v22_LAG_base", **LAG_KW, **LIQ_LAG)
    nav_lag0["time"] = pd.to_datetime(nav_lag0["time"])
    sig_lagC, tw_lagC, ex_lagC = add_capit_arm(sig_lag, nav_lag0, LAG_TW, "L", prices_lag)
else:
    sig_lagC, tw_lagC, ex_lagC = sig_lag, dict(LAG_TW), {}
events_lag, etf_lag = [], []
kwB = dict(LAG_KW); kwB["allowed_tiers"] = ["LAG_HI","LAG_LO"] + [t for t in tw_lagC if t.startswith("CAPIT")]
nav_lag, _ = simulate(sig_lagC, prices_lag, vni_dates, tier_weights=tw_lagC,
                      event_log=events_lag, etf_log=etf_lag,
                      name="pt_v22_LAG", **merge_extra(kwB, ex_lagC), **LIQ_LAG)
nav_lag["time"] = pd.to_datetime(nav_lag["time"])
print(f"  LAG events: {len(events_lag)} stock + {len(etf_lag)} ETF; final {nav_lag.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 8. Combine + transparent logs (state-conditional LAG/BAL allocator overlay; BEAR -> LAG 0)
# ============================================================================
print("\n[8] Building combined logs...")
nb = nav_bal.set_index("time"); nl = nav_lag.set_index("time")
common = nb.index.intersection(nl.index)
navb_c = nb["nav"].loc[common]; navl_c = nl["nav"].loc[common]

if USE_LAG_ALLOCATOR and len(common) >= 1:
    # State-conditional capital allocation between BAL and LAG, BAND-only rebalance:
    # fire only when |current w_LAG - state target| > ALLOC_REBAL_BAND (not at every
    # state change). cap_b/cap_l = VND in each sleeve; combined_nav = cap_b + cap_l.
    states_c = [int(state_ff.get(d) or state_by_date.get(d, 3) or 3) for d in common]
    rb = navb_c.pct_change().fillna(0.0).values
    rl = navl_c.pct_change().fillna(0.0).values
    # EDGE-CONDITIONAL allocator (DEPLOY 2026-06-13, walk-forward validated): tilt LAG->0.65 in good
    # states (3/4/5) ONLY when LAG's causal edge-health mean12 (trailing-12M mean LAG trade post-return)
    # >= EDGE_THR%; else hold 0.50 (avoid over-weighting LAG in its edge-cycle trough, e.g. 2022-23/2026).
    EDGE_THR = 4.0
    try:
        _eh = pd.read_csv(os.path.join(WORKDIR, "data", "lag_edge_health.csv"), parse_dates=["entry"])
        _m12 = _eh.drop_duplicates("entry").set_index("entry").sort_index()["mean12"].reindex(common, method="ffill")
        print(f"  [edge-alloc] thr={EDGE_THR}%; mean12 latest={_m12.iloc[-1]:.1f}% (LAG tilt->.65 only if >= thr)")
    except Exception as _ex:
        _m12 = pd.Series(np.nan, index=common); print(f"  [edge-alloc] edge-health unavailable -> static tilt ({_ex})")
    def w_lag_target(i):
        s = states_c[i]
        if s in (3, 4, 5):
            m = _m12.iloc[i]
            return 0.65 if (pd.notna(m) and m >= EDGE_THR) else 0.50
        return STATE_LAG_WEIGHT.get(s, 0.5)   # BEAR=0, CRISIS=0.50
    cap_b_a = np.empty(len(common)); cap_l_a = np.empty(len(common))
    w0 = w_lag_target(0)
    cb = (1.0 - w0) * TOTAL_NAV; cl = w0 * TOTAL_NAV
    n_rebal = 0
    for i in range(len(common)):
        if i > 0:
            cb *= (1.0 + rb[i]); cl *= (1.0 + rl[i])
        P = cb + cl; w_tgt = w_lag_target(i)
        if P > 0 and abs(cl / P - w_tgt) > ALLOC_REBAL_BAND:   # band breach -> rebalance
            P -= ALLOC_REBAL_TC * abs(w_tgt * P - cl)          # friction on moved capital
            cl = w_tgt * P; cb = (1.0 - w_tgt) * P; n_rebal += 1
        cap_b_a[i] = cb; cap_l_a[i] = cl
    cap_b = pd.Series(cap_b_a, index=common); cap_l = pd.Series(cap_l_a, index=common)
    combined_nav = cap_b + cap_l
    # coherence factors: scale each book's ledger columns so they sum to its allocated capital
    fb = (cap_b / navb_c).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    fl = (cap_l / navl_c).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    _ls = states_c[-1]; _wl = STATE_LAG_WEIGHT.get(_ls, 0.5)
    _wcur = float(cap_l.iloc[-1] / combined_nav.iloc[-1]) if combined_nav.iloc[-1] > 0 else 0.0
    print(f"  [ALLOCATOR] band-only ±{ALLOC_REBAL_BAND*100:.0f}pp ON (w_LAG={STATE_LAG_WEIGHT}); "
          f"{n_rebal} rebalances; latest state={_ls} tgt LAG {_wl*100:.0f}% / current {_wcur*100:.0f}%")
else:
    combined_nav = navb_c + navl_c
    fb = pd.Series(1.0, index=common); fl = pd.Series(1.0, index=common)

def annot(events, book):
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events); df["book"] = book
    df["ymd"] = pd.to_datetime(df["ymd"]); return df
def etf_to_tx(etf_evts, book):
    if not etf_evts: return pd.DataFrame()
    d = pd.DataFrame(etf_evts); d["ymd"] = pd.to_datetime(d["ymd"])
    return pd.DataFrame({
        "ymd": d["ymd"], "ticker": PARK_TICKER,
        "action": d["action"].apply(lambda a: "buy" if a == "buy_etf" else "sell"),
        "buy_amount": np.where(d["action"] == "buy_etf", d["amount_vnd"], 0.0),
        "sell_amount": np.where(d["action"] == "sell_etf", d["amount_vnd"], 0.0),
        "fee": d["friction_cost"], "adj_price": d["price_vn30"], "shares": d["shares"],
        "holding_id": d["holding_id"], "play_type": "ETF_PARK",
        "cash_after": d["cash_after"],
        "reason": "ETF_REBAL_state" + d["state"].astype(str), "book": book})

all_tx = pd.concat([annot(events_bal, "BAL"), annot(events_lag, "LAGGED"),
                    etf_to_tx(etf_bal, "BAL"), etf_to_tx(etf_lag, "LAGGED")], ignore_index=True)
if not all_tx.empty:
    all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)
tx_counts = all_tx.groupby(all_tx["ymd"]).size().cumsum() if not all_tx.empty else pd.Series(dtype=int)
n_tx_series = pd.Series(0, index=common, dtype=int)
for d, n in tx_counts.items():
    n_tx_series.loc[n_tx_series.index >= d] = int(n)

# scale each book's ledger columns by its allocation factor (fb/fl) so book parts sum to combined_nav
bal_cash_s = (nb["cash"].loc[common] * fb); bal_stk_s = ((nb["positions_mv"]+nb["pending_mv"]).loc[common] * fb)
bal_etf_s  = (nb["cash_etf"].loc[common] * fb)
lag_cash_s = (nl["cash"].loc[common] * fl); lag_stk_s = ((nl["positions_mv"]+nl["pending_mv"]).loc[common] * fl)
lag_etf_s  = (nl["cash_etf"].loc[common] * fl)
combined_logs = pd.DataFrame({
    "ymd": common, "nav": combined_nav.values,
    "BAL_cash": bal_cash_s.values, "BAL_stocks": bal_stk_s.values, "BAL_etf": bal_etf_s.values,
    "SECOND_cash": lag_cash_s.values, "SECOND_stocks": lag_stk_s.values, "SECOND_etf": lag_etf_s.values,
    "cash": (bal_cash_s + lag_cash_s).values,
    "cash_etf": (bal_etf_s + lag_etf_s).values,
    "stocks_mv": (bal_stk_s + lag_stk_s).values,
    "num_holdings": (nb["n_pos"]+nl["n_pos"]).loc[common].values,
    "num_transactions": n_tx_series.values,
    "state": pd.Series(common).map(state_ff).values,
    "active_leg": ("LAG_ALLOC" if USE_LAG_ALLOCATOR else "LAG_ALWAYS"), "ens_signal": 0,
})

# ============================================================================
# 9. Save + open positions + MTM phantoms + report
# ============================================================================
print("\n[9] Saving...")
os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
def safe_to_csv(df, path):
    try:
        df.to_csv(path, index=False); return path
    except PermissionError:
        alt = path.replace(".csv", ".new.csv"); df.to_csv(alt, index=False); return alt

logs_path = safe_to_csv(combined_logs, os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv"))
last_day = common[-1]
open_parts, mtm_rows = [], []
for navdf, book in [(nav_bal, "BAL"), (nav_lag, "LAGGED")]:
    op = navdf.attrs.get("open_positions_final")
    lots = navdf.attrs.get("etf_lots_final")
    if op is not None and not op.empty:
        open_parts.append(op.assign(book=book))
        for _, p in op.iterrows():
            mtm_rows.append({"ymd": last_day, "ticker": p["ticker"], "action": "sell",
                "buy_amount": 0.0, "sell_amount": float(p["mark_value"]), "fee": 0.0,
                "adj_price": float(p["last_price"]) if pd.notna(p.get("last_price", np.nan)) else None,
                "shares": float(p["shares"]), "holding_id": p["holding_id"],
                "play_type": p.get("play_type", "?"), "cash_after": None,
                "reason": "MTM_UNREALIZED", "book": book})
    if lots is not None and not lots.empty:
        open_parts.append(lots.assign(book=book))
        for _, lot in lots.iterrows():
            mtm_rows.append({"ymd": last_day, "ticker": PARK_TICKER, "action": "sell",
                "buy_amount": 0.0, "sell_amount": float(lot["mark_value"]), "fee": 0.0,
                "adj_price": float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
                "shares": float(lot["shares"]), "holding_id": lot["holding_id"],
                "play_type": "ETF_PARK", "cash_after": None, "reason": "MTM_UNREALIZED", "book": book})
open_df = pd.concat(open_parts, ignore_index=True) if open_parts else \
          pd.DataFrame(columns=["ticker","holding_id","shares","book"])
if mtm_rows:
    all_tx = pd.concat([all_tx, pd.DataFrame(mtm_rows)], ignore_index=True)
    all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)
tx_path = safe_to_csv(all_tx, os.path.join(WORKDIR, "data", "pt_v22_dt5g_transactions.csv"))
open_path = safe_to_csv(open_df, os.path.join(WORKDIR, "data", "pt_v22_dt5g_open_positions.csv"))
print(f"  {logs_path}\n  {tx_path} (incl {len(mtm_rows)} MTM phantoms)\n  {open_path}: {len(open_df)} open rows")

final_nav = combined_nav.iloc[-1]
years = max((common[-1] - common[0]).days / 365.25, 1e-9)
total_ret = (final_nav / TOTAL_NAV - 1) * 100
cagr = (final_nav / TOTAL_NAV) ** (1 / years) - 1 if years > 0.05 else 0.0
peak = combined_nav.cummax(); dd = ((combined_nav - peak) / peak).min() * 100
n_capit = sum(1 for e in capit_events if e["size"] > 0.005)

print("\n" + "=" * 100)
print(f" SUMMARY — V2.3 = V2.2 (BAL | LAG static + park) + CAPIT v2 on DT5G")
print(f" Period: {common[0].date()} -> {common[-1].date()} ({years:.3f}y)")
print(f" Init: 50B   Final: {final_nav/1e9:.4f}B   ret={total_ret:+.2f}%   MaxDD={dd:+.2f}%")
print(f" CAPIT events fired in window: {n_capit}")
print("=" * 100)

with open(os.path.join(WORKDIR, "data", "pt_v22_dt5g_report.md"), "w", encoding="utf-8") as f:
    f.write("# pt_v22_dt5g — V2.3 = V2.2 (BAL | LAG static + park) + CAPIT v2 on DT5G\n\n")
    f.write(f"*Period*: {common[0].date()} -> {common[-1].date()} ({years:.3f}y, {len(common)} trading days)\n\n")
    f.write(f"*Init NAV*: 50B  |  *Final NAV*: {final_nav/1e9:.4f}B  |  *Total ret*: {total_ret:+.2f}%  |  *MaxDD*: {dd:+.2f}%\n\n")
    f.write(f"*Books*: BAL {nb['nav'].loc[last_day]/1e9:.4f}B | LAG {nl['nav'].loc[last_day]/1e9:.4f}B  |  *CAPIT events*: {n_capit}\n\n")
    if capit_events:
        f.write("## CAPIT washout events\n\n| Date | State | Grind | dd52w | Size |\n|---|---|---|---|---|\n")
        for e in capit_events:
            f.write(f"| {e['date'].date()} | {e['state']} | {e['grind']} | {e['dd']:.1f}% | {e['size']:.2f} |\n")
print("\nDone. Run analyze_portfolio.py for the full report.")
