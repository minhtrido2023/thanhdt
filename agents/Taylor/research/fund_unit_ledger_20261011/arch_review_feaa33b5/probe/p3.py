import sys, json, os, tempfile, importlib
tree=sys.argv[1]
sys.path.insert(0, tree); sys.dont_write_bytecode=True
import daily_nav_snapshot as D
tmp=tempfile.mkdtemp()
def ff(recs):
    p=os.path.join(tmp,"f.json"); json.dump({"SpaceX":recs},open(p,"w")); return p
HIST=[{"date":"2026-07-02","nav":"1000000000"},{"date":"2026-07-03","nav":"1000000000"}]
cases={
 "T7 nạp 200tr (20%), bản ghi mặc định (không khai timing), snapshot T2 07-06": ([{"date":"2026-07-04","amount_vnd":200000000,"kind":"deposit","evidence":"sao kê"}],"2026-07-06",1.2e9),
 "nạp 200tr đúng ngày T2, mặc định": ([{"date":"2026-07-06","amount_vnd":200000000,"kind":"deposit","evidence":"sao kê"}],"2026-07-06",1.2e9),
 "nạp 20:00 thứ Sáu 07-03 (sau snapshot), mặc định, snapshot T2": ([{"date":"2026-07-03","amount_vnd":200000000,"kind":"deposit","evidence":"sao kê"}],"2026-07-06",1.2e9),
 "bản ghi tương lai 07-08 (rút dự kiến) + nhảy thật 20% hôm nay có market_only": ([{"date":"2026-07-08","amount_vnd":-50000000,"kind":"withdraw","evidence":"x","timing":"eod"},{"date":"2026-07-06","amount_vnd":0,"kind":"market_only","evidence":"y"}],"2026-07-06",1.2e9),
}
for name,(recs,date,nav) in cases.items():
    ok,msg=D.nav_jump_verdict("SpaceX",date,1e9,nav,15.0,HIST,components={},flows_path=ff(recs))
    print(f"- {name}\n    ok={ok} :: {(msg or '').strip().splitlines()[0][:150] if msg else None}")
    if msg and "Lỗi thật" in msg: print("    ", [l for l in msg.splitlines() if "Lỗi thật" in l][0][:200])
