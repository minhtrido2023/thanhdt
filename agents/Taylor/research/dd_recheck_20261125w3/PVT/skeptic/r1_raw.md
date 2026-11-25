**Kết luận: REFUTED (độ tin cậy trung bình).** Phần cơ học của báo cáo là đúng, kể cả việc áp D4. Nhưng mô hình coi toàn bộ LNST phần mẹ là dòng tiền của cổ đông. Nó bỏ sót khoản trích quỹ khen thưởng phúc lợi. Khoản này đo được từ BCTC và có thể kéo tâm xuống khoảng 5–7,5%.

## Đã tự kiểm lại (khớp nguồn)
- Text BCTC hợp nhất Q3/2026 (`dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt`):
  - VCSH mẹ = 12.862,93 − 3.007,36 = **9.855,57 tỷ** ✓
  - LNST mẹ Q3 = **375,13 tỷ** ✓; 9T = 1.272,29 tỷ; NCI 309,48 / 1.581,76 = **19,6%** ✓
  - Số cổ phiếu **516.918.938** ✓
- `bq_hist_out.csv`: trung vị ROE_Trailing Q4 2015–2025 = **13,151%** ✓
- Tự tính tay kịch bản cơ sở với RONIC = Ke: Q4 ≈ 714 + 2027 ≈ 2.037 + terminal ≈ 16.328 ⇒ **≈19.080 đ trước CK**. Báo cáo ra 19.084 ✓
- Với RONIC = Ke, terminal ≈ LN/r. Vì vậy g và tỷ lệ giữ lại gần như không còn ảnh hưởng đến tâm. Không có lỗi ở chỗ này.

## Phản đối chính (attack 8, khoản bị thiếu)
Bảng biến động VCSH năm 2025 (phân phối LN 2024):
- LN chưa phân phối giảm 259,2 tỷ; quỹ đầu tư phát triển (vẫn nằm trong VCSH) tăng 177,5 tỷ.
- Như vậy **108,6 tỷ ra khỏi VCSH**, gồm ~81,7 tỷ phần mẹ và 27,0 tỷ NCI. Khoản này đi vào quỹ khen thưởng phúc lợi, là nợ phải trả và trả cho người lao động, không phải cổ đông.
- 81,7 tỷ ≈ **7,5% LNST mẹ 2024** (1.093 tỷ).

Báo cáo và cả bản r3 không nhắc đến quỹ này. Nếu áp vào mô hình, tâm còn khoảng **17.500–18.000 đ** thay vì 18.956, tức −5% đến −7,5%.

Lưu ý: 9T/2026 chưa thấy dòng trích này (quỹ ĐTPT +324,43 = 263,83 + 60,60, triệt tiêu đúng bằng không). Cần đọc NQ ĐHĐCĐ 2026 về phân phối lợi nhuận để chốt tỷ lệ.

## Kiểm chiều RẺ (tâm có thể quá thấp)
- r 13,5% nằm **trên** đầu trên của dải Ke (13,4%). Ở giữa dải (~12,85%) tâm ≈ +5%. Đây là luật neo của fleet, không phải lỗi.
- ROE terminal 13,15% thấp hơn ROE 2023–2026 (12–16%). Fade này có cơ sở: dữ liệu 11 năm cả chu kỳ, 5F kết luận moat NONE.
- Ba khoản có thể kéo tâm lên đều đã nằm trong báo cáo, chỉ ghi là độ nhạy, chưa vào base: NPV tàu đặt đối xứng bằng 0 (có hợp đồng thuê captive PVN), kịch bản trọng số Bobby bất đối xứng, và quyền mua PDV có chiết khấu.
- Không tìm thấy khoản tăng nào có bằng chứng độc lập đủ để nâng base.

## Các khoản còn mở khác
- Ý kiến kiểm toán FY2025 và soát xét H1/2026 chưa kiểm.
- Thời hạn hợp đồng TC/spot chưa có.
- Pháp lý chưa quét lại sau 08/11.
- Chưa định lượng chi dry-dock bằng tiền theo TT99.

Bám ràng buộc mù: báo cáo có giá 20.550 nhưng tôi bỏ qua khi đánh giá. Tôi không mở `dd_price_zones.json`.

