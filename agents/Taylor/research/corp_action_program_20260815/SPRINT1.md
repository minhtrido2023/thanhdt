# Sprint 1 — research-grade event ledger + data-quality audit của `tav2_bq.corporate_action`

**Job** `Taylor_20260815_114954` · **Ngày đo** 2026-08-15 · **Tác giả** Taylor (quant)
**Phạm vi** READ-ONLY BigQuery. Không tạo bảng/view, không đụng production/cron/trading rule.
Mọi artifact nằm trong đúng thư mục này.

> ## GATE VERDICT: **CONDITIONAL PASS** → được sang Sprint 2 (cash dividend)
>
> | Loại nghiên cứu | Phán quyết | Vì sao |
> |---|---|---|
> | **Ex-date mechanical study** (phản ứng giá quanh ngày GDKHQ) | ✅ **ĐƯỢC PHÉP** | ex-date + `value_per_share` khớp chuỗi giá: 96,9% có bước điều chỉnh đúng ngày, 85,5% khớp ĐỘ LỚN trong ±0,2% |
> | **Post-event abnormal return** (drift sau ex-date) | ✅ **ĐƯỢC PHÉP**, kèm loại trừ cửa sổ nhiễm | mốc thời gian neo vào ex-date, không cần biết ngày công bố |
> | **Announcement study** (phản ứng quanh ngày công bố) | ❌ **CẤM** | `public_date` KHÔNG chứng minh được là ngày biết tin: 4,85% DIV / 39,1% ISS có `public_date ≥ exright_date`, và bảng bị **ghi đè tại chỗ** nên không có bản vintage để chứng minh giá trị chưa từng bị sửa |
> | **Bất kỳ study nào dùng `ticker.Price` của ĐÚNG DÒNG ex-date** | ❌ **CẤM** | bẫy đã biết (registry `ticker_price_stale_on_exdate.md`), sai tới +98,4% ở VHM 2026-08-06 |
>
> **Không còn blocker nào tạo alpha giả cho ex-date study.** Blocker duy nhất còn lại
> (`public_date` + thiếu vintage) chỉ chặn announcement study, và đã được cô lập bằng cờ
> `known_date_confidence` trong ledger — không thể vô tình lọt vào mẫu.

---

## 1. Phương pháp

Tất cả số dưới đây tái lập được bằng 3 lệnh (thứ tự bắt buộc — selfcheck đọc ledger):

```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd <thư mục này>
python3 profile_corp_action.py     # 20 truy vấn → out/*.csv + out/sql/*.sql
python3 build_event_ledger.py      # ledger + summary + sample + vintage snapshot
python3 selfcheck_sprint1.py       # 21 invariant
```

Nguyên tắc kỷ luật đã áp dụng: **không trích lại số của registry cũ nếu query live khác** —
mọi con số ở đây đo lại từ đầu ngày 2026-08-15 (registry ghi 36.149 dòng ngày 08-13; hôm nay là
**36.170**, xem §2).

---

## 2. Bảng hiện tại — và một phát hiện làm đổi cách hiểu về nguồn

| Chỉ tiêu | Giá trị (đo 2026-08-15) |
|---|---|
| Số dòng / `id` distinct | **36.170 / 36.170** (`id` là khoá thật) |
| Số mã | 1.792 |
| `public_date` | 2000-03-31 → 2026-08-13 |
| `exright_date` | 2000-03-31 → **2026-09-24** (có sự kiện TƯƠNG LAI đã công bố) |
| `ingested_at` | 2026-08-12 15:22 → **2026-08-14 15:49** UTC |

### 2.1 Bảng được GHI ĐÈ TẠI CHỖ, không phải append-only — hệ quả nặng cho point-in-time

| ngày ingest | số dòng ghi | trong đó `public_date` cũ hơn 30 ngày |
|---|---:|---:|
| 2026-08-12 | 35.541 | 35.387 |
| 2026-08-13 | 7 | 4 |
| 2026-08-14 | **622** | **462** |

