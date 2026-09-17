# 2026-09-17 — FUNDING gate chặn oan ZaloPay phiên chiều: lệnh MỞ bị tính 2 lần (giữ tiền ở broker + vẫn nằm trong nhu cầu)

**Hiện tượng.** Cron 13:00 ICT `run_bot.sh --account ZaloPay` thoát rc=3: Σ mua còn lại 31.030.070đ
> pp0Buy 26.922.394đ (115,3%). Bot không chạy phiên chiều. Buổi sáng (09:05) gate OK: 31.030.070đ
≤ 33.128.408đ (93,7%).

**Bằng chứng.** Plan 1 lệnh `BUY-VPI-BAL-ZaloPay-01`. Sáng 11:00 bot đặt child oid 257461 100cp @62.000,
tới 11:29 vẫn `status=open`, `filled=0` (state.json). pp0Buy sáng − chiều = **6.206.014đ** =
100 × 62.000 × (1+0,097%) — đúng tới từng đồng tiền broker đang GIỮ cho lệnh mở.

**Root cause.** Fix 911f12bb (sự cố 2026-08-11) chỉ trừ phần ĐÃ KHỚP (`parents[*].filled`) trong
`trading_bot/plan_funding_gate.py::_remaining_quantities`; phần ĐANG MỞ (children status open) đã bị
broker trừ khỏi pp0Buy nhưng vẫn nằm trong mẫu số nhu cầu ⇒ đếm 2 lần. Nếu trừ: nhu cầu thật
≈ 24,8tr ≤ 26,9tr (92%) ⇒ lẽ ra OK.

**Xử lý.** Không tự sửa (module lõi cấp vốn/thực thi — ranh giới ops-autofix). Escalate bus
question `funding-gate-open-order-double-count` với đề xuất: cộng lại vào sức mua (hoặc trừ khỏi
nhu cầu) giá trị các child `status=open` cùng phiên của state đã kiểm. Lệnh 257461 vẫn sống ở
broker, không bot quản phiên chiều (lệnh LO mua trong plan đã duyệt — không vượt rủi ro).

**Lesson.** "Còn lại" phải = qty gốc − filled − đang giữ ở broker; mọi resume sau khi có lệnh mở
đều tái hiện lỗi này.
