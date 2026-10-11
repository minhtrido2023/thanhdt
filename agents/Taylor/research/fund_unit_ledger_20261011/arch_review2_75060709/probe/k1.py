import sys, datetime as dt
sys.path.insert(0, "/tmp/ar2/WC/mike/bin")
import account_cash_flows as acf, nav_unit_ledger as nul, nav_period_returns as npr
D = dt.date
def R(d, nav, ts=None, hh="19:10:00"):
    return acf.NavRow(d, float(nav), balance_ts=(ts if ts is not None else f"{d}T{hh}"))
def F(d, t, amt, kind=None, timing=None):
    f = {"date": d, "time_ict": t, "amount_vnd": float(amt), "kind": kind or ("deposit" if amt>0 else "withdraw"), "evidence":"x", "timing": timing}
    return f
def run(label, rows, flows, inc=(D(2026,6,1), 1e9), asofs=None):
    try:
        led, info = nul.build_ledger(rows, flows, *inc)
    except Exception as e:
        print(f"{label:60s} => {type(e).__name__}: {str(e)[:230]}"); return None
    s = " ".join(f"{r['date'].strftime('%m-%d')}:{r['unit_price']:.1f}[{'b' if r['flow_bod_vnd'] else ''}{'e' if r['flow_eod_vnd'] else ''}]" for r in led[1:])
    print(f"{label:60s} => {s}  pend={len(info['pending'])} drop={len(info['dropped'])}")
    return led, info
if __name__ == "__main__":
    # Thứ: 2026-06-01 Mon ... T = Wed 06-03
    T0,T1,T2,T3,T4 = D(2026,6,1),D(2026,6,2),D(2026,6,3),D(2026,6,4),D(2026,6,5)
    flat = lambda extra_from=None, amt=0: [R(T1,1e9), R(T2,1e9 + (amt if extra_from and T2>=extra_from else 0)), R(T3,1e9 + (amt if extra_from and T3>=extra_from else 0)), R(T4, 1e9 + (amt if extra_from else 0))]
    print("== K1 4 dòng bảng (thị trường đứng yên, chụp 19:10, T=06-03)")
    # 1. Nạp 200tr 20:00 ngày T, mẫu mặc định (không timing, không time_ict) -> load_flows phải từ chối
    import json, tempfile, os
    def lf(recs):
        p = tempfile.mktemp(suffix=".json", dir="/tmp/ar2"); json.dump({"X": recs}, open(p,"w"))
        try: return acf.load_flows("X", flows_path=p)
        except Exception as e: return f"{type(e).__name__}: {e}"
        finally: os.remove(p)
    print("1 load (no time_ict):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x"}]))
    print("1b load (timing=eod, no time_ict):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","timing":"eod"}]))
    print("1c load (time_ict='' ):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","time_ict":""}]))
    print("1d load (time_ict=None):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","time_ict":None}]))
    print("1e load (time_ict='24:00'):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","time_ict":"24:00"}]))
    print("1f load (time_ict='9:5'):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","time_ict":"9:5"}]))
    print("1g load (time_ict=930 int):", lf([{"date":"2026-06-03","amount_vnd":200e6,"kind":"deposit","evidence":"x","time_ict":930}]))
    # 2. nạp 20:00 ngày T có time_ict -> bod T+1, 0%
    rows = [R(T1,1e9),R(T2,1e9),R(T3,1.2e9),R(T4,1.2e9)]
    run("2 nạp 200tr 20:00 T (sau chụp)", rows, [F(T2,"20:00",200e6)])
    run("2b cùng, khai timing=eod", rows, [F(T2,"20:00",200e6,timing="eod")])
    run("2c cùng, khai timing=bod", rows, [F(T2,"20:00",200e6,timing="bod")])
    rows = [R(T1,1e9),R(T2,1e9),R(T3,0.8e9),R(T4,0.8e9)]
    run("3 rút 200tr 20:00 T", rows, [F(T2,"20:00",-200e6)])
    # asof T (flow treo)
    rows = [R(T1,1e9),R(T2,1e9)]
    r = run("4 nạp 20:00 T, asof T (chỉ có dòng tới T)", rows, [F(T2,"20:00",200e6)])
    res = npr.compute_period_returns("X", T2, rows, {"inception_date":"2026-06-01","starting_capital":1e9}, [F(T2,"20:00",200e6)])
    print("   asof T:", res["inception"]["return_pct"], "pending:", res["pending_flows"])
    rows = [R(T1,1e9),R(T2,1.2e9),R(T3,1.2e9)]
    run("5 nạp 16:00 T (sau đóng cửa, trước chụp) -> eod T", rows, [F(T2,"16:00",200e6)])
    run("5b nạp 10:00 T (trong phiên) -> bod T", rows, [F(T2,"10:00",200e6)])
    run("6 nạp 14:45 đúng giờ đóng cửa", rows, [F(T2,"14:45",200e6)])
    run("6b nạp 14:44", rows, [F(T2,"14:44",200e6)])
    run("6c nạp 14:44:59", rows, [F(T2,"14:44:59",200e6)])
    run("7 nạp 19:10 đúng phút chụp (không giây)", rows, [F(T2,"19:10",200e6)])
    run("7b nạp 19:10:00 đúng giây chụp", rows, [F(T2,"19:10:00",200e6)])
    run("7c nạp 19:10:01 sau chụp 1s (nav đã có tiền!)", rows, [F(T2,"19:10:01",200e6)])
    run("7d nạp 19:09:59", rows, [F(T2,"19:09:59",200e6)])
