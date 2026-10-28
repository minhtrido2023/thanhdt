# B2 — Chuỗi NAV / P&L / dòng tiền qua sự kiện QUYỀN MUA (book LAG, SpaceX)

Auditor: Taylor (sub-agent), 2026-10-22 ICT. Chỉ đọc + chạy fixture cô lập. **Không sửa code production.**
Tái lập: `python3 agents/Taylor/research/lag_rights_audit_20261022/b2_nav_chain.py --bq`
(output: `b2_nav_chain_output.txt`; mọi ghi file bị guard chặn nếu ra ngoài `mkdtemp`; đã kiểm
mtime `data/execution_logs/nav_history_SpaceX.csv`, `active_nav_SpaceX.json`, `data/corp_actions.json`
không đổi sau khi chạy).

## 0. Dữ kiện nền (ĐO)

| Dữ kiện | Giá trị | Nguồn |
|---|---|---|
| SCL quyền mua | `issue_method_code='Rights'`, `exercise_ratio=0.35714286`, GDKHQ 2025-10-17, ĐKCC 2025-10-20, `issue_volumn=8e6`, `total_value=1e11` ⇒ giá phát hành 12.500, `listing_date=2026-01-29`, `value_per_share=NULL` | `bq query … tav2_bq.corporate_action AS c WHERE c.ticker="SCL"` |
| Close/Price SCL | 0,695495 (10-16) → 0,784332 (10-17) ⇒ hệ số 0,88674; lý thuyết TERP (P=22.200, S=12.500) 0,88501 | `bq query … tav2_bq.ticker AS t WHERE t.ticker="SCL" …` |
| Giá thô (Price) | 10-15 22.600 · 10-16 22.200 · 10-17 21.700 · 10-27 20.000 · 11-05 20.500 · 2026-01-29 21.000 | như trên |
| Sự kiện chồng | SCL **cổ tức CP 9% GDKHQ 2025-11-06** (nằm trong cửa sổ nộp tiền quyền mua) | corporate_action |
| Glitch BQ | Close/Price SCL 2025-10-23 = 0,8195 (một phiên), các phiên quanh = 0,784 | ticker |
| DNSE positions schema | 17 khoá: `openQuantity, tradeQuantity, accumulateQuantity, costPrice, marketPrice, …` — **KHÔNG có field CP chờ về / quyền mua**; balances cũng không có field quyền mua | quét 110 file `dnse_raw_*.jsonl` (12.949 bản ghi positions, 7.424 balances) |
| **Tiền lệ thật MBB quyền mua 10:1 @10.000** | SpaceX: `openQuantity` 1.565→**1.675 (+110) ngay bản đọc 2026-08-28 19:07:46**, `tradeQuantity` giữ 1.400, `costPrice` 21.405,75→20.656,72 (tổng vốn +1.100.000 = 110×10.000); totalCash −1.264.731 cùng bản đọc. ZaloPay +20 cùng ngày. 110 CP vẫn KHÓA tới 2026-10-07 (open 175 / trade 65) | dnse_raw 08-27→10-07, lọc `account_no` |
| Cách đã xử lý MBB | (a) dòng journal tay `FILL … CORP_ACTION,RIGHTS_SUBSCRIPTION` 110@10.000 (`exec_SpaceX_2026-08-28_journal.csv`, parent `MBB-RIGHTS-2026-08-28`); (b) `data/known_position_discrepancies.json` qty_delta +110 (hết hạn 2026-11-30); (c) `data/cash_identity_acks.json` cửa sổ 08-27→08-28 user xác nhận 10-12/10-14 | đọc file |

⇒ **Dạng A (KL tăng ngay khi nộp tiền, chưa giao dịch được) là dạng ĐO được trên DNSE.** Dạng B
(KL chỉ tăng ngày niêm yết) là GIẢ ĐỊNH, vẫn thử cho đủ.

Fixture: 14.000 SCL giá vốn 30.000, tiền 899.592.600 (vốn 1,32 tỷ), nộp quyền 5.000 cp ngày
(giả định) 2025-10-27 ⇒ tiền −62.500.000; costPrice broker bình quân 25.394,74.

## 1. Tóm tắt theo module × ngày

