# SZL — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_123133)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận: moat NARROW/LOCATION (tái dùng tag 05/06/2026), KHÔNG bền. Mô hình hiện hành KHÔNG nhất quán với luật 3c**: nó vốn hoá LN lõi ở biên TTM (GPM 39,0%) cao hơn TB chu kỳ của chính SZL (33,6%) tới 2053/vĩnh viễn, và cho g 2–4% không tái đầu tư (RONIC ngầm = ∞). Hiện hành: tâm **32.391** · P10 28.966 · P50 32.162 · P90 36.075 (sau CK 5 tỷ), **DƯỚI vùng**. **BẢN CHẶT-3C: tâm 24.423 (−24,6%) · P10 22.499 · P50 24.341 · P90 26.477, nhãn TRÊN vùng — quy ước chờ Mike/user duyệt; ở cỡ sleeve 40 tr là RANH GIỚI (P90 27.522 vs giá 27.650, cách 0,5%).**
Số: `5F/szl_moat_sens.py` → `5F/szl_moat_sens_out.txt/json` (exec nguyên phần khai báo `calc/model_r2.py`, tái lập đúng 32.391; chạy 2 lần trùng byte, md5 out `6634a9ed…`); ROIC/GPM: `5F/szl_5f_stats.py` → `5F/szl_5f_stats_out.txt` (BQ `ticker_financial`, truy vấn 07/11/2026, `5F/bq_fin_peers_20261107.csv`). Giá 27.650 (04/11).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng:** `data/moat_tags.csv` dòng SZL: NARROW · LOCATION · entry M · asof **2026-06-05** · src `5f_validated_compet` (5 tháng < 12 ⇒ chỉ kiểm nhanh, không nghiên cứu mới).
**Loại hình DN:** cho thuê đất KCN (KCN Sonadezi Long Thành, Đồng Nai) + dịch vụ hạ tầng (nước, xăng dầu, dịch vụ). Doanh thu thuê đất phần lớn thu trước, ghi nhận dần (DT chưa thực hiện 762,2 tỷ — REPORT_r2 §2).

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | Quỹ đất KCN cần quy hoạch + giao đất của Nhà nước; vị trí cạnh sân bay Long Thành (tag 06/2026). Nhưng Đồng Nai có nhiều KCN mới/mở rộng (cùng hệ Sonadezi: SZC, SZB) ⇒ rào cản hành chính, không độc quyền. |
| Nhà cung cấp | 🔴 Cao | Nhà nước (đất): trích bổ sung tiền thuê đất KCN Long Thành **44,3 tỷ** treo chưa quyết toán (TM16); khung giá đất thay đổi theo luật. |
| Người mua | 🟡 TB | Khách thuê FDI/nội địa ký hợp đồng dài, trả trước (ký quỹ 157,4 tỷ — TM17) ⇒ switching cost cao SAU khi ký. Tập trung khách: **cần kiểm chứng** (không có top-10 trong thư mục). |
| Sản phẩm thay thế | 🟡 TB | KCN lân cận Nhơn Trạch/Long Đức/Bà Rịa–Vũng Tàu — định tính, chưa có số giá thuê so sánh (**cần kiểm chứng**). |
| Cạnh tranh nội ngành | 🟡 TB | ROIC_Min5Y SZL **10,2%** vs trung vị 11 peer KCN nội địa **4,0%** ⇒ ổn định hơn peer. GPM không cùng định nghĩa: SZL TTM **39,0%** / TB năm 2017–25 **33,6%** vs peer trung vị **49,1%** / TB **46,0%** (TB năm 2017–25) — SZL lẫn mảng xăng dầu/nước biên thấp; peer: SZC, SZB, IDC, NTC, LHG, D2D, TIP, KBC, BCM, SIP, ITA (đều nội địa; loại PHR/DPR/GVR/VGC/IJC vì lõi cao su/VLXD/BĐS-thu phí, loại SNZ vì là mẹ hợp nhất SZL). |
| **Lực thứ 6** | 🔴 | (a) **Đồng hồ quỹ đất**: còn ~26 ha cho thuê, lấp đầy ~92% (tag 06/2026) ⇒ tăng trưởng thuê mới cạn đến khi có giai đoạn kế (CCN Long Phước, XDCB 344,7 tỷ — chưa có hợp đồng thuê). (b) **Thời hạn**: mốc 2053 (TM17, chưa đối chiếu giấy phép — **cần kiểm chứng**). (c) Chính sách đất đai/tiền thuê đất. |

