# PREREG — Đặc trưng kỹ thuật cho candidate BAL + LAG: (Q1) timing điểm mua, (Q2) nhóm rủi ro đuôi

Job `Taylor_20261022_070208` · 2026-10-22 · READ-ONLY (không sửa production, không pin registry, không ghi tên canonical).
Ghi và khoá md5 TRƯỚC khi tính bất kỳ đặc trưng/kết quả nào. Lệch sau khi thấy dữ liệu ⇒ mục "Deviations" của REPORT.
Khác nghiên cứu `lag_price_reaction_class_20261022` (NO-GO): ở đó LỌC LOẠI theo drift; ở đây Q1 = TIMING trong cửa sổ
vào lệnh (không đổi tập mã), Q2 = RỦI RO ĐUÔI, hành động = GIẢM TỶ TRỌNG, không loại.

## 1. Tập sự kiện (khoá)
- **LAG (event study)**: đúng 5.361 dòng `research/lag_entry_window_width_20261021/exp_window_events.csv`
  (entry chuẩn e = Release+5 phiên, mua Open e = `buyO0`, thoát Close e+25 = `exA0`). Cụm = mùa báo cáo (năm-quý Release).
- **BAL + LAG (cấp NAV/book)**: ledger R3 park0 đã pin trong kho bất biến:
  - **pin0% (SÀN)** `data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz`, md5 `537e349b5589408c994f8aceafeb9a39`
  - **pin1M (TRẦN)** `…__R3-park0-pin1M-SO-CHINH__a6ba34d8.csv.gz`, md5 `a6ba34d83a4d374a73293d897c0b43d9`
  - "Vị thế" = `holding_id` có ≥1 `ENTRY_FILL` và thoát bằng TIME/STOP/MTM_UNREALIZED. Lệnh ABANDONED_REFUND
    (chưa thành vị thế) KHÔNG phải vị thế — giữ nguyên như ledger trong mọi biến thể.
  - e = ngày ENTRY_FILL đầu tiên; phiên tín hiệu = e−1 (engine T+1 Open). Giá vào control = giá vốn TB ledger.
  - Book theo cột `book` (BAL / LAG; gồm cả CAPITB_/CAPITL_ của book đó). Cụm BAL = năm-quý dương lịch của e
    (BAL không theo mùa báo cáo — khai báo); cụm LAG-ledger = năm-quý của e.
- Giá: `tav2_bq.ticker` Open/High/Low/Close đã điều chỉnh qua `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`
  (CÙNG vintage với ledger pin). Không cột `profit_*`. VNINDEX không dùng.

## 2. Đặc trưng (4, đo tại CLOSE phiên e−1 ⇒ PIT; riêng GAP đo tại Open e, chỉ dùng cho luật Q1-R2 chạy lúc mở cửa)
- **VOL60** = độ lệch chuẩn lợi suất Close-Close 60 phiên [e−60, e−1] × √250.
- **RUN20** = C[e−1]/C[e−21] − 1.
- **DIST52** = C[e−1] / max(High[e−250..e−1]) − 1.
- **GAP** = Open[e]/C[e−1] − 1.
Thiếu lịch sử ⇒ đặc trưng NaN ⇒ không thuộc nhóm rủi ro (giữ nguyên size).

## 3. Q1 — 3 luật timing (khoá; R = C[e−1] = giá tham chiếu tín hiệu; cửa sổ = phiên e, e+1, e+2)
- **R1 LIMIT2**: lệnh giới hạn tại R×0,98, sống 3 phiên. Khớp ở phiên đầu tiên d có Low[d] ≤ giới hạn, giá
  = min(Open[d], giới hạn). Không khớp ⇒ KHÔNG vào lệnh (tiền nằm im tới ngày thoát control).
- **R2 GAPSKIP3**: GAP > +3% ⇒ bỏ vào lệnh; ngược lại mua Open e (= control).
- **R3 PULLBACK**: phiên d ∈ {e, e+1} đầu tiên có Close[d] < R ⇒ mua Open[d+1]; không có ⇒ mua Open[e+2]
  (luôn khớp; đo giá trị THUẦN của việc chờ).
- Thoát: giữ NGUYÊN ngày & giá thoát control (luật thoát hiện hành không đổi). Phí 0,1%/chiều (buy/sell cost factor
  của engine). Khớp ⇒ cùng số tiền giải ngân B (số cp = B/giá mới). Khi tiền nằm im: pin0% = 0, pin1M = dep1m PIT
  (`idle_rate_proxy.py` tier dep1m, lãi theo ngày lịch /365).
- Event-level: Δgiá vào bình quân (bps, trên lệnh khớp), tỷ lệ không khớp, tỷ lệ bỏ lỡ "mã thắng" (control return
  thuộc tercile cao) so với tỷ lệ không khớp chung, Δlợi suất giao dịch TB (không khớp ⇒ lãi nhàn rỗi).

