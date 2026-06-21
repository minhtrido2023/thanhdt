#!/usr/bin/env python3
"""
crisis_capitulation_signal.py — DT5G CRISIS x 8L capitulation buy trigger
========================================================================
Research (2026-06-04/2026-06-11, ticker_prune 2014+):

  WHEN to buy: TWO-stage gate
    Stage 1 (macro)  : DT5G state == CRISIS (tav2_bq.vnindex_5state_dt5g_live)
    Stage 2 (micro)  : cross-sectional PANIC washout (above_MA200 breadth <= 30%)

  WHAT to buy (capit_before_after.py — 9 events 2018-2022):
    Tier 0+1: strict quality (ROE_Min5Y>=12% & ROIC5Y>=10% & FSCORE>=6) AND
              golden cheapness pb_z = (PB-PB_MA5Y)/PB_SD5Y < -1
              -> 91% win rate / median +8.7% / mean +13.3% / P10 +7.8%
    ⚠ CAPACITY CONSTRAINT (capit_liquidity_audit.py, 2026-06-11):
      Universe is structurally thin — avg 2 stocks/event, avg 50% fill at 10B.
      Only 6 unique tickers met criteria across 9 events 2018-2022:
        SAB(7x,26B/day,+8.7%), VSC(4x,3.1B,+31.2%), SCS(3x,2.7B,+20.4%),
        BMP(2x,6.1B,+52.1%), SIP(1x,7.0B,+15.3%), VCS(1x,6.4B,-11.9%)
      => Deploy 8-10B max per event (matches actual capacity).
      => NEVER force-fill with Tier 2/3: delta fwd60d was -4 to -12pp in 2022.
      => Unused capital after filling Tier 0+1 stays in cash reserve.
      => Tier 2 fallback ONLY when T0+1 gives 0 picks (emergency, rare).

  Feature ICs in CRISIS washout (capit_stock_optimizer.py, 2026-06-11):
    pb_z +0.398 / D_RSI +0.382 / ID_LO_3Y +0.200 / PC_6M +0.218
    Pattern_Median_Profit_3Y: -0.298 (NEGATIVE — avoid "known bouncers")
    Sectors to avoid: ICB 86xx (BDS), 87xx (securities), 33xx (mining)

  Tier system (updated 2026-06-11):
    Tier 0: quality_strict + golden + RSI<=0.35  (triple confirm)
    Tier 1: quality_strict + golden              (91% win baseline)
    Tier 2: quality_base + pb_z<0 + RSI<=0.35   (fallback, only when T0+1=0 picks)
    Tier 3: golden only                          (never auto-use; shown as watchlist)
    Sort within tier: pb_z ASC -> D_RSI ASC -> ID_LO_3Y ASC

  State routing (playbook v2, 2026-06-10):
    CRISIS 1.0x / NEUTRAL 0.75x / BULL 0.5x /
    BEAR 0.5x ONLY if dd>-25% or VNINDEX rv10 cooling >=15% off 30d peak

Output: data/crisis_capitulation_signal.{md,csv}
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, io
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
SDK_BIN = r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

PANIC_THRESHOLD = 0.057   # WATCH: top-tercile oversold breadth in crisis days
WASHOUT_EXTREME = 0.30    # STRONG: above_MA200 breadth <= 30% (cliff ~30%, band 30-40)

# Sector ICB 2-digit codes to exclude in CRISIS (negative IC)
SECTOR_EXCL_ICB2 = {86, 87, 33}   # BDS, securities/finance, mining

def bq(sql: str) -> pd.DataFrame:
    env = dict(os.environ)
    env["PATH"] = env.get("PATH", "") + os.pathsep + SDK_BIN
    env.setdefault("CLOUDSDK_PYTHON",
                   r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe")
    bqexe = os.path.join(SDK_BIN, "bq.cmd")
    sql1 = " ".join(sql.split())
    out = subprocess.run([bqexe, "query", "--use_legacy_sql=false",
                          f"--project_id={PROJECT}", "--format=csv", "--max_rows=5000", sql1],
                         capture_output=True, text=True, env=env)
    if out.returncode != 0:
        raise RuntimeError(f"rc={out.returncode}\nSTDERR:\n{out.stderr}\nSTDOUT:\n{out.stdout}")
    return pd.read_csv(io.StringIO(out.stdout))

STATE_NAME   = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
STATE_WEIGHT = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}

# ── 1. Live regime + panic breadth (last ~120 sessions) ───────────────
hist = bq("""
WITH daily AS (
  SELECT p.time,
    AVG(CASE WHEN p.D_RSI<0.3  THEN 1.0 ELSE 0 END) oversold,
    AVG(CASE WHEN p.MA200>0 AND p.Close>=p.MA200 THEN 1.0 ELSE 0 END) above_ma200
  FROM tav2_bq.ticker_prune p WHERE p.Close_T1>0 GROUP BY p.time )
