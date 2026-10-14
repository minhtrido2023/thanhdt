# Quỹ mở — bước 3/4: khoá lịch sử + cơ chế đính chính

Job `Taylor_20261014_020334` (2 lượt; lượt 2 hoàn tất phần kiểm, mutant, bằng chứng, commit).
Nhánh **`feat/fund-history-lock-20261014`** @ **`3642e43a1`** (1 commit trên master `04ddef5f6`),
worktree `agents/Taylor/wt-fundlock-1014`. KHÔNG merge, KHÔNG push, KHÔNG ghi `data/` thật
(md5 `nav_history_SpaceX.csv` thật = `12ee9b87…`, ZaloPay = `f8b6a978…` — đúng bằng md5 "trước" mà
công cụ đo trên bản sao; thư mục thật không có file sổ/manifest/nhật ký nào).

Dựng lại mọi bằng chứng: `bash run_evidence.sh` (bản sao dữ liệu thật vào `/tmp/fundlock_1014/final_*`).

## A. Rà dòng ước tính + 3 giai đoạn Trứng vàng

**14 dòng `nav_is_estimate=True`** (SpaceX 8: 07-21, 07-22, 08-10, 08-25, 08-27, 09-21, 09-23, 10-01;
ZaloPay 6: 08-07, 08-10, 08-25, 08-27, 09-21, 09-23). Lý do ước tính của cả 14: dựng `--from-raw` (vị
thế + số dư trong `dnse_raw`, giá = BQ `Price`) thay vì chụp live. Đo (`A_review_rows.txt`,
`A2_est_arbitrate.txt`):
- Tiền / nợ / Trứng vàng của cả 14 dòng **khớp** bản ghi `balances` sau đóng cửa cùng ngày.
- Cổ phiếu = KL × BQ `Price`. So với giá broker cùng bản ghi: lệch −0,23%…+0,93% NAV, nhưng phần lớn
  là feed broker TRỄ một phiên (giá broker = giá phiên trước) ⇒ BQ đúng hơn.
- So với nguồn thứ ba (giá broker sáng phiên kế, 10/14 dòng có): |lệch| ≤ 0,12% NAV, trừ 09-21
  (SpaceX +0,41%, ZaloPay +0,22%) — đã phân xử: do DRI, giá sáng 09-22 là giá tham chiếu ngày
  KHÔNG HƯỞNG QUYỀN (BQ Price/Close của DRI đổi 1,0725 → 1,0 đúng 09-22), không phải BQ sai. Phần còn
  ngờ: BQ `Price` DRI đứng 14.800 ba phiên trong khi `Close` nhích +0,65% ngày 09-21 ⇒ tối đa
  ~333.000 đ (0,034% NAV SpaceX) / 171.000 đ (0,018% ZaloPay) — bậc 1.
- **Đề xuất: GIỮ NGUYÊN cả 14 + giữ nhãn ước tính.** Dựng lại `--from-raw` sẽ ra đúng số đang có
  (cùng công thức); không dòng nào cần loại khỏi sổ khoá.

**Trứng vàng — cách ghi đổi 3 lần** (`A4_egg_phases.txt`):
| Giai đoạn | SpaceX | ZaloPay | Cách ghi |
|---|---|---|---|
| I | 07-02 → 07-16 | 07-07 → 07-16 | hai cột trống (tiền Trứng vàng nằm trong `cash`) |
| II | 07-17 → 07-20 | 07-17 → 07-20 | `offbook_assets` nhập tay (302.108.211 / 147.473.247) |
| III | 07-21 → 08-18 | 07-21 → 08-18 | 0 hoặc trống (đã rút hết về mua cổ phiếu) |
| IV | 08-19 → nay | 08-19 → nay | `egg_assets` đọc từ API |

Bất biến `nav = mtm + cash − debt + offbook + egg` khớp 71/71 và 68/68 dòng. Phần dư đẳng thức tiền
tại MỌI cửa sổ đổi cách ghi: lớn nhất **+141.801 đ = 0,0152% NAV** (SpaceX 07-20→07-21), còn lại
≤ 0,003% ⇒ **không có bước nhảy giả trong giá đơn vị** (dưới ngưỡng 0,05%). Cách ĐỊNH GIÁ không đổi
(luôn là số dư Trứng vàng theo broker), chỉ đổi CỘT ghi ⇒ không phải ca "đổi cách định giá ⇒ tính lại cả
chuỗi". **Đề xuất: giữ nguyên + ghi chú ở registry.**

