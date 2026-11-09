# DGC — DD redo vòng 3b (09/11/2026, job Taylor_20261108_175121)

**Kết luận:** tâm **41.849 đ/cp** (sau CK 5 tỷ), P10/P50/P90 kết cục **33.272 / 41.362 / 50.227**; giá đóng cửa 06/11 **33.000** (BQ) ⇒ **DƯỚI vùng, mỏng**: giá thấp hơn P10 **0,8%**, **9,1%** trọng số kết cục nằm dưới giá. So r3: tâm 41.522 → 41.849 (**+0,8%**), P10 32.931 → 33.272, nhãn TRONG → **DƯỚI**. Số khớp ước tính của skeptic (41.849 / 33.272), tôi tự tái lập bằng `calc_r3b/model_r3b.py`.

Thay đổi duy nhất so với r3 là đính chính #4, chuyển sang **cách B** (user duyệt 08/11): giữ xác suất mở lại khai trường 25 ở **w = 0,5** như r2; nhánh mở lại **giữ** phần lãi gộp tăng thêm năm 2028 (+500 tỷ, `model.py:37` `up28`); **bỏ** phần biên tăng vĩnh viễn (terminal +1.000 tỷ/năm, `up`), vì phần này là thưởng moat mà moat thì không bền. Các đính chính #1, #2, #3, #5, #6, #7 của r3 giữ nguyên (code r3 được import, không sửa).

Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không email/PDF.

## 1. Cầu nối r3 → r3b (trước CK; CK 5 tỷ 0,725% → sau CK)

| Bước | Trước CK | Sau CK | Δ trước CK |
|---|---|---|---|
| r3 headline (w mở lại 0) — control assert khớp `model_r3_out.json` | 41.825 | 41.522 | |
| w 0 → 0,5, có biên vĩnh viễn 1.000 tỷ (= dòng w=0,50 của r3) | 48.101 | 47.753 | +6.276 |
| bỏ biên vĩnh viễn của nhánh mở lại (cách B) = **r3b** | **42.154** | **41.849** | −5.947 |

Trên mỗi cổ phiếu (tham số trung tâm, trước CK): lãi gộp 2028 của nhánh mở lại đóng góp **+659 đ/cp**; biên vĩnh viễn bị bỏ là **11.883 đ/cp**. Nhánh mở lại chỉ nhích tâm thêm +327 so với r3, nhưng cũng đủ đẩy P10 lên trên giá.

## 2. Tính lại các dòng biến thể mở lại khai trường (thay REPORT_r3.md:44-46)

| Biến thể (biên vĩnh viễn = 0) | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn | Dòng tương ứng ở r3 (có biên vĩnh viễn) |
|---|---|---|---|---|---|---|---|
| w = 0 (= headline r3) | 41.522 | 32.931 | 41.087 | 49.929 | 10,2% | TRONG | 41.522 |
| w = 0,10 | **41.587** | 33.006 | 41.228 | 49.941 | 10,0% | DƯỚI | 42.768 |
| w = 0,25 | 41.685 | 33.170 | 41.260 | 49.982 | 9,7% | DƯỚI | 44.637 |
| **w = 0,50 (HEADLINE r3b)** | **41.849** | **33.272** | **41.362** | **50.227** | **9,1%** | **DƯỚI** | 47.753 |
| w = 0,75 | 42.012 | 33.428 | 41.617 | 50.509 | 8,6% | DƯỚI | — |
| w = 1 (chắc chắn mở lại) | 42.176 | 33.586 | 41.742 | 50.581 | 8,0% | DƯỚI | — |

Dòng w=0,10 khớp skeptic (41.587; r3 ghi 42.768 vì có cộng biên vĩnh viễn). Khi bỏ biên vĩnh viễn, trục khai trường gần như **không còn tác dụng lên tâm** (w từ 0 lên 1 chỉ đổi tâm 41.522 → 42.176). Nó chỉ quyết định P10 nằm trên hay dưới giá 33.000, với khoảng cách vài trăm đồng.

