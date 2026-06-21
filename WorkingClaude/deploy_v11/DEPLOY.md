# BA-System V11 — Hướng dẫn triển khai live trên server mới

Phiên bản: 2026-05-18
Tác giả: BA-system maintainer

Đây là gói triển khai đầy đủ để chạy hệ thống khuyến nghị BA-system V11 hàng
ngày trên một server mới. Mục tiêu: sau khi đọc xong file này, người vận hành
mới có thể tự setup và chạy `recommend_holistic.py` mỗi chiều sau giờ đóng
cửa thị trường HSX/HNX.

---

## 1. Tổng quan hệ thống

### 1.1 Hệ thống làm gì?

`recommend_holistic.py` là engine khuyến nghị daily. Mỗi chiều sau giờ đóng
cửa, chạy `python recommend_holistic.py` sẽ:

1. Đọc dữ liệu BigQuery (giá, volume, chỉ báo kỹ thuật, fundamental, 5-state regime)
2. Tính TA score v10 cho ~1,200 cổ phiếu Việt Nam
3. Phân loại từng mã thành "play type" (MEGA / MOMENTUM / DEEP_VALUE_RECOVERY / RE_BACKLOG_BUY / ...)
4. Áp dụng V11 filter stack:
   - **P3 COMPOSITE overheat**: block lệnh mua khi VNI/MA200 > 1.30 AND (state=5 OR D_RSI>0.75)
   - **SV_TIGHT Fresh-Q**: lọc mã có Release_Date quá cũ (state-conditional: 30d/60d/no-filter)
   - **D1 RE_BACKLOG_BUY**: ICB 8633 (RE+KCN) với AdvCust YoY > 0.5 được up tier
5. Tách thành 2 books:
   - **BAL book**: top 12 picks từ toàn universe (sector Fin/RE cap = 4)
   - **VN30 book**: top 12 picks chỉ trong top 30 mã thanh khoản
6. In khuyến nghị + save CSV để execute hôm sau T+1

### 1.2 Workflow live hàng ngày

```
Chiều (sau 15:00):
  └─ python recommend_holistic.py
        ├─ holistic_YYYY-MM-DD.csv       (toàn universe đã scoring)
        ├─ ba_book_bal_YYYY-MM-DD.csv    (BAL book 12 picks)
        └─ ba_book_vn30_YYYY-MM-DD.csv   (VN30 book 12 picks)

Sáng hôm sau (T+1 entry):
  └─ Đặt lệnh theo Layer 3 v4 HYBRID:
        - T1_TOP (ADV ≥ 50B/ngày): MUA 14:45 ATC (MOC order)
        - Non-TOP: MUA 11:15 limit @ giá Open
        - BÁN (positions cũ): 09:00 ATO (Open)

Hàng tuần / hàng quý:
  └─ Refresh fundamental_rating_all.csv khi có BCTC quý mới
        python fundamental_rating.py
```

### 1.3 Risk parameters (cố định, đã validated 12 năm backtest)

| Parameter | Giá trị | Ghi chú |
|---|---|---|
| `max_positions` | 12 per book (D1+slot12) | NAV/10 per slot = 10% NAV |
| `hold_days` | 45 ngày | Time exit |
| `stop_loss` | -20% | Conservative, không nới |
| `min_hold` | T+3 (2 phiên) | Quy định VN |
| `sector_cap` Fin/RE | 4 mã (BAL only) | RE_BACKLOG_BUY exempt |
| `re-entry blacklist` | 20 ngày | Sau STOP/TRAIL |
| TC mua | 0.15% | Broker phí mua VN 2026 |
| TC bán | 0.15% + 0.1% thuế | Broker + CG tax |

Expected performance (50B NAV, validated 2014-2026):
- **CAGR**: ~17-19%
- **Sharpe**: ~1.2
- **MaxDD**: ~-15% (vs VNINDEX -45%)
- **2022 crash**: +2.6% (vs VNI -33%)

---

## 2. Server requirements

### 2.1 Hardware tối thiểu

- **CPU**: 2 cores
- **RAM**: 4 GB (BQ queries return ~50k-300k rows tùy date range)
- **Disk**: 10 GB free (logs + outputs tích lũy)
- **Network**: stable Internet, latency tới BigQuery US/SEA acceptable

