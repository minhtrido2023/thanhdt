#!/usr/bin/env python3
"""READ-ONLY probe: pp0Buy (sức mua VND) của SpaceX cho 5 mã rổ CAPIT.

Chỉ GET: latest_trade + get_buying_power() (GET /accounts/{acc}/ppse).
KHÔNG đặt lệnh, KHÔNG đổi gói vay, KHÔNG ghi file production.
Job Mafee_20260803_120648.
"""
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")

from trading_bot.config import load_config, load_accounts  # noqa: E402
from trading_bot.brokers import make_broker, qget  # noqa: E402

SYMBOLS = ["NCT", "PVT", "SAB", "SIP", "VNM"]

cfg = load_config()
prof = [p for p in load_accounts(cfg) if p["label"] == "SpaceX"][0]
print(f"[probe] SpaceX account_id={prof['account_id']} "
      f"loan_package_id(config)={prof.get('loan_package_id')}")

br = make_broker(prof["cfg"], otp=None, need_quotes=True, profile=prof).connect()
print(f"[probe] client.loan_package_id = {getattr(br.client, 'loan_package_id', None)}")

out = []
for sym in SYMBOLS:
    rec = {"symbol": sym}
    try:
        q = br.get_quote(sym)          # cùng đường production (Quote → VND)
        px = q.last or q.ref
        rec["price"] = px
        rec["quote"] = repr(q)
    except Exception as e:
        rec["price_error"] = f"{type(e).__name__}: {e}"
        px = None
    if px:
        try:
            rec["pp0Buy"] = br.get_buying_power(sym, px)
        except Exception as e:
            rec["pp0Buy_error"] = f"{type(e).__name__}: {e}"
        # raw ppse để dán làm bằng chứng (cùng call production dùng)
        try:
            rec["ppse_raw_cfg_pkg"] = br.client.ppse(prof["account_id"], sym, int(px))
        except Exception as e:
            rec["ppse_raw_error"] = f"{type(e).__name__}: {e}"
        # đối chứng READ-ONLY: cùng endpoint, query loanPackageId=1840 (gói margin
        # RocketX theo results_registry) — chỉ GET, KHÔNG đổi gói của tài khoản
        try:
            rec["ppse_raw_pkg1840"] = br.client.ppse(prof["account_id"], sym,
                                                     int(px), loan_package_id=1840)
        except Exception as e:
            rec["ppse_pkg1840_error"] = f"{type(e).__name__}: {e}"
    out.append(rec)

try:
    lp = br.client.loan_packages(prof["account_id"], symbol="NCT")
except Exception as e:
    lp = f"{type(e).__name__}: {e}"

print(json.dumps({"ppse": out, "loan_packages_NCT": lp}, ensure_ascii=False, indent=1))
