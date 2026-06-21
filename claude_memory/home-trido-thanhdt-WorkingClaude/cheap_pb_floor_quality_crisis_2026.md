---
name: cheap_pb_floor_quality_crisis_2026
description: "8L L1-Valuation — \"rẻ thật\" = quality + PB-near-1 + sụt đột ngột (PB-floor on temporary crisis), KHÁC value-trap rẻ-theo-PE"
metadata: 
  node_type: memory
  type: project
  originSessionId: 305a69ff-3483-4f95-8f30-23845b96fb7d
---

8L research ([REDACTED]02): định nghĩa "rẻ" cho L1 Valuation. User insight: PE-rẻ có thể là bẫy (giá vẫn rơi khi khủng hoảng NỘI TẠI vì E sụp); PB về gần 1 trên công ty TỐT đang crisis TẠM THỜI = mua giá rất tốt. **Empirically VALIDATED trên tav2_bq.ticker, 2014+, profit_3M (lọc Infinity, BETWEEN -100 AND 500).**

**Định nghĩa "chất lượng / rating lịch sử tốt"** = sàn nhiều năm: `ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6`. (Risk_Rating thô KHÔNG đơn điệu sạch — rating 1=7.2%/75%, 4=13.9%/77.5%, 5-6 kém → dùng quality-floor, không dùng Risk_Rating làm trục chính.)
"Sụt đột ngột" = `Close/HI_3M_T1 <= 0.80` (giảm >20% từ đỉnh 3M).

**Interaction table (median profit_3M / winrate%):**
| Cohort | PB<1.0 | PB 1.0-1.5 | PB>1.5 |
|---|---|---|---|
| Tốt + Sụt>20% | **+7.3%/66%** | +2.7%/58% | +2.2%/55% |
| Tốt + Không sụt | +4.4%/65% | +2.1%/58% | +0.6%/52% |
| Junk + Sụt>20% | +1.4%/52% | −1.7%/45% | −2.6%/43% |
| Junk + Không sụt | +0.7%/51% | 0.0%/47% | −0.8%/42% |

**Kết luận chính:**
1. **Cú sụt CHỈ tạo giá trị cho công ty tốt** (drop-premium +2.9pp: 4.4→7.3 ở PB<1.0). Với junk, sụt giảm = BẪY (−1.7..−2.6% ở PB≥1) → đúng "khủng hoảng nội tại" user mô tả.
2. **PB là trục rẻ sắc hơn PE** trong nhóm tốt+sụt: PB<1.0 = 7.3%/66% vs PE<8 = 6.1%/64%. PE chỉ an toàn KHI đã lọc chất lượng trước (PE bẫy chính là vì E sụp trong crisis nội tại).
3. **Sụt càng sâu càng tốt** (tốt + PB 0.7-1.3, đơn điệu): sụt>35%=+6.2%/67.5% > 20-35%=+4.3% > 8-20%=+3.6% > gần đỉnh=+2.9%. = "khủng hoảng tạm thời → giá tốt".
4. **Bền vững**: ô KEY (tốt+sụt>20%+PB<1.0) vượt market-median 12/13 năm (chỉ 2015 kém). Phòng thủ mạnh trong gấu: 2022 mkt −6.8%→+0.4%; 2023 +12.4 vs +1.7; 2025 −0.1→+12.2.

**Live screen ([REDACTED]01) khớp mẫu hình** (quality + PB≤1.35 + sụt): PVT (PB0.87/PE9.1/sụt−32%/liq118tỷ = textbook), SWC (illiquid). Nới ra: TV1, REE, QTP, PVP, DRI (DRI = rubber deep-dd, x-ref [[cyclical_commodity_framework_2026]]).

**DEEP-DIVE 2 ([REDACTED]02): horizon dài + PB_z (rẻ so với CHÍNH NÓ).** Forward return tính từ Close-adj qua LEAD(63/126/252 phiên).
1. **Chuỗi tăng MẠNH DẦN theo horizon** (tốt+sụt+PB<1.0): 3M +7.8% → 6M +14.1% → **12M +22.6%/78% win**; drop-premium nới từ +3.1pp(3M) lên +4.9pp(12M); gấp ~3× junk-dropped (12M +7.1%). "Phục hồi bền" xác nhận.
2. **PB_z = (PB−PB_MA5Y)/PB_SD5Y** (dist: p05=−1.33, p50=+0.39). Trong nhóm tốt+sụt, cross abs-PB × PB_z, forward 12M median:
   - **abs PB<1.0 & z<−1 (GOLDEN) = +59.1%/96% win** (n=528) ← rẻ tuyệt đối VÀ rẻ bất thường vs lịch sử
   - abs PB<1.0 & z∈−1..0 = +26.9%/87%; abs PB<1.0 & z>0 = chỉ +11.7%/67% (rẻ kinh niên, KHÔNG dislocation)
   - abs PB≥1.0 & z<−1 = +18.8%; z>0 = +6.1%
   → **hai chiều bổ sung; phải là dislocation thật, không phải cổ rẻ triền miên.**
