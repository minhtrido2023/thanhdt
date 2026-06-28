# Pipeline Review — Vấn đề & Khuyến nghị cải tiến
> Ngày review: 2026-06-28  
> Phạm vi: `worker/` — luồng cập nhật dữ liệu tự động BigQuery  
> Nguồn: phân tích kỹ thuật nội bộ (data quality + operations)  
> Tài liệu gốc: `DAILY_DATA_PIPELINE.md` v2026-06-25

---

## Tóm tắt điều hành

Review toàn diện quy trình cập nhật dữ liệu tự động phát hiện **20 vấn đề** (5 HIGH, 8 MED, 4 MED-HIGH, 3 LOW). Các vấn đề nghiêm trọng nhất tập trung vào 3 cụm:

1. **Dữ liệu sai sau sự kiện corporate action** — cơ chế daily chỉ cập nhật 10 phiên gần nhất, không đủ để rebuild toàn bộ lịch sử sau khi giá được điều chỉnh.
2. **Dữ liệu tài chính bị lỗi đồng thời và thiếu versioning** — hai tiến trình có thể ghi đồng thời vào cùng file; BQ chỉ lưu 1 dòng mới nhất mỗi ticker, bỏ qua các revision.
3. **Trạng thái thị trường (DT5G) có thể bị đóng băng mà không có cảnh báo** — nếu pipeline EOD fail ở bất kỳ bước nào, bảng `vnindex_5state_dt5g_live` giữ nguyên ngày hôm trước trong 24 giờ mà hệ thống không phát hiện.

---

## Phần 1 — Lỗi dữ liệu (Data Quality)

### DQ-1 — Corporate action không rebuild toàn bộ lịch sử
**Mức độ:** HIGH  
**Thành phần:** `[D] process_stock_indicator`, `update_stock_adjust_price`

**Mô tả:**  
Mỗi ngày, pipeline chỉ merge 10 phiên gần nhất (`merged.tail(10)`) vào file `ticker_v1a/{ticker}.csv`. Khi xảy ra corporate action (tách/gộp cổ phiếu, cổ tức bằng cổ phiếu), nhà cung cấp VCI re-adjust toàn bộ lịch sử giá. Tuy nhiên, chỉ 10 dòng mới nhất được ghi đè — tạo ra **điểm gián đoạn giá tại dòng thứ 11** trở về trước.

**Ảnh hưởng:**  
Mọi chỉ số dùng cửa sổ dài đều bị sai kể từ ngày corporate action: MA10/20/50/200, RSI, MACD, CMF, CMB, VAP 1W/1M/3M, Support/Resistance 1Y, tỷ lệ giá ngắn hạn (C_L1W, C_L1M, T1W–T3M). Cả dữ liệu huấn luyện ML lẫn tín hiệu live đều bị nhiễm.

**Khuyến nghị:**  
Khi phát hiện thay đổi `outstanding_shares` (đã có cơ chế check), bắt buộc chạy lại `process_stock_indicator` với `daily_update=False, upload=True` (rebuild toàn bộ lịch sử) thay vì chỉ cập nhật tail(10). Thêm guard phát hiện jump tỷ lệ giá adjusted/unadjusted bất thường để tự động escalate rebuild.

---

### DQ-2 — Forward-fill NaN vào dòng live signal gây look-ahead leak
**Mức độ:** HIGH  
**Thành phần:** `[D] process_stock_indicator` (bước build app dataset)

**Mô tả:**  
Bước cuối của `process_stock_indicator` có logic: *"fill last row NaN từ row trước"* — forward-fill toàn bộ cột NaN của dòng mới nhất từ dòng ngày hôm trước. Các cột `profit_2W`, `profit_1M`, `profit_2M`, `profit_3M` (là dữ liệu tương lai — forward-looking) của dòng cuối luôn là NaN (chưa biết tương lai), nhưng sau khi forward-fill sẽ nhận giá trị **từ ngày hôm qua đã realized** — đây chính xác là cột look-ahead.

**Ảnh hưởng:**  
Dòng live signal (dòng mới nhất trong `ticker_v1a/`) mang giá trị `profit_*` đã thực hiện từ ngày trước. Nếu bất kỳ bộ lọc/scoring nào chạm đến cột này → leak thông tin tương lai vào quyết định hiện tại. Lỗi này được đẩy lên BQ qua bước [H] mỗi ngày.

