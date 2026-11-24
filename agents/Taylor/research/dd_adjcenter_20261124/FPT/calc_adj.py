"""Tâm kỳ vọng điều chỉnh FPT — áp PREREG_adj.md (md5 ef5157cb…). Mù giá: không đọc giá."""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "..", "PREREG_adj.md")
assert hashlib.md5(open(PRE, "rb").read()).hexdigest() == "ef5157cb3f762d58623ed550ebc214c7"
C = 57312                    # kb/dd_price_zones.json FPT rev4 center
SH = 1885.727648e6           # N:320 cp lưu hành
S = "agents/Taylor/research/dd_recheck_20261124/FPT/skeptic/r1_raw.md"
N = "agents/Taylor/research/dd_FPT_20261101/calc/notes_q3_bctc.md"
R = "agents/Taylor/research/dd_recheck_20261124/FPT/REPORT_recheck_FPT.md"
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "Bneg": (0.35, 0.15, 0.55)}
def pct(vnd_bn): return vnd_bn * 1e9 / SH / C * 100
items = [
 dict(name="Tồn quỹ KTPL 1.477 tỷ chưa trừ khỏi NC", dir="down", mag_pct=-pct(1476.946474828), evidence_tier="A", rung="A",
      source=f"{N}:69; {S}:14", note="nợ phải trả, tiền tương ứng đang nằm trong NC 12.233 tỷ"),
 dict(name="XDCB 'Khác' 371 tỷ chưa cộng (NPV 0 = giá sổ, như XDCB giáo dục 760 tỷ)", dir="up", mag_pct=pct(371.099447553), evidence_tier="A", rung="A",
      source=f"{N}:344; {S}:24"),
 dict(name="Pha loãng ESOP (108 tỷ mệnh giá 9T26 ≈0,57%)", dir="down", mag_pct=-2.5, evidence_tier="B", rung="B1",
      source=f"{N}:321; {S}:16", note="m = ước lượng của skeptic (S:16), 1 quan sát (9T26)"),
 dict(name="conv CƠ SỞ 0,75 → 0,60 (FY25 0,60; 9T26 −0,12)", dir="down", mag_pct=-1.85, evidence_tier="B", rung="B1",
      source=f"{S}:17,47 (probe model_r3)", note="2 quan sát cùng hướng < 3 ⇒ mặc định; gồm phần capex đã thể hiện trong lịch sử"),
 dict(name="g CƠ SỞ 9% → 12% (LFL 9T26 +13,7%, LNTT CN +16,6%)", dir="up", mag_pct=3.32, evidence_tier="B", rung="Bneg",
      source=f"{S}:22,47 (probe model_r3)", note="1 quan sát (cùng kỳ); quan sát ngược: 5F Nhật Q3 giảm tốc (REPORT_recheck:56)"),
]
s_c = s_lo = s_hi = 0.0
for it in items:
    p, plo, phi = P[it.pop("rung")]
    m = it["mag_pct"] / 100
    it.update(p=p, p_low=plo, p_high=phi, counted_in_center_bool=True,
              contrib_pct=round(p * m * 100, 3), mag_pct=round(it["mag_pct"], 3))
    s_c += p * m; s_lo += min(plo * m, phi * m); s_hi += max(plo * m, phi * m)
