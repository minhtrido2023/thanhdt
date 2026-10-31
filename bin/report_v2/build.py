#!/usr/bin/env python3
"""report_v2/build.py — dựng báo cáo tài khoản chuẩn v2 (ngày / tuần / tháng / quý).

    python3 bin/report_v2/build.py <daily|weekly|monthly|quarterly> --account <SpaceX|ZaloPay> \
        --period <YYYY-MM-DD | YYYY-MM-DD (thứ Sáu) | YYYY-MM | YYYY-Qn> --out-dir <dir> \
        [--narrative narrative.json] [--asof-label DD/MM/YYYY]

Đầu ra (KHÔNG gửi gì — gửi là việc của report_delivery_gate.py):
  <out-dir>/<stem>.md                        TÓM TẮT cùng tên chuẩn (cadence/ledger/return gate đọc)
  <out-dir>/v2/<stem>/<stem>.pdf              PDF A4, Be Vietnam Pro nhúng
  <out-dir>/v2/<stem>/<stem>_email.html       HTML email, ảnh `cid:` (+ _email_cid.json)
  <out-dir>/v2/<stem>/manifest.json           sha256 của PDF/HTML/ảnh + nguồn khối thị trường
  <out-dir>/v2/<stem>/*.png|*.csv             chart + dữ liệu vẽ
<stem> = <Account>_<cadence>_report_<period> (weekly: <thứ Hai>_to_<thứ Sáu>; quý: <YYYY>-Q<n>).
File .md ghi sha256 của PDF ⇒ sổ giao (hash của .md) bám luôn bản PDF; send_report_email.py thấy
dòng `report_v2_manifest:` thì gửi HTML cid + đính kèm PDF thay cho render markdown.

Số liệu: data_sources.py (chỉ pipeline). Phần chữ: narrative.json (narrative.py kiểm trần từ/gạch +
cấm tự viết số). Không có narrative ⇒ câu tự động dựng từ chính số pipeline (fallback an toàn).
rc: 0 xong · 2 narrative bị từ chối · 3 thiếu nguồn số bắt buộc · 1 lỗi khác.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_sources as S  # noqa: E402
import narrative as N  # noqa: E402
import render as R  # noqa: E402
from render import bullets, footnote, img, kpi_tiles, pct, section, table, vn  # noqa: E402

MANIFEST_TAG = "report_v2_manifest:"
PAGE_CAP = {"daily": 1, "weekly": 5, "monthly": 6, "quarterly": 8}
SRC_ACC = "Nguồn: dữ liệu tài khoản tại công ty chứng khoán lưu ký (NAV chốt cuối ngày), tính toán nội bộ."
SRC_VNI = "VN-Index: HOSE (giá đóng cửa); bản có cổ tức do đội tự tính, sau thuế TNCN 5%."
DISCLAIMER = ("Đây không phải là khuyến nghị đầu tư. Kết quả hoạt động trong quá khứ không đảm bảo cho kết quả "
              "trong tương lai. Mọi số liệu được đối chiếu với dữ liệu giao dịch tại công ty chứng khoán lưu ký.")
ACCT_META = {
    "SpaceX": {"no": "0002023347", "desc": "Chiến lược V2.4, có sử dụng ký quỹ", "investor": True,
               "audience": "Báo cáo hiệu suất và quản lý danh mục — dành cho nhà đầu tư"},
    "ZaloPay": {"no": "0001743768", "desc": "Chiến lược V2.4, chỉ tiền mặt", "investor": False,
                "audience": "Bản đầy đủ nội bộ — không gửi nhà đầu tư ngoài"},
}


def ddmm(d):
    return f"{d:%d/%m}"


def ddmmyyyy(d):
    return f"{d:%d/%m/%Y}"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


class Ctx:
    """Một lần dựng: thư mục, chart, khối PDF và TẬP SỐ đã in (để kiểm narrative)."""

    def __init__(self, cadence, acct, stem, out_dir):
        self.cadence, self.acct, self.stem = cadence, acct, stem
        self.out_dir = out_dir
        self.asset_dir = os.path.join(out_dir, "v2", stem)
        os.makedirs(self.asset_dir, exist_ok=True)
        self.blocks, self.facts, self.md, self.recon = [], [], [], []
        self.meta = ACCT_META[acct]

    def f(self, name):
        return os.path.join(self.asset_dir, name)

    def fact(self, *strings):
        self.facts.extend(str(s) for s in strings)
        return strings[0] if len(strings) == 1 else strings

    def add(self, *blks):
        self.blocks.extend(blks)

    def tbl(self, header, rows, **kw):
        for r in rows:
            self.fact(*r)
        return table(header, rows, **kw)

    def kpis(self, tiles, per_row=4):
        for t in tiles:
            self.fact(t[1], t[2])
        return kpi_tiles(tiles, per_row)


# ───────────────────────── khối dùng chung ─────────────────────────
def nav_parts(acct, d):
    r = S.nav_row_on_or_before(acct, d)
    g = {k: float(r.get(k) or 0) for k in ("nav", "mtm_stock", "cash", "egg_assets", "margin_debt", "offbook_assets")}
    g["date"] = S.D(r["date"])
    return g


def bridge_numbers(p, attr=None):
    """Cầu NAV từ khối kỳ nav_period_returns: NAV đầu → lãi/lỗ đầu tư → nạp/rút → NAV cuối.
    attr (tuỳ chọn) tách lãi/lỗ đầu tư thành giá cổ phiếu / phí-thuế / phần còn lại."""
    nav0, nav1 = p["nav0"], p["nav1"]
    flow = p.get("net_flow_vnd", 0.0)
    pnl = p["pnl_vnd"]
    assert abs(nav0 + pnl + flow - nav1) < 1, "cầu NAV không khép"
    out = {"nav0": nav0, "nav1": nav1, "flow": flow, "pnl": pnl, "flows": p.get("cash_flows", [])}
    if attr is not None:
        price = sum(attr["by_ticker"].values())
        fee = sum(f["fee"] for f in attr["fills"])
        tax = sum(f["tax"] for f in attr["fills"])
        out.update(price=price, fee=fee, tax=tax, other=pnl - price + fee + tax)
    return out


def flow_text(f):
    kind = "Rút" if f["amount_vnd"] < 0 else "Nạp"
    when = "đầu ngày" if f["timing"] == "bod" else "cuối ngày"
    t = f" {f['time_ict']}" if f.get("time_ict") else ""
    return f"{kind} {vn(abs(f['amount_vnd']))} VND ngày {ddmm(S.D(f['date']))}{t} ({when})"


def bridge_section(cx, br, period_label, chart_name):
    """Biểu đồ thác + bảng cầu NAV (luật 9b — có ở mọi cadence)."""
    items = []
    if "price" in br:
        items += [("Biến động giá cổ phiếu", br["price"]), ("Phí và thuế giao dịch", -(br["fee"] + br["tax"])),
                  ("Cổ tức, lãi tiền gửi, khác", br["other"])]
    else:
        items += [("Lãi/lỗ đầu tư", br["pnl"])]
    items += [("Nạp/rút vốn", br["flow"])]
    png = R.chart_waterfall(br["nav0"], items, br["nav1"], f"Cầu NAV {period_label}: rút/nạp vốn tách khỏi lãi/lỗ đầu tư",
                            cx.f(chart_name), SRC_ACC)
    rows = [["NAV đầu kỳ", vn(br["nav0"])]]
    if "price" in br:
        rows += [["  Biến động giá cổ phiếu", vn(br["price"], 0, True)],
                 ["  Phí và thuế giao dịch", vn(-(br["fee"] + br["tax"]), 0, True)],
                 ["  Cổ tức, lãi tiền gửi, khác (phần còn lại)", vn(br["other"], 0, True)]]
    rows += [["Lãi/lỗ đầu tư", vn(br["pnl"], 0, True)], ["Nạp/rút vốn", vn(br["flow"], 0, True)],
             ["NAV cuối kỳ", vn(br["nav1"])]]
    tb = cx.tbl(["Khoản mục", "VND"], rows, bold_rows=(len(rows) - 3, len(rows) - 1))
    fl = "; ".join(flow_text(f) for f in br["flows"]) or "Không có nạp/rút trong kỳ."
    cx.fact(fl)
    return png, tb, fl


def market_rows(cx, kind, period_end):
    """Bảng thị trường 5 dòng từ dữ kiện script tính (không văn xuôi, không tên nội bộ)."""
    meta, fx = S.market_facts(kind, period_end)
    a, p = S.D(meta["as_of"]), S.D(meta["prev_as_of"])
    g = lambda k: fx.get(k, "không có")  # noqa: E731
    rows = [
        ["Xu hướng", f"Đóng cửa {g(f'Đóng cửa {ddmmyyyy(a)}')} ({g('Thay đổi trong kỳ')} so với {ddmm(p)})"],
        ["So với đường trung bình", f"MA20 {g('Đóng cửa so với MA20')} · MA50 {g('Đóng cửa so với MA50')} · MA200 {g('Đóng cửa so với MA200')}"],
        ["Động lượng", f"RSI(14) {g('RSI(14)')} · MACD trừ tín hiệu {g('MACD trừ đường tín hiệu')}"],
        ["Thanh khoản", f"KL khớp bình quân {g([k for k in fx if k.startswith('Khối lượng khớp trung bình phiên trong kỳ')][0]) if any(k.startswith('Khối lượng khớp trung bình phiên trong kỳ') for k in fx) else 'không có'} ({g('Chênh lệch khối lượng trung bình so với kỳ trước')} so với kỳ trước)"],
        ["Độ rộng (% mã trên MA50)", f"{g(f'Tỷ lệ cổ phiếu đóng cửa trên MA50 ngày {ddmmyyyy(a)}')} (đầu kỳ {g(f'Tỷ lệ cổ phiếu đóng cửa trên MA50 ngày {ddmmyyyy(p)}')})"],
    ]
    for r in rows:
        r[1] = re.sub(r"\s*\(\d+ mã trong rổ\)", "", r[1]) if r[0].startswith("Độ rộng") else r[1]
    rng = (f"Cao/thấp trong kỳ: {g('Cao nhất trong kỳ (giá trong phiên)')} / {g('Thấp nhất trong kỳ (giá trong phiên)')}")
    return meta, fx, rows, rng


def regime_rows(cx):
    """2 dòng định giá + trạng thái (§6b), tên công khai; lỗi ⇒ "không có" kèm lý do."""
    try:
        dtl, vr = S.regime_lines()
    except S.Unavailable as exc:
        return [["Mô hình trạng thái thị trường", "không có"], ["Định giá thị trường (tham khảo)", "không có"]], str(exc)
    state = {"CRISIS": "Khủng hoảng", "BEAR": "Giảm", "NEUTRAL": "Trung tính", "BULL": "Tăng", "EX-BULL": "Tăng mạnh",
             "EXBULL": "Tăng mạnh"}
    m = re.search(r"\((CRISIS|BEAR|NEUTRAL|BULL|EX-?BULL)\)", dtl or "")
    cand = "không có trạng thái mới đang hình thành" if "không có candidate" in (dtl or "") else "có trạng thái mới đang tích luỹ"
    st_txt = f"{state[m.group(1)]} · {cand}" if m else "không có"
    m2 = re.search(r"Value Radar:\s*\S+\s*([\d.]+)\s*(RẺ|TRUNG TÍNH|ĐẮT)", vr or "")
    m3 = re.search(r"P/E ([\d.]+) \(p(\d+)\) · P/B ([\d.]+) \(p(\d+)\)", vr or "")
    if m2 and m3:
        v_txt = (f"{m2.group(2).capitalize()} ({vn(float(m2.group(1)), 1)}/100, phân vị 10 năm) · P/E {vn(float(m3.group(1)), 2)}"
                 f" · P/B {vn(float(m3.group(3)), 2)} — tham khảo, 0/17 qua kiểm định")
    else:
        v_txt = "không có"
    return [["Mô hình trạng thái thị trường", st_txt], ["Định giá thị trường (tham khảo)", v_txt]], None


def positions_block(cx, acct, d, nav):
    """Danh mục cuối kỳ: tỷ suất §21 (report_return_gate.position_returns) + khối tổng theo lớp tài sản."""
    pr = S.position_returns(acct, d)
    pos = pr["positions"]
    rows, tot_val, tot_pl, tot_cost = [], 0.0, 0.0, 0.0
    for tk, p in sorted(pos.items(), key=lambda kv: -kv[1]["qty"] * kv[1]["market"]):
        val = p["qty"] * p["market"]
        tot_val += val
        ok = p.get("pct") is not None and not p.get("excluded")
        if ok:
            tot_pl += p["pl"]; tot_cost += p["qty"] * p["raw_cost"]
        rows.append([tk, vn(p["qty"]), vn(p["raw_cost"]) if ok else "—", vn(p["market"]), vn(val),
                     pct(val / nav["nav"] * 100, 1, False), pct(p["pct"]) if ok else "—¹"])
    return pr, rows, tot_val, (tot_pl / tot_cost * 100 if tot_cost else None)


def asset_block_rows(nav, n_pos, stock_pct_ret):
    nv = nav["nav"]
    r = [["Cổ phiếu — tổng (%d mã)" % n_pos, vn(nav["mtm_stock"]), pct(nav["mtm_stock"] / nv * 100, 1, False),
          pct(stock_pct_ret) if stock_pct_ret is not None else "—"],
         ["Tiền mặt", vn(nav["cash"]), pct(nav["cash"] / nv * 100, 1, False), ""],
         ["Tiền gửi Trứng vàng", vn(nav["egg_assets"]), pct(nav["egg_assets"] / nv * 100, 1, False), ""],
         ["Nợ ký quỹ", vn(-nav["margin_debt"]) if nav["margin_debt"] else "0", pct(-nav["margin_debt"] / nv * 100, 1, False) if nav["margin_debt"] else "0,0%", ""]]
    if nav.get("offbook_assets"):
        r.append(["Tài sản ngoài sổ CTCK", vn(nav["offbook_assets"]), pct(nav["offbook_assets"] / nv * 100, 1, False), ""])
    r.append(["Tổng NAV", vn(nv), "100,0%", ""])
    return r


def write_outputs(cx, title, kicker, sub, header_left, md_lines, extra_manifest):
    """Banner + PDF + HTML email + manifest + .md tóm tắt. Trả dict kết quả."""
    bn = R.banner(title, kicker, sub, cx.f("00_banner.png"), mono=cx.acct[:2].upper())
    pdf = cx.f(cx.stem + ".pdf")
    blocks = [img(bn)] + cx.blocks
    pages = R.build_pdf(blocks, pdf, header_left=header_left, header_right=cx.meta["audience"],
                        footer=f"{cx.acct} · {DISCLAIMER[:96]}…", archive_dirs=(cx.asset_dir,))
    html = R.build_email_html(cx.blocks, bn, title, cx.f(cx.stem + "_email.html"))
    lint = R.lint_pdf(pdf)
    cid = json.load(open(html[:-5] + "_cid.json", encoding="utf-8"))
    man = {"version": 1, "stem": cx.stem, "cadence": cx.cadence, "account": cx.acct,
           "pdf": os.path.basename(pdf), "pdf_sha256": sha256(pdf),
           "html": os.path.basename(html), "html_sha256": sha256(html),
           "cid": {k: {"file": os.path.basename(v), "sha256": sha256(v)} for k, v in cid.items()},
           "pages": pages, "page_cap": PAGE_CAP[cx.cadence], "lint": lint, **extra_manifest}
    man_path = cx.f("manifest.json")
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1, default=str)
    rel_pdf = os.path.relpath(pdf, cx.out_dir)
    rel_man = os.path.relpath(man_path, cx.out_dir)
    md = "\n".join(md_lines).rstrip() + (
        f"\n\n---\n📎 Bản đầy đủ (PDF A4, {pages} trang, có biểu đồ): `{os.path.basename(pdf)}` — đính kèm email.\n"
        f"<!-- {MANIFEST_TAG} {rel_man} pdf_sha256={man['pdf_sha256']} pdf={rel_pdf} -->\n")
    md_path = os.path.join(cx.out_dir, cx.stem + ".md")
    with open(md_path + ".tmp", "w", encoding="utf-8") as fh:
        fh.write(md)
    os.replace(md_path + ".tmp", md_path)
    if pages > PAGE_CAP[cx.cadence]:
        raise RuntimeError(f"{cx.stem}: {pages} trang > trần {PAGE_CAP[cx.cadence]}")
    if lint["raw_markdown_hits"] or lint["non_bvp_fonts"]:
        raise RuntimeError(f"{cx.stem}: lint PDF hỏng {lint['raw_markdown_hits'][:3]} {lint['non_bvp_fonts']}")
    return {"md": md_path, "pdf": pdf, "html": html, "manifest": man_path, "pages": pages,
            "prose_words": R.prose_words(cx.blocks, stop_at="Phụ lục"), "recon": cx.recon}


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] + ["---:"] * (len(header) - 1)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def apply_narrative(cx, nar, key, default):
    """Gạch của mục `key`: narrative nếu có, không thì câu tự động (đã qua cùng trần)."""
    items = (nar or {}).get("sections", {}).get(key) or default
    return bullets(items)


# ───────────────────────── THÁNG ─────────────────────────
def build_monthly(acct, period, out_dir, nar_path=None):
    y, m = map(int, period.split("-"))
    m0 = dt.date(y, m, 1)
    m_end = (m0 + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    stem = f"{acct}_monthly_report_{y:04d}-{m:02d}"
    cx = Ctx("monthly", acct, stem, out_dir)
    P = S.periods(acct, m_end)
    mtd, inc = P["mtd"], P["inception"]
    d1 = S.D(mtd["to_date"])                          # phiên cuối tháng có NAV
    q_start = dt.date(y, 3 * ((m - 1) // 3) + 1, 1)
    qtd = S.extra_period(acct, q_start, m_end)
    ytd = S.extra_period(acct, dt.date(y, 1, 1), m_end)
    vnd = S.vni_close()
    nav1 = nav_parts(acct, d1)
    nav0 = nav_parts(acct, S.D(mtd["from_date"]))
    mlab = f"{m:02d}/{y}"

    # ── số chính (đều từ nav_period_returns) ──
    bm = mtd["benchmark"]
    ex_m = S.excess_pp(mtd, vnd)
    ex_i = S.excess_pp(inc, vnd)
    led = S.daily_window(acct, m0, d1)
    dates = [d for d, _, _ in led]
    u0 = led[0][1]
    port = [u / u0 * 100 for _, u, _ in led]
    v0 = S.vni_on_or_before(vnd, dates[0])[0]
    bench = [S.vni_on_or_before(vnd, d)[0] / v0 * 100 for d in dates]
    rk = S.risk_stats([(d, u) for d, u, _ in led])
    rk_v = S.risk_stats([(d, S.vni_on_or_before(vnd, d)[0]) for d in dates])
    full = S.ledger(acct)
    rk_i = S.risk_stats([(r["date"], r["unit_price"]) for r in full if r["date"] <= d1])
    months = S.month_series(acct, m_end)

    # ── đóng góp + phí (sổ vị thế + lệnh broker) ──
    try:
        attr = S.attribution(acct, S.D(mtd["from_date"]), d1)
        attr_err = None
    except S.Unavailable as exc:
        attr, attr_err = None, str(exc)
    br = bridge_numbers(mtd, attr)

    # ── KPI: hiệu suất dẫn đầu, NAV tuyệt đối thứ yếu (luật 9b) ──
    tiles = [
        (f"Tháng {mlab} (đã loại nạp/rút)", pct(mtd["return_pct"]), f"VN-Index {pct(bm['vnindex_price_pct'])}", R.tone(mtd["return_pct"])),
        ("Chênh so VN-Index", R.pp(ex_m), f"có cổ tức: {R.pp(bm['excess_vs_tr_pp'])}", R.tone(ex_m)),
        (f"Quý {(m - 1) // 3 + 1} (từ {ddmm(max(q_start, S.D(inc['from_date'])))})", pct(qtd["return_pct"]), f"VN-Index {pct(qtd['benchmark']['vnindex_price_pct'])}", R.tone(qtd["return_pct"])),
        (f"Từ đầu (từ {ddmm(S.D(inc['from_date']))})", pct(inc["return_pct"]), f"VN-Index {pct(inc['benchmark']['vnindex_price_pct'])}", R.tone(inc["return_pct"])),
        ("Sụt giảm sâu nhất trong tháng", pct(rk["mdd"], 2, False), f"VN-Index {pct(rk_v['mdd'], 2, False)}", None),
        ("Độ biến động ngày", pct(rk["sd"], 2, False) if rk["sd"] is not None else "không có", f"VN-Index {pct(rk_v['sd'], 2, False)}" if rk_v["sd"] else "", None),
        ("Lãi/lỗ đầu tư tháng", R.mil(br["pnl"]), "VND, đã loại nạp/rút", R.tone(br["pnl"])),
        (f"NAV cuối tháng ({ddmm(d1)})", R.mil(nav1["nav"]), f"nạp/rút {R.mil(br['flow'])}" if br["flow"] else "không nạp/rút", None),
    ]
    better = "hơn" if ex_m > 0 else "kém"
    auto_head = (f"Tháng {mlab} {pct(mtd['return_pct'])} so với VN-Index {pct(bm['vnindex_price_pct'])}: "
                 f"{better} chỉ số {R.vn(abs(ex_m), 2)} điểm %, từ đầu {pct(inc['return_pct'])}")
    cx.fact(auto_head, ddmm(d1), ddmmyyyy(d1), mlab)

    # ── số tham chiếu cho narrative (fact set) — PHẢI tính trước khi kiểm narrative ──
    kp_html = cx.kpis(tiles)
    f1 = R.chart_index_vs_bench(dates, port, bench, f"NAV theo ngày tháng {mlab} so với VN-Index (cơ sở 100 = {ddmm(dates[0])})",
                                cx.f("01_nav_vs_vni.png"), f"{SRC_ACC} {SRC_VNI}", port_label="Danh mục (đã loại nạp/rút)",
                                size=(7.6, 2.7))
    png_br, tb_br, fl_txt = bridge_section(cx, br, f"tháng {mlab}", "02_bridge.png")

    per_rows = []
    for lab, p in ((f"Tháng {mlab}", mtd), (f"Quý {(m - 1) // 3 + 1}/{y} (từ {ddmm(max(q_start, S.D(inc['from_date'])))})", qtd),
                   (f"Năm {y} (từ {ddmm(max(dt.date(y, 1, 1), S.D(inc['from_date'])))})", ytd), (f"Từ khi bắt đầu ({ddmm(S.D(inc['from_date']))})", inc)):
        b_ = p["benchmark"]
        per_rows.append([lab, pct(p["return_pct"]), pct(b_["vnindex_price_pct"]) if b_.get("vnindex_price_pct") is not None else "không có",
                         pct(b_["vnindex_tr_pct"]) if b_.get("vnindex_tr_pct") is not None else "không có",
                         R.pp(b_["excess_vs_price_pp"]).replace(" điểm %", "") if b_.get("excess_vs_price_pp") is not None else "không có",
                         R.pp(b_["excess_vs_tr_pp"]).replace(" điểm %", "") if b_.get("excess_vs_tr_pp") is not None else "không có"])
    tb_per = cx.tbl(["Giai đoạn", cx.acct, "VN-Index", "VN-Index có cổ tức", "Chênh (điểm %)", "Chênh có cổ tức"],
                    per_rows, color_cols=(1, 4, 5))
    ml = [x[0] for x in months]
    f_grid = R.chart_month_grid(ml, [x[1] for x in months], [x[2] for x in months],
                                "Tỷ suất từng tháng so với VN-Index", cx.f("03_months.png"),
                                f"{SRC_ACC} Tháng đầu tính từ mốc vốn gốc. {SRC_VNI}", size=(7.6, 1.6))
    for x in months:
        cx.fact(pct(x[1]), pct(x[2]) if x[2] is not None else "", R.pp(x[1] - x[2]) if x[2] is not None else "")

    risk_rows = [
        ["Độ biến động ngày (tháng)", pct(rk["sd"], 2, False) if rk["sd"] is not None else "không có", pct(rk_v["sd"], 2, False) if rk_v["sd"] else "không có"],
        ["Độ biến động quy năm (tháng)", pct(rk["ann"], 1, False) if rk["ann"] is not None else "không có", pct(rk_v["ann"], 1, False) if rk_v["ann"] else "không có"],
        ["Sụt giảm sâu nhất trong tháng", f"{pct(rk['mdd'], 2, False)} ({ddmm(rk['mdd_date'])})", f"{pct(rk_v['mdd'], 2, False)} ({ddmm(rk_v['mdd_date'])})"],
        ["Sụt giảm sâu nhất từ khi bắt đầu", f"{pct(rk_i['mdd'], 2, False)} ({ddmm(rk_i['mdd_date'])})", "—"],
        ["Tỷ lệ phiên tăng (tháng)", pct(rk["up_ratio"], 0, False) if rk["up_ratio"] is not None else "không có", pct(rk_v["up_ratio"], 0, False) if rk_v["up_ratio"] is not None else "không có"],
        ["Beta so với VN-Index", "không có", "—"],
    ]
    tb_risk = cx.tbl(["Chỉ tiêu", "Danh mục", "VN-Index"], risk_rows)
    dd_p, pk = [], 0
    dd_v, pkv = [], 0
    fd = [r["date"] for r in full if r["date"] <= d1]
    for r in full:
        if r["date"] > d1:
            break
        pk = max(pk, r["unit_price"]); dd_p.append((r["unit_price"] / pk - 1) * 100)
    for d in fd:
        v = S.vni_on_or_before(vnd, d)[0]
        pkv = max(pkv, v); dd_v.append((v / pkv - 1) * 100)
    f_uw = R.chart_underwater(fd, dd_p, f"Sụt giảm từ đỉnh từ khi bắt đầu: sâu nhất {pct(rk_i['mdd'], 2, False)} ({ddmm(rk_i['mdd_date'])})",
                              cx.f("04_underwater.png"), f"{SRC_ACC} {SRC_VNI}", bench=dd_v)

    # đóng góp theo mã
    if attr is not None:
        items = sorted(attr["by_ticker"].items(), key=lambda kv: -abs(kv[1]))
        top = items[:8]
        rest = sum(v for _, v in items[8:])
        hb = [(k, v) for k, v in top] + ([("Các mã khác", rest)] if items[8:] else [])
        hb.sort(key=lambda kv: -kv[1])
        f_attr = R.chart_hbars(hb, f"Đóng góp giá cổ phiếu theo mã tháng {mlab} (tổng {R.mil(br['price'])})",
                               cx.f("05_attribution.png"), "Nguồn: KL vị thế và lệnh khớp tại CTCK lưu ký; giá đóng cửa HOSE/HNX/UPCoM chưa điều chỉnh.",
                               total=("Tổng", br["price"]), size=(7.6, 3.0))
        for k, v in hb:
            cx.fact(vn(v, 0, True), R.mil(v))
        # giao dịch: gộp theo mã + chiều
        agg = {}
        for f in attr["fills"]:
            a = agg.setdefault((f["ticker"], f["side"]), [0, 0.0])
            a[0] += f["qty"]; a[1] += f["value"]
        buys = sorted(((k[0], v) for k, v in agg.items() if k[1] == "B"), key=lambda kv: -kv[1][1])
        sells = sorted(((k[0], v) for k, v in agg.items() if k[1] == "S"), key=lambda kv: -kv[1][1])
        vb, vs = sum(v[1] for _, v in buys), sum(v[1] for _, v in sells)
        tr_rows = [["Mua", str(len(buys)), vn(vb), ", ".join(k for k, _ in buys[:6]) + (" …" if len(buys) > 6 else "") or "—"],
                   ["Bán", str(len(sells)), vn(vs), ", ".join(k for k, _ in sells[:6]) + (" …" if len(sells) > 6 else "") or "—"],
                   ["Tổng", str(len(buys) + len(sells)), vn(vb + vs), ""]]
        tb_tr = cx.tbl(["Chiều", "Số mã", "Giá trị khớp (VND)", "Mã chính"], tr_rows, total_rows=1, align=["l", "r", "r", "l"])
        n_conf = sum(1 for f in attr["fills"] if f["fee_src"] == "xác nhận CTCK")
        cost_rows = [["Giá trị mua trong tháng", vn(vb)], ["Giá trị bán trong tháng", vn(vs)],
                     [f"Phí giao dịch ({n_conf}/{len(attr['fills'])} dòng theo xác nhận CTCK, còn lại theo biểu phí)", vn(br["fee"])],
                     ["Thuế chuyển nhượng (0,1% giá trị bán)", vn(br["tax"])],
                     ["Tổng chi phí giao dịch", vn(br["fee"] + br["tax"])],
                     ["Lãi vay ký quỹ", "0 (không dư nợ cuối kỳ)" if not nav1["margin_debt"] else f"không có (dư nợ cuối kỳ {vn(nav1['margin_debt'])})"],
                     ["Phí quản lý / phí hiệu suất", "0"]]
        tb_cost = cx.tbl(["Khoản mục", "VND"], cost_rows, bold_rows=(4,))
        cx.fact(pct((br["fee"] + br["tax"]) / ((br["nav0"] + br["nav1"]) / 2) * 100, 2, False))
        mc = attr["mtm_check"]
        cx.recon.append(("Σ KL×giá đầu kỳ vs mtm_stock nav_history", mc["calc0"], mc["nav0_mtm"], mc["calc0"] - mc["nav0_mtm"]))
        cx.recon.append(("Σ KL×giá cuối kỳ vs mtm_stock nav_history", mc["calc1"], mc["nav1_mtm"], mc["calc1"] - mc["nav1_mtm"]))
    else:
        f_attr = tb_tr = tb_cost = None

    # danh mục cuối tháng
    pr, pos_rows, tot_val, stock_ret = positions_block(cx, acct, d1, nav1)
    show = pos_rows[:9]
    if len(pos_rows) > 9:
        rest_val = sum(float(r[4].replace(".", "").replace("−", "-")) for r in pos_rows[9:])
        show.append([f"{len(pos_rows) - 9} mã khác", "", "", "", vn(rest_val), pct(rest_val / nav1["nav"] * 100, 1, False), ""])
    tb_pos = cx.tbl(["Mã", "KL", "Giá vốn", "Giá cuối", "Giá trị (VND)", "% NAV", "Lãi/lỗ (đã cộng cổ tức)"], show,
                    color_cols=(6,), widths=[9, 9, 12, 12, 20, 10, 28])
    ab = asset_block_rows(nav1, len(pos_rows), stock_ret)
    tb_ab = cx.tbl(["Lớp tài sản", "Giá trị (VND)", "% NAV", "Lãi/lỗ"], ab, bold_rows=(0, len(ab) - 1), max_rows=None)
    f_al = R.chart_alloc([(f"Đầu tháng ({ddmm(nav0['date'])})", {"Cổ phiếu": nav0["mtm_stock"], "Trứng vàng": nav0["egg_assets"], "Tiền mặt": max(nav0["cash"], 0)}),
                          (f"Cuối tháng ({ddmm(d1)})", {"Cổ phiếu": nav1["mtm_stock"], "Trứng vàng": nav1["egg_assets"], "Tiền mặt": max(nav1["cash"], 0)})],
                         "Phân bổ tài sản đầu và cuối tháng (% NAV)", cx.f("06_allocation.png"), SRC_ACC)
    cx.fact(pct(nav0["mtm_stock"] / nav0["nav"] * 100, 1, False), pct(nav1["mtm_stock"] / nav1["nav"] * 100, 1, False))

    # thị trường
    try:
        mmeta, _fx, mk_rows, rng = market_rows(cx, "monthly", m_end)
        mk_err = None
    except Exception as exc:  # noqa: BLE001 — khối thị trường thiếu nguồn ⇒ "không có", báo cáo vẫn dựng
        mk_rows, rng, mk_err = [["Thị trường", "không có"]], "", f"{type(exc).__name__}: {exc}"
    rg_rows, rg_err = regime_rows(cx)
    tb_mk = cx.tbl(["Thị trường (VN-Index)", f"Cuối tháng {mlab}"], mk_rows + rg_rows, widths=[30, 70])
    cx.fact(rng)
    pass_blk = S.market_pass_block("monthly", m_end) if not mk_err else None
    fc_line = None
    if pass_blk and pass_blk.get("forecast", {}).get("fields"):
        ff = pass_blk["forecast"]["fields"]
        dirv = {"UP": "tăng", "DOWN": "giảm"}.get(ff.get("H20_DIR"), ff.get("H20_DIR", ""))
        fc_line = (f"Dự báo kỹ thuật 20 phiên đang mở: {dirv} (xác suất tự đánh giá {ff.get('H20_P_UP')}); đã chấm 0 dự báo, "
                   f"chưa tốt hơn giả định thị trường tăng.")
        cx.fact(fc_line)

    # ── narrative (kiểm SAU khi đã có tập số) ──
    nar = N.validate(N.load(nar_path), "\n".join(cx.facts), investor_facing=cx.meta["investor"],
                     allow_internal=not cx.meta["investor"])
    title = (nar or {}).get("headline") or auto_head
    key = (nar or {}).get("key_points") or [
        f"Tháng {mlab}: {pct(mtd['return_pct'])} so với VN-Index {pct(bm['vnindex_price_pct'])} (có cổ tức {pct(bm['vnindex_tr_pct'])}).",
        f"Lãi/lỗ đầu tư {R.mil(br['pnl'])}; nạp/rút {R.mil(br['flow'])} không tính vào hiệu suất.",
        f"Tỷ trọng cổ phiếu {pct(nav0['mtm_stock'] / nav0['nav'] * 100, 1, False)} đầu tháng, {pct(nav1['mtm_stock'] / nav1['nav'] * 100, 1, False)} cuối tháng.",
    ]

    # ── TRANG 1: tear sheet ──
    cx.add(kp_html, img(f1), section("3 điều cần biết"), bullets(key))
    # ── Cầu NAV + hiệu suất ──
    cx.add(section(f"Cầu NAV: lãi/lỗ đầu tư {R.mil(br['pnl'])}, nạp/rút {R.mil(br['flow'])}"),
           img(png_br, 470), tb_br, footnote(fl_txt),
           apply_narrative(cx, nar, "bridge", ["Hiệu suất tính theo giá đơn vị, đã loại nạp/rút; NAV tuyệt đối chỉ dùng trong cầu NAV."]))
    cx.add(section(f"Hiệu suất: tháng {pct(mtd['return_pct'])}, từ đầu {pct(inc['return_pct'])} so với VN-Index {pct(inc['benchmark']['vnindex_price_pct'])}"),
           tb_per, img(f_grid),
           apply_narrative(cx, nar, "performance", [f"Chênh tháng so VN-Index giá {R.pp(ex_m)}; từ khi bắt đầu {R.pp(ex_i)}."]))
    cx.add(section(f"Rủi ro: sụt giảm tháng {pct(rk['mdd'], 2, False)} so với VN-Index {pct(rk_v['mdd'], 2, False)}"),
           tb_risk, img(f_uw),
           apply_narrative(cx, nar, "risk", ["Beta chưa công bố: pipeline chưa có chuỗi đủ dài để ước lượng ổn định."]),
           footnote("Độ biến động = độ lệch chuẩn tỷ suất ngày theo giá đơn vị; quy năm × căn 252. Sharpe/Sortino chưa công bố do lịch sử NAV ngắn."))
    if f_attr:
        cx.add(section(f"Đóng góp: giá cổ phiếu {R.mil(br['price'])}, phí và thuế {R.mil(-(br['fee'] + br['tax']))}"),
               img(f_attr), apply_narrative(cx, nar, "attribution", [f"Phần còn lại {R.mil(br['other'])} gồm cổ tức, lãi tiền gửi và chênh giá đối chiếu."]))
        cx.add(section("Hoạt động giao dịch trong tháng"), tb_tr, apply_narrative(cx, nar, "trades", [f"Tổng giá trị khớp {R.mil(vb + vs)} trong tháng."]))
    else:
        cx.add(section("Đóng góp theo mã và giao dịch: không có"), footnote(f"Không dựng được từ sổ broker: {attr_err}"))
    cx.add(section(f"Danh mục cuối tháng ({ddmm(d1)}): cổ phiếu {pct(nav1['mtm_stock'] / nav1['nav'] * 100, 1, False)} NAV"),
           tb_pos, tb_ab, img(f_al),
           footnote("Lãi/lỗ từng mã: giá vốn thô (đã cộng lại phần cổ tức CTCK trừ khỏi giá vốn) và cổ tức tiền ròng sau thuế 5%. ¹ chưa đối chiếu xong cổ tức nên không công bố."),
           apply_narrative(cx, nar, "portfolio", [f"{len(pos_rows)} mã cuối tháng; tổng NAV {vn(nav1['nav'])} VND."]))
    if tb_cost:
        cx.add(section(f"Chi phí: {R.mil(br['fee'] + br['tax'])} phí và thuế giao dịch"), tb_cost,
               apply_narrative(cx, nar, "costs", ["Không có phí quản lý hay phí hiệu suất."]))
    cx.add(section("Thị trường và vĩ mô cuối tháng"), tb_mk, footnote(rng + ". " + SRC_VNI) if rng else footnote(f"Khối thị trường không có: {mk_err}"),
           *( [footnote(fc_line)] if fc_line else []),
           apply_narrative(cx, nar, "market", ["Định giá thị trường là thông tin tham khảo, không phải tín hiệu mua/bán."]))
    ol = (nar or {}).get("outlook")
    if ol:
        ol_rows = [[r["scenario"], r["condition"], r["invalidation"], r["prob"] or "—"] for r in ol]
        cx.add(section(f"Triển vọng tháng tới: {len(ol)} kịch bản"),
               table(["Kịch bản", "Điều kiện xác nhận", "Điều kiện bác bỏ", "Xác suất (ước lượng chủ quan)"], ol_rows,
                     align=["l", "l", "l", "l"], widths=[22, 31, 31, 16]))
    else:
        cx.add(section("Triển vọng tháng tới: không có"), footnote("Chưa có bảng kịch bản cho kỳ này."))
    # ── Phụ lục ──
    app = [section("Phụ lục — phương pháp, đối soát và công bố"),
           footnote("NAV mark-to-market theo giá đóng cửa, gồm cổ phiếu, tiền mặt, tiền gửi sinh lời tại CTCK, trừ dư nợ ký quỹ; đối chiếu với dữ liệu tài khoản tại CTCK lưu ký."),
           footnote("Hiệu suất = tỷ suất theo giá đơn vị (time-weighted), loại nạp/rút theo thời điểm ghi trong sổ dòng tiền; không tỷ suất nào lấy từ NAV cuối chia NAV đầu."),
           footnote(f"Mốc VN-Index kỳ từ khi bắt đầu: đóng cửa {ddmm(S.D(inc['benchmark'].get('anchor_date') or inc['from_date']))}. Đóng góp theo mã dùng giá đóng cửa chưa điều chỉnh."),
           footnote(DISCLAIMER)]
    if cx.recon:
        app.append(table(["Đối soát", "Tính lại", "Pipeline", "Lệch"], [[a, vn(b_), vn(c), vn(d, 0, True)] for a, b_, c, d in cx.recon],
                         max_rows=None))
    if attr and attr["qty_flags"]:
        app.append(footnote("KL đầu + mua − bán ≠ KL cuối (thường do cổ tức bằng cổ phiếu/quyền): "
                            + "; ".join(f"{t} {a}+{b_}−{c}≠{d}" for t, a, b_, c, d in attr["qty_flags"])))
    if nar and nar.get("internal"):
        for blk in nar["internal"]:
            app += [section("Nội bộ — " + blk["title"]), bullets(blk["bullets"], max_words=40, max_items=5)]
    cx.add(*app)

    # ── .md tóm tắt (cổng giao đọc) ──
    md = [f"# {title}", "",
          f"**Tài khoản:** {acct} · DNSE {cx.meta['no']} · {cx.meta['desc']}  ",
          f"**Kỳ báo cáo:** tháng {mlab} ({ddmm(m0)} – {ddmmyyyy(m_end)}, phiên cuối có NAV {ddmmyyyy(d1)})  ",
          f"**Đối tượng:** {cx.meta['audience']}", "",
          "## Tóm tắt", *[f"- {k}" for k in key], "",
          *md_table(["Chỉ tiêu", "Giá trị", "So sánh"], [[t[0], t[1], t[2]] for t in tiles]), "",
          "## Cầu NAV", *md_table(["Khoản mục", "VND"], [[r[0].strip(), r[1]] for r in [["NAV đầu kỳ", vn(br["nav0"])], ["Lãi/lỗ đầu tư", vn(br["pnl"], 0, True)], ["Nạp/rút vốn", vn(br["flow"], 0, True)], ["NAV cuối kỳ", vn(br["nav1"])]]]),
          f"_{fl_txt}_", "",
          "## Hiệu suất lũy kế", S.period_table_md(acct, m_end), "",
          f"## Danh mục cuối tháng ({ddmmyyyy(d1)})",
          *md_table(["Mã", "Khối lượng", "Giá vốn (đ/cp)", f"Giá đóng cửa {ddmm(d1)}", "Giá trị thị trường (đ)", "% NAV", "Lãi/lỗ chưa thực hiện (%)"], pos_rows), "",
          *md_table(["Lớp tài sản", "Giá trị (VND)", "% NAV", "Lãi/lỗ"], ab), ""]
    if nar and nar.get("internal"):
        md += ["## Nội bộ"] + [f"- **{blk['title']}:** " + " · ".join(blk["bullets"]) for blk in nar["internal"]] + [""]
    extra = {"period": f"{y:04d}-{m:02d}", "report_date": m_end.isoformat(), "nav_date": d1.isoformat(),
             "market_block": ({"md": pass_blk.get("md"), "block_sha256": pass_blk.get("block_sha256")} if pass_blk else None),
             "market_facts_error": mk_err, "regime_error": rg_err, "attribution_error": attr_err,
             "numbers": {"mtd_pct": mtd["return_pct"], "qtd_pct": qtd["return_pct"], "ytd_pct": ytd["return_pct"],
                         "inception_pct": inc["return_pct"], "nav1": nav1["nav"], "pnl_vnd": br["pnl"], "flow_vnd": br["flow"]},
             "narrative": bool(nar)}
    hl = f"Báo cáo tháng {mlab} · {acct}"
    return write_outputs(cx, title, f"BÁO CÁO THÁNG {mlab}", f"Tài khoản {acct} · {cx.meta['desc']} · dữ liệu đến {ddmmyyyy(d1)}",
                         hl, md, extra)


BUILDERS = {"monthly": build_monthly}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cadence", choices=("daily", "weekly", "monthly", "quarterly"))
    ap.add_argument("--account", required=True, choices=S.ACCOUNTS)
    ap.add_argument("--period", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--narrative")
    a = ap.parse_args(argv)
    if a.cadence not in BUILDERS:
        print(f"build.py: cadence {a.cadence} chưa có builder", file=sys.stderr)
        return 1
    os.makedirs(a.out_dir, exist_ok=True)
    try:
        res = BUILDERS[a.cadence](a.account, a.period, os.path.abspath(a.out_dir), a.narrative)
    except N.NarrativeError as exc:
        print(f"build.py: {exc}", file=sys.stderr)
        return 2
    except S.Unavailable as exc:
        print(f"build.py: THIẾU NGUỒN SỐ bắt buộc — {exc}", file=sys.stderr)
        return 3
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return 1
    print(json.dumps({k: v for k, v in res.items() if k != "recon"}, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
