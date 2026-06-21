---
name: rate-signal-ic-validation-2026
description: Validation that VN domestic rate MOMENTUM (not level) leads VNINDEX; deposit-rate not worth wiring into DT5G Pillar A now
metadata: 
  node_type: memory
  type: project
  originSessionId: 2a30a0b5-387e-420f-a6f4-e00deff68fdf
---

Validate [REDACTED]03 (triggered by tienphong.vn bài lãi suất tiết kiệm tăng): DT5G macro Pillar A "DOMESTIC MONEY" đo **SBV refi rate (policy)**, KHÔNG phải lãi suất tiết kiệm thương mại — hai cái phân kỳ được (NH đẩy deposit rate mà SBV chưa đổi policy). Live: refi=4.5% đứng yên từ 2023-06-19 (1079d), cap=9/easing=false → Pillar A ngủ đông, cú deposit-rate tăng trong bài KHÔNG được đo.

IC test (`test_rates_regime_signal.py`, lending_rate macro_daily.csv 2000-2023 annual+ffill, lag 21d, BQ vnindex_5state_dt_4gate):
- **Momentum là carrier, không phải level**: `rate_chg6m` IC −0.110/−0.150/−0.159 (fwd20/60/120, âm=tăng→giảm); level/rank chỉ −0.05..−0.10; real_rate ~0.
- Conditional fwd120 đơn điệu sạch: rates RISING fast −3.81% / flat +10.48% / FALLING +6.48% (chênh ~7-14pp).
- **KHÔNG lead CRISIS** (4/18 onsets có rates rising) → headwind mềm / sizing, không phải trigger lật state. Khớp [[dt5g_walkforward_event_audit]]: macro = gate phòng thủ không phải alpha, edge dồn vào đợt thắt chặt.
- Recovery: sau rate đỉnh + giảm → fwd120 +17.1% vs +8.6% → validate nhánh easing.

**Why không wire deposit-rate vào Pillar A bây giờ**: (1) feature đúng (`refi_chg6m`) đã đang dùng + validate, không cần sửa thiết kế; (2) cú deposit nhích 0.3-0.8pp quá nhỏ so ngưỡng Pillar A (mild +0.5/strong +1.5/extreme +3.0 pp/6m) → đúng ra nên bỏ qua, và đang bỏ qua đúng; (3) thiếu chuỗi deposit-rate theo tháng 2023→now live. Caveat data: annual granularity + ends 2023 + overlap phóng đại IC, edge thật nhưng dồn vào 2008/2011/2022.

**How to apply**: khi user hỏi lãi suất ảnh hưởng thị trường qua DT5G → momentum mới quan trọng (không phải mức); chỉ defensive khi đà ≥+1.5pp/6m; nhích nhẹ = noise. Nếu muốn nhạy hơn: dựng deposit-rate monthly series rồi áp đúng ngưỡng Pillar A hiện có (đừng thêm pillar mới). Related: [[feedback_us_vn_correlation_interpretation]].
