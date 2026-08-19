# Mike fleet — context pack (v2374)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-19T12:10:42] DollarBill/finding — bot_prepare_plan-py-broken-and-mismatched: {"bug1": "trading_bot/strategies.py:372 next_trading_day(signal_date) called with str not date, crashed 100% since commit e39aafbe 2026-08-15 (GDKHQ feature) -  …
- [2026-08-19T12:15:34] DollarBill/decision — plan-2026-08-20: {"account": "SpaceX", "plan_date": "2026-08-20", "orders": 0, "action": "HOLD_ALL", "reason": "cash tuc thi ~0 (availableCash 4.382d, qmaxBuy VPI=0); 0 tin hieu …
- [2026-08-19T12:17:53] DollarBill/decision — plan-ZaloPay-2026-08-20: {"account": "ZaloPay", "plan_date": "2026-08-20", "file": "data/trade_plans/plan_ZaloPay_2026-08-20.json", "orders": 0, "deferred_orders": 1, "deferred_ticker": …
- [2026-08-19T12:48:59] Mike/answer — zalopay-vix-reconcile-blocks-l1l2: {"resolved": "CONFIRMED corp action VIX-2026-08-20-STOCK-DIVIDEND ghi vao data/corp_actions.json (co tuc CP 5%, exright_date=2026-08-20, tav2_bq.corporate_actio …
- [2026-08-19T13:02:04] Taylor/finding — harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY: {"job": "Taylor_20260819_124400", "program": "extreme_regime", "claim": "Harness probe da duoc mo rong de bien bang chung tu MOT CHIEU thanh HAI CHIEU, ma KHONG …
- [2026-08-19T13:02:23] Taylor/finding — bal-shadow-track-dang-ky-xong: {"job": "Taylor_20260819_124845", "main_account_include_bal": "KHONG - paper main chi chay harness churn 6 ma cho extreme_regime/fill_timing/vol_scale_chase_cap …
- [2026-08-19T13:09:47] quant-skeptic/verification — ✅ CONFIRMED VERIFY: harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY: {"finding_topic": "harness mo rong bang chung gate extreme_regime: probe_linger 30' + tick log band-proximity, PAPER-ONLY", "verdict": "CONFIRMED", "confidence" …
- [2026-08-19T13:19:06] Taylor/answer — job Taylor_20260819_124400 HOAN TAT: harness mo rong bang chung + deadline extreme_regime 2026-08-25 16:00 ICT: {"job": "Taylor_20260819_124400", "context": "Dispatch tu Mike: implement harness mo rong bang chung gate extreme_regime (user duyet PHUONG AN 2 + sua chinh sac …
<!--RECENT-END-->

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
- **Trứng vàng DNSE** (off-book idle cash, `manual_offbook_assets_vnd`): ĐÃ ĐÓNG HẲN cả 2 account
  (2026-07-23), vĩnh viễn — KHÔNG đề xuất "rút thêm" bù cash gap. Chi tiết:
  [[project-dnse-trung-vang-offbook-assets]] (memory Mike). ⚠️ KHÁC field `egg.totalValue`
  (API balances, live 2026-08-18) — đó là số dư THẬT hiện có trong sản phẩm Trứng vàng của DNSE
  (SpaceX ~100,2tr/ZaloPay ~38,8tr đo 2026-08-19), đã cộng vào NAV tự động qua
  `compute_active_nav.py`/`daily_nav_snapshot.py` nhưng KHÔNG phải sức mua tức thời (`availableCash`)
  — cần lệnh rút, về tài khoản sáng hôm sau. Xem `kb/context_planning_ext.md` không tồn tại mục
  này (đã để trong `context_planning_mini.md` § "`egg.totalValue`") — DollarBill phải đọc egg
  trước khi kết luận "thiếu tiền".

## VPI (BAL) — HOLD 2026-08-20, KHÔNG PHẢI thiếu tiền — chờ paper-trading BAL đánh giá lại (quyết định user 2026-08-19)
Plan SpaceX/ZaloPay 2026-08-20 ghi lý do HOLD/defer VPI là "cash tức thời ~0" — **đúng về mặt kỹ
thuật** (`availableCash` thấp thật) nhưng **KHÔNG phải lý do THẬT user không mua**. User xác nhận
trực tiếp (Discord, topic 1521183164364754974, 2026-08-19): chưa mua VPI lần này vì (1) các chỉ số
thị trường/kỹ thuật chưa tốt, và (2) **hiệu suất gần đây của book BAL chưa tốt** — cần quan sát
thêm một thời gian trước khi mua thật. Đây là quyết định RỦI RO/TIN TƯỞNG vào tín hiệu, không phải
giới hạn vốn (egg SpaceX ~100,2tr/ZaloPay ~38,8tr thừa sức tài trợ 25,08tr nếu muốn, xem mục trên).
- **Quyết định**: đưa **BAL vào theo dõi paper-trading** để đánh giá thêm hiệu suất gần đây, TRƯỚC
  KHI resume mua thật cho tín hiệu BAL (bắt đầu từ case VPI). `decided_by: user`.
- **Việc cần làm** (đã dispatch Taylor 2026-08-19, xem bus): đăng ký 1 entry trong
  `mike/kb/paper_programs_registry.json` cho track này (owner Taylor), xác nhận account "main"
  paper hiện có đã chạy BAL trong strategy đầy đủ hay chưa (verify artifact, không giả định), đặt
  tiêu chí/checkpoint cụ thể để quay lại xét resume mua thật.
- **Ranh giới**: KHÔNG tự resume mua VPI (hay bất kỳ tín hiệu BAL mới nào ở mức tương tự) cho tới
  khi có checkpoint đánh giá rõ ràng + user xác nhận lại — nếu tín hiệu BAL khác xuất hiện trong
  lúc chờ, escalate hỏi thay vì tự áp dụng cùng logic HOLD hay tự resume.

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

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 28.86% / Sharpe 1.90 / DD −17.8% / Calmar 1.62** — pin CHÍNH THỨC từ
  **2026-08-03** (Final NAV 1.178,01B), đo trên **`universe_pit`** (point-in-time, không look-ahead).
  ⚠️ **KHÔNG phải "hệ tốt lên"** — KHÔNG có thay đổi mô hình nào. Đây là **đồng bộ registry theo
  code production**: mặc định `LAG_ADV_BASIS` (cơ sở giá của ADV book LAG) đã đổi `close`→`price`
  ngày 08-02 (commit `0062aa0`, để gỡ look-ahead + giữ bất biến "trần live == trần đã mô phỏng")
  nên số pin cũ không còn tái lập được bằng lệnh pin trên code hôm nay. Chân control (`close`) tái
  lập 27.24% TUYỆT ĐỐI cả 5 chỉ tiêu + cả 2 số IS/OOS ⇒ A/B hợp lệ. **Toàn bộ chênh nằm ở IS
  (+3,28pp), OOS chỉ +0,02pp** — hệ số `Close/Price` hội tụ về 1,00 gần đây nên chỉ khác ở nửa đầu
  mẫu; **KHÔNG trích +1,62pp như "edge mới"**. Chi tiết ở `data/results_registry.md` (mục
  **2026-08-03 RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION `LAG_ADV_BASIS=price`**), KHÔNG lặp lại ở đây.
  **Số lịch sử KHÁC VINTAGE / KHÁC CƠ SỞ / CÓ LỖI, không so trực tiếp**: 27.24%/1.81/−18.4%/1.48
  (pin 08-02, cơ sở ADV `close` — đúng với cơ sở đó, đã SUPERSEDED); 27.60%/1.84/−17.5%/1.58 (pin
  07-29, có look-ahead cơ sở giá rổ); 27.16%/1.81/−18.1%/1.50 (pin 07-22, đã mất, không tái lập
  được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`).
  ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho
  CAPIT pool/maturity. Lỗi fidelity `liq<=0` — **cơ chế nay đã tách được (T1-T5, job
  `Taylor_20260803_021414`/`_045138`, quant-skeptic CONFIRMED cao)**: giả thuyết "hiện vật sức
  chứa" BỊ BÁC BỎ hai lần bằng hai knob trực giao (`%ADV/ngày` và NAV), cả hai lần bằng SAI DẤU
  đạo hàm — không phải "chưa loại trừ được". Nhưng **MỨC thì KHÔNG tách được**: cả hai chân đứng
  trên 1 tham số mô hình fill (trần 20% ADV/phiên) mà 90-96% số phiên-fill sống Ở TRẦN đó, trong
  khi fill THẬT (DNSE) mới chỉ xác nhận tới ~3,86% ADV/phiên — 2 thiên lệch NGƯỢC CHIỀU cùng bậc
  độ lớn (+4,08pp do sửa đúng nhóm mã không mua được vs. −4,0..4,5pp do giả định fill quá lỏng)
  gần **triệt tiêu nhau**. ⇒ **28,86% ĐỌC LÀ ƯỚC LƯỢNG ĐIỂM có điều kiện vào 1 tham số chưa neo**,
  KHÔNG PHẢI cận dưới, không phải cận trên (đổi nhãn 2026-08-03, thay khoảng `[~27,2%;~31,3%]`
  đã hết hiệu lực) — **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng** ở bất kỳ
  chiều nào. Follow-up 08-04 (gate động theo executability thật) củng cố thêm: giải quyết được
  vấn đề cơ học (vị thế kẹt 35%→0%) nhưng KHÔNG cho lợi nhuận bền (đổi dấu khi bỏ 2020-2021,
  PBO cao) — cùng chữ ký reshuffle-luck. Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không
  bằng backtest thêm — sổ theo dõi + **mốc cứng 2026-12-15 / 2027-03-31**:
  `kb/projects/lag-adv-filter-tracking.md`, chi tiết cơ chế: `agents/Taylor/research/
  lag_fidelity_decomp_20260803/T5_DECISION.md`.
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
  ⚠️ **+0.125 ĐÚNG, đừng hạ** — đề xuất +0.096/+0.034 (nhân `Price/Close` "khử look-ahead") ĐÃ BỊ
  BÁC BỎ 2026-08-02: `PE` vốn đã ở cơ sở `Price` thô PIT đúng; nhân vào là ĐƯA look-ahead VÀO
  (R3 xấu −1,70pp). Xem `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)".
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

## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`
<!-- Rút gọn 2026-08-10: mỗi dòng trước đây là 2-4 câu kể lại diễn biến. File này bơm vào MỌI
     dispatch có context_pack ⇒ tường thuật của việc ĐÃ ĐÓNG là chi phí trả lại mỗi phiên.
     Giữ đúng phần còn quyết định được hành vi sau này: TÊN · FILE · PHÁN QUYẾT (nhất là NO-GO,
     để không ai đề xuất lại). Diễn biến vẫn nguyên trong file chi tiết. -->
- 2026-08-13→14 corporate_action BQ integration + paper-report bug fix → `corporate-action-bq-integration-0813.md` — XONG, Việc A/B wire an toàn (6 vòng), SANITY_FACTOR WARN phương án C wire+CONFIRMED 08-14 (1 gap coverage nhẹ còn mở), vòng 6 rc=1/KeyError chủ động bỏ qua
- 2026-07-31 CAPIT sizing bug 07-21 → `capit-sizing-bug-0721.md` — ĐÓNG, đã fix; user chốt KHÔNG bù phần thiếu
- 2026-07-28 DGC + TV1 fear-buy due-diligence → `dgc-tv1-fearbuy-discretionary.md` — XONG, cả 2 QUALIFIED, theo dõi discretionary riêng
- 2026-07-21 LAG 07-24 (IVS/TMG/TRC) → `lag-0724-ivs-tmg-trc.md` — XONG, gate %ADV + lọc thanh khoản LAG đã wire
- 2026-07-20 Deposit-rate auto-crosscheck → `deposit-rate-autocheck.md` — XONG, tự động, không cần người
- 2026-07-17 DCF upgrade → `dcf-earning-power-upgrade.md` — earning-power **NO-GO** (giữ FCFE); refresh-gate cron LIVE
- 2026-07-13 World Cup + rổ lãi suất huy động → `wc-deposit-rate-gate.md` — **NO-GO** cả 2 hướng, N quá mỏng
- 2026-07-13 Plan-approval gate → `plan-approval-gate.md` — XONG, re-send 23:00 + code-gate `bot_execute.py`
- 2026-07-13 Plan ZaloPay transition 5/5 → `zalopay-transition-0713.md` — XONG
- 2026-07-13 DT5G BULL-giả → audit freshness → `dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN, live không sai
- 2026-07-13 Báo cáo tuần 07-06→07-10 → `weekly-report-mechanism.md` — XONG, có WARN quá hạn
- 2026-07-13 Audit dữ liệu 8L (BCTC Q2) → `8l-data-audit.md` — XONG
- 2026-07-12 lag_edge_health.csv staleness → `lag-edge-health-staleness.md` — KHÔNG phải bug; check lại ~08-25
- 2026-07-12 fa_ratings/8L → `fa-ratings-rebuild.md` — re-tune 8L **NO-GO**; rebuild builder XONG
- 2026-07-12 V2.5 leverage → `v2.5-leverage-nogo.md` — **NO-GO**, giữ DISABLED (edge là IS-artifact)
- 2026-07-12 LAG-weight (tăng tỷ trọng PEAD) → `lag-weight.md` — ĐÓNG, KHÔNG tăng trần w_LAG
- 2026-07-12 Momentum-deals (MOM_N/MOM_S) → `momentum-deals.md` — KHÉP KÍN, production LIVE
- 2026-07-12 Q-sleeve → `q-sleeve.md` — **NO-GO** cả 2 trục
- 2026-07-12 Audit sẵn sàng BCTC Q2/2026 → `bctc-q2-readiness-audit.md` — KHÉP KÍN
- 2026-07-03 Usage-limit auto-resume → `usage-limit-auto-resume.md` — XONG
- 2026-07-02 Reliability hardening (AgentOps) → `reliability-hardening.md` — XONG

## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)
- R&D pipeline (mọi thử nghiệm paper-only) → `rnd-pipeline-tracker.md`
- Migration `ticker_prune` → `universe_pit` (G5-G9) → `universe-pit-migration.md`
- LAG ADV>0 filter — đo edge vs hiện vật fill → `lag-adv-filter-tracking.md` — chủ Taylor, mở 2026-08-03.
  **KHÔNG kết luận gì** trước 2 mốc cứng: checkpoint **2026-12-15**, rà soát đầy đủ **2027-03-31**.
- CASH_VENDOR gate (số cổ tức từ `tav2_bq.corporate_action` khi broker không giải được) →
  `cash-vendor-gate-tracking.md` — user chốt 2026-08-15 **giữ ĐÓNG**; mở lại chỉ khi có ≥1 sự
  kiện ISS/hỗn hợp VÀ đã qua **2026-09-13**, và vẫn cần user xác nhận lần nữa lúc đó.

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/ (index ở trên). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
