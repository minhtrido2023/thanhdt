import os, sys, json, importlib.util, collections
WT = "/home/trido/thanhdt/wt-erp-domestic-dcf-20261030/WorkingClaude"
spec = importlib.util.spec_from_file_location("dcf_valuation", os.path.join(WT, "dcf_valuation.py"))
D = importlib.util.module_from_spec(spec); sys.modules["dcf_valuation"] = D; spec.loader.exec_module(D)
sys.path.insert(0, WT)
from trading_bot import strategies as S
import pandas as pd
print("strategies:", S.__file__, file=sys.stderr)
tk = pd.read_csv(sys.argv[1]).ticker.dropna().unique().tolist()
asof = "2026-10-29"
out = {}
for t in tk:
    px = D.latest_price(t, asof)
    d = S._dcf_check_for_order(t, px, asof)
    out[t] = (d["status"], d.get("robust"), d.get("reason"), S.format_dcf_check(d, ticker=t)[:60])
c = collections.Counter(v[0] for v in out.values())
print(json.dumps({"frame": D.RATE_FRAME, "dcf_module": D.__file__, "n": len(tk), "status": c,
                  "dcf_error": [t for t, v in out.items() if str(v[2]).startswith("dcf_error")]}, ensure_ascii=False))
json.dump(out, open(f"/tmp/tay_sc/smoke_{D.RATE_FRAME}.json", "w"), ensure_ascii=False)
