# PB thích ứng theo chu kỳ — ROUND 3, khoá NỐT trần (PB_MAX_CEIL) bằng min-CV mechanical rule

> Job `Taylor_20260830_085015` · 2026-08-30 · **RESEARCH-ONLY, chưa sửa
> `bin/discretionary_candidate_funnel.py`.** Vòng cuối đóng lỗ hổng thứ 2 mà quant-skeptic verify
> lần 2 (job `Taylor_20260830_075523`, log `verify_20260830_080843_251411.log`) REFUTED: cutoff
> (70%) đã PASS — thật sự độc lập, min-CV mechanical, ticker-agnostic — nhưng trần `PB_MAX_CEIL=1.5`
> chỉ là khẳng định ("Graham heuristic") chưa qua sensitivity nào, và quant-skeptic tự quét
> 1.3–1.7 thấy `n_new` dao động 29→40 (38%). User duyệt làm nốt vòng này 2026-08-30 15:49 ICT.

## Kết luận 1 dòng

Khoá trần bằng **đúng cơ chế min-CV** đã dùng cho cutoff (không phải "elbow" — quant-skeptic đã chỉ
ra §2a round 2 mô tả sai code thật, xem §0 dưới) → **trần khoá ra 1,2, KHÔNG PHẢI 1,5** như 2 bản
trước giả định. Áp cả 2 tham số đã khoá (cutoff=70%, trần=1,2) lên hôm nay: **TV1 và DGC VẪN LỌT**
(PB 1,084/1,006, cả hai đều <1,2 dễ dàng), nhưng phễu hẹp lại đáng kể so với round 2: **113→136
(+20,4%, 23 tên mới)** thay vì 113→152 (+34,5%, 39 tên mới). Cụm ngành đổi: **CTCK (5 mã) lại là
cụm lớn nhất**, không phải hoá chất (4 mã) — điều kiện risk-auditor duyệt trước (cap CTCK) hoá ra
LẠI ĐÚNG, không cần mở rộng sang hoá chất như round 2 flag.

## §0 — Sửa mô tả sai đã bị quant-skeptic bắt (yêu cầu bắt buộc trong dispatch)

Round 2 báo cáo mô tả quy tắc chọn cutoff là "elbow của đường cong marginal-growth" — nhưng code
thật (`run_episode_sensitivity.py::best_cutoff = stability["cv"].idxmin()`) chỉ tính **min-CV**
(hệ số biến thiên thấp nhất). Elbow và min-CV **trùng nhau ở 70% một cách tình cờ trên bộ 7 episode
này** (mean cũng đạt đỉnh ở 70%, và vì CV=std/mean, đỉnh mean kéo CV xuống một cách cơ học — hai
con số không độc lập như round 2 khẳng định). Round 3 gọi đúng tên quy tắc: **min-CV stability qua
episode**, không dùng chữ "elbow" nữa. Cutoff **giữ nguyên 70%** — không mở lại tham số này.

## §1 — Khoá trần bằng min-CV, ĐỘC LẬP với dữ liệu hôm nay

**Cơ chế** (`run_ceiling_sensitivity.py`, thư mục
`discretionary_funnel_adaptive_pb_round3_20260830/`): tái dùng `cohort_washout_dd52.csv` +
`LOCKED_CUTOFF.txt` (=70%) đã có sẵn từ round 2 — **không re-query BQ, không đụng dữ liệu hôm nay
ở bước này**. Cutoff cố định 70% (đã khoá, không mở lại). Quét lưới `PB_MAX_CEIL` = 1,2 → 1,8
(bước 0,1, đúng theo yêu cầu dispatch), tính `n_OR(ceiling)` cho từng episode, marginal growth-rate
`g(e) = (n_OR(e) − n_OR(e_prev))/n_abs` (baseline e_prev=1,0 cho điểm lưới đầu tiên — vì trần=1,0
làm nhánh percentile trùng nhánh absolute, y hệt cách baseline `n_abs_pb_lt1` dùng cho cutoff), rồi
`CV(e) = std(g)/mean(g)` qua 7 episode — **đúng công thức, đúng code path đã dùng cho cutoff**, chỉ
đổi biến quét.

