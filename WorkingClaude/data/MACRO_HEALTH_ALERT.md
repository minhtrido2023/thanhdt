⚠️ MACRO HEALTH FAILED (SEV SEV1) @ 2026-07-03 08:00
-> use state source: DT4_only
market stress: False (vix_elevated=False, vni_below_ma200=False)
failing checks:
  [SEV1] bq_ticker_query: Command '"bq" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=2000000 < "/tmp/tmpaeszp_1x.sql"' returned non-zero exit status 127.
  [SEV1] macro_probe: get_macro_state failed: Command '"bq" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=2000000 < "/tmp/tmpoglbutll.sql"' returned non-zero exit status 127.
stale/missing sources:
  bq_ticker_vnindex: MISSING / unreadable