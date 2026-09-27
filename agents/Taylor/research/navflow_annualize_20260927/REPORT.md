# FAIL-H (số hạng dòng tiền) + FAIL-F (annualize theo lịch) — sửa, đo, cưỡng chế

Job `Taylor_20260927_045241` · 2026-09-27 · nguồn: `research/measurement_integrity_audit_20260927/REPORT.md`
§2 FAIL-H/FAIL-F + §5. **KHÔNG merge, KHÔNG sửa file canonical — chờ user sign-off.**

2 worktree (repo `WorkingClaude` thật ở `/home/trido/thanhdt`, `mike` là repo lồng ⇒ phải 2 cây):

| Repo | Worktree | Branch | Nội dung |
|---|---|---|---|
| WorkingClaude (`/home/trido/thanhdt`) | `/home/trido/thanhdt/wt-navflow-annualize` | `fix/nav-flow-term-annualize` | VIỆC 2: `bootstrap_nav.py`, `dsr_pbo_annex.py` |
| mike | `/home/trido/thanhdt/WorkingClaude/wt-navflow-mike` | `fix/nav-flow-term` | VIỆC 1 + cổng: `bin/*`, `kb/*`, `templates/*` |

---

## VIỆC 1 — FAIL-H: tỉ suất công bố không có số hạng nạp/rút

### (a) Nguồn sự thật của nạp/rút: **DNSE OpenAPI KHÔNG CÓ** (đã quét, không phỏng đoán)

| Nguồn kiểm | Kết quả |
|---|---|
| `dnse_api.py` (SDK wrapper) | 20 endpoint. KHÔNG có cash-statement / transaction / deposit / withdraw. `balances()` là **SỐ DƯ** tại một thời điểm, không phải **SỔ** dòng tiền. |
| `data/execution_logs/dnse_raw_*.jsonl` (86 file) | 12 loại record, tất cả là `orders` 17.936 · `positions` 7.648 · `balances` 7.181 · `quote_l2` 2.844 · `ppse` 2.491 · `place_order` 774 · `cancel_order` 379 · `loan_packages_resolve` 340 · `quote_unmapped` 53 · `accounts` 6 · `modify_order` 1+1. **Không loại nào ghi nạp/rút.** |
| Field nghe giống dòng tiền trong `balances.stock` | Đều KHÔNG phải: `depositInterest` (lãi tiền gửi), `depositFeeAmount` (phí/lãi đã post), `withdrawableCash` (hạn mức rút KHẢ DỤNG), `derivative.pendingDepositWithdraw` (chỉ phái sinh, luôn 0). |

⇒ Thiết kế file thủ công **`data/account_cash_flows.json`** (loader + validate: `mike/bin/account_cash_flows.py`;
template sẵn để `cp`: `mike/templates/account_cash_flows.json`). Schema: `date`, `amount_vnd`
(DƯƠNG=nạp / ÂM=rút), `kind` ∈ `deposit|withdraw|market_only`, `evidence` (bắt buộc non-empty),
`timing` ∈ `bod|eod` (mặc định `bod`). **File thiếu = chưa có dòng tiền nào ⇒ hành vi y như cũ,
bit-for-bit** (không cần tạo file để deploy). Bản ghi sai schema ⇒ `CashFlowError`, fail-closed.

**Cổng fail-closed** — `report_delivery_gate._check_nav_flow_records()`, gọi trong `deliver()` ngay sau
`_check_period_returns`: chặn khi có bước nhảy `|Δnav ngày| > 5,0%` **không có bản ghi dòng tiền nào**
cho ngày đó. Ngưỡng đo từ phân phối thật (2026-09-27, N=113 cặp phiên liên tiếp: SpaceX 58 từ
07-02, ZaloPay 55 từ 07-07):

