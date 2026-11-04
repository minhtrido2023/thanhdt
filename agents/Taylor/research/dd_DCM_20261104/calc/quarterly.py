"""Bóc KQKD hợp nhất DCM theo quý từ BCTC gốc (đọc ảnh, tỷ đồng). Nguồn mỗi số ghi ở comment.
YTD-differencing: Q = YTD(k) - YTD(k-1). Lưu ý: BCTC 9T/26 đã phân loại lại ~102,9 tỷ 'phân bổ giá trị tiềm năng'
từ GVHB sang QLDN cho H1 (9T - Q3 ≠ H1 đã công bố) -> số quý lấy theo cột QUÝ của KQKD khi có."""
import json
# KQKD cột quý (tỷ): DT gộp, giảm trừ, GVHB, DT TC, CP TC, lãi vay, CPBH, QLDN, LN khác, LNTT, LNST, LNST mẹ
PL = {
 # Q3/26 & Q3/25: BCTC HN Q3/2026 tr.3-4 (PDF p7-8)
 'Q3/26': dict(dt=5999.584, gt=258.084, cogs=4642.821, fin_inc=56.162, fin_cost=144.353, int_exp=37.356, sell=358.396, ga=154.067, other=3.394, pbt=501.419, pat=432.306, pat_m=429.608),
 'Q3/25': dict(dt=3096.350, gt=108.120, cogs=2331.497, fin_inc=128.649, fin_cost=28.052, int_exp=18.986, sell=271.052, ga=107.399, other=-0.303, pbt=378.576, pat=327.968, pat_m=327.688),
 # Q2/26 & Q2/25 (đã trình bày lại): BCTC HN Q2/2026 tr.3-4
 'Q2/26': dict(dt=6881.308, gt=169.117, cogs=4711.448, fin_inc=91.691, fin_cost=34.579, int_exp=32.312, sell=417.519, ga=451.729, other=-1.431, pbt=1187.175, pat=1067.429, pat_m=1068.063),
 'Q2/25': dict(dt=6252.273, gt=214.902, cogs=4796.742, fin_inc=121.900, fin_cost=30.225, int_exp=18.019, sell=214.403, ga=229.387, other=-0.273, pbt=888.242, pat=787.737, pat_m=786.124),
 # Q4/25: BCTC HN Q4/2025 tr.3 (+ CV giải trình: LNTT 436,07; LNST 389,45)
 'Q4/25': dict(dt=4627.596, gt=99.227, cogs=3276.251, fin_inc=54.498, fin_cost=19.624, int_exp=17.919, sell=382.387, ga=472.788, other=None, pbt=436.07, pat=389.45, pat_m=None),
}
# YTD 6T: Q2/26 report
YTD6 = {'26': dict(dt=12312.106, gt=313.866, cogs=8651.049, fin_inc=185.401, fin_cost=72.052, int_exp=59.844, sell=769.828, ga=630.192, other=4.380, pbt=2064.900, pat=1856.058, pat_m=1855.860),
        '25': dict(dt=9824.396, gt=380.318, cogs=7318.299, fin_inc=218.884, fin_cost=49.228, int_exp=33.501, sell=553.648, ga=401.323, other=1.623, pbt=1342.087, pat=1199.846, pat_m=1197.541)}
for y in ('26','25'):
    q2 = PL[f'Q2/{y}']
    PL[f'Q1/{y}'] = {k: (None if (YTD6[y][k] is None or q2[k] is None) else round(YTD6[y][k]-q2[k],3)) for k in YTD6[y]}
# FY25 (Q4/25 report tr.3) & 9T/25 (Q3/26 report cột 7)
FY25 = dict(dt=17548.342, gt=587.665, cogs=12926.048, fin_inc=402.031, fin_cost=96.904, int_exp=70.405, sell=1207.086, ga=981.509)
for q in PL.values():
    q['dtt'] = round(q['dt']-q['gt'],3); q['gp'] = round(q['dtt']-q['cogs'],3)
    q['gpm_net'] = round(q['gp']/q['dtt']*100,2)
    q['ebit_core'] = round(q['gp']-q['sell']-q['ga'],3)   # LN gộp - BH - QLDN
    q['fin_net'] = round(q['fin_inc']-q['fin_cost'],3)