Registry đo 36.149 dòng ngày 08-13; hôm nay 36.170 — **tăng ròng 21 dòng** trong khi batch 08-14
ghi **622 dòng**. ⇒ ít nhất ~600 dòng là **ghi đè lên `id` đã tồn tại**, không phải sự kiện mới.
462 trong số đó mang `public_date` cũ hơn 30 ngày, tức là sự kiện cũ được vendor **viết lại**.

**Hệ quả:** `ingested_at` là dấu thời gian LẦN GHI CUỐI, không phải lần đầu thấy. Không có
bản vintage ⇒ **không thể chứng minh** `public_date`/`value_per_share` của một dòng chưa từng bị
sửa. Đây là lý do kỹ thuật khiến announcement study bị CẤM ở §5, và cũng là lý do Sprint 1 tạo
`out/vintage_asof_20260814.csv.gz` (§8).

### 2.2 `id` giải mã được thành thời điểm vendor TẠO bản ghi

`id` là ObjectId 24-hex; 4 byte đầu là unix timestamp. Giải mã cho thấy **32.322/36.170 (89,4%)**
bản ghi được tạo cùng ngày **2024-10-11** = một đợt backfill lịch sử của vendor; phần còn lại rải
theo thời gian. Đây là mốc thời gian **thứ hai, độc lập** với `public_date` — ledger giữ nó ở cột
`id_created_date`. ⚠️ Nó là "vendor tạo bản ghi", KHÔNG phải "thị trường biết tin", và với 89,4%
dòng nó chỉ là ngày backfill ⇒ **không dùng làm known_date**, chỉ dùng để tie-break và để phát
hiện batch.

---

## 3. Coverage & missingness (`out/coverage_*.csv`, `out/missingness.csv`)

| `event_code` | n | executed | announced | not_executed |
|---|---:|---:|---:|---:|
| DIV | 17.070 | 16.947 | 123 | 0 |
| ISS | 11.722 | 9.300 | 639 | **1.783** |
| AIS | 4.881 | 4.786 | 95 | 0 |
| NLIS | 1.368 | 1.366 | 2 | 0 |
| SUSP | 681 | 677 | 4 | 0 |
| MOVE | 431 | 430 | 1 | 0 |
| MA | 17 | 17 | 0 | 0 |

Missingness ở các trường quyết định (%, NULL):

| | `exright_date` | `record_date` | `payout_date` | `value_per_share` | `exercise_ratio` |
|---|---:|---:|---:|---:|---:|
| **DIV** | **0,50** | 0,45 | 0,46 | **0,00** | 0,00 |
| **ISS** | 16,85 | 16,74 | 100 | 100 | 0,41 |

**DIV gần như hoàn hảo ở đúng 2 trường mà nghiên cứu cash dividend cần** (`exright_date` thiếu
0,50%, `value_per_share` thiếu 0%).

### 3.1 `exercise_ratio` — bẫy "0 không phải NULL", và vì sao nó KHÔNG cản Sprint 2

42,3% dòng ISS có `exercise_ratio` NULL **hoặc bằng 0**. Nhưng phân bố không ngẫu nhiên:

| method | n | ratio > 0 | ratio null/0 |
|---|---:|---:|---:|
| `DIV` (cổ tức CP) | 2.651 | **2.627** | 24 |
| `Bonus` | 1.534 | **1.504** | 30 |
| `Rights` | 2.190 | **2.096** | 94 |
| `PP` (riêng lẻ) | 3.096 | 293 | **2.803** |
| `EMPL` (ESOP) | 1.691 | 217 | **1.474** |
| `TRANS`/`PUBL`/`MERGER`/`ICRE`/`BBOD` | 560 | 24 | 536 |

Tỉ lệ thiếu **tập trung đúng vào nhóm KHÔNG phát sinh quyền cho cổ đông hiện hữu** — nhóm mà
ratio không cần cho câu hỏi điều chỉnh giá. Ba nhóm điều chỉnh giá (stock dividend / bonus /
rights) có ratio dương ở **96,9%** số dòng. ⇒ **lành tính cho Sprint 2**, vẫn **chí mạng** cho
mô hình số cổ phiếu lưu hành (đúng như `fundamentals/ticker_financial_oshares.md` đã ghi).

