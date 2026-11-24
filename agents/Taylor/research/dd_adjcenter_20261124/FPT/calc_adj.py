"""Tâm kỳ vọng điều chỉnh FPT — CHẠY LẠI theo PREREG_adj.md + PREREG_adj_v2.md (fan-out g1, job Taylor_20261124_110049).
Thay pilot (0d52b34ec): thêm C+ trích KTPL hằng năm; dải theo cực trị (p, m); quan sát ngược định tính không tính (g: Bneg→B1).
Mù giá: không đọc giá thị trường / forward return."""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
PRE1, PRE2 = (os.path.join(HERE, "..", f) for f in ("PREREG_adj.md", "PREREG_adj_v2.md"))
assert md5(PRE1) == "ef5157cb3f762d58623ed550ebc214c7" and md5(PRE2) == "835dfc1e07f9c67ac7f6c3028b529d13"
C = 57312                    # kb/dd_price_zones.json FPT rev4 center (dd_date 2026-11-01)
SH = 1885.727648e6           # N:320 cp lưu hành
S = "agents/Taylor/research/dd_recheck_20261124/FPT/skeptic/r1_raw.md"
N = "agents/Taylor/research/dd_FPT_20261101/calc/notes_q3_bctc.md"
R = "agents/Taylor/research/dd_recheck_20261124/FPT/REPORT_recheck_FPT.md"
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "B3": (0.65, 0.40, 0.90), "Bneg": (0.35, 0.15, 0.55)}
def pct(vnd_bn): return vnd_bn * 1e9 / SH / C * 100
# Trích KTPL hằng năm (C+): LNST mẹ 2025 = 9T25 6.866,6 (N:326) + Q4/25 2.509,5 (S:8) = 9.376,1 tỷ.
NP25 = 6866.605 + 2509.52
FUND_0, FUND_1 = 2160.077, 1476.946                      # N:323 (31/12/25 → 30/9/26), 9T26 không có dòng trích
draw_ann = (FUND_0 - FUND_1) * 4 / 3                     # tốc độ chi quỹ năm hoá
rate_lo = 0.5 * draw_ann / NP25                          # cận bảo thủ: một nửa mức giảm quy cho hợp nhất lại FTEL (phần chưa tách được)
rate_hi = draw_ann / NP25                                # toàn bộ mức giảm là chi quỹ ⇒ trích bền vững ≈ chi
SLOPE = -0.59                                            # % tâm mỗi 1pp LNST (phần DCF ≈59% tâm, S:9)
items = [
 dict(name="Tồn quỹ KTPL 1.477 tỷ chưa trừ khỏi NC", dir="down", m=-pct(FUND_1), m_lo=None, m_hi=None, evidence_tier="A", rung="A",
      source=f"{N}:323(dòng 69); {S}:14", note="nợ phải trả, tiền tương ứng đang nằm trong NC 12.233 tỷ; số trực tiếp BCTC"),
 dict(name="XDCB 'Khác' 371 tỷ chưa cộng (NPV 0 = giá sổ)", dir="up", m=pct(371.099447553), m_lo=None, m_hi=None, evidence_tier="A", rung="A",
      source=f"{N}:344; {S}:24"),
 dict(name="Trích quỹ KTPL hằng năm từ LNST (C+ — cận bảo thủ)", dir="down", m=rate_lo * 100 * SLOPE, m_lo=rate_lo * 100 * SLOPE, m_hi=rate_hi * 100 * SLOPE,
      evidence_tier="C+", rung="B1", source=f"{N}:323,326; {S}:8,9,15",
      note="dấu chắc chắn (quỹ giảm 683 tỷ trong 9T26 không có dòng trích ⇒ đang chi ~%.1f%% LNST/năm, phải trích bù để duy trì). Cận bảo thủ %.2f%% LNST = ½ tốc độ chi (½ còn lại quy cho FTEL ra khỏi hợp nhất); cận cao %.2f%%. 1 quan sát (9T26) ⇒ p B1" % (rate_hi * 100, rate_lo * 100, rate_hi * 100)),
 dict(name="Pha loãng ESOP (108 tỷ mệnh giá 9T26 ≈0,57%/năm)", dir="down", m=-2.5, m_lo=-0.47, m_hi=-3.0, evidence_tier="B", rung="B1",
      source=f"{N}:321; {S}:16", note="m điểm = số skeptic; khoảng ước lượng: thấp = một lần 0,57%×(1−10.000/57.312); cao = vĩnh viễn 0,57%/năm ≈ +0,57pp vào r trên phần DCF 59%, trừ tiền thu mệnh giá. 1 quan sát (9T26)"),
 dict(name="conv CƠ SỞ 0,75 → 0,60", dir="down", m=-1.85, m_lo=None, m_hi=None, evidence_tier="B", rung="B1",
      source=f"{S}:17,47 (probe model_r3)", note="2 kỳ báo cáo (FY25 0,60; 9T26 −0,12) cùng hướng < 3 ⇒ mặc định; gồm phần capex đã thể hiện trong lịch sử"),
 dict(name="g CƠ SỞ 9% → 12% (LFL 9T26 +13,7%)", dir="up", m=3.32, m_lo=None, m_hi=None, evidence_tier="B", rung="B1",
      source=f"{S}:22,47 (probe model_r3)", note="1 kỳ (LNST LFL và LNTT CN cùng 9T26 = 1 quan sát). v2 §3: quan sát ngược định tính (5F Nhật giảm tốc) KHÔNG tính ⇒ B1 (pilot dùng Bneg)"),
]
s_c = s_lo = s_hi = 0.0
for it in items:
    p, plo, phi = P[it.pop("rung")]
    m = it.pop("m") / 100
    ms = [m] + [x / 100 for x in (it.pop("m_lo"), it.pop("m_hi")) if x is not None]
    combos = [pp * mm for pp in (plo, phi) for mm in ms]
    it.update(p=p, p_low=plo, p_high=phi, mag_pct=round(m * 100, 3), mag_range_pct=[round(min(ms) * 100, 3), round(max(ms) * 100, 3)],
              counted_in_center=True, contrib_pct=round(p * m * 100, 3))
    s_c += p * m; s_lo += min(combos); s_hi += max(combos)
