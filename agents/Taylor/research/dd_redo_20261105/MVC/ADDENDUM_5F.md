> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (tâm 15.276 theo báo cáo gốc)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# MVC — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (r3, 07/11/2026, job Taylor_20261107_124458)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. r2 = `ADDENDUM_5F_r2.md` (job Taylor_20261107_123139). **Kết luận r3: moat đề xuất NARROW (không bền)/LOCATION (r2 ghi NONE — rút, xem §1); KHÔNG bền — (iii) có đồng hồ là đủ một mình (như NNC), (i) bằng chứng ROIC mâu thuẫn. Định giá KHÔNG phụ thuộc NONE/NARROW. Mô hình hiện hành KHÔNG nhất quán luật 3c: giữ biên trên TB chu kỳ ở 35% trọng số (STRUCTURAL 0,20 + ADMIN-perm05 0,15), cho cả Tân Lập lẫn NNC nhìn xuyên.** Hiện hành: tâm 15.276 · P10 9.857 · P50 13.748 · P90 23.516 (sau CK 5 tỷ), TRONG vùng. **BẢN CHẶT-3C: tâm 13.010 (−14,8%) · P10 9.795 · P50 12.931 · P90 16.473, 63,3% dưới giá, nhãn TRONG (không đổi), luật 4 không đạt (như cũ) — quy ước chờ Mike/user duyệt** (cùng quy ước NNC r2). Số định giá **không đổi so với r2**.
Số: `5F/moat_sens_5f.py` trên lưới khoá `calc/grid_mvc_redo_r2.csv` (assert tái lập tâm REPORT_r2 15.276; chạy 2 lần trùng byte, md5 out `79fcc69f…` = r2); GPM/ROIC `5F/gpm_q4_r3.py` trên `5F/bq_q_r3.csv` (bq `tav2_bq.ticker_financial` 07/11/2026; 2 lần trùng byte `96007d3b…`); V_NNC `5F/vnnc_check_5f.py` (2 lần trùng byte `29b58b2b…`).

**Đính chính GPM (Mike 07/11 19:50, ưu tiên hơn mọi đính chính trước):** BQ `GPM_P0` là **TTM** (4 quý trượt), không phải quý. r2 coi là "giá trị MỘT QUÝ" rồi tính Σ(DT×GPM)/ΣDT ⇒ **SAI, rút**. r3: GPM năm = `GPM_P0` dòng **Q4** (dùng thẳng); hiện tại = `GPM_P0` 2026Q3 (TTM Q4/25–Q3/26). Ở mô hình NNC nhìn xuyên: 0,494 = TTM Q4/25 = GPM năm 2025; list GPM_NNC theo Q4 = GPM năm; GPM_NOW 0,533 = TTM Q3/26 ⇒ **đúng, không phải bug** (bỏ mọi cảnh báo "lỗi quý/TTM" / "bản chặt bị thấp" từng nêu về `model_r6.py:31-33`/`model_r4.py:46`).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới: LÀM MỚI** — `data/moat_tags.csv` không có dòng MVC; `kb/projects/mvc-dd-20261103.md` và REPORT r2–r8 không có mục 5F ⇒ chưa từng audit. Dữ liệu đang có (BCTN 2025, BCTC, lưới) + BQ; không nghiên cứu mới.

