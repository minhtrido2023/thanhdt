# DD — DCM (PVCFC) · as-of 05/11/2026 · **VÒNG 5 (r5 = r4 sửa theo phản biện độc lập)** · job `Taylor_20261104_172238`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. `REPORT.md`, `_r2`, `_r3`, `_r4` giữ nguyên. Nguồn gốc hợp đồng, bảng A.1–A.3 và các mục 1–4 của r4 **không đổi** (xem `REPORT_r4.md`); file này chỉ ghi phần thay đổi và số mới.
> **Thứ tự chạy, trung thực:** tôi **đã biết giá 33.000 và nhãn ĐẮT** từ r1–r4 trước khi sửa. `calc/model_r5.py` không nhận giá/vốn hoá/PE. Khoá md5 lúc **00:24:45 ICT 05/11** (`calc/LOCK_r5_md5.txt`), sau đó mới chạy `calc/compare_px_r5.py`. Các sửa đều xuất phát từ văn bản hợp đồng / kiểm tra nội bộ mô hình, không từ giá.
> **Kiểm lại từng điểm phản biện (đo bằng chạy mô hình):** S1, S2, S3, S4, M1–M7 đều **đúng** và được áp. Số người phản biện ước **tái lập đúng**: A 24.192 (ước 24.197), B 24.459 (ước 24.459), chỉ sửa 2028 → 22.988 (ước 22.988), ND30+V1 đảo ở biên 243, ND44,8%+V1 ở 275, 2035+ phẳng Δ −7.607 (ước −7.606). Điểm lệch duy nhất: mức tuyệt đối 2035+ phẳng là 16.719 (ước ≈16.038) vì tâm nền khác (24.326 vs 23.644); Δ khớp.

## 0. Kết luận
- **Tâm 24.326 đ/cp = trung bình hai cách đọc nhất quán A (24.192) và B (24.459); dải [24.192 ; 24.459].** (r4: 23.644; r3: 27.021.)
- **Giá 33.000 cao hơn tâm +35,7%** (so A +36,4%, so B +34,9%, so nhánh CYC +30,3%). Nhãn **"giá trên vùng giá trị"** ở cả 3 lưới đối xứng (P90: 27.708 / 29.991 / 27.047).
- **Biên urê–khí dài hạn hàm ý của giá** (giá = giá trị kỳ vọng): **297** (A 299, B 295) ở Brent 67,8; 304 / 308 / 315 ở Brent 82 / 90 / 103 (tâm). Nếu chỉ nhánh CYC: 263–277. Mốc so sánh: TB 2016–25 = 179; 2025 = 257; dải bền của người đọc ngành 180–260.
- **Điều kiện đảo nhãn (S1, số đã tính lại sau S2/S3):** nhãn chỉ đảo sang "trong vùng" khi **đồng thời** (i) phần PM3 sau 2027 theo kịch bản rẻ (V1), (ii) Nam Du thấp (≈30%), (iii) biên ở **cận trên dải bền 180–260** (≥ ~243; ≥ ~224 nếu r thấp hơn 100bp). Với Nam Du 44,8% + V1 cần biên ≥ ~275 — **ngoài dải bền**. Tại tâm không có đảo.
- Các câu r4 "bớt phụ thuộc lựa chọn biên" **bỏ**: nhãn vẫn phụ thuộc biên, chỉ là ngưỡng đảo nằm ở cận trên/ngoài dải.
- Rủi ro lớn chưa vào base: **2035+** (S4) — hết khối lượng cam kết 25/4/2032; nếu khí giá 10,39 phẳng từ 2035: tâm **16.719 (−7.607)**.

