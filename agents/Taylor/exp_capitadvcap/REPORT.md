# DỪNG LẠI THEO ĐÚNG CHỈ ĐẠO — selfcheck cap %ADV cho kết quả KHÁC dự đoán (1/14, không phải 0/14)

Job `Taylor_20260720_170223` · 2026-07-21 · script: `selfcheck_adv_cap.py` · dữ liệu: `adv_cap_selfcheck.csv`
**CHƯA sửa một dòng nào trong production** (`pt_v23_audit_2014.py`, `golive_recommend_v23.py` nguyên vẹn).

Dispatch nói rõ: *"Nếu selfcheck cho kết quả KHÁC (cap kích hoạt ở event nào đó), DỪNG LẠI và báo cáo
trước khi tiếp tục."* → cap kích hoạt ở **1/14 event**. Đây là báo cáo đó.

---
## 1. Kết quả selfcheck

Công thức implement đúng như đã chốt, X=0,10 · D=2 · ADV20 = median 20 phiên **trước** ngày washout:

| sleeve (tỷ VND) | event bị cap | vị thế bị cap |
|---|---|---|
| **0,38 (mức tham chiếu của đề xuất)** | **1/14** | **1/66** |
| 0,75 | 1/14 | 2/66 |
| 1,50 | 2/14 | 4/66 |
| 3,75 | 9/14 | 17/66 |
| 7,50 | 12/14 | 26/66 |

Ca duy nhất ở mức 0,38 tỷ: **NNC, event 2016-01-18** — ADV20_pre = 0,335 tỷ → cap 0,067 tỷ/tên,
trong khi equal-weight đòi 0,38/5 = 0,076 tỷ. Vượt **0,009 tỷ (~9 triệu VND)**.

## 2. Nguyên nhân — KHÔNG phải lỗi implement, mà là hai CỬA SỔ ADV khác nhau

Con số "14/14 đủ capacity ở 0,38 tỷ" trong `exp_capitexit/RESULT.md §3b` được tính bằng ADV20
**SAU khi vào** (`axis3_liquidity.py`: `k ∈ [1,20]`). Công thức đã chốt lại dùng ADV20 **TRƯỚC**
ngày washout — vì live không thể biết ADV tương lai (phải nhân quả). Hai cửa sổ lệch nhau, và
NNC 2016 rơi đúng vào khe:

| ticker (event 2016-01-18) | ADV20 **PRE** (công thức chốt) | ADV ngày washout | ADV20 **POST** (job trước) |
|---|---|---|---|
| **NNC** | **0,335** | 0,138 | **0,431** |
| DRC | 0,472 | 2,885 | 3,841 |
| LIX | 0,864 | 7,729 | 2,566 |
| DPM | 22,98 | 9,20 | 10,60 |
| VNM | 45,14 | 44,67 | 38,51 |

→ capacity sleeve (equal-weight, n=5): **PRE 0,335 tỷ** vs **POST 0,431 tỷ**. Ngưỡng 0,38 nằm
đúng giữa hai số → 0/14 (POST) đổi thành 1/14 (PRE). **Tiền đề dispatch đúng với dữ liệu nó được
suy ra, chỉ là suy ra từ biến thể ADV khác với biến thể cuối cùng được chốt.** Tôi đã đối chiếu
lại panel gốc để xác nhận điều này, không phải suy đoán.

Ghi chú phụ đáng lưu ý: NNC là ca **ngược** với §3a — ADV ngày washout (0,138) THẤP hơn cả hai
cửa sổ. Tức 2016-01-18 với NNC không phải volume spike mà là ngày cạn thanh khoản. Lý do chọn
cửa sổ PRE (nhân quả, implement được live) vẫn đúng, nhưng nó không đơn thuần "bảo thủ hơn" như
lập luận §3a ngụ ý — nó chỉ là **khác**, có tên cao hơn có tên thấp hơn.

## 3. Tác động thực tế: bằng 0 với rổ hiện tại

Rổ CAPIT 2026-07-20 (NCT, PVT, SAB, VNM — PNJ đã bị due-diligence gate loại), ADV20 tới phiên
2026-07-20:

| ticker | ADV20 (tỷ) | cap/tên (tỷ) |
|---|---|---|
| NCT | 2,40 | 0,480 |
| SAB | 23,76 | 4,75 |
| PVT | 48,50 | 9,70 |
| VNM | 138,78 | 27,76 |

