"""TV2 — bước 3c (5F tầng b + moat trong mô hình), 07/11/2026, job Taylor_20261107_131643.
KHÔNG sửa model_tv2_r2.py. Chép nguyên hằng số/trục của r2, kiểm control = tâm r2 (15.832).
r2 hiện hành: P/E nội tại (1 − g/ROE)/(r − g) với ROE = LNST kịch bản / VCSH ⇒ RONIC ngầm = ROE kịch bản VĨNH VIỄN
(nhánh ROE > Ke được thưởng, nhánh ROE < Ke bị phạt) + mức LN sau 2028 = E × persist vĩnh viễn (không neo ngành).
Chặt-3c (NARROW/NONE không bền): RONIC = Ke ĐỐI XỨNG (P/E = 1/r mọi nhánh) + LN terminal về ROE TB chu kỳ NGÀNH × VCSH.
Neo ngành: ROE_Trailing dòng Q4 (= ROE 4 quý) 2012–2025 của peer PECC nội địa, từ bq_moat_tv1234_20261107.csv.
Quy ước năm: giống r2 — dòng LN năm t chiết khấu (1+r)^t, t=1 = 2027; Gordon tại T chiết khấu (1+r)^T.
Chạy: $DNA_PYEXE -I moat_5f_tv2.py → moat_5f_tv2_out.json/.txt
"""
import csv, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g

N = 67.526165; EQ = 19708 * N / 1000; CMC_EXPO = 666.374 + 188.6; TAX = 0.20
R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV2"); PX = L["price"]; disc = L["ref_discount"]
SLEEVE = L["sleeve_discount"]
HOLD = 2
AXES = dict(
    scen=[("tich_cuc", 250.0, 0.25), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.25)],
    mult=[("x0.9", 0.9, 1 / 3), ("x1", 1.0, 1 / 3), ("x1.1", 1.1, 1 / 3)],
    gg=[("g3", 0.03, 1 / 3), ("g4", 0.04, 1 / 3), ("g5", 0.05, 1 / 3)],
    cmc=[("0%", 0.0, 0.45), ("15%", 0.15, 0.30), ("30%", 0.30, 0.15), ("50%", 0.50, 0.10)],
    persist=[("sap70%", 0.30, 0.25), ("ben", 1.0, 0.50), ("+30%", 1.30, 0.25)],
)

# --- neo ngành từ BQ
rows = list(csv.DictReader(open(os.path.join(HERE, "bq_moat_tv1234_20261107.csv"))))
def roe(tks, y0=2012, y1=2025):
    return [float(r["ROE_Trailing"]) for r in rows if r["ticker"] in tks and r["quarter"].endswith("Q4")
            and y0 <= int(r["quarter"][:4]) <= y1 and r["ROE_Trailing"] not in ("", None)]
ANCH = {}
for nm, tks in (("TV3_TV4", ("TV3", "TV4")), ("TV1_TV3_TV4", ("TV1", "TV3", "TV4")), ("TV2_own", ("TV2",))):
    x = roe(tks); ANCH[nm] = dict(n=len(x), median=st.median(x), mean=st.mean(x))


def pe_r2(E, gg, r):
    return max((1 - gg / (E / EQ)) / (r - gg), 0.0)


def fn_r2(scen, mult, gg, cmc, persist, r=None):   # = model_tv2_r2.fn (control)
    rr = r0 if r is None else r; E = scen * mult
    if persist == 1.0:
        v = E * pe_r2(E, gg, rr)
    else:
        E2 = E * persist
        v = sum(E / (1 + rr) ** (t + 1) for t in range(HOLD)) + E2 * pe_r2(E2, gg, rr) / (1 + rr) ** HOLD
    v -= cmc * CMC_EXPO * (1 - TAX)
    return max(v / N * 1000, 0.0)