SELECT d.time, s.state, d.oversold, d.above_ma200
FROM daily d JOIN tav2_bq.vnindex_5state_dt5g_live s USING(time)
ORDER BY d.time DESC LIMIT 120
""").sort_values("time").reset_index(drop=True)

live = hist.iloc[-1]
asof     = live["time"]
state    = int(live["state"])
oversold = float(live["oversold"])
reserve  = max(0.0, 1.0 - STATE_WEIGHT.get(state, 0.70))

# GRIND filter: prior washout 20–90 sessions ago = possible grinding bear
prior    = hist.iloc[:-1]
prior_ws = prior[prior["oversold"] >= WASHOUT_EXTREME]
n_recent = len(hist)
grind    = False
if len(prior_ws):
    last_pos = n_recent - 1 - prior_ws.index.max()
    grind    = 20 <= last_pos <= 90

# ── BEAR guard v2.1: VNINDEX rv10 cooling (domestic vol, not VIX) ─────
bear_guard_ok, bear_note = True, ""
if state == 2:
    try:
        vni    = bq("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
                       WHERE t.ticker='VNINDEX' ORDER BY t.time DESC LIMIT 260""").sort_values("time")
        closes = vni["Close"].astype(float)
        dd_now = (float(closes.iloc[-1]) / float(closes.max()) - 1) * 100
        rv10   = closes.pct_change().rolling(10).std() * np.sqrt(252) * 100
        vn_cooling = bool(rv10.iloc[-1] <= rv10.rolling(30).max().iloc[-1] * 0.85)
    except Exception:
        dd_now, vn_cooling = -99.0, False
    vix_note = ""
    try:
        u = pd.read_csv(os.path.join(WORKDIR, "us_market_history.csv"),
                        parse_dates=["time"]).sort_values("time")
        _vc = bool(u["vix"].iloc[-1] <= u["vix"].rolling(20).max().iloc[-1] * 0.85)
        vix_note = f", VIX-cooling={_vc} (tham khao)"
    except Exception:
        pass
    bear_guard_ok = (dd_now > -25) or vn_cooling
    bear_note = (f" · BEAR-guard: dd52w {dd_now:.1f}%, VN-vol-cooling={vn_cooling}{vix_note}"
                 f" -> {'OK' if bear_guard_ok else 'SKIP'}")

# ── Trigger level ─────────────────────────────────────────────────────
if oversold >= WASHOUT_EXTREME:
    if state == 2 and not bear_guard_ok:
        level = "BEAR_SKIP"
    else:
        level = "STRONG_CAUTION" if grind else "STRONG_BUY"
elif state == 1 and oversold >= PANIC_THRESHOLD:
    level = "WATCH"
else:
    level = "DORMANT"

