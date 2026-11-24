"""MVC E17 — tam ky vong dieu chinh theo PREREG_adj (+v2); kiem ke khoa truoc: INVENTORY_adj_MVC.md. MU GIA.
Dau vao duy nhat: calc/calc_items_out.json (engine r3, tham so trung tam) + so NQ DHDCD 2026. Chay: python3 -I calc_adj.py"""
import hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); WT = os.path.abspath(os.path.join(HERE, '../../../../..'))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
PR = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124')
assert md5(os.path.join(PR, 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(PR, 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
assert md5(os.path.join(HERE, 'INVENTORY_adj_MVC.md')) == 'efee3d6721c790896c6cbae030fa82b9'
I = json.load(open(os.path.join(HERE, 'calc', 'calc_items_out.json')))
C0 = 16241; c0pre = I['c0_pre']; xh = I['cross_hold_factor']; R = 0.135
pct = lambda ty: -100 * ty * 10 * xh / c0pre          # ty (ty VND, PV) -> % tam (100 tr CP: 1 ty = 10 d/cp)
# #1 can bao thu: 11% x LNST rieng 2025 (122,521 ty, NQ:725-745), phang, 9 lan 2027..2035, chiet khau r
NP25 = 122.521054936; ann = (1 - (1 + R) ** -9) / R
m1_cons = round(pct(0.11 * NP25 * ann), 3)
m1_hi = round(I['fund11']['m_cons_pct'] + I['fund11']['m_9t26_pct'], 3)
nf = I['nnc_flow']; m2 = nf['d_mvc_pct'][f"{nf['m_nnc']:+.5f}"]; m2_lo = nf['d_mvc_pct'][f"{nf['m_nnc_lo']:+.5f}"]; m2_hi = nf['d_mvc_pct'][f"{nf['m_nnc_hi']:+.5f}"]
items = [
 dict(name='Trích quỹ 11% LNST hằng năm (KTPL 7% + HĐQT/BKS 2% + BĐH 2%) — C+ cận bảo thủ', dir='down', evidence_tier='C+',
      source='dd_MVC_20261103/txt/VI_BienBanHopDaiHoiDongCoDongThuongNien2026VaNghiQuyet.txt:725-785; skeptic/r1_raw.md (điểm 1, 3); calc/calc_items_out.json',
      note=f'dấu chắc chắn (NQ thông qua 100%; 2025 đã trích 10% trên LNST riêng 122,52 tỷ); cận bảo thủ = 11% × 122,52 tỷ phẳng × annuity 9 năm @13,5% ({ann:.4f}); cận cao = trên dòng tiền HĐ + 9T/26 ({m1_hi}%); 1 kỳ có số ⇒ thang B1',
      p=0.5, p_low=0.25, p_high=0.75, mag_pct=m1_cons, mag_range_pct=[m1_hi, m1_cons], counted_in_center=True),
 dict(name='Truyền dẫn tâm điều chỉnh NNC qua stake 44,07% (bỏ #4 chân MVC)', dir='down', evidence_tier='inherited',
      source='dd_adjcenter_20261124/NNC/adj.json (md5 ' + nf['nnc_adj_md5'] + '); calc/calc_items_out.json nnc_flow',
      note='p đã nằm trong adj NNC (sum_pct_combo trừ #4); dải = dải NNC trừ cực trị #4', p=1.0, p_low=1.0, p_high=1.0,
      mag_pct=m2, mag_range_pct=[m2_lo, m2_hi], counted_in_center=True)]
for it in items: it['contrib_pct'] = round(it['p'] * it['mag_pct'], 3)
S = sum(it['p'] * it['mag_pct'] for it in items)
lo = sum(min(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
hi = sum(max(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
assert abs(S) <= 5, S
ccn10 = round(pct(50), 2); phmt = round(pct(4.50), 2)
adj = round(C0 * (1 + S / 100))
d1A_cons = round(100 * (0.9 * m1_cons - 0.5 * m1_cons) / 100 * 1, 2); d1A_hi = round(0.9 * m1_hi - 0.5 * m1_cons, 2)
TRIG = [
 dict(event='BCTC riêng năm 2026 + NQ ĐHĐCĐ 2027 phân phối LNST 2026 (tỷ lệ quỹ thật trên LNST riêng thật)', when='03–04/2027', direction='down', delta_vnd=round(C0 * d1A_cons / 100), delta_pct=d1A_cons, note=f'#1 C+→A (p 0,9): ở cận bảo thủ {d1A_cons}%, ở cận cao {d1A_hi}%; tỷ lệ quỹ về 10% như 2025 ⇒ |m| ×10/11'),
 dict(event='NQ/kế hoạch vốn cụm công nghiệp ≤500 tỷ (tiến độ, giá thuê, vốn chủ)', when='ĐHĐCĐ 2027 hoặc CBTT', direction='both', delta_vnd=round(C0 * ccn10 / 100), delta_pct=ccn10, note='mỗi 10% hao hụt NPV trên 500 tỷ; có cơ sở độc lập ⇒ C→B, rev mới'),
 dict(event='Thuyết minh ký quỹ PHMT/đóng mỏ (Tân Lập + 2 mỏ mới)', when='BCTC năm 2026', direction='down', delta_vnd=round(C0 * phmt / 100), delta_pct=phmt, note='tham chiếu NNC 4,50 tỷ, không chiết khấu ⇒ cận trên'),
 dict(event='Cập nhật adj NNC (dữ kiện mới của NNC)', when='khi có', direction='both', delta_vnd=None, delta_pct=None, note='#2 đọc lại adj.json NNC; dải hiện −4,75…+0,09%'),
 dict(event='Hạn GP Tân Lập xác minh (2035/2040/2045)', when='khi tra', direction='both', delta_vnd=None, delta_pct=None, note='đổi trọng số trục lưới ⇒ rev mới, chạy lại mô hình'),
 dict(event='GP 2 mỏ mới được cấp / bị từ chối', when='khi có', direction='both', delta_vnd=None, delta_pct=None, note='nhánh lưới — rev mới'),
 dict(event='Lãi huy động 12T ±50bp (luật V1)', when='liên tục', direction='both', delta_vnd=-201, delta_pct=-1.24, note='+50bp −201; −50bp +210 (REPORT_recheck §2)'),
 dict(event='Pháp lý (Điều 195 LDN khi lên 51% NNC; quét sau 05/11)', when='khi có', direction='none', delta_vnd=0, delta_pct=0, note='chỉ WARNING')]
out = dict(ticker='MVC', dd_date='2026-11-03', rev=10, asof='2026-11-24', job='Taylor_20261124_131351',
           prereg_md5=dict(PREREG_adj='ef5157cb3f762d58623ed550ebc214c7', PREREG_adj_v2='835dfc1e07f9c67ac7f6c3028b529d13', INVENTORY_adj_MVC='efee3d6721c790896c6cbae030fa82b9'),
           blind_to_price=True, center_base=C0, center_base_source='LEDGER_PROPOSAL_MVC.json rev10 center (= sổ rev9 16.241; recheck không đổi tâm)',
           items=items, sum_p_m_pct=round(S, 3), aggregation='linear (|Σ|≤5%)',
           center_adj=adj, range_low=round(C0 * (1 + lo / 100)), range_high=round(C0 * (1 + hi / 100)),
           dividend_mech=dict(vnd=0, status='cổ tức 2025 600 đ (60 tỷ) = cổ tức phải trả V.19 đã trừ trong NETFIN; cổ tức 2026 do ĐHĐCĐ 2027 quyết — chưa có quyền tiền công bố'),
           sensitivity_only=[
             dict(name='Cụm công nghiệp ≤500 tỷ (base NPV 0 theo luật 03/11)', dir='both', evidence_tier='C', sensitivity=f'mỗi 10% hao hụt NPV trên 500 tỷ ⇒ {ccn10:+.2f}% (r4 từng trừ −8…−13%, không có dữ kiện mới)', why_not_center='không có kế hoạch/giá; luật house cấm suy "đầu tư mới ⇒ giảm giá trị" khi thiếu cơ sở độc lập', source='skeptic/r1_raw.md điểm 2'),
             dict(name='Ký quỹ PHMT/đóng mỏ', dir='down', evidence_tier='C', sensitivity=f'tham chiếu NNC 4,50 tỷ ⇒ {phmt:+.2f}% (cận trên, không chiết khấu)', why_not_center='chưa đọc thuyết minh MVC', source='REPORT_recheck_MVC.md §3 D3'),
             dict(name='Biên Tân Lập 38% / mỏ mới kịch bản tốt / upside 2034', dir='up', evidence_tier='C', sensitivity='không định lượng (không có dữ kiện mới)', why_not_center='không có số', source='skeptic/r1_raw.md symmetry'),
             dict(name='[LUẬT] CK holding 20% (dải 0…+20% user chốt 24/11; base 0%)', dir='down', evidence_tier='rule', sensitivity='−1.286 đ trước CK (−7,26%); 6%: −388; 15%: −967', source='REPORT_recheck_MVC.md §3'),
             dict(name='[LUẬT] r 13,5% vs dải Ke (E15)', dir='up', evidence_tier='rule', sensitivity='Ke 12,3% ⇒ 16.761 (+3,20%); 13,4% ⇒ +0,26%; β=1', source='REPORT_recheck_MVC.md §2')],
           trigger_table=TRIG,
           caveat='cộng tuyến tính (|Σ|≤5%); #1 cận bảo thủ dựng từ LNST riêng 2025 phẳng (LNST riêng 9T/26 ex-hoàn nhập ~180,7 tỷ cao hơn ⇒ thật sự bảo thủ); #2 số đo bằng engine r3 (calc_items.py), không phải số skeptic')
assert 0 < out['range_low'] <= adj <= out['range_high']
json.dump(out, open(os.path.join(HERE, 'adj.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(dict(m1_cons=m1_cons, m1_hi=m1_hi, m2=m2, m2_range=[m2_lo, m2_hi], S=round(S, 3), lo=round(lo, 3), hi=round(hi, 3), center_adj=adj, range=[out['range_low'], out['range_high']], ccn10=ccn10, phmt=phmt, trig1=[d1A_cons, d1A_hi]), ensure_ascii=False))
