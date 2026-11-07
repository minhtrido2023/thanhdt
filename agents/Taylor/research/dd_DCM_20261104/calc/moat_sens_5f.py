"""DCM 5F addendum 07/11/2026 — độ nhạy moat WIDE/NARROW/NONE. MÙ GIÁ: không nhận giá/vốn hoá/PE.
Dựng trên bảng r5 §4 (tâm theo biên dài hạn, tuyến tính: 98→18.356 … 260→30.272) và calc/model.py (LNST hoạt động theo biên, thuế 20%).
Vốn hoạt động = VCSH 30/9/26 (BVPS 22.446,5 × 529,4tr, BQ ticker_financial 2026Q3) − net cash 7.539 (model.py)."""
import sys, csv; sys.path.insert(0, 'calc'); import model as m
R = m.R0
V = {98: 18356, 138: 21298, 179: 24314, 220: 27330, 260: 30272}           # REPORT_r5 §4 bảng biên→giá trị (tâm)
k = (V[260]-V[98])/(260-98)                                                  # đ/cp mỗi USD/t biên vĩnh viễn từ năm 2
val = lambda s: V[179] + k*(s-179)
eq = 22446.51363191537*529.4e6/1e9; opcap = eq - m.net_cash
s_ke = next(s/10 for s in range(500, 3000) if m.lnst_at(s/10, 0.20) >= R*opcap)   # biên mà ROIC hoạt động (sổ sách) = Ke
cm = {int(r['yr']): (float(r['urea']), float(r['brent'])) for r in csv.DictReader(open('calc/bq_commod_out.csv'))}
px = {y: u-25*(2.5+0.06*b) for y, (u, b) in cm.items()}
s2125 = sum(px[y] for y in range(2021, 2026))/5
def deferred(s_from, s_to, start_year):  # biên s_from tới trước start_year, s_to từ start_year (năm 2 = 2028 ⇒ năm 1 = Q4/26–Q3/27)
    t = start_year - 2026                                                    # số năm kể từ định giá
    return val(s_from) + k*(s_to-s_from)*(1+R)**-(t-2)   # perpetuity bắt đầu năm t (năm1=Q4/26-Q3/27) so với perpetuity từ năm 2
out = {
 'k_per_usd': round(k, 2), 'equity_ty': round(eq), 'opcap_ty': round(opcap),
 'roic_op_at_179': round(m.lnst_at(179, .20)/opcap, 3), 'spread_roic_eq_ke': s_ke, 'proxy_avg_2021_25': round(s2125, 1),
 'NARROW_base_179': round(val(179)),
 'WIDE_220': round(val(220)), 'WIDE_2021_25_avg': round(val(s2125)), 'WIDE_260': round(val(260)),
 'NONE_fade_now': round(val(s_ke)), 'NONE_fade_from_2035': round(deferred(179, s_ke, 2035)),
}
for kk, v in out.items(): print(kk, v)
