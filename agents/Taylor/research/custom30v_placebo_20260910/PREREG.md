# VÒNG 5 — TIỀN ĐĂNG KÝ: THÍ NGHIỆM PHÂN RÃ (placebo) nguồn gốc +2,62pp của L1b
job `Taylor_20260909_165335` · viết **TRƯỚC** khi chạy bất kỳ chân nào · **PAPER-ONLY**
· AUDIT_EXP_TAG `c30vpb*` · thư mục `agents/Taylor/research/custom30v_placebo_20260910/`

---

## 0. Vòng này KHÔNG đi tìm một chân để wire

Deliverable là **một phép cộng sổ**: +2,62pp của L1b (pool 60→120, vòng 4) tách thành bao nhiêu
phần **pha loãng ngành** và bao nhiêu phần **thêm tên rẻ**. Kỳ vọng nền khai trước:
**DSR và block-bootstrap sẽ vẫn trượt như L1b** — 12,5 năm / 48 kỳ rebal không đủ mẫu để tách
+2,6pp/năm khỏi nhiễu quỹ đạo ở mức 95%. Không có tiêu chí GO nào trong vòng này và **sẽ không có
verdict GO**; DSR/PBO/bootstrap được in ra để định cỡ độ tin cậy của PHÂN RÃ, không phải để duyệt
một chân. Không nắn thiết kế để có PASS.

Chính sách user ghi nhận 2026-09-09 (đổi cách đọc mọi kết quả sau này): **vị thế overweight ngân
hàng 49,1% trọng số / 67,5% OOS / đỉnh 93,3% KHÔNG PHẢI chủ ý** — nó là tác dụng phụ của việc định
nghĩa pool bằng THANH KHOẢN. ⇒ **giảm tỷ trọng ngân hàng là mục tiêu hợp lệ tự thân**, không cần
biện minh bằng CAGR. Hệ quả cho vòng này: một chân giảm ngân hàng mà ΔCAGR ≈ 0 vẫn là kết quả
**có giá trị**, không phải thất bại.

## 1. Câu hỏi chính, và cái gì phân biệt được (X) với (Y)

+2,62pp của L1b đến từ:
- **(X) PHA LOÃNG NGÀNH** — chỉ vì rổ có ít tên tài chính hơn (33,19% → 20,76% số tên), hay
- **(Y) THÊM TÊN RẺ** — vì trung bình 132 tên đã qua cổng rating≤3 nhưng chưa bao giờ được chấm
  điểm định giá nay được vào cạnh tranh?

Hai chân placebo là **hai nửa bù nhau của cùng một thiết kế 2×2**, trên hai trục:
`pool ∈ {60, 120}` × `số tên tài chính ép vào top-30 ∈ {số của ctrl, số của L1b}`.

| ô | pool | số tên tài chính | chân |
|---|---|---|---|
| (60, ctrl-count) | 60 | tự nhiên (≈33%) | **ctrl** (tái lập pin R3) |
| (120, L1b-count) | 120 | tự nhiên (≈21%) | **L1b** (tái lập vòng 4) |
| (60, **L1b**-count) | 60 | **ép** = L1b cùng kỳ | **P1** — pha loãng ngành THUẦN, pool không đổi |
| (120, **ctrl**-count) | 120 | **ép** = ctrl cùng kỳ | **P2** — tên mới, ngành trả về như cũ |

**Cộng sổ chốt trước** (`Δ` = ΔCAGR vs ctrl, pp):
```
TỔNG      = CAGR(L1b) − CAGR(ctrl)                     (= +2,62pp đã đo vòng 4)
ΔP1       = CAGR(P1)  − CAGR(ctrl)      -> hiệu ứng ĐẾM (pha loãng), ở pool nền
ΔP2       = CAGR(P2)  − CAGR(ctrl)      -> hiệu ứng POOL (tên mới), ở số đếm nền
tương tác = TỔNG − ΔP1 − ΔP2
```

**Luật đọc kết quả, chốt TRƯỚC khi thấy số** (không sửa sau):
- ΔP1 ≥ 0,60·TỔNG **và** ΔP2 ≤ 0,40·TỔNG ⇒ kết luận **(X) chiếm ưu thế**.
- ΔP2 ≥ 0,60·TỔNG **và** ΔP1 ≤ 0,40·TỔNG ⇒ kết luận **(Y) chiếm ưu thế**.
- ngược lại ⇒ **hỗn hợp**, và báo cáo tỷ lệ ΔP1:ΔP2:tương tác dưới dạng %TỔNG, không gán nhãn.
- |tương tác| > 0,50·TỔNG ⇒ nói thẳng: phân rã cộng tính **không mô tả được** hệ này, và mọi
  gán nhãn (X)/(Y) đều không có cơ sở — đó cũng là một kết luận hợp lệ.

