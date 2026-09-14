---
kind: derived-file
status: DERIVED — coverage (LLR) khớp OCR primary 8/9 mã tới 0,1pp (Q2/2026); NPL lệch có hệ thống +1-2% tương đối; CASA đã verify ở file năm
source: data/fiinprox_bank_ratios_quarterly_20260914.csv (raw: data/fiinprox_bank_q_raw/)
group: fundamentals
writer: Mike (thủ công qua FiinXMCP execute_api → client.FundamentalAnalysis().get_ratios, KHÔNG có script/cron)
upstream: FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_bank_ratios_quarterly` — NPL/NIM/CASA/LLR 27 ngân hàng theo quý, 2010Q1→2026Q2

1.392 dòng (ticker × quý), 27 mã ICB 8355 (toàn bộ NH có trong `tav2_bq.ticker`). 1.289 dòng đủ
cả 4 chỉ tiêu. Cột: `npl_ratio_3_5_pct`, `nim_pct`, `casa_ratio_pct`, `llr_coverage_pct`, `flags`.
Không có CAR theo quý (CAR chỉ theo năm, xem `fiinprox_bank_ratios.md`, 9 mã).

Độ phủ: 7 mã có từ 2010 (ACB CTG EIB SHB STB VCB NVB); phần lớn mã còn lại đủ quý từ 2017-2018;
BVB/VAB trống nhiều quý 2018-2020; nhiều mã chỉ có Q4 trước 2017.

## Đối chiếu (2026-09-14)
1. **vs OCR BCTC gốc `data/bank_npl_coverage_primary_20260828.csv` (Q2/2026, 9 mã)**:
   - Coverage: khớp **8/9 mã tới 0,1pp** (BID 75,9 · CTG 134,0 · VCB 279,3 · ACB 105,3 · TCB 125,6 ·
     MBB 93,6 · VIB 43,6 · STB 56,7). SHB lệch −5,6pp (76,9 vs 82,5).
   - NPL: FiinPro **cao hơn có hệ thống +1,1-1,7% tương đối** ở 7 mã (vd MBB 1,470 vs 1,450; BID
     1,853 vs 1,827) ⇒ khác mẫu số (khả năng FiinPro loại cho vay ký quỹ/khoản khác khỏi dư nợ).
     Giữ nguyên thứ hạng. STB +0,34pp, SHB +0,14pp lệch nhiều hơn.
2. **vs file năm đã lưu (Q4 so với năm, 72 cặp mã-năm, 9 mã 2018-2025)**: NPL khớp ≤0,01pp 68/72,
   CASA 67/72, LLR ≤0,5pp 66/72. Lệch lớn (TCB 2022 NPL 0,92 vs 0,73; VCB 2019) = số quý 4 chưa
   kiểm toán vs số năm đã kiểm toán — đúng kỳ vọng, không phải lỗi.

## Bẫy
1. **NIM là luỹ kế từ đầu năm, quy năm** (Q1→Q4 trượt dần tới số năm), không phải NIM riêng quý.
2. **Bản ghi rác của provider đã xoá**: LLR âm/0 (33 dòng, mẫu 2010Q3/2013Q2: CASA trống + LLR âm =
   dòng phản chiếu), NPL=0 (12), CASA<0,5 (5). 71 dòng chỉ còn NIM (`flags=nim_only`). Dòng trùng
   kỳ (2010Q4 nhiều mã, chỉ khác NIM) giữ bản đầu tiên.
3. OCB 2016Q4 CASA 99,7% = rác (`casa_gt_60_suspect`). LPB 2015Q4 58,9% cũng đáng ngờ.
4. CASA = định nghĩa **narrow** (xem `fiinprox_bank_ratios.md`).
5. Cú nhảy NPL thật, không phải lỗi: SHB 2012Q3 13,8% (sáp nhập Habubank), STB 2015Q4-2017 (sáp nhập
   Phương Nam), NVB 2022-2024 tới 35,9%, KLB 2020 ~6,7%, STB 2025Q4→2026Q2 6,6→7,9%.
6. Số theo ngày công bố KHÔNG có ⇒ không phải PIT; khi backtest phải trễ ≥45 ngày sau quý (Q4: ≥90).

## Consumer tiềm năng (CHƯA wire)
`bank_lens_v3.py` / `rating_8l.py::rate_bank()` — hiện NaN NPL/coverage 9/18 mã. Wire = quyết định
riêng, qua quant-skeptic.

↩ [Về nhóm fundamentals](index.md) · [Về index tổng](../index.md)
