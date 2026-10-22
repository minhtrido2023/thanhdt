"""Probe: dựng lại (write=False) trên bản sao chuỗi, so dòng dựng lại vs dòng sealed giữ byte, và kiểm tail chain từ đâu."""
import sys, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import vnindex_total_return as v
cap = {}
orig = v.append_series
def spy(path, rebuilt, write=True):
    cap["rebuilt"] = [dict(r) for r in rebuilt]
    return orig(path, rebuilt, write=False)
v.append_series = spy
res = v.update(series_path=sys.argv[1], write=False)
print(json.dumps(res))
old = {r["date"].isoformat(): r for r in v.read_series(sys.argv[1])}
for r in cap["rebuilt"]:
    o = old.get(r["date"])
    if o is None: print(r["date"], "NEW"); continue
    print(r["date"], o["status"], "n", o["n_members"], "->", r["n_members"],
          "y", o["y_gross"], "->", r["y_gross"],
          "trg_rel %.3e" % (float(r["tr_gross"]) / o["tr_gross"] - 1))
