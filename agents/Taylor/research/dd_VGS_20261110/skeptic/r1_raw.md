**Kết luận: INCONCLUSIVE (độ tin cậy medium).** Các con số có trong báo cáo đều đúng. Tôi đối chiếu 14 số với BCTC gốc và khớp hết, tính lại SOTP cũng ra đúng. Nhưng báo cáo thiếu mấy khoản mà một chuyên viên ngành sẽ đòi. Những khoản thiếu gần như đều kéo tâm xuống, và khoản lớn nhất là Legend City thì không lượng hoá được.

**Đã kiểm độc lập.** BCTC gốc không còn trên đĩa vì đợt dọn thư mục ngày 19/11 đã xoá `src/` và `png/`. Tôi khôi phục từ commit backup `f154632f2`; md5 file `BCTC-Q3-HN.pdf` khớp `e30e74ce…`.
- **Bảng cân đối 30/09:** vay 1.201,6; tiền 71,65; HTM 1.096,6; liên kết 255,72; VCSH công ty mẹ 1.433,34; 61.524.155 cổ phiếu; XDCB Legend City 891,55; phải trả Vinaconex 498,74. Tất cả khớp.
- **KQKD 2024/2025:** phần lãi liên kết 10,90 và 43,56 khớp. TM23/25 (sản phẩm 5.383,8, giá vốn 5.099,2; hàng hoá 852,6, giá vốn 846,3) khớp.
- **Tính lại:** LN lõi cơ sở 129,36 tỷ ⇒ 15.575 đ/cp; EPV liên kết 421,6 tỷ ⇒ **1,65 lần sổ sách**; nợ ròng −542 đ/cp. Khớp với báo cáo.

**Chiều làm tâm QUÁ CAO (khoản thiếu, đều là ước lượng):**
1. **Legend City — thiếu tổng mức đầu tư, tiền sử dụng đất và hạn tiến độ.** ĐHĐCĐ 2026 (Điều 8) vừa duyệt kế hoạch 2026 và điều chỉnh chủ trương đầu tư, nhưng tờ trình 05 chưa lấy được. TM22 không nêu cam kết vốn nào. Luật NPV = 0 giả định mọi đồng vốn chi tiếp đều sinh lời đúng bằng Ke, trong khi một phần là nhà ở thu nhập thấp có thể bị trần lợi nhuận. Không lượng hoá được nhưng trọng yếu, và đây là lý do chính cho nhãn INCONCLUSIVE.
2. **Nhà máy ống đã khấu hao 82%** (nguyên giá 484,8, khấu hao luỹ kế 396,9; khấu hao 9 tháng chỉ 9,1 tỷ). EPV với g = 0 ngầm coi vốn duy trì bằng khấu hao. Nhu cầu thay thế thật có thể làm tâm giảm khoảng 8% (ước lượng).
2. **Quỹ khen thưởng phúc lợi không trừ.** EPS 2025 là 3.432, trong khi LNST/số cổ phiếu là 3.527: chênh ≈ 5,9 tỷ (2024 ≈ 6,6 tỷ). LNST chưa phân phối 2025 thấp hơn LNST 9,18 tỷ. Ảnh hưởng ≈ −2,3…−3,5% tâm.
4. **Thuê đất đến 2051** (công ty mẹ và công ty con) nằm trong chân trời EPV vô hạn: ≈ −2,4% tâm.
5. **Dòng "Các khoản dự phòng" −21,09 tỷ** trong lưu chuyển tiền tệ chưa được giải thích là hoàn nhập vào lãi lỗ hay đã sử dụng. Nếu là hoàn nhập thì biên gộp TTM thực chỉ 4,05%, không phải 4,31%: kịch bản tốt giảm khoảng −1,8%, và luận điểm "biên cải thiện" yếu đi.
6. **Liên kết được định giá 1,65 lần sổ** mà không có BCTC liên kết. TTM chồng FY25 một quý, nên Q4/25 bị đếm hai lần. Lõi VGS bị chấm moat NONE, nhưng liên kết lại được ngầm giả định ROE khoảng 22% mãi mãi. Hai cách đối xử không nhất quán.

**Chiều làm tâm QUÁ THẤP:**
- GPM cơ sở 3,6% là trung vị 10 năm, khi tỷ trọng hàng thương mại (biên ≈ 0,7%) còn cao. Mảng tự sản xuất đang ổn định ở 5,29%, nên biên cấu trúc có thể cao hơn.
- Khoản ứng trước Vinaconex 38 tỷ không có trong SOTP: khoảng +2%.
- Cách đọc (b) của W2 (cổ tức liên kết 2025 đã trình bày ròng): +535 đ.

