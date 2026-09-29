import os,re,subprocess,sys
WC="/home/trido/thanhdt/WorkingClaude"
seed=[l.strip() for l in open("/tmp/seed.txt") if l.strip()]
live=set(p for p in seed if os.path.isfile(p))
# candidate module lookup dirs (search roots for local imports)
roots=[WC, WC+"/mike/bin", WC+"/trading_bot", WC+"/mike/agents/Taylor"]
def excl(p):
    r=os.path.relpath(p,WC)
    return (r.startswith("wt-") or "/research/" in "/"+r or r.startswith("archive/")
            or "/.claude/worktrees/" in p or "/__pycache__/" in p or r.startswith("mike/archive/"))
for hop in range(4):
    new=set()
    for f in list(live):
        try: txt=open(f,encoding="utf-8",errors="replace").read()
        except Exception: continue
        if f.endswith(".sh"):
            for m in re.finditer(r'([A-Za-z0-9_./$\{\}-]+\.(?:py|sh))',txt):
                tok=m.group(1)
                tok=re.sub(r'\$\{?[A-Za-z_][A-Za-z0-9_]*\}?/?','',tok)
                if not tok or tok.startswith("."): continue
                for r in roots+[os.path.dirname(f)]:
                    c=os.path.join(r,tok)
                    if os.path.isfile(c): new.add(os.path.realpath(c)); break
        else:
            for m in re.finditer(r'^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_.]*)',txt,re.M):
                mod=m.group(1).split('.')[0]
                for r in roots+[os.path.dirname(f)]:
                    c=os.path.join(r,mod+".py")
                    if os.path.isfile(c): new.add(os.path.realpath(c)); break
                    d=os.path.join(r,mod)
                    if os.path.isdir(d) and os.path.isfile(os.path.join(d,"__init__.py")):
                        for x in os.listdir(d):
                            if x.endswith(".py"): new.add(os.path.realpath(os.path.join(d,x)))
                        break
            # subprocess calls to other py/sh
            for m in re.finditer(r'["\']([A-Za-z0-9_./-]+\.(?:py|sh))["\']',txt):
                tok=m.group(1)
                for r in roots+[os.path.dirname(f)]:
                    c=os.path.join(r,tok)
                    if os.path.isfile(c): new.add(os.path.realpath(c)); break
    new={p for p in new if not excl(p)}
    before=len(live); live|=new
    if len(live)==before: break
live={p for p in live if not excl(p)}
py=sorted(p for p in live if p.endswith(".py"))
sh=sorted(p for p in live if p.endswith(".sh"))
open("/tmp/live_py.txt","w").write("\n".join(py)+"\n")
open("/tmp/live_sh.txt","w").write("\n".join(sh)+"\n")
print("live py:",len(py),"live sh:",len(sh))
