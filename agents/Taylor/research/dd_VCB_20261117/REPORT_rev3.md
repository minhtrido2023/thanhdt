# DD — VCB (Ngân hàng TMCP Ngoại thương Việt Nam) · REV 3 · BCTC Q3/2026 · 2026-11-23 · job `Taylor_20261122_234428`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua; user quyết. Không ghi `dd_price_zones.json`, không email.
> Chuỗi bản: `REPORT.md` (rev 1, dd_date 2026-11-17; sổ: tâm 38.800 / vùng 30.800–42.000) → skeptic r1 REFUTED →
> `REPORT_rev2.md` (tâm 44.900) → skeptic r2 REFUTED (`skeptic/r2.json`) → **bản này**. Các bản cũ giữ nguyên.
> **Nguồn số:** [KT20xx] = BCTC hợp nhất KIỂM TOÁN năm 20xx, đọc ảnh scan từng trang trong phiên 23/11/2026:
> 2025 = `src/VCB_BCTC_2025_KT_HN.pdf` (EY); 2017/2019/2021/2023 tải từ
> `static2.vietstock.vn/data/HOSE/<năm>/BCTC/VN/NAM/VCB_Baocaotaichinh_<năm>_Kiemtoan_Hopnhat.pdf` (KPMG 2017–2021, EY 2023).
> [Q3] = `src/VCB_BCTC_Q3_2026_HN.pdf`. [BQ] = `tav2_bq.ticker_financial`. [Báo] = báo chí, ghi rõ.
> **Khoá giả định:** `assumptions_VCB_rev3_20261123.json` md5 `07853fb1c382f7c1b13486c64a8b5162` (+ bảng cân đối/KQKD Q3 giữ
> từ `assumptions_VCB_20261117.json` md5 `85d41e08f834127e57cd740ed88dd931`); tính bằng `calc_rev3.py`
> (md5 `d899e10ec2800744b92172355c6f4361`) → `calc_rev3_output.txt` (md5 `c77e48a41358ec3aaa40bfecbae5a069`).
> `bin/dd_assumptions_lint.py`: rc=0, chỉ cảnh báo (file chưa theo schema v1 — giai đoạn cảnh báo).
> **Mù giá:** khoá giả định trước khi so giá; không truy vấn giá mới. Giá đối chiếu duy nhất 52.100 (17/11/2026, từ rev 1), chỉ ở mục 7.

## 0. Kết luận

**Ở r 13,5% của fleet, giá trị có trọng số là 36.000 đ/cp (cơ sở 38.400; xấu 21.200 / tốt 45.900). Vùng hợp lý 31.200–42.500 (Ke ±100bp trên giá trị có trọng số). Giá 52.100 (17/11) nằm TRÊN vùng, cao hơn tâm 45%.**

Hai thay đổi so với rev 2, đều do skeptic r2 và đều có nguồn kiểm toán:
1. **Quỹ khen thưởng phúc lợi** trích từ lợi nhuận, không thuộc cổ đông: 2.975,8 tỷ = **8,46% LN 2025** (2024: 7,96%) [KT2025 TM34(a) tr.61]. ROE thuộc cổ đông giảm tương ứng.
2. **Biên PPOP và chi phí tín dụng lấy CÙNG KỲ** trong mỗi kịch bản: cơ sở = 9T/2026 (biên 3,55%, CC 0,70%); tốt = cửa sổ 2022–2026; xấu = stress (biên đáy 2025 + CC TB 9 năm).

