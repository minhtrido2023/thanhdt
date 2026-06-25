# Mike fleet — context pack (v62)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-25T01:28:02] Taylor/finding — MGE=1.3 exit mechanism in RECOVERY_CAPIT_ONLY: {"dispatch": "Mike — exit mechanism of MGE=1.3 leverage unwind in RECOVERY_CAPIT_ONLY", "source_file": "pt_v23_audit_2014.py (verified by code read, not inferre …
- [2026-06-25T01:36:27] Taylor/decision — Exp-8 v2: refined Signal C as CONFIRM (BullDvg arm + A-confirm) SUPERSEDES A-only — slightly higher return, same DD, fixes 2012 early-fire risk: {"exp": "Exp-8 v2 (user idea: C=leading arm, A=confirm; refined per DT5G D_RSI_BullDvg)", "tier3_bq_same_snapshot_2026_06_25_all_0VND": {"A_only_1.7x": "31.07/S …
- [2026-06-25T01:46:57] Taylor/finding — exp8-mge-why-1.5-loses: gap is sizing/path drag NOT borrow: {"dispatch": "Mike/user: why MGE1.5 loses 1.03pp OOS CAGR vs 1.3 (35.85->34.82) = ~4x the ~0.26%/yr borrow-drag estimate", "verdict": "PREMISE WRONG — gap is NO …
- [2026-06-25T01:55:52] Winston/finding — discord-pipeline-test: {"status": "ok", "message": "auto Discord notify working"}
- [2026-06-25T01:56:44] Winston/finding — discord-e2e-final: end-to-end pipeline confirmed
- [2026-06-25T02:50:27] Taylor/finding — Exp-8 FORCE_REAL_LEVER measured: real >100% leverage barely materialises (45.9M VND borrow / 12.47y), forcing it is net-negative on CAGR: {"dispatch": "Mike — 2-step task: (1) add FORCE_REAL_LEVER env, (2) run Tier-3 A∧C-confirm K40 + MGE1.3 + FORCE_REAL_LEVER=1", "step1": "FORCE_REAL_LEVER=1 ALRE …
- [2026-06-25T08:14:17] Bob/decision — Dựng tier phản biện quant-skeptic (verify_finding.sh) — gate bác-bỏ trước khi wire production: {"what": "adversarial verifier tier for Taylor R&D findings", "native_agent": "~/.claude/agents/quant-skeptic.md (read-only: Bash/Read/Grep/Glob)", "runner": "m …
- [2026-06-25T08:21:37] quant-skeptic/verification — VERIFY: Exp-8 FORCE_REAL_LEVER measured: real >100% leverage barely materialises (45.9M VND borrow / 12.47y), forcing it is net-negative on CAGR: {"finding_topic": "Exp-8 FORCE_REAL_LEVER measured: real >100% leverage barely materialises (45.9M VND borrow / 12.47y), forcing it is net-negative on CAGR", "v …
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
