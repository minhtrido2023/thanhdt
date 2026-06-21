#!/usr/bin/env python3
"""rating_8l.py — 8L Quality Rating 1-5 (credit-agency-style), sector-aware.

One axis = business durability / permanent-capital-impairment risk (NOT a buy signal).
  1 AAA/AA · 2 A · 3 BBB (lowest investment grade) | 4 BB · 5 B/CCC (speculative).
Router: BANK(ICB8355) / POWER(ICB7535) / CYCLICAL(commodity map+sugar) / COMPOUNDER(rest).
Through-the-cycle (uses _Min5Y floors), sticky, hard red-flag gate. Spec: rating_8l_criteria.md.
Validated (a): bins monotonic on fwd-12M return + downside; 3/4 boundary = dip-opportunity vs trap.

★★ STANDING RULE — MOAT UPGRADE REQUIRES AUDIT (user 2026-06-14) ★★
A moat may LIFT a rating (the +1 notch, prelim 2/3 -> top tier) ONLY when it has passed a 5F
competitive audit recorded in data/moat_tags.csv. Concretely:
  • moat_tier == WIDE (5F-validated)  -> notch allowed (can reach rating 1 / AAA).
  • registry NARROW / NONE            -> NO notch (a NARROW moat can erode — e.g. FPT −40% on AI
                                          fear despite stable earnings — so it must not reach AAA).
  • ticker ABSENT from the registry   -> quant notch TOLERATED ONLY as a temporary placeholder
                                          ("audit dần"); it is NOT a trusted upgrade. The moment such
                                          a name becomes screener/decision-relevant (liquid, surfaced
                                          in a list), it MUST be 5F-audited (added to moat_tags.csv)
                                          BEFORE the moat upgrade is relied upon.
The crude quant moat_tag() (GPM/ROE) is a PROXY, never a substitute for the 5F audit. Do NOT widen
what the moat notch can do without a corresponding audited moat_tags.csv entry. (Quant-fortress names
with core_score>=10 reach rating 1 on the scorecard alone — that is moat-INDEPENDENT and unaffected.)

WIRED into the live pipeline (pt_8l_daily.bat): exports data/rating_8l.csv + rating_8l_top30.csv +
rating_8l_buynow.csv + rating_8l_screener.csv (the default 2-axis quality×value list).
Usage: python rating_8l.py
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

COMMODITY_MAP = {
 "DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap",
 "CSV":"caustic_soda"}  # CSV = chlor-alkali (NaOH+chlorine+PVC), NOT dap fertilizer — own caustic-soda cycle
SUGAR_SET = {"SLS","SBT","LSS","KTS","QNS"}
# Cement = commodity cyclical (clinker/coal cost, property-demand-driven, chronic VN overcapacity, no pricing
# power) — route to CYCLICAL (cap 2 unless net-cash fortress) instead of COMPOUNDER. ICB 2353 is a grab-bag
# (also holds quality non-cement: BMP/NTP plastic pipes, VCS quartz, NNC/DHA/VLB stone, VGC glass/tiles) so we
# curate by ticker, NOT by ICB. Confirmed pure-cement only. Fortress (real_lev<=0.2 & ROIC3Y>=0.20) still
# earns tier 1 — e.g. CLH (net-cash, ROIC3Y 24%) stays 1; weak/over-levered cement (XMC/SCJ) drops via the
# trough-leverage gate. (Added 2026-06-05.)
CEMENT_SET = {"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=100000',
                           capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip(): raise RuntimeError("bq no rows. stderr:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))

MAIN_SQL = """
WITH L AS (SELECT MAX(time) mx FROM tav2_bq.ticker_1m)
SELECT t.ticker, t.ICB_Code,
  t.ROIC3Y, t.ROIC_Min3Y, t.ROE_Min3Y, t.ROIC_Trailing, t.ROIC5Y, t.ROIC_Min5Y, t.ROE_Min5Y, t.ROE5Y, t.Debt_Eq_P0, t.FSCORE,
  t.CF_OA_P0, t.CF_OA_P1, t.CF_OA_P2, t.CF_OA_P3,
  t.NP_P0, t.NP_P1, t.NP_P2, t.NP_P3,
  t.PB, t.PE, ROUND(SAFE_DIVIDE(t.PB-t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)),2) AS pb_z,
  ROUND(t.Trading_Value_1M_P50/1e9,2) AS liq_bn,
  ROUND((SAFE_DIVIDE(t.Close,t.HI_3M_T1)-1)*100,1) AS drop_pct
