# Domain-Constraint Layer — kiểm kê hiện trạng + phác thảo module

> Job `Taylor_20260729_015312` · Taylor (Quant/Algo) · 2026-07-29
> **Trạng thái: RESEARCH + DESIGN. KHÔNG có dòng code production nào bị sửa trong lần này.**
> Bối cảnh: talk "Why Agentic Systems Need Ontologies" (Frank Coyle, AI Engineer World's Fair
> 2026) — luận điểm: rủi ro thật của agent không phải "LLM suy luận sai" mà là **vi phạm một
> ràng buộc domain** ngay tại thời điểm gọi tool có side-effect không đảo ngược; văn xuôi
> (prompt/context-file) không đủ sức chặn, cần một lớp constraint hình thức đứng GIỮA plan
> LLM-authored và tool execution.

## 0. Kết luận sớm (đọc trước, 6 gạch đầu dòng)

1. **Hệ này ĐÃ CÓ một lớp ontology-ish khá dày, chỉ chưa gọi tên** — 12 guardrail cơ khí thật
   (fail-closed, chặn hành động chứ không "review bằng mắt"), đa số nằm đúng chỗ talk khuyến
   nghị: giữa `load_plan()` và broker API. Phần lớn được sinh ra sau một sự cố thật, có
   self-check riêng. Đây là điểm mạnh, không phải khoảng trống.
2. **Khoảng trống thật nằm ở KIẾN TRÚC, không ở số lượng rule**: các guardrail được gọi RẢI RÁC
   trong `main()` của `bot_execute.py` theo thứ tự thủ công, mỗi cái tự định nghĩa dạng trả về
   riêng (list dict khác schema), tự quyết fail-open/fail-closed riêng. Thêm rule thứ 13 = sửa
   `main()` lần nữa. Không có sổ cái nào liệt kê "tất cả ràng buộc đang hiệu lực".
3. **Đứt gãy nghiêm trọng nhất: tầng TÍN HIỆU và tầng THỰC THI không dùng chung ràng buộc.**
   Gate rating LAG (user chốt 07-27) chỉ sống ở `golive_recommend_v23.py`; chính docstring của
   nó ghi *"gate này KHÔNG có lưới an toàn ở executor"* (`lag_rating_filter.py:33-34`). Một plan
   LLM-authored viết tay lệnh LAG cho mã rating 4 sẽ đi thẳng ra broker.
4. **`data/trading_rules.json` — file "hạn mức" chính thức của hệ — KHÔNG được bất kỳ dòng code
   thực thi nào đọc.** `bot_execute.py` chỉ nhắc tên nó trong 1 comment. Các trần `name_cap_pct
   0.10`, `max_value_per_order_pct 0.05`, `max_daily_gross_pct 0.40`, `max_gross_exposure_pct
   1.50`, `neutral_parking 0.70 + risk_dial_override` hiện được enforce bằng câu *"Mafee
   hard-blocks"* — mà Mafee là agent LLM. Đây là prose-only ở đúng chỗ nguy hiểm nhất.
5. **Phải tách 2 LOẠI rule prose** — chỉ loại A thuộc phạm vi module này:
   **(A) runtime** (ràng buộc trên plan/order sắp thực thi → mechanize được bằng cổng validate);
   **(B) authoring-time** (§6 provenance, §9 data_registry, §11 cron_registry, §12 account_no —
   là kỷ luật khi VIẾT code, chỉ mechanize được bằng lint/pre-commit/self-check, không phải
   bằng cổng plan). Gộp chung 2 loại vào 1 module là sai kiến trúc.
6. **Ưu tiên theo tần suất tái phạm thật**: P0 = cash/funding discipline (3 lần / 6 ngày, tần
   suất TĂNG) — nhưng **phải viết dưới dạng CÓ ĐIỀU KIỆN (buying-power theo account), tuyệt đối
   không phải luật cấm cứng `orders ≤ cash`** — user đã từ chối đúng dạng cấm cứng đó lúc
   16:16 ICT 07-28 vì hệ sẽ dùng margin trong tương lai. Thiết kế dưới đây tôn trọng nguyên vẹn
   quyết định đó; nó KHÔNG mở lại đề xuất bị từ chối.

---

# NHIỆM VỤ 1 — Kiểm kê guardrail CƠ KHÍ đã có

Tiêu chí vào bảng: chặn/cắt một hành động **bằng code**, dựa trên một luật domain, không phụ
thuộc việc người/LLM có nhớ đọc rule hay không.

## 1.1 Bảng tổng hợp

