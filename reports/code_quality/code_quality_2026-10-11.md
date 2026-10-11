# Code quality weekly — 2026-10-11

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 1 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. + mike/bin/nav_unit_ledger.py [T0] (mới vào production, từ mike/bin/nav_period_returns.py)); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh)
Finding: 14 (từ 14 trước verify)

## /home/trido/thanhdt/WorkingClaude/mike/bin/dispatch.sh:1655 — correctness (medium)
- Owner đề xuất: Wags
- `_maybe_fallback_provider_on_usage_limit` được gọi trong `_bg_wrapper_run` (dòng 1566) nhưng KHÔNG có trong danh sách `export -f` (1655-1660). Ở chế độ --bg, wrapper chạy lại qua `bash -c '_bg_wrapper'` nên hàm này không tồn tại: `if` nhận rc=127 và rơi xuống `_maybe_schedule_usage_resume`. Hậu quả: job --bg của provider phụ (opencode/codex, đều enabled=true trong kb/cli_providers.json) khi hết usage/rate limit KHÔNG fallback ngay sang claude như user mandate 2026-08-03, mà bị xếp hàng resume mù ~5h trên chính provider đó (tối đa 3 lần). Lỗi 'command not found' không ai thấy vì `_detached_spawn` trỏ stderr vào /dev/null. Nhánh sync (dòng 1872) không bị ảnh hưởng.
- Bằng chứng: grep -n _maybe_fallback_provider_on_usage_limit bin/dispatch.sh → chỉ 607/622 (định nghĩa), 1566 và 1872 (gọi); dòng 1655-1660 `export -f _bg_wrapper _bg_wrapper_run ... _maybe_schedule_usage_resume _looks_like_usage_limit ... _new_session_id _record_job_telemetry` không có tên hàm này. Tái hiện cơ chế bằng bash thuần (không chạy dispatcher): `f(){ echo hi; }; g(){ if f; then echo IN; else echo rc=$?; fi; }; export -f g; bash -c g` → `environment: f: command not found` + `rc=127`. usage_limit_phrases.sh ghi rõ con `bash -c` chỉ thấy thứ đã export. Hàm thêm ở commit 0a990021.
- Hướng sửa đề xuất: Thêm `_maybe_fallback_provider_on_usage_limit` vào dòng `export -f` ở 1655-1660. Thêm 1 ca selfcheck --bg với provider stub không phải claude, khẳng định job record chuyển `status=provider_fallback`.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/capit_lever_selfcheck.py:348 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- A6/A7 (dòng ~340-349) và G1-G3 (~1404-1410) assert thẳng giá trị đang sống của `data/trading_rules.json`: `capit_margin_lever.enabled is True`, f=1.3, gói 1840, accounts=['SpaceX']. `enabled` chính là công tắc vận hành mà file này mô tả ở nhóm C19. Khi user tắt đòn bẩy (enabled=false), A7 và G1 đỏ dù code không đổi; đây là selfcheck thuộc phạm vi quét rộng của `trading_bot/plan.py` nên sẽ đỏ đúng lúc đang cần sửa code. (File 2376 dòng: đọc theo vùng, không đọc trọn.)
- Bằng chứng: Dòng ~348: `check("A7 …và đang BẬT (enabled=true) — user duyệt 2026-08-22", real_pol["enabled"] is True, ...)`; dòng ~1404: `check("G1 data/trading_rules.json :: capit_margin_lever.enabled == true (user 2026-08-22)", real_blk["enabled"] is True, ...)`. Comment ngay trên A7 tự ghi pin này đã phải đảo một lần: "Pin cũ `enabled is False` là trạng thái TRƯỚC quyết định đó — giữ nguyên thì selfcheck khoá hệ vào một quyết định đã bị thay thế".
- Hướng sửa đề xuất: Thay assert giá trị bằng assert bất biến: `enabled` là bool; khi enabled=true thì f/gói/accounts nằm trong hằng `CAPIT_LEVER_APPROVED_*` của trading_bot/plan.py và `live_requires_user_approval` là true. In trạng thái bật/tắt hiện tại như thông tin, không dùng làm điều kiện PASS.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/cctg_deposit_wiring_selfcheck.py:235 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- File đã cách ly CSV CCTG sống (dòng 46-52, sau 4 ngày selfcheck-red 10-05→10-09) nhưng chân Big-4 vẫn đọc `data/deposit_rate_vn_events.csv` sống qua `dep.current_deposit_rate()`. Dòng 235 pin `Big-4 == 6.8%` tại 2026-11-15; dòng 114 và 242 cần Big-4 < 7.5 (CCTG thắng); dòng 202-203 pin spread đúng 0.70pp. Chỉ cần lượt refresh Big-4 ghi một anchor khác 6.8 có ngày ≤ 2026-11-15 là dòng 235 đỏ dù logic wiring không đổi.
- Bằng chứng: Dòng 232-235: `BIG4_AT = dep.current_deposit_rate(STALE_DATE)` … `check("fixture sanity: Big-4-only at both fixture dates == 6.8%", abs(BIG4_AT - 6.8) < 1e-9)`. deposit_rate_vn.py:64,70-72 đọc `data/deposit_rate_vn_events.csv` (mtime Oct 3, dòng cuối `2026-10-03,6.8,...,web_crosscheck_auto`), không bị monkeypatch trong selfcheck này; chỉ `cctg._EVENTS_CSV` được trỏ sang thư mục tạm (dòng 52).
- Hướng sửa đề xuất: Cách ly chân Big-4 giống đã làm với CCTG: trỏ `dep._EVENTS_CSV` vào thư mục tạm rỗng (hoặc CSV fixture cố định) ngay sau dòng 52, để mọi số 6.8/7.5/0.70pp đến từ anchor đông cứng trong code.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/macro_state_live.py:305 — bare-datetime-now (medium)
- Owner đề xuất: Taylor
- `get_gated_state()` tính tuổi báo cáo health bằng `datetime.now()` trần trừ `h["ts"]`, mà `ts` do macro_healthcheck.py ghi cũng bằng `datetime.now()` trần (naive, không offset). Host là Etc/UTC, cron đặt TZ=Asia/Ho_Chi_Minh, nên writer và reader khác TZ sẽ lệch đúng 420 phút. Writer ICT + reader UTC: báo cáo 30h vẫn được coi là tươi (ngưỡng fail-closed 1440 phút thành ~1860). Writer UTC (chạy tay) + reader ICT: báo cáo 17h bị coi là quá hạn ⇒ rơi về DT4_only oan. Dòng 319 (`datetime.now().date()` cho `live_lag`) cùng lỗi.
- Bằng chứng: macro_state_live.py:305 `age_min = (datetime.now() - datetime.fromisoformat(h["ts"])).total_seconds() / 60.0`; :319 `live_lag = (datetime.now().date() - pd.Timestamp(end).date()).days`. macro_healthcheck.py:56 `NOW = datetime.now()`, :327 `"ts": NOW.isoformat(timespec="seconds")`. `cat /etc/timezone` → `Etc/UTC`; `crontab -l` dòng 2 `TZ=Asia/Ho_Chi_Minh`. kb/tz_anchor_baseline.json: `"macro_state_live.py": 2`, `"macro_healthcheck.py": 1` (nợ đã kiểm kê, chưa trả).
- Hướng sửa đề xuất: Reader: dùng `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` và gắn tzinfo ICT cho `ts` khi nó naive trước khi trừ. Writer: ghi `ts` bằng `datetime.now(ICT)`. Hạ baseline tz tương ứng.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/macro_healthcheck.py:56 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- `NOW = datetime.now()` và `TODAY = NOW.date()` theo TZ process. Chạy ngoài cron (TZ unset, host UTC) trong 00:00-07:00 ICT thì TODAY lùi 1 ngày: mọi tuổi nguồn (`tdays`, `sbv_age`, `verify_age_days`, `missed`) bị đếm thiếu 1, nên nguồn stale đúng ngưỡng vẫn qua. `ts` ghi ra cũng lệch 7h so với reader ICT (xem finding macro_state_live.py:305).
- Bằng chứng: Dòng 56-57: `NOW = datetime.now()` / `TODAY = NOW.date()`; dùng ở 70 (`ref: date = TODAY`), 102, 175, 187, 327. Host `Etc/UTC`. Baseline tz: `"macro_healthcheck.py": 1`.
- Hướng sửa đề xuất: `NOW = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`. Sửa cùng lượt với macro_state_live.py:305 để `ts` và phép trừ tuổi cùng một hệ.

