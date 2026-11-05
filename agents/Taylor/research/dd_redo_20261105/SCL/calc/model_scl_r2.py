"""SCL — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020018) theo STANDARD_r2.md.
Lõi = scl_r3_core.py (r3 03/11, chép nguyên văn ở vòng 1; tái lập byte). Vòng 2 chỉ đổi LỚP LƯỚI/PHÂN VỊ:
  - Kết cục = 3 nhánh chế độ ngành × DT × biên chuẩn hoá × g × ROE (như r3) × THÊM trục phải thu tập trung (một phía = cận sổ sách).
  - Phân vị mức kết cục bằng _shared/wpct.py.
  - Song song (điều 2): (a) CÓ trục IRR Phả Lại hai chiều 10/13,5/17%; (b) nhánh đối xứng hoá (thêm TROUGH gương của STRUCTURAL);
    (c) khung 'toàn bộ nợ theo mệnh giá' (cận dưới r3).
Giá 04/11 là CUM-quyền (ĐKCC 10/11) ⇒ so với giá trị/cp TRƯỚC quyền (38,84tr cp); TERP so giá trị SAU quyền (44,84tr cp).
Chạy: $DNA_PYEXE -I model_scl_r2.py → model_scl_r2_out.json/.txt + LOCK_r2_md5.txt
"""
import contextlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g
with contextlib.redirect_stdout(io.StringIO()):
    import scl_r3_core as c

R = g.r_info(); r0 = R["r"]
L = g.liquidity("SCL"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]
TERP = (PX + c.RATIO * c.SUB_PX) / (1 + c.RATIO)
B = 1e9
RECV_CONC = 116.0 * 0.585      # phải thu KH 116,0 × 58,5% một tập đoàn BĐS (REPORT vòng 1 §3, §6) = 67,9 tỷ

BR = {"CYCLICAL": 0.50, "ADMIN_GATED": 0.30, "STRUCTURAL": 0.20}
AXES = dict(
    branch=[(b, b, w) for b, w in BR.items()],
    rev=[(x, x, 0.5) for x in c.GRID["rev"]],
    norm=[(x, x, 1 / 3) for x in c.GRID["norm"]],
    g=[(f"g{x:.0%}", x, 1 / 3) for x in c.GRID["g"]],
    roe=[(f"roe{x:.0%}", x, 0.5) for x in c.GRID["roe"]],
    recv=[("0%", 0.0, 0.75), ("20%", 0.20, 0.20), ("50%", 0.50, 0.05)],
)
AXES_BASIS = dict(
    branch="chế độ ngành CYCLICAL/ADMIN_GATED/STRUCTURAL 0,5/0,3/0,2 (Bobby sector read VLXD nhẹ 29/10, đọc mù); mức quay về TB biên 100/50/0% là THIẾT KẾ nhóm nghiên cứu [UL]",
    rev="DT TTM vs 2026E (Q4 = Q3, ước lượng), đều",
    norm="biên ròng chuẩn hoá: TB 2020–TTM / TB 2023–TTM / lệch biên gộp, đều",
    g="g 3/4/5% (ước lượng), đều — hai chiều",
    roe="ROE dài hạn 15/20% (ước lượng), đều — hai chiều",
    recv="lỗ trên phải thu tập trung 1 tập đoàn BĐS (58,5% × 116,0 = 67,9 tỷ, sau thuế ×0,8): 0% = sổ sách (chưa dự phòng; kiểm toán 2025 chấp nhận toàn phần) p0,75; "
         "20% p0,20; 50% p0,05 [UL]. Không có phía trên sổ sách ⇒ trục một phía là CẬN SỔ SÁCH",
)
AXES_EXCLUDED = [
    dict(axis="IRR dự án Phả Lại (lên 17% / xuống 10%)", reason="luật 03/11: dự án mới = giá vốn/NPV 0 khi không có giá/sản lượng/hợp đồng đầu ra kiểm được (lên) và không có số công suất vùng (xuống) — loại CẢ HAI chiều; báo song song bản CÓ trục 10/13,5/17% (0,25/0,5/0,25 [UL])"),
    dict(axis="nhánh suy giảm cấu trúc (biên dưới TB chu kỳ, gương của STRUCTURAL)", reason="sector read Bobby không có lớp này; TB 2020–TTM (biên thấp nhất) đã là cận dưới của trục norm. Báo song song bản đối xứng hoá: thêm TROUGH (quay về TB rồi vượt xuống 50% khoảng cách) trọng số 0,2 lấy đều từ 3 nhánh"),
    dict(axis="khung nợ theo mệnh giá toàn bộ", reason="khung mô hình (không phải trục kết cục) — r3 dùng làm cận dưới; báo song song"),
    dict(axis="pha loãng/ESOP tương lai, vay cổ đông lớn 26 tỷ @10%", reason="quản trị ⇒ WARNING"),
]


