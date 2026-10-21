# B2b + B3 — Quyền mua trên mã LAG: park/unpark/drift (B2b) và auto-exit T+25 (B3)

Audit 2026-10-22 (Taylor, subagent). Chỉ đọc code + fixture giả trong `mktemp -d`. Không sửa code
production, không ghi `data/`, `mike/data`, `mike/state`, không có bus/Discord (`MIKE_BOT_TEST_MODE=1`,
`AUTO_EXIT_TEST_MODE=1`, subprocess recorder bắt được 0 lời gọi). Code đọc từ worktree
`wt-lag-rights-20261022` (HEAD `7c1fa3488`); `trading_bot/` từ `WorkingClaude/trading_bot`.
Interpreter: `$DNA_PYEXE` (`/home/trido/thanhdt/wc_venv/bin/python`).

Kịch bản fixture: account giả `RightsAcct`/`8888888888` (+1 record nhiễu account `7777777777` trong
mọi dnse_raw để thử §12). PARK FPT 6.000@100.000 + MBB 30.000@25.000 (= 1.350tr). LAG SCL 14.000cp mua
@30.000 ngày 2026-10-26 (FILL journal book=LAG). Quyền 14:5 @12.500 ⇒ 5.000cp, nộp 62.500.000đ.
Giá tham chiếu ngày GDKHQ = (30.000 + 5/14×12.500)/(19/14) = 25.394,7 → fixture dùng 25.400.

## 0. DNSE có field nào cho "CP chờ về / chưa giao dịch được" không?

- **ĐO** — key của dòng `positions` DNSE (bản ghi cuối `data/execution_logs/dnse_raw_2026-10-21.jsonl`):
  `accountNo, accumulateQuantity, averageClosePrice, breakEvenPrice, closedQuantity, costPrice,
  createdDate, id, loanPackageId, marketPrice, marketType, modifiedDate, openQuantity, side, status,
  symbol, tradeQuantity`. Không có field receiving/pending/right. `receivingT0/T1/T2` chỉ có ở
  `PHSFlashBroker.get_positions` (`trading_bot/brokers.py:1477-1481`, class bắt đầu :1380), không phải DNSE.
- **ĐO** — cách DNSE hiện CP chưa niêm yết, theo các ca CP thưởng thật: VPB ZaloPay `openQuantity/tradeQuantity`
  1.200/1.200 (09-22) → 1.512/1.200 (09-23, ngày credit, 1 phiên TRƯỚC ex 09-24) → vẫn 312/0 tới 2026-10-21. TPB
  SpaceX 30/0 từ 10-02 tới 10-21. Nghĩa là CP chưa niêm yết NẰM TRONG `openQuantity` ngay từ lúc credit, còn
  `tradeQuantity` loại phần đó ra. `bin/locked_shares.py:1-5` cũng dựa trên đúng quan sát này (có nêu quyền mua).
- **GIẢ ĐỊNH, chưa đo** — với CP quyền mua: DNSE credit vào `openQuantity` lúc nào (nhiều tuần sau GDKHQ, hay
  chỉ lúc niêm yết), và khoản nộp 62,5tr làm giảm `totalCash`/`availableCash` ngay hay không. Vì vậy cả hai dạng
  đều được thử: **dạng A** = KL `openQuantity` tăng khi credit, `tradeQuantity` chưa tăng; **dạng B** = KL chỉ
  tăng lúc niêm yết.

## 1. Kết luận chung

Gốc của mọi lỗi dưới đây là một chỗ: **sổ lô (`park_holdings.LotBook`) không có cách nào nhận 5.000cp
quyền mua.** Hai lý do: (i) user tự mua quyền bằng tay nên journal không có dòng FILL nào; (ii) sổ
`corp_actions` chỉ nhận `STOCK_DIVIDEND/BONUS_ISSUE/SPLIT` (`bin/corp_actions.py:75,112`). Khi broker
hiện 5.000cp này, cổng đối soát `Σ lô == openQuantity` (`bin/park_holdings.py:687`) thấy lệch ⇒ SCL thành
UNVERIFIED ⇒ L1 và L2 bị BLOCKED cho **cả tài khoản**, còn auto-exit thì chặn SCL hoặc bỏ sót 5.000cp
mà không báo gì (tuỳ thời điểm). Tình trạng này kéo dài cho tới khi có người sửa sổ, mà hiện chưa có đường
sửa nào hợp lệ.

