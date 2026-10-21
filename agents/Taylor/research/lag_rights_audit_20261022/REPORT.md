# Audit quyền mua (rights issue) cho mã đang giữ + vá cờ phải thu — job Taylor_20261021_165512

Nhánh `feat/lag-rights-audit-20261022`, worktree `/home/trido/thanhdt/WorkingClaude/wt-lag-rights-20261022`.
**KHÔNG merge, KHÔNG wire cron, KHÔNG đổi hành vi production.** Chi tiết + lệnh tái lập từng phần:
`B1_alerts.md`, `B2_nav_chain.md`, `B2b_B3_park_exit.md` (+ script `b1_*/b2_*/b3_*.py`, output `*_output.txt`).
Thử nghiệm chạy trên fixture/sandbox; không gửi Discord/bus, không ghi data/state production
(mtime `nav_history_SpaceX.csv`, `active_nav_SpaceX.json`, `corp_actions.json` không đổi — B2 đo).

Nhãn: **ĐO** = chạy lệnh/đọc file trong job này; **SUY LUẬN** = chưa đo trực tiếp.

## Tóm tắt cho user (trước vòng plan CN 25/10)

1. **Hệ thống hiện KHÔNG cảnh báo kịp quyền mua.** Sự kiện SCL 15,38% (trạng thái P, chưa có ngày/giá)
   có trong bảng suốt 61 snapshot nhưng 0 cảnh báo (ĐO). Khi có ngày, cảnh báo chỉ tới khoảng 2 phiên
   trước GDKHQ và không có số CP được mua, giá hay số tiền (ĐO). Gói DD LAG không nhắc quyền mua vì chỉ xét cổ tức tiền (ĐO).
2. **Ngày user nộp tiền mua quyền, chuỗi NAV sẽ CHẶN** (`daily_nav_snapshot` rc=5 ⇒ `compute_active_nav` rc=6, ĐO
   trên fixture). Không có đường phục hồi trong code. Cách thoát duy nhất là làm thủ công như MBB 28/08:
   dòng journal `CORP_ACTION/RIGHTS_SUBSCRIPTION` + `known_position_discrepancies` + ack cash_identity
   (artifact thật: `data/execution_logs/exec_SpaceX_2026-08-28_journal.csv`, `data/known_position_discrepancies.json`).
3. **L1/L2 park bị `BLOCKED_RECONCILE` toàn tài khoản** từ ngày CP quyền hiện trên broker (ĐO, fixture). L2 bị chặn
   thì lệnh mua cần unpark không được cấp vốn.
4. **Thoát T+25 không biết luật "không bán trước GDKHQ"** (ĐO: auto_exit không đọc corp-action). Nếu T+25 rơi trước GDKHQ thì
   vẫn bán 14.000 và mất quyền. Còn nếu đã bán trước khi 5.000 CP quyền về thì lô này mồ côi, không ai thoát và không có cờ (ĐO).
5. **⚠️ Không được thêm record `RIGHTS` vào `data/corp_actions.json`.** Validator raise ở mọi record kể cả
   PROPOSED ⇒ park_trim/jit_unpark crash, auto-exit chặn mọi book, mọi account (ĐO cơ chế, `corp_actions.py:75,174`; tác động
   toàn fleet là SUY LUẬN).

**Việc khuyến nghị cho SCL (vào lệnh ~26/10), chưa cần code:** Mike/DollarBill theo dõi tay sự kiện SCL 15,38%.
Khi vendor điền ngày, so GDKHQ với ngày thoát T+25 dự kiến. Nếu GDKHQ rơi trong lúc đang giữ ⇒ user quyết HOLD tay
lệnh thoát tới GDKHQ, vì code chưa có cơ chế; P3 bên dưới cần user duyệt. Ngày nộp tiền ⇒ chuẩn bị quy trình MBB trước 19:10.

## Bảng phát hiện

