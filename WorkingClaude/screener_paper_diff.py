#!/usr/bin/env python3
"""screener_paper_diff.py — daily side-by-side OLD vs NEW 8L screener (paper-trade before go-live).

Run AFTER rating_8l.py each day (the live pipeline produces data/rating_8l.csv + rating_8l_screener.csv).
  OLD zone = pre-2026-06-16 logic: pb_z-only val_state + ROE_Min5Y<0 trap (reconstructed from rating_8l.csv).
  NEW zone = current composite (relative pb_z + absolute 1/PE + CFO-3Y confirm + track-bonus + ROE_Min3Y
             trap, PERCENTILE zones) — read straight from rating_8l_screener.csv.
Logs the daily diff to data/screener_paper_diff_log.csv (one row/date) + a dated detail block to
data/screener_paper_diff.md, and prints SANITY FLAGS that would block go-live if they fire.

Go-live gate (user 2026-06-16): run daily to 2026-06-30; if NO sanity flag fires across the window, the
NEW composite screener goes live. Usage: python screener_paper_diff.py
"""
import os, sys, datetime
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WD = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
LIQ_MIN = 3.0
RATING_CSV = os.path.join(WD, "data", "rating_8l.csv")
SCREEN_CSV = os.path.join(WD, "data", "rating_8l_screener.csv")
LOG_CSV = os.path.join(WD, "data", "screener_paper_diff_log.csv")
LOG_MD  = os.path.join(WD, "data", "screener_paper_diff.md")

def old_zone(r):
    """pre-session pb_z-only logic on the investable (rating<=3 & liquid) universe."""
    z, roe5 = r["pb_z"], r.get("ROE_Min5Y", np.nan)
    if pd.isna(z): return "n/a"
    if z <= -0.3 and pd.notna(roe5) and roe5 < 0: return "4_TRAP"
    if z <= -0.3: return "1_BUY-NOW"        # dislocated / below-avg vs own history
    if z <=  0.6: return "2_ACCUMULATE"
    return "3_WATCH-RICH"

