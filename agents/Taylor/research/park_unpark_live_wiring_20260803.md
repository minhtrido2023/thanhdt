# Lớp dịch PARK → cash cho live: band breach KHÔNG phải bug, thiếu 2 đường BÁN PARK mới là

**Job** `Taylor_20260803_171515` (nối tiếp `Taylor_20260803_165225`) · **Ngày** 2026-08-03/04 · **Tác giả** Taylor
**Trạng thái**: A xong (verify code thật, có bổ sung quan trọng) · B thiết kế xong · C **đã sửa harness, đang chạy lại**
**KHÔNG sửa file production nào.** Ablation dùng BẢN SAO engine trong `exp_park_jit_20260803/`.
**quant-skeptic BẮT BUỘC trước khi wire — chưa chạy.**

---

## 0. ĐÍNH CHÍNH VÒNG TRƯỚC — ablation v1 là NO-OP, số của nó vô hiệu

Vòng `Taylor_20260803_165225` chạy 3 chân qua `run_jit.sh`, dùng `PYTHONPATH` để nạp bản sao engine.
**Cơ chế đó không hoạt động**: `pt_v23_audit_2014.py:42` gọi `sys.path.insert(0, WORKDIR)` **trước**
`import simulate_holistic_nav` (dòng 45) ⇒ thư mục production luôn thắng `PYTHONPATH`. Cả 3 chân
đều chạy **code production**, biến `PARK_JIT` chưa từng được đọc.

Bằng chứng cứng — 3 CSV output **giống hệt nhau từng byte**:

```
7d053e6201c9d107685ff4d1dd9d2d2a  ..._exp_jit_A_control_univpit.csv
7d053e6201c9d107685ff4d1dd9d2d2a  ..._exp_jit_B_off_univpit.csv
7d053e6201c9d107685ff4d1dd9d2d2a  ..._exp_jit_C_skip_univpit.csv
```

Điểm sáng duy nhất: chân A (= production) **tái lập chính xác số pin 08-03** — `Final NAV 1.178,01B ·
CAGR 28,86% · Sharpe 1,90 · MaxDD −17,8% · Calmar 1,62`, selfcheck cash-flow **0 VND** cả 2 sổ. Nên
môi trường + tham số là đúng; chỉ cơ chế nạp module sai.

**Sửa**: `exp_park_jit_20260803/run_leg.py` — pre-seed `sys.modules["simulate_holistic_nav"]` bằng
`importlib` trước khi `runpy` chạy `pt_v23_audit_2014.py`. Miễn nhiễm với thứ tự `sys.path`. Có 2
`assert` + 2 dòng in bắt buộc ở đầu log (`[ABLATION] shn = <đường dẫn bản sao>` / `PARK_JIT = <leg>`);
không thấy 2 dòng đó ⇒ kết quả phải vứt.

> Bài học cùng họ §14/§19 coding_guidelines: "script chạy xong, exit 0" **không** đồng nghĩa "cơ chế
> đã có tác dụng". Gate rẻ nhất bắt được lỗi này là `md5sum` output các chân — nếu 2 chân khác cấu
> hình cho ra file giống hệt, ablation đã chết. Nên là bước bắt buộc của mọi ablation sau này.

---

## A. Double-check phân tích của Mike — 3 đúng, 1 BÁC BỎ, 1 BỔ SUNG LỚN

### A1. Allocator band ±10pp là rule THẬT — ĐÚNG, nhưng nó không sinh lệnh

`pt_v22_dt5g.py:765-808` đúng như mô tả:

| Tham số | Giá trị | Dòng |
|---|---|---|
| `ALLOC_REBAL_BAND` | 0.10 | 116 |
| `ALLOC_REBAL_TC` | 0.001 (trên vốn di chuyển) | 109 |
| `w_lag_target` | 0.65 nếu `lag_edge_health.mean12 >= 4.0%`, else 0.50 | 782-788 |
| `STATE_LAG_WEIGHT` | CRISIS=0.50, BEAR=0.00 | 788 |

**Chi tiết đổi hẳn kết luận:** allocator nằm ở bước `[8] Building combined logs` — **lớp KẾ TOÁN VỐN
HẬU KỲ**. Hai sổ `nav_bal`/`nav_lag` đã mô phỏng **ĐỘC LẬP, XONG XUÔI** trước đó (mỗi sổ 25B). Vòng
lặp allocator chỉ nhân 2 **số vô hướng** `cb`/`cl` với suất sinh lời ngày của từng sổ, và khi lệch
band thì gán lại `cl = w_tgt × P` — rồi scale ledger bằng hệ số gắn kết `fb = cap_b/navb_c`,
`fl = cap_l/navl_c`. Nó **không feedback vào sizing vị thế bên trong mỗi sổ**.

> Allocator **không sinh ra một lệnh nào**. Không mua, không bán, không trim PARK — kể cả trong backtest.

⇒ **Không tồn tại "lớp dịch band breach → lệnh trim PARK" để đem sang live.** Đi tìm nó là đi tìm
thứ không có. Cơ chế thật cấp vốn nằm chỗ khác (A5/A6).

### A2. golive đọc lại từ sổ mô phỏng — ĐÚNG

`deploy_golive_dt5g_v4/golive_recommend_v23.py:748-759`:

```python
pl = pd.read_csv(os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv"), ...)
last = pl.iloc[-1]
lag_mv = float(last["SECOND_cash"]) + float(last["SECOND_stocks"]) + float(last["SECOND_etf"])
w_cur = lag_mv / float(last["nav"])
band_breach = (w_cur is not None) and (abs(w_cur - w_tgt) > ALLOC_BAND)
```

`w_cur` đến từ sổ mô phỏng ~48 tỷ, **không** tính lại từ NAV thật. `data/golive_v23_status.json`
hôm nay xác nhận: `w_lag_current=0.495`, `alloc_note="as of 2026-07-31"` (trong khi `date=2026-08-03`).

### A3. "Smoking gun" `plan_ZaloPay_2026-07-31` — **BÁC BỎ**

Chạy lại đúng công thức trên CSV tại 2026-07-31:

```
w_cur = (SECOND_cash 5,55B + stocks 5,41B + etf 12,98B) / nav = 0,495
|0,495 − 0,50| = 0,5pp  <  band 10pp  →  band_breach = False   ✓ ĐÚNG
```

`band_breach: false` **không phải field kế thừa sai** — nó đúng với sổ của nó. Con số **30,5%** của
DollarBill và **49,5%** của sim **khác mẫu số**, không so được:

| | Tử số sleeve LAG | 07-31 |
|---|---|---|
| Sim (`w_cur`) | cash + cổ phiếu + **ETF park** | 49,5% |
| DollarBill | **chỉ vị thế cổ phiếu** | 30,5% |

Phần chênh chính là PARK. Nghịch lý "19,5pp > band mà vẫn false" tan biến khi so cùng mẫu số.
**Không có bug ở đây.** (Vẫn còn một vấn đề THẬT nhưng khác loại: `w_cur` là số của sổ mô phỏng
48 tỷ, trễ 3 ngày — nó không mô tả account thật. Đó là *sai phạm vi*, không phải *sai giá trị*.)