| Mục | Số | Nguồn |
|---|---|---|
| BVPS 30/09/2026 | **30.359 đ** (VCSH mẹ 253.669 tỷ / 8.355,7 triệu cp); BQ 30.370 (Δ0,04%) | [Q3], [BQ] |
| ROE thuộc cổ đông — cơ sở | **15,2%** = (3,55% − 0,70%) × dư nợ/VCSH 7,30 × (1 − thuế 20%) × (1 − KTPL 8,46%) | `calc_rev3.py` |
| Kịch bản | Xấu 0,25: 11,5% ⇒ **21.200** · Cơ sở 0,50: 15,2% ⇒ **38.400** · Tốt 0,25: 16,8% ⇒ **45.900** · **Có trọng số 36.000** | `calc_rev3.py` |
| CC lịch sử (chi phí dự phòng / dư nợ BQ) | TB 2017–25 **0,87%** · tổn thất thực (xoá nợ) 2017–25 **0,49%** · TB 2022–26 0,49% · 9T/26 năm hoá **0,70%** | [KT2017–2025], [Q3] |
| Biên PPOP / dư nợ BQ | 2018–22 ~4,2–4,4% → **2025 3,02%** (đáy) → 9T/26 lõi **3,55%**; TB 2022–26 3,63% | [KT], [Q3] |
| Thanh khoản (V3) | chiết khấu **0%** ⇒ giá trị trước = sau = 36.000 | mục 7 |
| Moat (V5, tái dùng 5F 17/11) | **NARROW** — không thưởng, không trừ | mục 6 |
| Không kiểm chứng được | VCBNeo (ex-CBBank); CET1/LDR TT22/Pillar 3; hình thức 16.571 tỷ LN 2025 còn lại | mục 10 |

**Đọc nhanh:** VCB **đắt** ở r 13,5%. Giá 52.100 hàm ý ROE thuộc cổ đông bền ≈ 18,2% (ở Ke 13,5%) hoặc Ke ≈ 11,8% (ở ROE 15,2%) —
cả hai đều ngoài các kịch bản dựng từ số kiểm toán (kịch bản tốt chỉ 16,8%). Mốc đọc Ke theo β thật 12% cho 49.900, vẫn dưới giá.
So với rev 1 (38.800) tâm giảm 7%: CC có nguồn nay **thấp hơn** 0,8% (đẩy lên), nhưng quỹ KTPL và cặp cùng kỳ kéo xuống nhiều hơn.

---

## 1. Đính chính — từng hạng mục skeptic r1 và r2

### 1a. Skeptic r2 (22/11 → REPORT_rev2) — 5 hạng mục
| # | Hạng mục r2 | Xử lý rev 3 | Loại |
|---|---|---|---|
| r2-1 | **Quỹ KTPL ~9–12% LN rời VCSH** (killer objection); rev 2 bác bằng cửa sổ 9T sai | **Đã đọc [KT2025] TM34(a) tr.61:** trích quỹ KTPL 2025 **2.975.811** tr / LN 35.177.663 tr = **8,46%**; 2024 2.692.912 / 33.831.386 = 7,96%; "tạm trích lập vào thời điểm cuối năm" (nên 9T không thấy). Đối soát VCSH 2025: 196.112,9 + 35.177,7 − cổ tức tiền 3.760 − KTPL 2.975,8 = 224.554,8 so với thực 224.487,2 ⇒ **lệch còn 68 tỷ**. Mô hình: ROE × (1 − 8,46%) ở mọi kịch bản. Rev 2 mục 11 SAI, đã thay | (a) vào base, có nguồn |
| r2-2 | **Chọn đầu vào bất đối xứng**: biên 2026 nhưng CC lịch sử (thấp hơn mọi số 2026) | Mỗi kịch bản dùng **một cửa sổ**: cơ sở = 9T/26 (biên 3,55%, CC tổng 9.180 × 12/9 / dư nợ BQ = **0,70%**); tốt = 2022–2026 (biên TB 3,63%, CC TB 0,49%); xấu = stress biên 2025 + CC TB 9 năm 0,87% (ghi rõ là ghép stress). Cặp Q3 riêng (biên 3,99%, CC 1,42% năm hoá) ⇒ ROE 13,7% ⇒ **31.500** — hiển thị; CC Q3 là **tích luỹ bao phủ** (9T không xoá nợ: nợ đã xử lý ngoại bảng 83.546,3 → 83.482,8; hình thành NPL 9T 3.104 tỷ ≈ 0,24%/năm) nên không lấy làm mức bền. Tổn thất + duy trì 0,62% giữ làm kiểm chéo (thấp hơn base) | (a) |
| r2-3 | NII/dư nợ nhảy 3,76% → 4,37% giữa lúc chỉ đạo giảm lãi chưa giải thích | NII / tổng tài sản BQ cũng tăng 2,60% (2025) → 2,98% (9T/26) ⇒ không phải hiệu ứng mẫu số cho vay. Nguyên nhân (cơ cấu nguồn KBNN 171,6 nghìn tỷ, định giá lại tài sản/nguồn): **không kiểm chứng được** từ BCTC quý. Rủi ro đảo chiều nằm trong kịch bản xấu và lưới biên (3,02% ⇒ 25.300) | (c) + (b) |
| r2-4 | g 7% không nguồn; tỷ lệ chia hàm ý 54–59% vs chia tiền thực ~11% | g 7% giữ (ước lượng, ≤ GDP danh nghĩa dài hạn — luật V2). Gordon P/B đúng khi phần giữ lại sinh lời ROE; VCB giữ lại ~89% ⇒ hiển thị hai giai đoạn g1 10–13%: **39.400–40.500** ở Ke 13,5% (+3–5% so base). Không đổi base | (b) |
| r2-5 | Chi phí dự phòng 2017–19 có thể gồm trái phiếu đặc biệt VAMC | **Chưa kiểm** (cần TM33 từng năm). Ảnh hưởng hai chiều tới tỷ lệ tổn thất 0,49% — nay chỉ là kiểm chéo, **không còn nằm trong base** (base dùng CC 9T/26) | (c) |

