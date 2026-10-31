"""Mock báo cáo NGÀY v2 — SpaceX 30/10/2026, đúng 1 trang A4.

Số NAV/tỷ suất: nav_history + nav_period_returns. Bảng nhóm/vị thế, lệnh, quyền cổ đông, cờ theo dõi:
đọc từ đầu ra của eod_trading_report.sh ngày 30/10 (reports/SpaceX_daily_report_2026-10-30.md) — khi
gắn pipeline, các khối này lấy trực tiếp từ biến nguồn của eod (xem REPORT_STYLE_V2.md § Điểm gắn).
  source /home/trido/thanhdt/WorkingClaude/wc_env.sh && python3 mock_daily.py
"""
import csv
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_report_v2 as R  # noqa: E402
import data_sources as S  # noqa: E402
from build_report_v2 import b, bullets, footnote, img, kpi_tiles, mil, pct, section, table, vn  # noqa: E402

FIG, OUT, REC = (os.path.join(HERE, d) for d in ("figs", "out", "recon"))
ORIG = f"{S.MIKE}/reports/SpaceX_daily_report_2026-10-30.md"
A = "SpaceX"
GROUP = {"PARK custom30V": "Tạm giữ (rổ giá trị)", "LAG": "Sau công bố lợi nhuận", "Discretionary": "Chọn lọc cơ bản"}


def parse_eod(md):
    """Khối nhóm/vị thế từ báo cáo eod 30/10 (đơn vị M = triệu, như bản gốc)."""
    sleeves = {}
    for m in re.finditer(r"^\| (PARK custom30V|LAG|Discretionary) \((\d) mã\) \| ([\d.]+)M \| ([\d.]+)% \| (≈?[-+][\d.]+)%", md, re.M):
        sleeves[m.group(1)] = (float(m.group(3)), float(m.group(4)), m.group(5))
    pos = []
    for g in GROUP:
        blk = re.search(rf"\*\*Chi tiết {re.escape(g)} \(\d mã\)\*\*\n(.*)\n", md).group(1)
        for m in re.finditer(r"([A-Z0-9]{3}) ([\d.]+)M, ([-+][\d.]+)%(?: — phần ([\d,]+)cp)?", blk):
            pos.append((g, m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)))
    ca = re.findall(r"^\| ([A-Z]{3}) \| AIS \| (\d{4}-\d\d-\d\d) \| [A-Z]{3} - Niêm yết bổ sung ([\d.]+) cổ phiếu \|", md, re.M)
    return sleeves, pos, ca