### A4. Không có lệnh rút vốn khỏi PARK trong live — ĐÚNG

3 `play_type` trong recs: `LAG_HI`, `LAG_LO`, `CUSTOM30V_8L`. `CUSTOM30V_8L` là tín hiệu **xoay vòng
mã trong rổ 30** (giữ nguyên tổng vốn PARK), không phải exit. `PARK_EXIT` không tồn tại ở bất kỳ đâu
trong code ⇒ check của DollarBill luôn trả rỗng một cách máy móc. ĐÚNG như Mike mô tả.

### A5. 🔴 BỔ SUNG — engine có **BA** đường PARK, live chỉ có **MỘT**, và nó là đường MUA

Đây là phát hiện lớn nhất, và nó **mạnh hơn** cách diễn đạt ở vòng trước ("thiếu JIT"). Trong
`simulate_holistic_nav.py`, PARK có đúng 3 đường, mỗi đường 1 `reason_tag`:

| # | `reason_tag` | Dòng | Chiều | Kích hoạt | Có ở LIVE? |
|---|---|---|---|---|---|
| 1 | `PREFILL_STATE_REBAL` | 899-980 | **BÁN** | **Mỗi phiên, VÔ ĐIỀU KIỆN**: `park_mv > target + 0,5%×pool` | ❌ KHÔNG |
| 2 | `JIT_FOR_BA_BUY` | 1139-1199 | **BÁN** | Mỗi lệnh mua thiếu tiền: `cash < target_value × 0,99` | ❌ KHÔNG |
| 3 | `POST_FILL_SWEEP` | 1358-1420 | **MUA** | Cash thừa sau khi fill deal | ⚠️ chỉ dạng **văn xuôi** |

Đường 1 (`PREFILL_STATE_REBAL`) là thứ vòng trước bỏ sót và nó quan trọng nhất: comment trong code
gọi nó là "SELL-only prefill", chạy **hằng ngày**, **không phụ thuộc bất kỳ tín hiệu mua nào**:

```python
target_etf = total_cash_pool * etf_frac          # pool = cash + park
delta      = target_etf - current_etf_value
if delta < -total_cash_pool * 0.005 and px_ok:   # park VƯỢT target quá 0,5% pool
    sell_vnd_target = min(-delta, _etf_day_cap(today))   # FIFO bán, trần thanh khoản ngày
```

Đường 3 ở live chỉ tồn tại dưới dạng **câu chữ trong báo cáo**, không phải phép tính:
`golive_recommend_v23.py:1124` in ra `"- **Parking (cả 2 book):** park **70%** cash nhàn rỗi vào rổ
custom30V ..."` kèm danh sách mã. Không có `target_park`, không có `delta`, không có lệnh.

> **Phát biểu gọn nhất về lỗ hổng:** engine coi PARK là **bể chứa hai chiều** của tiền nhàn rỗi;
> live chỉ triển khai **chiều vào**, và chỉ bằng văn xuôi. Tiền vào PARK rồi không có đường ra ⇒
> **hiệu ứng bánh cóc (ratchet)**. Không cần giả thuyết nào phức tạp hơn để giải thích 3 tuần HOLD ALL.

### A6. 🔴 SÀN TIỀN MẶT 30% — đo trên số DNSE thật hôm nay

Vì `etf_frac` là **TRẦN** cho tổng PARK tính trên pool (cash + park), hệ quả cơ học là **30% pool
luôn phải là tiền mặt** ở NEUTRAL. Đo trên `dnse_raw_2026-08-03.jsonl` (bản ghi 19:10 ICT, lọc
`account_no` theo §12), PARK = 30 mã `CUSTOM30V_8L` trong recs 08-03, trừ 5 mã rổ CAPIT
(NCT/PVT/SAB/SIP/VNM) để tránh đếm trùng:

| | PARK (trừ CAPIT) | cash | pool | target park 70% | **PARK VƯỢT** | cash share (cần 30%) |
|---|---|---|---|---|---|---|
| **SpaceX** | 642,46tr | 14,60tr | 657,05tr | 459,94tr | **+182,52tr** | **2,2%** |
| SpaceX (dùng `availableCash`) | 642,46tr | 4,82tr | 647,28tr | 453,09tr | **+189,36tr** | **0,7%** |
| **ZaloPay** (trừ cả DGC excluded) | 297,63tr | 12,27tr | 309,90tr | 216,93tr | **+80,70tr** | **4,0%** |

Đối chiếu nhu cầu: `plan_SpaceX_2026-08-04.json` → `deferred_total_with_fee_vnd = 171.096.626`
(TV2 76,04tr + APF 95,06tr), `available_cash_vnd = 4.821.143`, `orders = 0`, HOLD ALL. Lý do ghi
nguyên văn: *"Chờ user nạp vốn mới → re-dispatch kích hoạt."*

> **182,5tr PARK vượt trần vs 171,1tr hai lệnh cần.** Nếu live chỉ đơn thuần **tuân thủ đúng tỷ lệ
> parking 70/30 mà chính nó đã backtest**, nó đã có đủ tiền cho cả 2 lệnh — **trước khi** cần đến
> JIT-unpark, và **không cần user nạp thêm một đồng nào**.

Đây là điểm cốt lõi: **không phải "thêm rule mới", mà là "live đang vi phạm một rule đã có"**.

⚠️ Cảnh báo về độ chắc của con số 642,46tr: xem A7.

### A7. 🔴 BLOCKER THI CÔNG — live KHÔNG có sổ quy vị thế về book

Bảng A6 phải quy PARK bằng **suy luận theo tên mã** (mã có trong rổ custom30V hôm nay ⇒ coi là PARK),
vì hệ thống live **không tag book cho từng lô**. Cách này sai được, và đã sai:

- `plan_SpaceX_2026-08-04.json` → `positions_snapshot_eod_20260803.holdings[].book_note` chính nó
  ghi **`"LAG/PARK"`** cho VPB — DollarBill cũng không phân định được.
- PVT/VNM/SAB/SIP/NCT nằm **đồng thời** trong rổ CAPIT và (một phần) rổ park lịch sử.
- Rổ custom30V **đổi theo quý** (`park_rebal_date = 2026-05-05`): một mã bị loại khỏi rổ nhưng
  vẫn đang giữ sẽ **biến mất khỏi PARK** theo cách quy này, dù tiền vẫn nằm đó.

⇒ **L1/L2 không thể thi công chính xác trước khi có tag book per-lot.** Việc phải làm trước
(nhỏ, cơ học, không đụng chiến lược): ghi `book`/`play_type` vào journal **tại thời điểm fill**
(plan đã có sẵn field `book` + `play_type` trên từng order — chỉ cần chuyển tiếp xuống journal),
rồi dựng vị thế theo lô FIFO từ journal đó. Đây là **điều kiện tiên quyết**, không phải việc phụ.

---

## B. Thiết kế lớp dịch

Nguyên tắc: **không chế tham số mới**. Mọi con số dưới đây đã tồn tại trong engine đã backtest.

### B0. Việc phải làm TRƯỚC (P0) — tag book per-lot

