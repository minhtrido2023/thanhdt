# -*- coding: utf-8 -*-
"""Phase-1 — Pre-registered family proxy evaluation (re-tune SIGNAL_V11 tren fa_ratings_8l).
Job Taylor_20260711_125524 (plan plan_fa8l_retune_20260711.md muc Phase 1).

KHONG phai full pt_v23 backtest (do la Phase 2). Proxy = signal-level composition + fwd-return
cua ENTRY SET (TIER_BAL semantics), do tren panel weekly BQ THAT, IS/OOS tach, per-year.

Grounding (Phase 0):
- 0b: giu FULL coverage 8L (coverage DUONG +0.88pp); degradation = thang do -> redesign bucket.
- 0c: rating8l = GATE theo context. Bull-momentum ctx IC am manh (r4/r5 xau); NEUTRAL momentum
  FLIP dau (OOS +0.10); SECURITIES route IC am manh ca IS+OOS (-0.22/-0.17); BANK OOS ~0;
  REALESTATE r5 xau IS. Compounder ctx hit monotonic r1>r2>...>r5.
- Harness reality (pt_v23_audit_2014.py): entry set = TIER_BAL 6 tiers, weight phang 0.10,
  sort ta; S_PRO/MOMENTUM_QUALITY/COMPOUNDER_BUY = INTERCEPT (non-entry). mp4 EXBULL suppress,
  SV_TIGHT fresh-gate state 2/3<=60d (1<=30d), D1 override RE_BACKLOG_BUY (ICB 8633).
- regime_size_overlay (rating>=4 halving) chi hoat dong state<=2 -> khong overlap voi gate s45.

Family: 11 config do + control legacy K0 (khong dem trial) + 1 reserve slot (khai bao, chua dung).
N-ledger: 4 da dung (2 drop-in + 2 diagnostic 0b) + 11 = 15/16; reserve dung not -> 16/16.

Proxy metrics per config: weekly equal-weight mean fwd profit_1M/2M cua entry set (uncapped +
top-20 theo ta, xap xi capacity), hit-rate, breadth, paired-diff vs K0 (cung tuan), per-year.
Forward cols CHI dung research, khong bao gio lam live filter.

Output: data/fa8l_exp/family_proxy_results_20260711.csv + panel parquet pin (plan 4.6).
"""
import os, sys, io
import numpy as np
import pandas as pd
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PROJECT = "lithe-record-440915-m9"
D = "/home/trido/thanhdt/WorkingClaude/data/fa8l_exp"
PANEL_PARQUET = f"{D}/panel_weekly_fa8l_phase1_20260711.parquet"
OUT_CSV = f"{D}/family_proxy_results_20260711.csv"
START, END = "2014-01-01", "2026-06-19"

SQL = f"""
WITH vni_history AS (
  SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time, MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
fa8_dated AS (
  SELECT f.ticker, f.time AS f_time, f.rating, f.route, f.tier AS tier8l,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings_8l AS f
),
leg_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier_leg,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
base AS (
  SELECT t.ticker, t.time,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END) AS ta_base,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.ICB_Code, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    t.profit_1M, t.profit_2M
  FROM tav2_bq.ticker AS t
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
  WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}'
    AND EXTRACT(DAYOFWEEK FROM t.time) = 4
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL
    AND t.Volume_3M_P50 * COALESCE(t.Price, t.Close) >= 1e9
),
staterc AS (
  SELECT b.time AS btime,
    ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state5
  FROM (SELECT DISTINCT time FROM base) AS b
  LEFT JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON s.time <= b.time
  GROUP BY b.time
),
rel AS (
  SELECT b.ticker, b.time, DATE_DIFF(b.time, MAX(tf.Release_Date), DAY) AS days_since_release
  FROM (SELECT DISTINCT ticker, time FROM base) AS b
  LEFT JOIN tav2_bq.ticker_financial AS tf
    ON tf.ticker = b.ticker AND tf.Release_Date <= b.time
  GROUP BY b.ticker, b.time
)
SELECT b.*, st.state5, r.days_since_release,
  fa8.rating, fa8.route, fa8.tier8l, leg.fa_tier_leg,
  fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy
FROM base AS b
LEFT JOIN staterc AS st ON st.btime = b.time
LEFT JOIN rel AS r ON r.ticker = b.ticker AND r.time = b.time
LEFT JOIN fa8_dated AS fa8
  ON fa8.ticker = b.ticker AND b.time >= fa8.f_time
 AND (fa8.next_f_time IS NULL OR b.time < fa8.next_f_time)
LEFT JOIN leg_dated AS leg
  ON leg.ticker = b.ticker AND b.time >= leg.f_time
 AND (leg.next_f_time IS NULL OR b.time < leg.next_f_time)
LEFT JOIN fin_dated AS fin
  ON fin.ticker = b.ticker AND b.time >= fin.fin_time
 AND (fin.next_fin_time IS NULL OR b.time < fin.next_fin_time)
"""

