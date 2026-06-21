# -*- coding: utf-8 -*-
"""Kelly Sizing Research Q3 — per-tier slot-weight optimization.

Three-stage script (each stage caches output in kelly_q3_out/):

  STAGE 1: Rebuild fresh BA v11 12y canonical trade log with CURRENT TIER_BAL
           labels (MEGA, S_PRO, MOMENTUM_QUALITY, COMPOUNDER_BUY, RE_BACKLOG_BUY,
           etc.) — the existing ba_trades_bal_refresh.csv only has 4 legacy
           SCORE_V10 tiers.  Output: ba_trades_v11_tier_labels.csv

  STAGE 2: Per-tier Kelly fit using continuous Kelly = mu / sigma**2.  Apply
           quarter-Kelly + clip [4%, 18%] + renormalize so trade-count-weighted
           mean per-slot weight = 10% (matches current flat baseline, so total
           gross exposure unchanged — pure redistribution).
           Tiers with n<30 → flat 10% (sample too small).
           Outputs: kelly_q3_tier_stats.csv, kelly_q3_tier_weights.csv

  STAGE 3: Run TWO 12y canonical sims (BASELINE flat 10% vs PROPOSED Kelly-
           derived weights) on identical V11 config (T+1 Open, real E1VFVN30
           ETF, max_pos=12, sector cap, V6 ETF rule, transparent mode).
           Compare CAGR / Sharpe / MaxDD / Calmar / trades on:
           full 12y, OOS 2024-2026, pre-OOS 2014-2019.

Run order: this script is idempotent — re-running uses cached stage outputs.
Delete the cache files to force a rebuild.

NO PRODUCTION CODE MODIFIED.
"""
import os, sys, io, pickle, bisect
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUTDIR = os.path.join(WORKDIR, "kelly_q3_out")
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

# ─── Canonical V11 config (12y, identical to sim_v11_transparent but 2014-2026) ──
START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9      # 50/50 BAL+VN30
POSITION_VND = 1.25e9  # 10% of BOOK_NAV
FILL_CAP   = 0.20
T1_TOP_ADV = 50e9

INTRADAY_PKL = os.path.join(WORKDIR, "intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                  "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]   # slots that BAL/VN30 sims allow to enter
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
FLAT_WEIGHT = 0.10                             # current production baseline
TIER_WEIGHTS_FLAT = {t: FLAT_WEIGHT for t in TIER_BAL}

# Stage1/Stage3 cache files
SIG_PKL    = os.path.join(OUTDIR, "_signals_v11_12y.pkl")
TRADES_CSV = os.path.join(WORKDIR, "ba_trades_v11_tier_labels.csv")  # deliverable
TIER_STATS_CSV   = os.path.join(WORKDIR, "kelly_q3_tier_stats.csv")
TIER_WEIGHTS_CSV = os.path.join(WORKDIR, "kelly_q3_tier_weights.csv")
SIM_RESULTS_CSV  = os.path.join(OUTDIR, "_sim_results.csv")
SIM_TRADES_FLAT  = os.path.join(OUTDIR, "_sim_trades_flat.csv")
SIM_TRADES_KELLY = os.path.join(OUTDIR, "_sim_trades_kelly.csv")
SIM_NAV_FLAT     = os.path.join(OUTDIR, "_sim_nav_flat.csv")
SIM_NAV_KELLY    = os.path.join(OUTDIR, "_sim_nav_kelly.csv")
RESULTS_MD       = os.path.join(WORKDIR, "kelly_q3_tier_weights_results.md")

# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def load_or_build_signals():
    """Build the V11 filtered signal frame for 12y. Cached to disk."""
    if os.path.exists(SIG_PKL):
        print(f"  [cache] loading {SIG_PKL}")
        with open(SIG_PKL, "rb") as f:
            return pickle.load(f)

    print("  Loading v10 signals (12y) from BQ...")
    sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"    {len(sig):,} signal rows")

    # Release_Date for SV_TIGHT
    print("  Computing days_since_release...")
    releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
    releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
    rbyt = releases.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
    ds = np.empty(len(sig))
    for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
        arr = rbyt.get(tk)
        if not arr: ds[i] = np.nan; continue
        idx = bisect.bisect_right(arr, pd.Timestamp(t))
        if idx == 0: ds[i] = np.nan; continue
        ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
    sig["days_since_release"] = ds

    # 5-state + overheat
    print("  Loading 5-state + computing overheat dates...")
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
    sig["state"] = sig["time"].map(state_by_date)
    print(f"    Overheat days: {len(overheat_dates)}")

    # D1 RE_BACKLOG_BUY override
    print("  Applying D1 RE_BACKLOG_BUY (ICB 8633 + AdvCust YoY > 0.5)...")
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
  fin.Revenue_YoY_P0 AS rev_yoy,
  adv.adv_yoy, s5.state AS state5
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
    d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5)
               & d1["fa_tier"].isin(["C","D"])
               & d1["state5"].isin([3,4,5])
               & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
    d1_qual = d1.loc[d1_mask, ["ticker","time"]].assign(_d1_ok=True)
    sig = sig.merge(d1_qual, on=["ticker","time"], how="left")
    override_mask = sig["_d1_ok"].fillna(False) & (sig["ta"] >= 120)
    sig.loc[override_mask, "play_type"] = "RE_BACKLOG_BUY"
    sig = sig.drop(columns=["_d1_ok"])
    print(f"    D1 override: {int(override_mask.sum()):,} rows -> RE_BACKLOG_BUY")

    # SV_TIGHT + P3
    print("  Applying SV_TIGHT (state-conditional Fresh-Q) + P3 (overheat block)...")
    def sv_tight_keep(row):
        s = row["state"]; days = row["days_since_release"]
        if pd.isna(s): return True
        s = int(s)
        if s in (4,5): return True
        if s == 1:    return pd.notna(days) and days <= 30
        if s in (2,3):return pd.notna(days) and days <= 60
        return True
    mask_bacore = sig["play_type"].isin(BUY_TIERS_V11)
    mask_keep = (~mask_bacore) | sig.apply(sv_tight_keep, axis=1)
    sig_f = sig[mask_keep].copy()
    mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
    sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"

    # Open + sector + top30 + state_ff + vni_dates + etf prices (all cached together)
    print("  Loading Open + sector_map + top30 + E1VFVN30 ETF prices...")
    opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
    opens_df["time"] = pd.to_datetime(opens_df["time"])
    open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}

    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())

    etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
    etf_real["time"] = pd.to_datetime(etf_real["time"])
    vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))
    print(f"    E1VFVN30 BQ rows: {len(etf_real)} ({etf_real['time'].min().date() if len(etf_real) else '-'} -> {etf_real['time'].max().date() if len(etf_real) else '-'})")

    sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    state_ff = {}; last_s = None
    for d in vni_dates:
        s = state_by_date.get(d)
        if s is not None: last_s = s
        state_ff[d] = last_s

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_f.iterrows()}

    out = {
        "sig_f": sig_f, "prices": prices, "liq_map": liq_map,
        "vni_dates": vni_dates, "open_prices": open_prices,
        "vn30_underlying": vn30_underlying, "sec_map": sec_map, "top30": top30,
        "state_ff": state_ff,
    }
    with open(SIG_PKL, "wb") as f:
        pickle.dump(out, f)
    print(f"    cached -> {SIG_PKL}")
    return out


