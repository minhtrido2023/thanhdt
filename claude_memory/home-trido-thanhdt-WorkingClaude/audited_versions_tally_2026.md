---
name: audited-versions-tally-2026
description: "Bảng tổng các bản đã chạy audit BQ-verifiable (T+1 Open, 2014→now) — V2.3 family + V11 + V12.1"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ef717ab-5c78-4933-9acd-888a2ecf9450
---

THỐNG KÊ TẤT CẢ các bản đã audit qua harness BQ-verifiable (T+1 Open, mọi data tav2_bq.*, KHÔNG intraday, output 1-file + self-check 0 VND, spot-check 0 mismatch). FULL 2014-01-02 → [REDACTED]11. VNINDEX B&H = 10.76% / Sh0.65 / DD−45.3%.

| Bản | State | CAGR | Sharpe | MaxDD | Calmar | File data/ |
|---|---|---|---|---|---|---|
| **V2.3A** (allocator+CAPIT) | DT5G | 21.94% | 1.59 | −23.7% | 0.92 | v23_golive_audit_2014_now.csv |
| **V2.3C** (static+CAPIT uncapped) | DT5G | 21.38% | 1.52 | −23.5% | 0.91 | v23c_golive_audit_2014_now.csv |
| **V2.2-base** (no CAPIT) | DT5G | 21.23% | 1.58 | −18.5% | **1.14** | v22base_audit_2014_now.csv |
| V2.3C cap15 | DT5G | 21.51% | 1.56 | −22.2% | 0.97 | v23c_…_cap15.csv |
| V2.3C cap20 | DT5G | 21.31% | 1.54 | −22.8% | 0.93 | v23c_…_cap20.csv |
| V2.3C mat-smooth | DT5G | 21.66% | 1.55 | −21.2% | 1.02 | v23c_…_matsmooth.csv |
| V2.3C mat-gate15 | DT5G | 21.86% | 1.57 | −20.9% | 1.04 | v23c_…_matgate15.csv |
| V2.3C ew2d | DT5G | 21.75% | 1.56 | −21.0% | 1.04 | v23c_…_matew2d.csv |
| **V11 Song Sinh** (BAL+VN30 momentum, KELLY) | DT5G | 19.80% | 1.27 | −20.3% | 0.97 | v11_audit_2014_now.csv |
| **V12.1 ensemble** (BAL + VN30⇄LAGGED switch) | v3.4b | 16.85% | 1.27 | −20.1% | 0.84 | v121_audit_2014_now.csv |
| **LAGGED+VN30(idle)** one-wallet 50B | DT5G | 17.76% | **1.44** | **−18.2%** | 0.98 | lagvn30_audit_2014_now.csv |
| **LAGGED+full-BAL(idle)** one-wallet 50B | DT5G | 17.04% | 1.18 | −18.5% | 0.92 | lagbal_audit_2014_now.csv |

**XẾP HẠNG GIẢM DẦN theo kiến trúc (xác nhận memory)**: V2.3 family (2 sổ BAL+LAG = momentum+value đa dạng hóa) **21-22%** > V11 (2 sổ momentum BAL+VN30, độc canh momentum, không value) **19.80%** > V12.1 (ensemble switch VN30⇄LAGGED, V4-family) **16.85%** = TỆ NHẤT. Khớp [[core_architecture_balanced_2026]] (balanced>momentum-only) + [[v4_faithful_reproduction_2026]] (V4/ensemble faithful 14.20% << V2.3). Ensemble switching hủy giá trị (switch-cost 0.5%/flip × 33 flip + chọn sai leg). ⚠️ V12.1 dùng state v3.4b (canonical của nó) khác DT5G của V2.3/V11 — một phần chênh do state, nhưng switching là driver chính (V11 cùng momentum books KHÔNG switch = 19.8 vs V12.1 switch = 16.85).

**LAGGED+VN30(idle) one-wallet (user [REDACTED]13)**: LAGGED HL_3y ưu tiên (prio 110/105) + VN30 top30 momentum lấp công suất nhàn rỗi, 1 ví 50B, sizing one-wallet 5%/5%/4%, NO ETF parking, DT5G. KQ: CAGR 17.76% NHƯNG **Sharpe 1.44 (cao nhất nhóm non-V2.3, vs V11/V12.1 đều 1.27) + DD −18.2% (thấp nhất TẤT CẢ, kể cả V2.2-base −18.5%)**. 2022+ Cal 0.62, 2025+ 0.71. → ghép value(PEAD/LAGGED)+momentum(VN30) trong 1 ví = risk-adjusted TỐT hơn momentum-only V11 (xác nhận balanced>mono); nhưng CAGR bị KẸP vì momentum-leg giới hạn top30 (ít cơ hội hơn full-universe BAL của V2.3) → đó là cái giá ~3-4pp CAGR vs V2.3. Capital-sharing (LAGGED idle→VN30) hoạt động (deployed tốt, Sharpe cao); bottleneck = VN30 top30 yếu hơn full-BAL.

