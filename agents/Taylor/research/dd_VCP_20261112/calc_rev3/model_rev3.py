#!/usr/bin/env python3
"""VCP DD rev3 — model mu gia. Doc assumptions_rev3.json, in JSON ket qua (ty dong, d/cp).
Chay: python3 model_rev3.py > model_out_rev3.json  (threads=1, khong dung du lieu gia)."""
import json, math, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "assumptions_rev3.json")))
S = A["shares_m"]
r, g = A["discount_rate"]["r"], A["discount_rate"]["g"]
B25, B_now = A["book"]["B_parent_2025end"], A["book"]["B_parent_after_div_20260930"]
dB = A["projects_npv0"]["delta_B"]
assert abs((B_now - B25) - dB) < 0.05
H = A["hydro"]
mc = H["marginal_cost_ratio"]


def ps(v):  # ty dong -> d/cp
    return v / S * 1000


plants = H["plants"]
etb = sum(p["etb"] for p in plants)
act = sum(p["actual_2025"] for p in plants)
ratio25 = act / etb
hist = [H["ratio_history"]["2023"], H["ratio_history"]["2024"], ratio25]
k = statistics.mean(hist)


def parent_profit(dv_mkwh, p):
    return dv_mkwh * p["rev_per_kwh"] / 1000 * (1 - mc) * (1 - p["tax"]) * p["own"]


def hydro_excess(kk):
    return sum(parent_profit(p["actual_2025"] - p["etb"] * kk, p) for p in plants)


exc = hydro_excess(k)
tf = (1 - A["tax_step"]["eff_plan_2026"]) / (1 - A["tax_step"]["eff_2025"])
wf = 1 - A["welfare_fund"]["pct_of_npat"]
N25 = A["N_2025_parent"]


def core(N, rr=r):
    return N / rr  # RONIC = Ke terminal (D4)


N_base = (N25 - exc) * tf * wf
N_bull = (700.8 - 74.9 - 57.8) * tf * wf
# El Nino: 2 nam o muc ty le 2023, so voi binh thuong k
en = A["el_nino"]
short = sum(parent_profit(p["etb"] * (k - en["ratio"]), p) for p in plants) * tf


def pv_ann(x, n, rr=r):
    return sum(x / (1 + rr) ** t for t in range(1, n + 1))


def scen(rr=r, Nb=None, Nu=None, loss=A["loan_loss_bear"], kk=None):
    Nb = N_base if Nb is None else Nb
    Nu = N_bull if Nu is None else Nu
    base = core(Nb, rr) + dB
    bull = core(Nu, rr) + dB
    bear = base - pv_ann(short, en["years"], rr) - loss
    return {"bear": bear, "base": base, "bull": bull}


W = A["scenarios"]["weights"]


def center(sc, w=W):
    return sum(w[s] * sc[s] for s in w)


sc = scen()
out = {
    "k_hist": [round(x, 4) for x in hist], "k": round(k, 4), "ratio_2025": round(ratio25, 4),
    "etb_hydro": round(etb, 2), "actual_hydro_2025": round(act, 2),
    "hydro_excess_parent_2025": round(exc, 1),
    "hydro_excess_if_k1": round(hydro_excess(1.0), 1),
    "tax_factor": round(tf, 4), "welfare_factor": round(wf, 4),
    "N_base": round(N_base, 1), "N_bull": round(N_bull, 1),
    "el_nino_short_per_year": round(short, 1), "el_nino_pv": round(pv_ann(short, 2), 1),
    "value_bn": {s: round(v, 1) for s, v in sc.items()},
    "value_ps": {s: round(ps(v)) for s, v in sc.items()},
    "center_ps": round(ps(center(sc))),
}
C = center(sc)
sens = {}
dep0 = A["discount_rate"]["deposit_12m"]
for beta in (1.0, 0.5):
    for bp in (-100, -50, 50, 100):
        rr = r + beta * bp / 10000
        sens[f"dep{bp:+d}bp_beta{beta}"] = round(ps(center(scen(rr))))
for ke in (0.123, 0.134):
    sens[f"Ke_{ke}"] = round(ps(center(scen(ke))))
# k = 1 (Etb thiet ke) va khong chuan hoa
Nb_k1 = (N25 - hydro_excess(1.0)) * tf * wf
sens["k1_design_etb"] = round(ps(center(scen(Nb=Nb_k1))))
sens["no_hydro_norm"] = round(ps(center(scen(Nb=N25 * tf * wf))))
# thue dai han 20% (ngay het uu dai khong kiem chung): buoc nhay tu nam T
f20 = (1 - 0.20) / (1 - A["tax_step"]["eff_plan_2026"])
for T in (0, 5, 10):
    hair = (1 - f20) * (1 / (1 + r)) ** T  # ty le mat gia tri phan core
    s2 = {k_: (v - dB) * (1 - hair) + dB for k_, v in sc.items()}
    sens[f"tax20_from_y{T}"] = round(ps(center(s2)))
# Cua Dat Pc giam 20% (uoc luong) tu nam T — tai dam phan PPA sau tra no (khong kiem chung)
cd = plants[0]
cd_rev_norm = cd["etb"] * k * cd["rev_per_kwh"] / 1000
cd_loss = cd_rev_norm * 0.20 * (1 - cd["tax"]) * tf * wf
for T in (0, 5):
    sens[f"cuadat_pc_minus20_from_y{T}"] = round(ps(C - cd_loss / r / (1 + r) ** T))
# NSX nhuong quyen het sau 20 nam (uoc luong): mat phan sau nam 20 cua LNST NSX 174,2 x 99,55%
nsx = 174.15 * 0.9955 * wf
sens["nsx_concession_20y"] = round(ps(C - nsx / r / (1 + r) ** 20))
# lai don tich chua thu 2025 tru khoi base
acc = (A["accrued_interest"]["fin_income_2025"] - A["accrued_interest"]["cash_interest_2025"]) * (1 - 0.20)
sens["base_minus_accrued_interest"] = round(ps(center(scen(Nb=N_base - acc * tf * wf))))
sens["accrued_interest_after_tax"] = round(acc, 1)
# trong so
for nm, w in {"w35_45_20": {"bear": .35, "base": .45, "bull": .20}, "w40_40_20": {"bear": .40, "base": .40, "bull": .20},
              "w25_45_30": {"bear": .25, "base": .45, "bull": .30}}.items():
    sens[nm] = round(ps(center(sc, w)))
# loan loss 0 / 100%
sens["loanloss0"] = round(ps(center(scen(loss=0))))
sens["loanloss100"] = round(ps(center(scen(loss=803.7))))
# ROE ngam thuong (cong thuc rev2: RONIC = ROE, B0 = B_now) — chi hien thi
roe_b = N_base / B25
sens["ronic_eq_roe_display"] = round(ps(center({"bear": sc["bear"], "base": B25 + (N_base - r * B25) / (r - g) + dB,
                                                  "bull": B25 + (N_bull - r * B25) / (r - g) + dB})))
sens["roe_base_on_B2025"] = round(roe_b, 4)
out["sens"] = sens
# V6 hai nen (chi hien thi) — giu dau vao rev2
fcfe = 301.3
roe_s = 0.16
vs = 411.8 * (1 - min(max(g / roe_s, 0), 0.8)) / (r - g)
vl = fcfe / (r - g)
out["v6"] = {"V_short": round(ps(vs)), "V_long": round(ps(vl)), "D": round(abs(math.log(vs / vl)), 3)}
print(json.dumps(out, ensure_ascii=False, indent=1))
