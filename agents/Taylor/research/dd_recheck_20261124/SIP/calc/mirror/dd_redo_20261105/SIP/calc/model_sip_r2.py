"""SIP — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020018) theo STANDARD_r2.md.
Hàm giá trị = vòng 1 (model_sip.py, SOTP), chỉ thêm tham số ktpl. Số BCTC chép NGUYÊN từ model_sip.py (nguồn TM ghi ở đó).
ĐỔI so vòng 1:
  - Lưới vòng 1 gói credit_loss/NCI/thu hồi/thuế tương lai VÀO kịch bản (chỉ lệch xuống ở 'xấu') ⇒ vi phạm điều 2.
    Vòng 2: các trục ĐỘC LẬP, mỗi trục có cả hai chiều quanh giá trị cơ sở (hoặc giải thích vì sao một phía là cận sổ sách).
  - Phân vị mức kết cục bằng _shared/wpct.py (vòng 1 dùng CDF bậc thang tự viết).
Chạy: $DNA_PYEXE -I model_sip_r2.py → model_sip_r2_out.json/.txt + LOCK_r2_md5.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
import ddr2 as g

SH = 242.112943
cash, deposits, loans_sc, bonds, stocks_fv = 400.8, 7187.6, 4223.4, 1792.4, 203.9
debt = 4599.3 + 894.9
infra_accrued = 3262.8
ktpl_fund = 638.8
deferred_rev = 457.2 + 14620.0
nci_profit = 100.3 / 1178.3
bonds_unsec_ex_vhm = 1792.4 - 363.6
loans_unsec = loans_sc * 0.6893
parent_net = 221.2 + 1792.4 + 6912.2 - 5491.9 - 2652.8
spent_land = 2529.6 + 290.6 + 1268.9 + 204.7 + 163.5
LAND_HA = 937.1
ROE5Y = 0.297
k = 4 / 3
gp = dict(util=497.0, land=235.8, kcn_svc=238.4, goods=25.9, constr=3.6, re=43.3, other=28.3)
sga = 33.2 + 75.2
assoc = 47.8
TAX = 0.20
KTPL_9T = 97.5 / 1078.0               # TM36 9T26 ước tính = 9,04%
KTPL_2025 = 0.0725                    # thực trích 2025 (GAPS G13, SKEPTIC F1: ~119/1.322,9 ≈ 9%; 7,25% theo NQ phân phối) — trục
core_ops_pt = (sum(gp.values()) - gp["land"]) * k - sga * k
subs_net = (cash + deposits + loans_sc + bonds + stocks_fv - debt - infra_accrued) - parent_net
# Gordon/ROE (điều 10) — BCĐ HN 30/09: VCSH 5.744,4 − NCI 568,4; EPS TTM theo BCTC 5.184 (sau KTPL); lãi TG+cho vay 9T 602,0 (TM28)
EQ_PARENT = 5744.4 - 568.4
NP_TTM = 5184 * SH / 1000
FIN_INC_Y = 602.0 * k

R = g.r_info(); r0 = R["r"]
L = g.liquidity("SIP"); PX, PX_DATE = L["price"], L["price_date"]
disc = L["ref_discount"]


def pv_even(total, yrs, r):
    return sum(total / yrs / (1 + r) ** (t + 0.5) for t in range(yrs))


def value(r, gcore, perha, yrs, credit_loss, nci_sub, recover, taxdef_mult, ktpl=KTPL_9T, adv_loss=0.0):
    pe = (1 - gcore / ROE5Y) / (r - gcore)
    core = (core_ops_pt * (1 - TAX) + assoc * k) * (1 - nci_profit) * (1 - ktpl) * pe
    fin = parent_net + subs_net * (1 - nci_sub) - ktpl_fund
    loss = credit_loss * (loans_unsec + bonds_unsec_ex_vhm)
    taxdef = pv_even(deferred_rev * 0.69 * TAX, 35, r) * taxdef_mult
    land = pv_even(LAND_HA * perha, yrs, r) * (1 - nci_profit) * (1 - ktpl)
    sunk = pv_even(spent_land * recover, yrs, r) * (1 - nci_profit)
    tot = core + fin - loss - taxdef + land + sunk - adv_loss
    return tot / SH * 1000


# ---- TRỤC (xác suất đều là [UL] trừ khi ghi nguồn) ----
LANDMKT = [  # (giá thực thu tỷ/ha toàn phần, số năm bán hết 937 ha) — gắn nhau vì cùng do cầu thuê quyết định
    ("tot", (18.0, 15), 0.20),   # ~150 USD/m², ~62 ha/năm (KH 2026 60 ha, AR25)
    ("co_so", (12.0, 22), 0.50),  # ~110–120 USD/m², ~43 ha/năm
    ("xau", (6.0, 30), 0.30),    # ~90 USD/m² + đền bù tăng, ~31 ha/năm (2025 thực 28,6 ha vs KH 45 — AR25; Bobby Tây Ninh −6,8% YoY)
]
AXES = dict(
    land=LANDMKT,
    perha_mult=[("x0.75", 0.75, 1 / 3), ("x1", 1.0, 1 / 3), ("x1.25", 1.25, 1 / 3)],
    gcore=[("g2", 0.02, 0.25), ("g3", 0.03, 0.50), ("g4", 0.04, 0.25)],
    credit=[("0%", 0.00, 0.60), ("10%", 0.10, 0.25), ("30%", 0.30, 0.15)],
    nci=[("8.5%", 0.085, 0.25), ("20%", 0.20, 0.50), ("31%", 0.31, 0.25)],
    recover=[("100%", 1.0, 0.75), ("60%", 0.6, 0.25)],
    taxdef=[("x0.8", 0.8, 0.25), ("x1", 1.0, 0.50), ("x1.2", 1.2, 0.25)],
    ktpl=[("7.25%", KTPL_2025, 0.5), ("9.04%", KTPL_9T, 0.5)],
)
AXES_BASIS = dict(
    land="kịch bản thị trường đất 20/50/30 nghiêng xuống (ước lượng; giữ từ DD 01/11 vì 2025 chỉ 28,6 ha vs KH 45)",
    perha_mult="×0,75/1/1,25 quanh tỷ/ha mỗi kịch bản, đều (ước lượng) — hai chiều",
    gcore="g mảng vận hành 2/3/4% (ước lượng) — hai chiều đối xứng",
    credit="lỗ trên tín dụng KHÔNG bảo đảm (cho vay CTCK 68,93% + TP trừ VHM): 0% = sổ sách (EY chấp nhận toàn phần, chưa dự phòng; "
           "cách đọc nhẹ TM4b: bên thứ ba = ngân hàng cho vay) p0,60; 10% p0,25; 30% p0,15 [UL]. Phía trên 0% không tồn tại (không thu quá gốc) ⇒ "
           "trục một phía là CẬN SỔ SÁCH, không phải chọn chiều",
    nci="NCI hiệu dụng trên tài sản ròng ở con 8,5/20/31% (8,5% = tỷ trọng LN; 31% = NCI VRG Long Thành, TM1) — chưa có BCTC từng con (G14)",
    recover="thu hồi chi phí đã chi cho quỹ đất: 100% = giá vốn (luật NPV=0) p0,75; 60% p0,25 (đền bù tăng theo bảng giá đất — Bobby KCN; tạm ứng PĐ-BL 2.421 chưa quyết toán) [UL]. "
            "Phía >100% đã nằm ở trục tỷ/ha (giá trị đất gia tăng) ⇒ không đếm hai lần",
    taxdef="PV thuế TNDN tương lai trên DT chưa thực hiện ×0,8/1/1,2 (ưu đãi/phần không chịu thuế vs thuế suất thực cao hơn) [UL]",
    ktpl="quỹ KTPL: 7,25% (thực 2025, G13) / 9,04% (ước tính 9T26, TM36), đều",
)
AXES_EXCLUDED = [
    dict(axis="tạm ứng 635,6 tỷ cho HĐQT/BGĐ/BKS/quản lý (TM40)", reason="quản trị/bên liên quan ⇒ WARNING (luật skill: pháp lý/quản trị không vào tâm); báo song song bản CÓ trục (mất trọn p0,15 [UL])"),
    dict(axis="kịch bản 'thuế đã nộp khi thu tiền' (+~2.000 đ/cp)", reason="BCĐ bác: không có TS thuế hoãn lại; thuế hiện hành 19,9% LNTT dù DT chưa TH +1.701,8 (SKEPTIC F7) ⇒ xác suất ≈0; chiều xuống tương ứng nằm ở trục taxdef ×1,2"),
    dict(axis="tiền thuê đất hằng năm trả Nhà nước trên đất đã cho thuê lại (G16)", reason="chưa có dữ liệu định lượng (chính sách kế toán/QĐ giao đất chưa đọc) — không có cả hai chiều; giữ open_issue"),
    dict(axis="chiết khấu quản trị 10% (DD 01/11)", reason="quản trị = WARNING; báo song song"),
]


def fn(land, perha_mult, gcore, credit, nci, recover, taxdef, ktpl, adv_loss=0.0, r=None):
    perha, yrs = land
    return value(r0 if r is None else r, gcore, perha * perha_mult, yrs, credit, nci, recover, taxdef, ktpl, adv_loss)


outs = g.build_grid(AXES, fn)
D = g.dist(outs, PX, disc)
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
# giá trị tại tham số trung tâm (điều 4)
central = fn((12.0, 22), 1.0, 0.03, 0.0, 0.20, 1.0, 1.0, KTPL_9T)
p10_branch = g.branch_share(outs, "land", 0.10); p90_branch = g.branch_share(outs, "land", 0.90)
p10_credit = g.branch_share(outs, "credit", 0.10)

# Song song (điều 2): bản CÓ trục tạm ứng bên liên quan (mất trọn 635,6 tỷ p0,15 [UL])
AX_ADV = dict(AXES, adv_loss=[("0", 0.0, 0.85), ("mat_tron", 635.6, 0.15)])
D_adv = g.dist(g.build_grid(AX_ADV, fn), PX, disc)
# Song song: trọng số kịch bản đất đối xứng 25/50/25
AX_SYM = dict(AXES, land=[("tot", (18.0, 15), 0.25), ("co_so", (12.0, 22), 0.50), ("xau", (6.0, 30), 0.25)])
D_sym = g.dist(g.build_grid(AX_SYM, fn), PX, disc)
# Song song: lưới vòng 1 (n=27) tính lại bằng wpct chuẩn — để tách hiệu ứng "đổi lưới" khỏi "đổi hàm phân vị"
SC1 = dict(tot=(0.20, 0.04, 18.0, 15, 0.0, 0.085, 1.0, 0.8), co_so=(0.50, 0.03, 12.0, 22, 0.0, 0.20, 1.0, 1.0), xau=(0.30, 0.02, 6.0, 30, 0.30, 0.31, 0.6, 1.2))
v1, w1 = [], []
for w, gc, ph, yr, cl, nc, rc, td in SC1.values():
    for m in (0.75, 1.0, 1.25):
        for dg in (-0.01, 0.0, 0.01):
            v1.append(value(r0, gc + dg, ph * m, yr, cl, nc, rc, td)); w1.append(w / 9)
D_r1grid = g.dist([dict(v=a, w=b, labels={}) for a, b in zip(v1, w1)], PX, disc)

# Độ nhạy r: tâm SAU CK
sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(g.build_grid(AXES, lambda **kw: fn(r=rr, **kw)), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)

# Gordon/ROE (điều 10), g 3%
gg = 0.03
roe_all = NP_TTM / EQ_PARENT
gordon_with = EQ_PARENT * (roe_all - gg) / (r0 - gg) / SH * 1000
net_fin_parent_share = parent_net + subs_net * (1 - 0.20) - ktpl_fund
np_ex = NP_TTM - FIN_INC_Y * (1 - TAX) * (1 - nci_profit)
eq_ex = EQ_PARENT - net_fin_parent_share
gordon_without = (eq_ex * (np_ex / eq_ex - gg) / (r0 - gg) + net_fin_parent_share) / SH * 1000

base_adj = [
    dict(item="nghĩa vụ hạ tầng đất đã cho thuê", effect_dong_per_share=-infra_accrued / SH * 1000, basis="nợ phải trả trên sổ", source="TM20 BCTC HN Q3/2026"),
    dict(item="quỹ KTPL", effect_dong_per_share=-ktpl_fund / SH * 1000, basis="nợ phải trả trên sổ", source="BCĐ mã 323"),
    dict(item="PV thuế TNDN tương lai trên DT chưa thực hiện (×1)", effect_dong_per_share=-pv_even(deferred_rev * 0.69 * TAX, 35, r0) / SH * 1000,
         basis="luật thuế TNDN 20%; thuế nộp theo phân bổ (không có TS thuế hoãn lại, thuế hiện hành 19,9% LNTT)", source="TM21, BCĐ; SKEPTIC F7"),
    dict(item="NCI 20% trên tài sản ròng ở con (cơ sở)", effect_dong_per_share=-subs_net * 0.20 / SH * 1000, basis="trung điểm 8,5% (tỷ trọng LN) và 31% (VRG Long Thành)", source="KQKD 9T26; TM1"),
]
SUMR2 = dict(
    axes_included=[dict(axis=k_, values=[(a, (list(b) if isinstance(b, tuple) else b), p) for a, b, p in v], basis=AXES_BASIS[k_]) for k_, v in AXES.items()],
    axes_excluded=AXES_EXCLUDED, base_adjustments=base_adj,
)
out = dict(ticker="SIP", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, dist=D, label=lab,
           center_param=central, center_param_post=central * (1 - disc),
           p10_land_branch=p10_branch, p90_land_branch=p90_branch, p10_credit_branch=p10_credit,
           parallel=dict(with_related_party_advance=D_adv, land_weights_25_50_25=D_sym, r1_grid_wpct=D_r1grid),
           sens_r=sens_r, gordon=dict(g=gg, roe_all=roe_all, with_interest=gordon_with, without_interest=gordon_without,
                                      roe_ex=np_ex / eq_ex),
           **SUMR2)
json.dump(out, open(os.path.join(HERE, "model_sip_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]
lines = [f"SIP r2 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} | n kết cục {D['n']}",
         f"Tâm (kỳ vọng lưới) TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 SAU {f(P['p50'])} | tham số trung tâm SAU {f(central*(1-disc))}",
         "Kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"% trọng số dưới giá {D['pct_w_below_px']:.1%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%}",
         f"Nhánh đất quanh P10 {p10_branch} | quanh P90 {p90_branch} | tín dụng quanh P10 {p10_credit}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; trong vùng √: {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()),
         f"SONG SONG có tạm ứng bên liên quan (mất trọn p0,15): tâm {f(D_adv['center_post'])} P10 {f(D_adv['P_post']['p10'])} P90 {f(D_adv['P_post']['p90'])}",
         f"SONG SONG đất 25/50/25: tâm {f(D_sym['center_post'])} P10 {f(D_sym['P_post']['p10'])} P90 {f(D_sym['P_post']['p90'])}",
         f"SONG SONG lưới vòng 1 (n27) + wpct chuẩn: tâm {f(D_r1grid['center_post'])} P10 {f(D_r1grid['P_post']['p10'])} P50 {f(D_r1grid['P_post']['p50'])} P90 {f(D_r1grid['P_post']['p90'])}",
         "Độ nhạy r (tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"Gordon g3% (trước CK): có lãi TG (ROE {roe_all:.1%}) {f(gordon_with)} | không lãi TG (ROE vận hành {np_ex/eq_ex:.1%} + TS tài chính ròng theo sổ) {f(gordon_without)}"]
open(os.path.join(HERE, "model_sip_r2_out.txt"), "w").write("\n".join(lines) + "\n")
g.write_lock(os.path.join(HERE, "LOCK_r2_md5.txt"), g.COMMON_FILES + [os.path.abspath(__file__)], "SIP r2")
print("\n".join(lines))
