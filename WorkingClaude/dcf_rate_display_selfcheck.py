# -*- coding: utf-8 -*-
"""Selfcheck dcf_rate_display (job Taylor_20261102_015334): 2 dòng hiển thị, fail-closed, mutation.
Chạy: python3 dcf_rate_display_selfcheck.py [--mutate]  (--mutate: tự phá 10 chỗ, mỗi chỗ PHẢI làm test đỏ)"""
import json, os, subprocess, sys, tempfile
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "dcf_rate_display.py")


def run_checks(mod):
    n = 0
    def ok(c, m):
        nonlocal n
        assert c, "FAIL: " + m; n += 1
    ser = {str(p): 12.0 + i * 0.01 for i, p in enumerate(pd.period_range("2014-01", "2026-10", freq="M"))}
    ser["2013-12"] = 30.0; ser["2022-12"] = 15.9; ser["2023-08"] = 12.1; ser["2026-10"] = 15.1
    ser = dict(sorted(ser.items()))   # cache thật ghi sort_keys=True
    d = tempfile.mkdtemp(); cp = os.path.join(d, "c.json")
    json.dump({"panel_asof": "2026-10-30", "n_last": 147, "r_const": 11.0, "series": ser}, open(cp, "w"))
    L = mod.rstar_line("2026-11-02", cp)
    ok("15.1%" in L and "DISPLAY-ONLY" in L and "KHÔNG phải tín hiệu" in L, "rstar fresh: " + L)
    ok("đỉnh 2022 15.9%" in L and "đáy 2022–23 12.1%" in L, "peak/trough")
    ok("percentile 99%" in L, "giá trị percentile (153/154 ≤ hiện tại): " + L)
    ok("lịch sử 2014-01→2026-10" in L, "cắt HIST_START (2013-12=30 không được lọt vào): " + L)
    ok("r hằng 11.00%" in L, "r_const lấy từ cache, không hardcode: " + L)
    ok(mod._NA in mod.rstar_line("2026-12-31", cp), "cache stale -> NA")
    ok(mod._NA in mod.rstar_line("2026-10-01", cp), "asof trước panel -> NA")
    ok(mod._NA in mod.rstar_line("2026-11-02", os.path.join(d, "nope.json")), "cache thiếu -> NA")
    open(cp, "w").write("{bad")
    ok(mod._NA in mod.rstar_line("2026-11-02", cp), "cache hỏng -> NA")
    def mk(rows): return lambda a: pd.DataFrame(rows, columns=["d", "v", "f"])
    rows = [("2025-10-30", 3.937, "2026-10-30"), ("2026-10-30", 4.58, "2026-11-01")]
    T = mod.tpcp_line("2026-11-02", mk(rows))
    ok("4.58%" in T and "Δ12T +0.64pp" in T and "UNVERIFIED" in T and "@2026-10-30" in T, "tpcp fresh: " + T)
    ok(mod._NA in mod.tpcp_line("2026-11-20", mk(rows)), "tpcp stale -> NA (khong dien so cu)")
    ok("4.58" not in mod.tpcp_line("2026-11-20", mk(rows)), "stale không lộ số cũ")
    ok(mod._NA in mod.tpcp_line("2026-11-02", mk([])), "tpcp rỗng -> NA")
    T2 = mod.tpcp_line("2026-11-02", mk([("2026-10-30", 4.58, None)]))
    ok("Δ12T: không có dữ liệu" in T2 and "4.58%" in T2, "thiếu mốc 12T: " + T2)
    T3 = mod.tpcp_line("2026-11-02", mk([("2025-09-30", 3.9, None), ("2026-10-30", 4.58, None)]))
    ok("Δ12T: không có dữ liệu" in T3 and "4.58%" in T3, "mốc cách 30 ngày ngoài cửa sổ 7 ngày -> NA: " + T3)
    TN = mod.tpcp_line("2026-11-02", mk([("2026-10-30", None, None)]))
    ok(TN.startswith("TPCP 10Y: " + mod._NA) and "nan" not in TN.lower(), "v NaN -> NA tiền tố, không lộ nan: " + TN)
    TN2 = mod.tpcp_line("2026-11-02", mk([("2025-10-30", 3.9, None), ("2026-10-30", float("nan"), None)]))
    ok("nan" not in TN2.lower() and TN2.startswith("TPCP 10Y: " + mod._NA) and "3.90" not in TN2, "NaN cuối bị bỏ -> quan sát hợp lệ cuối đã stale -> NA, không in nan/số cũ: " + TN2)
    def boom(a): raise RuntimeError("bq down")
    ok(mod._NA in mod.tpcp_line("2026-11-02", boom), "loader lỗi -> NA")
    TF = mod.tpcp_line("2026-11-02", mk(rows + [("2026-11-05", 9.99, "2026-11-06")]))
    ok("9.99" not in TF and "4.58%" in TF, "không dùng quan sát sau asof (PIT): " + TF)
    ok(len(mod.dcf_rate_lines("2026-11-02", cp, mk(rows))) == 2, "đúng 2 dòng")
    return n


def load(src):
    ns = {"__file__": SRC, "__name__": "m"}; exec(compile(src, SRC, "exec"), ns)
    class M: pass
    m = M(); m.__dict__.update(ns); return m


if __name__ == "__main__":
    src = open(SRC).read()
    print("PASS", run_checks(load(src)), "assertions")
    if "--mutate" in sys.argv:
        muts = [("TPCP_MAX_AGE_DAYS = 7", "TPCP_MAX_AGE_DAYS = 9999"),
                ("RSTAR_MAX_AGE_DAYS = 45", "RSTAR_MAX_AGE_DAYS = 99999"),
                ("last.v - pv.v:+.2f", "pv.v - last.v:+.2f"),
                ("return f\"r* thị trường: {_NA} ({type(e).__name__})\"", "return 'r* thị trường 12.25%'"),
                ("[DISPLAY-ONLY, thước đo hiển thị, KHÔNG phải tín hiệu mua/bán]", ""),
                ("df = df[df.d <= a]", "df = df[df.d <= pd.Timestamp('2099-01-01')]"),
                ("(h <= cur).mean()", "(h >= cur).mean()"),
                ('HIST_START = "2014-01"', 'HIST_START = "2013-12"'),
                ("tgt - pd.Timedelta(days=7)", "tgt - pd.Timedelta(days=400)"),
                ('df = df.dropna(subset=["v"]).copy()', "df = df.copy()")]
        for a, b in muts:
            assert src.count(a) == 1, "mutation target mất: " + a
            try:
                run_checks(load(src.replace(a, b))); print("SURVIVED (xấu):", a); sys.exit(1)
            except AssertionError as e:
                print("killed:", a[:45], "->", str(e)[:50])
        print("MUTATION: %d/%d killed" % (len(muts), len(muts)))
