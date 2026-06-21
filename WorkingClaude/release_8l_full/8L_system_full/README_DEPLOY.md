# 8L — Hệ thống đầy đủ để chạy live & tái tạo kết quả

Gói này chứa **toàn bộ** code + dữ liệu mà hệ 8L (8 Lăng Kính) đang dùng để ra kết quả hiện tại
(bảng xếp hạng, screener, DNA card, rổ 8L-VN30, alert). Mục tiêu: bên production cài đặt và **tái tạo
đúng kết quả**, rồi chạy live trên server.

Sinh ngày 2026-06-11. **Không** chứa secret (token Telegram) — dùng `telegram_config.template.json`.

---

## 0. Cấu trúc gói
```
8L_system_full/
  *.py                     25 module Python (toàn bộ closure: pipeline + feeders + bot)
  data/                    file dữ liệu trong data/ mà pipeline đọc
  <root>/*.csv,*.json      vài input ở thư mục gốc (fundamental_rating_all.csv, fa_ratings_lh.csv, sbv_*...)
  docs/                    8L_README.md (kiến trúc 8L) + CLAUDE.md (schema BQ + toàn hệ thống)
  reference/               pt_8l_daily.bat (Windows) · run_8l_daily.sh (Linux) · telegram_8l_bot.bat
  requirements.txt         thư viện Python
  telegram_config.template.json   mẫu config bot (copy thành telegram_config.json, điền token)
  README_DEPLOY.md         file này
```

## 1. Yêu cầu hệ thống
- **Python 3.11+** · `pip install -r requirements.txt` (pandas, numpy, requests).
- **Google Cloud SDK** (lệnh `bq`) đã auth service-account có quyền đọc dataset `tav2_bq`.
  Pipeline gọi `bq query` qua subprocess (xem `recommend_holistic.bq`, `vn30_8l._bq`).
- **vnstock** (chỉ cần khi REFRESH feeder ngân hàng/cước/commodity): `pip install vnstock`.
- Mạng tới `api.telegram.org` (cho alert/bot).

## 2. Biến môi trường
| Biến | Ý nghĩa |
|------|---------|
| `WORKDIR_8L` | Thư mục cài đặt 8L (nơi giải nén gói). **Bắt buộc.** Mọi script đọc/ghi quanh đây. |
| `DNA_PYEXE` | Đường dẫn Python interpreter (mặc định `python3`). Dùng khi spawn subprocess (dna_card, vn30_8l). |
| `PATH` | Phải có thư mục chứa `bq`. |

> ⚠️ Nhiều script có **đường dẫn Windows mặc định** trong biến `WORKDIR`/`PYEXE` (vd `C:\Users\...`).
> Khi `WORKDIR_8L` được set, code ưu tiên biến môi trường. Hãy **export `WORKDIR_8L` và `DNA_PYEXE`**
> trước khi chạy để override hoàn toàn các default Windows.

## 3. Bảng BigQuery cần có (dataset `tav2_bq`, location `asia-southeast1`)
- `ticker` (OHLCV + indicator ngày) · `ticker_1m` (snapshot ~1 tháng, dùng cho live) · `ticker_financial` (tài chính quý).
- `vnindex_5state_dt5g_live` — **cổng thị trường DT5G** (đọc read-only; do hệ market-timing riêng sinh ra,
  KHÔNG nằm trong gói này). Bot/`vn30` hiển thị state từ bảng này; thiếu thì tự xuống cấp.
- Chi tiết schema từng cột: `docs/CLAUDE.md`.

## 4. Cấu hình Telegram
```
cp telegram_config.template.json telegram_config.json
# điền bot_token (từ @BotFather) + chat_id
```

## 5. Chạy
### Pipeline EOD hằng ngày (nhẹ)
- Linux: `WORKDIR_8L=/opt/8l DNA_PYEXE=python3 bash reference/run_8l_daily.sh` (cron ~17:45 ngày giao dịch).
- Windows: `reference\pt_8l_daily.bat` (Task Scheduler).
- Thứ tự: `rating_8l → unified_screener → rank_8l → dna_card → vn30_8l → rank_8l_daily_alert → cheap_pb_floor → snapshot`.

