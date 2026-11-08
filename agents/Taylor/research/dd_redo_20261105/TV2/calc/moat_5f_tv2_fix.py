"""TV2 vòng sửa 08/11/2026 (job Taylor_20261108_024226): thêm neo Ke 13,5%, TV3+TV4 2022–25, ROE riêng TV2 2022–25.
Dùng lại nguyên hàm/trục của moat_5f_tv2.py (exec phần trước 'res = {'). Chạy: $DNA_PYEXE -I moat_5f_tv2_fix.py"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "moat_5f_tv2.py")).read().split("res = {")[0]
exec(compile(src, "moat_5f_tv2_head", "exec"))
assert abs(summ(fn_r2)["center"] - 15832) < 1.0
a_w = roe(("TV3", "TV4"), 2022, 2025); a_o = roe(("TV2",), 2022, 2025)
AN = {"Ke_13.5": r0, "TV3_TV4_2022_25_median": st.median(a_w), "TV2_own_2022_25_median": st.median(a_o),
      "TV3_TV4_2012_25_median": ANCH["TV3_TV4"]["median"]}
res = {k: summ(make_fn(a)) for k, a in AN.items()}
out = dict(anchors=AN, n_peer_2022_25=len(a_w), n_own_2022_25=len(a_o), res=res)
json.dump(out, open(os.path.join(HERE, "moat_5f_tv2_fix_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
L_ = [f"neo {k}: {AN[k]:.4%}" for k in AN]
for k, s in res.items():
    L_.append(f"NONE {k:26s} tâm {s['center']:7,.0f} P10 {s['p10']:7,.0f} P50 {s['p50']:7,.0f} P90 {s['p90']:7,.0f} dưới giá {s['below']:.1%} {s['label']} | 40tr tâm {s['sleeve_40tr']['center']:,.0f} P90 {s['sleeve_40tr']['p90']:,.0f} {s['sleeve_40tr']['label']}")
open(os.path.join(HERE, "moat_5f_tv2_fix_out.txt"), "w").write("\n".join(L_) + "\n")
print("\n".join(L_))
