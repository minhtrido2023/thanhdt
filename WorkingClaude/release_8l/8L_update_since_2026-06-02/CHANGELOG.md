# 8L — Bản cập nhật kể từ 02/06/2026

Gói này chỉ chứa **phần CODE + DATA đã thay đổi** của hệ 8L kể từ bản bàn giao ngày **02/06/2026**.
Phần kết nối Telegram (transport) do production tự quản — không nằm trong gói (xem mục "Telegram glue" cuối file).

> ⚠️ **Cách dùng:** production đang giữ bản 02/06 làm gốc. Hãy **diff từng file trong `code/` với bản gốc** để xem thay đổi chính xác. Mô tả dưới đây dựa trên changelog/ghi chú nội bộ của dự án, dùng để định hướng — bản diff của các bạn là nguồn xác thực.

---

## 1. Module 8L mới

| File | Vai trò |
|------|---------|
| `code/oil_transmission.py` + `data/oil_transmission_map.csv` | **Lăng kính L7 chuỗi dầu khí.** Truyền dẫn giá dầu qua 4 kênh khác dấu/độ trễ: UPSTREAM (PVD/PVS, theo level + trễ 2Q), LỌC/PP (BSR/OIL theo hướng, tồn kho phản ứng ngay), KHÍ (GAS, trễ 1–2Q), PHÂN BÓN (DCM/DGC, đồng pha energy-complex). Map ngành→kênh ở `oil_transmission_map.csv`. |
| `code/freight_map.py` + `data/freight_map.csv`, `data/freight_rates_quarterly.csv`, `data/bdi_daily_real.csv` | **Lăng kính cước vận tải biển** (HAH & nhóm shipping). Map cước/ BDI → tín hiệu chu kỳ biên, bơm vào margin-cycle cho các mã freight mà commodity-detector thuần không bắt. |
| `code/vn30_8l.py` | **MỚI — rổ "8L-VN30" triển khai được.** Carve top-30 mã có điểm 8L cao nhất vượt sàn thanh khoản ≥10B VND/ngày, equal-weight, tái cơ cấu quý. Query BQ lấy thanh khoản thật (kể cả ngân hàng) → `data/vn30_8l.csv`. Backtest 2014–2026: lợi thế vs VN30 là **drawdown thấp hơn ~10pp (phòng thủ)**, không phải alpha lợi nhuận; đòn bẩy thật là cổng thị trường DT5G. |
| `code/bot_8l_commands.py` | **MỚI — logic 3 lệnh danh sách cho bot:** `top-N` (gõ số), `new` (mã mới vào Top 30 trong tuần, dùng snapshot ngày), `vn30` (rổ trên + trạng thái cổng DT5G). Đây là lớp render; transport Telegram do production nối. `format_vn30()` gọi `get_dt5g_state(date)->(state,as_of,source)` qua try/except — thiếu provider thì tự xuống cấp "cổng không khả dụng". |

## 2. Module 8L được nâng cấp (đã có từ trước, đổi nội dung)

| File | Thay đổi chính (theo changelog dự án) |
|------|----------------------------------------|
| `code/moat_5f.py` | Lớp phủ moat 5-Forces (Porter) dạng **GATE độ bền** (không phải ranker): NONE −16, WIDE +1.2. Registry tag tay ở `data/moat_tags.csv`. Đã wire vào `rank_8l` + `dna_card`. ⚠️ LIVE-ONLY: không đưa vào backtester prodspec (không point-in-time). |
| `code/rank_8l.py` | Tích hợp lớp phủ moat 5F vào điểm composite route-aware. |
| `code/dna_card.py` | Tích hợp moat 5F + map dầu/cước vào hồ sơ 8L/mã (full-universe coverage). |
| `code/cyclical_structural.py` + `data/brent_monthly.csv` | Cập nhật neo Brent + đọc cấu trúc commodity (percentile × cung-cầu × cost-anchor). |
| `code/rating_8l.py` | Cập nhật rating chất lượng 1–5 (credit-style) → `rating_8l.csv` + top30 + buynow. |
| `code/power_lens.py` | Tinh chỉnh lăng kính POWER (vòng đời trả nợ ICB 7535). |
| `code/unified_screener.py` | Hợp nhất các map mới (oil/freight/sugar) + merge rating vào bảng sàng lọc toàn universe. |
| `data/moat_tags.csv` | Registry moat 5F (tag tay) — cập nhật nội dung. |

## 3. Thứ tự pipeline (tham khảo)

`reference/pt_8l_daily.bat` (orchestrator Windows hiện tại) — server Linux tự viết runner tương đương. **Bước mới so với 02/06:**
- Thêm `python vn30_8l.py` **sau** `rank_8l.py` (sinh rổ 8L-VN30).
- Thêm bước snapshot `rank_8l` theo ngày (phục vụ lệnh bot `new`): `python -c "import bot_8l_commands as b; b.snapshot_today()"` → `data/rank_8l_snap/`.

Thứ tự refresh đầy đủ (8L_README): bank_lens_v3 → power_lens → cash_machine_screen → margin_cycle_detector → saturation_detector → cyclical_structural → asset_play_detector → **oil_transmission / freight_map** → unified_screener → rank_8l → **vn30_8l** → dna_card → rank_8l_daily_alert → cheap_pb_floor.

## 4. Telegram glue (production tự quản — KHÔNG có trong gói)

Các file sau cũng đổi từ 02/06 nhưng thuộc lớp transport/báo cáo — các bạn tự nối:
- `telegram_8l_bot.py` — route `vn30` / số / `new` → gọi `bot_8l_commands`. Cần `import bot_8l_commands as CMD` và gọi `CMD.handle_command(text)` (hoặc `format_topn/format_new/format_vn30`).
- `telegram_recommend.py` — chứa `get_dt5g_state(date)` (đọc BQ `vnindex_5state_dt5g_live`) + `load_config/send_telegram_text`. `bot_8l_commands.format_vn30` cần `get_dt5g_state`.
- `dna_report.py` — block DNA+NOW cho bot (đã repoint sang `vnindex_5state_dt5g_live` 03/06).

## 5. Phụ thuộc ngoài gói (production phải có sẵn)
- **BigQuery**: dataset `tav2_bq` (bảng `ticker`, `ticker_1m`, `ticker_financial`...), auth service-account.
- **Cổng thị trường DT5G**: bảng BQ `tav2_bq.vnindex_5state_dt5g_live` do job market-timing riêng sinh ra (đọc read-only).
- **Env**: `WORKDIR_8L` = thư mục gốc; `DNA_PYEXE` = python interpreter; PATH có `bq` CLI.
- File config Telegram (`telegram_config.json`) **không** kèm gói vì chứa token — dùng template của các bạn.
