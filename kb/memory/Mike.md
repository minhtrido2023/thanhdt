# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-06 00:40 ICT)
- Broker corp-action PRIMARY: branch feat/broker-primary-20261003 CHƯA merge; chờ log shadow T3 06/10 19:25 ICT, rồi user quyết r5 hay merge có điều kiện (r5 cần DISPATCH_ROUND_CAP_OVERRIDE=1 — user quyết).
- Feed vendor corp_action_daily: 05/10 FRESH, 02/10 FAILED; 03/10–04/10 CHƯA xác minh (retro 10-06 phải đọc logs/corp_action_daily.log).
## Đang chờ
- 2 question selfcheck-red Wags (05:08 ICT 05/10: plan_position_drift_check_selfcheck, phs_flash_api_selfcheck) suppress 14 ngày, chưa có answer — đọc nguyên nhân.
- User: plan funnel 8L discretionary (kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md) 4 câu quyết định.
- Plan 06/10 HOLD BAL/LAG chờ duyệt (DollarBill).
## Đã xong 05/10
- Retro 10-05 ghi kb/incidents/retro/retro-2026-10-05.md (commit), draft đã xoá. Fearbuy thứ Sáu đã tắt (backup state/crontab_backup_20261005T172634Z_fearbuy_off.txt).
- Deposit: CCTG chuẩn = 12M cao nhất Big-4, anchor 7,4% (05/10); cron tuần 12/10 08:05 ICT chạy prompt mới lần đầu — kiểm Winston ghi đúng.
## Next
- Retro 10-06: đóng feed corp-action 03/10–04/10; đếm exit 7 dispatch.sh; đọc selfcheck-red.
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

