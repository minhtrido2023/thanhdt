# Nâng cảnh báo ADV 2 tỷ/phiên thành GATE CỨNG cho book LAG — đo A/B đầy đủ

**Job:** `Taylor_20260804_080547` · 2026-08-04 · Taylor
**Câu hỏi (user John, thread 1521735922066919515):** nếu ngưỡng `ADV_THIN_VND=2e9` — hiện chỉ
**hiển thị cảnh báo** — trở thành **gate cứng** loại ứng viên LAG có ADV3T < 2 tỷ tại ngày tín hiệu,
thì CAGR/Sharpe/MaxDD/Calmar của V2.4 R3 đổi thế nào và mất bao nhiêu deal LAG?

> **KẾT LUẬN 1 DÒNG — NO-GO như một "thay đổi để tăng lợi nhuận", nhưng KHÔNG phải vì gate xấu:**
> toàn bộ +3,58pp CAGR đo được là **cùng một hiệu ứng đã biết** (chặn mã ADV≤0 = không fill được),
> **không phải** do ngưỡng 2 tỷ. Đặt trên nền gate ADV>0 đã có, ngưỡng 2 tỷ **KHÔNG thêm CAGR**
> (−0,26pp) và **không thêm Sharpe** (−0,02) — nó chỉ đổi hồ sơ rủi ro (MaxDD −19,1% → −18,2%,
> Calmar 1,71 → 1,78). Và hiệu ứng vốn được cho là "tăng CAGR" thì **đổi dấu khi bỏ 3/13 năm**.

---

## 0. Hai tầng gate hiện tại — đọc từ code thật, không đoán (skill §1)

| Tầng | File | Chặn gì | Có phải gate cứng? |
|---|---|---|---|
| Tín hiệu | `lag_liquidity_filter.py::lag_filter_illiquid()` (LIVE 07-21) | ADV **≤ 0** / thiếu dữ liệu / dòng giá cũ > 30 ngày | **CÓ** — nhưng **nhị phân "đo được hay không"**, KHÔNG có ngưỡng độ lớn (`:179` `float(r.adv_vnd) > 0`) |
| Lệnh | `trading_bot/plan.py::cap_lag_orders` | trần %ADV cho size lệnh (fail-closed) | CÓ, nhưng chặn **KÍCH THƯỚC LỆNH**, không loại mã |
| Hiển thị | `trading_bot/due_diligence.py:45` `ADV_THIN_VND=2e9` | in `⚠ thanh khoản mỏng` | **KHÔNG** — comment `:42` ghi rõ "Ngưỡng CẢNH BÁO hiển thị (không phải gate)" |

⇒ Vùng **1e8 < ADV < 2e9** ("mỏng nhưng chưa chết") hiện **không bị chặn gì**. Đúng như mô tả trong
dispatch. Cả 3 tầng đều dùng cùng công thức ADV = `Volume_3M_P50 × COALESCE(Price, Close)`
(`due_diligence.adv_vnd:161-190`, `lag_liquidity_filter:156`, engine `LAG_ADV_BASIS="price"`).

**Engine backtest** có knob tương ứng nhưng ở tầng khác: `liquidity_require_positive`
(`simulate_holistic_nav.py`, bật qua `LIQ_ZERO_BLOCK=lag`) — hiện **mặc định TẮT** (`""`, opt-in),
là "lỗi fidelity `liq<=0` VẪN MỞ" ghi trong `results_registry.md`.

## 1. Thiết kế phép thử

Điểm chèn gate = vòng sinh tín hiệu LAG `pt_v23_audit_2014.py:1350-1357`, ngay sau kiểm tra giá:
tra `liq_lag[(ticker, signal_date)]` (chính là ADV tại ngày tín hiệu, cùng cơ sở giá `price`), thiếu
khóa ⇒ **loại (fail-closed)**, đúng ngữ nghĩa gate live.

- **Engine = BẢN SAO nghiên cứu** `mike/agents/Taylor/exp_lag_advgate_20260804/pt_v23_advgate.py`,
  khác production **đúng 3 khối đã ghi chú** (khai báo knob / gate / dump danh sách bị loại), **no-op
  hoàn toàn khi `LAG_ADV_MIN_VND=0`**. `git status` trên `pt_v23_audit_2014.py`,
  `lag_liquidity_filter.py`, `trading_bot/due_diligence.py`, `simulate_holistic_nav.py`,
  `trading_bot/plan.py` **SẠCH** (skill §14).
  ⚠️ **Đính chính (quant-skeptic bắt đúng):** `deploy_golive_dt5g_v4/golive_recommend_v23.py` **CÓ**
  diff chưa commit — nhưng là việc **KHÔNG liên quan** của job khác cùng ngày (`ETF_PARK {3: 0.7} →
  {3: 0.8}`, F1 park, sửa lúc 11:33 ICT, trước job này). Lần kiểm đầu của tôi gõ sai đường dẫn
  (`golive_recommend_v23.py` ở gốc repo không tồn tại) nên git im lặng trả rỗng ⇒ đã tuyên bố "sạch"
  quá tay. Không ảnh hưởng phép thử: backtest không import file này, và chân chạy đặt
  `PARK_STATES="3:0.7"` tường minh.
