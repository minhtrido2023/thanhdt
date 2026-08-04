# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-03 (dọn cuối ngày, sau daily retro bước 3/3)

## Trạng thái cuối ngày 08-03
- Daily retro 08-03 XONG: 5 sự cố (1 có file trước, 4 mới bổ sung), 2 pattern. Wags verify
  GAPS FOUND → đã sửa (sự cố #3 job-exitcode thực ra ĐÃ SỬA commit 50666778, không phải
  "chưa sửa" như draft; số đếm LEVER_PACKAGE_UNAUTHORIZED 107 không phải ~85). Entry:
  kb/incidents/retro/retro-2026-08-03.md.
- 6 việc treo từ báo cáo trước (deposit rate, LAG fidelity dispatch, KB editorial catch-up,
  /api/notify UTF-8 fix, wakeup_profile.py wiring, Wags git-add coordination) — TẤT CẢ ĐÃ
  ĐÓNG hôm 08-03, chi tiết đã consolidate vào KB, không cần giữ ở đây nữa.

## Việc treo sang 08-04 (ưu tiên)
1. **Wakeup compliance 08-04**: nếu ≥15% hoặc tiếp tục tăng (đã 9.5%→18.2%) → escalate
   `retro-pattern-recurring-wakeup-compliance-regression` ngay theo bước 6 quy trình retro.
2. `retro-pattern-recurring-silent-cron-spof-2` — cần thêm 2-4 ngày xác nhận cron_health_check
   sạch liên tục (hôm nay ngày 1/3-5, câu hỏi còn PENDING trên bus).
3. `dt5g-live-writer-la` — writer lạ ghi vnindex_5state_dt5g_live 16:21 ICT ngoài mọi cửa sổ
   biết đến; cần Winston đối chiếu ngày trước + xác định danh tính.
4. Kiểm tra job Taylor_20260803_021414 (LAG fidelity research plan, dispatch --bg hôm 08-03,
   opus/high) — chưa có kết quả lúc note trước, cần xem lại khi quay lại.
5. Bridge ccdb-mike.service restart để nhận fix /api/notify (commit cacbfb9c) — cần hỏi user
   trước (ảnh hưởng mọi session), CHƯA làm.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- opus-drift 74.2% — xem lại tuần sau có giảm về baseline không.
- funding_required residual risk; PNJ TTL anomaly_flags (~08-23 review);
  coding_guidelines.md ~39KB gần ngưỡng 40KB.

- [2026-08-04T09:34:02Z] PENDING DECISION user: 2 câu hỏi từ Taylor (job 091700/091703, bus question vol-scale-chase-cap-gate4-can-user-quyet-huong) — (1) netting production (commit ab20a77, 07-27) đang giết evidence paper của CẢ vol_scale_chase_cap lẫn fill_timing từ 07-28 (0 lệnh BUY probe chạm executor); Taylor đề xuất sửa paper_main_probe_plan.py để basket mua≠bán hoặc miễn netting cho account paper. (2) vol_scale_chase_cap gate 4 (real-fill vs proxy) KHÔNG BAO GIỜ đóng được bằng paper (PaperBroker luôn khớp đúng giá limit) — 3 lựa chọn A(re-scope+đóng, Taylor đề xuất)/B(live pilot nhỏ ZaloPay)/C(park). Chưa bật live gì, production không đổi.
