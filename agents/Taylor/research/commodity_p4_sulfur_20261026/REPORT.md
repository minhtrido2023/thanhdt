# REPORT — P4 (sunsirs) + lưu huỳnh (TE) → KQKD quý (job Taylor_20261026_160657, 2026-10-26)

Chỉ nghiên cứu (PAPER-ONLY). Không wire, không đổi production, không ghi BQ (chỉ đọc). Mọi số đo trong phiên này;
file nguồn ghi cạnh từng mục. Danh sách trial B2/B3 khai trước khi chạy: `TRIALS_B2B3.md` md5 `065ea443903bee1ec4b57a97232182f9`.

⚠️ **WARNING pháp lý (DGC):** đang trong vụ án hình sự (lãnh đạo bị khởi tố), cổ phiếu ở diện hạn chế giao dịch HOSE,
BCTC 2025 có ý kiến ngoại trừ. Phân tích dưới đây là phân tích số liệu bình thường (chỉ đạo user 27/9).

## Kết luận
1. **P4 sunsirs là chuỗi P4 thật, dùng được từ 2018.** Mức 2026 khoảng 28k CNY/t, khớp `data/phosphorus_weekly.csv`
   (125 điểm từ 2026-03, chênh trung vị 0,0%, p95 0,11%). Chuỗi này thay được TE `phosphorus`, vốn là quặng.
2. **Giá P4 trung bình quý từng là nowcast KQKD của DGC/PAT** (IC 0,46–0,50, N = 30 quý). Nhưng mức này chủ yếu
   đến từ đợt sốc 2021–22, và không qua Bonferroni. Bỏ 2021Q3–2022Q4 thì IC còn 0,23; từ 2024 trở đi IC là −0,21.
   **Quan hệ giữa giá P4 và LN của DGC đã gãy từ 2024.**
3. **Lưu huỳnh không đo được như một chi phí ở cấp nhóm** (DDV/LAS/CSV). Giá lưu huỳnh đi cùng nhịp chu kỳ phân bón
   nên IC dương. Chỉ LAS có dấu âm như kỳ vọng (mô tả, post-hoc).
4. **Không có ứng viên giao dịch nào.** Đã chạy 4 trial mới, tổng tích luỹ là 17. Không viết PREREG; DSR/PBO không áp dụng.
5. **DGC Q3/2026:** cả hai giá đều bất lợi so với Q2 (P4 −11,9%, lưu huỳnh +16,6%). Chiều này khớp với dự báo đã khoá
   (320 tỷ). Mô hình giá thuần (1.119 tỷ) không dùng được vì sai số 2026 quá lớn. Giá hàng hoá không cho thêm thông tin
   để chỉnh dự báo.

## B1 — Kiểm kê (`fetch.py`, `b1_inventory.py` → `b1_inventory.json`, `b1_*_by_year.csv`)
| | yellow_phosphorus | sulfur |
|---|---|---|
| Nguồn | `sunsirs` daily, CNY/T, prodetail-708 | `trading_economics` daily, CNY/T (CFD) |
| Số dòng / khoảng | 2.365 · 2012-06-11 → 2026-10-26 | 1.777 · 2020-01-02 → 2026-10-23 |
| Độ phủ | **Dày từ 2018** (≈65 phiên/quý). Trước 2018 chỉ 38 dòng, khe lớn nhất 191 ngày ⇒ bỏ | Đủ mọi quý 2020+, 0 khe >10 ngày |
| Đứng giá so phiên trước | 68,5% (549 giá trị khác nhau) | 53,3% |
| Nhảy bất thường | 2019-07: 14.800 → 25.500 → 15.867 trong 4 tuần, hợp lý nhưng chưa xác minh. 2021-09: đỉnh 60.000 (giai đoạn cắt điện Vân Nam, `ước lượng` theo hiểu biết thị trường) | 2022-07 −28%/phiên. 2026-06 ±15% |
| Cuối tuần | 27 dòng T7/CN trong năm 2026, lặp giá T6 ⇒ đã loại | không có |
| Trễ nạp | Quan sát 2026-10-26 được nạp 19:23 ICT cùng ngày (1 lần nạp) | Phiên cuối 10-23, nạp 10-25 |

**PIT:** không có vintage. `fetched_at` chỉ có một lần backfill (P4 toàn bộ 2026-10-26 12:23 UTC). Đây là **bản hiện
hành**, không chứng minh được là bản công bố đầu. Sunsirs/TE có thể đã sửa lịch sử mà không để lại dấu vết.

**Đối chiếu 5 bẫy TE:**
- (1) Mỗi mã chỉ có một nguồn, không có metric_key trùng nguồn khác. WB không có lưu huỳnh.
- (2) Mọi truy vấn dùng `source=` tường minh; không dùng `commodity_latest`.
- (3) Lưu huỳnh không có khe. P4 dày từ 2018; nhịp đứng giá cao (~tuần).
- (4) `fetched_at` không đo được trễ.
- (5) Bẫy tên mới: **TE `phosphorus` đã đổi `metric_key` thành `phosphate_rock_cny`**. Registry và
  `commodity_map_te.csv` vòng trước vẫn dùng tên cũ (stale). Chủ file registry là Winston.

