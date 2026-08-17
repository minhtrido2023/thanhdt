# Pipeline snapshot TIẾN-TỚI cho `corporate_action` + `insider_transaction`

> Taylor · 2026-08-17 · job `Taylor_20260817_041202` · user duyệt 2026-08-17
> Artifact: `mike/bin/snapshot_corp_action_daily.py` · `mike/bin/snapshot_corp_action_selfcheck.py`
> Selfcheck: **41/41 PASS**. Lần snapshot đầu tiên **ĐÃ CHẠY THẬT** 2026-08-17 (xem §7).

## 1. Vấn đề — và vì sao không có đường nào khác

Cả hai bảng vendor là **snapshot trạng thái, không phải event-log**. Khi một sự kiện lật trạng thái
(`Đăng ký` → `Đã thực hiện xong`, `announced` → `executed`), ETL vendor **ghi đè `public_date` tại
chỗ** trên cùng `id`. Ngày công bố Ý ĐỊNH biến mất vĩnh viễn.

`kb/data_registry/fundamentals/insider_transaction.md` §Bẫy(1) đã xác nhận điều này **ở tầng nguồn**
(bq_admin đọc source ETL 2026-07-29): `publicDate` là field VCI tự maintain, và bước
`_merge_prefer_done` cho dòng Done luôn thắng dòng not-Done khi merge — **kể cả khi lần sync trước
đã bắt được dòng lúc còn `Đăng ký`**. Không có cột nào khác giữ ngày đăng ký gốc.

Hệ quả đã trả giá: **Sprint 1 (`corp_action_program_20260815`) CẤM mọi announcement study** vì thiếu
point-in-time provenance (gate CONDITIONAL PASS). Pipeline này là **tiền đề duy nhất** để mở lại.

### Bằng chứng ghi đè — đo thật, không suy luận (2026-08-17)

Batch ingest gần nhất của vendor (UTC 2026-08-15, ≈ 06:20–06:48 ICT ngày 08-16):

| Bảng | Dòng bị rewrite | Trong đó `public_date` < 2026-08-01 | `public_date` cũ nhất bị chạm |
|---|---:|---:|---|
| `corporate_action` | 1.331 | **1.185 (89%)** | 2024-09-13 |
| `insider_transaction` | 1.332 | **1.154 (87%)** | 2026-05-14 |

⇒ Vendor **sửa dòng LỊCH SỬ mỗi lần chạy**, không chỉ append dòng mới. Đây không phải rủi ro giả
định; nó đang xảy ra hàng tuần.

### Vendor refresh KHÔNG đều — đo thật

`COUNT(*) GROUP BY DATE(ingested_at)` (UTC):

```
corporate_action     : 08-12 → 34.841  | 08-13 → 4      | 08-15 → 1.331
insider_transaction  : 07-27 → 50.942  | 08-01 → 69     | 08-03 → 1    | 08-04 → 6
                       08-08 → 94      | 08-10 → 12     | 08-15 → 1.332
```

Khoảng trống 3–5 ngày là bình thường. ⇒ **"Hash không đổi giữa 2 snapshot_date" KHÔNG có nghĩa
"không có sự kiện thật"** — rất có thể vendor đơn giản không chạy. Mọi phân tích trên bảng snapshot
phải đọc thêm `MAX(ingested_at)` của chính snapshot đó, đừng suy từ lịch.

## 2. Schema 2 bảng snapshot

Nguyên tắc: **schema nguồn nguyên vẹn, thứ tự nguyên vẹn**, + đúng 2 cột meta ở cuối.

| Bảng | Nguồn | Cột | Partition | Cluster |
|---|---|---:|---|---|
| `tav2_mike.corporate_action_snapshots` | `tav2_bq.corporate_action` | 35 + 2 = **37** | `snapshot_date` (DAY) | `ticker`, `id` |
| `tav2_mike.insider_transaction_snapshots` | `tav2_bq.insider_transaction` | 25 + 2 = **27** | `snapshot_date` (DAY) | `ticker`, `id` |

Hai cột meta:

