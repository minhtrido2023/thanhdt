# PREREG — BAL monthly edge-health gate vs BLIND (job Taylor_20261110_053025)
Written 2026-11-10 ~12:40 ICT BEFORE any treatment leg ran (only blind ledger + sign-persistence stat seen).

**Question:** does blocking NEW BAL buys after a negative month (unlock after positive) improve
risk-adjusted R3 vs BLIND, on top of DT5G + current gates?

**Engine:** R3 park0 pin command (registry "2026-10-08"), code `wt-balgate-1110` = bb700ab67 (BAL_MAX_POS
knob default 12, SLOT_AUDIT inert) + knob `BAL_BUY_BLOCK_FILE` (commits 2c69cfa62, 33f005209). Control legs
must be byte-identical to pins 537e349b (pin0%) / a6ba34d8 (pin1M). $DNA_PYEXE, threads=1, AUDIT_END 2026-06-19.

**Signal:** blind BAL book (`nav_bal_ref`, pin0% blind ledger) calendar-month return; month with mean stock
exposure <5% or ret==0 ⇒ "no sample" ⇒ hold state. Month M decides state for sessions of M+1+LAG (blocks first
fills; in-flight + exits untouched). Same schedule for both carries.

**Trials (N_trials = 8 rule configs, each × 2 carry conventions; carry is a convention, not a trial):**
G1_L0 (base) · G1_L1 · G1_L2 · G2_3m (3M trailing) · G3_x2 (lock < −2%) · G4_hu2 (unlock needs 2 pos) ·
G5_hl2 (lock needs 2 neg) · G6_n3 (sample needs ≥3 BAL buys or expo ≥30%). Extra: G1_L0 CAPIT-exempt (sensitivity,
counted → N_trials=9), G1_L0 on LAG book (measurement only, not a trial).

**N independent:** G1 = 26 lock episodes / 51 transitions / 62 of 150 months; 101 consecutive sample-month pairs.
Pre-flight (per-episode, N=26, 9 trials): detectable only if incremental Sharpe ≥ 0.96/yr; Sharpe 1.0 GO, 0.5 NO-GO.

**Primary metric:** ΔCalmar and ΔSharpe (gate − blind), combined R3 NAV, BOTH carries; DD anchor = floor (pin0%).
**Decision rule (fixed now):** EFFECTIVE only if G1_L0 ΔSharpe AND ΔCalmar > 0 with paired block bootstrap
(L=21, B=4000) P>0.95 under BOTH carries, IS and OOS same sign, LOO-year never flips sign, beats ≥95% of placebos
(random lock schedules, same months-locked fraction and transition count, ≥1000 draws) and DSR ≥0.95 across family.
HARMFUL if ΔCAGR/ΔCalmar <0 with P>0.95. Otherwise INDISTINGUISHABLE (= risk preference, not edge).
Placebo is run on a trade-subtraction approximator (full engine ×1000 infeasible); approximator validated against
the full engine on the real variants before use.