## /home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py:129 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- `current_cctg_rate(asof=None)` lấy 'hôm nay' bằng `pd.Timestamp.today().normalize()` theo TZ process (gate AST §16 chưa phủ pd.Timestamp). Process UTC trong 00:00-07:00 ICT thì asof là hôm qua: anchor có effective_date = hôm nay (ICT) chưa được nhìn thấy, hàm trả lãi suất anchor trước cho effective_deposit_rate / kill-switch A.
- Bằng chứng: Dòng 129: `asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)`. deposit_rate_vn.py:195,280,306 có cùng mẫu (ngoài danh sách tuần này).
- Hướng sửa đề xuất: Dùng `pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").normalize().tz_localize(None)` cho nhánh asof=None.

## /home/trido/thanhdt/WorkingClaude/freshness_ops_selfcheck.py:207 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- `_write_dt5g_evidence` ghi `as_of` bằng `datetime.now().date()` theo TZ host, trong khi script được test (bq_freshness_check.sh:52) ép `export TZ=Asia/Ho_Chi_Minh` vô điều kiện và so `as_of` với phiên gần nhất theo ICT. Chạy selfcheck với TZ unset (host UTC) trong 00:00-07:00 ICT thứ 3-7: `as_of` = hôm qua ≠ LAST_TRADING_DAY ⇒ S1 đỏ giả. Dòng 198 và 220 cùng mẫu.
- Bằng chứng: Dòng 207: `d = datetime.now().date()`; 198: `json.dumps({"checked_at": datetime.now().isoformat()})`. bq_freshness_check.sh:47-52 `export TZ=Asia/Ho_Chi_Minh` (comment ghi finding code-quality 2026-09-20 đã sửa phía script); :456 `as_of=... ≠ phiên gần nhất $LAST_TRADING_DAY`. Baseline tz: `"freshness_ops_selfcheck.py": 3`.
- Hướng sửa đề xuất: Dùng `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` ở cả 3 chỗ, rồi chạy lại dưới `env -u TZ` và một TZ ngoại lai theo skill verify-before-done.

