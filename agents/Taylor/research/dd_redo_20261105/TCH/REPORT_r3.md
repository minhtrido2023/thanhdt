# TCH — DD REDO VÒNG 3 · 09/11/2026 · job `Taylor_20261108_180134`

> Thay `REPORT_r2.md` (05/11) ở phần định giá/nhãn. Áp đính chính fundamental-skeptic `TOP5D_CORRECTIONS_20261108.md` mục TCH (đã kiểm từng điểm bằng calc, §6).
> Số: `calc_r3/tch_r3.py` → `tch_r3_out.json/txt`, `grid_tch_r3.csv` (2 lần trùng byte: `run1.md5 = run2.md5`); khoá `calc_r3/LOCK_md5.txt` ghi bằng `md5sum` lúc
> **2026-11-09T01:05:24+07:00, TRƯỚC khi đọc giá** (đủ 20 file upstream); so giá: `calc_r3/tch_r3_compare.py` → `compare_r3_out.txt` + `SUMMARY.json` (2 lần trùng byte: `cmp1.md5 = cmp2.md5`).
> Giá tham chiếu: đóng cửa 06/11/2026 = **13.500** (BQ `tav2_bq.ticker`, `calc_r3/px_tch_r3_20261106.csv`). r = 13,5% + 1,0×(7,40% − 7,40%) = **13,50%** (CCTG 12T 02/11).
> Không đặt lệnh · không sửa `kb/dd_price_zones.json` · không email/PDF.

## 0. Kết luận (headline = mô hình cơ sở sau đính chính)

| | r3 HEADLINE | r2 (05/11) |
|---|---|---|
| Tâm sau CK 5 tỷ | **16.244** | 13.768 |
| P10 / P50 / P90 (mức kết cục, `wpct`) | **15.578 / 16.208 / 16.950** | 12.559 / 13.726 / 14.983 |
| Giá trị tại tham số trung tâm | 16.208 | 13.775 |
| Giá 06/11 | 13.500 | (12.750 @04/11) |
| % trọng số dưới giá | **0,0%** (n=27) | 19,1% @12.750 → **44,5% @13.500** |
| Giá / tâm | **−16,9%** | −7,4% @12.750 → −1,9% @13.500 |
| Nhãn cỡ 5 tỷ | **DƯỚI vùng** (giá < P10 13,3%) | TRONG vùng |
| Nhãn sleeve 10/20/40 tr | DƯỚI vùng (tâm 16.342/16.340/16.338) | TRONG |
| Luật 4 (giá ≤ 0,85×tâm) | 5 tỷ: 13.500 ≤ 13.807 **ĐẠT**; sleeve: ≤ 13.889 **ĐẠT** | — |

**Nhãn ĐẢO TRONG → DƯỚI vùng.** Lý do: hai đính chính kéo lên (bỏ CK holding [UL] khỏi base +1.164; đất cũ nhất quán với biên gộp quan sát +1.300), không do đổi định nghĩa vùng (P10–P90 giữ nguyên).

⚠️ **Hai bản nổi bật — user phán xử** (headline giữ CK holding = 0 theo quy tắc chung; bản có CK holding chỉ song song):

| Bản | Tâm | P10 | P90 | Nhãn @13.500 | % dưới giá |
|---|---|---|---|---|---|
| HEADLINE (holding 0) | 16.244 | 15.578 | 16.950 | DƯỚI | 0,0% |
| + CK holding {0;10;20;30} đều (r2) | 14.960 | 13.590 | 16.327 | DƯỚI (sát) | 7,0% |
| + CK holding {10;20;30} (r1) | 14.532 | 13.500 | 15.521 | DƯỚI/biên P10 | 9,4% |
| + CK holding 27% (mức HHS) | 13.933 | 13.375 | 14.523 | TRONG | 20,3% |
| + CK quản trị 10% | 14.619 | 14.020 | 15.255 | DƯỚI | 0,0% |
| + CK quản trị 15% | 13.807 | 13.242 | 14.407 | TRONG | 25,0% |
| Biên ngành 40% cho cả backlog + đất cũ | 14.622 | 14.180 | 15.104 | DƯỚI | 0,0% |

**Giá ngụ ý** (13.500 = tâm khi): CK holding đều **32,1%** phần qua công ty con, HOẶC CK quản trị **16,9%**, HOẶC biên gộp BĐS chung **28,9%** cho cả backlog lẫn đất cũ (quan sát 51,9%), HOẶC chỉ đất cũ g 16,3% (s 6,0%). P/B tại giá 1,11x. (Skeptic ước ~19% holding / ~10% quản trị trên mô hình r2 — mức ngụ ý cao hơn vì thặng dư đất cũ tăng.)

