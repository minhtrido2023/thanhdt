---
name: ticker_ingest_lag_ticker1m_switch
description: BQ ticker table ingests late (~22:30 VN); live scripts switched to ticker_1m for same-day freshness; ticker_1m has NO VNINDEX
metadata: 
  node_type: memory
  type: project
  originSessionId: 3989bbcc-d947-47c5-a6eb-b9a6cc4ea7cb
---

Verified [REDACTED]09 (VN 16:40). Data-freshness map of the BQ feature tables and the live-consumer fix.

**Ingest cadence (upstream ETL, NOT in this repo — no script here writes `tav2_bq.ticker`):**
- `tav2_bq.ticker` (heavy feature table, partitioned by MONTH despite CLAUDE.md saying DAY) ingests **at night ~22:30–22:40 VN**. So any script reading it before ~22:30 gets data only up to **yesterday's** session. Evidence: June partition last_modified 06-08 22:39; May partition 06-04 22:38.
- `tav2_bq.ticker_1m` refreshes **intraday, fresh by ~16:40 VN** (has today's session). Full universe (1,252 tk) but only the latest **~22 trading days**. Same schema EXCEPT it lacks `PS`.
- `tav2_bq.vnindex_5state_dt5g_live` also has today (06-09) — state pipeline pulls VNINDEX from its own source, not `ticker`.

**⚠️ Key gotcha: `ticker_1m` does NOT contain VNINDEX (0 rows — only individual tickers).** So index-level reads (VNINDEX RSI/overheat) CANNOT be de-lagged via ticker_1m. In `signal_v11_sql.py` the VNINDEX `latest_vni_max3m`/`vni_history` CTEs stay on `ticker` (lag is immaterial — rsi_max3m is a 60-session rolling max). The stock-panel `ticker_data` CTE already had a ticker_1m fallback.

**Paper-trade lag is BY DESIGN, separate issue:** `pt_dates.detect_end_date()` caps END_DATE at `today-1` (T+1, no look-ahead). So pt_v4_dt5g etc. mark to yesterday regardless of ingest — fixing ticker ingest does NOT change paper-trade output.

**Fix applied [REDACTED]09 — switched latest-session CTE from `ticker`→`ticker_1m`** (keep deep-history side-CTEs like 52w-high on `ticker`):
- SWITCH (full): `vn30_8l.py` (_liquidity), `power_lens.py` (px CTE), `recommend_lh.py` (live snapshot, also fixed docstring mismatch), `universe_scan.py` (7d universe).
- HYBRID (latest row→1m, keep 52w-high on ticker): `unified_screener.py` (latest CTE — gates the whole 8L daily chain → rank_8l→daily_alert→bot), `dna_card.py`, `dna_report.py` (live_now).
- Round 2 (all run-tested exit 0): `quality_tactical_scanner.py` (market snapshot CTE→1m, keep 52w-high 400d on ticker), `whitelist_monitor.py` (additive overlay: append freshest ticker_1m Close for stocks onto the 500d history; VNINDEX stays on ticker), `golive_recommend.py` D1 ICB-8633 panel (fallback-UNION pattern — SAFE for its 15:30 run: adds rows only for dates ticker lacks, no-op if ticker_1m not ready yet).
- CANNOT de-lag (VNINDEX not in ticker_1m): `golive_recommend.py` overheat gate, `recommend_holistic.py`(+`deploy_v11/`) VNI_OVERHEAT — left on ticker (1-day lag immaterial for slow regime gate). recommend_holistic STOCK snapshot was ALREADY hybrid (UNION ticker+ticker_1m) → no change.

**Schedule timing (Windows Task Scheduler, verified):** `8L_Daily_Alert`(pt_8l_daily.bat)=17:45 → ticker_1m ready (finalizes ~16:41) ✓. `PaperTrade3Sys`(papertrade_daily.bat)=15:30 → contains golive_recommend; at 15:30 ticker_1m may not be ready yet → use additive/fallback patterns (not hard SWITCH) so it's a safe no-op when stale. Real lever for the 15:30 batch = reschedule later (~17:00) if same-day freshness needed there.
- Already-fresh / no change: `rating_8l.py` (reference impl, already ticker_1m), `cheap_pb_floor.py`/`rank_8l*` (read CSVs), `recommend_tomorrow.py` (scoring already ticker_1m).

Validated: rewritten queries return time=[REDACTED]09; SIGNAL_V11 dry-run passes. See [[daily_report_dt5g_v4_2026]].