**Loại hình DN:** tài nguyên/khai thác đá (mỏ Tân Lập) + mảng phụ (gạch, xăng dầu, BOT đã hết) + **holding NNC 44,07%** (9.659.170 cp tại Q3/26 [HN-Q3 V.12]). **Đối soát:** BCTN 2025 EN ghi **43,55%** = 9.545.270 cp tại 31/12/2025 (`dd_MVC_20261103/txt/EN_AnnualReport_2025.txt:421-422`); chênh = mua thêm 113.900 cp (6,01 tỷ) trong 9T/26 [LCTT mã 25] (`dd_MVC_20261103/REPORT_r2_20261103.md:57`) ⇒ hai số đều đúng ở hai mốc, mô hình dùng mốc mới. Khác: NHC 30,04%, MCC 29,9% (txt:417-424). r8: phần NNC 594,7/1.670,2 tỷ ≈ 36% giá trị tại tham số (`REPORT_r8_20261103.md:36`).

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Giấy phép mỏ + bán kính vận chuyển; hành chính: MVC đang vào qua **đấu giá** (BCTN 2025 EN tr.13; 2 mỏ mới đã chi 438,4 tỷ, khai thác dự kiến 2028). |
| Nhà cung cấp | 🔴 Cao | Nhà nước (giấy phép, thuế/phí tài nguyên, giá trần Sở XD). BOT Bình Thắng **đã chấm dứt 10/2024** (BCTN 2025 tr.12). |
| Người mua | 🟡 TB | Cầu theo đầu tư công/hạ tầng. Phân phối qua **Hoa Lư ICD — công ty con 100% vốn MVC** (EN AR txt:425; r2 gọi là "bên liên quan" ⇒ sửa: nội bộ tập đoàn, không phải bên ngoài). Tập trung khách lớn nhất: **cần kiểm chứng**. |
| Sản phẩm thay thế | 🟢 Thấp (đá) / 🔴 (gạch) | Đá dăm không có thay thế quy mô (định tính). Gạch: **dừng SX Mỹ Phước 08/2025** (BCTN 2025 tr.12). |
| Cạnh tranh nội ngành | 🟡 TB | Peer nội địa cùng cụm đá ĐNB: KSB, DHA, VLB (NNC = công ty liên kết). **GPM năm (Q4 `GPM_P0`), cửa sổ CHUNG 2017–25 cho mọi mã (9 năm/mã; r2 lệch cửa sổ MVC 2017–25 / peer 2016–25 / NNC 2012–25 — đã thống nhất):** MVC **16,1%** vs KSB 43,6 · DHA 29,1 · VLB 24,5 ⇒ **TB peer 32,4%, trung vị 29,1%** (bỏ KSB có mảng KCN: 26,8%); NNC 34,9%. **Hiện tại (TTM Q3/26):** MVC **35,2%** vs DHA 37,2 · VLB 33,6 · KSB 33,1 · NNC 53,3 (TB peer 34,6%, trung vị 33,6%) ⇒ MVC **trong nhóm, trên KSB/VLB** — r2 "MVC ở đáy nhóm" (dựa số 9T sai cách tính) **rút**. GPM MVC lẫn gạch/xăng/BOT (không báo cáo bộ phận) ⇒ TB lịch sử bị kéo thấp bởi mảng phụ; biên đá riêng Tân Lập **cần kiểm chứng**. |
| **Lực thứ 6** | 🔴 | (a) **Hạn GP Tân Lập: cần kiểm chứng** (mô hình trục 2035/W/2045). (b) BOT hết 10/2024. (c) GP 2 mỏ mới chưa cấp (dự kiến 2028). (d) NNC nhìn xuyên: Mũi Tàu GP tới 2043, truy thu chạm mỏ lõi (NNC addendum r2). (e) Đất Mỹ Phước — chưa định giá, sổ sách. |

