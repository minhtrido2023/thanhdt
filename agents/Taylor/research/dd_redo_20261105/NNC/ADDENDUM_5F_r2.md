# NNC — ADDENDUM bước 3c (r2): 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_122441; bản cũ = `ADDENDUM_5F_r1.md`)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận r2: moat NARROW/LOCATION (tái dùng tag 05/06/2026), KHÔNG bền. Mô hình hiện hành KHÔNG ĐƯỢC ghi là 'nhất quán với luật 3c': nó giữ biên trên TB chu kỳ tới 2043 ở 35% trọng số (STRUCTURAL 0,20 + ADMIN-perm05 0,15).** Hiện hành: tâm 57.589 · P10 30.219 · P50 52.916 · P90 93.649 sau CK, TRONG vùng. **BẢN CHẶT-3C (đúng nghĩa luật 3c): tâm 48.181 · P10 29.431 · P50 48.891 · P90 64.272, 43,7% dưới giá, luật 4 KHÔNG đạt, nhãn TRONG vùng — quy ước chờ Mike/user duyệt.** Số độ nhạy lấy từ lưới khoá `calc/grid_nnc_redo_r2.csv` qua `5F/moat_sens_5f_r2.py` (cột hiện hành tái lập đúng REPORT_r2; chạy 2 lần trùng byte, md5 out `9d10b881…`; r1 = `moat_sens_5f.py`).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới:** TÁI DÙNG. `data/moat_tags.csv` dòng NNC: NARROW · LOCATION · asof **2026-06-05** · src `5f_validated_compet` (5 tháng < 12 tháng ⇒ theo luật tần suất 06/11 chỉ kiểm nhanh). Không nghiên cứu mới; số kiểm nhanh lấy từ BQ `tav2_bq.ticker_financial` (truy vấn 07/11/2026) và dữ kiện đã có trong REPORT_r2 / `dd_NNC_20261030/`.

**Loại hình DN:** tài nguyên/khai thác đá xây dựng — hào = vị trí (bán kính vận chuyển) + giấy phép; rủi ro lõi = vòng đời giấy phép/trữ lượng + Nhà nước.

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Cần giấy phép mỏ (Mũi Tàu 51,5 ha, 1,0 tr m³ nguyên khối/năm, GP tới 2043 — BCTN25 tr.3). Nhưng mỏ mới trong cụm được đấu giá (VĐ4/Đồng Nai tới 06/2027 — REPORT_r2 §8) ⇒ rào cản là hành chính, không vĩnh viễn. Bán kính vận chuyển: **cần kiểm chứng** (không có số chi phí/km trong thư mục). |
| Nhà cung cấp | 🔴 Cao | Nhà nước = nhà cung cấp quyền lực nhất: tổng truy thu Núi Nhỏ ≈**42 tỷ ≈1.900 đ/cp**; truy thu đã chạm mỏ lõi Mũi Tàu (dự phòng 0,84 tỷ, CQKTKS 1,735 tỷ — cờ E12 chưa đóng). Đầu vào khác (điện, dầu, nổ mìn) phân tán. |
| Người mua | 🟡 TB | Cầu theo dự án hạ tầng (Long Thành, VĐ4) — lổn nhổn. Bên liên quan NHC chiếm **61% phải thu**; DT dịch vụ 2025 18,92 tỷ ≈ DT từ NHC 18,41 tỷ (REPORT_r2 §7). Khách lẻ ngoài NHC: **cần kiểm chứng** cơ cấu. |
| Sản phẩm thay thế | 🟢 Thấp | Đá dăm không có vật thay thế quy mô cho bê tông/nền đường (định tính, không có số). |
| Cạnh tranh nội ngành | 🟡 TB | Cụm mỏ Đông Nam Bộ: DHA, VLB, KSB. GPM TB 2012–25: **NNC 34,1%** vs KSB 40,4% · DHA 26,0% · VLB 24,7% (`dd_NNC_20261030/r3/calc/sector_gpm_roe.csv`) ⇒ giữa nhóm. Chu kỳ gần: GPM **TTM 51%** (Q4/25–Q3/26, trọng số doanh thu; quý Q3/26 riêng 53%) = đỉnh chu kỳ (2022: 21%). Cùng cách tính (BQ `GPM_P0` là giá trị MỘT QUÝ, TTM = trọng số doanh thu 4 quý), 9T/2026: **NNC 51,6%** vs DHA 37,2 · KSB 34,9 · VLB 31,9 (peer nội địa cùng cụm đá Đông Nam Bộ, không loại peer nào) ⇒ biên hiện tại của NNC cao hơn peer ~14–20pp. Đây là dữ kiện biên, **không** dùng để khẳng định 'trạng thái ngành chứ không phải lợi thế riêng' (đã bỏ lập luận đó ở r1); phần chênh có thể do cơ cấu sản phẩm/mỏ/giá chu kỳ — **cần kiểm chứng**, không đủ để gọi là hào bền khi (i) và (iii) trượt. |
| **Lực thứ 6** | 🔴 | (a) **Đồng hồ giấy phép**: Mũi Tàu hết 2043 (~17 năm); đã từng xảy ra — Núi Nhỏ hết GP 2019 ⇒ ROE rơi từ 38–49% (2012–20) xuống **10–13%** (2021–23). (b) Quy định/truy thu (như trên). (c) MVC được uỷ quyền lên 51% (giao dịch bên liên quan). (d) Có thể gia hạn hào: CBTT 17/04/2026 trúng đấu giá quyền khai thác (UBND TP.HCM) — **chưa đối chiếu** mỏ/giá/hạn. |

