# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-07-22 EOD (sau daily retro finalize)

## RETRO 2026-07-22 — XONG (3-bước: draft→Wags verify→finalize), ghi kb/INCIDENTS.md, commit `696cfa8`
4 sự cố (Wags verify tìm 2 gap trong draft, đã sửa trước khi ghi): (1) near-miss P0
`universe_pit_q` cutover thiếu cron — FIXED trong 8', (2) `sync_bq_cache.py` 3 bug hạ tầng —
2/3 FIXED, **bug#3 (`ticker_financial` delta-only sync không bắt kịp sửa-đổi lịch sử) CÒN HỞ,
chưa ai nhận việc fix**, (3) git commit headless bị permission classifier chặn — **lần 2 liên
tiếp (07-21→07-22), CÒN HỞ HOÀN TOÀN, chưa có prevention** — nếu tái diễn lần 3 (bất kỳ lúc
nào) → escalate ngay, không chờ retro, (4) Discord `DISCORD_THREAD_ID` không export cho tiến
trình con — Wags tự sửa 3 commit, arch-reviewer CONFIRMED. Escalation cross-account-
contamination (từ 07-19/07-21) **ĐÓNG hôm nay** — rule §12 + selfcheck + audit đủ 3 lớp.

## Việc còn treo sang mai
- `sync_bq_cache.py` bug#3 — cần dispatch ai đó fix (chưa gán).
- Pattern git-commit-blocked-by-classifier — theo dõi, escalate nếu tái diễn lần 3.
- `ticker_prune`/`ticker_financial` corruption 07-14/15 — vẫn chờ quyết định khôi phục backup.
- Bus question cũ (`retro-pattern-recurring-headless-wake-assumption-3` 07-20,
  `retro-pattern-recurring-data-registry-accuracy-5days` 07-15,
  `retro-pattern-recurring-joblifecycle-timeout-3` 07-14) — chưa có answer, >6 ngày một số cái.
- Dự án `ticker_prune→universe_pit`: R3 cutover CHÍNH THỨC xong 07-22 (27,16%/1,81/-18,1%/1,50,
  quant-skeptic CONFIRMED). G2b/G3 (quality flag cho tầng chiến lược) đang tiếp tục — kiểm tra
  `bin/jobs.sh status` trước khi báo cáo bất cứ điều gì.
- Phát hiện phụ (chưa fix, không khẩn): tái tính NAV cho ngày QUÁ KHỨ (`--date` cũ) bị cuốn theo
  vị thế HIỆN TẠI thay vì point-in-time đúng ngày — chỉ ảnh hưởng khi CHỦ ĐỘNG tái tính lịch sử,
  không ảnh hưởng vận hành hàng ngày.
- M5 nợ cũ: `executor.py`/paper trials đọc `ticker_prune.parquet` monolith chết từ 06-26 — chưa
  dispatch, không khẩn (chỉ ảnh hưởng paper).

## Trạng thái vận hành
SpaceX/ZaloPay LIVE, V2.4. CAPIT fired 07-20/21 (SAB/SIP/VNM khớp, PVT/NCT còn vướng). Xem
`context_pack.md` "MỚI NHẤT" cho tin mới nhất thay vì tin nguyên văn phần này nếu đã qua nhiều
ngày.

- [2026-07-23T12:26:06Z] SỰ CỐ 07-23: DollarBill mua lại IVS (đã loại 07-21) + đòi rút thêm Trứng vàng (đã cạn) trong plan 07-24 — do context_planning_mini.md không cập nhật từ 07-17. Root cause = Mike không đẩy quyết định sang file role-scoped đúng lúc. Đã fix file + dispatch DollarBill sửa 2 plan (job DollarBill_20260723_122510). CẦN LÀM: audit các file role-scoped khác (execution_mini/dataops_mini) xem có stale tương tự không — đưa vào Friday KB editorial review.
