# Phân loại candidate LAG theo dạng phản ứng giá quanh công bố — có nên không?

**Job** `Taylor_20261022_053319` · 2026-10-22 · Taylor · READ-ONLY (không sửa production, không pin registry)
PREREG: `PREREG.md` md5 `0af5bd9d3627a3d7e571ee6cad590052` (ghi và khoá trước khi tính bất kỳ đặc trưng nào).
Script: `reaction_study.py` → `study_stdout.txt`, `filter_grid.csv`, `event_features.csv`; hậu kiểm `diag_avol.py` → `diag_avol_stdout.txt`.

## 0. Kết luận

**NO-GO cho giả thuyết phản ứng giá.** "Đã tăng hết / chưa phản ứng / tăng rồi giảm" không phân biệt được drift sau phiên chuẩn. Cả 3 đặc trưng giá (REACT, GAP, PRERUN), DIST52 và 4 lớp đều có CI95 cụm-mùa chứa 0. Dấu còn **ngược** giả thuyết: lớp UP_FULL drift 4,92%, cao hơn phần còn lại 4,46%. Δ +0,47pp, CI [−1,39; +2,70].

**Theo đúng luật PREREG thì nhãn tổng là INCONCLUSIVE.** Lý do duy nhất là một đặc trưng phụ, khối lượng bất thường ngày phản ứng (AVOL, họ (b)):
- Loại tercile AVOL thấp: Δ **−2,99pp**, CI [−4,62; −1,48]. Qua c1–c4: IS/OOS cùng dấu, bỏ-một-năm max −2,37pp, qua Holm.
- Trượt **c5**: nhóm bị loại vẫn lãi 2,34%, gấp khoảng 7 lần lãi nhàn rỗi pin1M 0,34%. Loại chúng ra để tiền nằm im là thua.
- Trượt **c6**: DSR 0,924 < 0,95.
- Hậu kiểm cho thấy đây chủ yếu là **proxy thanh khoản kém**. 48% nhóm có khối lượng ngày phản ứng = 0; chỉ 22% nằm trong universe_pit.
- Trong universe_pit (tập production thực sự giao dịch), Δ −1,73pp với CI [−4,08; +0,55]: **không có ý nghĩa**.

→ **Không wire bộ lọc nào, không chạy A/B NAV.** Tín hiệu duy nhất sống sót qua bỏ-một-năm là AVOL thấp, nhưng production đã chặn phần lớn nó bằng universe_pit + lọc ADV.

| Hạng mục | Kết quả | Nhãn |
|---|---|---|
| N sự kiện / mã / ngày công bố / **mùa (N độc lập)** | 5.361 / 789 / 572 / **51** | ĐO |
| Drift TB sau phiên chuẩn (Open e → Close e+25) | 4,551% (live W3·Luật A: 4,610%) | ĐO |
| Bộ lọc đặc trưng giá có CI95 loại trừ 0 | **0 / 12** | ĐO |
| AVOL thấp: Δ toàn bộ | −2,99pp [−4,62; −1,48] | ĐO |
| AVOL thấp: Δ trong universe_pit | −1,73pp [−4,08; +0,55] | ĐO (hậu kiểm) |
| AVOL thấp: DSR / PBO cả lưới | 0,924 / 0,048 | ĐO |
| Lãi nhàn rỗi pin1M trên kỳ nắm 25 phiên | 0,318% TB (dep1m PIT) | ĐO |

## 1. Thiết kế (theo PREREG)
- **Tập sự kiện** = `lag_entry_window_width_20261021/exp_window_events.csv`, gồm 5.361 dòng theo luật engine LAG. Entry e = Release+5 phiên, thoát Close e+25 (luật hiện hành).
- **Đặc trưng** đo tại Close e−1 (PIT, mua ở Open e). Giá lấy từ `tav2_bq.ticker`, đã điều chỉnh. VNINDEX lấy từ hàng `ticker='VNINDEX'` gốc, không dùng cột mirror vì cột đó là TRAP.
  - REACT = lợi suất vượt VNI từ d0−1 tới e−1
  - GAP = Open d0 / Close d0−1
  - AVOL = khối lượng d0 / trung bình 20 phiên trước
  - PRERUN = lợi suất vượt d0−21 → d0−1
  - DIST52 = khoảng cách tới đỉnh High 250 phiên
  - 4 lớp UP_FULL / UP_THEN_DOWN / DOWN / FLAT, ngưỡng 5%
- **Ngưỡng**: tercile cắt trên IS (2014–19), áp nguyên cho OOS.
- **14 trials**, toàn bộ dạng loại bỏ.
- **Thống kê**: bootstrap cụm theo mùa (năm-quý release), 2.000 lần, seed 20261022; Holm; DSR; PBO CSCV S=10.
- **Môi trường**: threads=1. Giá lấy qua `BQ_LOCAL_CACHE` (snapshot đêm 10-21).

