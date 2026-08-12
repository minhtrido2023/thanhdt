# OPS RUNBOOK — Vận hành trading hàng ngày (tự phát hiện → tự sửa → báo cáo)

> Mandate user 2026-07-07: *"quản lý hệ thống vận hành chung cho trading mỗi ngày, bất cứ
> khi nào phát sinh lỗi thì tự động fix bug, không thụ động chờ báo lỗi... tự fix rồi báo
> cáo lại"*. Đây là tài liệu chuẩn tắc: timeline mỗi ngày, mỗi bước kiểm tra gì, lỗi thì
> ai tự sửa, khi nào phải hỏi user. Mike đọc file này mỗi phiên; MỌI checker lỗi đều gọi
> `bin/ops_autofix.sh` thay vì chỉ cảnh báo suông.

## Nguyên tắc phân quyền tự sửa (áp dụng mọi bước)

**Bảng dưới đây LÀ NGUỒN CHUẨN TẮC (canonical) cho ranh giới tự-sửa domain OPS/TRADING** —
`bin/ops_autofix.sh` (comment + prompt) và `bin/weekly_ops_audit.sh` chép LẠI nguyên văn nội
dung này vào prompt dispatch (bắt buộc, LLM headless cần thấy ranh giới trực tiếp trong
context, không thể chỉ "đọc file" đáng tin cậy bằng được nhắc thẳng) — **sửa bảng này thì PHẢI
sửa luôn 2 chỗ chép đó cùng lúc** (grep `TUYỆT ĐỐI\|CẤM tự sửa\|CẤM TUYỆT ĐỐI` trong `bin/*.sh`
để tìm hết các bản chép trước khi coi là xong).

| Loại vấn đề | Hành động |
|---|---|
| Bug code script report/check/pipeline/cache, cache thối, report không gửi được, lock/flag kẹt, daemon phụ trợ chết | **TỰ SỬA** (ops_autofix → Winston/fable) + verify + báo Trading Daily |
| Chạm tiền thật: trade plan, trading_rules.json, logic đặt lệnh executor/brokers, crontab dòng thực thi, xoá dữ liệu, BOT_STOP | **KHÔNG tự sửa** — escalate (bus `question` + Telegram) và dừng |
| Bot execution chết giữa phiên | `bot_heartbeat.sh` TỰ RESTART (có sẵn); restart fail → Telegram khẩn |
| Số liệu client-facing sai đã gửi | Sửa nguồn + GỬI ĐÍNH CHÍNH ngay kênh cũ (không im lặng sửa) |

Chống bão: mỗi vấn đề (label) chỉ autofix 1 lần/giờ — tái diễn trong cooldown = fix trước
chưa ăn → notify "cần người xem", không dispatch lặp vô hạn.

## Nguyên tắc phân quyền tự sửa — domain ĐIỀU PHỐI (Wags, KHÁC bảng trên)

**Canonical cho `bin/wags_autofix.sh`** (chép lại nguyên văn vào prompt dispatch Wags, cùng lý
do LLM-cần-thấy-trực-tiếp ở trên) — phạm vi HẸP HƠN NHIỀU bảng OPS/TRADING vì Wags là
Fleet Ops Coordinator, không chạm domain trading:

| Loại vấn đề | Hành động |
|---|---|
| Tooling điều phối: `dispatch.sh`/`jobs.sh`/`mike_json.py`/`ops_autofix.sh`/`wags_autofix.sh`/checker, sau khi test | **ĐƯỢC sửa** + verify artifact + arch-reviewer audit (rủi ro cao) hoặc sample-queue (rủi ro thấp, xem `wags_risk_tier.py`) |
| BẤT KỲ THỨ GÌ thuộc trading: plan/executor/cron thực thi/`trading_rules.json` | **TUYỆT ĐỐI không đụng** — không phải domain của Wags, kể cả khi trông như liên quan tới điều phối |

Chống bão: cùng cooldown 1h/label với bảng trên (`state/autofix/`, chung cơ chế).

### ĐÓNG bus question sau khi việc đã xong bằng HÀNH ĐỘNG (kỷ luật, 2026-08-10)

