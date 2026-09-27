# PART2 — audit "lỗi đo cơ bản", 3 việc paper-only còn lại
job=`Taylor_20260927_052433` (attempt 2) · 2026-09-27 · tiếp `REPORT.md` cùng thư mục · **KHÔNG sửa code
production, KHÔNG merge**. Bất biến (a)-(f) và quy tắc phán: xem `PREREG.md`.

Artifact đo: `part2/`. Nhánh đề xuất: `proposal/fail-e-fail-g-pricebasis-gate` @ worktree
`/home/trido/thanhdt/wt-faileg-proposal` (chưa merge).

---

## (A) FAIL-D — chân park custom30V dùng total-return gộp, không trừ thuế cổ tức 5%

### Cách đo
Với **49 kỳ rebal** của `data/custom30v_8l_publish.csv`: thành viên + `weight` THẬT của từng kỳ,
cổ tức TIỀN từ `tav2_bq.corporate_action` (chỉ event cổ tức tiền, `value_per_share`, **ex-date rơi
trong `[effective_from, effective_to)` của chính kỳ đó**), chia cho **giá THÔ** (`COALESCE(Price,Close)`)
tại ngày rebal ⇒ DY hiệu dụng theo trọng số từng kỳ. Script: `part2/measure_dy_haircut.py`; dữ liệu
thô `part2/div_events.csv` (1.832 event), `part2/px_at_rebal.csv`; kết quả `part2/dy_by_rebal.csv`
+ `part2/dy_summary.json`.

Chất lượng đo: **0 (ticker,kỳ) thiếu giá**, trọng số phủ ≥ 0,999997 mọi kỳ, **0 event trạng thái
"announced"** rơi trong cửa sổ (toàn bộ là `executed` ⇒ không dùng cổ tức chưa thực hiện).
Cross-check độc lập: cột `DY` của BQ theo cùng trọng số (`part2/dy_col_crosscheck.csv`) cho
6,82%/năm ở kỳ 2014-08 so với 6,20%/năm đo từ event — cùng cỡ, cùng hình dạng giảm dần theo năm.

### Kết quả — DY hiệu dụng của rổ park
| | giá trị |
|---|---|
| DY tích luỹ 49 kỳ / 11,86 năm (gộp) | **2,924 %/năm** |
| DY quy năm từng kỳ: trung bình / median | 2,85 % / 2,05 % |
| khoảng | 0,00 % → 11,27 % (kỳ 2015-05 nhiều cổ tức) |
| tổng số event cổ tức tiền dùng | 327 |

DY theo năm (tổng `dy_period` các kỳ BẮT ĐẦU trong năm): 2014 2,46 · 2015 4,93 · 2016 **6,20** ·
2017 4,58 · 2018 2,28 · 2019 2,12 · 2020 1,51 · 2021 **0,91** · 2022 0,87 · 2023 2,06 · 2024 2,67 ·
2025 1,90 · 2026 2,19 (%). Xu hướng giảm mạnh 2016→2022 rồi hồi — khớp DY toàn thị trường
(`part2/market_dy_by_year.csv`: liq-weighted 4,96% năm 2011 → 1,28% năm 2021).

### Haircut và tác động — **dấu và độ lớn**
Hệ số haircut mỗi đồng cổ tức: `k = thuế 5% + phí 0,1% × (1−thuế) = 5,095%`.

| đại lượng | giá trị |
|---|---|
| tích luỹ `(1 − k·DY_kỳ)` trên 49 kỳ | 0,982480 |
| drag trên **mức tăng trưởng của chính chân park** | **0,149 pp/năm** |
| drag lên CAGR chân park (nếu gộp 16,90%) | 0,174 pp/năm |
| drag lên CAGR chân park (nếu gộp 24,38%) | 0,185 pp/năm |
| **drag lên CAGR NAV R3 tổng** (nhân tỷ trọng park THẬT) | **0,055 pp/năm** |

Chân NAV: tỷ trọng park theo NAV trung bình toàn kỳ **24,53%** (2014-01-02→2026-06-19, 12,46 năm
lịch), tích luỹ `(1 − k·DY_kỳ·park_share_kỳ)` = 0,994481 ⇒ **CAGR R3 24,3775% → 24,3223%**
(`part2/nav_drag.txt`, `part2/nav_drag_by_rebal.csv`).

