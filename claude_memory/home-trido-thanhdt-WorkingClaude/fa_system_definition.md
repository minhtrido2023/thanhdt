---
name: FA-system definition
description: Hệ thống đánh giá cơ bản 7 trục cho cổ phiếu VN; script chính là fundamental_rating.py
type: project
originSessionId: 83f7db02-996e-45e7-8368-3e4ec45d6182
---
# FA-system — 7-Axis Fundamental Rating

**Script**: `fundamental_rating.py`  
**Output**: `fundamental_rating_all.csv` (toàn bộ lịch sử), `fundamental_rating_latest.csv` (mới nhất)

## 7 trục & trọng số

| Trục | Weight | Indicators |
|------|--------|------------|
| quality | 0.18 | ROIC5Y, ROE_Min5Y, FSCORE |
| stability | 0.18 | NP_CV, Rev_CV, LT_CAGR |
| cash | 0.18 | CF_OA_5Y, CFOA_NP |
| shareholder | 0.15 | DY_adj, Dividend_Min3Y, FCF_OA_ratio, DY_sust |
| growth | 0.13 | NP_R, Revenue_YoY_P0, GPM_change, NP_peak_ratio, Rev_peak_ratio |
| health | 0.08 | Debt_Eq_P0, IntCov_P0, CashR_P0 |
| valuation | 0.10 | PE_self_z, PB_self_z, PE_ind_z, PB_ind_z, PCF_ind_z, growth_yield |

## Tier phân loại

- **A**: total_score ≥ 0.65  
- **B**: 0.55 – 0.65  
- **C**: 0.45 – 0.55  
- **D**: 0.35 – 0.45  
- **E**: < 0.35  

## Các chỉ số đặc biệt (v4)

- **DY_adj** = DY × mult, mult = clip(1 + 2×NP_R, 0, 1) khi NP_R < 0 — giảm DY khi lợi nhuận giảm
- **DY_sust** = mult riêng lẻ trong Shareholder axis — phạt NP suy giảm kể cả stock không chia cổ tức
- **NP_peak_ratio** = NP_P0 / max(NP_P0..NP_P7) — 1.0 = đỉnh 8Q, <0.6 = suy giảm cơ cấu
- **Rev_peak_ratio** = Revenue_P0 / max(Revenue_P0..Revenue_P7) — tương tự cho doanh thu
- **growth_yield** = NP_R / PE (clip ±0.15) — growth per PE unit; âm khi NP giảm trong khi PE cao

## Kết quả đã xác nhận

- Tier ordering Q4 history: A > B > C > D > E ✓
- VCS 2022Q4 false upgrade (DY=11.8%, NP_R=-55.8%) ngăn chặn thành công ✓
- MAX_RATING_AGE = 400 ngày (dùng trong live_picks_2026.py)

## Quan hệ với các hệ thống khác

- **live_picks_2026.py**: dùng FA-system scores + tech multiplier (MA200/MA50/MACD/CMB) → top 10 picks
- **rank_profile_hits.py**: đánh giá workflow — FA-system không cải thiện alpha phổ quát cho technical deals; D-tier là mean-reversion plays; UnderBV+A/B mạnh nhất (WR 80.2%)
- **VNINDEX 5-state**: H-system/F-system/P-system dùng market timing; FA-system dùng stock selection
