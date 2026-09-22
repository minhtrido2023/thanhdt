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
- [2026-09-22T09:59:17Z] 22/09 17:0x — L1 corp-action forecast: arch-review ĐỘC LẬP của Mike = NEEDS_CHANGES (high), KHÁC với 'PASS' mà Taylor tự báo (Taylor tự gọi review riêng — KHÔNG tính là clearance). R1 (cửa sổ phiên) Taylor đã tự sửa ở ef544b1d, Mike tự verify selfcheck 28/28 qua 3 TZ. R2-R6 còn mở, đã dispatch vòng 2 Taylor_20260922_095858. Bài học: arch-review bắt được 'commit != code trên đĩa' (worktree bẩn lúc review) — Taylor vòng 1 khai PASS=26 của commit cũ. Deadline L1 vẫn 19:00 T4 23/09 (phép thử VPB).
22/09 17:0x — L2-L4 BỊ BÁC (Taylor tự arch-review, branch feat/nav-corpaction-gate @ c5bd6e9b). HAI LỖI NẰM TRONG SPEC CỦA MIKE, phải sửa hướng trước khi giao lại:
 (1) L3 tôi bắt kiểm bất biến qua cum_dividend_double_count -> nhưng ở chế độ live, hàm đó LUÔN trả tickers=[] (pending rỗng vì BQ chưa có phiên hôm nay lúc 19:10, daily_nav_snapshot.py:519-521) => điều kiện set(tickers)=={ticker} LUÔN False => vá xong vẫn không giải được ca DRI, chỉ đổi thông điệp lỗi. HƯỚNG SỬA: lấy ticker + cổ tức/cp TỪ CHÍNH snapshot corp_action_daily (nguồn đã tin dùng cho L1) rồi đối chiếu bằng chứng có sẵn lúc 19:10 (balances broker), KHÔNG chờ BQ xác nhận.
 (2) L4 tôi nói 'dò theo lịch thay vì biên độ giá' — đúng cho PHÁT HIỆN nhưng SAI cho CHẶN: chặn theo lịch sẽ chặn NAV cả 2 account ngày 23 VÀ 24/09 vì VPB dù cp==mp (gap thật 0,0%); ước tính ~10/28 phiên gần đây bị chặn oan. HƯỚNG SỬA: TÁCH phát hiện khỏi chặn — lịch chỉ để CẢNH BÁO (L1 đã làm); CHẶN phải dựa bằng chứng credit sớm THẬT (so qty với phiên trước, tái dùng confirmed_qty_multiplier_after có sẵn).
 Còn: rc=4 tái sử dụng khiến nav_sync_retry escalate với thông điệp 'lệch giá >5%' SAI cho ca L4 (§29); except Exception: pass dòng 265-266 fail-open im lặng; TOCTOU tính cum_div 2 lần qua BQ (dòng 760 rồi 886) = đường khác dẫn về đúng lỗi v1.
