# Giai đoạn 4 — Rolling 3-4 cửa sổ IS/OOS cho C1 (điều kiện #3/4 để mở lại)

Job `Taylor_20260829_173433` (dispatch Mike, danh sách nghiên cứu cuối tuần). Yêu cầu của
quant-skeptic khi REFUTED plan live-25% (2026-08-26): chia lại 2014-2026 thành 3-4 cửa sổ
liên tiếp thay vì 2 (IS 2014-19 / OOS 2020+), xem OOS +1.70pp có tập trung vào 1-2 episode
may mắn hay không.

**Không backtest mới.** Tái dùng 100% `exp_dc3book_c1_stateswap_univpit.csv` (Phase 3 Phần A,
job `_153800`) — cột `state/r_bal/r_lag/r_dc/port_c1_stateswap/baseline_2book_prod` hằng ngày,
2014-08-05→2026-06-19. Script mới: `exp_dc3book_c1_rollingwindows_20260830.py` (window-level) +
1 script ad-hoc episode-level (không lưu file .py riêng, logic inline trong finding này — output
`exp_dc3book_c1_episode_breakdown.csv`).

## 1. Window-level (4 cửa sổ, khớp đúng ranh giới IS/OOS gốc)

W1 2014-16 + W2 2017-19 = IS 2014-19 gốc. W3 2020-22 + W4 2023-26 = OOS 2020+ gốc.

| Window | N BULL days | N episode | gross_BAL | gross_LAG | gross_DC | DC−LAG | Leader | Portfolio delta_pp (local) |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| W1 2014-16 | 0 | 0 | — | — | — | — | N/A | −0.40 |
| W2 2017-19 | 70 | 2 | 50.32% | 6.09% | **−2.92%** | **−9.01pp** | BAL | −0.65 |
| W3 2020-22 | 213 | 4 | 69.42% | 53.08% | 65.67% | **+12.59pp** | BAL | **+2.64** |
| W4 2023-26 | 139 | 4 | 8.96% | 20.46% | 33.33% | **+12.87pp** | DC | +0.94 |

`gross_*` = arithmetic annualization (mean daily return trong state=BULL AND window đó × 252,
đúng convention Phần B). N episode tổng = 0+2+4+4 = **10**, khớp đúng số Phần A.

**Đọc thoáng qua ở tầng window:** DC−LAG margin gần như GIỐNG HỆT nhau giữa W3 (+12.59pp) và W4
(+12.87pp) — trông như bằng chứng "ổn định 2 giai đoạn OOS độc lập", có vẻ PHẢN BÁC lo ngại
"1-2 lucky episode". **Đây là kết luận SAI do cách gộp che khuất** — xem mục 2.

## 2. Episode-level (10 episode BULL riêng biệt, compound return thật trong từng episode)

| Ep | Giai đoạn | N ngày | BAL% | LAG% | DC% | DC−LAG (pp) | Thắng |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2017-12-26→2018-02-26 | 39 | 12.46 | 4.41 | 1.86 | −2.55 | BAL |
| 2 | 2018-03-22→2018-05-08 | 31 | 1.32 | −2.72 | −2.65 | +0.07 | BAL |
| 3 | **2020-10-06→2020-12-25** | 59 | 27.74 | 11.37 | **29.08** | **+17.71** | **DC** |
| 4 | 2021-03-05→2021-07-23 | 98 | 15.60 | 20.79 | 22.84 | +2.06 | DC |
| 5 | 2021-08-23→2021-09-09 | 12 | 6.02 | 3.07 | 3.94 | +0.88 | BAL |
| 6 | 2021-10-26→2021-12-24 | 44 | 11.74 | 12.18 | 4.91 | −7.27 | LAG |
| 7 | **2024-01-24→2024-05-13** | 70 | 8.67 | 1.39 | **12.78** | **+11.38** | **DC** |
| 8 | 2025-03-07→2025-05-16 | 47 | 0.20 | 10.91 | 5.57 | −5.34 | LAG |
| 9 | 2025-09-22→2025-10-03 | 10 | −1.74 | 0.00 | −2.85 | −2.85 | LAG |
| 10 | 2026-01-28→2026-02-12 | 12 | −3.68 | −0.96 | 2.07 | +3.03 | DC |

