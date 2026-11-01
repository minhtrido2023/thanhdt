#!/usr/bin/env bash
# Bản đồ khu vực TV2 (chạy từ investor_report/). Toạ độ: OSM Nominatim 01/11/2026, gần đúng cấp xã/phường/huyện (không phải ranh dự án).
set -euo pipefail
PY=/home/trido/thanhdt/wc_venv/bin/python
M=/home/trido/.claude/skills/dd-investor-report/scripts/make_map.py
$PY -I $M --points scripts/pts_south.csv --bbox 104.6,8.5,107.3,11.3 --highlight "Cần Thơ,Cà Mau,Hồ Chí Minh" \
  --title "Phía Nam: trụ sở và hai hợp đồng EPC nguồn điện" \
  --source "Ranh giới: geoBoundaries VNM-ADM1 (2008, tỉnh cũ). Toạ độ: OpenStreetMap Nominatim 01/11/2026, gần đúng cấp phường/xã (Phước Thới–Ô Môn; xã Tân Thuận, Đầm Dơi cũ), không phải ranh dự án." \
  --out figs/map_south.png
$PY -I $M --points scripts/pts_north.csv --bbox 104.2,21.4,105.7,22.3 --highlight "Yên Bái,Tuyên Quang" \
  --title "Phía Bắc: hai nhà máy sinh khối eREX (Yên Bái, Tuyên Quang cũ)" \
  --source "Ranh giới: geoBoundaries VNM-ADM1 (2008). Yên Bái cũ nay thuộc Lào Cai; Tuyên Quang mới gồm Hà Giang cũ. Toạ độ: OSM Nominatim 01/11/2026 — Yên Bái 1 lấy trung tâm huyện Văn Yên (Mậu A), Tuyên Quang lấy xã Xuân Vân; gần đúng." \
  --out figs/map_north.png
