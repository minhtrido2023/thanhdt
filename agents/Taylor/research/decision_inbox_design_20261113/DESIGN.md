# Decision Inbox — quyết định của user tự lên bus, không qua lệnh Bash của phiên LLM

Job `Taylor_20261113_075639` · 2026-11-13 · **CHỈ THIẾT KẾ** — không sửa code production, không sửa
settings/permission, không merge. Mọi số trong file này đo trong phiên này (lệnh ghi ở §0), trừ chỗ gắn
nhãn `ước lượng`.

## 0. Hiện trạng đo được (nền cho mọi quyết định bên dưới)

| Sự kiện | Số đo | Lệnh/nguồn |
|---|---|---|
| Tool-result bị classifier chặn trong phiên Mike | **73** lần, 14/10→13/11 (25 ngày có ca), max **8**/ngày (29/10, 05/11); 13/11 = 6 | `clf_count.py` (cùng thư mục) (parse `tool_result` chứa chuỗi `denied by the Claude Code auto mode classifier` trong `~/.claude/projects/*agents-Mike/*.jsonl`); đếm chuỗi thô = 150 vì cùng 1 lần chặn xuất hiện lại trong context ⇒ **phải đếm theo tool_result, không grep -c** |
| Lệnh bị chặn nhiều nhất | `approve_plan_simple.sh` 4, `clear_books_daily.sh` 4, `curl /api/spawn` 4, **`close_bus_question.py` 4**, `jobs.sh` 3, `remember.sh` 3, `notify_thread.sh` 2, ScheduleWakeup 2 | như trên |
| Taylor / Wags cũng bị | Taylor 15, Wags 2 (đếm chuỗi thô, chưa khử trùng) | như trên |
| Vì sao có classifier | `CCDB_PERMISSION_MODE=auto` trong `/workspace/ccdb-mike/.env` | đọc `.env` (chỉ key) |
| Câu hỏi bus đang mở | **21**, chỉ **3** có `options` (PNJ, fleet-backup-gh001, nav-loss-brake) | `bus_question_audit.py --json` + join inbox |
| Câu hỏi mang Discord thread/message id | **0** câu | grep `thread` trong payload `question` ở `bus/inbox/*.jsonl` |
| Bridge | `ccdb-mike.service` (systemd **--user**), cwd `/workspace/ccdb-mike`, code `/workspace/claude-code-discord-bridge`; `main.py` đọc `CUSTOM_COGS_DIR` (cog_loader.py) — **hiện CHƯA đặt**; `allowed_user_ids=None` (không có OWNER) | `systemctl --user cat`, `main.py:80,189,204` |
| API `GET /api/threads/{id}/messages` | trả `id, author(display_name), is_bot, content, created_at, jump_url` — **KHÔNG có author.id, KHÔNG có reply-to** | `api_server.py:96-111` |
| `POST /api/notify` | **không trả message_id** (chỉ `thread_id` khi tạo thread) | `api_server.py:479-548` |

Hệ quả thiết kế: (1) 3 câu có options mở cùng lúc ⇒ "A" trần **luôn nhập nhằng** nếu không gắn câu
hỏi vào tin nhắn Discord cụ thể; (2) gắn bằng id phải được tạo ra — hiện chưa có; (3) chỉ bên trong
process bridge mới thấy `author.id` + `message.reference` ⇒ quyết định chọn đường (a).

## 1. Hai phương án đường chạy

### (a) Custom cog trong bridge ccdb-mike — **CHỌN**
- File mới **ngoài repo bridge**: `mike/ccdb_cogs/decision_inbox_cog.py` (`async def setup(bot, runner, components)`),
  bật bằng 1 dòng `CUSTOM_COGS_DIR=/home/trido/thanhdt/WorkingClaude/mike/ccdb_cogs` trong
  `/workspace/ccdb-mike/.env` + `systemctl --user restart ccdb-mike`.
- **Không chạm core bridge** (`claude_chat.py` giữ nguyên) ⇒ `ccdb_bridge_drift_check.sh` không thấy drift,
  rebase upstream không xung đột. Listener `on_message` của cog chạy **song song** với `ClaudeChat.on_message`
  (discord.py gọi mọi listener) — không nuốt tin, Mike vẫn nhận tin như cũ.