**Tác động lên +2,01pp parking mới pin** (registry mục `2026-09-27 (bis)`): **+2,01pp → +1,95pp**.
Dấu là ÂM (parking bị đánh giá cao hơn thực tế), độ lớn **−0,055pp**.

Độ nhạy theo thuế: 0% → 0,001 pp/năm · 5% → 0,055 · 10% → 0,109.

### Ý nghĩa cho quyết định parking 70/80/85% của user
**Không đổi quyết định.** −0,055pp/năm nhỏ hơn một bậc so với thứ đã đảo dấu kết luận parking ở
hậu kiểm 09-27 (+7,4pp → +2,01pp, và parking LÀM XẤU Sharpe/DD/Calmar). Tăng tỷ lệ park từ 70%→85%
chỉ làm drag tăng tuyến tính theo `park_share` (≈ +0,012pp/năm mỗi 20% tăng tỷ trọng park) — đây
KHÔNG phải lý do để chọn mức nào. Lý do vẫn là **Calmar/DD**, và mốc 80% đã mất căn cứ (question
`custom30v-park-fraction-80-mat-can-cu` còn treo).

**Không chạy knob haircut trên engine** vì đã đo được bằng số học đúng theo định nghĩa (drag hình
học trên chuỗi level, có tỷ trọng park thật theo từng kỳ) và độ lớn 0,055pp nhỏ hơn sai số làm tròn
của bản pin — một leg engine ~1h chỉ để xác nhận con số ở chữ số thập phân thứ hai là không đáng.
Ghi thẳng: **chưa có chân engine, chỉ có chân số học**; nếu sau này park_share đổi lớn thì đo lại.

---

## (B) Quét 2 file chưa quét: `backtest_recovery_alloc.py` + `..._2011.py`

Cả hai được `data/results_registry.md` trích. Bảng theo 6 bất biến PREREG:

| bất biến | `backtest_recovery_alloc.py` (2014+) | `backtest_recovery_alloc_2011.py` |
|---|---|---|
| (a) RETURN-ADJ | **PASS** — `:35` `d["v"].pct_change()` trên `VNINDEX` (level index), không nhân số CP | **PASS** — `:52` như trên |
| (b) HỆ QUY CHIẾU | **PASS có ghi chú** — không có mcap/notional; lọc thanh khoản `:30` `Trading_Value_1M_P50>3e9` là ngưỡng **VND danh nghĩa cố định** cho cả 2013-2026 ⇒ siết dần theo lạm phát (`Inflation_7`), universe trôi | **PASS cùng ghi chú** (`:40`) |
| (c) KHÔNG ĐẾM 2 LẦN | **FAIL** (xem B1) | **FAIL** (xem B1) |
| (d) SỐ CP ĐÚNG NGÀY | N/A | N/A |
| (e) KHÔNG LOOK-AHEAD | **FAIL** (xem B2); state đọc đúng bảng `vnindex_5state_dt5g_live` `:26` — PASS phần đó | **FAIL** (B2) + **FAIL** (B3 nguồn regime) |
| (f) ĐƠN VỊ/TẦN SUẤT | **PASS** — `:81` `yrs=days/365.25`, `:83` `spd=len(r)/yrs` (đúng chuẩn; trái ngược FAIL-F ở `bootstrap_nav.py`). Nhưng **FAIL** ở tái lập: xem B4 | **PASS/FAIL** y hệt |

### B1 — FAIL (c): chân cổ phiếu KHÔNG có cổ tức, chân tiền ĂN lãi gửi thật ⇒ lệch quy ước hai chiều
`:72-73` (2014) / `:102-103` (2011): `w·r_vnindex + (1−w)·dep_d − (w−1)·bor_d`. `VNINDEX` là index
**GIÁ**, không phải total return ⇒ chân cổ phiếu mất toàn bộ cổ tức, trong khi chân tiền nhàn rỗi
được cộng lãi Big-4 **THẬT** (trung bình 5,96%/năm ở cửa sổ 2014+, **6,99%/năm** ở cửa sổ 2011+).
Hai lệch CÙNG CHIỀU: đều thưởng cho việc GIỮ TIỀN, tức đều đánh vào chính luận điểm mà 2 file này
được viết để kiểm ("khủng hoảng rẻ thì giải ngân nhiều hơn").

