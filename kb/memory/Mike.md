# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn sạch 2026-07-10 22:00 ICT (cron daily_retro.sh) — lịch sử đầy đủ ở kb/INCIDENTS.md
> (RETRO 2026-07-10) + git log. Chỉ giữ trạng thái THẬT cần biết ngay để tiếp mạch việc.

## Đang chờ / treo sang ngày mai — QUAN TRỌNG NHẤT
- **Xác nhận plan thứ Hai 2026-07-13 trước 08:45 ICT**: DollarBill re-dispatch sáng nay
  (job `DollarBill_20260710_150834` SpaceX, `DollarBill_20260710_150924` ZaloPay) để sửa
  lỗi tính sai ngày T+1 (xem dưới) — CHƯA xác nhận hoàn tất lúc viết dòng này (còn running).
  Việc đầu tiên phiên sau: `bin/jobs.sh status <job_id>` cả 2, rồi kiểm tra
  `data/plan_SpaceX_2026-07-13.json` / `plan_ZaloPay_2026-07-13.json` tồn tại + plan_date
  đúng. Nếu thiếu → RED thật trước phiên thứ Hai, xử lý tay ngay.
- 2 file cũ `plan_SpaceX/ZaloPay_2026-07-11.json` (ngày sai — thứ Bảy) vẫn còn nguyên tên
  gốc (rename bị permission classifier chặn — đúng ranh giới "trade plan"). Vô hại, nhưng
  nên hỏi user có muốn dọn tay không.
- Bus question mới `retro-pattern-recurring-dataprovenance-2` (đề xuất tổng quát hoá quy
  tắc freshness-check cho MỌI cặp pipeline producer→consumer nội bộ, không chỉ BQ-vs-DNSE)
  — chờ user/Mike xác nhận hướng.
- V2.5 live-recommend integration: user go-ahead vẫn treo từ 2026-07-07.

## Sự cố hôm nay (2026-07-10) — cả 3 đã fix root cause, xem RETRO trong INCIDENTS.md
1. `ops_health_check.sh` không clear được câu hỏi trả lời chéo-agent — ĐÃ ĐÓNG (commit
   `d1c71fb`, arch-reviewer CONFIRMED).
2. DollarBill đọc DT5G hôm qua (2 cron lệch thứ tự) — ĐÃ ĐÓNG (commit `1a3ea5c`+`5ea7592`,
   cron dời 17:30→19:00, MAX_STATE_LAG 2→1). Đây là 1 dạng MỚI của Pattern B (data
   provenance) — recurring dù chính sách bright-line vừa chốt sáng nay, xem escalation ở
   trên.
3. DollarBill tự tính "ngày mai" = thứ Bảy thay vì thứ Hai (2 lần dispatch cùng ngày đều
   sai) — root cause ĐÃ ĐÓNG (commit `e3001fa`: precompute `next_trading_day()` trong
   bash, không để LLM tự cộng ngày) — nhưng KẾT QUẢ VẬN HÀNH (plan 07-13 đúng) chưa xác
   nhận, xem mục "Đang chờ" trên. Pattern MỚI lần đầu: LLM tự làm phép tính tất định thay
   vì dùng code có sẵn — cần rà thêm các dispatch prompt khác có cùng dạng (chưa làm).

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Same-day data: bắt buộc DNSE API, cấm BigQuery cho tới sau 23:45 ICT sync (bright-line
  rule, coding_guidelines.md §6, chốt 2026-07-10 — nhưng KHÔNG bao phủ hết Pattern B, xem
  escalation-2 ở trên).
- Bất cứ giá trị tính tất định được (ngày, %, số lượng) → tính bằng code, truyền literal
  vào dispatch prompt, KHÔNG giao LLM tự suy luận (bài học sự cố #3 hôm nay).
- Dispatch job dài LUÔN kèm `--bg`. Trước khi nói về trạng thái job nền → `jobs.sh status`
  trong CÙNG turn, không suy đoán.
- Trước khi báo 1 vấn đề là "còn mở/chưa xử lý" → verify ARTIFACT thật (crontab -l, đọc
  file, giá trị API) — đừng chỉ tin bus question chưa có answer (bài học retro 07-09 tự
  mắc lỗi này, Wags phát hiện + sửa).
- Crontab paper-main (TZ + luân phiên T2/4/6 SELL-window / T3/5 BUY-window + early_check)
  — ĐÃ CÀI ĐỦ (xác nhận `crontab -l` 2026-07-10), không còn treo.
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp —
  escalate hoặc dispatch agent đúng vai (dispatch DollarBill để SINH plan mới thì được —
  đó là routine hàng ngày bình thường; RENAME/XOÁ file plan đã tồn tại thì KHÔNG — bị chặn
  đúng theo thiết kế permission classifier).

## Pattern A (job nền chết vì lifecycle) — ĐÃ ĐÓNG từ 07-09, không có tái phát hôm nay
2 lớp fix (systemd-run --scope cgroup + heartbeat-aware deadline), verify e2e. Không có
job nào chết oan hôm nay — 1 tuần quan sát tiếp tục tốt.

