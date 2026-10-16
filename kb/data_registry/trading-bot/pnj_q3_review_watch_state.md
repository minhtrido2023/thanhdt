---
kind: local-file
status: CANONICAL
source: data/pnj_q3_review_watch_state.json
group: trading-bot
note: state chống-lặp của watcher PNJ BCTC Q3 — MỘT LẦN, không phải chuỗi thời gian
writer: mike/bin/pnj_q3_review_watch.py (bq_freshness_check.sh, 19:00 ICT)
---

# data/pnj_q3_review_watch_state.json

**Status: CANONICAL (state một-lần) — tạo 2026-10-13, job Taylor_20261013_125149, user duyệt**

## Là gì
State chống lặp của `mike/bin/pnj_q3_review_watch.py`: watcher canh "PNJ công bố BCTC Q3/2026" — review
trigger của việc loại PNJ khỏi 2 account từ 2026-09-30 (`kb/current_ops.md`). Khi `tav2_bq.ticker_financial`
có dòng PNJ `quarter='2026Q3'`, watcher bắn ĐÚNG MỘT LẦN bus `question` topic `pnj-bctc-q3-review-trigger`
+ 1 tin Discord Trading Daily, rồi ghi file này.

Khoá: `ticker`, `quarter`, `topic`, `detected` (`n`, `release_date`, `time` đo lúc phát hiện),
`bus_posted_at`, `bus_found_existing`, `discord_attempted_at`, `discord_ok`, `discord_error` (mốc giờ ICT).

## Ai ghi / cadence
Chỉ `pnj_q3_review_watch.py`, trong chuỗi 19:00. File KHÔNG tồn tại cho tới lần phát hiện đầu tiên — vắng
file = "chưa bắn", không phải lỗi. Ghi nguyên tử (tmp + `os.replace`).

## Bẫy
1. **Xoá file = cho phép bắn lại.** Đã có `question` trên bus thì watcher tự nhận ra (quét mọi tầng
   `bus/**/*.jsonl`) và không post bus lần hai, nhưng Discord SẼ gửi lại một lần.
2. **File hỏng ⇒ watcher im lặng vĩnh viễn** (fail-closed, in `WARN pnj-q3-watch: KHÔNG đọc được state` vào
   `logs/bq_freshness.log` mỗi tối). Chủ ý: thà chậm còn hơn spam; thấy dòng WARN đó thì sửa/xoá file tay.
3. `discord_ok=false` KHÔNG được gửi lại (tối-đa-một-lần) — question trên bus là bản ghi bền.
4. Đây là watcher MỘT mã MỘT quý (hằng số `TICKER`/`QUARTER` trong script). Sau khi review PNJ xong, script +
   file này hết việc — gỡ bước gọi trong `bq_freshness_check.sh` khi đóng question.
5. Watcher KHÔNG đụng `excluded_tickers`; khôi phục PNJ vẫn cần user duyệt sau due-diligence.

## Follow-up GỠ watcher (user duyệt 2026-10-13)

GỠ khối `pnj_q3_review_watch` khỏi `bin/bq_freshness_check.sh` (và file state này) NGAY KHI review PNJ Q3 xong và bus question `pnj-bctc-q3-review-trigger` đã đóng. Watcher hardcode PNJ/2026Q3, bắn đúng 1 lần — để nguyên sẽ thành mã chết. Con trỏ ở `kb/current_ops.md` mục PNJ (REVIEW TRIGGER).