**Đo thật** (`part2/diag_recovery_2011.py` → `part2/out_diag_2011.txt`), cộng lại DY thị trường
liq-weighted ròng thuế 5% (2,43%/năm toàn kỳ; **4,09%/năm giai đoạn 2011-13**) vào chân cổ phiếu,
cửa sổ 2011-01-04→2026-09-25:

| variant | CAGR trước | CAGR sau | Δ | **seg 2011-13 trước → sau** |
|---|---|---|---|---|
| BASELINE | 11,9 % | 13,2 % | +1,3 | 9,1 % → 10,6 % (+1,5) |
| recovery deep (C.70,B.70) | 11,4 % | 13,1 % | +1,7 | 4,7 % → 7,7 % (**+3,0**) |
| DEPTH lev-free 0,95 | 11,0 % | 12,8 % | +1,8 | 2,8 % → 6,3 % (**+3,5**) |
| DEPTH margin 1,5 | 9,3 % | 11,3 % | +2,0 | −2,7 % → **+1,5** (**+4,2**) |
| +DEPgate lev-free 0,95 | 12,3 % | 13,7 % | +1,4 | 9,4 % → 11,3 % (+1,9) |

Lệch **BẤT ĐỐI XỨNG**: variant giải ngân nhiều bị phạt 2-3× nặng hơn baseline, và đúng ở segment
khủng hoảng 2011-13 (nơi DY cao nhất). "DEPTH margin 1,5 làm âm 2011-13" là **artifact đo**, thực
tế +1,5%.
**Xếp hạng KHÔNG đảo**: baseline vẫn ≥ các variant deploy thuần; `+DEPgate lev-free0,95` vẫn là
variant duy nhất vượt baseline (13,7 vs 13,2) — nó đã vượt trước khi sửa (12,3 vs 11,9). Vậy
**kết luận định tính giữ nguyên, nhưng độ lớn "hình phạt khi giải ngân" bị phóng đại 1,5-4,2pp**.

**Lệch quy ước lãi tiền gửi** (`part2/out_diag_dep0.txt`): CLAUDE.md §Backtest chốt **lãi tiền gửi
nhàn rỗi 0%/năm** cho mọi backtest dùng chung; 2 file này cố ý dùng Big-4 thật (docstring gọi là
"honest"). Đo ở cửa sổ END=2026-06-19:

| file / variant | dep = THẬT | dep = 0 (quy ước) | Δ |
|---|---|---|---|
| 2014 BASELINE | 13,57 % | 10,95 % | **2,62** |
| 2014 DEPTH 1,0 | 13,37 % | 11,11 % | 2,26 |
| 2011 BASELINE | 12,37 % | 8,62 % | **3,76** |
| 2011 DEPTH 0,95 | 11,16 % | 8,82 % | 2,34 |
| 2011 DEPTH 1,5 | 9,41 % | 7,71 % | 1,71 |

⇒ **2,6-3,8pp CAGR của baseline đến từ lãi tiền gửi**, và lợi thế đó giảm dần theo mức giải ngân
(baseline hưởng nhiều nhất). Hệ quả vận hành: **số CAGR của 2 file này không so sánh trực tiếp được
với bất kỳ số pin nào của V2.4/R3** (những số đó dùng 0%). Không phải "sai" — nhưng registry đang
đặt chúng cạnh nhau mà không ghi chú.

### B2 — FAIL (e): tín hiệu `pbz` tính trên universe `ticker_prune` KHÔNG point-in-time
`:28-31` (2014) / `:38-42` (2011): median `pb_z` theo tháng lấy `FROM tav2_bq.ticker_prune` — đúng
anti-pattern `coding_guidelines §9b` (membership của `ticker_prune` là universe chất lượng **as-of
hôm nay**). Đây là **tín hiệu kích hoạt giải ngân**, không phải cột hiển thị.

**Đo thật** (1 query BQ, 165 tháng 2013-01→nay), thay universe bằng `tav2_mike.universe_pit`
(`in_universe`, join theo `(ticker,time)`):
- **18/165 tháng (10,9%) ĐỔI PHÍA của ngưỡng `pbz ≤ −0,3`** — tức 18 tháng đổi trạng thái
  deploy/không-deploy.
