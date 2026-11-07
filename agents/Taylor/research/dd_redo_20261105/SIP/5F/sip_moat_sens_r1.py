"""SIP bước 3c — độ nhạy moat (07/11/2026, job Taylor_20261107_130211).
Exec NGUYÊN phần khai báo calc/model_sip_r2.py (tới trước build_grid), tái lập tâm 54.230, rồi đổi 3 kênh moat:
 (R) RONIC mảng vận hành: hiện hành = ROE5Y 29,7%; chặt-3c = Ke (= r của TỪNG ô, đối xứng mọi g, mọi r trong độ nhạy).
 (M) biên: GPM TTM Q4/25–Q3/26 vs TB GPM năm 2019–25 của chính SIP (BQ GPM_P0 dòng Q4 = GPM cả năm; Revenue_P0 = quý).
 (H) thời hạn: vĩnh viễn (hiện hành) vs annuity N năm (NONE).
Quy ước năm 1 giữ như model: E năm 1 = E hiện hành × payout, không nhân (1+g).
"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "calc", "model_sip_r2.py")
src = open(SRC).read().split("outs = g.build_grid(AXES, fn)")[0]
ns = {"__file__": SRC, "__name__": "sipmodel"}
exec(compile(src, SRC, "exec"), ns)
g = ns["g"]; AXES = ns["AXES"]; PX = ns["PX"]; disc = ns["disc"]; L = ns["L"]; r0 = ns["r0"]

# --- GPM SIP từ BQ (cùng file peer của SZL 5F, truy vấn 07/11/2026) ---
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "..", "..", "SZL", "5F", "bq_fin_peers_20261107.csv"))) if r["ticker"] == "SIP"]
gq4 = {r["quarter"][:4]: float(r["gpm"]) for r in rows if r["quarter"].endswith("Q4") and r["gpm"]}
cyc_years = [str(y) for y in range(2019, 2026)]
gpm_cyc = sum(gq4[y] for y in cyc_years) / len(cyc_years)
last = {r["quarter"]: r for r in rows}
gpm_ttm = float(last["2026Q3"]["gpm"])
rev_ttm = sum(float(last[q]["rev"]) for q in ("2025Q4", "2026Q1", "2026Q2", "2026Q3")) / 1e9
dgp = (gpm_ttm - gpm_cyc) * rev_ttm            # tỷ/năm, LN gộp vượt TB chu kỳ
gp_core_y = (sum(ns["gp"].values()) - ns["gp"]["land"]) * ns["k"]

def value(r, gcore, perha, yrs, credit_loss, nci_sub, recover, taxdef_mult, ktpl, adv_loss=0.0,
          ronic=None, margin_cyc=False, horizon=None):
    ro = r if ronic == "ke" else (ns["ROE5Y"] if ronic is None else ronic)
    pay = 1 - gcore / ro
    pe = pay / (r - gcore) if horizon is None else pay * (1 - ((1 + gcore) / (1 + r)) ** horizon) / (r - gcore)
    ops = ns["core_ops_pt"] - (max(dgp, 0.0) if margin_cyc else 0.0)   # chỉ hạ khi TTM > TB (không nâng)
    core = (ops * (1 - ns["TAX"]) + ns["assoc"] * ns["k"]) * (1 - ns["nci_profit"]) * (1 - ktpl) * pe
    fin = ns["parent_net"] + ns["subs_net"] * (1 - nci_sub) - ns["ktpl_fund"]
    loss = credit_loss * (ns["loans_unsec"] + ns["bonds_unsec_ex_vhm"])
    taxdef = ns["pv_even"](ns["deferred_rev"] * 0.69 * ns["TAX"], 35, r) * taxdef_mult
    land = ns["pv_even"](ns["LAND_HA"] * perha, yrs, r) * (1 - ns["nci_profit"]) * (1 - ktpl)
    sunk = ns["pv_even"](ns["spent_land"] * recover, yrs, r) * (1 - ns["nci_profit"])
    return (core + fin - loss - taxdef + land + sunk - adv_loss) / ns["SH"] * 1000

def mk(**mo):
    def fn(land, perha_mult, gcore, credit, nci, recover, taxdef, ktpl, r=None):
        perha, yrs = land
        return value(r0 if r is None else r, gcore, perha * perha_mult, yrs, credit, nci, recover, taxdef, ktpl, **mo)
    return fn

sl_key = list(L["sleeve_discount"].keys())[-1]; sl_disc = L["sleeve_discount"][sl_key]
VARS = [
    ("WIDE_ROE5Y_hien_hanh", dict()),
    ("WIDE_ROIC5Y", dict(ronic=float(last["2026Q3"]["ROIC5Y"]))),
    ("chi_R_RONIC_Ke", dict(ronic="ke")),
    ("chi_M_bien_TB_chu_ky", dict(margin_cyc=True)),
    ("CHAT_3C_NARROW", dict(ronic="ke", margin_cyc=True)),
    ("NONE_chat_3c_30nam", dict(ronic="ke", margin_cyc=True, horizon=30)),
]
res = {}
for name, mo in VARS:
    outs = g.build_grid(AXES, mk(**mo))
    D = g.dist(outs, PX, disc); Ds = g.dist(outs, PX, sl_disc)
    res[name] = dict(center_pre=D["center_pre"], center=D["center_post"], p10=D["P_post"]["p10"], p50=D["P_post"]["p50"],
                     p90=D["P_post"]["p90"], below=D["pct_w_below_px"], label=g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"]),
                     sleeve=dict(key=sl_key, disc=sl_disc, center=Ds["center_post"], p10=Ds["P_post"]["p10"], p90=Ds["P_post"]["p90"],
                                 label=g.label(PX, Ds["P_post"]["p10"], Ds["P_post"]["p90"])))
# độ nhạy r của bản chặt (RONIC=Ke theo r từng ô — đối xứng)
sens = {}
for key, rr in g.r_grid(r0).items():
    if key.startswith("b1.0"):
        sens[key] = g.dist(g.build_grid(AXES, lambda **kw: mk(ronic="ke", margin_cyc=True)(r=rr, **kw)), PX, disc)["center_post"]
pe_now = (1 - 0.03 / ns["ROE5Y"]) / (r0 - 0.03); pe_ke = (1 - 0.03 / r0) / (r0 - 0.03)
out = dict(price=PX, r=r0, gpm_q4_by_year=gq4, gpm_cyc_2019_25=gpm_cyc, gpm_ttm_2026Q3=gpm_ttm, rev_ttm_ty=rev_ttm,
           dgp_ty=dgp, gp_core_y_ty=gp_core_y, dgp_pct_of_core_gp=dgp / gp_core_y, pe_core_g3=dict(ronic_roe5y=pe_now, ronic_ke=pe_ke),
           variants=res, sens_r_chat=sens)
json.dump(out, open(os.path.join(HERE, "sip_moat_sens_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt
lines = [f"GPM SIP Q4(=năm) {', '.join(f'{y}:{v:.4f}' for y, v in sorted(gq4.items()))} | TB 2019-25 {gpm_cyc:.4f} | TTM Q3/26 {gpm_ttm:.4f}",
         f"DT TTM {rev_ttm:.1f} tỷ | ΔLN gộp vượt TB {dgp:.1f} tỷ/năm = {dgp/gp_core_y:.1%} LN gộp lõi (ex-đất) {gp_core_y:.1f}",
         f"PE lõi g3%: RONIC ROE5Y {pe_now:.3f} | RONIC=Ke {pe_ke:.3f} ({pe_ke/pe_now-1:+.1%})"]
for n, v in res.items():
    s = v["sleeve"]
    lines.append(f"{n}: tâm {f(v['center'])} P10 {f(v['p10'])} P50 {f(v['p50'])} P90 {f(v['p90'])} dưới giá {v['below']:.1%} nhãn {v['label']} | sleeve {s['key']} tâm {f(s['center'])} P10 {f(s['p10'])} P90 {f(s['p90'])} {s['label']}")
lines.append("Độ nhạy r chặt-3c: " + " | ".join(f"{k} {f(v)}" for k, v in sens.items()))
open(os.path.join(HERE, "sip_moat_sens_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
