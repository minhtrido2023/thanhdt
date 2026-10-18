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
