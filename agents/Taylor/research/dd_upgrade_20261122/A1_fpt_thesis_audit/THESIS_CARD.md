# THESIS CARD — FPT (A1 v2, 22/11/2026) · chỉ đọc; không đổi định giá/lệnh/stop
v1 của Taylor bị fundamental-skeptic REFUTED (văn bản, medium-high); v2 áp 9 đính chính (số phiên, plan, GDKHQ, điều kiện huỷ, lập luận). Nguồn đối chiếu độc lập: BQ `tav2_bq.ticker`/`corporate_action`, `dnse_raw_2026-11-20.jsonl`, `data/trade_plans/plan_*`, `kb/dd_price_zones.json` rev3, `REPORT_r3.md`, lưới 540 kết cục khôi phục từ git `fc5bd02d9` (calc_r3 đã bị trim ở `14ad1c925`).

## 0. Việc user cần biết TRƯỚC khi quyết
- **Plan nháp 23/11 (cả 2 tài khoản) ĐÃ có lệnh STOP SELL FPT 800 (SpaceX) / 500 (ZaloPay), chưa duyệt.** Duyệt plan như thường = bán.
- Chuỗi 19/11: duyệt bán 21:50 → **hủy 23:09**, lý do ghi "DD không có tin xấu/pháp lý mới; giữ vị thế". Tiền đề "không có tin pháp lý mới" **chưa ai kiểm** (r3 §10: chưa quét pháp lý sau 01/11).
- Giá 20/11 = **45.000**: thấp hơn giá vốn 12,0% (51.137,5 SpaceX / 51.160 ZaloPay), dưới stop −10% (46.023,8 / 46.044) 2,2%, dưới đáy vùng rev3 (45.270) 0,6%.
- **GDKHQ cổ tức 1.000đ = 27/11** (chốt 30/11, trả 10/12). DNSE điều chỉnh giá từ tối 26/11 ⇒ P&L mà bộ đo stop đọc thấp thêm ~2pp một cách cơ học (≈−14%).

## 1. Luận điểm (rev3)
- Kỳ vọng trọng số **57.312** (còn quyền cổ tức; sau GDKHQ ≈56,3k), vùng P10–P90 **45.270–68.466** (≈44,3k sau GDKHQ). Skeptic 09/11 CONFIRMED. §2.5 fear-buy KHÔNG đủ điều kiện.
- Khi vào (giá vốn ~51.140) thấp hơn tâm 10,8%. Với giá 45.000 chỉ **8,7%** trọng số kết cục dưới giá (27,0% ở lúc vào); giá ≈ trung bình nhánh XẤU (45.435 sau chiết khấu thanh khoản, −1%), KHÔNG phải "thấp hơn kịch bản XẤU" (nhánh XẤU trải 40,1–52,2k).
- Độ mong manh: chặn RONIC ở ROIC5Y → 52.311; chặn ở Ke → 50.652 (bản G); Gordon 47,5–51,1k — tất cả vẫn **cao hơn 45.000**, nhưng phụ thuộc giả định tăng trưởng 5 năm.

