#!/usr/bin/env python3
"""
value_radar_chart.py — concentric ring gauge cho Value Radar (section 4.2 báo cáo tuần)
==========================================================================================
Vẽ 4 vòng concentric (P/E, P/B, Spread E/P, Composite) từ value_radar.value_radar_now().
Display-only, giống hệt ranh giới của value_radar.py chính nó — KHÔNG phải tín hiệu mua/bán.
"""
import argparse
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

CHEAP_MAX = 33
EXPENSIVE_MIN = 67
COLOR_CHEAP = "#16a34a"
COLOR_FAIR = "#d97706"
COLOR_EXPENSIVE = "#dc2626"
COLOR_TRACK = "#e5e7eb"

_LABEL_VN = {"CHEAP": "RẺ", "FAIR": "TRUNG TÍNH", "EXPENSIVE": "ĐẮT"}

RINGS = [
    ("p_pe", "P/E", 0.21, 0.05),
    ("p_pb", "P/B", 0.285, 0.05),
    ("p_sp", "Spread E/P", 0.36, 0.05),
    ("score", "Composite", 0.45, 0.065),
]


def _color_for(pct):
    if pct < CHEAP_MAX:
        return COLOR_CHEAP
    if pct > EXPENSIVE_MIN:
        return COLOR_EXPENSIVE
    return COLOR_FAIR


def _label_for(pct):
    if pct < CHEAP_MAX:
        return "RẺ"
    if pct > EXPENSIVE_MIN:
        return "ĐẮT"
    return "TRUNG TÍNH"


def _placeholder_data():
    return dict(
        score=50.0, label="FAIR",
        pe_cap10=float("nan"), p_pe=50.0,
        pb_cap10=float("nan"), p_pb=50.0,
        spread=float("nan"), p_sp=50.0,
        asof="n/a (placeholder — value_radar_now() lỗi)",
    )


def build_chart(data, out_path):
    fig = plt.figure(figsize=(8, 4.5))
    ax = fig.add_axes([0.02, 0.05, 0.55, 0.9])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    center = (0.5, 0.5)
    for key, name, r_outer, width in RINGS:
        pct = max(0.0, min(100.0, float(data.get(key, 0.0))))
        color = _color_for(pct)
        # track nền (full circle)
        ax.add_patch(mpatches.Wedge(center, r_outer, 0, 360, width=width,
                                     facecolor=COLOR_TRACK, edgecolor="none"))
        # arc giá trị, bắt đầu từ 90° (top), quét theo pct
        theta1 = 90.0
        theta2 = 90.0 + pct / 100.0 * 360.0
        ax.add_patch(mpatches.Wedge(center, r_outer, theta1, theta2, width=width,
                                     facecolor=color, edgecolor="none"))

    score = float(data.get("score", float("nan")))
    label_vn = _LABEL_VN.get(data.get("label"), data.get("label", "?"))
    ax.text(0.5, 0.53, f"{score:.0f}", ha="center", va="center",
            fontsize=26, fontweight="bold", color="#111827")
    ax.text(0.5, 0.42, label_vn, ha="center", va="center",
            fontsize=13, fontweight="bold", color=_color_for(score))

    # legend bên phải
    lax = fig.add_axes([0.60, 0.05, 0.38, 0.9])
    lax.axis("off")
    lines = [
        ("Composite", f"p{data.get('score', float('nan')):.0f} — {label_vn}", _color_for(data.get("score", 50))),
        ("P/E cap-10", f"{data.get('pe_cap10', float('nan')):.2f}  (p{data.get('p_pe', float('nan')):.0f})", _color_for(data.get("p_pe", 50))),
        ("P/B cap-10", f"{data.get('pb_cap10', float('nan')):.2f}  (p{data.get('p_pb', float('nan')):.0f})", _color_for(data.get("p_pb", 50))),
        ("Spread EY−tiết kiệm", f"{data.get('spread', float('nan')):+.2f}pp  (p{data.get('p_sp', float('nan')):.0f})", _color_for(data.get("p_sp", 50))),
    ]
    y = 0.90
    for name, val, color in lines:
        lax.add_patch(mpatches.Rectangle((0.0, y - 0.02), 0.05, 0.05,
                                          facecolor=color, edgecolor="none", transform=lax.transAxes))
        lax.text(0.10, y, name, transform=lax.transAxes, fontsize=10.5,
                 fontweight="bold", va="center")
        lax.text(0.10, y - 0.07, val, transform=lax.transAxes, fontsize=10, va="center", color="#374151")
        y -= 0.22

    lax.text(0.0, 0.06, f"as-of {data.get('asof', '?')}", transform=lax.transAxes,
              fontsize=8, color="#6b7280")
    lax.text(0.0, 0.0, "display-only, không dùng làm tín hiệu mua/bán",
              transform=lax.transAxes, fontsize=8, color="#6b7280", style="italic")

    fig.savefig(out_path, dpi=150, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/value_radar_chart.png")
    args = ap.parse_args()

    try:
        from value_radar import value_radar_now
        data = value_radar_now()
        if data is None:
            raise RuntimeError("value_radar_now() trả None (fail-safe path)")
    except Exception as e:
        print(f"[value_radar_chart] WARNING: value_radar_now() lỗi ({e}), dùng placeholder", file=sys.stderr)
        data = _placeholder_data()

    build_chart(data, args.out)
    print(args.out)


if __name__ == "__main__":
    main()