3. **Golden cell DỒN vào đáy khủng hoảng** (2020 n=200/+101%, 2022 +43%, 2023 +48% = ~80% mẫu) NHƯNG xuất hiện 9 năm và **excess vs thị trường DƯƠNG mọi năm 2015-25** (+2.4 đến +81pp; 2022 mua giữa gấu, mkt −10.5% mà nhóm +43% = +54pp) → ALPHA thật, không chỉ beta đáy. Tín hiệu HIẾM, chờ cửa sổ hoảng loạn.
4. **⚠️ Live [REDACTED]01: KHÔNG mã thanh khoản nào ở golden cell** (cần z<−1). PVT abs-PB 0.87 trông rẻ NHƯNG z=+1.41 (đắt vs chính nó, PB nền ~0.6) → ô yếu, KHÔNG mua theo mẫu này. REE z+1.53, PVP z+1.32 cùng cảnh. Gần nhất TV1 z−0.44 nhưng liq 2.3tỷ mỏng. Thị trường vùng cao → chưa có dislocation.

**Ứng dụng 8L**: L1 Valuation lens — "rẻ thật" = quality-floor × **PB<1.0 × PB_z<−1 (rẻ vs lịch sử chính nó)** × recent-drawdown × thanh khoản (Trading_Value_1M_P50≥2tỷ). PB_z là discriminator mạnh nhất trong vùng cheap; tránh cổ rẻ kinh niên (z>0). PE thấp đơn thuần = bẫy.

**SCRIPT ([REDACTED]02): `cheap_pb_floor.py`** — daily EOD scanner. Pull ticker_1m latest, tier hóa: GOLDEN (qual+sụt≥20%+PB<1.0+z<−1), STRONG (PB<1.0+z∈−1..0), DISLOCATION (z<−1+PB≥1.0), WATCH. So baseline cũ (data/cheap_pb_floor_prev.csv) → Telegram alert khi có mã MỚI vào GOLDEN/STRONG/DISLOCATION (qua telegram_recommend, pattern như rank_8l_daily_alert.py). Wired bước [4/4] vào `pt_8l_daily.bat` (15:30 trading days). Flags: --[REDACTED] (push standing), --no-telegram, --min-liq (def 2.0tỷ). Lần chạy đầu [REDACTED]02: 0 mã alert-tier (PVT z+1.41 đắt-vs-sử; CDN/BAX/SWC z<−1 nhưng sụt chỉ −13/−17% & illiquid) → đúng "thị trường vùng cao chưa dislocation". **EXIT-RULE BACKTEST ([REDACTED]02, `backtest_pb_floor_exit.py`)**: 553 raw signals→43 episodes (gap>60TD, 35 tk), forward daily path, mỗi rule chỉ tính entry đủ data cap (no censoring). Total ret / median hold TD / annualized-median / win%:
- FIXED hold (total tăng đều, ann GIẢM): 3M +14%/ann70% · 6M +22%/49% · 12M +43%/43% · 18M +57%/35% · **24M +82%/35%** (win 87-93% suốt). → phục hồi BỀN tới 2 năm, đừng bán non.
- **Z_TO_0 (bán khi PB_z về lại mean 5Y, z≥0) = WINNER hiệu quả vốn: +33% total / hold ~110TD(~5th) / ann **159%** / win 92.5%.** Z0_CAP12 gần y hệt (+31%/ann149%/win95%) → đa số revert trong <12M, không phụ thuộc cap dài.
- Z_TO_1 (chờ overshoot trên mean): +58% total nhưng hold 250TD/ann chỉ 72% (đổi thời gian lấy total).
- TP_30 cắt non winner (+32% capped, để lỡ phần lớn sóng vì fixed cho thấy còn chạy xa); TP_50 +51%/ann74%.
**KẾT LUẬN EXIT: bán khi PB_z≥0 (định giá về lại mức nền chính nó)** = exit đúng luận điểm (hết "rẻ vs sử") + risk-adj tốt nhất (~5th, ann 159%, 92%win). Muốn total cao hơn & vốn nhàn → giữ 12-24M (+43..82%). TRÁNH take-profit chặt (cắt winner). ⚠ n=43 dồn 2020/2022, ann inflated bởi V-recovery nhanh + chưa trừ phí/slippage. EXIT-SIGNAL feature (track holdings + Telegram "🔔 EXIT: PB_z≥0" qua data/pb_floor_holdings.csv) = **CHỜ, CHỈ build khi user XÁC NHẬN ĐÃ MUA một mã** (user [REDACTED]02: "nếu được xác nhận mua, mới cần signal này"). Hiện scanner chỉ làm entry-alert; không cần exit tracking khi chưa có vị thế thật. x-ref [[fa_layer_ic_audit_2026]], [[cyclical_commodity_framework_2026]].
