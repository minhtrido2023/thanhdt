#!/usr/bin/env python3
"""build_rating_8l_history.py — POINT-IN-TIME 8L quality rating (1-5) per ticker-quarter.

The live rating_8l.py computes ONE current snapshot. For a prod-spec backtest of the
distress-exclusion (B) and regime-conditional sizing (C) overlays we need the rating
AS IT WOULD HAVE BEEN KNOWN on each historical date — i.e. point-in-time, no look-ahead.

Approach: the rating is driven by quarterly fundamentals (ROIC/ROE/leverage/cash/FSCORE/
GPM-moat), all present in tav2_bq.ticker_financial. So compute the rating ONCE per
(ticker, quarter), stamp it with the publication date (Release_Date — when the market
actually had the numbers), and forward-fill to daily in the consumer via merge_asof.

Limitations vs the live rating (documented, conservative):
  - BANK (ICB 8355) and POWER lenses are vnstock/current-only (no NPL/CAR history) →
    rated 3 (neutral) across all history. Effect: banks/power are NEVER distress-excluded
    nor down-weighted → the overlay's effect is measured ONLY on names where we have a
    genuine historical fundamental read (COMPOUNDER / CYCLICAL / REALESTATE / INSURANCE /
    SECURITIES). This is the correct conservative choice for an insurance-style gate.
  - Route classification (commodity map, holdings/RE overrides, power_set) is structural
    and applied across all history for the ticker.

Output: data/rating_8l_history.pkl  columns [ticker, eff_time, quarter, route, rating]
Usage:  python build_rating_8l_history.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))

# ---- route sets (structural, ported from rating_8l.py) ----
COMMODITY_MAP = {
 "DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap",
 "CSV":"caustic_soda"}  # CSV = chlor-alkali (NaOH+chlorine+PVC), NOT dap fertilizer — own caustic-soda cycle
SUGAR_SET = {"SLS","SBT","LSS","KTS","QNS"}
HOLDING_OVERRIDE    = {"REE"}
REALESTATE_OVERRIDE = {"HHS"}
INSURANCE_ICB  = lambda c: pd.notna(c) and 8530 <= c <= 8579
SECURITIES_ICB = lambda c: pd.notna(c) and 8770 <= c <= 8779
# 5F-audited moat governance (user 2026-06-14 "siết A-mềm", identical to rating_8l_history.py): the quant
# moat +1 notch is honored ONLY for a 5F-WIDE moat (moat_tier); registry NARROW/NONE -> no notch; absent ->
# notch kept (quant, audit dần). PIT: no-notch override applies only to eff >= MOAT_GOV_CUTOFF (deep history
# keeps quant proxy). Quant-fortress (prelim 1) moat-independent, unaffected.
MOAT_TIER = {}
MOAT_GOV_CUTOFF = pd.Timestamp("2025-06-01")


def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=10000000',
                           capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip(): raise RuntimeError("bq no rows. stderr:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))


# ─── ported scorecard logic (identical thresholds to rating_8l.py) ──────────────
def real_lev(r):
    v = r.get("STLTDebt_Eq_P0", np.nan)
    return v if pd.notna(v) else r.get("Debt_Eq_P0", np.nan)

def moat_tag(r, roe5y):
    gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]
    gpms = [g for g in gpms if pd.notna(g)]
    if not gpms: return "WEAK"
    gmean = float(np.mean(gpms))
    cv = (float(np.std(gpms))/gmean) if gmean > 0 else 9.0
    hi_level  = gmean >= 0.25
    stable    = (len(gpms) >= 4 and cv <= 0.20)
    hi_roe    = pd.notna(roe5y) and roe5y >= 0.15
    if gmean < 0.15 or (pd.notna(roe5y) and roe5y < 0.10): return "WEAK"
    if hi_level and stable and hi_roe: return "STRONG"
    if (hi_level and (stable or hi_roe)) or (stable and hi_roe): return "MODERATE+"
    return "MODERATE"

def core_score(r):
    ttm_cfo = sum(r.get("CF_OA_P%d"%i, np.nan) for i in range(4))
    ttm_np  = sum(r.get("NP_P%d"%i,    np.nan) for i in range(4))
    cfo_np  = (ttm_cfo/ttm_np) if (pd.notna(ttm_np) and ttm_np != 0) else np.nan
    roic, roicm, roe_tr, de, fs = r.get("ROIC3Y",np.nan), r.get("ROIC_Min3Y",np.nan), r.get("ROE_Trailing", np.nan), real_lev(r), r.get("FSCORE", np.nan)
    s  = (2 if roic>=0.15 else 1 if roic>=0.10 else 0) if pd.notna(roic) else 0
    s += (2 if roicm>=0.10 else 1 if roicm>=0.05 else 0) if pd.notna(roicm) else 0
    s += (2 if roe_tr>=0.18 else 1 if roe_tr>=0.12 else 0) if pd.notna(roe_tr) else 0
    s += (2 if de<=0.3 else 1 if de<=1.0 else 0) if pd.notna(de) else 0
    s += (2 if (pd.notna(cfo_np) and cfo_np>=1.0 and ttm_cfo>0) else 1 if (pd.notna(cfo_np) and cfo_np>=0.7) else 0)
    s += (2 if fs>=8 else 1 if fs>=6 else 0) if pd.notna(fs) else 0
    return s, (round(cfo_np,2) if pd.notna(cfo_np) else np.nan), ttm_np

def redflag(r, ttm_np):
    rs = []
    if pd.notna(ttm_np) and ttm_np < 0: rs.append("NP_TTM<0")
    lev = real_lev(r)
    if pd.notna(lev) and lev > 3: rs.append("debt/eq>3")
    return ",".join(rs)

def bin_core(s):
    return 1 if s>=10 else 2 if s>=7 else 3 if s>=4 else 4 if s>=2 else 5

def eq_flag(r):
    """Earnings-quality gate for COMPOUNDER/CYCLICAL (PIT version, identical to rating_8l.py.eq_flag):
    NP>=0.9*GP (or NP+ on gross loss) = earnings not from core operations -> cap speculative(4);
    escalate to impaired(5) when also CF_OA_5Y<=0 (chronically non-cash). Fail-safe on missing data."""
    ttm_np = sum(r.get("NP_P%d"%i, np.nan) for i in range(4))
    if not (pd.notna(ttm_np) and ttm_np > 0): return 0
    lev = real_lev(r)                                    # leverage precondition (spares net-cash VEA/PHR)
    if not (pd.notna(lev) and lev >= 0.25): return 0
    rev = [r.get("Revenue_P%d"%i, np.nan) for i in range(4)]
    gpm = [r.get("GPM_P%d"%i, np.nan) for i in range(4)]
    if any(pd.isna(x) for x in rev + gpm): return 0
    ttm_gp = sum(g*v for g, v in zip(gpm, rev))
    if not ((ttm_gp <= 0) or (ttm_np/ttm_gp >= 0.90)): return 0
    cf5 = r.get("CF_OA_5Y", np.nan)
    return 5 if (pd.notna(cf5) and cf5 <= 0) else 4

def rate_securities(r):
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe
    ttm_np = sum(r.get("NP_P%d"%i, np.nan) for i in range(4))
    if (pd.notna(roe) and roe < 0) or (pd.notna(ttm_np) and ttm_np < 0): return 5
    if pd.notna(roe) and roe>=0.13 and pd.notna(r3) and r3>=0.11: return 2
    if pd.notna(roe) and roe>=0.09 and pd.notna(r3) and r3>=0.07: return 3
    if pd.notna(roe) and roe>=0.05: return 4
    return 5

def rate_insurance(r):
    roe_tr = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe_tr): roe_tr = r.get("ROE_Min3Y", np.nan)
    if pd.notna(roe_tr) and roe_tr < 0: return 5
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe_tr
    if pd.notna(roe_tr) and roe_tr>=0.15 and pd.notna(r3) and r3>=0.12: return 1
    if pd.notna(roe_tr) and roe_tr>=0.11 and pd.notna(r3) and r3>=0.09: return 2
    if pd.notna(roe_tr) and roe_tr>=0.07: return 3
    if pd.notna(roe_tr): return 4
    return 4

def rate_realestate(r, cfo_np, ttm_np):
    if pd.notna(ttm_np) and ttm_np < 0: return 5
    roe_tr, roic, de, fs, roicm = r.get("ROE_Trailing",np.nan), r.get("ROIC3Y",np.nan), real_lev(r), r.get("FSCORE", np.nan), r.get("ROIC_Min3Y",np.nan)
    unearn, assets = r.get("UnearnRev_P0",np.nan), r.get("totalAsset_P0",np.nan)
    pipeline = (unearn/assets) if (pd.notna(unearn) and pd.notna(assets) and assets>0) else np.nan
    s  = (2 if (pd.notna(roe_tr) and roe_tr>=0.18) else 1 if (pd.notna(roe_tr) and roe_tr>=0.10) else 0)
    s += (2 if (pd.notna(roic) and roic>=0.12) else 1 if (pd.notna(roic) and roic>=0.07) else 0)
    s += (2 if (pd.notna(de) and de<=0.5) else 1 if (pd.notna(de) and de<=1.5) else 0)
    s += (1 if (pd.notna(cfo_np) and cfo_np>=0.8) else 0)
    s += (1 if (pd.notna(fs) and fs>=6) else 0)
    s += (1 if (pd.notna(roicm) and roicm>=0) else 0)
    s += (1 if (pd.notna(pipeline) and pipeline>=0.15) else 0)
    return 2 if s>=6 else 3 if s>=4 else 4

# BANK_POWER_MODE: "neutral" (=3, no historical lens) or "roe" (point-in-time ROE bins).
# The live bank/power lenses (NPL/CAR/debt-lifecycle) are vnstock current-only -> can't be
# back-tested point-in-time. "roe" approximates them honestly from ROE history (in ticker_financial):
# it scores the FRANCHISE-strength axis (the base of the live bank lens) without the asset-quality
# upgrade to 1-2 (which needs NPL/coverage we don't have historically). Conservative & no look-ahead.
BANK_POWER_MODE = os.environ.get("BANK_POWER_MODE", "neutral")

def rate_fin_roe(r):
    """ROE-based bins for bank/power (point-in-time, from ROE_Trailing/ROE3Y history).
    Mirrors the live bank lens's ROE base (no NPL/CAR upgrade): <8% impaired franchise."""
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe
    if pd.isna(roe): return 3                       # no data -> neutral
    if roe < 0.08: return 5                          # weak franchise
    if roe >= 0.15 and pd.notna(r3) and r3 >= 0.12: return 2   # cap 2 w/o asset-quality lens
    if roe >= 0.12: return 3
    return 4

