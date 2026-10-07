# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-07 00:40 ICT)
- Broker corp-action PRIMARY: MERGED mike master dd893add, mặc định SHADOW. Trước live: m2/m3 test, m4 quyết I2 xuyên lượt. Cron 19:25 tối 07/10 chạy bản mới lần đầu → kiểm corp_action_auto_confirm.log khi user hỏi.
- Sell-split BID ZaloPay (merge WC 8a669a9a 13:24 ICT 06/10): CHƯA xác minh bot đã restart (bot start 13:10 trước merge).
## Đang chờ
- USER: journal BID phiên 07/10 (kỳ vọng 20@1258 + 7@1826). Nếu thiếu → restart bot có chủ đích (user/Mafee quyết).
- USER: Pattern A polish-chain (escalate `retro-pattern-recurring-polish-chain-rounds-override-recurring`) chọn a/b/c.
- USER: plan funnel 8L discretionary (kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md) 4 câu quyết định.
- Plan 06/10 HOLD BAL/LAG chờ duyệt (DollarBill). Plan 07/10 SpaceX park shortfall 10,31tr (4 mã sellable0 T+2) chờ duyệt.
- Selfcheck-red còn triaged, chưa có chủ: plan_position_drift_check, capit_lever, cctg_deposit_wiring, wags_autofix_postq (05/10).
- Corp-action feed 03/10 chưa có bằng chứng (log không có dòng) — đọc trước khi kết luận.
- Shadow cutloss (intraday_price_watch) chạy từ 06/10 11:10; tổng kết ~12/10. Tin "SHADOW ..." KHÔNG phải lệnh thật.
- Cron tuần 12/10 08:05 ICT (CCTG/Big-4 prompt mới) — kiểm Winston ghi đúng.
## Đã xong 06/10
- Retro 10-06 ghi kb/incidents/retro/retro-2026-10-06.md (commit 619659a7), Wags GAPS FOUND đã sửa.
- Làn C funnel MERGED (eeadb970, 5e9c6057); user chốt giữ C1S, không C1A.
- portfolio_status fix MERGED (ebae8ba1, bdddff54); báo cáo từ 07/10 hết warning.
## Next
- Sáng 07/10: khối D topic 08:00 phải hiện 'Khởi tạo' (làn C) — kiểm khi user nhắc.
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

