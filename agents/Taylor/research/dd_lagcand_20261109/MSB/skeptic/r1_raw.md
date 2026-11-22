**Kết luận: REFUTED (độ tin cậy medium). Lỗi then chốt làm tâm bị kéo xuống THẤP, không phải lên cao.** Mô hình lấy ROE tính trên vốn chủ bình quân (khoảng 14%) để làm ROE tính trên vốn chủ đầu kỳ, nên lợi nhuận dự phóng bị hạ có hệ thống. Sửa lỗi này đẩy tâm lên khoảng +6 đến +10%, vượt ngưỡng trọng yếu 5%.

Tôi không xem giá thị trường. Các số giá có sẵn trong báo cáo (16.350, P/B 1,31x, hồi quy so với các ngân hàng cùng ngành) tôi bỏ qua khi chấm mô hình.

**Những gì tự tính lại và khớp:**
- Chạy lại `value()` từ `assumptions.json` (md5 `3f3ba648…` khớp). Kết quả XẤU 9.931 / CƠ SỞ 13.230 / TỐT 16.435, tâm 13.068 trước chiết khấu và 13.018 sau chiết khấu, đúng từng đồng.
- Các mức nhạy theo Ke khớp: 14.740 ở 12,5%, 13.844 ở 13%, 12.255 ở 14%.
- NPL hợp nhất 2,698%, bao phủ 47,17%, NPL riêng lẻ 2,46%: khớp với số liệu trong `notes_read.md`.
- Đối chiếu BigQuery: VCSH 30/09 là 46.857 và 31/12/25 là 42.446; LNST Q3 1.649. VCSH năm 2025 tăng 5.628, đúng bằng LNST 2025 là 5.628; 9 tháng 2026 tăng 4.411, gần bằng LNST 4.414. Như vậy không có khoản trích quỹ khen thưởng phúc lợi nào rò ra khỏi vốn chủ, và giả định payout 0 là hợp lý.

**Lỗi chiều RẺ (tâm quá thấp), định lượng được:**
- Cột `ROE_Trailing` 14,09% trong BigQuery chia cho vốn chủ bình quân (mẫu số khoảng 44,5 nghìn tỷ). Nhưng `model.py` nhân ROE với vốn chủ đầu kỳ.
- Cùng cách tính đầu kỳ như mô hình, số thực tế là: 2025 ≈ 15,3%; TTM ≈ 14,8%; 2026 ước tính ≈ 14,4%.
- ROE cuối kỳ 14% theo cách đầu kỳ chỉ tương đương khoảng 13,1% theo cách bình quân, tức là thấp hơn Ke 13,5%. Như vậy mô hình đã ngầm ép ROE về Ke, trái với luật 08/11 mà chính báo cáo dẫn ra.
- Tác động lên tâm: +0,5pp cho +5,9% (13.787); +0,8pp cho +9,5% (14.257); +1pp cho +11,9% (14.573).

**Rủi ro chiều ĐẮT (tâm quá cao), chưa định lượng được nên chỉ đủ mức INCONCLUSIVE:**
- **Lãi dồn tích:** lãi ghi nhận 9 tháng 22.349 so với lãi thực thu 20.394. Lãi phải thu từ tín dụng tăng 19%, nhanh hơn dư nợ (12%). Mô hình không áp haircut cho khoản này.
- **Phải thu ngoài sổ cho vay:** mua LC miễn truy đòi 9.229 cộng phải thu khác 18.501 (riêng Q3 tăng thêm 4.720 không tách được), chỉ có 38 tỷ dự phòng chung.
- **Chưa kiểm:** cho vay bên liên quan, trái phiếu doanh nghiệp đang nắm, CET1, ESOP.
- **Ý kiến kiểm toán FY2025:** lấy từ nguồn thứ cấp, trong khi file kiểm toán đã tải về nhưng chưa đọc. Lý do đổi kiểm toán viên cũng không được giải thích. Đây đúng là kiểu lỗi đã gặp ở TV1.