### Refresh feeder (định kỳ — sau báo cáo quý / cập nhật commodity tháng)
Các module xây CSV trung gian mà screener/rank đọc. Chạy lại khi dữ liệu nền đổi (xem cuối `run_8l_daily.sh`):
`bank_lens_v3 · power_lens · cash_machine_screen · margin_cycle_detector · saturation_detector · cyclical_structural · oil_transmission · freight_map · asset_play_detector`.

### Bot tương tác
`python telegram_8l_bot.py` (long-poll). Lệnh: gõ **số** (Top N) · `vn30` (rổ + cổng) · `new` (mã mới vào Top 30 trong tuần) · **mã CP** (DNA chi tiết). Đăng ký ONLOGON/systemd để chạy thường trú.

## 6. Phân loại dữ liệu (QUAN TRỌNG để tái tạo)
| Loại | File | Nguồn / cách làm mới |
|------|------|----------------------|
| **Tự sinh từ BQ** | rank_8l.csv, unified_screener.csv, dna_cards.csv, vn30_8l.csv, rating_8l*.csv, cheap_pb_floor.csv | Pipeline tự tạo mỗi phiên. Bản kèm = snapshot để **đối chiếu tái tạo**. |
| **Feeder trung gian** | bank_lens_v3.csv, power_lens.csv, cash_machine_screen.csv, engine_class.csv, margin_cycle_detector.csv, saturation_detector.csv, cyclical_structural.csv, asset_play.csv | Module feeder tạo (mục 5). bank_lens_v3 cần **vnstock** (NPL/CAR). |
| **Input THỦ CÔNG** | `data/*_monthly.csv` (brent, sugar...), `data/moat_tags.csv`, oil/freight map | **Nhập tay**, không tự cập nhật. brent/commodity ← FRED/EIA/ycharts; moat_tags ← biên tập tay. (xem ghi chú trong từng file). |
| **Input thượng nguồn** | `fundamental_rating_all.csv`, `fa_ratings_lh.csv`, `fundamental_rating_latest.csv` | Bảng rating tài chính (xây từ `ticker_financial`). Bản kèm = snapshot hiện hành; làm mới bằng builder fundamental của hệ (ngoài phạm vi 8L screening). |
| **Macro/SBV** | `sbv_*.json`, `sbv_macro_log.csv` | `sbv_macro_overlay.py` (lãi suất điều hành). |

## 7. Quy trình tái tạo & kiểm chứng
1. Giải nén vào `WORKDIR_8L`, `pip install -r requirements.txt`, auth `bq`, set env, tạo `telegram_config.json`.
2. (Tùy chọn) refresh feeder nếu muốn dựng lại từ đầu; nếu chỉ kiểm chứng, dùng feeder CSV kèm sẵn.
3. Chạy pipeline daily.
4. **So sánh** `data/rank_8l.csv` và `data/vn30_8l.csv` mới sinh với bản snapshot kèm trong gói → phải khớp
   (sai khác nhỏ chỉ do dữ liệu BQ đã cập nhật thêm phiên mới). Đây là phép xác nhận tái tạo thành công.

## 8. Lưu ý kiến trúc
- `telegram_recommend.py` còn có hàm `main()` = **báo cáo thị trường V4 12.1** (ngoài phạm vi 8L); bot 8L chỉ
  dùng các hàm tiện ích của nó (`get_dt5g_state`, `load_config`, `send_telegram_text`). Vài CSV V4 nhỏ
  (pt_v*_logs, compare_v11...) đi kèm chỉ để các hàm đó không lỗi khi import — không cần cho screening 8L.
- Toàn bộ logic 8L nằm ở các module lăng kính + `unified_screener`/`rank_8l`/`dna_card`/`vn30_8l`. Đọc
  `docs/8L_README.md` để hiểu router + 8 lăng kính.
