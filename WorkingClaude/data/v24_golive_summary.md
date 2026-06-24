# V2.4 Go-Live Bundle — Formal Summary
> Ngày: 2026-06-24 | Status: PROPOSED paper → chờ user + Spyros approval | Go-live target: 2026-06-30

## Config chính thức

| param | value |
|---|---|
| RECOVERY_PARK | 1 |
| RECOVERY_WMAX | 0.95 |
| RECOVERY_PBZ_DEEP | -0.5 |
| RECOVERY_DEP_GATE | 1 (DORMANT) |
| DEP_FLOOR | 0.075 (7.5%) |
| DEP_CEIL | 0.12 (12%) |
| trading_rules version | v1.6 |
| max_gross_exposure | 1.0 (leverage-free) |
| real-margin 1.3x | NOT in go-live (post-go-live option, Spyros approval needed) |

**Base config (unchanged):** `argv v23a none postbull 0 edge` + `ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"` @ 50B NAV

## Performance (same-snapshot 2026-06-24, CSV-pinned, self-check 0 VND)

| metric | R3 baseline (recovery OFF) | V2.4 go-live (recovery ON + dep-gate DORMANT) | delta |
|---|---|---|---|
| CAGR (2014-26) | 29.00% | 30.63% | **+1.63pp** |
| Sharpe | 1.90 | 1.97 | +0.07 |
| MaxDD | -18.5% | -17.5% | **+1.0pp (BETTER)** |
| Calmar | 1.56 | 1.75 | **+0.19** |
| IS CAGR (2014-19) | 28.99% | 28.99% | 0 (signal never fired IS) |
| IS Calmar (2014-19) | 1.97 | 1.97 | 0 |
| OOS CAGR (2020+) | 28.97% | 32.14% | **+3.17pp** |
| OOS Calmar (2020+) | 1.56 | 1.84 | **+0.28** |
| OOS Sharpe (2020+) | 1.88 | 2.01 | +0.13 |
| self-check | 0 VND | 0 VND | ✓ |

**CSV artifacts (pinned):**
- R3 baseline: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv`
- V2.4 go-live: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_recpark95z50.csv`

## Cơ chế RECOVERY_PARK

Recovery-park triển khai idle cash vào custom30V basket trong trạng thái CRISIS/BEAR khi `median pb_z ≤ -0.5` (thị trường rẻ sâu theo lịch sử). Quy trình:
1. **Trigger:** state ∈ {CRISIS, BEAR} AND median(pb_z, universe) ≤ -0.5
2. **Sizing:** `frac = clip((-0.5 - pb_z_median) / 0.5, 0, 1) × wmax × dep_m`
   - `wmax = 0.95` (giữ 5% cash đệm → self-check exact 0 VND)
   - `dep_m = clip((0.12 - deposit) / (0.12 - 0.075), 0, 1)` = 1.0 toàn bộ 2014-26
3. **Fire history:** 59 ngày / 2 episodes (COVID-2020 + post-SCB 2022-11)
4. **IS/OOS split:** signal CHƯA BAO GIỜ fire IS 2014-19 → toàn bộ edge là OOS opportunity-capture

## Risk statement

- **Leverage-free:** gross exposure ≤ 100% tại mọi thời điểm (idle cash deploy, không borrow)
- **Deposit-gate DORMANT:** fires ONLY if deposit rate > 7.5% (SBV post-2014 ≤ 6% thực tế, chưa cắn một lần nào 2014-26). Forward insurance cho scenario lãi cao kiểu 2011-12.
- **Overfit assessment:** IS OOS **PASS** — IS unchanged (signal dormant IS), OOS +3.17pp CAGR. Profile = DT5G macro gate: insurance/opportunity-capture, không phải statistical alpha từ nhiều mẫu. Deploy conservative (wmax=0.95, không tune sâu hơn).
- **n=2 caveat:** toàn bộ edge từ 2 episode (59 phiên). Không re-tune params vào IS/OOS — giá trị ở FAIL-SAFE không ở statistical precision.
- **Real-margin 1.3x CAPIT-only:** separate R&D item, NOT deployed → requires Spyros sign-off + user approval. Self-check đã sạch (0 VND), DD bounded (-15.5% vs leverage-free -17.5%), nhưng đòn bẩy THẬT (cash < 0).
- **DT5G fail-safe via get_gated_state():** falls back to DT4 if feed stale (<1440 min).

## Audit trail

- Self-check 0 VND: confirmed 2026-06-23 (3-run battery: gate-OFF / DORMANT-7.5 / ACTIVE-6)
- Deposit-gate DORMANT = byte-identical to gate-OFF: NAV 1561.18B = 1561.18B (2026-06-23 snapshot)
- Fed-spread-gate tested: byte-identical to deposit-gate (m_fed=1.00 on all 59 fire days, 2026-06-23)
- Data-drift acknowledged: 31.81% (2026-06-22 snapshot) → 30.63% (2026-06-23 snapshot) due to ticker_prune corp-action refresh. **DELTA +1.63pp bền với drift.**
- Registry: `data/results_registry.md` entries: deposit-gate section (line ~180), fed-spread-gate + data-drift (line ~192), real-margin fix (line ~198)

## Rejected alternatives (không vào go-live)

| alternative | verdict | lý do |
|---|---|---|
| RECOVERY_WMAX=1.0 | LOẠI | self-check 12.6k VND (JIT cash rounding) |
| RECOVERY_DEP_GATE active floor=6% | LOẠI | -0.98pp vs baseline; cắt nhầm SCB-2022 deploy |
| real-margin MGE=1.5x | LOẠI | MaxDD -32.5% (COVID tail amplified, fragile) |
| bull-park N+B 0.7 (R2) | LOẠI | Sharpe 1.82 < R3 1.87; lumpy 2024/25 |
| v3-composite selector | LOẠI | IS-overfit: OOS -0.78pp vs yieldcombo |
| FSCORE-tilt | LOẠI | proxy negative cả IS+OOS |

## Next steps sau approval

1. **User + Spyros review** → go-live approval
2. **Wire trading_rules v1.6** vào live execution engine (leverage cap 1.3x, cho nhánh post-go-live)
3. **Deploy custom30V** với RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_GATE=1
4. **Post-go-live item (optional, Spyros duyệt):** real-margin 1.3x CAPIT-only — đòn bẩy thật, cần sign-off

---
*Tạo bởi Taylor (quant researcher), 2026-06-24. Audience: Mike, DollarBill, Spyros, Mafee.*