DIV = 1000
sens = [
 dict(name="Cam kết capex DC/AI/giáo dục vượt lịch sử conv (chưa đọc thuyết minh)", dir="down", evidence_tier="C",
      sensitivity="mỗi 1.000 tỷ cam kết NPV âm toàn phần = %.2f%% (%d đ/cp)" % (-pct(1000), -round(1000e9 / SH)), source=f"{S}:13"),
 dict(name="Trích quỹ KTPL hằng năm từ LNST (tỷ lệ chưa kiểm)", dir="down", evidence_tier="C",
      sensitivity="5%% ⇒ −3%% (S:15); mỗi 1pp ⇒ ≈−0,59%% (phần DCF ≈59%% tâm, S:9)", source=f"{S}:9,15; {N} (không có dòng trích KTPL 9T26)"),
 dict(name="OTHER_ASSOC_BOOK 1.500 tỷ [UL]", dir="both", evidence_tier="C",
      sensitivity="trục oth −1.300…+2.600 đ/cp = %.2f%%…+%.2f%%" % (-1300 / C * 100, 2600 / C * 100), source=f"{S}:23,39; {N}:277"),
 dict(name="Lãi LK Q4/25 600 tỷ [UL] (G10)", dir="both", evidence_tier="C",
      sensitivity="740 tỷ ⇒ 56.616 (%.2f%%); thấp hơn 600 ⇒ chiều lên" % ((56616 / C - 1) * 100), source=f"{R}:62"),
 dict(name="[LUẬT] r 13,5% vs dải Ke 12,3–13,4% (E15)", dir="up", evidence_tier="rule",
      sensitivity="Ke 12,3% ⇒ 61.176 (+6,74%); 13,4% ⇒ 57.606 (+0,51%)", source=f"{R}:13,37-41"),
 dict(name="[LUẬT] chặn RONIC pha 5 năm ở Ke (bản G)", dir="down", evidence_tier="rule",
      sensitivity="50.652 (%.2f%%)" % ((50652 / C - 1) * 100), source=f"{R}:51"),
]
ca = round(C * (1 + s_c)); lo = round(C * (1 + s_lo)); hi = round(C * (1 + s_hi))
def d_center(dp_pct): return round(C * dp_pct / 100)
m_conv, m_g, m_esop = -1.85, 3.32, -2.5
trig = [
 dict(event="GDKHQ cổ tức tiền 1.000 đ (chốt quyền 30/11/2026; ngày GDKHQ cần xác nhận CBTT)", when="cuối 11/2026",
      direction="down", delta_vnd=-DIV, delta_pct=round(-DIV / C * 100, 2), note="cơ học, chắc chắn"),
 dict(event="BCTC Q4/2026 + năm 2026: thuyết minh cam kết vốn (DC/AI/giáo dục)", when="ước lượng cuối 01/2027 (chưa xác minh lịch)",
      direction="down", delta_vnd=-round(1000e9 / SH), delta_pct=round(-pct(1000), 2), note="mỗi 1.000 tỷ cam kết NPV âm: C→A; cam kết growth có NPV≈0 ⇒ 0"),
 dict(event="BCTC năm 2026: conv FY26 ≤0,60", when="ước lượng cuối 01/2027", direction="down",
      delta_vnd=d_center((0.9 - 0.5) * m_conv), delta_pct=round((0.9 - 0.5) * m_conv, 2), note="p conv 0,50→0,90 (thành 3 quan sát cùng hướng + số năm trực tiếp)"),
 dict(event="BCTC năm 2026: conv FY26 ≥0,75", when="ước lượng cuối 01/2027", direction="up",
      delta_vnd=d_center((0.1 - 0.5) * m_conv), delta_pct=round((0.1 - 0.5) * m_conv, 2), note="p conv 0,50→0,10"),
 dict(event="Q4/2026 LFL LNST cả năm ≥12% và Nhật không giảm tốc tiếp", when="ước lượng cuối 01/2027", direction="up",
      delta_vnd=d_center((0.65 - 0.35) * m_g), delta_pct=round((0.65 - 0.35) * m_g, 2), note="p g 0,35→0,65"),
 dict(event="Q4/2026 LFL LNST <9%", when="ước lượng cuối 01/2027", direction="down",
      delta_vnd=d_center((0.0 - 0.35) * m_g), delta_pct=round((0.0 - 0.35) * m_g, 2), note="p g 0,35→0"),
 dict(event="Tài liệu/NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL", when="ước lượng 03–04/2027", direction="down",
      delta_vnd=d_center(0.9 * -3.0), delta_pct=round(0.9 * -3.0, 2), note="C→A; ví dụ tỷ lệ 5% (m −3%, S:15); mỗi 1pp ≈ −0,59%×0,9"),
 dict(event="NQ ĐHĐCĐ 2027: có ESOP cùng cỡ 2026", when="ước lượng 03–04/2027", direction="down",
      delta_vnd=d_center((0.9 - 0.5) * m_esop), delta_pct=round((0.9 - 0.5) * m_esop, 2), note="ESOP B→A; KHÔNG có ESOP ⇒ +%.2f%%" % (0.5 * -m_esop)),
 dict(event="BCTC kiểm toán 2026 / BCTN25 điều chỉnh: lãi LK Q4/25", when="ước lượng 03/2027", direction="both",
      delta_vnd=56616 - C, delta_pct=round((56616 / C - 1) * 100, 2), note="ví dụ 740 tỷ; C→A"),
 dict(event="Thuyết minh LK chi tiết (BCTC năm): giá trị liên kết khác", when="ước lượng 03/2027", direction="both",
      delta_vnd=None, delta_pct=None, note="−1.300…+2.600 đ/cp (C→A)"),
 dict(event="Lãi huy động 12T hiệu dụng đổi Δ (luật V1, β=1)", when="theo dõi liên tục", direction="both",
      delta_vnd=-1406, delta_pct=-2.45, note="mỗi +50bp ⇒ −1.406 (REPORT_recheck:42); −50bp ⇒ +1.519"),
 dict(event="Số dư quỹ KTPL mới (mỗi BCTC quý)", when="mỗi quý", direction="both",
      delta_vnd=None, delta_pct=None, note="m1 tính lại = −số dư/SH/tâm; p 0,9"),
]
out = dict(ticker="FPT", asof="2026-11-24", prereg_md5="ef5157cb3f762d58623ed550ebc214c7", blind_to_price=True,
           center_base=C, center_base_source="kb/dd_price_zones.json FPT rev4 (center, gồm cổ tức 1.000 đ chưa GDKHQ)",
           items=items, sum_p_m_pct=round(s_c * 100, 3),
           center_adj=ca, range_low=lo, range_high=hi,
           center_adj_ex_div=ca - DIV, range_low_ex_div=lo - DIV, range_high_ex_div=hi - DIV,
           dividend_mech=dict(vnd=-DIV, pct=round(-DIV / C * 100, 3), note="cộng trừ đ/cp, tách khỏi Σ (PREREG §4)"),
           sensitivity_only=sens, trigger_table=trig,
           caveat="cộng tuyến tính probe độc lập (bỏ tương tác g×conv); m của ESOP/conv/g là số skeptic, không rerun model")
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "center_adj_ex_div", "sum_p_m_pct"]}))
for it in items: print(it["evidence_tier"], it["p"], it["mag_pct"], it["contrib_pct"], it["name"])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"])
