"""DCM — định giá MÙ GIÁ THỊ TRƯỜNG (không có đầu vào giá/vốn hoá/PE của DCM). Đơn vị tỷ đồng; đ/cp = tỷ*1e9/529,4tr.
Nguồn: BCTC HN Q3/2026 (BS 30/9, TM4/5/12/24/25), BQ ticker_financial (LNST năm), BQ commodity_prices WB (urê, Brent năm),
sector read Bobby 04/11/2026 (nhãn & xác suất CYCLICAL .50 / ADMIN .30 / STRUCTURAL .20; công thức proxy biên).
Giả định tự đặt gắn (ước lượng)."""
import csv, json, itertools
SH = 529.4e6
def ps(ty): return ty*1e9/SH
# --- 1. Lịch sử: LNST năm (BQ) vs biên proxy urê−khí (WB) — proxy Bobby: urê − 25×(2,5+0,06×Brent)
np_ = {int(r['yr']): float(r['np_sum_ty']) for r in csv.DictReader(open('calc/bq_np_hist_out.csv')) if r['np_sum_ty'] and r['nq']=='4'}
cm = {int(r['yr']): (float(r['urea']), float(r['brent'])) for r in csv.DictReader(open('calc/bq_commod_out.csv'))}
proxy = {y: u-25*(2.5+0.06*b) for y,(u,b) in cm.items()}
fit_years = [2021,2022,2023,2024,2025]   # chế độ hiện tại: nhà máy đã khấu hao gần hết, nợ dài hạn ~0, net cash lớn
xs=[proxy[y] for y in fit_years]; ys=[np_[y] for y in fit_years]
mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); icpt=my-slope*mx
resid={y: round(np_[y]-(icpt+slope*proxy[y]),0) for y in fit_years}
spread_tc = sum(proxy[y] for y in range(2016,2026))/10      # biên trung bình chu kỳ 10 năm 2016-2025
spread_2026 = proxy[2026]
pred26 = icpt+slope*spread_2026
# --- 2. Bảng cân đối 30/9/2026 (BCTC HN Q3/26)
cash=3470.521; htm=4555.582; pledged=2219.886; st_debt=2699.345; lt_debt=7.511
net_cash = cash+htm+pledged-st_debt-lt_debt
restricted = 332.0    # TM5: tiền gửi 332 tỷ bị hạn chế giao dịch (BGĐ: thu hồi được, không dự phòng) — base GIỮ, độ nhạy −332
# lãi tiền gửi ròng sau thuế nằm trong LNST lịch sử -> tách ra để không vốn hoá tiền mặt ở r
NI_cash_pre = 288.398-70.405     # 2025: lãi tiền gửi − lãi vay (TM27/28 BCTC Q4/25)
TAX_HIST = 0.108                 # thuế hiệu dụng 9T/26 = (242,7+35,2)/2.562,9 (KQKD Q3/26)
# --- 3. Tham số
R0, DEP0 = 0.135, 7.40           # r neo 13,5% @ lãi huy động 12T hiệu dụng 7,40% (cctg_12m 02/11/2026, deposit_rate_vn)
TAX_NEW = 0.20                   # (ước lượng) ưu đãi 10%/15 năm từ khi SX (TM BCTC qua baodautu) — giả định bắt đầu 2012 => hết 2026
EXPORT_TAX_SAVE_PRE = 285.4/0.75 # TM21: thuế XK phát sinh 9T/26 285,4 tỷ -> năm hoá (ước lượng, 9T có XK cao bất thường)
P_EXPORT_TAX0 = 0.55             # Bobby: P(nghị định 0% ban hành trước 31/3/2027)
SPREAD_NEAR = 222                # Bobby: biên proxy T10/2026 & trung vị forecast 60-120 ngày (219-225)
SCEN = {  # biên dài hạn (USD/t urê) theo nhãn Bobby; năm 1 (Q4/26-Q3/27) dùng SPREAD_NEAR cho mọi nhánh
 'CYCLICAL':   dict(p=0.50, s_lr=None),   # = biên trung bình chu kỳ 10 năm (đo)
 'ADMIN_GATED':dict(p=0.30, s_lr=None),   # = CYC + kỳ vọng chính sách (thuế XK 0% P=.55)
 'STRUCTURAL': dict(p=0.20, s_lr=125.0),  # (ước lượng) Bobby: TQ bỏ sàn + Brent cao => biên 100-150; khí Nam Du giá cố định/LNG
}
def lnst_at(s, tax):  # LNST hoạt động (trừ lãi tiền gửi ròng), theo thuế mới
    pbt = (icpt+slope*s)/(1-TAX_HIST) - NI_cash_pre
    return pbt*(1-tax)
def value(s_lr, r=R0, tax=TAX_NEW, extra_pre=0.0, near=SPREAD_NEAR, tax_y1=TAX_HIST, nc_adj=0.0):
    y1 = lnst_at(near, tax_y1) + extra_pre*0           # năm 1 thuế hiện hành
    lr = lnst_at(s_lr, tax) + extra_pre*(1-tax)
    v_ops = y1/(1+r) + (lr/r)/(1+r)                      # năm 1 + vĩnh viễn từ năm 2 (tăng trưởng = 0 thực chất, RONIC=r)
    return v_ops + net_cash + nc_adj, y1, lr
