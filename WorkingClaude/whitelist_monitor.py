#!/usr/bin/env python3
"""
whitelist_monitor.py
====================
Daily/weekly monitoring of long-hold whitelist positions.

Checks each whitelist ticker for:
  - Current FA tier (vs baseline expectation)
  - Price vs MA50 / MA200
  - Drawdown from all-time peak
  - 1Y relative strength vs VNINDEX
  - Sector cycle position (for cyclical names like DGC, CSV)
  - Recent news flags (manual input)

Outputs colored alerts: 🟢 HOLD / 🟡 WATCH / 🔴 REVIEW

Usage:
  python whitelist_monitor.py                    # snapshot today
  python whitelist_monitor.py 2026-05-15        # specific date
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"

# ─── WHITELIST DEFINITION (FINAL 2026-05-15) ─────────────────────────────
WHITELIST = {
    # Tier 1 — True compounders, no-sell core (32% NAV)
    "MBB":  {"tier":"Tier1", "sector":"BANK",            "target_pct":8, "expected_fa":"A", "notes":""},
    "FPT":  {"tier":"Tier1", "sector":"IT_SERVICES",     "target_pct":8, "expected_fa":"A",
             "notes":"Tier 1 - FTel deconsolidation override active until 2027-04-30",
             "fa_override": {
                 "reason": "FTel deconsolidation 2026-01-01 (Bộ Công an 50.2%): equity method causes artificial revenue YoY drop; Q1 2026 core ex-FTel +8.5% YoY, tech segment 87% rev / 56% profit still strong",
                 "expires": "2027-04-30",   # ~Q1 2027 release lifts FA back to A
                 "suppress_if_tier_in": ["B"],   # only override if FA still B; if drops to C+, alert
             }},
    "REE":  {"tier":"Tier1", "sector":"INDUSTRIALS",     "target_pct":6, "expected_fa":"A", "notes":"Multi-engine: M&E+RE+Power+Water"},
    "MCH":  {"tier":"Tier1", "sector":"CONSUMER",        "target_pct":5, "expected_fa":"A", "notes":"Masan brand pricing"},
    # Tier 2 — Quality cyclical or sector-specific (19% NAV)
    "HDG":  {"tier":"Tier2", "sector":"REAL_ESTATE_DEV", "target_pct":4, "expected_fa":"A", "notes":"Multi-engine: RE + Renewable + Retail"},
    "PVT":  {"tier":"Tier2", "sector":"OIL_TANKER",      "target_pct":5, "expected_fa":"A", "notes":"PVN subsidiary, oil tanker bull post-Russia sanctions"},
    "DRI":  {"tier":"Tier2", "sector":"RUBBER",          "target_pct":3, "expected_fa":"A", "notes":"Fresh A 2026Q1, small cap (liquidity cap)"},
    "DCM":  {"tier":"Tier2", "sector":"FERTILIZER",      "target_pct":4, "expected_fa":"A", "notes":"Commodity bull, peak warning if NP >+50% sustained"},
    "CSV":  {"tier":"Tier2", "sector":"CHEMICALS_SPEC",  "target_pct":3, "expected_fa":"A", "notes":"Specialty chemicals (less cyclical than DGC)"},
    # Hold-only — mature, don't add
    "SIP":  {"tier":"Hold",  "sector":"KCN",             "target_pct":3, "expected_fa":"A", "notes":"Mature compounder - hold existing only"},
    # Special — concentrated high-conviction bet
    "DGC":  {"tier":"Special","sector":"CHEMICALS_P4",   "target_pct":40,"expected_fa":"A", "notes":"⚠ Political risk + P4 catalyst (Sunsirs uptrend confirmed, PAT +20% Q2 guide)"},
}
# Dropped from earlier consideration: CTR (PE expensive), BMP (oil-input cycle peak), GMD (PE expensive vs PVT), HHV (low quality BOT), TV1 (thin liq + FA E)

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── PULL CURRENT DATA ───────────────────────────────────────────────────
snap_dt = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else pd.Timestamp.today().normalize()
print(f"Whitelist Monitor — Snapshot: {snap_dt.date()}")
print(f"{'─'*100}")

tickers_str = "','".join(WHITELIST.keys())
print(f"\nPulling latest market data for {len(WHITELIST)} whitelist tickers ...")

# Price data: last 500 trading days for MA200 + 1Y relative
sql_price = f"""
SELECT t.ticker, t.time, t.Close
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('{tickers_str}','VNINDEX')
  AND t.time >= DATE_SUB("{snap_dt.date()}", INTERVAL 500 DAY)
  AND t.time <= "{snap_dt.date()}"
  AND t.Close > 0
