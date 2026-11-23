**Kết luận: REFUTED, độ tin cậy trung bình.** Phần tính toán của mô hình đúng. Con số tâm thì không đứng vững: bước lớn nhất của nó (+4.800, ô O2) mâu thuẫn với chính tài liệu của fleet. Ngoài ra có hai khoản trọng yếu vắng mặt trong mô hình.

**Đã tự kiểm lại**
- Chạy lại `selfcheck_r5.py`: cây 66.470,1 so với đường độc lập 66.475,3, lệch +0,0079%. Khớp, và `model_out_r5.json` khớp báo cáo (từng cây q: 69.581 / 66.057 / 63.772).
- Cước/DT nước ngoài: 22,844 / 487,508 = 4,6858%, khớp hệ số 0,046858. Ảnh gốc `png_q326/p29, p31` không còn trên đĩa nên tôi chỉ kiểm được phép chia, không đối chiếu được ảnh.
- Phép tính chiết khấu khớp: 66.470 × 0,9 = 59.823; 0,85 × 59.823 = 50.850.
- Báo cáo này trùng md5 (`64aa2b2d…`) với bản mà skeptic r1 đã chấm. Tôi tự kiểm lại nguồn chứ không chép kết luận r1, và có một điểm tôi sửa lại r1 (hạn thuê đất, xem dưới).