### 3.2 Hai lỗ hổng coverage phải nói thẳng

1. **KHÔNG có cột sàn (HOSE/HNX/UPCOM) trong bảng này.** Dispatch yêu cầu coverage "theo sàn" —
   không làm được từ nguồn này. `icb_code_lv1` là mã NGÀNH, không phải sàn. Thay bằng coverage
   theo ngành (`out/coverage_icb.csv`) + theo universe đầu tư (§6). Muốn cắt theo sàn thật thì
   phải nối nguồn khác — ghi vào ISSUES_LEDGER.md.
2. **`ref_price` = 100% NULL trên DIV và ISS.** Nó chỉ có giá trị ở NLIS (81% có)/MOVE (87% có),
   tức là giá tham chiếu ngày niêm yết/chuyển sàn. **Không dùng được** làm giá tham chiếu ex-right.

---

## 4. Taxonomy ISS — quy tắc auditable (`ca_lib.classify`)

Khoá phân loại chính là **`issue_method_code`** (enum vendor, không phụ thuộc ngôn ngữ), fallback
`issue_method_name_vi`. **Tiêu đề KHÔNG BAO GIỜ được dùng để gán nhãn.**

| `issue_method_code` | subtype | n | điều chỉnh giá tại ex-date? |
|---|---|---:|---|
| `DIV` | `STOCK_DIVIDEND` | 2.651 | ✅ |
| `Bonus` | `BONUS` | 1.534 | ✅ |
| `Rights` | `RIGHTS` | 2.190 | ✅ |
| `EMPL` | `ESOP` | 1.691 | ❌ |
| `PP` | `PRIVATE_PLACEMENT` | 3.096 | ❌ |
| `TRANS`+`ICRE` | `CONVERTIBLE` | 256 | ❌ |
| `PUBL` | `AUCTION` | 176 | ❌ |
| `MERGER` | `MERGER` | 113 | ❌ |
| `BBOD` | **`UNKNOWN`** | **15** | ❌ (fail-safe) |

**`UNKNOWN` = 15 sự kiện = 0,042% ledger.** Đây là kết luận có bằng chứng, không phải bỏ sót:
15 dòng `BBOD` có `issue_method_name_vi`, `event_title_vi`, `event_description_vi` **đều NULL** và
`exercise_ratio = 0` — không có trường nào trong bảng nói nó là gì. Chúng bị chặn khỏi mẫu
actionable (selfcheck T7c).

### 4.1 Kiểm chứng chéo — và một cái bẫy tự kiểm chứng phải nói ra

Ý định ban đầu: đối chiếu nhãn theo field với nhãn suy từ `event_title_vi`. Kết quả **0 xung đột**
— nhưng con số đó **VÔ NGHĨA**: tiêu đề được vendor ghép máy móc từ chính field đó
(`"Phát hành cổ phiếu - " + issue_method_name_vi [+ " tỉ lệ x%"]`). Một "confusion matrix" trên
đó chỉ đang so một trường với chính nó.

Thay bằng phép kiểm chứng **thật sự độc lập**: tỉ lệ nhúng trong CHỮ của tiêu đề so với cột SỐ
`exercise_ratio` → **6.669 sự kiện kiểm được, 6.669 khớp, 0 lệch (100,0%)** trong dung sai ±0,05pp
(= đúng độ chính xác tiêu đề in ra, 1 chữ số thập phân của %). Đây là bằng chứng dương cho
`exercise_ratio`, không phải cho nhãn subtype.

*Ghi nhận sai sót trong quá trình đo:* lần chạy đầu dùng dung sai chính xác tuyệt đối và báo 1.132
"lệch" (17%). Kiểm tay 12 ca → toàn bộ là làm tròn của chính tiêu đề (7,15% → in "7.2%"). Dung sai
đã sửa; con số 17% **không phải** kết luận và không được trích.

---

## 5. Point-in-time audit — timestamp nào dùng được vào việc gì

