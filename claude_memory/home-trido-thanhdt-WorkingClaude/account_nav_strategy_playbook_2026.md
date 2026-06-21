---
name: account-nav-strategy-playbook-2026
description: "Standing rule — khi user giao một tài khoản, nhìn AUM và chọn cấu hình V2.3 (nhất là parking policy) theo dải NAV như đã nghiên cứu"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c43f57c4-5ab6-411b-90c9-9b936e53b60c
---

User ([REDACTED]15): "Khi tôi giao cho bạn quản lý một tài khoản, bạn nhìn vào số tiền quản lý và quyết định chiến lược như đã nghiên cứu." → STANDING OPERATING PROCEDURE: nhận tài khoản → suy cấu hình V2.3 từ AUM, tự động, không hỏi lại.

**LUẬT (từ park-state + capacity sweep [REDACTED]15, BQ-audited T+1 Open, self-check 0 VND, vehicle=custompitg, deploy config `v23a none postbull 0.0 edge`, state=DT5G):**
- Vehicle custompitg LUÔN bật; **position sizing tự %-of-NAV**; **CHỈ cổng parking `cash_etf_states` đổi theo NAV.**
- **AUM 1 – ~100 tỷ → `{3:0.7}`** (NEUTRAL-only = V0 live hiện tại). park-BULL **TẮT**. Dưới ~50 tỷ idle là CẤU-TRÚC/phòng-thủ (cash CRISIS/BEAR + sổ không phải lúc nào cũng đủ 12+12 tín hiệu), KHÔNG phải kẹt-công-suất → park-BULL chỉ thêm beta/DD vô ích (50 tỷ: V1 +BULL1.0 = −0.79pp CAGR, Sharpe 1.79→1.59, DD −17.8→−19.1).
- **AUM ≥ ~150 tỷ → `{3:0.7, 4:0.7}`** (thêm BULL liều **0.7 = VỪA**, KHÔNG full-1.0, KHÔNG exbull). Gỡ idle kẹt: **+1.08pp@200 tỷ** (21.28→22.36), **+1.37pp@500 tỷ** (18.83→20.20), Calmar giữ/tăng (1.05→1.13@500), audit 0 VND. Full-1.0 bị dominate (DD/Sharpe tệ + artifact self-check ~3e-7 ở frac=1.0); exbull (V3) làm tệ hơn V2.
- **~100–150 tỷ = vùng chuyển tiếp** (park-BULL ≈ trung tính), mặc định giữ TẮT. Ngưỡng 150 tỷ là **NỘI SUY** (đo 50 & 200 tỷ, chưa đo V2@100); khi tài khoản tiến gần ~100–150 tỷ → chạy nhanh V2@100/150 chốt ngưỡng trước khi bật.

**⚡ TRIGGER LÀ NAV HIỆN TẠI, KHÔNG PHẢI NAV KHỞI ĐẦU (user [REDACTED]17, ĐÃ CHỐT):** "khi NAV đạt mốc 150 tỷ thì chuyển custom30 vào bull-park, cho dù NAV bắt đầu tại bao nhiêu." → Đây là quy tắc ĐỘNG theo running-NAV, KHÔNG phải quyết-một-lần lúc nhận tài khoản: tài khoản start 50 tỷ compound lên 150 tỷ → vẫn PHẢI bật `{3:0.7,4:0.7}`; ngược lại nếu drawdown về <150 thì tắt lại. Kiểm tại mỗi rebal/daily-plan. Confirm lại tại 50B ([REDACTED]17): bull-park 0.7 ở 50B = REJECTED (26.5→24.8% CAGR, Sharpe 1.84→1.61, DD xấu hơn — ôm index qua correction hậu-bull); chỉ ≥150 mới dương. **Đòn bẩy đúng cho idle-cash ở MỌI NAV = lãi tiền gửi 4-5% trên ~37% idle = +1.5-1.85pp không-rủi-ro (backtest để 0%/yr), KHÔNG phải ép bull-park ở NAV nhỏ.**

**Capacity curve (live-prod V0, full 1→500 tỷ, BQ-audited):** 1–50 tỷ = dải PHẲNG 25.5–27.0% CAGR (đỉnh ~10–20 tỷ; risk-adj sweet spot 20–50 tỷ Calmar 1.45–1.48; 1 tỷ hơi thấp 25.5% DD −20.7% vì fill nhanh-đầy → tập trung cao). Decay CHỈ >50 tỷ: 50→100→200→500 = 25.9→23.8→21.3→18.8 (−7pp). idle%avg phẳng ~33–35% dưới 50 tỷ (cấu-trúc), phình →39% ở 500 tỷ (công-suất).

**Why:** parking-beta chỉ có giá trị ở SCALE (khi idle thật sự kẹt); ép beta ở AUM nhỏ chỉ tăng DD không tăng return. **How to apply:** đọc AUM → set NAV input + cổng parking theo bảng; mọi thứ khác tự chạy. **Ranh giới:** tôi quyết cấu hình + sinh kế hoạch hằng ngày (`recommend_tomorrow`/`bot_prepare_plan`); KHÔNG tự đặt lệnh/chuyển tiền (nguyên tắc + đặt-lệnh PHS/DNSE chưa thông) → execution qua bot user cho phép.

**Trạng thái wiring (ĐÃ WIRE [REDACTED]17):** `pt_v22_dt5g.py` giờ derive `PARK_DICT = {3:0.7,4:0.7} if TOTAL_NAV>=150e9 else {3:0.7}` (dòng ~64-71) và dùng `cash_etf_states=PARK_DICT` ở cả 2 book (BAL/LAG). `TOTAL_NAV` đọc từ env `NAV_TOTAL_B` (mặc định 50), `BAL_NAV=LAG_NAV=TOTAL_NAV/2` → **mỗi run live đọc NAV hiện tại → tự bật bull-park khi chạm 150 tỷ, bất kể NAV khởi đầu**. Verify: 50/100B→{3:0.7}; 150/200B→{3:0.7,4:0.7}; syntax OK; behavior @50B không đổi. **Vận hành: operator/bot set `NAV_TOTAL_B`=NAV tài khoản hiện tại mỗi ngày** (nếu không set, mặc định 50 → bull-park không bao giờ bật). `pt_v23_audit_2014.py` đã parametrize qua env `PARK_STATES`. ⚠️ Backtest single-path (2014→nay) KHÔNG flip giữa-sim (cash_etf_states tĩnh cho cả sim); dynamic-flip chỉ áp cho LIVE per-run — muốn backtest đúng đường-compound-vượt-150 cần sửa trong simulate() (chưa làm, không cấp thiết). Artifacts: `collect_parkstate.py`, `data/parkstate_experiment_summary.csv`. Liên quan [[capacity-ceiling-custom-vn30-2026]].
