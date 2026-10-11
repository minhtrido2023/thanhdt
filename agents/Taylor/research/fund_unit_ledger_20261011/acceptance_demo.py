#!/usr/bin/env python3
"""In ra các ca nghiệm thu tổng hợp (file ở tempdir, KHÔNG đụng data/ thật). argv[1] = <worktree>/bin."""
import sys, tempfile, datetime
sys.path.insert(0, sys.argv[1])
import nav_unit_ledger_selfcheck as sc
import account_cash_flows as acf
D = datetime.date
tmp = tempfile.mkdtemp(prefix="fu_accept_")
dep, Env = sc.dep, sc.Env

def show(label, env, date=sc.REPORT):
    r = env.returns(date)["inception"]
    led = env.ledger()[0]
    gap = max(abs(x["units"] * x["unit_price"] - x["nav"]) for x in led)
    print(f"{label:58s} twr {r['return_pct']:>7}%  mwr {r['mwr_pct']}%  pnl {r['pnl_vnd']:>14,.0f}  "
          f"ròng {r.get('net_flow_vnd', 0):>14,.0f}  đơn vị cuối {led[-1]['units']:>14,.4f}  giá cuối {led[-1]['unit_price']:>12,.4f}  "
          f"max|đv×giá−NAV| {gap:.2e}đ  quy năm {r['annualized_return_pct']}")

print("== 1. Nạp 200tr vào 1 tỷ đúng ngày thị trường +2%")
nav_e = [("2026-07-02", 1e9), ("2026-07-03", 1.22e9), ("2026-07-06", 1.22e9)]
nav_b = [("2026-07-02", 1e9), ("2026-07-03", 1.224e9), ("2026-07-06", 1.224e9)]
eod, bod = [dep("2026-07-03", 200_000_000)], [dep("2026-07-03", 200_000_000, "bod", "10:15")]
show("chuỗi NAV 1.220tr đọc eod (mặc định) — tay: +2,000%", Env(tmp, "1a", nav_e, eod))
show("chuỗi NAV 1.220tr đọc bod            — tay: +1,667%", Env(tmp, "1b", nav_e, bod))
show("chuỗi NAV 1.224tr đọc bod            — tay: +2,000%", Env(tmp, "1c", nav_b, bod))
show("chuỗi NAV 1.224tr đọc eod            — tay: +2,400%", Env(tmp, "1d", nav_b, eod))
print("== 2. Rút một phần (nạp 200 rồi rút 300, thị trường đứng yên 2 ngày đó; trước +1%, sau +1%) — tay: +2,010%")
flat = [("2026-07-02", 1.01e9), ("2026-07-03", 1.21e9), ("2026-07-06", 0.91e9), ("2026-07-07", 919.1e6)]
show("eod", Env(tmp, "2a", flat, [dep("2026-07-03", 200_000_000), dep("2026-07-06", -300_000_000)]))
show("bod", Env(tmp, "2b", flat, [dep("2026-07-03", 200_000_000, "bod", "09:30"), dep("2026-07-06", -300_000_000, "bod", "09:30")]))
print("== 3. Rút gần hết (còn 1tr) rồi +5% — tay: +5,000%, còn 100 đơn vị")
near = [("2026-07-02", 1e9), ("2026-07-03", 1e6), ("2026-07-06", 1.05e6)]
show("eod", Env(tmp, "3a", near, [dep("2026-07-03", -999_000_000)]))
for label, env in (("rút HẾT đầu ngày", Env(tmp, "3b", near, [dep("2026-07-03", -1_000_000_000, "bod", "09:00")])),
                   ("rút HẾT cuối ngày", Env(tmp, "3c", [("2026-07-02", 1e9), ("2026-07-03", 0.0)], [dep("2026-07-03", -1_000_000_000)]))):
    try: env.ledger_raw(); print(label, "→ KHÔNG bị từ chối (SAI)")
    except ValueError as e: print(f"{label} → TỪ CHỐI: {e}")
print("== 4. Nạp 500tr ĐÚNG ngày inception — bị loại (đã nằm trong vốn khởi điểm), số không đổi so với không khai")
plain = [("2026-07-02", 1.01e9), ("2026-07-03", 1.02e9), ("2026-07-06", 1.03e9)]
show("không khai gì", Env(tmp, "4a", plain, []))
e = Env(tmp, "4b", plain, [dep("2026-07-01", 500_000_000)])
show("khai nạp 500tr ngày 07-01", e)
p = e.cli("--tail", "0"); print("   CLI rc =", p.returncode, "| stderr:", p.stderr.strip())
print("== 5. Ba dòng tiền cùng ngày 07-03: bod +100, eod +200, eod −50 — tay: 1,01 × (1282,2−150)/(1010+100) − 1 = +3,020%")
show("", Env(tmp, "5", [("2026-07-02", 1.01e9), ("2026-07-03", 1.2822e9), ("2026-07-06", 1.2822e9)],
             [dep("2026-07-03", 200_000_000), dep("2026-07-03", -50_000_000), dep("2026-07-03", 100_000_000, "bod", "09:20")]))
print("== 6. Dòng tiền rơi vào ngày KHÔNG có dòng nav_history (thứ Bảy 07-04, mặc định eod) — fail-closed")
e = Env(tmp, "6", plain, [dep("2026-07-04", 200_000_000)])
p = e.cli("--seal"); print("   nav_unit_ledger --seal rc =", p.returncode, "| sổ được tạo:", e.sealed.exists(), "\n   stderr:", p.stderr.strip())
try: e.returns_raw(); print("   nav_period_returns: KHÔNG từ chối (SAI)")
except acf.CashFlowError as ex: print("   nav_period_returns: TỪ CHỐI (CashFlowError)")
print("== 7. Nhân đôi mọi dòng tiền — chỉ nạp vào tiền mặt, thị trường đứng yên từ lần nạp đầu (trước đó +1%, −0,5%) — tay: +0,495% cả hai")
for timing, t in (("eod", None), ("bod", "09:10")):
    for k in (1, 2):
        stock = [1e9 * f for f in (1.01, 1.01 * 0.995, 1.01 * 0.995, 1.01 * 0.995, 1.01 * 0.995)]
        cash = [0.0, 0.0, 150e6 * k, 150e6 * k, 400e6 * k]
        days = ["2026-07-02", "2026-07-03", "2026-07-06", "2026-07-07", "2026-07-08"]
        show(f"{timing} × {k}", Env(tmp, f"7{timing}{k}", [(d, s + c) for d, s, c in zip(days, stock, cash)],
             [dep("2026-07-06", 150e6 * k, timing if t else None, t), dep("2026-07-08", 250e6 * k, timing if t else None, t)]))
print("== 8. Quy năm: SpaceX-giả từ 2026-07-01")
e = Env(tmp, "8", [("2026-07-02", 1e9), ("2027-06-30", 1.05e9), ("2028-05-31", 1.2e9), ("2028-06-23", 1.205e9), ("2028-06-30", 1.21e9)], [])
for d in (D(2027, 6, 30), D(2028, 6, 30)):
    r = e.returns(d)["inception"]; print(f"   asof {d}: {r['days']} ngày, twr {r['return_pct']}%, annualized_return_pct={r['annualized_return_pct']}, note={r.get('annualized_note')}")
