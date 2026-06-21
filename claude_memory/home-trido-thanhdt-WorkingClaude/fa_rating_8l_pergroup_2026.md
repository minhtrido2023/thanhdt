# FA_rating ← 8L per-group ([REDACTED]07)

**Câu hỏi user**: dùng phân nhóm 8L (router bank/cyclical/power/compounder/RE/sec/ins) để cải thiện FA_rating (`tav2_bq.fa_ratings`, tier A–E) đang dùng trong các bản paper-trade V11/V12x. "Nếu integrated chưa tốt thì căn chỉnh lại rating cho hợp 8L."

## B1 — chẩn đoán per-group IC của FA phẳng hiện tại
FA cũ = composite 7 trục TRỌNG SỐ CỐ ĐỊNH, percentile TOÀN cohort, KHÔNG phân nhánh nhóm. Forward sạch (LEAD giá, point-in-time, KHÔNG dùng profit_*):
- **COMPOUNDER (n≈10k): đơn điệu HOÀN HẢO A→E** (med120 A+2.4→E−5.4, win .53→.42). Composite phẳng chạy tốt — đây là ~75% universe + lõi book.
- **CYCLICAL (n≈474): ĐẢO** — 120d D(+9.2)>C(+8.4)>A(+6.1). Tier thấp ở đáy chu kỳ = forward tốt nhất. FA phẳng vô dụng/hại đúng nhóm này.
- **POWER: nhiễu/đảo** (A tệ nhất). **BANK: A–D ổn** (A+8.6), chỉ E nhiễu n nhỏ.

## B2/B3 — dựng 8L 1–5 theo lịch sử + map A–E per-group
`rating_8l_history.py`: port `rate_row()` của `rating_8l.py` lên FULL ticker_financial history (52k rows). COMPOUNDER/CYCLICAL/RE/SEC/INS tái lập CHÍNH XÁC point-in-time; BANK proxy ROE-only (NPL là snapshot, không có history), POWER proxy lifecycle D/E. **Map A–E = per-group percentile**: COMPOUNDER xếp theo core_score trong cross-section TỪNG QUÝ (khôi phục E-floor cân bằng); nhóm nhỏ giữ rating rời rạc 1→A..5→E. Bảng BQ `tav2_bq.fa_ratings_8l` (A5163/B10354/C15767/D13664/E7484).
- IC rating MỚI: **CYCLICAL hết đảo** (B+5.7/.60 tốt nhất, D/E âm); **COMPOUNDER E-floor khôi phục** (win .547→.400 đơn điệu); BANK sạch (E-floor, 100% historical). SECURITIES vẫn đảo ở đỉnh (broker ROE cao=đỉnh chu kỳ) ⚠ nhỏ.
→ **8L per-group LÀ rating tốt hơn khi đứng RIÊNG.** ✅

## B4 — full-NAV V11 book (BAL+VN30=V1), prod-spec params, controlled A/B
2 signal pkl build từ cùng SIGNAL_V11 chỉ khác bảng FA. `run_fa8l_ab.py`:
- **Full −0.65pp** (17.16→16.51), Sharpe 1.18→1.14, **DD −20.4→−27.4**, Calmar 0.84→0.60.
- IS 2014-19 +2.81 nhưng **OOS 2020-now −4.22pp** (24.01→19.79), DD/Sharpe đều tệ hơn.
→ **THAY nguyên fa_tier trong book = THUA.** Book capacity-bound (12 slot) không hưởng; per-group đẩy thêm A/B value → lệch value, tụt sóng momentum-bull 2020+ (khớp "FA edge ZERO in BULL"). Tái xác nhận memory "BA-core momentum book RESISTS FA overlays".

## Cách tích hợp ĐÚNG (prior art `run_prodspec_rating_BC.py`, data/rating_8l_BC_prodspec.csv)
- **exclude5** (chặn cứng buy mã rating-5): V1 −0.60 ✗
- **regime_size** (giảm ½ size mã yếu rating≥4 CHỈ khi BEAR/CRISIS state≤2 qua `tier_weights_by_state`): **V1 +0.80, V5 +0.97, MỌI hệ CAGR+Sharpe+DD+Calmar tốt hơn** ✅✅ = "FA matters in stress".

