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
