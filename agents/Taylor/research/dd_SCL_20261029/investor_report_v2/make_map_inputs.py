"""Toạ độ có nguồn (vi.wikipedia.org API prop=coordinates, tra 03/11/2026) + gọi make_map.py. Chạy: wc_venv/bin/python -I make_map_inputs.py"""
import csv, subprocess, os
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, "figs")
MM = "/home/trido/.claude/skills/dd-investor-report/scripts/make_map.py"; PY = "/home/trido/thanhdt/wc_venv/bin/python"
W = "vi.wikipedia.org/wiki/"
north = [
 ("Trụ sở + nhà máy, dự án Phả Lại (Chí Linh)", 21.107744, 106.388995, "hq", 0.04, 0.05, "tâm TP Chí Linh (Hải Dương cũ, nay thuộc Hải Phòng); " + W + "Chí_Linh_(thành_phố)"),
 ("Hà Nội", 21.028333, 105.853333, "market", -0.05, 0.06, W + "Hà_Nội"),
 ("Hải Phòng", 20.866389, 106.6825, "market", 0.04, -0.05, W + "Hải_Phòng"),
 ("Bắc Ninh", 21.187548, 106.073406, "market", -0.05, 0.06, W + "Bắc_Ninh"),
]
south = [
 ("Green SCL — tro xỉ Vĩnh Tân (Tuy Phong)", 11.37861111, 108.52611111, "plant", -0.6, 0.12, "tâm huyện Tuy Phong (Bình Thuận cũ, nay thuộc Lâm Đồng); " + W + "Tuy_Phong_(huyện)"),
 ("TP.HCM", 10.769444, 106.681944, "market", 0.05, -0.1, W + "Thành_phố_Hồ_Chí_Minh"),
]
for name, rows, bbox, hl, title in (
        ("fig_09_map_north", north, "105.5,20.55,106.95,21.5", "Hải Dương,Hà Nội,Hải Phòng,Bắc Ninh", "Miền Bắc: trụ sở, nhà máy và dự án Phả Lại cạnh các đô thị tiêu thụ"),
        ("fig_10_map_south", south, "106.3,10.4,109.1,11.9", "Bình Thuận,Ho Chi Minh", "Phía Nam: nguồn tro xỉ Vĩnh Tân và thị trường TP.HCM")):
    p = os.path.join(F, name + ".csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["name", "lat", "lon", "kind", "dx", "dy", "note"]); w.writerows(rows)
    subprocess.run([PY, "-I", MM, "--points", p, "--bbox", bbox, "--highlight", hl, "--title", title,
        "--source", "Ranh giới tỉnh: geoBoundaries VNM-ADM1 (bản 2008, tỉnh cũ). Vị trí gần đúng theo tâm huyện/thành phố (vi.wikipedia.org), không phải ranh nhà máy. Địa danh: BCTC Q3/2026, website công ty. Tỷ trọng thị trường: không công bố.",
        "--out", os.path.join(F, name + ".png")], check=True)
print("maps ok")
