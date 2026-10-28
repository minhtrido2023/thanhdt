# Độ trễ rating 8L — Phần 1 (trễ vận hành) + Phần 3 (giả định trễ trong backtest)

Job `Taylor_20261020_032153` · 2026-10-20 · read-only (không sửa code production, không ghi đè pin).
Phần 2 ("trễ tín hiệu") KHÔNG làm ở đây — chỉ đề xuất ở §5.

**Đơn vị N**: cặp (ticker, quý) = một sự kiện công bố độc lập. **Universe**: `tav2_mike.universe_pit`
(`in_universe` tại phiên cuối cùng của quý, ruleset_version 1). Không dùng `profit_*`.
Mọi số dưới đây in ra từ `analyze_lag.py` / `phase3_classify.py` (stdout lưu ở `out_analyze_stdout.txt`,
`out_phase3_stdout.txt`); các số đo trực tiếp trong lệnh tay được ghi lệnh/CSV cạnh nó.

## 0. Kết luận ngắn

1. **Không có nguồn ngày công bố THẬT đầy đủ, độc lập.** Có hai nguồn, cả hai đều không hoàn hảo:
   `ticker_financial.Release_Date` (vendor; `fa_ratings_8l.time` = chính cột này) và
   `tav2_bq.stock_news` (tin FiinGroup, độc lập; **CHƯA có trong `data_registry`**, phủ dày chủ yếu
   2019-2021). Hai nguồn khớp trong ±1 ngày ở **62,3%** của N=7.934 cặp; tiêu đề tin có thể là bản
   tóm tắt FiinGroup đăng muộn hơn hồ sơ ⇒ tin không phải sự thật tuyệt đối.
2. **Phần 1 — trễ vận hành từ Release_Date tới khi rating xuất hiện trong `fa_ratings_8l`**:
   - Q2/2026 (cửa sổ cũ: ngày làm việc 15→31/7), universe N=380: **median 3,4 ngày, p75 8,4, p90 9,4,
     max 26,4**. Đoạn (a) RD→có trong `ticker_financial` (ước lượng FIFO): median 2, p75 4, p90 7 ngày.
     Đoạn (b) có trong TF→có rating: median 15,9 giờ, p75/p90 111,9 giờ (= chờ refresh thứ Bảy, vì
     cửa sổ cũ kết thúc 31/7 và 1-10/8 bị SKIP).
   - Q3/2026 (cửa sổ mới, 17:30 hằng ngày kể cả cuối tuần), N=15 (4 trong universe) — time-travel
     theo giờ: (a) cùng ngày 4/15 · hôm sau 9/15 (gồm KBC bị cắt trái — đã có từ đầu cửa sổ 10-13 17:00) · 2 ngày 1/15 · 4 ngày 1/15 (CMD, qua cuối tuần);
     (b) **1 giờ ở 12/15**, 18 giờ ở 2/15 (TF vào lúc nửa đêm ⇒ chờ 17:30 hôm sau), 1 ca bị cắt trái.
   - Ingest TF quan sát được trong khung **16:00–17:00 ICT** (snapshot giờ chẵn) — khớp `cron_registry`
     (~16:36) ⇒ refresh 17:30 hiện là đúng giờ.
