# AUDIT THỨ TỰ CRON TOÀN HỆ THỐNG — 2026-07-12 (job Winston_20260712_142100)

> Phương pháp: đọc CODE THẬT từng script (không tin comment), grep consumer toàn repo,
> đối chiếu log chạy thật + query live BQ. Mọi claim quan trọng đều có file:line hoặc log/BQ evidence.
> KHÔNG sửa gì — audit + đề xuất, Mike/user quyết.

## PHẦN 0 — PHÁT HIỆN KHẨN (không thuần ordering, nhưng audit chuỗi 18:30→19:00 lộ ra)

### C1 🔴 CRITICAL — publish DT5G đọc qua BQ_LOCAL_CACHE (T-1) → thứ Hai 07-13 19:00 SẼ BLOCK DollarBill
**Cơ chế (verify từng mắt xích):**
- `wc_env.sh:7` export `BQ_LOCAL_CACHE=data/bq_cache` (vào repo ~2026-06-25, commit 366b922).
- `daily_refresh_v34b_linux.sh:20` source `wc_env.sh` → mọi step con thừa hưởng env này.
- `macro_state_live.py:87,264` dùng `from simulate_holistic_nav import bq`; `simulate_holistic_nav.py:191-201`
  route MỌI query qua DuckDB cache khi env set. Comment trong chính `get_macro_state` nói
  "SOURCE OF TRUTH = BigQuery… NOT a local CSV" — ý định đọc live, nhưng env global đã âm thầm
  chuyển hướng sang cache từ ~06-25.
- Cache sync 23:45 đêm trước → lúc publish chạy (18:30 và 19:00) cache luôn là **T-1**.
  → `vnindex_5state_dt5g_live` luôn được publish TRỄ ≥1 phiên, dù base `v34b_clean` vừa được
  ghi live tới ngày T ngay trước đó trong cùng script.

**Bằng chứng log/BQ (không phải suy luận):**
- `data/refresh_v34b_linux_2026-07-09.log:351-362`: `[BQ_LOCAL_CACHE] ready — 13 tables` →
  `WARNING: BQ base state max=2026-07-08 < requested end=2026-07-09 → base is STALE` →
  `wrote … -> 2026-07-08`; cùng log in `_v34b_clean max=2026-07-09  dt5g_live max=2026-07-08`.
- `mike/logs/bq_freshness.log` 07-10 19:00: pipeline-1 `wrote … 2014-01-02 -> 2026-07-09`,
  `as_of=2026-07-09` — plan thứ Hai đã lập trên state 07-09 (team ĐÃ biết vụ này, đã siết gate).
- Live BQ query 2026-07-12: `dt5g_live max=2026-07-09`, `v34b_clean max=2026-07-09`,
  `ticker_prune max=2026-07-10` → dt5g hiện trễ 1 phiên so với giá.

**Vì sao thứ Hai chắc chắn block:** `MAX_STATE_LAG=0` (commit 3feed6f, 07-11 — siết đúng ý định
"lag≥1 là bất thường"). Thứ Hai 18:30 daily_refresh ghi base live tới 07-13, nhưng publish đọc
cache (v34b_clean trong cache = **07-09**, vì thứ Sáu daily_refresh 18:30 không chạy — xem C1b) →
dt5g publish tới 07-09. 19:00 check: gap trading-day 07-09→07-13 = 2 > 0 → **FAIL, exit 1,
KHÔNG chạy pipeline, KHÔNG dispatch DollarBill** → thứ Ba không có plan → preflight RED.
Kể cả trường hợp đẹp nhất (cache tươi T-1 = 07-10) gap vẫn = 1 > 0 → **với MAX_STATE_LAG=0,
publish-đọc-cache KHÔNG BAO GIỜ pass** — gate mới và bug cache là mâu thuẫn cấu trúc.