| Module | Tối cum (T−1) | GDKHQ T0 | Ngày nộp tiền (dạng A) | Ngày niêm yết |
|---|---|---|---|---|
| `daily_nav_snapshot` | **rc=4** nếu broker đã hạ marketPrice về TERP (live & `--from-raw`) | rc=0, NAV −0,58% | **rc=5** (live & from-raw), không đường phục hồi | dạng A rc=0; dạng B **rc=5** |
| `exdate_frame`/`compute_active_nav` | không chặn (KL không đổi) | không chặn | **blocked ⇒ rc=6** | dạng B blocked |
| `verify_account_snapshot` | — | — | P&L chỉ 14.000@30.000, **verified=True im lặng**; có journal tay ⇒ WARN rc=1 | — |
| `reconcile_equity` | — | — | **residual +62.500.000 (+5,59%), rc=1, vĩnh viễn** | — |
| `cash_identity` | — | — | cửa sổ mở `không kết luận được` (dạng B: **`nghi nạp/rút` — sai nhãn**) | — |
| `dividend_adjusted_return` | — | `ISS_NONFREE` đúng (không coi là cổ tức tiền / CP thưởng) | — | — |
| Chồng cổ tức CP 9% (11-05) khi quyền đã nộp | **rc=5 + blocked rc=6; `--from-raw` KHÔNG phục hồi được** nếu CP quyền chưa được hưởng 9% | | | |

## 2. Chi tiết từng module

### 2.1 `bin/daily_nav_snapshot.py`

**(a) Tối cum — cổng giá, rc=4. Mức CAO (vận hành). ĐO (fixture) + SUY LUẬN (thời điểm broker hạ giá).**
- Lệnh: `b2_nav_chain.py` ca `A1_cum_evening_mp_adjusted_fromraw` và `A1_live_cum_evening_mp_adjusted`.
- Output: `rc=4 … SCL: close_price=22,200 vs vị thế broker marketPrice=19,650 (lệch 13.0%)`; biến thể
  marketPrice chưa hạ (`A1b`) ⇒ rc=0.
- Cơ chế: `classify_qty_residual` trả "ok" (KL không đổi) ⇒ `classify_corp_action_gap` chỉ có nhánh
  `CASH_DIV`; quyền mua rơi vào `kind="SHARE_EVENT"` ⇒ "unexplained" (`daily_nav_snapshot.py:555-585`);
  vòng `is_today` so `cp` vs `mp` >5% ⇒ `mismatched` ⇒ `return 4` (`:1508-1531`). Đường `--from-raw`
  dùng `classify_raw_price_gap` (`:255-272`) chỉ biết `early_credit` qua `qty_multiplier` CONFIRMED,
  mà `corp_actions.validate` chỉ nhận `{STOCK_DIVIDEND, BONUS_ISSUE, SPLIT}` (`bin/corp_actions.py:75,112`)
  ⇒ **không có cách ghi quyền mua vào sổ ⇒ backfill cũng rc=4 ⇒ mất vĩnh viễn dòng nav_history ngày cum**.
- Bằng chứng thời điểm: DRI (cổ tức tiền) marketPrice 14.800→13.800 lúc **19:07:29** 2026-09-21; VPB (ISS)
  28.000→22.100 lúc **19:07:25** 2026-09-23; MBB 2026-08-10 điều chỉnh 19:32 (`positions.modifiedDate`).
  Quyền mua là `price_adjusting=True` (`corp_action_lib.py:34-38`) nên **suy luận** broker cũng hạ
  marketPrice về TERP tối cum; `nav_sync_retry.sh` chỉ retry tới 21:15 rồi escalate.
- Kinh tế: NAV tối cum tính `14.000 × 22.200` là ĐÚNG (giá cum còn quyền) — chặn ở đây là chặn oan.

**(b) Ngày nộp tiền (dạng A) — cổng KL, rc=5. Mức CAO. ĐO.**
- Ca `A3_payday_formA_no_journal_fromraw` và `A3_live_payday_formA_no_journal`: `rc=5`, artifact
  `nav_gate_block`: `residual +5000, ex_date null, evidence residual_not_explained_by_fills_or_ratio`.