Theo A7. Không có nó, mọi phép tính `park_mv_live` đều là ước lượng theo tên mã.
Thành phẩm: một hàm `park_holdings(account)` trả về danh sách lô `(ticker, qty, entry_date, cost)`
được gắn nhãn PARK **từ journal**, không từ suy luận tên.

### B1. Hai lớp TÁCH BIỆT, ưu tiên L1 trước L2

Đề bài gốc ("band breach → trim PARK") gộp 2 việc; A1/A3 cho thấy band **không phải** trigger đúng.
Thiết kế đúng gồm 2 lớp độc lập, **cả hai đều là PORT của cơ chế đã có trong engine**, không phải rule mới:

| | Lớp | Port từ | Trigger | Ưu tiên |
|---|---|---|---|---|
| **L1** | Park-target compliance | `PREFILL_STATE_REBAL` | `park_mv > target + 0,5%×pool` — **hằng ngày, vô điều kiện** | **1** |
| **L2** | JIT unpark | `JIT_FOR_BA_BUY` | Có lệnh mua mà `cash < target_value × 0,99` | 2 |

L1 giải quyết 182,5tr/171,1tr của case hiện tại ⇒ **L1 đủ để đóng case, rủi ro thấp hơn hẳn** (chỉ
đưa tỷ lệ về đúng thiết kế, không phụ thuộc bất kỳ tín hiệu mua nào). L2 là bảo hiểm cho trường hợp
lệnh mua lớn hơn phần dư 30%.

### B2. L1 — Park-target compliance (khuyến nghị wire TRƯỚC)

```
pool        = cash_live + park_mv_live            # DNSE, KHÔNG BQ (§6); park_mv_live từ B0
etf_frac    = ETF_PARK[state_today]               # NEUTRAL 0.70 — hằng số đã pin, dùng chung với golive
target_park = pool × etf_frac
delta       = target_park − park_mv_live
if delta < −pool × 0.005:                         # ngưỡng 0,005 COPY từ engine dòng 918
    trim = min(−delta, etf_day_cap_live)          # trần thanh khoản, y hệt engine dòng 921
    → sinh lệnh BÁN PARK tổng giá trị `trim`
```

Không có tham số nào ở đây do tôi đặt ra: `0.70` từ `PARK_STATES`, `0.005` và `_etf_day_cap` từ
`simulate_holistic_nav.py` khối 4c.

### B3. L2 — JIT unpark, bám sát `JIT_FOR_BA_BUY`

```
for order in pending_buys:                        # theo thứ tự engine duyệt lệnh
    if cash < order.target_value × 0.99:
        needed = min(order.target_value − max(cash,0), etf_day_cap_remaining)
        → bán PARK FIFO đúng `needed`; cash += needed × (1 − friction)
```

`× 0.99`, `min(...)`, FIFO, friction — tất cả là hằng số đã có trong engine.
Fallback khi vẫn không đủ: engine **co lệnh** về `(cash + margin_room) × 0.95` (dòng 1207-1209),
bỏ hẳn nếu `< 1tr`. Live hiện nay **defer nguyên lệnh** — đây là chân C của ablation.

### B4. Trả lời 3 câu hỏi Mike đặt

**Thứ tự trim mã nào trước?** → **FIFO theo lô (`entry_date`), đúng như engine.** Mọi lựa chọn "khôn
hơn" (weight cao nhất trước, DD kém nhất trước) đều là **tham số mới chưa backtest** — sẽ làm live
lệch khỏi số đã pin, đúng thứ đề bài yêu cầu tránh.
⚠️ Khác biệt hiện vật: engine mô phỏng PARK là **một** rổ chia lô; live PARK là **30 mã riêng lẻ**.
Tương đương gần nhất với "bán một phần rổ" là **trim pro-rata theo trọng số hiện tại**, **không** bán
sạch vài mã (bán sạch = đổi cấu trúc rổ = đổi hẳn thứ đã backtest). Trong mỗi mã thì FIFO theo lô.

**Trần trim mỗi phiên?** → **`_etf_day_cap(today)` đã có sẵn trong engine**, không đặt trần %/phiên
mới. Đây chính là cơ chế chống "bán sạch PARK trong 1 phiên" mà backtest đã tính vào kết quả.

**Điều kiện phụ (chỉ trim khi có LAG candidate sạch)?**
- **L2**: có sẵn theo định nghĩa — chỉ chạy khi có lệnh mua thật.
- **L1**: **KHÔNG thêm điều kiện phụ.** Engine sweep vô điều kiện theo state. Thêm gate "chỉ trim khi
  có candidate sạch" là chế tham số mới **và tái tạo đúng lỗi hiện tại ở chiều ngược lại**: giữ PARK
  quá mức ⇒ không có dry powder khi cơ hội đến (LAG/PEAD có cửa sổ vào lệnh cố định — lỡ là mất hẳn,
  không phải hoãn). Tiền mặt 30% **là** thiết kế, không phải lãng phí.
- Mọi lệnh mua sinh ra vẫn đi qua gate LIVE đang có (DD, 8L rating≤3, `cap_lag_orders` %ADV,
  `filter_lag_rating_orders`) — **L1/L2 chỉ cấp vốn, không tạo quyền mua.**

### B5. Ranh giới an toàn

- Cash/giá đọc **từ DNSE, không từ BQ** (§6 — same-day BQ là giá hôm qua).
- **Dùng `availableCash`, không dùng `totalCash`**: hôm nay `totalCash` 14,60tr gồm 9,78tr
  `cashDividendReceiving` chưa về ⇒ tính pool bằng `totalCash` sẽ ước tính thừa sức mua.
- L1/L2 chỉ **đề xuất lệnh vào plan**; user vẫn duyệt, Mafee vẫn plan-bound.
- `excluded_tickers` (DGC/ZaloPay) phải được tôn trọng ở cả 2 lớp — DGC nằm trong rổ custom30V
  nhưng **không được** trim.
- Vị thế CAPIT `stop_exempt`/`slot_exempt` **không** phải PARK — cấm trim (exit CAPIT do người quyết định).
- Sizing theo `active_nav`, không phải NAV tổng (§7).

---

## C. Ablation — ĐÃ CHẠY XONG (harness v2), và kết quả **không ủng hộ** cách kể chuyện "mất tiền"

Đo giá của việc thiếu đường L2 (`JIT_FOR_BA_BUY`), trên bản sao engine (production không đổi).
Lệnh: `exp_park_jit_20260803/run_jit2.sh <tag> <on|off|skip>`. `AUDIT_END=2026-06-19`, `NAV=50B`,
`universe_pit`, `BQ_LOCAL_CACHE=bq_cache_asof20260729_postrestate`, threads=1.

### C1. Hai gate tự kiểm — **PASS cả hai**

- Chân A tái lập **chính xác** số pin 08-03: `Final NAV 1.178,01B · CAGR 28,86% · Sharpe 1,90 ·
  MaxDD −17,8% · Calmar 1,62`; và CSV của nó **md5 `7d053e6201c9…` trùng khít** với CSV do lần chạy
  production sinh ra ⇒ đường nạp module mới **trung thành tuyệt đối**.
