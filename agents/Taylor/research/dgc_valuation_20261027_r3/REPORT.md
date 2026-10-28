# DGC định giá VÒNG 3 (hoàn thiện phần mở), 27/10/2026

Job `Taylor_20261026_180245`. r1/r2 và `../dgc_q3_forecast_20261026/FORECAST.md` KHÔNG sửa. READ-ONLY, không phải khuyến nghị. Đơn vị tỷ đồng, đ/cp. **[UL]** = ước lượng. Tra web ngày 27/10/2026. Tái lập: `python3 model.py` (log `run_stdout.txt`), md5 ở `LOCK.txt`. Đã bỏ qua tin pháp lý (user xác nhận không có tin mới) và thuế suất lãi tiền gửi (legal-vn).

> **BCTC Q3 của DGC CHƯA công bố** (tìm 27/10: chỉ có dự báo MBS 350 tỷ LNST mẹ, bài 29/09; không có số thực). Không so được Q3 thực với dự báo khoá 320 [270;370]. Vẫn phải chạy lại khi BCTC Q3 ra.

## Kết luận (10 dòng)
1. **Kỳ vọng r3 = 32.650 đ/cp (r2: 32.457, +193)**; cơ sở 33.640; thuận 51.983; nghịch 18.110. Duy nhất đầu vào đổi: tiền PAT thuộc CĐKKS 365 → **274** (xem mục 4). So giá 26/10 (32.100): +1,7%; vẫn gần như không có biên an toàn.
2. **1.600 tỷ: nghiêng HỢP NHẤT, nhưng KHÔNG đọc được Nghị quyết gốc.** Mọi bài báo chỉ ghi "lợi nhuận sau thuế 1.600" không nhãn; chỉ doanh thu 10.100 được gắn nhãn "hợp nhất" (Cafef 23/07). Phép chia 54%: LNST hợp nhất bán niên 871 (tự lập) / 863 (sau soát xét) ÷ 1.600 = 54,4% / 53,9%, còn LNST mẹ ~797–789 ÷ 1.600 = 49,8% / 49,3% (không ra 54%). Đánh giá **~70% hợp nhất [UL]** (r2: 50/50). Xác suất đạt 1.600: **24,4%** (r2 ≈ 20%) = 0,7×31,3% + 0,3×8,4%. Không đổi giá trị nội tại.
3. **Khai trường 25: vẫn đóng; KHÔNG có mốc mở lại nào.** ĐHĐCĐ 13/08: "chưa thể đưa ra thời điểm khai trường này hoạt động trở lại"; 29/09: "tiếp tục dừng hoạt động, khiến DGC phải nhập khẩu 100% quặng". Bằng chứng ĐỊNH HƯỚNG duy nhất: giấy phép 10/11/2020 cho 6 năm từ 03/2021 (hết ~03/2027) và SHS dự kiến gia hạn "vào cuối năm 2026" (nguồn thứ cấp, chưa kiểm). Giả định "mở lại ½ năm 2028" vẫn **không có nguồn** — không đổi.
4. **PAT: tiền + đầu tư nắm giữ đến đáo hạn 30/09 = 559 tỷ** (giảm 33% so đầu năm), thấp hơn ước lượng r2 (650–750). CĐKKS 49% × 559 = **274** (r2: 365) ⇒ +91 tỷ = **+240 đ/cp** cho phần tiền; kỳ vọng +193 sau haircut/lãi.
5. **Cổ tức 8.000 đ/cp** (50% còn lại 2025 + tạm ứng 30% 2026) = 3.038,2 tỷ / 379,8 tr cp: số tiền XÁC NHẬN (baophapluat); chốt 15/09, dự kiến chi 25/09 (ngày chi thực tế chưa thấy thông báo hoàn tất).
6. **HOSE: vẫn "Cảnh báo và hạn chế giao dịch"** tại 24/10 (Vietstock); giá 33.700 ngày 23/10. Không có tin gỡ hạn chế.
7. **Nghi Sơn GĐ1: mốc vẫn Q4/2026** (HĐQT dời từ Q1/2026; đã giải ngân 1.378 tỷ hết 2025; GĐ1 ~2.400 tỷ), có rủi ro nhập titan từ Trung Quốc (13/08). Không tìm được tin T9–T10 về chạy thử/COD. Không đổi giả định (capex còn lại 929).
8. **Thuế hiệu dụng: KHÔNG tính được từ BQ** — `ticker_financial` không có cột lợi nhuận trước thuế/chi phí thuế (chỉ NP, EBITM, Cash, Debt…). Thuyết minh ưu đãi (dự án/năm hết hạn) **không tìm được** trên web; cần BCTC gốc (thuyết minh thuế TNDN). Không đổi (thuế lãi 13%, độ nhạy 20% = −109 đ/cp ở r2).
9. **BCTC bán niên soát xét (UHY):** LNST hợp nhất 871 → 862,71 (−8 tỷ), ý kiến **ngoại trừ** về vụ án (28/08). LNST **riêng lẻ** công ty mẹ H1 = 1.388 (chủ yếu cổ tức từ công ty con 1.297) — nghĩa thứ ba của "mẹ", KHÔNG phải mẹ-hợp nhất. Tiền/tiền gửi 30/06, vay, tồn kho, CĐKKS: **không tìm được** số gốc (bài chỉ nói tiền "giảm đáng kể so với đầu năm").
10. Còn mở: BCTC Q3 DGC (tiền ròng 30/09 vẫn dựng lại; sai ±500 tỷ ≈ ±1.300 đ/cp), MI lõi, mốc khai trường, Nghị quyết gốc.