**ONE-WALLET vs TWO-BOOK SILO (user [REDACTED]13, kết luận quan trọng)**: thử gộp LAGGED+momentum vào 1 ví 50B (LAGGED ưu tiên prio 110/105 + idle-fill, 5%/24). Cả 2 bản (top30: 17.76/Sh1.44; full-BAL: 17.04/Sh1.18) **THUA XA V2.2-base two-book silo (21.23/Sh1.58)** ~4pp CAGR + Sharpe/Calmar thấp hơn. → **SILO là FEATURE không phải hạn chế**: V2.3 cho mỗi sleeve 25B riêng + concentration (BAL 10%/12 best-momentum) → 2 sleeve không tranh slot; one-wallet LAGGED-priority CROWD-OUT top momentum (return driver chính) + pha loãng 5%/24 → bóp return. "Capital-sharing efficiency" là ẢO ở đây; concentration + dedicated allocation thắng. BONUS: trong setting pha-loãng one-wallet, **top30 (Sh1.44) > full-BAL (Sh1.18)** vì top30=lọc chất lượng/thanh khoản, full universe chỉ thêm noise. → xác nhận lại kiến trúc 2-sổ V2.3 là đúng.

**🏁 GATE POSTBULL — bản tốt nhất (user thesis [REDACTED]13, chốt số production)**: chặn CAPIT washout khi (VNINDEX trailing-2yr ≥60%) & (giảm-từ-đỉnh-1y >−15% nông) = hậu-bull-mạnh-chưa-điều-chỉnh. Hard-block (size 0). Validated full-history 2000→now (80% danger-day dính DD>25% trong 1y, trung vị fwd250 −7%; có false-pos đuôi 2005 mega-bull) + walk-forward (IS dormant=uncapped, OOS 2020+ THẮNG base+uncapped mọi trục: Cal 1.48 vs base 1.39 vs uncapped 1.03). Chặn ĐÚNG 2022-04, giữ 2025-10/2024/2018/2014-05/2016-01.
| config | CAGR | Sharpe | MaxDD | Calmar | file |
|---|---|---|---|---|---|
| V2.2-base (no CAPIT) | 21.23 | 1.58 | −18.5 | 1.14 | v22base_… |
| V2.3A uncapped (live cũ) | 21.94 | 1.59 | −23.7 | 0.92 | v23_golive_… |
| **V2.3C + postbull** (best risk-adj) | 23.35 | 1.72 | **−19.0** | **1.23** | v23c_…_matpostbull_shrink0 |
| **V2.3A + postbull** (max return, NEW live) | **24.04** | **1.79** | −20.6 | 1.17 | v23_golive_…_matpostbull_shrink0 |
**V2.3A+postbull = CAGR & Sharpe cao nhất TẤT CẢ**; vs live-cũ V2.3A uncapped: **+2.10pp CAGR VÀ DD −23.7→−20.6** (vừa thêm return vừa giảm rủi ro). Allocator thêm +0.69pp CAGR/+0.07 Sh so V2.3C+postbull NHƯNG tốn DD (−20.6 vs −19.0). → **Chọn live: max-return=V2.3A+postbull; best-risk-adj=V2.3C+postbull (bỏ allocator)**. Cả hai >> live cũ. ⚠️ ngưỡng postbull in-sample-tuned (1 loser 2022-04) nhưng full-history+walk-forward+generalize-2007/2018 = biện minh mạnh nhất mọi gate. Verifier: data/v23_audit_spotcheck.py (allocator) — 0 mismatch/0 VND/replay 0.

**⭐ EDGE-CONDITIONAL ALLOCATOR (user [REDACTED]13, faithful chốt số deploy)**: allocator tilt LAG→0.65 trong NEUTRAL/BULL/EXBULL CHỈ khi LAG edge-health mean12≥4% (causal, data/lag_edge_health.csv); else giữ 0.50. BEAR=0/CRISIS=0.50 nguyên. Lý do: V2.3A DD>V2.3C vì allocator dồn 66% LAG ở NEUTRAL-phục-hồi-2023 đúng lúc LAG bleeding (edge percentile-3); edge-cond tránh điều đó. `pt_v23_audit_2014.py v23a none postbull 0.0 edge` (argv[5]=edge, EDGE_THR=4). **Walk-forward PASS** (hiếm trong phiên): edge-health yếu ở CẢ IS(58%<4%) lẫn OOS(35%) → rule được tập+kiểm thật; edge-cond thr4 thắng state-tilt CẢ IS(Cal2.11>1.93) LẪN OOS(1.40>1.36); ngưỡng 4% kinh tế nằm plateau robust (IS-optimal=5 nhưng OOS revert→bài học ngưỡng-kinh-tế>tối-ưu-IS). Faithful = overlay-research KHỚP KHÍT (validation).
| config | CAGR | Sharpe | MaxDD | Calmar | file |
|---|---|---|---|---|---|
| V2.3A uncapped (live cũ) | 21.94 | 1.59 | −23.7 | 0.92 | v23_golive_… |
| V2.3C + postbull (min-DD) | 23.35 | 1.72 | **−19.0** | 1.23 | v23c_…_matpostbull_shrink0 |
| V2.3A + postbull | 24.04 | 1.79 | −20.6 | 1.17 | v23_…_matpostbull_shrink0 |
| **V2.3A+postbull+EDGE (DEPLOY)** | **24.64** | **1.82** | −20.3 | 1.22 | v23_…_matpostbull_shrink0_edge |
**Bản deploy = V2.3A+postbull+edge: CAGR & Sharpe CAO NHẤT toàn bộ; vs live-cũ +2.70pp CAGR & DD −23.7→−20.3 (−3.4pp).** Hai refinement (postbull + edge-alloc) ĐỀU walk-forward PASS. ⚠️ edge-cond cải thiện chủ yếu RETURN không phải DD (DD vẫn>V2.3C-no-allocator −19.0); chọn: max-return=V2.3A+postbull+edge; min-DD=V2.3C+postbull. Verifier data/v23_audit_spotcheck.py replay allocator qua cột w_lag_tgt (generic mọi rule, 0 VND). Research: data/research_edge_conditional_allocator.py + _walkforward.py.