| Cột | Kiểu | Mode | Nghĩa |
|---|---|---|---|
| `snapshot_date` | DATE | REQUIRED | Ngày **ICT** quan sát trạng thái bảng nguồn — KHÔNG phải ngày sự kiện, KHÔNG phải ngày vendor ghi |
| `row_sha256` | STRING | REQUIRED | SHA256 nội dung dòng, hex 64 ký tự |

DDL tương đương (schema thật do script tự dựng từ `client.get_table(src).schema`, không chép tay —
chép tay là cách chắc chắn nhất để lệch):

```sql
CREATE TABLE `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots`
( id STRING, ticker STRING, organ_code STRING, event_code STRING, category STRING,
  event_name_vi STRING, event_title_vi STRING, event_title_en STRING, public_date DATE,
  display_date1 DATE, display_date2 DATE, exright_date DATE, record_date DATE, issue_date DATE,
  payout_date DATE, listing_date DATE, value_per_share FLOAT64, exercise_ratio FLOAT64,
  dividend_year INT64, dividend_stage_vi STRING, issue_method_code STRING,
  issue_method_name_vi STRING, issue_volumn INT64, total_value FLOAT64, issue_status_code STRING,
  issue_status_vi STRING, shares_delta INT64, shares_total_after INT64, ref_price FLOAT64,
  effective_date DATE, event_status STRING, event_description_vi STRING, source_url STRING,
  icb_code_lv1 STRING, ingested_at TIMESTAMP,
  snapshot_date DATE NOT NULL, row_sha256 STRING NOT NULL )
PARTITION BY snapshot_date CLUSTER BY ticker, id;

CREATE TABLE `lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots`
( id STRING, ticker STRING, event_code STRING, event_name STRING, event_title STRING,
  action_type STRING, action_code STRING, trade_status STRING, trade_status_en STRING,
  trader_person_id INT64, trader_name STRING, role_name STRING, relative_name STRING,
  share_register INT64, share_acquire INT64, share_before INT64, share_after INT64,
  ownership_after FLOAT64, public_date DATE, display_date1 DATE, start_date DATE, end_date DATE,
  source_url STRING, icb_code_lv1 STRING, ingested_at TIMESTAMP,
  snapshot_date DATE NOT NULL, row_sha256 STRING NOT NULL )
PARTITION BY snapshot_date CLUSTER BY ticker, id;
```

**KHÔNG đặt partition expiration.** Toàn bộ giá trị của bảng này là tích luỹ dài hạn; một
`partition_expiration_days` đặt nhầm sẽ âm thầm xoá đúng thứ không tái tạo được.

### `row_sha256` — công thức và 2 quyết định thiết kế

```sql
TO_HEX(SHA256(TO_JSON_STRING(STRUCT(<mọi cột nguồn TRỪ ingested_at>))))
```

**(a) Vì sao `TO_JSON_STRING(STRUCT(...))` chứ không phải `CONCAT`.** Null-safe (NULL → `null`,
không lẫn với chuỗi rỗng — selfcheck T4.6 khoá điều này), delimiter-safe (JSON tự escape, khỏi phải
chọn ký tự phân cách "chắc không có trong data"), và mang theo TÊN cột nên hash tự mô tả tập cột nó
phủ.

**(b) Vì sao LOẠI `ingested_at` khỏi hash.** `ingested_at` là dấu vết pipeline, không phải nội dung
sự kiện. Đo thật ở §1: vendor chỉ chạm ~1,3k dòng mỗi lần refresh (không rewrite cả bảng), nên
`ingested_at` CÓ tương quan với thay đổi thật — nhưng nếu vendor rewrite một dòng với nội dung y hệt
thì hash-có-`ingested_at` sẽ báo **amendment giả**, làm hỏng đúng thứ bảng này sinh ra để đo. Cột
`ingested_at` vẫn được **lưu nguyên** trong snapshot ⇒ không mất thông tin nào, chỉ chuyển nó từ
"tín hiệu" thành "metadata". Selfcheck T4.5 khoá quyết định này.

## 3. Script — các tính chất phải giữ khi sửa về sau

`mike/bin/snapshot_corp_action_daily.py`

