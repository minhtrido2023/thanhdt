# DGC (Hóa chất Đức Giang): định giá chính thức, 27/10/2026

Job `Taylor_20261026_171735`. Đây là nghiên cứu READ-ONLY, không phải khuyến nghị mua bán. User đang sở hữu DGC; DGC bị EXCLUDED ở ZaloPay và báo cáo này không đụng tới.
Đơn vị: tỷ đồng và đ/cp. Nhãn **[UL]** nghĩa là ước lượng không có nguồn công bố. Số tính được tái lập bằng `python3 model.py`; kết quả ở `out_*.csv`, khoá trong `LOCK.txt`.

## Kết luận (10 dòng)
1. **Giá trị hợp lý: cơ sở ~34.500 đ/cp, dải nghịch–thuận 18.400 / 54.200.** Kỳ vọng có trọng số (0,3/0,5/0,2) là **~33.600**, chỉ cao hơn giá 32.100 khoảng **+5%**. Với trọng số 0,25/0,5/0,25 thì được 35.400 (+10%).
2. **Giá hiện tại ≈ đúng kịch bản cơ sở.** Ở 32.100, thị trường đang ngầm định LNST mẹ **lõi** chuẩn hoá ~1.010 tỷ/năm, trong khi cơ sở của tôi là 1.050. Không có biên an toàn lớn; luận điểm "rẻ" phụ thuộc vào việc khai trường mở lại.
3. **Bẫy số liệu: PB 0,75 trên BQ là số cũ.** BVPS 42.744 tính trước khi chi **8.000 đ/cp vào 25/09/2026** (5.000 còn lại của 2025 + 3.000 tạm ứng 2026, tổng ~3.038 tỷ). BVPS thật 30/09 ≈ **35.600**, nên **P/B ≈ 0,90**. Giá 32.100 là giá đã trừ quyền cổ tức.
4. **Tiền ròng 30/09 dựng lại ≈ 6.060 tỷ = ~16.000 đ/cp** [UL]. Mức "núi tiền 10,9 nghìn tỷ" là số trước cổ tức và chưa trừ vay 1.870. Sau haircut pháp lý 15%, tiền đóng góp ~13.600 đ/cp, tức ~42% giá.
5. **Q4/2026 cơ sở: LNST mẹ ~270 tỷ** (dải 180–365). Thấp hơn mức ~330 Mike ước vì thu nhập tài chính mất ~55 tỷ/quý sau khi chi cổ tức. **Cả năm 2026 cơ sở ~1.390 mẹ / ~1.520 hợp nhất.**
6. **1.600 tỷ nhiều khả năng là LNST HỢP NHẤT, không phải LNST mẹ.** Vietcap ghi "NPAT-MI 1,6tn", nhưng DSC nói 6T đạt 54% kế hoạch: 871/1.600 = 54% khớp với số hợp nhất, còn 797/1.600 chỉ là 50%. Nghị quyết gốc chưa đọc được.
   - Nếu là LNST mẹ: Q4 cần **~481** (khi Q3 = 321), xác suất **~8%**.
   - Nếu là hợp nhất: Q4 cần **~379**, xác suất **~31%**.
7. **2027: cơ sở 1.090 mẹ** (nghịch 740 / thuận 1.900). **2028: cơ sở 1.680** (840 / 2.540). Biến số quyết định duy nhất là khai trường 25/19B. Kịch bản cơ sở giả định quặng nhập 100% trong 2027 và mở lại một nửa trong 2028.
8. **Ba phương pháp hội tụ ở kịch bản cơ sở:**

   | Phương pháp | Giá trị cơ sở (đ/cp) |
   |---|---|
   | SOTP | 32.800 |
   | DCF FCFF (Ke 14,3%, g 3%) | 36.900 |
   | Multiple (PE lịch sử, peer, P/B lõi) | 33.800 |

   Phương pháp không phải nguồn sai số chính; giả định khai trường mới là nguồn sai số chính.