**Đề xuất fix (Mike quyết, chạm code ngoài scope Winston):** cho `publish_gated_state.py`
(và riêng step [12]/[13] của daily_refresh + pipeline-1 của bq_freshness_check) chạy với
`env -u BQ_LOCAL_CACHE` (hoặc unset trong chính publish_gated_state trước import) — publish
production state PHẢI đọc live. **Deadline: trước 18:30 thứ Hai 07-13.** Sau fix, mục chờ
"xác nhận dt5g có dòng 07-10/07-13" trong current_ops mới có thể PASS (07-10 sẽ vẫn thiếu
trong bảng cho tới khi replay/refresh bù — cần kiểm tra sau fix).

### C1b — Thứ Sáu 07-10 daily_refresh 18:30 KHÔNG chạy
Không có `data/refresh_v34b_linux_2026-07-10.log`; live `v34b_clean max=07-09`. Khớp comment
trong bq_freshness_check.sh:34-42 ("daily_refresh 18:30 miss" tối 07-10) — nguyên nhân khả dĩ:
crontab đổi giờ 23:15→18:30 trong ngày 07-10 sau 18:30, nên hôm đó rơi vào khe không lịch nào
chạy. Không tự lặp lại, nhưng để lại cache v34b_clean=07-09 làm C1 nặng thêm (gap 2 thay vì 1).
Bài học cho quy tắc: **đổi giờ cron trong ngày → phải chạy tay bù lần bị nhảy khe.**

### H2 🟠 HIGH — check `shares_outstanding_live` (BLOCK, lag≤2) calibrate trên giả định sai → false-BLOCK ~thứ Tư 07-15
`bq_freshness_check.sh:47-49` ghi "writer corp_action chạy ~17:44 ICT daily". SAI: cron
`update_shares_live.sh` 18:40 chỉ chạy `--scan` = detection-only, `main()` return TRƯỚC mọi MERGE
(`update_shares_live.py:449-450`; MERGE chỉ ở `process()`/`ack_cash()` = chạy TAY). Grep toàn repo:
không writer nào khác. `updated_at=07-10 17:44` mà 07-11 dùng để calibrate là 1 lần xử lý corp-action
THỦ CÔNG tình cờ. → nếu không có corp-action nào được xử lý tay, lag vượt 2 trading days vào
**thứ Tư 07-15 → block oan toàn bộ pipeline 19:00 + DollarBill**.
Đề xuất: hạ check này BLOCK→WARN, hoặc đổi metric sang "scan-alive" (mtime `data/shares_scan_*.log`
/ bus heartbeat của scan) — vì cadence thật của `updated_at` là event-driven, không phải daily.

## PHẦN 1 — VERDICT các chuỗi phụ thuộc chính (mục 2 của đề bài)

