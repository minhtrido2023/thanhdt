---
kind: bigquery-column
status: CANONICAL
source: PE / PB / PCF / PS (cột trong ticker + ticker_financial)
group: fundamentals
note: công thức đã verify bằng tính tay (job Winston_20260717_063633)
writer: Ingest ETL, cùng cadence ticker_financial
---

# PE / PB / PCF / PS (cột trong `ticker` + `ticker_financial`)

**Status: CANONICAL — công thức đã verify**

## Là gì
Định giá "tự tính từ tài chính thô" (bq_admin đổi từ nguồn bên-thứ-3 sang self-computed, ~2026-07).
**Công thức xác nhận bằng tính tay** (job Winston_20260717_063633): **PE = Price / EPS_ttm** (EPS_ttm =
Σ(NP_P0..P3)/OShares, 4 quý trailing) · **PB = Price / BVPS** · **PCF = Price / CF_ttm** · PS =
Price/Rev_ttm. Nhất quán giữa `ticker` daily và `ticker_financial` quarterly; ngân hàng dùng cùng công
thức NP-based. VNM/MBB khớp tới 4 chữ số.

## Ai ghi / cadence
Ingest ETL, cùng cadence `ticker_financial`.

## Bẫy
**(1) KHÔNG hồi tố** — verify toàn universe (~1260 mã × 2 ngày lịch sử 2023-06-01/2024-01-15) so
snapshot pre-change `bq_cache/ticker/*.parquet` (June-25) vs BQ live: PE/PB/PCF/BVPS + PE_MA5Y/PB_SD5Y
**giống hệt >99.7%** (0 PB đổi, ≤2 PE, ≤3 PCF>1% toàn mã illiquid); `ticker_financial` PE/PB/PS/PCF
100% identical July-8 vs July-16. → **mọi backtest đã pin + rating_8l an toàn, lịch sử KHÔNG bị viết
lại**. **(2) Negative PE/PCF là bình thường & PRE-EXISTING** — mã lỗ → PE âm (52/797 mã), CF hoạt động
âm → PCF âm (236/797); KHÔNG NULL-hóa (rating_8l đã tự guard: `cfo_yield` chỉ 1/PCF khi PCF>0). **(3)
`bigquery_dictionary.json` STALE**: ghi range "0..Inf" cho PE/PB/PCF nhưng thực tế có âm; và KHÔNG ghi
provenance self-computed — cần cập nhật (non-blocking).