| # | Cơ chế | File:line | Entity bảo vệ | Invariant enforce | Hành vi khi vi phạm |
|---|---|---|---|---|---|
| G1 | `filter_excluded_tickers()` | `trading_bot/plan.py:138`; gọi ở `bot_execute.py:297` | Account × Ticker | `order.ticker ∉ account.excluded_tickers` | **Loại lệnh** khỏi plan, trả list bị chặn để caller log. Không raise. |
| G2 | `_ghost_tickers()` | `trading_bot/executor.py:560`; dùng ở `:1040` (step), `:849`, `:966` | Order (idempotency) | Mọi lệnh sống/có fill ở broker phải có `oid` trong `state.json` | **Pause CẢ MÃ đó cho hết ngày**, không tự gộp vào state. Unpause = người sửa tay. Fail-safe-pause. |
| G3 | `approval_block_reason()` | `trading_bot/plan.py:509`; gọi ở `bot_execute.py:336` | Plan | `requires_user_approval ⇒ approved_by ≠ ∅` | **Từ chối cả account**, alert bus+Discord+Telegram (`bot_execute.py:49`), exit code 2. Normalize chuỗi `"None"/"null"/"false"`. |
| G4 | `cap_capit_orders()` | `trading_bot/plan.py:259`; gọi ở `bot_execute.py:317` | Order (CAPIT buy) | `qty×ref_price ≤ capit_adv_caps[account][ticker]` | **TRIM** xuống lô chẵn lớn nhất; **BLOCK** nếu artifact thiếu/schema cũ/`signal_date` lệch. Fail-closed. |
| G5 | `cap_lag_orders()` | `trading_bot/plan.py:363`; gọi ở `bot_execute.py:325` | Order (LAG buy) | `qty×ref_price ≤ 0.20×ADV×(1/N_live_accounts)` | **TRIM**; **BLOCK** khi ADV không đo được / ADV≤0 / dữ liệu cũ >30 ngày / không dựng được danh sách account live. Fail-closed. |
| G6 | `net_offsetting_orders()` | `trading_bot/plan.py:154`; gọi ở `bot_execute.py:310` | Plan (chuẩn hoá) | Không gửi 2 lệnh ngược chiều cùng mã/cùng ngày ra broker | Gộp thành 1 lệnh NET (hoặc 0 lệnh nếu net=0). Không chặn — chuẩn hoá. Có đối soát post-fill (`netting_recon.py`) fail-loud. |
| G7 | `_acquire_account_lock()` (fcntl) | `bot_execute.py:150`, gọi `:341` | Account × ngày | ≤1 process `bot_execute` cho mỗi (account, plan_date) | Bỏ qua account (không phải lỗi). Sinh sau sự cố double-buy 2026-07-02. |
| G8 | `_otp_flow_lock()` | `bot_execute.py:169` | Credential/token | 1 chu trình OTP tại một thời điểm cho mỗi file credentials | Blocking (chủ đích), reload token cache sau khi chờ. |
| G9 | `BOT_STOP` kill-switch | `config.py:13`; `executor.py:1135` | Toàn hệ | File tồn tại ⇒ dừng mọi thứ | Huỷ mọi lệnh treo mọi account rồi thoát. Cũng là hành động cuối của Spyros `risk_monitor.py:411`. |
| G10 | Sellable/T+2 cap | `executor.py:893-912` | Position | `qty_sell ≤ positions[ticker].sellable` | Không đặt lệnh, journal `WAIT_T2_SETTLEMENT`, thử lại chu kỳ sau. |
| G11 | Cash/ppse guard + participation quota | `executor.py:913-924` (cash), `:465`/`:491`/`:506` (`_child_qty`) | Account cash / Ticker liquidity | `child_value ≤ cash·(1+phí)` **và** `Σfleet_filled ≤ max_participation × KL/ADV20` | `WAIT_CASH` / `WAIT_QUOTA` — không đặt, không đoán. Quota chia CHUNG toàn fleet qua `shared`. |
| G12 | `_floor_guard_buy()` + `_extreme_regime` | `executor.py:810`, `:757`; dùng `:867-878` | Order (giá) | Không MUA khi quote cận sàn | `EXTREME_PAUSE`/`EXTREME_FLOOR_GUARD`, thử lại sau. (Gated bởi `extreme_regime_enabled` = paper-only hiện nay.) |

**Guardrail ở TẦNG TÍN HIỆU** (khác tầng, xem §1.3):

| # | Cơ chế | File:line | Invariant | Khi vi phạm |
|---|---|---|---|---|
| S1 | `lag_filter_low_rating()` | `lag_rating_filter.py:45`; gọi `golive_recommend_v23.py:592` | Ứng viên LAG phải có 8L rating ≤3 (point-in-time `time ≤ asof`) | **Loại thật** khỏi `lag_up`/`lag_recent`, ghi `status.json.lag_rating_excluded`. Fail-closed từng mã; **fail-OPEN khi cả truy vấn hỏng** (giữ danh sách + warning + `lag_rating_filter_error`). |
| S2 | `anomaly_excluded()` | `anomaly_gate.py:27`; gọi `golive_recommend_v23.py:281/658` | Mã có cờ bất thường còn hiệu lực (TTL 30 ngày) ∉ rổ CAPIT | Loại khỏi rổ, ghi `capit_dd_excluded`. Nguồn dùng chung cho production + 3 paper book. |
| S3 | `lag_filter_illiquid()` | gọi `golive_recommend_v23.py:585` | Ứng viên LAG phải đo được thanh khoản | Loại khỏi danh sách (có lưới G5 ở executor). |
| S4 | Trần `max_orders_per_day` / `max_daily_gross_value` | `trading_bot/strategies.py:422-429` | ≤60 parent order, ≤20B GTGD/ngày | Cắt bớt / cảnh báo. ⚠️ **Chỉ áp trong `V23Strategy`** — plan LLM-authored KHÔNG đi qua đây. |
| S5 | Episode-DD breaker, concentration, margin check | `mike/agents/Spyros/risk_monitor.py:219/350/362` | NAV drop ≥15% từ episode-entry ⇒ halt | Ghi bus + `BOT_STOP` + Telegram. Chạy hậu-kiểm (EOD), không ở đường lệnh. |

## 1.2 Đặc điểm chung — cái hệ này đã làm ĐÚNG

- **Fail-safe pause, không đoán**: G2/G4/G5/G10/G11 đều dừng và báo người thay vì tự suy diễn.
  Đúng `coding_guidelines.md §5`.
- **Enforce độc lập plan generator**: docstring G1/G4/G5 nói thẳng lý do tồn tại — *"không phụ
  thuộc vào việc plan generator (DollarBill/LLM) có nhớ hay không"*. Đây chính xác là luận điểm
  của talk, đã được nội bộ hoá từ trước.
- **Mỗi guardrail có self-check riêng**: `excluded_tickers_selfcheck.py`,
  `approval_gate_selfcheck.py`, `concurrent_lock_selfcheck.py`, `ghost_order_selfcheck.py`,
  `capit_participation_cap_selfcheck.py`, `lag_rating_filter_selfcheck.py`…
- **Chia tài nguyên dùng chung theo account** (G4/G5/G11): %ADV và participation là tài nguyên
  THỊ TRƯỜNG — mỗi account enforce full trần thì N account = N×trần. Bug này đã bị bắt và sửa.

## 1.3 Bốn khiếm khuyết kiến trúc (đây mới là thứ module mới cần giải quyết)

**K1 — Rải rác, không có sổ cái.** 5 guardrail tầng plan được gọi tuần tự trong `main()`
(`bot_execute.py:297→336`), thứ tự có ý nghĩa ngữ nghĩa (net TRƯỚC cap %ADV — chủ đích, ghi ở
`plan.py:180-186`) nhưng chỉ tồn tại dưới dạng thứ tự dòng code + comment. Không có nơi nào trả
lời được câu "hiện có bao nhiêu ràng buộc, cái nào đang bật, cái nào fail-open".

