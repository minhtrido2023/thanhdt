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
- [2026-07-23T12:54:53Z] Đang chờ 3 job song song: (1) DollarBill_20260723_125357 - sửa plan SpaceX 07-24 (bỏ TRC RATING_FAIL, trừ cash TV1 3.98M trước khi size PVT); (2) Taylor_20260723_125437 - audit toàn bộ ứng viên LAG hiện tại (rating/thanh khoản/DCF từng mã), đề xuất chính sách rating-gate cho LAG book; (3) Taylor_20260723_123927 - historical deep-value-crisis screen 2007-2026 (task lớn, có thể còn chạy lâu, không liên quan 2 job trên). Context_planning_mini.md đã thêm 2 rule mới (TV1 cash-reservation + LAG rating-fail escalation), đã commit.
- [2026-07-23T13:20:26Z] User chốt hướng B (gate chất lượng cho LAG) nhưng với lý do cụ thể: nghi ngờ suy giảm LAG gần đây chủ yếu do REGIME thị trường xấu (surprise mất ý nghĩa khi nhà đầu tư sợ giảm hơn sợ tăng), không chỉ do chọn sai tên. Đã dispatch Taylor_20260723_131958 (timeout 30') nghiên cứu sâu: phân rã hiệu suất LAG theo thời gian tìm đúng giai đoạn suy giảm, test IC(surprise, forward_return) theo regime/breadth bucket, so sánh 4 phương án (baseline/name-gate/regime-gate/kết hợp), chẩn đoán riêng giai đoạn gần đây quality-driven hay regime-driven. TRC vẫn HOLD chờ kết quả này. Job PVX (Taylor_20260723_130951, fear-buy case) chạy song song ở thread Discord khác (1521735922066919515), không cần poll ở đây.
- [2026-07-23T13:56:48Z] User đào sâu thêm 2 câu hỏi tinh tế cho LAG regime research (sau job 131958): (1) khả năng phân biệt RATING tốt/xấu có phụ thuộc regime không (giả thuyết: chỉ phân biệt được ở NEUTRAL, mất ý nghĩa ở BULL+) — khác trục với IC(surprise) đã đo; (2) DT5G 5-state quá thô, cần đặc trưng liên tục (drawdown/thanh khoản/tốc độ giảm/độ rộng) để đo edge LAG chính xác hơn, đặc biệt phân biệt 'neutral nghiêng bear' hiện tại với neutral thường. Đã dispatch Taylor_20260723_135623 (timeout 30'). TRC vẫn HOLD chờ kết quả. Job Taylor_20260723_134350 (fear-buy sleeve, thread Discord khác 1521735922066919515) vẫn chạy song song, không liên quan, tự báo cáo bên đó.
- [2026-07-23T14:21:02Z] Đã dispatch quant-skeptic verify cơ chế disc_c4/c5 (DT5G half-size LAG BEAR/low-neutral) + overlay roc20<-8 — script bin/verify_finding.sh --topic 'LAG deep-dive #2' --bg (pid 4084028, log verify_20260723_142043.log). Verdict sẽ ghi lên bus event quant-skeptic/verification. Nếu CONFIRMED, đây là bước cuối trước khi đề xuất wire (vẫn cần user sign-off cuối theo quy trình chuẩn). TRC vẫn HOLD chờ kết quả.
- [2026-07-23T16:28:29Z] User đồng ý HOLD TRC (không đưa vào plan) - chốt xong. Đã dispatch Taylor_20260723_162813 (timeout 30') chạy disc_c4/c5 trong bối cảnh BLENDED V2.4 đầy đủ (không chỉ LAG-only) theo đề xuất quant-skeptic sau CONFIRMED verdict. So sánh baseline R3 pin (27,16%) vs R3+disc_c4. Nếu kết quả tốt cần verify LẦN 2 (khác kết quả LAG-only đã verify) trước khi đề xuất wire chính thức.
