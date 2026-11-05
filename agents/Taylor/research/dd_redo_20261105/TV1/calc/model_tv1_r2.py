"""TV1 — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020018) theo STANDARD_r2.md.
Lõi = tv1_v2_core.py (INTRINSIC_v2 02/11, chép nguyên văn ở vòng 1; tái lập byte). r = 13,5% neo lãi huy động (ddg2.r_info).
ĐỔI so vòng 1:
  - Thêm trục THỜI ĐIỂM giá PPA SB5 hai chiều (điều 2): lùi hạ bậc 1/2 năm (lên; vòng 1 chỉ nêu ở §9) và truy thu bậc giá
    2022–26 áp hồi tố (xuống; vòng 1 để ở WARNING). Truy thu là tranh chấp HỢP ĐỒNG với EVN, không phải vụ án ⇒ vào lưới với xác suất [UL];
    bản không có trục báo song song.
  - Thêm trục vốn lưu động tư vấn 45/49/53% ΔDT (SKEPTIC_BLIND N2: đo 45–53%) hai chiều.
  - Phân vị mức kết cục bằng _shared/wpct.py.
Chạy: $DNA_PYEXE -I model_tv1_r2.py → model_tv1_r2_out.json/.txt + LOCK_r2_md5.txt
"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import tv1_v2_core as c

R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV1"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]
P_NOW = 949.0   # giá ròng hiện hành (tv1_v2_core PRICE P1)


def hydro(pk, q, timing, r):
    p = c.PRICE[pk]
    base = c.hydro_fcfe(p, q)
    if timing.startswith("delay"):
        n = int(timing[-1])
        cfs = c.hydro_fcfe(P_NOW, q)[:n] + base[n:]
    else:
        cfs = base
    v = c.pv_mid(cfs, r)
    if timing == "retro":
        v -= c.truy * (1 - c.TAX) / (1 + r)
    return v


def fn(ppa, consult, q, timing, wc, ban=None, r=None):
    rr = r0 if r is None else r
    shock = None if ban is None else ban
    v = hydro(ppa, q, timing, rr) + c.consult(consult, ke=rr, wc=wc, shock=shock)[0] + c.BS
    return max(c.ps(v), 0.0)   # trách nhiệm hữu hạn: vốn chủ không âm (chỉ chạm ở kết cục truy thu + 340 + biên 5%)


AXES = dict(
    ppa=[(k, k, c.PROB[k]) for k in c.PRICE],
    consult=[(k, k, c.P_CON[k]) for k in c.SCN],
    q=[(f"Q{x}", x, 1 / 3) for x in (175.0, c.Q_P50, 200.0)],
    timing=[("retro", "retro", 0.10), ("2027", "base", 0.70), ("delay1", "delay1", 0.15), ("delay2", "delay2", 0.05)],
    wc=[("45%", 0.45, 1 / 3), ("49%", 0.49, 1 / 3), ("53%", 0.53, 1 / 3)],
)
AXES_BASIS = dict(
    ppa="giá ròng SB5 2027+ 949/600/520/440/340, xác suất 0,05/0,25/0,30/0,20/0,20 [UL] (áp cơ học theo SKEPTIC_BLIND B1; 340 = bậc 2018 có văn bản)",
    consult="biên tư vấn 5/8/11/14%, xác suất 0,20/0,30/0,40/0,10 [UL] (SKEPTIC_BLIND B3 thêm kịch bản quay về 5%)",
    q="sản lượng 175/187,5/200 GWh, đều — đối xứng quanh P50 dài hạn 181–187",
    timing="thời điểm áp bậc giá thấp: truy thu hồi tố 2022–26 p0,10 [UL] (≈−17.400 đ/cp; chưa có văn bản đòi) · đúng 2027 p0,70 (lãnh đạo nêu 'từ 2027', KBSV — chưa kiểm bản gốc) · "
           "lùi 1 năm p0,15 · lùi 2 năm p0,05 [UL] (phụ lục 05 chưa thấy ký) — hai chiều",
    wc="vốn lưu động tư vấn 45/49/53% ΔDT (đo 45–53%), đều — hai chiều",
)
AXES_EXCLUDED = [
    dict(axis="cấm thầu EVN / khởi tố pháp nhân (vụ án 500kV mạch 3)", reason="vụ án ⇒ WARNING (luật user 27/09: vụ án ngoài tâm); báo song song bản CÓ trục: cấm 3 năm DT tư vấn −50% p0,35 (P(tiêu cực) M5 trong REPORT 02/11, SKEPTIC2 B1)"),
    dict(axis="buộc nộp tiền 20/50/100 tỷ", reason="vụ án ⇒ WARNING; số ở §6"),
    dict(axis="điện mặt trời nổi 46 MWp", reason="chưa đầu tư (vướng thủ tục) ⇒ NPV=0 theo luật 03/11, không có số giá/sản lượng cho cả hai chiều"),
    dict(axis="tỷ lệ KTPL", reason="đo được trên chính TV1 (30,1/150,2 = 20%) — tham số, không phải bất định lớn"),
]

outs = g.build_grid(AXES, fn)
D = g.dist(outs, PX, disc)
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
central = fn("P3_520", "C_giua", c.Q_P50, "base", 0.49)
p10_ppa = g.branch_share(outs, "ppa", 0.10); p90_ppa = g.branch_share(outs, "ppa", 0.90)
p10_tim = g.branch_share(outs, "timing", 0.10)

AX_NOTIM = dict(AXES, timing=[("2027", "base", 1.0)])
D_notim = g.dist(g.build_grid(AX_NOTIM, fn), PX, disc)
AX_R1 = dict(AXES, timing=[("2027", "base", 1.0)], wc=[("49%", 0.49, 1.0)])
D_r1 = g.dist(g.build_grid(AX_R1, fn), PX, disc)
AX_BAN = dict(AXES, ban=[("khong", None, 0.65), ("cam3y_-50%", [0.5] * 3, 0.35)])
D_ban = g.dist(g.build_grid(AX_BAN, fn), PX, disc)

sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(g.build_grid(AXES, lambda **kw: fn(r=rr, **kw)), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)

# Gordon/ROE (điều 10): VCSH Q3 574,7 tỷ (SKEPTIC_20261102); LNST 2025 150,2 sau KTPL 20% (ước lượng thay TTM — 9T25 không có trong core)
EQ = 574.7; NP = 150.2 * (1 - c.KTPL); INT_Y = 198.6 * 0.05 * (1 - c.TAX)   # lãi tiền gửi ≈ 5% × tiền+HTM 198,6 (ước lượng)
gg = 0.03
gordon_with = EQ * (NP / EQ - gg) / (r0 - gg) / c.SH * 1e9
cash_net = 198.6 - 129.9
gordon_without = ((EQ - cash_net) * ((NP - INT_Y) / (EQ - cash_net) - gg) / (r0 - gg) + cash_net) / c.SH * 1e9
base_adj = [
    dict(item="tiền ròng điều chỉnh (−cổ tức phải trả −lãi vay cá nhân phải trả −quỹ KTPL −KTPL sẽ trích +LNST Q4 sau KTPL)", effect_dong_per_share=c.ps(c.BS),
         basis="nợ phải trả trên sổ + KTPL 20% đo được; LNST Q4 50 tỷ là ước lượng [UL]", source="BCTC HN Q3/2026 BCĐ (mã 323 = 40,708 tỷ); tv1_v2_core §C"),
    dict(item="quỹ KTPL 20% trên dòng tiền thuỷ điện + tư vấn", effect_dong_per_share=None, basis="đo 30,1/150,2 LNST 2025", source="BCTC 2025 / H1 tr.30"),
]
out = dict(ticker="TV1", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, dist=D, label=lab,
           center_param=central, center_param_post=central * (1 - disc), p10_ppa_branch=p10_ppa, p90_ppa_branch=p90_ppa, p10_timing_branch=p10_tim,
           parallel=dict(no_timing_axis=D_notim, r1_axes_only=D_r1, with_ban_axis=D_ban), sens_r=sens_r,
           gordon=dict(g=gg, with_interest=gordon_with, without_interest=gordon_without, note="LNST 2025 sau KTPL; lãi TG 5% × 198,6 (ước lượng); bỏ qua hạ bậc PPA ⇒ chỉ đối chiếu"),
           truy_thu_dcp=c.ps(-c.truy * (1 - c.TAX) / (1 + r0)),
           axes_included=[dict(axis=k_, values=[(a, b, p) for a, b, p in v], basis=AXES_BASIS[k_]) for k_, v in AXES.items()],
           axes_excluded=AXES_EXCLUDED, base_adjustments=base_adj)
json.dump(out, open(os.path.join(HERE, "model_tv1_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]
n_zero = sum(o["w"] for o in outs if o["v"] == 0.0)
out["w_floor_zero"] = n_zero
json.dump(out, open(os.path.join(HERE, "model_tv1_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
lines = [f"TV1 r2 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} | n kết cục {D['n']}",
         f"Tâm TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 SAU {f(P['p50'])} | tham số trung tâm (520|giữa|187,5|2027|49%) SAU {f(central*(1-disc))}",
         "Kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"% trọng số dưới giá {D['pct_w_below_px']:.1%} | trọng số chạm sàn 0 {n_zero:.2%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%}",
         f"PPA quanh P10 {p10_ppa} | quanh P90 {p90_ppa} | timing quanh P10 {p10_tim}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; trong vùng √: {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()),
         f"SONG SONG không trục thời điểm: tâm {f(D_notim['center_post'])} P10 {f(D_notim['P_post']['p10'])} P90 {f(D_notim['P_post']['p90'])} | dưới giá {D_notim['pct_w_below_px']:.1%}",
         f"SONG SONG trục vòng 1 (n60) + wpct: tâm {f(D_r1['center_post'])} P10 {f(D_r1['P_post']['p10'])} P50 {f(D_r1['P_post']['p50'])} P90 {f(D_r1['P_post']['p90'])}",
         f"SONG SONG CÓ cấm thầu (p0,35): tâm {f(D_ban['center_post'])} P10 {f(D_ban['P_post']['p10'])} P90 {f(D_ban['P_post']['p90'])} | dưới giá {D_ban['pct_w_below_px']:.1%}",
         "Độ nhạy r (tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"Gordon g3% (trước CK, LNST 2025 sau KTPL — chưa trừ hạ bậc PPA): có lãi TG {f(gordon_with)} | không lãi TG {f(gordon_without)} | truy thu hồi tố {f(out['truy_thu_dcp'])} đ/cp"]
open(os.path.join(HERE, "model_tv1_r2_out.txt"), "w").write("\n".join(lines) + "\n")
g.write_lock(os.path.join(HERE, "LOCK_r2_md5.txt"), g.COMMON_FILES + [os.path.abspath(__file__), os.path.join(HERE, "tv1_v2_core.py"), os.path.join(HERE, "v2data", "bq_tv1_quarterly_2022_2025.csv")], "TV1 r2")
print("\n".join(lines))
