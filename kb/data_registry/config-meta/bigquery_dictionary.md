---
kind: config
status: CANONICAL
source: bigquery_dictionary.json
group: config-meta
note: đã có tiền lệ mô tả SAI đơn vị (dễ lọt review công thức)
writer: cập nhật tay khi schema đổi
---

# bigquery_dictionary.json

**Status: CANONICAL (dictionary), nhưng đã có tiền lệ mô tả sai đơn vị**

## Là gì
Semantic dictionary mọi cột BQ — tra TRƯỚC khi viết filter/query.

## Ai ghi / cadence
Cập nhật tay khi schema đổi.

## Bẫy
**Bẫy "đọc dict rồi viết công thức sai đơn vị"** (không phải sai bảng/tên như trap `vnindex_5state`, mà
đơn vị field mô tả sai trong lúc TÊN field trông hợp lý — dễ lọt qua review công thức vì trông "đúng
logic"): (1) **`CF_OA_P0` (2026-07-20, job `Taylor_20260720_111429`/`Winston_20260720_114006`)** — dict
cũ ghi "Cashflow over assets" (ngụ ý tỷ lệ 0..1) nhưng thực tế là **VND thô** (HPG 2026Q1 = 6.82e12,
cùng bậc với NP_P0). Đã sửa mô tả trong dict. Hậu quả thật: prototype R&D `ic_panel_ext_q3.py:57-60` (H4
accruals, kết quả CLOSED ghi ở `data/results_registry.md` mục `## 🟢 REAL-MARGIN self-check FIXED +
1.3x chốt làm trần...` — phần "T2 IC-PANEL EXTENSION", dòng "H4 accruals... INVALID (unit bug)";
cite by section title, số dòng trong sổ cái này trôi mỗi lần chèn mục mới) trừ nhầm 1 SỐ TIỀN THÔ cho 1 TỶ
LỆ → kết quả đã bị đánh dấu INVALID (không xoá, chỉ dán cảnh báo). Đã có tiền lệ mờ hơn ở
[`../fundamentals/roe_roic_fscore_quality.md`](../fundamentals/roe_roic_fscore_quality.md) (`CF_OA_3Y`)
ghi "KHÔNG phải sum ratio" nhưng chưa lan sang sửa field gốc `CF_OA_P0` — bài học: khi phát hiện 1
field con sai đơn vị, PHẢI kiểm tra hết field liên quan cùng họ, không dừng ở field đang xét. (2)
**`GPM_P0` (cùng job)** — dict cũ ghi "(%)" nhưng thực tế là **tỷ lệ 0..1** (VNM 2026Q1 = 0.417, không
phải 41.7). Production KHÔNG bị ảnh hưởng (đã grep xác nhận: mọi consumer CF_OA dùng sign-test hoặc tỷ
số cùng đơn vị; mọi consumer GPM dùng hiệu cùng đơn vị) — chỉ hại nghiên cứu proxy đọc dict rồi viết
công thức mới từ đầu. **Cảnh giác:** `GPM_P1..P7` và `CF_OA_P1..P4` (các biến thể quý khác cùng field)
CHƯA được audit riêng lẻ trong lần sửa này — dispatch chỉ yêu cầu sửa đúng `_P0`; giả định các
`_P1..P7` cùng họ cùng đơn vị nhưng CHƯA verify bằng số thật, tự kiểm tra trước khi dùng.
