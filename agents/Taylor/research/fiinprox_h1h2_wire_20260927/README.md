# JOB D — WIRE VỆ SINH H1 + H2 (job `Taylor_20260927_022319`)

> Branch `wire/fiinprox-h1-h2-ve-sinh`, worktree `/home/trido/thanhdt/wt-fiinprox-h1h2-wire`.
> **CHƯA MERGE — chờ user sign-off** (`rating_8l_history.py` và `cpi_vn.py` đều là input production).
> Nguồn: `kb/projects/fiinprox-data-usage-proposal-20260926.md` §6 · finding bus
> `fiinprox-H1-bank-route-8l` (quant-skeptic CONFIRMED high 2026-09-26T17:35:21Z) và
> `fiinprox-H2-cpi-swap`.

## Kết luận 1 đoạn

Cả 2 wire đều là **SỬA DỮ LIỆU, không phải đổi chiến lược**, và điều đó được **chứng minh chứ không
phải đoán**. H1: 360/981 dòng mã-quý BANK đổi rating nhưng **0 dòng lịch sử đổi cổng nhị phân
`rating≤3`** ⇒ 0 quyết định V2.4 đổi trên toàn bộ 2014-2026, 0 dòng route khác BANK đổi. H2: chuỗi
CPI đổi 211 tháng nhưng `macro_confidence_regime` đổi nhãn **đúng 27/185 tháng** (trùng khít danh
sách của finding) và **DCF Δ = 0,0 trên 7/7 mã**.

**HAI khoản Δ≠0 phải user quyết** (ban đầu tôi chỉ nêu 1 — quant-skeptic bắt thiếu 1):
bản vá fail-closed (c) làm **BVB** mất `QUALITY_OK` trong `universe_pit_quality` (§4), và làm **ABB**
vượt biên `rating≤2` ⇒ vào watchlist tier W của `anomaly_scan.py` chạy cron (§4b).

## 1. H1(a) — quét 2 nhóm consumer mà finding chưa kiểm

| Call site | Rating dùng kiểu gì | Trước/sau wire |
|---|---|---|
| `regime_size_overlay.py:96` `(s["rating8l"] >= WEAK_RATING_MIN)` , `WEAK_RATING_MIN=4` (dòng 28) | **NHỊ PHÂN** tại biên 3/4 | **Không đổi** — cùng bất biến đại số đã chứng minh |
| `regime_size_overlay.py:9` "tier D/E (relative)" | — | **Không phải code đang chạy**: đó là phương án ĐÃ BỊ LOẠI (`that LOST, OOS -0.45`). Không có tier D/E nào được tính từ rating trong file. |
| 15 × `*_screen.py`: `top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)` | **LIÊN TỤC** (sort theo rating) | **145/146 tháng top-25 y nguyên**; 1 tháng đổi 1 tên (2015-09-30: −VIC +BID), Jaccard 0,923. Danh sách này chỉ nuôi số chẩn đoán `overlap_8l_top25` trong verdict JSON — **không chọn mã, không sizing**. |

15 screen có call site đó: aviation, bank_compounder, compounder, construction, energy,
fertchem_rubber, fnb, livestock, logistics_port, re_compounder, retail_compounder, securities,
steel_buildmat, tech, textile. Script đo: `h1a_screen_top25_ab.py` → `screen_top25_ab.log`.

*Phát hiện phụ, KHÔNG sửa (ngoài phạm vi):* `ascending=False` trên `rating` nghĩa là các screen đang
lấy 25 mã **TỆ NHẤT**, không phải tốt nhất. Lỗi có TRƯỚC wire này; báo lại, không đụng (§3).

## 2. H1(b) — `rate_bank_hist()` thay `rate_bank_proxy()`

- Ngưỡng copy **nguyên văn** từ `rating_8l.py::rate_bank()`; ROE giữ chuỗi `ROE_Trailing → ROE5Y →
  ROE3Y` của proxy ⇒ biên 3/4 bất biến **theo cấu trúc**.
