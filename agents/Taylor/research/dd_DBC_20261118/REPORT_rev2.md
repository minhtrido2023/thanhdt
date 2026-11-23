# DD — DBC (CTCP Tập đoàn Dabaco Việt Nam, HOSE) · REV 2 · dựng 23/11/2026 · job `Taylor_20261123_050005` (tiếp job `Taylor_20261123_003456`)

> **Khoá giả định:** `rev2/assumptions_DBC_rev2.json`, **assumptions_md5 = `25d2e3059aa88705be3605ba500f9369`**. `bin/dd_assumptions_lint.py` trả 0 vi phạm. File khoá **không chứa giá thị trường**: trường `price_for_comparison_only` của rev1 đã bỏ.
> **Mô hình:** `rev2/calc_rev2.py` (md5 `ea3b5012…`), đầu ra `rev2/calc_rev2_output.txt` (md5 `cbf5855e…`). Mốc §9: `rev2/calc_rev2_milestones.py` → `calc_rev2_milestones_output.txt`. Mọi số trong báo cáo lấy từ hai file đầu ra này, trừ khi ghi nguồn khác.
> **Bản trước:** `REPORT.md` (rev1 ngày 18/11, tâm 19.491, vùng 11.314–27.270, assumptions_md5 `207da8c9…`). Phản biện bản trước: `skeptic/r1.json`, kết quả INCONCLUSIVE.
> **Mù giá:** giả định khoá xong mới đọc giá (DNSE, §6). Hạn chế đã biết: giá rev1 (16.950 ngày 17/11) có trong bản rev1 nên người dựng đã thấy trước. Các lựa chọn mới của rev2 đều **khai theo luật cơ học, chọn trước khi chạy**: cửa sổ (§2), tỉ lệ k (§3), cách tính XDCB (§4). Dù vậy, chiều lệch này không loại trừ được hoàn toàn (§10).

## 0. Kết luận

- **Tâm = 17.317 đ/cp.** Đây là giá trị kỳ vọng có trọng số 25/50/25 của ba kịch bản, đã trừ 2% chiết khấu thanh khoản. **Vùng [9.906; 24.478]**. Trước chiết khấu thanh khoản: tâm 17.670. Riêng kịch bản cơ sở: 17.442 (sau chiết khấu).
- **So rev1 (19.491): giảm 11,2%.** Ba thay đổi gây ra mức giảm:
  - (i) Trừ quỹ khen thưởng phúc lợi và thù lao HĐQT. Tỉ lệ trích k = 11,06% LNST, đo từ BCTC kiểm toán 2021–2025. Riêng bước này kéo tâm −15%.
  - (ii) Tâm lấy trung bình của **ba cửa sổ khai trước** (12, 15 và 20 quý), không dùng riêng cửa sổ 15 quý.
  - (iii) XDCB được trừ khỏi mẫu số **theo từng quý lịch sử**, thay vì một tỉ lệ hiện tại duy nhất.
- **Giá 16.200 (DNSE, 23/11/2026 11:29) = 0,94× tâm ⇒ quanh giá trị hợp lý, KHÔNG rẻ.** Cổng 0,85×tâm = 14.719, chưa đạt.
- **Độ bất định lớn, cả hai chiều. Tâm là trung bình của các cách nhìn chu kỳ, không phải một con số chắc:**
  - Theo cửa sổ: chỉ dùng 12 quý cho 23.493 (+35,7%); chỉ dùng 20 quý cho 11.573 (−33,2%).
  - Nếu XDCB cũng sinh lời bằng ROE lịch sử (không tách ra): 12.384 (−28,5%).
- **Kiểm toán:** BCTC hợp nhất 2025 do EY kiểm toán, ý kiến chấp nhận toàn phần (`src/kt25_hopnhat_vi.pdf`). LNST 2021–2025 trong BQ khớp BCTC kiểm toán, **trừ năm 2022**. Năm 2022, kiểm toán điều chỉnh giảm 144,9 tỷ ở Q4; rev2 đã sửa theo số kiểm toán.
- **Pháp lý: chỉ WARNING.** Phải thu người lao động 237,1 tỷ (giữ nguyên từ rev1 §7). Nếu mất trắng: −539 đ/cp. Khoản này không vào base.
- **Sizing (V8):** nếu vào vị thế, mức chuẩn là 2–4% NAV/mã. Ở giá hiện tại, tôi **không đề xuất mua** vì cổng 0,85 chưa đạt.