| Timestamp | Dùng được cho | KHÔNG được dùng cho |
|---|---|---|
| `exright_date` | **neo mọi ex-date/post-event study** | — |
| `record_date`, `payout_date` | mô tả, đối soát tiền về | neo sự kiện (sau ex-date) |
| `effective_date` (AIS) | ngày CP mới vào lưu hành | thay `exright_date` (lệch tới ~7 tuần) |
| `public_date` | **descriptive only** | **announcement study — CẤM** |
| `id_created_date` | tie-break, phát hiện batch | known_date (89,4% là ngày backfill) |
| `ingested_at` | freshness check | known_date (là lần ghi CUỐI) |

### 5.1 Vì sao `public_date` KHÔNG được mặc định là ngày biết tin — 2 bằng chứng độc lập

**(a) Nó không đứng trước sự kiện ở tỉ lệ không thể bỏ qua:**

| | n có ex-date | `public > ex` | `public = ex` | **% KHÔNG đứng trước** | lead p50 |
|---|---:|---:|---:|---:|---:|
| DIV | 16.984 | 49 | 775 | **4,85%** | 8 ngày |
| ISS | 9.747 | 649 | 3.162 | **39,10%** | 6 ngày |

Với ISS, `public_date` rõ ràng thường chỉ là **ngày chốt quyền chép lại**, không phải ngày công bố.
Với DIV nó *trông* hợp lý (p50 = 8 ngày trước, p05 = 1 ngày) nhưng vẫn hỏng ở 4,85%.
Phân rã theo năm (`out/pit_public_vs_exright_by_year.csv`) cho thấy **không phải tật của thời kỳ
đầu** — vẫn còn ở các năm gần đây, nên không thể "cắt mẫu từ 2014 là sạch".

**(b) Kể cả 95,15% còn lại cũng KHÔNG chứng minh được**, vì §2.1: bảng bị ghi đè tại chỗ, không có
lịch sử vintage. Một `public_date` "đẹp" hôm nay có thể đã được sửa sau khi sự kiện xảy ra và ta
không có cách nào biết. ⇒ **hạng cao nhất mà ledger cấp cho bất kỳ dòng nào là `WEAK_UNVERIFIED_VINTAGE`**
(30.830 sự kiện), phần còn lại `UNUSABLE_NOT_BEFORE_EVENT` (4.635). Không có hạng "STRONG" —
cố ý, và selfcheck T5c chặn ai đó thêm vào.

### 5.2 `fleet_known_from` — mốc trung thực của chính đội

Cột hằng trong ledger: **2026-08-12** = ngày đầu tiên fleet có BẤT KỲ dòng nào của bảng này
(assert bằng BQ ở selfcheck T8). Không backtest nào của đội được phép tuyên bố biết một corporate
action trước ngày đó, bất kể `public_date` nói gì. Đây là ranh giới giữa "nghiên cứu lịch sử" và
"tín hiệu chạy được".

### 5.3 Đo rủi ro amendment/revision — hiện CHƯA đo được, đã dựng hạ tầng để đo

Không thể đo tỉ lệ sửa đổi từ một snapshot duy nhất. Bằng chứng gián tiếp duy nhất có được là
§2.1 (≥600 dòng ghi đè trong 1 batch). Sprint 1 vì thế ghi
`out/vintage_asof_20260814.csv.gz` = `id → sha1(14 trường có thể đổi)`. Chạy lại
`build_event_ledger.py` sau N tuần rồi so 2 file vintage sẽ cho **tỉ lệ amendment thật, đo được**.
Đây là điều kiện cần để bao giờ đó mở lại announcement study.

---

## 6. Alignment với giá và với universe

### 6.1 Bước điều chỉnh giá tại ex-date (`out/div_price_step_alignment.csv`)

Đo trên **11.977 sự kiện DIV "sạch"** (executed, có value, KHÔNG có ISS nào trong ±3 ngày, từ
2014). `r = Price/Close` là hệ số điều chỉnh đang chạy; so `r` phiên **T−1** với phiên **T+1** —
**cố tình bỏ qua dòng ĐÚNG NGÀY ex-date** vì `ticker.Price` của dòng đó là bẫy đã biết.