out={}
def run(r=R0, tax=TAX_NEW, s_tc=None, near=SPREAD_NEAR, nc_adj=0.0, p=None, struct=125.0):
    s_tc = spread_tc if s_tc is None else s_tc
    vc,_,lrc = value(s_tc, r, tax, near=near, nc_adj=nc_adj)
    va,_,_ = value(s_tc, r, tax, extra_pre=P_EXPORT_TAX0*EXPORT_TAX_SAVE_PRE, near=near, nc_adj=nc_adj)
    vs,_,lrs = value(struct, r, tax, near=near, nc_adj=nc_adj)
    pp = p or {k:v['p'] for k,v in SCEN.items()}
    ev = pp['CYCLICAL']*vc + pp['ADMIN_GATED']*va + pp['STRUCTURAL']*vs
    return dict(CYC=ps(vc), ADMIN=ps(va), STRUCT=ps(vs), EV=ps(ev), lr_cyc=lrc, lr_struct=lrs)
base = run()
def rdep(dep, beta=1.0): return R0 + beta*(dep-DEP0)/100
if __name__=='__main__':
    L=[]
    L.append(f'1. Hồi quy LNST năm ~ biên proxy (2021-25, n=5): LNST = {icpt:.0f} + {slope:.2f}×biên (tỷ). Phần dư: {resid}')
    L.append(f'   proxy năm: '+', '.join(f'{y}:{proxy[y]:.0f}' for y in sorted(proxy)))
    L.append(f'   biên TB chu kỳ 2016-25 = {spread_tc:.1f}; 2026 (WB 9T) = {spread_2026:.1f} -> LNST dự báo 2026 {pred26:.0f} vs 9T/26 thực 2.285,5 (+Q4)')
    L.append(f'2. Net cash 30/9/26 = {net_cash:.1f} tỷ = {ps(net_cash):,.0f} đ/cp (tiền {cash} + HTM {htm} + ký quỹ phong toả {pledged} − vay NH {st_debt} − DH {lt_debt})')
    L.append(f'   lãi tiền gửi ròng 2025 (trước thuế) tách khỏi LNST = {NI_cash_pre:.1f}')
    L.append(f'3. LNST hoạt động dài hạn (thuế 20%): CYC {base["lr_cyc"]:.0f} · STRUCT {base["lr_struct"]:.0f} tỷ; năm 1 (biên {SPREAD_NEAR}, thuế 10,8%) {lnst_at(SPREAD_NEAR,TAX_HIST):.0f}')
    L.append(f'4. GIÁ TRỊ (đ/cp, trước CK thanh khoản), r={R0:.1%}: CYC {base["CYC"]:,.0f} · ADMIN {base["ADMIN"]:,.0f} · STRUCT {base["STRUCT"]:,.0f} · KỲ VỌNG {base["EV"]:,.0f}')
    sens={}
    for d in (-1.0,-0.5,0.5,1.0):
        for b in (0.5,1.0):
            sens[f'dep{d:+.1f}_b{b}']=round(run(r=rdep(DEP0+d,b))['EV'])
    sens['tax10%']=round(run(tax=TAX_HIST)['EV']); sens['restricted-332']=round(run(nc_adj=-restricted)['EV'])
    sens['near_spread_170']=round(run(near=170)['EV']); sens['near_spread_285']=round(run(near=285)['EV'])
    sens['tc_spread_150']=round(run(s_tc=150)['EV']); sens['tc_spread_210']=round(run(s_tc=210)['EV'])
    sens['struct_100']=round(run(struct=100)['EV']); sens['p_cyc_only']=round(base['CYC'])
    sens['slope_x0.8']=None
    L.append('5. Độ nhạy kỳ vọng (đ/cp): '+json.dumps(sens,ensure_ascii=False))
    # lưới đều để lấy phân vị
    grid=[]
    for r_,tax_,stc,near_,st_,rc in itertools.product([rdep(DEP0+d) for d in (-1,-.5,0,.5,1)],[0.108,0.20],[150,spread_tc,210],[170,222,285],[100,125,150],[0,-restricted]):
        grid.append(run(r=r_,tax=tax_,s_tc=stc,near=near_,struct=st_,nc_adj=rc)['EV'])
    grid.sort(); n=len(grid); q=lambda f: grid[int(f*(n-1))]
    L.append(f'6. Lưới {n} (r±100bp × thuế 10/20% × biên TC 150/{spread_tc:.0f}/210 × năm1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332): '
             f'P10 {q(.1):,.0f} · P25 {q(.25):,.0f} · P50 {q(.5):,.0f} · P75 {q(.75):,.0f} · P90 {q(.9):,.0f}')
    print('\n'.join(L)); open('calc/model_out.txt','w').write('\n'.join(L)+'\n')
    json.dump(dict(base=base,sens=sens,grid=dict(P10=q(.1),P25=q(.25),P50=q(.5),P75=q(.75),P90=q(.9)),net_cash=net_cash,
                   slope=slope,icpt=icpt,spread_tc=spread_tc),open('calc/model_out.json','w'),ensure_ascii=False,indent=1)