### 1b. Skeptic r1 (rev 1) — 11 hạng mục
| # | Hạng mục r1 | Xử lý (giữ từ rev 2, cập nhật rev 3) | Loại |
|---|---|---|---|
| 1 | CC 0,8% không nguồn (killer) | Chuỗi CC 2017–2025 từ 5 bộ BCTC kiểm toán (mục 3). Base nay dùng CC **cùng kỳ** 0,70%; lưới 0,5 / 0,6 / 0,62 / 0,8 / 0,87% ở mục 5 | (a) |
| 2 | Trung điểm hai mốc ROE là phán đoán | Bỏ trung điểm; thay bằng 3 kịch bản, mỗi kịch bản một cửa sổ dữ liệu | (a) |
| 3 | Số KT 2025 lấy từ dispatch | **Đọc lại từ PDF:** PPOP 47.211.823 (B03 tr.9) ✓; dư nợ 31/12/2024 1.449.198.899 (B02 tr.6) ✓; VCSH mẹ cuối 2024 196.209.168 − 96.261 = 196.112.907 ✓; cuối 2025 224.487.205 ✓ | (a) |
| 4 | Bảo lãnh ×2,37, Xây dựng +72% chưa đối chiếu | **Đọc:** [KT2025] B02 tr.8 + [Q3] B02a tr.5: bảo lãnh 58.339,4 (31/12/2024) → 138.449,7 (30/09/2026) = ×2,37 ✓; [KT2025] TM9 tr.38: Xây dựng 90.513,0 → 155.288,0 = +71,6% ✓. WARNING, đi vào kịch bản xấu | (b) |
| 5 | Thuế 20% vs 18,3% | ETR 2025 kiểm toán 8.821,7 / 44.019,6 = **20,04%** [KT2025 B03 tr.10]; 18,3% của 9T/26 thấp vì lãi đánh giá lại hợp nhất không chịu thuế | (a) |
| 6 | Trừ −2.850 đ vô điều kiện sau GDKHQ | Cổ tức tiền 450 đ/cp (~3.760 tỷ) đã GDKHQ trước 24/07, trả 27/08/2026 [vietnamplus 10/07/2026] ⇒ đã trong VCSH 30/09 (đối soát VCSH 2025 ở r2-1 khớp với 3.760). Phần còn lại 16.571 tỷ: hình thức chưa công bố [baodautu 24/04/2026]; tiền lệ 2025 chia cổ phiếu 49,5% (vốn điều lệ 55.890,9 → 83.556,8, [KT2025] B02 tr.7). Base không trừ; nếu bằng tiền: −1.983 đ/cp (mục 5) | (b) điều kiện |
| 7 | VCBNeo (ex-CBBank) không định lượng | Không nguồn nào có vốn/lỗ luỹ kế/cam kết ⇒ **không kiểm chứng được**; độ nhạy minh hoạ mục 5 | (c) |
| 8 | CAR một nguồn; thiếu CET1, LDR, Pillar 3 | CAR hợp nhất 30/06/2026 **11,14%** (vcci, 24hmoney, ACBS 07/08/2026 — cùng số, vẫn là báo); CET1/LDR TT22/Pillar 3 **không kiểm chứng được**; độ nhạy CAR 12% mục 5 | (b)/(c) |
| 9 | Nhóm 2, nhóm 3–4, bảo lãnh, Xây dựng không vào mô hình | Kịch bản xấu dùng CC 0,87% (gồm COVID 2020–21: 1,27–1,31%); base dùng CC 9T/26 0,70% đã phản ánh đợt trích Q3 | (b) |
| 10 | Riêng lẻ 6,5% | Ngoài base (V4a NPV=0, giá phát hành chưa biết) | (b) |
| 11 | Quỹ KTPL | **Rev 2 đánh giá sai là nhỏ** — sửa ở r2-1 | (a) |

