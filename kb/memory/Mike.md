# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- Retro 2026-09-21 XONG (3 sự cố). #1 plan-approval cuối tuần TÁI DIỄN (Pattern 1, HOÀN CHỈNH theo
  thiết kế, 0 thiệt hại). #2 checker `ops_health_check.sh` escalate-đã-xong TÁI DIỄN ở call site
  MỚI, Wags tự vá + arch-review CONFIRMED cùng lượt (`ed4e35a0`/`118bdbfb`). #3 **nav-price-xcheck-
  stuck DRI (SpaceX+ZaloPay, lệch 8,0%) CÒN MỞ** — NAV 21/09 thật sự thiếu ở cả 2 account, >10h
  chưa ai chẩn đoán. **Mốc theo dõi: nếu tới 09:00 ICT 22/09 2 câu hỏi
  `nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-21` vẫn chưa có answer/finding → escalate ngay
  trong ngày, không đợi retro 09-22.**

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353`** (raw `p["broker"]`/`p["mode"]`, cùng lớp bug config.py hard-
   boundary) — CHƯA sửa. Deadline escalate: **trước retro 2026-09-22** nếu vẫn chưa fix.
2. **nav-price-xcheck-stuck DRI 21/09** — xem mốc theo dõi ở trên. Chưa loại trừ được corp-action
   thật (cổ phiếu/bonus, cần xử tay theo MIKE.md §PRICE_XCHECK 09-12) hay chỉ broker trễ đồng bộ.
3. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 đã đóng 09-20.
4. **`Wags/selfcheck-red: anomaly_gate_prod_parity_selfcheck.py`** + **`.../production_manifest_
   selfcheck.sh`** (mở 09-20) PENDING — correctness PASS, chỉ fail coverage-gate, theo dõi.
5. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25).
6. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức.
7. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — chưa có selfcheck/commit xác nhận.
8. Spend-report feedback loop — `.proposed` từ 09-20, lần chạy tự động đầu Chủ Nhật 2026-09-27.

## Còn mở không khẩn
- job_cancel_guard nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- append_event.sh JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

- [2026-09-22T02:10:45Z] 22/09 09:xx: nav-price-xcheck-stuck DRI (SpaceX+ZaloPay 09-21) đã CHẨN ĐOÁN xong — cổ tức tiền DRI 1.000đ/cp ex-date 09-22, khớp mẫu DGC nhưng còn dư 100đ/0,7% chưa khớp tuyệt đối. CHƯA vá NAV (manual, hoãn qua giờ ATO). Việc còn lại: patch NAV 09-21 mark giá CUM 14.900 sau khi xác nhận cum_dividend_excl đã trừ đúng khoản phải thu (§21), làm sau khi thị trường ổn định (~10-11h).
- [2026-09-22T09:10:27Z] 22/09 16:1x — ĐÍNH CHÍNH chẩn đoán DRI sáng nay: KHỚP TỪNG ĐỒNG, không có 'dư 100đ'. Giá CUM của chính broker là 14.800 (19:07 hạ xuống 13.800 = 14.800−1.000 cổ tức). 100đ 'dư' sáng nay là do tôi so BQ close 14.900 với giá broker — khác nguồn, không phải lỗi. cashDividendReceiving rỗng ngày 09-21 (ex-date 09-22) ⇒ KHÔNG có rủi ro đếm 2 lần cho snapshot 09-21.
22/09 16:1x — VIỆC 3 (vá NAV 09-21): KHÔNG vá được bằng pipeline hiện tại. Đã thử daily_nav_snapshot.py --account SpaceX --date 2026-09-21 --from-raw (có source wc_env.sh) → vẫn bị gate chặn: close_price 09-21=14.900 (cum) vs broker EOD marketPrice=13.700 (đã điều chỉnh) = 8,8%. Mismatch này VĨNH VIỄN cho ngày đó, không tự lành. nav_history hiện dừng ở 09-18, thiếu CẢ 09-21 lẫn 09-22 (09-22 sẽ chạy 19:50 tối nay). KHÔNG ghi tay dòng CSV (vi phạm §6). => Backfill 09-21 trở thành ACCEPTANCE TEST của L2/L3: sau khi land, chạy lại lệnh --from-raw trên cho CẢ 2 account, phải điền đúng với DRI mark giá CUM 14.900. Phải xong trước weekly report thứ Sáu (§31 nav_period_returns cần chuỗi NAV liền).
22/09 16:0x — Dispatch Taylor_20260922_090801 (bg, 90') làm L1→L4 corp-action-aware NAV gate. L1 (báo trước 19:00 T-1) có DEADLINE CỨNG: land trước 19:00 T4 23/09 để kịp thử thật trên VPB ISS 26,04% ex-date T5 24/09 (giữ SpaceX 1.100cp + ZaloPay 1.300cp).