9. **Nghi Sơn GĐ1 ≈ 0 trong giá trị cơ sở** (−100 đ/cp). Giá trị NPV dương (~165 tỷ LNST steady × 7) gần như bị triệt tiêu bởi ~930 tỷ capex còn phải chi. Đây là tuỳ chọn tăng (thuận +2.100 đ/cp), không phải trụ định giá.
10. ⚠️ **WARNING pháp lý** (vụ án hình sự, hạn chế giao dịch, 2 ngoại trừ kiểm toán) được đưa vào định giá dưới dạng haircut tiền 5/15/35% và xoá sổ tồn kho 0–951 tỷ. Chúng không phải cổng chặn. Toàn dải nhạy (haircut 0–50% × tồn kho 0–951) chỉ dịch giá trị cơ sở trong khoảng **25.000–35.200**.

| Kịch bản | XS | LNST mẹ 2026 | 2027 | 2028 | SOTP | DCF | Multiple TB | **Blend** |
|---|---|---|---|---|---|---|---|---|
| Thuận | 0,20 | 1.584 | 1.897 | 2.542 | 54.867 | 53.885 | 53.799 | **54.184** |
| Cơ sở | 0,50 | 1.389 | 1.092 | 1.682 | 32.814 | 36.857 | 33.821 | **34.497** |
| Nghịch | 0,30 | 1.198 | 740 | 841 | 17.340 | 18.926 | 18.969 | **18.412** |
| **Kỳ vọng** | | | | | | | | **33.609** (+4,7% so với 32.100) |

## 1. Dữ liệu đầu vào và kiểm chứng
| Mục | Giá trị | Nguồn |
|---|---|---|
| Giá, số cp | 32.100 (26/10); 379,78 tr cp | BQ `ticker`, `ticker_financial.OShares` |
| LNST mẹ Q1, Q2/2026 | 408,8; 389 (6T 797) | BQ NP_P0 2026Q1; Vietcap flash 22/07; DSC 10/08 (6T 797 khớp) |
| LNST hợp nhất 6T | ~871 | [UL] ACBS Q1 ~430 + Vietcap Q2 440 |
| Cơ cấu Q2/26 | P4 1.572 tỷ (12,9 kt × 4.631 $/t); TPA 516 (17,2 kt × 1.140 $); mảng khác 316 (−65% YoY) | DSC 10/08/2026 (`data/dsc_dgc_q2_2026_extract.txt`) |
| Tiền + tiền gửi 30/06 | 10.921; tiền mặt riêng chỉ 37 | Vietcap/Elibook; DSC |
| Vay | 1.870, toàn bộ ngắn hạn, 0 dài hạn | DSC |
| Cổ tức | 8.000 đ/cp: GDKHQ 14/09, ĐKCC 15/09, **TT 25/09/2026** | doanhnhan.baophapluat.vn 13/09/2026 |
| Tồn kho | 1.681 → 2.460 (+46%) | DSC |
| XDCB Nghi Sơn | 1.221 / tổng GĐ1 2.400 | DSC, Nhadautu 13/08 |
| Kế hoạch 2026 (ĐHĐCĐ 13/08) | DT 10.100; LNST 1.600 | Nhadautu 13/08; Vietcap |
| Lãi suất phi rủi ro | Big4 12T online 6,8% (26/10) | `data/deposit_rate_vn_events.csv` (registry: CANONICAL-PROXY) |
| β | weekly vs VNINDEX: 2y 0,79 / 5y 1,20 → dùng 1,0 | `data/px_multiples.csv` (BQ `ticker`) |
| P4 TQ | 28.296 RMB/t (23/10); TB Q3 ~27.600 | `data/phosphorus_weekly.csv` (SunSirs) |
| Lưu huỳnh | ME FOB ~860–890 $/t (T8–T9); TQ nội địa ~1.330 $/t (DSC) | Argus thứ cấp; DSC |
| Quặng apatit nhập | 152–157 $/t | DSC |
| DAP | TB 2026 729 $/t; T9 800,6 | `data/dap_monthly.csv` (WB CMO) |

