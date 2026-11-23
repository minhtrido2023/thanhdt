**Kết luận: CONFIRMED, độ tin cậy trung bình.** r4 đã sửa được lỗi chính mà skeptic r2 chỉ ra. Tôi tự tính lại tâm kịch bản CƠ SỞ và ra **13.393 đ/cp, khớp đúng output model**. Các số BCTC 2025 then chốt cũng khớp bản EY gốc. Các lỗ hổng còn lại đều nhỏ hơn 5% tâm và nằm ở cả hai chiều. Giá 16.550 trong báo cáo tôi đã bỏ qua khi chấm.

**Đã tự kiểm lại:**
- **Mô hình CƠ SỞ, tính tay:**
  - BV đầu kỳ = 46.857 + 1.700 + 9.360 = 57.917.
  - RI 2027 = −695, PV −612. RI 2028 = 0. RI 2029 = 443, PV 303.
  - TV = 0,006 × 84.230 / 0,135 = 3.744, PV 2.560.
  - (60.168 − 9.360) / 1,0133 / 3.744 = **13.393**, khớp.
- **ROE 2026E:** (4.414 + 1.700) / 42.446 = 14,40%, khớp.
- **Số trong BCTN gốc** (`src/bctn_2025.txt`):
  - Lãi phải thu tín dụng 6.802.719 / 3.272.745 (dòng 11409–10).
  - Lãi phải thu chứng khoán 2.179.948 / 1.208.103 (dòng 11405–06).
  - Thu nhập lãi ghi nhận 21.601.251, thực thu 16.497.163, tức 76% (dòng 8431, 8628).
  - Đều khớp báo cáo.
- **Số cổ phiếu:** 3.120 tr CP tại 31/12/25 (BCTN dòng 6755). Cộng thưởng 20% (GDKHQ 28/08) ra 3.744 tr. EPS Q3 ngầm định ~3.748 tr. Khớp.
- **Quỹ khen thưởng phúc lợi:** chỉ 25,8 tỷ. Thay đổi VCSH 2025 đúng bằng LNST, nên payout 0 hợp lệ.
- **Cho vay bên liên quan:** TM 42 ghi 142,6 tỷ, khớp.

**Chỗ yếu, chiều làm tâm ĐẮT quá:**
- **Khoản đặt cọc thuê văn phòng 3.300 tỷ** (notes_read dòng 44; khoảng 7,8% VCSH 2025) có trong bảng nhưng không được phân tích. Bên nhận cọc không có tên trong TM 42. Nếu mất toàn bộ thì tâm giảm khoảng 5,4%; mất 25% thì giảm khoảng 1,4%.
- **Cho vay xây dựng +36,7% từ đầu năm (27.074 tỷ)**: r2 ghi "chưa kiểm", r4 bỏ hẳn mục này, không còn trong danh sách không kiểm chứng được.
- **Trục haircut lãi dự thu bỏ sót hai khoản:** lãi phải thu phái sinh (283 → 865) và phí phải thu (107 → 308). Ảnh hưởng khoảng −0,2%.
- **Terminal RI giữ chênh lệch ROE − Ke mãi mãi, không giảm dần**, dù moat là NONE. Phần terminal chiếm khoảng 5% giá trị kịch bản CƠ SỞ; nếu cho giảm dần thì tâm giảm khoảng 2–3%. Luật fleet cho phép làm vậy nên tôi không tính là lỗi.

**Chiều làm tâm RẺ quá:**
- **Ke 13,5%** cao hơn dải nội địa do chính báo cáo nêu: Ke 12,3% cho +16,3%; Ke 13,4% cho +1,2%. Đây là quyết định theo luật, không phải lỗi của mô hình.
- **Mức lãi dự thu "bình thường" lấy theo đúng một năm 2024 (1,85%)**, trong khi cho vay trung dài hạn +22% có thể giải thích một phần mức tăng. Trục haircut kỳ vọng làm tâm giảm khoảng 1,2%, nên có thể đang hơi khắt khe.

**Nguồn còn thiếu:** PDF BCTC Q3/2026 và 6T/2026 vẫn không có trong `src/`. LC 9.229 và phải thu khác 18.501 chỉ có một nguồn duy nhất là `notes_read.md`. Giá quyền mua 10.000 cũng chỉ từ một nguồn thứ cấp (vnba), dù ảnh hưởng tới tâm nhỏ (khoảng 0,7%).