**Kiểm nhanh "có gì đổi hào kể từ 05/06/2026":** không đổi tier. Mới từ BCTC Q3/26 (REPORT_r2): XDCB Long Phước 407 tỷ (có thể nối dài quỹ đất — chưa có hợp đồng ⇒ NPV 0), trích thuê đất 44,3 tỷ treo; GPM TTM 39,0% > TB chu kỳ 33,6% (Q3/26 NP quý 69,9 tỷ gồm cổ tức SZC/SZB) — chu kỳ/cơ cấu, không phải bằng chứng hào. WARNING SNZ (REPORT_r2 §6) không dùng trong 5F.
**moat_tier = NARROW · moat_type = LOCATION · rủi ro số 1 = quỹ đất KCN Long Thành gần cạn (~92% lấp đầy) + đồng hồ thời hạn 2053, tăng trưởng phụ thuộc Long Phước chưa có hợp đồng.**

## 2. Moat trong mô hình
| Điều kiện BỀN | KQ | Bằng chứng (BQ, 2026Q3; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ | **Hai phía ROIC:** ROIC_Min5Y **10,2%** < Ke; ROIC10Y **12,6%** < Ke; ROIC_Min10Y **8,0%**; ROIC5Y **13,7%** và ROIC3Y **13,8%** ≈ Ke (+0,2–0,3pp — không đủ "siêu ngạch"). ROIC5Y 2015–17 chỉ 5,7–6,5%. ROIC_Trailing 89,8% / _v1 61,7% mâu thuẫn ROIC5Y ⇒ nghi artifact vendor, không dùng. **ROE riêng** (không thay ROIC): ROE_Trailing 24,3% (Q3/26), ROE_Min5Y 16,7% > Ke — ROE bị đẩy bởi vốn chiếm dụng (DT chưa thực hiện 762 tỷ, ký quỹ) và đầu tư SZC/SZB theo giá gốc. |
| (ii) cơ chế gọi tên được | ✅ | LOCATION: quỹ đất KCN hiếm cạnh sân bay Long Thành + switching cost hợp đồng dài. |
| (iii) không đồng hồ | ❌ | Quỹ đất ~92% lấp đầy; thời hạn 2053. |

⇒ **moat_durable = false ⇒ luật 3c: RONIC=Ke VÀ biên về TB chu kỳ.** Rà soát `calc/model_r2.py` — **KHÔNG nhất quán**, hai kênh ngầm:
- **(R) RONIC:** `val()` dòng tiền = N0×(1−nc) tăng g 2–4%/năm **không trừ tái đầu tư** ⇒ RONIC ngầm = ∞ (kể cả nhánh 27 năm). Thu tiền thuê trả trước là danh nghĩa cố định ⇒ g không tự đến từ lạm phát. Bản chặt: dòng năm 1 = N0×(1−nc)×(1−g/r), áp **đối xứng** mọi ô g {2,3,4}% và r {12,5;13,5;14,5}% (giữ nguyên quy ước năm 1 của model: cf năm 1 không nhân (1+g), annuity 27 năm / Gordon — kiểm H).
- **(M) Biên:** N0 131,1 = LN lõi 9T/26 ×4/3 ở GPM TTM 39,0% (trọng số DT, Q4/25–Q3/26; BQ `GPM_P0` là giá trị MỘT quý) giữ tới 2053/vĩnh viễn, trên TB chu kỳ RIÊNG SZL 2017–25 **33,6%** (TB 9 năm GPM năm trọng số DT). Bản chặt: N0_cyc = N0 − (39,0%−33,6%) × DT TTM 581,8 × (1−20%) = **105,9 (−19,2%)** [UL: chi phí BH/QLDN giữ nguyên]; 5 mức ±12% đối xứng quanh N0_cyc. **TB ngành (peer 49,1%/46,0%) KHÔNG dùng**: khác định nghĩa (mảng xăng dầu/nước) và sẽ NÂNG N0 — không có cơ sở. Đây là lệch khỏi chữ "TB chu kỳ NGÀNH" của luật — chờ Mike duyệt.
- **Đã đúng luật:** XDCB Long Phước theo giá vốn (NPV 0 ⇒ RONIC=Ke trên đầu tư mới); đầu tư chưa niêm yết theo sổ; không bội số premium. Cross-check Gordon/ROE §3 REPORT_r2 dùng cùng N0 ⇒ cũng mang kênh (M).
- **Pháp lý (SNZ, thuê đất):** chỉ WARNING; không dùng ép N0. Trích thuê đất 44,3 đã trừ ở base, không trừ lại.

## 3. Độ nhạy WIDE / NARROW / NONE (lưới khoá 270 ô, trọng số giữ nguyên; sau CK 5 tỷ ~4,2%; giá 27.650)
| Moat giả định | Ánh xạ | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Nhãn 40 tr (P10/P90) |
|---|---|---|---|---|---|---|---|---|
| WIDE | không đồng hồ (chỉ vĩnh viễn), biên TTM, RONIC tự do | 33.691 | 29.810 | 33.484 | 38.379 | 1,1% | DƯỚI | DƯỚI |
| Hiện hành (REPORT_r2) | 27n/vv 3/4–1/4, biên TTM, RONIC ∞ | **32.391** | 28.966 | 32.162 | 36.075 | 3,4% | **DƯỚI** | DƯỚI (30.110/37.499) |
| chỉ (R) RONIC=Ke | | 27.578 | 25.197 | 27.476 | 30.120 | 54,8% | TRONG | TRONG |
| chỉ (M) biên TB chu kỳ | | 28.312 | 25.545 | 28.127 | 31.295 | 42,1% | TRONG | TRONG |
| **BẢN CHẶT-3C NARROW** *(chờ duyệt)* | (R)+(M), giữ đồng hồ 3/4–1/4 | **24.423** | 22.499 | 24.341 | 26.477 | 97,0% | **TRÊN** | **TRÊN — ranh giới** (23.388/27.522) |
| (độ nhạy) chặt-3c, g ≤2% coi là giá không cần tái đầu tư | | 26.981 | 24.726 | 26.705 | 29.593 | 66,7% | TRONG | TRONG |
| NONE | chặt-3c + chỉ 27 năm | 24.156 | 22.279 | 24.134 | 26.033 | 99,1% | TRÊN | TRÊN (P90 27.060) |

Tách chênh hiện hành → chặt (−7.968, −24,6%), tuần tự: (M) −4.079 rồi (R) −3.889; thứ tự ngược: (R) −4.813 rồi (M) −3.155. Hai kênh xấp xỉ ngang nhau. Nhãn **nhạy mạnh** với moat: DƯỚI (hiện hành) → TRONG (chỉ một kênh, hoặc g lạm phát miễn tái đầu tư) → TRÊN (chặt). Nhãn TRÊN của bản chặt phụ thuộc giả định N0_cyc [UL] và việc cho g lạm phát cũng cần tái đầu tư.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị và nhãn (nếu duyệt quy ước chặt-3c).** Mô hình REPORT_r2 giữ nguyên; KHÔNG sửa REPORT/SUMMARY cũ, KHÔNG ghi `dd_price_zones`. Theo luật 3c đúng nghĩa: tâm **32.391 → 24.423 (−24,6%)**, P10 28.966 → 22.499, P50 32.162 → 24.341, P90 36.075 → 26.477; % dưới giá 3,4% → 97,0%; **nhãn DƯỚI → TRÊN** ở 5 tỷ, **TRÊN nhưng ranh giới** ở 40 tr. Hai điểm quy ước chờ Mike/user: (1) "TB chu kỳ" dùng của riêng SZL thay ngành (peer khác định nghĩa GPM); (2) RONIC=Ke áp cả phần g ≈ lạm phát — nếu miễn g ≤2% thì tâm 26.981, TRONG vùng. Khoảng hợp lý theo quy ước: **24,4k–27,0k (chặt) so với 32,4k (hiện hành)**; mọi biến thể 3c đều thấp hơn nhãn DƯỚI của REPORT_r2 — nhãn DƯỚI chỉ đứng được nếu chấp nhận biên TTM bền + tăng trưởng không tái đầu tư, tức là thưởng moat mà (i)/(iii) không cho phép.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa file)
Giữ tier/type; entry = M giữ (độ hấp dẫn cấu trúc NGÀNH KCN, `moat_5f.py:33`, không theo tier); cột cuối `Y` giữ như dòng cũ (chỉ Mike quyết); làm mới risk1 + asof:
```
SZL,NARROW,LOCATION,M,"Sonadezi Long Thanh IP beside Long Thanh airport = scarce-land LOCATION; NOT durable: (i) ROIC_Min5Y 10.2% / ROIC10Y 12.6% / ROIC_Min10Y 8.0% < Ke 13.5% (ROIC5Y 13.7% ~Ke; ROE 24% flattered by prepaid-lease float), (iii) land bank ~92% leased + term to 2053 (unverified). #1 risk: growth hinges on Long Phuoc CIP 407bn with no lease contracts; GPM TTM 39.0% > own cycle 33.6% = cycle/mix not moat; State land-rent accrual 44.3bn unsettled",2026-11-07,5f_reuse_quickcheck,Y
```

## 6. Mở
Top khách thuê/tập trung; giá thuê so KCN lân cận; tách GPM theo mảng (để so peer cùng định nghĩa); giấy phép thuê đất mốc 2053; cơ sở N0_cyc (BH/QLDN theo chu kỳ). Chưa qua fundamental-skeptic (Mike chạy).

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý: chỉ WARNING (luật 27/09).*
