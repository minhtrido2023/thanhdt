# DD — VCB (Ngân hàng TMCP Ngoại thương Việt Nam) · REV 2 · BCTC Q3/2026 · 2026-11-23 · job `Taylor_20261122_234428`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua; user quyết. Không ghi `dd_price_zones.json`, không email.
> Rev này thay `REPORT.md` (rev 1, dd_date 2026-11-17, sổ: tâm 38.800 / vùng 30.800–42.000), sau khi skeptic DD_GENERAL
> 22/11/2026 phán **REFUTED** (`skeptic/r1.json`). Bản cũ giữ nguyên, không ghi đè.
> **Nguồn số:** [KT20xx] = BCTC hợp nhất KIỂM TOÁN năm 20xx, đọc ảnh scan từng trang trong phiên này (23/11/2026):
> 2025 = `src/VCB_BCTC_2025_KT_HN.pdf` (EY); 2017/2019/2021/2023 tải từ
> `static2.vietstock.vn/data/HOSE/<năm>/BCTC/VN/NAM/VCB_Baocaotaichinh_<năm>_Kiemtoan_Hopnhat.pdf` (KPMG 2017–2021, EY 2023).
> [Q3] = `src/VCB_BCTC_Q3_2026_HN.pdf`. [BQ] = `tav2_bq.ticker_financial`. [Báo] = báo chí, ghi rõ.
> **Khoá giả định:** `assumptions_VCB_rev2_20261123.json` md5 `460425ce1cc0aeec737dfe1d6ae7b6de` (+ phần bảng cân đối/KQKD Q3
> giữ từ `assumptions_VCB_20261117.json` md5 `85d41e08f834127e57cd740ed88dd931`); tính bằng `calc_rev2.py`
> (md5 `1bfc732477fcb301d6163d11e5296fd0`) → `calc_rev2_output.txt` (md5 `9c8c90bfe8d24e23b9c4282c4bd68f40`).
> `bin/dd_assumptions_lint.py`: rc=0, 19 cảnh báo (file chưa theo schema v1 — giai đoạn chỉ cảnh báo; nội dung khoá đủ cho mô hình P/B ngân hàng).
> **Mù giá:** giả định khoá trước khi so giá. Không truy vấn giá mới; giá đối chiếu duy nhất là 52.100 (17/11/2026) đã có trong rev 1, chỉ dùng ở mục "Sau khoá".

## 0. Kết luận

**Ở r 13,5% của fleet, giá trị có trọng số là 44.900 đ/cp (kịch bản cơ sở 47.300; xấu 26.200 / tốt 58.900). Vùng hợp lý 38.900–53.100 (Ke ±100bp trên giá trị có trọng số).**
Tâm tăng +15,7% so với rev 1 (38.800) vì **chi phí tín dụng chuẩn hoá nay có chuỗi kiểm toán 9 năm làm cơ sở (0,62%)** thay cho
mức 0,8% không nguồn, và vì bỏ phép lấy trung điểm hai mốc ROE bằng phán đoán. Rủi ro tụt NIM theo chỉ đạo và tầng nợ sớm
chuyển sang kịch bản xấu có xác suất, không vào base (luật V4/user 03/11).

