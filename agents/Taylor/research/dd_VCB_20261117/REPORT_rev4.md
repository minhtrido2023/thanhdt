# DD — VCB (Ngân hàng TMCP Ngoại thương Việt Nam) · REV 4 · BCTC Q3/2026 · 2026-11-23 · job `Taylor_20261123_120305`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua, user quyết. Không ghi `dd_price_zones.json`, không email.
> Chuỗi bản: `REPORT.md` (rev 1) → r1 REFUTED → `REPORT_rev2.md` → r2 REFUTED → `REPORT_rev3.md` (sổ rev 2: tâm 36.000, vùng 31.200–42.500)
> → r3 INCONCLUSIVE (`skeptic/r3.json`) → **bản này** (vòng skeptic cuối r4). Các bản cũ giữ nguyên.
> **Nguồn số:** [KT20xx] = BCTC hợp nhất KIỂM TOÁN (2017/2019/2021/2023 tải từ static2.vietstock.vn; 2025 = `src/VCB_BCTC_2025_KT_HN.pdf`);
> [Q3] = `src/VCB_BCTC_Q3_2026_HN.pdf`; [Báo] = báo chí, ghi rõ. Không có số mới ngoài các nguồn này.
> **Khoá giả định:** `assumptions_VCB_rev4_20261123.json` md5 `20dc556d1869d2d21ee1d7b0efb4a208` (+ BS/IS Q3 từ `assumptions_VCB_20261117.json`
> md5 `85d41e08f834127e57cd740ed88dd931`); `calc_rev4.py` md5 `599ddceb38a7f67fce5b9b31b37a9d71` → `calc_rev4_output.txt` md5 `b2bf5f62cbb3f0665fc61fee73e9b959`.
> `bin/dd_assumptions_lint.py`: rc=0, 21 cảnh báo schema v1 (giai đoạn cảnh báo).
> **Mù giá:** khoá giả định trước khi so giá; không truy vấn giá mới. Giá đối chiếu duy nhất 52.100 (17/11/2026), chỉ ở mục 7.

## 0. Kết luận

**Ở r 13,5%, giá trị có trọng số là 35.600 đ/cp (cơ sở 37.400; xấu 23.000 / tốt 44.700). Vùng hợp lý 30.900–42.100 (Ke ±100bp trên giá trị có trọng số). Giá 52.100 (17/11) nằm TRÊN vùng, cao hơn tâm 46%.**

| Mục | Số | Nguồn |
|---|---|---|
| BVPS 30/09/2026 sau trừ KTPL 2026 ước tích | **30.024 đ** (30.359 − 334) | [Q3], TM34(a) [KT2025], `calc_rev4.py` |
| Đòn bẩy (cuối kỳ, nhất quán BVPS) | **7,24** = dư nợ 1.816.093 / VCSH mẹ sau KTPL 250.875 | [Q3] |
| ROE thuộc cổ đông — cơ sở | **15,1%** = spread 2,85% × 7,24 × (1 − 20%) × (1 − 8,46%) | `calc_rev4.py` |
| Kịch bản (mỗi kịch bản MỘT cửa sổ đo được) | Xấu 0,25 (năm KT 2017, spread 2,26%) ⇒ **23.000** · Cơ sở 0,50 (9T/26, 2,85%) ⇒ **37.400** · Tốt 0,25 (2022–26, 3,15%) ⇒ **44.700** | `calc_rev4.py` |
| Thanh khoản (V3) | chiết khấu **0%** | mục 7 |
| Moat (V5) | **NARROW** (tái dùng 5F 17/11) | mục 6 |
| Không kiểm chứng được | VCBNeo (vốn/lỗ luỹ kế); CET1/LDR TT22/Pillar 3; nguyên nhân NII 2026 | mục 10 |

**Đọc nhanh:** VCB **đắt** ở r 13,5%. So rev 3, tâm giảm **−1,0%** (36.000 → 35.600). Có ba thay đổi kéo ngược chiều nhau: kịch bản xấu dựng từ năm kiểm toán thật (+), KTPL 2026 và đòn bẩy cuối kỳ (−). Chọn cửa sổ cơ sở vẫn là điểm phán đoán lớn nhất. Nếu cơ sở lấy cửa sổ chu kỳ 2017–25, tâm có trọng số lên **38.300** (+7,6%) và vẫn dưới giá 27%.

