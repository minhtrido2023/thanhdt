# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-10-20T03:14:43Z] ĐANG DỞ job Taylor_20261020_031433 (gate-block owned recovery, phương án A; wt nhánh feat/gate-block-owned-recovery-20261020, KHÔNG merge) | NEXT: kiểm kê cổng BLOCK bằng grep
- [2026-10-20T03:17:56Z] ĐANG DỞ job Taylor_20261020_031433: wt /home/trido/thanhdt/wt-Taylor_20261020_031433 nhánh feat/gate-block-owned-recovery-20261020 | NEXT: helper bin/gate_block_question.py + wire run_bot.sh/send_plan_report.sh/check_report_cadence.sh + selfcheck
- [2026-10-20T03:21:01Z] [vnindex-tr carry-forward vòng 2 10-20] XONG chờ Mike quant-skeptic vòng 2: nhánh research/vnindex-tr-carry-forward-20261019 (wt-Taylor_20261018_172548). Mở: báo cáo ZaloPay tuần 12-16/10 dòng 90+93 nếu gửi bằng v1; DMX/AAN/LPS thiếu giá chờ bq_admin.
- [2026-10-20T03:22:02Z] ĐANG DỞ job Taylor_20261020_032153 (rating 8L lag phần 1+3, read-only, out agents/Taylor/research/rating_8l_lag_20261020/) | NEXT: data_registry + rating_8l_history.py
- [2026-10-20T03:26:19Z] [gate-block-owned-recovery 10-20] XONG chờ Mike arch-review+merge+cài cron sweep: nhánh feat/gate-block-owned-recovery-20261020 @28f128801 (wt /home/trido/thanhdt/wt-Taylor_20261020_031433), finding gate-block-owned-recovery-20261020. (Thay dòng ĐANG DỞ job 031433.)
- [2026-10-20T03:39:50Z] ĐANG DỞ job Taylor_20261020_033928 (vòng 2 gate-block-owned-recovery, B1-B4+N1-N5,N8; wt-Taylor_20261020_031433) | NEXT: đọc review + code
- [2026-10-20T03:44:21Z] [rating-8l-lag p1+p3 10-20] XONG job Taylor_20261020_032153, REPORT research/rating_8l_lag_20261020/. Mở: 7 ca RD chép quý trước + 125 ca Q1 RD đầu 4 — đề xuất vá eff_date chờ Mike/user; Phần 2 chờ snapshot hằng ngày. (Thay dòng ĐANG DỞ job 032153.)
- [2026-10-20T03:45:58Z] ĐANG DỞ job Taylor_20261020_034545 (rating 8L lag P2 event-study, read-only, out agents/Taylor/research/rating_8l_lag_p2_20261020/) | NEXT: đọc REPORT P1 + data_registry
- [2026-10-20T03:55:05Z] [rating-8l-lag p2 10-20] XONG job Taylor_20261020_034545, REPORT research/rating_8l_lag_p2_20261020/. G1 drift ngan han +1.1-1.4% toi +20/40, chua tach PEAD. (Thay dong DANG DO job 034545.)
- [2026-10-20T04:08:54Z] [gate-block vòng 2 10-20] XONG chờ Mike arch-review lại+merge+cài cron sweep: nhánh feat/gate-block-owned-recovery-20261020 @8bbb6ffe9 (wt-Taylor_20261020_031433). (Thay dòng @28f128801 + ĐANG DỞ 033928.)
- [2026-10-20T04:52:14Z] ĐANG DỞ job Taylor_20261020_045201 (8L lag P2 vòng 2 prereg, out agents/Taylor/research/rating_8l_lag_p2v2_20261020/) | NEXT: PREREG.md + md5 trước khi tính CAR
- [2026-10-20T04:52:34Z] ĐANG DỞ job Taylor_20261020_045223 (rating 8L eff_date guard, wt nhánh feat/rating-8l-eff-date-guard-20261020, KHÔNG merge/KHÔNG ghi fa_ratings_8l) | NEXT: đọc REPORT §3 + verify time
- [2026-10-20T04:57:52Z] [rating-8l-lag p2v2 10-20] XONG job Taylor_20261020_045201: G1/G2 'khong co' theo PREREG (G1 truot b: IS p 0.18-0.19). REPORT research/rating_8l_lag_p2v2_20261020/. (Thay dong DANG DO 045201.)
- [2026-10-20T05:03:08Z] [gate-block vòng 3 10-20] XONG chờ Mike arch-review vòng 3+merge+cài cron sweep+regen production_manifest: nhánh feat/gate-block-owned-recovery-20261020 @76a27add4. (Thay dòng @8bbb6ffe9.)
- [2026-10-20T05:04:10Z] [ticker-mat-243 10-20] CHO restore tav2_bq.ticker (bq_admin/Mike) truoc 17:00 ICT; neu chua -> Mike quyet chan refresh fa_ratings_8l 17:30. Taylor khong tu tat cron.
- [2026-10-20T05:05:53Z] ĐANG DỞ job Taylor_20261020_045223: commit db7fca931 nhánh feat/rating-8l-eff-date-guard-20261020 (wt /home/trido/thanhdt/wt-Taylor_20261020_045223); 4 chân R3 đang chạy logs/ trong research/rating_8l_eff_guard_20261020 | NEXT: md5 + pin_ledger compare + REPORT + finding
- [2026-10-20T05:18:56Z] [rating-8l-eff-guard 10-20] XONG job Taylor_20261020_045223 chờ Mike arch-review+quant-skeptic: nhánh feat/rating-8l-eff-date-guard-20261020 @db7fca931 (wt repo ngoài). Δ R3=0. Mở: tav2_bq.ticker thiếu 243 mã (Winston); dọn wt _repin + cache _exp_r8lguard sau review. (Thay dòng ĐANG DỞ 045223.)
- [2026-10-20T05:50:11Z] ĐANG DỞ job Taylor_20261020_054959 (rating 8L PIT 2010-2014 feasibility, read-only, out agents/Taylor/research/rating_8l_pit_2010_20261020/) | NEXT: đọc rating_8l_history.py + data_registry
- [2026-10-20T05:50:31Z] ĐANG DỞ job Taylor_20261020_055002 (8L forward tracker B1 + costed BT B2, out agents/Taylor/research/rating_8l_forward_bt_20261020/, wt nhánh feat/rating-8l-forward-tracker-20261020, KHÔNG merge) | NEXT: đọc p2v2 REPORT + verify log
- [2026-10-20T05:56:54Z] [rating-8l-pit-2010 10-20] XONG job Taylor_20261020_054959: DUNG DUOC CO DIEU KIEN (survivorship 100%, RD 2012-13 = qend+32 batch). Cho user quyet co dung tiep + PREREG moi. (Thay dong DANG DO Taylor_20261020_054959.)
- [2026-10-20T06:03:56Z] ĐANG DỞ job Taylor_20261020_055002: B1 XONG (wt-Taylor_20261020_055002 @68b34b377, finding đã ghi) | NEXT: B2 kéo px pin -> control C0/C1 -> BT sleeve
- [2026-10-20T06:12:26Z] [rating-8l forward+bt 10-20] XONG job Taylor_20261020_055002: B1 tracker nhánh feat/rating-8l-forward-tracker-20261020 @68b34b377 (wt-Taylor_20261020_055002) chờ Mike review+cron; B2 nhãn 'thiếu N'. MỞ: verdict P2v2 sai do px thiếu 113 mã — pin cho G1 đạt (a)-(d), chờ Mike/quant-skeptic. (Thay dòng ĐANG DỞ 055002.)
- [2026-10-20T06:29:59Z] [gate-block followups 10-20] XONG chờ Mike arch-review+user duyệt merge: nhánh feat/gate-block-followups-20261020 @9534292e0 (wt-Taylor-gb-followups).
