# 8L — Deploy Note (cho Dev)

Hệ thống phân tích cổ phiếu chạy 24/7: **bot Telegram** (trả lời khi user nhắn mã, vd "BMP") +
**cron** chạy job hằng ngày (17:45) và hằng quý, gửi cảnh báo qua Telegram. Dữ liệu thị trường lấy từ
**Google BigQuery**. Đã đóng sẵn Docker — deploy bằng **2 lệnh**.

---

## 1. Cần chuẩn bị (server Linux)
- Docker + plugin `docker compose`
- **2 file bí mật** (chủ hệ thống gửi RIÊNG, KHÔNG nằm trong zip này) — đặt vào **thư mục gốc** của package:
  - `sa-key.json` — Google Cloud service-account key (đã cấp quyền BigQuery trên project `lithe-record-440915-m9`)
  - `telegram_config.json` — token bot + chat_id (có mẫu `telegram_config.template.json` để tham khảo cấu trúc)

## 2. Deploy (2 lệnh)
```bash
# (đã giải nén package, đã đặt sa-key.json + telegram_config.json ở thư mục gốc package)
cd deploy_8l
docker compose up -d --build
```
Xong. `bot` chạy 24/7; `cron` tự chạy job daily/quarterly. Data ghi vào `./data` (volume, không mất khi restart).

## 3. Kiểm tra
```bash
docker compose ps                    # cả 2 service Up
docker compose logs -f bot           # log bot (poll + truy vấn)
docker compose logs -f cron          # log cron
# test thủ công 1 bước:
docker compose exec cron python3 rating_8l.py
```
Test bot: nhắn `BMP` cho bot trên Telegram → phải nhận trả lời ranking 8L trong vài giây.

## 4. ⚠️ 2 lưu ý quan trọng
- **Chỉ MỘT bot Telegram chạy cùng lúc.** Trước khi `up`, **báo chủ hệ thống tắt bot đang chạy trên laptop**
  (nếu không Telegram trả lỗi 409 conflict, bot server không nhận tin).
- **Múi giờ** đã set sẵn `Asia/Ho_Chi_Minh` (cron 17:45 = sau giờ chốt phiên). Không cần chỉnh.

## 5. Vận hành
```bash
docker compose restart bot      # khởi động lại bot
docker compose down             # dừng tất cả
docker compose up -d            # chạy lại (không cần --build nếu code không đổi)
```

---

### Ghi chú kỹ thuật (không bắt buộc đọc)
- Image base `google/cloud-sdk:slim` (có sẵn `bq` CLI + python). Chi tiết: `deploy_8l/DOCKER.md`.
- Không thích Docker? Có thể chạy thẳng systemd + cron: xem `deploy_8l/README_DEPLOY.md`.
- BigQuery auth: entrypoint tự `gcloud auth activate-service-account` từ `sa-key.json` đã mount.
- Secret được mount read-only lúc chạy, KHÔNG bake vào image.
- Một thành phần (refresh dữ liệu ngân hàng qua `vnstock`) cố ý KHÔNG chạy trên server (chặn IP ngoài VN);
  chủ hệ thống tự đồng bộ file `data/bank_lens_v3.csv` — dev không cần quan tâm.