| # | Module / tình huống | Hành vi thật | Nhãn | Mức |
|---|---|---|---|---|
| F1 | L1 `compute_park_trim` + L2 `compute_jit_unpark` từ ngày CP quyền hiện ở broker | `BLOCKED_RECONCILE` toàn tài khoản (không trim, không unpark để tài trợ lệnh mua BAL/LAG) | ĐO | **CAO** |
| F2 | auto-exit, CP mới về **sau** khi 14.000 đã bán | 5.000cp mồ côi: không có lệnh, không có cờ chặn, in "không có candidate" | ĐO | **CAO** |
| F3 | auto-exit, CP mới về khi 14.000 **chưa** bán | Chặn SCL (cả 14.000 đã tới T+25), cờ `blocked` + cảnh báo. Không bán | ĐO | TRUNG BÌNH |
| F4 | auto-exit không kiểm GDKHQ quyền mua | T+25 rơi trước GDKHQ ⇒ vẫn chèn SELL 14.000 (bán ở đó là mất quyền) | ĐO | TRUNG BÌNH (chạm lệnh) |
| F5 | Ghi record `event_type: RIGHTS` vào corp_actions (cách sửa "tự nhiên") | `CorpActionError` cả khi chỉ là PROPOSED ⇒ crash park_holdings; auto-exit chặn CẢ book LAG lẫn BAL; sổ dùng chung nên ảnh hưởng mọi account | ĐO | TRUNG BÌNH |
| F6 | Workaround BONUS_ISSUE ×19/14 | Đối soát khớp lại, nhưng giá vốn lô sai (22.105 thay vì 25.395) và lô mới thừa hưởng entry_date gốc. Không cứu được ca F2 | ĐO | (không khuyến nghị) |
| F7 | Khoản nộp 62,5tr ngoài plan | L1 hiện tại (R3=0.0): delta không đổi. Nếu R3=0.30: trim thêm 18,75tr (MBB +300cp). L2: cash_start −62,5tr. Đúng theo thiết kế | ĐO | THẤP (không phải lỗi) |
| F8 | Ngày GDKHQ (KL không đổi, giá giảm) | park_holdings đối soát khớp, L1/L2 chạy bình thường | ĐO | không lỗi |
| F9 | `plan_position_drift_check` | Báo DRIFT đúng sự kiện (giá −15,3% quanh GDKHQ; KL ×1,3571 tối hôm credit), rc=0, không chặn. Không có drift giả | ĐO | THẤP |
| F10 | BAL có quyền mua: stop-loss −20% đo trên costPrice broker | Nếu DNSE không hạ costPrice ở GDKHQ (GIẢ ĐỊNH), thì chỉ cần giảm thật −6,3% so với TERP là kích stop-loss | ĐO hàm thuần + GIẢ ĐỊNH | TRUNG BÌNH (ngoài LAG) |
| F11 | `exdate_gate` ngày GDKHQ | Lệnh SELL của mã có quyền mua bị BỎ: nếu thiếu `RIGHTS_ISSUE_PRICE` thì G5 fail-closed; nếu có thì bị coi `changes_share_count` | SUY LUẬN (đọc code) | THẤP (an toàn, lý do in sai) |

## 2. B2b — park_holdings / L1 / L2 / drift

Lệnh: `$DNA_PYEXE b3_b2_park_unpark.py` → `b3_b2_park_unpark_output.txt` (rc=0). R3 thật đọc CHỈ-ĐỌC
`park_target_from_rules(data/trading_rules.json)` = **0.0** (PARK OFF từ 2026-10-01). Ngày: E=2026-10-26,
GDKHQ T0=2026-11-09, nộp tiền 11-16, credit (dạng A) 12-03, niêm yết 2027-02-02.

| Giai đoạn | reconcile | L1 | L2 (lệnh mua LAG HPG 120tr) |
|---|---|---|---|
| S0 trước GDKHQ | ok | TRIM, pool 1.800,0tr, delta −1.350,0tr | NO_JIT_NEEDED, cash_start 450,0tr |
| S1 ngày GDKHQ (14.000/14.000 @25.400) | ok | TRIM, pool 1.800,0tr | NO_JIT_NEEDED 450,0tr |
| S2 sau nộp 62,5tr | ok | TRIM, pool 1.737,5tr, delta −1.350,0tr | NO_JIT_NEEDED 387,5tr |
| **S3A dạng A 19.000/14.000** | **LỆCH** `{SCL ledger 14000, broker 19000, diff −5000}`, unverified=[SCL] | **BLOCKED_RECONCILE** | **BLOCKED_RECONCILE** |
| S3B dạng B (14.000/14.000) | ok | TRIM | NO_JIT_NEEDED |
| **S4 sau niêm yết 19.000/19.000** | **LỆCH** (như trên) | **BLOCKED_RECONCILE** | **BLOCKED_RECONCILE** |

