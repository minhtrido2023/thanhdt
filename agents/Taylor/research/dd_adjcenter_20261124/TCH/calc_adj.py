"""Tâm kỳ vọng điều chỉnh TCH — PREREG_adj.md + PREREG_adj_v2.md (fan-out g1, job Taylor_20261124_110049). Mù giá."""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
PRE1, PRE2 = (os.path.join(HERE, "..", f) for f in ("PREREG_adj.md", "PREREG_adj_v2.md"))
assert md5(PRE1) == "ef5157cb3f762d58623ed550ebc214c7" and md5(PRE2) == "835dfc1e07f9c67ac7f6c3028b529d13"
C = 15864                    # kb/dd_price_zones.json TCH rev5 center (sau CK 5 tỷ 0,63%; dd_date 2026-10-31)
SH = 1003.312808e6           # notes_read.md:40
RR = "agents/Taylor/research/dd_recheck_20261124/TCH/REPORT_recheck_TCH.md"
S1 = "agents/Taylor/research/dd_recheck_20261124/TCH/skeptic/r1_raw.md"
R3B = "agents/Taylor/research/dd_redo_20261105/TCH/REPORT_r3b.md"
S0 = "agents/Taylor/research/dd_redo_20261105/TCH/skeptic/r1_raw.md"
NR = "agents/Taylor/research/dd_TCH_20261031/calc/notes_read.md"
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "B3": (0.65, 0.40, 0.90), "Bneg": (0.35, 0.15, 0.55)}
def pv(vnd): return vnd / C * 100          # đ/cp → % tâm
def pb(bn): return bn * 1e9 / SH / C * 100  # tỷ → % tâm
items = [
 dict(name="Biên gộp BĐS base 51,9% (6T FY26 chưa soát xét) → 42,7% kiểm toán", dir="down", m=pv(13642 - C), m_lo=None, m_hi=None, evidence_tier="B", rung="Bneg",
      source=f"{R3B}:92,103-104; {RR}:46; {S1}:22", note="m = chạy lại mô hình r3b (song song g_audit_427, tái lập ở recheck). Cùng hướng: FY24 42,7%, FY25 42,7% (2 kỳ kiểm toán). Ngược có số: 6T FY26 51,9%, 6T FY25 51,0% (soát xét) ⇒ nhánh ngược"),
 dict(name="NOXH Green River (441 căn NOXH/1.251, 'đang thi công khu NOXH') hưởng biên thương mại trong mô hình (C+ — cận bảo thủ)", dir="down", m=pv(-274), m_lo=pv(-274), m_hi=pv(-480), evidence_tier="C+", rung="B1",
      source=f"{NR}:140,146; {S0}:10-12", note="dấu chắc chắn (NOXH có trần lợi nhuận, mô hình cho 51,9%); cận bảo thủ = stress skeptic tỷ trọng NOXH 20% (−274 đ), cận cao 35% ≈ 441/1.251 căn (−480 đ); số skeptic tính trên r3 (ước lượng). 1 nguồn ⇒ p B1"),
 dict(name="Dạng chính xác C_unsold (backlog chỉ chiếm cost_bl/(1+k) trong HTK) thay dạng thận trọng", dir="up", m=pv(16442 - C), m_lo=None, m_hi=None, evidence_tier="B", rung="Bneg",
      source=f"{R3B}:91; {S1}:'symmetry'", note="m = song song r3b. 1 quan sát (k đo 6T FY26); ngược có số: H2 k=2,958 bất thường (HTK 25% TMĐT dù 'xong thô', R3B:65-71) ⇒ k đo kém tin cậy ⇒ nhánh ngược"),
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
# tương tác (chỉ kiểm, không thay tâm): khi biên 42,7%, NOXH và dạng chính xác co theo (g−0,10)/(0,519−0,10) = 0,780 (m=0,8(g−0,10), S1 data_provenance)
f = (0.427 - 0.10) / (0.519 - 0.10)
pg = 0.35; pn, pe = 0.5, 0.35; mg, mn, me = (it["mag_pct"] / 100 for it in items)
s_int = pg * mg + pn * mn * (pg * f + (1 - pg)) + pe * me * (pg * f + (1 - pg))
sens = [
 dict(name="NOXH NC-II (chưa biết tỷ trọng; TM19 đặt cọc thuê NOXH An Hải 57,2 tỷ)", dir="down", evidence_tier="C",
      sensitivity="tỷ trọng 10–20%% ⇒ −288…−576 đ (%.2f…%.2f%%)" % (pv(-288), pv(-576)), source=f"{S0}:13; {NR}:36", why_not_center="chưa có văn bản xác nhận NC-II có NOXH ⇒ dấu chưa chắc"),
 dict(name="Quỹ KTPL trích từ thặng dư tương lai", dir="down", evidence_tier="C",
      sensitivity="5%% × ~5.700 tỷ ⇒ ≈−1,8%% (skeptic); mỗi 1pp ≈ −0,36%%", source=f"{S1}:13,'missing_items'; {NR}:50",
      why_not_center="không có cận từ dữ liệu: TM34 'chưa trích quỹ KTPL', bảng CĐKT không có dòng tồn quỹ ⇒ cận bảo thủ = 0"),
 dict(name="Tiền gửi HTM 678,3 tỷ 'Sài Gòn Tài Lộc' chưa xác minh", dir="down", evidence_tier="C",
      sensitivity="mất 100%% ⇒ −670 đ (%.2f%%)" % pv(-670), source=f"{R3B}:114; {S1}", why_not_center="không có dữ liệu xác suất mất"),
 dict(name="H2 k=2,958 bất thường (chặn k_H2=1)", dir="down", evidence_tier="C",
      sensitivity="15.568 (%.2f%%)" % pv(15568 - C), source=f"{R3B}:70-71", why_not_center="cùng trục k với hạng mục dạng chính xác; đã dùng làm quan sát ngược ở đó — không đếm hai lần"),
 dict(name="Thu tiền theo tiến độ trước mốc hoàn thành (người mua trả trước 5.599,8 tỷ); giá bán không tăng tới 2030; quỹ đất mới NPV0", dir="up", evidence_tier="C",
      sensitivity="chưa định lượng", source=f"{S1}:'symmetry'", why_not_center="không có số"),
 dict(name="[LUẬT] CK holding: dải user chốt 0…+20% (đo cho HHS); base 0%", dir="down", evidence_tier="rule",
      sensitivity="+20%% ⇒ 14.294 (%.2f%%); 27%% ⇒ 13.745" % pv(14294 - C), source=f"{RR}:21,59", why_not_center="tham số house (Bước 0), user chưa chốt áp cho TCH"),
 dict(name="[LUẬT] r 13,5% vs dải Ke (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3%% ⇒ 16.270 (+2,56%%); 13,4%% ⇒ +0,21%%", source=f"{RR}:42-45"),
 dict(name="[LƯỚI] y=4 mọi dự án, k=0 (bản skeptic)", dir="down", evidence_tier="rule", sensitivity="13.435 (%.2f%%)" % pv(13435 - C), source=f"{R3B}:94", why_not_center="trọng số/trục lưới kịch bản = luật"),
]
ca, lo, hi = (round(C * (1 + s)) for s in (s_c, s_lo, s_hi))
def dc(dp): return round(C * dp / 100)
trig = [
 dict(event="Báo cáo soát xét 6T FY26 (AASC): biên BĐS xác nhận ≈51,9%", when="ước lượng 11–12/2026 (hạn soát xét bán niên; chưa xác minh đã công bố)", direction="up",
      delta_vnd=dc((0.15 - 0.35) * mg * 100), delta_pct=round((0.15 - 0.35) * mg * 100, 2), note="quan sát ngược thành số soát xét ⇒ p biên 0,35→0,15"),
 dict(event="Báo cáo soát xét 6T FY26: biên điều chỉnh xuống ≤45%", when="ước lượng 11–12/2026", direction="down",
      delta_vnd=dc((0.90 - 0.35) * mg * 100), delta_pct=round((0.90 - 0.35) * mg * 100, 2), note="mất quan sát ngược, 3 kỳ cùng hướng có số trực tiếp ⇒ p→0,90"),
 dict(event="BCTC Q3 FY26 (quý đến 31/12/2026): biên BĐS quý ≥50% / ≤45%", when="cuối 01/2027", direction="both",
      delta_vnd=None, delta_pct=None, note="thêm 1 kỳ cho phía tương ứng; nhánh vẫn 'ngược' (có số cả hai phía) ⇒ p không đổi theo thang; ghi nhận, đổi khi FY26 kiểm toán"),
 dict(event="BCTC FY26 kiểm toán (năm đến 31/03/2027): biên BĐS ≥50%", when="ước lượng 06/2027", direction="up",
      delta_vnd=dc((0.15 - 0.35) * mg * 100), delta_pct=round((0.15 - 0.35) * mg * 100, 2), note="kỳ kiểm toán đầu tiên chủ yếu NC-II ⇒ p 0,15"),
 dict(event="BCTC FY26 kiểm toán: biên BĐS ≤45%", when="ước lượng 06/2027", direction="down",
      delta_vnd=dc((0.90 - 0.35) * mg * 100), delta_pct=round((0.90 - 0.35) * mg * 100, 2), note="p 0,90"),
 dict(event="QĐ đầu tư/BCTN: tỷ trọng chi phí NOXH Green River", when="khi đọc được BCTN25/QĐ dự án", direction="down",
      delta_vnd=dc(0.9 * pv(-480) - 0.5 * pv(-274)), delta_pct=round(0.9 * pv(-480) - 0.5 * pv(-274), 2), note="C+→A ở 35%% (441/1.251 căn), p 0,9; nếu 20%% ⇒ %.2f%%" % (0.9 * pv(-274) - 0.5 * pv(-274))),
 dict(event="Văn bản xác nhận NC-II có quỹ đất NOXH 20%", when="khi có", direction="down",
      delta_vnd=dc(0.9 * pv(-288)), delta_pct=round(0.9 * pv(-288), 2), note="C→A, mỗi 10% tỷ trọng −288 đ × 0,9"),
 dict(event="NQ ĐHĐCĐ (FY26, ~06–07/2027): tỷ lệ trích KTPL", when="ước lượng 06–07/2027", direction="down",
      delta_vnd=dc(0.9 * -1.8), delta_pct=round(0.9 * -1.8, 2), note="C→A ví dụ 5%; mỗi 1pp ≈ −0,36%×0,9"),
 dict(event="Xác minh đối tác HTM 678,3 tỷ là TCTD được cấp phép", when="khi đọc PDF gốc", direction="none", delta_vnd=0, delta_pct=0, note="đóng hạng mục; nếu KHÔNG phải TCTD ⇒ stress −670 đ chuyển thành hạng mục B"),
 dict(event="User chốt CK holding áp cho TCH ở +20%", when="khi user quyết", direction="down", delta_vnd=14294 - C, delta_pct=round(pv(14294 - C), 2), note="đổi luật ⇒ chạy lại, không cộng tay"),
 dict(event="Lãi huy động 12T ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_vnd=-164, delta_pct=-1.03, note="+50bp −164; −50bp +167 (REPORT_recheck:44,47)"),
]
out = dict(ticker="TCH", dd_date="2026-10-31", rev=5, asof="2026-11-24", job="Taylor_20261124_110049",
           prereg_md5=dict(PREREG_adj="ef5157cb3f762d58623ed550ebc214c7", PREREG_adj_v2="835dfc1e07f9c67ac7f6c3028b529d13"), blind_to_price=True,
           center_base=C, center_base_source="kb/dd_price_zones.json TCH rev5 center (sau CK 5 tỷ)",
           items=items, sum_p_m_pct=round(s_c * 100, 3), aggregation="linear (|Σ|≤5%)",
           interaction_check=dict(sum_with_margin_scaling_pct=round(s_int * 100, 3), center=round(C * (1 + s_int)), note="NOXH/dạng chính xác co 0,780 khi biên 42,7%; chỉ kiểm, không thay tâm"),
           center_adj=ca, range_low=lo, range_high=hi,
           dividend_mech=dict(vnd=0, status="không có cổ tức tiền đã công bố chưa GDKHQ trong nguồn (thưởng 10:1 đã thực hiện 10/09/2026)"),
           sensitivity_only=sens, trigger_table=trig,
           flags=["FLOOR_FAIL (CF_OA_3Y −771,7 tỷ) — không vào candidate bất kể tâm"],
           caveat="cộng tuyến tính; m NOXH là stress skeptic trên r3 (ước lượng); m biên/dạng chính xác là song song mô hình r3b")
assert 0 < lo <= ca <= hi
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "sum_p_m_pct", "interaction_check"]}, ensure_ascii=False))
for it in items: print(it["evidence_tier"], it["p"], it["mag_pct"], it["mag_range_pct"], it["contrib_pct"], it["name"][:60])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"][:70])