- 3 CSV **md5 KHÁC nhau** (`7d053e62…` / `fe06277c…` / `133a4c0a…`) ⇒ không còn no-op như §0.
- `selfcheck` cash-flow + NAV identity = **0 VND** cả 2 sổ, ở cả 3 chân.

### C2. Kết quả

| Chân | CAGR | Sharpe | MaxDD | Calmar | Final NAV | buy bị bỏ |
|---|---|---|---|---|---|---|
| **A** control (`on`) | **28,86%** | 1,90 | −17,8% | 1,62 | 1.178,01B | 0 |
| **B** off (co lệnh) | 28,42% | 1,90 | −17,7% | 1,60 | 1.129,07B | 0 |
| **C** skip (= LIVE) | 28,08% | 1,88 | −17,9% | 1,57 | 1.092,34B | **8.995** |

`A − C` toàn kỳ = **+0,78pp CAGR**, +0,02 Sharpe, +0,05 Calmar. 8.995 lượt mua bị bỏ trong 12,46 năm
⇒ JIT-unpark **không phải sự kiện hiếm**, nó là đường cấp vốn thường trực.

### C3. ⚠️ Nhưng edge đó **RỚT OOS và do một năm gánh** — không được trích như "lợi ích"

| | IS 2014-19 | OOS 2020-26 | Full |
|---|---|---|---|
| A control | 27,04% | 30,15% | 28,86% |
| C skip (live) | 25,43% | **30,29%** | 28,08% |
| **A − C** | **+1,61pp** | **−0,14pp** | +0,78pp |

- **OOS âm.** Theo chuẩn của đội (`kb/KNOWLEDGE.md` §Quy chuẩn 1: "edge rớt OOS = loại"), +0,78pp
  **không đủ tư cách** làm luận cứ deploy.
- **Per-year LOO**: bỏ riêng **2023** ⇒ chênh lệch về **+0,00pp**. Một năm gánh trọn toàn bộ edge —
  đúng dạng "reshuffle luck" mà `kb/KNOWLEDGE.md` §8 cảnh báo.
- C thắng A ở **6/13 năm** (2016, 2017, 2019, 2020, 2022, 2025), biên độ hai chiều lớn (±8pp).
- Rủi ro gần như không đổi (Sharpe 1,90 vs 1,88; MaxDD −17,8% vs −17,9%).

**Diễn giải đúng:** thiếu JIT-unpark **không chứng minh được là làm mất tiền**. Nó làm **đường đi
của live khác đường đã mô phỏng** — mỗi năm lệch ±8pp theo cả hai chiều. Đây là **lỗi trung thực
mô hình (fidelity)**, không phải "bỏ lỡ alpha đo được".

### C4. Phạm vi — cái C **không** đo

Ablation này chỉ tắt đường 2. Đường 1 (`PREFILL_STATE_REBAL`, khối 4c) **vẫn chạy** ở cả 3 chân ⇒
ngay cả chân C vẫn tự động trim PARK về đúng 70% mỗi phiên — thứ **live không hề làm**. Do đó:

> **A − C là CẬN DƯỚI của khoảng cách live-vs-backtest, không phải toàn bộ.**

Muốn định lượng riêng L1 phải thêm chân thứ 4 (tắt khối 4c). **CHƯA LÀM — cần thêm 1 vòng.**
Dự đoán trước khi đo (ghi lại để sau đối chiếu): tắt 4c sẽ tệ hơn C rõ rệt, vì nó chặn nốt đường
thoát cuối cùng của tiền khỏi PARK.

---

## Kết luận cho người quyết định

1. **`band_breach` không hỏng** — đừng sửa nó. Field đúng với sổ mô phỏng của nó (dù sổ đó không mô
   tả account thật — vấn đề phạm vi, không phải giá trị).
2. **Allocator không sinh lệnh, kể cả trong backtest.** "Lớp dịch band → trim PARK" là thứ không tồn tại.
3. **Lỗ hổng thật: engine có 3 đường PARK (2 bán, 1 mua); live chỉ có đường MUA, và chỉ là văn xuôi.**
   Tiền vào PARK không có đường ra — bánh cóc.
4. **Luận cứ để vá là TUÂN THỦ SPEC, KHÔNG PHẢI ALPHA.** Ablation C cho +0,78pp toàn kỳ nhưng
   **OOS −0,14pp** và **LOO-2023 = +0,00pp** ⇒ **cấm trích +0,78pp như lợi ích của việc wire**.
   Lý do đúng để wire: (a) live đang **vi phạm** rule parking 70/30 mà chính nó đã backtest —
   PARK vượt trần **182,5tr** ở SpaceX trong khi 2 lệnh defer cần **171,1tr**; (b) mọi số đã pin
   (28,86%) được sinh trên một đường thi hành mà live không có ⇒ số pin hiện **không mô tả** live.
5. **Ưu tiên L1 trước L2**: L1 đủ đóng case hiện tại, không phụ thuộc tín hiệu mua, và là port
   nguyên trạng của `PREFILL_STATE_REBAL` (0 tham số mới).
6. **Điều kiện tiên quyết (P0): tag book per-lot.** Không có nó, `park_mv_live` chỉ là ước lượng
   theo tên mã, và chính plan hôm nay đã ghi `"LAG/PARK"` vì không phân định được.
7. **Chưa wire gì.** quant-skeptic bắt buộc trước mọi thay đổi vào `golive_recommend_v23.py` hay
   plan generation. Việc còn nợ: chân thứ 4 (tắt 4c) để định lượng riêng L1.

---
---

# PHỤ LỤC (job `Taylor_20260803_180602`) — 3 việc còn nợ sau quant-skeptic CONFIRMED

Verdict vòng 1: **CONFIRMED (confidence high)**, nhưng **1/7 phép thử FAIL** (`capacity_adv_realism`)
+ 2 việc tự thân báo cáo đã nêu. Phụ lục này làm cả 3. **Vẫn KHÔNG sửa file production nào.**

---

## D. VIỆC 1 — Vá lỗ hổng capacity (`capacity_adv_realism`)

Script: `exp_park_jit_20260803/capacity_check.py` (chỉ ĐỌC) · số liệu `capacity_check_out.csv` ·
asof **2026-08-03**, rổ custom30V `rebal_date=2026-05-05` (30 mã).

### D0. ĐÍNH CHÍNH tiền đề của killer_objection — nhưng kết luận của nó VẪN ĐÚNG

quant-skeptic viết: *"`_etf_day_cap()` hiệu chỉnh theo ADV của ETF E1VFVN30, KHÔNG phải ADV từng mã
custom30V"*. **Vế đầu SAI với cấu hình production.** Run pin dùng `ETF_LIQ=custompitg`, và ở nhánh
`custom*` (`pt_v23_audit_2014.py:907-925`) phương tiện park **chính là rổ custom30V tự dựng**, không
phải E1VFVN30. `etf_adv_lookup` = `custom_basket.build_pit()`'s `adv_dict`, mà `custom_basket.py:1184-1206`
định nghĩa:

```
adv_t = trung bình trượt 60 phiên của  Σ_i (COALESCE(Price,Close)_i,t × Volume_i,t)
```

⇒ ADV **tổng của chính 30 mã đó**, không phải ADV của một ETF khác. Analogy sát hơn nhiều so với
mức quant-skeptic giả định.