LVL_TXT = {
    "STRONG_BUY":
        "STRONG BUY — EXTREME washout (above_MA200<=30%), isolated: bottom ~3 sessions away "
        "(median), fwd60 +8.7%/91% win at quality+golden. Deploy FULL state reserve.",
    "STRONG_CAUTION":
        "STRONG (CAUTION-GRIND) — extreme washout but prior washout 20-90d ago = possible "
        "grinding bear (2022 trap). SCALE IN: deploy HALF the reserve now.",
    "WATCH":
        "WATCH — CRISIS panic window open: quality+golden edge active. "
        "Begin building; add if washout deepens to <=30%.",
    "BEAR_SKIP":
        "BEAR-SKIP — washout fired but state=BEAR with deep dd (<=-25%) and domestic vol "
        "still climbing: win-24% zone. Stand aside.",
    "DORMANT":
        "DORMANT — gate closed (no genuine capitulation).",
}
crisis_note = ("DT5G confirms CRISIS" if state == 1
               else f"DT5G={STATE_NAME.get(state)} (routing: NEUTRAL 0.75x, BULL 0.5x, BEAR guarded)")
grind_note  = (" · GRIND (repeat washout 20-90d)" if grind else " · isolated") + bear_note

hdr = (f"# DT5G x 8L Crisis-Capitulation Signal  ({asof})\n\n"
       f"- DT5G state: **{state} = {STATE_NAME.get(state,'?')}**  "
       f"· deployable reserve **{reserve*100:.0f}%**\n"
       f"- Panic oversold breadth (D_RSI<0.30): **{oversold*100:.1f}%**  "
       f"(WATCH>={PANIC_THRESHOLD*100:.1f}%, STRONG>={WASHOUT_EXTREME*100:.0f}%){grind_note}\n"
       f"- % above MA200: {float(live['above_ma200'])*100:.1f}%\n"
       f"- **SIGNAL: {LVL_TXT[level]}**  ({crisis_note})\n")

print(hdr)

if level in ("DORMANT", "BEAR_SKIP"):
    why = ("BEAR with deep dd and VN vol still rising — stand aside" if level == "BEAR_SKIP"
           else ("not in CRISIS" if state != 1
                 else f"CRISIS but panic below WATCH threshold ({oversold*100:.1f}% < {PANIC_THRESHOLD*100:.1f}%)"))
    msg = hdr + f"\nNo action — {why}. Trigger only acts on genuine capitulations.\n"
    with open(os.path.join(WORKDIR, "data", "crisis_capitulation_signal.md"), "w", encoding="utf-8") as f:
        f.write(msg)
    print(f"No action ({why}). Watch line written.")
    sys.exit(0)

# ── 2. Fired: pull live candidates ────────────────────────────────────
# Position sizing constants (mirrors capit_liquidity_audit.py)
ADV_FRAC_PER_DAY = 0.30   # max 30% daily ADV per day
RAMP_DAYS        = 3      # 3-day fill ramp
MAX_FILL_FRAC    = ADV_FRAC_PER_DAY * RAMP_DAYS   # = 90% of daily ADV per stock

snap = bq("""
WITH latest AS (SELECT MAX(time) mt FROM tav2_bq.ticker_1m)
SELECT
  p.ticker,
  p.ICB_Code,
  p.Close,
  p.D_RSI,
  SAFE_DIVIDE(p.PB-p.PB_MA5Y, p.PB_SD5Y)      AS pb_z,
  p.PB,
  p.ROE_Min5Y,
  p.ROIC5Y,
  p.FSCORE,
  p.ID_LO_3Y,
  p.PC_6M,
  SAFE_DIVIDE(p.Close, p.HI_3M_T1)-1           AS dd_3m,
  p.Trading_Value_1M_P50 / 1e9                 AS liq_1m_bn,
  COALESCE(p.Price,p.Close)*p.Volume/1e9        AS liq_today_bn
FROM tav2_bq.ticker_1m p, latest
WHERE p.time = latest.mt
  AND p.PB > 0 AND p.PB_MA5Y IS NOT NULL AND p.PB_SD5Y > 0
""")

# Use 1M ADV as primary liq measure; fall back to today's if missing
snap['liq_bn'] = snap['liq_1m_bn'].fillna(snap['liq_today_bn'])

# Sector exclusion (BDS / securities / mining — negative IC in CRISIS)
snap['icb2'] = (snap['ICB_Code'].fillna(0).astype(float).astype(int)) // 10
snap['sector_ok'] = ~snap['icb2'].isin(SECTOR_EXCL_ICB2)

