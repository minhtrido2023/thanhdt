# Gate CỨNG "Σ orders[] ≤ sức mua thật" — thiết kế + code + selfcheck (CHƯA WIRE)

Job `Taylor_20260804_133014` · 2026-08-04 · Taylor
Trạng thái: **VIẾT XONG + TEST XONG, CHƯA BẬT.** Production **KHÔNG bị đụng** (`git status`:
`bot_execute.py` sạch). Chờ Mike đọc lại + quant-skeptic duyệt.

Sản phẩm:
| File | Vai trò | Trạng thái |
|---|---|---|
| `trading_bot/plan_funding_gate.py` | module gate (mới, chưa ai import) | file mới, untracked |
| `plan_funding_gate_selfcheck.py` | selfcheck 33 test | 33/33 PASS |
| `mike/agents/Taylor/research/plan_funding_gate_bot_execute.patch` | patch wire vào `bot_execute.py` | **CHƯA ÁP**, `patch --dry-run` sạch |

---

## 1. XÁC NHẬN HIỆN TRẠNG — không phải 1 tầng WARN, mà **4 tầng đều không chặn**

Đọc `bot_execute.py` 140–540 + `trading_bot/plan.py` + `trading_bot/executor.py` +
`kb/context_execution_mini.md`. Kết luận:

| # | Tầng | Có luật? | Có chặn? | Bằng chứng |
|---|---|---|---|---|
| 1 | DollarBill (nơi VIẾT plan) | ✅ văn xuôi | ❌ | `context_planning_mini.md` dòng 84–112 — đã thủng 3 lần (07-23, 07-27, 07-28) |
| 2 | `bot_execute.py` shadow | ✅ code | ❌ **WARN_ONLY** | `_log_plan_buying_power_shadow` (dòng 156–218): chỉ `print` + 1 dòng CSV, **không có** `return`/`raise`/`continue` |
| 3 | `executor.py` | ⚠️ per-ORDER | ❌ **một phần** | dòng 1066 `get_cash() < need` → `WAIT_CASH` + `continue` — **bỏ qua LỆNH ĐÓ, chạy tiếp lệnh sau** |
| 4 | Mafee | ❌ **không có** | ❌ | grep `kb/context_execution_mini.md`: không có luật Σ orders ≤ cash ở bất kỳ hình thức nào |

**Cascade đầy đủ trong `main()` (dòng 355–479)** — mọi gate CHẶN đều nằm ở đây, và không cái nào
xét tiền: `load_plan` → `filter_excluded_tickers` → `net_offsetting_orders` → `cap_capit_orders`
→ `cap_lag_orders` → `filter_lag_rating_orders` → `apply_capit_lever` → `approval_block_reason`
(**chặn thật**, `continue` + exit 2) → account lock → `connect()` → `lever_live_preflight` →
`_log_plan_buying_power_shadow` (**WARN**) → `Executor(...)` → `run_session`.

**Tầng 3 nguy hiểm hơn "không có gate"**, vì nó tạo ảo giác an toàn: plan vượt tiền vẫn khớp N
lệnh đầu (theo `priority`), phần còn lại treo `WAIT_CASH`. Đó **chính là** hành vi
"list-rồi-đợi-tiền" mà luật cấm — không phải cơ chế chặn nó.

**Xác nhận shadow log rỗng thật**: `data/plan_buying_power_shadow_log.csv` có **đúng 1 dòng** kể
từ 2026-07-29 (yêu cầu thiết kế là ≥10 phiên trước khi bàn ACTIVE ⇒ theo tiêu chí đó, gate P0 còn
cách ACTIVE rất xa).

---

## 2. PHÁT HIỆN QUAN TRỌNG NHẤT — dòng shadow log DUY NHẤT là **FALSE POSITIVE**

```
2026-07-29,SpaceX,5820000,0,dnse:ppse.pp0Buy@TV1,true      ← would_block=true
```

Truy `data/execution_logs/dnse_raw_2026-07-29.jsonl` (nguồn có thẩm quyền, §6):

