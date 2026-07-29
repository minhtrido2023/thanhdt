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

