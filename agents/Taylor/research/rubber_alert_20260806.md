# Rà cảnh báo cao su RSS3 (2026-08-05) — job Taylor_20260806_081258

**Kết luận 1 dòng:** Cảnh báo ALERT là **dương tính giả do lỗi code**, không phải tín hiệu thị trường.
RSS3 2,596 USD/kg **KHÔNG** phá đáy 52 tuần — nó nằm ở **phân vị 69%** của biên 52 tuần thật.
Không có vị thế cao su nào đang mở và không có model production nào cần cập nhật.

---

## 1. Lỗi cốt lõi: "phá biên 52 tuần" tính trên cửa sổ 6,6 TUẦN

`rubber_weekly.py:162-167` tính biên 52 tuần **chỉ trên các dòng `src != "wb_seed"`**:

```python
if len(real) >= 30:                                    # <-- đếm SỐ DÒNG, không phải số tuần
    win = real[real.index >= latest_dt - timedelta(days=365)]["rss3_usdkg"]
    if latest >= win.max():   band = "high"
    elif latest <= win.min(): band = "low"
```

Chuỗi "real" bắt đầu **2026-06-19** → tại ngày cảnh báo có **33 dòng trải 46 ngày = 6,6 tuần**.
Cổng `len(real) >= 30` đếm **số dòng**; vì feed ghi theo NGÀY nên nó mở sau ~6 tuần, không phải 52.
Toàn bộ cửa sổ đó nằm gọn trong phần ĐỈNH của nhịp tăng (2,60–2,92) → bất kỳ giá nào dưới 2,612
đều bị gắn nhãn "đáy 52 tuần mới".

**Biên 52 tuần THẬT** (chuỗi tháng World Bank `data/rubber_monthly.csv`):

| | |
|---|---|
| Biên 52 tuần thật (2025-07 → 2026-07) | **2,00 – 2,86** USD/kg |
| Đáy thật gần nhất | **2,00** (2025-10); 2025-09/11/12 = 2,11/2,03/2,06 |
| Giá hiện tại 2,596 | **phân vị 69%** của biên đó — cao hơn đáy thật **+30%** |

⇒ Tuyên bố "đáy mới" sai **~30%** so với đáy thật.

### Hệ quả trực tiếp: nếu không có lỗi này thì đã KHÔNG có cảnh báo nào

Chạy lại đúng `classify()` của chính script, chỉ bỏ `band`:

| | Tier | Lý do |
|---|---|---|
| Như đang chạy | **ALERT** → Bill + Telegram | `phá biên 52 tuần (đáy mới)` |
| Bỏ band artifact | **INFO** (im lặng) | *không có lý do nào* |

Ngưỡng: WoW −6,6% < ALERT 12% **và** < WATCH 7%; 4 tuần −7,4% < 15%; 3 tháng −3,5% < 18%.
**Cả ba trục biến động đều dưới ngưỡng WATCH.** Band artifact là lý do DUY NHẤT được in ra
(xác nhận trong `data/rubber_weekly_2026-08.log`) và nó đã nhảy thẳng INFO → ALERT, bỏ qua WATCH.

## 2. Cảnh báo đứng trên ĐÚNG MỘT giá, và giá đó mâu thuẫn với nguồn thứ hai

| | |
|---|---|
| Biến động 1 ngày 2026-08-03 → 08-04 | **−6,95%** (2,790 → 2,596) |
| z-score trên chính chuỗi real | **−3,22** |
| Ngày giảm mạnh thứ nhì trong toàn chuỗi | −3,19% (**bằng chưa tới một nửa**) |
| Spot Trung Quốc (SunSirs-586) **cùng ngày** | **+1,52%** (16.433 → 16.683 RMB/t) |
| TSR20 cùng cửa sổ | 2,163 → 2,244 (+3,7%) → 2,103 (−6,3%) — khứ hồi bất thường |

Hai thị trường của cùng một hàng hoá lệch **8,5 điểm phần trăm trong một ngày**, kèm cú khứ hồi
của TSR20, là **cờ chất lượng dữ liệu** — chưa đủ để khẳng định print sai, nhưng đủ để cấm coi
một print đơn lẻ chưa xác nhận là bằng chứng đảo chiều chu kỳ.

## 3. Ngay cả khi giá 2,596 là thật: chưa khác gì nhịp chỉnh đã xảy ra VÀ đã hồi trong cùng nhịp tăng

| Nhịp chỉnh trong cùng up-leg 2026 | Mức |
|---|---|
| 2026-06-23 → 07-01 | **−7,8%**, rồi hồi **lên đỉnh mới 2,919** (07-16) |
| 2026-07-16 → 08-04 (hiện tại) | **−11,1%** |

Nhịp hiện tại lớn hơn một nấc, **cùng bậc độ lớn**, không phải một sự kiện khác loại về cấu trúc.
Tín hiệu THÁNG cũng chưa xác nhận: tháng 7 mới −2,8% MoM.

## 4. Base rate 20 năm — hướng bearish nhưng N quá nhỏ để hành động

Nguồn: `data/rubber_monthly.csv` (World Bank, 2006-04 → 2026-07, 244 tháng).

Điều kiện gần nhất với hiện tại (giảm 1 tháng ≤ −6% khi đà 6 tháng ≥ +20%): **n = 3**
— fwd 3m median −9,5% (0/3 tăng), fwd 12m median −25,1%.

**Nhưng cả 3 đều nằm ở/gần ĐỈNH CHU KỲ**, còn hiện tại thì không:

| | Giá | Phân vị 20 năm | fwd 12m |
|---|---|---|---|
| 2010-05 | 3,67 | 92% | **+39,5%** |
| 2011-03 | 5,42 | 98% (đỉnh mọi thời đại 6,26) | −27,5% |
| 2017-03 | 2,35 | 66% | −25,1% |
| **2026-07** | **2,78** | **78%** (= 44% của đỉnh 2011) | ? |

