# Chuyển quyết định CƠ HỌC khỏi LLM trong pipeline lập plan T+1

**Job** `Taylor_20260804_125048` · **Ngày** 2026-08-04 · **Trạng thái** Bước 1-4 XONG, CHƯA wire vào dispatch

---

## 0. Tóm tắt cho người đọc vội

- **Bước 1 (rà soát)**: tìm thêm **6 quyết định cơ học** đang giao cho LLM ngoài 3 cái đã biết; **4/6
  đã từng gây sự cố thật** (mất tiền hoặc suýt mất tiền). Bảng §2, mỗi dòng có file+dòng.
- **Bước 2**: `mike/bin/filter_lag_entry_window.py` — lọc cửa sổ T+1. Selfcheck **43/43 PASS**.
- **Bước 3**: `mike/bin/sector_valuation_lens.py` — lăng kính ngành cho FLOOR_FAIL. Selfcheck **51/51 PASS**.
- **Phát hiện quan trọng nhất, làm đổi hẳn cách hiểu sự cố 07-28**: lăng kính ngành **KHÔNG hề
  thiếu**. `alt_valuation_lens.py` có từ **2026-07-20** (commit `8136112`, trước sự cố 8 ngày) và
  engine **đã in sẵn kết luận `— CHEAP` vào đúng ô CSV mà cả 2 phiên đang đọc**. Phiên ZaloPay
  không "thiếu công cụ phân tích" — nó **bỏ qua một giá trị đã tính xong nằm ngay trong ô nó đọc**.
  ⇒ Bước 3 KHÔNG viết lại lăng kính (sẽ là nhân bản logic, §2/§3 coding_guidelines); nó **trích**
  giá trị đó ra và biến thành quyết định dứt khoát.
- **Bước 4 (đối chiếu song song)**: script tái lập ĐÚNG kết luận của bên làm đúng (kể cả **trùng
  từng con số** P/B 0,91 / 0,75 / 1,33) và sửa được bên làm sai. Chi tiết §5.
- **Phát hiện phụ ngoài phạm vi dispatch**: ở ca 08-04, **CẢ HAI** plan đều thiếu, không chỉ ZaloPay.
  SpaceX bỏ sót MAC + TV3 (đều T+1 hợp lệ). Xem §5.1.

---

## 1. Vì sao lớp lỗi này tồn tại

DollarBill là **phiên LLM mới hoàn toàn mỗi lần dispatch**, không có state dùng chung giữa 2 phiên
SpaceX/ZaloPay. Mọi luật sống trong `kb/context_planning_mini.md` đều là luật LLM **tự nhớ và tự áp
lại từ đầu mỗi phiên**. Cùng một input ⇒ output có thể khác nhau tuỳ phiên đó "nhớ" đúng hay không.

Đây không phải giả thuyết: file `context_planning_mini.md` **tự nó ghi lại 3 lần** hai account cho
ra hai kỷ luật khác nhau trên cùng một danh sách ứng viên — dòng 94-96 (`funding_required`), dòng
152-157 (cửa sổ T+1), dòng 248-251 (FLOOR_FAIL). Thêm luật vào file chỉ làm tăng lượng thứ phải nhớ;
nó không đổi bản chất cơ chế.

**Tiêu chí lọc dùng cho §2** (đúng như dispatch mô tả): một quyết định vào danh sách khi nó là **suy
dẫn thuần tuý từ dữ liệu đã có sẵn** — tính ngày/offset, đọc field boolean rồi lọc, tra bảng
(ngành→công thức, ticker→danh sách loại trừ), so sánh số với hằng số có sẵn. Không cần phán đoán,
không cần sáng tạo. Ngược lại, "mã này có đáng mua không" thì KHÔNG vào danh sách.

---

## 2. Bước 1 — Kiểm kê đầy đủ

Ba cái đã biết được đánh dấu **[đã biết]**. Mọi dòng đều có bằng chứng đọc code thật.

