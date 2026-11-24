# SIP — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110052, nhóm g2)

Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + phụ lục `../PREREG_adj_v2.md` (md5 `835dfc1e…`), cả hai assert trong `calc_adj.py`. Chạy 2 lần: run1 = run2 (md5 `3bca2f15…`). Output `adj.json`.
- Tâm gốc = sổ **rev4, 54.466 đ/cp** (sau CK 1,39% @5 tỷ; `skeptic_final` = REFUTED_OPEN).
- **Σ tuyến tính = +5,13% > 5%** ⇒ theo v2 §5 phải chạy lại mô hình. Đã chạy lại nguyên `model_r3.py` của sổ rev4, theo **tổ hợp** 2⁴ = 16 tập hạng mục (mỗi hạng mục là Bernoulli độc lập với xác suất p).
  - Chạy trên bản sao tạm của mirror, md5 khớp LOCK r3. CONTROL: tái lập đúng 54.466.
  - Tổ hợp = 57.261, trùng tuyến tính. Lý do: bốn trục đều vào mô hình theo dạng cộng, không có tương tác đáng kể.
- Mù giá: chỉ lấy `center_post`. Không đọc/in giá, nhãn, tỷ lệ "dưới giá" hay "giá ngụ ý" của mô hình.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 57.261 đ/cp (+5,13% so với 54.466). Dải (cực trị p × m, tổ hợp): 55.818–59.340.**
- Không ghi nhận quyền chưa chốt trong nguồn: cổ tức 9T26 968,5 tỷ đã công bố và đã trả ⇒ một dòng.
- Chiều tăng đến chủ yếu từ #1 VAT: áp luật "base = sổ sách" cho cả hai chiều. Trước đây tạm ứng 643,7 tỷ được vào base theo sổ, còn VAT khấu trừ thì bị để ngoài.
- Rủi ro xuống lớn nhất chưa vào tâm là **G16 tiền thuê đất** (100 tỷ/năm ⇒ −5,83%). Chưa vào tâm vì không biết SIP trả một lần hay hằng năm, nên cận bảo thủ = 0.
- G16 là sự kiện đổi số quan trọng nhất (§4). Nếu thuyết minh cho thấy trả hằng năm ~100 tỷ, tâm về ≈ 54.085, tức ngang tâm gốc.

## 1. Hạng mục vào tâm (A/B)
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | VAT khấu trừ 890,5 − DTL 123,7 tỷ (sổ sách) | ↑ | +5,73 [+5,73; +6,66] | A | 0,90 [0,75; 1,00] | +5,16 | assumptions_r3 `vat_minus_dtl_ty`; r1_raw:32 |
| 2 | NCI công ty con 20% (giữa trục) → 9,9% (CĐKT) | ↑ | +3,19 [+3,19; +3,63] | B | 0,50 [0,25; 0,75] | +1,59 | `nci_bs_9_9`; model `nci_profit` 8,5%; r1_raw:33 |
| 3 | Đất cho thuê 9T26 đếm hai lần (vẫn nằm trong 937,1 ha) | ↓ | −1,67 [−0,60; −1,83] | B | 0,50 [0,25; 0,75] | −0,83 | notes_read TM21:56; r1_raw:23 |
| 4 | Chuẩn hoá biên gộp vận hành ×0,9457 | ↓ | −2,26 [−1,88; −2,26] | B | 0,35 [0,15; 0,55] | −0,79 | `gpm_peak_normalisation`; `sip_gpm_bq.csv` |
| | **Σ (tuyến tính = tổ hợp)** | | | | | **+5,13** | |

Lý do chọn p và m:
- **#1 (A):** số đọc thẳng từ CĐKT. Không hạ p, vì VAT khấu trừ được thu hồi qua VAT đầu ra từ hoạt động cho thuê đất. Hai mức m:
  - +5,73%: trừ DTL;
  - +6,66%: nếu DTL trùng với `taxdef` (chưa đọc thuyết minh).
- **#2 (B, 1 kỳ):** CĐKT và LN 9T cùng kỳ 30/9 nên tính là 1 quan sát. Hai mức m: 9,9% theo sổ; 8,5% theo tỷ trọng LNST. Đổi tỷ lệ sổ sang tỷ lệ giá trị là suy luận, nên xếp B.
- **#3 (B, 1 kỳ):** chắc chắn có đất cho thuê trong 9T26 (DT chưa thực hiện +1.701,8 tỷ). m có ba mức:
  - 60 ha (skeptic);
  - 21,5 ha (cận bảo thủ = tốc độ 2025 là 28,6 ha/năm × 0,75 năm);
  - 66 ha.
- **#4 (nhánh ngược 0,35):** 6/7 năm 2019–25 có GPM thấp hơn TTM 15,7% (BQ). Quan sát ngược có số: năm 2021 đạt 16,7%, và xu hướng từ 2022 đến TTM đi lên (13,5% → 15,7%). Cận nhỏ của m = FY25/TTM.

