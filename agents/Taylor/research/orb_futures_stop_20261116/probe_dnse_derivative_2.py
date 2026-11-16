import json, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file()
def t(name, fn):
    try: r = fn(); print(f"== {name}: OK", json.dumps(r, ensure_ascii=False, default=str)[:900])
    except Exception as e: print(f"== {name}: ERR {repr(e)[:400]}")
t("instr_all_p1", lambda: c.instruments(limit=3))
for mid in ("DVX","FU","DER","HNX_DER","DERIVATIVE","STX","HNX"):
    t(f"instr_mid_{mid}", lambda mid=mid: c.instruments(market_id=mid, limit=5))
t("instr_idx_VN30", lambda: c.instruments(index_name="VN30", limit=3))
for s in ("41I1GB000","41I1GC000","41I1G2000","VN30F2611"):
    t(f"trade_{s}", lambda s=s: c.latest_trade(s))
t("ohlc_der_VN30F1M", lambda: c.ohlc("VN30F1M", resolution="1", bar_type="derivative", **{"from": 1763258400, "to": 1763280000}))
t("ohlc_der_2611", lambda: c.ohlc("VN30F2611", resolution="1", bar_type="derivative", **{"from": 1763258400, "to": 1763280000}))
t("working_dates", c.working_dates)
