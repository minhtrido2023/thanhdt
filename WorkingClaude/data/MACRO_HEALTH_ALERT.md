⚠️ MACRO HEALTH FAILED (SEV SEV1) @ 2026-06-26 23:21
-> use state source: DT4_only
market stress: True (vix_elevated=True, vni_below_ma200=False)
failing checks:
  [INFO] sbv_verify_reminder: last SBV refi event 1103d old (4.5%) — MANUALLY VERIFY vs SBV; cannot auto-detect a missed rate change
  [SEV2] missed_runs: 2 trading days since last successful run (2026-06-24)
stale/missing sources:
  local_v34b_state_csv: as_of=2026-06-19 age=5td (max 3)
macro now: {'date': '2026-06-25', 'state': 3, 'state_dt4': 3, 'cap': 9, 'easing': False, 'active': False}