## 1. Các sửa so với r4 (mỗi điểm: kiểm lại → kết quả → áp/không)
| # | Kiểm lại | Kết quả | Áp |
|---|---|---|---|
| S1 | Chạy `model_r4` (2028 theo V1 cũ): ND30%+V1 đảo ở biên **224** (r −100bp: 207); riêng V1 ND54% đảo ở **277**. Câu r4 "≥ ~280, ND30 + PM3 rẻ" gộp hai ngưỡng khác nhau | **Đúng** | Áp, tính lại (mục 4) |
| S2 | 966,7 kt × 22 MMBtu/t = 21,27 triệu MMBtu = **602 triệu Sm3/năm = 1,215×LKN 495**. Nam Du theo bao tiêu 269,74 → **44,8%**; theo trần ngày 0,81×365 = 295,65 → **49,1%**; 54% (0,81/1,5) chỉ nhất quán nếu I_C ≈ **18,3** | **Đúng** | Áp: hai cách đọc A/B |
| S3 | 2028 ở r4 dùng cơ cấu V1 (86,5% khí giá quyền nhận PVN, Δ biên +36 USD/t): trái với mua Petronas hết cuối 2027 [BB25 p8] và Nam Du ≤ Q4/2028 [PL12 p29]; chỉ sửa điều này: 23.644 → **22.988 (−656)** | **Đúng** | Áp: 2028 dùng mức **V2** (PM3 = 50% quyền nhận PVN + 50% @13,7% Brent), cả A và B. **Không** dùng cơ cấu 2028 của VDSC (35% Nam Du không khớp hạn Q4/2028) |
| S4 | Sau 25/4/2032 hết khối lượng cam kết [PL12 Đ4.1(b)]; PM3 suy giảm; BB25 nhắc LNG | **Đúng** | Độ nhạy (không vào base), mục 5.3 |
| M1 | Pn1/Pn2 do Đ9.1 HĐ 3918 gốc quyết định, SĐBS 12 giữ nguyên Đ9.3; DP2 "Khí Bổ Sung" còn trong Đ9.2 [PL12 p31] | **Đúng** | Sửa chữ: ẩn số là **khối lượng khí bổ sung sau 2027 và nguồn thượng nguồn**, V1/V2 là kịch bản khối lượng |
| M2 | Đ10.2(a) p32: hoá đơn tính bằng USD; tỷ giá VCB 10:00 ngày phát hành hoá đơn điều chỉnh = 2 ngày làm việc trước ngày thanh toán (p33) | **Đúng** | Rủi ro tỷ giá cho **mọi** nguồn khí |
| M3 | "Cơ cấu 2030 vĩnh viễn" tính qua `pv_gas(mode='perm2030')` = đường đủ ⇒ **đã gồm** hiệu chỉnh độ dốc | **Đúng** | Đưa ra khỏi gạch "bỏ độ dốc" (mục 5.3) |
| M4 | Độ nhạy ND30 chưa tính chi phí bao tiêu: Khí Trả Trước Đ4.6(f2), sàn tháng 70% Đ4.1.2(i) | **Đúng** | Ghi là **cận trên** |
| M5 | Quy đổi cơ học 966,7 kt×26.400 = **25,5 tỷ/USD/t trước thuế** (19,2 sau thuế 20% và KTPL; đo `model_r5`), hồi quy r2: LNST = −318 + **8,84**×biên (thuế 10,8%) ⇒ **9,9** tỷ trước thuế; tỷ lệ **0,388** | **Đúng** | Độ nhạy thang hồi quy (mục 5.3); chế độ khí 2021–25 vẫn chưa kiểm |
| M6 | "Hợp đồng làm chi phí khí tăng" so với giả định r3 (PM3 giá cũ mãi mãi) | **Đúng** | Viết lại: đối chứng thật là PM3 suy giảm + hết mua Petronas 2027 ⇒ hụt khí / LNG, chưa mô hình hoá |
| M7 | "Chiều tác động ngược hướng giá" | **Đúng, sửa** | Tâm giảm 27.021 → 24.326 là **cùng hướng** nhãn đã biết (giá cao hơn giá trị), chỉ làm khoảng cách hẹp hơn r4 (+39,6% → +35,7%) và rộng hơn r3 (+22,1%); độ lớn do hợp đồng, nhưng hướng thì trùng với nhãn đã có |

## 2. Hai cách đọc nhất quán (S2) — `calc/model_r5.py`
| | **A** | **B** |
|---|---|---|
| Nam Du bình ổn | **44,8%** = bao tiêu 269,74 / tiêu thụ 602 tr Sm3 (tiêu thụ phân bổ theo Đ10.1(b)) | **54%** = LKNTĐ 0,81/1,5 [PL12 p28]; Nam Du **thay phần Petronas** (BB25 p8: mỏ cận biên bổ sung khi PM3 suy giảm, hết mua Petronas cuối 2027; VDSC) |
| PM3 còn lại | TB 0,5 V1 + 0,5 V2 (ước lượng) | V1 (rẻ ngang quyền nhận PVN 46% MFO) |
| 2028 | 25% Nam Du, PM3 theo **V2** | như A |
| 2034 | ½ mức bình ổn | như A |
| 2035+ | 50% quyền nhận PVN + 50% @13,7% Brent (ước lượng) | như A |
| **Giá trị (Brent 67,8)** | **24.192** | **24.459** |