if os.path.exists(PANEL_PARQUET):
    print(f"[phase1] loading pinned panel snapshot {PANEL_PARQUET}")
    df = pd.read_parquet(PANEL_PARQUET)
else:
    from google.cloud import bigquery
    print("[phase1] querying REAL BigQuery (weekly panel, pin snapshot)...")
    client = bigquery.Client(project=PROJECT)
    job = client.query(SQL)
    df = job.result().to_dataframe()
    print(f"  rows: {len(df):,}   bytes: {job.total_bytes_processed/1e9:.2f} GB")
    df["time"] = pd.to_datetime(df["time"])
    df.to_parquet(PANEL_PARQUET, index=False)
    print(f"  -> pinned {PANEL_PARQUET}")

df["time"] = pd.to_datetime(df["time"])
df["year"] = df["time"].dt.year
df["is_oos"] = np.where(df["time"] < "2020-01-01", "IS", "OOS")
df["fresh60"] = df["days_since_release"].notna() & (df["days_since_release"] <= 60)
df["fresh30"] = df["days_since_release"].notna() & (df["days_since_release"] <= 30)
df["growth20"] = (df["np_yoy"].fillna(-99) > 0.20) | (df["rev_yoy"].fillna(-99) > 0.20)
df["growth_pos"] = (df["np_yoy"].fillna(-99) > 0) | (df["rev_yoy"].fillna(-99) > 0)
df["warn_ext"] = df["warn_ext"].fillna(False).astype(bool)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
print(f"  panel: {len(df):,} rows, rating coverage {df['rating'].notna().mean():.1%}, "
      f"legacy coverage {df['fa_tier_leg'].notna().mean():.1%}")

s5 = df["state5"]
S4 = (s5 == 4); S3 = (s5 == 3); S45 = s5.isin([4, 5]); S345 = s5.isin([3, 4, 5])
r = df["rating"]          # NaN = no 8L rating (coverage ~99% -> pass-through, per 0b keep full coverage)
leg = df["fa_tier_leg"]   # legacy A-E, NaN = legacy NULL-branch
t8 = df["tier8l"]         # 8L built-for-purpose A-E panel (doi chung F10)
ta0 = df["ta_base"]
d1_base = (df["ICB_Code"] == 8633) & (df["adv_yoy"].fillna(-99) > 0.5) \
          & S345 & df["growth_pos"]

