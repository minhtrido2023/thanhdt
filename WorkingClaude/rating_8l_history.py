#!/usr/bin/env python3
"""rating_8l_history.py — POINT-IN-TIME historical reconstruction of the 8L 1-5 quality rating.

Goal (B2 of the FA_rating <- 8L group-aware project): replay rating_8l.py's rate_row() logic over the
FULL ticker_financial history so we get a (ticker, effective_date, rating 1-5, route) panel that can be
back-tested exactly like the flat fa_ratings table. We then map 1->A .. 5->E and re-run the per-group
forward-return IC diagnosis (B1) on the NEW rating to see, group by group, whether 8L preserves the
compounder monotonicity and FIXES the cyclical inversion the flat composite has.

Point-in-time honesty:
  - Each rating is computed ONLY from that quarter's financial row (no future data).
  - Effective date = Release_Date (when the financials became public) -> first tradable day >= that.
  - COMPOUNDER / CYCLICAL / REALESTATE / SECURITIES / INSURANCE: reconstructed EXACTLY (all inputs are in
    ticker_financial historically).
  - BANK: the live rate_bank() needs NPL/coverage from a CURRENT snapshot CSV (no history) -> we use an
    ROE-only historical proxy (ROE<8%->5, graded by ROE otherwise). Drops the asset-quality premium; BANK's
    flat composite was already decent so this is acceptable and clearly flagged.
  - POWER: the live rate_power() needs the lifecycle verdict (snapshot) -> we proxy with the D/E trajectory
    (STLTDebt_Eq_P0 vs _P4) + TTM-NP sign. Small-n group; flagged.

Writes data/rating_8l_history.csv and (optionally) loads it to BQ tmp table for the IC join.
Usage: python rating_8l_history.py
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

# --- router sets (identical to rating_8l.py) ---
COMMODITY_MAP = {
 "DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea","DDV":"dap","LAS":"dap","DGC":"dap","CSV":"caustic_soda"}
SUGAR_SET = {"SLS","SBT","LSS","KTS","QNS"}
CEMENT_SET = {"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}
HOLDING_OVERRIDE = {"REE"}
REALESTATE_OVERRIDE = {"HHS"}
INSURANCE_ICB  = lambda c: pd.notna(c) and 8530 <= c <= 8579
SECURITIES_ICB = lambda c: pd.notna(c) and 8770 <= c <= 8779
# 5F-audited moat governance (user 2026-06-14, "siết A-mềm"): the quant moat +1 notch is honored ONLY for
# a 5F-WIDE moat (data/moat_tags.csv moat_tier); registry NARROW/NONE -> NO notch (NARROW can erode, must
# not reach AAA via the notch). Absent-from-registry -> notch kept (quant, audit dần). Quant-fortress
# (core>=10 -> prelim 1) is moat-independent and unaffected. PIT-honesty: the registry is a CURRENT (2026-06)
# verdict, so the no-notch override applies ONLY to ratings effective >= MOAT_GOV_CUTOFF (trailing window);
# deep history (2014-2024) keeps the point-in-time quant proxy. Bounded distortion: recent quarters only.
MOAT_TIER = {}
MOAT_GOV_CUTOFF = pd.Timestamp("2025-06-01")


def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=2000000',
                           capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip(): raise RuntimeError("bq no rows. stderr:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))


# Pull FULL financial history. One row per (ticker, quarter). Includes _P4 leverage for the power proxy.
HIST_SQL = """
SELECT f.ticker, f.time AS q_time, f.Release_Date,
  f.ROIC3Y, f.ROIC_Min3Y, f.ROE_Min3Y, f.ROIC_Trailing, f.ROIC5Y, f.ROIC_Min5Y, f.ROE_Min5Y, f.ROE3Y, f.ROE5Y,
  f.ROE_Trailing, f.Debt_Eq_P0, f.Debt_Eq_P4, f.STLTDebt_Eq_P0, f.STLTDebt_Eq_P4, f.FSCORE,
  f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3, f.CF_OA_5Y,
  f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
  f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
  f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
  f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7,
  f.UnearnRev_P0, f.totalAsset_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.time >= '2014-06-01'
