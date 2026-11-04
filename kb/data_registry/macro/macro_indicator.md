---
kind: table
status: UNVERIFIED
source: tav2_bq.macro_indicator (TradingEconomics scrape) + view tav2_bq.macro_indicator_latest; 41 series_key / 4 country (VN 26, US 8, CN 6, JP 1)
upstream_true: nhiều nguồn gốc theo series (NSO/SBV/Fed/BLS/NBS/HNX-VBMA…); TE chỉ là aggregator — chưa đối chiếu nguồn thứ hai ngoài vn_bond_10y và (qua kế hoạch C1, chưa chạy) vn_policy_rate / vn_cpi_yoy
group: macro
writer: bq_admin (NGOÀI repo; user xác nhận 2026-11-05, cùng nguồn TradingEconomics với giá hàng hoá). Repo này KHÔNG có script ghi (grep macro_indicator: chỉ reader). Winston không sở hữu, không sửa bảng/view.
cron: ngoài repo, ~15:00 UTC hằng ngày (đo: fetched_at 2026-11-04 15:00:00→15:01:27 UTC, 41 series nối tiếp ~2s/series). Không có dòng crontab của repo.
vintage: đo 2026-11-05 00:1x ICT. Backfill 2026-10-30 07:25 UTC (84.324 dòng, 1 lần) → top-up rời rạc 11-01 (11 dòng), 11-02 (16), 11-03 (9) → 11-04 15:00 UTC đủ 41 series (mỗi series 1 dòng mới). Tổng 84.401 dòng; không có (series, observation_date) trùng.
consumer: dcf_rate_display.py::tpcp_line (vn_bond_10y; HIỂN THỊ, không gate) · research dcf_rate_proxy_20261102 · bin/macro_indicator_freshness.py (kiểm tươi, WARN-only, gọi từ bq_freshness_check.sh) · kế hoạch kb/projects/te-macro-integration-plan-20261104.md (C1/D1/D2/E1/F1 — chưa wire)
verified_by: Winston, job Winston_20261104_170458, đo BQ thật 2026-11-05 (bản trước: Taylor Taylor_20261102_015334 cho vn_bond_10y)
---
# `tav2_bq.macro_indicator` — chỉ báo vĩ mô TradingEconomics (41 series)

**Status: UNVERIFIED** — chỉ `vn_bond_10y` được đối chiếu nguồn thứ hai (lệch hệ thống, xem dưới); 40 series còn lại chưa đối chiếu. Dùng để HIỂN THỊ / nghiên cứu có khai báo; không làm input gate/sizing.

## Cột
`series_key, country, name_en, observation_date (DATE), value (FLOAT), unit, source, source_url, te_slug, fetched_at (TIMESTAMP), extra_json`. Một dòng = (series_key, observation_date); `fetched_at` = lúc scrape.

## View `tav2_bq.macro_indicator_latest`
Do bq_admin sở hữu. Định nghĩa (đọc từ `bq show`): dòng mới nhất mỗi `series_key` theo `observation_date DESC, fetched_at DESC` (ROW_NUMBER, `_rn=1`) ⇒ 41 dòng. Là **view lazy** (numRows 0 trong metadata là bình thường). KHÔNG phải view point-in-time: không có `macro_indicator_pit` (user không duyệt tạo view, 2026-11-05).

## Series theo tần suất (đo 2026-11-05; n = số dòng, khoảng = MIN→MAX observation_date)
**Hằng ngày** (obs cuối 2026-11-04, trừ ghi chú):
| series_key | n | khoảng |
|---|---|---|
| us_sp500 | 10.232 | 1946-11-19 → 2026-11-04 |
| us_bond_10y | 10.295 | 1926-12-01 → 2026-11-04 |
| us_bond_2y | 10.392 | 1976-11-11 → 2026-11-04 |
| us_dxy | 10.695 | 1986-11-10 → 2026-11-04 |
| jp_usdjpy | 8.059 | 1986-11-10 → 2026-11-04 |
| cn_usdcny | 7.572 | 1996-11-06 → 2026-11-04 |
| vn_usdvnd | 5.281 | 2006-11-06 → 2026-11-04 |
| vn_bond_10y | 5.077 | 2007-03-20 → 2026-11-04 |
| vn_interbank_3m | 7.231 | 1998-12-11 → **2026-11-02** (trễ 2d so với nhóm trên) |

