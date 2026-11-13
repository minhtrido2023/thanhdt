import json,glob,sys,collections,re
S="denied by the Claude Code auto mode classifier"
byday=collections.Counter(); bycmd=collections.Counter(); tot=0
for f in glob.glob(sys.argv[1]):
    uses={}
    for ln in open(f,errors="ignore"):
        if S not in ln and '"tool_use"' not in ln: continue
        try: o=json.loads(ln)
        except: continue
        c=(o.get("message") or {}).get("content")
        if not isinstance(c,list): continue
        for b in c:
            if not isinstance(b,dict): continue
            if b.get("type")=="tool_use":
                inp=b.get("input",{}); cmd=inp.get("command") or inp.get("file_path") or b.get("name")
                uses[b.get("id")]=(b.get("name"),str(cmd))
            elif b.get("type")=="tool_result" and S in json.dumps(b.get("content"),ensure_ascii=False):
                tot+=1; byday[(o.get("timestamp") or "")[:10]]+=1
                n,cmd=uses.get(b.get("tool_use_id"),("?","?"))
                m=re.search(r"(bin/[\w.-]+|mike/kb/\S+|\.claude/\S+)",cmd)
                bycmd[n+":"+(m.group(1) if m else cmd[:50])]+=1
print("total",tot); print(sorted(byday.items())); print(bycmd.most_common(15))