**Bẫy dữ liệu phát hiện trong phiên** (đề nghị Winston ghi vào registry):
- `ticker_financial.Cash_P0` của DGC chỉ là tiền mặt (37 tỷ), không gồm tiền gửi có kỳ hạn ~10,9 nghìn tỷ. Hệ quả là **`EVEB` trên BQ (6,2x) bị thổi phồng EV khoảng 10 nghìn tỷ**, không dùng được cho doanh nghiệp giàu tiền gửi.
- `PB`/`BVPS` trên BQ chưa phản ánh cổ tức đã chi sau kỳ BCTC.
- `risk_rating.Beta` là bin (4,0), không phải β số.

**Thu nhập tài chính ~190 tỷ/quý.** Q2 là 194 tỷ trên số dư 10,9–11,9 nghìn tỷ, tức lợi suất năm hoá ~6,5–7,1%. Mức này khớp với lãi suất Big4 12T (6,8%) và Elibook ghi nguồn là lãi tiền gửi, nên đây đúng là lãi tiền gửi, không phải lãi tỷ giá hay đầu tư. Sau khi chi 3.038 tỷ cổ tức, số dư gộp còn ~7.900, nên TNTC Q4 ~130 tỷ (cơ sở). Phần thu nhập này được định giá riêng như tiền mặt, không nhân PE lõi.

**Tồn kho +46% và CFO H1 âm.**
- CFO 6T theo Vietcap là −10 tỷ; theo BQ (CF_OA Q1 −1.093 + Q2 +853) là −240. Hai nguồn lệch nhau, cả hai đều quanh 0 hoặc âm.
- Lý do chính: (i) tồn kho +779 tỷ, gồm quặng nhập tích trữ ("đảm bảo nguyên liệu đến đầu năm sau", Nhadautu 13/08) và P4 tiêu thụ giảm 19,5%; (ii) phải thu +0,7 nghìn tỷ; (iii) Q1 có khoản khắc phục 331 tỷ (KB 07/23).
- Hàm ý cho định giá:
  - Khoảng ~780 tỷ (≈2.050 đ/cp) vốn lưu động là tiền bị giam, có thể thu hồi. Kịch bản cơ sở/thuận cho thu hồi 300 tỷ trong 2027; kịch bản nghịch cho thu hồi 0.
  - Tồn kho nhập giá cao có rủi ro trích lập NRV nếu P4 tiếp tục yếu. Rủi ro này nằm trong bảng nhạy tồn kho.
  - Không coi CFO âm là dấu hiệu mất khả năng tạo tiền của lõi: EBITDA lõi vẫn dương ~300/quý [UL].

## 2. Dự phóng (mô hình theo mảng, `model.py::SCN`)
**Q4/2026** (cầu: DT × biên − BH+QLDN 130 + TNTC trên tiền đã trừ cổ tức − CPTC 25, thuế 13%, CĐKKS 10%):

| | DT | Biên gộp | EBIT lõi | TNTC | LNST hợp nhất | **LNST mẹ** |
|---|---|---|---|---|---|---|
| Thuận | 2.450 | 19,5% | 348 | 145 | 407 | **366** |
| Cơ sở | 2.250 | 16,5% | 241 | 129 | 300 | **270** |
| Nghịch | 2.050 | 13,5% | 147 | 109 | 201 | **181** |

Lý do Q4 cơ sở ≈ Q3 cơ sở (321) trừ ~50:
- P4 đi ngang (T10 28.100–28.300, +2% so TB Q3).
- Lưu huỳnh vẫn cao.
- Quặng nhập 100%.
- TNTC giảm ~55 tỷ.

**2027–2028**, giả định theo mảng (đều [UL] trừ chỗ ghi nguồn; tỷ giá 26.300 hàm ý từ DSC):

| | P4 kt/năm × $/t | TPA kt × $/t | Mảng khác | Biên gộp khi quặng nhập | Khai trường (tỷ lệ năm) 27/28 | Lưu huỳnh | Nghi Sơn LNST 27/28 (steady) |
|---|---|---|---|---|---|---|---|
| Thuận | 58 × 4.400/4.600 | 70 × 1.150 | 1.700 | 18/19% | 0,5 / 1,0 | về 450–500 $/t | 100/200 (280) |
| Cơ sở | 54 × 4.150/4.250 | 68 × 1.100 | 1.400 | 16,5/17,5% | 0 / 0,5 | ~700 → 550 | 30/110 (165) |
| Nghịch | 50 × 3.950 | 66 × 1.050 | 1.200 | 14,5/15% | 0 / 0 | ≥850 kéo dài | −30/50 (70) |

