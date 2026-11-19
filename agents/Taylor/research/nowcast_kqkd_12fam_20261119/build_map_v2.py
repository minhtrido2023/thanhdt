"""A3 — bản đồ v2 'dữ liệu → ngành → mã' (đóng băng 19/11/2026). Mỗi dòng: mã, họ, khoá, nguồn, dấu, vai trò,
độ trễ PIT giả định (ngày lịch sau cuối quý), câu nhân quả MỘT câu. Không viết được câu nhân quả ⇒ status=EXCLUDED.
a4_family = số họ 1..12 của REPORT §5 A4 (rỗng = trong bản đồ nhưng không phải trial A4)."""
import pandas as pd
TE,SS,MI,TK,HC='trading_economics','sunsirs','macro_indicator','tav2_bq.ticker (tự tính)','data/hog_price_vn.csv'
R=[]
def add(tks,fam,a4,key,src,sign,role,lag,causal,status='IN',note=''):
    for t in tks.split(): R.append(dict(ticker=t,family=fam,a4_family=a4,key=key,source=src,sign=sign,role=role,pit_lag_days=lag,causal=causal,status=status,note=note))
# --- họ cũ (commodity_map_te.csv tier A/B, B2 26/10) — giữ, không phải trial A4 mới ---
add('DRI PHR DPR TRC GVR','rubber_tsr20','', 'rubber',TE,1,'đầu ra',2,'Doanh thu mủ = sản lượng × giá bán, giá bán bám giá cao su TSR20 quốc tế.')
add('DRC CSM','rubber_tsr20_cons','','rubber',TE,-1,'đầu vào',2,'Cao su tự nhiên là nguyên liệu chính của lốp, giá tăng ép biên khi giá lốp điều chỉnh chậm.')
add('PVS PVD PVC PVB','crude','','brent',TE,1,'đầu ra',2,'Khối lượng và giá dịch vụ E&P đi theo chu kỳ đầu tư thượng nguồn do giá dầu dẫn dắt.',note='độ trễ hợp đồng; IC B2 0,03')
add('GAS','crude','','brent',TE,1,'đầu ra',2,'Giá bán khí cho hộ công nghiệp/điện tính theo công thức gắn giá dầu.')
add('BSR','refining','','te_crack_spread_index',TE,1,'đầu ra',2,'Biên lọc dầu xấp xỉ crack spread sản phẩm − dầu thô.')
add('DPM DCM','urea','','urea',TE,1,'đầu ra',2,'Doanh thu phân đạm = sản lượng × giá urea, nguyên liệu khí giá tương đối cố định.')
add('DDV LAS','dap','','di_ammonium',TE,1,'đầu ra',2,'Giá bán DAP/lân bám giá DAP quốc tế.')
add('DDV LAS DGC','sulfur','','sulfur',TE,-1,'đầu vào',2,'Lưu huỳnh là nguyên liệu axit sunfuric để sản xuất DAP/axit photphoric.')
add('SBT LSS QNS','sugar','','sugar',TE,1,'đầu ra',2,'Giá đường nội địa theo giá đường thế giới (biên mậu/nhập khẩu).',note='QNS: đường là mảng phụ cạnh sữa đậu nành')
add('HPG TLH POM SMC','steel_cn','','steel',TE,1,'đầu ra',2,'Giá thép VN bám giá thép Trung Quốc qua cạnh tranh nhập khẩu.')
add('HSG NKG','steel_cn','','steel',TE,1,'đầu ra',2,'Giá thép VN bám giá thép Trung Quốc qua cạnh tranh nhập khẩu.',note='BANNED (chỉ đo KQKD)')
add('HPG','iron_ore','','iron_ore',TE,-1,'đầu vào',2,'Quặng sắt là đầu vào lớn nhất của lò cao HPG.')
add('HPG','coking_coal','','coking_coal',TE,-1,'đầu vào',2,'Than mỡ/cốc là đầu vào thứ hai của lò cao HPG.')
add('VOS','dry_bulk','','baltic_dry',TE,1,'đầu ra',2,'Giá cho thuê tàu hàng rời theo chỉ số cước BDI.')
add('HAH','container','','containerized_freight_index',TE,1,'đầu ra',2,'Cước cho thuê tàu/vận tải container theo mặt bằng cước container.')
add('AAA','pe_pp','','polyethylene',TE,-1,'đầu vào',2,'Hạt PE là nguyên liệu chính của màng/bao bì nhựa.',note='tier D cũ; mô hình kinh doanh AAA đã đa ngành')
add('TCM','cotton','','cotton',TE,-1,'đầu vào',2,'Bông là nguyên liệu kéo sợi của chuỗi sợi-dệt-may TCM.',note='tier D cũ')
add('DDV','liquid_ammonia','','liquid_ammonia',SS,-1,'đầu vào',2,'Amoniac là đầu vào sản xuất DAP cùng axit photphoric.',note='giá TQ, không phải Tampa; giả thuyết')
add('MSR','tungsten','','tungsten_apt',SS,1,'đầu ra',2,'Doanh thu chính của MSR là APT/vonfram bán theo giá thị trường.',note='133 quan sát từ 2026-06-24: chỉ mô tả')
add('CTD VCG HT1','construction','','vn_gdp_construction',MI,1,'hoạt động',60,'Sản lượng xây dựng là khối lượng thi công/tiêu thụ xi măng.',note='trễ công bố dài (giả định 60 ngày); không trong A4')
# --- 12 họ A4 (trial MỚI, khai trước) ---
add('HPG','steel_spread',1,'steel − 1,6×iron_ore_cny − 0,5×coke',f'{TE}+{SS}',1,'chênh lệch',2,'Biên gộp lò cao ≈ giá thép − định mức quặng và cốc trên mỗi tấn thép.',note='hệ số 1,6/0,5 là GIẢ ĐỊNH định mức, khoá trước')
add('DBC BAF','hog_margin',2,'hog_vn − 2,8×(0,65×corn + 0,25×soybean_meal_cny) VND/kg',f'{HC}+{TE}+{SS}+{MI}(FX)',1,'chênh lệch',2,'Biên chăn nuôi heo = giá heo hơi − chi phí thức ăn trên mỗi kg hơi.',note='FCR 2,8 và khẩu phần 65/25 là GIẢ ĐỊNH; BAF BANNED (chỉ đo KQKD)')
add('DGC PAT','yellow_phosphorus',3,'yellow_phosphorus',SS,1,'đầu ra',2,'Doanh thu chính bán phốt pho vàng/sản phẩm P4 theo giá thị trường TQ.')
add('CSV','caustic_soda',4,'caustic_soda',SS,1,'đầu ra',2,'Xút là sản phẩm chính của CSV, giá bán theo mặt bằng khu vực.',note='lịch sử từ 2023-09 ⇒ CHỈ MÔ TẢ, không đủ điều kiện GO')
add('STK','polyester_spread',5,'polyester_staple_fiber − 0,86×pta − 0,34×ethylene_glycol',SS,1,'chênh lệch',2,'Biên sợi polyester ≈ giá xơ − định mức PTA và MEG.',note='định mức 0,86/0,34 là GIẢ ĐỊNH chuẩn ngành; lịch sử từ 2020-10')
add('BMP NTP','pvc_input',6,'polyvinyl',TE,-1,'đầu vào',2,'Bột PVC chiếm phần lớn giá vốn ống nhựa, giá bán điều chỉnh chậm.')
add('MWG FRT DGW PNJ PET','retail',7,'vn_retail_sales_yoy (TB quý)',MI,1,'hoạt động',10,'Doanh thu nhà bán lẻ/phân phối đi theo tổng mức bán lẻ toàn quốc.',note='độ trễ +10 ngày GIẢ ĐỊNH (chưa có vintage)')
add('SSI VCI HCM VND SHS MBS','brokerage',8,'GTGD toàn thị trường TB phiên trong quý (Σ Trading_Value)',TK,1,'hoạt động',0,'Doanh thu phí môi giới và cho vay ký quỹ tỷ lệ với giá trị giao dịch thị trường.')
add('ACV SCS SAS','aviation',9,'vn_tourist_arrivals (Σ quý)',MI,1,'hoạt động',10,'Doanh thu cảng hàng không/dịch vụ sân bay tỷ lệ với lượng khách quốc tế.',note='độ trễ GIẢ ĐỊNH')
add('HVN VJC','aviation_banned','9-mô tả','vn_tourist_arrivals (Σ quý)',MI,1,'hoạt động',10,'Doanh thu hãng bay tỷ lệ với lượng khách.',note='BANNED; đo thêm chỉ mô tả, KHÔNG vào thống kê họ 9')
add('GMD VSC PHP','ports',10,'vn_exports + vn_imports (Σ quý)',MI,1,'hoạt động',15,'Sản lượng container qua cảng đi theo kim ngạch xuất nhập khẩu.',note='độ trễ GIẢ ĐỊNH')
add('VEA HAX','autos',11,'vn_car_registrations (Σ quý)',MI,1,'hoạt động',20,'Doanh thu/lãi liên doanh ô tô tỷ lệ với số xe bán ra.',note='độ trễ GIẢ ĐỊNH')
banks='ABB ACB BAB BID BVB CTG EIB HDB KLB LPB MBB MSB NAB NVB OCB PCB PGB SGB SHB SSB STB TCB TPB VAB VBB VCB VIB VPB'
add(banks,'bank_nim',12,'−[Δ4q(vn_interbank_3m − vn_policy_rate) + Δ4q vn_bond_10y] (pp, TB quý)',MI,1,'chi phí vốn',0,'Chi phí vốn liên ngân hàng/dài hạn tăng ép NIM trước khi lãi cho vay kịp điều chỉnh.',note='28 mã ICB 8355 từng trong universe_pit (REPORT ghi 25); thành viên PIT kiểm tại ngày tín hiệu')
# --- LOẠI: không viết được câu nhân quả trực tiếp / sai hàng ---
X=[('DGC PAT LAS','phosrock','phosphorus→phosphate_rock_cny',TE,'Khoá đổi thành QUẶNG photphat CNY (94% phiên đứng giá), không phải P4 — sai hàng'),
   ('HPG HSG NKG','hrc_us','hrc_steel',TE,'HRC Mỹ, không phải HRC TQ/VN — sai hàng'),
   ('NBC TVD THT','coal','coal',TE,'Than TKV bán theo giá điều tiết/hợp đồng EVN, không theo Newcastle'),
   ('QTP PPC','coal_power','coal',TE,'Nhiệt điện chuyển chi phí than qua hợp đồng EVN, dấu không xác định'),
   ('KSV MSR','tin_copper','tin',TE,'Thiếc không phải sản phẩm chính của KSV/MSR'),
   ('DBC MML','hog_us','lean_hogs',TE,'Heo CME Mỹ không đồng pha heo hơi VN — sai hàng (thay bằng họ 2)'),
   ('DBC','feed','corn',TE,'Đã gộp vào họ 2 (biên heo − TACN)'),
   ('PNJ','gold','gold',TE,'Dấu không xác định (giá vàng tăng: tăng giá bán nhưng giảm sức mua trang sức)'),
   ('LTG TAR','rice_us','rice',TE,'Gạo thô CBOT, không phải gạo VN 5% — sai hàng'),
   ('MSH','cotton_yarn','cotton_yarn',SS,'May mặc mua vải theo đơn FOB/CMT, không mua sợi trực tiếp'),
   ('-','lpg','lpg/propane',SS,'Biên phân phối LPG không có dấu một chiều theo giá'),
   ('-','kcn','vn_fdi/vn_ind_production_yoy/vn_mfg_pmi',MI,'Không viết được câu nhân quả trực tiếp tới doanh thu KCN theo quý'),
   ('-','enso','ONI/ENSO','-','Chưa có ánh xạ nhân quả theo quý tới mã cụ thể'),
   ('-','coffee','coffee',TE,'Arabica, VN chủ yếu Robusta; không có mã niêm yết thuần')]
for tks,fam,key,src,why in X:
    for t in tks.split(): R.append(dict(ticker=t,family=fam,a4_family='',key=key,source=src,sign='',role='',pit_lag_days='',causal='',status='EXCLUDED',note=why))
D=pd.DataFrame(R); D.to_csv('map_v2.csv',index=False)
print(D.status.value_counts().to_dict(), 'A4 rows',(D.a4_family.astype(str).str.match(r'^\d+$')).sum(), 'A4 fams',D[D.a4_family.astype(str).str.match(r'^\d+$')].a4_family.nunique())
