import csv
# --- electricity weighted price (flat 24/7 load); hours per week: peak 5h x6 =30, offpeak 6h x7=42, normal 168-72=96
w={'N':96/168,'T':42/168,'C':30/168}
def wp(n,t,c): return w['N']*n+w['T']*t+w['C']*c
new={'>=220kV':(1771,1101,3110),'35-220kV':(1792,1123,3218),'1-35kV':(1814,1166,3348),'<=1kV':(1966,1274,3586)}
old={'110kV+':(1811,1146,3266),'22-110kV':(1833,1190,3398),'6-22kV':(1899,1234,3508),'<6kV':(1987,1300,3640)}
print('weights',w)
for k,v in old.items(): print('old',k,round(wp(*v),1))
for k,v in new.items(): print('new',k,round(wp(*v),1))
pairs=[('110kV+','>=220kV'),('110kV+','35-220kV'),('22-110kV','35-220kV'),('22-110kV','1-35kV'),('6-22kV','1-35kV'),('<6kV','<=1kV')]
for o,n in pairs:
    a=wp(*old[o]);b=wp(*new[n]);print(o,'->',n,round(a,1),round(b,1),f'{(b/a-1)*100:.2f}%', 'normal-only', f'{(new[n][0]/old[o][0]-1)*100:.2f}%')
# --- per-group reductions EVN
red={'SX':578.1,'SH':424.1,'KD':433.0,'BL':49.54,'HC':47.04}
out={'SX':51.8,'SH':29.9,'KD':6.17,'BL':8.18,'HC':3.8}
tot=sum(red.values());to=sum(out.values())
print('tot red',tot,'tot out%',to)
for k in red: print(k,'red share',round(red[k]/tot*100,1),'output share',out[k],'red per 1% out',round(red[k]/out[k],2))
print('avg per 1% out',round(tot/to,2),'SX ratio',round((red['SX']/out['SX'])/(tot/to),3))
# --- cost sensitivity
dv9=373.218; dv25=501.863; gv9=1128.706
for pct in (0.01,0.02,0.033):
    print('pct',pct,'9T26 DV*pct',round(dv9*pct,2),'annualised(12/9)',round(dv9*pct*12/9,2),'5 months',round(dv9/9*5*pct,2))
print('DV/GVHB9T26',dv9/gv9,'DV/total elem',373.218/1186.038)
etr=14.672/230.384
print('ETR',etr)
for x in (7.46,10.0):
    print(x,'post-tax',x*(1-etr),'%plan280',x*(1-etr)/280*100,'%LNST9T26',x*(1-etr)/215.713*100)
# bottom-up electricity: kWh/t * price * tons
for kwh in (13000,14000):
  for price in (1842.6,1879.4,1904.7):
    for tons in (16000,18000,20000):
      print(kwh,price,tons, round(kwh*price*tons/1e9,1),'bn VND')
