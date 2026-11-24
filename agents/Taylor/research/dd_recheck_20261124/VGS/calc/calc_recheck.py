"""VGS recheck 24/11: chạy lại model_r2.py (KHÔNG sửa) ở các mức r; output vào thư mục này.
Assert md5 model + assumptions; CONTROL: r=13,5% tái lập tâm 26.778 / sau CK 1 tỷ 26.526."""
import hashlib, json, sys, io, contextlib
from pathlib import Path
H = Path(__file__).parent
SRC = H.parents[2] / "dd_VGS_20261110" / "calc" / "model_r2.py"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(SRC) == "05e025279e3603474cb8427f36dbc43d", md5(SRC)
assert md5(H / "assumptions_r2.json") == "c13014360aa523a102e31b5699c44db9"
code = compile(open(SRC).read(), str(SRC), "exec")
def run(r):
    g = {"__file__": str(H / "model_r2.py"), "__name__": "m"}
    sys.argv = ["x", str(r)]
    with contextlib.redirect_stdout(io.StringIO()):
        exec(code, g)
    return g["res"]
base = run(0.135)
assert round(base["center"]) == 26778 and round(base["liq"]["1.0ty"]["center_post"]) == 26526, (base["center"], base["liq"]["1.0ty"]["center_post"])
out = {}
for r in (0.123, 0.125, 0.130, 0.134, 0.135, 0.140, 0.145):
    x = run(r); l = x["liq"]["1.0ty"]
    out[f"{r:.3f}"] = dict(center_pre=round(x["center"]), p10_pre=round(x["p10"]), p90_pre=round(x["p90"]),
        center_1ty=round(l["center_post"]), p10_1ty=round(l["p10_post"]), p90_1ty=round(l["p90_post"]),
        d_center_1ty=round(l["center_post"] - base["liq"]["1.0ty"]["center_post"]),
        d_pct=round((l["center_post"] / base["liq"]["1.0ty"]["center_post"] - 1) * 100, 2))
(H / "model_out_r2.json").unlink()
json.dump(out, open(H / "calc_recheck_out.json", "w"), indent=1)
print(json.dumps(out, indent=1))
