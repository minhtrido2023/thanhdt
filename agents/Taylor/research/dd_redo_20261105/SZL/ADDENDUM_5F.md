# SZL — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình — r3 (07/11/2026, job Taylor_20261107_124455)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. Bản trước: `ADDENDUM_5F_r2.md`. **Kết luận: moat NARROW/LOCATION (tái dùng tag 05/06/2026), KHÔNG bền. Mô hình hiện hành KHÔNG nhất quán với luật 3c**: nó vốn hoá LN lõi ở biên GPM TTM 39,0% (cao hơn TB chu kỳ của chính SZL 33,6%) tới 2053/vĩnh viễn, và cho g 2–4% không tái đầu tư (RONIC ngầm = ∞). Hiện hành: tâm **32.391** · P10 28.966 · P50 32.162 · P90 36.075 (sau CK 5 tỷ), **DƯỚI vùng**. **BẢN CHẶT-3C (r3, đã sửa công thức): tâm 24.868 (−23,2%) · P10 23.011 · P50 24.724 · P90 27.099; nhãn 5 tỷ TRÊN vùng nhưng MONG MANH theo cửa sổ biên (P90 27.099 vs giá 27.650, cách 2,0%; cửa sổ 2021–25 ⇒ TRONG); ở cỡ sleeve 40 tr: TRONG (P10/P90 23.919/28.168) — quy ước chờ Mike/user duyệt.**
Số: `5F/szl_moat_sens.py` → `5F/szl_moat_sens_out.txt/json` (exec nguyên phần khai báo `calc/model_r2.py`, tái lập đúng 32.391; chạy 2 lần trùng byte, md5 out.txt `3b3ab52d…`, out.json `e5275d71…`); ROIC/GPM: `5F/szl_5f_stats.py` → `5F/szl_5f_stats_out.txt` (BQ `ticker_financial`, truy vấn 07/11/2026, `5F/bq_fin_peers_20261107.csv`). Giá 27.650 (04/11).

**Sửa so với r2:** (1) công thức RONIC=Ke ở nhánh hữu hạn (r2 nhân (1−g/r) vào annuity 27 năm ⇒ vốn tái đầu tư mất lợi suất ở 2053 ⇒ NPV âm, đếm hai lần với đồng hồ 2053, trái luật NPV 03/11) — chặt-3c 24.423 → **24.868**, nhãn 40 tr TRÊN → **TRONG**; (2) thêm độ nhạy cửa sổ biên; (3) điều kiện (i) thêm ROE lõi; (4) giữ mốc chiều lên sân bay Long Thành, gắn "cần kiểm chứng" cho số quỹ đất.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng:** `data/moat_tags.csv` dòng SZL: NARROW · LOCATION · entry M · asof **2026-06-05** · src `5f_validated_compet` (5 tháng < 12 ⇒ chỉ kiểm nhanh, không nghiên cứu mới).
**Loại hình DN:** cho thuê đất KCN (KCN Sonadezi Long Thành, Đồng Nai) + dịch vụ hạ tầng (nước, xăng dầu, dịch vụ). Doanh thu thuê đất phần lớn thu trước, ghi nhận dần (DT chưa thực hiện 762,2 tỷ — REPORT_r2 §2).

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Quỹ đất KCN cần quy hoạch + giao đất của Nhà nước; vị trí cạnh sân bay Long Thành (tag 06/2026: "premium catalyst"). Nhưng Đồng Nai có nhiều KCN mới/mở rộng (cùng hệ Sonadezi: SZC, SZB) ⇒ rào cản hành chính, không độc quyền. |
| Nhà cung cấp | 🔴 Cao | Nhà nước (đất): trích bổ sung tiền thuê đất KCN Long Thành **44,3 tỷ** treo chưa quyết toán (TM16); khung giá đất thay đổi theo luật. |
| Người mua | 🟡 TB | Khách thuê FDI/nội địa ký hợp đồng dài, trả trước (ký quỹ 157,4 tỷ — TM17) ⇒ switching cost cao SAU khi ký. Tập trung khách: **cần kiểm chứng** (không có top-10 trong thư mục). |
| Sản phẩm thay thế | 🟡 TB | KCN lân cận Nhơn Trạch/Long Đức/Bà Rịa–Vũng Tàu — định tính, chưa có số giá thuê so sánh (**cần kiểm chứng**). |
| Cạnh tranh nội ngành | 🟡 TB | ROIC_Min5Y SZL **10,2%** vs trung vị 11 peer KCN nội địa **4,0%** ⇒ ổn định hơn peer. GPM không cùng định nghĩa: SZL TTM **39,0%** / TB năm 2017–25 **33,6%** vs peer trung vị **49,1%** / TB **46,0%** (TB năm 2017–25) — SZL lẫn mảng xăng dầu/nước biên thấp; peer: SZC, SZB, IDC, NTC, LHG, D2D, TIP, KBC, BCM, SIP, ITA (đều nội địa; loại PHR/DPR/GVR/VGC/IJC vì lõi cao su/VLXD/BĐS-thu phí, loại SNZ vì là mẹ hợp nhất SZL). |
| **Lực thứ 6** | 🔴 | (a) **Đồng hồ quỹ đất**: còn ~26 ha cho thuê, lấp đầy ~92% (từ tag 06/2026, không phải BCTC — **cần kiểm chứng**) ⇒ tăng trưởng thuê mới cạn đến khi có giai đoạn kế (CCN Long Phước, XDCB — chưa có hợp đồng thuê). (b) **Thời hạn**: mốc 2053 (TM17, chưa đối chiếu giấy phép — **cần kiểm chứng**). (c) Chính sách đất đai/tiền thuê đất. |

