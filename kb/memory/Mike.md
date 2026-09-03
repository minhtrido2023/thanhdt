# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Retro 2026-09-03 — XONG, có việc cần theo dõi
kb/incidents/retro/retro-2026-09-03.md, commit d9589e2e. 3 sự cố: (1)+(2) `preflight_check.sh`
§5 rồi §3 false-warn "dữ liệu cũ" trong kỳ nghỉ Quốc khánh 31/08-02/09 — cả 2 cùng lỗi đo ngày
lịch không biết lễ, vá cách nhau vài giờ CÙNG buổi sáng 09-03 (đã fix cả 2, commit 0b83f507 +
81cc0428). Pattern 1 mới: 1 file checker có nhiều nhánh cảnh báo có thể lặp cùng lỗi thiết kế —
CHƯA đủ 2 lần retro để escalate, chỉ đề xuất quét `mike/bin/*.sh` tìm ngưỡng ngày-lịch tương tự.
(3) arch-reviewer NEEDS_CHANGES (05:57Z) cho Wags: Wags đã báo SAI cho user rằng ack deposit-rate
sẽ "tự nổi lại trước cron DCF 09-11" (cơ chế thật: ack vĩnh viễn, suppress_days trơ vì cron tháng).
**CẦN LÀM: kiểm tra Discord Trading Daily xem đã đính chính với user chưa** — chưa thấy bus event
xác nhận tính đến 2026-09-04 00:30 ICT. Nếu chưa đính chính, phải làm trước 2026-09-11 (cron DCF
kế tiếp) kẻo claim sai bị lộ bằng thực tế. Bus question `Wags/wags-fix-not-confirmed:
coord-2026-09-03` (0d tuổi, chưa overdue) đang theo dõi việc này — đừng mở question thứ 2.
Wags CONFIRMED (không gap) khi verify draft.

## Vận hành — không có việc treo khác
Không circuit breaker trip, không pending_resumes. 2 bus question mở (cả 2 mở trong ngày 09-03,
0d tuổi, không overdue): Wags/wags-fix-not-confirmed (xem trên), Winston/deposit-rate-refresh-question.

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Mania research (Taylor, chuỗi đang mở)
2026-09-03: top-detection-technical-signals, mania-exit-reentry-roundtrip-verdict,
mania-quality-tilt-verdict — 3 finding mới ghi bus, chưa tổng hợp thành kết luận wire/no-wire.
Research-only, chưa đổi gì production.

- [2026-09-03T10:32:16Z] ARIA (Automated Research & Intelligence Analytics) = tên vận hành chính thức của hệ thống, duyệt 2026-09-03. Dùng trong email gửi nhà đầu tư bên ngoài. Wire: render_report_html.py header + footer (commit fb5caaba worktree session/1522576692638388364).
