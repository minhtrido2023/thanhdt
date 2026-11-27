# OPS RUNBOOK — Vận hành trading hàng ngày (tự phát hiện → tự sửa → báo cáo)

> Mandate user 2026-07-07: *"quản lý hệ thống vận hành chung cho trading mỗi ngày, bất cứ
> khi nào phát sinh lỗi thì tự động fix bug, không thụ động chờ báo lỗi... tự fix rồi báo
> cáo lại"*. Đây là tài liệu chuẩn tắc: timeline mỗi ngày, mỗi bước kiểm tra gì, lỗi thì
> ai tự sửa, khi nào phải hỏi user. Mike đọc file này mỗi phiên; MỌI checker lỗi đều gọi
> `bin/ops_autofix.sh` thay vì chỉ cảnh báo suông.

## Playbooks theo tình huống — tách sang `kb/ops_runbook_playbooks/` (đọc khi gặp sự cố)

| Tình huống / Mục | Playbook OKF |
|---|---|
| Xử lý lỗi NAV, PRICE_XCHECK, Lệch nguồn cổ tức & Báo cáo ngày | [`ops_runbook_playbooks/nav-and-eod-gates.md`](ops_runbook_playbooks/nav-and-eod-gates.md) |
| Nơi kết quả đổ về (đọc mỗi sáng, KHÔNG cần user nhắc) | [`ops_runbook_playbooks/outputs-and-boot.md`](ops_runbook_playbooks/outputs-and-boot.md) |
| Boot — khởi động lại pipeline sau server downtime (≥1h, bao qua cron tối) | [`ops_runbook_playbooks/outputs-and-boot.md`](ops_runbook_playbooks/outputs-and-boot.md) |
| Phanh lỗ NAV — `nav_loss_brake_monitor.py` (CHỈ CẢNH BÁO) | [`ops_runbook_playbooks/nav-brake-and-market-state.md`](ops_runbook_playbooks/nav-brake-and-market-state.md) |
| Nhận tin "🟡 CỔNG DT5G SUY GIẢM" thì làm gì | [`ops_runbook_playbooks/nav-brake-and-market-state.md`](ops_runbook_playbooks/nav-brake-and-market-state.md) |
| Nhật ký & kinh nghiệm | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Headless agent bị classifier chặn git-write / BQ-write vào file production (tái diễn 09-27, 09-28) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Pattern B — fix THẬT đã merge nhưng câu hỏi bus không được đóng (tái diễn 08-13, 09-27, 09-28, 09-29 ×2) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Lược sử | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Classifier chặn headless agent ghi production / git merge (chốt phương án C, 2026-10-05) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Chạy TAY buổi sáng khi BQ xong muộn — `MIKE_MORNING_RUN=1` (thêm 2026-10-15, sau sự cố plan 15/10) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| VN-Index có cổ tức (vnindex_total_return) — đọc 🔒, ack, đính chính, undo (áp 2026-10-21) | [`ops_runbook_playbooks/nav-brake-and-market-state.md`](ops_runbook_playbooks/nav-brake-and-market-state.md) |
| Cổng DD trước plan LAG — Mike ghi ack + hợp đồng NO_PACK (thêm 2026-10-21, job Taylor_20261021_154311) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| Rollback LAG cache điều chỉnh (`97b2a7197`, LIVE từ 10/11/2026, user phê chuẩn 13/11) — thêm 2026-11-13 (job `Taylor_20261113_021438`) | [`ops_runbook_playbooks/workflow-and-gates.md`](ops_runbook_playbooks/workflow-and-gates.md) |
| NAV rc=2 "Tài sản phái sinh KHÔNG định giá được" — ký quỹ phái sinh (thêm 2026-11-17, branch feat/nav-deriv-margin-20261117, merge 8f51de633) | [`ops_runbook_playbooks/nav-brake-and-market-state.md`](ops_runbook_playbooks/nav-brake-and-market-state.md) |

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

### Verify tự thân của Wags KHÔNG được chạy dispatcher ở chế độ LIVE (2026-08-23)

Ca `coord-2026-08-23`: Wags verify 1 ack bằng cách chạy thẳng `bin/ops_health_check.sh` LIVE
từ bên trong chính job đang được dispatch — kết quả ghi bus event mạo danh Mike + gửi trùng
báo cáo Discord Chủ Nhật (script không tự biết hôm nay không phải ngày cron chạy), và nếu ack
không ăn thì chính lượt verify đó tự kích hoạt lại khối routing `wags_autofix.sh`, tạo tín hiệu
"tái diễn trong cooldown" giả — phép đo tự tạo ra cái nó đang đo.