"""

ICB_SQL = """
SELECT t.ticker, ANY_VALUE(t.ICB_Code) AS ICB_Code
FROM tav2_bq.ticker AS t
GROUP BY t.ticker
"""


# ---------- ported scorecards (faithful to rating_8l.py) ----------
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

def stability(r):
    s = 1.0
    if r.get("route") not in ("BANK","INSURANCE","SECURITIES"):
        gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]; gpms = [g for g in gpms if pd.notna(g)]
        if len(gpms) >= 4:
            m = float(np.mean(gpms))
            if m > 0:
                cv = float(np.std(gpms))/m
                s = min(s, 1.0 if cv<=0.20 else 0.8 if cv<=0.40 else 0.55)
    rt, r3 = r.get("ROE_Trailing", np.nan), r.get("ROE3Y", np.nan)
    if pd.notna(rt) and pd.notna(r3) and r3 > 0:
        ratio = rt/r3
        s = min(s, 1.0 if ratio<=1.3 else 0.75 if ratio<=1.8 else 0.5)
    return round(s, 2)

def redflag(r, ttm_np):
    rs = []
    if pd.notna(ttm_np) and ttm_np < 0: rs.append("NP_TTM<0")
    lev = real_lev(r)
    if pd.notna(lev) and lev > 3: rs.append("debt/eq>3")
    return ",".join(rs)

def bin_core(s):
    return 1 if s>=10 else 2 if s>=7 else 3 if s>=4 else 4 if s>=2 else 5

def eq_flag(r):
    """Earnings-quality gate for COMPOUNDER/CYCLICAL (identical logic to rating_8l.py.eq_flag, int return).
    TWO TIERS (structural tier added 2026-06-17 to fix HAG quarter-to-quarter flicker):
      * IMPAIRED(5) = STRUCTURAL: 2-year (8q) cumulative NP/GP >= 0.65 AND CF_OA_5Y <= 0, levered. Both
        legs slow-moving -> catches HAG's lumpy non-core gains whichever quarter they land in, immune to
        one-off COVID scars. Fires HAG every quarter 2023Q4->2026Q1 (incl. 2025Q4 the old gate missed).
      * SPECULATIVE(4) = TRANSIENT: TTM (4q) NP/GP >= 0.90, levered, 5Y cash still positive.
    Leverage precondition (real_lev>=0.25) spares net-cash holdcos (VEA/PHR). Cash leg vetoes cyclical
    margin-troughs (HPG/BSR, positive 5Y cash); non-core leg vetoes operating-loss recoverers (VJC/FRT).
    Fail-safe on missing data (8q unavailable -> TTM-4 leg only)."""
    lev = real_lev(r)
    if not (pd.notna(lev) and lev >= 0.25): return 0
    def _npgp(n):
        np_ = [r.get("NP_P%d"%i, np.nan) for i in range(n)]
        rev = [r.get("Revenue_P%d"%i, np.nan) for i in range(n)]
        gpm = [r.get("GPM_P%d"%i, np.nan) for i in range(n)]
        if any(pd.isna(x) for x in np_ + rev + gpm): return None
        tot_np = sum(np_); tot_gp = sum(g*v for g, v in zip(gpm, rev))
        if tot_np <= 0: return None
        return np.inf if tot_gp <= 0 else tot_np/tot_gp
    cf5 = r.get("CF_OA_5Y", np.nan)
    nocash = pd.notna(cf5) and cf5 <= 0
    r8 = _npgp(8)
    if r8 is not None and r8 >= 0.65 and nocash: return 5
    r4 = _npgp(4)
    if r4 is not None and r4 >= 0.90: return 5 if nocash else 4
    return 0

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

def rate_bank_proxy(r):
    """HISTORICAL proxy: ROE-only (no NPL/coverage history). Mirrors the franchise base of rate_bank()."""
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE5Y", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    if pd.isna(roe): return 3
    if roe < 0.08: return 5
    if roe >= 0.18: return 1       # elite ROE (proxy for elite franchise; no AQ data to gate)
    if roe >= 0.14: return 2
    if roe >= 0.12: return 3
    return 4

def rate_power_proxy(r, ttm_np):
    """HISTORICAL proxy for the debt-paydown lifecycle: D/E trajectory (STLTDebt_Eq_P0 vs _P4) + TTM-NP."""
    de0 = r.get("STLTDebt_Eq_P0", np.nan)
    if pd.isna(de0): de0 = r.get("Debt_Eq_P0", np.nan)
    de4 = r.get("STLTDebt_Eq_P4", np.nan)
    if pd.isna(de4): de4 = r.get("Debt_Eq_P4", np.nan)
    if pd.notna(ttm_np) and ttm_np < 0:
        return 5 if (pd.notna(de0) and de0 > 1.0) else 4         # losing money: stress
    if pd.isna(de0): return 3
    if de0 <= 0.3 and (pd.isna(de4) or de0 <= de4): return 2     # mature / low-debt yield
    if pd.notna(de4) and de0 < de4 - 0.05: return 3             # actively paying down = pre-inflection
    if pd.notna(de4) and de0 > de4 + 0.10 and de0 > 1.0: return 4  # leveraging up + high debt = stress
    return 3

def route_of(tk, icb):
    if tk in HOLDING_OVERRIDE: return "COMPOUNDER"
    if tk in REALESTATE_OVERRIDE: return "REALESTATE"
    if icb == 8355: return "BANK"
    if INSURANCE_ICB(icb): return "INSURANCE"
    if SECURITIES_ICB(icb): return "SECURITIES"
    if icb == 7535: return "POWER"
    if tk in COMMODITY_MAP or tk in SUGAR_SET or tk in CEMENT_SET: return "CYCLICAL"
    if icb == 8633: return "REALESTATE"
    return "COMPOUNDER"

def rate_row(r):
    route = r["route"]
    s, cfo_np, ttm_np = core_score(r)
    if route == "SECURITIES": return rate_securities(r)
    if route == "INSURANCE":  return rate_insurance(r)
    if route == "REALESTATE": return rate_realestate(r, cfo_np, ttm_np)
    if route == "BANK":       return rate_bank_proxy(r)
    if route == "POWER":      return rate_power_proxy(r, ttm_np)
    rf = redflag(r, ttm_np)
    if route == "CYCLICAL":
        if rf: return 5
        if pd.notna(real_lev(r)) and real_lev(r) > 1.5: return 5
        prelim = bin_core(s)
        fortress = (pd.notna(real_lev(r)) and real_lev(r)<=0.2 and pd.notna(r.get("ROIC3Y")) and r["ROIC3Y"]>=0.20)
        rating = prelim if prelim>=2 else (1 if fortress else 2)
        return max(rating, eq_flag(r))          # earnings-quality gate (downgrade-only)
    # COMPOUNDER
    if rf: return 4   # red-flag -> impaired, but profitable->4 floor applies (5 only via... see live: 5->4)
    prelim = bin_core(s)
    rating = prelim
    moat = moat_tag(r, r.get("ROE5Y", np.nan))
    if moat=="STRONG" and prelim in (2,3):
        _eff = pd.to_datetime(r.get("Release_Date"), errors="coerce")
        _recent = pd.notna(_eff) and _eff >= MOAT_GOV_CUTOFF
        _tier = MOAT_TIER.get(r.get("ticker"))
        _revoke = _recent and (_tier is not None and _tier != "WIDE")   # 5F NARROW/NONE: no AAA notch (recent)
        if not _revoke: rating = prelim-1
    stab_cap = stability(r)
    if pd.notna(stab_cap) and stab_cap <= 0.5 and rating < 3: rating = 3
    if rating == 5: rating = 4
    return max(rating, eq_flag(r))              # earnings-quality gate (downgrade-only, post-moat)


def override_current_bank_aq(out):
    """Override ONLY the CURRENT-snapshot bank rating with the live AQ-aware rate_bank value (NPL/coverage
    from data/bank_lens_v3.csv, via rating_8l.py -> data/rating_8l.csv) while leaving the entire historical
    proxy series untouched. Rationale (user 2026-06-16): the history publisher rates banks ROE-only because
    NPL/coverage have no deep history (avoids look-ahead); but for the MOST RECENT snapshot we DO have current
    asset quality, so the latest row per bank should reflect it (e.g. BID/SHB/HDB proxy=1 -> AQ-aware=3 when
    coverage<0.9). Only the single latest eff_date row per BANK ticker changes; all prior (backtest) rows keep
    the proxy -> no look-ahead introduced. Fail-safe: missing live file / ticker -> keep proxy."""
    try:
        live = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l.csv"))
    except Exception as e:
        print(f"  [bank-AQ override] SKIPPED (live rating_8l.csv unavailable -> keep proxy): {e}"); return out
    lb = live[live["route"] == "BANK"] if "route" in live.columns else live.iloc[0:0]
    live_map = {t: int(r) for t, r in zip(lb["ticker"], lb["rating"]) if pd.notna(r)}
    r2t = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    n = 0
    for tk in out.loc[out["route"] == "BANK", "ticker"].unique():
        if tk not in live_map: continue
        sub = out.loc[(out["ticker"] == tk) & (out["route"] == "BANK")].sort_values("eff_date")
        if not len(sub): continue
        i = sub.index[-1]; new_r = live_map[tk]
        if int(out.at[i, "rating"]) != new_r:
            out.at[i, "rating"] = new_r; out.at[i, "tier"] = r2t[new_r]; n += 1
    print(f"  [bank-AQ override] current-snapshot bank rating set to live AQ for {n} bank(s); history proxy untouched")
    return out


def refresh_bq_table(csv_path):
    """Refresh tav2_bq.fa_ratings_8l (ticker,time,route,rating,tier) from the history CSV — one-command
    refresh so the live regime_size overlay reads the latest point-in-time ratings. Dedup per (ticker,eff_date)."""
    try:
        load = (f'"{BQ_BIN}" load --replace --source_format=CSV --skip_leading_rows=1 '
                f'--project_id={PROJECT} tav2_bq.tmp_r8l_refresh "{csv_path}" '
                f'ticker:STRING,eff_date:DATE,q_time:DATE,route:STRING,rating:INT64,core_score:INT64,tier:STRING')
        subprocess.run(load, shell=True, capture_output=True, text=True, timeout=300)
        sql = ("CREATE OR REPLACE TABLE tav2_bq.fa_ratings_8l AS "
               "SELECT tk AS ticker, eff_date AS time, ANY_VALUE(route) AS route, "
               "ANY_VALUE(rating) AS rating, ANY_VALUE(tier) AS tier FROM ("
               "SELECT h.ticker AS tk, h.eff_date, h.route, h.rating, h.tier, "
               "ROW_NUMBER() OVER (PARTITION BY h.ticker, h.eff_date ORDER BY h.q_time DESC) rn "
               "FROM tav2_bq.tmp_r8l_refresh AS h) WHERE rn=1 GROUP BY tk, eff_date")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write(sql); tmp = f.name
        subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                       f'--project_id={PROJECT}', shell=True, capture_output=True, text=True, timeout=300)
        os.unlink(tmp)
        subprocess.run(f'"{BQ_BIN}" rm -f -t {PROJECT}:tav2_bq.tmp_r8l_refresh', shell=True, capture_output=True, text=True)
        print("refreshed BQ table tav2_bq.fa_ratings_8l")
    except Exception as e:
        print(f"[!] BQ table refresh skipped: {e}")

def main():
    print("pulling financial history ...")
    df = bq(HIST_SQL)
    icb = bq(ICB_SQL)
    df = df.merge(icb, on="ticker", how="left")
    print(f"  {len(df)} financial rows, {df['ticker'].nunique()} tickers")

    df["route"] = [route_of(t, c) for t, c in zip(df["ticker"], df["ICB_Code"])]
    global MOAT_TIER
    try:
        _mg = pd.read_csv(os.path.join(WORKDIR,"data","moat_tags.csv"))
        MOAT_TIER = dict(zip(_mg["ticker"], _mg["moat_tier"]))
        _wide = sorted(t for t,v in MOAT_TIER.items() if v=="WIDE")
        print(f"  [moat-gov] {len(MOAT_TIER)} 5F tiers; only WIDE earns +1 from {MOAT_GOV_CUTOFF.date()}: "
              f"{_wide}; registry NARROW/NONE -> no notch (recent)")
    except Exception as e:
        print("moat_tags load fail (quant ungated):", e); MOAT_TIER = {}
    # stability() reads route off the row
    df["rating"] = df.apply(lambda r: rate_row(r), axis=1)
    df["core_score"] = df.apply(lambda r: core_score(r)[0], axis=1)

    # ---- per-group A-E mapping (user choice: per-group percentile) ----
    # COMPOUNDER: percentile-rank core_score WITHIN each quarter's cross-section (point-in-time, ~500 names
    #   -> stable) using the same thresholds as the old fa_ratings (A top10 / B 10-30 / C 30-60 / D 60-85 / E
    #   bottom15). This restores a balanced A-E with a real E-floor that the fixed 1-5 bins lost for compounders.
    # SMALL GROUPS (bank/power/cyclical/RE/sec/ins): keep the validated discrete 8L rating 1->A..5->E
    #   (per-quarter cross-section is too thin to percentile reliably).
    def pct_tier(s):
        # percentile rank in [0,1]; higher score = better = A
        r = s.rank(pct=True, method="average")
        return pd.cut(r, bins=[-0.01,0.15,0.40,0.70,0.90,1.01], labels=["E","D","C","B","A"])
    df["tier"] = df["rating"].map({1:"A",2:"B",3:"C",4:"D",5:"E"})
    comp = df["route"]=="COMPOUNDER"
    df.loc[comp, "tier"] = (
        df.loc[comp].groupby("q_time")["core_score"].transform(lambda s: pct_tier(s)).astype(str)
    )
    # CONSISTENCY: an IMPAIRED rating (5) must not show an investment-grade TIER from a still-decent
    # core_score percentile. The EQ gate downgrades rating (e.g. HAG: scorecard ok but non-core/no-cash/
    # levered -> rating 5) without touching core_score, so force rating-5 names to the bottom tier (E).
    df.loc[df["rating"]==5, "tier"] = "E"

    # effective date = Release_Date (public) ; fall back to quarter end + 45d if missing
    df["eff_date"] = pd.to_datetime(df["Release_Date"], errors="coerce")
    qd = pd.to_datetime(df["q_time"], errors="coerce") + pd.Timedelta(days=45)
    df["eff_date"] = df["eff_date"].fillna(qd)
    df = df.dropna(subset=["eff_date"])

    out = df[["ticker","eff_date","q_time","route","rating","core_score","tier"]].copy()
    out["eff_date"] = out["eff_date"].dt.strftime("%Y-%m-%d")
    out = override_current_bank_aq(out)   # latest-snapshot bank rating -> live AQ (history proxy untouched)
    # FORENSIC EXCLUDE (2026-06-20, date-aware, NO hindsight): human-flagged 'exclude' (related-party/
    # manipulation, data/forensic_flags.csv). The flagged name's latest rating row predates the flag date,
    # so we APPEND an override row stamped at the flag date (rating 5/tier E) -> as-of-forward reads return 5
    # for every fa_ratings_8l consumer (custom30, golive sizing, audits); all history before it untouched.
    try:
        _ff = pd.read_csv(os.path.join(WORKDIR,"data","forensic_flags.csv"))
        _add = []
        for _, fr in _ff.iterrows():
            if str(fr["severity"]).strip() != "exclude": continue
            tk = fr["ticker"]; fdate = str(pd.Timestamp(fr["date"]).date())
            _rt = out.loc[out["ticker"] == tk, "route"]; rte = _rt.iloc[-1] if len(_rt) else "COMPOUNDER"
            _add.append({"ticker": tk, "eff_date": fdate, "q_time": fdate, "route": rte,
                         "rating": 5, "core_score": 0, "tier": "E"})
        if _add:
            out = pd.concat([out, pd.DataFrame(_add)], ignore_index=True)
            print(f"  [forensic] appended {len(_add)} exclude override row(s) rating 5 @flag date: {[a['ticker'] for a in _add]}")
    except Exception as e:
        print("  forensic_flags load fail:", e)
    path = os.path.join(WORKDIR,"data","rating_8l_history.csv")
    out.to_csv(path, index=False)
    print(f"wrote {path}  ({len(out)} rows)")
    refresh_bq_table(path)
    print("\ndistribution by route x rating (raw 1-5):")
    print(pd.crosstab(out["route"], out["rating"]).to_string())
    print("\ndistribution by route x TIER (final A-E, compounder=per-qtr percentile):")
    print(pd.crosstab(out["route"], out["tier"]).to_string())

if __name__ == "__main__":
    main()