order = ['Q1/25','Q2/25','Q3/25','Q4/25','Q1/26','Q2/26','Q3/26']
# ---- Thuyết minh theo sản phẩm (YTD, tỷ). Nguồn: TM28/30 Q3/26 (9T), TM27/29 Q2/26 (6T), TM24/26 Q1/26 (3T), TM24/26 Q4/25 (12T)
SEG = {
 '3T26': dict(ure_dt=2924.352, ure_dom=1058.535, ure_exp=1865.817, npk_dt=815.413, tm_dt=1488.510, oth_dt=202.146, ure_c=1711.928, npk_c=688.898, tm_c=1423.200, oth_c=115.574),
 '3T25': dict(ure_dt=2438.365, ure_dom=1042.514, ure_exp=1395.851, npk_dt=521.039, tm_dt=260.661, oth_dt=351.811, ure_c=1562.578, npk_c=445.764, tm_c=233.733, oth_c=279.482),
 '6T26': dict(ure_dt=6818.765, ure_dom=2269.436, ure_exp=4549.328, npk_dt=1953.774, tm_dt=3144.520, oth_dt=391.299, ure_c=3814.457, npk_c=1647.063, tm_c=2970.589, oth_c=220.536),
 '6T25': dict(ure_dt=4868.749, ure_dom=2731.116, ure_exp=2137.633, npk_dt=2256.017, tm_dt=2042.325, oth_dt=656.659, ure_c=3111.834, npk_c=1847.580, tm_c=1977.165, oth_c=381.720),
 '9T26': dict(ure_dt=9391.888, ure_dom=4103.000, ure_exp=5288.888, npk_dt=3577.807, tm_dt=4680.233, oth_dt=651.047, ure_c=5479.443, npk_c=2965.435, tm_c=4354.512, oth_c=386.057),
 '9T25': dict(ure_dt=6245.188, ure_dom=3312.538, ure_exp=2932.650, npk_dt=2752.970, tm_dt=3098.344, oth_dt=816.632, ure_c=3950.891, npk_c=2251.630, tm_c=2937.619, oth_c=509.657),
 '12T25': dict(ure_dt=8648.265, ure_dom=4596.660, ure_exp=4051.606, npk_dt=3877.634, tm_dt=4008.088, oth_dt=989.392, ure_c=5198.620, npk_c=3280.933, tm_c=3816.807, oth_c=617.891),
 '12T24': dict(ure_dt=7701.002, ure_dom=5181.412, ure_exp=2519.590, npk_dt=2795.859, tm_dt=2439.979, oth_dt=1001.739, ure_c=5498.270, npk_c=2393.727, tm_c=2289.619, oth_c=760.443),
}
def diff(a,b): return {k: round(SEG[a][k]-SEG[b][k],3) for k in SEG[a]}
SQ = {'Q1/25':SEG['3T25'],'Q2/25':diff('6T25','3T25'),'Q3/25':diff('9T25','6T25'),'Q4/25':diff('12T25','9T25'),
      'Q1/26':SEG['3T26'],'Q2/26':diff('6T26','3T26'),'Q3/26':diff('9T26','6T26')}
for q,s in SQ.items():
    s['ure_gp']=round(s['ure_dt']-s['ure_c'],1); s['ure_gpm']=round(s['ure_gp']/s['ure_dt']*100,1)
    s['npk_gp']=round(s['npk_dt']-s['npk_c'],1); s['tm_gp']=round(s['tm_dt']-s['tm_c'],1)
    s['exp_share']=round(s['ure_exp']/s['ure_dt']*100,1)
if __name__=='__main__':
    print('KQKD HN theo quý (tỷ)')
    keys=['dt','gt','dtt','cogs','gp','gpm_net','sell','ga','ebit_core','fin_inc','fin_cost','int_exp','fin_net','other','pbt','pat']
    print('quý   '+' '.join(f'{k:>9}' for k in keys))
    for q in order:
        print(f'{q:6}'+' '.join(f'{(PL[q][k] if PL[q][k] is not None else float("nan")):9.1f}' for k in keys))
    print('\nTheo sản phẩm (tỷ; Q3/26 và H1/26 bị ảnh hưởng phân loại lại ~102,9 tỷ GVHB->QLDN, chưa rõ dòng)')
    sk=['ure_dt','ure_dom','ure_exp','exp_share','ure_c','ure_gp','ure_gpm','npk_dt','npk_gp','tm_dt','tm_gp','oth_dt']
    print('quý   '+' '.join(f'{k:>9}' for k in sk))
    for q in order:
        print(f'{q:6}'+' '.join(f'{SQ[q][k]:9.1f}' for k in sk))
    json.dump({'PL':PL,'SQ':SQ},open('calc/quarterly_out.json','w'),ensure_ascii=False,indent=1)
