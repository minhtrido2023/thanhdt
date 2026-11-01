#!/usr/bin/env bash
# Bản đồ khu vực HHS (chạy từ investor_report/). Toạ độ: OSM Nominatim 01/11/2026 + 31/10/2026 (DD TCH).
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -I scripts/make_map.py --points scripts/pts_region.csv --bbox 105.55,20.55,107.05,21.25 --highlight "Hải Phòng,Hà Nội" \
  --title "Địa bàn BĐS: Hải Phòng (dự án) và Hà Nội (văn phòng CRV, tòa N01)" \
  --source "Ranh giới: geoBoundaries VNM-ADM1 (2008, public domain). Toạ độ: OpenStreetMap Nominatim 31/10–01/11/2026, gần đúng cấp phố/khu đô thị. Xe tải: bán toàn quốc (tỷ trọng vùng không công bố)." \
  --out figs/map_region.png
