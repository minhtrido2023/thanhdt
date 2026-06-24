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

