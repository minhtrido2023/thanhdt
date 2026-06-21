import os
#!/usr/bin/env python3
"""cheap_pb_floor.py — 8L BUY-NOW alerter: rating (quality) × PB-floor (valuation) × Ngũ Hành (timing).

Consumes data/rating_8l.csv (run rating_8l.py FIRST). The two-axis edge is backtest-validated
(2026-06-02, fwd-12M): COMBINED (rating≤3 + pb_z≤-1 + book-trustworthy) = +18.6%/70.5%win/-3.7%p25,
beating quality-only (+9.5%) and dislocation-only (+14.3%). Book guard is essential — capital-destroyer
dislocations (ROE_Min5Y<0, e.g. HAG) are a STATISTICAL TRAP (+8.8% ≈ baseline), excluded here.

Tiers (rating × valuation), all require book-trustworthy (ROE_Min5Y≥0) + liquidity:
  🏆 GOLDEN  rating 1 + DISLOCATED (pb_z≤-1)    — top quality at a genuine dislocation
  🔥 STRONG  rating 2 + DISLOCATED
  💧 SPEC    rating 3 + DISLOCATED               — speculative dislocation (lower conviction)
  👀 ACCUM   rating 1-2 + below-avg (pb_z -1..-0.3)
  ⛔ TRAP    pb_z≤-0.3 & ROE_Min5Y<0             — capital-destroyer, book unreliable -> NEVER alert

The signal is CONTRARIAN: shines in/after corrections, lags euphoric momentum bulls (2017). So the
market state (Ngũ Hành) gates the *framing*: in BULL/EX-BULL (state≥4) alerts carry a "lags-in-euphoria"
caution; in CRISIS/BEAR (state≤2) it flags the best contrarian window.

Telegram-alerts NEW entries into GOLDEN/STRONG vs last run. Usage:
  python cheap_pb_floor.py [--always] [--no-telegram] [--min-liq 3.0]
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, argparse, datetime, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))
RATING_CSV = os.path.join(WORKDIR, "data", "rating_8l.csv")
PREV = os.path.join(WORKDIR, "data", "cheap_pb_floor_prev.csv")
CUR  = os.path.join(WORKDIR, "data", "cheap_pb_floor.csv")

PBZ_DISLOC = -1.0    # cheap vs OWN 5y history = dislocation
PBZ_BELOW  = -0.3    # below own average (accumulate)

TIER_RANK = {"GOLDEN":4, "STRONG":3, "SPEC":2, "ACCUM":1, "":0}
TIER_EMO  = {"GOLDEN":"🏆", "STRONG":"🔥", "SPEC":"💧", "ACCUM":"👀"}
STATE_LBL = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=10', capture_output=True, text=True, timeout=120, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    return pd.read_csv(StringIO(r.stdout.strip())) if r.stdout.strip() else None

def ngu_hanh_state():
    # DT5G is the production Ngũ Hành foundation for ALL decisions (user-confirmed 2026-06-02).
    # Read the DT5G series explicitly — the canonical `vnindex_5state` table is NOT DT5G (only ~65%
    # historical match; appears to still serve v3.4b). All gating must align to DT5G.
    try:
        d = bq("SELECT state FROM tav2_bq.vnindex_5state_dt5g_live ORDER BY time DESC LIMIT 1")
        return int(d["state"].iloc[0])
    except Exception as e:
        print("Ngũ Hành (DT5G) state read failed:", e); return None

def classify(r, min_liq):
    rating, z, roemin5, liq = r["rating"], r["pb_z"], r["ROE_Min5Y"], r["liq_bn"]
    if pd.isna(z) or pd.isna(rating): return ""
    if not (pd.notna(liq) and liq >= min_liq): return ""
    if rating > 3: return ""                                   # investable only
    if pd.notna(roemin5) and roemin5 < 0:                      # capital-destroyer
        return "TRAP" if z <= PBZ_BELOW else ""
    if z <= PBZ_DISLOC:
        return {1:"GOLDEN", 2:"STRONG", 3:"SPEC"}.get(int(rating), "")
    if z <= PBZ_BELOW and rating <= 2:
        return "ACCUM"
    return ""

def main(always, telegram, min_liq):
    today = str(datetime.date.today())
    if not os.path.exists(RATING_CSV):
        print(f"ERROR: {RATING_CSV} not found — run `python rating_8l.py` first."); sys.exit(1)
    df = pd.read_csv(RATING_CSV)
    df["tier"] = df.apply(lambda r: classify(r, min_liq), axis=1)
    traps = df[df["tier"] == "TRAP"].copy()
    df = df[df["tier"].isin(TIER_RANK) & (df["tier"] != "") & (df["tier"] != "TRAP")].copy()
    df["trank"] = df["tier"].map(TIER_RANK)
    # within-tier: cheapest vs self first, higher stability first
    df = df.sort_values(["trank","stab","pb_z"], ascending=[False,False,True]).reset_index(drop=True)

    state = ngu_hanh_state()
    slbl  = STATE_LBL.get(state, "?")
    euphoric = (state is not None and state >= 4)
    stress   = (state is not None and state <= 2)

    # ---- diff vs baseline ----
    prev_rank = {}
    if os.path.exists(PREV):
        p = pd.read_csv(PREV); prev_rank = {row["ticker"]: TIER_RANK.get(str(row["tier"]),0) for _,row in p.iterrows()}
    alerts = []   # NEW/upgraded into GOLDEN/STRONG
    for _, r in df.iterrows():
        cr, pr = TIER_RANK[r["tier"]], prev_rank.get(r["ticker"], 0)
        if cr >= TIER_RANK["STRONG"] and cr > pr:
            alerts.append((r, "NEW" if pr == 0 else "↑"))
    df.to_csv(CUR, index=False); df.to_csv(PREV, index=False)

    # ---- console ----
    print(f"=== 8L BUY-NOW {today} | Ngũ Hành: {slbl}({state}) | min_liq {min_liq}bn ===")
    if euphoric: print("  ⚠ euphoric bull — contrarian dislocation signal historically LAGS (cf 2017); size cautiously.")
    if stress:   print("  🩸 stress regime — historically the BEST contrarian-buy window.")
    for _, r in df.iterrows():
        print(f"  {TIER_EMO[r['tier']]} {r['tier']:<7} {r['ticker']:<5} R{int(r['rating'])} {r['route'][:4]:<4} "
              f"PB {r['PB']:.2f} z{r['pb_z']:+.1f} drop {r['drop_pct']:+.0f}% stab {r['stab']:.2f} "
              f"ROEmin5 {r['ROE_Min5Y']*100:+.0f}% liq {r['liq_bn']:.0f}tỷ [{r['moat']}]")
    if len(traps):
        print(f"  ⛔ TRAP excluded (capital-destroyer, pb_z artifact): " + ", ".join(traps["ticker"]))
    if alerts:
        print(f"-- {len(alerts)} NEW into GOLDEN/STRONG --")

    first_run = not prev_rank
    if first_run and not always:
        print("(first run — baseline stored, no alert)"); return

    # ---- Telegram ----
    if telegram and (alerts or always):
        hdr = f"<b>💎 8L BUY-NOW — {today}</b>\nNgũ Hành: <b>{slbl}</b>"
        if euphoric: hdr += "  ⚠️ <i>euphoric — contrarian lags (cf 2017), size nhỏ</i>"
        elif stress: hdr += "  🩸 <i>stress = cửa sổ mua contrarian tốt nhất</i>"
        lines = [hdr]
        if alerts:
            lines.append("\n<b>⚡ MỚI vào vùng chất-lượng-rẻ:</b>")
            for r, tag in alerts:
                lines.append(f"{TIER_EMO[r['tier']]} <b>{r['ticker']}</b> {tag}→{r['tier']} (R{int(r['rating'])} {r['route'][:4]}) "
                             f"| PB {r['PB']:.2f} z{r['pb_z']:+.1f} | sụt {r['drop_pct']:+.0f}% | ổn định {r['stab']:.2f} | TK {r['liq_bn']:.0f}tỷ")
        sg = df[df["trank"] >= TIER_RANK["STRONG"]]
        if not sg.empty:
            lines.append("\n<b>📋 Đang trong vùng GOLDEN/STRONG:</b>")
            for _, r in sg.iterrows():
                lines.append(f"{TIER_EMO[r['tier']]} {r['ticker']} R{int(r['rating'])} — PB {r['PB']:.2f} z{r['pb_z']:+.1f} sụt {r['drop_pct']:+.0f}% TK {r['liq_bn']:.0f}tỷ")
        elif not alerts:
            lines.append("\nKhông có mã rating-1/2 nào ở vùng dislocated hôm nay.")
        lines.append("\n<i>🏆R1+rẻ · 🔥R2+rẻ · 💧R3+rẻ · book-guard loại capital-destroyer (bẫy PB_z)</i>")
        try:
            from telegram_recommend import send_telegram_text, load_config
            cfg = load_config()
            print("telegram:", send_telegram_text(cfg["bot_token"], cfg["chat_id"], "\n".join(lines)).get("ok"))
        except Exception as e:
            print("telegram skipped:", e)
    elif not alerts:
        print(f"{today}: no new GOLDEN/STRONG entries (use --always to push standing).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--always", action="store_true")
    ap.add_argument("--no-telegram", action="store_true")
    ap.add_argument("--min-liq", type=float, default=3.0)
    a = ap.parse_args()
    main(a.always, not a.no_telegram, a.min_liq)
