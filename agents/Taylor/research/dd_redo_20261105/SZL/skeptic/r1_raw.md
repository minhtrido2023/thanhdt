**Kết luận: INCONCLUSIVE (độ tin trung bình).** Các con số BCTC của r3c khớp nguồn độc lập, và cách sửa lỗi B (KTPL theo khung BÁN) là đúng. Nhưng trong base vẫn còn những lựa chọn chỉ kéo tâm về một chiều, chưa có căn cứ. Mỗi lựa chọn trên 5% tâm, cả về phía đắt lẫn phía rẻ. Thêm vào đó, tệp nguồn cần để tái lập không còn trong cây làm việc.

**Đã tự kiểm lại (BQ `ticker_financial`):**
- LNST 9T/2026 = 32,12 + 30,57 + 69,90 = **132,59**, khớp `NP_9M`.
- LNST 2025 = 140,69, khớp mẫu số của KTPL 11,215%.
- Tiền 171,22, vay ngắn hạn 110,03, vay dài hạn 196,34 và 48,199 tr cp tại Q3/26 đều khớp.
- Tính tay tại tham số trung tâm: lõi ≈ 746, SOTP ≈ 1.263 tỷ, tức 26.208 đ trước chiết khấu và ≈ 25.128 sau CK 4,12%. Báo cáo ghi 25.165; phần chênh do 1/r lồi trên lưới. Khớp.

**Chiều tâm quá THẤP:**
- **BĐS đầu tư mới 166,9 tỷ không vào base, trong khi XDCB 407 được cộng theo giá vốn.** Hai khoản bị đối xử khác nhau, ảnh hưởng +3.320 đ (+13%). Tiền làm khoản 166,9 đã nằm trong nợ ròng và capex, nhưng tài sản thì không được cộng. Không có tài liệu nào giải thích vì sao loại, hay phần lợi nhuận của nó đã nằm trong N0 bao nhiêu. Phần cần cộng lại nằm đâu đó trong khoảng 0 đến +3.320.
- **Ký quỹ dài hạn 147 tỷ trừ theo mệnh giá tới 2053**, không chiết khấu về hiện tại (PV), ảnh hưởng +2.827 (+11%). Đây là khoản điều chỉnh giảm, mà luật hai chiều của user đòi căn cứ riêng; báo cáo không đưa ra.
- Doanh thu tài chính bị loại 100% trong khi chi phí tài chính chỉ loại ×0,8. Lệch nhỏ, khoảng 0,6%.

**Chiều tâm quá CAO:**
- **N0 = 131,1 lấy từ 9T có biên đang ở đỉnh chuỗi.** Chính ADDENDUM_5F ghi GPM TTM 39% so với trung bình chu kỳ 33,6%. Lưới N0 ±12% lại đối xứng quanh mức đỉnh này. Ở mức 2025 (115,3), tâm giảm −1.791.
- Holdco trên SZC/SZB đặt 0%, và không có chiết khấu cho cỡ khối khi bán lô SZB.

**Mục còn thiếu (attack 8):**
- Không nêu ý kiến kiểm toán FY2025.
- Không xét tiền thuê đất hằng năm tăng theo bảng giá đất mới. Khoản trích treo 44,3 tỷ là dấu hiệu, và nếu khoản này đã ghi vào chi phí 9T thì N0 còn bị nhân ×4/3 cả phần một lần.
- Không có nghị quyết capex của Long Phước: phần 513 tỷ còn phải chi chỉ dựa trên báo chí.
- Không xét capex tuân thủ môi trường của KCN.
- Mốc 2053 chỉ có căn cứ cho một phần đất (TM17).

**Truy nguồn:** `src/Q3_2026_hopnhat.pdf`, `assumptions_r3c.json` và `model_r3c_out.txt` đã bị TRIM ngày 19/11 (commit `14ad1c925`). Hiện chỉ lấy lại được từ git `fc5bd02d9`, nên lệnh tái lập ghi trong báo cáo không chạy được.

