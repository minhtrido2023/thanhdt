"""arch-review E: ca DRI THẬT (ZaloPay + SpaceX, chốt 2026-10-02) với tài khoản thứ ba:
 (ii) không có bản ghi nào; (iii) có bản ghi positions RỖNG mỗi tối từ 2026-07-06 → 2026-10-09 (tài khoản live mới bật, chưa mua gì)."""
import json, os, sys, tempfile, shutil
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010/bin"); sys.path.insert(0, "/tmp/taylor_r2_old_bin")
os.environ["WC_ROOT"] = "/home/trido/thanhdt/WorkingClaude"
os.environ["DAR_BQ_MEMO_DIR"] = "/tmp/taylor_k1_memo.xagj2y7s"
import report_return_gate as rrg, dividend_adjusted_return as dar
live = []
_ol = dar._bq_live
dar._bq_live = lambda sql: (live.append(1), _ol(sql))[1]
REAL_ACC = dict(dar.ACCOUNTS)
FAKE = "0009999999"

def show(tag):
    out = {}
    for lb in ("ZaloPay", "SpaceX"):
        pr = rrg.position_returns(lb, "2026-10-02")
        r = pr["positions"]["DRI"]
        out[lb] = (round(r["pct"], 2) if "pct" in r else None, r["code"], [w[:230] for w in r["why"]][:1])
        nret = sum(1 for x in pr["positions"].values() if "pct" in x)
        out[lb] += (f"{nret}/{len(pr['positions'])} mã có tỉ suất",)
    print(f"{tag}\n   ZaloPay DRI: {out['ZaloPay']}\n   SpaceX  DRI: {out['SpaceX']}\n   (live BQ calls so far: {len(live)})", flush=True)

show("(i) 2 tài khoản thật")
dar.ACCOUNTS = {**REAL_ACC, "RocketX": FAKE}
show("(ii) + tài khoản thứ ba KHÔNG có bản ghi nào")
# (iii) sổ tổng hợp: bản ghi positions rỗng mỗi tối
d = tempfile.mkdtemp(prefix="archrev_p1real_")
import datetime as dt
day = dt.date(2026, 7, 6)
while day <= dt.date(2026, 10, 9):
    if day.weekday() < 5:
        with open(os.path.join(d, f"dnse_raw_{day}.jsonl"), "w") as fh:
            fh.write(json.dumps({"kind": "positions", "account_no": FAKE, "ts": f"{day}T19:07:00", "payload": {"positions": []}}) + "\n")
            fh.write(json.dumps({"kind": "balances", "account_no": FAKE, "ts": f"{day}T19:07:00", "payload": {"stock": {"totalCash": 5e6, "availableCash": 5e6, "depositInterest": 0, "cashDividendReceiving": 0}}}) + "\n")
    day += dt.timedelta(days=1)
keep = dar.EXEC_LOG_DIR
dar.EXEC_LOG_DIR = d
L3 = dar.account_ledger(FAKE)
dar.EXEC_LOG_DIR = keep
shutil.rmtree(d, ignore_errors=True)
print("   L3: first=%r n_ts=%d (bản ghi có thật: 70 tối, đều rỗng)" % (L3["first"], len(L3["ts"])))
_oal = dar.account_ledger
dar.account_ledger = lambda no: L3 if no == FAKE else _oal(no)
show("(iii) + tài khoản thứ ba có bản ghi positions RỖNG mỗi tối từ 06/07 (sổ phủ mọi cửa sổ, chưa từng giữ gì)")