---

## 1. Đính chính — từng hạng mục skeptic r3

| # | Hạng mục r3 | Xử lý rev 4 | Loại | Chiều tâm |
|---|---|---|---|---|
| r3-1 | **Cửa sổ cơ sở 9T/26 (killer):** spread 2,85% gần đáy 9 năm; chu kỳ 2017–25 cho +14% | Giữ 9T/26 làm cơ sở, kèm **bằng chứng độc lập**. (i) Cửa sổ kiểm toán FY2025 tách biệt cho spread **2,82%**, gần như trùng 9T/26 (2,85%), nên cơ sở không phụ thuộc vào cú nhảy NII 2026 (FY2025 ⇒ 36.700, −1,9% so base). (ii) Spread kiểm toán giảm **đơn điệu** 2022→2025: 3,55 / 3,42 / 3,11 / 2,82%. Đây là chế độ hiện hành, không phải dao động một quý. Chu kỳ 2017–25 (3,07% ⇒ 42.800) và trung vị năm (3,11% ⇒ 43.700) **không bị bỏ**: hiển thị ở mục 5, đồng thời nằm sát kịch bản tốt (3,15%). Nếu cơ sở = chu kỳ 2017–25 thì có trọng số = **38.300** | (a) chứng cứ + (b) độ nhạy | 0 (chọn), ± hiển thị |
| r3-2 | **Kịch bản xấu dưới mọi năm kiểm toán** (ghép stress 2,16%) | Thay bằng **năm kiểm toán tệ nhất 2017** (biên 3,49%, CC 1,23%, spread **2,26%**) ⇒ 23.000 (rev 3: 21.200) | (a) | **+** |
| r3-3 | **Đòn bẩy BQ 7,30 nhân BVPS cuối kỳ** | Dùng đòn bẩy **cuối kỳ** trên VCSH đã trừ KTPL ước tích: 7,24 (chưa trừ: 7,16) | (a) | **−** |
| r3-4 | **KTPL 2026 chưa trích trong BVPS 30/09** | Trừ 8,46% (tỷ lệ kiểm toán 2025, TM34(a)) × LNST mẹ 9T/26 33.032 = **2.794 tỷ = 334 đ/cp**. Đây là ước lượng tỷ lệ × LN, thấp hơn ước lượng 405 đ của skeptic | (a) tỷ lệ kiểm toán, số tiền ước lượng | **−** |
| r3-5 | **NII/dư nợ 3,76% → 4,37% chưa giải thích nhưng nằm trong base** | Nguyên nhân: **không kiểm chứng được** từ BCTC quý. Ảnh hưởng tới base đã được giới hạn: cửa sổ FY2025 không có cú nhảy, cho 36.700 (−1,9%). Đảo chiều sâu hơn (biên quay về 3,02% với CC 0,70%) nằm trong kịch bản xấu | (c) + chặn bằng (a) | 0 |
| r3-6 | **Gordon ROE bất biến dù biên giảm 2022–25** | Không đổi mô hình. Xu hướng giảm biên đã vào xác suất kịch bản xấu (0,25). Hai giai đoạn chỉ hiển thị (rev 3 §5). Biên giảm thêm ⇒ điều kiện đổi nhận định mục 9 | (b) | 0 |
| r3-7 | **VCBNeo chưa định lượng** | Tìm lại 23/11: không có BCTC/vốn/lỗ luỹ kế công khai. Báo chí ([doanhnhan.baophapluat.vn], [vnba 04/08/2026]) chỉ nói LN 2025 ≈ 2.000 tỷ, chưa phải số kiểm toán. ⇒ **không kiểm chứng được**. Độ nhạy minh hoạ (ước lượng): tổn thất 5/10/20 nghìn tỷ vào VCSH ⇒ base 36.700 / 35.900 / 34.400 (−2% … −8%) | (c) | không vào base |
| r3-8 | **CET1 / LDR TT22 / Pillar 3** | Tìm 23/11: không thấy Pillar 3 30/06/2026 công khai ⇒ **không kiểm chứng được**. CAR 11,14% chỉ từ báo. Độ nhạy CAR 12%: 32.400 (−13%) | (c) | không vào base |
| r3-9 | **CASA dẫn lại từ bản 17/11** | Nguồn gốc là [Q3] TM tiền gửi KH: không kỳ hạn 566.125,6 / tổng 1.781.703,0 = **31,8%** (`assumptions_VCB_20261117.json`, đọc từ BCTC Q3) | (a) | 0 |
| r3-10 | **Pha loãng: thiếu quy tắc chia lại vùng** | Quy tắc: sau GDKHQ phát hành cổ phiếu, vùng/cp × N_cũ/N_mới, với N_mới lấy theo CBTT. Chỉ thưởng 12,8%: ×0,8865 ⇒ vùng **27.400–37.300**, tâm 31.600. Thưởng + 16.571 tỷ chia cổ phiếu (19,8%): ×0,754. Trả TIỀN: trừ 1.983 đ/cp | (a) quy tắc | 0 (giá trị không đổi) |
| r3-11 | **Nhãn `cc_bull_source` sai** | Sửa trong file khoá rev 4: "TB 5 cửa sổ 2022–2026 = 0,49%" | (a) | 0 |