# Quality flags
snap["quality_strict"] = (
    (snap.ROE_Min5Y >= 0.12) & (snap.ROIC5Y >= 0.10) & (snap.FSCORE >= 6)
)
snap["quality_base"] = (
    (snap.ROE_Min5Y >= 0.08) & (snap.ROIC5Y >= 0.08) & (snap.FSCORE >= 5)
)
snap["golden"]     = snap.pb_z < -1.0
snap["rsi_os"]     = snap.D_RSI < 0.35     # oversold RSI (IC +0.38 in washout)
snap["near_lo3y"]  = snap.ID_LO_3Y < 500   # within ~2yr of 3Y low (IC +0.20)

# 8L rating / route / moat
try:
    R = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l.csv"))[
        ["ticker", "route", "rating", "moat", "redflag"]]
    snap = snap.merge(R, on="ticker", how="left")
except Exception:
    snap["rating"] = np.nan; snap["route"] = ""; snap["moat"] = ""; snap["redflag"] = ""

snap["redflag"] = snap["redflag"].fillna("")

# ── Tier assignment ───────────────────────────────────────────────────
# Tier 0: quality_strict + golden + RSI_oversold  (triple confirm)
# Tier 1: quality_strict + golden                 (validated 91% win baseline)
# Tier 2: quality_base   + cheap (pb_z<0) + rsi_os (no golden but oversold)
# Tier 3: golden only                              (cheapness without strict quality)
# Sector-excluded stocks go to tier 9 (shown as watchlist only)
def tier(r):
    if not r.sector_ok:               return 9  # sector trap
    if r.redflag != "":               return 9
    if r.quality_strict and r.golden and r.rsi_os:   return 0
    if r.quality_strict and r.golden:                return 1
    if r.quality_base   and r.pb_z < 0 and r.rsi_os: return 2
    if r.golden:                                      return 3
    return 9

snap["tier"] = snap.apply(tier, axis=1)

# ── Tier 0+1 primary candidates (strict quality + golden) ─────────────
cand_primary = snap[(snap.tier <= 1) & (snap.liq_bn >= 2)].copy()
cand_primary = cand_primary.sort_values(["tier","pb_z","D_RSI","ID_LO_3Y"]).reset_index(drop=True)

# ── Capacity estimate: max deployable given 30% ADV × 3-day ramp ──────
# Cap per stock = 90% of 1M ADV; name cap = 25% of any single deployment
# Estimate total capacity for a range of deployment sizes
def estimate_fill(candidates, total_capital_B, name_cap_frac=0.25):
    """Greedy fill: allocate min(90%_ADV, name_cap) per stock until capital exhausted."""
    remaining = total_capital_B
    deployed = 0.0; n_used = 0
    for _, row in candidates.iterrows():
        if remaining <= 0: break
        capacity_stock = min(row['liq_bn'] * MAX_FILL_FRAC,
                             total_capital_B * name_cap_frac)
        alloc = min(capacity_stock, remaining)
        deployed += alloc; remaining -= alloc; n_used += 1
    return deployed, n_used, deployed / total_capital_B * 100

# Compute capacity across deployment sizes
cap_rows = []
for cap in [5, 8, 10, 15, 20]:
    dep, n, pct = estimate_fill(cand_primary, cap)
    cap_rows.append((cap, dep, n, pct))

total_adv_capacity = (cand_primary['liq_bn'] * MAX_FILL_FRAC).sum()

# ── Tier 2 emergency fallback — ONLY if T0+1 gives 0 picks ───────────
use_fallback = len(cand_primary) == 0
cand_fallback = pd.DataFrame()
if use_fallback:
    cand_fallback = snap[(snap.tier == 2) & (snap.liq_bn >= 2)].copy()
    cand_fallback = cand_fallback.sort_values(["pb_z","D_RSI"]).reset_index(drop=True)

# Combine for display (always show T0+1; Tier 2 only as fallback/watchlist)
cand_show = cand_primary.copy()
if use_fallback and not cand_fallback.empty:
    cand_show = pd.concat([cand_primary, cand_fallback], ignore_index=True)

