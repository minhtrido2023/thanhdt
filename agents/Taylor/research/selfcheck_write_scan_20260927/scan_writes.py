#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIEC 2 — quet MOI selfcheck: cho nao GHI ra duong dan NGOAI thu muc tam?

AST, khong regex: `open(p,"w")` / `to_csv` / `to_json` / `to_parquet` / `to_pickle` /
`json.dump(_,f)` qua open / `shutil.copy*|move|copytree` / `os.replace|rename` /
`Path(...).write_text|write_bytes` / `mkdir|makedirs`.

Phan loai dich: SAFE neu bieu thuc dich (hoac bien no dan xuat tu, truy vet lien hoan trong file)
cham tempfile / mkdtemp / TemporaryDirectory / NamedTemporaryFile / '/tmp' / TMPDIR / gettempdir.
Nguoc lai => REPORT, de nguoi doc phan hang (a)/(b)/(c).
"""
import ast, os, sys, json, glob

WRITE_METHODS = {"to_csv","to_json","to_parquet","to_pickle","to_feather","to_excel",
                 "write_text","write_bytes","writestr"}
COPY_FUNCS = {"copy","copy2","copyfile","move","copytree","replace","rename","renames"}
TMP_MARKS = ("tempfile","mkdtemp","TemporaryDirectory","NamedTemporaryFile","gettempdir",
             "/tmp","/var/tmp","TMPDIR","TemporaryFile","mkstemp")

def src(n):
    try: return ast.unparse(n)
    except Exception: return "<?>"

class Scan(ast.NodeVisitor):
    def __init__(self, path, text):
        self.path=path; self.lines=text.split("\n")
        self.tmpvars=set(); self.hits=[]
    # --- pha 1: truy vet bien dan xuat tu tempfile (lap den khi on dinh) ---
    def taint(self, tree):
        changed=True
        while changed:
            changed=False
            for n in ast.walk(tree):
                if isinstance(n,(ast.Assign,ast.AnnAssign,ast.withitem)):
                    if isinstance(n,ast.withitem):
                        tgt=n.optional_vars; rhs=n.context_expr
                        if tgt is None: continue
                    else:
                        tgt=(n.targets[0] if isinstance(n,ast.Assign) else n.target); rhs=n.value
                    if rhs is None: continue
                    r=src(rhs)
                    tainted = any(m in r for m in TMP_MARKS) or any(
                        v and (v+"." in r or v+"," in r or v+")" in r or v+" " in r or r==v)
                        for v in self.tmpvars)
                    if not tainted: continue
                    for name in [x.id for x in ast.walk(tgt) if isinstance(x,ast.Name)]:
                        if name not in self.tmpvars:
                            self.tmpvars.add(name); changed=True
    def dest_safe(self, dest_src):
        if any(m in dest_src for m in TMP_MARKS): return True
        return any(v in dest_src for v in self.tmpvars)
    def add(self, node, kind, dest_node):
        d=src(dest_node) if dest_node is not None else "<?>"
        self.hits.append(dict(line=node.lineno, kind=kind, dest=d[:180],
                              safe=self.dest_safe(d), code=self.lines[node.lineno-1].strip()[:200]))
    def visit_Call(self, node):
        f=node.func
        fname = f.attr if isinstance(f,ast.Attribute) else (f.id if isinstance(f,ast.Name) else "")
        mod = src(f.value)[:40] if isinstance(f,ast.Attribute) else ""
        if fname=="open" or (isinstance(f,ast.Attribute) and fname=="open"):
            mode=None
            if len(node.args)>1: mode=src(node.args[1]).strip("'\"")
            for kw in node.keywords:
                if kw.arg=="mode": mode=src(kw.value).strip("'\"")
            if mode and any(c in mode for c in "wax+"):
                self.add(node,f"open(mode={mode})", node.args[0] if node.args else None)
        elif fname in WRITE_METHODS:
            if fname in ("write_text","write_bytes"):
                self.add(node,f"{mod}.{fname}", f.value)
            else:
                self.add(node,fname, node.args[0] if node.args else None)
        elif fname in COPY_FUNCS and ("shutil" in mod or "os" in mod or "Path" in mod):
            self.add(node,f"{mod}.{fname}", node.args[1] if len(node.args)>1 else None)
        elif fname in ("mkdir","makedirs") and ("os" in mod or "Path" in mod):
            self.add(node,f"{mod}.{fname}", node.args[0] if node.args else f.value)
        self.generic_visit(node)

def run(paths):
    out={}
    for p in paths:
        try: text=open(p,encoding="utf-8").read(); tree=ast.parse(text)
        except Exception as e:
            out[p]=dict(error=str(e)); continue
        s=Scan(p,text); s.taint(tree); s.visit(tree)
        unsafe=[h for h in s.hits if not h["safe"]]
        if unsafe:
            out[p]=dict(tmpvars=sorted(s.tmpvars), n_hits=len(s.hits), unsafe=unsafe)
    return out

if __name__=="__main__":
    WC="/home/trido/thanhdt/WorkingClaude"
    paths=sorted(glob.glob(f"{WC}/mike/bin/*selfcheck*.py"))+sorted(glob.glob(f"{WC}/*selfcheck*.py"))
    res=run(paths)
    print(f"QUET {len(paths)} file; {len(res)} file co it nhat 1 ghi NGOAI thu muc tam\n")
    for p,d in res.items():
        rel=p.replace(WC+"/","")
        print(f"### {rel}  ({len(d.get('unsafe',[]))} cho)")
        for h in d.get("unsafe",[]):
            print(f"   :{h['line']:5d} {h['kind']:26s} -> {h['dest']}")
    json.dump({k.replace(WC+'/',''):v for k,v in res.items()},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"scan_writes.json"),"w"),indent=1)
