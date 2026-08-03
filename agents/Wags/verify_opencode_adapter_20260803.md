---
kind: verification
title: Kiểm chứng thực nghiệm adapter opencode (chạy binary thật, không đọc doc)
owner: Mike
date: 2026-08-03
related: design_multi_cli_dispatch_20260803.md
---

# Kiểm chứng opencode — chạy thật, không suy từ tài liệu

Môi trường: `opencode-ai@1.18.11`, cài qua `npm install -g opencode-ai`, binary
`/home/trido/.nvm/versions/node/v22.23.0/bin/opencode`. **0 credentials**
(`~/.local/share/opencode/auth.json` rỗng). Model dùng: `opencode/deepseek-v4-flash-free`
(Zen free tier — user chốt 2026-08-03).

## Kết quả — 4 giả định cốt lõi của thiết kế

| # | Giả định | Cách kiểm | Kết quả |
|---|---|---|---|
| 1 | Zen free tier chạy **không cần login** | `opencode run -m opencode/deepseek-v4-flash-free "Reply with exactly: PONG"` | ✅ ra `PONG`, rc=0, 0 credentials. **Không có blocker auth cho opencode** |
| 2 | Đọc `CLAUDE.md` từ `--dir` (không cần sinh `AGENTS.md`) | tạo `CLAUDE.md` chứa mã bí mật `ROLE-ALPHA-771`, hỏi lại | ✅ trả đúng `ROLE-ALPHA-771` |
| 3 | Nạp context ngoài qua `opencode.json` → `instructions` (đường dẫn TUYỆT ĐỐI) | `{"instructions":["<abs>/extra_context.md"]}` chứa `CTX-BRAVO-442` | ✅ trả đúng `CTX-BRAVO-442` |
| 4 | Chạy được bash ⇒ ghi được bus (`append_event.sh`) | `--auto` + yêu cầu `echo BUSWRITE-OK > proof.txt` | ✅ file được ghi thật, log hiện dòng tool `$ echo …` |

⇒ **Artifact 3 (`render_agent_profile.sh`, flatten `@import`, sinh `AGENTS.md`) KHÔNG CẦN cho
opencode.** Thay bằng 1 file khai báo `agents/<id>/opencode.json` — sibling của
`.claude/settings.json`, track git, không phải file dẫn xuất ⇒ triệt tiêu luôn nguy cơ đua ghi
+ bị `consolidate.sh`/`fleet_backup.sh` quét `git add` blanket (§13 coding_guidelines).

## Ánh xạ flag đã xác minh trên `opencode run --help` (bản 1.18.11 thật)

| Trục | claude hôm nay | opencode |
|---|---|---|
| prompt | `-p "<text>"` | positional `run [message..]` |
| cwd | `cd $AGENT_DIR` | `--dir <DIR>` |
| model | `--model sonnet` | `-m provider/model` |
| effort | `--effort high` | `--variant` ("provider-specific reasoning effort, e.g. high, max, minimal") |
| autonomy | `--permission-mode auto` | `--auto` ("auto-approve permissions that are not explicitly denied") |
| turn cap | `--max-turns N` | **không có flag**; có `steps` trong agent config |
| output | log text thô | `--format json` (raw JSON events) — tốt hơn `tail -c 500` |
| resume | — | `-c/--continue`, `-s/--session`, `--fork` |

Ngoài ra: `opencode acp` (tự làm ACP server), `opencode serve` (headless server, tránh cold
boot — đáng cân nhắc nếu dispatch nhiều), `opencode models`, `opencode providers login`.

## ⚠️ Rủi ro vận hành đã QUAN SÁT ĐƯỢC, chưa giải thích

Một lần chạy (prompt 3 việc, `--auto`) **treo và bị `timeout 150` giết**, không ra output nào.
Chạy lại prompt tương tự (ngắn hơn) xong trong <15s. Chưa root-cause: nghi free tier bị
throttle/queue. ⇒ **Free tier KHÔNG đảm bảo độ trễ**. Hệ quả cho thiết kế:
- Không dùng Zen free cho việc nằm trên đường găng vận hành (plan T+1, EOD report…).
- Đúng lý do `allow_agents` phải giữ hẹp ở v1 (research/read-only).
- Cần đo lại độ trễ p50/p95 trước khi tin vào bất kỳ TIMEOUT mặc định nào.

## Chưa kiểm được (nợ, đừng coi là đã xong)

- **Log có STREAM khi chạy dài không** — lần chạy nền kết thúc <15s nên không lấy được mẫu
  giữa chừng. Đây là dữ kiện QUYẾT ĐỊNH cho `heartbeat: "log-mtime"`; nếu log chỉ được ghi lúc
  process thoát thì `log-mtime` vô dụng. **Phải đo bằng 1 task đủ dài trước khi wire.**
- `--format json` schema thật (mới đọc doc, chưa chạy).
- `permission: {edit|bash: allow|ask|deny}` có thật sự cưỡng chế khi kèm `--auto` không —
  `--auto` mô tả là "auto-approve permissions **that are not explicitly denied**", ngụ ý `deny`
  vẫn thắng, nhưng **chưa kiểm bằng thực nghiệm**. Đây là luận điểm an toàn chính của việc
  chọn opencode ⇒ không được tin vào doc, phải test.
