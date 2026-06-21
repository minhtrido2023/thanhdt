# Paper-trade 5 systems — Apr 1 → Aug 31 2026

**Started**: 2026-04-01 | **Decision target**: Sept 2026 | **Refresh**: daily 15:30 via Windows scheduled task
**Schedule task**: `PaperTrade3Sys` running `papertrade_daily.bat` (now 6 steps with V5 added)
**Compare script**: `papertrade_compare.py` → outputs `data/papertrade_compare5.{md,csv}`

Each system starts fresh at 50B VND on Apr 1. All use Tam Quan v3.4b state classifier unless noted otherwise.

---

## V1 — V11 + TQ34b (control / baseline architecture)

**Codename**: Song Sinh (Twin)
**Script**: `pt_v11_tq34b.py`
**Output prefix**: `data/pt_v11_tq34b_*`

**Architecture**:
- 25B BAL leg: BA v11 stack (SV_TIGHT + P3 overheat guard + RE_BACKLOG_BUY + V6 ETF parking)
- 25B VN30 leg: BA v11 on top-30 universe (by Volume_3M_P50 × Close)
- Each leg parks idle cash in E1VFVN30 ETF (state 3 NEUTRAL: 70%)

**Config**:
- State source: TQ v3.4b (`tav2_bq.vnindex_5state_tam_quan_v34b_clean`)
- ETF schedule: `cash_etf_states={3: 0.7}` (only NEUTRAL has ETF parking)
- Tier weights: flat 10% × max_positions=10 (default equal-weight)
- LAGGED leg: NONE
- Cost: deposit=0%, borrow=10%, TC=0.1%/side, ETF friction=0.15%/side

**12y backtest baseline** (from `test_rolling_m3_v121_ensemble.py` yesterday):
- FULL CAGR: **+21.14%** / Sharpe 1.45 / MaxDD -17.82% / Wealth 10.71×
- OOS 2024-26 CAGR: **+28.88%** / Sharpe 1.57 / MaxDD -16.91% / Calmar 1.71

**Purpose**: Pure V11 reference. Tests "Does BA v11 + VN30 dual-book + ETF parking still work in 2026 market?"

---

## V2 — V12 + TQ34b (LAGGED earnings-drift architecture)

**Codename**: Âm Dương (Yin Yang)
**Script**: `pt_v12_tq34b.py`
**Output prefix**: `data/pt_v12_tq34b_*`

**Architecture**:
- 25B BAL leg: same as V1
- 25B LAGGED HL_3y leg: V12 (fixed 8% per-position sizing, half-life 3y prior-good filter)
- BAL parks ETF; LAGGED no ETF (state-independent earnings drift play)

**Config**:
- State source: TQ v3.4b
- ETF schedule: `cash_etf_states={3: 0.7}`
- LAGGED: buy T+5 after NP_R≥15 if prior_n_good≥4 AND pa_HL3≥5 ; hold 25 trading days
- LAGGED sizing: **fixed 8% NAV per position** (no S2 modulation)
- Max 12 positions LAGGED, liquidity floor 2B VND ADV
- Cost: same as V1

**12y backtest baseline** (rebuilt today):
- FULL CAGR: **+21.96%** / Sharpe 1.65 / MaxDD -14.39% / Wealth 11.65×
- OOS 2024-26 CAGR: **+23.22%** / Sharpe 1.60 / MaxDD -9.64% / Calmar 2.41

**Purpose**: Tests LAGGED HL_3y earnings-drift edge with V11 BAL leg pairing. Hypothesis: LAGGED's uncorrelated alpha (Y2022 +7.77% defensive) improves risk-adjusted return.

---

## V3 — V12 + LIVE Ngũ Hành (state-machine alt)

**Codename**: Âm Dương + Tinh Tế Live
**Script**: `pt_v12_live.py`
**Output prefix**: `data/pt_v12_live_*`

**Architecture**: identical to V2 (BAL + LAGGED V12 fixed 8%)

**Config difference vs V2**:
- State source: **LIVE Ngũ Hành "Tinh Tế / Sâu Sắc"** (production 5-state, not TQ v3.4b)
- Everything else identical to V2

**Purpose**: Tests whether the LIVE production 5-state classifier (with current parameters) generates better signals than TQ v3.4b static state. Direct comparison V2 vs V3 isolates state-classifier impact.

**Note**: This is a state-machine swap experiment. If V3 ≈ V2 → both classifiers equivalent. If V3 > V2 → LIVE classifier deserves to be production state source.

---

## V4 — V121_ENS = V12.1 + Ensemble (CURRENT PRODUCTION CANDIDATE)

**Codename**: V121 Ensemble Âm Dương Tinh Tế + AND-HOLD
**Script**: `pt_v121_ensemble.py`
**Output prefix**: `data/pt_v121_ens_*`

**Architecture**:
- 25B BAL leg: BA v11 (same as V1/V2/V3)
- 25B SWITCHED leg: routes between two systems by ensemble signal
  - When `ens_signal=1` (V11 mode): VN30 active (BA v11 on top-30 + ETF parking)
  - When `ens_signal=0` (V12 mode): LAGGED V12.1 active (with S2 sizing)
