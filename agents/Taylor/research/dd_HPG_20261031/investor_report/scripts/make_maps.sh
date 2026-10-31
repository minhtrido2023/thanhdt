#!/bin/bash
# Bản đồ khu vực (luật 15) — chạy: bash make_maps.sh ; bản sao make_map.py của skill, chỉ đổi đường dẫn font/data + nhãn "plant".
set -e
cd "$(dirname "$0")"; IR=..; PY=/home/trido/thanhdt/wc_venv/bin/python
SRC="Ranh giới: geoBoundaries VNM-ADM1 (2008, tỉnh cũ). Vị trí gần đúng theo xã/huyện (Wikipedia/OSM), không phải ranh nhà máy. Thị trường: tỷ trọng không công bố."
$PY -I make_map.py --points pts_north.csv --bbox 105.45,20.55,106.95,21.35 --highlight "Hưng Yên,Hải Dương,Hà Nội,Hải Phòng" --title "Miền Bắc: trụ sở, KLH Hải Dương, thị trường Hà Nội–Hải Phòng" --source "$SRC" --out $IR/figs/map_north.png
$PY -I make_map.py --points pts_central.csv --bbox 107.75,15.05,109.15,16.3 --highlight "Quảng Ngãi,Đà Nẵng" --title "Miền Trung: KLH Dung Quất (HRC, thép thô)" --source "$SRC" --out $IR/figs/map_central.png
$PY -I make_map.py --points pts_south.csv --bbox 105.5,9.85,107.2,11.25 --highlight "Long An,Ho Chi Minh,Bình Dương,Đồng Nai,Cần Thơ" --title "Miền Nam: thị trường tăng nhanh nhất, NM Long An đang xây" --source "$SRC" --out $IR/figs/map_south.png
