# -*- coding: utf-8 -*-
"""
clean_vnindex_pe.py
===================
Clean + interpolate VNINDEX_PE from BQ for use in 5-state v2g system.

Issues handled:
  1. Filter 9 bad rows (PE < 3) in 2025 monthly snapshots — replace with NaN then interpolate
  2. Linear interpolate small gaps (≤ 5 trading days) within Bloomberg era 2006-2010
  3. Leave large gaps NaN (e.g., Jan-Mar 2006, Jan-Mar 2007)
  4. Calibrate pre-2011 Bloomberg PE to post-2011 source scale (multiplicative)
     - Reason: boundary 2010-12→2011-01 has +14% PE jump while Close +4% → +9.3% data shift
  5. Add `pe_quality` column:
        0 = raw clean
        1 = interpolated (≤ 5 day gap)
        2 = calibrated pre-2011 Bloomberg
        3 = missing (pre-2006-03 or gaps too large to interpolate)

Output: updates cached file `vnindex_full_2000_2026.csv` with new cols
        `VNINDEX_PE_clean` (calibrated + interpolated) and `pe_quality`.
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd
from io import StringIO

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"

def bq(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); p = f.name
    try:
        cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=200000 < "{p}"'
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(p)
    return pd.read_csv(StringIO(out.stdout))

# ════════════════════ 1. Pull fresh data ════════════════════
print("Pulling fresh VNINDEX OHLCV + PE from BQ ...")
vni = bq("""
SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume, t.VNINDEX_PE
FROM tav2_bq.ticker AS t
WHERE t.ticker = "VNINDEX"
ORDER BY t.time
""")
vni["time"] = pd.to_datetime(vni["time"])
print(f"  rows={len(vni)}  {vni['time'].min().date()} → {vni['time'].max().date()}")

# Append ticker_1m if newer
last_t = vni["time"].max()
try:
    add = bq(f"""
    SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume, t.VNINDEX_PE
    FROM tav2_bq.ticker_1m AS t
    WHERE t.ticker = "VNINDEX" AND t.time > "{last_t.strftime('%Y-%m-%d')}"
    ORDER BY t.time
    """)
    if len(add) > 0:
        add["time"] = pd.to_datetime(add["time"])
        vni = pd.concat([vni, add], ignore_index=True).drop_duplicates("time").sort_values("time").reset_index(drop=True)
        print(f"  Appended {len(add)} rows from ticker_1m")
except Exception:
    pass

# Numeric
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE"]:
    vni[c] = pd.to_numeric(vni[c], errors="coerce")

# OHLC outlier clamp (e.g., 2026-03-23 Close=1.59 bad row)
for col in ["Close","Open","High","Low"]:
    a = vni[col].values.astype(float)
    for i in range(1, len(a)):
        if a[i-1] > 0 and a[i] > 0 and abs(a[i]/a[i-1]-1) > 0.5:
            a[i] = a[i-1]
    vni[col] = a

# ════════════════════ 2. PE quality flags init ════════════════════
print("\n=== Cleaning PE ===")
pe_raw = vni["VNINDEX_PE"].values.copy()
n = len(pe_raw)
quality = np.where(np.isnan(pe_raw), 3, 0).astype(int)   # 3=missing, 0=raw

# 2a. Filter bad rows (PE < 3)
bad_mask = (~np.isnan(pe_raw)) & (pe_raw < 3)
n_bad = int(bad_mask.sum())
print(f"  Bad rows PE<3 (set to NaN, will interpolate): {n_bad}")
pe_raw[bad_mask] = np.nan
quality[bad_mask] = 3  # mark missing pending interpolation

# ════════════════════ 3. Calibration: pre-2011 Bloomberg → new source scale ════════════════════
# Compute calibration factor from boundary observation:
#   Dec 2010 mean PE / Jan 2011 mean PE, adjusted by Close ratio
mask_dec2010 = (vni["time"] >= "2010-12-01") & (vni["time"] <= "2010-12-31")
mask_jan2011 = (vni["time"] >= "2011-01-04") & (vni["time"] <= "2011-01-31")
pe_dec = pe_raw[mask_dec2010.values]; pe_dec = pe_dec[~np.isnan(pe_dec)]
pe_jan = pe_raw[mask_jan2011.values]; pe_jan = pe_jan[~np.isnan(pe_jan)]
cl_dec = vni.loc[mask_dec2010, "Close"].mean()
cl_jan = vni.loc[mask_jan2011, "Close"].mean()
if len(pe_dec) > 5 and len(pe_jan) > 5:
    pe_ratio    = pe_jan.mean() / pe_dec.mean()
    close_ratio = cl_jan / cl_dec
    pure_shift  = pe_ratio / close_ratio
    factor      = pure_shift
    print(f"  Boundary measurement:")
    print(f"    Dec 2010 PE mean = {pe_dec.mean():.3f}  Close mean = {cl_dec:.1f}")
    print(f"    Jan 2011 PE mean = {pe_jan.mean():.3f}  Close mean = {cl_jan:.1f}")
    print(f"    PE ratio = {pe_ratio:.4f}  Close ratio = {close_ratio:.4f}")
    print(f"    Pure PE shift = {pure_shift:.4f}  → calibration factor = {factor:.4f}")
else:
    factor = 1.0
    print("  Boundary data insufficient — no calibration applied")

# Apply calibration to all pre-2011-01-04 raw PE
pre_2011 = (vni["time"] < "2011-01-04").values
pe_cal = pe_raw.copy()
n_cal = 0
for i in range(n):
    if pre_2011[i] and not np.isnan(pe_cal[i]):
        pe_cal[i] = pe_cal[i] * factor
        quality[i] = 2   # calibrated
        n_cal += 1
print(f"  Calibrated {n_cal} pre-2011 rows (multiplied by {factor:.4f})")

# ════════════════════ 4. Interpolate gaps ════════════════════
# Quality codes:
#   0 = raw post-2011 (fully reliable)
#   1 = short-gap interpolated (≤ 5d) — high confidence
#   2 = pre-2011 Bloomberg, calibrated (already set above)
#   3 = long-gap interpolated (low confidence, use with caution)
#   4 = missing (pre-2006-03)
print("\n  Interpolating gaps ...")
pe_clean = pe_cal.copy()
i = 0; n_short = 0; n_long = 0; n_missing = 0
while i < n:
    if np.isnan(pe_clean[i]):
        j = i
        while j < n and np.isnan(pe_clean[j]):
            j += 1
        gap_len = j - i
        left_idx  = i - 1
        right_idx = j
        if left_idx >= 0 and right_idx < n and not np.isnan(pe_clean[left_idx]) and not np.isnan(pe_clean[right_idx]):
            lv = pe_clean[left_idx]; rv = pe_clean[right_idx]
            # ALL gaps with valid endpoints get interpolated; mark quality by length
            for k in range(i, j):
                frac = (k - left_idx) / (right_idx - left_idx)
                pe_clean[k] = lv + frac * (rv - lv)
                if gap_len <= 5:
                    quality[k] = 1; n_short += 1
                else:
                    quality[k] = 3; n_long += 1   # low-confidence long-gap interp
        else:
            # Cannot interpolate (start or end of series) — mark missing
            for k in range(i, j):
                quality[k] = 4; n_missing += 1
        i = j
    else:
        i += 1
print(f"  Short-gap interp (≤5d, quality=1): {n_short} rows")
print(f"  Long-gap  interp (>5d, quality=3): {n_long} rows")
print(f"  Truly missing (quality=4)        : {n_missing} rows")

# ════════════════════ 5. Save and summary ════════════════════
vni["VNINDEX_PE_raw"]   = pe_raw     # raw (calibration not applied)
vni["VNINDEX_PE_clean"] = pe_clean   # calibrated + interpolated
vni["pe_quality"]       = quality

# Also handle breadth: pull from BQ for completeness
print("\nPulling breadth (% tickers above MA50) ...")
br = bq("""
SELECT t.time,
       SAFE_DIVIDE(SUM(CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END), COUNT(*)) AS breadth
