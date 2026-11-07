# DCM — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07/11/2026 · job `Taylor_20261107_120603` · **r2** `Taylor_20261107_122448` (sửa theo fundamental-skeptic cụm 1; bản cũ = `ADDENDUM_5F_r1.md`)

> Bổ sung cho `REPORT_r5.md` (05/11). Mọi phần khác của r5 **giữ nguyên**. Nội bộ, read-only, không phải khuyến nghị.
> **Làm mới, không tái dùng:** `data/moat_tags.csv` không có dòng DCM; `kb/projects/dcm-dd-20261104.md` và REPORT r1–r5 không có mục 5F/moat ⇒ chưa có audit nào trong 12 tháng ⇒ làm đầy đủ theo `5F.md`.
> Định giá vẫn mù giá: `calc/moat_sens_5f.py` không nhận giá/vốn hoá/PE. 5F dựa một phần vào kiến thức LLM (non-PIT) ⇒ chỉ dùng cho DD sống, **không đưa vào backtest**.
> Nguồn số: [BQ] `tav2_bq.ticker_financial` dòng Q4 các năm (chạy 07/11); GPM = **TB 4 quý** (`calc/gpm_4q_5f.sql` → `gpm_4q_5f_out.csv`, `gpm_4q_5f_cmp.txt`), KHÔNG phải GPM_P0 quý Q4; [Bobby] `kb/data_registry/market-state/sector_read_phan_dam_ure_20261104.md` §4; [PL12]/[BB25] như r5; [M] `calc/moat_sens_5f_out.txt`.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Loại hình:** hàng hoá chu kỳ (urê, giá theo quốc tế, đầu vào khí gắn dầu theo hợp đồng). Ngành **mean-revert** theo biên urê–khí, không theo trend. Lợi thế của DN (nếu có) chỉ có thể là **vị thế chi phí/vị trí**, không phải thương hiệu.

**Bằng chứng lợi nhuận nhiều chu kỳ [BQ], Ke = r = 13,5% (r5):**

| | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| ROE DCM | 10,5% | 10,5% | 10,4% | 7,0% | 10,5% | 26,8% | 44,1% | 10,6% | 14,3% | 18,7% |
| ROE DPM (peer khí) | 13,1% | 8,5% | 8,7% | 4,8% | 8,5% | 32,6% | 42,8% | 4,4% | 4,7% | 9,5% |
| GPM DCM (TB4Q) | 25,0% | 24,1% | 21,1% | 15,5% | 15,3% | 20,8% | 35,1% | 21,5% | 18,4% | 21,3% |
| GPM DPM (TB4Q) | 29,8% | 26,6% | 22,1% | 18,4% | 21,7% | 28,3% | 41,6% | 23,8% | 13,4% | 15,6% |
| GPM DCM−DPM (pp) | −4,8 | −2,5 | −1,0 | −2,9 | −6,4 | −7,5 | −6,5 | −2,3 | +5,0 | +5,7 |
| GPM DHB (TB4Q, than) | n/a | 8,5% | 18,2% | 16,7% | −3,5% | 8,6% | 40,9% | 14,3% | 1,9% | 11,1% |

- TB ROE DCM 2016–20 = **9,8% < Ke**; 2021–25 = 22,9% (kéo bởi đỉnh 2022). `ROE_Min5Y` 2025 = **10,8%**, `ROIC_Min5Y` = **6,3%**, `ROIC5Y` = 17,0% (gồm 2022); `ROIC10Y` = **11,6% (<Ke)**, `ROIC_Min10Y` = 2,0%; `ROE10Y` = 16,2% (>Ke nhưng bị đỉnh 2022 kéo; **trung vị ROE Q4 2016–25 = 10,55% <Ke**). ROE và ROIC ghi riêng, không thay nhau. ⇒ lợi nhuận siêu ngạch **không liên tục qua chu kỳ** (điều kiện (i) **không đạt**).
- **So peer DPM (khí, nội địa, đúng đối thủ phía Nam):** GPM TB4Q DCM **thấp hơn DPM 5/5 năm 2016–20 và 8/10 năm 2016–25**; chênh 2023–25 = −2,3/+5,0/+5,7pp ⇒ **không có bằng chứng lợi thế biên gộp bền**; hai năm gần nhất DCM trội nhưng DPM đang xấu (13,4%/15,6%). Lợi thế duy nhất thấy được là **ROE**: cao hơn DPM 4/5 năm 2016–20 và 8/10 năm 2016–25 (có thể do cơ cấu vốn/đã khấu hao, cần kiểm chứng).
- **Peer than DHB (phía Bắc, bằng chứng thật cho NARROW):** `ROIC_Min5Y` 2025 = **−7,6%**, `ROIC_Min10Y` = −9,8%, ROE âm, GPM 2024 = 1,9% ⇒ nhà máy than kém chi phí rõ rệt; vị thế chi phí tương đối của khí đường ống có thật, nhưng DPM (cùng khí) lại cho thấy DCM không vượt trội về biên.
- ROIC hoạt động sổ sách ở biên 179 = **22,1%** [M] (VCSH 11.883 − net cash 7.539 = vốn HĐ 4.344 tỷ) — cao chủ yếu vì nhà máy (vận hành 2012) đã khấu hao gần hết (r5 base), **không phải bằng chứng rào cản**; so với chi phí thay thế: cần kiểm chứng.