- **Hai panel, hai con số — KHÔNG được trộn** (quant-skeptic bắt đúng chỗ này): **selfcheck** so
  `rate_bank_hist` vs `rate_bank_proxy` trên dòng THÔ, trước override/forensic ⇒ **365/980 (37,2%)**,
  phân rã 1→2:82, 1→3:158, 2→1:9, 2→3:116. **A/B đầu-cuối** so 2 CSV cuối cùng ⇒ **360/981**, phân rã
  1→2:80, 1→3:153, 2→1:8, 2→3:112 + 7 dòng mới nhất. Lệch 5 dòng vì `override_current_bank_aq` áp lại
  điểm live lên dòng mới nhất, che 5 thay đổi ở đó. Con số để TRÍCH DẪN về artifact là **360/981**.
- NPL/LLR từ `mike/data/fiinprox_bank_ratios_quarterly_20260914.csv`, as-of theo **trễ công bố ≥45
  ngày sau quý (Q4 ≥90)** — đúng `avail_date()` của `h1_bank_ab.py`, đúng bẫy 6 của registry.
- **Sống sau trial (28/09):** file FiinPro chỉ là vintage LỊCH SỬ, chỉ đọc cho `eff_date ≤` quý cuối
  trong file ⇒ không bao giờ cần refresh. Đường sống cho mã đang giữ là OCR
  `bank_npl_coverage_primary` → `data/bank_lens_v3.csv` → `rating_8l.py::rate_bank()` → dòng MỚI NHẤT
  qua `override_current_bank_aq()`. Đã ghi tường minh trong docstring module.
- Thiếu file / thiếu NPL+coverage cho quý đó ⇒ **rơi về proxy từng dòng**, không fail-open.
- §8: thêm 2 lối thoát để A/B không bao giờ chạm được artifact canonical — `R8L_HIST_OUT` (đổi
  đường ra) và `R8L_HIST_NO_BQ_REFRESH=1` (không `CREATE OR REPLACE tav2_bq.fa_ratings_8l`). Không
  đặt biến nào ⇒ hành vi production y nguyên.

## 3. H1(c) — vá fail-open `override_current_bank_aq`

`rate_bank()` trả **3 bịa ra** khi mã vắng trong `bank_lens_v3.csv` (`note=bank-nodata`) hoặc ROE
null (`bank-noROE`). Hàm override cũ nhập nguyên con 3 đó, đè lên một điểm có gốc từ ROE. Nay **từ
chối** mọi dòng live có 2 note đó — 9/27 dòng BANK thật: ABB, BAB, BVB, KLB, NVB, PGB, SGB, VAB, VBB.
Thiếu cột `note` ⇒ **từ chối toàn bộ** thay vì đoán (§28: vắng mặt không phải bằng chứng).

Điểm sau khi vá đều đúng với ROE thật: BVB 10,22%→4 · BAB 8,92%→4 · PGB 9,81%→4 · NVB 3,15%→5 ·
SGB 0,43%→5 · KLB 24,2%→3.

## 4. ⚠️ Δ ≠ 0 DUY NHẤT — cần user quyết

A/B đầu-cuối (`e2e_ab.py`, 53.687 dòng): **0 vi phạm cổng ở dòng LỊCH SỬ**, và **6 dòng MỚI NHẤT đổi
cổng** — đúng là bản vá (c): BAB/BVB/PGB 3→4, NVB/SGB 3→5, KLB 4→3.

Truy tiếp xem 6 tên đó có với tới được book không:

| Mã | `universe_pit_quality` 2026-09-25 | Kết luận |
|---|---|---|
| NVB | `FLOOR_FAIL` (CF_OA_3Y −1,25e12, ROE_min3Y −0,92) | đã loại sẵn, rating đổi **không thay đổi gì** |
| KLB | `FLOOR_FAIL` (CF_OA_3Y −3,10e12) + đang trong `forensic_flags` exclude ⇒ rating 5 | **không thay đổi gì** |
| BAB, PGB, SGB | không có trong `ticker_prune` 2026 | ngoài universe, **không thay đổi gì** |
| **BVB** | **`QUALITY_OK`, rating_8l 3,0** | **ĐỔI THẬT: 3→4 ⇒ mất `QUALITY_OK`** |

BVB có thanh khoản thật (ADV trung vị 11,6 tỷ, max 34,6 tỷ từ 06/2026) và có mặt trong
`bal_signal_panel.csv` với tín hiệu MUA thật (DEEP_VALUE_RECOVERY 52 phiên, MOMENTUM_A 14,
MOMENTUM_S_N 8) ⇒ **đây là một cái tên với tới được**, không phải rác UPCoM. Hiện KHÔNG nắm giữ,
và BVB chưa bao giờ vào custom30V (0/1.470 dòng).

