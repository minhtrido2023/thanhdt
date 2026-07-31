# Mike fleet — context pack (v1571)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-31T06:10:52] Winston/answer — escalate-ZaloPay-CAPIT-buys-missed-2026-07-21: {"resolution": "SUPERSEDED theo thoi gian — verify DNSE 2026-07-31 xac nhan ZaloPay dang giu du ca 5 ma CAPIT (SAB/SIP/VNM/PVT/NCT), nghia la mua bu da xay ra s …
- [2026-07-31T06:10:52] Winston/answer — SpaceX-plan-2026-07-23-chưa-duyệt: {"resolution": "SUPERSEDED — plan tung ngay da duoc duyet/thuc thi binh thuong tu do toi nay.", "closed_by": "Mike", "closed_reason": "stale_superseded"}
- [2026-07-31T06:14:41] Winston/finding — cron-freshness-audit-§14: {"audit_scope": "toàn bộ cron_registry.md (2026-07-31), tìm cặp producer→consumer có rủi ro §14 (consumer tin schedule-order thay vì freshness-check thật)", "me …
- [2026-07-31T06:40:26] Winston/finding — cron-freshness-fix-caseA-anomaly-flags: {"case": "A (HIGH) — ops_health_check 08:20 → golive_recommend_v23 19:00 qua data/anomaly_flags.json", "loi": "anomaly_excluded() chỉ tính TTL 30d từ last_alert …
- [2026-07-31T06:47:28] Winston/finding — cron-freshness-fix-A-anomaly-flags: {"case": "A (HIGH)", "cap": "ops_health_check 08:20 -> anomaly_flags.json -> golive_recommend_v23 19:00 (anomaly_gate.py)", "loi": "anomaly_excluded() chi tinh  …
- [2026-07-31T07:02:01] Winston/finding — cron-freshness-fix-caseB-dt5g-eod-8l: {"case": "B (HIGH)", "cap": "daily_refresh 18:30 (worst-case 90min) -> eod_trading_report 19:10 + pt_8l_daily 19:20 qua tav2_bq.vnindex_5state_dt5g_live", "loi" …
- [2026-07-31T07:02:01] Winston/finding — cron-freshness-fix-caseC-telegram-8l-csv: {"case": "C (MEDIUM)", "cap": "pt_8l_daily 19:20 -> telegram_run_daily 19:35 qua data/rating_8l.csv", "loi": "telegram_run_daily.sh khong check age file - chi d …
- [2026-07-31T08:00:32] Winston/finding — sbv-weekly-check-2026-07-31: {"date": "2026-07-31", "current_rate": 4.5, "fetch_status": "fetch_failed", "rate_changed": false, "note": "fetch_failed_assumed_unchanged", "verify_log": "/hom …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-30 (token-cost trim #2: gộp 3 mục ticker_prune rải rác, sửa stale
> due-diligence-mandate/G6-repin, nén sự cố-đã-đóng + Trứng vàng theo đúng kỷ luật đã có, gắn cờ
> 2 checkpoint R&D quá hạn chưa xác nhận thay vì giả định — KHÔNG tự đoán trạng thái)

## Domain-constraint layer — P1 LIVE, P0 shadow đang chạy (2026-07-29, commit `d64717f`)
Theo sau talk "Why Agentic Systems Need Ontologies" — thiết kế đầy đủ + kiểm kê 12 guardrail cơ
khí có sẵn: `mike/agents/Taylor/research/ontology_constraint_layer_design_20260729.md`. User chốt:
làm P1+P0 dạng patch tối thiểu, KHÔNG xây `trading_bot/constraints.py`/registry (chỉ đáng làm khi
có ≥3 rule cùng lúc, có thể là lúc V2.5 cần nhiều rule tường minh hơn).
- **P1 (ACTIVE, LIVE từ phiên 07-30)**: `filter_lag_rating_orders()` — lưới an toàn tầng ORDER cho
  gate 8L rating≤3 của LAG (chốt 07-27), vá lỗ hổng gate cũ chỉ sống ở tầng sinh tín hiệu. Gọi ở
  `bot_execute.py` ngay sau `cap_lag_orders`. Verify: 14/14 + 22/22 selfcheck (Mike tự chạy lại độc
  lập, không chỉ tin báo cáo Taylor), replay đúng case TRC/MST bị chặn, 0 lệnh khác đổi trên 21
  plan thật 07-20→07-28.
- **P0 (WARN_ONLY, chỉ log)**: `data/plan_buying_power_shadow_log.csv` — Σ lệnh mua vs sức mua
  broker sống (`ppse.pp0Buy`), KHÔNG chặn gì. Nhắm đúng pattern funding_required tái diễn 3 lần
  (07-23/07-27/07-28) mà KHÔNG đảo ngược quyết định user 16:16 07-28 (từ chối luật `orders≤cash`
  cứng vì margin tương lai) — vế phải là sức mua đo được (đã bao gồm hạn mức vay), không phải cash
  tĩnh. ⚠️ **Giới hạn đã biết**: SpaceX (account margin) chưa từng có bản ghi `pp0Buy` thật trong
  lịch sử (code chỉ gọi API đó khi thiếu cash mặt, SpaceX có margin nên chưa rơi nhánh đó) — số
  liệu replay 3/3 sự cố cũ dùng PROXY (`availableCash`), là cận dưới, không phải bằng chứng rule
  sẽ bắn đúng với `pp0Buy` thật. **Việc còn treo**: theo dõi log ≥10 phiên thật rồi Mike/user mới
  xét P0 → ACTIVE (không tự động promote).

## Sleeve "mua khi sợ hãi có tính toán" — quét chủ động HÀNG TUẦN (mandate user 2026-07-23)
Sau chuỗi case TV1 + DGC (cả 2 lần đầu bị đánh giá quá thận trọng, user tự phát hiện + sửa —
xem 2 mục trên/bên dưới) — user chỉ đạo: đừng chỉ chờ user tình cờ để ý, chủ động dò tìm THÊM
case hàng tuần. Đã cài `bin/fearbuy_weekly_scan.sh` (cron Friday 08:10 ICT, dispatch Taylor,
đăng ký `kb/cron_registry.md`) — kết hợp refresh `anomaly_scan.py` + WebSearch tin khởi tố/bắt
lãnh đạo DN niêm yết 7-14 ngày qua, áp bộ lọc QUALIFY/NON/AMBIGUOUS trong
`calculated_fear_state_backstop.md`. Luôn báo cáo (kể cả 0 case mới — quy tắc quiet-heartbeat).
Đây là recon, KHÔNG tự mua — mọi case đáng chú ý vẫn cần due-diligence sâu + user duyệt riêng
như TV1/DGC.

## Dự án thay thế `ticker_prune` → `universe_pit` (gộp 3 mục rải rác 2026-07-30, xem lịch sử ở `kb/incidents/`/git log nếu cần)
`ticker_prune` không có quản trị (curation circular-bias, không tái lập được, và **07-29 bị
bq_admin TRUNCATE+rebuild mất 58 mã khỏi toàn lịch sử** — 513→455 mã, -17%, đúng cơ chế "mã vào
bằng daily-append bị xoá ở lần rebuild toàn bộ kế tiếp" — user chốt 07-29 KHÔNG khôi phục từ
backup, giữ `ticker_prune_ttbackup_fresh_20260713` chỉ làm mỏ neo nghiên cứu) → team tự xây
`universe_pit` (point-in-time từ `tav2_bq.ticker`, B3=1,0 tỷ VND/ngày). **Cổng cứng §3.2b/Q9 ĐÃ
MỞ từ 2026-07-22** (user chốt A′+Q-C, không Q-B) — P1-P3 cutover production (custom30V→
`universe_pit_q` commit `ce7d457`, golive_recommend_v23 commit `0bfbdfe`). **CAPIT §4.4 = NỬA XONG
(G4)**: breadth cutover `universe_pit` (`CAPIT_BREADTH_SOURCE=pit`, top-250, washout_gate 0,31,
commit `dcee252`); **pool pbz + ADV cap CỐ Ý còn ghim `ticker_prune`** (đổi rổ đang giải ngân, 2
vòng đo thất bại tìm ngưỡng bảo toàn) — cấm cutover pool khi `capit_fired=true`. **G6 re-pin R3
XONG 2026-07-22** (`results_registry.md:4040`); số bị **re-pin LẠI 07-29 do đổi vintage restate
DT5G, không đổi mô hình** (số liệu ở "Tri thức chung của đội" bên dưới). Còn lại thật: G5 shadow
≥10 phiên, G7 N-trial review, G8 data/cron-registry gate, G9 quant-skeptic full review — cộng 3
việc mới phát sinh từ audit 07-29 (Winston_20260729_132257): (1) migrate breadth-decoupling guard
`macro_state_live.py:158` sang `universe_pit` (đang chạy, cần self-check+quant-skeptic trước khi
wire — input DT5G production); (2) pin/snapshot BQ hàng tháng cho bảng dễ restate (`ticker`/
`ticker_financial`/`ticker_prune`/`universe_pit`/VNINDEX_PE, dispatch Winston đang chạy); (3)
WASHOUT_GATE đã tự verify KHÔNG cần rà lại (0,31 hiệu chuẩn đúng trên `universe_pit`, không phải
bug). Tài liệu đầy đủ:
`mike/agents/Taylor/research/ticker_prune_replacement_plan.md` +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` +
`mike/agents/Winston/research/ticker_prune_hidden_risk_audit_20260729.md`.

## CAPIT (bear-washout) — vị thế THẬT vẫn đang giữ (verify DNSE 07-31), `capit_fired` KHÔNG phải "đang giữ" (cập nhật 2026-07-31)
⚠️ **Đính chính quan trọng (job `Taylor_20260731_025222`,
`mike/agents/Taylor/research/capit_state_visibility_gap_20260731.md`)**: `capit_fired` trong
`data/golive_v23_status.json` là **điều kiện đúng của NGÀY CHẠY** (`breadth_today >= WASHOUT_GATE`,
tính lại từ đầu mỗi phiên), **KHÔNG PHẢI** cờ "đang giữ vị thế CAPIT". Đã tắt về `false` từ 07-29
(breadth phục hồi dưới gate) — nhưng **vị thế THẬT vẫn còn giữ đủ**, verify trực tiếp DNSE API
2026-07-31 03:00 ICT: **5 mã** SAB/SIP/VNM/PVT/**NCT** (rổ đúng gồm NCT — bản trước ghi thiếu, chỉ
4 mã), SpaceX + ZaloPay đều chưa bán mã nào. Từ 07-29 tới nay **mọi kênh báo cáo (Telegram, EOD,
prompt DollarBill) đã im lặng hoàn toàn về CAPIT** vì đều gate theo `capit_fired` — đây là lỗ hổng
thông tin thật (user phát hiện 07-31), đang xử lý (xem việc đang chạy bên dưới).
**Việc đang triển khai** (dispatch `Taylor`, user duyệt 07-31): (1) `data/capit_episode.json` ghi
1 episode khi fire lần đầu, đóng khi exit thật; (2) đổi mọi kênh báo cáo sang
`capit_fired OR capit_episode_open`; (3) fail-closed interpreter trong `golive_recommend_v23.py`
(chặn ghi đè artifact khi sai pandas version — chặn nguyên nhân sự cố (c) cùng job); (4) đổi tên
`capit_fired`→`capit_signal_today` cho đúng ngữ nghĩa; (5) cập nhật data_registry. Kiểm tra lại
`kb/incidents/2026-07/` khi cần xem đã đóng chưa.

Rổ hiện tại luôn đọc `data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`,
`capit_dd_excluded`) — ĐỪNG chép cứng danh sách mã vào đây, rổ đổi theo phiên (đã từng sai lệch:
bản trước ghi cứng NCT/SAB dù rổ đã đổi — con số 5 mã ở trên là XÁC NHẬN MỘT LẦN có mốc thời gian
07-31, không phải danh sách sống). Nguồn vốn: `NAV_book_LAG × capit_size` (user chốt 07-20). 2
điểm cần nhớ: (a) sát biên "grind" (91 vs cửa sổ 20-90 phiên — lệch 1 phiên đổi size full 0,75 vs
0,375); (b) dd52w lúc fire (~-7%) nông nhất lịch sử 2014-2026 (kỷ lục cũ -7,4%) — ngoài rìa mẫu dữ
liệu đã biết.

**PNJ EXCLUDED khỏi rổ CAPIT** (due-diligence gate, 2026-07-20, quant-skeptic CONFIRMED cao — PNJ
xếp HẠNG 1 pool CAPIT 07-17 nếu không gate). PNJ khủng hoảng thật (lãnh đạo bị bắt buôn lậu kim
cương, giá sập ~-32%, kết luận AMBIGUOUS trong `calculated_fear_state_backstop.md` §7, cổng xác
nhận = BCTC Q3/2026 ~cuối tháng 10). Cơ chế `anomaly_scan.py` → `data/anomaly_flags.json` (gate
CHUNG theo cờ, không hardcode tên, **TTL 30 ngày** — cờ PNJ tự hết hạn ~08-23 nếu không có
alert mới trước cổng xác nhận thật tháng 10, cần theo dõi không để hở gate) — wire vào
`ops_health_check.sh` 08:20+12:45. `capit_dd_excluded` hiện tại đọc `data/golive_v23_status.json`
(PNJ + CSV loại tính đến giờ — danh sách có thể mở rộng, đừng chép cứng). Giới hạn: gate KHÔNG
backtest được (n=1) — coi là bảo hiểm chi phí chưa đo được, không phải alpha đã kiểm chứng; loại
1 mã thanh khoản khỏi rổ có thể làm nặng thêm vấn đề sizing của mã còn lại trong rổ — theo dõi ADV
cap thật (`capit_adv_caps`) khi fire.
> ⚠️ File này inject vào MỌI phiên/dispatch qua `context_pack.md` (ngưỡng cứng **45KB** — nâng
> từ 20KB 2026-07-30, `context_pack.md` thật ~39KB sau trim #3 không xuống được 20KB mà không
> cắt fact quyết định; file này riêng có ngưỡng phụ 28KB — kiểm tra SAME-DAY qua `kb_nightly.sh`,
> không chỉ Thứ Sáu, xem §Cron) — giữ NHỎ, chỉ mục LIVE/đang-mở. Dự án ĐÓNG → 1 file
> `kb/projects/<slug>.md` + 1 dòng `kb/projects/INDEX.md`. Sự cố ĐÃ GIẢI QUYẾT → **1-2 câu + pointer
> `kb/incidents/`** ngay khi đóng, không giữ play-by-play (bài học phình 0→36KB trong 3 tuần,
> 2026-07-17).

## Due-diligence MẶC ĐỊNH cho MỌI ứng cử viên mua — ĐÃ TRIỂN KHAI (mandate 2026-07-21, XONG cùng ngày)
`trading_bot/due_diligence.py` — thuần thông tin (không chặn/đổi sizing), 5 trục (thanh khoản/
valuation/PEAD-surprise cơ học/anomaly/FA thô), wire ở 4 choke-point: `golive_recommend_v23.py`
(mọi rec), `send_plan_report.sh` (mọi lệnh buy plan T+1), `eod_trading_report.sh`,
`dc_book_waterfall_paper.py`. Self-check 18/18 PASS + reproduce đúng 3 case tay (TMG/IVS/TRC).
KHÔNG wire `paper_main_probe_plan.py` (basket hardcode 6 mã, không có bước chọn mã). Ghi chú:
trần %ADV LAG = gate CỨNG live riêng (`cap_lag_orders`, `bot_execute.py:387`, fail-closed, từ
2026-07-22) — KHÁC với P1 domain-constraint layer phía trên (đó là gate rating≤3).

## Vận hành/kiến trúc daemon — trạng thái ổn định (không đổi gần đây)
Remote-control daemon `mike@Mike.service` tắt hẳn từ 07-07 (user chỉ dùng Discord qua
`ccdb-mike.service`, 2 service độc lập; bật lại: `systemctl --user enable --now mike@Mike.service`).
Model mặc định Mike = Sonnet 5, đồng bộ ở 3 tầng config (`.claude/settings.json` +
`ccdb-mike/.env` + `sessions.db` bảng `settings` — DB là nguồn ưu tiên cao nhất; sự cố malformed
model-string qua `/model` command đã fix ở tầng validation, xem [[reference-ccdb-model-config-layers]]
+ [[project-discord-only-workflow-remote-control-disabled]] trong memory Mike).

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (opus, hạ từ
fable 2026-07-17 — xem `kb/incidents/2026-07/2026-07-17-model-tier-drift-fable.md`) chẩn đoán + sửa + verify + báo
Trading Daily; đã wire vào `ops_health_check.sh` (08:20/12:45) và
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
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking target
  **70%** của phần idle cash khi BAL/LAG rỗng (`trading_rules.json` v2.1 `neutral_parking`,
  đổi ≠0.70 cần `risk_dial_override` xác nhận, không thì Mafee tự block plan) — chọn 70% thay
  vì 93.8% go-live gốc vì backtest risk-adjusted thắng rõ (Sharpe 1.78 vs 1.66, job
  `Taylor_20260703_130720`, quant-skeptic CONFIRMED). run_bot.sh 09:05 ICT mỗi T2-T6. NAV/vị
  thế hiện tại: đọc `nav_history_SpaceX.csv` hoặc EOD report mới nhất (Trading report topic),
  đừng dùng số hardcode cũ ở đây. Chuỗi sự cố go-live tuần đầu (trim 07-06, bug tên file plan
  `_v2`, T+2 sellable-chiều, giá EOD sai nguồn) đều đã fix+verify — chi tiết: `kb/incidents/index.md`
  (tìm "2026-07-06").
- **ZaloPay** (DNSE 0001743768, tên cũ `dnse_main`): V2.4 LIVE từ 2026-07-06, **CASH-ONLY**
  (không margin) — cơ hội so sánh V2.4 có/không margin. **DGC (vị thế legacy) EXCLUDED khỏi
  rebalancing** qua `excluded_tickers` (`secrets/trading_bot_accounts.json`, enforce cứng ở
  `bot_execute.py`) — lý do: HOSE hạn chế giao dịch (lãnh đạo bị khởi tố 17/03/2026, ước gỡ
  hạn chế ~11-12/2026); Taylor giữ vì lý do đầu tư riêng, không phải kẹt thanh khoản. Sizing
  V2.4 dùng `active_nav` (`bin/compute_active_nav.py --account ZaloPay`), không dùng NAV tổng.
  Cơ chế `excluded_tickers` viết tổng quát cho account tương lai có vị thế legacy tương tự —
  `kb/coding_guidelines.md` §7. Transition 5 ngày (07-07→07-13, bán dần vị thế cũ sang
  custom30V) đã XONG — `kb/projects/zalopay-transition-0713.md`. Known gap: `daily_nav_snapshot.py`
  chưa tính đúng P&L cho vị thế legacy (NAV/active_nav đã đúng, chỉ breakdown P&L báo cáo còn thiếu).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

### Trứng vàng DNSE (idle-cash off-book) — ĐÃ ĐÓNG HẲN cả 2 account (2026-07-23)
`manual_offbook_assets_vnd=0` vĩnh viễn cả 2 account — KHÔNG đề xuất "rút thêm Trứng vàng" bù cash
gap khi lập plan; thiếu cash → tự SHRINK lệnh. Cơ chế field vẫn giữ cho account tương lai có
off-book asset tương tự. Chi tiết: [[project-dnse-trung-vang-offbook-assets]] (memory Mike).

## Đang R&D (mọi mục PAPER-ONLY trừ khi ghi rõ LIVE — chi tiết đầy đủ: bus finding của Taylor + `kb/incidents/index.md`)
- **Insider-sell WATCH shadow (`insider_flags.py`)** (WATCH-only, chưa wire due-diligence, từ
  2026-07-29): cờ bán ròng nội bộ ≥1% CP lưu hành/90 ngày (chỉ `event_code IN ('DDIND','DDRP')`,
  TTL 90d). Scoping (job Taylor_20260729_015830 + Phụ lục A `_032713`) kết luận GO: overlap thấp
  với `anomaly_scan`/`forensic_flags` (7,1-21,7%), lift phần riêng 2,08× (z=5,74), ổn định IS/OOS;
  hai cờ bắn ở hai thời điểm khác nhau (insider sớm hơn ~2 tháng so với anomaly). Đang dựng
  writer/reader (job Taylor_20260729_104614). **Sàn review ~2026-08-29 (≥1 tháng shadow), trần
  ~2026-09-15.** Điều kiện TIẾP TỤC (wire vào due-diligence report như dòng bằng chứng): cadence
  refresh bảng nguồn xác nhận chạy đều (bq_admin đang fix bug tính đến 07-29) + shadow log sạch
  (không false-trigger bất thường) + qua quant-skeptic trước khi vào due-diligence chính thức.
  Điều kiện NGỪNG: bq_admin không fix xong cadence (bảng đứng im, cờ đóng băng) hoặc shadow log
  noise quá tải (~>5 mã/tháng cần review tay, vượt xa ước tính ~3/tháng). **Tuyệt đối không hard-
  exclude ở bất kỳ giai đoạn nào** — 85% mã bị cờ không sập (§3.5 research file), chỉ là dòng bằng
  chứng WATCH cho người duyệt plan cân nhắc. Research đầy đủ:
  `mike/agents/Taylor/research/insider_transaction_scoping_20260729.md`.
- **EXTREME-regime gate** (paper `main` only, từ 07-01): stress PASS 24/24, target checkpoint
  ~2026-07-28 **ĐÃ QUA, CHƯA XÁC NHẬN trạng thái** (không tìm thấy sign-off/close nào — cần dispatch
  Taylor kiểm tra lại, không tự đoán). Điều kiện LIVE (chưa đổi): 0 false-trigger ~4 tuần benign +
  không can thiệp NORMAL-path + user sign-off. ⚠️ audit `Winston_20260712_142100` (M5, xem
  `kb/incidents/index.md`) từng nêu `executor.py` đọc `ticker_prune.parquet` monolith đông cứng từ 06-26
  khiến rvol/prior_close trial này tính trên giá cũ 2+ tuần — bug monolith đã **FIXED 07-13**
  (Winston_20260713_143546), câu hỏi mở CHỈ còn là evidence giai đoạn 06-26→07-13 có giá trị
  không, cần Taylor xác nhận cùng lúc. KHÔNG bật ở live cho tới khi có xác nhận.
- **Vol-scale buy chase-cap patch#3** (paper `main` only, từ 07-01, k=2.0/ceil=0.04): stress PASS
  15/15, target checkpoint ~2026-07-14 **ĐÃ QUA HƠN 2 TUẦN, CHƯA XÁC NHẬN**. Điều kiện LIVE (chưa
  đổi): paper sạch, không đụng NORMAL-path ngày non-gap, skeptic rerun REAL-fill, user sign-off.
  Cùng câu hỏi M5 (evidence 06-26→07-13) áp dụng. KHÔNG bật ở live cho tới khi có xác nhận.
- **Sector sweep #10+**: chờ Mike dispatch.
- **Fill-timing khung giờ** (BUY 11:15 / SELL open): edge thật đo được (+17.6bps BUY t=12.0,
  +11.8bps SELL), KHÔNG flip `fill_timing_live_gate` — cần ≥5 phiên paper có BUY fill trong cửa sổ
  + 0 reject + không lệnh treo → quant-skeptic → user sign-off (điều kiện chốt sau audit fill thật
  `Taylor_20260709_101602`, phát hiện `execution_quality_review.py` từng đếm nhầm lệnh LIVE làm
  "98% adherence" giả — evidence-rate thật ≈0 khi đó). Checkpoint tự nhiên ~cuối 07 **ĐÃ TỚI, CHƯA
  XÁC NHẬN đủ điều kiện chưa** — cần Taylor kiểm tra số phiên đã đạt. Option: pilot ZaloPay trước
  SpaceX — chưa quyết.
- **V2.5**: R&D-complete, DISABLED. Reminder 2026-07-07: Mike hỏi user go-ahead integration.
- **DC-book (ConvergePort) NEUTRAL idle-cash waterfall** (paper `main` only, từ 07-06): thứ tự ưu
  tiên giải ngân **BAL/LAG (full trước) → DC book (double-confirm sector-lens BUY ∧ 8L rating≤2,
  capacity ~10-15B ex-DHG) → custom30V**; reverse-unwind khi BAL/LAG có deal lại. Backtest: +5.0pp
  sleeve parking (~+3.5pp/năm SpaceX-now), nhưng DSR phần excess chỉ 0.775 (<0.95 ngưỡng an toàn) —
  bảo hiểm hợp lý, CHƯA phải alpha tin cậy cao → lý do bắt buộc paper trước. Trong EOD daily report.
  Review = EVENT-ANCHORED (khi chu kỳ reverse-unwind đầu tiên hoàn tất + settle 4-6 tuần), sàn
  ~2 tháng, trần ~2026-10-06 (trượt theo nếu LAG refill trượt lịch).
  ⚠️ **Bug đã biết, sửa TẠI mốc review (không sửa sớm — user chốt 07-13, muốn quan sát whipsaw thật
  trước)**: paper sleeve dùng trigger NHỊ PHÂN thay vì spec đúng (DC book chạy liên tục trên residual)
  → hiện TỆ HƠN baseline không-DC (CAGR 27.26%/DD−17.8%/Calmar 1.53/turnover 20.7× vs spec đúng
  27.56%/−15.5%/1.77/3.18×). 4 việc khi tới review, theo thứ tự: (1) đổi sang continuous-residual
  trigger — bug thực chất, ưu tiên nhất; (2) đồng bộ rebalance vào q2m5 (giảm whipsaw ~4 lần);
  (3) cap gộp 0.15/tên (chống trùng DC↔custom30V); (4) liquidity floor 3B thay hard-exclude DHG.
  4 góc khác đã kiểm tra kỹ, không còn dư địa cải thiện — không cần backtest thêm cho chúng.

## Workflow ngày trading (SpaceX/ZaloPay, T2-T6, giờ ICT)
Timeline đầy đủ (giờ từng bước, checker gì, ranh giới tự sửa) đã chuẩn tắc hoá ở
**`kb/ops_runbook.md`** — đọc đó, đừng lặp lại ở đây (từng trùng ~25 dòng, dọn 2026-07-28).
Phần dưới đây là quy tắc **Discord topic routing** — KHÔNG có trong ops_runbook.md, chỉ ở đây.

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
  này qua `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/incidents/index.md`.
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
21:00 ICT (+ second-chance 23:00) giờ verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày kỳ vọng qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Nếu thiếu/sai ngày/hỏng schema →
**ESCALATE thật**: Telegram + Discord (như cũ) VÀ ghi bus event `question` (`plan-t1-not-ready`) để
Mike tự đọc được ở phiên sau, không chỉ trông chờ user thấy Telegram rồi tới hỏi. KHÔNG tự động
retry/re-dispatch (an toàn hơn — con người quyết định bước tiếp theo, đúng nguyên tắc human-in-the-loop
của toàn hệ thống).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory, **check context_pack.md/MIKE.md ngưỡng cứng MỖI đêm** (thêm 2026-07-30 — trước chỉ check Thứ Sáu; breach ngày thường → escalate question + Telegram cùng đêm, KHÔNG chờ tuần) |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review (đầy đủ) |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Sự cố đã đóng (cập nhật 2026-07-30) — rút gọn, chi tiết đầy đủ `kb/incidents/index.md`
Audit cron C1/H2 (2026-07-12), BQ cache monolith (2026-07-13), cross-account contamination
`reconcile_equity.py`/`verify_account_snapshot.py` (2026-07-19) — tất cả FIXED+VERIFIED. **Còn
treo thật** (1 mục, ưu tiên thấp): dọn crontab paper-trading lạc hậu — diff có sẵn
(`Winston_20260712_151206`), chưa áp dụng.

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.60% / Sharpe 1.84 / DD −17.5% / Calmar 1.58** — pin CHÍNH THỨC từ
  **2026-07-29**, đo trên **`universe_pit`** (point-in-time, không look-ahead). quant-skeptic
  **CONFIRMED (high)**. Re-pin do **VINTAGE DỮ LIỆU, KHÔNG đổi mô hình** (restate DT5G + trôi
  corp-action + `ticker_prune` mất 58 mã) — phân rã đủ 3 hiệu ứng + AS-OF snapshot pin ở
  `data/results_registry.md` (mục **2026-07-29 RE-PIN R3 SAU RESTATE DT5G**), KHÔNG lặp lại ở đây.
  **Số lịch sử KHÁC VINTAGE, không so trực tiếp**: 27.16%/1.81/−18.1%/1.50 (pin 07-22, đã mất, không
  tái lập được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`).
  ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho
  CAPIT pool/maturity. Lỗi fidelity `liq<=0` vẫn MỞ ⇒ khoảng kỳ vọng trung thực **[~27,6%; ~31,3%]**,
  **anchor DD ~−30%** (KHÔNG phải −17,5%).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

**MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12)** — thay đổi production chính thức, không phải "thử bị loại":
`MOMENTUM_N`+`MOMENTUM_S` gỡ khỏi `TIER_BAL` (giữ `MOMENTUM`/`MEGA` generic — vẫn đóng góp thật).
Lý do + chuỗi R&D: `kb/projects/momentum-deals.md`, `plan_close_mom_20260712.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State live hôm nay = `kb/current_ops.md` / `golive_state_today` (fact động, KHÔNG pin ở đây).

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- **`data/BOT_STOP`** = kill-switch tức thì.
- Giờ chuẩn tắc chuỗi ngày trading (T2-T6) + xử lý khi lỗi: `kb/ops_runbook.md`. Routing Discord:
  `kb/current_ops.md`. BQ cache / auto-OTP / PHS: `kb/KNOWLEDGE.md` §4.

### Kiến trúc fleet
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.
- Daemon / dispatch / escalate (cơ chế đầy đủ): `MIKE.md` + `kb/KNOWLEDGE.md` §3.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể: báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (ca Wave1/H8a-tiebreaker 2026-07-05: `kb/KNOWLEDGE.md` §8). V2.4/R3 đã qua chuẩn
   DSR/PBO (DSR≈1.0, PBO≈0.20 — `data/results_registry.md` mục "DSR / PBO Robustness Annex").

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 (đã đóng, kết luận lens/tilt): `kb/KNOWLEDGE.md` §7.

## Dự án đã đóng — chi tiết theo yêu cầu (đọc khi cần: `cat kb/projects/<file>.md`)
- 2026-07-28 **DGC + TV1 fear-buy discretionary due-diligence** → `kb/projects/dgc-tv1-fearbuy-discretionary.md` — XONG (research) — cả 2 QUALIFIED YES, đã chuyển sang theo dõi discretionary riêng ngoài current_ops.md (TV1: context_planning_mini.md + plan file; DGC: excluded_tickers + finding Taylor).
- 2026-07-21 **LAG 07-24 (IVS/TMG/TRC)** → `kb/projects/lag-0724-ivs-tmg-trc.md` — XONG — user chốt phương án C (chỉ mua TRC), gate %ADV LIVE wired, lọc thanh khoản LAG tầng tín hiệu wired, trần vị thế LAG=12 xác nhận là hệ quả tiền chứ không phải tham số riêng — quyết định bound tới phiên 07-24 đã qua.
- 2026-07-20 **Deposit-rate auto-crosscheck automation** → `kb/projects/deposit-rate-autocheck.md` — DONE — refresh_deposit_rate_vn.sh tự dispatch Winston xác nhận + ghi (không cần người), 10 vòng quant-skeptic REFUTED→fix→re-review (mỗi vòng 1 lỗi thật, khác nhau) rồi CONFIRMED — kể cả 1 bug thật trong `deposit_rate_vn.current_deposit_rate()` (consumer, không phải chỉ writer).
- 2026-07-17 **DCF upgrade (earning-power · GDP terminal-g · refresh-gate)** → `kb/projects/dcf-earning-power-upgrade.md` — TRIỂN KHAI XONG — Việc1 earning-power NO-GO (giữ FCFE); Việc3 `cap_rf` = default hiển thị `dcf_valuation.py` (level fix, không alpha, DCF non-decisional); Việc2 refresh-gate cron LIVE ngày 11. quant-skeptic CONFIRMED.
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
