# 2026-08-02 — Saga "PE có look-ahead giá điều chỉnh": 6 tuần một phép nhân sai + lần thứ 2 fleet suy diễn nhầm từ một quan sát ĐÚNG

**Trạng thái**: ĐÓNG (code đã khôi phục đúng, self-check 2 chiều PASS, quant-skeptic gate ở Bước 5)
**Mức độ**: MEDIUM — sai số liệu trên màn hình lọc human-facing; **đường giao dịch LIVE không bị
nhiễm** (chứng minh bên dưới). Không mất tiền, không lệnh sai.
**Job liên quan**: `Taylor_20260802_042110` (suy diễn sai) → `Taylor_20260802_054825` (bác bỏ) →
`Taylor_20260802_063752` (khôi phục + incident này) → `Taylor_20260802_081308` (**Phần 2**: lens
`ps`, ngược chiều) → `Taylor_20260802_141725` + `_150945` (**Phần 3**: rổ parking custom30V, re-pin
R3) → `Taylor_20260802_154231` + `_161942` (**Phần 4**: đóng nhánh CAPIT-membership).

> **File này có 4 phần.**
> - **Phần 1 (§1-§7)** — `PE` bị nhân thừa `Price/Close`. Human-facing, không chạm LIVE.
> - **Phần 2 (§8-§13)** — lens `ps` dùng thiếu, phải đổi `Close`→`Price`. **NGƯỢC CHIỀU phần 1** —
>   đọc §8 trước khi kết luận "cột nào đúng" ở chỗ khác trong repo.
> - **Phần 3 (§14-§19)** — rổ parking custom30V: lần đầu cùng họ lỗi **chạm số pin** ⇒ **re-pin R3
>   27,60% → 27,24%** (số cũ bị lỗi thổi phồng).
> - **Phần 4 (§20-§27)** — đóng khoảng mở cuối (nhánh CAPIT-membership): **gap = 0,00pp**, số pin
>   **không đổi**. Lý do là **bất biến cơ cấu** (R3 không đọc bảng đó), KHÔNG phải "đo ra ~0" —
>   §21 giải thích vì sao phân biệt này quan trọng.

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

## 6. Việc còn MỞ (đã đo, chưa sửa — chờ Mike/user quyết) → **ĐÃ ĐÓNG, xem Phần 2 (§8)**

Lens `ps` trong `rating_8l.py` dùng `Close·OShares/Revenue_ttm` — **sai cơ sở cùng họ** (đo ở job
này: `PS` lưu khớp cơ sở `Price` 99,7% vs `Close` 11,9% trên 7.321 dòng 2014-2016). Tác động LIVE
hôm nay = **0** (F≡1); tác động nếu tính lùi lịch sử: `sales_yield` lệch trung vị 90-131%, đổi
11-15/30 tên rẻ nhất. Đề xuất đổi sang `Price`, ưu tiên thấp. Chi tiết + số liệu:
`mike/agents/Taylor/research/rating8l_pe_adj_removal_20260802.md` (Bước 4).

**Cập nhật cùng ngày**: user đã duyệt, sửa xong trong job `Taylor_20260802_081308` — xem **§8**.

## 7. Tham chiếu

- `mike/agents/Taylor/research/pe_priceadj_refutation_ab_20260802.md` — bằng chứng bác bỏ + A/B NAV
- `mike/agents/Taylor/research/rating8l_pe_adj_removal_20260802.md` — thực thi + self-check 2 chiều
- `mike/agents/Taylor/research/rating8l_ps_price_basis_20260802.md` — **Phần 2** (lens `ps`)
- `mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` — "Bẫy (4)" (chốt chặn chuẩn tắc)
- `coding_guidelines.md` §9 (tra data_registry trước khi wire nguồn), §18 (skill `quant-research`)

---

# PHẦN 2 — lens `ps`: cùng họ lỗi, **NGƯỢC CHIỀU** (job `Taylor_20260802_081308`)