## 2. Cơ chế: `BASKET_PLACEBO_FIN` làm ĐÚNG cái gì (đã ĐỌC CODE, không suy từ tên)

`custom_basket.py::_placebo_reorder` (thêm 07-14, job `Taylor_20260714_121717`), đọc nguyên văn:

```python
tgt = _pl_n.get(d)                       # số tên tài chính mục tiêu, tra theo NGÀY REBAL từ CSV
fin = [x for x in gated if route(x) in {BANK, INSURANCE, SECURITIES}]   # giữ thứ tự điểm
non = [x for x in gated if route(x) not in {...}]
k    = min(tgt, len(fin))
keep = <k phần tử NGẪU NHIÊN của fin>    # <-- rng seed = (SEED, ngày)
head = keep + non[: top_n - len(keep)]   # slot phi-tài-chính = tên TỐT NHẤT theo đúng selector
```

Ba điều phải ghi rõ vì cái tên không nói ra:
1. **Nó chọn tên tài chính NGẪU NHIÊN**, không phải giữ `k` tên tài chính điểm cao nhất. Delta của
   nó vì thế **trộn** hiệu ứng-đếm với hiệu ứng-suy-giảm-chất-lượng-trong-nhóm-tài-chính.
2. Slot phi-tài-chính **đúng** như dispatch mô tả: lấp bằng tên phi-tài-chính tốt nhất theo
   yieldcombo trong pool (`non` giữ thứ tự điểm).
3. `_pl_route` tra route bằng **khớp tuyệt đối `(ticker, src_q)`** trong `data/value_panel_2014.csv`,
   không có fallback as-of; tên không có dòng đúng quý bị coi là **phi-tài-chính** (fail-open).
   Khác quy ước `route_asof` (bisect) mà `analyze.py` vòng 4 dùng để ĐO. Xử lý: xem §3.

## 3. Hai thay đổi RESEARCH-ONLY trong bản copy `custom_basket.py` (mặc định OFF ⇒ byte-identical)

**(a) `BASKET_PLACEBO_MODE = "random" (mặc định, giữ nguyên semantics 07-14) | "top"`.**
`"top"` giữ `k` tên tài chính **điểm cao nhất** (`fin[:k]`, `gated` đã sắp theo điểm giảm dần) thay
vì ngẫu nhiên. Lý do tồn tại: phân rã vòng này chỉ được phép đổi **SỐ ĐẾM**. Bản ngẫu nhiên đổi cả
số đếm lẫn *danh tính*, nên ΔP của nó không phải hiệu ứng-đếm thuần. `"top"` **bảo toàn thứ hạng**:
nó cắt đúng các tên tài chính biên — chính là cái nới pool làm — và không làm gì khác.
⇒ **`"top"` là chân CHÍNH (P1d/P2d).** Bản `"random"` chạy làm **chân phụ** (P1r/P2r) để trả lời
câu hỏi tách biệt *"danh tính ngân hàng nào có quan trọng không"* — vòng 4 L3 đã đo là **không**
(+0,31pp, dưới sàn nhiễu), nên prior khai trước: **P1r ≈ P1d, P2r ≈ P2d**. Lệch lớn = phát hiện.

**(b) `BASKET_FINCOUNT_DUMP=<path>`** — ghi số tên tài chính trong top-30 mỗi kỳ rebal, dùng **ĐÚNG
quy ước route mà `_placebo_reorder` cưỡng chế** (khớp tuyệt đối `(ticker, src_q)`). CSV mục tiêu của
P1/P2 vì thế sinh ra từ chính thước đo sẽ cưỡng chế nó ⇒ mục tiêu và phép đo **không thể lệch nhau**.

Không đụng file production. `sel_engine.py` re-insert thư mục này lên `sys.path[0]` (bẫy vòng 2).

## 4. Sáu chân — N_trials khai thật

| chân | pool | placebo | mode | seed |
|---|---|---|---|---|
| `ctrl` | 60 | — | — | — |
| `L1b` | 120 | — | — | — |
| **`P1d`** | 60 | count = L1b | `top` | — |
| **`P2d`** | 120 | count = ctrl | `top` | — |
| `P1r1`/`P1r2` | 60 | count = L1b | `random` | 101 / 202 |
| `P2r1`/`P2r2` | 120 | count = ctrl | `random` | 101 / 202 |