**Hằng tháng** (obs = cuối tháng): vn_cpi_yoy (370; 1996-01→2026-10) · vn_cpi_mom (380; 1995-02→2026-09) · vn_core_cpi_yoy (138; 2015-04→2026-09) · vn_policy_rate (319; 2000-04→2026-10) · vn_retail_sales_yoy (284; 2002-03→2026-10) · vn_ind_production_yoy (213; 2009-01→2026-10) · vn_exports (364; 1990-12→2026-09) · vn_imports (360; 1990-12→2026-09) · vn_trade_balance (356; 1990-12→2026-10) · vn_fdi (238; 1991-12→2026-10) · vn_fx_reserves (366; 1995-01→2026-08) · vn_tourist_arrivals (142; 2015-01→2026-10) · vn_car_registrations (243; 2006-07→2026-09) · vn_unemployment (73; 1998-12→2026-09) · vn_wages (66; 2007-12→2026-09) · vn_mfg_pmi (38; 2023-09→2026-10) · us_cpi_yoy (1.341; 1914-12→2026-09) · us_fed_funds_rate (663; 1971-08→2026-10) · us_ism_mfg_pmi (946; 1948-01→2026-10) · us_unemployment (944; 1948-01→2026-09) · cn_cpi_yoy (489; 1986-01→2026-09) · cn_ppi_yoy (405; 1993-01→2026-09) · cn_nbs_mfg_pmi (262; 2005-01→2026-10) · cn_caixin_mfg_pmi (38; 2023-09→2026-10).
**Hằng quý** (obs = cuối quý): vn_gdp_growth_yoy (105; 2000-06→2026-09) · vn_gdp_construction (54; 2013-03→2026-06) · vn_current_account (83; 1983-12→2026-03) · cn_gdp_growth_yoy (142; 1989-12→2026-09).
**Hằng năm**: vn_gdp_nominal (41; →2025-12) · vn_gdp_per_capita (42; →2025-12) · vn_govt_budget_gdp (36; →2024-12) · vn_govt_debt_gdp (26; →2025-12).
Cadence phân loại theo khoảng cách quan sát đo được + bản chất chỉ báo; không có cột cadence trong bảng. Lưu ý: ngày công bố KHÔNG suy được từ bảng (vd `vn_cpi_yoy` có obs 2026-10-31 tại lần scrape 2026-11-04; lúc nó xuất hiện đầu tiên không được ghi) — luôn dùng observation_date.

## Đối chiếu nguồn thứ hai (đo 2026-11-02)
Nguồn B = bản tin VBMA tháng 6 và 7/2026 (vbma.org.vn, lợi suất 10Y cuối tháng: 6/2026 = 4,362%; 7/2026 = 4,403%; tháng 5 suy ra từ "+11bp" = 4,252%).
| Cuối tháng | BQ (TE) | VBMA | Lệch |
|---|---|---|---|
| 2026-05-29 | 4,458 | 4,252 (suy ra) | +0,21 |
| 2026-06-30 | 4,5226 | 4,362 | +0,16 |
| 2026-07-31 | 4,5368 | 4,403 | +0,13 |
Chiều đúng, mức lệch hệ thống +0,13…+0,21pp (TE cao hơn), 1/3 mốc vượt 0,2 và mốc tháng 5 là suy ra. Không tìm được VBMA/HNX cho 2022–2023 và 09–10/2026 (search chuẩn không ra). ⇒ giữ **UNVERIFIED**; Δ12T (cùng nguồn, cùng lệch hệ thống) đáng tin hơn mức tuyệt đối.

## Bẫy
1. **Look-ahead (backtest):** `observation_date` series tháng/quý/năm = CUỐI KỲ tham chiếu, KHÔNG phải ngày công bố. Bảng KHÔNG có cột ngày công bố và KHÔNG có view point-in-time; `fetched_at` chỉ có từ 2026-10-30 (backfill dồn 1 ngày ⇒ vô nghĩa làm ngày công bố lịch sử). Backtest dùng bảng này phải TỰ giả định độ trễ công bố (bảo thủ) ở code nghiên cứu; dùng live (as-of = hôm nay) thì không cần lag. Muốn lag thật ⇒ nhờ bq_admin thêm cột (chưa đề xuất chính thức).
2. **`vn_bond_10y` lệch VBMA +0,13…+0,21pp** — chỉ tin Δ, mức tuyệt đối UNVERIFIED (bảng đối chiếu trên). Dòng hiển thị luôn gắn nhãn UNVERIFIED.
3. **Độ phân giải thập phân không đồng nhất:** backfill 10-30 giữ 4+ chữ số (vd us_sp500 2026-10-28 = 7743,97683) còn dòng hằng ngày chỉ 2 chữ số (2026-10-29 = 7720,39; có chỗ làm tròn nguyên 7679,0) ⇒ không dùng thay đổi tick nhỏ giữa 2 chế độ.
4. **`fetched_at` không phải khoá thời gian** (backfill vs top-up lệch; một ngày có thể bị ghi đè) — dùng observation_date.
5. **Writer ngoài repo:** scrape hỏng thì repo không có gì để sửa — báo bq_admin. Freshness: `bin/macro_indicator_freshness.py` (WARN-only) báo khi 1 trong 6 series hằng ngày (us_sp500, us_bond_10y, us_dxy, vn_usdvnd, vn_bond_10y, cn_usdcny) có observation_date cách hôm nay >3 ngày lịch, thiếu series, hoặc truy vấn lỗi. `vn_interbank_3m`, `us_bond_2y`, `jp_usdjpy` (cũng hằng ngày) CHƯA nằm trong kiểm tươi.
6. Fail-closed phía đọc: quan sát cuối cách asof > 7 ngày ⇒ dòng hiển thị in "không có dữ liệu", không điền số cũ.
