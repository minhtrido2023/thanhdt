#!/bin/bash
# Bản đồ KHU VỰC (luật 15). Chạy: bash make_maps.sh. Bản sao make_map.py của skill (chỉ đổi đường dẫn font/data + nhãn chú giải).
set -e
cd "$(dirname "$0")"; PY=/home/trido/thanhdt/wc_venv/bin/python
SRC="Ranh giới: geoBoundaries VNM-ADM1 (2008, tỉnh cũ). Vị trí gần đúng theo phường/quận (OSM/Wikipedia), địa chỉ trụ sở theo BCTC Q3/2026 và BCTN 2025. Số điểm giao dịch theo tỉnh: KHÔNG công bố nên điểm không theo cỡ."
$PY -I make_map.py --points pts_north.csv --bbox 105.35,20.6,106.95,21.4 --highlight "Hà Nội,Bắc Ninh,Hải Dương,Hải Phòng" --title "Miền Bắc: hội sở MB và MBV; 158 điểm giao dịch, 67% LNTT bộ phận 2025" --source "$SRC" --out ../figs/map_north.png
$PY -I make_map.py --points pts_south.csv --bbox 105.95,10.3,107.2,11.25 --highlight "Ho Chi Minh,Bình Dương,Đồng Nai,Long An" --title "Miền Nam: 122 điểm giao dịch, 27% LNTT bộ phận 2025" --source "$SRC" --out ../figs/map_south.png
