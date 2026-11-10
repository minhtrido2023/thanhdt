"""Make a patched COPY of pt_v22_dt5g.py: alt price pkls + non-canonical output names (coding_guidelines §8). usage: tag pxpkl ovpkl"""
import sys,re
tag,pxp,ovp=sys.argv[1:4]
WC="/home/trido/thanhdt/WorkingClaude"; R=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110/engine"
s=open(f"{WC}/pt_v22_dt5g.py").read()
n0=s.count('"data/earnings_px.pkl"')+s.count('"data/lagged_pos_ov.pkl"')
s=s.replace('open("data/earnings_px.pkl","rb")',f'open(r"{pxp}","rb")').replace('open("data/lagged_pos_ov.pkl","rb")',f'open(r"{ovp}","rb")')
s,k=re.subn(r'os\.path\.join\(WORKDIR, "data", "pt_v22_dt5g_',f'os.path.join(r"{R}", "{tag}_',s)
open(f"{R}/pt_{tag}.py","w").write(s); print("pkl refs",n0,"output paths patched",k)
