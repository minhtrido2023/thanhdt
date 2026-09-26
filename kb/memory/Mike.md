# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Retro 2026-09-26 XONG (commit a9b294de): 2 sự cố, Wags GAPS FOUND (minor, đã sửa — đếm
  event 153→163). Escalation: KHÔNG mở mới. 2 carry-over vẫn treo (xem dưới).
- **CARRY-OVER quan trọng nhất — `retro-pattern-recurring-ack-topic-counter-structural-3retros`**
  (mở 09-25T20:59:54Z): Mike đã quyết dispatch Wags 1 task hẹp sửa `daily_retro.sh:195` vs
  `ops_health_check.sh` (bug ack-topic-counter, arch-reviewer chỉ đúng 2 lần 09-23/09-25) —
  **CHƯA THỰC THI** qua 2 retro liên tiếp (~20h tính đến 09-26). Nếu vẫn chưa làm khi có
  instance mới (report/coordination chạy lại từ Thứ Hai 28/09) → lần tái diễn thứ 4, cần làm
  ngay đầu tuần.
- Carry-over: `retro-pattern-recurring-fpt-vendor-backfill-2days` — BQ FPT corp-action hệ số
  vẫn thiếu, chờ user chọn A/B/C. 0 report cuối tuần nên chưa verify lại được.
- `selfcheck-baseline-checker-no-tier-orb-vnstock-daily` (mở 09-25, low urgency) — treo, chưa
  tới ngưỡng escalate lại.

## Việc đang mở / cần theo dõi
1. **FiinPro harvest**: 74/74 lô XONG (26/09). 2 job song song đang chạy: JOB A
   Taylor_20260926_164113 (H3 PIT→H1 bank 8L→H2 CPI), JOB B Taylor_20260926_164143 (H4 foreign
   matched 2018→H5 retail ecology), timeout 3h, opus/high. Sau khi cả 2 xong: dispatch H6
   (Bobby/macro-strategist, lead-indicator credit/M2/fx) + H7 (GDP, thấp ưu tiên). Wakeup poll:
   claim-reply từng job trước khi post kết quả.
2. **excluded_dividend_receivable[DGC]** (ZaloPay) — dọn config khi tiền DGC về thật, đã qua hạn
   dự kiến ~09-25, kiểm lại khi có cập nhật.
3. Đối soát panel-vs-live gap (job Taylor_20260926_042824) đã XONG 04-44 26/09: 2 việc phụ còn
   mở không khẩn — `audit_lib.py` nhãn park sai E1VFVN30 vs CUSTOM_VN30G; 8-9 mã live ngoài rổ
   recommend chưa truy nguồn.
4. Opening-window l2-poll A/B (order_book_execution_shadow ext, commit 4d863548) DEPLOYED, cron
   09:13 ICT T2-T6 từ 28/09 — checkpoint sơ bộ 21/10, mốc quyết định cứng 25/01/2027.

## ĐÃ XÁC NHẬN KHÔNG CÒN TREO
- Chuỗi audit corp-action 4 call-site + vendor-mismatch + ex-date price-frame — ĐÓNG HOÀN TOÀN
  2026-09-24, tất cả LIVE trên master.
- context_pack.md 47.6KB đã vượt ngưỡng 45KB (ghi nhận 09-25, chưa xử — theo dõi nếu tiếp tục
  phình).

- [2026-09-26T17:48:06Z] 27/09 00:5x — FiinPro 7 HƯỚNG XONG (commit kb v: kết quả ở kb/projects/fiinprox-data-usage-proposal-20260926.md §6). Không wire gì. CHỜ USER QUYẾT: (1) bus question Taylor/custom30v-index-artifact-pham-vi-re-pin — R3 28,86%→24,38% (−4,48pp) khi bỏ bước nhảy số CP khỏi chuỗi return custom30V (custom_basket.py:220/:1125), quant-skeptic CONFIRMED high — A sửa+re-pin toàn bộ / B chỉ R3 / C TRAP; Taylor khuyên A + kiểm kê park LIVE có mua 30 mã thật không; (2) đóng B.1 production_mechanism_2009_2018 + G4 amh-review; (3) câu hỏi trục breadth-tercile 08-22 trượt 4/4 trên panel H5; (4) H1/H2 wire vệ sinh (giá trị 0/thấp) — có làm không. Đã lưu h5_retail_*.csv + artifact trong git (8acb69d4, aff8940e). Trial FiinPro hết 28/09 — KHÔNG mua.
