# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn sạch 2026-07-09 tối (daily retro đầu tiên) — lịch sử đầy đủ đã nằm ở kb/INCIDENTS.md
> (blameless postmortem) + git log, không cần chép lại ở đây. Chỉ giữ trạng thái THẬT
> cần biết ngay để tiếp mạch việc.

## Đang chờ (chưa xong lúc cuối ngày 2026-07-09)
- Job `Wags_20260709_134401`: tách dispatch.sh khỏi cgroup bridge (root-cause fix cho
  Pattern A — job nền chết khi process cha không liên quan restart/timeout, tái diễn
  3 lần trong 3 ngày). Kiểm `bin/jobs.sh status` khi resume, chưa biết kết quả.
- Crontab: đã chuẩn bị thêm dòng `bin/daily_retro.sh` (22:00 ICT) — CHƯA CÀI (cần user
  xác nhận rõ ràng, đúng quy tắc "chạm crontab luôn phải hỏi trước"). File đề xuất:
  `/tmp/crontab_proposed_with_retro.txt`.
- Pattern B (đọc nhầm nguồn dữ liệu trễ/sai — tái diễn ≥4 lần kể từ 07-03) — đã ghi
  nhận prevention hiện tại (coding_guidelines.md §6) chưa đủ mạnh, đề xuất checklist/
  static-check nhưng CHƯA triển khai, cần bàn phạm vi với user trước khi làm.
- V2.5 live-recommend integration: user quyết định go-ahead vẫn treo từ 2026-07-07.

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Dispatch job dài LUÔN kèm `--bg` — kể cả khi Mike tự chạy trong Bash tool của chính
  mình (bài học đau: quên --bg → Bash-tool timeout 2' giết job, job record kẹt "running"
  vĩnh viễn, xem INCIDENTS.md 2026-07-09 mục 7).
- Mọi report/plan-generation KHÔNG được lấy giá từ BQ trong khung giờ BQ biết chắc chưa
  sync (BQ sync 23:45 ICT; dispatch DollarBill chạy ~17:30 nên BQ LUÔN trễ 1 phiên tại
  thời điểm đó) — bắt buộc DNSE live quote, đã vá bq_freshness_check.sh.
- Odd-lot (<100cp): DNSE nhận lệnh bình thường qua orderCategory=NORMAL, không cần API
  riêng — bug là ở `round_lot()` tự làm tròn 0, đã vá executor.py (commit f7f9f52).
- Trước khi nói bất kỳ điều gì về trạng thái job nền → `jobs.sh status` trong CÙNG turn,
  không suy đoán/nói từ trí nhớ (đã sai 1 lần 2026-07-07, không lặp lại).
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp
  — escalate hoặc dispatch agent đúng vai (DollarBill cho plan), luôn hỏi trước khi cài
  crontab dù chỉ paper/non-trading.

## Cơ chế mới hôm nay (2026-07-09)
- `bin/daily_retro.sh` — retro cuối ngày tự động (22:00 ICT dự kiến): phân loại lỗi
  mới/tái diễn, đánh giá fix hoàn chỉnh chưa, viết entry RETRO vào INCIDENTS.md, dọn
  working memory, consolidate, báo Trading Daily. Tự escalate nếu 1 pattern tái diễn
  2 lần RETRO liên tiếp.

