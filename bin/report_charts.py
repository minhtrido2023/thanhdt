#!/usr/bin/env python3
"""Sinh 3 biểu đồ PNG chuẩn cho MỘT báo cáo weekly/monthly per-account:
  (a) NAV theo thời gian trong kỳ
  (b) Lợi nhuận lũy kế (indexed=100 đầu kỳ) so với VN-Index — MỘT trục duy nhất
  (c) Phân bổ danh mục cuối kỳ theo mã (bar ngang, tối đa ~9 hạng mục, dồn phần còn lại vào "Khác")

Chỉ vẽ — KHÔNG tự lấy dữ liệu (không đọc BQ/DNSE, không đọc data/VNINDEX.csv vì file đó dừng ở
2026-05-26, đã lỗi thời cho báo cáo tháng 8 trở đi). Người gọi (script soạn báo cáo) phải truyền
chuỗi ngày/NAV/VNINDEX đã qua đúng pipeline verify (coding_guidelines §6) qua tham số --series;
script này không chịu trách nhiệm về tính đúng của số liệu đầu vào, chỉ về cách vẽ.

Output: PNG tĩnh (matplotlib Agg) — kênh giao là email HTML (nhúng qua đường dẫn tương đối, xem
render_report_html.py::image_html) + Discord text (không đính kèm được, xem notify_thread.sh).
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PORTFOLIO_COLOR = "#1f6f5c"   # 1 màu chính, dùng xuyên suốt mọi báo cáo cho đường NAV/lợi nhuận
BENCHMARK_COLOR = "#9aa0a6"   # VN-Index — trung tính, không lấn át đường chính
GRID_COLOR = "#e5e7eb"
PALETTE = ["#1f6f5c", "#3f8f7a", "#6aab8f", "#9dc7ad", "#c7ddc9",
           "#f2c14e", "#e07a5f", "#8d99ae", "#495057"]
CASH_COLOR = "#c9ccd1"
LEGACY_COLOR = "#b23a48"


def _strip_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def chart_nav(dates, navs, account, title_suffix, out_path):
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    ax.plot(dates, navs, color=PORTFOLIO_COLOR, linewidth=2.2, marker="o", markersize=4)
    ax.set_title(f"NAV tài khoản {account} — {title_suffix}", fontsize=13, fontweight="bold")
    ax.set_ylabel("NAV (VND)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:,.0f} triệu"))
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    _strip_axes(ax)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def chart_cum_return(dates, navs, vnindex, account, title_suffix, out_path):
    nav0, vni0 = navs[0], vnindex[0]
    nav_idx = [v / nav0 * 100 for v in navs]
    vni_idx = [v / vni0 * 100 for v in vnindex]
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    ax.plot(dates, nav_idx, color=PORTFOLIO_COLOR, linewidth=2.2, marker="o", markersize=4,
            label=account)
    ax.plot(dates, vni_idx, color=BENCHMARK_COLOR, linewidth=2.0, linestyle="--",
            marker="o", markersize=3, label="VN-Index")
    ax.axhline(100, color=GRID_COLOR, linewidth=1)
    ax.set_title(f"Lợi nhuận lũy kế {account} so với VN-Index — {title_suffix}\n"
                 f"(chỉ số hóa = 100 tại đầu kỳ)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Chỉ số (đầu kỳ = 100)")
    ax.legend(frameon=False, loc="best")
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    _strip_axes(ax)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def chart_allocation(items, account, title_suffix, out_path):
    """items: list [[label, pct], ...] đã sắp theo thứ tự muốn hiển thị TRÊN xuống DƯỚI."""
    labels = [it[0] for it in items]
    vals = [it[1] for it in items]
    colors = []
    for lb in labels:
        if "legacy" in lb.lower() or "dgc" in lb.lower():
            colors.append(LEGACY_COLOR)
        elif "tiền mặt" in lb.lower() or "trứng vàng" in lb.lower():
            colors.append(CASH_COLOR)
        else:
            colors.append(PALETTE[len(colors) % len(PALETTE)])
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    y = list(range(len(labels)))[::-1]
    ax.barh(y, vals, color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("% NAV")
    ax.set_title(f"Phân bổ danh mục cuối kỳ — {account} ({title_suffix})",
                 fontsize=12, fontweight="bold")
    for yi, v in zip(y, vals):
        ax.text(v + max(vals) * 0.01, yi, f"{v:.1f}%", va="center", fontsize=9)
    ax.set_xlim(0, max(vals) * 1.15)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
    _strip_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True, choices=["SpaceX", "ZaloPay"])
    ap.add_argument("--label", required=True,
                     help="hậu tố tên file, vd monthly_2026-08 hoặc weekly_2026-08-24_to_2026-08-28")
    ap.add_argument("--title-suffix", required=True, help="vd 'Tháng 08/2026' hoặc '24-28/08/2026'")
    ap.add_argument("--dates", required=True, help='JSON list ["2026-07-31", ...] tăng dần')
    ap.add_argument("--nav", required=True, help="JSON list NAV VND cùng độ dài --dates")
    ap.add_argument("--vnindex", required=True, help="JSON list VNINDEX close cùng độ dài --dates")
    ap.add_argument("--allocation", required=True,
                     help='JSON list [["SIP", 8.5], ...] đã sắp xếp, tối đa ~9 dòng')
    ap.add_argument("--out-dir",
                     default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                           "reports", "assets"))
    args = ap.parse_args()

    dates = json.loads(args.dates)
    navs = json.loads(args.nav)
    vni = json.loads(args.vnindex)
    alloc = json.loads(args.allocation)
    assert len(dates) == len(navs) == len(vni), "dates/nav/vnindex phải cùng độ dài"

    os.makedirs(args.out_dir, exist_ok=True)
    p1 = os.path.join(args.out_dir, f"{args.account}_{args.label}_nav.png")
    p2 = os.path.join(args.out_dir, f"{args.account}_{args.label}_cumret.png")
    p3 = os.path.join(args.out_dir, f"{args.account}_{args.label}_allocation.png")

    chart_nav(dates, navs, args.account, args.title_suffix, p1)
    chart_cum_return(dates, navs, vni, args.account, args.title_suffix, p2)
    chart_allocation(alloc, args.account, args.title_suffix, p3)

    for p in (p1, p2, p3):
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