| Ceiling | mean marginal growth (7 episode) | std | CV |
|---|---|---|---|
| 1,2 | 0,1345 | 0,2157 | **1,6041 (thấp nhất)** |
| 1,3 | 0,0510 | 0,1007 | 1,9746 |
| 1,4 | 0,0351 | 0,0687 | 1,9557 |
| 1,5 | 0,0409 | 0,0874 | 2,1382 |
| 1,6 | 0,0213 | 0,0563 | 2,6458 |
| 1,7 | 0,0000 | 0,0000 | NaN (mean=0) |
| 1,8 | 0,0000 | 0,0000 | NaN (mean=0) |

→ **Trần = 1,2** (CV thấp nhất trong các mức có mean>0 — quy tắc `idxmin()` tự bỏ qua NaN, giống
hệt cách cutoff bỏ qua CV=NaN ở cutoff=10%/20%). Đầy đủ tại `ceiling_stability_cv.csv` +
`marginal_growth_by_ceiling_episode.csv` + `ceiling_sensitivity_full_grid.csv`.

**Kết quả này KHÁC 1,5** (giá trị cả round 1 lẫn round 2 đều dùng như một khẳng định chưa kiểm
định) — bằng chứng thêm rằng lần này quy tắc thực sự chạy trước khi biết kết quả, không phải chọn
sẵn 1,5 rồi tìm cớ biện minh sau.

## §2 — Áp cả 2 tham số đã khoá lên hôm nay (asof 2026-08-28)

`apply_today_locked_v2.py` — tái dùng `today_cross_section.csv` của round 2 (basis
`universe_pit∩Volume>0`, washout/dd52/PB/pb_pct_rank — không phụ thuộc ceiling nên không cần
re-query BQ), chỉ áp lại công thức qualify với cutoff=70%/trần=1,2.

Washout(≥30%)+dd52(≤−20%) cohort = **187** (khớp round 1/2). Absolute PB<1,0 = **113** (khớp).
OR-logic (cutoff=70%, trần=1,2) = **136** (**+20,4%, 23 tên mới**) — hẹp hơn round 2 (152, 39 tên,
+34,5%) vì trần 1,2 chặt hơn 1,5 đáng kể.

**TV1: PB=1,0840, percentile=50,28%, qualify_via=percentile → LỌT** (1,084 < trần 1,2 dễ dàng).
**DGC: PB=1,0055, percentile=46,05%, qualify_via=percentile → LỌT** (1,006 < trần 1,2 dễ dàng).

Cả hai case không hề "cận biên" so với trần mới — TV1 cách trần 1,2 một khoảng 0,116 (~10,7%),
DGC cách 0,195 (~16,2%) — cho thấy 2 case này lọt được là nhờ percentile thấp (46-50%, xa dưới
cutoff 70%), không phải nhờ trần được nới ra vừa đủ để "vớt" chúng.

**23 tên mới** (nhánh percentile):
```
AGR, ANV, CEO, DDV, DGC, ELC, GEX, HVT, KDH, OIL, PAC, PLC, PVB, PXL, SHS, SZC, TNG, TV1, VCS,
VDS, VIB, VIX, VND
```

So sánh với dải lịch sử tại cutoff=70%/trần=1,2 qua 7 episode:

| Episode | n_abs | n_OR | growth |
|---|---|---|---|
| 2007-04 | 92 | 92 | 0% |
| 2009-11 | 94 | 150 | **+59,6%** |
| 2011-05 | 128 | 128 | 0% |
| 2012-08 | 106 | 106 | 0% |
| 2018-05 | 77 | 92 | +19,5% |
| 2020-03 | 135 | 149 | +10,4% |
| 2022-05 | 297 | 311 | +4,7% |
| **Hôm nay** | **113** | **136** | **+20,4%** |

Mean lịch sử = 13,5%, median = 4,7%. Growth hôm nay (20,4%) nằm trong dải lịch sử (0%–59,6%), gần
nhóm 2018-05 (19,5%) — không phải outlier.

