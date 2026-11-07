# NNC — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_120556)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận: moat NARROW/LOCATION (tái dùng tag 05/06/2026), KHÔNG bền ⇒ không thưởng; mô hình KHÔNG ĐỔI** (tâm 57.589 · P10 30.219 · P50 52.916 · P90 93.649 sau CK; nhãn TRONG vùng). Tất cả số độ nhạy lấy từ lưới đã khoá `calc/grid_nnc_redo_r2.csv` qua `5F/moat_sens_5f.py` (đã đối chứng: cột NARROW hiện hành tái lập đúng số REPORT_r2; chạy 2 lần trùng md5).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới:** TÁI DÙNG. `data/moat_tags.csv` dòng NNC: NARROW · LOCATION · asof **2026-06-05** · src `5f_validated_compet` (5 tháng < 12 tháng ⇒ theo luật tần suất 06/11 chỉ kiểm nhanh). Không nghiên cứu mới; số kiểm nhanh lấy từ BQ `tav2_bq.ticker_financial` (truy vấn 07/11/2026) và dữ kiện đã có trong REPORT_r2 / `dd_NNC_20261030/`.

**Loại hình DN:** tài nguyên/khai thác đá xây dựng — hào = vị trí (bán kính vận chuyển) + giấy phép; rủi ro lõi = vòng đời giấy phép/trữ lượng + Nhà nước.

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Cần giấy phép mỏ (Mũi Tàu 51,5 ha, 1,0 tr m³ nguyên khối/năm, GP tới 2043 — BCTN25 tr.3). Nhưng mỏ mới trong cụm được đấu giá (VĐ4/Đồng Nai tới 06/2027 — REPORT_r2 §8) ⇒ rào cản là hành chính, không vĩnh viễn. Bán kính vận chuyển: **cần kiểm chứng** (không có số chi phí/km trong thư mục). |
| Nhà cung cấp | 🔴 Cao | Nhà nước = nhà cung cấp quyền lực nhất: tổng truy thu Núi Nhỏ ≈**42 tỷ ≈1.900 đ/cp**; truy thu đã chạm mỏ lõi Mũi Tàu (dự phòng 0,84 tỷ, CQKTKS 1,735 tỷ — cờ E12 chưa đóng). Đầu vào khác (điện, dầu, nổ mìn) phân tán. |
| Người mua | 🟡 TB | Cầu theo dự án hạ tầng (Long Thành, VĐ4) — lổn nhổn. Bên liên quan NHC chiếm **61% phải thu**; DT dịch vụ 2025 18,92 tỷ ≈ DT từ NHC 18,41 tỷ (REPORT_r2 §7). Khách lẻ ngoài NHC: **cần kiểm chứng** cơ cấu. |
| Sản phẩm thay thế | 🟢 Thấp | Đá dăm không có vật thay thế quy mô cho bê tông/nền đường (định tính, không có số). |
| Cạnh tranh nội ngành | 🟡 TB | Cụm mỏ Đông Nam Bộ: DHA, VLB, KSB. GPM TB 2012–25: **NNC 34,1%** vs KSB 40,4% · DHA 26,0% · VLB 24,7% (`dd_NNC_20261030/r3/calc/sector_gpm_roe.csv`) ⇒ NNC ở giữa nhóm, không vượt trội cấu trúc. GPM TTM Q3/26 **53%** = đỉnh chu kỳ (2022: 21%). |
| **Lực thứ 6** | 🔴 | (a) **Đồng hồ giấy phép**: Mũi Tàu hết 2043 (~17 năm); đã từng xảy ra — Núi Nhỏ hết GP 2019 ⇒ ROE rơi từ 38–49% (2012–20) xuống **10–13%** (2021–23). (b) Quy định/truy thu (như trên). (c) MVC được uỷ quyền lên 51% (giao dịch bên liên quan). (d) Có thể gia hạn hào: CBTT 17/04/2026 trúng đấu giá quyền khai thác (UBND TP.HCM) — **chưa đối chiếu** mỏ/giá/hạn. |

**Kiểm nhanh "có gì đổi hào kể từ 05/06/2026":** không đổi tier. Mới/được làm rõ: cờ truy thu chạm Mũi Tàu (E12, 31/10) — nghiêng xấu; GPM lên 53–58% là chu kỳ giá, không phải bằng chứng hào; CBTT đấu giá 17/04 (có trước asof nhưng tag không nhắc) — có thể kéo dài đồng hồ, chưa xác minh.

**moat_tier = NARROW · moat_type = LOCATION · rủi ro số 1 = đồng hồ giấy phép/Nhà nước trên mỏ đơn lẻ Mũi Tàu (~94% DT, GP tới 2043, truy thu đã chạm mỏ lõi).**

## 2. Moat trong mô hình
| Điều kiện moat BỀN | Kết quả | Bằng chứng (BQ `ticker_financial`, 07/11/2026) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ | ROIC_Min5Y **1,3%** (2026Q3) < Ke 13,5%; ROE_Trailing 2021/22/23/24 = **13,0/11,9/10,1/15,5%** — 3/4 năm dưới Ke. ROIC5Y 16,5% kéo lên bởi năm đỉnh. |
| (ii) cơ chế rào cản gọi tên được | ✅ | Giấy phép + bán kính vận chuyển (LOCATION). |
| (iii) không có đồng hồ cắt hào | ❌ | GP 2043; tiền lệ Núi Nhỏ 2019; truy thu chạm mỏ lõi. |

