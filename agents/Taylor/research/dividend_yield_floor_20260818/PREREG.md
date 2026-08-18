# PREREG — Dividend Yield Floor (ngưỡng giá hỗ trợ từ cổ tức tiền mặt)

- **Job**: `Taylor_20260818_021828` · **Ngày lập**: 2026-08-18
- **Trạng thái**: LOCKED — commit file này TRƯỚC khi chạy bất kỳ query outcome nào.
- **Phạm vi**: R&D thuần. KHÔNG wire production, KHÔNG sửa `filter.json`, KHÔNG đề xuất banned ticker.

---

## 0. Câu hỏi

User quan sát: cổ phiếu chia cổ tức TIỀN MẶT ổn định nhiều năm liên tiếp **không giảm mạnh** khi
tỉ suất cổ tức (yield) tiến gần/vượt lãi suất tiết kiệm. Cơ chế đề xuất: yield > lãi suất huy động
⇒ dòng tiền tiết kiệm chuyển sang cổ phiếu ⇒ **sàn giá tự nhiên (yield floor)**.

Đây là câu hỏi về **CƠ CHẾ ở MỨC GIÁ (level)**, KHÔNG phải về drift quanh ngày GDKHQ (Sprint 2
`corp_action_program_20260815` đã trả lời câu đó riêng, verdict RISK/DUE-DILIGENCE, không alpha).
Nếu cơ chế có thật, hàm ý là: **giá vào so với yield floor quan trọng hơn BHAR lịch sử** khi chọn
mã cổ tức ổn định.

**Claim cần kiểm chứng là claim về ĐUÔI TRÁI (downside), không phải về lợi suất trung bình.**
"Không giảm mạnh" ≠ "tăng nhiều". Vì vậy prereg này đặt HAI leg đồng-primary (H1 mean, H2 downside)
và tuyên bố verdict theo cả hai — nhưng leg quyết định bản chất cơ chế là **H2**.

---

## 1. Nguồn dữ liệu (đã tra `mike/kb/data_registry/` trước khi chọn)

| Nguồn | Status registry | Dùng làm gì | Bẫy đã đọc & cách né |
|---|---|---|---|
| `tav2_bq.corporate_action` | **TRAP** (`price-volume/corporate_action_bq.md`) | sự kiện DIV: `value_per_share` (VND/cp GỘP), `exright_date` | Bẫy 3 (trùng dòng) ⇒ dedup theo khoá KINH TẾ `(ticker, exright_date, dividend_year, dividend_stage_vi)` + `event_status='executed'`, y hệt Sprint 1/2. Bẫy 2b (upsert in-place) ⇒ **KHÔNG** dùng `public_date` làm mốc PIT; chỉ dùng làm tiebreak dedup. Bẫy 5 (`listing_date`) ⇒ không đụng tới. |
| `tav2_bq.ticker` | CANONICAL | `Close` (đã hồi tố) cho MỌI lợi suất; `Price` (thô) cho MẪU SỐ yield; `Low/High/Volume/PE/PB/ICB_Code` | `price-volume/ticker_price_stale_on_exdate.md`: `Price` dòng ĐÚNG NGÀY GDKHQ có thể chép nguyên T−1 ⇒ xem §4.2 |
| `tav2_mike.universe_pit` | CANONICAL | (a) benchmark EW point-in-time, (b) màng lọc "đầu tư được" tại t | Membership phải đúng ở CẢ HAI đầu của mỗi lợi suất ngày (chép nguyên SQL `EWUNIV` của Sprint 2) |
| `tav2_bq.vnindex_5state_dt5g_live` | CANONICAL | trạng thái DT5G tại t (robustness §7.2) | **KHÔNG** đọc `tav2_bq.vnindex_5state` (đó là v3.4b BASE, không phải DT5G) |
| `tav2_bq.ticker_financial` | CANONICAL | `OShares`/`Release_Date` — CHỈ dùng cho selfcheck đơn vị (§8), không vào công thức chính | join PIT theo `Release_Date < t` |
| `deposit_rate_vn.py::current_deposit_rate(asof=t)` | (code repo gốc) | ngưỡng lãi suất huy động 12M Big-4 | xem §1.1 |

