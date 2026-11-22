Kết luận: **REFUTED**. Các con số trong báo cáo khớp nguồn, nhưng cách ghép mô hình đếm hai lần dòng lợi nhuận của nhà máy cũ. Kết luận "không có biên an toàn" có thể vẫn đúng. Riêng tâm r2 (20.717) và nhãn r2 thì không đứng được.

**Đã tự kiểm lại (khớp):**
- LN mẹ năm từ BQ `ticker_financial`: 2019–2025 = 244,0 / 179,7 / 208,9 / 353,2 / 209,2 / 240,8 / 208,9. Trung bình 234,96, khớp con số 235,0 của báo cáo.
- 9T/2026 = 258,3, khớp.
- Tính lại tâm kịch bản CƠ SỞ: (235,0 − 32,65)/0,135 + 525,6 − 49,96 + 346,48 = 2.321 tỷ. Chia 110,50 triệu cổ phiếu được 21.005 đ/cp, khớp 21.002.

**Lỗi chính (thiếu hạng mục, attack 8; luật D3 22/11, bài học QTP):**
- E_core là lợi nhuận lịch sử của nhà máy BH1, tức nhà máy đang bị cưỡng chế tháo dỡ (QĐ 2408, QĐ 1122). Mô hình vẫn vốn hoá dòng này vĩnh viễn: 202,35/0,135 ≈ 1.499 tỷ.
- Cùng lúc, mô hình cộng thêm Nhơn Trạch theo NPV = 0 và bỏ qua khoảng 1.494 tỷ capex còn phải chi.
- Nhà máy cũ không thể tạo lợi nhuận mãi mãi nếu không có nhà máy thay thế. Phần capex dùng để thay công suất cũ là capex tuân thủ/duy trì, nên phải tính là dòng tiền ra.
- Errata r1 đã nêu đúng cách (b) này, nhưng r2 chọn cách (a) mà không giải quyết chuyện đếm hai lần.
- Mức ảnh hưởng: nếu 100% là thay thế thì khoảng −13.500 đ/cp (−65% so với tâm); nếu một phần ba thì khoảng −4.500 đ/cp. Đằng nào cũng vượt xa ngưỡng 5%.
- Báo cáo không nêu công suất BH1 cũ, nên không tách được phần thay thế với phần tăng trưởng.

**Chiều ngược lại (tâm có thể quá THẤP):**
- Bồi thường BH1 = 0, và tài sản đất HCM bị thu hồi = 0 dù báo cáo chưa đọc nội dung.
- Công suất 307.900 t có thể vượt nhà máy cũ, tức có phần tăng trưởng thật.
- Nền Q4 thấp.
- Các yếu tố này bù được một phần, nhưng không đủ cơ sở để bù khoản hàng nghìn tỷ.

**Nguồn và tái lập:**
- Thư mục `src/` không còn tồn tại. Các file `fin_csv_bq.csv`, `px_csv.csv`, `run1.txt`, `run2.txt`, `model_out.json` và các file LOCK cũng không có trong `calc/`. Vì vậy lệnh tái lập trong báo cáo không chạy được.
- `calc/assumptions.json` có mtime 20/11, sau ngày báo cáo 09/11. Md5 không đối chiếu được vì file LOCK đã mất.
- Ý kiến kiểm toán FY2025 Taylor ghi lại theo errata, chưa tự kiểm.
- Theo `dd-process-review-20261122.md` (F12), CSV nằm trong nhóm "đã áp đính chính, không chạy vòng phản biện nữa", tức r2 chưa từng được phản biện lại.

**Attack 6:** tôi chỉ so r1 với r2 trong thư mục ca. Không mở `dd_price_zones.json` vì brief cấm. Bộ phân loại quyền cũng đã chặn một lệnh định đọc riêng các dòng CSV trong file này, và tôi không thử lại.

