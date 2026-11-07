"""SCL — ADDENDUM 5F (bước 3c) 07/11/2026, job Taylor_20261107_123141. KHÔNG sửa REPORT_r2/SUMMARY.
Mô hình MÙ GIÁ: lõi = scl_r3_core.py (không đổi); lưới = y hệt model_scl_r2.py (chép AXES/fn, KHÔNG import để không ghi đè out/LOCK).
Giá + CK thanh khoản đọc từ model_scl_r2_out.json (chỉ dùng cho nhãn/% dưới giá, sau khi giá trị đã tính).
Chân đối chứng WIDE (= REPORT_r2) phải tái lập tâm 22.769.

Biến thể (luật 3c):
  RONIC=Ke : bội số (1 − g/ROE)/(r − g) với ROE := r ⇒ = 1/r, áp ĐỐI XỨNG cho mọi ô ROE (15% và 20% đều > Ke 13,5%).
  Biên về TB chu kỳ NGÀNH: m_ind = TB biên ròng năm 2020..2025 + TTM của từng peer (cùng cửa sổ với norm '2020-TTM' của SCL),
    rồi trung vị / trung bình qua peer. Fade tuyến tính từ biên của ô lưới (sau nhánh) về m_ind trong N năm:
    V = E_ind/r + Σ_{t=1..N} (E_ô − E_ind)·(N−t+1)/N /(1+r)^t  (năm 1 chiết khấu 1 kỳ — nhất quán quy ước mô hình hiện hành
    áp bội số lên E_TTM như E năm tới).  NONE: N=2 (fade nhanh); NARROW: N=5; N=0 = cận dưới tức thời.
Chạy: $DNA_PYEXE -I scl_5f.py → scl_5f_out.json/.txt
"""
import contextlib, io, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import scl_r3_core as c

B = 1e9
R2 = json.load(open(os.path.join(HERE, "model_scl_r2_out.json")))
r0 = R2["r"]; PX = R2["price"]; DISC = R2["liq"]["ref_discount"]; SLEEVE40 = R2["liq"]["sleeve_discount"]["40tr"]
TERP = R2["terp"]
RECV_CONC = 116.0 * 0.585
BR = {"CYCLICAL": 0.50, "ADMIN_GATED": 0.30, "STRUCTURAL": 0.20}
AXES = dict(
    branch=[(b, b, w) for b, w in BR.items()],
    rev=[(x, x, 0.5) for x in c.GRID["rev"]],
    norm=[(x, x, 1 / 3) for x in c.GRID["norm"]],
    g=[(f"g{x:.0%}", x, 1 / 3) for x in c.GRID["g"]],
    roe=[(f"roe{x:.0%}", x, 0.5) for x in c.GRID["roe"]],
    recv=[("0%", 0.0, 0.75), ("20%", 0.20, 0.20), ("50%", 0.50, 0.05)],
)
I_CIP = c.GRID["i_cip"][0]

# ---- Biên ròng năm peer (NP 4Q / DT 4Q), bq tav2_bq.ticker_financial 07/11/2026, quý 2020Q4..2025Q4 + TTM mới nhất ----
# Peer NỘI ĐỊA, KHÔNG phải đối thủ AAC trực tiếp (đối thủ AAC chủ yếu chưa niêm yết). VGC gồm cả KCN (đẩy biên lên).
PEER_NPM = {
    "VGC": [.0629, .1093, .1196, .0922, .0917, .1038, .1131],
    "CVT": [.0855, .0619, .0460, .0203, .0319, .0222, .0210],   # TTM = 2026Q2 (chưa có Q3)
    "VIT": [.0460, .0367, .0254, .0000, .0243, .0315, .0305],
    "VHL": [.0442, .0267, .0001, -.0565, -.0579, .0270, .0347],
    "TCR": [-.0315, .0099, .0020, -.0173, -.0668, .0015, .0292],
    "HT1": [.0729, .0495, .0276, .0022, .0082, .0344, .0446],
    "BTS": [.0056, .0168, .0167, -.0353, -.0734, .0112, .0212],
    "HOM": [.0010, .0010, .0102, -.0171, -.0388, .0129, .0130],
    "VCX": [.0240, .0361, .0095, .0113, .0267, .0338, .0213],
}
SET_A = ["VGC", "CVT", "VIT", "VHL", "TCR"]            # gạch/ốp lát/VLXD tường-hoàn thiện
SET_B = SET_A + ["HT1", "BTS", "HOM", "VCX"]           # + xi măng
pm = {k: st.mean(v) for k, v in PEER_NPM.items()}
M_IND = {"A_median": st.median([pm[k] for k in SET_A]), "A_mean": st.mean([pm[k] for k in SET_A]),
         "B_median": st.median([pm[k] for k in SET_B]), "B_mean": st.mean([pm[k] for k in SET_B]),
         "A_exVGC_mean": st.mean([pm[k] for k in SET_A if k != "VGC"]), "VGC_only": pm["VGC"]}


