---
kind: project
owner: Winston
status: closed
updated: 2026-11-19
title: "Yêu cầu bq_admin — lấp khoảng trống dữ liệu (8 mục) · 19/11/2026"
---
# Yêu cầu bq_admin — lấp khoảng trống dữ liệu (8 mục) · 19/11/2026

> Soạn bởi Winston (job `Winston_20261119_090441`) theo `agents/Taylor/research/arch_8l_dt5g_data_leverage_20261119/REPORT.md` §8; user duyệt 19/11. **Văn bản để user chuyển tay cho bq_admin — KHÔNG gọi bq_admin trực tiếp.**
> Mọi số "hiện trạng" đo ngày 19/11/2026 (REPORT §1; riêng #2 đo lại bằng lệnh ghi ở mục). Khi nhận hàng, người nghiệm thu chạy đúng câu SQL ở cột "Nghiệm thu"; trả kết quả vào ô `Kết quả` bên dưới.
> **Không lặp** yêu cầu 26/10 (`kb/projects/bq-admin-commodity-feed-request-20261026.md`): mục 5 chỉ tham chiếu + đánh dấu những gì vẫn chưa có.
> Project `lithe-record-440915-m9`, dataset `tav2_bq`. Ghi chú chung: bảng mới/cột mới **không ghi đè** `fetched_at`/`first_seen_at` ở lần nạp sau (xem #2); fleet đã tự chụp vintage từ 19/11/2026 ở `tav2_mike.{macro_indicator,commodity_prices}_vintage` — đó là LƯỚI AN TOÀN, không thay cho #2.

## Bảng ưu tiên

| # | Hạng mục | Ưu tiên | Người dùng chốt |
|---|---|---|---|
| 1 | Dòng tiền ngoại/tự doanh toàn universe | **P1** | user chỉ định |
| 2 | `first_seen_at` / ngày công bố cho `macro_indicator` | **P1** | user chỉ định |
| 7 | Chất lượng tài sản ngân hàng (NPL/coverage/CAR/CASA) sau 2026Q2 | **P1** | user chỉ định |
| 3 | TE monthly dừng nạp từ 25/10 | P2 (rẻ, chỉ cần xác nhận) | — |
| 4 | `vn30f_daily` đứng từ 08/06 | P2 (rẻ) | — |
| 6 | Hoạt động ngành (tín dụng/huy động, đầu tư công, điện, cảng, BĐS, TPDN, margin) | P3 | — |
| 5 | Chuỗi hàng hoá còn thiếu (đã xin 26/10) | P3 | — |
| 8 | Tin tức chung theo mã | P4 (chỉ khi user theo hướng "feature ngoài giá") | — |

---

## 1. Dòng tiền khối ngoại + tự doanh toàn universe — **P1**
- **Hiện trạng:** `ticker_foreign_flow` 10.812 dòng, **3 mã** (FPT từ 2006-12-13, SHS từ 2009-06-25, ROS 2016-09→2022-08); `ticker_prop_flow` 2.909 dòng, **3 mã**, 1–2 mã/phiên. Tạo 18/11, nạp một lượt, 0 consumer. Cấp chỉ số NO-GO hai lần ⇒ cần cấp **mã** để kiểm lại đúng chỗ.
- **Cần:** giữ nguyên schema 2 bảng hiện có (cột `foreign_*_total/matched/deal`, `foreign_net_*`, `foreign_room_*`, `total_trade_net_*` của prop…). Nạp cho **mọi mã trong `tav2_mike.universe_pit`** (334 mã ở phiên 18/11 theo REPORT §8) + dòng cấp chỉ số **VNINDEX, VN30** (dùng `ticker` = mã chỉ số, ghi rõ trong mô tả bảng). Tần suất: hằng ngày sau đóng cửa, trước 23:00 ICT.
- **Phạm vi ngày:** từ **2014-01-02** (hoặc xa nhất nguồn có; ghi rõ ngày bắt đầu thật từng mã) → hôm nay; nạp đuổi hằng ngày.
- **PIT:** `fetched_at` = lần nạp ĐẦU của dòng (không ghi đè khi nạp lại); nếu nguồn sửa số, thêm dòng mới hoặc cột `revised_at`, không UPDATE tại chỗ.
- **Nghiệm thu (đều bằng 1 câu):**
  - Phủ mã: `SELECT COUNT(DISTINCT f.ticker) FROM tav2_bq.ticker_foreign_flow f JOIN tav2_mike.universe_pit u ON u.ticker=f.ticker AND u.time=f.time WHERE f.time=(SELECT MAX(time) FROM tav2_bq.ticker_foreign_flow)` ≥ 95% số mã `universe_pit` cùng ngày (cùng câu cho `ticker_prop_flow`).
  - Lịch sử: `SELECT COUNTIF(n>=900) / COUNT(*) FROM (SELECT ticker, COUNT(*) n FROM tav2_bq.ticker_foreign_flow WHERE time BETWEEN '2014-01-02' AND '2018-12-31' GROUP BY 1)` ≥ 0,8 trên các mã có giao dịch cả giai đoạn.
  - Chỉ số: `SELECT COUNT(DISTINCT ticker) FROM tav2_bq.ticker_foreign_flow WHERE ticker IN ('VNINDEX','VN30')` = 2.
  - Tươi: `SELECT MAX(time) FROM tav2_bq.ticker_foreign_flow` = phiên giao dịch gần nhất (≤1 phiên trễ).
  - Không NULL hàng loạt: `SELECT COUNTIF(foreign_net_value_total IS NULL)/COUNT(*) FROM tav2_bq.ticker_foreign_flow WHERE time>='2020-01-01'` < 0,02 (hiện 184 NULL trên 10.812 dòng ≈ 1,7%).

## 2. `macro_indicator` — ngày công bố / `first_seen_at` — **P1**
- **Hiện trạng:** 84.491 dòng, 41 series. `fetched_at` bị ghi đè mỗi lần scrape (đo: `vn_cpi_yoy` obs 2026-10-31 — registry 05/11 ghi đã thấy ở lần scrape 04/11, nay `MIN(fetched_at)` của chính dòng đó = 2026-11-18; 15 giá trị `fetched_at` khác nhau 30/10→18/11) ⇒ không dựng được ngày thấy-lần-đầu. Cột hiện có: `series_key, country, name_en, observation_date, value, unit, source, source_url, te_slug, fetched_at, extra_json`.
- **Cần:** thêm 2 cột (tuỳ nguồn cung cấp được cái nào): `first_seen_at TIMESTAMP` (UTC lần đầu pipeline nhìn thấy cặp `(series_key, country, observation_date)`; **không bao giờ cập nhật lại**) và `release_date DATE` (ngày công bố chính thức nếu nguồn có, vd lịch TE; NULL nếu không). Nếu có revise giá trị: giữ `first_seen_at` của dòng gốc, thêm `value_revised_at`.
- **Backfill:** KHÔNG cần giả lập quá khứ — dòng cũ để `first_seen_at` = ngày nạp lần đầu thật nếu còn log, ngược lại NULL (ghi rõ trong mô tả cột; **không điền ngày giả**). Fleet đã giữ vintage thật từ snapshot 2026-11-19.
- **Nghiệm thu:**
  - Cột tồn tại: `SELECT column_name FROM tav2_bq.INFORMATION_SCHEMA.COLUMNS WHERE table_name='macro_indicator' AND column_name IN ('first_seen_at','release_date')` trả 2 dòng (hoặc ít nhất `first_seen_at`).
  - Không ghi đè: chạy scrape 2 lần cách ≥1 ngày rồi `SELECT COUNT(*) FROM (SELECT series_key,country,observation_date FROM tav2_bq.macro_indicator GROUP BY 1,2,3 HAVING COUNT(DISTINCT first_seen_at)>1)` = 0.
  - Đúng nghĩa: `SELECT COUNT(*) FROM tav2_bq.macro_indicator WHERE first_seen_at < TIMESTAMP(observation_date)` = 0 (không thấy trước ngày quan sát).
  - Phủ dòng mới: `SELECT COUNTIF(first_seen_at IS NULL)/COUNT(*) FROM tav2_bq.macro_indicator WHERE observation_date>='2026-11-19'` = 0.

## 3. TE monthly dừng nạp — P2
- **Hiện trạng:** `commodity_prices` nguồn TE cadence `monthly`: 103 mã, 42.041 dòng, tới obs 2026-10-22; lần nạp cuối 2026-10-25; monitor báo 20 khoá STALE (28–31 ngày). Fleet không biết là chủ ý hay lỗi.
- **Cần:** trả lời một trong hai: (a) lỗi ⇒ nối lại nạp; (b) chủ ý ⇒ xoá/đánh dấu hẳn (cột `status='retired'` hoặc bỏ khỏi bảng) để consumer không đọc nhầm. Nếu (a): lịch nạp hằng tháng ghi rõ ngày.
- **Nghiệm thu:** `SELECT MAX(fetched_at) FROM tav2_bq.commodity_prices WHERE source='trading_economics' AND cadence='monthly'` > 2026-11-19 (nếu nối lại); hoặc (nếu retire) `SELECT COUNT(*) FROM tav2_bq.commodity_prices WHERE source='trading_economics' AND cadence='monthly' AND (status IS NULL OR status<>'retired')` = 0 (hoặc bảng không còn dòng TE monthly), kèm văn bản xác nhận chủ ý.

## 4. `vn30f_daily` đứng từ 2026-06-08 — P2
- **Hiện trạng:** 2.188 dòng, 2017-08-10 → **2026-06-08**, không cron; chỉ 1 script cũ dùng (REPORT: CHẾT).
- **Cần:** (a) nối lại nạp hằng ngày + lấp khoảng 09/06→nay, hoặc (b) xác nhận bỏ và đổi tên `vn30f_daily_DEPRECATED`. Fleet chỉ cần câu trả lời; nếu nối lại thì giữ schema (`f1m_*`, `f2m_close`, `spot_vn30`, `basis`, `basis_pct`).
- **Nghiệm thu:** `SELECT MAX(time) FROM tav2_bq.vn30f_daily` = phiên gần nhất (≤1 phiên) và `SELECT COUNT(*) FROM tav2_bq.vn30f_daily WHERE time>'2026-06-08'` ≥ số phiên từ 09/06 đến nay; hoặc bảng đã đổi tên + thông báo.

## 5. Chuỗi hàng hoá còn thiếu (đã xin 26/10 — CHƯA có) — P3
- **Tham chiếu đầy đủ (mã CP, vì sao, nguồn gợi ý):** `kb/projects/bq-admin-commodity-feed-request-20261026.md`. **Không lặp lại ở đây**; chỉ nhắc để bq_admin trả lời tình trạng: BDTI/BCTI (PVT, VIP, GSP) · HRC Trung Quốc/VN (HPG) · cá tra, tôm (VHC, ANV, IDI) · Robusta/tiêu/điều/gạo VN 5% theo ngày · NH3 Tampa CFR · kali theo ngày · **vonfram trước 2026-06** (MSR; chuỗi APT hiện chỉ từ 2026-06).
- **Cần thêm so với 26/10:** với mỗi chuỗi nạp mới, ghi `cadence` đúng (daily/weekly/monthly) và `unit` + định nghĩa hàng trong `name_en`; dòng lịch sử nạp đuổi có `fetched_at` = thời điểm nạp thật (không giả).
- **Nghiệm thu (mỗi chuỗi):** `SELECT metric_key, MIN(observation_date), MAX(observation_date), COUNT(*) FROM tav2_bq.commodity_prices WHERE metric_key='<khoá_thoả_thuận>' GROUP BY 1` — `MAX` ≤ 3 ngày với chuỗi daily, ≥ 5 năm lịch sử (≥ 1.000 dòng với daily). Danh sách khoá do bq_admin đề xuất rồi người nhận ghi vào bảng này.

## 6. Hoạt động ngành chưa có trong DB — P3
- **Hiện trạng:** tín dụng & huy động toàn hệ thống theo tháng: snapshot FiinPro dừng 2026-07, chuỗi tiền gửi gãy từ 10/2025. Các mục sau KHÔNG có trong DB: giải ngân đầu tư công tháng · sản lượng điện + giá thị trường điện + cơ cấu thuỷ/nhiệt điện (38 mã tuyến POWER) · sản lượng container qua cảng · doanh số căn hộ sơ cấp · phát hành & chậm trả TPDN · dư nợ margin toàn thị trường.
- **Cần:** một bảng dài (cùng khuôn `macro_indicator`: `series_key, country, observation_date, value, unit, source, source_url, first_seen_at`) cho từng chuỗi, tần suất tháng/quý, lịch sử ≥ 2014 nếu có (tối thiểu 36 tháng); đề xuất nguồn: NHNN/TCTK/Bộ Tài chính/EVN-A0/VPA/HoREA-CBRE/HNX/UBCKNN (**ước lượng — bq_admin kiểm tra**). Nếu nguồn chỉ có trong PDF/báo cáo, ghi rõ để fleet cân nhắc OCR riêng.
- **Nghiệm thu (mỗi chuỗi):** `SELECT series_key, MIN(observation_date), MAX(observation_date), COUNT(*) FROM tav2_bq.macro_indicator WHERE series_key='<khoá>' GROUP BY 1` — số tháng ≥ 36, `MAX(observation_date)` trong vòng 2 kỳ báo cáo của nguồn.

## 7. Chất lượng tài sản ngân hàng sau 2026Q2 — **P1**
- **Hiện trạng:** lens ngân hàng 8L `BLOCKED-STALE`/`PARTIAL`: NPL/LLR chỉ tới 2026Q2; CAR/CASA không tái lập; **10/28 mã BANK ở nhánh `bank-nodata`** (VAB, KLB, NVB, PGB, SGB, PCB, ABB, BAB, BVB, VBB), 9 mã nhận rating 3 mặc định trong `data/rating_8l.csv` (cột hiển thị/discretionary; ĐƯỜNG TIỀN LAG/BAL/custom30V đọc `tav2_bq.fa_ratings_8l` nên 4 mã ABB/PCB/VAB/VBB vẫn =3 bằng proxy ROE và KLB =2 — đính chính 19/11 sau arch-review; nhu cầu dữ liệu NPL/CAR/CASA vẫn nguyên); ngân hàng chiếm 25,9% thanh khoản universe. `ticker_financial` không có cột NPL/CASA/CAR (đã ghi ở `kb/data_registry/fundamentals/bank_casa_ldr.md`); bản phái sinh `fiinprox_bank_ratios_quarterly` chỉ 27 mã tới 2026Q2.
- **Cần:** bảng quý `tav2_bq.bank_asset_quality` (hoặc cột vào `ticker_financial` cho mã ngân hàng) với: `ticker, quarter, time, Release_Date`(ngày công bố BCTC — bắt buộc cho PIT), `npl_ratio` (nhóm 3-5 / dư nợ, %), `npl_group2_ratio` (nợ nhóm 2 nếu có), `llr_coverage` (dự phòng/nợ xấu, %), `car` (%), `casa_ratio` (%), `nim` (nếu có), `ldr`, `credit_growth_ytd`. Cả **28 mã BANK** (đặc biệt 10 mã `bank-nodata`), **2018Q1 → 2026Q3** (Q3 công bố 10/2026), cập nhật mỗi quý trong vòng 5 ngày làm việc sau ngày công bố BCTC. Ghi `source` (BCTC/thuyết minh/công bố TCTD) + `first_seen_at`.
- **Nghiệm thu:**
  - Phủ mã: `SELECT COUNT(DISTINCT ticker) FROM tav2_bq.bank_asset_quality WHERE quarter='2026Q3' AND npl_ratio IS NOT NULL` ≥ 26 (trên 28 mã; ghi rõ mã nào thiếu và vì sao).
  - Phủ riêng 10 mã nodata: `SELECT COUNT(DISTINCT ticker) FROM tav2_bq.bank_asset_quality WHERE ticker IN ('VAB','KLB','NVB','PGB','SGB','PCB','ABB','BAB','BVB','VBB') AND quarter='2026Q2' AND npl_ratio IS NOT NULL` ≥ 8.
  - Lịch sử: `SELECT COUNT(*) FROM (SELECT ticker FROM tav2_bq.bank_asset_quality WHERE time>='2018-01-01' GROUP BY 1 HAVING COUNT(DISTINCT quarter)>=28)` ≥ 20.
  - PIT: `SELECT COUNTIF(Release_Date IS NULL OR Release_Date<time)/COUNT(*) FROM tav2_bq.bank_asset_quality` < 0,02.
  - Đúng khoảng: `SELECT COUNTIF(npl_ratio<0 OR npl_ratio>30 OR car<4 OR car>40) FROM tav2_bq.bank_asset_quality` = 0 (bắt nhầm đơn vị % vs tỷ lệ).
  - Đối chiếu độc lập: 5 mã bất kỳ khớp BCTC gốc ≤ 0,05pp (người nhận cung cấp bảng đối chiếu).

## 8. Tin tức chung theo mã — P4 (chỉ khi user theo hướng "feature ngoài giá" cho LAG)
- **Hiện trạng:** `stock_news` 60.709 dòng, 1.740 mã, 2015-03-02 → 2026-11-17; chỉ 8 mã sự kiện doanh nghiệp (DIV 31.694 · MA 14.167 · ISS 13.653 · BUYBACK 2.392 · AIS 1.839 · SUSP 1.082 · MOVE 186 · NLIS 173); 2020–21 dày (~11.200 dòng/năm) so ~4.000 các năm khác ⇒ không đồng nhất theo thời gian. Cột: `id, ticker, news_id, title, short_content, public_date, public_datetime, matched_event_codes, action_type, …, first_ingested_at, ingested_at`.
- **Cần:** (a) tin tức theo mã ngoài 8 loại (kết quả kinh doanh, hợp đồng lớn, thay đổi lãnh đạo, kiện tụng/thanh tra, cảnh báo/kiểm soát, giải trình, nghị quyết ĐHCĐ…); (b) `matched_event_codes` mở rộng + từ điển mã ở bảng riêng; (c) `public_datetime` đầy đủ giờ (PIT trong phiên) và `first_ingested_at` không ghi đè. Phạm vi: universe_pit từ 2018.
- **Nghiệm thu:** `SELECT COUNT(DISTINCT code) FROM tav2_bq.stock_news, UNNEST(SPLIT(matched_event_codes,',')) code` ≥ 15; `SELECT COUNTIF(public_datetime IS NULL)/COUNT(*) FROM tav2_bq.stock_news WHERE public_date>='2024-01-01'` < 0,05; số dòng/năm 2022–2025 không lệch quá 2× nhau (`SELECT EXTRACT(YEAR FROM public_date) y, COUNT(*) FROM tav2_bq.stock_news WHERE public_date>='2022-01-01' GROUP BY 1`).

---

## Ô trả lời (bq_admin / người nhận điền)
| # | Nhận? (Y/N/một phần) | Hạn dự kiến | Kết quả nghiệm thu (dán output SQL) | Ghi chú |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