| # | Quyết định cơ học | Bằng chứng (file:dòng) | Đã gây sự cố thật? | Trạng thái |
|---|---|---|---|---|
| **A1** | **Σ `orders[]` ≤ cash thực → tự SHRINK/defer**, và thứ tự ưu tiên khi phải bỏ bớt (LAG deadline T+1 > CAPIT top-up > discretionary đã duyệt) | luật: `kb/context_planning_mini.md:89-112`. Cơ chế duy nhất đang có: `bot_execute.py:151,156,478` `_log_plan_buying_power_shadow` — **WARN-only, không chặn**, và `data/plan_buying_power_shadow_log.csv` tới hôm nay có **đúng 1 dòng** (2026-07-29) | **CÓ — 3 lần**: 07-23 (177,2M vs cash 49,1M), 07-27 (460,7M vs 12,4M), 07-28 tái phạm lần 3 (146,5M vs 10,41M) | **HỞ — ưu tiên #1** |
| **A2** | Trừ trước tiền tranche discretionary (TV1) khỏi cash khả dụng **trước khi** size lệnh V2.4 | luật: `context_planning_mini.md:59-65`. Bộ chèn `mike/bin/discretionary_accumulation_inject.py` chạy **20:30 ICT, SAU** khi DollarBill ghi plan (~19:0x) và trước `send_plan_report` 21:00 (crontab). `grep -n "cash\|available\|ppse" mike/bin/discretionary_accumulation_inject.py` → **0 kết quả** ⇒ không tầng nào kiểm TỔNG của 2 nguồn lệnh | **CÓ** — 07-24: V2.4 45,9M + TV1 3,98M = 49,9M > cash 49,1M (thiếu ~0,78M) | **HỞ — ưu tiên #2** |
| **A3** | VND/slot của CAPIT: đọc thẳng `status["capit_slot_targets"]`, KHÔNG nhân lại từ cột `weight_pct` | `deploy_golive_dt5g_v4/golive_recommend_v23.py:958-961` (comment mô tả nguyên sự cố), `:983-990` (`weight_base = "NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI"`), `:1062` (`capit_slot_targets` đã tính sẵn), `:1211` | **CÓ** — 07-21: nhân `capit_size` 2 lần ⇒ SpaceX thiếu 87,1tr (`kb/projects/capit-sizing-bug-0721.md`) | **HỞ** (hàng rào hiện tại = **đặt tên cột cho xấu** + comment; root cause code đã fix nhưng đường LLM đọc CSV vẫn còn) |
| **A4** | Danh sách LAG bị user loại tường minh (IVS, TMG) | luật: `context_planning_mini.md:124-134`. `grep -rn "IVS\|TMG" --include=*.py trading_bot/ deploy_golive_dt5g_v4/ mike/bin/` → **chỉ có trong comment/docstring**, KHÔNG có danh sách nào trong code | **CÓ** — 07-23: IVS vào plan LAG 07-24 ở **cả 2 account** | **HỞ** (ADV-cap chặn được TMG nhờ ADV=0, nhưng đó là trùng hợp, không phải cơ chế) |
| **A5** | Có cờ đỏ DD + side=buy ⇒ bắt buộc `dd_override_reason` | `trading_bot/due_diligence.py:311-321` (`format_dd_check`), `:439-443` (disclaimer), `trading_bot/executor.py:588` (ghi lại lúc khớp) — toàn bộ là **chuỗi cảnh báo**, không có checker nào chặn plan thiếu field | **CÓ** — DHD 08-03 lọt vào plan dù 2 dòng 🔴 hiện đủ trong report | **HỞ, mức thấp hơn** (đúng thiết kế: mandate gốc "THUẦN THÔNG TIN, KHÔNG chặn lệnh") |
| **A6** | `ref_price` phải lấy DNSE, không lấy field giá trong CSV | `context_planning_mini.md:41-46`; hàng rào hiện có = **đổi tên cột cho xấu**: `golive_recommend_v23.py:965` `close_bq_stale_DO_NOT_USE_AS_REFPRICE` (comment `:953-956` nói rõ "prompt cấm không đủ") | **CÓ** — 07-09, 2/4 lệnh lệch +5,7% | **ĐÃ GIẢM RỦI RO** — tên cột là hàng rào cơ học thật; còn hở ở chỗ không ai kiểm `ref_price` sau khi plan viết xong |
| **A7** [đã biết] | Lọc cửa sổ entry T+1 | `context_planning_mini.md:147-169`; engine sinh `status` tại `golive_recommend_v23.py:739-745` | **CÓ** — 08-04 | ✅ **GIẢI ở Bước 2** |
| **A8** [đã biết] | `book_note` / phân loại book | — | **CÓ** — VPB/VND gắn nhãn `"LAG/PARK"` sai | ✅ **ĐÃ GIẢI** (`mike/bin/park_holdings.py`, 08-04) |
| **A9** [đã biết] | FLOOR_FAIL → lăng kính ngành | `context_planning_mini.md:244-261` | **CÓ** — 07-28 | ✅ **GIẢI ở Bước 3** |
| A10 | Sizing theo `active_nav` khi có `excluded_tickers` | `context_planning_mini.md:36-39` | — | ✅ **ĐÃ CƠ HỌC** — `bin/compute_active_nav.py` + `trading_bot.plan.filter_excluded_tickers()` gọi trong `bot_execute.py` (chặn thật, không chỉ nhắc) |
| A11 | LAG rating≥4 → loại | `context_planning_mini.md:81-87` | **CÓ** (TRC 07-23, MST 07-27) | ✅ **ĐÃ CƠ HỌC** — `lag_filter_low_rating()` loại thật ở nguồn |
| A12 | Park-trim L1 | `context_planning_mini.md:185-242` | **CÓ** (vượt trần +189,4tr) | ✅ **ĐÃ CƠ HỌC** — `mike/bin/compute_park_trim.py` |
| A13 | State DT5G / `dt4_gate_line` chép vào plan | `context_planning_mini.md:26-30` | **CÓ** (07-11, đọc nhầm bảng base) | ⚠ **THẤP** — `get_gated_state()` đã canonical; rủi ro còn lại chỉ là chép sai số vào JSON |