**moat_tier đề xuất = NARROW (không bền) · moat_type = LOCATION · rủi ro số 1 = Nhà nước/giấy phép (hạn GP Tân Lập chưa kiểm chứng + GP 2 mỏ mới 1.500 tỷ chưa cấp, nợ ròng tăng trước doanh thu).**
Vì sao rút NONE (r2): câu "own ops never earned above Ke" **SAI** — `ROIC_Trailing_v1` (số báo cáo) > Ke 16/16 quý liên tục 2022Q4–2026Q3, ROE_Trailing ≥ Ke ở 2025Q4 (13,6%) và 2026 (20,7% Q3); GPM TTM hiện ngang peer; mọi peer cụm đá có tag (NNC, DHA, VLB) đều NARROW/LOCATION; và "NONE + LOCATION" tự mâu thuẫn (type gọi tên rào cản mà tier nói không có). Phương án thay thế: giữ NONE kèm "cần kiểm chứng biên đá riêng Tân Lập". **Hệ quả `moat_5f.py`:** NONE ⇒ `NONE_CAP=3` (trần L4_moat) + `NONE_DUR_FACTOR −0,50` (giảm nửa điểm buy-fear, `moat_5f.py:45-47,92-94`); NARROW ⇒ trung tính ×1,0 (`:95`). Chỉ ảnh hưởng chấm điểm fear-buy, **không** ảnh hưởng định giá dưới đây.

