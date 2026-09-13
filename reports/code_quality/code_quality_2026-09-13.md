# Code quality weekly — 2026-09-13

File đã quét: 25 (hot-core tuần này: `/home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py`)
Finding: 25 (từ 25 trước verify)

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:518 — correctness (medium)
- Owner đề xuất: Taylor
- DNSEBroker.connect() ghi loan_package_id của account lên DNSEClient DÙNG CHUNG (pool theo credentials file) — 3 account live cùng credentials_file=None nhưng loan_package_id khác nhau (ZaloPay None, SpaceX 1841, RocketX 1122); tiến trình nào connect >=2 profile (bot_execute.py không --account hoặc nhiều --account, loop line 104-111 và 566-720) thì account connect sau ghi đè gói default của account trước, còn _resolve_loan_package_id/_validate_lever_package (line 865, 904) và dnse_api.place_order/ppse (line 149, 218) đều đọc lại client.loan_package_id ⇒ SpaceX có thể đặt lệnh/đo ppse bằng gói 1122 của RocketX. Cron hiện chạy 1 account/tiến trình nên đang latent.
- Bằng chứng: brokers.py:63-68 `_DNSE_POOL[path] = DNSEClient.from_credentials_file(path)` (1 client/credentials); :518-519 `if self._loan_package_id is not None: self.client.loan_package_id = self._loan_package_id`; secrets/trading_bot_accounts.json: ZaloPay/SpaceX/RocketX đều credentials_file=None, loan_package_id None/1841/1122; trading_bot/config.py:318-326 pick_accounts(labels=None) trả MỌI profile enabled; dnse_api.py:149 `lp = loan_package_id or self.loan_package_id`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:559 — duplicate-formula (medium)
- Owner đề xuất: Taylor
- Công thức NAV §25 chép tay 3 nơi và đã lệch: DNSEBroker.get_nav() = (totalCash−totalDebt) + MV, KHÔNG cộng egg.totalValue lẫn manual_offbook, trong khi compute_active_nav.py:297 và daily_nav_snapshot.py:566 đều cộng egg + offbook (egg SpaceX ~100,2tr theo T19e selfcheck). Caller duy nhất trading_bot/strategies.py:391 dùng get_nav() làm account_nav để scale paper→real ⇒ scale thấp hơn NAV báo cáo đúng bằng phần egg. Đồng thời _cash_totalcash_minus_debt (line 538-557) tự viết lại guard feed-0 yếu hơn bộ 3 guard park_holdings (_stock_block_all_zero/_cash_fields_all_zero/_cash_fields_inconsistent) mà compute_active_nav.py:112 tái dùng — ca 'totalCash=0 < availableCash' (quant-skeptic vòng 3, T18p) lọt qua brokers nhưng bị compute_active_nav chặn.
- Bằng chứng: brokers.py:564-573 `cash = self._cash_totalcash_minus_debt() ... return cash + mv`; :555 chỉ `if tc == 0 and td == 0 and (av is None or av == 0)`; compute_active_nav.py:297 `total_nav = cash + total_mv + egg_value + offbook`; daily_nav_snapshot.py:566 `nav = mtm_stock + cash - debt + offbook + egg_value`; grep -rn '.get_nav(' → duy nhất trading_bot/strategies.py:391
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/eod_trading_report.sh:384 — shared-file-no-account-filter (medium)
- Owner đề xuất: Wags
- Đọc dnse_raw_{date}.jsonl (file dùng chung SpaceX+ZaloPay) với bộ lọc account CÓ ĐIỀU KIỆN: nếu không tra được _target_account_no (secrets lỗi/đổi schema — except: pass ở line 372-373) hoặc record thiếu account_no thì KHÔNG lọc gì, gộp order của cả 2 account vào real_filled_by_ticker ⇒ báo 'FILL THẬT ≠ STATE' giả hoặc che lệch thật. §12: thiếu account_no là dấu hiệu thiếu tham số, không phải lý do bỏ lọc — đúng file từng lọt sweep 2026-07-19.
- Bằng chứng: eod_trading_report.sh:372-373 `except Exception: pass`; :384 `if _target_account_no and rec.get('account_no') and rec.get('account_no') != _target_account_no: continue` (fail-open khi _target_account_no rỗng)
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/fetch_new_listings.py:64 — bare-datetime-now (medium)
- Owner đề xuất: Taylor
- date.today() không neo TZ (§16) ở 2 chỗ: cutoff lookback (line 64) và today_str ghi vào fetched_date + bus event (line 170). Cron 18:10 ICT hiện đúng nhờ crontab export TZ=Asia/Ho_Chi_Minh; chạy tay/worktree/systemd không có TZ ⇒ ngày lệch 1 (sau 17:00 UTC) — lớp lỗi đã bắt 5 ca 2026-08-30, AST gate chưa phủ date.today().
- Bằng chứng: fetch_new_listings.py:64 `cutoff = (date.today() - timedelta(days=lookback_days)).isoformat()`; :170 `today_str = date.today().isoformat()`; không import ZoneInfo/now_ict
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/fetch_new_listings.py:66 — correctness (medium)
- Owner đề xuất: Taylor
- Query 'new listing' GROUP BY (ticker, ICB_Code) rồi HAVING MIN(time) >= cutoff — một mã cũ bị ĐỔI mã ngành ICB (tái phân loại) sẽ tạo group mới với MIN(time) = ngày đổi ⇒ báo là mã mới niêm yết, đẩy vào research_queue + bus finding (chưa xác nhận bằng BQ vì MCP chưa auth; suy ra trực tiếp từ SQL).
- Bằng chứng: fetch_new_listings.py:66-70 `SELECT t.ticker, MIN(t.time) AS listing_date, t.ICB_Code FROM tav2_bq.ticker t GROUP BY t.ticker, t.ICB_Code HAVING MIN(t.time) >= "{cutoff}"`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh:1147 — correctness (medium)
- Owner đề xuất: Wags
- Sau bản vá 2026-09-12 neo WC_ROOT theo marker wc_env.sh (line 111-126) vẫn còn 2 chỗ dùng thẳng $ROOT/..: source wc_env.sh (1147) và preflight_bq_cache.py (1149). Dispatch phát từ worktree mike/agents/wt-*/bin/ ⇒ $ROOT/.. = mike/agents ⇒ không source được PATH google-cloud-sdk (bq CLI thiếu trong phiên con) và preflight luôn 'failed' ⇒ unset BQ_LOCAL_CACHE — đúng gốc sai mà comment 112-116 mô tả, chỉ vá một nửa.
- Bằng chứng: dispatch.sh:111 `WC_ROOT="$(cd "$ROOT/.." && pwd)"` + :117-126 probe marker; :1147 `[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh"`; :1149 `python3 "$ROOT/../preflight_bq_cache.py" --offline`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh:185 — bare-datetime-now (medium)
- Owner đề xuất: Wags
- `date -Iseconds` không có TZ='Asia/Ho_Chi_Minh' ở 2 dòng ghi log máy-đọc (dispatch_rejected_prompts.log line 185, notify_thread_errors.log line 1197) mà ops_health_check check #10/#10b đọc theo cửa sổ 24h — đúng mẫu §16 nêu đích danh (ca notify_thread.sh 2026-08-23); timestamp đổi múi giờ theo TZ tiến trình gọi (cron có TZ, phiên agent/worktree/systemd không chắc).
- Bằng chứng: dispatch.sh:185 `"$(date -Iseconds)" "$id" ...  >> "$_rejlog"`; :1197 `"$(date -Iseconds)" ... >> "$ROOT/logs/notify_thread_errors.log"`; so với :1634 đã dùng `TZ='Asia/Ho_Chi_Minh' date`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/kb_nightly.sh:308 — guideline:§5 (medium)
- Owner đề xuất: Wags
- Phase 1 ghi lại kb/events_buffer.md bằng write_text() không atomic, NGAY SAU khi đã append phần cũ vào archive (302-305): kill giữa write_text ⇒ buffer bị cắt cụt, mất to_keep (event <3 ngày, chưa nằm ở archive); kill giữa 2 bước ⇒ archive trùng đêm sau. Cùng file, Phase 1a (line 230-233) và 1b/1b2 (383-385, 472-475) đều đã tmp+os.replace — chỉ Phase 1 sót.
- Bằng chứng: kb_nightly.sh:302-305 `with archive_path.open('a') ... f.writelines(to_archive)`; :308 `knowledge_path.write_text(''.join(canonical + to_keep), encoding='utf-8')`; đối chiếu :230-233 `tmp = str(path) + '.tmp' ... os.replace(tmp, path)`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/due_diligence_corp_flags_selfcheck.py:79 — assert-on-live-state (medium)
- Owner đề xuất: Wags
- Fixture âm no_ex = ('FPT','ACB','MBB','VNM','HPG','VCB') trừ with_ex — nhưng with_ex chỉ lấy từ 50 dòng đầu theo ex-date (LIMIT 50) rồi lọc universe; comment nói 'cũng verify lại bằng query' nhưng KHÔNG có query nào. Mùa cổ tức, FPT/ACB có ex-date trong cửa sổ nhưng đứng ngoài top-50 ⇒ B1 đỏ oan; đây chính là lớp 'chập chờn theo ngày' mà comment 52-59 vừa mô tả cho nhánh A (§23 hệ luận 1).
- Bằng chứng: due_diligence_corp_flags_selfcheck.py:51 `ORDER BY exright_date LIMIT 50`; :78-79 `# ... (cũng verify lại bằng query)` / `no_ex = [t for t in ("FPT","ACB","MBB","VNM","HPG","VCB") if t not in with_ex]`; :131 `check(f"B1. {tk_noex}: upcoming_exdate is None", ...)`
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:1474 — correctness (low)
- Owner đề xuất: Taylor
- make_broker() nhánh live truyền loan_package_id= cho mọi BROKER_CLASSES nhưng PHSBroker.__init__ (line 301-302) không nhận tham số này ⇒ profile broker='phs' mode='live' sẽ TypeError ngay lúc tạo broker. Hiện latent (3 profile phs đều paper).
- Bằng chứng: brokers.py:301 `def __init__(self, account_id=None, otp=None, quote_only=False, credentials_file=None, label="main")`; :1474-1477 `BROKER_CLASSES[btype](..., loan_package_id=p.get("loan_package_id"))`; secrets: main/ab_cross/ab_dip broker=phs mode=paper

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:354 — simplification (low)
- Owner đề xuất: Taylor
- `time` đã import ở module (line 20) nhưng 6 method import lại cục bộ (`import time as _t/_time` ở 354, 377, 500, 784, 989, 1167); _validate_lever_package dùng `self.__dict__.setdefault('_lever_pkg_cache', {})` (900) dù __init__ đã khởi tạo (478). Không đổi hành vi, chỉ là code thừa trong hot-core.
- Bằng chứng: brokers.py:20 `import time`; grep -n 'import time as' → 354,377,500,784,989,1167; :478 `self._lever_pkg_cache = {}` vs :900

