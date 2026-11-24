"""SIP — DD redo VÒNG 3 (09/11/2026, job Taylor_20261108_180132). Áp/kiểm đính chính TOP5D_CORRECTIONS_20261108.md mục SIP.
Giả định khoá: assumptions_r3.json (md5 vào LOCK_md5.txt bởi lock_r3.sh TRƯỚC khi chạy — model KHÔNG ghi LOCK).
Số BCTC chép NGUYÊN từ ../calc/model_sip_r2.py (không import: file đó ghi output khi chạy). Control: tái lập r2 54.230 (giá/CK 04/11).
Giá + thanh khoản r3: px_sip_r3_20261106.csv (BQ tav2_bq.ticker, px_sip_r3.sql).
Chạy: cd calc_r3 && $DNA_PYEXE -I model_r3.py > runN.txt (2 lần, cmp trùng byte)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "_common_g2r2"))
import ddr2 as g                     # noqa: E402
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = json.load(open(os.path.join(HERE, "assumptions_r3.json")))
ASOF = A["asof_price"]
# ---- số BCTC (y hệt ../calc/model_sip_r2.py; nguồn TM ở ../calc/model_sip.py) ----
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
KTPL_9T = 97.5 / 1078.0
KTPL_2025 = 0.0725
core_gp = sum(gp.values()) - gp["land"]
subs_net = (cash + deposits + loans_sc + bonds + stocks_fv - debt - infra_accrued) - parent_net
# ---- r3 ----
BOOK_ADD = sum(v for kk, v in A["book_assets_added_ty"].items() if kk != "basis")
ADV = A["advance_insiders_ty"]["value"]
S = A["sensitivities_not_in_center"]
d0 = effective_deposit_rate("2026-11-03"); d1 = effective_deposit_rate(ASOF)
R0 = 0.135 + 1.0 * (d1["rate"] - d0["rate"])


def pv_even(total, yrs, r):
    return sum(total / yrs / (1 + r) ** (t + 0.5) for t in range(yrs))


def value(r, gcore, perha, yrs, credit_loss, nci_sub, recover, taxdef_mult, ktpl=KTPL_9T, *, ronic_ke=True, book_add=BOOK_ADD,
          adv=ADV, ktpl_def=True, adv_loss=0.0, ha_less=0.0, gpm_mult=1.0, extra=0.0):
    pe = 1 / r if ronic_ke else (1 - gcore / ROE5Y) / (r - gcore)
    core_pt = (core_gp * gpm_mult) * k - sga * k
    core = (core_pt * (1 - TAX) + assoc * k) * (1 - nci_profit) * (1 - ktpl) * pe
    fin = parent_net + subs_net * (1 - nci_sub) - ktpl_fund + book_add + extra
    loss = credit_loss * (loans_unsec + bonds_unsec_ex_vhm)
    taxdef = pv_even(deferred_rev * 0.69 * TAX, 35, r) * taxdef_mult
    kdef = pv_even(deferred_rev * 0.69 * (1 - TAX) * (1 - nci_profit) * ktpl, 35, r) if ktpl_def else 0.0
    land = pv_even((LAND_HA - ha_less) * perha, yrs, r) * (1 - nci_profit) * (1 - ktpl)
    sunk = pv_even((spent_land + adv) * recover, yrs, r) * (1 - nci_profit)
    return (core + fin - loss - taxdef - kdef + land + sunk - adv_loss) / SH * 1000


W = A["land_weights"]; SC = A["land_scenarios"]
LAND = [(n, tuple(SC[n]), W[n]) for n in ("tot", "co_so", "xau")]
LAND_R2 = [("tot", (18.0, 15), 0.20), ("co_so", (12.0, 22), 0.50), ("xau", (6.0, 30), 0.30)]
AX = dict(
    land=LAND,
    perha_mult=[("x0.75", 0.75, 1 / 3), ("x1", 1.0, 1 / 3), ("x1.25", 1.25, 1 / 3)],
    gcore=[("g2", 0.02, 0.25), ("g3", 0.03, 0.50), ("g4", 0.04, 0.25)],
    credit=[("0%", 0.00, 0.60), ("10%", 0.10, 0.25), ("30%", 0.30, 0.15)],
    nci=[("8.5%", 0.085, 0.25), ("20%", 0.20, 0.50), ("31%", 0.31, 0.25)],
    recover=[("100%", A["recover"]["value"], 1.0)],
    taxdef=[("x0.8", 0.8, 0.25), ("x1", 1.0, 0.50), ("x1.2", 1.2, 0.25)],
    ktpl=[("7.25%", KTPL_2025, 0.5), ("9.04%", KTPL_9T, 0.5)],
)
AX_R2 = dict(AX, land=LAND_R2, recover=[("100%", 1.0, 0.75), ("60%", 0.6, 0.25)])


def run(axes, r, disc, px, **opt):
    def fn(land, perha_mult, gcore, credit, nci, recover, taxdef, ktpl):
        return value(r, gcore, land[0] * perha_mult, land[1], credit, nci, recover, taxdef, ktpl, **opt)
    outs = g.build_grid(axes, fn)
    return outs, g.dist(outs, px, disc)


R2OPT = dict(ronic_ke=False, book_add=0.0, adv=0.0, ktpl_def=False)
# ---- CONTROL: r2 (giá/CK/r 04/11) ----
L2 = g.liquidity("SIP")
_, D_ctrl = run(AX_R2, 0.135, L2["ref_discount"], L2["price"], **R2OPT)
# ---- dữ liệu r3 ----
g.PX_CSV = os.path.join(HERE, "px_sip_r3_20261106.csv")
L = g.liquidity("SIP"); assert L["price_date"] == ASOF, L["price_date"]
PX, disc = L["price"], L["ref_discount"]
SLV = L["sleeve_discount"]["40tr"]

# ---- CẦU r2 → r3 (luỹ kế, tâm SAU CK 5 tỷ) ----
steps = []
cur_ax, cur_opt = AX_R2, dict(R2OPT)
def step(name, ax=None, **o):
    global cur_ax, cur_opt
    cur_ax = ax or cur_ax; cur_opt.update(o)
    c = run(cur_ax, R0, disc, PX, **cur_opt)[1]["center_post"]
    steps.append(dict(step=name, center_post=c))
steps.append(dict(step="r2 (giá/CK/r 04/11) — control", center_post=D_ctrl["center_post"]))
step("0 giá/CK/r 06/11")
step("1 RONIC=Ke (đ.chính #1)", ronic_ke=True)
step("2 đất 25/50/25 (#2)", ax=dict(AX_R2, land=LAND))
step("3 thu hồi 100% (#3)", ax=AX)
step("4 tài sản sổ sách 396,8 (#4)", book_add=BOOK_ADD)
step("5 KTPL trên LN DT chưa thực hiện (#5)", ktpl_def=True)
step("6 tạm ứng 643,7 theo sổ (Taylor thêm, #6b)", adv=ADV)
for i in range(1, len(steps)):
    steps[i]["delta"] = steps[i]["center_post"] - steps[i - 1]["center_post"]

# ---- HEADLINE r3 ----
outs, D = run(AX, R0, disc, PX)
_, D_sl = run(AX, R0, SLV, PX)
lab5 = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"]); labS = g.label(PX, D_sl["P_post"]["p10"], D_sl["P_post"]["p90"])
central = value(R0, 0.03, 12.0, 22, 0.0, 0.20, 1.0, 1.0, KTPL_9T) * (1 - disc)
p10_branch = g.branch_share(outs, "land", 0.10); p90_branch = g.branch_share(outs, "land", 0.90)

# ---- ĐỘ NHẠY (không vào tâm) — Δ tâm SAU CK so headline ----
def c(ax=AX, **o):
    return run(ax, R0, disc, PX, **o)[1]["center_post"]
H = D["center_post"]
sens = {
    "VAT_khau_tru_890_5_tru_DTL_123_7 (+766,8 theo sổ)": c(extra=S["vat_minus_dtl_ty"]["value"]) - H,
    "dat_cho_thue_9T26_moi_50ha": c(ha_less=S["ha_leased_9T26"]["per_ha"]) - H,
    "thu_hoi_60pct_p0.25 (truc r2)": c(dict(AX, recover=[("100%", 1.0, 0.75), ("60%", 0.6, 0.25)])) - H,
    "GPM_ve_TB_2019_25 (x0,9457 LN gop van hanh)": c(gpm_mult=S["gpm_peak_normalisation"]["factor"]) - H,
    "NCI_con_9_9pct_co_dinh (BCD)": c(dict(AX, nci=[("9.9%", S["nci_bs_9_9"]["value"], 1.0)])) - H,
    "dat_20_50_30 (trong so r2)": c(dict(AX, land=LAND_R2)) - H,
    "RONIC=ROE5Y 29,7% (quy uoc r2)": c(ronic_ke=False) - H,
    "bo_tam_ung_643_7 (=0 nhu r2)": c(adv=0.0) - H,
}
sens_r = {kk: dict(r=rr, post=c_r, pct=c_r / H - 1) for kk, rr in g.r_grid(R0).items()
          for c_r in [run(AX, rr, disc, PX)[1]["center_post"]]}

# ---- SONG SONG ----
AX_ADV = dict(AX)
def fn_adv_axes():
    o1, _ = run(AX, R0, disc, PX)
    o2, _ = run(AX, R0, disc, PX, adv_loss=ADV, adv=0.0)
    allo = [dict(o, w=o["w"] * 0.85) for o in o1] + [dict(o, w=o["w"] * 0.15) for o in o2]
    return g.dist(allo, PX, disc)
D_adv = fn_adv_axes()
_, D_noadv = run(AX, R0, disc, PX, adv=0.0)
_, D_gov10 = run(AX, R0, disc, PX)
gov10 = dict(center_post=D_gov10["center_post"] * 0.9, p10=D_gov10["P_post"]["p10"] * 0.9, p90=D_gov10["P_post"]["p90"] * 0.9)

# ---- GIÁ NGỤ Ý ----
def solve(f, lo, hi):
    for _ in range(80):
        m = (lo + hi) / 2
        if (f(m) - PX) * (f(lo) - PX) > 0:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2
perha_scale = solve(lambda s: run(dict(AX, land=[(n, (v[0] * s, v[1]), p) for n, v, p in LAND]), R0, disc, PX)[1]["center_post"], 0.0, 3.0)
r_impl = solve(lambda rr: run(AX, rr, disc, PX)[1]["center_post"], 0.08, 0.30)

out = dict(ticker="SIP", round=3, asof_price_date=ASOF, price=PX, r=R0, deposit_anchor=d0, deposit_asof=d1, liq=L,
           control_r2=dict(center_post=D_ctrl["center_post"], p10=D_ctrl["P_post"]["p10"], p90=D_ctrl["P_post"]["p90"], price=L2["price"], disc=L2["ref_discount"]),
           dist=D, dist_sleeve40=D_sl, label_5ty=lab5, label_sleeve40=labS, center_param_post=central,
           p10_land_branch=p10_branch, p90_land_branch=p90_branch,
           rule4_5ty=PX <= 0.85 * D["center_post"], rule4_sleeve40=PX <= 0.85 * D_sl["center_post"],
           bridge=steps, sens=sens, sens_r=sens_r,
           parallel=dict(advance_loss_p015=dict(center_post=D_adv["center_post"], p10=D_adv["P_post"]["p10"], p90=D_adv["P_post"]["p90"]),
                         advance_zero=dict(center_post=D_noadv["center_post"], p10=D_noadv["P_post"]["p10"], p90=D_noadv["P_post"]["p90"]),
                         gov_disc_10=gov10),
           implied=dict(land_perha_scale=perha_scale, land_perha_coso=12.0 * perha_scale, r=r_impl))
json.dump(out, open(os.path.join(HERE, "model_r3_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]; Ps = D_sl["P_post"]
print(f"SIP r3 giá {f(PX)} ({ASOF}) | r {R0:.4f} (huy động {d0['rate']:.4f}→{d1['rate']:.4f}) | n {D['n']}")
print(f"CONTROL r2: tâm {f(D_ctrl['center_post'])} P10 {f(D_ctrl['P_post']['p10'])} P90 {f(D_ctrl['P_post']['p90'])} (kỳ vọng 54.230/43.784/68.713)")
print(f"HEADLINE @5 tỷ (CK {disc:.2%}): tâm {f(D['center_post'])} P10 {f(P['p10'])} P50 {f(P['p50'])} P90 {f(P['p90'])} min {f(D['min_post'])} max {f(D['max_post'])} | dưới giá {D['pct_w_below_px']:.1%} | {lab5} | luật4 {out['rule4_5ty']} (0,85×tâm {f(0.85*D['center_post'])})")
print(f"SLEEVE 40tr (CK {SLV:.2%}): tâm {f(D_sl['center_post'])} P10 {f(Ps['p10'])} P50 {f(Ps['p50'])} P90 {f(Ps['p90'])} | dưới giá {D_sl['pct_w_below_px']:.1%} | {labS} | luật4 {out['rule4_sleeve40']}")
print(f"tham số trung tâm SAU CK {f(central)} | nhánh đất quanh P10 {p10_branch} | quanh P90 {p90_branch}")
print("CẦU: " + " | ".join(f"{s['step']} {f(s['center_post'])}" + (f" ({s['delta']:+,.0f})" if 'delta' in s else "") for s in steps))
print("ĐỘ NHẠY: " + " | ".join(f"{kk} {v:+,.0f}" for kk, v in sens.items()))
print("ĐỘ NHẠY r: " + " | ".join(f"{kk} {f(v['post'])} ({v['pct']:+.1%})" for kk, v in sens_r.items()))
print(f"SONG SONG: mất trọn tạm ứng p0,15 tâm {f(D_adv['center_post'])} P10 {f(D_adv['P_post']['p10'])} | tạm ứng=0 tâm {f(D_noadv['center_post'])} P10 {f(D_noadv['P_post']['p10'])} P90 {f(D_noadv['P_post']['p90'])} | CK quản trị 10% tâm {f(gov10['center_post'])}")
print(f"GIÁ NGỤ Ý: tỷ/ha ×{perha_scale:.3f} (cơ sở {12*perha_scale:.2f} tỷ/ha) hoặc r {r_impl:.4f}")