## 8. Chuyện gì đã xảy ra (phần 2)

**Trạng thái**: ĐÓNG — sửa xong, self-check 2 chiều + 2 negative control PASS, quant-skeptic
**CONFIRMED (confidence high)**, đã commit.
**Mức độ**: LOW — thấp hơn phần 1. Chỉ nhiễm màn hình lọc human-facing; **tác động LIVE = 0**,
**ZERO NAV impact**, không đụng rating 8L (1-5) lẫn bảng `fa_ratings_8l`.

Cùng ngày, sau khi đóng phần 1, kiểm tra tiếp §6 và xác nhận lens `ps` sai cơ sở giá — **nhưng
theo chiều ngược lại**, và đây là điểm dễ hiểu nhầm nhất của cả saga:

| | Phần 1 — `PE` | Phần 2 — `ps` |
|---|---|---|
| Cột này lấy giá từ đâu | **Đã có sẵn** trong `ticker_financial`, vốn ĐÃ ở cơ sở `Price` (PIT) đúng | **Tự dựng** vốn hoá trong `rating_8l.py`, nên phải tự chọn cơ sở |
| Lỗi là gì | **Nhân thêm** `Price/Close` vào một số vốn đã đúng | Dùng `Close` (đã điều chỉnh) nhân `OShares` (PIT) — **trộn 2 cơ sở** |
| Phép sửa | **Gỡ** phép nhân, về `1/PE` | **Đổi** `Close` → `Price` |
| Hướng | Bỏ bớt `Price/Close` | Thêm vào `Price` |

> **Bài học cốt lõi của phần 2**: cùng một quan sát đúng (`F=Price/Close` giảm đơn điệu) dẫn tới
> **hai phép sửa ngược nhau** ở hai chỗ khác nhau — vì câu hỏi quyết định KHÔNG phải "cột nào đã
> điều chỉnh", mà là "**đại lượng này đã ở cơ sở nào rồi?**". Trả lời câu đó bằng phép kiểm định
> danh, đừng suy từ tên cột.

## 9. Khảo cổ git — không có comment sai, chỉ chọn nhầm cột

`git log -S'out["ps"] = np.where' -- rating_8l.py` → **duy nhất** `c9cc670` (2026-06-21, commit
checkpoint gộp) ⇒ lens `ps` có trước mốc đó, **không commit nào giải thích vì sao chọn `Close`**.
Khác phần 1 ở điểm quan trọng: phần 1 có comment **khẳng định sai** (`PE_stored = Close_adj/EPS`)
bị tái sử dụng như bằng chứng 6 tuần sau; ở đây comment gốc nói *"current-price PS =
mktcap/TTM-revenue"* — **ý đồ ĐÚNG**, chỉ lấy nhầm cột. Tức là: lỗi ít độc hại hơn (không lan
truyền thành tiền đề sai cho công việc khác), nhưng cũng **khó bị phát hiện hơn** vì đọc comment
không thấy gì bất thường.

## 10. Bằng chứng (tự đo lại trong job này, không copy số job trước)

**Phép định danh** — `PS` lưu trong `ticker_financial` ở cơ sở nào? (2014-01-01→2016-12-31,
`n = 7.377`):

```
Price·OShares/Rev_ttm khớp PS lưu (sai số <2%):  98,9%   | sai số tương đối trung vị: 0,0000
Close·OShares/Rev_ttm khớp PS lưu (sai số <2%):  11,8%   | sai số tương đối trung vị: 0,5261
```

**Tái lập công thức `rating_8l` trên 3 ngày cắt**:

| Ngày | n | F=Price/Close (trung vị) | \|sales_yield lệch\| trung vị | Spearman(fix,bug) | Top-30 rẻ nhất đổi |
|---|---|---|---|---|---|
| 2014-06-30 | 589 | 2,308 | **56,7%** | 0,889 | **15/30** |
| 2015-06-30 | 620 | 2,074 | 51,8% | 0,907 | 10/30 |
| 2016-06-30 | 702 | 1,906 | 47,5% | 0,909 | 13/30 |

