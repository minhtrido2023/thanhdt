# SpaceX tra gói vay theo default 1258 (08-11→08-14) — script nào, có chạm tiền thật không

Job `Taylor_20260913_055125` · follow-up cq-20260913 batch1 #1 · READ-ONLY (không sửa code).
Nguồn bằng chứng: `data/execution_logs/dnse_raw_2026-0{6..9}-*.jsonl` (lọc `account_no=="0002023347"`, §12),
`mike/logs/inject_discretionary.log`, `secrets/trading_bot_accounts.json`, crontab, git log.

## Kết luận ngắn

| Câu hỏi | Trả lời |
|---|---|
| Có ảnh hưởng tiền thật không? | **KHÔNG.** 0 lệnh SpaceX mang 1258; 0 lần `ppse` SpaceX gửi 1258; sizing đo bằng đúng gói. |
| Script tạo record 1258 (cron) | **`discretionary_accumulation_inject.py:116`** — nhánh cash-gate (`plan_cash_commitment` → `plan_funding_gate`). |
| `park_holdings.py:278`, `compute_active_nav.py:151` | **Vô can** — chỉ gọi `get_positions`/`get_cash`, không đụng gói vay. |
| Patch #1 có đóng ca này không? | **KHÔNG.** `_account_default_lp()` rơi về `client.loan_package_id` (=1258) khi broker dựng không có `loan_package_id`. Cần sửa thêm. |
| DNSE có dùng id 0 không? | **Không thấy lần nào** trong 72 file dnse_raw (06-12→09-13). |

Mức độ: **LATENT, không có tác động tiền.** Hiện ra 1258 chỉ ở tầng chọn gói, và bộ chọn gói trả đúng id nhờ
may mắn cấu trúc (luật "ưu tiên type N"). Ca sẽ lặp lại lần tới injector SpaceX chạy tới cash-gate (TV1 đang
ở deadband, thiếu 100cp).

## 1. Profile vs mặc định

`secrets/trading_bot_accounts.json`: SpaceX `loan_package_id=1841`, ZaloPay `None`, RocketX `1122` (disabled).
`secrets/dnse_credentials.json`: `loan_package_id=1258`. Mọi broker DNSE dùng chung 1 `DNSEClient`
(`_DNSE_POOL`, credentials_file=None). Chỉ `make_broker(cfg, profile=p)` truyền gói của profile; dựng
`DNSEBroker(...)` trực tiếp mà không truyền `loan_package_id` ⇒ client giữ 1258 ⇒ SpaceX mang default 1258.

## 2. Các chỗ dựng broker/client (WorkingClaude/*.py, trading_bot/, mike/bin/) — code hiện tại