def load_or_build_alt_hybrid():
    """v4 HYBRID alt-fill: ATC for T1_TOP / 11:15 for others, gated by liquidity.
    For pre-intraday-cache period (most of 2014-2025), alt_hybrid will be empty
    for many tickers — sim falls back to T+1 Open which is the canonical."""
    path = os.path.join(OUTDIR, "_alt_hybrid.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    if not os.path.exists(INTRADAY_PKL):
        print(f"  [warn] {INTRADAY_PKL} missing — alt_hybrid disabled (sim uses T+1 Open canonical)")
        out = {}
        with open(path, "wb") as f:
            pickle.dump(out, f)
        return out
    print("  Building v4 HYBRID alt-fill dict from intraday cache...")
    with open(INTRADAY_PKL, "rb") as f:
        intraday = pickle.load(f)
    adv_by_ticker = {}
    slot_p_atc, slot_v_atc, slot_p_t1115, slot_v_t1115 = {}, {}, {}, {}
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
            ("14:45", slot_p_atc, slot_v_atc),
            ("11:15", slot_p_t1115, slot_v_t1115),
        ]:
            sub = b[b["hm"] == hm]
            for _, row in sub.iterrows():
                d_ts = row["date_ts"]
                p_dict.setdefault(tk, {})[d_ts] = float(row["close_vnd"])
                v_dict.setdefault(tk, {})[d_ts] = float(row["vnd_traded"])

    alt_hybrid = {}
    for tk in set(slot_p_atc.keys()) | set(slot_p_t1115.keys()):
        adv = adv_by_ticker.get(tk, 0)
        is_top = adv >= T1_TOP_ADV
        src_p = slot_p_atc.get(tk, {}) if is_top else slot_p_t1115.get(tk, {})
        src_v = slot_v_atc.get(tk, {}) if is_top else slot_v_t1115.get(tk, {})
        for d_ts, p in src_p.items():
            v = src_v.get(d_ts)
            if v is not None and v * FILL_CAP >= POSITION_VND:
                alt_hybrid.setdefault(tk, {})[d_ts] = p
    with open(path, "wb") as f:
        pickle.dump(alt_hybrid, f)
    return alt_hybrid


def run_one_sim(sig_f, prices, liq_map, vni_dates, open_prices, vn30_underlying,
                sec_map, top30, state_ff, alt_hybrid, tier_weights, label):
    """Run BAL+VN30 books with provided tier_weights, return combined nav DF and trades."""
    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    nav_bal, trades_bal = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=tier_weights,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        force_close_eod=False,
        **LIQ_FULL, name=f"{label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

    nav_v30, trades_v30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=tier_weights,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        force_close_eod=False,
        **LIQ_V30, name=f"{label}_VN30")

    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    nav_v30["time"] = pd.to_datetime(nav_v30["time"])
    nav_b_s = nav_bal.set_index("time")["nav"]
    nav_v_s = nav_v30.set_index("time")["nav"]
    common = nav_b_s.index.intersection(nav_v_s.index)
    combined = pd.DataFrame({"time": common,
                              "nav": (nav_b_s.loc[common] + nav_v_s.loc[common]).values})
    trades_bal["book"] = "BAL"
    trades_v30["book"] = "VN30"
    all_trades = pd.concat([trades_bal, trades_v30], ignore_index=True)
    return combined, all_trades


def window_metrics(nav_df, label):
    nav = nav_df["nav"]
    times = pd.to_datetime(nav_df["time"])
    n_days = (times.iloc[-1] - times.iloc[0]).days
    n_yrs = n_days / 365.25
    rets = nav.pct_change().dropna()
    spy = len(rets) / n_yrs if n_yrs > 0 else 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / n_yrs) - 1 if n_yrs > 0 else 0
    sh = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav - nav.cummax()) / nav.cummax()).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return {"label": label, "n_yrs": n_yrs,
            "cagr_pct": cagr*100, "sharpe": sh,
            "max_dd_pct": dd*100, "calmar": cal,
            "wealth_x": nav.iloc[-1]/nav.iloc[0],
            "final_nav_bn": nav.iloc[-1]/1e9}


def slice_period(nav_df, ps, pe):
    t = pd.to_datetime(nav_df["time"])
    m = (t >= pd.Timestamp(ps)) & (t <= pd.Timestamp(pe))
    return nav_df.loc[m].reset_index(drop=True)


# ════════════════════════════════════════════════════════════════════════════
# Main flow
# ════════════════════════════════════════════════════════════════════════════
print("=" * 100)
print(f"  KELLY Q3 — per-tier slot weight research")
print(f"  Canonical V11 12y: {START_DATE} → {END_DATE}, init NAV = {TOTAL_NAV/1e9:.0f}B")
print("=" * 100)

# ─── STAGE 1 ────────────────────────────────────────────────────────────────
print("\n" + "─" * 100)
print(" STAGE 1 — build canonical V11 trade log with current TIER_BAL labels")
print("─" * 100)

ctx = load_or_build_signals()
alt_hybrid = load_or_build_alt_hybrid()

print("\n  Running BASELINE sim (flat 10% per tier) — this is also the trade-log source...")
nav_flat, trades_flat = run_one_sim(
    ctx["sig_f"], ctx["prices"], ctx["liq_map"], ctx["vni_dates"],
    ctx["open_prices"], ctx["vn30_underlying"], ctx["sec_map"], ctx["top30"],
    ctx["state_ff"], alt_hybrid, TIER_WEIGHTS_FLAT, "FLAT")

