# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 16/10 (dọn 00:40 ICT 17/10)
## Việc 17/10 (T7)
- Sáng: xác minh nguồn giá TV1 19.900 (vs DNSE 18.500) trong plan 19/10 SpaceX+ZaloPay (file 23:30 vẫn có buy TV1; bus DollarBill 12:04Z ghi HOLD ALL 0 lệnh ⇒ lệch). Plan chưa duyệt; không duyệt ⇒ HOLD. Đóng ~10 question plan-t1-not-ready-* khi xong.
- Weekly T7: kiểm khối CORR_STEP (mốc 23/10) + bảng 3.2.
- Taylor: nghiên cứu 'dấu vân tay hành vi công bố' GĐ0 (paper-only, thread 1559544863479824557) → quant-skeptic verify khi xong.
## Chờ user quyết
- Escalation retro-pattern-recurring-done-on-branch-not-merged-backlog (A merge ngoài giờ/B mốc cứng+cron/C bỏ): còn 2 nhánh chưa merge = feat/finding-measured-by-20261013, feat/gate-source-check-publish-20261012.
- DDL duyệt cho cột public_datetime của tav2_bq.corporate_action (snapshot_corp_action_daily fail-closed 14-16/10).
- Đính chính số đã công bố (Taylor): benchmark ZaloPay neo 03/07 vs 06/07; vol tháng 8 ZaloPay; EOD SpaceX 08-07 % ngày.
## Chưa điều tra
- ZaloPay DNSE 401 14:00Z (10-07,09,12,15) → giao Winston; adjfactor-drift-scan drift=4; gap N2/N4 universe_gap_fill (1a chạy thật 16/10 PASS); morning-mode lần dùng thật đầu.
## Đã xong 16/10
- ledger-seal SpaceX/ZaloPay chốt + merge f22dccbbb; nav-loss-brake merge d6cf8f276 (mốc xem lại 2026-11-09); cctg-tier2, fund-cashflow, dcf-rf đã merge từ trước.

- [2026-10-16T21:09:55Z] [17/10 weekly audit] EOD report 16/10 cả 2 account đã gửi THIẾU khối giao dịch (bug ATC price=None, đã sửa 87441a7bc) — chờ user quyết gửi lại hay không; report_delivery_gate không bắt được báo cáo mất khối giao dịch (lỗ hổng phủ, chưa vá).
