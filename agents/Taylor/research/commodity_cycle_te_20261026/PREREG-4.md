# PREREG-4 — Tách SUE của LAG: phần hàng hoá đã biết vs phần bất ngờ thật (FORWARD, PAPER-ONLY)

Job Taylor_20261026_095928, user duyệt hạng mục (c) ngày 26/10/2026. Văn bản này được **đóng băng** (md5 + commit)
TRƯỚC khi viết tracker. Không đổi LAG live, không wire, không lệnh/plan/sizing. Sửa văn bản sau commit = vô hiệu PREREG.

## 0. Cái đã biết TRƯỚC khi đóng băng (để không ai tưởng là OOS)
Nguồn: `b2_rerun.py` → `b2_rerun.json`, `b2_rerun_seasons.csv` (seed 20261027), dữ liệu tới 2026-10-23.
Tôi đã xem toàn bộ lịch sử 2017Q4–2026Q3. Mọi con số dưới đây là **in-sample/post-hoc**; chỉ dữ liệu forward ở §5 được tính.

- IC gộp họ×quý (tier A, 8 họ, 36 quý, 250 ô), CI90 moving-block bootstrap khối 4 quý, p = permutation MỘT dịch
  chuyển chung cho mọi họ (vét cạn 35 dịch chuyển ⇒ p nhỏ nhất đạt được = 1/36 = 0,028):
  c_yoy→rev_yoy 0,443 [0,317; 0,546] p 0,056 · c_yoy→np_d 0,450 [0,283; 0,567] p 0,028 · c_yoy→post60 −0,020
  [−0,109; 0,085] p 0,83. Split 2020: np_d trước 2020 **0,145 [−0,013; 0,331]** (N=49 ô, 9 quý, 6 họ — CI cắt 0)
  / 2020+ 0,494 [0,332; 0,600]. Split 2023: 0,496 / 0,353.
- Tách B2 (np_d ~ c_yoy, fit expanding THEO Release_Date), hồi quy post60 rank-trong-họ, SE block-4:
  phần dư b 0,095, t 1,77, CI90 [0,013; 0,191] (30 quý); phần hàng hoá b −0,025 (t −0,33). Trước 2023: dư t 1,04
  (CI cắt 0); 2023+: dư t 3,17, hàng hoá t −1,85. Trước 2020 không đủ quý có fit (4) ⇒ không báo.
- Thống kê chính §4 tính trên lịch sử: **S1 (np_d) ΔIC TB +0,043/mùa, SD 0,170, 65,5% mùa dương (29 mùa)**;
  **S2 (surprise_B_MA, công thức LAG live) ΔIC TB −0,012, SD 0,167, 51,7% mùa dương** — tức với đúng biến SUE mà LAG
  live dùng, việc tách KHÔNG cải thiện gì trong lịch sử. Tôi chọn S1 là chính SAU KHI thấy cả hai số; đây là đường
  rẽ (forking path) đã khai. Forward là phép thử sạch duy nhất cho cả hai.
- "Bản công bố đầu tiên" trong B2 là **sai**: `ticker_financial` không có dòng trùng (ticker,quarter) (67.946 dòng,
  0 trùng; pkl LAG 58.542 dòng, 0 trùng) ⇒ `drop_duplicates(keep='first')` là no-op; giá trị là bản ingest mới nhất.
  Không có nguồn snapshot theo Release_Date. Đo được mức restate qua 3 snapshot cũ: so bản 2026-07-08 với cache
  2026-10-23 (quý ≤2026Q1): NP_P0 đổi >0,5% ở 11/58.520 dòng (0,02%; tier A 1/1.562), Revenue_P0 1 dòng, NP_P4 0;
  **Release_Date đổi ở 43 dòng**. Bản 07-28/07-29 so 10-23: 0 thay đổi. Trong cùng bảng NP_P0(q) ≠ NP_P1(q+1) >0,5% ở
  0,16% cặp (2020+: 0,35%). Giới hạn: chỉ đo được cửa sổ ~3,5 tháng; ghi đè cũ hơn 07-08 là vô hình. Forward giải
  quyết bằng cách **chụp giá trị lúc thấy lần đầu** (§3, append-only).

