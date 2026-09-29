# PLAN PRE-REGISTERED — Margin theo KHOẢNG CÁCH ĐỊNH GIÁ (valuation spread), không theo regime state

> Job `Taylor_20260823_075808` · Phase 0 (bằng chứng mô tả + plan) hoàn tất 2026-08-23.
> **Phase 1 CHƯA CHẠY** — file này viết TRƯỚC khi biết kết quả engine-tier, đúng kỷ luật pre-registration.
> Mandate user 2026-08-23 (thread Taylor 1521735922066919515): *"đưa margin vào thành một cơ chế hợp
> lý chứ không lảng tránh nó"*, trigger = gap giữa earnings/cổ tức của thị trường so với tiết kiệm.

---

## §0. Phạm vi & điều KHÔNG làm

| Làm | Không làm |
|---|---|
| Đo xem **spread định giá tuyệt đối** (EY/DY vs lãi suất tiết kiệm & lãi vay) có phải điều kiện arm đòn bẩy tốt hơn/bổ sung cho cổng `dd52<=-20%` đang chạy | KHÔNG đề xuất bỏ DT5G, KHÔNG mở lại V2.5 (lever theo regime state, đã NO-GO 2026-07-12) |
| Kênh truyền dẫn = **rổ CAPIT** (kênh đã được duyệt, `capit_margin_lever`) | KHÔNG nới đòn bẩy ra toàn sổ (họ rủi ro KHÁC, chưa nghiên cứu, chưa duyệt — `known_limits` của chính rule đó ghi rõ) |
| Ngưỡng **TUYỆT ĐỐI** neo vào lãi suất (không có tham số fit) | KHÔNG dùng percentile định giá (`pe_pctile`, value_radar) — đã bị bác 2 lần, và Phase 0 đo lại thấy percentile FAIL khi ép point-in-time (§2.4) |

---

## §1. Việc đã đóng — không lặp lại (đọc trước khi phản biện plan này)

| Đã thử | Kết quả | Nguồn |
|---|---|---|
| V2.5 lever theo **regime state** (state-blind + PE-pctile), toàn vehicle | 🔴 NO-GO 2026-07-12 — IS-artifact (IS +1,88 / OOS −0,05), DSR 0,18-0,56, 1 episode hiệu dụng | `kb/projects/v2.5-leverage-nogo.md` |
| **Xu hướng** lãi suất huy động làm de-risk gate (Pillar A′) | 🔴 NO-GO 2026-07-13, 0/4 GO | `kb/projects/wc-deposit-rate-gate.md` |
| Lever gated bằng **`pe_pctile<=0,20`** trên washout CAPIT | 🔴 LÀM XẤU ĐI: N=17 washout, G3 (+6,16%) < G4 phần bù (+12,26%) | `research/margin_kelly_feardriven_washout_20260803.md` §4.1 |
| Lever gated bằng **`dd52<=-20%`**, f=1,3, CAPIT-only | 🟢 ĐANG LIVE (`trading_rules.json::capit_margin_lever`, user chốt 2026-08-22): dCAGR +0,663pp FULL (IS +0,487/OOS +0,832), DSR 1,0, PBO 0,10-0,14, N=15 event | `research/margin_kelly_engine_confirmation_20260803.md` |

**Hệ quả cho plan này:** margin **đã** là một cơ chế hợp lý trong hệ (không còn "lảng tránh"), nhưng
điều kiện arm hiện tại là **độ sâu drawdown**, không phải khoảng cách định giá. Câu hỏi Phase 1 vì vậy
**KHÔNG** phải "spread có dự báo được không" (Phase 0 cho thấy có) mà là:

> **H1 (câu hỏi duy nhất đáng chạy):** spread định giá tuyệt đối có mang thông tin **THÊM** so với
> `dd52<=-20%` đã có — đo ở tầng danh mục, sau chi phí vay — hay chỉ đang tìm lại cùng những sự kiện đó?

Biến của user **KHÁC** biến đã bị bác: `pe_pctile` là **percentile tương đối so với lịch sử của chính
nó** (mù với lãi suất); spread là **mức tuyệt đối so với chi phí vốn**. Hai cái tách nhau đúng ở chỗ
quan trọng nhất: 2011-2012 cổ phiếu RẺ theo percentile nhưng deposit 14%/margin ~19% ⇒ spread ÂM
(và thực tế lỗ nặng: net12 −17,1pp / −26,7pp); 2020-07 percentile chỉ trung bình nhưng deposit 5,7%
⇒ spread +1,01pp (net12 +53,4pp). Đây là cơ chế, không phải trùng hợp — nhưng vẫn phải chứng minh.

