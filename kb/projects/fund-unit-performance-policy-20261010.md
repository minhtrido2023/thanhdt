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

## Luật gán dòng tiền vào giá đơn vị (bước 1, LIVE trên master từ 2026-10-11)
Người khai CHỈ ghi ngày + giờ ICT (`time_ict`, bắt buộc) + số tiền + bằng chứng; code tự suy quy
ước. Một luật: **tiền giao dịch ở giá đơn vị chốt GẦN NHẤT TRƯỚC thời điểm tiền vào/ra**, tham gia
tỉ suất từ sau đó.
| Tiền vào/ra lúc | Giá áp dụng |
|---|---|
| Sau giờ đóng cửa ngày T (14:45), kể cả tối muộn | giá chốt ngày T |
| Trong phiên ngày T / trước giờ mở cửa ngày T | giá chốt phiên liền trước |
| Cuối tuần, ngày nghỉ lễ | giá chốt phiên liền trước |
Hai dòng cuối là phần Mike MỞ RỘNG từ quyết định 1 (user mới chốt ca "sau đóng cửa" và "trong
phiên") — **USER CHỐT 2026-10-11 10:22 ICT (`decided_by: user`): GIỮ giá chốt phiên liền trước**
cho tiền vào trước giờ mở cửa / cuối tuần / ngày nghỉ. Phương án bị loại = khớp ở giá chốt phiên KẾ
TIẾP (kiểu quỹ mở thuần). Hệ quả đã trình user: tiền mới nằm chờ làm LOÃNG tỉ suất của đúng phiên
đầu sau khi nạp (ví dụ nạp 200tr vào quỹ 1 tỷ, phiên đó +2% ⇒ in +1,67% thay vì +2,00%); tổng tiền
không đổi, các phiên sau hai cách đi giống nhau. Code bước 1 đã chạy đúng luật này — không sửa gì.
Fail-closed (từ chối, không đoán): thiếu giờ; ngày trong tương lai; `timing` khai khác suy ra; dòng
NAV dùng làm giá chụp TRƯỚC giờ đóng cửa của chính phiên đó; nav_history THIẾU dòng của phiên đóng
cửa gần nhất; `balance_ts` thiếu/không tăng nghiêm ngặt; số tiền không hữu hạn. Chi tiết + bẫy:
`kb/data_registry/trading-bot/account_cash_flows.md`, `nav_unit_ledger.md`, `account_inception.md`.

## Trạng thái
- **Bước 1 XONG — merge master `cdb565a6` (2026-10-11 04:1x ICT)**, nhánh
  `feat/fund-unit-ledger-20261011`, 3 vòng arch-review (feaa33b5 → 75060709 → e102ebef), lần cuối
  APPROVED. Có: `bin/nav_unit_ledger.py` (sổ đơn vị, `--seal` TỪ CHỐI thư mục dữ liệu thật tới bước
  3); `nav_period_returns.py` một công thức = tỉ số giá đơn vị + `pnl_vnd`, `mwr_pct` (IRR kỳ),
  `pending_flows`/`dropped_flows`, quy năm = null khi < 365 ngày; mọi % của dòng NAV hằng ngày
  (`daily_nav_snapshot.py`, `portfolio_status.py`) qua cùng công thức, mốc `account_inception.json`.
  Nghiệm thu asof 2026-10-09 không đổi: SpaceX −1,33 / 1,024 / 0,519; ZaloPay −4,907 / −1,162 / −2,01.
  Review + bằng chứng: `agents/Taylor/research/fund_unit_ledger_20261011/` (REVIEW.md, REVIEW2.md).
- **CHƯA chốt sổ thật** (`data/execution_logs/nav_unit_ledger_*.csv` chưa tồn tại) — thuộc bước 3.
- **Bước 2: USER DUYỆT giao 2026-10-11 10:04 ICT** — giao SAU khi lượt cron tối thứ Hai 12/10
  chạy sạch. Bước 3-4 chưa giao.

## Nợ đã biết sau bước 1 (đưa vào bước 2/3, không chặn)
- **Nhìn 2 dòng 💰 NAV của lần cron thật đầu tiên: 19:10 ICT thứ Hai 2026-10-12** (chưa có lượt
  `daily_nav_snapshot.py`/`eod_trading_report.sh` end-to-end thật với dòng mới). ZaloPay phải ra
  quanh −4,9% "Từ go-live" thay cho −6,06%.
- **Báo cáo ngày ZaloPay đã gửi in sai mốc**: 28/28 bản có dòng "Từ go-live" thấp hơn chuẩn
  1,127–1,220 điểm % (mốc 1 tỷ mặc định thay vì 987.865.567). Vượt ngưỡng đính chính 0,5% (điểm 4)
  ⇒ **USER DUYỆT 2026-10-11 10:04 ICT (`decided_by: user`)**: gửi MỘT dòng đính chính kèm báo cáo
  ngày 12/10, KHÔNG gửi lại 28 bản cũ. Chưa gửi (mốc: sau cron 19:10 ICT thứ Hai 12/10).
- nav_history THIẾU dòng phiên **2026-08-06** ở cả 2 tài khoản (dnse_raw ngày đó có balances tới
  19:10) ⇒ backfill `--from-raw` ở bước 3; tới lúc đó dòng tiền khai trong cửa sổ 08-06 14:45 →
  08-07 14:44 bị từ chối (đúng).
- 3 dòng NAV chụp trước giờ đóng cửa (SpaceX 2026-07-02 09:46; cả hai TK 2026-08-24 ~04:50) chưa
  có lối đính chính (08-24 không có balances sau đóng cửa) ⇒ bước 3.
- Còn sai IM LẶNG ngoài phạm vi bước 1 (arch-review lần 3): **K3** dòng NAV mang ngày T nhưng chụp
  sau khi phiên T+1 đã đóng cửa (xảy ra khi chạy lại snapshot ngày cũ theo đường live) — hướng sửa:
  một điều kiện "phiên đóng cửa gần nhất theo lần chụp của dòng cho giá == theo thời điểm tiền vào"
  gộp luôn kiểm thiếu phiên + chụp trước đóng cửa; **K1** SpaceX mốc 1 tỷ là số dư SÁNG 07-01 ⇒
  khe 07-01/07-02 (quá khứ, sổ dòng tiền rỗng); giờ khai lệch vài giây quanh lần chụp với khoản
  < 5% NAV (lớp bắt = đẳng thức tiền của bước 2).
- Lỗi nhỏ chưa sửa: **K2** `account_cash_flows.py:339` từ chối oan tiền tới ngày không phiên khi
  dòng ngày đó chụp trước 14:45 (1 dòng); **K5** `starting_capital`/`nav` = NaN ra "+nan%" ở dòng
  NAV ngày (`nav_unit_ledger.py:139`, 1-2 dòng); **K4** 4 mutant sống L06/T05/T07/D07.
- Cổng tỉ suất của `report_delivery_gate` vẫn fail-open khi CLI rc≠0, và chưa đọc `pending_flows`
  (nên cảnh báo, không chặn cứng) ⇒ bước 2.
- `trading_bot/vn_market.is_holiday` chưa khai Tết 2027/Giỗ Tổ ⇒ tiền vào dịp đó bị từ chối oan
  ("thiếu dòng của phiên") — khai lịch trước 02/2027.
- Hạ tầng (việc riêng, giao Wags): `tz_anchor_gate.baseline_key` tính sai khoá dưới GIT_DIR của
  worktree `WorkingClaude/wt-*` (buộc `SKIP=tz-anchor-gate`); `nav_scripts_2account_selfcheck.py`
  gọi broker thật và chạy snapshot trên `data/` THẬT khi chạy từ worktree (đêm 10→11/10 để lại
  `dnse_raw_2026-10-11.jsonl`, `verified_snapshot_*_2026-10-11.json`, nav_history thật có dòng
  10-11 trong ~23 giây rồi được khôi phục) ⇒ cần sandbox hoá; `portfolio_status_selfcheck` không
  khép kín (BigQuery + ghi `data/value_radar_series.csv`).
