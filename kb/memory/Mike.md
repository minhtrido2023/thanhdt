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

## Retro 2026-09-04 — XONG, escalate mở
kb/incidents/retro/retro-2026-09-04.md, commit 882a6bef. Wags CONFIRMED, 0 gap.
2 sự cố: (1) `macro_healthcheck.py::tdays()` (repo WorkingClaude/, NGOÀI mike/bin) — CALL-SITE
THỨ BA của cùng lỗi đếm tuổi dữ liệu bằng ngày lịch không biết lễ (sau preflight_check.sh §3+§5
vá 09-03) — lan sang repo khác. Fix + entry đã có trước retro (Winston, 96ebd124+9380cbc3).
(2) ops_health_check.sh deposit_rate hardening chủ động (§29), không phải sự cố thật.
**Pattern 1 tái diễn 2 retro liên tiếp (09-03→09-04) → ĐÃ ESCALATE** bus question
`retro-pattern-recurring-tdays-holiday-2days` — chờ Mike/user quyết có cơ học hoá gate kiểu
tz_anchor_gate.py (AST quét đếm ngày không qua vn_market.is_holiday) hay không. Đừng mở question
thứ 2 cho cùng pattern nếu nó tái diễn lần nữa — chỉ cập nhật escalation cũ.

## Retro 2026-09-03 — carry-over, vẫn mở
`Wags/wags-fix-not-confirmed: coord-2026-09-03` (1d tuổi, chưa overdue): Wags chưa có bằng chứng
đã đính chính với user trên trading_daily về claim sai cơ chế ack deposit-rate (ack KHÔNG tự
re-escalate, khác gì Wags từng nói). Cửa sổ có ý nghĩa: trước 2026-09-11 (cron DCF kế tiếp).

## Vận hành — không có việc treo khác
Không circuit breaker trip, không pending_resumes. 1 bus question mới mở hôm nay (escalation
pattern), 1 carry-over từ 09-03, 1 recurring quen thuộc (due_diligence_corp_flags_selfcheck,
trong hạn suppress, không cần theo dõi riêng).

