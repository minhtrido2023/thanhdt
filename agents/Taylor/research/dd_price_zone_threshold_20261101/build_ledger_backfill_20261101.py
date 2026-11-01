import json
R = "agents/Taylor/research/"
P = "kb/projects/"
def E(ticker, dd_date, q, low, center, high, price, pdate, verdict, src, ev, skeptic, center_kind=None,
      center_range=None, null_reason=None, notes=None, recorded_at="2026-11-01T23:00:00+07:00"):
    import datetime as d
    exp = (d.date.fromisoformat(dd_date) + d.timedelta(days=120)).isoformat()
    return {"ticker": ticker, "dd_date": dd_date, "bctc_quarter": q, "zone_low": low, "center": center,
            "zone_high": high, "center_range": center_range, "center_kind": center_kind,
            "price_ref": price, "price_date": pdate, "verdict_label": verdict, "source_file": src,
            "evidence": [{"file": f, "quote": qq, "fields": fl} for f, qq, fl in ev],
            "skeptic_status": skeptic, "expires_on": exp, "expires_basis": "dd_date+120 (mặc định); công cụ ghi đè bằng ngày công bố BCTC quý mới hơn đọc lúc chạy (PIT)",
            "null_reason": null_reason, "notes": notes, "recorded_at": recorded_at}
ents = []
f = R+"dd_FPT_20261101/investor_report/FPT_DD_investor_report_20261101.md"
ents.append(E("FPT","2026-11-01","2026Q3",55000,59800,66700,52700,"2026-10-30","trung dung — giá DƯỚI vùng cơ sở",f,
  [(f,"**55,0–66,7k**, tâm 59,8k",["zone_low","zone_high","center"]),(f,"giá 52.700 dưới vùng cơ sở 55–67k",["price_ref"])],
  "REFUTED-đã-áp (mức văn bản; v2)", center_kind="tâm (kịch bản cơ sở)", notes="kỳ vọng có trọng số 54,8k thấp hơn tâm; giá còn quyền cổ tức 1.000đ"))
f = R+"dd_HHS_20261101/investor_report/HHS_DD_investor_report_20261101.md"
ents.append(E("HHS","2026-11-01","2026Q3",7600,9950,13000,9450,"2026-10-30","trung dung — TRONG vùng, nửa dưới",f,
  [(f,"Giá 9.450 đ (đóng cửa 30/10/2026) nằm TRONG vùng giá trị hợp lý ≈7.600–13.000 đ, thấp hơn tâm ≈9.950–10.250 đ",["price_ref","zone_low","zone_high","center","center_range"])],
  "REFUTED-đã-áp (medium; v2)", center_kind="tâm (cận dưới của khoảng tâm)", center_range=[9950,10250],
  notes="LNST Q3 chưa soát xét; HHS nằm trong forensic_flags exclude (công cụ gắn cờ)"))
f = R+"dd_SIP_20261101/investor_report/SIP_DD_investor_report_20261101.md"
ents.append(E("SIP","2026-11-01","2026Q3",42000,47700,55000,48350,"2026-10-30","trung dung — TRONG vùng, tại tâm",f,
  [(f,"Giá 48.350 đ (khớp cuối 30/10/2026) nằm TRONG vùng giá trị hợp lý ≈42.000–55.000 đ, ngay tại tâm ≈47.700–50.300 đ",["price_ref","zone_low","zone_high","center","center_range"])],
  "REFUTED-đã-áp (medium; 11/11 đính chính)", center_kind="tâm (cận dưới của khoảng tâm)", center_range=[47700,50300]))
f = R+"dd_TV2_20261101/investor_report/TV2_DD_investor_report_20261101.md"
ents.append(E("TV2","2026-11-01","2026Q3",17100,20700,25300,27000,"2026-10-30","trung dung — TRÊN vùng cơ sở (+31% so kỳ vọng)",f,
  [(f,"Giá 27.000 đ (đóng cửa 30/10/2026) cao hơn giá trị kỳ vọng ≈20.700 đ khoảng 31% và nằm TRÊN vùng giá trị hợp lý cơ sở 17.100–25.300 đ",["price_ref","center","zone_low","zone_high"])],
  "REFUTED(v2)-đã-áp ở v3; v3 CHƯA qua skeptic vòng 2", center_kind="giá trị kỳ vọng (3 kịch bản 25/50/25)"))