3. **Phần 3 — giả định trễ trong backtest**:
   - Đường chính (`eff_date_of` = Release_Date, NULL → `time`, offset 0) **không có hằng số trễ** —
     nó TIN `Release_Date`. Trong universe 2014Q3–2026Q2 (N=17.206):
     - **Nhìn trộm CHẮC CHẮN: 7 cặp** (0 trước 2026; 5 ở 2026Q1, 2 ở 2026Q2): `Release_Date` ≤ RD
       quý trước (vendor chép RD của quý trước sang). Mỗi ca **sớm ~91 ngày** (median `time−RD`) và
       **ghi đè đúng dòng rating của quý trước** trong `fa_ratings_8l` (dedupe `ROW_NUMBER(q_time DESC)`).
     - **Nhìn trộm KHẢ NĂNG CAO: 125 cặp Q1 2025/2026** có RD = 01-07/04 (≤7 ngày sau quý, `time==RD`
       125/125). Ở các ca có tin (N=12, mọi universe), RD **sớm hơn tin median 35 ngày** (10/12 sớm ≥6 ngày).
       Đây là hiện tượng MỚI: 2014-2024 chỉ 14 cặp như vậy.
     - Theo tin độc lập (chỉ ở cặp có tin, N=2.427 universe): RD sớm hơn tin ≥6 ngày ở **9,7–10,2%**
       phi ngân hàng (Q1/Q2/Q4; theo giai đoạn 8,6–8,7%), 4,2% (Q3), **0% ngân hàng**. Một phần có thể do tin đăng muộn ⇒ đây là
       cận TRÊN, không phải số nhìn trộm.
   - **Quá thận trọng**: lens NPL/LLR ngân hàng (FiinPro, +45 ngày / Q4 +90) **luôn trễ một quý**: 0% dòng
     rating ngân hàng dùng NPL cùng quý (N=823 bank-quý), vì RD ngân hàng luôn sớm hơn mốc +45/+90
     (gap median 13–17 ngày Q1–Q3, **60 ngày Q4**). Q2 (bán niên soát xét): RD muộn hơn tin ≥6 ngày ở
     **57,8%** cặp ngân hàng có tin và 28,5% phi ngân hàng ⇒ vendor có vẻ ghi RD theo bản soát xét.
   - Dòng NULL RD (eff = `time` placeholder, offset 0 từ 2026-10-16): 0,2% (2014-19) → 1,1% (2020+) phi
     ngân hàng, 0% ngân hàng. Ở 18 dòng NULL có tin: `time` sớm hơn tin ≥2 ngày ở **11/18** (median −13,5
     ngày) ⇒ offset 0 nghiêng về nhìn trộm trên nhóm nhỏ này (N quá nhỏ để kết luận chắc).
   - **Không tự kết luận lại số pin R3/V2.4.** Hướng tác động: thiên lệch lạc quan nhỏ, tập trung 2025-2026
     (7 ca chắc + ≤125 ca Q1 khả năng cao, trên ~420 mã/quý), đúng giai đoạn OOS gần nhất.

## 1. Nguồn và ngữ nghĩa `Release_Date`

| Kiểm | Kết quả | Nguồn |
|---|---|---|
| `fa_ratings_8l.time` | = `eff_date_of(Release_Date, time)` (offset 0) | `rating_8l_history.py:78-85, 607` |
| `time == Release_Date` (universe, 2025Q1-26Q3) | 2.478/2.525 | A1, `out_analyze_stdout.txt` |
| RD vendor sửa LÙI sau khi đã ingest | 22/460 cặp Q2/2026 giữa pin 07-29 và hiện tại (vd HAT 07-29→07-21, BTW 07-27→07-20) | so `raw/tf_pin_202607.csv` vs `raw/tf_current.csv` |
| RD dồn cục theo ngày batch | Q4/2025: 444 dòng RD = 2026-02-02; Q1/2025: 136 dòng = 2025-05-05 | `raw/tf_current.csv` value_counts |
| Bảng có cột ingest-time? | **Không** (`ticker_financial`, `fa_ratings_8l` không có `ingested_at`) | `bq show` |

⇒ `Release_Date` là ngày vendor gán, đa số khớp ngày công bố (±1 ngày 62,3%), nhưng (i) có thể bị sửa
lùi sau ingest, (ii) có ca chép từ quý trước, (iii) Q1 2025/2026 có cụm RD đầu tháng 4 không thể là ngày
công bố BCTC quý 1.

Nguồn quan sát thời điểm vào BQ (vì không có cột ingest):
`data/ticker_financial_breadth.csv` (đếm thật ~19:00 ICT ngày làm việc, từ 2026-07-12) ·
`tav2_pin.*_pin_2026{07,08,10}` (snapshot 07-29 22:30, 09-05 10:33, 10-01 22:01 ICT) ·
BigQuery time-travel 7 ngày, chụp mỗi giờ (`pull_timetravel.py`) · log refresh
`mike/logs/fa_ratings_8l_refresh.log` (36 lần OK, 07-14 → 10-19).

## 2. Phần 1 — số liệu

