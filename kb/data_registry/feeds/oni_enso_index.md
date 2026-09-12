---
kind: local-file
status: CANONICAL
source: data/oni_index.csv
group: feeds
cadence: THÁNG (~ giữa tháng theo lịch publish CPC) — cron ĐỀ XUẤT, CHƯA cài (xem "Bẫy" #3)
writer: oni_index_feed.py
---

# data/oni_index.csv

**Status: CANONICAL** (nâng từ CANDIDATE-PARTIAL 2026-09-12, job `Taylor_20260912_081906`).

## Là gì
Chỉ số ONI (Oceanic Niño Index — proxy El Niño/La Niña/Neutral chính thức của NOAA CPC), 12 mùa
chồng lấn/năm (DJF, JFM, ..., NDJ), **919 dòng, 1950→JJA 2026** (full history, không cắt ở 2006
như bản cũ). Dùng làm biến thủy văn cho nghiên cứu tác động ENSO lên lợi nhuận nhóm thủy điện VN
— xem [`hydro_hydrology_oni_overlay_20260912.md`](../../../agents/Taylor/research/hydro_hydrology_oni_overlay_20260912.md).

Cột: `year,season,total,anom` (`total` = SST vùng Niño-3.4 độ C, `anom` = độ lệch so với chuẩn
30 năm trượt — đây là cột dùng cho phân loại El Niño/La Niña/Neutral, ngưỡng ±0.5).

## Ai ghi / cadence
**`oni_index_feed.py`** (root `WorkingClaude/`) — fetch trực tiếp
`https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt` (fixed-width ASCII, parse thẳng bằng
`str.split()`, KHÔNG qua WebFetch/model tóm tắt HTML — xoá bẫy #1 của bản CANDIDATE-PARTIAL cũ).
Idempotent: mỗi lần chạy ghi đè toàn bộ `data/oni_index.csv` từ nguồn gốc (không phải append —
nguồn NOAA tự chứa toàn bộ lịch sử 1950→nay mỗi lần fetch, không cần merge).

```bash
python3 /home/trido/thanhdt/WorkingClaude/oni_index_feed.py            # full history
python3 /home/trido/thanhdt/WorkingClaude/oni_index_feed.py --since 2006  # lọc năm >= 2006
```

**Cron: ĐỀ XUẤT, CHƯA CÀI** — xem Bẫy #3.

## Bẫy

**1. [ĐÃ SỬA] Trước đây qua model tóm tắt HTML (bản `oni_index_manual_20260912.csv`), giờ đọc
thẳng ASCII cố định.** Cross-check máy móc TOÀN BỘ 234 điểm chung 2006-2025 giữa bản mới (fetch
trực tiếp) và bản cũ (model tóm tắt): **224/234 khớp tuyệt đối (95,7%)**, 10/234 lệch — TẤT CẢ
10 điểm lệch đúng **0,05** (vd (2007,ASO): mới -1,05 vs cũ -1,00; (2018,NDJ): mới 1,05 vs cũ 1,10).
Không có lệch > 0,05, không có lệch dấu/nhầm mùa/nhầm năm. Diễn giải: khớp với ghi chú NOAA "bảng
dựa trên ERSSTv5 đã thay bằng v6" (bẫy #4 cũ) — chênh 0,05 nhất quán giống dấu hiệu revise chuẩn
SST hơn là lỗi transcribe của model. **Kết luận: bản CANDIDATE-PARTIAL cũ đủ tin cậy cho việc đã
dùng nó (memo hydro §3.2), nhưng từ giờ dùng bản CANONICAL này làm nguồn duy nhất.**

**2. Dòng năm 2026 (DJF→JJA, ANOM tới +1.80) là mùa ĐANG DIỄN RA / El Niño LIVE — KHÔNG dùng cho
backtest coi như đã kết thúc.** JJA 2026 ANOM=1.80 đã verify khớp ENSO Diagnostic Discussion CPC
2026-09-10 ("Niño-3.4 reached +1.8°C in August"). Dùng ONI trễ ≥2 quý so với thời điểm cần dự đoán
là đủ an toàn khỏi look-ahead (memo hydro §2) — GIỮ NGUYÊN caveat này từ bản cũ.

**3. [MỚI] Cron CHƯA cài — sandbox agent bị permission classifier chặn thao tác `crontab` (thay
đổi hệ thống dùng chung, cần xác nhận tương tác).** Dòng đề xuất (theo đúng pattern
`hog_price_feed.py`, đã ghi vào `kb/cron_registry.md`):
```
0 2 20 * * /usr/bin/python3 /home/trido/thanhdt/WorkingClaude/oni_index_feed.py >> /home/trido/thanhdt/WorkingClaude/logs/oni_index_feed.log 2>&1
```
= 09:00 ICT ngày 20 hàng tháng (NOAA CPC publish ONI update quanh giữa tháng — không có ngày cố
định công bố chính thức, ngày 20 là biên an toàn sau mốc publish thường gặp). Ai cài (Mike/user
qua `crontab -e`) nhớ verify chạy tay 1 lần trước, và note lại mtime thật vào đây.

**4. Không phải cron TỰ ĐỘNG chưa cài thì dữ liệu cũ.** File `data/oni_index.csv` đã fetch tay
thành công 2026-09-12 (919 dòng, latest JJA 2026). Chạy lại tay bất kỳ lúc nào cần dữ liệu mới hơn,
không phụ thuộc cron.

## Liên quan
- [`hydro_hydrology_oni_overlay_20260912.md`](../../../agents/Taylor/research/hydro_hydrology_oni_overlay_20260912.md) — nghiên cứu dùng file này
- `mike/agents/Taylor/research/oni_index_manual_20260912.csv` — snapshot thủ công cũ, GIỮ LẠI làm lịch sử/audit (guidelines §8), không dùng cho việc mới
- `mike/agents/Taylor/research/hydro_oni_merged_panel_20260912.csv` — panel đã merge ONI + NP thủy điện (BQ `ticker_financial`)
- `mike/agents/Taylor/energy_valuation_framework.md` sector #9 — screen tài chính thủy điện gốc (chưa có biến thủy văn)

↩ [Về index nhóm](index.md)