## B. Dòng thiếu / chụp trước đóng cửa / K3 / K1

| Dòng | Hiện trạng | Đề xuất | Hệ quả tỉ suất |
|---|---|---|---|
| **08-06 cả 2 TK** | thiếu | CHÈN: SpaceX 950.871.323, ZaloPay 937.070.077 (`--from-raw`, vị thế + số dư 19:10; VHM lấy 77.100) | từ đầu/MTD/WTD mọi ngày KHÔNG đổi; tỉ suất ngày 08-07: SpaceX +0,9735 điểm %, ZaloPay −2,6914 (trước đó gộp 2 phiên) |
| **SpaceX 07-02** (chụp 09:46) | NAV 994.733.747 **cao hơn thực 4.429.292 đ (0,4453%)** — đếm trùng lô VGC 100 cp | SỬA: tiền −409.315.545, NAV 990.304.455, `balance_ts` 14:45:00, ước tính | tỉ suất ngày 07-02 −0,4429 điểm %, 07-03 +0,4445; từ 07-03 trở đi KHÔNG đổi |
| **08-24 cả 2 TK** (chụp ~04:50) | NAV đúng là giá chốt | GIỮ + nhận tường minh `--accept-preclose` khi chốt | không |
| ZaloPay 07-27 (chụp 07-28 09:15) | hợp lệ (trước giờ đóng cửa phiên kế) | giữ | không |
| 08-31 (ngày không có phiên) | hợp lệ | giữ | không |

- `--from-raw` 08-06 **bị cổng giá từ chối** khi chưa có giá thay: BQ `Price` VHM 08-06 = 153.000 (đứng
  ở giá trước chia thưởng 1:1), `Close` = 77.100. Thêm `--raw-price-override MÃ=GIÁ` +
  `--raw-price-evidence` (chỉ với `--from-raw`, giá thay vẫn qua cổng lệch ≤5%, ghi dấu vào
  `nav_source`). Kết quả khớp số báo cáo tuần 03–07/08 ĐÃ GỬI đã tự dựng lại: 950.871.297 / 937.070.045 —
  lệch **+26 đ / +32 đ** (báo cáo lấy số dư 15:13, backfill lấy 19:10) ⇒ bậc 1.
- 08-24: 0 lệnh khớp cả 2 TK; cổ phiếu trong dòng = KL × BQ `Price` 08-24 (lệch 0 đ); tiền = tiền
  08-21; phần dư đẳng thức hai cửa sổ kề ≤ 33 đ. Không có `balances` sau đóng cửa ⇒ không dựng lại
  được, và không cần.
- **K3**: điều kiện "phiên đóng cửa gần nhất theo lần chụp" cho luật gán dòng tiền ĐÃ có ở master
  (bước 2) — không làm lại. Phần thêm: cùng điều kiện thành CỔNG CHỐT (`seal_gate`): dòng chụp sau khi
  phiên kế đã đóng cửa ⇒ từ chối chốt, không có lối nhận; gộp chung với kiểm thiếu phiên + chụp trước
  đóng cửa. Dữ liệu thật hiện không có dòng K3 nào.
- **K1** (mốc 1 tỷ SpaceX là số dư SÁNG 07-01): `dnse_raw_2026-07-01.jsonl` không có bản ghi `positions`
  nào và `balances` dừng 14:29:57 (trước đóng cửa) ⇒ **không dựng được dòng đóng cửa 07-01 bằng máy**.
  Đề xuất GIỮ + ghi chú: tỉ suất "ngày" đầu tiên (07-02) gộp hai phiên; mọi số từ đầu/MTD/WTD không phụ
  thuộc. Sổ dòng tiền rỗng, sao kê tháng 7 không có nạp/rút ⇒ khe này không gán sai dòng tiền nào.

File đính chính: `corrections/correction_{SpaceX,ZaloPay}_AB.json`; diff nav_history:
`corrections/nav_history_*_AB.diff`; lời xác nhận đẳng thức tiền phải đổi khoá theo:
`corrections/cash_identity_acks_PROPOSED.json` (cửa sổ SpaceX 07-02→07-03: `from` 09:46:35 → 14:45:00,
phần dư −539.935 đ không đổi). Không đổi khoá ⇒ cron đẳng thức tiền báo 1 nghi vấn (đã đo).