- **F1 (CAO, ĐO).** `compute_park_trim.py:413` và `compute_jit_unpark.py:370` fail-closed khi có lệch ở BẤT KỲ
  mã nào. SCL là LAG nên không nằm trong `pool = cash + egg + park_mv` (`compute_park_trim.py:573`) và cũng không
  phải mã L2 được bán, nhưng vẫn chặn cả tài khoản. Dạng A: chặn từ ngày credit (nhiều tuần trước niêm yết).
  Dạng B: chặn từ ngày niêm yết. Trong cả hai dạng, cổng không tự mở lại được (xem F5/F6). Hậu quả với R3=0.0: L1
  không trim được, chỉ cần quan tâm khi PARK bật lại. L2 bị chặn thì lệnh mua BAL/LAG cần unpark không được tài
  trợ. Theo cơ chế này, chặn trên tổng openQuantity, mỗi lần một mã LAG được hưởng quyền sẽ lặp lại.
- **Không đòi bán phần CP tăng thêm (ĐO).** L1/L2 không sinh lệnh nào cho SCL ở mọi giai đoạn (SCL không có lô PARK).
  Không thấy tỷ trọng park bị tính sai, vì `park_mv` chỉ cộng lô PARK.
- **F7 (THẤP, ĐO).** L1 dùng mẫu số `totalCash − totalDebt + egg + park_mv` (`compute_park_trim.py:506,573`).
  Với R3=0.0 thì delta = −park_mv, không phụ thuộc tiền (S1/S2 cùng −1.350,0tr). Với target giả định 0.30: S1 delta
  −810,00tr, S2 −828,75tr (lệch đúng 0,30×62,5tr), lệnh MBB 19.200→19.500cp. L2 dùng `availableCash + egg`
  (`compute_jit_unpark.py:419`): cash_start −62,5tr. Hành vi này giống hệt việc tài trợ một lệnh mua LAG từ
  PARK, nên đúng thiết kế, không phải lỗi. Còn GIẢ ĐỊNH: DNSE trừ khoản nộp vào field tiền nào, lúc nào.
- **F9 (THẤP, ĐO).** Lệnh `$DNA_PYEXE b3_drift.py` → `b3_drift_output.txt`. Kiểm qua `--sim-live-at 20:50 --no-bus --no-state`;
  mọi override trỏ vào sandbox, state dir sau khi chạy vẫn rỗng.
  D1 (batch hạ marketPrice 30.000→25.400 sau 19:05): DRIFT, "giá 30.000→25.400 (15,3%)", rc=0.
  D2 (ngày nộp tiền): "✅ Vị thế không đổi" (script không đọc tiền).
  D3 (credit sau 19:05): DRIFT "KL 14.000→19.000 (×1,3571)", rc=0. D3b (credit trước 18:50): DRIFT, mốc SAU_PHIEN.
  Cả 3 cờ đều phản ánh sự kiện thật, mỗi cờ chỉ xuất hiện một tối, rc luôn 0 (`plan_position_drift_check.py:720`),
  không chặn gì. Nhỏ: câu "Plan có thể dùng KL … TRƯỚC sự kiện" hiện ra cả khi plan không có lệnh SCL. Không cần vá.

## 3. B3 — auto_exit_inject.py (LAG T+25)

Lệnh: `$DNA_PYEXE b3_auto_exit.py` → `b3_auto_exit_output.txt` (rc=0). Gọi `process_account()` thật với
`book_lot_snapshot → park_holdings` thật (khuôn `patch_all_e2e` của `auto_exit_inject_selfcheck.py`). E=2026-10-26,
T+25=2026-11-30, GDKHQ=2026-11-09.

