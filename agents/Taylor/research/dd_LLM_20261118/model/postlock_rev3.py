# PHA SAU KHOA: gia tham chieu 33.300 (18/11/2026, REPORT rev2) — KHONG truy van gia moi
import importlib.util,os,io,contextlib
H=os.path.dirname(os.path.abspath(__file__)); spec=importlib.util.spec_from_file_location('c',os.path.join(H,'calc_rev3.py')); c=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(c)
P=33300; C=c.ctr(); print(f'gia/tam={P/C:.3f}; tam={C:.0f}; 0.85xtam={0.85*C:.0f}')
lo,hi=0.0,0.3
for _ in range(60):
    m=(lo+hi)/2; v=sum(c.w[k]*c.val(k,gpm=(m if k=='base' else None)) for k in c.w)*(1-c.L); lo,hi=(m,hi) if v<P else (lo,m)
print(f'GPM co so de tam=gia: {m:.4f}')
lo,hi=0.0,1.0
for _ in range(60):
    m=(lo+hi)/2; v=c.ctr(cs=m); lo,hi=(lo,m) if v<P else (m,hi)
print(f'cash share bao hanh can de tam=gia (neu tam van < gia o 0.9% thi khong dat): tam@0.9%={c.ctr(cs=0.009):.0f}')