> **Đối chiếu với §6 (90-131%) — KHÔNG mâu thuẫn, khác mẫu số**: §6 báo `sy_bug/sy_fix − 1 = F−1`;
> bảng trên báo `|sy_fix/sy_bug − 1| = 1 − 1/F`. Kiểm: F=2,308 ⇒ F−1 = 130,8% ≈ 131% ✓ và
> 1−1/F = 56,7% ✓. Chênh nhỏ còn lại (98,9% vs 99,7%; n 7.377 vs 7.321) do job này thêm điều kiện
> lọc `Price > 0`. **Ghi lại đối chiếu này ngay trong incident** vì hai con số cùng mô tả một sự
> kiện mà nhìn qua tưởng đá nhau — đúng loại nhầm lẫn saga này sinh ra.

**LIVE (2026-07-31)**: `Price == Close` **859/859**, `max|Price/Close−1| = 0,000000` ⇒ tác động
hôm nay bằng 0. Coverage: `Close IS NOT NULL AND Price IS NULL` = **0** ⇒ đổi cột không mất mã nào.

## 11. Self-check 2 chiều + 2 negative control

Sandbox 4 leg (`BEFORE/AFTER/PERTURB/PERTURB2`) trong `/tmp`; production CSV **không bị chạm**
(mtime giữ nguyên `2026-07-30 19:20`, quant-skeptic tự kiểm lại).

- **(a) Parity hôm nay — PASS**: cả 4 CSV output (`rating_8l` 859×39, `top30`, `buynow`,
  `screener`) **IDENTICAL** mọi cột, mọi mã.
- **(b) Positive control 2014-2016 — PASS**: có đổi thật, đúng bảng §10.
- **(c) `rate_row()` / `fa_ratings_8l` — KHÔNG ảnh hưởng** (kiểm RIÊNG cho `ps`, không giả định
  giống PE): (i) 7 hàm rating dòng 187-429 có **0** tham chiếu `ps`/`sales_yield`/`PS`; (ii)
  `out["ps"]` gán dòng 545 **sau** `rate_row` apply dòng 500 ⇒ bất khả về cấu trúc; (iii) thực
  nghiệm: cột `rating` IDENTICAL cả ở phép sửa thật lẫn ở NC2.

**⚠️ "IDENTICAL 100%" cũng là kết quả của một harness mù — nên phải bác bỏ khả năng đó.** Đây là
phần phương pháp đáng giữ lại nhất của job này:

| Negative control | Kết quả | Ý nghĩa |
|---|---|---|
| NC1: `ps × 1,5` (đều tay) | `sales_yield` khác 816/859; screener IDENTICAL | Harness BẮT được diff. Screener không đổi là **đúng kỳ vọng** — nhân vô hướng đều tay bảo toàn thứ hạng chéo ⇒ `ps_pct` không đổi |
| NC2: `ps × (1 + 1,5·i/n)` (đổi hạng) | `ps_pct` 59, `value_score_v3` 39, `value_score` 25, `value_pct` 58, **`zone` 2 mã**; `rating` **vẫn IDENTICAL** | Harness bắt được cả đường `ps→ps_pct→value_score→zone`, đồng thời xác nhận **thực nghiệm** rằng `rating` miễn nhiễm với `ps` |

⇒ "0 khác" của phép sửa thật là **thật**. NC1 một mình chưa đủ (không đụng tới đường xếp hạng) —
cần **NC2 đổi hạng** mới chứng minh được harness nhìn thấy đường `ps → zone`.

## 12. Việc còn MỞ sau phần 2 (quant-skeptic nêu, CHƯA giải quyết)

