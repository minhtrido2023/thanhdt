# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-14T17:45Z (dọn cuối ngày sau daily retro finalize)

## Retro 2026-08-14 — ĐÃ CHỐT
File: kb/incidents/retro/retro-2026-08-14.md. 6 sự cố (1 major đã đóng — git-stash-conflict
2 bot chết 09:05, tự phục hồi; 1 recurrence 3 ngày vừa vá — plan-dd-check-string; 1 chuỗi
dang dở — selfcheck-masking E5/F1/G1). Pattern-B (4 ngày) + backlog quyết định treo (5 ngày)
từ retro-08-13 ĐÃ ĐÓNG bằng quyết định user thật (coding_guidelines §28 + bỏ yêu cầu
1-sự-cố-1-file cứng).

## Việc còn hở — mai cần theo dõi/redispatch
1. **ops_health_check.sh::_rollup_resolved() substring-match** — arch-reviewer NEEDS_CHANGES
   05:26:23Z trên fix Wags (coord-2026-08-14 rollup_of), CHƯA vá (xác nhận còn nguyên sau 2
   commit tiếp theo). Cần redispatch Wags vá đúng required_changes rồi arch-reviewer verify lại.
2. Selfcheck-masking (E5 capit_lever/F1 ghost_order/G1 atc_sweep) — Taylor mới vá xong G1,
   chưa xác nhận E5 đã vá hay chỉ mới ĐO, chưa có event tổng kết đóng cả 3.
3. plan-dd-check-string fix (Taylor, commit 9a9dbb1) — chờ quant-skeptic verify + xác nhận
   trên phiên LIVE có FILL thật (kỳ vọng TV1 có dcf_check) không còn POLL_FAIL.
4. Dispatch collision cùng file lần 2 (08-07, 08-14, corp_action_daily.py) — watch-list, chưa
   escalate (chưa đạt ngưỡng rule 6); tái diễn lần 3 → ghi file kb/incidents/ + cân nhắc lại
   worktree isolation.

## Đang chờ (job nền, từ trước — chưa xác nhận trạng thái cuối)
- Wags_20260814_050658 (--bg, opus/high): 3 việc rẻ arch-reviewer đề xuất — kiểm lại đã xong
  chưa đầu phiên mai. problem_key/supersession redesign: DEFERRED theo quyết định user
  06:09:42Z (mở lại nếu có ca thật root-cause-D trong 3-4 tuần/15-20 vòng coord tới).
- merge_park_orders.py cron chain — user đồng ý cài (3 dòng), kiểm đã cài xong + cron_registry
  cập nhật chưa.

## Bối cảnh còn hiệu lực
- TV1: đừng tự nhắc lại status tĩnh (planning bên DollarBill đã báo) — chỉ nêu khi có thay đổi.
- corp_action_daily.py SANITY_FACTOR WARN: đã đóng 08-14, quant-skeptic CONFIRMED.
- stash@{0}: đã resolve xong (DROP đúng, duplicate landed), không còn việc mở.

