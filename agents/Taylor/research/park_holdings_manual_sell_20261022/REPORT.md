# park_holdings — đối soát lệnh BÁN TAY qua statement DNSE (DRI 21/10) — 2026-10-22

Job `Taylor_20261022_143258` · nhánh `fix/park-holdings-manual-sell-20261022` @ `30fe3ba7b`
(worktree `/home/trido/thanhdt/WorkingClaude/wt-park-manual-sell-20261022`) · **CHƯA merge master**,
chờ arch-review (đường tiền).

## Prompt (tóm tắt nguyên ý, user duyệt 22/10 21:32 ICT, thread plan-approval)
Vá `mike/bin/park_holdings.py` để sổ lô đối soát được lệnh bán tay DRI 21/10 (SpaceX −1.200, ZaloPay
−600 @15.400), gỡ BLOCKED_RECONCILE của L1 park-trim + L2 JIT-unpark. Tái dùng hợp đồng f0e293c30.
Yêu cầu: (1) bán trong statement chưa có trong journal → FIFO theo ticker (mục 4), lọc tiểu khoản §12;
(2) chống đếm đôi; (3) lệch dư vẫn fail-closed, không tự sửa lô; (4) statement thiếu/hỏng → hành vi
cũ; (5) đo thật 22/10; (6) selfcheck + mutant dưới `env -u TZ` + TZ lạ, chạy selfcheck liên quan;
(7) worktree/nhánh riêng, không merge, không đụng plan/trading_rules/cron.

## Thay đổi (`git diff --numstat master`: park_holdings.py +86/−1, selfcheck mới)
- `statement_extra_sells()`: đọc `dnse_khoplenh_broker_confirm_*.csv` trong `exec_dir`, ngày ∈
  [ngày SAU ngày chụp bootstrap, asof], qua `broker_fill_confirm.load_broker_fills(allow_fetch=False)`
  (lọc tiểu khoản). Theo (ngày, mã, chiều): thêm `statement − journal` nếu > 0 — journal ở đây là
  CHÍNH các fill sổ đã replay ⇒ fill bot không bị trừ lần 2 (= `max(journal, statement)` như f0e293c30).
- Chỉ chiều BÁN được áp, đặt ở `<ngày>T23:59:59`, `book=""` ⇒ `LotBook.sell` nhánh FIFO theo ticker
  ⇒ ticker gắn UNVERIFIED (luật mục 4 có sẵn). MUA chỉ-có-ở-statement: KHÔNG thêm lô, chỉ ghi chú ⇒
  đối soát chặn. Journal > statement: giữ journal + ghi chú. Statement thiếu/hỏng: ngày đó chỉ journal.
- `park_holdings(broker_statement=True)` mặc định bật; `False` = hành vi cũ.

## Đo thật 22/10 (DNSE live, read-only)
| | master | nhánh |
|---|---|---|
| SpaceX reconcile.ok / DRI sổ vs broker | False / 3.700 vs 2.500 | **True / 2.500 = 2.500** |
| ZaloPay reconcile.ok / DRI sổ vs broker | False / 1.900 vs 1.300 | **True / 1.300 = 1.300** |
| SpaceX L1 park-trim | BLOCKED_RECONCILE | BLOCKED_ALL_NAMES (*) |
| SpaceX L2 jit-unpark (plan 23/10) | BLOCKED_RECONCILE | NO_TRIGGER |
| ZaloPay L1 park-trim | BLOCKED_RECONCILE | NO_TRIM |
| ZaloPay L2 jit-unpark (plan 23/10) | BLOCKED_RECONCILE | NO_TRIGGER |

(*) target_park=0 ⇒ muốn bán sạch PARK 9.186.050đ nhưng mọi mã còn lại < 1 lô / sellable 0
(MBB 65cp, TPB/VIB 0cp…) — không liên quan DRI. Output: `l1_*_{master,patched}.json`,
`l2_*_{master,patched}.json` trong thư mục này (ghi bằng `--out` vào đây, KHÔNG ghi plan).

Trên 23 statement hiện có, bản vá chỉ thêm đúng 1 lệnh/account (DRI 21/10); không ngày nào khác phát
sinh ghi chú (không có journal>statement, không có MUA lạ). DRI cả 2 account nằm 100% ở book
`DISCRETIONARY_SPECIAL` ⇒ cờ UNVERIFIED trên DRI không ảnh hưởng PARK/LAG.

## Selfcheck
- Mới `bin/park_holdings_statement_selfcheck.py`: 13 kịch bản (2 account ra DRI 2.500 vs 1.300 — KHÁC
  nhau; FPT bot chỉ trừ 1 lần; lệch dư 100cp vẫn chặn; cờ tắt/statement thiếu/hỏng NaN ⇒ hành vi cũ;
  MUA không thêm lô; ngày chụp snapshot bỏ qua; journal>statement) + 4 mutant đều bị bắt (M1 bỏ lọc
  tiểu khoản, M2 bỏ chống đếm đôi, M3 cho lệch dư lọt, M4 áp MUA chỉ-có-ở-statement). rc=0 dưới
  `env -u TZ`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati`. Stdout: `selfcheck_stdout.txt`.
- Liên quan (§23), chạy `env -u TZ` ở nhánh và master, output khác nhau CHỈ ở timestamp:
  compute_park_trim (122/0), compute_jit_unpark (ma trận TZ PASS), corp_action (93/0), exdate_frame
  (63/63), corp_actions_skip_unsupported, auto_exit_inject (113/0), rights_subscription (64/64),
  park_rail_consistency, merge_park_orders, compute_active_nav_broker_fills — tất cả rc=0.

## Cho arch-review
- Khớp theo (ngày, mã, chiều) như f0e293c30 — KHÔNG theo giá (prompt nhắc "qty/giá", nhưng commit
  tham chiếu khớp theo tổng KL ngày; giữ đúng hợp đồng đã APPROVED).
- Statement không có giờ khớp ⇒ đặt cuối ngày. Ca rủi ro lý thuyết: corp-action có
  `broker_effective_ts` cùng ngày với lệnh bán tay sẽ được áp TRƯỚC lệnh bán (thứ tự ts) — lệch, nếu
  có, sẽ lộ ở cổng đối soát chứ không trôi im lặng.
- `portfolio_status.book_lot_snapshot`/`auto_exit_inject` cũng dùng `park_holdings` mặc định ⇒ cũng
  thấy lệnh bán tay (mong muốn: sổ đúng broker hơn).
