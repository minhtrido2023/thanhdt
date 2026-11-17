# Hit Details — 2026-11-17


Nguồn: `golive_v23_recommendations_2026-11-17.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### TCH — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **141.0** | ta (recomputed here) = **141**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.6362769579633792 |
| vol-breakout | `Volume>=Volume_3M_P50*1.3 & Close>Close_T1` | +20 | ✅ | Volume=7035900.0 Volume_3M_P50=5304600.0 Close=13250.0 Close_T1=13050.0 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=44.04347612439671 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=13250.0 MA20=12642.5 |
| PE-cheap-vs-5Y | `PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y` | +15 | ✅ | PE=16.69841661164735 PE_MA5Y=25.37023757660133 PE_SD5Y=12.689137422145617 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| RSI1W>0.65 | `D_RSI_Max1W > 0.65` | +5 | ✅ | D_RSI_Max1W=0.7452323376207147 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P4=40214422757.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=11849.0 MA50_T1=11826.0 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P1=125416921400.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