**K2 — Đứt gãy signal ↔ execution.** S1 (rating LAG) và S2 (anomaly) chỉ chặn ở bước SINH ứng
viên. Plan là JSON do LLM viết, có thể chứa bất kỳ mã nào. Kịch bản hỏng cụ thể: DollarBill (hoặc
người sửa tay plan) thêm `{"ticker":"MST","book":"LAG","side":"buy"}` → `filter_excluded_tickers`
không biết MST, `cap_lag_orders` chỉ kiểm ADV (MST ADV 15,5 tỷ — pass), `approval_block_reason`
pass nếu user đã duyệt → **lệnh đi ra broker dù MST rating 8L = 4, đúng thứ user vừa cấm 07-27**.
Rủi ro này được ghi nhận công khai trong chính docstring của gate (`lag_rating_filter.py:33-34`),
chưa ai đóng.

**K3 — `trading_rules.json` không có chân trong code.** File tự khai `owners: Taylor`,
`consumers: DollarBill (sizing), Mafee (hard-blocks), Spyros (kill-switch)`. Thực tế:
`risk_monitor.py` (Spyros) đọc vài ngưỡng ở tầng hậu-kiểm EOD; `bot_execute.py` **không đọc**.
Nghĩa là `name_cap_pct=0.10`, `max_value_per_order_pct=0.05`, `max_daily_gross_pct=0.40`,
`max_gross_exposure_pct=1.50` và toàn bộ cơ chế `risk_dial_override` (neutral parking ≠0.70 phải
kèm 2 field xác nhận) hiện **chỉ được thi hành bởi một agent LLM đọc file và tự nhớ**. Đây là
định nghĩa sách giáo khoa của vấn đề mà talk mô tả — và nó nằm ở file được gọi là "single source
of truth for risk/sizing limits".

**K4 — Không có invariant ở cấp PLAN (chỉ có cấp ORDER).** Mọi guardrail hiện tại xét từng lệnh
riêng. Không có gate nào xét được các mệnh đề dạng "tổng plan": Σ`orders.value` vs sức mua,
Σ theo mã vs name-cap, Σ gross vs NAV. Đây chính là hình dạng của sự cố tái diễn 3 lần
(funding/cash discipline) — nó **không thể** bị bắt bởi bất kỳ check per-order nào.

---

# NHIỆM VỤ 2 — Kiểm kê rule AN TOÀN-QUAN TRỌNG chỉ tồn tại dạng PROSE

## 2.1 Phân loại trước khi liệt kê

| Loại | Bản chất | Mechanize bằng gì | Thuộc module này? |
|---|---|---|---|
| **A. Runtime** | Ràng buộc trên plan/order/account sắp thực thi | Cổng validate trong đường lệnh | ✅ CÓ |
| **B. Authoring-time** | Kỷ luật khi VIẾT code/query mới | lint / pre-commit / self-check / CI | ❌ KHÔNG (vehicle khác) |

Bỏ qua ranh giới này là lỗi thiết kế thường gặp: §9 (data_registry) và §12 (account_no) **không
thể** enforce ở cổng plan — lúc plan chạy thì code sai đã viết xong từ lâu.

## 2.2 Loại A — runtime, prose-only (ứng viên promote thật sự)

| ID | Rule | Nguồn prose | Đã vi phạm thật? | Ghi chú mechanize |
|---|---|---|---|---|
| **A1** | `orders[]` chỉ chứa lệnh mà tổng ≤ **sức mua thực có ngay bây giờ**, không giả định vốn tương lai | `kb/context_planning_mini.md:79-102` | **3 lần** (07-23, 07-27, 07-28) — `INCIDENTS.md:4080` | ⚠️ User TỪ CHỐI validator cấm cứng (16:16 07-28). Phải viết dạng **buying-power CÓ ĐIỀU KIỆN** — xem §3.6. |
| **A2** | Ứng viên/lệnh LAG phải có 8L rating ≤3 | `context_planning_mini.md` "LAG entry — GATE CỨNG"; user chốt 07-27 | 2 near-miss (TRC 07-23, MST 07-27) — **bắt được ở tầng signal**, chưa lọt tới lệnh | Thiếu đúng "lưới executor" mà chính docstring gate thừa nhận. Chi phí thấp nhất / giá trị cao. |
| **A3** | `name_cap_pct ≤ 0.10`, `max_value_per_order_pct ≤ 0.05`, `max_daily_gross_pct ≤ 0.40`, `max_gross_exposure_pct ≤ 1.50` | `data/trading_rules.json` `/sizing`, `/execution_limits` + `_meta.consumers.Mafee = "hard-blocks"` | Chưa ghi nhận vi phạm lọt lệnh | Không dòng code nào đọc. `max_orders_per_day`/`max_daily_gross_value` chỉ áp trong `V23Strategy` (S4), plan LLM-authored bỏ qua. |
| **A4** | NEUTRAL parking ≠0.70 ⇒ plan phải mang `risk_dial_confirmed_by_user` **và** `risk_dial_warning_acknowledged` (có số liệu job 130720), nếu thiếu → BLOCK | `trading_rules.json` `/neutral_parking/risk_dial_override` | 1 lần dạng tiền thân (go-live 07-01: `target_equity_pct=93.8%` viết thẳng vào plan JSON, user bắt bằng cách hỏi trực tiếp) | Rule đã viết sẵn dạng gần-hình-thức (2 field bắt buộc, điều kiện rõ) — dịch sang code gần như 1-1. Ví dụ mẫu tốt nhất trong file. |
| **A5** | Lệnh mua mã "RICH ∧ robust" theo DCF phải có `dcf_override_reason` | `plan.py:31` (comment), `strategies.py:166` (chỉ in cảnh báo) | Chưa ghi nhận | Hiện là WARN thuần thông tin. Có thể nâng lên "block trừ khi có lý do" — cần user quyết, không tự nâng. |
| **A6** | Không đề xuất/giả định rút "Trứng vàng" (off-book = 0, đã đóng vĩnh viễn) | `kb/current_ops.md`, `context_planning_mini.md` | Là **lần 1** của chuỗi A1 | Đây là trường hợp riêng của A1 khi tổng quát hoá đúng ⇒ không cần rule riêng. |
| **A7** | Note lệnh LAG mới lúc regime dễ vỡ phải công bố rủi ro BEAR-liquidation (`w_LAG=0`) | `context_planning_mini.md` (thêm 07-27) | Chưa | Ràng buộc trên NỘI DUNG văn bản → chỉ WARN được, không nên block. Ưu tiên thấp. |