### 2.1 Quý kết thúc → Release_Date (universe, RD not null) — `out_qend_to_release_by_quarter.csv`

| Quý | Phi NH N | median | p75 | p90 | max | NH N | median | p90 | max |
|---|---|---|---|---|---|---|---|---|---|
| 2025Q1 | 391 | 23 | 29 | 35 | 35 | 23 | 28 | 29 | 29 |
| 2025Q2 | 397 | 29 | 31 | 31 | 32 | 23 | 30 | 30 | 31 |
| 2025Q3 | 407 | 28 | 30 | 34 | 34 | 25 | 29 | 30 | 31 |
| 2025Q4 | 394 | 33 | 33 | 33 | 33 | 25 | 33 | 33 | 33 |
| 2026Q1 | 389 | 28 | 34 | 34 | 34 | 24 | 28 | 29 | 34 |
| 2026Q2 | 360 | 30 | 30 | 31 | 38 | 24 | 30 | 31 | 31 |
| 2026Q3 (đang mùa) | 4 | 14 | 14,25 | 14,7 | 15 | – | – | – | – |

Phân phối bị cắt trên rất gắt (p90 = max) ⇒ khớp với RD = ngày batch vendor, không phải đuôi thật của
mã nộp muộn. Q4 KHÔNG trễ hơn ở bảng này (Q4/2025 = 33 ngày cho mọi mã) vì RD Q4 là BCTC quý 4 chưa
kiểm toán, không phải BCTC năm.

### 2.2 Đoạn (a): Release_Date → có trong `ticker_financial`

- **Q2/2026, breadth vs cum(RD≤d)** (`out_breadth_vs_cum_release_2026Q2.csv`): giữa mùa số mã THỰC CÓ
  ít hơn số mã có RD≤d **128–255 mã** (20/7 → 31/7); bắt kịp 17/8.
- **Ước lượng FIFO** (`out_a_segment_fifo_2026Q2.csv`; trừ dòng NULL RD theo `time`): N=1.024 (46 không
  ghép được): median 3, p75 4, p90 8, max 23 ngày lịch; universe N=380: median 2, p75 4, p90 7.
  Giả định FIFO ⇒ đây là cận DƯỚI của độ phân tán.
- **Kiểm chéo pin 07-29 22:30**: trong 552 cặp RD≤07-28, **96 (17,4%) chưa có** trong bảng lúc đó
  (`out_q2_2026_rd_before_pin_but_absent.csv`; chỉ 5 cặp universe). Trễ tối thiểu median 7 ngày.
- **Q3/2026 time-travel theo giờ** (`out_q3_2026_timetravel_first_seen.csv`, N=15): bảng ở §0.

### 2.3 Đoạn (b): có trong TF → có dòng trong `fa_ratings_8l`

- Độ phủ: **100%** cặp universe 2025Q1–2026Q3 có dòng rating tại eff_date (D1). Pin 09-05: 100 cặp TF
  chưa có dòng rating, chỉ 3 trong universe (MFS, ODE, BGE); 92/100 hiện đã có.
- Theo lịch chạy thật (`out_ab_total_2026Q2.csv`): Q2/2026 universe median 15,9 giờ, p75–p90 111,9 giờ.
  Lý do: luật cửa sổ CŨ trong mùa Q2 = "15 → hết tháng đầu quý, ngày làm việc" (log `RUN — trong cua so
  mua BCTC (15..het thang dau quy, ngay lam viec)`); 01-14/8 đều `SKIP` ⇒ chỉ còn refresh thứ Bảy
  (01/8, 08/8, 15/8 …). Luật hiện tại (10 tháng đầu → 10 tháng kế, hằng ngày) đã xoá đoạn hở này.
- Q3/2026 (luật mới): (b) = 1 giờ ở 12/15.

### 2.4 Tổng RD → rating, Q2/2026 universe: median 3,4 · p75 8,4 · p90 9,4 · max 26,4 ngày.

### 2.5 Ngoại lai

- **Trễ > p90 (RD)**: 75 cặp 2025Q1-26Q2 (`out_outliers_gt_p90.csv`), không mã nào lặp ≥3 quý ⇒
  không có "mã nộp muộn kinh niên" theo RD (RD bị cắt trên nên chỉ số này yếu).
