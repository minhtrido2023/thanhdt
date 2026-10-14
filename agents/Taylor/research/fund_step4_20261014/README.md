# Quỹ mở — bước 4/4, phần 1: nghiên cứu + đặc tả (job `Taylor_20261014_020336`)

Chỉ đọc dữ liệu thật; không sửa `bin/`, `data/`, `kb/`. Số đo tới phiên **2026-10-13**.
Chính sách gốc: `kb/projects/fund-unit-performance-policy-20261010.md` (điểm 2, 3).

| File | Nội dung |
|---|---|
| `README.md` | bảng chỉ mục + kết quả (file này) |
| `SPEC.md` | đặc tả cài đặt (file, hàm, test, cổng fail-closed) + câu hỏi cần user quyết |
| `tr_fetch.py`, `tr_build.py` | Việc 1 — kéo dữ liệu, dựng VN-Index có cổ tức |
| `out_tr_build.txt`, `out_tr_checks.txt`, `out_tr_sensitivity.txt` | đầu ra Việc 1 |
| `vnindex_tr_daily_proto.csv`, `vnindex_tr_summary.json` | chuỗi ngày nguyên mẫu 2014 → 2026-10-13 |
| `zalopay_bot_series.py` | Việc 2 — nguyên mẫu chuỗi (b) |
| `out_zalopay_bot_series.txt`, `zalopay_bot_series.csv`, `zalopay_bot_summary.json` | đầu ra Việc 2 |
| `px_zalopay_20260625_20261013.csv` | giá thô BQ (`ticker.Price`) của mọi mã ZaloPay từng giữ |
| `web/` | factsheet HOSE-Index 03/2025 (PDF + text), danh sách sàn VNDirect (3 file JSON) |
| `proposed_kb/*.proposed` | đề xuất mục registry (chưa áp) |

Chạy lại:
```bash
cd mike/agents/Taylor/research/fund_step4_20261014
/home/trido/thanhdt/wc_venv/bin/python tr_fetch.py            # ~150 MB BQ, ghi /tmp/fund_step4_tr
/home/trido/thanhdt/wc_venv/bin/python tr_build.py            # bảng 1b + kỳ báo cáo
python3 zalopay_bot_series.py                                 # bảng 2c + đối soát (ghi /tmp/fund_step4_zp)
python3 zalopay_bot_series.py --asof 2026-10-09               # chân đối chứng: ra đúng số đã công bố
```

## Lỗi số đã công bố (đã post `error` lên bus TRƯỚC khi làm tiếp)

Báo cáo ZaloPay neo VN-Index "từ khi bắt đầu" tại đóng cửa **03/07** (1.862,08) và ghi "cùng mốc
thời điểm với NAV gốc". NAV gốc 987.865.567 lấy từ balances + positions `2026-07-06T21:45:43`, định
giá bằng giá **đóng cửa 06/07** (DGC 46.250 = `Price` 06/07; 03/07 là 47.700;
`data/account_seed_capital.json` ghi rõ `price_source … 2026-07-06`). Mốc chỉ số đúng = **1.843,50**.

| Báo cáo | VN-Index đã in | Đúng | Chênh lệch đã in | Đúng |
|---|---:|---:|---:|---:|
| Tuần 28/09–02/10 | −6,68% | −5,74% | +2,89pp | +1,95pp |
| Tuần 05/10–09/10 | −6,82% | −5,88% | +1,91pp | +0,97pp |
| Tháng 9, dòng Q3 | −5,02% | −4,06% | +2,06pp | +1,10pp |

Không ảnh hưởng: tỉ suất danh mục, mọi số SpaceX, MTD/WTD. Dòng "tháng 7" của báo cáo tháng 9 cũng
neo 03/07 — chưa tính lại. Bus: `Taylor/error zalopay-vnindex-benchmark-anchor-03-07-vs-06-07`.

## VIỆC 1 — VN-Index có cổ tức

### 1a. Nguồn đã thử

| Nguồn | Kết quả | Dùng được cho cron? |
|---|---|---|
| HOSE — chỉ số tổng thu nhập chính thức | Factsheet HOSE-Index 03/2025 (`web/hose_factsheet_202503.txt`): "Availability: Price and Total Return" cho **VNAllshare, VN30, VNMidcap, VN100, VNSmallcap**, TRI tính cuối ngày. **VN-Index KHÔNG có bản TRI** (chỉ xuất hiện như dòng so sánh) | Không có chuỗi cho đúng mốc đang dùng |
| DNSE `services.entrade.com.vn/chart-api` | `VN30TRI`, `VN100TRI`, `VNALLSHARETRI`… ⇒ `invalid symbol`. `VNINDEX`, `VN30` (giá) có | Chỉ số giá: có. TRI: không |
| VNDirect `dchart-api` | các mã TRI trả rỗng | Không |
| FiinPro-X / FiinX | connector chưa được cấp quyền trong phiên này | **Chưa kiểm được** |
| Giấy phép dùng số TRI của HOSE | "HOSE-Index" là nhãn hiệu đăng ký; factsheet không nêu điều khoản cấp dữ liệu | **Chưa kiểm được** (cần Wendy nếu muốn mua/dùng) |
| Tự dựng từ `tav2_bq.corporate_action` + `ticker` | làm được, đã kiểm chứng chéo (dưới) | **Được chọn** |

