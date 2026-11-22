import json
L=json.load(open('kb/dd_price_zones.json'))['entries']
def last(t):
    return max((e for e in L if e['ticker']==t), key=lambda e:(e['dd_date'],e.get('rev',1)))
def ddref(t):
    e=last(t); return {"ticker":t,"dd_date":e['dd_date'],"rev":e.get('rev',1),"center":e['center'],"zone_low":e['zone_low'],"zone_high":e['zone_high'],"source":"kb/dd_price_zones.json (đọc từ sổ lúc dựng thẻ)"}
APPR="user 22/11/2026 19:27 ICT (decided_by: user): \"Discretionary sleeve không cần quy tắc thoát cố định\" — SPEC B3; kb/projects/dd-upgrade-final-action-20261122.md mục B3"
def exitp(extra=None):
    d={"kind":"user_decides","approval_ref":APPR,"note":"value_long: thoát do user quyết; KHÔNG stop/TIME/target cố định. Thẻ chỉ hiển thị/nhắc."}
    if extra: d["legacy_rules_note"]=extra
    return d
DD={"pct":15,"protocol":"rà 48 giờ theo thẻ — KHÔNG phải lệnh bán, KHÔNG phải stop","reviewer":"user (Mike nhắc)"}
def ms(id,date,metric,thr,dirn,src,owner,basis="công bố/hạn theo nguồn",note=""):
    return {"id":id,"date":date,"date_basis":basis,"metric":metric,"threshold":thr,"direction":dirn,"source":src,"owner":owner,"status":"pending","checked_at":None,"note":note}
def ab(id,cond,how,cur="chưa kiểm"):
    return {"id":id,"condition":cond,"how_measured":how,"current_status":cur}
