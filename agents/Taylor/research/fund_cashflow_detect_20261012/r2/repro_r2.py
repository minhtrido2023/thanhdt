import sys, os, json, csv, datetime, shutil, tempfile, re
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012/bin")
os.environ.pop("WC_ROOT", None); os.environ.pop("TZ", None)
import cash_identity as ci
ACC, NO = "SpaceX", "9000000001"
COLS = ["date","nav","mtm_stock","cash","margin_debt","offbook_assets","egg_assets","balance_ts","cum_dividend_excl","nav_is_estimate","nav_source"]
def world(name, rows, raw, flows=()):
    d = os.path.join("/tmp/fcf_r2/repro", name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    with open(f"{d}/nav_history_{ACC}.csv","w") as f:
        w = csv.DictWriter(f, COLS); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in COLS})
    for day, recs in raw.items():
        with open(f"{d}/dnse_raw_{day}.jsonl","w") as f:
            for r in recs: f.write(json.dumps(r)+"\n")
    json.dump({ACC: list(flows)}, open(f"{d}/flows.json","w"))
    json.dump({ACC: {"account_no": NO, "inception_date": "2026-03-01", "starting_capital": 1e9}}, open(f"{d}/inc.json","w"))
    return dict(nav_dir=d, raw_dir=d, flows_path=f"{d}/flows.json", inception_path=f"{d}/inc.json", seed_path=f"{d}/seed.json", today=datetime.date(2026,3,31))
def bal(ts, recv=0): return {"ts": ts, "kind": "balances", "account_no": NO, "payload": {"stock": {"cashDividendReceiving": recv}}}
def pos(ts, q): return {"ts": ts, "kind": "positions", "account_no": NO, "payload": {"positions": [{"accountNo": NO, "symbol": s, "openQuantity": n} for s, n in q.items()]}}
def row(day, nav, stock, cash, debt=0, egg=0, hh="19:10:05"): return {"date": f"2026-03-{day:02d}", "nav": nav, "mtm_stock": stock, "cash": cash, "margin_debt": debt, "offbook_assets": 0, "egg_assets": egg, "balance_ts": f"2026-03-{day:02d}T{hh}", "cum_dividend_excl": 0, "nav_is_estimate": "False", "nav_source": "live"}
def show(tag, p):
    res = ci.check_account(ACC, **p)
    print(f"--- {tag}: windows={len(res['windows'])} suspects={len(res['suspects'])} uncheckable={len(res['uncheckable'])}")
    for w in res["windows"]:
        if w["checkable"]: print(f"    {w['date0']}→{w['date1']} ΔK={w['delta_k']:+,.0f} unexplained={w['unexplained']:+,.0f} pct={w['pct_nav']:+.4f}% suspect={w['suspect']} acked={bool(w['acked'])}")
    lines = ci.warning_lines(ACC, **p); print(f"    warning_lines: {len(lines)}" + ("" if not lines else " | " + lines[0][:230]))
# R1: NẠP 50tr + MUA TAY 50tr (5.000 cp AAA @10.000) ngày HOLD — dnse_raw KHÔNG có bản ghi orders (đúng như 54/77 ngày thật của SpaceX)
fee = 50e6*0.00097
p = world("R1", [row(2, 1_000_000_000, 800e6, 200e6), row(3, 1_050_000_000 - fee, 850e6, 200e6 - fee)],
          {"2026-03-02": [bal("2026-03-02T19:10:05"), pos("2026-03-02T19:10:09", {"AAA": 80000})],
           "2026-03-03": [bal("2026-03-03T19:10:05"), pos("2026-03-03T19:10:09", {"AAA": 85000})]})
show("R1 nạp 50tr + mua tay 50tr, ngày không có bản ghi orders (NAV +5,0% do nạp)", p)
# R2: BÁN TAY 60tr + RÚT 60tr, không có bản ghi orders
cost = 60e6*(0.00097+0.001)
p = world("R2", [row(2, 1_000_000_000, 800e6, 200e6), row(3, 940_000_000 - cost, 740e6, 200e6 - cost)],
          {"2026-03-02": [bal("2026-03-02T19:10:05"), pos("2026-03-02T19:10:09", {"AAA": 80000})],
           "2026-03-03": [bal("2026-03-03T19:10:05"), pos("2026-03-03T19:10:09", {"AAA": 74000})]})
show("R2 bán tay 60tr + rút 60tr, không có bản ghi orders (NAV −6,0%)", p)
# R3: market_only (mở cổng bước nhảy NAV) che khoản NẠP 200tr cùng cửa sổ
raw = {"2026-03-02": [bal("2026-03-02T19:10:05")], "2026-03-03": [bal("2026-03-03T19:10:05")]}
p = world("R3", [row(2, 1e9, 800e6, 200e6), row(3, 1.2e9, 800e6, 400e6)], raw,
          [{"date": "2026-03-03", "amount_vnd": 0, "kind": "market_only", "evidence": "x"}])