## /home/trido/thanhdt/WorkingClaude/append_cctg_rate.py:182 — correctness (low)
- Owner đề xuất: Taylor
- `--force` được mô tả là 'append even if effective_date exists' nhưng không bao giờ ghi đè được: bước idempotent (168) bỏ qua SKIP khi có --force, rồi guard 'not newer than last anchor' (182) luôn chặn, vì ngày đã tồn tại thì luôn ≤ last_date (last_date tính từ chính các dòng CSV). Khối xoá dòng cũ ở 264-265 vì vậy không bao giờ có tác dụng. Người muốn đính chính một anchor gõ sai bằng --force nhận 'ERROR: not newer' và phải sửa CSV tay.
- Bằng chứng: Dòng 168 `if args.effective in existing and not args.force: ... return 0`; 178-182 `last_date = max(...rows...)` / `existing_ev["time"].max()` rồi `if eff <= last_date: sys.exit("ERROR: --effective ... is not newer ...")` không xét `args.force`; 264-265 `if args.force: rows = [r for r in rows if r["effective_date"] != args.effective]`. grep `--force` trong các selfcheck CCTG chỉ thấy ca 'bị từ chối khi có JOB_ID', không có ca --force ghi đè thành công.
- Hướng sửa đề xuất: Chọn một hướng và làm help khớp code: (a) cho --force đi qua guard khi `args.effective in existing` (chỉ chặn khi ngày nhỏ hơn anchor đông cứng trong code), hoặc (b) bỏ nhánh 264-265 và sửa help thành 'chỉ override delta guard'.

## /home/trido/thanhdt/WorkingClaude/deposit_cctg_trend_check.py:145 — correctness (low)
- Owner đề xuất: Taylor
- Cảnh báo staleness de-dup theo `last_date`: lần đầu bắn ở tuổi 35 ngày ('SẮP STALE, còn 10d') rồi ghi `staleness_warned_for_date`. Khi cùng anchor đó thật sự vượt 45 ngày, `already == last_date` nên bỏ qua: nhánh '⚠️ DỮ LIỆU ĐÃ STALE' (273-279) chỉ chạy được nếu lần cảnh báo đầu rơi sau ngày 45. Vận hành bình thường user chỉ nhận 1 tin báo trước, không có tin nào lúc CCTG overlay thật sự bị loại khỏi effective rate.
- Bằng chứng: Dòng 143-147: `if age < (STALE_DAYS_LIMIT - STALE_WARN_BEFORE_DAYS): continue` / `already = state.get(key, {}).get("staleness_warned_for_date")` / `if already == last_date: continue`; dòng 290-291 ghi state ngay khi gửi được tin đầu; dòng 273-279 là nhánh `days_to_stale < 0` với icon riêng.
- Hướng sửa đề xuất: Lưu thêm pha đã cảnh báo (vd `staleness_warned_phase: pre|stale`) cùng `last_date`, cho phép bắn thêm đúng 1 lần khi chuyển từ pre sang stale.