- [2026-10-06T03:31:22Z] 06/10 10:35: ZaloPay BID bán 27 fail 'Trade quantity not enough' — vị thế tách 2 gói (1258:20, 1826:7), _resolve_sell_loan_package_id không tách lệnh theo gói (gap đã ghi sẵn trong docstring 09-29). Đề xuất user: tách lệnh bán theo gói (chạm logic đặt lệnh → chờ duyệt). BID là mã nhiều-gói duy nhất hiện tại.
- [2026-10-06T03:33:30Z] 06/10 10:34: user duyệt B — dispatch Taylor_20261006_033324 (opus high) fix bán tách lệnh theo gói vay, branch fix/sell-split-by-loan-package-20261006 (WC), KHÔNG merge. Sau đó: arch-review → xin user merge; KHÔNG restart bot giữa phiên (ATC hôm nay BID vẫn sẽ fail, 0,93tr).
- [2026-10-06T04:02:39Z] 06/10 11:03: sell-split r1 e7715cd0 arch APPROVED (0 blocking, 10 NB). Dispatch r2 Taylor_20261006_040234 (sonnet) sửa NB-3 streak reset, NB-4 ATC skip vĩnh viễn, NB-5 lỗi im lặng, NB-1 fake DNSE. Sau r2: verify → xin user merge (hiệu lực phiên 07/10). Claim brokers.py giữ tới merge.
- [2026-10-06T04:11:55Z] 06/10 11:12: user duyệt — intraday watch SHADOW MERGED 26b36f9e + cron cài (* 2-7 + 30 1, backup state/crontab_backup_20261006T041001Z_intraday_watch.txt), registry chính thức, 4 mặc định a-d chốt decided_by user. Làn C funnel = nguồn ý tưởng: dispatch Taylor_20261006_041048 (opus high, branch feat/funnel-lane-c-20261006, KHÔNG merge) → arch-review → merge. Shadow 5 phiên: 06,07,08,09,12/10 ⇒ tổng kết ~12/10 15:00.
- [2026-10-06T04:16:40Z] 06/10 11:25: sell-split r2 8a669a9a XONG — Mike tự verify: selfcheck ALL OK (python3+DNA, env -u TZ), 24/24 mutation; hồi quy 57 selfcheck executor/broker HEAD vs base e829f429: rc giống hệt, dòng FAIL giống hệt (11 đỏ sẵn do thiếu data/secrets). X3/X4/X6 sống (reviewer xếp benign). CHỜ user duyệt merge WC main (hiệu lực 07/10).
- [2026-10-06T04:35:57Z] 06/10 11:37: làn C r1 9cf42868 arch NEEDS_CHANGES (mutate script ghi đè bin canonical; 3 test thiếu). Dispatch r2 Taylor_20261006_043550 (opus high) — merge TRƯỚC 19:37 ICT hôm nay (tránh cảnh báo giả 1 lần). Side: pyarrow abort exit 134 (Taylor) không tái lập được (reviewer 0/80). Shadow intraday watch chạy sạch tới 11:26 (log không lỗi).
- [2026-10-06T04:45:16Z] 06/10 11:46: làn C MERGED eeadb970 (r2 ce0d4aa8; Mike tự bắn 3 đột biến reviewer trên bản copy: chết cả 3; selfcheck master 210/210). Cron 19:37 tối nay chạy lần đầu bản mới: seed 64 mục (A9/B18/C37), không báo mới; sáng 07/10 khối D topic 08:00 phải hiện 'Khởi tạo' — kiểm khi user nhắc. Follow-up làn C chưa làm: FIFO hàng đợi, chọn quý mới nhất vs mới-biết, prune state.
- [2026-10-06T05:25:06Z] 06/10 12:25: user duyệt làm 3 follow-up làn C + MÙA VỤ (DRI: QoQ âm do mùa vụ nhưng YoY +192% ⇒ phải lọt). Dispatch Taylor_20261006_052500 (opus high, branch feat/funnel-lane-c-season-20261006, KHÔNG merge). Sau: Mike verify + arch-review 1 lần → merge (giữ tương thích ngược định dạng kết quả).
- [2026-10-06T06:01:05Z] 06/10 13:10: làn C mùa vụ+FIFO+quý mới nhất+dọn state MERGED 5e9c6057 (Taylor 05d1d7c2 + Mike vá B1 9fe3c736: rời C ⇒ gỡ queued_since, tránh QUEUE_EXPIRED giả). Selfcheck master 267/267, đột biến 105/105. Hôm nay làn C không đổi (37 mã), chỉ VLB gắn mùa vụ; DRI KHÔNG lọt (η² 0,10, không mùa vụ). CHỜ user: có chuyển sang C1A (đ/c mùa cho mọi mã: +DRI, −9 mã, IS/OOS lệch dấu) không — sửa 1 dòng + arch-review.
- [2026-10-06T06:23:10Z] 06/10 13:22: user chốt GIỮ làn C bản C1S (không C1A); DRI đi đường đề xuất tay có DD. Ghi plan commit trên master.
- [2026-10-06T06:26:10Z] 06/10 13:27: sell-split 8a669a9a MERGED WC main bởi user lúc 13:24:57 ICT; selfcheck trên main ALL OK (python3+DNA). Bot ZaloPay chiều start 13:10 (trước merge) ⇒ vẫn code cũ, BID PLACE_FAIL_STOPPED 13:11. Hỏi user có restart bot ZaloPay để bán BID hôm nay không; nếu không, kiểm journal BID phiên 07/10 (kỳ vọng 2 chân 20@1258 + 7@1826).
- [2026-10-06T13:13:06Z] 06/10 20:15: shadow cutloss ngày 1 sạch (8 quét 11:10-14:15, 1 kích hoạt PNJ watch-only −6,2%, 0 điều tra, 1 lỗi giá VPI HTTP500, 0 crash). Broker shadow 05+06/10: 0 sự kiện (MBB AIS/TV1 tiền không đổi KL) ⇒ chưa có bằng chứng. broker-primary kẹt r4 NEEDS_CHANGES (1 MAJOR vendor-conflict trước vòng ghi). Đã hỏi user: r5 (override) hay chờ sự kiện cổ phiếu thật.
- [2026-10-06T13:34:51Z] 06/10 20:35: user DUYỆT A — dispatch Taylor_20261006_133445 (opus high, override vòng) r5 broker-primary sửa trọn 6 mục arch v4. Sau: Mike verify + arch-review 1 lần → xin user merge (giữ mặc định shadow).
- [2026-10-06T14:05:12Z] 06/10 21:10: fix portfolio_status ValueError (TV1 value_per_share chuỗi) MERGED mike master ebae8ba1; báo cáo ngày từ 07/10 hết warning. Còn 2 assertion selfcheck cũ đỏ sẵn (lag_exit_hint kỳ vọng T+14/T+20 vs code T+25; risk_warning LAG -15% trả None) — chưa sửa, hỏi user.