| Chuỗi | Thứ tự cron | Verdict |
|---|---|---|
| daily_refresh 18:30 → bq_freshness 19:00 → send_plan 21:00 | ĐÚNG thứ tự | ✅ order đúng, ❌ nội dung bị C1 xuyên thủng (state publish T-1 bất kể order). 19:00 check đọc live BQ (không cache) ✅; verify artifact plan (đúng `plan_date`=next_trading_day + field `orders`, chọn theo mtime — `send_plan_report.sh:35-74`) ✅. Buffer 19:00→21:00 = 2h cho DollarBill: hợp lý, có escalation thật khi thiếu. |
| sync_bq_cache 23:45 → consumer cache | ĐÚNG cho mọi consumer HỢP LỆ | ✅ 06:00 newdeals, 08:52 paper probe, 15:05 dc_book, 15:20 paper report: đều cần T-1 close → cache đúng semantics. ❌ Consumer cache ẨN không hợp lệ: publish_gated_state (C1). ⚠️ Cuối tuần không sync → refresh fa_ratings* sáng thứ Bảy chỉ vào cache tối thứ Hai 23:45 (consumer cache chạy thứ Hai vẫn thấy bản cũ; consumer live-BQ thấy ngay). |
| fleet_backup 00:00 → daily_retro 00:30 → kb_nightly 02:00 | ĐÚNG | ✅ backup sau sync (23:45+~8'), retro đọc events NGÀY HÔM QUA trọn vẹn (không job nào ghi data ngày N sau 00:30). Lưu ý thiết kế: backup GitHub KHÔNG chứa data/execution_logs/bq_cache/bus thô (gitignore *.csv/*.jsonl/*.parquet/secrets) — DR = code+KB only, NAV history/journal chỉ tồn tại trên host này. |
| refresh_fa_ratings_8l 08:30 Sat → refresh_fa_ratings 09:15 Sat | ĐÚNG, KHÔNG chồng chéo | ✅ BQ artifacts disjoint (tmp_r8l_refresh+fa_ratings_8l vs fa_ratings_refresh_staging+fa_ratings), file local disjoint, cùng đọc-chỉ ticker_financial + CLOUDSDK_CONFIG (an toàn concurrent). Runtime thật đo 07-12: cả 2 xong trong ~2' mỗi cái → gap 45' dư rộng. |

## PHẦN 2 — Xung đột tài nguyên (mục 3): KHÔNG tìm thấy xung đột cứng nào mới

Đã soi có chủ đích, kết quả:
- `dnse_raw_{date}.jsonl`: file mutable dùng chung duy nhất trong ngày (bot SpaceX + ZaloPay +
  daily_nav_snapshot cùng append) — append-only JSONL, mọi record đã tag account từ fix 07-06
  (`brokers.py:150-159`) → an toàn. Paper main dùng file khác (`phs_raw_*.jsonl`).
- 15:00 eod / 15:05 dc_book / 15:20 paper report: bộ file hoàn toàn disjoint; dc_book chạy ~2s
  (đo mtime state 15:05:01.96), idempotent theo data_date nên 15:20 gọi lại `--section` chỉ
  read-only nếu 15:05 đã advance — phụ thuộc MỀM đúng thiết kế.
- rubber_weekly 18:35: không đụng BQ, không đụng file nào của daily_refresh — lần dời 18:30→18:35
  chỉ là né trùng phút CPU/network, không phải data conflict (giữ nguyên, đúng).
- Dual-writer benign (tuần tự, không đồng thời): `macro_health.json` + `us_market_history.csv`
  (papertrade 15:30 và daily_refresh 18:30); `dt5g_live`+`golive_state_today.json` (daily_refresh
  18:30 và pipeline-1 19:00 — cùng script publish, redundant nhưng vô hại; SAU khi fix C1 nên giữ
  cả 2 vì 19:00 là lưới đỡ nếu 18:30 miss như 07-10).
- kb_nightly 02:00 rewrite `events_buffer.md` KHÔNG lấy `locks/consolidator.lock` mà consolidate
  (hourly :07 + mọi dispatch xong) giữ — race window mili-giây, xác suất thấp; fix rẻ = flock cùng lock.
- OTP lock/exec lock per (account,date) đúng; pkill lunch pattern đã fix 07-06; heartbeat có grace
  window 09:00-09:10/13:00-13:10 tránh đá nhầm bot vừa khởi động.

## PHẦN 3 — Các phát hiện phụ (ngoài ordering nhưng audit lộ ra, xếp theo mức độ)

- **M5 (đụng deadline 07-14)**: `trading_bot/executor.py:507` đọc monolith
  `data/bq_cache/ticker_prune.parquet` — file này chết cứng từ **06-26** (sync đã chuyển
  ticker_prune sang thư mục chunked `ticker_prune/`, monolith không ai ghi nữa; ls xác nhận mtime
  Jun 26). Live account không ảnh hưởng (3 flag đều False → early-return), nhưng **paper main
  (EXTREME + chase-cap trials) đang tính prior_close/rvol_20d trên giá cũ 2+ tuần** — gap so giá
  cũ dễ trượt guard ±15% → fail-safe None → logic không bao giờ fire → evidence paper cho review
  chase-cap (~07-14) và EXTREME (~07-28) có thể vô giá trị. Cần Taylor xác nhận + fix path
  (glob `ticker_prune/*.parquet` hoặc `ticker_1m.parquet`) rồi đánh giá lại evidence đã tích.
- **M4**: `sync_bq_cache_daily.sh:12` — `PREFLIGHT_OUT=$(python3 preflight_bq_cache.py 2>&1)`
  thiếu `|| true` dưới `set -euo pipefail` → khi preflight exit≠0 (đúng kịch bản verify FAIL mà
  block notify/ops_autofix phía dưới sinh ra để bắt), wrapper chết TRƯỚC khi kịp notify → lời hứa
  tự-phát-hiện 07-07 bị hổng đúng chỗ cần nhất. Fix 1 token.
- **M3 (ordering thật, mức đề xuất)**: `pt_8l_daily` 17:45 (`rating_8l.py:709`, `cheap_pb_floor.py:65`)
  và `telegram_run_daily` 18:00 (`telegram_recommend.py:104`) đọc `dt5g_live` TRƯỚC refresh 18:30
  → luôn báo regime của hôm trước (hiện tại còn T-2 vì C1). Di sản từ thời refresh chạy 23:15
  (khi đó T-1 là bất khả kháng); nay refresh đã dời lên 18:30 thì có cơ hội cho user regime same-day.
  Đề xuất (sau khi C1 fix, user quyết vì đổi giờ report user-facing): dời `pt_8l_daily` → ~19:15
  và `telegram_run_daily` → ~19:30 (sau pipeline 19:00, tiện thể đọc luôn recommendations mới
  cùng ngày thay vì bản hôm qua — `telegram_recommend.py:556-574` đang đọc `golive_v23_status.json`
  của tối hôm trước). Nếu user thích giữ giờ 18:00 → chấp nhận + ghi rõ trong report "regime as-of hôm qua".
- **L6a**: `kb_nightly.sh:119` gọi `mike/bin/backup.sh` KHÔNG tồn tại (log xác nhận "No such file",
  nuốt bởi `|| true`) — dead step, trim 02:00 chỉ lên GitHub ở fleet_backup 00:00 hôm sau.
- **L6b**: `preflight_bq_cache.py` EXPECTED_TABLES = 12, thiếu `custom30_8l` (bảng thứ 13 thêm 07-06).
- **L6c**: preflight/plan-date quanh nghỉ lễ: cron chạy Mon-Fri bất kể lễ; `vn_market.py` chỉ có
  lễ dương lịch cố định (Tết chưa encode) → ngày lễ giữa tuần sẽ RED giả buổi sáng (vô hại nhưng ồn)
  và next_trading_day có thể sai quanh Tết. Ghi nhận, xử khi gần Tết.
- **L6d — comment lỗi thời phát hiện qua audit** (đúng cảnh báo đề bài): header
  `sync_bq_cache_daily.sh` nói "runs after BQ data ingest (~23:15)" (ingest thật có mặt trước
  ~17:30 — evidence: 17:30 run 07-10 đã thấy đủ 07-10); header daily_refresh nói "after ~22:30
  ingest" (cũ); `bq_freshness_check.sh:47` "writer ~17:44 daily" (sai — xem H2); watchdog header
  "notify none shipped" (đã ship); kb_nightly header nói trim KNOWLEDGE.md (thật ra events_buffer.md);
  prompt daily_retro còn ghi "22:00 ICT" (giờ 00:30).
- **Ghi nhận không cần làm gì**: feed write-only chưa có consumer (`vcb_fx_rate.csv`,
  `iron_ore/urea/dap_monthly.csv`) — archive cho research tương lai, hợp lệ; quota participation
  2 live bot là 2 process riêng nên KHÔNG share runtime (docstring nói single-process — đúng chữ,
  dễ hiểu nhầm); run_bot sáng bị double-log (cron `>>` + `tee -a` cùng file, cosmetic).

## PHẦN 4 — Đề xuất reorder cụ thể (mục 4)

**Về THỨ TỰ thuần: hệ thống hiện sắp xếp ĐÚNG — không có lỗi thứ tự nào cần đảo.** Các vấn đề tìm
thấy là bug NỘI DUNG (C1/H2/M4/M5) hoặc cơ hội cải thiện tự chọn (M3). Cụ thể:
1. KHÔNG đổi giờ job nào để chữa C1/H2 — chữa bằng code (unset cache cho publish; đổi metric check
   shares) chứ không phải bằng reorder.
2. M3 là đề xuất reorder DUY NHẤT: pt_8l_daily 17:45→~19:15, telegram 18:00→~19:30 (điều kiện:
   C1 đã fix; user duyệt vì đổi giờ báo cáo user-facing). Lợi: regime + recommendations same-day.
   Không đổi cũng chạy đúng như 3 tuần qua (semantics T-1).
3. Giữ nguyên: rubber 18:35, fa_ratings Sat 08:30/09:15, chuỗi đêm 23:45/00:00/00:30/02:00,
   khối trading sáng/chiều — đã audit kỹ, không tìm thấy lỗi thứ tự.

## PHẦN 5 — BẢN THẢO QUY TẮC: "Thêm cron mới đặt giờ nào?" (mục 5 — draft để Mike review)

### 5.1 Bốn câu hỏi bắt buộc trả lời TRƯỚC khi chọn giờ (ghi câu trả lời vào registry — xem 5.4)
1. **ĐỌC gì, vintage nào?** Liệt kê từng nguồn và phân loại:
   - BQ **live** (bq CLI / SDK trực tiếp)
   - BQ **local cache** `data/bq_cache/` — luôn là **T-1**, sync 23:45 T2-T6, KHÔNG sync cuối tuần.
     ⚠️ Cache có thể ẨN: mọi script source `wc_env.sh` VÀ đi qua `simulate_holistic_nav.bq` /
     `bq_local_cache` là consumer cache dù code không nhắc chữ "cache" — phải grep CHUỖI IMPORT,
     không chỉ grep tên biến (bài học C1: publish_gated_state tưởng đọc live suốt ~2.5 tuần).
   - **DNSE live API** (giá/positions same-day — bắt buộc cho MTM cùng ngày, xem coding_guidelines §6)
   - **File local** — ghi rõ AI ghi file đó, LÚC NÀO, và điều gì xảy ra nếu nó cũ (staleness check?)
   - **Web/external** — có retry chưa, tổng thời gian retry tối đa bao lâu (ảnh hưởng slot).
2. **Nguồn đó TƯƠI lúc nào trong ngày?** Mốc đã đo thật (2026-07): BQ ticker/ticker_prune ingest
   same-day có mặt ≤~17:30 ICT; DT5G tươi sau daily_refresh 18:30 (khi publish đọc live);
   recommendations/plan tươi sau pipeline 19:00; cache tươi-T-1 sau 23:45. KHÔNG dùng mốc trong
   comment cũ — comment đã sai nhiều lần; đo lại bằng log/query khi nghi ngờ.
3. **Job cần dữ liệu T hay T-1?** T-1 là ĐÚNG semantics cho planning-trước-mở-cửa và paper
   report → cache OK, chạy giờ nào cũng được miễn sau 23:45 đêm trước. Cần T (regime EOD, MTM
   same-day, freshness gate) → BẮT BUỘC nguồn live VÀ chạy SAU mốc nguồn có T.
4. **AI tiêu thụ output, deadline của họ?** Vẽ 1 dòng chuỗi: job → consumer → deadline cuối
   (thường là preflight 08:45 sáng hôm sau). Consumer là job cron khác → xem 5.3 buffer.

### 5.2 Tránh xung đột tài nguyên
- Liệt kê mọi file/bảng job GHI; grep repo tìm writer khác cùng đích. Có ≥2 writer → hoặc
  atomic write (tmp + `os.replace` — mẫu: `daily_nav_snapshot.py`, `dc_book_waterfall_paper.py`),
  hoặc append-only + tag nguồn (mẫu: `dnse_raw` sau fix 07-06), hoặc tách giờ và ghi rõ lý do.
- File đọc-sửa-ghi lại (kiểu events_buffer.md) → flock cùng lock với writer khác (mẫu:
  `consolidate.sh` `locks/consolidator.lock`).
- Không đặt 2 job nặng CPU/network trùng phút — lệch tối thiểu 5' (tiền lệ rubber 18:30→18:35).
- pkill trong cron: pattern phải không tự khớp (`[b]ot_execute` — bài học 07-06).

### 5.3 Buffer giữa job phụ thuộc — nguyên tắc "buffer + VERIFY ARTIFACT, không tin giờ"
- Buffer tối thiểu = runtime upstream ĐO THẬT (worst-case gồm retry: daily_refresh precheck tới
  ~90'; rubber retry ~12'; telegram retry ~32') + ≥10' dự phòng. Đo bằng log thật, không đoán.
- Nhưng buffer KHÔNG BAO GIỜ là bảo chứng duy nhất: downstream production phải verify artifact
  (mtime, ngày trong file, `MAX(time)` BQ) trước khi dùng — mẫu đúng đang chạy:
  `send_plan_report.sh` verify `plan_date`; `bq_freshness_check` verify `MAX(time)` từng bảng;
  daily_refresh [8b] mtime-assert intermediates. Job mới nối vào chuỗi production → bắt buộc có
  bước verify tương đương, và nếu đọc bảng BQ mới → thêm dòng `_check` vào `bq_freshness_check.sh`
  (WARN trước, nâng BLOCK sau khi **calibrate ngưỡng bằng cadence THẬT của writer** — query lịch
  sử nhiều lần chạy, không calibrate trên 1 điểm dữ liệu tình cờ; bài học H2 shares_outstanding).
- Publish bảng production (regime/giá/plan) PHẢI đọc nguồn live — chạy với `env -u BQ_LOCAL_CACHE`
  nếu import chain có thể dính cache (bài học C1).

### 5.4 Ghi lại ở đâu (để job sau không phá thứ tự mà không biết)
- **Comment crontab**: giờ ICT + 1 dòng "sau X vì Y, trước Z vì W" + ngày đổi + commit (mẫu tốt
  đang có: dòng daily_refresh "doi tu 23:15, 2026-07-10 - xem commit 1a3ea5c").
- **Registry trung tâm — đề xuất file mới `mike/kb/cron_registry.md`** (data_registry.md hiện là
  chuyện vintage bảng, không phải lịch): mỗi job 1 dòng: `giờ ICT | script | đọc (nguồn+vintage
  T/T-1) | ghi | consumer | buffer/depends-on | verify-artifact nào`. Cập nhật CÙNG COMMIT với mọi
  thay đổi crontab. Bảng trong audit này có thể làm seed v1.
- **Khi ĐỔI giờ 1 job**: grep registry tìm mọi upstream/downstream + sửa comment liên quan ở các
  script khác (bài học: header "ingest 22:30"/"refresh 23:15" lỗi thời làm audit/quyết định sai);
  nếu đổi trong ngày, xác định job có bị nhảy khe hôm đó không và chạy tay bù (bài học C1b 07-10).
- **Cuối tuần/ngày lễ**: khai báo rõ job chạy 1-5, 6, 0-4 hay daily; nhớ cache không sync cuối
  tuần (refresh BQ thứ Bảy chỉ vào cache tối thứ Hai) và lễ VN chưa encode đủ trong vn_market.py.