Câu hỏi `question` chỉ đóng được bằng `answer`/`decision` **GIỮ NGUYÊN topic gốc**. Checker
§5 fail-closed (đúng thiết kế) — nên việc "đã xong thật nhưng không ai post answer" khiến
`wags_autofix` bị dispatch 2 lần/ngày cho việc đã xong, cho tới khi câu hỏi rơi khỏi cửa sổ 48h.

- **Ai giải quyết thì người đó đóng.** Sửa xong / restart xong / gửi báo cáo xong → post
  `answer` cùng topic kèm **bằng chứng artifact** (dòng journal, file trên đĩa, output lệnh),
  không phải self-report kiểu "tôi đã làm xong".
- **Máy hỏi thì máy tự đóng.** Question do checker sinh ra (không có chủ sở hữu là người) phải
  có đường tự đóng khi artifact xuất hiện — mẫu: `check_report_cadence.sh` quét bus, thấy
  `target_file` đã tồn tại thì post `answer` (idempotent theo "đã có answer cùng topic chưa").
  Thêm checker mới sinh `question` → phải kèm cơ chế đóng tương ứng.
- **Hỏi lại lần 2/lần 3 cho CÙNG một việc thì dùng CÙNG topic** (hoặc ack), đừng đặt topic mới
  (`...-lan2`): mỗi topic mới = 1 mục pending riêng, nhân số lần auto-dispatch lên.
- Ca thật 2026-08-10: 4 question tồn đọng → cả 4 đã xong từ trước (bot ZaloPay restart lúc
  10:35, báo cáo tuần đã có trên đĩa từ 11:49), chỉ thiếu event đóng.

### Checker TRA CỨU sai cũng ra đúng triệu chứng đó (2026-08-11) — 3 luật cho người viết checker

Cùng triệu chứng "báo động treo nhiều ngày dù việc đã xong", nhưng root cause nằm trong CHÍNH
checker: nó tra không ra bằng chứng rồi báo như thể việc chưa xong. Ba luật, mỗi luật là 1 ca thật:

- **Producer nối chữ tự do vào topic → tra bằng PREFIX, đừng tra tuyệt đối.** `mike_json.py
  has-event` khớp topic TUYỆT ĐỐI (cố ý — 3 caller khác có producer ghi topic cố định:
  `weekly_ops_audit.sh`, `fearbuy_weekly_scan.sh`, `eod_trading_report.sh`). Nhưng prompt của
  `wags_autofix.sh` yêu cầu topic *bắt đầu bằng* `wags-fix: <label>` và Wags LUÔN nối mô tả phía
  sau ⇒ không bao giờ khớp ⇒ mỗi lần chạy lại báo 🟡 "Wags KHÔNG ghi finding" dù finding nằm ngay
  trên bus (08-04→08-11). Dùng **`has-event-prefix`** cho loại producer này (đã có sẵn từ 08-11).
- **"Tra không ra" ≠ "tra ra và kết luận xấu" — phải là 2 tín hiệu KHÁC NHAU.** Gộp 2 thứ vào
  một đường báo động thì người đọc mặc định hiểu là kết luận xấu, và lỗi tooling chạy ẩn hàng
  tuần. `wags_autofix.sh` giờ tách: `NEEDS_CHANGES`/`REFUTED` (arch-reviewer ĐỌC rồi bác) →
  question `wags-fix-not-confirmed:` như cũ; `INCONCLUSIVE`/rỗng (chuỗi kiểm chứng không ra phán
  quyết) → question **`wags-arch-review-inconclusive:`** + nói thẳng "KHÔNG phải arch-reviewer bác
  fix", kèm bằng chứng finding của Wags có trên bus hay không.
  ⚠️ **Tách nhánh question mới thì PHẢI thêm tiền tố đó vào `WAGS_SELF_Q_PREFIXES`**
  (`bin/ops_health_check.sh`) **CÙNG LÚC.** Chính bản tách 08-11 đã quên bước này: question
  `wags-arch-review-inconclusive:` rơi vào `pending_q` → COORD_WARN → tự dispatch `wags_autofix`
  mỗi chu kỳ checker cho ĐÚNG issue vừa không ra phán quyết, và job đó lại đẻ question cùng loại —
  đúng vòng tự nuôi audit §14 (2026-07-31) tưởng đã đóng. Câu hỏi do CHÍNH pipeline sinh ra là
  OUTPUT của vòng lặp; đưa lại vào INPUT là phản hồi dương. Selfcheck ca 11b
  (`ops_health_check_selfcheck.py`) so danh sách này với bản thật, quên là FAIL.