## 2. Moat trong mô hình
| Điều kiện moat BỀN | KQ | Bằng chứng (BQ `ticker_financial` 07/11/2026; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ⚠️ mâu thuẫn | **Phía thuận:** `ROIC_Trailing_v1` (báo cáo) Q4: 2021 5,3 · **2022 15,3 · 2023 19,4 · 2024 18,1 · 2025 23,5 · 2026Q3 38,4%** — > Ke **16/16 quý** từ 2022Q4; `ROIC_Trailing` (tự tính) 2022–26Q3 20–57%. **Phía trượt:** ROIC5Y **4,53%**, ROIC_Min5Y **1,43%**, ROIC10Y 3,8%, ROIC_Min10Y 0,4%. ROIC5Y mâu thuẫn **cả hai** chuỗi quý (TB Q4 2021–25: v1 **16,3%**, tự tính **23,4%**) ⇒ **'nghi artifact' gắn ĐỐI XỨNG**: hoặc ROIC5Y/Min5Y sai, hoặc chuỗi trailing sai — chưa phân xử được. ROE (riêng): `ROE_Trailing` Q4 2017 9,7 · 2018 13,3 · 2019 8,9 · 2020 6,5 · 2021 −3,6 · 2022 4,9 · 2023 6,1 · 2024 7,1 · 2025 13,6 · 2026Q3 20,7% ⇒ **< Ke 8/9 năm 2017–25**, ≥ Ke 2025–26. ROE **không sạch làm trọng tài** ở holding: vốn chủ gồm tài sản phi vận hành (NNC 43–44%, NHC 30%, CIP mỏ mới 438 tỷ) ⇒ ROE kéo thấp ROIC vận hành. ⇒ **"ROIC các nguồn mâu thuẫn; ROE < Ke 8/9 năm"** (r2 "mọi cửa sổ < Ke" — rút). |
| (ii) cơ chế rào cản gọi tên được | ⚠️ một phần | LOCATION/giấy phép có tên; ở NNC đã chuyển thành siêu ngạch (NARROW); ở MVC chỉ có bằng chứng từ 2022 (một chu kỳ). |
| (iii) không có đồng hồ cắt hào | ❌ | Hạn GP Tân Lập chưa kiểm chứng (2035–2045 trong lưới), BOT đã hết, NNC Mũi Tàu 2043. |

⇒ **moat_durable = false — ĐỦ nhờ (iii) một mình (như NNC)**, không cần (i) ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ ngành. Định giá **không phụ thuộc** tier NONE hay NARROW (cả hai đều không thưởng). Rà mô hình hiện hành (MVC r9 = `dd_MVC_20261103/r8/calc/model_r8.py` + `nnc_model_r6`, import bởi `calc/mvc_redo_r2.py`):
- **Đúng luật:** Tân Lập DCF hữu hạn 2027→hạn GP, không giá trị cuối kỳ (`model_r8.py:46`). Mỏ mới 438,4 tỷ, đất, cụm CN, mua NNC lên 51% = sổ sách/NPV0 ⇒ RONIC=Ke. Không bội số premium.
- **Trục biên Tân Lập {25%, 30%, ~NNC 34,0%} đều 1/3** (`model_r8_out.txt:2`) ⇒ TB trục **29,7% ≈ trung vị peer 29,1%** (r3), dưới TB peer 32,4% ⇒ ánh xạ trục **không đổi** so với r2 (trung vị ~0,30; TB ~{0,30; ~NNC}).
- **VI PHẠM 3c:** STRUCTURAL **0,20** + ADMIN-**perm05** **0,15** ⇒ 35% trọng số giữ biên trên TB chu kỳ ⇒ không ghi 'nhất quán'. Bản chặt bỏ cả hai, giữ nhánh ADMIN 0,45 (ramp/full ½–½) — giống quy ước NNC r2. RONIC=Ke đã có ⇒ chênh **100% do biên**. Đối xứng: mọi trục khác giữ nguyên cả hai phía.
- **Nhất quán với NNC r2 (V_NNC):** V_NNC được giải ĐỒNG THỜI trong từng nhánh/ADMIN (`model_r8.py:3`), nên bản CHẶT-3C MVC bỏ STRUCTURAL+perm05 **cho cả NNC nhìn xuyên** — cùng quy ước với CHẶT-3C NNC **48.181** (sau CK NNC; 49.997 trước CK). Đo tại tham số trung tâm: V_NNC ngầm trong CHẶT-3C MVC = **53.695** (hiện hành 62.923) ⇒ cao hơn NNC r2 trước CK **+7,4%**, nhưng phần lớn là chênh tham số-trung-tâm vs kỳ vọng lưới (cột hiện hành cùng phép so: 62.923 vs 59.760 = +5,3%). Nếu kéo V_NNC về đúng 49.997: tâm MVC chặt ≈ **−100 đến −360 đ/cp** (`ước lượng`, tuyến tính độ dốc +966 đ/cp mỗi +10.000 V_NNC, `model_r8_out.txt:78`) ⇒ ~12.650–12.910; nhãn TRONG không đổi (P90 ≫ giá). Không chạy lại lưới.
- **Còn mở:** nhánh CYCLICAL của NNC hồi về GPM chu kỳ **riêng NNC** (34,3% engine; TB Q4 2017–25 NNC 34,9%) > TB ngành 29,1–32,4% ⇒ còn một phần biên-trên-ngành qua NNC; chưa đo (cần chạy lại engine NNC).
- Pháp lý/sở hữu chéo: chỉ WARNING; không đếm trùng (REPORT_r2 §4 không có giảm trừ pháp lý trong base). Quy ước năm 1/chiết khấu: không chiết khấu lại, chỉ tái trọng số lưới khoá.

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 13.800, 04/11/2026) — không đổi so với r2
| Moat giả định | Ánh xạ trên lưới khoá | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|---|
| WIDE | 100% STRUCTURAL | 21.721 | 10.308 | 22.265 | 32.320 | 23,5% | TRONG |
| Hiện hành (REPORT_r2) | Bobby 0,20/0,45/0,35, ADMIN 3 mức | **15.276** | 9.857 | 13.748 | 23.516 | 50,6% | TRONG |
| Chỉ bỏ perm05, giữ STRUCTURAL | KB | 14.752 | 9.857 | 13.384 | 22.282 | 55,3% | TRONG |
| **BẢN CHẶT-3C** *(chờ duyệt)* | KB: bỏ STRUCT + perm05; ADMIN 0,45 ramp/full | **13.010** | 9.795 | 12.931 | 16.473 | 63,3% | TRONG |
| — chuẩn hoá toàn cục | | 12.982 | 9.795 | 12.914 | 16.401 | 63,9% | TRONG |
| — biên TL = trung vị peer (30%) | | 13.076 | 9.791 | 12.992 | 16.459 | 58,6% | TRONG |
| — biên TL ≈ TB peer ({30%, ~NNC}) | | 13.271 | 9.856 | 13.200 | 16.857 | 57,5% | TRONG |
| — biên TL 25% (sàn; ≈ TB peer bỏ KSB 26,8%) | | 12.489 | 9.750 | 12.454 | 15.540 | 74,9% | TRONG |
| NONE (= cũng là ánh xạ "NARROW không bền") | 100% CYCLICAL | 12.855 | 9.790 | 12.781 | 16.164 | 66,7% | TRONG |

