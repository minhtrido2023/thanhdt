# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-07-29 EOD (sau daily retro finalize, Wags GAPS FOUND → fixed → INCIDENTS.md commit 86a9cae)

## RETRO 2026-07-29 — 4 sự cố, pattern data-registry-accuracy (chi tiết đầy đủ: kb/INCIDENTS.md)
Biến thể MỚI của pattern quen thuộc: không phải "ta đọc nhầm nguồn" mà "bảng production của ta bị
BÊN NGOÀI ghi/đổi mà không hay biết ngay" — (1) DT5G lịch sử 134/144 phiên bị restate âm thầm,
fix `restate_guard.sh` LIVE nhưng chỉ ALERT không CHẶN; (2) `vnindex_5state_dt5g_live` có writer
thứ 2 độc lập (kaffa_v2, team khác) làm gate freshness mất tác dụng — **QUYẾT ĐỊNH CÒN TREO**;
(3) `ticker_prune` rebuild xoá 58 mã khỏi lịch sử, quyết định KHÔNG restore đã chốt nhưng root
cause (rebuild sẽ tái diễn) vẫn nguyên; (4) paper-report trễ 2 phiên, đã fix cron, 1 đề xuất còn
treo (đưa pt_capitulation_shadow vào chain 19:00 hay không).

## Việc còn treo sang mai
- **Sự cố 2 (ưu tiên cao)**: bus question `dt5g-live-2-writer-can-quyet` (11:17:14Z 07-29) —
  cần user/Mike quyết A/B/C cho writer kaffa_v2 ghi đè `dt5g_live`.
- Mốc theo dõi 2026-07-30 18:30: xác nhận cron thật đầu tiên chạy `restate_guard.sh` nhánh
  `dt5g_live` (check `data/refresh_v34b_linux_2026-07-30.log` + `restate_guard_history.jsonl`).
- Xác nhận độc lập breadth-guard migrate (`universe_pit`, commit `8f95895`) thật sự MERGED —
  chưa tự verify, chỉ đọc báo cáo Taylor.
- Đề xuất mới: mở rộng `mike/kb/data_registry/` để ghi cả bảng ta VIẾT (không chỉ ĐỌC) — chưa
  ai nhận việc.
- Sự cố 4: quyết định đưa `pt_capitulation_shadow` vào chain 19:00 hay giữ nguyên 15:30 (đề xuất
  Winston_20260729_103816, đang treo).
- funding_required/cash-discipline: lần 3 (07-23/27/28) user đã CHẤP NHẬN residual risk (16:16
  07-28, từ chối hard validator) — theo dõi nếu có lần 4, escalate ngay không chờ retro.
- Nợ cũ chưa dọn: gate cơ khí cho `daily_retro.sh` Bước 1 (đề xuất 3 lần, chưa cài); backfill
  RETRO 07-24→07-27 (chưa quyết); `sync_bq_cache.py` bug#3 (chưa dispatch); dọn crontab
  paper-trading lạc hậu (diff `Winston_20260712_151206`, chưa áp dụng); bus question cũ >2 tuần
  chưa answer (`retro-pattern-recurring-data-registry-accuracy-5days` 07-15,
  `retro-pattern-recurring-joblifecycle-timeout-3` 07-14,
  `retro-pattern-recurring-headless-wake-assumption-3` 07-20); commit `734cbac` review status
  (nợ từ RETRO 07-23).

## Trạng thái vận hành
SpaceX/ZaloPay LIVE, V2.4. Plan 07-30: SpaceX deferred_count=3 (140,65M, cash-gap đã biết, user
chấp nhận), ZaloPay HOLD. LAG rating gate cứng (≤3) LIVE. CAPIT fired 07-20/21, giải ngân dở.
Fear-buy sleeve TV1+DGC QUALIFIED YES, chờ user quyết mua discretionary. universe_pit R3 cutover
chính thức 07-22; CAPIT breadth cutover 07-22 (pool vẫn ghim ticker_prune, cố ý). Domain-constraint
layer P1 LIVE (LAG rating gate order-level), P0 shadow-log (buying-power) đang theo dõi.
Xem `context_pack.md` "MỚI NHẤT" cho tin mới hơn nếu đã qua nhiều ngày.

