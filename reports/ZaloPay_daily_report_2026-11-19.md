📊 **EOD Trading Report — ZaloPay (2026-11-19)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

⚠️ Không đọc được positions broker (ZaloPay): HTTPSConnectionPool(host='openapi.dnse.com.vn', port=443): Read timed out. (read timeout=30)
❌ [2026-11-19] Không lấy được vị thế broker — KHÔNG tính NAV (tránh đăng số thiếu vị thế).
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-11-19]
🧭 Value Radar: 🟢 2.3 RẺ (phân vị 10 năm) · P/E 9.66 (p0) · P/B 1.68 (p2) · spread EY−CCTG 12T +2.96pp (p5)  [dữ liệu tới 2026-11-19]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.85% − lãi vay 12.5% = -2.65pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-11-19, 313/333 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-11-18): quiet | EM_dd60=-16.2% VNI_dd60=-8.1% DXY_mom60=5.0% TNX=5.07 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-11-19)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-11-19


Nguồn: `golive_v23_recommendations_2026-11-19.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### TCH — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **121.0** | ta (recomputed here) = **121**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.6253262459680075 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=1.0436890630302855 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=13250.0 MA20=12777.5 |
| PE-cheap-vs-5Y | `PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y` | +15 | ✅ | PE=16.69841661164735 PE_MA5Y=25.340144037140416 PE_SD5Y=12.62349065735229 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| RSI1W>0.65 | `D_RSI_Max1W > 0.65` | +5 | ✅ | D_RSI_Max1W=0.7195155584211326 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P4=40214422757.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=11895.0 MA50_T1=11872.0 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P1=125416921400.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