def make_fn(anchor_roe=None, keep=0, fade=0, persist_on_anchor=False):
    """RONIC = Ke (P/E = 1/r; g không tạo giá trị). Năm 1–2: E. Rồi `keep` năm E×persist, `fade` năm tuyến tính về neo,
    terminal = neo/r. anchor_roe None ⇒ chỉ RONIC=Ke, terminal = E×persist (bản tách nguồn RONIC)."""
    def fn(scen, mult, gg, cmc, persist):
        rr = r0; E = scen * mult; E2 = E * persist
        A = E2 if anchor_roe is None else anchor_roe * EQ * (persist if persist_on_anchor else 1.0)
        path = [E] * HOLD + [E2] * keep
        for k in range(1, fade + 1):
            path.append(E2 + (A - E2) * k / (fade + 1))
        T = len(path)
        v = sum(x / (1 + rr) ** (t + 1) for t, x in enumerate(path)) + (A / rr) / (1 + rr) ** T
        v -= cmc * CMC_EXPO * (1 - TAX)
        return max(v / N * 1000, 0.0)
    return fn


def summ(fn):
    D = g.dist(g.build_grid(AXES, fn), PX, disc); P = D["P_post"]
    s = dict(center=D["center_post"], p10=P["p10"], p50=P["p50"], p90=P["p90"], below=D["pct_w_below_px"],
             label=g.label(PX, P["p10"], P["p90"]))
    for k, d in SLEEVE.items():
        f = (1 - d) / (1 - disc)
        s[f"sleeve_{k}"] = dict(center=D["center_post"] * f, p10=P["p10"] * f, p90=P["p90"] * f,
                                label=g.label(PX, P["p10"] * f, P["p90"] * f))
    return s


res = {"control_r2": summ(fn_r2), "ronic_only": summ(make_fn(None))}
for nm in ("TV3_TV4", "TV1_TV3_TV4"):
    for stat in ("median", "mean"):
        a = ANCH[nm][stat]
        res[f"NONE_{nm}_{stat}"] = summ(make_fn(a))                       # neo từ 2029
        res[f"NARROW_{nm}_{stat}"] = summ(make_fn(a, keep=2, fade=2))     # giữ E×persist 2029–30, fade 2031–32
a0 = ANCH["TV3_TV4"]["median"]
res["NARROW_TV3_TV4_median_persist_on_anchor"] = summ(make_fn(a0, keep=2, fade=2, persist_on_anchor=True))
assert abs(res["control_r2"]["center"] - 15832) < 1.0, res["control_r2"]["center"]

out = dict(ticker="TV2", price=PX, r=r0, disc_ref=disc, sleeve=SLEEVE, EQ=EQ, anchors=ANCH, res=res,
           roe_terminal_mean_r2=sum(p * q for _, p, q in AXES["persist"]) * sum(e * w for _, e, w in AXES["scen"]) / EQ)
json.dump(out, open(os.path.join(HERE, "moat_5f_tv2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
L_ = [f"TV2 3c | giá {PX:,.0f} | r {r0:.4f} | CK ref {disc:.2%} | VCSH {EQ:.1f} tỷ | ROE terminal kỳ vọng r2 (E×persist TB) {out['roe_terminal_mean_r2']:.2%}"]
for nm, a in ANCH.items():
    L_.append(f"neo ROE Q4 2012–25 {nm}: n {a['n']} trung vị {a['median']:.2%} TB {a['mean']:.2%}")
for k, s in res.items():
    L_.append(f"{k:44s} tâm {s['center']:7,.0f} P10 {s['p10']:7,.0f} P50 {s['p50']:7,.0f} P90 {s['p90']:7,.0f} dưới giá {s['below']:.1%} {s['label']} | sleeve40tr tâm {s['sleeve_40tr']['center']:,.0f} P90 {s['sleeve_40tr']['p90']:,.0f} {s['sleeve_40tr']['label']}")
open(os.path.join(HERE, "moat_5f_tv2_out.txt"), "w").write("\n".join(L_) + "\n")
print("\n".join(L_))
