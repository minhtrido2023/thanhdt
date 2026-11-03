"""Toạ độ có nguồn (vi.wikipedia.org API prop=coordinates, tra 03/11/2026) + gọi make_map.py. Chạy: wc_venv/bin/python -I make_map_inputs.py"""
import csv, subprocess, os
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, "figs")
MM = "/home/trido/.claude/skills/dd-investor-report/scripts/make_map.py"; PY = "/home/trido/thanhdt/wc_venv/bin/python"
W = "vi.wikipedia.org/wiki/"
assets = [
 ("Mỏ đá Tân Lập (CN Bình Phước)", 11.46917, 106.97056, "mine", 0.05, 0.05, "tâm huyện Đồng Phú; " + W + "Đồng_Phú_(huyện); toạ độ xã Tân Lập không tra được"),
 ("Mỏ mới Tam Lập 1 khu 1", 11.29417, 106.80778, "mine", 0.05, -0.02, "tâm huyện Phú Giáo; " + W + "Phú_Giáo_(huyện); vị trí mỏ không tra được"),
 ("Mỏ mới Minh Hòa", 11.27222, 106.37806, "mine", -0.02, 0.09, "tâm huyện Dầu Tiếng (xã Minh Thạnh thuộc Dầu Tiếng); " + W + "Dầu_Tiếng_(huyện)"),
 ("NM gạch Long Nguyên", 11.2725, 106.63472, "plant", -0.1, -0.09, "tâm huyện Bàu Bàng (xã Long Nguyên); " + W + "Bàu_Bàng_(huyện)"),
 ("NM gạch Mỹ Phước (dừng 08/2025)", 11.14944, 106.5975, "plant", -0.2, -0.07, "tâm thị xã Bến Cát; " + W + "Bến_Cát_(thị_xã)"),
 ("Trụ sở + BOT ĐT743", 10.92194, 106.76944, "hq", 0.05, -0.07, "phường Tân Đông Hiệp; " + W + "Tân_Đông_Hiệp"),
 ("ICD Hoa Lư (Lộc Thạnh)", 11.82444, 106.58639, "project", 0.05, -0.02, "tâm huyện Lộc Ninh (xã Lộc Thạnh); " + W + "Lộc_Ninh_(huyện)"),
]
markets = [
 ("TP.HCM", 10.769444, 106.681944, "market", -0.2, -0.1, W + "Thành_phố_Hồ_Chí_Minh (toạ độ dùng ở báo cáo NNC, vi.wikipedia)"),
 ("Đồng Nai (Biên Hòa)", 10.95, 106.87389, "market", 0.06, 0.0, W + "Biên_Hòa_(thành_phố)"),
 ("Bình Dương (Bến Cát)", 11.14944, 106.5975, "market", -0.2, 0.05, W + "Bến_Cát_(thị_xã)"),
 ("Mỏ Tân Lập", 11.46917, 106.97056, "mine", 0.05, 0.03, W + "Đồng_Phú_(huyện)"),
]
for name, rows, bbox, hl, title in (("fig_19_map_assets", assets, "106.15,10.7,107.25,11.95", "Bình Phước,Bình Dương", "Mỏ đá, nhà máy gạch, ICD và trụ sở của MVC"),
        ("fig_20_map_markets", markets, "106.3,10.6,107.3,11.6", "Bình Dương,Đồng Nai,Ho Chi Minh", "Thị trường tiêu thụ chính: Bình Dương – TP.HCM – Đồng Nai")):
    p = os.path.join(F, name + ".csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["name", "lat", "lon", "kind", "dx", "dy", "note"]); w.writerows(rows)
    subprocess.run([PY, "-I", MM, "--points", p, "--bbox", bbox, "--highlight", hl, "--title", title,
        "--source", "Ranh giới tỉnh: geoBoundaries VNM-ADM1 (bản 2008, tỉnh cũ). Vị trí gần đúng theo xã/huyện (toạ độ trung tâm, vi.wikipedia.org), không phải ranh giấy phép. Nguồn địa danh: BCTC Q3/2026, ĐHĐCĐ 2026, website công ty.",
        "--out", os.path.join(F, name + ".png")], check=True)
print("maps ok")
