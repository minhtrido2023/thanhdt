# Mike fleet — KNOWLEDGE (canonical)

> **Nguồn sự thật của toàn đội.** Được Mike biên tập thủ công, consolidator chỉ append.
> Agent đọc `context_pack.md` (distilled, ~8KB). File này dành cho tra cứu sâu và weekly review.
> Raw event log: `kb/archive/`. **Curated lần cuối: 2026-06-30 (Mike). KB v640.**

---

## 1. Chiến lược trung tâm — V2.4 Production

**Định nghĩa:** V2.4 = V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout, depth OFF) + HAG eq_flag fix. **Go-live: 2026-07-01**, tài khoản SpaceX (DNSE 0002023347), 1B VND.

**Cấu trúc 2 book:**
- **BAL** — momentum SIGNAL_V11 (yieldcombo rank: 1/PE + 1/PCF, v3 composite bị loại vì IS-overfit)
- **LAG** — PEAD/earnings drift. Allocator w_LAG theo state {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.

**Performance đã pin (threads=1, self-check 0 VND):**
- R3 NEUTRAL-only @50B: CAGR **28.05%** / Sharpe 1.87 / DD −18.8% / Calmar 1.50
- R1 @20B: CAGR **29.01%**
- Bootstrap 5th-pct CAGR: 18.6%, P(loss)=0. MaxDD understated vs bootstrap (−28.6% vs hist −17.6%).

**Parking — custom30V:**
- NEUTRAL parking: **production (30 mã, cap 0.10)** — phần tin cậy nhất: +7.4pp Full.
- **(30, 0.15) là OVERFIT** — walk-forward bác.
- Bull parking: chỉ bật khi NAV ≥150B. Custom30B bull-sleeve FAIL walk-forward, không hạ NAV threshold.

**Các thứ đã thử và BỊ LOẠI (không wire):**
- Custom30V permanent-exclude 7 tên: HURTS −1.0pp (walk-forward bác). DO NOT wire.
- LAG fresh-high-SUE tilt 3 tầng: −0.66pp vs binary. Giữ LAG nguyên.
- Hold-neutral test (exit CAPIT khi về NEUTRAL): thoát sớm 14/15 episode, −47B VND. Giữ CAPIT_HOLD=60td.
- Stability floor (ROE_Min<0 cap): −0.45pp CAGR, bác.

**V2.5 (tương lai):** = V2.4 + leverage layer (deep-cheap gate, MGE=1.5, ~2 episodes/decade). Chưa live.

**Kill-switches (wired trading_rules.json v1.7, duyệt bởi Spyros):** SBV>7.5%, pb_z rising >−0.3 while episode active, episode DD>−12%.

**Nguyên tắc audit:** self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) TRƯỚC khi wire. Edge full-period mà rớt OOS = overfit → loại. Pin kết quả vào `data/results_registry.md`.

---

## 2. DT5G — Market Regime Gate

**Production state:** bảng `tav2_bq.vnindex_5state_dt5g_live`, đọc qua `get_gated_state()`.
**KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions), KHÔNG phải DT5G (49 transitions).

**Trạng thái hiện tại (2026-06-30):** NEUTRAL(3), DT5G_macro HEALTHY sau khi pipeline được refresh 18:37 ICT (trước đó stuck 2026-06-19 trong >7 ngày). Plan 2026-07-01 tạo trong window DT4_only — outcome NEUTRAL giống DT5G_macro.

**Incident đáng nhớ:** 2026-06-23: SEV2 DEGRADED do 3 bugs từ commit 10ae395 phá paths. Fix xong cùng ngày. EASING_FLOOR đã disabled (re-risk chỉ qua price-based DT base).

**Nhãn bảng đã chốt (2026-06-26):** `vnindex_5state` = v3.4b BASE. `vnindex_5state_dt5g_live` = DT5G thật. Đừng nhầm.

---

## 3. Kiến trúc Fleet & Dispatch

**Companion daemon (systemd):** Chỉ còn **Mike + Taylor**. DollarBill/Mafee headless on-demand. Winston/Spyros/Wendy đã gỡ daemon (2026-06-25) → native subagent `Agent(subagent_type=...)`.

**Cơ chế dispatch đúng:** `bin/dispatch.sh` (headless `claude -p`). Directive/inbox deprecated cho task — chỉ dùng cho mandate dài hạn.