| Giờ | Sự kiện | Nội dung |
|---|---|---|
| 09:15:14 | `loan_packages_resolve` | TV1: default=**1841**, valid_ids=**[1122]**, resolved=**1122** |
| 09:15:15 | `place_order` | TV1 100cp @19.600, `loan_package_id=1122` → DNSE **NHẬN** (id 36241) |
| 09:15:14 | `balances` | `availableCash = 10.412.823đ` (dư tiền, plan chỉ 5,82M) |
| 13:00:02 | `ppse` (shadow log) | **không truyền** `loan_package_id` → gói default 1841 → `pp0Buy=0` |

Gói 1841 là gói mainboard, **không hợp lệ cho TV1 trên UPCOM** ⇒ `pp0Buy=0` là **hiện vật đo
đạc**, không phải hết tiền. **Nếu bật gate naive (1 lần query `pp0Buy` bằng gói default) thì ngày
2026-07-29 nó đã CHẶN OAN TOÀN BỘ plan SpaceX.** Tỉ lệ: 1/1 dòng dữ liệu lịch sử là báo động giả.

→ Đây là ràng buộc thiết kế cứng, không phải chi tiết phụ.

---

## 3. THIẾT KẾ GATE

**Vế phải = sức mua ĐO ĐƯỢC (`ppse.pp0Buy`), không phải cash tĩnh** — tôn trọng nguyên vẹn
quyết định user 16:16 ICT 07-28 (từ chối `Σ orders ≤ cash_vnd` vì hệ có dùng margin). `pp0Buy`
đã gồm hạn mức vay của gói đang dùng + tiền bán chờ về T+0 ⇒ chỉ bắt "vốn CHƯA TỒN TẠI", không
cấm đòn bẩy.

```
need_g = Σ(lệnh mua nhóm g) qty × ref_price × (1 + 0,00075)      # phí thật 0,075%
U      = Σ_g  need_g / pp0Buy_g
CHẶN khi U > 1,0        (đúng `≤` — hoà đúng bằng sức mua KHÔNG chặn)
```

- **Nhóm = gói vay hiệu lực**, giải **đúng cách `place_order` giải**: `o.loan_package_id` →
  `cash_only` ⇒ `broker._resolve_loan_package_id(ticker)` → default. Đây là phần vá lỗi §2.
- Mọi phiên thường lệ (tất cả lệnh gói default) → rút gọn về đúng `Σ need ≤ pp0Buy`.

**§3 của dispatch (kiến trúc injector) đã thoả về mặt cấu trúc**: gate đọc `pp0Buy`/`get_cash()`
**sống từ DNSE tại thời điểm `bot_execute.py` chạy (09:05 sáng T+1)** — sau khi injector 20:30
đêm trước đã trừ tiền xong. Gate **không đọc bất kỳ con số cash nào từ plan JSON**, và điều đó
còn được bảo đảm cứng: `TradePlan` **không có field cash nào cả** (chỉ `nav_basis` = NAV).

### Khi không đo được `pp0Buy` (None hoặc ≤0) — CẬN NGOÀI, không fail-closed máy móc

Fail-closed ở đây sai chiều (ca TV1 chứng minh "đo không được" xảy ra trên plan HỢP LỆ, và chặn
oan có phí thật: lỡ deadline vào lệnh LAG T+1/T+2). Cách xử:

```
bound = (availableCash + Σ lệnh BÁN trong plan) × 3,0     # đòn bẩy tối đa thật 2× ⇒ biên 50%
Σ need > bound  → CHẶN        (mức "vốn không tồn tại", đòn bẩy không giải thích nổi)
ngược lại       → UNVERIFIED: KHÔNG chặn, nhưng BÁO TO (bus + Discord + Telegram)
```

Đối chiếu **3 mốc dữ liệu THẬT** (đều là replay trong selfcheck, không phải giả định):

| Ngày | Σ mua | cash thật | bound | Verdict | Đúng? |
|---|---|---|---|---|---|
| 07-27 SpaceX (`funding_required`) | 460,7M | 12,4M | 37,2M | **BLOCK** | ✔ sự cố thật |
| 07-28 SpaceX ("user sẽ nạp 136M") | 146,5M | 10,41M | 31,2M | **BLOCK** | ✔ sự cố thật |
| 07-29 SpaceX (TV1) | 5,82M | 10,41M | 31,2M | KHÔNG chặn | ✔ false positive |
| 07-28 ZaloPay (xử lý ĐÚNG) | 25,0M | ppse 25,54M | — | OK | ✔ không phá plan đúng |

