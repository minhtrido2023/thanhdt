# PRE-REGISTRATION — CƠ CHẾ THOÁT của CAPIT (job Taylor_20260720_164006)
Viết TRƯỚC khi chạy bất kỳ test nào có dính forward-return. Chuẩn multiple-testing 2026-07-05.

## 0. ĐÍNH CHÍNH TIỀN ĐỀ DISPATCH (xác minh trong code, trước khi thiết kế)
Dispatch nói "K=5 slot". **SAI.** Production (cả `pt_v23_audit_2014.py::capit_basket` lẫn
`deploy_golive_dt5g_v4/golive_recommend_v23.py`) cap rổ ở **15 tên**:
```
pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick     # cả 2 file
tier_position_limit = {t: 15 for t in tiers}                      # add_capit_arm
```
Size mỗi tên = `capit_size / len(basket)` — equal-weight trên **kích thước rổ THỰC TẾ**, không
phải chia cho hằng số 5. Vì pool median ~7 tên (job `Taylor_20260720_160852`), trần 15 gần như
**không bao giờ ràng buộc** → "chọn K" hiện KHÔNG phải một tham số sống. Trục 2 được thiết kế lại
theo thực tế này (xem §3).

## 1. Câu hỏi (trục 1 — trọng tâm)
CAPIT hold **60 phiên cố định, stop-exempt, slot-exempt** — không có cơ chế thoát sớm nào.
Thêm một cơ chế thoát sớm có cải thiện risk-adjusted return của sleeve không?

## 2. N_TRIALS PRE-REGISTERED = 6 biến thể thoát (+ baseline E0)
| id | họ | quy tắc thoát sớm (mọi biến kiểm tra causal, dữ liệu tại T, thoát tại T+1 Open) |
|---|---|---|
| **E0** | baseline | giữ đủ 60 phiên, không thoát |
| E1 | (a) mean-reversion | pb_z hồi lên **≥ −0,5** → thoát |
| E2 | (a) mean-reversion | pb_z hồi lên **≥ 0,0** → thoát |
| E3 | (b) chất lượng | vỡ **bất kỳ** cổng gốc (ROE_Min5Y<0,12 ∨ ROIC5Y<0,10 ∨ FSCORE<6) → thoát |
| E4 | (b) chất lượng | vỡ **nặng** (ROE_Min5Y<0 ∨ FSCORE<4) → thoát |
| E5 | (c) time-decay | sau 30 phiên, nếu return vị thế < 0 → cắt **50%** size |
| E6 | (c) time-decay | sau 30 phiên, nếu pb_z chưa cải thiện so với lúc vào → cắt **50%** size |

Horizon quyết định duy nhất = **cửa sổ 60 phiên** (đúng holding period). Không thêm horizon nào
làm trial mới.

## 3. Thiết kế đo
### Panel A — position-level (test chính, có power)
14 washout event × rổ thực tế → ~100+ position-event. Với mỗi vị thế và mỗi biến thể:
- đường giá ngày 0..60, đường pb_z ngày, đường ROE_Min5Y/ROIC5Y/FSCORE ngày (PIT sẵn trong `ticker_prune`).
- Vào lệnh = **Open T+1** (đúng convention audit), thoát = **Open T+1 sau ngày tín hiệu**.
- **Vốn thoát sớm nằm im (0%/ngày) tới hết cửa sổ 60 phiên** — đo bảo thủ, không giả định tái đầu tư.
  Bản phụ (robustness): vốn thoát ăn return VNINDEX phần còn lại (proxy tái đầu tư vào parking).
- Suy diễn: paired t trên (biến thể − E0) theo từng vị thế, **cluster theo event** (14 cụm).

### Panel B — portfolio-level (14 event, N mỏng, định hướng)
Sleeve-return mỗi event = trung bình equal-weight các vị thế; so E0 vs Ek. Báo mean/median/
5th-pct/worst-event. **N=14 KHÔNG đủ power** — dùng để kiểm tra tính nhất quán, không để kết luận.

## 4. TIÊU CHÍ GO / NO-GO (định trước)
Một biến thể Ek là **GO-candidate (paper-first)** cần ĐỦ CẢ 5:
- (i) **Cải thiện thật**: mean sleeve-return 14 event tăng ≥ **+1,0pp** VÀ median cũng tăng.
- (ii) **Không xấu đuôi trái**: worst-event và 5th-pct vị thế không tệ hơn E0.
- (iii) **Có ý nghĩa thống kê sau hiệu chỉnh đa kiểm định**: paired t (cluster theo event) trên
  Panel A có **t > 2,6** (≈ Bonferroni p<0,05/6). t ∈ (2,0; 2,6] → INCONCLUSIVE, không phải GO.
- (iv) **LOO theo event**: bỏ bất kỳ 1 trong 14 event không đảo dấu cải thiện ở (i).
- (v) **IS/OOS cùng dấu**: event ≤2019 (N=4) và ≥2020 (N=10) cùng dấu ở (i).

**NO-GO** nếu trượt (i) hoặc (ii) hoặc (iv). **INCONCLUSIVE** nếu qua (i)(ii)(iv)(v) nhưng t≤2,6.

## 5. DSR
Điều kiện tiên quyết = có chuỗi NAV daily của config sắp deploy (chạy full `pt_v23_audit_2014.py`).
Chỉ báo DSR **nếu** có ≥1 biến thể qua (i)-(v); nếu tất cả NO-GO thì **không báo DSR** và nói rõ
lý do (không có config nào để deploy — giống 3 job trước).

## 6. Trục 2 & 3 (không thuộc chuẩn multiple-testing này)
- **Trục 2 (sizing/timing)**: sau đính chính §0, câu hỏi K gần như vô nghĩa. Đo lại: rổ thực tế
  mỗi event bao nhiêu tên, trần 15 có bao giờ ràng buộc không; và depth-weight (weight ∝ độ sâu
  pb_z) vs equal-weight — 1 phép so sánh mô tả, KHÔNG phải trial production.
- **Trục 3 (thanh khoản)**: risk-engineering, đề xuất công thức cap %ADV + sensitivity, không
  backtest nặng, không đòi GO/NO-GO thống kê.

## 7. Ranh giới
R&D thuần. KHÔNG sửa `capit_basket()`/sizing production, KHÔNG chạm plan/executor.