**NHƯNG vế sau — "không phải ADV TỪNG MÃ" — đúng nguyên vẹn, và đó mới là chỗ chết:** trần là một
con số **TỔNG**. Nó không biết gì về phân bố. Đo cụ thể:

| | Trần/ngưỡng | Nguồn |
|---|---|---|
| Trần TỔNG của engine `_etf_day_cap` | **1.337,0 tỷ/phiên** (=20% × ADV rổ 6.684,9 tỷ) | `ETF_LIQ_PCT` |
| Trim tổng an toàn tối đa cho MỌI mã (trọng số LIVE, SpaceX) | **120,8 tỷ/phiên** (mã ràng buộc **LPB**) | `LAG_ADV_PCT`×share |
| — nt — (ZaloPay) | **135,0 tỷ/phiên** (mã ràng buộc **BID**) | — nt — |
| — nt — (trọng số MỤC TIÊU của rổ) | **156,2 tỷ/phiên** (mã ràng buộc **BID**) | — nt — |

> **Trần tổng của engine LỎNG HƠN ràng buộc per-name 8,6–11,1×.** Tái dùng nguyên `_etf_day_cap()`
> làm trần duy nhất — đúng như B2/B3 đề xuất — là **sai về mặt cấu trúc**: nó cho phép một phiên trim
> gấp ~10 lần mức mà chính gate live `cap_lag_orders` đang cấm cho book LAG. **killer_objection đứng vững.**

### D1. Đo thực tế hôm nay — không mã nào vượt, dư địa 638–1.585×

Kịch bản: trim pro-rata theo **trọng số live hiện tại** (B4) để đưa PARK về đúng 70% pool.

| | park_mv | cash (`availableCash`) | pool | target 70% | **cần trim** | max %ADV per-name | vượt trần live |
|---|---|---|---|---|---|---|---|
| **SpaceX** | 642,5tr | 4,8tr | 647,3tr | 453,1tr | **189,4tr** | **0,016%** (LPB) | **0/15** |
| **ZaloPay** | 297,6tr | 5,8tr | 303,4tr | 212,4tr | **85,2tr** | 0,006% (BID/LPB) | **0/9** |

Trần live per-account = `LAG_ADV_PCT × ADV × share` = **20% × ADV × 0,5 = 10% ADV** (share=1/2 vì 2
account live — `trading_bot/plan.py:450-465`). Mã "căng" nhất là **LPB** ở SpaceX: bán 14,06tr trên
ADV 89,68 tỷ = **0,016%**, trần cho phép 8.967,9tr ⇒ **dư địa 638×**.

Kịch bản áp lực (bán SẠCH toàn bộ PARK trong 1 phiên — cận trên lý thuyết, không phải đề xuất):
SpaceX mã nặng nhất LPB = **0,053% ADV**; ZaloPay BID = **0,022% ADV**. Vẫn dưới trần ~190×.

> **Kết luận đo lường:** ở quy mô NAV hiện tại, ràng buộc per-name **không binding, cách xa 2–3 bậc
> độ lớn**. Rổ custom30V toàn ngân hàng/blue-chip (ADV 89–679 tỷ/mã) trong khi lượng cần trim là
> hàng chục triệu. Đây là lý do **thực tế** để không lo — nhưng nó **không** biện minh cho việc bỏ
> trần per-name, vì con số 638× là **hệ quả của quy mô hiện tại**, không phải của thiết kế.

### D2. Sửa thiết kế — thêm trần PER-NAME, KHÔNG chế tham số mới

Thay `min(−delta, etf_day_cap_live)` ở B2 bằng trần **hai tầng**, tầng thứ 2 tái dùng đúng hằng số
và đúng công thức của gate live đã có tiền lệ (`cap_lag_orders`, live từ 2026-07-22, fail-closed):

```
trim_total = min(−delta, _etf_day_cap_live())                 # tầng 1: trần TỔNG (engine, giữ nguyên)
for mỗi mã i trong rổ PARK:
    sell_i = w_live_i × trim_total                            # pro-rata theo trọng số hiện tại (B4)
    cap_i  = LAG_ADV_PCT × adv_vnd(i) × share                 # tầng 2: TRẦN RIÊNG, = gate LAG live
    sell_i = min(sell_i, cap_i)                               # phần dư CHUYỂN SANG PHIÊN SAU
```

- `LAG_ADV_PCT = 0.20`, `share = 1/n_live_accounts`, `adv_vnd()` = `Volume_3M_P50 × COALESCE(Price,Close)`
  — **cả ba đã tồn tại và đang chạy LIVE**, không phải tham số mới. Cùng cơ sở giá `Price` sau fix 08-02.
- **Phần bị cắt KHÔNG được phân bổ lại sang mã khác** — phân bổ lại sẽ làm lệch trọng số rổ (= đổi
  thứ đã backtest, đúng thứ B4 cấm). Nó **carry-over sang phiên sau**, y hệt ngôn ngữ của
  `cap_lag_orders` (*"phần dư mua tiếp phiên sau"*).
- **Fail-closed**: không đọc được ADV / ADV cũ > `LAG_ADV_MAX_STALE_DAYS` (30) / ADV ≤ 0 ⇒ **KHÔNG
  trim mã đó** phiên này. Sao chép nguyên hành vi `_block()` của `cap_lag_orders`.
- Hệ quả đo được hôm nay: tầng 2 **không cắt gì** (0/24 mã chạm trần) ⇒ hành vi giống hệt B2 nguyên
  bản. Nó là **bảo hiểm cấu trúc cho tương lai** (NAV lớn hơn, hoặc rổ đổi sang mã mỏng hơn sau rebal
  quý), chi phí bằng 0 ở hiện tại.

### D3. Hai khác biệt định nghĩa PHẢI giữ tách bạch (không được trộn)

| | Công thức | Dùng ở đâu |
|---|---|---|
| ADV **rổ** (engine) | trung bình trượt 60 phiên của **Σ Price×Volume** (giá trị giao dịch THẬT) | trần TỔNG `_etf_day_cap` |
| ADV **mã** (live gate) | **Volume_3M_P50 × COALESCE(Price,Close)** (trung vị 3 tháng) | trần PER-NAME `cap_lag_orders` |

Hai con số **không cùng đơn vị khái niệm**: Σ ADV per-name = 5.374,5 tỷ vs ADV rổ engine = 6.684,9 tỷ
(**chênh 24%** — trung vị 3M luôn thấp hơn trung bình 60 phiên trong thị trường đang sôi động). Script
tính cả hai riêng rẽ và **không bao giờ chia số này cho số kia**. Ai wire sau này phải giữ đúng ranh
giới đó — trộn hai định nghĩa là cách rẻ nhất để tự tạo ra một trần sai 24%.

### D4. Lỗi tôi tự bắt được khi chạy — ghi lại vì nó suýt vào báo cáo

