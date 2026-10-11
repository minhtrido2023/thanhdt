import sys, datetime, json, os, tempfile
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011/bin")
sys.dont_write_bytecode = True
import account_cash_flows as acf, nav_unit_ledger as nul, nav_period_returns as npr
D=datetime.date
INC={"inception_date":"2026-07-01","starting_capital":1_000_000_000}
def fl(date, amt, timing="eod", t=None, kind=None):
    return {"date":date,"amount_vnd":float(amt),"kind":kind or ("deposit" if amt>0 else "withdraw"),"evidence":"x","timing":timing,"time_ict":t}
def R(rows, flows, rd):
    return npr.compute_period_returns("SpaceX", rd, rows, INC, flows)
def show(tag, r, per="inception"):
    p=r[per]; print(f"  {tag}: {per} return_pct={p['return_pct']} pnl={p['pnl_vnd']:,.0f} mwr={p['mwr_pct']} net_flow={p.get('net_flow_vnd')} to={p['to_date']} up1={p['unit_price1']}")

print("== S1. (B) nạp 200tr lúc 20:00 ngày T (SAU snapshot 19:10), thị trường ĐỨNG YÊN cả kỳ. Sự thật: tỉ suất = 0%")
rows=[nul.NavRow(D(2026,7,2),1e9,False,"2026-07-02T19:10:00"), nul.NavRow(D(2026,7,3),1e9,False,"2026-07-03T19:10:00"),
      nul.NavRow(D(2026,7,6),1.2e9,False,"2026-07-06T19:10:00"), nul.NavRow(D(2026,7,7),1.2e9,False,"2026-07-07T19:10:00")]
for tag,flows in (("eod mặc định, KHÔNG time_ict (khai ngày T=07-03)",[fl(D(2026,7,3),200e6)]),
                  ("bod kèm giờ, ngày T=07-03 (hành vi mặc định CŨ)",[fl(D(2026,7,3),200e6,"bod","20:00")]),
                  ("bod phiên kế 07-06 (khai ĐÚNG)",[fl(D(2026,7,6),200e6,"bod","08:00")])):
    for rd in (D(2026,7,3),D(2026,7,6),D(2026,7,7)):
        try: show(f"{tag} | asof {rd}", R(rows,flows,rd))
        except Exception as e: print(f"  {tag} | asof {rd}: {type(e).__name__}: {str(e)[:150]}")
try:
    R(rows,[fl(D(2026,7,3),200e6,"eod","20:00")],D(2026,7,7))
except Exception as e: print("  eod CÓ time_ict 20:00 ⇒", type(e).__name__, str(e)[:120])

print("== S1b. RÚT 200tr lúc 20:00 ngày T sau snapshot, khai eod không giờ, báo cáo asof T")
rows=[nul.NavRow(D(2026,7,2),1e9,False,"2026-07-02T19:10:00"), nul.NavRow(D(2026,7,3),1e9,False,"2026-07-03T19:10:00"),
      nul.NavRow(D(2026,7,6),0.8e9,False,"2026-07-06T19:10:00")]
for rd in (D(2026,7,3),D(2026,7,6)):
    show(f"asof {rd}", R(rows,[fl(D(2026,7,3),-200e6)],rd)); show(f"asof {rd}", R(rows,[fl(D(2026,7,3),-200e6)],rd),"wtd")

print("== S2. pending: flow eod ghi NHẦM ngày tương lai (2026-07-13 thay vì 07-03), NAV đã chứa tiền")
rows=[(D(2026,7,2),1e9),(D(2026,7,3),1.04e9),(D(2026,7,6),1.04e9)]
a=R(rows,[fl(D(2026,7,13),40e6)],D(2026,7,6)); b=R(rows,[],D(2026,7,6))
print("  output có pending == output không flow:", a==b, "| return_pct", a["inception"]["return_pct"], "| keys chứa pending?", any("pend" in k for k in a))
jumps=acf.unexplained_nav_jumps(rows,[fl(D(2026,7,13),40e6)]); print("  cổng 5%:", jumps)

print("== S3. (C) nạp thứ Bảy 07-04 khai eod mặc định: hợp lệ lúc CN, thành LỖI sau snapshot thứ Hai")
rows_fri=[(D(2026,7,2),1e9),(D(2026,7,3),1e9)]
rows_mon=rows_fri+[(D(2026,7,6),1.1e9)]
f=[fl(D(2026,7,4),100e6)]
print("  CN (dòng cuối 07-03):", R(rows_fri,f,D(2026,7,5))["inception"]["return_pct"], "(pending, không báo)")
try: R(rows_mon,f,D(2026,7,6))
except Exception as e: print("  T2 sau snapshot:", type(e).__name__, str(e)[:230])
fb=[fl(D(2026,7,4),100e6,"bod","10:00")]
print("  làm theo gợi ý (bod+time, giữ ngày 07-04):", R(rows_mon,fb,D(2026,7,6))["inception"]["return_pct"])
print("  ...nhưng cổng báo cáo 5% (unexplained_nav_jumps) với CHÍNH bản ghi đó:", [(str(j['date']),round(j['change_pct'],2)) for j in acf.unexplained_nav_jumps(rows_mon,fb)])

print("== S4. flow ĐÚNG ngày cuối kỳ (eod trên to_date)")
rows=[(D(2026,7,2),1e9),(D(2026,7,3),1.01e9),(D(2026,7,6),1.2221e9)]   # 07-06: +1% rồi nạp 202 (1.0201+0.202)
r=R(rows,[fl(D(2026,7,6),202e6)],D(2026,7,6)); show("eod on to_date",r); print("   cash_flows:",r["inception"].get("cash_flows"))

print("== S5. IRR biên")
print("  0 nghiệm do lỗ >99,9% (dòng tiền KHÔNG đổi dấu):", npr.money_weighted_return(1000.0, 0.1, [(0.5, 10.0)]))
print("  pnl = 0 chính xác:", npr.money_weighted_return(1000.0, 1200.0, [(0.5, 200.0)]))
print("  nạp > NAV:", npr.money_weighted_return(1000.0, 6100.0, [(0.5, 5000.0)]))
print("  rút > nav0:", npr.money_weighted_return(1000.0, 600.0, [(0.3, -2500.0)]))
print("  nghiệm kép (chạm 0 không cắt) 1000y²−2200y+1210=(√1000 y−√1210)²:", npr.money_weighted_return(1000.0, -1210.0+0, [(0.5,-2200.0)]) )
print("  kỳ 0 ngày:", R([(D(2026,7,2),1e9)],[],D(2026,7,2))["wtd"]["days"], "| report_date = inception:", end=" ")
try: print(R([(D(2026,7,1),1e9),(D(2026,7,2),1e9)],[],D(2026,7,1))["inception"])
except Exception as e: print(type(e).__name__, e)
print("== S6. bod thứ Hai: w của IRR dùng CN (row−1) chứ không phải giá-chốt thứ Sáu hay ngày thật của flow")
rows=[(D(2026,7,2),1e9),(D(2026,7,3),1e9),(D(2026,7,6),1.224e9),(D(2026,7,10),1.224e9)]
for d in (D(2026,7,4),D(2026,7,6)):
    r=R(rows,[fl(d,200e6,"bod","09:00")],D(2026,7,10))["inception"]; print(f"  bod khai ngày {d}: twr={r['return_pct']} mwr={r['mwr_pct']}")
