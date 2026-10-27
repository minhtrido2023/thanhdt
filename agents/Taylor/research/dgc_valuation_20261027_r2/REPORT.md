# DGC (Hóa chất Đức Giang): định giá VÒNG 2, 27/10/2026

Job `Taylor_20261026_174426`; vòng 1: `../dgc_valuation_20261027/REPORT.md` (job `..._171735`, KHÔNG sửa). Nghiên cứu READ-ONLY, không phải khuyến nghị mua bán; DGC EXCLUDED ở ZaloPay, báo cáo không đụng tới. Đơn vị tỷ đồng, đ/cp. **[UL]** = ước lượng không có nguồn công bố. Tái lập: `python3 model.py` (log: `run_stdout.txt`), khoá md5 ở `LOCK.txt`. Dự báo Q3 `../dgc_q3_forecast_20261026/FORECAST.md` không sửa (md5 d6ea39f4).

> ## ⚠️ CHẠY LẠI NGAY KHI CÓ BCTC Q3 (công bố dự kiến 27/10–14/11). CHƯA CHỐT TRƯỚC ĐÓ.
> Tiền ròng 30/09 (6.063 tỷ) vẫn là số **dựng lại**: CFO Q3 +300 và capex Q3 250 là [UL]; phần cổ tức PAT trả cho CĐKKS chưa tính; PAT-CĐKKS 365 là ước lượng. Sai ±500 tỷ ≈ ±1.300 đ/cp.

## Kết luận (10 dòng)
1. **Giá trị kỳ vọng ~32.500 đ/cp (có điều kiện)**, thấp hơn vòng 1 (33.609) chủ yếu vì 3 sửa kỹ thuật (xem waterfall). Giá 26/10 là 32.100 (phiên −4,7%); trung bình 5 phiên 20–26/10 là 33.500 (đo từ BQ). Kỳ vọng so với giá 26/10 **+1,1%**, so với TB 5 phiên **−3,1%**: gần như **không có biên an toàn**.
2. **Kịch bản cơ sở = "cơ sở-có-mở-lại ½ trong 2028": 33.438.** Trọng số **thuận 0,2 / cơ sở 0,5 / nghịch 0,3**. Đổi sang thuận 0,3 / cơ sở 0,5 / nghịch 0,2 thì kỳ vọng = 35.839.
3. **Phụ thuộc có điều kiện vào khai trường 25/19B (HIỆN TRẠNG: quặng nhập kéo dài).** Nếu cơ sở và nghịch không mở lại (thuận giữ): kỳ vọng **30.096**, cơ sở **28.716**. Không mở lại ở cả 3 kịch bản: **27.506** (thuận hạ còn 38.818). Giá hiện tại nằm giữa hai trạng thái này.
4. Ở giá 32.100, thị trường ngầm định LNST mẹ **lõi** chuẩn hoá ~982 tỷ/năm; cơ sở của tôi 1.031, nghịch 542, thuận 1.728.
5. **Ba phương pháp KHÔNG phải xác nhận độc lập**: cả ba dùng chung LNST lõi 2027–28, `NET_CASH_0930` và haircut. Độ gần nhau (cơ sở 30.633–36.671) chỉ nói rằng chúng nhất quán nội bộ, không nói mô hình đúng.
6. BVPS BQ 42.744 là trước cổ tức 8.000 đ/cp (TT 25/09): BVPS thật 30/09 ≈ 35.600, **P/B ≈ 0,90**, không phải 0,75.
7. **Q4/2026 cơ sở: LNST mẹ 274 tỷ** (dải 183–371); cả năm 2026 cơ sở **1.393 mẹ / 1.521 hợp nhất**.
8. **Chỉ tiêu 1.600 tỷ chưa biết là mẹ hay hợp nhất: ~50/50** cho tới khi đọc Nghị quyết gốc. Xác suất đạt: nếu mẹ 8,3%, nếu hợp nhất 31,3%; **gộp 50/50 ≈ 20%**.
9. Nghi Sơn GĐ1 ≈ −140 đ/cp trong cơ sở (NPV LNST steady bị ~929 tỷ capex còn lại triệt tiêu); là tuỳ chọn tăng ở thuận (+2.000), không phải trụ định giá.
10. ⚠️ **WARNING pháp lý** (vụ án hình sự, hạn chế giao dịch HOSE, 2 ngoại trừ kiểm toán) nằm trong định giá dưới dạng haircut pháp lý 3/9/29% (đã tách riêng phần PAT) và bảng nhạy tồn kho; không phải cổng chặn. Dải nhạy haircut 0–50% × xoá sổ tồn kho 0–951: **24.682–34.362** (cơ sở).