**Đọc đúng:** loại BVB là hệ quả ĐÚNG — điểm 3 của nó là số bịa, điểm thật theo ROE là 4 (fragile).
Nhưng nó **là** một thay đổi eligibility live, nên không được gói vào câu "ΔNAV = 0". Đây là mục
user cần duyệt, không phải mục tự merge.

## 4b. ⚠️ BIÊN `rating≤2` — lỗ hổng trong kiểm kê consumer của CHÍNH TÔI (quant-skeptic phát hiện)

Bất biến đã chứng minh chỉ nói về **biên 3/4**. Nó KHÔNG nói gì về biên **2/3**, mà dữ liệu AQ làm
biên đó dịch rất nhiều: **266/981 dòng BANK (27,1%)** vượt biên `≤2` (1→3:153, 2→3:112, 3→2:1).
Nhiều nhất: HDB 34, VIB 33, VPB 25, SHB 22, NAB 18, MSB 16, BID 14, OCB 14.

| Consumer gate `≤2` | Nguồn rating | Ảnh hưởng |
|---|---|---|
| `mike/agents/Taylor/anomaly_scan.py:156` `query("rating<=2")` — **cron 08:20 T2-T6** (trong `ops_health_check.sh`) + `fearbuy_weekly_scan.sh` T6 08:10 | `data/bq_cache/fa_ratings_8l.parquet` = **bảng này** | **ĐỔI THẬT, live: đúng 1 tên — ABB dòng mới nhất 3→2 ⇒ ABB vào watchlist tier W.** Là WATCHLIST chất lượng, không phải vị thế, không phải sizing. |
| `custom30v_hybrid.py` (luật swap `rating≤2`) | `tav2_bq.fa_ratings_8l` | **backtest sẽ đổi** trên 266 dòng đó. Biến thể R&D, KHÔNG phải V2.4 production. |
| `cheap_pb_floor.py:83`, `sector_lens_monitor.py:453`, `newdeals_daily_report.py` | `data/rating_8l.csv` (đầu ra LIVE của `rate_bank`) | **Không ảnh hưởng** — module này không bao giờ ghi file đó. |

Phải sửa cách phát biểu: "0 quyết định V2.4 đổi" ĐÚNG (mọi consumer V2.4 gate ở biên 3/4), nhưng
**KHÔNG** được rút gọn thành "0 consumer nào đổi".

## 5. H2 — tầng T1.5 trong `cpi_vn.py`

Thứ tự tầng mới **T1 > T1.5 > T3 > T2**. T1 (NSO live) ưu tiên tuyệt đối, T2/T3 **giữ nguyên** làm
fallback. Có file: T1=13 tháng, T1.5=211, T3=12 (chỉ 2007), T2=0. Mất file: T1=13, T3=48, T2=175 —
**byte-identical với bản trước khi wire** (đã assert, không phải nhìn mắt).

**§14 freshness-check thật:** `cpi_coverage(end)` đọc tháng cuối **TỪ FILE** (mutation-test chứng minh
gate là data-driven, không hardcode) và in cảnh báo **một lần** khi caller vượt mọi tầng THẬT, nêu rõ
cách sửa = refresh `NSO_CPI_YOY_REAL` từ GSO (refresh FiinPro là bất khả sau 28/09). `dcf_valuation.py`
gọi `end="2026-12-01"` ⇒ cảnh báo đúng 4 tháng 2026-09→12.

**Đổi tên** `NSO_CPI_YOY_AVG_REAL` → `NSO_CPI_CORE_YOY_REAL`: xác minh lại trước khi đổi — khớp
`core_yoy_pct` **13/13**, khớp headline **0/13**; `grep --include=*.py` toàn repo: **0 file .py đọc
tên cũ**.

Số đo (tái lập CHÍNH XÁC finding, không xê dịch):
- `macro_confidence_regime`: REG_C **27/185** tháng, REG_B **17/185** — **cùng danh sách tháng** với
  `h2_regime_flips.csv`; **0 tháng** trong episode 2011 hoặc 2022-H2.
