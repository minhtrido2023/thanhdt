**Kết luận: INCONCLUSIVE, độ tin cậy trung bình.** Phần cơ học của r3c đúng và tái lập được, nhưng tâm 7.701 không vững theo cả hai chiều. Có một mục vắng mặt có thể đẩy tâm lên tới khoảng +30%, và một lần dời trọng số làm tâm tăng +8,4% mà không có dữ kiện mới thực sự đứng sau.

Báo cáo có ghi giá thị trường (10.200–10.300). Tôi bỏ qua các con số đó khi chấm mô hình.

**Những gì tôi tự kiểm lại**
- Chạy lại `qtp_model_r3c.py`: output trùng từng byte với `qtp_model_r3c_out.txt`. P0/cơ sở −10.478, tâm 8.557 trước chiết khấu / 7.701 sau.
- Tách chi phí biến đổi từ FS §3.1.7: amoniac 12.045.120 kg × 26.350 đ = 317,4 tỷ; điện tự dùng 18.470.400 kWh × 2.036 đ = 37,6 tỷ; phần dư 115,3 tỷ. Khớp với báo cáo.
- O&M cố định 15,69 × 6.501,57 GWh = 102,0 tỷ; biến đổi 72,33 × 6.501,57 GWh = 470,3 tỷ. Khớp.
- FIRR dự án tôi dựng lại độc lập ra khoảng 10,1%, FS ghi 11%. Nghĩa là giả định thu phần vốn qua giá trong 18 năm là đúng thiết kế của FS. Nếu chỉ thu 10 năm thì FIRR còn 5,6%, nhưng tâm chỉ giảm −3,6%.

**Chiều RẺ — tâm có thể đang quá thấp**
- **Chi phí biến đổi có thể được chuyển qua giá biến đổi của PPA hiện hữu.** Khoản 470 tỷ/năm (chủ yếu là amoniac) là phần lớn nhất của chi phí vận hành 572 tỷ/năm. Chi phí vận hành này chiếm −5.733 trong −10.478 của P0. Mảng pháp lý của báo cáo chỉ xét cơ chế bù phần vốn (TT12 Đ13.4, Luật Điện lực Đ52.4), chưa hề hỏi amoniac có tính được vào giá biến đổi qua mục vật liệu phụ / chi phí biến đổi khác hay không.
  - Nếu chuyển được ở mọi kịch bản, tâm lên **10.023 sau chiết khấu (+30,1%)**. Tôi tính bằng mô hình của chính báo cáo, đặt chi phí biến đổi = 0.
  - Chiều ngược lại: FS tự gộp 72,33 đ/kWh vào phần xin tăng giá. Điều đó gợi ý công ty không coi khoản này là tự động được chuyển.
- **Trọng số là biến lớn nhất mà không có nguồn đo.** P0 chạy từ 0,5 về 0 thì tâm sau chiết khấu đi từ 7.053 lên 10.293. Báo cáo tự ghi N = 0 tiền lệ.

**Chiều ĐẮT — tâm có thể đang quá cao**
- **Dời trọng số r3 → r3b (+648, tức +8,4%) chủ yếu là đọc lại dữ kiện cũ.**
  - Kiến nghị của EVN ngày 29/12/2025 từng là lý do giữ P0 = 0,50 ở r3 (`REPORT_r3.md:98`). Sang r3b, chính dữ kiện đó lại thành lý do hạ P0.
  - Thông tin pháp lý mới của r3b nghiêng về phía bất lợi: không có Đ14.6, TT07 đã bị bãi bỏ và TT12 không có điều tương đương. Chỉ có Đ52.4 là mới và thuận lợi, mà điều này còn đang tranh cãi.
  - §4 của báo cáo còn tự mâu thuẫn: mục "(0)" nằm dưới tiêu đề "giảm P0" nhưng nội dung lại nói nó làm tăng P0.