### 1.1 CAVEAT BẮT BUỘC — `deposit_rate_vn.py` KHÔNG phải PIT thật

26 mốc lịch sử trong `DEPOSIT_EVENTS` được **calibrate CÙNG MỘT LẦN ngày 2026-06-19** (docstring
ghi rõ: "Cyclical SHAPE from Trading Economics ... LEVELS pinned to known Big-4 web anchors"), và
file tự gắn nhãn `⚠️ PROXY`. Đây là **hindsight bias nhẹ**: các lần đổi lãi suất là sự kiện công
khai mà nhà đầu tư biết ngay tại thời điểm, nhưng *mức chính xác* trong series này được chọn khi
đã nhìn thấy toàn bộ lịch sử.

**Hệ quả pre-registered, không thương lượng:**
- Ngưỡng động (deposit-rate) là biến **PRIMARY**, nhưng finding CHỈ được coi là đáng tin khi nó
  **nhất quán qua ≥3 trong 4 ngưỡng CỐ ĐỊNH 5% / 6% / 7% / 8%** (§7.1). Ngưỡng cố định hoàn toàn
  miễn nhiễm với hindsight của series lãi suất.
- Nếu ngưỡng động ra kết quả mạnh mà 4 ngưỡng cố định không ⇒ kết luận là **REFUTED**, không phải
  "cơ chế phụ thuộc lãi suất". Đây là quy tắc chống tự lừa, khoá trước.

---

## 2. Định nghĩa — "Stable dividend payer"

Dùng **cửa sổ 365 ngày lịch trượt**, KHÔNG dùng năm dương lịch (năm dương lịch làm định nghĩa
phụ thuộc vị trí trong năm của ngày t — một mã trả tháng 6 sẽ "mất" một năm nếu đo ngày 1/3).

Tại phiên `t`, với `W_k(t) = (t − 365(k+1), t − 365k]` (k = 0,1,2,3,4):

- `n_div_k(t)` = số sự kiện DIV (đã dedup, `executed`, `value_per_share > 0`) có `exright_date ∈ W_k(t)`
- `div_k(t)`  = tổng `value_per_share` của các sự kiện đó (VND/cp)

| Nhãn | Điều kiện |
|---|---|
| **STABLE-3** (primary) | `n_div_0 ≥ 1 ∧ n_div_1 ≥ 1 ∧ n_div_2 ≥ 1` |
| **STABLE-5** (robustness) | `n_div_k ≥ 1` với mọi k ∈ {0,1,2,3,4} |
| **NON-PAYER** (nhóm chứng, §6) | `n_div_0 = n_div_1 = n_div_2 = 0` |
| (vùng xám) | còn lại — **loại khỏi cả hai nhóm**, không gán bừa |

- Chỉ tính sự kiện `exright_date ≥ 2010-01-01` (thị trường VN quá mỏng trước 2010).
- **CHỈ `event_code='DIV'`.** `ISS` (thưởng/tách/quyền mua/ESOP) KHÔNG phải cổ tức tiền mặt và
  KHÔNG được cộng vào tử số — kể cả `issue_method_code='DIV'` ("Trả cổ tức bằng Cổ phiếu"), vì cổ
  tức bằng cổ phiếu **không tạo dòng tiền** nên không cạnh tranh được với lãi tiết kiệm. Đây là
  điểm mấu chốt của cơ chế đang test.

---

## 3. Định nghĩa — trailing yield và yield floor price

```
trailing_div(t) = div_0(t)                      # VND/cp, 365 ngày gần nhất, ex_date ≤ t
yield(t)        = 100 × trailing_div(t) / P_raw(t)          # %/năm
floor_price(t)  = trailing_div(t) / (thr(t)/100)            # VND/cp — giá mà tại đó yield = thr
prox(t)         = P_raw(t) / floor_price(t) = thr(t) / yield(t)   # <1 = giá ĐÃ dưới sàn
```

