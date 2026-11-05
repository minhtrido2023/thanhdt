"""SIP — DD redo 05/11/2026 (job Taylor_20261105_014130). SOTP theo khung skill due-diligence luật 03/11.
Chạy: PYTHONPATH=../../_common_g2 $DNA_PYEXE -I model_sip.py  (hoặc từ bất kỳ đâu; tự thêm path)
→ model_sip_out.json + model_sip_out.txt. Đơn vị: tỷ VND trừ khi ghi khác.

NGUỒN SỐ ĐẦU VÀO (không chép giá trị đầu ra cũ — chỉ chép SỐ BCTC):
  dd_SIP_20261101/calc/notes_read.md (đọc ảnh BCTC HN Q3/2026 src/20261030-...-hop-nhat-q3-2026.pdf + riêng Q3)
  → mỗi biến dưới ghi mã thuyết minh (TMxx/BCĐ).
ĐỔI so với DD 01/11 (valuation.py v2) — theo luật skill hiện hành:
  1. r: 13,0% cứng (PV đất) + PE core gán tay 7/9/10x  →  r = 13,5% neo lãi huy động (ddg2.r_info) và
     PE core = (1 − g/RONIC)/(r − g) (RONIC = ROE5Y 29,7% BQ, g 2/3/4% (ước lượng)) ⇒ độ nhạy r có nghĩa.
  2. Chiết khấu QUẢN TRỊ 10%/20% trong cơ sở/xấu  →  BỎ khỏi mọi kịch bản (pháp lý/quản trị = WARNING); nêu độ nhạy.
  3. Lỗ tín dụng 5% trong CƠ SỞ (không có dữ liệu: EY chấp nhận toàn phần, BTGĐ chưa thấy suy giảm, không dự phòng)
     → cơ sở 0%; giữ 30% ở kịch bản xấu (cơ sở dữ liệu cụ thể: 68,93% không TS bảo đảm TM4b, GTHL TP chưa xác định TM4a).
  4. Thu hồi chi phí đã chi cho quỹ đất 60% ở cơ sở  →  100% (luật NPV=0: phần đã chi = tài sản theo giá vốn);
     60% chỉ ở kịch bản xấu (cơ sở: đền bù tăng theo bảng giá đất hằng năm — Bobby KCN 01/11; tạm ứng PĐ-BL 2.421 chưa quyết toán).
  5. Thanh khoản: chiết khấu đăng ký trước (ddg2.liquidity) — báo TRƯỚC và SAU.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2"))
import ddg2 as g

SH = 242.112943                       # triệu cp (TM24)
# --- BCĐ HN 30/09/2026 (notes_read.md) ---
cash, deposits, loans_sc, bonds, stocks_fv = 400.8, 7187.6, 4223.4, 1792.4, 203.9   # BCĐ; TM4b; TM4a
debt = 4599.3 + 894.9                 # vay NH + DH (TM23)
infra_accrued = 3262.8                # CP phải trả DH = nghĩa vụ hạ tầng đất đã cho thuê (TM20)
ktpl_fund = 638.8                     # quỹ KTPL (BCĐ mã 323)
deferred_rev = 457.2 + 14620.0        # DT chưa thực hiện (TM21)
nci_profit = 100.3 / 1178.3           # LNST NCI/LNST 9T26 = 8,5%
bonds_unsec_ex_vhm = 1792.4 - 363.6   # TP trừ Vinhomes (TM4a)
loans_unsec = loans_sc * 0.6893       # 68,93% không TS bảo đảm bên vay (TM4b)
parent_net = 221.2 + 1792.4 + 6912.2 - 5491.9 - 2652.8   # BCTC riêng mẹ 30/09: tiền + TP + HTM − vay − CP hạ tầng phải trả
spent_land = 2529.6 + 290.6 + 1268.9 + 204.7 + 163.5     # TM7 tạm ứng đền bù + TM10 XDCB KCN (loại nhà xưởng LMX3, cảng)
LAND_HA = 937.1                       # ha chưa cho thuê (AR25)
ROE5Y = 0.297                         # BQ ticker_financial ROE5Y (comps 30/10, dd_SIP_20261101/calc/comps_bq.csv)
# --- KQKD 9T26 (TM25/27, TM28, TM29) ---
k = 4 / 3
gp = dict(util=497.0, land=235.8, kcn_svc=238.4, goods=25.9, constr=3.6, re=43.3, other=28.3)
sga = 33.2 + 75.2
assoc = 47.8                          # LDLK sau thuế
TAX = 0.20
KTPL = 97.5 / 1078.0                  # trích KTPL 9T26 ước tính (TM36)
core_ops_pt = (sum(gp.values()) - gp["land"]) * k - sga * k   # run-rate trước thuế vận hành (ước lượng ×4/3)
subs_net = (cash + deposits + loans_sc + bonds + stocks_fv - debt - infra_accrued) - parent_net

R = g.r_info()
L = g.liquidity("SIP")
PX, PX_DATE = L["price"], L["price_date"]


def pv_even(total, yrs, r):
    return sum(total / yrs / (1 + r) ** (t + 0.5) for t in range(yrs))


def value(r, gcore, perha, yrs, credit_loss, nci_sub, recover, taxdef_mult, gov_disc=0.0):
    pe = (1 - gcore / ROE5Y) / (r - gcore)
    core = (core_ops_pt * (1 - TAX) + assoc * k) * (1 - nci_profit) * (1 - KTPL) * pe
    fin = parent_net + subs_net * (1 - nci_sub) - ktpl_fund
    loss = credit_loss * (loans_unsec + bonds_unsec_ex_vhm)
    taxdef = pv_even(deferred_rev * 0.69 * TAX, 35, r) * taxdef_mult   # thuế TNDN tương lai trên DT chờ phân bổ (69% phần thuộc con/mẹ chịu thuế — giữ quy ước DD cũ)
    land = pv_even(LAND_HA * perha, yrs, r) * (1 - nci_profit) * (1 - KTPL)
    sunk = pv_even(spent_land * recover, yrs, r) * (1 - nci_profit)
    tot = (core + fin - loss - taxdef + land + sunk) * (1 - gov_disc)
    return tot / SH * 1000, dict(pe=pe, core=core, fin=fin, loss=loss, taxdef=taxdef, land=land, sunk=sunk, tot=tot)


# Kịch bản (giả định (ước lượng) trừ dòng có nguồn)
SCEN = {
    "tot":  dict(w=0.20, gcore=0.04, perha=18.0, yrs=15, credit_loss=0.00, nci_sub=0.085, recover=1.0, taxdef_mult=0.8,
                 note="~150 USD/m² thực thu, ~62 ha/năm (KH 2026 60 ha AR25)"),
    "co_so": dict(w=0.50, gcore=0.03, perha=12.0, yrs=22, credit_loss=0.00, nci_sub=0.20, recover=1.0, taxdef_mult=1.0,
                 note="~110–120 USD/m², ~43 ha/năm; tín dụng 0% (không dự phòng, EY chấp nhận toàn phần)"),
    "xau":  dict(w=0.30, gcore=0.02, perha=6.0, yrs=30, credit_loss=0.30, nci_sub=0.31, recover=0.6, taxdef_mult=1.2,
                 note="~90 USD/m² + đền bù tăng, ~31 ha/năm (2025 thực 28,6 ha); lỗ 30% tín dụng không bảo đảm"),
}
SCEN_W_BASIS = "20/50/30 nghiêng xuống (ước lượng) — giữ từ DD 01/11 vì rủi ro tín dụng 6.016 tỷ + cho thuê chậm (28,6 ha 2025 vs KH 45)"


def scen_vals(r, **over):
    out = {}
    for k_, s in SCEN.items():
        a = {kk: vv for kk, vv in s.items() if kk not in ("w", "note")}
        a.update(over)
        out[k_] = value(r, **a)[0]
    return out


def expected(r, **over):
    v = scen_vals(r, **over)
    return sum(SCEN[k_]["w"] * v[k_] for k_ in SCEN)


r0 = R["r"]
sv = scen_vals(r0)
E_pre = expected(r0)
disc = L["ref_discount"]
E_post = E_pre * (1 - disc)

# LƯỚI: 3 kịch bản (trọng số kịch bản) × tỷ/ha toàn phần ×{0,75;1;1,25} × g core {−1;0;+1}pp (đều) ⇒ n=27
grid_vals, grid_w = [], []
for k_, s in SCEN.items():
    for m in (0.75, 1.0, 1.25):
        for dg in (-0.01, 0.0, 0.01):
            a = {kk: vv for kk, vv in s.items() if kk not in ("w", "note")}
            a["perha"] *= m
            a["gcore"] += dg
            grid_vals.append(value(r0, **a)[0]); grid_w.append(s["w"] / 9)
P_pre = g.wpct(grid_vals, grid_w)
P_post = {k_: v * (1 - disc) for k_, v in P_pre.items()}

sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = expected(rr) * (1 - disc)
    sens_r[key] = dict(r=rr, post=e, pct=e / E_post - 1)

warn_gov = expected(r0, gov_disc=0.10) * (1 - disc)
adv_loss = (expected(r0) - 635.6 / SH * 1000 * (1 - 0)) * (1 - disc)   # mất trọn tạm ứng 635,6 cho người quản lý
sens = dict(
    credit_loss_base={f"{c:.0%}": value(r0, **{**{kk: vv for kk, vv in SCEN['co_so'].items() if kk not in ('w', 'note')}, 'credit_loss': c})[0] for c in (0, .1, .3, .5)},
    perha_base={str(h): value(r0, **{**{kk: vv for kk, vv in SCEN['co_so'].items() if kk not in ('w', 'note')}, 'perha': h})[0] for h in (4, 8, 12, 16, 20)},
    recover_base={f"{x:.0%}": value(r0, **{**{kk: vv for kk, vv in SCEN['co_so'].items() if kk not in ('w', 'note')}, 'recover': x})[0] for x in (0.3, 0.6, 1.0)},
    warning_gov10_post=warn_gov, warning_adv6356_post=adv_loss,
)
base_detail = value(r0, **{kk: vv for kk, vv in SCEN["co_so"].items() if kk not in ("w", "note")})[1]

OLD = dict(low=42000, center=47700, high=55000, dd_date="2026-11-01")
out = dict(ticker="SIP", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L,
           scen_values_pre=sv, scen_weights={k_: s["w"] for k_, s in SCEN.items()}, scen_w_basis=SCEN_W_BASIS,
           center_pre_liq=E_pre, center_post_liq=E_post, P_pre=P_pre, P_post=P_post, grid_n=len(grid_vals),
           base_detail=base_detail, sens_r=sens_r, sens=sens,
           eps_bctc_ttm=4972 - 3838 + 4050, pe_ttm_bctc=PX / (4972 - 3838 + 4050),
           label=g.label(PX, P_post["p10"], P_post["p90"]),
           px_vs_center=PX / E_post - 1, px_vs_p10=PX / P_post["p10"] - 1, px_vs_p90=PX / P_post["p90"] - 1,
           zone_old=OLD, center_vs_old=E_post / OLD["center"] - 1)
json.dump(out, open(os.path.join(HERE, "model_sip_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
lines = [f"SIP giá {f(PX)} ({PX_DATE}) | r {r0:.4f} (neo {R['anchor']['rate']}% {R['anchor']['date']}; nay {R['current']['rate']}% {R['current']['source']})",
         f"Kịch bản trước CK thanh khoản: " + " | ".join(f"{k_} {f(v)} (w {SCEN[k_]['w']})" for k_, v in sv.items()),
         f"PE core cơ sở {base_detail['pe']:.2f}x | core {base_detail['core']:,.0f} fin {base_detail['fin']:,.0f} land {base_detail['land']:,.0f} sunk {base_detail['sunk']:,.0f} taxdef {base_detail['taxdef']:,.0f}",
         f"Tâm TRƯỚC CK {f(E_pre)} | CK thanh khoản {disc:.2%} @5 tỷ (ADV120 trung vị {L['adv120_med_ty']:.2f} tỷ; 10%/20% ADV: {L['sizes'][1]['days_p10']:.1f}/{L['sizes'][1]['days_p20']:.1f} phiên) | Tâm SAU {f(E_post)}",
         f"Lưới n={len(grid_vals)} TRƯỚC " + " ".join(f"{k_} {f(v)}" for k_, v in P_pre.items()),
         f"Lưới SAU " + " ".join(f"{k_} {f(v)}" for k_, v in P_post.items()),
         f"Giá so tâm {PX/E_post-1:+.1%} | so P10 {PX/P_post['p10']-1:+.1%} | so P90 {PX/P_post['p90']-1:+.1%} ⇒ {out['label']}",
         "Độ nhạy r (SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"Độ nhạy cơ sở (trước CK): tín dụng {json.dumps({k_: round(v) for k_, v in sens['credit_loss_base'].items()})} ; tỷ/ha {json.dumps({k_: round(v) for k_, v in sens['perha_base'].items()})} ; thu hồi {json.dumps({k_: round(v) for k_, v in sens['recover_base'].items()})}",
         f"WARNING (không vào tâm): CK quản trị 10% ⇒ {f(warn_gov)} ; mất trọn tạm ứng 635,6 tỷ ⇒ {f(adv_loss)}",
         f"Cũ (01/11): vùng {f(OLD['low'])}–{f(OLD['high'])} tâm {f(OLD['center'])} ⇒ tâm mới/cũ {E_post/OLD['center']-1:+.1%}"]
open(os.path.join(HERE, "model_sip_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
