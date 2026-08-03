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
| 4 | Chạy được bash ⇒ ghi được bus (`append_event.sh`) | ~~`echo BUSWRITE-OK > proof.txt`~~ → **dispatch thật `Wendy_20260803_033110`** dưới ĐÚNG gate production | ✅ 2 bus event thật, đúng `trace_id` |

> **⚠️ Đính chính #4 (2026-08-03, do `bin/second_opinion.sh` bắt được — xem cuối file).**
> Bằng chứng ban đầu tôi trích cho dòng #4 là **SAI**, dù kết luận đúng. Test `echo BUSWRITE-OK
> > proof.txt` chạy trong thư mục tạm mà `opencode.json` ở đó **chỉ có `instructions`, KHÔNG có
> khối `permission`** (đã kiểm lại: `keys: ['$schema','instructions']`) — tức nó chứng minh
> "bash chạy được khi KHÔNG có gate", không phải "ghi được bus DƯỚI gate production". Tệ hơn,
> `echo` **không nằm trong allowlist** của gate thật, nên chính test đó sẽ bị chặn nếu chạy đúng
> cấu hình — mâu thuẫn với dòng 61-64 của bản gốc.
> Bằng chứng ĐÚNG cho #4 là job `Wendy_20260803_033110`: chạy dưới `agents/Wendy/opencode.json`
> thật (deny-by-default + allowlist có `append_event.sh`) và ghi được 2 bus event đúng `trace_id`.

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
Chạy lại prompt tương tự (ngắn hơn) xong trong <15s. Chưa root-cause.

**Đính chính (2026-08-03, second_opinion bắt):** bản gốc suy từ **n=1** thành mệnh đề chắc nịch
"Free tier KHÔNG đảm bảo độ trễ" rồi lấy nó biện minh cho `allow_agents` hẹp. Cả hai đều quá tay:
- n=1 chưa loại trừ được nguyên nhân thay thế (prompt 3 việc dài, cold-start model, mạng, hoặc
  `timeout` giết trong khi process con vẫn đang chờ). Đúng mức là: **đã quan sát 1 lần độ trễ
  bất thường, chưa đủ mẫu để kết luận phân phối** — muốn khẳng định phải đo ≥20 lần lấy p50/p95
  và đối chứng cùng prompt trên claude để tách biến model / CLI / mạng.
- `allow_agents` hẹp là quyết định **AN TOÀN** (gate `permission` có lỗ hổng chuyển hướng `>`),
  **không phải** quyết định độ trễ. Trộn 2 khái niệm làm cả hai lý lẽ yếu đi.

Vẫn giữ khuyến nghị **không dùng Zen free cho việc trên đường găng** (plan T+1, EOD report) — nhưng
ghi đúng căn cứ: đó là lựa chọn thận trọng trước một biến chưa đo, không phải kết luận đã chứng minh.

## Chưa kiểm được (nợ, đừng coi là đã xong)

- **Log có STREAM khi chạy dài không** — lần chạy nền kết thúc <15s nên không lấy được mẫu
  giữa chừng. Đây là dữ kiện QUYẾT ĐỊNH cho `heartbeat: "log-mtime"`; nếu log chỉ được ghi lúc
  process thoát thì `log-mtime` vô dụng. **Phải đo bằng 1 task đủ dài trước khi wire.**
- `--format json` schema thật (mới đọc doc, chưa chạy).
- ~~`permission` có cưỡng chế khi kèm `--auto` không~~ → **ĐÃ KIỂM 2026-08-03, cưỡng chế thật:**
  với `bash: {"*":"deny", "echo ALLOWED*":"allow"}` + `--auto` — lệnh trong allowlist chạy (6s),
  lệnh ngoài allowlist **bị chặn**, trả lỗi sạch trong 7s (*"The user has specified a rule which
  prevents you from using this specific tool call"*, kèm liệt kê rule), **không treo**, file không
  được tạo. Output còn cho thấy `--auto` thêm rule `{"permission":"*","action":"allow"}` nhưng rule
  `bash deny` cụ thể vẫn thắng ⇒ xác nhận `--auto` KHÔNG đè lên `deny`.
  ⚠️ Nhưng đây là gate **chống tai nạn**, không phải sandbox: pattern khớp trên chuỗi lệnh nên một
  lệnh trong allowlist vẫn có thể kèm chuyển hướng (`grep x y > z`) để ghi file.

---

## Hậu kiểm: chính tài liệu này bị `bin/second_opinion.sh` phản biện (2026-08-03)

Lần chạy thật đầu tiên của `bin/second_opinion.sh` (opencode + `deepseek-v4-flash-free`, job
`Wags_20260803_041742`) lấy chính file này làm đối tượng, và **bắt được 3 điểm — 1 trong đó là
lỗi thật**:

1. **Bằng chứng cho giả định #4 không hợp lệ** (đã đính chính ở trên). Nó chỉ ra mâu thuẫn nội
   tại: doc vừa nói `echo > file` ghi được, vừa nói gate chặn `echo` — hai mệnh đề không thể cùng
   đúng. Kiểm lại: test đó chạy với `opencode.json` **không có khối `permission`**. Đúng.
2. **Suy từ n=1 thành chính sách độ trễ** + trộn nó với lý do an toàn (đã đính chính).
3. **"0 credentials" chỉ dựa trên 1 file** `auth.json`; chưa loại trừ keyring/env var. Điểm phụ
   (bằng chứng hành vi `PONG` rc=0 đã khá trực tiếp) nhưng nhận xét đúng.

Nó cũng **tự xác nhận độc lập** được giả định #2 và #3 — vì chính nó đang chạy dưới cấu hình đó và
thấy `agents/Wags/CLAUDE.md` + `context_ops_mini.md` + `WorkingClaude/CLAUDE.md` trong context của
mình — và **tự khai đúng cái nó không kiểm được** (bash bị gate chặn nên không chạy lại được
`opencode run --help`, không đọc được `auth.json`).

**Ý nghĩa**: đây đúng là giá trị mà multi-CLI được dựng lên để lấy — một họ model khác đọc cùng
tài liệu và thấy chỗ tác giả không thấy, với chi phí ~0. Lưu ý nó bắt lỗi **lập luận/bằng chứng**,
không phải lỗi domain; và nó vẫn là ADVISORY, không phải cổng duyệt.

---

## A/B trên TASK THẬT: deepseek vs claude, cùng một việc tra cứu (2026-08-03)

Chính sách user 2026-08-03 coi `deepseek-v4-flash-free` ngang tầm Sonnet để chia tải. Dưới đây là
phép đối chứng đầu tiên trên **một task vận hành có thật, lặp lại hàng tháng** (tra lãi suất huy
động Big-4 — 7+ lần trong mẫu job gần đây), với **ground truth độc lập**:

| | Job | Kết quả VCB 12T online |
|---|---|---|
| **claude** | `Winston_20260803_011003` (01:18Z, cron thật) | **5,9%** (trong chuỗi Agribank 6,8 / BIDV 6,8 / VietinBank 6,05 / VCB 5,9 → escalate vì phân kỳ) |
| **opencode + deepseek** | `Winston_20260803_045321` (04:53Z, dispatch tay) | **5,9%** |

Hai lần chạy **độc lập**, khác họ model, khác thời điểm, **ra cùng con số**.

Đáng chú ý hơn con số: bản deepseek **tự phát hiện 3 nguồn mâu thuẫn (5,2 / 5,9 / 4,6)**, nói
thẳng *"Cần đối chiếu thêm trước khi kết luận — không đoán"*, rồi đối chiếu 2 nguồn, dẫn tên trang
+ ngày khảo sát, và tự nêu giới hạn (*"chưa có khảo sát riêng cho tháng 8/2026; số mới nhất đã xác
minh là khảo sát 07/07/2026"*). Đó đúng kỷ luật provenance mà `coding_guidelines.md` §6 đòi — không
phải hành vi phải nhắc riêng.

**Kết luận có mức độ**: đủ để tin cho **lớp task tra-cứu-web read-only**, là đúng lớp đang được
chuyển tải. **KHÔNG** suy rộng ra lớp task khác (quant, code, phán đoán domain) — chưa đo.
n=1 task, 1 lần chạy: đây là tín hiệu ủng hộ chính sách, không phải phép đo phân phối.