- `pbz` trung bình lệch **−0,1032** (universe PIT trông RẺ HƠN) ⇒ bản legacy **giải ngân ÍT hơn
  đáng lẽ phải**, cùng chiều với B1.
- Số tên/tháng: 149,3 (prune + lọc thanh khoản) vs 302,9 (PIT).
- ⚠️ Caveat đã biết: chân PIT bỏ lọc `Trading_Value_1M_P50>3e9` (bảng `universe_pit` đã có luật
  thanh khoản riêng) nên phần lệch trộn cả "đổi universe" và "đổi lọc thanh khoản" — chưa tách
  được bằng 1 query. Con số 18/165 là **thượng giới** của tác động.

### B3 — FAIL (e) + văn xuôi SAI trong docstring: file 2011 chạy trên regime KHÔNG phải production
`:29` `REGIME` mặc định `"base"` → `:35` đọc `tav2_bq.vnindex_5state`. Việc chọn base là **có chủ
ý và có ghi lý do** (DT5G chỉ từ 2014) nên KHÔNG phải cái bẫy nhãn bảng. Nhưng lời biện hộ ở
docstring `:7-9` — *"DT5G == base in benign windows and only ADDS a macro cap on 4 episodes 2014+
→ using the base is the MORE permissive (harder) test"* — **SAI**: base v3.4b có **~153
transition**, DT5G có **49**; khác biệt lớn nhất KHÔNG phải macro cap mà là **thiếu hẳn bộ làm mượt
DT 4-gate** (`DT_10_25_25`). Chuỗi base whipsaw nhiều hơn ⇒ nhiều TC hơn, phân bố state khác ⇒
segment 2014+ của file này **không so sánh được** với file 2014 sibling, và không nằm trên đường
cong regime production. Chưa đo delta (cần 1 leg `REGIME=dt5g` trên cửa sổ 2014+) — **rẻ, nên đo
khi có ai dùng lại số của file này**.

Cùng ô: giả thiết đầu tiên của tôi rằng `VNINDEX_PE` NULL trước 2016-07 (làm `fed_gate` thành
no-op trong đúng cửa sổ khủng hoảng) — **BỊ BÁC BỎ bằng đo**: trên `ticker_prune`, `VNINDEX_PE>0`
liên tục **196 tháng từ 2010-06**, giá trị 7,67-22,49 (2011 avg 10,5 · 2012 11,1 · 2013 13,3) —
hợp lý. Trên `tav2_bq.ticker` cột này giờ có từ **2006-03-30** ⇒ ghi chú "backfill pending
2026-07-29" đã lỗi thời, backfill ĐÃ xong. Docstring `:45`/`:70` đúng. **PASS.**

### B4 — FAIL (f) tái lập: cả 2 file KHÔNG neo `END_DATE` ⇒ số pin trôi theo ngày chạy
Không file nào có biến cắt cuối; `load()` lấy hết dữ liệu BQ hiện có. Đo:

| | END=2026-06-19 | END=2026-09-25 | Δ |
|---|---|---|---|
| 2014 BASELINE | 13,6 % | 13,2 % | −0,4 |
| 2011 BASELINE | 12,4 % | 11,9 % | −0,5 |
| 2011 DEPTH 1,5 | 9,4 % | 9,3 % | −0,1 |

⇒ mọi số của 2 file này trong `results_registry.md` **không tái lập được** nếu không ghi kèm ngày
chạy. Cùng LỚP với phát hiện `dsr_pbo_annex.py::family_paths()` glob động (job `_043541`): số pin
phụ thuộc trạng thái thế giới lúc chạy chứ không phải chỉ tham số. Cách sửa rẻ nhất: thêm
`END_DATE = os.environ.get("END_DATE", ...)` và ghi vào tên file/ tag như `pt_v23` đang làm.

Phụ: `fired` sessions (2014 file) = **238** ở cả hai cửa sổ; tháng fire tập trung 2019 (38), 2020
(86), 2022 (44), 2023 (66), 2018 (4) — đúng episode COVID/SCB, không fire ở 2021 đắt. Chân
episode-faithfulness này **PASS**.

---

## (C) FAIL-E + FAIL-G — đề xuất sửa + cổng cơ học

