"""Giai đoạn 2 (SAU LOCK 21:54:32 ICT): so giá trị nội tại khoá với giá thị trường.
Tái lập: cd .. && python3 -I phase2/compare.py > phase2/compare_out.txt  (đọc phase2/dnse_20261102.json)"""
import io, json, contextlib, runpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    V = runpy.run_path(os.path.join(HERE, "..", "valuation_blind.py"))
ps, SH, pv_mid, hydro_fcfe, consult = V["ps"], V["SH"], V["pv_mid"], V["hydro_fcfe"], V["consult"]
BS, KE_C, CV, PRICE, PROB, P_CON = V["BS"], V["KE_C"], V["CV"], V["PRICE"], V["PROB"], V["P_CON"]
d = json.load(open(os.path.join(HERE, "dnse_20261102.json")))
lt = [t for t in d["latest_trade"]["trades"] if t["boardId"] == "G1"][0]
PX = lt["matchPrice"] * 1000
print(f"Giá DNSE latest_trade TV1: {PX:,.0f} đ (khớp {lt['time']}; TB phiên {lt['avgPrice']*1000:,.0f}; KL phiên {lt['totalVolumeTraded']*10:,} cp?) "
      f"| đóng cửa 30/10: 19.800 | fetched {d['fetched_ICT']}")
o = d["ohlc"]; vol20 = sum(o["v"][-20:]) / 20; px20 = sum(c * v for c, v in zip(o["c"][-20:], o["v"][-20:])) / max(sum(o["v"][-20:]), 1)
print(f"KL bình quân 20 phiên {vol20:,.0f} cp ≈ {vol20*px20*1000/1e9:.2f} tỷ/phiên")
mcap = SH * PX / 1e9
ttm = 63.85 + 124.636; ttm_core = ttm - 31.9; eq = 574.723
print(f"Vốn hoá {mcap:.1f} tỷ | P/E TTM {mcap/ttm:.2f} (lõi bỏ khác ròng Q3: {mcap/ttm_core:.2f}) | P/B {mcap/eq:.2f} | cổ tức 1.500 ⇒ lợi suất {1500/PX:.1%}")
centre = 27_788
print(f"\nGiá so tâm nội tại {centre:,}: {PX/centre-1:+.0%}; so ô trung vị 25.061: {PX/25061-1:+.0%}; so P20 22.090: {PX/22090-1:+.0%}")

# ---- Giá ngầm định: giữ các khối khác ở tâm, giải ra biến còn lại
target = mcap
def solve(f, lo, hi):
    for _ in range(80):
        m = (lo + hi) / 2
        if f(m) > target: hi = m
        else: lo = m
    return m
hyd_c = lambda p: pv_mid(hydro_fcfe(p, 195), KE_C)
con_w = sum(CV[s] * P_CON[s] for s in CV)
p_imp = solve(lambda p: hyd_c(p) + con_w + BS, 0, 1500)
print(f"\nNgầm định 1 — giá PPA ròng 2027+ (tư vấn = kỳ vọng {con_w:.0f}, Q195): {p_imp:.0f} đ/kWh")
p_imp2 = solve(lambda p: hyd_c(p) + CV['C_giua'] + BS, 0, 1500)
print(f"  (tư vấn = kịch bản giữa): {p_imp2:.0f} đ/kWh")
hyd_w = sum(pv_mid(hydro_fcfe(PRICE[k], 195), KE_C) * PROB[k] for k in PRICE)
c_imp = target - hyd_w - BS
print(f"Ngầm định 2 — giá trị tư vấn (thuỷ điện = kỳ vọng {hyd_w:.0f}): {c_imp:.0f} tỷ ⇒ = {c_imp/consult('C_giua')[1][0]:.1f}× LNST tư vấn 2027 kịch bản giữa; "
      f"so kịch bản thấp {CV['C_thap']:.0f}")
def tot(ke):
    h = sum(pv_mid(hydro_fcfe(PRICE[k], 195), ke) * PROB[k] for k in PRICE)
    c = sum(consult(s, ke=ke)[0] * P_CON[s] for s in CV)
    return h + c + BS
lo, hi = 0.10, 0.60
for _ in range(80):
    m = (lo + hi) / 2
    if tot(m) > target: lo = m
    else: hi = m
print(f"Ngầm định 3 — Ke chung (mọi giả định khác ở tâm): {m:.1%}")
loss = (centre - PX) / 1e3 * SH / 1e3 / 1e3  # tỷ
print(f"Ngầm định 4 — khoảng cách {centre-PX:,.0f} đ/cp = {(centre-PX)*SH/1e9:.0f} tỷ ≈ cú sốc 'cấm thầu EVN 3 năm −50% DT tư vấn' (−8.600 đ/cp) "
      f"hoặc ≈ P(cấm 3 năm) × 8.600 với P = {(centre-PX)/8626:.2f} nếu không có lý do nào khác")

# ---- Đối chiếu chéo peer (SAU khoá) [../dd_TV1_20261102/calc/peer_study/peer_study_out.txt, peer_calib.json]
print("\nĐối chiếu peer:")
PE_HYD = (7.9, 8.81, 9.22); PE_CON = (6.0, 9.2)   # thuỷ điện UPCOM p25/trung vị/nhóm; tư vấn TV4/TV3 2026 YTD (TV2 méo)
for k in PRICE:
    ni = V["hydro_ni"](PRICE[k], 195)
    print(f"  Thuỷ điện {k}: LNST28 {ni:.1f} × P/E peer {PE_HYD[0]}–{PE_HYD[2]} = {ni*PE_HYD[0]:.0f}–{ni*PE_HYD[2]:.0f} tỷ "
          f"(DCF mù {pv_mid(hydro_fcfe(PRICE[k],195),KE_C):.0f}) — P/E chỉ hợp khi giá đã ổn định; P1 so được, P2–P4 DCF cao hơn vì khấu hao hết 2039 + lá chắn")
ni_c26 = 45.0   # LNST tư vấn lõi 2026E [UL: 9T EBIT lõi 36,6–55,8 ×0,8 ⇒ 29–45; + Q4 nặng]
print(f"  Tư vấn: LNST lõi 2026E ~{ni_c26:.0f} [UL] × P/E TV4–TV3 {PE_CON[0]}–{PE_CON[1]} = {ni_c26*PE_CON[0]:.0f}–{ni_c26*PE_CON[1]:.0f} tỷ (DCF mù kỳ vọng {con_w:.0f})")
print(f"  ⇒ SOTP bằng peer (thuỷ điện kỳ vọng theo P/E giữa, tư vấn P/E 6–9,2): "
      f"{ps(sum(V['hydro_ni'](PRICE[k],195)*PE_HYD[1]*PROB[k] for k in PRICE)+ni_c26*PE_CON[0]+BS):,.0f}–"
      f"{ps(sum(V['hydro_ni'](PRICE[k],195)*PE_HYD[1]*PROB[k] for k in PRICE)+ni_c26*PE_CON[1]+BS):,.0f} đ/cp")
print(f"  P/E TTM TV1 {mcap/ttm:.1f}× vs tư vấn 6–9× & thuỷ điện 7,9–9,2× ⇒ chiết khấu {1-(mcap/ttm)/7.5:.0%} so mốc 7,5×")