- **Verdict lấy từ ARTIFACT (bus), đừng lấy từ stdout của pipe.** stdout đã nhiễu thật 2 lần
  (2026-07-08 `notify_thread.sh` in `{"status":"sent"}` → 2 question giả; 2026-07-22T05:55Z
  INCONCLUSIVE, 8 ngày sau đóng lại là FALSE_ALARM). `bin/wags_bus_verdict.py` đọc verification
  arch-reviewer ghi deterministic trên bus; chỉ dùng để NÂNG lên CONFIRMED khi stdout hỏng, không
  bao giờ dùng để hạ (bus im lặng = thiếu bằng chứng, giữ nguyên đường báo động).
  **Nhưng luật một chiều thì phải canh cả chiều còn lại**: stdout=CONFIRMED mà bus nói KHÁC
  (2 nguồn lẽ ra cùng một `verdict_json`) trước 08-12 đi thẳng vào ✅ HOÀN TẤT trong im lặng. Nay
  vẫn KHÔNG tự hạ verdict, nhưng đổi ✅→🟠 + ghi pipelog để người đối chiếu. Nguyên tắc chung: mỗi
  lần thêm một luật "chỉ X, không Y", hỏi ngay ca Y xảy ra thì ai thấy.

⚠️ Trước khi kết luận "báo động lặp = tooling hỏng": **đọc log/verdict thật của lần escalate đó**.
Verdict có chẩn đoán cụ thể (trích đúng dòng code, tái lập được lỗi) là review THẬT — phải sửa,
không được đóng bằng lý do "false alarm do bug tra cứu". Ca thật: 2 question
`wags-fix-not-confirmed: coord-2026-08-10 / coord-2026-08-11` từng bị nghi là do bug prefix ở trên,
kiểm lại thì cả 2 đều là `NEEDS_CHANGES` có bằng chứng — vẫn đang mở, cần round-2.

## Timeline ngày giao dịch (T2–T6, giờ ICT) — bước / kiểm tra gì / lỗi thì sao

