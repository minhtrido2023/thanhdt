# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 17/10 (dọn 00:40 ICT 18/10)
## Việc 18-19/10
- TRƯỚC 09:00 ICT T2 19/10: plan T+1 SpaceX+ZaloPay (file mtime 16/10 23:30, TV1 giá plan 19.900 vs DNSE 18.500; DollarBill HOLD ALL lệch) — refresh giá DNSE→dựng lại plan hoặc xác nhận HOLD; không duyệt ⇒ HOLD. Đóng các question plan-t1-not-ready-*.
- Weekly 12→16/10 bị G4 (rổ TR 351→333 mã cổ tức): xác nhận rebase rổ TR rồi chạy lại report_delivery_gate; monthly 31/10 sẽ gặp lại. Nếu pattern "cổng thiếu đường phục hồi" tái diễn 18/10 ⇒ escalate.
- Taylor: nghiên cứu 'dấu vân tay hành vi công bố' GĐ0 (paper-only, thread 1559544863479824557) → quant-skeptic verify.
## Chờ user quyết
- Gửi lại EOD 16/10 (thiếu khối giao dịch; gate chưa bắt lỗi thiếu nội dung).
- Escalation retro-pattern-recurring-done-on-branch-not-merged-backlog (A/B/C): 2 nhánh chưa merge feat/finding-measured-by-20261013, feat/gate-source-check-publish-20261012; đề xuất mốc cứng 25/10.
- Đính chính số công bố (Taylor): benchmark ZaloPay neo 03/07 vs 06/07; vol tháng 8 ZaloPay; EOD SpaceX 08-07 % ngày.
## TODO
- data_registry corporate_action_bq.md qua .proposed §13: public_datetime từ vintage 17/10; ≤13/10 NULL; thiếu vintage 14-16/10 (snapshot đã vá b1c183b3a).
- ZaloPay DNSE 401 14:00Z chưa giao Winston; selfcheck-red đã recovered (b4a8de8fc).
## Đã xong
- snapshot corp_action fix (A duyệt) merge b1c183b3a; ledger-seal, nav-loss-brake (mốc 2026-11-09).

- [2026-10-18T02:17:28Z] 18/10 09:40: HOÀN TẤT dọn nhánh: MERGED gate-source (3e5eb6d3b) + measured-by (25fdf2077) vào master (selfcheck x2TZ xanh), đóng escalation retro-pattern-recurring-done-on-branch-not-merged-backlog (decided_by user). User đã chạy delete_branches.sh; Mike xoá thêm 12 branch (SHA ở ~/wt_rescue_20261016/deleted_branches.txt). Còn: mike 2 branch session đang có worktree (1558282936489611354 weekly rev chưa gửi; 1559443521747026040 DGC note), outer: research/repin-dep1m-2709 (GIỮ, mốc rebase knob 30/10) + session/1522576692638388364-dna (tweak nhãn dna_report, hỏi user). KIỂM: sau finding đầu tiên có bus/_measured_by_warn.jsonl; retro 00:30 có dòng [measured-by-warn]; thêm file đó vào fleet_housekeeping rotate; chuỗi 19:00 T2 19/10 là lần đầu chạy bq_freshness_check.sh bản mới (gate-source) — xem logs/bq_freshness.log.
- [2026-10-18T03:38:44Z] 18/10 10:50: user duyệt siết luật Opus (merge 6cb05c063); thử tới 25/10; hoãn: nhắc cơ học dispatch.sh VÒNG 2+opus, hạ cron wags_autofix/selfcheck-red sweep xuống Sonnet — xét sau khi có số tuần sau (spend_report 25/10).
- [2026-10-18T04:14:11Z] 18/10 11:15: weekly 12-16/10 bị G4 do BQ ticker thiếu 100 mã (26 HOSE) ngày 14/10 (Winston: không có đường backfill ticker; cần bq_admin nạp lại). Code ack G4 (n_prev,n) đã merge c3ae7dac4 (arch-review 2 vòng, selfcheck 155). CHỜ USER xác nhận ghi ack data/benchmark/vnindex_tr_acks.json {G4:[{date:2026-10-14,n_prev:351,n:333,confirmed_by,reason}]} rồi chạy lại report_delivery_gate 2 báo cáo tuần. acked_g4_days chưa có consumer in ra báo cáo.
- [2026-10-18T10:44:09Z] 18/10 17:50: user xác nhận → ghi ack G4 14/10 (data/benchmark/vnindex_tr_acks.json, gitignored), regen bảng 3.2, gate COMPLETE cả SpaceX+ZaloPay weekly 12-16/10 (đã gửi Discord+email). LỖI: ZaloPay đã gửi còn 2 câu 'chưa có số' cũ (dòng 99, §6.1) → bản sửa ở reports/ZaloPay_weekly_..._.md.proposed_fix; CHƯA áp/gửi lại — hỏi user (sửa file đổi sha → cron check_report_cadence có thể tự gửi bù). SpaceX không bị. bq_admin chưa được nhờ nạp lại 14/10.
- [2026-10-18T17:08:20Z] 19/10 00:15: bq_admin báo 100 mã KHÔNG giao dịch 14/10 → dữ liệu BQ đúng, không cần nạp lại (request.md ghi ĐÃ RÚT). Ack G4 14/10 giữ nguyên, reason đã sửa. 26 mã HOSE ≈0,36% vốn hoá rổ. ZaloPay đã gửi còn 2 câu 'chưa có số' sai → .proposed_fix cập nhật lý do mới; CHỜ user quyết áp+gửi lại. Đề xuất sau: G4-số-mã sẽ lặp (16/76 phiên) → cân nhắc carry-forward mã không khớp lệnh (đổi phương pháp, cần quant-skeptic+user).
- [2026-10-18T17:25:55Z] 19/10 00:30: user duyệt HƯỚNG carry-forward giá mã không khớp. Dispatched Taylor_20261018_172548 (opus, thiết kế+đo tác động, KHÔNG wire). Sau khi xong: quant-skeptic phản biện → trình user (số công bố cũ đổi từ 25/06). ZaloPay weekly sửa 2 câu: vẫn chờ user.