`pp0Buy=0` vì **hết tiền thật** vẫn bị bắt: lúc đó cash≈0 ⇒ bound≈0 ⇒ Σ need > bound → CHẶN.

### Hành vi khi CHẶN
**Không đặt BẤT KỲ lệnh nào** của account đó (thực thi một phần chính là thứ luật cấm) → alert
bus `error:PLAN_FUNDING_GATE_BLOCK` + Discord Trading Daily + Telegram → `continue` → **exit 3**.
Account khác trong cùng process **vẫn chạy bình thường**. Đúng khuôn `approval_block_reason()`
đã có sẵn trong chính file này (exit 2). `run_bot.sh` coi mọi rc≠0 là lỗi ⇒ tự bắn Discord ❌ +
`ops_autofix` escalate. Gate read-only (1 lần gọi `ppse`/nhóm), không side-effect (§5 an toàn).

**Vị trí trong cascade**: ngay sau `_log_plan_buying_power_shadow`, ngay trước `Executor(...)` —
tức SAU toàn bộ bộ lọc/trần/đòn bẩy (Σ là tập lệnh THẬT SỰ sắp đặt), SAU `connect()` và SAU
`lever_live_preflight` (bước này có thể GỠ đòn bẩy ⇒ đổi gói vay ⇒ đổi sức mua).

---

## 4. VERIFY (theo skill `verify-before-done`)

**`plan_funding_gate_selfcheck.py` — 33/33 PASS**, phủ đúng 3 ca dispatch yêu cầu + 11 ca khác:
vi phạm→BLOCK · hợp lệ→OK · **biên `==` → KHÔNG chặn** · thiếu 1đ → CHẶN · phí 0,075% có vào Σ ·
đa gói vay · replay TV1 07-29 · 3 nhánh không-đo-được · replay 07-27 + 07-28 + ZaloPay-làm-đúng ·
chỉ-bán/paper/rỗng → SKIPPED · broker ném exception → không nổ · `get_cash()` cũng lỗi → cash=0
→ BLOCK (fail-safe, không đoán có tiền).

**Phụ thuộc môi trường**: gate **không** đọc TZ / ngày giờ / credential / cache / file nào.
Selfcheck dùng broker stub, không mạng, không ghi file. Chạy lại độc lập:
- `env -u TZ TZ=America/New_York`, cwd=`/tmp` → **33/33 PASS**
- `env -u TZ`, cwd=`/` → **33/33 PASS**

**Test tích hợp trên dữ liệu THẬT** (`load_plan` thật + `PlannedOrder` thật, 72 file plan trong
`data/trade_plans/`):
- sức mua = ĐÚNG BẰNG Σ mua (biên) → **OK 44 / SKIPPED 27 / BLOCK 0 / UNVERIFIED 0** — gate
  không chặn oan bất kỳ plan thật nào.
- sức mua = 1/2 Σ mua → **44/44** plan có lệnh mua bị CHẶN — gate thật sự nổ.
- 1 file không load được (`SpaceX_2026-07-06_v1_superseded_11name`, thiếu `ref_price`) — lỗi
  **có sẵn từ trước**, của `load_plan`, không liên quan gate.

**Patch**: `patch --dry-run` sạch; bản đã vá `py_compile` OK; chạy end-to-end thật
(`--date 1999-01-01`, nhánh không-có-plan) → import mới resolve, rc=0, không crash. File probe
tạm đã xoá.

**Production untouched**: `git status` — `bot_execute.py` sạch, `trading_bot/plan.py` sạch.
(`trading_bot/executor.py` có sửa dở của **người khác**, mtime 10:05 ICT hôm nay, trước phiên
này — tôi không đụng.)

---

## 5. CÒN THIẾU / CẦN QUYẾT

1. **`estimated_cost_vnd` không tồn tại.** Dispatch nói `Σ(orders[].estimated_cost_vnd +
   fee_est_vnd)`, nhưng `PlannedOrder` **không có** field đó và `load_plan()` **lọc bỏ** mọi field
   lạ. Nguồn chuẩn tắc duy nhất = `qty × ref_price` (`PlannedOrder.value`). Gate dùng cái này.
