#!/usr/bin/env python3
"""make_map.py — bản đồ định vị cho báo cáo DD (PNG, Be Vietnam Pro): vị trí mỏ/nhà máy/trụ sở + thị trường chính.

  /home/trido/thanhdt/wc_venv/bin/python -I make_map.py --points points.csv --bbox 106.0,10.3,107.6,11.9 \
      --highlight "Bình Phước,Đồng Nai,TP.HCM" --title "Mỏ Mũi Tàu và thị trường chính" \
      --source "Ranh giới: geoBoundaries VNM-ADM1 (2008, public domain); vị trí gần đúng theo xã/huyện" \
      --out figs/fig_map_assets.png

points.csv (UTF-8, có header): name,lat,lon,kind[,dx,dy][,note]
  kind ∈ mine (tam giác đỏ) · hq (ô vuông xanh) · plant (hình thoi) · market (chấm tròn xanh lá, kích thước ~ cỡ chữ) · project (sao vàng) · rival (hình thoi tím, mỏ/cơ sở cạnh tranh)
  dx,dy = độ lệch nhãn theo kinh/vĩ độ (tuỳ chọn) để tránh chồng chữ.
Ranh giới tỉnh: geoBoundaries gbOpen VNM ADM1 (BẢN 2008 — Hà Tây/Bình Phước/Bình Dương… còn là tỉnh CŨ; ghi chú trên hình). Cache ở
../data/vnm_adm1_simplified.geojson (tự tải lần đầu từ geoboundaries.org). Không cần geopandas/shapely — chỉ matplotlib.

⚠️ Quy tắc: CHỈ vẽ bản đồ KHU VỰC (bbox vài tỉnh). KHÔNG vẽ bản đồ toàn quốc/inset toàn quốc từ nguồn này — dữ liệu không có
quần đảo Hoàng Sa/Trường Sa, bản đồ Việt Nam thiếu hai quần đảo là lỗi nhạy cảm với độc giả Việt Nam.
⚠️ Toạ độ phải có NGUỒN (BCTN: tên xã/huyện → toạ độ trung tâm xã/huyện trên Wikipedia/OSM). Đây là vị trí GẦN ĐÚNG, ghi rõ trong
--source; KHÔNG khẳng định đó là toạ độ ranh giới giấy phép.
"""
import argparse, csv, json, os, unicodedata, urllib.request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = "/home/trido/.claude/skills/dd-investor-report/fonts"
DATA = "/home/trido/.claude/skills/dd-investor-report/data"
GJ = os.path.join(DATA, "vnm_adm1_simplified.geojson")
API = "https://www.geoboundaries.org/api/current/gbOpen/VNM/ADM1/"
NAVY, ACCENT, GREEN, GOLD, GREY = "#0d1b2a", "#c8553d", "#2e7d5b", "#e0a526", "#8a97a6"


def nfc(s):
    return unicodedata.normalize("NFC", s).strip()


def load_geo():
    if not os.path.exists(GJ):
        os.makedirs(DATA, exist_ok=True)
        j = json.load(urllib.request.urlopen(API, timeout=30))
        open(GJ, "wb").write(urllib.request.urlopen(j["simplifiedGeometryGeoJSON"], timeout=60).read())
    return json.load(open(GJ, encoding="utf-8"))


