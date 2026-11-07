# DCM — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07/11/2026 · job `Taylor_20261107_120603`

> Bổ sung cho `REPORT_r5.md` (05/11). Mọi phần khác của r5 **giữ nguyên**. Nội bộ, read-only, không phải khuyến nghị.
> **Làm mới, không tái dùng:** `data/moat_tags.csv` không có dòng DCM; `kb/projects/dcm-dd-20261104.md` và REPORT r1–r5 không có mục 5F/moat ⇒ chưa có audit nào trong 12 tháng ⇒ làm đầy đủ theo `5F.md`.
> Định giá vẫn mù giá: `calc/moat_sens_5f.py` không nhận giá/vốn hoá/PE. 5F dựa một phần vào kiến thức LLM (non-PIT) ⇒ chỉ dùng cho DD sống, **không đưa vào backtest**.
> Nguồn số: [BQ] `tav2_bq.ticker_financial` dòng Q4 các năm (chạy 07/11); [Bobby] `kb/data_registry/market-state/sector_read_phan_dam_ure_20261104.md` §4; [PL12]/[BB25] như r5; [M] `calc/moat_sens_5f_out.txt`.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Loại hình:** hàng hoá chu kỳ (urê, giá theo quốc tế, đầu vào khí gắn dầu theo hợp đồng). Ngành **mean-revert** theo biên urê–khí, không theo trend. Lợi thế của DN (nếu có) chỉ có thể là **vị thế chi phí/vị trí**, không phải thương hiệu.

**Bằng chứng lợi nhuận nhiều chu kỳ [BQ], Ke = r = 13,5% (r5):**

| | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| ROE DCM | 10,5% | 10,5% | 10,4% | 7,0% | 10,5% | 26,8% | 44,1% | 10,6% | 14,3% | 18,7% |
| ROE DPM (peer khí) | 13,1% | 8,5% | 8,7% | 4,8% | 8,5% | 32,6% | 42,8% | 4,4% | 4,7% | 9,5% |
| GPM DCM | 32,2% | 9,3% | 21,5% | 13,6% | 17,4% | 21,9% | 35,8% | 16,2% | 18,7% | 24,3% |
| GPM DPM | 22,5% | 28,3% | 20,4% | 18,2% | 22,3% | 29,1% | 42,1% | 12,2% | 14,1% | 17,7% |

- TB ROE DCM 2016–20 = **9,8% < Ke**; 2021–25 = 22,9% (kéo bởi đỉnh 2022). `ROE_Min5Y` 2025 = **10,8%**, `ROIC_Min5Y` = **6,3%**, `ROIC5Y` = 17,0% (gồm 2022). ⇒ lợi nhuận siêu ngạch **không liên tục qua chu kỳ** (điều kiện (i) **không đạt**).
- So peer: 2023–25 DCM vượt DPM rõ (ROE +6,2/+9,6/+9,2pp; GPM +4,0/+4,6/+6,6pp) — có dấu hiệu lợi thế chi phí gần đây; 2016–20 thì không (GPM thấp hơn DPM 3/5 năm, ROE thấp hơn 2016).
- ROIC hoạt động sổ sách ở biên 179 = **22,1%** [M] (VCSH 11.883 − net cash 7.539 = vốn HĐ 4.344 tỷ) — cao chủ yếu vì nhà máy (vận hành 2012) đã khấu hao gần hết (r5 base), **không phải bằng chứng rào cản**; so với chi phí thay thế: cần kiểm chứng.