| # | Mức | Module (file:line) | Hành vi thật | Nhãn |
|---|---|---|---|---|
| B1.1 | CAO | `corp_action_daily.py:1264-1268` | chỉ lấy sự kiện có `exright_date` trong 10 ngày; dòng P/NULL bỏ qua im lặng; BVB/NVL lượt đầu thấy = 2 phiên trước GDKHQ | ĐO (vintage thật `corporate_action_snapshots`) |
| B1.2 | CAO | `corp_action_daily.py:1282-1295`, `corp_action_lib.py:155-161` | tin không có giá phát hành, ngày chốt, số CP, số tiền; reader không SELECT `record_date/issue_volumn/total_value/id` | ĐO |
| B1.3 | CAO | `nav_exdate_forecast.py:228-252` | xếp Rights như cổ tức CP: in "KL tăng ~35,71%", "giá giảm ~26,32%" (TERP thật −11,50%; DIG báo 18,83% so với thật 8,35%) — dễ khiến user tưởng CP tự về | ĐO |
| B1.4 | CAO | `trading_bot/due_diligence.py:631-634` | `EXDATE_SAP_TOI` chỉ `codes=("DIV",)` ⇒ gói DD LAG SCL không nhắc quyền mua đang treo | ĐO |
| B1.5 | — | dedupe | P→có ngày được báo ngay lượt đầu (không dedupe theo id) — không phải lỗi | ĐO |
| B1.6 | THẤP | `corp_action_broker_detect.py:785-830`, `locked_shares.py:80-93` | không phải cảnh báo trước GDKHQ; locked_shares chỉ thấy sau khi đã nộp tiền | ĐO |
| B1.7 | — | BQ schema | `tav2_bq.corporate_action` (38 cột) KHÔNG có hạn đăng ký/nộp tiền; giá phát hành chỉ suy được `total_value/issue_volumn` và thường chỉ có khi trạng thái D (sau GDKHQ) | ĐO |
| B2.1 | CAO | `daily_nav_snapshot.py:464-513,1395-1447` → `compute_active_nav.py:487-508` | ngày nộp tiền (CP quyền vào `openQuantity` ngay — tiền lệ MBB 08-28): rc=5 → rc=6; `corp_actions` không có loại RIGHTS | ĐO (fixture + dnse_raw MBB) |
| B2.2 | CAO | cổng giá tối cum | nếu broker hạ marketPrice về TERP trước 19:10 ⇒ rc=4 ở cả `--from-raw`, mất dòng NAV ngày đó | cơ chế ĐO; thời điểm hạ giá SUY LUẬN (DRI/VPB 19:07, MBB 19:32) |
| B2.3 | TB | `daily_nav_snapshot.py:507` | SCL có cổ tức CP 9% (GDKHQ 06/11/2025) nằm trong cửa sổ chờ CP quyền: expected tính cả 5.000 CP quyền ⇒ rc=5/6 nếu CP quyền không hưởng | cơ chế ĐO; quyền hưởng SUY LUẬN (cần Wendy) |
| B2.4 | TB | `verify_account_snapshot.py:602-623` | giá vốn chỉ dựng từ lệnh sàn: 14.000 @30.000 (P&L −140tr) so với broker 19.000 @25.394,74 (−102,5tr), vẫn `verified=True` | ĐO |
| B2.5 | TB | `reconcile_equity.py:215,283,334,339` | lệch vĩnh viễn +62,5tr (rc=1); `missing_fills_broker_confirmed` bị bỏ qua khi có `--starting-capital` (SpaceX có) | ĐO |
| B2.6 | TB | `cash_identity.py:104` | dạng B dán nhãn "nghi tiền RÚT", NAV −5,86% vượt cổng 5%; không có kind cho tiền nộp quyền mua | ĐO (dạng B là GIẢ ĐỊNH broker) |
| B2.7 | TB | NAV/active_nav | thiếu giá trị quyền từ GDKHQ tới ngày nộp (≈5.000×(P−12.500), 46tr ≈3,8% NAV trên fixture) | ĐO trên fixture |
| B2.8 | THẤP | `dividend_adjusted_return.py` | phân loại đúng `ISS_NONFREE` (không phải cổ tức tiền §21); glitch BQ 2025-10-23 ⇒ UNVERIFIED (chặn công bố, không báo sai) | ĐO (BQ thật) |
| B2.9 | THẤP | `known_position_discrepancies.json` (MBB) | lý do ghi "broker chưa ghi có" trái với dnse_raw (openQuantity +110 từ 08-28) | ĐO |
| B2b.1 | CAO | `park_holdings.py:687`, `compute_park_trim.py:413`, `compute_jit_unpark.py:370` | `Σ lô ≠ openQuantity` ⇒ `BLOCKED_RECONCILE` L1+L2 cả tài khoản (SCL không trong pool); không tự mở lại | ĐO |
| B3.1 | CAO | `auto_exit_inject.py` + `portfolio_status.py:357-363` | đã bán 14.000 rồi 5.000 mới về ⇒ mồ côi, không lệnh/cờ | ĐO |
| B3.2 | TB | `auto_exit_inject.py` | CP về khi chưa bán (19.000/14.000) ⇒ chặn SCL + cờ + alert; không cố bán 19.000 nhưng giữ luôn 14.000 đã tới hạn | ĐO |
| B3.3 | TB | `auto_exit_inject.py` (grep exright/corp_action rỗng) | không HOLD tới GDKHQ quyền mua; `exdate_gate.py:175-187` chỉ chặn lệnh đúng ngày GDKHQ | ĐO (grep) / SUY LUẬN (exdate_gate) |
| B3.4 | — | `auto_exit_inject.py:89-129,290-309,386` | KL bán = sổ lô theo book, cắt theo sellable ⇒ không bị broker từ chối; trước khi CP quyền về bán đúng 14.000 | ĐO |
| B3.5 | TB | `corp_actions.py:174` | record RIGHTS (kể cả PROPOSED) ⇒ `CorpActionError` cho mọi consumer | ĐO cơ chế |
| B3.6 | TB (ngoài LAG) | stop-loss BAL | nếu costPrice broker không hạ ở GDKHQ ⇒ giảm thật −6,3% so với TERP có thể kích stop −20% | SUY LUẬN (GIẢ ĐỊNH costPrice) |
| B3.7 | THẤP | L1/L2 cash | tiền nộp 62,5tr làm giảm cash_start L2 — đúng thiết kế | ĐO |
| B3.8 | THẤP | `plan_position_drift_check.py` | báo DRIFT đúng sự kiện, rc=0, không drift giả | ĐO |