assert abs(s_c) <= 0.05, "v2 §5: |Σ|>5% ⇒ phải chạy mô hình tổ hợp"
DIV = 1000
sens = [
 dict(name="Cam kết capex DC/AI/giáo dục vượt lịch sử conv (chưa đọc thuyết minh)", dir="down", evidence_tier="C",
      sensitivity="mỗi 1.000 tỷ cam kết NPV âm toàn phần = %.2f%% (%d đ/cp)" % (-pct(1000), -round(1000e9 / SH)), source=f"{S}:13",
      why_not_center="không dấu chắc chắn (capex tăng trưởng NPV≈0) và không có cận; phần đã thể hiện trong lịch sử nằm ở conv"),
 dict(name="OTHER_ASSOC_BOOK 1.500 tỷ [UL]", dir="both", evidence_tier="C",
      sensitivity="−1.300…+2.600 đ/cp = %.2f%%…+%.2f%%" % (-1300 / C * 100, 2600 / C * 100), source=f"{S}:23,39; {N}:277"),
 dict(name="Lãi LK Q4/25 600 tỷ [UL] (G10)", dir="both", evidence_tier="C",
      sensitivity="740 tỷ ⇒ 56.616 (%.2f%%)" % ((56616 / C - 1) * 100), source=f"{R}:62"),
 dict(name="[LUẬT] r 13,5% vs dải Ke 12,3–13,4% (E15)", dir="up", evidence_tier="rule",
      sensitivity="Ke 12,3% ⇒ 61.176 (+6,74%); 13,4% ⇒ +0,51%", source=f"{R}:13,37-41"),
 dict(name="[LUẬT] chặn RONIC pha 5 năm ở Ke (bản G)", dir="down", evidence_tier="rule",
      sensitivity="50.652 (%.2f%%)" % ((50652 / C - 1) * 100), source=f"{R}:51"),
]
ca, lo, hi = (round(C * (1 + s)) for s in (s_c, s_lo, s_hi))
def dc(dp): return round(C * dp / 100)
m_conv, m_g, m_esop = -1.85, 3.32, -2.5
m_ktpl5 = 5 * SLOPE; c_ktpl_now = 0.5 * rate_lo * 100 * SLOPE
trig = [
 dict(event="GDKHQ cổ tức tiền 1.000 đ (chốt quyền 30/11/2026)", when="cuối 11/2026", direction="down", delta_vnd=-DIV, delta_pct=round(-DIV / C * 100, 2), note="cơ học"),
 dict(event="NQ/tài liệu ĐHĐCĐ 2027 hoặc BCTC năm 2026 có dòng trích KTPL: tỷ lệ thật", when="BCTC năm cuối 01/2027; ĐHĐCĐ 03–04/2027 (ước lượng lịch)",
      direction="both", delta_vnd=dc(0.9 * m_ktpl5 - c_ktpl_now), delta_pct=round(0.9 * m_ktpl5 - c_ktpl_now, 2),
      note="C+→A, p 0,9; ví dụ 5%% LNST; mỗi 1pp khác 5%% ⇒ %.2f%%; tỷ lệ ≤ %.1f%% ⇒ chiều lên" % (0.9 * SLOPE, (c_ktpl_now / 0.9) / SLOPE)),
 dict(event="Thuyết minh cam kết vốn DC/AI/giáo dục (BCTC năm 2026)", when="cuối 01/2027 (ước lượng)", direction="down",
      delta_vnd=-round(1000e9 / SH), delta_pct=round(-pct(1000), 2), note="mỗi 1.000 tỷ cam kết NPV âm: C→A; growth NPV≈0 ⇒ 0"),
 dict(event="Q4/2026 (kỳ mới) conv ≤0,60", when="cuối 01/2027", direction="down", delta_vnd=dc(0.15 * m_conv), delta_pct=round(0.15 * m_conv, 2), note="3 kỳ cùng hướng ⇒ p 0,50→0,65"),
 dict(event="Q4/2026 conv ≥0,75", when="cuối 01/2027", direction="up", delta_vnd=dc(-0.15 * m_conv), delta_pct=round(-0.15 * m_conv, 2), note="quan sát ngược có số ⇒ p 0,50→0,35"),
 dict(event="Q4/2026 LFL LNST ≥12% (kỳ mới) + KH 2027 ĐHĐCĐ ≥12%", when="01–04/2027", direction="up", delta_vnd=dc(0.15 * m_g), delta_pct=round(0.15 * m_g, 2), note="3 quan sát ⇒ p 0,50→0,65"),
 dict(event="Q4/2026 LFL LNST <9%", when="cuối 01/2027", direction="down", delta_vnd=dc(-0.15 * m_g), delta_pct=round(-0.15 * m_g, 2), note="quan sát ngược có số ⇒ p 0,50→0,35"),
 dict(event="NQ ĐHĐCĐ 2027: có ESOP cùng cỡ", when="03–04/2027", direction="down", delta_vnd=dc(0.4 * m_esop), delta_pct=round(0.4 * m_esop, 2), note="B→A p 0,9"),
 dict(event="NQ ĐHĐCĐ 2027: KHÔNG có ESOP", when="03–04/2027", direction="up", delta_vnd=dc(-0.5 * m_esop), delta_pct=round(-0.5 * m_esop, 2), note="p→0"),
 dict(event="BCTC kiểm toán 2026: lãi LK Q4/25 (ví dụ 740 tỷ)", when="03/2027", direction="both", delta_vnd=56616 - C, delta_pct=round((56616 / C - 1) * 100, 2), note="C→A"),
 dict(event="Lãi huy động 12T hiệu dụng ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_vnd=-1406, delta_pct=-2.45, note="+50bp −1.406; −50bp +1.519 (REPORT_recheck:42)"),
 dict(event="Số dư quỹ KTPL mới mỗi BCTC quý", when="mỗi quý", direction="both", delta_vnd=None, delta_pct=None, note="m#1 = −số dư/SH/tâm, p 0,9"),
 dict(event="Pháp lý FTEL", when="khi có", direction="none", delta_vnd=0, delta_pct=0, note="chỉ WARNING, không vào tâm"),
]
out = dict(ticker="FPT", dd_date="2026-11-01", rev=4, asof="2026-11-24", job="Taylor_20261124_110049",
           prereg_md5=dict(PREREG_adj="ef5157cb3f762d58623ed550ebc214c7", PREREG_adj_v2="835dfc1e07f9c67ac7f6c3028b529d13"), blind_to_price=True,
           center_base=C, center_base_source="kb/dd_price_zones.json FPT rev4 center (gồm cổ tức 1.000 đ chưa GDKHQ)",
           items=items, sum_p_m_pct=round(s_c * 100, 3), aggregation="linear (|Σ|≤5%)",
           center_adj=ca, range_low=lo, range_high=hi,
           center_adj_ex_div=ca - DIV, range_low_ex_div=lo - DIV, range_high_ex_div=hi - DIV,
           dividend_mech=dict(vnd=-DIV, record_date="2026-11-30", status="chưa GDKHQ", note="trừ đ/cp, ngoài Σ"),
           sensitivity_only=sens, trigger_table=trig,
           supersedes=dict(pilot_commit="0d52b34ec", pilot_center_adj=56204, pilot_range=[55092, 57345]),
           caveat="cộng tuyến tính (|Σ|≤5%); m ESOP/conv/g là số skeptic/probe, không rerun model (calc r3 bị TRIM)")
assert 0 < lo <= ca <= hi
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "center_adj_ex_div", "range_low_ex_div", "range_high_ex_div", "sum_p_m_pct"]}))
for it in items: print(it["evidence_tier"], it["p"], it["mag_pct"], it["mag_range_pct"], it["contrib_pct"], it["name"])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"])