## 2. Mô tả — drift TB Y (%) theo tercile IS — ĐO
| Đặc trưng | T1 (thấp) | T2 | T3 (cao) |
|---|---:|---:|---:|
| REACT | 4,67 (n=1.881) | 4,59 (1.681) | 4,40 (1.799) |
| GAP | 4,68 (1.414) | — (0, xem Deviation 1) | 4,51 (3.947) |
| AVOL | **2,34** (1.393) | 5,76 (1.925) | 4,91 (1.946) |
| PRERUN | 4,86 (2.010) | 4,26 (1.665) | 4,47 (1.686) |
| DIST52 | 4,72 (2.212) | 4,17 (1.689) | 4,75 (1.460) |

| Lớp | n | Y | Y_live | Y vượt VNI |
|---|---:|---:|---:|---:|
| UP_FULL (đã tăng ≥5%) | 1.093 | 4,92 | 5,07 | 3,08 |
| UP_THEN_DOWN | 273 | 5,33 | 5,39 | 3,94 |
| DOWN (≤−5%) | 784 | 4,38 | 4,62 | 1,21 |
| FLAT | 3.211 | 4,40 | 4,38 | 2,28 |

REACT có độ dốc nhẹ theo hướng giả thuyết (4,67 → 4,40), nhưng nhỏ so với nhiễu: CI của Δ rộng khoảng ±1,3pp.

## 3. Bảng chính — Δ = mean(Y | loại) − mean(Y | giữ), pp, CI95 cụm-mùa — ĐO
| Bộ lọc | % loại | Δ | CI95 | p | ΔIS | ΔOOS | LOYO max | c1 | c2 | c3 | Holm | c5 |
|---|---:|---:|---|---:|---:|---:|---:|:-:|:-:|:-:|:-:|:-:|
| REACT loại thấp | 35,1 | +0,18 | [−0,97; +1,46] | 0,76 | +0,72 | −0,17 | +0,45 | ✗ | ✗ | ✗ | ✗ | ✗ |
| REACT loại cao | 33,6 | −0,23 | [−1,60; +1,29] | 0,74 | −1,61 | +0,49 | +0,09 | ✗ | ✗ | ✗ | ✗ | ✗ |
| GAP loại ≤0 | 67,1 | −1,39 | [−3,17; +0,08] | 0,07 | +0,23 | −2,00 | −0,80 | ✗ | ✗ | ✓ | ✗ | ✗ |
| GAP loại ≥0 | 73,6 | −0,17 | [−1,34; +1,07] | 0,79 | −0,36 | −0,13 | +0,31 | ✗ | ✓ | ✗ | ✗ | ✗ |
| **AVOL loại thấp** | 26,0 | **−2,99** | **[−4,62; −1,48]** | 0,000 | −1,83 | −3,49 | −2,37 | ✓ | ✓ | ✓ | ✓ | **✗** |
| AVOL loại cao | 36,3 | +0,56 | [−0,84; +1,96] | 0,45 | −0,19 | +0,79 | +0,79 | ✗ | ✗ | ✗ | ✗ | ✗ |
| PRERUN loại thấp | 37,5 | +0,49 | [−1,22; +2,25] | 0,57 | +0,32 | +0,42 | +0,91 | ✗ | ✗ | ✗ | ✗ | ✗ |
| PRERUN loại cao | 31,5 | −0,12 | [−1,62; +1,26] | 0,88 | +0,04 | −0,13 | +0,31 | ✗ | ✗ | ✗ | ✗ | ✗ |
| DIST52 loại thấp | 41,3 | +0,28 | [−1,69; +2,29] | 0,76 | +1,22 | −0,44 | +1,10 | ✗ | ✗ | ✗ | ✗ | ✗ |
| DIST52 loại cao | 27,2 | +0,27 | [−1,40; +1,77] | 0,78 | +0,54 | +0,39 | +0,74 | ✗ | ✗ | ✗ | ✗ | ✗ |
| loại UP_FULL | 20,4 | +0,47 | [−1,39; +2,70] | 0,71 | −0,30 | +0,76 | +0,86 | ✗ | ✗ | ✗ | ✗ | ✗ |
| loại UP_THEN_DOWN | 5,1 | +0,82 | [−2,19; +4,41] | 0,70 | +2,14 | +0,14 | +1,64 | ✗ | ✗ | ✗ | ✗ | ✗ |
| loại DOWN | 14,6 | −0,20 | [−1,93; +1,64] | 0,79 | +0,23 | −0,47 | +0,21 | ✗ | ✗ | ✗ | ✗ | ✗ |
| loại FLAT | 59,9 | −0,38 | [−1,96; +1,11] | 0,66 | −0,26 | −0,30 | −0,00 | ✗ | ✓ | ✓ | ✗ | ✗ |

