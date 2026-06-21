---
name: custom30b-bull-sleeve-2026
description: "custom30B = vehicle parking riêng cho BULL (1/PE+momentum, liq-floor 10B/ngày, namecap, 30 mã); validated tốt hơn custom30V TRONG bull mọi trục nhưng lever bull-park nhỏ; chưa wire dual-vehicle (dormant)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9db4a8d3-af8f-423f-8d4c-e1e32d8b77bb
---

**custom30B = vehicle parking dành RIÊNG cho BULL/EXBULL** (user [REDACTED]20: "sleeve riêng cho bull để tận dụng tiền thừa, dựa ý Buy-now 8L, thanh khoản ~10 tỷ/ngày làm cổng, chọn chủ yếu 1/PE hoặc kết hợp momentum, ~30 mã, đầu tư hết tiền").

**Spec đã validate (REFINED [REDACTED]20)** — env trong `custom_basket.build_pit`, prod default OFF:
- `BASKET_SELECT=pemom` + `BASKET_MOM_W=1.0` = rank(1/PE) + 1.0·rank(mom200). (cũng có `petop`=1/PE thuần, `BASKET_RSI_W` cho RSI.)
- **`BASKET_LIQ_FLOOR_B=5`** = sàn thanh khoản 5 tỷ/ngày (SWEET SPOT, hạ từ 10 → 5; xem refine bên dưới).
- `weight_scheme="namecap"` (≤10%/mã, **KHÔNG** cap-weight), `gate_rating=3`, `top_n=30`, `rebal=q2m5`.

**3 cải tiến đã test (round 2, user [REDACTED]20: hạ liq-floor / thêm momentum-volume / tín hiệu chốt đỉnh):**
1. **LIQ-FLOOR 10→5B = WIN THẬT** (`custom30b_stage2.py` confirm): pemom1.0 namecap, BULL-days 10B 18.5%/Sh2.76/OOS22.2 → **5B 19.7%/Sh2.91/OOS24.4** (+1.2pp CAGR, +0.15 Sharpe, +2.2pp OOS), **DD y nguyên −18.2** (namecap "đặt cược đều" trung hòa rủi ro small-cap — đúng ý user). 2B 19.1%/2.83 (kém 5B chút + capacity rủi ro). IC-tier (`custom30b_factor_ic.py`): bull cổ liq<2B fwd-r3 +16.1% vs >10B +6.0%, 1/PE-IC vẫn +0.118 → hạ floor mở cơ hội thật. **Chốt 5B**: tốt nhất risk-adj + deploy được (1/30 NAV/mã vừa 5B/ngày tới ~50B; account nhỏ <20B dùng 2B được).
2. **THÊM factor momentum/volume cho SELECTION = KHÔNG cải thiện.** RSI: IC cross-sectional cao nhất (combo ey+rsi +0.177) NHƯNG ở BASKET dilute momentum (pemom1.0+rsi0.5 18.3 < pemom1.0 18.5) → **bỏ RSI**. Volume-surge (volsurge/vol_p90/vol_max1y): IC SELECTION ÂM/loãng (volsurge −0.024) → **bỏ**. 1/PE+momentum(mom200) đã là spec đúng, không factor nào thêm vượt.
3. **TÍN HIỆU CHỐT ĐỈNH bằng volume-khổng-lồ = BÁC BỎ** (`custom30b_exit_v2.py`, rolling stats tự tính vì cột `Volume_Max1Y_High` BQ không tin được): trong bull VN **volume blow-off → ĐI TIẾP, không đảo**. vol_z>5 fwd_r20 +3.8% (baseline +2.9%); climax gần 1Y-max +4.7%; EXBULL5 blow-off +5.6%; RSI≥0.70+blowoff +5.3%; %neg20 phẳng ~45-49% mọi bucket. "Volume to ở đỉnh = sợ" KHÔNG đúng ở horizon 1 tháng (spike = breakout/gom hàng). → custom30B **chốt bằng REGIME-gate DT5G (bull→neutral)** mà hệ đã làm sẵn, KHÔNG thêm climax-exit (bán sớm = bán vào sóng tăng tiếp).