| TK | max\|Δ\| | p95 | median | mean | sd | ngày max |
|---|---|---|---|---|---|---|
| SpaceX | 2,942% | 2,269% | 0,573% | 0,654% | 0,584% | 2026-07-30 |
| ZaloPay | **4,148%** | 3,105% | 0,826% | 1,092% | 0,926% | 2026-08-07 |

Chọn **5,0%** = cao hơn max quan sát 0,85pp ⇒ **0 false-positive trên cả 113 quan sát** (selfcheck
kiểm lại con số này mỗi lần chạy). Mở cổng = ghi bản ghi CÓ BẰNG CHỨNG, kể cả `kind:"market_only"`
(amount=0) khi đã xác minh đó là biến động thị trường thật.
**Giới hạn nói thẳng:** dòng tiền < ~5% NAV (≲50tr trên 1B) KHÔNG bị cổng này bắt. Cổng khác nhau
phủ khác nhau — xem mục (d) về `reconcile_equity.py`.

Cổng CỐ Ý fail-closed (khác `_check_period_returns` fail-open): cổng kia so 2 con số đã tồn tại nên
"thiếu dữ liệu" = không kết luận được; cổng này canh một HÌNH DẠNG (bước nhảy không giải thích được)
mà đúng hình dạng đó là hình dạng của nạp/rút chưa ghi — không chặn thì cái sai được công bố.

Ghi nhận thêm: `daily_nav_snapshot.py:1281` đã có sanity guard `NAV_SANITY_MAX_PCT=15%` **nhắc đến
nạp/rút**, nhưng đường thoát của nó là *"chạy lại với `NAV_SANITY_MAX_PCT` lớn hơn"* — tức bỏ qua và
ghi NAV, KHÔNG ghi lại dòng tiền ⇒ tỉ suất vẫn sai. Đó là cảnh báo, không phải cổng.

### (b) `nav_period_returns.py` → time-weighted return chain-link

Công thức cũ `nav1/nav0 − 1` (dòng 107 và 133) thay bằng TWR **tái định giá tại MỖI ngày có dòng tiền**
(định nghĩa sách giáo khoa, không phải xấp xỉ Dietz):

- `timing="bod"` (mặc định): `r_t = nav_t / (nav_{t-1} + flow_t) − 1`.
  **Vì sao mặc định:** DNSE ghi tiền nạp vào `totalCash` ngay khi nhận, mà `nav_t` là snapshot CUỐI
  ngày ⇒ `nav_t` ĐÃ chứa tiền nạp ⇒ vốn cơ sở sinh lời của ngày t là `nav_{t-1} + flow_t`. Rút: flow âm,
  `nav_t` đã trừ ⇒ cùng công thức. Nạp/rút trong giờ giao dịch (ca phổ biến với TK cá nhân) khớp quy ước này.
- `timing="eod"`: `r_t = (nav_t − flow_t) / nav_{t-1} − 1`, cho tiền vào/ra SAU khi NAV ngày t đã chốt.
  Bắt ghi rõ thay vì đoán — selfcheck chứng minh 2 quy ước cho 2 số KHÁC nhau (nếu bằng nhau thì
  quy ước là vô nghĩa). `eod` trên ngày không có dòng `nav_history` ⇒ `CashFlowError` (thực chất đó là
  `bod` của phiên sau — ghi cho đúng, đừng để script đoán).
- Vốn khởi điểm **KHÔNG phải flow**: bản ghi có `date <= inception_date` bị BỎ (đã nằm trong
  `starting_capital`) — nếu không sẽ trừ hai lần.

**BYTE-IDENTICAL: 115/115.** So `stdout` của bản cũ (canonical `mike/bin/nav_period_returns.py`
@`78494398`) với bản mới, cho **MỌI ngày có trong `nav_history` của CẢ 2 TK** (SpaceX 59 + ZaloPay 56):
0 khác biệt, kể cả `returncode`. Không phải "gần bằng": khi không có flow, các đoạn TWR telescope về
ĐÚNG một phép chia `nav1/nav0` ⇒ trùng bit, không có sai số dồn của phép nhân nhiều tỉ số. `net_flow_vnd`
+ `cash_flows` chỉ được thêm vào JSON **khi kỳ đó có dòng tiền**, chính là để giữ tính chất này.

