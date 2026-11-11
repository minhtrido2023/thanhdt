# PRELOCK — hệ số dung hoà w (job Taylor_20261111_040113)
Ghi 2026-11-11 ~11:20 ICT, TRƯỚC khi dựng panel mới / thấy bất kỳ số V(w) nào. Không đổi sau khi thấy số.
Nền: research/dd_vn_calib_20261111 (engine FCFE3y production, domestic_v2). Seed 20261111.

## 0. Sửa 3 điểm quant-skeptic
1. **Share-basis**: so sánh ở đơn vị VND (giá trị VỐN CHỦ), không per-share. Vốn hoá tại as-of
   MC0 = Price_asof (chưa đ/c) × số CP tại as-of từ `mike/data/fiinprox_oshares_pit_20260926.csv`
   (chuỗi theo ngày, neo ex-right — registry: đúng cho "vốn hoá tại ngày t"). V (VND) = FV_ps × OShares
   của chính dòng fin engine dùng (= giá trị vốn chủ, bất biến với số CP). Mã không có trong fiinprox:
   fallback MC0 = Price_finsession × OShares_fin × Close_asof/Close_finsession (quy giá về hệ CP của quý
   fin); báo riêng tỉ lệ dòng fallback và kết quả chỉ-fiinprox làm kiểm bền. Báo % dòng lệch >5% so với
   cách cũ (Price_asof × OShares_fin).
2. **K3 trung lập drift** (chính): đường giá tổng lợi suất TR_N = Close_{t+N}/Close_t (gồm cổ tức);
   V tiến theo r: V_N* = V·(1+r)^{N/12}. K3n_N = median|log(MC0·TR_N / V_N*)| ÷ median|log(MC0/V)|.
   Phụ: K3u_N = median|log(MC_{t+N} / V_{t+N})| ÷ median|log(MC0/V_t)| (V cập nhật tại quý as-of gần t+N,
   MC_{t+N} giá-thuần × CP fiinprox ngày đó). β_N = slope log TR_N ~ log(V/MC0). CI95 bootstrap cụm mã
   (B=1000) + cụm quý cho số chính.
3. **Nhãn sát ngưỡng**: CI chứa 1 (K3) hoặc chứa 0 (Δ so baseline) ⇒ ghi "yếu/chưa kết luận".

## 1. Hai nền (cùng r, g_exp, g_T của engine tại as-of — chỉ khác CƠ SỞ)
- V_dài = engine production: FCFE3y = (CF_OA_3Y + CF_Invest_3Y)/3, 5 năm + terminal (cap_rf). Biến thể
  FCFE5y = (CF_OA_5Y + CF_Invest_5Y)/5. Chọn 5y CHỈ KHI trên IS: IQR log(V/MC0) nhỏ hơn VÀ K3n36 ≤ của 3y.
- V_ngắn = LNST chuẩn hoá × (1 − g/ROE): NI_norm = trung vị các TTM năm (k=0,1,2 từ `_annual_series`
  của engine, PIT, ≥1 điểm) — trung vị 3 năm loại một lần/chu kỳ mà không cần gắn cờ thủ công.
  ROE = ROE3Y vendor (TB 3 năm, PIT theo fin.time), fallback ROE_Trailing; ROE ≤ 0 hoặc NI_norm ≤ 0 ⇒
  V_ngắn không xác định. Stage-1: NI_y = NI_norm(1+g_exp)^y, FCFE_y = NI_y(1 − clip(g_exp/ROE,0,1)).
  Terminal: NI_5(1+g_T)(1 − clip(g_T/ROE,0,1))/(r − g_T). Không dùng giá.
- Lớp fade ROIC→Ke theo moat + dự án mới NPV=0: KHÔNG có lịch sử PIT (moat_tags là nhãn hiện tại) ⇒
  KHÔNG kiểm định; V_dài backtest = engine thuần (bảo thủ: không thưởng moat). Ghi là hạn chế.