**Bằng chứng (faithful, `custom30b_stage1.py` + `custom30b_blend.py`, 2014→2026-06):**
- **IC-in-bull** (`value_bull_factor_ic.py`): trong BULL4_broad (state4 & breadth≥0.60) 1/PE IC **+0.161** = factor sạch CAO NHẤT (> junk +0.145 = bẫy "be fearful", > momentum +0.082). Quality (FSCORE/ROE) decay về +0.017. EXBULL fwd-r3 tụt (+8.3 vs +11.1) + junk IC fade = đỉnh hưng phấn. → 1/PE là vua, momentum bổ trợ, giữ rating-gate.
- **Bull-days head-to-head** (return rổ CHỈ trên 465 ngày bull/exbull): custom30B pemom1.0 **18.5%/Sh2.76/DD−18.2/Cal1.01/OOS22.2** > custom30V 1/PE+1/PCF **17.5%/Sh2.66/DD−19.7/Cal0.89/OOS21.0** — thắng MỌI trục, PASS chữ-ký (IS+OOS>0). Momentum tilt giúp (pemom>petop). **namecap ≫ cap-weight** (18.5 vs 16.5) → "đầu tư hết tiền" = trải 30 mã, KHÔNG mega-lean (cũng đóng lại ý megacap-sleeve cũ).
- **All-day**: custom30V (36.6%) > custom30B (27.9%) NGOÀI bull → custom30B đúng nghĩa vehicle CHỈ-bull (momentum hại ở neutral/bear); custom30V vẫn là parking NEUTRAL.

**Mức đóng góp THẬT (đừng overclaim):**
- Cả lever bull-park (giải ngân tiền nhàn trong bull) = **+0.49pp** faithful (R5 conditional bull-park, breadth-gated). Blend overlay `custom30b_blend.py` ra +2-4pp là ẢO (cộng f·return mọi ngày bull vô điều kiện, idle hằng định, không phí vốn) → upper-bound lạc quan, KHÔNG dùng số tuyệt đối.
- **Đổi vehicle custom30V→custom30B (giữ nguyên f) = +0.11→0.21pp full-system** (delta robust vì cùng f triệt tiêu sai số xấp xỉ) + Sharpe/DD tốt hơn trong bull. Nhỏ nhưng dương bền.

**SỐ THẬT FAITHFUL (dual-vehicle, self-check 0 VND, [REDACTED]20, registry R6):** đã wire splice custom30B-trong-bull vào `pt_v23_audit_2014.py` (env `BULL_VEHICLE_C30B=1 C30B_FLOOR=5`; spliced vn30_underlying + ADV theo state, 20%-ADV cap ép thật). PARK_STATES="3:0.7,4:0.7" (neutral custom30V + bull custom30B):
- **@50B = 29.23%/Sh1.81/DD−18.8/Cal1.56 = WASH vs custom30V bull-park (R2 29.24/1.82)** — floor-5B rổ mỏng → capacity cap ăn hết edge.
- **@20B = 32.26%/Sh1.94/DD−20.1/Cal1.61 = +0.57pp vs custom30V (R1 31.69/1.91)** — edge SỐNG khi capacity chưa ép.
→ **custom30B là tính-năng ACCOUNT-NHỎ (<~30-40B)**; ở NAV tham chiếu 50B ngang custom30V (Stage-1 +1pp bull-days & blend +0.15-0.2pp là UPPER-bound, capacity triệt tiêu ở 50B). Bull-park lever tổng @50B = +0.98pp vs NEUTRAL-only.

**TRẠNG THÁI = DORMANT, CHƯA wire production.** Lý do: bull-park là lever nhỏ default-OFF (re-measure khi bull tới — [[repro_results_registry_2026]] R5). Để dùng custom30B TRONG bull + custom30V TRONG neutral cần **dual-vehicle** trong `simulate_holistic_nav.simulate()` (hiện chỉ 1 `vn30_underlying`) — hoãn tới khi bật bull-park. Khi bật: bull vehicle = custom30B(pemom1.0/liq10/namecap), neutral giữ custom30V. [[settled_decisions_capit_8l_2026]] [[capacity_ceiling_custom_vn30_2026]]
