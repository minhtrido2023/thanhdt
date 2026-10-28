# PREREG — Độ rộng cửa sổ entry LAG (job Taylor_20261021_102832)

Ghi TRƯỚC khi chạy bất kỳ số nào của phần A/B/C. Read-only; không sửa production, không pin.

## A. Kiểm toán live 2026-07-01 → 2026-10-21 (SpaceX 0002023347, ZaloPay 0001743768)
- **Tập ứng viên** = mọi dòng `book=LAG` trong `deploy_golive_dt5g_v4/out/golive_v23_recommendations_*.csv`
  có ngày entry chuẩn (`WINDOW_PASSED <d>` / `UPCOMING <d>` / `UPCOMING T+n` quy về lịch phiên) trong khoảng.
  Đây là tầng TÍN HIỆU (trước mọi lọc vận hành) — nguồn cùng một file mà `filter_lag_entry_window.py` đọc.
- Với mỗi (ứng viên × account × phiên 1/2/3): plan có lệnh mua? (`orders[]`), bị hoãn (`deferred_orders[]`),
  hay chỉ nhắc trong `lag_analysis` (lý do SKIP)? Plan không tồn tại cũng là một mã.
- **Fill thật** = `dnse_raw_<d>.jsonl`, `kind=orders`, lọc `accountNo` ĐẦU TIÊN (§12), lấy `fillQuantity`
  lớn nhất theo `id`, side `NB`. Kiểm chéo bằng `data/execution_logs/dnse_khoplenh_broker_confirm_<dd-mm-yyyy>.csv`
  (email broker) ở những ngày có file. KHÔNG suy fill từ `orders[]` của plan.
- **Mã nguyên nhân** (một mã chính/ứng viên×account, gán theo thứ tự ưu tiên đọc được từ artifact):
  `FILLED_D1` / `FILLED_LATE` / `PARTIAL` / `SIG_FILTER_ADV_UNIV` (lọc ADV/universe ở tầng tín hiệu/plan) /
  `EXCLUDED_BANNED_DD` (banned/DD/rating gate/excluded) / `WAIT_CASH_DEFERRED` / `PLAN_EMPTY_BLOCKED` /
  `GHOST_PAUSE` / `PRICE_CEILING` (lệnh nằm sổ, 0 fill, giá đặt = trần) / `LIMIT_LOCK` /
  `VENDOR_LATE_RELEASE` / `NOT_IN_PLAN_UNEXPLAINED`. Ca không gán được bằng artifact ⇒ `UNEXPLAINED`, không đoán.
- N live dự kiến rất nhỏ (KB). Nếu số ứng viên × account được ĐƯA VÀO PLAN < 20 ⇒ phần B chỉ báo mô tả,
  không suy luận thống kê.

## B. Định lượng
- Tỷ lệ vốn mục tiêu LAG không triển khai/triển khai trễ = Σ(giá trị mục tiêu chưa khớp)/Σ(giá trị mục tiêu),
  mục tiêu lấy từ plan (qty×giá) nơi có; nơi không có lệnh (SKIP/deferred) dùng `deferred_orders` hoặc ghi "không đo được".
- Chi phí ước tính = (trễ k phiên × độ dốc suy giảm đo ở C) + (không khớp × lợi nhuận kỳ vọng phiên 1 đo ở C).
  Gán nhãn **ƯỚC LƯỢNG** (áp đường cong lịch sử vào ca live).
- Tách: phần "do cửa sổ" = ca có lệnh hợp lệ mà KHÔNG khớp vì hết cửa sổ/trần giá trong cửa sổ;
  phần "do vận hành" = mọi mã khác (tiền, plan rỗng, ghost, lọc, vendor).

## C. Backtest thiết kế cửa sổ (event study, KHÔNG phải NAV)
- Tập sự kiện sao y `exp_lag_entrylag_20260810/measure_entry_lag.py` (= luật engine: NP_R≥15 ∧ prior_n_good≥4 ∧
  pa_HL3≥5, forensic ON), entry chuẩn = Release+5 phiên, 2014-01-02 →. Thêm OHLC thô suy ra = OHLC_adj × Price/Close.
  Thêm cổng thanh khoản universe_pit? — KHÔNG: tập sự kiện giữ y hệt nghiên cứu 08-10 để so được; ghi rõ hạn chế.
- Lưới (khai đủ, **16 ô chính + 4 ô độ nhạy = 20 cấu hình**):
  W ∈ {1, 3, 4, 5} phiên × Trần ∈ {NONE (engine pin), RULE_A} × Thoát ∈ {ANCHORED (e+25 lịch chuẩn), SHIFTED (fill+25)}.
  Độ nhạy: RULE_A với phiên 1 KHÔNG trần (live phiên 1 không mang `entry_anchor_price`) cho W∈{1,3,4,5}, ANCHORED.
- Luật A mô phỏng: ref_k = Price thô phiên trước (XẤP XỈ: đúng HOSE/HNX ngày thường; sai UPCOM — bình quân gia quyền —
  và ngày GDKHQ). ceil_k = ref_k × 1,03. Khớp nếu Low_thô_k ≤ ceil_k; giá khớp = min(Close_thô_k, ceil_k)
  (giả định đặt lệnh và khớp quanh giá đóng/khi chạm trần). NONE: khớp ở Close_k (độ nhạy: Open_k như engine).
- Khoá trần biên độ: High_k == Low_k ∧ Price_k/ref_k − 1 ≥ 6,5% ⇒ KHÔNG khớp ở mọi biến thể (kể cả NONE).
- Khớp toàn phần hoặc không (không mô hình volume/partial). Không khớp trong W phiên ⇒ lợi nhuận 0 (tiền nằm im).
- Đại lượng: lợi nhuận trên vốn giao/sự kiện, fill%, ret|fill. Thống kê: bootstrap CỤM theo ngày công bố
  (2.000 lần, seed 20261021) cho mean và cho Δ so với baseline live **W3·RULE_A·ANCHORED**; leave-one-year-out (min/max Δ);
  IS 2014-2019 / OOS 2020+ tách riêng.
- **Quy tắc quyết định (chốt trước)**: chỉ khuyến nghị đổi độ rộng nếu Δ(W*) vs W3 có CI95 cụm không chứa 0
  ∧ cùng dấu ở cả IS và OOS ∧ LOYO không đổi dấu. Ngược lại ⇒ giữ 3 phiên.

## D. Độ trung thực engine pin
- Mô tả lệch engine (5 phiên, giá Open, 20% ADV/ngày, thoát theo ngày khớp đầu, không trần, không khoá trần) so live
  (3 phiên + Luật A + plan/vốn); dấu thiên lệch đo bằng ô NONE·W5·SHIFTED vs RULE_A·W3·ANCHORED ở C.
