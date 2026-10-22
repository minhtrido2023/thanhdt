# N1 + N4 — Sổ lô cho cổ phiếu quyền mua (phương án A, user chốt 22/10/2026 09:40 ICT)

Job `Taylor_20261022_032141` (attempt 2). Nhánh `feat/lag-rights-n1-20261022`, worktree
`/home/trido/thanhdt/WorkingClaude/wt-lag-rights-n1-20261022`, base `4d250ce71` (master). **CHƯA merge** —
chờ Mike arch-review mức cao.

| Commit | Phần |
|---|---|
| `9c0aa2a34` | PHẦN 1 — N1: sổ khai báo theo account + lô quyền kế thừa entry_date gốc |
| `63e0c11d3` | PHẦN 2 — N4: lô quyền chờ VSDC ghi nhận không vào cơ sở hưởng sự kiện CP |

Ghi chú tách commit: `pending_at/pending_qty/exempt_from` (helper N4) nằm sẵn trong
`bin/rights_subscription.py` từ commit 1 (file mới, viết một lượt); commit 1 không gọi chúng ở
consumer nào ⇒ hành vi N4 chỉ bật ở commit 2. Commit 1 tự nó PASS 43/43 + mutants 11/11.

## Thiết kế

**Sổ khai báo** `data/lag_rights/subscriptions.json` (`bin/rights_subscription.py`) — file RIÊNG, append-only,
ghi atomic (tmp + `os.replace`) dưới flock; bản MỚI NHẤT của (account, event_id) có hiệu lực;
`subscribed_qty=0` = huỷ. Trường bắt buộc: account, account_no, ticker, event_id (id dòng quyền mua BQ),
event_hash (phải khớp dòng BQ HIỆN TẠI), exright_date (lấy từ BQ), exercise_ratio, issue_price_vnd
(≠ BQ ⇒ từ chối), subscribed_qty, payment_date, credit_date (mặc định = payment_date), decided_by=user
(khác ⇒ từ chối), at (ISO có múi giờ, thiếu ⇒ từ chối), source (rỗng ⇒ từ chối). Tuỳ chọn:
registered_date (VSDC ghi nhận), listing_date. **Agent không tự ghi** — Mike chạy `--record` khi user
đã trả lời thật. File hỏng ⇒ `RightsSubscriptionError` ⇒ consumer fail-closed. Lọc account_no (§12).

**Lô mới** (`park_holdings.LotBook.rights_credit`): tại credit_date thêm lô `subscribed_qty` @ giá phát hành,
phí 0, book LAG, `entry_date` = entry của các lô hưởng quyền **chụp tại GDKHQ** (không phụ thuộc lô còn hay
đã bán sau đó); nhiều lô hưởng quyền ⇒ chia Hamilton theo KL hưởng. Không có lô hưởng quyền / khai vượt
quyền tối đa ⇒ không thêm, mã UNVERIFIED (fail-closed).

**Khoá chờ niêm yết** (`auto_exit_inject`, `portfolio_status`): phần chưa sellable ghi
'khoá chờ niêm yết' — không cờ quá hạn, không mồ côi, không lệnh; phiên đầu tiên sellable ⇒ auto-exit
bán ngay (quá hạn vì entry kế thừa) theo cơ chế sẵn.

**Consumer cùng đọc sổ**: daily_nav_snapshot (fill phí 0 trong `net_fills_between`) · exdate_frame
(active_nav) · verify_account_snapshot (giá vốn bình quân gồm lô quyền) · reconcile_equity (realized + giá vốn)
· cash_identity (phí 0) · park ledger. Quyền mua KHÔNG đi qua `dividend_adjusted_return` (§21: không phải
cổ tức tiền). Không nộp đủ/mất quyền: chỉ khai số thật ⇒ phần quyền bỏ không sinh lô; NAV vẫn từ KL broker.

**N4**: lô quyền "đang chờ" tại ngày D ⇔ `credit_date ≤ D < (registered_date or listing_date)` (chưa có
ngày ghi nhận ⇒ còn chờ). Sự kiện CP có GDKHQ trong khoảng chờ: KL kỳ vọng = (qty_prev − lô chờ) × tỉ lệ
(`classify_qty_residual(pending_rights=)`); park/verify/reconcile không nhân hệ số cho lô chờ. Broker credit
khác kỳ vọng ⇒ vẫn rc=5/6 (không nới). `pending_rights` mặc định 0 ⇒ phép tính y hệt bản cũ.