- `P_raw(t)` = giá THÔ chưa hồi tố (`ticker.Price`), vì `value_per_share` là VND/cp danh nghĩa tại
  thời điểm chi trả. Dùng `Close` (đã hồi tố) làm mẫu số sẽ cho yield **phóng đại tuỳ tiện** theo
  số sự kiện xảy ra SAU t — đó là look-ahead trá hình.
- **KHÔNG dùng `OShares`**: `value_per_share` đã là đơn vị VND/cổ phiếu (registry §DIV xác nhận
  "100% non-null, VND/cp GỘP"). `OShares` chỉ xuất hiện ở selfcheck §8 mục 4 để kiểm chứng đơn vị.
- Sự kiện được tính vào tử số **kể từ chính ngày `exright_date`** (từ phiên đó giá đã điều chỉnh
  giảm và quyền nhận đã chốt) — biên PIT sạch, không nhìn trước.
- `thr(t)`: primary = `current_deposit_rate(asof=t)`; robustness = {5, 6, 7, 8}.

---

## 4. Màng lọc mẫu (population filters) — tất cả PIT

### 4.1 Điều kiện chung cho MỌI ngày-cổ-phiếu vào mẫu
1. `t ∈ [2014-01-01, 2026-06-15]` — biên dưới do `vnindex_5state_dt5g_live` bắt đầu 2014-01-02
   (không muốn hai định nghĩa mẫu khác nhau giữa primary và robustness regime).
2. `in_universe = TRUE` tại `t` trong `tav2_mike.universe_pit` (PIT, không backfill-suy-diễn).
3. `P_raw(t) > 0`, `Close(t) > 0`, có ≥ 1.095 ngày lịch (3 năm) dữ liệu giá trước t.
4. `trailing_div(t) > 0`.
5. Không phải mã trong `BAD_TICKERS = {DNN, BCB, PTX}` (kế thừa Sprint 1 issue C3 — dữ liệu giá hỏng).

### 4.2 Xử lý bẫy `ticker.Price` đứng yên ngày GDKHQ (registry TRAP)
Loại dòng `t` khỏi tư cách **ngày kích hoạt episode** nếu bất kỳ điều nào sau đúng:
- `t` là `exright_date` của BẤT KỲ sự kiện `corporate_action` nào (DIV hoặc ISS) của chính mã đó;
- `P_raw(t)` nằm NGOÀI `[Low(t), High(t)]` — bằng chứng tự chứa là giá không thể có thật
  (chính lập luận điểm 2 của registry trên ca VHM 2026-08-06).

Cả hai đều **quan sát được tại t**, không nhìn trước. Ước tính ảnh hưởng: ~2% sự kiện (registry) —
không đáng kể với một nghiên cứu lấy mẫu theo NGÀY. **KHÔNG** sửa/vá giá bằng dữ liệu phiên sau
(đó là look-ahead); chỉ loại.

### 4.3 Chống chồng lấn cửa sổ
Một mã chỉ được đóng góp **1 episode trong mỗi 120 phiên** (giữ episode SỚM NHẤT trong cụm). Không
làm bước này thì mỗi "cụm" giá đi ngang quanh ngưỡng sinh ra hàng chục quan sát gần như trùng nhau
và mọi CI đều hẹp giả.

---

## 5. Test A — Episode "yield vừa vượt ngưỡng" (crossing từ dưới lên)

**Episode A tại (mã, t)** khi đồng thời:
1. mã là STABLE-3 tại `t`;
2. `yield(t−1) < thr(t−1)` và `yield(t) ≥ thr(t)` — vừa vượt, KHÔNG phải đã cao sẵn;
3. thoả §4.

**Outcome**: `BHAR_h = R_stock(t → t+h) − R_bench(t → t+h)`, `h ∈ {20, 60, 120}` phiên,
`R_stock` tính trên `Close` (hồi tố — đây là chỗ ĐÚNG để dùng `Close`), `R_bench` = lợi suất tích
luỹ **EW `universe_pit`** (SQL `EWUNIV` Sprint 2, membership yêu cầu ở cả hai đầu, winsor |ret|≤50%
để chặn dòng giá hỏng). **Horizon primary = 60 phiên.**