- Cơ chế: `net_fills_between` chỉ đọc journal (`:369-422`); quyền mua không phải lệnh khớp; lịch
  không có sự kiện phiên kế tiếp ⇒ `qty_unexplained` (`:464-513`) ⇒ `return 5` (`:1395-1447`). Đường
  phục hồi `confirmed_share_event_multiplier` cần `qty_multiplier` CONFIRMED đúng `nxt_session` ⇒ không
  tồn tại cho quyền mua ⇒ **chặn ở cả live lẫn `--from-raw`**.
- Né được bằng tiền lệ MBB (dòng journal tay): ca `A3_payday_formA_manual_journal_fromraw` ⇒ rc=0,
  NAV 1.217.092.600, day_change **+30.500.000 (+2,57%)** trên một phiên giá −2,4% — phần +37,5tr là
  giá trị quyền (5.000×(20.000−12.500)) được ghi nhận vào ngày nộp, không phải ngày GDKHQ.
- **Phân loại flow:** NAV không coi −62,5tr là rút vốn (cổng 15% chỉ xem tổng NAV); nhưng KL+tiền cùng
  đổi nên dạng A gần trung tính NAV. Dạng B (`A3_payday_formB_qty_unchanged_fromraw`): rc=0, NAV
  **−69.500.000 (−5,86%)** ⇒ lọt cổng ghi 15% nhưng vượt `NAV_JUMP_BLOCK_PCT=5%` của cổng công bố
  (`account_cash_flows.py:123`) ⇒ báo cáo bị giữ tới khi khai flow; `VALID_KINDS` chỉ có
  `deposit|withdraw|market_only` (`account_cash_flows.py:104`) ⇒ **không có cách khai đúng bản chất**
  (khai `withdraw` sẽ làm unit-price thổi phồng lãi ngày niêm yết).

**(c) Ngày niêm yết. ĐO.** Dạng A: chỉ `tradeQuantity` đổi ⇒ cổng chỉ đọc `openQuantity` ⇒ rc=0
(`A4_listing_formA…`). Dạng B: `rc=5` y như (b) (`A4_listing_formB…`). Mức THẤP (dạng B chưa từng
quan sát).

**(d) Chồng cổ tức CP 9% trong cửa sổ quyền (SCL thật: GDKHQ 11-06). Mức TRUNG BÌNH. ĐO (code) +
SUY LUẬN (quyền hưởng).**
- `expected = qty_prev × ratio` (`:507`) dùng `qty_prev=19.000` (gồm 5.000 CP quyền chờ phát hành).
  Nếu CP quyền CHƯA được hưởng 9% (chưa lưu ký tại ĐKCC — SUY LUẬN, cần Wendy/Winston xác minh) broker
  credit 1.260 ≠ 1.710 ⇒ `qty_unexplained` rc=5; **kể cả khi đã CONFIRMED mult 1,09**, `--from-raw`
  không phục hồi (`_mult_explains`: 20.260/1,09 = 18.587 ≠ 19.000) ⇒ mất vĩnh viễn dòng NAV
  (`A5_rights_pending_NOT_entitled_…` rc=5 cả hai biến thể). Đối chứng không quyền mua
  (`A5_control_…`) rc=0, quy ngược 15.260→14.000 đúng thiết kế; biến thể "được hưởng" 1.710 rc=0.

**(e) Phân loại sự kiện.** `classify_qty_residual` coi mọi ISS `price_adjusting` khác DIV là "sự kiện
CỔ PHIẾU" (`:499`) ⇒ quyền mua mang tỉ lệ 0,357 vẫn có thể "giải thích" một cú tăng KL đúng
`qty_prev×0,357` ở tối cum thành `share_event_credit`. Không xảy ra với DNSE (phải nộp tiền sau ĐKCC),
và hạ nguồn fail-closed (`B_HYPOTHETICAL…`: `verify_post_event_price=None`). Mức THẤP. ĐO.

### 2.2 `bin/exdate_frame.py` + `bin/compute_active_nav.py` (mẫu số sizing)