## B5 — regime_size: weak-flag rating≥4 (tuyệt đối) vs tier D/E (tương đối)
`run_fa8l_regime.py` (book V11, cùng harness, chỉ đổi weak-flag):
- **regime_oldR (rating≥4)**: Full **+0.73** (17.18→17.92), **OOS +0.84** (23.96→24.79), Sharpe↑ DD bằng/tốt → tái lập prior-art ✅
- **regime_DE (tier D/E)**: Full +0.06, **OOS −0.45**, DD tệ hơn → **THUA** ✗
→ **INSIGHT**: percentile TƯƠNG ĐỐI (D/E, đáy nhóm) hợp XẾP HẠNG (so peer) nhưng SAI cho phòng-thủ-size — fragility là chuyện TUYỆT ĐỐI (ROIC/đòn bẩy/FSCORE ngưỡng cứng), không tương đối. rating≥4 (tuyệt đối) bắt đúng mã mong manh khi stress. **Dùng nhầm vai làm mất lợi ích.**

## CHỐT
8L per-group cải thiện FA THẬT, nhưng **không thay cổng A/E** (thua −4.22pp OOS) **mà điều tiết SIZE theo regime** (thắng +0.73/+0.84). VÀ phải dùng ĐÚNG calibration cho đúng vai:
1. **Screener/dna_card/bot** → adopt `fa_ratings_8l` (percentile tương đối, xếp hạng trong peer). ✅
2. **Book V11/V12x** → regime_size với **rating 8L TUYỆT ĐỐI ≥4** (cột `rating` trong panel, KHÔNG phải tier D/E percentile), giảm ½ size khi BEAR/CRISIS. KHÔNG thay fa_tier. ✅
Files: rating_8l_history.py, build_fa8l_pkls.py, run_fa8l_ab.py (thay-cổng=thua), run_fa8l_regime.py (size: oldR thắng/DE thua), data/fa8l_{ab,regime}_navs.csv, BQ fa_ratings_8l.

## DEPLOYED ([REDACTED]07)
- **Screener/bot (A)**: ĐÃ sẵn — `unified_screener.py` đọc `data/rating_8l.csv` (rating per-group 1-5 từ rating_8l.py live, có real bank NPL). **+ Thêm cột `grade` ([REDACTED]07): IG=rating≤3 / SPEC=4 / AVOID=5** + shortlist "INVESTMENT-GRADE buy-zone" & "SPECULATIVE buy-zone" + chú giải. Ngưỡng ≤3 (KHÔNG phải ≤4) là lằn ranh đầu-tư-vs-đầu-cơ đã validate (≤3 dip +9-13%/win 61-67%; 4 chỉ +1.8-5% catalyst-only). exclude5 trên BOOK = vô tác dụng (−0.05pp Full, mã rating-5 hầu như không phát tín hiệu momentum). regime_size vẫn là lever book tốt nhất (+0.73).
- **Book (B) — regime_size wired**: helper `regime_size_overlay.py` (`apply_regime_size`: as-of merge rating tuyệt đối từ BQ `fa_ratings_8l`, split mã rating≥4 → `<tier>_W`, `tier_weights_by_state` halve 5% khi state≤2). Wired vào TẤT CẢ paper-trade trong papertrade_daily.bat: **pt_v11_tq34b, pt_v12_macro, pt_v121_ensemble, pt_v121_ens_q2, pt_v4_dt5g** (+ pt_v12_tq34b/pt_v12_live ngoài bat). Smoke-test cả 5: chạy sạch, coverage 99%, 9 mã weak, **dormant (NEUTRAL) → NAV không đổi** (BAL 25.4573B). An toàn, không phá thí nghiệm Apr–Sept.
- **golive_recommend.py KHÔNG sửa**: chỉ sinh entry MỚI; BEAR/CRISIS đã chặn vào lệnh (AVOID_bear) → regime_size (trim vị thế GIỮ khi stress) ngoài phạm vi recommender — đúng thiết kế.
- **Bảng `fa_ratings_8l` (ticker,time,route,rating,tier)**: tự refresh trong `rating_8l_history.py::refresh_bq_table` (1 lệnh refresh CSV+BQ). Re-run khi có quý tài chính mới (như fa_ratings). Hiện current tới [REDACTED]28.
- Weak-flag = rating TUYỆT ĐỐI≥4 (KHÔNG phải tier D/E percentile — đã chứng minh thua).