## Đính chính so với rev trước (từng hạng mục skeptic r1 → xử lý)

| # | Hạng mục skeptic r1 | Bằng chứng mới (nguồn) | Xử lý trong rev2 | Ảnh hưởng lên tâm |
|---|---|---|---|---|
| 1 | Thiếu quỹ KTPL (đòn 8, "trọng yếu, chưa định lượng") | Trích KTPL theo năm lợi nhuận, tỉ đồng: LN2021 → 47,49 (KT23 TM20); LN2022 → 0 (KT23 TM20); LN2023 → 0 (KT25 TM23); LN2024 → 200 + thù lao 3,835 (H1/26 TM25.1, kỳ trước); LN2025 → 88 + thù lao 7,52 (NQ ĐHĐCĐ 01/2026, TM25.1). LNST kiểm toán 2021–25: 829,56 / 5,19 / 25,01 / 769,08 / 1.506,77 | **(a) vào base:** k = 346,85 / 3.135,61 = **11,06%**, nhân (1−k) vào ROE cho cổ đông. Số dư quỹ đã là nợ phải trả (mã 322), nên không trừ lần nữa | −15% so với k=0. Độ nhạy: k 6,3% → 18.624; 13,0% → 16.785; 26,5% → 13.081 |
| 2 | Thiếu BCTC kiểm toán 2025 và ý kiến kiểm toán | Đã tải BCTC hợp nhất kiểm toán 2022, 2023, 2024, 2025 về `src/` | 2025: EY, chấp nhận toàn phần. **Sửa Q4/22** theo số kiểm toán: −224,0 thay cho −79,1 của BQ. Vốn chủ cuối 2021 và cuối 2022 lấy từ BCTC kiểm toán (BQ 2021Q4 = 2.348 sai do số cổ phiếu trước chia tách) | Chỉ ảnh hưởng cửa sổ 20 quý |
| 3 | Chưa đo lịch sử XDCB/vốn chủ (cách cộng 31% chỉ đúng nếu XDCB từng ≥15% vốn) | Mã 242, tỉ đồng: 31/12/21 467,9; 31/12/22 1.397,7; 31/12/23 475,7; 31/12/24 1.083,5; 31/12/25 1.750,0; 30/9/26 1.302,6 (BCTC kiểm toán + Q3) | **(a)** Mỗi quý tính ROE_op = 4×LNST / (vốn chủ − XDCB của chính quý đó). Các quý giữa nội suy tuyến tính, là **ước lượng**. XDCB/vốn trung bình: 20 quý 18,0%, 15 quý 17,4%, hiện tại 14,9% ⇒ **điều kiện ≥15% thoả** | Nội suy so với bậc thang: −3,8%. Kiểm tra: ở cửa sổ 15 quý, rev2 cho ROE_op 13,58%, cách tính rev1 cho 13,43% (gần nhau) |
| 4 | Tâm phụ thuộc cửa sổ chọn sau khi thấy giá (biên −20%/+35%) | — | **Khai trước luật:** tâm = trung bình đều ROE_op của 12, 15 và 20 quý kết thúc ở quý BCTC mới nhất. Từng cửa sổ chỉ là độ nhạy, nêu ở §0 | 12q: +35,7% · 15q: −2,5% · 20q: −33,2% |
| 5 | BQ ROE3Y 11,44% không phải bằng chứng độc lập | Đồng ý | Bỏ câu "xác nhận độc lập". Đối chiếu duy nhất còn giữ: LNST năm BQ khớp BCTC kiểm toán | — |
| 6 | 647 tỷ lỗ tính thuế chưa ghi tài sản thuế hoãn lại; XDCB bị haircut ở kịch bản xấu mà kịch bản tốt không có phần tăng tương ứng | TM 31.4 BCTC bán niên 2026 | **(b) chỉ ở kịch bản tốt:** lá chắn thuế 647 × 20% = 129,4 tỷ. Haircut 40% XDCB trại heo vẫn ở kịch bản xấu, vì có cơ sở độc lập (Bobby: làn sóng mở trại). Không cộng thêm phần tăng XDCB vì không có cơ sở độc lập | Kịch bản tốt +300 đ/cp (tâm +75) |
| 7 | Chi tuân thủ môi trường cho 6 trại | Tìm trên dabaco.vn và TM nợ tiềm tàng KT25: không thấy quyết định xử phạt hay nghĩa vụ chi | **(c) không kiểm chứng được.** Không đưa vào base, vì D3 yêu cầu có nguồn mới được trừ. Độ nhạy chi một lần 50–150 tỷ (ước lượng) | −116 đến −348 đ/cp (−0,7% đến −2,0%) |
| 8 | ESOP / phát hành theo NQ ĐHĐCĐ 2026 | Biến động vốn H1/26 (TM25.1) chỉ có cổ tức cổ phiếu 12% và tiền mặt 3%. Vốn điều lệ 30/9 = 4.310,46 tỷ = 431,05 triệu cp. Tìm "ESOP" trên dabaco.vn chỉ ra đợt 2024 (120 tỷ, đã nằm trong số cổ phiếu) | **(c) không kiểm chứng được đầy đủ** (chưa đọc toàn văn NQ 2026). Độ nhạy pha loãng 1–3% ở mệnh giá | tâm 17.243 đến 17.098 (−0,4% đến −1,3%) |