- **Ingest muộn nhất (Q2/2026)**: TLP (RD 04-03, vào 08-03), CT6/HTE/VHE/HOT/HPD/HVA/TA9/SD2/SGP
  (RD 05-04 = RD của Q1, dữ liệu Q2 vào 03-14/8) — nguyên nhân: **RD chép từ quý trước** (lỗi vendor),
  không phải công bố muộn. KHW/NTH (RD 07-14, chưa vào lúc 07-29) — chưa xác định nguyên nhân.
- **RD < cuối quý**: 22 cặp (7 universe), toàn bộ 2026Q1–Q2 (`out_release_date_before_quarter_end.csv`).

## 3. Phần 3 — kiểm kê hằng số trễ (grep `rating_8l.py`, `rating_8l_history.py`, `custom_basket.py`, `custom30*.py`)

| Vị trí | Hằng số | Dùng cho | Đường |
|---|---|---|---|
| `rating_8l_history.py:78` `NULL_RD_EFF_OFFSET_DAYS = 0` (đổi từ 45 ngày 2026-10-16) | 0 | eff_date dòng RD NULL (`eff_date_of`, l.81-85; dùng ở `main` l.607, `attach_icb_pit` l.208, `bank_eff_date` l.397) | LIVE + backtest |
| `rating_8l_history.py:12,607` eff_date = Release_Date | 0 (tin RD) | mọi dòng rating | LIVE + backtest |
| `rating_8l_history.py:352-355` `bank_aq_avail_date` | +45 ngày, Q4 +90 | FiinPro NPL/LLR ngân hàng (`bank_aq_asof`) | LIVE + backtest |
| `custom_basket.py:742-743` `rating_asof` | 0, `bisect_right` ⇒ dùng cả dòng eff == ngày rebal | custom30V gate | backtest (thực thi T+1 theo quy chuẩn) |
| `custom_basket.py:756` QFLOOR | RD, NULL → `time`+45 | Đ2 quality floor | nghiên cứu, mặc định TẮT |
| `custom_basket.py:1275` DY_TIEBREAK | RD, NULL → `time`+45 | tie-break cổ tức | nghiên cứu, mặc định TẮT |
| `custom_basket.py:464` | +45 | cửa sổ tìm ngày bước OShares (không phải trễ BCTC) | – |
| `rating_8l.py` | không có hằng số trễ | – | – |

### 3.1 Bảng phân loại (universe, 2014Q3–2026Q2) — `out_phase3_peek_classes.csv`

| Nhóm | N | NULL RD | Chắc chắn nhìn trộm | RD ≤ quý+7 | N có tin | RD sớm hơn tin ≥6 ngày | RD muộn hơn tin ≥6 ngày |
|---|---|---|---|---|---|---|---|
| 2014-19 NH | 237 | 0 | 0 | 0 | 22 | 0% | 4,5% |
| 2014-19 phi NH | 5.911 | 14 | 0 | 4 | 509 | 8,6% | 1,0% |
| 2020-24 NH | 442 | 0 | 0 | 0 | 102 | 0% | 24,5% |
| 2020-24 phi NH | 8.095 | 75 | 0 | 10 | 1.783 | 8,7% | 11,2% |
| 2025Q1-26Q2 NH | 144 | 0 | 0 | 5 | 0 | – | – |
| 2025Q1-26Q2 phi NH | 2.377 | 39 | **7 (0,29%)** | **122** | 11 | 18,2% (2/11) | 0% |

Theo quý (cột "tin" chỉ tính cặp có tin): sớm hơn tin ≥6 ngày — phi NH Q1 9,7% · Q2 9,7% · Q3 4,2% ·
Q4 10,2%; NH 0% mọi quý. Muộn hơn tin ≥6 ngày — **Q2: NH 57,8%, phi NH 28,5%**; các quý khác ≤1,1%.

Hằng số FiinPro ngân hàng so với RD ngân hàng (N=823; `gap` = mốc avail − RD; không có ca nào gap<0):
Q1 median 17 ngày (p10 11, p90 25) · Q2 13 (11, 17) · Q3 17 (13, 25) · **Q4 60 (57, 69)**.