**Tổng hợp chiều tâm:** 36.000 (rev 3) → **35.600**. Phần tăng do r3-2: bear 21.200 → 23.000, đóng góp +450 vào tâm có trọng số. Phần giảm do r3-3 và r3-4: base 38.400 → 37.400, bull 45.900 → 44.700, đóng góp −800. Không bước nào dùng giá thị trường.
**Flip-flop:** 38.800 → 44.900 → 36.000 → **35.600**. Biên dao động rev 3 → rev 4 là ±1%.

## 2. Chất lượng lợi nhuận (9T/2026, hợp nhất, tỷ đồng) — giữ rev 3

NII 57.179 (+34,5%) · PPOP 49.620 (lõi bỏ một lần 3.171: +30,9%) · dự phòng 9.180 (×3,9) · LNST mẹ 33.032, **lõi 29.861 (+12,5%)**.
Một lần 3.171: lãi đánh giá lại khi Bonday-Bến Thành thành công ty con (không chịu thuế).

## 3. Spread biên PPOP − chi phí tín dụng, từng cửa sổ đo được (dư nợ BQ)

| Cửa sổ | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 9T/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Biên PPOP | 3,49 | 4,37 | 4,38 | 4,20 | 4,35 | 4,45 | 3,79 | 3,35 | 3,02 | 3,55 |
| CC | 1,23 | 1,26 | 0,99 | 1,27 | 1,31 | 0,90 | 0,38 | 0,24 | 0,20 | 0,70 |
| **Spread %** | **2,26** | 3,11 | 3,38 | 2,93 | 3,04 | 3,55 | 3,42 | 3,11 | **2,82** | **2,85** |

Nguồn: [KT2017/2019/2021/2023/2025] B02/B03, [Q3]. Hai cửa sổ gần nhất là 2,82% (kiểm toán) và 2,85%. Chuỗi 2022–25 giảm đơn điệu.

## 4. Chất lượng tài sản, ngoại bảng, vốn — giữ rev 3

NPL 0,71% (31/12/25: 0,58%) · nhóm 2: 0,28% · bao phủ 243% · không xoá nợ mới 9T · bảo lãnh 138.449,7 (×2,37 từ 31/12/2024) · dư nợ Xây dựng +71,6% năm 2025 · CASA **31,8%** [Q3] · CAR 11,14% [Báo] · CET1/LDR **không kiểm chứng được**.
⚠️ WARNING (không nhân vào base ngoài CC 9T/26): nhóm 2 +85% YTD; nhóm 3–4 1.063 → 4.229.
Cổ đông: Nhà nước 74,80%, Mizuho 15,00%; 8.355.675.094 cp [Q3 TM1]. Chờ: thưởng ≈12,8%; 16.571 tỷ LN 2025 (hình thức chưa công bố); riêng lẻ ≤6,5%.