**Khuyến nghị:**  
- Thay thế `fill last row NaN from previous row` bằng whitelist cột được phép forward-fill (chỉ các cột fundamental thực sự sticky: PE, PB, FSCORE...).
- Tuyệt đối không fill `profit_*` và bất kỳ cột forward-looking nào.
- Thêm assertion trước bước BQ append [H]: tất cả `profit_*` phải là NULL cho ít nhất 60 phiên gần nhất.

---

### DQ-3 — Unadjusted price (cafef) chỉ lấy ~20 phiên — gap nếu pipeline ngừng lâu
**Mức độ:** MED  
**Thành phần:** `update_stock_price`, `load_full_unadjust_price_history`

**Mô tả:**  
API cafef.vn chỉ trả về ~20 phiên giao dịch gần nhất mỗi lần gọi. Pipeline merge kết quả này với local cache (dedup theo ngày, keep last). Nếu pipeline bị ngừng hơn 20 phiên giao dịch (~4 tuần), khoảng trống giữa cuối cache và đầu cửa sổ mới không được lấp đầy.

**Ảnh hưởng:**  
Cột `Price` (unadjusted) bị lỗ trong khoảng thời gian đó → `Trading_Value` (Price × Volume) sai, VAP (volume-at-price) sai. Trường hợp nguy hiểm: sự cố kéo dài, DR failover.

**Khuyến nghị:**  
Khi khởi động lại sau khoảng ngắt dài, kiểm tra `max(time)` của local cache; nếu gap > 15 phiên → tự động đọc lại toàn bộ GCS partition (`daily_update=False`) thay vì dựa vào cửa sổ 20 phiên. Thêm freshness assert trước bước preprocess.

---

### DQ-4 — Delete-before-upload không atomic — mất file nếu upload fail
**Mức độ:** MED  
**Thành phần:** `update_stock_adjust_price` (daily path)

**Mô tả:**  
Để reset `blob.updated` timestamp (dùng bởi `update_stock_list` để xác định tickers có data mới hôm nay), pipeline **xóa** file `preprocess/adjusted_price/{ticker}.csv` trên GCS trước, sau đó upload lại. Nếu VCI API fail hoặc quá trình ghi bị gián đoạn → file đã bị xóa mà không có bản thay thế.

**Ảnh hưởng:**  
`compute_indicators` [D] không tìm thấy file adjusted_price của ticker đó → skip ticker → ticker không xuất hiện trong `ticker_v1a/` ngày hôm đó → `is_monitor=False` → ticker biến mất khỏi universe screening. Tự lành vào ngày hôm sau nhưng mất 1 ngày data.

**Khuyến nghị:**  
Bỏ cơ chế delete-to-bump-timestamp. Thay bằng một trong: (a) upload vào temp blob rồi atomic rename/copy sang target, (b) dùng custom GCS metadata để ghi ngày update, (c) tính `is_monitor` từ nội dung file (`max(time) == today`) thay vì `blob.updated`.

---

### DQ-5 — BQ financial sync chỉ 1 row/ticker — bỏ qua revision
**Mức độ:** MED-HIGH  
**Thành phần:** `[H] sync_bigquery_table_batch` (financial)

**Mô tả:**  
`update_bigquery_daily_append` sync financial với `latest_rows_per_ticker=1` — chỉ đẩy 1 dòng mới nhất mỗi ticker vào BQ. Nếu doanh nghiệp release revision (sơ bộ → kiểm toán) cho quý đã có trong BQ → revision bị bỏ qua vì đã có "dòng mới hơn". Nếu Q4 annual và quarterly release cùng tuần → chỉ đẩy 1 trong 2.

**Ảnh hưởng:**  
`tav2_bq.ticker_financial` lưu số liệu sơ bộ vĩnh viễn cho các quý đã restate. Backtests train/eval trên số không chính xác. Valuation signal (PE/PB/FSCORE/ROE) sai cho các quý bị revision.

**Khuyến nghị:**  
Tăng `latest_rows_per_ticker` lên 2–3 cho financial sync. Hoặc dùng cơ chế high-watermark (`ID_Release`) thay vì chỉ lấy N dòng mới nhất — phát hiện revision theo ID và re-upsert.

---

### DQ-6 — DT5G BQ sync chỉ tail 5 rows + thiếu freshness guard
**Mức độ:** MED-HIGH  
**Thành phần:** `[G] update_market_regime_state`, `get_gated_state()`

