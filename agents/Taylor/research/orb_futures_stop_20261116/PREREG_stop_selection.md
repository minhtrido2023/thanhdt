# PRE-REGISTRATION — tiêu chí chọn mức stop thảm hoạ ORB VN30F

Khai báo TRƯỚC mọi lần đổi mức stop về sau (quant-skeptic 16/11/2026, job Taylor_20261116_165006).
File này commit RIÊNG, trước mọi lần chạy lại có ý định đổi `STOP_PCT`. Sửa file này = commit riêng,
có lý do, TRƯỚC khi nhìn kết quả mới. Mọi lần đổi phải trích commit hash của bản PREREG đang áp dụng.

## Tiêu chí (cố định)
1. **Chọn theo tần suất chạm, KHÔNG theo PnL/Sharpe/MaxDD.** Mức stop = mức NHỎ NHẤT trong lưới có tỉ lệ
   phiên chạm ≤ **3%** trên toàn tape ghép.
2. **Lưới cố định** `[1,0; 1,5; 2,0; 2,5; 3,0; 4,0]%` (N trial = 6). Thêm mức mới vào lưới ⇒ N tăng, khai
   báo lại ở đây trước khi chạy.
3. **Quy ước mô phỏng**: tín hiệu/vào giữ nguyên `orb_pt.py`; thoát close bar **14:29** cho MỌI đoạn tape;
   slip 1 tick/chiều + 0,6bps; khớp stop = mức stop, gap qua ⇒ giá mở bar. Luôn công bố THÊM kịch bản
   khớp ở cực trị bar (`fill="extreme"`).
4. **Số rủi ro công bố bắt buộc**: lỗ 1 phiên tệ nhất (khớp hoàn hảo + cực trị bar), MaxDD **CỘNG DỒN**
   cho 1 HĐ cố định (VND + % notional + % sleeve 100tr), độ nhạy phí +2bps khứ hồi, và tách theo đoạn
   (FiinX 2022-23 không có bar / bar 1m / từ 2024).
5. **Chỉ được ĐỔI mức khi** tỉ lệ chạm của mức hiện hành trên dữ liệu MỚI (sau 2026-11-16, ≥250 phiên) lệch
   khỏi khoảng [1%, 5%]. Không đổi vì PnL tốt/xấu.
6. Stop là **bảo hiểm**, không phải edge: không được trích cải thiện Sharpe/MaxDD của stop như bằng chứng
   alpha (toàn bộ cải thiện nằm ở đoạn FiinX 2022-23, khớp lý tưởng, không đo được trượt).

Script: `stop_study.py` (cùng thư mục). Kết quả: `stop_study_result.json` (khối `v2_risk`).
