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

- [2026-10-18T17:49:49Z] 19/10 00:55: Taylor carry-forward v2 xong (branch research/vnindex-tr-carry-forward-20261019 @37aa83657, worktree wt-Taylor_20261018_172548): G4 nổ 2→0, Δ công bố ≤0,0021pp. quant-skeptic CONFIRMED (medium): phương pháp đúng nhưng (a) DMX (HOSE từ 06/08, ~1,3% vốn hoá, cổ tức 4000đ GDKHQ 18/08) có 0 dòng tav2_bq.ticker/ticker_1m (Mike verify BQ: ticker=0, ticker_1m=0, corporate_action=10) → TR công bố lệch ~+0,05pp, lớn hơn 24 lần phần sửa carry; (b) G9/G10 thiếu đường ack; (c) chặn trộn N khác nhau; (d) fixture selfcheck giá phẳng, 4 mutant sống; (e) '1 ô đổi' sai (ZaloPay dòng 90+93). CHƯA wire, CHƯA đính chính báo cáo. Chờ user: giao Winston/bq_admin hỏi DMX + Taylor vòng sửa a-e.
- [2026-10-18T18:01:15Z] 19/10 01:00: vòng plan CN — Taylor v1 d570de2c9 (branch feat/sunday-plan-round-20261019, worktree wt-Taylor_20261018_173105) arch-review NEEDS_CHANGES (HIGH: job DollarBill ghi muộn/cancel no-op; cần kiểm cuối đêm md5). Vòng 2 dispatched Taylor; sau đó arch-review vòng 2 (opus/medium), rồi trình user duyệt cron (0 12 * * 0 + 0 16 * * 0). KHÔNG cài cron/merge trước khi user duyệt.
- [2026-10-18T19:20:11Z] 19/10 02:20: vòng plan CN — Taylor v2 bc6f53eab (selfcheck 657/0 x3TZ, 38/38 mutant); arch-review v2 = NEEDS_CHANGES hẹp, KHÔNG còn HIGH, 2 MED (MED-1 verify-lệch gỡ cả duyệt lại của user + không khôi phục bản đã quyết; MED-2 recover trong --verify không notify) + LOW-3 rc=5, LOW-7 SC2164, LOW-8 khai side effect. CHỜ USER chọn: A) 1 vòng sửa hẹp Taylor rồi merge+cài cron; B) merge nguyên trạng. Chưa merge/cài cron. Lần chạy đầu 25/10 19:00 ICT. Cron: 0 12 * * 0 wrapper; 0 16 * * 0 --second-chance(+verify); verify 08:30 T2.
- [2026-10-19T03:03:05Z] 19/10 10:05: vòng plan CN MERGED master 6ce022e29 (selfcheck Mike tự chạy 717/0 x3TZ, 43/43 mutant). CHƯA cài cron — chờ user duyệt 4 dòng (CN 19:00, CN 23:00 second-chance, T2 08:30 verify, T2 08:50 verify). Lần chạy thật đầu CN 25/10 19:00 ICT. Worktree wt-Taylor_20261018_173105 + wt-1521183164364754974 có thể dọn sau.
- [2026-10-19T04:14:39Z] 19/10 11:15: ĐÃ CÀI 4 dòng cron vòng plan CN (backup state/crontab_backup_20261019T041428Z_sunday_plan_round.txt). Lần chạy thật đầu CN 25/10 19:00 ICT => quan sát: macro_healthcheck, TV1 ref cuối tuần, 3 injector CN, ceiling_rule A; xem logs/sunday_plan_round.log + Trading Daily. Chưa dọn worktree wt-Taylor_20261018_173105 / wt-1521183164364754974.
- [2026-10-19T04:50:55Z] 19/10 11:55: MERGED master 602d56c33 — treasury_buyback_window_monitor (chỉ báo sự kiện MỚI, state seen, WARN_MAX 180d) + corp_action_feed_canary (ack giá trị MỚI theo (giá trị, n_all)); đã seed state hôm nay. Đóng-bằng-BCTC đã thử & GỠ (OShares BCTC loại cổ phiếu quỹ, GLT đóng nhầm). Mốc: thứ Hai 26/10 monitor kỳ đầu chỉ post sự kiện mới.
