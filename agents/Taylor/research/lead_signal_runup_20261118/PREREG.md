# PREREG: tín hiệu kỹ thuật báo trước run-up 1–10 phiên (job Taylor_20261118_122819)

PAPER-ONLY. Không wire, không sửa production/filter.json/trading_rules.json. Viết và tính md5 TRƯỚC khi chạy engine.
Tôi chưa xem bất kỳ con số lift/precision nào. TV1/VCP chỉ dùng làm mô tả; không tham số nào lấy từ hai mã này.

## 0. NO-GO liên quan đã đóng (không lặp lại)
- `livermore-divergence-nogo-20261114.md`: phân kỳ RSI 0/48 trial. Không đưa RSI vào họ trial ở đây.
- `ta-schools-vn-20261025.md`: nến/VSA/Darvas/dòng tiền làm tín hiệu VÀO, và cờ xu hướng làm bộ lọc LAG/BAL, đều NO-GO.
  Ở đây câu hỏi khác: dự báo NHÃN run-up 10 phiên (lift/precision), không phải lọc lệnh BAL/LAG. Vì VSA/dòng tiền đã
  NO-GO, nhóm (ii) dưới đây có tiên nghiệm thấp; tôi vẫn kiểm vì user hỏi đúng cơ chế đó, và để có số đo trực tiếp.
- `momentum-deals.md` (MOM_N/MOM_S đã gỡ production 07/2026): momentum 52w không phải ý tưởng mới.

## 1. Dữ liệu
- `data/bq_cache/ticker/20*.parquet` (mirror `tav2_bq.ticker`, CANONICAL cho lịch sử theo
  `kb/data_registry/price-volume/ticker_ohlcv_tables.md`). Dữ liệu tới 2026-11-17 (cache chưa có 18/11).
- Giá: `Open/High/Low/Close` đều đã back-adjust corp-action cùng một cơ sở (đã đo: năm 2016, 114.655 dòng có Close/Price<0,9
  thì 100% thoả Low≤Close≤High, 0,06% thoả Low≤Price≤High). `Price` là giá thô. Mọi đặc trưng giá và lợi suất dùng OHLC
  điều chỉnh. Khối lượng dùng **TV = Price×Volume** (VND danh nghĩa), không đổi khi chia tách. "Thực" = TV/Inflation_7.
- Universe: `data/bq_cache/universe_pit` `in_universe` (CANONICAL, ruleset 1). Không dùng `ticker_prune`, không dùng
  `profit_*`, `PC1W..PC2M`, `Open_1D`, `O1W..O2Y`, `Pattern_*` làm đặc trưng.
- VNINDEX: dòng ticker=VNINDEX cùng cache. Bối cảnh: `vnindex_5state_dt5g_live.state` (cùng dữ liệu `get_gated_state()`
  đọc; lịch sử thì đọc bảng) và breadth PIT = % mã in_universe có Close>MA50 tự tính. Hai thứ này CHỈ để phân tầng mô tả.
- Biên độ trần/sàn: cache không có cột sàn. Suy CAUSAL: band(t)=7% nếu max lợi suất tăng 1 phiên (điều chỉnh) trong
  t−250..t−1 ≤7,5%; 10% nếu ≤10,5%; ngược lại 15%. Ngày trần: ret(t) ≥ 0,95×band. Lợi suất điều chỉnh so với Close điều
  chỉnh hôm trước tương đương so với giá tham chiếu (kể cả ngày GDKHQ). Sai lệch đã biết: mã HNX/UPCoM chưa từng tăng >7,5%
  trong 250 phiên sẽ bị coi là HOSE (chỉ ảnh hưởng S18/S19 và cờ mở cửa trần).
- Đình chỉ: dòng t bị loại nếu khoảng lịch từ t tới dòng t+10 của mã > 25 ngày, hoặc thiếu dòng t+10.
  Lỗi dữ liệu: nhãn bị loại nếu có |ret ngày| > 25% trong (t, t+10].

## 2. Mẫu
- Dòng đủ điều kiện E(t): in_universe(t), Volume(t)>0, mã có ≥250 dòng trước t, ≥10/20 phiên trước có Volume>0, nhãn xác
  định được. t ∈ [2014-01-02, ngày cuối có đủ 10 phiên tương lai].
- IS = 2014–2019. OOS = 2020-01-01 trở đi. Ngưỡng mọi tín hiệu chốt sẵn ở §4 (không tối ưu trên IS); IS chỉ dùng để kiểm
  cùng chiều (G3) và để chốt mốc tercile ADV.
- **Mẫu chính = chống đuổi giá**: bỏ dòng có C(t)/C(t−5)−1 > 15%. Mẫu không lọc báo riêng.

