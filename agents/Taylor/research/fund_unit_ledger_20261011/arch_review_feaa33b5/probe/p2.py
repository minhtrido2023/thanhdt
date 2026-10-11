import sys, datetime, json, os, tempfile, subprocess, shutil
from pathlib import Path
WT="/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011/bin"
sys.path.insert(0, WT); sys.dont_write_bytecode=True
import account_cash_flows as acf, nav_unit_ledger as nul, nav_period_returns as npr
D=datetime.date
tmp=Path(tempfile.mkdtemp(prefix="archrev_p2_"))
rows=[nul.NavRow(D(2026,7,2),1.01e9),nul.NavRow(D(2026,7,3),1.02e9),nul.NavRow(D(2026,7,6),1.03e9)]
led,_=nul.build_ledger(rows,[],D(2026,7,1),1e9)
path=str(tmp/"nav_unit_ledger_SpaceX.csv")

print("== C1. TOCTOU: tiến trình khác chốt xen giữa read_sealed() và lần đọc old_text thứ hai trong seal()")
nul.seal(path, led[:2])                      # sổ có tới 07-02
orig_read=nul.read_sealed
def racing_read(p):
    out=orig_read(p)
    nul.read_sealed=orig_read
    nul.seal(p, led)                         # 'tiến trình B' chốt nốt 07-03, 07-06 ngay sau khi A đọc
    return out
nul.read_sealed=racing_read
sealed,new=nul.seal(path, led)               # 'tiến trình A'
nul.read_sealed=orig_read
print("  A báo thêm:", [str(r['date']) for r in new])
print("  file:", [l.split(',')[0] for l in open(path).read().splitlines()[1:]])
try: nul.read_sealed(path); print("  đọc lại: OK")
except Exception as e: print("  đọc lại:", type(e).__name__, str(e)[:120])
os.remove(path)

print("== C2. sửa tay cột suy ra thành nan/inf trong sổ đã chốt")
nul.seal(path, led)
txt=open(path).read().splitlines(keepends=True)
for val in ("nan","inf"):
    p=txt[2].split(","); p[6]=val; p[5]=val
    open(path,"w").write("".join(txt[:2]+[",".join(p)]+txt[3:]))
    try: print(f"  unit_price/units={val}: diffs =", nul.diff_against_sealed(led, nul.read_sealed(path)))
    except Exception as e: print("  ",type(e).__name__, e)
open(path,"w").write("".join(txt))

print("== C3. nav_history có 2 dòng trùng ngày + flow ngày đó")
dup=[nul.NavRow(D(2026,7,2),1e9),nul.NavRow(D(2026,7,3),1.2e9),nul.NavRow(D(2026,7,3),1.2e9)]
l2,_=nul.build_ledger(dup,[{"date":D(2026,7,3),"amount_vnd":200e6,"kind":"deposit","evidence":"x","timing":"eod","time_ict":None}],D(2026,7,1),1e9)
print("  ", [(str(r['date']),r['flow_eod_vnd'],round(r['unit_price'],2)) for r in l2])
p3=str(tmp/"dup.csv")
try:
    nul.seal(p3,l2); print("  seal ghi được; đọc lại:", end=" "); nul.read_sealed(p3); print("OK")
except Exception as e: print(type(e).__name__, str(e)[:100])

print("== C4. chạy lại daily_nav_snapshot cho ngày đã chốt (NAV đổi 1.234đ) ⇒ CLI nav_period_returns")
sb=tmp/"WC"; (sb/"data/execution_logs").mkdir(parents=True); (sb/"mike/bin").mkdir(parents=True)
(sb/"wc_env.sh").write_text(""); (sb/"mike/MIKE.md").write_text("x")
for f in ("nav_period_returns.py","nav_unit_ledger.py","account_cash_flows.py","report_delivery_gate.py","wc_paths.py"):
    shutil.copy2(f"{WT}/{f}", sb/"mike/bin"/f)
RD="/home/trido/thanhdt/WorkingClaude/data"
for f in ("account_inception.json","account_cash_flows.json"): shutil.copy2(f"{RD}/{f}", sb/"data"/f)
for a in ("SpaceX","ZaloPay"): shutil.copy2(f"{RD}/execution_logs/nav_history_{a}.csv", sb/"data/execution_logs")
env={k:v for k,v in os.environ.items() if k not in("TZ","WC_ROOT","MIKE_ROOT")}
run=lambda *a: subprocess.run([sys.executable,*a],cwd=sb/"mike",capture_output=True,text=True,env=env)
p=run("bin/nav_unit_ledger.py","--account","SpaceX","--seal"); print("  seal rc",p.returncode,p.stdout.splitlines()[1][:110])
h=sb/"data/execution_logs/nav_history_SpaceX.csv"; L=h.read_text().splitlines()
last=L[-1].split(","); print("   dòng cuối trước:", last[0], last[1], last[7])
last[1]=str(int(last[1])+1234); last[7]="2026-10-09T21:15:07"; L[-1]=",".join(last); h.write_text("\n".join(L)+"\n")
p=run("bin/nav_period_returns.py","--account","SpaceX","--report-date","2026-10-09"); print("  nav_period_returns rc",p.returncode,"|",p.stderr.strip().splitlines()[0][:160]); print("    ", p.stderr.strip().splitlines()[1][:160] if len(p.stderr.strip().splitlines())>1 else "")
p=run("bin/nav_unit_ledger.py","--account","SpaceX","--seal"); print("  seal lại rc",p.returncode)

print("== C5. cổng báo cáo khi sổ lệch: báo cáo ghi số SAI (+9,99%) có bị chặn không?")
sys.path.insert(0,str(sb/"mike/bin"))
for m in ("report_delivery_gate","wc_paths","nav_period_returns","nav_unit_ledger","account_cash_flows"): sys.modules.pop(m,None)
sys.path.remove(WT)
import report_delivery_gate as rdg
print("  rdg.ROOT =", rdg.ROOT)
rep=tmp/"SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
rep.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | +9,99% | x | y |\n",encoding="utf-8")
try:
    rdg._check_period_returns(rep); print("  ⇒ KHÔNG chặn (đi tiếp)")
except Exception as e: print("  ⇒ CHẶN:", str(e)[:200])
# đối chứng: sổ khớp lại ⇒ cổng chặn số sai
last[1]=str(int(last[1])-1234); L[-1]=",".join(last); h.write_text("\n".join(L)+"\n")
try:
    rdg._check_period_returns(rep); print("  đối chứng (sổ khớp) ⇒ KHÔNG chặn")
except Exception as e: print("  đối chứng (sổ khớp) ⇒ CHẶN:", str(e)[:160])
print("== C6. NAV_UNIT_LEDGER_DIR kế thừa từ môi trường làm tắt đối chiếu")
last[1]=str(int(last[1])+1234); L[-1]=",".join(last); h.write_text("\n".join(L)+"\n")
e2=dict(env, NAV_UNIT_LEDGER_DIR=str(tmp/"empty")); (tmp/"empty").mkdir()
p=subprocess.run([sys.executable,"bin/nav_period_returns.py","--account","SpaceX","--report-date","2026-10-09"],cwd=sb/"mike",capture_output=True,text=True,env=e2)
print("  rc",p.returncode, json.loads(p.stdout)["unit_ledger"] if p.returncode==0 else p.stderr[:100])
shutil.rmtree(tmp)