## 3. Headline vs biến thể khác (sau CK, giá 33.000; mọi dòng dùng w=0,5, biên vĩnh viễn = 0)

| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE r3b** | **41.849** | **33.272** | **41.362** | **50.227** | **9,1%** | **DƯỚI** |
| nền biên r4 + bỏ chồng lấn | 39.427 | 32.911 | 39.289 | 46.515 | 10,4% | TRONG |
| nền r4 không sửa (đối chiếu) | 37.405 | 29.427 | 37.140 | 44.956 | 23,9% | TRONG |
| lá chắn thuế dự phòng 20% [UL] | 42.419 | 34.359 | 42.050 | 50.590 | 5,7% | DƯỚI |
| RONIC 20% (thưởng moat, chỉ đối chiếu) | 43.813 | 34.629 | 43.323 | 52.910 | 5,7% | DƯỚI |
| trọng số kịch bản r2 0,3/0,5/0,2 | 41.194 | 32.767 | 40.731 | 49.556 | 10,5% | TRONG |
| CÓ trục pháp lý (haircut tiền ròng) | 38.919 | 29.938 | 38.760 | 47.970 | 20,5% | TRONG |
| đối chiếu: w=0,5 CÓ biên vĩnh viễn (= r3 dòng w=0,50) | 47.753 | 35.794 | 47.722 | 59.765 | 5,1% | DƯỚI |

r ±50/100bp: 42.547 / 43.315 (giảm r) · 41.176 / 40.562 (tăng r).

**Nhãn mỏng.** Bốn biến thể đưa nhãn về TRONG: w mở lại = 0 (r3), nền biên r4, trọng số kịch bản r2, và có trục pháp lý. Ba số cần tách bạch: tâm 41.849 (kỳ vọng của lưới) · P50 41.362 · tham số trung tâm 43.410 (khai trường dừng, dự phòng hữu hạn 4 quý). n = 810 kết cục, min 25.782, max 59.765.

**Giá 33.000 ngụ ý gì** (tính tại r = 13,5%): để tâm bằng giá thì EBIT lõi phải chỉ còn ≈ **0,59×** mức cơ sở mãi mãi; hoặc cả ba điều xảy ra chắc chắn cùng lúc là kịch bản xấu, dự phòng vĩnh viễn và khai trường đóng (khi đó tâm 30.215). Từng điều kiện riêng lẻ: khai trường đóng chắc chắn ⇒ 41.509 · dự phòng vĩnh viễn chắc chắn ⇒ 37.045 · kịch bản xấu chắc chắn ⇒ 35.333.

## 4. Chiết khấu thanh khoản (CK) — cỡ 5 tỷ và cỡ sleeve thật
ADV250 (05/11/25–06/11/26) 83,8 tỷ, σ 2,97% ⇒ CK 5 tỷ **0,725%** (Q/ADV 6,0%, trong vùng hiệu chỉnh) · ADV60 17,7 tỷ ⇒ CK 5 tỷ 1,13% (Q/ADV 28%, NGOÀI vùng hiệu chỉnh). Sleeve thật 10/20/40 triệu: CK 0,03/0,05/0,07% (ADV250), 0,05/0,07/0,10% (ADV60). Ở cỡ sleeve, P10 khoảng 33.481–33.504 và tâm khoảng 42.112–42.141 ⇒ **DƯỚI vùng** ở cả 6 ô (`SUMMARY.json.sleeve_size_labels`).

## 5. Kỷ luật exit (STANDARD #8) — vị thế ZaloPay

Vị thế hiện có (đối soát broker `dnse_raw_2026-11-08.jsonl`, tài khoản 0001743768): **10.000 cp, giá vốn 39.775**, giá 33.000 ⇒ giá trị thị trường **330,0 tr = 35,3% NAV** (NAV 06/11 **934,55 tr**, `nav_history_ZaloPay.csv`). Tính theo giá vốn là 397,75 tr = **42,6%**. Lỗ chưa thực hiện −67,75 tr. **Trần sleeve 2–4% NAV ⇒ vượt khoảng 9–18 lần.**

