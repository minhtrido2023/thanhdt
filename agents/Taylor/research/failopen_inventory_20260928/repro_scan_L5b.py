import ast, json, sys, os
D="mike/agents/Taylor/research/failopen_inventory_20260928"
files=[l.strip() for l in open(D+"/scope_live_py.txt") if l.strip()]
# tier map: reuse repro_tier heuristic by importing? simpler: re-declare A/B sets by name
A_NAMES={"executor.py","plan.py","brokers.py","plan_funding_gate.py","plan_cash_commitment.py",
 "due_diligence.py","config.py","strategies.py","bot_execute.py","daily_nav_snapshot.py",
 "verify_account_snapshot.py","compute_active_nav.py","compute_jit_unpark.py","compute_park_trim.py",
 "merge_park_orders.py","reconcile_equity.py","nav_period_returns.py","report_return_gate.py",
 "dividend_adjusted_return.py","account_cash_flows.py","marginability_check.py","vn_market.py",
 "dnse_api.py","report_delivery_gate.py"}
B_PREF=("rating_8l","macro_state_live","macro_healthcheck","dna_report","dna_card","lag_forensic_filter",
 "pt_v2","rank_8l","unified_screener","dcf_","golive_recommend","publish_gated_state",
 "dc_book_waterfall","edge_health_monitor","sector_lens_monitor","capit_episode","value_radar",
 "sbv_macro_overlay","idle_rate_proxy","dt5g_freshness","discretionary_")
def tier(p):
    b=os.path.basename(p)
    if "selfcheck" in b or b.startswith("test_"): return "S"
    if b in A_NAMES or "/trading_bot/" in p or p.startswith("trading_bot/"): return "A"
    if any(b.startswith(x) for x in B_PREF): return "B"
    return "C"

READERS={"load","loads","read_csv","read_json","read_parquet","read_pickle","safe_load","read_excel"}
def is_num(n):
    if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)) and not isinstance(n.value,bool): return True
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub): return is_num(n.operand)
    if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value!="" : return True
    return False
out=[]
for p in files:
    t=tier(p)
    if t not in ("A","B"): continue
    try: src=open(p,encoding="utf-8").read(); tree=ast.parse(src)
    except Exception as e: out.append({"file":p,"line":0,"kind":"PARSE_FAIL","code":str(e),"tier":t}); continue
    lines=src.splitlines()
    # vars bound to a file-read result (1 hop)
    filevars=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AnnAssign)):
            val=n.value
            if isinstance(val,ast.Call):
                f=val.func
                nm=f.attr if isinstance(f,ast.Attribute) else (f.id if isinstance(f,ast.Name) else "")
                if nm in READERS:
                    tgts=n.targets if isinstance(n,ast.Assign) else [n.target]
                    for tg in tgts:
                        for sub in ast.walk(tg):
                            if isinstance(sub,ast.Name): filevars.add(sub.id)
    for n in ast.walk(tree):
        code=lines[n.lineno-1].strip() if hasattr(n,"lineno") and n.lineno<=len(lines) else ""
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
            if n.func.attr=="get" and len(n.args)==2 and is_num(n.args[1]):
                base=n.func.value
                root=base
                while isinstance(root,(ast.Subscript,ast.Attribute,ast.Call)):
                    root=root.value if not isinstance(root,ast.Call) else root.func
                rid=root.id if isinstance(root,ast.Name) else ""
                out.append({"file":p,"line":n.lineno,"kind":"GET_DEFAULT","fromfilevar":rid in filevars,"root":rid,"code":code[:200],"tier":t})
            if n.func.attr=="fillna" and n.args and is_num(n.args[0]):
                out.append({"file":p,"line":n.lineno,"kind":"FILLNA","fromfilevar":None,"root":"","code":code[:200],"tier":t})
        if isinstance(n,ast.BoolOp) and isinstance(n.op,ast.Or) and len(n.values)==2 and is_num(n.values[1]):
            v0=n.values[0]
            if isinstance(v0,(ast.Subscript,ast.Call,ast.Attribute)):
                out.append({"file":p,"line":n.lineno,"kind":"OR_DEFAULT","fromfilevar":None,"root":"","code":code[:200],"tier":t})
json.dump(out,open(sys.argv[1],"w"),ensure_ascii=False,indent=0)
from collections import Counter
print(len(out), Counter((o["kind"],o["tier"]) for o in out))