- **Môi trường pin** (skill §3): snapshot `data/bq_cache_asof20260729_postrestate` (đúng vintage của
  pin 28,86%), `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, lệnh pin R3 nguyên văn
  (`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
  AUDIT_END=2026-06-19 … v23a none postbull 0 edge`), `EXP_TAG` cho mọi chân ⇒ **không đụng CSV
  canonical** (§8).
- **Nguồn dữ liệu** (skill §2): `tav2_bq.ticker` (`Volume_3M_P50`, `COALESCE(Price,Close)`) — đúng
  nguồn cả 3 tầng production đang đọc; universe quyết định = `universe_pit` (`ETF_LIQ=custompitg`),
  CAPIT pool vẫn `ticker_prune` như production. Cơ sở giá `price` = mặc định production (đã
  CONFIRMED 08-02, KHÔNG đảo lại — skill §9).
- **Self-check 0 VND**: `[selfcheck BAL]` và `[selfcheck LAG]` `= 0 VND` trên **cả 7 chân**, `EXIT=0`.

**Điều kiện hợp lệ đăng ký trước — ĐẠT:**

| Chân đối chứng | Kỳ vọng | Thực đo | Khớp |
|---|---|---|---|
| `LAG_ADV_MIN_VND=0` (= production) | pin R3 **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** | **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** | ✅ từng chữ số |
| `LIQ_ZERO_BLOCK=lag`, gate off | L1@0,20 cơ sở price **32,71 / 1,95 / −19,1 / 1,71 / 1.699,09B** (job `Taylor_20260803_052705`) | **32,71 / 1,95 / −19,1 / 1,71 / 1.699,09B** | ✅ từng chữ số |

⇒ harness tái lập **cả pin chính thức lẫn chân L1 của job trước** (lần tái lập độc lập thứ 3 của
32,71%) ⇒ mọi Δ dưới đây là chênh lệch thật do đúng biến can thiệp.

## 2. Kết quả — 7 chân

### 2a. Thang liều theo ngưỡng (skill §10), engine giữ mặc định production (`LIQ_ZERO_BLOCK=""`)

| Ngưỡng ADV | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | Δ CAGR vs pin |
|---|---|---|---|---|---|---|---|---|
| **0 = control (pin R3)** | **28,86%** | 1,90 | −17,8% | 1,62 | 1.178,01B | 27,09% | 30,48% | — |
| 0,5 tỷ | 32,38% | 1,92 | −18,3% | 1,77 | 1.647,52B | 27,31% | 37,21% | +3,52pp |
| 1 tỷ | 32,41% | 1,92 | −18,3% | 1,77 | 1.652,88B | 27,58% | 37,02% | +3,55pp |
| **2 tỷ (câu hỏi)** | **32,44%** | **1,93** | **−18,2%** | **1,78** | 1.656,39B | 27,52% | 37,12% | **+3,58pp** |
| 5 tỷ | 32,23% | 1,92 | −18,5% | 1,74 | 1.624,21B | 26,77% | 37,45% | +3,37pp |

**Thang KHÔNG có dose-response.** Bước 0 → 0,5 tỷ ăn **3,52pp/3,58pp = 98%** toàn bộ hiệu ứng; từ
0,5 → 5 tỷ đường **phẳng** (biên độ 0,21pp, và 5 tỷ còn *thấp hơn* 2 tỷ). Chữ ký này nói thẳng:
hiệu ứng đến từ **cái đuôi ADV ≈ 0**, KHÔNG từ ngưỡng 2 tỷ. Con số 2 tỷ không có gì đặc biệt.

### 2b. Phép thử quyết định — phần GIA TĂNG trên nền gate ADV>0 đã biết

| Chân | engine chặn ADV≤0? | gate độ lớn tại ngày tín hiệu | CAGR | Sharpe | MaxDD | Calmar | IS | OOS |
|---|---|---|---|---|---|---|---|---|
| control = pin R3 | KHÔNG (production hôm nay) | không | 28,86% | 1,90 | −17,8% | 1,62 | 27,09% | 30,48% |
| **L1** (`LIQ_ZERO_BLOCK=lag`) | CÓ | không | **32,71%** | 1,95 | −19,1% | 1,71 | 27,22% | 37,96% |
| gate 2 tỷ | KHÔNG | **2 tỷ** | 32,44% | 1,93 | −18,2% | 1,78 | 27,52% | 37,12% |
| **L1 + gate 2 tỷ** | CÓ | **2 tỷ** | **32,45%** | 1,93 | −18,2% | 1,78 | 27,63% | 37,04% |

**Đọc 2 dòng cuối so với dòng L1 — đây là câu trả lời thật:**
- Thêm gate 2 tỷ **lên trên** gate ADV>0: CAGR **32,71% → 32,45% = −0,26pp**, Sharpe **1,95 → 1,93**,
  OOS **37,96% → 37,04% = −0,92pp**. **Không thêm lợi nhuận, không thêm Sharpe.**
- Đổi lại: MaxDD **−19,1% → −18,2%** (+0,9pp) và Calmar **1,71 → 1,78**.
- `gate 2 tỷ` một mình (32,44%) ≈ `L1 + gate 2 tỷ` (32,45%): chênh **0,01pp** — vì tập ADV<2 tỷ là
  **tập cha** của tập ADV≤0, nên bật thêm gate engine gần như không đổi gì. Cơ chế khớp cơ học.

⇒ **+3,58pp không phải "edge của ngưỡng 2 tỷ"** mà là +3,85pp của hiệu ứng
`LIQ_ZERO_BLOCK` (đã đo, đã pin, đã dán nhãn **KHÔNG được trích như edge**) trừ đi 0,26pp mà chính
ngưỡng 2 tỷ làm mất. Con số nào của A/B này cũng **thừa hưởng nguyên vẹn** cảnh báo trong docstring
`lag_liquidity_filter.py`: cả hai chân dùng chung mô hình fill 20%ADV/phiên **chưa neo vào fill thật**
(fill live chỉ xác nhận tới 3,86%ADV/phiên) ⇒ **MỨC chưa hiệu chuẩn**, sổ theo dõi
`kb/projects/lag-adv-filter-tracking.md`, mốc cứng 2026-12-15 / 2027-03-31.

### 2c. Mất bao nhiêu deal LAG

| Đại lượng | control | gate 2 tỷ | Δ |
|---|---|---|---|
| Ứng viên LAG trong cửa sổ (sự kiện tín hiệu) | 5.317 | 2.085 | **−3.232 (−60,8%)** |
| Mã phân biệt bị gate loại | — | — | 653 mã |
| Vị thế LAG được mở | 1.901 | 1.465 | −436 (−22,9%) |
| Trong đó **bỏ dở** (`ABANDONED_REFUND`, không fill nổi) | 853 | 464 | −389 |
| **Deal HOÀN TẤT** | **1.048** | **1.001** | **−47 (−4,5%)** |
| Mã phân biệt thực sự giao dịch | 522 | 300 | −222 |

**Câu trả lời vận hành quan trọng nhất:** gate cắt 60,8% ứng viên và 436 vị thế, nhưng **89,2% số vị
thế bị cắt (389/436) vốn đang bị BỎ DỞ vì không fill nổi**. Deal thật sự hoàn tất chỉ mất **47 deal
(−4,5%)** trên 12,5 năm ≈ **3,8 deal/năm**.

**Phân rã kept-vs-removed ở tầng vị thế (skill §11)**, đo trên chính sổ lệnh chân control:

| Nhóm trong chân control | n vị thế | vốn triển khai luỹ kế | P&L | lợi nhuận/chu kỳ vốn | tỷ lệ bỏ dở |
|---|---|---|---|---|---|
| **bị gate 2 tỷ loại** | 918 | 4.539,1B | +76,32B | **1,682%** | **68,1%** |
| giữ lại | 983 | 11.559,9B | +489,43B | **4,234%** | 23,2% |
| tổng | 1.901 | 16.098,9B | +565,76B | 3,514% | 44,9% |

Nhóm bị loại hút **28% tổng vốn triển khai** để sinh lợi nhuận/chu kỳ **thấp hơn 2,5 lần** nhóm giữ
lại, và **2/3 số lần vào không fill nổi**. Đây là kênh cơ chế đúng — **giống hệt** kênh đã đo ở T3
job `Taylor_20260803_021414` (81% của Δ = không rót vốn vào nhóm bị chặn), củng cố kết luận "cùng
một hiệu ứng, không phải hiệu ứng mới".

Ví dụ mã bị gate loại (theo số lần xuất hiện làm ứng viên): VSI(24), CAP(21), DNC(21), TYA(20),
SFN(19), TV3(19), MAC(18), PRC(18), BED(17), GDT(17), PCT(17), VNF(17), CSC(16), SGC(16), TRA(16).
ADV trung vị của nhóm bị loại = **0,043 tỷ/phiên** (p90 = 1,017 tỷ) ⇒ **90% nhóm bị loại nằm dưới
1 tỷ**, tức gate 2 tỷ chủ yếu bắt đúng nhóm gần-như-không-giao-dịch, chứ không phải vùng "mỏng".
Phân bố theo năm khá đều (137 → 348/năm) ⇒ **không phải hiện vật lạm phát** (ngưỡng danh nghĩa cố
định 2 tỷ áp cho cả 2014 lẫn 2026), dù caveat này vẫn nên ghi nhận.

## 3. Δ CAGR có bền không? — KHÔNG (đây là lý do NO-GO thứ hai, độc lập)

N khai đúng (skill §4): đơn vị độc lập cho một Δ **mức danh mục** là **13 năm dương lịch** /
~50 quý, **không phải** 3.232 sự kiện ứng viên hay 3.106 phiên NAV.

| Năm | control | gate 2 tỷ | Δpp |
|---|---|---|---|
| 2014 | +49,14% | +41,82% | **−7,32** |
| 2015 | +27,48% | +21,35% | **−6,13** |
| 2016 | +14,22% | +13,99% | −0,23 |
| 2017 | +33,73% | +52,17% | **+18,45** |
| 2018 | +27,19% | +26,41% | −0,79 |
| 2019 | +13,81% | +13,67% | −0,14 |
| 2020 | +27,67% | +51,91% | **+24,24** |
| 2021 | +108,08% | +137,76% | **+29,68** |
| 2022 | −7,96% | −5,57% | +2,39 |
| 2023 | +22,56% | +21,99% | −0,58 |
| 2024 | +25,15% | +29,45% | +4,31 |
| 2025 | +48,10% | +41,88% | **−6,22** |
| 2026 (đến 06-19) | −1,22% | −1,06% | +0,16 |

- **Gate chỉ thắng 6/13 năm.** Sign test một phía P(X≥6 | p=0,5) = **0,709** ⇒ **không có ý nghĩa
  trên tần suất**.
- **LOO 1 năm: 13/13 dương** (min +1,92pp khi bỏ 2020, max +4,53pp) — nhưng đó là vì 3 năm khổng lồ
  gánh hết.
- **Bỏ ĐỒNG THỜI 2017+2020+2021: Δ ĐỔI DẤU = −1,24pp** (control 22,35% vs gate 21,10%). Bỏ
  2020+2021: chỉ còn **+0,40pp**.

⇒ Đúng dạng "1–2 năm gánh hết edge = reshuffle-luck" mà chuẩn `kb/KNOWLEDGE.md` §8 cảnh báo. Cộng
với thang liều phẳng ở §2a và phần gia tăng âm ở §2b: **không có căn cứ nào để wire ngưỡng 2 tỷ vì
lợi nhuận.**

## 4. Multiple-testing (skill §13)

`N_trials = 5` cấu hình ngưỡng cùng họ (0 / 0,5 / 1 / 2 / 5 tỷ) + 2 chân L1 kiểm chứng cơ chế = **7
lần chạy engine**.

- **DSR** trên NAV daily cả 5 chân: **1,0000** — nhưng đọc cho đúng, số này **vô nghĩa để phân biệt**
  ở đây: SR/quan sát của cả 5 chân nằm trong 0,11538–0,11665 (chênh <1,1%), nên DSR chỉ đang nói
  "chiến lược nền có Sharpe dương chắc chắn", **không** nói chân nào hơn chân nào.
- **PBO (CSCV, S=16, 12.870 tổ hợp, Ncfg=5, T=3.104) = 0,916**; median logit −1,609.
  **Kiểm khối suy biến trước khi chạy (bài học CAPIT navsize 07-31): 0/16 khối có sd≈0 hoặc NaN** ⇒
  CSCV hợp lệ, không có khối rỗng bị tính vào.
  **PBO 0,916 ≫ 0,5** ⇒ cấu hình tốt nhất IS gần như luôn rơi dưới trung vị OOS ⇒ **không cấu hình
  ngưỡng nào trong họ này được phép chọn theo số IS**. Kết quả này khớp hoàn hảo với thang phẳng §2a:
  khi 4 cấu hình gần như trùng nhau, "chọn cái tốt nhất" là tung đồng xu.

## 5. Đối chiếu với các finding liền kề (skill §12)

1. **`kb/projects/lag-adv-filter-tracking.md`** — dự án đó đo **edge-thật-vs-hiện-vật-fill** của gate
   `ADV≤0` **đã có**. Đây là câu hỏi khác (ngưỡng ĐỘ LỚN 2 tỷ). **Nhưng kết quả §2b cho thấy hai câu
   hỏi hội tụ về cùng một cơ chế**: gate 2 tỷ không mang lại gì mà gate ADV>0 chưa mang lại. ⇒
   **mọi con số CAGR ở đây bị chặn bởi đúng 2 mốc cứng của dự án đó (2026-12-15 / 2027-03-31)**,
   không được trích như edge trước mốc.
2. **Docstring `lag_liquidity_filter.py`** đã ghi "ĐỌC SỐ PIN KHÔNG THEO CHIỀU NÀO" và khoảng
   `[~27,2%; 31,3%]` đã hết hiệu lực. Báo cáo này **không** tạo khoảng thay thế và **không** đề xuất
   re-pin lên 32,4%.
3. **`ADV_THIN_VND=2e9` neo theo rổ CAPIT** (`Price*Volume/1e9 >= 2` trong `golive_recommend_v23.py`)
   — nghĩa là 2 tỷ là **một ngưỡng đã dùng ở nơi khác**, không phải số dò từ backtest này. Đó là lý
   do hợp lệ để giữ nó làm **ngưỡng cảnh báo**, nhưng KHÔNG phải căn cứ để nâng thành gate cứng.

## 6. Khuyến nghị

**NO-GO cho việc nâng 2 tỷ thành gate cứng LAG *với lý do lợi nhuận*.** Ba căn cứ độc lập:
(a) phần gia tăng trên nền gate ADV>0 là **−0,26pp CAGR / −0,02 Sharpe / −0,92pp OOS**;
(b) thang liều **phẳng** từ 0,5 đến 5 tỷ ⇒ ngưỡng 2 tỷ không có nội dung kinh tế riêng;
(c) Δ so với pin **đổi dấu khi bỏ 3/13 năm**, sign test 6/13 (p=0,709), **PBO = 0,916**.

**KHÔNG kết luận rằng gate là ý tồi.** Có một lập luận **khác, không dựa vào CAGR**, vẫn còn nguyên
giá trị và nên được quyết riêng:
- gate 2 tỷ **cải thiện MaxDD 0,9pp và Calmar 0,07** so với L1, và
- cắt **389 vị thế bỏ dở** (vốn kẹt trong lệnh không khớp) để đổi lấy **47 deal hoàn tất** trên 12,5 năm.
Nếu user muốn gate này, hãy chọn nó như một **luật khả-thi-thi-hành/vận hành** (đừng đặt mục tiêu vào
mã live không mua nổi — cùng tinh thần với `lag_filter_illiquid`), **không** như một cải tiến lợi
nhuận. Ngưỡng khi đó nên chọn theo **năng lực fill thật của tài khoản** (T4 đo được fill live tới
3,86%ADV/phiên; ở NAV 50B với w_LAG≈65%, một vị thế `LAG_HI` = 10% sổ LAG ≈ **3,25B**, muốn fill trọn
trong `max_fill_days=5` phiên cần ≈0,65B/phiên = 3,86%×ADV ⇒ **ADV ≳ ~17 tỷ/phiên** — tức 2 tỷ vẫn
**lỏng hơn ~8 lần** so với yêu cầu vận hành thật), **không** theo backtest.

**Chưa đụng production**: không sửa/commit gì; `git status` sạch trên toàn bộ file live liên quan.
Bước kế: quant-skeptic verify báo cáo này trước khi bất kỳ ai trích số.

## 7. Hiện vật

`mike/agents/Taylor/exp_lag_advgate_20260804/`:
`pt_v23_advgate.py` (bản sao engine, diff 3 khối) · `run_leg.sh` · `run_leg2.sh` ·
`dsr_pbo_advgate.py` · log 7 chân (`ctrl0804`, `gate500m`, `gate1000m`, `gate2000m`, `gate5000m`,
`L1_ctrl`, `L1_gate2000m`) · `dropped_*.json` (danh sách đầy đủ ứng viên bị loại từng chân).
CSV audit: `data/v23_golive_audit_2014_now_..._advprice[_liqzblag][_advmin*]_exp_*_univpit.csv`.
CSV canonical `..._wtnamecap.csv` **KHÔNG bị đụng**.