Chọn tự dựng vì (i) không tồn tại TRI công bố cho VN-Index, (ii) đổi mốc sang VN30/VNAllshare TRI là
đổi chỉ số so sánh chứ không phải "thêm cổ tức", (iii) dữ liệu cần đã có sẵn và có feed hằng ngày.

### Công thức (ở `tr_build.py`)

`y_t = Σ_i OShares_{i,t-1} × DIV_{i,t} / Σ_i Price_{i,t-1} × OShares_{i,t-1}` trên rổ mã HOSE ngày t
(vốn hoá ĐẦY ĐỦ, không free-float — đúng cách VN-Index tính); `TR_t = TR_{t-1} × (VNINDEX_t/VNINDEX_{t-1} + k·y_t)`,
k = 1 (gộp) hoặc 0,95 (sau thuế TNCN 5%). Phần GIÁ lấy nguyên chỉ số chính thức; sai số của rổ/trọng
số chỉ đi vào số hạng cổ tức.

Rổ HOSE theo thời điểm = `listedDate`/`delistedDate` của VNDirect (441 mã HOSE) + sự kiện rời sàn
trong `corporate_action` (53 mã). `universe_pit` KHÔNG dùng: đó là rổ lọc thanh khoản, không phải
thành phần VN-Index. `ticker_prune` không dùng.

### Kiểm chứng chéo

| # | Kiểm | Kết quả |
|---|---|---|
| K1 | Số tiền cổ tức: phương pháp B không đọc `corporate_action` (`Close_t/Close_{t-1} − Price_t/Price_{t-1}`, bỏ mã-ngày gần sự kiện phát hành) so với A trên CÙNG phạm vi | 2017–2026 lệch −0,05 … +0,08 điểm %/năm; 2015 −0,37; 2016 −0,11 |
| K2 | Rổ + trọng số: chỉ số GIÁ tổng hợp từ rổ so với VN-Index chính thức | 2020–2025 lệch ≤ 0,20 điểm %/năm; 2019 0,72; 2018 2,09; **2014–2016 lệch 1,6–4,0 ⇒ rổ kém tin** |
| K3 | Chỉ số giá BQ vs DNSE, 3.151 phiên từ 2014 | 59 phiên lệch > 0,05%; lớn nhất **2025-04-09: BQ 1.132,79 (lặp giá 08/04) vs DNSE 1.094,30**. 4 mốc kỳ báo cáo (01/07, 06/07, 30/09, 09/10 → 13/10) khớp tới 0,001 điểm % |
| K4 | Độ nhạy (`out_tr_sensitivity.txt`) | mọi mã 3 sàn thay vì HOSE: +0,07 … +0,37 điểm %/năm; số CP trễ thêm 1 quý: +0,00 … +0,19; danh sách HOSE hôm nay không theo thời điểm: 2024 lệch +0,40 |
| — | So với TRI công bố | **Chưa kiểm được** — không lấy được chuỗi TRI nào của HOSE |

K1 mới chỉ khẳng định TỔNG ròng khớp: ở mức mã-ngày còn 1.245 mã-ngày (2020+) B thấy chênh > 0,5% mà
A không có dòng DIV — chưa điều tra từng ca (nghi `Price` kẹt ngày GDKHQ tạo cặp dương/âm bù nhau).

### 1b. Chênh lệch cổ tức theo năm (điểm %; `out_tr_build.txt`)

| Năm | VN-Index giá | Cổ tức A | Cổ tức B | Có cổ tức (gộp) | Chênh gộp | Chênh sau thuế 5% | Lệch K2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2014 | 8,12 | 4,01 | 3,39 | 12,57 | 4,45 | 4,22 | −1,74 |
| 2015 | 6,12 | 3,68 | 2,63 | 10,09 | 3,97 | 3,77 | 1,55 |
| 2016 | 14,82 | 3,36 | 2,43 | 18,75 | 3,93 | 3,73 | −3,96 |
| 2017 | 48,03 | 2,94 | 2,79 | 52,45 | 4,41 | 4,19 | −0,79 |
| 2018 | −9,32 | 1,93 | 1,76 | −7,55 | 1,77 | 1,68 | 2,09 |
| 2019 | 7,67 | 1,96 | 1,92 | 9,79 | 2,13 | 2,02 | 0,72 |
| 2020 | 14,87 | 1,84 | 1,61 | 17,01 | 2,14 | 2,04 | 0,14 |
| 2021 | 35,73 | 1,22 | 0,95 | 37,39 | 1,66 | 1,58 | 0,19 |
| 2022 | −32,78 | 1,50 | 1,37 | −31,76 | 1,02 | 0,97 | 0,20 |
| 2023 | 12,20 | 1,68 | 1,53 | 14,10 | 1,90 | 1,81 | 0,11 |
| 2024 | 12,11 | 1,87 | 1,49 | 14,23 | 2,12 | 2,01 | 0,15 |
| 2025 | 40,87 | 1,62 | 1,51 | 43,17 | 2,30 | 2,18 | 0,01 |
| 2026 (→13/10) | −3,65 | 1,65 | 1,46 | −2,04 | 1,60 | 1,52 | 0,31 |