Lần chạy đầu cho `park_mv` SpaceX = **1.150,0tr**, lệch hẳn so với 642,46tr của §A6. Nguyên nhân:
tôi đọc `accumulateQuantity` của bản ghi `positions` — đó là **tổng đã mua tích luỹ**, gồm cả phần
đã bán (ACB: `accumulateQuantity=1800`, `openQuantity=1500`, `closedQuantity=300`). Field đúng là
**`openQuantity`**. Sau khi sửa: **642,5tr** — khớp §A6 tới 0,01tr, tức §A6 được **tái lập độc lập**
bằng một đường tính khác (giá `marketPrice` của broker thay vì giá BQ).

> Bài học cùng họ §6 coding_guidelines: một field có tên nghe hợp lý và một giá trị nghe hợp lý
> **không phải** là xác minh. Thứ bắt được lỗi là **đối chiếu chéo với một con số đã pin từ trước**
> (642,46tr của §A6) — không phải đọc lại code.


---

## F. VIỆC 3 — Thiết kế P0: tag `book`/`play_type` vào journal TẠI THỜI ĐIỂM FILL

**Đây là THIẾT KẾ, chưa implement** (đúng phạm vi dispatch). Mục tiêu: thay `park_mv_live` "suy luận
theo tên mã" (§A7 — đã biết sai với VPB, plan hôm nay tự ghi `book_note="LAG/PARK"`) bằng một sổ lô
dựng từ journal.

### F1. File cần sửa — đúng MỘT hàm

| | |
|---|---|
| **File** | `trading_bot/executor.py` |
| **Hàm** | `Executor._journal()` — dòng **262-273** |
| **File journal** | `data/execution_logs/exec_{account_label}_{plan_date}_journal.csv` (dòng 80: `self.journal_file`) |
| **Header hiện tại** | `ts, event, parent_id, ticker, side, child_oid, qty, price, filled_total, note` |

`_journal()` đã nhận sẵn `o` (một `PlannedOrder`), và `PlannedOrder` **đã có** `book` + `play_type`
(`trading_bot/plan.py:24-25`), đã được plan generation điền, và `load_plan()` giữ nguyên vì chúng nằm
trong `dataclasses.fields`. ⇒ **Không cần đổi plan, không cần đổi executor logic, không đụng đường đặt
lệnh.** Sửa đúng 2 chỗ trong 1 hàm:

```python
w.writerow(["ts", "event", "parent_id", "ticker", "side",
            "child_oid", "qty", "price", "filled_total", "book", "play_type", "note"])
...
w.writerow([..., o.book if o else "", o.play_type if o else "", note])
```

**Chèn TRƯỚC `note`, không append sau** — `note` là trường tự do có thể chứa dấu phẩy; giữ nó ở cuối
cùng là quy ước an toàn của file này. Ghi tại `_journal()` chứ không tại chỗ gọi ⇒ **mọi** event
(`FILL`, `PLACE`, `CANCEL`, `DONE`…) đều được tag đồng nhất, không sót nhánh nào.

⚠️ **Tương thích ngược bắt buộc**: `_journal` chỉ ghi header khi file CHƯA tồn tại ⇒ journal cũ có 10
cột, journal mới 12. **Mọi reader phải dùng `csv.DictReader` + `row.get("book", "")`**, tuyệt đối
không đọc theo chỉ số cột. (Nếu ai đó đang đọc positional, đây là chỗ nó vỡ — cần grep trước khi ship.)

### F2. Dựng lại sổ lô — `park_holdings(account, asof)`

**Ngữ nghĩa `qty` trong dòng FILL là TÍCH LUỸ theo `child_oid`, KHÔNG phải delta** — verify trên
`exec_SpaceX_2026-07-29_journal.csv`: 3 dòng FILL của `BUY-TV1-DISC-04` có `filled_total` = 0/100/200
(tích luỹ của PARENT trước dòng đó) trong khi `qty`=100 mỗi dòng là tích luỹ của CHILD. Executor ghi
lại dòng FILL mỗi lần `u.filled_qty` tăng ⇒ cùng một `child_oid` có thể xuất hiện nhiều lần với qty
tăng dần. Reconstruction đúng:

```
delta(child_oid) = qty(dòng này) − qty(dòng trước CÙNG child_oid)      # 0 nếu là dòng đầu của child
```

Cộng dồn kiểu "Σ qty mọi dòng FILL" sẽ **đếm trùng** — đây là cái bẫy số 1 của file này.

Thuật toán:
1. Duyệt journal theo **thứ tự ngày file** rồi `ts` trong file (KHÔNG glob rồi sort chuỗi tên — dùng
   `plan_date` parse ra `date`).
2. `side=buy` → **push lô** `{ticker, book, play_type, entry_date=ts[:10], qty=delta, price}`.
3. `side=sell` → **tiêu thụ FIFO TRONG CÙNG `book`** của lệnh bán (lệnh bán cũng mang tag `book` do
   plan sinh ra). Đây chính là chỗ cách suy-luận-theo-tên chết: VPB nằm cả LAG lẫn PARK, chỉ tag mới
   phân định được bán từ sổ nào.
4. Lệnh bán **không có** tag `book` (journal cũ, hoặc `GHOST_ORDER` — lệnh có ở broker mà không có
   trong state, `executor.py:1176`) → FIFO theo ticker, oldest-first, và **gắn cờ `UNVERIFIED`** cho
   toàn bộ ticker đó. **Cấm** dùng số `UNVERIFIED` làm cơ sở sinh lệnh trim (cùng tinh thần §21).
5. `park_mv_live = Σ (qty × marketPrice_broker)` trên các lô `book == "PARK"`.
   Giá **từ DNSE `positions[].marketPrice`**, không từ BQ (§6).

### F3. Bootstrap — điều kiện tiên quyết mà thiết kế KHÔNG được lờ đi

Journal trước ngày bật tag **không có cột `book`** và **không suy ngược được** (đó chính là §A7).
⇒ cần một **snapshot khởi tạo do người xác nhận**, một lần:

`data/book_tags_bootstrap_{account}.json` — với mỗi ticker đang giữ tại ngày cutover: danh sách lô
`{qty, book, entry_date, cost_price, source: "bootstrap"}`, tổng qty **phải khớp `openQuantity` của
broker** ngày đó. Sau cutover, FIFO chạy tiến từ snapshot này.

Không có bootstrap thì `park_holdings()` chỉ thấy phần mua SAU cutover ⇒ `park_mv_live` **thấp hơn
thực tế** ⇒ L1 tính ra "PARK chưa vượt target" và **không trim gì cả** — im lặng, đúng dạng lỗi khó
phát hiện nhất. **Không được ship L1 trước khi bootstrap tồn tại và đã đối chiếu.**

### F4. Đối soát bắt buộc + 3 khe hổng đã biết

**Đối soát hằng ngày**: Σ qty các lô mỗi ticker **phải bằng** `openQuantity` của broker
(`dnse_raw_{date}.jsonl`, **lọc `accountNo` ngay dòng đầu** — §12). Lệch ⇒ **fail loudly**, KHÔNG tự
điều chỉnh lô cho khớp (§5: không đoán-rồi-gộp).