## VIỆC A — `EQ_PHAI_THU_TANG` (commit `7c1fa3488`)

- Tra cứu (ĐO): `bigquery_dictionary.json` chỉ có `AR_P0` = "Accounts receivable"; schema `ticker_financial` 174 cột,
  **không có cột tách phải thu khách hàng / trả trước người bán**. `AdvCust_P*` là NGƯỜI MUA trả trước (nợ phải trả):
  SCL 2026Q3 `AdvCust_P0` = 1,8 tỷ, không phải 86,6 tỷ trả trước người bán.
- ⇒ Theo đề bài nhánh KHÔNG: **giữ cờ trên tổng phải thu (fail-closed), không đổi ngưỡng/cờ khác**; bằng chứng cờ và
  `working_capital.receivables.basis` ghi rõ "không tách được phải thu khách hàng/trả trước — kiểm thuyết minh BCTC".
- SCL thật: AR 203,5 tỷ so với 78,5 tỷ (+159%), doanh thu +89% ⇒ vẫn FLAG (ĐO trong selfcheck).
- Selfcheck `bin/lag_dd_gate_selfcheck.py`: thêm 6 case (SCL số thật; từ-0-lên; AdvCust lớn không được trừ; cờ tồn kho
  không mang ghi chú) + 4 mutant ⇒ **3 TZ PASS, 36/36 mutant killed** (ĐO).

## B4 — đề xuất cảnh báo (code trên nhánh, CHƯA wire)