## 3. Nhãn run-up (được dùng tương lai vì chỉ là nhãn)
- exR(t,k) = C(t+k)/C(t) − VNI(t+k)/VNI(t), k=1..10 (phiên của mã; VNI theo ngày).
- F_X(t) = 1 nếu max_k exR(t,k) ≥ X. **X ∈ {20%, 30%}.**
- Đợt (episode): theo mã và X, gộp các ngày F=1 cách nhau ≤3 dòng; đợt mới chỉ khi cách ngày F cuối của đợt trước ≥20 dòng
  (cooldown), không thì gộp. **T0 = ngày F=1 đầu tiên của đợt** (đóng cửa T0, giá chưa chạy; run-up nằm trong T0+1..T0+10).
  N độc lập = số đợt.
- Base rate b = P(F_X | E, mẫu chính) theo ô (năm × tercile ADV20 thực; mốc tercile lấy từ phân phối IS gộp).

## 4. Tín hiệu (tính CHỈ từ dữ liệu tới hết phiên t; vào lệnh Open(t+1))
Ký hiệu: TV, ADV20(t−1)=trung bình TV t−20..t−1, CLV=(C−L)/(H−L) (H=L thì 1 nếu C≥C(t−1) ngược lại 0), ret=C/C(t−1)−1.
| Mã | Cơ chế | Định nghĩa |
|---|---|---|
| S01 ATRP_LOW | (i) nén | ATR14/C tại t nằm ở phân vị ≤10% của 250 giá trị gần nhất của chính mã |
| S02 BBW_LOW | (i) | độ rộng BB20 (4σ20/MA20) phân vị ≤10% trong 250 |
| S03 NR7_ID | (i) | H−L(t) nhỏ nhất 7 phiên ∧ inside day (H≤H(t−1), L≥L(t−1)) |
| S04 TIGHT20 | (i) | maxH(t−19..t)/minL(t−19..t)−1 ≤ 10% |
| S05 VCP_CONTRACT | (i) | biên độ 3 cửa sổ 10 phiên liên tiếp giảm dần nghiêm ngặt, cửa sổ cuối ≤8%, C(t) ≥ 0,90×maxH(t−59..t) |
| S06 DRYUP | (ii) | median TV(t−9..t) ≤ 0,4×median TV(t−129..t−10) |
| S07 SURGE3 | (ii) | TV(t) ≥ 3×ADV20(t−1) ∧ CLV ≥ 0,5 ∧ ret>0 |
| S08 SURGE5 | (ii) | như S07 với 5× |
| S09 DRY_THEN_SURGE | (ii) | S06(t−1) ∧ S07(t) |
| S10 HIDDEN_ACC | (ii) | TV(t) ≥ 3×ADV20(t−1) ∧ |ret| ≤ 2% |
| S11 UPDOWN_VOL | (ii) | ΣTV ngày tăng / ΣTV ngày giảm trong t−19..t ≥ 2 |
| S12 OBV_DIV | (ii) | OBV(TV) tại t = max 60 phiên ∧ C(t)/C(t−20)−1 ∈ [−5%, +5%] |
| S13 HIGHER_LOWS | (iii) | minL(t−29..t−20) < minL(t−19..t−10) < minL(t−9..t) |
| S14 NEAR_52W | (iii) | 0,95×maxH(t−249..t−1) ≤ C(t) < maxH(t−249..t−1) |
| S15 BREAKOUT_52W | (iii) | C(t) > maxH(t−249..t−1) ∧ TV(t) ≥ 1,5×ADV20(t−1) |
| S16 RS_LEAD | (iii) | RS=C/VNI đạt max 120 phiên ∧ C(t) < maxC(t−119..t−1) |
| S17 MA_CONV_X | (iii) | |MA20/MA50−1| ≤ 2% ∧ C(t)>max(MA20,MA50) ∧ C(t−1) ≤ max(MA20,MA50)(t−1) |
| S18 CEIL_TODAY | (iv) | ngày trần tại t |
| S19 CEIL2_5D | (iv) | ≥2 ngày trần trong t−4..t |
| S20 GAPUP | (iv) | Open(t) ≥ 1,02×H(t−1) ∧ C(t) ≥ Open(t) |
| S21 TURN_RANK_JUMP | (iv) | phân vị TV(t) toàn universe hôm t trừ trung bình phân vị của mã t−20..t−1 ≥ 0,30 |
| C1 | combo | S04 ∧ S07 |
| C2 | combo | S01 ∧ S14 |
| C3 | combo | S16 ∧ S11 |
**Họ trial = 24 tín hiệu × 2 ngưỡng X = 48 trial.** Bối cảnh (v) chỉ phân tầng, không tính vào họ.

## 5. Thống kê
- Lift chuẩn hoá L = Σy / Σb trên các dòng có tín hiệu (b theo ô năm×tercile ADV ⇒ kiểm soát thanh khoản và năm).
  Precision = Σy / n. Báo kèm n dòng, số đợt độc lập bị "bắt", số false positive tuyệt đối/năm.
