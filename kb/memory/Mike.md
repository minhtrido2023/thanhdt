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
