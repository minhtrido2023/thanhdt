"""DD PVT 2026-10-29 — tai dung BCTC HN Q3/2026 tu text (src/), self-check hang dang thuc, dinh gia.
Chay: python3 calc.py > out.txt   (can wc_env.sh cho bq; DNSE gia song lay rieng, ghi cung o duoi)."""
import subprocess, io, csv, statistics as st
B = 1e9
# ---------- KQKD [text dong ~1060-1170], cot: Q3_26, Q3_25, 9T_26, 9T_25 (ty VND)
IS = {
 'rev':   [5610.131200449, 4419.446706829, 15525.134574859, 11568.687997535],
 'cogs':  [4816.368152043, 3835.342815821, 13126.090368953, 9896.769605588],
 'gp':    [793.763048406, 584.103891008, 2399.044205906, 1671.918391947],
 'fin_inc':[104.884653006, 90.015150486, 289.491400207, 241.752638596],
 'fin_exp':[145.836525287, 141.606135882, 429.436767308, 416.185348780],
 'interest':[116.660952263, 106.795985176, 345.641490397, 320.132696556],
 'selling':[4.913181647, 4.045293318, 15.236520071, 10.162722761],
 'ga':    [156.034864969, 140.702661237, 375.442705255, 352.333130455],
 'assoc': [5.052055742, 5.383063773, 18.077951494, 15.861770388],
 'op':    [596.915185251, 393.148014830, 1886.497564973, 1150.851598935],
 'oth_inc':[18.354887368, 50.251285502, 97.799332863, 97.313012197],
 'oth_exp':[2.084070495, 7.201271073, 4.340616038, 32.771417483],
 'pbt':   [613.186002124, 436.198029259, 1979.956281798, 1215.393193649],
 'tax_cur':[127.370503389, 93.450951078, 402.870981791, 236.215127890],
 'tax_def':[-3.538682896, -6.216516580, -4.678165454, -5.675212070],
 'npat':  [489.354181631, 348.963594761, 1581.763465461, 984.853277829],
 'np_parent':[375.130530320, 263.378756810, 1272.288228458, 771.874744421],
 'nci':   [114.223651311, 85.584837951, 309.475237003, 212.978533408],
}
cols = ['Q3_26','Q3_25','9T_26','9T_25']
print('== SELF-CHECK KQKD (ty VND, sai so phai ~0) ==')
for i,c in enumerate(cols):
    g = IS
    e1 = g['rev'][i]-g['cogs'][i]-g['gp'][i]
    e2 = g['gp'][i]+g['fin_inc'][i]-g['fin_exp'][i]-g['selling'][i]-g['ga'][i]+g['assoc'][i]-g['op'][i]
    e3 = g['op'][i]+g['oth_inc'][i]-g['oth_exp'][i]-g['pbt'][i]
    e4 = g['pbt'][i]-g['tax_cur'][i]-g['tax_def'][i]-g['npat'][i]
    e5 = g['np_parent'][i]+g['nci'][i]-g['npat'][i]
    print(f"{c}: rev-cogs-gp={e1:.6f} op_id={e2:.6f} pbt_id={e3:.6f} npat_id={e4:.6f} parent+nci={e5:.6f}")
# CV giai trinh 983
cv = {'Q3_26':489.354181631,'Q3_25':348.963594761,'9T_26':1581.763465461,'9T_25':984.853277829}
for i,c in enumerate(cols): print(f"CV983 vs KQKD {c}: diff={IS['npat'][i]-cv[c]:.9f}")
print(f"Q3 YoY NPAT {IS['npat'][0]/IS['npat'][1]-1:+.2%}; 9T {IS['npat'][2]/IS['npat'][3]-1:+.2%}")
print(f"Ke hoach 2026 (LNTT 1.500 / LNST 1.200 / DT 16.500): 9T dat LNTT {IS['pbt'][2]/1500:.1%}, LNST HN {IS['npat'][2]/1200:.1%}, DT {IS['rev'][2]/16500:.1%}")
# 6T & Q2 suy ra
pbt6 = IS['pbt'][2]-IS['pbt'][0]; rev6 = IS['rev'][2]-IS['rev'][0]
print(f"6T suy ra = 9T-Q3: LNTT {pbt6:.1f} (bao chi 1.366), DT {rev6:.1f}; Q2 DT bao chi 5.714 => Q1 DT {rev6-5714:.1f}; Q2 LNTT 834 => Q1 LNTT {pbt6-834:.1f}")
print(f"Q3 vs Q2: DT {IS['rev'][0]/5714-1:+.1%}; LNTT {IS['pbt'][0]/834-1:+.1%}")
# ---------- Bo phan (TM34)
seg = { # rev, cogs : Q3_26,Q3_25,9T_26,9T_25
 'van_tai': ([3514.972490283,2503.575341729,9582.465341446,7103.379520007],[2786.743307090,1974.319968904,7362.642182329,5669.183058746]),
 'kho_noi': ([152.412197690,143.499002729,434.561002097,446.564422376],[109.166711226,104.220589201,304.644488526,267.449380721]),
 'thuong_mai':([1678.220730763,1209.497993959,4971.583458020,3307.274003392],[1673.187593034,1204.086776658,4953.098972415,3294.961256921]),
 'khac':  ([264.525781713,562.874368412,536.524773296,711.470051760],[247.270540693,552.715481058,505.704725683,665.175909200]),
}
print('\n== BO PHAN (TM34) — tong kiem ==')
for i,c in enumerate(cols):
    sr = sum(v[0][i] for v in seg.values()); sc = sum(v[1][i] for v in seg.values())
    print(f"{c}: sum_rev-rev={sr-IS['rev'][i]:.6f} sum_cogs-cogs={sc-IS['cogs'][i]:.6f}")
