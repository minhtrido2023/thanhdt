# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-08-01 (token-cost trim #3, user mandate — phân loại lại "phải biết mỗi
> phiên" vs "đã xong/không cần đọc lại": chuyển R&D pipeline chi tiết → `kb/projects/
> rnd-pipeline-tracker.md`, universe_pit checklist G4-G9 → `kb/projects/universe-pit-migration.md`,
> CAPIT sizing-bug-đã-đóng → `kb/projects/capit-sizing-bug-0721.md`; nén due-diligence/onboarding/
> daemon-infra thành pointer 1-2 dòng — chi tiết đã có sẵn ở nơi khác, không mất thông tin, chỉ
> dời khỏi hot path đọc mỗi phiên. File giảm ~28KB → ~11KB, không giảm ngưỡng cứng 45KB nữa mà
> giảm THẬT nội dung.)

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking target
  **70%** của phần idle cash khi BAL/LAG rỗng (`trading_rules.json` v2.1 `neutral_parking`,
  đổi ≠0.70 cần `risk_dial_override` xác nhận, không thì Mafee tự block plan) — chọn 70% vì
  backtest risk-adjusted thắng rõ (Sharpe 1.78 vs 1.66, quant-skeptic CONFIRMED). run_bot.sh
  09:05 ICT mỗi T2-T6. NAV/vị thế hiện tại: đọc `nav_history_SpaceX.csv` hoặc EOD report mới
  nhất (Trading report topic), đừng dùng số hardcode cũ ở đây. Sự cố go-live tuần đầu: đã fix,
  chi tiết `kb/incidents/index.md` (tìm "2026-07-06").
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, **CASH-ONLY** (không margin). **DGC
  (vị thế legacy) EXCLUDED khỏi rebalancing** qua `excluded_tickers` — lý do: HOSE hạn chế giao
  dịch (lãnh đạo bị khởi tố 17/03/2026, ước gỡ hạn chế ~11-12/2026). Sizing dùng `active_nav`
  (`bin/compute_active_nav.py --account ZaloPay`), không dùng NAV tổng. Cơ chế `excluded_tickers`
  tổng quát cho account tương lai có vị thế legacy — `kb/coding_guidelines.md` §7. Known gap:
  `daily_nav_snapshot.py` chưa tính đúng P&L breakdown cho vị thế legacy (NAV/active_nav đúng).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.
- **Trứng vàng DNSE** (off-book idle cash): ĐÃ ĐÓNG HẲN cả 2 account (2026-07-23),
  `manual_offbook_assets_vnd=0` vĩnh viễn — KHÔNG đề xuất "rút thêm" bù cash gap. Chi tiết:
  [[project-dnse-trung-vang-offbook-assets]] (memory Mike).

## CAPIT (bear-washout) — vị thế THẬT đang giữ, `capit_fired` ≠ "đang giữ" (verify 2026-07-31)
⚠️ **`capit_fired`** trong `data/golive_v23_status.json` là điều kiện đúng CỦA NGÀY CHẠY
(tính lại mỗi phiên), **KHÔNG PHẢI** cờ "đang giữ vị thế". Rổ hiện tại LUÔN đọc
`data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`, `capit_dd_excluded`) — ĐỪNG
chép cứng danh sách mã, rổ đổi theo phiên. Nguồn vốn: `NAV_book_LAG × capit_size` (user chốt
07-20). Verify DNSE 07-31: **5 mã** SAB/SIP/VNM/PVT/NCT, cả 2 account chưa bán mã nào. Từ 07-29
mọi kênh báo cáo từng im lặng về CAPIT vì gate theo `capit_fired` (lỗ hổng đã phát hiện, đang xử
lý: `capit_episode.json` + đổi gate sang `capit_fired OR capit_episode_open` + đổi tên
`capit_fired`→`capit_signal_today`, dispatch Taylor, kiểm `kb/incidents/2026-07/` xem đã đóng
chưa). Sizing bug 07-21 (thiếu 87,1tr SpaceX) đã đóng, user chốt KHÔNG bù — chi tiết đầy đủ +
gate WARN-only mới: `kb/projects/capit-sizing-bug-0721.md`.

**PNJ EXCLUDED khỏi rổ CAPIT** (due-diligence gate, 2026-07-20, quant-skeptic CONFIRMED cao).
PNJ khủng hoảng thật (lãnh đạo bị bắt buôn lậu kim cương, giá sập ~-32%, AMBIGUOUS trong
`calculated_fear_state_backstop.md` §7, cổng xác nhận = BCTC Q3/2026 ~cuối tháng 10). Cờ
`anomaly_flags.json` **TTL 30 ngày** (~tự hết hạn 08-23 nếu không có alert mới trước cổng xác
nhận thật tháng 10 — cần theo dõi không để hở gate). Gate KHÔNG backtest được (n=1) — bảo hiểm
chi phí chưa đo được, không phải alpha đã kiểm chứng.

**Dự án thay `ticker_prune`→`universe_pit`**: R3/CAPIT-breadth đã cutover production (universe_pit
= nguồn chính thức). CAPIT pool + ADV cap CỐ Ý còn ghim `ticker_prune` (đổi rổ đang giải ngân giữa
chừng rủi ro cao, cấm cutover khi `capit_fired=true`). Checklist còn lại (G5 shadow/G7 N-trial/G8
data-registry gate/G9 quant-skeptic review + 3 việc mới từ audit 07-29): `kb/projects/
universe-pit-migration.md`.

## Domain-constraint layer — P1 LIVE, P0 shadow đang chạy (từ 2026-07-29, commit `d64717f`)
- **P1 (ACTIVE, LIVE)**: `filter_lag_rating_orders()` — lưới an toàn tầng ORDER cho gate 8L
  rating≤3 của LAG, vá lỗ hổng gate cũ chỉ sống ở tầng sinh tín hiệu. Verify: 14/14 + 22/22
  selfcheck, replay case TRC/MST bị chặn, 0 lệnh khác đổi trên 21 plan thật.
- **P0 — ĐÃ LÊN ACTIVE (HARD BLOCK), không còn WARN_ONLY** (từ 2026-08-04, commit `bb8583c`,
  `trading_bot/plan_funding_gate.py` `check_plan_funding()` gọi tại `bot_execute.py:536`; vượt ⇒
  KHÔNG đặt bất kỳ lệnh nào của account đó). `data/plan_buying_power_shadow_log.csv` vẫn ghi song
  song (audit trail), không còn là cơ chế chặn duy nhất. **2 bug thật phát sinh + đã vá tối
  2026-08-07** (Mike điều phối Mafee + Taylor song song, quant-skeptic CONFIRMED cao):
  1. UPCOM (DRI) đi ra `loan_package_id=None` ⇒ rơi về gói mainboard-only của account ⇒ ppse
     precheck lẫn `place_order` đều reject ⇒ WAIT_CASH vô hạn dù thừa tiền (trông y hệt thiếu
     tiền thật). Fix: `brokers.py`/`plan_funding_gate.py`/`executor.py` luôn giải gói vay theo MÃ
     (tái dùng `_resolve_loan_package_id`), commit `c22bd1c`.
  2. Nhánh (1) của gate không cộng tiền lệnh BÁN cùng plan chạy trước (cơ chế L2 JIT-unpark, LIVE
     từ 08-06) ⇒ chặn oan plan TỰ CẤP VỐN ĐỦ — ca thật: ZaloPay 08-07 bị chặn sạch 0/9 lệnh dù 8
     lệnh bán PARK (98,68tr) thừa nuôi 1 lệnh mua DRI (23,60tr). Fix: thêm tín dụng JIT theo tỉ lệ
     nhu cầu từng nhóm gói vay, chỉ tính lệnh bán priority < min priority mọi lệnh mua (tránh
     double-count + tái lập đúng bug "list lệnh rồi đợi tiền"), commit `087a3d0` + doc fix `00ffd2e`.
     quant-skeptic CONFIRMED cao (independent recompute khớp chính xác, kể cả case-71 "phòng vệ" là
     lệnh bán chỉ đảm bảo được THỬ trước, không đảm bảo KHỚP trước — rủi ro tồn dư, đã disclose, có
     backstop layer-3 WAIT_CASH không đổi).
  ⚠️ SpaceX (margin) chưa từng có bản ghi `pp0Buy` thật — số liệu replay dùng PROXY
  (`availableCash`), là cận dưới. Xác nhận sống cần chờ phiên thật (kỳ vọng 08-10, UPCOM buy nên
  ra `loan_packages_resolve … resolved=1122` trong `dnse_raw`, không WAIT_CASH giả). Thiết kế gốc:
  `mike/agents/Taylor/research/ontology_constraint_layer_design_20260729.md` (mô tả P0 lúc còn
  WARN_ONLY — đã lệch thực tế từ 08-04, đọc kèm ghi chú này).
  ⚠️ **Rủi ro quy trình phát hiện cùng tối**: dispatch Mafee + Taylor sửa CÙNG file
  `plan_funding_gate.py` trong vòng 1 phút không cách ly (không worktree) — commit của Mafee vô
  tình cuốn theo phần việc CHƯA COMMIT của Taylor (dead code lúc đó, cả 2 bên tự công bố minh
  bạch, không mất việc). Lần sau nên tách file hoặc chạy tuần tự khi 2 dispatch cùng chạm 1 file.

## Due-diligence MẶC ĐỊNH cho mọi ứng cử viên mua — ĐÃ SHIP, ổn định (2026-07-21)
`trading_bot/due_diligence.py` — thuần thông tin (không chặn/đổi sizing), 5 trục (thanh khoản/
valuation/PEAD-surprise/anomaly/FA thô), wire ở 4 choke-point: `golive_recommend_v23.py`,
`send_plan_report.sh`, `eod_trading_report.sh`, `dc_book_waterfall_paper.py`. Trần %ADV LAG =
gate CỨNG live riêng (`cap_lag_orders`, fail-closed từ 07-22) — KHÁC domain-constraint P1 trên.

**Sàn thanh khoản ADV3T 2 tỷ/phiên — GATE CỨNG mới ở tầng CHỌN MÃ (LIVE từ 2026-08-10, commit
`c4ca90f`).** Trước đó ADV3T<2 tỷ chỉ hiện cảnh báo (SCL ADV3T 1,30 tỷ vẫn mua đủ ngày 08-10).
`lag_liquidity_filter.py` (LAG) + `bal_filter_thin()` trong `golive_recommend_v23.py` (BAL) giờ
loại thẳng ứng viên <2 tỷ TRƯỚC due-diligence/plan — KHÔNG đụng `executor.py`/`plan.py`/
`signal_v11_sql.py` (nền backtest pin R3), KHÔNG đụng sleeve discretionary (TV1/DGC).
**Quyết định vì hiệu quả vốn (user chốt), KHÔNG phải edge** — backtest vẫn nói ngược (−0,26pp
CAGR/−0,92pp OOS/PBO 0,916, ghi trong comment code). ⚠️ Vốn dôi ra KHÔNG tự dồn sang deal LAG/BAL
lớn hơn (LAG không có hàng đợi; BAL có hàng đợi trần 12 nhưng chỉ lấp 55% phiên) — rơi về cash rồi
vào parking custom30V, user đã biết và chấp nhận trước khi duyệt. Cái giá: rổ LAG hôm nay 176→58
ứng viên (−67%), loại cả TRC (ADV 1,44 tỷ, mã đã duyệt mua 07-24). quant-skeptic CONFIRMED cao.
Rollback 1 chữ: `ADV_MIN_VND = 0` trong `lag_liquidity_filter.py`. Chi tiết:
`mike/agents/Taylor/research/adv3t_hard_gate_wire_20260810.md` +
`mike/agents/Taylor/research/adv_hard_gate_impact_20260810.md`.

## R&D pipeline (mọi mục PAPER-ONLY trừ khi ghi rõ LIVE)
Backlog đầy đủ (checkpoint, điều kiện GO/NO-GO, bug đã biết): `kb/projects/
rnd-pipeline-tracker.md`. Không có mục nào LIVE. **3 checkpoint đã quá hạn chưa xác nhận** (cần
dispatch Taylor kiểm tra, đừng tự đoán): EXTREME-regime gate (07-28), vol-scale chase-cap patch#3
(07-14), fill-timing khung giờ (cuối 07). Sleeve "mua khi sợ hãi có tính toán" (fear-buy): quét
chủ động HÀNG TUẦN qua `bin/fearbuy_weekly_scan.sh` (cron Friday 08:10 ICT) — mandate 2026-07-23
sau case TV1+DGC, kết hợp anomaly_scan + WebSearch tin khởi tố, áp bộ lọc QUALIFY/NON/AMBIGUOUS
trong `calculated_fear_state_backstop.md`. Recon thuần, KHÔNG tự mua.

**`srcwalk` — MỞ TOÀN FLEET 2026-08-03, nhưng CHIA THEO VIỆC** (skill `~/.claude/skills/srcwalk/`,
binary v1.3.0). Benchmark N=200 symbol + N=150 file cùng ngày (`kb/projects/srcwalk-benchmark-20260803.md`,
ground truth `ast`, bootstrap CI) chốt ranh giới: **`srcwalk` để ĐỌC file** (−88,8% token CI[86,5–90,7],
giữ 95,7% symbol, 0/150 phản ví dụ); **`grep` để TÌM** định nghĩa/call site (thắng ΔF1 +0,05/+0,06 CI
không chứa 0, rẻ 3–25×, và **0% im lặng trả rỗng** vs 8,2% của srcwalk). Ngoại lệ: tên rất phổ biến
(`main`/`run`) thì `srcwalk discover --scope <dir>` hơn (P 0,84 vs 0,46). ⚠️ **Bẫy `.gitignore`**:
`.gitignore` ẩn `mike/` ⇒ 44% file `.py` vô hình với discovery, `--scope .` cho F1 0,065 trên code
fleet → LUÔN scope vào thư mục chứa code. Vẫn cấm: `trace --depth ≥2`, khối "impact", symbol list của
`review`, bash. Quy tắc đầy đủ: `WorkingClaude/CLAUDE.md` § Code navigation.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (opus) chẩn đoán +
sửa + verify + báo Trading Daily; wire vào `ops_health_check.sh` (08:20/12:45),
`sync_bq_cache_daily.sh` (23:45), `cron_health_check_daily.sh` (08:25, mới 2026-08-01). Cooldown
1h/vấn đề chống bão dispatch. **Ranh giới cứng (không bao giờ tự sửa, escalate question +
Telegram):** trade plan, trading_rules.json, logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu,
BOT_STOP. Mike trong phiên sống thấy lỗi ops → tự sửa trực tiếp cùng ranh giới đó.

## Workflow ngày trading (SpaceX/ZaloPay, T2-T6, giờ ICT)
Timeline đầy đủ (giờ từng bước, checker gì, ranh giới tự sửa): **`kb/ops_runbook.md`**. Onboarding
account mới: **`kb/account_onboarding_runbook.md`** (cron dùng-chung tự nhận account mới qua
`trading_bot.config.live_dnse_labels()`; riêng 4 dòng cron THỰC THI THẬT luôn cần hỏi user trước).
Phần dưới đây là quy tắc **Discord topic routing** — KHÔNG có trong ops_runbook.md, chỉ ở đây.

**3 Discord topic tách biệt:**
- **Trading Daily (1521470705563340910)** — vận hành SỐNG trong ngày: preflight, run_bot,
  heartbeat, BQ freshness, `ops_health_check.sh`.
- **DollarBill plan channel (1521183164364754974)** — riêng việc LẬP KẾ HOẠCH của DollarBill
  (`send_plan_report.sh` + mọi `dispatch.sh DollarBill ...`). Route cố định qua
  `dispatch.sh`'s `_agent_thread_override` bất kể Mike gọi từ topic nào.
- **Per-job thread routing tổng quát** — `_agent_thread_override` chỉ đúng cho agent LUÔN thuộc
  1 topic cố định. Taylor phục vụ NHIỀU topic song song → `dispatch.sh` ghi `discord_thread_id`
  NGAY vào job record lúc dispatch (chụp 1 lần), mọi thông báo đọc lại field này qua
  `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/incidents/index.md`.
- **Trading report (1522576692638388364)** — kênh DUY NHẤT cho **báo cáo tổng hợp** ngày/tuần/
  tháng (khác alert vận hành sống ở Trading Daily). `eod_trading_report.sh` + báo cáo tuần/tháng
  Mike tự soạn đều đích vào đây.

**Duyệt plan — LUÔN mirror vào DollarBill plan channel:** khi user duyệt/thảo luận duyệt plan ở
BẤT KỲ topic Discord nào khác, Mike xử lý ngay tại chỗ (không ép đổi topic) NHƯNG phải
`notify_thread.sh` xác nhận vào **1521183164364754974** ngay sau đó — channel này luôn là bản ghi
đầy đủ mọi lần duyệt, tránh rải rác/loãng topic khác.

**Escalation khi plan T+1 không sẵn sàng:** `send_plan_report.sh` 21:00 ICT (+ second-chance
23:00) verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Thiếu/sai → ESCALATE thật:
Telegram + Discord + bus event `question` (`plan-t1-not-ready`). KHÔNG tự động retry/re-dispatch
(human-in-the-loop).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 08:25 | T2-T6 | cron_health_check_daily.sh — audit toàn bộ crontab (mới 2026-08-01) |
| 08:30 | T2-T6 | check_report_cadence.sh — báo cáo tuần/tháng quá hạn thì TỰ dispatch Taylor soạn+gửi + escalate Trading report topic (mới 2026-08-01, thay WARN cũ bị chôn im lặng 5 ngày); mỗi lần chạy cũng quét + gửi email (send_report_email.py, Gmail SMTP app password) mọi report chưa từng gửi qua email (thêm 2026-08-01, user yêu cầu) |
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory, check ngưỡng cứng kb file MỖI đêm |
| 02:00 (UTC Fri = ICT Sat sáng) | Weekly | kb_nightly.sh → dispatch Mike editorial KB review (đầy đủ) |
| 03:30 ICT Sat | Weekly | weekly_ops_audit.sh — audit sâu vận hành (mới 2026-08-01) |
| 00:00 | Daily | backup.sh → GitHub |

## Vận hành/kiến trúc daemon — trạng thái ổn định (không đổi gần đây)
Remote-control daemon `mike@Mike.service` tắt hẳn từ 07-07 (user chỉ dùng Discord qua
`ccdb-mike.service`). Model mặc định Mike = Sonnet 5, đồng bộ 3 tầng config (DB ưu tiên cao nhất).
Chi tiết: [[reference-ccdb-model-config-layers]] + [[project-discord-only-workflow-remote-control-disabled]]
trong memory Mike.

## Sự cố đã đóng — rút gọn, chi tiết đầy đủ `kb/incidents/index.md`
Audit cron C1/H2 (2026-07-12), BQ cache monolith (2026-07-13), cross-account contamination
(2026-07-19), 3 bug quoting silent-fail + full crontab audit (2026-08-01) — tất cả FIXED+VERIFIED.
**Còn treo thật** (1 mục, ưu tiên thấp): dọn crontab paper-trading lạc hậu — diff có sẵn
(`Winston_20260712_151206`), chưa áp dụng.