## /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav.py:269 — correctness (low)
- Owner đề xuất: Wags
- Account không có vị thế ⇒ in active_nav rồi `return` mà KHÔNG ghi active_nav_{account}.json ⇒ file cũ (nếu có) ở lại với computed_at cũ; consumer golive_recommend_v23._account_nav_basis chỉ hết hạn sau 5 ngày. Ca thật gần: RocketX mới mở (chưa vị thế) hoặc sau PARK bán sạch.
- Bằng chứng: compute_active_nav.py:269-273 `if not tickers: print(...); return` — trước khối ghi file :365-368

## /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav.py:171 — correctness (low)
- Owner đề xuất: Wags
- bq_close_prices lấy ngày = MAX(time) của mã ĐẦU TIÊN theo thứ tự alphabet cho TẤT CẢ mã; nếu mã đó bị ngừng giao dịch/thiếu dòng ngày mới nhất thì toàn bộ danh mục lấy giá ngày cũ hơn (fallback 'bq_close_stale' và nhánh --asof quá khứ).
- Bằng chứng: compute_active_nav.py:171-172 `AND t.time = (SELECT MAX(t2.time) FROM tav2_bq.ticker t2 WHERE t2.ticker = '{sorted(tickers)[0]}' AND {date_clause})`

## /home/trido/thanhdt/WorkingClaude/mike/bin/daily_nav_snapshot.py:510 — duplicate-formula (low)
- Owner đề xuất: Wags
- Guard 'block stock toàn 0' được viết inline trong main() (510-511) trong khi chính file đã có helper _stock_all_zero (172-175) dùng cho previous_balance; park_holdings._stock_block_all_zero là bản thứ 3 (compute_active_nav tái dùng). Sửa 1 nơi (vd loại bool/thêm field) thì 2 nơi kia lệch.
- Bằng chứng: daily_nav_snapshot.py:172-175 `def _stock_all_zero(stock): nums=[...]; return bool(nums) and not any(nums)`; :510-511 `numeric = [v for v in stock.values() if isinstance(v,(int,float)) and not isinstance(v,bool)]; if numeric and not any(numeric):`