for k,(r,cg) in seg.items():
    gp=[r[i]-cg[i] for i in range(4)]
    print(f"{k:10s} DT Q3 {r[0]:8.1f} vs {r[1]:8.1f} ({r[0]/r[1]-1:+.1%}) | LNG Q3 {gp[0]:6.1f} vs {gp[1]:6.1f} | bien Q3 {gp[0]/r[0]:.1%} vs {gp[1]/r[1]:.1%} | 9T DT {r[2]/r[3]-1:+.1%} LNG {gp[2]:7.1f} vs {gp[3]:7.1f} ({gp[2]/gp[3]-1:+.1%}) bien {gp[2]/r[2]:.1%} vs {gp[3]/r[3]:.1%}")
r,cg = seg['van_tai']; r6=r[2]-r[0]; g6=(r[2]-cg[2])-(r[0]-cg[0])
print(f"Van tai 6T/2026 suy ra: DT {r6:.1f} LNG {g6:.1f} bien {g6/r6:.1%}; Q3 bien {(r[0]-cg[0])/r[0]:.1%}; LNG Q3 vs TB quy 6T: {(r[0]-cg[0])/(g6/2)-1:+.1%}")
# ---------- Chat luong LN (TM26-29)
print('\n== CHAT LUONG LN 9T_26 vs 9T_25 ==')
fx_gain=[7.185249009,30.924875021,30.305582552,78.006974159]; dep_int=[96.430311682,55.418232396,250.953803131,157.599502226]
fx_loss_9t=[64.875095549+4.084965406, 84.581997039+3.597521378]  # thuc hien + danh gia lai (ghep cot, xem REPORT)
comp=[7.836241265,20.478690282,42.128959649,66.002689705]
print(f"Lai tien gui 9T {dep_int[2]:.1f} vs {dep_int[3]:.1f}; Q3 {dep_int[0]:.1f} vs {dep_int[1]:.1f}")
liquid_open, liquid_close = 1901.970628130+3043.996232955, 2060.184822477+4284.996606579
print(f"Tien+HTM dau ky {liquid_open:.1f} cuoi ky {liquid_close:.1f}; lai suat ngam 9T (nam hoa) = {dep_int[2]/0.75/((liquid_open+liquid_close)/2):.2%}")
print(f"Ty gia: lai 9T {fx_gain[2]:.1f} / lo ~{fx_loss_9t[0]:.1f} => rong ~{fx_gain[2]-fx_loss_9t[0]:.1f} (2025: {fx_gain[3]-fx_loss_9t[1]:.1f})")
print(f"Boi thuong (thu nhap khac) 9T {comp[2]:.1f} vs {comp[3]:.1f}; thanh ly TSCD lai 9T ~0,05 ty (TM28) => KHONG co lai ban tau")
core_pbt = IS['pbt'][2] - dep_int[2] - IS['assoc'][2] - (IS['oth_inc'][2]-IS['oth_exp'][2])
core_pbt25 = IS['pbt'][3] - dep_int[3] - IS['assoc'][3] - (IS['oth_inc'][3]-IS['oth_exp'][3])
print(f"LNTT loi (tru lai tien gui, LDLK, khac rong) 9T: {core_pbt:.1f} vs {core_pbt25:.1f} ({core_pbt/core_pbt25-1:+.1%}); ty trong lai tien gui/LNTT {dep_int[2]/IS['pbt'][2]:.1%}")
print(f"Hoan nhap du phong (LCTT ma 03) 9T_26 = -85,4 ty = {85.398/IS['pbt'][2]:.1%} LNTT (phi tien te; xem TT99)")
print(f"NCI/NPAT 9T {IS['nci'][2]/IS['npat'][2]:.1%}")
# ---------- BCDKT
BS = dict(cash=(2060.184822477,1901.970628130), htm=(4284.996606579,3043.996232955),
          st_debt=(1420.780517732,1394.164249726), lt_debt=(5543.718390902,6245.363980337),
          ta=(23681.065680037,22308.656455937), tl=(10818.137273876,10818.467171939),
          eq=(12862.928406161,11490.189283998), nci=(3007.359354829,2817.176678989),
          ca=(9565.206969934,7522.113324368), lta=(14115.858710103,14786.543131569),
          ar=(1913.150522267,1517.829993363), ppe=(12650.503036526,13495.052568359),
          ddock_prepaid=(391.122796513,241.481429975), ddock_prov=(403.488827845+23.609284664,266.959820218+273.997850796))
