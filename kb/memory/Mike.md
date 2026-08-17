# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T01:10Z (yêu cầu tóm tắt plan hôm nay, đang dispatch DollarBill)

## Tóm tắt plan hôm nay (08-17) — ĐANG CHỜ DollarBill trình bày
- User yêu cầu gửi lại tóm tắt plan mua/bán hôm nay, đúng định dạng đã yêu cầu 08-10
  (Bal/Lag/Park/Capit/Cash %NAV, trước/sau, lý do từng lệnh).
- Dispatch DollarBill (job DollarBill_20260817_011043, opus/high, timeout 900s, --bg — LƯU Ý:
  dispatch ĐỒNG BỘ bị timeout ở 2 phút Bash tool và job bị cancelled tự động, phải dùng --bg).
- Dữ liệu thô đã đọc từ plan file: SpaceX 1 lệnh (mua TV1 500cp @20.640, ceiling_rule=None vì
  injected TRƯỚC Rule A fix 08-15, không phải bug); ZaloPay 0 lệnh. Cả 2 approved_by=None.
- Cần verify %NAV breakdown qua pipeline §6 chuẩn (verify_account_snapshot.py +
  daily_nav_snapshot.py), không tự ước lượng.
- Cũng cần xác nhận trạng thái GDKHQ dry-run trace 08-17 (BID/MBS/SSI/VIX) đã setup/chạy chưa.
- ĐANG CHỜ job này — user cần trước ~09:05 ICT (giờ mở cửa).

## GDKHQ D1-D3 — CONFIRMED (high), quyết định: dry-run trace 08-17 trước khi bật thật
- Cần theo dõi/xác nhận dry-run hôm nay đã chạy đúng chưa (xem output trong job DollarBill vừa
  dispatch, hoặc tự kiểm riêng sau).

## Việc còn hở (chưa xử lý, không khẩn)
1. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
2. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17 (HÔM NAY).
3. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.
4. lag_entry_anchor.py:105 đọc thẳng ticker.Price làm trần — chưa vá, không khẩn, 0đ thiệt hại.
5. rollup-of-agent-ownership-bug-20260816 — chưa fix, không khẩn (rollup_of chưa dùng thật).

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- Dispatch job >2 phút BẮT BUỘC --bg — sync dispatch bị Bash tool cắt ở 2 phút và tự cancel job.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false, pilot chờ signal thật.
- TV1 Rule A (bản fix UPCOM) đang LIVE từ 08-15, an toàn.