Cộng các khoản lượng hoá được: chiều xuống khoảng −14…−16% (ước lượng), chiều lên khoảng +2…+5%. Không khoản đơn lẻ nào được đo chắc vượt 5%, nên tôi không kết luận REFUTED.

Tôi không xem giá thị trường. Các số giá, luật 4 và nhãn vùng trong báo cáo đều bị bỏ qua khi chấm.

<<<VERDICT_JSON>>>
{
  "case_topic": "VGS (CTCP Ống thép Việt-Đức VG PIPE) — DD r2 10/11/2026, SOTP tâm 26.778 đ/cp trước CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — không thấy WARNING pháp lý/quản lý nhà nước nào bị bỏ qua; báo cáo tự nêu W1 (cả BKS từ nhiệm 15/09/2025), W3/W7 (đối tác hai chiều Điện Xanh/Vinaconex), W4 (bên liên quan không kê giao dịch với liên kết); chưa có tín hiệu pháp nhân/tài sản lõi bị tác động",
    "optimistic_comp_sotp_bias": "fail (đã công bố nhưng không vào tâm) — liên kết 28,6% không công bố BCTC được định giá cơ sở 421,6 tỷ = 1,65× sổ 255,7 (ROE vĩnh viễn ngầm định ≈22%) trong khi lõi VGS bị chấm moat NONE; TB3 chồng Q4/25 hai lần (≈ −576 đ ở trọng số cơ sở, ước lượng, không chỉnh); kịch bản tốt TTM×5 là bội số tự đặt, không có comp. Độ nhạy −5…−12,7% có công bố nhưng tâm không đổi",
    "data_provenance": "pass có điều kiện — 14 số then chốt khớp BCTC gốc (khôi phục từ git f154632f2, md5 khớp); nhưng src/, png/, LOCK_*, model_out_r2.json đã bị xoá khỏi đĩa ngày 19/11 (commit 30ca17444), chỉ còn trong git; vài dữ kiện vẫn 'theo skeptic, chưa tự kiểm' (nền W3 01/01/2025, Vinaconex là nhà thầu, LCTT FY25 mã 27) — không mang tải định giá",
    "liquidity_capacity_realism": "na — bị ràng buộc mù giá/không tra ADV; ghi chú: mức báo cáo tự đề xuất ≤0,5 tỷ/phiên = 22% ADV60 của chính nó, cao hơn mức 10% ADV thông thường",
    "confirmation_bias_flipflop": "pass (phạm vi hẹp) — không mở dd_price_zones.json theo ràng buộc; so r1→r2 trong cùng thư mục: 27.090→26.778, thay đổi do áp 9 đính chính của skeptic trên CÙNG thông tin, theo chiều thận trọng, không phải lật kết luận để có YES",
    "exit_discipline_gap": "pass — §8 có M1–M7 hai chiều, có ngưỡng và hạn; claim fear-buy/abandon theo §3 không áp dụng",
    "missing_items": "fail — (1) Legend City: thiếu tổng mức đầu tư/vốn còn phải chi (ĐHĐCĐ 2026 Điều 8 vừa điều chỉnh chủ trương đầu tư, tờ trình 05 chưa lấy), tình trạng tiền sử dụng đất, hạn tiến độ dự án ⇒ KHÔNG lượng hoá được nhưng trọng yếu; (2) TSCĐ hữu hình khấu hao 82% (NG 484,8 / HMLK 396,9; khấu hao 9T 9,1 tỷ) — EPV coi vốn duy trì = khấu hao, ≈ −8% tâm (ước lượng); (3) quỹ khen thưởng phúc lợi: EPS FY25 3.432 so với LNST/CP 3.527 ⇒ ≈5,9 tỷ/năm (FY24 6,6), không mô hình hoá ⇒ ≈ −2,3…−3,5% tâm; (4) thuê đất đến 2051 (mẹ 55.056 m², con 20.000 m²) trong chân trời vô hạn ⇒ ≈ −2,4% lõi-tâm (ước lượng); (5) một lần trong năm gốc: 'Các khoản dự phòng' −21,09 tỷ ở LCTT 9T chưa rõ là hoàn nhập vào lãi lỗ ⇒ nếu đúng là hoàn nhập thì GPM TTM 4,05% chứ không phải 4,31%, kịch bản tốt ≈ −1,8% tâm. Đã có: số CP 61.524.155 (vốn góp 615,24 tỷ, không đổi), ý kiến kiểm toán FY25 chấp nhận toàn phần, bên liên quan có cờ W4. Chiều lên bị bỏ sót: ứng trước Vinaconex 38,0 tỷ (≈ +2%)"
  },
  "independent_verification": "Khôi phục BCTC gốc từ git f154632f2 (md5 BCTC-Q3-HN khớp e30e74ce…). Tại 30/09/2026 khớp: vay 1.201,601; tiền 71,653; HTM 1.096,6; liên kết 255,723; VCSH công ty mẹ 1.433,341 (tổng 1.433,519 − lợi ích CĐ không kiểm soát 0,179); vốn góp 615,24 tỷ = 61.524.155 CP; XDCB Legend City 891,547; phải trả Vinaconex 498,739. KQKD FY25 khớp: phần lãi liên kết 2024 10,896 và 2025 43,559. TM23/25 khớp: sản phẩm DT 5.383,8 / giá vốn 5.099,2; hàng hoá 852,6 / 846,3. Tính lại: LN lõi cơ sở 129,36 ⇒ 15.575 đ/cp; liên kết TTM 116,30, TB3 56,92 ⇒ EPV 421,6 tỷ; nợ ròng −542 đ/cp — tất cả khớp báo cáo.",
  "killer_objection": "Legend City (≈6.524 đ/cp, ~24% tâm) được định giá theo luật NPV=0 trong khi chính ĐHĐCĐ 2026 vừa duyệt điều chỉnh chủ trương đầu tư mà báo cáo chưa đọc được tờ trình; không có tổng mức đầu tư, tiền sử dụng đất hay hạn tiến độ. Với mục tiêu một phần là nhà ở thu nhập thấp (có thể bị trần lợi nhuận), mỗi đồng vốn chi tiếp có thể có NPV âm — kịch bản ×0,7 chỉ phạt vốn đã chi, không phạt cam kết tương lai.",
  "recommended_followups": [
    "Lấy Tờ trình 05/2026/TT-ĐHĐCĐ-VGP (Legend City: tổng mức đầu tư, tiến độ, phần nhà ở thu nhập thấp/thương mại) và Tờ trình 02/2026 (trích quỹ từ LNST 2025)",
    "Xác minh tình trạng tiền sử dụng đất của các QĐ giao đất 1829/2020, 2954/2021, 341/2024 (đã nộp, đã xác định giá hay còn treo)",
    "Đọc thuyết minh dự phòng phải trả (31,4 → 10,0) để biết −21,1 tỷ là hoàn nhập vào lãi lỗ hay đã sử dụng; nếu hoàn nhập, hạ GPM kịch bản tốt về ≈4,05%",
    "Ước lượng vốn duy trì nhà máy ống (TSCĐ khấu hao 82%) và trừ vào EPV lõi; trừ quỹ khen thưởng phúc lợi ≈2,7–4,2% LNST khỏi lợi nhuận thuộc cổ đông",
    "Bổ sung chiều lên: cộng ứng trước Vinaconex 38,0 tỷ nếu không phải chi phí dự án; xét GPM cấu trúc khi tỷ trọng hàng thương mại giảm",
    "Khôi phục src/ và calc/ về thư mục DD (hoặc ghi rõ con trỏ git) để lần soát sau truy được nguồn mà không cần khôi phục thủ công"
  ],
  "summary": "Dữ kiện trong báo cáo VGS chính xác: 14 số then chốt khớp BCTC gốc khôi phục từ git, tính lại SOTP ra đúng. Nhưng theo checklist khoản thiếu, mô hình bỏ qua cam kết vốn tương lai và tiền sử dụng đất của Legend City (ĐHĐCĐ 2026 vừa điều chỉnh chủ trương đầu tư, tờ trình không có trong hồ sơ), nhu cầu thay thế tài sản của nhà máy đã khấu hao 82%, quỹ khen thưởng phúc lợi (≈5,9 tỷ/năm), thuê đất hết hạn 2051, và một khoản dự phòng −21,1 tỷ chưa rõ có phải lãi một lần không. Cộng lại, chiều xuống ước khoảng −14…−16% so với chiều lên khoảng +2…+5% (ứng trước Vinaconex, biên cấu trúc khi tỷ trọng hàng thương mại giảm, cách đọc W2-b). Liên kết được định giá 1,65 lần sổ mà không có BCTC, không nhất quán với nhãn moat NONE của lõi. Không khoản đơn lẻ nào đo chắc vượt 5% nên không kết luận REFUTED; khoản lớn nhất (cam kết Legend City) không lượng hoá được ⇒ INCONCLUSIVE cho đến khi có tờ trình 05/2026 và tình trạng tiền sử dụng đất."
}
<<<END_VERDICT>>>