| Lực | Mức | Cơ chế + bằng chứng |
|---|---|---|
| 1. Gia nhập mới | 🟢 Thấp | Không có dự án urê mới ở VN; dư cung 0,6–1,0 tr t/năm làm đầu tư mới vô lý [Bobby §4]. Rào cản = vốn + nguồn khí, không phải giấy phép riêng của DCM |
| 2. Nhà cung cấp (khí) | 🔴 Cao | Một nhà cung cấp nhà nước (PVN/PV GAS), giá do hợp đồng: Petronas hết cuối 2027 [BB25 p8]; Nam Du 10,39×1,0225^t cố định [PL12 p31]; hết khối lượng cam kết 25/4/2032 [PL12 Đ4.1(b)]; hoá đơn USD [Đ10.2(a)]. Thượng nguồn: PSC/UGSA PM3-CAA **gia hạn tới 31/12/2047** (`REPORT_r5.md:127`, nguồn `src/dl_1844450.txt:435`) ⇒ nguồn khí **không bị cắt**; đồng hồ là rủi ro **giá/khối lượng không công bố**. DCM **không tự chủ đầu vào** |
| 3. Người mua | 🟡 TB | Phân tán (đại lý/nông dân), sản phẩm chuẩn hoá, giá nội địa "dính" nhưng neo quốc tế; 9T/26 XK 413 kt = 56% tiêu thụ urê (r2 §3 mục 2) ⇒ bán theo giá thế giới |
| 4. Thay thế | 🟢 Thấp–TB | Urê là nguồn N chính; thay thế bằng NPK/SA chỉ một phần — cần kiểm chứng tỷ trọng |
| 5. Nội bộ ngành | 🔴 Cao | 4 nhà máy (2 khí phía Nam ~0,8 tr t mỗi nhà máy, 2 than phía Bắc ~1,0–1,1 tr t) + urê NK giá thấp TQ/Indonesia [Bobby §4]; cạnh tranh giá, ngành dư cung |
| **6. Đồng hồ / chính sách** | 🔴 Cao | (a) đường khí: PM3 suy giảm (PSC tới 2047 nên là rủi ro giá/khối lượng, không phải mất nguồn), Petronas hết 2027, khối lượng cam kết hết 2032 ⇒ lợi thế khí rẻ có **hạn** (r5 S4: 2035+ −7.607); (b) ADMIN: thuế XK 5%/0%, VAT, hạn ngạch TQ dịch biên ±50–100 USD/t [Bobby]; (c) ưu đãi TNDN 10% hết 2026 (r2 §3 mục 7) |

**Kết luận:** ngành kém hấp dẫn về cấu trúc (dư cung, giá ngoại sinh, đầu vào độc quyền nhà nước). DCM có lợi thế chi phí **tương đối so than** (DHB ROIC_Min5Y −7,6%), nhưng **không trội so DPM cùng khí** về GPM (thấp hơn 8/10 năm); phần vị trí ĐBSCL: cần kiểm chứng logistics/thị phần.
- **moat_tier = NARROW · moat_type = COST/LOCATION.**
- **Bền? KHÔNG** — trượt (i) (ROE TB 2016–20 < Ke; ROE_Min5Y < Ke; ROIC10Y 11,6% < Ke; ROIC_Min5Y 6,3%) và (iii) (đồng hồ khí 2027/2032). (ii) chỉ đạt một phần (gọi tên được: khí đường ống, nhưng do nhà cung cấp nắm).
- **Rủi ro số 1:** giá/khối lượng khí (nguồn tới 2047 nhưng giá/khối lượng bổ sung không công bố) sau 2027 và sau 2032 (PM3 bổ sung V1/V2, Nam Du, LNG) — nhà cung cấp nhà nước quyết định biên, không phải DCM.

