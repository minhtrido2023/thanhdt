"""B1/E6 — locked_shares với quyền mua SCL 2025 (sau khi đã nộp tiền, CP chờ niêm yết 2026-01-29).
Fixture dnse_raw tạm (mktemp), BQ thật chỉ đọc. Không ghi data/ state/."""
import json, os, sys, tempfile
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, os.path.join(WT, "bin"))
import locked_shares as ls
print("module:", ls.__file__)
acct = "0000000000"
tmp = tempfile.mkdtemp(prefix="b1_ls_")
for asof, o, t in (("2025-11-20", 18999, 14000), ("2026-01-20", 18999, 14000), ("2026-03-20", 18999, 14000)):
    p = os.path.join(tmp, f"dnse_raw_{asof}.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"kind": "positions", "account_no": acct, "ts": asof + "T19:05:00+07:00",
                            "payload": {"positions": [{"symbol": "SCL", "openQuantity": o, "tradeQuantity": t}]}}) + "\n")
    res = ls.classify(acct, asof, tmp, os.path.join(tmp, "none.json"))
    print(asof, json.dumps(res, ensure_ascii=False, default=str))
    for tk, it in res["pending"].items():
        print("   describe:", ls.describe(tk, it))