| Khe hổng | Vì sao journal không thấy | Xử lý |
|---|---|---|
| **Sự kiện quyền** (cổ tức CP, chia tách) | qty đổi ngoài journal | đối soát phát hiện lệch → scale lô pro-rata trong ticker, gắn cờ, báo người. KHÔNG tự động. Liên quan §21 |
| **`GHOST_ORDER`** | fill có ở broker, không có trong state | ticker đó → `UNVERIFIED`, cấm dùng cho L1 |
| **Vị thế legacy** (DGC/ZaloPay) | mua trước khi bot quản lý | nằm trong `excluded_tickers`, **không** vào sổ PARK; sizing vẫn theo `active_nav` (§7) |

### F5. Selfcheck phải có trước khi gọi là xong (§19 `verify-before-done`)

`book_tagging_selfcheck.py`, tối thiểu 6 ca — mỗi ca là một cách reconstruction có thể sai thật:
(1) journal cũ 10 cột đọc được, `book` rỗng, không crash; (2) **cùng `child_oid` xuất hiện 3 lần
qty tăng dần → tổng đúng 1 lần, không nhân 3**; (3) VPB mua ở LAG rồi mua ở PARK, bán 1 lô LAG → PARK
không đổi; (4) bán không tag → cờ `UNVERIFIED` bật; (5) Σ lô ≠ `openQuantity` → raise, không tự sửa;
(6) 2 account cùng ngày cho ra 2 kết quả KHÁC nhau (§12 — hai output giống hệt = gần như chắc chắn
quên lọc account). Chạy dưới `env -u TZ` vì `now_ict()` dính TZ (§16).


---

## E. VIỆC 2 — Chân ablation thứ 4 (và thứ 5): 2×2 ĐẦY ĐỦ, và nó LẬT NGƯỢC §C4

Harness `exp_park_jit_20260803/run_jit3.sh <tag> <PARK_JIT> <PARK_PREFILL>`; switch mới
`PARK_PREFILL` tắt hẳn khối 4c (`simulate_holistic_nav.py:913`, bản sao research). Cùng cấu hình vòng
trước: `AUDIT_END=2026-06-19`, `NAV=50B`, `universe_pit`, `BQ_LOCAL_CACHE=bq_cache_asof20260729_postrestate`,
threads=1. Dispatch yêu cầu 1 chân (4c off, JIT on = **D**); tôi chạy thêm **E** (cả hai off) vì chỉ E
mới là mô phỏng trung thực của LIVE hôm nay — D một mình không trả lời được câu hỏi thật.

### E1. Gate tự kiểm — PASS cả ba

- **MD5 no-op gate**: chân **A** (on/on) với code đã thêm switch cho CSV **md5 `7d053e62…`** —
  **trùng khít** CSV vòng trước và CSV production. ⇒ `PARK_PREFILL` là no-op tuyệt đối khi `=on`.
- **MD5 phân biệt**: 4 chân ra 4 md5 khác nhau (`7d053e62` / `4220e893` / `133a4c0a` / `234892ba`)
  ⇒ không tái diễn lỗi no-op của §0.
- **selfcheck cash-flow + NAV identity = 0 VND** cả 2 sổ, ở **cả 4** chân.
- Chân **C** giữ nguyên CSV vòng trước (`133a4c0a`): delta code duy nhất là hội `and _PARK_PREFILL != "off"`,
  hằng đúng khi `=on` ⇒ không cần chạy lại. (Lập luận, không phải phép đo — nêu rõ để ai muốn có thể chạy lại.)

### E2. Bảng 2×2

| Chân | L1 `PREFILL` | L2 `JIT` | CAGR | Sharpe | **MaxDD** | **Calmar** | Final NAV | buy bị bỏ |
|---|---|---|---|---|---|---|---|---|
| **A** control (= số pin) | on | on | 28,86% | **1,90** | **−17,8%** | **1,62** | 1.178,01B | 0 |
| **D** (dispatch yêu cầu) | **off** | on | 29,92% | 1,76 | −25,1% | 1,19 | 1.304,09B | 0 |
| **C** | on | **skip** | 28,08% | 1,88 | −17,9% | 1,57 | 1.092,34B | 8.995 |
| **E = LIVE HÔM NAY** | **off** | **skip** | **33,16%** | **1,48** | **−33,7%** | **0,98** | 1.773,34B | **25.682** |

### E3. 🔴 §C4 SAI — và cái sai đó đổi hẳn luận cứ wire

§C4 dự đoán *"tắt 4c sẽ tệ hơn C rõ rệt"*. **Bác bỏ.** Tắt L1 làm **CAGR TĂNG** (28,86 → 29,92; tắt
cả hai → **33,16%**). Cái xấu đi là **RỦI RO**:

| A → | ΔCAGR | ΔMaxDD | ΔCalmar | ΔSharpe |
|---|---|---|---|---|
| **D** (tắt riêng L1) | **+1,06pp** | **−7,3pp** (−17,8→−25,1) | −0,43 | −0,14 |
| **C** (tắt riêng L2) | −0,78pp | −0,1pp | −0,05 | −0,02 |
| **E** (tắt cả hai) | **+4,30pp** | **−15,9pp** (−17,8→−33,7) | **−0,64** | **−0,42** |

**Cơ chế, một câu:** PARK **không phải tiền mặt** — nó là 30 blue-chip. Trần park 70% pool vì thế là
một **TRẦN TỶ TRỌNG CỔ PHIẾU** trá hình. Bỏ hai đường bán ⇒ tiền nhàn rỗi dồn vĩnh viễn vào cổ phiếu
⇒ tỷ trọng bò lên không kiểm soát ⇒ lãi hơn khi thị trường lên, **sập sâu gần gấp đôi** khi xuống.
Bằng chứng năm khủng hoảng: **2022 A −8% vs E −21%**; bằng chứng năm bùng nổ: **2020 A +28% vs E +70%**,
**2021 +108% vs +131%**. Đúng dấu vân tay của "tăng đòn bẩy tỷ trọng", không phải của alpha.

**Hai đường TƯƠNG TÁC MẠNH, không cộng tuyến:** riêng lẻ +1,06 và −0,78 (tổng +0,28pp) nhưng cùng lúc
**+4,30pp**; MaxDD riêng lẻ 7,3+0,1=7,4pp nhưng cùng lúc **15,9pp**. Lý do: L1 tắt ⇒ PARK phình to ⇒
số lệnh mua bị bỏ vì kẹt vốn nhảy từ 8.995 lên **25.682 (×2,9)**. ⇒ **Cấm ngoại suy tuyến tính từ
một chân đơn** — đây chính là lý do phải chạy đủ 2×2 chứ không chỉ chân D như dispatch yêu cầu.

### E4. Con số quyết định — nếu chỉ đọc một dòng thì đọc dòng này

> **Số pin R3 (28,86% · Sharpe 1,90 · MaxDD −17,8% · Calmar 1,62) KHÔNG mô tả live.**
> Mô phỏng trung thực của live hôm nay là chân **E: 33,16% · Sharpe 1,48 · MaxDD −33,7% · Calmar 0,98**.
> Live đang chạy một cuốn sổ **rủi ro cao hơn hẳn** cuốn đã được duyệt — **không ai từng sizing cho nó**.

