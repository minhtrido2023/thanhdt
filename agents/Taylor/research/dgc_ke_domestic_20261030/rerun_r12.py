"""Chạy lại r11_calc + r12_calc (r12) ở từng Ke trong bản sao riêng (rerun/ke_XX.X/), không chạm thư mục r12.
Thay duy nhất: CFG_R3 rf=0.074 → rf = Ke − 0,075 trong model.py; gỡ các assert neo số Ke 14,9.
Đối chứng: ở Ke 14,9 mọi out_r11_*/out_r12_*.csv phải trùng byte với bản trong r12.
Chạy: /home/trido/thanhdt/wc_venv/bin/python rerun_r12.py"""
import os, shutil, subprocess, filecmp, glob
HERE = os.path.dirname(os.path.abspath(__file__)); R12 = os.path.realpath(os.path.join(HERE, "..", "dgc_valuation_20261029_r12"))
PY = "/home/trido/thanhdt/wc_venv/bin/python"
STRIP = ['assert (A7, B7) == (32182, 37060); ', 'assert wavg["net_ps"] == -447, wavg',
         'assert list(a2.r11_tax20) == [-3245, 2524, 6781], list(a2.r11_tax20)']
for ke in (0.125, 0.130, 0.135, 0.149):
    d = os.path.join(HERE, "rerun", f"ke_{ke*100:.1f}"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for f in ("model.py", "r10_calc.py", "r11_calc.py", "r12_calc.py"):
        s = open(os.path.join(R12, f), encoding="utf-8").read()
        if f == "model.py":
            assert s.count("rf=0.074,") == 1; s = s.replace("rf=0.074,", f"rf={ke - 0.075:.6f},")
        if f == "r12_calc.py":   # hằng −6065 (Δ lặp vĩnh viễn ở Ke 14,9) → đọc từ out_r10_perpetual.csv của chính lần chạy
            assert s.count("(\"Dự phòng 100 tỷ/quý lặp vĩnh viễn (độ nhạy phụ)\", A7 - 6065, A7") == 1
            s = s.replace("A7 - 6065, A7", "A7 + int(perp[perp.per_quarter == 100].d_vs_R2.iloc[0]), A7")
        for a in STRIP:
            s = s.replace(a, "pass" if a.startswith("assert wavg") or a.startswith("assert list") else "")
        open(os.path.join(d, f), "w", encoding="utf-8").write(s)
    for sub in ("data", "src_r9", "source_pages", "source_pages_h1"):
        if os.path.exists(os.path.join(R12, sub)): os.symlink(os.path.join(R12, sub), os.path.join(d, sub))
    for f in glob.glob(os.path.join(R12, "*.csv")):   # r11/r12 có thể đọc out_* của vòng trước
        if not os.path.basename(f).startswith(("out_r10_", "out_r11_", "out_r12_")): shutil.copy(f, d)
    r0 = subprocess.run([PY, "r10_calc.py"], cwd=d, capture_output=True, text=True); assert r0.returncode == 0, r0.stderr[-500:]
    r = subprocess.run([PY, "r12_calc.py"], cwd=d, capture_output=True, text=True)
    open(os.path.join(d, "stdout.txt"), "w").write(r.stdout + r.stderr); print(ke, "rc", r.returncode, r.stderr[-300:])
    if abs(ke - 0.149) < 1e-9:
        outs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "out_r1[012]_*.csv")))
        bad = [o for o in outs if not filecmp.cmp(os.path.join(d, o), os.path.join(R12, o), shallow=False)]
        print("đối chứng Ke 14,9:", len(outs), "file, lệch:", bad)
