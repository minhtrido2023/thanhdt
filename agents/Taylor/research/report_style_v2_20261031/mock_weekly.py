"""Mock báo cáo TUẦN v2 — SpaceX 26–30/10/2026. Chỉ trình bày lại số của báo cáo gốc.

  source /home/trido/thanhdt/WorkingClaude/wc_env.sh && python3 mock_weekly.py
Đầu ra: out/SpaceX_weekly_26-30_10_v2.{pdf,html} + figs/w_*.png/.csv + recon/weekly_recon.csv
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_report_v2 as R  # noqa: E402
import data_sources as S  # noqa: E402
from build_report_v2 import b, bullets, footnote, img, kpi_tiles, mil, pct, pp, section, table, vn  # noqa: E402

FIG, OUT, REC = (os.path.join(HERE, d) for d in ("figs", "out", "recon"))
for d in (FIG, OUT, REC):
    os.makedirs(d, exist_ok=True)
ORIG = f"{S.MIKE}/reports/SpaceX_weekly_report_2026-10-26_to_2026-10-30.md"
A, D0, D1 = "SpaceX", dt.date(2026, 10, 23), dt.date(2026, 10, 30)
SRC_ACC = "Nguồn: dữ liệu tài khoản tại công ty chứng khoán lưu ký (NAV chốt cuối ngày)"


def F(n):
    return os.path.join(FIG, n)


def main():
    P = S.periods(A, "2026-10-30")
    wk, mtd, inc = P["wtd"], P["mtd"], P["inception"]
    calc, tabs = S.weekly_artifacts()
    c, t = calc[A], tabs[A]
    nh = S.nav_history(A)
    e = {k: float(nh["2026-10-30"][k]) for k in ("nav", "mtm_stock", "cash", "egg_assets", "margin_debt")}
    s0 = {k: float(nh["2026-10-23"][k]) for k in ("nav", "mtm_stock", "cash", "egg_assets")}
    navE = e["nav"]
    w_st, w_cash, w_egg = (e[k] / navE * 100 for k in ("mtm_stock", "cash", "egg_assets"))
    w_st0 = s0["mtm_stock"] / s0["nav"] * 100
    nonst = 100 - round(w_st, 1)
    bw, bm, bi = (x["benchmark"] for x in (wk, mtd, inc))
    vnd = S.vni_close()
    ex_w, ex_m, ex_i = (S.excess_pp(x, vnd) for x in (wk, mtd, inc))
    risk = t["risk"]
    vnd = S.vni_close()
    lv = S.livermore_block("2026-10-30")
    fx = dict(lv["facts"])
    fc = lv["forecast"]

    # ─── chuỗi cho biểu đồ ───
    L = S.unit_ledger(A)
    dates = [d for d, _, _ in L]
    port = [u / L[0][1] * 100 for _, u, _ in L]
    anchor = vnd[dt.date(2026, 6, 30)][0]
    bench = [100.0] + [S.vni_on_or_before(vnd, d)[0] / anchor * 100 for d in dates[1:]]
    pk, dd = 0, []
    for _, u, _ in L:
        pk = max(pk, u); dd.append((u / pk - 1) * 100)
    bars, ind, br = S.tape(dt.date(2026, 4, 1), D1)
    bdates = sorted(d for d in br if d >= dt.date(2026, 7, 1))

    # ─── biểu đồ ───
    f_nav = R.chart_index_vs_bench(
        dates, port, bench,
        f"Từ 01/07: danh mục {pct(inc['return_pct'])} so với VN-Index {pct(bi['vnindex_price_pct'])}; tuần này {pct(wk['return_pct'])} so với {pct(bw['vnindex_price_pct'])}",
        F("w_01_nav_vs_vni.png"),
        f"{SRC_ACC}; giá đơn vị đã loại dòng tiền ngoại sinh (rút 18,02 tr ngày 29/10). VN-Index: HOSE, cơ sở 30/06/2026 = 1.860,01. Nền xám = tuần báo cáo.",
        shade=(D0, D1), size=(7.6, 2.85))
    items = sorted(c["attr"].items(), key=lambda kv: -kv[1])
    items = [(k, v) for k, v in items if round(v) != 0] + [
        ("Lãi tiền gửi", c["interest"]), ("Phí + thuế giao dịch", -(c["fee"] + c["tax"])),
        ("Thuế cổ tức TV1", -c["divtax"])]
    f_attr = R.chart_hbars(
        items, f"Tuần {mil(c['dnadj'])}: giá cổ phiếu {mil(c['price'])}, bù một phần bởi lãi tiền gửi {mil(c['interest'], 2)}",
        F("w_02_attribution.png"),
        "Đóng góp vào NAV, VND. Giá: đóng cửa 23/10 và 30/10 + giá khớp thực tế từng lệnh. Phí/thuế 29–30/10 theo biểu phí, chờ sao kê. Chi tiết: Phụ lục.",
        total=("Thay đổi do đầu tư", c["dnadj"]), size=(7.6, 3.3))
    f_alloc = R.chart_alloc(
        [("23/10", {"Cổ phiếu": s0["mtm_stock"], "Trứng vàng": s0["egg_assets"], "Tiền mặt": s0["cash"]}),
         ("30/10", {"Cổ phiếu": e["mtm_stock"], "Trứng vàng": e["egg_assets"], "Tiền mặt": e["cash"]})],
        f"Cổ phiếu tăng từ {vn(w_st0, 1)}% lên {vn(w_st, 1)}% NAV; {vn(nonst, 1)}% ở tiền gửi và tiền mặt",
        F("w_03_allocation.png"), f"% NAV theo sổ. {SRC_ACC}.", size=(7.6, 1.75))
    pnl = [(r[0], r[6]) for r in sorted(t["rows"], key=lambda r: -r[6])]
    f_pnl = R.chart_hbars(
        pnl, f"Lãi chưa thực hiện {mil(t['tot'][2], 2)} ({pct(t['tot'][3])}): {sum(r[6] > 0 for r in t['rows'])} mã lãi, {sum(r[6] < 0 for r in t['rows'])} mã lỗ",
        F("w_04_unrealized.png"),
        "% trên giá vốn thô, giá đóng cửa 30/10, đã cộng cổ tức tiền mặt đã đối soát (sau thuế 5%).",
        fmt=lambda v: pct(v), size=(4.6, 3.0), unit="%")
    f_dd = R.chart_underwater(dates, dd, f"Sụt giảm tối đa từ đỉnh {pct(risk['dd'], 2, False)} (27/07), chưa bị vượt",
                              F("w_05_underwater.png"), "Giá đơn vị đã loại dòng tiền ngoại sinh, 01/07–30/10/2026.",
                              size=(4.6, 3.0))
    R.side_by_side([f_pnl, f_dd], F("w_45_pair.png"))
    zones = [(float(fx["MA50 ngày 30/10/2026"].split(" ")[0].replace(".", "").replace(",", ".")), 1781.45, "Kháng cự 1.773–1.781", "res"),
             (1727.00, 1736.69, "Hỗ trợ 1.727–1.737", "sup"), (1677.19 - 3, 1677.19 + 3, "Đáy 20/10: 1.677", "sup")]
    f_tape = R.chart_tape(bars, ind, "VN-Index dưới MA50 và MA200, còn trên MA20",
                          F("w_06_vnindex.png"), "HOSE; MA và khối lượng: bảng ticker (VNINDEX). Vùng hỗ trợ/kháng cự theo khối phân tích kỹ thuật 30/10.",
                          zones=zones, size=(4.6, 3.0))
    f_br = R.chart_line_threshold(bdates, [br[d][0] for d in bdates], 40,
                                  f"Trên MA50: {vn(br[D1][0], 1)}% số mã (30/10), từ {vn(br[D0][0], 1)}%",
                                  F("w_07_breadth.png"), "% mã đóng cửa trên MA50, rổ đủ điều kiện theo từng thời điểm (≈340 mã).",
                                  thr_label="ngưỡng 40%", size=(4.6, 3.0))
    R.side_by_side([f_tape, f_br], F("w_67_pair.png"))

    # ─── nội dung ───
    title = (f"Tuần {pct(wk['return_pct'])} so với VN-Index {pct(bw['vnindex_price_pct'])}: hơn chỉ số "
             f"{vn(ex_w, 2)} điểm % khi {vn(nonst, 1)}% NAV nằm ở tiền gửi và tiền mặt")
    ban = R.banner(title, "Báo cáo tuần · Tài khoản SpaceX · Chiến lược V2.4", "Kỳ 26/10 – 30/10/2026 · Lập ngày 31/10/2026",
                   F("w_00_banner.png"), mono="SpaceX")
    kp = kpi_tiles([
        ("NAV 30/10", mil(navE), f"theo sổ; rút {mil(-c['flow'])} ngày 29/10", None),
        ("Tuần (đã loại dòng tiền)", pct(wk["return_pct"]), f"VN-Index {pct(bw['vnindex_price_pct'])}", R.tone(wk["return_pct"])),
        ("So với VN-Index, tuần", vn(ex_w, 2, True) + " điểm %", "chỉ số giá", R.tone(ex_w)),
        ("Từ đầu tháng 10", pct(mtd["return_pct"]), f"VN-Index {pct(bm['vnindex_price_pct'])}", R.tone(mtd["return_pct"])),
        ("Từ khi bắt đầu (01/07)", pct(inc["return_pct"]), f"VN-Index {pct(bi['vnindex_price_pct'])}", R.tone(inc["return_pct"])),
        ("Sụt giảm tối đa", pct(risk["dd"], 2, False), "từ đỉnh, đáy 27/07", None),
        ("Cổ phiếu / NAV", vn(w_st, 1) + "%", f"tuần trước {vn(w_st0, 1)}%", None),
        ("Tiền gửi + tiền mặt", vn(nonst, 1) + "%", f"Trứng vàng {vn(w_egg, 1)}% · tiền mặt {vn(w_cash, 1)}%", None),
    ])
    know = bullets([
        f"{b('Hiệu suất')}: tuần {pct(wk['return_pct'])} so với {pct(bw['vnindex_price_pct'])}; từ đầu tháng {pct(mtd['return_pct'])}, kém chỉ số {vn(-ex_m, 2)} điểm %.",
        f"{b('Danh mục')}: mua HT1, VPB, MCH; giảm 50% DRI; thoái toàn bộ SCL sau đánh giá lại cơ bản ({mil(-2950000)}).",
        f"{b('Thị trường')}: chỉ số {pct(bw['vnindex_price_pct'])} nhưng độ rộng trên MA50 tụt từ 46,5% xuống 29,8%; mô hình trạng thái giữ Trung tính.",
    ])
    page1 = [img(ban), kp, img(f_nav), img(f_alloc), section("3 điều cần biết"), know]

    # trang 2: hiệu suất + attribution
    perf = table(["Giai đoạn", "Danh mục", "VN-Index", "VN-Index có cổ tức", "Chênh (giá)"], [
        ["Tuần 23/10–30/10", pct(wk["return_pct"]), pct(bw["vnindex_price_pct"]), pct(bw["vnindex_tr_net_pct"]), vn(ex_w, 2, True)],
        ["Tháng 10 (30/09–30/10)", pct(mtd["return_pct"]), pct(bm["vnindex_price_pct"]), pct(bm["vnindex_tr_net_pct"]), vn(ex_m, 2, True)],
        ["Từ khi bắt đầu (01/07–30/10)", pct(inc["return_pct"]), pct(bi["vnindex_price_pct"]), pct(bi["vnindex_tr_net_pct"]), vn(ex_i, 2, True)],
    ], color_cols=(1, 2, 3, 4), widths=[34, 14, 14, 22, 16])
    drows = [["23/10", vn(s0["nav"]), "—", "—"]]
    for d, (nv, r, v) in t["daily"].items():
        drows.append([f"{d[8:10]}/10", vn(nv), pct(r), pct(v)])
    daily = table(["Ngày", "NAV theo sổ (VND)", "Danh mục, đã loại dòng tiền", "VN-Index"], drows, color_cols=(2, 3))
    page2 = ["PAGEBREAK",
             section(f"Hiệu suất: hơn chỉ số {vn(ex_w, 2)} điểm % trong tuần và {vn(ex_i, 2)} điểm % từ khi bắt đầu",
                     "Tỷ suất đã loại dòng tiền ngoại sinh; chênh tính theo chỉ số giá, đơn vị điểm %."),
             perf, daily,
             footnote(f"NAV 29/10 gồm khoản rút {vn(-c['flow'])} VND. Độ biến động ngày {vn(risk['vol'], 2)}% (≈{vn(risk['ann'], 1)}%/năm), {risk['n'] - 1} quan sát."),
             section(f"Đóng góp: {mil(c['price'])} từ giá cổ phiếu, {vn(c['interest'] - c['fee'] - c['tax'] - c['divtax'], 0, True)} VND thu nhập ngoài giá"),
             img(f_attr),
             footnote(f"Đẳng thức: {vn(c['price'])} + {vn(c['interest'])} − {vn(c['fee'] + c['tax'])} − {vn(c['divtax'])} = {vn(c['dnadj'])} VND (khớp NAV đã loại dòng tiền, chênh 0 đồng).")]

    # trang 3: danh mục + hoạt động
    hold = [[r[0], vn(r[1]), vn(r[2]), vn(r[3]), vn(r[4]), vn(r[5], 2), pct(r[6])] for r in t["rows"]]
    hold.append(["Cổ phiếu (8 mã)", "", "", "", vn(t["tot"][0]), vn(t["tot"][0] / navE * 100, 2), pct(t["tot"][3])])
    acts = []
    for d, sd, tk, q, px, v in _activity(c):
        acts.append([d, sd, tk, vn(q), vn(px), vn(v)])
    page3 = ["PAGEBREAK",
             section(f"Danh mục: cổ phiếu {vn(w_st, 1)}% NAV, 8 mã, mã lớn nhất TV1 {vn(t['rows'][0][5], 2)}% NAV"),
             table(["Mã", "KL", "Giá vốn", "Giá 30/10", "Giá trị (VND)", "% NAV", "Lãi/lỗ"], hold, total_rows=1, color_cols=(6,)),
             img(F("w_45_pair.png")),
             section(f"Giao dịch: mua {mil(sum(v[1] for v in c['buy'].values()))}, bán {mil(sum(v[1] for v in c['sell'].values()))}; thoái toàn bộ SCL, vòng mua–bán −8,3%"),
             table(["Ngày", "Chiều", "Mã", "KL", "Giá khớp BQ", "Giá trị (VND)"], acts, align=["l", "l", "l", "r", "r", "r"]),
             bullets([
                 "Mua HT1, VPB, SCL (26/10, 28/10) và MCH (29/10) theo chiến lược khai thác hiệu ứng sau công bố lợi nhuận.",
                 "Bán DRI 50% (chủ tài khoản quyết định) và VPB 200 cp lấy vốn mua MCH.",
                 "Thoái toàn bộ SCL: quyền mua gây pha loãng, giá trị hợp lý ước tính thấp hơn giá thị trường.",
             ], max_words=25),
             footnote("Cổ tức tiền mặt TV1 3,45 tr (trước thuế) chi trả 29/10, khấu trừ thuế 5% = 172.500 đ.")]

    # trang 4: thị trường + triển vọng
    liv = table(["Góc nhìn", "Dữ kiện 30/10/2026"], [
        ["Xu hướng", f"{fx['Đóng cửa 30/10/2026'].replace(' điểm', '')} ({fx['Thay đổi trong kỳ']}); trên MA20 {fx['Đóng cửa so với MA20']}, dưới MA50 {fx['Đóng cửa so với MA50']}, dưới MA200 {fx['Đóng cửa so với MA200']}; đỉnh thấp dần từ 1.874,48 (07/09)."],
        ["Hỗ trợ / kháng cự", "Kháng cự 1.773–1.781 (MA50, đỉnh 26/10), MA200 1.795; hỗ trợ 1.727–1.737, sâu hơn 1.677."],
        ["Động lượng", f"RSI(14) từ 57,2 xuống 47,1; MACD trừ tín hiệu từ +5,86 xuống +5,59: đà hồi yếu đi, chưa có tín hiệu đảo chiều giảm."],
        ["Thanh khoản", f"KL bình quân {fx['Khối lượng khớp trung bình phiên trong kỳ (5 phiên)']} ({fx['Chênh lệch khối lượng trung bình so với kỳ trước']}), dưới TB20; phiên lớn nhất 30/10 là phiên giảm; CMF +0,05."],
        ["Độ rộng", "Trên MA50 từ 46,5% xuống 29,8%, yếu hơn nhiều so với chỉ số; một nhóm mã hẹp đang nâng đỡ điểm số."],
    ], align=["l", "l"], widths=[18, 82])
    pdir = {"UP": "TĂNG", "DOWN": "GIẢM"}[fc["fields"]["H20_DIR"]]
    fc_line = (f"Dự báo đang mở (lập {fc['entry_as_of'][8:10]}/{fc['entry_as_of'][5:7]}, chấm điểm {fc['due'][8:10]}/{fc['due'][5:7]}/{fc['due'][:4]}): "
               f"VN-Index {pdir} sau 20 phiên, xác suất tự đánh giá {vn(float(fc['fields']['H20_P_UP']), 2)}; giữ mức 1.677; vô hiệu nếu đóng <1.690 trong 5 phiên với KL ≥700 triệu, hoặc bất kỳ phiên đóng <1.677.")
    funda = table(["Chỉ báo", "Mức hiện tại", "Kỳ trước"], [
        ["Định giá tổng hợp (phân vị 10 năm)", "14,4/100 — RẺ; P/E 10,68 (p3), P/B 1,78 (p12), chênh lãi suất +1,97 điểm % (p28)", "24,8"],
        ["Trạng thái theo mô hình chiến lược", "Trung tính; không có tín hiệu chuyển trạng thái đang tích luỹ", "thận trọng 13/25 phiên"],
    ], align=["l", "l", "l"], widths=[28, 54, 18])
    scen = table(["Kịch bản (ước lượng)", "Xác suất", "Điều kiện", "Vùng giá"], [
        ["Cơ sở: giằng co", "50%", "MA20 1.736,7 và 1.727 giữ; độ rộng <40% khiến nhịp tăng khó bền", "1.727–1.781"],
        ["Tiêu cực", "30%", "Đóng <1.727 với KL > TB20 (666 triệu cp)", "kiểm tra 1.677–1.690"],
        ["Tích cực", "20%", "Đóng >1.781, KL cải thiện, độ rộng >40%", "hướng 1.795 (MA200)"],
    ], align=["l", "r", "l", "l"], widths=[20, 10, 48, 22])
    page4 = ["PAGEBREAK",
             section("Thị trường: chỉ số −1,83% nhưng độ rộng tụt mạnh hơn; dưới MA50 và MA200",
                     "Phân tích kỹ thuật độc lập, chỉ dữ kiện đã tính; không dùng cho quyết định phân bổ."),
             img(F("w_67_pair.png")), liv,
             footnote(fc_line),
             footnote("Số dự báo đã chấm điểm: 0 — chưa đủ để đánh giá độ chính xác; kiểm thử lịch sử chưa cho thấy tốt hơn giả định 'thị trường tăng'. Tham khảo, không phải khuyến nghị."),
             section("Định giá thị trường ở vùng rẻ của 10 năm; mô hình trạng thái giữ Trung tính"),
             funda,
             footnote("Chỉ báo định giá mang tính tham khảo (0/17 góc nhìn qua kiểm định đa giả thuyết). Lợi nhuận doanh nghiệp, khối ngoại, lãi suất mới: không có số liệu đã đối soát trong kỳ."),
             section("Tuần tới (02–06/11): cơ sở là giằng co 1.727–1.781",
                     "Kỳ trước: cơ sở 1.740–1.800 đúng về giá (5 phiên đóng 1.741,62–1.766,65); điều kiện độ rộng <40% đã xảy ra từ 29/10."),
             scen,
             footnote("Sai kịch bản cơ sở: đóng ngoài 1.727–1.781 với KL trên TB20. Xác suất là ước lượng chủ quan, chưa kiểm định."),
             bullets([
                 f"Danh mục: 4 mã chờ đến hạn xem xét mua; tiền và Trứng vàng {mil(e['cash'] + e['egg_assets'])} ({vn(nonst, 1)}% NAV). Không có cổ tức chờ thanh toán.",
                 "Nếu mô hình chuyển Gấu/Khủng hoảng sau đủ phiên xác nhận, tỷ trọng cổ phiếu mục tiêu giảm.",
             ])]

    # phụ lục
    arows = [[k, vn(v, 0, True)] for k, v in sorted(c["attr"].items(), key=lambda kv: -kv[1]) if round(v) != 0]
    ex = c["interest"] - c["fee"] - c["tax"] - c["divtax"]
    arows += [["Biến động giá (gồm phần đã bán)", vn(c["price"], 0, True)],
              ["Lãi tiền gửi Trứng vàng + không kỳ hạn", vn(c["interest"], 0, True)],
              [f"Phí giao dịch ({vn(c['fee'])}) + thuế chuyển nhượng ({vn(c['tax'])})", vn(-(c["fee"] + c["tax"]), 0, True)],
              ["Thuế TNCN 5% cổ tức TV1", vn(-c["divtax"], 0, True)],
              ["Thu nhập ngoài giá", vn(ex, 0, True)],
              ["Thay đổi NAV đã loại dòng tiền", vn(c["dnadj"], 0, True)],
              ["Dòng tiền ngoại sinh: rút 29/10", vn(c["flow"], 0, True)],
              ["Thay đổi NAV theo sổ 23/10–30/10", vn(c["dn"], 0, True)]]
    appx = ["PAGEBREAK", section("Phụ lục — đối soát và phương pháp"),
            table(["Đóng góp vào NAV", "VND"], arows, total_rows=1, color_cols=(1,), max_rows=None,
                  bold_rows={len(arows) - 8, len(arows) - 4, len(arows) - 3}),
            bullets([
                "NAV = cổ phiếu theo giá đóng cửa + tiền mặt + Trứng vàng − dư nợ; 165.674.300 + 30.122.995 + 749.343.751 = 945.141.046 (chênh 0).",
                "Đóng góp giá = giá trị cuối − đầu kỳ − mua + bán; phí/thuế 29–30/10 (57.270 + 37.340 đ) theo biểu phí, chờ sao kê.",
                "Lãi Trứng vàng tính theo hiệu số đẳng thức tiền (≈179 nghìn VND/ngày, ≈8,5%/năm trên số dư).",
                "Tỷ suất kỳ: giá đơn vị đã loại dòng tiền; vốn khởi điểm 1 tỷ VND ngày 01/07, VN-Index mốc 30/06 = 1.860,01.",
                "VN-Index có cổ tức: tự tính từ cổ tức tiền mặt HOSE, tái đầu tư ngày GDKHQ, sau thuế 5%.",
                "Độ rộng: % mã trên MA50 trong rổ đủ điều kiện tại từng thời điểm (không dùng danh sách hiện tại).",
                "Phí 0,097% (HOSE) / 0,088% (UPCOM) mỗi chiều; thuế 0,1% giá trị bán. Lịch sử 85 phiên: so sánh mang tính mô tả.",
                "Không phải khuyến nghị đầu tư; kết quả quá khứ không bảo đảm tương lai. Số liệu đối chiếu với công ty chứng khoán lưu ký.",
             ], max_words=30, max_items=None)]

    blocks = page1 + page2 + page3 + page4 + appx
    pdf = os.path.join(OUT, "SpaceX_weekly_26-30_10_v2.pdf")
    n = R.build_pdf(blocks, pdf, header_left="Tài khoản SpaceX · Báo cáo tuần 26/10–30/10/2026",
                    header_right="Lập ngày 31/10/2026", footer="Không phải khuyến nghị đầu tư. Kết quả quá khứ không bảo đảm kết quả tương lai.",
                    archive_dirs=(FIG,))
    R.build_email_html(blocks[1:], ban, title, os.path.join(OUT, "SpaceX_weekly_26-30_10_v2_email.html"))

    # ─── đối chiếu số mock vs báo cáo gốc ───
    recon = [
        ("NAV 30/10", vn(navE), "945.141.046"),
        ("NAV 23/10", vn(s0["nav"]), "968.934.792"),
        ("Thay đổi NAV theo sổ", vn(c["dn"]), "−23.793.746"),
        ("Rút vốn 29/10", vn(c["flow"]), "−18.023.489"),
        ("Thay đổi do đầu tư (attribution tổng)", vn(c["dnadj"]), "−5.770.257"),
        ("Tuần, danh mục", pct(wk["return_pct"]), "−0,60%"),
        ("Tuần, VN-Index", pct(bw["vnindex_price_pct"]), "−1,83%"),
        ("Tuần, VN-Index có cổ tức", pct(bw["vnindex_tr_net_pct"]), "−1,83%"),
        ("Tuần, chênh", vn(ex_w, 2, True), "+1,23"),
        ("MTD, danh mục", pct(mtd["return_pct"]), "−1,89%"),
        ("MTD, VN-Index", pct(bm["vnindex_price_pct"]), "−1,53%"),
        ("MTD, VN-Index có cổ tức", pct(bm["vnindex_tr_net_pct"]), "−1,47%"),
        ("MTD, chênh", vn(ex_m, 2, True), "−0,36"),
        ("Từ đầu, danh mục", pct(inc["return_pct"]), "−3,69%"),
        ("Từ đầu, VN-Index", pct(bi["vnindex_price_pct"]), "−6,37%"),
        ("Từ đầu, VN-Index có cổ tức", pct(bi["vnindex_tr_net_pct"]), "−5,74%"),
        ("Từ đầu, chênh", vn(ex_i, 2, True), "+2,67"),
        ("Giá trị cổ phiếu", vn(e["mtm_stock"]), "165.674.300"),
        ("Tiền mặt", vn(e["cash"]), "30.122.995"),
        ("Trứng vàng", vn(e["egg_assets"]), "749.343.751"),
        ("% cổ phiếu", vn(w_st, 1) + "%", "17,5%"),
        ("% Trứng vàng", vn(w_egg, 1) + "%", "79,3%"),
        ("% tiền gửi + tiền mặt", vn(nonst, 1) + "%", "82,5%"),
        ("Sụt giảm tối đa", pct(risk["dd"], 2, False), "−10,29%"),
        ("Độ biến động ngày", vn(risk["vol"], 2) + "%", "0,77%"),
        ("Đóng góp giá", vn(c["price"]), "−6.285.700"),
        ("Lãi tiền gửi", vn(c["interest"]), "917.832"),
        ("Phí + thuế GD", vn(c["fee"] + c["tax"]), "229.889"),
        ("Thuế cổ tức TV1", vn(c["divtax"]), "172.500"),
        ("Thu nhập ngoài giá", vn(ex, 0, True), "+515.443"),
        ("Lãi chưa thực hiện", pct(t["tot"][3]), "+0,87%"),
        ("Tổng mua (triệu)", vn(sum(v[1] for v in c["buy"].values()) / 1e6, 2), "135,09"),
        ("Tổng bán (triệu)", vn(sum(v[1] for v in c["sell"].values()) / 1e6, 2), "55,37"),
        ("Độ rộng 30/10", vn(br[D1][0], 1) + "%", "29,8%"),
        ("Độ rộng 23/10", vn(br[D0][0], 1) + "%", "46,5%"),
    ]
    for r in t["rows"]:
        recon.append((f"{r[0]} lãi/lỗ", pct(r[6]), None))
    for d, sd, tk, q, px, v in _activity(c):
        recon.append((f"{d} {sd} {tk}", f"| {d} | {sd} | {tk} | {vn(q)} | {vn(px)} | {vn(v)} |", None))
    for d, (nv, r, v) in t["daily"].items():
        recon.append((f"NAV {d}", vn(nv), None))
        recon.append((f"Ngày {d} danh mục", pct(r), None))
    orig = open(ORIG, encoding="utf-8").read()
    rows, bad = [], 0
    for lab, m, o in recon:
        o = o or m
        found = o.lstrip("+") in orig
        ok = (m == o) and found
        bad += not ok
        rows.append((lab, m, o, "0" if m == o else "KHÁC", "có" if found else "KHÔNG THẤY"))
    import csv
    with open(os.path.join(REC, "weekly_recon.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["chi_tieu", "mock", "bao_cao_goc", "sai_lech", "co_trong_ban_goc"]); w.writerows(rows)
    body_words = {"pdf_text_all_pages": len(" ".join(R.pdf_text(pdf)).split()), "pdf_text_body": _body_words(pdf),
                  "prose_body": R.prose_words(blocks, stop_at="Phụ lục —")}
    meta = {"pages": n, "recon_items": len(rows), "recon_bad": bad, "title": title, "body_words": body_words,
            "canonical_day_2910_pct": round((L[-2][1] / L[-3][1] - 1) * 100, 4)}
    json.dump(meta, open(os.path.join(REC, "weekly_meta.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False))
    if bad:
        for r in rows:
            if r[3] != "0" or r[4] != "có":
                print("LỆCH:", r)
        sys.exit(2)


def _activity(c):
    """Bảng lệnh gộp theo (ngày, chiều, mã) từ calc.json trades — đúng cách báo cáo gốc gộp."""
    agg = {}
    for d, sd, tk, q, v, *_ in c["trades"]:
        k = (d, sd, tk)
        a = agg.setdefault(k, [0, 0]); a[0] += q; a[1] += v
    out = []
    for (d, sd, tk), (q, v) in sorted(agg.items(), key=lambda kv: (kv[0][0], kv[0][1] == "S", kv[0][2])):
        out.append((f"{d[8:10]}/{d[5:7]}", "Mua" if sd == "B" else "Bán", tk, q, round(v / q), v))
    return out


def _body_words(pdf):
    """Số từ thân = mọi trang trừ phụ lục, bỏ header/footer và chữ trong ảnh (ảnh không có text layer)."""
    pages = R.pdf_text(pdf)
    body = [p for p in pages if "Phụ lục — đối soát" not in p]
    n = 0
    for p in body:
        lines = [x for x in p.split("\n") if not re.match(r"^(Tài khoản SpaceX · |Lập ngày|Không phải khuyến nghị|Trang \d)", x)]
        n += len(" ".join(lines).split())
    return n


if __name__ == "__main__":
    main()
