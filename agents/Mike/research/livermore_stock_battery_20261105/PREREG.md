# Livermore — bài thử cổ phiếu ẩn danh (soạn 05/11/2026, TRƯỚC khi chạy)
Mục đích: đo năng lực đọc kỹ thuật theo MÃ (vai mới: giữ cửa quyết bán FPT/NNC) với N lớn hơn thử mù 22/10 (N=16).
- N=100 case (ticker, as-of) chọn ngẫu nhiên (seed 20261105) từ `universe_pit` in_universe, as-of 2012-01-01..2025-09-30, tối đa 2 case/mã, cách nhau ≥40 phiên cùng mã.
- Input mỗi case: 250 phiên OHLC (÷ close đầu cửa sổ ×100) + volume (÷ median cửa sổ). KHÔNG mã, KHÔNG ngày, KHÔNG thị trường chung.
- Output mỗi case: H20_DIR (UP/DOWN so close +20 phiên với close as-of), H20_P_UP (0-1), ACTION_IF_UP10 (SELL_NOW/HOLD — giả sử đang lãi +10%), INVALIDATION.
- Chấm (script, sau khi khoá): hit H20_DIR; Brier(H20_P_UP); so với B0 đồng xu 0,5; B1 "luôn UP"; B2 động lượng (sign close/close[-20]); B3 động lượng 60 phiên.
- ACTION_IF_UP10 chấm: SELL_NOW đúng nếu fwd20<0, HOLD đúng nếu fwd20>0 (cùng thước hit).
- Tiêu chí SỐNG: Brier<0,25 VÀ hit > max(B1,B2,B3) nghiêm ngặt VÀ P(X>=hit | p=base rate) <0,10. Không đạt ⇒ KHÔNG dùng làm cửa quyết bán duy nhất (đề xuất user).
- Chỉ 1 lượt, 5 agent × 20 case, không chạy lại/chọn lại. Agent chỉ được đọc đúng file case của mình; tự báo nếu nhận ra mã/giai đoạn (cờ RECOGNIZED).
- Giới hạn: mô hình có thể nhận ra chuỗi từ trí nhớ (cờ RECOGNIZED để tách); case độc lập theo mã/thời điểm nhưng chung chế độ thị trường (cụm theo thời gian) ⇒ N hiệu dụng < 100.
