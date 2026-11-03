"""DD SCL r2 (03/11/2026) — mô hình MÙ GIÁ: KHÔNG có giá/vốn hoá/P-E của SCL trong file này.
Chạy: python3 -I model_r2.py  → model_r2_out.json/.txt ; khoá md5 (LOCK_md5_r2.txt) TRƯỚC khi đọc giá/ADV.

Khung (luật user 03/11): (a) dự án mới = giá vốn/NPV 0; (b) chu kỳ tài sản hiện hữu chuẩn hoá theo dữ liệu
nhiều năm + phân loại ngành độc lập (CYCLICAL .50 / ADMIN_GATED .30 / STRUCTURAL .20, sector read VLXD nhẹ
29/10); (c) r = 13,5% tại lãi huy động 12T 7,40% (cctg_12m 02/11/2026), r = 13,5% + β(lãi − 7,40%), β=1;
(d) quyền mua 100:15,4453 @12.500 (6,0tr CP, 75 tỷ trả nợ) — giá trị/cp trước & sau quyền.
Phương pháp: giá trị VCSH hoạt động hiện hữu = E_chuẩn hoá × (1 − g/ROE) / (r − g) (P/E nội tại, value-driver);
cộng dự án dở dang theo giá vốn và trừ nợ tài trợ nó (đã chi bằng vay ⇒ ròng 0), đồng thời bỏ lãi vay của khoản
nợ đó khỏi E (không vừa trừ trong nợ vừa trừ qua lãi vay = coi là mất).
"""
import itertools, json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
B = 1e9

# ---- Sự kiện [BCTC HN Q3/2026, ký 15/10/2026; tav2_bq.ticker_financial (không cột giá)] ----
SH_NOW = 38_836_815            # vốn góp 388.368.150.000 / 10.000
SH_NEW = 6_000_000             # NQ1363 / TB1368
SUB_PX = 12_500
RATIO = 0.154453
SH_POST = SH_NOW + SH_NEW
PROCEEDS = SH_NEW * SUB_PX / B  # 75,0 tỷ, mục đích: trả vay BIDV + nợ thuê TC
EQ_PARENT = (533.637891337 - 2.021610292)      # VCSH 30/9 trừ lợi ích CĐKKS
DEBT = 259.737284295 + 156.724386878           # vay + thuê TC NH + DH
INT_Q3 = 5.167026739                           # chi phí đi vay Q3/2026 (KQKD mã 24)
TAX = 9.551650988 / 47.656565350               # thuế TNDN Q3 / LNTT Q3 = 20,0%
# Dự án mới (XDCB dở dang 30/9, REPORT.md §4, đối chiếu thuyết minh HN-Q3):
CIP = {"Phả Lại (nhà máy/dây chuyền, tổng vốn 262,9 tỷ)": 178.0 + 12.7,
       "Tách tro Vĩnh Hảo GĐ2": 14.8}
CIP_TOTAL = sum(CIP.values())                  # 205,5 tỷ đã chi
PHALAI_TOTAL = 262.9
PHALAI_REMAIN = PHALAI_TOTAL - CIP[list(CIP)[0]]   # ~72,2 tỷ còn phải chi (ước lượng) ⇒ NPV 0

# Lịch sử năm (tỷ đ, DT GỘP BQ Revenue_P0, LNST cổ đông mẹ NP_P0) — fin_bq_scl.csv
HIST = {2020: (307.05, 24.85), 2021: (310.89, 20.40), 2022: (338.74, 15.78),
        2023: (473.47, 45.27), 2024: (427.73, 26.57), 2025: (618.58, 64.30)}
