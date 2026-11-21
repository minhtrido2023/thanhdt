# QTP DD r3c — sửa nhỏ theo skeptic vòng 2 · 20/11/2026 · job `Taylor_20261120_044905` (nền: r3b `Taylor_20261120_043725`)

> Chỉ NGHIÊN CỨU. Không ghi `dd_price_zones.json`, không email. Thay thế `REPORT_r3b.md` (không đè bản cũ).
> Mô hình `qtp_model_r3c.py` (khác r3b đúng 1 dòng :110 — doanh thu bù FOM+VC chỉ phát sinh cùng opex; md5 xem bus), output `qtp_model_r3c_out.txt`. Tâm 7.701 / center_alt 8.557 (trước CK) **tái lập không đổi** (chỉ biến thể `opex_start` bị ảnh hưởng).
> Kiểm độc lập `check_independent_r3b.py` (không import mô hình): P0/cơ sở **−10.478**, bỏ phần dư 115 **−9.237**, khớp từng đồng; biến thể dừng 2031 khớp (+1.638 độc lập vs +1.639 mô hình, chênh làm tròn).
> Nền r2 giữ nguyên, tái lập 14.599 trước CK.

## 0. Kết luận

- **Tâm r3b: 7.701 sau CK (8.557 trước CK)**, nhãn **ĐẮT**. r3 là 7.053 (trọng số P0 0,5 → 0,4: **+648 sau CK**).
- **Vùng giá trị cạnh tâm: 6.300 … 8.900** (cận trên đơn lẻ nay 8.894) theo biến thể đơn lẻ (sau CK). Theo trọng số P0 từ 0,5 về 0: 7.053 … 10.293. Kết hợp thuận lợi nhất (bỏ phần dư 115 + opex từ 2032 + lãi 7%): **9.240** (r3b ghi 9.611 do lỗi bù FOM+VC 2030–31).
- Giá 10.200–10.300 = **1,32–1,34× tâm**; vẫn **1,10× trên cả điểm thuận lợi nhất** (9.240; 10.200/9.240 = 1,104). Kết luận ĐẮT không đổi.
- Biến quyết định vẫn là việc dự án có được bù giá hay không (P0 → P100 ≈ 10.000 đ/cp). Quyền từ bỏ **không** cứu P0 một cách thực tế (§3).
- **Cảnh báo mới:** ở P0, dòng tiền toàn công ty âm từ 2030 (−119 … −424 tỷ/năm), cộng dồn 2030–39 **−3.110 tỷ**, đủ ăn hết 1.541 tỷ tiền ròng + FCFE 2027–29 ⇒ tiền ròng ~0 năm 2039 **kể cả không chi cổ tức**; với cổ tức 900đ/cp thì âm từ **2032** ⇒ phải vay thêm/tăng vốn (WARNING).

## 1. Đính chính pháp lý (legal-vn 20/11)

| Mục | r3 | r3b |
|---|---|---|
| Điều khoản bù | "TT12 Đ13.4/Đ14.6, lối duy nhất Đ27.3" | **Đ13.4 TT12 đúng; không có Đ14.6** (xoá) |
| TT57/2020 Đ20.3 | không rõ còn không | Tương đương ở **TT07/2024 Đ27.4** ("thoả thuận bổ sung chi phí vào giá phát điện, báo cáo Bộ CT xem xét"); **TT07 bị TT12/2025 bãi bỏ (Đ28.2), TT12 không có điều tương đương** |
| Đường còn lại | Đ27.3 | Luật Điện lực 61/2024 **Đ52.4** (a: thay đổi chính sách bất lợi; c: nâng cấp cải tạo hạng mục… để đáp ứng tiêu chuẩn mới; cụm ngoặc có thể loại trừ hệ thống trong nhà máy — tranh cãi) |
| Hiệu lực giá mới | — | Không văn bản quy định ngoài thoả thuận hai bên; "báo cáo Bộ" không phải phê duyệt trước |

