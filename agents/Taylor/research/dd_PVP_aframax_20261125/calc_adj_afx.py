"""PVP E17 cap nhat sau tai lieu DHDCD bat thuong 2026 (DU THAO 09/11, hop 30/11) — job Taylor_20261125_080254. MU GIA.
Ke thua adj.json dot 2 (assert md5) + 1 hang muc moi bac A theo PREREG_adj §1-3 (assert md5). Khong doi tam base 23.099.
Chay: python3 -I calc_adj_afx.py  (doc calc/calc_afx_out.json)"""
import hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); WT = os.path.abspath(os.path.join(HERE, '../../../..'))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
PR = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124')
assert md5(os.path.join(PR, 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(PR, 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
OLDP = os.path.join(WT, 'agents/Taylor/research/dd_recheck_20261124w2/PVP/adj.json')
OLD = json.load(open(OLDP)); OLD_MD5 = md5(OLDP)
X = json.load(open(os.path.join(HERE, 'calc', 'calc_afx_out.json')))
C0 = 23099; assert OLD['center_base'] == C0 == X['base']['center']
A = X['variants']['A_mot_tau_80']
items = [dict(it) for it in OLD['items']]
items.append(dict(
    name='Nhánh "một tàu" = DT-08/26/TBD ≤80 tr USD (thay Aframax #2 56,5 tr USD) — chỉ tác động qua nhánh xấu NPV −30% đã khoá',
    dir='down', evidence_tier='A',
    source='src/3-du-thao-to-trinh-dieu-chinh-danh-muc-dau-tu-nam-2026*.txt p1 (2 dòng 56,5+59,5 gộp thành "01 đến 03 tàu", tổng 116 giữ); '
           'src/4-du-thao-to-trinh-...-tau-cho-dau-tho*.txt p1,p3,p5 (TMĐT ≤80.000.000 USD, giá tàu 79.550.000, 10 tuổi, vay ≤70%); calc/calc_afx_out.json A_mot_tau_80',
    note='Văn bản công ty (tài liệu họp CBTT 09/11) ⇒ bậc A, p theo thang 0,90 [0,75;1,00] (PREREG §2 không cho hạ vì rủi ro biểu quyết — ghi rõ: ĐHĐCĐ họp 30/11, NQ chưa có). '
         'm = −0,72% (chạy mô hình r3, chỉ đổi giá trị nhánh chi_2 56,5→80; trọng số 0,50/0,35/0,15 + NPV {xấu −30%, cơ sở/tốt 0} GIỮ — luật house, không phải hạng mục). '
         'Khoảng m [−0,72; 0]: 80 là TRẦN ("không vượt quá"); giá mua ≤56,5 ⇒ 0.',
    p=0.90, p_low=0.75, p_high=1.00, mag_pct=A['d_pct'], mag_range_pct=[A['d_pct'], 0.0], counted_in_center=True))
for it in items:
    it['contrib_pct'] = round(it['p'] * it['mag_pct'], 3)
S = sum(it['p'] * it['mag_pct'] for it in items)
lo = sum(min(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
hi = sum(max(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
assert abs(S) <= 5
V = X['variants']
sens = [s for s in OLD['sensitivity_only'] if 'ĐHĐCĐ' not in s['name'] and 'NPV tàu mới' not in s['name']]
sens += [
 dict(name='[LUẬT] trọng số mua tàu 0,50/0,35/0,15 — "không" 0,15→0,05 (văn kiện đã xong, đã triệu tập)', dir='down', evidence_tier='C',
      sensitivity=f"{V['B_mot_tau_80_khong_005']['center']} ({V['B_mot_tau_80_khong_005']['d_pct']:+.2f}%)", why_not_center='trọng số kịch bản = tham số house (PREREG §4)', source='calc/calc_afx_out.json'),
 dict(name='[LUẬT] "không" 0,15→0,30 (không thông qua / không tìm được tàu — tờ trình 3: ít chủ tàu chào bán)', dir='up', evidence_tier='C',
      sensitivity=f"{V['C_mot_tau_80_khong_030']['center']} ({V['C_mot_tau_80_khong_030']['d_pct']:+.2f}%)", why_not_center='trọng số kịch bản = tham số house', source='calc/calc_afx_out.json'),
 dict(name='Dùng hết 116 tr USD chắc chắn / chỉ 1 tàu 80 chắc chắn', dir='down', evidence_tier='C',
      sensitivity=f"116: {V['E_ca_goi_116_chac']['center']} ({V['E_ca_goi_116_chac']['d_pct']:+.2f}%); 80: {V['D_chi_mot_tau_80_chac']['center']} ({V['D_chi_mot_tau_80_chac']['d_pct']:+.2f}%)",
      why_not_center='trọng số kịch bản', source='calc/calc_afx_out.json'),
 dict(name='NPV tàu mới: NPV0 mọi nhánh / −30% vô điều kiện (nhánh một tàu 80)', dir='both', evidence_tier='C',
      sensitivity=f"NPV0: {V['F_npv0_moi_nhanh_A']['center']} ({V['F_npv0_moi_nhanh_A']['d_pct']:+.2f}%); −30% vô đk: {V['G_m30_vo_dieu_kien_A']['center']} ({V['G_m30_vo_dieu_kien_A']['d_pct']:+.2f}%)",
      why_not_center='độ lớn [UL]; kiểm chéo: giá tàu 10 tuổi về TB 2023-25 (54) ⇒ −32,1% giá mua 79,55 (bảng Clarksons/Allied trong tờ trình 4 p3) — chỉ ủng hộ dấu/độ lớn nhánh xấu, không đổi tham số',
      source='calc/calc_afx_out.json xcheck_m30'),
]
out = dict(ticker='PVP', dd_date=OLD['dd_date'], rev=5, asof='2026-11-25', job='Taylor_20261125_080254',
           prereg_md5=OLD['prereg_md5'], inherits=dict(path='agents/Taylor/research/dd_recheck_20261124w2/PVP/adj.json', md5=OLD_MD5),
           blind_to_price=True, center_base=C0, center_base_source='sổ rev4 center 23.099 (không đổi — NQ ĐHĐCĐ bất thường chưa thông qua, họp 30/11/2026)',
           items=items, sum_p_m_pct=round(S, 3), aggregation='linear (|Σ|≤5%)',
           center_adj=round(C0 * (1 + S / 100)), range_low=round(C0 * (1 + lo / 100)), range_high=round(C0 * (1 + hi / 100)),
           dividend_mech=OLD['dividend_mech'], sensitivity_only=sens)
json.dump(out, open(os.path.join(HERE, 'adj.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ('sum_p_m_pct', 'center_adj', 'range_low', 'range_high')}, ensure_ascii=False))