## C. Chốt sổ (`nav_unit_ledger.py`, kho bất biến §8c)

Trên bản sao ĐÃ áp A+B (`C_seal/log.txt`); bản sao CHƯA sửa bị cổng từ chối (`C_seal/log_base_refused.txt`:
SpaceX 3 chỗ, ZaloPay 2 chỗ).

| | SpaceX | ZaloPay |
|---|---|---|
| Thiếu `--real-data` | rc=3 | rc=3 |
| Chưa nhận dòng 08-24 | rc=2 (SealGateError) | rc=2 |
| Chốt | 73 dòng → 2026-10-13 | 70 dòng → 2026-10-13 |
| Giá đơn vị cuối | **9.790,8754** (= −2,091%) | **9.380,1371** (= −6,199%) |
| md5 | `141f8bb35c07aed7adbbfcf193f8e9f7` | `379315ab2f87d4526b3cb33d4b58049b` |
| Chốt lần hai | rc=2 NothingToSeal (nêu đúng md5) | rc=2 |
| Đối chiếu chỉ-đọc | rc=0, khớp | rc=0, khớp |

Không có `--force`. md5 thật sẽ KHÁC nếu chốt sau 10-14 (thêm dòng).

## D. Cơ chế đính chính (`fund_restatement.py`) — chạy trên A+B (dry-run)

`D_impact/impact_{SpaceX,ZaloPay}_AB.{txt,json}`. "Số chính" = NAV cuối kỳ + tỉ suất các kỳ báo cáo đó in;
"theo ngày" = NAV/tỉ suất ngày trong kỳ.

| Báo cáo đã gửi | TK | Số chính | Bậc | Theo ngày | Bậc | Đã xem tay (lượt này) |
|---|---|---:|:-:|---:|:-:|---|
| SpaceX_weekly_report_2026-07-03 | SpaceX | 0 | 0 | 0,4453 | 2 | không in NAV/tỉ suất ngày 07-02 ⇒ không có số nào sai |
| SpaceX_ZaloPay_monthly_report_2026-07 | SpaceX | 0 | 0 | 0,4453 | 2 | in biến động năm hoá SpaceX **17,3%**; tính lại **17,4%** (17,27 → 17,38) ⇒ lệch 0,11 ⇒ **bậc 2: một dòng ghi chú ở báo cáo kế tiếp** |
| SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07 | cả hai | 0 | 0 | 0,9735 / 2,6914 | 3 | báo cáo ĐÃ in NAV 06/08 tự dựng lại; lệch backfill 26 đ / 32 đ ⇒ thực chất **bậc 1** |
| SpaceX_ZaloPay_monthly_report_2026-08 | cả hai | 0 | 0 | 0,9735 / 2,6914 | 3 | không in NAV 06/08; **§4 in biến động năm hoá SpaceX 12,37% / ZaloPay 25,58% ("mẫu có gap", có cảnh báo trong báo cáo)**; trên chuỗi đủ 21 phiên sau khi chèn 08-06: **12,80% (+0,43) / 18,27% (−7,31)** ⇒ ZaloPay vượt 0,5 ⇒ **user quyết** |
| SpaceX_monthly_report_2026-08 | SpaceX | 0 | 0 | 0,9735 | 3 | in cùng số 12,37% (dòng 26, 122) ⇒ +0,43 ⇒ bậc 2 |
| ZaloPay_monthly_report_2026-08 | ZaloPay | 0 | 0 | 2,6914 | 3 | in cùng số 25,58% "mẫu ~16 ngày" (dòng 34, 130) ⇒ −7,31 ⇒ vượt 0,5 ⇒ **user quyết** |

SpaceX 5/62 báo cáo bị ảnh hưởng, ZaloPay 3/60 (2 file chung). **Không báo cáo nào đổi số chính; không
báo cáo nào bậc 3 theo số chính ⇒ hàng đợi "phát hành lại" rỗng.** Hàng đợi "cần user quyết": 8 dòng
(6 file) vì công cụ không biết báo cáo có in số ngày hay không — cột cuối là kết quả tôi tự mở từng file.
`error` cho dòng 07-02 đã post lên bus 09:14 ICT (trước khi vá).

