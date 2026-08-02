# `PE` có look-ahead giá điều chỉnh không? — **KHÔNG**. Bác bỏ + A/B đo giá của phép "sửa"

**Job**: `Taylor_20260802_054825` · **Ngày**: 2026-08-02 · **Tiếp nối**: `Taylor_20260802_042110`
(`value_regime_crosssectional_20260802.md` §5) · **Loại**: verify dữ liệu + A/B đo lường.
**KHÔNG wire production. KHÔNG đổi công thức nào đang chạy.**

---

## 0. Trả lời ngắn

| | |
|---|---|
| **Tiền đề của dispatch** (`PE`/`PCF` lịch sử bị méo bởi giá điều chỉnh tương lai; phải nhân `Price/Close`) | **SAI — BÁC BỎ** |
| Thực tế | `PE`/`PB`/`PCF` trong `tav2_bq.ticker` tính trên **`Price` thô của chính ngày đó** ⇒ **point-in-time ĐÚNG**, `1/PE` đọc thẳng là earnings-yield hợp lệ |
| Nhân `Price/Close` thì sao? | **ĐƯA look-ahead VÀO** (hệ số phụ thuộc cổ tức/thưởng xảy ra SAU ngày t) |
| Giá phải trả nếu áp vào custom30V | **R3: CAGR 27,60% → 25,90% (−1,70pp)**, Calmar 1,58→1,39, NAV −160B, **11/13 năm xấu hơn** |
| `custom_basket.py::_yield_piv` | **ĐÃ ĐÚNG SẴN — không sửa gì** |
| `rating_8l.py:521-524` (`_pe_adj_factor`) | **LỖI THẬT, đang MỞ** — nó đang nhân `Price/Close`. Live ≈0, nhưng nhiễm nếu rebuild lịch sử. **ĐỀ XUẤT gỡ, chưa phải quyết định** (chạm production ⇒ user duyệt + quant-skeptic) |
| Số pin `results_registry.md` / `KNOWLEDGE.md` | **IC 1/PE +0,125 GIỮ NGUYÊN**; **R3 27,60% GIỮ NGUYÊN** |

> **Ghi chú về thứ tự Bước 1→3 của dispatch:** Mike giao 3 việc với giả định tiền đề đúng (viết cảnh
> báo "phải nhân `Price/Close`", rồi hạ số pin xuống +0,096/+0,034). Vì tiền đề bị bác bỏ, cả 3 bước
> **vẫn được làm đủ nhưng với nội dung ngược lại** — mục tiêu thật của Bước 1 ("chặn lan tiếp") chỉ
> đạt được khi cảnh báo nói đúng chiều. Không bước nào bị bỏ.

---

## 1. Vì sao phải kiểm tra tiền đề trước

Job trước đo được `F = Price/Close` giảm đơn điệu theo thời gian (trung vị 2,31 ở 2014 → 1,00 ở
2026) và kết luận đó là "hệ số điều chỉnh tích luỹ tới hôm nay đã ngấm vào `PE`". Quan sát về `F`
**đúng** — `Close` đúng là chuỗi đã điều chỉnh về hiện tại. Bước suy diễn "`PE` được tính từ
`Close`" mới là chỗ hỏng, và nó **chưa từng được kiểm chứng trực tiếp**.

Điểm đáng ngờ ngay từ đầu: `mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` đã ghi
"**PE = Price / EPS_ttm**" (verify tay, job `Winston_20260717_063633`) — mâu thuẫn thẳng với §5.
Nhưng lần verify đó làm trên dữ liệu **gần đây**, nơi `F≈1` nên **không phân biệt được** hai giả
thuyết. Phải kiểm trên dữ liệu **cũ**.

## 2. Phép thử quyết định

**Ý tưởng:** trong một kỳ báo cáo, `EPS_ttm` là hằng số. Nên:
- nếu `PE = Price/EPS_ttm` ⇒ `PE/Price = 1/EPS_ttm` **hằng số trong kỳ**;
- nếu `PE = Close_adj/EPS_ttm` ⇒ `PE/Close` mới là cái hằng số, còn `PE/Price` nhảy mỗi lần có sự
  kiện điều chỉnh.

Hai giả thuyết cho dự đoán **loại trừ nhau**, không cần biết `EPS_ttm` bằng bao nhiêu.

### 2.1 Quy mô universe (2014-01-01 → 2021-12-31, nhóm theo `ticker × ID_Release`, ≥20 phiên/kỳ)

