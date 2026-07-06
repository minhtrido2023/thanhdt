# Mike fleet — context pack (v749)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-06T04:09:58] Taylor/finding — sector#19 SOE-governance archetype — LENS-NOT-BOOK, NOT-A-GATE (cross-cutting governance note like 5F moat). State ownership is a MILD RETURN DRAG (state% IC -0.034; SOE fwd T+60 3.16% vs priv 4.25%; SOE-broad basket 9.45% vs identical-sector private-peer 14.50% ~-5pp/yr). NO governance discount to buy — flagships trade a PREMIUM (SOE/priv PB power 1.02x/banks 1.33x/insurance 2.12x). DY on an SOE = a POLICY variable not FCF, bifurcated (cash-cows GAS/VEA pay up vs state banks forced to RETAIN for CAR); the high-DY yield play is a documented INCOME TRAP (cash-cow price-CAGR 4.53% + ~4.5pp div = ~9.0% total-return STILL lags B&H 10.23%, -58% DD). Thin float is the one measurable signature: turnover vs state% Spearman -0.51, SOE median turnover 0.18 vs priv 0.44 (high-lock flagships ACV/GAS/VCB/VEA/BID starved; POW/NT2/PLX/VNM liquid exceptions). Do NOT wire; production untouched.: {"job": "Taylor_20260706_040038", "dispatch_from": "Mike", "scope": "RESEARCH-ONLY, new files only (soe_governance_screen.py + soe_governance_framework.md + dat …
- [2026-07-06T04:39:36] Taylor/finding — sector#20 holding-company/conglomerate SOTP archetype — LENS-NOT-BOOK, valuation METHOD not a gate. A blended P/E/P/B on a conglomerate is meaningless (VIC PB 11.3 with once-NEGATIVE NPM = VinFast option value, not property); value the parts. coverage=ParentMC/Σ(stake×listed-sub MC) gives a clean split: MSN 0.70×/GEX 0.77× DISCOUNT (real holdco leverage 1.8-6.7 + complexity) vs VIC 4.07×/GVR 14.8× PREMIUM (unlisted optionality — VinFast, landbank; GVR listed rubber subs only ~7% of cap). KEY: discount does NOT mean-revert — deep discount is a TRAP: pooled coverage-z IC +0.073/+0.054/+0.036 WRONG-SIGNED (premium-momentum not reversion), discount-tilt basket LOSES -8.1pp Full DD -57.6%, series trend/de-rate (MSN/GEX trend-t -0.68/-0.62). Any EW-all edge (+1.4pp) is 100% OOS-luck (IS -19.1pp/OOS +16.2pp = VIC+GVR run-up). Premium=optionality that deflates in CRISIS (GVR 14.7×→7.2×). DO NOT WIRE. Production untouched.: {"job": "Taylor_20260706_042831", "dispatch_from": "Mike", "scope": "RESEARCH-ONLY new files only (holdco_sotp_screen.py + holdco_sotp_valuation_framework.md +  …
- [2026-07-06T05:13:14] Taylor/finding — 20-sector consolidated classification + harvesting-workflow proposal — Section 0 & 7 added to sector_watchlist_framework.md (RESEARCH/SYNTHESIS, no code, production untouched): {"job": "Taylor_20260706_050653", "dispatch_from": "Mike", "scope": "Triage all 20 sector/archetype frameworks into A/B/C + design a harvesting workflow (propos …
- [2026-07-06T05:50:41] Taylor/finding — technical-stabilization filter on WATCH — REFUTED as return filter, only trims deep-DD tail (insurance not alpha); keep WATCH->BUY on fundamentals: {"job": "Taylor_20260706_054234", "dispatch_from": "Mike", "scope": "RESEARCH-ONLY, new file technical_stabilization_test.py + registry pin; production untouche …
- [2026-07-06T06:38:39] Taylor/finding — sector_lens_monitor.py built — Group-A 6-state weekly watchlist monitor (Section 7): {"job": "Taylor_20260706_062405", "dispatch_from": "Mike", "scope": "RESEARCH/MONITOR-ONLY, production untouched (custom30V/BAL/LAG/rating_8l.py unchanged). New …
- [2026-07-06T06:47:16] Taylor/finding — sector_lens_monitor.py built — weekly 6-state Group-A watchlist monitor: {"job": "Taylor_20260706_062405", "dispatch_from": "Mike", "scope": "Built Section-7 Harvesting-Workflow tool (user-approved). RESEARCH/MONITOR-ONLY, production …
- [2026-07-06T07:13:39] Taylor/finding — STRONG-tier (screaming-buy) calibration for Group-A sector lenses — 3 ADD / 3 NO-STRONG-by-design: {"job": "Taylor_20260706_070219", "dispatch_from": "Mike", "scope": "RESEARCH-ONLY backtest to define STRONG lines; new file sector_strong_threshold.py; code ch …
- [2026-07-06T07:31:25] quant-skeptic/verification — ✅ CONFIRMED VERIFY: STRONG-tier (screaming-buy) calibration for Group-A sector lenses — 3 ADD / 3 NO-STRONG-by-design: {"finding_topic": "STRONG-tier (screaming-buy) calibration for Group-A sector lenses — 3 ADD / 3 NO-STRONG-by-design", "verdict": "CONFIRMED", "confidence": "hi …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-03

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01. 23 vị thế, hiện 141.4% NAV (do sự cố double-buy
  07-02, chưa unwind). run_bot.sh 09:05 ICT mỗi T2-T6. ⚠️ **Đang có nợ margin THẬT ~409,86tr VND** (xác
  nhận qua ảnh chụp app DNSE thật 03/07 19:37 — không phải chỉ T+2 float như ghi nhận ban đầu 02/07
  09:46; xem `kb/INCIDENTS.md` entry 2026-07-03 "Real margin debt went unreported").
  **Đã duyệt (2026-07-03, event Mike/decision `plan-07-06-v2-trim-70pct`): trim GỘP về đúng 70% NEUTRAL
  target** (không chỉ khôi phục 1x như plan v1 cũ) — `data/trade_plans/plan_SpaceX_2026-07-06_v2.json`,
  bán tổng ~710M VND (71.8% NAV) trong 1 phiên 07-06 09:00-10:30, Mafee đã authorized, không cần duyệt
  lại. Sau thực thi kỳ vọng: exposure 141.4%→69.6%, dọn sạch 8 mã basket drift (LPB/MSB/VHC/HAH/VIB/
  VGC/DCM/MBS), margin debt→0 sau T+2 settle 07-08. **Lý do 70% (không phải 93.8-94.7% go-live gốc):**
  DollarBill từng tự đặt target_equity_pct=93.8% lúc go-live KHÔNG qua backtest — user chất vấn trực
  tiếp, Taylor backtest full 2-book NAV thật xác nhận 70% thắng tuyệt đối mọi metric risk-adjusted
  (Sharpe 1.78 vs 1.66, Calmar 1.63 vs 1.49, DD -16.5% vs -18.8%, job `Taylor_20260703_130720`, quant-
  skeptic CONFIRMED). Đã chính thức hoá thành `trading_rules.json` v2.1 section `neutral_parking`
  (default 0.70 của phần idle cash khi BAL/LAG rỗng, KHÔNG phải trần tổng cổ phiếu — khi 2 book có deal
  thật tổng cổ phiếu có thể vượt xa 70%, đúng thiết kế) + cơ chế `risk_dial_override` (muốn park≠0.70
  bắt buộc field `risk_dial_confirmed_by_user`+`risk_dial_warning_acknowledged`, thiếu 1 trong 2 →
  Mafee tự block plan).
  **Cập nhật 2026-07-06 08:5x ICT (trước giờ mở cửa):** phát hiện `plan_SpaceX_2026-07-06.json`
  (tên file executor thật sự đọc) vẫn là bản v1 cũ (11 lệnh, 94.7%) — v2 (23 lệnh, 70%, bản đã
  duyệt) nằm ở tên file `_v2` mà `trading_bot/plan.py` KHÔNG hề nhận diện. Nếu không phát hiện,
  09:05 sẽ chạy nhầm v1. Đã sửa (user duyệt): đổi tên v1→`..._v1_superseded_11name.json` (giữ audit),
  copy v2 đè vào tên file chính thức — xác nhận qua preflight 08:58 ICT: "23 lệnh, ~0.710B VND,
  approved=user" đúng như kỳ vọng. Tiện thể vá 2 lỗi hiển thị trong `preflight_check.sh` (field
  `approved_by`/`mafee_authorized` thiếu ở plan gốc gây báo NOT_APPROVED giả; field `est_value_vnd`
  vs `est_value` sai tên gây hiển thị `0.000B` giả). Chi tiết đầy đủ: `kb/INCIDENTS.md` 2026-07-06.
  **Cập nhật 2026-07-06 giữa phiên sáng:** phát hiện bot lặp ~2000 lần `HTTP 400: Trade quantity
  not enough` từ 09:12 ICT trên đúng 11 mã mua 02/07 (chưa qua T+2 — DNSE chỉ nhả sellable từ
  **phiên chiều** của ngày T+2, không phải từ đầu phiên sáng). Đã vá `trading_bot/executor.py`
  (commit `2cee603`): `step()` gọi `get_positions()` 1 lần/chu kỳ, cap qty bán theo `sellable`
  thật hoặc bỏ qua (`WAIT_T2_SETTLEMENT`) thay vì để broker tự từ chối. Fix này CHỈ có hiệu lực
  từ lần restart tự nhiên tiếp theo (nghỉ trưa 11:30 → resume 13:00), không restart tay giữa
  chừng. Cũng commit luôn fix `trading_bot/plan.py` (id/ref_price normalize cho schema v2, commit
  `7a2a145`) đã hotfix trên đĩa từ sáng nhưng chưa commit. Chi tiết: `kb/INCIDENTS.md` 2026-07-06
  (entry thứ 2 cùng ngày).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

## Đang R&D
- **Taylor · EXTREME-regime gate PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `extreme_regime_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`); global default + SpaceX/live GIỮ `False`. Week-1 stress-injection PASS 24/24 (`stress_extreme_regime.py`: arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls). **Target kết thúc ~2026-07-28 (~20 phiên).** 3 điều kiện còn lại trước LIVE: (a) ZERO false-trigger qua ~4 tuần benign, (b) không can thiệp NORMAL-path, (c) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor · vol-scale buy chase-cap (patch#3) PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `chase_cap_vol_scale_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`, k=2.0/ceil=0.04); global default + SpaceX/live GIỮ `False`. Executor-path stress PASS 15/15 (`stress_vol_scale_chase_cap.py`: wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · paper limit > static + NEG-control live→static). **Target kết thúc ~2026-07-14 (~10 phiên — ngắn hơn EXTREME vì fire trên gap-up thường, tích event nhanh).** Điều kiện trước LIVE: (a) paper sạch (wiring đúng trên quote thật + fail-safe khi thiếu rvol cache), (b) không can thiệp NORMAL-path ngày non-gap, (c) skeptic rerun REAL-fill vs `min(open,L)` proxy trên correlated gap-up @NAV target, (d) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor**: sector sweep #10+ (chờ Mike dispatch)
- **Taylor · fill-timing khung giờ (BUY 10:45-11:15 / SELL 09:15-09:45)**: ĐÃ xử lý xong 2026-07-02 (job Taylor_20260702_031608, note cũ ở dòng này lỗi thời). Edge THẬT & IS/OOS-stable (BUY tại 11:15 rẻ hơn open +17.6bps/lệnh, t=12.0; SELL tại open đúng, +11.8bps vs ATC) nhưng **KHÔNG flip `fill_timing_live_gate` ngay** — cần paper tích lũy ~3-4 tuần fill (từ go-live 2026-07-01, mới ~3-4 phiên) để `execution_quality_review.py` xác nhận NET-of-noise capture (noise 110-220bps >> edge 17bps) → quant-skeptic → user sign-off mới flip. Checkpoint tự nhiên: ~cuối tháng 7.
- **V2.5**: R&D-complete, DISABLED. Reminder: 2026-07-07 Mike hỏi user go-ahead integration.

## Chờ user quyết định
- V2.5 live-recommend integration: **2026-07-07** (trigger tự động)

## Reliability hardening (2026-07-02, theo yêu cầu user — 4 việc AgentOps)
Đã triển khai đủ 4 mục theo thứ tự ưu tiên, chi tiết + self-check trong `kb/INCIDENTS.md` và
`MIKE.md` §Quy chuẩn bắt buộc:
1. **Circuit breaker** per-agent trong `dispatch.sh` (`state/circuit/<id>.json`).
2. **Idempotency guard** (`Executor._ghost_tickers`, `trading_bot/executor.py`) — lớp phòng thủ
   THỨ HAI cho double-buy, đóng residual gap quant-skeptic tìm thấy sau flock fix (503aa2f).
   quant-skeptic CONFIRMED (verify_finding.sh 2026-07-02T13:48). Review vòng 2 (bên thứ ba, xem
   dưới) thêm 2 fix nữa. **Đã commit** repo WorkingClaude/thanhdt commit `e1d9b7c` (user duyệt
   2026-07-02T15:30).
3. **trace_id** trong bus event (`append_event.sh`, fallback tự động qua `$JOB_ID`).
4. **`kb/INCIDENTS.md`** — backfill 5 sự cố đã biết (double-buy, job chết theo session, callback
   ping-pong, Mafee zombie, go-live day-1 5 bugs).

**Review vòng 2 (2026-07-02, bên thứ ba độc lập)** — verify lại cơ chế bằng dữ liệu DNSE thật
(6.338 lệnh `dnse_raw_2026-07-02.jsonl`), xác nhận cơ chế đúng, tìm thêm 2 gap không-chặn +
1 note vận hành, cả 3 đã fix/ghi ngay trong lượt: (a) `_save_state()` không atomic → giờ
tmp+`os.replace()`; (b) `PaperBroker.poll_orders()` trả `raw=None` → guard là no-op trên paper,
giờ trả `raw={"symbol":...}` giống broker thật, paper trading diễn tập được; (c) không có quy
trình "unpause" chính thức — đã ghi rõ trong docstring `_ghost_tickers()` (executor.py) + KB
(chấp nhận theo thiết kế: unpause thủ công, không auto-reconcile). `ghost_order_selfcheck.py`
giờ 12/12 (thêm I/J cho 2 fix trên, verify catch-regression bằng cách revert-tạm rồi phục hồi).
**Đã commit** cùng lần với vòng 1 — commit `e1d9b7c` gộp cả 2 vòng review.

## Usage-limit auto-resume (2026-07-03, theo yêu cầu user)
User gặp vấn đề: task tự động research bị dừng giữa chừng khi tài khoản hết usage limit 5h
(`bin/usage_watch.py`), phải tự quay lại nhắc "tiếp tục". Đã tự động hóa cho **mọi agent qua
`dispatch.sh`** (không riêng agent nào — Taylor/DollarBill/Mafee/... đều được):
- `dispatch.sh` phát hiện dispatch fail vì usage-limit (log khớp cụm từ HOẶC
  `usage_watch.py` PCT≥95%) → KHÔNG coi là fail thật (không trip circuit breaker) → ghi
  `bus/pending_resumes/<job_id>.json` (resume_at = reset-time ước tính + buffer 10').
- **`bin/resume_pending.py`** (cron mới, `*/10 * * * *`) tự fire record đến hạn, dispatch lại
  đúng agent với prompt "đọc working memory, tiếp tục — đừng làm lại từ đầu".
- Chặn lặp vô hạn: tối đa 3 lần auto-resume liên tiếp (`DISPATCH_MAX_USAGE_RESUMES`), quá trần
  → rơi về xử lý fail thật (có trip circuit breaker) — phòng trường hợp đây là bug thật chứ
  không phải usage limit thật.
- Test end-to-end đầy đủ (fake usage-limit CLI, sync + `--bg`, cap boundary n=2/n=3, resume
  chain thật qua `resume_pending.py`) — tất cả đúng như thiết kế.
- **Giới hạn đã biết:** chỉ cứu headless dispatch, KHÔNG cứu được phiên tương tác trực tiếp
  của chính Mike (nếu turn hiện tại của Mike bị rate-limit thì turn đó chết hẳn, không tự
  lên lịch resume chính nó được). Chi tiết: `MIKE.md` §Quy chuẩn bắt buộc mục 6.

## Workflow ngày trading (SpaceX, T2-T6, giờ ICT)
1. **17:30** — `bq_freshness_check.sh`: BQ fresh → dispatch DollarBill lập plan T+1
2. **19:30** — `send_plan_report.sh`: gửi plan T+1 vào Trading Daily thread (duyệt trước 08:45 sáng mai)
3. **08:20** — `ops_health_check.sh --label "Trước phiên sáng"` (thêm 2026-07-06, theo yêu cầu user) —
   kiểm tra vận hành tự động TRƯỚC preflight: xung đột file plan (bài học sự cố 07-06), lỗi lặp lại
   bất thường trong journal (loại trừ WAIT_T2_SETTLEMENT/mẫu T+2 đã biết), circuit breaker, câu hỏi
   (question) chưa trả lời trong 48h — post tóm tắt vào **Trading Daily** (vận hành sống, không phải
   Trading report). Script: `bin/ops_health_check.sh`.
4. **08:45** — `preflight_check.sh`: kiểm tra sẵn sàng trước giờ mở cửa (GREEN/RED)
5. **09:05** — `run_bot.sh --auto-otp`: thực thi plan (phiên sáng)
6. **09:00-14:55** — `bot_heartbeat.sh` mỗi 5': giám sát liveness + digest fill mới
7. **11:30** — dừng bot giờ nghỉ trưa (`pkill -f "[b]ot_execute.py --account SpaceX"`, sửa 2026-07-06
   tối — pattern cũ tự khớp luôn dòng lệnh gọi chính nó qua `sh -c`, xem `kb/INCIDENTS.md`; vô hại
   vì `session_phase()` đã tự idle đúng qua trưa dù pkill không hiệu quả, nhưng vẫn cần fix cho đúng)
8. **12:45** — `ops_health_check.sh --label "Trước phiên chiều"` (thêm 2026-07-06) — kiểm tra lại toàn
   bộ khâu vận hành sau phiên sáng, trước khi resume phiên chiều — cùng nội dung kiểm tra như bước 3,
   chạy lại để bắt vấn đề phát sinh trong phiên sáng trước khi vào phiên chiều.
9. **13:00** — `run_bot.sh --auto-otp`: resume phiên chiều
10. **~14:50** — phiên đóng (ATC), bot tự cancel lệnh treo, ghi `exec_*_report.md`
11. **15:00** — `eod_trading_report.sh`: **báo cáo tổng kết EOD** (thêm 2026-07-01) — đọc `state.json`
   (giá khớp thực từng lệnh), tính tổng lệnh/mua-bán/khớp đủ-một phần-chưa khớp/tổng giá trị VND,
   post vào **Trading report topic** (đổi từ Trading Daily 2026-07-03, xem dưới). **Thêm 2026-07-03**:
   gọi `bin/daily_nav_snapshot.py` để in kèm NAV thật cuối ngày + biến động so hôm trước (MTM cổ phiếu
   từ BQ, cash/nợ margin từ balances API thật) — ghi vào `data/execution_logs/nav_history_SpaceX.csv`,
   nguồn duy nhất mọi báo cáo ngày/tuần/tháng dùng chung. Xem `kb/coding_guidelines.md` §6 "Standing
   pipeline" cho quy trình xác minh bắt buộc + phân biệt độ sâu nội dung theo từng loại báo cáo.

**3 Discord topic tách biệt (cập nhật 2026-07-03 — thêm Trading report):**
- **Trading Daily (1521470705563340910)** — nội dung VẬN HÀNH SỐNG trong ngày: preflight, run_bot,
  heartbeat, BQ freshness, `ops_health_check.sh` (08:20 + 12:45, thêm 2026-07-06). (EOD report đã
  CHUYỂN sang Trading report — xem dưới.)
- **DollarBill plan channel (1521183164364754974)** — riêng cho việc LẬP KẾ HOẠCH của DollarBill
  (`send_plan_report.sh`, và mọi `dispatch.sh DollarBill ...` khác dù cron hay ad-hoc). Root cause
  thread-leak (dispatch notify theo thread Mike đang active) đã fix ở tầng `dispatch.sh` qua hàm
  `_agent_thread_override` — route CỐ ĐỊNH cho DollarBill bất kể Mike gọi từ topic nào.
- **Trading report (1522576692638388364, thêm 2026-07-03, user chỉ đạo)** — kênh DUY NHẤT cho
  **báo cáo tổng hợp** trading ngày/tuần/tháng (khác với alert vận hành sống ở Trading Daily). Đã
  chuyển đích `eod_trading_report.sh` (báo cáo EOD + cảnh báo đối soát mismatch) sang topic này.
  Báo cáo tuần/tháng (khi Mike tự soạn thủ công theo yêu cầu user, vd báo cáo tuần go-live SpaceX
  2026-07-03) cũng đích đến topic này. User cũng dùng topic này để giao các yêu cầu vận hành liên
  quan đến báo cáo trading.

**Duyệt plan — LUÔN mirror vào DollarBill plan channel (thêm 2026-07-02, user chỉ đạo):** khi
user duyệt/thảo luận duyệt plan trực tiếp với Mike ở BẤT KỲ topic Discord nào khác (không riêng
plan channel), Mike vẫn xử lý ngay tại chỗ (không ép user đổi topic), NHƯNG phải
`notify_thread.sh` xác nhận vào **1521183164364754974** ngay sau đó — channel này luôn là bản ghi
đầy đủ mọi lần duyệt, dù hội thoại thật diễn ra ở đâu. Lý do: tránh rải rác/loãng topic khác.

**Escalation khi plan T+1 không sẵn sàng (thêm 2026-07-01, sau sự cố DollarBill "timeout" nhưng
plan thực ra đã ghi xong — dispatch.sh job status không đáng tin 100%):** `send_plan_report.sh`
19:30 ICT giờ verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày kỳ vọng qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Nếu thiếu/sai ngày/hỏng schema →
**ESCALATE thật**: Telegram + Discord (như cũ) VÀ ghi bus event `question` (`plan-t1-not-ready`) để
Mike tự đọc được ở phiên sau, không chỉ trông chờ user thấy Telegram rồi tới hỏi. KHÔNG tự động
retry/re-dispatch (an toàn hơn — con người quyết định bước tiếp theo, đúng nguyên tắc human-in-the-loop
của toàn hệ thống).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 28.05% / Sharpe 1.87 / DD −18.8% / Calmar 1.50** (pin threads=1).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State hiện tại 2026-07-01: **NEUTRAL(3)**, DT5G_macro HEALTHY.

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- `bin/run_bot.sh`: wrapper gọi bot_execute.py, Discord notify, publish bus event.
- **`data/BOT_STOP`** = kill-switch tức thì.
- BQ Local Cache (DuckDB, threads=1): `data/bq_cache/`, ~100ms vs 5-15s BQ. Sync 23:45 ICT.
- Auto-OTP Gmail: `gmail_otp_reader.py` dùng `internalDate` filter (KHÔNG `newer_than`).
- PHS: **BLOCKED** (lỗi -700003, chờ credential) → paper only.
- **Workflow ngày trading đầy đủ** (T2-T6): BQ freshness(17:30) → plan T+1(19:30) → preflight(08:45)
  → execute sáng(09:05) → resume chiều(13:00) → **EOD report(15:00, `eod_trading_report.sh`, thêm
  2026-07-01)**. Toàn bộ post vào 1 Discord thread — Trading Daily (1521470705563340910).

### Kiến trúc fleet
- Companion daemon: **CHỈ Mike**. Mọi agent khác (Taylor, Bill, Mafee, v.v.) headless/native on-demand.
- Winston/Spyros/Wendy = native subagent `Agent(subagent_type=...)`, không còn daemon.
- Dispatch đúng: `bin/dispatch.sh`. Directive = mandate dài hạn only (deprecated cho task).
- Self-dispatch chặn. Agent → Mike phải escalate (event `question`), KHÔNG spawn Mike headless.
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, R&D Q3 program H2, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể (parking/lever/basket sweep): báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (bài học Wave1/H8a-tiebreaker 2026-07-05: OOS CAGR/Calmar tăng đúng luật nhưng
   toàn bộ đến từ 2021+2023, LOO rớt → route qua skeptic trước khi wire). V2.4/R3 đã qua chuẩn DSR/PBO
   (DSR≈1.0, PBO≈0.20 — xem `data/results_registry.md` mục "DSR / PBO Robustness Annex", script
   `dsr_pbo_annex.py`).

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 xong: tất cả = lens/tilt, không phải standalone book (banking có OOS edge nhưng 74% trong custom30V).

### Backup / DR
`~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private). Daily 00:00 ICT.

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
