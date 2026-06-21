# BA-System V11 — Deployment Package

Gói triển khai live engine của hệ thống khuyến nghị BA-system V11
cho thị trường chứng khoán Việt Nam.

## Quick start

```bash
# 1. Setup (đọc kỹ DEPLOY.md trước)
pip install -r requirements.txt

# 2. Sửa WORKDIR + BQ_BIN trong recommend_holistic.py (xem DEPLOY.md §3.5)

# 3. Smoke test
python check_setup.py

# 4. Chạy live
python recommend_holistic.py        # → khuyến nghị cho ngày hôm nay
python recommend_holistic.py 2026-05-15   # → rerun cho ngày cụ thể
```

## Files

| File | Mô tả |
|---|---|
| `DEPLOY.md` | **Đọc đầu tiên** — hướng dẫn deploy đầy đủ |
| `requirements.txt` | Python dependencies |
| `recommend_holistic.py` | Main engine (sửa WORKDIR + BQ_BIN) |
| `fundamental_rating.py` | Refresh FA snapshot (chạy hàng quý) |
| `fundamental_rating_all.csv` | FA snapshot hiện tại (~5MB) |
| `bigquery_dictionary.json` | Reference — column dictionary |
| `check_setup.py` | Smoke test verify setup |
| `run_daily.sh` | Wrapper Linux/macOS (cron-friendly) |
| `run_daily.bat` | Wrapper Windows (Task Scheduler-friendly) |

## Yêu cầu

- Python 3.10+
- Google Cloud SDK (`bq` CLI)
- BigQuery access tới project `lithe-record-440915-m9`, dataset `tav2_bq`
- ~5GB disk, 4GB RAM
- Internet stable

## Đầu ra mỗi ngày

```
holistic_YYYY-MM-DD.csv         # toàn universe đã scoring
ba_book_bal_YYYY-MM-DD.csv      # 12 picks BAL book
ba_book_vn30_YYYY-MM-DD.csv     # 12 picks VN30 book
```

Expected performance (50B NAV, validated 2014-2026): CAGR ~17-19%,
Sharpe ~1.2, MaxDD ~-15%.

## Support

Toàn bộ chi tiết methodology + bug history + design decisions ở
file memory `MEMORY.md` (repo gốc).