TTM = (219.74 + 705.18, 23.35 + 94.37)         # Q4/25 + 9T/26
E2026 = (705.18 + 277.94, 94.37 + 38.09)        # 9T + Q4 giả định = Q3 (ước lượng)
# Biên gộp BQ GPM_P0 (định nghĩa BQ, nhất quán nội bộ) — trung bình 4 quý mỗi năm
GPM_BQ = {2023: st.mean([.4634, .4208, .3831, .3542]), 2024: st.mean([.3463, .3353, .3246, .3218]),
          2025: st.mean([.3326, .3382, .3597, .3533]), "TTM": st.mean([.3533, .3516, .3721, .3867])}

R0, DEP0 = 0.135, 0.0740
BRANCH_W = {"CYCLICAL": 0.50, "ADMIN_GATED": 0.30, "STRUCTURAL": 0.20}   # sector read 29/10 (đọc mù)
REVERT = {"CYCLICAL": 1.0, "ADMIN_GATED": 0.5, "STRUCTURAL": 0.0}         # mức quay về trung bình chu kỳ


def npm(rev, np_):
    return np_ / rev


NPM_TTM = npm(*TTM)
NPM_MEAN = {"2020-TTM": st.mean([npm(*HIST[y]) for y in range(2020, 2026)] + [NPM_TTM]),
            "2023-TTM": st.mean([npm(*HIST[y]) for y in range(2023, 2026)] + [NPM_TTM])}
# phương pháp lệch biên gộp: biên gộp TTM cao hơn TB 2023–TTM bao nhiêu ⇒ trừ phần đó (sau thuế) khỏi biên ròng
GM_GAP = GPM_BQ["TTM"] - st.mean([GPM_BQ[k] for k in (2023, 2024, 2025, "TTM")])
NPM_MEAN["GM-gap"] = NPM_TTM - GM_GAP * (1 - TAX)

GRID = dict(rev=["TTM", "2026E"], norm=list(NPM_MEAN), g=[0.03, 0.04, 0.05], roe=[0.15, 0.20],
            i_cip=[INT_Q3 * 4 / DEBT, 0.095])


def value(branch, rev, norm, g, roe, i_cip, r):
    rv = TTM[0] if rev == "TTM" else E2026[0]
    m_now = NPM_TTM if rev == "TTM" else npm(*E2026)
    m = m_now - REVERT[branch] * (m_now - NPM_MEAN[norm])
    e_exist = rv * m + CIP_TOTAL * i_cip * (1 - TAX)       # bỏ lãi vay của nợ tài trợ dự án dở dang
    mult = (1 - g / roe) / (r - g)
    v_ops = e_exist * mult
    v_total = v_ops + CIP_TOTAL - CIP_TOTAL                # dự án: giá vốn − nợ tài trợ (đã chi bằng vay) = 0 ròng
    return dict(e_exist=e_exist, mult=mult, v_total_pre=v_total,
                v_cum=v_total * B / SH_NOW, v_post=(v_total + PROCEEDS) * B / SH_POST)


def run(r):
    rows = []
    for br, w in BRANCH_W.items():
        combos = list(itertools.product(*GRID.values()))
        for c in combos:
            kw = dict(zip(GRID, c))
            v = value(br, r=r, **kw)
            rows.append(dict(branch=br, w=w / len(combos), **kw, **v))
    return rows


def wq(rows, key, q):
    s = sorted(rows, key=lambda x: x[key]); acc = 0; tot = sum(x["w"] for x in s)
    for x in s:
        acc += x["w"]
        if acc >= q * tot:
            return x[key]


def summary(rows):
    tot = sum(x["w"] for x in rows)
    out = {k: sum(x[k] * x["w"] for x in rows) / tot for k in ("v_cum", "v_post", "e_exist", "v_total_pre")}
    out["pct_post"] = {str(int(q * 100)): wq(rows, "v_post", q) for q in (.05, .10, .25, .50, .75, .90)}
    out["pct_cum"] = {str(int(q * 100)): wq(rows, "v_cum", q) for q in (.05, .10, .25, .50, .75, .90)}
    out["branch_post"] = {b: sum(x["v_post"] * x["w"] for x in rows if x["branch"] == b) /
                          sum(x["w"] for x in rows if x["branch"] == b) for b in BRANCH_W}
    out["branch_e"] = {b: sum(x["e_exist"] * x["w"] for x in rows if x["branch"] == b) /
                       sum(x["w"] for x in rows if x["branch"] == b) for b in BRANCH_W}
    return out