## 2.3 Loại B — authoring-time, prose-only (KHÔNG thuộc module này)

| ID | Rule | Guideline | Đã vi phạm thật? |
|---|---|---|---|
| B1 | Số liệu client-facing phải truy nguyên tới nguồn authoritative (broker fill), cross-check 2 nguồn | §6 | **CÓ** — 2026-07-03 báo cáo tuần đọc `ref_px_approx` làm cost basis. Đã có pipeline 3 script bắt buộc. |
| B2 | Dữ liệu same-day phải lấy DNSE, không BQ | §6 bright-line | **CÓ** — 2026-07-09, 2/4 lệnh định giá bằng close BQ cũ (+5,7% lệch) |
| B3 | Tra `kb/data_registry/` trước khi wire nguồn dữ liệu mới | §9 | **CÓ** — SIGNAL_V11 base-leak 07-11: 4 consumer đọc bảng TRAP `vnindex_5state`, paper book vào 6 mã trên tín hiệu giả |
| B4 | Tra `kb/cron_registry.md` + trả lời "4 câu hỏi bắt buộc" trước khi đổi lịch cron | §11 | **CÓ** — C1 CRITICAL 07-12: publish script đọc cache T-1 suốt ~2,5 tuần |
| B5 | Lọc `account_no` NGAY dòng đầu khi đọc file dữ liệu dùng chung | §12 | **CÓ 3 LẦN** — `daily_nav_snapshot` (07-06), `eod_trading_report` (07-21), `reconcile_equity`+`verify_account_snapshot` (07-19) |

**Nhận xét quan trọng:** B5 tái phạm đúng 3 lần — bằng A1 — nhưng **cách chữa hoàn toàn khác**:
B5 là bug trong code người/agent viết, chỉ có thể chặn bằng một self-check/lint chạy lúc commit
("chạy script cho cả 2 account trong 1 ngày có giao dịch, 2 kết quả phải KHÁC nhau" — đã ghi sẵn
trong §12, chưa ai tự động hoá). Nếu module constraint này cố ôm B5, nó sẽ phình ra thành một
framework không ai bảo trì. **Khuyến nghị: tách thành đề xuất riêng** (`bin/` self-check +
pre-commit hook), không nhét vào đây.

## 2.4 Case A1 — phân tích riêng (ràng buộc thiết kế cứng nhất)

Ba lần, ba vỏ bọc, mỗi lần fix đúng vỏ bọc trước:

| Lần | Ngày | Hình thức | Fix sau đó |
|---|---|---|---|
| 1 | 07-23 | Coi việc rút Trứng vàng (off-book) như vốn đã có | Cấm đề xuất rút Trứng vàng |
| 2 | 07-27 | Field `funding_required: true` (7/8 lệnh, 460,7M vs cash 12,4M) | Cấm field `funding_required` |
| 3 | 07-28 | **Văn xuôi tự nhiên**: "user sẽ nạp 136M" (4 lệnh 146,5M vs cash 10,41M) | Mở rộng thành câu tự-kiểm-tra không phụ thuộc hình thức |

Đây là minh hoạ chính xác luận điểm của talk: **cấm một hình thức diễn đạt không đóng được lỗ
hổng ngữ nghĩa**. Bộ sinh xác suất sẽ tìm ra vỏ bọc thứ 4 (bảng số, footnote, ước tính gộp).
Cả 3 lần đều được một bước QA thứ hai **tình cờ** chạy bắt được trước khi tới user — an toàn nhờ
may, không nhờ cơ chế.

**Ràng buộc thiết kế bắt buộc (user, 16:16 ICT 07-28):** đã CHỦ ĐỘNG từ chối validator code-level
dạng `orders ≤ cash_vnd`, lý do: hệ sẽ dùng margin/vay trong tương lai, luật cấm tuyệt đối sẽ sai
khi đó. **Thiết kế dưới đây không đảo ngược quyết định này.** Cách hoà giải: bất biến không phải
là "≤ tiền mặt" mà là **"≤ sức mua ĐO ĐƯỢC của account tại thời điểm này"**, trong đó sức mua là
một hàm phụ thuộc account (cash-only ⇒ `ppse` live; margin ⇒ `ppse` đã bao gồm hạn mức vay của
broker) và **luôn đọc từ broker sống, không bao giờ từ giả định**. Cùng một invariant phục vụ cả
hai chế độ; cái bị cấm là *vốn chưa tồn tại*, không phải *đòn bẩy*.

---

# NHIỆM VỤ 3 — Phác thảo module `trading_bot/constraints.py`

## 3.1 Nguyên tắc thiết kế

1. **Python thuần + dataclass** (khớp `trading_bot/*.py` hiện có). Pydantic là **tuỳ chọn**, chỉ
   nếu muốn validate schema plan JSON — không bắt buộc, không thêm dependency nếu chưa cần.
   **Không OWL/RDF/SPARQL** — không consumer nào trong hệ tiêu thụ RDF; chi phí ròng âm.
2. **Không viết lại guardrail đã chạy đúng.** Module là **registry + orchestrator**: bọc G1/G4/G5/
   G3 hiện có thành các `Constraint` (adapter mỏng, giữ nguyên hàm gốc), rồi thêm rule mới cùng
   khuôn. Giữ nguyên hành vi từng hàm — chuyển sang registry KHÔNG được đổi một byte kết quả
   (kiểm chứng bằng A/B "0 đồng lệch" như mọi cutover trước).