## §3 — Cụm ngành: CTCK lại là cụm lớn nhất, KHÔNG PHẢI hoá chất

Với trần chặt hơn (1,2 thay vì 1,5), phân bố ngành của 23 tên mới đổi khác round 2:

| Ngành (ICB) | Số mã | Danh sách |
|---|---|---|
| **CTCK (8777)** | **5** ⚠️ lớn nhất | AGR, SHS, VDS, VIX, VND |
| Hoá chất/phân bón (1357) | 4 | DDV, DGC, HVT, PLC |
| Bất động sản (8633) | 4 | CEO, KDH, PXL, SZC |
| Khác (1 mã/ngành) | 10 | ANV, ELC, GEX, OIL, PAC, PVB, TNG, TV1, VCS, VIB |

**CTCK (5/23 = 21,7%) một lần nữa là cụm lớn nhất** — điều kiện risk-auditor đã duyệt trước (cap
CTCK armed đồng thời ≤1) **áp dụng trực tiếp, không cần mở rộng**. Cụm hoá chất/phân bón round 2
flag (8/39) co lại còn 4/23 với trần chặt hơn — vẫn đáng chú ý nhưng không còn là cụm lớn nhất, và
DGC (mã hoá chất duy nhất trong 2 case gốc) nằm trong cụm này.

## §4 — Giới hạn

1. Cùng hạn chế N=7 episode như round 2 (§7.1/§7.2 bản redo) — không lặp lại ở đây, xem file đó.
2. Trần 1,2 vẫn dựa trên đúng 7 episode lịch sử — nhạy với việc thêm/bớt episode giống cutoff.
   Grid 1,2–1,8 (bước 0,1) đủ để bao trùm cả giá trị round 2 (1,5) và vùng quant-skeptic tự quét
   (1,3–1,7); không quét dưới 1,2 vì dưới đó ngày càng gần trùng nhánh absolute (PB<1,0), không còn
   ý nghĩa "trần chống-trôi" của nhánh percentile.
3. Baseline `e_prev=1,0` cho điểm lưới đầu tiên (1,2) là lựa chọn phương pháp luận (giống cách
   cutoff dùng baseline `n_abs_pb_lt1`) — nếu ai muốn quét cả 1,0–1,1 cần định nghĩa baseline khác.
4. Vẫn KHÔNG phải backtest lợi nhuận (giống hạn chế §7.3 bản redo) — DSR/PBO không áp dụng.
5. Chưa chạy quality floor/insider/marginability cho 23 tên mới — 3 tầng downstream vẫn cần chạy
   funnel thật trước khi coi là candidate cuối cùng.

## §5 — Đề xuất bước tiếp theo

1. **quant-skeptic pass lần 3 BẮT BUỘC** (theo dispatch) — trọng tâm: (a) cơ chế min-CV cho trần có
   thực sự đúng như đã áp cho cutoff, (b) baseline e_prev=1,0 có hợp lý, (c) mô tả §0 đã sửa đúng
   chưa lặp lại lỗi "elbow" narrative-integrity gap.
2. Nếu pass: sửa `bin/discretionary_candidate_funnel.py` theo công thức đã khoá — percentile
   basis=`universe_pit∩Volume>0`, cutoff=70%, **trần=1,2** (không phải 1,5), thêm cột
   `pb_percentile`/`pb_qualify_via`. Điều kiện risk-auditor cap CTCK ≤1 áp dụng trực tiếp (§3),
   không cần risk-auditor xem lại thêm (khác round 2 — lúc đó cụm hoá chất lớn hơn CTCK).

## Liên quan
- `discretionary_funnel_adaptive_pb_20260830.md` — bản gốc REFUTED (data-snooping 2 bậc tự do).
- `discretionary_funnel_adaptive_pb_redo_20260830.md` — round 2, khoá cutoff đúng nhưng trần vẫn
  là assertion, REFUTED lần 2 vì lý do đó (log `verify_20260830_080843_251411.log`).
- Data/code round 3: `agents/Taylor/research/discretionary_funnel_adaptive_pb_round3_20260830/`.
