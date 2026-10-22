# PREREG — Phân loại phản ứng giá quanh công bố cho candidate LAG (job Taylor_20261022_053319)

Ghi TRƯỚC khi tính bất kỳ đặc trưng/số kết quả nào. READ-ONLY: không sửa production, không pin registry.
User duyệt bước 1-2 lúc 12:32 ICT 22/10/2026. Định nghĩa dưới đây KHÔNG đổi sau khi thấy kết quả;
mọi lệch sẽ ghi ở mục "Deviations" của REPORT.

## 1. Tập sự kiện (tái dùng, không phát minh lại)
- Đúng 5.361 dòng `research/lag_entry_window_width_20261021/exp_window_events.csv` (= luật engine LAG:
  NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5, forensic ON; entry chuẩn e = Release+5 phiên; entry ≥ 2014-01-02).
- Thoát đúng luật hiện hành: Close tại e+25 phiên (neo lịch chuẩn, `exA0`).
- Hạn chế đã biết (giữ để so được với nghiên cứu 10-21): tập không áp universe_pit/ADV. Độ nhạy (KHÔNG phải
  trial): lọc `tav2_mike.universe_pit.in_universe` tại phiên e−1.

## 2. Biến kết quả
- **CHÍNH**: Y = Close_adj[e+25] / Open_adj[e] − 1 (= `exA0/buyO0 − 1`, khớp Open phiên chuẩn như engine).
- Phụ (độ nhạy, không phải trial): (i) Y_ex = Y − (VNI[e+25]/VNI_open-proxy… dùng VNI Close[e−1]→Close[e+25]);
  (ii) Y_live = cấu hình live W3·LuậtA·ANCH cơ sở Open (hàm `event_ret_open` của harness 10-21, không khớp ⇒ 0).

## 3. Đặc trưng (tối đa 4 họ; tất cả đo tại CLOSE phiên e−1 ⇒ PIT, mua ở Open e)
Giá: `tav2_bq.ticker` Open/High/Close đã điều chỉnh (lợi suất), Volume; VNINDEX = hàng `ticker='VNINDEX'`
gốc (KHÔNG dùng cột mirror `t.VNINDEX` — TRAP). Không dùng cột `profit_*`. d0 = phiên đầu tiên ≥ Release_Date.
- **(a) REACT** = (C[e−1]/C[d0−1] − 1) − (VNI[e−1]/VNI[d0−1] − 1).
- **(b1) GAP** = O[d0]/C[d0−1] − 1.  **(b2) AVOL** = V[d0] / mean(V[d0−20..d0−1]).
- **(c) PRERUN** = (C[d0−1]/C[d0−21] − 1) − (VNI[d0−1]/VNI[d0−21] − 1).
- **(d) DIST52** = C[e−1] / max(High_adj[e−250..e−1]) − 1 (chỉ đỉnh 52 tuần; "vùng cản" khác KHÔNG đo — ngoài phạm vi).
- **Lớp 3 dạng của user** (suy ra từ (a), không phải họ mới): PEAK = max_{j∈[d0,e−1]} excess tích luỹ từ d0−1.
  UP_THEN_DOWN: PEAK ≥ +5% ∧ REACT ≤ PEAK − 5pp ∧ REACT < +5%; UP_FULL: REACT ≥ +5%; DOWN: REACT ≤ −5% (không thuộc
  UP_THEN_DOWN); FLAT: còn lại. Ngưỡng 5% cố định, chốt ở đây.
- Giá thô `Price` không cần ở đây (không so giá live); nếu dịch sang live thì REACT/GAP phải tính trên chuỗi
  điều chỉnh tương đương (ghi trong REPORT).

## 4. Ngưỡng (khoá)
- Tercile của mỗi đặc trưng liên tục (REACT, GAP, AVOL, PRERUN, DIST52) cắt trên **IS (entry 2014–2019) thôi**,
  áp nguyên cho OOS (2020+). Sự kiện thiếu đặc trưng ⇒ không bao giờ bị loại (giữ lại).

## 5. Lưới bộ lọc (CHỈ dạng loại bỏ, không tilt) — N trials = 14
- 5 đặc trưng × {loại tercile THẤP, loại tercile CAO} = 10; + 4 lớp: loại UP_FULL / UP_THEN_DOWN / DOWN / FLAT = 4.

## 6. Thống kê
- N sự kiện và N độc lập = số **mùa báo cáo** (cụm = năm-quý dương lịch của Release_Date); khai cả số ngày công bố.
- Δ = mean(Y | bị loại) − mean(Y | giữ lại). Bootstrap CỤM theo mùa, 2.000 lần, seed 20261022 → CI95 + p hai phía
  (p = 2·min(P*(Δ≥0), P*(Δ≤0))). Không dùng t-test coi dòng là độc lập.
- Holm trên 14 p-value, α = 0,05.
- IS (entry 2014–2019) / OOS (2020+) riêng; bỏ-một-năm (LOYO theo năm entry): min/max Δ.
- Capacity: % sự kiện bị loại; % mùa mà bộ lọc loại >50% candidate của mùa; so mean(Y | bị loại) với lợi suất
  tiền nhàn rỗi 25 phiên ở **pin0%** (0) và **pin1M** (ước lượng ~0,4%/25 phiên từ dep1m, sẽ đo nếu cần).
- DSR: trên chuỗi Δ-theo-mùa của bộ lọc tốt nhất (Sharpe của "lợi ích giữ-lại − toàn bộ" theo mùa), N trials = 14,
  phương sai Sharpe giữa 14 trials. PBO: CSCV chia mùa theo thời gian S=10 khối (252 tổ hợp), metric = mean(Y giữ lại).

## 7. Quy tắc kết luận (chốt trước)
Một bộ lọc là **ỨNG VIÊN** nếu ĐỦ CẢ:
 1. Δ < 0 và CI95 cụm-mùa (full) có cận trên < 0;
 2. Δ_IS < 0 và Δ_OOS < 0;
 3. LOYO: max Δ < 0 (không năm nào bị bỏ ra làm đổi dấu);
 4. qua Holm (14 trials);
 5. mean(Y | bị loại) < lợi suất nhàn rỗi pin1M (nếu không, loại ra để vốn nằm im là thua);
 6. DSR ≥ 0,95 và PBO < 0,5.
- **GO** = ≥1 bộ lọc là ỨNG VIÊN ⇒ bước tiếp theo (KHÔNG làm trong job này nếu chưa có) là A/B NAV full-engine
  1 biến, self-check 0 VND, chân control tái tạo đúng số pin R3, threads=1, báo cả pin0% và pin1M.
- **INCONCLUSIVE** = có bộ lọc qua (1) nhưng trượt bất kỳ (2)–(6).
- **NO-GO** = không bộ lọc nào qua (1). Nói thẳng, không cứu bằng cấu hình mới.
- Kết quả ngược giả thuyết (vd loại UP_FULL làm XẤU đi) được báo đúng như vậy.
- Phần "đọc chart cảm tính" không lượng hoá được: ngoài phạm vi.
