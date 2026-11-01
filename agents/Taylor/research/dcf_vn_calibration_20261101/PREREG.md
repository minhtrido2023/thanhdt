# PREREG — Hiệu chuẩn DCF cho thị trường VN (job Taylor_20261101_155145)
Viết 2026-11-01 22:55 ICT, TRƯỚC khi chạy bất kỳ số nào của nghiên cứu này. R&D, không wire production,
không sửa default `dcf_valuation.py`.

## 0. Những gì ĐÃ biết trước (không mù — khai để skeptic trừ hao)
- Code hiện hành (domestic_v2): r = 12,25% hằng cho MỌI mã (không beta); base FCFE = (CF_OA_3Y+CF_Invest_3Y)/3;
  g_raw = TB 3 tăng trưởng năm TTM NP; kẹp [−2%, +20%]; g_exp = g_T + 0,5·(g_clamp − g_T); 5 năm; Gordon
  (1+g_T)/(r−g_T), g_T = min(CPI5Y + GDP15Y, 5,5%).
- Study A (07-2026): tăng trưởng quá khứ dự báo NGƯỢC tăng trưởng năm sau (rank-IC −0,10 IS / −0,20 OOS).
- ERP v2: IC MoS 4 quý ≈ 0,059 và KHÔNG đổi giữa các khung r/g_T (g_T/r chung cho mọi mã ⇒ trôi khỏi rank).
  ⇒ Dự đoán trước: mọi thay đổi THAM SỐ CHUNG (g_T, ERP, N, fade đồng loạt) chủ yếu là LEVEL, IC đổi ít.
  Chỉ tham số KHÁC NHAU GIỮA MÃ (beta riêng, growth theo nhóm, shrink) mới có thể đổi IC.
- `risk_rating.Beta` là BIN 1–5 (84% NaN) — không phải beta thô; chỉ đối chiếu dạng thứ hạng.
- Beta tuần trung bình theo regime ~0,34–0,55 (asymmetric_beta_regime.md) ⇒ dự đoán beta raw VN thấp hơn 1 nhiều
  do không đồng bộ giao dịch; Dimson/tuần sẽ cao hơn ngày.

## 1. Dữ liệu (đã tra `kb/data_registry/`)
- `ticker_financial` (CANONICAL; `time` = ngày công bố ở 99,2% dòng có `Release_Date`; dòng NULL `Release_Date`
  là placeholder cuối quý +32..35 ngày). OShares = TRAP (restate) — dùng OShares quý như MỌI nghiên cứu DCF
  trước (pin_oshares_source_fin) để so sánh được; ghi là điểm yếu, kiểm độ bền bằng cách loại ticker-date có
  OShares đổi >10% trong ±4 quý.
- Giá: `data/bq_cache/ticker/*.parquet` (2013→2026-10-30): `Price` thô cho MoS (đúng production), `Close` điều
  chỉnh cho lợi suất/beta. VNINDEX, VN30 có; VNALL KHÔNG có trong cache (ghi rõ, không thay thế).
- Universe: `universe_pit` (CANONICAL, ruleset 1) `in_universe` tại ngày đánh giá. Không dùng ticker_prune.
- Tài chính loại: `dcf_valuation.is_financial` (route 8L PIT, fallback ICB).
- Vintage ticker_financial: 2026-07-08, 07-28, 07-29, 10-30 (đo trễ nạp dữ liệu vendor).
- Không dùng `profit_*`.

## 2. Engine
Viết lại `fair_value` dạng vector (cùng công thức). **Selfcheck bắt buộc**: tái lập `dcf_valuation.fair_value`
(frame domestic_v2, OShares fin) trên ≥300 cặp (ticker, asof) ngẫu nhiên seed 20261101: |ΔFV| = 0 VND (dung sai
1e-6 tương đối). Trượt ⇒ dừng.

Ngày đánh giá: cuối tháng (phiên cuối), 2014-01 → 2025-10 cho IC 12T; tới 2026-10 cho level. IS 2014-2019,
OOS 2020+. Lợi suất kỳ hạn: Close(t+h)/Close(t)−1, h = 3, 6, 12 tháng. IC = Spearman MoS vs lợi suất trong mỗi ngày.
**N độc lập**: IC 12T trên ngày tháng chồng lấp ⇒ N hiệu dụng = số NĂM (12 cửa sổ không chồng lấp, 2014–2025);
IC 3T ⇒ N = số QUÝ không chồng lấp. Sai số chuẩn: Newey-West lag = h−1 tháng; CI bootstrap khối theo NĂM.

