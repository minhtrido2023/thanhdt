# -*- coding: utf-8 -*-
"""Regression self-check for lag_live_schedule.live_lag_candidates() — the point-in-time
LAG/PEAD candidate source for the LIVE money-path (golive_recommend_v23.py), added
2026-07-12 to fix audit gap R1 (Taylor_20260712_121642): the old source
`earnings_events_classified.csv` only surfaces an event after release+30 sessions (needs
the full price window), i.e. ~25 sessions AFTER the T+5 entry — every new release was
silently missed during an earnings season.

Checks:
  A. PARITY on real data — for every event the old CSV-only path could see, the new module
     returns the IDENTICAL candidate decision and identical prior_n_good / pa_HL3 /
     surprise_B_MA / tier (old walk replicated verbatim below as the reference).
  B. MBS 2026Q2 (released 2026-07-08, the real event that exposed the gap) — visible
     same-day in the new source with correctly SCORED gates (NP_R≈+36 ✓, prior_n_good=23 ✓,
     pa_HL3≈4.06 < 5 ✗ → qualify=False), and invisible to the old path.
  C. Synthetic event released TODAY (would-be qualifier) — appears immediately with
     qualify=True and schedules as "T+5 phiên tới" via the golive branch; the old CSV path
     cannot see it. Negative control: same event with only 3 priors does NOT qualify.
  D. Wiring guard — golive_recommend_v23.py imports live_lag_candidates and no longer
     builds candidates from the classified CSV.

Run: python lag_live_schedule_selfcheck.py   (exit 0 = all pass)
"""
import os, sys, pickle, tempfile
from datetime import datetime
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
from lag_live_schedule import live_lag_candidates  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def old_walk(csv_path, pkl_path):
    """Verbatim replica of the OLD golive_recommend_v23.py LAG block (pre-2026-07-12) —
    the reference implementation for the parity check. Returns the full ev table with
    prior_n_good / pa_HL3 / surprise_B_MA and a qualify column."""
    ev = pd.read_csv(csv_path, parse_dates=["Release_Date"])
    with open(pkl_path, "rb") as f:
        fin = pickle.load(f)
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
    fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
    fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
    ev = ev.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"]],
                  on=["ticker", "quarter", "Release_Date"], how="left")
    ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    LN2 = np.log(2); HL = 3.0; ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
    for tk, g in ev.groupby("ticker"):
        hist = []
        for ri in g.index.tolist():
            row = ev.loc[ri]; cd = row["Release_Date"]; ev.at[ri, "prior_n_good"] = len(hist)
            if hist:
                da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
                w = np.exp(-LN2 * ((cd - da).days.values / 365.25) / HL)
                ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]): hist.append((cd, row["post_ret"]))
    ev["qualify"] = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
    ev["tier"] = np.where(ev["surprise_B_MA"] > 0.5, "LAG_HI", "LAG_LO")
    return ev


CSV = os.path.join(WORKDIR, "data", "earnings_events_classified.csv")
PKL = os.path.join(WORKDIR, "data", "earnings_surprise_data.pkl")

# ── A. parity old-vs-new on the full real history ───────────────────────────
print("[A] parity vs verbatim old logic on real data (full history — takes ~1-2 min)...")
old = old_walk(CSV, PKL)
new = live_lag_candidates()   # no start filter: full parity surface
key = ["ticker", "quarter", "Release_Date"]
mrg = old.merge(new, on=key, how="left", suffixes=("_old", "_new"))
check("A1 every old event found in new source", int(mrg["qualify_new"].isna().sum()) == 0,
      f"{int(mrg['qualify_new'].isna().sum())} missing of {len(old):,}")
