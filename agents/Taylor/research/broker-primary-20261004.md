# broker-primary (job Taylor_20261003_162814) — design, Q5/Q6, arch-review v1

## Design
broker-primary design (job Taylor_20261003_162814)
- decide(): no DEFER_VENDOR, VENDOR_UNREADABLE not blocking, DIV compare moved into vendor_crosscheck(). After CONFIRMABLE: vendor_check status VERIFIED|PARTIAL|MISMATCH|NO_EVENT|UNREADABLE (+FEED_DEAD by caller). MISMATCH (mult>1%, cash>1d/cp, share event other ex within 10d, unknown price-adjusting code same ex, bad ratio) => verdict UNVERIFIED.
- price-only (qty unchanged): per-account evidence (cost drop c, m1 vs m0 staleness); ticker-level: c>0 => CASH_DIVIDEND only if cashDividendReceiving delta per account == expected sum (incl. cash legs of share events) and price consistent (HOSE/HNX); else AMBIGUOUS/INSUFFICIENT. c==0 & price adjusted (HOSE/HNX, not stale, |m1-px|>tol) => AMBIGUOUS (rights?). px/exchange unknown => gap row INSUFFICIENT.
- live order: broker FIRST (writer; CONFIRMABLE => CONFIRMED record provenance=broker + vendor_check), vendor confirm-only (no writes; ratio/N9 questions; vendor-only event with no broker entry => question). UNVERIFIED => no registry write, question naming Winston with proposed record. CASH_DIVIDEND => finding only (registry = qty events only).
- shadow: vendor branch unchanged (production writer), broker shadow logs new decisions, does not skip registry-existing (logs registry_has).

## Q5/Q6 (độc lập, chỉ báo cáo)
Q5 (plan T+1): DollarBill plan built ~19:06-19:09 ICT (bq_freshness_check.sh pipeline-4), reads DNSE positions 19:03-19:15 = INSIDE credit window. BID 08-14: ZaloPay pkg 1258 credited only 20:15 (plan built 19:06 on pre-credit data; no BID order that day so no harm). TPB 10-01 credit 18:52 => plan used adjusted 12,100 by luck of timing. No re-read/diff after 20:15 vs plan basis (20:15/20:30/20:40 jobs re-read for own outputs only). Proposal: ~20:50 read-only positions-drift diff vs plan basis -> flag in send_plan_report 21:00; + 21:00 second corp_action_auto_confirm pass.
Q5c (band +-7%): executor._limit_price clamps to live q.ceiling/floor (adjusted band) each cycle; but chase caps derive from plan ref_price (buy x1.015 config.py:137, sell floor x0.97 config.py:138). Only apply_exdate_gate (trading_bot/exdate_gate.py:77-160) rebases ref on ex-date, its calendar = BQ tav2_bq.corporate_action (DEAD since 09-26) -> NO_EVENT, not printed (bot_execute.py:651-659) => fails OPEN silently. TPB ex 10-02 absent from BQ; fine only due to 18:52 credit. Latent: stale ref P with ratio r>10.3% => sell floor P*0.97 > adjusted ceiling P/(1+r)*1.07 => sell pinned at ceiling never fills; buy +1.5% cap silently becomes +7%. No real out-of-band case found. Proposal: bot_execute cross-check plan ref vs live q.ref all orders (>~3% w/o known event => flag/block); exdate_gate: stale/dead vendor => CALENDAR_FAIL printed or fall back to corp_actions.json/broker evidence; print NO_EVENT.
Q6 (nav_exdate_forecast L1): source ONLY corp_action_daily_<asof>.json upcoming_events_held (07:30, from BQ corporate_action) + prior-evening active_nav. Consumers: bq_freshness_check.sh:667 --alert 19:00 (Discord+bus), :838 --note into DollarBill prompt, portfolio_status.py:708. Feed dead: stale-but-usable days (09-29..10-01, status OK feed_status STALE) => SILENT false all-clear (never reads feed_status); FAILED day (10-02) --alert prints generic 'no snapshot' (no feed_dead/since, no dedup), --note returns "" silently. Lost: TPB SHARE_EVENT warning 10-01 19:00 (=> NAV 10-01 blocked rc=5, manual backfill 10-03). Proposal: read feed_status/feed_stale_streak -> header warning in --alert/--note; _FAILED -> name failed_gate + max_ingested; --note returns 'calendar UNAVAILABLE (feed_dead)'; optional broker-side flag (r5 detector logic).

## Arch-review v1 @311c917a — NEEDS_CHANGES
Probe scripts của reviewer: /tmp/archrev_bp/{probe.py,probe2.py,probe3.py,pure.py,mut.py,mut2.py,vx.py}

Verified PASS (artifact): broker CONFIRMABLE = writer; vendor MISMATCH ⇒ UNVERIFIED + question [Winston]; shadow broker never writes corp_actions.json (new_recs requires mode=="live"); live vendor branch (_vendor_confirm_only) has no writer; 335/352 PASS 3TZ×2 interp; 230/230 author mutants named-killed; invariants intact.

MAJOR (NEW class):
- MAJOR-1: registry already has (ticker,ex) ⇒ live skip at auto_confirm.py:1144-1147 silent even when broker logs LỆCH VENDOR / human record ×1.3 vs broker ×1.15 / PROPOSED record (never applied). Vendor confirm-only only compares multiplier of provenance=broker records; log "vendor khớp" printed without comparison. Tests B9/B9b/L12c assert the silence.
- MAJOR-3: records written as NO_EVENT/UNREADABLE/FEED_DEAD/PARTIAL never re-verified (vendor calendar only upcoming, days_ahead≤1; corp_actions.py --verify not in cron).
- MAJOR-4: price-only screening (~2 DNSE calls/held ticker, 30s timeout, no budget) runs in scan_day BEFORE share-event registry write ⇒ DNSE slow can push write past park_trim 19:30 while holding lock.
MAJOR (SAME class): MAJOR-2: _vendor_confirm_only :634 checks holdings only in today's dnse_raw ⇒ account without record today ⇒ "không tài khoản nào giữ mã" (false), 0 bus.
Minor: m1 unreadable vendor DIV value → 0 ⇒ false VERIFIED; m2 vendor DIV-only vs broker share event ⇒ PARTIAL written w/o question (needs user design call); m3 §29 messages :623/:648; m4 detect:814 wrong reason; m5 vendor rows not de-duplicated; m6 DAYS_AHEAD_MAX calendar days (weekend); m7 near-dup rewrite drops Winston assignee from UNVERIFIED.
Reviewer surviving mutants: M21 c=min(cs), M27, M32 pre[0], M45 one_px, M50 holidays in price-only, M53, M54 DIV-only PARTIAL→VERIFIED, M57 corrupt ledger silent, M64 NaN ratio, M68; crash-only M30b.
Required: (1) registry reconciliation regardless of provenance incl. cash leg, ask once per (tk,ex,record id); (2) confirm-only holdings from previous snapshot/held_before, else INSUFFICIENT question; (3) post-ex vendor re-verify sweep OR explicit user acceptance; (4) price-only after share-event write + time budget; (5) m1/m3/m4 + tests for surviving mutants + real-calendar crosscheck test.

## r2 (job Taylor_20261004_024239) @4a23a787 — arch-review v2 NEEDS_CHANGES (DỪNG: có lỗi LOẠI MỚI)
Đã làm: RC1-RC5 + m1-m7 + 11 đột biến sống v1; selfcheck 427/0; --mutations 302/302 (assertion có tên); ma trận 17×2 interp×3 TZ = 102/102; replay D1-D5 PASS (_exchange_fn thật); dry-run thật 10-01: TPB MATCH record người ký; corp_actions.json md5 bfd681e5 không đổi; không ledger prod; dnse_raw không thêm dòng.
Reviewer v2 (probe /tmp/archrev_r2/): shadow KHÔNG ghi registry (PASS); off chỉ đổi m6 (lưu ý: days_ahead=0 cũ bị loại do `or 999`, nay nhận ex=hôm nay).
MAJOR: M1 (CÙNG loại RC1) record không khai cash_leg ⇒ "không so" ⇒ MATCH im lặng, nhưng validate()/park_holdings đọc vắng = 0 ⇒ cổng giá đêm FAIL (TPB thật: lệch −434,7 > 200) — test B9/RC1m đang khẳng định sai. M2 (LOẠI MỚI) câu hỏi UNVERIFIED vẫn dặn ghi record_proposed (id khác) khi registry đã có record CONFIRMED cùng (mã,ex) ⇒ làm theo = áp ×hệ số 2 lần. M3 (CÙNG loại RC2) held_tickers: tài khoản có mặt hôm nay mà positions toàn rỗng ⇒ coi không giữ. M4 đường cron thật run()→_LOCK_HELD→_all() chưa có test (Y16 sống). M5 dry-run re-verify chưa có test (X10 sống).
MINOR: m1 (LOẠI MỚI) registry+vendor có sự kiện, broker không credit ⇒ im; m2 ngân sách 90s không chặn prefetch tuần tự N mã×30s; m3 build_record _status luôn "LỆCH vendor"; m4 re-verify không đọc lịch asof < ex (vendor ex sớm hơn); m5 previous_file không giới hạn tuổi; m6 2 record CONFIRMED trùng (mã,ex) không bị bắt; m7 MATCH-continue không đóng câu hỏi cũ (§26).
Đột biến reviewer sống có ý nghĩa: X1 X2 Y1 (biên dung sai), X6 X7 X8 X12 X16 X17 X23 X24 X34 Y6 Y16 X10.

