# Cổng edge-health THEO THÁNG cho BAL — **NO-GO, user duyệt KHÔNG BẬT** (12/11/2026 17:10 ICT, `decided_by: user`)
Yêu cầu gốc 10/11: tháng BAL âm ⇒ dừng mua mới; dương ⇒ mở lại; âm ⇒ khoá lại. Kèm nghiên cứu "có hơn chạy mù không".

## Kết luận nghiên cứu (Taylor_20261110_053025; quant-skeptic CONFIRMED medium)
- ΔCAGR gate−mù **−2,62pp (pin0%) / −2,76pp (pin1M)**, P(Δ>0)=0,01, CI90 [−4,76;−0,65]; biến thể loại CAPIT −1,96/−2,05pp. IS/OOS cùng âm, 11/12 năm âm.
- Sharpe KHÔNG cải thiện; Calmar/MaxDD không phân biệt được với khoá ngẫu nhiên cùng tỷ lệ ⇒ lợi DD chỉ là giảm exposure.
- Tín hiệu vô thông tin: P(tháng sau âm|âm)=39,5% vs 38,1%|dương (Fisher p=1,0); lệnh bị chặn thắng 55,9% vs 56,6% lệnh giữ.
- 18/18 biến thể×quy ước âm; cùng luật cho LAG: −3,08/−3,37pp. KHÔNG phải edge.
- Báo cáo: `agents/Taylor/research/bal_edge_monthly_gate_20261110/REPORT.md`; registry `data/results_registry.md` mục 2026-11-10.

## Trạng thái code
Cổng tầng lệnh + máy trạng thái đã dựng, arch-review 2 vòng, selfcheck 88/0 — **KHÔNG MERGE, KHÔNG cài cron, KHÔNG ghi `data/edge_gate_state.json`**. Giữ để tham khảo: repo WorkingClaude nhánh `feat/bal-edge-monthly-gate-20261110` (commit f103ae0fa, worktree `wt-bal-edge-gate-20261110`); repo mike worktree `agents/Taylor/wt-mike-bal-edge-20261110` (8f9250363). BAL tại 10/11 theo shadow = LOCKED từ 2026-09 (tháng 10 −4,91%) — thông tin, không chặn gì.
Muốn bật lại về sau: quyết định khẩu vị rủi ro của user, giá ~2–2,8pp CAGR/năm.
Cổng LAG (DD + giá ≤ tâm, tạm) KHÔNG đổi: `lag-dd-zone-gate-20261109.md`.
