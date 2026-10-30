"""r10: áp sửa skeptic trên r9. (1) hàng vĩnh viễn: bảng 100/quý vs 100/năm; (2) cùng cơ sở thuế; (3) tách Q4 ex-dự phòng; (9) dải đối xứng 2 nền biên.
python3 r10_calc.py  (cần model.py cùng thư mục; không sửa model.py)"""
import os, pandas as pd, model as M
H = os.path.dirname(os.path.abspath(__file__)); o = []
def P(*a): o.append(" ".join(str(x) for x in a)); print(*a)
A7, B7 = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]; P("tái lập A7", A7, "B7", B7)
s = M.SCN["coso"]; revs = [s["p4_vol"] * s["p4_px"][i] * M.FX / 1e6 + s["tpa_vol"] * s["tpa_px"] * M.FX / 1e6 + s["other"] for i in (0, 1)]
cq3 = (2469.45 - 506.35) * 4; gmo = {k: list(v["gm"]) for k, v in M.SCN.items()}; SH = M.SH; ke = M.ke(); q4o = dict(M.Q4_NEW)
def run(cogs, cfg, q4ex=False):
    """cogs=None: nền r4. q4ex: cộng 100 tỷ tuyệt đối vào LN gộp Q4 mỗi kịch bản (Q4 ex-dự phòng)."""
    try:
        if cogs is not None:
            sh = [(1 - cogs / revs[i]) - gmo["coso"][i] for i in (0, 1)]
            for k in M.SCN: M.SCN[k]["gm"] = [gmo[k][i] + sh[i] for i in (0, 1)]
        if q4ex:
            for k, (rv, gm, ot) in q4o.items(): M.Q4_NEW[k] = (rv, gm + 100 / rv, ot)
        return M.per_scn(cfg)[0]
    finally:
        for k in M.SCN: M.SCN[k]["gm"] = gmo[k]
        M.Q4_NEW.update(q4o)
# --- (3) Q4 ex-dự phòng
rows = []
for nm, cogs in (("r4", None), ("R2", cq3 - 400)):
    for q4ex in (False, True):
        rows.append(dict(base=nm, q4_ex_provision=q4ex, A7=run(cogs, M.CFG_A7, q4ex), B7=run(cogs, M.CFG_B7, q4ex)))
q4t = pd.DataFrame(rows); P("\nQ4 ex-dự phòng (cộng 100 tỷ vào LN gộp Q4 mỗi kịch bản):\n", q4t.to_string(index=False))
d_q4 = {nm: int(q4t[(q4t.base == nm) & q4t.q4_ex_provision].A7.iloc[0] - q4t[(q4t.base == nm) & ~q4t.q4_ex_provision].A7.iloc[0]) for nm in ("r4", "R2")}
P("Δ A7 do tách Q4:", d_q4, "; mỗi bên đ/cp tính trực tiếp 100 tỷ =", round(100 * 1000 / SH), "(trước thuế)")
q4t.to_csv(f"{H}/out_r10_q4_split.csv", index=False)
base = {"r4": dict(A7=A7, B7=B7, A7x=int(q4t[(q4t.base == 'r4') & q4t.q4_ex_provision].A7.iloc[0]), B7x=int(q4t[(q4t.base == 'r4') & q4t.q4_ex_provision].B7.iloc[0])),
        "R2": dict(A7=int(q4t[(q4t.base == 'R2') & ~q4t.q4_ex_provision].A7.iloc[0]), B7=int(q4t[(q4t.base == 'R2') & ~q4t.q4_ex_provision].B7.iloc[0]),
                   A7x=int(q4t[(q4t.base == 'R2') & q4t.q4_ex_provision].A7.iloc[0]), B7x=int(q4t[(q4t.base == 'R2') & q4t.q4_ex_provision].B7.iloc[0]))}
# --- (1)(2) perpetual: 100/quý vs 100/năm; cùng cơ sở thuế
pr = []
for x in (25, 50, 100, 200):
    pr.append(dict(per_quarter=x, per_year=4 * x, ev_A7=run(cq3 - 400 + 4 * x, M.CFG_A7), d_vs_R2=run(cq3 - 400 + 4 * x, M.CFG_A7) - base["R2"]["A7"]))
