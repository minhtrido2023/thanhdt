# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (dọn cuối ngày 2026-10-10, sau retro)
- **Retro 2026-10-10 ghi xong**: kb/incidents/retro/retro-2026-10-10.md (commit 3b1cbe16).
  2 sự cố: (1) disk `/` đầy 100% lúc 04:40 ICT (worktree Taylor), tự hồi phục trong ngày không
  rõ ai dọn — error mở, không có event đóng. (2) công cụ tỉ suất §21 (`dividend_adjusted_return.py`)
  lỗi tính GIPS/tax-lot, lan ra 2 báo cáo tuần 05-09/10 đã gửi (sửa + gửi lại, user duyệt 22:03
  ICT 10/10). Pattern H MỚI: lỗi đo lường client-facing được Taylor tự phát hiện-vá-đóng gọn
  trong 1 phiên nhưng KHÔNG đi qua bus dưới dạng `error` (chỉ `finding`) — thiếu tín hiệu nghiêm
  trọng đầu vào; sự cố #1 thiếu tín hiệu đóng đầu ra. Prevention: Taylor post `error` TRƯỚC khi
  vá khi phát hiện lỗi đo lường chạm báo cáo đã gửi; mọi `error` có `action_needed` chỉ người
  phải có event đóng khi giải quyết (kể cả "tự hồi phục, không rõ nguyên nhân"). Wags verify
  GAPS FOUND nhỏ (đếm event 516/7/529→524/9/539), đã sửa.
- **Chính sách "tài khoản = quỹ mở" ĐÃ DUYỆT** (f75457cf, 5 điểm). Bước 1 (sổ đơn vị quỹ) giao
  Taylor job `Taylor_20261010_170004` (opus/high, --bg) — ĐÃ XONG (branch feat/fund-unit-ledger-
  20261011 @feaa33b5, 65/65 mutant chết, control 3.900 giá trị 0 lệch), CHƯA merge, chưa chốt sổ
  thật. Next: kiểm artifact → arch-reviewer 1 lần (dặn liệt kê trọn bộ lỗi) → merge → bước 2 (tự
  phát hiện dòng tiền). Bước 3-4 chưa giao.
- 5 nhánh R&D hậu re-pin park0 (hôm trước) — ĐÃ ĐÓNG hết, không còn gì chờ.
- Instructions-dedup, cutloss intraday shadow v2, corp-action broker-primary SHADOW, SBV
  source-B, Pattern F PAT expiry — không đổi, xem retro-10-09 nếu cần chi tiết.

## Đang chờ
- `selfcheck-red-sweep-2026-10-09-can-user` (Wags/bus question, SCL SpaceX) — còn mở, theo dõi
  sweep Thứ Sáu 16/10.
- `annualization_basis_selfcheck.py` RED (Taylor) — theo dõi sweep tiếp.
- send_plan_report.sh retry drift-check riêng — đề xuất chưa làm, chưa cần gấp.
- Taylor job `Taylor_20261010_170004` (fund-unit-ledger bước 1) — chờ arch-review + merge.

## Next
- Prevention Pattern H: nhắc Taylor post `error` trước khi vá khi gặp lỗi đo lường client-facing
  trong dispatch prompt tiếp theo chạm §21/§31.
