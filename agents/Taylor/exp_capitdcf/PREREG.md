# PRE-REGISTRATION — DCF MoS as PRIMARY rank for CAPIT basket (job Taylor_20260720_155015)
Written BEFORE running any test. Per multiple-testing discipline (chuẩn 2026-07-05).

## Câu hỏi
Thay pb_z bằng DCF margin-of-safety làm metric xếp hạng CỐT LÕI chọn rổ CAPIT.
(Khác job trước: lần trước DCF là filter/tiebreaker PHỤ, pb_z vẫn là rank chính.)

## Quan sát cấu trúc đã biết TRƯỚC khi test (không phải kết quả test)
- Universe sau quality+liquidity gate (ROE_Min5Y>=0.12, ROIC5Y>=0.10, FSCORE>=6, ADV>=2B):
  **median 7 tên/ngày, max 25** (3127 phiên 2014-2026).
- Rổ production sau cascade pb_z tại 14 washout event: **3-7 tên**, K=5.
  → ở 8/14 event pool <= K: rank metric KHÔNG chọn gì cả (lấy hết).
- Hệ quả: bất kỳ metric rank nào cũng chỉ đổi được rổ trong không gian rất hẹp.
  Sẽ ĐỊNH LƯỢNG trần tác động này (structural bound) như một kết quả độc lập với thống kê.

## Thiết kế test

### PANEL A (test chính — có power) — name-level rank IC
- Universe mỗi ngày quan sát = **toàn bộ** quality+liquidity gate (KHÔNG áp pre-filter pb_z),
  để 2 trục thi đấu trên cùng tập tên.
- Ngày quan sát: **quý, non-overlapping** với horizon chính h=60 phiên (~48 ngày, 2014-2026).
  Non-overlap = khoảng cách ngày quan sát >= h → không double-count/inflate N.
- Đo: within-date rank IC vs forward return h phiên. t-stat trên chuỗi IC theo ngày (N ngày độc lập).
- Phụ (robustness, KHÔNG dùng để quyết định): h=250 lấy mẫu **năm** (12 ngày non-overlapping);
  và bản monthly-overlapping với **cluster bootstrap theo năm** (12 block) để kiểm tra ổn định điểm ước lượng.

### PANEL B (tham khảo định hướng — KHÔNG đủ power, đã xác nhận job trước)
- 14 washout event, DCF-as-primary-rank vs production baseline, K=5, equal-weight.
- Nêu rõ N=14 không đủ power; không dùng làm căn cứ quyết định chính.

## N_TRIALS PRE-REGISTERED = 3 trục xếp hạng
1. **DCF**: rank MoS giảm dần (MoS cao = rẻ vs giá trị nội tại)
2. **PBZ**: rank pb_z tăng dần (baseline production)
3. **COMBO**: trung bình 2 rank chuẩn hoá (50/50)

Horizon chính duy nhất = **h=60**. h=250 và bản monthly là ROBUSTNESS, không phải trial mới.

## Xử lý DCF N/A (FCFE âm) — chốt trước, theo bằng chứng job trước
N/A = **rank TRUNG TÍNH** (median rank trong ngày). Job trước đã đo: nhóm N/A có return demeaned
+0.96pp ≈ nhóm CHEAP +0.93pp → loại N/A là loại nhầm. Sensitivity: bản chỉ tính IC trên tên
computable (loại N/A khỏi phép đo, không phải khỏi rổ).

## Tiêu chí GO / NO-GO (định trước, không sửa sau khi thấy số)
**GO** cần ĐỦ CẢ 4:
- (i) IC(DCF) > 0 với **t >= 2.0** trên panel A chính (h=60, quarterly non-overlap)
- (ii) Hiệu **paired** IC(DCF) − IC(PBZ) > 0 với **t >= 2.0** (ghép cặp theo ngày quan sát)
- (iii) LOO theo NĂM: bỏ bất kỳ 1 năm nào, hiệu paired vẫn dương
- (iv) IS (2014-2019) và OOS (2020+) **cùng dấu** cho hiệu paired

**NO-GO** nếu (i) hoặc (ii) trượt.
**INCONCLUSIVE** nếu đúng dấu nhưng 1.0 <= t < 2.0 và LOO ổn định.

## DSR
Chỉ báo DSR **nếu** (i)+(ii)+(iii) đạt. Nếu edge lại do 1 quan sát chi phối / LOO sụp → **không báo**,
nói rõ lý do (như job trước), không báo con số trang trí.

## Ràng buộc
- Point-in-time: DCF chỉ đọc `ticker_financial.time <= asof` (= Release_Date). Không look-ahead.
- threads=1, stable-sort tie-break `(metric, ticker)` theo chuẩn determinism 2026-07-13.
- R&D thuần: KHÔNG sửa `capit_basket()` production, không chạm plan/executor.