### 3.2 Tác động ước lượng (định tính — không chạy lại backtest)

- **Chiều lạc quan (nhìn trộm)**: 7 ca chắc chắn (~91 ngày) + tới 125 ca Q1 2025/2026 khả năng cao
  (~35 ngày, suy từ 12 ca có tin) + tới ~9% cặp phi NH lệch ≥6 ngày so với tin. Tập trung 2025-2026
  ⇒ chạm cửa sổ OOS gần nhất của R3/V2.4. Chỉ đổi kết quả khi dòng đó vượt cổng ≤3 trong cửa sổ lệch
  (≈60-90 lần vượt cổng mỗi quý trong universe, §5) ⇒ **ước lượng** ảnh hưởng nhỏ, chưa đo.
- **Chiều bi quan**: lens NPL ngân hàng luôn chậm một quý; Q2 RD theo bản soát xét (trễ hơn quý 2 chưa
  soát xét). Hướng: làm rating ngân hàng phản ứng chậm hơn thực tế — không nhìn trộm.
- **Đường live vs backtest**: backtest dùng rating từ RD; live có thêm (a)+(b) = median 3,4 ngày, p90
  9,4 (Q2/2026). Đây là chênh lệch thực thi, không phải nhìn trộm thông tin, nhưng làm backtest lạc
  quan hơn live đúng chừng đó cho các mã đổi rating.

## 4. Đề xuất (cần duyệt, CHƯA làm)

1. **Vá eff_date**: nếu RD ≤ RD quý trước hoặc RD < cuối quý ⇒ eff = `time` (hoặc NULL-fallback).
   7 ca, đổi rating thật ⇒ cần quant-skeptic + re-pin theo luật 1-trục.
2. **Hỏi bq_admin**: (i) nguồn của `Release_Date` + vì sao Q1 2025/2026 có RD 01-07/04 và RD bị sửa lùi;
   (ii) thêm cột `first_ingested_at` vào `ticker_financial` (giống `stock_news`).
3. **Data registry** (§9/§13, Mike duyệt): thêm entry `stock_news` (chưa có); bổ sung bẫy RD (carry-over,
   sửa lùi, cụm đầu tháng 4) vào `fundamentals/ticker_financial.md`.
4. Bank FiinPro +45/+90: có thể nới về RD của chính ngân hàng nếu FiinPro có ngày cập nhật — không đổi khi
   chưa có nguồn ngày.

## 5. Đề xuất cho Phần 2 (trễ tín hiệu)

- **Cần**: (1) snapshot hằng ngày `(ticker, quarter, Release_Date, time)` của `ticker_financial` +
  `(ticker, time, rating)` của `fa_ratings_8l` vào `tav2_mike` (append-only, như
  `corporate_action_snapshots`) — vì time-travel chỉ giữ 7 ngày và pin chỉ 1 lần/tháng; (2) cột
  `first_ingested_at` từ bq_admin nếu có; (3) giá `tav2_bq.ticker` để đo phản ứng giá quanh RD vs quanh
  ngày rating vào bảng.
- **N sự kiện**: số lần vượt cổng ≤3 trong universe (theo quý eff_date): 2025Q2 66 · Q3 64 · Q4 65 ·
  2026Q1 92 · Q2 53 · Q3 64 (tới nay) ⇒ ~60-90/quý (đo trên `raw/fa_current.csv`). Đo trễ thật (có
  snapshot) chỉ bắt đầu được từ khi cài snapshot ⇒ 1 quý ≈ 60-90 sự kiện; muốn ≥200 cần ~3 mùa BCTC,
  hoặc dùng proxy FIFO/pin cho Q2/2026 (đã có ở đây).

## Tái lập

```bash
cd mike/agents/Taylor/research/rating_8l_lag_20261020
# raw/*.csv kéo bằng bq (lệnh trong lịch sử job; tf_current = ticker_financial quarter>=2014Q1 + universe_pit tại cuối quý)
python3 pull_timetravel.py raw      # chỉ lặp lại được trong 7 ngày (time-travel)
python3 analyze_lag.py              # Phần 1 + bảng ngân hàng
python3 phase3_classify.py          # Phần 3
```