**Xếp ưu tiên theo độ rủi ro (tiêu chí dispatch: đã gây sự cố thật → ưu tiên):**

1. **A1 cash-discipline** — 3 sự cố/15 ngày, cùng một khuôn, lần thứ 3 xảy ra *sau khi* đã cấm tường
   minh bằng văn bản. Đây là bằng chứng mạnh nhất cho toàn bộ luận điểm của dispatch này: **cấm bằng
   văn xuôi đã thất bại 3 lần liên tiếp trên đúng lỗi đó**.
2. **A2 TV1 cash** — hở về **kiến trúc**, không phải hở về trí nhớ: hai bộ sinh lệnh (LLM 19:0x và
   cron injector 20:30) cùng tiêu một túi tiền mà không tầng nào cộng lại.
3. **A3 CAPIT slot VND** — sự cố đắt nhất đã đo được (87,1tr).
4. **A4 exclude list** — rẻ nhất để làm (1 file JSON + 1 checker), đã sai ở cả 2 account cùng lúc.

**Còn nợ**: A1-A4 CHƯA làm (dispatch giới hạn phạm vi ở 2 script). A5-A6 đề nghị để nguyên (đúng
thiết kế "thuần thông tin" mà user đã chốt; đổi thành gate cứng là quyết định chính sách của user,
không phải việc dọn dẹp kỹ thuật).

---

## 3. Bước 2 — `mike/bin/filter_lag_entry_window.py`

**Chỉ đọc.** Không BQ, không DNSE, không ghi plan. Đầu vào duy nhất: CSV khuyến nghị engine đã sinh.

Phân loại mọi dòng `book=LAG` thành 3 rổ: `due_today` (T+1, ứng viên DUY NHẤT của plan hôm nay) ·
`upcoming_next_plans` (T+2 trở đi) · `window_passed`. Kèm `unparsed` cho dòng không khớp mẫu — **không
tự bỏ qua**.

**Thứ đáng nói nhất trong thiết kế — CỔNG LỊCH (fail-closed).** "T+1" là T+1 **so với `signal_date`
của CSV**, không phải so với hôm nay. Nếu `plan_date` không phải phiên ngay sau `signal_date` (CSV cũ,
lập lại plan trễ, nghỉ lễ) thì nhãn T+1 **không còn trỏ vào plan_date** — script **từ chối phân loại**
và trả `calendar_check.ok=false` + exit code 2, thay vì đoán. Đây đúng là kiểu sai mà đọc CSV bằng mắt
không thể thấy: mọi dòng vẫn ghi "T+1", chỉ có cái mốc nó neo vào là đã đổi.

