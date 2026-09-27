---
kind: derived-table
status: TRAP
source: data/rating_8l_history.csv + tav2_bq.fa_ratings_8l (dựng bởi rating_8l_history.py) — cột `route` (phân ngành 8L)
group: fundamentals
note: route KHÔNG có vintage trước 2026 — nguồn ICB_Code (tav2_bq.ticker) gần như không ghi lại tái phân ngành
writer: rating_8l_history.py; cron weekly qua mike/bin/refresh_fa_ratings_8l.sh
---

# `rating_8l_history.csv` / `tav2_bq.fa_ratings_8l` — cột `route` (phân ngành 8L)

**Status: TRAP — `route` không phải point-in-time TRƯỚC 2026, và không thể làm cho nó point-in-time
từ nguồn hiện có.** Cột `rating`/`tier` thì dùng được bình thường; bẫy nằm ở `route` và ở việc
`rating` PHỤ THUỘC `route` (mỗi route có thẻ điểm riêng — `rate_row()`).

## Là gì
`rating_8l_history.py` dựng lại lịch sử rating 8L 1-5 theo quý (2014→nay) cho mọi mã. Bước đầu tiên
là gán **route** (BANK / INSURANCE / SECURITIES / POWER / CYCLICAL / REALESTATE / COMPOUNDER) từ
`ICB_Code`, vì route quyết định dùng thẻ điểm nào. Output: `data/rating_8l_history.csv` (đủ cột) và
`tav2_bq.fa_ratings_8l` (5 cột `ticker,time,route,rating,tier`, dedupe theo `(ticker, eff_date)`).

## Ai ghi / cadence
`rating_8l_history.py`, chạy weekly qua `mike/bin/refresh_fa_ratings_8l.sh`. Script **CREATE OR
REPLACE** bảng BQ mỗi lần chạy trừ khi `R8L_HIST_NO_BQ_REFRESH=1`. Output CSV đổi được bằng
`R8L_HIST_OUT`. **Mọi run thí nghiệm PHẢI set CẢ HAI** — xem bẫy (4).

## Bẫy

**(1) Nguồn `ICB_Code` KHÔNG có vintage — đây là giới hạn dữ liệu, không phải bug sửa được.**
Đo trên `tav2_bq.ticker` ngày 2026-09-27: **1.291 mã có `ICB_Code`, chỉ 6 mã từng có >1 giá trị**, và
5/6 lần đổi đầu tiên xảy ra từ 2017 trở về sau (2 mã chỉ đổi trong 2 tháng gần nhất). Một bảng giá
ngày được dựng lại thì không giữ được phân ngành *như đã biết tại thời điểm đó*. ⇒ **những lần tái
phân ngành trước 2026 gần như không được ghi lại, và KHÔNG khôi phục được từ bảng này.** Muốn đúng PIT
đầy đủ phải có nguồn phân ngành có vintage (FiinPro-X / lịch sử ngành HOSE).

**(2) Trước bản vá 2026-09-27, route là `ANY_VALUE(ICB_Code) GROUP BY ticker`** ⇒ gán phân ngành
**CỦA HÔM NAY** cho toàn bộ panel 2014→nay, và **không tất định** (ANY_VALUE không có thứ tự). Hai lần
chạy cùng dữ liệu có thể ra 2 route khác nhau cho mã vừa đổi ngành. Đã cắn thật: HDG đổi `ICB_Code`
8633→7535 ngày 2026-09-07, bản dựng 2026-09-27 10:36 gán **POWER cho cả 49 dòng từ 2014-08-01**, trong
khi suốt 4.136 phiên trước đó HDG là 8633 (REALESTATE). HDG là thành viên rổ custom30V (26 lượt trong
`data/custom30v_8l_publish.csv`) ⇒ đường quyết định, không phải hiển thị.

**(3) Bản vá (2026-09-27, branch `fix/rating8l-icb-pit`): đoạn liên tiếp ≥`ICB_MIN_RUN` (20) phiên +
`merge_asof` backward theo `eff_date`.** Hệ quả cần biết khi đọc số:
* **Ngưỡng 20 phiên là một knob có hiệu lực THẬT.** HDG có đoạn 7535 dài **15 phiên** (từ 2026-09-07)
  ⇒ CHƯA "xác lập" ⇒ HDG vẫn REALESTATE. Đoạn đó sẽ vượt 20 phiên trong ~1 tuần và **HDG sẽ tự đổi
  sang POWER ở lần refresh weekly kế tiếp** — đổi route ⇒ đổi thẻ điểm ⇒ có thể đổi rating. Không phải
  lỗi; nhưng ai thấy rating HDG nhảy sau đầu tháng 10/2026 thì đây là lý do.
