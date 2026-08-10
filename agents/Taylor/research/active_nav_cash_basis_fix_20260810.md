# `compute_active_nav.py` — cơ sở tiền `availableCash` → `totalCash − totalDebt`

**Job** `Taylor_20260810_004252` · **Ngày** 2026-08-10 · **Chủ** Taylor
**Trạng thái**: ĐÃ SỬA + selfcheck 26/26 PASS + đối soát độc lập khớp tuyệt đối.
**Hiệu lực**: **phiên 2026-08-11 trở đi**. KHÔNG áp cho plan 2026-08-10 (đã duyệt quy trình riêng).

---

## 1. Bug

`mike/bin/compute_active_nav.py:55` (bản cũ) lấy tiền qua `DNSEBroker.get_cash()`, mà hàm đó trả
**`availableCash`** (field đầu tiên trong `qget`, `trading_bot/brokers.py:430`).

```
active_nav = (availableCash) + Σ market_value − Σ market_value(excluded) + offbook
```

`availableCash` = "tiền TIÊU ĐƯỢC NGAY", **không** gồm tiền bán chưa settle T+2, cổ tức phải thu,
lãi tiền gửi; và công thức cũ **không trừ `totalDebt`**.

Đo thật, SpaceX 2026-08-07 (phiên chạy L1 park-trim, bán 13 mã PARK ≈189,4tr):

| Thời điểm | availableCash | totalCash |
|---|---:|---:|
| 11:25 (trước khớp) | 4.821.143 | 14.596.323 |
| 19:10 (sau khi bán 189,4tr) | **4.821.143** (y hệt) | **203.656.265** |

⇒ toàn bộ 189,06tr tiền bán chỉ hiện ở `totalCash`. Hệ quả trên active_nav:

| | active_nav SpaceX |
|---|---:|
| Bản cũ (`availableCash`) | 762.476.143 |
| Bản mới (`totalCash − totalDebt`) | **961.311.265** |
| Chênh | **−198.835.122đ = −20,7%** |

Đây là **cùng LOẠI** bug với mẫu số pool của `compute_park_trim.py` (sửa 2026-08-09, job
`Taylor_20260809_150316`, commit `df7d92b4`) — lần thứ hai trong hai ngày.

**Vì sao nghiêm trọng**: `active_nav` là MẪU của mọi phép sizing —
`LAG_book = active_nav × w_lag`, slot CAPIT, và trần chia %ADV giữa hai account
(`golive_recommend_v23._account_nav_basis`). Khai thiếu NAV ⇒ **under-deploy vốn có thật**, và
nặng nhất đúng vào phiên **sau một đợt bán lớn** — tức là đúng lúc hệ vừa giải phóng vốn để tái
triển khai. Chiều sai ngược với bug park-trim (bug kia gây BÁN quá tay; bug này gây MUA thiếu),
nên hai bug **không** triệt tiêu nhau.

Phần `totalDebt`: gap này đã được nêu trước đó trong
`research/margin_kelly_production_wiring_20260803.md` (mục cuối) — "`compute_active_nav.py` không
trừ `totalDebt` trong khi NAV chuẩn tắc của fleet có trừ". Nay đóng.

## 2. Bản vá

Chỉ sửa **một file production**: `mike/bin/compute_active_nav.py`.

1. Hàm mới `cash_basis(bal)` — parse block `stock` của payload `balances` thô, trả
   `(totalCash − totalDebt, chi_tiết)` hoặc `(None, chi_tiết_có_reason)`.
2. `live_balance_and_positions()` không gọi `b.get_cash()` nữa; đọc thẳng
   `b.client.balances()` (vẫn `_log_raw` để giữ nguyên dấu vết audit như trước).
3. **Fail-closed**: `cash is None` ⇒ `sys.exit(4)`, **KHÔNG ghi file**. File `active_nav_*.json`
   cũ ở lại nguyên vẹn; consumer tự hết hạn theo `computed_at` (`ACTIVE_NAV_MAX_AGE_D=5`) rồi lùi
   về `nav_history` — đường lùi có sẵn, không phải xây mới.
4. **Ba guard tái dùng NGUYÊN VẸN** (import, không chép lại) từ `mike/bin/park_holdings.py`, nơi
   chúng đã qua 3 vòng quant-skeptic ngày 08-09:
   - `_stock_block_all_zero` — block `stock` toàn 0 (sự cố feed thật 2026-07-27);
   - `_cash_fields_all_zero` — 3 field tiền = 0 nhưng `depositInterest` còn sống (guard trên mù);
   - `_cash_fields_inconsistent` — `totalCash < availableCash`, vi phạm bất biến kế toán (bắt ca
     lỗi feed chỉ ăn 2/3 field, cả hai guard trên đều mù).