- Tái dùng nguyên `classify_qty_residual` (`exdate_frame.py:195-219`) ⇒ hành vi giống 2.1:
  ngày nộp tiền dạng A `blocked=['SCL']` ⇒ `compute_active_nav.py:487-508` **exit 6**, không ghi
  `active_nav` (consumer lùi về nav_history ≤5 ngày). Có journal tay ⇒ không chặn. Chồng 9%:
  1.260 ⇒ blocked; 1.710 ⇒ credited và `verify_post_event_price` khớp (18.807). ĐO (mục B).
- Tối cum: KL không đổi ⇒ không chặn, giá đóng cửa cum × 14.000 — đúng hệ quy chiếu hôm nay (giá cum
  bao gồm quyền). Docstring `verify_post_event_price` (`exdate_frame.py:66-70`) đã ghi đúng: quyền mua
  không khớp `px_cum/multiplier` nên fail-closed. ĐO.
- **Thiếu giá trị quyền từ T0 tới ngày nộp:** DNSE không có field quyền ⇒ `active_nav` và NAV thấp hơn
  kinh tế ≈ 5.000×(P−12.500) (T0: 5.000×(21.700−12.500)=46,0tr ≈ 3,8% NAV fixture). Mức TRUNG BÌNH
  (sizing hơi bảo thủ, báo cáo lệch thời điểm). SUY LUẬN về giá trị quyền (không có feed giá quyền).

### 2.3 `bin/verify_account_snapshot.py` (giá vốn)

- Sổ vốn CHÍNH THỨC dựng từ `dnse_fill_events` (lệnh sàn) — `raw_books` (`:735-738`), cross-check
  journal. CP quyền không có lệnh sàn ⇒ **không vào giá vốn bình quân, không reset lô**.
- Không journal tay (`C_formA_no_journal`): `verified=True`, **0 cảnh báo**, qty 14.000, avg 30.000,
  unrealized **−140.000.000**; broker thật 19.000 @25.394,74 ⇒ **−102.500.000**. `pnl_coverage_warnings`
  chỉ so theo MÃ (`:602-623`), không so KL ⇒ thiếu 5.000 CP im lặng. Mức TRUNG BÌNH. ĐO.
- Có journal tay (`C_…_no_ack`): `WARN qty mismatch SCL: dnse_raw=14000 journal=19000` + cost mismatch
  15,35% ⇒ rc=1 (`verified=False`). Thêm `known_position_discrepancies` ⇒ INFO, rc=0 nhưng P&L vẫn
  14.000@30.000. ĐO.
- Lý do trong `data/known_position_discrepancies.json` ("broker chưa ghi có vì cổ phiếu chưa về") trái
  với dnse_raw (openQuantity đã +110 từ 08-28) — "broker" ở đó thực chất là "lệnh sàn dnse_raw". THẤP.

### 2.4 `bin/reconcile_equity.py`

- Vế trái = vốn + unrealized(snapshot) + realized(dnse_fill_events) − phí; vế phải = MTM(snapshot) +
  totalCash − nợ (`:334, 339`). Tiền nộp quyền chỉ ở vế phải, CP quyền không ở vế nào.
- Ca `[D]`: `lhs 1.179.592.600 · rhs 1.117.092.600 · residual +62.500.000 (+5,595%) · rc=1 ·
  "CHƯA GIẢI THÍCH ĐƯỢC"` — **vĩnh viễn** (không có fill nào sau này đóng nó). Phần
  `missing_fills_broker_confirmed` chỉ được đọc khi KHÔNG truyền `--starting-capital` (`:215-221, 283`) — SpaceX truyền nên không dùng được. MBB thật chỉ +1,1tr nên chìm dưới sàn 5tr. Mức
  TRUNG BÌNH (pipeline §6 bước 3, không chặn NAV). ĐO.

### 2.5 `bin/cash_identity.py`

- Dạng A: cửa sổ `không kết luận được`, `qty_gaps {SCL: 5000}`, suspect=True — **đúng hành vi** (đòi
  người xem), khớp tiền lệ ack MBB. Nhưng câu ước tính "nếu là lệnh ngoài bot ở giá thị trường thì còn
  **+37.597.000 đ** tiền vào/ra" (`:760-780`, định giá theo marketPrice) gợi ý sai một khoản nạp. THẤP.
- Dạng B: nhãn **`nghi nạp/rút chưa khai` — "nghi tiền RÚT ra"** — sai bản chất. TRUNG BÌNH (chỉ kênh
  vận hành; `investor_line` trung tính).
