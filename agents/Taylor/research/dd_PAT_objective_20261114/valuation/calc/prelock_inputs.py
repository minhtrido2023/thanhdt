# Tính các TỶ LỆ ĐẦU VÀO từ số BCTC (F2 đã đối chiếu ảnh) để ghi vào assumptions — chạy TRƯỚC khoá, không phải mô hình định giá.
import pandas as pd
# kỳ: (DT TP, GV TP, NVL, DV mua ngoài, vận chuyển BH, CPBH, QLDN, tổng CP yếu tố)
P={
'FY25':(1855.383,1421.382,852.216,501.863,66.866,82.151,18.160,1501.275),
'H1/25':(849.079,638.125,392.673,227.773,32.198,42.638,8.719,688.343),
'Q3/25':(1351.881-849.079,1013.634-638.125,595.580-392.673,360.861-227.773,49.575-32.198,63.192-42.638,12.851-8.719,1060.347-688.343),
'Q4/25':(1855.383-1351.881,1421.382-1013.634,852.216-595.580,501.863-360.861,66.866-49.575,82.151-63.192,18.160-12.851,1501.275-1060.347),
'H1/26':(927.491,740.547,456.178,257.918,18.182,27.239,8.038,784.104),
'Q3/26':(1366.520-927.491,1116.065-740.547,709.270-456.178,373.218-257.918,22.844-18.182,32.289-27.239,12.750-8.038,1186.038-784.104),
'9T26':(1366.520,1116.065,709.270,373.218,22.844,32.289,12.750,1186.038),
}
rows=[]
for k,(rv,cg,nvl,dv,tr,bh,ql,tot) in P.items():
    prod=tot-bh-ql            # chi phí sản xuất (ngoài BH+QLDN)
    sp=cg/prod                # tỷ lệ bán/sản xuất theo giá vốn
    dvx=dv-tr
    rest=prod-nvl-dvx
    rows.append(dict(ky=k,DT_TP=rv,GPM_TP=1-cg/rv,NVL_dt=nvl*sp/rv,DVx_dt=dvx*sp/rv,Rest_dt=rest*sp/rv,ban_sx=sp,NVL_DVx=nvl/dvx,SGA=bh+ql))
d=pd.DataFrame(rows); pd.set_option('display.width',200); print(d.round(4).to_string(index=False))
q=pd.read_csv('factpack/data/pat_quarterly_series.csv'); q=q[q.quarter>='2022Q1'].reset_index(drop=True)
q['ttm_np']=q.np.rolling(4).sum(); print(q[['quarter','np','ttm_np']].tail(13).to_string(index=False))
t=q.ttm_np.tail(12); print('median TTM LNST 12 quý gần nhất (3 năm, BQ, Q4/25 chưa KT):',round(t.median(),1))