| | n | % trên đo được |
|---|---:|---:|
| Đo được (có giá cả 2 phía) | **8.819** | 100% |
| Hệ số **có bước giảm** đúng ngày | **8.546** | **96,9%** |
| Khớp **ĐỘ LỚN** trong ±0,2% | **7.532** | **85,4%** |
| Khớp độ lớn trong ±1% | 8.171 | 92,7% |
| **Không có bước nào** (giá không điều chỉnh) | 182 | 2,1% |

Sai số tuyệt đối hệ số: p50 = 0,00022 · p90 = 0,0046. Phần lệch còn lại chia đều hai chiều
(592 undershoot / 518 overshoot) — chữ ký của việc sở giao dịch làm tròn giá tham chiếu theo bước
giá, không phải của dữ liệu sai hệ thống. 13 ca ngoại lai có `Price` cum < 1.000đ (giá thô vô lý).

> ⚠️ **Sai sót của chính lần đo này, ghi lại vì nó là bài học chứ không phải kết quả:** phiên bản
> đầu so cổ tức (VND thô) với `Close` (đã hồi tố) và ra 6,6% khớp — đúng cái lỗi "trộn Price thô
> với Close hồi tố" mà dispatch cấm. Sửa sang `Price` thô → 85,4%. **Con số 6,6% là lỗi đo, không
> phải kết quả, không được trích.**

### 6.2 Sanity giá trị cổ tức (`out/div_value_sanity.csv`)

Trên 16.522 cặp (mã, ex-date) executed: **0** giá trị ≤ 0 · **15 (0,09%)** có cổ tức > giá cum ·
24 có cổ tức > ½ giá cum · **p50 gross yield 4,40% · p99 18,13%** — phân bố kinh tế hợp lý.
4.102 (24,8%) không có giá cum trong 15 ngày trước = mã không có chuỗi giá trong `ticker`.

### 6.3 Coverage giá & universe (`out/div_coverage_investable.csv`)

| lát cắt (DIV executed, ex-date 2014→) | n |
|---|---:|
| Tổng sự kiện | 12.583 |
| Có giá trong `ticker` đúng ngày ex | 9.400 (74,7%) |
| **Nằm trong `universe_pit` (point-in-time) tại ex-date** | **3.032 (24,1%)** |
| Nằm trong `ticker_prune` tại ex-date | 2.259 (18,0%) |

**Con số quyết định cho Sprint 2 là 3.032, không phải 17.059.** Phần lớn corporate action rơi vào
mã ngoài universe đầu tư (thanh khoản mỏng, không có chuỗi giá dùng được). ~230 sự kiện/năm trên
universe PIT là N thật — đủ cho một cross-sectional study, KHÔNG đủ để cắt lát mỏng theo
ngành × regime × năm.

### 6.4 Nhiễm cửa sổ sự kiện (`out/div_window_contamination.csv`)

Trên 16.522 sự kiện DIV executed: **895 (5,4%)** có một ISS executed **cùng ngày ex** ·
932 (5,6%) trong ±5 ngày · **1.150 (7,0%)** trong ±21 ngày. Cửa sổ ±21 ngày là mức mà một
post-event drift study điển hình dùng ⇒ phải loại/ghi cờ ~7% mẫu. Ledger đã có cờ
`flag_same_exdate_other_family` cho lát cùng ngày.

---

## 7. Event ledger (`build_event_ledger.py`)

**36.170 dòng thô → 35.465 sự kiện kinh tế** (gộp 705 dòng, 521 sự kiện có >1 dòng nguồn).
Từ điển cột đầy đủ: **`DATA_DICTIONARY.md`**.

### 7.1 Chính sách dedup — quyết định quan trọng nhất của sprint

