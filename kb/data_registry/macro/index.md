---
kind: group-index
group: macro
title: Vĩ mô
---

# Vĩ mô

| Nguồn (file) | Status |
|---|---|
| [`breadth_data.md`](breadth_data.md) — data/breadth_data.csv | DEAD |
| [`cpi_vn.md`](cpi_vn.md) — cpi_vn.py (NSO_CPI_YOY_REAL + CPI_ANCHORS) | CANONICAL-PROXY |
| [`deposit_rate_vn.md`](deposit_rate_vn.md) — deposit_rate_vn.py (DEPOSIT_EVENTS + data/deposit_rate_vn_events.csv append-only) | CANONICAL-PROXY |
| [`fiinprox_cpi_monthly.md`](fiinprox_cpi_monthly.md) — data/fiinprox_cpi_monthly_20260914.csv (CPI headline/lõi/vàng/USD tháng 2008-01→2026-08; FiinPro-X trial) | **DERIVED** headline+lõi (khớp NSO 13/13); nội suy T2 cpi_vn.py lệch tới 2,5pp |
| [`fiinprox_gdp_nominal_quarterly.md`](fiinprox_gdp_nominal_quarterly.md) — data/fiinprox_gdp_nominal_quarterly_20260914.csv (GDP danh nghĩa quý + BĐS/xây dựng/tài chính, 2018Q1→2026Q2) | DERIVED có bẫy — gãy chuỗi 2020→2021 (đánh giá lại GDP) |
| [`fiinprox_money_credit_monthly.md`](fiinprox_money_credit_monthly.md) — data/fiinprox_money_credit_monthly_20260914.csv (M2/tín dụng/tiền gửi YoY tháng 2013→2026) | DERIVED tổng tín dụng · UNVERIFIED còn lại; tiền gửi gãy chuỗi 10/2025 |
| [`fiinprox_usd_fx_monthly.md`](fiinprox_usd_fx_monthly.md) — data/fiinprox_usd_fx_monthly_20260926.csv (USD/VND cuối tháng 2012-01→2026-09: trung tâm, VCB mua/bán, tự do, NHNN; FiinPro-X trial, snapshot một lần) | DERIVED cột VCB (khớp feed 3/3 tháng ≤20đ) · UNVERIFIED trung tâm/tự do/NHNN; `central` trước 2016 là chế độ khác |
| [`gdp_growth_vn.md`](gdp_growth_vn.md) — gdp_growth_vn.py (GDP_ANNUAL) | CANONICAL |
| [`macro_health.md`](macro_health.md) — data/macro_health.json | CANONICAL |
| [`sbv_refi_rate.md`](sbv_refi_rate.md) — SBV refi-rate (sbv_macro_overlay) | CANONICAL |
| [`us_market_history.md`](us_market_history.md) — us_market_history.csv (VIX/SPX) | CANONICAL |

↩ [Về index tổng](../index.md)