f = R+"dd_HPG_20261031/investor_report/HPG_DD_investor_report_20261031_v3.md"
ents.append(E("HPG","2026-10-31","2026Q3",18000,20200,22500,21000,"2026-10-30","trung dung — TRONG vùng, nửa trên",f,
  [(f,"Giá 21.000 đ (đóng cửa 30/10/2026) nằm TRONG vùng giá trị hợp lý 18.000–22.500 đ, cao hơn tâm ≈20.200 đ",["price_ref","zone_low","zone_high","center"])],
  "CONFIRMED (medium; B1/B2 đã sửa; v3)", center_kind="tâm ghép (2/3 RI + 1/3 EV/EBITDA)"))
f = R+"dd_MBB_20261031/investor_report/MBB_DD_investor_report_20261031.md"
ents.append(E("MBB","2026-10-31","2026Q3",18000,22000,26000,19300,"2026-10-30","trung dung — TRONG vùng, nửa dưới",f,
  [(f,"Giá 19.300 đ (đóng cửa 30/10/2026) nằm TRONG vùng giá trị hợp lý 18.000–26.000 đ, thấp hơn tâm ≈22.000 đ",["price_ref","zone_low","zone_high","center"])],
  "CONFIRMED (medium; 1 BLOCKING MBV đã xử)", center_kind="tâm (Ke nội địa)", notes="ở Ke thị trường ~15% tâm có trọng số ~18,7k ⇒ ngưỡng −15% so 22.000 là lạc quan"))
f = R+"dd_TCH_20261031/investor_report/TCH_DD_investor_report_20261031.md"
ents.append(E("TCH","2026-10-31","2026Q3",10150,12300,15050,11850,"2026-10-30","trung dung — TRONG vùng, nửa dưới",f,
  [(f,"Giá 11.850 đ (đóng cửa 30/10/2026) nằm TRONG vùng giá trị hợp lý ≈10.150–15.050 đ, thấp hơn tâm ≈12.300–12.650 đ",["price_ref","zone_low","zone_high","center","center_range"])],
  "REFUTED-đã-áp (medium; v2)", center_kind="tâm (cận dưới của khoảng tâm)", center_range=[12300,12650],
  notes="BCTC = quý 2 năm tài chính TCH (01/07–30/09/2026, chưa soát xét); tâm nhạy tham số thặng dư (25% ⇒ ~11.960)"))
f = R+"dd_NNC_20261030/investor_report_v2/NNC_DD_investor_report_20261031_v2.md"
ents.append(E("NNC","2026-10-31","2026Q3",59000,69000,79000,47100,"2026-10-30","trung dung — DƯỚI vùng, nghiêng rẻ (không chắc chắn)",f,
  [(f,"ở giá đóng cửa 30/10/2026 (47.100 đ), NNC nằm DƯỚI vùng giá trị hợp lý ~59.000–79.000 đ/cp (điểm giữa ~69.000; ước lượng)",["price_ref","zone_low","zone_high","center"])],
  "REFUTED-đã-áp (medium; 12 đính chính); bản đính chính CHƯA qua skeptic vòng 2", center_kind="điểm giữa vùng (theo nguồn)",
  notes="vùng = 2 giả định giá đá (danh nghĩa phẳng … giữ giá trị thực), không phải dải sai số; thanh khoản ~1,4–1,5 tỷ/phiên"))
f = R+"dd_DRI_20261027/investor_report_v3/DRI_DD_investor_report_20261030_v3.md"
ents.append(E("DRI","2026-10-30","2026Q3",9100,10500,11100,14700,"2026-10-29","trung dung — TRÊN vùng cơ sở",f,
  [(f,"giá trị kịch bản cơ sở ~9,1–11,1 nghìn đ/cp (ước lượng)",["zone_low","zone_high"]),
   (f,"| Bình quân ba kịch bản theo xác suất chủ quan | ~10.500 đ |",["center"]),
   (f,"giá đóng cửa 29/10 (14.700 đ)",["price_ref"])],
  "CONFIRMED (medium; định giá r4)", center_kind="bình quân 3 kịch bản (xác suất chủ quan)",
  notes="vùng = kịch bản cơ sở; kịch bản hoãn tái canh 13,2–15,1k; cổng mua nội bộ ≤13.000 do dri_buy_gate_watch.py lo riêng"))
