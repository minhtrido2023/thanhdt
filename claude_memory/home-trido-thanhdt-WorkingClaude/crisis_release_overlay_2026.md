---
name: crisis-release-overlay-2026
description: "Unconfirmed-CRISIS holds too long (2024 78d@0%); price-confirm release helps DT engines only at margin≥3%, naive release HURTS"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5a0359eb-dca9-4de4-acce-841f1aeedd6f
---

User concern ([REDACTED]02): DT5G held CRISIS 14/05→30/08/2024 (78 sessions @ 0% equity) with no macro confirm (easing_conf=0), driver=DT4-regime, exited HIGHER (+3.3%). Asked: are we too lax marking CRISIS?

**Diagnosis CONFIRMED — recurrent false-positive pattern.** CRISIS entered by internal r_score (`DT4-regime`, not MACRO-cap/easing), held long in flat markets:
- 2016-08-30→2017-01-04 (90d, +0.3%, max intra-DD −3.2%)
- 2023-10-23→2023-11-30 (28d, +0.1%, −6.0%)
- 2024-05-14→2024-08-30 (78d, +3.3%, −4.4%)
vs REAL crises (deep DD): 2018 −19.6%, COVID −11.9%, 2022 −21.3%. Clean separation: false-pos <6.5% DD, real >11%. NOT a DT smoothing artifact — ALL 4 family variants (canonical TinhTe, DT_10_25_25, v3.4b, DT5G state_raw) agree CRISIS the whole 2024 window. Root cause = r_score momentum-heavy/lagging (P3M 30%): a sharp-brief dip (Apr-2024) tanks rank <0.10 and min_stay locks it for months while price recovers. BULL→CRISIS skip (4 levels in 1 session) is itself a red flag.

**FIX built + backtested** (`crisis_release.py` + `test_crisis_release_nav.py`, pure state→VNINDEX-alloc NAV, canonical mechanics T+1/ramp3/TC0.1%/dep6%/bor10%/TARGET_W{1:0,2:.2,3:.7,4:1,5:1.3}). Rule: inside raw-CRISIS, downgrade→NEUTRAL when (d≥K sessions) AND (Close≥entry_px·(1+margin) held `hold` sessions) AND no macro. Daily-symmetric: if price falls back, CRISIS resumes.

**KEY SURPRISE — naive version HURTS:**
- **margin=0% (release when price reclaims entry): −0.6 to −2.7pp CAGR ALL variants.** Mechanism: re-enters 70% right into the volatility CRISIS was dodging (2024 released Jun→ate Aug-5 yen-carry −8.6% crash). The "false positives" provided REAL DD protection — not purely false.
- **margin=3-5% (require +3% CONFIRMED recovery above de-risk level): WINS but ONLY on smoothed DT engines.** Best = NEUTRAL, K=15, margin=3%: DT_10_25_25 / DT5G 2014+ **+0.47pp CAGR (15.03→15.50%), DD flat −18.38%, Sharpe +0.03**; 2020+ **+1.08pp**. Plateau across margin 3-5% (not knife-edge → not overfit-point). Adaptive: 2024 releases Jun-6 @+3.2% but RE-PROTECTS during Aug-5 (price fell below +3% thr), releases again after → captures recovery yet dodges crash. Real crises preserved (2008/2018 CRISIS days unchanged, DD flat).
- **HURTS twitchy variants (canonical TinhTe −1.1pp, v3.4b −1.3pp 2014+)** — they already churn (250-270 transitions); overlay adds whipsaw.

**RECOMMENDATION: apply to DT5G/DT4 ONLY, NOT whole family** (contradicts user's "cả họ Ngũ Hành" ask — canonical/v3.4b get worse). Config NEUTRAL/K=15/margin=3%/hold=3. Files: crisis_release.py, test_crisis_release_nav.py. Related: [[dt5g_walkforward_event_audit]] (de-risk = crisis insurance, keep as gate not alpha).

**PROD-SPEC V4/V5 CONFIRMED ([REDACTED]02, run_5systems_prodspec STATE_CSV_OVERRIDE env hook, init 50B 2014→2026-05). E1VFVN30 briefly vanished from ticker table mid-run (dev RESTORED it same day: 2595 rows 2016-01-07→[REDACTED]01); re-ran DT5G base+overlay with REAL ETF → BYTE-IDENTICAL to proxy run (V5 24.82/24.32, V4 22.74/22.71) because KELLY parking leg is tiny here (book near-fully-invested) → proxy-vs-real moot for these systems, delta fully robust:**
- **v3.4b book (harness default): overlay HURTS** — V4 22.83→20.89% (−1.94pp, DD −21.2→−24.9%), V5 23.72→22.02% (−1.70pp, DD −18.9→−29.5% blows out). Confirms twitchy-engine churn.
- **DT5G book (production regime): overlay HELPS modestly, concentrated in KELLY** — V4 22.71→22.74% (+0.03pp, flat — BASE book absorbs it), **V5 24.32→24.82% (+0.50pp CAGR, DD −24.97→−24.40% better, Sharpe 1.46→1.48, Calmar 0.97→1.02)**. Matches: KELLY most state-sensitive arm.
- Magnitude small (+0.50pp V5). User's CRISIS-too-lax intuition validated → real but minor refinement; naive version would've backfired. Harness edits kept: STATE_CSV_OVERRIDE hook (inert default) + ETF try/except (necessary — E1VFVN30 briefly gone, dev restored same day).

**FINAL DECISION ([REDACTED]02): DO NOT DEPLOY overlay — keep DT5G live AS-IS.** After building the 2000→now transitions HTML (sim_dt5g_crel_html.py → dt5g_cr_transitions.html / dt5g_cr_system.html / data/dt5g_cr_daily.csv; full DT5G pipeline pure-NAV), overlay = −0.47pp 2014+ (DD −18.7→−20.7%) on pure-VNINDEX-allocation — only +0.50pp on V5/KELLY book (ETF-parking mechanics). User concluded (correct): overlay adds complexity + a tuned param (margin3%, overfit risk) + toggling/TC (2024: 1 CRISIS block → 7 on/off), for a benefit that FLIPS SIGN by book. **Core insight: the thing it "fixes" doesn't leak money — the long flat-CRISIS holds were doing REAL DD protection (dodged Aug-5-2024 −8.6%); the 3.5-month hold was a COSMETIC concern, not a perf leak.** Keep de-risk as insurance, don't mechanize overriding it. CRISIS-too-lax remains a thing to MONITOR, not auto-correct. crisis_release.py / test_crisis_release_nav.py / sim_dt5g_crel_html.py retained for reference only.
