# 8L — Hệ thống 8 Lăng Kính (8 Lenses)

Hệ thống đánh giá cổ phiếu đa chiều, nhận-biết-ngành, do chúng ta xây (2026-05).
Triết lý cốt lõi: **mỗi doanh nghiệp được soi bằng đúng lăng kính theo bản chất của nó; và mỗi lăng kính có lớp phủ cấu trúc/sự kiện để không bị con số bề mặt đánh lừa.** Đi cùng hệ market-timing **Ngũ Hành** (5-state): Ngũ Hành định thời thị trường · 8L đọc cổ phiếu.

## ROUTER (bộ định tuyến — chọn lăng kính theo ngành)
Mỗi mã → BANK (ICB 8355) / POWER (ICB 7535) / CYCLICAL (commodity map) / COMPOUNDER (còn lại). Quyết định phiên bản lăng kính nào áp dụng.
- **POWER (thủy điện/nhiệt điện) = vòng đời trả nợ**: nhà máy = annuity hạ tầng có đòn bẩy. Validated: PRE‑INFLECTION (nợ cao **đang giảm** + CFO trả được nợ) + PB rẻ = 2Y +53%/win89% (mua đáy NT2‑2013); hết nợ = MATURE_YIELD (đã re‑rate, cổ tức — QTP); nợ tăng/CFO≤0 = DEBT_STRESS (tránh). FA generic nhìn NGƯỢC ngành này (nợ cao/EPS âm/IntCov âm đầu kỳ → chê đúng lúc nên mua). `power_lens.py`.

## 8 LĂNG KÍNH
- **L1 — Định giá** (đúng thước ngành): multi-lens rẻ (PEG/pe_z/pb_z + chặn value-trap) · bank P/B-vs-ROE · cyclical commodity-regime. *Bài học: "rẻ" phải tam giác hóa (GAS/FPT).*
- **L2 — Engine tăng trưởng**: runway × ROIC → COMPOUNDER / YIELD / LOWROIC(phá-giá-trị). *QTP=yield≠multibagger; cash-machine chưa đủ.*
- **L3 — Cash-machine ◆**: CFO > NP (TTM) bền + không hút vốn cổ đông. *Cách chọn VCS/DGC sớm.*
- **L4 — Moat**: lợi thế cạnh tranh (TECH/BRAND/LOCATION/SCALE/NONE) → độ bền catalyst. *DRC(no-moat)→transient vs VCS(tech+brand)→durable.*
- **L5 — Margin-cycle**: biên gộp ở đỉnh/đáy chu kỳ (DN tiêu thụ nguyên liệu). *BMP mua khi biên crushed, cảnh báo khi biên peak.*
- **L6 — Runway/TAM**: export-vô-hạn vs nội-địa-S-curve. *VNM/MWG bão hòa; FRT đang chiếm lĩnh; export=runway dài.*
- **L7 — Structural (commodity)**: percentile × cung-cầu × cost-anchor(dầu). *Rubber 0.95 nhưng deficit 6 năm → ELEVATED-SUPPORTED, không avoid mù; urê=cyclical-peak.*
- **L8 — Asset-play & Event**: NAV/SOTP cho quỹ-đất/holdco (PE đánh lừa, vd PHR) + event-override (sự cố tạm thời vs gãy cấu trúc, vd DGC).

## OUTPUT
- `unified_screener.py` → bảng sàng lọc toàn universe (route + verdict + engine + asset-play + structural).
- `rank_8l.py` → điểm tổng hợp route-aware → xếp hạng top-N.
- `dna_card.py` → hồ sơ 8L /mã (thả mã bất kỳ → đủ 8 lăng kính), 100% coverage.

## MONITORING (paper-trade + alert)
- `pt_8l_quarterly.py snapshot` → đóng băng top-20 đầu quý (entry date/price) thành cohort; `review --cohort <Q> --telegram` → cuối quý tính return/pick vs VNINDEX (win-rate, excess). Output data/pt_8l/.
- `rank_8l_daily_alert.py` (chạy EOD sau screener+rank) → so top-30 vs hôm trước, báo Telegram khi tăng hạng bất ngờ (↑≥8 bậc / mới vào top-30 / score ↑≥6). Baseline: data/rank_8l_prev.csv.
- `pt_8l_daily.bat` → orchestrator EOD (screener→rank→alert), lên lịch Task Scheduler ~15:30. Telegram qua telegram_config.json (đã có).

## PIPELINE refresh
```
bank_lens_v3.py (vnstock NPL/CAR) → power_lens.py (ICB7535 debt-lifecycle) → cash_machine_screen.py (engine)
→ margin_cycle_detector.py → saturation_detector.py → cyclical_structural.py (+Brent) → asset_play_detector.py
→ unified_screener.py → rank_8l.py (composite score) → dna_card.py
```

## META-NGUYÊN TẮC (xuyên suốt)
Mọi tín hiệu thống kê mã hóa một *prior* sẽ vỡ khi cấu trúc dịch chuyển → cần lớp phủ:
percentile→structural(cung+dầu) · PE→NAV(asset-play) · margin-revert→moat · reported-NP→event · runway→TAM · cash-machine→engine(ROIC×runway).
Chất lượng/an toàn = GATE (không phải ranker). "Rẻ"/"bão hòa" đọc 2 chiều. Mua khi sợ hãi/đáy. Giữ dài. Đo per-pick.
Hệ thống *để chỗ* cho kiến thức ngành qua manual tags: STRUCTURE · MOAT_TYPE · EVENTS · EXPORT.

## Trạng thái
Validate trên ví dụ thật: VCS/DGC (compounder export), QTP (yield), BMP (margin-cycle), DRC/DHC (moat × catalyst), PHR (asset-play), rubber (structural deficit), MBB (bank). Khoảng trống còn lại = DỮ LIỆU (P4/lưu huỳnh/% xuất khẩu chuỗi tháng — cần nguồn trả phí), không phải framework.
Memory: fa_layer_ic_audit_2026 · qt_v4_eventstudy_2026 · cyclical_commodity_framework_2026.