Khoá ngây thơ `(ticker, exright_date, event_code)` **PHÁ HỎNG dữ liệu thật**: nó gộp 404 nhóm
DIV / 829 dòng, nhưng kiểm tay cho thấy phần lớn là **các ĐỢT cổ tức khác nhau cùng đi ex một
ngày** — PHN ngày 2026-06-05 đi ex CẢ "2025 Đợt 3" (1.000đ) VÀ "2026 Đợt 1" (1.000đ): **cùng giá
trị, khác quyền hưởng, cả hai đều trả thật**. Gộp theo mã+ngày sẽ **âm thầm chia đôi** cổ tức PHN.

Khoá kinh tế đã chọn:

| họ | khoá |
|---|---|
| DIV | `(ticker, exright_date, dividend_year, dividend_stage_vi)` |
| ISS | `(ticker, exright_date, issue_method_code, exercise_ratio, issue_volumn)` |
| còn lại | `(event_code, ticker, effective_date∥public_date, shares_delta, shares_total_after)` |

Kết quả đo: DIV còn **6 nhóm trùng dư / 13 dòng (0,08%)**; ISS còn 22 nhóm / 45 dòng.
Người sống sót = `public_date` mới nhất → `id_created_date` mới nhất → `id` (hoàn toàn tất định,
selfcheck T9 kiểm bằng đảo thứ tự đầu vào).

**Không dòng nào bị mất:** `src_ids` giữ mọi `id` gốc, `dropped_ids` ghi id bị loại; selfcheck
T3b/T3c chứng minh 36.170 id xuất hiện đúng một lần trên toàn ledger.

**Trả lời đúng "không SUM mù":** cột `div_total_on_exdate` = tổng cổ tức thật đi ex ngày đó =
SUM **sau khi** đã dedup theo đợt. SUM dòng thô sẽ nhân đôi 6 nhóm trùng dư; dedup theo mã+ngày
sẽ đánh mất đợt thứ hai. Chỉ thứ tự "dedup theo đợt → rồi mới cộng" là đúng.

### 7.2 Mẫu actionable cho Sprint 2

`actionable = executed ∧ có ex-date ∧ (DIV: value > 0 | ISS: subtype ≠ UNKNOWN)`

| | n |
|---|---:|
| Sự kiện cash dividend trong ledger | 17.059 |
| — executed | 16.940 |
| — announced-only (chưa xảy ra) | 119 |
| — **actionable** | **16.940** |
| — thiếu ex-date | 82 |
| — trùng ngày ex với ISS | 921 |
| — `public_date` không dùng được cho PIT | 823 |
| Cặp (mã, ex-date) distinct | 16.559 |

`not_executed` (1.419 sự kiện, toàn bộ là ISS) **được giữ nguyên lineage** nhưng bị loại khỏi
actionable (selfcheck T4a/T4b).

---

## 8. Selfcheck — **21/21 PASS** (`selfcheck_sprint1.py`)

| nhóm | test |
|---|---|
| Taxonomy | T1 khớp tuyệt đối `corp_action_lib.is_price_adjusting` production trên 28.792 dòng · T2a/T2b mọi nhãn có evidence, `UNKNOWN` chỉ sinh từ nhánh `unmatched` |
| Dedup | T3a–T3e không id nào ở 2 sự kiện · lineage phủ đúng 36.170 dòng một lần · uid unique · survivor luôn nằm trong src_ids |
| No-cancelled | T4a không `not_executed` nào actionable · T4b vẫn giữ 1.419 dòng lineage · T4c announced-only không actionable |
| No-look-ahead | T5a lead ≤ 0 luôn bị hạ UNUSABLE · T5b thiếu public_date luôn UNUSABLE · **T5c không tồn tại hạng nào mạnh hơn WEAK** |
| Giá trị | T6a `div_total_on_exdate` tính lại độc lập khớp · T6b tổng ≥ mọi đợt thành phần · T7a/T7b/T7c actionable luôn có value > 0, có ex-date, không UNKNOWN |
| Horizon | T8 `fleet_known_from` == MIN(ingest) thật trên BQ (fail loud nếu vendor backfill sớm hơn) |
| Tất định | T9 chọn survivor bất biến khi đảo thứ tự đầu vào (3.994 nhóm) |

