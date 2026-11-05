"""TV2 — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020018) theo STANDARD_r2.md.
Hàm giá trị = vòng 1 (model_tv2.py): (LNST bền × P/E nội tại (1 − g/ROE)/(r − g) + khoản một lần)/N. Số chép nguyên từ model_tv2.py.
ĐỔI so vòng 1:
  - CMC: vòng 1 gói −80 tỷ VÀO kịch bản tiêu cực (chỉ lệch xuống, tương quan hoàn toàn với LN thấp). Vòng 2 = trục ĐỘC LẬP
    mất 0/15/30/50% phơi nhiễm 854,97 tỷ sau thuế (0% = sổ sách, chưa dự phòng ⇒ cận sổ sách, không có phía trên).
  - Thêm trục ĐỘ BỀN LN sau 2028 hai chiều (SKEPTIC_20261101 CAO-1: base rate LN sập ~70% khi hết HĐ EPC 2021→2022–25;
    chiều lên: HĐ mới nối tiếp, LN +30% [UL]).
  - Phân vị mức kết cục bằng _shared/wpct.py. Song song: trọng số 30/50/20 (SKEPTIC TB-6), lưới vòng 1.
Chạy: $DNA_PYEXE -I model_tv2_r2.py → model_tv2_r2_out.json/.txt + LOCK_r2_md5.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g

N = 67.526165
EQ = 19708 * N / 1000
CMC_EXPO = 666.374 + 188.6
TAX = 0.20
R = g.r_info(); r0 = R["r"]
L = g.liquidity("TV2"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]
HOLD = 2   # số năm LNST bền 2027–28 chắc chắn trước khi áp trục độ bền


def pe(E, gg, r, payout_if_low=False):
    if payout_if_low and E / EQ < r:
        return 1 / r   # chính sách: ROE < r ⇒ không tái đầu tư, trả hết (g=0) — chỉ dùng ở bản song song
    return max((1 - gg / (E / EQ)) / (r - gg), 0.0)   # ROE < g ⇒ công thức âm; sàn 0 (giữ bảo thủ, KHÔNG giả định chuyển sang trả hết cổ tức)


def fn(scen, mult, gg, cmc, persist, r=None, pol=False):
    rr = r0 if r is None else r
    E = scen * mult
    if persist == 1.0:
        v = E * pe(E, gg, rr, pol)
    else:
        E2 = E * persist
        ann = sum(E / (1 + rr) ** (t + 1) for t in range(HOLD))
        v = ann + E2 * pe(E2, gg, rr, pol) / (1 + rr) ** HOLD
    v -= cmc * CMC_EXPO * (1 - TAX)
    return max(v / N * 1000, 0.0)   # trách nhiệm hữu hạn


AXES = dict(
    scen=[("tich_cuc", 250.0, 0.25), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.25)],
    mult=[("x0.9", 0.9, 1 / 3), ("x1", 1.0, 1 / 3), ("x1.1", 1.1, 1 / 3)],
    gg=[("g3", 0.03, 1 / 3), ("g4", 0.04, 1 / 3), ("g5", 0.05, 1 / 3)],
    cmc=[("0%", 0.0, 0.45), ("15%", 0.15, 0.30), ("30%", 0.30, 0.15), ("50%", 0.50, 0.10)],
    persist=[("sap70%", 0.30, 0.25), ("ben", 1.0, 0.50), ("+30%", 1.30, 0.25)],
)
AXES_BASIS = dict(
    scen="LNST bền 2027–28: 250 (lặp 2019–21, LNST 256–272 BQ) / 177,5 (4 HĐ EPC đúng tiến độ) / 110 (vượt chi phí, lãi float giảm) — trọng số 25/50/25 [UL] (DD v3 01/11)",
    mult="LNST ×0,9/1/1,1 trong kịch bản, đều — hai chiều",
    gg="g 3/4/5% (ước lượng), đều — hai chiều",
    cmc="mất trên phơi nhiễm CMC 854,97 tỷ (phải thu 666,4 + đầu tư 188,6; BCTC Q3 tr.25, 43), sau thuế: 0% = sổ sách (chưa dự phòng) p0,45 · 15% p0,30 · 30% p0,15 · 50% p0,10 [UL]; "
        "cơ sở chiều xuống: phải thu 666 không dự phòng, thu tiền Q3 ≈ 0, Tân Thuận GĐ3 chưa COD. Không có phía trên sổ sách ⇒ trục một phía là CẬN SỔ SÁCH",
    persist="độ bền LN sau 2028: sập 70% p0,25 (base rate: LNST 214–272 tỷ 2017–21 → pha đáy 2022–25, SKEPTIC CAO-1) · bền p0,50 · +30% p0,25 (HĐ EPC mới nối tiếp) [UL] — hai chiều",
)
AXES_EXCLUDED = [
    dict(axis="vụ án (cựu Chủ tịch + KTT khởi tố Đ.353; 13 pháp nhân 'tư vấn xây dựng điện' chưa nêu tên)", reason="pháp lý ⇒ WARNING (ngoài tâm)"),
    dict(axis="tiền thô 1.951 tỷ (cộng tiền riêng)", reason="float khách ứng 2.418,6 là nợ thực chất; lãi float đã nằm trong LNST kịch bản ⇒ cộng tiền = đếm hai lần; chiều xuống (float ròng −55 tỷ) cũng không trừ riêng vì cùng lý do"),
    dict(axis="HĐ tổng thầu bên liên quan (NQ HĐQT 29/10 loại khỏi ngưỡng 35%)", reason="quản trị ⇒ WARNING; chưa thẩm định pháp lý"),
]

outs = g.build_grid(AXES, fn)
D = g.dist(outs, PX, disc)
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
central = fn(177.5, 1.0, 0.04, 0.0, 1.0)
p10_s = g.branch_share(outs, "scen", 0.10); p90_s = g.branch_share(outs, "scen", 0.90)
p90_p = g.branch_share(outs, "persist", 0.90)

AX_W = dict(AXES, scen=[("tich_cuc", 250.0, 0.20), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.30)])
D_w305020 = g.dist(g.build_grid(dict(AXES, scen=[("tich_cuc", 250.0, 0.30), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.20)]), fn), PX, disc)
D_w205030 = g.dist(g.build_grid(AX_W, fn), PX, disc)
D_payout = g.dist(g.build_grid(AXES, lambda **kw: fn(pol=True, **kw)), PX, disc)
D_nopersist = g.dist(g.build_grid(dict(AXES, persist=[("ben", 1.0, 1.0)]), fn), PX, disc)
# lưới vòng 1 (CMC −80 tỷ gói vào tiêu cực) + wpct
v1, w1 = [], []
for E, w, oo in ((250.0, 0.25, 0.0), (177.5, 0.50, 0.0), (110.0, 0.25, -80.0)):
    for m in (0.9, 1.0, 1.1):
        for gg in (0.03, 0.04, 0.05):
            v1.append((E * m * pe(E * m, gg, r0) + oo) / N * 1000); w1.append(w / 9)
D_r1 = g.dist([dict(v=a, w=b, labels={}) for a, b in zip(v1, w1)], PX, disc)

sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(g.build_grid(AXES, lambda **kw: fn(r=rr, **kw)), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)

# Gordon/ROE (điều 10), g 4%: LNST 2026E (217–242, trung điểm 229,5 — ước lượng DD v3) có / không lãi tiền gửi (TC ròng ~44% LNTT 9T ⇒ trừ 44% sau thuế)
gg = 0.04; NP26 = 229.5
gordon_with = EQ * (NP26 / EQ - gg) / (r0 - gg) / N * 1000
np_ex = NP26 * (1 - 0.44)
gordon_without = EQ * (np_ex / EQ - gg) / (r0 - gg) / N * 1000
base_adj = [dict(item="không có điều chỉnh khỏi sổ sách trong cơ sở", effect_dong_per_share=0.0,
                 basis="CMC theo sổ (0%) ở tham số trung tâm; mọi lệch nằm ở trục có xác suất", source="BCTC HN Q3/2026")]
out = dict(ticker="TV2", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, dist=D, label=lab,
           center_param=central, center_param_post=central * (1 - disc), p10_scen_branch=p10_s, p90_scen_branch=p90_s, p90_persist_branch=p90_p,
           parallel=dict(payout_when_roe_below_r=D_payout, w_30_50_20=D_w305020, w_20_50_30=D_w205030, no_persist_axis=D_nopersist, r1_grid_wpct=D_r1), sens_r=sens_r,
           gordon=dict(g=gg, np2026e=NP26, with_interest=gordon_with, without_interest=gordon_without, note="LNST 2026E ước lượng; 'không lãi TG' trừ 44% (tỷ trọng TC trong LNTT 9T)"),
           axes_included=[dict(axis=k_, values=[(a, b, p) for a, b, p in v], basis=AXES_BASIS[k_]) for k_, v in AXES.items()],
           axes_excluded=AXES_EXCLUDED, base_adjustments=base_adj)
json.dump(out, open(os.path.join(HERE, "model_tv2_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]
lines = [f"TV2 r2 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} | n kết cục {D['n']}",
         f"Tâm TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 SAU {f(P['p50'])} | tham số trung tâm (177,5|g4|CMC0|bền) SAU {f(central*(1-disc))}",
         "Kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"% trọng số dưới giá {D['pct_w_below_px']:.1%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%} | giá/P90 {PX/P['p90']-1:+.1%}",
         f"Kịch bản quanh P10 {p10_s} | quanh P90 {p90_s} | độ bền quanh P90 {p90_p}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; trong vùng √: {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()),
         f"SONG SONG trọng số 30/50/20: tâm {f(D_w305020['center_post'])} P10 {f(D_w305020['P_post']['p10'])} P90 {f(D_w305020['P_post']['p90'])} | 20/50/30: tâm {f(D_w205030['center_post'])} P90 {f(D_w205030['P_post']['p90'])}",
         f"SONG SONG chính sách trả hết khi ROE<r (g=0): tâm {f(D_payout['center_post'])} P10 {f(D_payout['P_post']['p10'])} P90 {f(D_payout['P_post']['p90'])} | dưới giá {D_payout['pct_w_below_px']:.1%}",
         f"SONG SONG không trục độ bền: tâm {f(D_nopersist['center_post'])} P10 {f(D_nopersist['P_post']['p10'])} P90 {f(D_nopersist['P_post']['p90'])} | dưới giá {D_nopersist['pct_w_below_px']:.1%}",
         f"SONG SONG lưới vòng 1 (n27) + wpct: tâm {f(D_r1['center_post'])} P10 {f(D_r1['P_post']['p10'])} P50 {f(D_r1['P_post']['p50'])} P90 {f(D_r1['P_post']['p90'])}",
         "Độ nhạy r (tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"Gordon g4% (trước CK, LNST 2026E 229,5 ước lượng): có lãi TG {f(gordon_with)} | không lãi TG {f(gordon_without)}"]
open(os.path.join(HERE, "model_tv2_r2_out.txt"), "w").write("\n".join(lines) + "\n")
g.write_lock(os.path.join(HERE, "LOCK_r2_md5.txt"), g.COMMON_FILES + [os.path.abspath(__file__)], "TV2 r2")
print("\n".join(lines))