- Mẫu chính: universe_pit (in_universe đúng phiên as-of), không-tài-chính, rating_8l ≤ 3 (merge_asof lùi),
  as-of cuối quý 2016Q1–2025Q4, V_ngắn>0 VÀ V_dài>0 (giá đỡ chung). Báo độ phủ khi chỉ V_ngắn có.

## 2. Cấu trúc w (lưới w ∈ {0,0.1,…,1})
- A: w hằng theo chân trời N ∈ {12,24,36,60}: V = w·V_ngắn + (1−w)·V_dài.             11×4 = 44
- G: biến thể hình học log V = w·log V_ngắn + (1−w)·log V_dài.                       11×4 = 44
- B: w_i = w_lo + (w_hi−w_lo)·q_i, (w_lo,w_hi) ∈ {0,.25,.5,.75,1}², 2 định nghĩa q (PIT, không giá):
  q1 = clip(CF_OA_3Y / Σ NI TTM 3 năm, 0, 1) (chuyển hoá tiền); q2 = 1 − clip(CV các TTM năm ≤5, 0, 1)
  (ổn định lợi nhuận).                                                               25×2×4 = 200
- C: phân kỳ D = |log(V_ngắn/V_dài)| > τ, τ ∈ {log2, log3}: V = min(V_ngắn,V_dài) (tâm bảo thủ khi hai nền
  bất đồng), còn lại V(w*_A).                                                          2×4 = 8
- B+C: B tốt nhất + C.                                                                 2×4 = 8
- Chọn 3y/5y: 2. **N trials khai = 306.**

## 3. Tiêu chí chọn (trên IS = as-of 2016–2019) và kết luận (trên OOS = 2020+)
- Mục tiêu tại mỗi N: K3n_N nhỏ nhất, ràng buộc trung vị V/MC0 ∈ [0,75; 1,25] (ngoài = loại).
  Hoà (chênh ≤ 0,005) ⇒ cấu trúc đơn giản hơn (A < G < C < B < B+C), rồi w nhỏ hơn (nghiêng nền
  dòng tiền, bảo thủ).
- B/G/C chỉ thay A nếu cải thiện IS > 0,01 VÀ Δ OOS (B−A) có CI95 < 0. Ngược lại giữ A.
- "VƯỢT baseline": OOS Δ K3n_N(c*) − K3n_N(baseline) có CI95 bootstrap cụm mã < 0, với baseline =
  (i) production w=0, (ii) LNST thuần w=1, (iii) 50/50 hằng. Báo riêng từng baseline.
- "Hội tụ": K3n_N CI95 trên < 1. CI chứa 1 ⇒ "yếu/chưa kết luận".
- H1 (kiểm, không giả định): w*(12) ≥ w*(24) ≥ w*(36) ≥ w*(60) và w*(12) − w*(60) ≥ 0,2 ⇒ "ủng hộ";
  ngược lại nói thẳng "dữ liệu không ủng hộ".
- Walk-forward phụ: IS 2016–21 / OOS 2022+ (N ≤ 36). LOYO: chọn lại w*_A bỏ từng năm; báo dải.
- PBO (CSCV, khối = năm as-of 2016–2023, N=36, trials A+G+B). DSR không áp cho metric phi-lợi-suất ⇒ N/A.
- Ngành (mô tả): w*_A theo nhóm ICB (BĐS 86xx · Xây dựng/VLXD 235x · Tài nguyên & hàng hoá chu kỳ 0xxx/1xxx ·
  Tiêu dùng & bán lẻ 3xxx/53xx · Công nghệ 9xxx · Tiện ích 7xxx · Công nghiệp khác 2xxx · còn lại).
  Chỉ đề xuất w theo ngành nếu Δ K3n36 so với w* chung có CI < 0 trên OOS.
- Rule 0,85×tâm: tần suất kích hoạt theo phiên (V giữ tới quý sau, PIT) cho w ∈ {0, w*, 1}; % phương sai
  chỉ báo kích hoạt nằm GIỮA các mã (mức "chọn theo danh tính mã").
Giá chỉ là NHÃN (MC0 để chấm, đường giá sau as-of). Không profit_*. Không ticker_prune. Không tune r/g_T.