"Cổ tức B" ở bảng này là B trên phạm vi HẸP hơn (bỏ mã-ngày gần phát hành) nên thấp hơn A có hệ
thống — phép so cùng phạm vi là K1. 2014–2017 chỉ nên đọc là "khoảng 3–4 điểm %/năm, kém chắc".
2018–2025: **1,2–2,0 điểm % cổ tức/năm**, chênh tỉ suất gộp 1,0–2,3.

### Kỳ báo cáo và tác động lên kết luận "hơn/kém VN-Index"

| Kỳ | VN-Index giá | Có cổ tức gộp | Sau thuế 5% | Chênh |
|---|---:|---:|---:|---:|
| SpaceX 01/07 → 13/10 | −7,92% | −7,28% | −7,31% | +0,64 / +0,61 |
| ZaloPay 06/07 → 13/10 | −6,73% | −6,09% | −6,12% | +0,65 / +0,61 |
| MTD 30/09 → 13/10 | −2,78% | −2,74% | −2,74% | +0,04 |
| WTD 09/10 → 13/10 | −0,90% | −0,90% | −0,90% | 0,00 |

| Danh mục "từ khi bắt đầu" | Danh mục | so chỉ số giá | so chỉ số có cổ tức (gộp) |
|---|---:|---:|---:|
| SpaceX tới 09/10 (đã công bố +5,75pp) | −1,33% | +5,75pp | **+5,10pp** |
| SpaceX tới 13/10 | −2,09% | +5,82pp | +5,19pp |
| ZaloPay (a) tới 09/10 (đã công bố +1,91pp, mốc sai) | −4,91% | +0,97pp (mốc đúng) | **+0,32pp** |
| ZaloPay (a) tới 13/10 | −6,20% | +0,53pp | **−0,11pp (đảo dấu)** |
| ZaloPay (b) tới 13/10 | −0,79% | +5,94pp | +5,30pp |

Kỳ tuần/tháng gần như không đổi; kỳ "từ khi bắt đầu" giảm ~0,64 điểm % (mùa chốt quyền tháng 7–9:
MBB, GAS, SAB, VCB, CTG, BID, DGC đóng góp lớn nhất). Sai số của con số 0,64: khoảng ±0,03–0,13
(K1/K4).

### Giới hạn

- Không có TRI công bố để so trực tiếp; mọi kiểm chứng là chéo-nội-bộ giữa hai phép điều chỉnh độc lập.
- Trọng số dùng `OShares` trễ theo quý (không trừ cổ phiếu quỹ); rổ thiếu 47/406 mã HOSE nhỏ không
  có trong bảng `ticker`.
- Tái đầu tư tại ngày GDKHQ theo quy ước chỉ số; tiền thật về sau 2–6 tuần.
- Bảng sàn của VNDirect là API công khai không cam kết; mã đã rời HOSE có ngày vào sàn giả định ở 43/53 mã.
- Dòng DIV vào `corporate_action` muộn hơn ngày GDKHQ ⇒ số ngày gần nhất có thể bị sửa lùi.

## VIỆC 2 — Chuỗi ZaloPay "phần bot quản lý"

### 2a. Phạm vi "ngoài bot" theo ngày (từ `dnse_raw_*`, lọc `account_no` ở dòng đầu)

- **DGC 10.000 cp, không đổi một cổ nào từ 06/07 tới 13/10** — là vị thế DUY NHẤT ngoài bot. Giá trị
  462,5tr (46,8% NAV) ngày 06/07 → 329,0tr (35,5%) ngày 13/10.
- 6 mã legacy còn lại (MSH, TCM, TLG, VHC, VIB, VPB) được giao cho bot từ 06/07 (ghi chú account) và
  bot bán dần: MSH 07/07, TLG 08/07, TCM 09/07, VHC 10/07, VIB 13/07, VPB rải tới 02/10.