Đường quyết định **không dùng lịch giao dịch**: khi cổng lịch PASS thì `T+1 ⇔ plan_date` theo định
nghĩa. Chỉ `entry_date_est` của nhóm T+2 trở đi mới suy từ `vn_market.next_trading_day` và được gắn
hậu tố `_est` — vì `_VARIABLE_HOLIDAYS` (Tết ÂL, giỗ Tổ) hiện **rỗng**, số đó có thể lệch quanh kỳ
nghỉ. Nó chỉ để hiển thị, không quyết định gì.

```bash
python3 mike/bin/filter_lag_entry_window.py --account SpaceX --plan-date 2026-08-04 \
    --signal-date 2026-08-03 [--out data/trade_plans/lag_window_<account>_<date>.json] [--json]
```

**Selfcheck** `mike/bin/filter_lag_entry_window_selfcheck.py` — **43/43 PASS** (chạy dưới `env -u TZ`).
Neo vào dữ liệu thật của 2 ca đã biết đáp án, cộng: cổng lịch lệch 1 phiên → FAIL, cổng lịch qua cuối
tuần (T6→T2) → PASS, plan_date rơi vào thứ Bảy → FAIL, dạng `UPCOMING <ngày>` end-to-end, dòng
`book=BAL` bị bỏ qua, status lạ → `unparsed`, thiếu CSV → error không raise, và **kết quả byte-identical
ở 4 cấu hình TZ** (`env -u TZ` / UTC / ICT / America/New_York — §16 coding_guidelines).

---

## 4. Bước 3 — `mike/bin/sector_valuation_lens.py`

### 4.1 Phát hiện làm đổi hẳn phạm vi việc này

Dispatch giao "viết script/bảng tra cứu mới trả về công thức định giá thay thế". Đọc code trước khi
viết cho kết quả khác: **bảng đó đã tồn tại và đã chạy sẵn trong production.**

- `alt_valuation_lens.py` — commit `8136112`, **2026-07-20 17:22 +0700**, tức **8 ngày TRƯỚC** sự cố
  07-28. Chứa đủ 6 lăng kính: Gordon P/B ngân hàng, P/B+ROE chứng khoán, P/B thô bảo hiểm, P/B trough
  vận tải biển (ICB 2773), EV/EBITDA cảng-hạ tầng (2777) và viễn thông (6535/2357), 8L fallback rộng.
- `golive_recommend_v23.py:999-1016` gọi `run_due_diligence` cho **mọi** ứng cử viên, và
  `trading_bot/due_diligence.py:393-408` gọi lại lăng kính đó, rồi in kết quả vào cột `due_diligence`
  của CSV.
- Kiểm chứng trên file gốc `deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-07-27.csv` — đúng
  file mà `plan_SpaceX_2026-07-28.json` khai ở field `recommendations_file`:

  ```
  EVF … → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.91 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP
  PSI … → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.75 (band cheap <1.8), ROE_TTM 8.8% (cần >8%) — CHEAP
  VCI … → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.33 (band cheap <1.8), ROE_TTM 9.2% (cần >8%) — CHEAP
  ```

**Kết luận lại nguyên nhân gốc 07-28**: không phải "thiếu lăng kính" và cũng không hẳn là "SpaceX
thông minh hơn". SpaceX **chép đúng** con số đã có trong CSV (P/B 0,91 / 0,75 / 1,33 khớp từng chữ số
với `dd_summary` trong plan của nó); ZaloPay **không đọc tới cuối ô đó**. Cùng một ô, hai phiên đọc
khác nhau. ⇒ Việc cần làm không phải tính lại, mà là **biến giá trị đã có thành một quyết định không
thể hiểu theo 2 nghĩa**.

### 4.2 Thiết kế

Script **không nhân bản logic lăng kính** (§2/§3 coding_guidelines). Hai nguồn, theo thứ tự:

1. `--signal-date`/`--csv` → **trích** từ cột `due_diligence`. Đúng point-in-time (là thứ engine đã
   tính tại signal_date đó) và **tái lập được cho mọi ngày quá khứ**.
