# Mike fleet — context mini (native agents)
> Chỉ các fact cốt lõi. Full KB: kb/context_pack.md

- **BQ**: project `lithe-record-440915-m9`, dataset `tav2_bq`, region `asia-southeast1`
- **CLI**: `bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 'SQL'`
- **Tables**: `ticker` (daily OHLCV), `ticker_prune` (liquid universe), `ticker_financial` (quarterly), `vnindex_5state_dt5g_live` (market regime)
- **Production strategy**: V2.4 — custom30V basket, DT5G gate, go-live 2026-06-30
- **Bus**: write findings via `append_event.sh <agent> finding <topic> '<json>'` (lands in `bus/inbox/<agent>.jsonl`)
- **Codebase root**: `/home/trido/thanhdt/WorkingClaude`