FROM tav2_bq.ticker AS t
WHERE t.MA50 IS NOT NULL AND t.Close IS NOT NULL
GROUP BY t.time
ORDER BY t.time
""")
br["time"] = pd.to_datetime(br["time"])
vni = vni.merge(br, on="time", how="left", suffixes=("", "_new"))
if "breadth_new" in vni.columns:
    vni["breadth"] = vni["breadth_new"]
    vni = vni.drop(columns=["breadth_new"])

# Save
out_path = os.path.join(WORKDIR, "data/vnindex_full_2000_2026.csv")
backup_path = os.path.join(WORKDIR, "data/vnindex_full_2000_2026_pre_pe_clean.csv")
if os.path.exists(out_path):
    import shutil
    shutil.copy2(out_path, backup_path)
    print(f"\n  Backup: {os.path.basename(backup_path)}")
vni.to_csv(out_path, index=False)
print(f"  Saved → {out_path}  ({len(vni)} rows)")

# ════════════════════ 6. Summary table ════════════════════
print("\n" + "="*78)
print("PE QUALITY SUMMARY")
print("="*78)
print(f"{'Quality':<6} {'Code':<6} {'Meaning':<40} {'n':>8} {'%':>7}")
labels = {0: "Raw (post-2011, fully reliable)",
          1: "Short-gap interpolated (≤5d)",
          2: "Pre-2011 Bloomberg, calibrated ×{:.3f}".format(factor),
          3: "Long-gap interpolated (low confidence)",
          4: "Missing (pre-2006-03, no anchor)"}
stars = {0: "★★★★", 1: "★★★", 2: "★★", 3: "★", 4: "—"}
for q in [0, 1, 2, 3, 4]:
    cnt = int(np.sum(quality == q))
    pct = cnt/n*100
    print(f"{stars[q]:<6} {q:<6} {labels[q]:<48} {cnt:>8} {pct:>6.1f}%")

# Distribution by era after cleaning
print("\nPE distribution by era after cleaning:")
era_2006_2010 = (vni["time"] < "2011-01-04").values
era_2011_now  = (vni["time"] >= "2011-01-04").values
for era_name, era_mask in [("2006-2010 (Bloomberg, calibrated)", era_2006_2010),
                            ("2011-2026 (new source, raw)", era_2011_now)]:
    pe_arr = vni.loc[era_mask, "VNINDEX_PE_clean"].dropna().values
    if len(pe_arr) == 0: continue
    print(f"  {era_name}: n={len(pe_arr)}, "
          f"min={pe_arr.min():.2f}, P10={np.percentile(pe_arr,10):.2f}, "
          f"P50={np.percentile(pe_arr,50):.2f}, P90={np.percentile(pe_arr,90):.2f}, "
          f"max={pe_arr.max():.2f}")

# Check boundary is now continuous
boundary_dec = vni.loc[mask_dec2010, "VNINDEX_PE_clean"].mean()
boundary_jan = vni.loc[mask_jan2011, "VNINDEX_PE_clean"].mean()
print(f"\nBoundary check after calibration:")
print(f"  Dec 2010 mean PE_clean = {boundary_dec:.3f}")
print(f"  Jan 2011 mean PE_clean = {boundary_jan:.3f}")
print(f"  ratio = {boundary_jan/boundary_dec:.4f} (was 1.140 before calibration)")
print(f"  Close ratio = {close_ratio:.4f} (target — close to this means continuous)")
