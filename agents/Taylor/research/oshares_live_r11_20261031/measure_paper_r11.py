"""R11 paper: dc_book_waterfall_paper state hiện tại — trước (không khai) vs sau (_dcf_echo_line thật của nhánh)."""
import json, glob, os
import dcf_valuation as dv
from trading_bot.strategies import _dcf_check_for_order, format_dcf_check
import dc_book_waterfall_paper as P
st = json.load(open("/home/trido/thanhdt/WorkingClaude/data/dc_book_waterfall_paper_state.json"))  # data PROD (WT khong co)
names, lc = st.get("dc_names") or [], st.get("last_close") or {}
asof = str(st.get("clock_date"))[:10]
print("asof", asof, "names", names)
pds = dv.price_sessions_for([(t, lc[t]) for t in names if isinstance(lc.get(t), (int, float))], asof)
for t in names:
    px = lc.get(t)
    if not isinstance(px, (int, float)):
        continue
    b = _dcf_check_for_order(t, px, asof); a = _dcf_check_for_order(t, px, asof, price_date=pds[(t, px)])
    print(t, px, pds[(t, px)], "| before:", format_dcf_check(b, "paper"), "| after:", format_dcf_check(a, "paper"),
          "| identical", json.dumps(b, sort_keys=True, default=str) == json.dumps(a, sort_keys=True, default=str))