**Biến động tháng 8 (số ĐÃ GỬI, có cảnh báo trong báo cáo)** — đo lại (σ mẫu × √252, mốc 31/07):
| | in trong báo cáo | dựng lại "như lúc viết" (thiếu 4–5 phiên) | nav_history hiện tại (thiếu 08-06) | sau khi chèn 08-06 |
|---|---:|---:|---:|---:|
| SpaceX | 12,37% | 12,04% | 11,98% | **12,80%** |
| ZaloPay | 25,58% | 24,78% | 21,35% | **18,27%** |

Tôi KHÔNG tái lập được đúng 12,37 / 25,58 (lệch 0,3–0,8 — không biết báo cáo dùng mốc/khoảng nào), nên
độ lệch nêu trên là so với số IN. Phần lớn độ lệch ZaloPay (25,58 → 21,35) đã có sẵn từ khi các dòng
07/10/25/27-08 được vá (09-13), không do thay đổi này; chèn 08-06 đưa nốt về 18,27. Sụt giảm tối đa
không đổi (−1,67% / −3,59%). Đã post `error` riêng cho số này (lượt 2).

## E. G1 — selfcheck khép kín
- `nav_unit_ledger_selfcheck.py` A2: thay dữ liệu sống bằng fixture đóng băng
  `bin/fixtures/nav_unit_ledger_asof_20261013/` + neo số công bố asof 10-13. **Số assertion đổi:
  4716↔4736↔4754 (trôi theo dữ liệu) → 4758 cố định.**
- `nav_jump_flow_gate_selfcheck.py` N11: `load_inception` trỏ vào fixture. Vẫn 25 ca.

## Nghiệm thu
1. **Số công bố** (`acceptance/TABLE_1_published_numbers.txt`): dữ liệu thật + code master = bản sao
   chưa sửa + code nhánh = bản sao đã áp A+B, cả 18 số (2 TK × 3 ngày × từ đầu/MTD/WTD). Δ = 0,000 mọi ô.
   SpaceX 10-13: −2,091 / −0,256 / −0,771; ZaloPay 10-13: −6,199 / −3,342 / −1,359. Số đổi do A+B chỉ ở
   4 ngày asof (07-02, 07-03, 08-06, 08-07 — `acceptance/all_dates_dev_AB.txt`).
2. **Bảng D**: trên.
3. **Seal**: trên; giá đơn vị cuối khớp `nav_period_returns` (9.790,8754 / 9.380,1371).
4. **Selfcheck** (`acceptance/selfcheck_3tz.txt`; chạy từ `/tmp`, `WC_ROOT` trỏ sandbox RỖNG không có
   `data/`), rc=0 ở cả 4 môi trường (gỡ TZ · America/New_York · Pacific/Kiritimati · Asia/Ho_Chi_Minh):
   `nav_ledger_vault_selfcheck` 183 · `fund_restatement_selfcheck` 118 · `nav_unit_ledger_selfcheck`
   4758 · `nav_jump_flow_gate_selfcheck` 25 ca · `daily_nav_snapshot_from_raw_selfcheck` 83.
   Lân cận (nhánh = master): `cash_identity_selfcheck` 348, `nav_corpaction_gate_e2e` 68,
   `corpaction_error` PASS; ba cái cần `data/` (`nav_period_returns --selfcheck` 9,
   `nav_cum_dividend` 38, `discretionary_margin_gate` 150) PASS trên bản sao.
   **Mutant** (`mutants.py`, `mutants_final.txt`): 78 cái — lần đầu 69 chết / **9 sống**
   (`mutants_run1.txt`): L2 không kiểm seq manifest · L28 đối chiếu chỉ-đọc không báo lệch dòng · L33
   "hôm nay" theo TZ máy (test cũ giả lập sai) · L36 restate quên lời nhận cũ · F5 số chính bỏ lệch NAV ·
   F12 dòng chèn không gọi người · F31 changed_rows chỉ so cột nav · F32 nav_history ngày lộn xộn · F34
   xoá hai lần. Đã thêm 10 assertion ⇒ **78/78 chết, 0 sống**. Lưu ý F32: chỉ chết nhờ khớp CÂU thông
   điệp — tầng dưới (`account_cash_flows`) cũng chặn cùng ca, tức là kiểm tra trùng lớp.

