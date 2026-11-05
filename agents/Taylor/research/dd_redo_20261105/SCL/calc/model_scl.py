"""SCL — DD redo 05/11/2026 (job Taylor_20261105_014130).
Khung định giá = r3 03/11 (đã theo luật skill 03/11: dự án mới giá vốn/NPV 0, r neo lãi huy động, CK thanh khoản),
mã lõi chép NGUYÊN VĂN ở scl_r3_core.py (tái lập: model_r3_out.txt md5 trùng r3 gốc; json chỉ lệch float ~1e-12).
File này: r lấy từ ddg2 (lãi huy động 04/11), CK thanh khoản từ ddg2 (cùng phương pháp đăng ký trước, dữ liệu tới 04/11),
số chuẩn hoá liên mã (tâm = kỳ vọng trọng số; P10/P50/P90 lưới 108), giá 04/11 (CUM-quyền; ĐKCC 10/11/2026).
Chạy: $DNA_PYEXE -I model_scl.py → model_scl_out.json/.txt
"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2"))
import ddg2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import scl_r3_core as core   # chạy lại lõi r3 (ghi model_r3_out.* trong thư mục này)

R = g.r_info()
r0 = R["r"]
L = g.liquidity("SCL")
PX, PX_DATE = L["price"], L["price_date"]
TERP = (PX + core.RATIO * core.SUB_PX) / (1 + core.RATIO)
disc = L["ref_discount"]


def stats(r):
    rows = core.run(r)
    tot = sum(x["w"] for x in rows)
    out = {}
    for key in ("v_cum", "v_post"):
        out[key] = dict(E=sum(x[key] * x["w"] for x in rows) / tot,
                        P=g.wpct([x[key] for x in rows], [x["w"] for x in rows]))
    out["n"] = len(rows)
    out["branch_post"] = {b: sum(x["v_post"] * x["w"] for x in rows if x["branch"] == b) /
                          sum(x["w"] for x in rows if x["branch"] == b) for b in core.BRANCH_W}
    out["branch_cum"] = {b: sum(x["v_cum"] * x["w"] for x in rows if x["branch"] == b) /
                         sum(x["w"] for x in rows if x["branch"] == b) for b in core.BRANCH_W}
    return out


S = stats(r0)
cum, post = S["v_cum"], S["v_post"]
E_pre, E_post = cum["E"], cum["E"] * (1 - disc)                 # chuẩn: giá 04/11 là CUM ⇒ so giá trị TRƯỚC quyền
P_pre = cum["P"]; P_post = {k: v * (1 - disc) for k, v in P_pre.items()}
EP_pre, EP_post = post["E"], post["E"] * (1 - disc)              # cơ sở SAU quyền (so TERP)
PP_post = {k: v * (1 - disc) for k, v in post["P"].items()}

sens_r = {}
for key, rr in g.r_grid(r0).items():
    s = stats(rr)
    sens_r[key] = dict(r=rr, cum_post_liq=s["v_cum"]["E"] * (1 - disc), post_post_liq=s["v_post"]["E"] * (1 - disc),
                       pct=s["v_cum"]["E"] / cum["E"] - 1)

OLD = dict(low=18600, center=21400, high=23900, dd_date="2026-10-29 (r3 03/11)", basis="SAU quyền, sau CK 5 tỷ")
out = dict(ticker="SCL", asof_price_date=PX_DATE, price=PX, price_basis="CUM-quyền (ĐKCC 10/11/2026)", terp=TERP,
           r=r0, r_info=R, liq=L, grid_n=S["n"], branch_weights=core.BRANCH_W,
           branch_cum_pre=S["branch_cum"], branch_post_pre=S["branch_post"],
           center_pre_liq=E_pre, center_post_liq=E_post, P_pre=P_pre, P_post=P_post,
           post_rights=dict(center_pre_liq=EP_pre, center_post_liq=EP_post, P_post=PP_post,
                            label_terp=g.label(TERP, PP_post["p10"], PP_post["p90"]), terp_vs_center=TERP / EP_post - 1),
           par_lower_bound_post_liq=dict(cum=core.PAR["v_cum"] * (1 - disc), post=core.PAR["v_post"] * (1 - disc)),
           sens_r=sens_r, label=g.label(PX, P_post["p10"], P_post["p90"]),
           px_vs_center=PX / E_post - 1, px_vs_p10=PX / P_post["p10"] - 1, px_vs_p90=PX / P_post["p90"] - 1,
           zone_old=OLD, center_vs_old=EP_post / OLD["center"] - 1,
           core_reproduced="model_r3_out.txt md5 f9e7346cfe70813e2c37763d7f6153d1 = dd_SCL_20261029/r3/calc")
json.dump(out, open(os.path.join(HERE, "model_scl_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
lines = [f"SCL giá {f(PX)} ({PX_DATE}, cum) TERP {f(TERP)} | r {r0:.4f} (neo {R['anchor']['rate']}% {R['anchor']['date']}; nay {R['current']['rate']}%)",
         f"CK thanh khoản {disc:.2%} @5 tỷ (ADV120 trung vị {L['adv120_med_ty']:.2f} tỷ; 10%/20%: {L['sizes'][1]['days_p10']:.1f}/{L['sizes'][1]['days_p20']:.1f} phiên; 1 tỷ {L['sizes'][0]['discount']:.2%}, 10 tỷ {L['sizes'][2]['discount']:.2%})",
         f"CUM (38,84tr cp): tâm TRƯỚC {f(E_pre)} SAU {f(E_post)} | lưới n={S['n']} TRƯỚC " + " ".join(f"{k} {f(v)}" for k, v in P_pre.items()),
         f"CUM SAU CK " + " ".join(f"{k} {f(v)}" for k, v in P_post.items()),
         f"Nhánh cum (trước CK): " + " ".join(f"{k} {f(v)}" for k, v in S['branch_cum'].items()),
         f"SAU QUYỀN (44,84tr cp): tâm TRƯỚC {f(EP_pre)} SAU {f(EP_post)} | " + " ".join(f"{k} {f(v)}" for k, v in PP_post.items()) + f" | TERP so tâm {TERP/EP_post-1:+.1%} ⇒ {out['post_rights']['label_terp']}",
         f"Giá cum so tâm cum {PX/E_post-1:+.1%} | so P10 {PX/P_post['p10']-1:+.1%} | so P90 {PX/P_post['p90']-1:+.1%} ⇒ {out['label']}",
         "Độ nhạy r (cum, SAU CK): " + " | ".join(f"{k} {f(v['cum_post_liq'])} ({v['pct']:+.1%})" for k, v in sens_r.items()),
         f"Cận dưới nợ mệnh giá (SAU CK): cum {f(out['par_lower_bound_post_liq']['cum'])} post {f(out['par_lower_bound_post_liq']['post'])}",
         f"Cũ r3: tâm sau quyền {f(OLD['center'])} vùng {f(OLD['low'])}–{f(OLD['high'])} ⇒ mới/cũ (cùng cơ sở sau quyền) {EP_post/OLD['center']-1:+.1%}"]
open(os.path.join(HERE, "model_scl_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
