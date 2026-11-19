# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 18/11 → 19/11
- Plan 18/11 SpaceX+ZaloPay: HOLD ALL 0 lệnh. Retro 17/11 đã đóng (DollarBill auto-resume done).
- 🔴 DD VCB CHƯA XONG (arch-reviewer REFUTED việc đóng bus question newdeals-season 01:20Z): còn skeptic sau r3 (D3/D4), PDF investor_report, ghi kb/dd_price_zones.json (0 VCB), kb/projects/vcb-dd-*.md; queue VCB=queued. Câu `Wags/wags-fix-not-confirmed: coord-2026-11-18` GIỮ MỞ làm tín hiệu — chỉ đóng khi VCB xong. Chưa có user chỉ đạo → hỏi user có tiếp VCB không.
- DD 18/11 xong, CHƯA email LLM (PDF md5 cf86360a…; chờ user 'gửi email': grep luật 18 + send_dd_report_email.py --pdf --banner, 1 lần). POW+DBC đã email, không gửi lại.
- Lead-signal run-up TV1/VCP = NO-GO 0/48 (chưa skeptic; chưa ghi ta-schools-vn NO-GO, chờ user).
- usage_watch dedupe đã áp; AT_100=2,5M chưa hiệu chỉnh vs app. rtk không cài.
- Taylor còn: DD QTP, orb-futures, nav-deriv; 1 bus question Taylor mở (chưa đọc).
## Mốc
- LAG ADV checkpoint + corp-action broker-primary xem lại 2026-12-15; measurement audit ~2026-12-27.

- [2026-11-19T03:45:53Z] 19/11 10:47: dispatch Taylor_20261119_034548 (Opus/medium) tìm nguyên nhân trôi G5 VN-Index TR (rổ synth > chính thức +0,52pp/60 phiên); kết quả: agents/Taylor/research/vnindex_tr_g5_drift_20261119/README.md; KHÔNG đổi G5_TOL/chạm chuỗi sealed chờ user duyệt
- [2026-11-19T03:55:01Z] 19/11 10:5x: ĐÃ gửi email DD LLM tới dtienthanh@gmail.com (PDF md5 cf86360a…, 1 lần) — không gửi lại
- [2026-11-19T04:40:47Z] 19/11 11:4x: user bảo mở topic mới intraday-research-19.11 (thread 1572833902333005824) — kế hoạch Fable /tmp/intraday_research_plan_20261119.md; Taylor_20261119_044040 chạy #3 fill_timing recheck (Sonnet/medium, --thread topic mới). Chờ user: gửi deal-list+NAV BOOK-3 (#1/#2/#4), duyệt sổ paper FZ (#8), pre-flight #5. Topic cũ dừng, không poll.
- [2026-11-19T04:44:19Z] 19/11 11:5x: user gửi deal_export.zip (BOOK-3) → /tmp/intraday_deals_20261119/deal_export; dispatch Taylor_20261119_044412 (Sonnet/medium, thread 1572833902333005824) làm #1 + #4 + #2 phần-từ-deal-list, out agents/Taylor/research/intraday_cluster_audit_20261119/. Còn chờ user: #8 sổ paper FZ, #5 pre-flight. #3 Taylor_20261119_044040 đang chạy.
- [2026-11-19T04:50:04Z] 19/11 11:5x: Taylor_20261119_044412 XONG: #1/#4/#2 = NO-GO (0/5 setup, cụm FZ-001 17/FZ-002 15, DSR<0,08, bỏ top-5 cụm thì mean ≤0; #4 chênh +0,31pp CI90 [-0,52;+1,09]). Chưa skeptic (chưa wire nên không cần). Chờ user: #8 sổ paper FZ + đóng băng job mới, #5 pre-flight; engine-rerun #2 cần nhóm kia. #3 Taylor_20261119_044040 còn chạy.
- [2026-11-19T05:07:06Z] 19/11 12:0x: #3 Taylor_20261119_044040 XONG: giữ nguyên fill_timing live (BUY block −18bps PASS, SELL block không PASS, KHÔNG có OOS thật — thiếu intraday 06-13→11/2026; REPORT.md chưa qua skeptic). Chờ user: duyệt kéo intraday 06-13→nay (Winston/Mafee) để chạy lại OOS thật; #8 sổ paper FZ; #5 pre-flight; có giao Taylor phép so 'rổ ngày bán tháo' vs CAPIT không.
- [2026-11-19T05:15:23Z] 19/11 12:2x: user DUYỆT 2 việc: (1) kéo intraday 06-12→18/11 + chạy lại PREREG fill_timing OOS thật = Taylor_20261119_051519; (2) rổ-ngày-bán-tháo vs FZ vs CAPIT = Taylor_20261119_051521 (Taylor Sonnet/medium, thread 1572833902333005824). Còn chờ user: #8 sổ paper FZ, #5 pre-flight.
- [2026-11-19T05:19:10Z] 19/11 12:2x: Taylor_20261119_051521 XONG: rổ vs FZ vs CAPIT = FZ ≈ cược thời điểm (rổ 53%/69% lợi nhuận, excess +0,88%/+0,77% CI90 chứa 0, 17/15 cụm) FAIL. Taylor_20261119_051519 (fill_timing OOS): fetch VCI xong 111 phiên 06-12→11-18 vào data/intraday_1m_ext_20261119/, đang chạy engine.
- [2026-11-19T05:22:05Z] 19/11 12:2x: Taylor_20261119_051519 XONG: fill_timing OOS thật (110 phiên 06-15→11-18) BUY −12,0bps CI95 [−27,4;+2,8] KHÔNG PASS nhưng xa ngưỡng rollback +22 ⇒ giữ live, monitor; SELL +1,2 không PASS. Cả 3 job topic intraday-research XONG. Còn chờ user: #8 sổ paper FZ+đóng băng, #5 pre-flight; việc mở: Mafee xác nhận >60% BUY đặt trước 11:00 có thuộc lịch HYBRID không; fill-vs-open thật cần giá chưa điều chỉnh.
- [2026-11-19T05:29:13Z] 19/11 12:3x: user DUYỆT cả 3 việc: A=Taylor_20261119_052906 (#8 sổ paper FZ + đóng băng, worktree, KHÔNG merge, Mike duyệt diff), B=Taylor_20261119_052908 (#5 pre-flight power, không backtest), C=Taylor_20261119_052911 (fill_timing: phân loại lệnh HYBRID + fill-vs-open thật; Taylor thay Mafee). Sau A xong: Mike duyệt diff rồi cập nhật current_ops/ghi chú; user chưa duyệt merge.
