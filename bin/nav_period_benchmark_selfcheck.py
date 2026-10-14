#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho khối `benchmark` + cờ `--sleeve bot` của `nav_period_returns.py` (quỹ bước 4,
SPEC §A5/§B4) — không BQ, không broker, không mạng, không ghi `data/` (file cấu hình ở thư mục tạm).
Chạy dưới `env -u TZ` và một TZ lạ (§16/§19):

    env -u TZ python3 mike/bin/nav_period_benchmark_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/nav_period_benchmark_selfcheck.py
"""
import contextlib
import datetime as dt
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nav_period_returns as npr  # noqa: E402
import nav_sleeve  # noqa: E402
import vnindex_total_return as V  # noqa: E402
from account_cash_flows import NavRow  # noqa: E402
from vnindex_total_return_selfcheck import mk_series, rechain  # noqa: E402

N_OK = 0
NO_ACKS = "/nonexistent/vnindex_tr_acks.json"


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def dump(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def strip_bm(res):
    res = json.loads(json.dumps(res))
    for k in ("inception", "wtd", "mtd", "day"):
        if res.get(k):
            res[k].pop("benchmark", None)
    return res


def fixture():
    """Chuỗi chỉ số 70 phiên (2030) + sổ NAV: 1 dòng TRƯỚC mốc (ca ZaloPay 03/07 ↔ 06/07), mốc D[40],
    dòng D[41..66] + một dòng THỨ BẢY sau D[60]."""
    D, series = mk_series(70)
    series = [dict(r) for r in series]
    for i, r in enumerate(series):            # cổ tức 0,02%/phiên ⇒ tr_gross ≠ tr_net (phân biệt cờ Q2)
        if i:
            r["y_gross"] = 0.0002
    series = rechain(series)                  # chuỗi TR nối được (G1 vòng 2 kiểm điều này)
    # index_anchor_date = phiên TRƯỚC inception_date (ca SpaceX: NAV gốc = số dư sáng ⇒ mốc = đóng cửa hôm trước)
    inc = {"inception_date": D[40].isoformat(), "starting_capital": 1_000_000_000,
           "index_anchor_date": D[39].isoformat()}
    rows = [NavRow(D[38], 990_000_000.0)]
    nav = 1_000_000_000.0
    for i in range(41, 67):
        nav *= 1.0 + (0.002 if i % 3 else -0.003)
        rows.append(NavRow(D[i], round(nav)))
    sat = next(D[60] + dt.timedelta(days=k) for k in range(1, 8) if (D[60] + dt.timedelta(days=k)).weekday() == 5)
    rows.append(NavRow(sat, rows[-1][1]))
    rows.sort(key=lambda r: r[0])
    return D, series, inc, rows, sat


def bm_fn(series, config_path="/nonexistent/benchmark_config.json"):
    return lambda a, b: V.report_benchmark(a, b, series=series, acks_path=NO_ACKS, config_path=config_path)


def pct(series, a, b, col):
    m = {r["date"]: r for r in series}
    return round(100 * (m[b][col] / m[a][col] - 1), 3)


def t_byte_identity_and_anchor(D, series, inc, rows, sat):
    for rd in (D[41], D[45], D[52], D[60], sat, D[66]):
        base = npr.compute_period_returns("SpaceX", rd, rows, inc, [])
        withb = npr.compute_period_returns("SpaceX", rd, rows, inc, [], benchmark=bm_fn(series))
        ok(dump(base) == dump(strip_bm(withb)), f"{rd}: bỏ khối benchmark phải ra ĐÚNG từng byte đầu ra cũ")
        for k in ("inception", "wtd", "mtd", "day"):
            p = withb[k]
            if p is None:
                continue
            bm = p["benchmark"]
            # Mốc chỉ số = ngày dòng sổ làm mốc kỳ — không do người soạn chọn; kỳ neo ở dòng 0 (vốn gốc)
            # dùng index_anchor_date của tài khoản (B1 vòng 2)
            row0 = p["from_date"] == D[40].isoformat()
            want = (inc["index_anchor_date"], "index_anchor_date") if row0 else (p["from_date"], "ledger_row")
            ok((bm["anchor_date"], bm["anchor_source"]) == want and bm["end_date"] == p["to_date"],
               f"{rd}/{k}: anchor {bm['anchor_date']}/{bm.get('anchor_source')}→{bm['end_date']} ≠ {want}"
               f"→{p['to_date']}")
    r = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=bm_fn(series))
    bm = r["inception"]["benchmark"]
    ok(bm["anchor_date"] == D[39].isoformat() and bm["index_anchor_date"] == D[39].isoformat(),
       f"B1: mốc inception phải = index_anchor_date {D[39]} (không phải dòng sổ 0 {D[40]}, không phải "
       f"dòng sổ {D[38]} trước đó): {bm}")
    ok(bm["status"] == "ok", f"chuỗi sạch phải ok: {bm}")
    ok(bm["vnindex_price_pct"] == pct(series, D[39], D[66], "vnindex"), f"giá: {bm}")
    ok(bm["vnindex_tr_gross_pct"] == pct(series, D[39], D[66], "tr_gross"), f"tr_gross: {bm}")
    ok(bm["vnindex_tr_net_pct"] == pct(series, D[39], D[66], "tr_net"), f"tr_net: {bm}")
    # ca ZaloPay: index_anchor_date = inception_date ⇒ mốc = chính dòng sổ 0
    bz = npr.compute_period_returns("ZaloPay", D[66], rows, dict(inc, index_anchor_date=D[40].isoformat()),
                                    [], benchmark=bm_fn(series))["inception"]["benchmark"]
    ok(bz["index_anchor_date"] == D[40].isoformat()
       and bz["vnindex_price_pct"] == pct(series, D[40], D[66], "vnindex"), f"mốc = inception_date: {bz}")
    ok(bm["vnindex_tr_gross_pct"] != bm["vnindex_tr_net_pct"], "fixture phải tách gross/net")
    # Q2 mặc định (user 2026-10-14): cột có cổ tức = tr_net, chú thích nói rõ sau thuế 5%
    ok(bm["tr_kind"] == "tr_net" and bm["vnindex_tr_pct"] == bm["vnindex_tr_net_pct"], f"Q2 mặc định: {bm}")
    ok("sau thuế TNCN 5%" in bm["footnote"], f"chú thích Q2: {bm['footnote']}")
    rp = r["inception"]["return_pct"]
    ok(bm["excess_vs_price_pp"] == round(rp - bm["vnindex_price_pct"], 3)
       and bm["excess_vs_tr_pp"] == round(rp - bm["vnindex_tr_net_pct"], 3), f"chênh: {bm}")


def t_config(D, series, inc, rows):
    tmp = tempfile.mkdtemp(prefix="npr_bench_sc_")
    cfg = os.path.join(tmp, "benchmark_config.json")
    with open(cfg, "w", encoding="utf-8") as f:
        json.dump({"report_tr_kind": "tr_gross"}, f)
    r = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=bm_fn(series, cfg))
    bm = r["inception"]["benchmark"]
    ok(bm["tr_kind"] == "tr_gross" and bm["vnindex_tr_pct"] == bm["vnindex_tr_gross_pct"]
       and "trước thuế" in bm["footnote"], f"cờ Q2 = tr_gross phải đổi cột, không sửa code: {bm}")
    ok(bm["excess_vs_tr_pp"] == round(r["inception"]["return_pct"] - bm["vnindex_tr_gross_pct"], 3),
       f"chênh theo tr_gross: {bm}")
    with open(cfg, "w", encoding="utf-8") as f:
        json.dump({"report_tr_kind": "tr_magic"}, f)
    r2 = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=bm_fn(series, cfg))
    bm = r2["inception"]["benchmark"]
    ok(bm["status"] == "unavailable" and bm["vnindex_tr_pct"] is None and "tr_magic" in bm["reason"],
       f"cờ lạ phải unavailable + trích giá trị đã đọc: {bm}")
    ok(dump(strip_bm(r2)) == dump(strip_bm(r)), "cấu hình hỏng KHÔNG được đổi số danh mục")


def t_unavailable(D, series, inc, rows):
    base = npr.compute_period_returns("SpaceX", D[66], rows, inc, [])
    # (1) không đọc được chuỗi ⇒ mọi ô None + lý do; số danh mục giữ nguyên
    old = V.SERIES_PATH
    try:
        V.SERIES_PATH = "/nonexistent/vnindex_tr_daily.csv"
        r = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=npr._benchmark_fn())
    finally:
        V.SERIES_PATH = old
    bm = r["inception"]["benchmark"]
    ok(bm["status"] == "unavailable" and bm["vnindex_price_pct"] is None and bm["vnindex_tr_pct"] is None
       and "vnindex_tr_daily.csv" in bm["reason"], f"thiếu chuỗi: {bm}")
    ok(bm["excess_vs_price_pp"] is None and bm["excess_vs_tr_pp"] is None, f"thiếu chuỗi ⇒ chênh None: {bm}")
    ok(dump(strip_bm(r)) == dump(base), "thiếu chuỗi KHÔNG đổi số danh mục")
    # (2) cổng phần cổ tức hỏng (G4) ⇒ ô giá có số, ô có cổ tức None — KHÔNG thay bằng giá
    bad = [dict(x) for x in series]
    bad[60]["n_members"] = 50
    bm = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=bm_fn(bad))["inception"]["benchmark"]
    ok(bm["vnindex_price_pct"] is not None and bm["vnindex_tr_pct"] is None and bm["vnindex_tr_net_pct"] is None
       and bm["excess_vs_tr_pp"] is None and bm["excess_vs_price_pp"] is not None and "G4" in bm["reason"],
       f"G4 hỏng: {bm}")
    # (3) phiên cuối của kỳ chưa có trong chuỗi ⇒ G1, cả ô giá None
    bm = npr.compute_period_returns("SpaceX", D[66], rows, inc, [], benchmark=bm_fn(series[:66]))
    bm = bm["inception"]["benchmark"]
    ok(bm["status"] == "unavailable" and bm["vnindex_price_pct"] is None and "G1" in bm["reason"]
       and D[66].isoformat() in bm["reason"], f"G1 phiên cuối: {bm}")


def t_non_session_row(D, series, inc, rows, sat):
    r = npr.compute_period_returns("SpaceX", sat, rows, inc, [], benchmark=bm_fn(series))
    bm = r["day"]["benchmark"]
    fri = max(d for d in D if d < sat)
    ok(bm["end_date"] == sat.isoformat() and bm["index_end_date"] == fri.isoformat()
       and any(sat.isoformat() in n and fri.isoformat() in n for n in bm.get("notes", [])),
       f"dòng sổ ngày nghỉ ⇒ mức chỉ số đóng cửa {fri} + ghi chú: {bm}")
    # kỳ "day" của dòng Thứ Bảy: chỉ số không đổi (cùng phiên) ⇒ 0,000
    ok(bm["vnindex_price_pct"] == 0.0, f"day ngày nghỉ: {bm}")


def t_sleeve(D, series, inc, rows):
    # B5.1: không có phần ngoài bot ⇒ (b) ≡ (a) (trừ field riêng của chuỗi b)
    same = {"rows": [r for r in rows if D[40] < r[0] <= D[66]], "flows": [], "inception_from": D[40],
            "nav0": 1_000_000_000.0, "outside_scope": [], "outside0_vnd": 0}
    orig = nav_sleeve.sleeve_inputs_for_report
    try:
        nav_sleeve.sleeve_inputs_for_report = lambda *a, **k: same
        b = npr.compute_sleeve_period_returns("ZaloPay", D[66], rows, inc, [], benchmark=bm_fn(series))
        a = npr.compute_period_returns("ZaloPay", D[66], rows, inc, [], benchmark=bm_fn(series))
        ok(b["series"] == "bot" and b["outside_scope"] == [] and b["outside_at_inception_vnd"] == 0, f"field b: {b}")
        bb = {k: v for k, v in b.items() if k not in ("series", "outside_scope", "outside_at_inception_vnd")}
        ok(dump(bb) == dump(a), "không có phần ngoài bot ⇒ (b) ≡ (a) từng byte")
        ok(b["inception"]["benchmark"]["anchor_date"] == inc["index_anchor_date"],
           "mốc chỉ số chuỗi b = index_anchor_date của tài khoản")
        # chưa có dòng nào ⇒ SleeveUnavailable (không phải kết quả rỗng)
        empty = dict(same, rows=[])
        nav_sleeve.sleeve_inputs_for_report = lambda *a, **k: empty
        try:
            npr.compute_sleeve_period_returns("ZaloPay", D[66], rows, inc, [], benchmark=bm_fn(series))
            ok(False, "chuỗi b rỗng phải ném SleeveUnavailable")
        except nav_sleeve.SleeveUnavailable as e:
            ok(str(D[40]) in str(e), f"thông điệp trích mốc: {e}")
    finally:
        nav_sleeve.sleeve_inputs_for_report = orig


def t_cli(D, series, inc, rows):
    """`main()` — đường `--sleeve bot` không có số ⇒ rc=3 + JSON `unavailable`; không cờ ⇒ chuỗi a."""
    saved = (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn,
             nav_sleeve.sleeve_inputs_for_report, sys.argv)

    def unavailable(*a, **k):
        raise nav_sleeve.SleeveUnavailable("chưa có nav_sleeve_history_ZaloPay.csv (chuỗi b chưa được dựng)")
    try:
        npr.load_nav_history = lambda acc: rows
        npr.load_inception = lambda acc: inc
        npr.load_flows = lambda acc, require_file=False: []
        npr._benchmark_fn = lambda: bm_fn(series)
        nav_sleeve.sleeve_inputs_for_report = unavailable
        out, err = io.StringIO(), io.StringIO()
        sys.argv = ["nav_period_returns.py", "--account", "ZaloPay", "--report-date", D[66].isoformat(),
                    "--sleeve", "bot"]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = npr.main()
        j = json.loads(out.getvalue())
        ok(rc == 3 and j["status"] == "unavailable" and j["series"] == "bot" and "chưa được dựng" in j["reason"],
           f"--sleeve bot không có số: rc={rc} {out.getvalue()}")
        out = io.StringIO()
        sys.argv = ["nav_period_returns.py", "--account", "ZaloPay", "--report-date", D[66].isoformat()]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = npr.main()
        j = json.loads(out.getvalue())
        ok(rc == 0 and "series" not in j and j["inception"]["benchmark"]["status"] == "ok",
           f"không cờ ⇒ chuỗi a có benchmark: rc={rc}")
    finally:
        (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn,
         nav_sleeve.sleeve_inputs_for_report, sys.argv) = saved


def t_index_anchor_field(D, series, inc, rows):
    """B1: thiếu/hỏng `index_anchor_date` ⇒ ValueError (CLI rc=1 + lý do), KHÔNG rơi về dòng sổ 0.
    Không truyền benchmark ⇒ không đòi trường (đầu ra cũ giữ nguyên byte)."""
    bad = {k: v for k, v in inc.items() if k != "index_anchor_date"}
    ok(dump(npr.compute_period_returns("SpaceX", D[66], rows, bad, []))
       == dump(npr.compute_period_returns("SpaceX", D[66], rows, inc, [])),
       "không benchmark ⇒ không cần index_anchor_date")
    for name, v, must in (("thiếu", None, "thiếu 'index_anchor_date'"),
                          ("sau inception", D[41].isoformat(), "phải trong"),
                          ("quá sớm", (D[40] - dt.timedelta(days=15)).isoformat(), "phải trong"),
                          ("không phải ngày", "30/06/2026", "không phải YYYY-MM-DD")):
        cfg = dict(bad) if v is None else dict(bad, index_anchor_date=v)
        try:
            npr.compute_period_returns("SpaceX", D[66], rows, cfg, [], benchmark=bm_fn(series))
            ok(False, f"index_anchor_date {name} phải ValueError")
        except ValueError as e:
            ok(must in str(e), f"{name}: {e}")
    saved = (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn, sys.argv)
    try:
        npr.load_nav_history = lambda acc: rows
        npr.load_inception = lambda acc: bad
        npr.load_flows = lambda acc, require_file=False: []
        npr._benchmark_fn = lambda: bm_fn(series)
        out, err = io.StringIO(), io.StringIO()
        sys.argv = ["nav_period_returns.py", "--account", "SpaceX", "--report-date", D[66].isoformat()]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = npr.main()
        ok(rc == 1 and out.getvalue() == "" and "index_anchor_date" in err.getvalue(),
           f"CLI thiếu index_anchor_date: rc={rc} stdout={out.getvalue()[:80]!r} stderr={err.getvalue()!r}")
    finally:
        (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn, sys.argv) = saved


def t_cli_sleeve_files(D, series, inc, rows):
    """B2 (arch-review vòng 1 #2): file phạm vi/chuyển giao THIẾU hoặc HỎNG ⇒ `--sleeve bot` rc=3 +
    JSON `unavailable` + lý do trích lỗi thật — KHÔNG traceback rc=1 (rc=1 làm cổng chặn cả báo cáo)."""
    import functools
    tmp = tempfile.mkdtemp(prefix="npr_sleeve_files_sc_")
    scope_ok = os.path.join(tmp, "scope_ok.json")
    with open(scope_ok, "w", encoding="utf-8") as f:
        json.dump({"ZaloPay": [{"ticker": "DGC", "from": D[40].isoformat()}]}, f)
    md5 = nav_sleeve.scope_md5(nav_sleeve.load_scope("ZaloPay", scope_ok))
    with open(nav_sleeve.history_path("ZaloPay", tmp), "w", encoding="utf-8") as f:
        f.write(f"date,scope_md5\n{D[40].isoformat()},{md5}\n")

    def put(name, text):
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p
    cases = [  # (tên, scope_path, transfers_path, report_date, chuỗi phải có trong lý do)
        ("thiếu sleeve_scope.json", os.path.join(tmp, "absent_scope.json"), "/nonexistent/t.json",
         D[66], "absent_scope.json"),
        ("sleeve_scope.json JSON hỏng", put("bad_scope.json", '{"ZaloPay": [{"ticker": "DGC",'),
         "/nonexistent/t.json", D[66], "JSONDecodeError"),
        ("scope rỗng", put("empty_scope.json", '{"ZaloPay": []}'), "/nonexistent/t.json", D[66],
         "không có mục trong sleeve_scope.json"),
        ("scope thiếu 'from'", put("nofrom_scope.json", '{"ZaloPay": [{"ticker": "DGC"}]}'),
         "/nonexistent/t.json", D[66], "thiếu ticker/from"),
        # report_date = mốc ⇒ không dòng nào cần lịch sử b ⇒ tới bước đọc transfers
        ("sleeve_transfers.json JSON hỏng", scope_ok, put("bad_tr.json", '{"ZaloPay": [{'), D[40],
         "JSONDecodeError"),
        ("sleeve_transfers.json thiếu trường", scope_ok,
         put("miss_tr.json", '{"ZaloPay": [{"proposal_id": "p1", "source": "dividend"}]}'), D[40],
         "thiếu 'ticker'"),
    ]
    saved = (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn,
             nav_sleeve.sleeve_inputs_for_report, sys.argv)
    orig = nav_sleeve.sleeve_inputs_for_report
    try:
        npr.load_nav_history = lambda acc: rows
        npr.load_inception = lambda acc: inc
        npr.load_flows = lambda acc, require_file=False: []
        npr._benchmark_fn = lambda: bm_fn(series)
        for name, sp, tp, rd, must in cases:
            nav_sleeve.sleeve_inputs_for_report = functools.partial(
                orig, exec_dir=tmp, scope_path=sp, transfers_path=tp, seed_path="/nonexistent/seed.json")
            out, err = io.StringIO(), io.StringIO()
            sys.argv = ["nav_period_returns.py", "--account", "ZaloPay", "--report-date", rd.isoformat(),
                        "--sleeve", "bot"]
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = npr.main()
            j = json.loads(out.getvalue())
            ok(rc == 3 and j["status"] == "unavailable" and must in j["reason"]
               and "chưa có số" in err.getvalue() and "Traceback" not in err.getvalue(),
               f"B2 {name}: rc={rc} (phải 3), reason={j.get('reason')!r} (phải chứa {must!r}), "
               f"stderr={err.getvalue()[-300:]!r}")
    finally:
        (npr.load_nav_history, npr.load_inception, npr.load_flows, npr._benchmark_fn,
         nav_sleeve.sleeve_inputs_for_report, sys.argv) = saved


def main() -> int:
    D, series, inc, rows, sat = fixture()
    t_byte_identity_and_anchor(D, series, inc, rows, sat)
    t_config(D, series, inc, rows)
    t_unavailable(D, series, inc, rows)
    t_non_session_row(D, series, inc, rows, sat)
    t_sleeve(D, series, inc, rows)
    t_cli(D, series, inc, rows)
    t_cli_sleeve_files(D, series, inc, rows)
    t_index_anchor_field(D, series, inc, rows)
    print(f"OK — {N_OK} assertion PASS (nav_period_benchmark_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
