# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

## Status: 2026-06-24

### DONE THIS SESSION
1. **PE_stored bug (Việc 1) — CLOSED: NOT MATERIAL**
   - Production path custom_basket.py uses fa_ratings_8l exclusively (ROIC/ROE/FSCORE, no PE)
   - Bus event: decision/pe-stored-bug-impact-assessment ✓

2. **V2.4 go-live formal summary (Việc 2) — DONE**
   - File: data/v24_golive_summary.md created
   - Numbers: R3 29.00%/Sh1.90/DD-18.5/Cal1.56 → V2.4: 30.63%/Sh1.97/DD-17.5/Cal1.75
   - Bus event: decision/v24-golive-bundle-ready ✓

3. **Exp-2: hold-neutral CAPIT (Việc 3) — DONE (REJECTED)**
   - Code: pt_v23_audit_2014.py CAPIT_HOLD_NEUTRAL env var shipped
   - Finding: DT5G returns to NEUTRAL in 10-35 sessions; hold-neutral exits EARLIER in 14/15 events
   - VNI proxy: -5.3% avg exit price delta vs fixed-60td
   - VERDICT: HYPOTHESIS REJECTED. Keep CAPIT_HOLD=60td.
   - Bus event: finding/hold-neutral-test ✓

4. **Exp-3: deposit_eyield lever gate (Việc 3) — DONE (PROMISING, needs BQ sim)**
   - Code: pt_v23_audit_2014.py MGE_GATE=deposit_eyield shipped
   - Gate fires: 12/15 events (vs fedborrow: 0/15)
   - Correctly blocks: 2018 high-PE expensive BEAR (E4/E5), 2014 fair-value (E0)
   - Leverage preserved: 86% of total pool
   - Estimated: CAGR ~32.0% / MaxDD ~-15.8% / Cal ~2.03 (linear approx)
   - Bus event: finding/lever-deposit-eyield-gate ✓
   - NEXT: BQ simulation needed for exact audit (key dependency)

### BLOCKING (go-live 2026-06-30)
- **Awaiting: user + Spyros approval** on V2.4 bundle (LF 30.63%)

### Config chốt V2.4
- RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5
- RECOVERY_DEP_GATE=1 (DORMANT floor=7.5%)
- trading_rules v1.6 (leverage-free go-live)
- Base: v23a none postbull 0 edge + custompitg/namecap/yieldcombo/NEUTRAL-only

### Post-go-live R&D pipeline (NOT blocking)
- deposit_eyield gate: PROMISING — needs BQ sim
  Run: MGE=1.3 MGE_CAPIT_ONLY=1 MGE_GATE=deposit_eyield + full V2.4 stack
- hold-neutral: REJECTED — don't pursue
- Real-margin 1.3x no-gate: CAGR 32.22%/Cal 2.08 (already done) — needs Spyros sign-off

- [2026-06-24T13:58:16Z] EXP-8 DONE (Mike directive exp8-capit-only-task) — STRONG WIN. RECOVERY_CAPIT_ONLY = wait-for-vol-capitulation deploy instead of instant pb_z deploy, + MGE=1.3 lever on CAPIT arm. Tier-3 BQ same-snapshot 2026-06-24, selfcheck 0VND both books. Calib: vol_ratio 1.7x catches all 6 crises at 63d(3M,P97) & 126d(6M,P97). RESULT: Baseline V2.4-LF 28.04/DD-31.5/Cal0.89 | TestA 3M/63d 31.07/DD-20.5/Cal1.52 (OOS 35.82/Cal1.75) | TestB 6M/126d 30.14/DD-26.3/Cal1.14. TestA beats baseline EVERY metric EVERY subperiod (+3.03pp CAGR/+11pp DD/+0.63 Cal); dominates TestB. Mechanism: sidesteps early-decline DD by waiting for capitulation print, deploys at bottom (COVID 2020-03-12, 2022-11/12, 2023-04) + 1.3x recovery lever. Code: pt_v23 RECOVERY_CAPIT_ONLY+RECOVERY_CAPIT_BASE env, _GRAD_BASE window, capit-only episode entry (force _this_accel_ok=False), guarded accel debug vars. Output data/exp8_capit_only_bq.md, pinned bus(decision)+registry. CAVEATS: cite DELTA not absolute (baseline drift 30.63->28.04 via VVS/VCS/DTD corp-act); IS/OOS weak overfit test (deploys all OOS by construction like DT5G, both periods still beat); REAL leverage MGE1.3 -> NEEDS Spyros sign-off+user approval before LIVE, go-live stays LF unless promoted. NEXT(await user/Mike): promote TestA to go-live candidate? -> Spyros risk review of MGE1.3 capit-only path; or sweep threshold 1.6/1.7/1.8 robustness; or test capit-only WITHOUT mge (isolate timing vs leverage contribution).