**Giá trung bình quý (ngày làm việc):** P4 Q3/25 22.592 · Q2/26 31.105 · Q3/26 27.606 · Q4/26 (18 phiên) 28.112.
Lưu huỳnh Q3/25 2.521 · Q2/26 7.541 · Q3/26 8.794 · Q4/26 (17 phiên) 6.921 (`b2_qavg.csv`).

## B2 — Nowcast KQKD (`b2_nowcast.py` → `b2_results.json`, `b2_panel.csv`, `b2_desc_ticker.csv`)
**Thiết kế:**
- Biến giải thích: c_yoy = log(giá TB quý / Q−4).
- Biến đích lấy từ BCTC bản công bố đầu: rev_yoy, gpm_d, np_d = (LN0−LN4)/DT4.
- PIT: giữ cặp chỉ khi qend+2 < Release_Date.
- **N độc lập = số QUÝ**: lấy trung vị nhóm theo quý, vì tín hiệu giống nhau cho mọi mã trong cùng quý.
- Kiểm định: Spearman, CI90 bằng moving-block bootstrap (block 4 quý, 5.000 lần), p bằng circular-shift (2.000 lần).

| Trial | Nhóm | IC | CI90 MBB | p | N quý | IS (≤2022) / OOS |
|---|---|---|---|---|---|---|
| N1 P4 → rev_yoy | DGC, PAT | 0,496 | [0,12; 0,82] | 0,071 | 30 | 0,19 / 0,46 |
| N2 P4 → gpm_d | DGC, PAT | 0,461 | [0,01; 0,80] | 0,067 | 30 | 0,13 / 0,53 |
| N3 P4 → np_d | DGC, PAT | 0,491 | [0,06; 0,83] | 0,067 | 30 | 0,24 / 0,49 |
| N4 S → rev_yoy | DDV, LAS, CSV | 0,401 | [0,11; 0,71] | 0,18 | 23 | 0,00 / 0,45 |
| N5 S → gpm_d (kỳ vọng −) | DDV, LAS, CSV | −0,081 | [−0,54; 0,57] | 0,59 | 23 | −0,43 / 0,06 |
| N6 S → np_d (kỳ vọng −) | DDV, LAS, CSV | **+0,230** (sai dấu) | [−0,30; 0,80] | 0,049 | 23 | 0,45 / −0,02 |
| N7 DGC np_d ~ P4 + S (OLS) | DGC | b_P4 0,534 [−0,03; 0,77]; b_S −0,059 [−0,27; 0,12] | | | 22 | |
| N8 spread P4 − 9×quặng → DGC np_d | DGC | −0,136 | | 1,0 | 11 | spread tương quan mức với P4 0,995 |

Bonferroni ×8: p nhỏ nhất ≈ 0,39 ⇒ **không quan hệ nào qua cổng**.

**Độ nhạy của N3** (`b4_residuals.txt`): bỏ 2021Q3–2022Q4 thì IC 0,23 (N = 24). Riêng 2024Q1+ thì IC −0,21 (N = 10).

**Spread:** quặng (TE `phosphate_rock_cny`, từ 2022-08) gần như đứng giá. Repo không có dữ liệu điện và than cốc
CNY ⇒ spread chỉ là P4 đổi thang đo; không có thông tin mới.

**IC theo mã** (mô tả, không suy luận, `b2_desc_ticker.csv`):
- Lưu huỳnh → np_d: DPM 0,77 · DCM 0,56 · CSV 0,48 · DGC 0,47 · DDV 0,44 · NFC 0,38 · VAF 0,31 · **LAS −0,34** · BFC −0,04.
- ⇒ Lưu huỳnh là **proxy cho chu kỳ phân bón/hoá chất**, không phải chi phí đo được.
- LAS (supe lân nội địa, giá đầu ra cứng) là mã duy nhất có dấu chi phí. Đây là giả thuyết post-hoc, chưa kiểm.

## B3 — Trial tích luỹ
| Trial giao dịch mới | IC | p | Bonf ×17 |
|---|---|---|---|
| G1 P4 → ann (DGC, PAT) | 0,081 | 0,56 | 1 |
| G2 P4 → post60 | −0,020 | 0,92 | 1 |
| G3 S (×−1) → ann (DDV, LAS, CSV) | 0,059 | 0,78 | 1 |
| G4 S (×−1) → post60 | −0,208 | 0,38 | 1 |

**Đếm trial:**
- Trial giao dịch: **13 → 17**. p Bonferroni nhỏ nhất toàn bộ = 0,024 × 17 = 0,41, ở ô H-a 1,10 cũ.
- Trial nowcast: 8 trial mới, cộng thêm vào họ nowcast của vòng trước.