# ---------------------------------------------------------------------------
# Config machinery. Each config -> (entry_mask, ta_adj) faithful to CASE order:
#   AVOID -> MEGA(prem) -> S_PRO -> MOMENTUM(prem) -> QUALITY(qual) -> MOMENTUM_N(ncond,fresh60)
#   -> COMPOUNDER(comp intercept) -> DVR(dvr) -> MOMENTUM_S -> ...
# Entry tiers: MEGA, MOMENTUM, MOMENTUM_N, DVR, MOMENTUM_S, RE_BACKLOG (D1 override, ta>=120).
# Overlays: mp4 EXBULL kills momentum entries (state5==5) -> momentum entries are S4-only;
#           SV_TIGHT: state3 entries need fresh60 (state 1/2 blocked by AVOID_bear anyway).
# ---------------------------------------------------------------------------
def build_entries(avoid, prem, qual, comp, dvr_c, ncond, d1_c, ta_adj):
    """Returns (entry_bool, ta_series). All args are boolean Series aligned to df (or None)."""
    ta = ta0 + ta_adj if ta_adj is not None else ta0
    ok = ~avoid
    # state-4 momentum chain (mp4: state5 EXBULL suppressed)
    mega   = ok & S4 & (ta >= 170) & prem
    s_pro  = ok & S4 & (ta >= 170) & ~mega                      # intercept (non-entry)
    mom    = ok & S4 & (ta >= 155) & ~mega & ~s_pro & prem
    qualm  = ok & S4 & (ta >= 155) & ~mega & ~s_pro & ~mom & qual  # intercept
    used = mega | s_pro | mom | qualm
    # NEUTRAL fresh momentum
    mom_n  = ok & S3 & (ta >= 155) & df["fresh60"] & ncond & ~used
    used = used | mom_n
    # compounder intercept (s345)
    compb  = ok & S345 & comp & (df["pe_z"] < -0.5) & (ta >= 95) & ~df["warn_ext"] & ~used
    used = used | compb
    # deep value recovery (s45; mp4 does not suppress DVR)
    dvr    = ok & S45 & dvr_c & (ta >= 100) & df["growth20"] & ~used
    used = used | dvr
    # momentum_S (S4 only after mp4)
    mom_s  = ok & S4 & (ta >= 140) & ~used
    entry = mega | mom | mom_n | dvr | mom_s
    # D1 override: RE_BACKLOG_BUY (overrides any bucket incl non-entry; harness applies pre-SV_TIGHT)
    d1 = d1_base & d1_c & (ta >= 120) & ~avoid
    entry = entry | d1
    # SV_TIGHT: state3 entries require fresh60 (mirror harness keep-rule; s45 unfiltered)
    entry = entry & np.where(S3, df["fresh60"], True)
    return entry, ta

TRUE = pd.Series(True, index=df.index)
FALSE = pd.Series(False, index=df.index)
NULLR = r.isna()

# T7 adjust variants
adj_legacy = pd.Series(0.0, index=df.index)
adj_legacy[(df["sec"] == 8) & (leg == "D")] += 10
adj_legacy[(df["sec"] == 8) & (leg == "A")] -= 10
adj_sec8l = pd.Series(0.0, index=df.index)
adj_sec8l[(df["route"] == "SECURITIES") & (r <= 2)] += 10
adj_sec8l[(df["route"] == "SECURITIES") & (r >= 4)] -= 10

# avoid variants (NULL rating never avoided -> full-coverage principle keeps pass-through tiny)
av5   = (r == 5)                                   # global avoid r5 (analog E)
av45s = np.where(S45, r >= 4, r == 5)              # strict in s45, r5 elsewhere
av45s = pd.Series(av45s, index=df.index) & r.notna()
avsec = av5 | ((df["route"] == "SECURITIES") & (r >= 4))   # r5 + fragile securities

# momentum premium variants (who reaches MEGA/MOMENTUM at ta>=155/170 in s45)
prem_all = TRUE                       # ta-only: no interception (S_PRO/QUALITY empty)
prem_le3 = (r <= 3) | NULLR           # fragile r4 intercepted at ta>=155 (chase-zone gate)
qual_none = FALSE
qual_r4   = (r == 4)                  # r4 -> QUALITY intercept (used with prem_le3)

# MOMENTUM_N variants
n_any  = TRUE
n_flip = (r >= 3)                     # NEUTRAL flip-play (OOS-driven, high risk)
n_strict = (r <= 3) | NULLR           # adversarial control for the flip

# compounder intercept (fixed rating<=2 per DC-book precedent; NULL never intercepted)
comp8l = (r <= 2)
comp_leg = leg.isin(["A", "B"])

# DVR variants
dvr_r3 = (r == 3)
dvr_leg = (leg == "C")