**Chiều ĐẮT (tâm quá cao)**
1. **Ô (A tắt, B bật) → O2, +4.800.** Lập luận là H1/26 là "quan sát sạch" của trạng thái không có mỏ DGC. Nhưng `A/A1_ore_mine_recovery.md:133` ghi ngày dừng KT25 "không xác định được, trong khoảng ~đầu 2026 đến 17/03". Dòng 143 còn ghi 2026 có khoảng 2,5 tháng tự khai thác. Như vậy H1/26 có lẫn quặng của nguồn A, nên mức O2 bị lệch về phía lạc quan.
   - Bằng chứng "không có kho quặng rẻ" lại dùng tồn kho của **PAT** (#R4). Kho quặng nằm ở DLC, nên số này không chứng minh được điều đó.
   - Gỡ bước này thì tâm còn **62.578 trước / 56.320 sau chiết khấu / cổng ≈ 47.870**, tức −5,9%.
   - Chiều giảm này có cơ sở bằng chứng riêng (A1), không chỉ là "cho thận trọng".
2. **Hạn thuê đất KCN.** Chi phí GPMB đất thuê phân bổ 16 năm (Q3 TM9). Mô hình chạy chuỗi tới 2045 rồi cộng Gordon vĩnh viễn.
   - Skeptic r1 suy ra hạn khoảng 2042.
   - `blind_val_20261114/assumptions_blind.md:69,89,116` lại đặt `lease_end_year: 2034` ("còn ~8 năm", nếu tính từ khoảng 2018).
   - Hạn thuê thật chưa ai kiểm. Nếu là 2034 mà không gia hạn, mất phần lớn giá trị cuối. Đây là khoản trọng yếu nhưng chưa định lượng được.
3. **Capex tuân thủ môi trường vắng mặt.** Vụ án có tội danh ô nhiễm môi trường (điều 235) và cáo buộc đổ thải hàng triệu tấn tại KCN Tằng Loỏng, nơi đặt nhà máy PAT. Mô hình chỉ có capex = khấu hao 45 tỷ, trong khi capex thực chỉ khoảng 3 tỷ/năm và hao mòn luỹ kế đã 62% nguyên giá. Kế hoạch đầu tư 2026: KHÔNG TÌM ĐƯỢC (F1).
4. **Cầm cố.** Độ nhạy −42,6 tỷ cho ra 64.766, tức khoảng 40 đ/cp cho mỗi tỷ. Theo r1, 439/551,6 tỷ tiền gửi kỳ hạn đang bị cầm cố, trong đó 130 tỷ cầm cố ở ACB mà không có dư nợ ACB. Mức độ nhạy hiện tại có thể quá nhẹ.

**Chiều RẺ (tâm quá thấp)**
- Tồn kho dư 44,44 tỷ đã bị gỡ (giữ nguyên thì +1.398). Việc gỡ có cơ sở độc lập: tồn kho nền 31/12/25 bị UHY ngoại trừ. Nhưng tồn kho 30/09 vẫn có thể giải phóng một phần.
- Giả định ΔVLĐ = 0 trong khi vốn lưu động 30/09 cao: r1 ước có thể làm tâm thấp tới khoảng 4.500 đ/cp. Tôi chưa tự đo con số này.
- Khoản 70 tỷ tính theo mệnh giá cho +1.805.

**Tính nhất quán qua các vòng:** việc giải phóng tồn kho đổi qua lại (r2 bỏ → r4 thêm → r5 bỏ). Mọi thay đổi r4 → r5 đều là đọc lại thông tin có từ 14/11; báo cáo tự nhận độ tin cậy thấp.

Kết luận "không có biên an toàn, không mua" của báo cáo không bị lật.

<<<VERDICT_JSON>>>
{
  "case_topic": "PAT — VALUATION_r5 (tâm 66.470 trước CK / 59.823 sau CK / cổng 50.850)",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra lập luận QUALIFY theo fear-buy/§2.5 (ledger_notes tự ghi PAT trượt §2 trụ #2)",
    "scandal_migration_risk": "fail (một phần) — các WARNING về vụ án đã được nêu, nhưng tội danh điều 235 (ô nhiễm, đổ thải hàng triệu tấn tại KCN Tằng Loỏng, A1:26) liên quan trực tiếp tới nơi đặt nhà máy PAT mà mô hình không có chi phí hay capex khắc phục nào; KT25 phụ thuộc giấy phép đến ~hết 2026 (A1:39, nguồn CTCK)",
    "optimistic_comp_sotp_bias": "fail — không dùng comp; nhưng bước +4.800 (ô (A tắt, B bật) → O2) hiệu chỉnh trên H1/26, giai đoạn còn lẫn quặng tự khai thác của A (A1:133,143: KT25 dừng trong khoảng ~đầu 2026 đến 17/03); lý do 'không có kho quặng rẻ' dùng tồn kho PAT trong khi kho quặng ở DLC ⇒ điểm hiệu chỉnh lệch lạc quan; gỡ bước này ⇒ 62.578 / 56.320 (−5,9%)",
    "data_provenance": "fail (nhẹ) — GTGD 1,01/0,60 tỷ, dư tồn kho 39,4, 'UHY ngoại trừ', PAT +1% vs P4 +19,5% đều 'theo dispatch, chưa tự đo' (báo cáo tự ghi); ảnh nguồn png_q326 p29/p31 cho #R1/#R2 không còn trên đĩa (find toàn /home/trido/thanhdt trả rỗng) ⇒ chỉ kiểm được phép chia, không đối chiếu được ảnh",
    "liquidity_capacity_realism": "pass — đã chiết khấu thanh khoản 10%, sizing ≤0,5% NAV, hành động là không mua; số ADV chưa tự đo vòng này",
    "confirmation_bias_flipflop": "fail — chỉ so các vòng r2–r5 trong thư mục rebuttal (không mở dd_price_zones.json theo ràng buộc của brief): tâm r3 66.864 → r4 66.318 → r5 66.470; tồn kho r2 bỏ → r4 thêm → r5 bỏ; ô 50/50 → O2; báo cáo tự nhận mọi thay đổi r4→r5 là đọc lại thông tin có từ 14/11 (#R11)",
    "exit_discipline_gap": "na — không mua, không có tranche; ledger_notes đã nêu HARD ABANDON §3 #4 (chuyển giá DLC) và các mốc theo dõi",
    "missing_items": "fail — (1) hạn thuê đất KCN: GPMB phân bổ 16 năm (Q3 TM9), blind_val đặt lease_end 2034, skeptic r1 ước ~2042, mô hình chạy tới 2045 + Gordon vĩnh viễn; hạn thuê thật chưa kiểm ⇒ trọng yếu, chưa định lượng (nếu 2034 không gia hạn: mất phần lớn TV); (2) capex tuân thủ môi trường/xử lý xỉ (~137kt/năm) + khắc phục đổ thải KCN: vắng, capex=KH 45 trong khi capex thực ~3/năm, HMLK 62% nguyên giá ⇒ chưa định lượng; (3) cầm cố: −42,6 tỷ ≈ −40 đ/cp mỗi tỷ, nhưng 439/551,6 tỷ HTM bị cầm cố (130 tỷ ACB không có dư nợ) ⇒ độ nhạy có thể quá nhẹ (130 tỷ ≈ −5.200, −7,8%); (4) chiều lên: ΔVLĐ=0 bỏ qua VLĐ 30/09 cao (r1 ước tới ~+4.500, tôi chưa tự đo). Đạt: số cổ phiếu 25 triệu (BCTC Q3), quỹ KTPL (×0,94), ý kiến KT FY2025 (ngoại trừ tồn kho) đã có, ưu đãi thuế TNDN hết 2030/2032 đã mô hình hoá, thuế XK 2027 có trong nút TX"
  },
  "independent_verification": "Chạy lại selfcheck_r5.py: cây 66.470,1 vs đường độc lập 66.475,3 (+0,0079%) — KHỚP; model_out_r5.json khớp từng cây q (69.581/66.057/63.772). Tự tính cước 22,844/487,508 = 4,6858% = hệ số 0,046858 — KHỚP (không đối chiếu được ảnh gốc vì file không còn). Phép tính CK: 66.470×0,9 = 59.823; ×0,85 = 50.850 — KHỚP. Đọc A1:133,143 xác nhận Q1/26 còn tự khai thác KT25 ⇒ bác tiền đề 'H1/26 sạch'.",
  "killer_objection": "Bước +4.800 dựa trên tiền đề H1/26 là quan sát thuần của ô (A tắt, B bật). Nhưng A1 của chính fleet ghi KT25 còn khai thác tới khoảng ~đầu 2026 đến 17/03, nên mức O2 có lẫn quặng rẻ tự khai thác. Tâm trung thực gần 62.578 / 56.320 sau CK / cổng ~47.870, và còn có thể thấp hơn nữa nếu hạn thuê đất KCN rơi vào 2034 trong khi mô hình định giá vĩnh viễn.",
  "recommended_followups": [
    "Đưa ô (A tắt, B bật) về 50/50 (62.578), hoặc chỉ hiệu chỉnh O2 trên Q2/26 (sau 17/03, VAPC còn chạy đến đầu 06) thay vì cả H1/26",
    "Truy hợp đồng thuê đất KCN Tằng Loỏng của PAT (ngày bắt đầu, hạn, điều khoản gia hạn và hoàn nguyên); giải quyết mâu thuẫn 2034 (blind_val) vs 2042 (r1)",
    "Định lượng capex/chi phí tuân thủ môi trường cho xỉ P4 và phần PAT trong khắc phục đổ thải KCN",
    "Đối chiếu cầm cố ACB 130 tỷ (không có dư nợ) và khoản 249 tỷ BIDV bảo đảm cho 'đơn vị trong Tập đoàn'; nâng độ nhạy mất cầm cố cho tương xứng",
    "Tự đo lại GTGD 64 phiên và dư tồn kho 39,4 trên BQ thay vì lấy theo dispatch; lưu lại ảnh nguồn p29/p31"
  ],
  "summary": "Phần tính toán của r5 sạch: self-check tái lập được, hệ số cước và phép chiết khấu thanh khoản khớp. Nhưng tâm 66.470 phụ thuộc vào bước +4.800 đọc H1/26 là quan sát 'sạch' không có mỏ DGC, trong khi tài liệu A1 của fleet ghi KT25 còn khai thác tới khoảng ~đầu 2026 đến 17/03 và kho quặng nằm ở DLC chứ không phải PAT. Gỡ bước này thì tâm về 62.578 trước / 56.320 sau chiết khấu (−5,9%). Theo mục thiếu, mô hình định giá vĩnh viễn mà chưa kiểm hạn thuê đất KCN (blind_val đặt 2034, r1 ước 2042), và không có capex tuân thủ môi trường dù vụ án có tội danh đổ thải tại chính KCN. Ở chiều ngược lại, tồn kho dư và ΔVLĐ=0 có thể làm tâm thấp đi vài nghìn đồng, nhưng tồn kho nền đã bị UHY ngoại trừ. Kết luận 'không có biên an toàn, không mua' giữ nguyên; tâm và cổng cần hạ hoặc phải có bằng chứng mới cho ô O2."
}
<<<END_VERDICT>>>