**N_trials = 4** cấu hình treatment phân biệt (P1d, P2d, P1r, P2r). Hai seed của mỗi chân random là
**một** ước lượng — báo cáo **trung bình 2 seed** và cả 2 giá trị thô; **không** chọn seed đẹp,
**không** thêm seed sau khi thấy số. `ctrl` và `L1b` là tái lập, không tính là trial.
Không có chân nào ngoài 6 chân trên. Không sweep tham số, không quét thêm điểm pool.

## 5. Bảng BẮT BUỘC có trong báo cáo (dispatch §1-4)

1. **Kiểm chứng cơ chế** — `n_fin` trung bình/kỳ của từng chân. P1 phải **khớp từng kỳ** với L1b;
   P2 phải **khớp từng kỳ** với ctrl. In số kỳ khớp/48 và mọi kỳ lệch (lệch xảy ra khi
   `len(fin) < tgt`, tức pool không đủ tên tài chính — phải nêu, không giấu).
2. **%tên tài chính + %TRỌNG SỐ tài chính theo ngày** cho từng chân (trọng số tính lại bằng chính
   vòng lặp `build_pit`, self-check khớp `lvl` như Phần 0 vòng 4 — không ước lượng).
3. **ADV rổ trung vị + sức park 20%/ngày** cho TỪNG chân. Đây là biến quyết định khả thi vận hành:
   P1 giữ pool 60 nên **phải** giữ thanh khoản gần ctrl (~1.744B/ngày). Nếu P1 thu được phần lớn
   edge **mà không mất thanh khoản** → nêu bật, đó là kết quả vận hành lớn nhất của cả 5 vòng.
4. Per-year + per-window (LOYO), DSR vs SR_ctrl (N=4), PBO CSCV toàn họ, block bootstrap CI95
   (block 63 phiên = 1 quý, khớp chu kỳ rebal), Δw_equity, turnover.
5. Cộng sổ §1 tường minh + trả lời thẳng **(X)/(Y)/hỗn hợp bao nhiêu-bao nhiêu**.
6. Nếu (X) chiếm ưu thế: đề xuất **dạng luật trần ngành tường minh trong pool 60** (giữ nguyên
   thanh khoản) để Mike/user cân nhắc vòng sau — **chỉ đề xuất, KHÔNG wire, KHÔNG backtest thêm
   trong vòng này** (backtest luật đó là một tiền đăng ký MỚI).

## 6. Điều kiện tiên quyết — kiểm TRƯỚC khi tin bất kỳ số nào

md5 CSV của `ctrl` phải bằng **`7d053e6201c9d107685ff4d1dd9d2d2a`** (pin R3). Lệch = harness bẩn,
**DỪNG**, không đọc số chân nào. `self-check 0 VND` (BAL + LAG) trên **mọi** chân.
`fincount` dump của ctrl/L1b sinh từ `build_pit` phải **trùng từng dòng** với dump của chính lần
chạy NAV đầy đủ tương ứng (nếu không: mục tiêu placebo không đại diện cho chân nó khớp tới).

Ràng buộc chung: `universe_pit` · `LAG_ADV_BASIS=price` · `BQ_CACHE_THREADS=1` ·
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate` · IS 2014-19 / OOS 2020+ ·
cấm cột forward-looking (`profit_*`, `_center_*`, `PC1W..PC2M`, `Open_1D`, `O*`, `Pattern_*`) ·
không sửa file production (`custom_basket.py` gốc, `filter.json`, `papertrade_daily.sh`,
`pt_v23_audit_2014.py`, `simulate_holistic_nav.py`, `trading_rules.json`) ·
`AUDIT_EXP_TAG` riêng trên MỌI chân kể cả control (§8 coding_guidelines).

## 7. Ghi trước điều sẽ KHÔNG làm
- Không wire gì vào production, kể cả nếu một chân trông đẹp. Vòng này không có đường tới wire.
- Không đổi `N_MEMBERS=30`, `name_cap=0,10`, `gate_rating=3`, `rebal=q2m5`, mức park 80%.
- Không thêm chân/seed sau khi thấy số. Không tách/gộp chân để cứu một kết quả.
- Không quét thêm điểm pool (đó là tuning, sẽ chết ở DSR y hệt vòng 4).
- Không backtest luật trần ngành đề xuất ở §5.6 trong vòng này.