## r3 (job Taylor_20261004_103554, Opus xhigh) — đọc lại TOÀN BỘ, bảng bất biến, sửa MỘT LẦN
### Bất biến (mỗi cái có chốt ở ĐIỂM GHI hoặc ở ô bảng trạng thái, không chỉ điểm đọc)
- I1 ≤1 record HIỆU LỰC (CONFIRMED*)/(mã, ex). Chốt ghi `_validate_for_write` trong `write_corp_actions` (CẢ nhánh vendor shadow/off lẫn broker) + khối validate trước ghi của broker. Lượt này tạo nhóm trùng ⇒ CorpActionError, 0 ghi (ca thật: lịch vendor ghi lặp 1 ISS ⇒ nhánh vendor cũ ghi 2 record). Nhóm trùng CÓ SẴN (người gõ) không chặn ghi mã khác; `_registry_view` coi là LỆCH khi đối chiếu (m6) + `_registry_sweep` hỏi 1 lần/(mã, ex, ids).
- I2 Registry/near-dup ĐÃ có record cho mã quanh ex ⇒ câu hỏi KHÔNG mang `record_proposed`, mang `registry_update_proposed` {record_id, số broker} + `ONE_RECORD_RULE` (chỉ SỬA/THU HỒI record hiện có hoặc đóng). Cả câu hỏi vendor-vs-registry / vendor-vs-broker / ratio-vs-broker bỏ "REVOKED rồi ghi tay". `record_proposed` CHỈ khi registry trống quanh ex. (M2)
- I3 Vắng `cash_leg_vnd_per_share` = 0.0 đúng như validate/park_holdings/exdate_frame đọc; đối chiếu chân tiền registry↔broker và record↔vendor dùng giá trị đó, lệch >1đ ⇒ LỆCH; NaN/không phải số ⇒ LỆCH. (M1)
- I4 Không suy "không giữ" từ vắng mặt: `held_tickers` ⇒ (held, unknown); tài khoản đã biết (dnse_raw 10 ngày) mà positions hôm nay rỗng/thiếu ⇒ file phiên trước CHỈ khi ≥ phiên liền trước, không thì "không xác định" ⇒ hỏi. (M3, m5)
- I5 Mọi ô kết thúc ở: ghi / hỏi / finding / dòng log trạng thái tường minh. Ô mới phủ: registry hiệu lực + broker không credit ⇒ credit-watch `CHỜ CREDIT` (ex = phiên kế tiếp, log) / `QUÁ HẠN` (ex ≤ hôm nay ≤ ex+1 phiên, sổ broker không có mục ở MỌI mode, mã giữ/không xác định ⇒ question high 1 lần) / `ĐÃ THẤY` / không giữ (log). Registry khớp broker ⇒ ghi 1 dòng sổ `observation_only` (intent+done, 0 bus) làm bằng chứng credit — thiếu nó phiên ex sẽ báo QUÁ HẠN giả. (m1)
- I6 shadow & dry-run: 0 ghi corp_actions.json, 0 question/answer (shadow: 1 finding tóm tắt). off: chỉ nhánh vendor + đúng 1 thay đổi: chốt I1.
- I7 Ngân sách chỉ-giá hỏi TRƯỚC TỪNG lời gọi DNSE, kể cả trong prefetch (prefetch hôm nay gọi từng mã). (m2)
- I8 Registry khớp broker (live) ⇒ đóng câu hỏi cũ cùng mã/phiên (answer 1 lần, khoá sổ); câu hỏi cũ chưa từng gửi ⇒ done `superseded`, không gửi bù. (m7)
- Khác: m3 `_status` record_proposed ghi đúng nguyên nhân (LỆCH vendor / THIẾU trục KL / lý do detector); m4 re-verify đọc lịch tươi asof ∈ [ex−45 ngày, hôm nay].

### Bảng trạng thái LIVE (R registry × B broker; V vendor ở trong ô)
| R \ B | CONFIRMABLE | INSUFF/AMBIG | CASH_DIV | không ứng viên |
|---|---|---|---|---|
| trống | ghi CONFIRMED (V≠/thiếu KL ⇒ UNVERIFIED + record_proposed) | hỏi | finding (V≠ ⇒ hỏi) | vendor có sự kiện: giữ ⇒ vendor-only; không xác định ⇒ held-unknown; không giữ ⇒ log |
| 1 hiệu lực | khớp ⇒ log+đóng hỏi cũ+dòng quan sát; khớp & V≠ ⇒ hỏi (sửa record); lệch ⇒ hỏi (sửa record) | hỏi + luật 1 record | lệch "KL không đổi" ⇒ hỏi | credit-watch CHỜ/QUÁ HẠN/ĐÃ THẤY/không giữ |
| chưa hiệu lực | "CHƯA áp dụng" ⇒ hỏi (sửa record) | hỏi + luật | hỏi | vendor có ⇒ hỏi "CHƯA áp dụng"; vendor không ⇒ không tác động (record không áp) |
| ≥2 hiệu lực | LỆCH "N record HIỆU LỰC" ⇒ hỏi + registry-dup | + registry-dup | + registry-dup | registry-dup |
| near-dup | AMBIGUOUS (giữ UNVERIFIED nếu V≠), sửa record gần | hỏi + luật | — | — |

### Verify (artifact)
selfcheck 498/0 × {python3 3.10, $DNA_PYEXE 3.12} × {ICT, env -u TZ, America/New_York}; ma trận 17 selfcheck ×2 interp ×3 TZ = 102/102 rc=0; `--mutations` 362/362 giết bởi assertion CÓ TÊN (0 chỉ-crash) — gồm 15 đột biến reviewer v2 (X1 X2 Y1 X6 X7 X8 X10 X12 X16 X17 X23 X24 X34 Y6 Y16) + X13 X19 X20 X27 X29; chạy lại mut.py/mut2.py GỐC của reviewer trên bản sao: mọi mẫu còn khớp bị giết trừ X18 (tương đương, đã ghi). Replay `--replay` 92 phiên/15 ứng viên, 515/0 cả 2 interp, sàn THẬT qua `_exchange_fn`. Dry-run THẬT 2026-10-01 (live + shadow): TPB CONFIRMABLE ×1.15 chân tiền 500, đối chiếu registry **MISMATCH** "TPB-2026-10-02-STOCK-DIVIDEND KHÔNG khai (consumer đọc 0)" — đúng thực tế (record production thiếu chân tiền ⇒ cổng giá đêm FAIL), không MATCH im. Dây bẫy DNSE (DNSEBroker/get_dnse_client) trong selfcheck: `tripwire.no_real_dnse_call` PASS. corp_actions.json md5 bfd681e5 không đổi; dnse_raw 10-01 1856 / 10-04 8 dòng không đổi; không tạo ledger production.

### Còn mở (KHÔNG sửa trong r3 — cần user/Mike quyết)
1. Nhánh VENDOR (writer shadow/off hiện hành) ghi record KHÔNG có `cash_leg_vnd_per_share` dù vendor có DIV cùng ex; `check_ratio` ±2% chỉ chặn khi chân tiền >~2% giá ⇒ chân tiền 0,5–2% giá lọt, cổng giá đêm FAIL. Shadow broker nay ghi sổ UNVERIFIED/MISMATCH cho ca này (L5b) nhưng shadow không hỏi. Đề xuất: writer vendor lấy Σ DIV cùng ex làm chân tiền, hoặc không ghi khi có DIV cùng ex.
2. Record production TPB-2026-10-02-STOCK-DIVIDEND thiếu chân tiền 500 — live sẽ hỏi Winston (registry_update_proposed: thêm cash_leg 500). Không sửa (ranh giới).
3. Credit SAU lượt 19:25 không được quét lại (cần lượt 21:00 thứ hai — Q5 cũ, cần duyệt cron); credit-watch QUÁ HẠN nói rõ khả năng này.
4. Record người ký/vendor không re-verify sau ex (chỉ provenance=broker) — giữ quy ước "người đã chốt".

### Arch-review v3 @58c6dff6 — NEEDS_CHANGES ⇒ DỪNG (có lỗi LOẠI MỚI m7; review duy nhất đã dùng)
Probe/kết quả reviewer: /tmp/archrev_r3/ (probe/p1–p7.py, mut3.py, mut4.py, *_out.txt). Reviewer tái hiện: 498/0 ×2 interp ×3 TZ, --mutations 362/362 (assertion có tên), mut.py/mut2.py v2 gốc chỉ X18 (tương đương) sống, 7 selfcheck phụ thuộc 42/42. Mọi mục v2 (M1–M5, m1–m7) xác nhận ĐÃ sửa thật bằng artifact. Artifact dry-run thật đã sinh lại từ HEAD: /tmp/brokerprim/r3_dry_live_1001_HEAD.txt (TPB MISMATCH "KHÔNG khai").
- MAJOR-1 (cùng loại M5/X10): dry-run shadow/off gửi bus question THẬT — writer vendor `write_corp_actions(dry_run=True)` chạy `_validate_for_write`, khối except (auto_confirm.py ~:540-598) gọi append_event validate-reject không kiểm dry_run. Trigger: dòng ISS lặp (chốt I1 mới) HOẶC registry có record hỏng (có từ master). Live dry-run sạch.
- MAJOR-2 (cùng loại M1, §28): khoá registry của script chỉ `.upper()`, consumer `validate()` làm `strip().upper()` ⇒ record "TPB "/" TPB" CONFIRMED ⇒ cả broker live lẫn writer vendor shadow ghi record HIỆU LỰC thứ hai; `_validate_for_write([TPB␠, TPB], [TPB␠])` không ném. 8 record production hiện sạch (tiềm ẩn). Sửa gợi ý: mọi khoá lấy từ output CA.validate().
- MINOR m1 gửi bù câu hỏi cũ mang record_proposed đông cứng (I2 lọt qua đường gửi bù); m2 confirm-only không nêu record NGƯỜI ký ở ex gần (`_broker_record_near` chỉ provenance=broker); m3 câu hỏi UNVERIFIED PRICE_ONLY dặn "ghi record_proposed"; m4 vendor-only/held-unknown/credit-overdue không được answer khi giải quyết + superseded chỉ ở nhánh MATCH; m5 `_record_vs_vendor` coi vendor không khai DIV là "0đ/cp" (vendor_crosscheck coi là PARTIAL); m6 §29 "vendor khai ×1" khi thiếu tỉ lệ, câu QUÁ HẠN liệt kê thiếu nguyên nhân; **m7 LOẠI MỚI: chốt I1 trong writer vendor từ chối CẢ LÔ** (1 ISS lặp chặn ABC hợp lệ; có hỏi người); m8 near-dup neo credit_day không neo ex + writer vendor chỉ chặn near-dup với record broker (có từ trước); m9 docstring off/I5/I6 + shadow phát 2 finding.
- 19 đột biến mới sống (thiếu test): N38 N42 N01 N06 N05 N27 N26 N59 N28 N29 N32 N34 N10b N08 N09 N15 N17 N46 (+ chi tiết ở /tmp/archrev_r3/mut3_out.txt, mut4_out.txt).
- required_changes (11 mục) nằm trong bus finding broker-primary-r3-20261004.