FROM tav2_bq.ticker_1m AS t, L
WHERE t.time = L.mx
"""
# GPM_P0 + ROE_Trailing + REAL leverage (STLTDebt_Eq = interest-bearing debt/equity, NOT total-liab)
# + UnearnRev (người mua trả tiền trước / deferred revenue = RE forward-recognition pipeline)
FIN_SQL = """
SELECT ticker, GPM_P0,GPM_P1,GPM_P2,GPM_P3,GPM_P4,GPM_P5,GPM_P6,GPM_P7,
       Revenue_P0,Revenue_P1,Revenue_P2,Revenue_P3, CF_OA_5Y,
       ROE_Trailing, ROE3Y, STLTDebt_Eq_P0, UnearnRev_P0, totalAsset_P0,
       (SELECT COUNTIF(n<0) FROM UNNEST([NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,NP_P5,NP_P6,NP_P7]) n) AS neg_q
FROM (
  SELECT t.*, ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
  FROM tav2_bq.ticker_financial AS t)
WHERE rn = 1
"""

INSURANCE_ICB  = lambda c: pd.notna(c) and 8530 <= c <= 8579   # 853x nonlife + 857x life insurance
SECURITIES_ICB = lambda c: pd.notna(c) and 8770 <= c <= 8779   # 877x brokers / investment services
# diversified holdings classified ICB 7535 but NOT pure power producers -> route as COMPOUNDER
HOLDING_OVERRIDE = {"REE"}  # office leasing + M&E + water + power investments (user-confirmed multi-sector)
# ICB-mislabeled real-estate (pivoted businesses still tagged by old ICB) -> route as REALESTATE
REALESTATE_OVERRIDE = {"HHS"}  # Hoàng Huy: ICB 3353 (trucks, stale) but now a property/holding play (sister of TCH)
# 5F-AUDITED moat governance (user 2026-06-14, "siết A-mềm"): the quant moat_tag()=STRONG +1 notch (which
# lifts a prelim-2/3 name to the top) may fire ONLY when the 5F competitive audit (data/moat_tags.csv,
# moat_tier) rates the moat WIDE — a NARROW moat can erode (e.g. FPT −40% on AI fear despite stable
# earnings) so it must NOT reach AAA via the notch. Registry NARROW/NONE -> NO notch (revert to scorecard).
# Ticker ABSENT from registry -> notch kept (quant proxy, audit incrementally). NOTE: this only gates the
# MOAT NOTCH; a quant-fortress (core_score>=10 -> prelim 1) still earns rating 1 on its own (moat-independent).
MOAT_TIER = {}   # {ticker: 'WIDE'/'NARROW'/'NONE'} loaded from data/moat_tags.csv in main()

# ---------- scorecards ----------
def real_lev(r):
    """Interest-bearing debt/equity (STLTDebt_Eq). Debt_Eq_P0 is TOTAL-liabilities/equity — it counts
    customer advances (người mua trả tiền trước) + payables + deferred rev as 'debt', wildly overstating
    leverage for real-estate/industrial-park (NTC 3.82 total-liab vs 0.03 real-debt). Fall back if null."""
    v = r.get("STLTDebt_Eq_P0", np.nan)
    return v if pd.notna(v) else r.get("Debt_Eq_P0", np.nan)

def moat_tag(r, roe5y):
    """Moat = durable pricing power. Built from GPM LEVEL + GPM STABILITY (stable high margins across
    8 quarters = pricing power that competitors can't erode) + ROE level. GPM/ROE are fractions in BQ.
    User-prioritized signal for long-term holds -> upgrades rating (see rate_row)."""
    gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]
    gpms = [g for g in gpms if pd.notna(g)]
    if not gpms: return "WEAK"
    gmean = float(np.mean(gpms))
    cv = (float(np.std(gpms))/gmean) if gmean > 0 else 9.0          # coefficient of variation
    hi_level  = gmean >= 0.25                                       # high gross margin
    stable    = (len(gpms) >= 4 and cv <= 0.20)                    # margins don't swing = pricing power
    hi_roe    = pd.notna(roe5y) and roe5y >= 0.15
    if gmean < 0.15 or (pd.notna(roe5y) and roe5y < 0.10): return "WEAK"
    # STRONG = high stable margin + decent returns (durable moat); else MODERATE
    if hi_level and stable and hi_roe: return "STRONG"
    if (hi_level and (stable or hi_roe)) or (stable and hi_roe): return "MODERATE+"
    return "MODERATE"

def core_score(r):
    """6-axis validated scorecard (max 12). Returns (score, cfo_np)."""
    ttm_cfo = sum(r.get("CF_OA_P%d"%i, np.nan) for i in range(4))
    ttm_np  = sum(r.get("NP_P%d"%i,    np.nan) for i in range(4))
    cfo_np  = (ttm_cfo/ttm_np) if (pd.notna(ttm_np) and ttm_np != 0) else np.nan
    # 3Y windows (not 5Y): hard 5Y-min junked COVID-hit monopolies (ACV/SAS ROIC_min5Y<0 but 3Y +13%/+11%).
    # 3Y is responsive and excludes stale one-off shocks (user directive 2026-06-02).
    roic, roicm, roe_tr, de, fs = r.get("ROIC3Y",np.nan), r.get("ROIC_Min3Y",np.nan), r.get("ROE_Trailing", np.nan), real_lev(r), r["FSCORE"]
    s  = (2 if roic>=0.15 else 1 if roic>=0.10 else 0) if pd.notna(roic) else 0       # avg ROIC quality (3Y)
    s += (2 if roicm>=0.10 else 1 if roicm>=0.05 else 0) if pd.notna(roicm) else 0    # ROIC floor (3Y, durability)
    s += (2 if roe_tr>=0.18 else 1 if roe_tr>=0.12 else 0) if pd.notna(roe_tr) else 0 # CURRENT profitability (ROE_Trailing, not stale _Min5Y)
    s += (2 if de<=0.3 else 1 if de<=1.0 else 0) if pd.notna(de) else 0
    s += (2 if (pd.notna(cfo_np) and cfo_np>=1.0 and ttm_cfo>0) else 1 if (pd.notna(cfo_np) and cfo_np>=0.7) else 0)
    s += (2 if fs>=8 else 1 if fs>=6 else 0) if pd.notna(fs) else 0
    return s, (round(cfo_np,2) if pd.notna(cfo_np) else np.nan), ttm_np

def stability(r):
    """0.4..1.0 — how STABLE profitability is (the real moat). Penalizes (a) volatile gross margin and
    (b) cyclical-peak earnings (trailing ROE >> 3Y avg = unsustainable peak, e.g. brokers in a bull mkt).
    User 2026-06-02: stability matters more than a high current number (VIX/CTS high ROE ≠ moat)."""
    s = 1.0
    if r.get("route") not in ("BANK","INSURANCE","SECURITIES"):   # GPM meaningless for financials
        gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]; gpms = [g for g in gpms if pd.notna(g)]
        if len(gpms) >= 4:
            m = float(np.mean(gpms))
            if m > 0:
                cv = float(np.std(gpms))/m
                s = min(s, 1.0 if cv<=0.20 else 0.8 if cv<=0.40 else 0.55)   # margin volatility
    rt, r3 = r.get("ROE_Trailing", np.nan), r.get("ROE3Y", np.nan)
    if pd.notna(rt) and pd.notna(r3) and r3 > 0:
        ratio = rt/r3
        s = min(s, 1.0 if ratio<=1.3 else 0.75 if ratio<=1.8 else 0.5)   # cyclical-peak detection
    return round(s, 2)

def redflag(r, ttm_np):
    # MINIMAL hard red-flags (user 2026-06-02: "hạn chế red-flag, để scorecard tự làm việc").
    # A single weak QUARTER must not junk a name — judge on the ANNUAL/TTM result.
    #   - ROIC_Min3Y<0 REMOVED: it's a quarterly-min artifact (PVS NP_TTM +1934bn but ROIC_min −0.016 → was 5).
    #     Weak ROIC still costs scorecard points (0), so the rating system handles it without a cliff.
    #   - Keep ONLY genuine structural distress: trailing-YEAR actually lost money, or extreme real leverage.
    rs = []
    if pd.notna(ttm_np) and ttm_np < 0: rs.append("NP_TTM<0")        # full-year loss = genuine
    lev = real_lev(r)
    if pd.notna(lev) and lev > 3: rs.append("debt/eq>3")             # interest-bearing debt >3x equity
    return ",".join(rs)

def bin_core(s):   # validated bins (max 12)
    return 1 if s>=10 else 2 if s>=7 else 3 if s>=4 else 4 if s>=2 else 5

def eq_flag(r):
    """EARNINGS-QUALITY red flag for OPERATING routes (COMPOUNDER/CYCLICAL only — financials/RE have
    their own lenses). Catches profit NOT generated by core operations (HAG forensic pattern):
      - TTM net profit >= 90% of TTM gross profit  => opex+interest+tax implausibly small, i.e.
        reported NP is propped by NON-OPERATING / one-off gains (divestments, FV revaluations, debt
        write-backs); OR a positive NP printed on a GROSS LOSS (purely non-core).
    Leverage precondition (real_lev>=0.25): the 8L axis is permanent-capital-impairment risk; non-core/
    opaque earnings in a NET-CASH company (VEA = Honda/Toyota JV associate income; PHR rubber+land) is
    NOT an impairment risk — no debt to threaten capital. Only LEVERED cash-bleeders (HAG lev 0.43) bite.
    Severity: non-core+levered -> speculative(4); ESCALATES to impaired(5) if also CF_OA_5Y<=0 (chronic
    non-cash). Surgical (validated full liquid universe 2026-06-14): only HAG/MST/SMC trigger the NP/GP
    leg; growth/cyclical cash-consumers (VJC/FRT/NKG/CTD, normal NP/GP) untouched; VEA/PHR/BSR spared by
    the leverage guard. Fail-safe: incomplete Revenue/GPM -> no flag. Returns (cap, note)."""
    ttm_np = sum(r.get("NP_P%d"%i, np.nan) for i in range(4))
    if not (pd.notna(ttm_np) and ttm_np > 0): return 0, ""        # losses handled by redflag()
    lev = real_lev(r)
    if not (pd.notna(lev) and lev >= 0.25): return 0, ""          # net-cash -> not an impairment risk
    rev = [r.get("Revenue_P%d"%i, np.nan) for i in range(4)]
    gpm = [r.get("GPM_P%d"%i, np.nan) for i in range(4)]
    if any(pd.isna(x) for x in rev + gpm): return 0, ""           # incomplete -> fail-safe (no flag)
    ttm_gp = sum(g*v for g, v in zip(gpm, rev))
    nonop = (ttm_gp <= 0) or (ttm_np/ttm_gp >= 0.90)
    if not nonop: return 0, ""
    cf5 = r.get("CF_OA_5Y", np.nan)
    weakcash = pd.notna(cf5) and cf5 <= 0
    return (5, "eq:NP≈GP+CFO5Y≤0+levered(non-core,no-cash)") if weakcash else (4, "eq:NP≈GP+levered(non-core)")

def rate_securities(r):
    """ICB 877x brokers/securities. Financial business: ROIC low/meaningless, leverage = margin-funding
    borrowings (operational, like a bank's), FSCORE/GPM/cash-conversion N/A. Earnings HIGHLY CYCLICAL
    (track market turnover + margin balances) -> cap at 2. Rate on ROE level + consistency."""
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)        # ROE_Trailing often missing for brokers
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe
    ttm_np = sum(r.get("NP_P%d"%i, np.nan) for i in range(4))
    if (pd.notna(roe) and roe < 0) or (pd.notna(ttm_np) and ttm_np < 0): return 5, "sec: lossmaking"
    if pd.notna(roe) and roe>=0.13 and pd.notna(r3) and r3>=0.11: return 2, "sec strong ROE"   # cap 2 (cyclical)
    if pd.notna(roe) and roe>=0.09 and pd.notna(r3) and r3>=0.07: return 3, "sec ok ROE"
    if pd.notna(roe) and roe>=0.05: return 4, "sec weak ROE"
    return 5, "sec poor/trough"

def rate_insurance(r):
    """ICB 853x/857x. ROIC/GPM/FSCORE/Debt_Eq are ALL meaningless for insurers (capital = investment
    portfolio + float; technical reserves are operational liabilities like a bank's deposits, not debt).
    Cat-event losses (storms/accidents) spike one period then recover -> rate on ROE LEVEL + CONSISTENCY
    (ROE_Trailing current + ROE3Y avg, which smooths a single cat year). User-requested own lens 2026-06-02."""
    roe_tr = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe_tr): roe_tr = r.get("ROE_Min3Y", np.nan)         # fallback
    if pd.notna(roe_tr) and roe_tr < 0: return 5, "ins: currently lossmaking"
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe_tr
    if pd.notna(roe_tr) and roe_tr>=0.15 and pd.notna(r3) and r3>=0.12: return 1, "ins elite ROE"
    if pd.notna(roe_tr) and roe_tr>=0.11 and pd.notna(r3) and r3>=0.09: return 2, "ins strong ROE"
    if pd.notna(roe_tr) and roe_tr>=0.07: return 3, "ins ok ROE"
    if pd.notna(roe_tr): return 4, "ins weak ROE"
    return 4, "ins no-data"

def rate_realestate(r, cfo_np, ttm_np):
    """ICB 8633 real-estate / industrial-park (L8 asset-play). The COMPOUNDER red-flags misfire here:
    prepaid land-lease revenue is booked as LIABILITY (inflates D/E) and land-bank acquisition years
    show NEGATIVE operating cash — neither is distress. So: red-flag only on genuine TTM losses,
    grade ROE_Trailing (realized) + ROIC + LENIENT leverage + lumpy-tolerant cash; cap at 2 (cyclical/lumpy)."""
    if pd.notna(ttm_np) and ttm_np < 0: return 5, "NP_TTM<0"
    roe_tr, roic, de, fs, roicm = r.get("ROE_Trailing",np.nan), r.get("ROIC3Y",np.nan), real_lev(r), r["FSCORE"], r.get("ROIC_Min3Y",np.nan)
    unearn, assets = r.get("UnearnRev_P0",np.nan), r.get("totalAsset_P0",np.nan)
    pipeline = (unearn/assets) if (pd.notna(unearn) and pd.notna(assets) and assets>0) else np.nan
    s  = (2 if (pd.notna(roe_tr) and roe_tr>=0.18) else 1 if (pd.notna(roe_tr) and roe_tr>=0.10) else 0)
    s += (2 if (pd.notna(roic) and roic>=0.12) else 1 if (pd.notna(roic) and roic>=0.07) else 0)
    s += (2 if (pd.notna(de) and de<=0.5) else 1 if (pd.notna(de) and de<=1.5) else 0)   # REAL debt (interest-bearing), not total-liab
    s += (1 if (pd.notna(cfo_np) and cfo_np>=0.8) else 0)                                 # lumpy -> light weight
    s += (1 if (pd.notna(fs) and fs>=6) else 0)
    s += (1 if (pd.notna(roicm) and roicm>=0) else 0)                                     # never destroyed capital
    s += (1 if (pd.notna(pipeline) and pipeline>=0.15) else 0)                            # người mua trả tiền trước = doanh thu tương lai đã bán
    # capped at 2 (lumpy/cyclical earnings); FLOOR 4 — land-bank asset backing limits permanent
    # impairment, so a profitable RE name never hits 5 (only genuine TTM losers, handled above)
    rating = 2 if s>=6 else 3 if s>=4 else 4
    return rating, f"RE asset-play (s{s})"

def rate_row(r):
    """returns dict with rating + diagnostics."""
    route = r["route"]
    s, cfo_np, ttm_np = core_score(r)
    moat = moat_tag(r, r["ROE5Y"])
    rf = redflag(r, ttm_np)
    note = ""
    if route == "SECURITIES":
        rating, note = rate_securities(r)
    elif route == "INSURANCE":
        rating, note = rate_insurance(r)
    elif route == "REALESTATE":
        rating, note = rate_realestate(r, cfo_np, ttm_np)
    elif route == "BANK":
        rating, note = rate_bank(r)
    elif route == "POWER":
        rating, note = rate_power(r)
    elif route == "CYCLICAL":
        if rf: rating = 5; note = "redflag:"+rf
        elif pd.notna(real_lev(r)) and real_lev(r) > 1.5: rating = 5; note = "debt/eq>1.5 trough-fragile"
        else:
            prelim = bin_core(s)
            fortress = (pd.notna(real_lev(r)) and real_lev(r)<=0.2 and pd.notna(r.get("ROIC3Y")) and r["ROIC3Y"]>=0.20)
            rating = prelim if prelim>=2 else (1 if fortress else 2)  # cap at 2 unless fortress
            note = "cap2" if (prelim<2 and not fortress) else ("fortress" if fortress else "")
    else:  # COMPOUNDER
        if rf: rating = 5; note = "redflag:"+rf
        else:
            prelim = bin_core(s)
            # Moat notch (prelim 2/3 -> one better) fires ONLY for a 5F-WIDE moat (siết A-mềm, user
            # 2026-06-14): NARROW moats can erode (forward competitive risk) so they don't earn AAA via
            # the notch; registry NARROW/NONE -> no notch (scorecard stands). Absent-from-registry -> notch
            # kept (quant, audit dần). Quant-fortress (prelim 1, core>=10) is unaffected (moat-independent).
            rating = prelim
            if moat=="STRONG" and prelim in (2,3):
                _tier = MOAT_TIER.get(r.get("ticker"))
                if _tier is None or _tier == "WIDE":
                    rating = prelim-1; note = "moat↑1"
                else:
                    note = f"moat↑1 REVOKED(5F:{_tier})"
            # Cyclical-peak / unstable-profitability cap: wire the EXISTING stability() metric into the
            # rating (it was computed for display only — a latent gap vs its own intent "high ROE ≠ moat").
            # stab<=0.5 means trailing ROE is a cyclical peak (ROE_Trailing/ROE3Y>1.8) or margins are highly
            # volatile => not investment-grade, demote to >=3. NOT a ROE_Min hard-gate (a single weak quarter
            # never triggers it). Surgical & validated 2026-06-05: catches the float/leverage-inflated ROE
            # mirage (e.g. VVS ROE_TTM 74% on GPM 7.6% / ROE_Min5Y 6.4%) with ZERO false positives in tier-1.
            stab_cap = stability(r)
            if pd.notna(stab_cap) and stab_cap <= 0.5 and rating < 3:
                rating = 3; note = (note+" " if note else "")+"stab≤.5→cap3"
            # No ROE_Min/ROIC_Min hard gate (user): a single weak quarter in 3Y must not cap a name whose
            # annual result is fine. The scorecard's ROIC/ROE/cash axes already score weak names low.
            # Rating 5 = IMPAIRED (lossmaking / over-leveraged = the red-flag branch). A PROFITABLE company,
            # however thin (e.g. CTD: GPM 4%, weak CFO, but NP+ & net-cash), is at worst speculative=4 not 5.
            if rating == 5: rating = 4; note = (note+" " if note else "")+"profitable→4"
    # EARNINGS-QUALITY gate (operating routes only): downgrade non-core/one-off-driven earnings in a
    # levered company even if the scorecard looks fine (HAG: ROIC/ROE/FSCORE recovered -> rating 2, but
    # NP≈GP & CFO5Y<0 & levered). FLOOR (max = worse), never an upgrade; after moat so it can't be rescued.
    if route in ("COMPOUNDER", "CYCLICAL"):
        eq, eqn = eq_flag(r)
        if eq > rating: rating = eq; note = (note+" " if note else "")+eqn
    rf_disp = rf if route in ("COMPOUNDER", "CYCLICAL") else ""  # D/E doesn't apply to bank/power/realestate
    return dict(rating=rating, core_score=s, moat=moat, stab=stability(r), cfo_np=cfo_np, note=note, redflag=rf_disp)

# bank rating from cached lens v3 (gate + metrics)
BANKD = {}
def rate_bank(r):
    """ROE (franchise strength) is the BASE; asset quality (NPL+coverage) is a DIFFERENTIATOR for the
    top grades, NOT a hard kill-switch. Market prizes AQ as a PREMIUM (VCB→1) but a high-NPL bank with
    strong ROE+capital is still investable (VPB: NPL 3.6% but ROE 15.5%/CAR 14.3% → 3, not 5).
    Only a genuinely weak franchise (low ROE) → 5. (Replaces the old NPL>3%-AVOID cliff, user 2026-06-02.)"""
    b = BANKD.get(r["ticker"])
    if not b: return 3, "bank-nodata"
    roe, npl, cov = b.get("ROE"), b.get("NPL"), b.get("coverage")
    if pd.isna(roe): return 3, "bank-noROE"
    if roe < 0.08: return 5, "weak franchise (ROE<8%)"          # only genuine weakness -> 5
    pristine = pd.notna(npl) and npl<=0.012 and pd.notna(cov) and cov>=1.5
    strong   = pd.notna(npl) and npl<=0.020 and pd.notna(cov) and cov>=0.9
    if roe>=0.15 and pristine: return 1, "elite asset-quality"
    if roe>=0.14 and strong:   return 2, "strong asset-quality"
    if roe>=0.12: return 3, "profitable (AQ-modulated)"         # high-NPL-but-profitable (VPB/HDB) land here
    return 4, "modest ROE"

POWERD = {}
def rate_power(r):
    p = POWERD.get(r["ticker"])
    if not p: return 3, "power-nodata"
    v = str(p["verdict"]).upper(); cfo = p.get("cfo_ttm_bn", np.nan)
    if "MATURE" in v: return 2, "MATURE_YIELD"
    if "PRE_INFLECTION" in v: return 3, "PRE_INFLECTION buy-zone"
    if "STRESS" in v or "AVOID" in str(p.get("action","")).upper():
        return (5 if (pd.notna(cfo) and cfo<0) else 4), "DEBT_STRESS"
    return 3, "power-other"

def main():
    df = bq(MAIN_SQL)
    try:
        fin = bq(FIN_SQL); df = df.merge(fin, on="ticker", how="left")
    except Exception as e:
        print("financial merge skipped:", e); df["GPM_P0"] = np.nan; df["ROE_Trailing"] = np.nan

    # load 5F-audited moat tiers (only WIDE earns the moat notch)
    global MOAT_TIER
    try:
        _mg = pd.read_csv(os.path.join(WORKDIR,"data","moat_tags.csv"))
        MOAT_TIER = dict(zip(_mg["ticker"], _mg["moat_tier"]))
        _wide = sorted(t for t,v in MOAT_TIER.items() if v=="WIDE")
        print(f"  [moat-gov] {len(MOAT_TIER)} 5F tiers; only WIDE earns +1 notch: {_wide}; registry NARROW/NONE -> no notch")
    except Exception as e:
        print("moat_tags load fail (quant proxy ungated):", e); MOAT_TIER = {}

    # load sector lenses
    global BANKD, POWERD
    try:
        bank = pd.read_csv(os.path.join(WORKDIR,"data","bank_lens_v3.csv"))
        BANKD = {row["ticker"]: row.to_dict() for _, row in bank.iterrows()}
        bank_set = set(bank["ticker"])
    except Exception as e:
        print("bank lens load fail:", e); bank_set = set()
    try:
        power = pd.read_csv(os.path.join(WORKDIR,"data","power_lens.csv"))
        POWERD = {row["ticker"]: row.to_dict() for _, row in power.iterrows()}
        power_set = set(power["ticker"]) - bank_set
    except Exception as e:
        print("power lens load fail:", e); power_set = set()

    def route_of(r):
        if r["ticker"] in HOLDING_OVERRIDE: return "COMPOUNDER"   # diversified holdings (REE) misfiled as power
        if r["ticker"] in REALESTATE_OVERRIDE: return "REALESTATE" # ICB-mislabeled RE (HHS)
        if r["ticker"] in bank_set or r["ICB_Code"]==8355: return "BANK"
        if INSURANCE_ICB(r["ICB_Code"]): return "INSURANCE"   # 853x/857x: own lens (ROE-based, ROIC meaningless)
        if SECURITIES_ICB(r["ICB_Code"]): return "SECURITIES" # 877x brokers: ROE-based, cyclical cap 2
        if r["ticker"] in power_set: return "POWER"
        if r["ticker"] in COMMODITY_MAP or r["ticker"] in SUGAR_SET or r["ticker"] in CEMENT_SET: return "CYCLICAL"
        if r["ICB_Code"]==8633: return "REALESTATE"   # L8 asset-play: deferred-rev/lumpy-CFO -> own lens
        return "COMPOUNDER"
    df["route"] = df.apply(route_of, axis=1)

    res = df.apply(lambda r: pd.Series(rate_row(r)), axis=1)
    out = pd.concat([df, res], axis=1)

    cols = ["ticker","route","rating","core_score","stab","moat","note","redflag",
            "ROIC3Y","ROIC_Min3Y","ROE_Min3Y","ROE_Trailing","ROE3Y","ROIC_Trailing","neg_q","ROE_Min5Y","ROIC_Min5Y","STLTDebt_Eq_P0","Debt_Eq_P0","cfo_np","FSCORE","GPM_P0",
            "PB","pb_z","PE","drop_pct","liq_bn","ICB_Code"]
    out = out[cols].sort_values(["route","rating","core_score"], ascending=[True,True,False])
    os.makedirs(os.path.join(WORKDIR,"data"), exist_ok=True)
    path = os.path.join(WORKDIR,"data","rating_8l.csv")
    try:
        out.to_csv(path, index=False)
    except PermissionError:
        path = os.path.join(WORKDIR,"data","rating_8l_NEW.csv")
        out.to_csv(path, index=False)
        print(f"[!] data/rating_8l.csv is locked (open in Excel?) -> wrote {os.path.basename(path)} instead")

    # ---- summary ----
    print(f"rated {len(out)} tickers -> data/rating_8l.csv")
    print("\ndistribution by route x rating:")
    print(pd.crosstab(out["route"], out["rating"]).to_string())
    known = ["VNM","FPT","MWG","HPG","QTP","MBB","VCB","ACB","VCS","DGC","REE","PVT","GAS","PNJ","DHC","BMP","NT2","DRI","PHR","SAB","VHC","GVR"]
    sub = out[out["ticker"].isin(known)].copy()
    sub["k"] = pd.Categorical(sub["ticker"], categories=known, ordered=True)
    sub = sub.sort_values("k")
    print("\nknown names (review):")
    print(sub[["ticker","route","rating","core_score","moat","ROIC3Y","ROE_Trailing","ROE_Min3Y","STLTDebt_Eq_P0","cfo_np","FSCORE","note","redflag"]].to_string(index=False))

    # ---- TOP 30 INVESTABLE (rating<=3), ranked by rating then a route-aware quality score ----
    LIQ_MIN = 3.0   # bn VND/day — needs to be actually tradable to count as "investable"
    FIN = {"BANK","INSURANCE","SECURITIES"}
    def qual(r):
        if r["route"] in FIN:   # financials: scorecard N/A -> quality = ROE (trailing, fallback 3Y)
            roe = r["ROE_Trailing"] if pd.notna(r["ROE_Trailing"]) else r["ROE3Y"]
            return min(12.0, (roe if pd.notna(roe) else 0)*60)   # ROE 0.20 -> 12 (≈ top core_score)
        return r["core_score"]
    inv = out[(out["rating"]<=3) & (out["liq_bn"]>=LIQ_MIN)].copy()
    inv["qual"] = inv.apply(qual, axis=1)
    # STABILITY is prioritized (user): quality is discounted by how stable/through-cycle it is, so a
    # cyclical-peak high-ROE broker (VIX/CTS) ranks BELOW a stable compounder of similar headline quality.
    inv["qual_adj"] = (inv["qual"] * inv["stab"]).round(1)
    inv["rank_score"] = (3 - inv["rating"])*100 + inv["qual_adj"]   # rating dominates; stability-adj quality breaks ties
    top = inv.sort_values(["rank_score","liq_bn"], ascending=False).head(30).reset_index(drop=True)
    top.index = top.index + 1
    top.to_csv(os.path.join(WORKDIR,"data","rating_8l_top30.csv"))
    # valuation state per name (axis 2): PB vs its OWN 5Y history (pb_z) + drawdown. For quality names
    # "cheap" = pb_z<0 (below own normal), DISLOCATED = pb_z<=-1 (the golden-cell buy zone, ~+59%/96% 12M).
    def val_state(r):
        z, roemin5 = r["pb_z"], r.get("ROE_Min5Y", np.nan)
        if pd.isna(z): return "n/a"
        # GUARD (user 2026-06-02): if the company DESTROYED capital in 5Y (ROE_Min5Y<0), its book value
        # is unreliable and its historical PB was distorted (HAG: PB_MA5Y 1.66 from a distressed/eroding
        # past) -> a low pb_z is a STATISTICAL ARTIFACT, not real cheapness. Flag, don't treat as buy.
        if z <= -0.3 and pd.notna(roemin5) and roemin5 < 0: return "0_PBz-TRAP(capital-destroyer)"
        if z <= -1.0: return "1_DISLOCATED"        # cheap vs own history = buy zone (book trustworthy)
        if z <= -0.3: return "2_below-avg"
        if z <=  0.6: return "3_fair"
        return "4_rich"
    out["val"] = out.apply(val_state, axis=1)
    top = top.merge(out[["ticker","val"]], on="ticker", how="left")
    print(f"\n=== TOP 30 INVESTABLE (rating<=3, liq>={LIQ_MIN}bn) — ranked by rating x STABILITY-adj quality ===")
    show = top[["ticker","route","rating","qual_adj","moat","ROE_Trailing","PB","pb_z","drop_pct","val"]].copy()
    print(show.to_string())

    # ---- BUY-NOW: quality (rating<=3) x cheap-vs-own-history (pb_z<=-0.3) x BOOK TRUSTWORTHY x liquid ----
    cheap = out[(out["rating"]<=3) & (out["liq_bn"]>=LIQ_MIN) & (out["pb_z"]<=-0.3)].copy()
    trap = cheap[cheap["ROE_Min5Y"]<0]                       # capital-destroyers -> pb_z is an artifact
    buy  = cheap[~(cheap["ROE_Min5Y"]<0)].copy()             # book trustworthy (no 5Y capital destruction)
    buy = buy.sort_values(["rating","pb_z"]).reset_index(drop=True); buy.index = buy.index+1
    buy.to_csv(os.path.join(WORKDIR,"data","rating_8l_buynow.csv"))
    print(f"\n=== BUY-NOW (rating<=3 + pb_z<=-0.3 + ROE_Min5Y>=0 book-trustworthy + liq>={LIQ_MIN}bn) — {len(buy)} names ===")
    if len(buy):
        print(buy[["ticker","route","rating","moat","stab","PB","pb_z","drop_pct","ROE_Trailing","ROE_Min5Y","liq_bn","val"]].to_string())
    else:
        print("none — quality names not dislocated right now (market rich). Wait for the pitch.")
    if len(trap):
        print(f"\n  [EXCLUDED as PB_z-traps — capital-destroyers (ROE_Min5Y<0), distorted book/PB]: "
              + ", ".join(f"{t.ticker}(z{t.pb_z:.1f},ROEmin5 {t.ROE_Min5Y:.0%})" for t in trap.itertuples()))

    # ====== CANONICAL 2-AXIS SCREENER — the DEFAULT actionable list (user 2026-06-14) ======
    # A quality-only list (top-30 by rating) surfaces uninvestable names (e.g. MCH/VTP at top-0.2% PB) and
    # is low-value as a buy list. The default must be BOTH axes: quality (rating<=3, MOAT-AUDITED) × value
    # (pb_z vs own history) × liquidity, split into actionability zones so the reader sees what to BUY now
    # vs what is great-but-too-expensive (WATCH-RICH) vs a statistical pb_z trap.
    scr = out[(out["rating"] <= 3) & (out["liq_bn"] >= LIQ_MIN)].copy()
    scr["moat5f"] = scr["ticker"].map(lambda t: MOAT_TIER.get(t, "—"))   # 5F-audited tier ("—" = chưa audit)
    def _zone(r):
        v = str(r["val"])
        if v.startswith("0_"): return "4_TRAP"            # pb_z artifact (capital-destroyer) — not a buy
        if v.startswith(("1_", "2_")): return "1_BUY-NOW" # cheap vs own history (pb_z<=-0.3) + book-trustworthy
        if v.startswith("3_"): return "2_ACCUMULATE"      # fairly priced quality
        return "3_WATCH-RICH"                              # rich (pb_z>0.6): great business, DON'T chase
    scr["zone"] = scr.apply(_zone, axis=1)
    scr = scr.sort_values(["zone", "rating", "pb_z"]).reset_index(drop=True); scr.index = scr.index + 1
    scr[["ticker","route","rating","moat5f","pb_z","val","drop_pct","ROE_Trailing","liq_bn","zone"]].to_csv(
        os.path.join(WORKDIR,"data","rating_8l_screener.csv"))
    print(f"\n=== 2-AXIS SCREENER (DEFAULT) — quality(rating<=3, moat-audited) × value × liq>={LIQ_MIN}bn ===")
    for z, lbl in [("1_BUY-NOW","🟢 BUY-NOW  (rẻ-vs-lịch-sử pb_z<=-0.3 + book-OK)"),
                   ("2_ACCUMULATE","🟡 ACCUMULATE  (định giá hợp lý)"),
                   ("3_WATCH-RICH","🔴 WATCH-RICH  (chất lượng nhưng ĐẮT pb_z>0.6 — đừng đuổi)")]:
        zz = scr[scr["zone"] == z]
        print(f"\n  {lbl} — {len(zz)} mã:")
        if len(zz):
            print(zz[["ticker","route","rating","moat5f","pb_z","drop_pct","liq_bn"]].head(25).to_string())

if __name__ == "__main__":
    main()
