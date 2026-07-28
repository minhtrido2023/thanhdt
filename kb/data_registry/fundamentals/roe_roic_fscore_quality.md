---
kind: bigquery-column
status: CANONICAL
source: ROE / ROIC / FSCORE / quality-gate cột (ROE5Y, ROE_Min3Y/5Y, ROIC3Y/5Y, ROIC_Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0, NP_P0..P3, CF_OA_P0..P3, CF_OA_3Y, OShares trong ticker+ticker_financial)
group: fundamentals
note: hồi tố đã verify AN TOÀN (job Winston_20260717_070859)
writer: Ingest ETL, cùng cadence ticker_financial
---

# ROE / ROIC / FSCORE / quality-gate cột (`ROE5Y, ROE_Min3Y/5Y, ROIC3Y/5Y, ROIC_Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0, NP_P0..P3, CF_OA_P0..P3, CF_OA_3Y, OShares` trong `ticker`+`ticker_financial`)

**Status: CANONICAL — hồi tố đã verify AN TOÀN**

## Là gì
Chỉ số chất lượng/quality-gate của 8L model, input `rating_8l.py`. bq_admin đang chủ động đổi phương
pháp tính nhiều chỉ số FA (~2026-07, đã báo).

## Ai ghi / cadence
Ingest ETL, cùng cadence `ticker_financial`.

## Bẫy
**(1) KHÔNG HỒI TỐ — golden-floor ỔN ĐỊNH** (job Winston_20260717_070859): so pre-change cache June-25
(`bq_cache/ticker/*`) vs BQ live, toàn universe ~1160-1250 mã × 2 ngày (2020-01-15, 2023-06-01): **100%
IDENTICAL 0-diff** cho ROE5Y/ROE_Min3Y/5Y, ROIC3Y/5Y/Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0,
NP_P0..P3, CF_OA_P0..P3, OShares, EVEB. **Golden-floor pass-set (`ROE_Min3Y≥0 ∧ CF_OA_3Y>0`): 0 FLIP**
(588/588 @2020, 530/530 @2023). `ticker_financial` Jul-8 vs Jul-16: **0 change** mọi cột trên →
R3/backtest pin + rating_8l value/quality **AN TOÀN**, lịch sử KHÔNG viết lại. **(2) `CF_OA_3Y` = tổng
CF_OA thô đơn vị VND** (KHÔNG phải sum ratio CF_OA_P0..P2 như dictionary gợi ý) — nhưng **cùng dấu**
sum(P0..P2) nên test golden-floor `>0` nhất quán; rating_8l đọc thẳng cột. **(3) Dividend_Min3Y ĐÃ ĐỔI
method** (June-25→Jul-8: continuous/nội suy ~702.0/415.0 → round event-based VND/sh ~800/1500/0,
~54/1250 mã) — NHƯNG là **value-LENS `div_yield`, KHÔNG phải golden-floor gate** (rating_8l.py:674-676
xác nhận rõ), bản LIVE = đúng "event-based" model đã thiết kế/backtest, đổi TRƯỚC pin R3 07-11 +
refresh fa_ratings_8l 07-12 → không tạo bất nhất ẩn. **(4) PB_MA5Y/PB_SD5Y** lệch nhỏ (~0.3-3%, ~57
mã, rolling 5Y stat feed pb_z) — non-material, không phải gate. **(5) Outlier ROE5Y/ROIC5Y cực đoan
(±25..50) + Debt_Eq âm** = PRE-EXISTING (0 hồi tố), mẫu số equity≈0, rating_8l dùng percentile-zone +
DẤU ROE_Min3Y nên robust. Hand-calc ROE_Trailing≈NP_ttm/equity khớp VNM/MBB/VCB(bank).
