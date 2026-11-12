# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 11/11 → 12/11
- Retro 11/11 ghi xong (kb/incidents/retro/retro-2026-11-11.md). Escalation mở, KHÔNG mở trùng: retro-pattern-recurring-fleet-backup-push-fail-pat-expired (A cấp lại PAT, B deploy key); cũ: bg-dispatch-wakeup-miss, anomaly-flags-stale (chờ user).
- VIỆC MỞ: đối soát fill VGS 11/11 (ATC oid 232411 SpaceX 2400cp, 232401 ZaloPay 1500cp, "New" sau 14:55 ICT, filled 0) bằng email khớp lệnh DNSE/skill dnse-fill-reconciliation; plan 12/11 (VGS+NNC, trần Livermore) đã duyệt 00:2x ICT 12/11.
- Backup mike-fleet: remote kẹt fc5bd02d; ~/.git-credentials mtime 00:08 ICT 12/11 ⇒ chạy lại fleet_backup.sh xác nhận PAT mới.
- Wakeup MISS về 0/12 hôm 11/11 (sau Stop hook G2) — theo dõi thêm vài ngày.
- Fix approved_by newline xong (json.dumps); còn nợ: quét script dựng JSON bằng nối chuỗi.
- Lệnh đối ứng cùng mã cùng phiên: chưa có guard code.

- [2026-11-12T05:18:17Z] DD VCP 12/11: Bobby sector read xong (sector_read_thuy_dien_20261112.md); Taylor job Taylor_20261112_051752 đang làm DD (brief: agents/Taylor/research/dd_VCP_20261112/brief.md). Sau: fundamental-skeptic -> PDF dd-investor-report (KHÔNG gửi email) -> dd_price_zones.json + kb/projects/vcp-dd-20261112.md. Cờ: DT phế liệu, goodwill, góp vốn 1.546 tỷ, quyết định xử phạt thuế.
- [2026-11-12T05:45:38Z] DD VCP: skeptic xong+vòng 2 áp, sổ dd_price_zones ghi (VCP rev1), kb/projects/vcp-dd-20261112.md xong. Taylor job Taylor_20261112_054520 dựng báo cáo NĐT PDF (investor_report/). Sau: Mike kiểm grep + render PNG, đính PDF .ccdb-attachments, báo user, KHÔNG gửi email; release claim topic:dd-VCP-20261112.