- Lợi ích khi khai trường chạy lại: +1.100 tỷ LN gộp/năm khi chạy đủ [UL]. Cách tính: ~500 kt quặng × (155 − ~60 $/t) × 80% tự cung (DSC).
- Kiểm tra chéo: 2025 LN gộp ~3.800, nay ~1.500–1.800/năm. Khoảng chênh ~2.000 gồm quặng (~1.100), giá lưu huỳnh/than cốc/amoniac và sụt giảm sản lượng/nội địa.
- Nghi Sơn: kịch bản cơ sở dùng DSC (30% công suất 2027, DT ~420) và ước lượng 23/07. 2027 cơ sở chỉ 30, thấp hơn mức 110–130 trong ước lượng tháng 7, vì COD tiếp tục trễ (chưa thấy tin chạy thử T9–T10).

| LNST mẹ | 2026 | 2027 | 2028 |
|---|---|---|---|
| Thuận | 1.584 | 1.897 | 2.542 |
| Cơ sở | 1.389 | 1.092 | 1.682 |
| Nghịch | 1.198 | 740 | 841 |

Ở kịch bản cơ sở 2027, khoảng 25% LNST mẹ là lãi tiền gửi (272/1.092).

**Mục tiêu 1.600:** H1 mẹ 797. Với Q3 cơ sở 321, Q4 cần 481 để đạt nếu 1.600 là LNST mẹ. Xác suất mô phỏng **~8%**: Q3 lấy phân phối từ FORECAST (sd ~82), Q4 sd 85 [UL], tương quan 0,6 [UL].
Nếu 1.600 là LNST hợp nhất (H1 ~871), Q4 cần ~379 hợp nhất; xác suất **~31%**. Tôi nghiêng về cách hiểu hợp nhất (≈ 60/40 [UL]), nên xác suất "đạt kế hoạch như DN công bố" gộp lại khoảng **~20%** [UL].
Mike ước 10–15% trên giả định LNST mẹ, như vậy hơi cao so với ~8% của tôi. Nhưng câu trả lời phụ thuộc chủ yếu vào định nghĩa chỉ tiêu.

## 3. Định giá
### (a) SOTP / EV — tiền tách khỏi lõi
| Cấu phần (đ/cp) | Nghịch | Cơ sở | Thuận | Ghi chú |
|---|---|---|---|---|
| Tiền ròng 30/09 (6.063 tỷ) sau haircut | 10.377 (hc 35%) | **13.569** (hc 15%) | 15.166 (hc 5%) | 10.921 − 3.038 cổ tức + 300 CFO − 250 capex − 1.870 vay [UL Q3] |
| Lõi: LNST mẹ lõi chuẩn hoá (TB 2027–28, đã loại TNTC) × PE lõi | 8.563 (542 × 6) | **19.363** (1.050 × 7) | 37.632 (1.786 × 8) | PE lõi thấp hơn PE trung vị 10y của DGC (8,3, vốn gồm cả lãi tiền) |
| Nghi Sơn: LNST steady × PE, chiết 2 năm, − capex còn lại 929 | −1.600 | **−118** | 2.068 | |
| **Tổng** | **17.340** | **32.814** | **54.867** | |

**Haircut tiền và lý do:**
- (i) Rủi ro truy thu thuế/phí tài nguyên/phạt từ vụ án về khai thác khoáng sản, môi trường và kế toán (DSC), chưa định lượng được.
- (ii) Ngoại trừ kiểm toán "chưa đánh giá được tác động của điều tra".
- (iii) Một phần tiền nằm ở PAT, trong đó 49% thuộc CĐKKS. Phần này chưa tách được nên đưa vào haircut.
- (iv) Quản trị: cổ đông thiểu số không kiểm soát việc dùng tiền (capex GĐ2–3 Nghi Sơn ~9.600 tỷ còn lại của tổ hợp 12.000).
- Mức haircut 15% cơ sở là phán đoán [UL], không có tiền lệ đo được.