- **Tâm công bố = trung bình A và B = 24.326** (trọng số 0,5/0,5, ước lượng); dải [A, B].
- ⚠️ **Hạn chế của B:** 54% × 602 tr Sm3 = 325 tr Sm3 > trần cung Nam Du theo công suất ngày 295,65 tr Sm3 (49,1%). B vì vậy **đẩy tỷ trọng Nam Du lên quá trần ngày** khi tiêu thụ ở mức 602; đổi lại nó đại diện cho kịch bản "Nam Du thay Petronas". Nếu cắt B về 49,1% (V1): **25.233**, tâm sẽ là **24.713** (+387). Không đưa vào base; ghi là độ nhạy.
- Định mức khí I_C: 21,1–22,8 MMBtu/t (TM38 ÷ sản lượng 9T ước lượng 700–750 kt ÷ giá công thức); dùng 22. Độ nhạy I_C 20 / 25: tâm **23.838 / 25.056** (A 23.449 / 25.306; B 24.228 / 24.807). Không chắc: TM38 có gồm VAT; sản lượng 9T là ước lượng; cước 1,14 là của VDSC.

## 3. Lịch giá khí (USD/MMBtu trước VAT gồm cước 1,14; Brent phẳng) — A | B
| Năm | 2026 | 2027 | 2028 | 2029 | 2030 | 2032 | 2034 | 2035+ (nền) |
|---|---|---|---|---|---|---|---|---|
| Brent 67,8 | 7,65 | 7,99 | 8,38 \| 8,46 | 9,00 \| 8,90 | 9,11 \| 9,03 | 9,33 \| 9,30 | 8,16 \| 7,56 | 7,99 |
| Brent 103 | 11,02 | 11,53 | 11,53 \| 11,53 | 10,61 \| 9,95 | 10,72 \| 10,08 | 10,94 \| 10,34 | 10,42 \| 9,22 | 11,53 |
| Δ biên A \| B (USD/t, Brent 67,8; dương = lợi) | +7,7 | +0,3 | −8,5 \| −10,3 | −22,1 \| −19,8 | −24,5 \| −22,7 | −29,4 \| −28,5 | −3,6 \| +9,7 | +0,3 |

Nam Du (tại mỏ, chưa VAT): 10,39 × 1,0225^(năm−2028): 10,39 (2028), 11,36 (2032), 11,87 (2034). Ở Brent 67,8, khí Nam Du đắt hơn khí PM3 mỗi năm 2029–33; ở Brent 103 B có Δ dương 2029–34.

## 4. So giá (sau khoá, `calc/compare_px_r5_out.txt`) và ngưỡng đảo nhãn
- 33.000 vs tâm 24.326: **+35,7%**. Lưới (Brent 67,8 trừ khi ghi):

| Lưới | n | P10 | P25 | P50 | P75 | P90 | Nhãn @33.000 |
|---|---|---|---|---|---|---|---|
| Đối xứng 138/179/220 | 270 | 20.522 | 21.643 | 24.095 | 26.243 | 27.708 | trên vùng giá trị |
| Đối xứng 98/138/179/220/260 | 450 | 18.062 | 20.458 | 24.095 | 27.752 | 29.991 | trên vùng giá trị |
| 138/179/220 × Brent 67,8/82/90/103 | 1.080 | 19.846 | 21.030 | 23.380 | 25.686 | 27.047 | trên vùng giá trị |

- **Bảng biên dài hạn → giá trị (đ/cp) và giá 33.000 cao hơn (Brent 67,8):**

| Biên | 98 | 138 | 179 | 220 | 260 |
|---|---|---|---|---|---|
| Tâm | 18.356 | 21.298 | 24.314 | 27.330 | 30.272 |
| Giá cao hơn | +79,8% | +54,9% | +35,7% | +20,7% | +9,0% |
| A \| B | 18.222 \| 18.490 | 21.164 \| 21.432 | 24.180 \| 24.448 | 27.196 \| 27.463 | 30.138 \| 30.405 |

  Theo Brent (biên 179, tâm): 24.314 / 23.794 / 23.500 / 23.023 (Brent 67,8 / 82 / 90 / 103). Biên 220: 27.330 / 26.810 / 26.516 / 26.039.
