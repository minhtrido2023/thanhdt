# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## CCS/8L accruals R&D — ĐÓNG HẲN 2026-09-06
Phase 0→0b→R3→Phase2-NARROW, tất cả NO-GO (lần NO-GO thứ 3 cho ý tưởng accrual-gate).
Phase 2-NARROW trim-bottom chết ở DSR (P=0.0012<0.95). Không thử thêm biến thể ở vị trí này —
mở lại chỉ khi có dữ liệu ngoài mẫu 2014-2026 + câu hỏi tiền-đăng-ký riêng.

## Retro 2026-09-06 — XONG (job Mike_20260906_173637)
File `kb/incidents/retro/retro-2026-09-06.md` (commit 85bc60b8), Wags GAPS FOUND (minor, đã sửa
decision count 2→4). 2 sự cố MỚI, cả 2 fix+verify hoàn chỉnh cùng ngày: compute_active_nav.py
NameError `_dt_stale` (59b268d2), spend_report_weekly.py effort-drift cảnh báo sai cho Taylor
(5f92402d). 0 pattern tái diễn — §29 bq-channel KHÔNG xuất hiện lại hôm nay (vẫn dừng ở 5 lần,
đề xuất RULE 2 cho diagnosis_evidence_gate.py chưa escalate, chờ lần tái diễn thứ 6).

## Bus question đang mở (2)
1. `Wags/wags-fix-not-confirmed: coord-2026-09-03` (3d+) — Wags chưa có bằng chứng đã đính
   chính với user trên trading_daily về cơ chế ack deposit-rate. Cửa sổ: trước 2026-09-11.
2. `Mike/bq-monthly-pin-thieu-202608-202609-chay-bu-hay-khong` — chờ user quyết A/B/C.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