### (c) Selfcheck `mike/bin/nav_flow_term_selfcheck.py` — **146 assertion PASS**

| Yêu cầu audit | Kết quả |
|---|---|
| Nạp +200tr giữa kỳ ⇒ `return_pct` KHÔNG đổi | PASS: +3,000% (công thức CŨ trên cùng chuỗi NAV: **+22,8%**) |
| Nạp mà thiếu ghi nhận ⇒ cổng CHẶN | PASS: `RuntimeError` "nav-flow BLOCK", nêu đúng ngày 2026-07-07 |
| Rút −100tr (eod) ⇒ không đổi | PASS: +3,000% (công thức CŨ: **−7,2%**, một khoản LỖ không tồn tại) |
| Ghi nhận `deposit` / `market_only` có bằng chứng ⇒ mở cổng | PASS |
| Báo cáo không phải của account (`spend_report_*`) ⇒ không chặn oan | PASS |
| Tên file không có ngày ⇒ CHẶN (không đoán kỳ) | PASS |
| 8 bản ghi hỏng schema ⇒ `CashFlowError` | PASS (thiếu/rỗng `evidence`, date sai, kind lạ, `market_only`≠0, sai dấu, timing lạ, `eod` không có snapshot) |
| Ngưỡng 5,0% có 0 false-positive trên 113 cặp phiên thật | PASS |
| Không flow ⇒ trùng `nav1/nav0 − 1` trên TOÀN BỘ 115 ngày thật | PASS |
| §16: `report_date` mặc định neo ICT (3 TZ ra cùng kết quả) | PASS |
| `deliver()` thật sự GỌI cổng (chống tháo lời gọi) | PASS |

Môi trường: **`python3` 3.10.12 + `$DNA_PYEXE` 3.12.13 × TZ {`Asia/Ho_Chi_Minh`, `UTC`,
`Pacific/Kiritimati`} + `env -u TZ`** → 146/146 PASS ở cả 7 tổ hợp. `nav_period_returns.py --selfcheck`
(8 assertion cũ) cũng PASS ở cả 6 tổ hợp. `tz_anchor_gate.py` trên 4 file: rc=0.

**Mutation test — 6/6 bị giết** (không có mutation nào sống):

| # | Mutation | Kết quả |
|---|---|---|
| M1 | Bỏ hẳn số hạng flow (quay về `nav1/nav0`) | BỊ GIẾT |
| M2 | Ngưỡng cổng 5,0 → 999 | BỊ GIẾT |
| M3 | Bỏ lọc flow ngày inception | BỊ GIẾT |
| M4 | Bỏ kiểm `evidence` rỗng | BỊ GIẾT |
| M5 | Xử `eod` như `bod` | BỊ GIẾT |
| M6 | Tháo lời gọi cổng khỏi `deliver()` | BỊ GIẾT (assert 9b, thêm sau khi M6 sống ở vòng 1) |

### (d) ZaloPay — có nạp/rút nào sau 2026-07-07 chưa? **KHÔNG, và số đã công bố KHÔNG sai**

Không có sổ dòng tiền của broker, nên dùng **đẳng thức lũy kế** (`reconcile_equity.py`, §6 pipeline
bước 3) — một lần nạp/rút chưa ghi sẽ hiện ra đúng ở đây dưới dạng residual. Chạy thật:

| TK | asof | CHÊNH LỆCH (trái−phải) | Dư sau diễn giải | `egg.totalValue` cùng bản ghi | **Dư THẬT sau khi trừ egg** |
|---|---|---|---|---|---|
| ZaloPay | 2026-09-25 | +103.731.346 (+12,14%) | +102.272.560 (+11,96% NAV) | 102.121.977 | **+150.583 = 0,016% NAV** |
| SpaceX | 2026-09-26 | +89.341.393 (+9,98%) | +85.765.426 (+9,58% NAV) | 85.469.401 | **+296.025 = 0,031% NAV** |

