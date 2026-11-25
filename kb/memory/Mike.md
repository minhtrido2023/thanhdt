# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 25/11 → 26/11
- Retro 25/11 đã ghi: kb/incidents/retro/retro-2026-11-25.md (4 sự cố, P1 = guard dựa suy luận gián tiếp/ngưỡng cứng lỗi thời).
- plan-gate-rootfix (Wags) ĐÃ merge (mike 617db0720 → outer 1455b6557), cron 12 dòng đã cài. Theo dõi đêm 25/11: bq_freshness 19:00 + plan_gate_recovery.log 19:40+. P3 follow-up (5 mục) chưa làm. Nhắc user nâng mốc config/trading_calendar_confirmed.json (hiện 2026-12-04). Chạy send_plan_report sau 00:00 PHẢI kèm --plan-date.
- Plan 25/11 + 26/11 đã có; DollarBill HOLD ALL 0 lệnh; park 0%.
- DD: đợt 2–4 + followup ĐÓNG (sổ 181 entry). Còn chờ: NT2 (BCTC 2026), TCH/DRI/VGS (dữ kiện), PVP đọc NQ/BB gốc sau ĐHĐCĐ 30/11, đợt 5 hoãn. POW: dựng lại báo cáo NĐT theo REV4 (tâm 9.387) + chạy lại fundamental-skeptic TRƯỚC email — chờ user duyệt; DD chỉ email khi user báo.
- DCF-VN hành vi: topic 1575099485153927261, Taylor_20261125_104308 (fable/medium) lập plan — poll/đọc kết quả ở topic đó. Dòng earnings-forecast + DCF V3.1 đã merge/đóng NO-GO.
- Giữ nguyên: DRI bán hết/TV1 không giữ; 4 quy tắc user 02/11 (kb/projects/dd-flag-rules-20261102.md).
- Tồn: prevention retro 22/11 (fleet_backup alert…), grep ngưỡng cứng 200 toàn repo, backup 24/11 lỡ chu kỳ chưa rõ nguyên nhân.

- [2026-11-25T17:35:45Z] [26/11 00:37] User duyệt B1+skeptic vòng 2, thứ tự Mike chọn: B1 trước (Taylor_20261125_173540, cùng nhánh pit2) → xong thì quant-skeptic vòng 2 trên script cuối → trình user + xin duyệt merge/cron/registry
- [2026-11-25T18:27:55Z] [26/11 01:3x] Skeptic vòng 2 pit2: (a) PIT CONFIRMED, (b) stepcar CONFIRMED, (c) sổ/cron REFUTED — 3 BLOCKING: freshness đo max_time BCTC (fail 39% tháng) → dùng sync; chưa có script tạo extract CA hằng tháng; chưa có cổng chạy trễ >5 ngày. Chờ user: giao Taylor vòng sửa 3 blocking (+non-blocking) rồi mới cron/registry/merge. Nhánh pit2 chưa merge.
