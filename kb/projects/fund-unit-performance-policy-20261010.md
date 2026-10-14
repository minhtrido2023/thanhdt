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
- **Bước 3: ĐÃ MERGE master (2026-10-14)** — nhánh `feat/fund-history-lock-20261014`: vòng 1 (`3642e43a1`) →
  arch-review NEEDS_CHANGES (B1 chặn: cờ `--raw-price-override` lách cổng ≤5% ⇒ GỠ hẳn, `daily_nav_snapshot.py`
  = master) → vòng 2/2b (`755be49f0`, `27d74c383`: B2-B16 + R1 mốc ngoài kho `--verify-anchor` + R2 quét tin EOD
  Discord) → review hẹp (không lỗi chặn) → Mike tự sửa F1-F5, F9, F10 (`9211c1589`). Có: kho bất biến
  (`nav_unit_ledger.py --seal/--restate/--verify-anchor`, manifest chỉ-thêm), công cụ đính chính
  `bin/fund_restatement.py` (impact/apply, bậc chính sách điểm 4, sao lưu, nhật ký), selfcheck khép kín.
  Evidence + README thao tác: `agents/Taylor/research/fund_history_lock_20261014/`.
  **CHƯA áp lên dữ liệu thật**: chuỗi 0-11 trong README đó (đính chính SpaceX 07-02 sửa NAV −4.429.292 đ, chèn
  08-06 cả 2 TK; đổi khoá lời xác nhận cash_identity; đợi ≥1 chu kỳ 19:10; rồi chốt sổ + post `SEAL_MD5` lên bus;
  rồi lịch kiểm lệch sổ chốt — user đã duyệt cả 4 việc 14/10 11:00).
- **Bước 2: ĐÃ MERGE master (2026-10-13)** — nhánh `feat/fund-cashflow-detect-20261012`: vòng 1 (`ea9d6969a`) → arch-review NEEDS_CHANGES → vòng 2 (`985821452`, `e6820cdc8`) → arch-review hẹp (không lỗi chặn) → vòng 2b Mike tự sửa N1-N4, N6-N8 (`b7d0576c6`). Chi tiết ở mục dưới. Bước 3-4 chưa giao.

## Xác nhận của user — 2 cửa sổ lệch tiền SpaceX KHÔNG phải nạp/rút (2026-10-12 23:17 ICT, `decided_by: user`)
Đẳng thức tiền (bước 2, ngưỡng 0,05% NAV) báo 2 cửa sổ lịch sử của SpaceX; user xác nhận cả hai
KHÔNG phải nạp/rút:
- 02/07 09:46 → 03/07 21:57: −539.935 đ (−0,054% NAV) — dòng NAV 02/07 chụp giữa loạt lệnh mua sáng
  go-live.
- 27/08 22:16 → 28/08 19:10: −1.107.515 đ (−0,112% NAV) — tiền đổi thành 110 MBB giá vốn 10.000 đ/cp
  (ZaloPay cùng ngày +20 MBB, −206.656 đ, dưới ngưỡng); chưa có nguồn ngoài xác nhận là quyền mua.
⇒ Nhánh `feat/fund-cashflow-detect-20261012` ĐÃ merge 2026-10-13; Mike chép 2 lời xác nhận (schema vòng 2,
`acked_residual_vnd`) từ `agents/Taylor/research/fund_cashflow_detect_20261012/proposed_acks.json`
vào `data/cash_identity_acks.json`, ghi người xác nhận = user, ngày 2026-10-12. CHƯA làm (file và
cơ chế chưa ở master). Review vòng 1: `.../arch_review_ea9d6969a/REVIEW.md`.

## Quyết định của user — bước 3 (2026-10-14 11:00 ICT, `decided_by: user`)
Sau arch-review nhánh `feat/fund-history-lock-20261014` (reviewer dựng lại độc lập: SpaceX 07-02 NAV đúng
990.304.455 — thấp hơn số đang lưu 4.429.292 đ; chèn 08-06 = 950.871.323 / 937.070.077):
1. **Lời xác nhận cash_identity cho cửa sổ SpaceX 07-02→07-03 ĐỔI KHOÁ** theo dòng đã đính chính
   (`balance_ts` 14:45:00): user xác nhận lại với khoá mới ⇒ sửa bản ghi hiện có, `confirmed_by` = user,
   ngày 2026-10-14 (không dùng bản ghi đứng tên Mike).
2. **Đính chính số đã công bố = MỘT dòng ghi chú ở báo cáo kế tiếp, KHÔNG phát hành lại** — áp cho các
   số lệch do sửa sổ (biến động tháng 8 ZaloPay in 25,58% đúng 18,27%; SpaceX 12,37 → 12,80; tháng 7
   17,3 → 17,4) và các số theo ngày đổi vì chèn 08-06 / sửa 07-02.
