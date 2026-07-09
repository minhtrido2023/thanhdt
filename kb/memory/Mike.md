# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn sạch 2026-07-09 22:00 ICT (cron daily_retro.sh, lần chạy đầu tiên) — lịch sử đầy
> đủ nằm ở kb/INCIDENTS.md (2 entry RETRO cùng ngày: bản thủ công ~20:46 + bản cron
> 22:00) + git log. Chỉ giữ trạng thái THẬT cần biết ngay để tiếp mạch việc ngày mai.

## Đang chờ / treo sang ngày mai
- Escalation MỚI tối nay: bus question `retro-pattern-recurring-dataprovenance` —
  Pattern B (đọc nhầm nguồn dữ liệu trễ/sai, ≥5 lần từ 07-03) đã bị flag ở 2 RETRO liên
  tiếp mà chưa có cơ chế chặn (chỉ có nguyên tắc viết trong coding_guidelines.md §6).
  Cần user chọn hướng: (a) checklist bắt buộc trong dispatch prompt report/plan-gen,
  (b) static lint script, hoặc (c) khác. CHƯA tự triển khai — chờ quyết định.
- Crontab `paper-main` (TZ fix Asia/Ho_Chi_Minh + tách phiên sáng SELL/BUY-window) đã
  soạn xong, chờ user cài tay (`Taylor` question `cron-paper-main-can-cai`, file diff ở
  `agents/Taylor/cron_paper_main_proposed_20260709.txt`).
- V2.5 live-recommend integration: user go-ahead vẫn treo từ 2026-07-07.

## Pattern A (job nền chết vì lifecycle) — coi như ĐÃ ĐÓNG tối nay, cần quan sát ~1 tuần
Đã nhận 2 lớp fix riêng biệt trong 1 buổi tối (2026-07-09): (1) `systemd-run --scope`
tách cgroup khỏi caller (Wags, arch-reviewer CONFIRMED high) — job --bg không còn chết
theo khi bridge/cron cha bị restart/kill; (2) heartbeat-aware deadline (`d3a7282` +
`b8f78bd`/`5446bf2`) — timeout không còn giết nhầm agent còn sống (HB_AGE lọc bỏ watcher
ping, chỉ tin heartbeat do agent tự ghi). Cả 2 verify bằng e2e test thật, không chỉ đọc
code. KHÔNG tuyên bố đóng hẳn — theo dõi ~1 tuần không có job nào chết oan nữa mới chốt.

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Dispatch job dài LUÔN kèm `--bg` — kể cả khi Mike tự chạy trong Bash tool của chính
  mình (bài học đau 07-09: quên `--bg` → Bash-tool timeout 2' giết job).
- Mọi report/plan-generation KHÔNG lấy giá từ BQ trong khung giờ biết chắc chưa sync
  (BQ sync 23:45 ICT) — bắt buộc DNSE live quote (đã vá bq_freshness_check.sh, nhưng
  xem escalation Pattern B ở trên — đây vẫn là nguyên tắc VIẾT RA, chưa phải cơ chế ép).
- Odd-lot (<100cp): DNSE nhận bình thường qua `orderCategory=NORMAL` — bug từng nằm ở
  `round_lot()` tự làm tròn 0 (đã vá, commit `f7f9f52`).
- Trước khi nói bất kỳ điều gì về trạng thái job nền → `jobs.sh status` trong CÙNG turn,
  không suy đoán/nói từ trí nhớ.
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp
  — escalate hoặc dispatch agent đúng vai, luôn hỏi trước khi cài crontab.

## Cơ chế `bin/daily_retro.sh` (cron 22:00 ICT) — đã chạy lần đầu tối nay
Tự đọc INCIDENTS.md + bus event trong ngày, phân loại mới/tái diễn, viết entry RETRO,
dọn working memory, consolidate, báo Trading Daily. Tự escalate bus question khi 1
pattern tái diễn ở 2 RETRO liên tiếp mà prevention không đổi (đã kích hoạt lần đầu tối
nay cho Pattern B — xem mục "Đang chờ" trên).