Báo cáo có ghi giá thị trường; tôi bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "SZL (Sonadezi Long Thành) — DD redo r3c, REPORT_r3c.md",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không claim fear-buy §2.5 (ghi rõ 'Không đủ điều kiện sleeve fear-buy §2.5')",
    "scandal_migration_risk": "pass (yếu) — WARNING thanh tra SNZ/Đồng Nai được nêu, không vào base, HARD ABANDON (a) chạm pháp nhân/tài sản KCN có; nhưng báo cáo tự ghi 'chưa tra lại sau 05/11' ⇒ trạng thái pháp lý hiện tại chưa xác minh",
    "optimistic_comp_sotp_bias": "fail (hai chiều) — SOTP không nhất quán: XDCB 407 cộng theo giá vốn (NPV 0) nhưng BĐS đầu tư mới 166,9 (mã 241 1.011,9→1.178,8) bị loại khỏi base dù vốn của nó đã nằm trong nợ ròng/capex (+3.320 đ, +13%, không ghi lý do loại); ký quỹ DH 147 trừ theo mệnh giá đến 2053 thay vì PV (+2.827, +11%) — điều chỉnh giảm không có căn cứ riêng. Ngược lại: N0 neo 9T/2026 ở đỉnh biên (GPM TTM 39% vs TB chu kỳ 33,6% theo ADDENDUM_5F) với lưới đối xứng ±12%; về mức 2025 (115,3) ⇒ −1.791; holdco 0% và không chiết khấu khối cho cổ phần SZB",
    "data_provenance": "pass một phần — số BCTC chịu lực khớp BQ (NP 9T 132,59; LNST 2025 140,69; tiền 171,22; vay 110,03/196,34; 48,199 tr cp, đối chiếu cổ phiếu quỹ ở r3). Nhưng src/Q3_2026_hopnhat.pdf, assumptions_r3c.json, model_r3c_out.txt, file giá/oshares đã bị TRIM 19/11 (commit 14ad1c925), chỉ còn trong git fc5bd02d9 ⇒ lệnh tái lập/LOCK md5 trong báo cáo hiện không chạy được. Tổng vốn Long Phước 920 lấy từ [báo chí]; tỷ lệ lấp đầy ~91% không có nguồn; căn cứ luật của khung GIỮ 'chưa tra'",
    "liquidity_capacity_realism": "na — không đề xuất size cụ thể ngoài sleeve 10–40 tr (8,7% ADV250, chia ≥2 phiên); chiết khấu thanh khoản dùng công thức σ√(Q/ADV), cỡ 5 tỷ tự ghi là ngoài vùng hiệu chỉnh",
    "confirmation_bias_flipflop": "pass có lưu ý — chỉ so các bản của chính SZL trong thư mục DD (không mở sổ vùng giá): tâm r2 ~31,9k → r3 29.257 → r3b 24.529 → r3c 25.165, tức −21% trên CÙNG một bộ BCTC, toàn do đổi phương pháp (A: RONIC=Ke −3.733; B: KTPL), không có thông tin mới. A có căn cứ (ROIC5Y 13,7% ≈ Ke theo ADDENDUM_5F). Nhưng các vòng chỉ sửa những gì skeptic chỉ ra; hai lựa chọn kéo tâm xuống (166,9; ký quỹ theo mệnh giá) chưa từng được biện minh",
    "exit_discipline_gap": "na — không phải deal fear-buy; dù vậy đã có mốc hai chiều kèm ngưỡng số và HARD ABANDON (a)(b)(c)",
    "missing_items": "fail (không định lượng được) — (1) ý kiến kiểm toán FY2025 không được nêu; (2) tiền thuê đất hằng năm có thể tăng theo bảng giá đất mới (Luật Đất đai 2024): khoản trích 44,3 tỷ là dấu hiệu, chưa xét tác động lặp lại lên N0, và nếu 44,3 đã ghi chi phí trong 9T thì N0 ×4/3 nhân cả khoản một lần (hai chiều); (3) cam kết capex Long Phước ~513 còn lại không có NQ HĐQT/ĐHĐCĐ, chỉ có báo chí; (4) capex tuân thủ môi trường KCN (xử lý nước thải) không đề cập; (5) mốc 2053 chỉ có căn cứ cho phần đất cho thuê 2004–08 (TM17), chưa đối chiếu giấy phép; (6) giao dịch bên liên quan (vay BLQ 23,9, trả trước NB 72,6, trả trước Bình Thuận) nêu ở r2 nhưng không định lượng trong mô hình. Có làm: số cổ phiếu (pass), quỹ KTPL (pass), DT chưa thực hiện 762 qua trục phi tiền mặt (pass)"
  },
  "independent_verification": "BQ tav2_bq.ticker_financial: NP SZL 2026Q1–Q3 = 32,12+30,57+69,90 = 132,59 (khớp NP_9M 132,589); LNST 2025 = 26,43+34,23+32,75+47,28 = 140,69 (khớp mẫu số KTPL 140,687 ⇒ k 11,215%); Cash_P0 171,22, StDebt 110,03, LtDebt 196,34, OShares 48,198884 tr khớp. Tính tay tâm tại tham số trung tâm: lõi ≈ 746 + cổ phần 428,0 + chưa niêm yết 113,25 + XDCB 407,0 − nợ ngoài vay 225,6 − nợ ròng 205,5 ≈ 1.263 tỷ ⇒ 26.208 đ trước CK ⇒ ≈ 25.128 sau CK 4,12%, so với 25.165 báo cáo (chênh do 1/r lồi trên lưới) — KHỚP.",
  "killer_objection": "Base đối xử bất nhất giữa các tài sản mới: XDCB 407 cộng theo giá vốn còn BĐS đầu tư mới 166,9 thì loại, và ký quỹ DH trừ theo mệnh giá thay vì PV. Riêng hai lựa chọn này đã lệch tâm tới +6.147 đ (~24%) mà không có căn cứ. Phía ngược lại, N0 neo ở biên đỉnh chu kỳ. Tâm 25.165 vì thế là kết quả của các lựa chọn chưa được biện minh theo cả hai hướng, chưa phải ước lượng trung tính.",
  "recommended_followups": [
    "Đọc TM BĐS đầu tư (mã 241) từ src PDF trong git fc5bd02d9: 166,9 là chuyển từ XDCB hay mua mới, đưa vào khai thác tháng nào, đã cho thuê/đóng góp bao nhiêu vào LN 9T ⇒ quyết định cộng bao nhiêu phần vào base",
    "Nêu căn cứ cho việc trừ ký quỹ DH theo mệnh giá (điều khoản hoàn trả/chấm dứt sớm), nếu không có thì dùng PV làm base",
    "Chuẩn hoá N0 theo biên trung bình chu kỳ (33,6%) làm kịch bản có trọng số thay vì neo đỉnh 9T",
    "Xác định khoản trích thuê đất 44,3 đã ghi chi phí trong 9T/2026 hay lũy kế các năm trước, và thuê đất hằng năm có bị điều chỉnh theo bảng giá mới không",
    "Ghi ý kiến kiểm toán FY2025 (BCTC kiểm toán 2025) và tìm NQ HĐQT/ĐHĐCĐ về tổng mức đầu tư Long Phước",
    "Khôi phục src/ + assumptions_r3c.json từ git (hoặc sửa lệnh tái lập trỏ vào commit) để LOCK md5 kiểm được",
    "Tra lại pháp lý SNZ/Đồng Nai sau 05/11"
  ],
  "summary": "Số BCTC chịu lực của r3c khớp BQ, và tính tay tâm ra ≈25.128 so với 25.165 báo cáo, tức mô hình chạy đúng như mô tả; lỗi khung KTPL của r3b đã được sửa đúng. Tuy vậy, khi soi hai chiều, base còn những lựa chọn không nhất quán và chưa có căn cứ: loại BĐS đầu tư mới 166,9 tỷ trong khi XDCB được cộng theo giá vốn (+13%), và trừ ký quỹ dài hạn theo mệnh giá (+11%), cả hai đều đẩy tâm xuống. Ngược lại, N0 neo ở biên đỉnh chu kỳ, đẩy tâm lên. Các mục thiếu: ý kiến kiểm toán FY2025, rủi ro tiền thuê đất hằng năm tăng, nguồn của cam kết capex Long Phước (chỉ báo chí), và capex môi trường. File nguồn đã bị TRIM khỏi cây làm việc nên chưa tái lập được. Chưa đủ để CONFIRMED; cần giải quyết khoản 166,9 và ký quỹ trước khi dùng tâm này."
}
<<<END_VERDICT>>>