- **c5 trượt ở cả 14 dòng.** Mọi nhóm bị loại đều lãi 2,3–5,3%, cao hơn hẳn lãi nhàn rỗi pin1M khoảng 0,32%. Ở pin0% (ngưỡng 0) càng rõ hơn.
- Nghĩa là bộ lọc chỉ có lợi nếu vốn được **dồn sang candidate LAG khác**. Nhưng nghiên cứu 10-21 đo được vốn LAG live đang **thiếu triển khai khoảng 90%** vì lý do vận hành, tức không thiếu candidate để thay. Ước lượng định tính, chưa đo bằng NAV.
- Độ nhạy (`filter_grid.csv`): Y_live (Luật A) và Y vượt VNI cho cùng kết luận. AVOL thấp với Y_live: −2,92pp [−4,46; −1,43].

## 4. Hậu kiểm AVOL thấp (KHÔNG có trong PREREG, không tính vào trials) — ĐO
| Tập con | n | n thấp | Δ | CI95 cụm-mùa |
|---|---:|---:|---:|---|
| Toàn bộ | 5.361 | 1.392 | −2,98 | [−4,61; −1,48] |
| **In universe_pit (e−1)** | 3.050 | 302 | **−1,73** | **[−4,08; +0,55]** |
| In pit · IS | 973 | 141 | −1,11 | [−3,40; +1,60] |
| In pit · OOS | 2.077 | 161 | −1,63 | [−5,60; +1,76] |
| Ngoài universe_pit | 2.311 | 1.090 | −3,01 | [−4,93; −1,52] |
| Bỏ ca V[d0]=0 | 4.690 | 721 | −1,34 | [−3,03; +0,11] |

- Có 671 ca khối lượng ngày phản ứng bằng 0, chiếm 48% nhóm thấp.
- Nhóm thấp: 21,7% in-pit. Nhóm còn lại: 71,0%.
- Bỏ-một-năm trong pit: điểm ước lượng luôn âm, từ −1,41 đến −2,22. Nhưng CI toàn tập pit chứa 0.
- Nếu muốn theo tiếp thì phải là PREREG MỚI, chỉ 1 trial, giới hạn trong universe_pit, có lọc ADV live. Tôi KHÔNG đề xuất: 302 sự kiện trên 51 mùa, CI rộng, và lại là một bộ lọc thanh khoản nữa sau khi liq-tilt đã bị REFUTED.

## 5. Capacity
- AVOL thấp loại 26% sự kiện. Trong 3,9% số mùa, bộ lọc loại >50% candidate.
- Các bộ lọc giá loại 20–74% sự kiện. GAP loại ≥0 làm >50% candidate biến mất ở 100% số mùa.
- Không bộ lọc nào đủ điều kiện, nên không đo tỷ lệ slot nhàn rỗi bằng NAV.

## 6. Deviations so với PREREG
1. **GAP suy biến**: P33 = P67 = 0 trên IS, vì rất nhiều phiên có Open_adj = Close trước. Do đó "loại thấp" = GAP ≤ 0 (67%) và "loại cao" = GAP ≥ 0 (74%), không phải tercile. Giữ nguyên cách cắt để không đổi định nghĩa sau khi thấy dữ liệu; hai dòng GAP vì vậy kém thông tin.
2. **Y chính không loại phiên khoá trần**, giống engine pin. Vì vậy Y TB 4,551% khác ô W1·NONE·ANCH 4,510% của nghiên cứu 10-21 (ô đó loại ca khoá trần). **Control**: Y_live (W3·Luật A·ANCH, cơ sở Open) = **4,610%**, khớp đúng 4,6098% của `exp_window_grid_openbasis.csv`.
3. **pin1M** lấy `idle_rate_proxy.py` tier `dep1m` từ commit `aaed41eec` (nhánh research, chưa vào main), trích vào `/tmp/irp_dep1m`. Lãi = r_dep1m(entry) × ngày lịch kỳ nắm / 365.
4. **Y_ex** cài đặt = Y − (VNI Close e−1 → Close e+25). Câu chữ PREREG §2(i) ghi lủng củng, đây là cách hiểu duy nhất khả thi.
5. **AVOL** thiếu 97 ca vì d0 < 20 phiên lịch sử. Theo luật, các ca này luôn được giữ lại.
6. **universe_pit** được đọc qua `BQ_LOCAL_CACHE`: 3.050/5.361 in-universe, thiếu 1 dòng.
7. **NAV không chạy**: không bộ lọc nào là ỨNG VIÊN. Vì thế self-check 0 VND, chân control NAV và dải pin0%/pin1M của NAV không áp dụng. Không đụng NAV, không đụng registry.

## 7. Ngoài phạm vi
"Đọc chart cảm tính": nền giá, mẫu hình nến, vùng cản ngoài đỉnh 52 tuần. Những thứ này không lượng hoá được bằng luật cố định, nên không bịa quy tắc.