| Kịch bản | Trọng số | LNST mẹ 2026 / 2027 / 2028 | SOTP | DCF | Multiple TB | **Blend** |
|---|---|---|---|---|---|---|
| Thuận (mở lại 0,5 năm 2027, đủ 2028) | **0,2** | 1.589 / 1.868 / 2.473 | 53.691 | 52.438 | 49.175 | **51.768** |
| **Cơ sở-có-mở-lại ½ trong 2028** | **0,5** | 1.393 / 1.101 / 1.651 | 33.011 | 36.671 | 30.633 | **33.438** |
| Nghịch (không mở lại) | **0,3** | 1.200 / 748 / 848 | 17.909 | 19.441 | 16.495 | **17.948** |
| **Kỳ vọng** | | | | | | **32.457** |
| *HIỆN TRẠNG: cơ sở KHÔNG mở lại (thuận giữ)* | | | | | | cơ sở 28.716 → kỳ vọng **30.096** |
| *Không mở lại ở cả 3 kịch bản* | | | | | | thuận 38.818 → kỳ vọng **27.506** |

Cột "Multiple TB" = trung bình của PE DGC 10y (8,3), PE peer **hiện tại** (9,1) và P/B lõi chính đáng. Mọi kết luận ở trên đều **có điều kiện** vào ba thứ: khai trường, tiền ròng 30/09 dựng lại, và định nghĩa 1.600.

## Thay đổi so với vòng 1 (điểm 1–15)

