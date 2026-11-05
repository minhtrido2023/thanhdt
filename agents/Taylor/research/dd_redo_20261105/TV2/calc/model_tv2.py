"""TV2 — DD redo 05/11/2026 (job Taylor_20261105_014130).
Giá trị = LNST bền 2027–28 (kịch bản, ước lượng từ DD v3 01/11) × P/E NỘI TẠI (1 − g/ROE)/(r − g) + khoản một lần.
ĐỔI so với v3 (dd_TV2_20261101/calc/valuation.py): P/E gán tay 7–9x (neo pha đỉnh 2017–21 trung vị 7,45x)
→ P/E suy từ r = 13,5% neo lãi huy động (ddg2.r_info), ROE = LNST kịch bản / VCSH mẹ 30/09, g {3;4;5}% (ước lượng);
7,45x giữ làm đối chiếu. CK thanh khoản (ddg2.liquidity). Pháp lý (khởi tố cựu Chủ tịch + KTT) = WARNING, ngoài tâm.
Nguồn số: N, VCSH mẹ [BCTC HN Q3/2026 tr.8; DD 28/10 out.txt BVPS 19.708]; phơi nhiễm CMC [Q3 tr.25, 43];
LNST kịch bản = DD v3 §0 bảng 3 kịch bản (trung điểm dải; ước lượng); one-off CMC −80 tỷ sau thuế (ước lượng: ~100 tỷ trước thuế).
Chạy: $DNA_PYEXE -I model_tv2.py → model_tv2_out.json/.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2"))
import ddg2 as g

N = 67.526165                       # tr cp
EQ = 19708 * N / 1000               # VCSH mẹ 30/09/2026, tỷ
CMC_EXPO = 666.374 + 188.6          # phải thu CMC + đầu tư (tỷ)
SCEN = {
    "tich_cuc": dict(w=0.25, E=250.0, oneoff=0.0, note="lặp chu kỳ EPC 2019–21 (LNST 256–272 BQ); HĐ mới; CMC thu đủ"),
    "co_so":    dict(w=0.50, E=177.5, oneoff=0.0, note="4 HĐ EPC đúng tiến độ (Ô Môn IV, eREX ×2, Tân Thuận GĐ3); TC ròng 50–70; LK ~30"),
    "tieu_cuc": dict(w=0.25, E=110.0, oneoff=-80.0, note="vượt chi phí EPC, lãi float giảm, CMC trích lập ~100 tỷ trước thuế (cơ sở: phải thu CMC 666 không dự phòng, gần như chưa thu Q3)"),
}
G0 = 0.04
R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV2"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]


def pe(E, gg, r):
    roe = E / EQ
    return (1 - gg / roe) / (r - gg)


def val(E, oneoff, gg, r):
    return (E * pe(E, gg, r) + oneoff) / N * 1000


def expected(r, gg=G0):
    return sum(s["w"] * val(s["E"], s["oneoff"], gg, r) for s in SCEN.values())


sv = {k: val(s["E"], s["oneoff"], G0, r0) for k, s in SCEN.items()}
pes = {k: pe(s["E"], G0, r0) for k, s in SCEN.items()}
E_pre = expected(r0); E_post = E_pre * (1 - disc)
vals, wts = [], []
for s in SCEN.values():
    for m in (0.9, 1.0, 1.1):
        for gg in (0.03, 0.04, 0.05):
            vals.append(val(s["E"] * m, s["oneoff"], gg, r0)); wts.append(s["w"] / 9)
P_pre = g.wpct(vals, wts); P_post = {k: v * (1 - disc) for k, v in P_pre.items()}
sens_r = {k: dict(r=rr, post=expected(rr) * (1 - disc), pct=expected(rr) / E_pre - 1) for k, rr in g.r_grid(r0).items()}
peak_pe = {k: (s["E"] * 7.45 + s["oneoff"]) / N * 1000 for k, s in SCEN.items()}
peak_E = sum(SCEN[k]["w"] * v for k, v in peak_pe.items())
warn = {f"mat_{int(x*100)}pct_CMC_sau_thue": -x * CMC_EXPO * 0.8 / N * 1000 for x in (0.15, 0.30, 0.50)}
implied_E = PX * N / 1000 / pe(177.5, G0, r0)

OLD = dict(low=17100, center=20700, high=25300, dd_date="2026-11-01", basis="v3: kỳ vọng 25/50/25, P/E gán 7–9x; vùng = dải kịch bản cơ sở; chưa CK thanh khoản")
out = dict(ticker="TV2", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, grid_n=len(vals),
           eq_parent=EQ, scen={k: dict(w=s["w"], E=s["E"], oneoff=s["oneoff"], roe=s["E"] / EQ, pe=pes[k], value_pre=sv[k]) for k, s in SCEN.items()},
           center_pre_liq=E_pre, center_post_liq=E_post, P_pre=P_pre, P_post=P_post, sens_r=sens_r,
           xcheck_peak_pe745_pre=peak_E, implied_E_at_price_base_pe=implied_E, warn_cmc=warn,
           label=g.label(PX, P_post["p10"], P_post["p90"]),
           px_vs_center=PX / E_post - 1, px_vs_p10=PX / P_post["p10"] - 1, px_vs_p90=PX / P_post["p90"] - 1,
           zone_old=OLD, center_vs_old=E_post / OLD["center"] - 1)
json.dump(out, open(os.path.join(HERE, "model_tv2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
lines = [f"TV2 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} (neo {R['anchor']['rate']}% {R['anchor']['date']}; nay {R['current']['rate']}%) | VCSH mẹ {EQ:,.1f} tỷ",
         "Kịch bản (g 4%): " + " | ".join(f"{k} w{s['w']} E {s['E']} ROE {s['E']/EQ:.1%} P/E {pes[k]:.2f}x ⇒ {f(sv[k])}" for k, s in SCEN.items()),
         f"CK thanh khoản {disc:.2%} @5 tỷ (ADV120 trung vị {L['adv120_med_ty']:.2f} tỷ; 10%/20%: {L['sizes'][1]['days_p10']:.1f}/{L['sizes'][1]['days_p20']:.1f} phiên)",
         f"Tâm TRƯỚC {f(E_pre)} SAU {f(E_post)} | đối chiếu P/E pha đỉnh 7,45x: {f(peak_E)} (trước CK)",
         f"Lưới n={len(vals)} TRƯỚC " + " ".join(f"{k} {f(v)}" for k, v in P_pre.items()),
         f"Lưới SAU " + " ".join(f"{k} {f(v)}" for k, v in P_post.items()),
         f"Giá so tâm {PX/E_post-1:+.1%} | so P10 {PX/P_post['p10']-1:+.1%} | so P90 {PX/P_post['p90']-1:+.1%} ⇒ {out['label']}",
         f"LNST bền ngầm định ở giá (P/E cơ sở {pes['co_so']:.2f}x): {implied_E:,.0f} tỷ",
         "Độ nhạy r (SAU CK): " + " | ".join(f"{k} {f(v['post'])} ({v['pct']:+.1%})" for k, v in sens_r.items()),
         "WARNING CMC (đ/cp): " + " | ".join(f"{k} {f(v)}" for k, v in warn.items()),
         f"Cũ v3: tâm {f(OLD['center'])} vùng {f(OLD['low'])}–{f(OLD['high'])} ⇒ mới (sau CK)/cũ {E_post/OLD['center']-1:+.1%}"]
open(os.path.join(HERE, "model_tv2_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