def rate_row(r):
    route = r["route"]
    s, cfo_np, ttm_np = core_score(r)
    moat = moat_tag(r, r.get("ROE5Y", np.nan))
    rf = redflag(r, ttm_np)
    if route == "SECURITIES":   return rate_securities(r)
    if route == "INSURANCE":    return rate_insurance(r)
    if route == "REALESTATE":   return rate_realestate(r, cfo_np, ttm_np)
    if route == "BANK":         return rate_fin_roe(r) if BANK_POWER_MODE=="roe" else 3
    if route == "POWER":        return rate_fin_roe(r) if BANK_POWER_MODE=="roe" else 3
    if route == "CYCLICAL":
        if rf: return 5
        if pd.notna(real_lev(r)) and real_lev(r) > 1.5: return 5
        prelim = bin_core(s)
        fortress = (pd.notna(real_lev(r)) and real_lev(r)<=0.2 and pd.notna(r.get("ROIC3Y")) and r["ROIC3Y"]>=0.20)
        rating = prelim if prelim>=2 else (1 if fortress else 2)
        return max(rating, eq_flag(r))          # earnings-quality gate (downgrade-only)
    # COMPOUNDER
    if rf: return 5
    prelim = bin_core(s)
    rating = prelim
    if moat=="STRONG" and prelim in (2,3):
        _eff = pd.to_datetime(r.get("Release_Date"), errors="coerce")
        _tier = MOAT_TIER.get(r.get("ticker"))
        _revoke = (pd.notna(_eff) and _eff >= MOAT_GOV_CUTOFF) and (_tier is not None and _tier != "WIDE")
        if not _revoke: rating = prelim-1
    if rating == 5: rating = 4       # profitable-but-thin -> speculative(4), not impaired(5)
    return max(rating, eq_flag(r))              # earnings-quality gate (downgrade-only, post-moat)


