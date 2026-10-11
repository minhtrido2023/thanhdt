import subprocess, sys, os, shutil, json
sys.path.insert(0, "/tmp/archrev_fu/mut")
from mutants import M
SB="/tmp/archrev_fu/sbx/WC/mike"; BIN=SB+"/bin"
PRISTINE="/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011/bin"
TESTS=[["bin/nav_unit_ledger_selfcheck.py"],["bin/nav_flow_term_selfcheck.py"],["bin/nav_jump_flow_gate_selfcheck.py"],["bin/report_delivery_gate_selfcheck.py"],["bin/nav_period_returns.py","--selfcheck"]]
env={k:v for k,v in os.environ.items() if k not in ("TZ","WC_ROOT","MIKE_ROOT","NAV_UNIT_LEDGER_DIR","ACCOUNT_CASH_FLOWS_PATH")}
env["PYTHONDONTWRITEBYTECODE"]="1"
only=set(sys.argv[1:])
res=[]
for m in M:
    mid,fn,old,new=m[:4]; occ=m[4] if len(m)>4 else None
    if only and mid not in only: continue
    src=open(f"{PRISTINE}/{fn}",encoding="utf-8").read()
    cnt=src.count(old)
    if cnt==0 or (occ is None and cnt!=1):
        res.append((mid,fn,"NOAPPLY",f"count={cnt}","")); print(mid,"NOAPPLY",cnt); continue
    if occ is None: mut=src.replace(old,new,1)
    else:
        idx=-1
        for _ in range(occ+1): idx=src.index(old,idx+1)
        mut=src[:idx]+new+src[idx+len(old):]
    line=src[:src.index(old) if occ is None else idx].count("\n")+1
    open(f"{BIN}/{fn}","w",encoding="utf-8").write(mut)
    verdict="SURVIVED"; by=""; detail=""
    try:
        for t in TESTS:
            try:
                p=subprocess.run([sys.executable]+t,cwd=SB,capture_output=True,text=True,env=env,timeout=180)
            except subprocess.TimeoutExpired:
                verdict="TIMEOUT"; by=t[0]; break
            if p.returncode!=0:
                out=p.stdout+p.stderr
                by=os.path.basename(t[0])+(" --selfcheck" if len(t)>1 else "")
                if "ASSERT-FAIL" in out or "AssertionError" in out or "FAIL" in out.replace("ASSERT-FAIL",""):
                    verdict="KILLED_ASSERT"
                else:
                    verdict="KILLED_CRASH"
                tail=[l for l in out.strip().splitlines() if l.strip()]
                detail=(tail[-1] if tail else "")[:230]
                break
    finally:
        shutil.copy2(f"{PRISTINE}/{fn}",f"{BIN}/{fn}")
    res.append((mid,fn,verdict,by,detail,line)); print(mid,fn,f"L{line}",verdict,by,"|",detail,flush=True)
json.dump(res,open("/tmp/archrev_fu/mut/results.json","w"),ensure_ascii=False,indent=1)
from collections import Counter
print(Counter(r[2] for r in res))
