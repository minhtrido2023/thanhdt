"""r9: phân rã R2→R1 theo phương pháp + độ nhạy N quý × mức trích. Không đổi model.py. python3 r9_calc.py"""
import os, pandas as pd, model as M
H = os.path.dirname(os.path.abspath(__file__)); o = []
def P(*a): o.append(" ".join(str(x) for x in a)); print(*a)
A7, B7 = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]; P("tái lập A7", A7, "B7", B7); assert (A7, B7) == (32182, 37060)
s = M.SCN["coso"]; revs = [s["p4_vol"] * s["p4_px"][i] * M.FX / 1e6 + s["tpa_vol"] * s["tpa_px"] * M.FX / 1e6 + s["other"] for i in (0, 1)]
cq3 = (2469.45 - 506.35) * 4; gmo = {k: list(v["gm"]) for k, v in M.SCN.items()}
P("doanh thu lõi cơ sở 2027/28", [round(r) for r in revs], "; giá vốn Q3×4 =", round(cq3), "; DT Q3×4 =", round(2469.45 * 4))
def run(cogs, cfg, **kw):
    sh = [(1 - cogs / revs[i]) - gmo["coso"][i] for i in (0, 1)]
    try:
        for k in M.SCN: M.SCN[k]["gm"] = [gmo[k][i] + sh[i] for i in (0, 1)]
        return M.per_scn(dict(cfg, **kw))
    finally:
        for k in M.SCN: M.SCN[k]["gm"] = gmo[k]
W = dict(zip(("thuan", "coso", "nghich"), M.CFG_A7["w"]))
def by_method(r):
    sm = r["summ"].set_index("scn"); w = pd.Series(W)
    d = {m: float((sm[m] * w).sum()) for m in ("sotp", "dcf", "v_pe_dgc10y", "v_pe_peer_used", "v_pb")}
    d["ev"] = r["ev"]; return d
rows = []
for lab, cogs, kw in (("R1 (prov 200 trừ)", cq3, {}), ("R2 (prov 200 trừ)", cq3 - 400, {}),
                      ("R1 không trừ 200", cq3, dict(prov=0.0)), ("R2 không trừ 200", cq3 - 400, dict(prov=0.0)),
                      ("A7 nền r4 16,5/17,5", None, {})):
    r = M.per_scn(M.CFG_A7)[4] if cogs is None else run(cogs, M.CFG_A7, **kw)[4]
    rows.append(dict(case=lab, **{k: round(v) for k, v in by_method(r).items()}))
t = pd.DataFrame(rows).set_index("case"); P(t.to_string())
d = t.loc["R2 (prov 200 trừ)"] - t.loc["R1 (prov 200 trừ)"]
contrib = pd.DataFrame(dict(delta_R2_minus_R1=d.round(), weight_in_ev=[1/3, 1/3, 1/9, 1/9, 1/9, 1]))
contrib["contrib_to_ev"] = (contrib.delta_R2_minus_R1 * contrib.weight_in_ev).round()
P("\nPhân rã R2−R1 theo phương pháp (blend = TB(SOTP, DCF, TB 3 bội số)):\n", contrib.to_string())
P("Kiểm: tổng đóng góp", contrib.contrib_to_ev[:-1].sum(), "vs ΔEV", d.ev)
P("Khoản 200 (527 đ/cp) trong R1:", t.loc["R1 không trừ 200", "ev"] - t.loc["R1 (prov 200 trừ)", "ev"], "; trong R2:", t.loc["R2 không trừ 200", "ev"] - t.loc["R2 (prov 200 trừ)", "ev"])
t.to_csv(f"{H}/out_r9_methods_R1_R2.csv"); contrib.to_csv(f"{H}/out_r9_decomp_R2_R1.csv")
# --- mỗi 100 tỷ/quý LẶP MÃI qua model (tuyến tính?) : R2 base, thêm X/quý vào giá vốn
pr = []
for x in (0, 50, 100, 200):
    ev = run(cq3 - 400 + 4 * x, M.CFG_A7)[0]; pr.append(dict(x_per_q=x, ev_A7=ev, d_vs_R2=ev - t.loc["R2 (prov 200 trừ)", "ev"]))
pr = pd.DataFrame(pr); P("\nLặp MÃI (vốn hoá qua model, A7):\n", pr.to_string(index=False)); pr.to_csv(f"{H}/out_r9_perpetual.csv", index=False)
# --- N quý hữu hạn: trừ PV dòng tiền X/quý, quý j (j=1..N) trả cuối quý, t=(j-0.5)/4+0.17 năm từ 29/10 [UL thời điểm chi]; chiết khấu ke
ke = M.ke(); SH = M.SH; base = t.loc["R2 (prov 200 trừ)", "ev"]
fr = []
for x in (50, 100, 200):
    for n in (0, 1, 2, 4, 8):
        pv = sum(x / (1 + ke) ** (0.17 + (j - 0.5) / 4) for j in range(1, n + 1))
        for tax in (0.0, 0.20):
            fr.append(dict(x_per_q=x, N=n, tax_shield=tax, pv_ty=round(pv * (1 - tax), 1), ps=round(pv * (1 - tax) * 1000 / SH),
                           ev_A7=round(base - pv * (1 - tax) * 1000 / SH), vs_px=round((base - pv * (1 - tax) * 1000 / SH) / 32900 - 1, 3)))