**Mô tả:**  
Pipeline [G] chỉ push 5 dòng cuối vào `vnindex_5state_dt5g_live`. Nếu pipeline miss >5 phiên → có gap thực sự trong bảng (không phải chỉ stale). Quan trọng hơn: `get_gated_state()` hiện check freshness của `macro_health.json` (feeds VIX/SPX/SBV) nhưng **không check freshness/continuity của chính bảng `dt5g_live`** — bảng có thể đang ffill-frozen mà không ai biết.

**Ảnh hưởng:**  
Trạng thái thị trường cũ → allocator V2.4 (`w_LAG` theo state: CRISIS 50%, BEAR 0%, NEUTRAL 65%) dùng regime sai → over/under allocation không có cảnh báo. Đây là root cause của incident ffill-frozen 2026-06-02.

**Khuyến nghị:**  
- Trong `get_gated_state()`: thêm check `max(time)` của `dt5g_live` — nếu lag > N phiên giao dịch → fail CLOSED sang DT4-only và fire Telegram alert.
- Mở rộng window BQ sync [G] từ 5 lên 15 dòng để tự heal miss ngắn.
- Thêm watchdog độc lập monitor `max(time)` drift của bảng này.

---

### DQ-7 — Không có barrier giữa pipeline() và financial report flow
**Mức độ:** MED  
**Thành phần:** `pipeline()`, `update_financial_reports()`

**Mô tả:**  
`update_financial_reports` chạy theo beat riêng (12:00 & 21:00) và `pipeline()` chạy qua cron riêng — hai luồng hoàn toàn độc lập, không có lock/sentinel. `pipeline()` đọc `preprocess/financial_report/*` tại thời điểm chạy, có thể đúng lúc financial flow đang ghi dở (một số tickers đã update quý mới, số khác chưa).

**Ảnh hưởng:**  
Trên ngày release báo cáo tài chính, compute_indicators [D] tính với snapshot không nhất quán: một nửa universe dùng số Q mới, nửa còn lại dùng số Q cũ → cross-sectional rating/screening bị lệch. Run 12:00 có thể trigger indicator recompute và BQ write trong giờ giao dịch từ data chưa đầy đủ.

**Khuyến nghị:**  
- Gate `do_report.sh` (pipeline trigger) sau khi financial flow 21:00 có done-marker/sentinel.
- Viết file tạm khi financial preprocess (`{ticker}.csv.tmp`) rồi atomic rename → không bao giờ có file nửa vời.
- Không trigger indicator recompute và BQ write trong giờ giao dịch (trước 15:00 ICT).

---

### DQ-8 — Chưa xác nhận Release_Date gating cho fundamentals (nguy cơ look-ahead)
**Mức độ:** MED-HIGH  
**Thành phần:** `compute_fa_indicator_v2` trong `process_stock_indicator`

**Mô tả:**  
Dữ liệu tài chính được lưu theo `quarter={year}Q{n}` và join vào ticker theo `(ticker, time)`. Chưa có xác nhận rằng `compute_fa_indicator_v2` stamp các chỉ số tài chính (PE, PB, ROE, FSCORE...) từ ngày `Release_Date` thực tế, thay vì từ ngày kết thúc quý (`quarter_end`). Nếu dùng `quarter_end`, fundamentals xuất hiện trong indicator series **trước khi thị trường biết**.

**Ảnh hưởng:**  
Look-ahead leak trong toàn bộ backtest có điều kiện fundamentals: 8L valuation rating, V2.4 LAG book (PEAD), bất kỳ filter nào dùng PE/PB/FSCORE/ROE. Kết quả backtest bị inflate.

**Khuyến nghị:**  
**Ưu tiên verify ngay**: kiểm tra code `compute_fa_indicator_v2` — xác nhận dùng `ID_Release` hoặc `Release_Date` làm ngưỡng visibility, không dùng `time` (quarter end). Nếu chưa có PIT gating → re-derive series và re-audit các backtest liên quan.

---

### DQ-9 — Duplicate rows trong risk_rating có thể chưa được dedup
**Mức độ:** MED  
**Thành phần:** `update_risk_indicators`, `process_stock_indicator`

**Mô tả:**  
Bảng `tav2_bq.risk_rating` có duplicate rows (cùng ticker + quarter xuất hiện 2 lần — đã ghi nhận trong KB). `update_risk_indicators` đọc từ đây để tạo `preprocess/others/risk_indicators.csv` — input của `process_stock_indicator`.