ORDER BY t.ticker, t.time
"""
px = bq_query(sql_price)
px["time"] = pd.to_datetime(px["time"])
# Overlay the freshest session from ticker_1m for stock tickers (ticker ingests ~22:30 VN;
# ticker_1m is intraday-fresh). VNINDEX is NOT in ticker_1m, so it keeps ticker's latest.
# Safe/additive: dedupe keeps one row when ticker_1m's max == ticker's max (no-op).
fresh = bq_query(f"""
SELECT t.ticker, t.time, t.Close
FROM tav2_bq.ticker_1m AS t
WHERE t.ticker IN ('{tickers_str}')
  AND t.time = (SELECT MAX(t2.time) FROM tav2_bq.ticker_1m AS t2)
  AND t.Close > 0
""")
if fresh is not None and len(fresh):
    fresh["time"] = pd.to_datetime(fresh["time"])
    px = (pd.concat([px, fresh], ignore_index=True)
            .drop_duplicates(subset=["ticker", "time"], keep="last")
            .sort_values(["ticker", "time"]))
print(f"  Price rows: {len(px):,}")

# FA ratings (latest)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time"])
latest_q = fa["quarter"].max()
fa_latest = fa[fa["ticker"].isin(WHITELIST.keys()) & (fa["quarter"]==latest_q)]
print(f"  FA latest quarter: {latest_q} ({len(fa_latest)} of {len(WHITELIST)} found)")

# State
sql_state = f'SELECT s.time, s.state, s.state_raw FROM tav2_bq.vnindex_5state AS s WHERE s.time <= "{snap_dt.date()}" ORDER BY s.time DESC LIMIT 30'
state = bq_query(sql_state)
state["time"] = pd.to_datetime(state["time"])
cur_state = state.iloc[0]
print(f"  Current 5-state: state={cur_state['state']} (raw={cur_state['state_raw']}) @ {cur_state['time'].date()}")

# ─── PER-TICKER MONITORING ───────────────────────────────────────────────
print(f"\n{'='*100}")
print(f"  WHITELIST POSITIONS — Daily Health Check")
print(f"{'='*100}\n")
print(f"  {'Ticker':<7}{'Tier':<10}{'Price':>10}{'%MA50':>9}{'%MA200':>9}{'DD peak':>10}{'1Y vs VNI':>12}{'FA':>4}  Status")

alerts = []
for tk, meta in WHITELIST.items():
    tk_px = px[px["ticker"]==tk].sort_values("time")
    if len(tk_px) == 0:
        print(f"  {tk:<7}{meta['tier']:<10}{'NO DATA':>10}")
        continue
    cur_px = tk_px["Close"].iloc[-1]
    cur_dt = tk_px["time"].iloc[-1]

    # MA50, MA200
    ma50 = tk_px["Close"].rolling(50, min_periods=30).mean().iloc[-1]
    ma200 = tk_px["Close"].rolling(200, min_periods=100).mean().iloc[-1]
    pct_ma50 = (cur_px / ma50 - 1) * 100 if pd.notna(ma50) else np.nan
    pct_ma200 = (cur_px / ma200 - 1) * 100 if pd.notna(ma200) else np.nan

    # Drawdown from 2Y peak
    peak_2y = tk_px["Close"].rolling(500, min_periods=100).max().iloc[-1]
    dd_peak = (cur_px / peak_2y - 1) * 100 if pd.notna(peak_2y) else 0

    # 1Y relative vs VNI
    vni_px = px[px["ticker"]=="VNINDEX"].sort_values("time")
    if len(tk_px) >= 252 and len(vni_px) >= 252:
        tk_1y_ago = tk_px["Close"].iloc[-252]
        vni_1y_ago = vni_px["Close"].iloc[-252]
        tk_ret_1y = (cur_px / tk_1y_ago - 1) * 100
        vni_ret_1y = (vni_px["Close"].iloc[-1] / vni_1y_ago - 1) * 100
        rel_1y = tk_ret_1y - vni_ret_1y
    else:
        rel_1y = np.nan

    # FA tier
    fa_row = fa_latest[fa_latest["ticker"]==tk]
    fa_tier = fa_row["tier"].iloc[0] if len(fa_row) > 0 else "N/A"

    # Status determination
    flags = []
    status_color = "🟢"
    # Check for active FA override (e.g. FPT FTel deconsolidation)
    override = meta.get("fa_override")
    override_active = False
    if override:
        expires = pd.Timestamp(override["expires"])
        if snap_dt <= expires and fa_tier in override.get("suppress_if_tier_in", []):
            override_active = True
    if fa_tier in ("D","E"):
        status_color = "🔴"; flags.append(f"FA={fa_tier} CRITICAL")
    elif fa_tier == "C":
        status_color = "🟡"; flags.append(f"FA dropped to C")
    elif fa_tier != meta["expected_fa"] and fa_tier in ("A","B"):
        if override_active:
            flags.append(f"FA={fa_tier} [OVERRIDE: {override['reason'][:50]}...]")
        else:
            flags.append(f"FA={fa_tier}")

    if dd_peak < -50:
        status_color = "🔴" if status_color != "🔴" else status_color
        flags.append(f"DD {dd_peak:.0f}% from peak")
    elif dd_peak < -30:
        if status_color == "🟢": status_color = "🟡"
        flags.append(f"DD {dd_peak:.0f}%")

    if pd.notna(pct_ma200) and pct_ma200 < -10:
        if status_color == "🟢": status_color = "🟡"
        flags.append(f"below MA200 {pct_ma200:.0f}%")

    if pd.notna(rel_1y) and rel_1y < -30:
        if status_color == "🟢": status_color = "🟡"
        flags.append(f"1Y rel {rel_1y:+.0f}pp")

    flag_str = " | ".join(flags) if flags else "OK"
    print(f"  {tk:<7}{meta['tier']:<10}{cur_px:>10.0f}{pct_ma50:>+8.1f}%{pct_ma200:>+8.1f}%{dd_peak:>+9.1f}%{rel_1y:>+11.1f}%{fa_tier:>4}  {status_color} {flag_str}")
    if status_color != "🟢":
        alerts.append({"ticker":tk, "color":status_color, "fa":fa_tier, "dd":dd_peak, "flags":flag_str})

# ─── ACTIVE FA OVERRIDES ─────────────────────────────────────────────────
active_overrides = [(tk, m) for tk, m in WHITELIST.items()
                    if m.get("fa_override") and snap_dt <= pd.Timestamp(m["fa_override"]["expires"])]
if active_overrides:
    print(f"\n{'='*100}")
    print(f"  ACTIVE FA-TIER OVERRIDES (model false negatives — keep Tier 1 status)")
    print(f"{'='*100}")
    for tk, m in active_overrides:
        ov = m["fa_override"]
        print(f"\n  {tk} — override until {ov['expires']}")
        print(f"    Reason: {ov['reason']}")
        print(f"    Suppress if FA in: {ov.get('suppress_if_tier_in', [])}")
        print(f"    Action: ignore FA tier flag during bridge; treat as Tier 1 compounder")
        print(f"            apply normal exit if FA drops further outside override scope")

# ─── DGC SPECIAL CASE DEEP-DIVE ──────────────────────────────────────────
print(f"\n{'='*100}")
print(f"  DGC SPECIAL MONITOR — Political Risk + P4 Catalyst Pending")
print(f"{'='*100}")
dgc_px = px[px["ticker"]=="DGC"].sort_values("time").tail(120)  # last 6 months
if len(dgc_px) > 0:
    cur_dgc = dgc_px["Close"].iloc[-1]
    peak_dgc = dgc_px["Close"].max()
    dd_dgc = (cur_dgc / peak_dgc - 1) * 100
    ma50_dgc = dgc_px["Close"].rolling(50, min_periods=30).mean().iloc[-1]
    above_ma50_days = (dgc_px["Close"].tail(40) > dgc_px["Close"].rolling(50, min_periods=30).mean().tail(40)).sum()
    print(f"  Current price: {cur_dgc:.0f}")
    print(f"  6M peak: {peak_dgc:.0f} | drawdown: {dd_dgc:+.1f}%")
    print(f"  MA50: {ma50_dgc:.0f} | price vs MA50: {(cur_dgc/ma50_dgc - 1)*100:+.1f}%")
    print(f"  Days above MA50 in last 40d: {above_ma50_days}")
    print(f"\n  DGC catalyst checklist:")
    print(f"    [ ] FA tier next quarter (2026-Q2) confirms A: status pending Q2 earnings report")
    print(f"    [ ] Price above MA50 for 4+ weeks: {'✓' if above_ma50_days >= 20 else '✗'} (currently {above_ma50_days}/40d)")
    print(f"    [ ] P4 spot prices uptrend confirmed: requires external commodity data — user input")
    print(f"    [ ] Political news cycle ended (6+ weeks no investigation news): user manual confirm")
    print(f"    [ ] Q2 2026 earnings show P4 unit price recovery: pending earnings release ~Aug 2026")
    print(f"\n  Action: HOLD existing position (if any). DO NOT add/average down until 3+ checklist items confirmed.")

# ─── SECTOR CYCLE STATUS ─────────────────────────────────────────────────
print(f"\n{'='*100}")
print(f"  SECTOR CYCLE STATUS (for cyclical whitelist holdings)")
print(f"{'='*100}")
sec_cycle_path = "data/lh_v3_sector_cycle.csv"
if os.path.exists(sec_cycle_path):
    sec = pd.read_csv(sec_cycle_path)
    latest_sec_q = sec["quarter"].max()
    recent = sec[sec["quarter"]==latest_sec_q]
    relevant_groups = {"CHEMICAL", "REIT_RES", "BANK"}  # for our whitelist
    print(f"\n  Latest quarter: {latest_sec_q}")
    print(f"  {'Group':<15}{'cycle_recovery':>17}{'cycle_overheat':>17}{'NP_yoy_med':>13}{'ret_6m_med':>13}")
    for _, r in recent.iterrows():
        if r["cmd_group"] in relevant_groups:
            print(f"  {r['cmd_group']:<15}{r['cycle_recovery']:>+16.2f}{r['cycle_overheat']:>+16.2f}{r['S_NP_yoy_med']*100:>+12.1f}%{r['S_ret_6m_med']*100:>+12.1f}%")
else:
    print(f"\n  Sector cycle file not found — skip")

# ─── SUMMARY ─────────────────────────────────────────────────────────────
print(f"\n{'='*100}")
n_green = len(WHITELIST) - len(alerts)
n_yellow = sum(1 for a in alerts if a["color"]=="🟡")
n_red = sum(1 for a in alerts if a["color"]=="🔴")
print(f"  Summary: 🟢 {n_green} HOLD  |  🟡 {n_yellow} WATCH  |  🔴 {n_red} REVIEW")

if alerts:
    print(f"\n  Action items:")
    for a in alerts:
        print(f"    {a['color']} {a['ticker']}: {a['flags']}")

print(f"\nDone. Re-run weekly or when major news.")
