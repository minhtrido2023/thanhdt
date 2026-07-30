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