### (b) DCF FCFF lõi (gồm Nghi Sơn vận hành)
- Ke = rf 6,8% (Big4 12T) + β 1,0 × ERP 7,5% [UL] = **14,3%**. Không vay dài hạn nên WACC ≈ Ke.
- Dự phóng tường minh 2027–2031, sau đó dùng Gordon. Tái đầu tư ròng = g/RONIC (RONIC 12% [UL]); D&A ≈ capex duy tu [UL]; vốn lưu động thu hồi 300 trong 2027.
- Cộng tiền ròng sau haircut, trừ capex Nghi Sơn còn lại.
- Kết quả: nghịch **18.900** / cơ sở **36.900** / thuận **53.900**.

Nhạy cơ sở theo Ke × g:

| Ke \ g | 1% | 2% | 3% | 4% |
|---|---|---|---|---|
| 12% | 42.812 | 43.041 | 43.271 | 43.500 |
| 13% | 40.142 | 40.153 | 40.121 | 40.032 |
| **14,3%** | 37.272 | 37.099 | **36.857** | 36.525 |
| 16% | 34.270 | 33.960 | 33.569 | 33.078 |
| 18% | 31.508 | 31.119 | 30.651 | 30.086 |

g ít tác động vì có tái đầu tư (RONIC 12% < Ke, nên tăng trưởng gần như không tạo giá trị).

Nhạy theo Ke × biên gộp dài hạn (giữ cố định từ 2027; doanh thu = 2028 cơ sở):

| Ke \ biên | 14% | 17% | 20% | 23% | 26% | 30% |
|---|---|---|---|---|---|---|
| 12% | 29.027 | 33.989 | 38.952 | 43.914 | 48.877 | 55.494 |
| **14,3%** | 25.598 | 29.595 | 33.593 | 37.590 | 41.587 | 46.917 |
| 18% | 22.272 | 25.333 | 28.395 | 31.457 | 34.518 | 38.601 |

**Mỗi 3pp biên gộp ≈ 4.000 đ/cp**, nên biên gộp là biến nhạy nhất. Ở Ke 14,3%, giá 32.100 tương đương biên dài hạn ~19%. Mức này nằm giữa "quặng nhập" (15–17%) và "khai trường chạy lại" (~23%+). Lịch sử: 2023–25 khoảng 32–37% (BQ GPM, có đỉnh P4), 2026 khoảng 16–19%.

### (c) Multiple
- **PE lịch sử DGC** (BQ `ticker.PE`, 10 năm): phân vị 10/25/50/75/90 = 5,0 / 6,7 / **8,3** / 12,5 / 15,5. Theo năm: 2019 5,8; 2023 5,0; 2024 14,4; 2026 7,0. DGC định giá ở 5–6x tại đáy lợi nhuận và 12–15x khi kỳ vọng tăng.
- **Peer** (BQ, 26/10):

  | | BFC | CSV | DCM | DDV | DPM | LAS |
  |---|---|---|---|---|---|---|
  | PE hiện tại | 12,6 | 9,9 | 7,2 | 6,4 | 8,3 | 15,2 |

  Trung vị hiện tại **9,1**; trung vị PE 10 năm **10,5**. PAT 5,2x bị loại vì là công ty con. Lưu ý DPM/DCM cũng giàu tiền, nên so PE gộp với gộp.
- Áp lên LNST mẹ chuẩn hoá (TB 2027–28, gồm lãi tiền gửi):

  | | PE DGC 8,3 | PE peer 10y 10,5 | P/B lõi chính đáng = (ROE lõi − g)/(Ke − g) × VCSH phi-tiền + tiền sau haircut |
  |---|---|---|---|
  | Cơ sở | 30.459 | 38.165 | 32.838 (ROE lõi 14,1%, P/B lõi 0,98) |
  | Nghịch | 17.360 | 21.751 | 17.796 |
  | Thuận | 48.741 | 61.072 | 51.584 |

- PB 2,8x trung vị 5 năm không dùng vì thuộc chế độ ROE 25–40% của thời có quặng tự chủ, chế độ đó đã mất.
- EV/EBITDA trên BQ bị loại (xem bẫy `Cash_P0` ở mục 1).

