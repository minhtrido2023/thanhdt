# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 22/10 (dọn 00:35 ICT 23/10)
## Chờ USER
- Retro-pattern fail-closed gate (2 câu bus `...-owned-recovery-path` 18/10 + `...-recovery-path-recurring` 19/10; trả lời xong đóng CẢ HAI).
- Lãi CCTG A/B (6,8% vs 5,9%; mặc định giữ 6,80/7,40).
- Rights alert: NB mở (auto_exit_inject.py:343 '>' nên '>='; send_plan_report.sh:1007-1015; reconcile_equity chân tiền credit≠payment; N4 chưa wire dividend_adjusted_return).
- Livermore-cổ-phiếu NO-GO sát biên: thử tiếp = PREREG mới, chờ user. Việc 3 Livermore chỉnh tỉ lệ KHÓA tới >=12 lần chấm.
## Việc theo dõi (Mike)
- Sáng 23/10: xác nhận logs/prefetch_dnse_statement.log; dòng NAV 22/10 19:10 hợp lệ (đã có); phanh lỗ NAV 23/10 tự đo lại. Dọn 2 file .bak_pre_rm_bogus_20261022.
- Hook [pipeline-3b] DD + [pipeline-3c] rights alert chạy thật tối 22/10 → kiểm bq_freshness.log + Trading Daily (3c có thể WARN rc=3).
- Livermore cron 19:45 ICT T2-T6 đã cài; kiểm logs/livermore_trigger.log; DT CRISIS candidate 11/25, kích hoạt thật đầu ~27/10; baseline 21/10 chấm ~19/11.
- nav-snapshot-manual-fills: master 0821ce7fe đã merge; N2/N3 non-blocking + ghi không atomic (gmail_otp_reader.py:43, fetch_dnse_khoplenh_email.py:108).
- LAG: SCL vào ~26/10 ở LAG_LO 8% (hủy nếu VinCons chậm trả); user tự mua quyền, báo Mike số CP từng account. Đọc TAY báo cáo plan 25-26/10. Plan 23/10 dùng KL DRI mới (2.500/1.300).
- FPT Q3 BCTC ~28/10; DRI BCTC Q3 ~30/10 (LNST<22 tỷ→bán 50%).
- tav2_bq.ticker phục hồi đủ ~1294 mã? (Winston/bq_admin); 2 question Wags treo coord-2026-10-19/20.
- PREVENTION CHƯA LÀM (retro 22/10): (a) nav_scripts_2account_selfcheck.py:127 backup tên duy nhất/flock hoặc chạy tmpdir; (b) dispatch.sh --bg cảnh báo 'CHƯA đặt ScheduleWakeup'; (c) cổng dòng NAV ngoài cửa sổ EOD. Retro 10-24: nếu (b) vẫn chưa có → escalate user.
## Đã chốt hôm nay
- N1=A (lô quyền kế thừa entry gốc) merged 771daf4ea; park_holdings bán tay merged 67fc07b5f; cổng NAV merged e18c456b5/0821ce7fe.
- BAL trần sizing NO-GO; LAG price-reaction NO-GO; entry-risk Q1 NO-GO. Livermore live merged f2415a237/25b600fd9.
- Retro 22/10 logged (3 sự cố, Pattern A; Wags GAPS đã sửa), commit 0ca11d82b.
## Mốc
- nav-loss-brake 11-09; review BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27.

- [2026-10-23T04:46:03Z] 23/10: AlphaLens ĐÓNG (user chốt A, commit eda93647a). Paper còn lại giữ nguyên: ORB paused, expvol ckpt 11-10, engine-room 12-01 soi V23.
- [2026-10-23T07:51:54Z] 23/10 TV1: user gửi sơ đồ Vu Gia–Thu Bồn; LN 2026 user ước 140 tỷ (80 hydro+40 tư vấn+?) khớp H1 57,7 + H2 ~82. Theo dõi: BCTC Q3 TV1 ~30/10, sản lượng A Vương (AVC)/SB4 làm chỉ báo sớm mùa lũ Q4; rủi ro lớn hơn là giá PPA sau 2027 (500-600đ) chứ không phải 2026.
- [2026-10-23T08:06:40Z] 23/10 TV1/AVC: Taylor REPORT avc_tv1_hydrology_20261023 = CHƯA ĐỦ DỮ LIỆU (nghiêng KHÔNG). Hợp lưu A Vương/Bung vs SB5 CHƯA xác minh (Mike đọc từ hình, có thể sai). AVC Q3/26 ra 20/10: DT 200 (-2% yoy), LNST 101 (+5%). Mốc: BCTC Q3 TV1 ~30/10.
- [2026-10-23T08:52:19Z] 23/10: Architecture topic lọc nhiễu LIVE (merge 1a647928c, cron digest 18:00 ICT). Theo dõi: digest đầu tiên 18:00 23/10 có post; logs/arch_digest.log; state/arch_digest/. Chưa re-review vòng 2 sau khi sửa theo arch-review.