Comment trong code ghi lens `ps` được validate IC ngày **2026-06-19** (IC +0,135 CONSUMER/RETAIL;
+0,072 broad). **Nếu** nghiên cứu đó tính `ps` bằng chính công thức `Close`-based này thì con số IC
đó nhiễm và cần đo lại; nếu nó đọc thẳng `ticker_financial.PS` (đã chứng minh ở §10 là cơ sở
`Price` đúng) thì sạch. **Chưa xác định được** — tìm trong job này không ra script/report của
2026-06-19 (`agents/Taylor/research/` không có file tương ứng; các `exp_valframe`/`exp_value_radar`
là nghiên cứu khác và đều đã dùng `Price*OShares`).

**Không chặn phần 2**: phép sửa hôm nay đúng độc lập với câu hỏi này (chứng minh bằng phép định
danh §10, không dựa vào con số IC nào), và `value_score_v3` là **diagnostic-only** — không selector
giao dịch nào đọc nó. Ưu tiên **thấp**, xử lý khi có người đụng lại lens `ps`.

## 13. Tham chiếu (phần 2)

- `mike/agents/Taylor/research/rating8l_ps_price_basis_20260802.md` — báo cáo đầy đủ 5 bước
- `mike/agents/Taylor/exp_ps_basis/` — script + CSV + log (`measure_ps_basis.py`, `diff_legs.py`)
- `mike/logs/verify_20260802_082245.log` — verdict quant-skeptic thô (CONFIRMED / high)
- Commit: `rating_8l.py` (repo WorkingClaude) + incident/report này (repo mike)

---

# PHẦN 3 — cùng họ lỗi, lần này CHẠM SỐ PIN: rổ parking custom30V (job `Taylor_20260802_141725` + `Taylor_20260802_150945`)

## 14. Vì sao phần 3 nặng hơn phần 1 và 2

Phần 1 **bác bỏ** một tiền đề sai (PE không hề bị điều chỉnh). Phần 2 sửa một lens
**diagnostic-only** (`ps`), NAV impact = 0. **Phần 3 là lần đầu cùng họ lỗi này nằm trong đường
tính NAV thật và trong bảng LIVE** — nó làm đổi số pin chính thức của R3.

Điểm chung cả 3 phần: `Close` trong `tav2_bq.ticker` là chuỗi **bị viết lại hồi tố** sau mỗi sự
kiện quyền, còn `Price`/`Volume_3M_P50`/`OShares` là đại lượng **PIT thô**. Ghép 2 loại vào một
phép **cross-sectional** = đưa thông tin tương lai vào.

## 15. Hai lỗi được sửa

| Commit | File | Vai bị dùng sai | LIVE? |
|---|---|---|---|
| `ebeacad` | `custom_basket.py` | `Close × OShares` và `Volume_3M_P50 × Close` dùng cho **chọn rổ + trọng số**, trong khi 3 dòng bên cạnh nhánh ADV đã dùng đúng `COALESCE(Price,Close)` — file tự mâu thuẫn | backtest |
| `be6b976` | `custom30_history.py` | **Publisher** của `tav2_bq.custom30v_8l` lấy `mcap` (= chân **LỢI SUẤT**) làm **TRỌNG SỐ công bố** | **CÓ** |

`2c098c1` thêm self-check 2 chiều + knob `BASKET_PRICE_BASIS` (`legacy` = rollback 1 chữ).

**Vì sao lỗi publisher âm ỉ lâu:** nó chạy lại **mỗi phiên** (`papertrade_daily.sh` [6b]) nhưng
`rebal_date` chỉ đổi **mỗi quý**. `Close` bị viết lại hồi tố ⇒ trọng số công bố của MỘT rebal cố
định **trôi dần** mỗi lần có mã chốt quyền. Đúng ngày công bố (2026-05-05) hệ số = 1,00 cho cả 30
mã ⇒ **trọng số ĐÚNG hôm publish rồi hỏng dần từ đó** — nên không có ngày nào "sai rõ" để ai đó
bắt được bằng mắt.

## 16. Số

A/B 1 biến duy nhất, snapshot đóng cứng đúng vintage số pin:

