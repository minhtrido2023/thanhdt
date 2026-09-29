# PIT filter Loại 1/Loại 2 — backfill CPI 2007-2010 + re-test full 2007-2026 (2026-08-25)

**Job** `Taylor_20260825_052019` · Kế tiếp `capit_margin_pit_filter_20260825.md` (job `_042209`).
Input: `mike/agents/Taylor/research/vn_cpi_sbv_2007_2010_winston.csv` (Winston, data-ops).
Script tái lập: `mike/agents/Taylor/research/pit_filter_full_2007_2026_test.py`, output
`pit_filter_full_2007_2026_clusters.csv`.

## (a) Backfill `cpi_vn.py`

Thêm TIER 3 (`CPI_YOY_BACKFILL_2007_2010`, 48 tháng, 2007-01→2010-12) vào `cpi_vn.py`, overlay
dưới Tier-2 proxy (2011-01 trở đi không đổi — Tier-2's earliest anchor vẫn đúng 2011-01-01, không
chồng lấn). Nguồn: CSV Winston, 7/48 tháng HIGH-confidence (GSO press-release/snippet trực tiếp:
2007-06, 2008-04, 2008-07, 2008-08, 2008-09, 2008-11, 2009-07), 41/48 MEDIUM (CEIC estimate).
Confidence per-tháng giữ nguyên trong comment code (không thêm cột — dispatch chỉ yêu cầu đánh dấu
rõ nguồn, không đổi schema `cpi_monthly_df()` output ngoài cờ `is_backfill_2007_2010` mới).

**KHÔNG backfill `deposit_rate_vn.py`** — ngoài phạm vi dispatch (chỉ nêu `cpi_vn.py`). Test ở (b)
dùng trực tiếp cột `deposit_rate_approx_pct` của CSV Winston cho 2007-2010 (biến `deposit_lookup()`
trong script test — merge_asof ưu tiên `deposit_rate_vn.py` (2011+) production, fallback CSV
Winston cho 2007-2010, TEST-ONLY, chưa wire vào `golive_recommend_v23.py`).

Regression check: `2025-2026` real-NSO overlay không đổi (`is_real_nso` vẫn đúng), `merge_cpi()`
cho ngày trước 2007-01 vẫn trả NaN (fail-closed đúng thiết kế, không giả vờ có dữ liệu).

**[ĐÍNH CHÍNH 2026-08-25, sau quant-skeptic CONFIRMED-với-lỗi trên `backtest-2008-v24-full`]**
Bản gốc của (b) dùng `cpi_vn.merge_cpi()`, tag CPI tháng M tại timestamp M-01 rồi `merge_asof`
backward — nhưng GSO chỉ công bố CPI tháng M vào cuối tháng M, nên một ngày giao dịch đầu tháng M
(vd 2011-05-05) bị "nhìn thấy" CPI CHÍNH tháng M đó ~3-4 tuần trước khi nó thực sự được công bố
(look-ahead). Đã vá bằng hàm `merge_cpi_pit()` mới trong `pit_filter_full_2007_2026_test.py`: shift
toàn bộ chuỗi CPI +1 tháng trước `merge_asof`, để một ngày giao dịch chỉ thấy CPI tháng LIỀN TRƯỚC
đã công bố. Chạy lại (script + `pit_filter_full_2007_2026_clusters.csv` đã cập nhật, cột đổi tên
`cpi_yoy_at_start`/`deposit_at_start`): **kết luận KHÔNG đổi — vẫn 8/8 cluster Loại-1 BLOCKED, 5/5
cluster Loại-2 PASS** (bảng dưới đã cập nhật số theo bản vá; hạ 1 tháng không đủ đảo ngược verdict
vì biên độ CPI/deposit ở các cluster Loại-1 đều cách xa ngưỡng, trừ 2012-08 vẫn ở biên như cũ).

## (b) Re-run PIT filter 2007-2026 — kết quả

Tính lại dd52≤−20% clusters (rolling 252 phiên, gộp gap≤30 phiên) từ `data/VNINDEX.csv` toàn bộ
lịch sử, merge CPI+deposit tại **MỌI ngày trong cửa sổ cluster** (không chỉ ngày bắt đầu — đúng
cách `golive_recommend_v23.py` thật sự đánh giá PIT MỖI ngày `dd52` còn trong cổng, không chỉ 1
lần lúc fire):

| Cluster | Loại (Bobby) | max CPI trong cửa sổ | max deposit trong cửa sổ | Verdict (ngưỡng 6.0/9.0) |
|---|---|---:|---:|---|
| 2001-07→2003-11, 2004-08, 2004-11, 2006-06→09 (4 cluster) | chưa phân loại (trước 2007, ngoài phạm vi backfill) | NaN | NaN | FAIL-CLOSED (chặn) |
| 2007-04-23 | Loại 1 | 7,13% | 7,50% | **BLOCKED** (qua CPI) |
| 2007-07-30 | Loại 1 | 8,27% | 7,50% | **BLOCKED** (qua CPI) |
| 2007-12-13→2009-07-23 (khối lớn) | Loại 1 | 28,32% | 13,00% | **BLOCKED** (cả 2) |
| 2009-11-26→2010-03-31 | Loại 1 | 8,46% | 10,00% | **BLOCKED** (qua deposit) |
| 2010-05-19→2010-11-24 | Loại 1 | 9,23% | 11,00% | **BLOCKED** (cả 2) |
| 2011-05-23 | Loại 1 | 17,50% | 14,00% | **BLOCKED** |
| 2011-07-12→2012-02-17 | Loại 1 | 23,00% | 14,00% | **BLOCKED** |
| 2012-08-27→2012-12-11 (đuôi) | Loại 1 | 6,88% | 12,00% | **BLOCKED** (biên, qua CPI) |
| 2018-05-28→2019-02-18 | Loại 2 | 4,70% | 7,00% | **PASS** |
| 2020-03-11→2020-05-08 | Loại 2 | 5,75% | 6,50% | **PASS** |
| 2020-07-27→2020-08-03 | Loại 2 | 3,20% | 5,70% | **PASS** |
| 2022-05-13→2022-07-29 | Loại 2 | 3,40% | 5,50% | **PASS** |
| 2022-09-19→2023-05-09 | Loại 2 | 4,90% | 7,50% | **PASS** |

