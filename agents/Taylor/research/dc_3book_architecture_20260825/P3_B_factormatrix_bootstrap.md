# Giai đoạn 3, Phần B — Validate ma trận factor×regime (bootstrap CI + OOS stability)

Job `Taylor_20260825_153800`. Script: `exp_dc3book_bootstrap_20260825.py`.
Output: `exp_dc3book_bootstrap_ci.csv`, `exp_dc3book_oos_stability.csv`.

Nguồn dữ liệu: `exp_dc3book_c1_stateswap_univpit.csv` (Phần A cùng job) — r_bal/r_lag/r_dc/state
theo ngày, cùng cửa sổ 2014-08-05→2026-06-19. "gross" reverse-engineer khớp CHÍNH XÁC bảng phase 2
(`C_creative_alternatives.md`): **arithmetic annualization = mean(daily return trong state) × 252**
(không phải compound geometric) — verify khớp N và số liệu tới 2 chữ số thập phân cho cả 5 state.

## 2a. Bootstrap CI (N=1000, paired theo day-index, 5th-95th pct)

Paired = mỗi lần resample lấy CÙNG bộ ngày cho cả 3 factor (giữ đúng tương quan ngày-với-ngày thật
giữa BAL/LAG/DC), không bootstrap độc lập từng factor.

| State | N | gross_BAL (CI) | gross_LAG (CI) | gross_DC (CI) | Diff CI chứa 0? |
|---|---:|---|---|---|---|
| CRISIS | 443 | 1.94% [-6.8,10.4] | 10.33% [-12.5,31.0] | 14.94% [-13.9,44.5] | CẢ 3 cặp chứa 0 |
| BEAR | 241 | 1.55% [-8.5,12.0] | 1.12% [-16.1,18.3] | -7.58% [-44.6,29.1] | CẢ 3 cặp chứa 0 |
| NEUTRAL | 1799 | 32.11% [22.4,42.6] | 30.24% [18.9,41.5] | 19.40% [9.9,29.1] | BAL-DC **KHÔNG chứa 0** [5.8,19.8]; LAG-DC **KHÔNG chứa 0** [1.1,19.9]; BAL-LAG chứa 0 |
| BULL | 422 | 46.34% [12.6,77.7] | 34.54% [19.1,50.8] | 43.64% [22.0,64.7] | CẢ 3 cặp chứa 0 |
| EXBULL | 60 | 60.47% [-48.6,169.2] | 69.53% [18.0,125.4] | 47.85% [-55.5,147.0] | CẢ 3 cặp chứa 0 |

**Chỉ 1 kết luận đạt ý nghĩa thống kê 90% ở tầng bootstrap pooled: DC THUA CẢ BAL LẪN LAG ở
NEUTRAL** (cả 2 diff CI đều dương hoàn toàn, không chứa 0). Mọi kết luận "leadership" khác ở tầng
bootstrap pooled-sample đều KHÔNG đạt ngưỡng — kể cả BULL (DC 43.6% vs LAG 34.5%, cách biệt trông
lớn nhưng CI overlap hoàn toàn: diff LAG-DC = [-30.6pp, +13.3pp]).

## 2b. OOS stability (3 giai đoạn: pre-2017 / 2017-2020 / 2020-nay)

| State | pre-2017 leader (N) | 2017-2020 leader (N) | 2020-nay leader (N) | Nhất quán? |
|---|---|---|---|---|
| CRISIS | DC (88) | DC (58) | DC (297) | **NHẤT QUÁN cả 3 giai đoạn** |
| BEAR | BAL (21) | BAL (26) | LAG (194) | MIXED |
| NEUTRAL | LAG (495) | BAL (596) | BAL (708) | MIXED (DC không thắng ở BẤT KỲ giai đoạn nào) |
| BULL | N/A (0) | **BAL** (70) | **DC** (352) | MIXED — đảo ngược hoàn toàn giữa 2 giai đoạn có dữ liệu |
| EXBULL | N/A (0) | N/A (0) | LAG (60) | chỉ có 1 giai đoạn có dữ liệu, "nhất quán" là tầm thường |