**Routing guards (2026-06-27):**
1. Self-dispatch (from==id) → chặn, exit 2.
2. Agent → Mike: phải escalate qua event `question`, KHÔNG spawn Mike headless.

**Incident quan trọng — auto-callback loop (2026-06-27):** Taylor↔Winston dispatch lẫn nhau ~2h, 700+KB noise. Fix: dispatch.sh:172 guard — prompt bắt đầu `[AUTO-CALLBACK` không spawn callback tiếp.

**Execution pattern đúng cho trading:**
- `bot_execute.py --auto-otp` (Python, deterministic) thay vì dispatch Mafee headless cho đặt lệnh.
- Root cause Mafee 0-byte log: permission classifier block headless `claude -p` khi thao tác tiền thật.
- `bin/run_bot.sh` wrapper đã viết (2026-06-30): gọi bot_execute.py, Discord notify, publish bus event.

**Quy trình an toàn tiền thật:** Taylor đặt rule (user duyệt) → DollarBill lập plan (user duyệt) → `run_bot.sh` / Mafee chỉ thực thi lệnh CÓ trong plan → `data/BOT_STOP` = kill-switch tức thì.

**Quant-skeptic (2026-06-25):** native subagent `~/.claude/agents/quant-skeptic.md`, runner `bin/verify_finding.sh`. Rule: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.

---

## 4. Hạ tầng Kỹ Thuật

**BQ Local Cache (DuckDB, 2026-06-25):**
- 12 bảng BQ → parquet local `data/bq_cache/`, query ~100ms (vs 5-15s BQ).
- Env `BQ_LOCAL_CACHE=data/bq_cache` wire trong `wc_env.sh` + `dispatch.sh`.
- Sync daily 23:45 ICT (`sync_bq_cache_daily.sh --delta`). Fallback: nếu cache chưa verify → gọi BQ bình thường.
- **Non-determinism bug (fixed 2026-06-25):** DuckDB default threads=4 → ~0.2pp CAGR spread. Fixed threads=1 (commit 1325bf2). Self-check 0 VND KHÔNG đảm bảo reproducibility — phải pin threads.

**Auto-OTP Gmail (2026-06-26):** `gmail_otp_reader.py` đọc DNSE OTP qua Gmail OAuth2. Fix: dùng `internalDate` filter (không dùng `newer_than` — bị Gmail API ignore). Credential: `secrets/gmail_oauth_token.json`.

**Bot execution:**
- `bot_execute.py --auto-otp`: OTP + token + đặt lệnh trong 1 lệnh.
- `bot_prepare_plan.py`: tạo plan T+1. `next_trading_day()` đã xử lý T7/CN + ngày lễ cố định (1/1, 30/4, 1/5, 2/9). `_VARIABLE_HOLIDAYS` để trống, thêm thủ công theo thông báo SSC/HoSE.
- `executor.py`: SIZE-ADAPTIVE fill (DIP <2% ADV, TWAP ≥2% ADV). MODIFY quirky DNSE (HTTP 500 nhưng creates new order_id → must re-poll). Price unit = VND (không phải nghìn đồng).
- `_publish_bot_event()`: fire-and-forget lên Mike bus khi STEP_FAIL hoặc fill_lagging.