| cột | N dòng | N cặp ticker×kỳ | `X/Price` hằng số | `X/Close` hằng số |
|---|---|---|---|---|
| `PE` | 1.419.351 | 23.067 | **93,05%** (TB 1,22 giá trị/kỳ) | 10,96% (TB 17,84) |
| `PB` | 1.104.345 | 17.944 | **94,6%** | 12,57% |
| `PCF` | 1.104.345 | 17.944 | **86,9%** | 20,34% |

Phần ~5–13% kỳ mà `PE/Price` **không** hằng số = `OShares` đổi giữa kỳ (phát hành/ESOP), không
liên quan giá. Phần ~11–20% kỳ mà `PE/Close` hằng số = đúng những mã **không có** sự kiện điều
chỉnh nào trong kỳ (khi đó `F` không đổi nên cả hai đều hằng).

### 2.2 Đối chiếu tay (giá trị tuyệt đối, không chỉ tính hằng số)

| | `Price` | `Close` | `PE` | EPS hàm ý từ `Price` | EPS hàm ý từ `Close` | `Σ(NP_P0..P3)/OShares` thật |
|---|---|---|---|---|---|---|
| VNM 2015-06-30 | 113.000 | 32.510 | 18,116 | **6.237,5** | 1.794,7 | **6.237,5** (2015Q1) |
| FPT 2015-06-30 | 46.400 | 8.120 | 10,900 | **4.256,9** | 744,9 | **4.256,8** (NP_ttm Q1 / OShares Q2) |

Khớp tới 4–5 chữ số **chỉ với `Price` thô**. (VNM 2015 giao dịch thật quanh 110–140k, FPT quanh
46k — đúng mức giá thô đương thời.)

### 2.3 Đọc code, không chỉ đọc dữ liệu

- `rating_8l.py:521-524` — comment `"PE_stored = Close_adj/EPS; correct to unadjusted price basis"`
  rồi `out["PE"] = PE * (Price/Close)`. **Comment sai ⇒ phép nhân sai.** Đây chính là dòng mà job
  trước trích dẫn làm bằng chứng ủng hộ ("script duy nhất có phép sửa này") — nhưng một dòng code
  **cũng chỉ là một khẳng định**, không phải bằng chứng; nó chưa từng được kiểm bằng dữ liệu.
- `custom_basket.py::_yield_piv` — `AVG(SAFE_DIVIDE(1, t.PE))`, không nhân gì. **Đúng.**

⇒ **Cặp bị hoán vai hoàn toàn so với kết luận của job trước.**

---

## 3. A/B NAV custom30V — định lượng cái giá của phép sửa sai

### 3.1 Thiết kế

- **Cùng vintage cả 2 chân**: `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate` (snapshot
  đóng cứng 2,0GB của lần re-pin 07-29), `BQ_CACHE_THREADS=1`.
  Lớp cache là **DuckDB thực thi SQL trên parquet cục bộ**, *không* phải cache kết quả theo chuỗi
  SQL ⇒ query đổi vẫn đọc đúng vintage đóng cứng, không rơi ra BQ live. (Kiểm bằng
  `bq_local_cache.py` — `_register_tables()` + macro `SAFE_DIVIDE`.)
- **Knob INERT** `BASKET_PEADJ` thêm vào `custom_basket.py` (mẫu y hệt `BASKET_DCF_MODE`/
  `BASKET_QFLOOR` sẵn có trong chính hàm đó): mặc định OFF ⇒ SQL sinh ra **byte-identical** với
  trước (đã verify bằng so sánh chuỗi f-string cho cả `PE` lẫn `PCF`). Áp cho **cả hai** chân
  `PE` và `PCF` vì cả hai cùng cơ sở giá.
