"""aria-F2c: replay totalCash API ZaloPay ngay-qua-ngay theo fill EMAIL (T+0: +ban −mua −phi −thue).
Lech lon = dong tien ngoai / fill thieu. Doc balances dnse_raw loc account_no (§12)."""
import json, os
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); ACC = "0001743768"
d = pd.read_csv(os.path.join(H, "all_fills.csv"), dtype={"tieu_khoan": str})
d = d[d.tieu_khoan == ACC]; d["date"] = pd.to_datetime(d.email_date, format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
d["flow"] = d.gia_tri_khop.where(d.loai_lenh == "BÁN", -d.gia_tri_khop) - d.fee - d.thue
flow = d.groupby("date").flow.sum()
prev = None
for day in ["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-13"]:
    last = None
    for l in open(f"/home/trido/thanhdt/WorkingClaude/data/execution_logs/dnse_raw_{day}.jsonl"):
        r = json.loads(l)
        if r["kind"] == "balances" and r.get("account_no") == ACC:
            last = r["payload"]["stock"]["totalCash"]
    if prev is not None:
        exp = prev + flow.get(day, 0.0)
        print(f"{day} totalCash {last:>13,.0f}  replay {exp:>13,.0f}  lech {last-exp:>+10,.0f}")
    prev = last
