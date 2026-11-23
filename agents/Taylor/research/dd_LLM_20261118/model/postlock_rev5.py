# PHA SAU KHOA: gia tham chieu 33.300 (18/11/2026, REPORT rev2) — KHONG truy van gia moi
import importlib.util,os,io,contextlib
H=os.path.dirname(os.path.abspath(__file__)); spec=importlib.util.spec_from_file_location('c',os.path.join(H,'calc_rev5.py')); c=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(c)
P=33300; C=c.ctr(); print(f'gia/tam={P/C:.3f}; tam={C:.0f}; 0.85xtam={0.85*C:.0f}')
lo,hi=0.0,50.0
for _ in range(80):
    m=(lo+hi)/2; lo,hi=(m,hi) if c.ctr(p=m)<P else (lo,m)
print(f'hazard giai phong p can de tam=gia: {m:.3f}/nam (f_cash={c.fcash(m,c.r0):.3f})')
print(f'tam khi f=1 (khong mac ket): {c.ctr(fover=1.0,inv_trap=False):.0f} => gia/tam={P/c.ctr(fover=1.0,inv_trap=False):.3f}')
