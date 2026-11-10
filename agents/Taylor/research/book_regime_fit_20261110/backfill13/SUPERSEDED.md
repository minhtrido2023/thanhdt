# SUPERSEDED 2026-11-10 — KHÔNG ÁP bản này
Job Taylor_20261110_103537 (arch-review vòng 1 NEEDS_CHANGES): `raw_basis` cũ (heuristic stale |Close/Price−1|<0,2 +
đổi tỉ số >0,5%) ghi giá SAI vào pkl — 87 dòng trên 13 phiên thưa khác bản dựng lại >0,1% (đo: `../backfill13_v2/recon.txt`).
Thay bằng **`../backfill13_v2/`** (`earnings_px_bf13v2.pkl` / `lagged_pos_ov_bf13v2.pkl`, md5 trong `../backfill13_v2/MD5.txt`).
- pkl cũ đổi tên `*.SUPERSEDED.pkl` (md5 gốc vẫn ở `MD5.txt` của thư mục này); `build_backfill13.py --apply` nay từ chối.
- `engine/pt_bf13.py`, `engine/pt_liq2.py` trỏ tên cũ ⇒ không chạy lại được nữa; kết quả cũ (`engine/bf13*`, `engine/liq2*`) giữ làm lịch sử.