- [2026-10-07T02:20:45Z] 07/10 09:2x: user chọn (a) polish-chain → merged 6daeca8d (override cần REASON; review toàn bộ trước vòng 2), bus question đã đóng decided_by=user. Theo dõi: vòng 3+ còn lặp tuần tới ⇒ đề xuất (b).
- [2026-10-07T03:05:48Z] 07/10 10:05: user giao r7 broker-primary (test m2/m3 + luật m4: đã hỏi ex A, broker thấy ex B gần ⇒ BQ có đủ 2 sự kiện thì ghi, không thì hỏi lại; BQ lỗi ⇒ hỏi). Job Taylor_20261007_030542 opus high. Xong ⇒ Mike tự selfcheck đa TZ + arch-review 1 lần ⇒ xin user duyệt merge.
- [2026-10-07T03:26:39Z] 07/10 10:3x: Bobby nâng lên đọc chi phí vốn bằng bảng đa-proxy A-E (charter ~/.claude/agents/macro-strategist.md + prompt interim, merge 0a3ee57f; mốc kb/projects/vn_realestate_monthly_checks/2026-10-multiproxy.md). CHỜ USER: chốt ngưỡng 5-6 chỉ báo tăng ngầm + có thu thập CCTG 6M song song 12M trong cron tuần không.
- [2026-10-07T03:35:16Z] 07/10 10:35: r7 broker-primary (179e4686, wt-bp-r7-1007) arch-review NEEDS_CHANGES: MAJOR-1 _asked_rows bỏ câu vendor-only/held-unknown ⇒ live ghi KL sai ex không tra BQ; minor-1 BQ khớp DIV cho sự kiện KL; minor-2 gửi bù A dặn sửa B; minor-3 test AMBIGUOUS/DEFER/ex hỏng; minor-4 deadline BQ tổng. m2/m3 ĐẠT. Chờ user chọn: r8 sửa rồi merge / merge shadow ngay.
- [2026-10-07T03:38:42Z] 07/10 10:5x: user duyệt (1) 5 ngưỡng tăng ngầm → tracker + prompt Macro Watch (mike 5065b950); (2) CCTG 6M song song: append_cctg_rate.py --series 6m → data/cctg_rate_vn_6m_events.csv, chuỗi 3 trong cron tuần (WC b3169f92). Kiểm 12/10 sau 08:05: file 6M có dòng đầu + Winston báo đủ 3 chuỗi.
- [2026-10-07T03:44:38Z] 07/10 10:45: user duyệt (1) ⇒ r8 broker-primary sửa 5 lỗi r7 trên wt-bp-r7-1007; xong ⇒ selfcheck đa TZ + arch-review 1 lần ⇒ xin merge.
- [2026-10-07T04:30:30Z] 07/10 11:3x: intraday-watch VNINDEX last=None = DNSE cache /price/ohlc theo URL cố định (cũng làm idio dùng VNI kẹt 09:29). Vá merged mike 1b60ecae (to=phút hiện tại + chặn bar >5'). Kiểm lượt 13:00/13:15 trong data/intraday_watch/shadow_2026-10-07.jsonl: vni[0] phải tươi, hết HEALTH vnindex.
- [2026-10-07T05:02:03Z] 07/10 12:0x: r8 broker-primary (58aa852d) arch-review NEEDS_CHANGES: 5 mục r7 ĐÓNG THẬT (782/784 × 8 env, 538/538 đột biến, probe vendor-only nay hỏi). MAJOR-r8-1 MỚI: :921 loại câu vendor đã closed (resolve qua broker CASH_DIVIDEND ở A) ⇒ B ghi live không tra BQ (probe2 /tmp/arch_r8/). Sửa 1 dòng + đảo test MAJOR-1c + test probe2 + P8. Chờ user chọn r9 sửa nhỏ / merge shadow.
- [2026-10-07T05:06:52Z] 07/10 12:07: user duyệt r9 ⇒ Taylor sửa MAJOR-r8-1 + test probe2/P8 (opus medium) trên wt-bp-r7-1007; xong ⇒ selfcheck + review mục tiêu ⇒ xin merge.
- [2026-10-07T06:12:02Z] 07/10 13:1x: broker-primary r7-r9 MERGED mike master 2563e481 (arch-review r9 APPROVED, user duyệt (1) 12:06). Sau merge: selfcheck 785/0 (3.10) 787/0 (3.12), dry-run 10-06 rc=0 registry sha 21a88fb5 không đổi, MIKE_CA_BROKER_SOURCE unset ⇒ shadow. Cron 19:25 tối nay chạy bản mới. Còn để sau live: m3 confirmed khi BQ thiếu, m4 join trần, 7 đột biến tương đương/nhẹ.
- [2026-10-07T06:23:44Z] 07/10 13:2x: user yêu cầu fix 2 lỗ test m3 (confirmed[tk] khi BQ thiếu/lỗi) + m4 (th.join(left)) ⇒ job Taylor_20261007_062338 sonnet medium, test-only, worktree wt-bp-r10-1007. Xong ⇒ Mike tự chạy selfcheck đa TZ + kiểm 2 đột biến chết ⇒ xin user merge (không cần arch-review đầy đủ, chỉ test).
- [2026-10-07T06:58:40Z] 07/10 13:5x: r10 broker-primary test-only (6e26dbe1, wt-bp-r10-1007) Mike verify: code prod 0 dòng đổi; selfcheck 788/0 (3.10) 790/0 (3.12) × 3 TZ; đột biến m3 (2 FAIL có tên) + m4 (1 FAIL có tên) bị bộ mới giết, bộ cũ để lọt (785/0). Chờ user duyệt merge.
- [2026-10-07T07:40:33Z] 07/10 14:4x: r10 MERGED mike master bacf6e99 (user duyệt 14:39). Selfcheck master 788/0 (3.10) 790/0 (3.12); crontab không đặt MIKE_CA_BROKER_SOURCE ⇒ shadow. Còn để sau live: 7 đột biến tương đương/nhẹ. Worktree wt-bp-r7-1007 + wt-bp-r10-1007 có thể dọn.
- [2026-10-07T12:09:56Z] 07/10 19:2x: DT5G FROZEN 19:03 = báo GIẢ (DollarBill ad-hoc get_gated_state(today,today) → cửa sổ rỗng → NaT vào SQL). Guard merged WC b28d436f. Publish 19:01 DT5G_macro NEUTRAL đúng, plan 08/10 dùng golive_state_today.json. Phụ: cache local thiếu bảng universe_pit ⇒ breadth guard inactive khi chạy qua BQ_LOCAL_CACHE (chưa xử).
- [2026-10-07T12:39:34Z] 07/10 19:4x: user duyệt → cache local thêm universe_pit (WC a06c3ba3, nạp full khớp BQ 3.531.536 dòng). Breadth guard DT5G hết inactive; 2014-2026 0 ngày đổi state. Kiểm sáng 08/10: data/refresh_v34b_linux_2026-10-08.log KHÔNG còn 'breadth guard inactive' + sync.log đêm 07/10 có universe_pit delta OK.