2. `alt_valuation_lens.alt_lens()` live — chỉ khi mã không có trong CSV. Đọc `data/rating_8l.csv`
   (snapshot HÔM NAY) ⇒ kết quả **luôn kèm `caveat`** nói rõ không point-in-time.

**Không dùng BQ ở bất kỳ nhánh nào** ⇒ không thể vi phạm điều 6 (same-day phải là DNSE); script cũng
không đụng giá same-day.

**Ưu tiên trục định giá**: DCF chạy được (`CHEAP`/`RICH`) thì **DCF mới là trục chính**, script báo
`valuation_axis_used="DCF"` và không để fallback đè lên. Lăng kính thay thế chỉ vào cuộc khi
`DCF: NOT_COMPUTED`.

**Bảng quyết định** (1-1 với luật đã chốt):

| verdict | decision | nghĩa |
|---|---|---|
| CHEAP | `KHONG_SKIP_VI_FLOOR_FAIL` | lăng kính ngành ỦNG HỘ — FLOOR_FAIL **một mình** không đủ để loại |
| RICH | `SKIP_CO_CAN_CU` | lăng kính thay thế CŨNG nói đắt ⇒ skip có căn cứ, ghi rõ lý do |
| N/A | `CAN_NGUOI_QUYET` | chỉ có lăng kính THÔ/fallback ⇒ **không** lặng lẽ skip, cũng **không** lặng lẽ mua |
| không có lăng kính | `CAN_NGUOI_QUYET` | ngành chưa có lăng kính thay thế |

⚠ `KHONG_SKIP_VI_FLOOR_FAIL` **không cấp quyền mua**. Mọi lệnh vẫn qua nguyên các gate cứng hiện có
(8L rating≤3 đã lọc ở nguồn, `cap_lag_orders` %ADV, cash-discipline, DD cờ đỏ). Script chỉ gỡ đúng
một lý do skip không hợp lệ.

```bash
python3 mike/bin/sector_valuation_lens.py --signal-date 2026-07-27 --floor-fail-only
python3 mike/bin/sector_valuation_lens.py --ticker VCI --ticker PSI --ticker EVF
```

**Selfcheck** `mike/bin/sector_valuation_lens_selfcheck.py` — **51/51 PASS** (`env -u TZ`). Gồm một
test đáng chú ý: **round-trip qua hàm THẬT** — bơm 7 dòng giả vào cache của `alt_valuation_lens`, gọi
`format_alt_lens()` thật cho **mọi nhánh lăng kính**, rồi parse ngược. Ai đổi câu chữ bên module gốc
thì test vỡ ngay, thay vì để script lặng lẽ trả verdict rỗng.

---

## 5. Bước 4 — Chạy song song trên dữ liệu thật

### 5.1 Cửa sổ T+1 — signal 2026-08-03 → plan 2026-08-04

Script: `due_today = APF, MAC, TV2, TV3` (khớp đúng đáp án đã biết; DCM/PVT = T+2, DRI/POW = T+3).

| | Plan đã xét hôm đó | Đưa nhầm T+2/T+3 vào plan hôm nay | Bỏ sót T+1 |
|---|---|---|---|
| **SpaceX** | APF, TV2 | *không* | **MAC, TV3** |
| **ZaloPay** | DCM, DRI, POW, TV2 | **DCM (T+2), DRI (T+3), POW (T+3)** | **APF, MAC, TV3** |

**Phát hiện phụ, ngoài phạm vi dispatch: cả HAI plan đều thiếu, không chỉ ZaloPay.** SpaceX bỏ sót MAC
và TV3 — cả hai là T+1 hợp lệ. Cả hai mang cờ đỏ `THANH_KHOAN_CHET, NGOAI_UNIVERSE`, nên **rất có thể
loại chúng là đúng**; nhưng plan không ghi lại việc đã xét, nên không phân biệt được "đã xét rồi loại"
với "không thấy". Script buộc chúng xuất hiện trong `due_today` kèm cờ đỏ ⇒ phải nói rõ giữ hay bỏ.

Sửa được: **3 lệnh sai + 3 bỏ sót** ở ZaloPay, **2 bỏ sót** ở SpaceX.

