---
kind: bigquery-table
status: TRAP
source: lithe-record-440915-m9.tav2_bq.corporate_action
group: price-volume
scope: ex-rights price adjustment, O/shares (outstanding shares) update, dividend/split event lookup
writer: UNKNOWN — không có script/cron nào trong repo ghi bảng này (grep sạch, 2026-08-13)
---

# `tav2_bq.corporate_action`

**Status: TRAP** — dữ liệu chất lượng tốt và đúng thứ đang thiếu (xem
[`ticker_close_vs_price_dividend_adj.md`](ticker_close_vs_price_dividend_adj.md) §"BigQuery KHÔNG có
cột raw per-event"), nhưng **chỉ là 1 lần nạp**, chưa có cơ chế refresh — đừng coi là live feed.

## Là gì

Bảng corp-action per-EVENT (không phải per-ngày như `ticker`), 36.149 dòng, 1.792 mã, phủ
2000-2026, cluster theo `ticker`, partition theo `public_date` (MONTH). Kiểm tra thật 2026-08-13
(bq CLI, `lithe-record-440915-m9`).

**`event_code`** (cột `category` LUÔN NULL — bỏ qua, dùng `event_code`):

| `event_code` | n | Ý nghĩa | Field quan trọng |
|---|---:|---|---|
| `DIV` | 17.058 | Cổ tức **TIỀN MẶT** — `value_per_share` = VND/cp GỘP (100% non-null), `exright_date`/`record_date`/`payout_date` | `value_per_share`, `exright_date` |
| `ISS` | 11.719 | Phát hành CP (chia tách/thưởng/ESOP/quyền mua/riêng lẻ) — `issue_method_name_vi` phân loại, `exercise_ratio` = tỉ lệ CP mới/CP cũ | `exercise_ratio`, `issue_method_name_vi`, `exright_date` |
| `AIS` | 4.878 | **Niêm yết bổ sung** — ngày CP mới CHÍNH THỨC vào lưu hành. `shares_delta` + `shares_total_after` **chỉ populate ở đây** | `shares_delta`, `shares_total_after`, `effective_date` |
| `NLIS` | 1.368 | Niêm yết mới / chuyển sàn lên | `effective_date` |
| `SUSP` | 678 | Huỷ đăng ký giao dịch / delist | `effective_date` |
| `MOVE` | 431 | Chuyển sàn (HOSE↔UPCOM...) | `effective_date` |
| `MA` | 17 | M&A | — |

`event_status`/`issue_status_vi`: `announced`("Thông báo")/`executed`("Đã thực hiện")/
`not_executed`(huỷ, 77 dòng kể từ 2025 riêng ISS — LỌC BỎ trước khi dùng).

## Bẫy (1) — `exright_date` (giá đã đổi) và `AIS.effective_date` (Oshares chính thức đổi) **LỆCH XA**

Đo thật FPT thưởng CP 15% 2025: `ISS.exright_date = 2025-07-21` (giá đã pha loãng ngay hôm đó) nhưng
`AIS.effective_date = 2025-09-12` (**~7 tuần sau**) mới thấy `shares_total_after` cập nhật. Nếu chỉ
JOIN theo `AIS` để lấy Oshares "kịp thời" thì **trễ hàng tuần** — đúng vấn đề user muốn giải nhưng
làm ngược sẽ hỏng lại. Cách đúng: **ước tính ngay tại `exright_date`** bằng
`shares_new = shares_old × (1 + exercise_ratio)` (từ `ISS`), rồi **đối soát lại** bằng
`AIS.shares_total_after` khi nó xuất hiện (ground truth chính xác, có thể lệch nhẹ do CP quỹ/làm
tròn) — KHÔNG chờ AIS mới cập nhật.

## Bẫy (2) — CHƯA CÓ WRITER/CRON trong repo Mike biết, nạp lần đầu là MỘT LẦN

`ingested_at` toàn bộ 36.149 dòng nạp đầu nằm trong khoảng **2026-08-12 15:22:57 → 15:48:52** (một
batch, ~26 phút) — không phải chuỗi lịch sử tích luỹ. Grep sạch repo Mike: không script `.py`/`.sh`
nào ghi bảng này, không có dòng crontab, không bus event nào nhắc `corporate_action`.

**2026-08-13, user xác nhận: bảng sẽ được refresh HÀNG NGÀY từ hôm nay** (writer thuộc quy trình
NGOÀI repo Mike quản, không phải fleet tự dựng). ⇒ Coi là nguồn sống có chủ đích, nhưng **verify
artifact, đừng tin lời hứa refresh** (nguyên tắc chuẩn — MIKE.md mục 2): trước khi bất kỳ pipeline
nào dựa vào tính "hôm nay có dữ liệu hôm nay", kiểm tra thật `MAX(ingested_at)`/`MAX(public_date)`
mỗi lần đọc, đúng khuôn `kb/cron_registry.md` §11 (freshness check thật, không suy từ lịch). Ngày
đầu tiên nên xác nhận lại: 2026-08-14 kiểm `MAX(public_date)` đã nhích qua 2026-08-12/13 chưa.

**CỬA SỔ NẠP ĐO ĐƯỢC (bổ sung 2026-08-13, job `Taylor_20260813_091128`)**: `15:22:57 → 15:48:52
UTC` = **22:22 → 22:48 ICT**. Đây là mốc quan trọng khi đặt lịch consumer: một cron chạy CHIỀU
cùng ngày sẽ luôn đọc dữ liệu của HÔM TRƯỚC. `corp_action_daily.py` vì thế chạy 07:30 ICT sáng hôm
sau và phân loại freshness theo **phiên giao dịch liền trước**, không theo "hôm nay" (mốc "hôm nay"
sẽ báo động giả mỗi sáng, mốc "ngày lịch trước" sẽ báo động giả mỗi thứ Hai). ⚠️ n=1 quan sát —
đừng biến nó thành giả định; script tự đo `MAX(ingested_at)` mỗi lần chạy.

## Bẫy (2b) — bảng bị UPSERT IN-PLACE: `public_date` bị ghi đè khi sự kiện lật trạng thái

Đo thật 2026-08-17: batch ingest gần nhất rewrite 1.331 dòng, trong đó **1.185 (89%) có `public_date` cũ
hơn 2026-08-01** (cũ nhất 2024-09-13) ⇒ vendor sửa dòng LỊCH SỬ mỗi lần chạy, không chỉ append. Với sự
kiện đã `executed`, ngày công bố Ý ĐỊNH **đã mất vĩnh viễn** — cùng cơ chế đã xác nhận ở tầng source ETL
cho `insider_transaction` ([`../fundamentals/insider_transaction.md`](../fundamentals/insider_transaction.md)
§Bẫy(1)). Đây là lý do Sprint 1 `corp_action_program_20260815` CẤM announcement study.

✅ **Vá từ 2026-08-17**: [`corporate_action_snapshots.md`](corporate_action_snapshots.md) —
`tav2_mike.corporate_action_snapshots`, append-only, 1 vintage/ngày. Mọi câu hỏi dạng "bảng trông như thế
nào ngày D" / "dòng này bị sửa lúc nào" phải đọc bảng đó, KHÔNG đọc bảng này. Bảng này chỉ trả lời được
"hiện tại".

## Bẫy (3) — trùng `(ticker, exright_date, event_code)` — cần GROUP BY/dedup có chủ đích

`id` là unique key thật (36.149 distinct = đúng số dòng) nhưng nhiều dòng CÓ THỂ trùng
`(ticker, exright_date, event_code)` (vd `ING` 2007-12-31 có 7 dòng `ISS` cùng ngày) — có thể là
nhiều đợt phát hành khác nhau chốt cùng ngày (SUM đúng) hoặc amendment/revision của cùng 1 sự kiện
(lấy dòng `public_date` mới nhất). Đừng SUM mù `exercise_ratio`/`value_per_share` khi JOIN — kiểm
`event_title_vi` từng dòng trước.

## Cách dùng hiệu quả — 2 nâng cấp cụ thể so với cơ chế hiện có

1. **O/shares (`ticker_financial.OShares` trễ theo quý, `shares_outstanding_live` chỉ 4 dòng tay)**:
   build view `oshares_live` = Oshares quý gần nhất × cumulative product `(1+exercise_ratio)` của mọi
   `ISS.exright_date` sau ngày báo cáo quý đó, override bằng `AIS.shares_total_after` khi có (chính
   xác hơn). Thay thế cách làm thủ công của Winston (`update_shares_live.py`).
2. **Ex-rights price / dividend measurement** — bảng này là đúng "cột raw per-event" mà
   [`ticker_close_vs_price_dividend_adj.md`](ticker_close_vs_price_dividend_adj.md) nói KHÔNG tồn
   tại trên BQ (viết 2026-08-02, TRƯỚC khi bảng này được tạo 2026-08-12): `DIV.value_per_share` cho
   trực tiếp đồng/cp GỘP theo mã+ngày — không cần giải hệ phương trình từ `cashDividendReceiving`
   gộp toàn tài khoản nữa (Tầng 2 trong file đó), và phân biệt được DIV/ISS rõ ràng (giải Bẫy 4 của
   `Close/Price`). **Vẫn nên đối soát chéo với broker** (Tầng 2 cũ) trước khi thay hẳn — chưa kiểm
   chứng độ chính xác/độ trễ công bố của nguồn vendor đằng sau bảng này so với tiền thật về tài khoản.

## Consumer đã có (2026-08-13)

| Script | Đọc gì | Ghi gì | Trạng thái |
|---|---|---|---|
| `corp_action_lib.py` | reader + taxonomy dùng chung (`is_price_adjusting` / `dilutes_share_count` / `feed_freshness`) | — | LIVE, 7 ca hồi quy |
| `oshares_live.py` | AIS + ISS → số CP lưu hành point-in-time | — (thư viện) | vòng 4: cổng chứng nhận neo AIS nằm TRONG module (`AIS_UNCERTIFIED` ⇒ `value=None`), 32 ca hồi quy — an toàn khi gọi thẳng `oshares_at()` |
| `dividend_adjusted_return.py::bq_corp_action()` | DIV/ISS tại (mã, ex-date) | — | LIVE (tầng bổ sung; tiền broker vẫn là nguồn số chính thức §21) |
| `mike/bin/corp_action_daily.py` | cả 3 cái trên + `active_nav_<label>.json` | `data/corp_action_daily/corp_action_daily_<date>.json` + Discord `trading_daily` | cron **CHƯA CÀI**, chờ quant-skeptic (job `Taylor_20260813_091128`) |

**Bẫy 2 nay đã được CƠ GIỚI HOÁ**, không còn là lời nhắc văn xuôi: `corp_action_daily.py` phân loại
`FRESH / STALE / DEAD` mỗi lần chạy và **không publish** khi DEAD. Nhưng lời nhắc vẫn đúng cho MỌI
consumer khác — ai đọc bảng này ngoài cron đó thì vẫn phải tự gọi `feed_freshness()`.

## Việc còn treo trước khi wire vào report pipeline

- Xác nhận nguồn/refresh cadence của bảng (ai tạo, có cron nào update tiếp không).
- Nếu wire vào `dividend_adjusted_return.py`/report §21 gate: qua Taylor + quant-skeptic review
  (đổi công thức đo lợi nhuận per-position, thuộc diện §21/§22 coding_guidelines).

## Bẫy (5) — `listing_date` KHÔNG phải ngày công bố/thông báo Sở; nó là ngày NIÊM YẾT BỔ SUNG

**Phủ sóng**: NULL ở MỌI `event_code` **trừ `ISS`**, nơi **9.594/11.722 = 81,8%** dòng có giá trị.
(⚠️ `corp_action_program_20260815/DATA_DICTIONARY.md` từng ghi "100% NULL toàn bảng" — SAI, do đo
gộp cả bảng trong khi `DIV` chiếm 47% dòng và luôn NULL. Đã sửa 2026-08-17.)

**Ngữ nghĩa (đo, không suy)**: `ISS.listing_date` = cùng đại lượng với `AIS.effective_date` = ngày
CP mới chính thức vào lưu hành. Khi mã có dòng `AIS` trong ±365 ngày, tỉ lệ khớp CHÍNH XÁC:
STOCK_DIVIDEND 90,9% · BONUS 90,7% · PP 84,9% · ESOP 74,1% · RIGHTS 65,9%. Placebo chạy đúng phép
thử đó trên `exright_date`: 0,1–12,3%. Khớp exact và khớp ±3 ngày lệch nhau <1pp ở mọi subtype ⇒
đây là CÙNG MỘT trường, không phải hai ngày tình cờ gần nhau. Ca mẫu khớp tay: FPT thưởng CP 15%
2025 — `ISS.listing_date = 2025-09-12` = `AIS.effective_date = 2025-09-12` (đúng ca ~7 tuần mà
Bẫy (1) của file này đã mô tả).

**⇒ Ba hệ quả khi dùng:**
1. **Nằm SAU `exright_date`**, không phải trước: median RIGHTS **+91 ngày**, STOCK_DIVIDEND +50,
   BONUS +49. Chỉ 11/1.542 sự kiện RIGHTS có `listing_date` trước ex-date, và 9/11 lệch 100–436
   ngày (dữ liệu cũ hỏng, không phải thông báo).
2. **Là KẾT QUẢ của chính sự kiện** — CP mới lên sàn nhanh hay chậm phụ thuộc việc tổ chức phát
   hành thu tiền + hoàn tất hồ sơ, KHÔNG biết được tại `exright_date`. Neo lợi suất lên nó (kể cả
   cửa sổ hậu sự kiện) là **look-ahead**, không chỉ "sai ngày".
3. **Càng lùi về quá khứ càng kém tin**: `listing_date == exright_date` (giá trị rác, vendor chép
   ex-date khi không có ngày thật) chiếm 72,3% sự kiện RIGHTS giai đoạn 2002–2008, giảm đơn điệu
   về **0,0%** các năm 2023/2025/2026. Với PP, khối rác này là 69% toàn mẫu ⇒ **median gap của PP
   bằng 0 KHÔNG có nghĩa "niêm yết cùng ngày"**.

**Dùng được cho**: mô hình số CP lưu hành (thay/bổ sung cho việc phải chờ dòng `AIS` xuất hiện —
`ISS.listing_date` có sẵn ngay trên dòng phát hành, phủ 81,8% vs `AIS` chỉ 4.884 dòng).
**KHÔNG dùng được cho**: bất kỳ neo point-in-time nào, bất kỳ study nào cần "thị trường biết tin
lúc nào".

**Nhắc lại cho rõ**: bảng này **KHÔNG có cột nào ghi thời điểm thị trường lần đầu biết tin.** Cả 3
ứng viên đều đã bị loại bằng đo đạc — `public_date` (ghi đè tại chỗ, không vintage — Bẫy 2b),
`id_created_date` (89,4% = ngày backfill 2024-10-11), `listing_date` (hậu sự kiện, mục này). Đường
duy nhất còn lại là tích luỹ vintage ở `tav2_mike.corporate_action_snapshots` (sống từ 2026-08-17),
đo lại N **không sớm hơn 2027-08**.

## Nguồn
Kiểm tra trực tiếp bằng `bq` CLI 2026-08-13 (Mike, theo yêu cầu user tra cứu bảng mới).

↩ [Về index nhóm](index.md)