---

## §2. PHASE 0 — BẰNG CHỨNG ĐÃ ĐO (mô tả, không tối ưu tham số)

Artifact: `research/margin_valuation_spread_20260823/` (`monthly_spread_series.csv` 224 tháng,
`episodes_*.csv`, 4 script `analyze_spread*.py`, 2 file SQL). Universe = `tav2_mike.universe_pit`
(CANONICAL, point-in-time), giá/PE/DY từ `tav2_bq.ticker`, OShares join PIT theo `Release_Date`.

### 2.1 Chuỗi dựng được (A1)
- **EY_mkt**: `ey_agg` (cap-weighted, = ΣE/ΣMC trên phần PE>0) và `ey_med` (median 1/PE). 2008-01→2026-08.
- **DY_mkt**: `dy_agg` (cap-weighted), `dy_med_payers` (median của các mã CÓ trả cổ tức), `dy_ew`.
  **Ngữ nghĩa đã kiểm chứng, không đoán**: `Dividend_1Y` = **VND/cổ phiếu** (VNM 2015 = 4.000đ),
  `DY` = `Dividend_1Y / Price` (giá THÔ, không phải `Close` điều chỉnh — kiểm bằng VNM 2015-06:
  PE/DY biến động hàng ngày đúng theo `Price`), join tôn trọng `Release_Date` ⇒ **PIT hợp lệ**.
- **deposit_12m**: `deposit_rate_vn.deposit_events_df()` — chỉ có từ **2011-01**. 2008-01→2010-12
  dùng **proxy** = SBV refi (`sbv_macro_overlay.SBV_REFI_EVENTS`) + 0,50pp (median spread đo trên
  188 tháng chồng lấn, IQR [0,00; 1,50]). Cột `deposit_src` đánh dấu từng dòng.
- **margin_rate = deposit_12m + 5,0pp** — **GIẢ ĐỊNH**, neo vào số thật hiện tại (SpaceX RocketX
  12,5% vs deposit 6,8% ⇒ +5,7pp). Sensitivity +4/+6pp trong Phase 1. Không tìm được chuỗi lịch sử
  lãi margin CTCK VN nào đáng tin ⇒ **đây là mắt xích yếu nhất của toàn bộ phân tích**, phải nói rõ
  mỗi lần trích số.

### 2.2 Trả lời trực tiếp câu hỏi của user (A2) — **user nhớ ĐÚNG, nhưng cần chính xác hoá**
| Mệnh đề | Verdict | Số |
|---|---|---|
| "Có giai đoạn cổ tức tiền mặt vượt lãi suất huy động 1 năm" | ✅ **XÁC NHẬN** cho **nhóm cổ phiếu trả cổ tức** | 38/224 tháng, **4 episode độc lập**: 2012-09→2013-10, 2015-03→2016-12, 2020-03, 2020-07→10. Đỉnh 2012-11: DY median payer **11,49%** vs deposit **9,0%** (+2,49pp) |
| Điều đó có đúng ở **cấp chỉ số** (cap-weighted) không | ❌ **BÁC BỎ** | `dy_agg` max 6,30%; deposit min 4,70% ⇒ **KHÔNG BAO GIỜ** ≥ deposit trong 2008-2026 |
| Độ rộng cơ hội | — | tối đa **42,0% universe** có DY ≥ deposit (2009-02); median lịch sử 21,5%; **hôm nay 14,2%** |
| EY thị trường (cap-wtd) có bao giờ vượt **lãi vay** | ❌ **KHÔNG** — max spread3 = **−0,72pp** (2009-02) | Vay để mua "cả thị trường" chưa bao giờ có lãi dương kỳ vọng theo thước đo này |
| EY của **cổ phiếu median** có vượt lãi vay | ✅ có, 35/224 tháng, **9 episode** | đỉnh 2009-02: EY_med 20,12% vs margin 13,50% (+6,62pp) |

### 2.3 Carry ròng sau chi phí vay (A3/A4) — **có lãng phí cơ hội thật**
Baseline vô điều kiện (211 tháng có fwd12): fwd12 median **+8,0%**, net12 (fwd12 − margin_rate)
median **−4,9pp**, chỉ **43%** số tháng vay-có-lời. Tức **vay mù là lỗ kỳ vọng** — đúng như hệ đang giả định.