### 2.2 OS hỗ trợ

- ✅ Windows 10/11 (đang dùng production)
- ✅ Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- ✅ macOS 12+

Hướng dẫn dưới đây sẽ cho cả 3.

### 2.3 Phần mềm cần cài

| Phần mềm | Version | Mục đích |
|---|---|---|
| Python | 3.10+ | runtime |
| Google Cloud SDK | latest | `bq` CLI để query BigQuery |
| Git (optional) | latest | version control |

---

## 3. Setup từng bước

### 3.1 Cài Python

**Linux/macOS**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# macOS (Homebrew)
brew install python@3.12

# Verify
python3 --version  # nên >= 3.10
```

**Windows**:
- Tải Python từ https://www.python.org/downloads/windows/
- ✅ Khi cài, tick "Add Python to PATH"
- Verify trong PowerShell: `python --version`

### 3.2 Cài Google Cloud SDK

**Linux**:
```bash
# Tham khảo https://cloud.google.com/sdk/docs/install
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh
source ~/.bashrc
gcloud --version
bq --version
```

**macOS**:
```bash
brew install --cask google-cloud-sdk
gcloud --version
bq --version
```

**Windows**:
- Tải installer từ https://cloud.google.com/sdk/docs/install#windows
- Chạy `GoogleCloudSDKInstaller.exe`
- Tick "Bundled Python" trong wizard
- Mở PowerShell mới, verify:
```powershell
gcloud --version
bq --version
```

### 3.3 Authenticate BigQuery

Hệ thống dùng BQ project `lithe-record-440915-m9` (dataset `tav2_bq` ở
region `asia-southeast1`). Có 2 cách auth:

#### Cách A — Service Account (KHUYẾN NGHỊ cho server)

1. Yêu cầu admin BQ project tạo Service Account với role:
   - `roles/bigquery.dataViewer` (đọc table)
   - `roles/bigquery.jobUser` (chạy query)
2. Admin export JSON key file (ví dụ `ba-sa-key.json`)
3. Upload file đó lên server, đặt tại `/home/USER/.gcp/ba-sa-key.json`
4. Set env var (thêm vào `~/.bashrc` hoặc PowerShell profile):

   **Linux/macOS**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/home/USER/.gcp/ba-sa-key.json"
   ```

   **Windows (PowerShell)**:
   ```powershell
   [Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "C:\Users\USER\.gcp\ba-sa-key.json", "User")
   ```

5. Verify:
   ```bash
   bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 "SELECT 1 AS ok"
   ```
   Nếu trả về 1 dòng `ok=1` → OK.

#### Cách B — Cá nhân login (DEV ONLY, không khuyến nghị cho server)

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project lithe-record-440915-m9
```

### 3.4 Cài Python dependencies

```bash
cd deploy_v11/
pip install -r requirements.txt
```

(Hoặc tạo virtualenv riêng — khuyến nghị):
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

### 3.5 Cấu hình paths

Mở `recommend_holistic.py`, sửa hằng số ở đầu file (~line 34-36):

```python
WORKDIR = r"/home/USER/deploy_v11"          # Linux/macOS
# WORKDIR = r"C:\Users\USER\deploy_v11"     # Windows
PROJECT = "lithe-record-440915-m9"          # KHÔNG sửa (BQ project ID)
BQ_BIN = r"/usr/local/google-cloud-sdk/bin/bq"   # đường dẫn tới bq CLI
# BQ_BIN = r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
```

Cách tìm `BQ_BIN`:
```bash
which bq          # Linux/macOS
Get-Command bq    # Windows PowerShell
```

### 3.6 Test smoke

```bash
cd deploy_v11
python recommend_holistic.py
```

Output sẽ in ra console + tạo 3 CSV. Nếu thấy:
```
========================================================================================
  🏆 BA-SYSTEM LIVE ENGINE — 2026-05-18
     Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL  (D1+slot12: RE_BACKLOG exempt)
     PM: max=12pos, 10%/pos cap, hold=45d, stop=-20%, BL20, T+3 min hold
========================================================================================

[1/4] Loading TA v10 scoring + 5-state regime ...
      1234 tickers scored
