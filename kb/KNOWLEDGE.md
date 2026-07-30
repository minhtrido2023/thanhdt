# Mike fleet — KNOWLEDGE (canonical)

> **Nguồn sự thật của toàn đội — canonical-only, Mike biên tập thủ công.**
> Consolidator KHÔNG ghi vào đây (raw events → `kb/events_buffer.md`). File này ổn định.
> Agent đọc `context_pack.md` (~8KB, distilled). File này dành cho tra cứu sâu và weekly editorial.
> Raw event log: `kb/events_buffer.md` (hot, 7 ngày) + `kb/archive/` (lịch sử). **Curated: 2026-07-11 (Mike, weekly editorial).**

---

## 1. Chiến lược trung tâm — V2.4 Production

**Định nghĩa:** V2.4 = V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout, depth OFF) + HAG eq_flag fix. **Go-live: 2026-07-01**, tài khoản SpaceX (DNSE 0002023347). **ZaloPay (DNSE 0001743768) go-live thứ 2: 2026-07-06** (cash-only, xem §5).

**Cấu trúc 2 book:**
- **BAL** — momentum SIGNAL_V11 (yieldcombo rank: 1/PE + 1/PCF, v3 composite bị loại vì IS-overfit)
- **LAG** — PEAD/earnings drift. Allocator w_LAG theo state {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.

**Performance đã pin (threads=1, self-check 0 VND):**
- R3 NEUTRAL-only @50B: CAGR **27.60%** / Sharpe **1.84** / DD **−17.5%** / Calmar **1.58** — **pin CHÍNH THỨC từ 2026-07-29**, đo trên `universe_pit`, quant-skeptic CONFIRMED (high). Re-pin do **VINTAGE DỮ LIỆU, KHÔNG đổi mô hình**. Nguồn sống (đừng chép số ra chỗ khác): `data/results_registry.md` mục **"2026-07-29 — ⭐ RE-PIN R3 SAU RESTATE DT5G"**.
  - *Số LỊCH SỬ, KHÁC VINTAGE — không so trực tiếp, không dùng cho việc mới:* 27.16%/1.81/−18.1%/1.50 (pin 07-22, vintage đã bị ghi đè, KHÔNG tái lập được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`, sau khi đóng kênh MOM); 28.05%/1.87/−18.8%/1.50 (pin gốc, job `_130720` — as-of re-run 2026-07-09 cho ~26.75% do batch/as-of recompute variance, **KHÔNG phải regression**).
- R1 @20B: CAGR **29.01%**
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **DSR/PBO annex (2026-07, `dsr_pbo_annex.py`):** R3 đã qua chuẩn deflated-Sharpe/PBO — DSR≈1.0, PBO≈0.20 (robust, không phải may mắn overfit). Đây là baseline cho mọi so sánh DSR mới (xem "Multiple-testing discipline" dưới).

**Parking — custom30V:**
- NEUTRAL parking: **production (30 mã, cap 0.10)** — phần tin cậy nhất: +7.4pp Full.
- **(30, 0.15) là OVERFIT** — walk-forward bác.
- Bull parking: chỉ bật khi NAV ≥150B. Custom30B bull-sleeve FAIL walk-forward, không hạ NAV threshold.
- **NEUTRAL parking target = 70%, ở MỌI mức NAV** — chính thức hoá `trading_rules.json` v2.1 section `neutral_parking` (default 0.70 của phần idle cash khi BAL/LAG rỗng, KHÔNG phải trần tổng cổ phiếu). Muốn park≠0.70 bắt buộc `risk_dial_override` (2 field: `risk_dial_confirmed_by_user` + `risk_dial_warning_acknowledged`) — thiếu 1 trong 2 thì Mafee tự block plan.
  - Nguồn quyết định 70% (không phải 93.8-94.7% go-live gốc do DollarBill tự đặt không qua backtest): full 2-book NAV backtest (job `Taylor_20260703_130720`, quant-skeptic CONFIRMED) — 70% thắng tuyệt đối mọi metric risk-adjusted (Sharpe 1.78 vs 1.66 @94%, Calmar 1.63 vs 1.49, DD −16.5% vs −18.8%).
  - **2026-07-09 sweep NAV nhỏ (job `Taylor_20260709_012737`):** premise "NAV nhỏ (~20B) → nên đẩy park 70→90 an toàn hơn" — **REFUTED, đảo ngược**. Ở NAV nhỏ, tăng park mua ÍT CAGR hơn (+0.56pp) và trả NHIỀU risk hơn (Sharpe −0.12, Calmar −0.14, DD −2.0pp) so với ở 50B (+1.26pp CAGR, risk cost thấp hơn) — vì 2 book lõi ở NAV nhỏ đã chạy giàu hơn baseline, phần park thêm chỉ cộng DD không cộng lợi tương xứng. **GIỮ park=0.70 ở mọi NAV hiện hành**, không đổi production/paper.

**Multiple-testing discipline (chốt 2026-07-05, Bailey–López de Prado):** mọi wire production khai báo **N trials** + **DSR** trên NAV daily. **DSR<0.95 → RED FLAG**, không wire nếu chưa sign-off. Khi chọn từ họ ≥~8 biến thể: báo thêm **PBO (CSCV)** — PBO≥0.5 = ưu tiên config robust-trung vị. Kèm **per-year leave-one-out** khi OOS edge mỏng năm (bài học Wave1/H8a-tiebreaker, xem §7/§8: OOS tăng đúng luật nhưng toàn bộ đến từ 2 năm, LOO rớt → route qua skeptic trước khi wire, KHÔNG wire).

**Paper-trading pipelines đang chạy (mọi cái đều account paper `main`, KHÔNG chạm live SpaceX/ZaloPay — trừ khi ghi rõ):**
- **EXTREME-regime gate** (từ 2026-07-01, target kết thúc ~2026-07-28): Week-1 stress-injection PASS 24/24. Điều kiện LIVE: ZERO false-trigger ~4 tuần benign + không can thiệp NORMAL-path + user sign-off.
- **Vol-scale buy chase-cap (patch#3)** (từ 2026-07-01, target kết thúc ~2026-07-14): executor-path stress PASS 15/15. Điều kiện LIVE: paper sạch + không can thiệp NORMAL-path + quant-skeptic rerun REAL-fill vs proxy + user sign-off.
- **DC-book (ConvergePort) NEUTRAL idle-cash waterfall** (từ 2026-07-06, job `Taylor_20260706_125540` + `_131247` + deep-dive `_173317`): khi NEUTRAL và BAL/LAG rỗng, thứ tự ưu tiên **BAL/LAG (full trước) → DC book (double-confirm sector-lens BUY ∧ 8L rating≤2, ex-DHG, cap gộp overlap 0.15, floor thanh khoản Trading_Value_1M_P50≥3B) → custom30V**. DC làm top-priority (thay BAL/LAG) = REFUTE mạnh; DC làm lớp giữa (đúng thứ tự trên) = +5.0pp trên sleeve parking, ước tính +3.5pp/năm cho SpaceX-now. **Caveat: DSR phần excess chỉ 0.775 (<0.95 ngưỡng) — bảo hiểm hợp lý, CHƯA phải alpha tin cậy cao** → paper trước, không wire live. Review **event-anchored** (không phải ngày cố định): mốc = khi chu kỳ reverse-unwind ĐẦU TIÊN (LAG refill dự kiến cuối 07) hoàn tất + settle 4-6 tuần sau — sàn ~2 tháng, trần ~2026-10-06 (tránh mùa BCTC Q3), trượt theo nếu LAG refill trượt lịch.
- **Fill-timing khung giờ** (BUY 10:45-11:15 / SELL 09:15-09:45): edge THẬT & IS/OOS-stable (BUY@11:15 rẻ hơn open +17.6bps/lệnh t=12.0; SELL@open +11.8bps vs ATC) nhưng **KHÔNG flip live ngay** — đây là mechanics-gate (cần verify cơ chế khớp lệnh sạch), không phải edge-gate (edge đã chứng minh trên backtest lịch sử, KHÔNG cần live tự chứng minh lại — noise 110-220bps >> edge 17bps nên live/paper vài tuần không bao giờ tự thấy edge, đúng thiết kế). **2026-07-09 audit fill thật** (job `Taylor_20260709_101602`, phản hồi user nghi "mua xong lỗ ngay trong phiên"): cảm nhận user ĐÚNG về giá trị (BUY vsClose −41.7bps VW) nhưng nguyên nhân = trôi thị trường 1 ngày cụ thể (07-02, deploy lớn lúc 09:15 gặp bank fade cả phiên), KHÔNG phải lỗi cơ chế khớp (vsOpen +3.4bps, sạch). Đồng thời phát hiện + sửa bug đo lường: `execution_quality_review.py` đếm nhầm cả lệnh LIVE (bị ép mult=1.0) vào "in-window adherence" → con số "98% adherence" là GIẢ; sau fix, evidence-rate thật ≈0 (paper main CHƯA từng chạy phiên sáng có BUY thật trong cửa sổ). Checkpoint flip vẫn ~cuối tháng 7, điều kiện: ≥5 phiên paper có BUY fill trong cửa sổ + 0 reject + không lệnh treo → quant-skeptic → user sign-off. Option trung gian: pilot flip riêng ZaloPay (cash-only, lệnh nhỏ) trước SpaceX — chưa quyết.

**Đã thử, BỊ LOẠI — không wire:**
- Custom30V permanent-exclude 7 tên: HURTS −1.0pp (walk-forward bác). DO NOT wire.
- LAG fresh-high-SUE tilt 3 tầng: −0.66pp vs binary. Giữ LAG nguyên.
- Hold-neutral test (exit CAPIT khi về NEUTRAL): thoát sớm 14/15 episode, −47B VND. Giữ CAPIT_HOLD=60td.
- Stability floor (ROE_Min<0 cap): −0.45pp CAGR, bác.
- **Composite v3 làm entry/parking selector** (thay custom30V yieldcombo): LOSES trong MỌI window (Full −7 đến −11pp, OOS còn tệ hơn IS — không phải IS-artifact). Composite v3 vẫn LIVE nhưng chỉ ở vai trò **value-lens trong 8L rating** (không phải selector NAV). Composite v3 as-selector đã bị loại từ 2026-06-22, re-confirm 2026-06-30 (2 job Taylor cùng ngày).
- DC-book (ConvergePort) làm top-priority thay BAL/LAG: −12.05pp CAGR / DD gấp đôi so với đúng thứ tự — bác mạnh (xem waterfall ở trên).
- SOFT-threshold glide cho NEUTRAL idle-cash: REFUTED (không cải thiện risk-adjusted, 4 indicator + negative-control sạch).
- Technical-stabilization filter trên WATCH universe: REFUTED làm return filter (research-only).
- Wave1/H8a-tiebreaker (LAG within-tier d_NPR fill-reorder): CONDITIONAL PASS ban đầu nhưng **leave-one-out xác nhận LUMPY — DO NOT WIRE** (toàn bộ gain đến từ 1-2 năm cụ thể, không phải signal bền — bài học multiple-testing discipline).
- gq_score growth gate, pbcombo dual-vehicle, liq-tilt custom30, deep-discount sleeve (PARKED): giữ nguyên trạng thái cũ, chưa thay đổi.

**V2.5 (tương lai):** R&D-complete, DISABLED. Reminder go-ahead fired 2026-07-07 — **user vẫn CHƯA quyết** (treo, không phải đã bỏ qua). = V2.4 + leverage layer (deep-cheap gate, MGE=1.5, ~2 episodes/decade).

**Kill-switches (wired trading_rules.json, gốc v1.7 duyệt bởi Spyros, giờ v2.1 với neutral_parking):** SBV>7.5%, pb_z rising >−0.3 while episode active, episode DD>−12%. `data/BOT_STOP` = kill-switch tức thì toàn hệ thống.

**Nguyên tắc audit:** self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) TRƯỚC khi wire, threads=1 (pin reproducibility). Edge full-period mà rớt OOS = overfit → loại. Pin kết quả vào `data/results_registry.md`. **Bright-line 2026-07-09: same-day/live calc PHẢI đọc DNSE API, KHÔNG BAO GIỜ BigQuery** (BQ chỉ sync qua đêm 23:45 ICT — bất kỳ script chạy trước đó đọc BQ cho "hôm nay" là đọc dữ liệu HÔM QUA một cách có cấu trúc, không phải staleness thỉnh thoảng). Xem `coding_guidelines.md` §6.

---

## 2. DT5G — Market Regime Gate

**Production state:** bảng `tav2_bq.vnindex_5state_dt5g_live`, đọc qua `get_gated_state()`.
**KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions), KHÔNG phải DT5G (49 transitions).

**✅ INCIDENT LỚN 2026-07-10 — BULL commit giả do bug stale EW-leg — ĐÃ ĐÓNG 2026-07-13** (đường đi B/zero-touch: Taylor backfill EW-leg thủ công tối CN 07-12 + cron `daily_refresh` 18:30 ICT thứ Hai 07-13 recompute toàn cửa sổ và publish → `dt5g_live` có đủ cả 07-10 lẫn 07-13, `macro_health.json` tươi lại; trong lúc stale `get_gated_state()` fail-closed về DT4-only đúng thiết kế, DT4==DT5G==NEUTRAL nên không lệch hành vi. Chi tiết: `kb/incidents/2026-07/2026-07-13-dt5g-refresh-missed-cron-time-change.md`). *Ghi chép root-cause dưới đây giữ nguyên làm bài học:*
- **Root cause:** repo reorg 2026-06-21 (commit `10ae395`) đổi path reader sang `data/` nhưng writer trong `vnindex_5state_ew_v1.py` (dòng 519) vẫn ghi ra WORKDIR root → `data/vnindex_5state_ew_full.csv` đóng băng ở 06-19 từ 06-22. Base v3.4b mất 30-42% trọng số EW-leg + factor breadth (NaN) đúng lúc concentration cao → mọi cơ chế chống rally hẹp bất hoạt từ TRƯỚC khi episode BULL bắt đầu (06-24).
- **Phát hiện (Taylor, job `Taylor_20260710_163939`):** candidate BULL (streak 9/10, sắp commit tối 07-10) có breadth/thanh khoản TỆ NHẤT so với cả 8 lần BULL-commit thật lịch sử 2014-2026 (breadth 0.32 vs min lịch sử 0.52; thanh khoản 0.60 vs min 1.06) — dấu hiệu rõ ràng đây là artifact, không phải regime thật.
- **Fix + verify (job `Taylor_20260710_170527`, commit `498c3a6`):** sửa 1 dòng (ew_v1.py ghi ra `data/`), rerun toàn chain local. Counterfactual KHỚP: base giữ NEUTRAL(3) LIÊN TỤC 06-22→07-10, episode BULL giả 06-24→07-06 biến mất hoàn toàn.
- **Publish BQ: BỊ CHẶN (tại thời điểm 07-10, đã giải quyết 07-13)** bởi harness permission classifier (`bq load --replace` là production write, dispatch relay không tính là consent trực tiếp) — Taylor dừng đúng guardrail, KHÔNG lách. Backup rollback đã tạo (`vnindex_5state_archive_predeploy_20260711_002056`). BQ hiện tại (07-10) vẫn bản cũ nhưng **`dt5g_live` (production consumer thật) vẫn NEUTRAL(3), KHÔNG bị ảnh hưởng** — chưa có quyết định trading nào dựa trên tín hiệu hỏng.
- **Đường đi ĐÃ CHỌN & ĐÃ CHẠY = (B) zero-touch:** cron thứ Hai 2026-07-13 18:30 ICT tự chạy NGOÀI harness (không bị classifier chặn) với code đã fix, publish TRƯỚC preflight/plan cần dùng state. *(Phương án A — manual publish ngay — không dùng.)*
- **Audit mở rộng (Winston, job `Winston_20260710_173031`, DONE_FULL_AUDIT, read-only):** tìm thêm 2 path-mismatch mới (không ảnh hưởng production, chỉ research-path đọc file frozen) + 1 "trap ngược" do chính fix trên tạo ra (root `ew_full.csv` giờ orphan, 2 script research đọc phải, trong đó có chính `bull_commit_breadth_check.py` Taylor vừa dùng hôm 07-10) + 1 bug freshness-check no-op (`bq_freshness_check.sh:75` dùng `-le` nên MAX_STATE_LAG 2→1 không có tác dụng chặn lag=1 như comment ý định). **Lỗ hổng gốc thật sự** khiến bug sống 3 tuần không bị phát hiện: KHÔNG có bất kỳ check freshness/mtime nào cho các file trung gian trong chain local (ew_full/ew_staging/dual_v3_staging/concentration/v3_1_clean/v3_4b/dt_4gate) — mọi check hiện có chỉ nhìn ngày trên tên/timestamp output cuối, không phải nội dung input có thật sự mới hay không. **Đề xuất ĐÃ WIRE** (verify 2026-07-30 trong code): post-chain assertion nằm ở `daily_refresh_v34b_linux.sh` step **[8b]** (`assert_chain_outputs.sh "$CHAIN_START_EPOCH" …`) — mọi file output kỳ vọng phải có mtime ≥ lúc chain bắt đầu, thiếu/cũ → alert + `die` **TRƯỚC khi publish BQ** (bắt generic mọi writer sót tương lai, không chỉ path này).

**Trạng thái trước incident trên (baseline, vẫn đúng):** EASING_FLOOR disabled 2026-06-03 (re-risk chỉ qua price-based DT base). Nhãn bảng đã chốt 2026-06-26 (`vnindex_5state`=v3.4b BASE, `vnindex_5state_dt5g_live`=DT5G thật). DT5G là gate PHÒNG THỦ (insurance), KHÔNG phải return-enhancer (performance annex đầy đủ trong CLAUDE.md).

---

## 3. Kiến trúc Fleet & Dispatch

**Companion daemon:** **KHÔNG CÒN daemon nào** kể cả Mike (2026-07-07, user quyết định). `mike@Mike.service` (remote-control desktop app session) đã **TẮT HẲN** — user giờ chỉ dùng Discord (`ccdb-mike.service`, bridge độc lập hoàn toàn với `mike@Mike.service`, KHÔNG phụ thuộc nhau — xác nhận qua `systemctl --user show`, không có Requires/After/PartOf/BindsTo chéo nhau) để nói chuyện với Mike, tách theo topic. Desktop app chỉ dự phòng khi bất thường (vd lỗi model version không xử lý được qua Discord). `watchdog.sh`/`fleet_health.sh` tự động iterate qua unit đang `enabled` nên không báo cảnh báo giả cho unit đã tắt. Cần bật lại (hiếm khi cần): `systemctl --user enable --now mike@Mike.service`.
Mọi agent khác (Taylor, DollarBill, Mafee, Wags, ...) headless/native on-demand qua `dispatch.sh` — không có daemon riêng từ trước (lịch sử: Winston/Spyros/Wendy 2026-06-25 → DollarBill/Mafee 2026-06-30 → Taylor 2026-07-01).

**Cơ chế dispatch đúng:** `bin/dispatch.sh` (headless `claude -p`). Directive/inbox deprecated cho task — chỉ dùng cho mandate dài hạn.

**Model routing Sonnet 5 vs Fable 5 (thêm 2026-07-06):** `dispatch.sh --model NAME` (`sonnet|opus|haiku|fable`) — chọn theo **TASK, không phải theo agent cố định**: Q1 tra cứu/query cơ học → Sonnet 5 (mặc định); Q2 trade-off/tổng hợp/sinh giả thuyết/phản biện tinh vi → Fable 5; Q3 chạm production/live-trading chưa có template → Fable 5 bất kể Q1. Native subagent dùng tham số `model` sẵn có.
**Model mặc định của chính Mike:** đổi sang Fable 5 (2026-07-06) rồi **ĐẢO NGƯỢC LẠI Sonnet 5** (2026-07-07, user yêu cầu). Phát hiện **3 tầng config** trong bridge Discord (`ccdb-mike`): thread override (DB) > global (DB) > `.env` fallback — sửa `.env` vô tác dụng nếu DB đã có row cũ. Dọn 4 dòng rác sai format (`"Sonnet 5"`/`"sonnet 5"` có dấu cách — CLI từ chối) từng gây lỗi `/model` ở 1 thread. Đã đồng bộ cả 3 nơi.

**Routing guards (2026-06-27):**
1. Self-dispatch (from==id) → chặn, exit 2.
2. Agent → Mike: phải escalate qua event `question`, KHÔNG spawn Mike headless.

**Reliability hardening 2026-07-02 (4 việc AgentOps, theo yêu cầu user):**
1. **Circuit breaker** per-agent (`state/circuit/<id>.json`) — 3 lỗi liên tiếp → TRIPPED, cooldown 1800s.
2. **Idempotency ghost-order guard** (`Executor._ghost_tickers`, `trading_bot/executor.py`) — lớp phòng thủ thứ 2 độc lập với `fcntl.flock`, đóng gap process bị kill ngay sau `place_order()` thành công nhưng trước `_save_state()`. quant-skeptic CONFIRMED. Review vòng 2 (bên thứ 3, cùng ngày) tìm thêm: `_save_state()` không atomic (fix: tmp+`os.replace`), `PaperBroker.poll_orders()` guard no-op (fix: trả `raw` giống broker thật để paper diễn tập được), không có quy trình unpause chính thức (chấp nhận theo thiết kế — thủ công). Đã commit `e1d9b7c` (gộp cả 2 vòng review).
3. **trace_id** trong bus event, fallback `$JOB_ID`.
4. `kb/incidents/` (index: `kb/incidents/index.md`) — nhật ký sự cố đầy đủ, backfill từ đầu.

**Usage-limit auto-resume (2026-07-03):** `dispatch.sh` phát hiện fail vì hết usage limit 5h tài khoản (không phải task lỗi thật) → ghi `bus/pending_resumes/`, KHÔNG trip circuit breaker. `bin/resume_pending.py` (cron 10') tự dispatch lại "tiếp tục từ working memory". Trần 3 lần lặp (`DISPATCH_MAX_USAGE_RESUMES`) rồi rơi về xử lý fail thật. **Chỉ cứu headless dispatch, KHÔNG cứu phiên tương tác sống của Mike** — khi Mike thấy usage cao giữa task dài, phải chủ động báo trước + đề xuất `CronCreate` one-shot (session-only, mất nếu Mike restart giữa chừng — phải nói rõ giới hạn này mỗi lần).

**Fast wake-on-completion sau `dispatch.sh --bg` (2026-07-03, sửa nhiều lần, chốt 2026-07-07):** cơ chế chính hiện tại = **`ScheduleWakeup` poll ngắn lặp lại (240-270s)**, không phải 1 lần chờ dài theo worst-case (sửa 2026-07-06 sau khi user chỉ ra lãng phí thời gian cộng dồn qua nhiều bước sector-sweep). **Wrapper `Agent(run_in_background: true)` KHÔNG còn dùng được** từ 2026-07-07 — tham số này đã bị gỡ khỏi schema Agent tool sau khi Mike đổi sang Fable 5; `isolation:"worktree"` KHÔNG phải background (agent vẫn chạy đồng bộ, chỉ cách ly git worktree) — sự cố thật 2026-07-07: Mike bọc 1 dispatch bằng `Agent(isolation:worktree)` tưởng là nền, wrapper trả lời sớm rồi thoát, job thật xong sạch mà Mike không biết tới khi user tự hỏi. **Self-check bắt buộc:** đã nói với user bất kỳ điều gì về trạng thái 1 job thì CÙNG turn phải có 1 lần `bin/jobs.sh status <job_id>` làm bằng chứng — không nói từ trí nhớ/suy đoán (2 lần lỗi giám sát job nền trong cùng ngày 07-07: LOG_AGE nhìn như treo trong khi job sống; wrapper sai cơ chế mất tín hiệu hoàn tất).

**Wags (Fleet Ops Coordinator, thêm ~2026-07) — headless on-demand:** triage job nghi treo qua HB_AGE, pattern độ tin cậy dispatch, audit backlog escalation. `arch-reviewer` (native, adversarial, read-only) audit BẮT BUỘC sau mọi thay đổi Wags đề xuất/thực hiện — báo cáo vào topic Discord "Architecture". `bin/wags_autofix.sh` khi có lỗi điều phối giữa agent (KHÔNG đưa cho Winston — đây là scope của Wags).

**Execution pattern đúng cho trading:** `bot_execute.py --auto-otp` (Python, deterministic) — KHÔNG dispatch Mafee headless cho đặt lệnh (permission classifier block khi thao tác tiền thật). Quy trình an toàn: Taylor đặt rule (user duyệt) → DollarBill lập plan (user duyệt) → `run_bot.sh`/Mafee chỉ thực thi lệnh CÓ trong plan → `data/BOT_STOP` = kill-switch tức thì.

**Quant-skeptic:** native subagent, runner `bin/verify_finding.sh`. Rule: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.

**Công cụ mới 2026-07-03:** `bin/trace.sh <job_id>` (gộp job + mọi bus event cùng `trace_id` thành 1 timeline). `bin/staleness_watch.py` (watch-the-watcher cho pipeline tự báo freshness qua field `ts`). `bin/verification_audit.sh` (báo cáo coverage kiểm chứng finding↔verification, không tự gate).

---

## 4. Hạ tầng Kỹ Thuật

**BQ Local Cache (DuckDB, 2026-06-25):**
- 12 bảng BQ → parquet local `data/bq_cache/`, query ~100ms (vs 5-15s BQ). Sync daily 23:45 ICT.
- **Non-determinism bug (fixed):** DuckDB default threads=4 → ~0.2pp CAGR spread. Fixed threads=1. Self-check 0 VND KHÔNG đảm bảo reproducibility — phải pin threads.
- **⚠️ Bright-line rule (2026-07-09, user directive):** BQ chỉ sync qua đêm — mọi tính toán same-day/live (order sizing, ref price T+1 plan, live NAV/exposure) PHẢI đọc **DNSE API** (`dnse_api.py` secdef/latest_trade/positions/balances), KHÔNG BAO GIỜ BigQuery, bất kể giờ chạy script. Incident: 2026-07-09 DollarBill's T+1 plan generator giá 2/4 lệnh off BQ close (stale 1 ngày, lệch tới +5.7%) trong khi 2 lệnh khác dùng đúng DNSE quote — sự KHÔNG NHẤT QUÁN đó mới là thứ để lộ bug. BQ chỉ OK cho: (a) backtest lịch sử, (b) same-day SAU KHI freshness gate xác nhận sync xong (không suy đoán theo giờ).

**Auto-OTP Gmail:** `gmail_otp_reader.py` dùng `internalDate` filter (KHÔNG `newer_than`).

**Bot execution:**
- `bot_execute.py --auto-otp`: OTP + token + đặt lệnh trong 1 lệnh. Price unit = VND.
- `executor.py`: SIZE-ADAPTIVE fill. MODIFY quirky DNSE (HTTP 500 nhưng creates new order_id → must re-poll). `_ghost_tickers()` idempotency guard (xem §3). `_save_state()` atomic (tmp+`os.replace`), chạy ngay sau mỗi lần đặt lệnh thành công (không đợi hết `step()`).
- **DNSE cash account T+0 buying power (fixed `10d98e9`):** tiền bán settle T+2 nhưng `ppse` cộng vào sức mua ngay sáng cùng ngày — `availableCash` KHÔNG phản ánh; bot phải check `ppse` trước khi kết luận thiếu tiền.
- **T+2 chỉ sellable từ phiên CHIỀU** (không phải đầu phiên sáng) — plan bán mã mới mua phải né lịch sáng đúng ngày T+2.
- **`_publish_bot_event()`:** fire-and-forget lên Mike bus khi STEP_FAIL hoặc fill_lagging.

**`excluded_tickers` — cơ chế tổng quát cho account có vị thế legacy (2026-07-06):** khai báo trong config (`secrets/trading_bot_accounts.json`), enforce ở MỘT chỗ duy nhất (`trading_bot.plan.filter_excluded_tickers()`, gọi ngay sau `load_plan()` — không phụ thuộc plan generator nhớ đúng). Size strategy theo `active_nav` (= total NAV − market_value(excluded)), tính bằng `bin/compute_active_nav.py --account <label>` (đọc broker live, không phụ thuộc journal nội bộ). Dùng cho ZaloPay/DGC — xem §5.

**Watchdog & monitoring:** `bin/watchdog.sh` (cron 10'): DOWN restart + ZOMBIE (clear bridge-pointer + restart). `bin/is_serving.py`: oracle liveness thật. `bin/fleet_health.sh`: bảng sức khỏe tức thì. `bin/notify.sh` → Telegram, dedup 300s. `bin/usage_watch.py`/`bin/context_watch.py`: cảnh báo trần 5h/context dài — chỉ log, không tự sửa.

**Data quality bugs đã phát hiện (2026-06-28, vẫn còn hiệu lực):**
- DQ-1: `process_stock_indicator` chỉ ghi `tail(10)` rows → corp-action recompute sai indicator windows. Fix: force full-history recompute.
- DQ-2: `profit_*` forward-fill trong app-dataset → fabricates forward-looking values cho live row. KHÔNG dùng `profit_*` filter live.
- DQ-6: `get_gated_state()` raises `FrozenStateError` nếu DT5G row cũ >2 ngày trên live call.

**Provenance/idempotency 2 quy tắc client-facing (coding_guidelines.md §6, §8):**
- **Report cost-basis/P&L:** PHẢI qua `bin/verify_account_snapshot.py` (broker-native, cross-checked) — KHÔNG đọc field ước tính (`ref_px_approx`) trực tiếp. Incident 2026-07-03: field này bị đọc nhầm làm cost basis thật, biến 1 tuần lãi VHM thành lỗ giả −6.4%.
- **Không ghi output experiment vào filename canonical/registry-pinned** — mọi config axis ảnh hưởng số phải đổi filename hoặc dùng `OUT_CSV=` override; regenerate baseline pin PHẢI dùng đúng lệnh + đúng interpreter pin (`$DNA_PYEXE`, không phải `python3` hệ thống — pandas version khác nhau gây lỗi unpickle).
- **`dnse_raw_{date}.jsonl` account-tagging (fixed 2026-07-06):** file log dùng chung mọi account theo ngày, bản ghi `balances` KHÔNG gắn account → gây NAV SpaceX lẫn balance ZaloPay. Fix: `brokers.py` gắn `account_no`/`label` mọi bản ghi, `daily_nav_snapshot.py` lọc đúng account.

**Backup:** `~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private), branch `main` (code) + `mike-fleet` (fleet config+KB). Daily 00:00 ICT.

---

## 5. Go-Live — Trạng Thái Hiện Tại (2 tài khoản)

| Mục | SpaceX (DNSE 0002023347) | ZaloPay (DNSE 0001743768) |
|---|---|---|
| Go-live | 2026-07-01 | 2026-07-06 |
| Loại | margin (cash=1841, margin_rocketx=1840) | **cash-only** (package "ZaloPay" id=1258, không margin) |
| enabled | true | true |
| NAV (xác nhận API) | ~983M VND (07-06), tiếp tục theo dõi daily qua `daily_nav_snapshot.py` | active_nav 534.470.378đ (loại DGC), tổng NAV 1.011.470.378đ (07-06) |
| Đặc thù | Trim 07-06 hoàn tất (23/23 lệnh, 710.5tr/710.1tr kế hoạch, khớp broker 100%), nợ margin ~409.86tr chờ giảm dần theo settle T+2 | **DGC (47.2% NAV) EXCLUDED** khỏi rebalancing (`excluded_tickers`, xem §4) — HOSE hạn chế GD (QĐ 448) + cảnh báo (QĐ 544) do lãnh đạo bị khởi tố hình sự 17/03/2026; ước gỡ ~11-12/2026. 7 vị thế legacy khác (MSH/TCM/TLG/VHC/VIB/VPB + DGC). Đang transition sang custom30V theo Option A (bán dần, đã chọn hướng, dispatch DollarBill soạn plan) |
| Cron thực thi thật | run_bot.sh sáng/chiều, bot_heartbeat.sh, lunch-pkill | Thêm cùng bộ cron 2026-07-06 tối — tự động y hệt SpaceX |
| Plan 2026-07-13 | HOLD, 0 lệnh, `approved_by=auto` | 2 lệnh (SELL VIB + 1), `approved_by=None` — **cần user duyệt tay trước preflight 08:45 07-13** |

**Neutral parking:** cả 2 account cùng dùng `trading_rules.json` `neutral_parking` default 0.70 (xem §1) — không có override riêng account nào tại thời điểm này.

**Known gap:** `daily_nav_snapshot.py` chưa tính đúng P&L cho vị thế legacy ZaloPay (thiếu lịch sử FILL nội bộ) — NAV/active_nav đúng, P&L breakdown cho báo cáo cần việc riêng.

**AlphaLens Paper Portfolio** (DollarBill phụ trách): FPT@70,200 + ACB@22,650 + MBB@25,200 + HDB@25,850 (equal-weight 25%/tên), benchmark entry VNINDEX 1860.01, tracking 2026-07-01→2026-09-30, Taylor audit cuối kỳ.

**Workflow ngày trading đầy đủ (T2-T6, ICT — giờ chuẩn tắc ở `kb/ops_runbook.md`):** 19:00 `bq_freshness_check.sh` → 21:00 `send_plan_report.sh` → 08:20 `ops_health_check.sh` (tự kiểm vận hành trước phiên) → 08:45 `preflight_check.sh` → 09:05 `run_bot.sh --auto-otp` → 11:30 nghỉ trưa → 12:45 `ops_health_check.sh` lần 2 → 13:00 resume chiều → ~14:50 ATC → 19:10 `eod_trading_report.sh` (+ `daily_nav_snapshot.py`). 3 Discord topic tách biệt: Trading Daily (vận hành sống), DollarBill plan channel (lập kế hoạch), Trading report (báo cáo tổng hợp ngày/tuần/tháng). Chi tiết đầy đủ + cron mapping: `kb/current_ops.md`.

**Vận hành hàng ngày = tự phát hiện lỗi → tự sửa → báo cáo** (mandate 2026-07-07): `kb/ops_runbook.md` + `bin/ops_autofix.sh`. Ranh giới cứng KHÔNG BAO GIỜ tự sửa: trade plan, `trading_rules.json`, logic đặt lệnh, dòng cron thực thi, xoá dữ liệu, `BOT_STOP`.

---

## 6. Risk & Compliance

**Margin conventions (KHÔNG nhầm lẫn):**
- DNSE: equity-ratio per-symbol (margin call ≤40%, force-sell ≤30%).
- PHS: collateral-coverage portfolio (call ≤80%, force-sell ≤75%). **PHS live BLOCKED** (chờ client credential, lỗi -700003) → PHS chạy paper.

**Cổ phiếu BANNED vĩnh viễn:** PC1, VVS, KSF, NKG, HSG (leverage traps), HVN (equity âm), VJC (PB never <1), NVL, GEG, SBA, DMC/IMP/TRA (pharma timing destroys alpha), TOS, VTP.

**DGC — hai nhánh TÁCH BIỆT, cập nhật 2026-07-06:**
1. **Compounder screen**: permanent_exclude trong `sector_watchlist_framework` (valuation lens) — KHÔNG liên quan case bên dưới.
2. **Special situation (SpaceX)**: giá 48,800 VND vs fair 83,000–95,000 VND. Half-Kelly, stop nếu CF_OA Q2 âm sâu hoặc pháp lý leo thang. DO NOT buy thêm cho đến khi hạn chế GD được dỡ.
3. **ZaloPay (legacy 47.2% NAV)**: EXCLUDED khỏi rebalancing hoàn toàn (xem §4/§5) — lý do vận hành (hạn chế GD + cảnh báo kiểm toán do khởi tố hình sự lãnh đạo 17/03/2026), KHÔNG phải lý do đầu tư (Taylor giữ vì thesis target 70-75k/12-18 tháng, +37% EV, 65% xác suất). Ước gỡ hạn chế ~11-12/2026 (Điều 42 QĐ 22 cần đủ khắc phục nguyên nhân + 6 tháng CBTT sạch liên tục — legal-vn research 2026-06-21/26/29).

**Phát hiện rủi ro sector (2026-06-30, vẫn đúng):** HPG/Steel un-capturable; VOS/Shipping leverage trap; BVH/Insurance no margin of safety; Fertilizer edge = single 2021 supercycle, không lặp lại.

---

## 7. Research Cổ Phiếu — Phát Hiện Đáng Nhớ

**8L Rating system:**
- 1/PE dominant factor (IC +0.125, hit 94%). Rating = binary gate ≤3, KHÔNG phải return tilt.
- Composite v3 LIVE: value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 VÀ CF_OA_3Y>0. **Value dominates ALL regimes** kể cả BULL (IC 1/PE +0.156 trong BULL, momentum chỉ +0.002).
- **VALUE_VERSION=v3_da PROMOTED thành default (2026-07-04, job `Taylor_20260704_111020`):** wired D&A_HEAVY route classification vào `rating_8l.py` — sửa gap EV/EBITDA cho nhóm D&A nặng (đã audit route/tên qua job `_100727` trước khi wire).
- **Composite v3 as entry-selector**: bị loại hẳn (xem §1 "đã thử bị loại").

**Sector synthesis — mở rộng từ 15 lên tới #20 sector (2026-07-05/06):**
- 15-sector sweep gốc (2026-06-30) giữ nguyên kết luận: Securities/CK (DT5G tạo alpha DUY NHẤT), Banking Tier 1, FPT Tier 1, CTR Tier 2, Rubber defensive, Pharma buy-and-hold, Shipping Tactical.
- **#16 Textile/Garment export** (2026-07-05): FX-sensitivity hypothesis **REFUTED** — verdict LENS not BOOK (sweep Rule 3 giữ nguyên qua mọi sector mới).
- **#17 Livestock/Animal-feed (hog cycle)** (2026-07-05): hog-cycle signal **CONFIRMED** (contrast rõ với textile), vẫn LENS not BOOK. Follow-up: hog price→GPM leading-indicator test (DBC/BAF) + hog−feed margin-spread proxy (2026-07-06).
- **#18 Construction (civil/industrial EPC)**, **#19 SOE governance archetype**, **#20 Holding company/conglomerate SOTP** (tất cả 2026-07-06): cùng verdict LENS not BOOK — Rule 3 của sweep giữ vững qua 20 sector.
- **Sector lens monitor** (`sector_lens_monitor.py`, 2026-07-06): 6-state monitor cho Group-A watchlist, STRONG-tier calibration, tích hợp daily 8L Telegram.

**ConvergePort (DC-book) research (2026-07-06, nhiều job cùng ngày):** double-confirm sector-lens ∧ 8L≤2 converge portfolio. Kết luận chính: KHÔNG thay thế 2-book V2.4 (test as full active-book REPLACEMENT bị bác — MaxDD sâu hơn kể cả có DT5G state-gate); vai trò đúng = **NEUTRAL idle-cash waterfall layer** (xem §1). UNION(OR) vs double-confirm(AND): AND thắng. Capacity-appropriate sleeve size đã tính riêng.

**Paper-trading program reorg (2026-07-07, job `Taylor_20260707_132048`):** audit 22 script → 9 chương trình registry chính thức (`kb/paper_programs_registry.json`). **Phát hiện quan trọng:** `pt_v22_dt5g` (V2.3) KHÔNG PHẢI paper mirror — nó là **SỔ TÍN HIỆU PRODUCTION** (`trading_bot/strategies.py` đọc trực tiếp để build plan LIVE cho SpaceX/ZaloPay) — KEEP bắt buộc, retire nhầm = giết plan generation live. `pt_v4_dt5g` giữ làm control-arm (review checkpoint 2026-12-01). 6 step retired (window đã hết hoặc quyết định đã chốt từ trước — vol_spike_hedge, f_sleeve, pt_dt4_vs_tq34b_ab, amh_cockpit, pt_sleeve_allocator, ecology_dashboard — reversible bằng bỏ comment).

**Macro/khác:** ACB OShares stale ex-date (2026-06-22, PE thực 8.87). DRI Q3'26 nowcast ~40-42B NP. HVN routing bug (ICB 5751 rơi vào COMPOUNDER route sai, fix scheduled post-go-live — **chưa xác nhận đã fix, cần kiểm lại**). SBV TT25/2026 nới trần vốn ngắn hạn 30→40% hiệu lực 07-01, credit easing chưa kích hoạt DT5G.

---

## 8. Incidents & Lessons Learned

> Bảng tóm tắt — chi tiết đầy đủ + self-check trong `kb/incidents/` (index: `kb/incidents/index.md`).

| Ngày | Incident | Root Cause | Fix | Bài học |
|---|---|---|---|---|
| 2026-06-22 | Zombie Mafee | stale bridge-pointer.json | clear bridge + restart | watchdog.sh ZOMBIE branch |
| 2026-06-23 | DT5G SEV2 DEGRADED | 3 bugs từ commit 10ae395 | fix paths cùng ngày | Test pipeline sau mọi refactor |
| 2026-06-26 | DDV ex-date sai 6 ngày | Vendor data báo sai ex-date | Corp-action v2 detector | Không tin vendor, cross-check |
| 2026-06-27 | Auto-callback loop ~2h | dispatch --bg job trigger callback vòng lặp | Guard tại dispatch.sh:172 | Callback chains phải có terminator |
| 2026-06-28 | DQ-1/DQ-2 data quality | tail(10) recompute + profit_* ffill | Fix scope 2 bug | Indicator windows full-history; profit_* train-only |
| 2026-06-30 | Mafee 0-byte log | Permission classifier block headless khi thao tác tiền | run_bot.sh (Python direct) | LLM headless ≠ deterministic execution |
| 2026-07-02 | Double-buy near-miss | Lock không cứu process chết giữa place_order và save_state | `_ghost_tickers` + atomic save (commit e1d9b7c) | Idempotency ≠ locking — xem coding_guidelines.md §5 |
| 2026-07-03 | Weekly report VHM fake loss | `avg_cost_vnd` đọc field `ref_px_approx` (ước tính, sai mục đích) làm cost basis thật | `verify_account_snapshot.py` pipeline bắt buộc | Field tên đúng + giá trị hợp lý ≠ đã verify — coding_guidelines.md §6 |
| 2026-07-05 | Wave1/H8a-tiebreaker overfit | OOS edge tăng đúng luật nhưng carry hết bởi 2 năm | LOO phát hiện, route qua skeptic → KHÔNG wire | Per-year leave-one-out bắt buộc khi OOS mỏng năm |
| 2026-07-06 | Plan file versioning gap | `load_plan()` chỉ đọc tên file chính thức, `_v2` vô hình với bot | Luôn promote/overwrite tên chính thức khi plan duyệt lại | Không dùng suffix cho bản đã duyệt |
| 2026-07-06 | dnse_raw shared-log account leak | Log balances dùng chung ngày, không gắn account | Gắn account_no/label mọi record + filter đúng account | Log dùng chung nhiều tenant phải tag nguồn ngay từ ghi |
| 2026-07-06 | R3-CSV canonical overwrite risk (pattern lặp) | Config axis không phản ánh trong filename output | Rule: mọi axis ảnh hưởng số → đổi filename/OUT_CSV override | coding_guidelines.md §8 |
| 2026-07-06 | "Margin netting" hypothesis sai | Balance API stale giữa phiên bị hiểu nhầm thành netting cố ý | Đính chính: NAV = Cash+Stock−Debt đơn giản, dùng bản đọc mới nhất | Đừng dựng model bù trừ khi chỉ là staleness |
| 2026-07-07 | ccdb model config 2 tầng song song | Thread override DB > global DB > .env, .env không hiệu lực nếu DB có row cũ | Đồng bộ cả 3 nơi, dọn override sai format | Kiểm TẤT CẢ tầng config trước khi kết luận "đã đổi" |
| 2026-07-07 | Agent(isolation:worktree) tưởng nhầm là background | isolation ≠ background; job xong sạch mà Mike không biết | Chuyển cơ chế chính sang ScheduleWakeup poll ngắn | Đừng suy đoán semantics tool — kiểm schema trước khi dùng |
| 2026-07-09 | T+1 plan giá lệch dùng BQ stale | BQ chỉ sync qua đêm, script chạy trước đó đọc "hôm nay" = hôm qua | Bright-line: same-day PHẢI dùng DNSE API | coding_guidelines.md §6 — cấu trúc, không phải thỉnh thoảng |
| 2026-07-10 | DollarBill tính sai ngày T+1 (thứ Bảy thay vì thứ Hai) | Giao phép tính lịch tất định cho LLM tự suy luận giữa task khác | Fix commit e3001fa, dùng `next_trading_day()` có sẵn | Giá trị tính tất định được → tính bằng code, truyền literal, không giao LLM |
| 2026-07-10 | DT5G BULL-commit giả (EW-leg stale, xem §2) | Reorg 06-21 path writer/reader lệch, không freshness-check nội bộ chain | Fix commit 498c3a6, publish chờ cron/manual | Chain nhiều bước cần post-chain mtime assertion generic, không phải 1-1 patch |

**Pattern đang mở (chưa đóng hẳn):** "code âm thầm đọc/dùng dữ liệu chưa sẵn sàng, che giấu bởi tolerance/giả định lịch trình rộng" — đã vá 1 lát cắt hẹp (BQ-vs-DNSE, 07-09) và 1 lát cắt khác lộ ra ngay sau đó dưới dạng khác (DT5G cron-order + chain freshness, 07-10). Bus question `retro-pattern-recurring-dataprovenance-2` đề xuất tổng quát hoá quy tắc freshness-check cho MỌI cặp pipeline producer→consumer nội bộ — **vẫn chờ user/Mike xác nhận hướng**, chưa tới ngưỡng escalate mức cao hơn.

---

## 9. Quy Ước & Tra Cứu Nhanh

**Naming KB:**
- `_P0` = quarter hiện tại, `_P1` = 1 quý trước, `_P4` ≈ 1 năm trước.
- `_T1` = 1 ngày GD trước, `_T1W` = 1 tuần trước.
- `_Min3Y/5Y` = minimum N năm (quality floor).
- `_Trailing` = sum 4 quý gần nhất (TTM).

**Tài khoản (số cụ thể trong `secrets/`, KHÔNG ghi đây):**
- SpaceX: DNSE, live, margin. ZaloPay: DNSE, live, cash-only (excluded_tickers: DGC). RocketX_Deal: DNSE, paper.
- loan_id: cash=1841, margin_rocketx=1840 (SpaceX).

**File quan trọng:**
- `data/trading_rules.json` — kill-switches + sizing rules (v2.1, gồm `neutral_parking` + `risk_dial_override`).
- `data/BOT_STOP` — kill-switch tức thì.
- `data/results_registry.md` — pin mọi backtest result có audit trail (bao gồm DSR/PBO annex).
- `data/trade_plans/plan_<Account>_YYYY-MM-DD.json` — plan hàng ngày, per account (SpaceX/ZaloPay). Luôn overwrite tên file chính thức khi duyệt lại — không dùng suffix `_v2`.
- `data/execution_logs/nav_history_<Account>.csv` — nguồn NAV duy nhất mọi báo cáo ngày/tuần/tháng dùng chung.
- `kb/incidents/` (index: `kb/incidents/index.md`) — nhật ký sự cố đầy đủ. `kb/ops_runbook.md` — quy trình tự phát hiện/tự sửa vận hành hàng ngày.
- `kb/paper_programs_registry.json` — 9 chương trình paper-trading chính thức (bao gồm `pt_v22_dt5g` = production signal book, KHÔNG phải paper mirror).
- `kb/archive/` — raw consolidation blocks cũ (không cần đọc thường xuyên).

**Cron quan trọng (ICT)** — *nguồn sống là `kb/ops_runbook.md` (bảng timeline) + `crontab -l`; bảng dưới chỉ là bản tóm, đã đối chiếu 2026-07-30:*
- 19:00 T2-T6: `bq_freshness_check.sh` → DollarBill lập plan T+1 *(đổi từ 17:30, 2026-07-10)*.
- 21:00 T2-T6: `send_plan_report.sh` → gửi plan qua Telegram + Discord *(đổi từ 19:30, 2026-07-10; thêm 23:00 `--second-chance` từ 2026-07-13)*.
- 08:20 & 12:45 T2-T6: `ops_health_check.sh` — tự kiểm vận hành, post Trading Daily.
- 08:45 T2-T6: `preflight_check.sh`.
- 09:05 & 13:00 (sau nghỉ trưa) T2-T6: `run_bot.sh --auto-otp`.
- 19:10 T2-T6: `eod_trading_report.sh` (+ `daily_nav_snapshot.py`) → Trading report *(đổi từ 15:00, 2026-07-15, user duyệt — chạy sau publish DT5G 19:01 để "tình trạng thị trường" là regime HÔM NAY)*.
- 23:45 T2-T6: `sync_bq_cache_daily.sh`.
- 00:30 daily: `daily_retro.sh` (đổi từ 22:00, 2026-07-10).
- 00:00 daily: `backup.sh` → GitHub.

---

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9, file này). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md. Incidents: kb/incidents/index.md.
