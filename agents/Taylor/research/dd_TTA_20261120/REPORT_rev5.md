# DD — TTA rev 5 · 2026-11-23 · job `Taylor_20261123_120303` (vòng cuối, sau skeptic DD_GENERAL r2 = INCONCLUSIVE)

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. Không đặt lệnh, không email, **không ghi `kb/dd_price_zones.json`** (đề xuất sổ: `LEDGER_PROPOSAL_TTA.json`).
> Bản cũ giữ nguyên: REPORT.md / REPORT_r2.md / REPORT_r3.md / REPORT_r4.md. Mô hình rev 5: `model/dcf_tta_r5.py` → `model/out_r5.json`; mọi số dưới đây đọc từ file này trừ khi ghi nguồn khác.
> Khoá giả định: `assumptions_TTA_r5.json` (`bin/dd_assumptions_lint.py`: 1 cảnh báo L14 — quan sát lãi huy động 02/11 cách 21 ngày; `deposit_rate_vn.consumer_deposit_rate_detail()` chạy lại 23/11 vẫn 7,40%, last_update 16/11, chưa có quan sát mới hơn).
> Mù giá: L1–L3 lấy từ quyết định giá điện và BCTC kiểm toán. KHÔNG truy vấn giá TTA mới trong phiên này. Giá 10.250 đ (đóng cửa 19/11/2026, có sẵn từ r3) chỉ dùng ở §7 (pha sau khoá).

## 0. Kết luận rev 5

| Mục (V1 bù trừ ngay, trọng số A/B/B′/C = 0,15/0,25/0,35/0,25 — giữ nguyên r2–r4, không re-tune) | đ/cp |
|---|---|
| A / B / B′ / C (trước TK) | 15.170 / 10.975 / 7.026 / 1.174 |
| **Tâm có trọng số TRƯỚC chiết khấu thanh khoản** | **7.772** (r4: 8.802, −11,7%) |
| Chiết khấu thanh khoản d(5 tỷ) (giữ phương pháp r3/r4) | 2,89% (ADV 250 phiên); 3,87% (ADV 68 phiên) |
| **Tâm SAU thanh khoản (expected_weighted)** | **7.547** (ADV 68 phiên: 7.472) |
| Vùng cùng nền sau TK: dưới ≤ 0,85× · hợp lý · trên > 1,15× | **≤ 6.415 · 6.415 – 8.680 · > 8.680** |
| Giá 19/11 10.250 / tâm | **1,36× sau TK** · 1,32× trước TK ⇒ **TRÊN vùng hợp lý** |

Hướng giữ nguyên (TRÊN vùng hợp lý). Tâm GIẢM 11,7% vì hai đính chính có cơ sở độc lập:
- **L1 + L2:** biểu giá chi phí tránh được phẳng danh nghĩa trong cả 7 quyết định năm 2020→2026.
- **L3:** chuỗi doanh thu bộ phận Yên Bái được đo thẳng từ BCTC kiểm toán.

Kết luận nay **bền với mọi ô lưới trọng số**: 0/30 ô vượt giá, ô cao nhất 9.902 < 10.250 (§3).

**Phân rã r4 → rev 5 (tâm trước TK, đ/cp; `out_r5.json` `sens_center_pre`):**
| Bước | Tâm |
|---|---|
| r4 (tái lập bằng r5: hyd_g 1% + PF_G 1% + nền 373) | 8.802 |
| + L1/L2: chỉ số thuỷ điện và giá sau FIT về 0% (nền giữ 373) | 7.865 (−937; riêng phần giá sau FIT ≈ −92, so `PF_G=0.01` 7.864 với 7.772) |
| + L3: nền thuỷ điện 373 → 369,9 (bộ phận đo) | **7.772** (−93) |

## 1. Đính chính so với rev trước — từng hạng mục skeptic r2 (`skeptic/r2.json`, md5 báo cáo r4 `43300d8c…`)

