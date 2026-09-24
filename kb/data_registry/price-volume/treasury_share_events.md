---
kind: bigquery-table
status: PROPOSED — bảng CHƯA TỒN TẠI. Dry-run CSV đã có, DDL chưa chạy. Không wire vào bất kỳ code nào.
source: lithe-record-440915-m9.tav2_mike.treasury_share_events
group: price-volume
scope: sự kiện mua/bán cổ phiếu quỹ ĐÃ THỰC HIỆN, gộp + định lượng từ tav2_bq.treasury_news
writer: mike/agents/Taylor/research/treasury_table_20260918/build_treasury_share_events.py — ONE-TIME, KHÔNG cron
upstream: tav2_bq.treasury_news (gộp theo ticker|public_date|action_type) + tav2_bq.ticker_financial.OShares (33 ca suy luận)
created: 2026-09-18 (job Taylor_20260918_103820, vá B1 job Taylor_20260918_110145)
---

# `tav2_mike.treasury_share_events` — sự kiện mua/bán CP quỹ ĐÃ THỰC HIỆN

577 sự kiện, 233 mã, 2015→2026. Một dòng = một `(ticker, public_date, action_type)`.
`action_type ∈ {buy_done, sell_done}` (chỉ kết quả đã thực hiện, không gồm đăng ký/dự kiến).

Đây là tầng **định lượng** đặt trên [`treasury_news_buyback.md`](treasury_news_buyback.md)
(status PARTIAL): bảng nguồn chỉ có `shares_delta` ở 23,9% dòng và nhiều dòng trùng cho một sự
kiện thật (bẫy 1 + bẫy 4 của entry đó). Bảng này gộp dòng trùng, tách bạch nguồn của từng con số
theo tier, và **để NULL khi không biết** thay vì nội suy.

## Bốn cái bẫy

**1. `outstanding_delta` NULL ≠ 0.** 413/577 dòng (71,6%) là `UNSIZED` — vendor không công bố số
lượng và không suy được. Trong control đo được **62 sự kiện có size thật >0 mà `OShares` không
nhúc nhích** (lớn nhất PVI 7.590.400 CP) ⇒ `unsized_reason='NO_MOVE'` tuyệt đối không được đọc
thành 0. Mọi consumer phải xử NULL tường minh (fail-closed hoặc cờ), không `COALESCE(...,0)`.

**2. `public_date` KHÔNG phải ngày PIT cho 33 dòng suy luận.** Với `source='OSHARES_DELTA_INFERRED'`,
con số chỉ thực sự biết được từ `confirmed_asof` (ngày BCTC quý sau công bố) — trung vị **muộn hơn
45 ngày**, tối đa 149. Join theo `public_date` vào hệ rating/sizing = **nhìn trước 45 ngày**. Join
đúng: `COALESCE(confirmed_asof, public_date) <= asof`.

**3. Ba tier KHÔNG đáng tin như nhau.** `confidence='high'` (131 dòng, `VENDOR_PUBLISHED` +
`SIBLING_ROW`) là số vendor công bố. `confidence='medium'` (33 dòng, `OSHARES_DELTA_INFERRED`) là
suy luận từ lệch OShares, đo trên control n=13: 77% khớp chính xác, 85% sai ≤5%, 92% sai ≤20% —
**không** dùng cho số liệu kế toán/báo cáo nhà đầu tư; dùng được cho ranking/universe nơi sai 5%
trên một cấu phần <5% OShares là nhiễu.

⚠️ **Nhóm control đó KHÔNG đại diện cho 5/33 dòng có cửa sổ 2 quý.** `inferred_window_days` là bề
rộng THẬT của cửa sổ OShares dùng để suy: 28 dòng ~1 quý (76–115 ngày), **5 dòng 176–188 ngày**
(TSJ 2019-01-23, SGP 2018-06-04, DRH 2020-04-06, LSS 2021-04-09, SMN 2023-06-27) — phải nới ra 2
quý vì quý kế tiếp bị confounder. Nhóm control gốc của Winston gần như chỉ gồm ca 1 quý (12 ca
k=0 / 1 ca k=1) ⇒ ba con số 77%/85%/92% là thống kê của **cửa sổ 1 quý**, không đo được cho 5
dòng này. Cần chắc hơn thì lọc `inferred_window_days <= 120`.