- Đường đóng sạch đã có sẵn: một bản ghi `missing_fills_broker_confirmed` (buy 5.000 @12.500) trong
  `account_seed_capital.json` ⇒ cửa sổ đóng, residual **+60.625** (= phí 0,097% áp nhầm cho giao dịch
  quyền mua không có phí), `kind=None`. ĐO (ca `E_formA_with_seed_missing_fill_rights`).

### 2.6 `bin/dividend_adjusted_return.py` (§21)

- Phân loại ĐÚNG: quyền mua nằm trong `NONFREE_ISS` (`:260`) ⇒ `ISS_NONFREE`, `share_multiplier=1`,
  `cash_per_share=0` — không cộng như cổ tức tiền, không nhân như CP thưởng; nhánh D1 hạ UNVERIFIED
  nếu solver lỡ giải ra tiền (`:1814-1846`). ĐO trên BQ thật: cửa sổ 2025-10-01→10-21
  `2025-10-17 ISS_NONFREE resolved=True`.
- Cửa sổ tới 10-31: glitch BQ 2025-10-23 (tỉ số 0,8195 một phiên) thành `UNVERIFIED` ⇒ kéo
  `frame_ok=False` cho cả sự kiện quyền ⇒ `build_position_return.unverified=['2025-10-17','2025-10-23']`
  ⇒ fail-closed (không công bố tỉ suất), không báo sai. Với mã đang giữ, `_noise_vetoes` có sổ broker
  nên có thể tự gỡ — chưa đo. THẤP (lỗi dữ liệu → Winston).
- `classify_cost_steps` (`:1107-1150`): bước costPrice ngày nộp quyền (KL tăng, tổng vốn tăng) ⇒ `buy`
  — đúng. Tỉ suất per-position chỉ đúng nếu caller dùng KL/giá vốn broker (19.000 @25.394,74); nếu
  caller lấy từ verify_account_snapshot (14.000 @30.000) thì sai — xem 2.3.

### 2.7 `bin/locked_shares.py`

Đã do B1 soát (`b1_locked_shares_output.txt`): CP quyền xếp `pending` đúng tới khi sự kiện quyền rơi
khỏi `LOOKBACK_DAYS=150`; sau đó vẫn `pending` nhưng nhãn chuyển sang "Cổ tức CP 9%". Không lặp lại.

## 3. Đề xuất patch (CHƯA áp — **cần arch-review + user duyệt vì chạm NAV/sizing**)

**P1 — MỘT sổ cho "fill broker xác nhận ngoài sàn" (quyền mua), mọi consumer đọc cùng sổ** (đóng
2.1b, 2.2, 2.3, 2.4, 2.5 thay vì 3 artifact tay như ca MBB). Tái dùng
`account_seed_capital.json → missing_fills_broker_confirmed` (cash_identity đã đọc, ĐO đóng được cửa sổ),
thêm `"kind": "rights_subscription"`, `"fee_rate": 0`.
```diff
--- bin/daily_nav_snapshot.py  net_fills_between()
+    # fill broker xác nhận ngoài sàn (quyền mua) — CÙNG sổ với cash_identity/reconcile_equity
+    from cash_identity import load_confirmed_missing_fills
+    for fx in load_confirmed_missing_fills(account):
+        d = fx["moment"].date().isoformat()
+        if after_date < d <= upto_date:
+            out[fx["symbol"]] = out.get(fx["symbol"], 0.0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])
--- bin/verify_account_snapshot.py  main(), sau vòng đọc dates
+    for fx in load_confirmed_missing_fills(args.account):     # vào CẢ raw_events và journal_events
+        ev = (fx["moment"].isoformat(), "broker-confirmed", fx["symbol"], fx["side"], fx["qty"], fx["value"] / fx["qty"])
+        raw_events.setdefault(d, []).append(ev); journal_events.setdefault(d, []).append(ev)
--- bin/reconcile_equity.py  main()
-    if seed:
-        for fx in seed.get("missing_fills_broker_confirmed", []):
+    for fx in (seed or _load_seed_entry(args.account)).get("missing_fills_broker_confirmed", []):
--- bin/cash_identity.py  build_windows(): phí = 0 cho fx.get("kind") == "rights_subscription"
```
Luật đi kèm: KHÔNG ghi dòng journal tay nữa (tránh đếm 2 lần với sổ). Selfcheck đề xuất: tái dùng
`b2_nav_chain.py` ca A3/B/C/D/E làm assertion (rc=0, book 19.000 @25.394,74 = costPrice broker,
residual |·| < sàn, cửa sổ `kind=None`); **mutant**: (m1) bỏ dòng cộng sổ trong `net_fills_between` ⇒ A3
phải về rc=5; (m2) ghi sổ sai KL 4.999 ⇒ rc=5; (m3) ghi cả journal tay lẫn sổ ⇒ residual −5.000 ⇒ rc=5
(chứng minh luật chống đếm 2 lần có hiệu lực). Chạy dưới `env -u TZ` + TZ lạ (§16/§19).

