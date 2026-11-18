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
- [2026-11-18T04:36:54Z] [18/11] POW: Taylor r2 xong (tâm 9.792, vùng 7.166-12.419, giá 13.250=1,35x, nhãn ĐẮT, md5 rev2 721c5f28a97867749da9499ca68fa20e). Đã dispatch Taylor dựng báo cáo NĐT (investor_report/). Kế: Mike kiểm grep+xem PDF, ghi dd_price_zones.json + kb/projects/pow-dd-20261118.md, trình user, KHÔNG email
- [2026-11-18T04:37:23Z] DBC: r3 verified; zones ghi (DBC@2026-11-18#1) + kb/projects/dbc-dd-20261118.md xong. Taylor_20261118_043658 đang dựng investor_report; sau đó Mike grep luật 18 + xem PDF, trình user (chưa email)
- [2026-11-18T04:47:35Z] [18/11] POW: DD xong, PDF 9 trang + zones ghi (POW@2026-11-18) + kb/projects/pow-dd-20261118.md; trình user, CHƯA email — chờ 'gửi email' (gửi 1 lần bằng send_dd_report_email.py --pdf --banner, kiểm lại grep luật 18).
- [2026-11-18T04:49:12Z] DBC: DONE — PDF investor_report (md5 d5a8515f…) trình user, CHƯA email; khi user nói 'gửi email': grep luật 18 lại rồi send_dd_report_email.py --pdf --banner figs/title_banner.png (1 lần)
- [2026-11-18T08:15:21Z] [18/11] Khảo sát 9 repo token/context (topic 1572525264964026488): đề xuất CHỈ ccusage (cross-check usage_watch, pinned, read-only) + trial rtk A/B tuỳ chọn; còn lại loại. CHỜ user 'bắt đầu'. Chưa chạy/cài gì. README tải ở /tmp/repo_survey.
- [2026-11-18T08:27:45Z] [18/11] Khảo sát repo xong: ccusage OK (khớp dedupe 0,4%), usage_watch.py đếm trùng 2,1× — patch /tmp/repo_survey/pw/usage_watch_dedupe.patch CHƯA áp, chờ user duyệt + số %/usage thật từ app để hiệu chỉnh USAGE_TOKENS_AT_100; rtk: KHÔNG cài hook (rtk err/test nuốt dòng FAIL).
- [2026-11-18T10:14:22Z] [18/11] ĐÃ ÁP: usage_watch dedupe (merge master) + token-saver mục 5. Hằng số AT_100 rescale 2,5M (chưa hiệu chỉnh vs app: ccdb five_hour utilization=0.0 cho tới khi vượt ngưỡng cảnh báo). rtk không cài.
- [2026-11-18T12:09:36Z] [18/11 19:1x ICT] ĐÃ GỬI email DD POW (pdf md5 4823098c…) + DBC (pdf md5 d5a8515f…) tới địa chỉ user, mỗi mã đúng 1 lần. Không gửi lại.
- [2026-11-18T12:23:51Z] [18/11 19:5x ICT] DD LLM (Lilama, UPCoM, giá 33.300, ADV ~1 tỷ): Bobby xong (sector_read_epc_lap_may_20261118.md, ambiguous), BCTC Q3 tải ở dd_LLM_20261118/src, Taylor đang DD (brief.md). Kế: fundamental-skeptic -> PDF dd-investor-report (KHÔNG email) + dd_price_zones.json + kb/projects/llm-dd-20261118.md
- [2026-11-18T12:43:11Z] [18/11 19:4x ICT] Lead-signal run-up TV1/VCP: Taylor_20261118_122819 xong = NO-GO 0/48 (PREREG md5 ef70c866 khoá trước kết quả; chưa qua skeptic; chưa ghi vào ta-schools-vn NO-GO — chờ user nói bắt đầu). Báo cáo agents/Taylor/research/lead_signal_runup_20261118/REPORT.md
- [2026-11-18T12:46:58Z] [18/11 19:5x ICT] LLM: Taylor r1 xong (giá/tâm 1,05, D=1,69); skeptic r1 REFUTED (thiếu ý kiến NGOẠI TRỪ soát xét AASC H1, biên 7% lạc quan, 13 điểm — skeptic_r1.md). Đã dispatch Taylor r2 (brief_r2.md). Sau r2: KHÔNG skeptic r4 nếu r2 verified; PDF + zones + kb/projects/llm-dd-20261118.md; KHÔNG email
