# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## KHẨN — security leak CHƯA đóng (retro 2026-08-24, kb/incidents/retro/retro-2026-08-24.md)
- Số tài khoản DNSE THẬT (SpaceX/ZaloPay) lộ public trên GitHub `minhtrido2023/thanhdt`.
  2 commit fix local (`c1303a96`, `3d358b14`) đã có nhưng **CHƯA PUSH** — `git push origin main`
  bị Claude Code auto-mode classifier chặn khi tự thử (2026-08-25 12:5x ICT). CẦN user tự
  `cd /home/trido/thanhdt && git push origin main` (an toàn — chỉ push commit đã xoá secret,
  không có gì mới cần review) hoặc duyệt cho Mike làm.
- Sau khi push: HEAD sạch nhưng repo vẫn `visibility=public` + số tài khoản còn trong git
  history cũ — 2 việc còn lại (chuyển private / rewrite history) cần user quyết.
- Sự cố #2 cùng batch: 3 tài khoản Linux khác trên máy (hainguyen/hungle/namiq) có sudo,
  vô hiệu hoá phân quyền file bảo vệ credential trading — cũng cần user quyết, chưa mở
  bus question. Nguồn: Taylor job `Taylor_20260824_070023`.

## Ưu tiên hiện tại
- **Go-live V2.4 lever LIVE từ 08-24**: capit_margin_lever.enabled=TRUE (SpaceX+ZaloPay). Mỗi
  ngày có CAPIT margin phải chạy `approve_margin_day.py --approved-by "John"` TRƯỚC bot.
- **VPI/BAL signal HOLD đến 2026-09-16** — SpaceX+ZaloPay HOLD_ALL theo VPI, không tự đổi.
- **Thứ Bảy 2026-08-29**: implement code chính sách margin đơn mã discretionary
  (`kb/projects/discretionary-margin-policy-20260823.md` §"VIỆC KẾ TIẾP") — dời có chủ đích
  để tránh đụng plan.py/executor.py lúc capit_margin_lever mới live.

## Còn hở nhỏ (low priority)
- `order_book_execution_shadow`: 0/40 outcome coverage.
- `PHSBroker.get_nav()` vẫn get_cash()-based (§25 gap) — rủi ro 0 (paper-only), escalate nếu
  có account PHS live tương lai.

## Đóng sổ gần đây (KHÔNG tự nêu lại)
- Retro 08-23, 08-24 cả hai đã ghi kb/incidents/retro/, Wags verify GAPS FOUND cả 2 lần, đã sửa.
- Bobby (macro-strategist) hoạt động chính thức từ 08-24, 3/7 episode margin-valuation-spread
  còn chưa phân loại độc lập (2007-08, 2011-12, 2018) — dispatch riêng khi cần.
- Heartbeat ccdb fix + false-positive paper-main early-check fix: cả hai merged, verified live.

