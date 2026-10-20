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
