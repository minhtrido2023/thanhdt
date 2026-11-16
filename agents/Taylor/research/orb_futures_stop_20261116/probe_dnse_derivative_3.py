import json, sys, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file(); ACC="0002023347"
ICT=ZoneInfo("Asia/Ho_Chi_Minh")
f=int(dt.datetime(2026,11,16,9,0,tzinfo=ICT).timestamp()); t_=int(dt.datetime(2026,11,16,14,46,tzinfo=ICT).timestamp())
def t(name, fn, n=1500):
    try: r = fn(); print(f"== {name}: OK", json.dumps(r, ensure_ascii=False, default=str)[:n]); return r
    except Exception as e: print(f"== {name}: ERR {repr(e)[:400]}")
t("secdef_GB", lambda: c.secdef("41I1GB000"))
t("secdef_GB_G1", lambda: c.secdef("41I1GB000", board_id="G1"))
t("secdef_GC", lambda: c.secdef("41I1GC000"))
t("close_GB", lambda: c.close_price("41I1GB000"))
t("quote_GB", lambda: c.latest_quote("41I1GB000"))
for bt in ("derivative","stock"):
    r=t(f"ohlc_GB_1m_{bt}", lambda bt=bt: c.ohlc("41I1GB000", resolution="1", bar_type=bt, **{"from": f, "to": t_}), 600)
    if r and r.get("t"): print("   nbars", len(r["t"]), "first", dt.datetime.fromtimestamp(r["t"][0],ICT), r["o"][0], r["c"][0], "last", dt.datetime.fromtimestamp(r["t"][-1],ICT), r["c"][-1]); json.dump(r, open(f"/tmp/dnse_ohlc_GB_{bt}.json","w"))
t("ohlc_VN30F1M_1m", lambda: c.ohlc("VN30F1M", resolution="1", bar_type="derivative", **{"from": f, "to": t_}), 300)
t("ppse_DER", lambda: c.ppse(ACC, "41I1GB000", 1843, market_type="DERIVATIVE", loan_package_id=1306))
t("history_DER", lambda: c.order_history(ACC, from_date="2026-10-01", to_date="2026-11-16", market_type="DERIVATIVE"), 600)
