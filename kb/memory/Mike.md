# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 20/11 → 21/11
- 🔴 Backup mike-fleet: auto-commit FAIL 19+20/11 do discord-id-gate; `bin/mbb_rights_tradeable_watch.py:19` còn Discord ID trần (THREAD→resolve("trading_daily")), file staged A. Vá TRƯỚC 17:00Z 21/11; hỏi user phương án --no-verify cho backup cron. Verify bằng `git ls-remote` + logs/backup.log, KHÔNG chạy backup_freshness_check.sh (side effect).
- 🔴 DD VCB CHƯA XONG (dd_price_zones 0 VCB); `Wags/wags-fix-not-confirmed: coord-2026-11-18` giữ mở; hỏi user có tiếp không.
- Chờ user: merge wire dna_report macro-stress (91b9a1ef1, đề xuất chỉ ZaloPay); PREREG-5 DBC (a)/(b); G3 45% bank-nodata (đề xuất giữ); email TTA khi user báo; phs_flash (sandbox PHS ngoài, 1 selfcheck đỏ Taylor).
- MBB quyền mua: cron mbb_rights_tradeable_watch 19:15; nhắc 28/11 (hết hạn 30/11); patch session/15727-a chưa merge.
- FPT: plan 20/11 hủy bán; Livermore WAIT_CONFIRM close≥47.950 & vol≥1,5×v20, cancel 42.990; hỏi user miễn STOP −10%/mua thêm.
- Theo dõi: lượt cron DD ứng viên 19:45 đầu T2 23/11; rating_8l.csv 19:20 sau regen bank-nodata; báo cáo tuần 21/11 cần ack G8 VNINDEX TR (ack hết hạn 27/12).
- R&D intraday FZ ĐÓNG BĂNG. Rà mồ côi CN 10:30 ICT; xoá thật từ 29/11.
## Mốc
- LAG ADV + corp-action broker-primary 2026-12-15; measurement audit ~2026-12-27.

- [2026-11-20T22:32:33Z] 21/11 05:3x weekly audit: VÁ backup mike-fleet (70eeb517d, discord-id-gate mbb_rights:19); pre-commit staged 0 Failed; verify dòng mike-fleet trong logs/backup.log lượt 2026-11-21T17:00Z
