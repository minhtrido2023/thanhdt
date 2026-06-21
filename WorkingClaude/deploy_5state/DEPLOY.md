# 5-State Market Regime — Hướng dẫn triển khai live trên server

Phiên bản: 2026-05-19

Gói này build & maintain bảng `tav2_bq.vnindex_5state` mà
`recommend_holistic.py` (BA-system V11 daily engine) phụ thuộc vào.

**Phải deploy gói này TRƯỚC khi deploy `deploy_v11/`** (hoặc song song nhưng
chạy nó sớm hơn trong lịch daily).

---

## 1. Tổng quan

### 1.1 Hệ thống làm gì?

Hệ thống `vnindex_5state_system.py` phân loại trạng thái thị trường VNINDEX
mỗi ngày thành 1 trong 5 trạng thái:

| State | Tên | Target weight | Đặc trưng |
|---|---|---|---|
| 1 | CRISIS | 0% | r_score < 0.10 + có thể PE>P90 / DD<-25% / Vol>1.5× avg |
| 2 | BEAR | 20% | r_score 0.10-0.30 |
| 3 | NEUTRAL | 70% | r_score 0.30-0.75 |
| 4 | BULL | 100% | r_score 0.55-0.75 |
| 5 | EX-BULL | 130% | r_score > 0.75 |

**7 factors** (xếp hạng expanding percentile, min 252 sessions):
- P3M(30%) — return 3 tháng
- P1M(10%) — return 1 tháng
- MA200-dev(15%) — Close/MA200 - 1
- RSI Wilder-14(15%)
- MACD-hist(10%)
- CMF-14(8%)
- Breadth-%>MA50(12%) — đo độ rộng thị trường

**Smoothing pipeline**: EMA(α=0.40) → mode(window=15) → min_stay_filter(7
sessions) — loại micro-transitions 1-3 ngày.

**BearDvg / BullDvg gates**: 4 patterns (2 bear + 2 bull) phát hiện RSI
divergence + MACDdiff + CMF + ratio Close/RSI_Max3M_Close (mask_2011 trở đi).
Khi BearDvg fire → floor=CRISIS (0%) tới khi exit OR:
  - BullDvg fire, hoặc
  - P3M_rank > 0.45 AND **PE_rank < 0.80** (cần VNINDEX_PE), hoặc
  - r_score_ema > 0.65 liên tiếp 10 phiên
Min duration 60 sessions sau BearDvg cuối cùng.

**PE expanding histogram** (yêu cầu `tav2_bq.ticker.VNINDEX_PE`):
  - **Risk override #1**: PE > P90 expanding → cap state at BULL (không cho EX-BULL)
    bảo vệ khi định giá bubble.
  - **Gate exit condition**: PE_rank < 0.80 cho phép thoát BearDvg gate khi
    định giá đã hợp lý lại.
  - Cả 2 dùng expanding window (no look-ahead, min 60 valid samples).

### 1.2 Daily workflow

```
Mỗi chiều sau giờ đóng cửa (~15:00 ICT):
  ┌─ refresh_data.py            (pull VNINDEX + breadth từ BQ)
  ├─ vnindex_5state_system.py  (phân loại states, output CSV)
  └─ upload_to_bq.py            (ghi đè tav2_bq.vnindex_5state)
       ↓
  Tiếp theo: recommend_holistic.py (gói deploy_v11) đọc bảng đã update.
```

### 1.3 Kết quả validated

Walk-forward IS (2000-2020) + OOS (2021-nay):
- **Since 2011**: CAGR 12.1%, Sharpe 1.06, MaxDD -19.3%, Calmar 0.63
- vs B&H since 2011: CAGR 9.2%, Sharpe 0.57, MaxDD -45.3%
- 128 state transitions, median stay 20 sessions, 0 micro-transitions ≤5 sessions

---

## 2. Server requirements

Y hệt như `deploy_v11/`:
- Python 3.10+
- Google Cloud SDK (`bq` CLI)
- BigQuery service account với quyền:
  - `roles/bigquery.dataViewer` (đọc tav2_bq.ticker, ticker_prune)
  - `roles/bigquery.dataEditor` (ghi đè tav2_bq.vnindex_5state)
  - `roles/bigquery.jobUser` (chạy query + load)
