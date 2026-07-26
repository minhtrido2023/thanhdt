# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-07-23 EOD (sau daily retro finalize)

## RETRO 2026-07-23 — XONG (3-bước: draft→Wags verify→finalize), ghi kb/INCIDENTS.md, commit `c110208`
Ngày sạch: 0 sự cố mới, 0 pattern mới. 1 near-incident (Mafee APPROVAL_GATE_BLOCK x5,
02:05-02:15Z) tự xác định NOT-A-BUG cùng ngày bởi Winston — khớp tiền lệ 07-20, không tính
là sự cố. Wags verify tìm 3 gap trong draft (đã sửa trước khi ghi): (G1 nhỏ) đếm sai x4→x5;
(G2 vừa) draft khẳng định sai "arch-reviewer CONFIRMED commit 734cbac" — bus thực tế chỉ có
NEEDS_CHANGES + INCONCLUSIVE, KHÔNG có CONFIRMED; (G3 rất nhỏ) thiếu event finding song song
của Winston. Wakeup-compliance 0,0% vi phạm (26 dispatch --bg) — tốt nhất từ trước tới nay.

## Việc còn treo sang mai
- **MỚI**: xác minh lại trạng thái review thật của commit `734cbac` (topic-routing fix từ
  RETRO 07-22) — bus không có CONFIRMED, chỉ NEEDS_CHANGES/INCONCLUSIVE. RETRO 07-22 từng ghi
  sai là đã CONFIRMED. Cần kiểm tra có quyết định đóng nào khác hay cần re-review.
- `sync_bq_cache.py` bug#3 (`ticker_financial` delta-only sync không bắt kịp sửa-đổi lịch sử)
  — chưa dispatch ai fix.
- Pattern git-commit-blocked-by-classifier — theo dõi, escalate nếu tái diễn lần 3 (2 lần liên
  tiếp 07-21→07-22, 0 lần 07-23).
- `ticker_prune`/`ticker_financial` corruption 07-14/15 — vẫn chờ quyết định khôi phục backup.
- Dọn crontab paper-trading lạc hậu (diff `Winston_20260712_151206`) — chưa áp dụng, verify lại
  07-23 vẫn còn 4 dòng cũ.
- Bus question cũ chưa answer: `retro-pattern-recurring-data-registry-accuracy-5days` (07-15,
  >8 ngày), `retro-pattern-recurring-joblifecycle-timeout-3` (07-14, >9 ngày).
- M5 nợ cũ: `executor.py`/paper trials đọc `ticker_prune.parquet` monolith chết từ 06-26 — chưa
  dispatch, không khẩn (chỉ ảnh hưởng paper).

## Trạng thái vận hành
SpaceX/ZaloPay LIVE, V2.4. CAPIT fired 07-20/21 (SAB/SIP/VNM khớp, PVT/NCT còn vướng).
LAG: TRC HOLD (user chốt, chờ nghiên cứu regime deep-dive #2 xong — job Taylor_20260723_162813
đang chạy so sánh disc_c4/c5 trong BLENDED V2.4 đầy đủ, quant-skeptic đã CONFIRMED bản LAG-only
trước đó, cần verify lần 2 cho bản blended nếu kết quả tốt). Fear-buy sleeve: TV1 + DGC cả 2
đảo ngược thành QUALIFIED YES (deep-value/asset-backed) sau due-diligence lần 2 — CẦN USER
QUYẾT ĐỊNH CUỐI có mua discretionary hay không, Mike/Taylor không tự đặt lệnh ngoài V2.4.
universe_pit: R3 cutover CHÍNH THỨC xong 07-22 (27,16%/1,81/-18,1%/1,50). Xem `context_pack.md`
"MỚI NHẤT" cho tin mới nhất thay vì phần này nếu đã qua nhiều ngày.

- [2026-07-26T12:55:40Z] Đang chạy song song: Taylor_20260726_125456 (backtest tranche-theo-xác-nhận cho CAPIT vs lump+ramp3phiên hiện tại, so trên lịch sử các lần CAPIT fire) + DollarBill_20260726_125529 (thiết kế vận hành NẾU tranche hóa — field plan JSON, xử lý Trứng vàng, timeout T2/T3). Đây là ý tưởng thiết kế mới do user đề xuất (lấy cảm hứng từ sleeve 'mua khi sợ hãi có tính toán' đã có tranche T1/T2/T3 cho từng mã đơn lẻ, giờ xét áp dụng cho CAPIT cấp thị trường). KHÔNG kết luận trước — chờ cả 2 kết quả.
