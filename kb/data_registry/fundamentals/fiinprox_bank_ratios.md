---
kind: derived-file
status: UNVERIFIED (1 nguồn, trial account) — 3/9 mã cross-check khớp sát nguồn cũ (VCB/ACB/TCB), 2 lệch nhẹ (BID/HDB), 4 chưa đối chiếu
source: data/fiinprox_bank_ratios_20260914.csv
group: fundamentals
writer: Mike (thủ công qua MCP tool call, KHÔNG có script/cron)
upstream: FiinXMCP (`mcp__claude_ai_FiinXMCP__get_fundamental_data`, data_type=ratios) — FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_bank_ratios` — CAR/CASA/NIM/NPL/LLR 9 ngân hàng, 2018-2025 (FiinPro-X trial)

## Vì sao tồn tại

Gap đã biết từ lâu (xem `bank_casa_ldr.md` "Vì sao tồn tại"): BQ `ticker_financial` không có
NPL/CAR/NIM/CASA cho ngân hàng. `bank_casa_ldr.md` lấp gap này bằng OCR BCTC gốc — cực kỳ chính
xác nhưng chỉ **1 kỳ** (Q2/2026) và chỉ 2 chỉ tiêu (CASA+LDR), tốn công OCR nặng nếu muốn thêm kỳ.

FiinPro-X (đang dùng thử, hết hạn **2026-09-28**) cho **5 chỉ tiêu** (CAR/CASA/NIM/NPL/LLR coverage)
× **8 năm** (2018-2025) × **9 mã** qua 1 lệnh API — không OCR, không rủi ro đọc nhầm chữ số.

## Cách lấy (không có script — gọi tool trực tiếp qua session có MCP)

1. `search_fundamental_fields` với keyword tiếng Việt (NPL/CAR/CASA/NIM) → lấy `path_mapping.BANK`
2. `get_fundamental_data(data_type="ratios", tickers=[...], years=[...], fields=[path_mapping...])`

5 field path dùng trong file này:
- CAR: `1_capital_adequacy_component.car`
- CASA: `2_asset_quality_component.casa_ratio`
- NIM: `5_profitability_component.nim`
- NPL (nợ nhóm 3-5/tổng dư nợ — ĐÚNG định nghĩa NPL chuẩn, không phải nợ xấu tuyệt đối):
  `4_liquidity_and_assets_component.debt_category_3_5_gross_loan_to_customer`
- LLR coverage (dự phòng/nợ xấu): `2_asset_quality_component.loan_loss_reserves_np_ls`

⚠️ Không có script tái lập — MCP tool chỉ gọi được trong session có connector `FiinXMCP` đã OAuth
(xem `kb/current_ops.md` hoặc hỏi Mike cách connect). Không chạy được qua `bin/dispatch.sh` headless
(cần OAuth tương tác, xem log kết nối 2026-09-11→09-14).

## Đối chiếu với audit cũ (26/08, nguồn BCTC/báo chí Q2/26 độc lập) — 2026-09-14

| Mã | NPL cũ | NPL FiinPro 2025 | Coverage cũ | Coverage FiinPro 2025 | Khớp? |
|---|---|---|---|---|---|
| VCB | 0,61% | 0,59% | 279% | 258% | ✅ khớp gần tuyệt đối |
| ACB | 1,03% | 0,98% | 105% | 114% | ✅ khớp sát |
| TCB | 1,08% | 1,08% | 126% | 128% | ✅ khớp gần tuyệt đối |
| BID | 1,83% | 1,50% | 76% | 100% | ⚠️ lệch — có thể do vintage (FY2025 vs Q2/26) |
| HDB | 2,12% | 2,47% | 50% | 55% | ⚠️ lệch nhẹ, cùng hướng "mỏng nhất" |
| MBB | ~1,7-1,9% (ước) | 1,31% | 93,6% | 94% | ✅ FiinPro tốt hơn ước tính cũ |

3/6 mã khớp gần tuyệt đối với nguồn độc lập → dữ liệu đáng tin. CTG/STB/VPB chưa có số đối chiếu cũ.

## Bẫy đã biết

1. **CTG có `car=0.0` ở 2018 và 2020** — rõ ràng thiếu dữ liệu (null bị trả về 0), KHÔNG phải CAR
   thật bằng 0. Đừng tính trung bình/percentile gộp cả 2 điểm này.
2. **`year` trong response luôn kèm `quarter=5`** — đây là marker "cả năm" của FiinPro-X (không
   phải quý 5 có thật). Không nhầm với dữ liệu quý thật (chưa test field `quarters=[1,2,3,4]`
   trong job này).
3. **CASA định nghĩa CHƯA xác minh khớp `bank_casa_ldr.md`** — file đó phân biệt 3 công thức CASA
   khác nhau (strict/narrow/pressdef) và cảnh báo lệch tới 2,65pp tùy công thức. FiinPro-X trả 1
   con số `casa_ratio` duy nhất, chưa biết khớp công thức nào. Đừng thay thế `bank_casa_ldr.md`
   bằng file này cho tới khi đối chiếu công thức tại cùng 1 kỳ (Q2/2026).
4. **STB NPL 2025 = 6,62%** — cao bất thường so 8 mã còn lại (0,6-2,5%), không nắm giữ trong
   portfolio nhưng đáng nhớ nếu sau này cân nhắc.
5. **Trial hết hạn 2026-09-28** — sau đó không gọi lại được tool này trừ khi mua subscription.
   Muốn thêm mã/năm/chỉ tiêu khác, làm TRƯỚC hạn đó.

## Điều kiện để nâng status

- Cần đối chiếu CASA cùng kỳ Q2/2026 với `bank_casa_ldr.md` (khác nguồn hoàn toàn — BCTC gốc OCR
  vs FiinPro-X ratios) để biết công thức có khớp không.
- Cần ≥1 consumer thật (hiện chỉ dùng để đánh giá mua/không mua FiinPro-X, chưa wire vào bất kỳ
  gate/screen production nào).

↩ [Về nhóm fundamentals](index.md) · [Về index tổng](../index.md)