- [2026-07-29T17:49:43Z] Daily_retro gate SHIPPED (commit 01a7f99, arch-reviewer CONFIRMED sau 1 gap fix): session_start.sh giờ skip recap_prev.py cho headless Mike dispatch (root cause thật của Pattern A, không phải model flakiness) + daily_retro.sh có content-shape gate _draft_valid(). Đóng Prevention#1 nợ từ RETRO 07-18/07-19/07-28. Follow-up CHƯA làm (arch-reviewer nêu, ưu tiên cao): chiều NGƯỢC LẠI vẫn hở — phiên live Mike cũng tự resume/recap transcript của headless dispatch (245 lần quan sát được), cùng họ bug, lớn hơn.
- [2026-07-30T03:17:53Z] 2026-07-30 03:xx: bảng bất biến DT5G (state_publish_immutable.py) + sync_bq_cache lock/atomic đã LIVE, quant-skeptic CONFIRMED cả 2, commit fe838df+9de2870+e8d8228. Mốc theo dõi 18:30 ICT tối nay: xác nhận cron thật daily_refresh_v34b_linux.sh chạy full chain [10]->[11]->[11b]->[12]->[12b] không lỗi (publisher mới, _v34b_clean sync 3 cột tường minh, restate_guard RESTATE_LOOKBACK_DAYS=45). Việc nhỏ tồn đọng không khẩn: audit đầy đủ ~50 consumer của _v34b_clean cho SELECT*/positional-access (quant-skeptic mới spot-check 2), fix CSV path chết trong analyze_vix_peak_bottom.py (bug có sẵn, không liên quan).
- [2026-07-30T05:59:38Z] P1/P2/P3 (Wags audit dispatch-content-verification) SHIPPED, commit dd9d6dd, arch-reviewer CONFIRMED sau 2 vòng (vòng 1 bắt 3 blocker thật ở P1: no-op cho ZaloPay do chỉ đọc ref_price không phải mtm_price_ref, orders:null crash làm mất second-chance 23:00 trong im lặng, DNSE 0/N verify không hiện gì cho người duyệt — cả 3 đã sửa + re-verify bằng cách replay đúng file plan ZaloPay 07-10 thật). Nợ còn lại đã ghi nhận rõ trong code comment (không phải bug, là giới hạn có chủ đích): P2 không bao giờ bắt được label gắn ngày dùng 1 lần (vd run-bot-fail-*-<date>) vì cơ chế check-ở-lần-sau cần label lặp lại; 3% price tolerance chưa hiệu chỉnh kỹ (đo được 1.7% lệnh lịch sử vượt ngưỡng, rủi ro false-positive ngày biến động mạnh). Cả 3 việc user duyệt hôm nay (vá chiều ngược session-collision + known-issue lookup + audit tổng quát P1/P2/P3) đã XONG hết.
- [2026-07-30T08:46:06Z] 2026-07-30: fixed session_start.sh 'Đã resume xong' spam (ccdb compact-guardrail reruns) — commit 0073460, 3 vòng arch-reviewer. TRADEOFF CÒN CHỜ USER: fix cũng tắt luôn tín hiệu 'compact thật sự xong' gốc (2026-07-03) — hỏi user có chấp nhận không.
- [2026-07-30T10:53:51Z] 2026-07-30: thêm tín hiệu 'Compact xong' riêng (commit ab8c0ee) — chỉ báo khi source=compact + trigger=manual + đã idle ≥60s, tự lọc auto-compaction + double-compact chain. 5 vòng arch-reviewer, vòng cuối CONFIRMED. Trước đó tradeoff (fix spam commit 0073460) đã hỏi user và user chọn làm thêm tín hiệu này thay vì chấp nhận mất.
- [2026-07-30T12:40:24Z] fleet_housekeeping.sh LIVE (cron CN 22:00 ICT) — user chốt A (kaffa_v2 45GB = project khác, bq_admin quản, KHÔNG đụng). Còn treo: B (mike repo git 279MB CSV/pkl exp, .git 242MB — cần hỏi Taylor + xét git gc), C (chốt policy giữ bao nhiêu bản bq_cache_asof* vào coding_guidelines §8, hiện chỉ có 1 bus event dễ trôi), D/E không cần hành động.
- [2026-07-31T02:39:05Z] 2026-07-31: dt5g-live-2-writer câu 2 đã chốt phương án B (chỉ đọc/giám sát, không đụng kaffa_v2) — gate publisher-evidence + writer-watch LIVE (commit faf5e8a6). Mike tự verify bắt 1 bug TZ thật trong dt5g_writer_watch.py (host UTC, script giả định ICT) — Winston sửa + Mike commit 282cb98f, selfcheck 4/4 PASS dưới env -u TZ. Production tối nay không bị ảnh hưởng (wc_env.sh đã export TZ trước khi gọi) nhưng bug latent đã đóng.
- [2026-07-31T06:18:32Z] 2026-07-31: DGC ZaloPay chốt GIU FULL (đóng bus question). dataprovenance-2 Mike tự quyết + viết coding_guidelines.md §14 (producer→consumer freshness). Dọn backlog bus question: quét cả hot+archive (45 total lịch sử), đóng 21→còn 1 (Wags self-loop đang chạy). Phát hiện 2 câu hỏi thật 06-22/06-27 từng bị archive 30d làm biến mất khỏi mọi report — đã đóng cả 2. Dựng bin/bus_question_audit.py + item 11 Friday kb_nightly.sh post báo cáo Architecture channel — cơ chế weekly accountability user yêu cầu. Winston audit §14 tìm 3 case rủi ro thật, Case A HIGH: ops_health_check→golive_recommend_v23 qua anomaly_flags.json KHÔNG check file có ghi hôm nay không — ảnh hưởng CAPIT gate live. CHƯA fix, cần dispatch follow-up.
- [2026-07-31T07:02:18Z] 2026-07-31: Fix xong cả 3 case data governance §14 (anomaly_flags CAPIT gate HIGH, DT5G EOD/8L HIGH, telegram rating_8l.csv MEDIUM) — job Winston_20260731_062642 hết lượt (max-turns 50) trước khi commit, Mike tự đọc từng diff + tự chạy lại selfcheck độc lập (46/46 PASS) rồi commit (WorkingClaude 0daf864, mike d51f74eb). Tất cả WARN-only, không đổi hành vi gate/loại trừ hiện có. Case B/C finding tự ghi bus thay Winston (job hết lượt trước khi report).
- [2026-08-01T04:25:08Z] 2026-08-01: user duyệt 3 việc — (1) opus%-alert (item 5c kb_nightly.sh, mirror fable check, ngưỡng ≥60% hoặc +20pp/3 tuần, review chất lượng chứ không tự sửa thói quen); (2) daily_retro freshness check (ops_health_check.sh item 9, WARN nếu thiếu retro-<hôm qua>.md); (3) weekly_ops_audit.sh mới, cron Sat 03:30 ICT, lặp lại kiểu audit sâu Mike vừa làm, báo Architecture channel+Telegram. BONUS: khi tự kiểm quoting đoạn mình thêm vào kb_nightly.sh, phát hiện 2 bug quoting CÓ SẴN (item 5b + item 7, cả 2 từ 07-17) làm TOÀN BỘ Friday/Saturday editorial dispatch (11 mục, gồm cả bus-question weekly report mandate 07-31) chết lặng 2 TUẦN LIỀN — dispatch.sh nhận sai argument, exit 1 ngay, không ai biết vì log chỉ ghi 'launched'. Đã fix cả 2 (commit 45f5c5d0), verify bằng mô phỏng thật (arg-count stub). Lần chạy ĐÚNG đầu tiên sẽ là Sat 08-08 (hôm nay 08-01 đã lỡ, chạy bằng bản cũ trước khi tôi fix). Toàn bộ 3 bug quoting phát hiện hôm nay (daily_retro + 2 trong kb_nightly) đều cùng 1 nguyên nhân gốc: chèn markdown-style " hoặc ` vào chuỗi bash double-quoted mà không escape, không test lại bằng cách chạy thử.
