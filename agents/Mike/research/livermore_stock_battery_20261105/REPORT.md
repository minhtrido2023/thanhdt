# Livermore — thử 100 chuỗi cổ phiếu ẩn danh (05/11/2026)
PREREG md5: xem PREREG.md5 (soạn TRƯỚC khi chạy). 1 lượt, 5 agent × 20 case.
Kết quả: hit 55/100, Brier 0,2507, base rate tăng 47%, baseline tốt nhất 50/100 (mom20). P(≥55|p=0,5)=0,184; P(≥55|p=base)=0,067.
Theo tiêu chí PREREG (Brier<0,25 ∧ hit>max baseline ∧ p<0,10): KHÔNG ĐẠT, trượt ở Brier 0,0007.
Đọc đúng: hơn baseline 5 điểm hit nhưng với N hiệu dụng <100 (case cụm theo thời gian: 2021 chỉ 2/11) chưa phân biệt được với đồng xu. Nghiêng DOWN (60/100 call), 0 RECOGNIZED. ACTION_IF_UP10 chỉ lặp hướng H20 ⇒ không phải phép thử riêng.
Hệ quả vận hành: KHÔNG có bằng chứng Livermore đủ năng lực làm cửa quyết bán duy nhất; bằng chứng cũng không loại nó. Chạy sống FPT/NNC (LVR-STK-*) cho tới 2026-12-10 để chấm.
