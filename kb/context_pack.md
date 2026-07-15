# Mike fleet — context pack (v1105)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-15T05:51:36] Wags/finding — wags-fix: coord-2026-07-15 — question plan-0715 tồn vì chờ Mike (đã answer + bàn giao 2 quyết định); root cause phụ tìm ra: ops_autofix dispatch song song cùng-issue-khác-account → 2 Winston mâu thuẫn, đã fix global episode guard: {"job": "Wags_20260715_054507", "trigger": "COORD_WARN checker: question Winston/plan-0715-thieu-stamp-mafee-authorized (01:25:33Z) không có answer", "diagnosis …
- [2026-07-15T05:55:14] Winston/finding — ops-autofix 12:45: macro_health stale DA FIX + phat hien ticker_prune corruption 07-08+ (mo rong su co ticker_financial): {"job": "Winston_20260715_054514", "status": "DONE", "fix": "macro_health.json cu 21.2h = daily_refresh 07-14 ABORT o precheck (ticker_prune 10 tickers cho 07-1 …
- [2026-07-15T05:59:19] Winston/finding — ops-autofix 12:45 (job 2/2): backup ticker_prune pre-corruption + restore cache local + depth-check chong freshness-mu: {"job": "Winston_20260715_054508", "status": "DONE", "context": "Chay song song voi Winston_20260715_054514 (cung checker 12:45, per-account) — job kia da fix m …
- [2026-07-15T06:00:13] arch-reviewer/verification — ✅ CONFIRMED ARCH-REVIEW: wags-fix: coord-2026-07-15 — question plan-0715 tồn vì chờ Mike (đã answer + bàn giao 2 quyết định); root cause phụ tìm ra: ops_autofix dispatch song song cùng-issue-khác-account → 2 Winston mâu thuẫn, đã fix global episode guard: {"finding_topic": "wags-fix: coord-2026-07-15 — ops_autofix global episode guard (f814cc2) + answer question plan-0715", "verdict": "CONFIRMED", "confidence": " …
- [2026-07-15T06:29:11] Winston/finding — cron-reschedule-3-reports: registry DONE, crontab CAN THAY TAY: {"job": "Winston_20260715_061920", "status": "PARTIAL_DONE", "done": ["crontab diff prepared at /tmp/crontab_new.txt (3 changes verified: pt_8l 17:45->19:20, te …
- [2026-07-15T08:44:14] Taylor/finding — DCF echo: them fair_value_ps + gia thi truong vao dong hien thi (thuan hien thi, khong dung logic): {"job": "Taylor_20260715_084136", "status": "DONE — committed 5d3d49c (repo WorkingClaude)", "scope": "THUAN HIEN THI. KHONG doi logic quyet dinh/gate/status/ro …
- [2026-07-15T08:44:36] Winston/finding — ab_cross go khoi Paper Programs Daily Report — park vao kb/projects: {"job": "Winston_20260715_084136", "status": "DONE", "action": "Bo entry id=ab_cross khoi mang programs trong mike/kb/paper_programs_registry.json (8 chuong tri …
- [2026-07-15T08:49:51] quant-skeptic/verification — ✅ CONFIRMED VERIFY: DCF echo: them fair_value_ps + gia thi truong vao dong hien thi (thuan hien thi, khong dung logic): {"finding_topic": "DCF echo: them fair_value_ps + gia thi truong vao dong hien thi (thuan hien thi, khong dung logic)", "verdict": "CONFIRMED", "confidence": "h …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-14
> ⚠️ File này inject vào MỌI phiên/dispatch — giữ NHỎ. Chỉ để mục LIVE/đang-mở. Dự án ĐÓNG (NO-GO/
> KHÉP KÍN/XONG) → chuyển thành 1 file `kb/projects/<slug>.md` + thêm 1 dòng vào `kb/projects/INDEX.md`
> (INDEX được inject, chi tiết chỉ `cat` khi cần). Đừng để nhật ký dự án đã đóng tích lại ở đây.

## `mike@Mike.service` (remote-control daemon) đã TẮT HẲN (2026-07-07, user quyết định)
User giờ chỉ dùng Discord để nói chuyện với Mike (tách nhiều topic tiện phân việc hơn hẳn so với
ClaudeCode desktop app), gần như không dùng desktop app trực tiếp nữa (chỉ dự phòng lúc bất
thường, vd lỗi version model không xử lý được qua Discord). Đã xác nhận qua điều tra process/
systemd: **`mike@Mike.service`** ("Claude agent Mike, remote-control") và **`ccdb-mike.service`**
(bridge Discord thật, nhận tin nhắn + spawn `claude -p --resume <thread-uuid>` cho MỖI topic) là
**2 service độc lập hoàn toàn** — `ccdb-mike.service` KHÔNG phụ thuộc `mike@Mike.service` (xác
nhận `systemctl --user show ccdb-mike.service` không có Requires/After/PartOf/BindsTo nào trỏ tới
service kia). Đã `systemctl --user disable --now mike@Mike.service` — verify: service này
`inactive (dead)`, còn `ccdb-mike.service` vẫn `active (running)` bình thường, Discord không hề
gián đoạn. **Không cần sửa `bin/watchdog.sh`/`bin/fleet_health.sh`** — cả 2 script tự động iterate
qua unit đang `enabled` (không hardcode tên `mike@Mike.service`), nên tự động bỏ qua unit đã tắt,
không báo cảnh báo giả "DOWN"/"PERSISTENT DOWN" nữa.

**Nếu cần bật lại** (vd muốn dùng lại tính năng remote-control của desktop app):
`systemctl --user enable --now mike@Mike.service`.

## Model mặc định của chính Mike — SỬA LẠI về Sonnet 5 (2026-07-07, user yêu cầu, đảo ngược quyết
định 2026-07-06 đổi sang Fable 5)
Đã đồng bộ **3 nơi** (phát hiện có 2 tầng cấu hình song song trong bridge, không chỉ 1 chỗ — xem
[[reference-ccdb-model-config-layers]]):
1. `agents/Mike/.claude/settings.json` → `"model": "claude-sonnet-5"`.
2. `/workspace/ccdb-mike/.env` → `CCDB_MODEL=claude-sonnet-5` (đây là fallback thấp nhất, KHÔNG
   phải nguồn quyết định thật nếu DB đã có row).
3. **`/workspace/ccdb-mike/data/sessions.db` bảng `settings`** — đây mới là nguồn ưu tiên CAO NHẤT
   (thread override > global > `.env`). Phát hiện 4 dòng rác sai format từ các lần `/model` trước
   đó (`"Sonnet 5"`, `"sonnet 5"` có dấu cách — CLI từ chối, đây chính là lỗi user gặp ở 1 topic
   khác). Đã dọn: xóa hết override riêng theo thread, chỉ giữ 1 giá trị global
   `model.global.claude = "claude-sonnet-5"` (+ đồng bộ key legacy `claude_model` cho nhất quán
   hiển thị). Không cần restart `ccdb-mike.service` — bridge tự đọc lại nguồn này mỗi lần spawn
   session mới.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (fable) chẩn
đoán + sửa + verify + báo Trading Daily; đã wire vào `ops_health_check.sh` (08:20/12:45) và
`sync_bq_cache_daily.sh` (23:45). Cooldown 1h/vấn đề chống bão dispatch. **Ranh giới cứng
(không bao giờ tự sửa, escalate question + Telegram):** trade plan, trading_rules.json,
logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Mike trong phiên sống thấy
lỗi ops → tự sửa trực tiếp cùng ranh giới đó, không cần chờ checker.

## Onboarding account mới cho team Mike (thêm 2026-07-06, user yêu cầu chuẩn hoá quy trình)
Khi user nói "giao quyền quản lý tài khoản X cho team Mike" → làm theo
`kb/account_onboarding_runbook.md` theo đúng thứ tự, không tự bịa quy trình. Tóm tắt: cron
dùng-chung (preflight/ops-health-check/send-plan-report/eod-report/dispatch-DollarBill) đã
tổng quát hoá qua `trading_bot.config.live_dnse_labels()` + `bin/for_each_live_account.sh` —
account mới `enabled:true/mode:live/broker:dnse` trong `trading_bot_accounts.json` tự động
được các bước này nhận, KHÔNG cần sửa cron. Riêng 4 dòng cron THỰC THI THẬT (`run_bot.sh`,
`bot_heartbeat.sh`, lunch-pkill) KHÔNG tự động — luôn hỏi user xác nhận trước khi thêm (điểm
không thể đảo ngược: bot tự đặt lệnh thật lần đầu, không người duyệt giữa chừng).

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01. **Trim 07-06 ĐÃ HOÀN TẤT** (23/23 lệnh bán,
  710,5tr/710,1tr kế hoạch = 100%, không lệch đối soát broker) — exposure 141,4%→~70% NEUTRAL target
  như kế hoạch, 8 mã basket-drift đã thoát hết (LPB/MSB/VHC/HAH/VIB/VGC/DCM/MBS). **Nợ margin thật
  VẪN CÒN 409,86tr VND** (chưa trả — lần đọc API giữa chiều báo debt=0 là do balance CHƯA cập nhật
  xong, không phải nợ đã được trả; xác nhận bằng ảnh chụp app DNSE thật của user + đọc lại API lúc
  16:12 ICT, xem `kb/INCIDENTS.md` 2026-07-06 "CORRECTION"). **NAV xác nhận đúng: 983.002.349 VND**
  (khớp chính xác ảnh chụp app: Tiền 709.276.086 + Cổ phiếu 683.590.000 − Nợ 409.863.737). Nợ margin
  sẽ giảm khi tiền bán thật sự settle T+2 (08/07). 15 vị thế còn lại. run_bot.sh 09:05 ICT mỗi T2-T6.
  **Cập nhật cùng ngày:** `verify_account_snapshot.py` từng dùng BQ Close (sync đêm 23:45) cho MTM
  cùng ngày → NAV đã post lúc 15:00 dùng nhầm giá 07-03 (688,38tr thay vì 683,59tr thật). Đã vá: dùng
  `close_price()`/`latest_trade()` DNSE boardId=G1 khi `--asof`=hôm nay (verified khớp app tới đồng),
  BQ vẫn dùng cho ngày quá khứ. `nav_history_SpaceX.csv` dòng 07-06 đã sửa lại đúng. Chi tiết:
  `kb/INCIDENTS.md` 2026-07-06 "Two wrong end-of-day market price sources".
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
- **ZaloPay** (DNSE 0001743768, tên cũ `dnse_main`, đổi tên 2026-07-06): V2.4 LIVE từ 2026-07-06
  (user quyết định). **CASH-ONLY** (không margin, package "ZaloPay" id=1258 type N) — cơ hội so
  sánh V2.4 có-margin (SpaceX) vs không-margin. Tài khoản có 7 vị thế CŨ (giữ từ trước khi bot
  quản lý, không có lịch sử FILL trong journal nội bộ): DGC/MSH/TCM/TLG/VHC/VIB/VPB. **DGC (47,2%
  NAV) EXCLUDED khỏi rebalancing** qua field mới `excluded_tickers` trong
  `secrets/trading_bot_accounts.json` (enforce cứng ở `bot_execute.py` qua
  `trading_bot.plan.filter_excluded_tickers()`, không phụ thuộc plan generator nhớ đúng) — lý do:
  đang bị HOSE hạn chế giao dịch (QĐ 448, chỉ khớp định kỳ, cắt margin) + cảnh báo (QĐ 544, kiểm
  toán ngoại trừ) do lãnh đạo bị khởi tố hình sự 17/03/2026, ước gỡ hạn chế ~11-12/2026 (xem
  legal-vn/Wendy research 2026-06-21/26/29 — Điều 42 QĐ 22 cần đủ 2 điều kiện: khắc phục nguyên
  nhân + 6 tháng sạch CBTT liên tục). Taylor giữ DGC vì lý do đầu tư (target 70-75k/12-18 tháng,
  +37% EV, 65% xác suất, briefing 2026-06-29), KHÔNG phải vì kẹt thanh khoản.
  NAV thật go-live (xác nhận API 2026-07-06T07:42): **tổng NAV 1.011.470.378đ, active NAV (loại
  DGC, dùng làm cơ sở target V2.4) 534.470.378đ** — dùng `bin/compute_active_nav.py --account
  ZaloPay` để tính lại khi cần (không phụ thuộc lịch sử journal, đọc trực tiếp balance/positions
  thật + giá BQ). **Known gap:** `daily_nav_snapshot.py` chưa tính đúng P&L cho vị thế legacy này
  (cần lịch sử FILL nội bộ mà account không có) — NAV/active_nav đã đúng, phần P&L breakdown cho
  báo cáo cần việc riêng sau. Cơ chế `excluded_tickers` viết TỔNG QUÁT (không riêng ZaloPay) để
  dùng cho account tương lai có vị thế legacy tương tự — xem `kb/coding_guidelines.md` §7. Chi
  tiết đầy đủ + 10 selfcheck: `kb/INCIDENTS.md` không có entry riêng (không phải sự cố, là setup
  bình thường) — xem commit `87392be` (WorkingClaude repo).
  **Cập nhật 2026-07-06 tối (user xác nhận 2 lần):** đã thêm 4 dòng cron thực thi thật
  (`run_bot.sh --account ZaloPay` sáng/chiều, `bot_heartbeat.sh ZaloPay`, lunch-pkill) —
  ZaloPay giờ tự động y hệt SpaceX. **Plan 07-07 hiện tại vẫn là HOLD/0 lệnh** (bản nháp
  transition Option A — bán dần VIB/VHC/TCM/TLG/MSH, mua custom30V thay thế, user đã chọn
  hướng A — dispatch DollarBill 2 lần đều timeout/treo, KHÔNG ghi được file cập nhật, cần
  dispatch lại + điều tra nguyên nhân treo) → phiên chạy tự động ĐẦU TIÊN sáng mai
  (2026-07-07) sẽ không làm gì (an toàn). `approved_by` vẫn null → preflight 08:45 mai sẽ
  báo RED cho ZaloPay (NOT_APPROVED) — ĐÃ BIẾT TRƯỚC, vô hại vì 0 lệnh. **Bug nghiêm trọng
  phát hiện + đã vá cùng tối:** `dnse_raw_{date}.jsonl` dùng chung cho MỌI account theo
  ngày, bản ghi "balances" không gắn account → NAV SpaceX báo sai 688,5tr (lẫn balance
  ZaloPay) khi tính lại báo cáo EOD hôm nay. Đã vá tận gốc (`trading_bot/brokers.py` gắn
  account_no/label mọi bản ghi log, `daily_nav_snapshot.py` lọc đúng account) + verify lại
  đúng 982.867.365đ + gửi đính chính (Telegram — Discord "Trading report" lỗi HTTP 500,
  không phải do nội dung). Chi tiết: `kb/INCIDENTS.md` 2026-07-06. **Topic Trading report đã
  THÔNG lại ~23:45 cùng tối**: root cause = private thread, bot rớt membership khi archive —
  unarchive KHÔNG đủ, user phải @mention bot trong topic để thêm lại. Report EOD chính thức
  đã gửi vào topic. eod_trading_report.sh giờ có fallback Telegram+Trading Daily khi post fail
  (không bao giờ rơi im lặng nữa).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

## Đang R&D
- **Taylor · EXTREME-regime gate PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `extreme_regime_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`); global default + SpaceX/live GIỮ `False`. Week-1 stress-injection PASS 24/24 (`stress_extreme_regime.py`: arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls). **Target kết thúc ~2026-07-28 (~20 phiên).** 3 điều kiện còn lại trước LIVE: (a) ZERO false-trigger qua ~4 tuần benign, (b) không can thiệp NORMAL-path, (c) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor · vol-scale buy chase-cap (patch#3) PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `chase_cap_vol_scale_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`, k=2.0/ceil=0.04); global default + SpaceX/live GIỮ `False`. Executor-path stress PASS 15/15 (`stress_vol_scale_chase_cap.py`: wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · paper limit > static + NEG-control live→static). **Target kết thúc ~2026-07-14 (~10 phiên — ngắn hơn EXTREME vì fire trên gap-up thường, tích event nhanh).** Điều kiện trước LIVE: (a) paper sạch (wiring đúng trên quote thật + fail-safe khi thiếu rvol cache), (b) không can thiệp NORMAL-path ngày non-gap, (c) skeptic rerun REAL-fill vs `min(open,L)` proxy trên correlated gap-up @NAV target, (d) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor**: sector sweep #10+ (chờ Mike dispatch)
- **Taylor · fill-timing khung giờ (BUY 10:45-11:15 / SELL 09:15-09:45)**: ĐÃ xử lý xong 2026-07-02 (job Taylor_20260702_031608, note cũ ở dòng này lỗi thời). Edge THẬT & IS/OOS-stable (BUY tại 11:15 rẻ hơn open +17.6bps/lệnh, t=12.0; SELL tại open đúng, +11.8bps vs ATC) nhưng **KHÔNG flip `fill_timing_live_gate` ngay** — cần paper tích lũy ~3-4 tuần fill (từ go-live 2026-07-01, mới ~3-4 phiên) để `execution_quality_review.py` xác nhận NET-of-noise capture (noise 110-220bps >> edge 17bps) → quant-skeptic → user sign-off mới flip. Checkpoint tự nhiên: ~cuối tháng 7.
- **V2.5**: R&D-complete, DISABLED. Reminder: 2026-07-07 Mike hỏi user go-ahead integration.
- **Taylor · DC-book (ConvergePort) NEUTRAL idle-cash waterfall PAPER-TRADING** (bắt đầu 2026-07-06,
  user duyệt trực tiếp, job `Taylor_20260706_125540` + `Taylor_20260706_131247`): khi NEUTRAL và
  BAL/LAG rỗng (đúng tình trạng SpaceX từ ~04/2026), thứ tự ưu tiên giải ngân phần tiền rảnh:
  **BAL/LAG (full trước, không đổi) → DC book/ConvergePort (double-confirm sector-lens BUY ∧ 8L
  rating≤2, capacity ~10-15B ex-DHG) → custom30V (phần còn lại)**. Khi BAL/LAG có deal trở lại → rút
  ưu tiên ngược lại, bán custom30V trước rồi mới đến DC book (reverse-unwind). Backtest xác nhận: DC
  làm top-priority (thay BAL/LAG) = REFUTE mạnh (12.05% CAGR/DD-38.4% vs R3 28.05%/DD-18.8%); DC làm
  lớp giữa (đúng thứ tự trên) = +5.0pp trên sleeve parking, ước tính +3.5pp/năm cho SpaceX-now. **Caveat
  quan trọng: DSR phần excess này chỉ 0.775 (<0.95 ngưỡng an toàn) — bảo hiểm hợp lý, CHƯA phải alpha
  tin cậy cao** → lý do bắt buộc phải paper trước, không wire live ngay. Chạy CHỈ trên account paper
  `main` (override trong `trading_bot_accounts.json`), global default + SpaceX/live GIỮ nguyên (không
  đổi gì). **Đã thêm vào EOD daily report** (theo yêu cầu user 2026-07-06) — xem section paper sleeve
  trong `eod_trading_report.sh` output.
  **Review = EVENT-ANCHORED, KHÔNG PHẢI ngày cố định** (user quyết định 2026-07-06, sau khi Taylor tự
  đính chính lý do "3 tháng" không phải vì DSR mà vì chu-kỳ cơ chế): mốc review = khi chu kỳ
  reverse-unwind ĐẦU TIÊN (LAG dự kiến refill cuối 07, job `Taylor_20260704_033932`) hoàn tất + settle
  4-6 tuần sau đó. Sàn ~2 tháng (đủ thấy trọn unwind+settle), trần ~2026-10-06 (tránh mùa BCTC Q3).
  Nếu LAG refill trượt lịch → mốc review trượt theo, KHÔNG giữ cứng 10-06. **Mike + Taylor cùng theo
  sát diễn biến portfolio để đề xuất ngày review cụ thể khi đủ điều kiện** — không tự động, không
  phải 1 con số đã chốt sẵn.

  **⚠️ AGENDA SỬA tại mốc review (thêm 2026-07-13, job `Taylor_20260713_100550`, user xác nhận CHƯA
  sửa ngay — để tự nhiên chạy sai thêm một thời gian nhằm quan sát whipsaw thật qua đúng đợt LAG
  refill, rồi sửa gộp 1 lần tại mốc review).** Phát hiện quan trọng: **paper sleeve ĐANG CHẠY SAI so
  với chính spec đã backtest/pin** — dùng trigger NHỊ PHÂN (BAL/LAG có deal → tắt hẳn DC book) thay vì
  spec đúng là DC book chạy LIÊN TỤC trên phần tiền dư (residual). Hậu quả đo được: 57.8% ngày
  NEUTRAL-có-✓✓ vẫn có deal BAL/LAG mới trong khi tiền park còn ~38% NAV → bản nhị phân đang chạy hiện
  tại **TỆ HƠN CẢ baseline không có DC book** (CAGR 27.26% / DD −17.8% / Calmar 1.53 / turnover 20.7×,
  so với spec đúng 27.56% / −15.5% / 1.77 / 3.18× và baseline R3 27.35% / −17.6% / 1.55). 4 việc cần
  làm tại mốc review, theo đúng thứ tự ưu tiên:
  1. **Đổi trigger sang continuous-residual** (quan trọng nhất — đây là bug thực chất, không phải tối ưu thêm).
  2. Đồng bộ lịch rebalance DC book vào q2m5 (giống custom30V) — tự giảm whipsaw ~4 lần, đã backtest (job `Taylor_20260706_173317`).
  3. Cap gộp 0.15/tên (chống trùng mã DC↔custom30V vượt trần name_cap 10% NAV khi sleeve lớn — job `Taylor_20260707_042827`).
  4. Liquidity floor 3B thay hard-exclude DHG đơn thuần (job `Taylor_20260707_042827`).
  Đã kiểm tra kỹ 4 góc còn lại (sizing/depth-weight, ✓✓ làm tiebreaker BAL/LAG, mở rộng CRISIS/BEAR,
  sector-lens đứng riêng) — **không còn không gian cải thiện thật**, không cần backtest thêm cho các
  góc đó khi tới review, chỉ cần làm đúng 4 việc trên.

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
- **Per-job thread routing tổng quát (thêm 2026-07-06)** — `_agent_thread_override` chỉ đúng cho
  agent LUÔN thuộc 1 topic cố định (DollarBill). Nhưng Taylor phục vụ NHIỀU topic song song (vd
  user tách riêng "nghiên cứu 8L" và "nghiên cứu vĩ mô", cả 2 đều dispatch Taylor) — báo cáo hoàn
  thành từng job phải về ĐÚNG topic đã yêu cầu job đó, không phải topic Mike đang hoạt động lúc
  job xong. Fix: `dispatch.sh` giờ ghi `discord_thread_id` NGAY vào job record lúc dispatch (chụp
  1 lần, không đổi), mọi thông báo (nhận việc/xong/fail/circuit-breaker/usage-limit) đọc lại field
  này qua `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/INCIDENTS.md`.
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

## Audit cron toàn hệ thống XONG (Winston_20260712_142100) — 2 fix đang dispatch (2026-07-12)
User yêu cầu review thứ tự cron. Kết quả: **thứ tự ĐÚNG**, nhưng lộ 2 bug nội dung khẩn:
- **C1 CRITICAL** (tự verify độc lập bằng code+BQ live, xác nhận đúng 100%): `publish_gated_state.py`
  đọc DT5G qua `BQ_LOCAL_CACHE` (T-1) thay vì live — với `MAX_STATE_LAG=0` (siết 07-11), thứ Hai
  07-13 19:00 sẽ FAIL, không dispatch DollarBill. Dispatch Taylor (fable) fix ngay hôm nay: job
  `Taylor_20260712_151135`.
- **H2 HIGH**: check `shares_outstanding_live` calibrate sai giả định → false-BLOCK ~thứ Tư 07-15.
  Đề xuất hạ BLOCK→WARN — CHƯA dispatch, chờ quyết sau khi C1 xong.
- Phụ: M5 (executor.py đọc ticker_prune.parquet monolith chết từ 06-26, ảnh hưởng 2 paper trial
  evidence), M4 (sync_bq_cache thiếu `|| true`), M3 (optional reorder pt_8l/telegram sau 19:00).
- Bản thảo quy tắc "thêm cron mới đặt giờ nào" ở Phần 5 `mike/agents/Winston/audit_cron_order_20260712.md`
  — CHƯA chính thức hoá thành `kb/cron_registry.md`/coding_guidelines, còn nợ.

User đồng thời yêu cầu dọn crontab paper-trading lạc hậu (dựa production hiện tại V2.4 + version
numbering + research đã đóng: V2.5 lever NO-GO, Q-sleeve NO-GO, DVR-8L NO-GO, momentum-deals NO-GO
đã production-thực-thi-rồi, fa8l CP2 NO-GO). Dispatch Winston (fable) research + đề xuất diff (KHÔNG
tự sửa crontab thật): job `Winston_20260712_151206`. Việc còn đang chạy: EXTREME (~07-28), chase-cap
(~07-14), fill-timing (~cuối tháng 7), DC-book (event-anchored) — KHÔNG được đụng.

**Còn nợ sau khi 2 job trên xong**: verify C1 fix (quant-skeptic), quyết H2, formalize cron_registry.md,
áp dụng diff dọn crontab (sau khi tôi review), dispatch Taylor xem lại M5 (2 paper trial evidence).

## C1 CRITICAL (publish DT5G qua BQ_LOCAL_CACHE) — FIX + COMMIT + VERIFY XONG (2026-07-12)
Fix: `deploy_golive_dt5g_v4/publish_gated_state.py` — `os.environ.pop('BQ_LOCAL_CACHE', None)` process-
local trước import `macro_state_live` (commit `4995262`, repo WorkingClaude). Cả 2 attempt dispatch
Taylor đều timeout (tự mở rộng phạm vi sang backfill C1b không cần thiết — Monday's daily_refresh tự
recompute full window nên không cần backfill riêng); Mike tự verify code + tự commit + dispatch
quant-skeptic bằng `--claim` (không có finding event chính thức từ Taylor do timeout).
**quant-skeptic CONFIRMED (high confidence)**: độc lập tái lập cơ chế bằng Python replica thật (pop
env → cache branch bypass → live path), xác nhận process-local (mỗi step trong daily_refresh/
bq_freshness_check chạy subprocess riêng, không leak sang sibling), không side-effect logic khác.
1 ghi chú tùy chọn (pop thêm `LOCAL_SNAPSHOT_DIR`) — hiện vô hại vì biến chưa được export ở đâu.
**Xong, không còn gì treo cho C1.** H2 (shares_outstanding_live false-BLOCK ~07-15) vẫn CHƯA quyết.

## User tự phát hiện BQ local cache stale — vấn đề LỚN HƠN dự kiến (2026-07-13)
User hỏi lại "BQ local đang stale, trễ mấy ngày" sau khi tôi báo cáo đã fix xong 8L cache (chỉ
verify fa_ratings/fa_ratings_8l, KHÔNG kiểm tra toàn bộ bq_cache). Tự kiểm tra phát hiện:
`data/bq_cache/ticker_prune.parquet` (monolith) đứng yên từ **06-26** (17 ngày) trong khi thư mục
chunked thay thế (`ticker_prune/<year>.parquet`) vẫn đồng bộ đúng — sync_bq_cache.py đã migrate
sang chunked quanh 06-26 nhưng monolith cũ không ai xoá/cập nhật.

**Blast radius LỚN**: grep xác nhận **27 file** vẫn đọc thẳng monolith cũ — không chỉ
`trading_bot/executor.py:507` (đã biết từ audit M5 hôm qua), mà còn 17 sector-screener script +
9 script backtest/research khác (gap_fairvalue_*, gq_score_gate, neutral_glide_backtest,
converge_union_test, lag_dnpr_event_study, gap_adaptive_proxy, gap_ev_by_liquidity).

Dispatch song song: `Winston_20260713_143546` (fix đường dẫn đọc cho cả 27 file, archive
monolith cũ theo coding_guidelines §10) + `Taylor_20260713_143629` (đánh giá tác động — finding
nào từ 06-26 tới nay đã dùng dữ liệu đông băng, ưu tiên cao nhất: chase-cap vol-scale review dự
kiến MAI 07-14 có bị ảnh hưởng rvol_20d/prior_close không).

## 2026-07-14: HOLD chủ động — user quyết định không giao dịch hôm nay
User yêu cầu 08:34 ICT (30' trước giờ mở cửa): "hôm nay không cần giao dịch". Đã xử lý:
- **SpaceX**: plan gốc (DollarBill) có 2 lệnh basket-swap (bán HPG 2200cp do basket drift ra khỏi
  custom30V_8L, mua LPB 900cp thay thế) — đã sửa `plan_SpaceX_2026-07-14.json` về orders=[],
  summary.action=HOLD, giữ nguyên 2 lệnh gốc trong field `user_override_original_orders` để tham
  khảo/xử lý lại sau nếu cần (basket drift HPG vẫn còn đó, chưa biến mất). Verify `load_plan()`
  đọc đúng, 0 orders → bot sẽ tự skip sạch.
- **ZaloPay**: không có file plan cho 07-14 (transition đã hoàn tất 07-13, không phát sinh gì
  mới) — verify `load_plan()` return None khi thiếu file → bot tự skip, an toàn, không cần sửa gì.
- Đã mirror vào kênh DollarBill plan channel.

**Việc còn treo (không khẩn)**: HPG vẫn basket-drift ra khỏi custom30V_8L — nếu muốn xử lý basket
swap này, cần lập lại plan cho ngày kế tiếp (không tự động quay lại, vì override hôm nay chỉ áp
dụng cho 07-14, ngày mai DollarBill sẽ tự tính lại từ đầu dựa trên basket composition mới nhất).

## User tự phát hiện BQ local cache stale — vấn đề LỚN HƠN dự kiến (2026-07-14→15)
User hỏi "BQ local lại stale à, sao không ai fix" sau khi thấy alert. Điều tra: KHÔNG phải cùng
loại lỗi hôm qua (cache/monolith). Phát hiện thật: bus event error thật (Taylor, 20:45 ICT 07-14)
— Taylor chạy TAY `refresh_fa_ratings.sh` (không qua cron, cron cũ đã xoá/cron mới chưa tới hạn)
làm 1 phần việc R&D khác, script tự ABORT đúng thiết kế vì fresh build chỉ ra 1 dòng cho 2026Q1
thay vì 337 dòng đã publish — bảo vệ thành công, KHÔNG ghi đè bảng `fa_ratings` (Mike tự verify
BQ live: vẫn đủ 337 dòng 2026Q1, an toàn).

**Phát hiện NGHIÊM TRỌNG HƠN trong lúc điều tra root cause của abort này**: bảng NGUỒN
`tav2_bq.ticker_financial` hiện tại (query BQ live, Mike tự làm 3 lần, unset cache, fully-qualified
table) báo **MAX(time)=2026-05-04, MAX(Release_Date)=2026-04-20, 65,178 dòng** — trong khi CHÍNH
audit hôm qua (`Winston_20260713_100733`) đã xác nhận qua BQ live: MAX(time)=MAX(Release_Date)
=**2026-07-08** (có MBS Q2). Dữ liệu không thể tự lùi 2 tháng cho 1 bảng append-only — nghi ngờ có
ghi đè/CREATE OR REPLACE làm hỏng bảng nguồn giữa 13/07 và giờ, có thể liên quan tới job Taylor
chạy refresh thủ công hoặc job R&D khác chạm bảng này.

Dispatch khẩn: `Winston_20260714_174411` — xác nhận độc lập mâu thuẫn, kiểm tra BQ table metadata
(lastModifiedTime), truy vết script/job nào có thể đã ghi đè, đánh giá rủi ro cho cron mới
(20:00 ICT tối nay 07-15, lần chạy thật đầu tiên của quy tắc quý mới) nếu bảng nguồn thật sự hỏng.
KHÔNG tự sửa/rebuild — chờ xác định nguyên nhân trước.

## Plan 07-15 đã duyệt (SpaceX + ZaloPay) — quyết định khôi phục ticker_financial ĐANG CHỜ user (2026-07-15)
User: sẽ tự hỏi BQ admin (upstream tav2 pipeline) về sự cố ticker_financial rồi quyết định hướng
xử lý sau — Mike KHÔNG tự khôi phục/tạm dừng cron cho tới khi có quyết định. Trong lúc chờ, user
đã duyệt trực tiếp plan 07-15 cho cả 2 account (Mike verify trước: cả 2 plan 0 BAL/0 LAG, chỉ là
basket-swap dựa trên custom30V_8l composition đã thiết lập từ trước rebalance quý gần nhất —
không bị ảnh hưởng bởi corruption ticker_financial 07-14). approved_by=user đã ghi vào cả 2 file.

**Còn treo, chờ user quay lại**: quyết định khôi phục ticker_financial/fa_ratings_8l từ backup
Winston đã chụp (`ticker_financial_ttbackup_fresh_20260714`, `fa_ratings_8l_ttbackup_fresh_20260714`)
+ quyết định có tạm dừng cron mới 20:00 ICT (quy tắc quý mới, sẽ chạy lại tối nay 07-15) hay không
nếu nguồn upstream chưa được xác nhận đã sửa.

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.84% / Sharpe 1.84 / DD −18.2% / Calmar 1.53** (pin threads=1,
  re-pin 2026-07-12 sau khi đóng kênh MOM_N/MOM_S trong TIER_BAL — commit `4fbd492`, quant-skeptic
  CONFIRMED; xem `data/results_registry.md` + `plan_close_mom_20260712.md`). Số cũ 28.05%/28.82% đã
  lỗi thời qua 2 lần re-pin (DT5G swap 07-11, rồi MOM closure 07-12).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12) — không phải "thử bị loại", là thay đổi production chính thức
Sau chuỗi R&D đầy đủ (momdeal Phase 1 CP1 NO-GO 0/13 feature → nhánh DVR-8L-sizing CP-DVR1 NO-GO →
đo tác động Scope A/B → kiểm tra tách MOM_N-vs-MOM_S, tất cả quant-skeptic CONFIRMED), user duyệt
đóng `MOMENTUM_N`+`MOMENTUM_S` khỏi `TIER_BAL` (giữ nguyên `MOMENTUM`/`MEGA` generic — Scope B đóng
cả họ bị số đo bác, generic vẫn đóng góp thật). Lý do: thành công lịch sử của 2 tier này chủ yếu do
dồn mẫu regime 2020-21, không phải pattern lặp lại được; hậu-2021 gần như hoà vốn. Chi tiết đầy đủ:
`plan_close_mom_20260712.md`, `plan_dvr_8l_sizing_20260712.md`, `plan_momentum_deals_20260711.md`.

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

## Dự án đã đóng — chi tiết theo yêu cầu (đọc khi cần: `cat kb/projects/<file>.md`)
- 2026-07-13 **World Cup + rổ lãi suất huy động (Pillar A′)** → `kb/projects/wc-deposit-rate-gate.md` — ĐÓNG cả 2 hướng — N quá mỏng / 0-4 GO, không wire production.
- 2026-07-13 **Plan-approval gate (second-chance cron + code-gate)** → `kb/projects/plan-approval-gate.md` — XONG — second-chance re-send 23:00 + code-gate bot_execute.py, hiệu lực 09:05 07-14 (commits 4216295/27e1282/54d488c).
- 2026-07-13 **Plan ZaloPay transition day 5/5 (FINAL)** → `kb/projects/zalopay-transition-0713.md` — XONG — bán VIB + mua BID, ngày cuối chuỗi transition 07-07→07-13.
- 2026-07-13 **DT5G BULL-giả bug → audit freshness toàn hệ thống** → `kb/projects/dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN — EW-leg path fix + CRITICAL custom30V basket fix + F3 re-pin; live không sai.
- 2026-07-13 **Báo cáo tuần 07-06→07-10 + chống tái diễn** → `kb/projects/weekly-report-mechanism.md` — XONG — đã gửi + WARN check báo cáo tuần/tháng quá hạn (commit 7147ac3).
- 2026-07-13 **Audit dữ liệu 8L (mùa BCTC Q2)** → `kb/projects/8l-data-audit.md` — XONG — 8L đầy đủ; 3 fix cache/cadence/doc dispatch (Winston_20260713_103213).
- 2026-07-12 **lag_edge_health.csv staleness** → `kb/projects/lag-edge-health-staleness.md` — KHÔNG phải bug — mtime-tươi/content-cũ đọc nhầm; falsifiable check ~08-25.
- 2026-07-12 **fa_ratings/8L re-tune + rebuild builder** → `kb/projects/fa-ratings-rebuild.md` — Re-tune 8L NO-GO (16/16); rebuild fa_ratings builder HOÀN TẤT, BQ-write-identity fixed.
- 2026-07-12 **V2.5 leverage verification** → `kb/projects/v2.5-leverage-nogo.md` — NO-GO, giữ DISABLED — edge là IS-artifact (OOS âm), DSR<0.95.
- 2026-07-12 **LAG-weight (tăng tỷ trọng PEAD)** → `kb/projects/lag-weight.md` — ĐÓNG — chấp nhận kết luận mô tả, không tăng trần w_LAG.
- 2026-07-12 **Dự án momentum-deals (đóng kênh MOM_N/MOM_S)** → `kb/projects/momentum-deals.md` — KHÉP KÍN — production LIVE, re-pin R3 27.84%/1.84/-18.2/1.53 (commit 4fbd492+9df396d).
- 2026-07-12 **Dự án Q-sleeve (rổ nhỏ chất lượng cao)** → `kb/projects/q-sleeve.md` — NO-GO cả 2 trục, quant-skeptic CONFIRMED.
- 2026-07-12 **Audit sẵn sàng mùa BCTC Q2/2026** → `kb/projects/bctc-q2-readiness-audit.md` — KHÉP KÍN — fix CRITICAL LAG-blind + MEDIUM freshness + 3 mục nhỏ, đều verified.
- 2026-07-03 **Usage-limit auto-resume** → `kb/projects/usage-limit-auto-resume.md` — XONG — dispatch.sh phát hiện usage-limit → pending_resumes → resume_pending.py cron.
- 2026-07-02 **Reliability hardening (4 việc AgentOps)** → `kb/projects/reliability-hardening.md` — XONG — circuit breaker + idempotency guard + trace_id + INCIDENTS.md (commit e1d9b7c).

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/ (index ở trên). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
