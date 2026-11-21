"""Kiem doc lap r3b (khong import mo hinh): P0/co so voi VC bo phan du 115; dung 2031; + r2 stop 2031."""
r=.135; i=.09; T=3484.88; L=2787.9; E=T-L; SH=450; df=lambda t:(1+r)**-t
def p0(vc, stop=2047):
    w=[.3,.45,.25]; bal=0; pv=0; idc=0
    for k,wk in enumerate(w):
        d=L*wk; c=i*(bal+d/2); idc+=c; bal+=d; pv-=(E*wk+c)*df(k+.5)
    P=L/10; base_tax=503.8/.8*.2; opex=102.01+vc
    ny=stop-2030+1
    ob=L
    for n in range(ny):
        pr = ob if (2030+n==stop) else min(P,ob)
        pv-=(pr+i*(ob-pr/2))*df(3.5+n)
        ob-=pr
    for n in range(ny): pv-=opex*df(3.5+n)
    for n in range(ny): pv+=base_tax*df(3.5+n)   # P0: lo => mat het thue nen (moi nam 2030..stop)
    return pv/SH*1000
print('P0 co so VC 470,29:',round(p0(470.29)),'| VC 355,0:',round(p0(355.0)),'| dung 2031:',round(p0(470.29,2031)))