| Điều kiện (TUYỆT ĐỐI, không fit) | N episode | fwd12 median | net12 median | % episode net12>0 |
|---|---|---|---|---|
| DY(median payer) − deposit ≥ 0 | **4** | +44,0% | **+30,2pp** | 75% (3/4) |
| EY(median) − margin ≥ 0 | **9** | +19,5% | **+8,7pp** | 67% (6/9) |
| EY(median) − margin ≥ +1pp | 6 | +42,5% | +27,9pp | 67% (4/6) |
| Baseline | — | +8,0% | −4,9pp | 43% |

**Dose-response đơn điệu** (bằng chứng mạnh nhất ở N nhỏ, skill §10) — chia 211 tháng theo ngũ phân vị
spread `DY(payer)−deposit`: net12 median **−22,5 → −18,0 → −1,1 → 0,0 → +9,0pp**, tỷ lệ vay-có-lời
**14% → 24% → 43% → 50% → 86%**. Hình dạng này giữ nguyên khi: bỏ hẳn 2008-2010 (chỉ dùng anchor
Big-4 thật, n=175), chỉ 2014+ (n=139), và khi phạt proxy 2008-2010 thêm +2pp bất lợi.

**N THẬT = 4 (trục DY) / 9 (trục EY) / 7 (hợp)** — KHÔNG phải 38 hay 35 tháng (cửa sổ chồng lấn).
Sign test 3/4 ⇒ p=0,31; 6/9 ⇒ p=0,25 — **KHÔNG có ý nghĩa thống kê trên tần suất**. Công cụ phù hợp
với N này: **leave-one-episode-out + bootstrap theo episode**, KHÔNG phải t-test/walk-forward tần suất.
LOO (sp≥0, net12): bỏ 2020-03 ⇒ median tụt 30,2 → 7,0pp; bỏ 2015-03 ⇒ 3/3 dương. ⇒ **kết luận phụ
thuộc nặng vào 2020**, đúng dạng rủi ro đã giết V2.5.

### 2.4 Cái BẪY đã đo được (quan trọng nhất của Phase 0)
Nếu định nghĩa "spread cực đoan" bằng **percentile của chính chuỗi spread** (expanding 80th pct,
tối thiểu 36 tháng lịch sử, không look-ahead) thì kết quả **ĐẢO CHIỀU**: 8 episode, net12 median
**−6,9pp**, chỉ **38%** dương — vì ở giai đoạn 2011-2016 ngưỡng expanding còn thấp nên nó arm đúng lúc
spread vẫn ÂM tuyệt đối (−2,10 / −1,50 / −1,29pp). Cùng bộ dữ liệu, ngưỡng full-sample (có look-ahead)
lại đẹp. ⇒ **Phase 1 CẤM mọi ngưỡng dạng percentile; chỉ dùng mốc tuyệt đối neo vào lãi suất.**
Đây cũng là lời giải thích cơ chế cho việc `pe_pctile` bị bác ở p1 2026-08-03 — thống nhất, không mâu thuẫn.

### 2.5 Mâu thuẫn kiến trúc với DT5G (A5) — CÓ THẬT, và cách hoà giải
Trong 26 tháng có spread ≥ 0 kể từ 2014: **5 tháng DT5G = CRISIS (trần 0%)**, 2 tháng BEAR (20%),
18 tháng NEUTRAL, 1 tháng BULL. Episode **tốt nhất toàn mẫu (2020-03, net12 +68,3pp) rơi đúng vào
CRISIS** — tức lúc DT5G cắt sạch exposure. Đây là mâu thuẫn thật, không né được.

**Đề xuất hoà giải (KHÔNG bỏ DT5G, không override):** đòn bẩy chỉ **arm ở PHA HỒI PHỤC** —
spread ≥ mốc tuyệt đối **VÀ** base state đã **thoát CRISIS** (state ≥ 2). Ba lý do hội tụ:
(a) khớp conviction của user (*asymmetric edge = recovery crisis→bear + cheap valuation, not exbull leverage*);
(b) khớp số của p1: washout ở `state>=3` (+13,87%, p=0,006) tốt hơn hẳn `state<=2` (+5,11%, p=0,348);
(c) episode 2020-07 (state 3, spread +1,01pp, net12 +53,4pp) vẫn được giữ; chỉ mất 2020-03.
Chi phí của việc hoà giải này phải được ĐO ở Phase 1 (biến thể V5 vs V2), không được giả định.