**Flip-flop minh bạch:** rev1 r1 42.035 → rev1 r3/r4 35.497 (cơ sở) / 38.800 (trọng số) → rev 2 47.300 / 44.900 → **rev 3 38.400 / 36.000**.
Mọi bước rev 2–3 có đầu vào mới từ BCTC kiểm toán gốc (chuỗi CC 9 năm; TM34 quỹ KTPL) hoặc sửa nhất quán cửa sổ; không bước nào dùng giá.

## 2. Chất lượng lợi nhuận (9T/2026, hợp nhất, tỷ đồng)

| Dòng | 9T/26 | 9T/25 | Δ |
|---|---|---|---|
| Thu nhập lãi thuần | 57.179 | 42.505 | +34,5% |
| PPOP | 49.620 | 35.470 | +39,9% (lõi, bỏ một lần 3.171: +30,9%) |
| Tổng dự phòng (cho vay 6.190 + TPDN 2.997) | (9.180) | (2.338) | ×3,9 |
| LNTT | 40.440 | 33.133 | +22,1% |
| LNST mẹ | 33.032 | 26.549 | +24,4% headline; **lõi 29.861, +12,5%** |

Một lần 3.171 tỷ: lãi đánh giá lại khi Bonday-Bến Thành thành công ty con (giải trình LNST mục 2, TM8), không chịu thuế.
NII/dư nợ BQ: 2022 5,06% → 2023 4,44% → 2024 4,08% → **2025 3,76%** → 9T/26 4,37%; NII/tổng TS BQ 2025 2,60% → 9T/26 2,98%.

## 3. Chuỗi chi phí tín dụng & biên PPOP — BCTC kiểm toán gốc (tỷ đồng)

| Năm | Dư nợ KH cuối kỳ | Chi phí dự phòng RRTD (B03) | CC / dư nợ BQ | PPOP | PPOP / dư nợ BQ | Nguồn |
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
| 9T/26 năm hoá | 1.816.093 (30/09) | 12.240 | **0,70%** | 61.932 lõi | **3,55%** | Q3 |

Tổn thất thực 2017–2025: tổng chi phí dự phòng 62.659 − tăng số dư dự phòng 20.070 (cho vay 8.087 → 24.976; CK đầu tư 180 → 3.362; liên NH 0 → 0)
= 42.588 tỷ = **0,49%** dư nợ BQ; + duy trì tỷ lệ dự phòng 1,49% khi dư nợ tăng 9%/năm (ước lượng) 0,12% ⇒ **0,62%** (kiểm chéo; base dùng 0,70% cùng kỳ, cao hơn).
2025 thấp vì hoàn nhập dự phòng cụ thể (20.495 → 12.553 sau xoá 7.288; [KT2025] TM10 tr.39).

## 4. Chất lượng tài sản, ngoại bảng, vốn [Q3, KT2025]

| Chỉ tiêu | 30/09/2026 | 31/12/2025 |
|---|---|---|
| Nhóm 2 | 4.995 (0,28%) | 2.702 (0,16%) |
| Nợ xấu nhóm 3–5 | 12.817 (**0,71%**) | 9.714 (0,58%) |
| Dự phòng cho vay | 31.168; bao phủ **243%**; = 1,75× toàn bộ nhóm 2–5 (17.812) | 24.980; 257% |
| Nợ khó đòi đã xử lý (ngoại bảng) | 83.482,8 | 83.546,3 ⇒ không xoá nợ mới 9T |
| Bảo lãnh (vay vốn + khác) | **138.449,7** (≈55% VCSH) | 99.093,7 (31/12/2024: 58.339,4) |
| Dư nợ Xây dựng | n/a | **155.288** (2024: 90.513, +71,6%) |
| CAR hợp nhất | 11,14% (30/06, [Báo]; chưa Pillar 3) | — |
| CET1 / LDR TT22 | **không kiểm chứng được** | — |