mrg = mrg[mrg["qualify_new"].notna()]
# same-day siblings (one ticker, two quarters released the same date): the old walk counted
# the sibling as "prior" using its post_ret — a release+30 look-ahead, CSV-row-order-dependent,
# and uncomputable on the release date for a fresh event. The new module uses strictly-earlier
# priors only, so prior_n_good/pa_HL3 may differ ON EXACTLY THOSE ROWS (2 in the full history:
# BOT 2026-01-28, CT6 2026-02-02) — qualify must still be identical (A6).
tie = mrg.duplicated(["ticker", "Release_Date"], keep=False)
same_prior = (mrg["prior_n_good_old"].astype(int) == mrg["prior_n_good_new"].astype(int))
check("A2 prior_n_good identical outside same-day-sibling ties", bool((same_prior | tie).all()),
      f"{int((~same_prior).sum())} mismatches, {int((~same_prior & ~tie).sum())} outside ties")
pa_ok = (mrg["pa_HL3_old"].isna() & mrg["pa_HL3_new"].isna()) | \
        np.isclose(mrg["pa_HL3_old"].fillna(-1e18), mrg["pa_HL3_new"].fillna(-1e18), rtol=0, atol=1e-9)
check("A3 pa_HL3 identical outside same-day-sibling ties (atol 1e-9)", bool((pa_ok | tie).all()),
      f"{int((~pa_ok).sum())} mismatches, {int((~pa_ok & ~tie).sum())} outside ties")
sur_ok = np.isclose(mrg["surprise_B_MA_old"], mrg["surprise_B_MA_new"], rtol=0, atol=1e-12)
check("A4 surprise_B_MA identical", bool(sur_ok.all()), f"{int((~sur_ok).sum())} mismatches")
check("A5 tier identical", bool((mrg["tier_old"] == mrg["tier_new"]).all()))
q_ok = (mrg["qualify_old"].astype(bool) == mrg["qualify_new"].astype(bool))
check("A6 qualify decision identical on all shared events", bool(q_ok.all()),
      f"{int((~q_ok).sum())} mismatches / old qualifiers={int(old['qualify'].sum()):,}")
csv_max = old["Release_Date"].max()
fresh = new[new["Release_Date"] > csv_max]
check("A7 new source additionally sees post-CSV releases", len(fresh) > 0,
      f"{len(fresh)} events after CSV max {csv_max.date()}")

# ── B. MBS 2026Q2 — the real event that exposed the gap ─────────────────────
print("[B] MBS 2026Q2 (released 2026-07-08) scored same-day...")
mbs = new[(new["ticker"] == "MBS") & (new["Release_Date"] == pd.Timestamp("2026-07-08"))]
check("B1 MBS 2026-07-08 present in new source", len(mbs) == 1)
if len(mbs):
    r = mbs.iloc[0]
    check("B2 NP_R scored in % (≈ +36)", abs(r["NP_R"] - 36.0) < 1.0, f"NP_R={r['NP_R']:.1f}")
    check("B3 prior_n_good = 23 (full history counted)", int(r["prior_n_good"]) == 23,
          f"prior_n_good={int(r['prior_n_good'])}")
    check("B4 pa_HL3 ≈ 4.06 (< 5 gate)", 3.9 < r["pa_HL3"] < 4.2, f"pa_HL3={r['pa_HL3']:.2f}")
    check("B5 qualify=False (pa_HL3 gate) — scored, not skipped", not bool(r["qualify"]))
mbs_old = old[(old["ticker"] == "MBS") & (old["Release_Date"] == pd.Timestamp("2026-07-08"))]
check("B6 old CSV path blind to MBS (the R1 gap)", len(mbs_old) == 0)