| # | Kết quả | Chi tiết |
|---|---|---|
| 1 | **ĐÃ SỬA** (lập luận sai chiều) | Lợi suất lãi tiền sau thuế/MI trên tiền ròng bình quân 2027 = 282/5.350 ≈ 5,3% (`out_forecast.csv`; 5.350 là ước lượng của skeptic, [UL]) ⇒ PE 8,3–10,5 chỉ trả **0,44–0,55 đồng cho 1 đồng tiền**, không phải 1,2–1,3. Lập luận đúng ở mục 5. Kiểm phương pháp (c): (c) áp PE lên LNST **2027–28** (đã trừ cổ tức và capex NS trong đường tiền), **không** áp lên EPS 2026, nên không mắc đúng lỗi bị chê; nhưng (c) định giá tiền ở 0,34–0,40 đồng/đồng (`out_multiples.csv`, cột `cash_value_in_pe`, trên tiền ròng 30/09) trong khi SOTP/DCF định giá ~0,9. Đây là **thiên lệch XUỐNG của nhánh (c)**, giữ nguyên và nêu rõ (không đổi cấu trúc để ba nhánh còn khác nhau). |
| 2 | **ĐÃ SỬA** | Bỏ chữ "khớp". Mục tiêu DSC 41.000 = PE 8,5 × EPS 2026F; DSC dự LNST mẹ 2026 = **1.722** (extract), cao hơn tôi (1.393) **24%**; DSC ghi cổ tức 2026 = 0%. Quy đổi cùng phương pháp DSC: 41.000 − 8.000 × (6,8% × (1−13%)) × 8,5 ≈ **37.000** (skeptic ước ~37.500). So với cơ sở 33.438, DSC cao hơn ~10%, đúng chiều với dự phóng cao hơn của họ. Ngày báo cáo DSC: extract ghi **"Cập nhật: 27/07/2026"**, sửa mọi chỗ ghi 10/08 (vòng 1 sai). |
| 3 | **ĐÃ SỬA** | Nhãn trọng số tường minh **thuận 0,2 / cơ sở 0,5 / nghịch 0,3** mọi chỗ; kịch bản đảo: thuận 0,3 / cơ sở 0,5 / nghịch 0,2 ⇒ 35.839 (vòng 1 ghi 37.200). |
| 4 | **ĐÃ SỬA + chạy lại** | 500 kt × (155−60=95 $/t) × 26.300 = 1.249 tỷ ở 100%; × 80% = **999 ≈ 1.000** (vòng 1 dùng 1.100: 1.250 là mức 100%, nhầm). Tác động −507 đ/cp trên kỳ vọng. |
| 5 | **ĐÃ SỬA** | Mục 4 dưới đây: bằng chứng cả hai phía, hạ về 50/50, tính lại xác suất (≈20%). Nguyên văn extract dòng 43–45 là "LNST công ty mẹ đạt 797 tỷ đồng … 54% kế hoạch". |
| 6 | **ĐÃ SỬA (phần làm được)** | Bảng biên gộp có đủ Q1/2026 23,0%; ghi rõ chỉ 1 quý thực tế sau khi dừng khai trường (Q2 18,9%); Q3 = dự báo chưa chấm; thêm bẫy GPM_P0 BQ vs báo chí. **Không nối được** giá lưu huỳnh/P4 với biên gộp trong SCN: chưa có định mức tiêu hao theo mảng và chỉ 1 quý quan sát để hiệu chỉnh ⇒ cột lưu huỳnh trong SCN **chỉ là mô tả**, biên gộp là giả định theo kịch bản. |
| 7 | **ĐÃ SỬA** | Bảng tiêu đề thêm dòng HIỆN TRẠNG (xem trên); kịch bản cơ sở đổi tên "cơ sở-có-mở-lại ½ trong 2028". Số của tôi (28.716 / 30.096 / 27.506) gần số skeptic (29.163 / 30.942 / 28.018); chênh vì tôi đã áp thêm các sửa khác. |
| 8 | **ĐÃ SỬA** | rf = max(Big-4 12M, CCTG 12M) = **7,4%** (`data/cctg_rate_vn_events.csv` dòng 10/05 và 10/12: BIDV/VietinBank 12T 7,4%; Big-4 12T online là 6,8%). Ke 14,3% → 14,9%. Lãi tiền gửi của chính DGC vẫn tính 6,8% (đó là lợi suất DGC thực nhận, không phải rf). Tác động −502 đ/cp. |
| 9 | **ĐÃ SỬA** | Báo cả hai: PE peer hiện tại **9,1**, trung vị 10 năm **10,5**. **Điểm chính = 9,1.** Lý do: PE hiện tại phản ánh cùng chế độ lãi suất/lợi nhuận hiện tại với DGC; trung vị 10y chứa giai đoạn 2021 (peer PE 12–13) khi kỳ vọng khác hẳn. Dùng 10,5 làm độ nhạy (kỳ vọng +538 ⇒ 32.995). Tác động −534 đ/cp. |
| 10 | **ĐÃ SỬA** | Cộng dồn 4+8+9 ⇒ **32.066** (đúng ước tính ≈32.066 của skeptic; waterfall dưới). Sau thêm 12–13: **32.457**. Giá 26/10 = 32.100 (phiên −4,7%); TB 5 phiên 20–26/10 = **33.500** (BQ: 20/10 33.650; 21/10 34.250; 22/10 33.800; 23/10 33.700; 26/10 32.100). |
| 11 | **ĐÃ SỬA** | Bỏ "ba phương pháp hội tụ"; viết là cùng chung đầu vào (kết luận 5, mục 3). |
| 12 | **ĐÃ SỬA, có tự kiểm BQ** | PAT BQ 2026Q2: totalAsset **1.010,6 tỷ**, BVPS 29.694 × 25 tr cp = VCSH **742 tỷ** (khớp skeptic). Tách PAT-CĐKKS **365 tỷ [UL]** (49% × tiền gửi PAT ~650–750; TNTC Q3 11,4 tỷ là số của skeptic, **chưa tự kiểm**; trần 49% × VCSH 742 = 364) = 961 đ/cp, trừ khỏi tiền ròng **không qua haircut**. Haircut pháp lý còn lại **3/9/29%** (vòng 1: 5/15/35%, trong đó ~6pp là phần PAT). Tác động chỉ −26 đ/cp. Câu hỏi "còn ~9–10% thay vì 15%": chọn **9%**. |
| 13 | **ĐÃ SỬA / GIỮ** | Chi tiết ở mục 6 (thiên lệch chiều xuống). Sửa được: (a) lõi Q4/2026 189 tỷ ≈ +498 đ/cp cộng vào tiền (+483 trên kỳ vọng); (b) MI 10% không ăn lên lãi tiền của DGC mẹ (+42); (c) DCF chiết khấu giữa-năm từ 27/10 thay vì nguyên 1 năm (+344); (d) Nghi Sơn thống nhất ba phương pháp: P/B tách NS khỏi VCSH lõi, PE và P/B đều trừ 929 capex (−452). **Giữ + nêu số:** lợi suất tiền 6,5% vs 7,1% (độ nhạy +207); MI lõi thực 17,8% ở Q2 (độ nhạy −1.872). |
| 14 | **ĐÃ KIỂM, đưa vào độ nhạy** | Thuế lãi tiền gửi 13% **chưa xác minh**; ở 20%: kỳ vọng −109 đ/cp (32.348), chỉ qua nhánh PE vì tiền định giá theo mệnh giá ở SOTP/DCF. **Cần legal-vn** xác nhận thuế suất áp cho lãi tiền gửi của DGC. |
| 15 | **ĐÃ SỬA** | Banner đầu báo cáo. |

