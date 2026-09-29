import ast,sys,json,os
EMPTY_CONSTS=(None,0,"",False)
def is_broad(h):
    if h.type is None: return True   # bare except
    names=[]
    t=h.type
    for n in (t.elts if isinstance(t,ast.Tuple) else [t]):
        names.append(ast.unparse(n))
    return any(x in ("Exception","BaseException") for x in names)

def empty_val(node):
    """node is an expression; True if it's an 'empty' sentinel"""
    if node is None: return True
    if isinstance(node,ast.Constant) and (node.value is None or node.value==0 or node.value=="" or node.value is False):
        return True
    if isinstance(node,(ast.Dict,ast.List,ast.Set,ast.Tuple)) and not (getattr(node,'elts',None) or getattr(node,'keys',None)):
        return True
    return False

def classify(h):
    """return list of (label, detail)"""
    body=[s for s in h.body]
    out=[]
    real=[s for s in body if not isinstance(s,ast.Pass)]
    # L1: pass only (or pass + nothing)
    if all(isinstance(s,ast.Pass) for s in body):
        return [("L1","except: pass")]
    if len(body)==1 and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):
        return [("L1","except: docstring-only (no-op)")]
    # continue-only => swallow in loop
    if all(isinstance(s,(ast.Pass,ast.Continue)) for s in body):
        return [("L1","except: continue (skip record silently)")]
    # L3: return empty
    for s in body:
        if isinstance(s,ast.Return) and empty_val(s.value):
            out.append(("L3","except -> return %s"%(ast.unparse(s.value) if s.value is not None else "None")))
    # L2: has print/log then falls through (no raise, no sys.exit) OR assigns empty
    has_raise=any(isinstance(s,ast.Raise) for s in ast.walk(h))
    has_exit=any(isinstance(n,ast.Call) and "exit" in ast.unparse(n.func) for s in body for n in ast.walk(s))
    has_report=any(isinstance(n,ast.Call) and any(k in ast.unparse(n.func).lower() for k in ("print","log","warn","err","stderr"))
                   for s in body for n in ast.walk(s))
    assigns_empty=[ast.unparse(s.targets[0]) for s in body if isinstance(s,ast.Assign) and empty_val(s.value)]
    if not has_raise and not has_exit:
        if assigns_empty:
            out.append(("L2","except -> %s = empty, continue"%(",".join(assigns_empty))))
        elif has_report and not any(isinstance(s,ast.Return) for s in body):
            out.append(("L2","except -> report only, continue"))
        elif not has_report and not out and not any(isinstance(s,ast.Return) for s in body):
            out.append(("L2","except -> silent fallthrough"))
    return out

def enclosing(tree):
    m={}
    for fn in ast.walk(tree):
        if isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            for n in ast.walk(fn):
                if hasattr(n,'lineno') and n not in m:
                    m[id(n)]=fn.name
    return m

hits=[]
files=[l.strip() for l in open(sys.argv[1]) if l.strip()]
unparsed=[]
for f in files:
    try:
        src=open(f,encoding="utf-8",errors="replace").read()
        tree=ast.parse(src)
    except Exception as e:
        unparsed.append((f,str(e)[:80])); continue
    encl=enclosing(tree)
    lines=src.splitlines()
    for h in ast.walk(tree):
        if not isinstance(h,ast.ExceptHandler): continue
        if not is_broad(h): continue
        for lab,det in classify(h):
            try_ctx=""
            hits.append(dict(file=os.path.relpath(f,"/home/trido/thanhdt/WorkingClaude"),
                             line=h.lineno, cls=lab, detail=det,
                             func=encl.get(id(h),"<module>"),
                             exc=ast.unparse(h.type) if h.type else "bare"))
json.dump(dict(hits=hits,unparsed=unparsed),open(sys.argv[2],"w"),indent=1)
from collections import Counter
c=Counter(h["cls"] for h in hits)
print("files scanned:",len(files)-len(unparsed),"unparsed:",len(unparsed))
print(dict(c))
