"""B1: commodity_map_te.csv = bản đồ mã VN <-> metric_key TE daily. KHÔNG đè commodity_map.csv đóng băng (prereg2)."""
import pandas as pd
# family, te_key, tickers, sign(+1 producer / -1 consumer), tier(A=panel chính B2/B3, B=phụ/proxy, D=chỉ mô tả), trap/note
R=[
("rubber_tsr20","rubber","DRI PHR DPR TRC GVR",+1,"A","TE=TSR20 (USc/kg), KHÔNG phải RSS3 của WB; TNC/DRG universe quá ngắn bỏ"),
("rubber_tsr20_cons","rubber","DRC CSM",-1,"B","lốp: cao su là chi phí, chiều ngược; SRC hết universe 2022"),
("crude","brent","PVS PVD PVC PVB GAS",+1,"A","Brent TE daily; WB 'crude average' khác định nghĩa — không nối"),
("refining","te_crack_spread_index","BSR",+1,"B","TE Crack Spread Index (chỉ số tổng hợp, không phải crack Singapore); BSR từ 2018"),
("urea","urea","DPM DCM",+1,"A","TE urea chỉ từ 2019-06 (37% phiên đứng giá) => IS ngắn; khí đầu vào neo dầu"),
("dap","di_ammonium","DDV LAS",+1,"A","TE DAP từ 2019-06, 63% phiên đứng giá (cập nhật ~tuần)"),
("phosrock","phosphorus","DGC PAT LAS",+1,"D","BẪY TÊN: TE 'phosphorus' ~1.000 CNY/t = QUẶNG photphat TQ, KHÔNG phải P4 (~20-30k CNY/t); từ 2022-08, 94% phiên đứng giá, 43 giá trị => vô dụng cho tín hiệu"),
("sulfur","sulfur","DDV LAS DGC",-1,"B","lưu huỳnh = đầu vào axit H2SO4 cho DAP/lân => chiều ngược; 2026 tăng x7 so 2020 (CHƯA xác minh đơn vị)"),
("sugar","sugar","SBT LSS QNS",+1,"A","ICE #11 USc/lb; giá nội địa có thuế CBPG; SLS rời universe 2026-07"),
("steel_cn","steel","HPG HSG NKG TLH POM SMC",+1,"A","SHFE thép cây CNY/t (giá TQ – neo nhập khẩu VN); HSG/NKG BANNED giao dịch nhưng giữ để đo"),
("hrc_us","hrc_steel","HPG HSG NKG",+1,"B","BẪY: TE hrc_steel USD/t ~ HRC Mỹ (CME, đỉnh 1.945 năm 2021) — KHÔNG phải HRC TQ/VN"),
("iron_ore","iron_ore","HPG",-1,"B","quặng = CHI PHÍ của HPG => chiều ngược (biên = thép − quặng − than)"),
("coking_coal","coking_coal","HPG",-1,"B","than cốc = chi phí; TE từ 2019-11"),
("coal","coal","NBC TVD THT",+1,"D","Newcastle USD/t; than TKV bán EVN giá điều tiết => proxy lỏng; universe ngắn/đứt"),
("dry_bulk","baltic_dry","VOS",+1,"A","BDI TE daily khớp csv 98% (Winston 10-26); VNA hết universe 2024"),
("container","containerized_freight_index","HAH",+1,"A","chỉ số container ~SCFI, 81% phiên đứng giá (tuần); HAH trễ ~2Q (freight_map)"),
("tin_copper","tin","KSV MSR",+1,"D","KSV universe từ 2021-11; MSR KHÔNG có vonfram — thiếc/đồng chỉ phụ phẩm"),
("hog_us","lean_hogs","DBC MML",+1,"D","BẪY: CME Lean Hogs (Mỹ) không đồng pha heo hơi VN (dịch ASF); dùng data/hog_price_vn.csv (2019+) thay"),
("feed","corn","DBC",-1,"D","ngô/khô đậu = chi phí TACN; corn CBOT"),
("pvc","polyvinyl","BMP NTP",-1,"B","PVC TQ CNY/t = nguyên liệu ống nhựa => chiều ngược"),
("pe_pp","polyethylene","AAA",-1,"D","AAA thương mại hạt nhựa/ bao bì – pass-through"),
("gold","gold","PNJ",+1,"D","vàng: lãi tồn kho, nhưng cầu trang sức giảm khi vàng đắt — dấu không rõ"),
("cotton","cotton","TCM",-1,"D","bông = chi phí sợi/dệt"),
("rice_us","rice","LTG TAR",+1,"D","BẪY: TE rice = gạo thô CBOT Mỹ (USD/cwt), KHÔNG phải gạo VN 5%; WB có VN 5% monthly"),
("coffee","coffee","",+1,"D","Arabica ICE; VN sản xuất Robusta; không có mã niêm yết thuần cà phê"),
]
rows=[]
for fam,key,tks,sg,tier,note in R:
    for t in (tks.split() or ["-"]):
        rows.append(dict(ticker=t,family=fam,te_metric_key=key,sign=sg,tier=tier,note=note))
m=pd.DataFrame(rows); m.to_csv("commodity_map_te.csv",index=False)
print(m.groupby('tier').ticker.count(), len(m))