3. **Một cổng duy nhất**, đúng mô hình `filter_excluded_tickers` đã làm đúng: gọi ở đúng 1 chỗ
   trong `bot_execute.py`, không rải rác.
4. **Constraint khai báo được, có điều kiện, tắt/bật được** — bắt buộc theo ràng buộc §2.4.
   Mỗi constraint có `applies_to(ctx) → bool` và `status ∈ {ACTIVE, WARN_ONLY, DISABLED}`.
5. **Fail-mode khai báo tường minh**, không ẩn trong `try/except`: `FAIL_CLOSED` (lỗi ⇒ chặn) hay
   `FAIL_OPEN` (lỗi ⇒ cho qua + cảnh báo bắt buộc hiển thị). Hôm nay hai kiểu này lẫn lộn và chỉ
   phân biệt được bằng cách đọc docstring từng hàm.
6. **Vi phạm ⇒ tạm dừng + báo người, không tự sửa** (`coding_guidelines §5`).

## 3.2 Entities

Không phát minh mô hình mới — hình thức hoá đúng cái đang tồn tại:

```python
@dataclass(frozen=True)
class AccountCtx:            # từ config.load_accounts() + broker sống
    label: str               # "SpaceX" | "ZaloPay" | ...
    mode: str                # "paper" | "live"
    broker: str              # "dnse" | "phs"
    excluded_tickers: tuple[str, ...]
    margin_enabled: bool     # loan_package_id là gói vay thật (≠ gói tiền mặt)
    nav_vnd: float | None    # NAV để tính các trần %NAV (None ⇒ rule %NAV không áp dụng được)
    buying_power_vnd: float | None   # ĐỌC TỪ BROKER SỐNG (ppse), không phải giả định
    buying_power_source: str         # "dnse:ppse" | "dnse:availableCash" | "unavailable"

@dataclass(frozen=True)
class TickerFacts:           # tra lười (lazy), chỉ khi có rule cần
    ticker: str
    rating_8l: int | None    # fa_ratings_8l, point-in-time time ≤ asof
    adv_vnd: float | None    # Volume_3M_P50 × Close (due_diligence.adv_vnd)
    anomaly_flagged: bool    # anomaly_gate.anomaly_excluded(asof)
    in_universe: bool | None # universe_pit_q

# Order / Plan: DÙNG LẠI PlannedOrder + TradePlan (plan.py:17/47), không tạo type song song.

@dataclass
class ValidationCtx:
    plan: TradePlan
    account: AccountCtx
    asof: date
    facts: TickerFactsProvider   # cache, lazy, fail-safe → None khi không tra được
```

## 3.3 Constraint & Verdict

```python
class Remedy(Enum):
    BLOCK_ORDER = "block_order"   # loại 1 lệnh, phần còn lại chạy tiếp
    TRIM_ORDER  = "trim_order"    # giảm qty xuống mức hợp lệ
    BLOCK_PLAN  = "block_plan"    # từ chối cả account (như approval gate hiện tại)
    WARN        = "warn"          # ghi + hiển thị, không đổi hành vi

@dataclass(frozen=True)
class Constraint:
    id: str                       # "LAG_RATING_MAX", "PLAN_BUYING_POWER", ...
    scope: str                    # "order" | "plan"
    entity: str                   # "Order" | "Plan" | "Account"
    invariant: str                # 1 dòng, đọc-được-bởi-người, in ra trong mọi log vi phạm
    remedy: Remedy
    fail_mode: str                # "closed" | "open"
    status: str                   # "ACTIVE" | "WARN_ONLY" | "DISABLED"
    applies_to: Callable[[ValidationCtx], bool]   # ĐIỀU KIỆN — trái tim của yêu cầu user
    check: Callable[..., list[Violation]]
    evidence: str                 # job id / incident / commit đã hợp thức hoá rule này

@dataclass(frozen=True)
class Violation:
    constraint_id: str
    order_id: str | None
    ticker: str | None
    detail: str                   # con số thật: "Σorders 146.500.000đ > buying_power 10.410.000đ"
    remedy: Remedy
    qty_after: int | None         # cho TRIM
```

Bảng constraint là **dữ liệu**, không phải chuỗi `if` — thêm rule = thêm 1 entry + 1 self-check,
không sửa `main()`. Đây là điểm khác biệt thật so với hiện trạng (K1).

## 3.4 Invariant — phát biểu hình thức cho từng rule

**Đã cơ khí hoá (bọc lại, giữ nguyên hành vi):**

| id | Invariant | Remedy | fail_mode | applies_to |
|---|---|---|---|---|
| `ACCOUNT_EXCLUDED_TICKER` | `order.ticker ∉ account.excluded_tickers` | BLOCK_ORDER | closed | `len(excluded)>0` |
| `CAPIT_ADV_CAP` | `order.value ≤ caps[account][ticker]` | TRIM (BLOCK khi artifact hỏng) | closed | `order.book=="CAPIT" ∧ side=="buy"` |
| `LAG_ADV_CAP` | `order.value ≤ 0.20·ADV·share` | TRIM (BLOCK khi ADV n/a) | closed | `order.book=="LAG" ∧ side=="buy"` |
| `PLAN_APPROVAL` | `requires_user_approval ⇒ approved_by ≠ ∅` | BLOCK_PLAN | closed | `len(orders)>0` |
| `ORDER_IDEMPOTENCY` | ∄ lệnh broker sống/có-fill ngoài `state.json` | PAUSE_TICKER | closed | luôn (tầng executor, **giữ nguyên tại chỗ** — xem §3.5) |

**Ứng viên promote (theo thứ tự ưu tiên §3.7):**