| | CAGR | Sharpe | MaxDD | Calmar | Final NAV |
|---|---|---|---|---|---|
| legA `legacy` (tiền-sửa) | **27,60%** | 1,84 | −17,5% | 1,58 | 1.041,95B |
| legB `split` (bản sửa) | **27,24%** | 1,81 | −18,4% | 1,48 | 1.006,33B |

legA **tái lập số pin 07-29 tuyệt đối** ⇒ A/B hợp lệ. Self-check 0 VND cả 2 chân.
**Bản sửa làm số XẤU ĐI −0,36pp** — đó là bằng chứng lỗi cũ đang **thổi phồng** pin, không phải lý
do bỏ bản sửa. Tác động LIVE: **thành viên 0/30 đổi**, chỉ lệch trọng số Σ|Δw| = 1,6526pp (ACB
+0,478pp); **không đề xuất giao dịch nào**.

quant-skeptic **CONFIRMED (high)** — `mike/logs/verify_20260802_151136.log`, có independent
recompute thật (tự chạy lại cả 2 self-check + `extract_peryear.py` + 1 truy vấn BQ riêng).

## 17. Bài học (khác 2 phần trước)

1. **Bản đồ bước 1 quét theo FILE là chưa đủ.** Lỗi thứ 2 (`custom30_history.py`) nằm **một tầng
   downstream** của file được quét, và nó mới là cái nằm trên đường LIVE. Quét theo **luồng dữ
   liệu** (ai tiêu thụ output của hàm này), không chỉ theo file đang sửa.
2. **"Live impact = 0 vì Close≈Price hôm nay" là lập luận SAI khi hệ thống có replay.** Đúng ở
   **hàng as-of**, sai ở mọi **cửa sổ lịch sử**: 2025-01..2026-06 hệ số p50 0,926 với 55,8% số dòng
   lệch >5%. Phần 2 dùng được lập luận đó vì lens `ps` chỉ đọc ngày chạy; phần 3 thì không.
3. **Một self-check sai vẫn có ích nếu nó FAIL.** T3 bản đầu giả định "factor<1 ⇒ trọng số phải
   TĂNG" — sai, vì trọng số là đại lượng **tương đối**. Test sai, code đúng; thay bằng bất biến đại
   số (`w_new/w_old == (1/factor) × k` chung) thì spread 1,1e-15.
4. **Δ per-year không phải lúc nào cũng quy kết được.** Năm Δ âm lớn nhất (2025, −6pp) lại là năm
   mức lỗi ~0 ⇒ về cơ chế không thể do cơ sở giá. Đây là **single-path carry**. Headline A/B hợp lệ,
   phân rã theo năm thì không — đừng kể chuyện nhân quả theo năm chỉ vì bảng có sẵn cột năm.

## 18. Còn mở sau phần 3 → **cả 2 mục đầu ĐÃ ĐÓNG ở Phần 4, xem §25**

- ~~**Nhánh CAPIT-membership**~~ (`pt_v23_audit_2014.py:124`, `_c30v_asof`) đọc thành viên từ bảng đã
  publish ⇒ trong A/B vẫn là thành viên cơ sở CŨ ⇒ **−0,36pp là CẬN DƯỚI**. Đo đủ cần republish rồi
  chạy lại. Đây cũng là *killer objection* quant-skeptic nêu.
  → ✅ **ĐÓNG (Phần 4, §20-§22)**: gap = **0,00pp**, số pin không đổi. Không cần republish — R3
  (`CAPIT_BEAR_OVERFLOW` mặc định OFF) **không hề đọc** bảng đó. **−0,36pp là số ĐẦY ĐỦ.**
- `lag_liquidity_filter.py:100` — **cố ý không đụng** (1 trong 5 điểm giữ bất biến parity
  live==sim). Job riêng. → vẫn giữ nguyên chủ đích, không phải nợ kỹ thuật.
