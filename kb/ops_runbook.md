# OPS RUNBOOK — Vận hành trading hàng ngày (tự phát hiện → tự sửa → báo cáo)

> Mandate user 2026-07-07: *"quản lý hệ thống vận hành chung cho trading mỗi ngày, bất cứ
> khi nào phát sinh lỗi thì tự động fix bug, không thụ động chờ báo lỗi... tự fix rồi báo
> cáo lại"*. Đây là tài liệu chuẩn tắc: timeline mỗi ngày, mỗi bước kiểm tra gì, lỗi thì
> ai tự sửa, khi nào phải hỏi user. Mike đọc file này mỗi phiên; MỌI checker lỗi đều gọi
> `bin/ops_autofix.sh` thay vì chỉ cảnh báo suông.

## Nguyên tắc phân quyền tự sửa (áp dụng mọi bước)

| Loại vấn đề | Hành động |
|---|---|
| Bug code script report/check/pipeline/cache, cache thối, report không gửi được, lock/flag kẹt, daemon phụ trợ chết | **TỰ SỬA** (ops_autofix → Winston/fable) + verify + báo Trading Daily |
| Chạm tiền thật: trade plan, trading_rules.json, logic đặt lệnh executor/brokers, crontab dòng thực thi, xoá dữ liệu, BOT_STOP | **KHÔNG tự sửa** — escalate (bus `question` + Telegram) và dừng |
| Bot execution chết giữa phiên | `bot_heartbeat.sh` TỰ RESTART (có sẵn); restart fail → Telegram khẩn |
| Số liệu client-facing sai đã gửi | Sửa nguồn + GỬI ĐÍNH CHÍNH ngay kênh cũ (không im lặng sửa) |

Chống bão: mỗi vấn đề (label) chỉ autofix 1 lần/giờ — tái diễn trong cooldown = fix trước
chưa ăn → notify "cần người xem", không dispatch lặp vô hạn.

## Timeline ngày giao dịch (T2–T6, giờ ICT) — bước / kiểm tra gì / lỗi thì sao

| Giờ | Bước (cron) | Kiểm tra | Khi lỗi |
|---|---|---|---|
| 18:30 (chiều trước) | `daily_refresh_v34b_linux.sh` | v3.4b base + DT5G publish tới BQ, macro_health.json HEALTHY | Log `!!! ABORT` → autofix; macro_health FAILED kéo dài → xem mục "Macro health" dưới |
| 19:00 (tối trước) | `bq_freshness_check.sh` | BQ fresh → pipeline EOD → dispatch DollarBill lập plan T+1 **cho MỌI account live** | STALE → block DollarBill + alert (có sẵn); dispatch fail → check `bus/jobs`, circuit breaker |
| 20:30 (tối trước) | `inject_discretionary_orders.sh` | Chèn lệnh gom DISCRETIONARY_SPECIAL (vd TV1 tranche) vào plan T+1 sau khi DollarBill ghi, trước gửi plan | — |
| 21:00 (tối trước) | `send_plan_report.sh` (per account) | Plan T+1 TỒN TẠI THẬT, đúng ngày, đúng schema (verify artifact, không tin job status) | Escalate bus `question` + Telegram (có sẵn) — plan cần user duyệt, KHÔNG tự tạo |
| 23:00 (tối trước) | `send_plan_report.sh --second-chance` (per account) | Re-send idempotent nếu plan sửa sau 21:00 chưa được gửi lại | Như 21:00 |
| 23:45 (đêm trước) | `sync_bq_cache_daily.sh` | **Cache verified OK toàn bộ bảng** (không chỉ preflight) | Verify FAILED → **autofix tự động** (đã wire 2026-07-07) — bài học: cache thối âm thầm 10 ngày gây false-SEV1 |
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
- **Hết hạn 30 ngày phải có DẤU VẾT** (required_change #4): question vượt horizon 30d không
  còn im lặng biến mất — checker phát 1 `decision` topic
  `<topic-hỏi> — EXPIRED-30d-khong-ai-tra-loi` (đóng theo HẾT HẠN, KHÔNG phải đã trả lời) và
  in 1 dòng WARN-only. Idempotent nhờ chính quy ước hậu-tố. Vẫn cần quyết → mở question MỚI.
- **Marker `[WARN-ONLY]`** (required_change #5): dòng WARN mang tiền tố này bị loại khỏi CẢ
  `COORD_WARN` và `OTHER_WARN` → không spawn agent. Phân luồng dispatch bám MARKER, không bám
  câu chữ tiếng Việt (đổi wording WARN trước đây âm thầm đổi routing; topic tự do nhúng trong
  dòng chứa "Circuit breaker"/"Job board:" từng kéo cả dòng vào COORD_WARN → dispatch oan).
- **Question TREO LÂU >48h** (thêm Wags 2026-07-30): checker có dòng WARN riêng
  `⚠️ Câu hỏi TREO LÂU (>48h, chưa ai quyết)` cho question quá cửa sổ 48h mà vẫn chưa có
  answer/decision (horizon 30 ngày). Trước đó question >48h RƠI KHỎI radar hoàn toàn → chết
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

- Mọi sự cố ảnh hưởng workflow sống → `kb/INCIDENTS.md` (blameless, có commit hash).
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