| Tính chất | Cơ chế | Selfcheck |
|---|---|---|
| **Idempotent trong ngày** | `COUNT(*) WHERE snapshot_date = D` > 0 ⇒ SKIP | T2 (+ live §7) |
| **Không partial-write** | ĐÚNG MỘT câu `INSERT ... SELECT` ⇒ nguyên tử ở tầng BQ. Không có đường ghi từng lô. | — |
| **Fail-closed** | Mọi exception ⇒ log + `exit 1`. Không có nhánh "ghi tạm rồi sửa sau". | T3.4, T6, T7 |
| **Schema drift làm DỪNG pipeline** | So cột nguồn vs cột snapshot mỗi lần chạy; lệch ⇒ RuntimeError | T3.1–3.5 |
| **Chống chụp giữa lúc vendor rebuild** | Nguồn < 90% snapshot gần nhất ⇒ ABORT (`SNAPSHOT_MIN_ROW_RATIO`) | T6 |
| **Verify sau ghi** | Đếm lại partition, khác `src.num_rows` ⇒ RuntimeError | T7 |
| **Timezone ICT tường minh (§16)** | `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` | T5 (4 TZ host, kể cả TZ bị gỡ) |
| **`--dry-run` không chạm gì** | Không tạo bảng, DML gửi dưới `dry_run=True` | T1 |

**Vì sao KHÔNG tự động evolve schema.** Thêm/bớt một cột nguồn làm **đổi tập cột vào hash** ⇒ ở
snapshot kế tiếp *mọi dòng* sẽ trông như vừa bị amend. Đó là hỏng đúng chức năng chính. Nên lệch
schema là quyết định của **người** (thêm cột vào bảng snapshot + ghi vintage đổi hash vào
data_registry), không phải của cron. Cron sẽ đỏ mỗi ngày cho tới khi có người xử lý — đúng ý đồ.

**Cổng row-depth 90% không phải phòng xa.** Tiền lệ thật trong chính dataset này:
`kb/data_registry/config-meta/bq_pin_snapshots.md` — "pin rơi giữa `TRUNCATE...INSERT` sẽ chụp bảng
rỗng"; và `ticker_prune.md` §2026-07-29 — TRUNCATE+rebuild làm 58 mã biến mất khỏi TOÀN BỘ lịch sử.
Một snapshot sai vintage là **vĩnh viễn** (không sửa lại được bằng cách chạy lại hôm sau), nên cổng
này phải fail-closed chứ không phải cảnh báo.

## 4. Rủi ro dataset — vì sao `tav2_mike` chứ không phải `tav2_bq`

**Đây là điểm tôi đi lệch so với mô tả ban đầu của dispatch, và là việc cần Mike/user xác nhận.**

Dispatch phác thảo `tav2_bq.corporate_action_snapshots`. Tôi mặc định ghi vào **`tav2_mike`**:

- `tav2_bq` là dataset của **bq_admin**, và đã có **tiền lệ thật** WRITE_TRUNCATE + rebuild xoá lịch
  sử (`ticker_prune` 2026-07-29: 58 mã biến mất khỏi toàn bộ lịch sử; `ticker` bị TRUNCATE+rebuild
  gần như mỗi ngày theo `value_radar_series.md`).
- `tav2_mike` được dựng **chính xác để nằm ngoài tầm TRUNCATE đó** — xem mô tả dataset trong
  `build_universe_pit.py`: *"Mike-owned tables. KHONG nam trong tam TRUNCATE cua bq_admin"*.
- Bảng này **không tái tạo được**. Mất một lần = mất toàn bộ tích luỹ, không có đường backfill. Đây
  là tài sản có tính chất khác hẳn mọi bảng dẫn xuất khác của fleet.

Đổi lại một biến môi trường nếu Mike/user muốn: `SNAPSHOT_DATASET=tav2_bq`. Chi phí đổi lúc này gần
như bằng 0 (bảng mới có 1 vintage) — nhưng sẽ tăng dần theo mỗi ngày tích luỹ, nên nếu muốn đổi thì
nên quyết sớm.

## 5. Chi phí — ước tính, đơn giá chưa đối chiếu billing console