## r4 (job Taylor_20261004_120510, Opus xhigh, chế độ B) — sửa TRỌN arch-review v3 trong MỘT lượt
### Rà soát cả NHÓM trước khi sửa (không chỉ 2 điểm reviewer chỉ)
- **Mọi đường gửi bus / ghi sang (MAJOR-1)**: r3 truyền `dry_run` bằng tay ⇒ 1 chỗ quên (validate-reject writer vendor). Kiểm kê
  bằng AST: `subprocess.run(APPEND_EVENT…)` ở 3 nơi (`_bus`, `post_bus`, validate-reject writer), notify ở `post_bus`,
  `BD.ledger_append` ở 6 nơi, marker ngày ở `_ask_day_once`, registry ở `write_corp_actions`. Nay: **MỘT cổng**
  `_effects_blocked` (cờ `_dry_scope` do `run`/`run_vendor`/`run_broker` đặt); hàm DUY NHẤT chạm từng loại tác dụng:
  `_bus` (append_event), `_discord` (notify), `_ledger_append` (sổ), `write_corp_actions` (registry), `_ask_day_once`
  (marker). Selfcheck D0 kiểm bằng AST rằng KHÔNG hàm nào khác chạm append_event/notify/ledger_append/os.replace/ghi file
  — thêm đường gửi mới vòng qua cổng ⇒ FAIL có tên. Bỏ luôn cờ `dry_run` riêng của `_registry_sweep`/`_reverify` (1 cơ chế);
  dry-run nay IN câu hỏi lẽ ra gửi ("[DRY-RUN] KHÔNG gửi bus question …").
- **Mọi chỗ tạo khoá registry (MAJOR-2)**: 9 nơi tự `.upper()`/`[:10]` riêng (`already_confirmed_set`, `_effective_groups`,
  `_registry_view`, `_near_duplicate`, `_broker_record_near`, `_broker_record_ratio_diff`, `_reverify`, so mã sổ/held/lịch
  vendor/symbol DNSE). Nay: `_reg_rows` = khoá (mã, ex, id) VÀ giá trị (hệ số, chân tiền, hiệu lực) lấy từ OUTPUT
  `CA.validate` — đúng cái consumer đọc; record validate() từ chối ⇒ `_invalid` ⇒ LỆCH. Mã KHÔNG từ registry (symbol DNSE,
  lịch vendor, dòng sổ, held) qua `_norm_ticker` = đúng quy tắc validate (K0 khoá 2 quy tắc vào nhau). Hệ quả: bỏ hẳn các
  phép đọc số riêng (`_cash_leg_as_read`, parse float NaN) — N08/N09/N14/N15/N17/N46 không còn chỗ để sai.
- Hợp nhất: writer vendor dùng CHUNG `_record_vs_vendor` (mọi provenance/trạng thái) + `_near_duplicate` (mọi provenance) với
  nhánh chỉ-xác-nhận ⇒ xoá `_broker_record_near`, `_broker_record_ratio_diff`, `_ask_ratio_vs_broker`,
  `already_confirmed_set`, `_close_stale_questions` (thay bằng `_close_resolved` có khoá 1-lần).

### Đã sửa (đối chiếu required_changes v3)
| Mục | Sửa | Test có tên |
|---|---|---|
| MAJOR-1 | cổng `_effects_blocked` duy nhất (trên) | D0 D0b D1 D2 D3×(6 đường × 3 mode, kèm đối chứng không-dry) D4 D4b D4c D5 |
| MAJOR-2 | `_reg_rows`/`_norm_ticker`/`_iso` từ CA.validate | K0 K1 K1b K1e K2 K2b K3 K4 K5 K6 K7 K8 K9 K10 K11 I1w |
| m1 | gửi bù: `_i2_refresh` tính lại I2 theo registry HIỆN TẠI (cùng ex + near-dup); write-incomplete không mang record khi đã có record khác | m1 ×3, m1b |
| m2 | confirm-only: `_near_duplicate` mọi provenance, câu hỏi nêu id + ONE_RECORD_RULE | m2, B31b |
| m3 | dặn ghi record_proposed CHỈ khi câu hỏi mang nó; chỉ-giá nói "không có record nào để ghi" | m3 |
| m4 | `_resolve_asks` (trong `_registry_sweep`, live) trả lời vendor-only / held-unknown / conflict / cash-leg / QUÁ HẠN khi giải quyết; ghi CONFIRMED ⇒ việc dở cùng mã/phiên superseded + câu đã gửi được answer; câu superseded KHÔNG BAO GIỜ bị "trả lời" (`ledger_state(done_meta=…)`) | m4 ×10, m4b, m4c, N32/N34 |
| m5/m6 | vendor vắng DIV / vắng tỉ lệ = "không khai" (PARTIAL), không 0đ / ×1; `_vendor_mult`; câu QUÁ HẠN nêu điều đã đọc (số mục sổ phiên credit / sổ ĐỌC HỎNG) + 4 nguyên nhân | m5 m6 m6b m6c, m6 QUÁ HẠN ×2 |
| m7 (loại mới v3) | `_group_candidates` gộp dòng trùng hệt TRƯỚC vòng ghi; mâu thuẫn ⇒ CHỈ mã đó bị chặn + hỏi [Winston]; mã khác vẫn ghi; record vừa ghi đi vào near-dup của ứng viên sau | I1d m7 ×2 m7b |
| m8 | near-dup neo ex VÀ phiên credit; mọi provenance ở CẢ writer vendor; REVOKED không khoá (chỉ người sửa tay mới hiệu lực lại), PROPOSED khoá | N41 m8a m8b N42 N42c V1 |
| m9 | docstring off/shadow/dry-run; shadow ĐÚNG 1 finding/lượt (gom pha KL + chỉ-giá) | m9 m9b |
| open #1 r3 (chân tiền writer vendor) | ĐÓNG: writer không tự ghi + hỏi `vendor-cash-leg` khi lịch vendor có DIV cùng ex / lịch DIV đọc hỏng / giá vốn broker báo chân tiền ≥1đ/cp; tài khoản MISMATCH chỉ vì giá vốn (KL đúng hệ số — TPB thật 500đ ≈ 3%) nay HỎI thay vì im "MISMATCH" | C ×4, C5 C6 C7, D3 cash-leg |

### Thay đổi hành vi nhánh vendor ở `off`/`shadow` (writer hiện hành) — đều chỉ biến "ghi/im" thành "không ghi + hỏi"
1. record người ký CÙNG (mã, ex) lệch hệ số/chân tiền vendor ⇒ hỏi (cũ: im "đã CONFIRMED rồi"); record PROPOSED/REVOKED cùng
   (mã, ex) ⇒ đối chiếu, không ghi CONFIRMED thứ hai cạnh nó; 2. record mọi provenance ở ex gần ⇒ hỏi (cũ: chỉ record broker);
   3. ứng viên trùng gộp/mâu thuẫn chặn riêng mã đó; 4. dấu hiệu chân tiền ⇒ hỏi; 5. khoá theo CA.validate.

### Verify (artifact, r4)
- selfcheck broker: **639/0** (python3 3.10) · **641/0** ($DNA_PYEXE 3.12 — thêm biến thể ex dạng gọn mà validate 3.12 đọc
  được) × {ICT, `env -u TZ`, America/New_York}; ma trận 17 selfcheck × 2 interp × 3 TZ = **102/102 rc=0**
  (chạy LẠI trên bản cuối md5 07abe615/0b7a1b22/59341f52: /tmp/brokerprim/r4_matrix_final.txt).
- `--mutations` (chạy lại trên bản cuối, file khôi phục đúng md5 sau lượt): 427 đột biến (362 cũ — 69 mẫu viết lại theo code
  mới, nhãn `r4↻` — + 65 mới r4). **3.10 (interpreter cron): 427/427 giết bởi assertion CÓ TÊN, 0 chỉ-crash.**
  3.12: 426/427 giết bởi assertion CÓ TÊN, 0 chỉ-crash; sống duy nhất `parse 5 chữ số` (đột biến CŨ, tương đương DƯỚI 3.12 vì
  `fromisoformat` 3.12 tự nhận 5 chữ số; cron chạy shebang python3 3.10 nơi nó bị A13 giết).
