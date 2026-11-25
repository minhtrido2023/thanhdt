# PRELOCK ADDENDUM J3 — chu kỳ hàng hoá / chu kỳ ngành (job Taylor_20261125_014736)

Khoá và commit TRƯỚC khi chạy bất kỳ mô hình chu kỳ nào (bước 1 = vá J2 đã commit `1304ad1dd`; chưa có dòng code chu kỳ nào chạy).
Mọi thứ ở `PRELOCK.md` (§0 dữ liệu, mẫu chung, sai số e, era IS 2014–2019 / OOS 2020+) giữ nguyên trừ chỗ ghi đè dưới đây.
Panel định giá: V3.1 `in_snapshot_v31/vp2.parquet` md5 `3b89e78d40d1ce68a3212223e6cd5b11` (= `out_F/vp2.parquet` trong MD5SUMS của dcf_vn_redesign V3.1).

## 0. Nguồn chu kỳ (đã tra `mike/kb/data_registry/` trước khi chọn)
- **Dùng**: World Bank CMO tháng (`data/_wb_cache/CMO-Historical-Data-Monthly.xlsx`, CANONICAL, snapshot `in_cycle/` md5 `689f456062fc470e3011c1ef7a799cf6`, "Updated on November 03, 2026"), 1960→, phủ IS.
  Chuỗi: Rubber RSS3, Crude oil average, Urea, DAP, Sugar world (đúng 5 họ của bản đồ đóng băng).
  **PIT**: giá tháng m coi là biết từ ngày cuối tháng m + 35 ngày (WB ra Pink Sheet đầu tháng sau; +35 bảo thủ). **Hạn chế khai trước**: 1 vintage (bản 03/11/2026), WB có sửa nhỏ số tháng gần nhất ⇒ không phải vintage đầu; mức sửa không đo được.
- **Loại** (khai lý do): TE daily (`commodity_prices`, từ 2016-10 ⇒ IS chỉ 3 năm, `fetched_at` backfill 1 lần ⇒ không PIT); sunsirs (P4 chỉ từ 2018, không PIT); `bdi_daily_real.csv` (từ 2026-05); `hog_price_vn.csv` (chỉ ~2026, map ghi 2019+ ⇒ không IS); `freight_rates_quarterly.csv` (không đăng ký, dựng lại); `caustic_soda_monthly.csv` (SYNTHETIC); thép HRC/VN (không có chuỗi PIT phủ IS). Thép, thuỷ sản, chăn nuôi, vận tải biển, KCN, xây dựng, xi măng ⇒ **chỉ** vào được qua phân loại chu kỳ PIT từ chính LNST (mục 1b), không có yếu tố giá hàng hoá.
- Kết luận đã có, không lặp: `commodity_cycle_te_20261026` (giá hàng hoá quý → tăng trưởng LN IC ~0,45 nhưng không có edge giá cổ phiếu); `commodity_cycle_prereg_20261025` (momentum hàng hoá → giá: NO-GO). Ở đây chỉ đo **dự báo earnings + tâm định giá**, không đo tín hiệu giao dịch.

## 1. Nhóm & pha (PIT, công thức khoá)
a. **COMM** = mã `in_primary == "Y"` trong `in_cycle/commodity_map.csv` (đóng băng 2026-10-25, md5 `cf4bef531aba172309e433113261b957`, đọc bằng csv parser; bản đồ theo mô tả hoạt động kinh doanh, KHÔNG dựng từ kết quả — hạn chế: mô tả kinh doanh là hiện tại). 5 họ: cao su, dầu thô, urê, DAP, đường.
b. **Độ chu kỳ PIT** (mọi mã): cyc = độ lệch chuẩn của ROE_ttm (= ΣNP_P0..3 / E, điểm ROE năm) trên các sự kiện của chính mã có K ≤ K hiện tại, cửa sổ 32 quý gần nhất, cần ≥ 16. Tercile chéo trong quý báo cáo ⇒ CYC_HI / CYC_MID / CYC_LO.
c. **FIN** = route PIT (rating 8L gần nhất ≤ K) ∈ {BANK, SECURITIES, INSURANCE} (chu kỳ tín dụng — báo riêng).
   Nhóm loại trừ để báo cáo: COMM > FIN > CYC_HI > CYC_MID > CYC_LO (> NA nếu thiếu lịch sử).
d. **Pha** (mọi mã): dev = ROE_ttm − trung vị(ROE_ttm của ≤ 32 quý TRƯỚC, cần ≥ 16); s = sd cùng cửa sổ. PEAK nếu dev > +0,5·s; TROUGH nếu dev < −0,5·s; MID còn lại.
   Phụ cho COMM: pha giá hàng hoá cph = log(TB 3 tháng biết gần nhất / TB 60 tháng biết gần nhất): HIGH > +0,15, LOW < −0,15, MID.