| id | Invariant | Remedy | fail_mode | applies_to |
|---|---|---|---|---|
| `PLAN_BUYING_POWER` | `Σ{o.value : o.side=="buy"} ≤ account.buying_power_vnd` | BLOCK_PLAN | **closed nếu đo được sức mua; BLOCK kèm lý do "không đo được" nếu không** | `account.mode=="live" ∧ buying_power đo được` — xem §3.6 |
| `LAG_RATING_MAX` | `order.book=="LAG" ⇒ facts.rating_8l ≤ 3` | BLOCK_ORDER | closed từng mã / **open khi cả nguồn hỏng** (đồng bộ S1) | `order.book=="LAG" ∧ side=="buy"` |
| `NAME_CAP` | `(pos_value + Σ buy cùng mã) ≤ name_cap_pct · NAV` | TRIM → BLOCK | closed | `nav_vnd ≠ None` |
| `ORDER_VALUE_CAP` | `order.value ≤ max_value_per_order_pct · NAV` | TRIM | closed | `nav_vnd ≠ None` |
| `DAILY_GROSS_CAP` | `Σ|order.value| ≤ max_daily_gross_pct · NAV` | BLOCK_PLAN | closed | `nav_vnd ≠ None` |
| `GROSS_EXPOSURE_CAP` | `(stock_value + Σbuy − Σsell)/NAV ≤ max_gross_exposure_pct` | BLOCK_PLAN | closed | `account.margin_enabled` |
| `RISK_DIAL_OVERRIDE` | `park ≠ 0.70 ⇒ plan có CẢ `risk_dial_confirmed_by_user` VÀ `risk_dial_warning_acknowledged`` | BLOCK_PLAN | closed | plan khai báo mức parking |
| `DCF_RICH_OVERRIDE` | `dcf.status=="RICH" ∧ robust ∧ side=="buy" ⇒ dcf_override_reason ≠ ""` | WARN (nâng lên BLOCK cần user duyệt) | open | có `dcf_check` |
| `ANOMALY_FLAG` | `order.ticker ∉ anomaly_excluded(asof)` | BLOCK_ORDER | closed | luôn |

## 3.5 Vị trí trong pipeline

```
 golive_recommend_v23.py  ──► status.json (S1 rating · S2 anomaly · S3 liq · CAPIT caps)
            │
            ▼
 DollarBill (LLM)  ──►  plan_<account>_<date>.json      ◄── KHOẢNG TRỐNG NGỮ NGHĨA HÔM NAY
            │
            ▼
 bot_execute.py:
    plan = load_plan(...)
    plan, verdict = constraints.validate(plan, account_ctx, asof)   ◄── ★ CỔNG DUY NHẤT ★
    if verdict.plan_blocked: alert + skip account (exit 2)
    ... (executor giữ nguyên toàn bộ guard realtime: ghost/cash/quota/T+2/floor)
            ▼
        broker API (side-effect KHÔNG đảo ngược)
```

Quyết định vị trí:

- **Cổng nằm ở tầng PLAN, ngay sau `load_plan()`** — vì đó là nơi ranh giới "đầu ra của LLM →
  đầu vào của máy" thật sự nằm. `validate()` gói trọn chuỗi hiện tại (`filter_excluded` → `net`
  → `cap_capit` → `cap_lag` → `approval`) **giữ nguyên thứ tự đã có ý nghĩa** (net trước cap
  %ADV — `plan.py:180-186`), rồi chèn rule mới vào đúng chỗ trong thứ tự đó.
- **KHÔNG chuyển các guard realtime của executor vào cổng này.** G2/G10/G11/G12 phụ thuộc trạng
  thái thay đổi từng chu kỳ poll (sổ lệnh broker, cash, KL khớp, quote). Chúng thuộc về vòng lặp
  thực thi. Cổng plan = ràng buộc **tĩnh**, biết được trước khi phiên bắt đầu. Trộn hai loại là
  cách nhanh nhất phá vỡ một hệ đang chạy đúng.
- **Registry vẫn liệt kê chúng dạng read-only** (`enforced_at="executor"`) để `constraints.
  describe()` in ra được **toàn bộ** ràng buộc đang hiệu lực — trả lời câu hỏi K1 mà không đụng
  code executor.

## 3.6 `PLAN_BUYING_POWER` — thiết kế chi tiết (tôn trọng quyết định user 07-28)

Đây là rule nhạy cảm nhất; viết sai sẽ tái lập đúng thứ user đã từ chối.

```python
Constraint(
  id="PLAN_BUYING_POWER",
  scope="plan",
  invariant=("Σ giá trị lệnh MUA trong orders[] ≤ sức mua ĐO ĐƯỢC của account tại thời điểm "
             "validate. Sức mua = số broker báo (ppse), KHÔNG phải giả định về vốn tương lai. "
             "Account có margin: ppse đã bao gồm hạn mức vay do broker cấp ⇒ rule KHÔNG cấm "
             "dùng đòn bẩy, chỉ cấm dùng vốn CHƯA TỒN TẠI."),
  remedy=Remedy.BLOCK_PLAN,
  applies_to=lambda c: c.account.mode == "live",
  status="ACTIVE",          # cấu hình được: WARN_ONLY để chạy shadow trước
  evidence="INCIDENTS.md:4080 (3 lần 07-23/07-27/07-28); user từ chối luật cấm cứng 16:16 07-28",
)
```

Bốn điểm khiến rule này **khác** với đề xuất đã bị từ chối:

1. **Vế phải là `buying_power` do BROKER báo, không phải `cash`.** Khi SpaceX bật margin
   (V2.5), `ppse` của DNSE tự bao gồm hạn mức vay ⇒ rule tự nới, không cần sửa code, không cần
   nhớ tắt. Đây chính là lý do user nêu khi từ chối, và nó được giải quyết bằng cách chọn đúng
   đại lượng chứ không bằng cách bỏ rule.
2. **`applies_to` + `status` cấu hình được**: có thể giới hạn theo account
   (`account.margin_enabled == False`), theo mode, hoặc hạ xuống `WARN_ONLY`. Không có luật tuyệt
   đối nào bị đóng cứng vào code.
3. **Trần đòn bẩy là rule KHÁC** (`GROSS_EXPOSURE_CAP`, ngưỡng lấy từ `trading_rules.json`), tách
   bạch: A1 chống *vốn ảo*, GROSS_EXPOSURE chống *vay quá tay*. Trộn hai thứ là nguồn gốc của
   hiểu lầm 07-28.
4. **Không đọc được sức mua ⇒ BLOCK kèm lý do "không đo được"**, không đoán. Đúng §5 và đúng
   bright-line §6 (sức mua same-day phải lấy DNSE, tuyệt đối không suy từ BQ).

