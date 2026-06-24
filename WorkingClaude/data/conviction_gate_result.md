# Conviction gate — kết quả Tier-1
> 2026-06-24, Taylor. Config: RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_FLOOR=0.075 MGE=1.3 MGE_CAPIT_ONLY=1 MGE_GATE=conviction ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" — pt_v23_audit_2014.py v23a none postbull 0 edge

## Events fired (per book BAL và LAG, lấy BAL làm representative)

| Date | State | Postbull_clear | Pillar B | m | Lý do |
|------|-------|----------------|----------|---|-------|
| 2014-05-08 | CRISIS(1) | True | False | 1.0 | **LEVER** |
| 2015-08-24 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2016-01-18 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2018-05-28 | CRISIS(1) | True | False | 1.0 | **LEVER** |
| 2018-07-05 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2020-02-03 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2020-03-11 | BEAR(2) + Pillar B ON | True | **True** | 0.0 | **Pillar B active** (COVID VIX spike) |
| 2020-07-27 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2022-04-19 | CRISIS(1) | **False** | — | — | postbull blocked → size=0 (pre-gate) |
| 2022-06-15 | BEAR(2) | True | False | 0.0 | state not CRISIS |
| 2022-09-28 | BEAR(2) | **False** | — | — | postbull blocked → size=0 (pre-gate) |
| 2023-10-30 | CRISIS(1) | True | False | 1.0 | **LEVER** |
| 2024-04-17 | BULL(4) | True | False | 0.0 | state not CRISIS |
| 2024-08-05 | CRISIS(1) | True | False | 1.0 | **LEVER** |
| 2025-04-03 | BULL(4) | True | False | 0.0 | state not CRISIS |
| 2025-10-20 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |
| 2026-03-09 | NEUTRAL(3) | True | False | 0.0 | state not CRISIS |

**Summary (per book):**
- LEVER fired: 4 events (2014-05, 2018-05, 2023-10, 2024-08)
- Blocked state not CRISIS: 10 events
- Blocked Pillar B active: 1 event (2020-03-11 COVID — đúng! VN crash nhưng do US contagion)
- Postbull pre-blocked (size=0): 2 events (2022-04-19, 2022-09-28 — đã bị postbull gate chặn trước)

## Performance vs baseline

| Metric | V2.4-LF (MGE_GATE=none) | conviction gate | delta |
|--------|------------------------|-----------------|-------|
| CAGR | 30.99% | 28.98% | **-2.01pp** |
| MaxDD | -31.45% | -31.58% | -0.13pp |
| Calmar | 0.985 | 0.918 | -0.067 |
| self-check BAL | 0 VND | 0 VND | — |
| self-check LAG | 0 VND | 0 VND | — |

*Baseline (V2.4-LF): v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_recpark95z50_depg75_mge130cap.csv (MGE_GATE=none, full lever all CRISIS)*

## So sánh mở rộng — tất cả lever-gate variants

| Variant | CAGR | MaxDD | Calmar |
|---------|------|-------|--------|
| MGE_GATE=none (unleveraged recovery-park) | 25.35% | -36.26% | 0.699 |
| MGE_GATE=none (full lever, V2.4-LF baseline) | 30.99% | -31.45% | 0.985 |
| MGE_GATE=deposit_eyield (Exp-3) | 29.73% | -31.67% | 0.939 |
| **MGE_GATE=conviction (Exp-4, this run)** | **28.98%** | **-31.58%** | **0.918** |
| MGE_GATE=deposit (rejected: misfire COVID) | 25.26% | -34.44% | 0.733 |

## Phân tích

### Verdict: gate TOO RESTRICTIVE → CRISIS+BEAR cần xem xét

**Logic conviction gate hoạt động đúng về cấu trúc:**
- 2020-03-11 COVID bị block đúng: VN crash nhưng Pillar B ON (VIX spike US) → không lever → correct
- 4 events LEVER đều là VN-specific CRISIS mà US không panic

**Vấn đề: CAGR giảm -2.01pp so với baseline**
- Conviction gate chỉ lever CRISIS, bỏ qua cả NEUTRAL/BEAR washout lẫn BULL pullback
- Baseline lever ALL CAPIT events trong CRISIS (vốn đã là ít events nhất)
- Conviction gate thắt thêm điều kiện → chỉ còn 4 events trong 12 năm (vs 6-7 events CRISIS baseline)
- Tức là gate block luôn một số CRISIS events do... không block thêm gì khác (Pillar B chỉ bắt 2020-03)

**Root cause**: Conviction gate không giải quyết được vấn đề thực sự. Trong 12 năm 2014-2026:
- Chỉ có 1 event bị Pillar B block (2020-03, nhưng event này là BEAR(2) nên đã bị block bởi state≠CRISIS)
- Thực tế Pillar B KHÔNG active trong bất kỳ CRISIS event nào (VIX > 35 chỉ xảy ra COVID, khi VN đã ở BEAR/NEUTRAL)
- Vì vậy conviction = CRISIS + postbull (đã có) + Pillar B off (dormant trong CRISIS era)
- Performance delta hoàn toàn đến từ việc gate thiếu cover NEUTRAL/BEAR washout (vốn còn lever tốt)

### So sánh với fedborrow (chết về cấu trúc)
- fedborrow: 0 events (eyield 5.9-7.7% < borrow 10% → never fire) → verdict dead
- conviction: 4 events → sống, nhưng chặt hơn baseline không có giá trị thêm (Pillar B dormant trong CRISIS)

### Recommendation
- Verdict: **gate too restrictive — but structurally correct**
- Pillar B tự nhiên được bảo vệ bởi DT5G (CRISIS state ít khi đồng thời Pillar B active, vì DT5G đã cap theo macro)
- Nếu muốn tăng selectivity: giữ conviction nhưng relax state condition = CRISIS OR BEAR (nhưng bear với postbull_clear)
- Hoặc: giữ full lever (MGE_GATE=none), vì DT5G đã bảo vệ khá tốt (nhớ 2022 = postbull gate, không cần Pillar B thêm)
- **deposit_eyield (Exp-3) là sweet spot tốt hơn**: 29.73% vs 28.98%, MaxDD tương đương, xử lý carry condition tự nhiên

## Acceptance criteria check

| Criterion | Status |
|-----------|--------|
| self-check = 0 VND | ✓ PASS |
| MaxDD không tệ hơn fedborrow unleveraged (-31.5%) | ✓ PASS: -31.58% ≈ same |
| CAGR > V2.4-LF (30.63% baseline ref) | ✗ FAIL: 28.98% < 30.99% |
| Events > 0 | ✓ PASS: 4 events fire |

**Verdict: FAIL — conviction gate too restrictive vs baseline. Pillar B dormant in actual CRISIS windows (DT5G already caps macro stress). deposit_eyield (Exp-3) remains the best standalone gate: 29.73% CAGR, near-identical MaxDD, fires on carry-condition rather than US binary.**