## 4. Q2 — 3 nhóm rủi ro (khoá; ngưỡng cắt trên IS = e trong 2014–2019, RIÊNG mỗi tập: LAG-event / BAL-ledger / LAG-ledger)
- **G_VOL**: VOL60 ≥ P80(IS).  **G_RUN**: RUN20 ≥ P80(IS).  **G_DEEP**: DIST52 ≤ P20(IS).
- Kết quả trong thời gian giữ [e, ngày thoát]: **MAE** = min Low / giá vào − 1; **HIT15** = 1{MAE ≤ −15%};
  **P5** = phân vị 5% lợi suất giao dịch (sau phí). Chính = ΔHIT15 = P(HIT15|nhóm) − P(HIT15|còn lại).
- Hành động thử ở NAV: **giảm 50% size** vị thế thuộc nhóm (phần tiền không giải ngân nằm im như §3).

## 5. Cấp NAV (overlay bậc 1 trên ledger pin — KHÔNG chạy lại full engine)
NAV'(t) = NAV_pin(t) + Σ_vị-thế Δ_i(t); Δ_i(t) = (giá trị phần biến thể: cp × Close_t hoặc tiền nằm im + lãi) −
(cp control × Close_t) trong [e, thoát); sau thoát đóng băng ở chênh tiền thu về. Bỏ qua: tái đầu tư phần chênh,
phản hồi allocator/NAV-sizing, đổi slot. Báo cáo CAGR, Sharpe(252), MaxDD, Calmar trên NAV tổng (BAL+LAG) và từng book
(`nav_bal_ref`/`nav_lag_ref`), ở cả pin0% và pin1M; IS 2014–19 / OOS 2020+; per-year + bỏ-một-năm.
Self-check control: (a) metric tính lại từ DAILY khớp METRIC đã pin (CAGR 22,12% / 25,42%); (b) overlay rỗng ⇒ Δ ≡ 0 VND;
(c) dựng lại giá trị cổ phiếu từ TX × Close cache so với `*_stocks_ref` DAILY, báo sai số VND tối đa.

## 6. Thống kê, số trial
- Trials = 12: Q1 3 luật × 2 book + Q2 3 nhóm × 2 book. Q2 trên LAG-event 5.361 là bằng chứng event-level của trial
  Q2-LAG (không tính thêm trial).
- CI: bootstrap CỤM (mùa/quý) 2.000 lần, seed 20261022; khai N sự kiện và N cụm.
- Holm trong mỗi họ (Q1: 6 p; Q2: 6 p), α=0,05.
- DSR trên chuỗi Δ lợi suất ngày (biến thể − control, NAV tổng pin0%) của biến thể tốt nhất, N=12, phương sai Sharpe
  giữa 12 trials. PBO: CSCV S=16 khối thời gian trên lợi suất ngày NAV tổng pin0% của 12 biến thể + control, metric Sharpe.

## 7. Tiêu chí (chốt trước)
**Q1 — một luật là ỨNG VIÊN nếu ĐỦ:** (1) Δlợi suất giao dịch TB > 0 với CI95 cụm loại trừ 0; (2) ΔCAGR > 0 VÀ
ΔCalmar > 0 ở CẢ pin0% và pin1M (NAV tổng); (3) ΔCAGR IS > 0 và OOS > 0; (4) bỏ-một-năm: ΔCAGR > 0 ở mọi lần bỏ;
(5) Holm; (6) DSR ≥ 0,95 và PBO < 0,5. Cải thiện giá vào mà không qua (2) = KHÔNG phải ứng viên.
**Q2 — một nhóm là NHÓM RỦI RO XÁC NHẬN nếu:** (1) ΔHIT15 > 0 với CI95 cụm loại trừ 0; (2) cùng dấu IS và OOS;
(3) bỏ-một-năm: ΔHIT15 > 0 mọi lần; (4) Holm. **Hành động giảm size là ỨNG VIÊN nếu thêm:** (5) MaxDD tốt hơn VÀ
Calmar cao hơn control ở CẢ pin0% và pin1M; (6) Calmar IS và OOS đều không xấu đi; (7) DSR ≥ 0,95, PBO < 0,5.
- **GO** = ≥1 ứng viên ⇒ bước sau (KHÔNG trong job này) là A/B full-engine 1 biến, control tái hiện byte pin, quant-skeptic.
- **CẢNH BÁO-ONLY** = nhóm qua Q2 (1)–(4) nhưng trượt (5)–(7): được dùng làm nhãn cảnh báo hiển thị, không đổi size.
- **NO-GO** = không gì qua. Nói thẳng; không thêm biến thể. Kết quả ngược giả thuyết báo đúng như vậy.