### 5.2 Lăng kính ngành — signal 2026-07-27 → plan 2026-07-28

| Mã | Script | `plan_SpaceX_2026-07-28.json` (bên làm đúng) | `plan_ZaloPay_2026-07-28.json` (bên làm thiếu) |
|---|---|---|---|
| EVF | CHEAP → `KHONG_SKIP_VI_FLOOR_FAIL` · P/B 0,91 · ROE_TTM 9,6% | "FLOOR_FAIL nhưng P/B+ROE screen: P/B 0,91 cheap <1,8, ROE_TTM 9,6% ≥ 8% → CHEAP" | `"FLOOR_FAIL — skip"` |
| PSI | CHEAP → `KHONG_SKIP_VI_FLOOR_FAIL` · P/B 0,75 · ROE_TTM 8,8% | "…P/B 0,75 cheap, ROE_TTM 8,8% → CHEAP" | `"FLOOR_FAIL — skip"` |
| VCI | CHEAP → `KHONG_SKIP_VI_FLOOR_FAIL` · P/B 1,33 · ROE_TTM 9,2% | "…P/B 1,33 cheap, ROE_TTM 9,2% → CHEAP" | `"FLOOR_FAIL — skip"` |

Script **trùng từng con số** với bên làm đúng (không chỉ trùng nhãn CHEAP) và **đảo ngược** kết luận
sai của bên làm thiếu. Trên cùng CSV, `--floor-fail-only` còn cho ra đủ 3 loại quyết định — RICH →
`SKIP_CO_CAN_CU` (AGR P/B 1,14 ROE 6,6%; FTS P/B 1,86; HCM P/B 2,36) và fallback 8L →
`CAN_NGUOI_QUYET` (AFX, PV2) — tức nó **không phải cỗ máy luôn nói CHEAP**.

---

## 6. Ranh giới & những gì CHƯA làm

- **Chưa wire vào pipeline dispatch.** `kb/context_planning_mini.md` chưa đổi. Đó là bước riêng SAU
  khi Mike/user duyệt §1-5 — đúng như dispatch yêu cầu.
- **Không sửa production nào**: `git status` chỉ thêm 4 file mới trong `mike/bin/`.
  `golive_recommend_v23.py`, `trading_bot/`, `alt_valuation_lens.py` **không đụng tới**.
- **Rủi ro thấp hơn hẳn việc PARK/L1 sáng nay**: hai script này **chỉ đọc**, không đụng tiền, không
  sinh lệnh, không đổi sizing. Đầu ra tệ nhất chỉ là một danh sách sai — và nó được đối chiếu ngay
  với plan thật ở §5.
- **Còn nợ (§2)**: A1 cash-discipline, A2 TV1-cash, A3 CAPIT slot VND, A4 exclude list. Cả 4 đều đã
  gây sự cố thật; A1 nặng nhất (3 lần/15 ngày).
- **Điểm dễ vỡ đã biết của Bước 3**: nếu ai đó đổi câu chữ trong `alt_valuation_lens.format_alt_lens()`
  mà không đổi regex, `_parse_lens` trả `None` ⇒ script rơi về nhánh live (có `caveat`) thay vì bịa
  verdict. Selfcheck §B bắt đúng tình huống này. Cách bền hơn là để `alt_valuation_lens` xuất thẳng
  dict thay vì để nơi khác parse chuỗi — nhưng đó là sửa production, ngoài phạm vi dispatch này.

---

## 7. File

| File | Vai trò |
|---|---|
| `mike/bin/filter_lag_entry_window.py` | MỚI — lọc cửa sổ entry LAG (chỉ đọc) |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | MỚI — 43/43 PASS |
| `mike/bin/sector_valuation_lens.py` | MỚI — lăng kính ngành cho FLOOR_FAIL (chỉ đọc) |
| `mike/bin/sector_valuation_lens_selfcheck.py` | MỚI — 51/51 PASS |
| `alt_valuation_lens.py` | **KHÔNG ĐỔI** — nguồn lăng kính thật, có từ 2026-07-20 |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | **KHÔNG ĐỔI** |
| `trading_bot/due_diligence.py` | **KHÔNG ĐỔI** |