## 2. A' — sai số dự báo theo nhóm × pha (MÔ TẢ, không fit)
Trên mẫu chung J2/J3 (`out_J3/fc.parquet`, h = 1 và tổng 4 quý): MdAE, thiên lệch có dấu (trung vị e) của ENS và D0imp theo nhóm × pha × era.
Câu hỏi khoá: (i) thiên lệch D0imp có tập trung ở PEAK (D0imp đánh giá thấp ⇒ e > 0) / TROUGH (đánh giá cao ⇒ e < 0) và ở CYC_HI/COMM hơn CYC_LO? (ii) phần |sai số| D0imp do CYC_HI+COMM chiếm bao nhiêu.
Báo sign-count theo năm cho mỗi ô có ≥ 30 sự kiện/năm. Không CI khối năm làm bằng chứng.

## 3. B' — dự báo có chu kỳ (đúng 5 biến thể; Bonferroni 5 ⇒ dùng 99% khi cần CI mô tả)
1. `D0tc8` = roe_tc8 · E/4; roe_tc8 = TB ROE_ttm của ≤ 32 quý gần nhất (gồm hiện tại, cần ≥ 16) — ROE "xuyên chu kỳ" 8 năm thay 5 năm.
2. `MRph` = MR với tốc độ φ theo ô (tercile cyc × pha) = 9 ô: φ_ô = hệ số OLS qua gốc của (ROE_ttm,q+4 − tc5) theo (ROE_ttm,q − tc5), chỉ trên gốc IS có K_A4 ≤ 2019-12-31, clip [0; 1]; ô < 100 quan sát ⇒ φ = 0,65 (mặc định J2). Dự báo E·[tc5 + φ^{h/4}(ρ − tc5)]/4.
3. `ENSph` = trung vị(SRWD, MxR, MRph).
4. `COMMF` (chỉ COMM) = NP_P{4−h} + β·c·Rev_P{4−h}; c = log(TB 3 tháng biết gần nhất tại K / TB cùng 3 tháng năm trước) của chuỗi họ; β gộp 1 hệ số OLS trên gốc IS (K_A_h ≤ 2019-12-31), mục tiêu (A − NP_P{4−h})/Rev_P{4−h} (winsor 1/99).
5. `ENScm` = trung vị(SRWD, MxR, MRph, COMMF) cho COMM; = ENSph ngoài COMM.
Thước: R vs SRW và **R vs ENS** (cặp, cùng mẫu) theo quý → trung bình nhân; tách nhóm. "Chu kỳ giúp dự báo" ⇔ R(ENSph/ENS) < 1 ở IS VÀ OOS với sign-count năm OOS ≥ 5/7 (h = 1); riêng COMM: R(ENScm/ENS) < 1 cả 2 era và ≥ 5/7 năm OOS. Ngược lại ⇒ NO-GO, báo thẳng.
Null bắt buộc: SRW (naive mùa vụ), −ROE_ttm (đã ở B), E/P, B/P (ở C').

## 4. C' — tâm D0 chu kỳ-hoá (chỉ đổi roe_n, như §4 PRELOCK)
- `C4` roe_n = roe_tc8 · `C5` roe_n = tc5 + φ_ô·(ROE_ttm − tc5) (ROE chuẩn hoá 1 năm theo pha, φ từ B'.2). Tham chiếu: D0, C2 (J3), EP.
- Đo bằng `d_metrics2.py` V3.1 (md5 `1b8d9c3af29deb223816450a404b1313`) phạm vi ALL h50, trên (i) toàn universe, (ii) chỉ COMM+CYC_HI, (iii) phần còn lại — (ii)/(iii) bằng cách che `in_universe` ⇒ chuẩn EW và IC tính TRONG tập con (ghi rõ).
- Tiêu chí "đáng nghiên cứu tiếp": ΔIC36 vs D0 > 0 ở ≥ 4/6 năm IS và ≥ 3/4 năm OOS, ∧ U-hit/O_right_rel không tệ hơn 5pp, ∧ IC36 OOS ≥ E/P. PBO CSCV trên IC36 năm {D0, C2, C4, C5}; DSR trên chuỗi ΔIC36 năm với N thử = 7 (5 dự báo + 2 định giá). Chỉ tham khảo.

## 5. N độc lập — nói thẳng
- Đơn vị độc lập của phần chu kỳ = **năm × họ/nhóm**, không phải dòng. COMM: 5 họ, ~19 mã, ≤ 12 năm ⇒ tối đa ~60 ô họ-năm, và các họ tương quan (dầu–urê–DAP cùng chu kỳ năng lượng).
- Số chu kỳ lớn VN trong mẫu (đỉnh/đáy 2015, 2018, 2020, 2022): **~2–3 chu kỳ đầy đủ**; pha PEAK/TROUGH của từng mã tương quan chéo mạnh theo năm ⇒ mọi kết luận theo pha là MÔ TẢ, N thật ≈ số năm.
- Embargo: mọi fit (φ, β) chỉ dùng mục tiêu thực hiện ≤ 2019-12-31; OOS từ K ≥ 2020-01-01.
- Không tự xưng CONFIRMED; không tín hiệu mua/bán; không wire.
