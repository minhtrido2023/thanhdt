"""SAU KHOA: to hop dieu kien doi nhan dinh (cung mo hinh model_r3, khong sua tham so goc)."""
import sys; sys.dont_write_bytecode=True
import model_r3 as R
B=R.BASE
C={'TIEU CUC: Q4/26 bien gop <28% (W 15/60/20/5) + gia So XD Q2/27 <-7% (PW 25/50/25) + capex +30%':
     dict(W={'tot':.15,'co_so':.60,'xau':.20,'rat_xau':.05},PW={'flat':.25,'g2031':.5,'real':.25},CAPEX_LEFT=B['CAPEX_LEFT']*1.3),
   'TIEU CUC nhe: chi W 15/60/20/5 + PW 25/50/25': dict(W={'tot':.15,'co_so':.60,'xau':.20,'rat_xau':.05},PW={'flat':.25,'g2031':.5,'real':.25}),
   'TICH CUC: bien gop >=35% (W 35/50/10/5) + So XD >+7% (PW 5/35/60) + capex -30%':
     dict(W={'tot':.35,'co_so':.50,'xau':.10,'rat_xau':.05},PW={'flat':.05,'g2031':.35,'real':.60},CAPEX_LEFT=B['CAPEX_LEFT']*0.7),
   'TICH CUC nhe: chi W 35/50/10/5 + PW 5/35/60': dict(W={'tot':.35,'co_so':.50,'xau':.10,'rat_xau':.05},PW={'flat':.05,'g2031':.35,'real':.60}),
   'Mo moi bo/dung (san dung ap moi kb) + capex khong chi': dict(floor_all=True)}
for k,v in C.items(): print(f'{k:100s} {R.EV(v):8,.0f} ({R.EV(v)-R.EV():+,.0f})')