pr = pd.DataFrame(pr); pr["d_per_cp_per_100_ty_per_year"] = (pr.d_vs_R2 / (pr.per_year / 100)).round(); P("\nVĩnh viễn qua model:\n", pr.to_string(index=False))
pr.to_csv(f"{H}/out_r10_perpetual.csv", index=False)
r1 = int(pr[pr.per_quarter == 100].d_vs_R2.iloc[0])
# vĩnh viễn thô (PV trước thuế, không tăng trưởng, thanh toán giữa quý, cùng timing bảng N)
def pv(x, n, tax=0.0): return sum(x / (1 + ke) ** (0.17 + (j - 0.5) / 4) for j in range(1, n + 1)) * (1 - tax) * 1000 / SH
pperp = {tax: pv(100, 4000, tax) for tax in (0.0, 0.2)}
P("PV vĩnh viễn thô 100/quý (ke %.3f): trước thuế %.0f ; sau lá chắn 20%% %.0f ; model R1 %d" % (ke, pperp[0.0], pperp[0.2], r1))
# --- bảng N: cùng 2 cơ sở thuế, Q4 tách đúng (nền R2 ex-Q4)
rows = []
for x in (50, 100, 200):
    for n in (0, 1, 2, 4, 8):
        for tax in (0.0, 0.2):
            ps = pv(x, n, tax); rows.append(dict(x_per_q=x, N=n, tax_shield=tax, ded_ps=round(ps), A7_R2_q4ex=round(base["R2"]["A7x"] - ps), A7_r4_q4ex=round(base["r4"]["A7x"] - ps),
                                                A7_R2_old=round(base["R2"]["A7"] - ps), A7_r4_old=round(base["r4"]["A7"] - ps)))
fN = pd.DataFrame(rows); fN.to_csv(f"{H}/out_r10_finite_N.csv", index=False)
for tax in (0.0, 0.2): P(f"\nBảng N, lá chắn thuế {tax} (nền R2 / r4, Q4 ex-dự phòng):\n", fN[fN.tax_shield == tax].pivot(index="N", columns="x_per_q", values=["ded_ps", "A7_R2_q4ex", "A7_r4_q4ex"]).to_string())
# --- (9) ngầm 281 tỷ/năm
cogs_r4 = revs[0] * (1 - gmo["coso"][0]); P("\nGiá vốn 2027 nền r4 =", round(cogs_r4), "; nền R2 =", round(cq3 - 400), "; chênh ngầm =", round(cogs_r4 - (cq3 - 400)), "tỷ/năm; biên r4/R2:", gmo["coso"], [round(1 - (cq3 - 400) / r, 4) for r in revs])
# --- dải cuối đối xứng 2 nền (Q4 ex), lá chắn 0% & 20%
rows = []
for nm in ("r4", "R2"):
    for lab, x, n in (("N=0 (Q4 ex-dự phòng, không trích thêm)", 100, 0), ("100 × 1 quý", 100, 1), ("100 × 4 quý", 100, 4), ("200 × 4 quý", 200, 4), ("100 × 8 quý", 100, 8), ("200 × 8 quý", 200, 8)):
        for tax in (0.0, 0.2):
            ps = pv(x, n, tax); rows.append(dict(base=nm, case=lab, tax_shield=tax, A7=round(base[nm]["A7x"] - ps), B7=round(base[nm]["B7x"] - ps)))
    rows.append(dict(base=nm, case="(r9, Q4 gồm ~100 ngầm) N=0", tax_shield=0.0, A7=base[nm]["A7"], B7=base[nm]["B7"]))
g = pd.DataFrame(rows); g.to_csv(f"{H}/out_r10_final_grid.csv", index=False); P("\nDải cuối đối xứng:\n", g.to_string(index=False))
# R1 vĩnh viễn giữ nguyên (đã gồm Q4 ngầm nhất quán)
P("R1 (model, thuế lõi trong model):", base["R2"]["A7"] + r1, "; R1 − R2 ex-Q4 =", base["R2"]["A7"] + r1 - base["R2"]["A7x"])
open(f"{H}/run_stdout_r10.txt", "w").write("\n".join(o))
