"""Tâm kỳ vọng điều chỉnh DRI — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). Mù giá: không đọc giá cổ phiếu.
Job Taylor_20261124_110052 (fan-out g2). Số m lấy từ output engine r3 (sổ rev4) đã khoá md5; không chạy lại engine (|Σ|<5%)."""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(os.path.join(HERE, "..", "PREREG_adj.md")) == "ef5157cb3f762d58623ed550ebc214c7"
assert md5(os.path.join(HERE, "..", "PREREG_adj_v2.md")) == "835dfc1e07f9c67ac7f6c3028b529d13"
RC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_recheck_20261124/DRI"
O3 = RC + "/calc/mirror/dd_redo_20261105/DRI/calc/dri_redo_r3_out.txt"
S, S2 = RC + "/skeptic/r1_raw.md", RC + "/calc/mirror/dd_redo_20261105/DRI/SUMMARY_r2.json"
assert md5(O3) == "6c55c8ed972236a85fe94f568fb46900" and md5(S) == "173753a762e36b112e664d1391de6f99" and md5(S2) == "3443c3da61c98abfac1fd33772a3504d"
rel = lambda p: p.split("mike/")[1]
o3, s, s2, rr = rel(O3), rel(S), rel(S2), rel(RC + "/REPORT_recheck_DRI.md")
C, SH, CK = 15257, 73.2e6, 0.02          # sổ rev4 center (sau CK 2,00% @5 tỷ); SH khớp BQ OShares (S:4)
P = {"A": (0.90, 0.75, 1.00), "B1": (0.50, 0.25, 0.75), "B3": (0.65, 0.40, 0.90), "Bneg": (0.35, 0.15, 0.55)}
pc = lambda vnd: vnd / C * 100
# KTPL: giá trị vận hành ∝ (1−KTPL−TAU)·0,9 (wht=10%×(1−KTPL−TAU), assumptions_r3 wht_basis); TAU 7,8%
k_ratio = (1 - 0.099 - 0.078) / (1 - 0.106 - 0.078) - 1
op_share = (15568 - 236.7e9 / SH - 72.71e9 / SH) / 15568   # phần vận hành ≈ tâm trước CK − tiền ròng 236,7 tỷ − XDCB 72,71 tỷ (ước lượng)
items = [
 dict(name="Haircut khoản cho Dakruco vay 40 tỷ (TSĐB = 6 tr cp DRI, rủi ro cùng chiều)", dir="down", tier="B", rung="Bneg",
      m_lo=pc(-268), m_hi=pc(-536), m_basis="engine r3: haircut 50% −268, mất trắng −536 (sau CK) — ước lượng khoảng; tâm m = trung điểm",
      p_basis="1 quan sát ủng hộ (khoản vay phải gia hạn, REPORT_recheck:77) + quan sát NGƯỢC có số (đã trả đúng hạn 80→40 tỷ H1, SUMMARY_r2:84) ⇒ nhánh ngược",
      source=f"{o3} ('haircut 50%', 'mat trang'); {s}:13; {s2}:84,136; {rr}:77"),
 dict(name="Tỷ lệ KTPL 10,6% (FY25) → 9,9% (mẫu 9T26)", dir="up", tier="B", rung="B1",
      m_lo=k_ratio * 100 * 0.5, m_hi=k_ratio * 100, m_basis="(1−0,099−0,078)/(1−0,106−0,078)−1 = +%.2f%% trên phần vận hành; tâm m = × phần vận hành %.0f%% (ước lượng); cận dưới = ½" % (k_ratio * 100, op_share * 100),
      m_mid=k_ratio * 100 * op_share, p_basis="1 quan sát (9T26, 1 kỳ) ⇒ mặc định B",
      source=f"{s}:33 (too_low 'KTPL 16,68/157,4 = 10,6% … 9,9%'); assumptions_r3.json wht_basis"),
]
s_c = s_lo = s_hi = 0.0
for it in items:
    p, plo, phi = P[it.pop("rung")]
    mm = it.pop("m_mid", (it["m_lo"] + it["m_hi"]) / 2)
    it.update(mag_pct=round(mm, 3), mag_range_pct=[round(it.pop("m_lo"), 3), round(it.pop("m_hi"), 3)], p=p, p_low=plo, p_high=phi,
              evidence_tier=it.pop("tier"), counted_in_center_bool=True, contrib_pct=round(p * mm, 3))
    cands = [a * b for a in (plo, phi) for b in it["mag_range_pct"]]
    s_c += p * mm / 100; s_lo += min(cands) / 100; s_hi += max(cands) / 100