Mở rộng (n=6, đà 6 tháng ≥ +10%) thì **MỨC GIÁ mới là biến phân tách**, không phải cú giảm:
ở mức cao (≥ phân vị 80) fwd12m median **−27,1%** (n=3); ở mức trung/thấp **+8,3%** (n=3).

⚠️ **N = 3 và 6, cửa sổ tháng CHỒNG LẤN → không phải sự kiện độc lập.** Đây là mức **giai thoại**,
theo kỷ luật §18/`quant-research` **không đủ làm căn cứ cho bất kỳ quyết định vị thế nào**. Ghi lại
để đối chiếu về sau, không phải để hành động.

## 5. Rà production (yêu cầu #1) — không có gì cần cập nhật

| Kiểm tra | Kết quả |
|---|---|
| Vị thế cao su đang mở (broker DNSE, 2026-08-06) | **KHÔNG** — SpaceX 21 mã, ZaloPay 16 mã, 0 mã cao su |
| GVR/PHR/DPR/DRI/HRC trong tín hiệu BAL/LAG/CAPIT | **Không xuất hiện** |
| TRC | Đã **auto-exclude** khỏi LAG: `RATING_FAIL 8L=4 (≥4)`, policy user 2026-07-27 |
| CAPIT | `capit_signal_today=false`, `capit_fired=false`, `capit_dd_excluded=[]` |
| Model production đọc giá cao su | **Không có.** `rubber_weekly.py` là feed cảnh báo, không model nào tiêu thụ |
| `dri_q3_nowcast.py`, `dri_q3_volume_model.py` | Script **nghiên cứu ad-hoc**, KHÔNG có trong crontab |

**Giả định giá cao su cũ duy nhất tìm được:** `dri_q3_volume_model.py:38` hardcode
`priceQ3 = 2.73  # Q3'26 spot` (viết 2026-06-27). Đối chiếu thực tế:
Q3 chạy = (T7 2,78 + Aug-to-date 2,693)/2 = **2,736 vs giả định 2,730 — lệch 0,2%.**
⇒ **Vẫn đúng, không cần sửa.** (`dri_q3_nowcast.py` vốn đã chạy kịch bản 2,45/2,60/2,73 — mức
2,60 hiện tại nằm sẵn trong dải kịch bản.)

## 6. Kết luận & khuyến nghị

**Về vị thế (input cho DollarBill): KHÔNG hành động.** Không phải vì "đã cân nhắc và quyết định
giữ", mà vì **không có vị thế cao su nào để hành động**, và cảnh báo kích hoạt nó là dương tính giả.

**Về đánh giá chu kỳ:** **CHƯA đủ căn cứ gọi đảo chiều chu kỳ.** Bằng chứng hiện có = một print
đơn lẻ, chưa xác nhận, mâu thuẫn với nguồn thứ hai cùng ngày, biên độ tương đương một nhịp chỉnh
đã hồi trong cùng up-leg. Cũng **không** khẳng định ngược lại rằng xu hướng tăng còn nguyên —
đơn giản là chưa có dữ liệu để phán. Đọc lại sau 3–5 phiên có giá.

**Về báo cáo DRI của Mike:** khuyến nghị "chờ tín hiệu tạo đáy" có thể vẫn hợp lý vì lý do khác
(dải kịch bản DCF quá rộng: fair value 13.430 → 35.510), nhưng **bằng chứng cụ thể được viện dẫn
để đảo khuyến nghị — "RSS3 phá đáy 52 tuần" — là không đứng vững.** Nếu đó là lý do chính thì
nên xem lại; đừng neo quyết định DRI vào con số đó.

### Việc cần làm (KHÔNG tự sửa — research-only, cần quant-skeptic + user duyệt)

1. **Sửa cổng band** `rubber_weekly.py:164`: đổi `len(real) >= 30` (đếm dòng) sang điều kiện
   **phủ theo lịch** — ví dụ yêu cầu chuỗi real trải ≥ 300 ngày trước khi bật nhãn "52 tuần";
   hoặc ghép chuỗi tháng WB vào cửa sổ band để có biên 52 tuần thật ngay. Đây đúng dạng lỗi
   `coding_guidelines §14`: một cổng/dung sai rộng hơn rủi ro thật, che một giả định sai suốt
   nhiều tuần.
2. Cân nhắc yêu cầu **xác nhận 2 print** (hoặc đối chiếu spot TQ) trước khi bắn ALERT tier — cảnh
   báo hiện tại có thể nâng thẳng INFO → ALERT từ một print duy nhất.
3. Trong lúc chưa sửa: **mọi nhãn "phá biên 52 tuần" từ feed này phải coi là chưa đáng tin**, đối
   chiếu tay với `data/rubber_monthly.csv`.

### Mức độ tin cậy

| Kết luận | Tin cậy | Căn cứ |
|---|---|---|
| "Đáy 52 tuần" là artifact; không có band thì tier = INFO | **CAO** | Cơ học, tái lập bằng chính `classify()` của script |
| Không có vị thế/model production cần cập nhật | **CAO** | Đối chiếu vị thế broker thật + golive status + crontab |
| Giả định Q3 DRI 2,73 vẫn đúng | **CAO** | 2,736 vs 2,730 |
| Chưa phải đảo chiều chu kỳ | **TRUNG BÌNH** | Vắng bằng chứng đảo chiều; bản thân một print thì thật sự chưa rõ |
| Hướng base rate (mức giá > cú giảm) | **THẤP** | n=3/n=6, cửa sổ chồng lấn, không độc lập |
