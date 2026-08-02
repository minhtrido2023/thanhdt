# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-01 EOD (sau daily retro finalize, Wags GAPS FOUND → fixed → kb/incidents/retro/retro-2026-08-01.md, commit 1059a085)

## RETRO 2026-08-01 — 8 sự cố (6 đã ghi trước, 2 gap tự bổ sung), Pattern 1 ESCALATED
Ngày nặng: 4 cơ chế nền của chính fleet chết ÂM THẦM (daily_retro.sh 2 đêm, kb_nightly.sh 2 tuần,
dispatch --bg toàn fleet 1h10m, báo cáo tuần/tháng 2 tuần) — TÁI DIỄN đúng Pattern A mà RETRO 07-28
đã cảnh báo. Đã escalate `retro-pattern-recurring-silent-cron-spof-2` lên bus. Tin tốt: hôm nay
ship prevention thật (không chỉ prose) — `bin/cron_health_check_daily.sh` (cron 08:25) +
`bin/shellcheck_gate.sh` (pre-commit, chặn đúng lớp bug quoting gây sự cố 1+4) + forcing-function
báo cáo cadence. Cả 3 CHƯA qua 1 chu kỳ production thật nào tại thời điểm viết retro.

## Việc còn treo sang mai (ưu tiên cao nhất trước)
- **Sự cố 7 (saga "coord-", ưu tiên CAO — human-in-the-loop integrity)**: Wags tự sửa
  ops_health_check.sh check #5, ≥5 vòng arch-review (07-30→08-01) vẫn NEEDS_CHANGES. Round-5 phát
  hiện: 1 phiên Mike đã tự tay đóng 21 bus question (07-31, closed_by=Mike/stale_superseded) —
  round-5 nhầm "pool đã cạn" là bằng chứng fix đúng. Bus question mới nhất:
  `wags-fix-not-confirmed: coord-2026-08-01` (08:30:29Z) CHƯA có answer. Cần user/Mike quyết
  bước tiếp theo — KHÔNG tự dispatch Wags thêm vòng nữa cho tới khi có quyết định rõ.
- Xác nhận `cron_health_check_daily.sh` chạy chu kỳ thật đầu tiên (08:25 ICT 08-02).
- `bin/wakeup_profile.py` (Wags DONE, code+test xong, CHƯA wire live) — chờ Mike duyệt; có thể
  giúp giảm vi phạm §8 wakeup (3/9 = 33,3% hôm nay, cả 3 dạng "bundle").
- Backfill RETRO 07-30/07-31 hay bỏ qua — nợ cũ (07-24→07-27 vẫn treo, giờ +2 ngày = 6 ngày chưa
  từng review).
- Kế thừa treo cũ (không mới hôm nay): funding_required residual risk (theo dõi lần 4 nếu xảy
  ra), PNJ TTL anomaly_flags (~08-23), dt5g-live-2-writer quyết định A/B/C (bus question 07-29,
  vẫn PENDING).

- [2026-08-02T17:20:54Z] 2026-08-02: user hỏi về job fail 'quá 50 tasks' (max-turns) — có bình thường không, nên điều chỉnh sao. Điều tra data thật: 29 lần trong lịch sử, 5 lần NGAY HÔM NAY, tất cả attempt 2/2 dùng CHUNG 1 trần 50 (retry vô ích, đúng 'chạy tới chạy lui' user mô tả), tất cả effort=high/opus (task thật sự phức tạp, không phải lỗi). Fix 2 lớp mirror cơ chế usage-limit-resume có sẵn: (1) default --max-turns SCALE theo effort khi omit (high→80, xhigh/max→120); (2) auto-continuation thật — hết lượt còn attempt thì BUMP gấp đôi retry ngay trong loop, hết attempt thì queue bus/pending_resumes (kind=max_turns, resume NGAY ~30s, giữ nguyên model/effort, trần bump thêm lần nữa, cap DISPATCH_MAX_TURNS_RESUMES=2). Bonus fix: usage-limit resume trước đây CŨNG âm thầm rơi model/effort về default mỗi lần resume — giờ cả 2 loại đều giữ nguyên. Tự bắt lỗi export list thiếu (function mới chạy trong systemd-run --scope detached child cần export -f tường minh) trước khi test. Verify end-to-end thật: mock claude binary tái hiện đúng lỗi, chạy dispatch.sh thật, xác nhận đúng chuỗi 80→160→200(cap)→pending_resumes, xác nhận resume_pending.py build đúng argv --model/--effort/--max-turns, xác nhận backward-compat record cũ (6 arg, không có kind) vẫn hoạt động đúng. Commit + incident kb/incidents/2026-08/2026-08-02-max-turns-auto-continuation.md.
