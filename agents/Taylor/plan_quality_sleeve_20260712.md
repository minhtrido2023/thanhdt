# PLAN — Sleeve buy-and-hold "chất lượng cao" co giãn theo BAL (cảm hứng AlphaLens)
> Taylor, 2026-07-12 · job Taylor_20260712_073149 · trạng thái: **SCOPE XONG — CHỜ USER DUYỆT, CHƯA CHẠY BACKTEST NÀO**
> Trial MỚI, sổ N riêng. Cấu trúc theo mẫu `plan_lag_weight_20260712.md` / `plan_dvr_8l_sizing_20260712.md`.

## 0. Tóm tắt cho user (đọc 1 phút)

Ý tưởng của user tách được thành **3 trục độc lập**, và scope cho thấy chúng ở 3 trạng thái rất khác nhau:

1. **"Tỷ trọng co giãn bù phần BAL rỗng" — ĐÃ CÓ SẴN trong engine, không cần phát minh.** Parking
   waterfall hiện tại về mặt cơ học chính là công thức user muốn: sleeve chỉ ăn **idle cash** =
   NAV − (BAL đã deploy) − (LAG đã deploy). BAL deploy càng ít → idle càng lớn → sleeve càng to,
   tự động, hàng ngày. Không có gì phải thiết kế thêm ở trục này (§4).
2. **"Giữ từ NEUTRAL trở lên (thêm BULL/EX-BULL)" — tiền lệ 4 lần đo, cả 4 đều BÁC** (§2.2):
   bull-park custom30V R2 (Sharpe giảm, hại 2024/25), custom30B vehicle (FAIL walk-forward,
   IS→OOS đảo dấu), R5 conditional (marginal +0.49pp, chỉ opt-in), và mới nhất DC-book CÂU 1
   (2026-07-06: toàn bộ edge +BULL = 2020+2021, ba năm bull gần nhất đều ÂM, LOO bác). Nguyên
   nhân cấu trúc: IS 2014-19 chỉ có ~53 ngày BULL → mọi feature BULL-only sinh ra đã yếu
   walk-forward. Tôi vẫn đưa 1 trial extension vào family (đúng ý user) nhưng **khai báo trước
   prior mạnh nghiêng NO-GO** ở trục này.
3. **"Rổ CỐ ĐỊNH nhỏ, chất lượng cao, xoay quý" — phần MỚI thật sự duy nhất, chưa ai đo đúng
   config này.** Câu hỏi đo được: *top-8/12 quality-gated có thắng custom30V (30 mã value) trong
   vai trò parking vehicle không?* Prior cũng nghiêng chống (mọi selector thiên-quality từng thua
   value: composite v3 −7..−11pp, 8L drop-in fail, track-record cao underperform) nhưng đây là
   gap thật và đo RẺ — builder `custom_basket.build_pit()` đã có sẵn knob `top_n`/`gate_rating`.

**Khuyến nghị của tôi (user quyết):** đáng đo, nhưng thu hẹp kỳ vọng — giá trị khả dĩ nhất của
sleeve này là **thay/cạnh tranh vehicle custom30V ở NEUTRAL** (trục 3), KHÔNG phải mở regime mới
(trục 2) hay cơ chế co giãn mới (trục 1 — đã có). Family N=5 pre-registered ở §6, gate chặt ở §7.
Kỳ vọng khai báo trước: **−0.5 đến +0.5pp CAGR vs R3, prior lệch về NULL/NO-GO**; nếu ra +2pp trở
lên → nghi bug trước khi mừng.

## 1. Bối cảnh & ý tưởng user (giữ nguyên nuance)

- Nguyên văn ý user: sleeve buy-and-hold **BỔ SUNG** bên cạnh BAL/LAG (không thay thế); rổ **cố
  định, nhỏ, chất lượng cao** (không phải 30 mã đa dạng như custom30V), xoay vòng in/out **mỗi
  quý**; chỉ giữ từ **NEUTRAL trở lên** (3/4/5), không giữ CRISIS/BEAR; tỷ trọng **co giãn** để
  bù phần BAL đang giảm/rỗng (không phải % cố định). Cảm hứng: paper AlphaLens (FPT/ACB/MBB/HDB
  equal-weight, benchmark VNINDEX 1860.01, tracking 07-01→09-30).
