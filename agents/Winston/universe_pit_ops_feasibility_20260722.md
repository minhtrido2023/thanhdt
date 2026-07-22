# `universe_pit` — Khả thi VẬN HÀNH (data-ops lens)

Job `Winston_20260722_033620` · 2026-07-22 · Winston (Data/Regime Ops)
**RESEARCH. Không implement code/cron trong job này.** Phần kiến trúc/thuật toán = Taylor
(`Taylor_20260722_033547`). Đây chỉ trả lời: *chạy được không, tốn bao nhiêu, chạy lúc nào, hỏng thì sao.*

Nguồn đọc: `agents/Taylor/research/ticker_prune_universe_governance.md` +
`/tmp/ccdb-uploads/1529330622634528930/ticker_prune_universe_QA.md` (bản QA của bq_admin —
**lưu ý: file này KHÔNG nằm trong repo**, chỉ có ở đường dẫn upload; nên copy vào repo trước khi nó bay mất).

---

## 0. TL;DR — 5 câu

1. **Chi phí BQ không phải vấn đề, không cần cân nhắc.** Backfill toàn bộ 26 năm từ
   `tav2_bq.ticker` = **182,7 MB / 2,5 giây / ~0,001 USD** (đo thật, `--dry_run` + chạy thật).
   Rebuild TOÀN BỘ mỗi ngày cũng chỉ **~0,024 USD/tháng**. Không có bài toán chi phí ở đây.
2. **Bằng chứng quyết định: `ticker_prune` là TẬP CON THỰC SỰ của universe tính thẳng từ `ticker`,
   tại MỌI mốc lịch sử — `only_prune = 0` ở cả 8 mốc đo.** Curation `hit_ticker_list` **chỉ BỚT
   mã, không bao giờ THÊM** mã trượt ngưỡng thanh khoản → **rủi ro số 1 trong §5 doc Taylor
   ("rule của ta có thể thua curation của họ") đã bị bác bỏ bằng dữ liệu.** Bỏ curation không mất
   thông tin nào.
3. **Nhưng đọc thẳng `ticker` KHÔNG miễn nhiễm ghi-đè-lịch-sử** — `tav2_bq.ticker` cũng có
   `creationTime = 2026-07-12 01:06 ICT` (bị TRUNCATE+tạo lại y hệt `ticker_prune`), và đo được
   **+4.062 dòng được thêm vào lịch sử 2016-2025** so với cache local. Nhẹ hơn prune ~11× về tỉ lệ
   (0,12% vs 1,39%) nhưng **khác 0** ⇒ lớp append-only đóng băng của ta là **bắt buộc**, không phải
   "nice to have".
4. **Cadence: KHÔNG nên thêm 1 dòng cron mới.** Nên nhét builder thành **step [0.5] trong
   `daily_refresh_v34b_linux.sh` (18:30 ICT)**, ngay sau vòng lặp precheck đã tự chứng minh ingest
   ngày T xong. Tái dùng luôn cơ chế chờ/abort/alert có sẵn, tự động nằm trước `bq_freshness_check`
   19:00 và `golive_recommend` — không phát sinh race mới.
5. **Cutover: KHÔNG fallback ngầm về `ticker_prune`.** Nhưng cũng đừng cắt một nhát — chạy
   **shadow 10 phiên** (build + so depth mỗi ngày, chỉ alert), rồi cutover theo nhóm. Một consumer
   phải được Taylor A/B trước khi đổi: **breadth trong `macro_state_live.py`** (input regime
   production, mẫu số đổi tới +26% ở lịch sử).

---

## 1. Chi phí BQ thật (đo, không đoán)

Bộ lọc đã được bq_admin xác nhận (QA §0), mọi cột đều có sẵn trong `tav2_bq.ticker`:

```sql
Volume_3M_P50 * Price / NULLIF(Inflation_7, 0) > 1e9
```

| Phép đo | Bytes scanned | Thời gian | Chi phí @$6,25/TiB |
|---|---|---|---|
| **A. Backfill toàn bộ** `ticker` 2000-07-28 → 2026-07-21 | **182.741.835 (182,7 MB)** | **2,5 s** | **~0,0011 USD** |
| B. Incremental cửa sổ 7 ngày | 445.741 (446 KB) | <1 s | ~0,000003 USD |
| C. *(hiện tại)* `SELECT DISTINCT ticker FROM ticker_prune` | 4.680.694 (4,7 MB) | — | ~0,00003 USD |
| D. *(hiện tại)* PIT join `(time, ticker)` trên `ticker_prune` | 12.122.654 (12,1 MB) | — | ~0,00007 USD |
| E. *(hiện tại)* breadth MA200 trên `ticker_prune`, 1 năm | 2.557.496 (2,6 MB) | — | ~0,00002 USD |