## 1. Giả thuyết
**H1:** trong tập sự kiện công bố BCTC của danh sách mã đóng băng (§2), SUE_res = SUE − SUE_hat(hàng hoá) dự báo lợi suất
vượt trội 60 phiên sau công bố **tốt hơn** SUE thô, đo bằng ΔIC = IC(SUE_res, post60) − IC(SUE_raw, post60) > 0.
**H0:** ΔIC ≤ 0 (phần hàng hoá không làm nhiễu, hoặc thị trường không phân biệt).
Đối chứng: (a) SUE thô cùng sự kiện (chính là vế trừ trong ΔIC); (b) nhóm **không hàng hoá** = sự kiện LAG
qualify của mã ngoài danh sách, chỉ mô tả IC(SUE thô, post60) theo mùa (không phải tiêu chí).

## 2. Mẫu (đóng băng)
- Danh sách mã = 25 mã tier A của `commodity_map_te.csv` (md5 `9414e8640baca06a8837813e4280a31b`), 8 họ:
  rubber_tsr20(DRI,PHR,DPR,TRC,GVR)·crude/brent(PVS,PVD,PVC,PVB,GAS)·urea(DPM,DCM)·dap(DDV,LAS)·sugar(SBT,LSS,QNS)·
  steel_cn(HPG,HSG,NKG,TLH,POM,SMC)·dry_bulk(VOS)·container(HAH). Dấu +1 cả 8 họ. **Không thêm/bớt mã sau khi thấy
  kết quả.** HSG/NKG (BANNED giao dịch) vẫn đo (giả thuyết về thông tin, không về khả năng giao dịch), gắn cờ
  `banned=1`; độ nhạy bỏ 2 mã này là mô tả.
- Sự kiện = một dòng (ticker, quarter) trong `data/bq_cache/ticker_financial.parquet` có Release_Date. Đủ điều kiện
  khi: mã thuộc universe_pit ở phiên cuối ≤ Release_Date; tín hiệu hàng hoá đã có trước công bố (Release_Date >
  qend+2 ngày); Revenue_P4>0 (S1); đủ lịch sử fit (§3). Thiếu điều kiện ⇒ vẫn ghi dòng, `counts=False`, `reason`.
- Mã LAG không có hàng hoá: mọi sự kiện `qualify=True` của `lag_live_schedule.live_lag_candidates()` có ticker ngoài
  danh sách ⇒ ghi dòng `group=NO_COMMODITY`, `reason=EXCLUDED_NO_COMMODITY`, không vào H1. Mã tier A mà LAG qualify
  được gắn `lag_qualify=1` (tập con chỉ mô tả: lịch sử chỉ 264 sự kiện, ~8–10/mùa gần đây).
- Mùa = quý tài chính. **Mùa đếm: 2026Q4 trở đi.** Mùa 2026Q3 (đang ra lúc đóng băng, 5 mã tier A đã công bố
  20–22/10) = `PRE_FREEZE_BACKFILL`, `counts=False`, kể cả mã công bố sau ngày đóng băng.
- LATE: dòng thấy lần đầu muộn hơn 10 phiên sau Release_Date ⇒ `counts=False`, `reason=LATE`.

## 3. Biến (tính 1 lần lúc thấy sự kiện lần đầu, ghi vào nhật ký, KHÔNG tính lại)
- Hàng hoá: `tav2_bq.commodity_prices` `source='trading_economics' AND cadence='daily'` (tường minh, không
  `commodity_latest`). avgQ = TB giá ngày trong quý lịch, chỉ khi ≥40 quan sát.
  c_yoy = log(avgQ/avgQ−4); c_ma = log(avgQ / TB(avgQ−1..Q−4)).
- **S1 (CHÍNH)** sue1 = (NP_P0 − NP_P4)/Revenue_P4, cắt [−0,5; 0,5]; hồi quy trên c_yoy.
- **S2 (PHỤ)** sue2 = surprise_B_MA đúng công thức `lag_live_schedule.py` ((NP_P0 − TB(NP_P1..P4))/max(|TB|,1e9),
  cắt ±5); hồi quy trên c_ma.
- SUE_hat: OLS y = a + b·c, riêng từng họ, trên MỌI sự kiện cùng họ (25 mã, từ 2017) có **Release_Date < Release_Date
  sự kiện này** (chặt), cần ≥8 sự kiện và ≥6 quý khác nhau; thiếu ⇒ `reason=NO_FIT_HISTORY`. Lịch sử fit đọc từ bản
  cache tại ngày chạy (giới hạn restate ở §0). Ghi a, b, n_fit, sue_hat, sue_res cho S1 và S2.