| Giờ | Bước (cron) | Kiểm tra | Khi lỗi |
|---|---|---|---|
| 18:30 (chiều trước) | `daily_refresh_v34b_linux.sh` | v3.4b base + DT5G publish tới BQ, macro_health.json HEALTHY | Log `!!! ABORT` → autofix; macro_health FAILED kéo dài → xem mục "Macro health" dưới |
| 19:00 (tối trước) | `bq_freshness_check.sh` | BQ fresh → pipeline EOD → dispatch DollarBill lập plan T+1 **cho MỌI account live** | STALE → block DollarBill + alert (có sẵn); dispatch fail → check `bus/jobs`, circuit breaker |
| 20:30 (tối trước) | `inject_discretionary_orders.sh` | Chèn lệnh gom DISCRETIONARY_SPECIAL (vd TV1 tranche) vào plan T+1 sau khi DollarBill ghi, trước gửi plan | — |
| 21:00 (tối trước) | `send_plan_report.sh` (per account) | Plan T+1 TỒN TẠI THẬT, đúng ngày, đúng schema (verify artifact, không tin job status) | Escalate bus `question` + Telegram (có sẵn) — plan cần user duyệt, KHÔNG tự tạo |
| 23:00 (tối trước) | `send_plan_report.sh --second-chance` (per account) | Re-send idempotent nếu plan sửa sau 21:00 chưa được gửi lại | Như 21:00 |
| 23:45 (đêm trước) | `sync_bq_cache_daily.sh` | **Cache verified OK toàn bộ bảng** (không chỉ preflight) | Verify FAILED → **autofix tự động** (đã wire 2026-07-07) — bài học: cache thối âm thầm 10 ngày gây false-SEV1 |
| 04:30 | `selfcheck_weekly_baseline_check.sh` (**tên di sản — nhịp thật là NGÀY từ 2026-08-12**) | Chạy 93 selfcheck production HEAD (gốc `WorkingClaude/` + `mike/bin/`) bằng `$DNA_PYEXE` + env theo `kb/selfcheck_baseline.json.required_env`, diff `known_red` | ĐỎ MỚI → 1 bus `question` `selfcheck-red: <file>` + ack + Discord `architecture`, **1 lần/ca** (ghi vào `known_red` nên không báo lại); xanh lại → tự đăng `answer` đóng vòng. **Wags KHÔNG tự sửa selfcheck giao dịch** — chủ sở hữu file / user quyết |
| 08:20 | `ops_health_check.sh` (per account) | BOT_STOP, xung đột file plan, lỗi lặp journal, circuit breaker, question tồn, đối chiếu preflight | WARN > 0 → **autofix tự động** (wire 2026-07-07) + vẫn post cảnh báo như cũ |
| 08:45 | `preflight_check.sh` (per account) | Plan hôm nay tồn tại + approved + macro_health + Gmail OTP + BQ lag | RED vì plan thiếu/chưa duyệt → USER phải xử lý (không autofix); RED vì hạ tầng → autofix |
| 09:05 | `run_bot.sh` (per account) | Bot chạy, đặt lệnh theo plan | — (thực thi thật, autofix KHÔNG đụng) |
| 09:00–14:55 | `bot_heartbeat.sh` /5' (per account) | Bot sống, có tiến triển fill | Chết → TỰ RESTART; restart fail → Telegram khẩn (có sẵn) |
| 11:30 | lunch pkill (per account) | Bot dừng nghỉ trưa | pkill fail vô hại (session_phase tự idle) |
| 12:45 | `ops_health_check.sh` lần 2 | Như 08:20 + bắt vấn đề phát sinh phiên sáng | Như 08:20 |
| 13:00 | `run_bot.sh` resume (per account) | Resume state, chạy phiên chiều | Như 09:05 |
| ~14:50 | phiên đóng (ATC) | Bot tự cancel lệnh treo, ghi `exec_*_report.md` | — (thực thi thật, autofix KHÔNG đụng) |
| 15:05 | `dc_book_waterfall_paper.py --update` | Paper sleeve DC-book cập nhật | Lỗi → autofix (paper, không chạm tiền thật) |
| 19:10 | `eod_trading_report.sh` (per account) | Report khớp lệnh + NAV verify-pipeline + đối soát broker≠state | Crash → autofix; kênh Discord hỏng → ĐÃ CÓ fallback Telegram+Trading Daily tự động |
| Mỗi 10' | `watchdog.sh` | Session Mike sống, macro_health staleness (`staleness_watch.py`) | Tự restart/clear-bridge (có sẵn) |

## Nơi kết quả đổ về (đọc mỗi sáng, KHÔNG cần user nhắc)

- **Trading Daily** (1521470705563340910): mọi alert vận hành sống + báo cáo autofix.
- **Trading report** (1522576692638388364): report EOD/tuần/tháng. ⚠️ private thread — bot
  rớt membership khi archive; nếu 403 Missing Access → nhờ user @mention bot trong topic
  (đã có fallback tự động trong lúc chờ).
- **DollarBill plan channel** (1521183164364754974): plan T+1 + mọi record duyệt plan.
- Bus `question` events = việc CHỜ USER — Mike phải chủ động trình user, không để tồn >48h
  (ops_health_check tự bắt).
- **QUY ƯỚC ĐÓNG question** (bắt buộc, fix Wags 2026-07-21): để `ops_health_check.sh` gỡ 1
  question khỏi backlog, event đóng (`answer` HOẶC `decision`) PHẢI mang topic **chứa nguyên
  topic của question** — hoặc y hệt, hoặc thêm hậu-tố trạng thái (`…-closed` / `…-confirmed`
  / `… [RESOLVED]`). Checker khớp 1 chiều: `resolver ⊇ topic-hỏi`. Đóng bằng topic KHÁC HẲN
  (vd question `deposit-rate-refresh-question` đóng bằng answer `deposit-rate-refresh` cụt
  đuôi, hoặc bằng decision chủ đề rời) → checker KHÔNG thấy → question "tồn đọng" vĩnh viễn
  → spawn Wags vô nghĩa. Trước 2026-07-21 checker so topic BẰNG NHAU TUYỆT ĐỐI nên cả hậu-tố
  `-closed` cũng trượt (7 answer trên bus dính lỗi này).
