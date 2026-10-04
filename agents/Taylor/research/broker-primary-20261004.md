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