3. **Thứ tự thao tác dữ liệu thật**: áp đính chính trong khung 09:00–18:30 ICT, ĐỢI ≥ 1 chu kỳ 19:10, kiểm
   lại rồi mới CHỐT sổ (chốt gần như không đảo ngược).
4. **Duyệt thêm kiểm lệch sổ đã chốt** (chỉ-đọc, cảnh báo — không chặn gửi) vào chuỗi tối hoặc
   `report_delivery_gate`; cron/đường chạy cụ thể Mike tra `kb/cron_registry.md` (§11) trước khi cài.
Còn MỞ với user: các câu Q1–Q10 của bước 4 (`agents/Taylor/research/fund_step4_20261014/SPEC.md`), trước
hết đính chính mốc VN-Index của báo cáo ZaloPay (03/07 → 06/07).

## Nợ đã biết sau bước 1 (đưa vào bước 2/3, không chặn)
- ✅ **ĐÃ KIỂM lượt cron thật đầu tiên 19:10 ICT 2026-10-12 — sạch**: SpaceX "Từ go-live" −1,38%
  (CLI −1,375), ZaloPay −5,71% (CLI −5,712, mốc 987.865.567; mốc cũ 1 tỷ sẽ in −6,86%; con số
  −4,9% là asof 10-09, phiên 12/10 NAV −0,85%). `report_delivery_gate` COMPLETE cả hai.
- **Báo cáo ngày ZaloPay đã gửi in sai mốc**: 28/28 bản có dòng "Từ go-live" thấp hơn chuẩn
  1,127–1,220 điểm % (mốc 1 tỷ mặc định thay vì 987.865.567). Vượt ngưỡng đính chính 0,5% (điểm 4)
  ⇒ **USER DUYỆT 2026-10-11 10:04 ICT (`decided_by: user`)**: gửi MỘT dòng đính chính kèm báo cáo
  ngày 12/10, KHÔNG gửi lại 28 bản cũ. ✅ ĐÃ GỬI 2026-10-12 19:5x ICT vào topic Trading report
  (một tin `notify_thread.sh ... trading_report`; chỉ Discord, không email).
- nav_history THIẾU dòng phiên **2026-08-06** ở cả 2 tài khoản (dnse_raw ngày đó có balances tới
  19:10) ⇒ backfill `--from-raw` ở bước 3; tới lúc đó dòng tiền khai trong cửa sổ 08-06 14:45 →
  08-07 14:44 bị từ chối (đúng).
- 3 dòng NAV chụp trước giờ đóng cửa (SpaceX 2026-07-02 09:46; cả hai TK 2026-08-24 ~04:50) chưa
  có lối đính chính (08-24 không có balances sau đóng cửa) ⇒ bước 3.
- **Bước 2 — vòng 1, nhánh `feat/fund-cashflow-detect-20261012` (đã merge sau vòng 2/2b; job
  `Taylor_20261012_124854`)**: đẳng thức tiền `bin/cash_identity.py` (ngưỡng ĐO 0,05% NAV — registry
  `kb/data_registry/trading-bot/cash_identity.md`); **K2/K3/K5 đã sửa, K4 đã giết** (L06/T05/T07/D07
  + D11); cổng tỉ suất `report_delivery_gate` **fail-CLOSED** khi CLI rc≠0 /
  đầu ra hỏng; dòng tiền treo + chờ khai ra CẢNH BÁO (không chặn). Dạng cảnh báo ở vòng 1 (hai
  đoạn thô trong báo cáo nhà đầu tư) đã THAY bằng thiết kế vòng 2 ngay bên dưới.
- **Bước 2 VÒNG 2 (job `Taylor_20261012_162001`, sau arch-review NEEDS_CHANGES —
  `agents/Taylor/research/fund_cashflow_detect_20261012/arch_review_ea9d6969a/REVIEW.md`)**: sửa
  C1 (đối chiếu số lượng cổ phiếu ở MỌI cửa sổ), C2 (báo cáo gửi nhà đầu tư chỉ mang MỘT dòng trung
  tính; chi tiết đi Trading Daily + nav_snapshot JSON), S1 (lời xác nhận ở FILE RIÊNG
  `data/cash_identity_acks.json`, mang phần dư đã xem — `market_only` không còn tắt đẳng thức),
  S2 (khấu trừ rút Trứng vàng vào đẳng thức + nhãn "cần xác nhận khoản nội bộ"), S3 (dòng "phần dư
  trôi có hệ thống" trên 20 cửa sổ), S4/S5 (cổng tỉ suất chặn ô số hỏng; đường cảnh báo không làm
  gãy giao báo cáo), S6-S9, G3/G6/G7/G8. Arch-review hẹp vòng 2 (không lỗi chặn) → Mike tự sửa N1
  (gửi hỏng mang `NOTIFY_FAILED`), N2 (`nav_snapshot_daily.sh` cũng gửi chi tiết vận hành), N3
  (bản ghi vị thế chỉ nhận trong ±10 phút quanh lần chụp), N4 (bản ghi vị thế RỖNG khi NAV có cổ
  phiếu = không đọc được), N6 (selfcheck cho mã biến mất / lô trùng mã / thanh lý hết), N8 (cửa
  sổ thiếu bằng chứng trong 30 ngày qua vào dòng đếm hằng tối). **N5 CHƯA làm** (nhãn "cổ tức ghi
  và trả cùng cửa sổ" quá rộng — một khoản nạp thật nhỏ có thể mang nhãn nội bộ; cửa sổ vẫn MỞ nên
  không phải âm tính giả, chỉ là nhãn dễ dẫn người duyệt ack nhầm).