assert abs(s_c) <= 0.05   # PREREG v2 §5: |Σ|≤5% ⇒ cộng tuyến tính được
ca, lo, hi = round(C * (1 + s_c)), round(C * (1 + s_lo)), round(C * (1 + s_hi))
obl10 = 10e9 / SH * (1 - CK)
sens = [
 dict(name="Đất tô nhượng Lào 01616/KĐ/DDT4 + nghĩa vụ trả/trồng bù rừng bảo tồn Đông Huê Sáo (D3)", dir="down", evidence_tier="C",
      sensitivity="(a) trả đất SAU chu kỳ 1: ≈0 (tái canh chu kỳ 2 đã = NPV0 theo luật 20); (b) chi tuân thủ bắt buộc: mỗi 10 tỷ PV = −%d đ/cp (%.2f%%); (c) trả đất TRƯỚC hết đời cạo: mỗi 1.000 ha mất ngay ≈ −%.1f%% (ước lượng cận trên: 1.000/8.166 ha × phần vận hành %.0f%%)" % (round(obl10), -pc(obl10), 1000 / 8166 * op_share * 100, op_share * 100),
      why="Không có diện tích chồng lấn / chi phí trồng bù trong tài liệu công bố ⇒ không có dấu chắc + cận bảo thủ (cận = 0) ⇒ C, không phải C+",
      source=f"{s}:12,36; dd_DRI_20261027/investor_report_v4/DRI_DD_investor_report_20261103.md:178"),
 dict(name="Trục q khối thanh lý 1.975 ha [UL]", dir="both", evidence_tier="C", sensitivity="q 0,7 cố định +652 (+4,27%); q 1,0 −652; q 0,5 +1.522",
      why="Chỉ có dữ liệu định tính 'q<1' (đã vào lưới 0,7/0,85/1)", source=f"{o3} ('q khoi'); {s}:14"),
 dict(name="FCF/LN lõi 90% [UL] vs CFO TTM yếu", dir="both", evidence_tier="C", sensitivity="80% −936 (−6,13%); 100% +936",
      why="3 kỳ TTM không chồng (Q3/24, Q3/25, Q3/26) CFO/LNST = 1,36 / 0,91 / 0,48 — NGƯỢC chiều nhau, trung bình 0,92 ≈ base; Q3/26 thấp do giữ hàng (thành phẩm 138,8 tỷ)",
      source="dd_recheck_20261124/DRI/calc/v6_bq.csv (BQ ticker_financial); " + s + ":16"),
 dict(name="wht 8,16% vs quan sát 7,04% (2025) / 8,30% (2024)", dir="both", evidence_tier="C", sensitivity="7,04% +159; 8,30% −20; 10% phẳng −260",
      why="Base nằm TRONG dải 2 quan sát, hai quan sát ngược chiều", source=f"{o3} ('wht'); assumptions_r3.json wht_basis"),
 dict(name="Giữ lại 15% tiền tại Lào (~197 tỷ)", dir="down", evidence_tier="C", sensitivity="−395 (−2,59%)",
      why="Dấu chắc (0% đã là trần) nhưng không có số quan sát về tỷ lệ giữ lại ⇒ cận bảo thủ = 0", source=f"{o3} ('giu 15%'); {s2}:88"),
 dict(name="Trục wp PEAK giá cao su (E16 ĐỈNH LỢI NHUẬN?)", dir="both", evidence_tier="C", sensitivity="mỗi 0,1 wp ∓76; wp 0 +382; wp 1 −382",
      why="Phân vị giá RSS3 thực phụ thuộc cửa sổ: 2014–26 ≈89% (investor_report:22) nhưng 2006–26 = 56% (đo lại từ rubber_monthly_snapshot + CPI trong mirror) ⇒ không có hướng",
      source=f"{o3} ('wp PEAK'); calc/mirror/dd_DRI_20261027/r5/calc/data/rubber_monthly_snapshot_20261103.csv"),
 dict(name="Giá gỗ LAK ±10%", dir="both", evidence_tier="C", sensitivity="±164 (±1,07%)", why="Tỷ giá, không có hướng", source=o3),
 dict(name="GPM về peer 25%", dir="down", evidence_tier="C", sensitivity="−20,6% (ADDENDUM_5F)",
      why="Bị dữ liệu bác: GPM lịch sử chính DRI 28–43%, tb ~37% (skeptic tự kiểm BQ)", source=f"{s}:9"),
 dict(name="Gia hạn tô nhượng sau 2054", dir="up", evidence_tier="C", sensitivity="≈0 dưới luật NPV0 chu kỳ 2; nếu chu kỳ 2 có NPV>0 thì ≤ +1,6% (ước lượng: chiết khấu 28 năm @13,5% ≈ 0,03)",
      why="Văn bản tô nhượng chưa công khai", source=f"{s}:15"),
 dict(name="Ý kiến kiểm toán BCTC FY2025", dir="both", evidence_tier="C", sensitivity="chưa ghi; nếu ngoại trừ ⇒ chuyển hạng mục liên quan C→A", why="Báo cáo recheck không nêu", source=f"{s}:32"),
 dict(name="[LUẬT] r 13,5% vs dải Ke 12,3–13,4% (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3% ⇒ 15.713 (+2,99%); 13,4% ⇒ 15.294 (+0,24%)",
      why="Tham số luật V1 (PREREG v2 §4), không vào Σ", source=f"{rr}:14,38-44"),
 dict(name="[LUẬT] tái canh = NPV0 (RONIC=Ke) — hai chiều", dir="both", evidence_tier="rule",
      sensitivity="nhánh KINH TẾ 0,1/0,2/0,3 ⇒ −164/−329/−494; chiều lên (đất không mất tiền thuê) chưa lượng hoá", why="Luật 20 / V5", source=o3),
 dict(name="Cổ tức", dir="none", evidence_tier="mech", sensitivity="Cổ tức 2025 1.000 đ ĐÃ chi từ 20/10/2026 (đã GDKHQ); chưa có cổ tức mới công bố ⇒ một dòng", why="PREREG v2 §6",
      source="dd_redo_20261105/DRI/REPORT.md:20; investor_report_v4:104"),
]
dv = lambda pct: round(C * pct / 100)
mD, mK = items[0]["mag_pct"], items[1]["mag_pct"]
trig = [
 dict(event="BCTC Q4/2026 hoặc CBTT: Dakruco trả nốt 40 tỷ", when="ước lượng cuối 01/2027 (lịch chưa xác minh)", direction="up", delta_vnd=dv(-0.35 * mD), delta_pct=round(-0.35 * mD, 2), note="hạng mục Dakruco hết (p→0)"),
 dict(event="BCTC Q4/2026: Dakruco gia hạn tiếp / quá hạn / DRI trích dự phòng", when="ước lượng cuối 01/2027", direction="down", delta_vnd=dv((0.9 - 0.35) * mD), delta_pct=round((0.9 - 0.35) * mD, 2), note="p 0,35→0,90; nếu trích dự phòng có số ⇒ thay m bằng số đó"),
 dict(event="Văn bản tô nhượng / thuyết minh BCTN: diện tích rừng bảo tồn phải trả + chi trồng bù", when="khi công bố (BCTN 2026 ước lượng 04/2027) hoặc legal-vn tra", direction="down", delta_vnd=-round(obl10), delta_pct=round(-pc(obl10), 2), note="mỗi 10 tỷ PV nghĩa vụ; trả đất trước hết đời cạo: chạy lại engine với A0 − X ha"),
 dict(event="BCTC kiểm toán 2026: tỷ lệ KTPL cả năm ≤10%", when="ước lượng 03/2027", direction="up", delta_vnd=dv(0.4 * mK), delta_pct=round(0.4 * mK, 2), note="p 0,5→0,9"),
 dict(event="BCTC kiểm toán 2026: tỷ lệ KTPL ≥10,6%", when="ước lượng 03/2027", direction="down", delta_vnd=dv(-0.5 * mK), delta_pct=round(-0.5 * mK, 2), note="p→0"),
 dict(event="Kết quả đấu giá 1.975 ha (giá trúng vs khởi điểm 36 tr LAK/ha; danh tính bên trúng)", when="theo lịch đấu giá NQ15", direction="both", delta_vnd=164, delta_pct=1.07, note="mỗi +10% giá gỗ ≈ +164; bên trúng là bên liên quan (Dakruco/Dakruwood) ⇒ WARNING quản trị"),
 dict(event="HĐQT 12/2026: mua Dakruwood từ Dakruco (bên liên quan)", when="12/2026", direction="down", delta_vnd=-round(obl10), delta_pct=round(-pc(obl10), 2), note="mỗi 10 tỷ trả cao hơn giá trị sổ/NPV0"),
 dict(event="BCTN 2026: năng suất khối thanh lý", when="ước lượng 04/2027", direction="both", delta_vnd=652, delta_pct=4.27, note="q 0,7 ⇒ +652; q 1,0 ⇒ −652 (C→A)"),
 dict(event="Lãi huy động 12T hiệu dụng ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_vnd=-180, delta_pct=-1.18, note="+50bp −180; −50bp +186"),
 dict(event="Ý kiến kiểm toán FY2025/FY2026 có ngoại trừ", when="khi đọc BCKT", direction="down", delta_vnd=None, delta_pct=None, note="khoản ngoại trừ có số ⇒ A, trừ theo đ/cp"),
]
out = dict(ticker="DRI", dd_date="2026-11-03", rev=4, asof="2026-11-24", prereg_md5="ef5157cb3f762d58623ed550ebc214c7", prereg_v2_md5="835dfc1e07f9c67ac7f6c3028b529d13",
           blind_to_price=True, center_base=C, center_base_source="kb/dd_price_zones.json DRI rev4 (center sau CK 2,00% @5 tỷ)",
           items=items, sum_p_m_pct=round(s_c * 100, 3), combination_rerun=False,
           center_adj=ca, range_low=lo, range_high=hi, dividend_rights="không còn quyền chưa chốt (cổ tức 2025 đã chi 20/10/2026)",
           sensitivity_only=sens, trigger_table=trig,
           caveat="cộng tuyến tính (|Σ|<5%); m Dakruco = trung điểm khoảng engine; m KTPL ước lượng theo phần vận hành")
assert 0 < lo <= ca <= hi
json.dump(out, open(os.path.join(HERE, "adj.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["center_adj", "range_low", "range_high", "sum_p_m_pct"]}))
for it in items: print(it["evidence_tier"], it["p"], it["mag_pct"], it["mag_range_pct"], it["contrib_pct"], it["name"])
for t in trig: print(t["delta_vnd"], t["delta_pct"], t["event"])
print("op_share", round(op_share, 4), "k_ratio", round(k_ratio * 100, 3), "obl10", round(obl10))
