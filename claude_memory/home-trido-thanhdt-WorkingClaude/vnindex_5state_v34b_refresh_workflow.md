# Tam Quan v3.4b daily-refresh workflow (REMEMBER FULLY)

## Trigger
User hỏi "trạng thái thị trường hôm nay" hoặc "state hôm nay theo v3.4b/v5 production":
- **KHÔNG được trả lời chỉ bằng query BQ** — BQ table có thể stale nếu daily job chưa chạy.
- **PHẢI** kiểm tra freshness và rebuild full chain nếu thiếu.

## Freshness check (luôn làm trước khi answer)
```bash
bq query --use_legacy_sql=false --project_id=[REDACTED] --format=pretty \
  'SELECT MAX(t.time) FROM `[REDACTED].tav2_bq.vnindex_5state` AS t'
```
So sánh với `today`. Nếu < today (Mon-Fri trading day) → rebuild.

## Full rebuild pipeline (7 bước, từ MAIN WORKDIR `C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude`)

| # | Script | Output | Notes |
|---|--------|--------|-------|
| 1 | `rm _cache_vnindex_2000_now.pkl _cache_universe_2013_now.pkl` | (delete caches) | Bắt buộc, vì `vnindex_5state_ew_v1.py` skip refresh nếu cache tồn tại |
| 2 | `python vnindex_5state_ew_v1.py` | `vnindex_5state_ew_full.csv` + 2 pkl caches | Pull VNINDEX 2000-now + universe ~1500 tickers từ BQ; ~90s |
| 3 | `python build_concentration_history.py` | `concentration_history.csv` | ~20s |
| 4 | `python vnindex_5state_dual_v3.py` | `vnindex_5state_dual_v3_staging.csv` + `_full.csv` | ~10s |
| 5 | `python deploy_v3_4b_package/pull_us_market.py` | `deploy_v3_4b_package/us_market_history.csv` | yfinance SPX+VIX; **PHẢI copy sang main WORKDIR** sau khi pull |
| 6a | `STATE_WORKDIR=<MAIN> python deploy_v3_4b_package/build_v3_1_clean.py` | `vnindex_5state_tam_quan_v3_1_clean.csv` (main) | Set `STATE_WORKDIR` = main workdir để dùng staging fresh |
| 6b | `cp vnindex_5state_tam_quan_v3_1_clean.csv vnindex_5state_tam_quan_v3_1_full_history.csv` | (rename) | Builder v3.4 đọc tên `_full_history` |
| 6c | `STATE_WORKDIR=<MAIN> python deploy_v3_4b_package/build_v3_4_bull_aware.py` | `vnindex_5state_tam_quan_v3_4b_full_history.csv` (main) | Output v3.4a/b/c — chỉ b là production |
| 7 | **`cp vnindex_5state_tam_quan_v3_4b_full_history.csv deploy_v3_4b_package/`** rồi `python deploy_v3_4b_package/deploy_v3_4b_to_live.py` | BQ `tav2_bq.vnindex_5state` updated | **BUG QUAN TRỌNG**: deploy script đọc CSV từ package dir, KHÔNG phải main WORKDIR. Phải copy fresh CSV vào package dir TRƯỚC khi deploy |
| 8 | (optional) sync `tav2_bq.vnindex_5state_tam_quan_v34b_clean` | Cùng schema | `bq load --replace ... --schema=time:DATE,state:INT64,state_raw:INT64` |

## 🚨 BUGS PHẢI NHỚ

### Bug 1: Stale caches
`vnindex_5state_ew_v1.py` có logic `if os.path.exists(CACHE_VNI): return pd.read_pickle(CACHE_VNI)` — nếu không xóa pkl trước thì pull cũ vẫn dùng. **Luôn `rm` 2 pkl trước khi rebuild**.