## 1. Waterfall vòng 1 → vòng 2 (`out_waterfall.csv`, bật dần)
| Bước | Kỳ vọng | Δ | Cơ sở |
|---|---|---|---|
| Vòng 1 (tái lập đúng) | 33.609 | | 34.497 |
| +4 uplift khai trường 1.000 | 33.102 | −507 | 34.013 |
| +8 rf 7,4% | 32.600 | −502 | 33.489 |
| +9 PE peer hiện tại 9,1 | **32.066** | −534 | 32.949 |
| +12 tách PAT-CĐKKS | 32.040 | −26 | 32.986 |
| +13a lõi Q4/2026 vào tiền | 32.523 | +483 | 33.484 |
| +13b MI không ăn lãi tiền | 32.565 | +42 | 33.527 |
| +13c DCF giữa-năm từ 27/10 | 32.909 | +344 | 33.889 |
| +13d Nghi Sơn thống nhất | **32.457** | −452 | 33.438 |

Thứ tự bật không thay đổi tổng cuối, nhưng Δ từng bước phụ thuộc thứ tự. Hai bước 13a và 13c (+827) bù cho 4+8+9 (−1.543).

## 2. Dữ liệu đầu vào
Giữ nguyên bảng đầu vào, mục tồn kho/CFO H1 và dự phóng theo mảng của vòng 1 (`../dgc_valuation_20261027/REPORT.md` §1–§2), trừ các điểm sửa ở đây. Khác biệt cần nhớ:
- DSC cập nhật **27/07/2026** (không phải 10/08); URL tệp vẫn tên `BCCN_DGC_Q2_2026`. DSC dự LNST mẹ 2026F **1.722**, giá mục tiêu 41.000 trên giá 44.200 (trước cổ tức).
- LNST mẹ 2025 (BQ: 809,3 + 842,2 + 751,6 + 621,8) = **3.025**; 1.722 / (1 − 43%) ≈ 3.021 khớp ⇒ DSC dùng nền **mẹ**.
- rf DCF 7,4% (xem điểm 8).

### Biên gộp theo quý (điểm 6)
| Kỳ | Biên gộp | Trạng thái |
|---|---|---|
| Q1/2026 | **23,0%** (LN gộp 488,7 / DT 2.125) | thực tế (báo chí); trạng thái khai trường trong Q1 chưa xác minh, không dùng làm mốc "đã dừng" |
| Q2/2026 | **18,9%** (456 / 2.415) | thực tế, **quý duy nhất sau khi dừng khai trường** |
| Q3/2026 | 16,0% (dải 80% 12,3–19,8%) | **dự báo khoá, chưa chấm** (công bố 27/10–14/11) |
| Q4/2026 cơ sở | 16,5% | giả định |
| 2027 / 2028 cơ sở (quặng nhập; hiệu ứng mở lại) | 16,5% / 22,8% hiệu dụng | giả định (2028 gồm +500 tỷ mở lại ½) |