## 3. Vấn đề 1 — thời điểm chạy
(a) Trễ công bố = Release_Date − cuối quý (chỉ dòng có Release_Date), theo quý Q1..Q4, 2014+ vs 2020+; p50/p80/p90/p95,
    % trước hạn luật (Q1-Q3: 30 ngày hợp nhất; Q2 soát xét 45; Q4 kiểm toán 90; NOTE: BCTC quý 4 chưa kiểm toán thường
    công bố ~30 ngày, kiểm toán năm ~90 ngày — dòng nào vendor ghi làm "Q4" sẽ được xác định từ số liệu).
    Trễ nạp vendor: % dòng có Release_Date ≤ V có mặt trong vintage V.
(b) Tuổi BCTC = t − time của dòng mới nhất ≤ t. Nhóm 0–30 / 31–60 / 61–90 / >90.
    - Sai số dự báo cơ bản: dự báo NP 1 năm = TTM NP_last × (1+g_exp); thực hiện = TTM NP của dòng mới nhất công
      bố ≤ t+365. Sai số = |log(thực/dự)| (cả hai >0). Tương tự FCFE: base_fcfe·(1+g_exp) vs TTM FCFE (CF_OA_P0..3 +
      CF_Invest_P0..3) dòng ≤ t+365 (thực ≤0 ⇒ tính tỷ lệ "sai dấu"). Báo trung vị theo nhóm tuổi + trong cùng mã
      (hiệu ứng cố định ticker×năm) để tách chất lượng "nộp muộn".
    - IC MoS (3T) theo nhóm tuổi: pooled theo nhóm trong mỗi ngày có ≥30 mã/nhóm; báo theo nhóm.
(c) Lịch đề xuất suy từ (a): cửa sổ chạy = từ ngày p80 trễ công bố tới p95 + trễ nạp. Cờ STALE: tuổi > ngưỡng = p95
    trễ công bố của quý kế tiếp + 15 ngày (khai số khi có (a)). Chạy lại giữa quý: so sánh mức đổi MoS do giá vs do
    BCTC mới (tỷ trọng phương sai) — luật: nếu giá đóng góp > BCTC thì MoS phải tính lại theo giá hằng ngày (đã là
    hành vi on-demand của dcf_check), còn FV chỉ đổi khi có BCTC.

## 4. Vấn đề 2 — beta
Ngày ước lượng: cuối quý 2014Q4 → 2025Q3 (5Y cần 2009+: nếu giá trước 2013 không có trong cache thì lấy BQ
`tav2_bq.ticker` time,ticker,Close 2008–2012; không được thì 5Y chỉ từ 2018 và ghi rõ).
Mã: universe_pit tại ngày ước lượng, ≥ 70% phiên có giao dịch trong cửa sổ.
Biến thể (khai đủ để đếm N trials): tần suất {ngày, tuần W-FRI không chồng lấp, tháng} × cửa sổ {1,2,3,5 năm} ×
kỹ thuật {OLS, Blume 0,67β+0,33, Vasicek (về TB cắt ngang, dùng SE), Dimson (lag −1..+1; ngày và tuần),
Scholes-Williams (ngày)} × benchmark {VNINDEX, VN30} + bottom-up ngành (trung vị beta tuần 2Y Vasicek theo ICB cấp 2,
loại chính mã) + hằng 1,0.
"Sự thật" (khai trước): beta 12 tháng KẾ TIẾP = Dimson tuần (lag 0,1) vs VNINDEX, 52 tuần. Phụ: OLS ngày 12T kế tiếp.
Tiêu chí OOS (2020+ là chính, IS báo kèm):
 (i) Spearman(beta dự báo, beta thật) trung bình theo quý; MSE mức (beta dự − thật)² — level quan trọng cho Ke.
 (ii) Spearman(beta dự báo, lợi suất cộng dồn của mã trong các TUẦN VNINDEX giảm, 12T kế tiếp) (càng âm càng tốt) +
     đặc biệt các pha hạ: 2018-04→2018-07, 2020-01→2020-03, 2022-04→2022-11.
 (iii) FV/MoS: r_i = 6,75 + β_i·5,5 (β đã kẹp), so với r hằng: FV median, %RẺ, IC MoS 3/12T.