Ghi chú hội tụ (không phải cùng nguyên nhân, nhưng cùng chiều): `kb/current_ops.md` đã dặn **anchor DD
~−30%, KHÔNG phải −17,8%** vì lỗi fidelity `liq<=0` còn mở. Chân E cho **−33,7%** từ một nguyên nhân
hoàn toàn khác (thiếu 2 đường bán PARK). Hai đường độc lập cùng chỉ về vùng −30% ⇒ **con số −17,8%
không nên dùng làm neo rủi ro trong bất kỳ tài liệu nào cho tới khi cả hai được đóng.**

### E5. Đường đi ĐÚNG cho quyết định: live → L1 → L1+L2

So sánh phải xuất phát từ **E** (live), không phải từ A:

| Bước | Chân | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|
| Live hôm nay | **E** | 33,16% | 1,48 | −33,7% | 0,98 |
| **+ wire L1** (park-target compliance) | **C** | 28,08% | 1,88 | **−17,9%** | **1,57** |
| **+ wire L2** (JIT unpark) | **A** | 28,86% | 1,90 | −17,8% | 1,62 |

> **L1 một mình lấy lại gần như TOÀN BỘ kỷ luật rủi ro**: Calmar 0,98 → **1,57** (+0,59), MaxDD
> −33,7% → **−17,9%** (+15,8pp), Sharpe 1,48 → 1,88. L2 thêm phần nhỏ còn lại (Calmar +0,05).
> ⇒ Khuyến nghị **"L1 trước L2"** của §B1 được xác nhận bằng số — và bằng **lý do đúng (rủi ro), không
> phải lý do cũ (0,78pp CAGR đã bị chính §C3 bác)**.

**Giá phải trả, nói thẳng:** wire L1 **hạ CAGR mô phỏng 33,16% → 28,08%** (−5,08pp). Đây không phải
"mất alpha" — đó là trả lại phần lợi nhuận vay mượn từ tỷ trọng cổ phiếu vượt thiết kế, kèm đổi lại
**một nửa mức sụt giảm tối đa**. Người quyết định phải thấy cả hai vế; ai chỉ trích vế CAGR sẽ kết
luận ngược.

### E6. Phạm vi & điều KHÔNG được suy ra

- IS/OOS (`extract_peryear.py`, tính lại thống nhất cho cả 4 chân): A **IS 27,09 / OOS 30,48**;
  E **IS 26,28 / OOS 39,63**. Toàn bộ khoảng cách CAGR của E nằm ở **OOS (2020+, giai đoạn bò)** —
  đúng như kỳ vọng của "thừa tỷ trọng": thắng đậm trong bull, và trả lại ở 2022 (−21% vs −8%).
  (Số IS/OOS của A ở §C3 là 27,04/30,15 — chênh nhẹ do §C3 dùng cách cắt khác; ở đây dùng **một**
  công cụ cho **cả bốn** chân để so được với nhau.)
- **Không chạy DSR/PBO** — cố ý. DSR/PBO là công cụ cho việc **chọn 1 cấu hình từ một họ để lấy
  alpha**. Ở đây không chọn gì: L1/L2 là **port nguyên trạng** cơ chế đã có trong engine đã pin,
  N_trials = 0, và luận cứ là **tuân thủ spec + kỷ luật rủi ro**, không phải edge. Nếu ai đề xuất
  *tinh chỉnh* tham số (đổi 0,70, đổi 0,005, đổi FIFO) thì **lúc đó** DSR/PBO trở thành bắt buộc.
- **Không suy ra "live đang lãi hơn nên cứ để vậy".** Toàn bộ khung margin/đòn bẩy hiện hành
  (V2.5 DISABLED, trần MGE) được đặt **với giả định trần tỷ trọng park tồn tại**. Nó không tồn tại.
- Ablation chạy ở NAV 50B trên `universe_pit`; SpaceX có margin, ZaloPay cash-only ⇒ mức phóng đại
  rủi ro ở tài khoản có margin có thể **cao hơn** chân E, không thấp hơn.


---

## G. Kết luận phụ lục — trạng thái 3 việc & điều kiện để lên quant-skeptic vòng 2

| Việc | Trạng thái | Kết quả cốt lõi |
|---|---|---|
| **1. Capacity** | ✅ XONG, thiết kế đã sửa | Tiền đề của objection sai (ADV rổ custom30V, không phải E1VFVN30) **nhưng kết luận đúng**: trần TỔNG của engine lỏng hơn ràng buộc per-name **8,6–11,1×**. Đo thực tế: **0/24 mã vượt, dư địa 638×**. Đã thêm **trần per-name tầng 2** dùng nguyên `LAG_ADV_PCT×ADV×share` — **0 tham số mới** |
| **2. Chân ablation 4 (+5)** | ✅ XONG, **lật ngược §C4** | Live thật = chân **E: 33,16% / Sharpe 1,48 / MaxDD −33,7% / Calmar 0,98** vs số pin 28,86/1,90/−17,8/1,62. **L1 một mình** kéo Calmar 0,98→1,57. Hai đường **tương tác mạnh**, cấm ngoại suy tuyến tính |
| **3. P0 book tagging** | ✅ XONG (thiết kế) | Sửa đúng `Executor._journal()` (`executor.py:262-273`), +2 cột `book`/`play_type` từ `PlannedOrder` đã có sẵn. Bẫy chính: `qty` FILL là **tích luỹ theo `child_oid`**. **Bắt buộc có bootstrap snapshot** trước khi ship L1 |

**Luận cứ wire ĐÃ ĐỔI HẲN so với thân báo cáo.** Phiên bản cũ (§C3, §Kết luận mục 4): *"đừng trích
+0,78pp, wire vì tuân thủ spec"*. Phiên bản đúng sau 2×2: **wire vì KỶ LUẬT RỦI RO, và cái giá là
CAGR mô phỏng GIẢM 5,08pp** — một luận cứ mạnh hơn hẳn, và một cái giá phải nói thẳng với người quyết
định. Mục 4 của §Kết luận thân báo cáo nay đã **lỗi thời**; đọc §E4/§E5 thay thế.

**Điều kiện để lên quant-skeptic vòng 2** (chưa đủ, còn thiếu):
1. ✅ Thiết kế capacity-safe (§D2) — xong.
2. ✅ Tách được đóng góp L1 vs L2 (§E) — xong.
3. ✅ Thiết kế P0 (§F) — xong (thiết kế; **implement + selfcheck là việc riêng, chưa làm**).
4. ⬜ **CHƯA**: bootstrap snapshot book-tag cho SpaceX/ZaloPay (§F3) — không có nó, L1 sẽ im lặng
   không trim gì. Cần người xác nhận, không tự sinh được.
5. ⬜ **CHƯA**: quyết định của user về **đánh đổi −5,08pp CAGR đổi lấy MaxDD −33,7%→−17,9%**. Đây là
   một lựa chọn khẩu vị rủi ro, **không phải** một câu hỏi kỹ thuật — Taylor không tự quyết.

**Vẫn KHÔNG sửa file production nào.** `git diff` trên `golive_recommend_v23.py`,
`simulate_holistic_nav.py` (bản production), `trading_bot/` = rỗng. Mọi thay đổi nằm trong
`mike/agents/Taylor/exp_park_jit_20260803/`.
