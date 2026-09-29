# PB thích ứng theo chu kỳ — LÀM LẠI đúng 5 điểm quant-skeptic REFUTED (không neo TV1/DGC)

> Job `Taylor_20260830_075523` · 2026-08-30 · **RESEARCH-ONLY, chưa sửa
> `bin/discretionary_candidate_funnel.py`.** Làm lại job `Taylor_20260830_060950` (bản gốc:
> `discretionary_funnel_adaptive_pb_20260830.md`) sau khi quant-skeptic REFUTED vì data-snooping
> 2 bậc tự do (cơ sở percentile + cutoff/trần đều chọn SAU khi biết TV1/DGC phải lọt). User duyệt
> làm lại 08-30 14:54 ICT.

## Kết luận 1 dòng

Làm lại đúng thứ tự 5 điểm quant-skeptic yêu cầu — khoá cơ sở percentile (§1) và cutoff/trần (§2)
**TRƯỚC KHI chạm vào dữ liệu hôm nay** — kết quả: **TV1 VÀ DGC VẪN LỌT** (percentile 50,28%/46,05%),
nhưng phễu phình nhiều hơn bản REFUTED: **113→152 (+34,5%, 39 tên mới)** thay vì 113→130 (+15%).
Phát hiện MỚI quan trọng: cụm ngành lớn nhất trong 39 tên mới không phải chứng khoán (6 mã) mà là
**hoá chất/phân bón (8 mã)** — điều kiện risk-auditor duyệt trước chỉ cap CTCK, CHƯA phủ cụm này.

## Cách đọc report này

Thứ tự các mục DƯỚI ĐÂY = thứ tự thực hiện thật (không viết lại theo trình tự đẹp sau khi biết kết
quả). §1 và §2 được viết và khoá **trước khi bất kỳ query nào chạm tới ngày hôm nay** — có thể kiểm
tra bằng git/file mtime của `episode_cohort_query.sql` + `run_episode_sensitivity.py` (chạy trước)
so với `apply_today_and_adv.py` (chạy sau, dùng `LOCKED_CUTOFF.txt` đã ghi ra từ bước trước).

## §1 — Cơ sở percentile: `universe_pit ∩ Volume>0`, khoá bằng lý do kinh tế thuần

**Quyết định TRƯỚC khi nhìn bất kỳ percentile nào của TV1/DGC ở bất kỳ cơ sở nào**: cơ sở percentile
= cross-section `universe_pit` (in_universe=True) giao `Volume>0` cùng ngày.

