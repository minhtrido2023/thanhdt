# Mike fleet — context pack (v627)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-30T07:13:33] Taylor/finding — Energy/Utilities triple screen: weakest group alongside steel — mature utilities structurally LAG (don't compound), oil services a 2-faced high-beta oil-cycle bet (FAIL IS/star OOS, DD-68 un-ownable), renewables a documented capture FAILURE; all lens-not-book. Durable exports = DY-uncapturable rule + FCF>0 maturity gate: {"job": "Taylor_20260630_070640", "sector": "#9 Energy/Utilities (Oil&Gas + Power + Renewables)", "framework": "mike/agents/Taylor/energy_valuation_framework.md …
- [2026-06-30T07:24:42] Taylor/finding — Pharma defensive screen built+backtested: dispatched PE-mean-reversion screen FAILS both IS(-3.0pp) and OOS(-5.1pp) — holds cash 82% of months, misses every bull. KEY: the names compound (B&H same names +15.96%/+5.73pp/lower DD) — TIMING destroys it. Pharma = buy-and-hold lens, not a timed screen. IMP/ETC-growth = documented capture failure (100% rejected by quality floor): {"job": "Taylor_20260630_072007", "sector": "#12 Pharmaceuticals (generic+distribution, no R&D)", "framework": "mike/agents/Taylor/pharma_valuation_framework.md …
- [2026-06-30T07:25:00] Taylor/finding — F&B dual screen (sector #10): both lens-not-book, weak tier (steel/energy company). FMCG-defensive = strong IS +11pp → NO OOS edge (−2.4pp, megacap-rerate-then-derate like retail); Seafood-cyclical = single-event OOS (+7pp ENTIRELY 2022 ASP super-cycle, fails IS −8pp). Durable exports: GPM-stability moat gate (rejects KDC), seafood duty-cycle value-trap filter, VHC un-capturable as trough-buy, DY-uncapturable reconfirmed: {"job": "Taylor_20260630_071901", "framework": "mike/agents/Taylor/fnb_valuation_framework.md", "script": "fnb_screen.py", "outputs": ["data/fnb_fmcg_monthly.cs …
- [2026-06-30T07:25:25] Taylor/finding — Tech/IT-services screen built+backtested: VN tech = SINGLE-NAME (FPT) entry-timing lens, not a sector book; dispatch ROIC>18 gate collapses universe to 0 names (FPT blended 12-17pct via Telecom+education); lens REAL (+26pp fwd-12M, 88pct win) but mono-name cash-drag kills monthly book (-7.4pp vs B&H): {"job": "Taylor_20260630_071941", "script": "tech_screen.py", "framework": "mike/agents/Taylor/tech_valuation_framework.md", "outputs": ["data/tech_fpt_lens.csv …
- [2026-06-30T07:34:24] Taylor/finding — VTP/CTR/TOS single-name framework — CTR is a real CAPTURABLE EVEB lens, VTP a Viettel-halo decelerator, TOS un-capturable (thin): {"job": "Taylor_20260630_073023", "framework": "mike/agents/Taylor/viettel_logistics_infra_framework.md", "names": {"CTR": {"archetype": "asset-light telecom-in …
- [2026-06-30T07:38:04] Taylor/finding — Securities/Brokerage screen: standalone pick FAILS (loses to owning the sector) but it's the ONE sector where DT5G is a RETURN-enhancer not just insurance — gating halves DD −66→−32% and lifts CAGR 17.7→27.7% on the highest-beta sector (β1.27): {"job": "Taylor_20260630_073104", "sector": "#13 Securities/Brokerage", "script": "securities_screen.py", "framework": "mike/agents/Taylor/securities_valuation_ …
- [2026-06-30T07:53:22] Taylor/finding — Aviation dual screen (sector #14): weakest group alongside steel/energy: {"job": "Taylor_20260630_074607", "sector": "#14 Aviation (airlines + airport/cargo services)", "script": "aviation_screen.py", "framework": "mike/agents/Taylor …
- [2026-06-30T08:03:11] Taylor/finding — Insurance (sector #15) quick check — thin + below-COE, no walk-forward edge: {"job": "Taylor_20260630_080041", "sector": "#15 Insurance (life + non-life)", "framework": "mike/agents/Taylor/insurance_valuation_framework.md", "universe": { …
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
