#!/usr/bin/env bash
# Bản đồ vùng KCN của SIP (chạy từ investor_report/). Toạ độ: OpenStreetMap Nominatim 01/11/2026 (tên KCN/xã theo BCTN 2025).
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -I /home/trido/.claude/skills/dd-investor-report/scripts/make_map.py --points scripts/pts_region.csv --bbox 105.95,10.45,107.35,11.45 \
  --highlight "Tây Ninh,Ho Chi Minh,Đồng Nai,Bình Dương" \
  --title "Bốn KCN của SIP: 75% quỹ đất còn lại nằm ở Phước Đông (Tây Ninh)" \
  --source "Ranh giới: geoBoundaries VNM-ADM1 (2008, tỉnh cũ: Bình Dương nay thuộc TP.HCM; Gò Dầu–Trảng Bàng thuộc Tây Ninh). Toạ độ: OpenStreetMap Nominatim 01/11/2026, gần đúng theo tên KCN/xã, không phải ranh dự án. Diện tích còn lại: BCTN 2025 (31/12/2025)." \
  --out figs/map_region.png