2. **Quyết định thiết kế cần Mike/quant-skeptic phán**: nhánh `UNVERIFIED` **không chặn**. Tôi
   chọn vậy vì 1/1 điểm dữ liệu lịch sử của nhánh này là false positive, và chặn oan có phí thật.
   Ai muốn siết thành fail-closed thì đổi 1 dòng — nhưng phải chấp nhận rủi ro chặn oan cả plan.
3. **`FALLBACK_LEVERAGE_MULT = 3,0` là tham số phán đoán**, không phải số đo. Neo vào
   initialRate 0,5 (đòn bẩy 2×) + 50% biên. Bắt được cả 3 sự cố (14×–37×) với biên rất rộng.
4. **Tầng 4 (Mafee) vẫn trống.** Gate này ở `bot_execute.py` = đường đặt lệnh thật nên đã phủ
   được đường sống; nhưng `kb/context_execution_mini.md` nên thêm 1 mục trỏ về gate này để Mafee
   biết luật tồn tại (đề xuất, chưa làm — sửa file `kb/` cần theo §13 `.proposed`).
5. **Tầng 3 (`executor.py:1066` WAIT_CASH)** giữ nguyên — đúng vai trò của nó (lưới per-order khi
   tiền biến động trong phiên). Nó chỉ sai khi bị coi là gate cấp plan; gate mới đứng trước nó.

---

## 6. VÒNG 2 — sửa lỗi quant-skeptic REFUTED (job `Taylor_20260804_143001`, 2026-08-04)

**Verdict vòng 1: REFUTED (confidence medium).** `killer_objection` đúng và cụ thể — không phải
nghi ngờ chung chung.

### 6.1 Lỗi thật là gì

`_effective_loan_package()` tuyên bố "giải ĐÚNG cách `place_order` giải" nhưng **chỉ đúng cho một
trong hai nhánh**:

| nhánh | `place_order` (brokers.py) làm gì | gate vòng 1 làm gì | hệ quả |
|---|---|---|---|
| `cash_only` | `_resolve_loan_package_id(symbol)` (dòng 552-591) | ✅ gọi đúng hàm đó | đúng |
| `order.loan_package_id` (đòn bẩy CAPIT) | `_validate_lever_package(symbol, want)` (dòng **629-644**) → gói không hợp lệ cho MÃ ĐÓ ⇒ **HẠ về gói default account** | ❌ tin thẳng id lệnh khai báo | **đo THỪA sức mua** |

Gói CAPIT 1840 có `initialRate` 0,5 ⇒ sức mua **gấp đôi** gói default 1841. Gate đo bằng 1840
trong khi lệnh thật khớp bằng 1841 ⇒ tưởng còn gấp đôi tiền ⇒ **cho qua đúng loại plan
"list-rồi-đợi-tiền" mà gate sinh ra để chặn**, chỉ khác nhánh code. Đây là rủi ro **DƯỚI-chặn**
(ngược chiều với false positive TV1 mà module đã lo rất kỹ).

Nhánh này đang **tắt mặc định** (`capit_margin_lever` DISABLED) nên chưa gây hại — nhưng nó thật
ngay khi bật đòn bẩy CAPIT, và **cả 33 case selfcheck vòng 1 không hề chạm tới nó** (mọi order
stub đều `loan_package_id=None`). Đó là lý do lỗi sống sót qua "33/33 PASS".

### 6.2 Đã sửa gì

`trading_bot/plan_funding_gate.py :: _effective_loan_package()` — nhánh `lp is not None` nay gọi
`broker._validate_lever_package(order.ticker, lp)` và dùng **giá trị nó trả về**, đúng như
`place_order` dùng (hợp lệ → giữ 1840; không hợp lệ → gói default account). Thêm
`_account_default_package(broker)` = `broker.client.loan_package_id` — ĐÚNG giá trị fallback mà
`_validate_lever_package` trả về, không tự chế.

Ba nhánh biên, tất cả chọn chiều **fail-safe = đo bằng gói NHỎ HƠN** (thà chặn/under-deploy còn
hơn để lệnh vay vượt mức đi ra):
- broker không có `_validate_lever_package` (paper/broker khác) → gói default account;
- hàm ném exception (bản thân nó đã tự nuốt mọi lỗi mạng) → gói default account;
- hợp lệ → giữ nguyên gói đòn bẩy, **không hạ oan** (case O1 canh đúng chiều này).

