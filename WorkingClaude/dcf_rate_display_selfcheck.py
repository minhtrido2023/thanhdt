# -*- coding: utf-8 -*-
"""Selfcheck dcf_rate_display (job Taylor_20261102_015334): 2 dòng hiển thị, fail-closed, mutation.
Chạy: python3 dcf_rate_display_selfcheck.py [--mutate]  (--mutate: tự phá nhiều chỗ, mỗi chỗ PHẢI làm test đỏ)"""
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
    L = mod.rstar_line("2026-11-02", cp, None)
    ok("15.1%" in L and "DISPLAY-ONLY" in L and "KHÔNG phải tín hiệu" in L, "rstar fresh: " + L)
    ok("đỉnh 2022 15.9%" in L and "đáy 2022–23 12.1%" in L, "peak/trough")
    ok("percentile 99%" in L, "giá trị percentile (153/154 ≤ hiện tại): " + L)
    ok("lịch sử 2014-01→2026-10" in L, "cắt HIST_START (2013-12=30 không được lọt vào): " + L)
    ok("r hằng 11.00%" in L, "r_const lấy từ cache, không hardcode: " + L)
    ok(mod._NA in mod.rstar_line("2026-12-31", cp, None), "cache stale -> NA")
    ok(mod._NA in mod.rstar_line("2026-10-01", cp, None), "asof trước panel -> NA")
    ok(mod._NA in mod.rstar_line("2026-11-02", os.path.join(d, "nope.json"), None), "cache thiếu -> NA")
    open(cp, "w").write("{bad")
    ok(mod._NA in mod.rstar_line("2026-11-02", cp, None), "cache hỏng -> NA")
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
    ok(len(mod.dcf_rate_lines("2026-11-02", cp, mk(rows), None)) == 2, "đúng 2 dòng")
    # --- vòng 3: ghim percentile giữa dải, cửa sổ Δ12T, biên stale TPCP (arch-review vòng 2)
    mid = {str(p): (10.0 + i * 0.01 if i < 77 else 16.0 + i * 0.01)
           for i, p in enumerate(pd.period_range("2014-01", "2026-09", freq="M"))}
    mid["2013-12"] = 30.0; mid["2026-10"] = 15.0
    mid = dict(sorted(mid.items())); cp2 = os.path.join(d, "mid.json")
    json.dump({"panel_asof": "2026-10-30", "n_last": 147, "r_const": 12.25, "series": mid}, open(cp2, "w"))
    LM = mod.rstar_line("2026-11-02", cp2, None)
    ok("percentile 51%" in LM, "percentile giữa dải = 78/154 = 50.6% -> 51 (diệt <, bỏ dòng cuối, gồm 2013-12): " + LM)
    # --- A': cache untracked mới hơn được ưu tiên; cũ hơn/hỏng/thiếu thì không
    newer = dict(mid); newer["2026-11"] = 17.7; newer = dict(sorted(newer.items())); cpn = os.path.join(d, "new.json")
    json.dump({"panel_asof": "2026-11-30", "n_last": 150, "r_const": 12.25, "series": newer}, open(cpn, "w"))
    ok("17.7%" in mod.rstar_line("2026-12-05", cp2, cpn), "cache live mới hơn thắng tracked: " + mod.rstar_line("2026-12-05", cp2, cpn))
    ok("17.7%" in mod.rstar_line("2026-12-05", cpn, cp2), "thứ tự tham số không ảnh hưởng")
    ok("15.0%" in mod.rstar_line("2026-11-02", cp2, os.path.join(d, "x.json")), "live thiếu -> dùng tracked")
    open(os.path.join(d, "bad.json"), "w").write("{bad")
    ok("15.0%" in mod.rstar_line("2026-11-02", cp2, os.path.join(d, "bad.json")), "live hỏng -> dùng tracked, không NA")
    old = dict(mid); old2 = os.path.join(d, "old.json")
    json.dump({"panel_asof": "2026-09-30", "n_last": 1, "r_const": 12.25, "series": {**old, "2026-10": 9.9}}, open(old2, "w"))
    ok("9.9%" not in mod.rstar_line("2026-11-02", cp2, old2), "live CŨ hơn tracked không ghi đè")
    ok(mod._NA in mod.rstar_line("2027-03-01", cp2, cpn), "cache newest cũng bị fail-closed 45 ngày")
    def one(prev_rows, asof="2026-11-02"):
        return mod.tpcp_line(asof, mk(prev_rows + [("2026-10-30", 4.58, None)]))
    ok("Δ12T +0.68pp" in one([("2025-10-27", 3.9, None)]), "mốc 12T lệch -3 ngày VẪN trong cửa sổ: " + one([("2025-10-27", 3.9, None)]))
    ok("Δ12T: không có dữ liệu" in one([("2025-10-22", 3.9, None)]), "mốc lệch -8 ngày ngoài cửa sổ -> NA")
    T4 = one([("2025-10-24", 3.0, None), ("2025-10-29", 3.9, None)])
    ok("Δ12T +0.68pp" in T4 and "@2025-10-29" in T4, "2 dòng trong cửa sổ: lấy dòng GẦN mốc nhất, không phải đầu: " + T4)
    ok("4.58%" in one([], "2026-11-06"), "biên stale: age=7 vẫn hiển thị")
    ok(mod._NA in one([], "2026-11-07") and "4.58" not in one([], "2026-11-07"), "biên stale: age=8 -> NA")
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
                ("TPCP_MAX_AGE_DAYS = 7", "TPCP_MAX_AGE_DAYS = 10"),
                ("RSTAR_MAX_AGE_DAYS = 45", "RSTAR_MAX_AGE_DAYS = 99999"),
                ("last.v - pv.v:+.2f", "pv.v - last.v:+.2f"),
                ("return f\"r* thị trường: {_NA} ({type(e).__name__})\"", "return 'r* thị trường 12.25%'"),
                ("[DISPLAY-ONLY, thước đo hiển thị, KHÔNG phải tín hiệu mua/bán]", ""),
                ("df = df[df.d <= a]", "df = df[df.d <= pd.Timestamp('2099-01-01')]"),
                ("(h <= cur).mean()", "(h >= cur).mean()"),
                ('HIST_START = "2014-01"', 'HIST_START = "2013-12"'),
                ("tgt - pd.Timedelta(days=7)", "tgt - pd.Timedelta(days=400)"),
                ("tgt - pd.Timedelta(days=7)", "tgt - pd.Timedelta(days=0)"),
                ("tgt - pd.Timedelta(days=7)", "tgt - pd.Timedelta(days=29)"),
                ("pv = prev.iloc[-1]", "pv = prev.iloc[0]"),
                ("(h <= cur).mean()", "(h < cur).mean()"),
                ("h = ser.loc[HIST_START:]", "h = ser"),
                ('df = df.dropna(subset=["v"]).copy()', "df = df.copy()"),
                ("if best is None or pa > best[0]:", "if best is None or pa < best[0]:"),
                ("[path] if live_path is None else [path, live_path]", "[path]"),
                ("[path] if live_path is None else [path, live_path]", "[live_path or path]")]
        for a, b in muts:
            assert src.count(a) == 1, "mutation target mất: " + a
            try:
                run_checks(load(src.replace(a, b))); print("SURVIVED (xấu):", a); sys.exit(1)
            except AssertionError as e:
                print("killed:", a[:45], "->", str(e)[:50])
        print("MUTATION: %d/%d killed" % (len(muts), len(muts)))