Nhánh `proposal/fail-e-fail-g-pricebasis-gate`, worktree `/home/trido/thanhdt/wt-faileg-proposal`,
**4 file, +245/−9**. Patch dạng file: `part2/proposal_fail_e_g_gate.patch`. **CHƯA MERGE.**

### C1 — Cổng cơ học T5 `scan_price_basis()` (mở rộng `basket_price_basis_selfcheck.py`, +145 dòng)
Luật: trong biểu thức TIỀN/ADV/mcap-weight, cấm nhân **SỐ LƯỢNG thô** (`Volume*`, `OShares`) với
**GIÁ ĐÃ ĐIỀU CHỈNH** (`Close`, `Close_T1*`). Giá đúng = `Price`, `COALESCE(Price,Close)`, `pxw_sql()`.

Ba quyết định thiết kế, mỗi cái để chặn một cách cổng tự chết:
1. **Phạm vi = 12 file BẢO VỆ, không phải cả repo.** Đo thật: regex khớp **2.349 dòng / 1.010 file
   `.py`** toàn repo, gần hết là `backtest_*`/`test_*` legacy registry không trích. Một cổng 2.349
   mục là cổng không ai chạy. Siết dần bằng cách thêm file vào `PROTECTED`.
2. **Phân biệt CODE với VĂN XUÔI bằng AST + tokenize**, không bằng "dòng bắt đầu bằng `#`". Vòng
   thử đầu báo 3 dòng **docstring** của `custom_basket.py` (`:35`, `:46`, `:58`) — chính đoạn văn
   MÔ TẢ cái bug này. Điều kiện thứ hai: dòng phải chứa từ khoá SQL **phân biệt hoa/thường**
   (`AND` ≠ `and`). Xử lý riêng PEP 701: Python 3.12 tách f-string thành `FSTRING_*`, không còn
   `STRING` ⇒ chỉ lọc `tok.STRING` sẽ báo trùng; runner thật (`$DNA_PYEXE`) LÀ 3.12.
3. **Miễn trừ có trần** (`EXEMPT_MARK = "pricebasis-gate:legacy-control"`, `EXEMPT_BUDGET = 1`) —
   chỉ cho chân đối chứng A/B; thêm cái nữa phải nâng trần trong cùng commit (ratchet như
   `bin/tz_anchor_gate.py`). Dùng comment SQL `--` nên BigQuery vẫn hợp lệ.

**ĐÃ VERIFY THẬT (yêu cầu bắt buộc của job)** — chạy `scan_price_basis(root=...)`:

```
root = /home/trido/thanhdt/WorkingClaude  (HEAD, CHƯA vá)
      pt_v23_audit_2014.py:895  GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30
      custom30v_hybrid.py:72    ... AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) nd
vi phạm: 2   miễn trừ: 0
root = wt-faileg-proposal (ĐÃ vá)
      [miễn trừ có đánh dấu] pt_v23_audit_2014.py:910
vi phạm: 0   miễn trừ: 1
```

⇒ **fire ĐÚNG `pt_v23:895` ở HEAD** như job yêu cầu, và **bắt thêm 1 ca chưa có trong FAIL list
gốc: `custom30v_hybrid.py:72`** — cùng lớp lỗi, ở file dựng overlay xếp hạng custom30V. Đây chính
là lý do cần cổng cơ học chứ không chỉ selfcheck hành vi: `LAG_ADV_BASIS` và `custom_basket.py:333`
đã vá 2026-08-02, mà 2 call-site khác sống thêm gần 2 tháng.
Chạy riêng cổng, không đụng BQ: `$DNA_PYEXE basket_price_basis_selfcheck.py --scan-only`.

### C2 — FAIL-E: `pt_v23_audit_2014.py:894-895` nhánh `ETF_LIQ="creation"`
Ba lỗi trong 2 dòng: (1) `Volume_3M_P50*Close` trộn hệ quy chiếu; (2) cửa sổ chọn top-30
**hardcode 2020-01-01..2025-01-01** rồi áp cho backtest từ 2014 = hindsight membership;
(3) `IN (SELECT DISTINCT ticker FROM ticker_prune)` không có `time` (§9b).

