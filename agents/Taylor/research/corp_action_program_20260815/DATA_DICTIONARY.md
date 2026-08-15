# DATA_DICTIONARY — `out/event_ledger.csv.gz`

Một dòng = **một sự kiện kinh tế đã deduplicate**. 35.465 dòng dựng từ 36.170 dòng thô của
`lithe-record-440915-m9.tav2_bq.corporate_action` (đo 2026-08-15, job `Taylor_20260815_114954`).
Dựng lại: `python3 build_event_ledger.py`. Ngữ cảnh + phán quyết gate: `SPRINT1.md`.

Mẫu đọc được ngay (không cần giải nén): `out/event_ledger_sample.csv` (phân tầng theo subtype).

---

## Lineage — trả lời "dòng thô nào đẻ ra dòng này"

| cột | kiểu | ý nghĩa |
|---|---|---|
| `event_uid` | str(16) | sha1 của khoá kinh tế, cắt 16 hex. Ổn định giữa các lần dựng lại **nếu** khoá không đổi. Không phải id vendor. |
| `src_ids` | str | **mọi** `id` thô của sự kiện này, phân tách `;`, đã sort. Đây là lineage đầy đủ — mọi id gốc xuất hiện đúng 1 lần trên toàn ledger (selfcheck T3b). |
| `n_raw_rows` | int | `len(src_ids)`. `>1` ⇒ có dòng bị dedup gộp lại. |
| `survivor_id` | str | `id` của dòng thô được chọn làm nguồn giá trị. Luôn nằm trong `src_ids` (T3e). |
| `dropped_ids` | str | id bị loại (rỗng nếu `n_raw_rows=1`). Xem `out/dedup_dropped_sample.csv`. |

**Quy tắc chọn survivor** (tất định, T9): `public_date` mới nhất → `id_created_date` mới nhất →
`id` theo thứ tự chữ. Ý nghĩa: bản công bố sau thay thế bản trước.

## Định danh

| cột | ý nghĩa |
|---|---|
| `ticker` | mã CK |
| `organ_code` | mã tổ chức của vendor |
| `icb_code_lv1` | mã **NGÀNH** ICB cấp 1. ⚠️ KHÔNG phải sàn — bảng nguồn không có cột sàn. |
| `event_family` | `CASH_DIVIDEND` · `ISSUANCE` · `ADDITIONAL_LISTING` · `NEW_LISTING` · `SUSPENSION` · `EXCHANGE_MOVE` · `MERGER_ACQUISITION` · `OTHER` |
| `event_subtype` | với `ISSUANCE`: `STOCK_DIVIDEND` · `BONUS` · `RIGHTS` · `ESOP` · `PRIVATE_PLACEMENT` · `CONVERTIBLE` · `AUCTION` · `MERGER` · `UNKNOWN`. Với họ khác = chính tên họ. |
| `taxonomy_rule` | đường ra nhãn: `event_code` · `issue_method_code` · `issue_method_name_vi` · `unmatched` |
| `taxonomy_evidence` | **giá trị trường** đã quyết định nhãn (vd `Rights`). Cho phép kiểm tay từng dòng. |

`UNKNOWN` chỉ sinh ra từ `taxonomy_rule='unmatched'` (T2b) và không bao giờ actionable (T7c).

## Ngày tháng

| cột | ý nghĩa | dùng được cho |
|---|---|---|
| `exright_date` | ngày GDKHQ | **neo mọi study** ✅ |
| `public_date` | vendor gọi là ngày công bố | **descriptive only** ❌ (xem `known_date_confidence`) |
| `record_date` | ngày chốt danh sách | mô tả |
| `payout_date` | ngày trả tiền (chỉ DIV) | đối soát tiền về |
| `issue_date` | ngày phát hành (AIS/NLIS/SUSP/MOVE) | mô tả |
| `listing_date` | 100% NULL toàn bảng | — |
| `effective_date` | ngày hiệu lực (AIS = CP mới vào lưu hành) | mô hình số CP; ⚠️ lệch `exright_date` tới ~7 tuần |
| `id_created_date` | giải mã 4 byte đầu ObjectId = **vendor tạo bản ghi** | tie-break; ⚠️ 89,4% = ngày backfill 2024-10-11, **không phải known_date** |
| `ingested_at` | timestamp ghi **CUỐI** vào BQ (bảng bị ghi đè tại chỗ) | freshness check |

## Trạng thái

| cột | giá trị |
|---|---|
| `event_status` | `executed` · `announced` · `not_executed` |
| `issue_status_vi` | nhãn tiếng Việt tương ứng của vendor |

## Thời điểm biết tin (point-in-time)