⚠️ **Vùng P10–P90 HẸP do cấu trúc, KHÔNG phải thước đo bất định đầy đủ**: sổ sách 12.119 đ/cp = 74% tâm là hằng số, không có trục chất lượng tài sản (không có dữ liệu suy giảm). Bất định thật nằm ở các trục song song trên (holding/quản trị/biên ngành) — đều [UL] hoặc không có dữ liệu.

⚠️ **Không đủ điều kiện sleeve fear-buy §2.5**: không có khủng hoảng/sự kiện sợ hãi; **FLOOR_FAIL** (CF_OA_3Y −771,7 tỷ) — đúng lý do đã bỏ lệnh MUA TCH 03/11. Luật 4 ĐẠT không mở được sleeve.

## 1. Mô hình (giữ r2, đổi trục)
NAV mẹ = VCSH mẹ 12.159,1 (trực tiếp 5.958,6 + qua công ty con 6.200,5) + thặng dư backlog NMTT (NC-II 3.099,2 @68,02%, Green River 1.837,8, H2 617,8, H1+khác 45,0; PV 1–2 năm) + thặng dư đất cũ chưa bán (PV 4 năm) + quỹ đất mới 3.006,3 = giá sổ (NPV0). SH 1.003,31 tr cp. Số BCTC không đổi từ r1/r2 (`dd_TCH_20261031/calc/notes_read.md`, BCTC HN 6T FY26).