⚠️ WARNING (không nhân vào base ngoài CC 9T/26 đã có): nhóm 2 +85% YTD khi dư nợ +8,5%; nhóm 3–4 1.063 → 4.229; bảo lãnh ×2,37 trong 21 tháng; Xây dựng +71,6% năm 2025.

**Cổ đông/hành động vốn:** Nhà nước 74,80%, Mizuho 15,00% [Q3 TM1(b)]; 8.355.675.094 cp không đổi 9T. Chờ: thưởng từ quỹ dự trữ bổ sung vốn
điều lệ tối đa ~1.068 triệu cp (~10.686–10.687 tỷ, ≈12,8%) [nhandan, baodautu 24/04/2026]; phân phối 16.571 tỷ còn lại của LN 2025 (hình thức
chưa công bố); riêng lẻ ≤6,5% (543,1 triệu cp); NH con tại VIFC vốn 3.000 tỷ. Cổ phiếu thưởng/cổ tức cổ phiếu không đổi giá trị.

**VCBNeo (ex-CBBank, nhận chuyển giao bắt buộc giá 0 đồng, QĐ 2299/QĐ-NHNN 17/10/2024):** miễn hợp nhất và loại khỏi CAR; BCTC không có thuyết
minh quy mô/lỗ luỹ kế/hỗ trợ; báo chí 03–07/2026 chỉ nói "bắt đầu có lãi" (không số) ⇒ **không kiểm chứng được**.

## 5. Định giá — P/B = (ROE − g)/(Ke − g), mù giá thị trường

**Không áp dụng cho ngân hàng:** P/PCF, EV/EBITDA, FCFE ⇒ **V6 (V_ngắn/V_dài, C4, D2) không áp**.

**V1 — r:** **13,5%** tại neo 03/11/2026; lãi huy động 12T hiệu dụng `deposit_rate_vn` 7,40% (CCTG 12M 02/11/2026; đo trong rev 1 ngày 17/11) ⇒ Δ=0.
D4: hai đầu Ke nội địa 12,3% / 13,4% ⇒ base **47.100 / 39.000**. Mốc đọc Ke β thật (0,76 thô, Blume 0,84; rev 1) 12% ⇒ 49.900 — không làm tâm.

**ROE thuộc cổ đông** = (biên PPOP − CC) × (dư nợ BQ / VCSH mẹ BQ 9T/26 = 7,30) × (1 − 20%) × (1 − quỹ KTPL 8,46%). g = 7% (ước lượng).

| Kịch bản | P | Cửa sổ | Biên PPOP | CC | ROE | P/B | Giá trị/cp |
|---|---|---|---|---|---|---|---|
| Xấu — stress: NIM về đáy theo chỉ đạo + tổn thất kiểu 2017–21 | 0,25 | ghép stress | 3,02% (2025) | 0,87% (TB 2017–25) | 11,5% | 0,70 | **21.200** |
| **Cơ sở** | 0,50 | 9T/2026 | 3,55% | 0,70% | **15,2%** | 1,265 | **38.400** |
| Tốt | 0,25 | 2022–2026 | 3,63% | 0,49% | 16,8% | 1,51 | **45.900** |
| **Có trọng số** | | | | | | | **36.000** |

Xác suất 0,25/0,50/0,25 giữ như rev 1 (không có cơ sở mới để đổi).

**Lưới CC trên biên 3,55%:** 0,5% ⇒ 43.400 · 0,6% ⇒ 40.900 · 0,62% (tổn thất + duy trì) ⇒ 40.500 · 0,8% ⇒ 35.900 · 0,87% ⇒ 34.300.
**Lưới biên ở CC 0,70%:** 3,02% ⇒ 25.300 · 3,55% ⇒ 38.400 · 3,63% ⇒ 40.500. Cặp Q3 (3,99% / 1,42%) ⇒ 31.500.

**Độ nhạy theo lãi huy động (V1), base:**

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β = 1 | 45.400 (+18%) | 41.600 (+8%) | 38.400 | 35.700 (−7%) | 33.300 (−13%) |
| β = 0,5 | 41.600 | 39.900 | 38.400 | 37.000 | 35.700 |