f = R+"dd_DGC_20261029/investor_report_v2_2/DGC_DD_investor_report_20261029_v2_2.md"
ents.append(E("DGC","2026-10-30","2026Q3",33514,None,38832,33300,"2026-10-30","ngang cận dưới dải A7–B7, chưa có đệm cho rủi ro pháp lý (nhãn nội bộ AMBIGUOUS-nghiêng-constructive, user chốt)",f,
  [(f,"mốc giữa Ke 13%: 33.514 – 38.832",["zone_low","zone_high"]),(f,"ở đóng cửa 30/10 (33.300)",["price_ref"])],
  "CONFIRMED (high; vòng 7, bản 2.2 rev2)", center_kind=None,
  null_reason="center=null: dải A7 (khai trường dừng) – B7 (mở lại) là 2 kịch bản pháp lý, nguồn ghi 'nhóm không chọn kịch bản nào làm cơ sở' ⇒ không có tâm, không tự lấy trung điểm",
  notes="zone = mốc giữa Ke 13% (Ke 12,5–13,5%: A7 33.118–33.951, B7 38.305–39.414)"))
f = R+"dd_PVP_20261029/investor_report/PVP_DD_investor_report_20261029.md"
ents.append(E("PVP","2026-10-29","2026Q3",15500,None,22400,18750,"2026-10-29","NON (không-phải-case-§2.5); dải tham khảo ngoài §2.5",f,
  [(f,"| Dải tham khảo (ngoài §2.5) | **15,5–22,4 nghìn (ước lượng)** |",["zone_low","zone_high"]),(P+"pvp-dd-20261029.md","NON / không-phải-case-§2.5 @18.750",["price_ref"])],
  "CONFIRMED (vòng 2; v2.1)",
  null_reason="center=null: dải nối 2 phương pháp (P/B trung vị lịch sử 15.545 → SOTP kỳ vọng 22.387), không có tâm",
  notes="giá 18.750 là giá sàn trong phiên 29/10 (13:58), không phải đóng cửa"))
f = P+"pvt-dd-20261029.md"
ents.append(E("PVT","2026-10-29","2026Q3",19400,20000,21200,21300,"2026-10-29","NON — ≈ giá hợp lý, không biên an toàn",f,
  [(f,"FV ≈ 19,4–21,2k (≈ giá hợp lý, không biên an toàn)",["zone_low","zone_high"]),(f,"**Verdict: NON @21.300",["price_ref"]),
   (R+"dd_PVT_20261029/REPORT.md","−15% của ~20k ≈ **~17.000 (ước lượng)**",["center"])],
  "CONFIRMED phân loại NON; định giá đã đính chính (REPORT §14)", center_kind="~20k (nguồn dùng làm mốc −15%)",
  notes="giá 21.300 là giá sàn trong phiên 29/10, không phải đóng cửa"))
f = P+"scl-dd-20261029.md"
ents.append(E("SCL","2026-10-29","2026Q3",None,25500,None,31100,"2026-10-29","NON (discretionary) — FV có trọng số ~25.500 sau phát hành",f,
  [(f,"**NON (discretionary) @31.100 cum / TERP 28.612; FV có trọng số ~25.500 sau phát hành (ước lượng)**",["price_ref","center"])],
  "REFUTED một phần — NON đứng (REPORT §13)", center_kind="giá trị có trọng số (cơ sở EX-QUYỀN, 44,84tr CP)",
  null_reason="zone=null: bảng vùng trong REPORT là vùng NHÃN (QUALIFY/AMBIGUOUS/NON), không phải vùng giá trị hợp lý",
  notes="tâm theo giá EX-QUYỀN (quyền 100:15,4453 @12.500, ĐKCC 10/11); giá cum trước ex-date không so trực tiếp được; đã thoái khỏi LAG 30/10"))