| Lực | Mức | Cơ chế + bằng chứng |
|---|---|---|
| 1. Gia nhập mới | 🟢 Thấp | Không có dự án urê mới ở VN; dư cung 0,6–1,0 tr t/năm làm đầu tư mới vô lý [Bobby §4]. Rào cản = vốn + nguồn khí, không phải giấy phép riêng của DCM |
| 2. Nhà cung cấp (khí) | 🔴 Cao | Một nhà cung cấp nhà nước (PVN/PV GAS), giá do hợp đồng: Petronas hết cuối 2027 [BB25 p8]; Nam Du 10,39×1,0225^t cố định [PL12 p31]; hết khối lượng cam kết 25/4/2032 [PL12 Đ4.1(b)]; hoá đơn USD [Đ10.2(a)]. DCM **không tự chủ đầu vào** |
| 3. Người mua | 🟡 TB | Phân tán (đại lý/nông dân), sản phẩm chuẩn hoá, giá nội địa "dính" nhưng neo quốc tế; 9T/26 XK 413 kt = 56% tiêu thụ urê (r2 §3 mục 2) ⇒ bán theo giá thế giới |
| 4. Thay thế | 🟢 Thấp–TB | Urê là nguồn N chính; thay thế bằng NPK/SA chỉ một phần — cần kiểm chứng tỷ trọng |
| 5. Nội bộ ngành | 🔴 Cao | 4 nhà máy (2 khí phía Nam ~0,8 tr t mỗi nhà máy, 2 than phía Bắc ~1,0–1,1 tr t) + urê NK giá thấp TQ/Indonesia [Bobby §4]; cạnh tranh giá, ngành dư cung |
| **6. Đồng hồ / chính sách** | 🔴 Cao | (a) đường khí: PM3 suy giảm, Petronas hết 2027, khối lượng cam kết hết 2032 ⇒ lợi thế khí rẻ có **hạn** (r5 S4: 2035+ −7.607); (b) ADMIN: thuế XK 5%/0%, VAT, hạn ngạch TQ dịch biên ±50–100 USD/t [Bobby]; (c) ưu đãi TNDN 10% hết 2026 (r2 §3 mục 7) |

**Kết luận:** ngành kém hấp dẫn về cấu trúc (dư cung, giá ngoại sinh, đầu vào độc quyền nhà nước). DCM có lợi thế chi phí **tương đối** (khí đường ống vs nhà máy than, vị trí ĐBSCL gần vùng tiêu thụ — phần vị trí: cần kiểm chứng logistics/thị phần).
- **moat_tier = NARROW · moat_type = COST/LOCATION.**
- **Bền? KHÔNG** — trượt (i) (ROE TB 2016–20 < Ke; Min5Y < Ke) và (iii) (đồng hồ khí 2027/2032). (ii) chỉ đạt một phần (gọi tên được: khí đường ống, nhưng do nhà cung cấp nắm).
- **Rủi ro số 1:** giá/khối lượng khí sau 2027 và sau 2032 (PM3 bổ sung V1/V2, Nam Du, LNG) — nhà cung cấp nhà nước quyết định biên, không phải DCM.

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
| NONE, fade từ 2035 | biên 179 tới 2034, rồi biên làm ROIC HĐ = Ke (132) | 23.056 | −1.270 (−5,2%) |
| NONE, fade ngay | biên 132 từ năm 2 | 20.850 | −3.476 (−14,3%) |
| Đối chiếu: đồng hồ khí (r5 S4) | khí 10,39 phẳng từ 2035 | 16.719 | −7.607 |

- Nhãn @33.000 (chỉ so điểm, chưa chạy lại lưới P10–P90): mọi kịch bản vẫn **trên vùng giá trị**; kể cả WIDE mạnh 31.534 vẫn thấp hơn giá 4,6%. Moat sai một bậc (NARROW→WIDE 220) dịch tâm +12%; nhãn không đảo.

## 4. Thay đổi so với báo cáo hiện hành
**Mô hình không đổi, giá trị không đổi, nhãn không đổi.** Tâm 24.326, dải A/B [24.192; 24.459], P10/P50/P90 các lưới, nhãn "giá trên vùng giá trị" — giữ nguyên `REPORT_r5.md`. Bổ sung duy nhất: mục 5F + bảng độ nhạy moat ở trên. Không ghi `dd_price_zones`, không sửa REPORT/SUMMARY cũ.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi — Mike/user duyệt)
```
DCM,NARROW,COST/LOCATION,M,"Cost edge = pipeline PM3 gas vs coal-based northern peers, but gas is set by state supplier PVN/PV GAS (Petronas ends 2027, committed volume ends 2032-04-25, Nam Du 10.39 USD/MMBtu +2.25%/y fixed); not through-cycle: ROE avg 2016-20 9.8% < Ke 13.5%, ROE_Min5Y 10.8%, ROIC_Min5Y 6.3%; sector oversupplied 0.6-1.0 Mt/y",2026-11-07,5f_taylor_dd_addendum,N
```
(cột `entry` = M theo quy ước các dòng NARROW hiện có — Mike chỉnh nếu khác.)

*Phân tích, không phải khuyến nghị; số liệu nên kiểm chứng lại bằng BCTC/BCTN/NQ ĐHĐCĐ mới nhất.*