## 1. Nguồn số liệu và đối chiếu

- **LNST theo quý:** BQ `ticker_financial.NP_P0`. Đối chiếu tổng năm với dòng 60 của BCTC kiểm toán:
  - 2021: 829,56 — khớp.
  - **2022: 5,19 theo kiểm toán, BQ cộng 150,1 ⇒ lệch 144,9, đã sửa vào Q4/22.**
  - 2023: 25,01; 2024: 769,08; 2025: 1.506,77 — khớp.
  - H1/26 = 663,16 và Q3/26 = 200,17 khớp BCTC (rev1 §1).
- **Vốn chủ công ty mẹ theo quý:** chuỗi rev1 (BVPS × số cổ phiếu từ BQ, đã sửa 2 điểm), cộng thêm 2021Q4 = 4.685,9 và 2022Q4 = 4.641,2 lấy từ BCTC kiểm toán.
- **XDCB:** các mốc năm lấy từ BCĐKT kiểm toán. Các quý giữa là nội suy (ước lượng), có độ nhạy bậc thang.

## 2. Chuẩn hoá ROE — luật khai trước

- **Định nghĩa:** ROE_op của quý = 4 × LNST quý / (vốn chủ mẹ cuối quý − XDCB cuối quý). XDCB được ghi theo sổ sách với NPV = 0 (V4a).

| Cửa sổ | Quý | ROE toàn vốn | ROE_op (nội suy) | ROE_op (bậc thang) |
|---|---|---|---|---|
| W12 | Q4/23–Q3/26 | 14,32% | 17,33% | 16,84% |
| W15 | Q1/23–Q3/26 | 11,42% | 13,58% | 13,33% |
| W20 | Q4/21–Q3/26 | 9,03% | 10,57% | 10,19% |
| **Tâm = trung bình đều** | | | **13,83%** | 13,45% |

- **Vì sao dùng ba cửa sổ:**
  - W12 bỏ quý lỗ Q1/23 và đáy 2022. Nó chỉ chứa đỉnh 2024–25.
  - W20 chứa cả đáy 2022–23 nhưng thiếu đỉnh ASF 2020.
  - W15 nằm giữa.
  - Không cửa sổ nào là "đúng chu kỳ". Lấy trung bình đều là cách không phải chọn sau.
- **Kiểm tra mức hợp lý:** LNST chuẩn hoá = 1.025,7 tỷ/năm, tức EPS 2.380 đ (2.116 đ sau KTPL). Mức này nằm giữa LNST 2024 (769) và 2025 (1.507).

## 3. Quỹ khen thưởng phúc lợi

- **Tỉ lệ trích k = 11,06% LNST** (gồm KTPL và thù lao HĐQT/BKS), luật **gộp 5 năm lợi nhuận 2021–2025**, khớp cửa sổ W20.
- **Phân bố theo năm lệch mạnh:** 5,7% / 0% / 0% / 26,5% / 6,3%. Năm 2024 trích 26,5% (200 tỷ) sau hai năm không trích. Cách gộp nhiều năm hấp thụ hiện tượng "trích bù" này.
- **Thù lao từ lợi nhuận 2021–2023 chưa đọc được**, nên k có thể thấp hơn thực tế một chút.
- **Trong mô hình:** ROE cho cổ đông = ROE_op × (1 − k) = 12,30%.

