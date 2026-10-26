# bdi_daily_te_fill — ghi chú (Winston, job Winston_20261026_070857, 2026-10-26)
Nguồn: tav2_bq.commodity_prices, metric_key=baltic_dry, source=trading_economics, cadence=daily. KHÔNG phải nguồn production; chưa có consumer.
`bdi_daily_te_fill.csv` = 10 ngày TE có mà `bdi_daily_real.csv` thiếu trong 2026-05-05→2026-10-23 (9 ngày đã biết + 2026-10-23).

## 2 ngày LỆCH giá trị — chưa chọn bên nào (chờ Taylor/Mike)
| date | csv (bdi_daily_real) | TE | ghi chú |
|---|---|---|---|
| 2026-07-06 | 2717 | 2797 | |
| 2026-08-31 | 3186 | 3157 | csv 08-31 = 3186 đúng bằng TE 08-28 (3186); 08-28 không có trong csv → nghi csv gán nhầm ngày (lệch 1 phiên cuối tuần), CHƯA kết luận |

Đối chiếu 114 ngày chung: 112 khớp, 2 lệch (trên). 0 ngày csv không có trong TE.