def fn(branch, rev, norm, g, roe, recv, irr=None, r=None, basis="cum"):
    rr = r0 if r is None else r
    if branch == "TROUGH":
        v = c.value("CYCLICAL", rev, norm, g, roe, c.GRID["i_cip"][0], rr)
        rv = c.TTM[0] if rev == "TTM" else c.E2026[0]
        m_now = c.NPM_TTM if rev == "TTM" else c.npm(*c.E2026)
        m = c.NPM_MEAN[norm] - 0.5 * (m_now - c.NPM_MEAN[norm])
        tot = (rv * m + c.CIP_TOTAL * c.GRID["i_cip"][0] * (1 - c.TAX)) * v["mult"]
    else:
        tot = c.value(branch, rev, norm, g, roe, c.GRID["i_cip"][0], rr)["v_total_pre"]
    tot -= recv * RECV_CONC * (1 - c.TAX)
    if irr is not None:
        tot += c.PHALAI_TOTAL * (irr / rr - 1)
    return tot * B / c.SH_NOW if basis == "cum" else (tot + c.PROCEEDS) * B / c.SH_POST


outs = g.build_grid(AXES, fn)
D = g.dist(outs, PX, disc)
outs_post = g.build_grid(AXES, lambda **kw: fn(basis="post", **kw))
Dp = g.dist(outs_post, TERP, disc)
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
lab_terp = g.label(TERP, Dp["P_post"]["p10"], Dp["P_post"]["p90"])
central = fn("ADMIN_GATED", "TTM", "2023-TTM", 0.04, 0.175, 0.0)  # tham số trung tâm: nhánh giữa, DT TTM, norm giữa, g 4%, ROE trung điểm 17,5%
p10_br = g.branch_share(outs, "branch", 0.10); p90_br = g.branch_share(outs, "branch", 0.90)

AX_IRR = dict(AXES, irr=[("10%", 0.10, 0.25), ("13.5%", 0.135, 0.50), ("17%", 0.17, 0.25)])
D_irr = g.dist(g.build_grid(AX_IRR, fn), PX, disc)
AX_TR = dict(AXES, branch=[("CYCLICAL", "CYCLICAL", 0.5 - 0.2 / 3), ("ADMIN_GATED", "ADMIN_GATED", 0.3 - 0.2 / 3),
                           ("STRUCTURAL", "STRUCTURAL", 0.2 - 0.2 / 3), ("TROUGH", "TROUGH", 0.2)])
D_tr = g.dist(g.build_grid(AX_TR, fn), PX, disc)
# khung nợ mệnh giá (r3 PAR): giá trị tại từng ô r3, cùng trục recv
def fn_par(branch, rev, norm, g, roe, recv):
    v = c.value_par(branch, rev, norm, g, roe, c.GRID["i_cip"][0], r0)["v_pre"] - recv * RECV_CONC * (1 - c.TAX)
    return v * B / c.SH_NOW
D_par = g.dist(g.build_grid(AXES, fn_par), PX, disc)

sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(g.build_grid(AXES, lambda **kw: fn(r=rr, **kw)), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)

# Gordon/ROE (điều 10): SCL không có tiền gửi đáng kể (tiền 95,1 vs nợ 416,5) ⇒ chỉ một biến thể; ghi rõ
roe_ttm = c.TTM[1] / c.EQ_PARENT
gordon = c.EQ_PARENT * (roe_ttm - 0.04) / (r0 - 0.04) * B / c.SH_NOW

