# Quy kết chênh lệch r2 vs bản gốc: gỡ từng đính chính (một lần một) trên đường cơ sở r2
import importlib.util,sys,io,contextlib
spec=importlib.util.spec_from_file_location('m','model.py'); m=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
B=dict(nvl27=m.EN27,nvlLR=m.ENLR,f=m.Ef,p=m.EP,s_exp=m.Esx); b=m.value(**B)
rows=[]
rows.append(('T: s_eff cố định 0,35 (bản gốc)', m.value(m.EN27,m.ENLR,0.9*(1-0.35*m.STEP)+0.1,m.EP,0.35)))
rows.append(('TX: 15% chắc chắn (bản gốc)', m.value(m.EN27,m.ENLR,1-0.751*m.STEP,m.EP,m.Esx)))
rows.append(('O: cố định O2 (= chế độ cơ sở bản gốc)', m.value(m.n27('O2'),m.LR['O2'],m.Ef,m.EP,m.Esx)))
rows.append(('2027: GĐ2 cả năm (bản gốc)', m.value(m.G2_27,m.ENLR,m.Ef,m.EP,m.Esx)))
rows.append(('P: giá giữ 1,0 (bản gốc cơ sở)', m.value(m.EN27,m.ENLR,m.Ef,1.0,m.Esx)))
rows.append(('Điện ×0,98 (bỏ F5)', m.value(**B,elec=0.98)))
rows.append(('Cốc dài hạn 2.108 + định mức 1,5', m.cokeLR.__wrapped__(2108,1.5) if hasattr(m.cokeLR,'__wrapped__') else m.cokeLR(2108,1.5)))
dv0,rs0=m.DV,m.REST; m.DV,m.REST=0.2413,0.0620; rows.append(('DV/khác theo Q3 (bản gốc trộn kỳ)', m.value(**B))); m.DV,m.REST=dv0,rs0
rows.append(('Tiền ròng 415,4 (bản gốc)', m.value(**B,cash=m.NET_CASH0)))
print(f"CO SO r2 {b:,.0f}")
for k,v in rows: print(f"{k:40s} {v:,.0f}  (gỡ đính chính => {v-b:+,.0f})")
