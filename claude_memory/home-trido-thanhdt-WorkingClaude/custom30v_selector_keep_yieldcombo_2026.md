---
name: custom30v_selector_keep_yieldcombo_2026
description: custom30V parking selector — keep yieldcombo; 8L v3 axis / PS does NOT robustly improve it
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

**Câu hỏi ([REDACTED]19):** custom30V parking selector "yieldcombo" (1/PE+1/PCF, go-live 30/06) chính là bản rút gọn của trục [[value_composite_v3_2026]] (ey+cfy+**ps**+golden). Áp full v3 / thêm PS làm selector có tốt hơn không? → **Audit faithful (`custom30v_select_audit.py`, build_pit gate≤3/namecap10/q2m5, chỉ khác ranker, 2014→now):**

| selector | CAGR% | Sharpe | MaxDD% | Calmar |
|---|---|---|---|---|
| yieldcombo (PROD) | 36.48 | 1.43 | −36.7 | 0.99 |
| v3gated (PS chỉ retail) | 36.87 | 1.45 | −35.1 | 1.05 |
| ps3 (PS đều, equal) | 39.43 | 1.50 | −35.2 | 1.12 |
| v3comp (PS rộng + sector-wt + golden) | 38.05 | 1.49 | −33.8 | 1.12 |

**KẾT LUẬN: GIỮ yieldcombo, KHÔNG đổi selector.** Lý do:
1. **PS gated chỉ-retail ≈ yieldcombo (+0.4pp, nhiễu)** — lợi ích PS KHÔNG đến từ bán lẻ mà từ áp RỘNG lên non-retail (rổ VN30-like chỉ ~3-5 mã retail). Trực giác "PS chỉ work retail" không đúng data.
2. Bản "có ăn" (PS rộng, +1.6-2.9pp) thì **trái lý do kinh tế** (PS vô nghĩa cho bank/financial) + **in-sample** (v3 weights tuned 2014-now) + **cực lụm cụm** (v3gated 2021 +27.7 / 2024 −18.3 / 2020 −12.4 → net ~0; ps3 dồn 2016; v3comp dồn 2021). Edge return độ tin thấp; chỉ Calmar/DD nhích nhẹ.
3. NAV impact quy ra V2.3 nhỏ (rổ chỉ chạy khi park idle cash NEUTRAL@0.7 → ~+0.5-1pp trên phần parked).

**Bài học kiến trúc:** trục 8L v3 ĐÚNG chỗ = **SCREENER** (universe rộng, IC edge thật/validated); SAI chỗ nếu nhét vào **selection của rổ tập trung gated** (khớp prior [[capit_selection_study_2026]]: chọn-mã trong rổ gated khó cải thiện, overlay = overfit). custom30V/V2.3 chọn mã theo RATING + yieldcombo đơn giản là đúng — KHÔNG wire valuation v3 vào basket selection. Code `BASKET_SELECT=v3comp|ps3|v3gated` để lại trong custom_basket.py (env-guarded, dormant; prod default yieldcombo/blend bất biến).
