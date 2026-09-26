---
kind: group-index
group: fundamentals
title: Fundamentals / tài chính
---

# Fundamentals / tài chính

| Nguồn (file) | Status |
|---|---|
| [`bank_casa_ldr.md`](bank_casa_ldr.md) — CASA + LDR rổ 13 NH đang nắm giữ (`data/bank_casa_ldr_*.csv` LDR · `data/bank_casa_primary_*.csv` CASA; vnstock/VCI + thuyết minh BCTC gốc) | **DERIVED** cả 2 chân — LDR verify chéo 5/5; CASA 13/13 mã từ BCTC gốc, 3 chân verify. Chỉ **1 kỳ** (Q2/2026), 3 cột CASA khác định nghĩa — đọc bẫy trước khi trích |
| [`fiinprox_bank_ratios.md`](fiinprox_bank_ratios.md) — CAR/CASA/NIM/NPL/LLR 9 NH, 2018-2025 (`data/fiinprox_bank_ratios_20260914.csv`; FiinXMCP trial, hết hạn 2026-09-28) | **DERIVED** (CASA — khớp OCR 12/13 mã tới 3-4 số lẻ, = `casa_narrow_pct` KHÔNG phải strict); **UNVERIFIED** (NPL/CAR/NIM/LLR — chỉ cross-check gián tiếp) |
| [`fiinprox_bank_ratios_quarterly.md`](fiinprox_bank_ratios_quarterly.md) — NPL/NIM/CASA/LLR 27 NH theo quý 2010Q1→2026Q2 (`data/fiinprox_bank_ratios_quarterly_20260914.csv`; FiinPro-X trial) | **DERIVED** — coverage khớp OCR 8/9 mã tới 0,1pp; NPL cao hơn OCR +1-2% tương đối (khác mẫu số); NIM luỹ kế năm |
| [`fiinprox_oshares_pit.md`](fiinprox_oshares_pit.md) — số CP lưu hành theo NGÀY ĐỔI SỐ, 647 mã universe_pit 2013→2026-09 (`data/fiinprox_oshares_pit_20260926.csv`; FiinPro-X trial, snapshot một lần) | **UNVERIFIED-PIT** — chưa nghiệm thu với `corporate_action` (H3); ứng viên thay TRAP `OShares` cho cửa sổ lịch sử |
| [`insider_transaction.md`](insider_transaction.md) — tav2_bq.insider_transaction (giao dịch nội bộ TT96/2020) | CANONICAL (4 bẫy PIT — đọc trước khi dùng) |
| [`insider_transaction_snapshots.md`](insider_transaction_snapshots.md) — lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots (snapshot tiến-tới; đường DUY NHẤT lấy lại ngày công bố ĐĂNG KÝ, từ 2026-08-17) | CANONICAL (2 bẫy PIT riêng + mọi bẫy bảng nguồn) |
| [`risk_rating.md`](risk_rating.md) — tav2_bq.risk_rating | CANONICAL |
| [`roe_roic_fscore_quality.md`](roe_roic_fscore_quality.md) — ROE / ROIC / FSCORE / quality-gate cột (ROE5Y, ROE_Min3Y/5Y, ROIC3Y/5Y, ROIC_Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0, NP_P0..P3, CF_OA_P0..P3, CF_OA_3Y, OShares trong ticker+ticker_financial) | CANONICAL |
| [`ticker_financial.md`](ticker_financial.md) — tav2_bq.ticker_financial | CANONICAL |
| [`ticker_financial_oshares.md`](ticker_financial_oshares.md) — cột `OShares` (số CP lưu hành theo quý) | **TRAP** (RESTATE, không point-in-time — đọc TRƯỚC khi viết code chạm cột này) |
| [`valuation_pe_pb_pcf_ps.md`](valuation_pe_pb_pcf_ps.md) — PE / PB / PCF / PS (cột trong ticker + ticker_financial) | CANONICAL |

↩ [Về index tổng](../index.md)