* Lọc nhiễu là cần thiết, không phải tô điểm: SBM nhảy 7535↔2357 liên tục 2020-2025, mỗi lần 1-4
  phiên; TV3 có 4 đoạn nhiễu 1 phiên. As-of theo `MIN(time)` mỗi mã sẽ biến một phiên nhiễu thành
  "đổi ngành vĩnh viễn".
* Chỉ **3 mã** (DIH, LIC, TV3) hiện có >1 đoạn đã xác lập trải trên >1 `ICB_Code`.
* SQL phát **một dòng cho MỖI đoạn**, KHÔNG gộp `GROUP BY ticker, icb` + `MIN(icb_from)` — gộp làm mất
  lần **quay lại** mã cũ (X→Y→X). Hiện 0/1.291 mã gặp ca này ⇒ là guard cho bẫy tiềm ẩn, có test riêng
  (`rating8l_icb_pit_selfcheck.py` T2) vì nếu không thì đó là code không ai kiểm.

**(4) `route` là cross-sectional: đổi route của MỘT mã làm đổi `tier` của mã KHÁC.** Tier của route
COMPOUNDER là **phân vị theo từng quý** trong pool COMPOUNDER. Đo thật khi DIH chuyển vào COMPOUNDER:
**40 dòng / 39 mã khác đổi tier** (đều tốt lên 1 bậc), không mã nào đổi `route` hay `rating`. Consumer
nào đọc `tier` phải biết điều này; consumer đọc `rating` (cổng ≤3) thì không ảnh hưởng.

**(5) Chạy thí nghiệm mà quên `R8L_HIST_NO_BQ_REFRESH=1` sẽ GHI ĐÈ BẢNG PRODUCTION.** Đã cắn thật
2026-09-27 13:00:29 ICT (job `Taylor_20260927_052433`): run thí nghiệm ICB-PIT có `R8L_HIST_OUT` trỏ
ra file EXP nhưng **thiếu** `R8L_HIST_NO_BQ_REFRESH=1` ⇒ `refresh_bq_table()` vẫn CREATE OR REPLACE
`tav2_bq.fa_ratings_8l` bằng dữ liệu chưa được duyệt. Guard đã tồn tại từ `f4b081b7` — lỗi là KHÔNG
DÙNG guard. Consumer bị ảnh hưởng trong lúc bảng sai: `regime_size_overlay`, `custom30v_hybrid`
(luật swap rating≤2), golive sizing, `build_universe_pit_quality`, `lag_rating_filter`.
Snapshot bản bị ghi đè:
`mike/agents/Taylor/research/measurement_integrity_audit_20260927/part2/fa_ratings_8l_CONTAMINATED_snapshot_20260927.csv`.
Khôi phục = chạy lại đúng đường production:
`python3 -c "import rating_8l_history as R; R.refresh_bq_table('<WC>/data/rating_8l_history.csv')"`
rồi **kiểm chứng bằng truy vấn** — `refresh_bq_table()` bắt mọi Exception và chỉ in `[!] skipped`,
nên stdout "thành công" KHÔNG phải bằng chứng.

**(6) `custom_basket.build_pit` đọc rating từ BẢNG BQ (`fa_ratings_8l`), không từ CSV** —
`custom_basket.py:631`. Backtest chạy với `BQ_LOCAL_CACHE` thì đọc `<cache>/fa_ratings_8l.parquet`,
tức **vintage của cache, không phải bảng live**. Hệ quả: con số pin R3 phụ thuộc vintage rating trong
snapshot cache đã ghim, và một thí nghiệm muốn A/B rating PHẢI đổi chính file parquet đó (đường đã
dùng: symlink farm + thay 1 file) chứ không phải đổi CSV.

## Dùng đúng
* Cổng chất lượng (`rating ≤ 3` cho LAG — `lag_rating_filter.py`; `gate_rating` trong
  `custom_basket.build_pit`): dùng bình thường, as-of `eff_date`.
* Cần `route` cho một ngày trong quá khứ: chỉ tin từ 2026 trở đi; trước đó coi như "phân ngành gần
  nhất đã xác lập", và nói rõ giới hạn này trong bất kỳ kết luận nghiên cứu nào.
* Đừng dùng `tier` COMPOUNDER như một đại lượng độc lập theo mã — nó là phân vị trong pool.

## Nguồn / lineage
Bản vá FAIL-G: audit `measurement-integrity-audit-2026-09-27` PART2 §C, branch
`fix/rating8l-icb-pit`, báo cáo + mọi CSV lớp lệch:
`mike/agents/Taylor/research/failg_icb_pit_20260927/`. Selfcheck:
`WorkingClaude/rating8l_icb_pit_selfcheck.py` (24/24 PASS × 4 biến thể TZ, 4 mutation KILLED).
