"""Tâm kỳ vọng điều chỉnh NNC — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). Mù giá: không đọc giá thị trường.
Σ dự kiến > ~4% và có 3 hạng mục dòng tiền ⇒ tâm lấy từ CHẠY LẠI mô hình tổ hợp (rerun_combo.py, v2 §5) thay vì cộng tuyến tính;
hạng mục ngoài mô hình (chân MVC) cộng tuyến tính sau. Chạy: python3 calc_adj.py"""
import json, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(HERE, '..', 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(HERE, '..', 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
RR = json.load(open(os.path.join(HERE, 'rerun_combo_out.json'))); K = RR['cases']
C = 61273; assert RR['control_center'] == C           # kb/dd_price_zones.json NNC rev6 center
SH = 21.92e6
S = "agents/Taylor/research/dd_recheck_20261124/NNC/skeptic/r1_raw.md"
RP = "agents/Taylor/research/dd_recheck_20261124/NNC/REPORT_recheck_NNC.md"
FP = "/tmp/ddrestore_B/agents/Taylor/research/dd_NNC_20261030/src/fpts_nnc_init_20260107.txt (git 14ad1c925^/ef7472f56^)"
R2 = "agents/Taylor/research/dd_redo_20261105/NNC/REPORT_r2.md"
BQ = "BQ tav2_bq.ticker_financial NNC NP_P0 theo quý (LNST 2023 36,61 / 2024 62,62 / 2025 147,84 tỷ)"
TB = {'A': (0.90, 0.75, 1.00), 'B1': (0.50, 0.25, 0.75), 'B3': (0.65, 0.40, 0.90), 'Bneg': (0.35, 0.15, 0.55)}
# chân MVC (ngoài mô hình): +556 đ/cp MVC (redo MVC r3 vá trần chu kỳ) × 10,3 tr cp × 1/(1-0,103×0,4407) / 21,92 tr × CK 61273/63591
m_mvc = 556 * 10.3e6 / (1 - 0.103 * 0.4407) / SH * (61273 / 63591) / C * 100
items = [
 dict(name="Trích quỹ KTPL hằng năm từ LNST 2026–2043 chưa trừ (C+ — cận bảo thủ)", dir="down", evidence_tier="C+", rung="B1",
      mag_pct=K['KT_4.6']['d_pct'], mag_range_pct=[K['KT_4.6']['d_pct'], K['KT_8.2']['d_pct']],
      note="Dấu chắc chắn. Cận dưới tỷ lệ = Δtồn quỹ/LNST kỳ trước (chi quỹ ≥0 ⇒ trích ≥ Δtồn): 2024: (7−4)/36,61 = 8,2%; 2025–9T26: (16,78−7)/(62,62+147,84) = 4,6%. "
           "Vào tâm ở 4,6% (cận bảo thủ), dải m tới 8,2%. 2 kỳ ⇒ p mặc định B. m đo bằng chạy lại mô hình (thuế hiệu dụng NNC + trừ KT×LN 2026).",
      source=f"{S}:11; {FP}:2038 (tồn quỹ 2023A 4 / 2024A 7); BCTC Q3/26 tr.3 16,78 ({RP}:100); {BQ}"),
 dict(name="Capex duy trì > khấu hao (giả định 'capex ≈ KH' không nguồn)", dir="down", evidence_tier="B", rung="B3",
      mag_pct=K['G_7.5']['d_pct'], mag_range_pct=[0.0, K['G_19']['d_pct']],
      note="Capex: 2022 23 / 2023 19 / 2024 23 / 2025 54 tỷ (FPTS); KH: 2023 7 / 2024 10 tỷ (FPTS), Q3/26 5,56 tỷ/quý ⇒ 22,2/năm (BCTC VI.9). "
           "3 kỳ cùng hướng có số (2023 +12, 2024 +13, 2025 ≥+32) ⇒ p 0,65. m ước lượng: khoảng hở 7,5 tỷ/năm = capex TB 2022–25 29,75 − KH 22,2 [0; 19 = TB 3 khoảng hở cùng năm].",
      source=f"{S}:12; {FP}:1323-1330,2203 + bảng LCTT 'Đầu tư TSCĐ'; agents/Taylor/research/dd_NNC_20261026/REPORT.md:86-88"),
 dict(name="LNST Q4/26 ước 60 tỷ thấp hơn nhịp quý (Q3/26 thực 69,29)", dir="up", evidence_tier="B", rung="Bneg",
      mag_pct=K['Q4_flat']['d_pct'], mag_range_pct=[0.0, K['Q4_seasonal']['d_pct']],
      note="Q4/Q3: 2024 1,28; 2025 1,27 (lên) — 2023 0,92 (ngược, có số) ⇒ nhánh ngược. m: Q4 = Q3 (phẳng, +9,29 tỷ) [0; Q3×1,275 = +28,3 tỷ].",
      source=f"{BQ} quý 2023Q3–2025Q4; {S}:37 (n_q4 60 là ước lượng)"),
 dict(name="Chân MVC 10,3% dùng engine MVC r6 chưa vá trần chu kỳ", dir="up", evidence_tier="B", rung="B1",
      mag_pct=m_mvc, mag_range_pct=[0.0, m_mvc],
      note="Vá D1 ở MVC redo r3 = +556 đ/cp MVC (sau CK). Quy về NNC qua hệ sở hữu chéo (×1/(1−0,103×0,4407)) và CK NNC; ước lượng, có thể đã vá một phần trong NNC r3 ⇒ cận dưới 0.",
      source=f"{S}:18,36; agents/Taylor/research/dd_redo_20261105/MVC/REPORT_r3.md:22"),
 dict(name="Truy thu Núi Nhỏ ~42 tỷ vs dự phòng 22,37 — ĐÃ PHỦ ĐỦ", dir="none", evidence_tier="A", rung="A", mag_pct=0.0, mag_range_pct=[0.0, 0.0],
      note="42 = dự phòng 15,58 + 5,95 (nằm trong 22,37, đã trừ ở tiền ròng) + 20,43 đã nộp 2026 (đã ra khỏi tiền). Khoảng hở skeptic (≤1,5%) đóng = 0.",
      source=f"{S}:13; {R2}:60; agents/Taylor/research/dd_NNC_20261030/archive_internal/REPORT_v2_20261031.md:93,202"),
]
lin_c = lin_lo = lin_hi = 0.0
for it in items:
    p, plo, phi = TB[it.pop('rung')]
    m, (ma, mb) = it['mag_pct'] / 100, (x / 100 for x in it['mag_range_pct'])
    cands = [a * b for a in (plo, phi) for b in (ma, mb)]
    it.update(p=p, p_low=plo, p_high=phi, counted_in_center_bool=True, contrib_pct=round(p * m * 100, 3),
              mag_pct=round(it['mag_pct'], 3), mag_range_pct=[round(x, 3) for x in it['mag_range_pct']])
    lin_c += p * m; lin_lo += min(cands); lin_hi += max(cands)
mvc = items[3]; pm = mvc['p'] * mvc['mag_pct'] / 100; pm_lo = 0.0; pm_hi = mvc['p_high'] * mvc['mag_pct'] / 100
ca = round(K['COMBO_center']['center'] * (1 + pm)); lo = round(K['COMBO_low']['center'] * (1 + pm_lo)); hi = round(K['COMBO_high']['center'] * (1 + pm_hi))
assert 0 < lo <= ca <= hi
sens = [
 dict(name="[LUẬT] r 13,5% vs dải Ke 12,3–13,4% (E15)", dir="up", evidence_tier="rule", sensitivity="Ke 12,3% ⇒ 63.725 (+4,00%); 13,4% ⇒ 61.467 (+0,32%)", source=f"{RP}:76-80"),
 dict(name="Đối thủ hết GP từ 2034", dir="up", evidence_tier="C", sensitivity="+4.367 đ/cp (+7,13%)", source=f"{S}:20"),
 dict(name="ADMIN perm05", dir="up", evidence_tier="C", sensitivity="+4.962 đ/cp (+8,10%)", source=f"{S}:21"),
 dict(name="Trả trước dài hạn CNBP là tiền thuê", dir="up", evidence_tier="C", sensitivity="+2.126 đ/cp (+3,47%)", source=f"{S}:22"),
 dict(name="Trọng số STRUCTURAL 0,20 → 0,30", dir="up", evidence_tier="C", sensitivity="≈ +4,8%", source=f"{S}:23"),
 dict(name="Truy thu lan sang mỏ lõi Mũi Tàu (E12; dự phòng 0,84, CQKTKS 1,735 tỷ)", dir="down", evidence_tier="C", sensitivity="chưa có cơ sở độ lớn ngoài 0,84 đã trừ", source=f"{RP}:106"),
 dict(name="Chi PHMT/đóng mỏ 2043 ngoài 4,50", dir="down", evidence_tier="C", sensitivity="không trọng yếu (hệ số chiết khấu ≈0,12)", source=f"{S}:14"),
 dict(name="Pháp lý (MVC 44,07% + uỷ quyền 51%/D195; NHC 61% phải thu)", dir="down", evidence_tier="warning", sensitivity="WARNING, không vào tâm", source=f"{RP}:106"),
]
def dv(pct): return round(C * pct / 100)
kt_slope = (K['KT_8.2']['d_pct'] - K['KT_4.6']['d_pct']) / 3.6   # %/pp
def kt_m(rate_pct): return K['KT_4.6']['d_pct'] + (rate_pct - 4.6) * kt_slope
cur_kt = 0.5 * K['KT_4.6']['d_pct']; cur_g = 0.65 * K['G_7.5']['d_pct']; cur_q4 = 0.35 * K['Q4_flat']['d_pct']
trig = [
 dict(event="Đọc thuyết minh VCSH BCTC kiểm toán 2025 (KT25, đã công bố) — số trích KTPL từ LN 2024", when="có thể làm ngay", direction="down",
      delta_pct=round(0.9 * kt_m(8.2) - cur_kt, 2), delta_vnd=dv(0.9 * kt_m(8.2) - cur_kt), note="ví dụ tỷ lệ 8,2%%: C+→A p 0,9; mỗi 1pp ≈ %.2f%%×0,9" % kt_slope),
 dict(event="NQ ĐHĐCĐ 2027 phân phối LN 2026: tỷ lệ trích KTPL 5%", when="ước lượng 04/2027*", direction="down",
      delta_pct=round(0.9 * kt_m(5) - cur_kt, 2), delta_vnd=dv(0.9 * kt_m(5) - cur_kt), note="C+→A"),
 dict(event="NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL 10%", when="ước lượng 04/2027*", direction="down",
      delta_pct=round(0.9 * kt_m(10) - cur_kt, 2), delta_vnd=dv(0.9 * kt_m(10) - cur_kt), note="C+→A (ngoại suy tuyến tính từ 2 lần chạy)"),
 dict(event="BCTC Q4/2026: LNST Q4 ≥ 69 tỷ", when="ước lượng cuối 01/2027*", direction="up",
      delta_pct=round(0.9 * K['Q4_flat']['d_pct'] - cur_q4, 2), delta_vnd=dv(0.9 * K['Q4_flat']['d_pct'] - cur_q4), note="B→A"),
 dict(event="BCTC Q4/2026: LNST Q4 ≤ 60 tỷ", when="ước lượng cuối 01/2027*", direction="down",
      delta_pct=round(-cur_q4, 2), delta_vnd=dv(-cur_q4), note="hạng mục = 0"),
 dict(event="LCTT năm 2026: capex 2026 − KH 2026 ≥ 7,5 tỷ (kỳ thứ 4 cùng hướng)", when="ước lượng cuối 01/2027*", direction="down",
      delta_pct=round(0.9 * K['G_7.5']['d_pct'] - cur_g, 2), delta_vnd=dv(0.9 * K['G_7.5']['d_pct'] - cur_g), note="p 0,65→0,90"),
 dict(event="LCTT năm 2026: capex 2026 ≤ KH 2026 (quan sát ngược có số)", when="ước lượng cuối 01/2027*", direction="up",
      delta_pct=round(0.35 * K['G_7.5']['d_pct'] - cur_g, 2), delta_vnd=dv(0.35 * K['G_7.5']['d_pct'] - cur_g), note="p 0,65→0,35"),
 dict(event="Vá trần chu kỳ engine MVC r6 rồi chạy lại chân MVC trong NNC", when="khi có việc (nội bộ)", direction="up",
      delta_pct=round(0.4 * mvc['mag_pct'], 2), delta_vnd=dv(0.4 * mvc['mag_pct']), note="B→A p 0,9 (nếu đã vá sẵn: −%.2f%%)" % (0.5 * mvc['mag_pct'])),
 dict(event="Lãi huy động 12T hiệu dụng ±50bp (luật V1, β=1)", when="liên tục", direction="both", delta_pct=-1.54, delta_vnd=-944, note="−50bp ⇒ +988 (REPORT_recheck:78,81)"),
 dict(event="Văn bản truy thu mới chạm Mũi Tàu / D195 MVC", when="khi có", direction="down", delta_pct=0, delta_vnd=0, note="WARNING; có số tiền ⇒ trừ ở tiền ròng theo số (A)"),
]
out = dict(ticker="NNC", dd_date="2026-11-03", rev=6, asof="2026-11-24", prereg_md5="ef5157cb3f762d58623ed550ebc214c7", prereg_v2_md5="835dfc1e07f9c67ac7f6c3028b529d13",
           blind_to_price=True, center_base=C, center_base_source="kb/dd_price_zones.json NNC rev6 center (sau CK 3,65% @5 tỷ)",
           method="chạy lại mô hình r3 tổ hợp (rerun_combo.py; |Σ| gần ngưỡng 5%) cho KTPL/capex/Q4 + cộng tuyến tính chân MVC",
           rerun_md5=md5(os.path.join(HERE, 'rerun_combo_out.json')), items=items,
           sum_p_m_pct_linear=round(lin_c * 100, 3), sum_pct_combo=round((ca / C - 1) * 100, 3),
           center_adj=ca, range_low=lo, range_high=hi, range_low_linear=round(C * (1 + lin_lo)), range_high_linear=round(C * (1 + lin_hi)),
           dividend_mech=dict(status="không có cổ tức tiền đã công bố chưa GDKHQ trong nguồn (cổ tức phải trả 5,89 tỷ đã trừ ở tiền ròng)", vnd=0),
           center_adj_ex_div=ca, sensitivity_only=sens, trigger_table=trig,
           caveat="m KTPL/capex/Q4 đo bằng chạy lại mô hình (CONTROL trùng byte r3); m capex & Q4 là ước lượng có khoảng; chân MVC ước lượng tuyến tính; thu nhập tài chính không chịu KTPL trong hook (nhỏ)")
json.dump(out, open(os.path.join(HERE, 'adj.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ['center_adj', 'range_low', 'range_high', 'sum_p_m_pct_linear', 'sum_pct_combo', 'range_low_linear', 'range_high_linear']}))
for it in items: print(it['evidence_tier'], it['p'], it['mag_pct'], it['mag_range_pct'], it['contrib_pct'], it['name'])
for t in trig: print(t['delta_vnd'], t['delta_pct'], t['event'])
