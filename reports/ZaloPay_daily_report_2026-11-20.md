📊 **EOD Trading Report — ZaloPay (2026-11-20)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

💰 **NAV 2026-11-20: 904,952,158 VND** (-3,647,751 VND, -0.40% so với hôm trước)
   Cổ phiếu 441,642,650 · Tiền mặt 9,283,200 · Nợ margin 0 · Trứng vàng 454,026,308
   Từ go-live: -95,936,898 VND lãi/lỗ (-9.67%); NAV đổi -82,913,409 VND, trong đó nạp/rút ròng +13,023,489 VND
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-11-20]
🧭 Value Radar: 🟢 2.1 RẺ (phân vị 10 năm) · P/E 9.62 (p0) · P/B 1.67 (p2) · spread EY−CCTG 12T +3.00pp (p4)  [dữ liệu tới 2026-11-20]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.93% − lãi vay 12.5% = -2.57pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-11-20, 315/338 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-11-19): quiet | EM_dd60=-17.9% VNI_dd60=-8.8% DXY_mom60=5.2% TNX=5.05 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-11-20)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-11-20


Nguồn: `golive_v23_recommendations_2026-11-20.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### TCH — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **141.0** | ta (recomputed here) = **141**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.7018759359591991 |
| vol-breakout | `Volume>=Volume_3M_P50*1.3 & Close>Close_T1` | +20 | ✅ | Volume=15750900.0 Volume_3M_P50=5304600.0 Close=13900.0 Close_T1=13250.0 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=23.19067929066398 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=13900.0 MA20=12872.5 |
| PE-cheap-vs-5Y | `PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y` | +15 | ✅ | PE=17.517584219011184 PE_MA5Y=25.26372737702471 PE_SD5Y=12.474238184429636 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| RSI1W>0.65 | `D_RSI_Max1W > 0.65` | +5 | ✅ | D_RSI_Max1W=0.7018759359591991 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P4=40214422757.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=11939.0 MA50_T1=11895.0 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P1=125416921400.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