- post60 = Close(t0+60)/Close(t0) − 1 − (lợi suất kép bình quân đều universe_pit, thành viên t−1, cùng cửa sổ),
  t0 = phiên đầu tiên ≥ Release_Date + 1 ngày. Close = giá điều chỉnh `data/bq_cache/ticker`. Tính 1 lần khi đủ
  60 phiên, ghi nhật ký kết quả. Không `profit_*`, không `ticker_prune`.

## 4. Thống kê & tiêu chí (cố định; chỉ `commodity_sue_decomp_forward_review.py` tính)
- Mùa hợp lệ: ≥6 sự kiện `counts=True` có post60, thuộc ≥3 họ. ΔIC_q = Spearman(res, post60) − Spearman(raw, post60)
  trên các sự kiện đó (trong 1 họ×quý res và raw cùng thứ hạng ⇒ khác biệt chỉ đến từ thành phần cấp họ).
- **Đơn vị độc lập = mùa** (họ×quý lồng trong mùa; tự tương quan bậc 1 của ΔIC lịch sử 0,031). Số trial = **2**
  (S1, S2), Holm. Kiểm định: t một phía trên ΔIC_q qua các mùa.
- **N và power (đo, §0):** SD ΔIC 0,170 (S1) / 0,167 (S2) mỗi mùa. MDE theo SD S2 (một phía α 0,05, power 80%; S1 lớn hơn ~2%): 2 mùa 0,29 · 4 mùa 0,21 · 8 mùa
  0,15 · 16 mùa 0,10. Hiệu lịch sử S1 +0,043 cần ≈ (2,49·0,17/0,043)² ≈ 97 mùa ≈ 24 năm. **Tức forward này chỉ
  phát hiện được hiệu LỚN (≥ ~0,10 sau 16 mùa); với hiệu cỡ lịch sử, kết cục dự kiến là "KHÔNG PHÂN BIỆT ĐƯỢC".**
  Không hứa kết luận dương.
- **Mốc review** (script từ chối chạy trước mốc đầu): 2027-09-01 (≈2 mùa 2026Q4, 2027Q1 — CHỈ kiểm toàn vẹn nhật ký,
  không verdict, quant-skeptic xem) · 2028-09-01 · 2029-09-01 · 2030-09-01 · **CUỐI 2031-09-01** (≈18 mùa).
- **FAIL sớm** (từ 2028-09-01, cho từng S): N ≥ 8 mùa và TB ΔIC ≤ 0 ⇒ FAIL S đó, dừng đếm S đó.
- **PASS** (chỉ ở mốc CUỐI, cho từng S): N ≥ 16 mùa VÀ (1) p Holm một phía < 0,05; (2) TB > 0 và trung vị > 0;
  (3) ≥ 60% mùa ΔIC > 0; (4) LOFO: bỏ bất kỳ 1 họ (tính lại ΔIC_q), TB vẫn > 0; (5) TB > 0 ở cả nửa đầu và nửa sau
  các mùa. Thiếu N ở mốc cuối ⇒ "KHÔNG PHÂN BIỆT ĐƯỢC", đóng, **không tự gia hạn**.
- PASS = ứng viên R&D, cần quant-skeptic CONFIRMED + user; KHÔNG tự wire vào LAG.
- Mô tả kèm (không phải tiêu chí): tập con lag_qualify=1; bỏ banned; IC(raw) nhóm NO_COMMODITY vs tier A.

## 5. Vận hành
- Tracker `mike/bin/commodity_sue_decomp_forward_tracker.py`: khoá md5 PREREG-4 + commodity_map_te.csv trong code
  (lệch ⇒ dừng, không ghi). Nhật ký APPEND-ONLY `data/commodity_sue_decomp_forward_events.csv` +
  `data/commodity_sue_decomp_forward_outcomes.csv`, khoá (family, quarter, ticker), ghi nguyên tử. Tracker KHÔNG in
  IC/TB/CI/p hay bất kỳ thống kê nào gộp sự kiện với post60.
- Cron đề xuất (Mike duyệt cài): 1 lần/ngày ngày 10–31 tháng 1/4/7/10 và 1–15 tháng 2/5/8/11 (phủ qend+10…qend+46;
  đo 2022+: 0/455 sự kiện tier A công bố >45 ngày sau qend). Kết quả post60 tính bù ở lần chạy sau khi đủ 60 phiên.
- Rủi ro tồn dư đã biết: TE có thể sửa lịch sử (không vintage); Close điều chỉnh có thể đổi sau corp action;
  Release_Date có thể bị sửa (43 dòng/3,5 tháng) — nhật ký giữ bản thấy lần đầu.