Cỡ khác (CHẶT-3C): 1 tỷ tâm 13.678 · P10 10.298 · P90 17.318 TRONG; 40 triệu P10 10.623 TRONG; 10 triệu TRONG. Luật 4 (giá ≤ 0,85×tâm) **không đạt ở mọi biến thể trừ WIDE**.
Đọc: hiện hành → CHẶT = **−2.266 tâm (−14,8%)**, P90 −7.043; tách tuần tự: bỏ perm05 −524, bỏ STRUCTURAL −1.742. Theo cách chọn peer (trung vị ↔ TB, có/không KSB) tâm chặt **12.489–13.271 (≈ ±3%)**; cộng điều chỉnh V_NNC (`ước lượng` −100…−360) vẫn trong TRONG. Nhãn **không nhạy** theo moat/peer/cỡ.

## 4. Thay đổi so với báo cáo hiện hành (và so với r2)
Mô hình/REPORT_r2/SUMMARY.json **giữ nguyên, không sửa; không ghi `dd_price_zones`**. Headline luật 3c: **BẢN CHẶT-3C: tâm 15.276 → 13.010 (−14,8%), P10 9.857 → 9.795, P50 13.748 → 12.931, P90 23.516 → 16.473, % dưới giá 50,6% → 63,3%; nhãn TRONG → TRONG; luật 4 không đạt → không đạt** — chênh 100% do biên. **Quy ước chờ Mike/user duyệt** (cùng quyết định NNC r2). **So với r2:** số định giá KHÔNG đổi (ánh xạ trục biên giữ nguyên dưới GPM tính lại); đổi văn bản: tier NONE → NARROW (không bền), (i) "mọi cửa sổ < Ke" → "ROIC các nguồn mâu thuẫn", GPM peer tính lại từ Q4 (MVC 16,2→16,1; TB peer 32,6→32,4; trung vị 29,9→29,1; hiện tại MVC ngang peer, không còn "đáy nhóm"), Hoa Lư ICD = công ty con, đối soát 44,07%/43,55%, thêm kiểm V_NNC. Kết luận durable=false **không đổi** (đứng trên (iii)).

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa — chỉ đề xuất)
entry = M (cấu trúc NGÀNH đá xây dựng, như NNC/DHA/VLB; `moat_5f.py:33`); moat_upgrade = N.
```
MVC,NARROW,LOCATION,M,"Stone quarry (Tan Lap) + 44.07% NNC holding (~36% of value, NARROW/LOCATION look-through); NOT durable: (iii) alone suffices - Tan Lap license end unverified, BOT ended 10/2024, NNC Mui Tau license 2043, 2 new quarries (1,500bn plan) license pending 2028 with rising net debt; (i) ROIC sources contradict: ROIC_Trailing_v1 >13.5% Ke 16/16 qtrs 2022Q4-2026Q3 (15.3-38.4%) vs ROIC5Y 4.5%/ROIC_Min5Y 1.4% = artifact suspect both sides; ROE_Trailing <Ke 8/9 yrs 2017-25 but holding ROE diluted by non-op assets (NNC/NHC/CIP 438bn); GPM annual (Q4 TTM) 2017-25 avg 16.1% vs peer median 29.1% (mixed brick/fuel/BOT, no segments) but TTM Q3/26 35.2% in line with peers; brick halted 08/2025; related-party cross-holding with NNC; very thin liquidity",2026-11-07,5f_full_dd_redo,N
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm backtest. Pháp lý/sở hữu chéo: chỉ WARNING (luật 27/09). Chưa qua fundamental-skeptic (Mike chạy).*
