**Verdict: CONFIRMED, độ tin cậy trung bình.** Tâm 21.338 tái lập được đúng từng đồng. Không có hạng mục thiếu nào kéo tâm quá 5%. Hai lỗi cần ghi lại: (a) quỹ khen thưởng phúc lợi (KTPL) bị bỏ sót, làm tâm cao hơn khoảng 1,8–4,4%; (b) câu "vốn tăng thêm sinh lời = Ke" ở §3 sai so với code. Nếu áp đúng câu đó, tâm cao hơn 7,7%.

**Đã tự kiểm**
- Khôi phục `calc_r3` từ `14ad1c925^` vào `/tmp/skep_hpg_t6jV` và chạy lại `calc_recheck.py`. Mọi assert đều qua, bảng độ nhạy r ở §2 khớp đủ 7 dòng.
- Vốn chủ của cổ đông công ty mẹ (BV0) = VCSH 149.568,4 − cổ đông không kiểm soát 772,9 = 148.795,5 tỷ, khớp `notes_bs.md:23`.
- Số cổ phiếu = vốn điều lệ 84.429,6 tỷ / 10.000 = 8.442,96 triệu cp, khớp VI.17c.
- Không chạy truy vấn BigQuery nào. Hai số trên đối chiếu với bản ghi chép BCTC trong `notes_bs.md`.

**Các biến thể tôi chạy trên mô hình r3**

| Kiểm | Tâm | Δ |
|---|---|---|
| Phần vốn giữ lại vượt cam kết sinh lời = Ke (đúng như câu D4 ở §3) | 22.971 | **+7,7%** |
| Quỹ KTPL 2,1% LNST (tỷ lệ 2025: 331,7/15.515 tỷ) | 20.944 | −1,8% |
| Quỹ KTPL ở mức trần 5% (NQ ĐHĐCĐ 2026) | 20.400 | −4,4% |
| ETR thép 6,5% thay 12% trong TAXF | 20.878 | −2,2% |
| Toàn bộ cam kết vốn + XDCB không sinh lời (biến thể I của r3, dùng làm cận trên cho capex môi trường D3) | 20.456 | −4,1% |

- **Chiều đắt:** cộng dồn mọi hạng mục, kể cả bản J −665 và đếm trùng cam kết vốn −200, ra khoảng −1,7k (−8%).
- **Chiều rẻ:** r base 13,5% nằm *ngoài* dải Ke 12,3–13,4%. Chỉ riêng việc này đã khoảng +0,8%, lấy giữa dải thì khoảng +5,6%. Cộng thêm +7,7% từ câu D4.
- Hai chiều xấp xỉ cân nhau, nên tôi không bác tâm.
- Theo ràng buộc mù, tôi bỏ qua giá 21.200 có trong báo cáo và không mở sổ vùng giá. Kiểm flip-flop vì vậy chỉ dựa trên bridge r2→r3.

