# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-06 (dọn cuối ngày, sau daily retro bước 3/3)

## Trạng thái cuối ngày 08-06
- Daily retro 08-06 XONG: 8 sự cố + 4 pattern. 2 pattern escalate từ 08-05 (paper_checkpoint_
  escalation.sh, dt5g-live-writer-la KAFFA_WINDOW) đều ĐÓNG trong đêm — escalate mechanism hoạt
  động đúng thiết kế. 0 escalate mới hôm nay (2 pattern mới chỉ lần đầu quan sát, ghi Prevention
  theo dõi). Wags verify GAPS FOUND → đã sửa (bus-sweep count sai, dòng jit_unpark thiếu info,
  cột "Nguồn gốc" nêu tên agent cụ thể vi phạm blameless). Entry: kb/incidents/retro/
  retro-2026-08-06.md.
- L2 JIT unpark (park thụ động) đã WIRE production hôm nay (04:23Z) — DollarBill bắt buộc chạy
  compute_jit_unpark.py sau khi viết orders[]. Đóng câu hỏi PARK-thụ-động từ 08-03.
- PARK trim (L1) không kịp thực thi phiên chiều 08-06 (classifier chặn 2 lần, đúng thiết kế) —
  user chốt để cron 19:00 ICT tự tính lại ngày mai. Verify sáng 08-07: plan_*_2026-08-07.json
  có park_trim_proposal decision=TRIM (không BLOCKED_RECONCILE, VHM CONFIRMED).

## Việc treo sang 08-07 (ưu tiên)
1. **Verify độc lập fix VHM** (NAV-report + LotBook corp-action) — 2 ngày liên tiếp chưa ai verify
   ngoài Taylor tự chạy lại script. Cần quant-skeptic/arch-review thật.
2. **lag-sizing-basis-lech-2-account** (finding DollarBill 17:25:23Z 08-06): SpaceX size LAG theo
   `%active_nav` sai mẫu số, phải là `%LAG_book`. Job hôm nay chỉ override 1 lần chạy (TV2/DRI) —
   cần Taylor/Mike xác nhận chuẩn + soát lại các phiên SpaceX trước có oversize thật không.
3. **compute_jit_unpark.py phương án C**: đã xây + quant-skeptic CONFIRMED 6/6 (job
   Taylor_20260806_033014) — chờ quyết định WIRE vào production.
4. **"Aborted job không kill tiến trình con"** (case Taylor_20260806_025532 orphan process) —
   cần xác nhận cách sửa cơ chế dispatch-orchestration, chưa tự triển khai (blast radius chưa rõ).
5. **Quy tắc "closure event cùng topic khi tự xử lý việc đang treo câu hỏi"** — vá 1 lần cụ thể
   (KAFFA_WINDOW case), cần khái quát hoá vào kb/ops_runbook.md.
6. Theo dõi: wakeup compliance (10% miss 08-06, cải thiện từ 25% 08-05, chưa về 0%); Pattern 2
   retro 08-05 (test code ghi bus production thật, chưa có bằng chứng mới để đóng/bác).

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Paper-main netting fix (Taylor_20260804_094514): cần xác nhận LIVE end-to-end.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- funding_required residual risk; PNJ TTL anomaly_flags (~08-23 review);
  coding_guidelines.md ~40KB gần ngưỡng; bin/crontab_add_line.sh wrapper (khuyến nghị chưa làm).