# D1 variants
d1_le4 = (r <= 4) | NULLR
d1_leg = leg.isin(["C", "D"])
d1_mid = r.isin([3, 4])

CONFIGS = {
  # control (KHONG dem trial): legacy production semantics
  "K0_control_legacy": dict(avoid=(leg == "E"), prem=leg.isin(["C","D"]), qual=leg.isin(["A","B"]),
                            comp=comp_leg, dvr_c=dvr_leg, ncond=leg.isin(["C","D"]),
                            d1_c=d1_leg, ta_adj=adj_legacy),
  # F1 spine: gate-lean (avoid r5 only, ta-only momentum, no N cond, drop T7, DVR=r3, D1<=4)
  "F1_gate_lean":      dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F2: strict s45 fragility gate (avoid r>=4 in s45)
  "F2_gate_strict45":  dict(avoid=av45s, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F3: graded chase-zone gate (r5 avoided; r4 blocked only at ta>=155 via QUALITY intercept)
  "F3_gate_chasezone": dict(avoid=av5, prem=prem_le3, qual=qual_r4, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F4: F1 + SECURITIES route x rating ta-adjust (0c: sec IC -0.22 IS / -0.17 OOS)
  "F4_sec_adjust":     dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_any, d1_c=d1_le4, ta_adj=adj_sec8l),
  # F5: F1 + NEUTRAL flip (MOMENTUM_N requires r>=3; OOS-driven probe)
  "F5_n_flip":         dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_flip, d1_c=d1_le4, ta_adj=None),
  # F6: adversarial control cua F5 (MOMENTUM_N r<=3) — neu F6>=F5, flip la noise
  "F6_n_strict":       dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_strict, d1_c=d1_le4, ta_adj=None),
  # F7: F1 bo DVR (test bucket con earn keep duoi 8L khong)
  "F7_dvr_merge":      dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=FALSE, ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F8: avoid r5 + fragile-SECURITIES avoid (route-conditional gate)
  "F8_sec_avoid":      dict(avoid=avsec, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F9: max-OOS-evidence combo (lean gate + sec adjust + N flip)
  "F9_lean_combo":     dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_flip, d1_c=d1_le4, ta_adj=adj_sec8l),
  # F11: all-conservative combo (strict s45 gate + N strict + sec adjust)
  "F11_conservative":  dict(avoid=av45s, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=dvr_r3, ncond=n_strict, d1_c=d1_le4, ta_adj=adj_sec8l),
  # F12 (RESERVE SLOT — kich hoat 2026-07-11 sau composition check, khai bao truoc khi chay):
  # F1 + DVR rating in {2,3}. Ly do: DVR ~77% entry rows -> truc don bay cao nhat; 0c hit r2>r3.
  "F12_dvr_23":        dict(avoid=av5, prem=prem_all, qual=qual_none, comp=comp8l,
                            dvr_c=r.isin([2, 3]), ncond=n_any, d1_c=d1_le4, ta_adj=None),
  # F10 doi chung: tier8l A-E panel, legacy bucket shapes + avoid-E fix theo context (s45 only)
  "F10_tier8l_ctl":    dict(avoid=pd.Series(np.where(S45, t8.isin(["D","E"]), t8 == "E"),
                                            index=df.index) & t8.notna(),
                            prem=t8.isin(["C","D"]), qual=t8.isin(["A","B"]),
                            comp=t8.isin(["A","B"]), dvr_c=(t8 == "C"), ncond=t8.isin(["C","D"]),
                            d1_c=t8.isin(["C","D"]), ta_adj=None),
}

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def weekly_stats(sub, ta, topn=None):
    """Per-week equal-weight mean fwd; optional top-N by ta. Returns dict of weekly series."""
    x = sub.copy(); x["_ta"] = ta[sub.index]
    if topn:
        x = x.sort_values(["time", "_ta"], ascending=[True, False]).groupby("time").head(topn)
    g1 = x.groupby("time")["profit_1M"].mean()
    g2 = x.groupby("time")["profit_2M"].mean()
    n = x.groupby("time").size()
    hit2 = x.groupby("time")["profit_2M"].apply(lambda v: (v > 0).mean())
    return dict(w1=g1, w2=g2, n=n, hit2=hit2, rows=x)

