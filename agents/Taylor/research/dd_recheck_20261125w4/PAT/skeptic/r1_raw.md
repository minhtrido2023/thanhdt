**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Tôi tái lập được mô hình: tâm trước chiết khấu (CK) ra đúng 61.697, tiền ròng 357,35 tỷ. Nhưng có ba hạng mục trọng yếu chiều xuống vẫn chưa định lượng được, và một điểm chưa nhất quán nội tại có định lượng ở mức −8,5%.

**Đã tự kiểm (`/tmp/patsk/chk.py`, gọi trực tiếp `model_r5`):**
- Tiền ròng: 1,246 + 558,069 − 67,218 − 76,690 = 415,41; trừ LOCKED70 45,11 và quỹ KTPL 9 tháng 12,94 còn **357,35**. Khớp `facts_extracted.md:24` và giả định r5.
- Tâm base trước CK **61.697** tái lập đúng từng chữ số. V_ngắn tính lại được 97.709, báo cáo ghi 97.800 (chỉ lệch làm tròn). GPMB 13,158/1,63 = 8,07 năm, tức hết phân bổ khoảng 2034, khớp báo cáo.
- Chưa đối chiếu được với BCTC gốc vì không có PDF trong thư mục local, chỉ có bản trích của fleet.

**Chiều ĐẮT (tâm có thể quá cao):**
1. **Tăng trưởng không tái đầu tư trong pha tường minh.** Luật D4 (RONIC = Ke) chỉ áp vào giá trị cuối kỳ. Trong khi đó chuỗi 2028–2045 vẫn tăng 2%/năm mà capex = khấu hao, ΔVLĐ = 0, tức RONIC ngầm là vô hạn trong 18 năm. Tôi chạy lại với g = 0 (RONIC = Ke cho cả chuỗi) thì được **56.470, −8,5%**. Phần đệm capex ~40 tỷ/năm có bù được một phần, nhưng báo cáo đã dùng chính phần đệm đó để thay capex môi trường (D3). Cùng một khoản đệm không thể vừa nuôi tăng trưởng vừa trả capex tuân thủ.
2. **Hạn thuê đất KCN.** Nếu hết năm 2034 mà không gia hạn thì tâm giảm 28,7%. Mốc 2034 chỉ suy ra từ lịch phân bổ GPMB, không phải từ hợp đồng thuê, và xác suất không gia hạn không có dữ liệu.
3. **Trách nhiệm hình sự của pháp nhân theo Điều 235.** Chủ tịch PAT đã bị khởi tố tội gây ô nhiễm môi trường. Theo hiểu biết của tôi (chưa kiểm), Bộ luật Hình sự 2015 Điều 76 cho phép truy cứu pháp nhân thương mại về tội này, với hình phạt có thể gồm đình chỉ hoạt động. `dd_PAT_20261114/REPORT.md:271` đã ghi việc lò P4 bị đình chỉ là điều kiện từ bỏ, nhưng rev6 chỉ để ở mức WARNING và không định lượng. Đình chỉ 6 tháng ước khoảng −10%.
4. **Capex tuân thủ môi trường.** Không có nghị quyết ĐHĐCĐ hay kế hoạch đầu tư 2026 (mục F1 không tìm được), nên không có số.

**Chiều RẺ (tâm có thể quá thấp):**
- **Đưa base từ ô O2 về ô D (−5,82%) là điều chỉnh xuống thiếu bằng chứng độc lập.** Tài liệu A1:133,143 chỉ cho thấy tín hiệu H1/26 bị lẫn nguồn quặng A, nghĩa là bằng chứng cho O2 yếu đi. Nó không chứng minh mức D. Q2/26 với biên LNST 21,2% còn nghiêng về phía O2. Thế mà base đặt p(O2) = 0, trong khi E17 của chính báo cáo dùng p = 0,5 (ra 64.302, +4,2%).
- r = 13,5% nằm trên đầu dải Ke 12,3–13,4%. Ở r = 12,3% tâm tăng 7,66%.
- Tồn kho dư 44,44 tỷ bị đặt bằng 0 (giải phóng thì +2,27%). Khoản 70 tỷ cầm cố tính theo mệnh giá thì +2,92%.
- Mốc 2034 cho đất thuê cũng có thể quá sớm, vì kỳ phân bổ GPMB không bằng thời hạn hợp đồng thuê.

