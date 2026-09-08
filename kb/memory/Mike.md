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
Phase 0→0b→R3→Phase2-NARROW, tất cả NO-GO (lần thứ 3 cho ý tưởng accrual-gate). Mở lại chỉ khi có
dữ liệu ngoài mẫu 2014-2026 + câu hỏi tiền-đăng-ký riêng.

## Retro 2026-09-07 — XONG (job Mike_20260907_173542)
File `kb/incidents/retro/retro-2026-09-07.md` (commit 47168ff6), Wags CONFIRMED. 1 sự cố CÒN HỞ:
cron `vn_realestate_monthly_check.sh` chạy 20:00 UTC (=03:02 ICT ngày sau) nhưng comment/2 file doc
(`cron_registry.md:93`, `vn-realestate-structural-risk-20260826.md:49`) ghi sai là 20:00 ICT ngày 6 —
do hiểu nhầm dòng `TZ=` đầu crontab chỉ set env cho script, KHÔNG đổi cách cron parse giờ (host
Etc/UTC). arch-reviewer bắt được (NEEDS_CHANGES), nhưng Wags CHƯA sửa 3 nơi doc drift + chưa sửa
lại con số sai trong chính finding trên bus. Pattern §29 góc mới: agent xử lý sự cố tự chép giả
định chưa verify runtime, dù bằng chứng (mtime/ts bus) đã nằm sẵn trong log agent đang đọc.
**Việc còn treo, cần theo dõi**: câu hỏi bus `Wags/wags-fix-not-confirmed: coord-2026-09-07` — đóng
khi có commit sửa cả 3 nơi doc + finding trên bus.

## Bus question đang mở (2)
1. `Wags/wags-fix-not-confirmed: coord-2026-09-07` (mới, 09-07) — 3 nơi doc drift cron
   vn_realestate_monthly_check.sh CHƯA SỬA, xem chi tiết trên. Cửa sổ theo dõi: trước cron chạy
   lại tháng sau (~10-06).
2. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C, đã ack
   triaged-needs-human bởi Wags 01:21:19Z.

⚠️ Đã ĐÓNG (không còn treo, verify lại 09-07 qua bus_question_audit.py): `Wags/wags-fix-not-confirmed:
coord-2026-09-03` (retro 09-05, tz_anchor_gate.py RULE 2, commit 0aab5fae) và
`Mike/bq-monthly-pin-thieu-202608-202609-chay-bu-hay-khong`.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

- [2026-09-08T05:01:27Z] Treasury-buyback OShares overlay (VRE vs AIS) ĐÓNG 2026-09-08: CONFIRMED 2 vòng quant-skeptic nhưng user chốt KHÔNG wire production, giữ ad-hoc tool. kb/projects/treasury-buyback-oshares-overlay-20260907.md