- Lệnh = **lệnh pin R3 nguyên văn**, chỉ thêm `EXP_TAG` (§8 coding_guidelines — không đè CSV
  canonical).

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
[BASKET_PEADJ=1] BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
AUDIT_END=2026-06-19 EXP_TAG=peadj_ctrl|peadj_on $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
```

### 3.2 Kết quả

| leg | yield | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 2014-19 | OOS 2020+ | self-check |
|---|---|---|---|---|---|---|---|---|---|
| **A — ctrl (= production)** | `1/PE`, `1/PCF` | **27,60%** | **1,84** | **−17,5%** | **1,58** | **1.041,95B** | 23,45% | 31,51% | **0 VND** BAL+LAG |
| B — `BASKET_PEADJ=1` | `1/(PE×Price/Close)` | 25,90% | 1,78 | −18,6% | 1,39 | 881,89B | 20,88% | 30,69% | **0 VND** BAL+LAG |
| **Δ (B−A)** | | **−1,70pp** | −0,06 | **+1,1pp xấu** | **−0,19** | **−160,06B** | −2,57pp | −0,82pp | |

**Chân A tái lập CHÍNH XÁC số pin 07-29**: 27,60 / 1,84 / −17,5 / 1,58, NAV 1.041,95B, 18.496 dòng
CSV; recompute độc lập `extract_peryear.py` → **FULL 27,60% / IS 23,45% / OOS 31,51%**, khớp từng
chữ số với `data/results_registry.md` mục "RE-PIN R3 SAU RESTATE DT5G". ⇒ **harness sạch**, Δ đo
được là thật chứ không phải trôi môi trường.

### 3.3 Per-year (Δ = B − A, pp)

| năm | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Δ | −1,16 | **+2,26** | −3,87 | −5,54 | −2,15 | −5,20 | −2,64 | **+8,49** | −1,17 | −1,51 | −2,84 | −0,26 | −1,33 |

**11/13 năm xấu hơn.** Leave-one-out: bỏ 2021 (năm duy nhất có Δ lớn dương) thì khoảng cách toàn kỳ
còn **rộng hơn**, nên kết luận không do một năm may rủi gánh. Xấu đi đồng thời trên **cả 4 trục**
(CAGR, Sharpe, MaxDD, Calmar) và **cả IS lẫn OOS** — nhiễu không có dạng này.

### 3.4 Đọc kết quả cho đúng — 3 cảnh báo

1. **A/B này KHÔNG chứng minh chiều đúng.** Một look-ahead có thể làm **đẹp** *hoặc* làm **xấu**
   backtest tuỳ tương quan của nó với return. Bằng chứng quyết định là §2 (cơ sở dữ liệu); §3 chỉ
   định lượng **cái giá**. Nếu chỉ có §3, ta không được kết luận gì về tính đúng sai.
2. **Cơ chế xấu đi** (nhất quán, không phải ngẫu nhiên): `F` lớn ⇔ mã sẽ chia cổ tức/thưởng **nhiều
   về sau** — thường là nhóm doanh nghiệp khoẻ. Nhân `F` vào mẫu số làm yield của đúng nhóm đó nhỏ
   đi ⇒ bị **đẩy tụt hạng** khỏi rổ. Selector mất đúng nhóm nó nên giữ.
3. **Δ headline (−1,70pp) nhỏ hơn Δ per-year** (tới −5,5pp) — đúng hiệu ứng single-path đã ghi ở
   mục re-pin 07-29: đường NAV bị bẩn từ điểm chạm trở đi rồi gộp lãi.

### 3.5 R3 có phụ thuộc custom30V không — **CÓ** (đọc code, không giả định)

`ETF_LIQ=custompitg` → `pt_v23_audit_2014.py:199-205` bật `_IS_CUSTOM` → gọi
`custom_basket.build_pit(...)`, `BASKET_SELECT=yieldcombo` → `_yield_piv("PE")` + `_yield_piv("PCF")`.
Đây đúng là rổ parking NEUTRAL custom30V mà KB mô tả "+7,4pp Full". ⇒ A/B trên `_yield_piv` **đo
thẳng vào R3**, không phải nhánh phụ.

---

## 4. Việc còn MỞ — đề xuất, **chưa** phải quyết định

### 4.1 `rating_8l.py:521-524` — lỗi thật, chạm production

```python
# PE_stored = Close_adj/EPS; correct to unadjusted price basis: PE_true = PE * (Price/Close).   # <- comment SAI
_pe_adj_factor = np.where(out["Close"] > 0, out["Price"] / out["Close"], 1.0)
out["PE"] = np.where(out["PE"] > 0, (out["PE"] * _pe_adj_factor).round(2), out["PE"])
```

- **Tác động LIVE ≈ 0**: builder đọc `ticker_1m` ở `MAX(time)` (dòng 91) ⇒ hàng hôm nay có
  `Price≈Close` ⇒ hệ số ≈1.
- **Lịch sử `fa_ratings_8l` chưa nhiễm**: bảng là snapshot **ghi nối tiếp từng ngày**, mỗi dòng
  viết vào lúc hệ số ≈1; dòng code lại mới thêm ~2026-06.
- **Rủi ro thật = bất kỳ lần rebuild lịch sử nào** từ `tav2_bq.ticker` (đúng loại việc đã làm nhiều
  lần: rebuild builder 07-12, audit 8L 07-13…).
- **Đề xuất**: gỡ 3 dòng + sửa comment. Vì `rating_8l.py` là production (composite v3 LIVE) ⇒
  **cần user duyệt + quant-skeptic**, và nên kèm A/B `fa_ratings_8l` rebuild-lịch-sử trước/sau.
  **Tôi KHÔNG tự sửa** (kỷ luật dispatch + §quant-research).

### 4.2 `rating_8l.py` lens `ps` — cùng họ, chiều ngược lại, chưa đo

`out["ps"] = Close * OShares / Revenue_ttm` — `Close` **đã điều chỉnh** nhân với `OShares` **kỳ hiện
hành** ⇒ market-cap hàm ý sai trên dữ liệu lịch sử. Live không ảnh hưởng. **Chưa đo tác động** — ghi
lại ở data_registry "Bẫy (5)" để lần sau không phải phát hiện lại.

### 4.3 Ghi chú phụ đã sửa vào registry

`tav2_bq.ticker` **KHÔNG có cột `PS`** (dù `CLAUDE.md` liệt kê) — chỉ `ticker_financial` có.

---

## 5. Kỷ luật & tái lập

- **N_trials = 1** (một A/B khai báo trước, không sweep tham số). Không tính DSR/PBO vì **không có
  đề xuất wire** — khuyến nghị là **GIỮ NGUYÊN** production.
- **Self-check**: `[selfcheck BAL] 0 VND` + `[selfcheck LAG] 0 VND` ở **cả hai** chân; chân ctrl
  recompute độc lập từ CSV khớp bản in; knob OFF verify byte-identical SQL.
- **Production `git status`**: chỉ `custom_basket.py` đổi, và chỉ bằng knob INERT default-OFF.
  `rating_8l.py`, `pt_v23_audit_2014.py`, `macro_state_live.py`, `trading_bot/` **không đụng**.
  CSV canonical `..._wtnamecap.csv` **không bị đè** (dùng `EXP_TAG`).
- **Hạn chế**: (i) phép thử §2 chạy trên 2014–2021; giai đoạn trước 2014 chưa kiểm (không cần cho
  mọi backtest hiện dùng, sàn 2014). (ii) A/B áp `F` cho **cả** `PE` và `PCF`; chưa tách riêng đóng
  góp từng chân — không cần, vì khuyến nghị là không đổi gì. (iii) `−1,70pp` là con số của **một**
  vintage/one path; nó đo *hướng và bậc độ lớn* của thiệt hại, không phải hằng số phổ quát.

**Tái lập:**
```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
# (a) bang chung co so gia
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
  'SELECT ... COUNT(DISTINCT ROUND(PE/Price,8)) ... GROUP BY ticker, ID_Release'   # xem §2.1
