# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 19/11 → 20/11
- 🔴 DD VCB CHƯA XONG: còn skeptic sau r3, PDF, kb/dd_price_zones.json (0 VCB), kb/projects/vcb-dd-*.md. Câu `Wags/wags-fix-not-confirmed: coord-2026-11-18` GIỮ MỞ; hỏi user có tiếp VCB không.
- bank-nodata R1-R3 ĐÃ merge main (0784394d8); csv + BQ fa_ratings_8l đã regen 20/11 00:2x (ABB/PCB/VAB/VBB 3→4, KLB 2→4). Theo dõi rating_8l.csv 19:20 + cổng. Backup state/bank_nodata_regen_20261120/.
- Plan 20/11: user duyệt; FPT HỦY bán (orders=0); Livermore FPT WAIT_CONFIRM close≥47.950 & vol≥1,5×v20, cancel 42.990. Hỏi user: miễn STOP −10% FPT? mua thêm?
- MBB quyền mua: chờ bán được (cron mbb_rights_tradeable_watch 19:15); patch nhánh session/15727-a CHƯA merge; nhắc 28/11 (khai báo lệch hết hạn 30/11).
- Kiểm sáng 20/11: fill_timing_monitor chạy thật 07:40 ICT (state/fill_timing_monitor.json, logs/fill_timing_monitor.log); đêm: snapshot macro vintage 23:20 ICT (snapshot_date=2026-11-20).
- Chờ user: merge wire dna_report macro-stress (91b9a1ef1, đề xuất chỉ ZaloPay); PREREG-5 DBC (a) sổ rẻ+2 cron / (b) đóng; G3 45% bank-nodata (đề xuất giữ); PDF dd_* ra ngoài git?
- G8 VNINDEX TR: 6 ack hết hạn 27/12; bq_admin chưa lấp DMX/GEL/CRV/HPA/DSH/DVV. Báo cáo tuần 21/11 cần ack (đã có).
- R&D intraday FZ ĐÓNG BĂNG (sổ ngủ). Lịch rà mồ côi tuần CN 10:30 ICT; xoá thật đầu sớm 29/11.
## Mốc
- LAG ADV + corp-action broker-primary xem lại 2026-12-15; measurement audit ~2026-12-27.

- [2026-11-20T04:19:42Z] 20/11 11:2x: DD TTA (Taylor_20261120_041933, brief dd_TTA_20261120) + QTP r3 sửa lỗi khí thải 3.485 tỷ không trừ (Taylor_20261120_041936). Bobby sector read mặt trời/thuỷ điện nhỏ xong; legal-vn: không tự bù giá PPA. Sau Taylor: fundamental-skeptic cả 2, PDF TTA (chưa email), QTP email 17/11 đã gửi bản sai → hỏi user gửi bản sửa; ghi dd_price_zones TTA + QTP rev3 sau skeptic.
- [2026-11-20T04:49:10Z] 20/11 11:5x: TTA r1 skeptic REFUTED mức số (hướng KHÔNG RẺ giữ; thêm kịch bản B' ~5.863; tâm ~6.550) → Taylor_20261120_044902 r2. QTP r3b skeptic CONFIRMED (tâm 7701 sau CK, vùng 6300-8900) → Taylor_20261120_044905 r3c sửa nhỏ; SAU r3c: ghi dd_price_zones QTP rev3 (supersedes QTP@2026-11-17#2), kb/projects/qtp-dd-20261117.md, hỏi user gửi lại email. TTA: sau r2 → PDF (KHÔNG email), dd_price_zones, kb/projects/tta-dd-20261120.md.
- [2026-11-20T04:51:08Z] QTP r3c đã ghi sổ giá rev3 + pointer kb/projects (20/11). Chờ user: gửi lại email QTP bản sửa? TTA r2 job 044902 còn chạy.
- [2026-11-20T05:00:40Z] 20/11 12:0x: TTA r2 skeptic vòng 2 REFUTED nhẹ (chiết khấu thanh khoản 10% phẳng → ~3-4%; tâm ~6.1k sau TK) → Taylor_20261120_050035 làm r3 + investor report (PDF, KHÔNG email). Sau: Mike grep luật, render kiểm, ghi dd_price_zones TTA (assumptions_md5), kb/projects/tta-dd-20261120.md, đính PDF .ccdb-attachments. QTP: chờ user quyết gửi lại email.
- [2026-11-20T05:13:34Z] TTA xong: PDF đính, sổ giá TTA@2026-11-20#1, pointer kb/projects. Chờ user: 'gửi email' TTA? gửi lại email QTP bản sửa?
- [2026-11-20T09:29:35Z] 20/11 16:3x: user lệnh 'Gửi lại QTP bản sửa' → Taylor dựng investor report mới QTP_DD_investor_report_20261120 (dd_QTP_20261117/investor_report_20261120/). Sau: Mike grep luật 18, render, rồi GỬI ĐÚNG 1 LẦN send_dd_report_email.py (+banner, subject không 'đính chính'), báo địa chỉ + md5 PDF.
- [2026-11-20T09:38:08Z] QTP email bản mới ĐÃ GỬI 20/11 16:4x (md5 9e7cbbee…). TTA chờ user 'gửi email'.
