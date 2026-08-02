# 2026-08-02 — Saga "PE có look-ahead giá điều chỉnh": 6 tuần một phép nhân sai + lần thứ 2 fleet suy diễn nhầm từ một quan sát ĐÚNG

**Trạng thái**: ĐÓNG (code đã khôi phục đúng, self-check 2 chiều PASS, quant-skeptic gate ở Bước 5)
**Mức độ**: MEDIUM — sai số liệu trên màn hình lọc human-facing; **đường giao dịch LIVE không bị
nhiễm** (chứng minh bên dưới). Không mất tiền, không lệnh sai.
**Job liên quan**: `Taylor_20260802_042110` (suy diễn sai) → `Taylor_20260802_054825` (bác bỏ) →
`Taylor_20260802_063752` (khôi phục + incident này).

## 1. Chuyện gì đã xảy ra

**Quan sát ĐÚNG** (nhiều lần, nhiều agent): hệ số `F = Price/Close` trong `tav2_bq.ticker` giảm đơn
điệu theo thời gian — trung vị **2,31 @2014 → 1,00 @2026**. `Close` là chuỗi giá **đã điều chỉnh lùi**
theo chia/thưởng/cổ tức; `Price` là giá thô đã khớp thật ngày đó.

**Suy diễn SAI từ quan sát đúng đó**: "vậy `PE` lưu trong bảng chắc cũng ở cơ sở `Close` đã điều
chỉnh ⇒ `1/PE` bị nhiễm look-ahead ⇒ phải nhân lại `Price/Close` để về giá thô."

**Hệ quả trong code**: phép nhân `PE ← PE · (Price/Close)` được thêm vào `rating_8l.py`
(`_pe_adj_factor`) kèm comment khẳng định `PE_stored = Close_adj/EPS`.

**Bác bỏ (job 054825, bằng chứng cứng)**: trong MỘT kỳ báo cáo, `EPS_ttm` là hằng số, nên 2 giả
thuyết cho dự đoán loại trừ nhau. Trên 2014-2021 (1.419.351 dòng / 23.067 cặp ticker×ID_Release):
`PE/Price` hằng số trong **93,1%** số kỳ, `PE/Close` chỉ **11,0%** (PB: 94,6% vs 12,6%; PCF: 86,9%
vs 20,3%). Verify tay độc lập: VNM 2015-06-30 `Price=113.000`, `PE=18,116` ⇒ EPS hàm ý **6.237,5**
= đúng chính xác `NP_ttm/OShares`; tính từ `Close=32.510` ra EPS 1.794,5 (vô lý). ⇒ **`PE` vốn đã
point-in-time đúng; nhân `Price/Close` là ĐƯA look-ahead VÀO** (hệ số phụ thuộc sự kiện xảy ra SAU
ngày t). A/B NAV custom30V: phép "sửa" làm **xấu −1,70pp CAGR / −0,19 Calmar / −160B NAV**.

**Khôi phục (job này)**: gỡ phép nhân, khôi phục `earn_yield = 1/PE`, thay comment sai bằng cảnh báo
ngược chiều + trỏ bằng chứng.

## 2. Đính chính quan trọng: lỗi KHÔNG sinh ra hôm nay — nó đã sống 6 tuần

Dispatch giả định job `Taylor_20260802_042110` (sáng nay) đã tự "sửa" `rating_8l.py`. **Sai** — khảo
cổ git:

```
git log -S "_pe_adj_factor" --all -- WorkingClaude/rating_8l.py   → 3c54745 (2026-06-24), a1a4709
git show 3c54745^:WorkingClaude/rating_8l.py | grep _pe_adj_factor → không có
git log --since=2026-08-01 --all -- WorkingClaude/rating_8l.py     → RỖNG
```

Phép nhân vào file **2026-06-24**, sống **~6 tuần**. Job 042110 hôm nay không chạm file; nó **trích
dẫn** đoạn code đó làm chỗ dựa ("script duy nhất có phép sửa này") và **thừa hưởng** tiền đề sai.
Đây là điểm nặng nhất của saga: một khẳng định sai nằm trong comment code đủ lâu để **được đọc như
bằng chứng** bởi công việc sau đó.

## 3. Bán kính ảnh hưởng thật (đo bằng đọc code, không suy đoán)

| Thành phần | Nhiễm? | Vì sao |
|---|---|---|
| **Rating 8L 1-5** (gate LAG ≤3, gate custom30V) | **KHÔNG** | `rate_row()` không dùng PE/PB/PCF; và nó chạy ở dòng ~500 **trước** phép nhân (dòng 523-524 chỉ đụng `out`, không đụng `df`) |
| **`tav2_bq.fa_ratings_8l`** (bảng `custom_basket.rating_asof` bisect) | **KHÔNG** | Bảng chỉ chứa `ticker,time,route,rating,tier`, do `rating_8l_history.py` sinh — script này chưa từng có phép nhân |
| `data/rating_8l.csv` cột `PE`/`earn_yield`; screener `value_score`/`zone`/top30/buynow/`rank_8l.md` | **CÓ** | nhưng chỉ snapshot của ngày chạy |