fr = pd.DataFrame(fr); P(f"\nN quý hữu hạn (nền R2 {base}, ke {ke:.3f}):\n", fr[fr.tax_shield == 0].pivot(index="N", columns="x_per_q", values="ev_A7").to_string())
P(fr[fr.tax_shield == 0.2].pivot(index="N", columns="x_per_q", values="ev_A7").to_string()); fr.to_csv(f"{H}/out_r9_finite_N.csv", index=False)
# B7 tương ứng
b2 = run(cq3 - 400, M.CFG_B7)[0]; b1 = run(cq3, M.CFG_B7)[0]; P("B7 R2", b2, "B7 R1", b1)
# --- biên ngụ ý
P("\nBiên 2027/28 ngụ ý: R1", [round(1 - cq3 / r, 3) for r in revs], "R2", [round(1 - (cq3 - 400) / r, 3) for r in revs], "r4", gmo["coso"])
P("A7 nền r4 ⇔ giá vốn cố định ⇒ 'dự phòng ngầm' năm 2027 =", round(cq3 - revs[0] * (1 - gmo["coso"][0])), "tỷ/năm (so giá vốn Q3×4 gồm 400 dự phòng)")
P("R1/R2 ở DT Q3×4 (không hạ DT):", round(1 - cq3 / (2469.45 * 4), 3), round(1 - (cq3 - 400) / (2469.45 * 4), 3))
open(f"{H}/run_stdout_r9.txt", "w").write("\n".join(o))
# --- giá trị mỗi 1pp biên 2027-28 (mọi kịch bản) quanh nền r4 và R2
pp = []
for basis, cogs in (("r4 16,5/17,5", None), ("R2 19,5/20,7", cq3 - 400)):
    for dpp in (-0.02, -0.01, 0, 0.01, 0.02):
        if cogs is None:
            try:
                for k in M.SCN: M.SCN[k]["gm"] = [x + dpp for x in gmo[k]]
                a, b = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]
            finally:
                for k in M.SCN: M.SCN[k]["gm"] = gmo[k]
        else:
            sh = [(1 - cogs / revs[i]) - gmo["coso"][i] + dpp for i in (0, 1)]
            try:
                for k in M.SCN: M.SCN[k]["gm"] = [gmo[k][i] + sh[i] for i in (0, 1)]
                a, b = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]
            finally:
                for k in M.SCN: M.SCN[k]["gm"] = gmo[k]
        pp.append(dict(basis=basis, dpp=round(dpp * 100), A7=a, B7=b))
pp = pd.DataFrame(pp); P("\nBiên ±pp:\n", pp.to_string(index=False)); pp.to_csv(f"{H}/out_r9_margin_pp.csv", index=False)
P("đ/cp mỗi 1pp biên (A7, nền r4):", round((pp[(pp.basis.str.startswith('r4')) & (pp.dpp == 1)].A7.iloc[0] - pp[(pp.basis.str.startswith('r4')) & (pp.dpp == -1)].A7.iloc[0]) / 2))
# --- dải cuối: nền biên × dự phòng hữu hạn (PV không lá chắn thuế, bảo thủ)
bases = {"R1 15,2/16,5 (giá vốn Q3 gồm dp, phẳng)": (A7r1 := t.loc["R1 (prov 200 trừ)", "ev"], b1),
         "r4 16,5/17,5 (giả định r1, A7)": (A7, B7), "R2 19,5/20,7 (giá vốn Q3 bỏ dp, phẳng)": (base, b2)}
fin = []
for nm, (a, b) in bases.items():
    for x, n in (((0, 0),) if nm.startswith("R1") else ((0, 0), (100, 1), (100, 2), (100, 4), (200, 4), (100, 8), (200, 8))):   # R1 đã lặp mãi ⇒ cộng thêm hữu hạn là tính đôi
        ded = float(fr[(fr.x_per_q == (x or 50)) & (fr.N == n) & (fr.tax_shield == 0)].ps.iloc[0]) if n else 0
        fin.append(dict(margin_basis=nm, extra=f"{n} quý × {x}" if n else "không trích thêm", A7=round(a - ded), B7=round(b - ded), A7_vs_px=round((a - ded) / 32900 - 1, 3)))
fin = pd.DataFrame(fin); P("\nDải cuối (nền biên × trích thêm hữu hạn):\n", fin.to_string(index=False)); fin.to_csv(f"{H}/out_r9_final_grid.csv", index=False)
open(f"{H}/run_stdout_r9.txt", "w").write("\n".join(o))
