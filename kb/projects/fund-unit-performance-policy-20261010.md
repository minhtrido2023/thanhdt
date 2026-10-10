# Tài khoản quản lý = quỹ mở: chính sách đo hiệu suất (user duyệt 2026-10-10 23:57 ICT)

`decided_by: user` — user duyệt cả 5 điểm ở topic Discord 1558282936489611354 (phương án Mike
trình 23:40 ICT cùng ngày). Áp cho SpaceX + ZaloPay và mọi account thêm sau.

## Quyết định (5 điểm)
1. **Quy tắc chốt giao dịch vốn**: nạp/rút ngày T ghi theo giá đơn vị quỹ chốt CUỐI ngày T
   (`timing="eod"` là mặc định). User nạp/rút NGOÀI giờ giao dịch. Buộc phải làm trong phiên ⇒
   bản ghi dòng tiền phải khai giờ và dùng quy ước đầu ngày (`"bod"`) tường minh.
2. **ZaloPay hai chuỗi**: (a) toàn tài khoản = số chính thức của chủ tài khoản; (b) "phần bot
   quản lý" loại DGC + vị thế legacy, dùng để so với SpaceX/backtest. Tiền bán DGC chuyển sang
   bot = dòng tiền vào chuỗi (b).
3. **Mốc so sánh**: thêm VN-Index CÓ cổ tức (total return), giữ song song VN-Index giá. Nguồn dữ
   liệu chưa xác minh — phải kiểm trước khi wire.
4. **Ngưỡng đính chính số đã công bố** (theo độ lệch NAV/tỉ suất): < 0,05% NAV ⇒ sửa từ nay,
   không đính chính · 0,05%–0,5% ⇒ sửa sổ + ghi chú ở báo cáo kế tiếp · > 0,5% ⇒ phát hành lại
   báo cáo.
5. **KHÔNG mô phỏng phí quản lý/phí thưởng** — số công bố đã trừ mọi chi phí thật (phí giao
   dịch, thuế, lãi vay); gross = net.

## Nguyên tắc đo
- Số hiệu suất chính thức = tỉ suất gia quyền thời gian qua **giá một đơn vị quỹ** (khởi điểm
  10.000 đ tại `data/account_inception.json`). Nạp ⇒ phát hành đơn vị, rút ⇒ huỷ đơn vị; giá đơn
  vị không đổi vì dòng tiền. Sổ đơn vị chỉ-ghi-thêm.
- Dòng tiền NGOÀI: nạp/rút ngân hàng, chuyển cổ phiếu vào/ra. NỘI BỘ (không phải dòng tiền): cổ
  tức, lãi Trứng vàng, phí, thuế, lãi vay ký quỹ, chuyển tiền ↔ Trứng vàng, vay/trả ký quỹ.
- Báo HAI số, không trộn: tỉ suất gia quyền thời gian (so với quá khứ/chỉ số/backtest) và tỉ
  suất gia quyền theo tiền (IRR) + lãi/lỗ VND (kết quả thật của chủ tài khoản).
- Kỳ < 12 tháng KHÔNG quy năm (SpaceX có số quy năm từ 2027-07-01). Đủ 36 tháng mới thêm độ biến
  động 3 năm.
- Đổi cách định giá ⇒ tính lại cả chuỗi theo cách mới + ghi chú trong báo cáo.
- Áp PHƯƠNG PHÁP của GIPS, KHÔNG tuyên bố "tuân thủ GIPS" (đó là chứng nhận cấp công ty).

## Hiện trạng lúc duyệt (đo 2026-10-10)
- `bin/nav_period_returns.py` đã chain-link theo ngày có dòng tiền; `data/account_cash_flows.json`
  rỗng cả 2 account (chưa có nạp/rút sau inception) ⇒ dựng sổ đơn vị không phải ước lượng lại.
- Lỗ hổng: chưa có chuỗi giá đơn vị chốt; dòng tiền ghi tay + cổng bước nhảy NAV 5% (lọt khoản
  ≲50tr); `timing` mặc định đang là `bod`; nav_history có ngày `nav_is_estimate=True` (SpaceX
  8/69, ZaloPay 6/66) và cột Trứng vàng đổi cách ghi 3 giai đoạn; mốc so sánh là chỉ số giá; ZaloPay
  có DGC ~36% NAV ngoài phạm vi bot.

## Lộ trình (mỗi bước qua arch-review trước khi merge)
1. Sổ đơn vị quỹ + `timing` mặc định `eod` + IRR/lãi-lỗ VND + chặn quy năm < 12 tháng. Nghiệm
   thu: chưa có dòng tiền ⇒ ra ĐÚNG số đang công bố (SpaceX asof 2026-10-09: từ đầu −1,33%).
2. Tự phát hiện dòng tiền bằng đẳng thức tiền hằng tối (ngưỡng đo từ nhiễu thật, dự kiến ~0,1%
   NAV) + kiểm DNSE có email xác nhận nạp/rút không.
3. Rà các ngày NAV ước tính + 3 giai đoạn ghi Trứng vàng, khoá chuỗi lịch sử; cài ngưỡng đính
   chính (điểm 4) thành cơ chế.
4. Mốc so sánh có cổ tức + chuỗi riêng ZaloPay "phần bot quản lý".

## Trạng thái
- 2026-10-10: bước 1 giao Taylor (xem `kb/memory/Mike.md` cho job id). Bước 2-4 chưa bắt đầu.