**Kiểm nhanh "có gì đổi hào kể từ 05/06/2026":** không đổi tier. Mới/được làm rõ: cờ truy thu chạm Mũi Tàu (E12, 31/10) — nghiêng xấu; GPM lên TTM 51% (quý Q3/26 53%) là chu kỳ giá + chưa kiểm chứng nguồn chênh peer, không phải bằng chứng hào; CBTT đấu giá 17/04 (có trước asof nhưng tag không nhắc) — có thể kéo dài đồng hồ, chưa xác minh.

**moat_tier = NARROW · moat_type = LOCATION · rủi ro số 1 = đồng hồ giấy phép/Nhà nước trên mỏ đơn lẻ Mũi Tàu (~94% DT, GP tới 2043, truy thu đã chạm mỏ lõi).**

## 2. Moat trong mô hình
| Điều kiện moat BỀN | Kết quả | Bằng chứng (BQ `ticker_financial`, 07/11/2026) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ (trượt) | **Hai phía:** ROIC_Min5Y **1,3%** < Ke 13,5% (trượt) — NHƯNG đây là print FY2022 đơn lẻ, mâu thuẫn ROE 11,9% cùng năm ⇒ **nghi artifact vendor**; ROIC5Y **16,5%** (> Ke) và ROIC10Y **29,6%** (ROIC_Min10Y cũng 1,3%) ủng hộ phía siêu ngạch nhiều năm. ROE (riêng, không thay ROIC): Trailing 2021/22/23/24 = 13,0/11,9/10,1/15,5%, 2026Q3 35,9%. Kết luận: (i) vẫn trượt theo chuẩn Min5Y nhưng yếu hơn r1 nói; **(iii) một mình đủ để loại 'bền'**. |
| (ii) cơ chế rào cản gọi tên được | ✅ | Giấy phép + bán kính vận chuyển (LOCATION). |
| (iii) không có đồng hồ cắt hào | ❌ | GP 2043; tiền lệ Núi Nhỏ 2019; truy thu chạm mỏ lõi. |

