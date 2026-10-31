"""Mock báo cáo QUÝ v2 — SpaceX Quý 3/2026 (01/07–30/09, quý đầu tiên).

Chỉ dựng từ nav_history_SpaceX.csv + nav_period_returns (tỷ suất kỳ, giá đơn vị). Thống kê rủi ro
(độ biến động, sụt giảm, tỷ lệ phiên tăng) là thống kê MÔ TẢ trên chuỗi giá đơn vị đó. Mục không có
nguồn pipeline (attribution theo mã/ngành, tỷ suất từng vị thế cuối quý, chi phí, triển vọng) ghi
"không có" — không tự tính.
  source /home/trido/thanhdt/WorkingClaude/wc_env.sh && python3 mock_quarterly.py
"""
import csv
import datetime as dt
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_report_v2 as R  # noqa: E402
import data_sources as S  # noqa: E402
from build_report_v2 import b, bullets, footnote, img, kpi_tiles, mil, pct, section, table, vn  # noqa: E402

FIG, OUT, REC = (os.path.join(HERE, d) for d in ("figs", "out", "recon"))
A, Q0, Q1 = "SpaceX", dt.date(2026, 6, 30), dt.date(2026, 9, 30)
MONTH_ENDS = [("Tháng 7", "2026-07-31"), ("Tháng 8", "2026-08-31"), ("Tháng 9", "2026-09-30")]
ORIG_MONTHLY = f"{S.MIKE}/reports/SpaceX_monthly_report_2026-09.md"


def stats(series):
    """series=[(date, level)] → độ lệch chuẩn ngày %, quy năm %, MDD %, ngày đáy, số phiên tăng/tổng."""
    r = [series[i][1] / series[i - 1][1] - 1 for i in range(1, len(series))]
    pk, mdd, dday = series[0][1], 0.0, None
    for d, v in series:
        pk = max(pk, v)
        if v / pk - 1 < mdd:
            mdd, dday = v / pk - 1, d
    sd = st.stdev(r) * 100
    return {"sd": sd, "ann": sd * 252 ** 0.5, "mdd": mdd * 100, "mdd_date": dday,
            "up": sum(x > 0 for x in r), "n": len(r)}