## 5. Định giá — P/B = (ROE − g)/(Ke − g), mù giá thị trường

V6 (V_ngắn/V_dài) không áp cho ngân hàng. **V1 — r:** 13,5%, lãi huy động 12T hiệu dụng 7,40% (đo 17/11, không đo lại) ⇒ Δ=0. g = 7% (ước lượng).
ROE = spread × đòn bẩy cuối kỳ 7,24 × (1 − 20%) × (1 − KTPL 8,46%); BVPS 30.024.

| Kịch bản | P | Cửa sổ | Spread | ROE | P/B | Giá trị/cp |
|---|---|---|---|---|---|---|
| Xấu — năm kiểm toán tệ nhất | 0,25 | 2017 | 2,26% | 12,0% | 0,77 | **23.000** |
| **Cơ sở** | 0,50 | 9T/2026 | 2,85% | **15,1%** | 1,246 | **37.400** |
| Tốt | 0,25 | 2022–2026 | 3,15% | 16,7% | 1,49 | **44.700** |
| **Có trọng số** | | | | | | **35.600** |

**Cửa sổ cơ sở thay thế (hiển thị, KHÔNG vào base):**

| Cơ sở thay bằng | Spread | Base | Có trọng số |
|---|---|---|---|
| FY2025 kiểm toán | 2,82% | 36.700 | 35.300 |
| Chu kỳ 2017–21 | 2,94% | 39.800 | 36.800 |
| Chu kỳ 2017–25 | 3,07% | 42.800 | 38.300 |
| Trung vị năm 2017–25 | 3,11% | 43.700 | 38.800 |
| Bình quân đều 10 cửa sổ (giá trị) | — | 42.300 | — |

Vì sao không chọn chu kỳ: cửa sổ 2018–22 có biên 4,2–4,45% trước đợt giảm lãi định hướng. Bốn năm kiểm toán liên tiếp sau đó cho spread giảm đơn điệu, và hai cửa sổ độc lập gần nhất khớp nhau ở 2,82–2,85%. Đây là phán đoán có bằng chứng, không phải đo lường thuần. Nếu biên quay về mức chu kỳ, kịch bản tốt (3,15%) đã phủ.

Có trọng số ở Ke ±100bp: **42.100 / 30.900** ⇒ vùng hợp lý. D4 Ke 12,3% / 13,4% ⇒ base 45.900 / 38.000. g 6% / 8% ⇒ 36.400 / 38.700.

**Độ nhạy theo lãi huy động (V1), base:**

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β = 1 | 44.200 | 40.500 | 37.400 | 34.700 | 32.400 |
| β = 0,5 | 40.500 | 38.900 | 37.400 | 36.000 | 34.700 |

**Độ nhạy KHÔNG vào base:** CAR 12% bằng giảm đòn bẩy ⇒ 32.400 (−13%). VCBNeo tổn thất 5/10/20 nghìn tỷ (ước lượng minh hoạ) ⇒ 36.700 / 35.900 / 34.400. Nếu 16.571 tỷ trả tiền: −1.983 đ/cp, có trọng số sau GDKHQ 33.300.

**Vùng đọc:** rẻ ≤ **30.300** (0,85 × tâm) · hợp lý **30.900–42.100** · trên 42.100 = đắt theo r 13,5%.
**Quy tắc chia lại vùng khi pha loãng:** vùng/cp × N_cũ/N_mới sau GDKHQ (chỉ thưởng 12,8% ⇒ 27.400–37.300, tâm 31.600).
**V4:** VIFC, riêng lẻ, VCBNeo ⇒ NPV = 0 ở giá sổ sách. Không có capex tuân thủ đáng kể ngoài opex (đã trong PPOP).

## 6. Moat (V5) — tái dùng 5F 17/11 (<12 tháng)

**NARROW**: chi phí vốn (CASA 31,8% [Q3]) + chất lượng tài sản (NPL 0,71%). Rủi ro số 1 là nghĩa vụ chính sách. ROE base 15,1% > Ke 13,5% chỉ ~1,6pp. Không thưởng, không trừ.