5. **Minh bạch cổ tức phải thu**: `cashDividendReceiving` nằm trong `totalCash` nhưng giá cổ phiếu
   có thể chưa rơi ex-date ⇒ đếm 2 lần, tự triệt tiêu sau 1-2 phiên. Script **không tự hiệu chỉnh**
   (cần lịch sử `dnse_raw` + ex-date từ BQ như `daily_nav_snapshot.cum_dividend_double_count`,
   ngoài phạm vi bản vá) mà **CÔNG BỐ**: in cảnh báo + ghi `cash_dividend_receiving_vnd` +
   `cash_dividend_double_count_warning` vào JSON khi khoản đó > 0,5% active_nav. Cảnh báo này đã
   **nổ thật ngay lần chạy đầu** (SpaceX 9.775.000đ = 1,02%; ZaloPay 6.453.500đ = 1,27%).
6. JSON đầu ra thêm `cash_total_vnd` / `cash_debt_vnd` / `cash_available_vnd` /
   `cash_dividend_receiving_vnd` / `cash_basis` — audit tái lập được số mà không phải gọi lại API.
   Key `active_nav`, `total_nav`, `cash`, `positions` **giữ nguyên tên** (consumer không phải sửa).

### Ranh giới — chỗ KHÔNG đụng (và selfcheck cưỡng chế)

| Đường | Field | Vì sao giữ |
|---|---|---|
| `DNSEBroker.get_cash()` | `availableCash` | `check_plan_funding()`/executor hỏi **sức mua đặt lệnh ngay**, không phải NAV. Sửa = **nới lỏng gate tiền** — hướng sai nguy hiểm. |
| `compute_jit_unpark.py` (L2) | `availableCash` | Cố ý: "tiêu được ngay bao nhiêu". |
| `compute_active_nav.py` | `totalCash − totalDebt` | Cơ sở TÍNH TỶ TRỌNG mục tiêu. |

Nguyên tắc chung: **cơ sở tỷ trọng ≠ sức mua thực thi**. Đúng tinh thần đã áp cho
`manual_offbook_assets_vnd` (vào NAV, không vào sức mua).

## 3. Xác minh

### 3a. Selfcheck — `mike/bin/compute_active_nav_selfcheck.py`, **26/26 PASS**
Mọi ca chạy qua **hàm thật** `cash_basis()`, không có ca khẳng định suông.
- **A (5)** công thức: ca vàng SpaceX 08-09; trừ nợ margin; nợ>tiền ra số **âm** (không kẹp về 0,
  kẹp = giấu rủi ro); **A3 — đổi riêng `availableCash` KHÔNG làm đổi kết quả** (chứng minh nó đã
  ra khỏi công thức, không chỉ "trông có vẻ đúng"); hằng đẳng thức ZaloPay 08-07
  `5.818.854 + 6.453.500 + 318 = 12.272.672 = totalCash`.
- **B (6)** guard fail-closed, gồm ca lỗi feed **chỉ ăn 2/3 field** mà hai guard kia mù.
- **C (4) CHỨNG MINH NGƯỢC** — gỡ đúng điều kiện gây lỗi của từng ca B thì hàm phải trả số bình
  thường. Không có nhóm này, mọi PASS ở B cũng đúng với một hàm `return None` vô điều kiện.
- **D (4)** 4 hình dạng payload (list/dict, có/không bọc `stock`) → cùng kết quả.
- **E (3)** ranh giới: `get_cash()` **vẫn** ưu tiên `availablecash`; `compute_active_nav` không
  còn **lệnh gọi** `get_cash()` nào (kiểm bằng **AST**, không grep chuỗi — docstring có nhắc tên
  hàm như văn xuôi giải thích, grep sẽ báo động giả); L2 vẫn `availableCash`.
- **F (3)** fail-closed đến tận đầu ra: nhánh `cash is None` nằm **trước** mọi lệnh ghi file,
  thoát `sys.exit(4)`, không có fallback âm thầm.

Chạy lại dưới `env -u TZ`, `TZ=America/New_York`, và env đã tước `LANG`/`LC_ALL`: **PASS cả ba**
(§16 + skill `verify-before-done` — không phụ thuộc môi trường tác giả).

**Regression**: `money_path_freshness_selfcheck.py` (selfcheck DUY NHẤT nạp
`compute_active_nav.py`, tìm bằng grep vì nó nạp qua `importlib` nên
`selfcheck_scope_map.sh` không thấy) — **ALL CHECKS PASS**.

### 3b. Đối soát ĐỘC LẬP — khớp tuyệt đối đến từng đồng

`daily_nav_snapshot.py` tính NAV bằng **đường hoàn toàn khác** (đọc `dnse_raw_*.jsonl` + giá riêng,
`nav = mtm_stock + cash − debt + offbook`, cash = `stock["totalCash"] − stock["totalDebt"]`).
`nav_history_SpaceX.csv` dòng 2026-08-07 so với dry-run bản mới:

| | nav_history (daily_nav_snapshot) | compute_active_nav (bản mới) |
|---|---:|---:|
| NAV | 961.311.265 | **961.311.265** |
| mtm_stock | 757.655.000 | **757.655.000** |
| cash | 203.656.265 | **203.656.265** |

Khớp **tuyệt đối cả 3 cấu phần**. Bản cũ lệch −198.835.122đ so với chính con số này — tức bug đã
quan sát được từ trước qua chênh lệch hai nguồn, chỉ là chưa ai đối chiếu.

### 3c. Chạy thật cả HAI account (§12) — kết quả KHÁC nhau, đúng như phải thế

Ghi ra đường dẫn scratch `--out mike/agents/Taylor/job_20260810_004252/DRYRUN_*.json`,
**KHÔNG** chạm `data/execution_logs/active_nav_*.json` production.

| Account | cash (mới) | availableCash (cũ) | cổ phiếu | excluded | **active_nav mới** |
|---|---:|---:|---:|---:|---:|
| SpaceX | 203.656.265 | 4.821.143 | 757.655.000 | 0 | **961.311.265** |
| ZaloPay | 12.272.672 | 5.818.854 | 938.446.500 | 442.000.000 (DGC) | **508.719.172** |

## 4. Phạm vi ảnh hưởng (consumer)

| Consumer | Đọc gì | Ảnh hưởng | Cần sửa? |
|---|---|---|---|
| `golive_recommend_v23._account_nav_basis()` | `active_nav`, `computed_at` | Cơ sở chia trần %ADV giữa 2 account: **60,3/39,7 → 65,4/34,6**. Không breaking, đúng hơn. | **Không** |
| DollarBill (`build_plans_*.py`) | `nav["cash"]` + `nav["positions"]`, tự dựng `active_nav = cash + stock_live` | Tự động ăn bản sửa vì **tên key không đổi** và đồng nhất thức vẫn đúng. SpaceX: LAG_book target **+198,8tr × w_lag** (w_lag=0,65 ⇒ **+129tr**). | **Không** (nhưng xem cảnh báo dưới) |
| `send_plan_report.sh` | `nav_basis` trong file plan | Hiển thị, do DollarBill ghi. | Không |
| `anomaly_scan.py` | `positions` | Không đụng. | Không |
| `exp_capitadvcap` selfcheck D7 | label giả `_sc_navbasis` | Fixture tổng hợp, không đọc số thật. | Không |
| Fallback `nav_history_*.csv` | — | Sau vá, **hai nguồn cùng quy ước tiền** ⇒ hết bậc nhảy khi active_nav quá hạn và consumer lùi về nav_history. Trước vá, cú lùi đó tự làm NAV nhảy +20%. | Lợi phụ |

**⚠️ Cảnh báo vận hành cho DollarBill/Mike (không phải lỗi, là hệ quả đúng):**
plan đầu tiên dựng trên cơ sở mới sẽ có LAG/PARK target **cao hơn rõ rệt** cho SpaceX (+26% NAV).
Đó chính là phần vốn trước đây bị bỏ quên, nhưng `totalCash` gồm tiền **chưa settle** ⇒ **cơ sở tỷ
trọng có thể lớn hơn sức mua của riêng phiên đó**. Hai lớp đã LIVE lo phần này, không cần thêm gì:
gate P0 `check_plan_funding()` (HARD BLOCK từ 08-04, có tín dụng JIT từ lệnh bán cùng plan, commit
`087a3d0`) và L2 JIT-unpark. Chỉ cần biết trước để **không đọc nhầm** một plan mua lớn hơn là lỗi
sizing. Riêng ca 08-07: tiền bán ngày 08-07 settle T+2 = **08-11**, đúng phiên bản vá có hiệu lực.

## 5. Việc CỐ Ý không làm (nêu rõ, không giấu)

1. **Không hiệu chỉnh cổ tức phải thu** (`cum_dividend_double_count`) — cần `dnse_raw` lịch sử +
   ex-date từ BQ; sai lệch ≤1,3% NAV và tự triệt tiêu sau 1-2 phiên. Đã CÔNG BỐ thay vì im lặng.
   → Follow-up nếu muốn đóng hẳn.
2. **Không sửa lệch vintage của `--asof` quá khứ** (bug có sẵn, không do bản vá): `--asof <ngày cũ>`
   dùng giá BQ ngày đó nhưng vị thế + tiền **LIVE hôm nay**. Sai lệch này tồn tại từ trước; sửa
   đúng nghĩa là đọc `dnse_raw_{asof}.jsonl` (như `park_holdings.read_broker_snapshot` đã làm) —
   thay đổi ngữ nghĩa của một script đang phục vụ sizing, không gộp vào bản vá tiền.
