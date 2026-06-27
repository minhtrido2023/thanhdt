# Mike fleet — context pack (v110)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-27T02:43:34] Bob/decision — Thêm routing guard vào dispatch.sh: chặn self-dispatch + agent→Mike (escalate thay vì spawn): {"file": "bin/dispatch.sh", "guards": ["(1) self-dispatch from==id → exit 2 (tránh split context + double-write bus/working-memory)", "(2) target Mike chỉ khi D …
- [2026-06-27T02:59:29] Spyros/decision — mge20-tail-review-REJECT-cap-at-1.5: {"dispatch_from": "Taylor", "subject": "Tail risk review — MGE=2.0 vs 1.3 vs 1.5 (Config D recovery lever)", "Q1_s4_fire_point": {"formula": "price_drop_to_S4 = …
- [2026-06-27T02:53:42] Taylor/finding — clean MGE sweep config D full curve: 2.0 best in-sample (30.44/DD-19.1/Cal1.60) but LUMPY+tail — Spyros re-review for gross 2.0; lean 1.5 default: {"correction": "earlier 2-point read over-extrapolated 1.3=1.5 plateau on incomplete cache; full 4-point on stable cache refutes", "sweep_50B_cleanD4": {"1.3":  …
- [2026-06-27T02:56:32] Taylor/finding — #18 bottom-basket proxy: pbcombo (1/PB-heavy) deploys +1.25%/day vs yieldcombo at bottoms, 75% win — worth dual-vehicle wiring: {"proxy": "bottom_basket_proxy.py, deep-cheap deploy days, equal-wt top15, liquid>=5bn+quality floor", "result": {"yieldcombo": "6.54% mean fwd2M, 66% win", "pb …
- [2026-06-27T03:50:24] Spyros/decision — S4-episode-breaker-implemented: {"dispatch_from": "Taylor", "subject": "Episode-drawdown breaker S4 implemented in risk_monitor.py (MGE=1.5, threshold=-15%)", "status": "DONE", "design": {"thr …
- [2026-06-27T03:36:46] Taylor/finding — #18 dual-vehicle pbcombo REJECTED by harness — +0.46pp CAGR but DD -20.3→-22.3, Calmar 1.48→1.37; keep yieldcombo: {"wiring": "BOTTOM_VEHICLE_PBCOMBO env, regime-conditional: base=yieldcombo, deep-cheap deploy-holding=pbcombo (0.67/0.23/0.10 PB/PCF/PE), spliced post-recovery …
- [2026-06-27T03:56:37] Mafee/answer — dnse-margin-probe-config-D: {"dispatch_from": "Taylor", "subject": "DNSE loan_packages live probe — margin gate cho Config D (MGE=1.5)", "verdict": "MARGIN_ENABLED_ON_0002023347_ONLY — V2. …
- [2026-06-27T03:54:10] Taylor/decision — V2.4-L blockers B3+B4 DONE+verified; B2 done (Spyros); only B1 (Mafee margin) left: {"B3_nav_cap": "engine lever_nav_cap + LEVER_NAV_CAP_B=100; verified @150B gross 1.000 (lever off), @50B gross 1.197 (early bottoms only); @50B CAGR 30.05>=unca …
<!--RECENT-END-->

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-06-21. Lịch sử/chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc auditable: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). Đây là hệ **POC nghiên cứu**, chưa chạy tiền thật tự động.

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-06-30**, trên TTCK Việt Nam.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout, depth OFF) + HAG eq_flag fix**.
- 2 book static 50/50: **BAL** (momentum SIGNAL_V11) + **LAG** (PEAD/earnings drift). Allocator w_LAG theo state {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- Live config <150B = **R3 NEUTRAL-only @50B: CAGR 28.26% / Sharpe 1.87 / DD −18.8 / Calmar 1.50**. @20B (R1) 31.69%.
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full (IS +8.7 / OOS +6.2, lại GIẢM DD).** Bull-park chỉ bật khi **NAV ≥150B**.
- **custom30** = rổ "đỗ tiền nhàn" beta (KHÔNG phải alpha picker): giữ **production (30 mã, cap 0.10)**; **(30,0.15) là OVERFIT** (walk-forward bác). **custom30B** (sleeve bull): @20B > custom30V, @50B wash (capacity-bound).

### DT5G — market regime gate
- Production state = bảng **`tav2_bq.vnindex_5state_dt5g_live`**, đọc qua **`get_gated_state()`** (fail-safe → DT4 khi feed cũ). **KHÔNG** đọc bảng trống `vnindex_5state` (đó là **v3.4b BASE**, không phải DT5G).
- Bản chất: **gate phòng thủ (insurance), KHÔNG phải bộ tăng lợi nhuận**. Cảnh giác bug **ffill-frozen** (đã gặp 2026-06-02).

### 8L valuation/rating
- **Composite v3 đang LIVE** trong `rating_8l.py` (default, thay v2): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS), no-reward khi PE/PCF âm. **Golden floor yêu cầu ROE_Min3Y≥0 VÀ CF_OA_3Y>0**. Moat governance: chỉ WIDE (đã audit 5F) mới được notch lên hạng cao.

### Kronos (foundation model nến)
- Đã tích hợp skill `/kronos`, fine-tune VN. Kết luận thẳng: **chỉ sửa calibration (MAE 3.93%→2.56%), KHÔNG tạo edge định hướng**; **RL bị loại** (OHLCV↔hướng ngày mai gần như không có MI). Dùng như **lăng kính kịch bản/biến động**, KHÔNG phải tín hiệu giao dịch.

### Backtest battle (đã chốt)
- Single-book custom30V **KHÔNG thắng** V2.3 multi-book khi audit faithful per-name. Trần auditable ~**25.7% @50B** (27.7% @20B); **>30% từ 2014 KHÔNG tồn tại** (số cao là do panel curated + CAPIT hardcode, không phải BQ-live).
- Illiquidity premium VN tập trung ở **vi-mô < 1 tỷ/ngày ADV**.

### Hạ tầng giao dịch
- `trading_bot/` (brokers/executor/plan) sẵn sàng. **DNSE live OK** (số tiểu khoản nằm trong `secrets/`, KHÔNG ghi ở KB). **PHS live BLOCKED** (chờ client credential, lỗi `-700003`) → PHS chạy paper.
- **Ủy quyền lệnh (an toàn tiền thật):** Taylor đặt rule (user duyệt) → Bill lập plan `data/plan_<acct>_<T+1>.json` (user duyệt) → **Mafee chỉ thực thi lệnh CÓ trong plan**, trong hạn mức cứng (`trading_bot/config.py` + `data/trading_rules.json`); paper full-auto, live trong limit, **KHÔNG tự chế lệnh**. Spyros giám sát + kill-switch `data/BOT_STOP`. Handoff = file `data/` + bus (companion model).
- **Auto-OTP (Gmail API)**: DNSE trading token (8h) tự động lấy qua `bot_execute.py --auto-otp`. Flow: gửi email OTP → `gmail_otp_reader.py` poll Gmail (`gmail.readonly` OAuth2) → trích 6 số → `create_trading_token()`. Credential: `secrets/gmail_oauth_token.json`. **Mafee chạy `--auto-otp` thay vì `--otp` trên các ngày giao dịch (T2–T6)**, trước 09:15 ICT. Fallback nếu Gmail lỗi: token cache còn hạn vẫn chạy; hết hạn → cảnh báo Telegram, user can thiệp thủ công.
- **BQ Local Cache (DuckDB)**: 12 bảng BQ cached → parquet local (`data/bq_cache/`), query qua DuckDB ~100ms thay vì 5-15s BQ. Env `BQ_LOCAL_CACHE=data/bq_cache` đã wire trong `wc_env.sh` + `dispatch.sh` → mọi `bq()` call tự route local. Sync daily 23:45 ICT + preflight check. Fallback: cache chưa verify → `bq()` tự gọi BQ bình thường.

### Quy chuẩn làm việc (bắt buộc — khoa học & auditable)
1. Backtest phải **auditable**: self-check 0 VND + recompute từ CSV + **walk-forward IS(2014–19)/OOS(2020+) TRƯỚC khi wire**. Edge full-period mà rớt OOS = overfit → loại.
2. **No look-ahead**; cột forward (`profit_*`) chỉ để train, KHÔNG dùng filter live.
3. **Reproducible**: pin kết quả vào `data/results_registry.md` (lệnh + CSV path + AUDIT_END).
4. Ghi tri thức bền lên bus ngay khi tạo ra (`append_event.sh`), kèm số liệu/nguồn.
5. Tiền thật: human-in-the-loop ở tầng Taylor/Bill; Mafee plan-bound; Spyros là gate rủi ro.

### Backup / DR
- `~/thanhdt/backup.sh` → GitHub **minhtrido2023/thanhdt** (private): nhánh **main** = workspace + code + scrubbed Claude history; nhánh **mike-fleet** = fleet (config + KB). **Tự động daily 00:00 ICT** (cron) + chạy tay `./backup.sh "msg"` cho mốc quan trọng. PAT có hạn — push lỗi auth thì cấp lại token.

## Nguồn chuẩn tắc đầy đủ
Lịch sử/chi tiết: kb/KNOWLEDGE.md (Mike biên tập). Trạng thái fleet: kb/fleet_status.md.