Không có ứng viên ⇒ **không viết PREREG**. DSR/PBO không áp dụng vì không có kết luận giao dịch. Kết quả giữ nguyên
kết luận vòng trước: thị trường định giá cùng nhịp với hàng hoá; phản ứng quanh ngày công bố không có edge.

## B4 — Giá Q3/2026 ⇒ KQKD Q3 DGC (`b4_dgc_q3.py` → `b4_dgc_q3.json`)
- **Giá:**
  - P4 TB Q3 là 27.606, +20,0% log YoY nhưng **−11,9% QoQ**.
  - Lưu huỳnh TB Q3 là 8.794 CNY/t, ×3,5 YoY (log 1,25, vượt mức lớn nhất trong mẫu fit 1,15) và **+16,6% QoQ**.
- **Mô hình giá thuần** (fit ≤2026Q2):

  | Mô hình | LNST Q3 (tỷ) | Dải 80% |
  |---|---|---|
  | M1 np_d ~ P4 | 1.119 | [442; 1.796] |
  | M2 + lưu huỳnh (ngoại suy) | 925 | |
  | M3 QoQ | 506 | [−552; 1.565] (b 0,088 ≈ 0) |

- **Vì sao bỏ các mô hình này:** phần dư của DGC ở 2026Q1 là −0,21 và ở 2026Q2 là **−0,32** (lớn nhất cả chuỗi).
  Q2/26 giá P4 +28% YoY mà LN lại −52% YoY. Động lực riêng của DGC đang lấn át giá: khai trường dừng nên phải mua quặng
  ngoài, sản lượng giảm, yếu tố pháp lý. Phần này đã ghi ở FORECAST.
- **Đối chiếu dự báo đã khoá** (`../dgc_q3_forecast_20261026/FORECAST.md`, md5 đọc lại `d6ea39f404e4058452532fec353732ad`
  khớp LOCK, không sửa):
  - Dự báo khoá: 320 tỷ, khoảng 50% [270; 370].
  - Hướng QoQ của cả hai giá đều bất lợi ⇒ **cùng chiều** với kịch bản LN dưới Q2.
  - FORECAST ước lưu huỳnh +26% QoQ (KSP Kuwait FOB USD). TE CNY đo được +16,6%. Hai chuỗi khác nhau, cùng chiều.
  - Không có cơ sở định lượng để dịch dự báo khoá.
- **Lưu ý BQ:** NP_P0 Q2/26 trong BQ là 380,1, còn báo chí ghi LNST mẹ 389. FORECAST đã ghi GPM_P0 2026 của BQ lệch
  báo chí ⇒ gpm_d của DGC 2026 trong panel không đáng tin.

## Self-check
- `selfcheck.txt`: tính tay DGC 2026Q2 từ `raw.parquet` + `ticker_financial`. cP4 = 0,280618 và np_d = −0,159604, khớp
  panel tới 1e-9 ⇒ **PASS**.
- Không có backtest NAV nên không áp dụng self-check 0 VND.

## Giới hạn
- **N nhỏ:** 30 quý cho P4, chủ yếu là DGC vì PAT chỉ có từ 2022. YoY chồng lấn nên N hiệu dụng < 30.
- **P4 TQ ≠ giá bán của DGC.** DGC bán P4 xuất khẩu (USD) và nhiều sản phẩm khác; chưa quy đổi CNY/VND.
- **Không PIT cho giá hàng hoá** (backfill một lần). `Release_Date` trong BQ được giả định là ngày công bố thật.
- **Thiếu dữ liệu chi phí:** điện, quặng VN; than cốc sunsirs chưa ghép ⇒ spread không làm được.

## Việc làm tiếp
1. Winston: cập nhật registry — thêm `yellow_phosphorus` (sunsirs) là chuỗi P4 CANONICAL từ 2018; ghi
   `phosphorus` → `phosphate_rock_cny` (đổi key); đề xuất sửa `commodity_map_te.csv` (DGC/PAT/LAS dòng `phosphorus`).
2. Display-only: thêm P4 sunsirs vào khối nowcast hàng hoá cho DGC/PAT, kèm cảnh báo "quan hệ gãy từ 2024".
3. Chấm FORECAST DGC Q3 khi công bố (27/10–14/11). Không dùng mô hình giá thuần.
4. Nếu muốn kiểm LAS (dấu chi phí lưu huỳnh): PREREG riêng, dữ liệu forward 2027. Hiện là ý post-hoc, không chạy thêm.
5. Spread P4: than cốc CNY đã có (`coke` sunsirs), chỉ thiếu giá điện công nghiệp TQ (Vân Nam/Quý Châu) → xin bq_admin nếu cần.

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/commodity_p4_sulfur_20261026
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY fetch.py && $PY b1_inventory.py && $PY b2_nowcast.py && $PY b4_dgc_q3.py   # seed 20261026
```
Dữ liệu cổ phiếu và BCTC lấy từ `data/bq_cache` (vintage 2026-10-23), dùng `common.py` của commodity_cycle_te_20261026.
Không dùng `ticker_prune` và `profit_*`.
