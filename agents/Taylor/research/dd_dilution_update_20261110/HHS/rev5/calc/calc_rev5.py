"""HHS rev5 (23/11/2026) — biến đổi pha loãng trên phân phối r3 (mù giá). KHÔNG đọc giá thị trường.
Sửa so với r4 theo skeptic r1: (1) c<1: HHS vẫn bơm đủ 2.591,9 tỷ vào NĐL, phần thiếu vay (nợ ghi theo mệnh giá)
=> ΔVCSH = k*CASH - (1-c)*CASH (r4 dùng k*c*CASH); (2) bỏ k=0,946, thay bằng mô hình tường minh bên khác mua NĐL;
(3) NĐL lợi ích trước = 51,14% (BCTC Q3 TM1.5) thay 51,01%; (4) độ nhạy gọi vốn thêm cho I.14; (5) V_ngắn (V6)."""
import json, os, statistics, hashlib
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(f"{H}/assumptions.json"))
SRC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_dilution_update_20261110/calc/dilution_out.json"
assert hashlib.md5(open(SRC, 'rb').read()).hexdigest() == "0450ba0aee972c6c4ec97847fe2de68c"
D = json.load(open(SRC))["HHS"]
d5 = D["inputs"]["d5"]
N0, NR, OFF, DIV = 431_985_968, 259_191_580, 10_000, 0.07
CASH = NR * OFF
TCH = A["tch_stake_hhs"]
Q = ("center", "p10", "p50", "p90")
pre = {"HEADLINE_CK0": D["HEADLINE_CKholding0"]["pre"], "SONGSONG_CK27": D["song_song_CKholding_r2_27pct"]["pre"]}
K_PAR = 0.73   # bản song song: tiền vào công ty con chịu cùng CK holding (giữ quy ước r4)

def ex(V, c, k, div=DIV, extra_debt=0.0):
    """giá trị / cp cuối. c: tỷ lệ bao phủ; HHS bơm đủ CASH, vay (1-c)*CASH."""
    dE = (k * CASH - (1 - c) * CASH - extra_debt) if c > 0 else 0.0   # c=0: không phát hành ⇒ không bơm
    return (V * N0 + (1 - d5) * dE) / (N0 + c * NR) / (1 + div)

def ex_r4(V, c, k):  # công thức r4 (để đối chiếu)
    return (V * N0 + (1 - d5) * k * c * CASH) / (N0 + c * NR) / (1 + DIV)

out = {"inputs": dict(N0=N0, NR=NR, cash=CASH, div=DIV, d5=d5, tch=TCH), "pre": pre}
# control: tái lập r4 dòng EX đủ k=1 = 11.615
ctl = round(ex_r4(pre["HEADLINE_CK0"]["center"], 1.0, 1.0)); assert ctl == 11615, ctl
assert round(ex(pre["HEADLINE_CK0"]["center"], 1.0, 1.0)) == 11615
out["control_r4_ex_full_k1"] = ctl

# --- NĐL: k tường minh ---
nd = A["ndl"]; sh0 = nd["charter_bn"] * 1e9 / 10_000; eq0 = sh0 * nd["bv_per_share"]; own0 = nd["hhs_econ_pre"] * sh0
def k_from_others(x_other):
    tot = sh0 + 260e6 + x_other; own = (own0 + 260e6) / tot
    gain = own * (eq0 + (260e6 + x_other) * 10_000) - (nd["hhs_econ_pre"] * eq0 + 2.6e12)
    return own, gain, 1 + gain / 2.6e12
own_only, g_only, k_only = k_from_others(0.0)
x7541 = (own0 + 260e6) / 0.7541 - sh0 - 260e6
own_c, g_c, k_c = k_from_others(x7541)
out["ndl"] = dict(sh0=round(sh0), eq0_bn=round(eq0/1e9, 1),
    only_hhs=dict(own=round(own_only, 4), gain_bn=round(g_only/1e9, 1), k=round(k_only, 4)),
    company_7541=dict(others_new_sh_m=round(x7541/1e6, 2), gain_bn=round(g_c/1e9, 1), k=round(k_c, 4)),
    note="Mọi cách đọc cho k>=1 vì giá phát hành 10.000 < BV 11.210 (BV tự lập, không kiểm toán ⇒ phần k>1 chỉ là độ nhạy lên)")