Không sửa/đơn giản hoá logic của `place_order`; gate chỉ *gọi lại* chính hàm đó. Cả
`_resolve_loan_package_id` lẫn `_validate_lever_package` đều **cache theo `(symbol[, want])`
trong phiên** ⇒ giá trị gate đo và giá trị `place_order` dùng **không thể lệch nhau**.

### 6.3 Test — chạy TRƯỚC khi sửa để chứng minh nó bắt đúng lỗi (skill `verify-before-done`)

Thêm mục **[O] 18 assertion** vào `plan_funding_gate_selfcheck.py` (33 → **51**), stub broker có
thêm `_validate_lever_package` + `client.loan_package_id`:

| case | tình huống | kỳ vọng |
|---|---|---|
| O1 | 1840 **hợp lệ** cho FPT | OK, đo bằng 1840, **không** hạ oan |
| **O2** ★ | 1840 **KHÔNG hợp lệ** cho SAB (bp 1840=200M, 1841=80M, Σ=100,075M) | **BLOCK**, đo bằng 1841, `buying_power=80M`, U≈1,2509 |
| O3 | broker không có `_validate_lever_package` | BLOCK (đo gói default) |
| O4 | hàm ném exception | không nổ, BLOCK (đo gói default) |
| O5 | plan hỗn hợp: FPT@1840 hợp lệ (0,50) + SAB bị hạ (0,60) | BLOCK, tách **2 nhóm** gói vay, U≈1,10 |

**Chạy TRƯỚC fix: 37 PASS / 14 FAIL — toàn bộ 14 FAIL nằm trong [O]**, O2 fail đúng như dự đoán
(`OK: Σ 100.075.000đ ≤ sức mua 200.000.000đ (50.0%)`). **Chạy SAU fix: 51 PASS / 0 FAIL.** 33 case
cũ không case nào đổi kết quả.

### 6.4 Verify đầy đủ

- `plan_funding_gate_selfcheck.py` → **51/51 PASS** (33 cũ + 18 mới).
- Độc lập môi trường: `env -u TZ TZ=America/New_York` cwd=`/tmp` → 51/51; `env -u TZ` cwd=`/` →
  51/51. Gate không đọc TZ/ngày giờ/credential/cache/file nào.
- **Replay plan THẬT** — `mike/agents/Taylor/plan_funding_gate_replay_probe.py` (probe vòng 1 đã
  xoá; bản này giữ lại để chạy lại được). 77 file trong `data/trade_plans/`, **72 load được**
  (45 có lệnh mua): sức mua = ĐÚNG Σ mua → **OK 45 / SKIPPED 27 / BLOCK 0** (không chặn oan plan
  thật nào); sức mua = 1/2 Σ mua → **BLOCK 45/45**. Chạy lại dưới `env -u TZ TZ=UTC` → y hệt.
  5 file không load được là lỗi **có sẵn của `load_plan`** (2 `bootstrap_book_snapshot_*` thiếu
  key `orders`, 2 `park_trim_*` thiếu 6 field bắt buộc, 1 `_superseded_11name` thiếu `ref_price`)
  — không liên quan gate. Probe chép từng file sang tmpdir dưới tên chuẩn rồi trỏ `PLAN_DIR` vào
  đó ⇒ mọi file đều đi qua **đúng bộ parse production**, không viết lại logic đọc plan.
- `py_compile` sạch cả 3 file.
- **Production KHÔNG đụng**: `git status` — `bot_execute.py` sạch, `trading_bot/plan.py` sạch,
  `trading_bot/brokers.py` sạch. `trading_bot/executor.py` vẫn là bản sửa dở của **người khác**
  (mtime 10:05 ICT, trước phiên này — không đụng). Patch `plan_funding_gate_bot_execute.patch`
  KHÔNG đổi và vẫn `patch --dry-run -p0` sạch (gate nằm CUỐI cascade, sau `apply_capit_lever` +
  `lever_live_preflight`, nên `order.loan_package_id` đã chốt khi gate đọc).

### 6.5 Trạng thái

**SẴN SÀNG cho quant-skeptic review VÒNG 2.** Mike tự dispatch `verify_finding.sh` — Taylor không
tự gọi. Gate vẫn **CHƯA WIRE** vào production (ranh giới giữ nguyên: patch riêng, `bot_execute.py`
không đụng lần này).