Chọn: biến thể có MSE thấp nhất OOS mà Spearman không kém nhất >0,02; kẹp sàn/trần = p5/p95 của beta thật.
Quyết định "beta riêng hay hằng": dùng beta riêng CHỈ KHI (iii) IC MoS OOS cải thiện ≥ +0,01 so với r hằng VÀ không
xấu đi IS; ngược lại kết luận beta riêng chỉ là DISPLAY (Ke hiển thị), giữ r hằng cho xếp hạng.

## 5. Vấn đề 3 — giai đoạn & tăng trưởng
(a) Panel năm: TTM NP tại cùng quý mỗi năm (dòng PIT). Tăng trưởng g = NP_t/NP_{t−1}−1 (NP_{t−1}>0). Tốc độ trở về:
    hồi quy cắt ngang g_{t+k} lên g_t (k=1..5) và lên g_trailing3Y; phần trăm nhóm top-quintile tăng trưởng còn
    top-quintile sau k năm; CAGR k năm theo nhóm: ROE5Y (tam phân), quy mô (vốn hoá tam phân), ICB cấp 1,
    "tuổi tăng trưởng" (số năm liên tiếp g>15%). 2008+ (thị trường mỏng trước 2008).
(b) Biến thể đường tăng trưởng (thử, đếm N trials):
    2-stage N ∈ {3,5,7,10}; 3-stage nhanh N1 ∈ {3,5} + fade tuyến tính N2 ∈ {3,5,7}; H-model (half-life H ∈ {2,3,5});
    shrink ∈ {0, 0,25, 0,5, 0,75, 1}; base growth = TB 3Y (hiện tại) vs hệ số hồi quy đo ở (a) (shrink "kinh nghiệm"
    hiệu chuẩn IS, áp OOS).
    Tiêu chí KHÔNG phải giá: sai số |log(Σ NP thực năm 1..K / Σ NP dự năm 1..K)|, K=3 và 5 (dữ liệu tới 2026-10).
    Rồi IC MoS và level (median P/FV, %RẺ).
(c) g_T ∈ {4,5; 5; 5,5; 6; 7}%. Nhất quán: FCFE_terminal = NI·(1 − g/ROE_T), ROE_T ∈ {Ke, ROE5Y hội tụ về Ke}.
    Đo trung vị FCFE/NI dài hạn và tỷ lệ chi trả VN để kiểm tính hợp lý.
(d) Level hiệu chuẩn CHỈ tổng thể: median P/FV toàn universe mỗi tháng; mục tiêu |log(median P/FV)| nhỏ và không
    xu hướng; LOYO (bỏ 1 năm) cho tham số level. KHÔNG fit theo từng mã.
Luật chọn: cấu trúc/biến thể đổi IC phải qua: OOS ΔIC ≥ +0,01, IS không âm, DSR (N trials đếm đủ) ≥ 0,95 mới được
gọi là "alpha"; còn lại = level/display fix.

## 6. Case diagnostic VNM + panel
Panel PIT khai trước (trước khi nhìn FV): non-financial, có mặt universe_pit ≥ 90% tháng 2014-2026, FCFE 3Y > 0 ở
≥ 80% ngày đánh giá, vốn hoá top-30 tại 2014-01. Thêm bắt buộc theo yêu cầu: VNM, FPT, MWG, PNJ, DGC, GAS, REE, CTR,
DHG (nếu không qua tiêu chí thì vẫn vẽ, gắn nhãn "ngoài tiêu chí").
Cho mỗi mã: FV theo biến thể (hiện tại vs đề xuất) vs giá 2014-2026 (CSV + PNG), reverse-DCF g ngầm định (giữ r) và r
ngầm định (giữ g_exp,g_T). Giải thích lệch bằng cơ bản. KHÔNG chỉnh tham số theo mã.

## 7. Báo cáo
REPORT mở đầu bằng bảng khuyến nghị + "hiện tại vs đề xuất" (FV median, %RẺ, IC). Mọi số = đo trong phiên hoặc
gắn nhãn ước lượng. Mục "tấn công bản thân". Code đề xuất (nếu có) = knob mặc định TẮT, worktree riêng, chưa merge.
