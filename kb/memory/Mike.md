# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T03:47Z (bug UPCOM ref-price phát hiện + đang fix)

## ⚠️ BUG THẬT — Rule A anchor sai cơ sở cho UPCOM (2026-08-15, user phát hiện)
- HOSE/HNX: giá tham chiếu = giá đóng cửa phiên trước (Rule A đang ĐÚNG cho nhóm này).
- **UPCOM: giá tham chiếu = BÌNH QUÂN GIA QUYỀN phiên trước, KHÁC giá đóng cửa** — lệch vài %
  ngay ngày bình thường. Xác nhận qua WebSearch (≥3 nguồn) + khớp đúng data N=66 mã của chính
  commit 59f9569 (SCL −3,376%/TMG +0,949%/TV1 −0,497% = 3 ca UPCOM trong 7 ca lệch).
- Phạm vi: DRI=UPCOM, SCL=UPCOM, TV1=UPCOM (3/5 mã Rule A). POW=HOSE, SSI=HOSE không ảnh hưởng.
- **ĐÃ TỰ LÙI**: TV1 state file (SpaceX+ZaloPay) — field `ceiling_rule`→`ceiling_rule_REVERTED_
  20260815`, verify sống mode=dynamic (mean-5) trở lại, ceiling=20.497đ đúng số cũ.
- **Đang chờ**: job Taylor_20260815_034407 (opus/high, timeout 3600s) — điều tra độc lập + fix
  anchor basis theo sàn (UPCOM dùng q.ref DNSE thay vì tự tính close) + sửa fail-safe guard
  (C1/C2) cho nhất quán + hồi quy đo chênh lệch thực tế.
- **QUY TẮC**: TV1 KHÔNG được tự lật lại Rule A cho tới khi Mike thấy quant-skeptic CONFIRMED
  bản fix mới + tự quyết/hỏi lại user. LAG book (DRI/SCL) chưa áp plan thật nên không cần revert
  gì, nhưng PHẢI fix trước khi dùng cho 2 mã này.
- Bus: event `tv1-rule-a-UPCOM-anchor-bug-revert` (Taylor_20260814_170351 trace).

## Mạch Rule A ceiling trước đó — bối cảnh (đã supersede một phần bởi bug trên)
- Nghiên cứu → user chọn Rule A → wire plan generator (2db6d37) → gap ref_price → fail-safe
  (59f9569) + TV1 adaptive (a106e97) → cả 2 CONFIRMED (high) → Mike lật TV1 live → **user phát
  hiện bug UPCOM ngay sau đó → lùi lại**. File state KHÔNG git-tracked (.gitignore *.json).

## Việc còn hở từ trước (chưa xử lý)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.
6. Citation N=29 BQ-vs-DNSE cho ngưỡng 1% (no_chase_ceiling.py) — gap auditability nhẹ, không
   khẩn, có thể gộp vào lần fix UPCOM này vì cùng file/chủ đề.

## Bối cảnh còn hiệu lực
- TV1: đừng tự nhắc lại status tĩnh cũ — chỉ nêu khi có thay đổi thật.
- dispatch-prompt-heredoc skill (~/.claude/skills/dispatch-prompt-heredoc/) — dùng heredoc-vào-
  biến cho MỌI prompt dispatch có backtick/code snippet.

