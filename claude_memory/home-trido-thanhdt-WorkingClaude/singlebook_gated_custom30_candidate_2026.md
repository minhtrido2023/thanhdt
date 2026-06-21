---
name: singlebook_gated_custom30_candidate_2026
description: "DT5G-gated custom30 SINGLE-book — REJECTED after faithful per-name engine (LOSES to V2.3 every metric); the light index-sim was badly optimistic"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

## ⛔ FINAL VERDICT [REDACTED]20 (supersedes the optimistic finding below): SINGLE-BOOK REJECTED — LOSES to V2.3.
Faithful PER-NAME engine (MODE=singlebook in pt_v23_audit_2014: empty momentum/PEAD + cash_etf_states=SB_GATE {1:0,2:.2,3:.7,4:1,5:1}=custom30 + CAPIT-on-idle arm; SAME engine as V2.3; self-check final-NAV 0 VND), 2014→now @50B:
- single-book gated (no capit): **23.38% / Sh1.36 / DD−31.7 / Cal0.74**
- single-book + CAPIT-on-idle: **23.65% / Sh1.35 / DD−30.9 / Cal0.76**
- **Production V2.3 multi-book: 25.27% / Sh1.61 / DD−23.8 / Cal1.06 → WINS every metric.**
**The light index-sim (numbers below, ~29.65%/DD−16.4) was BADLY OPTIMISTIC: overstated CAGR ~4pp, understated DD ~15pp** — it applied clean state-weight gating to the basket INDEX (instant perfect de-risk, no T+1, no parking friction). Real engine: T+1 + fill + parking deploy/withdraw friction + basket held through transitions → DD −31.7 (the −16 was fiction). CAPIT-on-idle (user idea, mechanism correct) added only +0.27pp (capit capacity-limited + single-book idle cash mostly in benign states). **LESSON: NEVER trust index×state-weight sims for RISK — they hide DD; run the per-name engine. Diversification+allocator of V2.3 genuinely manage DD better than a concentrated basket. PRODUCTION = V2.3 (custom30V); single-book hướng ĐÓNG.** [[custom30v_selector_keep_yieldcombo_2026]] [[v23_audit_2014_now_deliverable]]

### (Below = SUPERSEDED optimistic finding from the FLAWED light sim — kept for the record)

User ([REDACTED]20) hỏi: nếu chạy custom30 như MỘT sổ (thay cả danh mục), số trong bảng basket-ablation (yieldcombo 36.5%/ps3 39.4/v3comp 38.0, 2014→nay) có đạt được không? + v3comp có bền vững hơn yieldcombo không?

**Bảng basket-ablation là GROSS INDEX** (`custom_basket.build_pit`: level=1000·cumprod(1+ret), cap-weight chained, KHÔNG TC/T+1/gating/slippage, [REDACTED]-100%-invested). 36% chỉ đạt như rổ trần [REDACTED]-invested (MaxDD −36.7%).

**FAITHFUL single-book DT5G-gated** (`custom30v_singlebook_faithful.py`: state-weight W={1:0,2:.2,3:.7,4:1.0,5:1.3} T-1 causal + TC 0.3%×turnover + EXBULL borrow 10%/yr + transition-TC + rebal-TC):
| selector | 2018→nay CAGR/Sh/DD/Cal | 2014→nay |
|---|---|---|
| yieldcombo (custom30V) | **29.65% / 1.55 / −21.1 / 1.41** | 27.96/1.60/−21.1/1.33 |
| v3comp | 29.52 / 1.59 / −19.6 / 1.51 | 28.50/1.66/−19.6/1.45 |
| (ref) Production V2.3 multi-book | *25.07 / 1.52 / −29.9 / 0.84* | — |

**🔑 PHÁT HIỆN: single-book gated custom30 VƯỢT V2.3 multi-book trên giấy MỌI trục** (+4.5pp CAGR, DD −21 vs −30, Calmar 1.41 vs 0.84), kể cả faithful (phí transition+borrow chỉ ăn ~1pp vì DT5G ~49 transitions/12y). Nghĩa là sleeve active (BAL momentum/LAG PEAD/CAPIT) gần đây DRAG so với chỉ ôm rổ quality-cheap gated (BAL grind 2025, LAG edge-cycle).

**⚠️ CAVEAT trước khi kết luận (CHƯA switch production):** (1) single-book là INDEX-level (rổ×state-weight), CHƯA per-name engine T+1-Open như V2.3 25.07% → cần chạy rổ-gated qua pt_v23 per-name để apples-to-apples; (2) tập trung 1 factor (quality-cheap large-cap), V2.3 đa dạng hơn → không hedge nếu factor đảo; (3) DD −21 phụ thuộc HOÀN TOÀN DT5G timing (single point of failure); (4) DT5G state in-sample (nhưng V2.3 cũng vậy → fair). NEXT (chờ user): per-name engine + walk-forward IS/OOS chống overfit.

**v3comp vs yieldcombo BỀN VỮNG?** RETURN: KHÔNG — by-year v3comp thắng chỉ **6/14 năm**, edge dồn 2021(+18.5pp)+2014; 2018→nay HÒA (−0.13pp). RISK-ADJUSTED: nhỉnh đều nhẹ (Sh 1.66 vs 1.60, DD −19.6 vs −21.1, Cal 1.45 vs 1.33). → giữ kết luận [[custom30v_selector_keep_yieldcombo_2026]]: v3comp không bền trên return; chỉ hơn nhẹ risk-adj. Production parking vẫn yieldcombo=custom30V.