...
```
→ Setup thành công.

---

## 4. Daily live workflow

### 4.1 Lịch chạy đề xuất

| Thời điểm | Hành động |
|---|---|
| **15:00 (sau ATC)** | Chạy `recommend_holistic.py` để có khuyến nghị T+1 |
| **15:00 hôm sau (T+1)** | Đặt lệnh BUY ATC cho mã T1_TOP, lệnh BUY 11:15 limit cho non-TOP |
| **09:00 hôm sau (T+1)** | Đặt lệnh SELL Open cho positions cần exit (STOP/TIME từ T) |
| **Cuối tuần** | Review performance, kiểm tra log lỗi |
| **Sau ngày công bố BCTC quý** | Refresh `fundamental_rating_all.csv` |

### 4.2 Schedule tự động

#### Linux (cron)

```bash
crontab -e
```

Thêm dòng:
```cron
# Mon-Fri 15:05 ICT (UTC+7) → 08:05 UTC
5 8 * * 1-5 cd /home/USER/deploy_v11 && /home/USER/deploy_v11/.venv/bin/python recommend_holistic.py >> logs/run_$(date +\%Y-\%m-\%d).log 2>&1
```

Tạo log dir trước:
```bash
mkdir -p /home/USER/deploy_v11/logs
```

#### Windows (Task Scheduler)

```powershell
$Action = New-ScheduledTaskAction `
    -Execute "C:\Users\USER\deploy_v11\.venv\Scripts\python.exe" `
    -Argument "recommend_holistic.py" `
    -WorkingDirectory "C:\Users\USER\deploy_v11"

$Trigger = New-ScheduledTaskTrigger -Daily -At "15:05" -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday

Register-ScheduledTask -TaskName "BAv11Daily" -Action $Action -Trigger $Trigger -RunLevel Highest
```

#### macOS (launchd)

