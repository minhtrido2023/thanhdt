import sys; sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from simulate_holistic_nav import bq
b=bq("SELECT t.time,t.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean t WHERE t.time>='2014-01-01' ORDER BY t.time")
b.to_csv('base_v34b.csv',index=False)
p=bq("SELECT t.time,t.Close FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time>='2014-01-01' ORDER BY t.time")
p.to_csv('vnindex.csv',index=False)
l=bq("SELECT t.time,t.state,t.state_raw FROM tav2_bq.vnindex_5state_dt5g_live t WHERE t.time>='2014-01-01' ORDER BY t.time")
l.to_csv('dt5g_live.csv',index=False)
print(len(b),b.time.max(),len(p),p.time.max(),len(l),l.time.max())