def main():
    print("[1] Pulling ticker_financial quarterly history + ICB...")
    fin = bq("""
    SELECT f.ticker, f.time, f.Release_Date, f.quarter,
      f.ROE5Y, f.ROIC3Y, f.ROIC_Min3Y, f.ROE_Trailing, f.ROE3Y, f.ROE_Min3Y,
      f.STLTDebt_Eq_P0, f.Debt_Eq_P0, f.FSCORE,
      f.GPM_P0,f.GPM_P1,f.GPM_P2,f.GPM_P3,f.GPM_P4,f.GPM_P5,f.GPM_P6,f.GPM_P7,
      f.CF_OA_P0,f.CF_OA_P1,f.CF_OA_P2,f.CF_OA_P3, f.CF_OA_5Y,
      f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,
      f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
      f.UnearnRev_P0, f.totalAsset_P0
    FROM tav2_bq.ticker_financial AS f
    WHERE f.time >= DATE '2012-01-01'
    """)
    icb = bq("""SELECT t.ticker, APPROX_TOP_COUNT(t.ICB_Code, 1)[OFFSET(0)].value AS ICB_Code
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL GROUP BY t.ticker""")
    fin = fin.merge(icb, on="ticker", how="left")
    print(f"  financial rows: {len(fin):,}  tickers: {fin['ticker'].nunique()}")

    # structural route sets
    try:
        bank_set = set(pd.read_csv(os.path.join(WORKDIR,"data","bank_lens_v3.csv"))["ticker"])
    except Exception: bank_set = set()
    try:
        power_set = set(pd.read_csv(os.path.join(WORKDIR,"data","power_lens.csv"))["ticker"]) - bank_set
    except Exception: power_set = set()

    def route_of(r):
        tk, c = r["ticker"], r.get("ICB_Code")
        if tk in HOLDING_OVERRIDE: return "COMPOUNDER"
        if tk in REALESTATE_OVERRIDE: return "REALESTATE"
        if tk in bank_set or c == 8355: return "BANK"
        if INSURANCE_ICB(c): return "INSURANCE"
        if SECURITIES_ICB(c): return "SECURITIES"
        if tk in power_set: return "POWER"
        if tk in COMMODITY_MAP or tk in SUGAR_SET: return "CYCLICAL"
        if c == 8633: return "REALESTATE"
        return "COMPOUNDER"
    fin["route"] = fin.apply(route_of, axis=1)

    global MOAT_TIER
    try:
        _mg = pd.read_csv(os.path.join(WORKDIR,"data","moat_tags.csv"))
        MOAT_TIER = dict(zip(_mg["ticker"], _mg["moat_tier"]))
    except Exception as e:
        print("moat_tags load fail (quant ungated):", e); MOAT_TIER = {}

    print("[2] Computing rating per quarter...")
    fin["rating"] = fin.apply(rate_row, axis=1).astype(int)

    # publication date (no look-ahead): Release_Date if present, else fiscal-end + 45 calendar days
    fin["time"] = pd.to_datetime(fin["time"])
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"], errors="coerce")
    fin["eff_time"] = fin["Release_Date"].fillna(fin["time"] + pd.Timedelta(days=45))

    out = fin[["ticker","eff_time","quarter","route","rating"]].sort_values(["ticker","eff_time"]).reset_index(drop=True)
    # de-dup: keep the latest publication per (ticker, eff_time) in case of restatements on same day
    out = out.drop_duplicates(subset=["ticker","eff_time"], keep="last")
    # FORENSIC EXCLUDE (2026-06-20, date-aware, NO hindsight): a human-flagged 'exclude' name (related-party/
    # manipulation, data/forensic_flags.csv) -> rating 5 (fails gate<=3) ONLY from its flag date forward, so
    # every fa_ratings_8l consumer (custom30, golive sizing, audits) drops it going forward; history untouched.
    try:
        _ff = pd.read_csv(os.path.join(WORKDIR,"data","forensic_flags.csv"))
        for _, fr in _ff.iterrows():
            if str(fr["severity"]).strip() == "exclude":
                _fd = pd.Timestamp(fr["date"]); _m = (out["ticker"] == fr["ticker"]) & (out["eff_time"] >= _fd)
                out.loc[_m, "rating"] = 5
                if _m.any(): print(f"  [forensic] {fr['ticker']} -> rating 5 from {_fd.date()} ({int(_m.sum())} rows)")
    except Exception as e:
        print("  forensic_flags load fail:", e)
    suffix = "" if BANK_POWER_MODE == "neutral" else f"_{BANK_POWER_MODE}"
    path = os.path.join(WORKDIR, "data", f"rating_8l_history{suffix}.pkl")
    out.to_pickle(path)
    print(f"  saved {path}  rows={len(out):,}")
    print("\n  rating distribution (all quarters):")
    print(out["rating"].value_counts().sort_index().to_string())
    print("\n  route x rating crosstab:")
    print(pd.crosstab(out["route"], out["rating"]).to_string())
    print("\n  eff_time range:", out["eff_time"].min().date(), "->", out["eff_time"].max().date())


if __name__ == "__main__":
    main()