- 2 bộ đột biến GỐC reviewer v3 (mut3.py/mut4.py) chạy lại trên bản sao: mọi mẫu còn khớp bị giết trừ N12 (reviewer ghi tương
  đương) và N39 (CONFIRMABLE + registry đã có ⇒ luôn thành MATCH-continue/UNVERIFIED trước dòng đó — không chạm được); N40
  nay bị giết (test N40 lưới cuối I1 writer broker). Mẫu không còn khớp (code viết lại) có đột biến tương đương r4 trong MUTANTS.
- Replay `--replay` 92 phiên / 15 ứng viên, D1 7/7 + D5 chỉ-giá, sàn THẬT qua `_exchange_fn`: 656/0 (3.10), 658/0 (3.12) — chạy lại trên bản cuối, output trùng lượt trước.
- Dry-run THẬT 2026-10-01 (live/shadow/off): TPB CONFIRMABLE ×1.15 chân tiền 500, đối chiếu registry **MATCH** — KHÁC r3
  (MISMATCH "KHÔNG khai") vì record production TPB-2026-10-02-STOCK-DIVIDEND đã được thêm cash_leg 500 sau r3 (md5 nay
  e7ace20b) — đúng, không phải lỗi; off: lịch vendor 10-01 không có ứng viên CP. 0 bus (/tmp/brokerprim/r4f_dry_*_1001.txt).
- Dây bẫy `tripwire.no_real_dnse_call` PASS; corp_actions.json md5 **e7ace20b** không đổi; dnse_raw 10-01 1856 / 10-04 8 dòng
  không đổi; không có sổ/khoá production `data/corp_action_broker_ledger.jsonl*`.
- Sự cố trong lúc verify (đã xử lý): lượt `--mutations` chạy foreground bị trần 10' của tool giết giữa đột biến K-j ⇒ file
  `corp_action_auto_confirm.py` còn mang đột biến; phát hiện bằng so md5 với bản sao sạch, khôi phục, chạy lại nền (nohup).
  Soi `git diff` trước commit: không còn dấu vết đột biến.

### Còn mở sau r4
1. Credit SAU lượt 19:25 không quét lại (cần lượt 21:05 — Q5, user duyệt bỏ qua tới khi merge).
2. Record người ký/vendor không re-verify sau ex (giữ quy ước "người đã chốt").
3. Câu hỏi vendor-vs-registry / vendor-near-record không tự `answer` (giải quyết = người sửa record ⇒ người đóng).
4. N39 tương đương (ghi trên); phạm vi `run_broker` dry-run: cờ `_dry_scope` là phòng thủ chiều sâu.

### Arch-review v4 @696797c0 — NEEDS_CHANGES, KHÔNG có lỗi loại mới (review duy nhất r4; KHÔNG vá tiếp — chờ log shadow T2 05/10 + T3 06/10)
**Đã đóng thật (reviewer kiểm bằng artifact, bản sao /tmp/rv4 có stub bus, BUS_LEAK.log rỗng):** MAJOR-1 v3 (0 đường gửi/ghi
ngoài cổng `_effects_blocked`, kiểm grep+AST+runtime 10 giá trị env, `_dry_scope` try/finally), MAJOR-2 v3 (mọi khoá registry từ
CA.validate trong `cac`), I1 ở 16 kịch bản cả 2 writer; m1 m2 m3 m5/m6 m7 m8 m9 open#1. Selfcheck tái hiện 639/641 × 3 TZ; 2 lời
khai đột biến (`parse 5 chữ số` tương đương ở 3.12, N39 tương đương) xác nhận đúng. Đột biến reviewer: 48 mẫu, 34 giết bởi assertion
có tên, 0 chỉ-crash, 10 sống do thiếu test, 4 tương đương.

| # | Mức | Loại | Lỗi |
|---|---|---|---|
| 1 | MAJOR | cùng M2 v2 / m1 v3 (lần lọt I2 thứ 3) | writer vendor (off/shadow) phát `vendor-conflict` / `vendor-cash-leg` TRƯỚC vòng ghi (`_existing_id` tính trước vòng, auto_confirm :481-484, :578-582, :641-642) ⇒ câu hỏi khẳng định "registry chưa có record quanh ex" trong khi cùng lô ghi record cùng mã ở ex kề ⇒ người làm theo tạo record hiệu lực thứ 2 (×hệ số 2 lần). Trigger: lịch vendor cùng mã ở 2 ex trong [hôm nay, phiên kế] — đúng hình dạng test m7b; feed vendor đang chết ⇒ chưa cấp bách |
| 2 | minor | cùng MAJOR-2 v3 | detector gom theo symbol DNSE THÔ (broker_detect :175, :224, :896-898, :917-919, :928); `_norm_ticker` chỉ ở biên `cac` ⇒ A1 'TPB' credit + A2 'tpb ' chưa credit ⇒ CONFIRMABLE thay vì INSUFFICIENT. DNSE thật trả mã chuẩn |
| 3 | minor | cùng m4 v3 | `_resolve_asks` chỉ chạy ở live; `vendor-cash-leg` chỉ phát ở off/shadow ⇒ không bao giờ được answer (nhánh resolver đó là code chết); test m4 dựng ở live |
| 4 | minor | cùng họ M5 v2 / MAJOR-1 v3 (có từ trước r2) | dry-run nhánh broker vẫn là đường riêng (:1735-1749), không chạy quyết định near-dup/I2 ⇒ in "CONFIRMABLE" trong khi lượt thật hỏi `broker-ambiguous`. Không tác dụng phụ. ⇒ artifact "dry-run thật 10-01" KHÔNG phủ near-dup/I2 |
| 5 | minor | cùng m7 v3 (ở writer broker) | lưới cuối writer broker từ chối CẢ LÔ khi 1 record validate() hỏng (detector chặn QTY_MULT_MAX nhưng không CASH_LEG_MAX 50.000) ⇒ mã hợp lệ cùng lô mất ghi đêm đó (có bus question, không im) |
| 6 | minor | test thiếu | đột biến sống G4 (thứ tự `_prune_daymarks` vs cổng) C3 R3 K7 K4 R2 G1 X2 (+K2 N3 bán tương đương) |

Ghi thêm: selfcheck check F0 đọc file production `corp_action_daily_2026-10-02_FAILED.json` (thiếu ⇒ 638 thay vì 639) — phụ thuộc
môi trường. AST D0 không bắt `from subprocess import run` / `os.system` / `open(mode=…)` / `Path.write_text` (code hiện không dùng).
Probe tái hiện + bộ đột biến reviewer: /tmp/rv4/probe/p1-p7.py, /tmp/rv4/mut/ (tạm, có thể mất).

### r5 (job Taylor_20261006_133445, user DUYỆT phương án A 06/10 20:33 — vượt trần vòng có duyệt) — sửa trọn arch-review v4
**MAJOR-1 (I2 lọt lần 3) — sửa tận gốc:** câu hỏi khẳng định trạng thái registry quanh ex KHÔNG còn gửi trong vòng quyết.
- Writer vendor: conflict / cash-leg / near-record gom vào `deferred`, gửi ở `_flush_deferred` SAU khi lô có kết quả, trên
  registry SAU lô (cũ + record lô đã ghi / dry-run sẽ ghi; lô bị từ chối ⇒ chỉ cũ). Câu cash-leg nay nhận `existing` (nêu
  record lô + ONE_RECORD_RULE).
