#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `period_table_32.py` (render bảng 3.2 + cổng ô chỉ số) và đường nối
`report_delivery_gate._check_benchmark_table` — không BQ, không broker, không ghi `data/`, không gửi gì
(CLI giả trả JSON dựng từ `compute_period_returns` trên chuỗi tự chế). Chạy dưới `env -u TZ` và TZ lạ:

    env -u TZ python3 mike/bin/period_table_32_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/period_table_32_selfcheck.py
"""
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nav_period_returns as npr  # noqa: E402
import period_table_32 as pt  # noqa: E402
import report_delivery_gate as rdg  # noqa: E402
from nav_period_benchmark_selfcheck import bm_fn, fixture  # noqa: E402

N_OK = 0
RECV = [0.0]                       # cashDividendReceiving giả cho selfcheck (B4); test đọc thật ở cuối
_real_div_receiving = pt.div_receiving
pt.div_receiving = lambda *a, **k: RECV[0]
_recv_fn = lambda account, d: RECV[0]  # noqa: E731


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def blocks(text, cli, must=(), installed=True, acc="ZaloPay"):
    try:
        pt.check_report("X_weekly.md", text, acc, "2030-06-06", cli=cli, series_installed=lambda: installed, recv_fn=_recv_fn)
    except pt.TableBlock as e:
        for m in must:
            ok(m in str(e), f"thông điệp phải trích {m!r}: {e}")
        return str(e)
    ok(False, f"phải CHẶN (cần {must})")


def passes(text, cli, installed=True, acc="ZaloPay"):
    out = pt.check_report("X_weekly.md", text, acc, "2030-06-06", cli=cli, series_installed=lambda: installed, recv_fn=_recv_fn)
    ok(out and ("PASS" in out[0] or "WARN" in out[0]), f"phải qua: {out}")
    return out[0]


def mkcli(main, sleeve, main_rc=0, sleeve_rc=0):
    def cli(account, d, s):
        return (sleeve_rc, sleeve, "") if s else (main_rc, main, "lỗi giả" if main_rc else "")
    return cli


def doc(table):
    return f"# Báo cáo tuần\n\n### 3.2 Hiệu suất lũy kế\n\n{table}\n### 3.3 Khác\n"


def replace_cell(text, row_kw, col, new):
    lines = text.splitlines()
    hdr = None
    for i, ln in enumerate(lines):
        if ln.startswith("| Giai đoạn"):
            hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
        if hdr and ln.startswith("|") and row_kw in ln.split("|")[1]:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            cells[hdr.index(col)] = new
            lines[i] = "| " + " | ".join(cells) + " |"
            return "\n".join(lines) + "\n"
    raise AssertionError(f"không thấy dòng {row_kw}")


def main() -> int:
    # B3: selfcheck PHẢI test module của CHÍNH cây chứa nó (worktree từng có symlink `mike` → checkout chính;
    # `python3 mike/bin/..._selfcheck.py` chạy từ gốc worktree sẽ test nhầm master).
    for mod in (pt, npr, rdg):
        ok(os.path.realpath(mod.__file__).startswith(os.path.realpath(HERE) + os.sep),
           f"{mod.__name__} nạp từ {mod.__file__}, KHÔNG phải cây của selfcheck ({HERE}) — test nhầm cây khác")
    D, series, inc, rows, _sat = fixture()
    rd = D[66]
    a = npr.compute_period_returns("ZaloPay", rd, rows, inc, [], benchmark=bm_fn(series))
    a = json.loads(json.dumps(a))
    # chuỗi b giả: NAV b = 60% NAV a (ngoài bot 40%) — chỉ cần đúng cấu trúc đầu ra --sleeve bot
    rows_b = [type(r)(r[0], r[1] * 0.6) for r in rows if D[40] < r[0] <= rd]
    b = npr._assemble("ZaloPay", rd, *npr.build_ledger(rows_b, [], D[40], 600_000_000.0), D[40], bm_fn(series),
                      inc)
    b.update({"series": "bot", "outside_scope": [{"ticker": "DGC", "from": D[40].isoformat(), "to": None}],
              "outside_at_inception_vnd": 400_000_000})
    b = json.loads(json.dumps(b))

    # 1. parse_cell
    ok(pt.parse_cell("−1,16%") == -1.16 and pt.parse_cell("+1,91pp") == 1.91 and pt.parse_cell("**+0,52%**") == 0.52,
       "parse số VN")
    ok(pt.parse_cell("chưa có số (G4: …)") == pt.NO_NUMBER and pt.parse_cell("—") is None
       and pt.parse_cell("−1.330,5%") is None and pt.parse_cell("+nan%") is None, "parse ô lạ")
    ok(pt.fmt_num(-1.157, "%") == "−1,16%" and pt.fmt_num(0.0004, "pp") == "0,00pp", "fmt_num")

    # 2. render → cổng: vòng tròn khép kín qua (kèm dòng b), số lấy NGUYÊN từ CLI
    t = pt.render(a, b)
    ok(pt.COL_TR in t and "sau thuế TNCN 5%" in t and "DGC" in t and "40,00% NAV" in t, f"render:\n{t}")
    ok(t.count(pt.SLEEVE_LABEL) == 4, "3 dòng b + 1 chú thích")      # 3 dòng + chú thích
    # B1 vòng 2: mốc VN-Index theo tài khoản ≠ dòng sổ 0 ⇒ chú thích nêu đúng ngày mốc đã dùng
    ia = a["inception"]["benchmark"]["index_anchor_date"]
    ok(ia == inc["index_anchor_date"] and f"giá đóng cửa {ia[8:10]}/{ia[5:7]}/{ia[:4]}" in t,
       f"chú thích mốc VN-Index {ia}:\n{t}")
    cli = mkcli(a, b)
    ok("(b) inception: khớp CLI" in passes(doc(t), cli), "render → PASS")
    bm = a["inception"]["benchmark"]
    ok(pt.fmt_num(bm["vnindex_tr_pct"], "%") in t and pt.fmt_num(bm["excess_vs_tr_pp"], "pp") in t, "ô = CLI")

    # 3. lệch > 0,005 điểm % ⇒ chặn, trích ô + số CLI; ⩽ 0,005 qua
    t2 = replace_cell(doc(t), "Từ khi bắt đầu", pt.COL_TR, pt.fmt_num(bm["vnindex_tr_pct"] + 0.01, "%"))
    blocks(t2, cli, (pt.COL_TR, f"{bm['vnindex_tr_pct']:+.3f}"))
    a2 = copy.deepcopy(a)
    a2["inception"]["benchmark"]["vnindex_price_pct"] = 1.1249
    tt = replace_cell(doc(t), "Từ khi bắt đầu", pt.COL_PRICE, "+1,12%")
    passes(tt, mkcli(a2, b))
    a2["inception"]["benchmark"]["vnindex_price_pct"] = 1.1149
    blocks(tt, mkcli(a2, b), ("lệch 0.005",))
    # chênh lệch tự trừ lại từ số đã làm tròn (không lấy NGUYÊN từ CLI) ⇒ chặn khi lệch > 0,005
    a3 = copy.deepcopy(a)
    a3["inception"]["benchmark"]["excess_vs_price_pp"] += 0.009
    blocks(doc(t), mkcli(a3, b), (pt.COL_XP,))

    # 4. Q9: cột có cổ tức chuỗi chính chưa có số ⇒ CHẶN; render in đúng 'chưa có số (lý do)', ô giá giữ số
    bad = [dict(x) for x in series]
    bad[60]["n_members"] = 50
    g4 = json.loads(json.dumps(npr.compute_period_returns("ZaloPay", rd, rows, inc, [], benchmark=bm_fn(bad))))
    tg = pt.render(g4, None)
    ok("chưa có số (G4" in tg and pt.fmt_num(g4["inception"]["benchmark"]["vnindex_price_pct"], "%") in tg,
       f"render G4:\n{tg}")
    blocks(doc(tg), mkcli(g4, None), ("Q9", "G4"))
    # 4b. thay số giá vào cột có cổ tức (rơi im lặng) ⇒ chặn
    tsub = replace_cell(doc(tg), "Từ khi bắt đầu", pt.COL_TR,
                        pt.fmt_num(g4["inception"]["benchmark"]["vnindex_price_pct"], "%"))
    blocks(tsub, mkcli(g4, None), ("KHÔNG thay bằng số khác",))

    # 5. chuỗi b: CLI rc=3 unavailable ⇒ dòng b 'chưa có số' qua; dòng b ghi số ⇒ chặn
    un = {"account": "ZaloPay", "report_date": rd.isoformat(), "series": "bot", "status": "unavailable",
          "reason": "chưa có nav_sleeve_history_ZaloPay.csv"}
    tu = pt.render(a, un)
    ok(tu.count("chưa có số (chưa có nav_sleeve_history") == 15, f"5 ô × 3 dòng b:\n{tu}")
    ok("(b) wtd: chưa có số" in passes(doc(tu), mkcli(a, un, sleeve_rc=3)), "b chưa có số ⇒ qua")
    blocks(doc(t), mkcli(a, un, sleeve_rc=3), ("chưa có số", "nav_sleeve_history"))
    # 5b. chuỗi b có số nhưng ô có cổ tức của b chưa có số ⇒ KHÔNG chặn (số chính thức là a)
    bg = copy.deepcopy(b)
    for k in ("wtd", "mtd", "inception"):
        bg[k]["benchmark"].update({"vnindex_tr_pct": None, "excess_vs_tr_pp": None, "reason": "G4: giả"})
    passes(doc(pt.render(a, bg)), mkcli(a, bg))

    # 6. thiếu cột có cổ tức: chuỗi đã cài ⇒ chặn; chưa cài ⇒ WARN
    old = ("| Giai đoạn | ZaloPay | VN-Index | Chênh lệch |\n|---|---:|---:|---:|\n"
           "| Từ khi bắt đầu hoạt động (06/07 → 09/10) | −4,91% | −6,82% | +1,91pp |\n")
    blocks(doc(old), cli, ("thiếu cột", pt.COL_TR))
    ok("WARN" in passes(doc(old), cli, installed=False), "định dạng cũ trước khi cài ⇒ WARN")

    # 7. thiếu chú thích cố định ⇒ chặn; cờ Q2 đổi (chú thích khác) ⇒ chặn tới khi bảng render lại
    foot = bm["footnote"]
    blocks(doc(t).replace(foot, ""), cli, ("thiếu chú thích", "tr_net"))
    a4 = copy.deepcopy(a)
    for k in ("wtd", "mtd", "inception"):
        a4[k]["benchmark"]["footnote"] = foot.replace("sau thuế TNCN 5% trên cổ tức", "trước thuế")
    blocks(doc(t), mkcli(a4, b), ("thiếu chú thích",))

    # 8. CLI rc≠0 ⇒ chặn; dòng lạ có số ⇒ chặn, dòng lạ '—' qua
    blocks(doc(t), mkcli(a, b, main_rc=1), ("rc=1", "lỗi giả"))   # rc≠0 dù stdout có JSON
    extra = t.replace("|---|---:|---:|---:|---:|---:|\n",
                      "|---|---:|---:|---:|---:|---:|\n| Từ đầu năm (YTD) | +1,00% | +2,00% | — | — | — |\n")
    blocks(doc(extra), cli, ("Từ đầu năm",))
    extra2 = t.replace("|---|---:|---:|---:|---:|---:|\n",
                       "|---|---:|---:|---:|---:|---:|\n| Từ đầu năm (YTD) | +1,00% | — | — | — | — |\n")
    passes(doc(extra2), cli)

    # 8b. N-a vòng 2: NFD + 'Luỹ kế' vẫn nhận bảng; thiếu bảng khi chuỗi đã cài ⇒ CHẶN (chưa cài ⇒ SKIP);
    #     cột tỉ suất TK + ô WTD/MTD đối chiếu CLI; thiếu dòng kỳ CLI có ⇒ CHẶN; cột 2 sai tên TK ⇒ CHẶN
    import unicodedata
    nfd = unicodedata.normalize("NFD", doc(t).replace("Hiệu suất lũy kế", "Hiệu suất Luỹ kế"))
    ok(nfd != doc(t) and "(b) inception: khớp CLI" in passes(nfd, cli), "NFD + 'Luỹ' ⇒ vẫn đối chiếu")
    notab = "# Báo cáo tuần\n\n### 3.2 Hiệu suất\n\nkhông có bảng\n"
    blocks(notab, cli, ("không có bảng", "bắt buộc có bảng 3.2"))
    sk = pt.check_report("X_weekly.md", notab, "ZaloPay", "2030-06-06", cli=cli, series_installed=lambda: False, recv_fn=_recv_fn)
    ok("SKIP" in sk[0], f"chưa cài chuỗi ⇒ SKIP: {sk}")
    blocks(replace_cell(doc(t), "Tuần này", "ZaloPay", pt.fmt_num(a["wtd"]["return_pct"] + 0.02, "%")), cli,
           ("Tuần này", "'ZaloPay'", f"{a['wtd']['return_pct']:+.3f}"))
    blocks(replace_cell(doc(t), "Từ đầu tháng", pt.COL_PRICE,
                        pt.fmt_num(a["mtd"]["benchmark"]["vnindex_price_pct"] + 0.02, "%")), cli,
           ("Từ đầu tháng", pt.COL_PRICE))
    nomtd = "\n".join(ln for ln in doc(t).splitlines() if not ln.startswith("| Từ đầu tháng")) + "\n"
    blocks(nomtd, cli, ("thiếu dòng", "mtd"))
    blocks(doc(t).replace("| Giai đoạn | ZaloPay |", "| Giai đoạn | SpaceX |"), cli, ("cột 2 tên 'ZaloPay'",))

    # 9. đường nối report_delivery_gate: daily ⇒ không chạy; weekly lệch ⇒ RuntimeError; khớp ⇒ qua
    td = Path(tempfile.mkdtemp(prefix="pt32_sc_"))
    saved, saved_inst = pt.run_cli, pt._series_installed
    calls = []

    def fake(account, d, sleeve=False, bin_dir=None):
        calls.append((account, d, sleeve, bin_dir))
        return (0, b, "") if sleeve else (0, a, "")
    try:
        pt.run_cli = fake
        daily = td / "ZaloPay_daily_report_2026-10-09.md"
        daily.write_text(t2, encoding="utf-8")
        rdg._check_benchmark_table(daily)
        ok(calls == [], "daily không có bảng này ⇒ cổng không chạy")
        wk = td / "ZaloPay_weekly_report_2026-10-05_to_2026-10-09.md"
        wk.write_text(t2, encoding="utf-8")
        try:
            rdg._check_benchmark_table(wk)
            ok(False, "weekly lệch ô phải RuntimeError")
        except RuntimeError as e:
            ok("benchmark-table BLOCK" in str(e), f"{e}")
        ok(calls[0][:3] == ("ZaloPay", "2026-10-09", False) and calls[0][3] == str(rdg.ROOT / "bin"),
           f"cổng gọi CLI của cây canonical với report-date từ tên file: {calls[0]}")
        mo = td / "SpaceX_monthly_report_2026-09.md"
        mo.write_text(doc(pt.render(dict(a, account="SpaceX"), None)), encoding="utf-8")
        rdg._check_benchmark_table(mo)
        ok(calls[-1][:3] == ("SpaceX", "2026-09-30", False), f"monthly ⇒ ngày cuối tháng: {calls[-1]}")
        # N-e vòng 2: báo cáo gộp SpaceX_ZaloPay_* — mỗi TK một bảng; thiếu bảng của 1 TK ⇒ chặn
        sa = pt.render(dict(a, account="SpaceX"), None)
        both = td / "SpaceX_ZaloPay_weekly_report_2026-10-05_to_2026-10-09.md"
        both.write_text(doc(sa) + doc(pt.render(a, b)), encoding="utf-8")
        del calls[:]
        rdg._check_benchmark_table(both)
        ok({c[0] for c in calls} == {"SpaceX", "ZaloPay"}, f"gộp ⇒ đối chiếu cả 2 TK: {calls}")
        both.write_text(doc(sa), encoding="utf-8")
        pt._series_installed = lambda: True
        try:
            rdg._check_benchmark_table(both)
            ok(False, "gộp thiếu bảng ZaloPay phải RuntimeError")
        except RuntimeError as e:
            ok("ZaloPay" in str(e) and "không có bảng" in str(e), f"{e}")
    finally:
        pt.run_cli, pt._series_installed = saved, saved_inst
    src = Path(rdg.__file__).read_text(encoding="utf-8")
    ok(src.count("_check_benchmark_table(report)") == 1
       and src.index("_check_period_returns(report)\n") < src.index("_check_benchmark_table(report)"),
       "deliver() phải gọi cổng bảng ngay sau cổng period-return")
    # 9. Luồng B2 (13/11): cột "gửi tiết kiệm" — khớp CLI ±0,005 + excess = TWR − hurdle; template chưa đổi
    #    (bảng không có cột này ⇒ phần trên không đổi hành vi). Dương: khớp; âm: lệch số / thiếu khối CLI.
    CS, CX = pt.COL_SAV, pt.COL_SAVX
    asv = copy.deepcopy(a)
    for k, _ in pt.PERIODS:
        if asv.get(k):
            hv = round(0.37 + 0.11 * len(k), 3)
            asv[k]["savings"] = {"hurdle_pct": hv, "excess_vs_savings_pp": round(asv[k]["return_pct"] - hv, 3),
                                 "status": "ok", "anchor_warning": "Cảnh báo neo giả."}
    ts = pt.render(asv, None)                                   # B3: render TỰ phát cột + nhãn + cảnh báo
    ok(CS in ts and CX in ts and pt.SAV_LABEL in ts and pt.SAV_WARN in ts, "B3: render có cột + nhãn + cảnh báo")
    ok("Cảnh báo neo giả." in ts, "B3: render in anchor_warning của CLI")
    ok("chưa tính thuế" not in ts, "B3: không còn câu 'chưa tính thuế' cũ trong bảng render")
    ok(CS not in pt.render(a, None) and pt.SAV_LABEL not in pt.render(a, None),
       "B3: CLI không phát savings ⇒ bảng KHÔNG có cột/nhãn tiết kiệm (hành vi cũ)")
    ok("inception: khớp CLI" in passes(doc(ts), mkcli(asv, b)), "B2 dương: cột tiết kiệm khớp CLI")
    ok("khớp" in passes(doc(pt.render(a, None)), mkcli(asv, b)), "B2: bảng KHÔNG có cột tiết kiệm ⇒ không đổi hành vi")
    def bump(col, d):
        return replace_cell(doc(ts), "Từ khi bắt đầu", col, pt.fmt_num(
            asv["inception"]["savings"]["hurdle_pct" if col == CS else "excess_vs_savings_pp"] + d,
            "%" if col == CS else "pp"))
    blocks(bump(CS, 0.02), mkcli(asv, b), (CS,))                # hurdle lệch
    blocks(bump(CX, 0.02), mkcli(asv, b), (CX,))                # excess lệch
    a_ok = copy.deepcopy(asv)
    a_ok["inception"]["savings"]["hurdle_pct"] += 0.004                  # ⩽ 0,005 vẫn qua
    a_ok["inception"]["savings"]["excess_vs_savings_pp"] -= 0.004
    passes(doc(ts), mkcli(a_ok, b))
    a_bad = copy.deepcopy(asv)
    a_bad["inception"]["savings"]["hurdle_pct"] += 0.007                 # > 0,005 ⇒ chặn
    blocks(doc(ts), mkcli(a_bad, b), (CS, "lệch"))
    a_nos = copy.deepcopy(asv)
    del a_nos["inception"]["savings"]
    blocks(doc(ts), mkcli(a_nos, b), ("khối `savings`",))                 # CLI không có khối ⇒ chặn
    a_un = copy.deepcopy(asv)
    a_un["inception"]["savings"] = {"hurdle_pct": None, "excess_vs_savings_pp": None, "status": "unavailable"}
    blocks(doc(ts), mkcli(a_un, b), (CS,))                               # CLI không có số mà bảng có số ⇒ chặn
    blocks(bump(CX, 0.02), mkcli(asv, b), (CX,))                         # excess tự bịa
    # B3: nhãn/cảnh báo bắt buộc NGUYÊN VĂN
    blocks(doc(ts.replace(pt.SAV_LABEL, "")), mkcli(asv, b), ("nhãn tiết kiệm",))
    blocks(doc(ts.replace(pt.SAV_WARN, "")), mkcli(asv, b), ("cảnh báo",))
    blocks(doc(ts.replace("miễn thuế TNCN", "chịu thuế TNCN")), mkcli(asv, b), ("nhãn tiết kiệm",))   # sửa chữ nhãn
    # B3 / skeptic B2: cột GIỐNG tiết kiệm nhưng không nhận ra theo tên ⇒ CHẶN (không để lọt khỏi đối chiếu)
    for bad_name in ("Gửi tiet kiem", "Lãi gửi ngân hàng", "Hurdle (tiền gửi)", "Savings", "Lãi tiền gửi 12T"):
        tsx = ts.replace(CS, bad_name)
        blocks(doc(tsx), mkcli(asv, b), (bad_name,))
    # mọi cột render() phát ra đều được cổng phân loại (không cột "mồ côi" tên lạ)
    hdr = [c.strip() for c in ts.splitlines()[0].strip("|").split("|")]
    ok(all(any(k in pt.strip_accents(c) for k in pt.SAV_LIKE) is False or "tiết kiệm" in c for c in hdr),
       "B3: mọi cột giống tiết kiệm trong header render() đều chứa 'tiết kiệm'")
    # sleeve: dòng bot có "—" ở cột tiết kiệm, cổng bỏ qua khi CLI --sleeve bot không có khối savings
    tz = pt.render(asv, b)
    ok("—" in tz and CS in tz, "B3: dòng bot có cột tiết kiệm '—'")
    passes(doc(tz), mkcli(asv, b))

    # ── B4 (13/11): nhãn có điều kiện theo cashDividendReceiving của kỳ ───────────────────────────────
    ALT = pt.SAV_LABEL_ALT
    ok(ALT != pt.SAV_LABEL and "5% cổ tức" not in ALT and "chờ về" in ALT, "B4: biến thể ALT khác V0, không khẳng định 5% đã trừ")
    ok(pt.sav_label_for(0) == pt.SAV_LABEL and pt.sav_label_for(0.0) == pt.SAV_LABEL, "B4: recv=0 ⇒ nhãn V0")
    for v in (1.0, 3_800_000.0, None):
        ok(pt.sav_label_for(v) == ALT, f"B4: recv={v!r} ⇒ nhãn ALT (không suy ra 0 khi không đọc được)")
    try:
        RECV[0] = 3_800_000.0
        t_alt = pt.render(asv, None)
        ok(ALT in t_alt and pt.SAV_LABEL not in t_alt, "B4: recv≠0 ⇒ render in ALT, không in V0")
        passes(doc(t_alt), mkcli(asv, b))                        # cổng chấp nhận ALT nguyên văn
        blocks(doc(ts), mkcli(asv, b), ("cashDividendReceiving", "3,800,000"))   # V0 khi recv≠0 ⇒ CHẶN
        RECV[0] = None
        blocks(doc(ts), mkcli(asv, b), ("không đọc được",))      # V0 khi không đọc được ⇒ CHẶN
        passes(doc(t_alt), mkcli(asv, b))
        RECV[0] = 0.0
        passes(doc(ts), mkcli(asv, b))                            # V0 khi recv=0 ⇒ qua
        passes(doc(t_alt), mkcli(asv, b))                         # ALT luôn đúng (thận trọng) ⇒ qua
        blocks(doc(t_alt.replace("chưa được trừ", "đã được trừ")), mkcli(asv, b), ("nhãn tiết kiệm",))   # sửa chữ ALT
        blocks(doc(ts.replace(pt.SAV_LABEL, "").replace(ALT, "")), mkcli(asv, b), ("nhãn tiết kiệm",))
    finally:
        RECV[0] = 0.0
    # đọc THẬT (hàm gốc) trên thư mục giả: lọc account_no, lấy bản ghi balances CUỐI ngày, thiếu ⇒ None
    import json as _j, tempfile as _t
    with _t.TemporaryDirectory() as td:
        inc = Path(td) / "inc.json"
        inc.write_text(_j.dumps({"A1": {"account_no": "111"}, "A2": {"account_no": "222"}}), encoding="utf-8")
        (Path(td) / "dnse_raw_2030-06-06.jsonl").write_text("\n".join(_j.dumps(r) for r in [
            {"account_no": "111", "kind": "balances", "ts": "t1", "payload": {"stock": {"cashDividendReceiving": 5}}},
            {"account_no": "222", "kind": "balances", "ts": "t2", "payload": {"stock": {"cashDividendReceiving": 900}}},
            {"account_no": "111", "kind": "balances", "ts": "t3", "payload": {"stock": {"cashDividendReceiving": 0}}},
            {"account_no": "111", "kind": "orders", "ts": "t4", "payload": {}}]), encoding="utf-8")
        g = lambda acc, d: _real_div_receiving(acc, d, exec_dir=td, inception_path=str(inc))  # noqa: E731
        ok(g("A1", "2030-06-06") == 0.0, "B4: lấy bản ghi balances CUỐI của đúng account (A1=0, bỏ A2=900)")
        ok(g("A2", "2030-06-06") == 900.0, "B4: account khác ⇒ số khác (§12)")
        ok(g("A1", "2030-06-07") is None, "B4: thiếu file ngày ⇒ None (không suy ra 0)")
        ok(g("A3", "2030-06-06") is None, "B4: account không có mốc ⇒ None")

    print(f"OK — {N_OK} assertion PASS (period_table_32_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