# ── C. synthetic event released TODAY qualifies + schedules immediately ─────
print("[C] synthetic new event released today...")
TODAY = pd.Timestamp(datetime.now().date())
prior_dates = pd.to_datetime(["2024-01-15", "2024-07-15", "2025-01-15", "2025-07-15", "2026-01-15"])
with tempfile.TemporaryDirectory() as td:
    # classified CSV: 5 mature good priors (NP_R=50%, post_ret=+10 → pa_HL3=10 ≥ 5)
    pd.DataFrame({
        "ticker": "TST", "quarter": [f"P{i}" for i in range(5)], "Release_Date": prior_dates,
        "NP_R": 50.0, "Rev_YoY": 10.0, "pre_ret": 0.0, "rel_ret": 0.0, "post_ret": 10.0,
        "pattern": "LAGGED_POS"}).to_csv(os.path.join(td, "ev.csv"), index=False)
    # surprise pkl: the 5 priors + a NEW event released TODAY (NP_R=40%, surprise > 0.5)
    base = {"NP_P1": 1.0e11, "NP_P2": 1.0e11, "NP_P3": 1.0e11, "NP_P4": 1.0e11}
    rows = [{"ticker": "TST", "quarter": f"P{i}", "Release_Date": d, "NP_P0": 1.0e11,
             "NP_R": 0.50, **base} for i, d in enumerate(prior_dates)]
    rows.append({"ticker": "TST", "quarter": "NEWQ", "Release_Date": TODAY, "NP_P0": 2.0e11,
                 "NP_R": 0.40, **base})   # surprise = (2e11-1e11)/1e11 = 1.0 > 0.5 → LAG_HI
    with open(os.path.join(td, "fin.pkl"), "wb") as f:
        pickle.dump(pd.DataFrame(rows), f)
    got = live_lag_candidates(pkl_path=os.path.join(td, "fin.pkl"), csv_path=os.path.join(td, "ev.csv"))
    ne = got[got["quarter"] == "NEWQ"]
    check("C1 event released today visible immediately", len(ne) == 1)
    if len(ne):
        r = ne.iloc[0]
        check("C2 qualifies (NP_R=40≥15, priors=5≥4, pa_HL3=10≥5)", bool(r["qualify"]),
              f"npr={r['NP_R']:.0f} prior={int(r['prior_n_good'])} pa={r['pa_HL3']}")
        check("C3 tier LAG_HI (surprise=1.0>0.5)", r["tier"] == "LAG_HI")
        # golive scheduling branch (same logic as golive_recommend_v23.td_offset + loop):
        trade_dates = pd.bdate_range(end=TODAY, periods=300)   # latest session = today
        pos = int(np.searchsorted(np.array(trade_dates, dtype="datetime64[ns]"),
                                  np.datetime64(r["Release_Date"]), side="right")) - 1
        tgt = pos + 5
        ahead = None if tgt < len(trade_dates) else tgt - (len(trade_dates) - 1)
        check("C4 schedules as UPCOMING T+5 (not entered, not stale)", ahead == 5,
              f"ahead={ahead}")
    # old path on the same fixtures: CSV has no NEWQ row → blind
    got_old = old_walk(os.path.join(td, "ev.csv"), os.path.join(td, "fin.pkl"))
    check("C5 old CSV path cannot see the new event", (got_old["quarter"] == "NEWQ").sum() == 0)
    # negative control: only 3 priors → prior_n_good gate must reject
    pd.DataFrame({
        "ticker": "TST", "quarter": [f"P{i}" for i in range(3)], "Release_Date": prior_dates[:3],
        "NP_R": 50.0, "Rev_YoY": 10.0, "pre_ret": 0.0, "rel_ret": 0.0, "post_ret": 10.0,
        "pattern": "LAGGED_POS"}).to_csv(os.path.join(td, "ev3.csv"), index=False)
    got3 = live_lag_candidates(pkl_path=os.path.join(td, "fin.pkl"), csv_path=os.path.join(td, "ev3.csv"))
    r3 = got3[got3["quarter"] == "NEWQ"].iloc[0]
    check("C6 negative control: 3 priors → qualify=False", not bool(r3["qualify"]),
          f"prior_n_good={int(r3['prior_n_good'])}")

# ── D. wiring guard on golive_recommend_v23.py ──────────────────────────────
print("[D] wiring guard...")
src = open(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"), encoding="utf-8").read()
check("D1 golive imports live_lag_candidates", "live_lag_candidates" in src)
check("D2 golive no longer READS the classified CSV (name may remain in comments)",
      'read_csv(os.path.join(WORKDIR, "data/earnings_events_classified.csv"' not in src
      and "earnings_events_classified.csv\", parse_dates" not in src)

print()
if fails:
    print(f"❌ {len(fails)} FAIL(s): {fails}")
    sys.exit(1)
print("✅ all lag_live_schedule checks passed")
sys.exit(0)