⇒ Cơ chế bù: nền pháp lý **yếu hơn "có" nhưng không bị cấm**; coi là quyền thoả thuận chưa có tiền lệ.

## 2. Tách 470,29 tỷ/năm "điện–nước–hoá chất" (FS §3.1.7)

| Cấu phần | Tỷ/năm | Nguồn |
|---|---|---|
| Amoniac 12.045.120 kg × 26.350 đ | **317,4** | FS (số liệu rõ) |
| Điện tự dùng 18.470.400 kWh × 2.036 đ/kWh (giá mua điện chạy thử) | **37,6** | FS (đo bằng nhân hai số FS) |
| **Phần dư** | **115,3** | **FS không thuyết minh** (nước/hoá chất khác?) — nhãn "chưa giải thích" |

Bỏ phần dư: P0/cơ sở **−9.237** (từ −10.478); tâm (trọng số r3) 7.718 sau CK; tâm r3b 8.287 sau CK. Không bỏ trong tâm vì thiếu cơ sở bác bỏ; nêu trong vùng.

## 3. Sửa logic r3 mục 9 (quyền từ bỏ) + dòng tiền toàn công ty

**Quyền từ bỏ (dừng cuối 2031)** — kịch bản cơ sở r2, trước CK (đ/cp):

| | chạy đến hết 2047 | dừng cuối 2031 | chênh |
|---|---|---|---|
| P0 | 4.722 | 6.360 | **+1.639** |
| P50 | 10.269 | 7.816 | −2.453 |
| P100 | 15.014 | 8.999 | −6.015 |

- Chỉ có lợi ở P0, và chỉ nếu quyết định **sau khi biết** P. Giá trị quyền ≈ +655 trước CK / +590 sau CK (trọng số W_F, chỉ cơ sở).
- **KHÔNG vào tâm.** Điều kiện chưa kiểm chứng: PPA/pháp lý cho phép dừng NMNĐ Quảng Ninh (DNNN, phục vụ miền Bắc), cam kết vay/EPC đã ký, hậu quả tài sản (đã nhập sunk). Gắn nhãn **chỉ khi pháp lý/hợp đồng cho phép**.
- Dừng 2031 cũng bỏ lợi nhuận nền (r2 từ 15.200 → 13.562, −1.638); mô hình tính cả hai phía.

**Dòng tiền toàn công ty, P0, cơ sở (tỷ):**

| Năm | FCFE nền | ΔFCFE | Toàn công ty | Tiền ròng luỹ kế (chưa cổ tức) |
|---|---|---|---|---|
| 2027 | 907 | −247 | +660 | 2.202 |
| 2028 | 907 | −445 | +462 | 2.663 |
| 2029 | 844 | −394 | +450 | 3.114 |
| 2030 | 844 | −963 | **−119** | 2.994 |
| 2031 | 641 | −938 | −298 | 2.697 |
| 2032 | 489 | −913 | **−424** | 2.272 |
| 2035 | 489 | −838 | −349 | 1.149 |
| 2039 | 489 | −738 | **−249** | **3** |
| 2040 | 489 | −446 | +42 | 46 |

- Cộng dồn 2030–39: **−3.110 tỷ** (đo bằng mô hình; skeptic nêu ≈ −3.400, lệch do cách làm tròn/giả định lãi).
- Tiền ròng < 0 đầu tiên (P0): không có cổ tức **không âm** (tiền thấp nhất 3 tỷ, 2039); cổ tức 500đ/cp: **2034**; 900đ/cp: **2032**.
- P50: tiền ròng thấp nhất 2.202 tỷ (2027) — không thâm hụt.
- Lưu ý: "tiền ròng luỹ kế" cộng FCFE nên thêm tiền 2027–29; tiền ròng đầu kỳ 1.541 tỷ (30/9/2026).

## 4. Trọng số: lập luận có nguồn (chốt TRƯỚC khi chạy lưới)