### Đối chiếu
Ba phương pháp cơ sở nằm trong khoảng 32,8–36,9k. DCF cao nhất vì (i) giá trị kết thúc vốn hoá trên năm 2028 (đã mở lại một nửa khai trường) thay vì TB 2027–28, và (ii) có thu hồi vốn lưu động. Độ phân tán giữa kịch bản (18–54k) lớn gấp ~9 lần độ phân tán giữa phương pháp (~4k).

## 4. Rủi ro và WARNING pháp lý
⚠️ **WARNING** (luật user 27/09/2026: phân tích bình thường, ghi rõ nguồn và ảnh hưởng, không tự hạ kết luận hay loại mã):
- **Vụ án hình sự:** khởi tố từ cuối 2025 về khai thác khoáng sản, môi trường, kế toán; T3/2026 áp dụng biện pháp tố tụng với lãnh đạo; cuối T7 có thêm thông báo với nhân sự chủ chốt (DSC 10/08). Cựu Chủ tịch Đào Hữu Huyền bị khởi tố (Nhadautu 13/08). ĐHĐCĐ bất thường 08/05 miễn nhiệm 3 thành viên HĐQT.
  - Ảnh hưởng đã biết: **khai trường 25 + 19B (80% quặng tự cung) dừng**, đây chính là biến số quyết định của định giá. Có thể có truy thu/phạt, nằm trong haircut tiền.
- **HOSE:** cảnh báo từ 23/04; kiểm soát từ 13/05 (ra khỏi VN30); **hạn chế giao dịch từ 26/05/2026** (BCTC kiểm toán chậm), khớp lệnh định kỳ. CafeF 04/07: vẫn hạn chế. Trạng thái sau T8: **chưa xác minh**.
  - Ảnh hưởng: thanh khoản và chiết khấu bội số. PE lõi 6–8 thấp hơn PE lịch sử là một phần vì lý do này.
- **BCTC 2025 (UHY) có 2 ý kiến ngoại trừ:** (1) chưa chứng kiến kiểm kê tồn kho ~951 tỷ; (2) chưa đánh giá được tác động của điều tra (Elibook). Soát xét bán niên 2026: nguồn thứ cấp không nêu ngoại trừ, **chưa đọc bản gốc**.
  - Ảnh hưởng: bảng nhạy SOTP cơ sở dưới đây.

| SOTP cơ sở | tồn kho −0 | −475 | −951 tỷ |
|---|---|---|---|
| haircut tiền 0% | 35.209 | 34.121 | 33.031 |
| 15% | 32.815 | 31.727 | 30.636 |
| 30% | 30.420 | 29.332 | 28.242 |
| 50% | 27.227 | 26.139 | 25.049 |

Rủi ro khác:
- Ưu đãi thuế: thuế hiệu dụng 13% có thể hết ưu đãi; lên 20% thì giá trị lõi giảm ~8% [UL].
- Capex GĐ2–3 Nghi Sơn có thể dùng tiền với RONIC thấp hơn Ke.
- Giá P4 phụ thuộc điện mùa khô ở Vân Nam.
- Không có giá mục tiêu CTCK nào sau tháng 7. DSC 10/08 cho 41.000 trên giá 44.200 trước cổ tức; trừ 8.000 cổ tức thì tương đương ~33.000, khớp với kịch bản cơ sở ở đây.

## 5. Phản biện ước lượng sơ bộ của Mike
- **"Q4 ~330, cả năm ~1.450 mẹ":** Q4 cơ sở là 270, vì sau cổ tức 25/09 TNTC giảm ~55/quý. Cả năm cơ sở 1.389.
- **"PE 8–9x":**
  - PE 8–9 trên LNST 2026 vừa gồm lãi tiền gửi (định giá tiền ở 8–9x lợi nhuận tức là trả ~1,2–1,3 đồng cho 1 đồng tiền), vừa dùng một năm không chuẩn hoá. Tách ra thì lõi đáng ~7x.
  - 2027 cơ sở (1.090) THẤP hơn 2026 vì TNTC giảm và quặng vẫn nhập. Nếu dùng PE × LNST 2027 cơ sở thì chỉ được ~24–26k (EPS 2.875 × 8,3–9).
  - Giá trị 34k cơ sở chỉ đứng được khi tính cả khả năng mở lại khai trường một nửa trong 2028.
