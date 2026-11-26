**Kết luận: REFUTED (độ tin cậy trung bình).** Tôi tái lập được số học của rev5, nhưng tâm 9.387 đang đếm khoản hồi tố hai lần. Sửa lỗi này thì tâm xuống khoảng **8.549 (−8,9%)**, vượt ngưỡng trọng yếu 5%.

**Lỗi chính: hồi tố bị đếm hai lần (chiều ĐẮT)**
- Mức ROE di sản 8% được dựng bằng cách cộng lại khoản hồi tố khoảng 2.455 tỷ sau thuế vào lợi nhuận các năm 2019–25 (`REPORT.md:179`, điều chỉnh "(ii)"). Phản biện r1 cũng dựng lại theo đúng cách đó (`skeptic/r1_raw.md:43`: "cộng hồi tố ~2.455 sau thuế chia 7 năm ⇒ ~8,0%").
- Rev4 rồi rev5 giữ nguyên ROE 8% vĩnh viễn, đồng thời ghi thêm chính khoản 2.454,7 theo sổ ở hệ số 1,0×. Lý do nêu ở R2-1 ("đã cộng vào tử số các năm trước nên không tính lại vào lợi nhuận tương lai") sai: đã cộng vào ROE thì nghĩa là ngoại suy nó vào tương lai.
- Dòng hồi tố khoảng 350,7 tỷ/năm tương đương +1,21 điểm ROE. Vốn hoá ở 13,5% ra khoảng 2.598 tỷ, tức khoảng 847 đ/cp. Bỏ phần này: ROE còn khoảng 6,8% và tâm 8.635 trước chiết khấu / **8.549 sau chiết khấu**. Thử ROE 7% thì ra 8.695 (−7,4%).

**Phần đã kiểm và khớp**
- Tâm: 28.939,8×0,08/0,135 + 9.000 + 2.740 + 2.454,7 − 2.255 = 29.089 tỷ, chia 3.067,85 triệu cp = 9.482 → 9.387 sau chiết khấu 1%.
- Tổng các khối vốn = 43.134,5, đúng bằng VCSH mẹ.
- Biên upside NT3&4 ở F3: 2.111 và 9.519 tỷ đều đúng.

**Lỗi nhỏ:** F1 dùng vay ngắn hạn 19.438,3, là số mà A6 đã sửa thành 19.418,3.

**Chiều RẺ (đã kiểm 9 mục, nhiều hơn 8 mục chiều đắt):**
- r = 13,5% nằm trên đầu dải Ke 12,3–13,4%; đưa về 13,4% chỉ được +0,4%.
- Báo cáo tự đo tỷ trọng vốn đang khấu hao s ≈ 0,69, nhưng bảng độ nhạy §C chỉ tới 0,64, nên upside thật có thể trên +16%. Chưa vào base vì chưa có số theo từng nhà máy.
- Cơ chế chênh lệch tỷ giá của VA1 có thể tái diễn. Phần nhận diện được (khoảng 490 tỷ) bù được chưa tới 1/5 phần bị đếm hai lần.
- Opex QCVN tính vĩnh viễn trong khi đời còn lại của nhà máy ngắn; lệch nhỏ (+0,6%).
- ROE cốt lõi 2026 khoảng 12–14%, nhưng chưa tách được phần cấu trúc khỏi phần chu kỳ.

Không mục nào đủ cơ sở độc lập để kéo tâm lên.

**Mục còn thiếu (chưa đóng được):** hạn PPA và nguồn khí CM1&2/NT1, giá trị sổ theo nhà máy, giá trị giao dịch bên liên quan, nghĩa vụ quyết toán CPH còn lại, loại tiền và loại lãi suất của khoản vay ngắn hạn.