Đề xuất: env `ETF_CREATION_BASIS` (`pit` mặc định | `legacy` giữ hành vi cũ + tag filename theo §8).
`pit` = ADV trên `COALESCE(Price,Close)` + cửa sổ **365 ngày kết thúc tại `START_DATE`** + `EXISTS`
trên `UNIVERSE_PIT_TABLE`. **Giới hạn thừa nhận:** rổ vẫn TĨNH cho cả backtest (chọn một lần) —
hết look-ahead chứ chưa point-in-time theo quý; PIT đầy đủ là thay đổi lớn hơn, ngoài phạm vi.
**Chưa đo delta NAV** (cần 1 leg engine với `ETF_LIQ=creation`; nhánh này mặc định `off` nên không
ảnh hưởng số R3 đang pin — đó là lý do hoãn).

### C3 — FAIL-G: `rating_8l_history.py:116-117` `ANY_VALUE(ICB_Code)` không có `time`
**Đo trên `tav2_bq.ticker`** (không đoán từ tên hàm):
- **1.285/1.291 mã chỉ có MỘT `ICB_Code`** ⇒ nguồn gần như không đổi theo thời gian.
- **6 mã có HAI giá trị**: DIH (2357→8633 từ 2026-08-21, 22 phiên) · HDG (8633 4.136 phiên →7535
  từ 2026-09-07, **15 phiên**) · LIC (2357 27 phiên → 2353 từ 2017-07-12) · SBM (7535 2.186 phiên,
  bị 2357 chen vào **27 phiên rải rác, mỗi lần 1-4 phiên**) · TV3 (2357→2791 từ 2015-10-05) ·
  VNH (3573/8985).
- ⇒ tái phân ngành THẬT là cực hiếm; phần lớn là **NHIỄU một-vài-phiên**. Vì thế as-of theo
  `MIN(time)` mỗi mã là KHÔNG đủ — nó biến một phiên nhiễu thành "đổi ngành vĩnh viễn".

Đề xuất: lấy **các ĐOẠN LIÊN TIẾP** của `ICB_Code`, chỉ coi là xác lập khi đoạn dài
`≥ ICB_MIN_RUN = 20` phiên, rồi `merge_asof` backward theo `eff_date`. Tất định (hết `ANY_VALUE`).

**ĐO TÁC ĐỘNG THẬT** — chạy bản vá, xuất ra tên **KHÔNG canonical** (§8)
`part2/rating_8l_history_EXP_icbpit.csv`, diff với `data/rating_8l_history.csv` (bản 09-27 10:36):

| | |
|---|---|
| dòng đổi `route` | **98** (HDG 49 POWER→REALESTATE · DIH 49 REALESTATE→COMPOUNDER) |
| dòng đổi `rating` | **36** (HDG 3→2 ×21, 4→2 ×2, 4→3 ×5 · DIH 3→4 ×5, 5→4 ×3) |
| **dòng vượt ranh 3/4** (gate LAG cứng + gate custom30V) | **12** |

⇒ **ĐƯỜNG QUYẾT ĐỊNH, không phải hiển thị**: HDG có mặt **26 lượt** trong
`data/custom30v_8l_publish.csv`. Bản hiện tại gán HDG = POWER cho **cả 49 quý từ 2014-08-01** dù
`ICB_Code=7535` chỉ tồn tại **15 phiên kể từ 2026-09-07** — hồi tố 12 năm từ một nhãn 3 tuần tuổi,
và vì `ANY_VALUE` không tất định, lần chạy sau có thể ra khác. Hướng lệch: bản vá làm HDG **TỐT
hơn** (thang REALESTATE) ⇒ bug legacy đang **loại HDG oan** ở 7 quý.

**Giới hạn phải nói rõ — trả lời trực tiếp câu hỏi của job ("có sửa được từ dữ liệu này không?"):**
`ICB_Code` **CÓ** time-varying trong `tav2_bq.ticker`, nhưng chỉ ghi lại 6 lần đổi và **5/6 xuất
hiện từ 2017 trở về sau, 2 ca mới nhất chỉ trong 2 tháng gần đây**. Nguồn **hầu như không ghi lại
tái phân ngành trước 2026**. Vậy: bản vá đảm bảo **TẤT ĐỊNH + đúng PIT cho những lần đổi ĐƯỢC
GHI**; những lần đổi KHÔNG được ghi thì **không sửa được từ dữ liệu này** — cần nguồn phân ngành
có vintage (FiinProX/HOSE).