def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            yield ring


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--points", required=True)
    ap.add_argument("--bbox", required=True, help="minlon,minlat,maxlon,maxlat")
    ap.add_argument("--highlight", default="", help="tên tỉnh (đúng chính tả bản 2008) tô đậm, cách nhau bằng dấu phẩy")
    ap.add_argument("--title", default="")
    ap.add_argument("--source", default="Ranh giới: geoBoundaries VNM-ADM1 (2008, public domain); vị trí gần đúng")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    for fn in os.listdir(FONTS):
        if fn.endswith(".ttf"):
            fm.fontManager.addfont(os.path.join(FONTS, fn))
    plt.rcParams["font.family"] = "Be Vietnam Pro"
    x0, y0, x1, y1 = [float(v) for v in a.bbox.split(",")]
    hl = {nfc(s) for s in a.highlight.split(",") if s.strip()}
    gj = load_geo()
    import math
    asp = (y1 - y0) / ((x1 - x0) * math.cos(math.radians((y0 + y1) / 2)))  # tỉ lệ khung sau hiệu chỉnh vĩ độ
    W, Hm = 7.2, 7.2 * asp
    fig = plt.figure(figsize=(W, Hm + 0.8), dpi=200)
    ax = fig.add_axes([0, 0.5 / (Hm + 0.8), 1, Hm / (Hm + 0.8)])
    for f in gj["features"]:
        nm = nfc(f["properties"].get("shapeName", ""))
        on = nm in hl or nm.replace("Ho Chi Minh", "TP.HCM") in hl
        nm = nm.replace("Ho Chi Minh", "TP.HCM")
        for ring in rings(f["geometry"]):
            xs = [p[0] for p in ring]
            if max(xs) < x0 or min(xs) > x1:
                continue
            ys = [p[1] for p in ring]
            if max(ys) < y0 or min(ys) > y1:
                continue
            ax.add_patch(PathPatch(Path(ring), fc="#dfe9f3" if on else "#f1f3f5", ec="#ffffff" if not on else "#5b7a99", lw=0.8 if on else 0.6))
        if on or any(x0 < p[0] < x1 and y0 < p[1] < y1 for r in rings(f["geometry"]) for p in r[::7]):
            r = max(rings(f["geometry"]), key=len)
            cx, cy = sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)
            if x0 + 0.05 < cx < x1 - 0.05 and y0 + 0.05 < cy < y1 - 0.05:
                ax.text(cx, cy, nm, fontsize=6.5, color=GREY, ha="center", va="center", style="italic", zorder=1)
    style = {"mine": ("^", ACCENT, 150), "hq": ("s", NAVY, 90), "plant": ("D", "#6b4fa0", 80), "market": ("o", GREEN, 70), "project": ("*", GOLD, 220), "rival": ("D", "#6b4fa0", 80)}
    seen = set()
    for r in csv.DictReader(open(a.points, encoding="utf-8")):
        k = (r.get("kind") or "market").strip()
        m, c, s = style.get(k, style["market"])
        lon, lat = float(r["lon"]), float(r["lat"])
        ax.scatter([lon], [lat], marker=m, c=c, s=s, edgecolors="white", linewidths=1.0, zorder=5)
        dx, dy = float(r.get("dx") or 0.04), float(r.get("dy") or 0.04)
        ax.annotate(nfc(r["name"]), (lon, lat), (lon + dx, lat + dy), fontsize=8, weight="bold", color=NAVY, zorder=6,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6) if abs(dx) > 0.12 or abs(dy) > 0.12 else None)
        seen.add(k)
    names = {"mine": "Mỏ khai thác", "hq": "Trụ sở", "plant": "Trụ sở MBV (không hợp nhất)", "market": "Trung tâm kinh tế / thị trường chính", "project": "Dự án hạ tầng", "rival": "Mỏ / cơ sở cạnh tranh"}
    hs = [plt.Line2D([], [], marker=style[k][0], color="w", markerfacecolor=style[k][1], markersize=9, label=names[k]) for k in style if k in seen]
    ax.legend(handles=hs, loc="lower left", fontsize=7.5, frameon=True, framealpha=0.95, edgecolor="#dfe3e8")
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / math.cos(math.radians((y0 + y1) / 2)))
    ax.axis("off")
    if a.title:
        fig.text(0.02, 1 - 0.18 / (Hm + 0.8), a.title, fontsize=11, weight="bold", color=NAVY, ha="left", va="center")
    fig.text(0.02, 0.22 / (Hm + 0.8), a.source, fontsize=6, color=GREY, ha="left", va="center")
    fig.savefig(a.out, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
