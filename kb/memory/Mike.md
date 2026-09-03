# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Retro 2026-09-02 — XONG
kb/incidents/retro/retro-2026-09-02.md, commit 60bc61a5. 3 sự cố: (1) paper_checkpoint_escalation
báo động giả (registry field tổng vs per-gate không đồng bộ khi fill_timing go-live, đã vá
commit 75dbc7a3), (2) SCL BQ Price vs broker giá lệch — CHƯA điều tra tận gốc, theo dõi tiếp,
(3) báo cáo tuần 08-24→08-28 thiếu cổ tức 6 mã, chỉ 1/6 (SCL) bị report_return_gate.py chặn — 5
mã còn lại lọt gate, chỉ người tự rà bắt được → khoảng trống gate THẬT (không phải điểm tích
cực như draft ban đầu tưởng). 2 pattern theo dõi (chưa đủ 2 lần retro để escalate): Pattern 1
registry field-sync (2 lần/tuần), Pattern 2 dividend-gate-gap. Wags GAPS FOUND đã sửa vào entry.

## Vận hành — không có việc treo
Không circuit breaker trip, không pending_resumes, không bus question mới mở (3 câu cũ đã đóng
thật trong ngày 09-02, có artifact).

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Chuỗi crisis-trigger research (30/08-31/08) — ĐÓNG HOÀN TOÀN
Research-only, không wire gì production. KHÔNG đổi playbook margin/derisk đã chốt 26/08.

- [2026-09-03T10:32:16Z] ARIA (Automated Research & Intelligence Analytics) = tên vận hành chính thức của hệ thống, duyệt 2026-09-03. Dùng trong email gửi nhà đầu tư bên ngoài. Wire: render_report_html.py header + footer (commit fb5caaba worktree session/1522576692638388364).