f = R+"dd_DDV_reweight_20261028/REPORT.md"
ents.append(E("DDV","2026-10-28","2026Q3",12300,14500,17300,16700,"2026-10-27","NON, nghiêng xấu đi (tái trọng số theo Bobby)",f,
  [(f,"**~14.500** (dải 12.300–17.300 theo độ dốc biên, §3)",["center","zone_low","zone_high"]),(f,"**16.700 (27/10)**",["price_ref"])],
  "CHƯA qua skeptic (bản tái trọng số 28/10; DD gốc 26/10 không có file skeptic)", center_kind="giá trị kỳ vọng (net cash 7.583)",
  notes="kịch bản net cash stress ~12.900 (10.700–15.700); đợt mua nội bộ ≤~12.000/≤~10.500"))
f = R+"dd_NT2_20261026/REPORT.md"
ents.append(E("NT2","2026-10-26","2026Q3",None,25400,None,None,None,"NON (sleeve fear-buy) — quanh giá trị hợp lý trên LN chuẩn hoá",f,
  [(f,"kỳ vọng có trọng số khoảng **25.400 đ ≈ +5%**",["center"])],
  "CHƯA qua skeptic (không có file skeptic)", center_kind="giá trị kỳ vọng có trọng số",
  null_reason="zone=null: chỉ có 3 kịch bản bear/base/bull (17.800/25.600/32.500), không có vùng hợp lý; price_ref=null: nguồn không ghi giá nguyên văn (chỉ '≈ +5%')"))
f = R+"dd_SAS_20261026/REPORT.md"
ents.append(E("SAS","2026-10-26","2026Q3",None,32600,None,37000,"2026-10-23","NON — kỳ vọng thấp hơn giá 12%",f,
  [(f,"kỳ vọng có trọng số ≈ **32.600 đ** (−12% so giá)",["center"]),(f,"(tại giá 37.000 đ, phiên 23/10/2026)",["price_ref"])],
  "CHƯA qua skeptic (không có file skeptic)", center_kind="giá trị kỳ vọng có trọng số",
  null_reason="zone=null: nguồn chỉ có kỳ vọng có trọng số, không có vùng", notes="free float ≈4,4% — ràng buộc thực thi"))
f = R+"dd_SZL_20261026/REPORT.md"
ents.append(E("SZL","2026-10-26","2026Q3",None,27200,None,28200,None,"NON — giá hợp lý, không rẻ",f,
  [(f,"trọng số 25/50/25 ≈ **27.200 đ (−3,5%)**",["center"]),(f,"hiện 28.200 = −6% từ đỉnh năm",["price_ref"])],
  "CHƯA qua skeptic (không có file skeptic)", center_kind="SOTP có trọng số",
  null_reason="zone=null: chỉ có 3 kịch bản 18.900/27.200/35.600; price_date=null: nguồn ghi 'hiện', không ghi ngày",
  notes="thanh khoản 0,37–0,50 tỷ/phiên"))
f = P+"tv2-dd-20261028.md"
ents.append(E("TV2","2026-10-28","2026Q3",None,None,None,26050,"2026-10-27","NON (khung nội bộ discretionary)",f,
  [(f,"**Verdict: NON @26.050 (27/10)",["price_ref"])],
  "CONFIRMED (high)",
  null_reason="DD 28/10 chỉ có ngưỡng chạy lại DD (≤~19.500), không có vùng/tâm; BỊ THAY bởi DD 01/11",
  recorded_at="2026-11-01T23:00:00+07:00"))
doc = {"schema": "dd_price_zones/v1",
  "doc": "Sổ MỨC GIÁ DD (user yêu cầu 2026-11-01 22:39 ICT). Append-only theo (ticker, dd_date): DD mới hơn THÊM entry mới, không sửa entry cũ; bản dd_date mới nhất của mã thắng. Mỗi số khớp nguyên văn một trích dẫn trong evidence (bin/dd_price_zones_selfcheck.py). Vùng/tâm là bản SAU phản biện. Ghi chú để user cân nhắc — KHÔNG phải tín hiệu mua, KHÔNG nạp vào plan tự động.",
  "center_rule": "center = số nguồn gọi là tâm/kỳ vọng/điểm giữa; khi nguồn cho KHOẢNG tâm thì center = cận DƯỚI (bảo thủ: ngưỡng −15% kích hoạt muộn hơn), khoảng đầy đủ ở center_range. null = nguồn không có — không tự suy.",
  "units": "đồng/cổ phiếu", "entries": ents}
print(json.dumps(doc, ensure_ascii=False, indent=1))