**DC thắng LAG 6/10 episode tổng (5/8 episode OOS).** Nhưng magnitude cực kỳ lệch: tổng
(DC−LAG) trên 8 episode OOS ≈ **+19.6pp**, trong đó **riêng episode 3 (2020-10→12, COVID
recovery, 59 ngày) đóng góp +17.71pp = 90% của tổng đó.** Cộng thêm episode 7 (2024-01→05,
+11.38pp) thì 2 episode này ĐÃ VƯỢT 100% tổng (+29.1pp) — nghĩa là **6 episode OOS còn lại gần
như TRIỆT TIÊU LẪN NHAU** (3 dương nhỏ +2.06/+0.88/+3.03, 3 âm −7.27/−5.34/−2.85 → tổng ròng
≈ −9.5pp). Đây đúng là dạng "1-2 lucky episode kéo toàn bộ số lên" mà quant-skeptic lo ngại —
**KHÔNG PHẢI bị window-level làm lộ ra, mà bị window-level CHE KHUẤT**: gộp theo mean-per-day
trong cửa sổ 3 năm (W3 có 213 ngày BULL, episode 3 chiếm 59/213 ≈ 28% số ngày) khiến 1 episode
biên độ lớn kéo lệch trung bình cả cửa sổ, tạo ảo giác "ổn định qua 2 cửa sổ OOS độc lập".

**Tín hiệu gần nhất đảo chiều:** 2 episode gần nhất (2025-03→05, 2025-09→10) đều LAG thắng DC
(−5.34pp, −2.85pp) — dữ liệu mới nhất KHÔNG ủng hộ giả thuyết DC>LAG trong BULL, ngược lại.

## 3. Trả lời câu hỏi dispatch đặt ra

> "OOS +1.70pp có phân bổ đều qua các cửa sổ 2020+ hay tập trung vào 1 giai đoạn cụ thể (vd
> riêng 2020-2021 hậu COVID)?"

**Tập trung, không phân bổ đều — nhưng phức tạp hơn giả thuyết "chỉ riêng COVID".** Ở tầng
episode (đơn vị đúng để đo N độc lập, không phải window): 1 episode COVID (ep 3) đóng góp áp
đảo, CỘNG 1 episode khác không-COVID (ep 7, đầu 2024) đóng góp gần bằng — 2 episode này ĐÃ VƯỢT
100% tổng lợi ích ròng OOS vì các episode còn lại triệt tiêu lẫn nhau. Window-level 4-cửa-sổ
(yêu cầu chính của dispatch) tự nó **KHÔNG đủ để phát hiện ra điều này** — nó cho kết quả trông
"ổn định" (+12.6pp và +12.9pp margin ở W3/W4) chính vì phép gộp trung bình theo ngày làm loãng
sự tập trung episode. Phải hạ xuống tầng episode mới thấy rõ.

## 4. Kết luận cho câu hỏi mở-lại-C1 (điều kiện #3/4)

**KHÔNG xác nhận "OOS ổn định qua nhiều cửa sổ" — NGƯỢC LẠI, củng cố REFUTED gốc của
quant-skeptic.** Bằng chứng bổ sung lần này đi theo hướng CỦNG CỐ lo ngại "1-2 lucky episode",
không phải làm nó yếu đi. Thêm 1 phát hiện mới không có trong bản gốc: 2 episode GẦN NHẤT
(2025) đảo chiều so với kỳ vọng lịch sử — nếu có bất kỳ trọng số nào cho "recency", đây là tín
hiệu tiêu cực thêm.

**Không đề xuất mở lại C1 dựa trên phần bằng chứng này.** Đây là 1/4 điều kiện quant-skeptic
đặt ra khi REFUTED — 3 điều kiện còn lại (nếu có, xem finding gốc `Taylor_20260826...` REFUTED
plan live-25%) cần đánh giá độc lập, không tự động bù trừ cho phát hiện tiêu cực ở điều kiện
này.

## File output

- `exp_dc3book_c1_rollingwindows_20260830.py` — script window-level (4 cửa sổ).
- `exp_dc3book_c1_rollingwindows_metrics.csv` — kết quả window-level.
- `exp_dc3book_c1_episode_breakdown.csv` — kết quả episode-level (10 episode, compound return
  thật trong từng episode, không phải arithmetic-mean annualized).