- **Ngưỡng đảo (biên mà giá trị kịch bản = 33.000; Brent 67,8):**

| Nam Du | PM3 sau 2027 V1 | V2 | V1, r −100bp |
|---|---|---|---|
| 30% | **243** | 302 | **224** |
| 44,8% (A) | **275** | 322 | 255 |
| 49,1% | 285 | 328 | 264 |
| 54% (B) | 295 | 335 | 274 |

  Đọc: nhãn "trong vùng" chỉ đạt trong dải bền 180–260 ở ô **Nam Du ≈30% + V1** (243–260), hoặc r thấp hơn 100bp (224–260). Mọi ô còn lại cần biên > 260.
- **Câu r4 sai** "chỉ đảo nếu Nam Du ~30%, PM3 rẻ, và biên ≥ ~280": 224 (r4, ND30+V1) và 277 (r4, ND54%+V1) là **hai** ngưỡng; r5 cho 243 và 275.

## 5. Kết quả, cầu nối, độ nhạy
### 5.1 Cầu nối (đ/cp)
| Bước | Kỳ vọng | Δ |
|---|---|---|
| r3 (= r2) | 27.021 | |
| + hiệu chỉnh độ dốc proxy | 29.098 | **+2.077** |
| + đường khí hợp đồng 2027–34 (A −4.907; B −4.639; tâm) | **24.326** | **−4.773** |
| **r5** | **24.326** | **−2.695** |

Từ r4: 23.644 → sửa 2028 theo V2 **22.988 (−656)** → hai cách đọc A/B (tâm) **24.326 (+1.338)**. Nhánh: CYC 25.322 · ADMIN 25.322 · STRUCT 20.342; trọng số 0,50/0,30/0,20 giữ nguyên. Chiết khấu thanh khoản ≈ 0 (ADV 74 tỷ, r3).

### 5.2 Theo Brent phẳng (tâm | A | B; PV phần khí A | B)
| Brent | 67,8 | 82 | 90 | 103 |
|---|---|---|---|---|
| Tâm | 24.326 | 23.806 | 23.512 | 23.035 |
| A | 24.192 | 23.385 | 22.929 | 22.189 |
| B | 24.459 | 24.227 | 24.095 | 23.882 |
| PV khí A \| B | −2.829 \| −2.562 | −3.636 \| −2.794 | −4.092 \| −2.926 | −4.832 \| −3.139 |
| Phần độ dốc riêng | +2.077 | −242 | −1.553 | −3.683 |

- **Cơ cấu 2030 vĩnh viễn (đã GỒM phần độ dốc, M3):** A −5.246 / B −4.800 ở Brent 67,8; A −3.084 / B −14 ở Brent 103.
- Chiều đúng: khi Brent tăng, tâm **giảm nhẹ** (24.326 → 23.035) vì phần độ dốc (giả định biên proxy cố định) và vì khí PM3 gắn dầu đắt lên; hợp đồng Nam Du giá cố định chỉ có lợi tương đối ở Brent cao với cách đọc B.

### 5.3 Độ nhạy (đ/cp; `model_r5_out.txt` dòng 7)
- **Lãi huy động (r):** ±50bp → 23.923 / 24.762; ±100bp → 23.550 / 25.236.
- **Nam Du thấp 30%** (cụm Cà Mau; **cận trên**, chưa tính chi phí bao tiêu: Khí Trả Trước Đ4.6(f2), sàn tháng 70% Đ4.1.2(i)): PM3 V1 **28.288**, TB V1/V2 **26.142**, V2 23.996. Nam Du 60,5%: TB **22.128**.
- Khí đầu trễ sang 2029: A 24.744; B 25.214.
- **Thang hồi quy (M5):** nhân phần khí với 0,388 (hồi quy r2 ≈ 9,9 tỷ trước thuế/USD/t vs 25,5 tỷ quy đổi cơ học): tâm **25.974** (A 25.922; B 26.026). Chiều đúng chưa rõ; ±1–2k. Chế độ khí 2021–25 (50/50 @12,7%) **chưa kiểm** — quyết định độ lệch −11,7 USD/t và phần độ dốc +2.077.
- **S4 — 2035+ (KHÔNG vào base):** giá 10,39 phẳng (+ cước 1,14, 100% khối lượng) từ 2035: tâm **16.719 (−7.607)** (A 16.586; B 16.853); ở Brent 103: 23.042. Nếu tiếp tục leo thang 2,25%/năm tới 2035 (12,14 + cước): **12.962 (−11.364)**. Lý do: hết khối lượng cam kết 25/4/2032; PM3 suy giảm; BB25 nhắc LNG. Kịch bản LNG không có giá nguồn → không định lượng riêng.
- (e) PM3 sau 2027 chuyển V1 / V2 ở cách đọc A: **25.920 / 22.463** (±1.7k so với A).

