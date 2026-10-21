# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 20/10 (dọn 00:35 ICT 21/10)
## Chờ USER
- Retro-pattern fail-closed gate (2 câu bus: `...-owned-recovery-path` 18/10 + `...-recovery-path-recurring` 19/10; trả lời xong đóng CẢ HAI).
- Lãi CCTG A/B (6,8% vs 5,9%; mặc định giữ 6,80/7,40). Áp `ZaloPay_weekly .md.proposed_fix` + gửi lại.
## Việc dở (Mike)
- Arch-review + merge `feat/fa-ratings-ticker-gate-20261020` (c12bb294a) TRƯỚC cron T7 09:15.
- Xác nhận `tav2_bq.ticker` phục hồi đủ ~1294 mã (bq_admin/Winston; COUNT 5 ngày gần nhất mới 1026); đọc lại verdict P2v2 trên pin.
- Mã niêm yết mới từ 05/2026 (DMX) thiếu BQ + 230/447 mã delisted mất dữ liệu: giao Winston/bq_admin.
- 2 question Wags treo (`wags-fix-not-confirmed: coord-2026-10-19/20`); watchdog "no enabled mike@ units" lặp — nhiễu hay bỏ check.
- Prevention đề xuất: memcap/mem_slots ép trong dispatch.sh (container 40GB, không swap, treo 20/10); cảnh báo dispatch --bg thiếu wakeup.
## Đã chốt
- Plan 20/10 HOLD ALL. DT gate: giữ luật đếm (CRISIS commit sớm nhất ~11/11). Vòng plan CN chạy thật 25/10 19:00 ICT.
- Retro 20/10 logged (6 sự cố, 2 pattern, Wags GAPS đã sửa).
## Mốc
- nav-loss-brake 11-09; review BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27; monitor treasury_buyback 26/10.
- Dọn worktree: wt-Taylor_20261018_173105, wt-1521183164364754974, wt-Taylor_20261019_052148.

- [2026-10-20T18:03:11Z] 01:10 21/10: Taylor_20261020_162558 XONG (claimed; PREREG V1D 2c1a3a71/V1E 12daef05/V3Ap 4b52b717/V4 a210a290 khớp REPORT; control 4/4 byte-identical, 20/20 selfcheck 0 VND). V1D chặn ADV3M<=0 nhân quả: ΔCAGR +1,25..+2,03 (DƯƠNG) → phần Vol=0/ADV3M<=0 KHÔNG là nguồn lợi nhuận pin (31% giá trị mua nhưng 9-11% PnL); nhưng 41-47% giá trị mua LAG vẫn >20% giá trị khớp cùng ngày, nhóm X gánh 43% PnL (54% 2022-26) → CHƯA thể nói pin thực thi được ở 50B. ΔIS âm mọi biến thể, ΔOOS dương. V3A' không đổi nhãn. Skeptic survivorship-volzero-V1D-V1E-V3Ap-V4 chạy nền (logs/verify_survivorship_v1d_bg.log). Chờ user: stock_news.proposed; bước kế capacity (trần tham gia theo phiên).
- [2026-10-21T01:20:38Z] 08:25 21/10: stock_news.md ĐÃ nằm trong registry price-volume (PARTIAL, đã commit bởi consolidator 17:00Z 20/10; index đã có dòng) — không cần áp thêm. User duyệt 3 việc skeptic → dispatch Taylor_20261021_012028 (opus medium, 14400s): F1 V1D có trần hoãn bán N=5/20 + chiết khấu/mark 0, F2 tách tái phân bổ (vốn giải phóng để cash/ETF), F3 trần tham gia nhân quả bằng dự báo KL. Khi xong: claim-reply, verify PREREG, control 4 chân, skeptic nền. Poll 30' kèm hb_age.
