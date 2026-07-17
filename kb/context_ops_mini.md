# Mike fleet — context ops-mini (fleet-ops/tooling tasks only)
> Dành cho agent làm việc THUẦN hạ tầng điều phối (Wags và mọi dispatch gắn cờ
> `--context mini`) — KHÔNG có domain trading (V2.4/8L/DT5G/BQ). Nếu việc đang làm
> cần hiểu chiến lược/dữ liệu trading, đây KHÔNG đủ — báo lại cho Mike thay vì đoán.
> Full context: `kb/context_pack.md` (nặng hơn nhiều, chỉ dùng khi thật sự cần).

## ROOT
`/home/trido/thanhdt/WorkingClaude/mike` — mọi đường dẫn dưới đây tương đối gốc này.

## Cơ chế dispatch (bạn đang chạy TRONG 1 lần dispatch)
- Dispatched qua `bin/dispatch.sh <id> "prompt" [--bg] [--model] [--effort] [--context]`.
- Job record: `bus/jobs/<job_id>.json` — tra bằng `bin/jobs.sh status <job_id>` (exit
  0=done 2=running 3=overdue 1=failed/timeout 4=not-found).
- Ghi kết quả lên bus: `bin/append_event.sh <agent_id> finding "<chủ đề>" '<payload_json>' '<trace_id=job_id>'`
  (hoặc `decision`/`answer`/`error`). Đây là phiên headless — kết quả PHẢI lên bus để fleet thấy được.
- Heartbeat bắt buộc mỗi 4-5 tool call: `bin/append_event.sh <agent_id> heartbeat '<job_id>' '{"status":"in_progress","note":"..."}' '<job_id>'`.
- `discord_thread_id` được ghi lại NGAY lúc dispatch trên chính job record — mọi thông báo
  Discord tự động đi đúng topic đã gọi việc, không cần bạn tự lo Discord routing.

## Vòng đời sự cố điều phối (Wags) — pipeline `bin/wags_autofix.sh`
1. Chẩn đoán + sửa trực tiếp file trong `bin/`, `MIKE.md`, `hooks/`, `kb/INCIDENTS.md`.
2. Ghi finding lên bus (`wags-fix: <topic>`) kèm root_cause/fix/verify/commit.
3. Pipeline tự dispatch `arch-reviewer` (đọc-only) audit lại — **bắt buộc nếu fix chạm
   `bin/dispatch.sh`/`bin/run_bot.sh`/`bot_execute.py`/`trading_bot/`/`trading_rules.json`/
   plan JSON**; các fix KHÁC (docs, notification text, log format, tooling không đụng
   surface tiền thật) chỉ cần self-check kỹ + có thể được audit lấy mẫu sau, không bắt
   buộc chờ arch-reviewer mỗi lần (chính sách 2026-07-17, xem `kb/INCIDENTS.md`).
4. **KHÔNG BAO GIỜ** tự sửa: trade plan, `trading_rules.json`, logic đặt lệnh, dòng cron
   THỰC THI, xoá dữ liệu, `BOT_STOP` — luôn escalate (event `question`) cho việc này.

## Coding guidelines cốt lõi (đầy đủ ở `kb/coding_guidelines.md`)
1. Simplicity first — code tối thiểu giải quyết đúng vấn đề, không thêm tính năng chưa
   được yêu cầu.
2. Surgical changes — chỉ đụng đúng chỗ cần, không "tiện tay" dọn code không liên quan.
3. Idempotent side-effects — script có side-effect ngoài (đặt lệnh, gửi tin) phải chịu
   được bị kill giữa chừng rồi chạy lại mà không lặp hành động.
4. Khi sửa 1 quy tắc hành vi: grep MỌI nơi quy tắc đó được "operationalize" (docs, chuỗi
   in ra runtime, config) — sửa văn bản mô tả không tự động sửa code thực thi.
5. Ưu tiên ghi sự thật bền NGAY LÚC phát sinh (vd job thuộc topic nào) thay vì suy luận
   lại từ trạng thái hiện tại dễ đổi.

## Công cụ hay dùng
- `bin/jobs.sh {list|status|wait}` — poll job board.
- `bin/trace.sh <job_id>` — gộp job record + mọi bus event cùng trace_id thành 1 timeline.
- `bin/fleet_health.sh` — bảng sức khỏe toàn fleet (SERVING/CTX/uptime).
- `bin/verify_finding.sh` — dispatch quant-skeptic phản biện 1 finding R&D (không dùng
  cho việc tooling thuần).
- Git: repo `mike` (fleet code) — commit trực tiếp cho quyết định sống, message mô tả rõ
  root cause/fix/verify. Repo `WorkingClaude` (trading code) — commit sau khi user xác
  nhận nếu chạm surface tiền thật.

## Khi nào KHÔNG đủ (báo lại thay vì tự đoán)
- Cần hiểu chiến lược trading (V2.4, allocator, custom30V, DT5G, 8L rating).
- Cần schema/tên bảng BigQuery cụ thể.
- Cần lịch sử quyết định nghiệp vụ (vd tại sao 1 mã bị BANNED, tại sao chọn tham số X).

Những việc trên → escalate về Mike (event `question`) hoặc yêu cầu dispatch lại với
context đầy đủ, đừng suy đoán từ context-mini này.