| Chỗ dựng | Truyền gói profile? | Gọi gì trên broker | Có đụng gói vay? |
|---|---|---|---|
| `bot_execute.py:111`, `:720`, `bot_prepare_plan.py:50` | CÓ (`make_broker(profile=p)`) | toàn bộ: ppse / place_order | có — đúng gói (nhưng dính rò #1 khi nhiều account/1 tiến trình) |
| **`mike/bin/discretionary_accumulation_inject.py:116`** | **KHÔNG** | `get_positions`, `get_quote`, rồi `gate_injected_order(broker)` → `check_plan_funding` (`_resolve_loan_package_id`, `_validate_lever_package`, `get_buying_power`) + `residual_headroom` (`get_buying_power`) | **CÓ** — chỉ đo sức mua / sizing lệnh chèn vào plan, KHÔNG đặt lệnh |
| `mike/bin/park_holdings.py:278` | KHÔNG | `connect`, `get_positions` | không |
| `mike/bin/compute_active_nav.py:151` | KHÔNG | `connect`, `get_positions`, `get_cash` | không |
| `mike/bin/daily_nav_snapshot.py:117` | KHÔNG | `connect`, `get_positions`, `get_cash` | không |
| `mike/bin/compute_park_trim.py:240`, `lag_rule_a_ceiling.py:179` | quote_only | quote | không |
| `bot_execute.py:532/543`, `send_plan_report.sh:302`, `verify_account_snapshot.py:483`, `capture_upcom_vwap_eod.py:96`, `marginability_check.py:147` | client thô | OTP / balances / loan_packages đọc thuần | không log `loan_packages_resolve`; không ppse/order |
| `dnse_order_test.py:62` (tool tay, commit cuối 06-21) | KHÔNG | **`place_order` thật** (mua giá sàn) | **CÓ, latent** — nếu `accounts()[0]` là SpaceX thì lệnh đi bằng 1258. Orderbook 07→09 chưa từng thấy. |

`loan_packages_resolve` chỉ do `DNSEBroker._resolve_loan_package_id` ghi, nên mọi record `default=1258` của
SpaceX phải đến từ một `DNSEBroker` KHÔNG truyền gói, có đi qua bộ chọn gói.

## 3. Khớp với log thật — mọi record SpaceX `loan_packages_resolve.default == 1258`, toàn kỳ 06-12→09-13

Quét toàn bộ 72 file: record 1258 CHỈ nằm trong 4 ngày này.

| Ngày | Giờ ICT | Số record | Nguồn | Bằng chứng |
|---|---|---|---|---|
| 08-13 | 20:30:02 | 1 (TV1, resolved 1122) + ppse TV1 gói 1122 pp0Buy 444.509.858 | **cron `inject_discretionary_orders.sh`** | `inject_discretionary.log`: `=== [inject_discretionary] SpaceX — 2026-08-13 20:30 ICT ===` … `cash-gate: PASS — sức mua 444,509,858đ (gói 1122, resolved:cash_only)` — trùng từng đồng với ppse trong dnse_raw |
| 08-14 | 20:30:02 | 1 (TV1 → 1122) + ppse pp0Buy 425.701.185 | **cron injector** | log: `SpaceX — 2026-08-14 20:30 ICT` … `cash-gate: PASS — sức mua 425,701,185đ (gói 1122, …)` — trùng từng đồng |
| 08-12 | 23:34:33, 23:53:45 | 2 (TV1 → 1122) + ppse pp0Buy 459.058.903 | chạy tay đường injector (không phải cron) | Cùng chữ ký record với cron (positions → quote_l2 TV1 → resolve → ppse, SpaceX rồi ZaloPay). Không có dòng trong log cron. Trùng giờ job `Taylor_20260812_161457` (commit `bc8ce26a`/`397ffa0c` 00:10 ICT 08-13 "injector: đọc active_nav…") — **suy luận theo thời gian commit, không có log tiến trình** |
| 08-13 | 07:06:06 | 1 (TV1 → 1122) + ppse pp0Buy 459.058.903 | chạy tay đường injector | Cùng chữ ký. Trùng phiên sửa `compute_active_nav` (commit `470d9f5b` 00:37Z = 07:37 ICT) — **suy luận theo thời gian** |
| 08-11 | 01:22→02:24 | 44 (TV1, DRI, ACB…VRE) + ppse DRI(1122)/HPG(1841) | tiến trình tay, KHÔNG phải cron (crontab giờ 18 UTC trống; 19 UTC chỉ có `kb_nightly`) | Chữ ký = `check_plan_funding` trên toàn plan cho cả 2 account trong 1 tiến trình, broker dựng không truyền gói. **02:28:16 cùng chữ ký nhưng SpaceX default=1841 và ZaloPay default=1841** = tiến trình dùng `make_broker(profile)` lặp account → đúng ca rò #1. **Không gán được tên script** — không có file log nào ghi mốc giờ đó |

Đối chứng âm (cùng cơ chế): injector SpaceX 08-11/08-12 20:30 = `status=completed` no-op → không có record
1258 lúc 20:30. Từ 08-17 trở đi mọi lượt SpaceX dừng ở `decision: skip` (đã đạt mục tiêu / deadband) trước
cash-gate → cũng không có record 1258. Record 1258 xuất hiện **khi và chỉ khi** injector chạy tới cash-gate.

## 4. Tác động TIỀN THẬT

1. **Lệnh đã đặt** — orderbook broker (`orders`, dedupe theo id) SpaceX 07→09: **160 lệnh, `loanPackageId` ∈ {1841: 78, 1122: 82}, 0 lệnh 1258.**
   `place_order` SpaceX (đã log): 159 record, gói đã log ∈ {1122, 1841, None}. Lệnh None = bán / lệnh trước khi có
   bộ chọn gói → dnse_api rơi về default của client trong tiến trình bot (make_broker → 1841); orderbook xác nhận.
   Đối chứng ZaloPay: 198 lệnh ∈ {1258: 185, 1826: 13}, 0 gói ngoại.
2. **Lệnh do injector sinh ra thực sự đi với gói nào** — `plan_SpaceX_2026-08-14` `BUY-TV1-DISC` 1200cp
   `loan_package_id=None, cash_only=True`; bot đặt `09:15:14 TV1 600 @20.400 lp 1122`, `14:08:08 TV1 100 lp 1122`;
   plan 08-17 500cp → `09:15:18 TV1 500 @20.100 lp 1122`. Đúng gói UPCOM của SpaceX. Plan không mang theo 1258.
3. **Sizing / sức mua** — ppse SpaceX gửi gói 1258: **0 lần** trong toàn kỳ. Mọi ppse của injector dùng gói đã
   chọn (1122). Lý do đúng: 1258 không nằm trong danh sách gói hợp lệ của SpaceX ⇒ bộ chọn rơi về "ưu tiên type N"
   ⇒ mainboard [1841 N, 1840 M] → 1841, UPCOM [1122] → 1122. Xác nhận bằng log: 02:24:47 (default 1258) và
   02:28:16 (default 1841) cho **cùng** `resolved` trên 17 mã.
4. **NAV** — `compute_active_nav`/`daily_nav_snapshot`/`park_holdings` không đọc gói vay ⇒ không ảnh hưởng.

⇒ **Không có tác động tiền.** Kết quả đúng là **nhờ may**, không phải do thiết kế. Ba đường có thể ra sai:
- (a) Mã có >1 gói type N cho SpaceX (ca `SAB` trong selfcheck patch #1): bộ chọn lấy gói N **đầu tiên** thay vì 1841.
- (b) Plan SpaceX có lệnh đòn bẩy CAPIT không hợp lệ cho mã → `_validate_lever_package`/`_account_default_package`
  trả 1258 → `check_plan_funding` đo `ppse` bằng gói của account KHÁC ⇒ số sức mua vô nghĩa (tới giờ chưa xảy ra: 0 ppse 1258).
- (c) State discretionary `cash_only=false` → `_resolved_package` trả None → `get_buying_power(lp=None)` → dnse_api gửi 1258.
Chiều hỏng của (b)/(c): nhiều khả năng DNSE trả 0/lỗi → injector fail-safe không chèn (hụt vốn, không vay vượt), nhưng
đây là giả định chưa kiểm với DNSE.

## 5. Patch #1 (`cq20260913_batch1_item1.patch`) có đóng ca này không — KHÔNG

Patch bỏ việc ghi gói profile lên client dùng chung và thêm `DNSEBroker._account_default_lp()` =
`self._loan_package_id` nếu có, **không thì `client.loan_package_id` (credentials = 1258)**. Injector dựng
`DNSEBroker(account_id=…, credentials_file=None, label=account)` ⇒ `_loan_package_id=None` ⇒ vẫn 1258.
Patch đóng ca rò 02:28 (ZaloPay mượn 1841), không đóng ca 1258 của SpaceX. Không xung đột với fix đề xuất dưới đây.

## 6. Đề xuất fix (chưa làm — cần Mike/user duyệt; chạm `brokers.py` = lõi, §23 phải quét rộng)

**Khuyến nghị (gốc, 1 chỗ):** trong `trading_bot/brokers.py`, sau patch #1, `_account_default_lp()` khi
`self._loan_package_id is None` và có `account_id` → tra profile theo `account_id` trong
`secrets/trading_bot_accounts.json` (`config.load_accounts`) và dùng `loan_package_id` của profile đó; profile
không có gói (ZaloPay) → giữ nguyên rơi về gói credentials (hành vi không đổi từng byte cho ZaloPay). Lý do chọn
chỗ này: đóng mọi nơi dựng broker hiện tại lẫn sau này. Sửa từng script chỉ chặn đúng ca đó, script tiếp theo sẽ lặp
lại (bài học §28). Selfcheck: thêm ca "`DNSEBroker(account_id=SpaceX)` không truyền gói → resolve/ppse/place_order
ra 1841" vào `loan_package_multi_account_selfcheck.py`, kèm đối chứng RED trên base.

**Nếu không muốn chạm lõi — sửa theo file:**
- `mike/bin/discretionary_accumulation_inject.py:116` — **BẮT BUỘC**: truyền
  `loan_package_id=<profile[account].loan_package_id>` (tra `load_accounts(load_config())` theo label), hoặc
  `make_broker(cfg, profile=p)`. Selfcheck: SpaceX → `loan_packages_resolve.default==1841`.
- `dnse_order_test.py:62` — nên sửa: tool đặt lệnh thật mà không có gói profile; truyền gói profile hoặc chặn account ≠ chỉ định.
- `mike/bin/park_holdings.py:278`, `mike/bin/compute_active_nav.py:151`, `mike/bin/daily_nav_snapshot.py:117` —
  **không cần sửa về chức năng** (không đọc gói). Chỉ nên sửa cho nhất quán nếu KHÔNG chọn fix gốc.

## 7. Phụ — `dnse_api.py:149` / `:218` `loan_package_id or self.loan_package_id`

Quét 72 file dnse_raw (06-12→09-13), mọi nơi có id gói (`loanPackageId` trong orders/positions/deals, `loanPackages[].id`,
`valid_ids`, `resolved`): tập id = **{1122, 1258, 1769, 1826, 1840, 1841}**. **Không có id 0.** `or` bỏ qua 0 là vô
hại trên dữ liệu thực tế. Vẫn nên đổi sang `is not None` cho đúng ngữ nghĩa khi có dịp chạm file (không gấp). Lưu ý
`:218` cố ý gửi chuỗi `"0"` làm sentinel khi không có gói nào — đó là giá trị gửi đi, không phải id DNSE cấp.
Giới hạn: đây là "không quan sát được", không phải xác nhận từ tài liệu DNSE.
