# READ-ONLY probe DNSE phai sinh. KHONG goi place/modify/cancel.
import json, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file()
ACC = "0002023347"
out = {}
def tryit(name, fn):
    try: r = fn(); out[name] = r; print(f"== {name}: OK"); print(json.dumps(r, ensure_ascii=False, default=str)[:1500])
    except Exception as e: out[name] = {"error": repr(e)[:600]}; print(f"== {name}: ERR {repr(e)[:600]}")
tryit("accounts", c.accounts)
tryit("balances", lambda: c.balances(ACC))
tryit("positions_DER", lambda: c.positions(ACC, market_type="DERIVATIVE"))
tryit("orders_DER", lambda: c.orders(ACC, market_type="DERIVATIVE"))
tryit("orders_DER_cond", lambda: c.orders(ACC, market_type="DERIVATIVE", order_category="CONDITIONAL"))
tryit("loanpk_DER", lambda: c.loan_packages(ACC, market_type="DERIVATIVE"))
tryit("instr_fu", lambda: c.instruments(symbol="VN30F2611"))
for s in ("VN30F1M", "VN30F2611", "VN30F2612", "41I1FB000"):
    tryit(f"secdef_{s}", lambda s=s: c.secdef(s))
json.dump(out, open("/tmp/orb_probe_out.json", "w"), ensure_ascii=False, indent=1, default=str)
