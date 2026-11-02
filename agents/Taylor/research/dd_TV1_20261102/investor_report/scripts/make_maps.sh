#!/usr/bin/env bash
# Bản đồ khu vực TV1 (chạy từ investor_report/). Toạ độ gần đúng, có nguồn — xem SELFCHECK.md / Phụ lục C.
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
M=/home/trido/.claude/skills/dd-investor-report/scripts/make_map.py
$PY -I $M --points scripts/pts_central.csv --bbox 107.2,15.35,108.45,16.3 --highlight "Quảng Nam,Đà Nẵng" \
  --title "Miền Trung: nhà máy thuỷ điện Sông Bung 5 (Quảng Nam cũ, nay thuộc TP Đà Nẵng)" \
  --source "Ranh giới 2008 (geoBoundaries). Sông Bung 5: Global Energy Monitor (xã Mà Cooih–Thạnh Mỹ); Đà Nẵng: OSM. Gần đúng." \
  --out figs/map_central.png
$PY -I $M --points scripts/pts_hn.csv --bbox 105.45,20.75,106.15,21.25 --highlight "Hà Nội" \
  --title "Hà Nội: trụ sở công ty (mảng tư vấn)" \
  --source "Ranh giới 2008 (geoBoundaries). Địa chỉ: pecc1.com.vn; toạ độ OSM, gần đúng." \
  --out figs/map_hn.png
