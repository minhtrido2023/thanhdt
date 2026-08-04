## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 28.86% / Sharpe 1.90 / DD −17.8% / Calmar 1.62** — pin CHÍNH THỨC từ
  **2026-08-03** (Final NAV 1.178,01B), đo trên **`universe_pit`** (point-in-time, không look-ahead).
  ⚠️ **KHÔNG phải "hệ tốt lên"** — KHÔNG có thay đổi mô hình nào. Đây là **đồng bộ registry theo
  code production**: mặc định `LAG_ADV_BASIS` (cơ sở giá của ADV book LAG) đã đổi `close`→`price`
  ngày 08-02 (commit `0062aa0`, để gỡ look-ahead + giữ bất biến "trần live == trần đã mô phỏng")
  nên số pin cũ không còn tái lập được bằng lệnh pin trên code hôm nay. Chân control (`close`) tái
  lập 27.24% TUYỆT ĐỐI cả 5 chỉ tiêu + cả 2 số IS/OOS ⇒ A/B hợp lệ. **Toàn bộ chênh nằm ở IS
  (+3,28pp), OOS chỉ +0,02pp** — hệ số `Close/Price` hội tụ về 1,00 gần đây nên chỉ khác ở nửa đầu
  mẫu; **KHÔNG trích +1,62pp như "edge mới"**. Chi tiết ở `data/results_registry.md` (mục
  **2026-08-03 RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION `LAG_ADV_BASIS=price`**), KHÔNG lặp lại ở đây.
  **Số lịch sử KHÁC VINTAGE / KHÁC CƠ SỞ / CÓ LỖI, không so trực tiếp**: 27.24%/1.81/−18.4%/1.48
  (pin 08-02, cơ sở ADV `close` — đúng với cơ sở đó, đã SUPERSEDED); 27.60%/1.84/−17.5%/1.58 (pin
  07-29, có look-ahead cơ sở giá rổ); 27.16%/1.81/−18.1%/1.50 (pin 07-22, đã mất, không tái lập
  được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`).
  ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho
  CAPIT pool/maturity. Lỗi fidelity `liq<=0` — **cơ chế nay đã tách được (T1-T5, job
  `Taylor_20260803_021414`/`_045138`, quant-skeptic CONFIRMED cao)**: giả thuyết "hiện vật sức
  chứa" BỊ BÁC BỎ hai lần bằng hai knob trực giao (`%ADV/ngày` và NAV), cả hai lần bằng SAI DẤU
  đạo hàm — không phải "chưa loại trừ được". Nhưng **MỨC thì KHÔNG tách được**: cả hai chân đứng
  trên 1 tham số mô hình fill (trần 20% ADV/phiên) mà 90-96% số phiên-fill sống Ở TRẦN đó, trong
  khi fill THẬT (DNSE) mới chỉ xác nhận tới ~3,86% ADV/phiên — 2 thiên lệch NGƯỢC CHIỀU cùng bậc
  độ lớn (+4,08pp do sửa đúng nhóm mã không mua được vs. −4,0..4,5pp do giả định fill quá lỏng)
  gần **triệt tiêu nhau**. ⇒ **28,86% ĐỌC LÀ ƯỚC LƯỢNG ĐIỂM có điều kiện vào 1 tham số chưa neo**,
  KHÔNG PHẢI cận dưới, không phải cận trên (đổi nhãn 2026-08-03, thay khoảng `[~27,2%;~31,3%]`
  đã hết hiệu lực) — **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng** ở bất kỳ
  chiều nào. Follow-up 08-04 (gate động theo executability thật) củng cố thêm: giải quyết được
  vấn đề cơ học (vị thế kẹt 35%→0%) nhưng KHÔNG cho lợi nhuận bền (đổi dấu khi bỏ 2020-2021,
  PBO cao) — cùng chữ ký reshuffle-luck. Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không
  bằng backtest thêm — sổ theo dõi + **mốc cứng 2026-12-15 / 2027-03-31**:
  `kb/projects/lag-adv-filter-tracking.md`, chi tiết cơ chế: `agents/Taylor/research/
  lag_fidelity_decomp_20260803/T5_DECISION.md`.
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

**MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12)** — thay đổi production chính thức, không phải "thử bị loại":
`MOMENTUM_N`+`MOMENTUM_S` gỡ khỏi `TIER_BAL` (giữ `MOMENTUM`/`MEGA` generic — vẫn đóng góp thật).
Lý do + chuỗi R&D: `kb/projects/momentum-deals.md`, `plan_close_mom_20260712.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State live hôm nay = `kb/current_ops.md` / `golive_state_today` (fact động, KHÔNG pin ở đây).

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
  ⚠️ **+0.125 ĐÚNG, đừng hạ** — đề xuất +0.096/+0.034 (nhân `Price/Close` "khử look-ahead") ĐÃ BỊ
  BÁC BỎ 2026-08-02: `PE` vốn đã ở cơ sở `Price` thô PIT đúng; nhân vào là ĐƯA look-ahead VÀO
  (R3 xấu −1,70pp). Xem `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)".
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- **`data/BOT_STOP`** = kill-switch tức thì.
- Giờ chuẩn tắc chuỗi ngày trading (T2-T6) + xử lý khi lỗi: `kb/ops_runbook.md`. Routing Discord:
  `kb/current_ops.md`. BQ cache / auto-OTP / PHS: `kb/KNOWLEDGE.md` §4.

### Kiến trúc fleet
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.
- Daemon / dispatch / escalate (cơ chế đầy đủ): `MIKE.md` + `kb/KNOWLEDGE.md` §3.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể: báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (ca Wave1/H8a-tiebreaker 2026-07-05: `kb/KNOWLEDGE.md` §8). V2.4/R3 đã qua chuẩn
   DSR/PBO (DSR≈1.0, PBO≈0.20 — `data/results_registry.md` mục "DSR / PBO Robustness Annex").

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 (đã đóng, kết luận lens/tilt): `kb/KNOWLEDGE.md` §7.
