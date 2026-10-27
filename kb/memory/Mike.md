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