<<<VERDICT_JSON>>>
{
  "case_topic": "MSB — DD r4 (RI ngân hàng, tâm 13.042 đ/cp con quyền sau CK; P10 9.144 / P90 17.062)",
  "mode": "DD_GENERAL",
  "verdict": "CONFIRMED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không nêu claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — pháp lý không WARNING (kế thừa r2); TM 42 không thấy giao dịch bên liên quan trọng yếu (cho vay 142,6 tỷ; nhóm ROX < 0,1 tỷ). Caveat: thanh tra NHNN gần nhất không kiểm chứng được",
    "optimistic_comp_sotp_bias": "pass — không dùng comp/SOTP; RI thuần. Tính tay CƠ SỞ = 13.393, khớp model. Hai chiều: terminal không fade spread (ĐẮT ~2–3% nếu fade, luật fleet cho phép); Ke 13,5% cao hơn dải 12,3–13,4% (RẺ, tới +16%, theo luật V1)",
    "data_provenance": "pass (có caveat) — FY2025 đối chiếu BCTN gốc: lãi phải thu TD 6.802.719/3.272.745, CK 2.179.948/1.208.103, TN lãi 21.601.251 vs thực thu 16.497.163, 3.120 tr CP + thưởng 20% = 3.744; tất cả khớp. Q3/6T (LC 9.229, phải thu khác 18.501) chỉ một nguồn notes_read do PDF gốc thiếu; giá quyền mua 10.000 chỉ một nguồn thứ cấp (ảnh hưởng ~0,7%)",
    "liquidity_capacity_realism": "na — sizing đề xuất 0% discretionary; ADV250 96 tỷ so với 5 tỷ không ràng buộc",
    "confirmation_bias_flipflop": "pass — r2 13.018 → r3 14.621 → r4 13.042. Mỗi lần đổi đều do skeptic chỉ ra lỗi có nguồn BCTC (quy ước ROE đầu kỳ; ROE nền chưa làm sạch lãi dự thu). Khoá r4 lập sau khi đã thấy giá nhưng tâm dịch XA giá, không về phía giá",
    "exit_discipline_gap": "na — không có claim vào lệnh; bảng mốc ↑/↓ hai chiều có ngưỡng định lượng (mục 6)",
    "missing_items": "pass (có caveat) — Đã có: CAR 11,67%/cấp 1 11,87%, NPL 2,70%, nhóm 2 +66% YTD, bao phủ 47%, LDR, CASA, room tín dụng, TPDN 4,6% VCSH, bên liên quan, kiểm toán EY FY2025 chấp nhận toàn phần, số CP + quyền mua, quỹ KTPL 25,8 tỷ (không trọng yếu). Thiếu: (1) đặt cọc thuê văn phòng ~3.300 tỷ không xác định bên nhận cọc, không có trong TM 42 (mất 25% ⇒ −1,4%; mất toàn bộ ⇒ −5,4%, xác suất thấp); (2) cho vay xây dựng +36,7% YTD (27.074 tỷ) bị bỏ khỏi danh sách chưa kiểm mà không giải thích (stress hợp lý ~−1%); (3) lãi phải thu phái sinh 283→865 và phí 107→308 không vào trục haircut (~−0,2%); (4) ESOP 2026 ≤ −1%. Không hạng mục nào định lượng được vượt 5% tâm"
  },
  "independent_verification": "Tự tính lại giá trị kịch bản CƠ SỞ từ assumptions_r4.json (md5 f39391ea… khớp): 13.393 đ/cp, khớp output model. ROE 2026E 14,40% khớp. Năm số FY2025 then chốt khớp BCTN EY gốc (src/bctn_2025.txt dòng 8431, 8628, 11405–11410). Số CP 3.120 tr (31/12/25) × 1,2 = 3.744 khớp EPS Q3 ngầm định ~3.748",
  "killer_objection": "Khoản đặt cọc thuê văn phòng ~3.300 tỷ (≈7,8% VCSH 2025) là tài sản không sinh lãi, không xác định bên nhận cọc và không có trong thuyết minh bên liên quan; báo cáo liệt kê nhưng không phân tích. Nếu đối tác là bên có liên hệ cổ đông lớn hoặc khó thu hồi, tâm có thể giảm tới ~5% — ngoài các trục rủi ro đã mô hình hoá",
  "recommended_followups": [
    "Tra thuyết minh 15.1 / BCTC 6T về đối tác và hợp đồng của khoản đặt cọc thuê văn phòng ~3.300 tỷ (bên nhận cọc, kỳ hạn, có phải bên liên quan không)",
    "Đưa cho vay xây dựng +36,7% YTD trở lại danh sách chưa kiểm hoặc kèm một phép thử độ nhạy",
    "Tải lại PDF BCTC Q3/2026 và 6T/2026 (cần user/Mike cho phép gọi AJAX hoặc tải tay) để có nguồn thứ hai cho LC 9.229 / phải thu khác 18.501",
    "Cộng lãi phải thu phái sinh và phí phải thu vào trục haircut lãi dự thu cho đầy đủ",
    "Xác nhận giá quyền mua 10.000 và ngày chốt quyền từ nguồn chính thức (NQ HĐQT/UBCK)"
  ],
  "summary": "r4 sửa đúng lỗi chính của skeptic r2: ROE nền neo vào mức 2026E quan sát 14,4% trừ 0,3pp làm sạch lãi dự thu, bỏ giả định hồi phục, và thêm lãi phải thu chứng khoán 388 tỷ vào trục haircut. Tôi tính tay giá trị CƠ SỞ ra 13.393, khớp đúng model; các số FY2025 then chốt và số cổ phiếu khớp BCTC EY gốc. Chiều ĐẮT còn một số hạng mục chưa xét: đặt cọc thuê văn phòng ~3.300 tỷ không rõ đối tác, cho vay xây dựng bị bỏ khỏi danh sách chưa kiểm, lãi phải thu phái sinh/phí không vào trục, terminal không giảm dần. Chiều RẺ: Ke 13,5% cao hơn dải nội địa và mốc lãi dự thu 2024 có thể khắt khe. Không hạng mục định lượng được nào vượt 5% tâm, và hai chiều bù trừ một phần, nên vùng 9.100–17.100, tâm ~13.000 (con quyền) đứng vững. Còn hai caveat nguồn: PDF Q3/6T gốc thiếu, và khoản cọc văn phòng cần tra."
}
<<<END_VERDICT>>>