base = run(R0)
S = summary(base)
# độ nhạy lãi huy động (β=1 và β=0,5)
sens = {}
for beta in (1.0, 0.5):
    for bp in (-100, -50, 0, 50, 100):
        r = R0 + beta * bp / 1e4
        s = summary(run(r))
        sens[f"b{beta}_{bp:+d}"] = dict(r=r, v_post=s["v_post"], v_cum=s["v_cum"],
                                        d_pct=s["v_post"] / S["v_post"] - 1)
# độ nhạy IRR dự án Phả Lại (KHÔNG vào base: chưa có giá/sản lượng/hợp đồng đầu ra kiểm được)
irr_sens = {f"{irr:.3f}": PHALAI_TOTAL * (irr / R0 - 1) * B / SH_POST for irr in (0.10, 0.12, 0.135, 0.15, 0.17)}
# kiểm kê khoản cộng/trừ gắn dự án mới
inventory = [
    dict(item="Phả Lại — phần đã chi 190,7 tỷ (XDCB dở dang)", base="tài sản theo giá vốn; nợ vay tài trợ nó trừ đủ ở mệnh giá; bỏ lãi vay tương ứng khỏi E",
         basis="BCTC HN Q3/2026 thuyết minh XDCB; LCTT capex 9T 198,1 tỷ; CFO 9T 9,9 tỷ ⇒ tài trợ bằng vay"),
    dict(item="Phả Lại — phần còn phải chi ~72 tỷ (ước lượng)", base="NPV 0 (tài sản = nợ/vốn đối ứng)", basis="tổng vốn 262,9 tỷ − 190,7 tỷ"),
    dict(item="Tách tro Vĩnh Hảo GĐ2 14,8 tỷ", base="như Phả Lại (giá vốn, ròng 0, bỏ lãi vay)", basis="BCTC HN Q3/2026 XDCB"),
    dict(item="Phả Lại — lợi nhuận tăng thêm khi vận hành", base="KHÔNG cộng (không có giá/sản lượng/hợp đồng đầu ra kiểm được)", basis="chỉ độ nhạy IRR"),
    dict(item="Phả Lại — rủi ro thừa cung vùng", base="KHÔNG trừ (chỉ có nhận định ngành chung, không dữ liệu vùng)", basis="sector read: không có số công suất toàn quốc"),
    dict(item="Trả trước người bán 86,6 tỷ (một phần có thể là thiết bị)", base="không cộng thêm (đã nằm trong vốn lưu động, mục đích từng khoản không công bố đủ)", basis="BCTC HN Q3 V.3"),
]
# định lượng hiệu ứng khoản Phả Lại+Vĩnh Hảo so với cách cũ (dự án không được tính, lãi vay vẫn trừ)
eff = {}
for br in BRANCH_W:
    pass
cip_int_effect = sum(x["w"] * CIP_TOTAL * x["i_cip"] * (1 - TAX) * x["mult"] for x in base) / sum(x["w"] for x in base)
eff["cip_effect_total_ty"] = cip_int_effect
eff["cip_effect_post_dcp"] = cip_int_effect * B / SH_POST
eff["cip_effect_cum_dcp"] = cip_int_effect * B / SH_NOW