Đơn giá dùng: quét $6,25/TB · storage logical active $0,02/GB/tháng (long-term $0,01 sau 90 ngày).
Ghi rõ là **ước tính bậc độ lớn**, không phải hoá đơn.

| Khoản | corporate_action | insider_transaction | Tổng |
|---|---:|---:|---:|
| Kích thước 1 snapshot (logical) | 14,6 MB | 19,5 MB | 34,1 MB/ngày |
| Quét mỗi lần chạy | 14,6 MB ≈ $0,00009 | 19,5 MB ≈ $0,00012 | ≈ **$0,0002/ngày** = $0,08/năm |
| Tích luỹ storage | 5,33 GB/năm | 7,13 GB/năm | **12,5 GB/năm** (18,7 GB ở 18 tháng) |
| Storage năm đầu | ~$0,64 | ~$0,86 | **~$1,5/năm** |

Physical bytes nén tốt hơn ~2× (CA: 7,76 MB physical vs 14,6 MB logical) ⇒ nếu dataset dùng
physical storage billing thì rẻ hơn nữa. **Tổng chi phí thực tế dưới $2/năm** — không phải yếu tố
cần tối ưu.

**Query khi build amendment report**: quét 12 tháng cả 2 bảng = 12,5 GB ≈ **$0,08/lần**. Lọc
`snapshot_date` (partition pruning) hoặc `ticker` (cluster) làm rẻ hơn nhiều. Chi phí không phải lý
do để né chạy report này thường xuyên.

**Đã cân nhắc và BỎ: lưu delta (chỉ dòng có hash đổi).** Giảm ~99% storage nhưng đổi lấy: mọi câu
hỏi "bảng trông như thế nào ngày D" phải qua window function thay vì một `WHERE snapshot_date = D`.
Ở mức $1,5/năm, sự đơn giản đó đáng giá hơn nhiều lần khoản tiết kiệm. Không có lý do định lượng
nào để đổi sang delta trước khi bảng vượt ~vài trăm GB, tức là > 20 năm nữa.

## 6. Truy vấn tiêu chuẩn — dò amendment

```sql
-- Mọi lần một dòng bị vendor sửa nội dung, kèm ngày công bố TRƯỚC và SAU khi sửa.
WITH v AS (
  SELECT id, ticker, snapshot_date, row_sha256, public_date, trade_status, share_acquire,
         LAG(row_sha256)   OVER w AS prev_sha,
         LAG(public_date)  OVER w AS prev_public_date,
         LAG(trade_status) OVER w AS prev_status,
         LAG(snapshot_date) OVER w AS prev_snapshot_date
  FROM `lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots`
  WINDOW w AS (PARTITION BY id ORDER BY snapshot_date)
)
SELECT * FROM v
WHERE prev_sha IS NOT NULL AND row_sha256 != prev_sha
ORDER BY snapshot_date DESC, ticker;
```

Ba biến thể hay dùng:

```sql
-- (a) Dòng MỚI xuất hiện lần đầu ở ngày D  (= sự kiện vendor mới công bố)
SELECT * FROM snap s WHERE s.snapshot_date = D
  AND NOT EXISTS (SELECT 1 FROM snap p WHERE p.id = s.id AND p.snapshot_date < D);

-- (b) Dòng BIẾN MẤT sau ngày D  (vendor xoá — bảng snapshot bắt được, bảng nguồn thì không)
SELECT * FROM snap s WHERE s.snapshot_date = D
  AND NOT EXISTS (SELECT 1 FROM snap n WHERE n.id = s.id AND n.snapshot_date > D);

-- (c) NGÀY CÔNG BỐ Ý ĐỊNH THẬT — thứ Sprint 1 thiếu.
--     = snapshot_date SỚM NHẤT ta thấy dòng đó khi nó còn ở trạng thái đăng ký.
SELECT id, ticker, MIN(snapshot_date) AS first_seen_registered
FROM `...insider_transaction_snapshots`
WHERE trade_status = 'Đăng ký' GROUP BY 1, 2;
```

