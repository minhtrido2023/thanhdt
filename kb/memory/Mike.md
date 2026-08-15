# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T04:41Z (bug UPCOM ref-price — fix xong, chờ verify)

## Bug UPCOM ref-price — FIX XONG, chờ quant-skeptic (2026-08-15)
- Job Taylor_20260815_034407 XONG: commit `38b6c04` (WorkingClaude, PHẦN 2 fix) +
  `1533b596`/`e524d326` (mike repo, injector fix + research doc/regression).
- Tự đọc diff xác nhận: TV1 VẪN reverted (Taylor tự tôn trọng ranh giới, không lật lại).
- 2 bug THÊM tự phát hiện: (1) `Quote.exchange` fail-OPEN — DNSE trả `marketId` không phải
  `exchange`/`market`/`floorcode`, nên 43/43 mã test mặc định "HOSE" (root cause sự cố SHS/MBS
  07-01, trước chỉ vá ngọn). (2) Ngày GDKHQ: tham chiếu đã điều chỉnh quyền, giá đóng thì
  không — ca SSI 08-17 trần cũ sẽ CAO HƠN CẢ trần hợp lệ phiên → luật A vô hiệu im lặng.
- Hồi quy N=777 phiên-mã (DRI+SCL+TV1): median lệch 0,553% (18% ngân sách τ=3%), p90 1,527%,
  max 9,868%, 1,8% phiên vượt cả τ. Lệch 2 CHIỀU (37,6% mất tiền thật, 32,6% mất cơ hội) —
  KHÔNG phải bias 1 chiều sửa được bằng hằng số. **0 thiệt hại tiền thật** (chưa từng áp live).
- Cơ chế mới: anchor = `q.ref` (giá tham chiếu chính thức DNSE) thay vì tự tính close; 3 cổng
  G1/G2/G3 (sàn xác định được / biên độ khớp sàn / tham chiếu ∈ [Low,High] phiên trước);
  fail-safe guard đổi mốc sống close→q.ref (chặt hơn, không lỏng hơn); BQ hạ vai trò kiểm chéo.
- Selfcheck 25/25 PASS (TZ-robust), hồi quy 96 plan LIVE: 0/23 lệnh đổi giá trị.
- **ĐANG CHỜ**: 2 verify_finding.sh chạy nền (topic "XAC MINH DOC LAP" + "BAN VA"). Khi CONFIRMED
  cả 2 → hỏi lại user có muốn lật TV1 sang Rule A (bản fix) lần nữa không.
- TV1 VẪN ở mean-5 (Rule B) — KHÔNG tự lật cho tới khi user quyết lại.

## Việc còn hở từ trước (chưa xử lý)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.

## Bối cảnh còn hiệu lực
- TV1: đừng tự nhắc lại status tĩnh cũ — chỉ nêu khi có thay đổi thật.
- dispatch-prompt-heredoc skill (~/.claude/skills/dispatch-prompt-heredoc/) — dùng heredoc-vào-
  biến cho MỌI prompt dispatch có backtick/code snippet.