<<<VERDICT_JSON>>>
{
  "case_topic": "HPG — DD recheck 25/11/2026 (B5+E15/E16) của REPORT_r3, tâm 21.338 đ/cp",
  "verdict": "CONFIRMED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không nêu luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — đã liệt kê WARNING: hệ Đại Quang Minh–TLSH 25,13%, tiền gửi cầm cố 8.294 tỷ, ưu đãi thuế DQ2 (CV 377), các QĐ AD; web_tlsh_governance.md không thấy xử phạt/khởi tố 2025–26. Lưu ý báo cáo tự ghi 'chưa quét pháp lý sau 08/11'.",
    "optimistic_comp_sotp_bias": "pass — RI một mô hình, không dựa comp; TLSH theo sổ (bản E trục r2 cho 21.144, −0,9%). Chênh dài hạn ROE_T−r trên vốn hiện hữu không fade nhưng đối xứng: XẤU 10,36% < r cũng giữ vĩnh viễn, ước tính ròng ≈ +2–3%.",
    "data_provenance": "pass — BV0 148.795,5 = VCSH 149.568,4 − CĐKS 772,9 (notes_bs.md:23); SH 8.442,96 tr = VĐL 84.429,6/10.000 (VI.17c); cam kết vốn 19.472 ghi rõ là số 30/06 (TM41); LN lõi 9T ≈19.200 đã bóc lãi chuyển nhượng 4.929. Đường LN v3 kế thừa, không đổi.",
    "liquidity_capacity_realism": "na — sizing 3% NAV chỉ áp khi giá dưới ngưỡng luật 4; không có lệnh cụ thể. ADV 589 tỷ thì 5 tỷ ≈0,85%/ngày, khả thi.",
    "confirmation_bias_flipflop": "pass (giới hạn) — theo ràng buộc mù, không mở kb/dd_price_zones.json. Tâm r3→recheck đổi 0%. Bước nhảy r2→r3 +31% (16.286→21.338) có bridge từng bước C1–C4, xuất phát từ sửa lỗi do skeptic 08/11 nêu, không phải đọc lại cùng dữ kiện theo hướng thuận hơn.",
    "exit_discipline_gap": "na — không phải luận điểm fear-buy; có ngưỡng luật 4 (18.137) và trần sizing 3%",
    "missing_items": "fail (dưới ngưỡng trọng yếu) — (1) quỹ KTPL/thưởng BĐH trích từ LNST không có trong mô hình: 2025 = 331,7 tỷ ≈2,1% LNST ⇒ −394 đ/cp (−1,8%); trần 5% theo NQ 2026 ⇒ −938 (−4,4%). (2) capex tuân thủ môi trường D3 chưa định lượng; cận trên bằng biến thể I (cam kết + XDCB lợi suất 0) = −4,1% < 5%. (3) hình thức cổ tức 2026 15% chưa công bố: nếu trả bằng cổ phiếu thì phải điều chỉnh cơ sở số cổ phiếu khi gắn nhãn. Các mục pass: lợi ích CĐKS (BV0 và LN là phần mẹ), số cổ phiếu tại 30/09, KT25 + soát xét 6T, one-off đã bóc, giao dịch liên quan/TLSH đã WARNING, không ESOP/phát hành riêng lẻ trong 9T.",
    "symmetry": "{too_high_checked: 8, too_low_checked: 9, too_low_items: ['r base 13,5% nằm ngoài dải Ke 12,3–13,4% (đầu trên +0,8%, giữa dải ≈+5,6%)', 'vốn giữ lại vượt cam kết sinh lời 5,92% vĩnh viễn, trái câu D4 ở §3 (= Ke ⇒ +7,7%)', 'nhánh XẤU giữ chênh âm vĩnh viễn, không mean-revert', 'ETR hiện hành giữ 2030–34 (bản C +3,7%)', 'g_RI kiểu r2 (bản D +5,6%, loại có lý do)', 'TLSH theo sổ, không có upside trên sổ', 'đường XẤU 16.000 so run-rate lõi ~25.600', 'trọng số kịch bản 25/50/25', 'lãi tiền gửi sau thuế so với chi phí nợ được trả bớt (nợ ròng 59.608 tỷ)']}"
  },
  "independent_verification": "Khôi phục calc_r3 từ git 14ad1c925^, chạy lại calc_recheck.py: CONTROL và mọi assert qua, 7 dòng độ nhạy r khớp đúng §2. BV0 tính lại từ notes_bs.md:23 khớp 148.795,5; SH khớp VI.17c. Không chạy truy vấn BigQuery. Chạy thêm 5 biến thể trên mô hình: Ke-on-excess 22.971, KTPL 2,1% 20.944, KTPL 5% 20.400, ETR 6,5% 20.878; biến thể I 20.456 lấy từ output r3.",
  "killer_objection": "§3 ghi 'vốn tăng thêm sinh lời = Ke (D4)' nhưng code cho phần vốn giữ lại vượt cam kết 19.472 chỉ sinh lời 5,92% mãi mãi trong terminal; áp đúng câu đó thì tâm 22.971 (+7,7%). Chiều ngược lại, KTPL bị bỏ sót và ETR thép 6,5% kéo xuống −1,8…−4,4% và −2,2%. Hai lỗi lệch ngược chiều nên tâm đứng được, nhưng là nhờ bù trừ chứ không phải nhờ mô hình đúng.",
  "recommended_followups": [
    "Sửa câu D4 ở §3 cho khớp code, hoặc chạy và báo song song biến thể 'vốn vượt cam kết = Ke' (22.971) như một cận trên",
    "Thêm hệ số trích KTPL/thưởng BĐH (2,1% lịch sử, trần 5% theo NQ 2026) vào đường LN, hoặc ghi như một biến thể",
    "Giải trình vì sao r base 13,5% nằm ngoài dải Ke 12,3–13,4%, hoặc báo thêm tâm ở giữa dải",
    "Lấy từ BCTN/báo cáo PTBV phần capex môi trường trong cam kết 19.472 (cận trên −4,1% đã định lượng)",
    "Theo dõi hình thức cổ tức 2026 15%: nếu trả bằng cổ phiếu thì điều chỉnh cơ sở số cổ phiếu khi gắn nhãn",
    "Quét pháp lý sau 08/11 (TLSH/BĐS Hòa Phát)"
  ],
  "summary": "Bản recheck không đổi mô hình r3, chỉ đổi r, và bảng độ nhạy tái lập chính xác. BV0 và số cổ phiếu khớp ghi chép BCTC. Kiểm thiếu hạng mục cho thấy quỹ KTPL bị bỏ sót (−1,8% theo tỷ lệ 2025, −4,4% ở trần 5%) và capex môi trường chưa định lượng (cận trên −4,1%); cả hai đều dưới ngưỡng 5%. Chiều rẻ có hai điểm đáng kể: r base nằm ngoài dải Ke, và câu D4 ở §3 mâu thuẫn với code (áp đúng câu đó thì +7,7%). Các sai lệch hai chiều xấp xỉ bù nhau nên tâm 21.338 được giữ, nhưng cần sửa câu D4 và đưa KTPL vào mô hình trước khi dùng tiếp."
}
<<<END_VERDICT>>>