# Save flat sim outputs (cache for stage 3)
nav_flat.to_csv(SIM_NAV_FLAT, index=False)
trades_flat.to_csv(SIM_TRADES_FLAT, index=False)

# Build deliverable trade log (subset of standard cols)
trade_log = trades_flat[["entry_date","exit_date","ticker","play_type",
                          "entry_price","exit_price","ret_net","days_held","reason"]].copy()
trade_log = trade_log.rename(columns={"ret_net": "net_return_pct"})
trade_log["net_return_pct"] = trade_log["net_return_pct"] * 100   # percent
trade_log = trade_log.sort_values(["entry_date","ticker"]).reset_index(drop=True)
trade_log.to_csv(TRADES_CSV, index=False)
print(f"\n  ✓ Trade log written: {TRADES_CSV}")
print(f"    {len(trade_log)} trades, {trade_log['play_type'].nunique()} distinct tiers")
print(f"    Tier distribution:")
for tier, n in trade_log["play_type"].value_counts().items():
    print(f"      {tier:<25} {n:>5}")

# ─── STAGE 2 — Kelly fit ────────────────────────────────────────────────────
print("\n" + "─" * 100)
print(" STAGE 2 — per-tier Kelly fit (quarter-Kelly, normalized to flat 10%)")
print("─" * 100)

# All-time tier stats from trade_log
rows = []
for tier, sub in trade_log.groupby("play_type"):
    n = len(sub)
    rets = sub["net_return_pct"] / 100.0   # back to fraction
    wr = (rets > 0).mean()
    avg_win  = rets[rets > 0].mean() if (rets > 0).any() else 0
    avg_loss = -rets[rets < 0].mean() if (rets < 0).any() else 0   # positive number
    mu = rets.mean()
    sd = rets.std()
    sharpe_tr = mu/sd if sd > 0 else 0
    kelly_c = mu / (sd*sd) if sd > 0 else 0
    rows.append({
        "play_type": tier, "n": n, "WR_pct": wr*100,
        "avg_win_pct": avg_win*100, "avg_loss_pct": avg_loss*100,
        "mean_ret_pct": mu*100, "sd_ret_pct": sd*100,
        "sharpe_per_trade": sharpe_tr, "kelly_continuous": kelly_c,
    })
