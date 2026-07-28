# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-28 (token-cost trim: Trứng vàng staleness fix, workflow/CAPIT/universe_pit/R&D compression, ~9KB saved)

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
commit `0bfbdfe`, cả 2 user duyệt + selfcheck pass). **Cổng CAPIT §4.4 vẫn ĐÓNG riêng** — breadth/pool
CAPIT vẫn đọc `ticker_prune` có chủ ý tới khi hiệu chuẩn lại (2 vòng đo đều thất bại cấu trúc tìm
ngưỡng bảo toàn; cấm cutover khi `capit_fired=true`). R3 (allocator gate) đã cutover chính thức — xem
số liệu ở "Tri thức chung của đội" bên dưới. Còn lại: G5 shadow ≥10 phiên, G6 re-pin R3, G7 N-trial
review, G8 data/cron-registry gate, G9 quant-skeptic full review. Tài liệu đầy đủ (kiến trúc/vận
hành/Q&A gốc, bảng G0-G9): `mike/agents/Taylor/research/ticker_prune_replacement_plan.md` +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` +
`.../ticker_prune_universe_QA_bq_admin_20260722.md`.

## CAPIT (bear-washout) — ĐÃ FIRE từ 07-20/07-21, đang giải ngân dở (cập nhật 2026-07-22)
`capit_fired=true` từ 07-20 (`data/golive_v23_status.json`, breadth_oversold vượt xa
washout_gate=0,3). SAB/SIP/VNM đã khớp; PVT/NCT còn vướng (chờ trần giá/quota) — theo dõi qua EOD
report. Nguồn vốn: `NAV_book_LAG × capit_size` (user chốt 07-20). 2 điểm cần nhớ: (a) sát biên
"grind" (91 vs cửa sổ 20-90 phiên — lệch 1 phiên đổi size full 0,75 vs 0,375); (b) dd52w lúc fire
(~-7%) nông nhất lịch sử 2014-2026 (kỷ lục cũ -7,4%) — ngoài rìa mẫu dữ liệu đã biết.

**PNJ EXCLUDED khỏi rổ CAPIT** (due-diligence gate, 2026-07-20, quant-skeptic CONFIRMED cao — PNJ
xếp HẠNG 1 pool CAPIT 07-17 nếu không gate). PNJ khủng hoảng thật (lãnh đạo bị bắt buôn lậu kim
cương, giá sập ~-32%, kết luận AMBIGUOUS trong `calculated_fear_state_backstop.md` §7, cổng xác
nhận = BCTC Q3/2026 ~cuối tháng 10). Cơ chế `anomaly_scan.py` → `data/anomaly_flags.json` (gate
CHUNG theo cờ, không hardcode tên, **TTL 30 ngày** — cờ PNJ tự hết hạn ~08-23 nếu không có
alert mới trước cổng xác nhận thật tháng 10, cần theo dõi không để hở gate) — wire vào
`ops_health_check.sh` 08:20+12:45. Rổ hiện tại (nếu
fire hôm nay): NCT, PVT, SAB, VNM (PNJ đã loại). Giới hạn: gate KHÔNG backtest được (n=1) — coi là
bảo hiểm chi phí chưa đo được, không phải alpha đã kiểm chứng; rổ neo vào NCT (ADV 2,18 tỷ/ngày,
sát sàn 2 tỷ) sau khi loại PNJ — vấn đề sizing NCT có sẵn từ trước, cần theo dõi nếu fire thật.
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