**⚠️ ETF PARKING LIQUIDITY CAP (user bắt lỗi [REDACTED]13, QUAN TRỌNG)**: engine cũ KHÔNG cap thanh khoản E1VFVN30 parking (`buy_amt=min(delta,cash)`, không ADV) — trong khi mua cổ phiếu cap 20%ADV/5d. Audit cũ: 66% sweep vượt cap, max 298B/ngày vs ADV E1VFVN30 ~15-20B/ngày, ETF nắm cuối 379B=49% danh mục = ~20-25 ngày volume. ĐÃ vá engine: param `etf_adv_lookup`+`etf_liquidity_pct` (default off=legacy), cap cả buy+rebalance-sell+JIT-sell, fill nhiều ngày. Harness `ETF_LIQ=off|strict|creation` env.
| deploy config | CAGR | Sharpe | MaxDD | Calmar | ETF cuối |
|---|---|---|---|---|---|
| uncapped (cũ) | 24.64 | 1.82 | −20.3 | 1.22 | 49% |
| **strict** (20%×ADV thứ cấp ~2B/d) | **23.68** | **1.96** | **−17.2** | **1.37** | 40% |
| **creation** (20%×rổ-VN30 ~464B/d) | **24.64** | 1.82 | −20.3 | 1.22 | 49% |
**Phát hiện**: (1) **creation ≈ uncapped** (24.64, cap 464B/d hiếm khi binding) → ETF parking KHẢ THI ở quy mô lớn QUA primary-creation (giao rổ VN30 cho DCVFM). (2) **strict chỉ −0.96pp CAGR (23.68) NHƯNG risk-adj TỐT HƠN** (Sh 1.96>1.82, DD −17.2<−20.3, Cal 1.37=tốt nhất tất cả) — vì ít park=ít beta VN30=ít vol/DD; frictionless-ETF-parking cũ THÊM drawdown đổi return mỏng. → **"inflation" user lo là NHỎ (~1pp) và thực ra parking thừa đang thêm rủi ro**. Bracket số thật: **23.68% (sàn, chỉ thứ cấp) ↔ 24.64% (trần, có creation)**; thực tế gần creation nếu dùng primary-creation (khả thi quy mô tổ chức). ⚠️ strict-mode idle-cash unparked earn deposit=0 (drag) → 23.68 là sàn bảo thủ (deposit thật ~3-5% sẽ kéo lên). Ảnh hưởng MỌI version (V11 KELLY{3:1.0} park nhiều hơn → bị hơn). Files data/..._etfliqstrict/_etfliqcreation.csv.

**Risk-adjusted champion (không CAPIT) = V2.2-base** (Calmar 1.14, DD −18.5%, 0 param). CAPIT/allocator/gates đều thêm return mỏng đổi lấy DD (xem [[v23_audit_2014_now_deliverable]]). Bản DD thấp nhất tuyệt đối = LAGGED+VN30 (−18.2%) nhưng CAGR thấp.

**Hạ tầng audit dùng chung** (theo [[simulation_[REDACTED]_audit_default]]): `pt_v23_audit_2014.py` (V2.3 family, MODE+cap+maturity args), `pt_v11_audit_2014.py`, `pt_v121_audit_2014.py`; emitter chung `audit_lib.py` (N-sổ, cột carry=lãi-vay-cash-âm để sổ tự khớp 100%, combined_override cho ensemble); verifier chung `data/audit_spotcheck_generic.py` (đọc nhãn sổ + switched-recurrence từ META). MỌI file audit: cash-flow identity 0 VND, final-NAV identity 0, giá vs BQ 0 mismatch, metric dựng-lại-từ-DAILY khớp.
