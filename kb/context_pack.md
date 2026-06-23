# Mike fleet — context pack (v25)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-22T14:26:15] Taylor/finding — margin 1.5x in pt_v23: BEST config (31.60%/Sh2.01/DD-16.3/Cal1.94) but self-check non-zero (frac>=1.0 JIT edge) -> needs simulate fix: {"user_ask": "margin 1.5x in harness to exploit rare cheap opportunities", "result": "parking DOES leverage at frac>1.0 (not clipped). recovery wmax1.5: CAGR 31 …
- [2026-06-22T14:30:13] Taylor/decision — CORRECTION: recovery wmax1.5 is NOT margin — parking caps at cash (engine: ETF never uses margin): {"corrects": "my prior claim recovery wmax1.5 = margin 1.5x in harness. WRONG.", "verified": "simulate_holistic_nav.py line 197: max_gross_exposure note says ET …
- [2026-06-22T14:47:23] Taylor/decision — recovery-park FINAL clean config: 0.95/-0.5 = 31.81%/Sh2.02/DD-16.4/Cal1.94, 0 VND, LEVERAGE-FREE: {"config": "RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5", "result": "CAGR 31.81% / Sharpe 2.02 / MaxDD -16.4% / Calmar 1.94 | self-check 0 VND EXA …
- [2026-06-22T17:38:14] Taylor/finding — 2011 crisis-buy + margin backtest: thesis is REGIME-CONDITIONAL, deposit-gate is the fix: {"window": "2011-2026 VNINDEX-exposure, regime=base vnindex_5state (DT5G only 2014+), borrow=deposit+4% era-aware (VN margin ~18-24%/yr in 2012 not 10%)", "head …
- [2026-06-23T01:30:17] Taylor/finding — 2012 crisis-buy CONFIRMED at stock-selection layer (reconciles index-timing hold-cash): {"test": "probe_stockpick_2012.py — quality+deep-value top8 (NP_P0>0, FSCORE>=5, ROE5Y>=5%, DebtEq<3, rank pb_z asc), formed monthly, forward 6M/12M vs VNINDEX  …
- [2026-06-23T04:52:00] Taylor/finding — macro-view: post-2011 SBV regime more disciplined -> high-rate tail thinner -> deposit-gate as DORMANT insurance (floor7.5) not active re-rate: {"regime_now": "DT5G NEUTRAL/BULL-ish 2026; not the constraint here", "thesis": "User+Taylor: the 2011-12 inflation/rate crisis (deposit 14%, credit-to-property …
- [2026-06-23T04:52:00] Taylor/finding — macro-view: post-2011 SBV regime more disciplined -> high-rate tail thinner -> deposit-gate as DORMANT insurance (floor7.5) not active re-rate: {"regime_now": "DT5G NEUTRAL/BULL-ish 2026; not the constraint here", "thesis": "User+Taylor: the 2011-12 inflation/rate crisis (deposit 14%, credit-to-property …
- [2026-06-23T05:00:58] Winston/finding — test-delta-probe: {"note": "this is the only thing testdelta should see", "big": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx …
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
