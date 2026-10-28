# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (dọn cuối ngày 27/10, ghi 00:4x 28/10)
## SÁNG T4 28/10 — việc đầu tiên (hạn cứng 08:30)
- MERGE vá funding-ceiling (CHƯA merge, classifier chặn): outer `session/1564443626463957113-funding-ceiling` (wt /home/trido/thanhdt/wt-1564443626463957113-c) + mike `session/1564443626463957113-egg-report` (commit cd2a56798). Phải merge CÙNG LƯỢT trước alert 08:30. Chưa merge ⇒ user chuyển ≥1,4tr SpaceX. Nợ: net_offsetting_orders (plan.py:410-419) rơi hard_no_chase_ceiling_vnd — báo user.
- Plan T+1 28/10 đã duyệt cả 2 TK (23:44): SELL DRI-DISC-01 SpaceX 1250 / ZaloPay 650 @14.400 LO + mua SCL 300/200. Kiểm fill DRI sau phiên; nếu plan bị dựng lại ⇒ mất lệnh bán + duyệt (backup state/plan_redo_20261027).
- Egg: nhắc user chuyển trước gate 09:05.
## Chờ USER
- Bus Wags/wags-fix-not-confirmed: retro-pattern-wakeup (đề xuất B — đã LIVE exit-8 gate f16a39cb1).
- DRI: ghi KB dri-triggers kết luận r4 + giao Taylor sửa REPORT (bỏ 'tái canh hoà vốn', thêm trục có/không tái canh). Mốc: BCTC Q3 chi tiết 30/10, SXKD T10 ~10/11. Giảm 50% đã duyệt, KHÔNG mua.
- LAG capacity: chờ fill thật 15/12. SCL vào ~26/10 ở LAG_LO 8%.
## Retro 27/10 (kb/incidents/retro/retro-2026-10-27.md)
- Pattern A: quyết định user đã chốt không chảy vào bước tự động (plan thiếu SELL DRI). Prevention đề xuất: `data/user_decisions_pending_plan.json` + cổng pre-send fail-closed (gộp nợ (d) lag_dd/ack). Nếu tái diễn 28/10 ⇒ `retro_escalate.py --pattern decisions-not-propagated-to-plan --days 3`.
- Pattern B: vá tiền kẹt cổng duyệt trong cửa sổ hẹp — nhờ user duyệt merge trước hết ngày.
## Mốc
- nav-loss-brake 11-09; DT CRISIS commit sớm ~11/10; Livermore chấm ~19/11; BĐS 11-26; commodity PREREG-2 11-25; LAG 12-15; measurement audit ~12-27; DD DRI/TV1 BCTC Q3 30/10 (cron one-shot session-only); FPT 29/10.
- Nợ prevention retro: (c) cổng NAV ngoài cửa sổ EOD; (d) plan-vs-ack; (e) quét script in cảnh báo stdout; context_pack ~45KB cần trim.

- [2026-10-28T02:52:15Z] DDV: Bobby đọc mù ngành DAP xong 28/10 (B 70/30, file kb/data_registry/market-state/sector_read_fertilizer_dap_20261028.md). CHẤM forecast: S TE 2027-01-31 (TB 4.900) & 04-30 (4.400); DAP TE 01-31 (770). Chờ user duyệt: Taylor tái trọng số kịch bản DDV (Bobby nặng hơn base Taylor). Ngưỡng DDV: đợt1 ≤13.000, đợt2 ≤11.500; không mua.
- [2026-10-28T04:31:08Z] 28/10 11:4x: user yêu cầu cổng mua DRI ≤13.000; đã ghi G0-G7 vào dri-triggers (ngoại lệ thăm dò, cần duyệt từng tranche, chưa wire). Chờ user: script cảnh báo ≤13.100 + checklist.
- [2026-10-28T04:44:59Z] 28/10 12:0x: script DRI gate watch (bin/dri_buy_gate_watch.py) đã merge master ceea8e69d, selfcheck 15/15, Telegram test ok. CRON CHƯA CÀI (classifier chặn crontab) — chờ user cài tay hoặc cho phép; sau đó thêm dòng vào kb/cron_registry. Dòng cron: */5 2-7 * * 1-5 cd WC && TZ=Asia/Ho_Chi_Minh timeout 50 wc_venv/bin/python mike/bin/dri_buy_gate_watch.py run >> mike/logs/dri_buy_gate_watch.log 2>&1
- [2026-10-28T04:54:01Z] 28/10 11:5x: cron DRI gate ĐÃ CÀI (user duyệt), registry ghi. Chờ giá DRI ≤13.100 thì Telegram; mọi tranche cần user duyệt.
- [2026-10-28T05:17:38Z] 28/10 12:3x: DD TV2 — Bobby xong (sector_read_power_consulting_20261028.md, chưa commit/bus); BCTC Q3 tải ở agents/Taylor/research/dd_TV2_20261028/src (scan, đọc bằng pymupdf /tmp/pdflib + Read ảnh); Taylor job Taylor_20261028_051709 đang chạy → sau đó fundamental-skeptic → trình user. Skill ~/.claude/skills/due-diligence đã tạo. Pháp lý TV2: Chủ tịch+KTT cũ bị khởi tố 05/2026 ⇒ WARNING, vẫn phân tích.
- [2026-10-28T05:32:41Z] 28/10 12:4x: DD TV2 XONG — NON @26.050, skeptic CONFIRMED, commit af6123807 (kb/projects/tv2-dd-20261028.md). Mốc: BCTC Q4/26 + kiểm toán FY2026 01-03/2027; QUALIFY cần phải thu CMC ≤470 tỷ + CFO năm trừ tiền ứng ≥0; giá ≤19.500 chỉ chạy lại DD. Chờ user: có muốn thêm TV2 vào watchlist/checklist mốc không.
- [2026-10-28T16:24:26Z] 28/10 23:2x: user duyệt sửa gốc auto_exit/portfolio_status entry-date theo LÔ (VPB ZaloPay SELL 700 sai, đúng 282; SCL display). Taylor job Taylor_20261028_162413 (opus high). Sau đó: arch-reviewer → merge (classifier có thể chặn) → gỡ SELL-VPB-AUTOEXIT-LAG 700 khỏi plan_ZaloPay_2026-10-29, chạy lại auto_exit_inject ZaloPay (qty=282), resend plan report để user duyệt trước 08:45. Plan chưa duyệt (approved None).
- [2026-10-28T16:55:17Z] 28/10 23:5x: arch-review vòng 1 NEEDS_CHANGES (FIFO thứ tự lô quyền mua; stop-loss BAL bị dedup nuốt). Vòng 2 Taylor_20261028_165505 (opus medium) trên nhánh session/lot-exit-20261028 (wt WorkingClaude/wt-lot-exit-20261028). Sau xong: arch-review vòng 2 (CHỈ kiểm required_change) → merge → gỡ SELL-VPB-AUTOEXIT-LAG 700 khỏi plan_ZaloPay_2026-10-29, chạy auto_exit_inject ZaloPay --signal-date 2026-10-28 (kỳ vọng 282), resend plan report.
