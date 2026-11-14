# PREREG — Phân kỳ RSI cơ học, 48 trial (P1 của `kb/projects/livermore-training-plan-20261114.md` §3)

Job `Taylor_20261114_063556` · soạn 14/11/2026 TRƯỚC khi chạy engine phân kỳ lần đầu (chưa tính một tín hiệu
phân kỳ nào). PAPER-ONLY, không chạm production. Mọi lệch khỏi file này ghi ở REPORT §Lệch PREREG.
Nguồn đặc tả: §3 kế hoạch (giữ NGUYÊN họ 48 trial, không thêm tham số). Phần dưới chỉ làm rõ chỗ §3 để mở.

## 1. Dữ liệu (point-in-time)
- Giá: `data/bq_cache/ticker/*.parquet` (mirror `tav2_bq.ticker`, 2013→2026-11-13). `Close/Open/High/Low` là chuỗi
  **ĐÃ ĐIỀU CHỈNH** cổ tức+chia tách, hồi tố theo vintage hôm nay (`kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`).
  VNINDEX pre-2013 (chỉ cho climatology U1): `vnindex_pre2013.csv` (BQ, md5 46361d6a).
- **Chống double-count corp-action (dòng 8 quant-skeptic):** RSI, pivot VÀ lợi suất kỳ hạn đều tính trên CÙNG MỘT
  chuỗi `Close` điều chỉnh; KHÔNG nhân/chia/trừ `Close` với bất kỳ chuỗi số lượng (OShares, khối lượng, trọng số)
  và KHÔNG cộng thêm cổ tức riêng (Close đã là total-return). Lợi suất = tỉ số hai Close điều chỉnh ⇒ hệ số
  điều chỉnh triệt tiêu. Rào dữ liệu: loại sự kiện nếu cửa sổ [p1 − 20, t + 1 + H] có phiên |Close/Close₋₁ − 1| > 16%
  (vượt mọi biên độ ±7/10/15% ⇒ điều chỉnh hỏng / niêm yết lại / dừng giao dịch); báo số bị loại.
  `Price` (thô) CHỈ dùng trong MDV60; dòng GDKHQ có thể kẹt hệ CUM (`ticker_price_stale_on_exdate.md`) — trung vị 60
  phiên chịu được 1 dòng lệch, chấp nhận.
- Universe U2: `tav2_mike.universe_pit` (cache `data/bq_cache/universe_pit`, CANONICAL theo
  `kb/data_registry/price-volume/universe_pit.md`), `in_universe=True` tại ngày tín hiệu t. **KHÔNG `ticker_prune`.**
  Thanh khoản: **MDV60 thực** = trung vị 60 phiên (t−59..t) của `Price × Volume / Inflation_7` (VND-2026) ≥ **20 tỷ**
  (đúng bậc L20 của `ta_model_5pct_20261106/engine.py`; tái dùng nguyên văn công thức). U1 = VNINDEX (không lọc).
- Không dùng `profit_*`, `*_center_*`, `PC*`, `O1W..O2Y`, `Open_1D` (forward-looking).

## 2. Chỉ báo + pivot (causal, mọi đại lượng ≤ ngày tín hiệu)
- **RSI Wilder(n)**, n ∈ {14, 9}: Δ = Close − Close₋₁ theo mã; AU/AD = EWM α=1/n, `adjust=False`, `min_periods=n`
  (đúng code RSI của engine ta-model); RSI = 100 − 100/(1 + AU/AD). Thang 0–100.
- **Pivot cao** tại i: Close(i) = max Close(i−5..i+5) và i là vị trí ĐẦU TIÊN đạt max trong cửa sổ (phá hoà);
  **pivot thấp** tương tự với min. k = 5. Pivot chỉ **biết** tại i+5 (xác nhận).
- Cặp pivot: p2 = pivot vừa xác nhận; p1 = pivot CÙNG LOẠI gần nhất trước p2 có 10 ≤ p2 − p1 ≤ 60 phiên
  (bỏ qua pivot gần hơn 10 phiên). **Ngày tín hiệu t = p2 + 5.**