⇒ **moat_durable = false (đủ bởi (iii)) ⇒ luật 3c: RONIC=Ke VÀ biên về TB chu kỳ ngành.** Rà soát mô hình hiện hành (`dd_NNC_20261030/r4–r6/calc`, import bởi `calc/nnc_redo_r2.py`) — **r1 ghi 'nhất quán' là SAI; kết quả rà:**
- **Phần đã đúng luật —** không có giá trị cuối kỳ: DCF hữu hạn 2027–2043 (`r3/calc/model_r3.py:90`), sau GP = 0 ⇒ chặt hơn cả RONIC = Ke; khớp với đồng hồ (iii).
- **Đầu tư mới** (CIP Tam Lập 1 khu II 83,5 tỷ) ở sổ sách, NPV 0 ⇒ RONIC = Ke. Nhất quán.
- **Biên:** CYCLICAL hồi về GPM chu kỳ **34,3%** (TB NNC 2012–25 + chênh đá; `r4/calc/model_r4_out.txt:5`) — đúng chuẩn "NARROW ⇒ biên về TB chu kỳ". ADMIN_GATED hồi biên có trễ 1 năm (nghẽn hành chính tạm thời).
- **VI PHẠM 3c — hai kênh giữ biên trên TB chu kỳ tới 2043, tổng 35% trọng số:** (a) STRUCTURAL **0,20** (biên đỉnh giữ tới 2043); (b) ADMIN-**perm05** **0,15** (ADMIN có 3 mức perm05/ramp/full, mỗi 1/3 của 0,45; perm05 = stress 0,5 vĩnh viễn, ĐẾM TRÙNG KÊNH — docstring `r5` tự gọi vậy). Kênh (a) có cơ sở Bobby (cung ngành, đọc mù) nhưng trong khung 3c vẫn là biên NNC trên TB chu kỳ ngành kéo dài ⇒ **không được gọi là 'nhất quán'/'không premium'**. Bản chặt bên dưới đưa cả hai về TB chu kỳ.
- **Đối xứng lưới:** ở bản chặt, K {0,87/0,97/1,07}, SL, trần chu kỳ, thuê Núi Nhỏ giữ nguyên cả hai phía (chỉ bỏ nhánh/mức, không cắt một chiều); RONIC = Ke đã sẵn (không TV, CIP NPV 0) nên chênh còn lại **100% do biên**, RONIC không đóng góp.
- **Vụ án/truy thu:** chỉ WARNING; không dùng ép biên trong bản chặt (neo bằng (iii) + dữ liệu chu kỳ), không trùng giảm trừ pháp lý đã có.
- Không dùng bội số premium nào (Gordon chỉ để kiểm chéo, ROE chuẩn hoá — REPORT_r2 §6).

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 46.900)
Nhãn: **TRONG vùng ở mọi biến thể** (P10 < 46.900 < P90). Biến thể KB = giữ nguyên trọng số NHÁNH ADMIN 0,45, chia lại ramp/full (0,225 mỗi mức); biến thể 'toàn cục' = chuẩn hoá lại mọi trọng số.

| Moat giả định | Ánh xạ trên lưới khoá | Tâm | P10 | P50 | P90 | % dưới giá | Luật 4 (≤0,85×tâm) |
|---|---|---|---|---|---|---|---|
| WIDE | 100% STRUCTURAL | 84.655 | 31.729 | 89.665 | 127.891 | 25,0% | đạt |
| NARROW — hiện hành | Bobby 0,20/0,45/0,35, ADMIN 3 mức mỗi 1/3 (= REPORT_r2) | **57.589** | 30.219 | 52.916 | 93.649 | 37,5% | đạt |
| Chỉ bỏ perm05, giữ STRUCTURAL | KB (ramp/full) | 55.476 | 30.015 | 51.012 | 89.665 | 39,9% | đạt (dư 254đ) |
| **BẢN CHẶT-3C** (bỏ STRUCTURAL & perm05) *— chờ duyệt quy ước* | KB: ADMIN ramp/full 0,225+0,225 (nhánh 0,45) + CYC 0,35, chuẩn hoá 0,5625/0,4375 | **48.181 (−16,3%)** | 29.431 | 48.891 | 64.272 | 43,7% | **không** |
| (toàn cục, tham chiếu) bỏ STRUCT & perm05 | chuẩn hoá lại toàn lưới | 48.078 | 29.431 | 48.801 | 64.196 | 44,0% | không |
| (r1 'NARROW chặt' — chỉ bỏ STRUCTURAL, giữ perm05) | ADMIN 3 mức | 50.822 | 30.015 | 50.616 | 69.773 | 40,6% | không |
| NONE | 100% CYCLICAL | 47.608 (−17,3%) | 29.431 | 48.521 | 63.576 | 45,4% | không |

