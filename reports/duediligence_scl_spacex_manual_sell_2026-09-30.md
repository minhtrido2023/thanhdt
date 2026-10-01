# Due diligence — bán SCL ngoài plan (SpaceX, 2026-09-30)

## Sự việc
User John **tự bán SCL 1.500cp qua app DNSE** lúc ~14:43 ICT ngày 2026-09-30, không qua lệnh bot,
không nằm trong plan đã duyệt hôm đó. Lô bị bán thuộc **sổ LAG** (`BUY-SCL-LAG-03`, mua 2026-08-10,
1.500cp giá vốn 23.600,0001đ/cp). Tài khoản ZaloPay **không** bán SCL (vẫn giữ nguyên vị thế).

## Xác nhận — 2 nguồn độc lập, khớp tuyệt đối
1. **Broker position snapshot** (`dnse_raw_2026-09-30.jsonl`, account 0002023347): vị thế SCL
   chuyển OPEN→PENDING_CLOSE lúc `modifiedDate=2026-09-30T07:43:39.401943562Z` (=14:43:39 ICT),
   `accumulateQuantity=1500`, `closedQuantity=1500`, `openQuantity=0`, `averageClosePrice=28300`,
   `costPrice=23600.0001`.
2. **Email khớp lệnh DNSE** (`fetch_dnse_khoplenh_email.py` → `dnse_khoplenh_broker_confirm_30-09-2026.csv`):
   2 dòng BÁN SCL, tiểu khoản 0002023347 — 1.400cp + 100cp = **1.500cp @ 28.300đ**, tổng giá trị
   42.450.000đ, phí: phí_trả_sở 7.641đ + phí_DNSE 29.715đ + thuế 42.450đ = **tổng phí 79.806đ**.

Hai nguồn khớp 100% (số lượng, giá, thời điểm) → xác nhận sự kiện có thật, không phải lỗi dữ liệu.

## Tài chính
- Giá trị bán: 1.500 × 28.300 = 42.450.000đ
- Giá vốn: 1.500 × 23.600,0001 = 35.400.000,15đ
- **Lãi gộp: +7.049.999,85đ** (+19,9% trên giá vốn)
- Phí + thuế: 79.806đ
- **Lãi ròng: +6.970.194đ**
- Tiền mặt về tài khoản: 42.450.000 − 79.806 = 42.370.194đ

## Tác động NAV
- Đóng 1 vị thế sổ LAG, chuyển từ cổ phiếu sang tiền mặt; NAV tổng không đổi ngoài phần lãi ròng
  thực hiện (+6.970.194đ ghi nhận realized P&L).
- Nếu KHÔNG bán, theo giá đóng cửa 2026-09-30 (28.600đ), unrealized P&L tại thời điểm chốt sổ sẽ là
  +7.500.000đ (+21,2%) — tức bán sớm hơn khoảng 1,9pp so với nắm tới cuối phiên, chênh lệch không
  đáng kể so với lãi đã chốt.

## Khớp sổ (ledger) — đã xử lý
Thêm dòng FILL (PLACE/FILL/DONE) vào `exec_SpaceX_2026-09-30_journal.csv` (account SpaceX ONLY,
không đụng ZaloPay — §12 coding_guidelines), book=LAG, theo đúng tiền lệ xử lý sự kiện ngoài-bot
(MBB rights-subscription 2026-08-28). Sau khi thêm:
- `park_holdings.py --account SpaceX`: **reconcile.ok = True**, 0 mismatch.
- `compute_park_trim.py --account SpaceX` (park target 0%, dry-run): decision=TRIM, trim_proposed
  151.685.000đ / park_mv 166.620.850đ, blocked=[], reconcile_ok=true.

## Ghi chú về xác minh P&L tổng (verify_account_snapshot.py)
Script chuẩn `verify_account_snapshot.py` lấy fill P&L từ bản ghi `orders` trong `dnse_raw` —
ngày 2026-09-30 **không có bản ghi `orders`** cho SpaceX (chỉ có `positions`/`balances`/`quote_l2`),
vì lệnh bán này đặt qua app di động, không qua API mà poller daily đang theo dõi. Hệ quả: báo cáo
tổng P&L danh mục của script này tạm thời còn liệt SCL như một vị thế ĐANG MỞ với unrealized P&L —
**không dùng con số đó cho SCL**; P&L thực của sự kiện này đã được tính độc lập ở trên (xác nhận
qua 2 nguồn), còn `park_holdings.py`/journal đã phản ánh đúng SCL đã đóng.

## Phân loại
Bán bất thường ngoài plan đã duyệt (user tự quyết, không phải signal hệ thống). Không có dấu hiệu
sai lệch rủi ro/risk-limit. Không cần escalate thêm trừ khi user muốn thay đổi chiến lược LAG cho
mã này.
