# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Chuỗi audit lớp lỗi corp-action (exdate price-frame + 3 call-site + vendor-mismatch chain)
  ĐÃ ĐÓNG HOÀN TOÀN 2026-09-24 — tất cả LIVE trên master, xác nhận qua bus finding
  corp-action-4sites-audit-COMPLETE-all-4-LIVE + memory entries chi tiết bên dưới nếu cần tra lại.
- 0 bus question pending (đã đóng 2 câu cuối 2026-09-24 20:2x: wags-fix-not-confirmed coord-09-23
  [chỉ lỗi độ-chính-xác log, việc thật đã xong từ trước] + selfcheck-red production_manifest
  [đã fix: phân loại 2 cron mới paper_corp_action.py=T1, plan_approval_reminder.sh=T0, commit 4e89ca46]).

## Việc đang mở / cần theo dõi (xác nhận lại 2026-09-24 20:3x — nhiều mục cũ trong memory là STALE)
1. **FiinPro harvest**: 25/74 lô, kẹt vì rate-limit DAILY của connector (không phải lỗi) — tự
   resume 00:20 ICT mỗi ngày, tối nay (09-25 00:20) sẽ chạy tiếp vài lô nữa. Theo dõi thụ động.
2. **excluded_dividend_receivable[DGC]** (ZaloPay) — dọn config sau khi tiền DGC về thật, dự kiến
   ~2026-09-25 (MAI). Chưa tới hạn, chưa hành động.
3. Pattern 2 (daily_retro.sh:195 topic escalate nhúng bộ đếm ngày, ack không phủ khi topic đổi số)
   — CHƯA sửa gốc, không urgent. CHỈ escalate nếu lặp lại ở retro 09-24 (tối nay/mai).

## ĐÃ XÁC NHẬN KHÔNG CÒN TREO (đừng báo lại nhầm — nhiều mục memory cũ đã lỗi thời)
- test_trading_bot.py:353 — ĐÃ SỬA từ 09-23 (commit 9fefd245 + 91564b1b + aa7a36ee), verify lại
  bằng grep 09-24: dùng đúng p["cfg"]["mode"].
- universe-pit-migration G7/G8/G9 — ĐÃ ĐÓNG 2026-09-19 (job Taylor_20260919_033750).
- NAV corp-action gate v2 rc=5 runbook — ĐÃ DUYỆT + promote 09-22 (commit c581c74e).
- data/discretionary_margin_arms.json (WorkingClaude root) — arm giả đã dọn sạch, hiện = [].
- dnse-balances-stock-block-zero 09-24 — tự hồi phục, fail-closed guard hoạt động đúng, không
  cần can thiệp.
- Treasury buyback branch — user duyệt "theo ý bạn", rút 31 file lên master 09-24 (commit 83f6a3ef),
  nhánh cũ đã xoá. Điều kiện wire chính thức giữ nguyên từ 08-09 (cần case đổi quyết định thật).

## Bài học tích luỹ quan trọng (đừng lặp lại)
- TRƯỚC KHI dispatch dựa trên tracker/memory: verify bằng git log + bus TRƯỚC (2 phút, rẻ hơn
  job sai hướng) — Mike đã viết spec sai dựa trên memory lỗi thời ít nhất 7 LẦN trong chuỗi audit
  09-24. Tracker `kb/projects/*.md` có thể STALE dù mới đọc gần đây.
- acceptance/verify tự chạy: phải xem output có NỘI DUNG THẬT không, đừng chỉ so 2 chuỗi bằng nhau
  (ca report_return_gate.py --report vs positional arg — 2 lỗi argparse giống nhau cũng "identical").
- Lớp lỗi §29 (chẩn đoán không dựa bằng chứng) có thể có NHIỀU CỬA trong CÙNG 1 file — 1 vòng
  review chỉ đóng đúng cửa nó thấy, không đảm bảo hết (case discretionary_margin_gate.py: 12 vòng).