**4. `SUM(outstanding_delta)` KHÔNG AN TOÀN nếu không lọc theo cột dedup — PHẢI có
`WHERE is_canonical`.** Khoá gộp `(ticker, public_date, action_type)` không bắt được trường hợp
**cùng một giao dịch thật được công bố ở hai ngày khác nhau**. Hai ca đo thật trên 577 dòng:

| Ca | Hai dòng | Mỗi dòng | SUM thô | Thật |
|---|---|---|---|---|
| NDN `buy_done` | 2018-05-17 + 2018-05-18 (cả hai `VENDOR_PUBLISHED`) | −1.000.000 | −2.000.000 (+2,5% trên ~39,6tr CP lưu hành) | −1.000.000 |
| CTD `buy_done` | 2021-02-01 (`OSHARES_DELTA_INFERRED`) + 2021-02-03 (`VENDOR_PUBLISHED`) | −2.008.900 / −2.000.000 | −4.008.900 (+2,7%) | −2.000.000 |

Luật gộp (xác định, không đoán): cùng `ticker` + `action_type`, cách dòng **NEO** của nhóm
**≤14 ngày**, `|outstanding_delta|` lệch **≤5%** ⇒ cùng một giao dịch. Đúng một dòng được
`is_canonical=TRUE` (tier tin nhất `VENDOR_PUBLISHED` > `SIBLING_ROW` > `OSHARES_DELTA_INFERRED`,
rồi `public_date` sớm nhất, rồi `id` nhỏ nhất); dòng còn lại **ở lại trong bảng** để audit với
`is_canonical=FALSE` + `duplicate_of` trỏ về canonical. Trên lô hiện tại: **2 nhóm, 2 dòng
non-canonical**; `SUM` thô −247.899.980 vs lọc canonical **−244.891.080** (chênh 3.008.900 CP).

⚠️ **Dòng canonical KHÔNG nhất thiết mang ngày công bố SỚM nhất của giao dịch.** Canonical chọn
theo TIER trước (độ tin của con số), không theo ngày: CTD giữ dòng vendor `public_date=2021-02-03`
(tin báo chí) trong khi công bố THẬT sớm hơn — văn bản chính thức 2021-02-01 17:25. Ai cần *ngày
công bố thật* phải lấy `MIN(public_date) OVER (PARTITION BY dup_group_id)`, không đọc thẳng
`public_date` của dòng canonical.

Ngưỡng chọn từ phân phối thật, không cảm tính: 2 cặp ứng viên nằm ở gap **1–2 ngày**, cặp
consecutive-event gần nhất KHÁC nằm ở **53 ngày**, và mọi cặp cùng-giá-trị (lệch ≤5%) còn lại đều
≥**244 ngày** (HWS/VND/TW3 mua lại đúng lô cũ — đợt mua THẬT thứ hai, không được gộp). Mọi N
trong [2, 52] cho cùng kết quả; chọn 14 để hai đợt mua thật cách nhau 3 tuần không bao giờ bị gộp.
Neo theo dòng ĐẦU nhóm (không chain truyền tiếp) ⇒ bề rộng một nhóm bị chặn cứng ở 14 ngày; chain
sẽ gộp nhầm nhiều đợt mua thật liên tiếp thành một (mất dữ liệu — tệ hơn là đếm 2 lần).

⚠️ **Dedup chỉ phủ dòng SIZED.** 413 dòng `UNSIZED` có delta NULL nên không so được theo giá trị
(và không cộng vào `SUM`). Đo được **6 cặp SIZED–UNSIZED + 18 cặp UNSIZED–UNSIZED** trong vòng 14
ngày — nghi trùng nhưng KHÔNG chứng minh được, nên để nguyên `is_canonical=TRUE`. Hệ quả:
`COUNT(*)` số sự kiện có thể phồng tối đa 24; `SUM(outstanding_delta)` thì không.

## Query mẫu (an toàn)

```sql
SELECT ticker, SUM(outstanding_delta) AS delta_luu_hanh
FROM `lithe-record-440915-m9.tav2_mike.treasury_share_events`
WHERE is_canonical                                        -- bẫy 4
  AND size_status = 'SIZED'                               -- bẫy 1 (NULL ≠ 0)
  AND COALESCE(confirmed_asof, public_date) <= @asof      -- bẫy 2
  AND confidence = 'high'                                 -- bẫy 3, nếu cần số kế toán
GROUP BY ticker
-- COUNT(*) KHÔNG an toàn, xem bẫy 4 (tối đa 24 cặp UNSIZED nghi trùng chưa gộp được).
```