def main():
    md = open(ORIG, encoding="utf-8").read()
    sleeves, pos, ca = parse_eod(md)
    P = S.periods(A, "2026-10-30")
    day, inc, mtd = P["day"], P["inception"], P["mtd"]
    vnd = S.vni_close()
    nh = S.nav_history(A)
    e = {k: float(nh["2026-10-30"][k]) for k in ("nav", "mtm_stock", "cash", "egg_assets", "margin_debt")}
    nav = e["nav"]
    calc, _ = S.weekly_artifacts()
    trades = [x for x in calc[A]["trades"] if x[0] == "2026-10-30"]
    assert len(trades) == 1 and trades[0][2] == "SCL" and trades[0][1] == "S"
    tr = trades[0]

    # chart 1: tháng 10 cơ sở 100 tại 30/09 (khớp MTD)
    L = [x for x in S.unit_ledger(A) if x[0] >= dt.date(2026, 9, 30)]
    ds = [x[0] for x in L]
    port = [x[1] / L[0][1] * 100 for x in L]
    v0 = vnd[dt.date(2026, 9, 30)][0]
    bench = [S.vni_on_or_before(vnd, d)[0] / v0 * 100 for d in ds]
    f1 = R.chart_index_vs_bench(ds, port, bench,
                                f"Tháng 10: danh mục {pct(mtd['return_pct'])}, VN-Index {pct(mtd['benchmark']['vnindex_price_pct'])}",
                                os.path.join(FIG, "d_01_mtd.png"),
                                "Cơ sở 100 = 30/09/2026; danh mục đã loại dòng tiền ngoại sinh. Nguồn: CTCK lưu ký, HOSE.",
                                size=(4.6, 2.7))
    # chart 2: phân bổ theo nhóm (% NAV)
    items = [(GROUP[g], sleeves[g][0] * 1e6) for g in GROUP] + [("Trứng vàng", e["egg_assets"]), ("Tiền mặt", e["cash"])]
    plt = R.setup_mpl()
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    cols = [R.S1, R.S1, R.S1, R.S2, R.S3]
    alphas = [1, 0.75, 0.5, 1, 1]
    y = list(range(len(items)))[::-1]
    for yi, (lab, v), c, a in zip(y, items, cols, alphas):
        ax.barh(yi, v / nav * 100, color=c, alpha=a, height=0.6)
        ax.text(v / nav * 100 + 1, yi, f"{vn(v / nav * 100, 1)}%", va="center", fontsize=7.8)
    ax.set_yticks(y, [x[0] for x in items]); ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.set_xlim(0, 95); ax.set_xlabel("% NAV")
    ax.set_title(f"Cổ phiếu {vn(e['mtm_stock'] / nav * 100, 1)}% NAV; Trứng vàng {vn(e['egg_assets'] / nav * 100, 1)}%")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    f2 = R._save(fig, os.path.join(FIG, "d_02_groups.png"),
                 "Nhóm cổ phiếu theo giá CTCK cuối ngày; Trứng vàng, tiền mặt theo NAV chốt ngày.",
                 [(k, v, round(v / nav * 100, 3)) for k, v in items], ["nhom", "vnd", "pct_nav"])
    R.side_by_side([f1, f2], os.path.join(FIG, "d_12_pair.png"))

    title = (f"30/10: NAV {pct(day['return_pct'])} so với VN-Index {pct(day['benchmark']['vnindex_price_pct'])}; "
             f"bán nốt {vn(tr[3])} cp SCL, khớp đủ")
    ban = R.banner(title, "Báo cáo ngày · Tài khoản SpaceX · Chiến lược V2.4", "Phiên 30/10/2026", os.path.join(FIG, "d_00_banner.png"), mono="SpaceX")
    kp = kpi_tiles([
        ("NAV 30/10", mil(nav), f"{vn(day['nav1'] - day['nav0'], 0, True)} VND trong ngày", None),
        ("Trong ngày", pct(day["return_pct"]), f"VN-Index {pct(day['benchmark']['vnindex_price_pct'])}", R.tone(day["return_pct"])),
        ("Từ đầu tháng", pct(mtd["return_pct"]), f"VN-Index {pct(mtd['benchmark']['vnindex_price_pct'])}", R.tone(mtd["return_pct"])),
        ("Từ khi bắt đầu", pct(inc["return_pct"]), f"lãi/lỗ {mil(inc['pnl_vnd'])}", R.tone(inc["return_pct"])),
        ("Trạng thái thị trường", "Trung tính", "ổn định, không có tín hiệu tích luỹ", None),
        ("Định giá tổng hợp", "14,4 — RẺ", "P/E 10,68 (p3) · P/B 1,78 (p12)", None),
    ], per_row=6)
    rows = []
    for g, tk, v, r, part in pos:
        rows.append([tk + (f" ({part.replace(',', '.')} cp)" if part else ""), GROUP[g], vn(v, 1), pct(r)])
    hold = table(["Mã", "Nhóm", "Giá trị (tr)", "Lãi/lỗ"], rows, align=["l", "l", "r", "r"], color_cols=(3,))
    ev = table(["Sự kiện 7 ngày tới", "Ngày", "Nội dung"],
               [[f"{t} — niêm yết bổ sung", f"{d[8:10]}/{d[5:7]}", f"{vn(int(n.replace('.', '')))} cp"] for t, d, n in ca],
               align=["l", "l", "r"], widths=[40, 20, 40])
    blocks = [img(ban), kp, img(os.path.join(FIG, "d_12_pair.png")),
              section(f"Giao dịch: 1 lệnh bán SCL {vn(tr[3])} cp × {vn(tr[4] / tr[3])} = {vn(tr[4])} VND, khớp đủ 100% kế hoạch"),
              hold,
              footnote("Lãi/lỗ trên giá vốn, giá đóng cửa, đã cộng cổ tức tiền mặt sau thuế. VPB nằm ở 2 nhóm: tỷ suất là của toàn mã."),
              ev,
              section("Cần theo dõi"),
              bullets([
                  "DRI, TV1 (nhóm chọn lọc): đã nắm 55 phiên từ 11/08, đến kỳ xem xét thoát vị thế.",
                  "4 mã đang trong cửa sổ chờ mua theo chiến lược sau công bố lợi nhuận; chưa đặt lệnh.",
                  "Rổ tạm giữ chốt 05/08; kỳ cân bằng kế tiếp ước tính khoảng 01/12.",
              ]),
              footnote(f"Đối soát: khớp lệnh trong ngày khớp đúng với CTCK; sao kê CTCK chưa có lúc lập (gửi khoảng 16:30). NAV = cổ phiếu {vn(e['mtm_stock'])} + tiền mặt {vn(e['cash'])} + Trứng vàng {vn(e['egg_assets'])} − nợ ký quỹ {vn(e['margin_debt'])}."),
              ]
    pdf = os.path.join(OUT, "SpaceX_daily_2026-10-30_v2.pdf")
    n = R.build_pdf(blocks, pdf, header_left="Tài khoản SpaceX · Báo cáo ngày 30/10/2026", header_right="Phiên 30/10/2026",
                    footer="Không phải khuyến nghị đầu tư. Kết quả quá khứ không bảo đảm kết quả tương lai.", archive_dirs=(FIG,))
    R.build_email_html(blocks[1:], ban, title, os.path.join(OUT, "SpaceX_daily_2026-10-30_v2_email.html"))

    # đối chiếu
    recon = [("NAV 30/10", vn(nav), "945,141,046", "945.141.046"),
             ("Thay đổi NAV trong ngày", vn(day["nav1"] - day["nav0"]), "-700,678", "−700.678"),
             ("Trong ngày %", pct(day["return_pct"]), "-0.07%", "−0,07%"),
             ("Lãi/lỗ từ go-live", vn(inc["pnl_vnd"]), "-36,835,465", "−36.835.465"),
             ("Từ go-live %", pct(inc["return_pct"]), "-3.69%", "−3,69%"),
             ("Cổ phiếu", vn(e["mtm_stock"]), "165,674,300", "165.674.300"),
             ("Tiền mặt", vn(e["cash"]), "30,122,995", "30.122.995"),
             ("Trứng vàng", vn(e["egg_assets"]), "749,343,751", "749.343.751"),
             ("Giá trị lệnh bán (M)", vn(tr[4] / 1e6, 1), "9.0M", "9,0")]
    for g, tk, v, r, part in pos:
        recon.append((f"{tk} {g}", f"{vn(v, 1)} / {pct(r)}", f"{tk} {v}M, {r:+.2f}%".replace("+-", "-"), f"{vn(v, 1)} / {pct(r)}"))
    for g, (v, w, r) in sleeves.items():
        recon.append((f"Nhóm {g}", vn(v, 1), f"{v}M", vn(v, 1)))
    out, bad = [], 0
    for lab, m, o_raw, o_fmt in recon:
        found = o_raw in md
        ok = (m == o_fmt) and found
        bad += not ok
        out.append((lab, m, o_raw, "0" if m == o_fmt else "KHÁC", "có" if found else "KHÔNG THẤY"))
    with open(os.path.join(REC, "daily_recon.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["chi_tieu", "mock", "bao_cao_goc", "sai_lech", "co_trong_ban_goc"]); w.writerows(out)
    meta = {"pages": n, "recon_items": len(out), "recon_bad": bad, "title": title,
            "prose_body": R.prose_words(blocks), "pdf_words": len(" ".join(R.pdf_text(pdf)).split())}
    json.dump(meta, open(os.path.join(REC, "daily_meta.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False))
    for r in out:
        if r[3] != "0" or r[4] != "có":
            print("LỆCH:", r)
    if bad or n != 1:
        sys.exit(2)


if __name__ == "__main__":
    main()