Theo `coding_guidelines` §23 hệ luận 1, các test assert lên **bất biến** (quan hệ, dấu, hướng
fail-safe), không lên số đếm sống — trừ T8, cố ý neo vào BQ vì đó chính là fact không được phép
trôi im lặng.

---

## 9. Điều kiện & ranh giới cho Sprint 2 (cash dividend)

**ĐƯỢC PHÉP**
1. Ex-date mechanical study và post-event drift, neo vào `exright_date`.
2. Dùng `div_total_on_exdate` làm số cổ tức trên mỗi cổ phiếu đi ex một ngày.
3. Cắt mẫu `actionable = 1`, và với mọi kết luận cấp danh mục thì thêm điều kiện nằm trong
   `universe_pit` tại ex-date (**N ≈ 3.032 sự kiện, 2014→**).

**BẮT BUỘC**
4. Loại hoặc gắn cờ `flag_same_exdate_other_family` (5,4% cùng ngày) và mở rộng kiểm nhiễm ISS
   ra đúng cửa sổ study đang dùng (±21 ngày ⇒ 7,0%).
5. Giá cum lấy ở **T−1**, giá sau lấy ở **T+1**; **cấm** đọc `ticker.Price` của dòng đúng ngày
   ex-date. Cấm trộn `Price` thô với `Close` hồi tố trong cùng một biểu thức.
6. Báo cáo phải khai N là **số sự kiện độc lập**, không phải số dòng — và chú ý cụm theo mã
   (một mã trả cổ tức nhiều năm không phải các quan sát độc lập).

**CẤM**
7. Announcement study dưới mọi hình thức cho tới khi có ≥2 vintage để đo tỉ lệ amendment.
8. Dùng `public_date` như ngày biết tin, kể cả trên tập con "trông sạch".
9. Suy số cổ tức từ tỉ số `Close/Price` (quan hệ là phép NHÂN, và không phân biệt được cổ tức
   tiền mặt với chia tách — `coding_guidelines` §21).
10. Dùng `exercise_ratio` để mô hình số CP lưu hành mà không fail-closed ở 42,3% dòng null/0.

---

## 10. Hạn chế đã biết của chính Sprint 1

1. **Không cắt được theo sàn** — bảng không có cột sàn (§3.2).
2. **Tỉ lệ amendment chưa đo được** — mới dựng vintage đầu tiên (§5.3).
3. **Chưa đối soát với tiền thật về tài khoản.** `value_per_share` mới chỉ được đối soát với
   chuỗi giá (§6.1), chưa với sổ broker. §21 `coding_guidelines` vẫn giữ nguyên: tiền broker là
   nguồn chính thức cho tỉ suất per-position trong báo cáo nhà đầu tư.
4. **`div_total_on_exdate` bỏ qua thuế cổ tức** (5% TNCN với cá nhân) — đây là số GỘP.
5. **182 sự kiện (2,1%) có cổ tức nhưng chuỗi giá không điều chỉnh gì.** Chưa truy nguyên; cần
   loại hoặc điều tra ở Sprint 2.

---

## 11. Artifact

| file | nội dung |
|---|---|
| `ca_lib.py` | reader BQ read-only + taxonomy có evidence + `num()` + `title_ratio()` |
| `profile_corp_action.py` | 20 truy vấn profiling, SQL xuất ra `out/sql/*.sql` |
| `build_event_ledger.py` | dựng ledger + summary + sample + vintage |
| `selfcheck_sprint1.py` | 21 invariant |
| `DATA_DICTIONARY.md` | từ điển 45 cột ledger |
| `ISSUES_LEDGER.md` | quy tắc đã thử & loại + câu hỏi chưa trả lời |
| `out/*.csv`, `out/ledger_summary.json` | mọi số trích trong file này |
| `out/event_ledger_sample.csv` | mẫu spot-check phân tầng theo subtype, có lineage |
| `out/dedup_dropped_sample.csv` | dòng bị dedup loại, kèm id sống sót |
| `out/vintage_asof_20260814.csv.gz` | snapshot hash để đo amendment về sau |
| `out/event_ledger.csv.gz` | ledger đầy đủ — **KHÔNG commit** (dựng lại bằng script) |
