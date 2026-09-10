# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## AMH (Adaptive Market Hypothesis) — ĐÓNG HẲN 2026-09-10
File tổng: `kb/projects/amh-adaptivity-review-20260910.md` (mục 10 = INPUT dùng thẳng cho review VPI/BAL 09-16).
KHÔNG WIRE GÌ (BAL edge-gate NO-GO, change-point NO-GO, t_eff REFUTED, efficiency gauge = chu kỳ không phải cấu trúc).
Phụ phẩm đã đóng: A/B exit-keyed (Taylor_20260910_142406) — lỗi khóa-entry vô hướng, LIVE không đổi;
Mike tự sửa `data/results_registry.md` (+0,60pp → đúng +0,29pp, commit `a76b00d7`), bus question đã đóng 09-10.

## Retro 2026-09-10 — ĐÃ GHI, verify CONFIRMED (Wags)
`kb/incidents/retro/retro-2026-09-10.md`. Pattern A: escalation NAV PRICE_XCHECK gate (4 ngày liên tiếp,
4 nguyên nhân gốc khác nhau) ĐÃ ĐÓNG bằng fix kiến trúc thật (commit `c30e0580`, verify bằng NAV CSV thật).
Pattern B: 2 near-miss "cơ chế mới lộ kẽ hở lần soi đầu tiên" — rollup_of circular-closure đã có gate cơ học
(`close_bus_question.py --ack-rollup-auto-closes`, commit `9aece3af`); +0,60pp đã đóng vòng bus hôm nay.
Đề xuất còn treo (chưa làm, không khẩn): thêm câu cụ thể vào coding_guidelines §9/§18 — "trích số liệu cũ
từ hội thoại/KB phải grep lại results_registry.md xem có mục ## + CSV/md5 hay không".

## Bus question đang mở, CHỜ USER
1. `Mike/bq-cache-manifest-not-updated-by-selfheal-2026-09-09` — self-heal quên rewrite manifest.json. Chưa sửa.
2. `Wags/wags-fix-not-confirmed: coord-2026-09-07` — doc drift cron vn_realestate_monthly_check.sh.
3. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C.

## R&D đã ĐÓNG HẲN (đừng mở lại nếu không có dữ liệu ngoài mẫu mới)
- AMH 7 hướng (09-10) · CCS/8L accruals (09-06, NO-GO lần 3) · BAL/custom30V 5 vòng (09-09, tất cả NO-GO).
- custom30V: user chốt overweight bank là TÁC DỤNG PHỤ của pool thanh khoản; cắt 16pp bank tốn ~0 CAGR
  nhưng LUÔN trả bằng ADV.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm → §-mới tiếp theo phải tách sang _ext.md.

