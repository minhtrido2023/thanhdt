# PRELOCK — V_ngắn có thông tin BỔ SUNG so với V_dài và so với "co về giá"? (job Taylor_20261111_043843)
Ghi 2026-11-11 11:40 ICT, TRƯỚC khi chạy bất kỳ rank IC / partial IC nào. Không đổi sau khi thấy số.
Nền: research/dd_blend_20261111 (panel `out/panel.parquet` md5 ghi ở out/inputs_md5.txt, TÁI DÙNG, không dựng lại)
+ verdict quant-skeptic logs/verify_20261111_042238_1862901.log (REFUTED w=0,5). Seed 20261111. User duyệt (b) 11:37 ICT.

## 0. Mẫu (F) — giữ nguyên job dd-blend
universe_pit in_universe tại phiên as-of, không-tài-chính, rating_8l ≤ 3 (merge_asof lùi), as-of cuối quý
2016Q1–2025Q4, fin.time ≤ as-of (assert ở build_panel), MC0 = Price_asof × CP fiinprox (fallback quy hệ CP quý fin).
Giá chỉ là NHÃN: x = log(V/MC0) dùng MC0 làm thước; y = log TR_N (Close đ/c, gồm cổ tức). Không profit_*, không ticker_prune.
Mẫu của biến thể v: {V_s^v > 0, V_l3 > 0, MC0 hữu hạn, full_N}. Kiểm bền: giao của mọi biến thể (cùng dòng).
IS = as-of 2016–2019; OOS = as-of 2020+.

## 1. Thước đo (A) — bất biến thang đo
- Theo từng quý as-of q (chỉ quý có ≥ 20 dòng): IC_q = Spearman(x, y_dm), y_dm = log TR_N − trung vị quý
  (Spearman trong quý bất biến với phép trừ hằng ⇒ y_dm chỉ để minh bạch). IC = trung bình IC_q theo quý.
- Partial (chính): trong mỗi quý, chuẩn hoá hạng (z của rank) của y, x_s = log(V_s/MC0), x_l = log(V_l/MC0);
  OLS z(y) ~ z(x_s) + z(x_l) ⇒ β_s,q, β_l,q (hệ số chuẩn hoá). PIC_s = trung bình β_s,q theo quý; PIC_l tương tự.
  Báo thêm partial Spearman (tương quan phần dư) làm mô tả.
- CI95: bootstrap cụm theo MÃ (B=1000; rút mã có hoàn lại, giữ toàn bộ dòng của mã, tính lại IC_q trong mỗi quý
  rồi trung bình). Kiểm tra: cụm theo QUÝ (B=1000). Ghi chú: nhãn N>3 tháng chồng lấp giữa các quý ⇒ CI cụm quý lạc quan.
- Chân trời N ∈ {12, 24, 36, 60} tháng.

## 2. Chân kiểm soát co-về-giá (B)
- V_l^c = MC0·(V_l/MC0)^c. c(w) = IQR_IS(log V_hh(w)/MC0) / IQR_IS(log V_l/MC0) cho w ∈ lưới; thêm lưới c ∈ {0,25; 0,5; 0,65; 0,75}.
- CHỐT CHẶN cơ học: IC(V_l^c) phải BẰNG IC(V_l) (|Δ| < 1e-12) ở mọi N, mọi split, mọi c. Không bằng ⇒ code sai, dừng.
- Mô tả kèm (không dùng để quyết): AEdm và β của V_l^c, V_hh(w) như job trước — để cho thấy AEdm/β thưởng việc co.
- Baseline bắt buộc cho blend: V_dài thuần, V_ngắn thuần (rank IC). Thắng w=0 thôi là KHÔNG đủ.

## 3. Ổn định theo thời gian (C) — mô tả + dùng cho tiêu chí (iii)
- IC(V_s), IC(V_l), PIC_s, PIC_l theo từng NĂM as-of 2016–2025 (năm có ≥ 2 quý đủ nhãn), mọi N, CI cụm mã.
- Chế độ: OOS bỏ as-of 2020–2021 (tức as-of 2022+); toàn kỳ bỏ 2020–2021. Phân theo DT5G tại as-of (mô tả).