- 4 GB RAM, 2 GB disk

**Lưu ý**: gói này CẦN quyền WRITE BQ (khác với deploy_v11 chỉ cần READ).

---

## 3. Setup từng bước

### 3.1 Cài Python, Cloud SDK, BQ auth

Y hệt mục 3.1-3.3 của `deploy_v11/DEPLOY.md`. Service account JSON key
đặt tại `~/.gcp/ba-sa-key.json`.

**Khác biệt**: yêu cầu admin BQ cấp thêm `roles/bigquery.dataEditor` trên
bảng `tav2_bq.vnindex_5state`. Để verify quyền:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/ba-sa-key.json
bq show --project_id=lithe-record-440915-m9 tav2_bq.vnindex_5state
```

### 3.2 Install dependencies

```bash
cd deploy_5state/
python3 -m venv .venv
source .venv/bin/activate  # hoặc .venv\Scripts\Activate.ps1 trên Windows
pip install -r requirements.txt
```

### 3.3 Smoke test

```bash
python check_setup.py
```

Output kỳ vọng:
```
[1/6] Python version
  [✓] Python 3.12.x
[2/6] Python dependencies
  [✓] pandas 2.x
  [✓] numpy 1.2x
[3/6] Google Cloud SDK / bq CLI
  [✓] bq found at: ...
[4/6] BigQuery read access
  [✓] Read tav2_bq.ticker
  [✓] Read tav2_bq.ticker_prune
[5/6] BigQuery write check (vnindex_5state table)
  [✓] Table tav2_bq.vnindex_5state exists
[6/6] Local files
  [✓] vnindex_5state_system.py
  [✓] refresh_data.py
  [✓] upload_to_bq.py
  [✓] filter.json

  ✅ Setup OK. Bước tiếp theo: python refresh_data.py
```

### 3.4 Khởi tạo dữ liệu lần đầu

```bash
# Pull VNINDEX history từ 2000-01-01 (full history)
python refresh_data.py --since 2000-01-01

# Classify states (mất ~30-60s)
python vnindex_5state_system.py

# Upload to BQ (OVERWRITE bảng)
python upload_to_bq.py
```

Sau bước 3 sẽ thấy:
```
✓ BQ table updated (tav2_bq.vnindex_5state)
Table now has 6XXX rows, latest=2026-05-XX
```

### 3.5 Verify

```bash
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
  "SELECT time, state FROM tav2_bq.vnindex_5state ORDER BY time DESC LIMIT 5"
```

Phải thấy 5 dòng mới nhất với state ∈ {1..5}.

---

## 4. Daily workflow tự động

### 4.1 Schedule (cron Linux)

```bash
crontab -e
```

Thêm:
```cron
# 5-state daily: 14:50 ICT Mon-Fri → 07:50 UTC
# Chạy TRƯỚC recommend_holistic.py (15:05 ICT) để bảng đã sẵn sàng
50 7 * * 1-5 /home/USER/deploy_5state/run_daily.sh
```

### 4.2 Schedule (Task Scheduler Windows)

```powershell
$Action = New-ScheduledTaskAction `
    -Execute "C:\Users\USER\deploy_5state\run_daily.bat" `
    -WorkingDirectory "C:\Users\USER\deploy_5state"

$Trigger = New-ScheduledTaskTrigger -Daily -At "14:50" `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday

Register-ScheduledTask -TaskName "VnIndex5State" -Action $Action `
    -Trigger $Trigger -RunLevel Highest
