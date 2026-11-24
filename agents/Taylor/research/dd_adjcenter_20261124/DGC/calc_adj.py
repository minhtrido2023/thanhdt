"""Tâm kỳ vọng điều chỉnh DGC — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). Mù giá.
Pháp lý (vụ án hình sự) theo luật 27/09: chỉ WARNING, KHÔNG vào tâm. Tâm lấy từ chạy lại mô hình tổ hợp (rerun_combo.py). Chạy: python3 calc_adj.py"""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(HERE, '..', 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(HERE, '..', 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
RR = json.load(open(os.path.join(HERE, 'rerun_combo_out.json'))); K = RR['cases']
C = 41849; assert RR['control_center'] == C            # kb/dd_price_zones.json DGC rev3 center
SH, S_EQ, F = 379779286, 0.029737431908924937, 1 - RR['ck']
S = "agents/Taylor/research/dd_recheck_20261124/DGC/skeptic/r1_raw.md"
RP = "agents/Taylor/research/dd_recheck_20261124/DGC/REPORT_recheck_DGC.md"
EX = "/tmp/ddrestore_B/agents/Taylor/research/dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md (git 60fe58b82^; md5 0e8288ee…)"
R3B = "agents/Taylor/research/dd_redo_20261105/DGC/REPORT_r3b.md"
TB = {'B1': (0.50, 0.25, 0.75)}
items = [
 dict(name="Trích quỹ KTPL hằng năm từ LNST (2026→vĩnh viễn) chưa trừ (C+ — cận bảo thủ)", dir="down", evidence_tier="C+", rung="B1",
      mag_pct=K['KT_lo']['d_pct'], mag_range_pct=[K['KT_lo']['d_pct'], K['KT_hi']['d_pct']],
      note="Mô hình chỉ trừ tồn quỹ 592,8 (stock). Quỹ tăng 405,7 → 592,8 (+187,1) trong Q3/26 — chi quỹ ≥0 ⇒ trích ≥ 187,1 trên LNST mẹ 2025 3.024,9 (BQ) = 6,19% (cận bảo thủ, 1 kỳ ⇒ p mặc định). "
           "Cận trên m dùng 10% = ước lượng (không có số DGC). m đo bằng chạy lại mô hình: core×(1−KT) + trừ KT×LNST mẹ 9T/26 1.267,10.",
      source=f"{EX}:35 (quỹ KTPL 592,8; 30/06 405,7); BQ ticker_financial DGC NP_P0 2025Q1–Q4; mô hình r3b value_ps (trừ FUND_KTPL)"),
 dict(name="EBIT lõi Q4/26 (base 9T/3 = 417,92 trước dự phòng) thấp hơn nhịp Q3 (481,21)", dir="up", evidence_tier="B", rung="B1",
      mag_pct=K['Q4_q3runrate']['d_pct'], mag_range_pct=[0.0, K['Q4_q3runrate']['d_pct']],
      note="Q3/26: LN gộp 506,35 − BH 76,18 − QLDN 48,96 + dự phòng 100 trong giá vốn = 481,21; H1 TB 386,3. Skeptic nghi Q4 'quá cao' vì gồm thời gian khai trường còn chạy — số Q3 (sau khi dừng) đi NGƯỢC nghi ngờ đó. 1 kỳ ⇒ p mặc định.",
      source=f"{EX}:8-17,35,40; {S}:34 (too_high 'Q4 lấy TB 9T <1%')"),
]
lin_c = lin_lo = lin_hi = 0.0
for it in items:
    p, plo, phi = TB[it.pop('rung')]
    m = it['mag_pct'] / 100; ma, mb = (x / 100 for x in it['mag_range_pct'])
    cands = [a * b for a in (plo, phi) for b in (ma, mb)]
    it.update(p=p, p_low=plo, p_high=phi, counted_in_center_bool=True, contrib_pct=round(p * m * 100, 3),
              mag_pct=round(it['mag_pct'], 3), mag_range_pct=[round(x, 3) for x in it['mag_range_pct']])
    lin_c += p * m; lin_lo += min(cands); lin_hi += max(cands)
ca, lo, hi = K['COMBO_center']['center'], K['COMBO_low']['center'], K['COMBO_high']['center']
assert 0 < lo <= ca <= hi
per1000 = round(1000e9 * (1 - S_EQ) / SH * F)       # đ/cp mỗi 1.000 tỷ ngoài lõi
def sv(k): return "%s (%+.2f%%)" % (f"{K[k]['center']:,}".replace(',', '.'), K[k]['d_pct'])
sens = [
 dict(name="[QUYẾT ĐỊNH USER 08/11 — cách B] biên vĩnh viễn nhánh mở lại khai trường 25", dir="up", evidence_tier="user_decision",
      sensitivity="w=0,5 CÓ biên vĩnh viễn ⇒ " + sv('S_ore_w0.5_term') + "; w=1 không biên ⇒ " + sv('S_ore_w1.0') + "; w=0 ⇒ " + sv('S_ore_w0'),
      source=f"{S}:15; {R3B}:5,13-15"),
 dict(name="[LUẬT] r 13,5% vs dải Ke 12,3–13,4% (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3% ⇒ 43.657 (+4,32%); 13,4% ⇒ 41.987 (+0,33%)", source=f"{RP}:72-76"),
 dict(name="[LUẬT D4] RONIC = Ke (thay vì 20%)", dir="up", evidence_tier="rule", sensitivity="RONIC 20% ⇒ " + sv('S_ronic20'), source=f"{S}:34"),
 dict(name="Ngoại trừ kiểm toán 2025: 950,9 tỷ tồn kho", dir="down", evidence_tier="C",
      sensitivity="mất toàn bộ ⇒ " + sv('S_inv_qual_full') + "; sau thuế ⇒ " + sv('S_inv_qual_full_aftertax') + "; cận dưới 0 (tồn kho có thật)", source=f"{S}:16; {R3B}:77"),
 dict(name="Giải phóng vốn lưu động: tồn kho 2.085,9 về mức YE25 1.681,9", dir="up", evidence_tier="C", sensitivity=sv('S_wc_release_to_YE25'), source=f"{S}:34; {EX}:32"),
 dict(name="Trục dự phòng môi trường 100 tỷ/quý (1/3 một lần · 1/3 bốn quý · 1/3 vĩnh viễn [UL])", dir="both", evidence_tier="C",
      sensitivity="một lần ⇒ " + sv('S_prov_mot_lan') + "; bốn quý ⇒ " + sv('S_prov_4q') + "; vĩnh viễn ⇒ " + sv('S_prov_vinh_vien'), source=f"{R3B}:91"),
 dict(name="Lá chắn thuế của dự phòng 0 [UL]", dir="up", evidence_tier="C", sensitivity="20% ⇒ " + sv('S_shield20'), source=f"{R3B}:40"),
 dict(name="Nền biên r4 thay R2 (đã đối chiếu: GPM Q3 trước dự phòng 24,6% ủng hộ R2)", dir="down", evidence_tier="C", sensitivity=sv('S_r4_fix'), source=f"{S}:34"),
 dict(name="HTM 9.531 chưa đối chiếu PDF gốc", dir="both", evidence_tier="C", sensitivity=f"mỗi 1.000 tỷ lệch ⇒ ∓{per1000:,} đ/cp".replace(',', '.'), source=f"{S}:10"),
 dict(name="Capex môi trường bắt buộc sau vụ án (bãi thải/xử lý nước/hoàn nguyên KT25)", dir="down", evidence_tier="C",
      sensitivity=f"mỗi 1.000 tỷ NPV âm ⇒ −{per1000:,} đ/cp (ngoài trục dự phòng đã có)".replace(',', '.'), source=f"{S}:16; {RP}:85"),
 dict(name="Nhà cung cấp quặng mua ngoài / bên liên quan", dir="down", evidence_tier="C", sensitivity="chưa có số", source=f"{S}:33"),
 dict(name="PHÁP LÝ — vụ án hình sự (luật 27/09: chỉ WARNING)", dir="down", evidence_tier="warning",
      sensitivity="trục haircut tiền ròng 3/9/29% (hiển thị) ⇒ " + sv('S_legal_axis') + "; KHÔNG vào tâm", source=f"{RP}:100; {S}:27"),
]
def dv(pct): return round(C * pct / 100)
kt_cur = items[0]['p'] * items[0]['mag_pct']; q4_cur = items[1]['p'] * items[1]['mag_pct']
pv_ = K['S_prov_vinh_vien']['d_pct']; p4 = K['S_prov_4q']['d_pct']
trig = [
 dict(event="Đọc thuyết minh 18 (quỹ KTPL) BCTC Q3/26 + NQ ĐHĐCĐ 2026: số trích thật từ LN 2025 = 10%", when="làm được ngay", direction="down",
      delta_pct=round(0.9 * K['KT_hi']['d_pct'] - kt_cur, 2), delta_vnd=dv(0.9 * K['KT_hi']['d_pct'] - kt_cur), note="C+→A p 0,9"),
 dict(event="… số trích thật = 6,2% (đúng cận dưới)", when="làm được ngay", direction="down",
      delta_pct=round(0.9 * K['KT_lo']['d_pct'] - kt_cur, 2), delta_vnd=dv(0.9 * K['KT_lo']['d_pct'] - kt_cur), note="C+→A p 0,9"),
 dict(event="BCTC soát xét bán niên 2026 (đã công bố): ngoại trừ tồn kho 950,9 còn/gỡ", when="làm được ngay", direction="down",
      delta_pct=round(0.9 * K['S_inv_qual_full_aftertax']['d_pct'], 2), delta_vnd=dv(0.9 * K['S_inv_qual_full_aftertax']['d_pct']),
      note="gỡ ⇒ 0; còn VÀ kiểm toán lượng hoá mất toàn bộ ⇒ C→A p 0,9 (sau thuế); mất một phần ⇒ tỷ lệ theo số"),
 dict(event="BCTC Q4/2026: không trích dự phòng môi trường mới", when="ước lượng cuối 01/2027*", direction="up",
      delta_pct=K['S_prov_mot_lan']['d_pct'], delta_vnd=K['S_prov_mot_lan']['d_vnd'], note="trục dự phòng → nhánh một lần (w=1)"),
 dict(event="BCTC Q4/2026: trích tiếp ≥100 tỷ", when="ước lượng cuối 01/2027*", direction="down",
      delta_pct=round((pv_ + p4) / 2, 2), delta_vnd=dv((pv_ + p4) / 2), note="loại nhánh một lần; bốn quý/vĩnh viễn 50/50"),
 dict(event="BCTC Q4/2026: EBIT lõi Q4 trước dự phòng ≥ 481 tỷ", when="ước lượng cuối 01/2027*", direction="up",
      delta_pct=round(0.9 * items[1]['mag_pct'] - q4_cur, 2), delta_vnd=dv(0.9 * items[1]['mag_pct'] - q4_cur), note="B→A"),
 dict(event="BCTC Q4/2026: EBIT lõi Q4 ≤ 418 tỷ", when="ước lượng cuối 01/2027*", direction="down",
      delta_pct=round(-q4_cur, 2), delta_vnd=dv(-q4_cur), note="hạng mục = 0"),
 dict(event="Văn bản thời hạn GP + trữ lượng KT25/19B", when="khi có", direction="up",
      delta_pct=K['S_ore_w0.5_term']['d_pct'], delta_vnd=K['S_ore_w0.5_term']['d_vnd'],
      note="CẬN TRÊN (vĩnh viễn). Biên hữu hạn theo thời hạn GP nằm giữa 0 và số này; đổi cách B là QUYẾT ĐỊNH USER, không tự áp. Quyết định đóng vĩnh viễn ⇒ " + str(K['S_ore_w0']['d_vnd'])),
 dict(event="Đối chiếu HTM 9.531 với PDF gốc", when="làm được ngay", direction="both", delta_pct=round(per1000 / C * 100, 2), delta_vnd=per1000, note="mỗi 1.000 tỷ lệch"),
 dict(event="NQ/công văn: capex môi trường bắt buộc", when="khi có", direction="down", delta_pct=round(-per1000 / C * 100, 2), delta_vnd=-per1000, note="mỗi 1.000 tỷ NPV âm; C→A"),
 dict(event="Lãi huy động 12T hiệu dụng ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_pct=-1.58, delta_vnd=-661, note="−50bp ⇒ +712 (REPORT_recheck:74,77)"),
 dict(event="Pháp lý: khởi tố pháp nhân / phạt, truy thu có số tiền", when="khi có", direction="down", delta_pct=0, delta_vnd=0,
      note="WARNING (luật 27/09). Có SỐ TIỀN phạt/truy thu ⇒ trừ tiền ròng theo số (A), không phải haircut"),
]
out = dict(ticker="DGC", dd_date="2026-10-30", rev=3, asof="2026-11-24", prereg_md5="ef5157cb3f762d58623ed550ebc214c7", prereg_v2_md5="835dfc1e07f9c67ac7f6c3028b529d13",
           blind_to_price=True, center_base=C, center_base_source="kb/dd_price_zones.json DGC rev3 center (sau CK 0,725% @5 tỷ)",
           method="chạy lại mô hình r3b tổ hợp (rerun_combo.py) — CONTROL 41.849 + 7 biến thể r3b tái lập đúng",
           rerun_md5=md5(os.path.join(HERE, 'rerun_combo_out.json')), items=items,
           sum_p_m_pct_linear=round(lin_c * 100, 3), sum_pct_combo=round((ca / C - 1) * 100, 3),
           center_adj=ca, range_low=lo, range_high=hi, range_low_linear=round(C * (1 + lin_lo)), range_high_linear=round(C * (1 + lin_hi)),
           dividend_mech=dict(status="cổ tức 8.000 đ/cp đã chi xong (phải trả 0,06 tỷ); không có quyền tiền mặt chưa GDKHQ trong nguồn", vnd=0),
           center_adj_ex_div=ca, legal="WARNING — vụ án hình sự (luật 27/09): phân tích trên BCTC, pháp lý không vào tâm",
           sensitivity_only=sens, trigger_table=trig,
           caveat="m KTPL & Q4 đo bằng mô hình; cận trên KTPL 10% là ước lượng; trục dự phòng/biên mở lại giữ nguyên [UL]/quyết định user")
json.dump(out, open(os.path.join(HERE, 'adj.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ['center_adj', 'range_low', 'range_high', 'sum_p_m_pct_linear', 'sum_pct_combo', 'range_low_linear', 'range_high_linear']}))
for it in items: print(it['evidence_tier'], it['p'], it['mag_pct'], it['mag_range_pct'], it['contrib_pct'], it['name'])
for s in sens: print('S', s['name'][:50], '|', s['sensitivity'])
for t in trig: print(t['delta_vnd'], t['delta_pct'], t['event'])