## 2. Điều kiện HUỶ / mốc hạ (đo được hay không, trong cửa sổ deal hay không)
| Điều kiện (nguồn) | Hiện trạng | Quan sát được trước 11/12? |
|---|---|---|
| Kiểm toán ngoại trừ/từ chối (§3 HARD ABANDON, r3 §9) | chưa có BCTC kiểm toán mới | KHÔNG (≈cuối 01/2027) |
| Khoản 618,8 tỷ không thu hồi lớn hơn đã ghi | chưa kiểm | KHÔNG (BCTC) |
| CFO 2026 âm cả năm | chưa có số năm | KHÔNG (≈Q1/2027) |
| Cổ tức đã hứa bị huỷ (§3 #4) | công bố 19/11 | CÓ — 10/12 |
| FTEL thu hồi/chuyển giao ngoài giá thị trường; FTEL pha loãng/FOX mất tư cách đại chúng | **chưa quét sau 01/11** | CÓ (tin) — cần legal-vn/web |
| **KQKD tháng 10–11: ký mới NN luỹ kế <+15%** (REPORT.md:166, r2 §8) → hạ | chưa kiểm số tháng 10 | **CÓ — giữa 11 và 12/2026** (mốc cơ bản duy nhất trong cửa sổ) |
| Nhật (JPY) <+15% (r2 §8) | chưa kiểm | một phần |
| Lãi huy động +100bp (r2 §8) | hiệu dụng 7,4% không đổi (cctg 02/11), Big-4 12M 6,8% (16/11) ⇒ chưa xảy ra | CÓ (đo được) |
| ROIC5Y ≥20% = mốc NÂNG, không phải hạ (r3:77); hiện 17,7% | cập nhật theo năm | KHÔNG |
Hệ quả: **nếu miễn stop, trong cửa sổ 11/12 chỉ còn tin pháp lý FTEL, KQKD T10–11, lãi huy động và giá** để huỷ luận điểm; 3/4 điều kiện HARD ABANDON không quan sát được.

## 3. Dữ kiện mới từ 06/11
Giá 06/11 50.800 → 20/11 45.000 (−11,4%); VNINDEX 1.725,36 → 1.688,79 (−2,1%). Giảm liên tiếp 16–20/11 (49.400→45.000); KL 18–20/11 16,2M/18,4M/15,7M ≈1,6×/1,7×/1,4× Volume_1M. **Giải thích còn mở, ba nguồn:** (i) thị trường biết điều chưa có trong DD (chưa chứng minh), (ii) bán tháo, (iii) **nguồn cung cơ học: 171,4M cổ phiếu thưởng 10% giao dịch từ 12/11 — KL tăng vọt đúng 12/11 (17,3M)**. Livermore (06/11 14:19 user đã gỡ khỏi quyết định FPT): H20 dự báo DOWN, chấm 03/12 — chưa chấm, không dùng làm lý do. Tin/CBTT FPT ngoài `corporate_action`: chưa kiểm.

## 4. Mốc
Phiên **10/25** (đếm sau ngày vào 06/11, theo `count_trading_days`; còn 15) · phiên 25 = 11/12 nhưng luật còn treo câu "TIME bán ở plan 11/12 hay 12/12" · GDKHQ 27/11 · Livermore chấm 03/12 · trả cổ tức 10/12 · BCTC Q4: ≈cuối 01/2027 (ngoài cửa sổ).

## 5. Câu hỏi để user quyết (không khuyến nghị)
Dữ kiện cho hai phía: **ủng hộ miễn stop** — giá ≈ trung bình nhánh XẤU, tâm/bản G/Gordon đều cao hơn giá, lãi huy động chưa tăng, 4 điều kiện cứng chưa xảy ra. **Chống** — stop đã xuyên, đà giảm kèm KL 1,4–1,7× và chưa tách được yếu tố cổ phiếu thưởng, giá vốn thấp hơn 12%, cỡ 5% NAV vượt trần 2–4%/mã của khung §3, chân trời DD 5 năm ≠ deal 25 phiên, điều kiện cơ bản đo được trong cửa sổ rất ít. (Cổ tức và "luật 4 đạt" KHÔNG phải lý do: cổ tức trung tính về giá trị; luật 4 là luật xét candidate MUA.)
(a) Miễn stop, hay giữ −10%/25 phiên (⇒ duyệt plan 23/11 = bán)? (b) Nếu miễn: ngưỡng/sự kiện huỷ thay thế nào (vd. KQKD T10–11 ký mới <+15%, tin FTEL, giá < đáy vùng sau GDKHQ ≈44,3k)? (c) Chạy quét pháp lý FTEL/Bộ Công an + KQKD tháng 10 (legal-vn/web) trước khi quyết — tôi đề nghị làm ngay nếu anh muốn, vì lần hủy bán 19/11 dựa trên tiền đề này.
