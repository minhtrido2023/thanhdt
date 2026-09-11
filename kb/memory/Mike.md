# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI. Plan T+1 2026-09-14 (cả SpaceX+ZaloPay) đã HOLD_ALL đúng.

## CẦN THEO DÕI — DGC NAV ZaloPay stuck (2026-09-11, CÒN MỞ)
`Mafee/nav-price-xcheck-stuck-ZaloPay-2026-09-11` — gap 20,6% (close_price BQ 46.750 vs marketPrice
broker 38.750), quá cutoff 21:15 ICT. Trùng thời điểm DGC GDKHQ cổ tức 8.000đ/cp hiệu lực 14/09
(3 phiên sau, CHƯA qua ex-date) — KHÔNG kết luận nguyên nhân, cần Winston/Mafee verify DNSE trực
tiếp trước phiên 14/09. Nguyên nhân gốc thứ 5 (khác 4 nguyên nhân đã đóng bằng c30e0580 09-10).
Retro: `kb/incidents/retro/retro-2026-09-11.md`.

## AMH (Adaptive Market Hypothesis) — ĐÓNG HẲN 2026-09-10
`kb/projects/amh-adaptivity-review-20260910.md` (mục 10 = INPUT cho review VPI/BAL 09-16).
KHÔNG WIRE GÌ. Đóng, đừng mở lại nếu không có dữ liệu ngoài mẫu mới.

## Bus question đang mở, CHỜ USER
1. `Mike/bq-cache-manifest-not-updated-by-selfheal-2026-09-09` — self-heal quên rewrite manifest.json.
2. `Wags/wags-fix-not-confirmed: coord-2026-09-07` — doc drift cron vn_realestate_monthly_check.sh.
3. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C.
4. `Mafee/nav-price-xcheck-stuck-ZaloPay-2026-09-11` — xem mục trên.

## R&D đã ĐÓNG HẲN (đừng mở lại nếu không có dữ liệu ngoài mẫu mới)
- AMH 7 hướng (09-10) · CCS/8L accruals (09-06, NO-GO lần 3) · BAL/custom30V 5 vòng (09-09, tất cả NO-GO).
- custom30V: user chốt overweight bank là TÁC DỤNG PHỤ của pool thanh khoản; cắt 16pp bank tốn ~0 CAGR
  nhưng LUÔN trả bằng ADV.

## append_event.sh JSON isolation — pattern lâu dài đã biết, KHÔNG escalate (18+ lần từ 07-11)
0 mất dữ liệu, agent luôn tự lành <60s, sidecar `bus/_rejected_resolved.jsonl` khử báo động giả.
Căn nguyên cấu trúc (Bash ad-hoc không lint được) vẫn hở nhưng chấp nhận được — theo dõi tần suất,
chỉ đáng xem lại nếu ≥2 ca CÙNG PHÁT SINH thật trong 1 ngày liên tục vài ngày.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm → §-mới tiếp theo phải tách sang _ext.md.