# (b) A/B  (2 leg, ~8 phut/leg)
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 \
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
AUDIT_END=2026-06-19 EXP_TAG=peadj_ctrl $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
BASKET_PEADJ=1 ... EXP_TAG=peadj_on   $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
$DNA_PYEXE extract_peryear.py data/v23_..._exp_peadj_{ctrl,on}_univpit.csv
```
**Log**: `data/peadj_ab/legA_ctrl.log`, `data/peadj_ab/legB_peadj.log`.

---

## 6. Bài học quy trình (đáng ghi hơn cả kết quả)

1. **Một dòng code kèm comment tự tin KHÔNG phải bằng chứng.** Job trước dùng
   `rating_8l.py:_pe_adj_factor` làm chỗ dựa ("script duy nhất có phép sửa này") và thừa hưởng luôn
   cái sai của nó. Cùng loại lỗi §14 coding_guidelines đã ghi: *code không thực thi cái mà comment
   tuyên bố*.
2. **Khi kết luận mới mâu thuẫn với data_registry, mâu thuẫn đó là tín hiệu phải điều tra, không
   phải chi tiết bỏ qua.** Registry đã ghi rõ "PE = Price/EPS_ttm" từ 07-17; nếu đối chiếu ngay thì
   §5 đã không ra đời. (Đúng tinh thần §9: tra registry **trước**.)
3. **Verify trên dữ liệu có thể phân biệt được hai giả thuyết.** Lần verify 07-17 đúng nhưng làm ở
   vùng `F≈1` nên vô hiệu với câu hỏi này — "đã verify rồi" không đồng nghĩa "đã verify cho câu hỏi
   đang hỏi".
4. **Bằng chứng cơ chế trước, A/B sau.** Nếu chỉ chạy A/B và thấy −1,70pp, rất dễ kết luận nhầm
   "phép sửa làm mất alpha thật nên đừng sửa" — đúng hành động, sai lý do, và lần sau sẽ sai tiếp.
