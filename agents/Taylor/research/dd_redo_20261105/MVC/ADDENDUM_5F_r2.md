# MVC — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_123139)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận: moat NONE (mảng tự vận hành) / NARROW-LOCATION qua cổ phần NNC 44,07%; KHÔNG bền — (i) trượt cả hai phía, (iii) có đồng hồ. Mô hình hiện hành KHÔNG nhất quán luật 3c: giữ biên trên TB chu kỳ ở 35% trọng số (STRUCTURAL 0,20 + ADMIN-perm05 0,15), cho cả Tân Lập lẫn NNC nhìn xuyên.** Hiện hành: tâm 15.276 · P10 9.857 · P50 13.748 · P90 23.516 (sau CK 5 tỷ), TRONG vùng. **BẢN CHẶT-3C: tâm 13.010 (−14,8%) · P10 9.795 · P50 12.931 · P90 16.473, 63,3% dưới giá, nhãn TRONG vùng (không đổi), luật 4 không đạt (như cũ) — quy ước chờ Mike/user duyệt** (cùng quy ước NNC r2, cũng đang chờ).
Số: `5F/moat_sens_5f.py` trên lưới khoá `calc/grid_mvc_redo_r2.csv` (assert tái lập tâm REPORT_r2 15.276; chạy 2 lần trùng byte, md5 out `79fcc69f…`); BQ `tav2_bq.ticker_financial` truy vấn 07/11/2026 (`5F/bq_gpm_annual_rw.csv`).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới: LÀM MỚI** — `data/moat_tags.csv` không có dòng MVC; `kb/projects/mvc-dd-20261103.md` và REPORT r2–r8 không có mục 5F/moat ⇒ chưa từng audit. Làm theo `5F.md` từ dữ liệu đang có trong thư mục (BCTN 2025, BCTC, lưới) + BQ; không nghiên cứu mới.

**Loại hình DN:** tài nguyên/khai thác đá (mỏ Tân Lập) + mảng phụ (gạch, xăng dầu, BOT đã hết) + **holding 44,07% NNC** (r8: phần NNC 594,7/1.670,2 tỷ ≈ 36% giá trị tại tham số; Tân Lập 487,3; mỏ mới 389,7 sổ sách; BOT 93,7; gạch/xăng 41,5 — `dd_MVC_20261103/REPORT_r8_20261103.md` dòng 36).

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Cần giấy phép mỏ + bán kính vận chuyển. Rào cản là hành chính: chính MVC đang vào qua **đấu giá** (HĐQT giao TGĐ "tham gia đấu giá ít nhất 1 mỏ đá" — BCTN 2025 EN tr.13; 2 mỏ mới đã chi 438,4 tỷ, khai thác dự kiến 2028). Lợi nhuận siêu ngạch không tồn tại (dưới) ⇒ không có bằng chứng rào cản đang giữ được lợi nhuận. |
| Nhà cung cấp | 🔴 Cao | Nhà nước (giấy phép, thuế/phí tài nguyên, giá trần Sở XD). BOT Bình Thắng **đã chấm dứt 10/2024**, trả tuyến cho Nhà nước (BCTN 2025 tr.12) ⇒ dòng tiền phụ thuộc hợp đồng Nhà nước đã từng bị cắt. |
| Người mua | 🟡 TB | Cầu theo đầu tư công/hạ tầng — lổn nhổn. Phân phối qua bên liên quan Hoa Lư ICD (HĐQT duyệt — BCTN 2025 tr.13). Tỷ trọng khách lớn nhất: **cần kiểm chứng** (BCTC không tách). |
| Sản phẩm thay thế | 🟢 Thấp (đá) / 🔴 (gạch) | Đá dăm không có thay thế quy mô (định tính). Gạch nung bị thay thế/ế: **dừng sản xuất gạch Mỹ Phước 08/2025** (BCTN 2025 tr.12). |
| Cạnh tranh nội ngành | 🟡 TB | Peer nội địa cùng cụm đá Đông Nam Bộ: KSB, DHA, VLB (+NNC là công ty liên kết). **GPM năm trọng số DT** (BQ `GPM_P0` là giá trị MỘT QUÝ ⇒ Σ(DT×GPM)/ΣDT theo năm, 4 quý đủ): TB 2017–25 **MVC 16,2%** vs KSB 43,7 · DHA 29,9 · VLB 24,2 (2016–25) ⇒ **TB peer 32,6%, trung vị 29,9%**; NNC 34,7%. 9T/2026: **MVC 31,7%** vs DHA 37,2 · KSB 34,9 · VLB 31,9 · NNC 51,6 ⇒ MVC ở đáy nhóm. GPM MVC lẫn gạch/xăng/BOT (không có báo cáo bộ phận) ⇒ biên đá riêng **cần kiểm chứng**. KSB có mảng KCN (peer không thuần) — không loại, ghi khoảng ở §3. |
| **Lực thứ 6** | 🔴 | (a) **Hạn GP Tân Lập: cần kiểm chứng** (không tìm thấy trong BCTN/BCTC; mô hình để trục 2035/W/2045). (b) Đồng hồ đã điểm: BOT hết 10/2024. (c) Mỏ mới: GP khai thác chưa cấp (dự kiến 2028). (d) Nhìn xuyên NNC: Mũi Tàu GP tới 2043, truy thu chạm mỏ lõi (NNC addendum r2). (e) Asset-play: đất Mỹ Phước (gạch dừng) dự kiến nhà ở xã hội — chưa định giá, sổ sách. |

