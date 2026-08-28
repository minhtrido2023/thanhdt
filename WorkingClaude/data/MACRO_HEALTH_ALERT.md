⚠️ MACRO HEALTH FAILED (SEV SEV1) @ 2026-08-28 15:00
-> use state source: DT4_only
market stress: False (vix_elevated=False, vni_below_ma200=False)
failing checks:
  [SEV1] v34b_csv_read: Command '"bq" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=2000000 < "/tmp/tmp664h71q3.sql"' returned non-zero exit status 1.
  [SEV1] bq_ticker_query: Command '"bq" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=2000000 < "/tmp/tmpcspq4jrr.sql"' returned non-zero exit status 1.
  [SEV1] macro_probe: get_macro_state failed: Command '"bq" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=2000000 < "/tmp/tmpvof0qdth.sql"' returned non-zero exit status 1.
stale/missing sources:
  local_v34b_state_csv: MISSING / unreadable
  bq_ticker_vnindex: MISSING / unreadable