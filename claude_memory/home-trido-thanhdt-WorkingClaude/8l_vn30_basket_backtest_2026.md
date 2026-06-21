---
name: 8l-vn30-basket-backtest-2026
description: "Liquidity-screened 8L-quality 30-stock basket vs VN30 — backtest 2014-2026, PIT proxy"
metadata: 
  node_type: memory
  type: project
  originSessionId: 50b1889d-4ee8-4d58-ad56-4b899bb1146b
---

# "8L-VN30" — rổ 30 mã chất lượng 8L lọc thanh khoản, có hơn VN30 không? ([REDACTED]08)

User hỏi: dựng một "VN30 phiên bản 8L" (sắp theo thanh khoản) có hiệu quả cao hơn VN30 không. Backtest quarterly-rebalance 2014→2026, sàn thanh khoản ≥10B/ngày, top 30, EW + liq-weight, mục tiêu Calmar.

**⚠️ PROXY, KHÔNG phải 8L live.** 8L thật (`rank_8l.py`) là snapshot hiện tại, không PIT. Dựng proxy point-in-time từ cột `ticker`: ROE_Min5Y/ROIC5Y/FSCORE (quality), pb_z/pe_z=(X−MA5Y)/SD5Y (rẻ-vs-lịch-sử), Close/HI_3M_T1 (dislocation), Volume_3M_P50*Price (liq). Dùng **percentile-rank** (miễn nhiễm outlier fundamental đầu kỳ). v1 composite thuần = HỎNG (loại sạch bank → thua VNINDEX). **v3 FAITHFUL** = bank theo lăng kính thật của rank_8l (gate NPL + cov + ROE + PB/ROE) merge_asof từ `bank_rating_history.csv` (18 bank, ROE/NPL/cov 2018+, theo eff_time=ngày công bố → PIT chuẩn; pre-2018 fallback ROE_Min5Y+PB), non-bank = composite percentile rescale 0-95; gate non-bank ROE_Min5Y≥12%&FSCORE≥4 hoặc ROIC≥12%. → rổ **6.7 bank/kỳ** (khớp 8L thật ~6; rổ 2026 CTG/ACB/MBB/TCB/VCB top). Vẫn KHÔNG tái dựng được commodity-trough (cyclical) PIT → cyclical under-rep, coi là **ước lượng sàn**.

**Kết quả FAITHFUL (Calmar):** VN30_LIQ(≈VN30) 6.83%/Sh.37/DD−52/Cal.13 · **8L_EW 6.53%/Sh.38/DD−42.7/Cal.15** · 8L_LIQ 6.07%/DD−49.5/Cal.12 · VNINDEX 9.70%/Sh.53/DD−43.6/Cal.22 · **8L_EW+timing 8.22%/Sh.50/DD−37.8/Cal.22** · **VN30_LIQ+timing 11.35%/Sh.56/DD−44.4/Cal.26**. Timing = về cash khi state(vnindex_5state) BEAR/CRISIS.

**3 kết luận (vững sau khi sửa bank):**
1. **vs VN30 thuần: 8L hơn KHIÊM TỐN, lợi thế = RỦI RO** (Calmar .15 vs .13, MaxDD tốt hơn ~9-10pp, 2022 −37% vs −52%, vol 25% vs 30%); lợi nhuận NGANG/thua nhẹ. Rổ không-timing nào cũng THUA VNINDEX.
2. **Đưa BANK vào đúng cách lại GIẢM nhẹ return (6.94→6.53%), KHÔNG tăng** — vì bank lag pha bò tập trung megacap: 2021 rổ+48% vs VN30+80%; **2025 rổ EW chỉ +3.6% vs index +40%** (VIC-led, EW loại VIC/VHM-giá-nào-cũng-mua). "Thắng VN30 về return" KHÓ *chính vì* return VN30 = sự TẬP TRUNG megacap mà rổ EW chất lượng cố tình tránh.
3. **Đòn bẩy thật = CỔNG THỊ TRƯỜNG (DT5G đã có), không phải chọn cổ 8L.** Cash-in-bear nâng mọi rổ vượt VNINDEX về Calmar; triệt 2022 (−37%→0). Khi đã timing, 8L quality KHÔNG tăng return (VN30+t 11.35% > 8L+t 8.2%) chỉ GIẢM RỦI RO (vol 19.6 vs 24.3, DD −37.8 vs −44.4). Khớp [[fa_layer_ic_audit_2026]] ("momentum book RESISTS FA overlays", FA edge ZERO in BULL), [[dt5g_walkforward_event_audit]] ("DT5G = fail-safe risk gate not return-enhancer").

**Size sweep (user hỏi rổ 20):** càng ÍT mã càng KÉM. 8L_EW Calmar theo N: 15→.12, **20→.10 (TỆ NHẤT, DD−47.8)**, 25→.14, 30→.15(DD−42.7), 40→.17(DD−42.0); +timing cùng xu hướng (30→.22, 40→.23). Quality 8L = tilt PHÒNG THỦ DIỆN RỘNG (breadth), KHÔNG phải alpha top-N tập trung → cô đặc chỉ thêm rủi ro đặc thù + đào sâu DD. Chốt: giữ 30 mã (40 nhỉnh hơn chút nhưng turnover/phí cao hơn). Reinforces "quality = mild diffuse tilt not sharp stock-pick".

**Cảnh báo:** dòng "+timing" LẠC QUAN (vnindex_5state v3.4b base = in-sample, biết 2022 trước); 2020 lộ giá thật của timing (rổ +50%→−1%, lỡ chữ V). Bản deploy trung thực = DT5G qua get_gated_state. Quarterly DD thô; TC 0.2%/turnover, 8L quay vòng nhiều hơn (0.65 vs 0.45/q).

**Đề xuất thực dụng "8L-VN30":** 18 mã 8L liquid ≥10B hiện tại (FPT,VCB,ACB,MBB,TCB,BID,CTG,VNM,IDC,OIL,NKG,HAH,HSG,CTR,VGC,BMP,SIP,GEG), EW, gắn cổng DT5G. Kỳ vọng (sau −1.5pp): lợi nhuận ngang/nhỉnh VN30, **DD thấp hơn ~10–15pp** = chuyến đi êm. Files: backtest_8l_vn30.py, data/{panel_8l_quarterly,bt_8l_vn30_nav,vnindex_qtr,state_qtr}.csv.