3. **Không đụng** `data/trade_plans/plan_*_2026-08-10.json`, không đụng
   `data/execution_logs/active_nav_*.json` production, không đụng `trading_bot/brokers.py`.

## 6. quant-skeptic — **CONFIRMED, confidence cao, vòng 1**
Log đầy đủ: `mike/logs/verify_20260810_005523_2453897.log`.

Reviewer **không** chỉ đọc báo cáo — nó tự chạy lại: selfcheck 26/26 dưới 3 môi trường (mặc định,
`env -u TZ`, `TZ=America/New_York`); tự đọc `nav_history_SpaceX.csv` và xác nhận khớp từng đồng;
tự tính lại tỉ lệ chia %ADV 60,3/39,7 → 65,4/34,6 từ số thô; và **tự quét lại toàn repo tìm
consumer đọc `active_nav_*.json` chưa được liệt kê — không tìm thấy cái nào**. Cũng xác nhận
`git diff` trên working tree khớp đúng cái mà selfcheck vừa chạy (không phải bản cached).

### Rủi ro tồn dư reviewer nêu (giữ nguyên, KHÔNG giấu)
> `totalCash` gồm tiền bán chưa settle T+2 ⇒ đúng phiên một đợt bán lớn khớp, active_nav (cơ sở
> sizing) **có thể lớn hơn sức mua triển khai được trong chính phiên đó**. Bản vá **công bố** điều
> này (§4) và dựa vào hai gate đã ship độc lập — P0 `check_plan_funding` (HARD BLOCK từ 08-04) và
> L2 JIT-unpark — để chặn overshoot ở tầng THỰC THI thay vì ở tầng sizing. Lựa chọn thiết kế này
> nhất quán với `manual_offbook_assets_vnd` và với cách xử lý cổ tức ở trên, nhưng nó có nghĩa là
> **ranh giới sizing/thực thi nay tựa hoàn toàn vào hai gate đó tiếp tục chạy đúng**; nếu một
> trong hai regress, bản vá NAV này sẽ **âm thầm oversize plan** chứ không tự báo lỗi.

⇒ Hệ quả hành động: coi P0 `check_plan_funding` + L2 JIT-unpark là **phụ thuộc cứng** của bản vá
này. Regression ở một trong hai không còn là "lỗi cục bộ của gate" mà biến thành lỗi sizing.

### 3 việc reviewer đề nghị chạy lại (chưa làm, cần phiên thật)
1. Sau khi live 08-11: đối chiếu một file `active_nav_SpaceX.json` **do pipeline thật sinh ra** với
   một lần gọi `balances()` cùng thời điểm — xác nhận hành vi live khớp payload tổng hợp của selfcheck.
2. Xác nhận P0 + L2 **thật sự nổ** (không chỉ tồn tại trong code) ở phiên đầu tiên có khoảng cách
   lớn giữa active_nav và tiền settle — đóng killer-objection bằng bằng chứng chạy, không bằng đọc code.
3. Chạy lại selfcheck sau commit để bắt drift phút chót của working tree. *(Đã làm — mục 7.)*

## 7. Pattern lặp lại → coding_guidelines §25

Hai bug cùng loại trong hai ngày (`compute_park_trim.py` 08-09, `compute_active_nav.py` 08-10) là
đủ để thành luật, không phải trùng hợp. §25 **"Tiền KHÔNG phải một con số — mỗi consumer phải khai
rõ đang hỏi câu nào"** đã soạn ra `kb/coding_guidelines.md.proposed` (§13: KHÔNG sửa tại chỗ, chờ
Mike duyệt rồi `mv`). Nội dung: bảng quyết định 2 câu hỏi × field đúng × script nào dùng, 4 hệ quả
bắt buộc (fail-closed / tái dùng 3 guard / đối soát chéo nguồn khác path / cơ sở tỷ trọng ĐƯỢC PHÉP
> sức mua nhưng phải công bố), và số neo đo thật.

Bài học riêng đáng ghi: `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` **ĐÃ**
ghi rõ "3 field cash khác nhau" từ 2026-08-03 — bug vẫn xảy ra **hai lần** sau đó. Tài liệu kia nói
*các field khác nhau*; cái còn thiếu là **script NÀO của mình phải dùng field NÀO**. Đó là lý do
§25 mang bảng ánh xạ script→field chứ không chỉ nhắc lại sự khác biệt.

**Kiểm tra sau commit** (reviewer đề nghị #3): selfcheck chạy lại trên cây đã commit — 26/26 PASS,
`money_path_freshness_selfcheck.py` ALL PASS. Không có drift.