- Switch cost: 0.5% round-trip per flip

**Ensemble signal (M1+M3r AND-HOLD)**:
- M1 = VNINDEX 6m return − Equal-Weight 6m return (high → concentrated → favor V11/VN30)
- M3r = Top10 (rolling 1Y ADV) − all-prune 6m return (no-lookahead version)
- Binary: each metric > its expanding-median (252d warmup) ⇒ 1 else 0
- AND-HOLD: both agree ⇒ adopt; disagree ⇒ keep current state

**LAGGED V12.1 sizing** (S2 modulation): pos_pct = **10% if surprise_B_MA > 0.5 else 8%**
- Surprise = (NP_P0 − mean(NP_P1..P4)) / max(|mean|, 1B VND)

**Config**:
- State source: TQ v3.4b
- ETF schedule: `cash_etf_states={3: 0.7}` (NEUTRAL only, 70%)
- Everything else identical to V2

**12y backtest baseline** (yesterday's winner):
- FULL CAGR: **+24.70%** / Sharpe 1.76 / MaxDD -15.43% / Wealth **15.32×** 🥇
- OOS 2024-26 CAGR: **+31.92%** / Sharpe 1.81 / MaxDD -10.89% / Calmar 2.93

**Purpose**: V4 is the leading deployment candidate. Tests "Does M1+M3r ensemble signal correctly route between V11 (concentrated TOP30) and V12.1 (LAGGED earnings drift) based on market regime?"

**Current paper trade** (Apr 1 → May 19, 7 weeks): NAV 51.56B (+3.13%, CAGR +26.40%, DD -2.41%). Ensemble in V11-mode 32/32 days (no flips yet). 19 open positions.

---

## V5 — V121_ENS + Q2_ONLY (NEW: Kelly NEUTRAL boost overlay)

**Codename**: V121 Ensemble Âm Dương + Kelly Q2 NEUTRAL
**Script**: `pt_v121_ens_q2.py` (created 2026-05-23, copy of pt_v121_ensemble.py)
**Output prefix**: `data/pt_v121_ens_q2_*`

**Architecture**: **IDENTICAL to V4** (BAL + SWITCHED with M1+M3r AND-HOLD ensemble + S2 sizing on LAGGED V12.1)

**Single change vs V4**: ETF schedule
- V4: `cash_etf_states={3: 0.7}` (NEUTRAL ETF 70%)
- V5: `cash_etf_states={3: 1.0}` (NEUTRAL ETF 100%, Kelly Q2_ONLY overlay)

**Rationale**: Q2 Kelly research found that pushing NEUTRAL ETF deployment from 70% → 100% captures additional alpha during NEUTRAL regime (idle cash gets E1VFVN30 tracking instead of sitting unproductive). Other states (CRISIS/BEAR/BULL/EX-BULL) unchanged.

**ETF logic fix dependency** (2026-05-23): V5 relies on the JIT-sell + cur_nav fix in `simulate_holistic_nav.py`:
- Pre-fill 4c: SELL-only (release ETF on state down-transitions)
- Step 5 JIT sell: BA fills can JIT-sell ETF when cash short (FIFO, 0.15% friction)
- Step 6b post-fill SWEEP: park leftover cash to ETF up to state target
- cur_nav now includes `cash_etf` (was missing → BA target_value collapsed to 0 when ETF held most NAV)

Without these fixes, V5 would silently shut down BA leg (BA can't buy because cash [REDACTED] swept to ETF).

**12y backtest expected** (from `test_ensemble_with_q2_only.py` today):
- FULL CAGR: **+25.71%** / Sharpe 1.70 / MaxDD -16.93% / Wealth **16.93×** (+1.61× vs V4)
- OOS 2024-26 CAGR: **+36.16%** / Sharpe 1.84 / MaxDD -14.94% / Calmar 2.42

**Δ vs V4 baseline**:
- FULL: +1.01pp CAGR, -0.06 Sharpe, -1.50pp MaxDD
- **OOS: +4.24pp CAGR, +0.03 Sharpe, -4.05pp MaxDD** ⚠️

**Trade-off**:
- ✅ Best OOS CAGR among all 5 systems (+36.16%)
- ✅ Sharpe maintained (slight improvement in OOS)
- ✅ Wealth maxes at 16.93× over 12y
- ⚠️ MaxDD widens ~4pp in OOS (from -10.89 → -14.94%)
- ⚠️ DD risk from VN30 mode (when ensemble active in V11): double-ETF leg overlay
- Calmar drops 2.93 → 2.42 (still > 2.0, acceptable)

**Purpose**: V5 stress-tests the Q2_ONLY Kelly overlay on the leading ensemble candidate. Hypothesis: Q2 +4.24pp OOS CAGR is real but DD cost is acceptable trade-off.

**Watch points during paper trade**:
- If MaxDD > -18% in any rolling 60-day window → **alert and review** (DD widening larger than backtest range)
- If V5 underperforms V4 by > 3% over Q3 2026 → revert (Q2 effect failing in live)
- Track ETF transaction count vs V4 (V5 should have HIGHER ETF turnover due to JIT sells)
- Verify BA leg stays active during NEUTRAL state (BAL_stocks > 0 in NEUTRAL days) — this was the pre-fix bug

---

## Comparison matrix (5 systems side-by-side)

| Field | V1 V11 | V2 V12+TQ | V3 V12+LIVE | V4 V121_ENS | **V5 V121_ENS+Q2** |
|---|---|---|---|---|---|
| BAL leg | ✓ BA v11 25B | ✓ same | ✓ same | ✓ same | ✓ same |
| Second leg | VN30 25B | LAGGED V12 25B | LAGGED V12 25B | SWITCHED (VN30⇄LAG_V12.1) | SWITCHED (VN30⇄LAG_V12.1) |
| LAGGED sizing | — | fixed 8% | fixed 8% | S2 (8/10%) | S2 (8/10%) |
| State source | TQ34b | TQ34b | **LIVE** | TQ34b | TQ34b |
| ETF schedule | {3: 0.7} | {3: 0.7} | {3: 0.7} | {3: 0.7} | **{3: 1.0}** |
| Ensemble switch | NO | NO | NO | M1+M3r AND-HOLD | M1+M3r AND-HOLD |
| Backtest 12y CAGR | 21.14% | 21.96% | ~22% (similar) | 24.70% | **25.71%** |
| Backtest OOS CAGR | 28.88% | 23.22% | ~23% | 31.92% | **36.16%** |
| Backtest OOS Sharpe | 1.57 | 1.60 | ~1.60 | 1.81 | **1.84** |
| Backtest OOS MaxDD | -16.91% | -9.64% | ~-10% | -10.89% | -14.94% |
| Backtest 12y Wealth | 10.71× | 11.65× | ~12× | 15.32× | **16.93×** |

## Hypothesis matrix

| Comparison | Tests | Status |
|---|---|---|
| V1 vs V4 | Does ensemble + LAGGED beat dual-VN30? | V4 wins +3.56pp 12y CAGR |
| V2 vs V3 | TQ34b vs LIVE state classifier | TBD — pending paper trade data |
| V2 vs V4 | Fixed-8% LAGGED vs S2-modulated + ensemble switch | V4 wins +2.74pp 12y |
| V4 vs V5 | Kelly Q2 NEUTRAL boost on ensemble | V5 +1.01pp FULL / +4.24pp OOS (CAGR), -4pp DD |
| V1 vs V5 | Plain V11 vs ensemble + Q2 stacked | V5 +4.57pp 12y / +7.28pp OOS |

## Daily refresh task

Windows scheduled task `PaperTrade3Sys` (legacy name, now 5+ systems) runs `papertrade_daily.bat` daily at 15:30. **Add V5 step** by editing the bat to include `python pt_v121_ens_q2.py` after the V4 step. Comparison script `papertrade_compare.py` should be extended to read V5 outputs and produce `data/papertrade_compare5.{md,csv}`.

## Decision flow (Sept 2026)

After 5 months of live paper trade data:

1. Compare realized CAGR / Sharpe / MaxDD across all 5 systems
2. Identify which architecture wins on the user's preferred metric (likely Sharpe or Calmar)
3. Verify Q2_ONLY didn't blow up DD in V5 vs V4 (gate: V5 DD ≤ V4 DD + 4pp tolerance)
4. Verify ensemble flipping frequency matches backtest expectation
5. Pick production system for real-money deployment
6. If V5 wins → may also consider Q3 BOOST overlay later (gated by V5 success)

## Files inventory

- `pt_v11_tq34b.py` → V1
- `pt_v12_tq34b.py` → V2
- `pt_v12_live.py` → V3
- `pt_v121_ensemble.py` → V4
- `pt_v121_ens_q2.py` → **V5** (new, created 2026-05-23)
- `papertrade_compare.py` → comparison script (needs extension for V5)
- `data/pt_v*_logs.csv` / `_transactions.csv` / `_open_positions.csv` / `_report.md` → outputs per system
- `data/papertrade_compare5.{md,csv}` → 5-system comparison (replace compare4.*)

## Memory references

- `papertrade_4sys_2026Q2Q3.md` → original 4-system note (superseded by this)
- `tam_quan_v3_4b_dinh_tam.md` → TQ v3.4b state classifier spec
- `ba_v12_1_am_duong_tinh_te.md` → V12.1 S2 sizing spec
- `lagged_pos_hl3y_spec.md` → LAGGED HL_3y strategy spec
- `ngu_hanh_tinh_te.md` → LIVE 5-state classifier (used by V3)
- `v11_transparent_sim_bugs_fixed.md` → transparent sim infrastructure
- ETF fix log → `simulate_holistic_nav.py` 2026-05-23 changes: ETF SELL-only prefill + JIT sell + POST_FILL_SWEEP + cur_nav include cash_etf
