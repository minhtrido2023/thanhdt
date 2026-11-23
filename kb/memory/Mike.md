# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 22/11 → 23/11
- ✅ Đóng 22/11: backup mike-fleet (lượt 17:00Z OK); báo cáo tuần 16–20/11 đã giao (waiver c30875f95, G5 ack merged); VCB r4+PAT r5, VLB DD xong (PDF NĐT đăng Discord, CHƯA email — chỉ gửi khi user báo); cq-hard-boundary mục 1–4 xong (c9810c857).
- Hở prevention (chờ user/arch-review): fleet_backup.sh alert ngay khi "FAIL fleet commit"; cơ chế ack-trước G5/benchmark để weekly không phụ thuộc waiver CN; kiểm weekly delivery T6 trước giờ gửi. Escalate nếu backup FAIL lần nữa do gate khác.
- DD nâng cấp (topic GĐ2 1574099638007505046): nhóm A+B (trừ B7) merged master; B6 skeptic thay xong; B3 cron thesis CHỜ user; F sizing a/b/c (0,5–1% / 2–4% / 5% NAV) CHỜ user chọn; E: SKEPTIC_PATH_REQUIRED_FROM giữ 9999-12-31 tới khi 2 DD kế tiếp có skeptic/rN.json thật → kiểm rồi đề xuất ngày bật. Wakeup audit 22/11: 1/14 dispatch --bg thiếu ScheduleWakeup (session 3778f7bd, chưa điều tra).
- Chờ user: merge wire dna_report macro-stress (91b9a1ef1, đề xuất chỉ ZaloPay); PREREG-5 DBC; G3 45% bank-nodata (giữ); email TTA/VCB/VLB khi user báo; phs_flash; DD VCB/Wags coord-2026-11-18 giữ mở.
- MBB quyền mua: cron 19:15; nhắc 28/11 (hết hạn 30/11). FPT: exit miễn, plan 23/11 hủy STOP SELL; Livermore WAIT_CONFIRM close≥47.950 & vol≥1,5×v20, cancel 42.990.
- Theo dõi 23/11: cron DD ứng viên 19:45 T2; rating_8l.csv 19:20. R&D intraday FZ ĐÓNG BĂNG. Rà mồ côi CN 10:30 ICT; xoá thật từ 29/11.
## Mốc
- LAG ADV + corp-action broker-primary 2026-12-15; measurement audit ~2026-12-27; review quý Bobby ~11-26.

- [2026-11-22T18:14:04Z] [23/11 01:2x] GĐ2 DD: A–D, E, G xong+merged master (72dc4d3bd). CHỜ user: F sizing a/b/c; chọn ca dựng lại rev từ RECONFIRM_RESULTS. Cron thesis_card_watch 01:33 UTC đã cài; chạy 08:33 ICT 23/11 lần đầu — kiểm log mike/logs/thesis_card_watch.log.
- [2026-11-22T23:44:52Z] [23/11 06:5x] Việc dựng lại rev 18 ca đã BÀN GIAO sang topic 1574208662719828062 (lô 1 dispatch 5 job Taylor_20261122_234422..30; plan agents/Taylor/research/dd_rebuild_20261123/PLAN.md). Sizing chuẩn 2–4% đã ghi skill (chưa sửa dòng trong current_ops_ext). Topic cũ 1574099638007505046 dừng — KHÔNG poll ở đó.
- [2026-11-22T23:46:02Z] [23/11 06:5x] Phiên mới topic 1574208662719828062: sửa current_ops_ext sizing xong+merged. Lô 1 (DCM/TTA/PNJ/VCB/MSB) đang chạy, poll bằng ScheduleWakeup; worktree ../wt-mike-1574208662719828062 (branch session/1574208662719828062). Usage 71%.
- [2026-11-23T00:10:58Z] [23/11 07:2x] Lô 1 XONG+áp sổ (909717709): MSB CONFIRMED rev3; TTA/PNJ/VCB/DCM REFUTED_OPEN — hỏi user vòng 3. Lô 2 dispatched 07:2x: CST=Taylor_20261123_001043 CSV=…001046 LLM=…001048 HHS=…001050 VLB=…001052. Quy trình áp sổ: copy artifact nhẹ (không src/pdf) sang worktree, script /tmp/apply_rebuild_lot1.py (mẫu), xoá bản untracked giống hệt ở cây chính trước merge.
- [2026-11-23T00:35:08Z] [23/11 07:4x] Lô 2 XONG+áp sổ (716ce45ef): 5 ca REFUTED_OPEN. Lô 3 dispatched: BSR=Taylor_20261123_003452 GAS=…003454 DBC=…003456 POW=…003458 SZL=…003503. Lô 4 = VCP,QTP,SCL sau lô 3. CHỜ USER: vòng 3 (DCM/PNJ/TTA/VCB/CST…), HHS CK holding 0 vs 27%. Script áp sổ mẫu /tmp/apply_rebuild_lot2.py.