Các lựa chọn dưới đây chỉ để user cân nhắc: tôi KHÔNG quyết thay và KHÔNG đặt lệnh. HOSE hạn chế giao dịch mã này (chỉ khớp phiên chiều), nên mỗi đợt = 1 phiên chiều. Tác động giá = σ60 × √(Q/ADV60).

| Lựa chọn | Giữ lại | Bán | Tỷ trọng còn lại | Giá trị bán | Q/ADV60 (mỗi đợt) | Tác động nếu bán 1 lần | Lỗ thực hiện @33.000 | Phí + thuế |
|---|---|---|---|---|---|---|---|---|
| A — giữ nguyên | 10.000 | 0 | 35,3% | 0 | — | — | 0 | 0 |
| B — về ~10% NAV, 2 đợt | 2.800 | 7.200 | 9,9% | 237,6 tr | 1,34% (0,67%) | 0,25% | −48,8 tr | 0,47 tr |
| C — về trần 4%, 3 đợt | 1.100 | 8.900 | 3,9% | 293,7 tr | 1,66% (0,55%) | 0,27% | −60,3 tr | 0,58 tr |
| D — về sàn 2%, 3 đợt | 500 | 9.500 | 1,8% | 313,5 tr | 1,77% (0,59%) | 0,28% | −64,4 tr | 0,62 tr |

Đọc bảng:
- **Thanh khoản không phải ràng buộc**: cả gói lớn nhất chỉ bằng 1,8% ADV60, tác động giá < 0,3% ngay cả khi bán một lần. Việc chia đợt chủ yếu để giảm rủi ro chọn sai thời điểm (một phiên chiều HOSE hạn chế có thể mỏng bất thường), không phải để giảm tác động giá.
- **Định giá kéo theo chiều khác**: giá 33.000 đang DƯỚI vùng, thấp hơn tâm 21%. Bán ở giá này là chốt lỗ ở mức mà mô hình đánh giá rẻ.
- **Nhưng kỷ luật tỷ trọng không phụ thuộc định giá**: 35% NAV vào một mã đang có vụ án ở lãnh đạo, bị HOSE hạn chế giao dịch và cắt margin là rủi ro tập trung, đúng loại rủi ro mà trần sleeve được đặt ra để chặn.
- Nếu chọn A, cần user ghi nhận bằng văn bản đây là ngoại lệ có chủ đích (ngoài trần sleeve), kèm mốc xem lại.
- Nếu chọn B/C/D, nên gắn với các mốc ở §7 (vd chỉ bán đợt cuối khi có tin xấu xuống), không bán theo lịch cố định.

## 6. §2.5 fear-buy và WARNING pháp lý/quản trị
- **§2.5: NON (đứng).** P/B công ty mẹ ≈ 0,96 (đạt). Trụ #2 là tiêu chí **§2** (doanh nghiệp có nhà nước chi phối), không phải §2.5 như REPORT_r3 ghi; tiêu chí này trượt vì DGC là doanh nghiệp tư nhân ⇒ không đủ điều kiện sleeve fear-buy.
- Vụ án môi trường/khai thác/kế toán: cựu Chủ tịch HĐQT Đào Hữu Huyền (sở hữu 18,38%) bị tạm giam 17/03/2026; 07/2026 khởi tố thêm TGĐ, thành viên HĐQT, PTGĐ và GĐ mỏ KT25. Chưa thấy quyết định khởi tố pháp nhân. Quét WebSearch 08/11: không có tin truy tố/xử phạt pháp nhân mới, không có tin mở lại khai trường 25. Các rủi ro này chỉ ở mức WARNING, không đưa vào base (luật user 02/11).
- Ý kiến ngoại trừ BCTC kiểm toán 2025 (950,9 tỷ tồn kho) · HOSE hạn chế giao dịch từ 26/05/2026 · cắt margin · dự phòng môi trường 200 tỷ chưa phân định có lặp lại hay không · HTM 9.531 chưa đối chiếu PDF gốc.

