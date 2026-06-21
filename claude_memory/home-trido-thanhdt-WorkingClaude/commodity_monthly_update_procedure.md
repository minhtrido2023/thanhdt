---
name: commodity-monthly-update-procedure
description: "data/*_monthly.csv (7 commodity) là NHẬP TAY, không tự cập nhật — staleness làm lệch pctile/verdict 8L cyclical; quy trình refresh chuẩn (FRED/EIA/ycharts + BRENT string trong cyclical_structural.py)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 66803bb4-8954-40d8-8c66-bb6c17436242
---

7 file `data/{urea,dap,iron_ore,rubber,sugar,caustic_soda,brent}_monthly.csv` là dữ liệu **nhập tay** — KHÔNG có job tự cập nhật. [REDACTED]12 production phát hiện đứng ở 2026-03 (3 tháng stale) → đã cập nhật tới 2026-05.

> ⚠️ **NGUỒN GỐC (đính chính [REDACTED]12, production audit):** 5 file `urea/dap/iron_ore/rubber/sugar` + `brent` = dữ liệu **THẬT từ World Bank Pink Sheet** (CMO Historical Monthly, có đúng các commodity này; chỉ 1-3 tháng gần nhất là ước tính tròn nhập tay, flag est). **NHƯNG `caustic_soda_monthly.csv` = SYNTHETIC/BỊA** — World Bank Pink Sheet **KHÔNG có caustic soda** (xác minh trực tiếp file CMO 02/06/2026: 71 commodity, không có caustic). Series này dựng bằng **nội suy tuyến tính** giữa mốc đoán (basis ~700 USD/t + narrative TQ glut): chữ ký 35% điểm nằm thẳng hàng + 53% số tròn/thirds (vs iron_ore 0%/0%, rubber 3%/1% = thật). **Production ĐÚNG khi không tin.** Blast radius = chỉ mã **CSV** (COMMODITY_MAP trong cyclical_structural.py). FIX: rebuild 5+brent từ Pink Sheet xlsx; caustic soda KHÔNG có nguồn WB → cần provider thật (Sunsirs/business-analytiq/Intratec China chlor-alkali) HOẶC bỏ lăng kính caustic, đánh dấu CSV "no reliable commodity proxy".

**Why:** pctile 5y trong `cyclical_structural.py` (ngưỡng >0.75 + AMPLE → AVOID-new; <0.40 → BUY-zone) và `unified_screener.py` tính trực tiếp trên các file này; data cũ làm lệch verdict cyclical (lần này: iron_ore 0.35→0.48 khiến thép HPG/HSG mất BUY-zone; urea 0.90→0.77 vẫn AVOID; DAP 0.70/caustic 0.67 → DDV/LAS/CSV vẫn WAIT).

**How to apply — TỰ ĐỘNG HÓA ([REDACTED]14, ƯU TIÊN SỐ 1):**
- `python auto_update_commodity_wb.py` — **tự dò link Pink Sheet mới nhất từ trang WB** (hash đổi theo tháng, regex HTML + FALLBACK_URL) → tải xlsx về `data/_wb_cache/` → parse → **validate** (định dạng month, tăng dần, dải giá hợp lệ per-commodity bắt lỗi sai cột, không lùi tháng/thu nhỏ chuỗi) → **ghi atomic + .bak** 6 file. Có `--dry-run`, `--url <U>`, `--xlsx <path>` (offline). Tự cập nhật cả khi WB **revise** giá tháng cuối. caustic_soda KHÔNG đụng. Đã test [REDACTED]14: dò đúng link live, tải 574KB, parse 1960→2026-05, 6/6 khớp file hiện có. Lịch định kỳ: Task Scheduler đầu mỗi tháng (lệnh trong docstring). Sau update gợi ý chạy lại cyclical_structural.py.
- (Thủ công, fallback nếu đã có xlsx) `python rebuild_commodity_wb.py "<path-to-xlsx>"` → 6 file từ cột WB (mapping: iron_ore="Iron ore, cfr spot", urea="Urea ", dap="DAP", rubber="Rubber, RSS3", sugar="Sugar, world", brent="Crude oil, Brent"). Cửa sổ 2006-04→latest.
- `cyclical_structural.py` nay **ĐỌC brent từ brent_monthly.csv** (bỏ chuỗi BRENT hard-code; brent là input WB như commodity khác). `caustic_soda` KHÔNG rebuild (no WB source) — giữ synthetic + flag.
- Chạy lại `python cyclical_structural.py` → `python unified_screener.py` để lan truyền. ([REDACTED]12: WB chuẩn làm **dap lật WAIT→AVOID-new** pctile 0.70→0.88, urea 0.77→0.90 — ước tính tay cũ đã sai: urea T4 thật 856.88 vs nhập 740, dap T5 769.5 vs 705.)

**How to apply — FALLBACK (FRED/EIA, nếu không có xlsx; caustic luôn cần nguồn riêng):**
1. FRED (không cần key): `curl "https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>"` — PRUBBUSDM (rubber, cents/lb ×0.0220462→USD/kg), PIORECRUSDM (iron ore, chain MoM% vào basis hiện có), PSUGAISAUSDM (sugar, cents/lb→USD/kg), POILBREUSDM (brent IMF — tham khảo, basis series là EIA cao hơn ~3-4%).
2. Brent: dùng EIA monthly avg; phải sửa **chuỗi BRENT hard-code trong `cyclical_structural.py`** (script ghi đè brent_monthly.csv mỗi lần chạy).
3. Urea/DAP: không còn FRED — dùng ycharts US DAP Gulf spot + tin benchmark (DTN/farmpolicynews/Green Markets); ghi rõ tháng nào là ước lượng. Caustic soda: basis riêng (~700 USD/t), chỉ có narrative TQ glut → extend theo hướng, flag estimate.
4. WB Pink Sheet xlsx công bố trễ nhiều (tải về 6/2026 chỉ tới 12/2024) — không dùng để extend.
5. Chạy lại: `python cyclical_structural.py` → `python unified_screener.py` (job đêm pt_8l_daily sẽ propagate rank_8l/dna_card).

Giá trị 2026-04/05 đã nhập: urea 740/600(est), dap 725.25/705(est), iron_ore 106.21/108.41, rubber 2.56/2.81, sugar 0.31/0.33, caustic 690/680(est), brent 117.29/107.00. Bối cảnh: Hormuz bị phong tỏa 28/02/2026 → urea/DAP/brent spike T3-T4, urea xì hơi từ đầu T5 (NOLA về mức trước chiến tranh ~500 USD/t đầu T6).

Liên quan: [[oil-gas-chain-8l-2026]], [[fa-rating-8l-pergroup-2026]].