### 2.6 Trạng thái hôm nay (2026-08-21) — **cơ chế sẽ KHÔNG arm**
EY_med 9,24% · EY_agg 7,96% · DY payer 5,17% · deposit 6,80% · margin(gt) 11,80% ·
spread(DY−dep) **−1,63pp** · spread(EY_med−margin) **−2,56pp** · breadth 14,2% · DT5G NEUTRAL · dd52 −8%.
⇒ Không có hành động live nào phát sinh từ nghiên cứu này ở thời điểm hiện tại.

---

## §3. Nguồn dữ liệu + caveat bắt buộc mang theo (đã tra `kb/data_registry/`)

| Nguồn | Status | Caveat phải trích kèm mỗi lần dùng |
|---|---|---|
| `tav2_mike.universe_pit` | CANONICAL | point-in-time thật, 2000-12→2026-08 |
| `tav2_bq.ticker` (PE/DY/Price) | CANONICAL | PE/DY là tỷ số lưu sẵn trên **giá THÔ `Price`**, KHÔNG phải `Close` |
| `tav2_bq.ticker_financial` (OShares, Dividend_1Y) | CANONICAL | join bằng `Release_Date <= t`; `EPS` trong bảng này là **1/PE**, KHÔNG phải VND/cp (bẫy) |
| `deposit_rate_vn.py` | CANONICAL-PROXY | ⚠️ **26 mốc neo hồi tố CÙNG 1 lần 2026-06-19 ⇒ KHÔNG point-in-time thật cho quá khứ**. Mọi kết luận lịch sử mang bias hindsight ở mức "biết đúng hình dạng chu kỳ lãi suất". Không thể khắc phục bằng code — chỉ có thể công bố |
| `sbv_macro_overlay.SBV_REFI_EVENTS` | CANONICAL | dùng làm proxy deposit 2008-2010; pre-2011 có sai số ngày ±1-2 tháng theo chính docstring |
| `tav2_bq.vnindex_5state_dt5g_live` | CANONICAL | 2014-01-02→; mã state 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL |
| lãi suất **margin** lịch sử | ❌ **KHÔNG CÓ NGUỒN** | giả định deposit+5pp; đây là rủi ro mô hình lớn nhất, phải sweep |

**3 lỗ hổng dữ liệu phải xử lý ở Phase 1 (không được lờ đi):**
1. **DY là cổ tức ĐÃ TRẢ 12 tháng qua** ⇒ trong khủng hoảng nó phồng lên đúng lúc cổ tức sắp bị CẮT
   (value trap). Test bắt buộc: so `Dividend_1Y` tại t với `Dividend_1Y` tại t+12M cho chính rổ đó.
2. **"Median payer" đổi thành phần theo thời gian** (số mã trả cổ tức tăng khi thị trường rẻ) ⇒ phải
   có biến thể tính spread trên **chính rổ danh mục V2.4** thay vì trên universe.
3. **Không phân biệt được cổ tức tiền mặt với cổ tức cổ phiếu** trong `Dividend_1Y` — phải đối chiếu
   mẫu với `corp_action` (Winston) trước khi coi DY là "tiền mặt".

---

## §4. Họ chính sách — **N_trials = 7, khai TRƯỚC khi chạy**

Kênh truyền dẫn: **CAPIT sleeve** (đúng kênh `capit_margin_lever` đang live). Đòn bẩy = nhân hệ số f
vào capital target của CAPIT, y hệt `apply_capit_lever()`; KHÔNG đụng %ADV cap.

| # | Điều kiện ARM (tất cả TUYỆT ĐỐI) | f | Vai trò |
|---|---|---|---|
| **V0** | `dd52<=-20%` (production hiện tại) | 1,3 | **CONTROL** — không tính vào N_trials |
| V1 | `EY_med − margin ≥ 0` | 1,3 | spread vay thuần |
| V2 | `EY_med − margin ≥ +1,0pp` | 1,3 | bậc thang liều |
| V3 | `DY_payer − deposit ≥ 0` | 1,3 | trục cổ tức (đúng chữ của user) |
| V4 | V1 **hoặc** V3 | 1,3 | hợp 2 trục |
| V5 | V2 **và** DT5G base state ≥ 2 (đã thoát CRISIS) | 1,3 | **hoà giải kiến trúc §2.5** |
| V6 | V5 | 1,5 | liều đòn bẩy (trần ruin p1: gross 1,5 ⇒ equity/ts 55,5% tại MAE xấu nhất) |
| V7 | `dd52<=-20%` **hoặc** V5 | 1,3 | **test GIA TĂNG — câu hỏi H1 thật sự** |