- Bốn loại (RSI lấy tại đúng ngày pivot):
  - **RBEAR** regular bearish (pivot cao): Close(p2) > Close(p1)×1,01 ∧ RSI(p2) ≤ RSI(p1) − 3 ∧ RSI(p1) ≥ 60 ⇒ dự báo DOWN.
  - **RBULL** regular bullish (pivot thấp): Close(p2) < Close(p1)×0,99 ∧ RSI(p2) ≥ RSI(p1) + 3 ∧ RSI(p1) ≤ 40 ⇒ UP.
  - **HBULL** hidden bullish (pivot thấp): Close(p2) > Close(p1) ∧ RSI(p2) < RSI(p1) − 3 ⇒ UP.
  - **HBEAR** hidden bearish (pivot cao): Close(p2) < Close(p1) ∧ RSI(p2) > RSI(p1) + 3 ⇒ DOWN.
  - Ngưỡng 60/40/±3 và ±1% áp NGUYÊN cho RSI(9) (không chỉnh lại theo n).
- Hồi chiêu: 1 tín hiệu / loại / mã / 20 phiên (theo vị trí phiên của mã).
- Mã U2 phải có dòng dữ liệu liên tục theo vị trí phiên của mã (không nội suy); thiếu dữ liệu tương lai ⇒ loại, ghi số.

## 3. Kết cục (thực thi trễ T+1)
- Vào tại Close(t+1), ra Close(t+1+H), H ∈ {10, 20, 40} phiên của mã. fwd_H = Close(t+1+H)/Close(t+1) − 1.
- Dấu dự báo s = +1 (UP) / −1 (DOWN). **hit** = 1[s·fwd_H > 0] (fwd = 0 ⇒ không hit).
- Kỳ: t ∈ [2014-01-01, cuối dữ liệu − H]. **IS = t ∈ 2014–2019, OOS = t ≥ 2020-01-01.** Hậu FTSE: t ≥ 2026-09-21,
  báo riêng, KHÔNG kết luận.

## 4. Họ trial — 48, cố định
4 loại × H{10,20,40} × U{U1,U2} × RSI{14,9} = **48**. Không thêm tham số, không đổi k/ngưỡng sau khi thấy số.
Slippage khác 0,2% chỉ là độ nhạy (không có trong họ).

## 5. Tần suất nền — đo và GHI FILE (`FREQ.md`) TRƯỚC bước hiệu quả
Mỗi trial: số sự kiện, số **ngày tín hiệu độc lập** (U2: gộp mọi mã cùng t thành 1 quan sát = trung bình), số tháng
có tín hiệu, tách IS/OOS, số bị loại vì rào dữ liệu. MDE hit (một phía α 0,05, power 0,8, nhị thức quanh 50%):
MDE ≈ 1,2435/√N_ngày_OOS.

## 6. Thống kê hiệu quả (mọi số tính trên N = ngày tín hiệu độc lập)
- **Climatology PIT** (cập nhật theo tháng): tại tháng m, c_m = tỉ lệ ngày d có fwd_H(d) > 0 trong các cửa sổ ĐÃ KẾT THÚC
  trước ngày đầu tháng m. U1: mọi ngày VNINDEX từ 2007-01-01. U2: mọi (mã, ngày) đủ điều kiện U2 từ 2013.
  Cùng cách cho trung bình lợi suất climatology r̄_m (dùng cho excess U1).
- **Dự báo xác suất của trial** (causal, không tham số tune): p_t = (k_up + 2·c_m)/(n + 2), với n, k_up = số sự kiện
  CÙNG TRIAL có cửa sổ đã kết thúc trước t và số trong đó UP (pseudo-count 2 cố định). Brier sự kiện U2 = trung bình
  theo ngày. **BSS = 1 − ΣBS_trial / ΣBS_clim** (trên ngày OOS). CI95 bootstrap **khối THÁNG** (5000 lần, seed 20261114);
  p một phía = tỉ lệ bootstrap BSS ≤ 0.
- **Hiệu quả theo dấu**: U1 exR_t = s·(fwd_H − r̄_m); U2 exR_t = trung bình mã của s·(fwd_H,mã − fwd_H,ctrl), ctrl =
  trung bình fwd_H của MỌI mã đủ điều kiện U2 cùng t (= ngẫu nhiên cùng ngày, cùng bộ lọc). CI bootstrap khối tháng.
