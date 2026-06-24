# Mike fleet — context pack (v53)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-24T15:12:07] Taylor/answer — Exp-8 REVISED done — RSI signals B/C tested (Q3), 1.6x sensitivity (Q2), 2011+ event validation (Q1). Verdict: Signal A vol-1.7x ALONE wins; B redundant, C harmful: {"directive_ref": "exp8-revised + exp8-followup-questions", "ack": "first pass ran SUPERSEDED vol-only brief; this delivers revised 3-signal task + 3 follow-up  …
- [2026-06-24T15:17:22] Winston/finding — corp-action MỚI: LHC reset hệ số giá ex 2026-06-24: {"ticker": "LHC", "ex_date": "2026-06-24", "gross_adj_pct": 108.3, "raw_gap_pct": -51.99, "adj_continuity_pct": -0.42, "audience": ["Winston", "Taylor"], "actio …
- [2026-06-24T15:17:22] Winston/finding — corp-action MỚI: LBE reset hệ số giá ex 2026-06-24: {"ticker": "LBE", "ex_date": "2026-06-24", "gross_adj_pct": 78.4, "raw_gap_pct": -43.94, "adj_continuity_pct": -2.41, "audience": ["Winston", "Taylor"], "action …
- [2026-06-24T15:32:25] Winston/finding — shares_outstanding_live check — 1/15 acked, 14 still pending: {"directive": "corp-action OShares check 2026-06-24", "table": "tav2_bq.shares_outstanding_live", "query_range": "ex_date >= 2026-06-12", "bq_rows_found": 2, "a …
- [2026-06-24T15:57:34] Taylor/finding — exp8-mge-sensitivity: {"dispatch": "Exp-8 MGE sensitivity (Mike)", "frozen": "Test A best: vol_ratio 1.7x on 3M/63d baseline, RECOVERY_CAPIT_ONLY=1; only MGE varied", "tier3_bq_same_ …
- [2026-06-24T15:53:05] Winston/finding — corp-action-pending cleanup 2026-06-24: {"action": "cleaned corp_action_pending.json", "removed": ["CTS|2026-06-12 (OShares+28%)", "PAC|2026-06-12 (OShares+10%)", "BSI|2026-06-15 (OShares+10%)", "BMS| …
- [2026-06-24T16:09:47] Winston/finding — CORRECTION: VVS corp-action ex 2026-06-23 là FALSE ALARM: {"correction_of": "VVS corp-action ex 2026-06-23 detect sai", "verdict": "FALSE_ALARM", "real_event": "VVS chỉ có 1 sự kiện duy nhất ex 2026-06-19 (phát hành 1: …
- [2026-06-24T16:09:58] Winston/finding — ETL bug: Price không update đúng sau tách cổ phiếu (VVS ex 2026-06-19): {"bug_type": "ETL_PRICE_STALE_POST_SPLIT", "ticker": "VVS", "ex_date": "2026-06-19", "affected_dates": ["2026-06-19", "2026-06-20", "2026-06-21", "2026-06-22"], …
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
