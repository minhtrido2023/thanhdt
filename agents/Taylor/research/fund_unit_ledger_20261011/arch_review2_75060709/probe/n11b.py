import sys, os, csv, json, tempfile, traceback
os.environ["MIKE_BOT_TEST_MODE"] = "1"
sys.path.insert(0, "/tmp/ar2/WC/mike/bin")
import daily_nav_snapshot as dns
hist = list(csv.DictReader(open("/tmp/ar2/WC/data/execution_logs/nav_history_SpaceX.csv")))
def trial(label, flows_obj=None, inception=None, hist_rows=None, raw_text=None, account="SpaceX", date="2026-10-09"):
    p = tempfile.mktemp(suffix=".json", dir="/tmp/ar2")
    if raw_text is not None: open(p, "w").write(raw_text)
    elif flows_obj is not None: json.dump(flows_obj, open(p, "w"))
    os.environ["ACCOUNT_CASH_FLOWS_PATH"] = p
    try:
        perf, err = dns.unit_price_performance(account, date, hist_rows or hist, inception=inception)
        paren, lines = dns.nav_performance_lines(-643220.0, perf, err)
        print(f"[{label}] OK-handled: ({paren[:110]}) | {lines[0][:200]}" + (f" | +{len(lines)-1} dòng: {lines[1][:150]}" if len(lines) > 1 else ""))
    except Exception as e:
        print(f"[{label}] *** THOÁT RA NGOÀI (dòng nav_history ĐÃ ghi, rc=1, không in 💰): {type(e).__name__}: {e}")
    finally:
        if os.path.exists(p): os.remove(p)
        os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)
G = {"evidence": "x", "kind": "deposit", "amount_vnd": 5e7}
trial("flows rỗng", {"SpaceX": []})
trial("thiếu file flows")                                  # path không tồn tại
trial("JSON hỏng", raw_text="{not json")
trial("JSON là list", raw_text="[]")
trial("flow thiếu time_ict", {"SpaceX": [dict(G, date="2026-10-05")]})
trial("flow date=null", {"SpaceX": [dict(G, date=None, time_ict="10:00")]})
trial("flow date=20261005 (số)", {"SpaceX": [dict(G, date=20261005, time_ict="10:00")]})
trial("flow amount là list", {"SpaceX": [dict(G, date="2026-10-05", time_ict="10:00", amount_vnd=[1])]})
trial("flow amount NaN", raw_text='{"SpaceX":[{"date":"2026-10-05","time_ict":"10:00","amount_vnd":NaN,"kind":"deposit","evidence":"x"}]}')
trial("flow amount Infinity", raw_text='{"SpaceX":[{"date":"2026-10-05","time_ict":"10:00","amount_vnd":Infinity,"kind":"deposit","evidence":"x"}]}')
trial("flow amount 1e400", raw_text='{"SpaceX":[{"date":"2026-10-05","time_ict":"10:00","amount_vnd":1e400,"kind":"deposit","evidence":"x"}]}')
trial("flow timing=[] ", {"SpaceX": [dict(G, date="2026-10-05", time_ict="10:00", timing=[])]})
trial("flow kind=[] ", {"SpaceX": [dict(G, date="2026-10-05", time_ict="10:00", kind=[])]})
trial("flow hợp lệ 10:00 05/10", {"SpaceX": [dict(G, date="2026-10-05", time_ict="10:00")]})
trial("flow hợp lệ 20:00 09/10 (treo)", {"SpaceX": [dict(G, date="2026-10-09", time_ict="20:00")]})
trial("flow rút 990tr 10:00 05/10", {"SpaceX": [dict(G, kind="withdraw", amount_vnd=-990e6, date="2026-10-05", time_ict="10:00")]})
trial("flow rút 2 tỷ 10:00 05/10", {"SpaceX": [dict(G, kind="withdraw", amount_vnd=-2e9, date="2026-10-05", time_ict="10:00")]})
trial("flow trong cửa sổ 08-24", {"SpaceX": [dict(G, date="2026-08-24", time_ict="10:00")]})
trial("inception_date=None", {"SpaceX": []}, inception={"inception_date": None, "starting_capital": 1e9})
trial("inception starting_capital='abc'", {"SpaceX": []}, inception={"inception_date": "2026-07-01", "starting_capital": "abc"})
trial("inception starting_capital=[1]", {"SpaceX": []}, inception={"inception_date": "2026-07-01", "starting_capital": [1]})
trial("inception là list", {"SpaceX": []}, inception=["x"])
trial("account lạ (không có trong inception)", {"NewAcct": []}, account="NewAcct")
trial("hist có balance_ts hỏng + flow", {"SpaceX": [dict(G, date="2026-10-05", time_ict="10:00")]}, hist_rows=[dict(r, balance_ts="garbage") for r in hist])
trial("hist có nav='abc'", {"SpaceX": []}, hist_rows=hist[:-1] + [dict(hist[-1], nav="abc")])
trial("hist có date sai dạng", {"SpaceX": []}, hist_rows=hist[:-1] + [dict(hist[-1], date="2026/10/09")])
trial("date trước inception", {"SpaceX": []}, date="2026-06-30")
trial("entry account là dict", {"SpaceX": {}})
trial("bản ghi là chuỗi", {"SpaceX": ["x"]})