| # | Hạng mục skeptic r2 | Bằng chứng độc lập tìm được | Xử lý | Ảnh hưởng tâm trước TK |
|---|---|---|---|---|
| 1 | **(killer)** Chỉ số 1%/năm cho thuỷ điện đo từ 2019; 2021→2026 gần như đứng yên | Tra đủ biểu giá chi phí tránh được (BGCPTĐ) TỪNG NĂM, miền Bắc, điện năng mùa khô cao/bình thường/thấp điểm · mùa mưa:<br>• QĐ 4036/QĐ-BCT 31/12/2019 (năm 2020): 726/726/725 · 703/704/702<br>• QĐ 650/QĐ-BCT 2021: như trên<br>• QĐ 131/QĐ-BCT 28/01/2022: như trên<br>• QĐ 1028/QĐ-BCT 27/04/2023: như trên<br>• QĐ 1670/QĐ-BCT 25/06/2024: như trên<br>• QĐ 3734/QĐ-BCT 31/12/2024 (năm 2025): như trên<br>• QĐ 392/QĐ-BCT 06/03/2026: như trên<br>Công suất tránh được 1.932 không đổi cả chuỗi. ⇒ phẳng danh nghĩa 6 năm liền (2021→2026, đã xác nhận). Năm 2020 trùng số, nhưng chưa đối chiếu bản gốc. Mức 1% của r4 chỉ đến từ bước 2019 (QĐ 226/2019, 663–671) → 2020, cũng là lúc đổi cấu trúc biểu giá theo TT 29/2019 | **(a) base**: HYD_G = 0% (L1). Độ nhạy 1% / 2% giữ | −845 (= −937 − (−92); phần thuỷ điện) |
| 1b | Chỉ số 1% áp cho Ngòi Hút 2 (48 MW, ~59% công suất) không có bằng chứng | TT 16/2025/TT-BCT Đ4 k1 điểm a (TT 36/2025 đổi thành "công suất đặt"): nhà máy > 30 MW thuộc diện tham gia trực tiếp thị trường điện, trừ ngoại lệ khoản 3. **Không** tìm được xác nhận NH2 đã đăng ký thị trường, cũng không có PPA/điều khoản giá trong BCTC/CBTT | **(c) không kiểm chứng được** cơ chế giá NH2. Nhờ L1, base đã PHẲNG danh nghĩa cho toàn bộ thuỷ điện, kể cả NH2, nên không còn giả định chỉ số hoá nào thiếu bằng chứng. Mức doanh thu NH2 đã nằm trong nền đo của bộ phận Yên Bái (#3). Rủi ro còn lại là biến động giá thị trường điện quanh mức nền: hai chiều, không định lượng được | 0 (gộp trong #1) |
| 1c | Giá sau FIT 1.100 đ cũng chỉ số hoá 1% (cùng cơ sở) | Cơ sở duy nhất của 1% là chuỗi BGCPTĐ ở #1 | **(a) base**: PF_G = 0% (L2); độ nhạy 1% ⇒ 7.864 | −92 |
| 2 | Thuỷ điện 2021–23 dùng TỔNG doanh thu BQ, không phải doanh thu mảng điện/bộ phận (2024: 734,1 vs 720,4) | Thuyết minh bộ phận "Khu vực Yên Bái" (thuỷ điện), BCTC kiểm toán tổng hợp, tỷ đồng:<br>• 2021: **344,46** (BCTN 2021 tr.45 phần BCTC)<br>• 2022: **474,41** (BCTN 2022 tr.45)<br>• 2023: **315,32** (BCTN 2023 tr.43)<br>• 2024: **386,19** (BCTC KT 2024 tr.43)<br>• 2025: **379,06** (KT25 tr.45)<br>Kiểm chéo: Yên Bái + Ninh Thuận = tổng DT, khớp tổng 4 quý BQ mà skeptic r2 đã kiểm (661,35 / 808,70 / 655,48 / 734,11). Tệp gốc và md5 ở cuối báo cáo | **(a) base**: nền = trung bình cắt (bỏ 474,41 cao nhất, 315,32 thấp nhất) = **369,9** (L3); trung vị 379,06, TB 5 năm 379,9 | −93 |
| 3 | Cam kết vốn chủ cho Phước Hoà (1.200 MW) chưa công bố | Nguồn báo (nhadautu.vn, không phải văn bản gốc): tổng mức đầu tư dự án **22.865 tỷ**; chủ đầu tư là liên danh do Trường Thành đứng đầu cùng Daewoo E&C (Hàn Quốc) và nhà đầu tư trong nước. UBND Khánh Hoà nói dự án chậm, khó kịp 2030. **Không** nêu tỷ lệ góp của TTA | **(c) không kiểm chứng được** tỷ lệ góp/cam kết. Base giữ NPV = 0 tại giá sổ 90,7 (luật V4(a), dự án tăng trưởng). Rủi ro tài trợ/pha loãng giữ ở **HARD ABANDON #7** (§8). Thang tham chiếu (ước lượng, không vào base): mỗi 10% tỷ lệ góp × 30% vốn chủ/TMĐT ≈ 686 tỷ vốn chủ ≈ 3.840 đ/cp phải huy động. Nếu phát hành dưới giá trị nội tại thì cổ đông hiện hữu bị pha loãng. Độ nhạy xoá giá sổ Phước Hoà = 0 ⇒ 7.054 sau TK | 0 (base) |
| 4 | Thời hạn HTKD + giấy phép nước/đất thuỷ điện tới 2060 | Không có trong BCTC/BCTN đã tải (2021–2025) | **(c) không kiểm chứng được**. Độ nhạy thuỷ điện dừng 2050 ⇒ 7.319 (−453) | — |
| 5 | EPTC trả 49% hoá đơn mặt trời 9T/2026 (55% cùng kỳ); mô hình coi thu đủ từ 2027 | Đo lại từ BCTC (`out_r5.json` `eptc_pay`) | **(b) độ nhạy** qua phải thu vượt: = 0 ⇒ 5.966 (cận xấu). Độ trễ thu từng năm không có cơ sở, nên không vào base | — |
| 6 | (chiều tăng) VAT trên khoản hồi tố không vào base | Không có văn bản xác nhận được giảm thuế đầu ra khi lập hoá đơn điều chỉnh | **(c) không kiểm chứng được**; độ nhạy vat = 1,0 ⇒ **8.039** (+267) | — |
| 7 | (chiều tăng) Nhịp thuỷ điện 2026 ≈ 397 > nền | 9T/2026 279,8 vs 9T/2025 262,3 (r4 §1). Năm 2026 chưa có Q4 | **(b) độ nhạy, không vào base** (một năm thuỷ văn ≠ nền): nền 397 ⇒ **8.580** | — |
| 8 | (chiều tăng) Tỷ giá 2021–2025 tăng 3,2%/năm | Giữ CAGR dài 2016→2025 1,86% (r4 K3) | **(b) độ nhạy**: FX 3,2% ⇒ **8.293**; FX 0% ⇒ 7.170 | — |
| 9 | Dòng tiền Q4/2026 bị bỏ | Lịch gốc Q4/2026 không tách được | **(b)** như r4: ±~1,4% tâm (ước lượng skeptic) | — |
| 10 | Cài poppler để đọc lại PDF | Máy vẫn thiếu `pdftoppm`. Số bộ phận 2021–2024 lấy từ ảnh trang PDF, đã kiểm chéo bằng tổng (#2) | Ghi nhận giới hạn | — |

Giữ từ r4, không đổi:
- Hai giả định ước lượng của r1, vẫn trong base: giá thuỷ điện cắt −15% sau 2036, và giá sau FIT 1.100 đ (2026).
- Độ nhạy bỏ cắt −15%: 8.198.

## 2. Đầu vào mô hình — nguồn (chỉ liệt kê tham số đổi; còn lại như r4 §2)

| Tham số | rev 5 | r4 | Nguồn |
|---|---|---|---|
| DT thuỷ điện 2026 | **369,9 tỷ, phẳng danh nghĩa** | 373, +1%/năm | Bộ phận Yên Bái 2021–2025 (BCTN 21/22/23, BCTC KT24, KT25); BGCPTĐ 2020–2026 |
| Giá sau FIT | **1.100 đ phẳng** | 1.100 +1%/năm | ước lượng r1; BGCPTĐ phẳng |
| Chi phí tiền thuỷ điện | 80 +3%/năm (giữ) | như nhau | KT25 tr.45: 175,94 − 91,97 = 83,97 (2025) |
| Tỷ giá FIT | 26.189 × 1,018^t (giữ) | như nhau | `data/macro_usdvnd.csv` |

## 3. Trọng số, lưới, độ nhạy (sau TK 2,89% trừ khi ghi)

**Trọng số (V1, trước TK).**
- Đường thử: 0,20/0,25/0,35/0,20 → 8.472 · 0,15/0,25/0,40/0,20 → 8.065 · **chốt 0,15/0,25/0,35/0,25 → 7.772**.
- Biến thể bù trừ: H 7.891 · V2 7.979.

**Bộ trọng số khác (sau TK).** Lạc quan 0,25/0,30/0,30/0,15 **9.098** · r1-style 9.297 · A/B′/C 7.380 · đều 8.338 · bi quan 0,10/0,15/0,35/0,40 **5.916** · 0/0/0,5/0,5 3.982.

**Lưới P(A) × P(C)** (P(C) ∈ {0,10; 0,20; 0,25; 0,30; 0,40}, B:B′ = 1:1,4):
- P(A)=0: 7.694…5.510
- P(A)=0,15: 8.641…6.456
- P(A)=0,25: 9.271…7.087
- P(A)=0,35: **9.902**…7.718
- ⇒ **0/30 ô > 10.250**. Kết luận "trên vùng" không còn phụ thuộc vào trọng số.
- Chỉ khi loại hẳn B′/C (A/B thuần, ≥ B 10.975 > 10.555 = 10.250/0,9711) thì giá mới dưới tâm.

**Độ nhạy tâm TRƯỚC TK** (một tham số mỗi lần):
- Thuỷ điện: g 1% **8.612** / 2% 9.550 · nền 330 6.571 / 350 7.175 / 379,06 8.046 / 397 **8.580** · dừng 2050 7.319 · bỏ cắt −15% 8.198
- Giá sau FIT 1%: 7.864 · tỷ giá g 0% 7.170 / 2,5% 8.026 / 3,2% 8.293
- Pháp lý / tài sản: Bầu Ngứ dừng 2027 6.945 · Phương Mai = 0 7.285 · BIDV 70 = 0 7.478
- Thu hồi: phải thu vượt = 0 5.966 · VAT hồi tố thu hồi 8.039
- **Cận trên một-tham-số cao nhất** (thuỷ điện g 2%): 9.550 × 0,9711 = **9.274** < 10.250.

## 4. DSCR 2027 (sau thuế + HTKD, trước hồi tố)
A **1,36** · B **1,23** · B′ **1,09** · C **0,79** (r4: 1,37/1,24/1,10/0,80). EBITDA B′ 523,4; lãi 130,6; gốc 280.

## 5. Vị thế & lợi thế cạnh tranh (5F) — tái dùng (V5)
5F đầy đủ làm 20/11/2026 (REPORT.md §5), chưa quá 12 tháng ⇒ tái dùng: **moat_tier NONE**.
- L1 (biểu giá phẳng 6–7 năm) củng cố kết luận "không có quyền định giá".
- Không thưởng, không trừ. Dòng tiền hữu hạn ⇒ không áp terminal.

## 6. Chi phí vốn (V1/V2)
- r = **13,5%**, neo 03/11/2026 = lãi huy động 12T hiệu dụng 7,40%.
- Kiểm lại 23/11/2026 bằng `deposit_rate_vn.consumer_deposit_rate_detail()`: **7,40%** (cctg_12m 02/11/2026, Big-4 6,80%, last_update 16/11/2026) ⇒ Δ = 0 ⇒ r giữ 13,5% (β = 1).
- Dải Ke nội địa 12,3–13,4% báo kèm.
- Độ nhạy tâm sau TK: −100bp **8.119** · −50bp 7.826 · 0 **7.547** · +50bp 7.284 · +100bp **7.033**.

## 7. Pha SAU KHOÁ — thanh khoản (V3) + so giá
**Thanh khoản (phương pháp r3/r4 giữ nguyên).**
- σ ngày 1,626% · ADV trung vị 2,20 tỷ (250 phiên) / 1,13 tỷ (68 phiên) · spread Corwin-Schultz 0,88%.
- ⇒ d(5 tỷ) **2,89%** (cận dưới 3,87%).

**So giá.**
- Giá 10.250 (19/11/2026, `model/data/px_tta.csv`) = **1,36×** tâm sau TK, 1,32× trước TK ⇒ **trên vùng hợp lý**, vượt ngưỡng trên 8.680 khoảng 18%.

**Sizing (V8)** — chuẩn 2–4% NAV/mã:
- Giá đang trên vùng ⇒ **không đề xuất mua**.
- Nếu giá về vùng hợp lý: tối đa 2% NAV (cận dưới), vì rủi ro FIT hai chiều và thanh khoản 22 phiên để thoát 5 tỷ.

## 8. Điều kiện đổi nhận định (hai chiều) + HARD ABANDON
**Chiều tăng:**
- FIT Núi Một 1 được xác nhận giữ (loại B′/C).
- BGCPTĐ 2027 tăng danh nghĩa, hoặc có PPA Ngòi Hút 2 với điều khoản chỉ số hoá ⇒ quay về độ nhạy g 1% (8.612).
- EPTC trả lại > 70% hoá đơn hai quý liên tiếp.

**Chiều giảm:**
- Quyết định hồi tố/hạ giá cả hai nhà máy.
- Phải thu EPTC > 450 tỷ.
- BGCPTĐ giảm danh nghĩa.

**HARD ABANDON** — giữ #1–#7 của r4:
- #3: DSCR 2027 sau thuế + HTKD < 1,00, hoặc vi phạm covenant / giãn-hoãn nợ / tái cấp vốn.
- #6: có quyết định đình chỉ/thu hồi/không cấp giấy phép vận hành Bầu Ngứ theo Luật Thuỷ lợi.
- #7: công bố cam kết vốn chủ cho Phước Hoà > 300 tỷ trước khi vụ FIT có kết luận. TMĐT dự án 22.865 tỷ (báo) ⇒ chỉ cần TTA góp ≥ ~4,4% vốn chủ dự án (giả định vốn chủ 30% TMĐT, ước lượng) là chạm ngưỡng.

## 9. Hai nền (V6 — chỉ hiển thị)
| V_ngắn (r1) | V_dài (DCF tâm trước TK) | D = \|ln(V_ngắn/V_dài)\| |
|---|---|---|
| 6.632 | 7.772 | 0,159 < ln2 — không cờ |

## 10. Hạng mục còn thiếu / không kiểm chứng được (sau rev 5)
**Còn thiếu:**
- Cơ chế giá / đăng ký thị trường điện của Ngòi Hút 2. Đã trung hoà bằng base phẳng; rủi ro giá thị trường còn lại là hai chiều.
- Tỷ lệ góp vốn và cam kết vốn chủ Phước Hoà (TMĐT 22.865 tỷ theo báo).
- Thời hạn HTKD; giấy phép nước/đất thuỷ điện.
- BCTC Phương Mai; bên được bảo lãnh của hạn mức BIDV 70 tỷ; giấy phép Thuỷ lợi Bầu Ngứ.
- Thu hồi VAT hồi tố; lịch gốc Q4/2026.
- Bản gốc QĐ 4036/2019 (năm 2020) chưa đối chiếu. Không đổi kết luận vì 2021→2026 phẳng đã xác nhận.

**Đã đóng ở rev 5:**
- Chỉ số thuỷ điện (L1).
- Chỉ số giá sau FIT (L2).
- Chuỗi DT thuỷ điện 2021–2024 (L3).

Phản biện lại: bắt buộc (tâm dịch −11,7% > 5%) — `skeptic/r3.json` (vòng cuối).

## Khai md5
- **assumptions_file** = `agents/Taylor/research/dd_TTA_20261120/model/dcf_tta_r5.py` · **assumptions_md5 = `bfeea44ff92a6aca5d06eaf48dd79193`**
- Output `model/out_r5.json`: md5 `163c4edebba54dd8c7f4dc84b1d4562f`
- Khoá schema: `assumptions_TTA_r5.json` (md5 ghi trong finding)
- Tái lập: `cd dd_TTA_20261120 && /home/trido/thanhdt/wc_venv/bin/python -I model/dcf_tta_r5.py`

**Nguồn tải mới** (`src/dl_r5/`, từ static2.vietstock.vn; website công ty không phân giải được từ máy này):
| Tệp | md5 |
|---|---|
| TTA_BCTN_2021.pdf | `460981520c9b920343a7d5b67c49b212` |
| TTA_BCTN_2022.pdf | `87a966d1f868da5d44ba5c5b3a07fe08` |
| TTA_BCTN_2023.pdf | `a2c6e878f224de73221130d10cef28a0` |
| TTA_BCTN_2024.pdf | `f0ea3701486842e39060a18de4065bd3` |
| TTA_BCTC_KT_2024.pdf | `13311491e2296f2a2dba322c5bc255cb` |

**Quyết định giá điện:**
- [QĐ 4036/2019 (năm 2020)](https://luatvietnam.vn/thue/quyet-dinh-4036-qd-bct-bieu-gia-chi-phi-tranh-duoc-nam-2020-180634-d1.html)
- [QĐ 650/2021](https://luatvietnam.vn/tai-chinh/quyet-dinh-650-qd-bct-bieu-gia-chi-phi-tranh-duoc-nam-2021-198589-d1.html)
- [QĐ 131/2022](https://hethongphapluat.com/quyet-dinh-131-qd-bct-ve-bieu-gia-chi-phi-tranh-duoc-nam-2022-do-bo-truong-bo-cong-thuong-ban-hanh.html)
- [QĐ 1028/2023](https://luatvietnam.vn/dien-luc/quyet-dinh-1028-qd-bct-2023-bieu-gia-chi-phi-tranh-duoc-271008-d1.html)
- [QĐ 1670/2024](https://hethongphapluat.com/quyet-dinh-1670-qd-bct-ve-bieu-gia-chi-phi-tranh-duoc-nam-2024-do-bo-truong-bo-cong-thuong-ban-hanh.html)
- [QĐ 3734/2024 (năm 2025)](https://hethongphapluat.com/quyet-dinh-3734-qd-bct-nam-2024-ve-bieu-gia-chi-phi-tranh-duoc-nam-2025-do-bo-truong-bo-cong-thuong-ban-hanh.html)
- [QĐ 392/2026](https://luatvietnam.vn/dien-luc/quyet-dinh-392-qd-bct-2026-ban-hanh-bieu-gia-chi-phi-tranh-duoc-cho-nha-may-thuy-dien-nho-431541-d1.html)

**Quy định thị trường điện:** [TT 16/2025/TT-BCT](https://thuviennhadat.vn/vbpl/thong-tu-16-2025-tt-bct-van-hanh-thi-truong-ban-buon-dien-canh-tranh-644586.html).

**Phước Hoà:** [nhadautu.vn](https://nhadautu.vn/khanh-hoa-go-kho-cho-hai-du-an-thuy-dien-tich-nang-gan-44000-ty-d101338.html).