**Ảnh hưởng:**  
Nếu không áp GROUP BY / DISTINCT khi đọc, Beta và Deviation bị double-count hoặc tính trung bình sai → `Risk_Rating` composite không chính xác → sizing gated theo risk bị lệch.

**Khuyến nghị:**  
Xác nhận `update_risk_indicators` có dedup `(ticker, quarter) keep-last` trước khi ghi `risk_indicators.csv`. Thêm assertion: mỗi ticker chỉ có 1 dòng trong output.

---

### DQ-10 — Nhầm bảng vnindex_5state vs vnindex_5state_dt5g_live
**Mức độ:** LOW  
**Thành phần:** Consumer scripts (research/backtest)

**Mô tả:**  
Bảng `tav2_bq.vnindex_5state` (không suffix) là **v3.4b BASE** (~153 transitions), không phải DT5G production (~49 transitions). Pipeline [G] ghi đúng vào `vnindex_5state_dt5g_live`. Nhưng research/backtest scripts có thể đọc bảng không suffix và nhầm đây là DT5G.

**Ảnh hưởng:**  
Phân phối CRISIS và EX-BULL khác nhau đáng kể (v3.4b: CRISIS 748 ngày, EX-BULL 194 ngày; DT5G: CRISIS 525, EX-BULL 59) → condition trên regime state cho kết quả khác nhau giữa research và production.

**Khuyến nghị:**  
Không cần thay đổi pipeline. Rà soát tất cả scripts có đọc `vnindex_5state` — redirect sang `vnindex_5state_dt5g_live` hoặc dùng `get_gated_state()`. Cân nhắc đổi tên bảng không suffix để giảm nhầm lẫn.

---

## Phần 2 — Vấn đề vận hành (Operations)

### OPS-1 — Không có monitoring cho pipeline EOD
**Mức độ:** HIGH  
**Thành phần:** `pipeline()`, `cron/do_report.sh`

**Mô tả:**  
`pipeline()` không có Celery beat trigger — chỉ chạy qua cron shell bên ngoài. Không có heartbeat, completion signal, hay failure alert. Nếu cron chết hoặc fail silent → toàn bộ EOD bị skip mà không ai biết → dẫn trực tiếp đến DQ-6 (DT5G ffill-frozen).

**Khuyến nghị:**  
Thêm Telegram alert: nếu không nhận được "pipeline done" signal trước 20:00 ICT mỗi ngày giao dịch → alert ngay. Thêm heartbeat từng bước lớn (A/D/G/H) để biết pipeline đang ở đâu nếu chậm.

---

### OPS-2 — Financial report 2 instance chạy đồng thời, không có lock
**Mức độ:** HIGH  
**Thành phần:** `update_financial_reports()`, Celery beat

**Mô tả:**  
Beat 12:00 & 21:00 mỗi ngày đều spawn `update_financial_reports`. Với ~1270 tickers × sleep(3) ≈ 63 phút baseline — nếu VCI API chậm và retry (2 lần × countdown 120s), run 12:00 có thể chưa xong khi 21:00 start. Celery không mặc định ngăn 2 instance cùng task.

**Ảnh hưởng:**  
2 instance ghi đồng thời vào `preprocess/financial_report/{ticker}.csv` → file có thể bị corrupt. Double API call → nguy cơ bị rate-limit hoặc ban IP bởi VCI.

**Khuyến nghị:**  
Thêm Redis-based task lock (`one_at_a_time` pattern) cho `update_financial_reports`. Đặt `hard time_limit` hợp lý. Xem xét chỉ giữ lại beat 21:00 (sau market close) và bỏ 12:00 nếu không cần intraday.

---

### OPS-3 — BQ financial sync bỏ qua multiple release trong cùng tuần
**Mức độ:** HIGH  
**Thành phần:** `update_bigquery_daily_append`, `sync_bigquery_table_batch` (financial)

*(Xem chi tiết tại DQ-5 — cùng vấn đề, góc ops)*  
Mùa báo cáo Q4: doanh nghiệp release Q4 thường + annual cùng tuần. `latest_rows_per_ticker=1` chỉ đẩy 1 trong 2 lên BQ. Taylor query BQ miss financial data → valuation signal sai ngay trong mùa earnings quan trọng nhất.

---

### OPS-4 — Joblib disk cache không TTL, không invalidate sau deploy
**Mức độ:** MED  
**Thành phần:** `compute_indicators`, `/tmp/joblib_cache/`

**Mô tả:**  
Cache expensive computation tại `/tmp/joblib_cache/{user}/` không có TTL và không tự xóa sau restart thông thường. Nếu deploy thay đổi thuật toán chỉ số, cache cũ vẫn được serve.