- Cog **mỏng**: chỉ thu `{message_id, channel_id, parent_id, author_id, reference_message_id, content, created_at}`,
  ghi 1 dòng JSONL atomic vào `mike/state/decision_inbox/raw/<YYYYMMDD>.jsonl`, rồi
  `asyncio.create_subprocess_exec(python3, mike/bin/decision_inbox.py, --event-file ...)` timeout 30s.
  Mọi logic khớp/đóng/hành động nằm trong **script xác định** `bin/decision_inbox.py` — test được ngoài bridge.
- Cog cũng nghe **tin của chính bot** chứa thẻ `[#q<6hex>]` ⇒ ghi map `message_id → question event_id` vào
  `state/decision_inbox/surfaced.jsonl` (đây là cách tạo liên kết reply-to mà §0 thiếu).
- Ưu: thấy author.id (chặn người khác trong kênh), reply-to, real-time (<2s `ước lượng`).
- Rủi ro: bridge restart khi đổi `.env` (~15s gián đoạn, `RestartSec=15`); lỗi trong cog bị `cog_loader`
  log-and-skip — **không làm sập bridge** (`cog_loader.py` docstring: "A single Cog's failure is logged and skipped").
  Lỗi trong handler runtime: bọc `try/except Exception` toàn bộ, log + đếm, không raise.