## 7. Sau khoá — V3 thanh khoản, so giá, sizing

- **V3:** ADV trung vị 3 năm 175 tỷ/phiên (rev 1; không truy vấn lại). Vị thế 2–4% NAV thoát trong ≤2 phiên ⇒ **chiết khấu 0%**. Trước = sau = 35.600.
- **So giá:** Giá 52.100 (17/11/2026) = P/B 1,74 trên BVPS 30.024; **+46%** so tâm, +39% so base; TRÊN đầu vùng 42.100. Giá hàm ý ROE thuộc cổ đông ≈ 18,3% ở Ke 13,5%. Mức này cao hơn mọi cửa sổ đo được (cửa sổ tốt nhất 2022 spread 3,55% ⇒ ROE ~18,8% chỉ đạt khi giữ biên đỉnh 2022 vĩnh viễn).
- **Nhãn:** đắt theo r 13,5%. **V8:** khung 2–4% NAV; ở giá hiện tại **không đề xuất mở vị thế**. Chỉ xét đầu dưới 2% khi giá ≤ 30.300.

## 8. Pháp lý / quản trị — chỉ WARNING

KTNN điều chỉnh hồi tố nhỏ (+29 tỷ VCSH). EY 2025 chấp nhận toàn phần. Thanh tra NHNN chỉ ở cấp chi nhánh, không thấy vụ án. Nghĩa vụ chính sách: VCBNeo, chỉ đạo giảm lãi.

## 9. Điều kiện đổi nhận định

**Tâm ↑:** BCTC Q4/2026 cho spread cả năm ≥ 3,1% (cơ sở chuyển về chu kỳ ⇒ ~38.300); lãi huy động −50bp (+8%); 16.571 tỷ chia cổ phiếu; VCBNeo công bố lãi kiểm toán, không cần hỗ trợ.
**Tâm ↓:** spread Q4 ≤ 2,6%; NPL > 1,0%; CAR/CET1 < 11% buộc giảm đòn bẩy (−13%); hỗ trợ VCBNeo > 5 nghìn tỷ; lãi huy động +50bp (−7%); 16.571 tỷ trả tiền (−1.983 đ/cp).

## 10. Không kiểm chứng được / còn thiếu

- VCBNeo: vốn, lỗ luỹ kế, cam kết hỗ trợ, thời hạn miễn trừ hợp nhất. Ảnh hưởng ước lượng −2% … −8% base.
- CET1, LDR TT22, Pillar 3. Ảnh hưởng: nếu CAR thực buộc về 12% thì −13%.
- Nguyên nhân NII 2026 tăng. Ảnh hưởng tới base được chặn bởi cửa sổ FY2025 (−1,9%).
- Thành phần VAMC trong dự phòng 2017–19. Có thể làm kịch bản xấu (2017) bi quan hơn thực; ảnh hưởng tâm ≤ +1% (ước lượng).
- KTPL 2026 thực trích (ước lượng 334 đ/cp theo tỷ lệ 2025).

## Nguồn
- BCTC hợp nhất kiểm toán VCB 2017–2025: `https://static2.vietstock.vn/data/HOSE/<năm>/BCTC/VN/NAM/VCB_Baocaotaichinh_<năm>_Kiemtoan_Hopnhat.pdf`; Q3/2026: `src/VCB_BCTC_Q3_2026_HN.pdf`
- VCBNeo (báo, không số kiểm toán): https://doanhnhan.baophapluat.vn/hoi-sinh-sau-chuyen-giao-bat-buoc-vcbneo-bao-lai-gan-2-000-ty-dong-nhom-ngan-hang-yeu-kem-dong-loat-thoat-lo.html · https://vnba.org.vn/vi/vcbneo-tong-ket-hoat-dong-nam-2025--trien-khai-nhiem-vu-nam-2026-20651.htm
- CAR 30/06/2026 [Báo]: https://acbs.com.vn/acbsmedia/2026/08/VCB_cap-nhat_ACBS_07.08.2026-VN.pdf
- Cổ tức/ĐHĐCĐ: xem `REPORT_rev3.md` mục Nguồn.
