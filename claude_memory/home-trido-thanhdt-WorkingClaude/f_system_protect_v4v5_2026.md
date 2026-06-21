---
name: f_system_protect_v4v5_2026
description: "Test dung F-system (VN30F overlay) bảo vệ book V4/V5 — phần lớn DƯ THỪA + sai công cụ; chỉ cứu gấu-chậm-2022, vô dụng với grind phi-khủng-hoảng (rủi ro thật của V5)"
metadata: 
  node_type: memory
  type: project
  originSessionId: da955fb4-3cf3-4f12-a372-44b0e169e1a4
---

**[REDACTED]08.** User hỏi dùng F-system (overlay VN30F1M, margin không chiếm vốn) BẢO VỆ book V4/V5 (đã gated DT5G) đang paper-trade. Model: combined_ret = V_ret + λ×F_sleeve_ret. Files: f_protect_v4v5_test.py. NAV V4/V5 từ data/5sys_prodspec_201401_202605_dt5g.csv (V4_V121_ENS, V5_V4_KellyQ2).

**KẾT LUẬN: F bảo vệ V4/V5 rất hạn chế + phần lớn DƯ THỪA.**

Hai sleeve khác hẳn:
- **F_hedge** (M_SHORT: CRISIS−1.0/BEAR−0.3/else flat) = HEDGE THẬT: corr V5 −0.14 (worst10% −0.09), +0.28% đúng ngày V5 xấu nhất.
- **F_full** (DT5G+VanB+deadband.10 overlay) = KHÔNG hedge: corr +0.45, −0.84% đúng ngày V5 xấu → return-amplifier đi XUỐNG cùng V5.

**Hiệu quả giảm DD theo episode (V5 + 0.3×F_hedge):**
- COVID 2020 crash nhanh: −11.3%→−11.6% (TỆ hơn, gate+short đều trễ velocity, V5 tự gate đã lo).
- Bear 2022 gấu CHẬM: −10.5%→−6.7% (+3.8pp ✅ — chỗ DUY NHẤT F_hedge giúp: DT5G fire 148/169 ngày, sụt từ từ đủ cho short tích lũy).
- **Grind 2025-26 = MaxDD THẬT của V5 −24.7%: →−24.7% VÔ TÁC DỤNG (0/136 ngày crisis/bear).**

**Hai lý do F không cứu rủi ro thật:**
1. CÙNG CÒ SÚNG DT5G → dư thừa: MaxDD V5 (−24.7%, 9/2025→3/2026, 135 phiên) xảy ra 100% trong NEU/BULL/EXBULL, DT5G KHÔNG báo crisis ngày nào → F_hedge đứng FLAT đúng lúc V5 chảy máu. V4/V5 đã tự phòng thủ bằng chính gate đó.
2. SAI CÔNG CỤ: grind 2025-26 = sách 8L phân kỳ khỏi VN30 đang phẳng/lên (pattern VIC-led megacap, khớp [[8l_vn30_basket_backtest_2026]]) = rủi ro STYLE/idiosyncratic KHÔNG phải market-beta. Short VN30F khi index phẳng/lên = LỖ KÉP.

**Dùng F đúng vai:** (a) F_hedge nhỏ λ0.2-0.3 = bảo hiểm gấu-CHẬM-2022 rẻ/sạch (âm corr, +0.3-1pp CAGR, −3-4pp DD gấu kéo dài) — KHÔNG cứu grind/crash-nhanh; (b) F_full = TẤN CÔNG tăng return (V5 CAGR 27.5→34%@λ0.3, Sharpe 1.54→1.61) nhưng MaxDD sâu hơn −24.7→−26%, KHÔNG phải phòng thủ.