### Bug 2: STATE_WORKDIR mặc định = script dir
`build_v3_1_clean.py` và `build_v3_4_bull_aware.py` lấy `WORKDIR = os.environ.get("STATE_WORKDIR", os.path.dirname(__file__))`. Nếu không set env → đọc files từ `deploy_v3_4b_package/` (có thể stale). **Luôn set `STATE_WORKDIR=<MAIN_WORKDIR>` khi gọi**.

### Bug 3: Deploy script bị stale-CSV (CRITICAL)
`deploy_v3_4b_to_live.py` hardcode đường dẫn CSV ở chính package dir của nó. Nếu refresh ở main WORKDIR mà không copy về package dir → **deploy push CSV CŨ lên BQ, xóa data fresh**. Đã gặp ngày 2026-05-25.
→ **Trước khi `deploy_v3_4b_to_live.py`, ALWAYS**:
```bash
cp <MAIN>/vnindex_5state_tam_quan_v3_4b_full_history.csv \
   <MAIN>/deploy_v3_4b_package/vnindex_5state_tam_quan_v3_4b_full_history.csv
```

### Bug 4: 2 BQ tables song song
- `tav2_bq.vnindex_5state` — canonical LIVE (recommend_holistic.py đọc)
- `tav2_bq.vnindex_5state_tam_quan_v34b_clean` — spec table user hay query thẳng

`deploy_v3_4b_to_live.py` chỉ update table thứ nhất. Phải `bq load --replace` thủ công cho table thứ 2:
```bash
bq load --replace --source_format=CSV --skip_leading_rows=1 --location=asia-southeast1 \
  --schema=time:DATE,state:INT64,state_raw:INT64 \
  [REDACTED]:tav2_bq.vnindex_5state_tam_quan_v34b_clean \
  <CSV_PATH>
```

## Verification gate (chạy SAU deploy)
```bash
bq query --use_legacy_sql=false --project_id=[REDACTED] --format=pretty \
  'SELECT t.time, t.state, t.state_raw 
   FROM `[REDACTED].tav2_bq.vnindex_5state` AS t 
   ORDER BY t.time DESC LIMIT 5'
```
Đảm bảo `MAX(time) = today`. Nếu lệch → deploy bị stale-CSV (Bug 3), redeploy.

## Rule for future user-questions
1. User hỏi "state hôm nay" → kiểm tra freshness BQ ngay.
2. Nếu stale → KHÔNG báo state cũ kèm câu "có thể đã flip" — phải refresh full chain trước, rồi mới trả lời.
3. Đừng đọc `state_raw` từ stale data để suy luận "sắp flip" — raw cũng có thể wrong khi upstream stale (đã thấy raw=4 stale vs raw=3 fresh ngày 2026-05-25).

## [REDACTED]02 — DEV RECONCILIATION (DT5G reference lệch) = STALE VINTAGE, đã sync + 2 fix
- **Triệu chứng dev gửi:** 104/112 transition của DT5G reference trùng đúng ngày; 8 lệch (~5 sự kiện) là lag +1/+3/+7 ngày + 2 nhịp ngắn bị bỏ (2007-08-02 BEAR, 2025-06-11..06-25 BULL), rải cả 2007/2009/2013 → **lệch vintage, KHÔNG phải PE/logic**.
- **Chẩn đoán:** mọi nguồn stale so với spine `ticker`=06-01: BQ `vnindex_5state`/`v34b_clean`=05-25, `vnindex_5state_dt_4gate`=05-26, local v3.4b=05-29, US/breadth=05-29/28. Daily refresh đã không chạy từ ~05-25. PE bác bỏ: `VNINDEX_PE` local==BQ 100% (2014→now, max diff 0.0000); local v3.4b vs BQ state 99.87% (chỉ 4 ngày flicker EX-BULL/BULL = vintage P90, không phải PE data). NOTE: `ticker_financial.time` THỰC RA = Release_Date (không phải quý-kết-thúc) → fin join point-in-time đúng.
- **ĐÃ SYNC (deploy live, có backup `vnindex_5state_archive_tinh_te_20260602_094352`):** rebuild full chain từ BQ hiện tại (re-pull US → rm cache → ew_v1 → concentration → dual_v3 → v3.1 → v3.4b → build_dt_4gate) → deploy CẢ 3 bảng BQ về 06-01 (`vnindex_5state` qua deploy script + `bq load --replace` thủ công `v34b_clean` & `dt_4gate`) → regenerate `export_dt5g_transitions.py`. Reference mới: 112 transitions, 2000→06-01, NAV 111.83B/CAGR 20.02%; latest state NEUTRAL(3). Nhịp 2025-06-11..06-25 & 2025-09-19 (dev báo lệch) nay khớp.
- **FIX nguồn breadth của reference:** `export_dt5g_transitions.py` trước đọc breadth từ file `C:\Users\hotro\Downloads\preprocess_...csv` → ĐỔI sang BQ `ticker_prune` (`AVG(Close>MA200)`, COUNT) khớp y hệt live engine `macro_state_live.py`. Tác động: đổi đúng 1 transition pre-2014 (2009-06-02→06-03), 111/112 giống. Downloads CSV deprecated.
- **DEV next:** pull lại BQ (cả 3 bảng=06-01) + dùng artifacts `deploy_golive_dt5g_v4/dt5g_transitions.csv` & `dt5g_daily_reference.csv` (vintage 06-01) → khớp.
- **OneDrive lock:** ghi `data/dt5g_transitions.csv` đôi khi "Device or resource busy" (OneDrive sync) → retry sau vài giây là được.