**Lệnh bán dùng số lượng nào?** `qty` lấy từ **sổ lô theo book** (`book_lot_snapshot`, `auto_exit_inject.py:386`;
`_lag_bal_candidates :89-129`, `qty = lot["qty"]`), KHÔNG lấy từ plan và KHÔNG lấy tổng broker. Broker chỉ được
dùng để (i) chặn khi sổ > broker (:105-112), (ii) cắt theo `sellable = Σ tradeQuantity` (`_cap_sellable :290-309`).
`auto_exit_inject.py` không có tham chiếu nào tới exright/corp_action/ex_date (`grep -n "exright\|corp_action\|ex_date"` ra rỗng).

| Ca | Broker open/trade | Kết quả | Trả lời câu hỏi |
|---|---|---|---|
| X1 trước khi CP mới về | 14.000/14.000 | SELL SCL **14.000** LAG | (a) đúng 14.000 |
| X2 dạng A, chưa niêm yết | 19.000/14.000 | **0 lệnh**, `blocked: reconcile lệch broker: sổ lô=14000 broker=19000` + alert | (b) KHÔNG cố bán 19.000. Chặn luôn cả 14.000 đã tới hạn (F3) |
| X3 sau niêm yết, sổ chưa sửa | 19.000/19.000 | 0 lệnh, blocked như X2 | (c) không bán gì cho tới khi sửa sổ |
| **X4** 14.000 đã bán T+26, niêm yết | 5.000/5.000 | **0 lệnh, 0 cờ**, "không có candidate tới mốc exit"; park_holdings `ledger 0 vs broker 5000` | (c) **5.000cp mồ côi, im lặng** (F2) |
| **X4b** như X4, chưa niêm yết | 5.000/0 | như X4 | F2 |
| X5 workaround BONUS ×19/14 (credit trước T+25) | 19.000/14.000 | SELL 14.000, `capped 19000→14000` | cap đúng, broker không bị từ chối |
| X5b workaround, đã bán 14.000 | 5.000/0 | 0 lệnh, `capped 5000→0` (mỗi tối) | 5.000 thừa hưởng entry 2026-10-26 |
| X5c workaround, niêm yết | 5.000/5.000 | SELL **5.000**, "giữ 65 phiên" | đồng hồ lô mới = entry gốc |
| **X5d** workaround nhưng CP về SAU khi bán | 5.000/0 | 0 lệnh, 0 cờ, ledger 0 vs broker 5000 | workaround không cứu được F2 |
| **X6** T+25 rơi trước GDKHQ (ex = 2026-12-02, plan 12-01) | 14.000/14.000 | SELL 14.000 vẫn được chèn | F4 |