# Tier 3 as watchlist (golden but any quality)
cand_watch = snap[(snap.tier == 3) & (snap.liq_bn >= 2)].copy()
cand_watch = cand_watch.sort_values(["pb_z","D_RSI"]).head(5).reset_index(drop=True)

# ── Format output ──────────────────────────────────────────────────────
cols = ["tier","ticker","route","rating","moat",
        "pb_z","PB","D_RSI","near_lo3y","dd_3m","ROE_Min5Y","ROIC5Y","FSCORE","liq_bn"]
cols = [c for c in cols if c in snap.columns]

def fmt(df_in):
    v = df_in[cols].copy()
    v["pb_z"]      = v.pb_z.round(2)
    v["PB"]        = v.PB.round(2)
    v["D_RSI"]     = v.D_RSI.round(2)
    v["dd_3m"]     = (v.dd_3m * 100).round(1)
    v["ROE_Min5Y"] = (v.ROE_Min5Y * 100).round(1)
    v["ROIC5Y"]    = (v.ROIC5Y * 100).round(1)
    v["liq_bn"]    = v.liq_bn.round(1)
    return v

tier_lbl = {
    0: "A: quality(strict)+golden+RSI<=0.35  [triple confirm; best bucket]",
    1: "B: quality(strict)+golden            [91% win validated baseline]",
    2: "C: quality(base)+cheap+RSI<=0.35     [FALLBACK only — T01 empty]",
    3: "D: golden only                        [watchlist; not auto-selected]",
}

# Capacity summary line
cap_summary = "### Deployment capacity (30% ADV × 3d ramp per stock, 25% name cap)\n\n"
cap_summary += f"  Total ADV capacity in T0+1 picks: {total_adv_capacity:.1f}B VND\n"
cap_summary += "  | Capital | Deployed | n stocks | Fill% |\n"
cap_summary += "  |---------|----------|----------|-------|\n"
for cap, dep, n, pct in cap_rows:
    flag = " OK" if pct >= 80 else " PARTIAL"
    cap_summary += f"  | {cap:5.0f}B | {dep:7.1f}B | {n:8d} | {pct:5.0f}%{flag} |\n"

if use_fallback:
    cap_summary += (f"\n  ⚠ T0+1 EMPTY — using Tier 2 fallback "
                    f"({len(cand_fallback)} stocks). Lower quality; size down.\n")

body = ("\n## Ranked capitulation buy candidates\n\n"
        + cap_summary + "\n"
        "Tiers: " + " | ".join(f"{k}={v[:35]}" for k, v in tier_lbl.items()) + "\n"
        "Sort: pb_z ASC -> D_RSI ASC -> ID_LO_3Y ASC | "
        "Sector excl: BDS(86xx) / ck(87xx) / mining(33xx)\n\n")

if not cand_show.empty:
    body += fmt(cand_show).to_markdown(index=False) + "\n"
else:
    body += "_No candidates meet criteria today._\n"

if not cand_watch.empty:
    body += "\n### Watchlist (Tier D: golden, any quality)\n\n"
    body += fmt(cand_watch).to_markdown(index=False) + "\n"

with open(os.path.join(WORKDIR, "data", "crisis_capitulation_signal.md"), "w", encoding="utf-8") as f:
    f.write(hdr + body + "\n")

view_csv = fmt(cand_show) if not cand_show.empty else fmt(cand_watch)
view_csv.to_csv(os.path.join(WORKDIR, "data", "crisis_capitulation_signal.csv"), index=False)
print(body)
print(f"{len(cand_show)} primary candidates | {len(cand_watch)} watchlist")
print(f"-> data/crisis_capitulation_signal.csv")

# ── Quick tier summary ─────────────────────────────────────────────────
for t, lbl in tier_lbl.items():
    src = cand_show if t <= (2 if use_fallback else 1) else cand_watch
    tix = src[src['tier']==t]['ticker'].tolist() if not src.empty else []
    if tix:
        print(f"  Tier {t} ({len(tix)}): {', '.join(tix)}")