**moat_tier = NONE (vận hành trực tiếp) — NARROW/LOCATION chỉ qua NNC nhìn xuyên · moat_type = LOCATION · rủi ro số 1 = Nhà nước/giấy phép (hạn GP Tân Lập chưa kiểm chứng + GP 2 mỏ mới 1.500 tỷ chưa cấp, nợ ròng tăng trước doanh thu) — biên chu kỳ đá đang ở đỉnh (ROE 20,7% Q3/26 so 6–7% TB 2022–24).**

## 2. Moat trong mô hình
| Điều kiện moat BỀN | KQ | Bằng chứng (BQ `ticker_financial`, 07/11/2026; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ | **Phía trượt:** ROIC_Min5Y **1,4%**, ROIC5Y **4,5%**, ROIC10Y **3,8%**, ROIC_Min10Y **0,4%** — mọi cửa sổ < Ke. ROE (riêng, không thay ROIC) `ROE_Trailing` quý Q4: 2017 9,7 · 2018 13,3 · 2019 8,9 · 2020 6,5 · 2021 −3,6 · 2022 4,9 · 2023 6,1 · 2024 7,1 · 2025 13,6 · 2026Q3 20,7%; ROE5Y 6,9%, ROE_Min5Y 1,3% ⇒ < Ke 8/9 năm, chỉ chạm Ke ở đỉnh. **Phía thuận:** `ROIC_Trailing` (tự tính) 2022–26Q3 = 20–57% — mâu thuẫn ROE cùng năm (4,9–20,7%) và ROIC5Y ⇒ **nghi artifact định nghĩa**, không dùng; vẫn ghi ra. |
| (ii) cơ chế rào cản gọi tên được | ⚠️ một phần | LOCATION/giấy phép có tên, nhưng chưa từng chuyển thành lợi nhuận siêu ngạch ở MVC; ở NNC thì có (NARROW). |
| (iii) không có đồng hồ cắt hào | ❌ | Hạn GP Tân Lập chưa kiểm chứng (2035–2045 trong lưới), BOT đã hết, NNC Mũi Tàu 2043. |

⇒ **moat_durable = false ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ ngành.** Rà mô hình hiện hành (MVC r9 = `dd_MVC_20261103/r8/calc/model_r8.py` + `nnc_model_r6`, import bởi `calc/mvc_redo_r2.py`):
- **Đúng luật:** Tân Lập DCF hữu hạn 2027→hạn GP, không giá trị cuối kỳ (`model_r8.py:46`) ⇒ chặt hơn RONIC=Ke. Mỏ mới 438,4 tỷ, đất, cụm CN, mua NNC lên 51% = sổ sách/NPV0 ⇒ RONIC=Ke. Không có bội số premium (Gordon chỉ kiểm chéo).
- **Trục biên Tân Lập {25%, 30%, ~NNC 34,0%} đều 1/3** (`model_r8_out.txt:2`) ⇒ TB trục **29,7% ≈ trung vị peer 29,9%**, dưới TB peer 32,6% ⇒ nhất quán "biên về TB ngành" trong nhánh CYCLICAL/ADMIN.
- **VI PHẠM 3c:** STRUCTURAL **0,20** (giữ giá/biên đỉnh cả Tân Lập lẫn NNC nhìn xuyên, bất biến theo trục biên) + ADMIN-**perm05** **0,15** (= 1/3 của 0,45; kênh đếm trùng như NNC r2) ⇒ 35% trọng số giữ biên trên TB chu kỳ ngành ⇒ **không ghi 'nhất quán'**. Bản chặt bỏ cả hai, giữ trọng số nhánh ADMIN 0,45 (ramp/full ½–½) — giống hệt quy ước NNC r2.
- **Đối xứng:** bản chặt giữ nguyên mọi trục khác cả hai phía (chi phí, REL, SL, hạn GP 2035/W/2045, trần, biên TL); chỉ bỏ nhánh/mức. RONIC=Ke đã có sẵn ⇒ chênh **100% do biên**.
- **Còn mở (nhất quán với NNC r2, không sửa ở đây):** nhánh CYCLICAL của NNC nhìn xuyên hồi về GPM chu kỳ **riêng NNC 34,3%** (TB NNC, không phải TB ngành 29,9–32,6%) ⇒ bản chặt vẫn còn một phần biên-trên-ngành qua NNC; chưa đo độ lớn (cần chạy lại engine NNC).
- Pháp lý/sở hữu chéo: chỉ WARNING; không dùng ép biên. Không đếm trùng với khoản nào trong REPORT_r2 §4 (không có giảm trừ pháp lý trong base).
- Quy ước năm 1/chiết khấu: addendum KHÔNG chiết khấu lại, chỉ tái trọng số lưới khoá ⇒ giữ nguyên quy ước của engine.

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 13.800, 04/11/2026)
| Moat giả định | Ánh xạ trên lưới khoá | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|---|
| WIDE | 100% STRUCTURAL | 21.721 | 10.308 | 22.265 | 32.320 | 23,5% | TRONG |
| Hiện hành (REPORT_r2) | Bobby 0,20/0,45/0,35, ADMIN 3 mức | **15.276** | 9.857 | 13.748 | 23.516 | 50,6% | TRONG |
| Chỉ bỏ perm05, giữ STRUCTURAL | KB | 14.752 | 9.857 | 13.384 | 22.282 | 55,3% | TRONG |
| **BẢN CHẶT-3C** *(chờ duyệt)* | KB: bỏ STRUCT + perm05; ADMIN 0,45 ramp/full | **13.010** | 9.795 | 12.931 | 16.473 | 63,3% | TRONG |
| — chuẩn hoá toàn cục | | 12.982 | 9.795 | 12.914 | 16.401 | 63,9% | TRONG |
| — biên TL = trung vị peer (30%) | | 13.076 | 9.791 | 12.992 | 16.459 | 58,6% | TRONG |
| — biên TL ≈ TB peer ({30%, ~NNC}) | | 13.271 | 9.856 | 13.200 | 16.857 | 57,5% | TRONG |
| — biên TL 25% (sàn) | | 12.489 | 9.750 | 12.454 | 15.540 | 74,9% | TRONG |
| NONE | 100% CYCLICAL | 12.855 | 9.790 | 12.781 | 16.164 | 66,7% | TRONG |