show("R3 nạp 200tr CHƯA khai + market_only cùng ngày", p)
# R5: rút Trứng vàng trước hạn 319tr (ZaloPay thật: NAV 931.434.028, egg 319.114.008), mất 0,2013% như lần đo 09-17
egg, navz = 319_114_008, 931_434_028; lost = egg*0.002013
p = world("R5", [row(2, navz, 607e6, 4.9e6, egg=egg), row(3, navz - lost, 607e6, 4.9e6 + egg - lost, egg=0)], raw)
show(f"R5 rút hết Trứng vàng (nội bộ), khấu trừ {lost:,.0f}đ", p)
# R6: lãi vay ký quỹ post dồn 1 tháng: dư nợ 400tr × 12,5%/12
it = 400e6*0.125/12
p = world("R6", [row(2, 1e9, 1400e6, 0, debt=400e6), row(3, 1e9 - it, 1400e6, 0, debt=400e6 + it)], raw)
show(f"R6 DNSE post lãi vay tháng {it:,.0f}đ", p)
# R8: cổ tức 80tr chốt quyền VÀ chi trả trong cùng một cửa sổ (phải thu 0 → 0), tiền +76tr
p = world("R8", [row(2, 1e9, 800e6, 200e6), row(3, 1e9 + 76e6, 800e6, 276e6)], raw)
show("R8 cổ tức 80tr ghi + trả trong một cửa sổ", p)
# R10: rút nhỏ giọt 450k × 10 phiên (mỗi cửa sổ 0,045% < ngưỡng) — tổng 4,5tr = 0,45% NAV
rows = [row(2+i, 1e9 - 450e3*i, 800e6, 200e6 - 450e3*i) for i in range(11)]
p = world("R10", rows, {f"2026-03-{2+i:02d}": [bal(f"2026-03-{2+i:02d}T19:10:05")] for i in range(11)})
res = ci.check_account(ACC, **p); print(f"--- R10 rút nhỏ giọt 450k×10: suspects={len(res['suspects'])}, Σ unexplained={sum(w['unexplained'] for w in res['windows']):+,.0f} ({sum(w['pct_nav'] for w in res['windows']):+.3f}% NAV)")
# R11: lãi Trứng vàng đổi 8,54% → 6,5%/năm trên 500tr, 20 cửa sổ 1 ngày
egg0 = 500e6; rows=[]; e=egg0
for i in range(21):
    rows.append(row(2+i if i < 29 else 30, 1e9 + (e-egg0), 500e6, 0, egg=round(e))); e *= 1 + 0.065/365
p = world("R11", rows, {f"2026-03-{2+i:02d}": [bal(f"2026-03-{2+i:02d}T19:10:05")] for i in range(21)})
res = ci.check_account(ACC, **p); print(f"--- R11 lãi Trứng vàng thật 6,5%/năm: suspects={len(res['suspects'])}, phần dư mỗi cửa sổ ≈ {res['windows'][0]['unexplained']:+,.0f}đ ({res['windows'][0]['pct_nav']:+.4f}%), Σ20 = {sum(w['unexplained'] for w in res['windows']):+,.0f}đ")
# R12: nav = "nan" ở một dòng
rows = [row(2, 1e9, 800e6, 200e6), row(3, "nan", 800e6, 400e6), row(4, 1.2e9, 800e6, 400e6)]
p = world("R12", rows, raw); print("--- R12 nav='nan':", ci.warning_lines(ACC, **p)[0][:200])
# R13: một dòng có cash rỗng (cột trống) ⇒ _num = 0
rows = [row(2, 1e9, 800e6, 200e6), dict(row(3, 1e9, 800e6, ""), )]
p = world("R13", rows, raw); show("R13 ô cash RỖNG ở dòng sau (đọc thành 0)", p)
# ---- thêm ở vòng 2 (Taylor): in NHÃN từng ca + dòng trôi của R10/R11 (repro gốc chỉ in 230 ký tự đầu)
print("=== NHÃN TỪNG CA (vòng 2)")
for name in ("R1", "R2", "R3", "R5", "R6", "R8", "R10", "R11", "R12", "R13"):
    d = os.path.join("/tmp/fcf_r2/repro", name)
    p = dict(nav_dir=d, raw_dir=d, flows_path=f"{d}/flows.json", inception_path=f"{d}/inc.json", seed_path=f"{d}/seed.json", today=datetime.date(2026,3,31))
    lines = ci.warning_lines(ACC, **p)
    rep = ci.report(ACC, **p)
    print(f"{name}: {len(lines)} dòng vận hành; dòng nhà đầu tư = {rep['investor_line']!r}")
    for l in lines: print("   ", l[:210])