- **Những mục vắng mặt, chưa lượng hoá được:**
  - Thay lớp xúc tác SCR định kỳ, trong khi FS ghi "tuổi thọ dự án 10 năm" mà mô hình cho chạy tới 2047.
  - Rủi ro tỷ giá trên phần EPC 89,76 triệu USD (≈ −3% nếu VND mất giá 10%).
  - Mô hình giữ cố định 6.501,57 GWh. Nếu nhà máy được huy động ít đi thì khoản bù tính theo đ/kWh ở P50/P100 cũng giảm theo.
  - Quỹ khen thưởng – phúc lợi trích từ lợi nhuận sau thuế: không thấy trong r2 lẫn r3c, ước tác động khoảng −4…5%.
  - Phụ lục 2 của GPMT 517 chưa đọc được, nên vẫn chưa biết có buộc chạy SCR trước 2032 hay không. Báo cáo đã tự gắn cờ mục này.

<<<VERDICT_JSON>>>
{
  "case_topic": "QTP — DD r3c (dự án cải tạo hệ thống khí thải 3.485 tỷ, tâm 7.701 sau CK)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — không có scandal; mục pháp lý/giấy phép: GPMT 517/GPMT-BTNMT 03/12/2024 Phụ lục 2 (SCR có buộc chạy trước 2032 không) chưa đọc được, báo cáo tự gắn cờ và để ngoài tâm, có biến thể +9,8%",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; DCF dựa trên FS gốc; dựng lại FIRR độc lập ≈10,1% vs FS 11% ⇒ thu FC 18 năm (tới 2047) đúng thiết kế FS; nếu chỉ 10 năm thì −3,6%",
    "data_provenance": "pass, có lưu ý — TMĐT 3.484,88 / O&M 102,01 / biến đổi 470,29 / amoniac / điện tự dùng khớp FS §3.1.7 từng dòng; lãi vay 9%, kỳ hạn 10 năm, tiến độ giải ngân, COD và trọng số P đều là (ước lượng) và được gắn nhãn; phần dư 115,3 tỷ chưa giải thích, đã gắn nhãn",
    "liquidity_capacity_realism": "na — báo cáo không có claim về sizing/khớp lệnh",
    "confirmation_bias_flipflop": "fail (vừa) — r3→r3b hạ P0 0,50→0,40 (+648 sau CK, +8,4%), nhưng EVN 29/12/2025 đã là lý do giữ P0 cao ở r3 (REPORT_r3.md:98); thông tin pháp lý mới của r3b nghiêng bất lợi cho việc bù (không có Đ14.6, TT07 bị bãi bỏ, TT12 không có điều tương đương); chỉ Đ52.4 Luật 61/2024 là mới và còn tranh cãi. Không so dd_price_zones theo ràng buộc mù; so giữa các bản r2 (14.599 RẺ) → r3 (7.053) → r3b/r3c (7.701 ĐẮT): cú lật r2→r3 có dữ kiện mới thật (FS dự án)",
    "exit_discipline_gap": "na — không có claim sizing; dù vậy báo cáo có điều kiện huỷ có ngày (chưa ký phụ lục giá PPA trước COD ~12/2029; EVN/BCT từ chối bằng văn bản)",
    "missing_items": "fail — (1) chuyển chi phí biến đổi (amoniac 317 tỷ/năm) qua giá biến đổi PPA hiện hữu (vật liệu phụ / chi phí biến đổi khác) không được phân tích: nếu được, tâm 10.023 sau CK (+30,1%, đo bằng mô hình r3c với vc_abs=0), xác suất không lượng hoá được ⇒ INCONCLUSIVE; (2) thay xúc tác SCR định kỳ / tái đầu tư sau 'tuổi thọ dự án 10 năm' của FS: vắng mặt, chưa lượng hoá; (3) tỷ giá trên EPC 89,76 triệu USD: vắng mặt, ≈ −3% nếu VND mất giá 10%; (4) bù theo đ/kWh nhạy với sản lượng huy động (cố định 6.501,57 GWh): vắng mặt; (5) quỹ khen thưởng–phúc lợi trích từ LNST: không thấy trong r2/r3c, ước −4…5%. Đạt: capex bắt buộc có trong mô hình; số cổ phiếu 450 triệu (khớp tạm ứng cổ tức 1.000đ = 449,3 tỷ, LCTT 9T26); thuê đất tới 15/3/2047 = chân trời mô hình; kiểm toán FY2025 chấp nhận toàn phần; khoản một lần FX Q4/25 đã loại khỏi năm gốc; phải thu EVN đã nêu ở r2"
  },
  "independent_verification": "Chạy lại qtp_model_r3c.py: output trùng từng byte với qtp_model_r3c_out.txt (tâm 8.557/7.701, P0 −10.478). Tách chi phí biến đổi từ FS §3.1.7 khớp (317,4 + 37,6 + 115,3 = 470,29); 15,69 và 72,33 đ/kWh × 6.501,57 GWh = 102,0 và 470,3 tỷ, khớp. FIRR dựng lại độc lập ≈10,1% vs FS 11%, hợp lý. Biến thể tự tính: thu FC 10 năm −3,6%; chi phí biến đổi chuyển qua giá +30,1%.",
  "killer_objection": "P0 giả định toàn bộ 470 tỷ/năm chi phí biến đổi (chủ yếu amoniac) không bao giờ được thu hồi, trong khi chưa kiểm xem khoản này có đi qua giá biến đổi của PPA hiện hữu như vật liệu phụ hay không — kênh này khác và có thể dễ hơn kênh bù phần vốn đầu tư. Nếu đi qua được, tâm lên khoảng 10.000 (+30%), vượt trên toàn bộ vùng biến thể đơn lẻ mà báo cáo nêu (6.300–8.900).",
  "recommended_followups": [
    "legal-vn: TT12/2025 và PPA QTP–EPTC — giá biến đổi có gồm vật liệu phụ / chi phí biến đổi khác không, amoniac cho SCR có đủ điều kiện không, có cần ký phụ lục PPA không",
    "Hỏi công ty / đọc PPA: thời hạn PPA và cơ chế giá cố định sau khi hết khấu hao (r2 đã nêu là biến lớn nhất)",
    "FS/hồ sơ EPC: chu kỳ thay xúc tác SCR và chi phí đã nằm trong O&M 102 tỷ hay chưa; ý nghĩa của 'tuổi thọ dự án 10 năm'",
    "Thêm biến thể tỷ giá cho phần EPC USD và biến thể sản lượng huy động (ví dụ 5.000 h) áp lên doanh thu bù đ/kWh",
    "BCTC FY2025: tỷ lệ trích quỹ khen thưởng–phúc lợi ⇒ trừ khỏi FCFE trong r2",
    "Viết lại §4 trọng số: tách rõ dữ kiện MỚI ở r3b với dữ kiện đã có từ r3; sửa chỗ mâu thuẫn ở mục (0)",
    "Lấy bản GPMT 517 Phụ lục 2 từ công ty / BNNMT"
  ],
  "summary": "Phần cơ học của r3c đúng: mô hình tái lập trùng từng byte, các con số FS khớp từng dòng, FIRR dựng lại ≈ FS. Nhưng tâm 7.701 không vững theo cả hai chiều. Chiều rẻ: kịch bản P0 cho rằng toàn bộ chi phí biến đổi 470 tỷ/năm không bao giờ được thu hồi, trong khi chưa kiểm kênh giá biến đổi của PPA hiện hữu; nếu kênh này dùng được thì tâm lên khoảng 10.000 (+30%). Chiều đắt: việc hạ P0 0,5→0,4 (+8,4%) dựa phần lớn vào việc đọc lại dữ kiện đã có ở r3, trong khi thông tin pháp lý mới lại nghiêng bất lợi cho việc bù; thêm vào đó là các mục vắng mặt (thay xúc tác SCR, tỷ giá EPC USD, sản lượng huy động, quỹ phúc lợi), mỗi mục kéo tâm xuống vài phần trăm. Tâm chủ yếu là hàm của trọng số P, mà trọng số này là ước lượng với N = 0. Chưa thể xác nhận cho tới khi có câu trả lời pháp lý về việc chuyển chi phí biến đổi qua giá."
}
<<<END_VERDICT>>>