## ĐO (chạy trong phiên này)

- `bin/rights_subscription_selfcheck.py` (fixture SCL 14.000 + quyền 5.000 @12.500; `MIKE_LAG_RIGHTS_DIR`
  tạm, `MIKE_BOT_TEST_MODE=1`): commit 1 **43/43**, commit 2 **52/52** dưới `env -u TZ`, `Pacific/Kiritimati`,
  `America/New_York`. Mutants: commit 1 **11/11 killed**, commit 2 **16/16 killed**, control (không đột biến)
  rc=0. Có đối chứng hành vi cũ cho từng consumer (P0, N0, N4a, E0, E2, V0, C0).
- Số chính (fixture): R1 hết lệch +62,5tr (= 5.000 × 12.500) ở reconcile_equity; V1 giá vốn 19.000 @25.394,7
  = costPrice broker; N1 NAV = 19.000 × 20.000 + tiền, rc=0; N4b (20.260−5.000)/1,09 + 5.000 = 19.000 ⇒ phục
  hồi rc=0; N4c broker credit 1.710 ⇒ vẫn rc=5; E3 active_nav credit 1.260 = 14.000 × 9% ⇒ không chặn.
- Hồi quy 36 selfcheck phụ thuộc (grep import/đường dẫn corp_actions, daily_nav_snapshot, exdate_frame,
  auto_exit_inject, portfolio_status, park_holdings, verify_account_snapshot, reconcile_equity,
  lag_rights_exit_hold, cash_identity), base `4d250ce71` vs nhánh `63e0c11d3`, `env -u TZ`: **35/36 giống
  hệt** (rc + số dòng PASS/FAIL). Ngoại lệ `nav_scripts_2account_selfcheck.py` rc=1 trên nhánh khi chạy SONG
  SONG với base — chạy lại riêng: rc=0 PASS. Nguyên nhân: selfcheck này chạy DNSE live + backup/restore
  `nav_history_*.csv` bằng tên cố định ⇒ race khi 2 lượt chồng nhau (xem Sự cố bên dưới). Bảng:
  `regress_base_4d250ce71.tsv`, `regress_branch_63e0c11d3.tsv` (danh sách: `regress_selfcheck_list.txt`) (cột: file, rc, #PASS, #FAIL). Đếm PASS/FAIL bằng grep là thô, so
  sánh hai bên cùng cách đếm.
- `data/corp_actions.json`, `known_position_discrepancies.json`, `active_nav_*.json`: mtime không đổi.
  `data/lag_rights/` không tồn tại trên production (không có khai báo thật nào, không có record SCL).

## SUY LUẬN (chưa đo)

- Ca thật SCL chưa có GDKHQ/giá ⇒ chưa chạy đường `--record` với BQ thật (đã test bằng `fetch` giả).
- Ngày VSDC ghi nhận/niêm yết thật của DNSE chưa quan sát; giả định broker hiện CP quyền trong
  `openQuantity`/`total` từ credit_date nhưng không sellable tới niêm yết (khớp audit B2, chưa đo trên ca thật).
- N4 dựa trên ý kiến legal-vn mức TB-cao — user nên xác nhận văn bản với DNSE. Nếu DNSE lại tính lô chờ vào
  cơ sở: broker credit lớn hơn kỳ vọng mới ⇒ rc=5 (fail-closed, người xử lý) — không sai im lặng.

## Rủi ro còn lại

1. Quên khai `registered_date` ⇒ lô bị coi "đang chờ" tới listing_date; nếu cả hai trống thì chờ vô hạn ⇒ sự
   kiện CP sau đó không nhân lô quyền ⇒ nếu broker thực có nhân ⇒ rc=5 (fail-closed, không sai im lặng).
2. Khai sai KL/ngày credit ⇒ rc=5 (N1b/N1c) — đúng chủ đích nhưng sẽ gây chặn NAV tới khi khai lại.
3. verify_account_snapshot vẫn gộp theo NGÀY (giới hạn cũ đã ghi trong docstring) — lô quyền dùng khoá
   riêng nên N4 đúng, nhưng ca bán xen giữa các lô khác ex_date vẫn ngoài phạm vi.
4. `nav_scripts_2account_selfcheck.py` race backup (có từ trước, không thuộc N1) — đã escalate.

## Sự cố phát hiện trong lúc làm (đã escalate, KHÔNG tự sửa)

`data/execution_logs/nav_history_SpaceX.csv` và `_ZaloPay.csv` có dòng `2026-10-22` ghi lúc 10:00:11 / 10:00:54
ICT (trong phiên) — trước khi job này bắt đầu (10:21). `dnse_raw_2026-10-22.jsonl` cho thấy các lượt
`nav_scripts_2account_selfcheck` chạy chồng nhau quanh 10:00 ⇒ race backup tên cố định để lại dòng rác. EOD
19:10 ghi đè cùng ngày thì tự sạch; nếu EOD rc=5 (như DRI 21/10) thì cron 19:50 bỏ qua vì "đã có dòng" ⇒ NAV
10:00 thành NAV ngày. Bus `question nav-history-bogus-intraday-row-20261022` (urgency high). Taylor cũng chạy
selfcheck này song song lúc ~10:47 (hồi quy) ⇒ góp một lượt race; nội dung hiện tại = bản mtime 10:00:12, các
dòng thật tới 2026-10-20 còn nguyên (10-21 thiếu do rc=5 DRI, có từ trước).

## Hoàn nguyên

- Chưa merge ⇒ bỏ nhánh là xong. Sau merge: `git revert 63e0c11d3` (chỉ bỏ N4) hoặc revert cả hai commit.
- Tắt nóng không cần revert: xoá/đổi tên `data/lag_rights/subscriptions.json` ⇒ mọi consumer về hành vi cũ
  (không khai báo = đúng nhánh đối chứng P0/N0/E0/V0/C0 — ngày nộp tiền lại rc=5, cần người).

## Runbook cho user (khi SCL — hoặc mã LAG khác — có lịch quyền mua)

1. Khi có GDKHQ: bot tự giữ lệnh thoát LAG tới GDKHQ (X1, đã merge). Không làm gì thêm.
2. Trong kỳ nộp tiền: user tự đặt **lệnh tay** đăng ký + nộp tiền trên DNSE cho TỪNG account; ghi lại số CP
   thực mua ở mỗi account (có thể khác nhau, có thể 0).
3. **Ngay sau khi nộp tiền (trước 19:10 cùng ngày)**: nhắn Mike cho từng account: account, mã, số CP mua, giá
   phát hành, ngày nộp tiền (+ ngày CP hiện trên tài khoản nếu khác). Mike chạy
   `python3 mike/bin/rights_subscription.py --record --account <A> --ticker <T> --event-id <id> --event-hash <h>
   --subscribed-qty <n> --issue-price <p> --payment-date <D> --decided-by user --at <ISO+07:00> --source "<link tin nhắn>"`
   (event_id/hash lấy từ tin `rights_issue_alert`/`lag_rights_exit_hold`). Account không mua: không khai.
4. **Kiểm 19:10 (EOD)**: NAV ghi được (không 🚨 KHỐI LƯỢNG ... CHƯA GIẢI THÍCH). Nếu rc=5: so số CP broker với số
   đã khai; sai ⇒ khai lại (bản mới nhất có hiệu lực), Mike chạy `daily_nav_snapshot.py --from-raw` cho ngày đó.
5. Khi VSDC ghi nhận/niêm yết: nhắn ngày ⇒ Mike khai lại cùng event với `--registered-date`/`--listing-date`
   (quan trọng nếu có cổ tức CP/quyền khác có ĐKCC trong khoảng chờ — N4).
6. Phiên đầu tiên CP quyền sellable: bot tự bán lô quyền (đã quá hạn T+25 vì kế thừa entry gốc). Không cần lệnh tay.
7. Kiểm mỗi tối cho tới khi bán xong: `verify_account_snapshot` giá vốn = costPrice broker, `reconcile_equity`
   không lệch +KL×giá phát hành.

---

## Vòng 2 — sửa sau arch-review mức cao (job `Taylor_20261022_041232`, 22/10)

Verdict NEEDS_CHANGES (2 BLOCKING). Cùng nhánh, mỗi bản sửa 1 commit, **CHƯA merge**.

| Commit | Mục |
|---|---|
| `d25a54510` | **B1** — khoá chờ niêm yết chỉ cho lô CHƯA niêm yết, có hạn, có báo |
| `7941ada71` | **B2** — đường sizing production (`broker_statement=True`) cộng lô quyền |
| `ecc300ccf` | NB1 — reconcile_equity không tính phí 0,097% lên lô quyền |
| `9fe8c3374` | NB2 — cash_identity: chân TIỀN ở payment_date, chân KL ở credit_date |
| `fa376eda0` | NB3 — docstring giới hạn `--from-raw` định giá CUM cho lô chờ |

### B1 (auto_exit_inject / portfolio_status / send_plan_report)
- `book_lot_snapshot` trả thêm `rights_lots` (qty + credit_date/listing_date/event_id từng lô).
- `_rights_lock_status(rights_lots, plan_date)`: lô còn khoá ⇔ `listing_date > plan_date`, HOẶC chưa khai
  listing_date và `count_trading_days(credit_date, plan_date) ≤ 10` (lịch VN, so chuỗi ngày ISO, không đọc
  đồng hồ máy — §16). Hết khoá (tới listing_date / quá 10 phiên / không đếm được phiên) ⇒ không khoá, chẩn
  đoán nêu đúng ngày + số phiên đã đọc được gắn vào cảnh báo cắt (`rights_diag`, §29) ⇒ `_send_block_alert` như cũ.
- `_rights_locked_split(tk, qty, unlisted, positions)`: khoá = min(lô chưa niêm yết còn hạn, KL thoát,
  openQuantity − tradeQuantity). Phần còn lại đi qua `_cap_sellable` ⇒ thiếu sellable do lý do KHÁC (lô đã
  niêm yết, SELL book khác chiếm chỗ) vẫn bị cảnh báo cắt. Thiếu openQuantity ⇒ không khoá (fail-loud).
- `rights_locked` giờ được GHI vào plan note (kể cả khi không có lệnh nào), hiện trong `send_plan_report.sh`
  (khối ℹ️, lấy entry auto mới nhất) và lên Discord ℹ️ MỘT lần (dedup theo ticker/book/KL như capped;
  không post bus cho ca chỉ có khoá). State dedup không bị tỉa khi còn khoá.
- Probe arch-review `_rights_locked_split(..., {'SCL':{'sellable':16000}})` (không openQuantity) ⇒ (19000, 0).

### B2 (exdate_frame)
`net_fills_journal_and_broker(..., account_no=)` CỘNG THÊM `rights_subscription.fill_events` (lọc account +
account_no, §12) SAU phép max(journal, statement); ghi note. `classify_positions` truyền account_no. Không có
sổ khai báo ⇒ y hệt cũ (đối chứng E0b/E2b; `compute_active_nav_broker_fills_selfcheck` ALL PASS).

### ĐO (trong phiên này, đường dẫn tuyệt đối trong worktree, `MIKE_BOT_TEST_MODE=1`)
- `bin/rights_subscription_selfcheck.py`: **64/64 PASS** dưới `env -u TZ`, `TZ=Pacific/Kiritimati`,
  `TZ=America/New_York`; `--mutants` **24/24 killed** (control rc=0) dưới cả 3 TZ. Ca mới: P12 (a) đã tới
  listing_date nhưng tradeQuantity 0 ⇒ cắt 5.000→0 kèm chẩn đoán; P13 (b) SELL book khác 2.000 ⇒ khoá 3.000,
  cắt 16.000→14.000 (vòng 1 nuốt im lặng); P14 (c) chưa khai listing_date, 11 phiên > 10 ⇒ cắt 19.000→14.000
  kèm "đã 11 phiên"; P15 đối chứng còn trong hạn ⇒ vẫn khoá; P16 probe; P17 alert ℹ️ 1 lần/⚠️ hết hạn;
  E0b–E3b (`broker_statement=True`); R3 (NB1); C2 (NB2). Mutant mới M17–M24, mỗi cái bị giết đúng ca
  (M17→P13, M18→P12, M19→P14, M20→P12, M21→P17, M22→E1b, M23→R3, M24→C2).
- P1c/P2/P3 cập nhật fixture: khai `listing_date` (tương lai) — vì PAY→T25+1 = 11 phiên, không khai thì
  đúng là quá hạn (chính P14). P2 giờ GHI plan (note rights_locked) theo yêu cầu (3).
- Sửa chập chờn: `run_exit` so NỘI DUNG plan thay vì mtime (1/3 lượt `env -u TZ` FAIL P2 do độ phân giải mtime).
- `send_plan_report_aei_notes_selfcheck.py`: **13/13 PASS** ×3 TZ (T8a/T8b mới); mutant bỏ khối ℹ️ ⇒ T8a FAIL.
- Hồi quy 35 selfcheck (danh sách `regress_selfcheck_list.txt`, BỎ `nav_scripts_2account_selfcheck.py`),
  `env -u TZ`, `python3`, chạy TUẦN TỰ: nhánh `fa376eda0` vs base `4d250ce71` chạy CÙNG lúc trong worktree
  tạm (`git worktree add --detach`, đã gỡ) ⇒ **35/35 giống hệt** (rc, #dòng PASS, #dòng FAIL), mọi rc=0.
  Bảng: `regress_branch_vong2_fa376eda0.tsv`, `regress_base_4d250ce71_vong2.tsv`. So với bảng base CŨ của vòng 1
  có 3 file lệch số dòng grep (corp_action_broker_detect, portfolio_status, daily_nav_snapshot_from_raw) —
  base chạy lại cùng lúc cho ra y hệt nhánh ⇒ lệch do môi trường/thời điểm/interpreter (bảng cũ chạy py3.12),
  không do code.
- `data/` thật: không selfcheck nào ghi. `nav_history_{SpaceX,ZaloPay}.csv` đổi mtime 11:24:29 trong lúc sweep
  — ĐÃ ĐỐI CHIẾU: đó là Mike xoá 2 dòng rác 10-22 theo user duyệt (bus answer
  `nav-history-bogus-intraday-row-20261022` 04:24:36Z, backup `*.bak_pre_rm_bogus_20261022`); giá trị giữ
  nguyên, chỉ bỏ dòng 10-22 — nhưng file mới đổi CRLF→LF (backup 79/76 dòng có `\r`, file mới 0) ⇒ lần ghi
  csv kế tiếp sẽ trộn kiểu xuống dòng (csv reader đọc được; ghi chú cho Mike).

### Non-blocking còn lại (KHÔNG sửa vòng này)
- **NB2 phần reconcile_equity**: chân tiền vẫn ở credit_date. Chỉ lệch khi khai `credit_date > payment_date`
  VÀ chạy reconcile với asof nằm giữa hai ngày đó (tiền đã rời, CP chưa về ⇒ residual ≈ −KL×giá phát hành).
  Sửa đúng cần khái niệm "phải thu CP đã nộp tiền" trong vế trái — không phải vài dòng. Mặc định credit =
  payment ⇒ không phát sinh. Runbook: nếu khai credit khác payment, đừng đọc reconcile_equity trong khoảng đó.
- **NB3**: chỉ ghi docstring `daily_nav_snapshot.py` + runbook dưới. Mức lệch "~0,8% NAV/1 ngày" là ƯỚC LƯỢNG
  của arch-review, CHƯA đo trong phiên này.
- **NB4**: N4 chưa wire vào `dividend_adjusted_return` — lô quyền chờ trong ngày có cổ tức CP: tỉ suất
  per-position có thể lệch; đường đó vốn fail-closed (`UNVERIFIED` khi chưa đối soát broker, §21) ⇒ không vào
  báo cáo nhà đầu tư im lặng. Chưa sửa.
- **NB5/NB6**: không sửa theo chỉ đạo dispatch; nội dung ở verdict arch-review.

### Runbook bổ sung (thay bước 5–6 ở trên)
5. Khi biết ngày niêm yết: Mike khai lại cùng event với `--listing-date` (và `--registered-date` nếu có).
   **Chưa khai thì khoá chỉ giữ tối đa 10 phiên kể từ credit_date** — sau đó plan/Discord hiện ⚠️ cắt kèm
   "đã N phiên > hạn 10 phiên — cần khai --listing-date hoặc kiểm broker". Đó là tín hiệu cần hành động, không phải lỗi.
6. Trong thời gian khoá: báo cáo plan có dòng ℹ️ "lô CP quyền mua KHOÁ chờ niêm yết"; Discord ℹ️ một lần.
   Tới listing_date mà broker vẫn chưa cho bán ⇒ ⚠️ cắt kèm "đã tới ngày niêm yết theo khai báo nhưng broker
   vẫn chưa cho bán" ⇒ kiểm DNSE.
8. `--from-raw` cho ngày broker ghi có sớm cổ tức CP/thưởng trong lúc có lô quyền chờ VSDC: đối chiếu tay NAV
   với DNSE trước khi đưa vào báo cáo (NB3), hoặc dùng dòng EOD ngày kế tiếp.