- Writer broker: record lô vào `rows` ngay khi quyết (mục sau cùng mã ex kề ⇒ near-dup; cùng (mã, ex) ⇒ "lô này đã quyết
  ghi"); I2 (bỏ record_proposed, gắn registry_update_proposed) tính MỘT NƠI — `_i2_refresh` sau vòng cho CẢ mục mới lẫn gửi
  bù, trên registry + lô. Nhánh I2 trong vòng (tính trên registry TRƯỚC lô) đã gỡ.

**Kiểm kê cùng lớp ("khẳng định trạng thái registry tính trước khi lô ghi") ở CẢ 2 writer:**

| # | Writer | Chỗ | Trạng thái |
|---|---|---|---|
| 1 | vendor | vendor-conflict (`_existing_id` trước vòng) | SỬA (deferred) |
| 2 | vendor | vendor-cash-leg ("registry chưa có record") | SỬA (deferred + `existing`) |
| 3 | vendor | vendor-near-record: near có thể là record CỦA LÔ, lô bị từ chối ⇒ câu nêu record không tồn tại (chiều ngược) | SỬA (tính lại trên registry sau lô; không còn ⇒ không hỏi, in lý do) |
| 4 | vendor | vendor-vs-registry (record CÙNG (mã, ex) có sẵn) | KHÔNG thuộc lớp — lô không bao giờ ghi trùng khoá; record có trước và sau lô |
| 5 | vendor | post_bus AUTO-CONFIRMED | đã sau ghi (B-4) |
| 6 | vendor live | confirm_only: không ghi; nhánh broker chạy TRƯỚC, vendor đọc registry mới | OK; conflict flush trên registry hiện tại |
| 7 | broker | `dup` trên `rows` trước lô ⇒ 2 CONFIRMABLE cùng mã ex kề ghi CẢ HAI (×2) | SỬA (batch rows) |
| 8 | broker | cùng (mã, ex) 2 lần trong lô ⇒ I1 từ chối CẢ LÔ | SỬA (batch_keys) |
| 9 | broker | upd/record_proposed của mục quyết TRƯỚC record lô | SỬA (`_i2_refresh` sau lô) |
| 10 | broker | gửi bù `_i2_refresh` trước lô | SỬA (sau lô) |
| 11 | broker | write-incomplete `upd` | nhận từ #9/#10 |
| 12 | broker | `registry_has` trong finding shadow | sự thật về registry thật (không khẳng định vắng quanh ex) — giữ |
| 13 | cả 2 | `_registry_sweep` / re-verify | đọc lại registry SAU ghi — OK |

**minor-2:** `BD.norm_ticker` (quy tắc CA.validate) áp NGAY ở `read_series` (khoá symbol) + `same_day_fills`; mọi chỗ
reviewer nêu (:896-898, :917-919, :928, held_tickers) dẫn xuất từ `read_series`. `cac._norm_ticker` gọi `BD.norm_ticker` (1
quy tắc). `_held_info` bỏ chuẩn hoá lặp. Test: A1 'TPB' credit + A2 'tpb ' chưa ⇒ MỘT mã TPB INSUFFICIENT.
**minor-3:** GỠ nhánh resolver `vendor-cash-leg` (chọn gỡ thay vì cho resolver chạy off/shadow): câu đó chỉ phát ở writer
vendor (off/shadow), resolver chỉ chạy live và off KHÔNG chạy `_registry_sweep` ⇒ cho resolver chạy ở off/shadow là thêm
một đường gửi bus answer mới + test cho một câu hiếm, vẫn không phủ off; người ghi record chân tiền đóng câu đó (cùng cách
vendor-near-record / vendor-vs-registry). vendor-conflict giữ (live cũng hỏi).
**minor-4:** dry-run nhánh broker gọi CÙNG `_all()` (2 pha `_run_broker_locked`, re-verify, sweep) với lượt thật; tác dụng
chặn ở `_effects_blocked`; không khoá (0 file .lock); record lô coi như đã ghi (`registry_ids |= lô`) để không báo
write-incomplete giả; sweep nhận `seen_now`. Dòng `[DRY-RUN] <mã> ex … <verdict detector>` giữ làm tóm tắt.
**minor-5:** writer broker validate + I1 TỪNG record trên registry + lô tới giờ ⇒ record hỏng bị loại riêng (live: 0 intent +
question `broker-validate-reject-<mã>-<phiên>`; shadow: mục vẫn vào sổ, why nêu "live sẽ KHÔNG ghi"); registry hỏng TỪ TRƯỚC ⇒
1 question phiên `bad_record_is_preexisting=True` (B-3). Lưới cuối cả-lô gỡ (lô luôn hợp lệ theo dựng). Detector chặn
`cash_leg > CASH_LEG_MAX` ⇒ AMBIGUOUS.
**Test:** `test_r5` 26 assertion có tên (+1 case m4 vendor-conflict, N40 viết lại theo ngữ nghĩa mới, F0 bỏ đọc file production
⇒ dùng fixture, luôn chạy). Control leg: chạy selfcheck mới trên code r4 (HEAD~ của 2 file) ⇒ 16/16 assertion hành vi r5 FAIL
(n2c bỏ qua vì r4 không có `BD.norm_ticker`), 8 assertion đột biến-reviewer PASS (canh hành vi sẵn có) — đúng kỳ vọng.

**Verify:** selfcheck 666/0 (3.10) · 668/0 (3.12; +2 check gated theo phiên bản, có từ r4) × Asia/Ho_Chi_Minh / UTC / `env -u TZ`.
Mutation (bộ đầy đủ trong selfcheck, 449 đột biến; +29 mới r5 gồm G1 G4 C3 R3 R2 K7 K4 X2; cập nhật 15 mẫu cũ theo code mới; bỏ
7 đột biến code đã gỡ/tương đương: X10, N40, r3 I2×2, N38, K-f, err=base_err): **449/449 (3.10)**, **448/449 (3.12 — `parse 5
chữ số` tương đương, đã khai từ r4)**, 0 chỉ-crash. ruff F: sạch. Dry-run thật live 10-01 (TPB MATCH registry) và 10-06 (TV1
PRICE_ONLY INSUFFICIENT — production đang shadow nên không hỏi) rc=0, sha256 registry + sổ y nguyên.

**Đính chính câu chữ minor-3 (r6, arch-review v5 #5):** câu "resolver chỉ chạy live ⇒ nhánh trả lời cash-leg là code chết" ở
trên là SAI. Câu cash-leg hỏi ở off/shadow nằm trong CÙNG sổ broker; `_resolve_asks` chạy ở live ĐỌC được khoá `ASKED` đó và
sẽ trả lời nó SAU khi bật live ⇒ resolver r4 không chết. Việc gỡ nó vẫn giữ, nhưng vì lý do đúng: tiêu chí "registry có record
HIỆU LỰC (mã, ex)" KHÔNG chứng minh chân tiền đã đúng (record thiếu chân tiền vẫn hiệu lực) ⇒ tự trả lời có thể đóng sai.
Hệ quả thật của việc gỡ: câu cash-leg (và vendor-multi-event r6) KHÔNG BAO GIỜ được tự đóng, kể cả sau khi lên live — người
ghi/sửa record đóng nó. Comment ở `_RESOLVE_BY_REGISTRY` đã sửa theo.

### r6 (job Taylor_20261006_143910, user DUYỆT option (2) 06/10 21:38 — sửa trước rồi mới merge) — I2 đóng bằng CẤU TRÚC

**BƯỚC 0 — kiểm chứng thông tin miền của user bằng dữ liệu** (`tav2_bq.corporate_action`, registry: TRAP — dùng làm thống kê
lịch sử, không làm feed). Sự kiện điều chỉnh giá: `DIV` (tiền) + `ISS` có `issue_method_name_vi` ∈ {Trả cổ tức bằng CP, CP
thưởng, Quyền mua CP cho cổ đông hiện hữu} (riêng lẻ/ESOP/chuyển đổi không có ex điều chỉnh giá), bỏ `not_executed`, khoá
(mã, ex) DISTINCT. 20.636 (mã, ex) / 21.523 chân; **cùng ngày có cả chân KL lẫn tiền: 887 (4,3%)**. Cặp (cùng mã, ex KHÁC nhau):

| Loại cặp | Giai đoạn | ≤7 ngày | ≤10 ngày | ≤30 ngày |
|---|---|---:|---:|---:|
| KL–KL | <2015 | 5 | 7 | 15 |
| KL–KL | ≥2015 | 2 | 3 | 8 |
| KL–tiền | <2015 | 15 | 19 | 82 |
| KL–tiền | ≥2015 | 20 | 29 | 133 |
| tiền–tiền | <2015 | 2 | 2 | 7 |
| tiền–tiền | ≥2015 | 5 | 7 | 36 |
| **Tổng** | | **49** | **67** | **281** |

≤10 ngày = 67 / 20.636 ≈ 0,32% sự kiện cả lịch sử; từ 2020: 24 cặp ≈ 4/năm TOÀN thị trường (ví dụ: AIG 07-31→08-04/2026 tiền→KL,
DSE 01-07→01-09/2026, GEE 04-23→04-28/2025, PNJ 12-29/2022→01-06/2023 KL→tiền, MWG 06-07→06-16/2022, ABW 08-20→08-25/2021 KL–KL).
⇒ **Xác nhận "hiếm" (nhưng không bằng 0)**; "cùng ngày" phổ biến hơn ~13×. Thiết kế dưới chặn + hỏi người cho ca hiếm, giữ
nguyên đường cùng-ngày.

**Thiết kế (khuyến nghị arch-review v5).** `_multi_event(rows, tk, cand, credit_day)`: sự kiện trong cửa sổ = ex ứng viên lô ∪ ex
record registry gần (`_near_rows`: MỌI provenance, mọi trạng thái trừ REVOKED, neo MỌI ex ứng viên + phiên credit, ±NEAR_DUP_DAYS=10,
ex không đọc được ⇒ tính gần — CÙNG vị từ với `_near_duplicate`, nay dùng chung). Nhiều chân CÙNG ex = 1 sự kiện (đối chiếu /
conflict như cũ). **≥2 ex KHÁC nhau ⇒ writer KHÔNG ghi gì cho mã, hỏi người ĐÚNG 1 lần, liệt kê đủ** (lô + record registry).
- Writer vendor (off/shadow): gom theo mã TRƯỚC vòng (ứng viên + chân conflict) ⇒ `vendor-multi-event-<mã>-<phiên>` [Winston]
  (khoá sổ `[vendor-multi-event, mã, các ex, sha1(danh sách), ASKED]` — tập đổi ⇒ hỏi lại). Mã còn lại có đúng 1 ex và registry
  không có record của mã ở ex khác trong cửa sổ ⇒ việc lô ghi gì KHÔNG đổi được câu trả lời cho câu hỏi về mã nào ⇒ mọi câu hỏi
  (conflict / cash-leg / vendor-vs-registry) gửi NGAY trong vòng. **Gỡ:** `deferred`, `_flush_deferred`, nhánh near-record
  trong writer (mã đó đã vào multi), `rows += record lô`, tham số `existing` của câu cash-leg (luôn None theo cấu trúc).
- Writer broker: gom kết quả sự kiện KL (kind None) theo mã TRƯỚC vòng; ≥2 ex trong cửa sổ (tính registry) — HOẶC ≥2 kết quả
  cho 1 mã trong 1 pha (detector hứa ≤1/mã/pha; vi phạm ⇒ không đoán) — ⇒ ĐÚNG 1 mục sổ AMBIGUOUS (UNVERIFIED nếu có chân lệch
  nguồn ⇒ vẫn gọi Winston), why + `multi_event` liệt kê đủ, KHÔNG record/record_proposed. **Gỡ:** `batch_keys`,
  `rows = rows + record lô`, `fin = actions_raw + batch` (suy luận "registry sau lô").
- Câu nào còn gửi SAU khi ghi tính trên registry **ĐỌC LẠI từ đĩa**: `_i2_refresh` cho mục mới + gửi bù (dry-run: + record lô —
  cổng đã chặn ghi); đọc lại thô hỏng ⇒ `_i2_unknown` (không bao giờ đề xuất ghi record, nói thẳng). Mục mới cũng qua I2 TRƯỚC khi
  ghi sổ (registry trước lô = sau lô cho mã của mục, theo cấu trúc) ⇒ dòng sổ không mang record_proposed cạnh record có sẵn.

**Danh sách sửa A (arch v5):**
1. Câu hỏi dời mất khi exception/OSError/kill — **không còn câu dời** ở writer vendor (lý do cấu trúc trên). Writer broker:
   lỗi ghi (OSError…) được bắt, đọc lại registry quyết (CONFIRMABLE vắng ⇒ write-incomplete CÙNG lượt, không chờ lượt sau);
   validate-reject gửi trong `finally`. Còn lại (đã biết): SIGKILL đúng giữa ghi và câu validate-reject broker ⇒ câu đó mất
   (record bị từ chối có 0 dòng sổ) — cửa sổ mili-giây; ở off, exception trong `run_vendor` vẫn lan ra cron như trước (off không
   có `_run_branch`) — câu hỏi ĐÃ quyết trước đó đã gửi. Test `r6 #1a/#1b` × off/shadow (gồm probe p4 v5).
2. Đột biến sống v5: N01 (`r6 N01`), N23 (`r6 N23`), N03 (`r6 N03` — write-incomplete khi record của mục ĐÃ trong file mà
   load_corp_actions() lỗi: không tự trỏ, không mang record; thêm cờ `record_in_file`), N22 (`r6 N22`), N04 (`r6 N04`), N05
   (`r6 N05` — shadow: record TPB không vào lô khi registry đã có (mã, ex) ⇒ ABC không bị lưới I1 đánh oan). `if rcf:` ⇒ check
   có tên `r6 tiền đề M1` (thiếu CONFIRMABLE ⇒ FAIL có tên, không im lặng bỏ ca).
3. Câu broker validate-reject: gửi SAU write + đọc lại (trong `finally`), qua `_i2_refresh`/`_i2_act` trên registry đọc lại;
   "mã khác cùng lô ĐÃ ghi" chỉ cho id đọc lại xác nhận (`batch_written`); rc bus từng câu kiểm (lỗi ⇒ in mã chưa được hỏi, rc=1).
   Writer vendor: rc câu validate-reject vào `ask_failed` ⇒ câu vendor-ask-failed. Test `r6 #3a–#3e`, `#3v`.
4. `_SEEN_NOW[ngày]` = kết quả nhánh broker lượt này ⇒ `_vendor_confirm_only(seen_now=…)` (cả dry-run lẫn live — live: record
   bị validate từ chối có 0 dòng sổ, thiếu nó vendor hỏi vendor-only trùng). Test `r6 #4/#4b/#4c`.
5. Đính chính minor-3 ở trên.

**Thay đổi hành vi so với r5 (cố ý):** mã có 2 ex trong cửa sổ — r5 ghi 1 record rồi hỏi (near-record/cash-leg/conflict nêu
record vừa ghi); r6 KHÔNG ghi gì và hỏi 1 câu multi-event. B17: lỗi ghi broker không còn ném ra (r5: lan ra, câu
write-incomplete chờ lượt sau). N40: 2 kết quả cùng (mã, ex) trong 1 pha — r5 ghi 1 + AMBIGUOUS; r6 0 record + 1 AMBIGUOUS.
Gỡ thêm `+ batch` khỏi validate từng record broker (đột biến v5 N08 thành TƯƠNG ĐƯƠNG theo cấu trúc; `write_corp_actions` vẫn
validate CẢ danh sách lần cuối, lỗi ⇒ bắt + đọc lại). Chốt "chỉ sự kiện KL vào multi" còn MỘT chỗ (`share`), bỏ điều kiện lặp ở
vòng (đột biến cũ "chặn ×2 áp cả chỉ-giá" sống vì 2 chốt dư — nay bị L1b giết).

**Verify (artifact, r6):**
- Selfcheck: **705/0 (py3.10) · 707/0 (py3.12)** × Asia/Ho_Chi_Minh / UTC / `env -u TZ` — 6/6 xanh. Mới: `test_r6` (danh sách A +
  N01 N03 N04 N05 N22 N23), `test_r6b` (biên cửa sổ D−10/EX+10/D−11/EX+11, ex không đọc được, `_SEEN_NOW` cũ, near-record live có
  id), `r6 S1*` thay M1a–f (mỗi ca chạy CẢ thứ tự xuôi lẫn ngược ⇒ kiểm không phụ thuộc thứ tự lô), N11, M2a+; B17/B31/V*/R4b–R6/
  Q11/Q21/D3/m7b/N40 viết lại theo ngữ nghĩa mới.
- Control: selfcheck r6 chạy trên code r5 (`git archive 26fbc30d`) ⇒ **48 FAIL có tên** + crash cuối (`_SEEN_NOW` không có) — các
  assertion hành vi mới đều FAIL; assertion canh đột biến-reviewer (N04/N05/N22 …) PASS trên r5 đúng kỳ vọng (canh hành vi sẵn có).
- Mutation (bộ trong selfcheck, chạy song song trên bản sao — KHÔNG chạy selfcheck khác trong worktree lúc đang đột biến tại chỗ):
  **472/472 (3.10)**, **471/472 (3.12 — `parse 5 chữ số` tương đương, khai từ r4)**, 0 chỉ-crash. 31 neo cũ hết khớp: 20 neo lại
  (`[r6 neo lại]`), 11 đột biến của cơ chế đã gỡ thay bằng đột biến tương ứng của thiết kế mới (`r6 [thay …]`); +23 đột biến r6
  (gồm ý v5 N01/N23, N05, N11, N17, N22). Lần chạy đầu 459/467: 8 sống + 1 chỉ-crash (#9 khoá near-record, chặn ×2 chỉ-giá, hậu
  tố "số broker để sửa", m8 neo ex/credit ×2, I2 trước ghi sổ, `_near_rows` ex hỏng, `_SEEN_NOW` không xoá; crash M2b) ⇒ thêm test
  có tên/sửa code, 9/9 bị giết.
- Bộ đột biến reviewer v5 (`/tmp/rv5/mut/muts.py`, 23): **11/11 neo còn khớp bị giết** (N04 N05 N06 N07 N09 N11 N12 N16 N18 N19
  N20); 12 neo trỏ vào code đã gỡ (N01 N02 N03 N08 N10 N13 N14 N15 N17 N21 N22 N23 — deferred/_flush_deferred, batch, fin suy luận,
  nhánh near-record writer) — ý của N01/N03/N17/N22/N23 có đột biến tác giả tương ứng, đều bị giết.
- Dry-run dữ liệu thật 10-01 và 10-06 × off/shadow/live: rc=0; sha256 `data/corp_actions.json` (21a88fb5…) y nguyên, sổ broker
  production vẫn không tồn tại (chỉ có .lock cũ 10-05). 10-01 live: TPB CONFIRMABLE ⇒ MATCH record người ký, không ghi/hỏi;
  10-06 live: TV1 PRICE_ONLY INSUFFICIENT ⇒ in câu insufficient lẽ ra gửi. Không mã nào rơi vào multi-event trên dữ liệu thật.

**Còn mở / cần Mike–user quyết:** (a) câu `vendor-multi-event` không có resolver tự động (như cash-leg) — người đóng; (b) SIGKILL
đúng giữa ghi và câu validate-reject broker ⇒ câu đó mất (0 dòng sổ) — nếu muốn bền tuyệt đối thì ghi intent `VALIDATE_REJECT`
vào sổ (thêm verdict mới, đụng consumer sổ) — chưa làm; (c) KHÔNG merge, KHÔNG đổi crontab, `MIKE_CA_BROKER_SOURCE` mặc định giữ
shadow.

### r7 (job Taylor_20261007_030542, user giao 07/10 10:02 — vòng cuối phạm vi hẹp) — m2 + m3 test, m4 I2 XUYÊN LƯỢT
Nhánh `feat/broker-primary-r7-20261007` (worktree `wt-bp-r7-1007`, từ master 6daeca8d ⊇ dd893add). KHÔNG merge, KHÔNG đổi
crontab, `MIKE_CA_BROKER_SOURCE` mặc định giữ shadow.

**m2 (V19, V46 — chỉ test).** `test_r7`: "r7 V19" (UNVERIFIED mang record_proposed + đọc lại thô hỏng ⇒ câu KHÔNG mang
record_proposed, nói "ĐỌC LẠI HỎNG", không dặn ghi), "r7 V46" (p10: ghi OK, đọc lại thô + load_corp_actions EIO ⇒ write-incomplete
record=None + registry_unreadable; mục GỬI BÙ VPB mang record_proposed cũng bỏ nó), tiền đề có tên (đường lỗi thật sự đi qua).
Phụ (sửa hẹp, có): key `registry_unreadable` vào payload câu UNVERIFIED VÀ câu chung (INSUFFICIENT/AMBIGUOUS) — test có tên.
**m3 (V17 — chỉ test).** "r7 V17": p9 (gửi bù UNVERIFIED ex A record_proposed + lô CONFIRMABLE ex B, BQ có đủ 2 sự kiện) — lượt
thật ghi B + gửi bù bỏ record_proposed; dry-run bắt payload qua `_bus` ⇒ câu gửi bù GIỐNG HỆT lượt thật, registry không đổi.

**m4 — thiết kế (luật user 07/10).**
- `_asked_rows(intents, mode, rows)`: câu hỏi ĐÃ có trong sổ broker (cùng mode; đã gửi hay chờ gửi bù) = verdict mở
  (INSUFFICIENT/AMBIGUOUS/DEFER/UNVERIFIED) + CONFIRMABLE mà record VẮNG registry (write-incomplete); bỏ dòng chỉ-quan-sát, CASH_DIVIDEND
  (finding, không phải câu hỏi), mục không có ex, và ex đã thành record registry (mọi trạng thái: hiệu lực ⇒ nhánh multi-event
  registry sẵn có giữ nguyên; REVOKED ⇒ người đã xử lý ex đó). Dạng phần tử `_reg_rows` ⇒ dùng CHUNG `_near_rows`.
- `_cross_day` (chỉ khi `_multi_event` registry/lô = None): câu đã hỏi ex A ≠ ex lô B trong cửa sổ ±10 (neo mọi ex lô + phiên
  credit, cùng vị từ) ⇒ `_bq_event_exes`: `corp_action_lib.feed_freshness` (nạp gần nhất ICT < phiên liền trước ⇒ STALE — cùng mốc
  FRESH của `corp_action_daily.gate_freshness`, không import file đó vì pop env + cổng SystemExit) rồi `pricing_events([mã],
  since=min−1, until=max)` + `is_price_adjusting` (định nghĩa BƯỚC 0). **BQ có sự kiện ở MỌI ex ⇒ xử lý B bình thường; thiếu ≥1 /
  tra lỗi / stale / quá trần ⇒ KHÔNG ghi B, 1 mục AMBIGUOUS (UNVERIFIED nếu chân lệch nguồn) nêu: câu đã hỏi (ex A, verdict, phiên,
  topic, khoá sổ) + lô ex B + "BQ: … THIẾU […]" hoặc "tra BQ LỖI (<lỗi thật>)".** Payload thêm `cross_day`.
- Hỏi 1 lần: khoá done `["broker-cross-day", mã, "exA,exB", sha1(mode+tập ex), "ASKED"]` ghi CÙNG chỗ với done của mục
  (`_done_rows`: live sau bus, shadow sau finding, gửi bù cũng vậy). Khoá có ⇒ không tạo mục, vẫn không ghi B. Tập ex đổi ⇒ hỏi lại.
  mode trong sha1 ⇒ done của lượt shadow KHÔNG chặn câu live sau khi bật.
- Trần thời gian BQ `BQ_XDAY_BUDGET_S=60` (luồng daemon): tra BQ chạy TRƯỚC mọi lần ghi của lô, `bq()` mặc định 300s × 2 truy vấn
  ⇒ không chặn trần thì BQ treo kéo ghi registry các mã khác qua park_trim 19:30. Quá trần = lỗi ⇒ hỏi.
- Registry đã có record (mã, B) ⇒ không cross-day (không ghi gì cho B; nhánh đối chiếu registry lo).
- shadow chạy CÙNG logic trên sổ shadow (finding nêu lý do) — bản xem trước trung thực của live; dry-run đọc BQ (đọc, không tác dụng).

**ĐỀ XUẤT (không làm):** (1) áp ngoại lệ "BQ có đủ sự kiện ở mọi ex" cho nhánh multi-event REGISTRY (A đã là record): hiện vẫn chặn +
hỏi kể cả khi BQ xác nhận 2 sự kiện thật — ~4 ca/năm toàn thị trường, đổi = thêm đường tự ghi cạnh record có sẵn, cần user chốt.
(2) ~~Câu hỏi phía vendor (`vendor-*` ASKED, off/shadow + confirm-only live) KHÔNG tính vào `_asked_rows`: vendor_check của detector đã
đối chiếu lịch vendor mỗi lượt (ex lệch ⇒ UNVERIFIED); thêm thì phải parse khoá done tự do.~~ **SAI — sửa ở r8 (MAJOR-1 arch r7):**
lịch vendor chỉ chứa ex trong [asof, asof+10] (`corp_action_daily.py:1265`) ⇒ ex A đã qua KHÔNG còn trong lịch ⇒ broker suy ex B ≠ A
thì vendor_check = NO_EVENT ⇒ CONFIRMABLE ⇒ r7 ghi B không tra BQ, không hỏi (probe reviewer). r8 tính khoá done vendor-*. (3) `_close_resolved` vẫn chỉ đóng câu
cùng phiên credit — câu cross-day do người đóng (như vendor-multi-event).

**Verify (artifact, r7):**
- Selfcheck **751/0 (py3.10) · 753/0 (py3.12)** × Asia/Ho_Chi_Minh / UTC / `env -u TZ` — 6/6. Mới: `test_r7` 41 assertion (V19×3,
  V46×4, V17×2, m4.1–m4.8 gồm 3 nhánh BQ đủ/thiếu×4/lỗi×3 + quá trần + biên tươi ICT, biên cửa sổ D−10/EX+10 hỏi, D−11/EX+11 ghi,
  idempotent/tập đổi/tách mode, lọc câu đã hỏi ×6, shadow, dry-run) + dây bẫy BQ (`tripwire.no_real_bq_call`). M1g (r5) viết lại theo
  luật mới: chạy với BQ có đủ 2 sự kiện.
- Control: selfcheck r7 trên code master ⇒ 11 FAIL có tên (m2 payload ×2, V46 gửi bù, m4.1b/4.2×4/4.3×3) rồi crash
  (`BQ_XDAY_BUDGET_S` chưa có); V19/V17/V46-mới PASS trên master đúng kỳ vọng (canh hành vi sẵn có — đó là lỗ hổng TEST m2/m3).
- Mutation (bộ trong selfcheck, song song trên bản sao `/tmp/r7_pmut.py`): **506/506 (3.10)**, **505/506 (3.12 — `parse 5 chữ số`
  tương đương, khai từ r4)**, 0 chỉ-crash. +31 đột biến r7 (V17/V19/V46 neo Y NGUYÊN của reviewer + V46b + 27 cho m2 payload/m4). Lần
  chạy đầu: 2 sống ("khoá bỏ tập câu đã hỏi" ⇒ đổi thiết kế khoá sang (mode, tập ex) đúng chữ user + test tách mode; "khoá bỏ mode"
  ⇒ test dùng khoá do lượt shadow THẬT sinh ra); 2 hồi quy bộ cũ do r7 đụng (r4 m9 neo lại `_done_rows`; r4 N42 crash KeyError
  'effective' ⇒ phần tử câu-đã-hỏi mang đủ khoá `_reg_rows`). Sau sửa: hết.
- Probe reviewer r6 trên r7: p8(1) payload có `registry_unreadable`, không record_proposed; p8(2) (hôm qua hỏi TPB ex 10-01, hôm nay
  CONFIRMABLE ex 10-02) ⇒ registry [] + 1 câu ambiguous (BQ ở probe = dây bẫy ⇒ lỗi ⇒ hỏi); p10 write-incomplete record=None.
- Dry-run dữ liệu thật 10-01 và 10-06 × off/shadow/live: rc=0 cả 6; sha256 `data/corp_actions.json` 21a88fb5… y nguyên; sổ broker
  production vẫn không tồn tại (chỉ .lock 10-05) ⇒ không câu đã hỏi nào ⇒ không tra BQ. 10-01 live: TPB MATCH record người ký; 10-06
  live: TV1 PRICE_ONLY INSUFFICIENT (câu lẽ ra gửi).

### r8 (job Taylor_20261007_034436, user DUYỆT phương án (1) 07/10 10:44 — sửa cả 5 lỗi arch-review r7, vòng sửa cuối)
Cùng nhánh `feat/broker-primary-r7-20261007` (worktree `wt-bp-r7-1007`, trên 179e4686). KHÔNG merge, KHÔNG đổi crontab,
`MIKE_CA_BROKER_SOURCE` mặc định giữ shadow. Đọc lại TOÀN BỘ phần đụng một lần trước commit.

- **MAJOR-1 (khoá vendor).** `_asked_rows(intents, done, mode, rows)` đọc thêm khoá done `[loại, mã, ex(,…), 'ASKED']` với loại ∈
  `_ASKED_VENDOR_KINDS` = vendor-only, vendor-held-unknown, vendor-conflict, vendor-cash-leg, vendor-multi-event (k[2] tách ','),
  vendor-near-record, vendor-vs-registry — mọi mode (câu vendor là câu THẬT đã gửi); bỏ khoá đã có `("closed",)+k[:-1]` (đã được
  `_resolve_asks` trả lời) và ex đã thành record registry (như mục sổ broker). Lý do gồm cả 7: mọi loại vendor-* đều là câu hỏi người
  về sự kiện CP ở ex trong khoá; vendor-vs-registry/near-record có record ở/quanh ex — ex đã là record thì `inreg` loại, ex vendor ≠ ex
  record thì ex vendor VẪN là câu đã hỏi. KHÔNG tính: broker-cross-day (tập ex = mục sổ broker + câu đã hỏi, đã đếm từ gốc),
  credit-overdue/registry-dup/reverify (hỏi về record registry). Probe reviewer: r7 `registry=['TPB-…-BROKER-SHARE-EVENT'] BQ_calls=[]
  questions=[]` → r8 `registry=[] BQ_calls=[fresh, events] questions=['corp-action-broker-ambiguous-TPB-2026-10-01']` (cả ca vendor-only
  lẫn broker UNVERIFIED).
- **minor-1 (loại sự kiện).** `_bq_event_exes_raw` trả `{ex: {SHARE|CASH}}` (ISS điều chỉnh giá ⇒ SHARE, DIV ⇒ CASH). `_cross_day`
  đòi ĐÚNG loại theo ex: ex lô (nhánh KL, kind None) ⇒ SHARE; câu đã hỏi theo `need` (event_kind SHARE_EVENT/None + mọi câu vendor ⇒
  SHARE; PRICE_ONLY/khác ⇒ CASH). Câu hỏi nêu "THIẾU ex X: ISS điều chỉnh giá / DIV". Fake V17 + M1g sửa ISS ở cả 2 ex.
- **minor-2 (gửi bù).** `_cross_day` khi BQ đủ ghi bằng chứng `confirmed[mã] = {exes, bq}` (`xday_ok` của lượt). `_i2_refresh(…, xday)`:
  mục có ex trong tập đó ⇒ record ở ex KHÁC trong tập KHÔNG tính near-dup (BQ chứng minh khác sự kiện) ⇒ giữ `record_proposed`,
  KHÔNG `registry_update_proposed`, mang `cross_day_bq`; câu UNVERIFIED/write-incomplete/chung thêm câu nói bằng chứng + key
  `cross_day_bq` trong payload. V17 (lượt thật + dry-run) và M1g viết lại theo hành vi mới.
- **minor-3 (lỗ test).** Test có tên: câu AMBIGUOUS và DEFER_VENDOR lượt trước tính là đã hỏi; ex không đọc được ⇒ `_bq_event_exes_raw`
  trả LỖI "ex không đọc được […]" (trước: bỏ qua ⇒ phụ thuộc caller) ⇒ hỏi, không gọi BQ events.
- **minor-4 (trần TỔNG).** `xday_deadline = monotonic() + BQ_XDAY_BUDGET_S` một lần/lượt; `_bq_event_exes(…, deadline)` chờ phần còn
  lại; hết trước khi tra ⇒ KHÔNG tra, lỗi "hết trần TỔNG 60s … (các mã trước đã dùng hết)"; quá giữa chừng ⇒ "quá trần TỔNG". Cả hai
  fail-closed ⇒ không ghi mã đó, hỏi người với lý do thật.

**Verify (artifact, r8):**
- Selfcheck **782/0 (py3.10) · 784/0 (py3.12)** × Asia/Ho_Chi_Minh / UTC / `env -u TZ` — 6/6. Mới: `test_r8` 30 assertion (MAJOR-1 ×7
  loại vendor [multi-event: ex gần ở VỊ TRÍ 2 của k[2]] + đủ/closed/đã-record/khoá-không-tính ×4/shadow + "HỎI LẠI" trong câu; minor-1 ×4;
  minor-2b ×3 (mục gửi bù ex NGOÀI tập BQ ⇒ I2 thường + dry-run trung thực); minor-3 ×3; minor-4 ×3 gồm luồng treo là daemon) + m4.2
  ca "DIV ở ex lô KL".
- Control: selfcheck r8 trên code r7 (179e4686) ⇒ 13 FAIL có tên (M1g, V17 ×2, m4.2-DIV, m4.3c, MAJOR-1 ×7, MAJOR-1b) rồi crash
  (`_asked_rows` đổi chữ ký).
- Mutation (bộ trong selfcheck, `--mutations` trên 2 bản sao cô lập `/tmp/r8_m310`, `/tmp/r8_m312`): **538/538 (3.10)**,
  **537/538 (3.12 — `parse 5 chữ số` tương đương, khai từ r4)**, 0 chỉ-crash. +32 đột biến r8 (MAJOR-1 ×14: tắt nguồn done vendor,
  bỏ từng loại ×7, multi-event không tách ex, tính câu đã closed, không đòi ASKED, tính mọi loại khoá, tính ex đã thành record, câu
  không nêu topic; minor-1 ×6; minor-2 ×6; minor-3 ×2; minor-4 ×2; reviewer HỎI LẠI + daemon) + 6 đột biến r7 neo lại theo code r8.
  Lần chạy đầy đủ thứ nhất: 3 sống ("r7 V17 dry-run fin_raw" — V17 nay không còn phân biệt vì bằng chứng BQ giữ record_proposed;
  "multi-event không tách ex" — ex đầu trùng A nên `_iso[:10]` che; "minor-2 áp cả mục ex NGOÀI tập") ⇒ thêm minor-2b (mục gửi bù C ex
  10-13 ngoài cửa sổ câu-đã-hỏi nhưng gần phiên credit ⇒ I2 thường; lượt thật vs dry-run) + đặt ex gần ở VỊ TRÍ 2 của khoá
  multi-event. Sau sửa: hết.
- Đột biến reviewer r7 (`/tmp/arch_r7/mut.py`, chạy lại trên bản sao cô lập `/tmp/r8_rev`): áp được 12/16 (4 pattern không còn vì code
  đổi — bản tương ứng nằm trong bộ selfcheck: "r8 minor-4 trần theo từng mã", "r8 minor-3 ex không đọc được ⇒ coi BQ có", "r7 m4 BQ có
  1 sự kiện đã coi là đủ", bản "asked chỉ tính câu CHƯA done" thay bằng nguồn done vendor). 9 GIẾT (gồm bỏ AMBIGUOUS / DEFER_VENDOR /
  cả hai). 3 SỐNG ở lần đầu: "câu hỏi lại bỏ chữ HỎI LẠI" + "daemon False" ⇒ thêm assertion có tên (r8 "HỎI LẠI", r8 minor-4c) +
  neo vào MUTANTS; "ask_key chỉ theo mã" = TƯƠNG ĐƯƠNG (khoá vẫn chứa tập ex ở k[2] và mode trong sha1 ⇒ không đổi hành vi).
- ⚠ Sự cố quy trình (tự gây, đã xử lý): lần đầu tôi chạy SONG SONG 2 runner đột biến trên CÙNG file worktree (cả hai sửa tại chỗ) ⇒
  kết quả lần đó vô hiệu, file còn 3 vết đột biến (`if True:` ở is_price_adjusting, chữ "HỎI LẠI" bị xoá, đuôi `__main__` nhân đôi) —
  phát hiện bằng đối chiếu pattern MUTANTS + đọc toàn bộ diff, khôi phục tay, rồi mọi lần chạy đột biến sau đều trên bản sao riêng.
- Dry-run dữ liệu thật 10-01 và 10-06 × off/shadow/live: rc=0 cả 6; sha256 `data/corp_actions.json` 21a88fb5… y nguyên; sổ broker
  production vẫn không tồn tại (chỉ .lock 10-05) ⇒ không câu đã hỏi ⇒ không tra BQ. 10-01 live: TPB MATCH record người ký; 10-06 live:
  TV1 PRICE_ONLY INSUFFICIENT (câu lẽ ra gửi).

## r9 (2026-10-07, job Taylor_20261007_050650) — arch-review r8 MAJOR-r8-1

- **Lỗi (do r8 tạo ra):** `_asked_rows` (`bin/corp_action_auto_confirm.py`, nhánh (b) khoá vendor) loại câu vendor đã có khoá
  `("closed",)+khoá[:-1]`. Nhưng `_resolve_asks` đóng câu vendor-only khi sổ broker LIVE có mục (mã, ex) với verdict BẤT KỲ, kể cả
  CASH_DIVIDEND (`decided_by agent`) ⇒ probe2 reviewer: vendor-only hỏi TPB ex A=09-28 → broker thấy chỉ-giá ở (TPB, A) ra
  CASH_DIVIDEND → câu bị đóng → lượt D broker KL ex B=10-02 CONFIRMABLE được GHI mà không tra BQ (trái luật m4 user "đã HỎI bất
  kỳ nhánh nào ⇒ tra BQ", không điều kiện câu còn mở).
- **Sửa:** bỏ điều kiện closed. Đường đóng bằng record registry đã có `inreg` phủ.
- **Test:** đảo `r8 MAJOR-1c` thành `r9 MAJOR-1c` (câu vendor đã closed VẪN là câu đã hỏi ⇒ tra BQ, không ghi B, đúng 1 câu);
  `r9 probe2` ×2 (tiền đề: `_resolve_asks` THẬT ghi `['closed','vendor-only','TPB',A]` vì CASH_DIVIDEND; rồi BQ chỉ ISS+DIV ở A ⇒
  không ghi B, tra BQ, đúng 1 câu ambiguous); `r9 P8` (gửi bù UNVERIFIED ex A ∈ tập BQ {A,B} + record C 09-20 gần A NGOÀI tập ⇒ bỏ
  record_proposed, đề nghị sửa C).
- **Đột biến:** +2 — "r9 MAJOR-1 câu vendor đã đóng không tính là đã hỏi (bản r8)" (thay đột biến r8 ngược chiều) và "r9 P8 I2 xday
  lọc MỌI record của mã" (chỉ `r9 P8` giết). 3 neo r8 (`if (len(k) < 4 …`) neo lại theo dạng `if` một dòng mới.
- **Control:** selfcheck r9 trên code r8 (58aa852d) ⇒ đúng 2 FAIL có tên (`r9 MAJOR-1c`, `r9 probe2`).
- Selfcheck **785/0 (py3.10) · 787/0 (py3.12)** × Asia/Ho_Chi_Minh / UTC / `env -u TZ` — 6/6. Mutation (bản sao cô lập
  `/tmp/tay_r9/wt`, `/tmp/tay_r9/wt312`): **539/539 (3.10)**, **538/539 (3.12 — `parse 5 chữ số` tương đương, khai từ r4)**, 0 chỉ-crash.
- probe2 reviewer chạy lại trên bản sao code r9: registry `[]`, BQ tra 1 lần, đúng 1 câu `corp-action-broker-ambiguous-TPB-2026-10-01`.
  probe P8: bỏ record_proposed, `registry_update_proposed` = `TPB-2026-09-20-BROKER-SHARE-EVENT`.
- Dry-run dữ liệu thật 10-01 và 10-06 × off/shadow/live: rc=0 cả 6, 0 Traceback; sha256 `data/corp_actions.json` 21a88fb5… y nguyên;
  sổ broker production vẫn không tồn tại (chỉ .lock 10-05). Không làm m3/m4 khác của reviewer (để sau live).
