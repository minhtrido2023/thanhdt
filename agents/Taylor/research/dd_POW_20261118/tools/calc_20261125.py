"""Phép tính số học cho DD POW 25/11/2026 (đầu vào là số đọc từ BCTN/BCTC/CBTT, ghi trong REPORT_rev5 Phụ lục F)."""
cap=1624; H=8760; h9=6552; hr=6543   # MW; giờ/năm; giờ 9T (273 ngày); suất hao BTU/kWh (ước lượng, REPORT_rev4 §4)
full=cap*H/1e6        # tỷ kWh
print("100% CS:",round(full,2),"tỷ kWh; 9 tỷ kWh =",round(9/full*100,1),"%; Qc65% =",round(.65*full,2),"tỷ kWh; 75-80% =",round(.75*full,2),round(.8*full,2))
print("thực 9T 3,757 tỷ kWh: CF",round(3.757/(cap*h9/1e6)*100,1),"%; năm hoá",round(3.757*4/3,2))
mm=lambda tkwh: tkwh*1e9*hr/1e6/1e6   # tr MMBtu
print("MMBtu: term 20,7 -> tỷ kWh",round(20.7e6*1e6/hr/1e9,2),"=",round(20.7e6*1e6/hr/1e9/full*100,1),"% CS")
print("cần cho 9 tỷ kWh",round(mm(9),1),"; cho 5,0 tỷ",round(mm(3.757*4/3),1),"; 9T thực",round(mm(3.757),1),"vs nhận 23,8; 75% CS",round(mm(.75*full),1),"80%",round(mm(.8*full),1))
print("term/need9:",round(20.7/mm(9)*100,1),"% ; term/need_actual:",round(20.7/mm(3.757*4/3)*100,1))
# nợ
fy_usd,fy_vnd=14403.396,5118.957; print("FY25 USD%",round(fy_usd/(fy_usd+fy_vnd)*100,1))
ci,smbc=11261.9,4035.6; lt=20134.7; usd=ci+smbc
print("Q3 USD-bank",usd,round(usd/lt*100,1),"%; VND-bank",round(lt-usd,1))
print("±1% USD/VND tỷ",round(usd*.01,1),"sau thuế",round(usd*.01*.891,1),"đ/cp",round(usd*.01*.891/3067.845688*1000,1))
print("+100bp LT tỷ",round(lt*.01,1),"sau thuế",round(lt*.01*.891,1),"đ/cp",round(lt*.01*.891/3067.845688*1000,1),"% LNST cốt lõi nămhoá",round(lt*.01*.891/5362*100,2))
print("lãi vay: 2025 KQKD+vh",655.4+791.0,"2024",381.6+622.0,"2026E",round(1535.7*4/3,0),"ratio KQKD",round(1535.7*4/3/655.4,2),"ratio kinh tế",round(1535.7*4/3/(655.4+791.0),2))
# kịch bản upside
E=9000; r=.135; sh=3067.845688
for n in (1500,2500):
    v=n/r; print("LNST",n,"ROE",round(n/E*100,1),"V",round(v),"+",round(v-E),"tỷ =",round((v-E)/sh*1000),"đ/cp; tâm9387+",round(9387+(v-E)/sh*1000))
print("NPV0 LNST",round(E*r),"; margin",round(1500/35000*100,1),round(2500/30000*100,1),"; giá/kWh",round(30000/9),round(35000/9))