Disarm (chung cho mọi biến thể, khai trước): spread rơi xuống dưới mốc arm trừ 0,5pp (hysteresis,
tránh nhấp nháy) **HOẶC** DT5G về CRISIS **HOẶC** drawdown của chính danh mục kể từ lúc arm ≤ −12%
**HOẶC** quá 12 tháng kể từ lúc arm. Disarm = ngừng vay MỚI + trả dần theo dòng tiền bán, KHÔNG bán
cưỡng bức (bán cưỡng bức lúc spread rộng là đúng chiều sai).

**Mô hình gọi ký quỹ / cưỡng chế bán (bắt buộc, không được bỏ):** gói RocketX 1840, `initial_rate`
0,5 (đã xác nhận trong `trading_rules.json`). **Tỷ lệ ký quỹ duy trì THẬT chưa có trong registry** ⇒
**việc chặn đầu tiên của Phase 1**: hỏi Mafee/DNSE lấy con số hợp đồng. Trước khi có: mô phỏng ở
maintenance 30%/35%/40% equity ratio, forced-sell tại giá mở cửa T+1 + slippage 0,5%. Bất kỳ biến
thể nào phát sinh margin call ở kịch bản 40% ⇒ **loại thẳng**, không cần xét lợi nhuận.

---

## §5. Chi phí (khai trước, không đổi giữa chừng)
- Lãi vay: **10%/năm** (quy ước `CLAUDE.md`) là leg chính; **12,5%/năm** (số thật SpaceX) là leg đối
  chứng bắt buộc; **15%/năm** làm stress. Lãi tính trên dư nợ thực tế theo ngày.
- TC **0,1%/chiều** trên phần vốn thực giao dịch; lãi tiền gửi nhàn rỗi 0%/năm.
- Quy đổi thực tế khi báo cáo: **CAGR thật ≈ CAGR backtest − 1,5%**.
- Slippage forced-sell 0,5% (chỉ trong kịch bản margin call).

## §6. Phương pháp
1. **Episode-windowed sim** ±60 phiên giao dịch quanh mỗi episode arm, **cùng path nền**
   (điều kiện tái xét (b) của V2.5 — KHÔNG diff 2 full-run, tránh lẫn path-divergence noise).
2. Harness: `pt_v23_audit_2014.py` cấu hình production R3 (`LAG_ADV_BASIS=price`, `PARK_STATES="3:0.7"`,
   `NAV_TOTAL_B=50`, `BASKET_SELECT` hiện hành), `threads=1`, `$DNA_PYEXE`, **stable-sort `(time,ticker)`**
   + chứng minh determinism bằng md5 (bắt buộc, `run_depgate_variant_sorted.py` là mẫu).
3. **Control leg phải tái hiện ĐÚNG số pin R3** (CAGR 28,86 / Sharpe 1,90 / DD −17,8 / Calmar 1,62,
   Final NAV 1.178,01B) trước khi tin bất kỳ treatment leg nào. `self-check 0 VND` trên MỌI leg.
4. **Ràng buộc N không thể vượt qua — nói trước:** harness chỉ chạy từ **2014**, nên trong 9 episode
   trục EY-margin chỉ **3** nằm trong cửa sổ engine (2015-08, 2016-10, 2020-01) và trong 4 episode trục
   DY-deposit cũng chỉ **3** (2015-03, 2020-03, 2020-07). Các episode 2008-2013 — gồm cả hai episode
   mạnh nhất về spread (2009-02 EY−margin +6,62pp, 2012-11 DY−deposit +2,49pp) — **chỉ có bằng chứng
   tầng vị thế, KHÔNG BAO GIỜ có bằng chứng engine**. Đây là lý do §7 không cho phép wire live chỉ
   bằng engine-tier.
5. IS 2014-2019 / OOS 2020+ (OOS là tiebreaker); **LOO theo episode** + bootstrap theo episode.
6. DSR trên chuỗi excess; PBO (CSCV) chỉ khi ≥8 biến thể (hiện 7 ⇒ ghi rõ không chạy PBO, thay bằng
   LOO + dose-response monotonicity).
7. Kiểm tra bắt buộc chống ngộ nhận: **cổ tức tương lai bị cắt** (§3 lỗ hổng 1) và **spread tính trên
   rổ V2.4 thay vì universe** (§3 lỗ hổng 2).