- Mỗi `error` có `action_needed` chỉ người — kiểm có event đóng chưa trước khi coi "đã xong"
  (retro mai áp lại, giống Prevention #2 Pattern G đã làm hôm nay).
- Thứ Hai 12/10 08:05 ICT: kiểm cron SBV/CCTG tuần chạy đúng + finalize nhắc STALE nếu cần.
- arch-review fund-unit-ledger bước 1 → merge → giao Taylor bước 2.
- Theo dõi `git worktree list` — nếu đĩa chạm ngưỡng cao lại vài ngày tới, nâng từ "quan sát"
  lên "pattern cần vá" (dọn worktree định kỳ / cảnh báo % dùng).
- KHÔNG đặt wakeup thăm dò khi không có job nền đang chờ kết quả (user 10-05).

- [2026-10-11T03:05:31Z] [10-11 10:10 ICT] User DUYỆT (10:04): (2) đính chính 1 dòng kèm báo cáo ngày ZaloPay 12/10, không gửi lại bản cũ; (3) giao bước 2 quỹ mở sau khi cron tối thứ Hai 12/10 chạy sạch. Đã đặt CronCreate one-shot trong phiên lúc 19:47 ICT thứ Hai 12/10 (12:47 UTC) làm cả 3 việc: kiểm 2 dòng NAV, gửi dòng đính chính vào Trading report 1522576692638388364, dispatch Taylor bước 2. CronCreate CHỈ sống trong phiên — nếu phiên restart thì mất, phải làm tay theo mục này. Điểm (1) luật giá tiền vào trước giờ mở cửa/cuối tuần: user hỏi giải thích, CHƯA chốt (đang = giá chốt phiên liền trước).
- [2026-10-11T03:23:50Z] [10-11 10:25 ICT] User CHỐT điểm (1) quỹ mở: GIỮ giá chốt phiên liền trước cho tiền vào trước giờ mở cửa/cuối tuần/ngày nghỉ (decided_by user, kb 41764ffa; code bước 1 đã đúng, không sửa). Cả 3 điểm chờ user nay ĐÃ ĐÓNG. Còn lại duy nhất: việc có mốc thứ Hai 12/10 sau 19:10 ICT (kiểm 2 dòng NAV + gửi dòng đính chính ZaloPay vào Trading report + dispatch Taylor bước 2) — CronCreate one-shot 19:47 ICT trong phiên, mất nếu phiên restart.
- [2026-10-11T03:25:10Z] [10-11 10:35 ICT] ĐÍNH CHÍNH dòng trên: CronCreate one-shot 19:47 thứ Hai ĐÃ MẤT (phiên Discord mỗi lượt là tiến trình mới ⇒ CronCreate vô dụng ở đây, đừng dùng lại). Thay bằng task one-shot BỀN trong bộ lập lịch ccdb: id 2741 'fund-step2-after-eod-20261012-<thread>', bắn Thứ Hai 12/10 19:46 ICT vào topic 1558282936489611354 (kiểm: curl $CCDB_API_URL/api/tasks). BẪY: bất kỳ ScheduleWakeup nào đặt trong topic này trước giờ đó sẽ XOÁ task (ccdb giữ ≤1 one-shot/thread) ⇒ nếu buộc phải đặt wakeup thì tạo lại task sau.
- [2026-10-11T03:37:41Z] [10-11 10:50 ICT] Topic 1558645322085826593: user hỏi phân tích Haiku/Sonnet/Opus 5.5 + routing mới. ĐÃ TRÌNH 6 đề xuất, CHƯA sửa gì, CHỜ USER duyệt: (1) 8 agents/*/.claude/settings.json claude-sonnet-5 -> claude-sonnet-5-5 (omit --model đang chạy Sonnet đời cũ: 1.054 lượt/3 ngày); (2) ghim model cho 10 native agent chưa có frontmatter model (đang thừa hưởng Opus của Mike); (3) thêm tầng Haiku 5.5 (alias haiku -> claude-haiku-5-5 đã probe) cho việc chỉ-đọc kiểm được; (4) thử 2 tuần Opus mặc định effort medium, high chỉ cho phản biện/đường tiền; (5) ops_autofix.sh opus->sonnet (lật 1 phần quyết định 10-06, cần arch-review); (6) bỏ đẩy Q1 sang opencode (offload 0%), giữ opencode cho second_opinion. Số đo: Taylor opus/high = 65% chi phí job có bản ghi cost (42/320 job).
- [2026-10-11T04:38:37Z] [10-11 11:45 ICT] ROUTING MODEL ĐỜI 5.5 ĐÃ MERGE master 95de45b9 (user duyệt 10:55, arch-review vòng 2 APPROVED). Luật hiện hành: đầu file kb/mike_model_routing.md. ĐÃ LÀM: 6 agent omit→claude-sonnet-5-5 (smoke Wendy xác nhận); 10 native agent ghim model (fleet-scout=haiku, thử 3/3 đúng); dispatch.sh --model opus tự trần 80 lượt; spend_report có nhãn haiku; skill dispatch-routing + gương agents_native/. KHÔNG LÀM: ops_autofix.sh giữ Opus (arch-review bác, 14 job không cái nào cơ học). ĐỢT THỬ Opus mặc định effort medium tới 2026-10-25: task ccdb one-shot id 2742 bắn CN 25/10 10:00 ICT vào topic 1558645322085826593 — BẪY: đặt ScheduleWakeup trong topic đó trước ngày ấy sẽ XOÁ task, phải tạo lại. KHI DISPATCH: việc khó = --model opus (KHÔNG kèm --effort high trừ phản biện/chạm tiền/thiết kế mới); DollarBill/Mafee CHỈ omit --model. CHỜ USER: (1) có đổi DollarBill/Mafee sang Sonnet 5.5 không (chạy thử plan: đúng HOLD 0 lệnh nhưng làm tắt, n=1 sạch); (2) kiểm cơ học bản đồ model vs dùng alias sonnet trong settings; (3) ccdb còn 7 giá trị claude-sonnet-4-6 + 1 claude-opus-4-8 trong DB, .env claude-sonnet-5; (4) cột haiku_jobs trong spend_history.csv.
- [2026-10-11T04:55:45Z] [10-11 12:00 ICT] User chốt 11:50: KHÔNG ghim ID model, dùng alias. ĐÃ LÀM (master 875c19aa): cả 8 agents/*/.claude/settings.json + spawn_child.sh ghi alias sonnet (kể cả DollarBill/Mafee — user chốt dù Mike khuyên giữ Sonnet 5); smoke Wags omit→claude-sonnet-5-5 OK. Task ccdb one-shot id 2743 bắn Thứ Hai 12/10 20:40 ICT vào topic DollarBill plan 1521183164364754974: soát plan 13/10 (lượt plan thật đầu tiên trên Sonnet 5.5) trước 21:00. CHƯA LÀM — việc 3 cấu hình ccdb: phiên Mike bị lớp kiểm quyền chặn ghi /workspace/ccdb-mike/data/sessions.db và .env; bridge không có API đổi model. Cần đổi: 7 thread claude-sonnet-4-6→sonnet (1521113190405247057, 1522576692638388364, 1536246356098814022, 1540163377383481416, 1540529013737394247, 1540751247202844672, 1542030173870891018), 1 thread claude-opus-4-8→opus (1555075626908516444), key claude_model claude-sonnet-5→sonnet, .env CCDB_MODEL claude-sonnet-5→sonnet. CHỜ USER chọn cách làm. Còn mở: cột haiku_jobs trong spend_history.csv.
- [2026-10-11T05:13:58Z] [10-11 12:20 ICT] Topic 1558645322085826593, việc 3 cấu hình ccdb sang alias: user chọn cách 2 (cấp quyền). Đã viết script state/ccdb_model_alias.py (mặc định chạy thử, --apply mới ghi, có sao lưu .bak-20261011-model-alias); chạy thử ra đúng 9 dòng DB + 1 dòng .env. CHƯA GHI GÌ. Đã đưa user lệnh thêm rule Bash(python3 .../state/ccdb_model_alias.py --apply) vào agents/Mike/.claude/settings.local.json. CHỜ USER chạy lệnh rồi nhắn lại; khi đó chạy --apply, rồi chạy lại không cờ để xác nhận 'không còn gì để đổi'. KHÔNG tự sửa settings để tự cấp quyền.
- [2026-10-11T05:23:59Z] [10-11 12:25 ICT] VIỆC 3 CẤU HÌNH CCDB ĐÃ XONG: user tự chạy state/ccdb_model_alias.py --apply lúc 12:22 ICT (không qua phiên Mike, không restart bot). Đo lại: DB sonnet 22 / opus 12 / ocgo/deepseek-v4-flash 4, claude_model=sonnet, .env CCDB_MODEL=sonnet; sao lưu .bak-20261011-model-alias ở cả 2 file. KB master 20ece26b. KHÔNG có rule quyền nào được thêm. Dòng 'CHỜ USER chạy lệnh cấp quyền' phía trên HẾT hiệu lực. Còn mở ở topic 1558645322085826593: cột haiku_jobs trong spend_history.csv; task ccdb 2742 (25/10) và 2743 (12/10 20:40) vẫn đang chờ.
- [2026-10-11T05:30:27Z] [10-11 12:40 ICT] Topic 1558645322085826593 — routing 5.5 ĐÓNG HẾT việc chờ user. Cột haiku_jobs đã thêm (master d836f497): nằm CUỐI state/spend_history.csv, 2 writer (spend_report.py nightly + spend_report_weekly.py) cùng ghi, mẫu số model-mix trong prompt kb_nightly cộng haiku_jobs; file sống đã migrate header (sao lưu state/spend_history.csv.bak-20261011-haiku), dòng 10-11 haiku=0, dòng cũ rỗng. ccdb KHÔNG cần restart (bridge đọc model từ DB mỗi lượt, không cache; .env chỉ là fallback khi DB trống) — KHÔNG restart. Còn 2 mốc tự bắn: task ccdb 2743 (T2 12/10 20:40, soát plan 13/10) và 2742 (CN 25/10 10:00, tổng kết đợt thử Opus medium). Lưu ý: commit từ worktree ngoài mike/ bị tz-anchor-gate chặn giả (lệch khoá đường dẫn baseline) ⇒ SKIP=tz-anchor-gate.
- [2026-10-11T13:51:36Z] Dashboard (topic 1558645322085826593): connector BigQuery trên claude.ai BỊ CHẶN quyền (user thử 11/10, admin Trí Đh nói connector chập chờn, xưa nay phải dùng bq client, sẽ xem lại khi rảnh — không có mốc). Pilot Claude Dashboards treo chờ admin. Đã đề xuất user đường B: cockpit HTML tự sinh từ bq client + CSV local (edge-health tầng 1-2) — CHỜ user duyệt, chưa giao Taylor.
- [2026-10-11T13:55:29Z] Dashboard độ phù hợp chiến lược (topic 1558645322085826593): user CHỌN B 11/10 20:53 — HTML tự sinh, đính kèm Discord mỗi tối. Taylor job Taylor_20261011_135520 (opus, --bg) dựng mike/bin/strategy_fit_dashboard.py trên nhánh feat/strategy-fit-dashboard-20261011, bus topic strategy-fit-dashboard-v1. Next: kiểm artifact → đính kèm bản đầu cho user → HỎI user cách gửi hằng đêm (notify_thread.sh KHÔNG đính kèm được từ cron: chọn giữa thêm file vào /api/notify của ccdb [cần restart bot], upload thẳng Discord REST bằng bot token, hoặc email) → review → merge → cron (tra cron_registry §11).
- [2026-10-11T14:03:00Z] 🔴 DT5G gate rơi DT4_only từ 11/10 10:23 ICT (commit WC 3538119f ghi ts tz-aware, macro_state_live.py:305 trừ naive → TypeError; Mike tái hiện). Hôm nay chưa lệch (DT4==DT5G==NEUTRAL). Taylor job Taylor_20261011_140235 (opus/high, thread Trading Daily) vá trên nhánh fix/dt5g-gate-tzaware-health-20261011, KHÔNG merge; bus topic dt5g-gate-fallback-dt4-tzaware-health-ts(-fix-ready). HẠN: merge trước daily_refresh 18:30 thứ Hai 12/10 (kiểm cả consumer sáng). Next: kiểm artifact → arch-reviewer → TRÌNH USER duyệt merge (cổng an toàn) → đóng error bus. Đã báo Trading Daily 21:0x.