⇒ **moat_durable = false ⇒ KHÔNG thưởng.** Rà soát mô hình hiện hành (`dd_NNC_20261030/r4–r6/calc`, import bởi `calc/nnc_redo_r2.py`) — **đã nhất quán, không cộng premium:**
- **Không có giá trị cuối kỳ:** DCF hữu hạn 2027–2043 (`r3/calc/model_r3.py:90`), sau GP = 0 ⇒ chặt hơn cả RONIC = Ke; khớp với đồng hồ (iii).
- **Đầu tư mới** (CIP Tam Lập 1 khu II 83,5 tỷ) ở sổ sách, NPV 0 ⇒ RONIC = Ke. Nhất quán.
- **Biên:** CYCLICAL hồi về GPM chu kỳ **34,3%** (TB NNC 2012–25 + chênh đá; `r4/calc/model_r4_out.txt:5`) — đúng chuẩn "NARROW ⇒ biên về TB chu kỳ". ADMIN_GATED hồi biên có trễ 1 năm (nghẽn hành chính tạm thời).
- **Điểm cần nói rõ — nhánh STRUCTURAL (trọng số 0,20):** giữ biên đỉnh tới 2043. Cơ sở là trạng thái CUNG CẤP NGÀNH của Bobby (sàn giá do đấu giá/mỏ xa — áp cho cả cụm, đọc MÙ mã), không phải lợi thế riêng của NNC; nó là một kịch bản có trọng số, không phải premium cộng lên base ⇒ tôi coi là **không đếm hai lần với moat**. Nhưng nếu đọc luật NARROW chặt ("không giữ biên trên TB chu kỳ dưới mọi hình thức") thì đây là chỗ duy nhất mô hình giữ siêu ngạch kéo dài — số "NARROW chặt" ở bảng dưới để Mike quyết.
- Không dùng bội số premium nào (Gordon chỉ để kiểm chéo, ROE chuẩn hoá — REPORT_r2 §6).

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 46.900)
| Moat giả định | Cách ánh xạ trên lưới khoá | Tâm | P10 | P50 | P90 | % dưới giá | Luật 4 (giá ≤ 0,85×tâm) |
|---|---|---|---|---|---|---|---|
| WIDE | 100% STRUCTURAL (biên đỉnh bền tới 2043) | 84.655 | 31.729 | 89.665 | 127.891 | 25,0% | đạt |
| **NARROW — hiện hành** | Bobby 0,20/0,45/0,35 (= REPORT_r2) | **57.589** | **30.219** | **52.916** | **93.649** | 37,5% | đạt |
| NARROW chặt | bỏ STRUCTURAL; ADMIN/CYC 0,5625/0,4375 | 50.822 (−11,8%) | 30.015 | 50.616 | 69.773 | 40,6% | **không** (ngưỡng 43.199) |
| NONE | 100% CYCLICAL (biên về TB chu kỳ ngay 2028) | 47.608 (−17,3%) | 29.431 | 48.521 | 63.576 | 45,4% | **không** |

Đọc: P10 gần như không nhạy theo moat (29,4–31,7k — được neo bởi tiền ròng + sàn chi phí); moat chỉ di chuyển tâm và đuôi phải. Nhãn **TRONG vùng giữ ở cả 4 dòng** (P10 < 46.900 < P90). NONE "theo peer" (biên về TB DHA/VLB ~25%, thấp hơn TB chính NNC) **chưa đo** — sẽ thấp hơn dòng NONE.

## 4. Thay đổi so với báo cáo hiện hành
Không đổi giá trị, không đổi nhãn: moat NARROW đã được mô hình phản ánh đúng (không giá trị cuối kỳ, RONIC = Ke cho đầu tư mới, biên hồi về TB chu kỳ ở 80% trọng số). Điều mới duy nhất là **minh bạch hoá**: luận điểm "rẻ theo luật 4" phụ thuộc nhánh STRUCTURAL 0,20 — nếu Mike chọn đọc NARROW chặt, tâm 50.822 và luật 4 KHÔNG còn đạt (nhãn vẫn TRONG vùng). Không ghi `dd_price_zones`, không sửa REPORT/SUMMARY cũ.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa file — chỉ đề xuất)
Giữ tier/type; chỉ làm mới risk1 + asof kiểm nhanh:
```
NNC,NARROW,LOCATION,M,"Single-asset Mui Tau (~94% rev, license to 2043) = finite clock; NOT durable: ROIC_Min5Y 1.3% (2026Q3) < Ke 13.5%, ROE 10-13% in 2021-23 license-gap yrs; State is top supplier (back-charges ~42bn, now touching Mui Tau core, flag E12 open); GPM 53% TTM Q3/26 = cycle peak not moat; 17/04/2026 auction win unverified (possible clock extension); MVC may go to 51% (related-party); very thin liquidity",2026-11-07,5f_reuse_quickcheck,Y
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý: chỉ WARNING (luật 27/09).*
