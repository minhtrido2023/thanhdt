📊 **EOD Trading Report — ZaloPay (2026-11-18)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

💰 **NAV 2026-11-18: 914,361,764 VND** (-7,881,103 VND, -0.85% so với hôm trước)
   Cổ phiếu 451,263,150 · Tiền mặt 9,282,996 · Nợ margin 0 · Trứng vàng 453,815,618
   Từ go-live: -86,527,292 VND lãi/lỗ (-8.73%); NAV đổi -73,503,803 VND, trong đó nạp/rút ròng +13,023,489 VND
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-11-18]
🧭 Value Radar: 🟢 2.7 RẺ (phân vị 10 năm) · P/E 9.70 (p0) · P/B 1.69 (p3) · spread EY−CCTG 12T +2.91pp (p5)  [dữ liệu tới 2026-11-18]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.85% − lãi vay 12.5% = -2.65pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-11-18, 314/334 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-11-17): quiet | EM_dd60=-15.7% VNI_dd60=-6.8% DXY_mom60=4.7% TNX=5.10 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-11-18)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-11-18


Nguồn: `golive_v23_recommendations_2026-11-18.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### TCH — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **141.0** | ta (recomputed here) = **141**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.6491376589962673 |
| vol-breakout | `Volume>=Volume_3M_P50*1.3 & Close>Close_T1` | +20 | ✅ | Volume=7324000.0 Volume_3M_P50=5304600.0 Close=13350.0 Close_T1=13250.0 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=24.97007352115964 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=13350.0 MA20=12715.0 |
| PE-cheap-vs-5Y | `PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y` | +15 | ✅ | PE=16.824442397395632 PE_MA5Y=25.551252000532088 PE_SD5Y=12.767888854295515 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| RSI1W>0.65 | `D_RSI_Max1W > 0.65` | +5 | ✅ | D_RSI_Max1W=0.7195155584211327 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P4=40214422757.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=11872.0 MA50_T1=11849.0 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P1=125416921400.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