## Quy ước dấu
`outstanding_delta` = Δ lượng CP **LƯU HÀNH** = `-treasury_news.shares_delta`.
`buy_done` ÂM (mua vào quỹ ⇒ lưu hành giảm) · `sell_done` DƯƠNG. Đo trên 577/577 sự kiện, 0 vi phạm.
⚠️ Mua CP quỹ **KHÔNG đổi số NIÊM YẾT** — `corporate_action.AIS.shares_total_after` là niêm yết
(GỒM CP quỹ), `ticker_financial.OShares` là lưu hành (đã trừ). Hấp thụ kiểu ISS là sai chiều
(xem `agents/Taylor/research/treasury_reconcile_20260917/report.md` §A2).

## Mức verify — cái gì đã độc lập, cái gì còn kế thừa

Loader **recompute lại GIÁ TRỊ** của cả 33 ca suy luận trực tiếp từ `ticker_financial.OShares`
(không tin chuỗi `why` của Winston): 33/33 khớp chính xác, 0 ca bị từ chối. **Nhưng chỉ giá trị
là độc lập** — *cửa sổ quý* nào được chọn và *bộ lọc confounder* (CA_CONFOUNDED / NO_MOVE /
MULTI_EVENT / ISSUANCE_MATCH / SIGN_MISMATCH / OVER_CAP) vẫn **kế thừa nguyên** của Winston
(job `Winston_20260918_052425`), chưa verify độc lập. Nói cách khác: "cho cửa sổ này, số đúng" đã
kiểm; "cửa sổ này là cửa sổ đúng" thì chưa.

## Freshness
One-time. `loaded_at` + `loader_version` trên từng dòng. **Chưa có cadence xác nhận** cho
`treasury_news` (n=1 lô 2026-09-13 + 6 dòng 2026-09-16) ⇒ nếu chuyển recurring thì §14 bắt buộc
một freshness gate thật trên `loaded_at`, không phải kiểm tra bảng tồn tại.

## Nạp lại

**(a) Chỉ nạp lại bằng REBUILD TOÀN BỘ (`CREATE OR REPLACE` / truncate+load) — KHÔNG `MERGE`
per-row.** Ba cột dedup (`dup_group_id` / `is_canonical` / `duplicate_of`) chỉ đúng trong phạm vi
MỘT lần build: `mark_duplicates()` chỉ nhìn các dòng của lượt chạy hiện tại, không đọc lại bảng đã
có. Dòng MERGE thêm vào sẽ mang `is_canonical=TRUE` mặc định, đứng cạnh dòng cũ cũng `TRUE` ⇒ tái
diễn đúng bug đếm-2-lần ở bẫy 4, **không có lỗi nào báo**. Đây không phải rủi ro giả định:
`treasury_news` vẫn đang nhận dòng mới (lô 2026-09-13 + 6 dòng 2026-09-16).

**(b) Hai tham số dedup phải ĐO LẠI nếu chuyển recurring.** `DUP_MAX_GAP_DAYS=14` và
`DUP_REL_TOL=5%` được chọn từ phân phối thật của **đúng 577 dòng lô này** (khoảng trống giữa
1–2 ngày và 53 ngày, mọi cặp cùng-giá-trị khác ≥244 ngày). Lô mới có thể lấp chính khoảng trống
đó — đo lại phân phối trước khi giữ nguyên hai con số, không mặc định kế thừa.

## Consumer
**Hiện tại: KHÔNG CÓ.** `oshares_live` chưa đọc bảng này; điều kiện mở lại của quyết định 09-08
(chưa có case đổi quyết định đầu tư) vẫn đứng.

## Liên quan
- [`treasury_news_buyback.md`](treasury_news_buyback.md) — bảng NGUỒN (`tav2_bq.treasury_news`,
  PARTIAL). Bẫy 1 (`shares_delta` 23,9%) và bẫy 4 (dòng trùng cùng ngày = tier `SIBLING_ROW` ở
  đây) chính là lý do bảng này tồn tại.
- [`../fundamentals/ticker_financial_oshares.md`](../fundamentals/ticker_financial_oshares.md) —
  nguồn của 33 ca suy luận; RESTATE, không PIT thật (gốc của bẫy 2).
- Report đầy đủ: `mike/agents/Taylor/research/treasury_table_20260918/report.md`;
  DDL đề xuất `.../schema.sql` (CHƯA CHẠY).

↩ [Về index nhóm](index.md)