## /home/trido/thanhdt/WorkingClaude/mike/bin/kb_nightly.sh:591 — dead-code (low)
- Owner đề xuất: Wags
- Khối `if git diff --quiet && git status --porcelain | grep -q .; then :; fi` không có tác dụng gì (thân là `:`), chạy 2 lệnh git mỗi đêm vô ích.
- Bằng chứng: kb_nightly.sh:591-593 `if git -C "$ROOT" diff --quiet && git -C "$ROOT" status --porcelain | grep -q .; then\n    :  # new untracked files\nfi`

## /home/trido/thanhdt/WorkingClaude/mike/bin/kb_nightly.sh:288 — correctness (low)
- Owner đề xuất: Wags
- Phase 1: dòng tiếp nối (payload nhiều dòng) sau event được gán theo `if to_archive and not to_keep` — tức chỉ đúng khi CHƯA có event nào giữ lại; khi buffer xen kẽ (block consolidation mới rồi cũ) thì dòng tiếp nối của event bị archive lại nằm ở to_keep ⇒ mồ côi vĩnh viễn trong events_buffer.md (comment nói 'attach to whichever bucket the last event went to' nhưng code không làm vậy).
- Bằng chứng: kb_nightly.sh:285-291 `if in_events: if to_archive and not to_keep: to_archive.append(line) else: to_keep.append(line)`