**Chống lách bằng vỏ bọc mới:** rule tính trên **tổng `orders[]` thực tế**, độc lập hoàn toàn với
tên field và văn xuôi. Không quan trọng plan gọi nó là `funding_required`, `funding_needed`, một
câu note, hay không gọi gì cả — Σ vẫn là Σ. Đó là khác biệt cốt lõi giữa lớp constraint và lệnh
cấm-theo-hình-thức đã thất bại 3 lần. Đồng thời rule **không** cấm `deferred_orders[]` (cơ chế
đúng đã được dạy) — chỉ `orders[]` bị ràng buộc.

## 3.7 Thứ tự ưu tiên mechanize

Tín hiệu ưu tiên = **tần suất tái phạm thực tế** (theo yêu cầu), sau đó là chi phí/rủi ro triển khai.

| # | Constraint | Tái phạm | Chi phí | Lý do xếp hạng |
|---|---|---|---|---|
| **P0** | `PLAN_BUYING_POWER` | **3 lần / 6 ngày, tần suất TĂNG** (4 ngày → 1 ngày) | Trung bình (cần đọc ppse live) | Pattern tái diễn duy nhất đang tăng tốc. Cả 3 lần thoát nhờ QA thứ 2 **tình cờ** chạy. ⚠️ **Cần user duyệt trước khi ACTIVE** vì chạm đúng đề xuất user đã từ chối — đề nghị chạy `WARN_ONLY` (shadow) ≥10 phiên, báo cáo số lần rule sẽ bắn, rồi mới xin duyệt ACTIVE. |
| **P1** | `LAG_RATING_MAX` (lưới executor) | 0 lọt lệnh, 2 near-miss | **Thấp nhất** — `lag_rating_filter.lag_filter_low_rating()` đã tồn tại, chỉ cần gọi ở tầng plan | Lỗ hổng cấu trúc được chính docstring gate thừa nhận (`lag_rating_filter.py:33-34`). Rule đã được user chốt rõ ràng 07-27 ⇒ không cần quyết định chính sách mới. Tỷ lệ giá trị/chi phí cao nhất. |
| **P2** | `NAME_CAP`, `ORDER_VALUE_CAP`, `DAILY_GROSS_CAP` | 0 | Thấp (số học thuần trên plan + NAV) | Đóng K3: khiến `trading_rules.json` có chân trong code lần đầu. Rủi ro thấp vì hiện các plan đều nằm sâu dưới trần ⇒ bật ACTIVE gần như no-op, đúng tinh thần "bảo hiểm". |
| **P3** | `RISK_DIAL_OVERRIDE` | 1 tiền thân (07-01, `target_equity_pct=93.8%`) | Thấp | Rule đã viết sẵn dạng gần-hình-thức trong `trading_rules.json`, dịch 1-1. |
| **P4** | `GROSS_EXPOSURE_CAP` | 0 (margin chưa bật) | Trung bình (cần vị thế + NAV live) | **Phải xong TRƯỚC khi V2.5/margin go-live** — lúc đó nó chuyển từ dormant sang binding. |
| **P5** | `ANOMALY_FLAG` ở tầng plan | 0 | Thấp | Mirror của `LAG_RATING_MAX`: gate anomaly cũng chỉ ở tầng signal. Gộp chung 1 lần triển khai với P1. |
| **P6** | `DCF_RICH_OVERRIDE` nâng WARN→BLOCK | 0 | Thấp | **Cần user quyết chính sách** — hiện là "thuần thông tin" có chủ đích. Không tự nâng. |
| — | B1–B5 (authoring-time) | B5: 3 lần | — | **Vehicle khác** (self-check/pre-commit), đề xuất riêng. B5 xứng đáng ưu tiên ngang P0 nhưng KHÔNG thuộc module này. |

## 3.8 Kế hoạch triển khai (nếu user duyệt)

| Bước | Việc | Verify |
|---|---|---|
| 1 | `trading_bot/constraints.py`: dataclass + registry + `validate()`; bọc 5 guardrail hiện có, **không thêm rule mới** | `constraints_selfcheck.py` + A/B trên 20 plan lịch sử: kết quả **byte-identical** với đường hiện tại |
| 2 | `bot_execute.py`: thay 5 lời gọi rải rác bằng 1 `constraints.validate()` | Chạy lại A/B, self-check cũ (`excluded_tickers`, `approval_gate`, `capit_participation_cap`) vẫn PASS nguyên |
| 3 | Thêm P1 + P5 (`LAG_RATING_MAX`, `ANOMALY_FLAG`) status=ACTIVE | Self-check tái dựng case TRC/MST/PNJ; replay plan 07-20→07-28 xác nhận **0 lệnh thật bị đổi** |
| 4 | Thêm P0 status=**WARN_ONLY**, chạy shadow ≥10 phiên | Báo cáo: rule sẽ bắn bao nhiêu lần, có false-positive nào không |
| 5 | Trình user quyết P0 → ACTIVE (hoặc giữ WARN_ONLY) | Quyết định của user, không mặc định |
| 6 | P2/P3, rồi P4 trước khi margin go-live | Self-check + quant-skeptic |

**Không nằm trong phạm vi:** không đụng `executor.py`, không đụng logic đặt lệnh, không đổi
hành vi bất kỳ guardrail nào đang chạy ở bước 1-2. Mọi thay đổi áp vào LIVE cần user duyệt
(quy tắc sở hữu `trading_rules.json`).

## 3.9 Rủi ro & phản biện tự đặt

1. **Rủi ro lớn nhất: tạo tầng trừu tượng cho một hệ đang chạy đúng.** `coding_guidelines §2`
   nói thẳng "không abstraction cho code dùng-một-lần". Phản biện: registry chỉ đáng làm NẾU
   thực sự thêm ≥3 rule mới; nếu user chỉ duyệt P1, thì **cách đúng là thêm 1 lời gọi
   `lag_filter_low_rating` vào `bot_execute.py`, KHÔNG xây registry**. Ngưỡng quyết định nên
   nêu rõ khi review, không giả định sẵn là "xây module".