## 4. XDCB (dự án tăng trưởng)

- XDCB 30/9/2026 = 1.302,6 tỷ, trong đó trại heo 873,4 tỷ (TM 8 Q3).
- **Base:** ghi theo sổ sách, NPV = 0 (V4a). Phần vốn chủ còn lại (7.417,8) sinh ROE_op.
- **Kịch bản xấu:** haircut 40% XDCB trại heo, dải 30–50%.
- **Biến thể "toàn vốn"** (XDCB cũng sinh ROE lịch sử, không tách riêng): ROE 11,59%, tâm 12.384. Đây là cận dưới nếu giả định XDCB không bao giờ tạo lợi nhuận vượt mức lịch sử.

## 5. Bảng cân đối, dòng tiền, V6 (chỉ hiển thị)

- CFO trung bình 1.133,3 tỷ/năm. Capex (gồm thuê tài chính) 1.178,7 tỷ/năm. **FCFE ≈ −45,5 tỷ/năm ⇒ V_dài không xác định.** Chỉ báo V_ngắn.
- **V_ngắn = 12.998 đ/cp.** Tỉ lệ tái đầu tư g/ROE = 0,478, với ROE toàn vốn sau KTPL 10,46%.
- FCFE âm do capex tăng trưởng (trại heo, nhà máy ép đậu), không phải dấu hiệu đắt (§E8).
- **Không tính được chênh lệch D giữa hai nền**, nên không có cờ D>ln2. Luật 0,85×tâm không bị đình chỉ bởi cờ, nhưng tâm cũng không được trộn với V_ngắn.
- Dòng C4/D2 của rev1 giữ nguyên nhãn "chưa qua tiêu chí khoá trước, chỉ theo dõi".

## 6. Định giá

### 6a. Khung

- **Mô hình thu nhập thặng dư trên vốn chủ:** V = (vốn chủ − XDCB) × (ROE_op×(1−k) − g)/(r − g) + XDCB − haircut + lá chắn thuế (chỉ kịch bản tốt).
- **Tham số:**
  - Vốn chủ mẹ 30/9 = 8.720,4 tỷ; 431,05 triệu cp.
  - r = 13,5%; g = 5%.
  - Kịch bản ±3,25 điểm % ROE toàn vốn, tương đương ±3,82 điểm % ROE_op.
- **V1 — chi phí vốn r:**
  - r = 13,5%, neo lãi huy động 12 tháng hiệu dụng 7,4% (`deposit_rate_vn`, CCTG 12T ngày 02/11). Ngày 18/11 và 23/11 vẫn 7,4% ⇒ Δ = 0, β = 1.
  - Độ nhạy:

    | Lãi huy động | r | Tâm (β = 1) | β = 0,5 |
    |---|---|---|---|
    | −100bp | 12,5% | 19.248 (+11,1%) | 18.222 (+5,2%) |
    | −50bp | 13,0% | 18.222 (+5,2%) | 17.756 (+2,5%) |
    | +50bp | 14,0% | 16.513 (−4,6%) | 16.903 (−2,4%) |
    | +100bp | 14,5% | 15.793 (−8,8%) | 16.513 (−4,6%) |

  - **Dải Ke nội địa (D4):** Ke 12,3% cho tâm 19.697; Ke 13,4% cho 17.489.
- **g:** 4% cho 17.568; 6% cho 16.999.

### 6b. Kịch bản

| Kịch bản | p | ROE_op | Giá trị trước chiết khấu thanh khoản | Ghi chú |
|---|---|---|---|---|
| Xấu | 25% | 10,01% | 10.108 | haircut 40% XDCB trại heo |
| Cơ sở | 50% | 13,83% | 17.798 | |
| Tốt | 25% | 17,65% | 24.978 | + lá chắn thuế 129,4 tỷ |
| **Kỳ vọng, sau chiết khấu 2%** | | | **17.317** | vùng [9.906; 24.478] |

- **Đổi trọng số:** 35/50/15 cho 15.860 (−8,4%); 15/50/35 cho 18.774 (+8,4%).

### 6c. V3 — thanh khoản