base_adj = [
    dict(item="Phả Lại + Vĩnh Tân GĐ2 (XDCB 205,5 tỷ)", effect_dong_per_share=0.0, basis="giá vốn − nợ tài trợ = 0 ròng (luật NPV=0)", source="BCTC HN Q3/2026 XDCB; LCTT capex 9T 198,1 vs CFO 9,9"),
    dict(item="cộng lại lãi vay của nợ tài trợ dự án vào E (lãi P&L thực 4,96%)", effect_dong_per_share=c.eff["cip_effect_cum_dcp"],
         basis="không vừa trừ nợ theo mệnh giá vừa trừ lãi qua P/E; lãi P&L thực = 5,167×4/416,5 (SKEPTIC_R2); hiệu ứng = kỳ vọng lưới r3 (scl_r3_core.eff, đ/cp cum)", source="KQKD Q3/2026 mã 24"),
]
out = dict(ticker="SCL", asof_price_date=PX_DATE, price=PX, price_basis="CUM-quyền (ĐKCC 10/11/2026)", terp=TERP, r=r0, r_info=R, liq=L,
           dist=D, dist_post_rights=Dp, label=lab, label_terp=lab_terp, center_param=central, center_param_post=central * (1 - disc),
           p10_branch=p10_br, p90_branch=p90_br,
           parallel=dict(with_phalai_irr=D_irr, symmetric_branches_trough=D_tr, par_debt_framework=D_par),
           sens_r=sens_r, gordon=dict(g=0.04, roe_ttm=roe_ttm, value=gordon, note="không có biến thể 'không lãi tiền gửi': tiền 95,1 tỷ, nợ ròng 321,4; thu nhập TC không đáng kể"),
           axes_included=[dict(axis=k_, values=[(a, b, p) for a, b, p in v], basis=AXES_BASIS[k_]) for k_, v in AXES.items()],
           axes_excluded=AXES_EXCLUDED, base_adjustments=base_adj)
json.dump(out, open(os.path.join(HERE, "model_scl_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]; PP = Dp["P_post"]
lines = [f"SCL r2 giá {f(PX)} ({PX_DATE}, CUM) TERP {f(TERP)} | r {r0:.4f} | n kết cục {D['n']}",
         f"CUM: tâm TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 SAU {f(P['p50'])} | tham số trung tâm SAU {f(central*(1-disc))}",
         "CUM kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"CUM % trọng số dưới giá {D['pct_w_below_px']:.1%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%} | giá/P90 {PX/P['p90']-1:+.1%}",
         f"SAU QUYỀN: tâm SAU CK {f(Dp['center_post'])} " + " ".join(f"{k_} {f(v)}" for k_, v in PP.items()) + f" | TERP dưới-giá-trọng-số {Dp['pct_w_below_px']:.1%} ⇒ {lab_terp}",
         f"Nhánh quanh P10 {p10_br} | quanh P90 {p90_br}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; trong vùng √: {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()),
         f"SONG SONG có IRR Phả Lại: tâm {f(D_irr['center_post'])} P10 {f(D_irr['P_post']['p10'])} P90 {f(D_irr['P_post']['p90'])} | dưới giá {D_irr['pct_w_below_px']:.1%}",
         f"SONG SONG nhánh đối xứng (TROUGH 0,2): tâm {f(D_tr['center_post'])} P10 {f(D_tr['P_post']['p10'])} P90 {f(D_tr['P_post']['p90'])}",
         f"SONG SONG khung nợ mệnh giá: tâm {f(D_par['center_post'])} P10 {f(D_par['P_post']['p10'])} P90 {f(D_par['P_post']['p90'])}",
         "Độ nhạy r (CUM tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"Gordon g4% (CUM, trước CK): ROE TTM {roe_ttm:.1%} ⇒ {f(gordon)} (một biến thể — không có lãi tiền gửi đáng kể)"]
open(os.path.join(HERE, "model_scl_r2_out.txt"), "w").write("\n".join(lines) + "\n")
g.write_lock(os.path.join(HERE, "LOCK_r2_md5.txt"), g.COMMON_FILES + [os.path.abspath(__file__), os.path.join(HERE, "scl_r3_core.py")], "SCL r2")
print("\n".join(lines))