⇒ Lo ngại "rebuild lịch sử sẽ nhiễm" ghi ở job 054825 **được thu hẹp**: bảng ratings lịch sử không
đi qua script này, nên **không có đường nào để lỗi chạm vốn thật**. Thiệt hại thực tế: số PE/yield
sai trên màn hình lọc con người đọc — và trong 6 tuần đó `Price ≈ Close` nên sai số ~0.

## 4. Vì sao sống được 6 tuần

1. **Tự vô hiệu ở hiện tại**: `F ≡ 1,0` cho **859/859** mã ngày 2026-07-31 ⇒ phép nhân sai không
   tạo ra triệu chứng nào ở live. Lỗi chỉ hiện hình trên dữ liệu cũ.
2. **Comment tự khẳng định**: dòng `# PE_stored = Close_adj/EPS` đọc như một sự thật đã kiểm chứng.
   Không ai kiểm lại vì nó *nghe* đúng và khớp với quan sát F giảm đơn điệu.
3. **Verify cũ chạy trên dữ liệu gần đây**: `Winston_20260717_063633` từng kiểm và không thấy vấn
   đề — vì trên dữ liệu gần đây `F≈1` nên **hai giả thuyết loại trừ nhau lại cho cùng một kết quả**.

## 5. BÀI HỌC (điểm chính của incident này)

> **Kiểm định một giả thuyết về XU HƯỚNG THEO THỜI GIAN thì phải test trên dữ liệu CŨ. Dữ liệu gần
> đây có thể làm hai giả thuyết đối nghịch trông giống hệt nhau.**

Đây là **lần thứ 2** fleet vấp đúng hình dạng này (lần trước: `Winston_20260717_063633`). Cụ thể hoá
thành 3 thói quen:

1. **Điểm test phải nằm ở chỗ hai giả thuyết TÁCH RA.** Ở đây `F=Price/Close`: 2014 (F≈2,3) tách rõ,
   2026 (F≡1,0) không tách gì. Test ở 2026 = không test.
2. **Ưu tiên phép kiểm ĐỊNH DANH thay vì phép kiểm "nghe hợp lý".** Cả 2 lần đóng được đều nhờ một
   đại lượng bất biến trong kỳ: `EPS_ttm` hằng số ⇒ `PE/Price` phải hằng số nếu PE ở cơ sở Price
   (93,1% vs 11,0% — không cần diễn giải). Tương tự khi đo lens `ps` ở job này: đối chiếu trực tiếp
   `Price·OShares/Rev_ttm` với `PS` đã lưu ⇒ 99,7% khớp vs 11,9% (Close).
3. **Comment khẳng định về CƠ SỞ DỮ LIỆU phải kèm bằng chứng hoặc không được viết.** Comment sai ở
   đây không chỉ gây hiểu nhầm — nó **được tái sử dụng như bằng chứng** 6 tuần sau. Comment mới đã
   viết theo chuẩn này (nêu số liệu + job + file bằng chứng).

**Đã đẩy ra "công cụ" ở mức có thể** (theo chính sách enforcement của `coding_guidelines.md`): cảnh
báo NGƯỢC chiều đã ghi vào `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` mục **"Bẫy (4)"**
(job 054825) — tức là chốt chặn nằm ở nơi §9 bắt buộc phải đọc trước khi wire nguồn dữ liệu, không
chỉ nằm trong văn xuôi incident này. Không viết lint rule: pattern "nhân giá điều chỉnh vào tỷ số
định giá" không có dạng cú pháp cơ học đủ chính xác (cùng lý do đã ghi ở §12/§16 — rule nhiễu làm hỏng
niềm tin vào cả cổng nhanh hơn là không có rule).

## 6. Việc còn MỞ (đã đo, chưa sửa — chờ Mike/user quyết)

Lens `ps` trong `rating_8l.py` dùng `Close·OShares/Revenue_ttm` — **sai cơ sở cùng họ** (đo ở job
này: `PS` lưu khớp cơ sở `Price` 99,7% vs `Close` 11,9% trên 7.321 dòng 2014-2016). Tác động LIVE
hôm nay = **0** (F≡1); tác động nếu tính lùi lịch sử: `sales_yield` lệch trung vị 90-131%, đổi
11-15/30 tên rẻ nhất. Đề xuất đổi sang `Price`, ưu tiên thấp. Chi tiết + số liệu:
`mike/agents/Taylor/research/rating8l_pe_adj_removal_20260802.md` (Bước 4).

## 7. Tham chiếu

- `mike/agents/Taylor/research/pe_priceadj_refutation_ab_20260802.md` — bằng chứng bác bỏ + A/B NAV
- `mike/agents/Taylor/research/rating8l_pe_adj_removal_20260802.md` — thực thi + self-check 2 chiều
- `mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` — "Bẫy (4)" (chốt chặn chuẩn tắc)
- `coding_guidelines.md` §9 (tra data_registry trước khi wire nguồn), §18 (skill `quant-research`)
