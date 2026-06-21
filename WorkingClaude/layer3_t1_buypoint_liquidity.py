# -*- coding: utf-8 -*-
"""Phase 4 — Liquidity-aware ATC fill analysis.

CRITICAL question: ATC has low traded volume vs full session — can a BA-system
position (typically 1.25B VND per buy at 50B NAV/2-book/10-position split)
actually FILL at ATC for thin BAL tickers?

For each REAL BA-v11 trade in the 2.5y window:
  1. Tag liquidity tier by avg session VND traded:
       T1_TOP    : ADV >= 50B  (deeply liquid)
       T2_MID    : ADV 10-50B
       T3_LIQUID : ADV 2-10B
       T4_THIN   : ADV < 2B
  2. Compare position-size VND (~1.25B per book) vs:
       ATC bar volume (14:45)
       T1115 bar volume (11:15)
       Full-session volume
  3. Estimate fill probability at each slot if we limit fill to 20% of bar volume.
  4. Compute alpha conditional on liquidity tier.
  5. Recommend slot mix: ATC for liquid, intraday-staggered for thin.
"""
import os, sys, io, pickle
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")
TRADES_CSV = os.path.join(WORKDIR, "data", "layer3_t1_buypoint_alttrades.csv")

# Position sizing (BA-system 50B / 2 books / 10 pos = 2.5B per pos; per book 1.25B)
POSITION_SIZE_VND = 1.25e9  # per book leg
MAX_FILL_OF_BAR_VOL = 0.20  # don't take >20% of a 15m bar's traded volume

# Liquidity tier cutoffs (avg session VND, full-day)
T1_THR = 50e9   # >= 50B/day -> TOP
T2_THR = 10e9   # 10-50B -> MID
T3_THR = 2e9    # 2-10B -> LIQUID
                # < 2B -> THIN

print("=" * 100)
print("  Phase 4: ATC liquidity-tier check")
print("=" * 100)