## 7. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **Lên (DƯỚI sâu hơn):** dự phòng môi trường Q4/26 = 0 · GPM quý ≥ 22% không dự phòng 2 quý liền · văn bản cho khai trường 25 hoạt động lại. Lưu ý: ở r3b văn bản mở lại chỉ đổi tâm rất ít (≤ +330); chỉ khi chứng minh được lợi thế chi phí BỀN thì mới xét lại phần biên vĩnh viễn.
- **Xuống (về TRONG):** dự phòng tiếp tục ≥ 100 tỷ ở Q4/26 · GPM quý < 17% (về nền r4) · khởi tố pháp nhân hoặc có phạt/truy thu định lượng được · quyết định đóng vĩnh viễn khai trường 25 (w → 0 ⇒ TRONG).
- **HARD ABANDON:** khởi tố pháp nhân DGC + đình chỉ hoạt động nhà máy chính, hoặc tiền gửi/HTM bị phong toả.

## 8. Sửa văn bản so với REPORT_r3 (không sửa REPORT_r3.md, file có hash trong LOCK r3)
- **REPORT_r3.md:72**: số vị thế đúng là 330,0 tr = **35,3% NAV theo giá thị trường** (NAV 934,55 tr ngày 06/11), hoặc 42,6% theo giá vốn 39.775. Đã đối soát với broker. "Trụ #2" là tiêu chí §2, không phải §2.5.
- **REPORT_r3.md:17** (và §1 dòng #5): viện "luật 3c" làm cơ sở cho nền biên R2 là sai. Cơ sở thật là số BCTC HN Q3/2026: biên gộp **20,5%** (gồm dự phòng) / **24,6%** (bỏ dự phòng); Q3 chạy hoàn toàn bằng quặng mua ngoài; R2 19,5% ≈ trung vị 4 peer **19,47%** (ADDENDUM_5F_r2.md dòng 16).
- **REPORT_r3.md:44-46**: thay bằng bảng §2 ở trên.
- `ADDENDUM_5F.md` và `SUMMARY_5F.json` còn ghi tâm cũ 44.767 (r2) ⇒ đã thêm ghi chú đồng bộ r3b ở đầu mỗi file. Hai file này không có trong LOCK nào; số cũ được giữ nguyên bên dưới ghi chú.

## 9. Giả định khoá (đủ ở `SUMMARY.json.assumptions`, mỗi dòng có basis)
Giữ nguyên như r3: nền biên R2 19,5/20,7% · kịch bản 0,25/0,5/0,25 [UL] · RONIC = Ke · dự phòng 100 tỷ/quý chia ba nhánh một lần/4 quý/vĩnh viễn, mỗi nhánh 1/3 [UL], lá chắn thuế 0 [UL] · Nghi Sơn theo sổ sách, trục ±500 · r = 13,5% ±50bp · g 3%, thuế dài hạn 15% · hệ số EBIT 0,8–1,2 · pháp lý ngoài base. **Mới ở r3b:** mở lại khai trường w = 0,5 [UL, user chốt]; nhánh mở lại chỉ +500 tỷ lãi gộp năm 2028, terminal +0.

## 10. Tái lập
`$DNA_PYEXE -I calc_r3b/model_r3b.py` (control assert: headline r3 41.825 trước CK + 3 dòng mở lại của r3, khớp `calc/model_r3_out.json`) → `calc_r3b/LOCK_r3b_md5.txt` (ghi **2026-11-09T00:54:10+0700**, TRƯỚC khi so giá; 23 file assert + 2 file nguồn live chỉ khai md5) → `compare_r3b.py` → `make_summary_r3b.py`. Chạy 2 lần trùng byte: `model_r3b_out.json` `a8fa8dac…`, `summary_r3b_core.json` `918d751e…`, `compare_r3b_out.txt` `627d8894…`, `SUMMARY.json` `180e03bf…`. Backup r3: `SUMMARY_r3.json` (`a86b5916…` = SUMMARY.json của r3).