Cap **không kích hoạt tới tận sleeve 1,5 tỷ** (n=4 → 0,375 tỷ/tên < cap NCT 0,480 tỷ). Sleeve
thực tế hiện nay ~0,24–0,49 tỷ. **Nếu CAPIT fire hôm nay, cap có hay không có đều cho kết quả
y hệt.** Kết luận "dormant safeguard" của dispatch VẪN ĐÚNG cho hiện tại — chỉ sai ở chi tiết
"0/14 lịch sử".

## 4. Vấn đề kiến trúc phát hiện thêm — cap KHÔNG biểu diễn được trong backtest engine

Cần nêu trước khi bàn tiếp, vì nó quyết định "wire ở đâu":

- **`golive_recommend_v23.py` (đường LIVE)**: sizing là **per-name** (`weight_pct = capit_size /
  len(basket)`, mỗi ticker một dòng rec) → cap per-name gắn vào được tự nhiên. NHƯNG script này
  **không biết NAV** (nó là advisory, phát ra % chứ không phải VND). Muốn áp cap phải hoặc (a)
  truyền NAV_book_LAG vào, hoặc (b) phát ra **hạn mức VND tuyệt đối/tên** (`X·ADV20·D`) rồi để
  DollarBill áp `min(weight×NAV, cap_vnd)` lúc lập plan. (b) tương đương toán học, không cần
  golive biết NAV, và tôi nghiêng về (b) — nhưng nó đẩy phần enforce sang plan-generator (LLM),
  nên nếu chọn (b) thì phải enforce cứng ở `bot_execute.py` giống `excluded_tickers`, chứ không
  dựa vào DollarBill nhớ.
- **`pt_v23_audit_2014.py` (backtest)**: sizing là **tier-level** — `tw2[pt] = wt / len(names)`,
  một trọng số duy nhất dùng chung cho mọi tên trong tier. **Không có vector trọng số per-name.**
  Cap per-name không implement được nếu không sửa engine `shn` (thêm per-name weight). Đây là
  thay đổi sâu vào lõi backtest đã pin R3 — rủi ro cao hơn nhiều so với giá trị của một safeguard
  ngủ. Khuyến nghị: **không đụng backtest engine**, chỉ wire live + giữ selfcheck này làm bằng
  chứng parity (ở mức sleeve hiện tại chênh lệch = 0).

## 5. Ba lựa chọn — cần quyết định trước khi tôi viết tiếp

| | phương án | hệ quả |
|---|---|---|
| **A** | Chấp nhận 1/14, wire nguyên công thức đã chốt | Trung thực nhất với spec đã duyệt. Backtest lịch sử lệch **0,009 tỷ ở đúng 1 vị thế năm 2016** — nhỏ tới mức không đo được ở NAV path, nhưng KHÔNG còn tuyên bố được "zero thay đổi historical". Live hôm nay: zero. |
| **B** | Giữ nguyên công thức, chỉ **sửa lại tuyên bố** trong tài liệu từ "0/14" thành "1/14, lệch 9 triệu VND" | Giống A về code, khác ở chỗ không giả vờ dormant tuyệt đối. Đây là phương án tôi **khuyến nghị**. |
| **C** | Nới X hoặc D (vd D=3) để ép về 0/14 | **Phản đối.** X/D là quy ước ngành, không có dữ liệu hiệu chỉnh; chỉnh nó để khớp một con số kỳ vọng chính là fit tham số vào 1 quan sát duy nhất — đúng thứ multiple-testing discipline cấm. |

Chênh lệch A/B vs C là ~9 triệu VND ở một event 2016. Cái đáng giữ không phải con số đó mà là
**không chỉnh tham số cho vừa kỳ vọng**.

## 6. Trạng thái self-check 0 VND
`self-check 0 VND: FAIL` — theo đúng nghĩa đen: cap tái phân bổ 0,008975 tỷ VND (≈9 triệu) trên
toàn 14 event. Đây KHÔNG phải bug NAV-path (backtest chưa hề bị sửa); nó chỉ là đại lượng đo
chính xác mức lệch nếu về sau cap được đưa vào backtest. Ghi lại nguyên vẹn thay vì làm tròn về 0.

## 7. Việc chưa làm (đang chờ chỉ đạo)
- ❌ Wire vào `golive_recommend_v23.py` — chờ chốt phương án A/B/C **và** chốt (a) hay (b) ở §4.
- ❌ Dispatch quant-skeptic — chưa có diff production để verify. Sẽ chạy ngay sau khi có code.
- ✅ Selfcheck + chẩn đoán nguyên nhân + đo tác động rổ hiện tại — xong, trong file này.