def main():
    today = str(datetime.date.today())
    for p in (RATING_CSV, SCREEN_CSV):
        if not os.path.exists(p):
            print(f"ERROR: {p} not found — run `python rating_8l.py` first."); sys.exit(1)
    R = pd.read_csv(RATING_CSV)
    S = pd.read_csv(SCREEN_CSV)   # already the rating<=3 & liquid universe, with NEW `zone`
    # OLD zones on the SAME universe (rating<=3 & liq>=LIQ_MIN)
    inv = R[(R["rating"] <= 3) & (R["liq_bn"] >= LIQ_MIN)].copy()
    inv["zone_old"] = inv.apply(old_zone, axis=1)
    m = inv[["ticker", "zone_old", "pb_z", "ROE_Min3Y", "ROE_Min5Y", "rating"]].merge(
        S[["ticker", "zone", "value_score", "value_pct", "value_yield_pct", "cfo_confirm"]],
        on="ticker", how="outer", indicator=True)
    m = m.rename(columns={"zone": "zone_new"})

    ZB = "1_BUY-NOW"
    old_buy = set(m.loc[m.zone_old == ZB, "ticker"])
    new_buy = set(m.loc[m.zone_new == ZB, "ticker"])
    entered = sorted(new_buy - old_buy)     # NEW surfaces, OLD missed
    left    = sorted(old_buy - new_buy)     # OLD had, NEW dropped
    old_trap = set(m.loc[m.zone_old == "4_TRAP", "ticker"])
    new_trap = set(m.loc[m.zone_new == "4_TRAP", "ticker"])
    # GENUINE recovered scars only: old-trapped (ROE_Min5Y<0) but NOW ROE_Min3Y>=0 (no recent-3Y loss).
    # (A still-chronic destroyer that merely became 'expensive' -> WATCH is NOT a recovery; exclude it.)
    untrapped = sorted(t for t in (old_trap - new_trap)
                       if (m.loc[m.ticker == t, "ROE_Min3Y"].iloc[0] >= 0))

    # ---- SANITY FLAGS (any firing = investigate before go-live) ----
    flags = []
    bad_buy = m[(m.zone_new == ZB) & (m.ROE_Min3Y < 0)]            # BUY with chronic destroyer = guard leak
    if len(bad_buy): flags.append(f"CRIT: {len(bad_buy)} NEW-BUY with ROE_Min3Y<0 ({list(bad_buy.ticker)})")
    leak = m[(m.zone_new == ZB) & (m.rating > 3)]                  # universe leak
    if len(leak): flags.append(f"CRIT: {len(leak)} NEW-BUY with rating>3 ({list(leak.ticker)})")
    nb = len(new_buy)
    if nb == 0: flags.append("WARN: NEW BUY-NOW is EMPTY (screener produced nothing)")
    if nb > 0.55 * len(S): flags.append(f"WARN: NEW BUY-NOW = {nb} (> 55% of {len(S)} universe — too loose)")
    only_new = m[m._merge == "right_only"]; only_old = m[m._merge == "left_only"]
    if len(only_new) or len(only_old):
        flags.append(f"INFO: universe mismatch (screener-only {len(only_new)}, rating-only {len(only_old)})")

    # ---- append daily summary row ----
    dist = lambda col: {z: int((m[col] == z).sum()) for z in [ZB, "2_ACCUMULATE", "3_WATCH-RICH", "4_TRAP"]}
    row = {"date": today, "n_univ": len(S),
           "buy_old": len(old_buy), "buy_new": len(new_buy),
           "entered_buy": len(entered), "left_buy": len(left), "untrapped": len(untrapped),
           "flags": " | ".join(flags) if flags else "OK"}
    log = pd.read_csv(LOG_CSV) if os.path.exists(LOG_CSV) else pd.DataFrame()
    log = log[log["date"] != today] if len(log) else log              # idempotent per date
    log = pd.concat([log, pd.DataFrame([row])], ignore_index=True)
    log.to_csv(LOG_CSV, index=False)

    # ---- dated detail block ----
    det = [f"\n## {today}  (univ={len(S)}, BUY old={len(old_buy)} new={len(new_buy)})",
           f"- **SANITY:** {'🟢 OK' if not flags else '🔴 ' + ' ; '.join(flags)}",
           f"- **Entered BUY (new, old missed)** [{len(entered)}]: " +
           ", ".join(f"{t}(vpct{m.loc[m.ticker==t,'value_pct'].iloc[0]:.2f},ROE3 {m.loc[m.ticker==t,'ROE_Min3Y'].iloc[0]:+.0%})" for t in entered),
           f"- **Left BUY (old had, new dropped)** [{len(left)}]: " +
           ", ".join(f"{t}(pb_z{m.loc[m.ticker==t,'pb_z'].iloc[0]:+.2f},ey%{m.loc[m.ticker==t,'value_yield_pct'].iloc[0]:.2f})" for t in left),
           f"- **Un-trapped (recovered scars NEW spares)** [{len(untrapped)}]: " + ", ".join(untrapped)]
    with open(LOG_MD, "a", encoding="utf-8") as f: f.write("\n".join(det) + "\n")

    # ---- console ----
    print(f"=== 8L screener paper-diff {today} | universe {len(S)} ===")
    print(f"  BUY-NOW: old {len(old_buy)} -> new {len(new_buy)}  (entered {len(entered)}, left {len(left)})")
    print(f"  ENTERED BUY (new surfaces, old missed): {', '.join(entered) if entered else '-'}")
    print(f"  LEFT BUY (new drops): {', '.join(left) if left else '-'}")
    print(f"  UN-TRAPPED (recovered scars spared): {', '.join(untrapped) if untrapped else '-'}")
    print(f"  SANITY: {'🟢 OK — no blocker' if not flags else chr(10) + chr(10).join('   🔴 '+x for x in flags)}")
    print(f"  -> logged to {os.path.basename(LOG_CSV)} + {os.path.basename(LOG_MD)} "
          f"({len(log)} days; go-live gate = all-OK through 2026-06-30)")

if __name__ == "__main__":
    main()