- **"30–34k nếu ~1.450":** khớp về con số, nhưng lý do khác. Giá hợp lý là ~33–35k không phải vì LNST 2026, mà vì tiền ~13,6k/cp (sau haircut) + lõi ~19k/cp.

## 6. Điểm yếu nhất của định giá này (đổi kết luận nhiều nhất)
1. **Thời điểm và quy mô khai trường mở lại.** Đây là toàn bộ chênh lệch giữa nghịch (18k) và thuận (54k). Kịch bản cơ sở "0 trong 2027, một nửa trong 2028" là phán đoán; không có nguồn nào cho mốc thời gian. Lợi ích +1.100 tỷ/năm cũng là [UL] (định mức quặng/P4, chi phí khai thác tự có ~60 $/t chưa xác minh).
2. **Tiền ròng 30/09 là số dựng lại** (CFO và capex Q3 [UL] ±500 tỷ ≈ ±1.300 đ/cp). Ngoài ra chưa tách được tiền của PAT (49% CĐKKS). BCTC Q3 (sắp công bố) sẽ sửa trực tiếp điểm này.
3. **Trọng số kịch bản 0,2/0,5/0,3 mượn từ FORECAST Q3**, không được hiệu chỉnh cho câu hỏi khai trường. Đổi sang 0,3/0,5/0,2 thì kỳ vọng = 37.200 (+16%).
4. **Biên gộp khi nhập quặng 16–17% dựa trên 2 quý** (Q2 18,9%, Q3 dự báo 16%). Không có số liệu biên theo mảng; giá lưu huỳnh theo 2 nguồn lệch nhau (ME FOB ~870 vs TQ ~1.330 $/t). ±3pp biên ≈ ±4.000 đ/cp.
5. **Định nghĩa chỉ tiêu 1.600 chưa đọc từ Nghị quyết gốc.** Bằng chứng duy nhất là phép chia của DSC. Điểm này đổi xác suất "đạt kế hoạch" từ 8% sang 31%, nhưng không đổi giá trị nội tại.

## Nguồn
- BQ `tav2_bq.ticker`, `ticker_financial`, `risk_rating` (query 27/10/2026 ~00:20 ICT) → `data/*.csv`.
- DSC cập nhật Q2/2026 (10/08/2026): https://extgw.dsc.com.vn/eback/uploads/BCCN_DGC_Q2_2026_f4ec47b822.pdf → `data/dsc_dgc_q2_2026_extract.txt`.
- Vietcap flash/AGM 22/07/2026: https://www.vietcap.com.vn/en/research-center/dgc-h1-2026-npat-mi-falls-52-yoy-on-weaker-volumes-cost-pressure-2026-agm-guidance-implies-downside-risk-earnings-flash-agm-documents-note
- ĐHĐCĐ 13/08: https://nhadautu.vn/dgc-dat-ke-hoach-loi-nhuan-giam-gan-mot-nua-nguon-quang-tro-thanh-bien-so-d106952.html
- Cổ tức: https://doanhnhan.baophapluat.vn/lich-chot-quyen-co-tuc-tuan-14-18-9-hoa-chat-duc-giang-duoc-hau-giang-habeco-cung-thanh-toan-ty-le-cao-nhat-120.html
- HOSE: https://vietnamfinance.vn/co-phieu-dgc-thoat-canh-chi-giao-dich-phien-chieu-d145103.html ; Elibook https://elibook.vn/2026/09/08/dgc-loi-nhuan-quy-2-roi-hon-nua-kiem-toan-ngoai-tru-va-ghe-chu-tich-doi-nguoi-nhung-khong-doi-ho/
- Q3 forecast khoá: `../dgc_q3_forecast_20261026/FORECAST.md` (md5 d6ea39f4…, không sửa). Nghi Sơn: `../dgc_nghison_phase1_estimate_20260723.md`.
- BCTC gốc Q2/bán niên 2026 và Nghị quyết ĐHĐCĐ: **chưa đọc được bản gốc**. Mọi số bảng cân đối ở đây là nguồn thứ cấp có ghi nguồn.
