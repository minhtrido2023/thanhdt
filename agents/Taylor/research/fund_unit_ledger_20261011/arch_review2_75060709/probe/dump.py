import sys, json, datetime
root = sys.argv[1]
sys.path.insert(0, root + "/mike/bin")
import nav_period_returns as npr
out = {}
for acct in ("SpaceX", "ZaloPay"):
    rows = npr.load_nav_history(acct); inc = npr.load_inception(acct)
    d = datetime.date(2026, 6, 25)
    while d <= datetime.date(2026, 10, 15):
        try:
            r = npr.compute_period_returns(acct, d, rows, inc)
        except Exception as e:
            r = {"ERR": f"{type(e).__name__}: {e}"}
        out[f"{acct}|{d}"] = r
        d += datetime.timedelta(days=1)
json.dump(out, open(sys.argv[2], "w"), default=str)