## Bảng: giả định r2 → bằng chứng mới
| # | Giả định r2 | Bằng chứng mới (nguồn, ngày tra 27/10) | Kết quả |
|---|---|---|---|
| 1 | 1.600 mẹ/hợp nhất 50/50 | Cafef 23/07 (https://cafef.vn/hoa-chat-duc-giang-dat-muc-tieu-loi-nhuan-giam-gan-mot-nua-chia-co-tuc-80-188260723145118381.chn): "doanh thu hợp nhất ở mức 10.100 tỷ đồng, lợi nhuận sau thuế 1.600 tỷ đồng" (không nhãn LN). Nhà Đầu Tư/Stockbiz 13/08 (https://stockbiz.vn/tin-tuc/dgc-dat-ke-hoach-loi-nhuan-giam-gan-mot-nua-nguon-quang-tro-thanh-bien-so/41426802): ĐHĐCĐ thông qua "doanh thu 10.100 tỷ đồng, lợi nhuận sau thuế 1.600 tỷ đồng và mục tiêu cổ tức 30%"; kế hoạch cổ tức 2026 30%. Thuongtruong 28/08 + baophapluat: LNST hợp nhất H1 862,71 | **~70% hợp nhất [UL]**; p(đạt)=24,4%. Nghị quyết gốc: không tìm được |
| 2 | Số bảng cân đối H1/BCTC gốc: thứ cấp | https://thuongtruong.com.vn/news/hoa-chat-duc-giang-dgc-bi-kiem-toan-ngoai-tru-loi-nhuan-ban-nien-giam-mot-nua-168802.html (28/08): ngoại trừ UHY do vụ án; 871→862,71. Số 10.921 tỷ tiền gửi: không xác nhận được | Không đổi; BCTC Q3: chưa công bố |
| 3 | Thuế 13% lãi tiền | BQ không có cột PBT/thuế; web không có thuyết minh ưu đãi | Không đổi, nêu "không tìm được" |
| 4 | PAT-CĐKKS 365 [UL] | https://chuyendongthitruong.vn/cong-ty-con-cua-hoa-chat-duc-giang-dgc-bao-lai-quy-32026-giam-46-so-voi-cung-ky-346601.html (25/10): PAT Q3 DT 440, LNST 59 (−46%), thu nhập tài chính **11** (−18%), tiền+đáo hạn "hơn 559 tỷ đồng, giảm 33% so với đầu năm". Cổ tức PAT 29% = 72,5 tỷ, chốt 16/09, chi 25/09 (baophapluat/stockbiz; DGC Lào Cai 51% nhận ~37 tỷ ⇒ CĐKKS ~35,5 tỷ) — đã ra khỏi số dư 30/09 | **274**; TNTC Q3 11 khớp skeptic 11,4 (tự kiểm theo bài, BQ chưa có Q3 PAT). Chạy lại model |
| 5 | Khai trường mở lại ½ 2028 (không nguồn) | Stockbiz 13/08: "chưa thể đưa ra thời điểm…"; nguồn quặng "ngày càng khan hiếm", mục tiêu đủ nguyên liệu "ít nhất đến đầu năm sau". Nguoiquansat 29/09: "tiếp tục dừng hoạt động… nhập khẩu 100% quặng". Giấy phép 10/11/2020, 6 năm từ 03/2021; SHS: gia hạn dự kiến cuối 2026. Không có tin T9–T10 về cấp lại | Không đổi. Không tìm được bằng chứng mốc |
| 6 | Nghi Sơn GĐ1 Q4/2026 | Stockbiz 13/08: "vẫn giữ mục tiêu… vận hành trong quý IV/2026", khó nhập titan; baophapluat: dời Q1→Q4/2026, giải ngân 1.378 tỷ hết 2025. Không có tin T9–T10 | Không đổi |
| 7 | HOSE hạn chế; cổ tức 8.000 | Vietstock cập nhật 24/10: "Cảnh báo và hạn chế giao dịch"; hạn chế từ 26/05 (khớp lệnh định kỳ lô chẵn), cảnh báo từ 30/06. Cổ tức: 3.038,2 tỷ, ~8.000 đ/cp, chốt 15/09, chi dự kiến 25/09 (baophapluat) | Xác nhận số tiền; ngày chi thực tế chưa xác nhận |

## Mục 8: chạy lại model (đầu vào đổi duy nhất: `PAT_MI_CASH` 365 → 274)
| Kịch bản | r2 | r3 |
|---|---|---|
| Thuận | 51.768 | 51.983 |
| Cơ sở | 33.438 | 33.640 |
| Nghịch | 17.948 | 18.110 |
| **Kỳ vọng** | **32.457** | **32.650** (+193) |
Nhạy MI lõi 13%: 31.929; 17,8%: 30.778; PE peer 10y: 33.189 (`out_sensitivities.csv`). Chênh r2→r3 hoàn toàn do PAT-CĐKKS; xác suất 1.600 là kết quả phụ, không vào giá. Không đổi: 1.600 không tác động EV; mốc khai trường; Nghi Sơn; tiền ròng 6.063 (vẫn dựng lại).

## Chưa tìm được (nói thẳng)
Nghị quyết ĐHĐCĐ gốc; BCTC gốc Q2/bán niên (số tiền, vay, tồn kho, thuế, CĐKKS); BCTC Q3 DGC; thuyết minh ưu đãi thuế; tin T8–T10 về cấp lại phép khai trường 25/19B; tin chạy thử Nghi Sơn T9–T10.