<<<VERDICT_JSON>>>
{
  "case_topic": "CSV (Hoá chất Cơ bản Miền Nam) DD r2 09/11/2026 — tâm 20.717, nhãn TRONG vùng",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không khẳng định fear-buy/§2.5",
    "scandal_migration_risk": "pass — cưỡng chế BH1 (QĐ 2408) và dừng TB2 (QĐ 1122) là thi hành đề án chuyển đổi KCN, không phải xử phạt; báo cáo có nêu. Nhưng các NQ giao dịch NCLQ 2026 và nội dung thu hồi đất HCM (19/10) chưa đọc",
    "optimistic_comp_sotp_bias": "fail — không dùng comp, nhưng phép cộng SOTP đếm hai lần: E_core (lợi nhuận nhà máy BH1 đang bị tháo dỡ) vốn hoá vĩnh viễn ≈1.499 tỷ, CỘNG nhà máy thay thế Nhơn Trạch theo NPV=0 cộng 346,5 tỷ đã chi, bỏ qua ~1.494 tỷ capex còn lại. Errata r1 đã nêu cách (b), r2 không giải quyết",
    "data_provenance": "fail — số BCTC/BQ khớp (LN mẹ 2019-25 kiểm lại trên BQ), nhưng src/ (PDF gốc), fin_csv_bq.csv, px_csv.csv, run1/run2, model_out.json, LOCK_*.txt đều không còn ⇒ lệnh tái lập không chạy được; assumptions.json mtime 20/11 > ngày báo cáo 09/11, không đối chiếu được md5; ý kiến kiểm toán FY2025 Taylor chưa tự kiểm (ghi theo errata); 110.499.910 cp không ghi ngày/nguồn",
    "liquidity_capacity_realism": "na — không có claim sizing/fear-buy; CK thanh khoản chỉ là chiết khấu định giá (≤1,7%)",
    "confirmation_bias_flipflop": "pass (yếu) — r1→r2 (17.273→20.717, TRÊN→TRONG) do sửa phương pháp từ errata skeptic, không phải tin mới, có ghi minh bạch; nhưng r2 chưa từng qua vòng phản biện (F12 trong dd-process-review-20261122.md). Chỉ so r1/r2 trong thư mục ca; dd_price_zones.json không mở vì brief cấm",
    "exit_discipline_gap": "na — không có đề xuất vị thế; mốc đổi nhận định hai chiều và HARD ABANDON đã nêu ở §8",
    "missing_items": "fail — (1) capex thay thế/tuân thủ cho di dời bắt buộc: phần capex Nhơn Trạch còn lại ~1.494 tỷ (1.294 nếu 200 tỷ ứng trước là của dự án) ≈ 11.700–13.500 đ/cp; phần thay công suất cũ phải là dòng tiền ra (D3) ⇒ tâm giảm ~4.500 (1/3 là thay thế) tới ~13.500 đ/cp (100%); (2) công suất BH1 cũ vắng mặt ⇒ không tách được thay thế với tăng trưởng; (3) lịch đóng BH1/chạy Nhơn Trạch (G4) vắng; (4) đất HCM thu hồi và bồi thường BH1 = 0 chưa đọc (chiều tăng, chưa định lượng); (5) quỹ khen thưởng phúc lợi trích từ LN không bàn; (6) NQ NCLQ chưa đọc. Ý kiến kiểm toán FY2025 có (theo errata), BCTC Q3/2026 có"
  },
  "independent_verification": "BQ ticker_financial: tổng NP_P0 theo năm CSV 2019-2025 = 244,0/179,7/208,9/353,2/209,2/240,8/208,9 ⇒ TB 234,96 (báo cáo 235,0), min 179,7, 9T/26 258,3 — khớp. Tính lại tâm CƠ SỞ: (235,0−32,65)/0,135 + 525,6 − 49,96 + 346,48 = 2.321 tỷ / 110,5 tr cp = 21.005 (báo cáo 21.002) — khớp.",
  "killer_objection": "Lợi nhuận chuẩn hoá đến từ nhà máy BH1 đã khấu hao gần hết và đang bị cưỡng chế tháo dỡ; muốn giữ dòng lợi nhuận này thì phải bỏ ~1.840 tỷ xây Nhơn Trạch. Mô hình vừa vốn hoá vĩnh viễn lợi nhuận cũ, vừa coi capex thay thế là NPV=0 cộng phần đã chi ⇒ cùng một dòng tiền bị đếm hai lần, tâm có thể bị thổi lên tới ~13.500 đ/cp (~65%).",
  "recommended_followups": [
    "Dựng lại theo cách (b) của errata: E_core/r trừ capex thay thế còn lại (và khấu hao/lãi vay mới nếu có cơ sở), hoặc chỉ vốn hoá lợi nhuận BH1 tới ngày đóng cửa rồi cộng giá trị Nhơn Trạch",
    "Lấy công suất từng nhà máy BH1 cũ (xút, axit, HCl) để tách phần thay thế (dòng tiền ra) với phần tăng trưởng (được NPV=0)",
    "Khôi phục src/, fin_csv_bq.csv, px_csv.csv, LOCK_*.txt, run1/run2 hoặc tái tạo kèm md5 mới; giải thích mtime 20/11 của assumptions.json",
    "Đọc thông báo thu hồi đất HCM 19/10/2026 và bất kỳ phương án bồi thường BH1 nào (chiều tăng)",
    "Đóng G2 (242,4 tỷ trả trước người bán) và G4 (lịch chuyển giao) trước khi chốt tâm",
    "Tự đọc trang ý kiến kiểm toán FY2025 thay vì ghi theo errata"
  ],
  "summary": "Các số BCTC và BQ của báo cáo CSV r2 đều khớp (tôi đã tính lại LN mẹ 2019-25 và tâm kịch bản CƠ SỞ 21.005 so với 21.002). Lỗi nằm ở cách ghép mô hình: lợi nhuận lịch sử của nhà máy BH1, vốn đang bị cưỡng chế tháo dỡ, được vốn hoá vĩnh viễn (~1.499 tỷ), trong khi nhà máy thay thế Nhơn Trạch 1.840 tỷ lại được tính NPV=0 cộng phần đã chi, bỏ qua ~1.494 tỷ capex còn lại. Phần capex thay công suất cũ là capex tuân thủ/duy trì và phải là dòng tiền ra (D3, bài học QTP). Bỏ sót nó làm tâm cao thêm ~4.500 đến ~13.500 đ/cp tuỳ tỷ lệ thay thế, vượt xa ngưỡng 5%. Chiều ngược lại, bồi thường BH1, đất HCM và phần công suất tăng thêm bị đặt bằng 0 hoặc chưa định lượng, nên bù được một phần nhưng không đủ. Ngoài ra không tái lập được vì src/, file dữ liệu và file khoá đã mất, và r2 chưa từng qua phản biện. Tâm 20.717 và nhãn r2 không đứng được; cần dựng lại theo cách (b) sau khi có công suất BH1 cũ."
}
<<<END_VERDICT>>>