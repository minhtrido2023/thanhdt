---
name: lag_forensic_peak_audit_2026
description: LAG (PEAD) book vs peak-earnings/forensic — state-conditional audit; wired forensic gate only
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

User ([REDACTED]20): LAG (PEAD) cũng dễ dính peak-earnings; review theo trạng thái thị trường (hưng phấn vs bi quan khác nhau). **Audit `lag_forensic_audit.py` (5302 LAG entries 2014+, faithful schedule NP_R≥15/prior4/pa_HL3≥5 từ earnings_events_classified.csv, post_ret=PEAD hold return, DT5G state @entry).**

**LAG = chiến lược HƯNG PHẤN/momentum** (post_ret median by state): CRISIS 0.0/BEAR 0.0/NEUTRAL +0.89/**BULL +3.96**/**EXBULL +16.4** (win 49→86%). Allocator ĐÃ zero LAG ở BEAR (đúng).

**🔑 PEAK-EARNINGS KHÔNG transfer từ value book (đảo trực giác):** trong LAG, peak>1.5 có median CAO HƠN ở NEUTRAL(+1.59 vs +0.54)/BULL(+4.15 vs +3.64)/EXBULL(+17.9 vs +16.1) — PEAD **cưỡi** drift của đỉnh (khác value book HOLD vào đảo chiều). Giá duy nhất = crash% gấp đôi (8% vs 4%) ở CRISIS/BEAR. → **KHÔNG copy peak-guard sang LAG** (sẽ cắt return đúng chỗ LAG kiếm tiền). Bài học: guard đúng cho sách này có thể sai cho sách kia.

**non-op filter (NPM>1.2·EBITM): VALIDATE THẤT BẠI risk-adjusted.** Per-entry edge thật (clean > non_op ~1pp, by-year 9/13). NHƯNG A/B re-sim full-history V2.3 (pt_v23_audit_2014, LAG_NONOP_FILTER 0 vs 1): baseline 20.95%/Sh1.51/DD−25.4/Cal0.83 → filtered 21.39%/Sh1.52/DD**−27.6**/Cal**0.77** (drop 1330 entries=25% → concentration làm DD sâu hơn, edge per-entry bị nuốt). +0.44pp CAGR đổi −2.2pp DD = KHÔNG robust → **KHÔNG wire** (để dormant env `LAG_NONOP_FILTER=1`).

**forensic gate: WIRED ON.** Backtest ~nil (flags date-aware đề hôm nay → chỉ forward) nhưng = bảo hiểm forward miễn phí chống LAG cưỡi fraud đã xác nhận (PC1 arrest, L40 −12.3%, KSF −9.8% trong 60 entries flagged lịch sử, MIXED — có lúc cưỡi pump lãi VVS+23.5/BFC+9.4 nhưng fraud blow-up không giới hạn). WIRED `pt_v22_dt5g.py` + `pt_v23_audit_2014.py` (env `LAG_FORENSIC_GATE` default 1), date-aware drop 8 mã forward (BFC/DIG/HHS/KLB/KSF/L40/PC1/VVS). Default non_op OFF path KHÔNG gọi bq (chỉ read forensic_flags.csv). [[forensic_registry_system_2026]] [[lag_bal_state_conditional_allocator_2026]]
