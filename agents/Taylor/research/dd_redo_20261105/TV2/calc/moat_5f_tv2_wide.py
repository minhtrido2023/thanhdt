"""TV2 3c — bản WIDE (chỉ để đo độ nhạy, KHÔNG có cơ sở): terminal = ROE TB chu kỳ RIÊNG TV2 (trung vị Q4 2012–25)
× VCSH, RONIC = ROE đó (P/E = (1−g/ROE)/(r−g), g theo lưới), giữ E×persist 2029–30, fade 2031–32. Import moat_5f_tv2 (tất định)."""
import json, os, sys, contextlib, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import moat_5f_tv2 as m
A = m.ANCH["TV2_own"]["median"]
def fn(scen, mult, gg, cmc, persist):
    rr = m.r0; E = scen * mult; E2 = E * persist; At = A * m.EQ
    path = [E] * m.HOLD + [E2] * 2 + [E2 + (At - E2) * k / 3 for k in (1, 2)]
    T = len(path); pe = max((1 - gg / A) / (rr - gg), 0.0)
    v = sum(x / (1 + rr) ** (t + 1) for t, x in enumerate(path)) + At * pe / (1 + rr) ** T
    return max((v - cmc * m.CMC_EXPO * (1 - m.TAX)) / m.N * 1000, 0.0)
s = m.summ(fn)
json.dump(dict(anchor_roe=A, res=s), open(os.path.join(m.HERE, "moat_5f_tv2_wide_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
print(f"WIDE_TV2own_{A:.4f} tâm {s['center']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} dưới giá {s['below']:.1%} {s['label']} | sleeve10tr {s['sleeve_10tr']['label']} 40tr {s['sleeve_40tr']['label']}")
