"""TV1 — DD redo 05/11/2026 (job Taylor_20261105_014130).
Lõi = INTRINSIC_v2 02/11 (dd_TV1_blind_20261102/valuation_blind_v2.py, định giá mù giá, vụ án/truy thu ngoài tâm),
chép nguyên văn sang tv1_v2_core.py; tái lập: tv1_v2_core_out.txt md5 785bcd8c… = bản gốc.
ĐỔI: Ke 12,85% (dải khung 30/10) → r = 13,5% neo lãi huy động 12T hiệu dụng (luật 03/11, ddg2.r_info) cho CẢ thuỷ điện
(FCFE tới 08/2059) và tư vấn; CK thanh khoản (ddg2.liquidity, 5 tỷ); số chuẩn hoá liên mã (tâm kỳ vọng; P10/P50/P90 lưới).
Lưới = 5 kịch bản giá PPA SB5 (xác suất v2) × 4 kịch bản tư vấn (xác suất v2) × sản lượng {175; 187,5; 200} GWh
(đối xứng ±12,5 quanh P50, trọng số đều) ⇒ n=60.
Chạy: $DNA_PYEXE -I model_tv1.py → model_tv1_out.json/.txt
"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2"))
import ddg2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import tv1_v2_core as c

R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV1"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]
QG = (175.0, c.Q_P50, 200.0)


def centre(ke, q=c.Q_P50):
    return c.ps(sum(c.sotp(pk, ck, q=q, ke=ke) * c.PROB[pk] * c.P_CON[ck] for pk in c.PRICE for ck in c.SCN))


def parts(ke):
    hyd = sum(c.pv_mid(c.hydro_fcfe(c.PRICE[pk], c.Q_P50), ke) * c.PROB[pk] for pk in c.PRICE)
    con = sum(c.consult(ck, ke=ke)[0] * c.P_CON[ck] for ck in c.SCN)
    return dict(hydro=c.ps(hyd), consult=c.ps(con), netcash=c.ps(c.BS))


E_pre = centre(r0); E_post = E_pre * (1 - disc)
vals, wts, cells = [], [], {}
for pk in c.PRICE:
    for ck in c.SCN:
        for q in QG:
            v = c.ps(c.sotp(pk, ck, q=q, ke=r0))
            vals.append(v); wts.append(c.PROB[pk] * c.P_CON[ck] / len(QG))
            if q == c.Q_P50:
                cells[f"{pk}|{ck}"] = v
P_pre = g.wpct(vals, wts); P_post = {k: v * (1 - disc) for k, v in P_pre.items()}
E_grid = sum(v * w for v, w in zip(vals, wts)) / sum(wts)

sens_r = {k: dict(r=rr, post=centre(rr) * (1 - disc), pct=centre(rr) / E_pre - 1) for k, rr in g.r_grid(r0).items()}
old_ke = centre(c.KE_C)
# WARNING (ngoài tâm) — tính lại ở r0
base_c = c.consult("C_giua", ke=r0)[0]
warn = {}
for lab, shock in [("cam_thau_3nam_-50%", [0.5] * 3), ("cam_thau_5nam_-50%", [0.5] * 5), ("cam_thau_3nam_-70%", [0.3] * 3)]:
    warn[lab] = c.ps(c.consult("C_giua", ke=r0, shock=shock)[0] - base_c)
for amt in (20, 50, 100):
    warn[f"nop_{amt}ty"] = c.ps(-amt / (1 + r0))
warn["truy_thu_bac_gia_2022_26"] = c.ps(-c.truy * (1 - c.TAX) / (1 + r0))

OLD = dict(low=11400, center=18100, high=24200, dd_date="2026-11-02", basis="rev5 blind: tâm kỳ vọng Ke 12,85%, vùng = P20–P80, chưa CK thanh khoản")
out = dict(ticker="TV1", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, grid_n=len(vals),
           prob_ppa=c.PROB, price_ppa=c.PRICE, prob_consult=c.P_CON, q_grid=QG,
           center_pre_liq=E_pre, center_post_liq=E_post, center_grid_pre=E_grid, parts_pre=parts(r0),
           P_pre=P_pre, P_post=P_post, cells_q50_pre=cells, sens_r=sens_r,
           centre_at_old_ke_pre=old_ke, old_ke=c.KE_C, warn_post_ke=warn,
           label=g.label(PX, P_post["p10"], P_post["p90"]),
           px_vs_center=PX / E_post - 1, px_vs_p10=PX / P_post["p10"] - 1, px_vs_p90=PX / P_post["p90"] - 1,
           zone_old=OLD, center_vs_old=E_post / OLD["center"] - 1)
json.dump(out, open(os.path.join(HERE, "model_tv1_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
pp = parts(r0)
lines = [f"TV1 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} (neo {R['anchor']['rate']}% {R['anchor']['date']}; nay {R['current']['rate']}%) | Ke cũ {c.KE_C:.4f} ⇒ tâm cũ tái lập {f(old_ke)}",
         f"Cấu phần ở r (trước CK): thuỷ điện {f(pp['hydro'])} + tư vấn {f(pp['consult'])} + tiền ròng {f(pp['netcash'])}",
         f"CK thanh khoản {disc:.2%} @5 tỷ (ADV120 trung vị {L['adv120_med_ty']:.2f} tỷ; 10%/20%: {L['sizes'][1]['days_p10']:.0f}/{L['sizes'][1]['days_p20']:.0f} phiên; 1 tỷ {L['sizes'][0]['discount']:.2%} ({L['sizes'][0]['days_p10']:.0f}/{L['sizes'][0]['days_p20']:.0f} phiên))",
         f"Tâm TRƯỚC {f(E_pre)} (kỳ vọng lưới {f(E_grid)}) SAU {f(E_post)}",
         f"Lưới n={len(vals)} TRƯỚC " + " ".join(f"{k} {f(v)}" for k, v in P_pre.items()),
         f"Lưới SAU " + " ".join(f"{k} {f(v)}" for k, v in P_post.items()),
         f"Giá so tâm {PX/E_post-1:+.1%} | so P10 {PX/P_post['p10']-1:+.1%} | so P90 {PX/P_post['p90']-1:+.1%} ⇒ {out['label']}",
         "Ô lưới Q187,5 (trước CK): " + " ".join(f"{k} {f(v)}" for k, v in cells.items()),
         "Độ nhạy r (SAU CK): " + " | ".join(f"{k} {f(v['post'])} ({v['pct']:+.1%})" for k, v in sens_r.items()),
         "WARNING ngoài tâm (đ/cp): " + " | ".join(f"{k} {f(v)}" for k, v in warn.items()),
         f"Cũ rev5: tâm {f(OLD['center'])} P20–P80 {f(OLD['low'])}–{f(OLD['high'])} ⇒ mới (sau CK)/cũ {E_post/OLD['center']-1:+.1%}"]
open(os.path.join(HERE, "model_tv1_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