print('\n== BCDKT (30/9/26 | 31/12/25) ==')
for j,lab in enumerate(['30/9/26','31/12/25']):
    print(f"{lab}: TTS-(NPT+VCSH)={BS['ta'][j]-BS['tl'][j]-BS['eq'][j]:.6f}; TTS-(TSNH+TSDH)={BS['ta'][j]-BS['ca'][j]-BS['lta'][j]:.6f}")
    liq = BS['cash'][j]+BS['htm'][j]; debt=BS['st_debt'][j]+BS['lt_debt'][j]
    print(f"   tien+HTM {liq:.1f}; vay {debt:.1f}; NO RONG {debt-liq:.1f}; VCSH me {BS['eq'][j]-BS['nci'][j]:.1f}; du phong dry-dock {BS['ddock_prov'][j]:.1f}; CP sua chua lon tra truoc {BS['ddock_prepaid'][j]:.1f}")
print(f"Vay giam {BS['st_debt'][1]+BS['lt_debt'][1]-BS['st_debt'][0]-BS['lt_debt'][0]:.1f} (TM20: tong 7.639,5 -> 6.964,5)")
# ---------- LCTT
cfo=(2733.350568765,2235.358732626); capex=(946.964192257,938.407703478); da=(1829.146447941,1611.897924297)
print('\n== LCTT 9T ==')
print(f"Tien dau 1901,97 + LCT 158,12 + FX 0,10 = {1901.970628130+158.116733802+0.097460545:.6f} vs BCDKT 2060.184822477")
print(f"CFO {cfo[0]:.1f} vs {cfo[1]:.1f}; CFO/NPAT {cfo[0]/IS['npat'][2]:.2f}; capex {capex[0]:.1f}; FCF {cfo[0]-capex[0]:.1f} vs {cfo[1]-capex[1]:.1f}; KH {da[0]:.1f} (capex/KH {capex[0]/da[0]:.2f})")
ebitda9 = IS['gp'][2]-IS['selling'][2]-IS['ga'][2]+da[0]
print(f"EBITDA 9T_26 (LNG-BH-QL+KH) = {ebitda9:.1f}; nam hoa {ebitda9/0.75:.1f}")
# ---------- Gia/thi truong
SH = 516.918938  # trieu cp, TM22d
px_live = 21300  # DNSE latest_trade 10:59 29/10/2026 (san); tham chieu 22.850
def q(sql):
    out = subprocess.run(['bash','-lc',f'source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=5000 "{sql}"'],capture_output=True,text=True).stdout
    return list(csv.DictReader(io.StringIO(out)))
px = q("SELECT t.time, t.Close, t.Volume, t.PE, t.PB FROM tav2_bq.ticker AS t WHERE t.ticker='PVT' AND t.time>='2018-01-01' ORDER BY t.time")
last = px[-1]; print(f"\n== GIA (BQ den {last['time']}) ==")
vals=[float(r['Close'])*float(r['Volume']) for r in px[-20:]]; vals60=[float(r['Close'])*float(r['Volume']) for r in px[-60:]]
print(f"ADV20 {st.mean(vals)/B:.1f} ty; ADV60 {st.mean(vals60)/B:.1f} ty; Close cuoi {last['Close']}")
yr0=[r for r in px if r['time']>='2026-01-01']; hi=max(yr0,key=lambda r:float(r['Close']))
print(f"YTD: dau nam {yr0[0]['Close']} ({yr0[0]['time']}), dinh {hi['Close']} ({hi['time']}); live {px_live} = {px_live/float(yr0[0]['Close'])-1:+.1%} YTD, {px_live/float(hi['Close'])-1:+.1%} tu dinh")
for lb in ['2026-10-20','2026-10-27','2026-10-28']:
    r=[x for x in px if x['time']<=lb][-1]; print(f"  {r['time']} close {r['Close']}")