- DCF: CPI TB 5 năm 3,4426% → 3,4147% (Δ −0,0279pp) nhưng `g_term` **bất biến 6,8000%** (trần
  `cap_rf = r_f`) ⇒ fair value Δ = **0,0** trên 7/7 mã (CSV DGC DRI NCT SAB TV1 VNM).
- Chuỗi wire trùng khít `h2_cpi_series.csv` của finding: n=236, max|diff| = 0,0.

**Consumer `cpi_vn` — kiểm kê lại đầy đủ** (quant-skeptic phát hiện thiếu 1):
`macro_confidence_regime.py` · `dcf_valuation.py` · **`deploy_golive_dt5g_v4/golive_recommend_v23.py:920`
— cổng đòn bẩy CAPIT, `CAPIT_LEVER_PIT_CPI_THRESHOLD = 6.0` (dòng 579), CHẶN vay khi PIT CPI ≥6%.**
Đo thật: giá trị LIVE tại 2026-09-25 là **4,69% trước và sau** (nhánh đó đã lấy `max(nội suy, số NSO
thật gần nhất)` nên T1.5 không thể hạ xuống). 4 tháng lịch sử đổi trạng thái cổng, **tất cả cùng một
chiều — proxy nội suy THỔI PHỒNG và đã chặn vay oan**: 2012-07 6,88→5,35 · 2012-08 6,87→5,04 ·
2013-10 6,23→5,92 · 2013-11 6,11→5,78. Cổng chỉ đánh giá live nên 4 tháng này là tư liệu.

**Không bán kèm:** không có bằng chứng nào nói việc này tăng lợi nhuận. Đổi `DCF_TERMINAL_MODE` sang
`cpi` thì −0,0279pp đi thẳng vào `g_term` — kết luận "Δ=0" HẾT hiệu lực.

## 6. Selfcheck

| File | Assertion | TZ | Mutation-kill |
|---|---|---|---|
| `rating_8l_history_bank_aq_selfcheck.py` | **33 PASS / 0 FAIL** | no-TZ, UTC, America/New_York | 2 (fail-open override; cliff NPL>3%→4 bị bắt 59 lần) |
| `cpi_vn_tier15_selfcheck.py` | **33 PASS / 0 FAIL** | no-TZ, UTC, Pacific/Auckland | 1 (T1.5 "không bao giờ hết hạn" làm câm gate) |

Log: `h1_selfcheck_alltz.log`, `h2_selfcheck_alltz.log`, `e2e_ab.log`, `screen_top25_ab.log`.

## 7. Registry (§13 — ghi `.proposed`, chưa áp live)

- `kb/data_registry/fundamentals/fiinprox_bank_ratios_quarterly.md.proposed` — mục Consumer.
- `kb/data_registry/macro/fiinprox_cpi_monthly.md.proposed` — bẫy #1 đã sửa + mục wire T1.5.

## 7b. quant-skeptic

**CONFIRMED, confidence `medium`** (log `mike/logs/verify_20260927_024812_1975996.log`). Cả 3 lỗ hổng
reviewer nêu đều THẬT; tôi tự xác minh lại từng cái rồi vá vào docstring + README: (1) 365 vs 360 —
đã tách 2 panel (§2); (2) biên `rating≤2` + ABB (§4b); (3) cổng CPI CAPIT của golive (§5). Một chi
tiết reviewer ghi lệch: `anomaly_scan.py` nằm ở `mike/agents/Taylor/`, không phải gốc `WorkingClaude/`
(nội dung `:156 rating<=2` thì đúng); và 3 consumer `≤2` khác đọc `data/rating_8l.csv` nên KHÔNG bị
ảnh hưởng như reviewer ngụ ý. Không cái nào đổi quyết định merge — nhưng chúng đổi NỘI DUNG câu hỏi
cho user: sign-off phải phủ **BVB và ABB**, không chỉ BVB.

## 8. Còn treo

1. **User duyệt merge** — cả 2 file là input production; và §4 (BVB) là Δ live thật.
2. Nếu merge H1: chạy lại `rating_8l_history.py` canonical để refresh `tav2_bq.fa_ratings_8l`
   (KHÔNG đặt `R8L_HIST_NO_BQ_REFRESH`), rồi `universe_pit_quality` sẽ đổi trạng thái BVB.
3. Kết luận "0 quyết định đổi" **hết hiệu lực** nếu ai đặt `BASKET_GATE_RATING<3` hoặc `ETF_LIQ`
   sang biến thể `quality=tilt` (`custompitgq`) — đã ghi thành cảnh báo trong docstring.