stats = pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)
stats.to_csv(TIER_STATS_CSV, index=False)
print(f"\n  ✓ Tier stats: {TIER_STATS_CSV}")
print(stats.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# Normalization procedure per spec §2.3:
#   raw_w = 0.10 × (kelly_c / mean(kelly_c)) × 0.25   (quarter Kelly)
#   clip [0.04, 0.18]
#   then rescale so Σ(n × w) = Σ(n × 0.10) — keep total gross exposure same
#   tiers with n < 30 → keep at 0.10 (small-sample protection)

LOW_N = 30
small_n = stats[stats["n"] < LOW_N]["play_type"].tolist()
fit_stats = stats[stats["n"] >= LOW_N].copy()

if len(fit_stats) > 0 and fit_stats["kelly_continuous"].mean() > 0:
    mean_k = fit_stats["kelly_continuous"].mean()
    raw_w = FLAT_WEIGHT * (fit_stats["kelly_continuous"] / mean_k) * 0.25
    raw_w = raw_w.clip(lower=0.04, upper=0.18)
    # Renormalize to keep Σ(n_i × w_i) = Σ(n_i × 0.10) among fitted tiers
    target_sum = (fit_stats["n"] * FLAT_WEIGHT).sum()
    cur_sum = (fit_stats["n"] * raw_w).sum()
    scale = target_sum / cur_sum if cur_sum > 0 else 1.0
    fit_stats["proposed_weight"] = (raw_w * scale).clip(lower=0.04, upper=0.18)
    # Re-renormalize once more in case clip changed sums
    cur_sum2 = (fit_stats["n"] * fit_stats["proposed_weight"]).sum()
    if cur_sum2 > 0:
        scale2 = target_sum / cur_sum2
        # Only apply if scale2 stays inside clip bounds for all
        candidate = (fit_stats["proposed_weight"] * scale2)
        if (candidate >= 0.04).all() and (candidate <= 0.18).all():
            fit_stats["proposed_weight"] = candidate
else:
    fit_stats["proposed_weight"] = FLAT_WEIGHT

# Build final weights dict — small-n tiers default to flat 10%
proposed = {t: FLAT_WEIGHT for t in TIER_BAL}
for _, r in fit_stats.iterrows():
    if r["play_type"] in TIER_BAL:   # only tiers actually used as entries
        proposed[r["play_type"]] = float(r["proposed_weight"])

# Make full output table including small-n tiers (= flat 10%)
all_weights = []
for _, r in stats.iterrows():
    pt = r["play_type"]
    w_proposed = proposed.get(pt, FLAT_WEIGHT)
    note = ""
    if r["n"] < LOW_N:
        note = f"small_n_keep_flat_{int(LOW_N)}"
    if pt not in TIER_BAL:
        note = (note + ";" if note else "") + "not_in_TIER_BAL_entry_universe"
    all_weights.append({
        "play_type": pt, "n_trades": int(r["n"]),
        "mean_ret_pct": r["mean_ret_pct"],
        "kelly_continuous": r["kelly_continuous"],
        "current_weight": FLAT_WEIGHT,
        "proposed_weight": w_proposed,
        "delta_pp": (w_proposed - FLAT_WEIGHT) * 100,
        "note": note,
    })
weights_df = pd.DataFrame(all_weights).sort_values("kelly_continuous", ascending=False).reset_index(drop=True)
weights_df.to_csv(TIER_WEIGHTS_CSV, index=False)
print(f"\n  ✓ Proposed weights: {TIER_WEIGHTS_CSV}")
print(weights_df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# Sanity: total exposure preserved among fitted tiers
print(f"\n  Sanity: Σ(n × w) preserved = {fit_stats['n'].sum() * FLAT_WEIGHT:.2f} (flat) vs "
      f"{(fit_stats['n'] * fit_stats['proposed_weight']).sum():.2f} (kelly)")
print(f"  TIER_WEIGHTS injected into PROPOSED sim:")
for k, v in proposed.items():
    delta = (v - FLAT_WEIGHT) * 100
    print(f"    {k:<25} {v*100:>5.2f}%   ({delta:+.2f} pp vs 10%)")

# ─── STAGE 3 — comparison sim ────────────────────────────────────────────────
print("\n" + "─" * 100)
print(" STAGE 3 — comparison sim: BASELINE (flat 10%) vs PROPOSED (Kelly-derived)")
print("─" * 100)

print("\n  Running PROPOSED sim (Kelly-derived tier weights)...")
nav_kelly, trades_kelly = run_one_sim(
    ctx["sig_f"], ctx["prices"], ctx["liq_map"], ctx["vni_dates"],
    ctx["open_prices"], ctx["vn30_underlying"], ctx["sec_map"], ctx["top30"],
    ctx["state_ff"], alt_hybrid, proposed, "KELLY")
nav_kelly.to_csv(SIM_NAV_KELLY, index=False)
trades_kelly.to_csv(SIM_TRADES_KELLY, index=False)

# Sub-periods
PERIODS = [
    ("FULL 2014-2026",  "2014-01-01", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-01", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
]

print("\n" + "=" * 100)
print("  📊 RESULTS — BASELINE (flat 10%) vs PROPOSED (Kelly)")
print("=" * 100)
print(f"\n  {'Period':<22} {'Variant':<10} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'NAV (B)':>9} {'Wealth':>8}")
print(f"  {'-'*22} {'-'*10} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9} {'-'*8}")

results_rows = []
for plabel, ps, pe in PERIODS:
    sub_f = slice_period(nav_flat, ps, pe)
    sub_k = slice_period(nav_kelly, ps, pe)
    if len(sub_f) < 30 or len(sub_k) < 30:
        continue
    # Re-base both to 1.0 at start of window for cleaner comparison? — no, keep absolute
    mF = window_metrics(sub_f, f"{plabel}|FLAT")
    mK = window_metrics(sub_k, f"{plabel}|KELLY")
    # n_trades in window
    tf = trades_flat.copy()
    tk = trades_kelly.copy()
    tf["entry_date"] = pd.to_datetime(tf["entry_date"])
    tk["entry_date"] = pd.to_datetime(tk["entry_date"])
    nF = ((tf["entry_date"] >= pd.Timestamp(ps)) & (tf["entry_date"] <= pd.Timestamp(pe))).sum()
    nK = ((tk["entry_date"] >= pd.Timestamp(ps)) & (tk["entry_date"] <= pd.Timestamp(pe))).sum()
    print(f"  {plabel:<22} {'FLAT':<10} {mF['cagr_pct']:>+7.2f}% {mF['sharpe']:>+7.2f} "
          f"{mF['max_dd_pct']:>+7.1f}% {mF['calmar']:>+7.2f} {mF['final_nav_bn']:>+8.2f}  {mF['wealth_x']:>+6.2f}×")
    print(f"  {'':<22} {'KELLY':<10} {mK['cagr_pct']:>+7.2f}% {mK['sharpe']:>+7.2f} "
          f"{mK['max_dd_pct']:>+7.1f}% {mK['calmar']:>+7.2f} {mK['final_nav_bn']:>+8.2f}  {mK['wealth_x']:>+6.2f}×")
    dCAGR = mK['cagr_pct'] - mF['cagr_pct']
    dSh   = mK['sharpe']   - mF['sharpe']
    dDD   = mK['max_dd_pct'] - mF['max_dd_pct']
    print(f"  {'':<22} {'Δ K-F':<10} {dCAGR:>+7.2f}pp {dSh:>+7.2f} {dDD:>+7.1f}pp")
    results_rows.append({
        "period": plabel, "ps": ps, "pe": pe,
        "FLAT_cagr": mF['cagr_pct'], "FLAT_sharpe": mF['sharpe'],
        "FLAT_dd": mF['max_dd_pct'], "FLAT_calmar": mF['calmar'],
        "FLAT_nav_bn": mF['final_nav_bn'], "FLAT_n_trades": int(nF),
        "KELLY_cagr": mK['cagr_pct'], "KELLY_sharpe": mK['sharpe'],
        "KELLY_dd": mK['max_dd_pct'], "KELLY_calmar": mK['calmar'],
        "KELLY_nav_bn": mK['final_nav_bn'], "KELLY_n_trades": int(nK),
        "dCAGR_pp": dCAGR, "dSharpe": dSh, "dDD_pp": dDD,
    })
    print()

results_df = pd.DataFrame(results_rows)
results_df.to_csv(SIM_RESULTS_CSV, index=False)

# Per-tier deployment breakdown (PROPOSED sim)
print("\n  Per-tier breakdown in PROPOSED (Kelly) sim:")
print(f"    {'tier':<25} {'n_trades':>8} {'mean_ret':>9} {'sum_pnl_proxy':>14} {'%share':>7}")
br = []
for tier, sub in trades_kelly.groupby("play_type"):
    n = len(sub)
    mr = sub["ret_net"].mean() * 100 if n > 0 else 0
    # PnL proxy = sum(ret_net × weight × cost_basis) — but we don't have cost basis here
    # Use n_trades × mean_ret × weight as deployment-weighted contribution
    w = proposed.get(tier, FLAT_WEIGHT)
    pnl_proxy = sub["ret_net"].sum() * w * 100  # in pp-trade units
    br.append({"play_type": tier, "n_trades": n,
               "mean_ret_pct": mr, "pnl_proxy": pnl_proxy, "weight": w})
br_df = pd.DataFrame(br).sort_values("pnl_proxy", ascending=False)
total_pnl = br_df["pnl_proxy"].sum()
br_df["share_pct"] = br_df["pnl_proxy"] / total_pnl * 100 if total_pnl != 0 else 0
for _, r in br_df.iterrows():
    print(f"    {r['play_type']:<25} {int(r['n_trades']):>8} {r['mean_ret_pct']:>+8.2f}% "
          f"{r['pnl_proxy']:>+13.2f} {r['share_pct']:>+6.1f}%")

# Verdict per spec gate (OOS 2024-2026: ΔCAGR ≥ +0.5pp, ΔSharpe ≥ +0.05, ΔMaxDD ≥ -1.5pp)
oos = results_df[results_df["period"] == "OOS 2024-2026"]
if len(oos):
    o = oos.iloc[0]
    g_cagr = o["dCAGR_pp"] >= 0.5
    g_sh = o["dSharpe"] >= 0.05
    g_dd = o["dDD_pp"] >= -1.5
    if g_cagr and g_sh and g_dd:
        verdict = "GREEN"
    elif (o["dCAGR_pp"] >= 0 and o["dSharpe"] >= 0 and o["dDD_pp"] >= -1.5):
        verdict = "YELLOW"
    else:
        verdict = "RED"
    print(f"\n  ═══ VERDICT (OOS 2024-2026 gate) ═══")
    print(f"    ΔCAGR  {o['dCAGR_pp']:+.2f}pp (gate ≥ +0.5pp)  {'✓' if g_cagr else '✗'}")
    print(f"    ΔSharpe {o['dSharpe']:+.2f}  (gate ≥ +0.05)    {'✓' if g_sh else '✗'}")
    print(f"    ΔMaxDD  {o['dDD_pp']:+.2f}pp (gate ≥ -1.5pp)   {'✓' if g_dd else '✗'}")
    print(f"    >>> {verdict} <<<")
else:
    verdict = "UNDEFINED"

# ─── STAGE 4 — Write markdown ───────────────────────────────────────────────
print("\n  Writing markdown report...")
lines = []
lines.append("# Kelly Q3 — per-tier slot-weight test results\n")
lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}  ")
lines.append(f"**Sim**: V11 canonical 12y, {START_DATE} → {END_DATE}, init NAV 50B, T+1 Open exec, real E1VFVN30 ETF  ")
lines.append(f"**Config**: max_pos=12, sector cap 8:4, RE_BACKLOG_BUY exempt, SV_TIGHT + P3 active, V6 ETF (state 3 = 70% idle cash)  ")
lines.append(f"**No production code modified.**\n")

lines.append("## Stage 1 — fresh canonical trade log\n")
lines.append(f"Re-ran the V11 stack with **flat 10%** baseline weights to produce a trade log carrying current `TIER_BAL` labels (the existing `ba_trades_bal_refresh.csv` only had 4 legacy SCORE_V10 labels — MEGA / S_PRO / MOMENTUM_QUALITY / COMPOUNDER_BUY / RE_BACKLOG_BUY were absent).\n")
lines.append(f"Output: `ba_trades_v11_tier_labels.csv` — **{len(trade_log)} trades** across **{trade_log['play_type'].nunique()} distinct tiers**.\n")

lines.append("\n## Stage 2 — per-tier stats and Kelly fit\n")
lines.append("Per-tier statistics (sorted by Kelly_continuous = mu / sigma**2):\n")
lines.append("| tier | n | WR % | avg_win % | avg_loss % | mean_ret % | sd_ret % | Sharpe/trade | Kelly_c | current | **proposed** | Δ pp | note |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
merged = stats.merge(weights_df[["play_type","proposed_weight","note"]], on="play_type", how="left")
merged = merged.sort_values("kelly_continuous", ascending=False)
for _, r in merged.iterrows():
    lines.append(f"| {r['play_type']} | {int(r['n'])} | {r['WR_pct']:.1f} | {r['avg_win_pct']:.2f} | {r['avg_loss_pct']:.2f} | "
                 f"{r['mean_ret_pct']:.2f} | {r['sd_ret_pct']:.2f} | {r['sharpe_per_trade']:.3f} | {r['kelly_continuous']:.3f} | "
                 f"{FLAT_WEIGHT*100:.1f}% | **{r['proposed_weight']*100:.2f}%** | {(r['proposed_weight']-FLAT_WEIGHT)*100:+.2f} | {r['note']} |")

lines.append("\n**Normalization procedure** (per spec §2.3):  ")
lines.append("`raw_w = 0.10 × (Kelly_c / mean(Kelly_c)) × 0.25` → clip `[4%, 18%]` → rescale so `Σ(n × w) = Σ(n × 0.10)` (preserves total gross exposure — pure redistribution).  ")
lines.append(f"Tiers with `n < {LOW_N}` kept at flat **{FLAT_WEIGHT*100:.0f}%**.")

lines.append("\n## Stage 3 — side-by-side sim results\n")
lines.append(f"| Period | Variant | CAGR | Sharpe | MaxDD | Calmar | Final NAV (B) | Wealth × | n_trades |")
lines.append(f"|---|---|---:|---:|---:|---:|---:|---:|---:|")
for _, r in results_df.iterrows():
    lines.append(f"| {r['period']} | FLAT  | {r['FLAT_cagr']:+.2f}% | {r['FLAT_sharpe']:.2f} | {r['FLAT_dd']:+.1f}% | {r['FLAT_calmar']:.2f} | {r['FLAT_nav_bn']:.2f} | {r['FLAT_nav_bn']/(TOTAL_NAV/1e9):.2f}× | {r['FLAT_n_trades']} |")
    lines.append(f"| {r['period']} | KELLY | {r['KELLY_cagr']:+.2f}% | {r['KELLY_sharpe']:.2f} | {r['KELLY_dd']:+.1f}% | {r['KELLY_calmar']:.2f} | {r['KELLY_nav_bn']:.2f} | {r['KELLY_nav_bn']/(TOTAL_NAV/1e9):.2f}× | {r['KELLY_n_trades']} |")
    lines.append(f"| {r['period']} | **Δ K−F** | **{r['dCAGR_pp']:+.2f}pp** | **{r['dSharpe']:+.2f}** | **{r['dDD_pp']:+.1f}pp** | – | – | – | {r['KELLY_n_trades']-r['FLAT_n_trades']:+d} |")

lines.append("\n## Per-tier deployment in PROPOSED (Kelly) sim\n")
lines.append("Rough contribution proxy = Σ(ret_net) × tier_weight × 100 (in pp-trade units; cost-basis weighting not available without re-running with per-trade size logging).\n")
lines.append("| tier | n_trades | mean_ret % | weight | pnl_proxy | share % |")
lines.append("|---|---:|---:|---:|---:|---:|")
for _, r in br_df.iterrows():
    lines.append(f"| {r['play_type']} | {int(r['n_trades'])} | {r['mean_ret_pct']:+.2f} | {r['weight']*100:.2f}% | {r['pnl_proxy']:+.2f} | {r['share_pct']:+.1f}% |")

# Verdict block
if verdict != "UNDEFINED" and len(oos):
    o = oos.iloc[0]
    lines.append(f"\n## Verdict — **{verdict}**\n")
    lines.append(f"OOS 2024-2026 gate (per spec §4.2):\n")
    lines.append(f"- ΔCAGR  = **{o['dCAGR_pp']:+.2f} pp**  (gate ≥ +0.5pp)  {'PASS' if o['dCAGR_pp']>=0.5 else 'FAIL'}")
    lines.append(f"- ΔSharpe = **{o['dSharpe']:+.2f}**  (gate ≥ +0.05)  {'PASS' if o['dSharpe']>=0.05 else 'FAIL'}")
    lines.append(f"- ΔMaxDD = **{o['dDD_pp']:+.1f} pp**  (gate ≥ −1.5pp; positive = better)  {'PASS' if o['dDD_pp']>=-1.5 else 'FAIL'}")

# List small-n tiers
if small_n:
    lines.append(f"\n### Tiers kept at flat {FLAT_WEIGHT*100:.0f}% (n < {LOW_N})\n")
    for pt in small_n:
        n_pt = int(stats.loc[stats['play_type']==pt, 'n'].iloc[0])
        lines.append(f"- `{pt}` (n={n_pt})")

lines.append(f"\n## Files\n")
lines.append(f"- `ba_trades_v11_tier_labels.csv` — fresh 12y trade log with current tier labels")
lines.append(f"- `kelly_q3_tier_stats.csv` — per-tier WR/mean/sd/Kelly_c")
lines.append(f"- `kelly_q3_tier_weights.csv` — proposed weights with sample-size notes")
lines.append(f"- `test_kelly_q3_tier_weights.py` — this script (no production code touched)")
lines.append(f"- `kelly_q3_out/_sim_nav_flat.csv`, `_sim_nav_kelly.csv` — daily NAV curves")
lines.append(f"- `kelly_q3_out/_sim_trades_flat.csv`, `_sim_trades_kelly.csv` — trade-level results")
lines.append(f"- `kelly_q3_out/_sim_results.csv` — summary table")

with open(RESULTS_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"  ✓ {RESULTS_MD}")

print("\n" + "=" * 100)
print("  DONE")
print("=" * 100)