2. **Fail-closed sai chỗ có thể tự nó gây sự cố.** G4/G5 đã cho thấy fail-closed nghiêm ngặt tạo
   BLOCK ngoài ý muốn khi artifact lệch. Mọi rule mới phải qua shadow trước khi ACTIVE (bước 4).
3. **P0 chạm quyết định user đã đưa ra.** Tài liệu này KHÔNG tự triển khai P0; nó chỉ chỉ ra
   dạng phát biểu tương thích với lý do user nêu (margin tương lai). Nếu user vẫn muốn giữ
   context-file rule, **P1-P5 vẫn đứng độc lập và vẫn đáng làm**.
4. **Không nên chạy đua với LLM về hình thức diễn đạt.** Bài học 3 lần của A1: chỉ những invariant
   phát biểu được trên **số học của artifact** (Σ giá trị, rating, %ADV, %NAV) mới đáng mechanize.
   Ràng buộc trên nội dung văn bản (A7 — note phải công bố rủi ro BEAR) nên dừng ở WARN mãi mãi.

---

## Phụ lục — chỉ mục file:line đã kiểm chứng

| Thành phần | Đường dẫn |
|---|---|
| Cổng plan hiện tại | `bot_execute.py:291-344` |
| `filter_excluded_tickers` | `trading_bot/plan.py:138` |
| `net_offsetting_orders` | `trading_bot/plan.py:154` |
| `cap_capit_orders` | `trading_bot/plan.py:259` |
| `cap_lag_orders` | `trading_bot/plan.py:363` |
| `approval_block_reason` | `trading_bot/plan.py:509` |
| `_ghost_tickers` | `trading_bot/executor.py:560` (dùng `:1040`, `:849`, `:966`) |
| `_floor_guard_buy` | `trading_bot/executor.py:810` |
| Sellable/T+2, cash, quota | `trading_bot/executor.py:893`, `:913`, `:465` |
| `BOT_STOP` | `trading_bot/config.py:13`, `executor.py:1135` |
| `ACCOUNT_DEFAULTS` / `excluded_tickers` | `trading_bot/config.py:119` / `:128` |
| Trần orders/gross (chỉ V23Strategy) | `trading_bot/strategies.py:422-429` |
| Gate rating LAG | `lag_rating_filter.py:45`, `golive_recommend_v23.py:592` |
| Gate anomaly | `anomaly_gate.py:27`, `golive_recommend_v23.py:281/658` |
| Chính sách hạn mức (prose) | `data/trading_rules.json` `/sizing`, `/execution_limits`, `/neutral_parking` |
| Rule cash-discipline (prose) | `mike/kb/context_planning_mini.md:79-102` |
| Sự cố A1 ×3 | `mike/kb/INCIDENTS.md:4080-4126` |

---

# PHỤ LỤC B — Trạng thái TRIỂN KHAI (job `Taylor_20260729_022049`, 2026-07-29)

User duyệt làm **P1 + P0**, **KHÔNG** xây `trading_bot/constraints.py` (registry chỉ đáng làm khi
có ≥3 rule cùng lúc — §3.9 điểm 1). Đã triển khai đúng phạm vi đó, dạng **patch tối thiểu**:

| Rule | Trạng thái | Nơi sống | Verify |
|---|---|---|---|
| `LAG_RATING_MAX` (P1) | **ACTIVE** (chờ user xác nhận trước phiên chạy thật) | `trading_bot/plan.py::filter_lag_rating_orders`, gọi 1 chỗ trong cascade `bot_execute.py` ngay sau `cap_lag_orders` | `lag_rating_order_gate_selfcheck.py` — 14 unit + 6 live = 20/20 PASS; replay TRC 07-23 / MST 07-27 bị chặn đúng; replay 21 plan thật 07-20→07-28 (110 lệnh, 2 LAG-buy) **0 lệnh bị đổi** |
| `PLAN_BUYING_POWER` (P0) | **WARN_ONLY (chỉ ghi CSV)** | `bot_execute.py::_log_plan_buying_power_shadow` → `data/plan_buying_power_shadow_log.csv`; sức mua = `BrokerBase.get_buying_power` mới (DNSE `ppse.pp0Buy`) | `plan_buying_power_shadow_replay.py` — 22/22 PASS; **3/3 ngày sự cố would_block=true**, 5/5 ngày lành would_block=false hoặc không log |

**Điều chỉnh so với §3.7 sau khi chạm dữ liệu thật** (ghi lại để lần sau không phải đo lại):

1. `data/execution_logs/dnse_raw_*.jsonl` có **0 bản ghi `ppse` nào của SpaceX** từ trước tới nay
   (`get_max_buy_qty` chỉ được gọi khi `availableCash` không đủ). Nên replay P0 phải dùng PROXY
   `availableCash`/`totalCash`. Với account CÓ margin, `pp0Buy` ≥ cash ⇒ verdict `would_block=true`
   của replay là kết luận theo **cận dưới** của sức mua, chưa phải bằng chứng rule sẽ bắn với
   `pp0Buy` thật. **Đây là câu hỏi mở quan trọng nhất trước khi bàn ACTIVE** (xem §3.6: rule cố ý
   KHÔNG cấm đòn bẩy — nếu `pp0Buy` thật của SpaceX lớn, cả 3 sự cố có thể KHÔNG vi phạm chính
   invariant này, dù vẫn vi phạm quy tắc cash-discipline dạng prose mà user chọn giữ).
2. Bằng chứng "cash ≠ sức mua" đo được: ZaloPay 07-28 `availableCash` 5,68M / `totalCash` 32,01M /
   **`pp0Buy` THẬT 25,54M**. Xác nhận việc chọn `pp0Buy` làm vế phải (§3.6 điểm 1) là đúng —
   dùng `availableCash` sẽ báo động giả.
3. Bản plan VI PHẠM của cả 3 lần đều **không còn trên đĩa** (đã bị sửa đè lên đúng tên file
   canonical trước khi lưu) ⇒ replay phải tái dựng Σ từ bus event của chính job DollarBill lúc đó.
   Hệ quả cho lần sau: `data/trade_plans/` KHÔNG phải audit trail của cái gì đã từng được đề xuất.
