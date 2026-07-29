# Mike fleet — context pack (v1491)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-29T09:04:14] Winston/finding — paper-report-tre-2-phien: root cause + fix cron 15:20->16:00: {"trieu_chung": "Report 2026-07-29 hien muc (7) Capitulation + (8) Engine-room asof 2026-07-27 (tre 2 phien), muc (6) ORB asof 2026-07-28 (tre 1 phien) — cung n …
- [2026-07-29T10:53:13] Winston/finding — paper-pipeline 19:00 — phan loai A/B/C + doi gio dung cho: {"job": "Winston_20260729_103816", "yeu_cau_goc": "doi TAT CA paper report/pipeline sang 19:00 de co du lieu cuoi ngay", "ket_luan": "BAC BO MOT PHAN — chi 2/15 …
- [2026-07-29T10:55:56] Taylor/finding — insider_flags.py WATCH-only da dung xong (shadow) — selftest 8/8 + selfcheck 15/15 + cong freshness PASS; de xuat cron 18:45 ICT T2-T6, CHUA wire: {"job": "Taylor_20260729_104614", "buoc": "§5.3 — dung ha tang insider_flags.py WATCH-only, chay shadow", "trang_thai": "XONG code + selfcheck; CHUA wire vao ba …
- [2026-07-29T11:11:22] Winston/finding — new-listings-daily: {"date": "2026-07-29", "lookback_days": 90, "total_new": 1, "needs_manual_rating": 0, "fresh_ipo": 0, "research_queue": [], "snapshot": "/home/trido/thanhdt/Wor …
- [2026-07-29T11:16:51] Winston/finding — dt5g_live co WRITER THU HAI: pipeline kaffa_v2 (team du lieu) ghi truc tiep bang production tu 2026-06-08: {"priority": "HIGH", "table": "tav2_bq.vnindex_5state_dt5g_live", "writer_found": true, "source": "/workspace/kaffa_v2/worker/tasks/market_state_tasks.py :: tas …
- [2026-07-29T11:56:27] Winston/finding — kaffa_v2 DT5G writer: KHONG co LLM, 2 engine bit-identical cung vintage: {"job": "Winston_20260729_114625", "report": "mike/agents/Winston/kaffa_dt5g_writer_taskspec_20260729.md", "dinh_chinh_3_gia_dinh": {"ton_token_claude": "SAI -  …
- [2026-07-29T11:57:01] Winston/answer — Task-spec de xuat cho hainguyen/bq_admin ve writer thu hai dt5g_live: {"job": "Winston_20260729_114625", "report_day_du": "mike/agents/Winston/kaffa_dt5g_writer_taskspec_20260729.md", "message_gui_thang_cho_ho": "co san o muc 6 cu …
- [2026-07-29T12:07:36] DollarBill/decision — plan-2026-07-30-SpaceX: {"account": "SpaceX", "plan_date": "2026-07-30", "action": "HOLD_ALL", "orders": 0, "nav_vnd": 900082648, "cash_vnd": 4527648, "state": "NEUTRAL(3)", "lag_new": …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-28 (token-cost trim: Trứng vàng staleness fix, workflow/CAPIT/universe_pit/R&D compression, ~9KB saved)

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

## Dự án thay thế `ticker_prune` → `universe_pit` — G0-G3 XONG, R3 đã cutover chính thức (2026-07-22)
`ticker_prune` không có quản trị (curation circular-bias, không tái lập được) → team tự xây
`universe_pit` (point-in-time từ `tav2_bq.ticker`, B3=1,0 tỷ VND/ngày). **Cổng cứng §3.2b/Q9 ĐÃ
MỞ từ 2026-07-22** (user chốt A′+Q-C, không Q-B, sau khi G2b đo xong độ rò chất lượng) — P1-P3 đã
cutover production (due_diligence.py, custom30V→`universe_pit_q` commit `ce7d457`, golive_recommend_v23
commit `0bfbdfe`, cả 2 user duyệt + selfcheck pass). **Cổng CAPIT §4.4 = NỬA XONG (G4)**: breadth ĐÃ
cutover sang `universe_pit` (`CAPIT_BREADTH_SOURCE=pit`, top-250, washout_gate 0,31, commit `dcee252`,
selfcheck 26/26, quant-skeptic CONFIRMED, A/B live 0 đồng); **pool pbz + ADV cap CỐ Ý còn ghim
`ticker_prune`** (pool `pit` đổi rổ đang giải ngân — tách khỏi migration, 2 vòng đo đều thất bại cấu
trúc tìm ngưỡng bảo toàn cho pool) — cấm cutover pool khi `capit_fired=true`. R3 (allocator gate) đã
cutover chính thức — xem số liệu ở "Tri thức chung của đội" bên dưới. Còn lại: G5 shadow ≥10 phiên,
G6 re-pin R3, G7 N-trial review, G8 data/cron-registry gate, G9 quant-skeptic full review. Tài liệu
đầy đủ (kiến trúc/vận
hành/Q&A gốc, bảng G0-G9): `mike/agents/Taylor/research/ticker_prune_replacement_plan.md` +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` +
`.../ticker_prune_universe_QA_bq_admin_20260722.md`.

## CAPIT (bear-washout) — ĐÃ FIRE từ 07-20/07-21, đang giải ngân dở (cập nhật 2026-07-22)
`capit_fired=true` từ 07-20 (`data/golive_v23_status.json`, breadth_oversold vượt xa
washout_gate=0,3). Rổ hiện tại luôn đọc `data/golive_v23_status.json` (`n_capit_basket`,
`capit_adv_caps`, `capit_dd_excluded`) — ĐỪNG chép cứng danh sách mã vào đây, rổ đổi theo phiên (đã
từng sai lệch: bản trước ghi cứng NCT/SAB dù rổ đã đổi). Nguồn vốn: `NAV_book_LAG × capit_size`
(user chốt 07-20). 2 điểm cần nhớ: (a) sát biên
"grind" (91 vs cửa sổ 20-90 phiên — lệch 1 phiên đổi size full 0,75 vs 0,375); (b) dd52w lúc fire
(~-7%) nông nhất lịch sử 2014-2026 (kỷ lục cũ -7,4%) — ngoài rìa mẫu dữ liệu đã biết.

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
> ⚠️ File này inject vào MỌI phiên/dispatch — giữ NHỎ. Chỉ để mục LIVE/đang-mở. Dự án ĐÓNG (NO-GO/
> KHÉP KÍN/XONG) → chuyển thành 1 file `kb/projects/<slug>.md` + thêm 1 dòng vào `kb/projects/INDEX.md`
> (INDEX được inject, chi tiết chỉ `cat` khi cần). Đừng để nhật ký dự án đã đóng tích lại ở đây.
> ⚠️ Sự cố ĐÃ GIẢI QUYẾT (fix xong + verify) → rút về **1-2 câu + pointer `kb/INCIDENTS.md`**
> ngay khi đóng, KHÔNG giữ nguyên play-by-play ở đây "cho chắc" (bài học sự cố model-drift/
> context-bloat 2026-07-17 — file này phình 0→36KB trong 3 tuần chủ yếu vì narrative sự cố đã
> đóng không được rút gọn, đè phí token lên MỌI dispatch qua `context_pack.md`).

## Due-diligence MẶC ĐỊNH cho MỌI ứng cử viên mua — mandate mới (user, 2026-07-21)
User chỉ đạo: bất kỳ mã nào trở thành ứng cử viên mua (mọi book: BAL/LAG/CAPIT/DC-book/
custom30V rotation) phải qua bước due-diligence — không chỉ để bảo vệ giao dịch đó, mà còn
để LỘ RA điểm hệ thống cần cải thiện (như lỗ hổng %ADV cho LAG vừa phát hiện ở trên). **Mặc
định trong quy trình cho CẢ production lẫn paper-trading**, không phải opt-in/chỉ khi có cờ
đặc biệt. Đây là mở rộng của due-diligence trigger hiện có (forensic_flags, >7% NAV,
first-time-buy, DCF=RICH+robust override, anomaly Tier-H — vẫn giữ nguyên làm HARD gate) sang
diện rộng hơn: MỌI candidate, không chỉ các case có cờ. Đã dispatch Taylor thiết kế + triển
khai (xem bus finding sau 2026-07-21 13:xx) — theo dõi kết quả trước khi coi mandate này đã
xong.

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
fable 2026-07-17 — xem `kb/INCIDENTS.md` "Model-tier drift") chẩn đoán + sửa + verify + báo
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
  `_v2`, T+2 sellable-chiều, giá EOD sai nguồn) đều đã fix+verify — chi tiết: `kb/INCIDENTS.md`
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

### Trứng vàng DNSE (idle-cash off-book) — ĐÃ ĐÓNG HẲN, cả 2 account (cập nhật 2026-07-23)
SpaceX + ZaloPay đều `manual_offbook_assets_vnd=0` — rút hết vĩnh viễn, KHÔNG phải "tạm hết".
KHÔNG giả định/đề xuất "user rút thêm Trứng vàng" để bù cash gap khi lập plan — nguồn này không
còn tồn tại, không phải ATM nạp lại theo nhu cầu. Thiếu cash → tự SHRINK/loại bớt lệnh, không
yêu cầu user nạp thêm. Cơ chế field (`manual_offbook_assets_vnd/_asof/_note` trong
`secrets/trading_bot_accounts.json`, wire vào `daily_nav_snapshot.py`/`compute_active_nav.py`)
vẫn còn đó cho account tương lai có off-book asset tương tự — nếu 1 account MỚI thật sự dùng
Trứng vàng, cập nhật lại field NGAY khi nạp/rút (nếu quên → NAV/active_nav đếm trùng, không rủi
ro tiền thật vì executor check cash/ppse live). Chi tiết đầy đủ: [[project-dnse-trung-vang-offbook-assets]] (memory Mike) + `kb/context_planning_mini.md`.

## Đang R&D (mọi mục PAPER-ONLY trừ khi ghi rõ LIVE — chi tiết đầy đủ: bus finding của Taylor + `kb/INCIDENTS.md`)
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
- **EXTREME-regime gate** (paper `main` only, từ 07-01): stress PASS 24/24. Target kết thúc
  ~2026-07-28 (~20 phiên). Trước LIVE cần: 0 false-trigger ~4 tuần, không đụng NORMAL-path,
  user sign-off. KHÔNG bật ở live.
- **Vol-scale buy chase-cap patch#3** (paper `main` only, từ 07-01, k=2.0/ceil=0.04): stress PASS
  15/15. Target kết thúc ~2026-07-14. Trước LIVE cần: paper sạch, không đụng NORMAL-path ngày
  non-gap, skeptic rerun REAL-fill, user sign-off. KHÔNG bật ở live.
- **Sector sweep #10+**: chờ Mike dispatch.
- **Fill-timing khung giờ** (BUY 11:15 / SELL open): edge thật đo được (+17.6bps BUY t=12.0,
  +11.8bps SELL) nhưng KHÔNG flip `fill_timing_live_gate` — cần ~3-4 tuần paper fill để
  `execution_quality_review.py` xác nhận NET-of-noise (noise 110-220bps >> edge 17bps). Checkpoint
  tự nhiên ~cuối tháng 7.
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
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Sự cố đã đóng, chỉ còn 2 mục thật sự CÒN TREO (rút gọn 2026-07-17, chi tiết đầy đủ `kb/INCIDENTS.md`)
Audit cron 07-12 (C1 DT5G-cache-bug + H2 freshness-false-block) — cả 2 **FIXED+VERIFIED**
(commit `4995262`, `6459b6d`, quant-skeptic CONFIRMED). BQ cache monolith 07-13 (27 file đọc
nhầm `ticker_prune.parquet` chết) — **FIXED** (Winston_20260713_143546, archived). 2026-07-14
HOLD — 1 ngày đã qua, không còn ảnh hưởng vận hành (DollarBill tự tính lại plan mỗi ngày).
Cross-account contamination trong `reconcile_equity.py`/`verify_account_snapshot.py` (phát
hiện 2026-07-19 khi Taylor soạn báo cáo tuần 07-13→07-17, job `Taylor_20260719_055139`) —
**FIXED** cả 2 file (mirror đúng fix `daily_nav_snapshot.py` 07-06/07: filter theo account_no
tự tra config, raise nếu không lọc được thay vì âm thầm dùng nhầm account); thiếu 1 dòng NAV
ZaloPay 07-14 (no-plan day, không có journal) — backfill bằng vị thế THẬT từ `dnse_raw`
`kind=positions` + giá đóng cửa BQ 07-14 (963.451.542đ), verify khớp broker positions record.

**Còn treo thật** (2 mục):
1. Dọn crontab paper-trading lạc hậu — diff đã có (`Winston_20260712_151206`), **chưa áp dụng**
   (chờ Mike review). Ưu tiên thấp, không khẩn.
2. **`ticker_financial`/`ticker_prune` corruption 07-14/15** (rows 07-08→07-14 bị xóa/ghi đè
   upstream) — mitigations đã xong (depth-check gate commit `1b66428`, backup time-travel
   `*_ttbackup_fresh_20260714`), nhưng **quyết định khôi phục dữ liệu từ backup vẫn CHỜ USER**
   (đang hỏi BQ admin upstream). Mike KHÔNG tự khôi phục/tạm dừng cron cho tới khi có quyết
   định. Kiểm tra nhanh còn treo hay đã xong: `kb/INCIDENTS.md` (tìm "ticker_prune cũng bị
   corruption") + hỏi lại user nếu > vài ngày chưa thấy cập nhật ở đây.

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.16% / Sharpe 1.81 / DD −18.1% / Calmar 1.50** — pin CHÍNH THỨC từ
  **2026-07-22**, đo trên **`universe_pit`** (bảng đội tự sở hữu, point-in-time, không look-ahead;
  `UNIVERSE_SRC` default = `pit` trong `pt_v23_audit_2014.py`). threads=1, self-check 0 VND.
  **Số lịch sử (KHÔNG dùng để trích dẫn mới)**: 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`);
  cùng vintage cache 07-22 `ticker_prune` cho 27.95%/1.85/−18.4%/1.52 ⇒ Δ universe = **−0,79pp CAGR**,
  đúng hướng pre-register (khử curation/look-ahead bias của `ticker_prune`). quant-skeptic **CONFIRMED
  (high)**. ⚠️ Nhãn đúng khi trích dẫn: **MIXED-universe** — `universe_pit` cho *cổng quyết định*,
  `ticker_prune` vẫn cho *CAPIT pool / breadth / maturity* (~10 vị trí, cutover riêng). Lỗi fidelity
  `liq<=0` vẫn MỞ ⇒ khoảng kỳ vọng trung thực vẫn **[~27,2%; ~31,3%]**, anchor DD **~−30%**. Chi tiết:
  `data/results_registry.md` (mục 2026-07-22 CUTOVER R3 CHÍNH THỨC).
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
- **Workflow ngày trading đầy đủ** (T2-T6, giờ chuẩn tắc ở `kb/ops_runbook.md`): BQ
  freshness(19:00) → plan T+1(21:00) → preflight(08:45) → execute sáng(09:05) →
  resume chiều(13:00) → **EOD report(19:10, `eod_trading_report.sh`)**. Alert vận hành sống
  post vào Trading Daily (1521470705563340910); EOD/tuần/tháng vào Trading report
  (1522576692638388364) — xem chi tiết routing ở `kb/current_ops.md`.

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