- **Event đóng phải xuất hiện SAU question** (fix Wags 2026-07-30 round2, arch-reviewer
  required_change #1): `_resolved()` giờ so `resolver.ts >= question.ts`. Vì sao bắt buộc —
  nhiều alert TỰ ĐỘNG LẶP dùng topic **không có ngày**, nên chỉ cần đóng MỘT lần bằng hậu-tố
  là mọi lần alert TƯƠNG LAI bị pre-resolve vĩnh viễn (checker mù luôn):
  | Topic alert lặp (không có ngày) | Emitter |
  |---|---|
  | `plan-t1-not-ready-<ACCOUNT>` | `bin/send_plan_report.sh:380` |
  | `ops-autofix-unresolved: ops-health-<ACCOUNT>` | `bin/ops_autofix.sh:168` |
  Sự cố thật: ZaloPay mù từ answer Winston 2026-07-14, SpaceX mù từ đợt vệ sinh
  coord-2026-07-30 — 2 alert `plan-t1-not-ready-ZaloPay` (07-24) chỉ hiện lại SAU khi thêm
  so-ts. Ai thêm topic question mới cho alert lặp: **nên nhúng ngày vào topic** (vd
  `plan-t1-not-ready-SpaceX-2026-07-30`); sửa emitter thuộc surface trading → escalate cho
  owner, Wags không tự sửa.
- **KHÔNG có auto-expire** (Wags 2026-07-31): question chưa ai trả lời thì ở LẠI danh sách
  TREO LÂU vô thời hạn — checker KHÔNG tự đóng theo thời gian. Chỉ `answer`/`decision` của
  NGƯỜI mới đóng được. ⚠️ "Ở lại danh sách" ≠ "luôn được IN ra": xem chính sách in ở gạch
  đầu dòng *Question TREO LÂU* bên dưới — đừng để runbook hứa nhiều hơn code. **Điều này CHỈ đúng vì check #5 quét cả `bus/inbox/archive/*.jsonl.gz`** (Wags
  2026-07-31 round-4): `kb_nightly.sh` Phase 1b2 (`EVENT_KEEP_DAYS=30`) chuyển MỌI event
  >30 ngày khỏi hot inbox sang archive nén, KHÔNG lọc `event_type` — nên trước fix này có
  một **cliff 30 ngày IM LẶNG** ở kb_nightly (không WARN, không dấu vết) dù checker đã gỡ
  hết horizon. Đã xảy ra THẬT: `Wendy/confirm-dnse-phs-margin-thresholds` (06-22) và
  `Taylor/cache-stability go-live blocker` (06-27) biến mất khỏi mọi kênh dù CHƯA TỪNG được
  trả lời; sau fix cả hai hiện lại ở dòng TREO LÂU (38d/34d). Ai đổi Phase 1b2 hoặc đường
  dẫn archive: phải cập nhật glob của check #5 cùng lúc — ràng buộc này giờ được **khoá bằng
  test**, không còn bằng văn xuôi: `bin/ops_health_check_selfcheck.py` (dựng archive theo
  đúng layout Phase 1b2 rồi assert question >30d VẪN hiện), chạy mỗi đêm ở `kb_nightly.sh`
  Phase 0 (alert-only, không gate prune). Selfcheck trích code thật giữa 2 marker
  `# CHECK5_BEGIN` / `# CHECK5_END` trong `ops_health_check.sh` — xoá/đổi marker là test đỏ.
- **Đường lỗi ĐỌC không được im lặng** (Wags 2026-08-01 round-5): file bus/archive hỏng
  (gz cắt cụt, đang ghi dở) → check #5 bỏ qua file đó nhưng PHÁT WARN đếm rõ file nào; và
  nếu `bus/inbox/archive/` tồn tại mà glob `*.jsonl.gz` khớp 0 file (dấu hiệu Phase 1b2 đổi
  layout) cũng WARN. Cả hai WARN này **không** mang `[WARN-ONLY]` → route về `COORD_WARN`
  (Wags sửa), vì đó là lỗi tooling sửa được chứ không phải backlog chờ user.