**Truy nguồn:** trong thư mục không có `src/*.pdf`, `bq_msb_px.csv`, các file `*_out.txt` hay `LOCK_*`. Vì vậy `model.py` không chạy lại nguyên vẹn được, và các số BCTC chỉ truy được về sổ ghi chép của chính agent, ngoại trừ hai số đã đối chiếu BigQuery ở trên.

**Mức thay đổi tâm giữa r1 và r2:** không thể so với sổ vùng giá vì ràng buộc mù cấm mở `kb/dd_price_zones.json`, nên tôi so r1 với r2 trực tiếp. Tâm tăng +2,2% là do sửa lại cho kịch bản đối xứng theo errata của skeptic r1, có nêu căn cứ (ROE_Min5Y), không phải do thông tin mới. Tôi chấp nhận được, nhưng mức +2,2% này nhỏ hơn hẳn lỗi về cách tính ROE ở trên.

<<<VERDICT_JSON>>>
{
  "case_topic": "MSB — DD r2 (dd_lagcand_20261109), RI ngân hàng, tâm 13.018 đ/cp",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass (yếu) — không có mục pháp lý WARNING; chỉ 1 lượt WebSearch standard, chưa kiểm thanh tra NHNN gần nhất (báo cáo tự ghi 'chưa kiểm')",
    "optimistic_comp_sotp_bias": "pass — headline thuần RI, so sánh ngang ngành (18 NH) không vào tâm; trọng số kịch bản đối xứng; trục haircut phải thu 4.101 chỉ một chiều nhưng đúng bản chất (sổ sách là trần). Có lỗi định nghĩa ROE — xem missing_items/killer",
    "data_provenance": "fail (một phần) — số BCTC chỉ truy được về calc/notes_read.md; src/*.pdf, bq_msb_px.csv, model_out/LOCK/*_out.txt KHÔNG có trong thư mục ⇒ model.py không chạy lại nguyên vẹn được. Đã đối chiếu BQ: VCSH 46.857/42.446, LNST Q3 1.649 khớp. Ý kiến kiểm toán FY2025 'chấp nhận toàn phần' lấy từ nguồn thứ cấp trong khi file KT 2025 đã tải nhưng chưa đọc",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất size vượt khẩu phần; không đánh giá theo thị giá",
    "confirmation_bias_flipflop": "pass — r1→r2 tâm +2,2% (12.739→13.018) do đối xứng kịch bản XẤU theo errata skeptic r1, có căn cứ (ROE_Min5Y 14,2%), không phải thông tin mới; không mở dd_price_zones.json theo ràng buộc mù",
    "exit_discipline_gap": "na — không có claim sizing/fear-buy; có bảng trigger hai chiều ở mục 6",
    "missing_items": "fail — (1) ROE_T 14% hiệu chỉnh theo ROE_Trailing BQ (vốn chủ bình quân, mẫu số ≈44,5 nghìn tỷ) nhưng model nhân trên vốn chủ đầu kỳ; ROE đầu kỳ thực tế 2025 15,3%, TTM 14,8%, 2026E 14,4% ⇒ tâm thấp ≈6–10% (+0,5pp → +5,9%, +0,8pp → +9,5%) — định lượng được, >5%; (2) lãi dồn tích: thu thực 20.394 vs ghi nhận 22.349 (9T), lãi phải thu tín dụng +19% vs dư nợ +12%, không haircut — chưa định lượng, ước ~−2–3% nếu haircut 20%; (3) LC miễn truy đòi 9.229 + phải thu khác 18.501 (Q3 +4.720 không tách) chỉ có DP chung 38 tỷ — chưa định lượng; (4) bên liên quan, TPDN, CET1, ESOP chưa kiểm; (5) rò quỹ khen thưởng phúc lợi: PASS — ΔVCSH 2025 = LNST 5.628, 9T26 4.411 ≈ 4.414; số cổ phiếu 3.744 tr (VĐL 31.200 + thưởng 20% từ VCSH) PASS; quyền mua 936 tr @10.000 có trong model PASS; CAR/NPL/nhóm 2/bao phủ/LDR/CASA có mặt PASS"
  },
  "independent_verification": "Chạy lại value()/dist() độc lập từ assumptions.json (md5 khớp): XẤU 9.931 / CƠ SỞ 13.230 / TỐT 16.435, tâm 13.068 trước CK → 13.018 sau CK, Ke 12,5/13/14% = 14.740/13.844/12.255 — khớp đúng. NPL HN 2,698%, bao phủ 47,17%, NPL riêng lẻ 2,46% khớp notes. BQ ticker_financial: BVPS×OShares 2026Q3 = 46.857, 2025Q4 = 42.446, NP_P0 Q3 = 1.649 khớp; ROE_Trailing 14,09% ⇒ mẫu số ≈44,5 nghìn tỷ (vốn chủ bình quân), chứng minh lệch định nghĩa ROE.",
  "killer_objection": "ROE cuối kỳ 'giữ ở mức dữ liệu 14%' thực chất ≈13,1% nếu tính trên vốn chủ bình quân như số liệu được trích (thấp hơn Ke 13,5%), vì model nhân ROE trên vốn chủ ĐẦU KỲ trong khi ROE_Trailing BQ là trên vốn chủ BÌNH QUÂN; ROE đầu kỳ thực tế 14,4–15,3% ⇒ tâm thấp có hệ thống ~6–10%, trái luật 08/11 'không ép ROE_T về Ke'. Ngược chiều, các khoản lãi dồn tích và phải thu ngoài sổ cho vay chưa có haircut có thể bù trừ một phần.",
  "recommended_followups": [
    "Hiệu chỉnh lại toàn bộ path/ROE_T sang cùng một cách tính (ROE trên vốn chủ đầu kỳ) và nêu rõ cách tính; chạy lại tâm/P10/P90",
    "Đọc BCTC KT 2025 gốc: ý kiến kiểm toán, lý do đổi kiểm toán viên, thuyết minh bên liên quan, bancas trả trước",
    "Định lượng haircut lãi dồn tích (lãi phải thu tín dụng 8.103 tại 30/06, tách theo nhóm nợ) như một trục kịch bản",
    "Tách phải thu khác 30/09 (18.501; Q3 +4.720) và rủi ro đối tác LC miễn truy đòi 9.229",
    "Đưa src/*.pdf, bq_msb_px.csv và các file *_out/LOCK vào thư mục để tái lập được"
  ],
  "summary": "Số học của mô hình RI đúng: tự tính lại khớp từng đồng với 13.018, và các số bảng cân đối/KQKD đã đối chiếu BQ đều khớp. Tuy nhiên có một lỗi định nghĩa làm lệch tâm theo chiều THẤP: ROE 14% lấy từ ROE_Trailing BQ (vốn chủ bình quân) nhưng được nhân trên vốn chủ đầu kỳ, nên ROE dài hạn của kịch bản CƠ SỞ thực chất ≈13,1% < Ke, tức ngầm ép ROE về Ke. Theo cùng cách tính đầu kỳ, ROE quan sát là 14,4–15,3%, và sửa lại đẩy tâm lên khoảng +6–10% (>5% ⇒ REFUTED). Ở chiều ĐẮT có các khoản chưa định lượng (lãi dồn tích tăng nhanh hơn dư nợ, LC miễn truy đòi và phải thu khác lớn với dự phòng 38 tỷ, bên liên quan/TPDN/CET1 chưa kiểm, kiểm toán FY2025 chưa đọc gốc) có thể bù trừ một phần. Truy nguồn còn yếu vì file gốc và output không có trong thư mục. Đã bỏ qua mọi số thị giá có trong báo cáo khi chấm."
}
<<<END_VERDICT>>>