```

### 4.3 Theo dõi log

```bash
tail -f logs/5state_$(date +%Y-%m-%d).log
```

Lỗi thường gặp:
- `bq command not found` → kiểm tra PATH
- `Permission denied` BQ load → thiếu `dataEditor` role
- `VNINDEX_PE` thưa (<50%) → `refresh_data.py` sẽ in warning. BQ column
  `tav2_bq.ticker.VNINDEX_PE` cần upstream pipeline backfill nếu data
  thiếu nhiều — PE risk override + gate exit qua PE_rank sẽ không hoạt động.

---

## 5. Files trong gói

| File | Mô tả | Có sửa? |
|---|---|---|
| `DEPLOY.md` | File này | — |
| `README.md` | Quick reference | — |
| `requirements.txt` | pandas + numpy | Không |
| `vnindex_5state_system.py` | **Classifier chính** | Không (canonical) |
| `state_transition_logic.py` | Explainer (optional, debug) | Không |
| `refresh_data.py` | Pull VNINDEX + breadth từ BQ | Không |
| `upload_to_bq.py` | Ghi đè BQ table | Không |
| `filter.json` | MARKET_DICT_FILTER (BearDvg/BullDvg) | Không |
| `check_setup.py` | Smoke test | Không |
| `run_daily.sh` | Wrapper Linux/macOS | Đường dẫn |
| `run_daily.bat` | Wrapper Windows | Đường dẫn |

**Outputs runtime** (gen ra mỗi ngày):
- `VNINDEX.csv` (~300 KB) — input cache
- `breadth_data.csv` (~60 KB) — input cache
- `vnindex_5state_history.csv` (~150 KB) — output classifier
- `vnindex_5state_system.html` (~2 MB) — visualization, optional
- `vnindex_transitions_v2.html` (~1 MB) — transitions log, optional

---

## 6. Hỏi đáp / Troubleshooting

**Q: Tôi không có quyền ghi BQ table, làm sao?**
A: Liên hệ admin BQ project. Cần `roles/bigquery.dataEditor` trên dataset
`tav2_bq` (hoặc specifically trên bảng `vnindex_5state`).

**Q: Lần đầu chạy mất bao lâu?**
A:
- `refresh_data.py`: ~30s (pull ~6500 rows VNINDEX + ~3000 rows breadth)
- `vnindex_5state_system.py`: ~30-60s (build full history + HTML)
- `upload_to_bq.py`: ~5s (bq load 6500 rows)

Tổng ~2 phút. Daily run incremental sẽ ~1 phút (refresh lại từ 2000 vẫn rẻ).

**Q: HTML reports có cần generate không?**
A: Không. Chỉ là visualization để debug. Bạn có thể tắt bằng cách comment
phần HTML write trong `vnindex_5state_system.py` (lines ~1100-1700). Nhưng
giữ lại tiện cho human review.

**Q: Nếu BQ table `tav2_bq.vnindex_5state` chưa tồn tại?**
A: `upload_to_bq.py` dùng `bq load --replace` sẽ TỰ tạo table với schema:
`time:DATE, state:INT64, state_raw:INT64`. Service account chỉ cần
`dataEditor` trên dataset.

**Q: BearDvg gate hiện đang mở (state forced về CRISIS), tôi có thể tắt không?**
A: KHÔNG khuyến nghị. Đây là feature bảo vệ. Để xem lý do gate đang mở:
```bash
python state_transition_logic.py
```
Output sẽ in chi tiết các điều kiện exit gate còn thiếu.

**Q: Có cần refresh từ 2000-01-01 mỗi ngày không?**
A: Có — vì 5-state cần đủ 252 sessions lookback để expanding rank ổn định.
Refresh full history cũng nhanh (~30s). Đừng cắt ngắn vì dễ sai state khi
phase break (giữa các đợt BEAR/BULL).

**Q: Bị mismatch với production state hiện tại?**
A: Kiểm tra:
1. `VNINDEX.csv` có đủ tới hôm qua không?
2. `breadth_data.csv` có dữ liệu mới không?
3. Filter `mask_2011` trong `filter.json` đúng không?

Để debug 1 ngày cụ thể:
```python
# Trong state_transition_logic.py
explain_day("2026-05-15")
```

---

## 7. Tham khảo

- Canonical spec: `MEMORY.md` mục "VNINDEX 5-State Market System" (repo gốc)
- Parameter rationale: file `vnindex_5state_v2g.md` (DON'T deploy v2g — đã revert)
- Backtest results: `market_timing_final_system.md`

Liên hệ owner cho config chi tiết (filter.json MARKET_DICT logic, gate
parameters) — KHÔNG nên tinker mà chưa hiểu rõ.
