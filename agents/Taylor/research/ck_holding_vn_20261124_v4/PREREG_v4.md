# PRE-REGISTRATION — CK holding VN v4 (job Taylor_20261124_053704)

Viết TRƯỚC khi chạy calc v4 (chưa có số v4 nào). Đã biết: toàn bộ số v3 + ước lượng của skeptic v3 (OCH sửa ⇒ đầu trên ≈14%).
Đã đọc dữ liệu đầu vào (cap_events_v4, KBS cổ đông lớn mới, shares_pit GLT/SZL) để viết quy tắc — KHÔNG chạy calc.
Khoá md5 ở PREREG_v4_md5.txt + LOCK_md5.txt. Không sửa sau khi chạy. Code diễn giải khác chữ file này ⇒ ghi vào mục
"Khác PREREG" của report, không im lặng.

## A. Sửa (quy tắc chung, không vá riêng mã)
F1. **Pha loãng do phát hành cho người khác** (PP, Rights; PUBL thêm vào — cùng cơ chế, ghi là mở rộng ngoài chữ dispatch).
  Nguồn `inputs/cap_events_v4.csv` (tav2_bq.corporate_action, event ISS), sau khử trùng F2; bỏ sự kiện issue_volumn ≤ 0;
  ngày có cặp volume âm/dương cùng method (VIC PP 21/08/2025) ⇒ không dùng, liệt kê.
  - Áp cho tỷ lệ mẹ→con khi: con là mã phát hành, ex ≤ D (PIT), ex > stake_date (stake KBS đo trước sự kiện).
  - S_pre = số CP dùng ở tháng cuối < ex; r_b = tổng Bonus/DIV cùng ngày ex; S_post = S_pre(1+r_b) + Σ volume cùng ngày.
    Hệ số f = S_pre(1+r_b)/S_post; tỷ lệ mẹ s_eff = s × Π f (mặc định: mẹ KHÔNG tham gia).
  - Đối chiếu KBS: nếu có bản ghi cổ đông lớn của CHÍNH MẸ tại con với update_date ≥ ex (raw/kbs_sh_v4 rồi raw/kbs_sh)
    ⇒ dùng % đó từ D ≥ listing_date của đợt phát hành (kết quả chào bán phải công bố trước niêm yết); thiếu listing_date
    ⇒ từ update_date + 90 ngày. Trước mốc đó dùng mặc định. Độ nhạy: (i) chặt: luôn update_date+90; (ii) tham gia đủ (s giữ nguyên).
  - Số CP con (CAP_FIX): D ≥ ex mà số CP < S_post × 0,98 ⇒ dùng S_post (CP mới tồn tại kinh tế dù chưa niêm yết).
  - VCSH (mọi mã có sự kiện, cả mẹ lẫn con — mở rộng): D ≥ ex ⇒ E += total_value nếu total_value > 0 VÀ CĐKT đang dùng
    chưa phản ánh (paid_in/10.000 < S_post × 0,99; không có paid_in ⇒ cuối quý CĐKT < ex). Gắn cờ PROCEEDS_ADD.
  - Liệt kê mọi ca (trong và ngoài N) với s trước/sau, nguồn KBS.
F2. **Khử dòng trùng** corporate_action TRƯỚC khi cộng cùng ngày ex: khoá (mã, ex, method, ratio, issue_volumn) — thêm
  issue_volumn so với chữ dispatch để không gộp nhầm cặp VIC PP ±. Giữ dòng có listing_date. Liệt kê (GAS Bonus 3% 2025-08-28…).
F3. **5 chỗ khác PREREG v3:**
  (i) TREASURY_FIX giữ, ghi là mở rộng ngoài PREREG v3; điều kiện siết: không áp nếu có sự kiện ISS ex ≥ cuối quý BQ (bao gồm bằng).
  (ii) Cùng ngày ex: giữ CỘNG tỷ lệ (Bonus + DIV cùng gốc CP trước ex; BSR sổ thật ×1,615) — ghi là khác chữ Π của PREREG v3;
       độ nhạy Π(1+r) báo kèm.
  (iii) ISS_FIX hai chiều đúng chữ PREREG v3: |CP/kỳ vọng − 1| > 2% ⇒ kỳ vọng, cửa sổ [ex, ex sự kiện CP kế tiếp KHÁC loại
       Bonus/DIV); độ nhạy một chiều (v3).
  (iv) §C2 áp đúng chữ: (c) đầu tiên theo thứ tự c1, c2, c3 đạt N ≥ 8 thay cho (a). Báo kèm hull (a)∪(d) để so.
  (v) LOO của (d) dùng n ≥ 11.
F4. GLT / SZL: kiểm và ghi kết luận (ngoài N); share_fixes chỉ giữ nhãn đúng.
F5. Trình bày TRUNG TÂM là KHOẢNG: {trung vị N, LOO min…max (chẵn/lẻ N), bỏ KSF, bỏ KSF&CMX} + bootstrap khối p5/p25/p75/p95.
  KSF giữ trong đặc tả chính (BANNED là luật đầu tư, không phải tiêu chí đo).

## B. KHÔNG đổi
Ứng viên dải (a)–(d), R1/R2, con mỏng, độ phủ ≥60% ở ≥3 tháng, stale, VCSH mẹ, PIT stake +90, tiêu chí §C v3 (trừ đúng chữ C2).

## C. Ánh xạ ra đề xuất HHS (khai trước; chỉ là đề xuất)
Base 0%. Mốc độ nhạy (mỗi mốc gắn nhãn nguồn):
- "trung tâm" = khoảng F5 (đầu trên khoảng); "hiện tại" = trung vị cắt ngang tháng cuối (d, 11/2026);
- "phân tán một holding" = q75 liên-holding của N (đặc tả chính); đầu âm chỉ giữ nếu HHS thuộc R1/R2 (premium cấu trúc).
Báo hull (chọn theo §C2 đúng chữ) và hull (a)∪(d): độ rộng, 0% ở phân vị nào. Số không ủng hộ gợi ý skeptic thì nói thẳng.
