#!/usr/bin/env python3
"""Selfcheck newdeals_season.py (job Taylor_20261117_102211). Không chạm dữ liệu thật: mọi I/O trong thư
mục tạm, nguồn live được tiêm (live_fn/prices_fn/mos_fn/bus_fn).

  python3 newdeals_season_selfcheck.py            # chạy test (rc 0 = PASS)
  python3 newdeals_season_selfcheck.py --mutate   # mutation test: mỗi đột biến PHẢI làm selfcheck FAIL
Chạy cả dưới `env -u TZ` và `TZ=America/New_York` (ngày ICT không được phụ thuộc TZ của host).
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.environ.get("NDS_MODULE_DIR", HERE)


def _load():
    spec = importlib.util.spec_from_file_location("nds_under_test", os.path.join(MOD_DIR, "newdeals_season.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


FAILS = []


def check(cond, name):
    print(("  PASS " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


def fin(rows):
    import pandas as pd
    return pd.DataFrame(rows, columns=["ticker", "time", "quarter"])


WL = [f"T{i:02d}" for i in range(10)]


def t_trigger(m):
    print("[trigger]")
    rows = [(t, "2026-08-10", "2026Q2") for t in WL]
    rows += [(t, "2026-10-25", "2026Q3") for t in WL[:8]]
    rows += [("ZZZ", "2026-10-20", "2026Q3")]
    cov = m.quarter_coverage(fin(rows), WL, "2026-11-17")
    check(cov["quarter"] == "2026Q3" and abs(cov["frac"] - 0.8) < 1e-9, "8/10 phủ ⇒ frac 0,8 quý 2026Q3")
    check(cov["last_fin_date"] == "2026-10-25", "last_fin_date = ngày BCTC mới nhất của watchlist")
    check(m.season_due(cov, {})[0] is True, "80% ⇒ đến hạn")
    rows7 = [(t, "2026-08-10", "2026Q2") for t in WL] + [(t, "2026-10-25", "2026Q3") for t in WL[:7]]
    cov7 = m.quarter_coverage(fin(rows7), WL, "2026-11-17")
    check(abs(cov7["frac"] - 0.7) < 1e-9 and m.season_due(cov7, {})[0] is False, "70% ⇒ CHƯA đến hạn")
    covpit = m.quarter_coverage(fin(rows), WL, "2026-10-01")
    check(covpit["quarter"] == "2026Q2", "PIT: asof trước ngày BCTC Q3 ⇒ vẫn 2026Q2")
    check(m.season_due(cov, {"seasons_done": ["2026Q3"]})[:2] == (False, "2026Q3"), "mùa đã xong ⇒ no-op")
    check(m.season_due(covpit, {"seasons_done": ["2026Q3"]})[2] == "older_than_last_done", "không chạy lùi mùa")


def t_diff_queue(m):
    print("[diff + hàng đợi DD]")
    prev = m.make_snapshot({"A": 2, "B": 3, "C": 2, "D": 3, "E": 3}, {"A": "ACCUMULATE", "C": "STRONG"},
                           ["A", "B", "C", "D", "E"])
    cur = m.make_snapshot({"A": 2, "B": 2, "C": 4, "D": 3, "E": 5}, {"A": "STRONG", "B": "ACCUMULATE"},
                          ["A", "B", "C", "D", "E"])
    ch = m.diff_season(prev, cur)
    check(ch["enter"] == ["B"] and ch["exit"] == ["C"], f"VÀO B / RA C (got {ch['enter']}/{ch['exit']})")
    check({r["ticker"] for r in ch["rerank"]} == {"B", "C", "E"}, "ĐỔI HẠNG B,C,E")
    q = m.build_dd_queue(ch, cur, {}, "2026Q3")
    tk = [i["ticker"] for i in q["items"]]
    check(tk == ["B"], f"RA (C) và tụt xuống 5 (E) không tốn suất DD (got {tk})")

    names = [f"N{i}" for i in range(8)]
    cur2 = m.make_snapshot({t: 2 for t in names}, {"N7": "STRONG"}, names)
    ch2 = {"enter": names, "exit": [], "rerank": []}
    ddx = {"N0": {"dd_date": "2026-11-01", "rev": 1, "bctc_quarter": "2026Q3"},
           "N1": {"dd_date": "2026-08-01", "rev": 1, "bctc_quarter": "2026Q2"}}
    prevq = {"items": [{"ticker": "N6", "status": "deferred_next_season"}]}
    q2 = m.build_dd_queue(ch2, cur2, ddx, "2026Q3", prevq, mos={"N2": 0.3, "N3": 0.1})
    st = {i["ticker"]: i["status"] for i in q2["items"]}
    queued = [i["ticker"] for i in q2["items"] if i["status"] == "queued"]
    check(sum(v == "queued" for v in st.values()) == 5, f"TRẦN 5 mã/mùa (got {queued})")
    check(st["N0"] == "dd_fresh", "DD đúng quý ⇒ dd_fresh, không tốn suất")
    check(st["N1"] != "dd_fresh", "DD quý cũ ⇒ vẫn phải xếp hàng")
    check(queued[:3] == ["N6", "N7", "N2"], f"ưu tiên: dư mùa trước → double-confirm → MoS (got {queued[:3]})")
    check(sum(v == "deferred_next_season" for v in st.values()) == 2, "phần dư = deferred_next_season")


def t_labels(m):
    print("[nhãn DD]")
    idx = m.latest_dd_index([
        {"ticker": "AAA", "dd_date": "2026-08-01", "rev": None, "bctc_quarter": "2026Q2"},
        {"ticker": "BBB", "dd_date": "2026-08-01", "rev": 3, "bctc_quarter": "2026Q2"},
        {"ticker": "BBB", "dd_date": "2026-11-01", "rev": 1, "bctc_quarter": "2026Q3"},
        {"ticker": "BBB", "dd_date": "2026-10-01", "rev": 9, "bctc_quarter": "2026Q2"}])
    check(idx["BBB"]["bctc_quarter"] == "2026Q3", "bản (dd_date, rev) cao nhất thắng")
    md = ("🟢 **AAA** Banking **BUY·ACCUMULATE** R2 ✓✓\n🟢 **BBB** Tech **BUY·STRONG** R2\n"
          "🟢 **CCC** Pharma **BUY·ACCUMULATE** R1\n- **AAA**·STRONG — DCF: N/A\n**Portfolio**: +1%")
    out = m.apply_dd_labels(md, idx, "2026Q3", only={"AAA", "BBB", "CCC"}).split("\n")
    check("⚠️ DD cũ (2026Q2)" in out[0] and "~~ACCUMULATE~~" in out[0], "DD cũ ⇒ cảnh báo + gạch ACCUMULATE")
    check("ACCUMULATE" not in out[0].replace("~~ACCUMULATE~~", ""), "DD cũ ⇒ không còn ACCUMULATE chưa gạch")
    check("~~STRONG~~" in out[3] and "DD cũ" in out[3], "DD cũ ⇒ gạch STRONG ở dòng DC Book")
    check(out[1].endswith("DD asof 2026Q3") and "~~" not in out[1], "DD đúng quý ⇒ 'DD asof 2026Q3', không gạch")
    check(out[2].endswith("DD: chưa có") and "~~" not in out[2], "chưa DD ⇒ nhãn, không gạch")
    check(out[4] == "**Portfolio**: +1%", "dòng không phải mã ⇒ giữ nguyên")
    check("⚠️ DD cũ" in m.apply_dd_labels("**AAA** x", idx, "2026Q4"), "quý mới hơn ⇒ DD 2026Q3 thành cũ")


def t_dcbook(m):
    print("[sổ DC theo mùa]")
    paper = {"meta": {"start_date": "2026-07-06", "entry_price_asof": "2026-06-26", "benchmark_entry": 1871.91},
             "seed_double_confirm_set": [{"ticker": "OLD", "entry_price": 1.0}], "parking": {}}
    new = m.reset_dc_book(paper, "2026Q3", "2026-11-17", {"A": "STRONG", "B": "ACCUMULATE"},
                          {"A": 10.0, "B": 20.0}, 1700.0, "2026-11-16", {"A": 2, "B": 1}, {"A": "X"})
    h = new["meta"]["season_history"]
    check(len(h) == 1 and h[0]["seed_double_confirm_set"][0]["ticker"] == "OLD", "seed cũ vào lịch sử, KHÔNG xoá")
    check([p["ticker"] for p in new["seed_double_confirm_set"]] == ["A", "B"], "seed mới = double-confirm mùa mới")
    check(new["meta"]["benchmark_entry"] == 1700.0 and new["meta"]["start_date"] == "2026-11-17", "mốc mới")
    check(paper["seed_double_confirm_set"][0]["ticker"] == "OLD", "không sửa object đầu vào")
    again = m.reset_dc_book(new, "2026Q3", "2026-11-18", {"Z": "STRONG"}, {"Z": 1.0}, 1.0, "x", {}, {})
    check(again == new, "cùng mùa ⇒ idempotent, không đặt lại")
    try:
        m.reset_dc_book(paper, "2026Q3", "2026-11-17", {"A": "S"}, {}, 1700.0, "d", {}, {})
        check(False, "thiếu giá ⇒ raise")
    except ValueError:
        check(True, "thiếu giá ⇒ raise")


def t_run(m):
    print("[run_refresh end-to-end, thư mục tạm]")
    d = tempfile.mkdtemp(prefix="nds_sc_")
    try:
        P = dict(state_path=f"{d}/state.json", queue_path=f"{d}/queue.json", snap_dir=f"{d}/snap",
                 paper_path=f"{d}/paper.json", log_path=f"{d}/log")
        with open(P["paper_path"], "w") as f:
            json.dump({"meta": {"start_date": "2026-07-06"}, "seed_double_confirm_set":
                       [{"ticker": "T00", "buy_mode": "ACCUMULATE", "entry_price": 5.0}]}, f)
        rows = [(t, "2026-10-25", "2026Q3") for t in WL]
        calls = {"bus": 0, "live": 0}

        def live(a):
            calls["live"] += 1
            return {"T01": "STRONG", "T02": "ACCUMULATE"}, {}

        def bus(season, q, ch):
            calls["bus"] += 1

        kw = dict(wl=WL, fin_df=fin(rows), ratings={t: 2 for t in WL}, live_fn=live,
                  prices_fn=lambda tk: ({t: 10.0 for t in tk}, 1700.0, "2026-11-16"),
                  mos_fn=lambda tk, a: {}, dd_entries=[], bus_fn=bus, **P)
        r0 = m.run_refresh(asof="2026-11-17", rating_asof="2026-10-20", notify_bus=True, **kw)
        check(r0["reason"].startswith("rating_not_fresh") and not os.path.exists(P["state_path"]),
              "rating cũ hơn BCTC ⇒ hoãn, không đánh dấu mùa")
        r1 = m.run_refresh(asof="2026-11-17", rating_asof="2026-11-16", notify_bus=True, **kw)
        st = json.load(open(P["state_path"]))
        check(st["seasons_done"] == ["2026Q3"] and calls["bus"] == 1, "lượt đầu: mùa xong + 1 bus post")
        paper = json.load(open(P["paper_path"]))
        check(paper["meta"]["season"] == "2026Q3" and len(paper["meta"]["season_history"]) == 1,
              "sổ DC đặt lại theo mùa, seed cũ trong lịch sử")
        check(os.path.exists(f"{P['snap_dir']}/2026Q3.json"), "snapshot mùa được lưu")
        r2 = m.run_refresh(asof="2026-11-18", rating_asof="2026-11-17", notify_bus=True, **kw)
        check(r2["reason"] == "season_already_done" and calls["bus"] == 1 and calls["live"] == 1,
              "lượt 2 cùng mùa ⇒ no-op (không tính lại, không post lặp)")
        check(len(json.load(open(P["paper_path"]))["meta"]["season_history"]) == 1, "lượt 2 không đặt lại sổ")
        # bus lỗi ⇒ bus_pending, lượt sau thử lại đúng 1 lần
        shutil.rmtree(d); os.makedirs(d)
        with open(P["paper_path"], "w") as f:
            json.dump({"meta": {}, "seed_double_confirm_set": []}, f)

        def bad_bus(*a):
            raise RuntimeError("bus down")
        kw2 = dict(kw); kw2["bus_fn"] = bad_bus
        try:
            m.run_refresh(asof="2026-11-17", rating_asof="2026-11-16", notify_bus=True, **kw2)
        except RuntimeError:
            pass
        check(json.load(open(P["state_path"])).get("bus_pending") == "2026Q3", "bus lỗi ⇒ bus_pending")
        r3 = m.run_refresh(asof="2026-11-18", rating_asof="2026-11-17", notify_bus=True, **kw)
        check(r3.get("bus_retry") == "2026Q3" and calls["bus"] == 2, "lượt sau post bù đúng 1 lần")
        m.run_refresh(asof="2026-11-19", rating_asof="2026-11-18", notify_bus=True, **kw)
        check(calls["bus"] == 2, "post bù xong ⇒ không post nữa")
        # dry ⇒ không ghi gì
        shutil.rmtree(d); os.makedirs(d)
        with open(P["paper_path"], "w") as f:
            json.dump({"meta": {}, "seed_double_confirm_set": []}, f)
        rd = m.run_refresh(asof="2026-11-17", rating_asof="2026-11-16", dry=True, **kw)
        check(rd.get("dry") and sorted(os.listdir(d)) == ["paper.json"], "--dry ⇒ không ghi file nào")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_fresh_tz(m):
    print("[độ tươi + TZ]")
    exp = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    check(m.today_ict() == exp, f"today_ict = ngày ICT dưới TZ={os.environ.get('TZ', '<unset>')}")
    d = tempfile.mkdtemp(prefix="nds_fr_")
    try:
        line, q = m.freshness_line("2026-11-17", wl=WL, fin_path=f"{d}/x.parquet", rating_csv=f"{d}/r.csv",
                                   dcf_state=f"{d}/s.json", paper_file=f"{d}/p.json")
        check(line.startswith("🧭") and "?" in line and q is None, "thiếu mọi nguồn ⇒ không raise, hiện '?'")
        fin([(t, "2026-10-25", "2026Q3") for t in WL[:9]]).to_parquet(f"{d}/f.parquet")
        open(f"{d}/r.csv", "w").write("ticker,rating\n")
        json.dump({"season_done": ["2026-11-15:full"]}, open(f"{d}/s.json", "w"))
        json.dump({"meta": {"season": "2026Q3", "start_date": "2026-11-10"}}, open(f"{d}/p.json", "w"))
        line, q = m.freshness_line("2026-11-17", wl=WL, fin_path=f"{d}/f.parquet", rating_csv=f"{d}/r.csv",
                                   dcf_state=f"{d}/s.json", paper_file=f"{d}/p.json")
        check(q == "2026Q3" and "9/10" in line and "90%" in line and "2026-11-15:full" in line
              and "(7 ngày)" in line, f"dòng độ tươi đủ 4 phần: {line}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


MUTATIONS = [
    ("stale-compare-flip", "if latest_q and q < latest_q:", "if latest_q and q > latest_q:"),
    ("no-strike", 'line = _MODE_RE.sub(r"~~\\1~~", line) + f"', 'line = line + f"'),
    ("threshold-zero", 'if cov["frac"] < threshold:', 'if cov["frac"] < 0.0:'),
    ("no-idempotency", "    if q in done:\n", "    if False:\n"),
    ("cap-6", "DD_CAP = 5 ", "DD_CAP = 6 "),
    ("dc-reset-not-idempotent", 'if meta.get("season") == season:', "if False:"),
    ("rating-fresh-check-off", 'if cov["last_fin_date"] and (rating_asof or "") < cov["last_fin_date"]:', "if False:"),
    ("pit-off", 'df = df[df["time"] <= pd.Timestamp(asof)]', "df = df"),
    ("history-dropped", "hist.append(", "list("),
]


def mutate():
    src = open(os.path.join(HERE, "newdeals_season.py"), encoding="utf-8").read()
    bad = []
    for name, a, b in MUTATIONS:
        if a not in src:
            print(f"  MUTANT-MISSING {name}: chuỗi gốc không còn trong module"); bad.append(name); continue
        d = tempfile.mkdtemp(prefix="nds_mut_")
        open(os.path.join(d, "newdeals_season.py"), "w", encoding="utf-8").write(src.replace(a, b, 1))
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env={**os.environ, "NDS_MODULE_DIR": d},
                           capture_output=True, text=True)
        shutil.rmtree(d, ignore_errors=True)
        killed = r.returncode != 0
        print(f"  {'KILLED  ' if killed else 'SURVIVED'} {name}")
        if not killed:
            bad.append(name)
    print(f"mutation: {len(MUTATIONS) - len(bad)}/{len(MUTATIONS)} killed")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--mutate" in sys.argv:
        sys.exit(mutate())
    m = _load()
    for t in (t_trigger, t_diff_queue, t_labels, t_dcbook, t_run, t_fresh_tz):
        t(m)
    print(f"{'ALL PASS' if not FAILS else 'FAILED: ' + str(FAILS)}")
    sys.exit(1 if FAILS else 0)