## Thao tác dữ liệu thật — thứ tự cho Mike (sau arch-review + merge + user duyệt)
Chạy ban ngày, tránh giờ `daily_nav_snapshot` ghi nav_history (19:05–19:15, 20:15, 23:30).
1. Sao lưu `nav_history_{SpaceX,ZaloPay}.csv`, `cash_identity_acks.json`.
2. Đo lại tác động trên dữ liệu lúc đó (md5 nav_history đã đổi vì có dòng mới; file đính chính vẫn dùng
   được): `fund_restatement.py impact --account SpaceX --correction <đây>/corrections/correction_SpaceX_AB.json --out /tmp/impact_SpaceX.json` (rồi ZaloPay).
3. Trình user bảng D + quyết định ghi chú (đề xuất: một dòng ở báo cáo kế tiếp, không phát hành lại).
4. `fund_restatement.py apply --account SpaceX --nav-dir data/execution_logs --correction … --impact-report /tmp/impact_SpaceX.json --approved-by "user <ngày>" --real-data` (rồi ZaloPay).
5. NGAY SAU bước 4: đổi khoá lời xác nhận SpaceX 07-02→07-03 trong `data/cash_identity_acks.json`
   (`from` → `2026-07-02T14:45:00`; mẫu: `corrections/cash_identity_acks_PROPOSED.json` — so lại với file
   lúc đó, đừng chép đè nếu đã có lời xác nhận mới).
6. Kiểm: `nav_period_returns.py` asof 10-09/10-12/10-13 không đổi; `cash_identity.py --json` 0 nghi vấn.
7. `nav_unit_ledger.py --account SpaceX --seal --real-data --accept-preclose 2026-08-24="<lý do ở C_seal/log.txt>"` (rồi ZaloPay).
8. `nav_unit_ledger.py --account <TK> --ledger-dir data/execution_logs` ⇒ rc=0 "khớp chuỗi dựng lại".
9. Áp hai file `kb/data_registry/trading-bot/*.proposed` + cập nhật mục bước 3 ở policy.

## Giả định tự đặt
- `balance_ts` của dòng SpaceX 07-02 sau sửa = `14:45:00` là mốc QUY ƯỚC "số dư tại giờ đóng cửa",
  không phải giờ chụp thật (phải vượt qua cú khớp 09:46:55, nếu không đẳng thức tiền đếm lô VGC hai lần).
- Sửa 07-02 chỉ phần CHẮC CHẮN 4.429.292 đ; 539.935 đ còn lại là phần dư user đã xác nhận không phải nạp/rút.
- VHM 08-06 = 77.100 lấy từ BQ `Close` (từ 08-07 `Price` = `Close`); không có nguồn giá thứ hai độc lập ngoài BQ.
- Bậc xếp theo số LỚN NHẤT trong (lệch NAV %, lệch tỉ suất điểm %) của từng báo cáo; đúng biên 0,05 ⇒ bậc 2, đúng 0,5 ⇒ bậc 2.
- Chốt tới HÔM QUA (ICT), không chốt hôm nay.

## Làm khác dispatch
- Backfill 08-06 đưa vào dạng lệnh CHÈN của `fund_restatement.py` (có nhật ký + ràng md5) thay vì để Mike
  chạy `--from-raw` trên dữ liệu thật; số do chính `--from-raw` sinh trên bản sao.
- Thêm `--raw-price-override` vào `daily_nav_snapshot.py` (ngoài danh sách) — không có thì B không làm được.
- K3 không thêm vào `assign_flow` (đã có ở master); thêm ở cổng chốt.
- 08-24 không "đính chính" mà nhận tường minh có bằng chứng.
- Không cần `SKIP=tz-anchor-gate`: cổng qua bình thường; diff không thêm `now()`/`today()` trần.

## Chưa làm
- Cổng công bố (`report_delivery_gate`) chưa đối chiếu sổ đã chốt; chưa có cron chốt hằng ngày.
- `fund_restatement` chỉ tìm NAV cũ trích NGUYÊN SỐ trong báo cáo; chỉ số suy diễn (biến động, drawdown)
  phải người xem — ca 17,3% → 17,4% (tháng 7) và 25,58% → 18,27% (tháng 8) là tôi tính tay, công cụ chỉ gắn cờ.
- Chưa có file `.proposed` cho policy (chỉ registry).
- Ba selfcheck lân cận vẫn đọc `data/` (ngoài G1).
- K1 chỉ ghi chú, không dựng dòng 07-01.