Có trọng số ở Ke ±100bp: **42.500 / 31.200** ⇒ vùng hợp lý. g 6% / 8% ⇒ 37.300 / 39.900.

**Độ nhạy KHÔNG vào base:**
- CAR lên 12% bằng giảm đòn bẩy (D-SIB giả định): ROE 14,1% ⇒ **33.300** (−13%).
- VCBNeo tổn thất vào VCSH (ước lượng minh hoạ, không kiểm chứng được): 5 / 10 / 20 nghìn tỷ ⇒ 37.600 / 36.900 / 35.400.
- Nếu 16.571 tỷ còn lại chia **bằng tiền** (chưa công bố): −1.983 đ/cp ⇒ base sau GDKHQ 35.900, tổng cho cổ đông gồm tiền 37.900; có trọng số sau GDKHQ 33.600. Nếu bằng cổ phiếu (≈19,8% số cp): không đổi giá trị. **Vùng chỉ trừ khi có thông báo trả tiền.**
- Hai giai đoạn (hiển thị, giữ lại ~89% thực tế): Ke 13,5%, g1 13% / 10% ⇒ 40.500 / 39.400; Ke 12,5% ⇒ 49.400 / 47.300.

**Vùng đọc:** rẻ ≤ **30.600** (0,85 × tâm có trọng số) · hợp lý **31.200–42.500** · trên **42.500** = đắt theo r 13,5%.

**V4:** VIFC, riêng lẻ 6,5%, VCBNeo = đầu tư/hành động vốn mới ⇒ base NPV = 0 ở giá sổ sách. Không có capex tuân thủ đáng kể ngoài chi phí hoạt động (đã trong PPOP).

## 6. Vị thế & lợi thế cạnh tranh (5F) — V5: tái dùng bản 17/11 (<12 tháng) + kiểm nhanh

Bản đầy đủ `REPORT.md` §6 (17/11/2026): **moat_tier NARROW**, moat_type = chi phí vốn (CASA 31,8% vs ngành 19,4%) + chất lượng tài sản (NPL 0,71% vs ngành 2,09%);
rủi ro số 1 = nghĩa vụ chính sách (chỉ đạo lãi vay, NH chuyển giao, quy chế KBNN). Kiểm nhanh 23/11: ROE thuộc cổ đông base 15,2% > Ke 13,5% nhưng chỉ ~1,7pp;
biên PPOP giảm 4,45% → 3,02% (2022–25) là đồng hồ cắt hào. Không thưởng, không trừ. Độ nhạy WIDE (kịch bản tốt, ROE 16,8%) 45.900 · NARROW 38.400 · NONE (ROE = Ke) 30.400.

## 7. Sau khoá — V3 thanh khoản, so giá, sizing

- **V3:** ADV trung vị 3 năm 175 tỷ/phiên (rev 1, BQ đến 17/11/2026; không truy vấn lại). Tham gia 10–20% ⇒ 17,5–35 tỷ/phiên; vị thế 2–4% NAV ở quy mô fleet (dưới vài chục tỷ, ước lượng) thoát ≤2 phiên; free float ~10% không ràng buộc ⇒ **chiết khấu 0%**, trước = sau = 36.000.
- **So giá** (52.100, 17/11/2026): P/B 1,72; **+45%** so tâm có trọng số, +36% so base; **trên** đầu trên vùng 42.500. Giá hàm ý ROE thuộc cổ đông 18,2% ở Ke 13,5%, hoặc Ke 11,8% ở ROE 15,2%.
- **Nhãn:** **đắt theo r 13,5%**; chất lượng tài sản tốt nhất hệ thống nhưng giá đã trả trước ROE cao hơn mọi kịch bản dựng từ số kiểm toán.
- **V8 sizing:** khung chuẩn 2–4% NAV; ở giá hiện tại **không đề xuất mở vị thế**. Vào vùng rẻ ≤ 30.600 mới xét đầu dưới 2%.

## 8. Pháp lý / quản trị — chỉ WARNING

- KTNN điều chỉnh hồi tố 2025, nhỏ (VCSH +29 tỷ). EY 2025: chấp nhận toàn phần, không ngoại trừ.
- Thanh tra NHNN cấp chi nhánh 2026 (Đà Nẵng, Bình Phước) [Báo/DNSE]; không thấy vụ án.
- Nghĩa vụ chính sách: VCBNeo (không kiểm chứng được), chỉ đạo giảm lãi, phê duyệt hình thức cổ tức/tăng vốn bởi cơ quan chủ sở hữu.
- BCTC Q3 không soát xét.