out = dict(asof="2026-11-03", r0=R0, dep0=DEP0, dep0_src="deposit_rate_vn.macro_killswitch_a_status(): cctg_12m(2026-11-02) 7,40%",
           tax=TAX, eq_parent=EQ_PARENT, bvps_cum=EQ_PARENT * B / SH_NOW, bvps_post=(EQ_PARENT + PROCEEDS) * B / SH_POST,
           debt=DEBT, cip_total=CIP_TOTAL, phalai_remain=PHALAI_REMAIN, int_q3_rate=INT_Q3 * 4 / DEBT,
           npm_ttm=NPM_TTM, npm_2026e=npm(*E2026), npm_mean=NPM_MEAN, gm_gap=GM_GAP, gpm_bq=GPM_BQ,
           hist_npm={y: npm(*HIST[y]) for y in HIST}, grid=GRID, n_grid=len(base),
           tam_post=S["v_post"], tam_cum=S["v_cum"], e_exist=S["e_exist"], v_total_pre=S["v_total_pre"],
           pct_post=S["pct_post"], pct_cum=S["pct_cum"], branch_post=S["branch_post"], branch_e=S["branch_e"],
           sens_rate=sens, irr_sens_post=irr_sens, inventory=inventory, cip_effect=eff,
           thresholds_preregistered=dict(
               rule="nhãn dựa trên giá trị SAU chiết khấu thanh khoản ở quy mô tham chiếu 1 tỷ đ",
               cheap_margin="giá ≤ P10 (sau CK thanh khoản) ⇒ RẺ có biên an toàn",
               below="P10 < giá < P25 ⇒ DƯỚI vùng hợp lý", inside="P25..P75 ⇒ TRONG vùng", above="> P75 ⇒ TRÊN vùng",
               compare="giá cum-quyền so với giá trị/cp TRƯỚC quyền; TERP so với giá trị/cp SAU quyền"),
           liquidity_method_preregistered=dict(
               exit_cost="nửa spread (Corwin-Schultz từ High/Low 120 phiên, tav2_bq.ticker) + tác động giá căn bậc hai Y·σ_ngày·√(Q/ADV_trung vị), Y∈{0,5;1,0}",
               days="số phiên thoát = Q/(p·ADV_trung vị), p∈{10%,20%}", cross_check="Amihud ILLIQ 120 phiên (|r|/giá trị GD) × Q, chỉ đối chiếu",
               discount="chiết khấu = chi phí thoát 1 chiều (Y=1, trung điểm) ở quy mô 1/5/10 tỷ đ; tham chiếu 1 tỷ"))
json.dump(out, open(os.path.join(HERE, "model_r2_out.json"), "w"), ensure_ascii=False, indent=1, default=str)
with open(os.path.join(HERE, "model_r2_out.txt"), "w") as f:
    f.write(f"tam_cum {S['v_cum']:.0f}  tam_post {S['v_post']:.0f}  E_exist {S['e_exist']:.1f} ty  V_pre {S['v_total_pre']:.1f} ty\n")
    f.write(f"pct_post {json.dumps({k: round(v) for k, v in S['pct_post'].items()})}\n")
    f.write(f"pct_cum {json.dumps({k: round(v) for k, v in S['pct_cum'].items()})}\n")
    f.write(f"branch_post {json.dumps({k: round(v) for k, v in S['branch_post'].items()})}  branch_E {json.dumps({k: round(v,1) for k, v in S['branch_e'].items()})}\n")
    f.write(f"npm_ttm {NPM_TTM:.4f} npm_mean {json.dumps({k: round(v,4) for k,v in NPM_MEAN.items()})} gm_gap {GM_GAP:.4f} tax {TAX:.4f} i_q3 {INT_Q3*4/DEBT:.4f}\n")
    f.write(f"cip_effect post {eff['cip_effect_post_dcp']:.0f} cum {eff['cip_effect_cum_dcp']:.0f} total {eff['cip_effect_total_ty']:.1f} ty\n")
    for k, v in sens.items():
        f.write(f"sens {k}: r {v['r']:.4f} post {v['v_post']:.0f} ({v['d_pct']*100:+.1f}%)\n")
    f.write(f"irr_sens_post {json.dumps({k: round(v) for k, v in irr_sens.items()})}\n")
print(open(os.path.join(HERE, "model_r2_out.txt")).read())