## /home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh:318 — dead-code (low)
- Owner đề xuất: Wags
- EFFORT_FLAG gán ở 318 nhưng không nơi nào dùng (_build_argv truyền `--effort "$EFFORT"` trực tiếp); MODEL_FLAG chưa bao giờ được gán nhưng vẫn export ở 1531 — sót từ bản `$MODEL_FLAG $EFFORT_FLAG` cũ chỉ còn trong comment 1020-1021.
- Bằng chứng: grep -n 'MODEL_FLAG\|EFFORT_FLAG' dispatch.sh → 318 (gán), 1020-1021 (comment), 1531 (export); _build_argv :1023-1024 dùng $MODEL/$EFFORT

## /home/trido/thanhdt/WorkingClaude/mike/bin/bus_question_closure_selfcheck.py:164 — correctness (low)
- Owner đề xuất: Wags
- Dòng kết `print("bus_question_closure_selfcheck: 17/17 PASS")` là số đếm tay, file hiện có 19 câu assert — trái nguyên tắc §16 'selfcheck tự đếm và tự in con số'; log/baseline weekly đọc dòng này sẽ thấy 17 dù thêm/bớt case.
- Bằng chứng: `grep -c '^\s*assert ' bus_question_closure_selfcheck.py` = 19; :164 `print("bus_question_closure_selfcheck: 17/17 PASS")`

## /home/trido/thanhdt/WorkingClaude/mike/bin/bus_question_audit.py:282 — correctness (low)
- Owner đề xuất: Wags
- Hợp đồng docstring 'exit code = số PENDING' sai khi >=256 (shell cắt mod 256: 256 pending ⇒ exit 0 = 'sạch'). Caller hiện tại đều dùng --json nên chưa cắn, nhưng docstring mời gọi dùng rc.
- Bằng chứng: bus_question_audit.py:17-18 docstring; :282 `return len(pending)`; :286 `sys.exit(main())`

