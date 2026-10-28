# PREREG V3 — Cổng state cho LAG (bản sao engine; job Taylor_20261020_122917, EXPLORATORY)

Không sửa engine thật, pin, registry, pin_ledger. Không kết luận đổi luật. Viết + md5 + commit TRƯỚC khi chạy V3.

## 1. Câu hỏi
REPORT_D (job 113646): mỗi chân 107–110 lô LAG (book ref) mở lúc BEAR (w_lag_tgt=0, state 2); 42–43 lô còn mở khi
cap_lag bật lại ⇒ có trọng số combined khác 0. Đo đóng góp ròng của nhóm này lên R3 bằng engine (bản sao `eng/`).

## 2. Biến thể (env `V3_MODE`, chỉ áp cho lệnh gọi `simulate()` có name bắt đầu `v23audit_LAG` — cả lượt base cho
CAPIT lẫn lượt chính; mặc định off ⇒ byte-identical với pin)
- **V3A `noentry_bear`**: lệnh LAG (mọi play_type của book LAG, kể cả CAPIT_L nếu có) CHƯA khớp phần nào bị huỷ nếu phiên
  khớp có `state == 2` (state_ff, đúng nguồn allocator dùng cho w_lag_tgt). Lệnh đã khớp một phần trước khi vào BEAR
  vẫn khớp tiếp như engine.
- **V3B `close_reopen`**: lô có `state(entry_date) == 2` bị xếp lệnh bán T+1 Open (reason `V3_REOPEN`) ở phiên ĐẦU TIÊN
  `state != 2` (tức phiên allocator mở lại cap). Lô hết hạn 25 phiên trước đó thì không bị ảnh hưởng. Còn 1 phiên phơi
  nhiễm (phiên mở cap → Open phiên sau) — hệ quả cơ học của T+1, ghi rõ.
- Không kết hợp ZVF (V1) — mỗi biến thể đổi đúng 1 trục so với pin.

## 3. Đo
- 4 chân × {V3A, V3B}: `METRIC cagr/sharpe_252/max_dd` từ CSV engine; Δ = biến thể − pin.
- Số lệnh bị huỷ / lô bị đóng (`[V3]` trong log); số lô LAG mở lúc BEAR còn lại (theo cách đếm `d_bear_lag.py`).
- Nhãn theo |ΔCAGR| vs sàn nhiễu 0,46pp ở 4 chân (như PREREG_V1 §3). Diễn giải: −ΔCAGR(V3A) ≈ đóng góp ròng của việc
  MỞ lô LAG trong BEAR (gồm cả hiệu ứng thứ cấp: tiền/slot rảnh sau BEAR). −ΔCAGR(V3B) ≈ đóng góp của phần GIỮ các lô
  đó sau khi cap mở lại. Hai số không cộng được với nhau.
- Kèm IS (2014–2019) / OOS (2020+) CAGR từ DAILY combined_nav cho mô tả (không phải kiểm định; N sự kiện BEAR nhỏ:
  lô BEAR tập trung 2015/2020/2022/2023).

## 4. Control + self-check
Như PREREG_V1 §4: ZVF_MODE=off & V3_MODE=off ⇒ 4 md5 pin; mọi run self-check 0 VND BAL+LAG.

## 5. Giới hạn
- Không kết luận đổi luật (yêu cầu dispatch). Số lô BEAR ít và dồn vào 2022 ⇒ Δ là mô tả 1 giai đoạn, không phải edge.
- Huỷ lệnh ở BEAR làm book LAG ref có cash rảnh khi vào lại NEUTRAL ⇒ đường NAV book ref khác pin cả SAU BEAR.
