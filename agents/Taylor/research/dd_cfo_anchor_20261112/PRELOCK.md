# PRELOCK — dd_cfo_anchor_20261112 (job Taylor_20261111_095819)

Khoá TRƯỚC mọi lần tính IC/PIC/hồi quy định giá của job này. Đã làm trước khoá: dựng `out/ext2.parquet`
(chuỗi năm TTM CFO/capex/LNST/doanh thu, NWC, ROIC3Y, ADV60, nhãn TR3/TR6) và kiểm đơn vị KHÔNG nhãn
(CFO cuốn 3 năm / CF_OA_3Y trung vị 0,99, IQR 0,61–1,25; DA ≤ 0 ở 10,5% dòng; CF_OA_3Y/NI3 trung vị 0,80).

**Đã BIẾT trước khoá (từ các job trước, thiên lệch chọn ứng viên phải khai):** dd_fcfe3y_decay: CFO3/MC0 giữ
PIC OOS +0,15…+0,20; capex/CFO dự báo DƯƠNG OOS; accrual (NI−CFO)/TA dự báo ÂM OOS; C4 = CFO3 − min(capex, DA)
Δ OOS dương 4/4 N (N≥12 tháng) nhưng CI mã 2/4. dd_fwd_prelock: V_ngắn PIC ≈ 0 IS, dương OOS. Chưa từng đo
chân trời 3/6 tháng; chưa từng đo A/B/C/D/E dưới đây.

## Dữ liệu
- Panel `dd_blend_20261111/out/panel.parquet` (md5 1de5145f42281f9b3bf5e940064e473c; universe_pit, phi tài chính,
  as-of cuối quý 2016Q1–2025Q4, BCTC fin_time ≤ as-of) + `dd_fcfe3y_decay_20261111/out/ext.parquet` + `out/ext2.parquet`.
- MC0 = Price_asof × số CP fiinprox tại as-of (fallback quy về hệ CP quý fin) — bản đã sửa share-basis.
- Nhãn y = log TR_N (Close điều chỉnh). **Chân trời chính N ∈ {3, 6, 12} tháng**; phụ (mô tả) {24, 36}.

## Ký hiệu (tất cả VND, PIT)
NI3 = tổng 3 LNST năm tài chính gần nhất (annual_np[:3]); NI_norm = trung vị 3 năm đó (= nền V_ngắn).
CFO3 = CF_OA_3Y (tổng 3 năm TC), CPX3 = −CF_Invest_3Y, CPX5 = −CF_Invest_5Y.
cfo_yj = CFO TTM kết thúc quý q0−4j (j=0..4, cuốn theo quý). DA = EBITDA_P0 − EBITM_P0 × DT TTM (>0, ngược lại NaN).
ROE = ROE3Y (fallback ROE TTM); ROIC = ROIC3Y (fallback ROE). r, g_exp, g_T = engine (domestic_v2).
V(base, b) = DCF 2 giai đoạn của engine (5 năm g_exp, rồi g_T), dòng tiền = base × (1 − b). b_E = clip(g/ROE, 0, 0,8),
b_I = clip(g/ROIC, 0, 0,8) (g = g_exp giai đoạn 1, g_T giai đoạn cuối).

## Ứng viên (9 trial lựa chọn)
| Mã | Nền | b |
|---|---|---|
| A1 | NI_norm × clip(CFO3/NI3, 0, 1)  (NI3>0) | b_E |
| A2 | min(NI3, CFO3)/3 | b_E |
| B3 | trung vị(cfo_y0..y2) | b_I |
| B5 | trung vị(cfo_y0..y4) | b_I |
| C1 | NI3/3 + DA − min(CPX3/3, DA) | b_E |
| C2 | C1 − (NWC_q0 − NWC_q0−12)/3, NWC = tồn kho + phải thu − (nợ NH − vay NH) | b_E |
| D1 | CFO3/3 − CPX5/5 | 0 (như engine) |
| D2 | CFO3/3 − m_grp,q × DT TTM, m = trung vị chéo-mã (cùng quý as-of, cùng nhóm ngành) của CPX3/DT3 năm | 0 |
| E | w·V_earn + (1−w)·V_cash; V_earn = V(NI_norm, b_E); V_cash = V(CFO3/3 − min(CPX3/3, DA), 0) (= C4); w = (a+b+c)/3: a) CFO3/NI3 ≥ 0,8; b) cfo_y0, y1, y2 đều > 0; c) \|NI_TTM − CFO_TTM\|/tổng TS ≤ 0,10 | – |
Nền ≤ 0 hoặc thiếu ⇒ không định nghĩa (không có V).

## Baseline và chân điều khiển
- BL_F = V_dài production (FCFE3y, V_l3). BL_S = V_ngắn (V_s, b clip[0,1]). BL_C4 = V_cash ở trên.
- **K_shrink** (co về giá thuần): X^c = MC0^(1−c)·X^c, c ∈ {0,25; 0,5; 0,75}. Rank IC bất biến ⇒ assert IC(X^c) = IC(X)
  (1e-12) cho mọi ứng viên; nghĩa là rank IC không thưởng việc co về giá.
- **K_blend** (co về giá bằng trộn cố định, KHÔNG thông tin mới) = 0,5·V_s + 0,5·V_l3 (blend dd_blend đã bị REFUTED là chỉ co về giá).
- **E_const** = w̄·V_earn + (1−w̄)·V_cash, w̄ = trung bình w trên dòng M0 IS (hằng số, tính không nhãn) — chân điều khiển riêng của E.