| cột | ý nghĩa |
|---|---|
| `known_date` | = `public_date`, chép lại để tách bạch vai trò |
| `known_date_confidence` | `WEAK_UNVERIFIED_VINTAGE` (n=30.830) · `UNUSABLE_NOT_BEFORE_EVENT` (n=4.635) · `UNUSABLE_NO_PUBLIC_DATE` (n=0) |
| `known_date_lead_days` | `exright_date − public_date`. ≤0 ⇒ luôn bị hạ UNUSABLE (T5a). |
| `fleet_known_from` | hằng `2026-08-12` = ngày đầu tiên fleet có bất kỳ dòng nào của bảng. |

> **Không tồn tại hạng nào mạnh hơn `WEAK`** — cố ý, và selfcheck T5c chặn ai đó thêm vào. Lý do:
> bảng bị ghi đè tại chỗ và không có bản vintage, nên "public_date chưa từng bị sửa" là **giả
> định**, không phải phép đo. Chi tiết `SPRINT1.md` §5.

## Giá trị

| cột | ý nghĩa |
|---|---|
| `value_per_share` | **DIV: VND/cp tiền mặt GỘP** (chưa trừ thuế TNCN 5%). NULL với mọi họ khác. |
| `div_total_on_exdate` | **tổng cổ tức tiền mặt thật đi ex của (mã, ex-date)** = SUM `value_per_share` **sau khi** dedup theo đợt, bỏ `not_executed`. Đây là số Sprint 2 phải dùng — KHÔNG tự SUM dòng thô. |
| `exercise_ratio` | CP mới / CP cũ. ⚠️ NULL **hoặc 0** ở 42,3% dòng ISS. `0` ≠ "không pha loãng" — nhân `(1+0)` là no-op im lặng. |
| `issue_volumn` | số CP phát hành |
| `total_value` | tổng giá trị đợt phát hành |
| `shares_delta`, `shares_total_after` | chỉ có ở `AIS`/`NLIS`/`SUSP`; **NULL 100% trên ISS** |
| `ref_price` | **NULL 100% trên DIV/ISS**; chỉ có ở NLIS/MOVE = giá tham chiếu ngày niêm yết. Không phải giá tham chiếu ex-right. |

## Cờ (đều 0/1)

| cột | =1 nghĩa là | n |
|---|---|---:|
| `is_price_adjusting` | kỳ vọng giá điều chỉnh tại ex-date (DIV, hoặc ISS thuộc stock-div/bonus/rights) | 23.356 |
| `flag_cancelled` | `event_status='not_executed'` — giữ lineage, **cấm** vào mẫu actionable | 1.419 |
| `flag_announced_only` | `announced` — chưa xảy ra | 849 |
| `flag_no_exright` | thiếu `exright_date` | — |
| `flag_div_no_value` | DIV thiếu/không dương `value_per_share` | 0 |
| `flag_ratio_unusable` | ISS có `exercise_ratio` NULL hoặc 0 | 4.661 |
| `flag_unknown_subtype` | subtype = `UNKNOWN` | 15 |
| `flag_pit_public_not_before_ex` | `known_date_confidence` bắt đầu bằng `UNUSABLE` | 4.635 |
| `flag_same_exdate_other_family` | có `event_code` khác cùng đi ex ngày đó trên cùng mã (DIV+ISS) | 1.969 (trong đó 921 là sự kiện DIV) |
| `flag_residual_dup` | `n_raw_rows > 1` | 521 |
| `actionable` | `executed ∧ có exright_date ∧ (DIV: value>0 \| ISS: subtype≠UNKNOWN)` | 26.218 |

---

## `out/vintage_asof_<YYYYMMDD>.csv.gz`

Snapshot để **đo tỉ lệ amendment về sau** — thứ duy nhất một snapshot đơn lẻ không nói được.
Đặt tên theo `MAX(ingested_at)` của chính bảng (không theo đồng hồ) nên tái lập được.

| cột | ý nghĩa |
|---|---|
| `id` | id thô vendor |
| `payload_sha1` | sha1 của 14 trường **có thể đổi**: `event_status`, `public_date`, `exright_date`, `record_date`, `payout_date`, `effective_date`, `value_per_share`, `exercise_ratio`, `issue_volumn`, `shares_delta`, `shares_total_after`, `issue_method_code`, `dividend_year`, `dividend_stage_vi` |
| `public_date`, `event_status` | tách riêng để thấy ngay 2 trường nhạy nhất |

**Cách dùng:** chạy lại `build_event_ledger.py` sau N tuần → join 2 file theo `id` → `payload_sha1`
khác nhau = sự kiện đã bị vendor viết lại. Đó là phép đo cần có trước khi mở lại announcement study.

## `out/div_price_step_detail.csv.gz`

Một dòng mỗi sự kiện DIV "sạch" đo được (n=8.819): `observed_factor` (= `r_before/r_after`, với
`r = Price/Close`) so với `expected_factor` (= `P_cum/(P_cum − D)`, **`P_cum` là `Price` THÔ**,
không phải `Close` hồi tố). `factor_error` là hiệu. Dùng để truy nguyên 2,1% sự kiện có cổ tức
nhưng chuỗi giá không điều chỉnh gì.