## /home/trido/thanhdt/WorkingClaude/dna_report.py:90 — perf (low)
- Owner đề xuất: Taylor
- `get_capitulation()` quét toàn bộ lịch sử `tav2_bq.ticker_prune` (GROUP BY p.time, không có điều kiện thời gian) rồi mới `ORDER BY ... DESC LIMIT 120`. Bảng partition theo `time` nên mỗi lần cache hết hạn (TTL 5 phút, gọi từ `build_report` mỗi tin nhắn bot và `build_market_alert`) là một lần đọc mọi partition từ 2000 để dùng 120 phiên cuối.
- Bằng chứng: Dòng 90-95: `WITH daily AS (SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold FROM tav2_bq.ticker_prune p WHERE p.Close_T1>0 GROUP BY p.time) ... ORDER BY d.time DESC LIMIT 120`. Cùng file, `get_compass()` dòng 131 đã lọc `t.time>=DATE_SUB(CURRENT_DATE(),INTERVAL 130 DAY)`. CLAUDE.md: `ticker_prune` part `time` / cluster `ticker`.
- Hướng sửa đề xuất: Thêm `AND p.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 200 DAY)` vào CTE `daily` (200 ngày lịch đủ cho 120 phiên mà logic grind 20-90 phiên cần).

## /home/trido/thanhdt/WorkingClaude/dna_report.py:246 — duplicate-formula (low)
- Owner đề xuất: Taylor
- Dòng 'Gate DT5G' trong báo cáo (kể cả khối §6b weekly/monthly) replay gate bằng bản chép `dt_4gate` trong `mike/agents/Taylor/dt_gate_hazard_research.py`, không phải hàm production `macro_state_live._dt_4gate`. Hai định nghĩa cùng chữ ký sống độc lập (thêm bản thứ ba ở pt_v12_dt4.py): nếu logic/tham số ở macro_state_live đổi mà bản chép không đổi, đồng hồ candidate k/need trong báo cáo lệch state production mà không có gì kêu.
- Bằng chứng: dna_report.py:246 `from dt_gate_hazard_research import extract_episodes, dt_4gate`. `grep -rnE "^\s*def _?dt_4gate\b"` → macro_state_live.py:104 `def _dt_4gate(states, default=10, enC=25, exC=10, enX=25, exX=10)`; mike/agents/Taylor/dt_gate_hazard_research.py:26 `def dt_4gate(states, default=10, enC=25, exC=10, enX=25, exX=10)`; pt_v12_dt4.py:117.
- Hướng sửa đề xuất: Cho dt_gate_hazard_research.py import `_dt_4gate` từ macro_state_live làm `dt_4gate` thay vì giữ bản chép; `extract_episodes` giữ nguyên.

## /home/trido/thanhdt/WorkingClaude/lag_governance_order_gate_selfcheck.py:83 — assert-on-live-state (low)
- Owner đề xuất: Taylor
- Phần unit chạy với deps thật, đọc `data/forensic_flags.csv` sống (chdir WORKDIR dòng 22-23): assert BFC bị chặn kind='forensic' (83-85) và POW 'mã sạch' không bị chặn (86-87). Đây là assert lên rổ mã của file dữ liệu production: cờ BFC bị gỡ/đổi severity hoặc POW nhận cờ exclude là selfcheck đỏ dù `filter_lag_governance_orders` không đổi.
- Bằng chứng: Dòng 83-87: `pl, blk = run([("BFC", "LAG", "buy")])` / `check("cờ forensic exclude (BFC) bị chặn ở tầng lệnh", len(pl.orders) == 0 and blk[0]["kind"] == "forensic")` / `check("mã sạch (POW) KHÔNG bị chặn", ...)`. lag_forensic_filter.py:93 `FORENSIC_CSV = "data/forensic_flags.csv"`, :118 `ff = pd.read_csv(csv_path)`. File đã có mẫu tiêm `csv_path` ở `_no_csv_deps` (137-143).
- Hướng sửa đề xuất: Ở mục 2, bọc deps giống `_no_csv_deps` nhưng trỏ `csv_path` tới CSV fixture tạm (1 dòng exclude cho mã giả, không có POW) để kiểm quan hệ 'có cờ ⇒ chặn / không cờ ⇒ giữ' thay vì tên mã đang sống.