**Luật: verify bất kỳ thay đổi nào chạm `ops_health_check.sh`/`ops_autofix.sh`/`wags_autofix.sh`
PHẢI dùng `OPS_HEALTH_DRY_RUN=1 bin/ops_health_check.sh --account <acct>` (khối đã có sẵn trong
script, dòng ~1423-1429), KHÔNG BAO GIỜ chạy live để "kiểm tra thử".** Cần trạng thái thật (đã
ghi bus/Discord chưa) thì đọc file/bus có sẵn (`logs/ops_health.log`, bus event cùng ngày), đừng
tái tạo bằng cách chạy lại chính bộ dispatcher.

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
| 09:00–14:55 | `bot_heartbeat.sh` /5' (per account) | Bot sống, có tiến triển fill | Chết → TỰ RESTART; restart fail → Telegram khẩn (có sẵn) ⚠ Restart KHÔNG `--once` là CỐ Ý: bot `--once` (run_bot.sh) exit trước 14:45, chỉ bot restart chạy loop mới vào CLOSED ⇒ chờ ATC (aria-K). Đừng thêm `--once` vào `_restart_bot`. |
| 11:30 | lunch pkill (per account) | Bot dừng nghỉ trưa | pkill fail vô hại (session_phase tự idle) |
| 12:45 | `ops_health_check.sh` lần 2 | Như 08:20 + bắt vấn đề phát sinh phiên sáng | Như 08:20 |
| 13:00 | `run_bot.sh` resume (per account) | Resume state, chạy phiên chiều | Như 09:05 |
| ~14:50 | phiên đóng (ATC) | Bot tự cancel lệnh treo, ghi `exec_*_report.md` | — (thực thi thật, autofix KHÔNG đụng) |
| 15:05 | `dc_book_waterfall_paper.py --update` | Paper sleeve DC-book cập nhật | Lỗi → autofix (paper, không chạm tiền thật) |
| 19:10 | `eod_trading_report.sh` (per account) | Report khớp lệnh + NAV verify-pipeline + đối soát broker≠state | Crash → autofix; kênh Discord hỏng → ĐÃ CÓ fallback Telegram+Trading Daily tự động; cổng tỉ suất CHẶN ⇒ mục "Báo cáo NGÀY bị cổng tỉ suất CHẶN" |
| 19:50 | `nav_snapshot_daily.sh` (mọi account live) | Đường ghi NAV thứ 2, độc lập EOD: chưa có dòng `nav_history` hôm nay ⇒ gọi `daily_nav_snapshot.py`; có rồi ⇒ bỏ qua | rc=2/timeout tự retry 2 vòng×5'; rc=4 ⇒ marker cho `nav_sync_retry`; **rc=5 ⇒ KHÔNG retry, escalate NGAY** (xem § NAV thiếu dòng mục 5); rc=2 hết retry / rc=3 ⇒ 🔴 Trading Daily, xử lý TAY (xem § NAV thiếu dòng) |
| Mỗi 10' | `watchdog.sh` | Session Mike sống, macro_health staleness (`staleness_watch.py`) | Tự restart/clear-bridge (có sẵn) |

> Chi tiết xử lý lỗi NAV (`nav_history`, `compute_active_nav` rc=5/6/7, `PRICE_XCHECK` rc=4), lệch nguồn cổ tức và cổng tỉ suất báo cáo ngày đã tách sang [`ops_runbook_playbooks/nav-and-eod-gates.md`](ops_runbook_playbooks/nav-and-eod-gates.md).

## Macro health — phân biệt 3 tầng khi FAILED (bài học 2026-07-06, 3 bug chồng nhau)

1. **BQ upstream thật** stale? → verify trực tiếp `bq query MAX(time)` — nếu stale thật:
   việc của data-ops (Winston), thường do daily_refresh/ingest hỏng.
2. **Cache cục bộ** (data/bq_cache) thối? → `sync_bq_cache.py --verify`; lệch → resync
   (autofix được). Nhớ: env có cache "verified" sẽ đọc cache, env cache-fail đọc BQ thật —
   2 env có thể cho 2 kết quả khác nhau với CÙNG câu query.
3. **Chính checker sai** (đường dẫn chết, nguồn sai)? → so kết quả checker với query tay
   cùng nguồn — nếu lệch: bug checker (autofix được).
   Fail-safe khi chưa rõ: hệ thống tự rơi về DT4_only (an toàn, chỉ mất lớp macro-cap).

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

**`_ext.md` size (OKF split, chủ: Wags)**: `kb_nightly.sh` cảnh báo (không chặn) qua
`notify.sh` khi bất kỳ `*_ext.md` nào >35KB (cùng tỉ lệ ngưỡng core 40KB) — split là xử lý
MẶC ĐỊNH của Phase 4.6 (mandate 2026-08-19) nên `_ext.md` không có trần tự nhiên. Hành động:
rà soát/nén tay khi cảnh báo tới, không có auto-fix cho ext (khác core — chưa rõ tách ext
tiếp về đâu). Không phải arch-review bắt buộc (chỉ đụng nội dung KB, không đụng tooling).

