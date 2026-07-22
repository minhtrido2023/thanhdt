# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-07-22 (làm 3 việc user giao — xem chi tiết dưới)

## Vừa xử lý xong (3 việc user giao "làm luôn 3 việc đi")
1. **ops_health_check.sh:188** — thực ra ĐÃ XONG từ 07-21 (commit a268476/a59cd85, arch-reviewer
   CONFIRMED). Working memory trước đó carry-forward claim SAI ("chưa ai áp dụng") — đã sửa.
2. **Selfcheck 2-account-interleaved** — MỚI, `bin/nav_scripts_2account_selfcheck.py` (commit
   `8d07529`). Test cho daily_nav_snapshot.py/verify_account_snapshot.py/reconcile_equity.py,
   backup+restore an toàn (verified md5sum 4 lần chạy thật). PASS trên dữ liệu thật 07-20/07-21/07-22
   — không có dấu hiệu lẫn account.
3. **Dọn crontab paper-trading lạc hậu** — dòng comment lỗi thời (Winston_20260712_151206 đề xuất
   xóa) ĐÃ KHÔNG CÒN trong crontab thật — đã xong từ trước, không rõ ai/khi nào, không cần làm gì.

**Bài học tự nhận ra**: 2/3 việc trong danh sách "còn treo" của working memory hoá ra ĐÃ XONG —
carry-forward claim cũ mà không re-verify là đúng pattern lỗi đã biết (xem mục dưới). Từ giờ,
trước khi báo "còn treo/chưa làm", LUÔN grep/kiểm tra artifact thật trước khi tin văn bản cũ.

## Phát hiện phụ MỚI (chưa fix, cần biết): tái tính NAV cho ngày quá khứ SAI sau khi có giao dịch mới
`daily_nav_snapshot.py`/`verify_account_snapshot.py` tái tính cho 1 ngày QUÁ KHỨ (vd `--date
2026-07-20` chạy vào 07-22) dường như cuốn theo VỊ THẾ HIỆN TẠI thay vì đúng point-in-time của
ngày yêu cầu — SpaceX bị tự chặn bởi NAV_SANITY_MAX_PCT khi tái tính 07-20/07-21 (lệch +24-32%
so với lịch sử đã lưu, sau khi CAPIT mua thêm ~236M ngày 07-21). KHÔNG phải bug lẫn account (2
account vẫn luôn ra số khác nhau rõ ràng) — là giới hạn riêng của cơ chế tái-tính-ngày-cũ. Chưa
điều tra sâu/fix — nếu cần tái tính lịch sử chính xác cho báo cáo, ĐỪNG tin kết quả tái tính ngày
cũ mà không đối chiếu lại, và cân nhắc dispatch Taylor/Winston điều tra root cause nếu việc này
trở nên quan trọng (hiện tại chỉ ảnh hưởng khi CHỦ ĐỘNG tái tính ngày cũ, không ảnh hưởng vận
hành hàng ngày bình thường vì đó luôn chạy cho ngày HIỆN TẠI).

## Đang chờ / treo — còn lại sau khi xử lý 3 việc trên
- M5 nợ cũ: `executor.py`/paper trials đọc `ticker_prune.parquet` monolith chết từ 06-26 — chưa
  dispatch Taylor, không khẩn (chỉ ảnh hưởng paper).
- Job Taylor đang theo dõi (universe_pit G2b/G3, thread riêng) — xem lịch sử hội thoại gần nhất,
  kiểm tra `bin/jobs.sh status` trước khi báo cáo bất cứ điều gì về nó.
- 2 câu hỏi "wags-fix-not-confirmed: coord-2026-07-22" (round1+round2) trên bus — round2 đóng
  5/7 required_changes theo commit `678e81d`, còn 2/7 CHƯA rõ trạng thái — CHƯA điều tra, không
  vội (không phải tiền thật).

## RETRO 2026-07-20 — tóm tắt cũ (chi tiết đầy đủ: kb/INCIDENTS.md)
6 sự cố, quy trình retro tự nó lỗi 2 lần liên tiếp (07-18→07-19) — ĐÃ ĐÓNG 07-22: chọn hướng B,
daily_retro.sh redesign 3-bước (bash tự chờ Wags, không qua Mike), commit `734cbac`,
arch-reviewer CONFIRMED trước commit.

## Trạng thái vận hành (cần tự kiểm tra lại độ mới trước khi tin — xem bài học ở trên)
SpaceX/ZaloPay LIVE, V2.4. CAPIT đã fire 07-21 (SAB/SIP/VNM khớp, PVT/NCT còn vướng). ZaloPay
từng crash do seed_shared KeyError (07-21), đã fix commit `ef5053e`. Chi tiết mới nhất: xem
context_pack.md "MỚI NHẤT" thay vì tin nguyên văn phần này nếu đã qua nhiều ngày.