## 6. Mốc khoá trước & điều kiện đổi nhận định (hai chiều)
Mốc giữ như r4: 24/11/2026; 03/01/2027; 04/03/2027; BCTC Q4/26 cuối 01/2027; nghị định thuế XK 0% hạn 31/03/2027; **NQ chính thức + SĐBS 12 đã ký**; công bố giá/khối lượng khí bổ sung PM3 từ 01/01/2028; ngày khí Nam Du đầu tiên (≤ Q4/2028); thông báo lượng khí từ 25/4/2032.

**Điều kiện NÂNG** (mỗi điều kiện ⇒ CHẠY LẠI):
- (a)–(d) như r3. (e) khí bổ sung PM3 sau 2027 theo V1: +1.728 (A). (f) Nam Du ≈30% (cận trên): +1.816 (TB V1/V2). (g) Brent bền ≥ ~100 **và** urê bám chi phí khí thực (phần độ dốc = 0): cộng ≈ +3.683 vào 23.035 ⇒ ≈26.718 (phép cộng từ dòng độ dốc, **chưa chạy lại**). (h) Văn bản xác nhận cam kết giá Nam Du không vượt giá Petronas hiện tại (Elibook, thứ cấp).

**Điều kiện HẠ:**
- (a)–(e) như r3. (f) khí bổ sung PM3 theo V2: −1.729 (A). (g) **2035+ không có khí giá ≤ PM3** (S4): −7.607 (phẳng 10,39) tới −11.364 (leo thang). (h) **Hụt khí 2028–29 / sau 2032** (PM3 suy giảm, mua Petronas hết 2027): chưa mô hình hoá, chiều hạ. (i) **VND mất giá — mọi nguồn khí** tính bằng USD (Đ10.2(a)); vị thế USD 189 triệu của DCM tự phòng hộ một phần. (j) Nam Du ≥ 60,5%: 22.128.

## 7. Pháp lý / quản trị — WARNING (không vào base)
Như r4 §7. Cập nhật trạng thái SĐBS 12: trong tài liệu chỉ có **DỰ THẢO** trình ĐHĐCĐ bất thường 23/9/2026 (mục 1.2). Tìm NQ/Biên bản chính thức: **không thấy** (WebSearch: chỉ bài VCCI mô tả nội dung trình, không ghi ngày họp; hai file fireant `NewsAttachedFile/1857081`, `/1866171` là báo cáo quản trị 12T/2025 và thông báo 23/3/2026 — không liên quan). Chưa xác minh được thông qua / tỷ lệ biểu quyết / khác biệt so với dự thảo.

## 8. Chưa xác minh (ưu tiên)
1. **Khối lượng và giá khí bổ sung PM3 sau 2027** (Pn1/Pn2 do Đ9.1 HĐ gốc; nguồn thượng nguồn UGSA gia hạn tới 2047 không công bố giá) — ẩn số lớn nhất (V1/V2 cách nhau ≈3,5k đ/cp ở A).
2. **Bản SĐBS 12 đã ký + NQ ĐHĐCĐ 23/9/2026.**
3. **Tỷ trọng Nam Du thực tế** (44,8% / 49,1% / 54% / 30%) và chi phí bao tiêu.
4. Định mức I_C, TM38 có VAT, sản lượng 9T; cước Tp từ 2028.
5. Chế độ giá khí 2021–25 (giả định 50/50 @12,7%); thang quy đổi 25,5 vs 9,9 tỷ.
6. Giá khí / nguồn thay thế sau 2032; hụt khí 2028–29.
7. Các mục 2, 4–10 của r3 §8.

## 9. Sản phẩm
`calc/model_r5.py` (+`_out.txt/.json`, `LOCK_r5_md5.txt` 00:24:45 ICT), `calc/compare_px_r5.py` (+`_out.txt`). **Không email, không đặt lệnh, không sửa plan.**