- **F2 (CAO, ĐO).** `book_lot_snapshot` chỉ đưa vào `blocked` những mã "THUỘC `book_label`, đang có qty>0 trong
  sổ" (`bin/portfolio_status.py:357-363`). 5.000cp không có lô ở bất kỳ book nào nên không xuất hiện ở đâu cả.
  Đó đúng là dạng "im lặng" mà §29 cấm. Trường hợp này rất có thể xảy ra trong thực tế: SCL thật GDKHQ 2025-10-17,
  CP mới niêm yết 2026-01-29. Với khoảng cách như vậy, T+25 thường tới trước ngày credit/niêm yết, nên 14.000cp
  được bán trước, còn lô mới về sau rơi vào nhánh mồ côi. Tín hiệu duy nhất còn lại là L1/L2 BLOCKED_RECONCILE (F1).
  `corp_action_split` không cứu được, vì nó chỉ nhân các lô còn trong sổ (`park_holdings.py:504-507`, "không giữ mã
  này — no-op").
- **Đồng hồ T+25 của lô mới (ĐO).** Không có lô nào trong sổ thì không có đồng hồ (X2-X4). Với workaround BONUS, lô mới
  thừa hưởng `entry_date` gốc (X5c "giữ 65 phiên"), nên bán ngay khi `sellable` cho phép. Chưa có luật nào nói lô
  quyền mua nên tính T+25 từ đâu. Việc này cần user quyết.
- **F4 (TRUNG BÌNH, ĐO).** Luật "không bán trước GDKHQ" (user 21/10) chưa có trong code. Auto-exit chèn SELL cho
  plan_date < GDKHQ (X6). `exdate_gate` (`trading_bot/exdate_gate.py:175-187`) chỉ bắt lệnh **của đúng ngày**
  GDKHQ, không bắt T-1. Hiện chỉ còn người duyệt plan làm lưới.
- **F3 (TRUNG BÌNH, ĐO).** Chặn ở mức từng mã là đúng tinh thần fail-safe. Tuy nhiên 14.000cp đã tới hạn bị giữ quá
  T+25 suốt từ ngày credit tới khi có người sửa sổ. Có cờ + alert (dedup theo nội dung).
- **F10 (TRUNG BÌNH, ngoài LAG).** `$DNA_PYEXE b3_bal_stoploss.py` → `b3_bal_stoploss_output.txt`:
  `_bal_stop_loss_candidates` với avg_cost 30.000. Ở marketPrice 25.400: pnl −15,3%, không kích. Ở 23.800: pnl
  −20,7% thì kích, trong khi so với TERP mức giảm thật chỉ −6,3%. Kết quả phụ thuộc GIẢ ĐỊNH costPrice DNSE không
  đổi ở GDKHQ quyền mua (chưa đo; với CP thưởng thì broker có hạ costPrice, như ca MBB trong `park_holdings.py:494-497`).

## 4. F5/F6 — đường sửa sổ hiện có đều hỏng

- **F5 (ĐO, `b3_rights_record_trap.py` → `_output.txt`).** `corp_actions.load_all()` validate MỌI record trước khi
  lọc `CONFIRMED` (`corp_actions.py:174`). Vì vậy một record `RIGHTS` dù chỉ PROPOSED vẫn làm `CorpActionError`
  (không phải `SystemExit`) bung ra từ `park_holdings.py:633`. Hệ quả: `compute_park_trim`/`compute_jit_unpark`
  crash. `book_lot_snapshot` bắt được (`except Exception`) và trả `ok=False` cho **cả LAG lẫn BAL**, tức auto-exit
  chặn toàn bộ hai book. File `data/corp_actions.json` dùng chung nên cả SpaceX lẫn ZaloPay cùng bị
  (SUY LUẬN từ việc dùng chung file, chưa chạy 2 account).
  Đường tự động `corp_action_auto_confirm.py:612-619` chỉ ghi `BONUS_ISSUE/SPLIT`, và chỉ khi broker credit đúng lúc
  sự kiện còn "upcoming". Quyền mua credit sau nhiều tuần nên không đi qua đường này (SUY LUẬN, đọc code).
- **F6 (ĐO).** Giả làm `BONUS_ISSUE` ×19/14 thì đối soát khớp lại, nhưng lô thành 19.000 @**22.105** trong khi giá
  vốn thật là (14.000×30.000+62,5tr)/19.000 = **25.395** (`corp_action_split` giữ nguyên tổng giá vốn). Ngoài ra
  `verify_against_bq` sẽ MISMATCH, vì hệ số giá của quyền mua khác hệ số KL. Đây là ghi sai sự kiện, không khuyến
  nghị dùng.
- Lối tạm duy nhất KHÔNG cần sửa code: dựng bootstrap snapshot mới được user APPROVED (`load_bootstrap` lấy file mới
  nhất, `park_holdings.py:105-122`). Cách này nặng (phải khai lại entry_date mọi lô) và vẫn cần người làm.

## 5. Đề xuất patch tối thiểu (văn bản, CHƯA áp)

**P1 — gốc của F1/F2/F3/F5. Cần arch-review + user duyệt (chạm sổ lô → sizing L1/L2 và lệnh auto-exit).**
Thêm loại sự kiện `RIGHTS_SUBSCRIPTION`. Record do người ký, khai **số CP thật user đã mua theo từng account** và giá
phát hành. Sổ thêm một LÔ MỚI (không nhân lô cũ), gán book theo các lô được hưởng quyền **tại GDKHQ**, kể cả khi các
lô đó đã bán.
```diff
--- bin/corp_actions.py
-QTY_EVENT_TYPES = {"STOCK_DIVIDEND", "BONUS_ISSUE", "SPLIT"}
+QTY_EVENT_TYPES = {"STOCK_DIVIDEND", "BONUS_ISSUE", "SPLIT"}
+RIGHTS_EVENT_TYPES = {"RIGHTS_SUBSCRIPTION"}   # thêm lô mới; KHÔNG nhân lô cũ, KHÔNG verify bằng tỉ số Close/Price
@@ def validate(rec, idx=0):
-    if etype not in QTY_EVENT_TYPES:
+    if etype in RIGHTS_EVENT_TYPES:
+        # bắt buộc: subscribed_qty_by_account {account_no: int>0}, issue_price_vnd > 0, ex_date, broker_effective_ts
+        ...  # qty_multiplier = None
+    elif etype not in QTY_EVENT_TYPES:
--- bin/park_holdings.py  (timeline: thêm mốc ex_date ghi nhận lô được hưởng, mốc broker_effective_ts thêm lô)
+    def rights_credit(self, ticker, entitled_books, qty, price, entry_date, source, event_id):
+        """Một lô MỚI per book (chia theo tỉ lệ qty được hưởng tại ex_date, làm tròn Hamilton);
+        entry_date theo luật user chọn (A: entry gốc của lô hưởng quyền | B: ngày credit)."""
@@ for _ts, kind, ev, fname in timeline:
-        if kind == 1:
+        if kind == 1 and ev["event_type"] == "RIGHTS_SUBSCRIPTION":
+            book.rights_credit(...)   # entitled_books chụp ở ex_date, KHÔNG phụ thuộc lô còn hay đã bán
+            continue
+        if kind == 1:
```
Cần user quyết: (1) entry_date của lô quyền: thừa hưởng entry gốc (bán ngay khi niêm yết) hay tính từ ngày credit;
(2) record khai riêng cho từng account, vì user mua tay và có thể không mua đủ quyền.

**P2 — F2, chống im lặng. Cần arch-review.** Mã có broker>0 mà sổ=0 ở mọi book phải hiện ra cho người duyệt plan:
```diff
--- bin/portfolio_status.py  book_lot_snapshot()
     for lot in h["lots"]:
         ...
+    # MỒ CÔI: broker có, sổ = 0 ở MỌI book ⇒ không book nào "sở hữu" để exit. §29: phải hiện ra.
+    for m in h["reconcile"]["mismatches"]:
+        if m["ledger_qty"] == 0 and m["broker_qty"] > 0:
+            blocked.setdefault(m["ticker"], f"MỒ CÔI: broker {m['broker_qty']}cp, sổ 0 ở mọi book "
+                                            f"(CP quyền/thưởng về sau khi đã bán?) — không exit tự động")
     return out, True, None, blocked
--- bin/auto_exit_inject.py  _add_blocked: dedup mồ côi theo (ticker, reason), bỏ qua book (LAG và BAL cùng gọi)
```

**P3 — F4. Cần user duyệt (chạm lệnh).** Trước khi chèn SELL LAG, tra lịch quyền mua của mã (nguồn: lịch
`corp_action_daily` upcoming_events_held / `price_frame.pricing_events`). Nếu `plan_date < exright_date` và
`exright_date` nằm trong N phiên tới thì KHÔNG chèn, ghi `blocked` "HOLD tới GDKHQ quyền mua {d} (luật user
2026-10-21)". Lịch lỗi thì fail-open và báo to, giống `exdate_gate`.

