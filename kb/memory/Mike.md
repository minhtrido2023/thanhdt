# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 21/11 → 22/11
- ✅ Backup mike-fleet ĐÃ VÁ (70eeb517d); lượt 17:00Z 21/11 commit tự động OK (d7f67955d). Còn hở: fleet_backup.sh chưa alert ngay khi "FAIL fleet commit"; chờ user/arch-review: alert + pre-commit trên staged mới + --no-verify cho backup. Lần FAIL kế do gate khác = tái diễn 2 ⇒ escalate.
- 🔴 Báo cáo tuần 16–20/11 (SpaceX+ZaloPay): Taylor INCOMPLETE chặn Q9 G5, cần ack G8 VNINDEX TR; trạng thái gửi Discord/email CHƯA verify — kiểm bằng report_delivery_gate (có side effect gửi) sau khi user ack.
- 🔴 DD VCB CHƯA XONG; `Wags/wags-fix-not-confirmed: coord-2026-11-18` giữ mở; hỏi user có tiếp không.
- Chờ user: merge wire dna_report macro-stress (91b9a1ef1, repo WorkingClaude, đề xuất chỉ ZaloPay); PREREG-5 DBC; G3 45% bank-nodata (đề xuất giữ); email TTA khi user báo; phs_flash.
- MBB quyền mua: cron 19:15; nhắc 28/11 (hết hạn 30/11).
- FPT: plan 20/11 hủy bán; Livermore WAIT_CONFIRM close≥47.950 & vol≥1,5×v20, cancel 42.990; hỏi user miễn STOP −10%/mua thêm.
- Theo dõi: cron DD ứng viên 19:45 T2 23/11; rating_8l.csv 19:20.
- R&D intraday FZ ĐÓNG BĂNG. Rà mồ côi CN 10:30 ICT; xoá thật từ 29/11.
## Mốc
- LAG ADV + corp-action broker-primary 2026-12-15; measurement audit ~2026-12-27.

- [2026-11-22T04:28:18Z] Báo cáo tuần 16-20/11 bị chặn bởi G5 (11-11 lệch +0,52>0,5, 1 điểm duy nhất, nay +0,10) — chờ user duyệt waiver Q9 2 file + hướng sửa cấu trúc (G5 nằm vĩnh viễn trong MTD/inception); chưa sửa gì
- [2026-11-22T09:41:47Z] Báo cáo tuần 16-20/11: ĐÃ gửi (waiver c30875f95) + G5 ack merged (selfcheck 365/159) + ack 11-11 diff_bp=52 ghi data/benchmark/vnindex_tr_acks.json; MTD nay status ok không cần waiver. Xong.
- [2026-11-22T09:45:06Z] DD VLB (topic 1573994100712280134, 22/11): Bobby xong; Taylor job Taylor_20261122_094500 đang chạy; kế: skeptic → PDF (CHƯA gửi email) → dd_price_zones + kb/projects/vlb-dd-20261122.md; dir agents/Taylor/research/dd_VLB_20261122
- [2026-11-22T09:46:37Z] [22/11 17:0x] topic 1573364582402101400 ĐÓNG: comment :350 sửa (098d30e22), TTL/corp_action_lib.bq đo xong không cần sửa. Chỉ còn theo dõi cron DD 19:45 T2 23/11.
- [2026-11-22T09:47:31Z] [22/11 16:5x] User yêu cầu mở topic mới: 'VCB vòng 4 + PAT r5' id=1573998148680941748 (topic cũ 1571691433084325938 ĐÓNG, KHÔNG poll). Taylor VCB R4 job Taylor_20261122_094712, PAT r5 job Taylor_20261122_094714 (sonnet, nền, --thread topic mới). wake_thread đã gọi phiên mới theo dõi + hoàn tất chuỗi (đối chiếu → PDF VCB KHÔNG email → zone → đóng bus q newdeals-season-2026Q3 dd-queue; PAT ghi sổ rev mới). Ghi chú: DD VCB trước đó dừng 17/11 sau skeptic R3 (REFUTED văn bản).
