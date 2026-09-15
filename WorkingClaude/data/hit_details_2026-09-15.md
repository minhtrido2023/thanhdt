# Hit Details — 2026-09-15


Nguồn: `golive_v23_recommendations_2026-09-15.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### VPI — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **131.0** | ta (recomputed here) = **131**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.5704463532895055 |
| uptrend | `Close>MA50>MA200` | +25 | ✅ | Close=61000.0 MA50=57780.6 MA200=54340.45 |
| vol-breakout | `Volume>=Volume_3M_P50*1.3 & Close>Close_T1` | +20 | ✅ | Volume=2657200.0 Volume_3M_P50=1661250.0 Close=61000.0 Close_T1=60300.0 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=61000.0 MA20=59414.5 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P4=3904359336.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=57780.6 MA50_T1=57681.8 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P1=26895380753.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