Đọc: chênh hiện hành → CHẶT-3C = **−9.408 (−16,3%) tâm**, P90 −29.377; **toàn bộ do biên** (RONIC=Ke đã có). Tách: bỏ STRUCTURAL (từ bản KB bỏ perm05) ≈ −7.295; bỏ perm05 (giữ STRUCTURAL) ≈ −2.113 — tách tuần tự (57.589 → 55.476 → 48.181) nên cộng đúng −9.408. P10 gần như bất động theo moat (29,4–31,7k, neo bởi tiền ròng + sàn chi phí). CHẶT-3C ≈ NONE (chênh 573 ở tâm) ⇒ phần chênh còn lại là ADMIN-ramp (trễ 1 năm) trong 0,45. NONE 'theo peer' (biên về TB DHA/VLB) **chưa đo**, sẽ thấp hơn. Độ nhạy theo cách chọn peer: peer KSB/DHA/VLB đều nội địa, không loại peer nào; chưa chạy NONE theo peer nên chưa có khoảng.

## 4. Thay đổi so với báo cáo hiện hành
**r1 ghi 'không đổi/nhất quán' — rút lại.** Mô hình hiện hành (REPORT_r2) giữ nguyên, KHÔNG sửa REPORT/SUMMARY cũ, KHÔNG ghi `dd_price_zones`. Nhưng theo luật 3c đúng nghĩa (NARROW không bền ⇒ RONIC=Ke + biên về TB chu kỳ), headline là **BẢN CHẶT-3C: tâm 57.589 → 48.181 (−16,3%), P10 30.219 → 29.431, P50 52.916 → 48.891, P90 93.649 → 64.272, % dưới giá 37,5% → 43,7%; luật 4 đạt → KHÔNG đạt; nhãn TRONG vùng → TRONG vùng (không đổi)**. Quy ước 'bỏ cả STRUCTURAL lẫn perm05' **chờ Mike/user duyệt**. Nếu chỉ bỏ perm05 (giữ STRUCTURAL của Bobby): 55.476, luật 4 vẫn đạt dư 254đ — sát ranh giới. Nhãn không nhạy theo trung vị/TB peer hay cỡ sleeve ở lát cắt này (chưa chạy cỡ sleeve 10–40 triệu: **chưa đo**).

**Ngoài phạm vi (chỉ ghi, để vào báo cáo):** `dd_NNC_20261030/r4/calc/model_r4.py:46` đặt `gpm_co` 2025 = 0,494 = GPM QUÝ Q4/25, trong khi GPM FY2025 trọng số doanh thu = **42,8%** (BQ, 4 quý 2025; đã đo). Chênh đá/toàn công ty 2025 thành +7,6pp thay vì +1,0pp ⇒ GAP TB +3,35pp (thay +0,10pp), GPM đá chu kỳ 37,6% thay 34,3%, trần chu kỳ cao hơn ≈ +5,2% (**ước lượng**, chưa chạy lại engine). Hướng: làm bản CHẶT và hiện hành đều cao hơn; chưa biết độ lớn trên tâm. Không áp dụng ở đây.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa file — chỉ đề xuất)
Giữ tier/type; cột entry = M giữ nguyên dòng cũ (độ hấp dẫn cấu trúc NGÀNH, moat_5f.py:33, không theo tier); cột cuối `Y` (moat_upgrade) giữ như dòng cũ — chỉ Mike quyết; làm mới risk1 + asof:
```
NNC,NARROW,LOCATION,M,"Single-asset Mui Tau (~94% rev, license to 2043) = finite clock; NOT durable: (i) fails on ROIC_Min5Y but (iii) alone suffices; ROE 10-13% in 2021-23 license-gap yrs; State is top supplier (back-charges ~42bn, now touching Mui Tau core, flag E12 open); GPM TTM 51% (Q4/25-Q3/26; Q3/26 qtr 53%) = cycle peak not moat; ROIC_Min5Y 1.3% is a lone FY2022 print (ROIC5Y 16.5%, ROIC10Y 29.6%, contradicts ROE 11.9% same yr = vendor artifact suspect); 17/04/2026 auction win unverified (possible clock extension); MVC may go to 51% (related-party); very thin liquidity",2026-11-07,5f_reuse_quickcheck,Y
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý: chỉ WARNING (luật 27/09).*
