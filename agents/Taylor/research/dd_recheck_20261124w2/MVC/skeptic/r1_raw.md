**Kết luận: REFUTED, độ tin cậy trung bình.** Tâm 16.241 đ/cp đang được công bố khi chưa trừ một khoản phân phối bắt buộc mà chính báo cáo đã định lượng được. Khoản thứ hai là cam kết đầu tư cụm công nghiệp ≤500 tỷ, đang được gán NPV = 0 mà báo cáo không nhắc tới. Theo luật “thiếu hạng mục đo được, trọng yếu >5%” thì riêng khoản trích quỹ đã đủ để bác.

**Đã tự kiểm lại**
- **Nguồn trích quỹ:** đọc thẳng biên bản ĐHĐCĐ 2026 (`VI_BienBan…NghiQuyet.txt` ~767-785). Năm 2026 trích 39% đầu tư phát triển / 7% khen thưởng–phúc lợi / 2% HĐQT-BKS / 2% Ban điều hành / 50% cổ tức. Năm 2025 trích 7% + 1,5% + 1,5% trên LNST 122,52 tỷ. Khớp báo cáo.
- **Số học:** tự tính lại khớp cả bốn số.
  - Hệ số sở hữu chéo: 1/(1 − 0,4407 × 0,103) = 1,04755.
  - Dòng tiền hoạt động: 0,11 × 705,26 tỷ × 10 × 1,04755 / 17.704 = **−4,59%**.
  - Phần LNST 9T/26: **−1,51%**. Phần NNC: **−4,03%**. Tổng **−10,13%**.

**Các điểm yếu chính**
1. **Trích quỹ 11% chưa vào tâm (chiều ĐẮT).** Mức thực tế nhiều khả năng khoảng −5…−7%: lấy −4,59% cộng phần 9T/26. Báo cáo tự nhận khoản này lật luật 4 nhưng vẫn giữ tâm và vùng cũ.
2. **Cụm công nghiệp ≤500 tỷ (chiều ĐẮT).** Đây là cam kết đã qua ĐHĐCĐ, đang để NPV = 0, nằm ngoài base và ngoài lưới.
   - Bản r4 từng trừ −1.300 … −2.100 đ/cp (−8…−13%). Bản r5 đổi về 0 với lý do “chưa có kế hoạch/giá”, không có dữ kiện mới.
   - Bản recheck này chỉ nêu khoản này ở mục WARNING, không có trong mục “hạng mục thiếu”.
3. **Chiều RẺ — dải trích quỹ đang bị phóng đại:**
   - Quỹ trích trên LNST kế toán, tức sau khấu hao và sau lãi vay (nợ ròng tiến tới 1,4–1,5 nghìn tỷ). Mô hình lại áp 11% lên dòng tiền hoạt động chưa trừ khấu hao, nên mức −4,59% bị thổi lên.
   - Số 9T/26 lấy từ BCTC hợp nhất, có lãi liên kết NNC phi tiền mặt, nên phần −1,51% cũng bị thổi.
   - Cận −10,13% coi lãi liên kết là cơ sở trích quỹ. Thông thường quỹ trích trên LNST riêng, nơi chỉ có cổ tức NNC chuyển về chứ không có lãi liên kết.
   - r = 13,5% cao hơn đầu trên dải Ke (13,4%); β = 1 chỉ là giả định.
4. **Pháp lý và nguồn số còn mở:** chưa xác minh hạn giấy phép Tân Lập, chưa đọc ký quỹ phục hồi môi trường, chưa quét pháp lý sau 05/11. Số BCTC đọc từ pdftotext, chưa soát bằng mắt.