results, weekly2 = [], {}
for name, cfg in CONFIGS.items():
    entry, ta = build_entries(**cfg)
    sub = df[entry & df["profit_2M"].notna()]
    st_all = weekly_stats(sub, ta)
    st_20 = weekly_stats(sub, ta, topn=20)
    weekly2[name] = st_20["w2"]
    rec = {"config": name}
    for per in ["IS", "OOS"]:
        m = sub["is_oos"] == per
        wk1, wk2 = st_all["w1"], st_all["w2"]
        wmask = wk2.index.isin(sub.loc[m, "time"].unique())
        t1, t2 = st_20["w1"], st_20["w2"]
        rec[f"{per}_nweek"] = int(wmask.sum())
        rec[f"{per}_breadth"] = round(float(st_all["n"][wmask].mean()), 1) if wmask.sum() else np.nan
        rec[f"{per}_fwd1M"] = round(float(wk1[wmask].mean()), 3) if wmask.sum() else np.nan
        rec[f"{per}_fwd2M"] = round(float(wk2[wmask].mean()), 3) if wmask.sum() else np.nan
        rec[f"{per}_top20_2M"] = round(float(t2[t2.index.isin(wk2[wmask].index)].mean()), 3) if wmask.sum() else np.nan
        rec[f"{per}_hit2M"] = round(float(st_20["rows"].loc[st_20["rows"]["is_oos"] == per, "profit_2M"].gt(0).mean()), 4)
    results.append(rec)

res = pd.DataFrame(results)

# paired diff vs control (top-20 2M, same weeks)
k0 = weekly2["K0_control_legacy"]
diffs = []
for name in CONFIGS:
    if name == "K0_control_legacy":
        continue
    w = weekly2[name]
    common = k0.index.intersection(w.index)
    dcommon = (w[common] - k0[common]).dropna()
    per = pd.Series(np.where(dcommon.index < pd.Timestamp("2020-01-01"), "IS", "OOS"), index=dcommon.index)
    row = {"config": name}
    for p in ["IS", "OOS"]:
        dd = dcommon[per == p]
        # NW-lite: horizon 2M ~ 8 tuan overlap -> scale t bang sqrt(8) (conservative)
        t = dd.mean() / (dd.std() / np.sqrt(len(dd))) / np.sqrt(8) if len(dd) > 20 else np.nan
        row[f"{p}_pairdiff_2M"] = round(float(dd.mean()), 3)
        row[f"{p}_t_adj"] = round(float(t), 2) if t == t else np.nan
    # per-year paired diff (top20 2M) — LOO sanity
    ydiff = dcommon.groupby(dcommon.index.year).mean().round(3)
    row["per_year_diff"] = ";".join(f"{y}:{v}" for y, v in ydiff.items())
    diffs.append(row)
dres = pd.DataFrame(diffs)

out = res.merge(dres, on="config", how="left")
out.to_csv(OUT_CSV, index=False)
pd.set_option("display.width", 300)
print("\n===== FAMILY PROXY RESULTS (weekly entry-set, top-20 by ta, fwd profit_2M) =====")
cols = ["config","IS_nweek","IS_breadth","IS_fwd2M","IS_top20_2M","IS_hit2M",
        "OOS_nweek","OOS_breadth","OOS_fwd2M","OOS_top20_2M","OOS_hit2M",
        "IS_pairdiff_2M","IS_t_adj","OOS_pairdiff_2M","OOS_t_adj"]
print(out[cols].to_string(index=False))
print("\n----- per-year paired diff vs K0 (top20 2M) -----")
for _, rw in dres.iterrows():
    print(f"{rw['config']:<20} {rw['per_year_diff']}")
print(f"\n-> {OUT_CSV}")
print("DONE phase1 proxy.")