- ~~Script audit/nghiên cứu cùng họ lỗi, chưa sửa~~: `basket_concentration.py:28`,
  `basket_scheme_concentration.py:23`, `custom30_core_select_audit.py:101`, `v4final_lib.py:103`.
  → ✅ **ĐÓNG**: commit `76ba560` (+ phát hiện thêm 1 lỗi tại `custom30_core_select_audit.py:37`),
  kèm `basket_price_basis_audit_selfcheck.py`.

## 19. Tham chiếu (phần 3)

- `mike/agents/Taylor/research/basket_price_basis_ab_20260802.md` — báo cáo A/B đầy đủ
- `data/basis_ab_20260802/` — runner + log 2 chân
- `basket_price_basis_selfcheck.py` (4 test), `custom30_publish_weight_selfcheck.py` (5 test)
- `data/results_registry.md` mục **2026-08-02 — ⭐ RE-PIN R3 SAU KHI TÁCH VAI CƠ SỞ GIÁ**
- Commit: `ebeacad`, `2c098c1`, `be6b976` (repo WorkingClaude)

---

# PHẦN 4 — ĐÓNG khoảng mở cuối cùng: nhánh CAPIT-membership (job `Taylor_20260802_154231` chạy + `Taylor_20260802_161942` đọc kết quả/viết kết luận)

## 20. Khoảng mở là gì và vì sao phải đóng

§18 để lại **1 khoảng mở chạm số pin**: A/B ở Phần 3 chỉ đổi cơ sở giá trên **đường dựng rổ trực
tiếp**; nhánh **CAPIT** lại đọc THÀNH VIÊN rổ từ **bảng đã publish** `tav2_bq.custom30v_8l`
(`pt_v23_audit_2014.py`, hàm `_c30v_asof`), mà bảng đó trong A/B vẫn dựng bằng cơ sở **CŨ**. Nên
**−0,36pp phải ghi là CẬN DƯỚI** — đúng *killer objection* quant-skeptic nêu. Chừng nào chưa đóng,
số pin R3 còn kèm một dấu hỏi về độ phủ.

## 21. Kết quả: gap = **0,00pp**, số pin **KHÔNG đổi**

`27,24% / 1,81 / −18,4% / 1,48 / 1.006,33B` giữ nguyên từng chữ số.

⚠️ **Điểm dễ chép sai nhất của phần này — LÝ DO, không phải con số.** 0,00pp **không** có nghĩa "đã
đo một chênh lệch và nó nhỏ tới mức làm tròn thành 0". Nó là **BẤT BIẾN CƠ CẤU**: cấu hình R3
production **không hề đọc** bảng đó, nên nội dung bảng (cơ sở cũ hay đã sửa) **không thể** ảnh hưởng
tới số R3 — dù đầu vào lệch bao nhiêu đi nữa.

Đường đọc `custom30v_8l` **duy nhất** trong toàn engine nằm TRỌN trong nhánh cờ mặc định TẮT:
```
105 : CAPIT_BEAR_OVERFLOW = os.environ.get("CAPIT_BEAR_OVERFLOW", "0") == "1"   # mặc định OFF
1203: if CAPIT_BEAR_OVERFLOW and len(golden) < CAPIT_OVERFLOW_MIN:
1214:     vmems = _c30v_asof(d)        # <-- lần đọc DUY NHẤT (grep chỉ ra 3 hit: 121/124 định nghĩa, 1214 gọi)
```

## 22. Vì sao phải có CẢ negative control LẪN positive control

Đây là bài học phương pháp chính của phần 4. Một mình negative control (**đổi bảng → kết quả không
đổi**) **không chứng minh được gì** — nó không phân biệt nổi 2 khả năng:
(a) bất biến thật, và (b) **đường ống hỏng / overlay không được đọc**, tức thí nghiệm vô hiệu.