**Khuyến nghị:**  
Version cache path theo code hash (`/tmp/joblib_cache/{version_hash}/`), hoặc thêm post-deploy hook `rm -rf /tmp/joblib_cache/` trước khi restart worker.

---

### OPS-5 — Breadth beat 03:00 race với EOD pipeline chạy muộn
**Mức độ:** MED  
**Thành phần:** `aggregate_market_data` (beat 03:00), `compute_indicators` [D]

**Mô tả:**  
Beat 03:00 T2-T6 đọc `ticker_v1a/` để tính market breadth. Nếu pipeline EOD chạy muộn (queue backlog, sau nửa đêm), 03:00 đọc `ticker_v1a/` đang được ghi bởi [D] đang chạy.

**Ảnh hưởng:**  
`market_indicators_all_tickers.csv` tính từ universe chưa đầy đủ → DT5G breadth-decoupling guard (Pillar B suppression) dùng breadth sai → có thể miss US-VN decoupling hoặc false-suppress US panic cap.

**Khuyến nghị:**  
Beat 03:00 kiểm tra pipeline completion flag trước khi chạy. Hoặc thêm file lock trên `ticker_v1a/` trong suốt quá trình pipeline [D] ghi.

---

### OPS-6 — update_us_market fail silent, DT5G Pillar B dùng VIX T-2
**Mức độ:** MED  
**Thành phần:** `update_us_market()` (beat 15:00), DT5G Pillar B

**Mô tả:**  
`update_us_market` chạy lúc 15:00 ICT (08:00 EST, US chưa mở) nên lấy data US T-1 — đây là thiết kế đúng. Nhưng nếu yfinance fail (max_retries=2, countdown=20s) → không có alert, EOD pipeline dùng data T-2. Thứ Hai cần xử lý gap cuối tuần (Friday close).

**Ảnh hưởng:**  
DT5G Pillar B VIX/SPX gate dùng data cũ 2 ngày → miss VIX spike nhanh, state không cap xuống CRISIS kịp. Đặc biệt nguy hiểm cuối tuần/nghỉ lễ Mỹ.

**Khuyến nghị:**  
Alert Telegram nếu `us_market_history.csv` không refresh sau 15:30 ICT. Thêm fallback source (FRED, alpha vantage). Xử lý đặc biệt cho T2 (Monday) với weekend gap.

---

### OPS-7 — DT5G BQ publish là bước cuối — fail upstream = freeze silent 24h
**Mức độ:** MED  
**Thành phần:** `pipeline()` step [G], `vnindex_5state_dt5g_live`

**Mô tả:**  
Bước [G] publish DT5G lên BQ là bước cuối cùng trong pipeline(). Bất kỳ fail nào ở bước A–F sẽ khiến pipeline dừng trước khi đến [G] → `vnindex_5state_dt5g_live` giữ nguyên ngày hôm qua → cả fleet đọc regime cũ trong 24h mà không có cảnh báo. `get_gated_state()` fallback DT4-only sau 1440 phút nhưng transition này SILENT.

**Lưu ý:** Đây là root cause của incident 2026-06-02.

**Khuyến nghị:**  
- Sau mỗi pipeline run, chạy explicit check: so sánh `max(time)` của `vnindex_5state_dt5g_live` với today.
- Alert Telegram ngay nếu lệch trước 19:00 ICT ngày giao dịch.
- Đây là check CRITICAL cần được thêm trước go-live.

---

### OPS-8 — Local price cache không TTL, không checksum
**Mức độ:** MED  
**Thành phần:** `load_full_unadjust_price_history`, local cache

**Mô tả:**  
`$GCS_LOCAL_PATH/local/price/{ticker}.csv` không có cơ chế expire hay validate. Data lịch sử trong cache không bao giờ được re-check với GCS.

**Khuyến nghị:**  
Thêm periodic validation (weekly): so sánh row count / checksum với GCS partition. Hoặc max-age 30 ngày forcing rebuild từ GCS nguồn.

---

### OPS-9 — update_stock_list không có lock, hai nơi gọi với params khác nhau
**Mức độ:** LOW  
**Thành phần:** `update_stock_list`, pipeline [E], beat 02:00 Chủ Nhật