## 2. Moat trong mô hình
**Không thưởng; mô hình hiện hành đã ở mặc định NARROW/NONE-không-premium, nhất quán.** Rà soát `calc/model.py` + `model_r5.py`:
- Terminal = vĩnh viễn từ năm 2, **g = 0, RONIC = r** (`model.py` dòng `value()`), không có fade kéo dài siêu ngạch, không có bội số.
- Biên dài hạn = **TB chu kỳ 2016–25 = 179** (proxy chi phí khí chung của ngành, không phải chi phí riêng DCM) — đúng luật "biên về TB chu kỳ ngành". Lớp khí riêng DCM (r5) chỉ cộng/trừ Δ theo hợp đồng 2026–34; 2035+ Δ ≈ +0,3 USD/t ⇒ về proxy chung, **không ngầm giữ lợi thế khí rẻ vĩnh viễn**.
- Không đếm hai lần: không có premium nào để cắt. Một điểm cần nói rõ: biên 179 giữ vĩnh viễn ⇒ ROIC HĐ sổ sách 22% vĩnh viễn trên vốn đã khấu hao; điều này phản ánh **tài sản đã khấu hao** chứ không phải moat, và capex thay thế nhà máy (khi hết vòng đời) chưa mô hình hoá (chiều hạ, chưa định lượng).
- Đồng hồ cắt hào (6a) **đã có** trong r5 dưới dạng độ nhạy S4 (không vào base) — giữ nguyên quyết định của r5; Mike quyết có đưa vào trọng số hay không.

## 3. Độ nhạy theo moat (đ/cp, Brent 67,8, tâm; [M], tuyến tính theo bảng r5 §4, k = 73,56 đ/cp mỗi USD/t)

| Kịch bản moat | Giả định | Giá trị | Δ vs tâm r5 24.326 |
|---|---|---|---|
| WIDE (giả định, **bị bác**) | biên bền 220 | 27.330 | +3.004 (+12,3%) |
| WIDE mạnh (bị bác) | biên = TB 2021–25 = 277 | 31.534 | +7.208 (+29,6%) |
| **NARROW (= base r5)** | biên TB chu kỳ 179, RONIC = r | 24.314 | −12 |
| Stress cận dưới, fade từ 2035 | biên 179 tới 2034, rồi biên làm ROIC HĐ sổ sách = Ke (132) | 22.886 | −1.428 (−5,9%) |
| Stress cận dưới, fade ngay | biên 132 từ năm 2 | 20.850 | −3.476 (−14,3%) |
| Đối chiếu: đồng hồ khí (r5 S4) | khí 10,39 phẳng từ 2035 | 16.719 | −7.607 |

- Hai dòng "stress cận dưới" (trước gọi NONE) là **cận dưới cơ học**: ROIC sổ sách trên nhà máy đã khấu hao ≠ moat, nên không đọc như kịch bản NONE thật. Hàm `deferred` r1 chiết khấu ^−(t−1) lệch một năm so quy ước năm 1 = Q4/26–Q3/27; r2 dùng ^−(t−2) (perpetuity bắt đầu năm t so với perpetuity từ năm 2) ⇒ 23.056 → **22.886**.
- Nhãn @33.000 (chỉ so điểm, chưa chạy lại lưới P10–P90): mọi kịch bản vẫn **trên vùng giá trị**; kể cả WIDE mạnh 31.534 vẫn thấp hơn giá 4,4%. Moat sai một bậc (NARROW→WIDE 220) dịch tâm +12%; nhãn không đảo.

## 4. Thay đổi so với báo cáo hiện hành
**Mô hình không đổi, giá trị không đổi, nhãn không đổi.** Tâm 24.326, dải A/B [24.192; 24.459], P10/P50/P90 các lưới, nhãn "giá trên vùng giá trị" — giữ nguyên `REPORT_r5.md`. Bổ sung duy nhất: mục 5F + bảng độ nhạy moat ở trên. Không ghi `dd_price_zones`, không sửa REPORT/SUMMARY cũ.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi — Mike/user duyệt)
```
DCM,NARROW,COST/LOCATION,L,"Cost edge = pipeline PM3 gas vs coal-based northern peers, but gas is set by state supplier PVN/PV GAS (Petronas ends 2027, committed volume ends 2032-04-25, Nam Du 10.39 USD/MMBtu +2.25%/y fixed); not through-cycle: ROE avg 2016-20 9.8% < Ke 13.5%, ROE_Min5Y 10.8%, ROIC_Min5Y 6.3%, ROIC10Y 11.6% < Ke, ROE10Y 16.2% (2022 peak; median 10.55%); GPM TB4Q below DPM 8/10y; coal peer DHB ROIC_Min5Y -7.6%; PSC to 2047; sector oversupplied 0.6-1.0 Mt/y",2026-11-07,5f_taylor_dd_addendum,N
```
(cột `entry` = **L**: độ hấp dẫn cấu trúc NGÀNH, urê dư cung/giá ngoại sinh/đầu vào độc quyền — không theo tier; moat_upgrade=N.)

*Phân tích, không phải khuyến nghị; số liệu nên kiểm chứng lại bằng BCTC/BCTN/NQ ĐHĐCĐ mới nhất.*
