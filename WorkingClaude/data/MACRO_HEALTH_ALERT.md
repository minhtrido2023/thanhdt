⚠️ MACRO HEALTH FAILED (SEV SEV1) @ 2026-06-22 15:30
-> use state source: DT4_only
market stress: False (vix_elevated=False, vni_below_ma200=False)
failing checks:
  [SEV1] bq_ticker_query: unsupported operand type(s) for -: 'datetime.date' and 'NaTType'
  [INFO] sbv_verify_reminder: last SBV refi event 1099d old (4.5%) — MANUALLY VERIFY vs SBV; cannot auto-detect a missed rate change
  [SEV1] macro_probe: get_macro_state failed: 'time'
stale/missing sources:
  bq_ticker_vnindex: MISSING / unreadable