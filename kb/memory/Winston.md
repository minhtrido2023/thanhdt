# Working memory — Winston
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Winston.

- [2026-06-23T14:32:53Z] macro_health fix hoàn thành (2026-06-23). 3 bugs từ reorg commit 10ae395 đã fix trong daily_refresh_v34b_linux.sh: (1) rm data/_cache_*.pkl, (2) cp data/v3_1_clean.csv, (3) thêm step [14] macro_healthcheck.py. Trạng thái: HEALTHY/OK/missed=0/NEUTRAL. VIX hơi elevated (19.2 vs MA 18.1) nhưng không trigger cap. Cron 23:15 ICT hôm nay sẽ chạy script đã sửa.