- **Dọn `bus/inbox/archive/`: KHÔNG BAO GIỜ DỌN TỰ ĐỘNG** (quyết định Wags 2026-08-01,
  required_change #4). Không có cron/script nào xoá archive; đây là bản ghi lịch sử bus duy
  nhất còn lại sau khi Phase 1b2 prune hot inbox, và check #5 phụ thuộc nó để không dựng lại
  cliff 30d. Chi phí: check #5 đọc TOÀN BỘ archive 2 lần mỗi lần chạy (2 pass), 4 lần/ngày
  (2 khung giờ × 2 account). Mốc hiện tại 2026-08-01: ~778 event / **252KB nén**, full run
  5.4s — tăng ~250KB nén/tháng. **Mốc phải xem lại: archive >20MB nén hoặc check #5 >15s**
  → khi đó mới bàn nén theo năm / index riêng, KHÔNG xoá event.
  (Bản 07-30 từng auto-close sau 30 ngày bằng 1 `decision` "EXPIRED-30d" ghi dưới
  `agent_id=Mike`; arch-reviewer NEEDS_CHANGES high bác: check #5 là kênh backlog DUY NHẤT của
  fleet → sau EXPIRED question biến mất khỏi mọi báo cáo, chỉ hoãn chết-im 48h→30d, lại để MÁY
  quyết thay người trên escalation tiền thật và ô nhiễm KB. Đã gỡ hẳn khối đó.)
- **Marker `[WARN-ONLY]`** (required_change #5): dòng WARN mang tiền tố này bị loại khỏi CẢ
  `COORD_WARN` và `OTHER_WARN` → không spawn agent. Phân luồng dispatch bám MARKER, không bám
  câu chữ tiếng Việt (đổi wording WARN trước đây âm thầm đổi routing; topic tự do nhúng trong
  dòng chứa "Circuit breaker"/"Job board:" từng kéo cả dòng vào COORD_WARN → dispatch oan).
- **ACK `triaged-needs-human:`** (thêm Wags 2026-08-03): câu hỏi <48h mà đã triage và kết
  luận "chỉ NGƯỜI/thời gian quyết được, không có fix tooling" trước đây vẫn nằm trong
  `pending_q` → `COORD_WARN` → `wags_autofix` bị dispatch LẠI 2 lần/ngày cho tới khi câu hỏi
  quá 48h mới rơi vào nhánh TREO LÂU (vốn đã `[WARN-ONLY]` vì ĐÚNG lý do đó). Ca thật
  2026-08-03: cùng 2 câu hỏi bị triage 01:20, Mike xác nhận lại 02:38, checker vẫn đốt thêm
  1 job Wags lúc 05:45. Cách dùng — agent triage ghi 1 event:
  `append_event.sh <id> status "triaged-needs-human: <topic câu hỏi gốc>" '<lý do>'`.
  Khớp CHÍNH XÁC topic (hoặc dạng `Agent/topic` copy thẳng từ báo cáo) và ack phải đăng SAU
  câu hỏi. Nó **chỉ tắt auto-dispatch**: không đụng `resolvers`/`_resolved()`, không đóng câu
  hỏi, không giấu khỏi báo cáo — chỉ chuyển sang dòng `[WARN-ONLY] … ĐÃ TRIAGE, chờ NGƯỜI
  quyết`. Fail-closed: không ack (hoặc ack sai topic/sai thứ tự thời gian) → dispatch như cũ.
  Không cần hạn dùng: quá 48h câu hỏi tự sang nhánh TREO LÂU (cũng WARN-ONLY). Khoá bằng
  regression ca 12–13 trong `bin/ops_health_check_selfcheck.py` (2 mutation độc lập đều đỏ).
  - **`suppress_days` cho topic TÁI PHÁT** (Wags 2026-08-11): ack mặc định chỉ phủ ĐÚNG
    instance câu hỏi đang có. Topic do CRON tự phát lại y nguyên mỗi đêm sinh câu hỏi ts MỚI
    hơn ack ⇒ ack hết tác dụng ⇒ đốt thêm 1 job `wags_autofix` để kết luận lại y hệt (ca thật:
    `Mike/context-bloat-same-day` phát lại 08-01 → 08-05 → 08-10 cho CÙNG một quyết định A/B
    Wags đã triage 08-06 mà người chưa trả lời). Khai `{"suppress_days": N}` trong payload ack
    để phủ cả các lần phát lại CÙNG topic trong N ngày:
    `append_event.sh Wags status "triaged-needs-human:<topic>" '{"suppress_days":7,"note":"..."}'`.
    Trần cứng `ACK_MAX_SUPPRESS_DAYS = 14` (không ack nào tắt dispatch vĩnh viễn); payload
    hỏng / N không phải số / N≤0 / hết cửa sổ → rơi về cửa sổ 0 = hành vi cũ (fail-closed).
    Vẫn **chỉ tắt auto-dispatch**, câu hỏi vẫn in `[WARN-ONLY]`. Khoá bằng ca 14–15 selfcheck.
    `bin/bus_question_audit.py` (báo cáo TUẦN) CỐ Ý không biết tới ack — nó liệt kê mọi câu hỏi
    chưa có resolver, nên ack không làm backlog biến mất khỏi kênh audit.
  - **Ngoại lệ "self-ack tại nguồn" — ĐIỀU KIỆN NGẶT** (Wags 2026-08-06, arch-reviewer
    NEEDS_CHANGES high coord-2026-08-05): một script alert được phép TỰ ack câu hỏi nó tự
    phát **chỉ khi** (a) chính nó dispatch owner đi xử lý, VÀ (b) dispatch trả về **thành
    công** (bắt exit code thật — `| tail -n` nuốt mất exit code, script không `set -e`).
    Dispatch hỏng ⇒ **KHÔNG ack, KHÔNG ghi cooldown**, phát thêm event `error`, để câu hỏi
    ở lại `pending_q` routable. Nếu không giữ điều kiện này, `ACK_PREFIX` quay về nghĩa gốc
    "đã có agent triage" và ack trở thành lời khẳng định SAI: dispatch hỏng + ack + cooldown
    = điểm mù đúng bằng thời gian cooldown, gỡ mất chính detector chủ động duy nhất.
    Tiền lệ nguy hiểm: nếu mọi nguồn alert đều tự ack thì `pending_q` routable rỗng vĩnh
    viễn và `wags_autofix` không còn gì để triage. Mẫu tham chiếu +
    regression: `bin/paper_checkpoint_escalation.sh` + `bin/paper_checkpoint_escalation_selfcheck.py`
    (13 assertion, chứng minh ĐỎ 5/5 trên bản code trước fix).
- **Question TREO LÂU >48h** (thêm Wags 2026-07-30): checker có dòng WARN riêng
  `⚠️ Câu hỏi TREO LÂU (>48h, chưa ai quyết)` cho question quá cửa sổ 48h mà vẫn chưa có
  answer/decision (KHÔNG có horizon thời gian — chỉ cắt theo ĐỘ DÀI DÒNG IN; nguồn quét =
  hot inbox **+ archive nén**, xem gạch đầu dòng auto-expire ở trên).
  **Chính sách IN (sửa Wags 2026-08-01 round-5)**: ≤10 mục → in ĐỦ; >10 mục → in 5 mục CŨ
  NHẤT + 5 mục giữa bị giấu + 3 mục MỚI NHẤT, kèm trỏ sang `bin/bus_question_audit.py` cho
  danh sách đầy đủ. Lý do đổi: pool này không bao giờ tự cạn (drain rate thực nghiệm = 0),
  bản cũ chỉ in 5 mục CŨ NHẤT nên chỉ cần thêm 2 zombie già hơn là escalation tiền thật MỚI
  (vd `Taylor/DGC ZaloPay 46,8% NAV`, 7d) bị đẩy vào "…và N mục khác" — tức đổi một cliff-30d
  im lặng lấy một crowd-out im lặng. Khoá bằng test ở `ops_health_check_selfcheck.py`. Trước đó question >48h RƠI KHỎI radar hoàn toàn → chết
  im, không owner (vd `Winston/dt5g-live-2-writer-can-quyet` 07-29 sẽ vô hình từ 07-31).
  Dòng này **CỐ TÌNH không dispatch autofix** (loại khỏi cả `COORD_WARN` và `OTHER_WARN`):
  loại question này chỉ USER quyết được, spawn Wags/Winston lặp là token thuần lãng phí — nó
  chỉ cần hiện trong báo cáo Trading Daily để người thấy. Muốn dòng ngắn lại → đóng question
  đã xong theo QUY ƯỚC ĐÓNG ở trên (đúng việc Wags làm 2026-07-30: 6→2 mục).

## Macro health — phân biệt 3 tầng khi FAILED (bài học 2026-07-06, 3 bug chồng nhau)

1. **BQ upstream thật** stale? → verify trực tiếp `bq query MAX(time)` — nếu stale thật:
   việc của data-ops (Winston), thường do daily_refresh/ingest hỏng.
2. **Cache cục bộ** (data/bq_cache) thối? → `sync_bq_cache.py --verify`; lệch → resync
   (autofix được). Nhớ: env có cache "verified" sẽ đọc cache, env cache-fail đọc BQ thật —
   2 env có thể cho 2 kết quả khác nhau với CÙNG câu query.
3. **Chính checker sai** (đường dẫn chết, nguồn sai)? → so kết quả checker với query tay
   cùng nguồn — nếu lệch: bug checker (autofix được).
   Fail-safe khi chưa rõ: hệ thống tự rơi về DT4_only (an toàn, chỉ mất lớp macro-cap).

## Nhật ký & kinh nghiệm

- Mọi sự cố ảnh hưởng workflow sống → **1 file mới** trong `kb/incidents/<YYYY-MM>/` (blameless,
  có commit hash) + 1 dòng trong `kb/incidents/index.md`. KHÔNG append vào `kb/INCIDENTS.md` (STUB).
- Fix xong PHẢI verify artifact thật (chạy lại checker, đối chiếu số thật) — không tin
  self-report của agent/job status (MIKE.md §Quy chuẩn #2).
- Số đã gửi cho user mà phát hiện sai → đính chính NGAY trên kênh đã gửi, không âm thầm sửa.
- Bug ở 1 script → grep các script khác làm việc TƯƠNG TỰ (bài học 07-06: 3 bug cùng dạng
  "logic trùng lặp không đồng bộ" trong 1 ngày).

## Lược sử
2026-07-07: viết lần đầu + wire autofix vào ops_health_check.sh & sync_bq_cache_daily.sh
(sau chuỗi sự cố 07-06: EOD crash, NAV sai 2 lần, cache thối 10 ngày, false-SEV1 macro).

## Phân domain tự sửa lỗi (cập nhật 2026-07-07 tối — thêm Wags + arch-reviewer)

| Domain | Fixer | Reviewer | Cơ chế |
|---|---|---|---|
| Vận hành TRADING/data/pipeline/report (cache thối, report crash, BQ stale...) | Winston | — (quant-skeptic cho finding R&D) | `bin/ops_autofix.sh` |
| ĐIỀU PHỐI giữa agent (dispatch treo/timeout, circuit breaker, question tồn, job board, bus, notification routing) | **Wags** | **arch-reviewer** (bắt buộc, tự động) | `bin/wags_autofix.sh` |

`wags_autofix.sh` pipeline: Wags chẩn đoán + sửa (ranh giới: chỉ tooling điều phối, không
trading) → arch-reviewer (`~/.claude/agents/arch-reviewer.md`, fable, 7 hướng tấn công
kiến trúc) audit → **báo hoàn tất vào TOPIC ARCHITECTURE (1521475726329516122)**:
CONFIRMED = ✅ xong; NEEDS_CHANGES/REFUTED = ⚠ cần người xem + bus question (không tự lặp
vòng 2 — chống ping-pong). Review ad-hoc 1 finding Wags: `wags_autofix.sh --review-topic
"<substr>"`. `ops_health_check.sh` tự route: cảnh báo circuit-breaker/question → Wags,
còn lại → Winston.
