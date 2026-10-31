#!/usr/bin/env bash
# Bản đồ khu vực TCH (chạy từ investor_report/). Toạ độ: OSM Nominatim 31/10/2026 (src/assets_notes.md).
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -I scripts/make_map.py --points scripts/pts_region.csv --bbox 105.45,20.40,107.25,21.35 --highlight "Hải Phòng" \
  --title "Địa bàn: gần như toàn bộ quỹ đất ở Hải Phòng" \
  --source "Ranh giới: geoBoundaries VNM-ADM1 (2008, public domain). Toạ độ: OpenStreetMap Nominatim 31/10/2026, gần đúng cấp phố/khu đô thị." \
  --out figs/map_region.png