⚠️ (c) cho **cận trên** của ngày công bố thật (ta thấy nó ngày ta chụp, không phải ngày vendor
đăng), độ phân giải 1 ngày. Với sự kiện mà `first_seen_registered` = ngày snapshot ĐẦU TIÊN của
bảng (2026-08-17) thì nó là **censored bên trái** — sự kiện đã đăng ký từ trước, không dùng được cho
event study. Phải lọc bỏ nhóm này, nếu không sẽ trộn 2.233 sự kiện tồn đọng vào mẫu.

## 7. Trạng thái thật — đã chạy, không phải kế hoạch

Lần snapshot đầu tiên chạy tay **2026-08-17** (không qua cron, cron chưa cài):

```
corporate_action    -> tav2_mike.corporate_action_snapshots     36.176 dòng  job efcaf3a7-…
insider_transaction -> tav2_mike.insider_transaction_snapshots  52.456 dòng  job 926fecf9-…
verify: partition 2026-08-17 = đúng số dòng nguồn, cả 2 bảng
```

Đối soát sau ghi (query độc lập, không đọc self-report của script):

| Bảng | dòng | `COUNT(DISTINCT row_sha256)` | `row_sha256 IS NULL` | `COUNT(DISTINCT id)` |
|---|---:|---:|---:|---:|
| `corporate_action_snapshots` | 36.176 | **36.176** | 0 | 36.176 |
| `insider_transaction_snapshots` | 52.456 | **52.456** | 0 | 52.456 |

Hash phân biệt hoàn toàn (không va chạm), không NULL. Chạy lại ngay sau đó ⇒ **SKIP** cả 2 bảng,
0 byte quét ⇒ idempotency được xác nhận **trên BQ thật**, không chỉ trên mock.

**Vintage đầu tiên đã bắt được 2.233 sự kiện đang treo** — đây là giá trị tức thời, không phải
tương lai:

| Bảng | Trạng thái treo | n | % |
|---|---|---:|---:|
| `insider_transaction` | `Đăng ký` | **1.364** | 2,6% |
| `corporate_action` | `announced` | **869** | 2,4% |

Mỗi dòng trong 2.233 dòng này, khi nó lật sang `Đã thực hiện xong`/`executed`, sẽ cho một cặp
(vintage đăng ký, vintage kết quả) — thứ mà **trước hôm nay không thể lấy lại được ở bất kỳ giá
nào**. Trước lần chạy này, mỗi ngày trôi qua là mất vĩnh viễn phần này.

## 8. Hạn chế đã biết — đọc trước khi dùng cho nghiên cứu

1. **KHÔNG backfill được.** Lịch sử trước 2026-08-17 đã mất ở tầng nguồn. Không có nguồn thay thế
   trong tầm với của fleet.
2. **Độ phân giải 1 ngày.** Vendor sửa rồi sửa lại trong cùng một ngày ICT ⇒ ta chỉ thấy trạng thái
   cuối ngày. Không có cách nào bắt sub-day mà không polling liên tục (không đáng).
3. **`snapshot_date` là ngày QUAN SÁT, không phải ngày vendor ghi.** Vendor ghi lúc ~06:20 ICT thì
   ta thấy ở snapshot 23:50 cùng ngày; vendor không chạy 4 ngày thì 4 snapshot giống hệt nhau. Đọc
   `MAX(ingested_at)` trong chính snapshot để phân biệt "không có sự kiện" vs "vendor không chạy".
4. **Censoring bên trái.** Sự kiện đã treo từ trước 2026-08-17 không có vintage đăng ký thật — phải
   loại khỏi mẫu event study (xem §6c).
5. **Runway tới lúc mở lại announcement study.** Tốc độ tích luỹ ≈ tốc độ sự kiện mới:
   `insider_transaction` ~52.456 dòng / ~11,6 năm ≈ **4.500 sự kiện/năm**;
   `corporate_action` ~36.176 / 26 năm ≈ 1.400/năm (phủ không đều theo năm, con số này là bậc độ
   lớn). ⇒ 12 tháng cho ~4,5k cặp đăng-ký→kết-quả có ngày công bố THẬT cho insider — đủ N cho một
   event study nghiêm túc; 18 tháng cho ~6,7k. Con số này khớp với ước lượng 12–18 tháng đã nêu
   trong dispatch, nhưng **phải đo lại bằng dữ liệu thật lúc review**, không dùng lại con số này.