**Cò-súng-NHANH độc-lập-DT5G (f_fast_hedge_test.py) — CÓ bắt phần DT5G bỏ lỡ nhưng có TRẦN:**
- ⚠️ Đính chính nhận định "short index=lỗ kép" trước đó là QUÁ bi quan: grind 2025-26 VN30F THẬT giảm −6.2% (intra-DD −16.7%) trong khi V5 −24.7%, corr lúc đó 0.84 (beta V5↔VN30F toàn kỳ=0.42). Tức DT5G bỏ lỡ cú index-DD −16.7% mà không báo crisis → cò nhanh CÓ cơ hội.
- **Vol-spike** (rv10>1.3×median) × λ0.4 = bảo hiểm tail THẬT: cắt grind −24.7→−20.4% (cò DT5G C/B cũ cắt 0), giúp cả COVID −11.3→−9.7 & Bear22 −10.5→−7.1; Calmar 1.11→1.22. PHÍ ~2.6pp CAGR (27.5→24.9), Sharpe giữ 1.55.
- **MA20-break** × λ0.4 = overlay gần MIỄN PHÍ: Sharpe 1.54→1.70, CAGR +0.6pp (short trend có carry dương) — nhưng hedge trend NHANH, không cứu grind chậm.
- TRẦN cứng: V5 −24.7% vs VN30F −16.7% → ~8pp phân kỳ style KHÔNG hedge được bằng bất kỳ công cụ VN30F. Hedge sâu (λ0.8) cắt grind −16% nhưng đẻ drawdown MỚI −27% (over-hedge lỗ khi hồi) + Sharpe sụp 1.22. Trần thực tế ≈ cắt 4-5pp.
- ⚠️ IN-SAMPLE: grind=1 episode, ngưỡng+λ fit trên chính nó → −4.3pp LẠC QUAN (vol-spike giúp cả COVID/Bear22 = cross-val nhẹ, tín hiệu thật nhưng đừng tin độ lớn).
- CHỐT 2 tool khác vai: vol-spike λ0.4=insurance tail (phí 2.6pp) ; MA20-break λ0.4=Sharpe-booster gần free. Fix THẬT cho style-grind vẫn ở phía SÁCH (drawdown-stop V5 / giảm tập trung ngành), futures chỉ van phụ ~4-5pp.

**Drawdown-stop NGAY TRÊN SÁCH V5 (f_v5_drawdown_stop_test.py, shadow-based, full 2014+) — BÁC BỎ:**
- Lưới X(8-15%)stop × Y(4-6%)reentry × floor(cash/nửa-size): MỌI cấu hình bị **futures vol-spike hedge THỐNG TRỊ**. Best stop X10/Y4-cash = CAGR 21.9%/Sh1.42/MaxDD−20.0/Cal1.09/grind−19.5 vs vol-spike×0.4 CAGR 24.9/Sh1.55/MaxDD−20.4/Cal1.22/grind−20.4 (futures cao hơn mọi mặt).
- Stop thất bại vì: (1) whipsaw đắt — BÁN sách lúc yếu, re-enter cao hơn, mất hồi phục sắc → cú V COVID/Bear22 còn TỆ HƠN (−11.3→−14.6); (2) đẻ drawdown whipsaw MỚI, MaxDD nhiều cấu hình xấu đi; (3) chỉ grind chậm cải thiện nhưng tốn −3.6pp CAGR + Sharpe sụt. Floor nửa-size đỡ tốn CAGR nhưng bảo vệ ít hơn, vẫn thua futures.
- CƠ CHẾ: V5=momentum Sharpe cao, alpha ở HỒI PHỤC SẮC; stop VỨT BỎ quyền hồi phục (bán hết), overlay GIỮ sách+thêm short (nhẹ hơn). → BÁN(stop) tệ hơn HEDGE(overlay). Khớp "momentum book kháng overlay".

**TỔNG KẾT điều tra "bảo vệ V5": vol-spike futures hedge ×0.4 = TỐT NHẤT (cắt grind −4.3pp, Sharpe giữ, phí −2.6pp, độc lập DT5G); MA20-break = booster Sharpe gần free; F_hedge DT5G-keyed = dư thừa; F_full = tấn công; drawdown-stop = BÁC BỎ. SỰ THẬT CUỐI: ~8pp grind là phân kỳ style 8L-vs-megacap KHÔNG hedge/stop được — fix gốc ở CẤU TRÚC SÁCH (giảm tập trung/lệch style 2025 VIC-led), van timing chỉ chạm ~4-5pp phần beta.**

Liên quan [[vn30f_data_fsystem_revalidation_2026]], [[dt5g_walkforward_event_audit]], [[8l_vn30_basket_backtest_2026]], [[fa_layer_ic_audit_2026]].
