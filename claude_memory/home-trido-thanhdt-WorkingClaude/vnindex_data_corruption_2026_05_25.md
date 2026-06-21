# VNINDEX BQ data corruption (2026-05-25)

## Incident
User uploaded VNINDEX_PE update tới BQ → bulk-upload script vô tình **overwrite Close + D_CMF (và có thể D_RSI/MA200) toàn bộ 2014-2026 VNINDEX rows** với rounded/stale values.

## Evidence
- BQ now vs time-travel 24h ago, 3088 VNINDEX rows 2014-2026:
  - `Close`: **98.7%** rows changed (corrupted với rounded values 670/680/690...)
  - `D_CMF`: **98.6%** rows changed (set = 0 cho 100% phiên 2013/2014/2016/2019)
  - `VNINDEX_PE`: **7.9%** rows changed (user's actual intended update = 245 days)
- Other tickers (VNM/FPT/HPG/VCB/MWG) **UNCHANGED** — corruption only on VNINDEX.
- Local `VNINDEX.csv` (May 10) has clean OHLC+PE 2014→2026-03-30.

## Impact on v3.4b model state
- Pre-corruption state distribution (BQ backup `vnindex_5state_archive_tinh_te_20260525_220509`): CRISIS 23.9%, NEUTRAL 50.4%
- Post-corruption (fresh refresh today): CRISIS 55.7%, NEUTRAL 25.4%
- **37.9% of all 2014-2026 days** got reclassified (1169/3085)
- Year 2017: **100%** phiên flip; 2014/2016/2019/2021: 50-70% flip

## Root cause **NOT** model weight
Tested W_PE = 0.00 / 0.01 / 0.03 → all give CRISIS ~55% (no recovery). Model architecture OK. 100% data-source issue.

## Restore procedure
BQ time-travel works (verified 24h ago = clean Close 672.01, D_CMF 0.079 for 2017-01-03).

### Option A (full revert):
```sql
DELETE FROM `tav2_bq.ticker` WHERE ticker = 'VNINDEX';
INSERT INTO `tav2_bq.ticker`
SELECT * FROM `tav2_bq.ticker`
  FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
WHERE ticker = 'VNINDEX';
```

### Option B (preserve user's PE update — RECOMMENDED):
MERGE: restore Close + High + Low + Open + Volume + D_CMF + D_RSI + MA200 + D_MACDdiff... từ time-travel, KEEP VNINDEX_PE current.

### Rollback LIVE state table:
```bash
bq cp tav2_bq.vnindex_5state_archive_tinh_te_20260525_220509 tav2_bq.vnindex_5state
```

## Lessons learned
1. **Always sanity-audit data sources** before trusting state pipeline output. Check `Close_uniq_pct` and `CMF_zero_pct` per year — if too low/high → corruption.
2. **Bulk upload scripts on BQ** must use MERGE INTO with explicit column list, NOT INSERT OR REPLACE which can null other columns.
3. **State distribution shift > 5pp** in any state should trigger an audit before deploy.
4. **BQ time-travel** is the friend — 7-day default window, use for forensics + emergency restore.
5. **Local VNINDEX.csv** is golden source — use as fallback when BQ suspicious.

## Trigger for future Claude
Nếu user báo "tôi vừa update X lên BQ" → trước khi trust output:
1. Query `Close_uniq_pct` and key cols by year for X
2. So sánh với `FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(NOW, INTERVAL 24 HOUR)` xem có collateral damage
3. Only refresh pipeline cache AFTER data validation passes