**Các điểm đạt:** cách đọc lại cầm cố đúng (130 tỷ ACB và 199 tỷ BIDV bảo đảm cho vay của chính PAT, không trừ). Đã tính quỹ KTPL, số cổ phiếu 25 triệu (thuyết minh TM17), BCTC kiểm toán FY2025 có ý kiến ngoại trừ. Bảng độ nhạy r và bắc cầu §1 khớp `model_r6_out.json`. Tôi bỏ qua mọi giá thị trường và nhãn giá có trong báo cáo khi đánh giá.

<<<VERDICT_JSON>>>
{
  "case_topic": "PAT — DD rev6 recheck 25/11/2026 (tâm 55.527 sau CK / 61.697 trước CK)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không tuyên bố fear-buy/§2.5",
    "scandal_migration_risk": "fail — WARNING §6 nêu Chủ tịch bị khởi tố Điều 235 (22/07/2026) nhưng không xét trách nhiệm hình sự pháp nhân thương mại (BLHS 2015 Đ.76, hình phạt có thể gồm đình chỉ hoạt động — cần legal-vn xác minh); dd_PAT_20261114/REPORT.md:271 tự liệt kê 'lò P4 bị đình chỉ' là trigger nhưng rev6 không định lượng (6 tháng đình chỉ ≈ −10% ước lượng)",
    "optimistic_comp_sotp_bias": "pass — không dùng comp/SOTP; DCF cây 9.072 lá, Σp=1; bảng r §2 và bắc cầu §1 khớp model_r6_out.json; nhưng xem missing_items về tăng trưởng tường minh không tái đầu tư (g=0 ⇒ 56.470, −8,5%)",
    "data_provenance": "pass (có điều kiện) — tiền ròng 415,41/357,35, 25tr cp, KTPL 76,69, capex 0,115, KH 44,82 truy được về facts_extracted.md:24,27,34,57; BCTC gốc PDF không có local nên chỉ đối chiếu với bản trích; ngày hết thuê 2034 là SUY LUẬN từ phân bổ GPMB, không phải điều khoản HĐ",
    "liquidity_capacity_realism": "na — không đề xuất vị thế; V8 ghi rõ ≤0,5% NAV do thanh khoản",
    "confirmation_bias_flipflop": "fail (nhẹ) — rev3 59.823 → rev6 55.527 (−7,18%): D4 là luật mới (hợp lệ); ô O2→D (−5,82%) dựa trên A1:133,143 vốn đã có từ trước, là diễn giải lại cùng thông tin; A1 chỉ vô hiệu hoá bằng chứng cho O2, không lập bằng chứng độc lập cho D, trong khi Q2/26 LNST% 21,2% nghiêng về O2 — base p(O2)=0 không nhất quán với p=0,5 ở E17 của chính báo cáo",
    "exit_discipline_gap": "na — không có khuyến nghị vị thế",
    "missing_items": "fail — (1) hạn HĐ thuê đất KCN + điều khoản gia hạn: chỉ suy từ GPMB, kịch bản 2034 −28,7%, xác suất không có ⇒ trọng yếu, không định lượng được; (2) trách nhiệm pháp nhân Điều 235 / đình chỉ P4: vắng, ~−10%/6 tháng (ước lượng); (3) capex tuân thủ môi trường theo nghị quyết ĐHĐCĐ/HĐQT 12 tháng: không tìm được (F1); (4) tăng trưởng 2%/năm 2028–2045 không tái đầu tư/ΔVLĐ: định lượng được −8,5% (g=0 ⇒ 56.470), bù một phần bởi đệm capex ~40 tỷ/năm nhưng đệm đó đã được dùng cho D3. Đạt: số cp (TM17, 30/09/26), quỹ KTPL, kiểm toán FY2025 (UHY ngoại trừ tồn kho), bên liên quan/bảo đảm chéo, giá chuyển giao DLC (nút T), CIT/thuế XK trong mô hình",
    "symmetry": "{too_high_checked: 7, too_low_checked: 8, too_low_items: ['r 13,5% vs dải Ke 12,3–13,4% (+7,66% @12,3%)', 'ô D vs O2: hạ xuống không có bằng chứng độc lập, Q2/26 21,2% (+6,2%; E17 p=0,5 +4,2%)', 'tồn kho dư 44,44 tỷ đặt 0 (+2,27%)', '70 tỷ LOCKED theo mệnh giá (+2,92%)', 'capex thực ≤8 tỷ/năm ≪ KH 45 — đệm FCF nếu duy trì (ước +~6% nếu 20 tỷ/năm × 8 năm)', 'CK thanh khoản 10% là quy ước, không có cơ sở đo riêng cho PAT', 'mốc 2034 có thể quá sớm: kỳ phân bổ GPMB ≠ hạn HĐ thuê (kịch bản 2042 chỉ −11,5%)', 'cầm cố ACB 130/BIDV 199 không trừ — kiểm lại đúng, phản bác −7,8% của skeptic r1 có cơ sở văn bản']}"
  },
  "independent_verification": "Gọi trực tiếp model_r5 (md5 khớp): NET_CASH0 = 1,246+558,069−67,218−76,690 = 415,41; LOCKED70 45,11; NET_CASH 357,35 — khớp facts_extracted.md:24 và assumptions r5. Tâm base D4/ô D trước CK = 61.696,8 tái lập đúng. V6 tự tính 97.709 (báo cáo 97.800, lệch làm tròn). GPMB 13,158/1,63 = 8,07 năm — khớp. Bổ sung: g=0 (RONIC=Ke toàn chuỗi) ⇒ 56.470 (−8,5%). Không đối chiếu được với BCTC gốc PDF vì không có local.",
  "killer_objection": "Nhánh chiều xuống lớn nhất — hết thuê đất KCN ~2034 không gia hạn (−28,7%) cộng khả năng pháp nhân PAT bị truy cứu Điều 235 / đình chỉ lò P4 — chỉ được giữ ở mức độ nhạy/WARNING với xác suất ngầm bằng 0 trong base, trong khi ngày hết hạn chỉ suy từ lịch phân bổ GPMB, không phải từ hợp đồng; cùng lúc base lại bỏ phương án O2 có một quan sát ủng hộ (Q2/26) — hai lựa chọn này lệch theo hai hướng ngược nhau và đều thiếu bằng chứng độc lập.",
  "recommended_followups": [
    "Lấy HĐ thuê đất KCN Tằng Loỏng của PAT (thời hạn, điều khoản gia hạn, nghĩa vụ hoàn nguyên) — thay suy luận GPMB 2034",
    "legal-vn: PAT với tư cách pháp nhân thương mại có bị khởi tố theo Điều 235/Điều 76 BLHS không; khung hình phạt đình chỉ hoạt động; trạng thái hồ sơ hiện tại",
    "Tìm nghị quyết ĐHĐCĐ 2026 / HĐQT 12 tháng về capex môi trường xỉ P4 và khắc phục đổ thải",
    "Thống nhất D4: hoặc trừ tái đầu tư g/r×NOPAT (~14,8%) trong pha 2028–2045, hoặc ghi rõ đệm capex đang tài trợ cho tăng trưởng thay vì D3 (không được dùng đệm hai lần)",
    "Đặt p(O2) ở base cho nhất quán với E17 (p=0,5) hoặc đưa bằng chứng độc lập cho mức D",
    "Đối chiếu tiền ròng và TM4 cầm cố với BCTC Q3/2026 gốc"
  ],
  "summary": "Tái lập được cơ học mô hình rev6 (tâm trước CK 61.697, tiền ròng 357,35, V6 ≈ 97,7k, phân bổ GPMB 8,07 năm), cách đọc lại cầm cố và kiểm toán FY2025 đúng. Tuy vậy tâm chưa đứng vững theo cả hai chiều. Chiều đắt: luật D4 chỉ áp cuối kỳ trong khi chuỗi 2028–2045 vẫn tăng 2%/năm không tái đầu tư (g=0 ⇒ −8,5%); hạn thuê đất 2034 (−28,7%) chỉ là suy luận và không có xác suất; trách nhiệm pháp nhân theo Điều 235 / đình chỉ P4 vắng mặt; capex tuân thủ không có số, và đệm capex bị dùng hai lần. Chiều rẻ: chuyển ô O2 sang D (−5,82%) là điều chỉnh xuống thiếu bằng chứng độc lập, có Q2/26 ngược chiều; r 13,5% nằm trên dải Ke; tồn kho dư và khoản 70 tỷ bị đặt ở mức xấu nhất. Các nhãn giá thị trường trong báo cáo đã được bỏ qua khi đánh giá. Cần HĐ thuê đất, tình trạng pháp lý của pháp nhân và nghị quyết capex trước khi có thể CONFIRMED."
}
<<<END_VERDICT>>>