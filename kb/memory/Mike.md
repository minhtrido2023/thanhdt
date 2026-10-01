# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-10-01 11:20 ICT (thread 1554692001541398628)
- DONE: park 0% merge (WC main ff + mike master), arch-review APPROVED, current_ops cập nhật (96d05e3e), bus question merge đã đóng. SCL SpaceX đã ghi sổ LAG (job 040222): park_holdings SpaceX reconcile.ok=true (Mike tự đọc lại artifact 11:16). Dry-run đêm nay: SpaceX TRIM ~151,7tr (park_mv 166,5tr), ZaloPay ~84tr/13 mã.
- ĐANG CHỜ: Taylor job 041603 (kill-switch A vòng 4: CCTG silent-drop/range guard/armed nhất quán/tests/text trigger). Sau đó quant-skeptic vòng 4; CONFIRMED mới merge branch wire/macro-killswitch-a-deposit75-20261001, rồi áp text trigger vào trading_rules.json, đóng bus questions (duyet-merge-macro-killswitch-a-wiring, quant-skeptic-round2/3-...).
- ⚠️ RỦI RO MỚI user cần biết: park 0% đẩy ~236tr (SpaceX 152 + ZaloPay 84) vào Trứng vàng — vượt trần đề xuất legal-vn (sleeve ≤10% NAV, ~2%/TCPH, chưa user chốt). Egg SpaceX hiện 304,9tr.
- ⚠️ verify_account_snapshot không bắt lệnh bán SCL tay (bảng P&L vẫn liệt kê SCL mở) — báo cáo tháng 09 (tạo 02:00 01/10) có thể sai SCL SpaceX; cần kiểm.
## Chờ user: định nghĩa 'xu hướng hạ' (trigger park); quyết rating_8l/DCF dùng effective rate (bảng diff registry cctg_rate_vn.md); Discretionary DRI/TV1.
## Backlog: 9 topic selfcheck-red cần triage; VNM exright note cho Winston.

- [2026-10-01T04:30:33Z] 11:30 kill-switch A: quant-skeptic vòng 4 NOT_CONFIRMED (close): còn (1) dòng CSV CCTG ngày ≤ anchor 2026-09-30 bị drop im lặng, (2) text trigger v2 nói 'stale→armed ngay' nhưng code chỉ armed nếu lần đọc cuối >7,5, (3) docstring cũ. Chờ user: chấp nhận merge kèm gap hay vòng 5 micro-fix. Branch wire/macro-killswitch-a-deposit75-20261001 (814a91ff) CHƯA merge. Park 0% + SCL ledger đã xong.
- [2026-10-01T04:41:03Z] 11:40 user DUYỆT: (a) vòng 5 micro-fix kill-switch A; (b) CHÍNH SÁCH tiền sau park 0%: tiền thu về phần lớn VÀO TRỨNG VÀNG, trừ khi số tiền quá ít hoặc tiền chưa về (T+2/chưa settle) — user chấp nhận dồn egg, chưa nêu trần cụ thể. Dispatch: Taylor killswitch vòng 5, Taylor egg-routing design (read-only), Taylor/data-ops kiểm báo cáo tháng 09 SCL SpaceX.