### (b) Cron/inotify poll — loại
- Nguồn khả dĩ: `GET /api/threads/{id}/messages` (poll mỗi 1'), hoặc transcript `~/.claude/projects/*agents-Mike/*.jsonl`.
- Loại vì: API **không có author.id** (chỉ display_name — giả mạo được bằng đổi nickname) và **không có
  reply-to**; transcript chỉ có prompt đã bị bridge bọc (`[now: …]`), không có message id, và chỉ tồn tại
  khi phiên LLM đã chạy — đúng thứ ta muốn bỏ phụ thuộc. Thêm: phải biết trước danh sách thread để poll.
- Giữ (b) làm **lưới đối soát hằng ngày** (không đóng gì): xem §6 bước 7.

## 2. Bộ khớp xác định (`bin/decision_inbox.py`)

### 2.1 Ngữ pháp câu trả lời (toàn bộ tin nhắn phải khớp — không tìm "A" lẫn trong câu dài)
Chuẩn hoá: NFC → lower → bỏ dấu tiếng Việt (chỉ cho từ khoá) → gộp khoảng trắng → bỏ `.!` cuối.
```
^(?:(duyet|chon|chot|ok|dong y)\s+)?(?:(phuong an|pa|option)\s+)?([a-h])(?:\s+#(q[0-9a-f]{6}))?$
```
Ví dụ khớp: `A`, `Duyệt A`, `chọn B`, `PA a`, `Duyệt A #q1f2e3d`. Không khớp (⇒ bỏ qua im lặng, để Mike LLM
xử lý như bình thường): `A nhưng sửa ngưỡng`, `ok`, `đồng ý`, `chọn cái đầu`, mọi tin >40 ký tự.

### 2.2 Ứng viên câu hỏi
Nguồn duy nhất: `bus_question_audit.py --json` (giống `close_bus_question.py::pending`) join payload từ
`bus/inbox/*.jsonl`. Chỉ xét câu có `options`. Nhãn option: tiền tố `^([A-H])\s*[:)\.]` trong chuỗi option;
không có tiền tố ⇒ nhãn theo thứ tự A,B,C… và đánh dấu `labels_inferred=true`.

### 2.3 Thứ tự ràng buộc (dừng ở tầng đầu tiên cho ra kết quả)
| Tầng | Điều kiện | Cho phép với câu `risk=money` |
|---|---|---|
| T1 reply-to | `reference_message_id` ∈ `surfaced.jsonl` ⇒ đúng 1 câu | ✅ |
| T2 thẻ | `#q<6hex>` = 6 hex đầu `event_id` câu hỏi, đúng 1 câu | ✅ |
| T3 thread | Trong `channel_id` này, tin gần nhất của bot có thẻ trỏ tới câu X, X còn mở, và **không có câu mở nào khác** từng được surface trong thread | ❌ |
| — | Không tầng nào | **không làm gì, không hỏi** (đa số "A" trong chat là trả lời Mike chứ không phải câu bus) |

Sau khi có câu X: chữ cái phải ∈ nhãn của X; nếu `labels_inferred` và X là `money` ⇒ coi như không khớp.

### 2.4 Nhập nhằng → hỏi lại ĐÚNG 1 lần
Nhập nhằng = T3 thấy ≥2 câu mở, hoặc chữ cái không thuộc nhãn, hoặc câu `money` chỉ khớp được bằng T3.
Cog trả lời trong thread (qua `components`/`message.reply`, không qua LLM):
> Mình chưa đóng được vì chưa rõ bạn trả lời câu nào: `#q1f2e3d` Mike/nav-loss-brake… (A/B) · `#q9a8b7c` …
> Reply thẳng vào tin câu hỏi, hoặc gõ `A #q1f2e3d`.

Chống lặp: khoá `(channel_id, sorted(candidate ids))` trong `state/decision_inbox/asked.jsonl`, TTL 24h —
cùng tập ứng viên trong 24h không hỏi lần 2. Ghi `status` lên bus (`decision-inbox-ambiguous`), **không** tạo
`question` mới (tránh vòng câu-hỏi-về-câu-hỏi).

### 2.5 Phân loại rủi ro (guard tiền thật)
`risk` lấy từ payload câu hỏi (`"risk": "money"|"normal"`). **Vắng mặt ⇒ suy BẢO THỦ là `money`** nếu bất kỳ:
agent ∈ {DollarBill, Mafee}; hoặc topic/summary/options khớp
`plan|lệnh|lenh|order|BOT_STOP|margin|park|excluded|trading_rules|live|bán|mua|NAV|sizing|egg|trứng`.
Câu `nav-loss-brake-review-20261113` (chứa `BOT_STOP`, `NAV`) ⇒ `money` ⇒ chỉ đóng qua T1/T2.
Câu `money` **không bao giờ** kích hoạt `on_answer` (§4) — chỉ đóng + báo Mike.

### 2.6 Chỉ user thật
`author_id ∈ DECISION_INBOX_USER_IDS` (đặt trong `.env` ccdb-mike, fail-CLOSED: biến rỗng ⇒ cog không làm
gì, log 1 cảnh báo lúc load). Bridge hiện `allowed_user_ids=None` nên KHÔNG được dựa vào lớp đó.

## 3. Đóng + provenance (tương thích audit/§20/skill)

Mở rộng **tối thiểu** `bin/close_bus_question.py`: thêm `--provenance-json '<obj>'` (merge vào payload sau
khi validate là dict, cấm ghi đè các key `resolves/decided_by/closed_by`). Gọi:
```
close_bus_question.py 'Mike/nav-loss-brake-review-20261113' \
  --resolution 'User chọn A: giữ cảnh báo' \
  --evidence 'discord msg 1438…(jump_url)' --source-topic 'discord:<thread_id>' \
  --decided-by-user --actor Mike --provenance-json '{...}'
```
Payload kết quả (answer, topic = topic gốc ⇒ matcher chính xác, không dính bẫy substring):
```json
{"resolution":"…","evidence":"…","resolves":["Mike/nav-loss-brake-review-20261113"],
 "closed_by":"Mike","decided_by":"user",
 "decision":{"option":"A","option_text":"A: giữ cảnh báo","labels_inferred":false},
 "provenance":{"via":"decision_inbox","matcher_version":"1","matched_by":"reply_to|tag|thread",
   "discord_message_id":"…","discord_channel_id":"…","discord_author_id":"…",
   "message_text":"Duyệt A","message_ts":"2026-11-13T…Z","question_event_id":"dbacf02d-…",
   "risk":"money"}}
```
- `decided_by:"user"` chỉ đặt khi tầng ràng buộc + author check qua — đúng §20 ("user xác nhận thời gian thực").
- `bus_question_audit.py` đọc `resolves` + `decided_by` sẵn (dòng 117-129) ⇒ không cần sửa audit; thêm
  (tuỳ chọn) bucket `via=decision_inbox` trong báo cáo provenance.
- Giữ nguyên guard rc=4 (rollup) và rc=5 (substring collateral): decision_inbox **không bao giờ** truyền
  `--ack-*`; rc≠0 ⇒ không đóng, post `status decision-inbox-blocked` + báo thread.
- Kết quả hợp lệ chỉ khi helper in `CLOSED` hoặc `ALREADY_CLOSED_OR_UNKNOWN` (skill bước 5). Mike LLM nhận
  cùng tin và cố đóng sau ⇒ nhận `ALREADY_CLOSED_OR_UNKNOWN` — vô hại.
- Phản hồi user (deterministic): react ✅ + reply `Đã ghi: Mike/nav-loss… = A (user)`.

## 4. Hậu quả khai báo sẵn (`on_answer`) — chạy bởi script, không bởi LLM

Payload câu hỏi được phép thêm:
```json
"on_answer": {"A": [{"action":"remember","agent":"Mike","note":"phanh lỗ NAV: giữ CHỈ cảnh báo (user 13/11)"}],
              "B": [{"action":"dispatch_bg","target":"Taylor","template":"nav_brake_autostop_design"}]}
```
- **Whitelist** cố định trong code `bin/decision_actions.py` (không đọc từ file cấu hình để LLM không mở rộng
  được): `remember` (→ `remember.sh`), `append_event` (finding/status, không question/answer), `notify_thread`
  (thread đã đăng ký trong `discord_channels.py`), `dispatch_bg` (target ∈ {Taylor, Winston, Wags} — **cấm
  Mafee/DollarBill**, prompt lấy từ template có tên trong `mike/decision_templates/*.md`, không nhận text tự do),
  `paper_registry_set` (ghi field vào `paper_programs_registry.json`, có schema).
- **Cấm vĩnh viễn trong whitelist**: tạo/xoá `data/BOT_STOP`, sửa `trading_rules.json`, `secrets/**`,
  `approve_plan*`, mọi lệnh broker, crontab. Câu `risk=money` bỏ qua toàn bộ `on_answer` (chỉ đóng + báo).
- Validate lúc **ghi câu hỏi**: thêm check vào `append_event.sh` nhánh `question` — `on_answer` sai schema/action
  lạ ⇒ từ chối ghi (fail loud), để lỗi hiện ra khi hỏi chứ không phải khi user đã trả lời.
- Idempotent (§5 coding_guidelines): ledger `state/decision_inbox/actions.jsonl`, khoá
  `(question_event_id, option, action_index)`, ghi `started` trước khi gọi, `done/failed` ngay sau (tmp+`os.replace`
  cho file trạng thái). Gặp `started` không có `done` ⇒ **không chạy lại**, post `status decision-action-unknown`
  cho người xem (fail-safe pause).

## 5. Giám sát classifier trong `daily_retro.sh`

- Script mới `bin/classifier_denial_count.py --day YYYY-MM-DD [--agents Mike,Taylor,Wags] --json`:
  logic như `clf_count.py` (cùng thư mục) (đếm theo `tool_result`, map `tool_use_id → lệnh`), **bucket theo ngày ICT**
  (`ZoneInfo("Asia/Ho_Chi_Minh")`, §16) — bản đo ở §0 bucket theo UTC, cần chuyển.
- Output: `{"day","total","by_agent","by_cmd_top5"}`.
- `daily_retro.sh`: thêm 1 khối bằng chứng đọc-only vào draft (cùng chỗ `measured_by_warn_report.py`), và nếu
  `Mike > N` gọi `retro_escalate.py --pattern classifier-denials-mike --days 1 --payload …` (topic ổn định, không
  bộ đếm — đúng cổng `append_event.sh:122`).
- **N đề xuất = 5/ngày** — trên dữ liệu 14/10→13/11 sẽ bắn 4 ngày/30 (10-16:6, 10-29:8, 11-05:8, 11-13:6). Thêm
  điều kiện thứ hai: bất kỳ lần chặn nào trên `close_bus_question.py` ⇒ cảnh báo dù tổng ≤N (đó đúng ca 13/11).
- Selfcheck: fixture 3 jsonl (1 lần chặn lặp 2 dòng phải đếm 1; ca 23:30Z = ngày ICT hôm sau; file hỏng 1 dòng).

## 6. Kế hoạch từng bước

| # | Bước | File chạm | Verify | Công `ước lượng` |
|---|---|---|---|---|
| 1 | `close_bus_question.py --provenance-json` | `bin/close_bus_question.py`, `bin/bus_question_closure_selfcheck.py` | selfcheck cũ PASS + ca mới: key cấm bị từ chối, payload đọc lại có `provenance` | 0,5h |
| 2 | Bộ khớp xác định | mới `bin/decision_inbox.py` + `bin/decision_inbox_selfcheck.py` | ≥25 ca bảng (§7), chạy `env -u TZ` và `TZ=America/New_York` | 4h |
| 3 | Whitelist hành động | mới `bin/decision_actions.py`, `mike/decision_templates/`; nhánh validate trong `bin/append_event.sh` | selfcheck: action lạ bị từ chối lúc ghi; kill giữa chừng ⇒ không chạy lại; `money` bỏ qua on_answer; shellcheck gate | 3h |
| 4 | Thẻ `[#q…]` khi surface câu hỏi | `hooks/user_prompt_submit.sh` Mike hoặc chỉ dẫn Mike: mọi câu hỏi user kèm thẻ; tuỳ chọn `bin/surface_question.py` đăng qua `/api/notify` có thẻ | tin bot có thẻ ⇒ `surfaced.jsonl` có map | 1h |
| 5 | Cog | mới `mike/ccdb_cogs/decision_inbox_cog.py` (+ `_selfcheck` với `discord.Message` giả) | load thử bằng `load_custom_cogs` trong venv bridge, không token | 2h |
| 6 | Bật | `.env` ccdb-mike: `CUSTOM_COGS_DIR`, `DECISION_INBOX_USER_IDS`, `DECISION_INBOX_MODE=shadow` | **shadow 5 phiên**: chỉ ghi "sẽ đóng X" lên bus `status`, không đóng; so với quyết định thật của user; 0 sai ⇒ `live` (user duyệt) | 0,5h + 5 ngày quan sát |
| 7 | Lưới đối soát | `daily_retro.sh`: số tin khớp ngữ pháp mà không ràng buộc được, số đóng tự động, số hỏi lại | đọc retro 3 ngày đầu | 0,5h |
| 8 | Classifier monitor | §5 | selfcheck §5 | 1,5h |
| 9 | arch-reviewer (Agent tool) trên toàn bộ diff trước khi bật live | — | APPROVED | — |

Tổng `ước lượng` ~13h code + 5 ngày shadow. Thứ tự giao: 1 → 2 → 8 (độc lập, giá trị ngay) → 3 → 4 → 5 → 6.

## 7. Selfcheck bắt buộc (bảng ca cho `decision_inbox_selfcheck.py`)
1. `Duyệt A` reply-to tin có thẻ câu money ⇒ đóng, `matched_by=reply_to`, `decided_by=user`.
2. `A` trần trong thread có 2 câu mở được surface ⇒ không đóng, hỏi lại 1 lần; gửi `A` lần 2 ⇒ **không hỏi thêm**.
3. `A` trần, thread không có câu nào surface ⇒ không làm gì, không hỏi.
4. `A` trần, thread chỉ 1 câu normal ⇒ đóng (`thread`); cùng tình huống câu money ⇒ hỏi lại.
5. `C` cho câu chỉ có A/B ⇒ hỏi lại.
6. `A nhưng sửa ngưỡng` ⇒ không khớp ngữ pháp.
7. Author ngoài `DECISION_INBOX_USER_IDS` ⇒ bỏ qua; biến rỗng ⇒ cog không hoạt động.
8. Câu đã đóng giữa lúc khớp và lúc gọi ⇒ `ALREADY_CLOSED_OR_UNKNOWN`, không lỗi.
9. Topic chứa topic khác (bẫy substring) ⇒ helper rc=5 ⇒ không đóng, báo.
10. Options không tiền tố + câu money ⇒ không đóng.
11. `on_answer` cho câu money ⇒ không chạy; action lạ ⇒ bị `append_event.sh` từ chối lúc ghi.
12. Kill sau `started` ⇒ lần sau không chạy lại action.
13. `#q` trỏ câu không tồn tại ⇒ không làm gì.
Bus thật không bị đụng: selfcheck dùng `--root` tmpdir (như `close_bus_question.py --root`), và đặt
`MIKE_BOT_TEST_MODE=1`.

## 8. Đề xuất allow-list cho `agents/Mike/.claude/settings.json` — CHỈ VĂN BẢN, KHÔNG ÁP DỤNG

Giả định cần user kiểm sau khi thêm (chưa đo): ở `permission_mode=auto`, luật `allow` khớp được xử lý trước
classifier. Verify: chạy 1 lệnh trong danh sách ở phiên Mike, xác nhận không có dòng `denied by … classifier`
mới (đếm bằng script §5). Lệnh nên gọi bằng **đường dẫn tuyệt đối, không bọc `cd …;`** để khớp mẫu.

| Luật đề xuất | Rủi ro | Ghi chú |
|---|---|---|
| `Bash(python3 /home/trido/thanhdt/WorkingClaude/mike/bin/close_bus_question.py *)` | TRUNG BÌNH | Có thể đóng sai/gắn `--decided-by-user` không thật; giảm bởi guard rc=4/5 + audit provenance. Sau khi Decision Inbox live, đường user-decided đi qua cog, Mike chỉ dùng cho đóng-bằng-artifact. |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/append_event.sh *)` | THẤP–TB | Append-only, có validate JSON; rủi ro là ghi `answer`/`decision` giả — truy được vì mọi event có agent+ts. |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/remember.sh *)` | THẤP | Chỉ working memory của agent. |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh *)` | THẤP–TB | Đăng Discord nội bộ; bẫy đã biết: cờ lạ (`--help`) bị gửi thành text. |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/jobs.sh claim-reply *)` | THẤP | |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/jobs.sh cancel *)` | TRUNG BÌNH | Huỷ được job đang chạy của agent khác (gồm job DollarBill lập plan). |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/verify_finding.sh *)` | THẤP | Skeptic đọc-only. |
| `Bash(/home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh *)` | **CAO** | Spawn agent với prompt tự do, gồm Mafee (đặt lệnh thật, plan-bound). **Nếu thêm thì PHẢI kèm deny**: `Bash(*dispatch.sh Mafee*)`, `Bash(*dispatch.sh DollarBill*)` (deny thắng allow). |
| `Edit(//home/trido/thanhdt/WorkingClaude/mike/kb/**)`, `Write(...kb/**)` | TRUNG BÌNH–CAO | KB được nạp vào mọi phiên cả fleet; §13 đòi `.proposed` khi chưa duyệt. **Khuyến nghị hẹp hơn**: `Write(//…/mike/kb/**/*.proposed)` + `Edit(//…/mike/kb/memory/Mike.md)` + `Edit(//…/mike/kb/incidents/**)`. Cổng pre-commit vẫn chặn khi commit. |

**KHÔNG nên allow** (classifier đang làm đúng việc): `approve_plan_simple.sh` (bị chặn 4 lần — đường tiền),
`clear_books_daily.sh`, `curl … /api/spawn`, mọi thứ chạm `data/BOT_STOP`, `data/trading_rules.json`, `secrets/**`.

**Phát hiện phụ trong settings hiện tại** (không sửa, báo user): đã có `Bash(git push --force*)` và
`Bash(crontab*)` trong `allow` — cả hai rủi ro CAO hơn mọi dòng đề xuất ở trên (force-push ghi đè lịch sử
backup; crontab thay toàn bộ lịch §11). Nên cân nhắc gỡ hoặc thu hẹp.

## 9. Việc tức thời (ngoài phạm vi thiết kế)
`Mike/nav-loss-brake-review-20261113` **vẫn mở** (audit 13/11). Thiết kế này không đóng nó; Mike/user đóng tay
bằng `close_bus_question.py … --decided-by-user --source-topic <thread>` kèm id tin nhắn "A" của user khi có.
