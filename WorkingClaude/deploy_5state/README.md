# 5-State Market Regime — Deployment Package

Gói build & maintain bảng `tav2_bq.vnindex_5state` cho hệ thống BA-system V11.

**PHẢI deploy gói này TRƯỚC `deploy_v11/`** — recommend_holistic.py phụ
thuộc vào bảng này để lấy market regime state mỗi ngày.

## Quick start

```bash
# 1. Setup (đọc DEPLOY.md trước)
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/ba-sa-key.json   # cần dataEditor role

# 2. Verify
python check_setup.py

# 3. Initial run (full history)
python refresh_data.py --since 2000-01-01
python vnindex_5state_system.py
python upload_to_bq.py

# 4. Schedule daily (cron: 14:50 ICT Mon-Fri, BEFORE recommend_holistic.py)
crontab -e   # add: 50 7 * * 1-5 /home/USER/deploy_5state/run_daily.sh
```

## 5 trạng thái

| State | Name | Target W | Action |
|---|---|---|---|
| 1 | CRISIS | 0% | Tránh mua mới (BA-system stays in cash) |
| 2 | BEAR | 20% | Tránh mua mới |
| 3 | NEUTRAL | 70% | Mua bình thường + V6 ETF parking 70% idle cash |
| 4 | BULL | 100% | Full deployment |
| 5 | EX-BULL | 130% | Có thể leverage (F-system overlay) |

## Files

| File | Mô tả |
|---|---|
| `DEPLOY.md` | **Đọc đầu tiên** |
| `vnindex_5state_system.py` | Classifier chính (canonical) |
| `refresh_data.py` | Pull VNINDEX + breadth từ BQ |
| `upload_to_bq.py` | Ghi đè tav2_bq.vnindex_5state |
| `state_transition_logic.py` | Debug — giải thích state hôm nay |
| `filter.json` | MARKET_DICT BearDvg/BullDvg signals |
| `check_setup.py` | Smoke test |
| `run_daily.sh` / `.bat` | Wrapper cron / Task Scheduler |

## Yêu cầu

- Python 3.10+
- Google Cloud SDK
- BQ Service Account với **dataViewer + dataEditor + jobUser** trên `tav2_bq`
- 4 GB RAM, 2 GB disk
- Internet stable

## Outputs

Sau mỗi lần chạy (1 ngày):
- BQ table `tav2_bq.vnindex_5state` updated (read by `recommend_holistic.py`)
- Local `vnindex_5state_history.csv`
- Optional HTML visualization
