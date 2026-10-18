# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 18/10 (dọn 00:40 ICT 19/10)
## Việc 19/10 — TRƯỚC 09:00 ICT
- Plan T+1 SpaceX+ZaloPay 19/10: file mtime 16/10 23:30 (TV1 plan lệch giá DNSE; DollarBill HOLD ALL). Refresh giá DNSE→dựng lại plan hoặc xác nhận HOLD; không duyệt ⇒ HOLD. Đóng question plan-t1-not-ready-*.
- Chuỗi 19:00 T2 = lần đầu chạy bq_freshness_check.sh bản mới (gate-source): xem logs/bq_freshness.log. Kiểm bus/_measured_by_warn.jsonl + rotate trong fleet_housekeeping.
## Đang chờ
- Taylor_20261018_172548 (carry-forward giá mã không khớp lệnh, user duyệt hướng; KHÔNG wire) → quant-skeptic → trình user (đổi số công bố từ 25/06).
- User quyết: áp reports/ZaloPay_weekly_..._.md.proposed_fix (sửa 2 câu 'chưa có số') + gửi lại; gửi lại EOD 16/10 (thiếu khối giao dịch).
- Escalation retro-pattern-recurring-fail-closed-gate-without-owned-recovery-path (cổng BLOCK cần owner+hạn+lệnh recover; quét placeholder trong delivery gate) — chờ user.
- Taylor đính chính số công bố: benchmark ZaloPay neo 03/07 vs 06/07; vol tháng 8 ZaloPay; EOD SpaceX 08-07 %ngày.
## Đã chốt 18/10
- Weekly 12→16/10 gửi xong (ack G4 14/10 user xác nhận). bq_admin: 100 mã 14/10 là no-trade, BQ đúng (finding trên bus).
- Merged gate-source + measured-by; code ack G4 c3ae7dac4. Opus-rule siết, thử tới 25/10 (xét hạ cron wags_autofix/selfcheck sweep xuống Sonnet sau spend_report 25/10).
## TODO
- data_registry corporate_action_bq.md qua .proposed §13 (vintage 17/10). ZaloPay DNSE 401 14:00Z chưa giao Winston. Nhánh mike còn: 1558282936489611354 (weekly), 1559443521747026040 (DGC note); outer research/repin-dep1m-2709 giữ (mốc 30/10), session/...-dna hỏi user.
- Mốc: nav-loss-brake 2026-11-09; measurement audit ~12-27; review BĐS ~11-26.

