---
kind: derived-file
status: DERIVED — headline CPI khớp NSO thật 13/13 tháng (diff 0,00); lõi khớp 13/13; vàng/USD UNVERIFIED
source: data/fiinprox_cpi_monthly_20260914.csv
group: macro
writer: Mike (thủ công qua MCP tool call, KHÔNG có script/cron)
upstream: FiinXMCP `get_economy(metrics=["cpi"], cpi_scope="inflation", data_type="YoY")` — FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_cpi_monthly` — CPI YoY tháng 2008-01→2026-08 (FiinPro-X trial)

224 dòng. Cột: `month, cpi_yoy_pct` (headline) · `core_yoy_pct` (lạm phát cơ bản, từ 2015-04) ·
`gold_idx_yoy_pct` · `usd_idx_yoy_pct` (chỉ số giá vàng / đô la Mỹ của GSO — KHÔNG phải giá SJC
hay tỷ giá). Harvest 2 lệnh (2008-2016, 2017-2026), filter server-side 4 `type_name`.

## Đối chiếu với `cpi_vn.py` (2026-09-14)

| Tầng cpi_vn.py | n | MAE | max lệch | tháng lệch >1pp |
|---|---|---|---|---|
| T1 NSO thật (2025-06→2026-06) | 13 | 0,00 | 0,00 | 0 |
| T2 nội suy tuyến tính (2011-01→2025-05) | 173 | 0,49 | **2,51** | 30 |
| T3 backfill CEIC (2007→2010, phần chồng 2008+) | 36 | 0,31 | **3,01** | 5 |

- 36 **anchor** của T2 khớp FiinPro ≤0,16pp ⇒ anchor đúng; sai số nằm ở ĐOẠN NỘI SUY giữa anchor.
  Tệ nhất 2019-09/10 (proxy 4,5-4,7 vs thật 2,0-2,2) và 2011-02/03, 2012-02/03/08.
  `cpi_yoy_chg3` (hướng 3 tháng) cùng dấu chỉ **77,5%** số tháng T2.
- T3 sai ở 2009-09/10 (backfill 0,68 / −0,02 vs thật 2,42 / 2,99) và 2010-09→11 (lệch 1,3-2,3pp).
  ⇒ "đáy base-effect −0,02% Oct-2009" trong docstring `cpi_vn.py` là SAI; đáy thật 1,97% (2009-08).

## Bẫy
1. ~~**`NSO_CPI_YOY_AVG_REAL` trong `cpi_vn.py` bị gắn nhãn sai**~~ — **ĐÃ SỬA 2026-09-27**
   (branch `wire/fiinprox-h1-h2-ve-sinh`, job `Taylor_20260927_022319`): đổi tên thành
   `NSO_CPI_CORE_YOY_REAL` + sửa comment. Xác minh lại trước khi đổi: khớp `core_yoy_pct` **13/13**,
   khớp `cpi_yoy_pct` (headline) **0/13** ⇒ đúng là lạm phát CƠ BẢN. `grep --include=*.py` toàn repo
   2026-09-27: **0 file .py nào đọc** tên cũ (chỉ định nghĩa ở `cpi_vn.py`) ⇒ rename không thể làm
   hỏng caller nào.
2. `core_yoy_pct` 2013-12 FiinPro trả `0.0` trơ trọi giữa chuỗi null — đã ghi trống.
3. 2015-09/10 headline = `0` là số thật (giảm phát sát 0), không phải null.
4. Không có cột MoM/nhóm hàng (11 nhóm có sẵn — chưa lấy).

## Nâng status / dùng
- Headline + lõi: DERIVED.

### LIVE từ 2026-09-27 (merge `1546895a`) — `cpi_vn.py` tầng **T1.5**
Branch `wire/fiinprox-h1-h2-ve-sinh`, job `Taylor_20260927_022319`. Thứ tự tầng mới
**T1 > T1.5 > T3 > T2**: T1 (NSO live, 13 tháng) giữ ưu tiên TUYỆT ĐỐI; T1.5 = `cpi_yoy_pct` của
file này phủ 2008-01→2026-08; **T2 và T3 GIỮ NGUYÊN làm fallback** (mất file ⇒ chuỗi byte-identical
với bản trước khi wire — đã assert). Hệ quả: T3 chỉ còn phục vụ 2007 khi có file.

⚠️ **§14 — file là snapshot đông lạnh, không phải feed.** `cpi_vn.cpi_coverage(end)` đọc tháng cuối
**TỪ FILE** (không hardcode) và in cảnh báo MỘT LẦN khi caller hỏi tháng vượt mọi tầng THẬT, nêu rõ
cách sửa = refresh `NSO_CPI_YOY_REAL` từ GSO (refresh FiinPro là bất khả sau 28/09). Hiện tại
`dcf_valuation.py` gọi `end="2026-12-01"` ⇒ cảnh báo đúng 4 tháng 2026-09→12.

Đo thật (`cpi_vn_tier15_selfcheck.py`, 33 assertion, PASS ở 3 TZ, 1 mutation-kill):
- `macro_confidence_regime` đổi nhãn **đúng 27/185 tháng** REG_C và **17/185** REG_B — TRÙNG KHỚP
  danh sách tháng đã công bố ở finding, không hơn không kém; **0 tháng** nằm trong episode lạm phát
  2011 hoặc 2022-H2.
- DCF: CPI TB 5 năm 3,4426% → 3,4147% (Δ −0,0279pp) nhưng `g_term` **bất biến 6,8000%** do trần
  `cap_rf=r_f` ⇒ fair value Δ = **0,0** trên 7/7 mã định giá được. KHÔNG rút gọn thành "CPI không
  ảnh hưởng DCF": đổi `DCF_TERMINAL_MODE` sang `cpi` là −0,0279pp đi thẳng vào `g_term`.
- KHÔNG có bằng chứng nào nói việc này tăng lợi nhuận hay cải thiện chất lượng tín hiệu. Đây là
  VỆ SINH DỮ LIỆU.


### Hậu kiểm sau merge trên `main` (2026-09-27, job `Taylor_20260927_033050`)
`cpi_vn_tier15_selfcheck.py`: **33/33 PASS** ở cả 3 TZ (ICT / UTC / `env -u TZ`), relabel
**REG_C 27/185 · REG_B 17/185** — khớp con số mục trên.
⚠️ **Cách chạy ĐỔI sau merge:** selfcheck là A/B thật, `CPI_OLD_ROOT` mặc định trỏ vào checkout
canonical — sau merge canonical CHÍNH LÀ bản mới ⇒ chạy mặc định **hard-fail**
(`AttributeError: module 'cpi_old' has no attribute 'NSO_CPI_YOY_AVG_REAL'`), KHÔNG phải regression.
Muốn chạy lại phải trỏ `CPI_OLD_ROOT` vào một root có `cpi_vn.py` TRƯỚC merge, ví dụ:
`git show 1546895a^1:./cpi_vn.py` vào một thư mục symlink-mirror của `WorkingClaude/`
(cần `mike/` + `data/macro_features.csv`).

↩ [Về nhóm macro](index.md) · [Về index tổng](../index.md)
