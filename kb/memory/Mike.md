# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 17/11 → 18/11
- Plan T+1 18/11 (SpaceX+ZaloPay): DollarBill HOLD ALL 0 lệnh (NNC đóng 47.950 > trần Livermore 46.000; BAL FLOOR_FAIL). Chưa thấy user duyệt/phản hồi.
- Retro 17/11 ghi (kb/incidents/retro/retro-2026-11-17.md): 1 sự cố nhẹ — 2 job DollarBill_20261117_120328/120330 usage_limited, auto-resume lần 1/3 (epoch 1794918360); chưa xác nhận resume xong → kiểm `jobs.sh status`.
- Pattern BQ raw thủng ĐÃ ĐÓNG (wire [0b] TI-PRECHECK ở daily_refresh_v34b_linux.sh, merge 3f1dbed08, user chọn A 17/11). Theo dõi 3 ngày: nếu raw thủng mà [0b] không bắt → mở lại.
## Đang chờ / mở
- Taylor: DD VCB (r3 áp xong; mục 6 thiếu công cụ đọc PDF — nếu lặp ≥2 ngày cân nhắc cấp), DD QTP, orb-futures, nav-deriv.
- Taylor có 1 bus question mở 17/11 (chưa đọc nội dung ở retro).
- Mốc: LAG ADV checkpoint 2026-12-15; corp-action broker-primary xem lại 2026-12-15; measurement audit ~2026-12-27.

- [2026-11-18T03:57:49Z] DD DBC (topic 1572457748526800986, 18/11): Bobby sector read xong (kb/data_registry/market-state/sector_read_chan_nuoi_heo_tacn_20261118.md); Taylor job Taylor_20261118_035743 đang chạy (dir agents/Taylor/research/dd_DBC_20261118). Kế: skeptic -> PDF dd-investor-report (CHƯA gửi email) -> dd_price_zones.json
- [2026-11-18T04:14:08Z] [18/11] DD POW (topic 1572462081150685267): Bobby xong (kb/data_registry/market-state/sector_read_phat_dien_20261118.md), BCTC tải xong, Taylor_20261118_041402 đang DD (dir agents/Taylor/research/dd_POW_20261118). Kế: fundamental-skeptic -> PDF dd-investor-report (CHƯA gửi email) -> dd_price_zones.json
- [2026-11-18T04:19:07Z] DBC: skeptic r1 REFUTED (văn bản) -> Taylor r2 đang áp (skeptic_r1.md trong dd_DBC_20261118). Sau r2: dựng PDF dd-investor-report, ghi zones+kb/projects/dbc-dd-20261118.md, trình user, KHÔNG email
- [2026-11-18T04:31:17Z] DBC: skeptic r2 REFUTED(phương pháp) -> Taylor r3 (cuối, skeptic_r2.md) ; sau r3 KHÔNG skeptic r4; Mike tự rerun calc rồi PDF + ghi dd_price_zones.json + kb/projects/dbc-dd-20261118.md; KHÔNG email
- [2026-11-18T04:33:11Z] [18/11] POW: Taylor vòng1 xong (tâm 8.806, giá 13.250=1,50x ĐẮT); skeptic r1 REFUTED (g=2% sai chiều, vốn dự án mới phải theo sổ sách; kỳ vọng tâm ~9.958); đã dispatch Taylor vòng 2 áp skeptic_r1.md. Kế: PDF dd-investor-report (KHÔNG email) + dd_price_zones.json + kb/projects/pow-dd-20261118.md