| Mục | Số | Nguồn |
|---|---|---|
| BVPS 30/09/2026 | **30.359 đ** (VCSH mẹ 253.669 tỷ / 8.355,7 triệu cp); BQ 30.370 (Δ0,04%) | [Q3], [BQ] |
| Chi phí tín dụng (CC) chuẩn hoá — base | **0,62%** dư nợ BQ = tổn thất thực 2017–2025 **0,49%** + duy trì tỷ lệ dự phòng 1,49% khi dư nợ tăng 9% **0,12%** | [KT2017–2025], `calc_rev2.py` |
| CC lịch sử (chi phí dự phòng / dư nợ BQ) | TB 2017–2025 **0,87%** (trung vị 0,99%) · TB 2021–25 0,61% · TB 2023–25 0,28% · 9T/26 năm hoá 0,70% (tổng), 0,47% (chỉ cho vay) | [KT], [Q3] |
| Biên PPOP / dư nợ BQ | 2022 4,45% → 2025 **3,02%** (đáy) → 9T/26 lõi **3,55%**; TB 5 năm 2022–26 3,63% | [KT], [Q3] |
| ROE bền — base | **17,1%** = (3,55% − 0,62%) × đòn bẩy dư nợ/VCSH 7,30 × (1 − thuế 20%) | `calc_rev2.py` |
| Kịch bản | Xấu 0,25: ROE 12,6% ⇒ **26.200** · Cơ sở 0,50: 17,1% ⇒ **47.300** · Tốt 0,25: 19,6% ⇒ **58.900** · **Có trọng số 44.900** | `calc_rev2.py` |
| Thanh khoản (V3) | Chiết khấu **0%** ⇒ giá trị trước = sau = 44.900 | mục V3 |
| Moat (V5, tái dùng 5F 17/11) | **NARROW** — không thưởng, không trừ | mục 6 |
| Pháp lý | WARNING: KTNN hồi tố 2025 (nhỏ); thanh tra chi nhánh; VCBNeo (ex-CBBank) **không kiểm chứng được** quy mô | mục 8 |
| Sau khoá | Giá 52.100 (17/11) = **+16%** so với tâm có trọng số, **trong** vùng hợp lý, dưới đầu trên 53.100 | mục 7 |

**Đọc nhanh:** VCB **không rẻ** ở r 13,5%: giá ở nửa trên vùng hợp lý. Rev 1 kết luận "đắt, trên vùng" là do CC 0,8% không nguồn
và trung điểm phán đoán; khi CC được neo vào số kiểm toán, giá 52.100 cần ROE bền ≈ 18,2% (ở Ke 13,5%) — cao hơn base 17,1% nhưng
thấp hơn kịch bản tốt 19,6%. Biến số lớn nhất còn lại là **biên PPOP** (2025 đáy 3,02% ⇒ 33.000; 2026 lõi 3,55% ⇒ 47.300).

---

## 1. Đính chính so với rev 1 (từng hạng mục skeptic r1)

