# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 (production yieldcombo, KHÔNG dùng v3 composite — IS-overfit)
## Đang chờ
- Winston: hoàn thành snapshot pipeline (scripts/build_snapshot.py + daily_refresh step 15 + chạy lần đầu)
- Wendy: legal-severity DGC → Taylor risk/reward
## Next
- Sau khi Winston xong: test Tier-1 sweep với `LOCAL_SNAPSHOT_DIR=data/snapshots python sweep_configs.py`
- gộp answer các con vào KB mỗi nhịp consolidate
## Đã xong hôm nay
- 3-tier experiment protocol: Taylor patch simulate_holistic_nav.py (LOCAL_SNAPSHOT_DIR) + sweep_configs.py + experiment_protocol.md
- Winston snapshot pipeline: in progress