Chỉ có **một** quan sát thực tế (Q2) ở chế độ quặng nhập; biên 16–17% của 2027 dựa trên một quý thực tế cộng một dự báo. ±3pp biên ≈ ±4.000 đ/cp (bảng DCF Ke × biên, `out_dcf_sens_ke_gm.csv`). Không nối giá lưu huỳnh/P4 vào biên gộp trong SCN (xem điểm 6); cột lưu huỳnh chỉ mô tả.

**Bẫy dữ liệu bổ sung (đề nghị Winston ghi registry):** `ticker_financial.GPM_P0` của DGC **xung đột báo chí**: BQ Q1/2026 = **28,7%**, Q2 = **24,8%** (đo) so với 23,0% và 18,9% từ báo cáo/Vietcap (FORECAST §3 cũng ghi nhận). Hai nguồn lệch 5,7–5,9pp ⇒ **không dùng GPM_P0 của BQ cho 2026**; nguồn chấm là BCTC gốc. Cũng nhắc lại bẫy vòng 1: `Cash_P0` DGC chỉ là tiền mặt (37 tỷ, không gồm tiền gửi), `EVEB` BQ bị thổi phồng; `PB`/`BVPS` BQ trước cổ tức.

## 3. Định giá
**Ba phương pháp dùng chung** `core_np_mi` 2027–28, `NET_CASH_0930` (6.063) và haircut/tách PAT; do đó khoảng cách giữa chúng không phải bằng chứng độc lập mà chỉ là tính nhất quán.

### (a) SOTP (đ/cp, cơ sở)
| Cấu phần | Nghịch | **Cơ sở** | Thuận |
|---|---|---|---|
| Tiền ròng 6.063 − PAT-CĐKKS 365, × (1 − haircut pháp lý 29/9/3%) + lõi Q4/2026 | 10.955 | **14.150** | 15.269 |
| Lõi: LNST mẹ lõi chuẩn hoá (TB 2027–28) × PE lõi 6/7/8 | 8.563 (542) | **19.003** (1.031) | 36.400 (1.728) |
| Nghi Sơn: LNST steady × PE, chiết 2 năm theo Ke 14,9%, − capex 929 | −1.608 | **−143** | 2.021 |
| **Tổng** | **17.909** | **33.011** | **53.691** |

### (b) DCF FCFF lõi
Ke = 7,4% + 1,0 × 7,5% = **14,9%**, g 3%, RONIC 12% [UL]; dòng tiền giữa-năm từ 27/10 (t = 0,68 + j; giá trị kết thúc cũng ở t = 4,68). Kết quả: nghịch **19.441** / cơ sở **36.671** / thuận **52.438**. Nhạy Ke × g (cơ sở): 14,9% g 3% = 36.671; Ke 16% = 34.684; Ke 18% = 31.814 (`out_dcf_sens_ke_g.csv`). Nhạy biên dài hạn: 17% = 30.107, 20% = 34.087, 23% = 38.066 (Ke 14,9%). Hoà vốn: giá 32.100 ≈ biên dài hạn ~19%.

### (c) Multiple (đ/cp)
| | PE DGC 10y 8,3 | PE peer hiện tại **9,1** | PE peer 10y 10,5 | P/B lõi chính đáng + NS |
|---|---|---|---|---|
| Nghịch | 15.381 | 16.978 | 19.814 | 17.126 |
| **Cơ sở** | 28.269 | **31.022** | 35.914 | 32.607 (ROE lõi 16,2%, P/B 1,11) |
| Thuận | 45.935 | 50.278 | 57.994 | 51.313 |

Mọi nhánh trừ 929 capex Nghi Sơn còn lại và cộng lõi Q4/2026; P/B tách 1.471 tỷ NS ghi sổ ra khỏi VCSH lõi rồi cộng giá trị NS như SOTP. Peer (BQ, 26/10): BFC 12,6, CSV 9,9, DCM 7,2, DDV 6,4, DPM 8,3, LAS 15,2; PAT bị loại (con công ty). **Thiên lệch xuống:** nhánh PE coi lãi tiền như lợi nhuận thường nên định giá tiền ở ~0,4 đồng/đồng (điểm 1).

