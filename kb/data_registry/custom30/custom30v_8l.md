---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.custom30v_8l
group: custom30
role: production parking (money-path)
writer: custom30_history.py với CUSTOM30_TABLE=custom30v_8l, papertrade_daily.sh step [6b] 15:30 ICT
---

# tav2_bq.custom30v_8l

**Status: CANONICAL (production parking)**

## Là gì
Rổ custom30V (yieldcombo, namecap≤10%) — đúng rổ đã backtest +7.4pp; `golive_recommend_v23.py` đọc qua
`custom30.TABLE_V`, `pt_v22_dt5g.py`/DC-book/screens cũng đọc.

## Ai ghi / cadence
`custom30_history.py` với `CUSTOM30_TABLE=custom30v_8l`, `papertrade_daily.sh` step [6b] 15:30 ICT —
**writer từng mồ côi 2026-06-18→07-11** (drop sau cutover 06-30), revive job Taylor_20260711_035824,
**verify sống 07-11 15:45 ICT** (chạy tay, job Taylor_20260711_084145: 1440 rows/48 rebals, rebal hiện
tại 2026-05-05, overlap 16/30 vs blend — đúng rổ yieldcombo).

## Bẫy
07-11 là THỨ BẢY → cron 1-5 không chạy cuối tuần; lần cron ĐẦU TIÊN chạy [6b] = T2 07-13 15:30 ICT
(fix e02a75b vào sau lần cron cuối T6 07-10). Deadline thật = rebalance quý ~2026-08-05: nếu
`MAX(rebal_date)` không nhích sau 08-05 → writer lại chết.

**Cập nhật 2026-08-04**: xác nhận `MAX(rebal_date)`/`__TABLES__.last_modified_time` sống đúng lịch
(ghi 08-04 15:33:15 ICT, 3' sau cron 15:30 — writer KHỎE, chỉ chưa tới ngày rebalance mới nên nội
dung 1440 rows/48 rebals chưa đổi). Bẫy "im lặng nếu mồ côi lại" giờ có gate chủ động, không còn
phải chờ ai hỏi mới kiểm tra tay: `mike/bin/custom30v_rebalance_watch.sh` (cron 16:05 ICT T2-T6,
sau `papertrade_daily.sh`) — so `MAX(rebal_date)` với ngày trigger q2m5 gần nhất, WARN ngày đầu
chưa nhích, RED nếu sang ngày thứ 2. Xem `kb/cron_registry.md` dòng 16:05.