- **PNJ** có trong `excluded_tickers` (cả hai tài khoản, từ 30/09) nhưng là lệnh cấm MUA, vị thế 0 ⇒
  không ảnh hưởng chuỗi.
- **TV1, DRI** là mã discretionary nhưng do bot đặt lệnh, tính trên `active_nav`, có ở cả SpaceX ⇒
  nguyên mẫu để TRONG chuỗi (b).
- Không vị thế nào đổi phạm vi giữa chừng. Sự kiện duy nhất chạm ranh giới: **cổ tức DGC 8.000 đ/cp**
  (GDKHQ 14/09, chi trả 25/09): phải thu 80.000.000 ghi 11/09 19:07; về tiền giữa 25/09 04:51 và 19:07.

### 2b. Cách tính (ở `zalopay_bot_series.py`)

`NAV_b = NAV_a − KL_DGC × Price − cổ tức DGC phải thu (gộp, từ ngày GDKHQ tới trước ngày tiền về)`.
Tiền mặt, Trứng vàng, nợ thuộc trọn chuỗi (b). Cổ tức DGC về tiền = dòng VÀO chuỗi (b) **76.000.000**
(ròng) ngày 25/09; 4.000.000 thuế là chi phí của phần ngoài bot. Tỉ suất = `nav_unit_ledger.build_ledger`
(import chỉ đọc) trên bản sao ở `/tmp/fund_step4_zp`. Mốc (b): 525.365.567 đ ngày 06/07.

### 2c. Kết quả tới 13/10 (tỉ suất gia quyền thời gian)

| Kỳ | ZaloPay (a) | ZaloPay (b) | SpaceX cùng cửa sổ |
|---|---:|---:|---:|
| Từ đầu (06/07 → 13/10) | −6,199% | **−0,790%** | −0,385% |
| MTD (30/09 → 13/10) | −3,342% | −0,173% | −0,256% |
| WTD (09/10 → 13/10) | −1,359% | −0,626% | −0,771% |
| Tháng 7 (06/07 → 31/07) | −10,025% | −5,242% | −4,521% |
| Tháng 8 | +7,148% | +4,929% | +5,028% |
| Tháng 9 | +0,662% | −0,048% | −0,408% |

SpaceX "từ đầu" của chính nó (01/07) là −2,091%. Lãi/lỗ VND cả kỳ: (a) −61.234.124 = (b) −3.734.124
+ ngoài bot −57.500.000 (DGC −133,5tr giá + 80tr cổ tức − 4tr thuế). Gần như toàn bộ khoản kém của
ZaloPay so với SpaceX là DGC; phần bot lệch SpaceX −0,4 điểm %, dồn ở tháng 7 (−0,7) — nguyên nhân
chưa phân rã (tháng đó bot còn giữ và bán dần 6 mã legacy; đây là quan sát, chưa phải kết luận).

Chân đối chứng `--asof 2026-10-09`: (a) −4,907% / MTD −2,010%, SpaceX MTD +0,519% — đúng số đã công bố.

Độ nhạy: giờ tiền cổ tức về 25/09 không đo được — trước đóng cửa cho −0,790%, sau đóng cửa −0,707%.
Loại thêm TV1/DRI ("chỉ V2.4", dòng tiền xấp xỉ bằng giá đóng cửa): −1,381%. Loại cả 6 mã legacy tới
khi bán: +1,857% nhưng **vô nghĩa** — mốc chuỗi còn 4,9tr tiền mặt, tỉ suất mấy phiên đầu chạy trên
mẫu số gần 0.

### Đối soát

1. `NAV_a = NAV_b + ngoài bot`: lệch 0 đ trên 68/68 ngày (đúng theo cách dựng).
2. Dựng ngược từ dưới lên, không dùng cột `nav` (Σ mã trong bot × `Price` BQ + tiền + Trứng vàng − nợ −
   phải thu DGC): **54/68 ngày lệch đúng 0 đ**; 4 ngày lệch > 0,05% NAV, không ngày nào do DGC:
   05/08 −45,9tr (VHM được ghi KL mới tối trước GDKHQ; nav_history định giá đúng hệ), 27/07 −20,0tr
   (NAV chụp sáng 28/07, vị thế lệch 9,8 giờ), 23/09 −8,7tr (VPB, cùng kiểu VHM; dòng ước tính),
   27/08 −0,6tr (dòng ước tính). 10 ngày còn lại lệch ≤ 414.000 đ.
3. Lãi/lỗ cộng được: lệch 0 đ.

Cạm bẫy đã dính khi dựng: một mã nằm ở NHIỀU lô trong `positions` (khác `loanPackageId`) — đọc bằng
dict ghi đè làm thiếu 24,4tr (MBB/BID/VCB, 11/08 → 28/09). Phải CỘNG theo mã.

### 2d. Chưa biết / cần user quyết → `SPEC.md` mục "Câu hỏi"