### 5.1 Phân rã nguyên nhân vượt ngưỡng (BẮT BUỘC báo cáo, khoá trước)
Yield vượt ngưỡng vì 3 lý do khác hẳn nhau về kinh tế. Không tách ra thì "floor" và "dao rơi" bị
gộp làm một:

| Nhãn | Điều kiện (so t vs t−21 phiên) | Diễn giải |
|---|---|---|
| `PRICE_DRIVEN` | `trailing_div` không đổi ∧ `P_raw` giảm | giá rơi tới ngưỡng — ca thú vị nhất, cũng là ca "dao rơi" |
| `DIV_DRIVEN` | `trailing_div` tăng | doanh nghiệp trả nhiều hơn |
| `THRESHOLD_DRIVEN` | `thr` giảm ∧ `trailing_div` không đổi ∧ `P_raw` không giảm | **thuần cơ học của series lãi suất** |

`THRESHOLD_DRIVEN` **bị loại khỏi mẫu primary của biến thể ngưỡng động** (nó chỉ phản ánh
`deposit_rate_vn.py` đổi bậc, không phải hành vi thị trường), và được báo cáo riêng. Với 4 ngưỡng
CỐ ĐỊNH, nhóm này rỗng theo định nghĩa — thêm một lý do ngưỡng cố định là trọng tài.

---

## 6. Test B — Chống đỡ giá gần sàn (đồng-primary, leg ĐUÔI TRÁI)

**Episode B tại (mã, t)**: `prox(t) ∈ [0,97 ; 1,03]` (giá đang ở sát sàn cổ tức), thoả §4, và
`prox(t−1) > 1,03` (tiếp cận **từ TRÊN** xuống — đúng câu hỏi "chạm sàn thì có đỡ không").

**Outcome chính**: `MDD_60 = min_{1≤k≤60} [ Close(t+k)/Close(t) − 1 ]` (mức lỗ sâu nhất trong 60
phiên kế tiếp, ≤ 0). Phụ: `P(MDD_60 < −10%)`, `P(MDD_60 < −20%)`, và `BHAR_60`.

**Nhóm chứng ghép cặp (matched control)** — bắt cặp CÙNG NGÀY để mọi biến vĩ mô tự triệt tiêu:
- ứng viên: NON-PAYER (§2), cùng `t`, thoả §4;
- cùng `ICB_Code` (nhóm ngành thô CT/NH/BH/CK của `ticker`);
- gần nhất theo **`rvol_60`** (độ lệch chuẩn lợi suất ngày 60 phiên trước t), giữ ứng viên có
  `rvol_60` trong dải `[0,8 ; 1,25] ×` của mã sự kiện; lấy tối đa **3** ứng viên gần nhất, lấy
  trung bình outcome của chúng;
- không tìm được ứng viên nào ⇒ **loại episode khỏi test ghép cặp** (không so với "toàn thị trường"
  thay thế — đó là đổi câu hỏi).
- Thống kê: `ΔMDD = MDD_60(sự kiện) − MDD_60(chứng)` theo từng cặp. Ghép theo độ biến động là lựa
  chọn có chủ đích: drawdown bị chi phối bởi vol trước cả bởi định giá, nên không ghép vol thì test
  chỉ đo lại "mã cổ tức ổn định thì ít biến động hơn" — một sự thật hiển nhiên, không phải yield floor.

---

## 7. Test C + Robustness (pre-registered, không thêm sau)

### 7.1 Bảng ngưỡng (bắt buộc, là TRỌNG TÀI của mọi kết luận)
Chạy lại Test A và Test B đầy đủ với `thr ∈ {deposit_rate(t), 5%, 6%, 7%, 8%}`. Báo cáo N, mean,
CI, t (two-way cluster), IS/OOS cho từng ngưỡng trong MỘT bảng.

### 7.2 Regime DT5G
Chạy lại loại bỏ episode có `state ∈ {1 (CRISIS), 5 (EX-BULL)}` tại `t`. Yield cao trong CRISIS
thường là "dao rơi" chứ không phải sàn — nếu hiệu ứng chỉ tồn tại khi CÓ CRISIS thì đó là confound,
không phải cơ chế. Kèm bảng breakdown theo 5 state.