Tôi không tra giá thị trường. Giá DNSE 13.350 có trong báo cáo đã được bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "POW — DD REPORT_rev5 (tâm 9.387, vùng 6.966–11.808)",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — §G: Deloitte FY2025 chấp nhận toàn phần + nhấn mạnh quyết toán CPH chưa duyệt; không thấy khởi tố/xử phạt trong 83 CBTT (chưa tra UBCKNN, báo cáo tự nêu); CPH có độ nhạy −2,5%",
    "optimistic_comp_sotp_bias": "fail — không dùng comp, nhưng khung SOTP đếm hồi tố 2 lần: ROE di sản 8% dựng bằng cách cộng hồi tố ~2.455 sau thuế chia 7 năm vào tử số 2019–25 (REPORT.md:179 điều chỉnh (ii); skeptic/r1_raw.md:43), rồi rev4/rev5 ghi thêm chính 2.454,7 ở 1,0x. Dòng ~350,7 tỷ/năm = +1,21pp ROE ≈ 2.598 tỷ PV ≈ 847 đ/cp; bỏ ra thì tâm ≈ 8.549 (−8,9%). Thêm nữa, 8% là cận trên của dải 7–8% do chính báo cáo ước lượng",
    "data_provenance": "pass (có nit) — số cp 3.067.845.688 (TM23/OShares), VCSH mẹ 43.134,5, PV QCVN19, cơ cấu nợ USD 73,8% đều có nguồn; nit: F1 dùng vay NH 19.438,3, số A6 đã sửa thành 19.418,3; ROE 8% gắn nhãn ước lượng",
    "liquidity_capacity_realism": "na — sizing ở giá hiện tại 'không mở'; ADV 63,3 tỷ (BQ 18/11) đủ cho trần 2–4% NAV; không đánh giá sâu theo mode",
    "confirmation_bias_flipflop": "fail (nhẹ) — so với rev3, R2-1 tăng tâm +3,6% sau khi đã đọc giá, trong khi giá nằm trên tâm; sửa phương pháp do skeptic yêu cầu là chính đáng nhưng làm chưa đến nơi: chuyển hồi tố sang 1,0x mà không gỡ phần hồi tố đã cộng vào ROE 8%. Không mở dd_price_zones.json theo ràng buộc mù; so sánh dựa trên lịch sử revision ghi trong chính báo cáo",
    "exit_discipline_gap": "na — DD_GENERAL; dù vậy báo cáo có điều kiện đổi nhận định hai chiều (§F) và trần sizing 2–3% NAV",
    "missing_items": "fail — (1) [định lượng được, trọng yếu] lỗi đếm hai lần hồi tố trong ROE di sản ≈ −8,9% tâm; (2) [không định lượng được, trọng yếu] hạn PPA/nguồn khí CM1&2 và NT1, giá trị sổ theo nhà máy (đời di sản ~7 năm theo báo cáo, có thể kéo tâm theo cả hai chiều); (3) giá trị giao dịch bên liên quan không kiểm chứng (OCR hỏng); (4) quỹ KTPL chỉ ở độ nhạy −1,8…−2,9%, chưa vào base dù là khoản trích định kỳ; (5) loại tiền/lãi suất vay ngắn hạn ~19,4 nghìn tỷ chưa biết; (6) nghĩa vụ CPH còn lại chưa biết. Có mặt: capex QCVN19 VA1 trong base, kiểm toán FY2025 đủ, one-off 9T/26 đã tách, Quỳnh Lập/VA III đã bàn ở §B3",
    "symmetry": {"too_high_checked": 8, "too_low_checked": 9, "too_low_items": ["r 13,5% trên đầu dải Ke 12,3–13,4% (+0,4% ở 13,4%, +5,0% ở 12,3%) — lệch nhỏ, không đủ cơ sở đổi", "§C: báo cáo tự đo s≈0,69 nhưng lưới chỉ tới 0,64 ⇒ upside đời hữu hạn có thể >+16%; không vào base vì thiếu số theo nhà máy", "chênh lệch tỷ giá VA1 còn ~490 tỷ + cơ chế NT2/Đakđrinh có thể tái diễn ⇒ một phần dòng hồi tố trong ROE là thật; ~490 chỉ bù <1/5 phần bị đếm hai lần", "ROE cốt lõi 2026 ~12–14% so với base 8% — chưa tách được cấu trúc khỏi chu kỳ", "NT3&4 NPV>0 nếu Qc≥63% (F3: +688…+3.103 đ/cp) — 4 điều kiện cần đều chưa có số", "opex QCVN19 vĩnh viễn trong khi đời còn lại ngắn — biến thể dừng 2045 chỉ +0,6%", "trọng số bù giá P0/P50/P100 mượn từ QTP; Luật Điện lực 61/2024 Đ52.4 mở lối — P100 +7,8%, chưa có tiền lệ", "chiết khấu thanh khoản 1% trên ADV 63 tỷ — có thể ~0%, tác động +1%", "trọng số kịch bản 25/50/25 với kịch bản xấu 4,5% ≈ đáy El Niño 2023–24 — đối xứng, không thấy thiên lệch"]}
  },
  "independent_verification": "Tính lại tâm: (28.939,8×0,08/0,135 + 9.000 + 2.740 + 2.454,7 − 2.255)/3.067,85 = 9.482 → 9.387 sau CK 1% — khớp; tổng các khối vốn 28.939,8+9.000+2.740+2.454,7 = 43.134,5 = VCSH mẹ — khớp; F3: (1.500−1.215)/0,135 = 2.111 và (2.500−1.215)/0,135 = 9.519 — khớp. Tính lại khi gỡ hồi tố khỏi ROE (2.454,7/7 = 350,7 tỷ/năm = 1,21pp trên 28.939,8): tâm 8.635 trước CK / 8.549 sau CK (−8,9%); ở ROE 7%: 8.695 sau CK (−7,4%).",
  "killer_objection": "ROE di sản 8% đã chứa sẵn khoản hồi tố ~2.455 tỷ (dựng bằng cách cộng lại phần hồi tố thuộc các năm trước vào tử số 2019–25), nên ghi thêm 2.454,7 ở 1,0x theo R2-1 là đếm hai lần. Sửa thì tâm ≈ 8.549 (−8,9%), vượt ngưỡng trọng yếu 5%.",
  "recommended_followups": [
    "Dựng lại ROE di sản chỉ với điều chỉnh XDCB (i), bỏ điều chỉnh hồi tố (ii), ghi bảng tính theo năm; dùng mức đó cho base trong khi giữ hồi tố 2.454,7 ở 1,0x",
    "Nếu cho rằng hồi tố/chênh lệch tỷ giá có tính tái diễn: định lượng dòng tái diễn có nguồn (CLTG VA1 ~490 còn lại, NT2/Đakđrinh) và đưa vào ROE thay cho mức chia đều 7 năm",
    "Sửa vay ngắn hạn ở F1 từ 19.438,3 về 19.418,3 cho khớp A6",
    "Đóng hạng mục ngành bắt buộc: hạn PPA/nguồn khí CM1&2, NT1 và giá trị sổ theo nhà máy (BCTN thuyết minh TSCĐ theo đơn vị)",
    "Mở rộng lưới §C tới s≈0,69 như báo cáo đã đo"
  ],
  "summary": "Rev5 tái lập được số học (9.482/9.387, tổng vốn khớp VCSH mẹ 43.134,5, biên F3 đúng) và Phụ lục F không đổi tâm. Nhưng thay đổi R2-1 của rev4 tạo lỗi đếm hai lần: ROE di sản 8% được dựng bằng cách cộng hồi tố ~2.455 tỷ sau thuế vào lợi nhuận lịch sử (REPORT.md:179; skeptic r1 xác nhận cùng phép dựng), rồi chính khoản đó được ghi thêm ở 1,0x. Gỡ phần hồi tố khỏi ROE (~1,21pp) thì tâm ≈ 8.549 (−8,9%), vượt ngưỡng trọng yếu 5% ⇒ REFUTED. Chiều ngược lại có những upside thật nhưng chưa đủ cơ sở độc lập để vào base: s đo được 0,69 vượt lưới §C, chênh lệch tỷ giá VA1 có thể tái diễn một phần, r cao hơn đầu dải Ke 0,1pp. Hạng mục PPA/nguồn khí và giá trị sổ theo nhà máy vẫn mở như ba vòng trước. Không tra giá; giá DNSE trong báo cáo bị bỏ qua khi đánh giá mô hình."
}
<<<END_VERDICT>>>