## Mẫu
- M0 = rating≤3 ∧ MC0 hữu hạn ∧ V_l3>0 ∧ V_s>0 (mẫu các job trước). **Đánh giá chính trên Mx = M0 ∩ {X>0} ∩ {K_blend hữu hạn}**,
  so cùng dòng với baseline. Mô tả kèm: hỗ trợ riêng (rating≤3 ∧ X>0, không đòi V_l3>0) + độ phủ.
- IS = as-of 2016–2019; OOS = 2020+. Quý < 20 dòng bị bỏ.

## Thước đo
- IC(X) = Spearman(log X/MC0, log TR_N) mỗi quý, trung bình quý. PIC(X|K) = hệ số chuẩn hoá của X trong hồi quy hạng
  (X, K) mỗi quý. CI95: bootstrap cụm MÃ (B=1000) và bootstrap KHỐI NĂM (rút năm có hoàn lại). N độc lập = số quý
  (N=3 không chồng lấp; 6, 12 chồng lấp ⇒ dùng CI khối năm cho kết luận thời gian).

## Tiêu chí ĐẠT (khoá) — trên chân trời chính {3, 6, 12}
- **T1 ổn định IS/OOS:** IC(X) IS điểm > 0 ở ≥2/3 N; OOS IC > 0 ở 3/3 N và CI mã loại 0 ở ≥2/3 N.
- **T2 vượt chân co-về-giá:** PIC(X | K_blend) toàn kỳ > 0 với CI mã loại 0 ở ≥2/3 N; và PIC(X|K_blend) điểm > 0 ở CẢ IS
  lẫn OOS ở ≥2/3 N. Riêng E: thêm ΔIC(E − E_const) toàn kỳ > 0 điểm ở ≥2/3 N.
- **T3 LOYO:** IC toàn kỳ bỏ lần lượt từng năm as-of luôn > 0 ở 3/3 N; bỏ 2 năm có IC cao nhất vẫn > 0 ở ≥2/3 N.
- **T4 cụm thời gian:** IC toàn kỳ CI khối năm loại 0 ở ≥2/3 N.
- **T5 BH-FDR:** p một phía của PIC(X|K_blend) toàn kỳ (tỉ lệ mẫu bootstrap mã ≤ 0, sàn 1/B) — BH q=0,10 trên họ 9 ứng
  viên, riêng từng N; phải sống ở ≥2/3 N.
- ⇒ **HIỂN THỊ được (display-only, cạnh V_dài)** nếu đạt T1–T5.
- **T6 thay V_dài:** ΔIC(X − BL_F) OOS > 0 với CI mã loại 0 ở ≥2/3 N; ΔIC IS ≥ −0,03 điểm ở mọi N; PBO (CSCV trên IC theo
  năm 2016–2025, 9 ứng viên + 3 baseline, N=6) < 0,5; t-thống kê (IC toàn kỳ / SE khối năm, N=6) của ứng viên > E[max Z]
  của 9 trial (deflate trong họ). Báo kèm E[max Z] cho 434 trial cộng dồn (chỉ thông tin, không chấm).
  ⇒ **Đủ để THAY V_dài** nếu đạt T1–T6. Nhiều ứng viên đạt ⇒ chọn IC IS trung bình 3 N cao nhất trong nhóm đạt.
- Không ứng viên nào đạt T1–T5 ⇒ "chưa đủ bằng chứng, giữ nguyên".

## Đòn tấn công tự kiểm (mô tả, không chấm; báo nếu đổi kết luận)
Bỏ BĐS; bỏ tercile ADV60 thấp nhất mỗi quý; chỉ dòng MC0 fiinprox (share-basis); dòng thiếu nhãn (sống sót) đếm theo N;
one-off: so A1 (trung vị) với A2 (trung bình); hỗ trợ riêng (độ phủ lớn hơn) có giữ dấu không.

## Q4 — luận điểm "thị trường định giá theo LN + chất lượng LN" (mô tả, không chấm trial)
(i) Mỗi as-of Q4 2016–2025, chéo mã toàn panel (mọi rating) có NI_norm>0 ∧ CFO3>0 ∧ FCFE3>0: OLS log MC0 ~
  M1 log NI_norm · M2 log NI_norm + clip(CFO3/NI3, −1, 3) · M3 log(CFO3/3) · M4 log FCFE3 · M5 log NI_norm + log FCFE3;
  R² có và không FE nhóm ngành; so trung bình 2016–19 vs 2020–25.
(ii) Thưởng định giá cho chất lượng: log(MC0/NI_norm) (NI_norm>0) ~ chỉ báo tercile CFO3/NI3 trong năm (cao vs thấp)
  + FE nhóm ngành + log1p(g_exp) + ROE; theo năm và gộp 2016–19 / 2020–25; CI bootstrap cụm mã.

## Đếm trials & tái lập
Lựa chọn: 9 (A1, A2, B3, B5, C1, C2, D1, D2, E). Q4 và đòn tấn công là mô tả. Cộng dồn chuỗi DD: 425 + 9 = 434.
Chạy analyze 2 lần md5 trùng; tái tính độc lập 3–5 mã từ ticker_financial gốc cho A1, B3, C1, D1, E.
