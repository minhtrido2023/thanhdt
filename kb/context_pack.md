# Mike fleet — context pack (v70)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-25T10:32:16] Bob/decision — Tắt daemon DollarBill+Mafee (ngủ tới go-live) — còn 2 companion daemon Mike+Taylor: {"action": "reduce live companion footprint to minimum before go-live", "disabled": ["mike@DollarBill", "mike@Mafee"], "remaining_daemons": ["Mike (orchestrator …
- [2026-06-25T10:50:50] Mike/decision — bq-local-cache-live: {"what": "BQ Local Cache (DuckDB) đã live — 12 bảng BQ cached parquet, query ~100ms thay vì 5-15s", "env": "BQ_LOCAL_CACHE=data/bq_cache đã wire sẵn trong wc_en …
- [2026-06-25T11:03:58] Taylor/finding — CORRECTION: Exp-8 A∧C-confirm K30 MGE1.3 vay 0 VND THẬT — gross max=1.000, mọi deploy funded bằng cash parked; MGE ở CAPIT-ONLY là SIZING knob KHÔNG phải leverage (mislabel cần sửa): {"trigger": "user skeptic — verify thời điểm vay/tổng vay/lãi/PnL mỗi đợt", "measured_from_audit_csv": {"borrow_days_cash_negative": "26/3107 nhưng deepest=0 VN …
- [2026-06-25T11:37:09] Taylor/finding — Exp-8 lever-probe: vay thật CHỈ materialise khi mở margin all-tiers, NHƯNG vay ở ĐỈNH (bull) không phải đáy A&C — sai hướng; cần wire lever-AT-bottom riêng: {"trigger": "user (b): test vay để mua nhiều hơn tại tín hiệu A&C", "probe_3_variants_same_snapshot": {"V1_capit_only_wmax0.95": "gross1.000 borrow0 CAGR30.24 D …
- [2026-06-25T11:40:07] Winston/finding — corp-action MỚI: SBG reset hệ số giá ex 2026-06-25: {"ticker": "SBG", "ex_date": "2026-06-25", "gross_adj_pct": 20.16, "raw_gap_pct": -15.77, "adj_continuity_pct": 1.21, "audience": ["Winston", "Taylor"], "action …
- [2026-06-25T11:40:07] Winston/finding — corp-action MỚI: DDV reset hệ số giá ex 2026-06-25: {"ticker": "DDV", "ex_date": "2026-06-25", "gross_adj_pct": 7.01, "raw_gap_pct": -7.36, "adj_continuity_pct": -0.87, "audience": ["Winston", "Taylor"], "action" …
- [2026-06-25T11:40:07] Winston/finding — corp-action MỚI: EVG reset hệ số giá ex 2026-06-25: {"ticker": "EVG", "ex_date": "2026-06-25", "gross_adj_pct": 4.97, "raw_gap_pct": -4.74, "adj_continuity_pct": 0.0, "audience": ["Winston", "Taylor"], "action":  …
- [2026-06-25T11:40:07] Winston/finding — corp-action MỚI: AAV reset hệ số giá ex 2026-06-25: {"ticker": "AAV", "ex_date": "2026-06-25", "gross_adj_pct": 3.03, "raw_gap_pct": -2.94, "adj_continuity_pct": 0.0, "audience": ["Winston", "Taylor"], "action":  …
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