| | Đầu vào `custom30v_8l` | md5 CSV | CAGR |
|---|---|---|---|
| **NC** legB (số pin) | bảng gốc trong snapshot | `51a1ec0f` | 27,2438% |
| **NC** bảng **RỖNG** | **0 dòng** | `51a1ec0f` | 27,2438% |
| **NC** membership **ĐÃ SỬA** | **1.440 dòng** (cơ sở `split`) | `51a1ec0f` | 27,2438% |
| **PC** cờ BẬT, bảng **CŨ** | 1.440 dòng (cơ sở `legacy`) | `c6d56907` | 29,0938% |
| **PC** cờ BẬT, bảng **ĐÃ SỬA** | 1.440 dòng (cơ sở `split`) | `58208ffa` | 29,0749% |

- **NC**: 3 chân **BYTE-IDENTICAL** — trùng cả 3.107 dòng DAILY + 10.750 dòng TX, không chỉ trùng
  chỉ tiêu tổng hợp. Self-check `nav_identity_err` = **0 VND** (BAL và LAG) mọi chân.
- Đầu vào **thật sự khác nhau**: overlay rỗng (0 dòng, 4.025 B) vs overlay đã sửa (1.440 dòng,
  21.073 B); bản `split` lệch bản `legacy` **346/1.613 dòng thành viên**, `max|Δw| = 0,0656`.
  ⇒ chặn được phản bác "chạy trùng một cấu hình hai lần".
- **PC**: 2 chân **KHÁC nhau** ⇒ overlay **được đọc thật**, engine **thực sự dùng** bảng khi cờ bật
  ⇒ bất biến ở NC là **tính chất thật của cấu hình R3**, không phải thí nghiệm hỏng.

Kỹ thuật overlay đáng tái dùng: symlink **toàn bộ** snapshot cache đã pin, **chỉ thay đúng 1 file**
parquet cần thử. Cô lập 1 biến tuyệt đối, tốn ~4-21 KB đĩa thay vì nhân bản ~2 GB.

## 23. Số `29,07%` — hàng rào chống trích dẫn nhầm

**29,0938% / 29,0749% là số của một cấu hình KHÔNG DÙNG (`CAPIT_BEAR_OVERFLOW=1`).** Tuyệt đối
không trộn với số R3 hiện hành. Ý nghĩa duy nhất: **nếu tương lai** ai bật cờ đó lên thì cơ sở giá
của bảng **mới bắt đầu** có tác dụng, và tác dụng đó đo được là **−0,019pp CAGR** — nhỏ hơn **một
bậc** so với −0,36pp của kênh dựng rổ trực tiếp. Số này **chưa** qua quant-skeptic, **chưa** được
pin; chỉ là tài liệu tham khảo cho job tương lai.

## 24. Bài học (khác 3 phần trước)

1. **"Không đo được chênh lệch" ≠ "chênh lệch bằng 0" ≠ "kênh đó không tồn tại".** Ba mệnh đề khác
   nhau, và chỉ mệnh đề thứ ba đúng ở đây. Viết registry bằng mệnh đề sai sẽ khiến người sau tưởng
   đã có một phép đo bao phủ kênh CAPIT — trong khi thực tế kênh ấy chưa từng được kích hoạt. Đây
   đúng cái bẫy Phần 1 và Phần 2 đã mắc theo kiểu khác: **suy diễn nhầm từ một quan sát ĐÚNG**.
2. **Negative control không có positive control là bằng chứng rỗng.** "Đổi đầu vào mà đầu ra không
   đổi" là hình dạng giống hệt nhau giữa *bất biến thật* và *thí nghiệm chưa từng chạy đúng*. Bắt
   buộc phải có một chân chứng minh đường ống sống.
3. **Bằng chứng cơ cấu (đọc code) mạnh hơn bằng chứng thực nghiệm** cho loại khẳng định "X không ảnh
   hưởng Y". `grep -n` ra 3 dòng cho kết luận phổ quát trên MỌI dữ liệu; chạy mô phỏng chỉ cho kết
   luận trên đúng bộ dữ liệu đã chạy. Ở đây có cả hai, và chúng khớp nhau.