- Chiết khấu 2% (ước lượng) trên cơ sở ADV đo sau khoá ở rev1 (§5, 18/11): vị thế ≤20 tỷ thoát lệnh trong ≤10 phiên ở mức tham gia 10%. Rev2 không truy vấn lại.
- Giá trị **trước** chiết khấu: 17.670; **sau**: 17.317. Độ nhạy: 0% cho 17.670; 5% cho 16.787. Nhãn rẻ/đắt dùng giá trị **sau** chiết khấu.

### 6d. So giá (bước cuối, sau khoá)

- **Giá DNSE** `latest_trade` board G1: **16.200 đ** (23/11/2026 11:29). Giá/tâm = 0,94; giá/kịch bản cơ sở = 0,93.
- **P/B hàm ý tại tâm 0,86; P/E chuẩn hoá hàm ý 7,3.**
- **Dải giá/tâm** theo các độ nhạy phán đoán chính: cửa sổ 12q→20q cho 0,69–1,40; k 6,3%→26,5% cho 0,87–1,24.
- **⇒ Nhãn: quanh giá trị hợp lý, không rẻ rõ rệt.** Cổng 0,85×tâm = 14.719 chưa đạt.

## 7. Pháp lý / quản trị — chỉ WARNING

- **Phần giữ nguyên rev1 §7:**
  - EY soát xét bán niên 2026 sạch.
  - Phải thu người lao động 237,1 tỷ: −539 đ/cp nếu mất trắng; không vào base.
  - Vốn 2024 đã dùng 100% đúng phương án.
  - Bên liên quan nhỏ (Transeco 20 tỷ).
- **Bổ sung rev2:** BCTC kiểm toán 2025 (EY) chấp nhận toàn phần. Kiểm toán 2022 điều chỉnh giảm LNST Q4 144,9 tỷ. Đây là dấu hiệu cần theo dõi chất lượng số liệu quý chưa kiểm toán, không phải sai phạm.
- **Không kiểm chứng được:** giấy phép môi trường từng trại (mục 7 bảng đính chính); toàn văn NQ ĐHĐCĐ 2026 về ESOP (mục 8).

## 8. Vị thế & lợi thế cạnh tranh (5F) — V5

- **Tái dùng 5F đầy đủ của rev1 §8** (làm 18/11/2026, dưới 12 tháng): **moat_tier = NARROW (mỏng; NONE cũng đứng được), moat_type = COST/INTEGRATION; rủi ro số 1 = chu kỳ giá heo + ASF lọt trại nái.**
- **Kiểm nhanh rev2:** chuỗi ROE_op 20 quý dao động rất rộng (W12 17,3% so với W20 10,6%). Điều này xác nhận không có lợi nhuận siêu ngạch bền qua chu kỳ ⇒ không thưởng tham số moat. Đề xuất dòng `moat_tags.csv` giữ như rev1 (không sửa file).

## 9. Mốc khoá trước — điều kiện đổi nhận định CẢ HAI CHIỀU

- **Cửa sổ trượt theo luật khai trước.** Khi có BCTC Q4/26, cả ba cửa sổ trượt thêm một quý. Q1/23 (lỗ) rơi khỏi W15 và Q4/21 rơi khỏi W20. Vì vậy tâm **tăng cơ học** dù quý mới xấu:

  | LNST Q4/26 | Tâm | Thay đổi |
  |---|---|---|
  | −50 | 18.252 | +5,4% |
  | +35 | 18.792 | +8,5% |
  | +120 | 19.320 | +11,6% |

- ⚠️ Mức +5,4% ở LNST −50 là **hiệu ứng rơi quý lỗ, không phải cơ bản cải thiện**. Phán đoán đổi nhận định dựa trên bảng dưới, không dựa vào việc tâm tăng sau khi trượt.