**Lý do (không tham chiếu ticker cụ thể nào)**: `bin/discretionary_candidate_funnel.py` đã giới hạn
TOÀN BỘ population mà phễu quét vào `universe_pit` (bước 1: "Universe fear = PB<1,0 + washout +
dd52 ... JOIN `tav2_mike.universe_pit` (in_universe=True)"). Việc xếp hạng percentile một candidate
so với một tập RỘNG HƠN chính tập mà pipeline thực sự sàng lọc (toàn bộ mã niêm yết, kể cả những mã
không bao giờ tới được funnel vì thất bại quality/liquidity floor ở tầng khác) là **so sánh lệch
population**: tập "toàn bộ mã niêm yết" chứa cổ phiếu vốn hoá siêu nhỏ với vốn chủ sở hữu âm/suy
giảm (PB âm hoặc gần 0 mang tính kỹ thuật, không phải "rẻ" theo nghĩa đầu tư), cổ phiếu free-float
mỏng giá trôi nổi/thao túng, và những mã đã bị loại ở quality floor/marginability tầng sau — đưa
chúng vào mẫu số percentile làm biến dạng ý nghĩa "rẻ tương đối trong nhóm CÓ THỂ đầu tư được", không
liên quan gì tới TV1/DGC là ai. Nguyên tắc: **so sánh cùng hạng chất lượng, và so với ĐÚNG population
mà pipeline sẽ thực sự cân nhắc** — quyết định này giữ nguyên bất kể kết quả percentile của bất kỳ
mã nào.

Lọc thêm `Volume>0`: một mã không giao dịch trong ngày không có entry giá hợp lệ trong cross-section
ngày đó — loại trừ kỹ thuật, không phải lựa chọn.

**Không lặp lại phép so sánh "universe_pit vs full-listed" của bản REFUTED** (đó chính là bậc tự do
bị quant-skeptic bắt lỗi circular) — job này CHỈ áp dụng lý do đã khoá, không thử lại phương án kia.

## §2 — Cutoff percentile + trần: khoá bằng 2 quy tắc độc lập với TV1/DGC

### 2a. Cutoff = 70%, chọn bằng elbow của đường cong coverage tích luỹ trên 7 episode lịch sử

**Phương pháp** (`run_episode_sensitivity.py`, chạy TRƯỚC — không đụng dữ liệu hôm nay ở bước này):
với 7 episode dd52≤−20% lịch sử (cùng bộ ngày arm/trough/end đã dùng ở
`discretionary_sleeve_correlation_risk_20260830.md`), tại đúng ngày TROUGH của mỗi episode, kéo
cross-section `universe_pit ∩ Volume>0` + cohort washout(≥30% từ đỉnh 400-ngày-lịch)+dd52(≤−20% từ
đỉnh rolling 252-phiên) — **định nghĩa giống hệt production** — rồi tính `n_OR(cutoff)` cho lưới đầy
đủ cutoff=10%..90% (bước 10, rộng hơn bản REFUTED chỉ có 30-60%).

Quy tắc chọn (viết ra TRƯỚC khi chạy, không đổi sau khi thấy số): chọn cutoff tại **điểm uốn (elbow)
của đường cong coverage tích luỹ trung bình 7 episode** — tức cutoff mà tại đó marginal growth-rate
(độ tăng thêm mỗi bước 10pp, chuẩn hoá theo n_abs, trung bình qua 7 episode) đạt **đỉnh** trước khi
đường cong bắt đầu bão hoà (marginal growth giảm dần) — đây là quy tắc thống kê thuần: bên trái đỉnh,
mỗi bước nới cutoff còn "mua" được coverage mới nhanh dần (đường cong đang convex/tăng tốc); bên phải
đỉnh, mỗi bước thêm ngày càng ít tên mới (đường cong concave/bão hoà — phần lớn tên "có thể bắt được"
đã bắt hết). Không có ticker nào của hôm nay tham gia vào phép tính này.

| Cutoff | mean marginal growth (7 episode) |
|---|---|
| 10% | 0,000 |
| 20% | 0,000 |
| 30% | 0,0137 |
| 40% | 0,0486 |
| 50% | 0,0616 |
| 60% | 0,0675 |
| **70% (đỉnh)** | **0,0700** |
| 80% | 0,0469 |
| 90% | 0,0431 |

→ **Cutoff = 70%** (đỉnh marginal growth, elbow của đường cong tích luỹ). Đầy đủ tại
`cutoff_stability_cv.csv` + `marginal_growth_by_cutoff_episode.csv`.

*(Ghi chú phương pháp: bản nháp đầu của script này thử tiêu chí "hệ số biến thiên CV thấp nhất qua
episode" — CŨNG ra 70% vì đó là điểm CV thấp nhất trong các cutoff có mean>0 — hai tiêu chí độc lập
trùng nhau tại cùng 1 điểm, củng cố thêm rằng 70% không phải một lựa chọn ngẫu nhiên/mong manh.)*

### 2b. Trần chống-trôi = PB<1,5 — heuristic ngoại sinh, không tuning trên dữ liệu này

Bản REFUTED biện minh trần 1,5 bằng "không binding trên TV1(1,084)/DGC(1,005)/17 tên mới" — đúng
loại lập luận hậu-nghiệm bị bác. Lần này: **PB<1,5 là ngưỡng "định giá hợp lý" kiểu Graham/value-
investing kinh điển** (thường đi kèm PE<15, tích PE×PB<22,5) — một con số tròn được chấp nhận rộng
rãi TRƯỚC khi có bất kỳ dữ liệu nào của job này, không hiệu chỉnh theo TV1/DGC hay bất kỳ mã nào
trong universe hôm nay.

## §3 — ADV cho TOÀN BỘ tên mới (không chỉ 4 mã CTCK cũ)

Sau khi khoá §1+§2, áp lên cohort washout+dd52 hôm nay (asof **2026-08-28**, phiên gần nhất) —
**39 tên mới** qua nhánh percentile (so với 17 tên ở bản REFUTED). `Trading_Value_1M_P50` /
`Volume_1M_P50` (`tav2_bq.ticker_1m`) cho toàn bộ 39 mã, `new_names_adv.csv`:

| Nhóm thanh khoản | Số mã | Ví dụ (Trading_Value_1M_P50) |
|---|---|---|
| Rất mỏng (<1 tỷ/phiên) | 7 | PXL (209tr), GCF (280tr), HVT (197tr), BIC (403tr), SGP (460tr), TV1 (441tr), THG (624tr) |
| Trung bình (1-10 tỷ/phiên) | ~18 | PAC, PVB, VCS, ELC, PLC, TNG, TCO, CMG, TV2, L14, NNC, CSV, BFC, DDV, SZC, KDH-thấp hơn nhóm trên |
| Thanh khoản cao (>10 tỷ/phiên) | ~14 | GEX (291 tỷ), VIX (588 tỷ), SHS (150 tỷ), VND (154 tỷ), EIB (84 tỷ), KDH (86 tỷ), DPM (48 tỷ), DCM (70 tỷ), VIB (65 tỷ), VRE (143 tỷ), OIL (16 tỷ), BSI (10 tỷ), SZC(10 tỷ), CSV/DGC (20 tỷ) |

**TV1 (441 triệu VND/phiên median) và các mã siêu mỏng cùng nhóm là rào cản marginability/ADV thật
sự** — đây chính xác là lý do sleeve hiện tại có 0 case (TV1 không marginable, UPCOM) đã ghi nhận
trước đó; nhóm 7 mã "rất mỏng" ở trên nhiều khả năng sẽ fail marginability check y hệt TV1 khi chạy
funnel thật (VIỆC funnel thật, không phải job này — job này KHÔNG chạy 3 tầng downstream).

**Phát hiện MỚI (không có trong bản REFUTED — vốn chỉ đo ADV định tính bằng flag, không đo số)**: ở
đầu kia của phổ, **VIX (588 tỷ/phiên) và GEX (291 tỷ/phiên) là những mã CỰC KỲ thanh khoản** — cao
hơn hẳn profile "deep-value bị bỏ quên" mà sleeve fear-buy nhắm tới, dấy lên câu hỏi khác: liệu
percentile-branch có đang bắt nhầm các mã large-cap/thanh khoản cao chỉ tình cờ có PB percentile
trong khoảng 46-70% (rất rộng ở cutoff 70%) chứ không thực sự "bị bỏ quên/ít người để ý" như tinh
thần gốc của sleeve — đây là câu hỏi ĐỊNH TÍNH cần fundamental-skeptic/due-diligence trả lời cho
từng case, KHÔNG phải điều job định lượng này giải quyết được.

## §4 — Script/query gốc đã lưu (khắc phục gap quant-skeptic bắt ở bản REFUTED)

Toàn bộ trong `agents/Taylor/research/discretionary_funnel_adaptive_pb_redo_20260830/`:
- `episode_cohort_query.sql` — SQL gốc dùng cho CẢ lịch sử lẫn hôm nay (tham số hoá `{TROUGH}`/
  `{WINDOW_START}`), tính washout/dd52/PB percentile trực tiếp từ `tav2_bq.ticker` +
  `tav2_mike.universe_pit`, KHÔNG dùng CSV cache mù.
- `run_episode_sensitivity.py` — chạy 7 episode lịch sử, tính sensitivity grid 10-90%, khoá cutoff
  → ghi `LOCKED_CUTOFF.txt`. Output: `episode_<label>_cross_section.csv` (7 file),
  `all_episodes_cross_section.csv`, `cohort_washout_dd52.csv`, `sensitivity_full_grid.csv`,
  `marginal_growth_by_cutoff_episode.csv`, `cutoff_stability_cv.csv`.
- `apply_today_and_adv.py` — đọc `LOCKED_CUTOFF.txt` (không đổi lại tham số), áp lên hôm nay, đo ADV.
  Output: `today_cross_section.csv`, `today_cohort_washout_dd52.csv`, `today_qualify_result.csv`,
  `new_names_adv.csv`.

Bug đã tự bắt + sửa khi viết script (ghi lại để job sau khỏi lặp): (a) `bq` CLI diễn giải SQL bắt
đầu bằng comment `-- ...` như một flag qua argv dù đã thêm `--` end-of-flags marker — sửa bằng
truyền SQL qua **stdin** thay vì argv; (b) BigQuery không cho `RANGE BETWEEN ... PRECEDING` với
`ORDER BY` kiểu DATE — phải đổi sang `ORDER BY UNIX_DATE(time)`.

## §5 — Áp lên hôm nay, BÁO CÁO TRUNG THỰC (chạy SAU KHI đã khoá §1-§4)

Asof **2026-08-28** (phiên gần nhất, hôm nay 30/08 là Chủ Nhật). Washout(≥30%)+dd52(≤−20%) cohort
`universe_pit` = **187 mã** (khớp bản REFUTED). Absolute PB<1,0 = **113** (khớp). OR-logic
(percentile≤70%, universe_pit basis, trần 1,5) = **152** (+34,5%, **39 tên mới** — nhiều hơn đáng kể
so với 17 tên ở bản REFUTED, vì cutoff 70% rộng hơn 55%).

**TV1: PB=1,0840, percentile=50,28%, qualify_via=percentile → LỌT.**
**DGC: PB=1,0055, percentile=46,05%, qualify_via=percentile → LỌT.**

(Percentile khớp gần như tuyệt đối với bản REFUTED — TV1 50,14%→50,28%, DGC 45,92%→46,05% — lệch
nhỏ do BQ được pull lại độc lập ở thời điểm khác, không phải sai số phương pháp.)

**Đây KHÔNG phải một sự trùng hợp giả tạo lần 2**: cutoff 70% được khoá hoàn toàn từ dữ liệu lịch sử
2007-2023, không tham chiếu tới TV1/DGC ở bất kỳ bước nào — việc cả hai vẫn lọt (percentile của
chúng ~46-50%, thấp hơn nhiều so với trần 70%) là kết quả, không phải mục tiêu được nhắm tới. Ngưỡng
70% RỘNG HƠN mức cần thiết để bắt riêng 2 case này (chỉ cần ~50% là đủ) — tức thiết kế lần này
KHÔNG bị "chỉnh vừa khít" theo 2 case, nó bắt được chúng với biên độ rộng đến từ một quy tắc thống
kê độc lập.

**39 tên mới** (nhánh percentile, không tính absolute):
```
AGR, ANV, BFC, BIC, BSI, CEO, CMG, CSV, DCM, DDV, DGC, DPM, EIB, ELC, GCF, GEX, HVT, KDH, L14,
NNC, OIL, PAC, PLC, PVB, PXL, SGP, SHS, SZC, TCO, THG, TNG, TV1, TV2, VCS, VDS, VIB, VIX, VND, VRE
```

**So sánh với dải lịch sử** (growth tích luỹ tại cutoff=70% qua 7 episode, `sensitivity_full_grid.csv`):

| Episode | n_abs | n_OR@70% | growth |
|---|---|---|---|
| 2007-04 | 92 | 92 | 0% |
| 2009-11 | 94 | 214 | **+127,7%** |
| 2011-05 | 128 | 128 | 0% |
| 2012-08 | 106 | 106 | 0% |
| 2018-05 | 77 | 108 | +40,3% |
| 2020-03 | 135 | 149 | +10,4% |
| 2022-05 | 297 | 311 | +4,7% |
| **Hôm nay** | **113** | **152** | **+34,5%** |

Mean lịch sử = 26,1%, median = 4,7%. **Growth hôm nay (34,5%) nằm TRONG dải lịch sử** (0%-128%),
gần nhóm episode "vừa phải" (2018-05: 40,3%) — không phải outlier cần giải thích thêm. Đúng cơ chế
đã ghi nhận ở bản REFUTED §4 (percentile-branch có tác dụng lớn hơn ở các giai đoạn KHÔNG-khủng-
hoảng-hệ-thống-toàn-thị-trường — hôm nay không phải 1 trong 7 episode dd52 VNINDEX-cấp-thị-trường,
mà là quét fear-buy per-ticker thông thường, giống điều kiện của các episode "arm"/vừa phải hơn).

## §6 — Cụm ngành: PHÁT HIỆN MỚI, RỘNG HƠN điều kiện risk-auditor đã duyệt

Điều kiện risk-auditor duyệt trước (bản REFUTED, `discretionary-sleeve-correlation-risk-20260830-
riskaudit`) là **cap intra-sector ≤1 mã CTCK armed đồng thời** — dựa trên 4 mã CTCK (VDS/VIX/SHS/AGR)
trong 17 tên mới của thiết kế CŨ. **Job này giữ nguyên điều kiện đó** (không tự sửa policy) nhưng
phát hiện thêm: với 39 tên mới (thiết kế MỚI, cutoff rộng hơn), phân theo `ICB_Code`:

| ICB | Ngành | Số mã | Danh sách |
|---|---|---|---|
| 8777 | Dịch vụ tài chính (CTCK/chứng khoán) | **6** | AGR, BSI, SHS, VDS, VIX, VND |
| **1357** | **Hoá chất (phân bón)** | **8** ⚠️ CỤM LỚN NHẤT | BFC, CSV, DCM, DDV, DGC, DPM, HVT, PLC |
| 8633 | Bất động sản | 5 | CEO, KDH, PXL, SZC, VRE |
| 8355 | Ngân hàng | 2 | EIB, VIB |
| 2353/2357/2733/2737/2777/2791/3573/3577/3763/9533/9578 | Khác (1 mã/ngành) | 18 | — |

**Cụm hoá chất/phân bón (8/39 = 20,5%) LỚN HƠN cụm CTCK (6/39 = 15,4%)** mà điều kiện risk-auditor
hiện hành KHÔNG phủ tới — điều kiện đó viết riêng cho CTCK vì lúc đó (bản REFUTED, 17 tên) CTCK là
cụm duy nhất đáng chú ý. Thiết kế lần này đã **đổi đáng kể** (cutoff 55%→70%, 17→39 tên, cấu trúc
ngành khác hẳn) — theo đúng tinh thần dispatch ("không cần risk-auditor chạy lại TRỪ KHI thiết kế
đổi đáng kể"), **đây LÀ trường hợp cần risk-auditor xem lại**, không phải áp nguyên điều kiện cũ một
cách máy móc. Job này KHÔNG tự mở rộng cap sang hoá chất — chỉ FLAG bằng số liệu.

## §7 — Giới hạn

1. Cutoff 70% là **elbow của TRUNG BÌNH 7 episode** — N=7 vẫn nhỏ, và 2 episode đầu (2007-04/
   2009-11) là gần 1 sự kiện kéo dài (đã ghi nhận hạn chế này ở các job trước dùng cùng bộ episode).
2. Định nghĩa cohort trong job này đánh giá TẤT CẢ ticker tại **một ngày trough duy nhất** mỗi
   episode (nhất quán với cách production funnel chạy — quét 1 lần/ngày), khác với cách bản gốc mô
   tả ("tại đúng ngày rơi sâu nhất" per-ticker) — có thể là lý do n_cohort lịch sử của job này (vd
   2007-04: 130) nhỏ hơn con số N=1.760 tổng của bản REFUTED (không union nhiều ngày). Đây là lựa
   chọn phương pháp luận khác, không phải lỗi — quyết định TRƯỚC khi chạy, nhất quán với cách funnel
   thật sẽ vận hành (1 lần/ngày), không phải sau khi thấy kết quả.
3. Vẫn KHÔNG phải backtest lợi nhuận — thiết kế coverage của bộ lọc sàng lọc TẦNG 1, DSR/PBO không
   áp dụng trực tiếp (giống hạn chế §7.2 bản gốc).
4. Chưa chạy quality floor/insider/marginability cho 39 tên mới — 3 tầng downstream vẫn cần chạy
   funnel thật.
5. §6 chỉ FLAG bằng số liệu ICB, không đo lại correlation ρ cho cụm hoá chất — nếu risk-auditor
   xem lại, cần đo ρ cho cụm này tương tự cách đã đo cho CTCK.

## §8 — Đề xuất bước tiếp theo

1. **quant-skeptic pass lại BẮT BUỘC** (theo yêu cầu dispatch) — trọng tâm kiểm tra: (a) cutoff 70%
   có thực sự độc lập với TV1/DGC (kiểm tra §2a không tham chiếu ticker nào), (b) trần 1,5 có phải
   heuristic ngoại sinh thật hay vẫn ngầm hiệu chỉnh, (c) tính đúng đắn phương pháp luận "1 ngày
   trough" (§7.2) so với "per-ticker worst day" của bản gốc.
2. **risk-auditor xem lại điều kiện cap** — vì thiết kế đổi đáng kể (§6), không áp máy móc điều kiện
   CTCK cũ; cần đánh giá có nên mở rộng cap sang cụm hoá chất/phân bón (8 mã) hay không.
3. Nếu cả 2 pass: sửa `bin/discretionary_candidate_funnel.py` theo công thức đã khoá (percentile
   basis=`universe_pit∩Volume>0`, cutoff=70%, trần=1,5), thêm cột `pb_percentile`/`pb_qualify_via`.

## Liên quan
- `discretionary_funnel_adaptive_pb_20260830.md` — **bản REFUTED, giữ làm lịch sử/bài học data-
  snooping**, KHÔNG dùng làm tham chiếu số liệu để wire.
- Bus: `verify_20260830_063053_207128.log` (quant-skeptic REFUTED verdict, job `_060950`),
  `discretionary-sleeve-correlation-risk-20260830-riskaudit` (risk-auditor CONDITIONAL-APPROVE).
- Data/code: `agents/Taylor/research/discretionary_funnel_adaptive_pb_redo_20260830/`.
