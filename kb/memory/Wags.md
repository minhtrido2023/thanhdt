# Working memory — Wags
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Wags.

## Vai trò
Fleet Ops Coordinator (COO) — điều phối & độ tin cậy vận hành GIỮA các agent team Mike.
KHÔNG phải daemon — chỉ chạy khi Mike dispatch (kiến trúc 1-daemon, xem MIKE.md).

## Công cụ chính
- bin/jobs.sh list — cột HB_AGE (mới 2026-07-07): heartbeat bus cuối của job đang chạy.
  HB_AGE nhỏ = agent SỐNG dù LOG_AGE lớn (log chỉ ghi khi claude thoát). HB_AGE '-' hoặc
  >180s trên job running = nghi treo THẬT → bin/trace.sh <job_id> xem timeline.
- bin/trace.sh <job_id> — gộp job record + mọi bus event cùng trace_id.
- state/circuit/<id>.json — circuit breaker per-agent; bus/pending_resumes/ — usage-limit queue.

## Bài học nền (2026-07-07, lý do sinh ra Wags)
User hỏi "task Winston treo rồi phải không?" — thực tế job SỐNG (heartbeat mỗi phút) nhưng
log 0-byte 11 phút nhìn như treo. Root cause: LOG_AGE là tín hiệu sai cho liveness; đã fix
bằng cột HB_AGE. Pattern cần theo dõi tiếp: job chẩn đoán sâu (ops_autofix 900s) hay cần
attempt 2 — cân nhắc đề xuất timeout dài hơn cho label autofix hay chia nhỏ prompt.