# ============================================================================
# 1) Load intraday and build per-(ticker, date) volume profile
# ============================================================================
print("\n[1/4] Loading intraday cache + computing volume profile...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)

# Fast vectorized build: long-form panel then pivot for slot lookups.
# Store as nested dict: {(ticker, date): {"session": x, "atc": y, ...}}
vol_lookup = {}                    # (tk, date_ts) -> dict of slot vnd
adv_by_ticker = {}                 # tk -> mean session vnd
import time
t_start = time.time()
for i, (tk, bars) in enumerate(intraday.items()):
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date_ts"] = b["time"].dt.normalize()  # Timestamp at midnight (fast group key)
    b["hm"] = b["time"].dt.strftime("%H:%M")
    # vnstock prices in thousands -> raw VND
    b["vnd_traded"] = b["close"].astype(float) * 1000.0 * b["volume"].astype(float)
    # Per-day session sum (vectorized)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    # Slot volumes via pivot-like: filter then groupby
    slots_to_capture = {"atc":"14:45", "t1115":"11:15", "t0915":"09:15",
                         "t1330":"13:30", "t1415":"14:15"}
    slot_series = {}
    for label, hm in slots_to_capture.items():
        s = b[b["hm"] == hm].set_index("date_ts")["vnd_traded"]
        slot_series[label] = s
    # Build lookup
    for d_ts, sess_vnd in sess.items():
        rec = {"session": float(sess_vnd)}
        for label, s in slot_series.items():
            v = s.get(d_ts)
            rec[label] = float(v) if v is not None and not pd.isna(v) else np.nan
        vol_lookup[(tk, d_ts)] = rec
    adv_by_ticker[tk] = float(sess.mean())
    if (i+1) % 50 == 0:
        print(f"  {i+1}/{len(intraday)} tickers processed ({time.time()-t_start:.0f}s)")
print(f"  Done: {len(vol_lookup):,} ticker-sessions built in {time.time()-t_start:.0f}s")

# ============================================================================
# 2) Per-ticker avg session VND (liquidity tier)
# ============================================================================
print("\n[2/4] Tagging liquidity tiers...")
# adv_by_ticker already built in step 1 (vectorized)

def liq_tier(adv):
    if pd.isna(adv): return "T4_THIN"
    if adv >= T1_THR: return "T1_TOP"
    if adv >= T2_THR: return "T2_MID"
    if adv >= T3_THR: return "T3_LIQUID"
    return "T4_THIN"

tier_by_ticker = {tk: liq_tier(adv) for tk, adv in adv_by_ticker.items()}
tier_counts = pd.Series(list(tier_by_ticker.values())).value_counts()
print("  Ticker count by tier:")
for t in ["T1_TOP", "T2_MID", "T3_LIQUID", "T4_THIN"]:
    n = tier_counts.get(t, 0)
    print(f"    {t}: {n}")

# ============================================================================
# 3) Load real BA trades and tag with liquidity tier + fill risk per slot
# ============================================================================
print("\n[3/4] Joining BA trades to liquidity + slot volume...")
trades = pd.read_csv(TRADES_CSV)
trades["entry_date"] = pd.to_datetime(trades["entry_date"])

# Add tier
trades["tier"] = trades["ticker"].map(tier_by_ticker).fillna("T4_THIN")

# Vectorized slot-volume lookup via the (tk, date_ts) dict
def get_vol(tk, date_ts, label):
    rec = vol_lookup.get((tk, pd.Timestamp(date_ts).normalize()))
    if rec is None: return np.nan
    return rec.get(label, np.nan)

for label in ["session", "atc", "t1115", "t0915", "t1415"]:
    trades[f"vol_{label}"] = [get_vol(tk, ed, label)
                                for tk, ed in zip(trades["ticker"], trades["entry_date"])]

# Fill capacity ratio: position size / (MAX_FILL_OF_BAR_VOL × bar volume)
# If ratio > 1, we can't fill the full position in that bar.
def fill_ratio(vol):
    if pd.isna(vol) or vol <= 0: return np.nan
    return POSITION_SIZE_VND / (MAX_FILL_OF_BAR_VOL * vol)

for slot in ["atc", "t1115", "t0915", "t1415"]:
    trades[f"fill_ratio_{slot}"] = trades[f"vol_{slot}"].apply(fill_ratio)

# ============================================================================
# 4) Reports
# ============================================================================
print("\n[4/4] Reports")

print("\n--- Trades by liquidity tier ---")
print(trades.groupby("tier").size().to_string())

print("\n--- ATC fill feasibility (fill_ratio_atc <= 1 means can fill within 20% of ATC bar) ---")
fb = trades.groupby("tier").apply(lambda g: pd.Series({
    "n": len(g),
    "atc_fill_ok_pct": (g["fill_ratio_atc"] <= 1).mean()*100 if len(g) else np.nan,
    "atc_fill_median_ratio": g["fill_ratio_atc"].median(),
    "atc_fill_p90_ratio": g["fill_ratio_atc"].quantile(0.90),
    "atc_vnd_median_B": g["vol_atc"].median()/1e9 if g["vol_atc"].notna().any() else np.nan,
    "session_vnd_median_B": g["vol_session"].median()/1e9 if g["vol_session"].notna().any() else np.nan,
}))
print(fb.to_string(float_format=lambda x: f"{x:>8.2f}"))

# Compare fill feasibility across slots
print("\n--- Fill feasibility comparison across slots (% of trades fillable within 20% bar volume) ---")
slot_fb = trades.groupby("tier").apply(lambda g: pd.Series({
    "n": len(g),
    "ATC_14:45":  (g["fill_ratio_atc"]   <= 1).mean()*100,
    "T1415":      (g["fill_ratio_t1415"] <= 1).mean()*100,
    "T1115_11:15":(g["fill_ratio_t1115"] <= 1).mean()*100,
    "T0915_09:15":(g["fill_ratio_t0915"] <= 1).mean()*100,
}))
print(slot_fb.to_string(float_format=lambda x: f"{x:>8.1f}"))

# Alpha breakdown by tier (using existing roi_atc vs roi_open from trades CSV)
print("\n--- Per-trade ROI alpha vs OPEN by liquidity tier ---")
alpha_modes = ["roi_t1115_mkt", "roi_t1115_lim", "roi_atc", "roi_vwap"]
alpha_by_tier = trades.groupby("tier").apply(lambda g: pd.Series({
    "n": len(g),
    "roi_open_mean":   g["roi_open"].mean()*100,
    "atc_alpha_pp":    (g["roi_atc"] - g["roi_open"]).mean()*100,
    "t1115_alpha_pp":  (g["roi_t1115_mkt"] - g["roi_open"]).mean()*100,
    "t1115_lim_pp":    (g["roi_t1115_lim"] - g["roi_open"]).mean()*100,
    "vwap_alpha_pp":   (g["roi_vwap"] - g["roi_open"]).mean()*100,
}))
print(alpha_by_tier.to_string(float_format=lambda x: f"{x:>8.2f}"))

# Save trades with tier + fill ratios
out_csv = os.path.join(WORKDIR, "data", "layer3_liquidity_check.csv")
trades.to_csv(out_csv, index=False)
print(f"\nSaved: {out_csv}")
