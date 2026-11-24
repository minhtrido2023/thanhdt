"""PVP E17 — tam ky vong dieu chinh theo PREREG_adj (+v2), kiem ke khoa truoc: INVENTORY_adj_PVP.md. MU GIA.
Chay: wc_venv python -I calc_adj.py <restore>/agents/Taylor/research/dd_redo_20261105"""
import hashlib, json, os, sys, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); WT = os.path.abspath(os.path.join(HERE, '../../../../..'))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
PR = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124')
assert md5(os.path.join(PR, 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(PR, 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
assert md5(os.path.join(HERE, 'INVENTORY_adj_PVP.md')) == 'c0d80348a3f758e101dc4d58b391c20c'
D3 = json.load(open(os.path.join(HERE, 'calc', 'calc_d3_tot_out.json')))
C0 = 23099
items = [dict(name='Lên đà định kỳ sau TT99 — chỉ nhánh tốt (C+ cận bảo thủ k=0,5)', dir='down', evidence_tier='C+',
              source='agents/Taylor/research/dd_recheck_20261124w2/PVP/skeptic/r1_raw.md:10-14; calc/calc_d3_tot_out.json; dd_PVP_20261029/REPORT.md:73 (LCTT mã 03 9T/25 53,1 tỷ)',
              note='dấu chắc chắn (lên đà đăng kiểm bắt buộc); cận bảo thủ ½ mức trích cũ; 1 quan sát ⇒ B1', p=0.5, p_low=0.25, p_high=0.75,
              mag_pct=D3['k0.5']['d_pct'], mag_range_pct=[D3['k1.0']['d_pct'], D3['k0.5']['d_pct']], counted_in_center=True)]
for it in items:
    it['contrib_pct'] = round(it['p'] * it['mag_pct'], 3)
S = sum(it['p'] * it['mag_pct'] for it in items)
lo = sum(min(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
hi = sum(max(p * m for p in (it['p_low'], it['p_high']) for m in it['mag_range_pct']) for it in items)
assert abs(S) <= 5
# do nhay C (chay mo hinh, khong vao tam)
sys.argv = [sys.argv[0], sys.argv[1]]; sys.path.insert(0, os.path.join(HERE, 'calc'))
with contextlib.redirect_stdout(io.StringIO()):
    import calc_recheck as R  # noqa: E402
P, M1 = R.P, R.M1
def corp_years(n):
    k = M1.CORP_YEARS; M1.CORP_YEARS = n
    try: return R.summ(P.R3, 0.135)['center']
    finally: M1.CORP_YEARS = k
cy6, cy8 = corp_years(6), corp_years(8)
def scrap(usd):
    return R.summ(dict(P.R3, scrap_usd=usd), 0.135)['center']
sc1, sc5 = scrap(1.0), scrap(5.0)
# KTPL: 5% phan LN sau thue tu doi tau + FSO - chi phi cong ty (uoc luong theo PV tai tham so trung tam)
pp = R.P.parts('coso', 6, 0.135, 'ca_hai', 'thanh_tien', R.P.R3)
ktpl5 = -0.05 * (pp['tankers'] + pp['fso'] + pp['corp']) * 1e9 / M1.SH * (1 - R.D)
TRIG = [
 dict(event='Văn kiện/NQ ĐHĐCĐ bất thường tàu Aframax "số 3": huỷ/hoãn mua', when='hạn ≤30/11/2026', direction='up', delta_vnd=1579, delta_pct=6.84, note='nhánh không mua = NPV0 (biến thể r3 24.678)'),
 dict(event='… có phát hành cổ phiếu dưới giá trị nội tại / tàu #3 ngoài 116 tr USD', when='hạn ≤30/11/2026', direction='down', delta_vnd=None, delta_pct=None, note='pha loãng SH theo tỷ lệ phát hành; dưới book = HARD ABANDON'),
 dict(event='Thuyết minh BCTC năm 2026: lịch + chi phí lên đà từng tàu', when='01–03/2027', direction='down', delta_vnd=-443, delta_pct=-1.92, note='#1 C+→A; khoảng −221…−443'),
 dict(event='LDT từng tàu + giá phế liệu', when='khi tra', direction='up', delta_vnd=117, delta_pct=0.51, note='mỗi 1 tr USD'),
 dict(event='NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL', when='03–04/2027', direction='down', delta_vnd=-173, delta_pct=-0.75, note='mỗi 1% LN, ước lượng'),
 dict(event='Phụ lục FSO giá thấp hơn / hạn ngắn hơn 2036', when='khi có', direction='down', delta_vnd=-610, delta_pct=-2.64, note='biến thể bỏ dòng >5 năm 22.489'),
 dict(event='177 tỷ FSO năm 1 hoà giải được / không', when='BCTC năm 2026', direction='both', delta_vnd=639, delta_pct=2.77, note='+639 (luôn thành tiền) / −639 (không)'),
 dict(event='DT vận tải Q4/2026 < Q3', when='~20/01/2027', direction='down', delta_vnd=None, delta_pct=None, note='trọng số cước xấu ↑ — rev mới, chạy lại mô hình'),
 dict(event='Lãi huy động 12T ±50bp (luật V1)', when='liên tục', direction='both', delta_vnd=-198, delta_pct=-0.86, note='+50bp −198; −50bp +202'),
 dict(event='Pháp lý', when='khi có', direction='none', delta_vnd=0, delta_pct=0, note='chỉ WARNING')]
out = dict(ticker='PVP', dd_date='2026-10-29', rev=3, asof='2026-11-24', job='Taylor_20261124_131351',
           prereg_md5=dict(PREREG_adj='ef5157cb3f762d58623ed550ebc214c7', PREREG_adj_v2='835dfc1e07f9c67ac7f6c3028b529d13', INVENTORY_adj_PVP='c0d80348a3f758e101dc4d58b391c20c'),
           blind_to_price=True, center_base=C0, center_base_source='LEDGER_PROPOSAL_PVP.json rev3 center (= sổ rev2 23.099; recheck không đổi tâm)',
           items=items, sum_p_m_pct=round(S, 3), aggregation='linear (|Σ|≤5%)',
           center_adj=round(C0 * (1 + S / 100)), range_low=round(C0 * (1 + lo / 100)), range_high=round(C0 * (1 + hi / 100)),
           dividend_mech=dict(vnd=0, status='cổ tức 2025 1.000 đ đã trả 20/10/2026, đã trừ trong tiền ròng (DIV_PAY); không có quyền tiền chưa chốt đã biết'),
           sensitivity_only=[
               dict(name='Phế liệu đội tàu hiện hữu (base = 0)', dir='up', evidence_tier='C', sensitivity=f'+1 tr USD ⇒ {sc1} ({100*(sc1/C0-1):+.2f}%); +5 tr USD ⇒ {sc5} ({100*(sc5/C0-1):+.2f}%)',
                    why_not_center='không có LDT/giá phế liệu trong tay ⇒ không có cận từ dữ liệu', source='skeptic/r1_raw.md:15-18'),
               dict(name='ĐHĐCĐ bất thường 23/10/2026 — tàu Aframax "số 3", nguồn vốn/phát hành', dir='both', evidence_tier='C', sensitivity='không định lượng được (chưa có văn kiện); nhánh "không mua" NPV0 ⇒ biến thể r3 NPV0 24.678 (+6,8%); phát hành dưới giá trị nội tại ⇒ pha loãng',
                    why_not_center='không có văn kiện trong tay', source='skeptic/r1_raw.md:19-22'),
               dict(name='Trích quỹ KTPL hằng năm (ví dụ 5% LN sau thuế)', dir='down', evidence_tier='C', sensitivity=f'{round(ktpl5)} đ/cp ({100*ktpl5/C0:+.2f}%) — ước lượng: 5% × PV(đội tàu+FSO−chi phí công ty) tại tham số trung tâm',
                    why_not_center='không có số dư/tốc độ chi quỹ trong tay', source='skeptic/r1_raw.md:27'),
               dict(name='Chi phí công ty 10 năm [UL]', dir='up', evidence_tier='C', sensitivity=f'8 năm ⇒ {cy8} ({100*(cy8/C0-1):+.2f}%); 6 năm ⇒ {cy6} ({100*(cy6/C0-1):+.2f}%)',
                    why_not_center='tham số tự đặt; FSO hợp đồng tới 2036 ≈ 10 năm', source='skeptic/r1_raw.md:26'),
               dict(name='NPV tàu mới −30% nhánh xấu [UL]', dir='up', evidence_tier='C', sensitivity='NPV0 mọi nhánh 24.678 (+6,8%); −30% vô điều kiện 18.935 (−18,0%) (REPORT_r3 §3)', why_not_center='độ lớn [UL]', source='skeptic/r1_raw.md:46'),
               dict(name='[LUẬT] r 13,5% vs dải Ke (E15)', dir='up', evidence_tier='rule', sensitivity='Ke 12,3% ⇒ 23.593 (+2,14%); 13,4% ⇒ +0,17%', source='REPORT_recheck_PVP.md §2')],
           trigger_table=TRIG,
           caveat='cộng tuyến tính (1 hạng mục); D3 tính bằng mô hình r3 (calc_d3_tot.py), không phải số skeptic')
json.dump(out, open(os.path.join(HERE, 'adj.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ('center_base', 'sum_p_m_pct', 'center_adj', 'range_low', 'range_high')}, ensure_ascii=False))
for s in out['sensitivity_only']: print(s['name'], '|', s['sensitivity'])