**Phát hiện quan trọng nhất — BULL leadership KHÔNG ổn định qua thời gian**: giai đoạn 2017-2020
(N=70), BAL dẫn áp đảo (50.32%), LAG (6.09%) và **DC ÂM (-2.92%)** đều yếu. Giai đoạn 2020-nay
(N=352, chiếm 83% tổng N BULL), DC vượt lên (52.90%) và LAG cải thiện (40.20%). Kết luận "DC thắng
LAG trong BULL" mà Phần A/phase-2 Phần C dựa vào **là hiện tượng của riêng giai đoạn 2020+**, không
phải pattern ổn định đa thời kỳ — khớp trực tiếp với phát hiện của Phần A (C1 backtest: IS 2014-19
THUA baseline, toàn bộ lợi ích net dương tập trung OOS 2020+).

## 2c. Kết luận — state nào đủ tin, state nào chưa

**Đủ tin để dùng trong thiết kế state-adaptive** (2 nguồn bằng chứng độc lập đồng thuận):
- **CRISIS: DC dẫn đầu, ĐÁNG TIN dù bootstrap CI rộng.** Lý do: bootstrap CI rộng vì variance
  NGÀY cao (thị trường khủng hoảng biến động mạnh), nhưng leadership NHẤT QUÁN qua cả 3 giai đoạn
  lịch sử độc lập (pre-2017/2017-20/2020-nay) — đây là dạng bằng chứng KHÁC (robustness đa thời kỳ)
  bổ sung cho ý nghĩa thống kê pooled-sample, không thay thế nó. Khuyến nghị: tin vào HƯỚNG (DC>LAG
  >BAL trong CRISIS), thận trọng với ĐỘ LỚN (magnitude còn bất định, CI [-13.9%,+44.5%] quá rộng để
  chốt một con số cụ thể).
- **NEUTRAL: DC thua CẢ BAL LẪN LAG, ĐÁNG TIN** — CI thống kê rõ ràng (90% pooled) VÀ nhất quán
  chiều hướng ở cả 3 giai đoạn (DC không thắng ở bất kỳ đâu). Đây là kết luận PHỦ ĐỊNH chắc chắn
  nhất trong toàn bộ ma trận: đừng đặt DC vào NEUTRAL.

**CHƯA đủ tin, cần thêm dữ liệu/thời gian trước khi thiết kế trọng số dựa vào**:
- **BULL: DC vs LAG KHÔNG đáng tin** — CI overlap hoàn toàn + đảo ngược giữa 2 giai đoạn có dữ
  liệu. Đây là phát hiện quan trọng nhất Phần B: nó giải thích TRỰC TIẾP vì sao Phần A's C1 backtest
  chỉ có lợi ích net dương ở OOS (2020+) mà IS (2014-19, chứa cả giai đoạn 2017-2020 BAL-dẫn-đầu)
  lại thua baseline — không phải nhiễu ngẫu nhiên của backtest, mà là chính bản chất thống kê của
  factor leadership trong BULL chưa ổn định.
- **BEAR: mixed, không đáng tin** — cả bootstrap lẫn OOS đều không nhất quán; DC âm ở 2/3 giai
  đoạn (đã biết từ trước, DC KHÔNG NÊN chạy ở BEAR bất kể thiết kế nào).
- **EXBULL: N=60, không đủ dữ liệu để kết luận** — chỉ có 1 giai đoạn lịch sử (2020-nay) có đủ N,
  "LAG dẫn EXBULL" không qua kiểm định chéo được vì không có giai đoạn thứ 2 để so sánh; bootstrap
  CI của LAG dù dương hoàn toàn [18.0%,125.4%] nhưng overlap với DC's CI rất rộng — **"LAG dẫn
  EXBULL" là kết luận YẾU, không nên dùng làm cơ sở thiết kế**.

**Hàm ý cho hướng C3 (state-adaptive factor rotation, phase-2 khuyến nghị #2)**: chỉ 2/5 state
(CRISIS, NEUTRAL) đủ tin cậy để hard-code trọng số factor theo state ngay bây giờ; BULL/BEAR/EXBULL
cần thêm dữ liệu lịch sử (chờ thêm chu kỳ) hoặc một cơ chế thích ứng mềm hơn (không hard-switch) —
thiết kế allocator dựa trên ma trận điểm-ước-lượng đơn (như C3.1 phác thảo ở phase 2) sẽ OVERFIT
vào chính giai đoạn 2020+ nếu áp dụng nguyên trạng cho BULL/EXBULL.