- **Ròng sau phí** (U2 chính, U1 tham khảo): exR_ròng = exR − 2×(0,097% + 0,2%) = exR − 0,594% (hành động theo tín hiệu
  tốn một vòng mua-bán so với không làm gì). Độ nhạy slippage 0,1%/0,3% báo kèm.
- **Placebo**: hoán vị NGUYÊN KHỐI THÁNG — mỗi tháng có tín hiệu được gán sang một tháng khác ngẫu nhiên (hoán vị
  các tháng trong vùng mẫu), giữ thứ tự phiên trong tháng (cắt về phiên cuối nếu tháng đích ngắn hơn); U2 giữ mã,
  bỏ sự kiện nếu mã không đủ điều kiện ở ngày đích. 1000 lần; thống kê = exR trung bình OOS; p = P(placebo ≥ thật).
  Không hoán vị trong năm.
- **BH-FDR q = 0,10** trên p_BSS (một phía, OOS) của cả 48 trial.
- **DSR** (Bailey–López de Prado) trên 48: SR = mean/sd của exR ngày OOS (không năm hoá), có skew/kurt, số thử = 48,
  phương sai SR = phương sai SR giữa 48 trial. **PBO**: CSCV, S = 16 khối thời gian bằng nhau (toàn kỳ), metric = exR
  trung bình theo khối, khối không có tín hiệu = 0.
- **LOYO**: bỏ lần lượt từng năm 2014–2026 (13 năm), tính lại exR trung bình toàn kỳ; đếm số năm làm đổi dấu.
  Mô tả kèm: dấu exR từng năm.

## 7. Tiêu chí ĐẠT (§3.3 kế hoạch) — một trial đạt khi TẤT CẢ:
(a) BSS_OOS > 0 và CI95 khối tháng không chứa 0; (b) qua BH-FDR q=0,10 trong 48; (c) LOYO đổi dấu ≤ 2/13;
(d) chỉ U2: exR_ròng OOS > 0 (điểm ước lượng, sau 0,594%).
Bổ sung (không thay tiêu chí): placebo p, DSR, PBO họ. **G1:** 0/48 đạt ⇒ đóng hướng phân kỳ vào `ta-schools-vn` NO-GO.
U1 đạt mà U2 không (hoặc ngược) ⇒ chỉ phần đạt sang P2.
Tiên nghiệm khai trước (§3 kế hoạch): P(U1 qua tiêu chí) ≈ 15%; P(U2 exR dương CI loại 0 nhưng âm sau phí) ≈ 25%;
P(U2 ròng dương sau phí) ≈ 5%.

## 8. §6 DT5G (mô tả, không trong họ 48)
Lead time của RBEAR (RSI14, U1) tại đỉnh 250 phiên (Close(p2) = max Close 250 phiên tới p2) so với ngày DT 4-gate
commit rời BULL/EX-BULL (11 lần, `B_result.json`); false alarm = RBEAR mà 40 phiên sau t không có commit nào rời
BULL/EX-BULL/NEUTRAL đi xuống. N nhỏ ⇒ chỉ mô tả.

## 9. Self-check
1. Control leg: tái lập số pin ta-model `n_elig` L20 = **300437** (meta.json 06/11, cắt dữ liệu ≤ 2026-11-05) bằng
   bộ lọc universe_pit+MDV60 của engine này. Lệch ⇒ ghi rõ nguyên nhân (vintage cache) trước khi tin U2.
2. 300 sự kiện ngẫu nhiên (seed 20261114) tính lại bằng vòng lặp Python thuần (RSI, pivot, điều kiện phân kỳ, fwd,
   exR, ròng) ⇒ |Δ| < 1e-9; tỉ lệ khớp sự kiện 100%.
3. Mỗi sự kiện: t ≥ p2 + 5 và mọi đầu vào có index ≤ t (assert).
4. RSI14 VNINDEX của engine so với cột BQ `D_RSI`×100 (chỉ báo tham khảo — báo tỉ lệ khớp, không chặn).