- [2026-08-14T17:51:05Z] [2026-08-14T17:51:05Z] Nghiên cứu ceiling A/B (tham chiếu ×1,03 vs mean-5) + participation TV1-class: job Taylor_20260814_170351 XONG, cả 2 finding quant-skeptic CONFIRMED (1 high, 1 medium — gap auditability nhẹ: script IS day-clustered chưa commit, không đổi khuyến nghị). Đã báo đầy đủ vào thread 1521183164364754974. ĐANG CHỜ user chốt (a) đổi rule giá A hay giữ B (chính sách, không phải tối ưu miễn phí); (b) đề xuất Taylor ghi 'số phiên gom kỳ vọng' vào plan note cho lệnh >10% ADV20 — sẽ làm luôn trừ khi user phản đối. Chi tiết: agents/Taylor/research/ceiling_ab_pacing_20260814/README.md.
- [2026-08-14T21:40:22Z] [weekly-ops-audit 2026-08-15] Va 2 bug im lang (03419973: for_each_live_account fail-OPEN lam 6 cron giam sat bi bo qua khi config loi; discover_sessions ten file >255B giet ca luot) + dong bo pham vi selfcheck sweep (445f46e9, 647→120 file). CHO USER: (a) EOD daily report chua bao gio gui email — wire hay sua §6.5? (b) 2 dong cron chay tu worktree wt-1522576692638388364. CHO THU 2 08-17: grep POLL_FAIL exec_*_2026-08-17_journal.csv phai RONG (xac nhan fix 9a9dbb1 tren phien LIVE). CON HO: MIKE.md 44,2KB da VUOT 40KB (+800B/ngay, trim tay khong giu duoc — can tach OKF); job_cancel_guard_selfcheck do that thuoc Wags; coord-2026-08-14 _rollup_resolved() van chua va.
- [2026-08-15T00:28:57Z] [2026-08-15T00:28:57Z] Ceiling A/B: user CHỐT giữ B (không wire luật trần giá mới, decided_by=user đã ghi bus). Dispatch Taylor (job Taylor_20260815_002825, opus/medium) làm việc (b) đã đồng ý: ghi 'số phiên gom kỳ vọng' vào plan note cho lệnh >10% ADV20 (info-only) + đóng gap auditability (script IS day-clustered). Đang chờ job.
- [2026-08-15T00:34:19Z] [2026-08-15T00:34:19Z] ĐÍNH CHÍNH: user chọn Rule A (không phải B) — tôi hiểu nhầm '(B) Đồng ý' trước đó là chọn giá B, thực ra là đồng ý việc (b). Đã sửa bus (event ceiling-rule-AB-user-decision-CORRECTED, decided_by=user, supersedes event sai). NEXT: sau khi job Taylor_20260815_002825 (việc b, đụng plan.py) xong → dispatch Taylor wire Rule A vào plan generator (hard_no_chase_ceiling_vnd = close phiên trước × 1,03, tái lập mỗi lần lập plan, KHÔNG trượt trong phiên) theo đúng cách wire ghi trong README §4a — chạy TUẦN TỰ (không song song) để tránh đụng file plan.py với job (b). plan.py là module lõi 21 selfcheck, quét rộng bắt buộc + quant-skeptic CONFIRMED trước khi coi là sẵn sàng deploy.
- [2026-08-15T00:41:43Z] [2026-08-15T00:41:43Z] LƯU Ý: dispatch job Taylor_20260815_004105 (wire Rule A) bị lỗi shell — backtick trong prompt (`_limit_price`, `ref_price = anchor/1.04`) bị bash hiểu thành command substitution trước khi tới dispatch.sh (lỗi 'command not found' hiện ra ngay sau khi gọi), khiến 2 đoạn đó rơi mất khỏi prompt thật gửi Taylor. Điểm 3 (KHÔNG đụng guard cuối executor.py) có thể bị suy yếu. KHI JOB XONG: bắt buộc tự đọc diff/commit, xác nhận thật sự KHÔNG đụng executor.py's _limit_price/guard cuối trước khi coi an toàn — đừng chỉ tin báo cáo của Taylor. Bài học: heredoc thay vì double-quote string khi prompt có backtick.
- [2026-08-15T00:53:16Z] 2026-08-15: user yêu cầu ngăn lỗi backtick-trong-prompt-dispatch lặp lại — đã tạo skill ~/.claude/skills/dispatch-prompt-heredoc/ (heredoc-vào-biến thay double-quote inline) + trỏ từ kb/coding_guidelines.md + _ext.md §15 (gap: shellcheck_gate.sh chỉ bắt .sh đã commit, không bắt Bash tool call tương tác). Commit 1f0965ba. Việc cũ (Taylor_20260815_004105 xác nhận diff không đụng executor.py) vẫn còn hở, chưa làm trong lượt này.
- [2026-08-15T01:14:58Z] [2026-08-15T01:14:58Z] Rule A wiring (job Taylor_20260815_004105) XONG + tự verify diff: executor.py KHÔNG bị đụng (confirmed). Phạm vi: chỉ LAG (DRI/POW/SCL/SSI), loại tường minh DISCRETIONARY_SPECIAL/TV1 (đã có sessions=5 riêng = Rule B, đổi sang Rule A là quyết định RIÊNG cần user duyệt). CODE+SELFCHECK xong, CHƯA áp plan thật. Đang chạy verify_finding.sh (bg). NEXT: (1) chờ verdict quant-skeptic, (2) hỏi user duyệt lần cuối trước khi DollarBill dùng cho plan thật, (3) hỏi user riêng có đổi TV1 sang Rule A không, (4) nhắc DollarBill: ref_price PHẢI cập nhật theo trần mới khi áp dụng, không thì tác dụng bốc hơi.
