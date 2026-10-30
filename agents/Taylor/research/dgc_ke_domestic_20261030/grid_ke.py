"""Chạy lại r10_calc.py (r12) ở từng Ke: lưới dự phòng + lặp vĩnh viễn R1. Không sửa file r12; output ghi vào thư mục này.
Cách làm: đặt rf = Ke − 0,075 vào M.CFG/CFG_A7/CFG_B7 rồi exec mã r10_calc (bỏ assert tái lập và đổi thư mục ghi).
Chạy: /home/trido/thanhdt/wc_venv/bin/python grid_ke.py"""
import os, sys, io, contextlib, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R12 = os.path.join(HERE, "..", "dgc_valuation_20261029_r12")
sys.path.insert(0, R12)
with contextlib.redirect_stdout(io.StringIO()):
    import model as M
src = open(os.path.join(R12, "r10_calc.py"), encoding="utf-8").read()
src = src.replace("assert (A7, B7) == (32182, 37060); ", "").replace("import os, pandas as pd, model as M", "import os, pandas as pd")
src = src.replace('H = os.path.dirname(os.path.abspath(__file__))', 'H = OUTDIR')
assert "assert (A7, B7)" not in src and "H = OUTDIR" in src
rows = []
for ke in (0.105, 0.125, 0.130, 0.135, 0.140, 0.149, 0.158):
    rf = round(ke - 0.075, 6); od = os.path.join(HERE, f"r10_at_ke{ke*100:.1f}"); os.makedirs(od, exist_ok=True)
    keep = {n: getattr(M, n)["rf"] for n in ("CFG", "CFG_A7", "CFG_B7")}
    for n in keep: getattr(M, n)["rf"] = rf
    g = {"M": M, "OUTDIR": od, "__file__": os.path.join(od, "r10_calc.py")}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src, "r10_calc.py", "exec"), g)
    finally:
        for n, v in keep.items(): getattr(M, n)["rf"] = v
    fg = g["g"]; cell = lambda b, c, t, col="A7": int(fg[(fg.base == b) & (fg.case == c) & (fg.tax_shield == t)][col].iloc[0])
    A7 = g["A7"]; R1 = g["base"]["R2"]["A7"] + g["r1"]
    rows.append(dict(ke=round(ke * 100, 1), A7=A7, B7=g["B7"], R2_A7_N0=cell("R2", "N=0 (Q4 ex-dự phòng, không trích thêm)", 0.0),
                     r4_A7_N0=cell("r4", "N=0 (Q4 ex-dự phòng, không trích thêm)", 0.0), R1_model=R1, d_perp_model=g["r1"],
                     perp_raw_pre=round(g["pperp"][0.0]), perp_raw_post=round(g["pperp"][0.2]),
                     low_r4_perp_model=A7 + g["r1"], low_r4x_perp_raw_post=round(g["base"]["r4"]["A7x"] - g["pperp"][0.2]),
                     low_r4x_perp_raw_pre=round(g["base"]["r4"]["A7x"] - g["pperp"][0.0]),
                     r4_200x8_pre=cell("r4", "200 × 8 quý", 0.0)))
df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "out_grid_ke.csv"), index=False)
pd.set_option("display.width", 250); print(df.to_string(index=False))
c = df[df.ke == 14.9].iloc[0]
print("đối chứng Ke 14,9: A7", c.A7, "B7", c.B7, "R1", c.R1_model, "R2N0", c.R2_A7_N0, "low", c.low_r4_perp_model)
assert (c.A7, c.B7, c.R1_model, c.R2_A7_N0) == (32182, 37060, 30598, 36880)
