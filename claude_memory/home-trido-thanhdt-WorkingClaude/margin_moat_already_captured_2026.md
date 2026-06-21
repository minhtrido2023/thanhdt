---
name: margin_moat_already_captured_2026
description: "Operating/net margin as moat signal in 8L rating — already captured by GPM+ROIC; don't add"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

User ([REDACTED]20): biên LN hoạt động (EBITM) & ròng (NPM) chưa được rating đánh giá cao; DN đạt biên >20% ổn định (so đối thủ ngành) thường có MOAT → nên rate cao hơn. **Validated → thesis ĐÚNG bản chất NHƯNG hệ đã bắt qua proxy; KHÔNG thêm.**

Rating hiện dùng: `moat_tag` = **GPM (biên gộp)** level(≥0.25)+ổn định(cv≤0.20)+ROE; `core_score` = ROIC/ROE/debt/CFO-NP/FSCORE. KHÔNG có trục EBITM/NPM trực tiếp.

**Validation (BQ panel 2014+, non-financial, industry-relative rank trong sector-month, vs profit_3M):**
1. Margin CÓ dự báo + giảm crash (thesis moat đúng): crash% theo EBITM-tercile 16.9%(lo)→12.0%(hi); IC ebitm_rel +0.045/npm_rel +0.045/**gpm_rel +0.050 (cao nhất)**.
2. **EBITM_rel ⟂(GPM_rel+ROIC_rel) = resid-IC −0.007 (t−0.6) = ZERO** → operating margin REDUNDANT once GPM+ROIC có. NPM_rel resid +0.016 (t1.3) not-sig. Kinh tế: ROIC≈op-profit/vốn + GPM=pricing-power đã span EBITM.
3. **NPM TOXIC**: 82 mã NPM≥30% nhưng EBITM<5% = moat giả từ lãi-ngoài-hoạt-động (VEF/CII/KDC/PDR/NVB/SCR/VEA 164%/HHS 338% — equity-method/holding, EBITM ÂM). Đây là lý do hệ né NPM. Reverse trap = CTF (NPM mỏng che distress, [[value_composite_v3_2026]]).

**VERDICT: KHÔNG thêm EBITM/NPM vào rating.** Thesis biên=moat đã mã hóa đúng qua GPM+ROIC+ROE (SCS EBITM72%/KSF59% đã moat STRONG rating2; rating-1 median EBITM18%/NPM25%). Thêm = redundant (EBITM) hoặc phá (NPM); đổi rating còn đụng custom30/V2.3 (gate theo rating). GPM (đang dùng) là margin-signal sạch+mạnh nhất. Option duy nhất hợp lý nếu user muốn = thêm EBITM/NPM vào OUTPUT chỉ để HIỂN THỊ (transparency, không đổi score) — chưa wire.