def cell_parts(branch, rev, norm, roe, g_):
    rv = c.TTM[0] if rev == "TTM" else c.E2026[0]
    m_now = c.NPM_TTM if rev == "TTM" else c.npm(*c.E2026)
    m = m_now - c.REVERT[branch] * (m_now - c.NPM_MEAN[norm])
    add = c.CIP_TOTAL * I_CIP * (1 - c.TAX)
    return rv, m, add


def fn_var(branch, rev, norm, g, roe, recv, ronic_ke=False, m_ind=None, N=0, basis="cum"):
    rv, m, add = cell_parts(branch, rev, norm, roe, g)
    rr = r0
    mult = 1 / rr if ronic_ke else (1 - g / roe) / (rr - g)
    if m_ind is None:
        tot = (rv * m + add) * mult
    else:
        e_cell, e_ind = rv * m + add, rv * m_ind + add
        tot = e_ind * mult + sum((e_cell - e_ind) * (N - t + 1) / N / (1 + rr) ** t for t in range(1, N + 1))
    tot -= recv * RECV_CONC * (1 - c.TAX)
    return tot * B / c.SH_NOW if basis == "cum" else (tot + c.PROCEEDS) * B / c.SH_POST


def run(**kw):
    D = g.dist(g.build_grid(AXES, lambda **a: fn_var(**a, **kw)), PX, DISC)
    Dp = g.dist(g.build_grid(AXES, lambda **a: fn_var(**a, basis="post", **kw)), TERP, DISC)
    P = D["P_post"]
    return dict(center=D["center_post"], center_pre=D["center_pre"], p10=P["p10"], p50=P["p50"], p90=P["p90"],
                pct_below=D["pct_w_below_px"], label=g.label(PX, P["p10"], P["p90"]),
                center_sleeve40=D["center_pre"] * (1 - SLEEVE40),
                post_center=Dp["center_post"], post_p90=Dp["P_post"]["p90"], label_terp=g.label(TERP, Dp["P_post"]["p10"], Dp["P_post"]["p90"]))


res = {}
res["WIDE_r2"] = run()
res["RONIC_Ke_only"] = run(ronic_ke=True)
for k, m in M_IND.items():
    res[f"margin_only_{k}_N5"] = run(m_ind=m, N=5)
    for N, tier in ((0, "NONE_N0"), (2, "NONE_N2"), (5, "NARROW_N5")):
        res[f"{tier}_{k}"] = run(ronic_ke=True, m_ind=m, N=N)
# biên về TB chu kỳ CỦA CHÍNH MÃ (mọi nhánh = CYCLICAL) + RONIC=Ke — tham chiếu, không phải luật 3c
res["own_cycle_RONIC_Ke"] = g.dist(g.build_grid(dict(AXES, branch=[("CYCLICAL", "CYCLICAL", 1.0)]),
                                                lambda **a: fn_var(**a, ronic_ke=True)), PX, DISC)
oc = res["own_cycle_RONIC_Ke"]
res["own_cycle_RONIC_Ke"] = dict(center=oc["center_post"], p10=oc["P_post"]["p10"], p50=oc["P_post"]["p50"], p90=oc["P_post"]["p90"],
                                 pct_below=oc["pct_w_below_px"], label=g.label(PX, oc["P_post"]["p10"], oc["P_post"]["p90"]))
ctrl_ok = abs(res["WIDE_r2"]["center"] - R2["dist"]["center_post"]) < 0.5
out = dict(job="Taylor_20261107_123141", r=r0, price=PX, disc_ref=DISC, sleeve40=SLEEVE40, terp=TERP,
           control_center_r2=R2["dist"]["center_post"], control_ok=ctrl_ok,
           npm_scl={"ttm": c.NPM_TTM, **c.NPM_MEAN}, peer_npm_mean=pm, m_ind=M_IND,
           mult_note={"roe15_g4": (1 - .04 / .15) / (r0 - .04), "roe20_g4": (1 - .04 / .20) / (r0 - .04), "ronic_ke": 1 / r0},
           results=res)
json.dump(out, open(os.path.join(HERE, "scl_5f_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
L = [f"control WIDE center {res['WIDE_r2']['center']:.0f} vs r2 {R2['dist']['center_post']:.0f} ok={ctrl_ok}",
     "m_ind " + " ".join(f"{k} {v:.4f}" for k, v in M_IND.items()),
     "peer " + " ".join(f"{k} {v:.4f}" for k, v in pm.items()),
     f"SCL npm ttm {c.NPM_TTM:.4f} " + " ".join(f"{k} {v:.4f}" for k, v in c.NPM_MEAN.items())]
for k, v in res.items():
    L.append(f"{k:28s} center {v['center']:7.0f} p10 {v['p10']:7.0f} p50 {v['p50']:7.0f} p90 {v['p90']:7.0f} below {v['pct_below']:.3f} {v['label']}"
             + (f" | sleeve40 {v['center_sleeve40']:.0f} | post {v['post_center']:.0f} p90 {v['post_p90']:.0f} {v['label_terp']}" if 'post_center' in v else ""))
open(os.path.join(HERE, "scl_5f_out.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
