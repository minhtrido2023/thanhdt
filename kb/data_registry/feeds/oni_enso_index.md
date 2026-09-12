---
kind: local-file
status: CANDIDATE-PARTIAL
source: mike/agents/Taylor/research/oni_index_manual_20260912.csv
group: feeds
cadence: KHÔNG tự động — snapshot 1 lần
writer: (thủ công) WebFetch 2026-09-12, không có script/cron
---

# ONI (Oceanic Niño Index) — mike/agents/Taylor/research/oni_index_manual_20260912.csv

**Status: CANDIDATE-PARTIAL** — dữ liệu dùng được cho nghiên cứu khám phá, CHƯA đủ điều kiện
CANONICAL vì không có script fetch lại được (một lần WebFetch, không cron, không idempotent).

## Là gì
Chỉ số ONI (proxy El Niño/La Niña/Neutral chính thức của NOAA CPC), 12 mùa chồng lấn/năm
(DJF, JFM, ..., NDJ), 2006-2025 (234 dòng). Dùng làm biến thủy văn cho nghiên cứu tác động ENSO
lên lợi nhuận nhóm thủy điện VN — xem
[`hydro_hydrology_oni_overlay_20260912.md`](../../../agents/Taylor/research/hydro_hydrology_oni_overlay_20260912.md).

## Ai ghi / cadence
**KHÔNG có cron/script.** Lấy 1 lần bằng WebFetch (model nhỏ tóm tắt HTML từ
`www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/`) ngày 2026-09-12. Trang gốc
`origin.cpc.ncep.noaa.gov/.../ONI_v5.php` (link trong CLAUDE.md gốc) đã REDIRECT sang trang v6 này
và **không resolve DNS được từ sandbox** — phải dùng URL redirect trực tiếp.

## Bẫy

**1. Không phải đọc trực tiếp `oni.ascii.txt` — qua model tóm tắt HTML, có rủi ro sai số/transcribe
nhầm.** Đã cross-check bằng các mốc ENSO nổi tiếng đã biết công khai (El Nino 2015-16 peak 2.6,
La Nina 2020-23 kéo dài 3 năm, El Nino 2023-24 peak 2.0) — khớp. Nhưng chưa verify từng số một
cách máy móc.

**2. Dòng năm 2026 (DJF→JJA trong bản fetch) nằm sau knowledge cutoff của mọi model tham gia —
KHÔNG verify được độc lập.** Đã loại khỏi phân tích định lượng trong memo trên, chỉ giữ tham khảo.
Bất kỳ ai dùng lại file này cho phân tích PHẢI lọc bỏ năm 2026 hoặc verify lại bằng nguồn khác trước.

**3. Muốn nâng CANONICAL**: viết script fetch trực tiếp `oni.ascii.txt` (định dạng cố định dễ parse
hơn HTML rất nhiều — không cần model tóm tắt) + so khớp lại toàn bộ chuỗi 2006-2025 hiện có trước
khi tin. Chưa có script này — đây là việc còn treo nếu nghiên cứu hydro/ENSO tiếp tục.

**4. Có độ trễ revise nhẹ theo thời gian (NOAA đổi chuẩn ERSST version — trang gốc tự nói "bảng
dựa trên ERSSTv5 đã thay bằng v6").** Dùng ONI trễ ≥2 quý so với thời điểm cần dự đoán là đủ an
toàn khỏi look-ahead (xem memo hydro §2).

## Liên quan
- [`hydro_hydrology_oni_overlay_20260912.md`](../../../agents/Taylor/research/hydro_hydrology_oni_overlay_20260912.md) — nghiên cứu dùng file này
- `mike/agents/Taylor/research/hydro_oni_merged_panel_20260912.csv` — panel đã merge ONI + NP thủy điện (BQ `ticker_financial`)
- `mike/agents/Taylor/energy_valuation_framework.md` sector #9 — screen tài chính thủy điện gốc (chưa có biến thủy văn)

↩ [Về index nhóm](index.md)
