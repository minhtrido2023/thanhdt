"""Ô None->số: (1) phân theo method mới; (2) chữ ký look-ahead = số mới trùng (<=1 CP) total_after
của một AIS có effective_date VENDOR > asof mà KHÔNG có AIS nào <= asof cùng số; (3) sai số so với
AIS kế tiếp (vendor eff > asof) — mốc kiểm sau-sự-kiện."""
import csv, sys, collections
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from corp_action_lib import bq
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/ais_chain_order_20261019"
R = [r for r in csv.DictReader(open(f"{D}/diff_cells.csv")) if r["kind"] == "none_to_num"]
tks = sorted({r["ticker"] for r in R})
ais = collections.defaultdict(list)
for a in bq("SELECT ticker, CAST(effective_date AS STRING) d, shares_total_after v FROM tav2_bq.corporate_action "
            "WHERE event_code='AIS' AND event_status='executed' AND shares_total_after IS NOT NULL AND effective_date IS NOT NULL AND ticker IN (%s)"
            % ",".join(f"'{t}'" for t in tks)):
    ais[a["ticker"]].append((a["d"], float(a["v"])))
meth = collections.Counter(r["new_method"] for r in R if r["branch"] == "pit" and r["asof"] != "2026-10-19")
la, errs = [], []
for r in R:
    if r["asof"] == "2026-10-19": continue
    v = float(r["new_value"]); A = ais[r["ticker"]]
    past = {x for d, x in A if d <= r["asof"]}
    fut = sorted((d, x) for d, x in A if d > r["asof"])
    if any(abs(x - v) <= 1 for d, x in fut) and not any(abs(x - v) <= 1 for x in past):
        la.append((r["asof"], r["ticker"], v, r["new_method"]))
    if fut:
        errs.append((abs(v / fut[0][1] - 1), r["asof"], r["ticker"], v, fut[0]))
print("PIT none->num ô:", sum(meth.values()), dict(meth))
print("chữ ký look-ahead:", len(la), "theo method", collections.Counter(m for *_, m in la), "mã", sorted({t for _, t, _, _ in la}))
errs.sort()
import statistics
e = [x[0] for x in errs]
print("so với AIS kế tiếp: n", len(e), "median %.4f%%" % (100 * statistics.median(e)), "<=0.1%%: %d" % sum(x <= 0.001 for x in e),
      ">5%%: %d" % sum(x > 0.05 for x in e))
for x in errs[-12:]: print("  lệch lớn", "%.1f%%" % (100 * x[0]), x[1:])

# Tách chữ ký: số mới có lăn qua ISS đã ex <= asof (events_applied) ⇒ lăn hợp lệ, AIS sau chỉ niêm yết TRỄ
import importlib.util
spec = importlib.util.spec_from_file_location("osl_new", "/home/trido/thanhdt/wt-Taylor_20261019_052148/WorkingClaude/oshares_live.py")
NEW = importlib.util.module_from_spec(spec); spec.loader.exec_module(NEW)
q, c = NEW._fetch(sorted({t for _, t, _, _ in la}), "2026-10-19")
cls = collections.Counter()
for asof, tk, v, m in la:
    rec = NEW.oshares_at([tk], asof, _cache=([x for x in q if x["ticker"] == tk], [x for x in c if x["ticker"] == tk]))[tk]
    rolled = bool(rec.get("events_applied"))
    cls[(m, "lăn ISS<=asof" if rolled else "KHÔNG lăn")] += 1
print("chữ ký look-ahead tách:", dict(cls))
