"""Cập nhật pha loãng HHS (quyền mua 60% @10.000 + cổ tức CP 7%) và SCL (quyền 15,4453% @12.500, GDKHQ 09/11).
Không định giá lại doanh nghiệp: dùng nguyên phân phối r3 (định giá mù giá), chỉ biến đổi theo số cp + tiền thu.
Phép biến đổi V -> (V*N0 + (1-d)*k*c*Cash)/(N0 + c*Nr)/(1+div) là tuyến tính tăng theo V => tâm (kỳ vọng) và phân vị
có trọng số biến đổi CHÍNH XÁC (không cần chạy lại lưới).
d = CK thanh khoản của r3 áp lên cả phần tiền (CK áp trên cổ phiếu, bất kể tài sản gì đứng sau)."""
import json, os
OUT = os.path.dirname(os.path.abspath(__file__))
R = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_redo_20261105"

# ---------------- HHS ----------------
hs = json.load(open(f"{R}/HHS/SUMMARY.json"))
N0 = 431_985_968            # NQ 01/NQ-ĐHĐCĐ 24/04/2026 + TT08 mục 8
NR = 259_191_580            # TT08 mục 10 / NQ 07/NQ-HĐQT 26/08/2026 mục 9
OFF = 10_000                # giá chào bán
CASH = NR * OFF             # 2.591.915.800.000 (chưa trừ chi phí)
assert CASH == 2_591_915_800_000
DIV = 0.07                  # TT09: 48.382.428 cp = 7% x 691.177.548, phát hành SAU khi kết thúc chào bán
assert round((N0 + NR) * DIV) == 48_382_428
d5 = hs["liq_disc_5ty"]
TCH = 0.5831                # BCTN25 p.15 (dd_HHS REPORT.md:207)
dists = {
  "HEADLINE_CKholding0": dict(center=hs["center_post_liq"], p10=hs["p10_post"], p50=hs["p50_post"], p90=hs["p90_post"], k=1.0),
  "song_song_CKholding_r2_27pct": dict(**{q: hs["parallel_versions"]["co_CK_holding_r2 (0/15/25/35/45%, ky vong 27%)"][q] for q in ("center","p10","p50","p90")}, k=0.73),
}
def tf(V, c, k, div=DIV):
    return (V * N0 + (1 - d5) * k * c * CASH) / (N0 + c * NR) / (1 + div)
def cum_exerciser(Vf, c):  # giá trị / 1 cp hiện tại của cổ đông thực hiện đủ quyền (đã trừ tiền nộp)
    return (1 + 0.6) * (1 + DIV) * Vf - 0.6 * OFF if c > 0 else (1 + DIV) * Vf
hhs = {"inputs": dict(N0=N0, NR=NR, offer=OFF, cash=CASH, div=DIV, n_final_full=N0+NR+48_382_428, d5=d5)}
for name, D in dists.items():
    rows = {}
    for c_lab, c in (("khong_phat_hanh", 0.0), ("chi_TCH_58.31pct", TCH), ("bao_phu_50pct", 0.5), ("du_100pct", 1.0)):
        for k in sorted({D["k"], 0.8, 0.946, 1.024}):
            if name.startswith("song") and k in (1.024, 0.946): continue
            v = {q: tf(D[q], c, k) for q in ("center", "p10", "p50", "p90")}
            v["cum_exerciser_center"] = cum_exerciser(v["center"], c)
            v["rule4_threshold_ex"] = 0.85 * v["center"]
            rows[f"{c_lab}|k={k}"] = {a: round(b) for a, b in v.items()}
    hhs[name] = dict(pre=dict((q, D[q]) for q in ("center","p10","p50","p90")), k_base=D["k"], scen=rows)