4. Hậu kiểm BẮT BUỘC sau merge: `build_universe_pit_quality` phải cho BVB → `RATING_FAIL`, ABB giữ
   `QUALITY_OK`, và danh sách tier W của `anomaly_scan.py` chỉ THÊM ABB.
5. Việc RIÊNG, ngoài job này: refresh `NSO_CPI_YOY_REAL` từ GSO (2026-07/08/09 đang là forward-fill —
   nay §14 cảnh báo mỗi lần chạy); `ascending=False` trong 15 screen; `merge_cpi` as-of đầu tháng làm
   `macro_confidence_regime` thấy CPI tháng M trước khi GSO công bố (có TRƯỚC wire này, reviewer nêu).

## 9. Xác minh lại ĐỘC LẬP (attempt 2 của job, 2026-09-27 ~10:05 ICT)

Attempt 1 bị cắt sau khi quant-skeptic CONFIRMED nhưng **trước** khi commit phần vá docstring +
registry + câu hỏi user. Trước khi commit, attempt 2 **đo lại từ đầu** mọi con số mà attempt 1 mới chỉ
ghi ra văn bản — không chép lại lời reviewer, không tin self-report:

| Claim | Cách đo lại độc lập | Kết quả |
|---|---|---|
| 360/981 dòng BANK đổi rating | merge `ab_old.csv.gz` × `ab_new.csv.gz` trên `(ticker,eff_date,q_time)`, `validate="1:1"`, 53.687 dòng khớp hết | **360/981 ✓** |
| 266 dòng vượt biên `≤2` | cùng merge | **266, 1→3:153 · 2→3:112 · 3→2:1 ✓** |
| 0 dòng LỊCH SỬ đổi cổng `≤3` | cùng merge | **6 dòng đổi cổng, TẤT CẢ là dòng mới nhất** (PGB/BVB/BAB 3→4, SGB/NVB 3→5, KLB 4→3) ⇒ 0 dòng lịch sử ✓ |
| 0 dòng route khác BANK đổi | cùng merge | **0 ✓** |
| ABB là Δ live duy nhất ở biên `≤2` | lọc dòng mới nhất mỗi mã | **ABB 2026-07-21 3→2, duy nhất ✓** |
| Cổng CPI CAPIT live không đổi | load 2 bản `cpi_vn.py` (master vs branch) trong cùng process, tái lập `golive_recommend_v23.py:918-933` | **GATE = 4,6900% cả 2 bản, `blocks=False` ✓** |
| 4 tháng lịch sử flip cổng 6% | `merge_cpi` 2011-01→2026-06 cả 2 bản | **đúng 4 tháng, đúng số: 2012-07 6,88→5,35 · 2012-08 6,87→5,04 · 2013-10 6,23→5,92 · 2013-11 6,11→5,78 ✓** |
| `golive_recommend_v23.py:920` + `:579` + `anomaly_scan.py:156` | `grep -n` | **cả 3 khớp ✓** |
| Selfcheck vẫn PASS sau khi sửa docstring | chạy lại cả 2 | **33/33 + 33/33 PASS, `py_compile` OK ✓** |

**Một điều attempt 1 không ghi, đáng ghi:** `cpi_vn.py` giải đường dẫn T1.5 theo `__file__`
(`FIINPRO_CPI_CSV`, override chỉ cho selfcheck) còn `rating_8l_history.py` theo `WORKDIR` hardcode
(`BANK_AQ_CSV`). Hệ quả thực tế: chạy trong **worktree** thì H1 vẫn đọc được file thật (WORKDIR trỏ về
checkout canonical) nhưng H2 **suy biến ỒN ÀO về T2** vì `<worktree>/WorkingClaude/mike/` không tồn tại
(`.gitignore` repo ngoài ẩn repo lồng). Đây là hành vi ĐÚNG và đã ghi trong docstring `cpi_vn.py`, chỉ
cần biết khi đọc log: selfcheck H2 trong worktree phải đặt `FIINPRO_CPI_CSV=` trỏ về file thật.

`ab_old.csv` / `ab_new.csv` đã **gzip** khi commit (2,3MB → 319KB mỗi file); giải nén trước khi đo lại.