### 7.3 Ổn định theo năm
Leave-one-year-out trên horizon primary (60 phiên): mean khi bỏ từng năm + `share_of_total_effect`.
Một năm gánh > 60% tổng hiệu ứng ⇒ hạ verdict xuống WEAK bất kể t-stat.

### 7.4 Ngành
Tách **ngân hàng (`ICB_Code = 'NH'`) vs phi ngân hàng**. Cơ học cổ tức ngân hàng khác hẳn (bị SBV
ràng buộc vốn, nhiều năm trả bằng cổ phiếu) nên gộp chung là so hai thứ khác nhau.

### 7.5 STABLE-5
Lặp toàn bộ primary với định nghĩa STABLE-5.

---

## 8. Thống kê & suy diễn (khoá trước)

- **t-stat quyết định verdict** = OLS chỉ có hằng số với **hiệp phương sai two-way cluster
  (Cameron–Gelbach–Miller: V₁ + V₂ − V₁₂)** theo `ticker` × `năm-tháng của t`. Tái dùng
  `ols_twoway()` của Sprint 2, không viết lại.
- **CI báo cáo** = block bootstrap 10.000 lần, block = **tháng dương lịch** (mùa ĐHCĐ khiến cổ tức
  VN dồn cụm theo mùa; resample từng episode sẽ cho CI hẹp vì GIẢ ĐỊNH, không vì BẰNG CHỨNG).
  Seed cố định `20260818`.
- **N khai báo = số EPISODE độc lập** (sau khử chồng lấn §4.3), KHÔNG phải số dòng ngày-cổ-phiếu.
  Mọi bảng phải in kèm số cụm (số mã, số tháng) bên cạnh N.
- **IS = t ≤ 2019-12-31; OOS = t ≥ 2020-01-01.** Tách trước khi nhìn, không đổi ranh giới.
- Placebo (bài học Sprint 2): chạy đúng pipeline trên **ngày giả** = `t − 250 phiên` cho cùng tập
  mã/ngày; null của pipeline này **không mặc định bằng 0** — mọi số primary phải báo cả dạng thô
  và dạng đã trừ placebo ghép cặp.

### 8.1 N kỳ vọng (ước lượng trước, chỉ từ đếm population — CHƯA chạm outcome)
Đếm thật trên `corporate_action`: 767–908 mã trả cổ tức tiền mặt mỗi năm 2017–2025 (2010: 416).
Sau khi giao với `universe_pit` (mã đầu tư được) + STABLE-3 + khử chồng lấn 120 phiên, ước:
- Test A: **1.500 – 5.000 episode** trên toàn 2014–2026 cho ngưỡng động; mỗi ngưỡng cố định cùng bậc.
- Test B: **1.000 – 4.000 episode**, giảm ~30–50% sau ghép cặp thành công.
- Nếu N thực tế < 300 ở horizon primary của ngưỡng primary ⇒ **tuyên bố UNDERPOWERED**, không cố
  ép ra verdict CONFIRMED/REFUTED.

---

## 9. TIÊU CHÍ GO/NO-GO (pre-registered — KHÔNG sửa sau khi nhìn số)

Ký hiệu: `t_c` = t-stat two-way cluster.

### CONFIRMED (cơ chế yield floor được ủng hộ)
Phải đúng **CẢ 4**:
1. **Leg đuôi trái (H2)**: `ΔMDD` (sự kiện − chứng, Test B, 60 phiên) **dương** (nghĩa là sụt ít
   hơn nhóm chứng) ≥ **1,5 pp**, với `|t_c| ≥ 2,0`;
2. đúng dấu và `|t_c| ≥ 2,0` ở **CẢ IS lẫn OOS** (leg H2);
3. **nhất quán dấu ở ≥ 3 trong 4 ngưỡng cố định** {5,6,7,8}%;
4. sống sót §7.2 (bỏ CRISIS + EX-BULL) — dấu không đổi, độ lớn không mất quá nửa.