## [REDACTED]02 (lần 2) — FRESH-BQ rebuild + raw r_score export cho dev
- Dev vẫn báo lệch → user yêu cầu: (1) chạy lại TƯƠI từ BQ (rm cache force pull), (2) xuất dữ liệu thô để dev tự tính r_score, (3) **TUYỆT ĐỐI không bypass BQ lấy local** (mất cơ sở đối chiếu).
- Đã rm 2 cache → pull tươi (universe 3,436,190 rows, VNINDEX 6291) → full chain → deploy lại 3 bảng BQ về **[REDACTED]02** (backup `archive_tinh_te_20260602_213635`). Reference: 111 transitions, NAV 19.90%, latest NEUTRAL(3).
- **ew_v1.py thêm 2 export (env EXPORT_RAW=1):** `vnindex_5state_ew_eligible_universe.csv` (936k rows: rổ EW từng ngày/mã + tv_avg60/above_ma50/log_ret/D_CMF) và `vnindex_5state_ew_daily_aggregates.csv` (ret_ew/breadth/cmf_med/close_ew). Pack cho dev ở `deploy_golive_dt5g_v4/` + README `dt5g_rscore_reconciliation_README.md` (BQ SQL + eligibility + factor weights + thresholds + caveats).
- **CẠM BẪY mới phát hiện (nguồn lệch tail):** trong BQ, dòng VNINDEX cập nhật TRƯỚC các mã thành phần → ngày cuối `n_universe` có thể =1 (vd 06-02), breadth/EW ngày đó vô nghĩa; state vẫn đúng nhờ smoothing nhưng dev pull khác giờ → r_score tail lệch. KHUYẾN NGHỊ: không publish ngày `n_universe<100`.
- **Quy tắc đối chiếu:** chỉ so cùng vintage (cùng ngày pull BQ cả 2 phía); reference cũ vs BQ mới = sai. breadth của reference đã chuyển sang BQ `ticker_prune` (khớp live engine).
- **macro_state_live.py SỬA ([REDACTED]02):** base state nay đọc **BQ `vnindex_5state_tam_quan_v34b_clean` TRƯỚC** (source of truth), trước đây ưu tiên local CSV. Nếu BQ stale (max<end) → IN CẢNH BÁO, KHÔNG âm thầm dùng local. Local chỉ fallback khi BQ read NÉM lỗi (in cảnh báo to). Test 06-02 OK, latest NEUTRAL(3), không fallback. → engine giờ luôn đối chiếu được với dev (cùng nguồn BQ); nếu BQ lag phải chạy refresh+deploy chain chứ không che bằng local.
