# Kickoff — BAL & LAG Stock-Selection Deep-Dive
**Created 2026-06-12 for a fresh session. Goal: improve the SELECTION criteria of V2.3's two books (BAL momentum, LAG PEAD) to reduce style-drag — work inside the SIGNAL, not via defensive overlays.**

## Why this session exists
V2.3 = V2.2 (BAL|LAG static + ETF parking) + capit sleeve = production champion (26.2%/Sh1.66/DD−20.1/Cal1.31, 2014→2026-05). Its only real weakness is the **2025-08→ style-divergence grind** (−11.8% / 294d underwater while VNINDEX +8.4%; breadth was 0.55 = NOT narrow — so the lag is from STOCK SELECTION / style rotation, not megacap-avoidance).

**Already ruled OUT this session (do NOT re-try):**
- Book C (value 3rd book) — dropped; value+momentum co-fell in 2025-26, only a Sharpe (not grind/tail) gain.
- Narrow-bull index participation overlay — no-op + premise wrong (breadth wasn't narrow).
- Book-level grind stops (DD-stop / NAV<MA / mom<0) — with real TC all cost 4-7pp CAGR, whipsaw, cut at bottoms.
- Conclusion that pointed here: the only lever left is **the selection logic itself**.

## CURRENT SELECTION — BAL (Book A), file `signal_v11_sql.py` (SIGNAL_V11)
A 100-pt composite TA score `ta` (~22 weighted CASE WHEN terms), then `play_type` by `ta` threshold × DT5G state × `fa_tier`.
- **`ta` components** (momentum-heavy): RSI level (>0.50 +25, >0.75 +5, <0.30 −10) · MA-stack (Close>MA50>MA200 +25, Close>MA20 +15) · volume surge (Vol≥1.3×Vol_3M_P50 & up +20) · MACDdiff>0 +15 · PE-vs-5Y (cheap +15 / rich −15) · VNINDEX rsi_max3m>0.65 +10 · near-3Y-high ID_HI_3Y≤5 +8 · D_RSI_Max1W>0.65 +5 · FSCORE≥8 +10 · NP YoY (+8/−8) · NP QoQ +8 · sector (banks/8,9 +5; 4,7 −5) · MA50 slope (+5/+5/−5) · drawdown-from-3M-high (Close/HI_3M<0.85 −10) · bank fa_tier (D +10 / A −10).
- **play_type tiers** (buys ONLY in state 3/4/5 — never CRISIS/BEAR): MEGA (ta≥170 bull C/D) · S_PRO (ta≥170) · MOMENTUM (ta≥155 bull C/D) · MOMENTUM_QUALITY (ta≥155 A/B) · MOMENTUM_N (ta≥155 NEUTRAL C/D, fresh-Q≤60d) · COMPOUNDER_BUY (A/B, pe_z<−0.5, ta≥95) · DEEP_VALUE_RECOVERY (C, ta≥100, bull, NP|Rev YoY>20%) · MOMENTUM_S (ta≥140) · MOMENTUM_A (ta≥125) · MOMENTUM_S_N (NEUTRAL ta≥140) · COMPOUNDER_HOLD/WAIT/PASS.
- **Book trades tiers (TIER_BAL)**: MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY. tier 10%/name, max 12, hold 45d, stop −20%, regime_size overlay, overheat-AVOID, +D1 RE_BACKLOG_BUY (bank ICB 8633).
- **Structural reason it lags grinds**: it chases strength (RSI/MA-stack/near-highs/volume) → when leadership rotates, it holds the prior winners and buys into fading momentum. fa_tier used INVERTED (C/D get the strong-momentum tiers; A/B get quality/compounder) — momentum book likes lower-quality names.

## CURRENT SELECTION — LAG (Book B), PEAD schedule (logic in `pt_v22_dt5g.py` §4, panels from earnings pkls)
- Event filter: **NP_R ≥ 15** (earnings YoY surprise ratio) AND **prior_n_good ≥ 4** (≥4 prior good-surprise quarters = track record) AND **pa_HL3 ≥ 5** (3yr-half-life-weighted prior post-earnings drift ≥ 5%).
- Entry T+5 after Release_Date, hold 25 trading days, sizing 10% (LAG_HI if surprise>0.5) / 8% (LAG_LO), **NO stop**, ETF-park {3:0.7} idle cash.
- Pure post-earnings-announcement-drift (PEAD). ⚠️ **LAG edge at 3rd percentile** (latest-12M +0.26%/42% win vs 2024 peak +9.8%/80%) — see [[edge-health-monitor-amh1-2026]]; cyclical but must watch.

## PROGRESS
- ✅ **Angle #1 DONE (2026-06-12) — see `workspace/bal_lag_finding1_exbull.md`**: per-term IC attribution found BAL momentum block INVERTS in EX-BULL (state5==5, IC_mom −0.31, 3/3 episodes). This caused the START of the 2025-08 grind (Aug-Sep 2025 = 27d EX-BULL, book bought the top; overheat guard never fired). Fix = suppress momentum tiers in state5==5 → validated win on faithful engine (V2.2+capit 2025+ 18.3→19.85%, DD −18.7→−17.4; BAL-leg MaxDD −25.4→−20.6). NOT yet deployed live.
- ✅ **Finding #3 DONE (2026-06-11) — `workspace/bal_lag_finding3_allocator.md`**: state-conditional LAG/BAL capital allocator. LAG >> BAL & scales well & alpha real (not ETF-beta) but LAGS in BEAR (−14%/yr → BEAR=0). Two-book recommended w_LAG: CRISIS .50/BEAR 0/NEUTRAL·BULL·EXBULL .65 → FULL 24.8→26.1%/DD−18.6/Sh1.79, 2025+ 13.7→16.1%. Gentle>aggressive (hard tilt amplifies 2020 crash). Deploy MODERATE — LAG at percentile-3 edge-trough now.
- ✅ **Angle #2 DONE (2026-06-12) — see `workspace/bal_lag_finding2_neutral_grind.md`**: the NEUTRAL grind persistence is **NOT fixable by momentum selection** (structural). Momentum-of-momentum gate works pooled but stayed POSITIVE through the grind (didn't flag it). Decomposition: EW quality universe absolutely declined while index rose on megacaps (VIC). The actual grind winners (VIC ta89, energy BSR/GAS/PVD/OIL ta50-82, VVS) scored LOW-MID `ta` → 0/20 top winners buyable at ta≥140. Momentum gradient flat in NEUTRAL (can't lower threshold) but steep in BULL (can't raise). REDIRECT: capturing them needs an orthogonal CYCLICAL/ENERGY or megacap sleeve (not generic value Book C) — future session.

## Research angles for the new session (pick/sequence as you see fit)
1. **Component IC attribution on BAL's `ta`**: which of the ~22 terms actually predict fwd return, in which DT5G state? Decompose `ta` → per-term IC (clean LEAD fwd-ret, NOT profit_*). Likely finding hypothesis: momentum terms strong in trend, destructive in rotation; value/quality terms weak in bull. Re-weight or regime-condition the score.
2. **Style-rotation detector for BAL**: is there a causal signal (leadership breadth, momentum-of-momentum decay, sector dispersion) that flags when to DOWN-weight the momentum tiers vs lean COMPOUNDER/value tiers — WITHOUT a defensive stop (those failed)?
3. **LAG threshold re-fit + decay**: re-examine NP_R≥15 / prior_n_good≥4 / pa_HL3≥5 against latest data; has PEAD drift compressed (hold 25d still optimal)? Is the edge regime-conditional?
4. **fa_tier role revisit**: BAL inverts FA (C/D momentum). Memory says momentum book RESISTS FA overlays ([[fa-layer-ic-audit-2026]], [[fa-rating-8l-pergroup-2026]]) — re-confirm whether any quality gate helps SELECTION (vs sizing).
5. **Capacity-aware**: any selection change must hold at 50B+ NAV (capit capacity trap lesson). Validate on the faithful 2-ledger engine, not reduced harness.

## Data / entry points
- BAL signal: `signal_v11_sql.py` (SIGNAL_V11). LAG: `pt_v22_dt5g.py` §4 + earnings pkls (earnings_px / lagged_pos_ov / earnings_surprise_data / earnings_events_classified).
- Faithful engine: `simulate_holistic_nav.py` (`simulate()`); live track `pt_v22_dt5g.py`; leg NAVs `data/pt_v22_bal_v21_cap.csv` / `pt_v22_lag_v21_cap.csv`.
- BQ: `tav2_bq.ticker` (full feature history + MA/RSI/MACD/PE/FSCORE/NP), `ticker_prune` (quality universe + profit_* targets — training only), `vnindex_5state_dt5g_live` (regime). Column dict: `bigquery_dictionary.json`.
- ⚠️ Table/column name collision: always alias tables, qualify columns (e.g. `tk.ticker='VNINDEX'`). Forward cols (profit_*) NEVER as live filters; use clean LEAD fwd-ret for IC.

## Method discipline (from this workspace's track record)
- Signal-level edge ≠ integrated edge: validate every change on the FAITHFUL full-NAV book, not a reduced harness (many signal-level wins die at integration).
- Charge real TC; adversarially check; report rejections honestly. Momentum book has repeatedly RESISTED overlays — expect to reject more than you adopt.
