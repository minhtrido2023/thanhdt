---
name: vix-peak-bottom-overlay-2026
description: "VIX-peak làm tín hiệu dự báo đáy VN / re-risk sớm khỏi CRISIS — tested [REDACTED]10, KHÔNG deploy vào DT5G"
metadata: 
  node_type: memory
  type: project
  originSessionId: aef6fbca-d773-43aa-a1a9-59d9cab14b3a
---

**Câu hỏi (user, [REDACTED]10):** dùng đỉnh VIX (causal-confirmed: VIX≥30 trong 60 phiên + đã nguội ≥25% từ đỉnh) để dự báo VNINDEX sớm chạm đáy / nâng state khỏi CRISIS sớm hơn — có hiệu quả hơn DT5G hiện tại không?

**Kết quả (analyze_vix_peak_bottom.py):**
1. **Standalone "mua khi VIX qua đỉnh" trên VN = FAIL**: 96 lần fire 2000→nay, median fwd60 **−2.8%**, win rate 43%, fwd120 −4.3%. Trong gấu kéo dài (2001-02, 2007-08, 2010-11, 2022H1) VIX lập đỉnh NHIỀU LẦN, mỗi lần "nguội" là một bull-trap — VN tiếp tục rơi.
2. **Mù cấu trúc (decoupling)**: chỉ **3/9 episode CRISIS của DT5G** (2020 COVID VIX 82.7, 2022H1 36.5, 2024 38.6) có VIX≥30. 6 episode còn lại (2014/2016/2018/2019/2022Q4/2023) là khủng hoảng nội địa, VIX max chỉ 17–26 → tín hiệu câm hoàn toàn. Đối xứng với bài học US-VN decoupling trong audit 2000-history.
3. **Gated overlay (CRISIS + VIX-peak-confirmed → floor BEAR 20%)**, NAV index-proxy 2014→nay: +0.30pp CAGR (12.42→12.72%), Sharpe 1.00→1.02, MaxDD ~bằng. Biến thể →NEUTRAL: +1pp CAGR nhưng DD xấu hơn (−18.8→−20.5). Floor BEAR + price-guard +3%: 12.80%/Sharpe 1.03 (tốt nhất nhưng cùng họ).
4. **Attribution = event-concentrated**: toàn bộ edge = 2020 (+5.9% NAV, đoạn 31/03→26/05) + 2022Q4 (+2.1%) + 2024 (+1.1%), bị trừ bởi 2018 (−1.8%, VIX-floor nâng state khi VN còn rơi tới 28/05) + 2022H1 (−3.3%). Net +4.5%/12 năm ≈ 2 sự kiện thắng vs 2 thua, n quá nhỏ.

**Quyết định: KHÔNG deploy** — cùng họ và cùng độ lớn với [[crisis-release-overlay]] confirmed-recovery (+0.50pp prod-spec, đã reject [REDACTED]02); vi phạm nguyên tắc DT5G re-risk thuần price-based (easing-floor đã tắt [REDACTED]03); và VIX mù 6/9 khủng hoảng VN. Chỗ ĐÚNG của VIX-nguội đã có sẵn: gate trong capitulation playbook (routing BEAR-guard + van margin crisis ×1.5) — mua golden-egg cổ phiếu size nhỏ, sai thì mất sleeve nhỏ chứ không re-risk cả book. Liên quan [[dt5g-walkforward-event-audit]], [[dt5g-8l-crisis-capitulation-2026]].