**P2 — nhánh "quyền mua" cho cổng giá tối cum** (đóng 2.1a), song song nhánh `cash_div_confirmed`:
```diff
--- bin/corp_action_daily.py upcoming_events(): thêm "issue_price" = total_value/issue_volumn (cả hai > 0)
--- bin/daily_nav_snapshot.py classify_corp_action_gap()
+    if kind == "SHARE_EVENT" and ev.get("issue_method_vi") == RIGHTS_METHOD and ev.get("issue_price") \
+            and qty_now == qty_prev:
+        r, s = float(ev["exercise_ratio"]), float(ev["issue_price"])
+        ref = (price_ref + r * s) / (1 + r)
+        if abs(mkt_price - ref) <= max(FRAME_TOL_VND, ref * FRAME_TOL_PCT):
+            return "rights_ref_confirmed", {"terp": ref, "issue_price": s, ...}
   # main(): `rights_ref_confirmed` ⇒ bỏ khỏi `mismatched`, mark giá CUM (giá cum còn quyền — đúng hệ hôm nay)
```
Thiếu `issue_price` ⇒ giữ rc=4 như hiện nay (fail-closed). Cần `corp_action_lib.events` select thêm
2 cột — **chưa kiểm reader có select chúng không**. Selfcheck: A1 ⇒ rc=0 với TERP 19.650; mutant
`issue_price` lệch 10% ⇒ rc=4; mutant KL đổi cùng tối ⇒ không vào nhánh này.

**P3 — loại quyền mua khỏi "sự kiện CỔ PHIẾU" trong `classify_qty_residual`** (2.1e, THẤP):
```diff
-    is_share_event = bool(ev and ev.get("price_adjusting") and ev.get("event_code") != "DIV")
+    is_share_event = bool(ev and ev.get("price_adjusting") and ev.get("event_code") != "DIV"
+                          and ev.get("issue_method_vi") != RIGHTS_METHOD)
```
Mutant: bỏ điều kiện ⇒ ca `B_HYPOTHETICAL…` quay lại `credited`.

**P4 — quyền hưởng cổ tức CP của CP quyền đang chờ** (2.1d): CHƯA đề xuất code — trước hết cần xác
minh pháp lý/lưu ký (Wendy + Winston, tốt nhất đo trên một ca broker thật). Nếu "không hưởng": `expected`
và `_mult_explains` phải trừ KL quyền đang chờ (lấy từ sổ P1 có `date` > ĐKCC… ) — phụ thuộc P1.

**Không đề xuất code** cho: giá trị quyền bị thiếu trong NAV từ T0 tới ngày nộp (không có feed giá
quyền; chỉ đề xuất chú thích trong báo cáo tuần), và flow kind mới cho dạng B (dạng B chưa quan sát).

## 4. Việc ngay (không cần code)

Khi user nộp tiền quyền SCL: tối đó gate sẽ rc=5 (NAV) + rc=6 (active_nav). Đường thoát hiện có, đúng
tiền lệ MBB: ghi dòng journal `CORP_ACTION,RIGHTS_SUBSCRIPTION` + `known_position_discrepancies` +
ack cash_identity, rồi `--from-raw`. Tối cum quyền (nếu broker hạ giá trước 19:10) sẽ rc=4 và hiện
**không có đường phục hồi** ngoài ghi tay dòng nav_history.
