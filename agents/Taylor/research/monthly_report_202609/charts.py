import json, subprocess
ns = json.load(open("navstats.json")); ps = json.load(open("positions_20260930.json"))
for acc in ["SpaceX", "ZaloPay"]:
    d = ns[acc]; nav = d["nav1"]; last = d["last"]
    rows = ps[acc]["rows"]
    top = rows[:8]
    alloc = [[r["sym"], round(r["mv"]/nav*100, 1)] for r in top]
    other = sum(r["mv"] for r in rows[8:])
    cash = float(last["cash"]) + float(last["egg_assets"]) - float(last["margin_debt"])
    alloc += [["Cổ phiếu khác", round(other/nav*100, 1)], ["Tiền mặt & tiền gửi", round(cash/nav*100, 1)]]
    print(acc, alloc, round(sum(a[1] for a in alloc), 1))
    cmd = ["python3", "/home/trido/thanhdt/WorkingClaude/mike/bin/report_charts.py", "--account", acc, "--label", "monthly_2026-09",
           "--title-suffix", "Tháng 09/2026", "--dates", json.dumps(d["dates"]), "--nav", json.dumps(d["nav"]), "--vnindex", json.dumps(d["vn"]),
           "--allocation", json.dumps(alloc, ensure_ascii=False)]
    print(subprocess.run(cmd, capture_output=True, text=True, cwd="/home/trido/thanhdt/WorkingClaude"))