## 9. Điều kiện đổi nhận định (hai chiều)

**Tâm ↑:** BCTC Q4/2026 biên PPOP cả năm ≥ 3,55% và CC cả năm ≤ 0,6%; lãi huy động hiệu dụng −50bp (+8%); riêng lẻ ≥ 1,5× BVPS; công bố 16.571 tỷ chia cổ phiếu; tỷ lệ trích KTPL giảm.
**Tâm ↓:** biên PPOP Q4 quay về ≤ 3,1% (base → kịch bản xấu); NPL > 1,0% hoặc nhóm 2–4 > 1,0% dư nợ; CC năm 2026 > 0,87%; CAR/CET1 công bố < 11% buộc giảm đòn bẩy (−13%); hỗ trợ VCBNeo > 5 nghìn tỷ hoặc bỏ miễn trừ hợp nhất/CAR; lãi huy động +50bp (−7%); 16.571 tỷ trả bằng tiền (vùng −1.983 đ sau GDKHQ).
**Theo dõi:** BCTC Q4/2026 (~01/2027), Pillar 3, CBTT hình thức cổ tức, thông tin VCBNeo.

## 10. Không kiểm chứng được / còn thiếu

- VCBNeo: vốn, lỗ luỹ kế, cam kết hỗ trợ, thời hạn miễn trừ — không có nguồn; ảnh hưởng ước lượng −2% … −8% base.
- CET1, LDR theo TT22, Pillar 3 CAR — không có; CAR 11,14% chỉ từ báo chí.
- Nguyên nhân NII/tài sản tăng 2,60% → 2,98% trong 2026 — BCTC quý không cho tách.
- Thành phần VAMC trong chi phí dự phòng 2017–19 — chưa kiểm (chỉ ảnh hưởng kiểm chéo 0,62%, không ảnh hưởng base).
- Hình thức phân phối 16.571 tỷ LN 2025 — chưa công bố.
- File khoá chưa theo schema `dd_assumptions_v1` (lint cảnh báo, rc=0).

## Nguồn
- BCTC hợp nhất kiểm toán VCB 2017/2019/2021/2023/2025: `https://static2.vietstock.vn/data/HOSE/<năm>/BCTC/VN/NAM/VCB_Baocaotaichinh_<năm>_Kiemtoan_Hopnhat.pdf`
- BCTC Q3/2026: https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%203/VCB_Baocaotaichinh_Q3_2026_Hopnhat.pdf
- Cổ tức 450 đ: https://www.vietnamplus.vn/vietcombank-chuan-bi-chi-hon-3760-ty-dong-tra-co-tuc-tien-mat-cho-co-dong-post1123414.vnp
- ĐHĐCĐ 2026: https://baodautu.vn/dhdcd-vietcombank-dang-tim-nha-dau-tu-de-chao-ban-65-von-du-chi--20331-ty-dong-tra-co-tuc-d576464.html · https://nhandan.vn/ocop/vietcombank-thong-qua-ke-hoach-phat-hanh-hon-1-ty-co-phieu-thanh-lap-ngan-hang-tai-trung-tam-tai-chinh-quoc-te-viet-nam-post958144.html
- CAR 30/06/2026: https://vcci.com.vn/tin-tuc/tu-nen-tang-tai-chinh-vung-chac-vietcombank-mo-rong-du-dia-tang-truong-moi · https://24hmoney.vn/news/vcb-giu-phong-do-tai-san-vuot-2-67-trieu-ty-c1a2806199.html · https://acbs.com.vn/acbsmedia/2026/08/VCB_cap-nhat_ACBS_07.08.2026-VN.pdf
- VCBNeo: https://en.vneconomy.vn/clear-signs-of-recovery-from-four-weak-banks.htm · https://vnba.org.vn/en/transferred-weak-banks-under-restructuring-17545.htm
- Ngành (đọc mù): `kb/data_registry/market-state/sector_read_ngan_hang_quoc_doanh_20261117.md`; vĩ mô: `macro_snapshot_20261117.md`.