## /home/trido/thanhdt/WorkingClaude/cpi_vn_tier15_selfcheck.py:225 — assert-on-live-state (low)
- Owner đề xuất: Taylor
- `test_regime` assert số đếm đúng tuyệt đối trên `data/macro_features.csv` đang nằm trong cây: 185 tháng, đúng 27 tháng REG_C và 17 tháng REG_B đổi nhãn; `test_dcf` assert đủ 7 mã định giá được tại 2026-09-26 qua dữ liệu sống. Hiện xanh chỉ vì macro_features.csv đứng im từ tháng 5; file được regenerate/kéo dài thêm 1 tháng là `len(Co) == 185` đỏ dù wire Tier 1.5 không đổi.
- Bằng chứng: Dòng 225-227: `ok(len(Co) == 185, ...)`, `ok(len(chC) == 27, ...)`, `ok(len(chB) == 17, ...)`; dòng 277 `ok(len(priced) == 7, ...)`. `ls -la data/macro_features.csv` → mtime May 19; đo thật: time 2011-01-04 → 2026-05-15, đúng 185 tháng.
- Hướng sửa đề xuất: Cắt `mf` về cửa sổ cố định của finding (`mf[mf.time <= "2026-05-15"]`) trước khi đếm, hoặc đọc bản đông cứng trong thư mục research REF; các số 185/27/17 khi đó là hằng của fixture.

## /home/trido/thanhdt/WorkingClaude/mike/bin/adjfactor_drift_detect_selfcheck.py:343 — assert-on-live-state (low)
- Owner đề xuất: Wags
- Assertion 'nhánh này KHÔNG chạm report_return_gate.py / dividend_adjusted_return.py' so `git diff merge-base(HEAD, master)..HEAD` và `git status --porcelain` của working tree. Trên master (nơi nó chạy sau merge) nửa commit luôn rỗng nên không còn chứng minh gì, còn nửa working-tree làm selfcheck đỏ mỗi khi có ai đang sửa dở 2 file đó vì việc không liên quan Layer 1. Cả hai file đang được phát triển tích cực. (File 2892 dòng: đọc theo vùng, không đọc trọn.)
- Bằng chứng: Dòng 343-351: `base = subprocess.run(["git", "-C", root, "merge-base", "HEAD", "master"], ...)` … `working = subprocess.run(["git", "-C", root, "status", "--porcelain", "--", *paths], ...)` … `ck("nhánh này KHÔNG chạm ...", committed == "" and working == "", ...)`. `git rev-parse --abbrev-ref HEAD` → master; `git log --oneline -3 -- bin/report_return_gate.py bin/dividend_adjusted_return.py` → 7812f586, 53b48b76, 318097fa.
- Hướng sửa đề xuất: Thay bằng bất biến tĩnh trên chính detector (đã có ở assertion kế tiếp: chỉ đọc `dar.ACCOUNTS`/`dar.broker_qty`), hoặc so với cặp commit đông cứng của bản wire Layer 1 như cách các selfcheck khác được sửa trong đợt selfcheck-red 2026-10-09.

## File đã đọc kỹ, không có vấn đề (13)
- /home/trido/thanhdt/WorkingClaude/atc_cancel_overorder_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/basket_return_leg_oshares_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/bot_execute.py
- /home/trido/thanhdt/WorkingClaude/capit_episode.py
- /home/trido/thanhdt/WorkingClaude/cctg6m_series_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/cq_hard_boundary_20261004_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/custom30_history.py
- /home/trido/thanhdt/WorkingClaude/custom30_publish_guard.py
- /home/trido/thanhdt/WorkingClaude/custom30_publish_guard_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/account_cash_flows.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/adjfactor_drift_alert.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/adjfactor_drift_daily.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/adjfactor_drift_detect.py