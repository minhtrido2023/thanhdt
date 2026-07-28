# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-07-28 EOD (sau daily retro finalize, 3 bước xong)

## RETRO 2026-07-28 — XONG, ghi kb/INCIDENTS.md (commit a67d59e), Wags verify GAPS FOUND → đã sửa 3 gap trước khi ghi
3 sự cố: (1) `spacex-loanpackageid-order-reject` — đã có entry đầy đủ từ trước, không mới.
(2) **MỚI, quan trọng**: daily-retro pipeline tự chết lặng 4 ngày (07-24→07-27) vì headless
session trả lời nhầm câu hỏi cũ trong context thay vì viết draft mới — mitigated (retry 1 lần,
commit 9fd7913) nhưng CHƯA fix gốc (thiếu gate cơ khí xác nhận nội dung draft đúng chủ đề —
đã bị đề xuất 2 lần ở RETRO 07-18/07-19, vẫn chưa cài). (3) **MỚI, pattern nguy hiểm nhất**:
funding_required/cash-discipline TÁI DIỄN LẦN 3 (07-23→07-27→07-28), mỗi lần đổi vỏ bọc khác
nhau (rút Trứng vàng trực tiếp → field cấm → văn xuôi tự nhiên), tần suất đang TĂNG. User đã
biết + CHỦ ĐỘNG từ chối hard-code validator (16:16 07-28, lý do margin/vay tương lai) — rủi ro
residual chấp nhận có chủ đích, cần THEO DÕI CHẶT nếu có lần 4.
**Insight chính**: retro pipeline chết lặng = single point of failure khiến pattern funding_required
lần 2 (07-27) không bị bắt kịp thời — khi retro không chạy, coi những ngày đó là "unknown", KHÔNG
phải "clean".

## Việc còn treo sang mai
- Quyết định có backfill RETRO cho 07-24→07-27 hay không (nợ do Wags nêu).
- Cân nhắc gate cơ khí thật cho `daily_retro.sh` Bước 1 (đề xuất lần 3, chưa cài — RETRO
  07-18/07-19 đã đề xuất 2 lần trước).
- Theo dõi funding_required lần 4 nếu xảy ra — escalate ngay, không chờ nhịp retro kế tiếp.
- `sync_bq_cache.py` bug#3 — chưa dispatch ai fix.
- `ticker_prune`/`ticker_financial` corruption 07-14/15 — vẫn chờ quyết định khôi phục backup.
- Dọn crontab paper-trading lạc hậu (diff `Winston_20260712_151206`) — chưa áp dụng.
- Bus question cũ chưa answer (>2 tuần): `retro-pattern-recurring-data-registry-accuracy-5days`
  (07-15), `retro-pattern-recurring-joblifecycle-timeout-3` (07-14),
  `retro-pattern-recurring-headless-wake-assumption-3` (07-20).
- Xác minh lại trạng thái review thật của commit `734cbac` (nợ từ RETRO 07-23, chưa làm).

## Trạng thái vận hành
SpaceX/ZaloPay LIVE, V2.4. Plan 07-29 đã duyệt (SpaceX: TV1 only 5,82M; ZaloPay: HOLD; 3 lệnh
140,65M bị defer do cash chưa đủ — theo dõi nếu user nạp thêm). LAG rating gate cứng (≤3) LIVE
từ commit d7417a2. CAPIT fired 07-20/21, SAB/SIP/VNM khớp, PVT/NCT còn vướng. Fear-buy sleeve
TV1+DGC cả 2 QUALIFIED YES, chờ user quyết định mua discretionary. universe_pit R3 cutover
chính thức 07-22. Xem `context_pack.md` "MỚI NHẤT" cho tin mới hơn nếu đã qua nhiều ngày.