- CI 95%: block bootstrap theo THÁNG lịch (B=2000, seed 20261118), không t-test trên mã-ngày.
- p một phía (H0: L≤1) từ bootstrap; BH-FDR q=0,10 trên 48 trial.
- MDE (80% power, α 5% hai phía) = exp(2,8×SE_boot(log L)). MDE > 1,5 ⇒ trial đó "không đủ sức kiểm định".
- Giao dịch: vào Open(t+1), ra Close(t+10); excess = lợi suất mã − VNI(Close t → Close t+10) (VNI thiếu Open tin cậy, ghi
  rõ). Phí 0,1%/chiều + slippage/chiều theo ADV20 danh nghĩa (`ước lượng`, chốt trước): ≥20 tỷ 0,1%; 5–20 tỷ 0,3%;
  1–5 tỷ 0,75%; <1 tỷ 1,5%. Mở cửa t+1 ≥ trần (0,95×band so với C(t)) ⇒ không khớp được, bỏ và đếm.
  Capacity/mã = 10%×ADV20 danh nghĩa.
- DSR (chỉ cho trial qua G1): trên chuỗi trung bình tháng của excess ròng OOS, SR0 từ phương sai SR của 48 trial.
- Placebo (chỉ cho trial qua G1–G5, và mô tả top-3 theo L OOS): dịch vòng chuỗi tín hiệu của từng mã đi bội số 21 phiên
  (≥63), 200 lần, p = tỉ lệ L_placebo ≥ L thật. Không hoán vị trong năm.
- Leave-one-year-out (OOS): bỏ từng năm.

## 6. Kill criteria (chốt trước)
Một trial **"có thông tin"** khi đạt ĐỦ:
- G1 L_OOS ≥ 1,5 ∧ CI95 dưới > 1,0
- G2 qua BH-FDR q=0,10 (48 trial)
- G3 L_IS > 1,0 (cùng chiều)
- G5 LOYO: min L khi bỏ 1 năm OOS ≥ 1,3 ∧ L khi bỏ 2 năm có nhiều hit nhất ≥ 1,2
- placebo p < 0,05
**"GO paper"** thêm: G4 excess ròng trung bình/lệnh > 0 với CI95 dưới > 0 · DSR ≥ 0,95 · G6 capacity trung vị ≥ 1 tỷ VND/mã
(nếu nhỏ hơn: ghi "có thông tin nhưng không giao dịch được ở quy mô").
Không trial nào đạt ⇒ **NO-GO** cho hướng "dấu hiệu kỹ thuật báo trước run-up".

## 7. Mô tả (không gate)
- Hai chiều: với các đợt OOS, recall_pre = P(tín hiệu bất kỳ ngày nào trong T0−5..T0−1), recall_T0 = P(tín hiệu tại T0),
  so với tỉ lệ cùng cửa sổ 5 ngày ở dòng không run-up (P(X | không tăng)).
- Phân tầng DT5G state và breadth tercile cho top-5 tín hiệu.
- Kết thúc đợt (câu hỏi đối xứng, 4 trial mô tả, BH riêng): dòng "đang trong đợt" = C(t)/minC(t−20..t)−1 ≥ 30%; nhãn
  D(t) = min_k exR(t,k) ≤ −15% trong 10 phiên. K1 TV(t)=max 60 phiên ∧ CLV≤0,3 ∧ H−L ≥ 1,5×ATR14; K2 C/MA20−1 ≥ 25%;
  K3 ≥5/6 phiên gần nhất tăng ∧ C(t)/C(t−6)−1 ≥ 20%; K4 ngày sàn tại t (ret ≤ −0,95×band).
- Case study TV1/VCP: SAU khi có kết quả toàn universe.

## 8. Self-check
1. Control leg: đếm dòng in_universe ∧ MDV60 thực ≥20 tỷ ∧ 2014 ≤ t ≤ 2026-11-05 phải tái lập 300.438 của
   `livermore_divergence_20261114/selfcheck.json` (khác thì giải thích bằng cache refresh, không lờ đi).
2. Không nhìn trước: 30 mã ngẫu nhiên × 3 mốc cắt, tính lại đặc trưng trên chuỗi đã cắt (và thay phần tương lai bằng nhiễu)
   ⇒ đặc trưng tại t ≤ mốc phải trùng tuyệt đối. S21 (cắt ngang) kiểm bằng cắt toàn universe tại 1 mốc.
3. Nhãn tính lại bằng vòng lặp thuần cho 2.000 dòng ngẫu nhiên ⇒ sai số 0.
4. 0 VND: P&L 500 lệnh ngẫu nhiên tính lại độc lập từ giá thô trên vốn 1 tỷ/lệnh ⇒ tổng chênh 0 VND (sai số float < 1 VND).
5. threads=1 (OMP/MKL/OPENBLAS_NUM_THREADS=1).