- **Việc của NGƯỜI sau khi merge bước 2** (user ĐÃ xác nhận 2 cửa sổ SpaceX 23:17 ICT 12/10 — xem mục "Xác nhận của user" ở trên; còn lại cửa sổ ZaloPay 08-28 chưa hỏi user): ba cửa sổ lịch sử đang mở (SpaceX 07-02→07-03; SpaceX
  và ZaloPay 08-27→08-28 — nhận thêm MBB ở giá vốn 10.000 đ/cp ngoài lệnh) ⇒ tới khi user xác nhận
  và Mike chép `agents/Taylor/research/fund_cashflow_detect_20261012/proposed_acks.json` thành
  `data/cash_identity_acks.json`, báo cáo ngày của CẢ HAI tài khoản mang một dòng "Có N khoản biến
  động tiền chưa đối chiếu xong …" và Trading Daily nhận một dòng đếm mỗi tối. Chưa xác minh bằng
  nguồn ngoài rằng MBB 08-28 là quyền mua phát hành thêm.
- **Nợ để lại sau vòng 2** (không chặn): G1 selfcheck sổ đơn vị + cổng bước nhảy còn đọc `data/`
  sống; G2 đẳng thức đọc lại toàn bộ `dnse_raw` mỗi lần gọi (~2 giây, tăng tuyến tính; archive
  `dnse_raw` sẽ sinh cảnh báo giả cho cửa sổ cũ); G4 mã lệnh DNSE không duy nhất qua các ngày (đừng
  dedupe toàn cục); G5 subprocess `nav_period_returns.py` trong cổng không có timeout. Chi tiết:
  `kb/data_registry/trading-bot/cash_identity.md` mục "Nợ".
- Còn mở sau bước 2: **K1** SpaceX mốc 1 tỷ là số dư SÁNG 07-01 ⇒ khe 07-01/07-02 (quá khứ, sổ dòng
  tiền rỗng); DNSE không gửi email xác nhận nạp/rút (đo 2026-10-12) ⇒ chứng từ nạp/rút vẫn do
  người cung cấp.
- `trading_bot/vn_market.is_holiday` chưa khai Tết 2027/Giỗ Tổ ⇒ tiền vào dịp đó bị từ chối oan
  ("thiếu dòng của phiên") — khai lịch trước 02/2027.
- Hạ tầng (việc riêng, giao Wags): `tz_anchor_gate.baseline_key` tính sai khoá dưới GIT_DIR của
  worktree `WorkingClaude/wt-*` (buộc `SKIP=tz-anchor-gate`); `nav_scripts_2account_selfcheck.py`
  gọi broker thật và chạy snapshot trên `data/` THẬT khi chạy từ worktree (đêm 10→11/10 để lại
  `dnse_raw_2026-10-11.jsonl`, `verified_snapshot_*_2026-10-11.json`, nav_history thật có dòng
  10-11 trong ~23 giây rồi được khôi phục) ⇒ cần sandbox hoá; `portfolio_status_selfcheck` không
  khép kín (BigQuery + ghi `data/value_radar_series.csv`).

## Bước 4 — quyết định user 2026-10-14 13:05 ICT (`decided_by: user`)
Q1–Q10 trong `agents/Taylor/research/fund_step4_20261014/SPEC.md` § "Câu hỏi cần user quyết": **chọn MẶC ĐỊNH cả 10 câu**,
trừ **Q2**: user yêu cầu chỉ số có cổ tức phản ánh **số thực nhận về hiệu suất thực tế, không phải số trên sổ** ⇒
cột chỉ số có cổ tức trong báo cáo dùng **`tr_net` (sau thuế 5%)**, KHÔNG phải `tr_gross`. `tr_gross` vẫn lưu trong
`vnindex_tr_daily.csv` để đối chiếu, không hiển thị làm số chính. Chú thích báo cáo phải nêu "sau thuế TNCN 5% trên cổ tức".
Mike diễn giải "số thực" = sau thuế (nhà đầu tư thật chỉ nhận ròng; danh mục cũng ghi cổ tức ròng) — chờ user xác nhận nếu hiểu khác.
