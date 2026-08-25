# Mike fleet — context pack (v2525)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-08-25T05:59:41] Taylor/finding — dt5g-pre2014-validation-PASS: {"job": "Taylor_20260825_055651", "check": "Step 1 - DT5G sanity pre-2014 via get_macro_state() direct (bypass get_gated_state wrapper)", "critical_bugfix": "st …
- [2026-08-25T06:11:22] Mike/finding — daily-retro-2026-08-24-finalized: {"file": "kb/incidents/retro/retro-2026-08-24.md", "verified_by": "Wags", "verdict": "GAPS_FOUND_AND_FIXED", "gap_summary": "draft understated leak severity - o …
- [2026-08-25T06:36:30] Taylor/finding — backtest-2008-v24-full: {"job": "Taylor_20260825_055651", "status": "DONE", "control_leg_pass": true, "oos_2014_2026_B": {"CAGR": "28.71%", "Sharpe": 1.9, "MaxDD": "-17.6%", "Calmar":  …
- [2026-08-25T07:29:46] quant-skeptic/verification — ✅ CONFIRMED VERIFY: backtest-2008-v24-full: {"finding_topic": "backtest-2008-v24-full", "verdict": "CONFIRMED", "confidence": "medium", "checks": {"look_ahead_leak": "fail — the ancillary PIT-filter's CPI …
- [2026-08-25T07:47:30] Taylor/finding — backtest-2008-v24-corrections-applied: {"event_count_fixed": {"claimed": 5, "actual": 10, "lever_gate_events_claimed": 1, "lever_gate_events_actual": 2, "lever_gate_dates": ["2010-08-09", "2012-08-23 …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-08-21 (token-cost trim #4 — warm sections → `kb/current_ops_ext.md`;
> giữ lại hot path: kill-switch, trading status, signal holds, routing rules).
> Chi tiết CAPIT/domain-constraint/due-diligence/cron/daemon: `cat kb/current_ops_ext.md`

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking **80%** idle cash (config F1, đổi từ 70% ngày 2026-08-04, `trading_rules.json` `neutral_parking.default_park_of_idle_pct`). run_bot.sh 09:05 ICT T2-T6. NAV: `nav_history_SpaceX.csv` hoặc EOD report.
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, CASH-ONLY. **DGC EXCLUDED** (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026). Sizing dùng `active_nav`. Cùng target parking 80% (không có override riêng).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking đến 2026-09-30. DollarBill phụ trách.
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,2tr / ZaloPay ~38,8tr (đo 08-19), đã cộng NAV tự động — KHÔNG phải `availableCash`, cần rút T+1. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.

## Signal holds — KHÔNG tự thay đổi trước checkpoint
- **VPI/BAL**: HOLD đến review **2026-09-16**. Lý do: hiệu suất BAL gần đây chưa tốt, chưa phải thiếu tiền. Quyết định user 08-19 (`decided_by: user`). Tín hiệu BAL mới → escalate hỏi, không tự mua hay tự hold theo logic cũ.
- **SpaceX plan 2026-08-21**: HOLD_ALL (VPI signal_hold đến 09-16).
- **ZaloPay plan 2026-08-21**: HOLD_ALL (VPI signal_hold đến 09-16).

## CAPIT — vị thế THẬT đang giữ (`capit_fired` ≠ "đang giữ")
⚠️ `capit_fired` tính lại mỗi phiên, KHÔNG phải cờ vị thế. Đọc `data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`). **PNJ EXCLUDED** (due-diligence gate, 07-20, TTL ~08-23). Chi tiết: `kb/current_ops_ext.md § CAPIT`.

## Domain-constraint layer
- **P1 LIVE**: `filter_lag_rating_orders()` — gate 8L rating≤3 tầng ORDER. 14/14+22/22 selfcheck.
- **P0 ACTIVE (HARD BLOCK)**: `check_plan_funding()` trong `bot_execute.py:536` từ 08-04. Chi tiết 2 bug đã vá (08-07): `kb/current_ops_ext.md § Domain-constraint`.

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate 2026-07-07)
Ranh giới cứng (KHÔNG tự sửa): trade plan, trading_rules.json, logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Chi tiết: `kb/ops_runbook.md`.

## Workflow ngày trading — Discord topic routing
- **Trading Daily (1521470705563340910)** — preflight, run_bot, heartbeat, ops_health_check.sh
- **DollarBill plan (1521183164364754974)** — lập kế hoạch. **Mirror duyệt plan vào đây dù đang ở topic khác.**
- **Trading report (1522576692638388364)** — báo cáo tổng hợp ngày/tuần/tháng (KHÔNG phải alert)
- Dispatch Taylor → ghi `discord_thread_id` vào job record ngay lúc dispatch, đọc lại qua `_job_thread_id`.
- Plan T+1 không sẵn sàng → ESCALATE (Telegram + Discord + bus question `plan-t1-not-ready`), KHÔNG retry tự động.

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

## Quy ước phân tích conditional — trục 2 mặc định (chốt 2026-08-22, user duyệt)

**Breadth-tercile PIT thay Value Radar zone làm trục 2 mặc định cho mọi phân tích conditional.**

Lý do:
- Value Radar zone ≈ kỷ nguyên: 54% số năm bị 1 nhãn chiếm ≥90% phiên → n_effective ~2-3 chu kỳ, không bao giờ đủ sức thống kê
- Breadth-tercile PIT (universe_pit %>MA200, phân vị rolling 252 phiên trước): 0% năm bị 1 nhãn chiếm ≥90%; 2.0× số episode so với radar

Cách tính breadth chuẩn:
- Nguồn: `tav2_mike.universe_pit` (CANONICAL)
- breadth_t = COUNT(Close_t > MA200_t | in_universe=True) / COUNT(in_universe=True)
- Phân loại phiên t: dùng breadth_{t-1} (PIT, không look-ahead cùng phiên)
- Tercile: phân vị rolling 252 phiên trước (không phân vị toàn mẫu)

Value Radar vẫn giữ vai trò DISPLAY-ONLY trong báo cáo (§6b coding_guidelines). Không wire vào sizing.

Kết quả dẫn tới quyết định: breadth-vs-radar-matrix-20260822 (Taylor, B2) + user confirm 2026-08-22.

## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`
<!-- Rút gọn 2026-08-10: mỗi dòng trước đây là 2-4 câu kể lại diễn biến. File này bơm vào MỌI
     dispatch có context_pack ⇒ tường thuật của việc ĐÃ ĐÓNG là chi phí trả lại mỗi phiên.
     Giữ đúng phần còn quyết định được hành vi sau này: TÊN · FILE · PHÁN QUYẾT (nhất là NO-GO,
     để không ai đề xuất lại). Diễn biến vẫn nguyên trong file chi tiết. -->
- 2026-08-23 Chính sách margin đơn mã sleeve fear-buy discretionary → `discretionary-margin-policy-20260823.md` — **POLICY DUYỆT, CHƯA CODE**: trần vị thế ≤3% NAV (đòn bẩy trên nền ≤1% vốn tự có), trần sleeve ≤5% NAV, phát hiện margin-call DNSE netting cấp ACCOUNT nên vô hiệu ở quy mô đơn mã ⇒ kỷ luật thoát tự áp −20% từ giá arm (không dựa broker); chưa case nào đủ điều kiện (TV1 UPCOM không marginable)
- 2026-08-23 Margin theo khoảng cách định giá + nhận diện đáy 11/2022 → `margin-valuation-spread-20260823.md` — **NO-GO** mọi cơ chế sizing/gate mới (5 vòng, Phase 1 engine quant-skeptic CONFIRMED high); `capit_margin_lever` dd52≤−20% GIỮ NGUYÊN; nhiễu harness 0,385pp ≫ hiệu ứng 0,009pp; đóng tập 7 episode, chỉ còn shadow-log spread EOD; hướng mở duy nhất = margin cấp CỔ PHIẾU trong sleeve fear-buy. **Đính chính 08-24**: thiếu trục "phòng thủ có mục tiêu" (2020/2022, dễ hồi) vs "cơ cấu tự cộng dồn" (2007-2012, không xử lý nhanh được) — 3/7 episode rất có thể là 3 sóng của 1 khủng hoảng, N độc lập thật ~4-5 không phải 7; không đổi verdict NO-GO, chỉ đổi cách đọc "phản ví dụ" 2010-08-25
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