## 4. Chỉ tiêu 1.600 tỷ: mẹ hay hợp nhất? (điểm 5)
| | Ủng hộ **hợp nhất** | Ủng hộ **mẹ** |
|---|---|---|
| Phép chia 54% | 871 / 1.600 = **54,4%** khớp "54%" | 797 / 1.600 = 49,8% **không** khớp; nếu mẹ thì kế hoạch phải ~1.476 (797/0,54) |
| Nhãn văn bản | | extract dòng 43–45 nguyên văn "**LNST công ty mẹ** đạt 797 tỷ … 54% kế hoạch"; Vietcap "**NPAT-MI** 1,6tn" |
| "Giảm ~50% so 2025" (Nhadautu) | 1.600 / 3.220 (nền hợp nhất 2025, **số của skeptic, chưa tự kiểm**) = −50,3% | 1.600 / 3.025 (nền mẹ, đã đo) = −47,1%, vẫn là "gần một nửa" |

Hai nhãn rõ ràng (nhãn văn bản) đối nghịch với phép chia; vòng 1 nghiêng 60/40 về hợp nhất là **quá tay**. Hạ về **50/50** cho tới khi đọc Nghị quyết ĐHĐCĐ gốc. Xác suất mô phỏng (Q3 sd 82, Q4 sd 85 [UL], tương quan 0,6 [UL]): nếu mẹ, Q4 cần **481** ⇒ **8,3%**; nếu hợp nhất, Q4 cần **379** ⇒ **31,3%**; **gộp 50/50 = 19,8% ≈ 20%** (vòng 1 với 60/40: 22,1%, ghi "~20%"). Điểm này đổi xác suất "đạt kế hoạch" nhưng không đổi giá trị nội tại.

## 5. Phản biện ước lượng sơ bộ của Mike (viết lại)
- **"Q4 ~330, cả năm ~1.450 mẹ":** Q4 cơ sở **274**, vì sau cổ tức 25/09 thu nhập tài chính giảm ~55 tỷ/quý. Cả năm cơ sở 1.393.
- **"PE 8–9x":** lập luận đúng là thế này, không dùng công thức "1,2–1,3 đồng cho 1 đồng tiền" của vòng 1 (sai chiều):
  - EPS 2026 còn chứa lãi của ~3.038 tỷ **đã chi cổ tức ngày 25/09**. Nhân PE vào EPS 2026 là định giá một khoản tiền không còn.
  - Lợi suất lãi tiền sau thuế/MI trên tiền ròng bình quân 2027 ≈ 5,3% (282/5.350 [UL mẫu số]), nên PE 8,3–10,5 chỉ trả 0,44–0,55 đồng cho 1 đồng tiền (định giá tiền *thấp* hơn mệnh giá). Dùng PE trên EPS 2027–28 (nhánh c) tránh được lỗi dùng 2026 nhưng nén giá trị tiền.
  - 2027 cơ sở (1.101) thấp hơn 2026 vì thu nhập tài chính giảm và quặng vẫn nhập. PE × LNST 2027 cơ sở chỉ cho ~24–26k (EPS 2.899 × 8,3–9,1).
- **"30–34k nếu ~1.450":** khớp về số, khác lý do: tiền ~14k/cp (sau haircut, tách PAT) + lõi ~19k/cp.

## 6. Thiên lệch chiều xuống đã biết (điểm 13) và các điểm yếu còn lại
Thiên lệch **xuống** (mô hình có thể đang thấp): (1) Q4 lõi 189 tỷ — **đã sửa**; (2) DCF chiết khấu nguyên năm — **đã sửa**; (3) lợi suất tiền 6,5% ở cơ sở vs 7,1% Q2 thực: độ nhạy 7,1% ⇒ kỳ vọng 32.664 (+207), giữ 6,5% vì lãi suất huy động đang giảm; (4) MI 10% áp lên lãi tiền — **đã sửa**; (5) nhánh P/B không trừ 929 capex — **đã thống nhất**; (6) nhánh PE định giá tiền ~0,4 — **giữ**, nêu rõ.
Thiên lệch **lên** (mô hình có thể đang cao): (7) MI lõi thực: Q2 MI 51 / LNST lõi sau thuế ~287 = **17,8%**, FORECAST Q3 ngầm ~13%; mô hình dùng 10% ⇒ độ nhạy 13% ⇒ **31.735** (−722), 17,8% ⇒ **30.585** (−1.872). Đây là điểm yếu số liệu lớn nhất còn chưa sửa vì cần BCTC Q3 để xác định PAT đóng góp; (8) trọng số 0,2 thuận chưa hiệu chỉnh (thuận cần mở lại sớm, không có mốc thời gian nào); (9) biên 16–17% dựa trên 1 quý thực tế.