## 2. Chỉ độ nhạy (C / luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| **G16 tiền thuê đất Nhà nước** | ↓ | −318 đ/cp mỗi 10 tỷ/năm (−0,58%); 100 tỷ/năm: −3.176 (−5,83%); cận trên dữ liệu 141 tỷ/năm (toàn bộ giá vốn mảng đất quy năm): −4.488 (−8,24%) | Trả một lần (đã nằm trong chi phí đất) ⇒ 0. Không biết hình thức trả ⇒ cận = 0 ⇒ C |
| 12 tỷ/ha ròng không có nguồn (~36% tâm) | ↕ | Trục ×0,75 cố định: −3.543; ×1,25: +3.543 | Không có giao dịch hay biên cho thuê lại để định hướng |
| Tín dụng 6.016 tỷ, bên vay G1/G2 chưa định danh | ↕ | Trục tổn thất 0/10/30% đã có trong lưới (−1.255) | Hai chiều (EY không trích dự phòng) |
| Tạm ứng nội bộ 643,7 tỷ | ↓ | Bỏ khỏi base: −826; mất trọn ở p 0,15: −517 | Không có dữ liệu tổn thất; base = sổ sách, đối xứng với #1 |
| Tài sản sổ sách 396,8 tỷ đọc từ ảnh scan | ↕ | ±1.616 | Chưa đối chiếu bản text |
| D3 hạ tầng môi trường 937 ha | ↓ | ≈ 0 | Theo định nghĩa, 12 tỷ/ha đã là số ròng sau hạ tầng |
| [LUẬT] r vs dải Ke (E15) | ↑ | Ke 12,3%: 57.744 (+6,02%); Ke 13,4%: +0,47% | Tham số luật V1 |
| [LUẬT] RONIC = Ke cho mảng vận hành | ↑ | RONIC = ROE5Y: +3.389 (+6,22%) | Luật V5/D4 (skeptic: thu nhập dịch vụ từ khách thuê mới) |

## 3. Không đếm hai lần
- **#3 và trọng số đất:** DT chưa thực hiện +1.701,8 tỷ đã được dùng ở r3 để đặt trọng số tốc độ bán (25/50/25). #3 là hiệu chỉnh cơ học khác: bỏ số ha đã cho thuê ra khỏi quỹ đất còn lại. Một số liệu, hai cơ chế khác nhau, không cộng chồng cùng một dòng tiền.
- **#1 VAT và tạm ứng:** VAT vào base theo sổ; tạm ứng giữ nguyên theo sổ (r3). Rủi ro mất tạm ứng chỉ nằm ở mục độ nhạy (C).
- **#4 GPM và RONIC:** #4 điều chỉnh mức lợi nhuận vận hành hiện tại. RONIC là luật tăng trưởng. Hai thứ tách nhau.
- **r / dải Ke / E15:** một dòng luật.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 54.466. Lịch công bố là ước lượng, chưa xác minh với CBTT của SIP.

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| **BCTC năm 2026: thuyết minh thuê đất (G16) — trả hằng năm** | ước lượng 03/2027 | C → A | −318 mỗi 10 tỷ/năm (100 tỷ ⇒ −3.176) | −0,58 mỗi 10 tỷ |
| Thuyết minh G16 — trả một lần | ước lượng 03/2027 | Đóng hạng mục | 0 | 0 |
| Thuyết minh VAT: khấu trừ/hoàn được | ước lượng 03/2027 | p#1 → 1,0 (DTL trùng ⇒ m +6,66%) | +312 | +0,57 |
| Thuyết minh VAT: không thu hồi được | ước lượng 03/2027 | p#1 → 0 | −2.811 | −5,16 |
| NCI từng công ty con (G14) ≈ tỷ lệ sổ | BCTC năm 2026 | p#2 → 0,9 | +694 | +1,27 |
| Số ha cho thuê 9T26/FY26 công bố (G12) | CBTT / BCTN 2026 | m#3 theo số chính thức, p → 0,9 | −15 mỗi ha | −0,03 mỗi ha |
| GPM Q4/2026 ≥ 15,5% | ước lượng cuối 01/2027 | p#4 → 0,15 | +246 | +0,45 |
| GPM Q4/2026 < 14,6% | ước lượng cuối 01/2027 | p#4 → 0,65 | −368 | −0,68 |
| Bên vay G1/G2 là bên liên quan | khi có | Trọng số tổn thất 0% giảm (C → B); WARNING | theo số | — |
| Giá/biên cho thuê lại gần đây được công bố | CBTT | Thay giả định 12 tỷ/ha | ×0,75: −3.543 / ×1,25: +3.543 | ∓6,5 |
| Lãi huy động 12T ±50bp (V1, β = 1) | liên tục | r | +50bp: −1.222 / −50bp: +1.303 | −2,24 / +2,39 |
| BCTC Q3 HN soát xét / kiểm toán năm | ước lượng 03/2027 | Đối chiếu sổ (396,8 tỷ ảnh scan) | ±1.616 | ±2,97 |

Kịch bản gộp (chỉ minh hoạ, tuyến tính, KHÔNG phải tâm):
- Chiều xấu: G16 trả hằng năm 100 tỷ, VAT không thu hồi được, GPM về trung bình ⇒ ≈ 57.261 − 3.176 − 2.811 − 368 ≈ 50.906.
- Chiều tốt: G16 trả một lần, VAT xác nhận, NCI xác nhận, GPM giữ ⇒ ≈ 57.261 + 312 + 694 + 246 ≈ 58.513.
