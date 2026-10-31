import json,subprocess,collections
C=json.load(open("calc.json")); T=json.load(open("tables.json"))
R="/home/trido/thanhdt/WorkingClaude/mike/"
def n(x): return f"{round(x):,}".replace(",",".").replace("-","−")
def p(x,d=2,sign=True):
    s=f"{x:+.{d}f}" if sign else f"{x:.{d}f}"
    return s.replace(".",",").replace("-","−")
def pn(x,d=2): return f"{x:.{d}f}".replace(".",",")
LIV=open(R+"data/livermore/report_block_2026-10-30_weekly.md").read().strip()
def cli(acc,extra=""):
    return subprocess.run(f"python3 {R}bin/period_table_32.py --account {acc} --report-date 2026-10-30 {extra}",shell=True,capture_output=True,text=True).stdout.strip()
TAB={ "SpaceX":cli("SpaceX"), "ZaloPay":cli("ZaloPay","--with-sleeve")}
VN=[("23/10 (cuối kỳ trước)",1774.15,None),("26/10",1763.55,-0.60),("27/10",1761.87,-0.10),("28/10",1766.65,0.27),("29/10",1755.61,-0.62),("30/10",1741.62,-0.80)]
vn_tab="| Ngày | VN-Index | Thay đổi |\n|---|---:|---:|\n"+"\n".join(f"| {d} | {pn(v)} | "+("—" if c is None else p(c)+"%")+" |" for d,v,c in VN)
def activity(a):
    g=collections.defaultdict(lambda:[0,0])
    for dt,s,tk,q,v,f,t,src in C[a]['trades']:
        x=g[(dt,s,tk)]; x[0]+=q; x[1]+=v
    rows=[]
    for (dt,s,tk),(q,v) in sorted(g.items(), key=lambda kv:(kv[0][0],kv[0][1]!="B",kv[0][2])):
        rows.append((dt[8:10]+"/10","Mua" if s=="B" else "Bán",tk,q,round(v/q),v))
    return rows
def alloc_note(a): return ""
def portfolio(a,withsplit):
    r=T[a]["rows"]; tv,tc,td,tp=T[a]["tot"]; N=T[a]["nav"]
    L=["| Mã | KL | Giá vốn | Giá 30/10 | Giá trị thị trường | % NAV | Lãi/lỗ (%) |","|---|---:|---:|---:|---:|---:|---:|"]
    for t,q,c,px,mv,w,pp,pnl,cost in r: L.append(f"| {t} | {n(q)} | {n(c)} | {n(px)} | {n(mv)} | {pn(w)} | {p(pp)}% |")
    L.append(f"| **Cổ phiếu — tổng ({len(r)} mã)** | | | | **{n(tv)}** | **{pn(tv/N*100)}** | **{p(tp)}%** |")
    if withsplit:
        dg=[x for x in r if x[0]=='DGC'][0]; ot=[x for x in r if x[0]!='DGC']
        otv=sum(x[4] for x in ot); otc=sum(x[8] for x in ot); otp=sum(x[7] for x in ot)
        L.append(f"| *trong đó DGC* | | | | *{n(dg[4])}* | *{pn(dg[5])}* | *{p(dg[6])}%* |")
        L.append(f"| *trong đó các mã còn lại ({len(ot)} mã)* | | | | *{n(otv)}* | *{pn(otv/N*100)}* | *{p(otp/otc*100)}%* |")
        T[a]['split']=(dg[7],dg[8],otp,otc)
    L.append(f"| **Tiền mặt** | | | | **{n(T[a]['cash'])}** | **{pn(T[a]['cash']/N*100)}** | |")
    L.append(f"| **Tiền gửi Trứng vàng** | | | | **{n(T[a]['egg'])}** | **{pn(T[a]['egg']/N*100)}** | |")
    L.append(f"| **Nợ ký quỹ** | | | | **0** | **0,00** | |")
    L.append(f"| **Tổng NAV** | | | | **{n(N)}** | **100,00** | |")
    return "\n".join(L)
def navtab(a):
    L=["| Ngày | NAV (VND) | Thay đổi NAV (đã loại dòng tiền) | Thay đổi VN-Index |","|---|---:|---:|---:|"]
    L.append(f"| 23/10 (cuối kỳ trước) | {n(C[a]['d']['nav'])} | — | — |")
    for d,(nv,r,v) in T[a]["daily"].items(): L.append(f"| {d[8:10]}/10 | {n(nv)} | {p(r)}% | {p(v)}% |")
    return "\n".join(L)
def attr(a):
    c=C[a]; items=sorted(c['attr'].items(), key=lambda kv:-kv[1]); L=["| Nguồn | Đóng góp |","|---|---:|"]
    for t,v in items:
        if round(v)!=0: L.append(f"| {t} | {('+' if v>0 else '−' if v<0 else '')}{n(abs(v))} |")
    L.append(f"| **Biến động giá (gồm phần đã bán trong kỳ)** | **{'−' if c['price']<0 else '+'}{n(abs(c['price']))}** |")
    L.append(f"| Lãi tiền gửi Trứng vàng và lãi tiền gửi không kỳ hạn | +{n(c['interest'])} |")
    L.append(f"| Phí giao dịch ({n(c['fee'])}) và thuế chuyển nhượng ({n(c['tax'])}) | −{n(c['fee']+c['tax'])} |")
    L.append(f"| Thuế thu nhập cá nhân 5% trên cổ tức tiền mặt TV1 (khấu trừ khi chi trả 29/10) | −{n(c['divtax'])} |")
    ex=c['interest']-c['fee']-c['tax']-c['divtax']
    L.append(f"| **Thu nhập ngoài giá (cộng)** | **{'+' if ex>0 else '−'}{n(abs(ex))}** |")
    L.append(f"| **Thay đổi NAV đã loại dòng tiền ngoại sinh** | **{'−' if c['dnadj']<0 else '+'}{n(abs(c['dnadj']))}** |")
    L.append(f"| Dòng tiền ngoại sinh: {'rút' if c['flow']<0 else 'nạp'} vốn 29/10 | {'−' if c['flow']<0 else '+'}{n(abs(c['flow']))} |")
    L.append(f"| **Thay đổi NAV theo sổ (23/10 → 30/10)** | **{'−' if c['dn']<0 else '+'}{n(abs(c['dn']))}** |")
    return "\n".join(L), ex
def acts(a):
    L=["| Ngày | Chiều | Mã | Khối lượng | Giá khớp bình quân | Giá trị (VND) |","|---|---|---|---:|---:|---:|"]
    for d,s,t,q,px,v in activity(a): L.append(f"| {d} | {s} | {t} | {n(q)} | {n(px)} | {n(v)} |")
    return "\n".join(L)
D={}
for a in ("SpaceX","ZaloPay"):
    D[a]=dict(attr=attr(a),acts=acts(a),port=portfolio(a,a=="ZaloPay"),nav=navtab(a))
open("blocks.json","w").write(json.dumps(dict(D=D,TAB=TAB,vn=vn_tab,LIV=LIV),ensure_ascii=False,indent=1))
for a in D: print(a,"\n",D[a]['attr'][:1800],"\n",D[a]['acts'],"\n",D[a]['port'],"\n",D[a]['nav'])
print(TAB["ZaloPay"][:200]); print(T["ZaloPay"].get("split"))
