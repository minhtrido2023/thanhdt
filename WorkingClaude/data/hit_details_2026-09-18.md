# Hit Details — 2026-09-18


Nguồn: `golive_v23_recommendations_2026-09-18.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### VPI — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **126.0** | ta (recomputed here) = **126**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.6226673407012446 |
| uptrend | `Close>MA50>MA200` | +25 | ✅ | Close=62900.0 MA50=58182.4 MA200=54530.9 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=174.48926870941864 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=62900.0 MA20=60474.0 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P4=3904359336.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=58182.4 MA50_T1=58043.8 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P1=26895380753.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