# --- bổ sung vòng 2 ---
H = dists["HEADLINE_CKholding0"]; P = dists["song_song_CKholding_r2_27pct"]
terp_div = (10000 + 0.6 * OFF) / 1.6 / (1 + DIV)
x = {}
# CUM headline theo quy ước CK trên tiền (c=1,k=1)
x["cum_ckcash"] = {q: round(cum_exerciser(tf(H[q], 1.0, 1.0), 1.0)) for q in ("center", "p10", "p50", "p90")}
x["cum_ckcash_note"] = "cum_exerciser(tf(V,1,1)); 13.969 = không áp CK lên phần tiền 6.000đ đã nộp"
# điểm hoà vốn luật 4 trên cơ sở EX: giá so sánh = TERP sau cổ tức; luật 4 <=> TERP <= 0,85*tâm_EX(k)
def center_k(k): return tf(H["center"], 1.0, k)
lo, hi = 0.0, 1.5
for _ in range(60):
    mid = (lo + hi) / 2
    if terp_div * 1 <= 0.85 * center_k(mid): hi = mid
    else: lo = mid
x["rule4_breakeven_k_EX"] = round(hi, 4)
x["rule4_EX_at_k"] = {str(k): dict(center=round(center_k(k)), thr=round(0.85*center_k(k)), pass_=bool(9346 <= 0.85*center_k(k))) for k in (1.0, 0.82, 0.8)}
# so sánh giá/tâm
x["terp_div"] = round(terp_div)
x["center_per_px_cum"] = round(H["center"] / 10000, 3); x["center_per_terp_ex"] = round(tf(H["center"], 1.0, 1.0) / terp_div, 3) if False else round(tf(H["center"],1.0,1.0)/9346, 3)
x["value_per_share_change"] = round(tf(H["center"],1.0,1.0)/H["center"]-1, 4)
x["terp_change"] = round(9346/10000-1, 4)
# CK holding song song: r3 (giá 9.990 vs tâm cum) và r4 (TERP vs tâm EX)
x["parallel_ckholding"] = dict(r3_center=P["center"], r3_px_vs_center=round(9990/P["center"]-1, 4),
    r4_ex_center=round(tf(P["center"],1.0,P["k"])), r4_terp_vs_center=round(9346/tf(P["center"],1.0,P["k"])-1, 4),
    r4_px10000_vs_cumcenter=round(10000/P["center"]-1, 4))
x["rule4_parallel"] = dict(thr=round(0.85*tf(P["center"],1.0,P["k"])))
# k tương đương NĐL theo tỷ lệ công ty nêu 75,41%
nd_sh0_ = 181_990_000 / 0.9999; eq0_ = nd_sh0_ * 11_210
g2 = 0.7541 * (eq0_ + 2.6e12) - (0.5101 * eq0_ + 2.6e12)
x["k_company_7541"] = dict(gain_vnd=round(g2), k=round(1 + g2 / 2.6e12, 4))
# vốn cần cho kịch bản chỉ TCH
x["tch_only_need_vnd"] = round((1 - TCH) * CASH); x["tch_cover_vnd"] = round(TCH * CASH); x["cash_q3_vnd"] = 181_900_000_000
x["ex_k_0946"] = {q: round(tf(H[q], 1.0, round(1 + g2 / 2.6e12, 3))) for q in ("center", "p10", "p50", "p90")}
x["ex_k_0946_cum_exerciser"] = round(cum_exerciser(tf(H["center"],1.0,round(1+g2/2.6e12,3)),1.0))
hhs["round2"] = x
# giá: BQ 09/11 close 9.990; DNSE 10/11 10:46 ICT matchPrice 10.000
for px_lab, px in (("BQ_0911_close", 9990), ("DNSE_1011_1046", 10000)):
    terp = (px + 0.6 * OFF) / 1.6
    hhs[f"market_{px_lab}"] = dict(px=px, terp_rights=round(terp), terp_rights_div=round(terp / (1 + DIV)),
                                  right_value_per_new=px - OFF)
# bargain NĐL: mua 260tr cp mới @10.000 vs BV 11.210 (TT08 tr.110). HHS lợi ích 51,01% trước; giả định NĐL chỉ phát hành 260tr cho HHS
nd_sh0, nd_bv = 181_990_000 / 0.9999, 11_210
eq0 = nd_sh0 * nd_bv; own0 = 0.5101 * nd_sh0
own1 = (own0 + 260e6) / (nd_sh0 + 260e6)
gain = own1 * (eq0 + 2.6e12) - (0.5101 * eq0 + 2.6e12)
hhs["bargain_NDL"] = dict(own_after_calc=round(own1, 4), own_after_company=0.7541, gain_vnd=round(gain), k_equiv=round(1 + gain / 2.6e12, 4),
                         note="Tỷ lệ tự tính 79,8% != công ty nêu 75,41% (TT08) ⇒ cấu trúc phát hành NĐL chưa rõ; chỉ dùng làm độ nhạy")