**P4 — F1, phương án thay P1 ngắn hạn (thiết kế, cần arch-review).** Thu hẹp Cổng 0 của L1/L2: lệch chỉ nằm ở mã
không có lô PARK và `broker > sổ` thì không chặn tài khoản, chỉ ghi note. Lý do: `pool` không chứa giá trị mã đó,
`build_pool` không bán mã đó. Rủi ro: che mất lỗi gắn book (lô PARK bị gắn nhầm book), nên ưu tiên P1.

**P5 — F5. Rẻ, không chạm lệnh.** `load_all()` gặp record chưa CONFIRMED mà không hợp lệ thì bỏ qua + cảnh báo thay
vì raise. Record CONFIRMED hỏng vẫn raise như cũ.

## 6. File trong thư mục này

`b3_common.py` (fixture chung) · `b3_b2_park_unpark.py` → `b3_b2_park_unpark_output.txt` · `b3_auto_exit.py` →
`b3_auto_exit_output.txt` · `b3_drift.py` → `b3_drift_output.txt` · `b3_bal_stoploss.py` →
`b3_bal_stoploss_output.txt` · `b3_rights_record_trap.py` → `b3_rights_record_trap_output.txt`.
Đã kiểm sau khi chạy: không file nào trong `data/trade_plans`, `data/auto_exit_block_alert_state.json`,
`data/capit_episode.json`, `data/corp_actions.json`, `mike/state/plan_position_drift` mang tên/nội dung
`RightsAcct`/`8888888888`. 6 file `*_2026-10-22*` trong `data/trade_plans` có mtime 23:30, trước các lần chạy
fixture, và là của cron production.
