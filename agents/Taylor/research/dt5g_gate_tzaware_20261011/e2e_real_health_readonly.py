"""READ-ONLY e2e: gọi get_gated_state trên data/macro_health.json THẬT (chỉ đọc) + BQ (chỉ SELECT).
argv[1] = thư mục chứa macro_state_live.py cần thử. Không publish, không alert, không ghi file."""
import sys, os, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC); sys.path.insert(0, sys.argv[1])
import macro_state_live as msl
print("module:", msl.__file__)
h = json.load(open(os.path.join(WC, "data", "macro_health.json"), encoding="utf-8"))
print("real health: ts=%s status=%s rec=%s" % (h["ts"], h["status"], h["recommended_state_source"]))
end = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
g = msl.get_gated_state("2014-01-01", end, alert=False)
t = g.tail(25)
print("rows=%d last=%s source=%s state=%d base=%d macro=%d stale=%s" % (
    len(g), str(g["time"].iloc[-1])[:10], g["source"].iloc[-1], g["state"].iloc[-1],
    g["base_state"].iloc[-1], g["macro_state"].iloc[-1], g["stale"].iloc[-1]))
print("tail25: n(macro!=base)=%d ; full history n(macro!=base)=%d" % (
    int((t["macro_state"] != t["base_state"]).sum()), int((g["macro_state"] != g["base_state"]).sum())))