**Mô tả:**  
Chạy tại pipeline [E] (`update_skip=False`) và beat Chủ Nhật 02:00 (`update_skip=True`). Timing xa nhau nên hiếm overlap, nhưng nếu EOD pipeline chạy muộn qua đêm Chủ Nhật → last-writer-wins trên `ticker_list.csv`.

**Khuyến nghị:**  
Thêm Redis lock defensive để ngăn concurrent execution. Rủi ro thấp với timing hiện tại.

---

### OPS-10 — Có thể mismatch tên file market_indicators (legacy vs new)
**Mức độ:** LOW  
**Thành phần:** `process_stock_indicator` [D], `aggregate_market_data`

**Mô tả:**  
Doc ghi `process_stock_indicator` đọc `preprocess/others/market_indicators.csv` (tên cũ), nhưng `aggregate_market_data` ghi ra `market_indicators_all_tickers.csv` (tên mới). Nếu code vẫn đọc tên cũ → đọc file legacy/rỗng.

**Khuyến nghị:**  
Verify path thực tế trong `data_tasks.py:637`. Nếu mismatch → update reference. Doc có thể đã outdated.

---

## Phần 3 — Ma trận ưu tiên

| # | Issue | Mức | Ảnh hưởng chính | Deadline |
|---|---|---|---|---|
| DQ-6 / OPS-7 | DT5G ffill-frozen silent | HIGH | Go-live risk: regime sai → sizing sai | **Trước 2026-06-30** |
| OPS-1 | Không có monitoring EOD | HIGH | Prerequisite để phát hiện mọi lỗi khác | **Trước 2026-06-30** |
| DQ-2 | profit_* forward-fill vào live row | HIGH | Look-ahead vào live signal + BQ | **Trước 2026-06-30** |
| DQ-8 | Release_Date PIT chưa verify | MED-HIGH | Look-ahead trong mọi backtest FA | **Verify ngay** |
| OPS-2 | Financial report concurrent write | HIGH | Data corruption ticker_financial | Ngay sau go-live |
| DQ-1 | Corp action không rebuild | HIGH | MA/RSI/MACD sai sau split | Ngay sau go-live |
| DQ-5 / OPS-3 | BQ financial 1 row/ticker | MED-HIGH | Miss revision + Q4 double release | Ngay sau go-live |
| DQ-4 | delete-before-upload non-atomic | MED | Drop ticker 1 ngày khi VCI fail | Q3 2026 |
| DQ-7 | Không có ordering barrier pipeline/financial | MED | Snapshot không nhất quán ngày release | Q3 2026 |
| OPS-5 | Breadth 03:00 race với EOD muộn | MED | DT5G Pillar B breadth sai | Q3 2026 |
| OPS-6 | US market fail silent | MED | VIX T-2 trong DT5G Pillar B | Q3 2026 |
| OPS-4 | Joblib cache không TTL | MED | Indicator sai sau deploy | Q3 2026 |
| DQ-3 | cafef ~20 phiên | MED | Gap unadjusted price nếu miss >20 ngày | Q3 2026 |
| DQ-9 | risk_rating dup rows | MED | Beta/Risk_Rating sai | Verify + fix |
| OPS-8 | Local price cache không TTL | MED | Cache stale dài hạn | Q4 2026 |
| OPS-9 | update_stock_list không lock | LOW | Race condition hiếm gặp | Q4 2026 |
| DQ-10 | Nhầm bảng vnindex_5state | LOW | Research scripts dùng BASE thay DT5G | Document |
| OPS-10 | market_indicators filename | LOW | Breadth context trong indicator | Verify |

---

## Phần 4 — Các fix nhanh (< 1 ngày engineering)

Những thay đổi nhỏ có thể thực hiện ngay để giảm rủi ro trước go-live:

1. **Thêm freshness check vào `get_gated_state()`**: 3–5 dòng Python — so `max(time)` của `dt5g_live` với today, fail CLOSED nếu lag > 2 ngày.

2. **Block `profit_*` khỏi NaN forward-fill**: Thêm danh sách `FORWARD_COLUMNS = ["profit_2W", "profit_1M", "profit_2M", "profit_3M", ...]` và exclude khỏi fillna.

3. **Telegram alert "pipeline không done"**: Script shell đơn giản check completion file + notify.sh, thêm vào cron sau `do_report.sh`.

4. **Mở rộng DT5G BQ sync window**: Đổi `tail 5` thành `tail 15` trong [G] — 1 dòng config.

---

*File này được tổng hợp từ kết quả phân tích của Taylor (data quality) và Winston (operations) ngày 2026-06-28.*
