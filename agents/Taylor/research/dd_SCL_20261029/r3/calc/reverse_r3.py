"""Định giá ngược SAU khoá: r ngầm định để giá trị kỳ vọng (sau CK thanh khoản 1 tỷ) = TERP; E cần thiết ở r 13,5%."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("m", os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_r3.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)   # chạy lại model (ghi đè out giống hệt — kiểm md5 sau)
C = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare_r3_out.json")))
terp, d = C["terp"], C["ref_discount"]
lo, hi = 0.06, 0.135
for _ in range(60):
    mid = (lo + hi) / 2
    v = m.summary(m.run(mid))["v_post"] * (1 - d)
    lo, hi = (lo, mid) if v < terp else (mid, hi)
r_imp = (lo + hi) / 2
S = m.summary(m.run(m.R0)); mult = S["v_total_pre"] / S["e_exist"]
e_need = (terp / (1 - d) * m.SH_POST / 1e9 - m.PROCEEDS) / mult
old = dict(E=.3*65+.5*135+.2*180, V=.3*65*9+.5*135*9+.2*180*10)
bridge = dict(old_total=old["V"], old_ps=old["V"]*1e9/m.SH_POST, old_mult=old["V"]/old["E"],
              dE=(S["e_exist"]-old["E"])*old["V"]/old["E"], dMult=S["e_exist"]*(mult-old["V"]/old["E"]), proceeds=m.PROCEEDS,
              new_total=S["v_total_pre"]+m.PROCEEDS)
bridge.update({k + "_ps": v * 1e9 / m.SH_POST for k, v in list(bridge.items()) if k in ("dE", "dMult", "proceeds")})
out = dict(r_implied=r_imp, dep_implied=m.DEP0 + (r_imp - m.R0), mult_avg=mult, e_needed_at_r0=e_need, e_now=S["e_exist"], bridge_old_new=bridge)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reverse_r3_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