Hạ P0 từ 0,50 → **0,40** (một bậc của lưới), P50:P100 giữ 60:40 ⇒ **0,40 / 0,36 / 0,24**.
- **Lên (giảm P0):** (0) **EVN là bên mua bị ép biên 2026–27** (framework §3 HARD ABANDON #4: rút giá trị khỏi cổ đông nhỏ) — làm tăng P0, không giảm; (i) TT07/2024 Đ27.4 từng có điều thoả thuận; (ii) FS thẩm tra vẫn dẫn TT57 Đ20.3 làm căn cứ; (iii) EVN kiến nghị 29/12/2025; (iv) Luật Điện lực 61/2024 Đ52.4(a) mở lối; (v) bên mua và chủ chi phối cùng EVN; P0 không tự duy trì (§3: tiền ròng hết ~2039; ~2032 nếu giữ cổ tức).
- **Xuống (giữ P0 cao):** (i) TT12/2025 **không** có điều tương đương; (ii) FS dẫn một điều đã bị bãi bỏ; (iii) 9 năm (2017→2026) chưa bù được; (iv) 0 tiền lệ nhà máy than được bù; (v) Đ52.4(c) có thể loại trừ hệ thống trong nhà máy.
- Cân bằng ⇒ chỉ nhích một bậc, không xuống 0,3 hay thấp hơn vì chưa có văn bản/tiền lệ. Trọng số là **(ước lượng)**, không phải tần suất đo (N = 0).

**Bảng độ nhạy trọng số (P50:P100 = 60:40; trước / sau CK):**

| P0 | trước | sau |
|---|---|---|
| 0 | 11.437 | 10.293 |
| 0,2 | 9.997 | 8.997 |
| 0,3 | 9.277 | 8.349 |
| **0,4 (chốt)** | **8.557** | **7.701** |
| 0,5 (r3) | 7.836 | 7.053 |

## 5. Biến thể (trên W_F; trước / sau CK)

| Biến thể | Trước | Sau | Δ so tâm |
|---|---|---|---|
| **Tâm r3b** | 8.557 | **7.701** | – |
| Bỏ phần dư 115 của VC | 9.208 | 8.287 | +7,6% |
| Opex SCR từ 2032 (QCVN 19:2024 bắt buộc 01/01/2032)* (r3c) | 9.398 | 8.458 | +9,8% |
| VC chỉ 50% | 9.882 | 8.894 | +15,5% |
| Bù chậm từ 2033 | 7.017 | 6.315 | −18,0% |
| P50 chỉ bù FC (không bù opex) | 7.598 | 6.838 | −11,2% |
| Khấu hao 18 năm | 8.446 | 7.601 | −1,3% |
| TMĐT 3.300 (vay 80%) | 8.832 | 7.949 | +3,2% |
| Giá bù 164,25 đ/kWh (bảng FS §3.1.7) | 8.436 | 7.593 | −1,4% |
| Lãi vay 7% / 11% | 8.958 / 8.152 | 8.062 / 7.337 | +4,7% / −4,7% |
| Lãi huy động −100bp / +100bp (r và lãi vay) | 9.031 / 8.130 | 8.128 / 7.317 | +5,5% / −5,0% |
| Kết hợp thuận lợi: bỏ dư 115 + opex 2032 + lãi 7% (r3c) | 10.267 | 9.240 | +20,0% |
| Kết hợp bất lợi: bù chậm 2033 + KH 18 + lãi 11% | 6.541 | 5.887 | −23,6% |

*Giấy phép môi trường: **GPMT số 517/GPMT-BTNMT 03/12/2024** (BNNMT tiếp tục cho cải tạo 4 hệ thống khí thải, VB 7589/BNNMT-MT 07/10/2025). QCVN 19:2024 bắt buộc từ **01/01/2032**, UBND tỉnh có thể ban hành lộ trình sớm hơn. Đã thử tra GPMT 517 Phụ lục 2 (web search 20/11): **không truy cập được văn bản** ⇒ vẫn **chưa biết có buộc chạy SCR trước 2032 không**; không đưa vào tâm; biến thể đã nêu. Việc cần làm: xin bản GPMT từ công ty/BNNMT.
- **Lãi suất/kỳ hạn NQ 105/NQ-NĐQN: tìm lại (web), không thấy** — vẫn là (ước lượng) 9% (biên 7–11%), trả gốc 10 năm.
- **Vùng:** biến thể đơn lẻ 6.315–8.894; kết hợp 5.887–9.240; theo trọng số 7.053–10.293. Giá 10.200 ngoài mọi biến thể đơn lẻ (1,147× cận trên). **Phân kỳ mạnh (D = ln(9.189/512) = 2,89 > ln 3 = 1,10) ⇒ luật 0,85×tâm không tự kích hoạt.**

## 6. Điều kiện huỷ mới + sửa r2 (Mike áp, tôi không sửa)

- **Điều kiện huỷ (thêm):** (a) tiền ròng < 0 trên BCTC; hoặc (b) tăng vốn / vay mới để tài trợ thâm hụt dự án (không phải cổ tức bị giảm); (c) cổ tức bị cắt dưới mức EPS nền do tài trợ dự án.
- **Điều kiện huỷ có ngày (r3c):** (d) **chưa ký thoả thuận bổ sung giá PPA trước COD (~12/2029)**, hoặc (e) EVN/BCT **từ chối bằng văn bản** vào bất kỳ lúc nào. Điều kiện (a) "tiền ròng < 0" là **chỉ báo trễ** (P0 không cổ tức chạm đáy ~2039) — không dùng làm điều kiện duy nhất.
- **`dd_QTP_20261117/REPORT.md`:**
  - dòng 316 (HARD ABANDON #4): đổi "EVN từ chối đưa vào giá (−1.550đ/cp nếu mất vốn chủ)" thành "**không có cơ chế bù ⇒ P0: −10.478 đ/cp (vốn + lãi + gốc −4.745, opex 572 tỷ/năm −5.733)**; huỷ nếu EVN/BCT xác nhận P0 hoặc tiền ròng < 0".
  - dòng 278 (bảng): "có số cụ thể ⇒ sang kịch bản tiêu cực" thành "đã có số cụ thể (TMĐT 3.485, vay 2.788, opex 572); tâm r3b 7.701".
  - dòng 112: bỏ câu "mức cực đoan, không đưa vào base"; thay bằng ba kịch bản P0/P50/P100 và trọng số 0,4/0,36/0,24.
  - §0: tâm 7.700 / vùng nêu 6.300–8.900 (đơn lẻ), 5.900–9.200 (kết hợp) / ĐẮT; cờ phân kỳ V_ngắn vs V_dài **BẬT** (V_ngắn 512 vs V_dài 9.189).
- `investor_report` (tiêu đề nêu cả hai vế) như r3 §8 mục 2; không nhắc đính chính.
- `dd_price_zones.json`: Mike làm sau (`center` = 7701 hoặc làm tròn; `assumptions_md5` = md5 `qtp_model_r3c.py`).

## 7. Giới hạn

- Lãi vay/kỳ hạn/giải ngân/COD là **(ước lượng)**; phần dư 115 chưa giải thích; chuyển lỗ không hết hạn; quyền từ bỏ không có kiểm chứng pháp lý.
- Dừng 2031 không mô hình hoá ghi giảm tài sản/lá chắn thuế từ xoá sổ (bảo thủ cho phương án dừng).
- Sửa r3c: chỉ dòng :110 (bù FOM+VC gắn với opex). Số P0/cơ sở, tâm, bảng trọng số không đổi.
- Cộng dồn −3.110 vs ước skeptic −3.400: chưa đối soát hết sai khác nguồn của ước đó.
