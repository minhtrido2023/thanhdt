# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (dọn cuối ngày 25/10, ghi 00:4x 26/10)
## T2 26/10 (quan trọng nhất)
- Plan T2 SpaceX+ZaloPay ĐÃ user duyệt (22:32 ICT 25/10, qua approve_plan_simple.sh đã sửa cộng egg). CHƯA xác nhận egg đã chuyển (≥107,1tr SpaceX / ≥65,3tr ZaloPay) — gate 09:05 chặn nếu quên: NHẮC user sáng nay.
- SCL vào ~26/10 ở LAG_LO 8% (hủy nếu VinCons chậm trả); user tự mua quyền, báo Mike số CP từng account. ZaloPay jit_unpark file cũ (SCL 900 LAG_HI) chỉ chú thích lệch, không đổi qty.
- Vòng plan CN 25/10 19:00 ZaloPay KHÔNG dựng lại được lớp park → GIỮ plan T6 (đã duyệt); SpaceX/MCH kiểm lại sáng nay.
## Chờ USER
- Bus `retro-pattern-recurring-wakeup-warning-nonblocking-still-missed` (đã POST 17:31Z; đề xuất B: dispatch.sh --bg chặn exit≠0 trừ khi --wakeup-ack/--no-followup). KHÔNG đăng thêm question cùng pattern.
- LAG capacity (R, skeptic CONFIRMED medium): 3 rerun (IS/OOS headline; dời lệnh LAG 5 phiên?; trần KL phiên mở+slippage).
- Livermore-cổ-phiếu: chỉ PREREG mới, không đề xuất. Báo cáo tuần SpaceX rev1 đã email user (user tự gửi NĐT).
## Mốc / theo dõi
- BCTC Q3: FPT 28/10; DRI/TV1 30/10 (CronCreate one-shot 17:50 ICT, session-only; checklist kb/projects/bctc-q3-checklist-fpt-tv1-dri-20261025.md). TV1 dựa BCTC, bỏ chỉ báo thuỷ văn.
- Commodity PREREG-2 cron 11-25 hàng tháng đã cài. nav-loss-brake 11-09; DT CRISIS commit sớm ~11/10; Livermore chấm ~19/11; BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27.
- Nợ prevention retro: (c) cổng NAV ngoài cửa sổ EOD; (d) cổng plan-vs-lag_dd/ack.json; (e) quét script in cảnh báo ra stdout; trigger làm mới anomaly_flags T7/CN + lớp park vào sunday_plan_round.
- context_pack ~45KB cần trim. Retro entry 25/10: kb/incidents/retro/retro-2026-10-25.md (9 mục).

- [2026-10-25T18:24:13Z] 26/10 01:30 Taylor S1-S3 xong+verify, ghi tracking. Chờ user: skeptic vòng 3 cho S? hỏi DollarBill/Mafee RESIDUAL + biến thể dời 3 phiên? Nhắc egg trước 09:05 (~07:30).
- [2026-10-26T01:10:27Z] 26/10 08:1x: user duyệt DD NT2+DDV (jobs Taylor_20261026_011018 NT2, _011019 DDV, opus). Giả thuyết user ghi trong prompt. SZL (KCN, cho thuê) + NNC (chu kỳ đầu tư công, giống SCL) xếp hàng sau, chưa duyệt. Nếu QUALIFY -> fundamental-skeptic. Nhắc egg trước 09:05.
- [2026-10-26T01:25:32Z] 26/10 08:2x: user duyệt DD SZL+NNC+SAS (Taylor opus). NT2+DDV xong, NON cả hai (báo cáo dd_NT2_20261026, dd_DDV_20261026). Nếu QUALIFY -> fundamental-skeptic.
- [2026-10-26T01:48:53Z] 26/10 08:5x: egg_transfer_alert nay gửi Telegram thật (notify_telegram.sh) 15'/lần 08:30-14:30 T2-T6 tới khi FUNDED; commit đã vào master. Sáng nay SpaceX FUNDED 08:45.
- [2026-10-26T04:50:57Z] 26/10 11:5x: user duyệt (1) mẫu DD khối chu kỳ + (2) khung ngành 1 trang 3 ngành. 2 job Taylor opus đã dispatch. BƯỚC SAU (phụ thuộc mẫu xong): chạy lại MÙ 5 mã NT2/DDV/SZL/SAS/NNC bằng job riêng (agent mới, viết khối chu kỳ TRƯỚC khi đọc BCTC/báo cáo cũ), so verdict.