**Kiểm nhanh "có gì đổi hào kể từ 05/06/2026":** không đổi tier. Mới từ BCTC Q3/26 (REPORT_r2): XDCB Long Phước 407 tỷ (có thể nối dài quỹ đất — chưa có hợp đồng ⇒ NPV 0), trích thuê đất 44,3 tỷ treo; GPM TTM 39,0% > TB chu kỳ 33,6% (Q3/26 NP quý 69,9 tỷ gồm cổ tức SZC/SZB) — chu kỳ/cơ cấu, không phải bằng chứng hào. **Mốc chiều lên giữ nguyên từ tag cũ:** sân bay Long Thành = "premium catalyst" (cầu thuê/giá thuê) — chưa lượng hoá trong base (không có hợp đồng/giá thuê để định giá, NPV 0 theo luật dự án mới). WARNING SNZ (REPORT_r2 §6) không dùng trong 5F.
**moat_tier = NARROW · moat_type = LOCATION · rủi ro số 1 = quỹ đất KCN Long Thành gần cạn (~92% lấp đầy, cần kiểm chứng) + đồng hồ thời hạn 2053, tăng trưởng phụ thuộc Long Phước chưa có hợp đồng.**

## 2. Moat trong mô hình
| Điều kiện BỀN | KQ | Bằng chứng (BQ, 2026Q3; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ | **Hai phía ROIC:** ROIC_Min5Y **10,2%** < Ke; ROIC10Y **12,6%** < Ke; ROIC_Min10Y **8,0%**; ROIC5Y **13,7%** và ROIC3Y **13,8%** ≈ Ke (+0,2–0,3pp — không đủ "siêu ngạch"). ROIC5Y 2015–17 chỉ 5,7–6,5%. ROIC_Trailing 89,8% / _v1 61,7% mâu thuẫn ROIC5Y — không dùng, nghi artifact vendor (**chưa kiểm**). **ROE riêng** (không thay ROIC): ROE_Trailing 24,3% (Q3/26), ROE_Min5Y 16,7%; **ROE lõi 33,9%** (REPORT_r2 §3: LN lõi / vốn CSH trừ đầu tư SZC/SZB + XDCB — vốn khớp N0). Phía thuận chiều này không đổi kết luận: (a) ROE lõi cao chủ yếu do mẫu số nhỏ vì khách thuê tài trợ đất qua tiền trả trước (DT chưa thực hiện 762 tỷ + ký quỹ 157 tỷ) — đó là đòn bẩy từ vốn chiếm dụng, không phải lợi suất trên vốn đầu tư; ROIC (đo trên vốn đầu tư) mới là phép thử (i); (b) phần vốn bị loại khỏi mẫu số (cổ phần SZC/SZB, XDCB Long Phước) KHÔNG tính là siêu ngạch vì chúng được định giá riêng trong SOTP (thị giá/sổ/giá vốn = NPV 0) — tính chúng vào lợi thế lõi là đếm hai lần; (c) ROE lõi một thời điểm (TTM, biên đang ở đỉnh chuỗi), không phải nhiều chu kỳ. |
| (ii) cơ chế gọi tên được | ✅ | LOCATION: quỹ đất KCN hiếm cạnh sân bay Long Thành + switching cost hợp đồng dài. |
| (iii) không đồng hồ | ❌ | Quỹ đất ~92% lấp đầy / ~26 ha còn lại (từ tag 06/2026, không BCTC — **cần kiểm chứng**); thời hạn 2053 (**cần kiểm chứng** giấy phép). |

⇒ **moat_durable = false ⇒ luật 3c: RONIC=Ke VÀ biên về TB chu kỳ.** Rà soát `calc/model_r2.py` — **KHÔNG nhất quán**, hai kênh ngầm:
- **(R) RONIC [SỬA r3]:** `val()` dòng tiền = N0×(1−nc) tăng g 2–4%/năm **không trừ tái đầu tư** ⇒ RONIC ngầm = ∞ (kể cả nhánh 27 năm). Thu tiền thuê trả trước là danh nghĩa cố định ⇒ g không tự đến từ lạm phát. Bản chặt r3: tăng trưởng tái đầu tư ở RONIC=Ke có **NPV 0** ⇒ giá trị = dòng tiền ban đầu không tăng trưởng: vĩnh viễn **cf₀/r**; nhánh 27 năm = **annuity không tăng trưởng** cf₀×(1−(1+r)⁻²⁷)/r. Áp đối xứng mọi ô g {2,3,4}% × r {12,5;13,5;14,5}%. Quy ước năm 1 giữ như model (cf năm 1 không nhân (1+g); kiểm H). *r2 nhân (1−g/r) vào annuity 27 năm: phần vốn giữ lại tái đầu tư không được thu hồi ở 2053 ⇒ NPV âm và trùng với đồng hồ 2053 — SAI, đã bỏ.*
- **(M) Biên:** N0 131,1 = LN lõi 9T/26 ×4/3 ở GPM TTM 39,0% giữ tới 2053/vĩnh viễn, trên TB chu kỳ RIÊNG SZL 2017–25 **33,6%**. Bản chặt: N0_cyc = N0 − (39,0%−33,6%) × DT TTM 581,8 × (1−20%) = **105,9 (−19,2%)** [UL: chi phí BH/QLDN giữ nguyên]; 5 mức ±12% đối xứng quanh N0_cyc. *Ghi chú quy tắc GPM 07/11 19:50:* đầu vào 39,0%/33,6% giữ như r2 theo chỉ đạo Mike (nhãn GPM TTM không đổi); script cũ tính chúng bằng TB trọng số DT của chuỗi GPM_P0 (giả định GPM_P0 là quý — mô tả đó sai, GPM_P0 là TTM). Theo quy tắc mới (TTM = GPM_P0 2026Q3 = 38,8%; năm = GPM_P0 Q4) tâm chặt-3c = **24.973** (+105 so với headline, nhãn không đổi) — xem §3b.
- **TB ngành (peer 49,1%/46,0%) KHÔNG dùng** — khác định nghĩa (SZL lẫn mảng xăng dầu/nước) và sẽ NÂNG N0. **Tách GPM theo mảng (thuê đất/nước/xăng dầu): KHÔNG có số trong thư mục** (BCTC `src/*.pdf` là bản scan không có lớp chữ; REPORT/REPORT_r2 không có số mảng) ⇒ **còn mở**: chưa so được GPM mảng KCN của SZL với peer cùng định nghĩa, nên quy ước "TB riêng SZL thay TB ngành" là lệch khỏi chữ luật — chờ Mike duyệt, chưa chốt.
- **Đã đúng luật:** XDCB Long Phước theo giá vốn (NPV 0 ⇒ RONIC=Ke trên đầu tư mới); đầu tư chưa niêm yết theo sổ; không bội số premium. Cross-check Gordon/ROE §3 REPORT_r2 dùng cùng N0 ⇒ cũng mang kênh (M).
- **Pháp lý (SNZ, thuê đất):** chỉ WARNING; không dùng ép N0. Trích thuê đất 44,3 đã trừ ở base, không trừ lại.

## 3. Độ nhạy WIDE / NARROW / NONE (lưới khoá 270 ô, trọng số giữ nguyên; sau CK 5 tỷ ~4,2%; giá 27.650)
| Moat giả định | Ánh xạ | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Nhãn 40 tr (P10/P90) |
|---|---|---|---|---|---|---|---|---|
| WIDE | không đồng hồ (chỉ vĩnh viễn), biên TTM, RONIC tự do | 33.691 | 29.810 | 33.484 | 38.379 | 1,1% | DƯỚI | DƯỚI (30.987/39.894) |
| Hiện hành (REPORT_r2) | 27n/vv 3/4–1/4, biên TTM, RONIC ∞ | **32.391** | 28.966 | 32.162 | 36.075 | 3,4% | **DƯỚI** | DƯỚI (30.110/37.499) |
| chỉ (R) RONIC=Ke | | 28.129 | 25.831 | 27.950 | 30.889 | 40,9% | TRONG | TRONG (26.850/32.109) |
| chỉ (M) biên TB chu kỳ | | 28.312 | 25.545 | 28.127 | 31.295 | 42,1% | TRONG | TRONG (26.553/32.530) |
| **BẢN CHẶT-3C NARROW** *(chờ duyệt)* | (R)+(M), giữ đồng hồ 3/4–1/4 | **24.868** | 23.011 | 24.724 | 27.099 | 95,3% | **TRÊN — mong manh** | **TRONG** (23.919/28.168) |
| (độ nhạy) chặt-3c, g ≤2% coi là giá không cần tái đầu tư | | 26.977 | 24.768 | 26.704 | 29.471 | 68,0% | TRONG | TRONG (25.746/30.634) |
| NONE | chặt-3c + chỉ 27 năm | 24.750 | 22.627 | 24.724 | 26.902 | 96,9% | TRÊN | TRONG (23.521/27.964) |

Tách chênh hiện hành → chặt (−7.523, −23,2%), tuần tự: (M) −4.079 rồi (R) −3.444; thứ tự ngược: (R) −4.262 rồi (M) −3.261. Hai kênh xấp xỉ ngang nhau.

**3b. Độ nhạy cửa sổ biên chu kỳ (chặt-3c, RONIC=Ke):** chuỗi GPM năm (cách r2) tăng gần đều **30,5% (2017) → 32,5 → 32,5 → 33,3 → 35,7 → 33,9 → 33,2 → 34,0 → 37,1 (2025) → 39,0% TTM** — chọn cửa sổ là chọn mức "chu kỳ".
| Cửa sổ biên chu kỳ | GPM TTM / chu kỳ | N0_cyc | Tâm | P10 | P90 | Nhãn 5 tỷ | Nhãn 40 tr (P10/P90) |
|---|---|---|---|---|---|---|---|
| TB năm 2017–25 (headline) | 39,04% / 33,63% | 105,9 | 24.868 | 23.011 | 27.099 | TRÊN | TRONG (23.919/28.168) |
| TB trọng số DT 2017–25 | 39,04% / 33,84% | 106,9 | 24.997 | 23.123 | 27.249 | TRÊN | TRONG (24.035/28.324) |
| TB năm 2021–25 | 39,04% / 34,77% | 111,2 | 25.555 | 23.605 | 27.897 | **TRONG** | TRONG (24.537/28.998) |
| Quy tắc GPM 07/11: Q4 GPM_P0 2017–25 | 38,77% / 33,53% | 106,7 | 24.973 | 23.101 | 27.220 | TRÊN | TRONG (24.013/28.295) |
| Quy tắc GPM 07/11: Q4 GPM_P0 2021–25 | 38,77% / 35,09% | 114,0 | 25.911 | 23.913 | 28.311 | **TRONG** | TRONG (24.857/29.429) |

(Cửa sổ 2021–25 brief nêu 34,85%; đo lại từ cùng CSV ra **34,77%** — chênh không đổi nhãn.) **Tâm chặt-3c hợp lý ~24,9k–25,9k** theo cửa sổ. **Nhãn 5 tỷ TRÊN là "mong manh theo cửa sổ"**: giá chỉ cao hơn P90 1,5%–2,0% ở các cửa sổ 2017–25, và lật sang TRONG khi dùng cửa sổ 2021–25. Ở cỡ sleeve 40 tr: **TRONG ở mọi cửa sổ**.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị và nhãn (nếu duyệt quy ước chặt-3c).** Mô hình REPORT_r2 giữ nguyên; KHÔNG sửa REPORT/SUMMARY cũ, KHÔNG ghi `dd_price_zones`. Theo luật 3c đúng nghĩa (r3): tâm **32.391 → 24.868 (−23,2%)**, P10 28.966 → 23.011, P50 32.162 → 24.724, P90 36.075 → 27.099; % dưới giá 3,4% → 95,3%; **nhãn 5 tỷ DƯỚI → TRÊN (mong manh theo cửa sổ: 2021–25 ⇒ TRONG)**; **nhãn 40 tr DƯỚI → TRONG** (r2 viết TRÊN-ranh giới — sai do lỗi công thức, đã đính chính). Hai điểm quy ước chờ Mike/user: (1) "TB chu kỳ" dùng của riêng SZL thay ngành (peer khác định nghĩa GPM; tách mảng còn mở); (2) RONIC=Ke áp cả phần g ≈ lạm phát — nếu miễn g ≤2% thì tâm 26.977, TRONG vùng. Khoảng hợp lý: **24,9k–27,0k (chặt, theo cửa sổ/g) so với 32,4k (hiện hành)**; mọi biến thể 3c đều rời nhãn DƯỚI của REPORT_r2 — DƯỚI chỉ đứng được nếu chấp nhận biên TTM bền + tăng trưởng không tái đầu tư, tức là thưởng moat mà (i)/(iii) không cho phép. moat_tier/durable không đổi (bằng chứng ROIC/đồng hồ không đổi).

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa file)
Giữ tier/type; entry = M giữ (độ hấp dẫn cấu trúc NGÀNH KCN, `moat_5f.py:33`, không theo tier); cột cuối `Y` giữ như dòng cũ (chỉ Mike quyết); làm mới risk1 + asof, giữ mốc chiều lên sân bay:
```
SZL,NARROW,LOCATION,M,"Sonadezi Long Thanh IP beside new Long Thanh airport (= premium catalyst, unquantified) = scarce-land LOCATION; NOT durable: (i) ROIC_Min5Y 10.2% / ROIC10Y 12.6% / ROIC_Min10Y 8.0% < Ke 13.5% (ROIC5Y 13.7% ~Ke; core ROE 33.9% flattered by prepaid-lease float), (iii) land bank ~92% leased / ~26ha left (from 06/2026 tag, unverified) + term to 2053 (unverified). #1 risk: growth hinges on Long Phuoc CIP 407bn with no lease contracts; GPM TTM 39.0% > own cycle 33.6% = cycle/mix not moat; State land-rent accrual 44.3bn unsettled",2026-11-07,5f_reuse_quickcheck,Y
```

## 6. Mở
Top khách thuê/tập trung; giá thuê so KCN lân cận; **tách GPM theo mảng** (BCTC scan — cần OCR/thuyết minh bộ phận) để so peer cùng định nghĩa; số quỹ đất 92%/26 ha từ BCTC/công bố; giấy phép thuê đất mốc 2053; ROIC_Trailing vendor (chưa kiểm); cơ sở N0_cyc (BH/QLDN theo chu kỳ). Chưa qua fundamental-skeptic (Mike chạy).

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý: chỉ WARNING (luật 27/09).*