# --- bảng kịch bản ---
rows = {}
for lab, V in pre.items():
    kb = 1.0 if lab.startswith("HEAD") else K_PAR
    for c_lab, c in (("khong_phat_hanh", 0.0), ("chi_TCH", TCH), ("bao_phu_50", 0.5), ("du_100", 1.0)):
        ks = [kb] if lab.startswith("SONG") else [1.0, 0.8, round(k_c, 4), round(k_only, 4)]
        for k in ks:
            if c == 0 and k != kb: continue
            r = {q: round(ex(V[q], c, k)) for q in Q}
            r["rule4_thr"] = round(0.85 * r["center"])
            r["cum_exerciser"] = round((1.6 * 1.07 * ex(V["center"], c, k) - 0.6 * OFF) if c > 0 else 1.07 * ex(V["center"], c, k))
            r["r4_formula_center"] = round(ex_r4(V["center"], c, k)) if c > 0 else round(V["center"] / 1.07)
            rows[f"{lab}|{c_lab}|k={k}"] = r
out["rows"] = rows
H0 = pre["HEADLINE_CK0"]
out["undercount_tch_only_k08_bn"] = round((1 - 0.8) * (1 - TCH) * CASH / 1e9, 1)
# điểm hoà vốn k cho P10_EX >= tâm r4 ... (không dùng giá) — bỏ.

# --- độ nhạy gọi vốn thêm I.14 (SCENARIO_ONLY) ---
gap = 1803.2e9
share_hhs = own_only
C2 = gap * share_hhs
V_ex = ex(H0["center"], 1.0, 1.0); N_ex = (N0 + NR) * 1.07
for p_off in (10_000,):
    n2 = C2 / p_off
    v2 = (V_ex * N_ex + (1 - d5) * C2) / (N_ex + n2)
    out["extra_call_I14"] = dict(gap_bn=1803.2, hhs_part_bn=round(C2/1e9, 1), offer=p_off, new_sh_m=round(n2/1e6, 1),
        ex_center_after=round(v2), delta_pct=round(v2 / V_ex - 1, 4),
        exerciser_wealth_change="0 với k=1 (NPV0) — chỉ giảm giá trị/cp, người thực hiện quyền không mất",
        debt_route="vay tại NĐL theo lãi thị trường = NPV0 ⇒ base không đổi")
# chênh lãi vay phần thiếu (kịch bản chỉ TCH): 2pp x 3 năm (ước lượng)
sp = 0.02 * 3 * (1 - TCH) * CASH
out["shortfall_spread_cost"] = dict(bn=round(sp/1e9, 1), per_share_ex=round(-(1 - d5) * sp / (N0 + TCH * NR) / 1.07))

# --- V6: V_ngắn (nền lợi nhuận), g=0 ---
np_q = {"2022Q4":71.92,"2023Q1":70.03,"2023Q2":63.69,"2023Q3":49.22,"2023Q4":165.17,"2024Q1":149.80,"2024Q2":107.67,
        "2024Q3":41.37,"2024Q4":68.35,"2025Q1":67.40,"2025Q2":None,"2025Q3":17.25,"2025Q4":-38.51,"2026Q1":40.17,"2026Q2":25.34,"2026Q3":115.76,
        "2022Q1":71.99,"2022Q2":40.32,"2022Q3":37.77}
ks_ = sorted(np_q); vals = [np_q[k] for k in ks_]
ttm = []
for i in range(3, len(ks_)):
    w = vals[i-3:i+1]
    if None in w: w = [x for x in w if x is not None]; w = w + [statistics.mean(w)]   # 2025Q2 một lần: thay bằng TB 3 quý còn lại
    ttm.append((ks_[i], sum(w)))
last12 = [v for k, v in ttm if k >= "2023Q4"][-12:]
np_norm = statistics.median(last12) * 1e9
out["V6"] = dict(np_ttm_median_3y_bn=round(np_norm/1e9, 1), r=0.135, g=0.0,
    v_short=round(np_norm / 0.135 / N0), v_short_ex=round(np_norm / 0.135 / ((N0 + NR) * 1.07)),
    v_long="không tính: CFO 9T/2026 âm (BQ CF_OA 2026Q1-Q3 = -679,5/-1.170,6/-72,2 tỷ; LCTT HN mã 20 = -2.110,2 tỷ) ⇒ FCFE<=0, chỉ V_ngắn",
    D="không áp (thiếu V_dài)", note="NP_P0 BQ (LN sau thuế); 2025Q2 3.507 tỷ loại (lãi hợp nhất CRV)")
json.dump(out, open(f"{H}/calc_rev5_out.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