- Baseline so sánh: **R3 re-pin 2026-07-12 (sau đóng MOM_N/MOM_S): CAGR 27.84% / Sharpe 1.84 /
  MaxDD −18.2% / Calmar 1.53** @50B (registry section RE-PIN 2026-07-12).
- Bối cảnh live: BAL/LAG đang RỖNG (NEUTRAL parking từ ~04/2026) — đúng tình huống user mô tả.
  Nghĩa là nếu sleeve này go-live, nó **đổi thành phần vị thế thật của SpaceX/ZaloPay ngay** (thay
  rổ parking), khác dự án w_LAG (dormant). Bù lại, scope này CHƯA chạm gì — chỉ plan.

## 2. Đối chiếu cơ chế ĐÃ CÓ (điểm 1 dispatch) — tránh phát minh lại

### 2.1 custom30V NEUTRAL parking — sleeve hiện tại đã làm 2/3 việc user muốn

| Trục ý tưởng user | custom30V parking hiện tại | Còn khác gì? |
|---|---|---|
| Lấp chỗ khi BAL/LAG rỗng | ĐÚNG vai trò này: park 70% **idle cash** ở NEUTRAL | không khác |
| Tỷ trọng co giãn theo BAL | ĐÃ co giãn: sleeve = 0.70 × idle, idle tự lớn khi BAL rỗng | không khác (§4) |
| Buy-and-hold, xoay quý | rebal q2m5 (quý, +5 ngày sau cụm deadline BCTC — đã được thống kê Release_Date xác nhận gần tối ưu, registry 2026-07-07 nhánh C) | không khác |
| Rổ nhỏ chất lượng cao | **KHÁC**: 30 mã, chọn theo VALUE (yieldcombo 1/PE+1/PCF), gate 8L ≤3, cap 0.10 | **← phần mới thật** |
| Giữ ở BULL/EX-BULL | **KHÁC**: NEUTRAL-only {3:0.7}; BULL/EXBULL idle nằm cash | **← phần mới, tiền lệ chống (§2.2)** |

### 2.2 "Bull parking (30, 0.15) = OVERFIT" + toàn bộ tiền lệ BULL-extension — PHẢI hiểu trước khi lặp lại

Truy nguồn đầy đủ (điểm 1b dispatch). Ghi chú "(30, 0.15)" trong canonical là spec rổ custom30V
biến thể **cap 0.15 thay vì 0.10** — bị loại vì walk-forward (Spyros risk-review 2026-06-24 ghi
rõ: "Rổ (30,0.15) đã bị loại (walk-forward overfit). Giữ production spec (30, cap 0.10)"; nó nằm
luôn trong danh sách attack chuẩn của quant-skeptic: `param_overfit((30,0.15) trap)`). Tức là:
**không phải "rổ 30 quá lớn" — mà là NỚI CONCENTRATION (cap 0.15) trông đẹp full-period nhưng không
sống qua walk-forward.** Trực tiếp liên quan ý tưởng mới: rổ 8 mã equal-weight = cap hiệu dụng
0.125/tên, còn đậm hơn 0.15 → gate walk-forward + concentration diagnostic phải chặt (§7).

Tiền lệ mở rộng regime (BULL/EXBULL), cả 4 lần đo độc lập, kết quả nhất quán:

| Tiền lệ | Kết quả | Vì sao chết |
|---|---|---|
| R2 bull-park custom30V @50B (`PARK_STATES 3:0.7,4:0.7`) | CAGR +1pp nhưng **Sharpe 1.82 < 1.87**, lumpy, hại 2024/25 → không default <150B | đổi return lấy risk xấu hơn |
| custom30B (pemom vehicle cho BULL) walk-forward | **FAIL**: IS −8pp → OOS +28pp (đảo dấu); edge = trọn regime 2020-21/2024-25 | IS 2014-19 chỉ **53 bull-days** (≈ mỗi 2018) → không có mẫu IS để kiểm |
| R5 conditional bull-park (breadth≥0.60) | robust nhưng **+0.49pp marginal** → opt-in, không default | edge mỏng |
| **DC-book CÂU 1 (2026-07-06)** — test đúng câu "NEUTRAL-only vs +BULL vs +EXBULL" | +BULL: FULL +0.88pp nhưng **IS ÂM**, toàn bộ edge = 2020 (+6.91pp) + 2021 (+9.20pp), **2018/2024/2025 đều ÂM**; +EXBULL: +0.01pp, Sharpe giảm → **GIỮ NEUTRAL-only** | reshuffle-luck 2 năm, LOO bác |

Kết luận cấu trúc (không phải ý kiến): idle cash trong BULL **có thật và không nhỏ** (406 ngày
BULL, cash mean 30.1% NAV — DC CÂU 1 đã đo), nhưng mọi cách deploy nó từng thử đều không qua
walk-forward vì IS gần như không có bull-days. Thêm nữa THREAD (c): value có IC đỉnh ở BULL
(+0.156) — nghĩa là nếu extension có bao giờ hoạt động, vehicle phải là VALUE, không phải
quality/momentum. Trial 4 ở §6 kế thừa đúng bài học này.

### 2.3 DC-book (ConvergePort) waterfall — tránh dẫm chân

DC-book (paper từ 07-06) đứng giữa: **BAL/LAG → DC (double-confirm sector-lens ∧ 8L ≤2, cap gộp
0.15, floor 3B) → custom30V**. Khác biệt bản chất với sleeve đề xuất: DC là membership **event/
signal-driven** (sector-lens BUY phải sống), sleeve user muốn là rổ **cố định xoay quý**. Để không
chồng cơ chế:
- Scope này đo sleeve mới như **vehicle A/B thay custom30V trong R3** (baseline production KHÔNG
  có DC — DC vẫn đang paper). KHÔNG thêm tầng waterfall thứ 4.
- Nếu về sau CẢ DC lẫn Q-sleeve cùng được duyệt live → phải đo lại thứ tự ưu tiên + cap gộp
  per-name (bài học nhánh A: cộng dồn tự do từng lên 20.1% NAV/tên). Đó là việc TƯƠNG LAI có điều
  kiện, khai báo trước để không quên, không nằm trong N của plan này.
- DSR tiền lệ đáng nhớ: DC excess DSR 0.111-0.775 << 0.95 — sleeve-on-parking là vùng
  insurance-grade, hiếm khi là alpha. Kỳ vọng cho Q-sleeve cũng phải đặt ở mức đó.

### 2.4 AlphaLens 4 mã — dùng làm cảm hứng, KHÔNG dùng làm evidence

- Paper mới chạy từ 2026-07-01, chưa có kết quả (tracking đến 09-30, n=1 window) — không phải
  bằng chứng cho hay chống.
- **Không được backtest hard-list {FPT,ACB,MBB,HDB} chọn năm 2026 rồi chạy ngược về 2014** —
  survivorship/curation bias kinh điển, quant-skeptic sẽ bác ngay (attack `panel_curation`).
  Muốn "chất lượng cao" phải là **RULE chọn được as-of từng quý** (§3). Hard-list chỉ dùng làm
  diagnostic overlap (rổ rule-based chọn ra có chứa các tên AlphaLens ở các quý gần đây không).

## 3. Định nghĩa "chất lượng cao" (điểm 2 dispatch) — 2 định nghĩa cụ thể, PIT-được

Cả 2 đều dùng cột có sẵn (BQ `ticker`/`ticker_financial` + bảng `fa_ratings*` as-of), builder
`custom_basket.build_pit()` đã hỗ trợ `top_n`/`gate_rating`, thêm quality-floor là knob nhỏ:

- **Đ1 — "quality-gated value" (khuyến nghị chính):** gate cứng 8L rating ≤ **2** (as-of, chặt hơn
  production ≤3) ∧ floor thanh khoản `Trading_Value_1M_P50 ≥ 5B` → rank **yieldcombo**
  (1/PE+1/PCF) lấy top-N, equal-weight. Căn cứ: rating đã validate ở vai trò GATE nhị phân (không
  phải tilt); value là return-engine duy nhất sống mọi regime (THREAD c); floor 5B vì slot rổ nhỏ
  to hơn (@50B×0.7 idle /8 tên ≈ 3-4B/tên, cần ADV tương xứng — cùng logic floor DC nhánh B).
- **Đ2 — "quality-floor fundamentals":** floor ROE_Min5Y ≥ 0.10 ∧ CF_OA_3Y > 0 ∧ FSCORE ≥ 5
  (đều là cột sẵn) thay cho gate rating, phần còn lại như Đ1. Căn cứ: đây là dạng "golden floor"
  mạnh hơn floor production (ROE_Min3Y≥0 ∧ CF_OA_3Y>0); độc lập với bảng fa_ratings (bớt phụ
  thuộc freshness của bảng vừa mới fix cron 07-12).
- KHÔNG đề xuất định nghĩa thứ 3 (vd track-record/moat) — registry đã ghi track-record cao
  underperform về return; giữ N nhỏ.

## 4. Cơ chế tỷ trọng co giãn theo BAL (điểm 3 dispatch) — công thức đã có sẵn, chỉ cần nói rõ

Engine (`pt_v23_audit_2014.py` / `simulate_holistic_nav.py`) mỗi ngày t:

```
idle_t   = NAV_t − BAL_deployed_t − LAG_deployed_t        (phần 2 book không dùng)
sleeve_t = PARK_FRAC(state_t) × idle_t                    (production: {NEUTRAL: 0.70})
```

⇒ `sleeve_t` **tự động** = hàm giảm của BAL_deployed — chính xác "càng BAL deploy ít, sleeve càng
lấp vào nhiều" mà user mô tả, đã chạy live (SpaceX hiện ~70% NEUTRAL parking chính vì BAL/LAG
rỗng). **Không cần công thức mới**; tham số tự do duy nhất là PARK_FRAC theo state — và 0.70 đã
được chốt 2 lần (job _130720 và sweep NAV-nhỏ 07-09: premise "NAV nhỏ đẩy 90%" REFUTED). Plan này
**không tune lại PARK_FRAC** (khai báo trước — đổi nó là trial khác, đã có 2 nghiên cứu đứng).
Phần "co giãn" duy nhất còn mở là **state coverage** (thêm 4/5 hay không) = trial 4 §6.

## 5. Kỳ vọng & ràng buộc khai báo trước (điểm cảnh báo)

- **Concentration cost có thật**: 8 tên equal-weight = 12.5%/tên sleeve; khi sleeve ~70% NAV
  (tình trạng hiện tại) = ~8.75% NAV/tên — sát trần tinh thần 10% NAV. 1 tên gãy kiểu DGC (án
  hình sự, mất thanh khoản) = −12.5% sleeve kẹt cứng. Đây là chi phí cấu trúc mà 30-mã/cap-0.10
  không có; diagnostic name-risk là gate bắt buộc (§7).
- **Prior từ mọi nghiên cứu quality-selector**: composite v3 as-selector thua custom30V **mọi
  window** (top20: Full −11.2pp, OOS −14.7pp); 8L drop-in swap fail; quality sector-sweeps 9 lần
  = "lens, not standalone book". Chưa có 1 selector thiên-quality nào thắng yieldcombo trong vai
  trò NAV-vehicle trên data này.
- **Kỳ vọng khai báo: −0.5..+0.5pp CAGR vs R3; xác suất chủ quan NO-GO > 60%.** Giá trị kỳ vọng
  nếu GO nghiêng về **DD/Calmar cải thiện** (rổ chất lượng rơi ít hơn trong sell-off) hơn là CAGR
  — đúng khung "insurance, not alpha" của cả DC lẫn DT5G. Nếu ra +2pp CAGR → nghi bug/leak trước.

