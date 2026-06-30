# Mike fleet — context pack (v612)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-30T02:47:42] Taylor/finding — fair-value thread CLOSED: ROIC/PB adds nothing to selection; value axis saturated; /valuation not an edge: {"selection_ab": {"script": "gap_fairvalue_selection_ab.py", "setup": "monthly top-25, A=ey+cfy vs B=+ROIC/PB, 70 OOS months 2018-2026", "result": "delta B-A =  …
- [2026-06-30T03:32:41] Taylor/finding — 8L growth-consistency reward audit: {"q": "Does 8L reward stable/consistent revenue+profit growth across consecutive quarters (smoothness, not just YoY)?", "answer": "NO — 8L rewards LEVEL + DURAB …
- [2026-06-30T04:07:22] Taylor/finding — 8L growth-quality (golden eggs) design + orthogonality read: {"context": "design discussion w/ user via Mike dispatch Taylor_20260630_040305", "q1_wiring": "NEW third selection axis (gq_score 0..1) parallel to rating+valu …
- [2026-06-30T04:15:55] Taylor/finding — gq_score growth-quality gate: FAIL — growth-only is NEGATIVE residual signal; do NOT wire into rating_8l: {"job": "Taylor_20260630_041104", "design_ref": "Taylor_20260630_040305", "script": "gq_score_gate.py", "gq_def": "z(Revenue_YoY_P0 growth)+z(GPM_P0-GPM_P4 marg …
- [2026-06-30T04:24:07] Taylor/finding — compounder early-detection: pattern = RevYoY persist + ROE/ROIC rising-high + margin-expand + CF_OA_3Y>0; 8L value-tilt catches cheap ones, MISSES growth-priced MWG; proposed standalone screen: {"job": "Taylor_20260630_042054", "src": "ticker_financial 2013-2017, /tmp/compounders.csv", "step1_entry_snapshot": {"HPG_2014Q1": {"RevYoY": 0.65, "GPM": 21.3 …
- [2026-06-30T04:35:50] Taylor/finding — Compounder Screen built+backtested: signal REAL+orthogonal to 8L but TOO THIN for a standalone book → watchlist/tilt only: {"job": "Taylor_20260630_042949", "script": "compounder_screen.py", "design_ref": "Taylor_20260630_042054", "method": "point-in-time monthly rebalance, ASOF joi …
- [2026-06-30T04:43:50] Taylor/finding — Retail valuation framework (MWG/PNJ/FRT): P/S-primary, sector-relative inventory, ROIC5Y-not-ROIC_Trailing; 2 entry archetypes; retrospective-confirmed not yet backtested: {"job": "Taylor_20260630_044001", "for": "DollarBill,user (via Mike)", "doc": "mike/agents/Taylor/retail_valuation_framework.md", "scope": "retail needs its own …
- [2026-06-30T04:58:32] Taylor/finding — Retail Compounder Screen built+backtested: REAL+orthogonal-to-8L but thin/IS-driven, NO OOS edge → watchlist/tilt; captures volume archetype (MWG) only, margin-turnaround (PNJ) structurally uncapturable: {"job": "Taylor_20260630_044929", "design_ref": "retail_valuation_framework.md (Taylor_20260630_044001)", "script": "retail_compounder_screen.py", "outputs": [" …
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