6. **`id` là khoá join xuyên vintage.** Nếu vendor đổi/tái sử dụng `id`, mọi truy vấn §6 hỏng âm
   thầm. Chưa quan sát thấy (36.176/36.176 và 52.456/52.456 distinct), nhưng nên kiểm định kỳ.
7. **Không có gate freshness của nguồn trong script.** Script snapshot cái nó thấy, kể cả khi nguồn
   đã cũ — đó là **đúng ý đồ** (một vintage "nguồn đứng yên" cũng là dữ kiện thật). Gate freshness
   là việc của consumer, xem `corp_action_lib.feed_freshness()`.

## 9. Cron ĐỀ XUẤT — **CHƯA CÀI**, cần Mike/user duyệt (§11 coding_guidelines)

```cron
# Snapshot tien-toi corporate_action + insider_transaction (provenance point-in-time).
# KHONG tu cai — cho user/Mike duyet. Chu: Taylor. Doc: agents/Taylor/research/corp_action_snapshot_pipeline_design_20260817.md
50 23 * * * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && python3 mike/bin/snapshot_corp_action_daily.py >> logs/snapshot_corp_action_$(date +\%Y\%m).log 2>&1
```

**23:50 ICT, chạy CẢ 7 NGÀY/TUẦN.** Lý do từng phần:

- **Sau 23:45** — `sync_bq_cache_daily.sh` chạy 23:45; không tranh chấp, và không có ràng buộc phụ
  thuộc thật giữa hai việc (script này đọc thẳng BQ, đã `pop BQ_LOCAL_CACHE`).
- **Cuối ngày ICT** — bắt trọn mọi thứ vendor ghi trong ngày lịch đó. Cửa sổ ingest quan sát được
  rất tản mát (22:22 ICT ở batch đầu; 06:20–06:48 ICT ở batch 08-16), nên không có "giờ an toàn"
  nào tốt hơn ngoài "muộn nhất có thể trong ngày".
- **7 ngày/tuần, không phải T2-T6** — công bố corp-action/nội bộ và các lần vendor sửa dữ liệu không
  tôn trọng lịch phiên; và một chuỗi vintage liên tục dễ phân tích hơn chuỗi có lỗ cuối tuần.
- **Chạy quá nửa đêm vẫn đúng nhãn**: `snapshot_date` được chốt lúc BẮT ĐẦU chạy, nên một lần chạy
  23:50 → 00:02 vẫn ghi nhãn ngày cũ. Không có ca biên nào ở đây.
- Lỡ một ngày **không hỏng gì** (chỉ mất vintage ngày đó); chạy lại trong ngày là no-op nhờ cổng
  idempotent. Không cần catch-up logic.

Chưa wire vào `ops_health_check.sh` / autofix. Đề xuất để **sau 1-2 tuần chạy thật**, rồi thêm một
check freshness đơn giản (`MAX(snapshot_date)` phải là hôm nay hoặc hôm qua) — đặt gate trước khi có
dữ liệu vận hành thật là đoán mò.

## 10. Việc còn treo

| # | Việc | Chủ | Ghi chú |
|---|---|---|---|
| 1 | Duyệt cron §9 + xác nhận lựa chọn dataset §4 | Mike/user | Cron chưa cài; dataset đổi bây giờ gần như miễn phí |
| 2 | quant-skeptic review | Mike trigger | Không chạm production trading code, nhưng là tiền đề cho một hướng nghiên cứu |
| 3 | Kiểm lại `id` còn unique xuyên vintage | Taylor | Sau ~1 tháng, cùng lúc với check đầu tiên có amendment thật |
| 4 | Đo tỉ lệ amendment thật từ 2 vintage | Taylor | ~2026-09-12 (đã ghi trong working memory từ Sprint 1/2) |
| 5 | Quyết định mở lại announcement study | Taylor + user | **Không sớm hơn 2027-08**; phải đo lại N thật, không dùng ước lượng §8.5 |