## 6. Family pre-registered — sổ N-ledger "Q-SLEEVE": **N = 5, đóng tại đây**

Câu hỏi nghiên cứu chính xác: *"Rổ nhỏ quality-gated (top-N, equal-weight, q2m5) làm parking
vehicle có cải thiện OOS-robust so với custom30V trong R3 không; và extension NEUTRAL→+BULL/EXBULL
có sống qua LOO không?"*

Khai báo TRƯỚC những gì KHÔNG đo (mỗi cái nếu muốn = trial mới xin duyệt riêng):
- KHÔNG tune PARK_FRAC (0.70 đứng, 2 nghiên cứu bảo chứng — §4), KHÔNG tune cap/weight-scheme
  (equal-weight cố định — đổi sang capwt/namecap là trial khác), KHÔNG sweep floor thanh khoản,
  KHÔNG thử N ngoài {8,12}, KHÔNG hard-list AlphaLens, KHÔNG thêm tầng waterfall.

| # | Trial | Config | Giả thuyết |
|---|---|---|---|
| 1 | **Q8-NEU** | Đ1, top_n=8, equal-weight, floor 5B, q2m5, NEUTRAL-only {3:0.7} | rổ nhỏ chất lượng > 30 mã đa dạng? |
| 2 | **Q12-NEU** | như 1, top_n=12 | điểm giữa concentration↔diversification (8 và 12 làm sensitivity lẫn nhau) |
| 3 | **QF8-NEU** | Đ2 (quality-floor fundamentals) thay Đ1, top_n=8 | định nghĩa quality nào tốt hơn — chỉ 1 biến thể |
| 4 | **Winner + BULL-ext** | winner của 1-3 chạy thêm `PARK_STATES 3:0.7,4:0.7,5:0.7` | đúng ý user "NEUTRAL trở lên"; prior chống mạnh (§2.2), gate LOO riêng cứng |
| 5 | **LOO gộp** cho winner (per-year 13 phép + ex-2021/ex-2020) | chỉ đọc, không đổi lựa chọn |

Control = R3 re-pin chạy lại contemporaneous cùng cache-vintage (không tính N). KHÔNG mở thêm
test sau khi chạy; muốn thêm → dừng, xin user duyệt N mới.

**Harness**: `pt_v23_audit_2014.py` @50B, đúng lệnh pin + **`BQ_LOCAL_CACHE=1 BQ_CACHE_THREADS=1`**
(bài học re-pin 07-12), knob mới qua env (vd `BASKET_TOP_N=8 BASKET_GATE_RATING=2
BASKET_WT=equal BASKET_LIQ_FLOOR_B=5` — `build_pit()` đã có param `top_n`/`gate_rating`, phần
plumbing env + equal-weight + quality-floor Đ2 ước ~15-30 dòng, unset = byte-identical baseline),
output tag **`_exp_qsleeve*`** (không thể đè canonical, guidelines §8). Self-check 0 VND bắt buộc
mỗi run. Nguồn dữ liệu: tra `mike/kb/data_registry.md` trước khi wire (state = `vnindex_5state_dt5g_live`
qua đúng đường harness; rating as-of từ bảng fa_ratings đã có cron — check freshness trước run).

## 7. Gate GO/NO-GO (CP-QS1, checkpoint duy nhất)

Winner (trial 1-3) phải đạt TẤT CẢ so control cùng cache-vintage:

| Gate | Tiêu chí |
|---|---|
| OOS 2020+ | CAGR **và** Calmar ≥ control |
| IS 2014-19 | Không tệ hơn control quá 0.3pp CAGR |
| Per-year LOO | Delta vs control KHÔNG âm mọi năm bỏ-ra, đặc biệt **ex-2021/ex-2020** |
| Tail | MaxDD không xấu hơn control (≈−18.2%) |
| Concentration diagnostic | max name-weight %NAV theo ngày + drawdown-contribution per-name; 1 tên đóng góp >40% tổng edge → FAIL (name-luck) |
| Capacity | fill-shortfall @50B với slot 3-4B/tên không tăng vật chất vs control |
| DSR | ≥ 0.95 trên NAV daily winner, N=5 khai báo |
| PBO | family 5 < 8 → không bắt buộc; LOO thay thế |
| quant-skeptic | CONFIRMED bắt buộc trước khi trình user |