**Trục r3** (n=27 tất định, `wpct` mid-block):
- biên gộp backlog g_bl = 51,9% ±5pp (1/4-1/2-1/4) → m = 0,8(g−0,1) trên DT trước VAT (33,5% ở tâm);
- biên gộp đất cũ g_old = 51,9% ±5pp, ĐỘC LẬP → s = 0,8(g−0,1)/(1−g) trên giá vốn (69,7% ở tâm; 55,6% / 87,1% ở hai đầu);
- r 13,5% ±100bp (1/4-1/2-1/4).
±5pp ≈ giá bán ±10% (g' = 1−(1−g)/(1+x): +10% → 56,3%, −10% → 46,6%); độ lớn ±5pp là quy ước đối xứng [UL] — không có dữ liệu giá bán.

**Tâm / P50 / tham số trung tâm**: 16.244 / 16.208 / 16.208 (s(g) lồi ⇒ tâm cao hơn một chút). P10 do g thấp cả hai trục + r+1%; P90 ngược lại; không nhánh trọng số nhỏ nào quyết định.

## 2. Cầu r2 → r3 (tâm sau CK 5 tỷ)
| Bước | Tâm | Δ |
|---|---|---|
| r2 công bố (control tái lập center_pre 13.857,2 trùng file) | 13.768 | — |
| CK 5 tỷ theo ADV đến 06/11 (0,6446% → 0,6307%) | 13.770 | +2 |
| Đ.1: CK holding → base 0% (tái lập skeptic 14.931) | 14.934 | +1.164 |
| Đ.2a: đất cũ s = s(g), g 51,9% ±5pp | 16.234 | +1.300 |
| Đ.2b/3: backlog m = m(g) cùng trục đối xứng | 16.244 | +10 |

## 3. Giả định (khoá `calc_r3/assumptions_r3.json`)
| Giả định | Giá trị | Cơ sở / nguồn |
|---|---|---|
| CK holding base | 0% | Đ.1 + quy tắc chung: độ lớn [UL] (dữ liệu chỉ cho cấu trúc 2 tầng niêm yết, CRV free float ~3%) |
| Biên gộp BĐS quan sát | 51,9% (6T FY26), 51,0% (6T FY25) | TM25 BCTC HN 6T FY26 — DỮ LIỆU; chủ yếu NC-II, GR/H2 chưa quan sát |
| Trục g | ±5pp, 1/4-1/2-1/4, độc lập 2 trục | [UL] quy ước đối xứng ≈ giá bán ±10% |
| m(g), s(g) | 0,8(g−0,1); 0,8(g−0,1)/(1−g) | CPBH+QLDN ~10% DT, TNDN 20% (skeptic B3); s áp trên chi phí ĐÃ phát sinh ⇒ thận trọng sẵn |
| r | 13,50% ±100bp | quy tắc r; dep 06/11 = 7,40% |
| Sở hữu H1+khác | 0,80 | [UL]; độ nhạy 0,5/1,0 ⇒ 16.197/16.275 |
| Quỹ đất mới | NPV0 | luật 03/11; ±10% ⇒ 16.090/16.398 |
| CK quản trị, mất tiền gửi SGTL | 0 | WARNING; song song |
| CK thanh khoản | 5 tỷ ADV250 0,63% (ADV60 0,71%) | ADV250 87,13 tỷ, Q/ADV 5,7% trong vùng hiệu chỉnh; ADV60 56,99 tỷ, 8,8% |

## 4. Thanh khoản
ADV250 (05/11/2025–06/11/2026) 87,13 tỷ, σ 2,63%; ADV60 (12/08–06/11) 56,99 tỷ, σ 2,39%; 0 phiên KL=0. CK 5 tỷ 0,631% (ADV60 0,707%); sleeve 10/20/40 tr: 0,028/0,040/0,056% — Q/ADV <0,1%, NGOÀI vùng hiệu chỉnh ⇒ chỉ là cận trên ≈ 0.

## 5. Kiểm chéo P/B–ROE (g 3%) — cờ, không vào base
| LN mẹ | ROE có lãi gửi | Giá trị | ROE bỏ lãi gửi (+ cộng tiền mẹ 2.960) | Giá trị |
|---|---|---|---|---|
| TTM BQ 796,1 (Q4/25–Q3/26) | 6,55% | 4.094 | 5,64% | 5.252 |
| chuẩn hoá r2 727 [UL] | 5,98% | 3.442 | 4,89% | 4.600 |

Rất dưới NAV: TTM là giai đoạn TRƯỚC bàn giao chính NC-II, không đại diện. Nhưng là cờ thật: nếu tiền bán hàng được tái đầu tư vào quỹ đất ROE < Ke, giá trị cổ đông < NAV — đúng cơ chế mà các bản CK holding/quản trị song song đo. Không đưa vào base vì không có dữ liệu RONIC (moat NONE ⇒ quỹ đất mới RONIC = Ke = NPV0 đã áp).

## 6. Kiểm từng đính chính
| # | Phán quyết | Bằng chứng |
|---|---|---|
| 1 CK holding đếm đôi | **ĐÚNG — áp** | hold_0 tái lập 14.931 (CK r2); song song {0;10;20;30} 14.960, r1 14.532 |
| 2 hai biên trên cùng dự án | **ĐÚNG — áp, dạng trục g thống nhất** (không chép lưới s của skeptic) | s(1−g)=0,8(g−0,1): g 51,9% ⇒ s 69,7%. Tái lập skeptic: s{55;70;85} 16.213 (≈+1.279), s{40;55;70} 15.573 (≈+640), backlog 40% 14.604 (≈−338). "Đệm chi phí hoàn thành" không định lượng ⇒ không vào base. **Biên FY24/FY25 CẢ NĂM theo mảng BĐS chưa đọc được** (BCTC kiểm toán FY25 là PDF scan, không có OCR trong phiên) ⇒ neo bằng hai kỳ 6T đã có (51,9% / 51,0%) |
| 3 vùng hẹp do cấu trúc | **ĐÚNG — áp một phần** | thêm trục giá bán hai chiều (g ±5pp ≈ ±10%, độ lớn [UL]); KHÔNG thêm trục chất lượng tài sản (không có dữ liệu) — ghi rõ ở §0 |
| 4 giá 13.500 | **ĐÚNG — áp** | BQ 06/11 13.500, +13,9% / 5 phiên (11.850 @30/10); r2 @13.500: −1,9%, 44,5% dưới giá |
| 5 sở hữu 0,80 + ROE | **ĐÚNG — áp** | độ nhạy <50 đ; ROE TTM BQ 6,55% |
| 6 WARNING thiếu | **ĐÚNG — áp** | §7; OShares đóng (BQ 2026Q3 1.003,31 tr = SH model; 912,1 tr là quý trước đợt cp thưởng 10%) |

## 7. WARNING (pháp lý/quản trị/dòng tiền — không vào base)
- **FLOOR_FAIL**: BQ `ticker_financial` 2026Q3 CF_OA_3Y = −771,7 tỷ (`calc_r3/fin_tch_r3.csv`) do chi mua quỹ đất (150 Tô Hiệu 1.677,5 + I.14 1.328,8) — lý do bỏ lệnh MUA 03/11.
- **Tiền gửi 678,3 tỷ "NH TMCP Sài Gòn Tài Lộc"** (21% tiền+HTM): danh tính MÂU THUẪN — `notes_read.md:21` "đọc ảnh; có thể SCB/SGB" vs `investor_report:131` "Sacombank đổi tên" (không nguồn) ⇒ CHƯA xác minh. Stress mất 100%: tâm 15.572 (vẫn DƯỚI).
- Dự phòng 282,4 tỷ đầu tư vào công ty con ở BCTC RIÊNG (theo skeptic 08/11; chưa tự đọc lại trong phiên này) — loại trừ khi hợp nhất, nhưng cho thấy công ty con dưới giá vốn đầu tư.
- QĐ 1020/QĐ-XPHC 03/04/2026 Thuế TP Hải Phòng: khai sai TNDN, tổng 20,21 tỷ (đã nộp); QĐ 1357/QĐ-XPHC 12/2024 UBCKNN (CBTT/BLQ, 295 tr) — 2 cơ quan, 2 loại vi phạm trong 16 tháng.
- Nhóm kiểm soát 35,99% (Đỗ Hữu Hạ 30,18% + HH Finance 5,81%), 71,2% phiếu ĐHĐCĐ 2026; Trưởng BKS kiêm KTT công ty con; CRV free float ~3%.
- BLQ trong tập đoàn đã công bố (TCH cho CRV vay 30 tỷ, hạn mức 500 tỷ); còn mở BLQ NGOÀI tập đoàn.
- Dragon Capital bán ròng xuống 4,71% (15/06/2026). BCTC 6T FY26 chưa soát xét; sử dụng vốn chào bán 865,5 tỷ.
- "Không có khởi tố/kiểm toán ngoại trừ": nguồn GAPS 31/10/2026 + web search 05/11/2026 (r2) — **không tra lại trong phiên này**.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| BCTC soát xét 6T FY26 (AASC) | 30/11/2026 | LN mẹ 6T ±5% của 663,1, không ngoại trừ | điều chỉnh >5% / ngoại trừ ⇒ nâng WARNING, xem lại biên |
| Biên gộp BĐS kỳ kế (Q3 FY26, ~31/01/2027) | ~31/01/2027 | ≥ 51,9% có GR/H2 ⇒ trục g giữ/nâng | **< 46,9% (đầu dưới trục)** ⇒ tâm về vùng both_g40 ~14.600; < 40% ⇒ chạy lại |
| BCTC FY25 kiểm toán theo mảng (OCR) | khi có | biên BĐS cả năm ≥ 50% | < 45% ⇒ hạ tâm trục g |
| Xác minh Sài Gòn Tài Lộc | khi có | rút được/không hạn chế | hạn chế rút ⇒ đưa stress 678 vào kịch bản có xác suất (tâm −670) |
| Phân bổ tiền bán NC-II | BCTC các quý | cổ tức tiền / mua lại | dồn vào quỹ đất ROE thấp ⇒ CK holding/quản trị song song trở nên có dữ liệu |
| CF_OA_3Y | mỗi quý | > 0 (gỡ FLOOR_FAIL) | âm sâu hơn |

**HARD ABANDON**: (a) kiểm toán ngoại trừ/từ chối ý kiến; (b) khởi tố pháp nhân TCH/CRV hoặc lãnh đạo chủ chốt; (c) tiền gửi 678,3 bị phong toả; (d) cho bên liên quan NGOÀI tập đoàn vay/bảo lãnh. Sleeve 10–40 tr ⇒ không tranche.

## 9. Mở
BCTC Q3 riêng CRV (tốc độ tiêu NMTT NC-II) · xác minh NH Sài Gòn Tài Lộc · legal-vn: nhóm ủy quyền 7,37% + chuẩn duy trì niêm yết CRV · BLQ ngoài tập đoàn · HHS SOTP thị trường ~0,5x phần CRV (neo thị trường cho CK holding, chưa dùng) · biên gộp BĐS FY24/FY25 cả năm (OCR PDF kiểm toán).
**Đã đóng**: OShares (1.003,31 tr).

## 10. Tái lập
```
cd dd_redo_20261105/TCH/calc_r3
/home/trido/thanhdt/wc_venv/bin/python -I tch_r3.py           # model, không đọc giá; md5 → run1/run2
# LOCK_md5.txt (md5sum, trước khi so giá)
/home/trido/thanhdt/wc_venv/bin/python -I tch_r3_compare.py   # kiểm mọi md5 LOCK rồi mới đọc giá → ../SUMMARY.json
```
Ghi chú tái lập: lần chạy compare ĐẦU TIÊN (trước khi bỏ 1 mục open_issues trùng) cho SUMMARY.json khác md5 so với lần 2 dù `compare_r3_out.txt` trùng; chưa xác định nguyên nhân. Sau đó 5 lần liên tiếp trùng byte; bản cuối `cmp1.md5 = cmp2.md5`.
