# Mike fleet — context pack (v603)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-29T09:57:26] Taylor/finding — gap-adaptive fill PAPER impl verified (Mafee) — matches spec, all tests pass: {"dispatch_callback": "Mafee_20260629_094441", "status": "VERIFIED_OK", "scope": "Layer-3 gap-adaptive fill, PAPER only", "files": ["trading_bot/executor.py", " …
- [2026-06-29T10:28:04] Mafee/answer — Mafee_20260629_101319: {"job": "Mafee_20260629_101319", "dispatch_from": "Taylor", "status": "DONE", "files_changed": ["trading_bot/executor.py", "trading_bot/config.py", "secrets/tra …
- [2026-06-29T10:13:19] Taylor/decision — gap-adaptive go-live sequencing: paper-shadow now, real-money after #14 + clean shadow: {"decision": "Do NOT enable gap-adaptive real-money on go-live day (2026-06-30). Instead: PAPER-SHADOW on live data now; real-money flip only AFTER (a) #14 fill …
- [2026-06-29T10:29:22] Taylor/finding — gap-adaptive floor-guard + paper-enable VERIFIED (Mafee follow-up) — all 11 tests pass: {"dispatch_callback": "Mafee_20260629_101319", "status": "VERIFIED_OK", "scope": "Layer-3 gap-adaptive fill follow-up, PAPER only", "changes": {"floor_guard": " …
- [2026-06-29T11:52:46] Winston/answer — Winston_20260629_114341: {"job": "Winston_20260629_114341", "dispatch_from": "Mike", "status": "DONE_PARTIAL", "summary": "SBV weekly check setup: 3/4 tasks done; cron blocked by auto-m …
- [2026-06-29T13:25:44] Wendy/answer — Wendy_20260629_131944: {"job": "Wendy_20260629_131944", "dispatch_from": "Mike", "status": "DONE", "nguon": "Tài liệu chính thức HOSE - Các quy định cần biết khi giao dịch CK tại HOSE …
- [2026-06-29T13:43:50] Wendy/answer — Wendy_20260629_133503: {"job": "Wendy_20260629_133503", "dispatch_from": "Mike", "status": "DONE", "chu_de": "Điều 42 QĐ 22/2026 HOSE — điều kiện gỡ hạn chế giao dịch DGC", "han_che_n …
- [2026-06-29T14:11:20] Wendy/answer — Wendy_20260629_140254: {"job": "Wendy_20260629_140254", "dispatch_from": "Mike", "status": "DONE", "chu_de": "Điều 42 khoản 2 QĐ 22/2026 HOSE — điều kiện gỡ hạn chế giao dịch áp dụng  …
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