# ---------------- SCL ----------------
sc = json.load(open(f"{R}/SCL/calc_r3/model_scl_r3_out.json"))
S0, RAT, SUB = 38_836_815, 0.154453, 12_500
SNR = S0 * RAT; SCASH = SNR * SUB
scl = {"inputs": dict(S0=S0, ratio=RAT, sub_px=SUB, new_sh=round(SNR), cash=round(SCASH), n_post=round(S0 + SNR), terp_r3=sc["terp"])}
for lab, cum_key, post_key, dcol in (("ck40tr", "headline", "ck40tr", "disc_40tr"), ("ck5ty", "headline_ck5ty", "ck5ty", "disc_5ty")):
    cum = sc["headline"]["dist"] if lab == "ck40tr" else sc["headline_ck5ty"]["dist"]
    post = sc["post_rights"][post_key]
    cpre = dict(center=cum["center_post"], **{q: cum["P_post"][q] for q in ("p10", "p50", "p90")})
    full = dict(center=post["center_post"], **{q: post["P_post"][q] for q in ("p10", "p50", "p90")})
    d = sc.get(dcol, sc.get("disc_5ty") if lab == "ck5ty" else None)
    # kịch bản bao phủ một phần: dùng V_cum (= giá trị trước quyền / cp cũ) ⇒ (V*S0 + (1-d)c*Cash)/(S0+c*SNR)
    dd = sc["disc_5ty"] if lab == "ck5ty" else sc["disc_40tr"]   # r2: áp CK lên cả phần tiền thu (nhất quán r3)
    part = {}
    for c in (0.0, 0.5, 1.0):
        part[str(c)] = {q: round((cpre[q] * S0 + (1 - dd) * c * SCASH) / (S0 + c * SNR)) for q in cpre}
    scl[lab] = dict(cum=dict((q, round(v)) for q, v in cpre.items()), post_full_r3=dict((q, round(v)) for q, v in full.items()), partial_recalc=part)
# ESOP đợt 2 giả định (2,1% announced 07/05, KHÔNG xác định được): +2,1% x 44,84tr @10.000 sau quyền
for lab in ("ck40tr", "ck5ty"):
    f = scl[lab]["post_full_r3"]; n = S0 + SNR; e = 0.021 * n
    scl[lab]["esop2_sens"] = {q: round((v * n + e * 10_000) / (n + e)) for q, v in f.items()}
scl["esop_overlap"] = {"base_pre_esop": 37_916_815, "esop": 920_000, "new_rights": 6_000_000,
  "reading_duplicate_pct": round(920_000 / (37_916_815 + 6_000_000) * 100, 3),
  "reading_separate_pct": round(920_000 / (37_916_815 + 6_000_000) * 100, 3),
  "note": "cả 2 cách đọc cùng mẫu số 43.916.815 → 2,095%; 2,1% đúng bằng 920.000/43,9tr (không phải 2,1% × 44,84 tr = 0,94 tr)"}
scl["market"] = dict(close_0611_cum=29400, close_0911_ex=28000, ohlc_0911=[28000, 29000, 27700, 28000], vol_0911=45100,
                     dnse_1011=dict(ref=28100, match=28300, time="2026-11-10 10:18 ICT", vol_lots=690))
for px_lab, px in (("0911", 28000), ("1011", 28300)):
    scl["market"][f"px_{px_lab}_vs_terp"] = round(px / sc["terp"] - 1, 4)
    scl["market"][f"right_implied_{px_lab}_per_new"] = px - SUB
    scl["market"][f"right_implied_{px_lab}_per_old"] = round(RAT * (px - SUB))
    scl["market"][f"cum_equiv_{px_lab}"] = round(px * (1 + RAT) - RAT * SUB)
json.dump(dict(HHS=hhs, SCL=scl), open(f"{OUT}/dilution_out.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(HHS=hhs, SCL=scl), ensure_ascii=False, indent=1))