def main():
    P = S.periods(A, "2026-09-30")
    q = P["inception"]
    assert q["from_date"] == "2026-07-01" and q["to_date"] == "2026-09-30"
    vnd = S.vni_close()
    bq = q["benchmark"]
    ex_q = S.excess_pp(q, vnd)
    months = []
    for lab, d in MONTH_ENDS:
        m = S.periods(A, d)["mtd"]
        months.append((lab, m["return_pct"], m["benchmark"]["vnindex_price_pct"], S.excess_pp(m, vnd), m))

    L = [x for x in S.unit_ledger(A) if x[0] <= Q1]
    # mốc khởi điểm 01/07 = vốn gốc trước phiên đầu tiên; VN-Index cùng mốc = đóng cửa 30/06
    pser = [(d, u) for d, u, _ in L]
    vdates = sorted(d for d in vnd if Q0 <= d <= Q1)
    vser = [(d, vnd[d][0]) for d in vdates]
    ps, vs = stats(pser), stats(vser)
    ps_sep = stats([x for x in pser if x[0] >= dt.date(2026, 8, 31)])
    nh = S.nav_history(A)
    nav30 = float(nh["2026-09-30"]["nav"])
    st_w = [(dt.date.fromisoformat(d), float(r["mtm_stock"]) / float(r["nav"]) * 100) for d, r in sorted(nh.items()) if d <= "2026-09-30"]
    below = next(d for d, v in st_w if v < 100)

    # ─── biểu đồ ───
    ds = [d for d, _ in pser]
    port = [u / pser[0][1] * 100 for _, u in pser]
    bench = [100.0] + [S.vni_on_or_before(vnd, d)[0] / vnd[Q0][0] * 100 for d in ds[1:]]
    f1 = R.chart_index_vs_bench(ds, port, bench,
                                f"Quý 3: danh mục {pct(q['return_pct'])} so với VN-Index {pct(bq['vnindex_price_pct'])}",
                                os.path.join(FIG, "q_01_nav_vs_vni.png"),
                                "Giá đơn vị đã loại dòng tiền ngoại sinh; cơ sở 100 = vốn 1 tỷ VND (01/07) và VN-Index 30/06/2026 (1.860,01). Nguồn: CTCK lưu ký, HOSE.",
                                size=(7.6, 2.9))
    assert months[0][3] > 0 and months[1][3] < 0 < months[1][2] and months[2][3] > 0, "tiêu đề heatmap không còn đúng"
    assert months[2][3] > 0.9 * ex_q, "tiêu đề 'chủ yếu nhờ tháng 9' không còn đúng"
    f2 = R.chart_month_grid([m[0] for m in months], [m[1] for m in months], [m[2] for m in months],
                            "Hơn chỉ số ở tháng 7 và tháng 9, kém ở tháng 8 khi thị trường tăng",
                            os.path.join(FIG, "q_02_months.png"), "Tỷ suất tháng đã loại dòng tiền ngoại sinh; VN-Index giá. Màu: xanh dương = dương, đỏ = âm.")
    pk, dd = 0, []
    for _, u in pser:
        pk = max(pk, u); dd.append((u / pk - 1) * 100)
    vpk, vdd = 0, []
    for d in ds:
        v = S.vni_on_or_before(vnd, d)[0] if d > ds[0] else vnd[Q0][0]
        vpk = max(vpk, v); vdd.append((v / vpk - 1) * 100)
    f3 = R.chart_underwater(ds, dd, f"Sụt giảm sâu nhất {pct(ps['mdd'], 2, False)} ({ps['mdd_date']:%d/%m}), nông hơn VN-Index {pct(vs['mdd'], 2, False)}",
                            os.path.join(FIG, "q_03_underwater.png"), "Từ đỉnh gần nhất; danh mục theo giá đơn vị, VN-Index theo đóng cửa.",
                            bench=vdd, size=(7.6, 2.4))
    f4 = R.chart_line([d for d, _ in st_w], [v for _, v in st_w],
                      f"Cổ phiếu từ {vn(st_w[0][1], 0)}% NAV (dùng ký quỹ) đầu quý xuống {vn(st_w[-1][1], 1)}% cuối quý",
                      os.path.join(FIG, "q_04_equity_weight.png"), "Giá trị cổ phiếu / NAV theo sổ, chốt cuối ngày. Trên 100% = có dư nợ ký quỹ.",
                      unit="% NAV", ref=100, ref_label="100% NAV", size=(7.6, 2.4), fmt_last=lambda v: vn(v, 1) + "%")

    title = (f"Quý 3/2026: danh mục {pct(q['return_pct'])} so với VN-Index {pct(bq['vnindex_price_pct'])}, "
             f"hơn chỉ số {vn(ex_q, 2)} điểm % với sụt giảm nông hơn")
    ban = R.banner(title, "Báo cáo quý · Tài khoản SpaceX · Chiến lược V2.4", "Quý 3/2026 (01/07 – 30/09), quý hoạt động đầu tiên",
                   os.path.join(FIG, "q_00_banner.png"), mono="SpaceX")
    best = max(months, key=lambda m: m[1]); worst = min(months, key=lambda m: m[1])
    kp = kpi_tiles([
        ("NAV 30/09", mil(nav30), "vốn khởi điểm 1.000,00 tr", None),
        ("Quý 3 (đã loại dòng tiền)", pct(q["return_pct"]), f"VN-Index {pct(bq['vnindex_price_pct'])}", R.tone(q["return_pct"])),
        ("So với VN-Index", vn(ex_q, 2, True) + " điểm %", f"có cổ tức: {pct(bq['vnindex_tr_net_pct'])}", R.tone(ex_q)),
        ("Sụt giảm tối đa", pct(ps["mdd"], 2, False), f"VN-Index {pct(vs['mdd'], 2, False)}", None),
        ("Biến động quy năm", vn(ps["ann"], 1) + "%", f"VN-Index {vn(vs['ann'], 1)}%", None),
        ("Phiên tăng", f"{ps['up']}/{ps['n']}", f"VN-Index {vs['up']}/{vs['n']}", None),
        ("Tháng tốt / xấu nhất", f"{pct(best[1])} / {pct(worst[1])}", f"{best[0]} / {worst[0]}", None),
        ("Cổ phiếu / NAV 30/09", vn(st_w[-1][1], 1) + "%", f"02/07: {vn(st_w[0][1], 1)}%", None),
    ])
    know = bullets([
        f"{b('Hiệu suất')}: quý {pct(q['return_pct'])} so với {pct(bq['vnindex_price_pct'])}; phần lớn khoảng cách đến từ tháng 9 ({vn(months[2][3], 2, True)} điểm %).",
        f"{b('Rủi ro')}: sụt giảm tối đa {pct(ps['mdd'], 2, False)} so với {pct(vs['mdd'], 2, False)} của chỉ số; biến động {vn(ps['ann'], 1)}%/năm so với {vn(vs['ann'], 1)}%.",
        f"{b('Phân bổ')}: cổ phiếu giảm từ {vn(st_w[0][1], 0)}% NAV (có ký quỹ) xuống {vn(st_w[-1][1], 1)}% cuối quý.",
    ])
    mrows = [[m[0], pct(m[1]), pct(m[2]), vn(m[3], 2, True)] for m in months]
    mrows.append(["Quý 3/2026", pct(q["return_pct"]), pct(bq["vnindex_price_pct"]), vn(ex_q, 2, True)])
    risk = table(["Chỉ số (01/07–30/09)", "Danh mục", "VN-Index"], [
        ["Độ lệch chuẩn lợi suất ngày", vn(ps["sd"], 2) + "%", vn(vs["sd"], 2) + "%"],
        ["Biến động quy năm (×căn 252)", vn(ps["ann"], 1) + "%", vn(vs["ann"], 1) + "%"],
        ["Sụt giảm tối đa từ đỉnh", f"{pct(ps['mdd'], 2, False)} ({ps['mdd_date']:%d/%m})", f"{pct(vs['mdd'], 2, False)} ({vs['mdd_date']:%d/%m})"],
        ["Số phiên tăng / tổng", f"{ps['up']}/{ps['n']}", f"{vs['up']}/{vs['n']}"],
    ], widths=[46, 27, 27])
    na = table(["Mục chuẩn của báo cáo quý", "Trạng thái trong mock"], [
        ["Đóng góp theo mã / theo ngành", "không có — chưa có pipeline attribution quý"],
        ["Danh mục cuối quý, tỷ suất từng vị thế", "không có — cần vị thế 30/09 đã đối soát cổ tức"],
        ["Chi phí (phí, thuế, lãi ký quỹ) cả quý", "không có — cần đối soát sao kê CTCK"],
        ["Triển vọng quý 4", "không có — mock không thêm nhận định mới"],
    ], align=["l", "l"])
    blocks = [img(ban), kp, img(f1), section("3 điều cần biết"), know,
              "PAGEBREAK",
              section(f"Theo tháng: hơn chỉ số {vn(ex_q, 2)} điểm % cả quý, chủ yếu nhờ tháng 9",
                      "Tỷ suất đã loại dòng tiền ngoại sinh; chênh theo chỉ số giá, điểm %."),
              img(f2),
              table(["Kỳ", "Danh mục", "VN-Index", "Chênh"], mrows, total_rows=1, color_cols=(1, 2, 3)),
              section(f"Rủi ro: biến động và sụt giảm đều thấp hơn chỉ số"),
              img(f3), risk,
              footnote("Thống kê mô tả trên chuỗi giá đơn vị đã loại dòng tiền; lịch sử 1 quý — chưa đủ dài để có ý nghĩa thống kê."),
              "PAGEBREAK",
              section(f"Phân bổ: cổ phiếu về dưới 100% NAV từ {below:%d/%m}, cuối quý {vn(st_w[-1][1], 1)}% NAV"),
              img(f4),
              section("Mục chưa có số liệu đối soát trong mock"), na,
              section("Phụ lục — phương pháp"),
              bullets([
                  "Tỷ suất kỳ = tỷ số giá đơn vị (vốn 1 tỷ VND ngày 01/07), đã loại dòng tiền ngoại sinh theo sổ dòng tiền.",
                  "VN-Index mốc 30/06/2026 = 1.860,01; bản có cổ tức tự tính từ cổ tức tiền mặt HOSE, sau thuế 5%.",
                  "NAV = cổ phiếu theo giá đóng cửa + tiền mặt + Trứng vàng − dư nợ ký quỹ, đối chiếu với CTCK lưu ký.",
                  "Không phải khuyến nghị đầu tư; kết quả quá khứ không bảo đảm kết quả tương lai.",
              ], max_items=None)]
    pdf = os.path.join(OUT, "SpaceX_quarterly_Q3_2026_v2.pdf")
    n = R.build_pdf(blocks, pdf, header_left="Tài khoản SpaceX · Báo cáo quý 3/2026", header_right="01/07 – 30/09/2026",
                    footer="Không phải khuyến nghị đầu tư. Kết quả quá khứ không bảo đảm kết quả tương lai.", archive_dirs=(FIG,))
    R.build_email_html(blocks[1:], ban, title, os.path.join(OUT, "SpaceX_quarterly_Q3_2026_v2_email.html"))

    # đối chiếu với báo cáo tháng 9 (đã gửi) — mục 2.2 + 4
    orig = open(ORIG_MONTHLY, encoding="utf-8").read()
    recon = [("NAV 30/09", vn(nav30), "981.599.301")]
    for lab, p_, b_, x_, _ in months:
        recon += [(f"{lab} danh mục", pct(p_), None), (f"{lab} VN-Index", pct(b_), None), (f"{lab} chênh", vn(x_, 2, True) + " điểm %", None)]
    recon += [("Quý 3 danh mục", pct(q["return_pct"]), None), ("Quý 3 VN-Index", pct(bq["vnindex_price_pct"]), None),
              ("Quý 3 chênh", vn(ex_q, 2, True) + " điểm %", None),
              ("Tháng 9 độ lệch chuẩn ngày (kiểm phương pháp)", vn(ps_sep["sd"], 3) + "%", "0,616%"),
              ("Cổ phiếu / NAV 30/09", vn(st_w[-1][1], 1) + "%", "64,2%")]
    rows, bad = [], 0
    for lab, m, o in recon:
        o = o or m
        found = o.lstrip("+") in orig
        bad += not ((m == o) and found)
        rows.append((lab, m, o, "0" if m == o else "KHÁC", "có" if found else "KHÔNG THẤY"))
    with open(os.path.join(REC, "quarterly_recon.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["chi_tieu", "mock", "bao_cao_thang9", "sai_lech", "co_trong_ban_goc"]); w.writerows(rows)
    meta = {"pages": n, "recon_items": len(rows), "recon_bad": bad, "title": title, "prose_body": R.prose_words(blocks, stop_at="Phụ lục —"),
            "pdf_words": len(" ".join(R.pdf_text(pdf)).split()), "port_stats": {k: str(v) for k, v in ps.items()}, "vni_stats": {k: str(v) for k, v in vs.items()}}
    json.dump(meta, open(os.path.join(REC, "quarterly_meta.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False))
    for r in rows:
        if r[3] != "0" or r[4] != "có":
            print("LỆCH:", r)


if __name__ == "__main__":
    main()