## 4. Tiêu chí kết luận (D) — trên biến thể CHÍNH v0
v0 = đúng V_ngắn của job dd-blend (NI trung vị TTM 3 năm · ROE3Y vendor, fallback ROE_Trailing · g/ROE cắt [0,1]).
"V_ngắn CÓ thông tin bổ sung ổn định" CHỈ KHI đủ cả ba:
 (i)  OOS: PIC_s > 0 và CI95 cụm-mã loại 0 ở ≥ 3/4 chân trời.
 (ii) IS: PIC_s điểm > 0 ở ≥ 3/4 chân trời.
 (iii) OOS bỏ as-of 2020–21 (as-of 2022+): PIC_s điểm > 0 ở MỌI chân trời có ≥ 6 quý đủ nhãn (≥20 dòng/quý),
      và phải có ≥ 2 chân trời như vậy (nếu < 2 ⇒ (iii) KHÔNG ĐẠT vì không kiểm được).
Ngược lại ⇒ "KHÔNG có thông tin bổ sung ổn định" ⇒ DD giữ V_ngắn hiển thị-chỉ (phương án (a)).
Nếu đạt (i)–(iii): w* ∈ {0; 0,1; …; 1} chọn theo IC(V_hh(w)) trung bình 4 N trên IS (hoà ≤ 0,002 ⇒ w nhỏ hơn);
chấm OOS: IC(w*) − IC(V_l) và IC(w*) − IC(V_s) phải có CI95 cụm-mã loại 0 (> 0) ở ≥ 3/4 N ⇒ mới đề xuất blend w*.
(Lưới w vẫn được chạy và báo mô tả kể cả khi (i)–(iii) không đạt; khi đó nó KHÔNG phải đề xuất.)

## 5. Biến thể V_ngắn (E) — 12 = 3 × 2 × 2
- NI: (a) trung vị TTM 3 năm [k=0..2] · (b) TTM hiện tại [k=0] · (c) trung bình 5 năm [k=0..4, cần ≥3 điểm].
- ROE: (v) ROE3Y vendor (fallback ROE_Trailing) · (s) tự tính = NI_variant / (BVPS × OShares) của dòng fin cuối
  (ticker_financial cache, ghép theo (mã, fin_time) lùi ≤ fin_time; vốn chủ ≤ 0 ⇒ không xác định).
  Kiểm đơn vị: trung vị ROE_s/ROE3Y phải trong [0,5; 2] (không thì dừng, sửa đơn vị — không tune).
- Cắt tái đầu tư b = g/ROE: [0, 1] · [0, 0,8].
- Quy tắc: kết luận chính là v0. Ngoài ra chọn v* = argmax trung bình 4N của PIC_s trên IS (12 biến thể). Nếu v* ≠ v0
  và v* đạt (i)–(iii) VÀ PBO(CSCV, 12 biến thể, khối = năm as-of 2016–2023, metric PIC_s N=12 và N=36) < 0,5 ⇒ báo
  "có thông tin bổ sung ở biến thể v*" kèm nhãn chọn-từ-12; nếu không ⇒ kết luận theo v0.
- N trials (lựa chọn) = 12 biến thể + 11 w = 23. Đánh giá phụ (năm, DT5G, c) là mô tả, không chọn.

## 6. Forward thật (G)
`calc/score_dd_zones_forward.py`: đọc kb/dd_price_zones.json, giữ rev cao nhất mỗi (mã, dd_date); giá tại dd_date =
price_ref (đ/cp, cùng hệ với center) và Close đ/c (BQ `ticker`) tại phiên ≤ dd_date và tại dd_date+N tháng (N ∈ {3,6,12,24,36});
x0 = log(price_ref/center); AE_N = |log(price_ref·TR_N/center)|; rank IC giữa các mã cùng nhóm dd_date (theo tháng dd_date)
cần ≥ 8 mã đủ N; cờ `insufficient_N`. Mốc chấm đầu tiên có nghĩa: 12 tháng sau dd_date (≈ 10–11/2027); 3 tháng (≈ 01–02/2027) chỉ mô tả.
Không chạy ra kết luận trong job này. Không ghi sổ, không sửa dd_price_zones.json.
