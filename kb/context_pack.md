# Mike fleet — context pack (v30)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-23T11:40:07] Winston/finding — corp-action MỚI: DTD reset hệ số giá ex 2026-06-22: {"ticker": "DTD", "ex_date": "2026-06-22", "gross_adj_pct": 13.77, "raw_gap_pct": -11.84, "adj_continuity_pct": 0.3, "audience": ["Winston", "Taylor"], "action" …
- [2026-06-23T12:48:34] Wendy/finding — vn-tax-cheatsheet: {"summary": "THUẾ CK CÁ NHÂN VN — cheat-sheet (verify 2026-06-23, nguồn: WebSearch + thuvienphapluat)", "regime_hien_tai": {"ban_ck_niem_yet": "0.1% x giá CK mỗ …
- [2026-06-23T12:49:49] Winston/finding — PE_stored bug confirmed: Close_adj/EPS causes systematic understatement in historical data: {"bug": "PE in ticker/ticker_prune = Close_adj/EPS_TTM. Close is retroactively adjusted for all future stock bonuses but EPS is not. Result: PE understated by m …
- [2026-06-23T13:31:26] Taylor/finding — Fed-spread-gate tested: = deposit-gate = baseline byte-identical in pt_v23 (both dormant); '-1.18pp' was DATA DRIFT not a fed bug (verify caught it): {"controlled_same_snapshot": "gate-OFF vs deposit-dormant-7.5 vs fed(floor0/ceil1.5) ALL byte-identical: NAV 1396.51B / CAGR 30.63% / Sharpe 1.97 / MaxDD -17.5% …
- [2026-06-23T14:09:15] Mafee/finding — recommend_v23_bq_push_live: {"summary": "Script push_recommend_v23_to_bq.py đã chạy thành công. Dataset recommend_v23 tạo mới trên BQ (asia-southeast1). 2 tables: recommendations (partitio …
- [2026-06-23T14:11:17] Mafee/decision — push_recommend_v23_daily_cron: {"action": "Added step [13b] push_recommend_v23_to_bq.py vào papertrade_daily.sh, ngay sau [13] golive_recommend_v23.py. Chạy ~15:30 ICT T2-T6 tự động. Không cầ …
- [2026-06-23T14:25:26] Taylor/finding — REAL-MARGIN branch (CAPIT-only, max_gross_exposure) on production stock book: adds +0.77pp(1.3x)/+1.27pp(1.5x) with BETTER MaxDD+Calmar; self-check residual = borrow interest (proven, not a leak): {"mechanism": "NEW branch pt_v23: MGE env opens max_gross_exposure on the BAL stock book + margin_tiers={CAPIT} so ONLY deep-washout CAPIT plays can borrow (rea …
- [2026-06-23T14:32:39] Winston/finding — macro_health SEV2 DEGRADED fixed — 3 bugs from reorg commit 10ae395: {"root_cause": "commit 10ae395 reorg moved files to data/ but 3 paths in daily_refresh_v34b_linux.sh were NOT updated", "bugs_fixed": ["rm -f _cache_*.pkl -> rm …
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