**Nợ đã biết trong CHÍNH bản vá** (tự soi, chưa vá): `SELECT ticker, icb, MIN(icb_from) ... GROUP BY
ticker, icb` gộp mọi đoạn cùng mã về đoạn SỚM NHẤT. Nếu một mã nhiễu tích được một đoạn ≥20 phiên
thì mã đó thành hiệu lực vĩnh viễn từ đó — sai. Hiện tại **vô hại: 0/1.291 mã gặp ca này** (kiểm
tra runs≥20 của SBM: chỉ 7535 có đoạn ≥20, các đoạn 2357 đều <20 ⇒ SBM giữ 7535 đúng). Nhưng đây
là bẫy latent nếu `ICB_MIN_RUN` bị hạ.

### C4 — `custom30v_hybrid.py:72` (ca cổng T5 tự tìm ra, KHÔNG có trong FAIL list gốc)
Hai lỗi 1 dòng: `Volume_3M_P50*Close` + `IN (SELECT DISTINCT ticker FROM ticker_prune)` không `time`.
Đã vá trong nhánh (đổi sang `COALESCE(Price,Close)` + `EXISTS` trên `universe_pit`). **Chưa đo
delta** — file này dựng overlay xếp hạng custom30V, cần 1 lần chạy để biết pool thanh khoản đổi bao
nhiêu tên.

---

## Bẫy môi trường mới, đã cắn thật trong chính job này
`source wc_env.sh` **có `cd "$WORKDIR_8L"` ở dòng 12** ⇒ sau khi source, cwd bị đưa về
`/home/trido/thanhdt/WorkingClaude` (main), bất kể bạn vừa `cd` vào worktree nào. Lần chạy đầu của
tôi `cd wt-faileg-proposal/WorkingClaude && source wc_env.sh && $DNA_PYEXE rating_8l_history.py` đã
**âm thầm chạy bản CHƯA VÁ ở main** và cho ra file **byte-identical** với canonical — tôi gần như
kết luận "bản vá là no-op". Dấu hiệu nhận ra: md5 trùng khít bản canonical. **Luật: chạy file của
worktree phải dùng ĐƯỜNG DẪN TUYỆT ĐỐI tới file trong worktree**, không dựa vào cwd.
(Cùng họ với `verify-before-done`: selfcheck/chân đối chứng PASS/no-op vì môi trường, không vì code.)

## Tổng kết PART2 — cái gì cần ai làm
| # | việc | trạng thái |
|---|---|---|
| A | FAIL-D đã đo: parking +2,01pp → **+1,95pp** (−0,055pp/năm) | **xong, không đổi quyết định 70/80/85%** |
| B1 | 2 file recovery_alloc: thiếu cổ tức + lãi gửi lệch quy ước, phạt variant deploy 1,5-4,2pp ở 2011-13; xếp hạng KHÔNG đảo | **đã đo**; cần Mike/user quyết có ghi caveat vào registry |
| B2 | `pbz` trên `ticker_prune` không PIT: 18/165 tháng đổi phía ngưỡng deploy (thượng giới) | **đã đo**, chưa sửa |
| B3 | file 2011 chạy regime base (153 transition) ≠ production; docstring biện hộ SAI | chưa đo delta, rẻ |
| B4 | cả 2 file không neo `END_DATE` ⇒ số registry không tái lập (±0,5pp) | cần sửa rẻ, cùng lớp `family_manifest` |
| C1 | cổng T5 grep-gate: **verify fire đúng `pt_v23:895`**, bắt thêm `custom30v_hybrid.py:72` | **chờ user duyệt merge** |
| C2 | FAIL-E `ETF_CREATION_BASIS` (mặc định `pit`, `legacy` rollback 1 từ) | chờ duyệt; delta chưa đo (`ETF_LIQ=off` mặc định) |
| C3 | FAIL-G ICB PIT: 98 route / 36 rating / **12 vượt ranh 3/4**, HDG trong rổ 26 lượt | chờ duyệt; **nếu merge phải chạy lại `rating_8l_history.csv` + hậu kiểm gate LAG/custom30V** |
| C4 | `custom30v_hybrid.py:72` | chờ duyệt; delta chưa đo |