### WEAK
Đúng (1) nhưng hỏng đúng một trong (2)/(3)/(4); hoặc leg H1 (`BHAR_60 > 0`, `|t_c| ≥ 2,0`,
IS+OOS) đạt trong khi leg H2 không đạt. Diễn giải WEAK = "có dấu hiệu, chưa đủ để đổi cách làm".

### REFUTED
`ΔMDD` không khác 0 có ý nghĩa ở ngưỡng primary **và** ở ≥ 3 ngưỡng cố định; hoặc dấu NGƯỢC
(stable payer sụt SÂU HƠN nhóm chứng khi chạm sàn).

### UNDERPOWERED
N < 300 (§8.1) hoặc số mã độc lập < 60 ở nhánh primary.

**Ràng buộc tự-hãm (mệnh lệnh dispatch, ghi lại để không quên):** KHÔNG được tự khẳng định
"yield mechanism is real" nếu `|t_c| < 2,0` hoặc IS/OOS không nhất quán — bất kể đồ thị trông
thuyết phục thế nào.

---

## 10. Selfcheck bắt buộc trước khi báo kết quả

1. Tái tạo **3 số bất kỳ** trong bộ kết quả bằng đường tính ĐỘC LẬP (đọc lại CSV thô, tính tay
   bằng pandas, không gọi lại hàm đã dùng).
2. Chạy toàn bộ selfcheck dưới `env -u TZ` **và** `TZ=UTC` — kết quả phải trùng từng byte (§16
   coding_guidelines).
3. **Cross-check công thức**: thay `trailing_div/P_raw` tự tính bằng cột `ticker.DY` của BQ trên
   cùng tập ngày-mã; báo cáo phân phối delta (median, p10/p90, tương quan Spearman). Đây là kiểm
   tra tính đúng đắn của công thức trailing yield, KHÔNG phải để thay thế nó — `DY` là hộp đen của
   vendor, có thể là forward/announced yield.
4. **Kiểm đơn vị `value_per_share`**: với 20 sự kiện lớn nhất, xác nhận
   `value_per_share / P_raw(ex−1)` nằm trong dải hợp lý (< 30%) và `value_per_share × OShares` cùng
   bậc độ lớn với lợi nhuận năm — bắt lỗi "đơn vị là đồng hay nghìn đồng".
5. Xác nhận **0 dòng** nào trong mẫu có `t` = `exright_date` (§4.2) và **0 dòng** có
   `P_raw ∉ [Low, High]`.
6. Xác nhận benchmark EW: tổng số mã/ngày > 50 ở mọi ngày dùng trong mẫu; không có ngày nào
   `n_impossible > 0` lọt vào chuỗi đã winsor.
7. Xác nhận biên PIT: với 200 episode ngẫu nhiên, mọi `exright_date` cấu thành `trailing_div(t)`
   đều `≤ t` và `> t − 365`.

---

## 11. Deliverables

`PREREG.md` (file này, commit TRƯỚC outcome) · `build.py` · `analyze.py` · `selfcheck.py` ·
`FINDINGS.md` · `DEVIATIONS.md` · bus finding topic `dividend-yield-floor-20260818` với verdict
CONFIRMED / WEAK / REFUTED / UNDERPOWERED.

## 12. Sai lệch đã biết so với prompt dispatch (ghi ngay, không giấu)

| Prompt dispatch nói | Thực tế | Xử lý |
|---|---|---|
| `corporate_action` có `cash_amount`, `ex_date` | Cột thật là **`value_per_share`** và **`exright_date`** (registry + kiểm bảng) | Dùng tên cột thật |
| "lọc `event_type='DIV'`" | Cột thật là **`event_code`**; `category` LUÔN NULL | Dùng `event_code`; thêm `event_status='executed'` |
| Bắt đầu từ 2010 | Lịch sử cổ tức dùng từ 2010, nhưng **cửa sổ đo outcome từ 2014** vì DT5G chỉ có từ 2014-01-02 | Ghi rõ ở §4.1 |

*Mọi sai lệch phát sinh SAU khi commit file này sẽ vào `DEVIATIONS.md`, đánh dấu `# DEVIATION Dn`
ngay tại dòng code gây ra nó.*