**Watchdog & monitoring:**
- `bin/watchdog.sh` (cron 10'): DOWN restart + ZOMBIE (clear bridge-pointer + restart).
- `bin/is_serving.py`: oracle liveness thật (không tin systemctl is-active).
- `bin/fleet_health.sh`: bảng sức khỏe tức thì.
- `bin/notify.sh` → Telegram @AbV6_bot, dedup 300s, kill-switch `state/NOTIFY_OFF`.
- Job board OVERDUE scan: session_start.sh + watchdog.sh đều scan → Discord alert khi job stuck.

**Dispatch monitoring:**
- Completion notify: đọc `agents/Mike/state/ccdb_thread_id` (persist bởi session_start.sh).
- Stale/empty log detection: alert tại 60s (empty) và 120s (stale).
- Milestone Discord: chỉ tại 10m và 30m (không spam mỗi 5m).

**Data quality bugs đã phát hiện (2026-06-28):**
- DQ-1 HIGH: `process_stock_indicator` chỉ ghi `tail(10)` rows → corp-action recompute sai indicator windows. Fix: force full-history recompute.
- DQ-2 HIGH: `profit_*` forward-fill trong app-dataset → fabricates forward-looking values cho live row. KHÔNG dùng `profit_*` filter live.
- DQ-6: `get_gated_state()` raises `FrozenStateError` nếu DT5G row cũ >2 ngày trên live call.
- Corp-action v2 detector: adj Close ≥3% DROP + raw Price stable (<1.5%) → thật. Tránh ETL price-catchup false positive.

**Backup:** `~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private), branch `main` (code) + `mike-fleet` (fleet config+KB). Daily 00:00 ICT.

---

## 5. Go-Live SpaceX — Trạng Thái Hiện Tại

| Mục | Trạng thái |
|---|---|
| Tài khoản | DNSE tiểu khoản **0002023347** (SpaceX), 1B VND confirmed |
| enabled | **true** (user flip 2026-06-30) |
| Plan 2026-07-01 | **APPROVED** bởi user — 23 BUY orders, 93.8% NAV, state NEUTRAL/DT5G_macro/HEALTHY |
| Execution | `run_bot.sh --auto-otp` via cron 09:05 ICT 2026-07-01 |
| Loan package | cash=1841, margin_rocketx=1840 |
| Bot config | `secrets/trading_bot_accounts.json`, KHÔNG ghi KB |

**AlphaLens Paper Portfolio:** 4 vị thế (FPT@7020 + 3 khác), paper tracking 2026-07-01 đến 2026-09-30. DollarBill phụ trách.

---

## 6. Risk & Compliance

**Margin conventions (KHÔNG nhầm lẫn):**
- DNSE: equity-ratio per-symbol (margin call ≤40%, force-sell ≤30%).
- PHS: collateral-coverage portfolio (call ≤80%, force-sell ≤75%).
- **PHS live BLOCKED** (chờ client credential, lỗi -700003) → PHS chạy paper.

**Cổ phiếu BANNED vĩnh viễn:** PC1, VVS, KSF, NKG, HSG (leverage traps), HVN (equity âm), VJC (PB never <1), NVL, GEG, SBA, DMC/IMP/TRA (pharma timing destroys alpha), TOS, VTP.

**DGC — hai nhánh TÁCH BIỆT:**
1. **Compounder screen**: permanent_exclude trong `sector_watchlist_framework` (valuation lens) — KHÔNG liên quan đến case bên dưới.
2. **Special situation**: Giá 48,800 VND vs fair 83,000–95,000 VND (no-legal-risk). Half-Kelly, stop nếu CF_OA Q2 âm sâu hoặc pháp lý leo thang. DO NOT buy thêm cho đến khi `hạn chế giao dịch` được dỡ.
   - Trạng thái 2026-06-30: Cảnh báo (QĐ 544) + Hạn chế GD (QĐ 448) đang song song. Nộp BCTC KHÔNG tự động dỡ hạn chế.

**Phát hiện rủi ro sector (2026-06-30):**
- HPG/Steel: un-capturable by value-trough screen — không có edge có thể khai thác.
- VOS/Shipping: leverage trap, loại.
- BVH/Insurance: fair value = near/below book, không có margin of safety.
- Fertilizer: edge = single 2021 urea supercycle, không lặp lại → cycle-gated lens only.

---

## 7. Research Cổ Phiếu — Phát Hiện Đáng Nhớ

**8L Rating system:**
- 1/PE dominant factor (IC +0.125, hit 94%). Rating = binary gate ≤3, KHÔNG phải return tilt (IC trong gate là NEGATIVE). FSCORE thêm +0.031 marginal.
- Composite v3 live (thay v2): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 VÀ CF_OA_3Y>0.
- **Value dominates ALL regimes:** IC 1/PE mạnh nhất trong BULL (+0.156). Momentum IC trong BULL = +0.002. Đòn bẩy chế độ = EXPOSURE, không phải SELECTION.

**Sector synthesis (15 sectors, 2026-06-30):**
- **Securities (CK)**: DT5G adds RETURN (27.74%/DD−31.7% gated vs 17.74%/DD−65.7% ungated) — sector DUY NHẤT DT5G tạo alpha.
- **Banking (MBB/ACB/HDB)**: Tier 1 BUY NOW. PB below Gordon floor. 74% đã trong custom30V.
- **FPT (Tech)**: Tier 1 BUY NOW. PE 12.4 < entry 16.8. EVEB<entry → +26pp fwd-12M, 88% win rate.
- **CTR (Telecom infra)**: Tier 2 Accumulate. EVEB<9 → +132% fwd-12M/100% win (n=23). EVEB hiện ~10.1.
- **Rubber (DPR/PHR)**: Defensive deep-value: DD −12.5% vs mkt −43% nhưng return âm. DRI = rating 2 (cyclical-peak warning PE 5.9).
- **Pharma (DHG/DBD)**: Buy-and-hold ONLY — timing screens destroy alpha.
- **Shipping (HAH)**: Tier 3 Tactical (EVEB 4.3). VOS loại (leverage).

**ACB note (2026-06-22):** OShares stale ex-date 2026-06-15 → PE thực 8.87 (không phải 7.85). PB thực 1.46.

**DRI Q3'26 nowcast (2026-06-27):** ~40–42B NP (+8% YoY). 2026 FY ~+30–40% YoY vs 2025.

**HVN routing bug (2026-06-27):** ICB 5751 (airline) falls into COMPOUNDER route by default (no ROE_Min floor). Fix scheduled post-go-live.

**SBV TT25/2026 (2026-06-22):** Nới trần vốn ngắn hạn 30→40% cho vay TDH, hiệu lực 2026-07-01. Credit easing cho banks/RE. DT5G chưa bị kích hoạt.

---

## 8. Incidents & Lessons Learned

| Ngày | Incident | Root Cause | Fix | Bài học |
|---|---|---|---|---|
| 2026-06-22 | Zombie Mafee | stale bridge-pointer.json | clear bridge + restart | watchdog.sh ZOMBIE branch |
| 2026-06-22 | ticker table bị truncate 73% | Windows-side ETL partial reload | ETL re-run | Verify BQ row count sau ETL |
| 2026-06-23 | DT5G SEV2 DEGRADED | 3 bugs từ commit 10ae395 | fix paths cùng ngày | Test pipeline sau mọi refactor |
| 2026-06-26 | DDV ex-date sai 6 ngày | Vendor data báo sai ex-date | Corp-action v2 detector | Không tin vendor, cross-check |
| 2026-06-27 | Auto-callback loop ~2h | Mọi dispatch --bg job trigger callback → vòng lặp vô hạn | Guard tại dispatch.sh:172 | Callback chains phải có terminator |
| 2026-06-28 | EOD health CRITICAL | Pipeline reorg phá paths | Fix paths cùng ngày | CI check sau pipeline refactor |
| 2026-06-28 | DQ-1: tail(10) bug | process_stock_indicator chỉ ghi 10 rows | Force full-history recompute | Indicator windows phải full-history |
| 2026-06-28 | DQ-2: profit_* ffill | App-dataset ffill fabricates forward values | Fix ffill scope | profit_* chỉ dùng train, KHÔNG live |
| 2026-06-30 | Mafee 0-byte log 20 phút | Permission classifier block headless claude khi thao tác tiền thật | run_bot.sh (Python direct) | LLM headless ≠ deterministic execution |
| 2026-06-30 | DT5G stuck 11 ngày | v3.4b pipeline output frozen | Manual refresh 18:37 ICT | Monitor pipeline freshness daily |

---

## 9. Quy Ước & Tra Cứu Nhanh

**Naming KB:**
- `_P0` = quarter hiện tại, `_P1` = 1 quý trước, `_P4` ≈ 1 năm trước.
- `_T1` = 1 ngày GD trước, `_T1W` = 1 tuần trước.
- `_Min3Y/5Y` = minimum N năm (quality floor).
- `_Trailing` = sum 4 quý gần nhất (TTM).

**Tài khoản (số cụ thể trong `secrets/`, KHÔNG ghi đây):**
- SpaceX: DNSE, live. RocketX_Deal: DNSE, paper.
- loan_id: cash=1841, margin_rocketx=1840 (SpaceX).

**File quan trọng:**
- `data/trading_rules.json` — kill-switches + sizing rules (v1.7, Spyros-approved).
- `data/BOT_STOP` — kill-switch tức thì, tạo file là Mafee dừng.
- `data/results_registry.md` — pin mọi backtest result có audit trail.
- `data/trade_plans/plan_SpaceX_YYYY-MM-DD.json` — plan hàng ngày.
- `kb/archive/` — raw consolidation blocks cũ (không cần đọc thường xuyên).

**Cron quan trọng (ICT):**
- 17:30 T2-T6: `bq_freshness_check.sh` → DollarBill lập plan T+1 (nếu BQ fresh).
- 19:30 T2-T6: `send_plan_report.sh` → gửi plan qua Telegram + Discord để user duyệt.
- 09:05 (T2-T6 khi cần): `run_bot.sh --auto-otp` → thực thi plan.
- 23:45 T2-T6: `sync_bq_cache_daily.sh` — sync BQ local cache.

---

*Phần dưới đây do consolidator tự động append (30'/lần). Mike review và compress vào canonical trên mỗi cuối tuần.*


## Consolidation 2026-06-30T16:07:01Z
- [2026-06-30T15:16:01Z] Mike/decision — alphalens-paper-setup: {"action": "AlphaLens Paper Portfolio initialized", "positions": {"FPT": 70200, "ACB": 22650, "MBB": 25200, "HDB": 25850}, "benchmark_entry": 1860.01, "start": "2026-07-01", "end": "2026-09-30", "manager": "DollarBill", "audit_trigger": "trig_01Sci1kqYgTjk6hjjFDnCpFM", "tracking_file": "data/alphalens_paper.json", "note": "Equal-weight 25% per name. DollarBill bao gồm trong daily Discord report. Taylor audit 2026-09-30."}

## Consolidation 2026-06-30T16:43:57Z
- [2026-06-30T16:40:18Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "in_progress", "note": "read 3 composite scripts; checking input data + existing outputs"}
- [2026-06-30T16:40:31Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "still_running", "elapsed_min": 1, "job_id": "Taylor_20260630_163930"}
- [2026-06-30T16:40:58Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "in_progress", "note": "registry shows v3-composite-as-SELECTOR already ruled IS-overfit 06-22; running sweep + ic_composites scripts fresh for IS/OOS"}
- [2026-06-30T16:41:31Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "still_running", "elapsed_min": 2, "job_id": "Taylor_20260630_163930"}
- [2026-06-30T16:42:32Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "still_running", "elapsed_min": 3, "job_id": "Taylor_20260630_163930"}
- [2026-06-30T16:43:32Z] Taylor/heartbeat — Taylor_20260630_163930: {"status": "still_running", "elapsed_min": 4, "job_id": "Taylor_20260630_163930"}
- [2026-06-30T16:43:36Z] Taylor/finding — composite-mới-methodological-review-NO-GOLIVE: {"job": "Taylor_20260630_163930", "question": "Review phương án composite mới (thuần methodological) — go-live?", "verdict": "NO — giữ production as-is cho go-live 2026-06-30", "auto_run_today": "KHÔNG có (scripts không trên cron; ran fresh now)", "candidates": {"composite_v3_sweep(value lens — ĐÃ LIVE)": {"result": "v3 ey+cfy+ps coverage-aware BEATS v2(pb_z+1/PE): broad 2M IC 0.077->0.090; per-route COMPOUNDER 0.103/CYCLICAL 0.113/CONSUMER 0.129; weight plateau FLAT 0.089-0.091; by-year 2014-2026 ALL positive (IS+OOS clean)", "read": "RE-VALIDATES production v3 lens robust — không cần đổi"}, "fa_ic_composites(drop neg-IC axes — LEGACY 7-axis, NOT in rating_8l.py v2)": {"result": "health IC -0.091, valuation -0.104 negative. CORE4 IS 0.134/OOS 0.093/ALL 0.104 vs CUR7 IS 0.112/OOS 0.088/ALL 0.095 — robust-signed both windows + simpler; BUT OOS gain tiny (+0.0045), decile spread WASH (CORE4 5.89<CUR7 6.53pp), composite không ở production", "read": "clean IC hygiene nhưng immaterial + off-production-path"}}, "why_no": ["selector=yieldcombo rating-blind, gate binary <=3 -> rating-composite tweak barely moves NAV", "registry đã chốt v3-composite-AS-SELECTOR = IS-overfit (OOS -0.78pp, THREAD b 06-22)", "value-lens v3 đã live + re-confirmed robust", "META rule: de-risk go-live, không thêm phức tạp"], "durable_export": "Nếu sau này dùng linear multi-axis rating làm production: DROP health+valuation (neg IC), equal-weight CORE4 là robust-simplest. Post-go-live hygiene optional, phải qua NAV self-check trước. KHÔNG phải go-live blocker/enhancer.", "logged": "data/results_registry.md"}
