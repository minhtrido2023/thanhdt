# REPORT — Mã đầu ngành × nowcast ngành ("việc 5", job Taylor_20261119_090450, 19/11/2026)

Chỉ nghiên cứu. Không wire, không sửa production/KB chuẩn tắc. PREREG: `PREREG.md` md5 `4de8f3168eac5a84f4a25766ae4a0191`,
commit `f485ae696`, commit **trước** khi chạy `run.py`. Mọi số dưới đây đo trong phiên này (file nguồn ghi cạnh).

## 0. KẾT LUẬN

1. **Không có sleeve/book đầu ngành nào nên mở.** Kết quả không đi ngược phán quyết **LENS not BOOK** của 20 sector
   sweep (`kb/KNOWLEDGE.md` §7: 15 sweep gốc 30/06 + #16–#20 ngày 05–06/07, cả 20 cùng phán quyết). Bằng chứng ở đây
   chỉ có 4 họ × 35–36 quý. p chính xác nhỏ nhất đạt được là 1/30 = 0,033. Không ô nào qua Bonferroni ×38, và họ dầu
   khí cho dấu ngược.
2. **Giả thuyết "đầu ngành định giá nhanh hơn" và "KQKD đầu ngành bám hàng hoá sạch hơn" đều SAI dấu.**
   - KQKD đầu ngành bám hàng hoá *kém* hơn mã còn lại: IC 0,22 so với 0,45 (T1 ΔIC −0,23; IS −0,40, OOS +0,04, đổi dấu ⇒ không đạt).
   - Trong chính quý tín hiệu, mã còn lại chạy theo hàng hoá *mạnh* hơn đầu ngành (T4 −3,95pp).
   - Đầu ngành không đi trước.
3. **Cái có thật là đầu ngành *ít nhạy* với chu kỳ:** giữ biên khi pha xuống.
   - T2: khi c_yoy < 0, np_d đầu ngành − mã còn lại = **+2,0pp doanh thu**, CI90 [+0,5; +3,5].
   - Cùng dấu IS +2,5 / OOS +1,6; BH q 0,075 (p chính xác); không năm nào bị loại mà làm đảo dấu (LOYO).
   - Đạt cổng **DISPLAY** theo PREREG.
4. **Trên giá: spread "đầu ngành − mã còn lại" tiếp diễn 3 tháng theo dấu nowcast.**
   - T6 = −3,7pp/3M; T9 so với universe = −3,2pp/3M. Cả hai đạt mọi cổng PREREG: CI90, IS/OOS, BH q 0,075, chi phí,
     LOYO, capacity.
   - Theo pha: sau quý nowcast **âm**, đầu ngành thắng universe_pit **+4,3pp/3M** (76 họ-quý); sau quý **dương**, đầu
     ngành thua −1,8pp (62).
   - Placebo rổ ngẫu nhiên cùng tercile thanh khoản cho trung vị −0,3pp; kết quả thật ở phân vị 2% ⇒ là hiệu ứng "đầu
     ngành", không phải hiệu ứng "mã to".
   - **Nhưng:** chỉ đúng ở 3/4 họ (dầu khí +1,6pp, sai dấu); T9 chỉ vừa bằng giá trị lớn nhất của phân bố dịch vòng
     (0,0319 vs 0,0318); năm 2020 đóng góp lớn (+16,3pp, pha xuống); Bonferroni ×38 = 1.
   - ⇒ Đây là **ứng viên PREREG-5 dạng paper forward**, không phải tilt.
5. **Đề xuất (cần user/Mike duyệt):**
   - (a) DISPLAY: thêm 1 dòng "đầu ngành giữ biên pha xuống (+2pp DT)" vào khối nowcast hàng hoá.
   - (b) PREREG-5 forward cho T9, giữ đủ **4 họ** (không được bỏ dầu khí sau khi đã thấy kết quả), đo paper ≥ 8 quý.
   - (c) Không tilt, không sleeve, không đụng BAL/LAG/custom30V cho tới khi qua quant-skeptic và có kết quả forward.

## 1. Thiết kế (tóm PREREG)

**Họ và đầu ngành**
- Họ lấy từ bản đồ tier A đóng băng 26/10 (`commodity_map_te.csv`).
- Đầu ngành = **top-2 theo trung vị `Trading_Value` 60 phiên**, đo ở phiên trước ngày đầu quý, chỉ trong universe_pit tại
  ngày đó. Danh sách đổi theo quý.
- `Trading_Value` = Price thô × Volume thô (kiểm HPG 17/06/2022: tỷ số 1,0 qua ngày chia cổ tức CP) ⇒ định nghĩa đầu
  ngành không có hệ số corp-action nào. Lợi suất chỉ dùng `Close` điều chỉnh.
- Họ cần ≥ 3 mã hợp lệ. Chỉ 4/8 họ đạt điều kiện: cao su, dầu khí, đường, thép. Urê, DAP, BDI, container có ≤ 2 mã nên
  **bị loại về cấu trúc**.

**Thống kê**
- N = họ × quý = **138 đơn vị** (134 ở +3M), **36 quý** 2017Q4–2026Q3, 4 họ. Đường chỉ có 30 quý.
- N hiệu dụng gần với 36 quý vì các họ cùng quý tương quan.
- CI90: moving-block bootstrap, khối 4 quý.
- p: dịch vòng chung c_yoy. BH trên 9 trial.
- IS < 2023Q1 / OOS ≥ 2023Q1. Mọi họ chỉ có TE từ 2016-10, nên tách 2023 như b2.

**Đối chứng tái lập: PASS** (`run.log` dòng CONTROL)
- np_d khớp `b2_panel.csv`: 99,36% (777/777 dòng ghép).
- IC gộp tier A c_yoy→np_d tính lại: 0,467, trong khoảng 0,450 ± 0,02.

**Phần lặp lại phép thử cũ (nói thẳng):** T7–T9 (so với universe, có điều kiện theo dấu nowcast) về bản chất là họ
momentum hàng hoá → giá đã NO-GO 17/17. Kết quả khớp kỳ vọng ở T7: trong quý, đầu ngành không lệch universe
(−0,75pp, p 0,57). Phần mới thật sự là tương phản **đầu ngành − mã còn lại** (T1–T6).

## 2. Kết quả 9 trial (`results.json`, `results_exact.json`)

| # | Trial | Ước lượng | CI90 | p chính xác | BH q | IS / OOS | LOYO min/max | MDE | Đạt PREREG? |
|---|---|---|---|---|---|---|---|---|---|
| T1 | ΔIC KQKD (L − R) | −0,232 | [−0,46; −0,06] | 0,067 | 0,100 | −0,40 / +0,04 | −0,31 / −0,14 | 0,30 | ✗ (đổi dấu IS/OOS; q = 0,100 không < 0,10) |
| T2 | np_d L−R, pha xuống | **+0,0204** | [+0,005; +0,035] | 0,033 | 0,075 | +0,025 / +0,016 | +0,014 / +0,027 | 0,023 | **✓ DISPLAY** |
| T3 | np_d L−R, pha lên | −0,013 | [−0,053; +0,008] | 0,27 | 0,34 | −0,006 / −0,025 | −0,025 / +0,003 | 0,047 | ✗ |
| T4 | H0 (trong quý) vs R | −3,95pp | [−6,7; −2,3] | 0,033 | 0,075 | −5,4 / −2,0 | −4,7 / −3,2 | 3,4 | không giao dịch được |
| T5 | +1M vs R | −0,74pp | [−1,8; −0,1] | 0,40 | 0,45 | +0,3 / −2,1 | −1,0 / −0,5 | 1,3 | ✗ |
| T6 | +3M vs R | **−3,67pp** | [−5,4; −2,7] | 0,033 | 0,075 | −2,7 / −5,0 | −4,4 / −3,0 | 2,1 | ✓ trên giấy (nhưng không có chiều bán khống ⇒ xem §3) |
| T7 | H0 vs universe (LẶP) | −0,75pp | [−3,8; +0,6] | 0,57 | 0,57 | −1,7 / +0,5 | −1,4 / +0,2 | 3,3 | không giao dịch được |
| T8 | +1M vs universe (LẶP) | −1,54pp | [−3,0; −0,3] | 0,067 | 0,100 | −1,5 / −1,6 | −2,0 / −1,0 | 2,1 | ✗ (q = 0,100) |
| T9 | +3M vs universe (LẶP) | **−3,19pp** | [−5,6; −1,6] | 0,033 | 0,075 | −3,9 / −2,2 | −3,8 / −2,0 | 3,1 | ✓ trên giấy |

- Dấu âm ở T4–T9 nghĩa là đầu ngành chạy *ngược* chiều nowcast so với chân so sánh: kém hơn khi pha lên, hơn khi pha xuống.
- Bonferroni ×38 (tổng trial tích luỹ) = 1,0 cho **mọi** ô.
- p ở `run.py` (0,0005) là ảo, xem "Lệch PREREG" bên dưới.

**Tách pha** (`run.log`, mô tả; spread L − C, đơn vị là lợi suất):

| Horizon | So với | Pha lên (n = 62) | Pha xuống (n = 76) | Không điều kiện |
|---|---|---|---|---|
| Trong quý | R | −3,9pp | +4,0pp | +0,5pp |
| +3M | R | −2,5pp | +4,6pp | +1,5pp |
| +3M | universe | −1,8pp | +4,3pp | +1,6pp |

**Theo họ, +3M so với universe** (`results_exact.json` → `phase_by_family`):

| Họ | Pha lên | Pha xuống |
|---|---|---|
| Cao su | −3,1pp | +6,9pp |
| Thép | −5,2pp | +4,8pp |
| Đường | −3,3pp | +5,6pp |
| **Dầu khí** | **+3,7pp** | **+0,2pp** (ngược dấu) |

- LOFO T9: từ −2,5 đến −4,9pp. Không họ nào bị loại mà làm mất dấu.
- Bỏ HSG/NKG (BANNED) khỏi chân đầu ngành (`banned_check.py`): T9 −2,85pp (pha xuống +4,2pp), T6 −3,33pp.
- **T9 pha xuống theo năm** (spread L − U trung bình):

  | Năm | Spread | n |
  |---|---|---|
  | 2017 | −10,5pp | 2 |
  | 2018 | +8,7pp | 8 |
  | 2019 | −2,4pp | 10 |
  | 2020 | +16,3pp | 10 |
  | 2022 | +2,1pp | 7 |
  | 2023 | +4,7pp | 10 |
  | 2024 | −2,0pp | 10 |
  | 2025 | +4,8pp | 14 |
  | 2026 | +6,3pp | 4 |

  ⇒ Có 3/9 năm âm. 2020 (COVID) là năm đóng góp lớn nhất.

**Placebo** (rổ ngẫu nhiên cùng tercile GTGD60, ngoài họ, 200 lần):

| Trial | Thật | Trung vị placebo | P5–P95 placebo | Phân vị của số thật |
|---|---|---|---|---|
| T8 | −1,54 | −0,06 | [−1,15; +0,98] | 2% |
| T9 | −3,19 | −0,28 | [−2,24; +2,14] | 2% |

## 3. Diễn giải nhân quả

- **Đầu ngành = "beta thấp" với chu kỳ hàng hoá, cả ở KQKD lẫn ở giá.** Đó là cơ chế quy mô / giữ biên: hợp đồng dài
  hạn, đa dạng sản phẩm, chi phí thấp hơn.
- **Mã đi sau mới là nơi chu kỳ hiện rõ:** KQKD bám hàng hoá mạnh hơn (IC 0,45), giá chạy theo mạnh hơn trong quý, và
  spread so với đầu ngành còn tiếp diễn thêm 3 tháng.
- **Giả thuyết "đầu ngành định giá nhanh, mã sau bắt kịp" bị bác:** T4 sai dấu, T5 ≈ 0.
- **Giới hạn giao dịch:** VN không bán khống, nên spread T6 không giao dịch được dạng long-short. Dạng long-only khả thi
  duy nhất là T9 pha xuống: nắm 2 đầu ngành 3 tháng sau quý nowcast âm (+4,3pp so với universe). Khả thi về mặt thực
  thi, nhưng chính là kiểu "sổ theo ngành" mà 20 sweep đã kết luận LENS not BOOK.
- **Mâu thuẫn cần quant-skeptic soi:** H-a (26/10) thấy *tiếp diễn* nhẹ ở cấp họ (+5,8pp, p 0,13). Ở đây đầu ngành lại
  *đảo chiều* so với universe sau quý xấu. Hai kết quả tương thích nếu phần tiếp diễn nằm ở mã đi sau, nhưng điều này
  chưa được kiểm.

## 4. Capacity (`results.json` → `capacity`)

- Có 276 lượt đầu ngành-quý. **100%** có GTGD60 ≥ 0,15 tỷ/phiên (sổ ~1,5 tỷ NAV). **96,4%** có ≥ 5 tỷ/phiên (sổ 50 tỷ);
  95,8% nếu bỏ mã banned.
- Đầu ngành 2026Q3 (GTGD60, tỷ/phiên):

  | Họ | Mã 1 | Mã 2 |
  |---|---|---|
  | Cao su | GVR 91,3 | PHR 19,0 |
  | Dầu khí | PVS 113,8 | GAS 109,8 |
  | Đường | SBT 10,0 | QNS 5,7 |
  | Thép | HPG 579,9 | HSG 36,3 (**BANNED**) |

- Capacity không phải nút thắt. Nút thắt là N: khoảng 4 họ-quý mỗi quý, trung bình ~2 họ ở pha xuống.

## 5. Lệch PREREG (khai thật)

1. **p dịch vòng:** `run.py` rút 2.000 lần độ dời k từ khoảng [4, nq−4]. Khoảng này chỉ có **29 giá trị k khác nhau**
   ⇒ p báo 0,0005 là ảo. `exact_p.py` liệt kê đủ 29 k (cùng phép thử, bản chính xác): p sàn 1/30 = 0,033. Mọi kết luận
   GO/NO-GO ở trên dùng p chính xác. Kết quả: T1 và T8 rơi từ q 0,061 lên đúng 0,100, tức **không** còn < 0,10.
2. `run.py` lần chạy đầu crash ở bước placebo (lỗi căn chỉnh index; T1–T9 đã in ra, giống hệt lần chạy lại). Đã sửa và
   thêm bảng tách pha **mô tả**. Không đổi định nghĩa trial.
3. Phần thêm sau, đều mô tả, không tính trial: LOFO, tách pha theo họ, theo năm, bỏ mã BANNED.

## 6. Trả lời thẳng câu hỏi dispatch

**Có sleeve/tilt đầu ngành nào đáng đưa vào PREREG-5/DISPLAY?**
- DISPLAY: có, một dòng (T2).
- PREREG-5: một ứng viên paper forward (T9, pha xuống, đủ 4 họ). Kỳ vọng tiên nghiệm thấp, vì sàn p, Bonferroni ×38,
  dầu khí ngược dấu và 2020 chi phối.
- Sleeve/book: **không**. Phán quyết LENS not BOOK (20/20 sweep) vẫn đứng: nowcast ngành là kính đọc KQKD, và kính này
  chỉ thêm được một ý — mã đi sau mới là nơi chu kỳ thể hiện, đầu ngành là vùng trú pha xuống.

**Trial tích luỹ:** 17 (26/10) + 12 (A4, đã duyệt) + 9 (việc này) = **38**.

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/sector_leaders_nowcast_20261119
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY run.py          # đối chứng + 9 trial + placebo + capacity → results.json, panel_famq.csv, leaders_by_quarter.csv (~vài phút)
$PY exact_p.py      # p chính xác 29 độ dời, LOFO, pha theo họ → results_exact.json
$PY banned_check.py # T6/T9 bỏ HSG/NKG
```
Dữ liệu: `data/bq_cache` (vintage 2026-11-18), TE parquet 26/10. Không dùng `ticker_prune`, không dùng `profit_*`.

**Rủi ro tồn dư:**
- TE không có vintage.
- KQKD là "bản công bố đầu tiên" trong bản ingest hiện tại.
- Universe_pit được dùng cho cả hai chân.
- Placebo chỉ khớp theo tercile thanh khoản, không khớp beta.