⇒ Cả 2 TK: **0 dòng tiền ngoại sinh vật chất kể từ inception** (dư 0,016%/0,031% NAV, dưới ngưỡng
0,3% của chính script). `starting_capital: null` của ZaloPay vì vậy **không gây sai số nào đã công bố**:
baseline = dòng `nav_history` đầu (07-07, 986.585.454đ), và vì không có flow thì TWR ≡ `nav1/nav0`.

**PHÁT HIỆN MỚI, ngoài phạm vi audit gốc — `reconcile_equity.py` BỎ SÓT `egg.totalValue`.**
`grep -c egg mike/bin/reconcile_equity.py` = **0**. Vế phải là `MTM + tiền − nợ margin`, thiếu túi
Trứng vàng ⇒ residual cao giả **+9,6% (SpaceX) / +12,0% (ZaloPay)** và script in
"⚠️ CHƯA GIẢI THÍCH ĐƯỢC" — một **báo động giả đang chạy**. Hệ quả kép: (1) cổng đối soát chặt nhất
của §6 hiện có sàn nhiễu ~10% NAV nên **không dùng được** làm lớp bắt dòng tiền nhỏ; (2) đúng lớp lỗi
coding_guidelines §25 ("tiền không phải một con số", chiều thứ BA `egg.totalValue`). **Chưa sửa** —
ngoài phạm vi 2 việc được giao, đề xuất user cho 1 job riêng.

Ghi nhận thêm: 2 file baseline của ZaloPay KHÔNG khớp nhau — `account_inception.json` dùng dòng
`nav_history` 07-07 (986.585.454), `account_seed_capital.json` dùng NAV 07-06 (987.865.567). Chênh
1,28tr ⇒ tỉ suất "từ khi bắt đầu hoạt động" lệch **0,125pp** tuỳ file nào được coi là gốc (−2,971%
vs −3,096%). Không phải lỗi tính, là 2 định nghĩa mốc khác nhau cho cùng một account — nên chốt một cái.

---

## VIỆC 2 — FAIL-F: annualize theo PHIÊN thay vì theo LỊCH

Đã sửa `bootstrap_nav.py` và `dsr_pbo_annex.py` sang `(t_last − t_first).days / 365.25`, Sharpe dùng
`sqrt(N_ret / yrs_lịch)` — đúng quy ước `simulate_holistic_nav.metrics:1567` (`n_yrs = n_days/365.25`,
`sessions_per_year = len(rets)/n_yrs`), nguồn của mọi số trong `data/results_registry.md`.

Cả 2 file giờ ĐÒI HỎI cột ngày: `bootstrap_nav.load_nav()` trả `pd.Series` có `DatetimeIndex`, không
có ngày parse được thì **SystemExit** — cố ý fail-closed, vì âm thầm rơi về `N/252` chính là con bug này.
`cagr_dd_sharpe(logp, yrs)` bỏ giá trị mặc định cho `yrs` (mặc định là cách `len(logp)/252` sống sót).

Cơ sở đo (cả 2 ledger R3): `N_ret = 3.106`, `2014-01-02 → 2026-06-19` = **4.551 ngày lịch** ⇒
**12,460y lịch** vs 12,325y theo phiên (249,3 obs/năm, không phải 252).

### Bảng cũ → mới, bootstrap (block L=21, B=4000, seed=12345)