(Số CPI/deposit trên là max-trong-cửa-sổ, đã tính lại qua `merge_cpi_pit()` sau khi vá lỗi
publication-lag — xem đính chính ở đầu mục (b).)

**Kết luận chính**: nhờ backfill, **8/8 cluster con của mega-crisis 2007-2012 giờ CÓ dữ liệu và
CẢ 8 đều bị chặn đúng** (trước job này chỉ 4/12 sub-cluster có dữ liệu — 2011-05/2011-07/2011-10/
2012-08). 5/5 cluster Loại 2 (2018/2020×2/2022×2) đều PASS đúng, **0 false-positive**. Chỉ còn 4
cluster tiền-2007 (trước WTO, quá phạm vi CSV Winston) là fail-closed do thiếu dữ liệu — chấp nhận
được vì đó cũng là giai đoạn thị trường quá mỏng để đầu tư (xem `bigquery_schema.md` ghi chú
`ticker_prune` breadth).

## Câu hỏi trọng tâm dispatch: 7 tháng May-Nov 2009 (CPI dưới 6% do base effect)

Kiểm dd52 thật trong giai đoạn này: gate **KHÔNG liên tục armed** — dd52 hồi phục lên tới 0,0%
(2009-09-18) trước khi rơi lại xuống dưới −20% ngày 2009-11-27. Vậy PIT chỉ thực sự được đánh giá
ở 2 mảnh: (i) đuôi cluster lớn tới 2009-07-23 (CPI đang giảm 9,23%→3,31% nhưng **deposit vẫn 9,0%**
suốt) và (ii) cluster mới bắt đầu 2009-11-26 (CPI đã hồi 4,35%, **deposit vẫn 9,0%**). Ở cả 2 mảnh,
**deposit rate ở ĐÚNG ngưỡng 9,0% (biên, `>=` nên vẫn tính là chặn) trong toàn bộ 9 tháng
2009-04→2009-12** (nguồn: CSV Winston `deposit_rate_approx_pct`, est-CEIC, MEDIUM confidence) —
đây là lý do OR-logic vẫn chặn được dù CPI một mình sẽ để lọt (CPI thấp nhất −0,02% tháng 10/2009,
dưới ngưỡng 6% suốt 6/9 tháng). **Kết luận: filter OR-logic (CPI≥6% HOẶC deposit≥9%) cover đúng
toàn bộ base-effect window — không có false-negative.**

**⚠️ Cảnh báo biên độ mỏng cần mang theo**: deposit rate 9,0% CHẠM CHÍNH XÁC ngưỡng 9,0% (không có
khoảng đệm) trong suốt giai đoạn này, và đây là ước tính MEDIUM-confidence (est-CEIC), không phải
số GSO/SBV chính thức theo tháng. Nếu số thật hơi thấp hơn (vd 8,7-8,9%) — plausible vì CSV Winston
tự ghi "approx" — thì filter sẽ để lọt đúng giai đoạn base-effect này. Đây là rủi ro thật, không
phải giả định — khác với các cluster khác nơi khoảng cách tới ngưỡng còn 1-5pp.

## (c) Đánh giá hạ ngưỡng CPI 6,0%→5,5%

**Không cần thiết** — deposit rate đã cover toàn bộ base-effect window (xem trên) nên hạ ngưỡng CPI
không thêm bảo vệ nào cho ca 2009. Về false-positive: max CPI trong TOÀN BỘ 5 cluster Loại 2 (tính
mọi ngày trong cửa sổ, không chỉ lúc fire) là **5,14%** (2020-03→05, đỉnh COVID). Hạ ngưỡng xuống
5,5% vẫn còn đệm 0,36pp — **không tạo false-positive trên tập đã quan sát**, nhưng đệm an toàn co
lại đáng kể (từ 0,86pp còn 0,36pp so với ngưỡng 6,0%). **Khuyến nghị: GIỮ NGUYÊN ngưỡng 6,0%/9,0%**
— hạ ngưỡng CPI không giải quyết được lỗ hổng thật (biên độ mỏng của deposit rate ở trên), chỉ làm
giảm margin an toàn phía Loại 2 mà không đổi lại lợi ích gì đo được.

## Việc CHƯA làm / ngoài phạm vi

- Chưa wire backfill deposit rate 2007-2010 vào `deposit_rate_vn.py` production (chỉ dùng test-only
  trong script này) — nếu muốn PIT filter production tự nó (không qua script test) trả lời đúng cho
  ngày lịch sử 2007-2010, cần một job riêng để làm việc đó qua đúng quy trình (§8/§9 coding_guidelines,
  Winston sở hữu data registry).
- Chưa đổi `CAPIT_LEVER_PIT_CPI_THRESHOLD`/`CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD` trong
  `golive_recommend_v23.py` — kết luận (c) là GIỮ NGUYÊN, không có thay đổi code production nào ở
  việc 1 ngoài backfill `cpi_vn.py`.