| # | Hạng mục skeptic r1 | Chiều | Xử lý trong rev 2 | Loại |
|---|---|---|---|---|
| 1 | CC 0,8% áp cho cả hai mốc ROE **không có nguồn** (killer objection) | tâm có thể quá thấp | Dựng chuỗi CC 2017–2025 từ 5 bộ BCTC kiểm toán gốc (bảng mục 3). Base = **tổn thất thực 0,49% + duy trì dự phòng 0,12% = 0,62%**; đối chiếu độc lập: TB 2021–25 = 0,61%. 0,87% (TB 9 năm, gồm pha tích luỹ bao phủ) chuyển sang kịch bản xấu. In lưới CC 0,5 / 0,6 / 0,8 / 0,87% (mục 5) | (a) vào base có nguồn |
| 2 | Tâm r1→r3 hạ 42.035→35.497 do **trung điểm phán đoán**, không do BCTC mới | thiên lệch bảo thủ | **Bỏ trung điểm.** Base dùng biên PPOP lõi 9T/26 (3,55%), có kiểm chéo độc lập: TB 5 năm 3,63%, và 2018–2022 đều ~4,2–4,4% ⇒ 2026 **không phải đỉnh** so lịch sử. Đáy 2025 (3,02%) + CC 0,87% = kịch bản xấu (P 0,25), căn cứ rủi ro cụ thể: chỉ đạo giảm lãi vay CV 9608/9736 [Bobby §2a] | (a) + (b) |
| 3 | Số KT 2025 (PPOP 47.211,8; dư nợ cuối 2024 1.449.198,9; VCSH cuối 2024 196.112,9) lấy từ dispatch, **chưa render từ PDF** | nguồn | **Đã đọc lại từ PDF:** B03 tr.9 PPOP **47.211.823** tr ✓; B02 tr.6 dư nợ 31/12/2024 **1.449.198.899** ✓; B02 tr.7 VCSH 196.209.168 − CĐKKS 96.261 = **196.112.907** ✓; VCSH cuối 2025 224.558.726 − 71.521 = 224.487.205 ✓ (chênh 29 tỷ với số trình bày lại Q3 = điều chỉnh KTNN) | (a) đã kiểm |
| 4 | Bảo lãnh ×2,37 và Xây dựng +72% **chưa đối chiếu src/** | nguồn | **Đã đọc:** [KT2025] B02 tr.8 bảo lãnh vay vốn 286,9 / bảo lãnh khác 58.052,5 (31/12/2024); [Q3] B02a tr.5: 9.549,9 / 128.899,8 ⇒ tổng **138.449,7 / 58.339,4 = ×2,37** ✓. [KT2025] TM9 tr.38 Xây dựng **90.513,0 → 155.288,0 = +71,6%** ✓. Vẫn chỉ WARNING (không có cơ sở độc lập về tổn thất) — đã gói vào CC 0,87% của kịch bản xấu | (b) |
| 5 | Thuế mô hình 20% so với thực 18,3% | nhỏ | **Giữ 20%, nay có nguồn:** ETR 2025 kiểm toán 8.821,7 / 44.019,6 = **20,04%** [KT2025 B03 tr.10]; 18,3% của 9T/26 thấp do lãi đánh giá lại hợp nhất 3.171 tỷ không chịu thuế | (a) |
| 6 | Trừ −2.850 đ (−8%) sau GDKHQ cổ tức tiền **vô điều kiện**, mâu thuẫn lịch sử 450 đ | tâm thấp sai | **Đã sửa.** Cổ tức tiền 2025 = **450 đ/cp (~3.760 tỷ), GDKHQ trước 24/07, trả 27/08/2026** [Báo vietnamplus 10/07/2026] ⇒ đã trừ sẵn trong VCSH 30/09. Phần còn lại 20.331 − 3.760 = 16.571 tỷ: **hình thức chưa công bố** ("đang trình cơ quan nhà nước" [baodautu 24/04/2026]); tiền lệ 2025 chia cổ phiếu 49,5% (vốn điều lệ 55.890,9 → 83.556,8 tỷ, [KT2025] B02 tr.7). Base: không trừ. Nếu bằng tiền: −1.983 đ/cp (mục 5, có điều kiện) | (b) điều kiện |
| 7 | **VCBNeo (ex-CBBank)** không định lượng; miễn hợp nhất/CAR có thể hết | tâm có thể quá cao | Tìm BCTC Q3, BCTC KT 2025, báo chí, ĐHĐCĐ 2026: **không có** số vốn, lỗ luỹ kế hay cam kết hỗ trợ. ⇒ **KHÔNG KIỂM CHỨNG ĐƯỢC.** Độ nhạy minh hoạ (ước lượng): tổn thất 5 / 10 / 20 nghìn tỷ vào VCSH ⇒ 46.400 / 45.400 / 43.600 (−2% / −4% / −8% so base). Không vào base | (c) |
| 8 | CAR một nguồn báo; thiếu CET1, LDR TT22, Pillar 3 | tâm có thể quá cao | CAR hợp nhất 30/06/2026 **11,14%** (nhiều nguồn báo: vcci, 24hmoney, ACBS 07/08/2026) — vẫn **chưa có Pillar 3**; CET1 và LDR TT22: **không kiểm chứng được**. Độ nhạy: nếu phải đưa CAR lên 12% bằng giảm đòn bẩy ⇒ ROE 15,9% ⇒ **41.600** (−12%). Không vào base | (b)/(c) |
| 9 | Nhóm 2 +85%, nhóm 3–4 ×4, bảo lãnh ×2,37, Xây dựng +72% **không mô hình hoá** | tâm có thể quá cao | Nay đi vào kịch bản xấu qua CC 0,87% (TB 9 năm, gồm 2020–21 COVID 1,27–1,31%). Base không đổi vì chưa có cơ sở độc lập rằng tổn thất vượt chuỗi lịch sử; nhóm 2 = 0,28% dư nợ, dự phòng 31.168 tỷ = 1,75× toàn bộ nhóm 2–5 (17.812 tỷ) | (b) |
| 10 | Phát hành riêng lẻ 6,5% chưa mô hình | tâm có thể quá thấp | Giữ ngoài base (giá phát hành chưa biết; NPV=0 ở giá sổ sách theo V4a). Ghi điều kiện đổi nhận định | (b) |
| 11 | Quỹ khen thưởng phúc lợi | nhỏ | Skeptic tự đánh giá nhỏ (khoảng trống VCSH 9T/26 giải thích chủ yếu bằng cổ tức 450 đ). Không điều chỉnh | — |

**Flip-flop minh bạch:** rev1 r1 42.035 (ROE 16%) → r3/r4 35.497 (ROE 14,6%) → **rev 2 base 47.294 (ROE 17,1%)**. Lần đổi này có
đầu vào MỚI kiểm chứng được: 9 năm chi phí dự phòng/dư nợ và biên PPOP đọc từ BCTC kiểm toán gốc. Không có đầu vào nào đến từ giá.

## 2. Chất lượng lợi nhuận (9T/2026, hợp nhất, tỷ đồng) — giữ từ rev 1, đã kiểm lại thuế

| Dòng | 9T/26 | 9T/25 | Δ |
|---|---|---|---|
| Thu nhập lãi thuần | 57.179 | 42.505 | +34,5% |
| PPOP | 49.620 | 35.470 | +39,9% (lõi, bỏ một lần 3.171: +30,9%) |
| Tổng dự phòng (cho vay 6.190 + TPDN 2.997) | (9.180) | (2.338) | ×3,9 |
| LNTT | 40.440 | 33.133 | +22,1% |
| LNST mẹ | 33.032 | 26.549 | +24,4% headline; **lõi 29.861, +12,5%** |

Khoản một lần 3.171 tỷ: lãi đánh giá lại khi Bonday-Bến Thành thành công ty con (giải trình LNST mục 2, TM8), không chịu thuế.
NII/dư nợ BQ: 2022 5,06% → 2023 4,44% → 2024 4,08% → **2025 3,76%** → 9T/26 4,37% (`calc_rev2.py`) ⇒ 2026 hồi về mức 2023, chưa vượt.

## 3. Chuỗi chi phí tín dụng & biên PPOP — BCTC kiểm toán gốc (tỷ đồng)

| Năm | Dư nợ KH cuối kỳ | Chi phí dự phòng RRTD (B03) | CC / dư nợ BQ | PPOP | PPOP / dư nợ BQ | Nguồn (trang báo cáo) |
|---|---|---|---|---|---|---|
| 2016 | 460.808 | 6.369 | — | 14.947 | — | KT2017 B02 tr.6, B03 tr.9 |
| 2017 | 543.434 | 6.198 | 1,23% | 17.540 | 3,49% | KT2017 |
| 2018 | 631.867 | 7.398 | 1,26% | 25.667 | 4,37% | KT2019 |
| 2019 | 734.707 | 6.790 | 0,99% | 29.913 | 4,38% | KT2019 |
| 2020 | 839.788 | 9.975 | 1,27% | 33.024 | 4,19% | KT2021 |
| 2021 | 960.750 | 11.761 | 1,31% | 39.149 | 4,35% | KT2021 |
| 2022 | 1.145.066 | 9.464 | 0,90% | 46.832 | 4,45% | KT2023 |
| 2023 | 1.270.359 | 4.565 | 0,38% | 45.809 | 3,79% | KT2023 |
| 2024 | 1.449.199 | 3.315 | 0,24% | 45.551 | 3,35% | KT2025 |
| 2025 | 1.673.526 | 3.192 | 0,20% | 47.212 | 3,02% | KT2025 |
| 9T/26 năm hoá | 1.816.093 (30/09) | 12.240 | 0,70% | 61.932 lõi | **3,55%** | Q3 |

**Tách tổn thất thực khỏi tích luỹ bao phủ:** tổng chi phí dự phòng 2017–2025 = 62.659 tỷ; số dư dự phòng tăng 20.070 tỷ (cho vay
8.087 → 24.976; CK đầu tư 180 → 3.362; liên NH 0 → 0) ⇒ tổn thất đã dùng dự phòng (xoá nợ) ≈ 42.588 tỷ = **0,49%** tổng dư nợ BQ.
Duy trì tỷ lệ dự phòng/dư nợ 1,49% (cuối 2025) khi dư nợ tăng 9%/năm (ước lượng, gần mức tăng 9T/26 năm hoá) cần thêm **0,12%**.
⇒ **CC chuẩn hoá 0,62%.** Kiểm chéo: TB 2021–2025 = 0,61% (chu kỳ đủ COVID + hoàn nhập). Năm 2025 thấp vì **hoàn nhập dự phòng
cụ thể** (dự phòng cụ thể 20.495 → 12.553 sau xoá 7.288; [KT2025] TM10 tr.39) — không phải mức bền, nên không lấy 0,2% làm base.

## 4. Chất lượng tài sản, ngoại bảng, vốn [Q3, KT2025]

| Chỉ tiêu | 30/09/2026 | 31/12/2025 |
|---|---|---|
| Nhóm 2 | 4.995 (0,28%) | 2.702 (0,16%) |
| Nợ xấu nhóm 3–5 | 12.817 (**0,71%**) | 9.714 (0,58%) |
| Dự phòng cho vay | 31.168; bao phủ **243%** | 24.980; 257% |
| Nợ khó đòi đã xử lý (ngoại bảng) | 83.482,8 | 83.546,3 ⇒ **không xoá nợ mới 9T** |
| Bảo lãnh (vay vốn + khác) | **138.449,7** (≈55% VCSH) | 99.093,7 (31/12/2024: 58.339,4) |
| Dư nợ Xây dựng | n/a | **155.288** (2024: 90.513, +71,6%) |
| CAR hợp nhất | 11,14% (30/06, [Báo] nhiều nguồn; chưa Pillar 3) | — |
| CET1 / LDR TT22 | **không kiểm chứng được** | — |

⚠️ WARNING (không nhân vào base): nhóm 2 +85% YTD khi dư nợ +8,5%; nhóm 3–4 tăng 1.063 → 4.229; bảo lãnh ×2,37 trong 21 tháng; Xây dựng +71,6% năm 2025. Đều đi vào kịch bản xấu qua CC 0,87%.

**Cổ đông/hành động vốn:** Nhà nước 74,80%, Mizuho 15,00% [Q3 TM1(b)]; 8.355.675.094 cp không đổi 9T. Chờ thực hiện: thưởng từ quỹ dự
trữ bổ sung vốn điều lệ tối đa ~1.068 triệu cp (~10.686–10.687 tỷ, ≈12,8%) [nhandan, baodautu 24/04/2026]; phân phối 16.571 tỷ còn lại của
LN 2025 (hình thức chưa công bố); riêng lẻ ≤6,5% (543,1 triệu cp). Cổ phiếu thưởng/cổ tức cổ phiếu chỉ chia nhỏ, không đổi giá trị.

**VCBNeo (ex-CBBank, NH nhận chuyển giao bắt buộc, giá 0 đồng, QĐ 2299/QĐ-NHNN 17/10/2024):** miễn hợp nhất và loại khỏi CAR. Không
có thuyết minh quy mô/lỗ luỹ kế/hỗ trợ trong BCTC; báo chí 03–07/2026 chỉ nói "bắt đầu có lãi" (vneconomy, vnba, không có số) ⇒
**không kiểm chứng được**; độ nhạy ở mục 5.

## 5. Định giá — P/B = (ROE − g)/(Ke − g), mù giá thị trường

**Không áp dụng cho ngân hàng:** P/PCF, EV/EBITDA, FCFE ⇒ **V6 (hai nền V_ngắn/V_dài, C4, D2) không áp** (CFO ngân hàng chứa biến động tiền gửi/cho vay).

**V1 — r:** r = **13,5%** tại neo 03/11/2026; lãi huy động 12T hiệu dụng `deposit_rate_vn` = 7,40% (CCTG 12M, 02/11/2026; đo trong rev 1 ngày 17/11, chưa có số mới) ⇒ Δ = 0, không điều chỉnh. β pass-through 1 (độ nhạy 0,5).
D4: hai đầu dải Ke nội địa 12,3% / 13,4% ⇒ base **58.000 / 48.000**. Mốc đọc Ke theo β thật (0,76 thô, Blume 0,84; rev 1) 12% ⇒ 61.500 — chỉ đọc, không làm tâm.

**ROE bền** = (biên PPOP − CC) × (dư nợ BQ / VCSH mẹ BQ 9T/26 = 7,30) × (1 − 20%). g = 7% (ước lượng; ≤ GDP danh nghĩa; tỷ lệ chia hàm ý 1 − g/ROE = 59%).

| Kịch bản | P | Biên PPOP | CC | ROE | P/B | Giá trị/cp |
|---|---|---|---|---|---|---|
| Xấu — NIM về đáy 2025 theo chỉ đạo giảm lãi + tổn thất kiểu 2017–21 | 0,25 | 3,02% (2025 KT) | 0,87% (TB 9 năm) | 12,6% | 0,86 | **26.200** |
| **Cơ sở** | 0,50 | 3,55% (9T/26 lõi) | 0,62% (tổn thất + duy trì) | **17,1%** | 1,558 | **47.300** |
| Tốt — biên TB 5 năm, CC chu kỳ hoàn nhập | 0,25 | 3,63% (TB 2022–26) | 0,28% (TB 2023–25) | 19,6% | 1,94 | **58.900** |
| **Có trọng số** | | | | | | **44.900** |

Xác suất 0,25/0,50/0,25 giữ như rev 1 (không có cơ sở mới để đổi).

**Lưới CC trên biên base 3,55%** (yêu cầu skeptic): 0,5% ⇒ 50.500 (ROE 17,8%) · 0,6% ⇒ 47.700 (17,2%) · 0,8% ⇒ 42.300 (16,0%) · 0,87% ⇒ 40.500 (15,7%).
**Lưới biên PPOP ở CC 0,62%:** 3,02% ⇒ 33.000 · 3,55% ⇒ 47.300 · 3,63% ⇒ 49.600.

**Độ nhạy theo lãi huy động (V1), base:**

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β = 1 | 55.900 (+18%) | 51.200 (+8%) | 47.300 | 43.900 (−7%) | 41.000 (−13%) |
| β = 0,5 | 51.200 | 49.200 | 47.300 | 45.500 | 43.900 |

Giá trị có trọng số ở Ke ±100bp: **53.100 / 38.900** ⇒ vùng hợp lý. g 6% / 8% ⇒ 45.000 / 50.400.

**Độ nhạy KHÔNG vào base:**
- CAR lên 12% bằng giảm đòn bẩy (D-SIB giả định): ROE 15,9% ⇒ **41.600** (−12%).
- VCBNeo tổn thất vào VCSH (ước lượng minh hoạ, không kiểm chứng được): 5 / 10 / 20 nghìn tỷ ⇒ 46.400 / 45.400 / 43.600.
- Nếu 16.571 tỷ còn lại chia **bằng tiền** (có điều kiện, chưa công bố): −1.983 đ/cp ⇒ base sau GDKHQ 44.200, tổng cho cổ đông gồm tiền 46.200; có trọng số sau GDKHQ 42.000. Nếu bằng cổ phiếu (≈19,8% số cp): không đổi giá trị. **Vùng giá chỉ trừ khi có thông báo trả tiền.**
- Hai giai đoạn (hiển thị): Ke 13,5%, g1 13% / 10% ⇒ 51.700 / 49.400; Ke 12,5% ⇒ 62.800 / 59.100.

**Vùng đọc:** rẻ ≤ **38.200** (0,85 × tâm có trọng số) · hợp lý **38.900–53.100** · trên **53.100** = đắt theo r 13,5%.

**V4:** VIFC (NH con 3.000 tỷ vốn), riêng lẻ 6,5%, VCBNeo đều là đầu tư/hành động vốn mới ⇒ base NPV = 0 ở giá sổ sách. Không có capex tuân thủ đáng kể ngoài chi phí hoạt động (đã trong PPOP).

## 6. Vị thế & lợi thế cạnh tranh (5F) — V5: tái dùng bản 17/11 (<12 tháng) + kiểm nhanh

Bản đầy đủ: `REPORT.md` §6 (17/11/2026): **moat_tier NARROW**, moat_type = chi phí vốn (CASA 31,8% vs ngành 19,4%) + chất lượng tài sản
(NPL 0,71% vs ngành 2,09%); rủi ro số 1 = nghĩa vụ chính sách (chỉ đạo lãi vay, NH chuyển giao, quy chế KBNN).
Kiểm nhanh 23/11: (i) ROE base 17,1% > Ke 13,5% — điều kiện (i) đúng lại (rev 1 yếu đi vì ROE 2025 chuẩn hoá bằng CC 0,8% = 13,2%);
biên PPOP giảm 4,45% → 3,02% (2022–25) vẫn là đồng hồ cắt hào. Không thưởng, không trừ. Độ nhạy WIDE (ROE 19,6% = kịch bản tốt) 58.900 · NARROW 47.300 · NONE (ROE = Ke) 30.400 (= BVPS).

## 7. Sau khoá — V3 thanh khoản, so giá, sizing

- **V3:** ADV trung vị 3 năm 175 tỷ/phiên (rev 1, BQ đến 17/11/2026). Tham gia 10–20% ⇒ 17,5–35 tỷ/phiên; vị thế 2–4% NAV ở quy mô fleet (dưới vài chục tỷ, ước lượng) thoát ≤2 phiên. Free float ~10% không ràng buộc ở quy mô này ⇒ **chiết khấu 0%**, giá trị trước = sau = 44.900.
- **So giá** (52.100, 17/11/2026, rev 1; không truy vấn lại): P/B 1,72; **+16%** so tâm có trọng số, +10% so base; trong vùng hợp lý, cách đầu trên 53.100 ~2%. Giá hàm ý ROE 18,2% ở Ke 13,5%, hoặc Ke 12,9% ở ROE 17,1% (ước lượng từ công thức P/B).
- **Nhãn:** "hợp lý, nghiêng đắt" ở r 13,5%; chưa chạm vùng rẻ ≤ 38.200.
- **V8 sizing:** nếu user cân nhắc, khung chuẩn 2–4% NAV; ở giá hiện tại đề xuất **không quá đầu dưới 2%** vì giá trên tâm 16%. Không phải tín hiệu mua.

## 8. Pháp lý / quản trị — chỉ WARNING

- KTNN điều chỉnh hồi tố 2025, quy mô nhỏ (VCSH +29 tỷ; khớp chênh 224.487 vs 224.516). EY 2025: chấp nhận toàn phần.
- Thanh tra NHNN cấp chi nhánh 2026 (Đà Nẵng, Bình Phước) [Báo/DNSE]; không thấy vụ án.
- Nghĩa vụ chính sách: VCBNeo (không kiểm chứng được), chỉ đạo giảm lãi, phê duyệt hình thức cổ tức/tăng vốn bởi cơ quan chủ sở hữu.
- BCTC Q3 không soát xét.

## 9. Điều kiện đổi nhận định (hai chiều)

**Tâm ↑:** BCTC Q4/2026 biên PPOP cả năm ≥ 3,55% và CC ≤ 0,62%; lãi huy động hiệu dụng −50bp (+8%); riêng lẻ ≥ 1,5× BVPS; công bố cổ tức cổ phiếu cho 16.571 tỷ (xoá rủi ro trừ tiền).
**Tâm ↓:** biên PPOP Q4 quay về ≤ 3,1% (đáy 2025) — base chuyển sang kịch bản xấu; NPL > 1,0% hoặc nhóm 2–4 > 1,0% dư nợ; CC năm 2026 > 0,87%; CAR/CET1 công bố < 11% buộc giảm đòn bẩy (−12%); công bố hỗ trợ VCBNeo > 5 nghìn tỷ hoặc bỏ miễn trừ hợp nhất/CAR; lãi huy động +50bp (−7%); 16.571 tỷ trả bằng tiền (vùng −1.983 đ sau GDKHQ).
**Theo dõi:** BCTC Q4/2026 (~01/2027), Pillar 3, nghị quyết/CBTT hình thức cổ tức, thông tin VCBNeo.

## 10. Không kiểm chứng được / còn thiếu

- VCBNeo: vốn, lỗ luỹ kế, cam kết hỗ trợ, thời hạn miễn trừ — **không có nguồn**; ảnh hưởng ước lượng −2% … −8% base (mục 5).
- CET1, LDR theo TT22, Pillar 3 CAR — **không có**; CAR 11,14% chỉ từ báo chí (nhiều nguồn cùng con số).
- Hình thức phân phối 16.571 tỷ LN 2025 — chưa công bố; nghị quyết ĐHĐCĐ gốc chưa đọc được (bài báo trước kết quả ĐHĐCĐ).
- Tổn thất 2016 trở về trước, dư nợ cuối 2015: không dùng (chuỗi từ 2017).
- File khoá chưa theo schema `dd_assumptions_v1` (lint cảnh báo, rc=0).

## Nguồn
- BCTC hợp nhất kiểm toán VCB 2017/2019/2021/2023/2025: `https://static2.vietstock.vn/data/HOSE/<năm>/BCTC/VN/NAM/VCB_Baocaotaichinh_<năm>_Kiemtoan_Hopnhat.pdf`
- BCTC Q3/2026: https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%203/VCB_Baocaotaichinh_Q3_2026_Hopnhat.pdf
- Cổ tức 450 đ: https://www.vietnamplus.vn/vietcombank-chuan-bi-chi-hon-3760-ty-dong-tra-co-tuc-tien-mat-cho-co-dong-post1123414.vnp
- ĐHĐCĐ 2026: https://baodautu.vn/dhdcd-vietcombank-dang-tim-nha-dau-tu-de-chao-ban-65-von-du-chi--20331-ty-dong-tra-co-tuc-d576464.html · https://nhandan.vn/ocop/vietcombank-thong-qua-ke-hoach-phat-hanh-hon-1-ty-co-phieu-thanh-lap-ngan-hang-tai-trung-tam-tai-chinh-quoc-te-viet-nam-post958144.html
- CAR 30/06/2026: https://vcci.com.vn/tin-tuc/tu-nen-tang-tai-chinh-vung-chac-vietcombank-mo-rong-du-dia-tang-truong-moi · https://24hmoney.vn/news/vcb-giu-phong-do-tai-san-vuot-2-67-trieu-ty-c1a2806199.html · https://acbs.com.vn/acbsmedia/2026/08/VCB_cap-nhat_ACBS_07.08.2026-VN.pdf
- VCBNeo: https://en.vneconomy.vn/clear-signs-of-recovery-from-four-weak-banks.htm · https://vnba.org.vn/en/transferred-weak-banks-under-restructuring-17545.htm
- Ngành (đọc mù): `kb/data_registry/market-state/sector_read_ngan_hang_quoc_doanh_20261117.md`; vĩ mô: `macro_snapshot_20261117.md`.