## §7. Cổng GO / NO-GO — viết TRƯỚC khi chạy, không sửa sau
**GO (đủ điều kiện đề xuất wire, vẫn cần quant-skeptic + user duyệt) khi ĐỦ CẢ 6:**
1. V7 (hợp) > V0 (control `dd52` thuần) ở **cả IS và OOS**, delta CAGR OOS **> 0**.
2. Ít nhất **1 biến thể** có delta CAGR FULL ≥ **+0,30pp** VÀ delta MaxDD xấu đi ≤ **0,50pp**.
3. **DSR ≥ 0,95** trên chuỗi excess của biến thể được đề xuất.
4. **LOO theo episode**: bỏ episode đóng góp lớn nhất, delta CAGR vẫn **> 0**. (V2.5 chết đúng ở đây.)
5. **0 margin call** ở kịch bản maintenance 40% và lãi vay 15%/năm.
6. Dose-response **đơn điệu** theo bậc thang spread (V1 → V2 và f 1,3 → 1,5 không được đảo dấu vô cớ).

**NO-GO ⇒ ĐÓNG hướng này** (như Pillar A′ đã đóng), không chuyển sang shadow-monitor, không "để dành".
**Kết quả trung gian** (qua 1-3 nhưng trượt 4-6, hoặc engine-tier N<4 episode độc lập): trần khuyến nghị
tối đa là **paper/shadow-monitor có mốc kết thúc cứng**, KHÔNG được wire live.
Bất kỳ biến thể nào **tốt hơn nhờ arm trong CRISIS** ⇒ loại thẳng (mâu thuẫn DT5G, §2.5).

## §8. Ranh giới LIVE (nếu và chỉ nếu GO)
- Chỉ **SpaceX** (`0002023347`, có margin). **ZaloPay cash-only — ngoài phạm vi tuyệt đối.**
- Chỉ mã có trong danh sách margin DNSE, gói **1840 RocketX** override **theo từng lệnh**, KHÔNG bao
  giờ đổi gói mặc định của tài khoản (1841).
- **Cổng người thứ hai giữ nguyên**: mỗi ngày có lệnh dùng đòn bẩy phải có
  `data/margin_approvals/margin_approval_<acct>_<date>.json` (`approve_margin_day.py`, nay tự chạy khi
  user duyệt plan — commit `322c7f4e`). Thiếu/không khớp ⇒ **gỡ đòn bẩy, lệnh vẫn chạy bằng vốn tự có**.
- Enforcement dùng lại **nguyên xi** `plan.py::apply_capit_lever()` + `_lever_package_audit()` — cơ chế
  mới CHỈ được đổi điều kiện arm, KHÔNG được đẻ đường thực thi thứ hai.
- Trần Σ VND vay hiển thị trong báo cáo 21:00 tính từ **lệnh thật**, không từ artifact (khe hai-trường
  đã biết, `known_limits`).

## §9. Timeline + chi phí compute (ước lượng)
| Bước | Nội dung | Ước |
|---|---|---|
| 0 | **Chặn**: lấy tỷ lệ ký quỹ duy trì thật từ DNSE (dispatch Mafee) + đối chiếu cổ tức tiền mặt vs cổ phiếu (dispatch Winston) | 1 phiên, ~0 compute |
| 1 | Dựng chuỗi spread ở **tầng rổ V2.4** + test cổ tức-bị-cắt | 1 phiên, ~15 phút BQ |
| 2 | Episode-windowed sim: 8 leg (V0-V7) × 3 mức lãi vay = 24 run ngắn | 2-4 giờ máy, `threads=1` |
| 3 | LOO + bootstrap theo episode + DSR + mô hình margin call | 1 phiên |
| 4 | quant-skeptic (bắt buộc nếu khuyến nghị đổi production) → user duyệt | — |

Tổng: **~3 phiên làm việc**, chi phí BQ không đáng kể (<1GB scan), chi phí engine là phần chính.

## §10. Điều sẽ khiến chính tôi bác plan này
- Nếu V7 ≈ V0 (spread không thêm gì ngoài `dd52`) ⇒ NO-GO, và đó là kết quả **có khả năng cao nhất**
  vì corr(spread, dd52) = 0,47 và cả hai đều bắt cùng một họ sự kiện hoảng loạn.
- Nếu edge tan khi lãi vay lên 12,5% (số THẬT) ⇒ NO-GO ngay, vì đó mới là chi phí mình thực trả.
- Nếu kết quả phụ thuộc episode 2020 (LOO) ⇒ NO-GO, y hệt V2.5.
- Nếu phải nới kênh ra ngoài CAPIT mới thấy tác dụng ⇒ **DỪNG và hỏi user**, đó là họ rủi ro khác.
