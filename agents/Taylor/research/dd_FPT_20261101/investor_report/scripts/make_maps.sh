#!/usr/bin/env bash
# Bản đồ khu vực FPT (chạy từ investor_report/). Toạ độ: OSM Nominatim 01/11/2026 (Quy Nhơn: Wikipedia, cấp thành phố). Chỉ bản đồ VÙNG (luật 15).
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
SRC="Ranh giới: geoBoundaries VNM-ADM1 (2008, public domain). Toạ độ: OpenStreetMap Nominatim 01/11/2026, cấp cơ sở; gần đúng."
$PY -I /home/trido/.claude/skills/dd-investor-report/scripts/make_map.py --points scripts/pts_north.csv --bbox 105.30,20.80,106.05,21.30 --highlight "Hà Nội" \
  --title "Miền Bắc: trụ sở và ĐH FPT Hòa Lạc" --source "$SRC" --out figs/map_north.png
$PY -I /home/trido/.claude/skills/dd-investor-report/scripts/make_map.py --points scripts/pts_central.csv --bbox 106.40,13.40,110.10,16.40 --highlight "Đà Nẵng,Bình Định" \
  --title "Miền Trung: Đà Nẵng, Quy Nhơn (Bình Định cũ, nay thuộc Gia Lai)" --source "$SRC Quy Nhơn: Wikipedia." --out figs/map_central.png
$PY -I /home/trido/.claude/skills/dd-investor-report/scripts/make_map.py --points scripts/pts_south.csv --bbox 105.30,9.70,107.20,11.60 --highlight "Ho Chi Minh,Bình Dương,Long An,Cần Thơ" \
  --title "Miền Nam: TP.HCM, Cần Thơ; dở dang ở Bình Dương 415 tỷ, Long An 37 tỷ (chỉ tô tỉnh)" --source "$SRC" --out figs/map_south.png
