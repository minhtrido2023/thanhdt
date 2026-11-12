# GĐ1 vòng 2 — áp required_change của quant-skeptic (REFUTED 12/11/2026 18:2x ICT)
Đọc: agents/Taylor/research/live_gap_phase1_20261112/REPORT.md (GĐ1 gốc) và verdict quant-skeptic trên bus topic "live-gap-phase1-20261112" (nếu cần chi tiết: các defect 1-7 ghi dưới). Mọi thứ vẫn trong nhánh/worktree cô lập, KHÔNG merge/đổi production/cron/data canonical. Ghi vào agents/Taylor/research/live_gap_phase1b_20261112/ (ledger tên _exp_gap_*). Làm MỘT lượt hết các mục, liệt kê trọn bộ kết quả.

Các defect đã xác nhận (đừng tranh luận lại, hãy sửa):
D1 Chân C1fix/D1fix chạy với wd=/home/trido/thanhdt/WorkingClaude (canonical) nên vá mergesort KHÔNG được import (engine tự in cảnh báo no-op). Kết luận "patch inert/hypothesis refuted" vô hiệu.
D2 "Gap không ở W1–W2a" chỉ đúng cold-start; warm: W1warm−W0warm = −4,28pp.
D3 Câu "live phơi nhiễm thấp hơn engine" SAI: live cổ phiếu/NAV (nav_history_SpaceX.csv mtm_stock/nav) T7 87%, T8 89%, T9 87%, T10 32%, T11 15% vs engine W1 cold 39/100/100/54/5; Trứng vàng chỉ 79% ở tháng 11, trung bình cửa sổ ~0,3. T7 gap chủ yếu là thời điểm phơi nhiễm (VNI T7 −6,68%).
D4 ZaloPay chưa tính warm (cơ sở 07-06: +3,103% / −1,004%) → khoảng gap ZaloPay bot 1,6–5,7pp.
D5 Dải warm trộn 3 trục (quy ước khởi động, quy mô NAV 575B/13B, file LAG); kiểm "LAG adj INERT" mới làm ở cửa sổ cold.
D6 Control "3 bộ code" thực chất 2 (C1fix=C0). Worktree pin-era wt-livegap-pincode-1112 đã bị xoá.
D7 Hurdle dùng lẫn phẳng 2,696 và PIT 2,548.

Việc (theo thứ tự):
1. D1: chạy lại C1fix & D1fix với PT_WORKDIR (hoặc đường tương đương) trỏ vào worktree/sandbox có vá để vá THẬT SỰ được import (kiểm bằng dòng WORKDIR trong log, không còn cảnh báo VO NGHIA); chạy determinism_check AUDIT_END 06-19 vs 07-29. Nếu VẪN lệch (đầu tiên 2018-07-06 CAPITB_E5/GAS): bisect tới nguyên nhân gốc và nêu rõ có phải look-ahead (chuẩn hoá toàn mẫu, dữ liệu sau ngày vào) hay không — đây là câu hỏi quan trọng nhất vì chạm engine pin. Nếu lệch được chữa bởi vá: báo số pin cũ có đổi không.
2. Warm leg ở quy mô live: NAV_TOTAL_B ≈ 0,0757 sao cho NAV(30/06) ≈ 1B (SpaceX) và tương tự cho ZaloPay (cơ sở 07-06); báo W0/W1 warm đúng quy mô. Đọc NAV 30/06 ghi rõ. Chạy W0warm trên sandbox_ctrl (LAG canonical) vs sandbox_adj để kiểm D5 toàn lịch sử.
3. Phân rã phơi nhiễm theo tháng: bảng live vs engine (cold, warm-live-scale) — %cổ phiếu/NAV, VNI tháng, lợi suất tháng; tách gap thành (i) phơi nhiễm×thị trường (beta) và (ii) chọn mã/thực thi (alpha-dư) dạng số học, thay câu cash drag. Làm cho cả SpaceX và ZaloPay bot.
4. Control: hoán TỪNG file data pin-era vào chạy control (earnings_surprise_data.pkl, earnings_events_classified.csv, lag_edge_health.csv, ... tìm backup/snapshot pin-era trong data_registry/bq_pin_snapshots) để xác định file gây lệch 4707bcbe→d7091b4b; kiểm xem hàng trước 06-19 có bị restate không (point-in-time). Nếu không tìm được backup pin-era, nói thẳng.
5. D7: bảng cuối dùng MỘT hurdle PIT (GĐ0 hurdle_pit.csv, 2,548% cho 01/07→11/11; ZaloPay 06/07→11/11 2,455%).
6. Báo cáo REPORT.md vòng 2 + cập nhật waterfall.csv/png (tách rõ cold / warm-live-scale), nêu khoảng gap đã sửa (SpaceX, ZaloPay bot) và bậc nào VẪN chưa đo (W2b knob, W3 lệnh tay, W4 fill thật, W5 egg — KHÔNG làm trong lượt này). Ghi bus finding "live-gap-phase1b-20261112", cập nhật kb/memory/Taylor.md.
Nguyên tắc: không kết luận quá phạm vi đo; N = một cửa sổ 4 tháng; khai số lần chạy.