4. **Tham chiếu treo còn nguy hiểm hơn thiếu tài liệu.** Job trước chết giữa chừng, kịp sửa "Giới
   hạn #1" thành "ĐÃ ĐÓNG, xem mục bên dưới" nhưng **chưa kịp viết mục đó**. Người đọc gặp một
   khẳng định dứt khoát ("0,00pp CHÍNH XÁC") không kèm bằng chứng, mà lại **trông như** đã có bằng
   chứng ở chỗ khác. Sửa "còn mở → đã đóng" phải nằm **cùng một commit** với phần bằng chứng, không
   bao giờ tách ra (cùng tinh thần `coding_guidelines` §10: canonical hoá và dọn biến thể trong
   cùng một lượt).

## 25. Trạng thái các mục "còn mở" của §18 sau phần 4

| Mục §18 | Trạng thái |
|---|---|
| Nhánh CAPIT-membership ⇒ −0,36pp là cận dưới | ✅ **ĐÓNG** — gap 0,00pp (bất biến cơ cấu); −0,36pp là số **đầy đủ** cho cấu hình R3 |
| 4 script audit/nghiên cứu cùng họ lỗi | ✅ **ĐÓNG** — commit `76ba560` (+ 1 lỗi nữa phát hiện thêm tại `custom30_core_select_audit.py:37`), kèm `basket_price_basis_audit_selfcheck.py` |
| `lag_liquidity_filter.py:100` | ⏸️ **CỐ Ý GIỮ** — 1 trong 5 điểm giữ bất biến parity live==sim. Job riêng, không phải nợ kỹ thuật bỏ quên |
| Lỗi fidelity `liq<=0` | 🔴 **VẪN MỞ** — ngoài phạm vi saga này; khoảng kỳ vọng trung thực **[~27,2%; ~31,3%]**, **anchor DD ~−30%** (không phải −18,4%) |

⇒ **Saga cơ sở giá `Price` vs `Close` khép lại ở đây.** Còn lại chỉ là mục `liq<=0` (họ lỗi khác) và
một lựa chọn có chủ đích.

## 26. Vì sao KHÔNG chạy lại quant-skeptic cho phần 4

Số cuối cùng **không đổi một chữ số** so với bản đã CONFIRMED (high)
(`mike/logs/verify_20260802_151136.log`); phần 4 **không đề xuất thay đổi production nào**, không
đổi tham số, không wire gì mới — chỉ biến một **luận cứ** từ "cận dưới" thành "đầy đủ, có lý do cơ
cấu". Bằng chứng lại thuộc loại **cơ học, tự kiểm chứng trong vài giây**: `md5sum` 3 file CSV +
`grep -n` 3 dòng code — không phải suy luận thống kê cần phản biện. **Bắt buộc gate lại NẾU** sau
này có ai bật `CAPIT_BEAR_OVERFLOW=1` để dùng thật; lúc đó 29,07% mới rời diện tham chiếu.

## 27. Tham chiếu (phần 4)

- `data/results_registry.md` mục **2026-08-02 — ĐÓNG KHOẢNG CÁCH CAPIT-MEMBERSHIP** — bằng chứng đầy đủ
- CSV: `data/v23_golive_audit_..._exp_{nc_c30v_empty,fix_c30v_membership,pc_ovf_oldtable,pc_ovf_fixtable}_univpit.csv`
- Overlay cache (**GIỮ** làm audit trail, chỉ ~4/21 KB dữ liệu thật, phần còn lại symlink):
  `data/bq_cache_ov_c30v_empty/`, `data/bq_cache_ov_c30v_fix/`
- Bảng regen 2 cơ sở: `data/c30v_regen_legacy.csv`, `data/c30v_regen_split.csv`
- Code: `pt_v23_audit_2014.py` dòng 105 / 121-124 / 1203 / 1214
- Commit: `982621a` (registry phần 4), `76ba560` (4 script audit)
