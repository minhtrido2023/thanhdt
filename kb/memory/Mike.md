# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-07 21:5x ICT (2 fix funding gate xong + verify)

## Tối 08-07 — 2 sự cố funding gate ĐÃ VÁ + quant-skeptic CONFIRMED, đóng hẳn
User duyệt đề xuất Winston (Winston_20260807_065124) tối nay, dispatch song song Mafee+Taylor:
- **fix_1+2 (UPCOM routing)**: Mafee, commit `c22bd1c` — luôn giải gói vay theo MÃ (tái dùng
  `_resolve_loan_package_id`) thay vì rơi về gói mainboard default khi lệnh không cash_only/không
  đòn bẩy. Vá WAIT_CASH vô hạn ca DRI. 18/18+51/51 selfcheck, Mike tự verify diff khớp yêu cầu.
- **fix_3 (funding cash-flow / JIT-unpark credit)**: Taylor, commit `087a3d0` + doc fix Mike
  `00ffd2e` — nhánh (1) của `check_plan_funding` nay cộng tín dụng lệnh BÁN cùng plan chạy trước
  (priority thấp hơn) theo TỈ LỆ NHU CẦU từng nhóm gói vay (Taylor tự bác đề xuất plan-wide của
  Mike bằng phản ví dụ P6 — đúng). Vá ca ZaloPay 08-07 bị chặn sạch 0/9 lệnh dù plan tự cấp vốn đủ.
  73/73 selfcheck + 81-plan replay, **quant-skeptic CONFIRMED cao** (independent recompute khớp
  hệt, kể cả số "21/50 plan tự cấp vốn hoàn toàn"). Rủi ro tồn dư đã disclose (sell chỉ đảm bảo
  ĐƯỢC THỬ trước, không đảm bảo KHỚP trước) — có backstop layer-3 WAIT_CASH không đổi, theo dõi
  bằng fill data thật (chưa có ledger riêng, cân nhắc thêm nếu tái diễn).
- **Bài học quy trình**: dispatch 2 agent sửa CÙNG file không cách ly (không worktree) trong 1
  phút → commit của agent A cuốn theo staged-work-chưa-commit của agent B (may mắn không đụng độ
  hàm, cả 2 tự công bố minh bạch). Lần sau: tách file theo agent, hoặc chạy tuần tự khi biết trước
  sẽ chạm cùng file. Đã ghi vào `kb/current_ops.md` §Domain-constraint layer P0.
- Domain-constraint P0 (`plan_funding_gate.py`) đã ACTIVE (hard block) từ 08-04 (`bb8583c`) —
  KHÔNG còn WARN_ONLY như tài liệu thiết kế gốc mô tả; cập nhật `kb/current_ops.md`. Xác nhận
  live thật còn treo tới phiên 08-10 (SpaceX pp0Buy margin case chưa từng có bản ghi thật).

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