| Ledger | basis | yrs | CAGR act | CAGR median | **CAGR 5th** | CAGR 95th | Sharpe act | Sharpe 5th | MaxDD act | MaxDD 5th | P(DD<−30%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3 POST-FIX | session (cũ) | 12,325 | 24,674% | 24,619% | 15,572% | 34,709% | 1,622 | 1,074 | −18,78% | −30,35% | 5,35% |
| R3 POST-FIX | **lịch (mới)** | 12,460 | **24,377%** | 24,324% | **15,392%** | 34,276% | 1,613 | 1,068 | −18,78% | −30,35% | 5,35% |
| R3 PRE-FIX | session (cũ) | 12,325 | 29,220% | 29,131% | 19,423% | 39,679% | 1,832 | 1,280 | −17,79% | −28,11% | 2,77% |
| R3 PRE-FIX | **lịch (mới)** | 12,460 | **28,863%** | 28,775% | 19,194% | 39,176% | 1,822 | 1,273 | −17,79% | −28,11% | 2,77% |

**Kiểm chứng phép đo khớp engine:** CAGR act theo lịch = **24,377%** / **28,863%**, trùng ĐÚNG 2 số pin
registry (24,3775% / 28,8627%). Thiên lệch cũ: **+0,297pp** (post-fix) / **+0,357pp** (pre-fix).
**MaxDD và P(DD<−30%) KHÔNG đổi một chữ số nào** — annualize không chạm drawdown.

### Bảng cũ → mới, DSR/PBO annex (`DSR_R3_CSV` = ledger R3 POST-FIX)

| Đại lượng | Cũ (252) | Mới (lịch) | Ghi chú |
|---|---|---|---|
| **DSR** @N_csv / N=120 / N=200 | 1,0000 / 1,0000 / 1,0000 | 1,0000 / 1,0000 / 1,0000 | **KHÔNG ĐỔI — DSR annualization-INVARIANT** (tính từ SR theo từng quan sát, `sr0`, `T`) |
| **PBO** | 0,5026 | 0,5026 | **KHÔNG ĐỔI** (rank tương đối theo block, không có hệ số năm) |
| SR0(ann) hiển thị | 0,376 / 0,320 / 0,341 | 0,374 / 0,318 / 0,339 | chỉ là hiển thị |
| Sharpe ann (R3) | 1,622 | 1,613 | |
| mean ann-SR trials | 1,775 | 1,765 | |
| bootstrap circular: CAGR 5th / med | 15,6% / 24,6% | **15,4% / 24,3%** | |
| bootstrap stationary(PR): CAGR 5th / med | 15,5% / 24,6% | **15,3% / 24,3%** | |
| MaxDD 5th (circ / stat) | −30,4% / −30,1% | −30,4% / −30,1% | KHÔNG ĐỔI |

**Đính chính framing của audit gốc:** audit nói FAIL-F làm "DSR, PBO" cao giả. Đo thật thì **DSR và
PBO không đổi** — thiên lệch chỉ ở cột CAGR và ở Sharpe *hiển thị*. Số KB cần thay là bootstrap
CAGR, không phải DSR/PBO.

**Về số KB "Bootstrap 5th-pct: CAGR 18,6%":** con số đó thuộc một ledger CŨ. Trên ledger R3 POST-FIX
hiện hành, 5th-pct CAGR theo lịch = **15,4%** — thấp hơn 18,6% chủ yếu vì **return-leg fix** (28,86→24,38),
không vì annualize. Δ do annualize chỉ **−0,18pp** (post-fix) / **−0,23pp** (pre-fix). Đừng gộp 2 nguyên nhân.

⚠️ **Job `Taylor_20260927_043541` chạy song song trên code CŨ** ⇒ mọi CAGR nó báo cao giả ~+0,3pp.
Mike thay bằng cột "lịch (mới)" ở trên. **KHÔNG sửa `data/results_registry.md`** trong job này.
Ghi nhận: cây canonical đang có 1 thay đổi CHƯA COMMIT ở `dsr_pbo_annex.py` (env override `DSR_R3_CSV`,
+7/−2 dòng) từ job đó; tôi đã port đúng thay đổi đó vào worktree để so cũ↔mới công bằng.

### Selfcheck `mike/bin/annualization_basis_selfcheck.py` — 10 assertion PASS

AST-scan (không regex — `yrs = N/252` và `yrs = N/ANN` chỉ khác Name vs Num, và phép chia viết xuống
dòng được). 2 rule:
- **RULE 1 `yrs-per-session`**: gán vào tên chứa `yrs|years|...` mà RHS là phép chia cho hằng 240..260
  (literal HOẶC tên hằng cấp module gán số đó).
- **RULE 2 `sqrt-session-const`**: `sqrt(<hằng 240..260>)` **chỉ trong scope ĐÃ tính CAGR**.
  Thu hẹp theo SỐ ĐO, không theo khẩu vị: bắt mù cho **600 hit** toàn repo, phần lớn là annualize ĐỘ
  BIẾN ĐỘNG (`rv = ret.rolling(20).std()*sqrt(252)`) — hợp lệ. Bất biến thật hẹp hơn: *trong cùng khối
  metric, Sharpe phải cùng hệ quy chiếu với CAGR*. Sau thu hẹp: 496 hit.

**Ratchet per-file** (`mike/kb/annualization_basis_baseline.json`, cùng cơ chế `tz_anchor_gate.py`):
kiểm kê ngày bật **496 vi phạm / 257 file trên 2.866 file `.py`**; đã HẠ 2 key của 2 file vừa sửa về 0
⇒ baseline lưu **488 / 255**, và mọi lần tái phạm ở 2 file đó bị CHẶN. Nợ cũ không bắt sửa, chỉ không được TĂNG.

Chứng minh cổng hoạt động (rc đo trực tiếp, không qua pipe):
- 2 file **canonical CHƯA sửa** → `rc=1`, in đúng 2 dòng CHẶN (`bootstrap_nav.py` 2 vi phạm > baseline 0;
  `dsr_pbo_annex.py` 6 > 0). Vị trí thật: `bootstrap_nav.py:47` (`yrs = N / 252.0`) + `:51` (`np.sqrt(252)`)
  — audit ghi `:51`/`:53`, lệch 4 dòng so với file ở `a808a613`; cùng 2 câu lệnh.
- 2 file **đã sửa** → `rc=0`, 0 vi phạm.
- Selfcheck: bản đúng (365.25) sạch · `N/252.0`+`sqrt(252)` ra đúng 2 hit · chia cho hằng `ANN` bị bắt ·
  phép chia XUỐNG DÒNG bị bắt (regex sẽ trượt) · 4 ca chia-252 hợp lệ KHÔNG bị báo (gồm realized-vol) ·
  đổi mẫu số sang 365.25 ở cả 3 fixture xấu ⇒ sạch.
- Môi trường: `python3` 3.10.12 + `$DNA_PYEXE` 3.12.13 × 3 TZ → 10/10 PASS cả 6 tổ hợp.
  Không parse được ⇒ KÊU ra stderr, KHÔNG gate file đó, KHÔNG đụng baseline (bài học `tz_anchor_gate` vòng 5).

---

## Cần user quyết

1. **Merge 2 branch?** Không tự merge theo chỉ đạo dispatch.
2. **`cp mike/templates/account_cash_flows.json data/account_cash_flows.json`** — chưa tạo file canonical.
   Không tạo thì mọi thứ vẫn chạy như cũ (file thiếu = 0 flow); tạo rồi thì có chỗ ghi khi nạp/rút thật.
3. **`reconcile_equity.py` bỏ sót `egg.totalValue`** (báo động giả +10-12% NAV đang chạy) — job riêng?
4. **ZaloPay 2 mốc baseline lệch 1,28tr (0,125pp)** giữa `account_inception.json` và
   `account_seed_capital.json` — chốt một mốc?
5. **Gắn `annualization_basis_selfcheck.py` vào pre-commit?** Hiện chỉ là công cụ chạy tay + selfcheck.
   Nợ cũ 488/255 đã đóng băng nên bật gate không chặn commit nào đang có.