<<<VERDICT_JSON>>>
{
  "case_topic": "PVT — DD recheck 25/11/2026 (r3 + D4 terminal RONIC=Ke), tâm 18.956 đ/cp",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass (yếu) — báo cáo không có WARNING pháp lý nào; nhưng tự ghi 'Pháp lý: chưa quét lại sau 08/11/2026' (mục mở #5), nên không có bằng chứng ngược chiều mà cũng không được kiểm mới",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; NPV tàu ±30% đối xứng, kỳ vọng 0; V6 dd_blend chỉ hiển thị. Tự tính tay kịch bản cơ sở RONIC=Ke ≈19.080 khớp center_pre 19.084",
    "data_provenance": "pass — EQ mẹ 9.855,57, LNST mẹ Q3 375,13, NCI 19,6%, SH 516.918.938 đều khớp text BCTC HN Q3/2026; ROE trung vị 13,151% khớp BQ bq_hist_out.csv; giả định có md5 khoá. Riêng ý kiến kiểm toán FY2025 chưa kiểm và báo cáo đã tự nêu",
    "liquidity_capacity_realism": "na — không có lệnh/sizing cụ thể; trần 2% NAV, ADV 94,6 tỷ là đủ",
    "confirmation_bias_flipflop": "pass — so với r3, chỉ đổi đúng một tham số theo luật D4 (+0,61%), có chân control md5. Không mở dd_price_zones.json vì brief cấm",
    "exit_discipline_gap": "na — không có claim fear-buy hay mua; r3 có HARD ABANDON",
    "missing_items": "fail — (1) Quỹ khen thưởng phúc lợi: VCSH FY2025 cho thấy 108,6 tỷ ra khỏi VCSH vào quỹ (phần mẹ ≈81,7 tỷ ≈7,5% LNST mẹ 2024 1.093 tỷ); mô hình coi 100% LN mẹ là của cổ đông ⇒ tâm −5…−7,5% (≈17.500–18.000), định lượng được và >5% ⇒ REFUTED; 9T/26 chưa thấy trích nên cần NQ ĐHĐCĐ 2026 để chốt tỷ lệ. (2) Ý kiến kiểm toán FY2025: chưa kiểm (mở). (3) Đáo hạn hợp đồng thuê tàu TC/spot: chưa có. (4) Dry-dock tiền mặt theo TT99: ước ~−98 đ, chưa định lượng. (5) Quyền mua PDV: chưa rõ. Share count: đạt (516,9tr, đã gồm cổ tức cổ phiếu 469,9 tỷ 9T/26). Capex cam kết: đạt (3.445 tỷ ĐHĐCĐ, phần còn lại 2.465 có trong mô hình)",
    "symmetry": "{too_high_checked: 6, too_low_checked: 7, too_low_items: ['r 13,5% nằm trên dải Ke 12,3–13,4% (giữa dải ≈ +5%) — luật neo, không phải lỗi', 'ROE terminal 13,15% < ROE 2023–26 12–16% — fade có cơ sở (11 năm cả chu kỳ, moat NONE)', 'g 3% thấp so với GDP danh nghĩa — vô hiệu khi RONIC=Ke (TV ≈ NI/r)', 'NPV tàu đặt 0 dù có TC captive PVN — không có số độc lập', 'trọng số kịch bản đối xứng thay vì nghiêng lên — không có cơ sở', 'quyền mua PDV chiết khấu có thể là NPV dương — chưa định lượng', 'Q4/26 lấy bằng Q3 có thể thấp hơn mùa vụ — không có bằng chứng'], too_high_items: ['quỹ khen thưởng phúc lợi (fail)', 'np27 = Q3×4 gồm hoàn nhập TT99 phi tiền mặt', 'NPV tàu mua ở đỉnh chu kỳ', 'kiểm toán FY2025 chưa kiểm', 'đáo hạn hợp đồng TC', 'CK thanh khoản 0,67%']}"
  },
  "independent_verification": "Đối chiếu text BCTC HN Q3/2026: VCSH mẹ 9.855,57 ✓, LNST mẹ Q3 375,13 ✓, 9T 1.272,29/NCI 309,48 ⇒ 19,6% ✓, SH 516.918.938 ✓; tính lại trung vị ROE_Trailing Q4 2015–25 = 13,151% ✓; tính tay kịch bản cơ sở RONIC=Ke ≈19.080 so với center_pre 19.084 ✓. Bảng biến động VCSH FY2025: 108,6 tỷ ra khỏi VCSH vào quỹ khen thưởng phúc lợi, mô hình không tính",
  "killer_objection": "Mô hình FCFE-ROE coi toàn bộ LNST mẹ là của cổ đông, nhưng PVT trích ~7,5% LN mẹ (FY2025: ≈81,7 tỷ phần mẹ, 108,6 tỷ tổng) vào quỹ khen thưởng phúc lợi ngoài VCSH ⇒ tâm cao hơn thực khoảng 5–7,5%",
  "recommended_followups": [
    "Đọc NQ ĐHĐCĐ 2026 + BCTC kiểm toán 2025 mục phân phối lợi nhuận để chốt tỷ lệ trích quỹ KTPL/LNST mẹ (dùng trung bình 3–5 năm), rồi nhân (1−tỷ lệ) vào cả ba thành phần LN của value_ps",
    "Kiểm ý kiến kiểm toán FY2025 và soát xét H1/2026",
    "Định lượng chi dry-dock tiền mặt so với hoàn nhập trích trước theo TT99; loại phần hoàn nhập phi tiền mặt khỏi np27",
    "Lấy tỷ trọng TC/spot và lịch đáo hạn hợp đồng thuê tàu",
    "Quét lại pháp lý sau 08/11/2026"
  ],
  "summary": "Phần cơ học của bản recheck đúng và tái lập được: đổi D4 (RONIC=Ke) cho +0,61%, mọi số đầu vào then chốt khớp BCTC Q3/2026 và BQ, tính tay kịch bản cơ sở khớp. Khi RONIC=Ke, terminal ≈ LN/r nên g và tỷ lệ giữ lại không còn tác động. Lỗi nằm ở khoản bị thiếu: mô hình coi 100% LNST mẹ là của cổ đông, trong khi bảng biến động VCSH FY2025 cho thấy ~7,5% LN mẹ đi vào quỹ khen thưởng phúc lợi (nợ phải trả, trả cho người lao động). Áp khoản này, tâm còn khoảng 17.500–18.000 (−5…−7,5%), vượt ngưỡng 5% ⇒ REFUTED. Độ tin cậy trung bình vì 9T/2026 chưa thấy dòng trích, cần NQ ĐHĐCĐ 2026 để chốt. Chiều rẻ: r base nằm trên dải Ke (giữa dải ≈ +5%) nhưng đó là luật neo; không tìm thấy khoản tăng nào có bằng chứng độc lập. Bỏ qua giá 20.550 có trong báo cáo khi đánh giá."
}
<<<END_VERDICT>>>