Cỡ khác (bản CHẶT-3C): 1 tỷ tâm 13.678 · P10 10.298 · P90 17.318 TRONG; 40 triệu P10 10.623 TRONG; 10 triệu TRONG. Luật 4 (giá ≤ 0,85×tâm) **không đạt ở mọi biến thể trừ WIDE**.
Đọc: hiện hành → CHẶT = **−2.266 tâm (−14,8%)**, P90 −7.043; tách tuần tự: bỏ perm05 −524, bỏ STRUCTURAL −1.742. P10 gần bất động (9,75–10,3k). Theo cách chọn peer (trung vị ↔ TB, có/không KSB) tâm chặt dao động **12.489–13.271 (≈ ±3%)**. Giá 13.800 > tâm chặt (+6%) nhưng < P90 16.473 ⇒ nhãn **không nhạy** theo moat/peer/cỡ.

## 4. Thay đổi so với báo cáo hiện hành
Mô hình/REPORT_r2/SUMMARY.json **giữ nguyên, không sửa; không ghi `dd_price_zones`**. Theo luật 3c đúng nghĩa (không bền ⇒ RONIC=Ke + biên về TB chu kỳ ngành), headline là **BẢN CHẶT-3C: tâm 15.276 → 13.010 (−14,8%), P10 9.857 → 9.795, P50 13.748 → 12.931, P90 23.516 → 16.473, % dưới giá 50,6% → 63,3%; nhãn TRONG → TRONG (không đổi); luật 4 không đạt → không đạt** — chênh 100% do biên (RONIC=Ke đã có). **Quy ước chờ Mike/user duyệt** (cùng quyết định NNC r2). Hệ quả đáng chú ý: vùng giá hẹp lại mạnh ở phía trên (P90 −30%) — phần "đuôi tăng" của REPORT_r2 gần như toàn bộ đến từ nhánh STRUCTURAL.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa — chỉ đề xuất)
entry = M (cấu trúc NGÀNH đá xây dựng, giống dòng NNC; `moat_5f.py:33`); moat_upgrade = N (không có chủ ý nâng).
```
MVC,NONE,LOCATION,M,"Own ops never earned above Ke: ROIC5Y 4.5%, ROIC10Y 3.8%, ROIC_Min5Y 1.4%, ROE_Trailing <13.5% in 8/9 yrs 2017-25 (2026Q3 20.7% = cycle peak); ROIC_Trailing 20-57% contradicts ROE = artifact suspect; GPM annual rev-weighted 2017-25 avg 16.2% vs peer median 29.9% (mixed brick/fuel, no segment data); value ~36% = 44.07% NNC stake (NARROW/LOCATION look-through, Mui Tau license 2043); Tan Lap license end unverified; BOT ended 10/2024; brick halted 08/2025; 2 new quarries (1,500bn plan) license pending 2028 with rising net debt; related-party cross-holding with NNC; very thin liquidity",2026-11-07,5f_full_dd_redo,N
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý/sở hữu chéo: chỉ WARNING (luật 27/09). Chưa qua fundamental-skeptic (Mike chạy).*