## B6 — financials có bị "bỏ qua" khi giữ flat fa ở cổng-vào? ([REDACTED]07)
Snapshot book universe: BANK 25 mã (chỉ 1 E-block, 11 ở A/B) + INSURANCE 9 (0 E-block) = KHÔNG bị bỏ qua, vẫn trade — chỉ MIS-RANK (flat chấm bằng trục sai: ABB flatC/8L1, BVB flatC/8L5). SECURITIES 35 mã = bị dìm hệ thống (0 lên A/B, 9 E-block) NHƯNG có lý (8L securities cũng đảo ở đỉnh, siêu chu kỳ).
**Bank-only swap test** (`run_fa8l_bankonly.py`, bảng tạm fa_ratings_bankhyb đã drop): bank lấy 8L, còn lại flat → Full **−0.35**, OOS **−0.71**, IS −0.01, DD nhỉnh hơn tí (−20.0) → net âm nhẹ, KHÔNG deploy. Nhẹ hơn nhiều thay-toàn-bộ (OOS −0.71 vs −4.22) nhưng vẫn không ăn: bank sector-8 cap 4 = thiểu số, book TA-driven hấp thụ, 8L bank=proxy-ROE đẩy thêm E-block. **KHẲNG ĐỊNH: book kháng MỌI thay rating ở cổng-vào kể cả phẫu thuật từng nhóm.** Financials được soi đúng ở screener (NPL/CAR) + regime_size (size bank yếu khi stress) — KHÔNG bị bỏ qua. Giữ flat ở cổng-vào là tối ưu.

## B7 — regime_size × capitulation overlay ([REDACTED]07)
Fold regime_size vào run_5systems_prodspec (env `REGIME_SIZE`, mặc định OFF→core gốc nguyên; file `_dt5g_rs`). V5 regime_size baseline 25.12% (vs gốc 25.51, −0.39 CAGR nhưng **MaxDD −24.7→−23.1 tốt hơn** = insurance). Overlay capitulation+grind (`final_overlay_realcash.py`, EXTENDED-GRINDHALF f=cash, addition-model lý tưởng, capitulation đang SHADOW chưa deploy): V5 gốc 35.15% vs regime_size 34.73% → **regime_size & capitulation GIẪM CHÂN** (cùng kích hoạt BEAR/CRISIS: RS phòng thủ giảm size, capit tấn công bơm cash).
**RS-off-in-capitulation test**: ⚠️ **SPLICE = DƯƠNG TÍNH GIẢ.** Splice returns (đổi nguyên path no-RS trong cửa sổ 60d) gợi ý hybrid 35.37% (best) NHƯNG chạy END-TO-END qua simulator thật (hook mới `regime_suppress_dates`: un-halve trọng số _W đúng ngày, giữ path RS) = **34.45% = TỆ NHẤT** (un-halve mã yếu đúng lúc washout rơi + ít cash hơn cho overlay = 2 cái hại path-dependent splice bỏ qua). **CHỐT: regime_size & capitulation là HÀNG THAY THẾ (XOR), không bổ trợ.** Khi deploy capitulation → TẮT regime_size (RS-never +cap = 35.15 best). Bây giờ chưa capitulation → giữ regime_size BẬT (DD độc lập). Hạ tầng đã gói dormant (simulator `regime_suppress_dates`, `build_capit_suppress_windows`, env `CAPIT_SUPPRESS`) nhưng policy window-suppress KHÔNG khuyến nghị. **Bài học: luôn validate end-to-end, đừng tin splice/addition-approx.** Files: run_5systems_prodspec.py(+REGIME_SIZE/CAPIT_SUPPRESS env), regime_size_overlay.py, test_regime_off_in_capitulation.py(splice-FALSE+), final_overlay_realcash_{rs,rscap}.py, cores _dt5g_{rs,rscap}.