Tạo `~/Library/LaunchAgents/com.bav11.daily.plist` — xem [Apple launchd doc](https://www.launchd.info/).

### 4.3 Đọc output

Sau khi script chạy xong, 3 file CSV xuất hiện trong `WORKDIR`:

```
holistic_2026-05-18.csv         # toàn universe với scoring + play_type
ba_book_bal_2026-05-18.csv      # 12 picks BAL book
ba_book_vn30_2026-05-18.csv     # 12 picks VN30 book
```

Mỗi book CSV có columns chính:
- `ticker`, `play_type`, `ta_score`, `fa_tier`
- `rsi`, `ma50_slope`, `vs_3m_high`, `pe_zscore`
- `np_yoy`, `sector_top`, `liq_b_vnd`

**Số lượng position cần mua mới mỗi ngày**: 0-12 trên mỗi book, tùy thanh
khoản signal. Trung bình 12 năm: ~5-7 mã/book/ngày.

### 4.4 Order placement guide

```
Hôm nay (T): script khuyến nghị 10 mã trong BAL book

Phân loại mỗi mã theo ADV (avg daily value):
  - ADV ≥ 50B VND/ngày → T1_TOP   (khoảng 30 mã, thường VN30 + bluechip)
  - ADV < 50B VND/ngày → Non-TOP

Sáng mai (T+1):
  09:00 ATO  — Đặt lệnh SELL Open cho mọi position từ T cần thoát
  11:15      — Đặt lệnh BUY limit @ giá Open cho Non-TOP mã trong book
  14:45 ATC  — Đặt lệnh BUY MOC cho T1_TOP mã trong book

Size mỗi position = 10% NAV của book (NAV book = 50% tổng NAV)
                  = 5% tổng portfolio
```

### 4.5 Khi nào KHÔNG mua

Script tự bypass khi:
- Market state = CRISIS (1) hoặc BEAR (2) → in `❌ BEAR/CRISIS regime — system stays in cash`
- P3 overheat triggered → in `V11 P3 COMPOSITE overheat (...): blocked N buy candidates`

Lúc đó: không đặt lệnh mới, giữ cash. Vẫn execute lệnh SELL của position cũ
theo stop/time.

---

## 5. Maintenance định kỳ

### 5.1 Refresh FA snapshot (hàng quý)

Khi BCTC quý mới công bố (Q1 thường lộn xộn cuối tháng 4 - đầu tháng 5), chạy:

```bash
cd deploy_v11
python fundamental_rating.py
```

Output: `fundamental_rating_all.csv` (overwrite).

Schedule này có thể tự động chạy cuối tuần đầu tiên của mỗi tháng.

### 5.2 Theo dõi log

```bash
tail -f logs/run_$(date +%Y-%m-%d).log
```

Lỗi thường gặp:
- `bq command not found` → check PATH (mục 3.2)
- `Permission denied` BQ table → check service account permissions (mục 3.3)
- `KeyError: 'fa_tier'` → `fundamental_rating_all.csv` corrupted/missing → refresh (mục 5.1)

### 5.3 Verify BQ data freshness

Sau ngày T market đóng cửa, dữ liệu trong `tav2_bq.ticker` cần được update.
Verify trước khi chạy live:

```bash
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
  "SELECT MAX(time) FROM tav2_bq.ticker WHERE ticker='VNINDEX'"
```

Nếu kết quả khác ngày T → chờ data pipeline hoặc dùng `ticker_1m` fallback
(script tự xử lý).

---

## 6. Files trong gói

| File | Mô tả | Có sửa? |
|---|---|---|
| `DEPLOY.md` | File này | — |
| `requirements.txt` | Python deps | Không |
| `recommend_holistic.py` | **MAIN** — daily engine | Sửa WORKDIR + BQ_BIN |
| `fundamental_rating.py` | FA scoring (quarterly refresh) | Sửa WORKDIR |
| `fundamental_rating_all.csv` | FA snapshot cache | Auto-overwrite |
| `bigquery_dictionary.json` | Reference — column dictionary | Không |
| `run_daily.sh` | Wrapper Linux/macOS | Đường dẫn |
| `run_daily.bat` | Wrapper Windows | Đường dẫn |

---

## 7. Hỏi đáp / Troubleshooting

**Q: Tôi muốn chạy lại cho một ngày quá khứ?**
A: `python recommend_holistic.py 2026-05-15` — pass date as argument.

**Q: Tại sao một số mã có trong universe nhưng không vào book?**
A: Filter pipeline: P3 overheat block → SV_TIGHT Fresh-Q (loại mã Release_Date
quá cũ) → top theo PRIORITY × ta_score → sector cap Fin/RE=4. Mã có tier
PASS / WAIT / COMPOUNDER_HOLD đều không vào BA book.

**Q: NAV của tôi khác 50B, có cần sửa code?**
A: Không. Script chỉ khuyến nghị mã, không tính position size theo VND.
Bạn tự nhân 10% × NAV thực tế cho mỗi slot.

**Q: Tôi không có quyền access BQ project, làm sao?**
A: Liên hệ owner để được cấp service account hoặc share data sang project
riêng của bạn. Tables cần access:
- `tav2_bq.ticker`
- `tav2_bq.ticker_1m`
- `tav2_bq.ticker_financial`
- `tav2_bq.fa_ratings`
- `tav2_bq.vnindex_5state`
- `tav2_bq.ticker_prune`

**Q: Có muốn deploy F-system futures overlay không?**
A: F-system là OPTIONAL 20% capital overlay với VN30F futures (long/short
theo state). Daily engine có in khuyến nghị F overlay. Nếu KHÔNG dùng
futures, bỏ qua phần in F-overlay. Performance core BA-system đã tính
KHÔNG tính F.

**Q: Backtest engine ở đâu?**
A: Gói này CHỈ chứa live engine. Backtest engine (`simulate_holistic_nav.py`
+ `sim_v11_transparent.py`) ở repo gốc — không cần cho deployment live.

**Q: Layer 3 paper-trade shadow tracker?**
A: OPTIONAL — script `layer3_v4_shadow.py` ở repo gốc, track xem rule
"BUY ATC vs T+1 Open" có còn lợi không. Cần cache intraday data, không
include trong gói này. Liên hệ owner nếu muốn deploy.

---

## 8. Liên hệ + Memory

- Memory cá nhân: `MEMORY.md` ở repo gốc tổng hợp toàn bộ insight + bug fix.
- Production proposal V11: file `ba_v11_production_proposal.md`.
- BA-system definition: file `ba_system_definition.md` (canonical spec).
- Layer 3 timing: file `t1_intraday_buypoint_results.md`.

Mọi câu hỏi về methodology / backtest history / decision rationale → đọc
các file memory trên (đều markdown, ~5KB mỗi file).