**Gate RIÊNG cho trial 4 (BULL-ext), chặt hơn vì tiền lệ**: mọi tiêu chí trên **VÀ** per-year
delta của phần extension KHÔNG âm ở **2018, 2024, 2025** (ba năm bull mà mọi tiền lệ đều âm —
đây là chỗ chết cũ) **VÀ** drop-2020+2021 tổng delta vẫn ≥ 0. Fail bất kỳ → extension NO-GO
nhưng winner NEUTRAL-only vẫn được xét độc lập (2 quyết định tách nhau).

NO-GO = đóng nhánh, ghi registry, không wire. GO ≠ wire: GO = trình user sign-off; wire live cần
duyệt riêng (đổi vehicle parking chạm tiền thật NGAY vì SpaceX đang 100% parking — khác dự án
w_LAG dormant) + re-pin baseline + quant-skeptic verify code change.

## 8. Rủi ro / caveat khai báo trước

1. **Idiosyncratic risk rổ 8 mã** — 12.5%/tên sleeve; bài học "(30,0.15)" cho thấy chính trục
   concentration là chỗ walk-forward hay bác nhất. Gate concentration diagnostic là án tử.
2. **BULL-extension đi ngược 4 tiền lệ đo độc lập** (§2.2) — trial 4 chạy vì đúng nuance ý user,
   nhưng user cần chấp nhận TRƯỚC: xác suất NO-GO trục này rất cao, và NO-GO là kết luận hợp lệ.
3. **fa_ratings freshness**: Đ1 phụ thuộc bảng fa_ratings (cron weekly mới fix 07-12, lần chạy
   scheduled đầu 07-18). Nếu wire live mà cron gãy → rổ đông cứng. Đ2 là hedge (không phụ thuộc).
4. **Quality theo mùa BCTC**: rating/fundamentals as-of đổi theo quý — rổ "cố định" thực tế vẫn
   churn ở rebal q2m5; phải báo turnover thật (kỳ vọng thấp hơn custom30V vì pool quality hẹp,
   nhưng phải ĐO, không giả định).
5. **Path-divergence noise**: đổi vehicle parking đổi path NAV từ 2014 — đọc kết quả ở mức cửa
   sổ + LOO (chuẩn Scope A/V2.5), không đọc 1 số FULL đơn lẻ.
6. **Nếu DC-book sau này go-live**: cần đo lại tương tác (cap gộp per-name, thứ tự waterfall) —
   khai báo trước là việc có-điều-kiện tương lai, không nằm trong N này.
7. **AlphaLens không phải evidence** — n=1 paper window, chỉ là cảm hứng; kết quả AlphaLens
   09-30 dù đẹp hay xấu cũng KHÔNG thay được backtest này (và ngược lại).

## 9. User cần quyết (3 câu riêng biệt)

1. **Duyệt chạy family Q-SLEEVE** (§6, N=5, gate §7)? Kỳ vọng khai báo −0.5..+0.5pp, prior
   NO-GO>60% — đo vì gap "rổ nhỏ quality làm parking vehicle" chưa ai đo đúng config, và chi phí
   đo thấp (builder có sẵn knob). Nếu user thấy prior thế là đủ để bỏ → đóng nhánh không tốn
   compute cũng là quyết định hợp lệ.
2. **Chấp nhận trước prior chống trục BULL-extension** (trial 4): NO-GO trục này = kết luận hợp
   lệ, không mở thêm biến thể extension khác (breadth-gate, EXBULL-only, v.v.) trong N này.
3. Nếu duyệt: xác nhận scale **maintenance trial gọn** (1 checkpoint CP-QS1, ~2-3 ngày compute,
   không mở chương trình nhiều phase), NO-GO = đóng nhánh ghi registry.