pe=[float(r['PE']) for r in px if r['PE'] not in ('',None) and 0<float(r['PE'])<60]; pb=[float(r['PB']) for r in px if r['PB'] not in ('',None) and 0<float(r['PB'])<10]
def pct(a,p): a=sorted(a); return a[int(p*(len(a)-1))]
print(f"PVT PE (BQ) 2018-: p25 {pct(pe,.25):.2f} med {pct(pe,.5):.2f} p75 {pct(pe,.75):.2f}; PB p25 {pct(pb,.25):.2f} med {pct(pb,.5):.2f} p75 {pct(pb,.75):.2f}")
# EPS/BV tu BCTC
np_q4_25 = 265.898037562  # BQ ticker_financial 2025Q4 NP_P0 (LNST me)
ttm = IS['np_parent'][2]+np_q4_25
bv = BS['eq'][0]-BS['nci'][0]
mcap = px_live*SH/1e3
print(f"\n== DINH GIA tai {px_live} ==")
print(f"LNST me TTM = 9T {IS['np_parent'][2]:.1f} + Q4/25 {np_q4_25:.1f} = {ttm:.1f}; EPS TTM {ttm/SH*1e3:.0f}; PE TTM {px_live/(ttm/SH*1e3):.2f}")
print(f"EPS Q3 nam hoa {IS['np_parent'][0]*4/SH*1e3:.0f} -> PE {px_live/(IS['np_parent'][0]*4/SH*1e3):.2f}")
print(f"BVPS me {bv/SH*1e3:.0f}; PB {px_live/(bv/SH*1e3):.2f}; von hoa {mcap:.0f} ty")
netdebt = BS['st_debt'][0]+BS['lt_debt'][0]-BS['cash'][0]-BS['htm'][0]
ev = mcap+netdebt+BS['nci'][0]
print(f"EV = von hoa + no rong {netdebt:.0f} + NCI so sach {BS['nci'][0]:.0f} = {ev:.0f}; EV/EBITDA (9T nam hoa) {ev/(ebitda9/0.75):.2f}")
# Lich su LNST me nam (BQ ticker_financial NP_P0, cong 4 quy)
fin = q("SELECT f.quarter, ANY_VALUE(f.NP_P0) np FROM tav2_bq.ticker_financial AS f WHERE f.ticker='PVT' AND f.quarter>='2018Q1' GROUP BY f.quarter ORDER BY f.quarter")
yr={}
for r in fin: yr.setdefault(r['quarter'][:4],[]).append(float(r['np'])/B)
print('LNST me theo nam (BQ, ty): '+', '.join(f"{y}:{sum(v):.0f}" for y,v in yr.items() if len(v)==4))
q12 = sum(yr['2026'][:2]); print(f"Kiem: BQ Q1+Q2/26 = {q12:.1f}; BCTC 9T-Q3 = {IS['np_parent'][2]-IS['np_parent'][0]:.1f} (lech {IS['np_parent'][2]-IS['np_parent'][0]-q12:+.1f} — dieu chinh H1 sau soat xet? khong xac dinh)")
# Peers
peers = q("SELECT t.ticker, t.time, t.Close, t.PE, t.PB FROM tav2_bq.ticker AS t WHERE t.ticker IN ('PVP','VOS','VTO','GSP','PVT') AND t.time='2026-10-28'")
print('Peers 28/10 (BQ PE/PB, PE BQ dung EPS nguon BQ):'); [print(f"  {r['ticker']} close {r['Close']} PE {float(r['PE']):.2f} PB {float(r['PB']):.2f}") for r in peers if r['PE']]
# Kich ban (UOC LUONG): LNST me 2027 & PE muc tieu
# LNST me 2027 (uoc luong): xau = ~2025 (1.039) tru KH tau mua dinh/cuoc ve day; co so = Q3/26 nam hoa (1.500) tru ~1/6 phan cuoc/Q2;
# tot = giu muc TTM. PE: xau 6,5 (de-rate dinh chu ky), co so 8,0 (~median BQ 2018- = 8,54, chiet khau nhe), tot 8,5.
scen = {'xau':(0.35, 1000, 6.5), 'co_so':(0.45, 1250, 8.0), 'tot':(0.20, 1500, 8.5)}
print('\n== KICH BAN 2027 (LNST me, PE: UOC LUONG) ==')
ev_px=0
for k,(w,npm,pe_t) in scen.items():
    eps=npm/SH*1e3; fv=eps*pe_t; ev_px+=w*fv
    print(f"{k:6s} w={w:.2f} LNST me {npm} -> EPS {eps:.0f} x PE {pe_t} = {fv:,.0f} ({fv/px_live-1:+.1%} vs {px_live})")
print(f"GIA TRI KY VONG = {ev_px:,.0f} ({ev_px/px_live-1:+.1%}); vung mua bien an toan 15% <= {ev_px*0.85:,.0f}")
print(f"PB tai gia ky vong {ev_px/(bv/SH*1e3):.2f}; PB 1,0 = {bv/SH*1e3:,.0f}")