Báo cáo có nêu giá thị trường 13.500; tôi bỏ qua khi chấm mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "MVC — recheck DD r3 (dd_recheck_20261124w2), tâm 16.241 đ/cp, vùng P10–P90 9.940–23.471",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "fail (một phần) — các mục WARNING (sở hữu chéo 44,07%↔10,3% chung Chủ tịch; mua NNC lên 51% với bên liên quan; dư nợ BIDV 452 > hạn mức 350) chỉ chép lại từ r3; tự thừa nhận chưa quét pháp lý sau 05/11 và chưa xin ý kiến legal-vn về Điều 195 LDN. Không có tín hiệu chuyển hoá nào, nhưng phần kiểm chưa làm xong",
    "optimistic_comp_sotp_bias": "fail — SOTP để CCN ≤500 tỷ (cam kết của ĐHĐCĐ) ở NPV=0, ngoài base và ngoài lưới; r4 từng trừ −1.300/−2.100 đ/cp; recheck không nhắc trong hạng mục thiếu. Holding discount base = 0% là đầu lạc quan của dải 0–20% (−7,3% ở mức 20%), có công khai",
    "data_provenance": "pass (một phần) — tỷ lệ trích quỹ 11% và LNST 2025 122,52 tỷ truy được về NQ ĐHĐCĐ 2026; các thành phần ở tham số trung tâm truy được về calc_items_out.json; cảnh báo: số BCTC từ pdftotext chưa soát mắt, hạn GP Tân Lập chưa xác minh (là trục lưới 2035/W/2045)",
    "liquidity_capacity_realism": "na — DD_GENERAL; sizing 2% NAV có nêu nhưng thanh khoản kế thừa từ r3 (ADV60 0,189 tỷ, tranche ≤20% ADV), không phải luận điểm mới",
    "confirmation_bias_flipflop": "fail (nhẹ) — không mở sổ vùng giá (theo ràng buộc mù), nhưng lịch sử revision trong file r4→r5 cho thấy CCN chuyển từ trừ −1.300/−2.100 (r4) sang NPV=0 (r5) chỉ với lý do 'chưa có kế hoạch/giá', không có dữ kiện mới",
    "exit_discipline_gap": "na — DD_GENERAL, báo cáo không có luận điểm sizing fear-buy",
    "missing_items": "fail — (1) trích quỹ 11% LNST (NQ ĐHĐCĐ 2026) chưa vào tâm: −4,59% (cận dưới) … −10,13%, khả năng ≈ −5…−7% ⇒ >5% của tâm; (2) CCN ≤500 tỷ NPV=0, r4 ước −8…−13%; (3) ký quỹ phục hồi môi trường/đóng mỏ chưa đọc (không định lượng được, tham chiếu NNC 4,5 tỷ nhỏ); (4) hạn GP Tân Lập chưa xác minh (đã bao bằng lưới); kiểm toán: BCTC riêng 2025 chấp nhận toàn phần, soát xét 6T/26 sạch (r2) — pass; số cổ phiếu 100 tr (cổ tức 60 tỷ/600đ) khớp",
    "symmetry": "{too_high_checked: 6, too_low_checked: 7, too_low_items: ['11% áp lên dòng tiền chưa trừ khấu hao, chưa trừ lãi vay, trong khi quỹ trích trên LNST kế toán ⇒ −4,59% bị thổi phồng', 'LNST 9T/26 hợp nhất gồm lãi LK NNC phi tiền mặt ⇒ −1,51% bị thổi phồng', 'cận −10,13% coi lãi LK là cơ sở trích quỹ; LNST riêng chỉ gồm cổ tức NNC', 'r 13,5% cao hơn đầu trên dải Ke 13,4% (+0,26%); @12,3% +3,2%', 'β=1 chỉ là giả định — chưa có bằng chứng ủng hộ β thấp hơn, không đổi', 'CCN NPV có thể dương — không có bằng chứng cả hai chiều', 'trục biên Tân Lập 38% / upside up2034 / mỏ mới kịch bản tốt nằm ngoài base — nêu ra, không có dữ kiện mới']}"
  },
  "independent_verification": "Đọc thẳng VI_BienBan…NghiQuyet.txt: phân phối 2026 = 39/7/2/2/50%, 2025 = 20/7/1,5/1,5/70% trên LNST 122,52 tỷ — khớp. Tự tính lại hệ số sở hữu chéo 1,04755, cận dưới −4,59%, phần 9T −1,51%, phần NNC −4,03%, tổng −10,13% — khớp calc_items_out.json. Xác nhận trong r5 inventory rằng CCN 500 tỷ đang ở NPV=0, ngoài lưới.",
  "killer_objection": "Tâm 16.241 công bố khi chưa trừ khoản phân phối bắt buộc mà chính báo cáo đã định lượng được (11% LNST mỗi năm, ≈ −5…−7% sau khi hiệu chỉnh cơ sở); cộng thêm cam kết CCN ≤500 tỷ để NPV=0 không có căn cứ ⇒ tâm và vùng hiện tại thiên cao.",
  "recommended_followups": [
    "Rev mới: đưa trích quỹ 11% vào base trên cơ sở LNST RIÊNG (sau khấu hao, sau lãi vay), không áp lên dòng tiền hoạt động; tính lại tâm/P10/P90",
    "Đưa CCN ≤500 tỷ vào lưới với thu hồi 50/70/100% thay vì NPV=0 cố định",
    "Đọc thuyết minh ký quỹ phục hồi môi trường/đóng mỏ (Tân Lập + 2 mỏ mới)",
    "Xác minh hạn GP Tân Lập; legal-vn về Điều 195 LDN; quét pháp lý sau 05/11",
    "Soát mắt các số BCTC lấy từ pdftotext đang chịu tải"
  ],
  "summary": "Recheck chỉ đổi r và công khai khoản trích quỹ 11% LNST theo NQ ĐHĐCĐ 2026, nhưng vẫn giữ tâm 16.241. Tôi đã đối chiếu tỷ lệ 11% với biên bản gốc và tự tính lại cả bốn con số tác động (−4,59/−1,51/−4,03/−10,13%) — khớp. Hai chiều: cơ sở đang dùng thổi phồng mức trừ (dòng tiền chưa trừ khấu hao và lãi vay, LNST hợp nhất gồm lãi liên kết), nên mức thực tế nhiều khả năng ≈ −5…−7%, vẫn trên ngưỡng trọng yếu 5% ⇒ hạng mục thiếu đo được và trọng yếu ⇒ REFUTED. Thêm vào đó cụm công nghiệp ≤500 tỷ (r4 ước −8…−13%) vẫn ở NPV=0 không căn cứ và không có trong mục hạng mục thiếu. Chiều rẻ: r 13,5% cao hơn dải Ke (+0,3…+3,2% nếu hạ), nhưng không bù được khoản trích quỹ. Giá thị trường trong báo cáo đã được bỏ qua khi chấm."
}
<<<END_VERDICT>>>