Điểm yếu đổi kết luận nhiều nhất: (i) khai trường (HIỆN TRẠNG vs mở lại: 28.716 vs 33.438 ở cơ sở; thuận 38.818–51.768); (ii) tiền ròng 30/09 dựng lại; (iii) MI lõi (−722 đến −1.872); (iv) định nghĩa 1.600.

## 7. Rủi ro và WARNING pháp lý (⚠️)
Luật user 27/09/2026: phân tích bình thường, ghi rõ nguồn và ảnh hưởng, không cổng chặn. Nội dung các mục (vụ án hình sự; HOSE hạn chế từ 26/05/2026, trạng thái sau T8 chưa xác minh; BCTC 2025 có 2 ngoại trừ: kiểm kê tồn kho ~951 tỷ và tác động điều tra) giữ nguyên như vòng 1 §4. Thay đổi: haircut pháp lý **3/9/29%** (sau khi tách PAT-CĐKKS), bảng nhạy SOTP cơ sở dưới (đã cộng lõi Q4, trừ PAT 365):

| SOTP cơ sở | tồn kho −0 | −475 | −951 tỷ |
|---|---|---|---|
| haircut pháp lý 0% | 34.362 | 33.273 | 32.183 |
| **9%** | **33.011** | 31.923 | 30.833 |
| 15% | 32.111 | 31.023 | 29.933 |
| 30% | 29.861 | 28.773 | 27.682 |
| 50% | 26.860 | 25.772 | 24.682 |

Thuế hiệu dụng 13% có thể hết ưu đãi: thuế 20% cho lãi tiền ⇒ −109 đ/cp (**cần legal-vn**); thuế 20% cho cả lõi vẫn là rủi ro ~−8% giá trị lõi [UL] như vòng 1.

## Độ nhạy bổ sung (`out_sensitivities.csv`, kỳ vọng / cơ sở)
| Trường hợp | Kỳ vọng | Cơ sở |
|---|---|---|
| r2 chính | 32.457 | 33.438 |
| thuế lãi tiền 20% [cần legal-vn] | 32.348 | 33.329 |
| MI lõi 13% | 31.735 | 32.710 |
| MI lõi 17,8% (Q2 thực) | 30.585 | 31.543 |
| PE peer 10y 10,5 | 32.995 | 33.982 |
| rf 6,8% (r1) | 32.970 | 33.974 |
| lợi suất tiền gửi 7,1% | 32.664 | 33.619 |

## Nguồn
- BQ `tav2_bq.ticker` (giá 20–26/10), `ticker_financial` (DGC, PAT), query 27/10/2026 ~00:45 ICT; dữ liệu cũ ở `data/*.csv`.
- `data/cctg_rate_vn_events.csv`, `deposit_rate_vn.py` (quy ước rf = max(Big-4 12M, CCTG 12M)).
- DSC cập nhật **27/07/2026**: https://extgw.dsc.com.vn/eback/uploads/BCCN_DGC_Q2_2026_f4ec47b822.pdf → `data/dsc_dgc_q2_2026_extract.txt`.
- Vietcap flash/AGM 22/07/2026; Nhadautu 13/08; cổ tức baophapluat 13/09; HOSE vietnamfinance; Elibook 08/09 (URL như vòng 1 §Nguồn).
- Q3 forecast khoá: `../dgc_q3_forecast_20261026/FORECAST.md`. BCTC gốc Q2/bán niên 2026 và Nghị quyết ĐHĐCĐ: **chưa đọc được bản gốc**; mọi số bảng cân đối là nguồn thứ cấp.
