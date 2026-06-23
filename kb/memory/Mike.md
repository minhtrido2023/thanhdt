# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 (production yieldcombo, KHÔNG dùng v3 composite — IS-overfit)
## Đang chờ
- Wendy: legal-severity DGC → Taylor risk/reward
## Next
- Test Tier-1 sweep: `LOCAL_SNAPSHOT_DIR=data/snapshots /home/trido/thanhdt/wc_venv/bin/python sweep_configs.py`
- Fix CLAUDE.md: VNINDEX mirror columns list sai (chỉ có VNINDEX và VNINDEX_PE trong ticker; không có VNINDEX_RSI_Max3M)
- gộp answer các con vào KB mỗi nhịp consolidate
## Đã xong hôm nay
- 3-tier experiment protocol SHIPPED:
  - Taylor: patch simulate_holistic_nav.py (LOCAL_SNAPSHOT_DIR) + sweep_configs.py + experiment_protocol.md
  - Winston: build_snapshot.py (SIGNAL_V11 đúng) + daily_refresh step 15 + snapshot today ready
  - Snapshot: data/snapshots/signal_20260624.parquet (657K rows, 9 cols, 8.3MB) + vni_20260624.parquet

