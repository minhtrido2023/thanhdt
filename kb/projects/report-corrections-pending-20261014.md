# Đính chính số đã công bố — hàng đợi ghi chú ở báo cáo kế tiếp (user duyệt 2026-10-14)

Cách đính chính (user chốt, Q1 + quyết định bước 3): **MỘT khối ghi chú ngắn ở báo cáo tuần kế tiếp (T7 17/10) + 1 tin vào topic Trading report; KHÔNG phát hành lại, KHÔNG sửa file báo cáo cũ.**
Prompt weekly (`bin/check_report_cadence.sh`, `CORR_STEP`) tự đưa mục này vào bản soạn nếu ngày soạn < 2026-10-24.

## A. Mốc VN-Index "từ khi bắt đầu" sai (bước 4, 9 ô)
Nguồn: `agents/Taylor/research/fund_step4_r2_20261014/published_inventory.md` (MEASURED 14/10, chuỗi `vnindex_tr_daily.csv`).
Mốc đúng (user duyệt 16:11 ICT 14/10): SpaceX = đóng cửa 30/06/2026; ZaloPay = đóng cửa 06/07/2026. Chỉ số GIÁ.

| Báo cáo | Đã công bố | Đúng | Mốc đã dùng |
|---|---:|---:|---|
| SpaceX tuần 14–18/09 | −2,76% | −2,38% | 01/07 |
| SpaceX tuần 21–25/09 | −4,40% | −4,03% | 01/07 |
| SpaceX tuần 28/09–02/10 | −6,94% | −6,58% | 01/07 |
| SpaceX tuần 05–09/10 | −7,08% | −6,72% | 01/07 |
| ZaloPay tuần 14–18/09 | −1,76% | −1,51% | 07/07 |
| ZaloPay tuần 21–25/09 | −3,42% | −3,17% | 07/07 |
| ZaloPay tuần 28/09–02/10 | −6,68% | −5,74% | 03/07 |
| ZaloPay tuần 05–09/10 | −6,82% | −5,88% | 03/07 |
| ZaloPay tháng 09 | −5,02% | −4,06% | 03/07 |

Hướng sai: chênh so VN-Index ở các ô SpaceX bị thổi ~0,37 điểm %; ZaloPay 0,25 (mốc 07/07) hoặc ~0,94 điểm % (mốc 03/07). Tỉ suất của chính tài khoản KHÔNG đổi.
Báo cáo tháng 07 (SpaceX_ZaloPay_monthly_report_2026-07): cột ZaloPay đúng mốc 06/07 là −5,84% (tỉ suất tài khoản đã đính chính riêng 27/09).

## B. Sổ NAV lịch sử (bước 3, áp lên dữ liệu thật 14/10 11:50 ICT)
Nguồn: `agents/Taylor/research/fund_history_lock_20261014/D_impact/` + `kb/projects/fund-unit-performance-policy-20261010.md`.
- NAV SpaceX 02/07 sửa còn 990.304.455 (trước 994.733.747): tỉ suất NGÀY 02/07 và 03/07 lệch ~0,44 điểm %; "từ đầu/MTD/WTD" không đổi.
- Chèn dòng 06/08 cho cả 2 tài khoản (trước đó thiếu): **biến động tháng 08** đã in ZaloPay 25,58% → đúng 18,27%; SpaceX 12,37% → 12,80%.
- Biến động tháng 07 SpaceX in 17,3% → 17,4%.
- Tin EOD Discord SpaceX 07/08 in "+0,12% so với hôm trước" → đúng +1,098%.