## /home/trido/thanhdt/WorkingClaude/mike/bin/cron_health_check.py:148 — dead-code (low)
- Owner đề xuất: Wags
- Tham số since_ts của scan_errors() không được dùng (hàm dùng hằng RECENT_DAYS=10), caller truyền NOW-7d ⇒ 2 con số 7d/10d mâu thuẫn, người đọc tưởng cửa sổ 7 ngày.
- Bằng chứng: cron_health_check.py:148 `def scan_errors(path, since_ts):` — thân hàm không tham chiếu since_ts; :157 dùng RECENT_DAYS; :264 `scan_errors(p, NOW - 7 * 86400)`

## /home/trido/thanhdt/WorkingClaude/mike/bin/compute_park_trim_selfcheck.py:465 — correctness (low)
- Owner đề xuất: Wags
- T18q 'CHỨNG MINH NGƯỢC' chỉ kiểm số học thuần `close(1_000e6 - 0.80*(0.0 + 1_000e6), 200e6, 1)` — không gọi compute_trim hay guard nào ⇒ luôn PASS dù code bị revert; không chứng minh được điều nhãn nói (khác T18b/T18i có gọi hàm thật).
- Bằng chứng: compute_park_trim_selfcheck.py:465-467

## /home/trido/thanhdt/WorkingClaude/hit_details.py:18 — dead-code (low)
- Owner đề xuất: Taylor
- `json` import và `_ICT = ZoneInfo(...)` (line 22) không được dùng ở đâu trong file; BAL_COLS (37-39) chép tay y hệt indicator_monitor.py:35-37 với ghi chú 'keep in sync by hand' — không có phép kiểm cơ học nào cho cặp này (khác ta_terms đã có self-check với cột ta).
- Bằng chứng: grep -n 'json\.\|_ICT' hit_details.py → chỉ dòng định nghĩa :22; indicator_monitor.py:34 `# same column list as hit_details.py's BAL_COLS`

## /home/trido/thanhdt/WorkingClaude/indicator_monitor.py:84 — dead-code (low)
- Owner đề xuất: Taylor
- Biến `asof = None` gán rồi không dùng.
- Bằng chứng: grep -n asof indicator_monitor.py → duy nhất :84 `asof = None  # informational only`

## /home/trido/thanhdt/WorkingClaude/fetch_new_listings.py:162 — correctness (low)
- Owner đề xuất: Taylor
- append_event() chạy subprocess với capture_output nhưng không kiểm returncode/stdout ⇒ bus event (kể cả heartbeat 'count 0') mất im lặng nếu append_event.sh từ chối payload; và history dedupe (242) keep='last' theo (ticker, listing_date) ghi đè fetched_date cũ nên file KHÔNG phải 'append-only running log' như docstring line 6 nói.
- Bằng chứng: fetch_new_listings.py:162-166 `subprocess.run([...], capture_output=True, text=True)` không gán kết quả; :240-242 comment 'ticker + listing_date + fetched_date' nhưng `drop_duplicates(subset=["ticker","listing_date"], keep="last")`

## /home/trido/thanhdt/WorkingClaude/edge_health_monitor.py:98 — correctness (low)
- Owner đề xuất: Taylor
- capit_edge_health() nuốt mọi exception khi đọc bt_capitulation_STRONG.csv và trả None không in gì ⇒ dòng '⚔️ Capit edge ... max capit carve' biến mất khỏi edge_health_block.md mà không có cảnh báo (lag_edge_health cùng file thì có in '[lag-edge] skipped').
- Bằng chứng: edge_health_monitor.py:98-101 `try: ev = pd.read_csv(CAPF) except Exception: return None`; :382-383 `ce = capit_edge_health(); if ce:`

## File đã đọc kỹ, không có vấn đề (11)
- /home/trido/thanhdt/WorkingClaude/biodiversity_test.py
- /home/trido/thanhdt/WorkingClaude/fitness_matrix.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/backup_freshness_check.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/backup_freshness_check_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/backup_push_selfcheck.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/check_report_cadence.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/close_bus_question.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/commit_collision_gate_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/csv_fresh_today.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/hit_details_daily.sh