**Mức tăng chi phí BQ hàng ngày nếu chuyển sang tính trực tiếp từ `ticker`:**

- Nếu chạy **incremental** (chỉ ngày mới): 446 KB/ngày vs 4,7-12,1 MB/ngày của cách gọi
  `ticker_prune` hiện tại → **RẺ HƠN**, không phải đắt hơn.
- Nếu chạy **full rebuild mỗi ngày** (an toàn nhất, idempotent tuyệt đối): 182,7 MB × ~21 phiên
  = 3,8 GB/tháng ≈ **0,024 USD/tháng**.

> **Kết luận chi phí: không tồn tại trade-off.** Cột `Volume_3M_P50`/`Price`/`Inflation_7` là 3
> cột trên bảng columnar 5,1 GB — BQ chỉ đọc đúng 3 cột đó. Cái làm `ticker` "nặng" (90+ cột) không
> bao giờ bị chạm. **Đừng để chi phí BQ vào bảng cân nhắc của user; nó là số 0.**

*(Đính chính doc drift: `CLAUDE.md` ghi `ticker` ~15,2 M dòng / 16,3 GB. Đo hôm nay:
**4.089.542 dòng / 5,14 GB / 1.291 mã / 2000-07-28 → 2026-07-21**. Cần sửa CLAUDE.md — non-blocking.)*

### 1.1 Kết quả backfill (chạy thật, không phải ước lượng)

```
rows_all = 4.089.542   rows_in_universe = 1.157.238
tickers_all = 1.291    tickers_từng_vào_universe = 911
range = 2000-07-28 → 2026-07-21
```

So với `ticker_prune`: 930.245 dòng / 543 mã. Tức universe thuần-thanh-khoản **rộng hơn 24% về dòng
và 68% về số mã** — đúng bằng phần mà `hit_ticker_list` (453 mã, suy ra từ kết quả backtest) đã cắt đi.

---

## 2. Bằng chứng quyết định: curation KHÔNG mang thông tin bổ sung

Đây là số quan trọng nhất của job này. So universe tính-từ-`ticker` (PIT) vs `ticker_prune`
tại 8 mốc lịch sử, join theo `(time, ticker)`:

| Ngày | n_pit | n_prune | n_both | **chỉ-có-ở-prune** |
|---|---|---|---|---|
| 2014-06-30 | 169 | 140 | 140 | **0** |
| 2016-06-30 | 198 | 167 | 167 | **0** |
| 2018-06-29 | 201 | 180 | 180 | **0** |
| 2020-06-30 | 255 | 226 | 226 | **0** |
| 2022-06-30 | 405 | 321 | 321 | **0** |
| 2024-06-28 | 369 | 310 | 310 | **0** |
| 2026-06-15 | 276 | 233 | 233 | **0** |
| 2026-07-21 | 264 | 264 | 264 | **0** |

**`ticker_prune` ⊊ `universe_pit`, chặt chẽ, ở mọi mốc.** Hệ quả trực tiếp:

- **Bác bỏ rủi ro §5 của Taylor** ("rule thanh khoản thuần của ta có thể thua curation của
  bq_admin — họ có thể lọc thêm mã cảnh báo/kiểm soát/BCTC ngoại trừ"). Nếu curation mang thông
  tin bổ sung, phải tồn tại mã nằm trong prune mà không đạt ngưỡng thanh khoản. **Không có mã nào,
  ở bất kỳ mốc nào.** Curation là phép trừ thuần túy, và theo QA §2.6-Tầng-2 phép trừ đó suy ra
  **từ kết quả backtest** → đó chính là selection bias, không phải thông tin.
- **Rule tái tạo chính xác hành vi LIVE hiện tại.** Ngày 2026-07-21: `n_pit = n_prune = 264`, khớp
  đúng con số `daily_refresh` log ghi (`ready: ticker_prune has 264 tickers`). Kiểm tra 12 phiên
  gần nhất: 267/265/268/265/266/266/265/265/263/263/262/**264** — trùng khít 100% với depth prune.
  ⇒ **Ngưỡng depth gate hiện hành (~225) chuyển thẳng sang universe_pit, không cần hiệu chuẩn lại.**
- Chênh lệch chỉ nằm ở **lịch sử** (prune bị TRUNCATE cắt cụt + hit-list lọc), không nằm ở hiện tại.

*(Caveat trung thực: 8 mốc, không phải toàn bộ ~6.500 phiên. Trước khi chốt nên chạy 1 lần
`only_prune` trên TOÀN lịch sử — vẫn chỉ ~183 MB, ~0,001 USD. Tôi không chạy trong job này vì nó
thuộc bước validate của Taylor, nhưng chi phí bằng 0 nên đừng bỏ qua.)*

---

## 3. Đọc thẳng `ticker` có thoát ghi-đè-lịch-sử không? — **KHÔNG hoàn toàn**

Đây là điều cần nói thẳng để user không yên tâm nhầm.

```
bq show tav2_bq.ticker        creationTime = 2026-07-11 18:06:41 UTC = 2026-07-12 01:06 ICT
bq show tav2_bq.ticker_prune  creationTime = 2026-07-11 18:08:23 UTC = 2026-07-12 01:08 ICT
```

**`ticker` cũng bị DROP + tạo lại, cùng lần chạy `--mode full` ngày 2026-07-12** — cách
`ticker_prune` đúng 102 giây. `WRITE_TRUNCATE` không chừa `ticker` ra.

Đo mức trôi lịch sử của chính `ticker` (BQ live vs cache local per-year, cache năm ≤2025 chưa
bị delta chạm lại):

| Năm | BQ live | Cache local | Chênh |
|---|---|---|---|
| 2013-2015 | — | — | 0 |
| 2016 | 196.110 | 196.095 | +15 |
| 2017 | 235.325 | 235.075 | +250 |
| 2018 | 269.324 | 268.931 | +393 |
| 2019 | 284.852 | 284.354 | +498 |
| 2020 | 296.397 | 295.893 | +504 |
| 2021 | 303.992 | 303.492 | +500 |
| 2022 | 309.688 | 309.190 | +498 |
| 2023 | 312.813 | 312.315 | +498 |
| 2024 | 316.591 | 316.202 | +389 |
| 2025 | 316.840 | 316.323 | +517 |
| **TỔNG** | **3.489.698** | **3.485.636** | **+4.062** |

Mẫu ~500 dòng/năm đều đặn ≈ lịch sử đầy đủ của **~2 mã** được nạp lại — đúng chữ ký của đường ghi
#3 (`replace_ticker_data_in_bigquery_table`), event-driven theo BCTC quý / điều chỉnh giá. QA §2.3
xác nhận cơ chế này **không có lịch và không có điểm kết thúc**.

**So sánh mức độ:**

| Bảng | Dòng trôi | Tổng dòng (≥2013) | Tỉ lệ |
|---|---|---|---|
| `ticker_prune` | +10.630 | 767.165 | **1,39 %** |
| `ticker` | +4.062 | 3.489.698 | **0,12 %** |

⇒ Chuyển sang `ticker` **giảm biên độ trôi ~11×** và **loại bỏ hoàn toàn** hai nguồn nhiễu lớn nhất
(hit-list curation + mất trắng mã sau TRUNCATE), **nhưng không đưa trôi về 0**. Do đó lớp
`universe_pit` **bắt buộc phải append-only + đóng băng dòng quá khứ** đúng như Taylor thiết kế —
đây không còn là lựa chọn thiết kế mà là yêu cầu bắt buộc do dữ liệu chứng minh.

### 3.1 Đề xuất ops kèm theo: **drift detector, gần như miễn phí**

Vì full rebuild chỉ tốn 182 MB / 2,5 s / 0,001 USD, **mỗi ngày hãy tính lại TOÀN BỘ lịch sử và
diff với bảng `universe_pit` đã đóng băng**:

- diff = 0 → im lặng.
- diff ≠ 0 → **KHÔNG sửa dòng quá khứ**, chỉ log + alert Discord: *"upstream `ticker` vừa viết lại
  N dòng lịch sử ở các năm X, Y, Z; các mã bị chạm: …"*.

Chi phí: **~0,024 USD/tháng, +2,5 s/ngày**. Đổi lại: đội có **cảnh báo chủ động** khi baseline bị
đổi dưới chân — đúng thứ mà §1.3 của doc Taylor phát hiện được sau 8 ngày một cách tình cờ. Đây là
cái mà 5 vấn đề của bq_admin (§5 dưới) *không* cần ta theo dõi thủ công nữa, vì mọi hệ quả của
chúng đều hiện ra ở đây.

---

## 4. Cron / cadence — trả lời 4 câu hỏi bắt buộc (`cron_registry.md`)

### Câu 1 — Đọc gì + vintage?
`tav2_bq.ticker` **LIVE**, tuyệt đối **KHÔNG qua `BQ_LOCAL_CACHE`**. Ba lý do:
(a) cache sync 23:45 ⇒ luôn T-1, builder chạy 18:30 sẽ tính universe của hôm qua;
(b) cache `ticker` là thư mục chunked delta-theo-năm, **về mặt cấu trúc không thể** thấy dòng lịch
sử bị viết lại (chính bảng §3 chứng minh: 4.062 dòng vô hình với cache);
(c) tiền lệ thật — sự cố 2026-07-12 `publish_gated_state.py` đọc cache T-1 làm gate
`MAX_STATE_LAG=0` fail cứng. Builder phải `os.environ.pop('BQ_LOCAL_CACHE')` process-local trước
import, **không sửa `wc_env.sh`**.

### Câu 2 — Nguồn tươi lúc nào? (ĐO THẬT, không tin comment)
`cron_registry.md` ghi "ingest xong ~17:30" — đo lại bằng log precheck thật của
`daily_refresh_v34b_linux.sh` 7 phiên gần nhất:

| Ngày | Kết quả precheck lúc 18:30 |
|---|---|
| 07-13 | ready, attempt 1 (265 mã) |
| **07-14** | **not ready ×4 → mất ~1 giờ** (10 mã lúc 18:30) |
| 07-15 | ready, attempt 1 (264) |
| 07-16 | ready, attempt 1 (262) |
| 07-17 | ready, attempt 1 (262) |
| 07-20 | ready, attempt 1 (261) |
| 07-21 | ready, attempt 1 (264) |

⇒ **6/7 phiên ingest xong trước 18:30; 1/7 trễ >1 giờ.** Comment "~17:30" đúng ở mode bình thường
nhưng **không phải bảo đảm** — builder bắt buộc phải có vòng chờ + depth gate, không được cho rằng
18:30 là chắc chắn.

Kiểm tra thêm chất lượng cột đầu vào ngày T (12 phiên gần nhất): `Volume_3M_P50 IS NULL = 0`,
`Price IS NULL = 0`, `Inflation_7 NULL-hoặc-0 = 0` trên mọi ngày ⇒ **không có độ trễ tính chỉ báo**,
ngày T dùng được ngay khi ingest xong, không phải chờ thêm phiên.

### Câu 3 — Cần T hay T-1?
**T** (cùng ngày). Consumer LIVE (`golive_recommend_v23.py` 19:00 chọn rổ CAPIT, `custom_basket.py`,
`preflight_check.sh` 08:45 sáng hôm sau) đều cần membership của phiên vừa đóng. Backtest chỉ cần
lịch sử ⇒ không ràng buộc.

### Câu 4 — Ai tiêu thụ + deadline?
Deadline cứng gần nhất = **`bq_freshness_check.sh` 19:00 ICT** (gate BLOCK cho DollarBill) và
`golive_recommend` chạy trong cùng chain đó. Deadline mềm = preflight 08:45 sáng T+1.

### → Khuyến nghị: **KHÔNG thêm dòng cron mới**

Nhét builder thành **step [0.5] của `daily_refresh_v34b_linux.sh`**, ngay sau vòng lặp precheck
hiện có (dòng 43-59):

| Tiêu chí | Cron riêng 18:25 | **Step [0.5] trong daily_refresh** |
|---|---|---|
| Vòng chờ ingest | phải viết lại (trùng lặp logic) | **tái dùng vòng đã có, đã chứng minh ingest xong** |
| Thứ tự với 19:00 / golive | phải tự bảo đảm | **tự động đúng** |
| Alert khi fail | phải viết mới | **tái dùng `die()` + alert Discord có sẵn** |
| Race với ingest chậm (07-14) | tự xử lý | **thừa hưởng retry 6×15' + abort sạch** |
| Runtime thêm | — | **+2,5 s** trên chain ~90 s+ |
| Dòng cron mới | +1 | **0** |

Bất lợi duy nhất: builder chết theo nếu `daily_refresh` chết. Nhưng đó **đúng là hành vi mong muốn**
— nếu ingest ngày T chưa xong thì universe ngày T *không được phép* tồn tại. Fail chung, fail-closed.

Cuối tuần / ngày lễ: không có dòng mới trong `ticker` ⇒ builder no-op (idempotent theo `as_of_date`),
không cần guard riêng.

---

## 5. Rà 5 vấn đề kỹ thuật bq_admin nêu (QA Phần 4) — **KHÔNG phải cả 5 đều vô hại**

Dispatch hỏi "nếu không liên quan thì nói rõ để user yên tâm không phải theo dõi nữa". Câu trả lời
trung thực là **2/5 vẫn liên quan**, nên tôi không nói "yên tâm" cho cả gói.

| # | Vấn đề bq_admin nêu | Còn ảnh hưởng `universe_pit`? | Lý do |
|---|---|---|---|
| 1 | Thống nhất nguồn universe giữa 3 đường ghi | **KHÔNG** | `universe_pit` không đọc `ticker_prune`, không đọc `hit_ticker_list`. Ba đường ghi đó chỉ tranh nhau nội dung `ticker_prune` — bảng ta sắp thôi dùng. Đây là việc nội bộ của họ. |
| 2 | Xây lớp snapshot as-of ở phía research | **CHÍNH LÀ VIỆC NÀY** | Đây là khuyến nghị họ đưa cho ta, đúng thứ đang thiết kế. |
| 3 | `delete_gcs_files(...)` bị comment tại `deeplearning/bigquery.py:538` → file CSV cũ trong `gs://tav2-gs/v2_prune/` không bao giờ bị xoá | **KHÔNG (với 1 dấu hỏi)** | Prefix `v2_prune/` chỉ nạp lại `ticker_prune` ở đường ghi #1. `universe_pit` đọc `tav2_bq.ticker`, không chạm GCS. **Dấu hỏi:** `ticker` cũng bị TRUNCATE cùng lần chạy (§3) nên hẳn có prefix GCS riêng của nó; ta **không có quyền đọc code/GCS của họ** để xác nhận prefix đó có bị bug tương tự không. ⇒ Không kết luận "an toàn", mà **đưa về ta kiểm soát**: drift detector §3.1 sẽ bắt được nếu file GCS cũ làm `ticker` mọc lại dòng lạ. |
| 4 | Cờ `is_skip` không nhất quán: `deeplearning/bigquery.py` không tôn trọng, worker `schedule_tasks.py:441` có | **CÓ THỂ CÓ** | `is_skip` quyết định **mã nào được pipeline xử lý** — nếu nó tác động ở tầng ticker-list thì nó ảnh hưởng cả nội dung `tav2_bq.ticker`, không riêng prune. Ta không kiểm chứng được từ ngoài. **Không nên xoá khỏi tầm ngắm.** |
| 5 | `max_bad_records=10` — mỗi load job có thể âm thầm bỏ tối đa 10 dòng lỗi | **CÓ** | Đây là cấu hình **load job**, áp cho mọi bảng nạp qua đường đó, gồm `ticker`. Nghĩa là ≤10 dòng/lần nạp có thể biến mất không báo. Với ~250 phiên/năm × nhiều load, đây là nguồn thiếu dòng ngẫu nhiên, im lặng, **có thật**. |

### Kết luận cho user về mục này

**Không cần theo dõi 5 vấn đề đó như 5 việc riêng — nhưng cũng đừng coi là đã hết.** Thay vì phụ
thuộc việc bq_admin có sửa hay không (ta không sở hữu ETL của họ, `governance §4.3`), gói toàn bộ
rủi ro còn lại vào **một control duy nhất phía ta**:

> **Drift detector (§3.1): mỗi ngày tính lại toàn bộ lịch sử universe từ `ticker`, diff với bảng đã
> đóng băng, alert nếu ≠ 0.**

Vì mọi hệ quả quan sát được của #3/#4/#5 — dòng lạ mọc lại từ file GCS cũ, mã bị skip lệch pha,
dòng bị `max_bad_records` nuốt — **đều biểu hiện thành thay đổi dòng lịch sử của `ticker`**, và đều
bị control này bắt trong 24 giờ. Chi phí 0,024 USD/tháng. Đây là câu trả lời đúng: không phải "yên
tâm, không liên quan", mà **"đã có người canh, và người canh là ta chứ không phải họ"**.

---

## 6. Cache impact (`data/bq_cache/`)

Hiện trạng đo được:

```
data/bq_cache/            2,0 GB tổng
  ticker/     (chunked)   1,4 GB   3.485.636 dòng
  ticker_prune/ (chunked) 415 MB     756.535 dòng   ← ứng viên xoá sau cutover
  ticker_financial.parquet 70 MB
  manifest.json: "verified": false  (từ 2026-07-21T16:53Z)
```

**Vì sao `verified: false`:** `sync_bq_cache.py` chạy delta theo năm — chỉ tải lại chunk năm
`>= max_year` (2026), các file năm cũ giữ nguyên (`sync_bq_cache.py:268-300`). Cơ chế này **về mặt
cấu trúc không thể** vớt dòng lịch sử bị viết lại ⇒ count-mismatch mỗi khi đường ghi #3 chạy. Đây
cùng một lớp lỗi với `fa_ratings`/`fa_ratings_8l` (đã phải chuyển `full_only`), **không phải bug
mới**. Prune lệch 10.630 dòng, ticker lệch 4.062 dòng — trùng khớp §3.

### Cần đổi gì

| Việc | Chi tiết |
|---|---|
| Thêm `universe_pit` vào `TABLES` của `sync_bq_cache.py` | `partition_col = as_of_date`. **Delta là ĐÚNG** ở đây (khác `fa_ratings`): bảng ta thiết kế append-only, dòng quá khứ không bao giờ bị sửa ⇒ delta-theo-ngày an toàn về mặt bản chất. Nếu sau này cho phép ghi đè quá khứ thì phải chuyển `full_only` — nhưng làm vậy là phá chính mục tiêu của lớp này. |
| Kích thước ước tính | 1.157.238 dòng in-universe × `(DATE, STRING(3), BOOL, +metadata)`. Parquet nén cột rất tốt với ticker lặp lại → **~8-15 MB**. Nếu lưu cả dòng `in_universe=false` (4,09 M dòng) thì ~25-40 MB. **Khuyến nghị lưu cả 2 trạng thái** — chỉ tốn thêm ~20 MB và giúp phân biệt "bị loại" vs "không có dữ liệu", vốn là 2 chuyện khác nhau (xem caveat §7). |
| Ảnh hưởng cache `ticker` / `ticker_financial` | **Không có.** Mỗi bảng là thư mục/parquet độc lập, không chia sẻ state ngoài `manifest.json`. Thêm ~20 MB vào job 23:45 = không đáng kể. |
| Cơ hội dọn dẹp | Sau cutover, **`ticker_prune` cache 415 MB có thể bỏ hẳn** → sync 23:45 ngắn lại, ổ đĩa nhẹ 20%. **Nhưng phải theo §10 `coding_guidelines`**: grep xác nhận hết caller (28 file từng đọc path này, đã sửa sang chunked ở job `Winston_20260713_143546`), `git mv` sang `data/archive/`, cập nhật `data_registry.md` — **không `rm`**, không làm cùng lúc với cutover. |
| Caveat vintage | Cache `ticker` chỉ chứa `time >= 2013-01-01`. `universe_pit` phủ từ 2000. Backtest cần pre-2013 phải đọc BQ live — nêu rõ trong registry để không ai tưởng cache là đủ. |

---

## 7. Rủi ro vận hành khi cutover production

### 7.1 Danh sách consumer đang đọc `ticker_prune` (grep repo, loại `archive/` + script research)

| Nhóm | File | Vai trò | Mức rủi ro |
|---|---|---|---|
| **Gate vận hành** | `mike/bin/bq_freshness_check.sh:187-202` | BLOCK gate EOD price + **depth gate** `MIN_PRUNE_NAMES` | **CAO** — chặn DollarBill |
| | `mike/bin/preflight_check.sh:145-171` | depth gate 08:45 (~225 mã) | CAO — gate trước giờ mở cửa |
| | `daily_refresh_v34b_linux.sh:43-59` | precheck ingest ngày T (`MIN_TICKERS=200`) | CAO — chặn cả chuỗi DT5G |
| **Regime production** | `macro_state_live.py` | breadth % trên MA200, Pillar-B decoupling guard (cần ≥100 mã) | **CAO — cần A/B, xem 7.3** |
| **Chọn rổ / tiền thật** | `custom_basket.py:114,202,656` | custom30V production | CAO |
| | `deploy_golive_dt5g_v4/golive_recommend_v23.py` | rổ CAPIT live 19:00 | CAO |
| | `trading_bot/due_diligence.py`, `trading_bot/executor.py` | cờ "ngoài universe" | TRUNG BÌNH |
| **Backtest canonical** | `pt_v23_audit_2014.py` (21 chỗ, gồm pin R3) | CAPIT breadth + basket | TRUNG BÌNH (không chạm tiền, nhưng chạm số ta tin) |
| | `pt_v22_dt5g.py`, `pt_v4_dt5g.py`, `pt_v121_ensemble.py`, `lag_dnpr_harness.py`, `recommend_holistic.py` | BAL/LAG sims | TRUNG BÌNH |
| **Research** | ~330 script khác | — | THẤP (§3 guidelines: đừng mass-edit) |

### 7.2 Nếu builder lỗi / trễ 1 ngày thì sao? — **fail-closed, KHÔNG fallback**

Khuyến nghị dứt khoát: **không bao giờ tự động rơi về `ticker_prune`.**

Lý do không phải tính giáo điều mà là số học: universe của prune **nhỏ hơn 1,6-2,6× và lệch có hệ
thống** (§2). Một lần "fallback êm" nghĩa là *rổ chọn mã của một ngày giao dịch thật được sinh từ
một universe khác hẳn, không ai biết*. Đó đúng là kịch bản `coding_guidelines §5` cấm: khi không
chắc trạng thái, **dừng có lỗi rõ ràng, không đoán rồi đi tiếp**. Cũng là tiền lệ đã có: DT5G
`get_gated_state()` fail-closed về DT4 chứ không đoán bừa, và `MAX_STATE_LAG=0` chấp nhận chặn
cứng còn hơn giao dịch trên state cũ.

Hành vi đúng khi `universe_pit` thiếu ngày T:

```
universe_pit thiếu ngày cần dùng
  → raise, thoát non-zero
  → bq_freshness_check BLOCK (đã có cơ chế)
  → alert Discord Trading Daily: "universe_pit thiếu <date> — plan T+1 KHÔNG được sinh"
  → KHÔNG sinh plan, KHÔNG đọc ticker_prune thay thế
```

Chi phí thật của việc này: mất **1 phiên giao dịch**. Chi phí của fallback ngầm: **không đo được**,
và không ai phát hiện. Đánh đổi rõ ràng.

Thêm nữa, xác suất fail thấp hơn hẳn hiện trạng: builder = **1 câu SQL 2,5 giây**, không có mô hình,
không có phụ thuộc mạng ngoài, chạy sau khi ingest đã được chứng minh xong. Bề mặt lỗi nhỏ hơn
`ticker_prune` (3 đường ghi độc lập, TRUNCATE thủ công, backfill event-driven vô hạn) rất nhiều.

### 7.3 Kế hoạch cutover đề xuất (theo pha, không cắt một nhát)

| Pha | Việc | Tiêu chí sang pha sau |
|---|---|---|
| **P0 — Shadow (10 phiên)** | Builder chạy, ghi `universe_pit`, **không consumer nào đọc**. Mỗi ngày log: depth pit vs depth prune, danh sách mã lệch, drift detector. | 10/10 phiên depth khớp ±2 mã; drift detector không báo bất thường lạ |
| **P1 — Gate vận hành** | Chuyển `bq_freshness_check` / `preflight` / `daily_refresh` step[0] sang đếm universe từ `ticker`. **Lợi ích ròng:** gate thôi phụ thuộc bảng có 3 đường ghi ⇒ miễn nhiễm sự cố kiểu 2026-07-15 (prune bị moi ruột trong khi `ticker` vẫn lành). Ngưỡng giữ nguyên (§2). | 5 phiên xanh |
| **P2 — Backtest canonical** | `pt_v23_audit_2014.py` đổi sang `EXISTS ... u.time = t.time`. **Bắt buộc A/B + re-pin** (đây là việc của Taylor, §4.1 doc gốc). | quant-skeptic CONFIRMED + user duyệt |
| **P3 — Chọn rổ tiền thật** | `custom_basket.py`, `golive_recommend_v23.py`, `due_diligence.py`. Chạm tiền thật ⇒ **user duyệt riêng**. | user duyệt |
| **P4 — Dọn** | Archive cache `ticker_prune` (§6), `data_registry` `ticker_prune` → TRAP, thêm dòng cấm `IN (SELECT DISTINCT …)` vào `coding_guidelines`. | — |

**⚠️ `macro_state_live.py` breadth — không được đưa vào P1 hay P3 mà không A/B.** Breadth = % mã
trên MA200 với mẫu số là universe. Đổi sang `universe_pit` làm **mẫu số lịch sử tăng tới +26%**
(2022: 321 → 405). Đây là input của Pillar-B decoupling guard trong **DT5G production regime**.
Bất kể chiều tác động, đây là thay đổi hành vi mô hình ⇒ **Taylor A/B + quant-skeptic + user duyệt**,
không phải quyết định vận hành của tôi (ranh giới CLAUDE.md: Winston không đổi mô hình).

### 7.4 Rủi ro tồn dư cần nêu thẳng

1. **Ngưỡng 1e9 là hardcode của bq_admin, không phải của ta.** Ta đang sao chép một hằng số nằm ở
   2 vị trí trong code họ, không có versioning (QA §7). Nếu họ đổi, universe của ta **không** đổi
   theo — điều này là **tốt** (ta chủ động), nhưng phải ghi rõ trong `universe_ruleset.md` rằng
   `ruleset_version=1` = "sao chép ngưỡng bq_admin @2026-07-22", chứ không phải "ngưỡng đã hiệu
   chuẩn". Đừng để 6 tháng sau ai đó tưởng con số 1 tỷ đã qua tối ưu hoá.
2. **`Price` là giá CHƯA điều chỉnh** (QA §0). Cột này bị tính lại khi có sự kiện điều chỉnh giá →
   đây chính là 1 trong 2 trigger của đường ghi #3, tức **nguồn trôi lịch sử §3**. Không tránh được
   ở tầng ta; drift detector là câu trả lời.
3. **`ticker` thưa theo ngày**: một phiên chỉ có ~760-840 dòng trên tổng 1.291 mã. **Không có dòng ≠
   đã huỷ niêm yết** (có thể chỉ là không khớp lệnh). Rule B6 của Taylor ("không có dòng 10 phiên
   ⇒ loại ngay") cần tính trên **lịch giao dịch của sàn**, không phải trên sự tồn tại của dòng, nếu
   không sẽ loại nhầm mã thanh khoản kém nhưng còn sống. → chuyển lưu ý này cho Taylor.
4. **Bằng chứng §2 dựa trên 8 mốc**, không phải toàn lịch sử. Chi phí chạy full = 0,001 USD —
   nên chạy trước khi chốt.

---

## 8. Việc tôi KHÔNG làm trong job này

Không tạo bảng, không sửa cron, không sửa `sync_bq_cache.py`, không sửa consumer nào. `data_registry.md`
chỉ ghi 1 dòng **hướng đi tạm** (§9 dưới), **chưa** đổi status `ticker_prune` thành TRAP — chờ Taylor
+ quant-skeptic + user duyệt, đúng yêu cầu dispatch.

---

## 9. Kết luận vận hành gửi Mike

| Câu hỏi dispatch | Trả lời |
|---|---|
| 1. Chi phí BQ thật? | **Không đáng kể, cả về tuyệt đối lẫn tương đối.** Backfill 182,7 MB/2,5 s/0,001 USD. Incremental hằng ngày **rẻ hơn** cách đọc `ticker_prune` hiện tại. Full rebuild mỗi ngày = 0,024 USD/tháng. **Bỏ chi phí ra khỏi bảng cân nhắc.** |
| 2. Cron/cadence? | **Không thêm cron.** Step [0.5] trong `daily_refresh_v34b_linux.sh` (18:30), sau vòng precheck có sẵn. Đọc BQ **live**, không cache. Đo thật: 6/7 phiên ingest xong trước 18:30, 1/7 trễ 1 h ⇒ bắt buộc giữ vòng chờ + depth gate. |
| 3. Cache impact? | Thêm `universe_pit` vào `sync_bq_cache.py`, **delta hợp lệ** (append-only), ~8-40 MB. Không ảnh hưởng cache `ticker`/`ticker_financial`. Sau cutover bỏ được cache `ticker_prune` 415 MB (theo §10 archive, không `rm`). |
| 4. 5 vấn đề của bq_admin? | **3/5 không liên quan** (GCS `v2_prune`, thống nhất 3 đường ghi, "tự xây snapshot" = chính việc này). **2/5 VẪN liên quan** (`is_skip`, `max_bad_records=10` — tác động ở tầng load, chạm cả `ticker`). **Không nói "yên tâm"** — thay vào đó gói hết vào 1 control của ta: drift detector 0,024 USD/tháng. |
| 5. Rủi ro cutover? | **Fail-closed tuyệt đối, không fallback ngầm về `ticker_prune`** (universe lệch 1,6-2,6× ⇒ fallback = giao dịch thật trên universe khác mà không ai biết). Cutover 5 pha, shadow 10 phiên trước. **`macro_state_live.py` breadth phải A/B riêng** (mẫu số lịch sử +26%, chạm regime production). |
| 6. Registry? | Ghi 1 dòng hướng đi tạm, **chưa chốt** — chờ Taylor + quant-skeptic. |

**Phát hiện có giá trị nhất của job này (ngoài phạm vi được hỏi):** `ticker_prune ⊊ universe_pit`
ở mọi mốc lịch sử ⇒ **curation của bq_admin không mang thông tin bổ sung nào**, chỉ trừ đi. Điều này
gỡ bỏ rủi ro lớn nhất mà Taylor tự nêu trong §5 ("thay thế mù có thể làm xấu universe") và làm cho
quyết định "tự xây `universe_pit`" trở nên **rõ ràng hơn nhiều** so với lúc doc gốc được viết.