`bin/rights_issue_alert.py` (chỉ CẢNH BÁO, chỉ đọc BQ + `data/execution_logs/active_nav_*.json`):
- 3 giai đoạn, dedupe riêng: **ANNOUNCE** khi lần đầu thấy (kể cả P, ngày NULL), **DATED** khi có/đổi GDKHQ,
  **REMIND** mỗi phiên khi còn ≤3 phiên cum. State ghi atomic NGAY sau mỗi lần gửi thành công (§5).
- Nội dung: tỉ lệ, GDKHQ, ngày chốt, giá phát hành (`value_per_share` hoặc `total_value/issue_volumn`, nếu thiếu thì ghi "CHƯA CÓ"),
  ghi rõ BQ không có hạn nộp tiền, **số CP được mua = floor(KL × tỉ lệ) và số tiền cần chuẩn bị theo từng account**,
  nhắc luật 21/10 và quy trình MBB.
- Hồi cứu không nhìn trước (`public_date ≤ asof`); không thấy file vị thế ⇒ rc=2, không kết luận "không giữ mã nào".
- Dry-run thật 2026-10-22: 7 mã đang giữ, 0 quyền mua (ĐO). Với vị thế giả SCL 14.000 trên BQ thật: báo ANNOUNCE
  15,38% ⇒ 2.153 CP, chưa có giá; asof 2025-10-13 ⇒ REMIND 5.000 CP × 12.500 = 62.500.000đ (ĐO).
  ⚠️ Hồi cứu dùng dòng BQ hiện tại; bảng bị ghi đè tại chỗ, nên giá/trạng thái lúc đó có thể chưa có (B1.7).
- Selfcheck `bin/rights_issue_alert_selfcheck.py`: 22 case, **3 TZ PASS, 11/11 mutant killed** (ĐO).
- Để wire (cần duyệt): cron T2-T6 sau `corp_action_daily` (tra `kb/cron_registry.md` §11) với `--send` ⇒ Trading Daily
  (`trading_daily`).

Các vá nhỏ cùng hướng, **chưa làm**, đề xuất:
- `due_diligence._get_upcoming_exdate`: thêm nhánh Rights ⇒ cờ `EXDATE_SAP_TOI` cho quyền mua kể cả khi ngày NULL.
  Chạm cổng DD LAG ⇒ cần arch-review.
- `nav_exdate_forecast.build_event_line`: tách Rights khỏi SHARE_EVENT, sửa câu "KL tăng" và dùng TERP. Chỉ là text cảnh báo.

## Patch đề xuất chạm NAV/sizing/lệnh — ⚠️ CẦN arch-review + user duyệt (chưa áp)

Diff chi tiết + selfcheck/mutant đề xuất có trong `B2_nav_chain.md` và `B2b_B3_park_exit.md`.
- **N1 (gốc của B2.1/B2.4/B2.5/B2b.1/B3.1):** một sổ "fill broker xác nhận ngoài sàn" kind `rights_subscription`
  (tái dùng `account_seed_capital.json → missing_fills_broker_confirmed`, phí 0). Thêm lô quyền vào sổ lô theo account,
  giá 12.500; `net_fills_between`/`verify_account_snapshot`/`reconcile_equity`/park ledger cùng đọc. User cần chọn
  entry_date của lô quyền (thừa hưởng entry gốc hay tính từ ngày credit) — đây là quyết định giao dịch.
- **N2:** cổng giá tối cum chấp nhận marketPrice ≈ TERP khi có sự kiện Rights đã có giá (B2.2).
- **N3:** loại Rights khỏi `is_share_event` (`classify_qty_residual`).
- **N4:** quyền hưởng cổ tức CP của CP quyền đang chờ — cần Wendy xác minh trước khi viết code.
- **X1:** auto-exit HOLD lệnh thoát mã có quyền mua tới GDKHQ (luật 21/10) — chạm lệnh ⇒ user duyệt.
- **X2:** mã mồ côi (broker còn, sổ lô hết) phải hiện vào `blocked` của auto-exit + alert.
- **X3:** `corp_actions.load_all` bỏ qua record chưa CONFIRMED bị lỗi thay vì raise toàn cục.