| Mốc | Ngày | Chiều tăng | Chiều giảm |
|---|---|---|---|
| BCTC Q4/26 | ≤ 30/01/2027 | LNST Q4 ≥ 120 tỷ và không trích lập tài sản sinh học ⇒ trọng số tốt 35% | LNST Q4 < −50 tỷ hoặc trích lập tài sản sinh học/tồn kho > 100 tỷ ⇒ trọng số xấu 35% |
| Trích KTPL từ LN 2026 (NQ ĐHĐCĐ 2027) | ~04/2027 | ≤ 6% LNST ⇒ k 5 năm giảm | ≥ 15% LNST ⇒ k tăng; tâm −3% đến −5% |
| Giá heo T1/27 (Bobby F1/F2) | 05/02/2027 | ≥ 65k ⇒ trọng số tốt 35% | < 50k ⇒ trọng số xấu 35% |
| BCTC Q1/27 | ≤ 30/04/2027 | LNST ≥ 300 tỷ và biên gộp mẹ ≥ 8,5% | LNST < 150 tỷ |
| Đàn heo T3/27 (Bobby F8) | 15/04/2027 | ≤ +3% so cùng kỳ | ≥ +4% ⇒ trọng số xấu 40% |
| Lãi huy động 12T | liên tục | −50bp ⇒ +5,2% | +50bp ⇒ −4,6% |
| XDCB/vốn chủ | mỗi BCTC | XDCB trại vào vận hành, ROE_op quý ≥ 13,8% | XDCB tăng > 20% vốn mà ROE_op quý < 10% ⇒ xem lại NPV=0 bằng kịch bản xấu |
| Phải thu người lao động | BCTC Q4/26 | ≤ 150 tỷ ⇒ gỡ WARNING | > 300 tỷ hoặc trích lập ⇒ WARNING cấp cao |

## 10. Điểm yếu của chính báo cáo

1. **Tâm là trung bình của các cách nhìn chu kỳ rất khác nhau** (độ nhạy cửa sổ −33% / +36%). Luật "ba cửa sổ đều trọng số" là khai trước nhưng vẫn là phán đoán. Người đọc nên coi vùng [9.906; 24.478] là thông tin chính, không phải tâm.
2. **XDCB các quý giữa là nội suy.** Biến thể bậc thang lệch −3,8%. Biến thể toàn vốn lệch −28,5% (cận dưới).
3. **k = 11,06% dựa trên 5 năm có phân bố rất lệch** (0% đến 26,5%). Thù lao 2021–23 chưa đọc ⇒ k hơi thấp.
4. **Chiều lệch tâm lý:** người dựng đã thấy giá rev1 (16.950). Hai trong ba thay đổi kéo tâm xuống (KTPL, W20), một kéo lên (W12). Kết quả 0,94× không nằm ở vùng "rẻ", nên không có dấu hiệu kéo về phía mua. Nhưng chiều lệch không loại trừ được.
5. **Chưa kiểm chứng được:** chi tuân thủ môi trường, ESOP 2026 (độ nhạy ≤ −2%); thời hạn hoàn ứng của khoản phải thu người lao động.

## 11. Nguồn

- **BCTC hợp nhất kiểm toán:**
  - `src/kt22_hopnhat_vi.pdf` (dabaco.vn wp-content 2023033120…hợp nhất_signed.pdf)
  - `src/kt23_hopnhat_vi.pdf` (drive id 18XK0rqA…, link từ trang dabaco.vn "bao-cao-tai-chinh-nam-2023-da-kiem-toan")
  - `src/kt24_hopnhat_vi.pdf`
  - `src/kt25_hopnhat_vi.pdf` (EY)
- **Kỳ 2026:** `src/h1_d.pdf` (soát xét EY H1/2026; TM25.1 ảnh `png/h1d_52_equity.png`), `src/q3_hopnhat.pdf`.
- **Ảnh thuyết minh:** `png/kt25_41_tm23.png` (quỹ KTPL 2024–25), `png/kt25_09.png` (BCĐKT 2025).
- **BQ:** `tav2_bq.ticker_financial` (DBC 2021Q1–2026Q3, NP_P0/BVPS/OShares; truy vấn 23/11/2026).
- **Lãi huy động:** `deposit_rate_vn.effective_deposit_rate`. **Giá:** DNSE `latest_trade` (sau khoá).
- **Nguồn ngành/macro:** Bobby sector read 18/11 và 5F tái dùng từ `REPORT.md` (rev1).

## 12. Sổ giá

- **KHÔNG ghi `kb/dd_price_zones.json`** (theo chỉ đạo job). Đề xuất entry nằm ở `LEDGER_PROPOSAL_DBC.json`.
- **Số cho sổ:** tâm 17.317, vùng [9.906; 24.478], center_alt (kịch bản cơ sở sau chiết khấu thanh khoản) 17.442, giá tham chiếu 16.200 (23/11/2026).
- **assumptions_md5 = `25d2e3059aa88705be3605ba500f9369`.**
- Không ghi `v_short`/`v_long`/`D` vào sổ.
