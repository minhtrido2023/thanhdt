"""Vòng 2 — đo trên dữ liệu THẬT (chỉ đọc) bằng code vòng 1: vị thế có ở mỗi lần chụp không,
số lượng đổi ngoài lệnh, tổng trượt 20 cửa sổ, quan hệ phần dư ~ dư nợ, dòng dnse_raw hỏng."""
import sys, os, json, glob, datetime
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012/bin")
import cash_identity as ci
D = "/home/trido/thanhdt/WorkingClaude/data"
E = D + "/execution_logs"
bad = 0; n = 0
for p in sorted(glob.glob(E + "/dnse_raw_*.jsonl")):
    for i, line in enumerate(open(p, encoding="utf-8"), 1):
        if not any(f'"{k}"' in line for k in ci.RawLog.KINDS): continue
        n += 1
        try:
            r = json.loads(line)
            if not isinstance(r.get("payload") or {}, dict): bad += 1; print("PAYLOAD", p, i, type(r.get("payload")))
        except Exception as e:
            bad += 1; print("BADJSON", os.path.basename(p), i, str(e)[:80])
print("dòng thuộc KINDS:", n, "hỏng:", bad)
for acc in ("SpaceX", "ZaloPay"):
    no = ci.load_account_no(acc, D + "/account_inception.json")
    rows = ci.load_nav_rows(acc, E); raw = ci.RawLog(no, E)
    print("==", acc, "rows", len(rows), "balance_ts mẫu", rows[0]["snap"], rows[-1]["snap"])
    res = ci.check_account(acc, nav_dir=E, raw_dir=E, flows_path=D + "/account_cash_flows.json",
                           inception_path=D + "/account_inception.json", seed_path=D + "/account_seed_capital.json")
    ws = res["windows"]; nopos = 0; roll = []
    for i, w in enumerate(ws):
        if not w["checkable"]: print("  UNCHECK", w["date1"], w["reason"]); continue
        q0, q1 = raw.quantities_at(w["snap0"]), raw.quantities_at(w["snap1"])
        if q0 is None or q1 is None: nopos += 1; print("  NOPOS", w["date0"], w["date1"], q0 is None, q1 is None); continue
        fills = raw.fills_between(w["snap0"], w["snap1"])
        net = {}
        for fx in fills: net[fx["symbol"]] = net.get(fx["symbol"], 0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])
        gaps = {s: q1.get(s, 0) - q0.get(s, 0) - net.get(s, 0) for s in set(q0) | set(q1) | set(net)}
        gaps = {s: g for s, g in gaps.items() if abs(g) > 1e-6}
        if gaps: print(f"  QTYGAP {w['date0']}→{w['date1']} {gaps} fills={len(fills)} unexpl={w['unexplained']:+,.0f} pct={w['pct_nav']:+.4f}")
    print("  cửa sổ thiếu vị thế:", nopos, "/", len(ws))
    pct = [w["pct_nav"] if w["checkable"] and not w["suspect"] else 0.0 for w in ws]
    worst = max(((abs(sum(pct[max(0, i - 19):i + 1])), ws[i]["date1"], sum(pct[max(0, i - 19):i + 1])) for i in range(len(ws))))
    print("  tổng trượt 20 cửa sổ lớn nhất (%NAV):", worst, " cuối:", round(sum(pct[-20:]), 4))
    over = [(str(ws[i]["date1"]), round(sum(pct[max(0, i - 19):i + 1]), 4)) for i in range(len(ws)) if abs(sum(pct[max(0, i - 19):i + 1])) > 0.05]
    print("  số điểm trượt vượt 0,05:", len(over), over[:6], over[-3:])
    deb = [(str(w["date1"]), round(max(r0, r1)), round(w["unexplained"]), (w["snap1"].date() - w["snap0"].date()).days)
           for w, r0, r1 in ((w, rows[i]["debt"], rows[i + 1]["debt"]) for i, w in enumerate(ws)) if w["checkable"] and max(r0, r1) > 0]
    print("  cửa sổ có dư nợ:", len(deb)); [print("    ", d) for d in deb[:40]]