FPTS="agents/Taylor/research/dd_upgrade_20261122/A1_fpt_thesis_audit/THESIS_CARD.md"
cards=[
{"ticker":"FPT","rev":1,"accounts":["SpaceX","ZaloPay"],"deal_type":"value_long",
 "exit_policy":exitp("FPT đã gỡ khỏi data/discretionary_exit_rules.json 22/11 (bak_20261122_fpt_exempt). Plan nháp 23/11 có STOP SELL 800/500 chưa duyệt — user quyết."),
 "entry":{"date":"2026-11-06","cost":{"SpaceX":{"qty":800,"cost_price":51137.5},"ZaloPay":{"qty":500,"cost_price":51160.0}},"source":"data/execution_logs/dnse_raw_2026-11-20.jsonl positions costPrice (DNSE)"},
 "thesis":["Kỳ vọng trọng số 57.312, vùng P10–P90 45.270–68.466 (rev3, skeptic CONFIRMED 09/11); §2.5 fear-buy KHÔNG đủ điều kiện.","Chân trời DD 5 năm ≠ deal 25 phiên; giá 20/11 = 45.000 ≈ trung bình nhánh XẤU.","Nguồn: "+FPTS+" (v2 qua skeptic)."],
 "dd_ref":ddref("FPT"),
 "milestones":[
  ms("FPT-M1","2026-11-27","GDKHQ cổ tức 1.000đ","DNSE điều chỉnh giá từ tối 26/11 ⇒ P&L đọc thấp thêm ≈2pp cơ học","info","THESIS_CARD §0 (corporate_action BQ)","Taylor"),
  ms("FPT-M2","2026-11-30","Ngày chốt quyền cổ tức","—","info","THESIS_CARD §4","Taylor"),
  ms("FPT-M3","2026-12-10","Trả cổ tức 1.000đ (cổ tức đã hứa không bị huỷ)","trả đúng hạn","abandon_if_cancelled","THESIS_CARD §2/§4","Taylor"),
  ms("FPT-M4","2026-12-10","KQKD tháng 10–11: ký mới NN luỹ kế","<+15% ⇒ hạ nhận định","lower_if_below","REPORT.md:166, r2 §8 (THESIS_CARD §2)","Taylor","ước lượng (chưa có lịch công bố; cửa sổ giữa 11 và 12/2026)","chưa kiểm số tháng 10"),
  ms("FPT-M5","2026-12-10","Tin pháp lý/CBTT FTEL, FOX (thu hồi/chuyển giao ngoài giá thị trường, pha loãng)","có tin bất lợi ⇒ hạ","lower_if_bad_news","THESIS_CARD §2; cần legal-vn/web quét sau 01/11","legal-vn","ước lượng (mốc rà trước khi quyết)","chưa quét pháp lý sau 01/11"),
  ms("FPT-M6","2026-12-10","Lãi huy động 12T (effective_deposit_rate)","+100bp so hiện 7,4% hiệu dụng ⇒ hạ","lower_if_above","r2 §8; cctg 02/11, Big-4 12M 6,8% (16/11)","Taylor","liên tục — ngày = mốc rà","chưa xảy ra"),
  ms("FPT-M7","2027-01-31","BCTC Q4/2026 (kiểm toán, khoản 618,8 tỷ, CFO 2026)","xem abandon_triggers","info","THESIS_CARD §2","Taylor","ước lượng (≈cuối 01/2027)")],
 "abandon_triggers":[
  ab("FPT-A1","Kiểm toán ngoại trừ/từ chối","BCTC kiểm toán 2026 (≈cuối 01/2027) — THESIS_CARD §2; HARD ABANDON r3 §9"),
  ab("FPT-A2","Khoản 618,8 tỷ không thu hồi lớn hơn đã ghi","BCTC Q4/2026 thuyết minh — THESIS_CARD §2"),
  ab("FPT-A3","CFO 2026 âm cả năm","BCTC năm 2026 (≈Q1/2027) — THESIS_CARD §2"),
  ab("FPT-A4","Cổ tức đã hứa bị huỷ","CBTT FPT trước 10/12/2026 — THESIS_CARD §2 (§3 #4)"),
  ab("FPT-A5","FTEL thu hồi/chuyển giao ngoài giá thị trường; FTEL pha loãng/FOX mất tư cách đại chúng","quét CBTT + legal-vn/web (chưa quét sau 01/11) — THESIS_CARD §2")],
 "open_items":["Giá giảm 16–20/11 kèm KL 1,4–1,7× Volume_1M: chưa tách được yếu tố cổ phiếu thưởng 171,4M (giao dịch từ 12/11) — THESIS_CARD §3","Tin/CBTT FPT ngoài corporate_action: chưa kiểm"]},
{"ticker":"NNC","rev":1,"accounts":["SpaceX","ZaloPay"],"deal_type":"value_long",
 "exit_policy":exitp("NNC vẫn còn ngưỡng stop −10%/TARGET +10%/TIME 25 phiên trong data/discretionary_exit_rules.json — chờ user xác nhận gỡ (chỉ đạo 22/11 chưa nêu rõ NNC/VGS)."),
 "entry":{"date":"2026-11-06","cost":{"SpaceX":{"qty":400,"cost_price":46675.0},"ZaloPay":{"qty":300,"cost_price":46950.0}},"source":"data/execution_logs/dnse_raw_2026-11-20.jsonl positions costPrice (DNSE)"},
 "thesis":["Tâm kỳ vọng 61.273 (r3, skeptic CONFIRMED 08/11), vùng P10–P90 30.375–95.341; điểm yếu chính: tâm hàm ý ROE bền ≈24% (biên đá ở đỉnh 15 năm).","Biên an toàn CÓ ĐIỀU KIỆN: giá đá cụm từ 2028 giữ; thanh khoản mỏng (~1,4–1,5 tỷ/phiên).","Nguồn: agents/Taylor/research/dd_redo_20261105/NNC/REPORT_r3.md (+REPORT_r2.md §7–§8)."],
 "dd_ref":ddref("NNC"),
 "milestones":[
  ms("NNC-M1","2027-01-20","BCTC Q4/2026: biên gộp","≥55% tích cực; <45% khi doanh thu đi ngang ⇒ tiêu cực","two_sided","REPORT_r2.md §8","Taylor","ước lượng (~20/01/2027)"),
  ms("NNC-M2","2027-01-20","Hợp đồng thuê Núi Nhỏ (thuyết minh)","bên thứ ba tới 2043 = tích cực; tới 2030/bên liên quan, giá dưới thị trường = tiêu cực","two_sided","REPORT_r2.md §8 + §7 (NHC bên liên quan)","Taylor","ước lượng (khi có thuyết minh; r3 §8a)"),
  ms("NNC-M3","2027-04-20","BCTC Q1/2027: biên gộp","≥55% / <45%","two_sided","REPORT_r2.md §8","Taylor","ước lượng (~20/04/2027)"),
  ms("NNC-M4","2027-06-30","Giá đá Sở XD Q2/2027","> Q3/2026 +7% tích cực; < −7% tiêu cực","two_sided","REPORT_r2.md §8","Taylor","ước lượng (cuối Q2/2027)"),
  ms("NNC-M5","2027-06-30","Vành đai 4 / mỏ đấu giá trong cụm","≥20% khối lượng tích cực; <20% (mỏ mới cấp sớm) tiêu cực","two_sided","REPORT_r2.md §8","Taylor","hạn theo nguồn (tới 30/06/2027)"),
  ms("NNC-M6","2026-12-31","legal-vn xác minh: MVC ≥51% NNC ⇒ Luật DN Đ195 buộc thoái 10,3% MVC (≈142 tỷ)?","xác minh được/không","open_item","REPORT_r2.md §7 (cần legal-vn)","legal-vn","ước lượng (mốc rà, chưa có hạn công bố)","chưa kiểm")],
 "abandon_triggers":[
  ab("NNC-A1","Thu hồi/đình chỉ giấy phép Mũi Tàu","CBTT NNC + UBND TP.HCM — REPORT_r2.md §8 HARD ABANDON (1)"),
  ab("NNC-A2","Truy thu mới làm tổng truy thu tăng vật chất (> +20 tỷ ≈ +900 đ/cp)","BCTC/CBTT — REPORT_r2.md §8 (2); hiện tổng ≈42 tỷ ≈1.900 đ/cp (§7)"),
  ab("NNC-A3","MVC ≥51% kéo theo buộc thoái sở hữu chéo với giá bất lợi cho cổ đông thiểu số","CBTT MVC/NNC + legal-vn — REPORT_r2.md §8 (3)"),
  ab("NNC-A4","Dồn tiền giữ lại vào BĐS (nghị quyết đầu tư > 30% tiền ròng)","NQ ĐHĐCĐ/HĐQT — REPORT_r2.md §8 (4)")],
 "open_items":["CBTT 17/04/2026 NNC trúng đấu giá quyền khai thác khoáng sản (UBND TP.HCM): chưa đối chiếu mỏ nào/giá/hạn — REPORT_r2.md §7","Cờ E12 truy thu mỏ Mũi Tàu CHƯA ĐÓNG (dd_NNC_20261030/SKEPTIC_20261031.md)"]},
{"ticker":"VGS","rev":1,"accounts":["SpaceX","ZaloPay"],"deal_type":"value_long",
 "exit_policy":exitp("VGS vẫn còn ngưỡng target +15%/stop −10%/TIME 25 phiên trong data/discretionary_exit_rules.json — chờ user xác nhận gỡ."),
 "entry":{"date":"2026-11-12","cost":{"SpaceX":{"qty":2300,"cost_price":20000.0},"ZaloPay":{"qty":1500,"cost_price":20000.0}},"source":"data/execution_logs/dnse_raw_2026-11-20.jsonl positions costPrice (DNSE)"},
 "thesis":["Tâm 26.526 (r2, kỳ vọng trọng số 18 kết cục), vùng 19.393–34.722; giá vào ≈ sát P10 ở cỡ ≤1 tỷ (MONG MANH).","Skeptic r1 INCONCLUSIVE (medium, 22/11): số khớp BCTC nhưng thiếu Legend City/capex thay thế/quỹ khen thưởng…; chiều xuống ≈−14…−16% (ước lượng) vs lên +2…+5%.","Nguồn: agents/Taylor/research/dd_VGS_20261110/REPORT.md + skeptic/r1.json."],
 "dd_ref":ddref("VGS"),
 "milestones":[
  ms("VGS-M1","2027-01-31","Lãi liên kết Q4/2026","≥35 tỷ tích cực; <25 tỷ hai quý liền (Q4/26,Q1/27) hoặc <22,8 ⇒ xấu; <10 tỷ nặng","two_sided","REPORT.md §8 M1 (ngưỡng là ước lượng)","Taylor"),
  ms("VGS-M2","2027-01-31","Biên gộp hợp nhất Q4/2026","≥4,5% hai quý liền / <3,0% hai quý liền","two_sided","REPORT.md §8 M2","Taylor"),
  ms("VGS-M3","2027-03-31","Phải thu KH 31/12/2026","≤400 tỷ không dự phòng / >800 tỷ hoặc trích dự phòng 2 khách lớn","two_sided","REPORT.md §8 M3","Taylor"),
  ms("VGS-M4","2027-12-31","Legend City: CBTT mở bán / doanh thu NOXH GĐ1","có giá bán kiểm được / XDCB tăng tiếp không bán ⇒ base ×0,85","two_sided","REPORT.md §8 M4","Taylor"),
  ms("VGS-M5","2027-03-31","Ý kiến kiểm toán BCTC 2026 + giải trình cổ tức liên kết 2025 (W2)","chấp nhận toàn phần / ngoại trừ-điều chỉnh hồi tố","two_sided","REPORT.md §8 M5","Taylor"),
  ms("VGS-M6","2026-12-31","Lãi huy động 12T (effective_deposit_rate)","−50bp tích cực / +50bp tiêu cực","two_sided","REPORT.md §8 M6","Taylor","liên tục — ngày = mốc rà"),
  ms("VGS-M7","2027-03-31","Thuế AD HRC TQ còn hiệu lực (Bobby F8, P 0,90)","bị huỷ ⇒ kịch bản xấu nặng hơn","lower_if_cancelled","REPORT.md §8 M7","Taylor"),
  ms("VGS-O1","2026-12-31","Lấy Tờ trình 05/2026/TT-ĐHĐCĐ-VGP (Legend City: tổng mức đầu tư, tiến độ) + Tờ trình 02/2026 (trích quỹ)","đã có/chưa","open_item","skeptic/r1.json recommended_followups[0]","Taylor","ước lượng (mốc rà)","chưa kiểm"),
  ms("VGS-O2","2026-12-31","Tình trạng tiền sử dụng đất QĐ 1829/2020, 2954/2021, 341/2024","đã nộp/treo","open_item","skeptic/r1.json recommended_followups[1]","Taylor","ước lượng (mốc rà)","chưa kiểm"),
  ms("VGS-O3","2026-12-31","Thuyết minh dự phòng phải trả (31,4→10,0): −21,1 tỷ là hoàn nhập vào lãi lỗ?","nếu hoàn nhập ⇒ GPM kịch bản tốt về ≈4,05%","open_item","skeptic/r1.json recommended_followups[2]","Taylor","ước lượng (mốc rà)","chưa kiểm")],
 "abandon_triggers":[
  ab("VGS-A1","Kiểm toán ngoại trừ/điều chỉnh hồi tố cổ tức liên kết 2025","BCTC kiểm toán 2026 (31/03/2027) — REPORT.md §8 M5"),
  ab("VGS-A2","Thuế AD HRC TQ bị huỷ","CBTT Bộ Công Thương — REPORT.md §8 M7"),
  ab("VGS-A3","Legend City: XDCB tăng tiếp, không bán, không xong GPMB","BCTC + CBTT dự án — REPORT.md §8 M4")],
 "open_items":["Skeptic r1 INCONCLUSIVE: Legend City cam kết vốn/tiền sử dụng đất không lượng hoá được; nhà máy ống khấu hao 82%; quỹ khen thưởng ≈5,9 tỷ/năm; thuê đất tới 2051 — skeptic/r1.json missing_items","Liên kết 28,6% định giá 1,65× sổ không có BCTC liên kết; TTM đếm Q4/25 hai lần"]}]
for c in cards:
    c.update({"drawdown_review":DD,"last_review_at":"2026-11-22","status":"active","draft_pending_user_review":True,"recorded_at":"2026-11-22T20:50:00+07:00"})
doc={"schema":"thesis_cards/v1","doc":"Sổ THẺ LUẬN ĐIỂM vị thế discretionary — CHỈ HIỂN THỊ/NHẮC, không đổi lệnh/luật thoát. Append-only theo (ticker, rev): đổi nội dung = THÊM thẻ rev+1 (supersedes). Bản rev cao nhất của mã thắng. SPEC B3 22/11/2026.","deal_types":["value_long","event_trade","fixed_rules"],"cards":cards}
json.dump(doc,open('kb/thesis_cards.json','w'),ensure_ascii=False,indent=1); open('kb/thesis_cards.json','a').write("\n")
print(len(cards))
