# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-14T02:30Z

## Daily retro 08-13 — ĐÃ ĐÓNG HẾT (không còn mục treo)
- Pattern-B prevention (§28 coding_guidelines.md, chuẩn hoá giá trị trước khi so 2 nguồn) —
  user duyệt ("Việc 1. Đồng ý"), đã commit `583d0335`.
- `retro-pattern-recurring-2-days` — user chọn "gộp vào báo cáo tổng" ("Việc 2").
- Ceiling TV1 (`zalopay-tv1-ceiling-vs-t1-band`) — user xác nhận "Việc 3. Đã quyết trong plan";
  bus `answer` đóng bằng artifact (`hard_no_chase_ceiling_vnd`=20.661 + fill thật 08-13).
- 3 file incident đã ghi đủ: `2026-08-13-tv1-ceiling-decision-via-action-not-bus.md`,
  `2026-08-13-append-event-word-split-silent-truncation.md` (Wags, commit `94b01dbb`),
  `2026-08-13-codex-headless-dns-block-tv1-and-smtp.md`.
- Nghi vấn codex `allow_agents` bypass (Mafee_codex_*/DollarBill_codex_* 08-13) — ĐÃ ĐÓNG
  2026-08-14: user xác nhận tự tay dùng codex khi claude chết đầu phiên 08-13, không qua
  `dispatch.sh`, KHÔNG phải lỗ hổng validate. Bus answer + incident file cập nhật, commit
  `9dc91370`.

## Còn mở — chưa xác nhận resolved
- TV1 mới đạt 61%(SpaceX)/50%(ZaloPay) kế hoạch 08-13 (ADV mỏng, §27 fill-reconciliation) —
  chưa quyết mua nốt 08-14 hay coi phiên đã đóng. Kiểm khi vào phiên sáng 08-14.
- `merge_park_orders.py` — Taylor khuyến nghị sequence C-rồi-A (shadow trước, cron sau); chưa
  có quyết định lịch cài cron chính thức.

## Bối cảnh còn hiệu lực (không đổi từ trước)
- Cron `compute_active_nav_all.sh` (20:15 ICT T2-T6) + permission Edit/Write `data/trade_plans/**`
  đã XONG (08-13 sáng).
- `tav2_bq.corporate_action` (DIV/ISS/AIS event-level) research xong, ghi
  `kb/data_registry/price-volume/corporate_action_bq.md` (status TRAP, chưa có writer/cron) —
  CHƯA wire vào pipeline nào khác ngoài `corp_action_daily.py`.
- Chuỗi corporate_action/paper-report (Việc A-E) khép lại 08-13; SANITY_FACTOR đóng 08-14 (user
  chọn phương án C — WARN, không ẩn số), Taylor wire (mike@1ea8c4ee), quant-skeptic CONFIRMED
  cao. 1 gap coverage kỹ thuật nhẹ còn mở (0 test run()-level) — không khẩn, không phải policy.
  `kb/projects/corporate-action-bq-integration-0813.md` đã đóng.

