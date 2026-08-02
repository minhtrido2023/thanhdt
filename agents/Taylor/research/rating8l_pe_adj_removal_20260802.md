# Gỡ `_pe_adj_factor` khỏi `rating_8l.py` — thực thi + self-check 2 chiều

**Job**: `Taylor_20260802_063752` · **Ngày**: 2026-08-02 · **Trạng thái**: code đã sửa, self-check
2 chiều PASS, chờ/kèm verdict quant-skeptic.

Tiền đề đã được chứng minh ở job `Taylor_20260802_054825`
(`research/pe_priceadj_refutation_ab_20260802.md`): `PE`/`PB`/`PCF` trong `tav2_bq.ticker` được tính
trên **`Price` thô point-in-time của chính ngày đó** ⇒ `1/PE` đọc thẳng đã đúng PIT; nhân thêm
`Price/Close` là **đưa look-ahead vào** (hệ số phụ thuộc sự kiện chia/thưởng XẢY RA SAU ngày t), và
A/B NAV custom30V đo được **−1,70pp CAGR / −0,19 Calmar**. User đã duyệt gỡ.

---

## Bước 1 — Khảo cổ code: ĐÍNH CHÍNH ngày sinh lỗi và bán kính ảnh hưởng

**(1a) Lỗi KHÔNG do job `Taylor_20260802_042110` hôm nay tạo ra — đây là đính chính so với giả định
trong dispatch.**

```
$ git log -S "_pe_adj_factor" --oneline --all -- WorkingClaude/rating_8l.py
a1a4709 auto-backup 2026-06-24T17:00:01Z
3c54745 auto-backup 2026-06-24T17:00:01Z
$ git show 3c54745^:WorkingClaude/rating_8l.py | grep -n "_pe_adj_factor"   # → không có
$ git log --since=2026-08-01 --all --oneline -- WorkingClaude/rating_8l.py  # → RỖNG
```

Phép nhân vào file ngày **2026-06-24** (commit auto-backup rollup), sống **~6 tuần** trong
production. Hôm nay job 042110 **không hề chạm** `rating_8l.py`; nó chỉ **trích dẫn** đoạn code này
làm chỗ dựa cho tiền đề sai ("script duy nhất có phép sửa này") — tức là **thừa hưởng** lỗi chứ
không tạo ra lỗi. Điều này làm bài học quy trình ở Bước 6 nặng hơn, không nhẹ đi: một quan sát sai
nằm im 6 tuần rồi được dùng làm bằng chứng cho một suy diễn sai tiếp theo.

**(1b) Bán kính ảnh hưởng HẸP HƠN mọi ghi chú trước đó — đo bằng đọc code, không suy đoán:**

| Thành phần | Có nhiễm không? | Bằng chứng |
|---|---|---|
| **Rating 8L 1-5** (gate LAG ≤3, gate custom30V) | **KHÔNG** | `rate_row()` (dòng 349-413) không dùng `PE`/`PB`/`PCF`; hơn nữa `res = df.apply(rate_row)` chạy ở dòng ~500, **TRƯỚC** phép nhân ở dòng 523-524 (phép nhân chỉ đụng `out`, không đụng `df`) |
| **BQ `tav2_bq.fa_ratings_8l`** (bảng `custom_basket.rating_asof` bisect) | **KHÔNG** | Bảng chỉ có `ticker,time,route,rating,tier` (`rating_8l_history.py:refresh_bq_table`), do **script khác** sinh; `rating_8l_history.py` chưa từng có `_pe_adj_factor` |
| `data/rating_8l.csv` cột `PE`, `earn_yield` | CÓ | ghi ở dòng 563-568 |
| Screener `value_score`/`zone`/top30/buynow/`rank_8l.md` | CÓ (qua `earn_yield`) | dòng 628-881 |

⇒ **Đường giao dịch LIVE (custom30V/BAL/LAG) chưa từng bị nhiễm**, kể cả nếu rebuild lịch sử —
vì bảng ratings lịch sử không đi qua script này. Nhiễm chỉ ở **snapshot màn hình lọc (human-facing)
của chính ngày chạy**. Đây là bản đính chính cho lo ngại "rebuild lịch sử sẽ nhiễm" ghi ở job 054825.

## Bước 2 — Phép sửa

Xoá 2 dòng nhân + comment sai (`PE_stored = Close_adj/EPS`), khôi phục đúng trạng thái trước
2026-06-24 (`out["earn_yield"] = 1/PE`), thay bằng comment cảnh báo NGƯỢC chiều + trỏ tới bằng chứng.
`git diff` xác nhận phần code còn lại **byte-identical** với bản trước commit 3c54745.

## Bước 3 — Self-check 2 chiều

Sandbox: `WORKDIR_8L=/tmp/r8l_sbx_*/{BEFORE,AFTER}` (4 CSV input `moat_tags/forensic_flags/
bank_lens_v3/power_lens` copy vào từng leg — lần chạy đầu thiếu file này đã bị phát hiện và chạy lại).
Xác nhận `data/rating_8l*.csv` production **không bị chạm**: mtime vẫn `2026-07-30 19:20`, `git
status` sạch. Interpreter `/home/trido/thanhdt/wc_venv/bin/python` (pandas 3, đúng pin registry).

**(3a) Parity ngày gần đây — PASS.** Snapshot live `ticker_1m` = **2026-07-31**:

```
d,          n,   n_eq, minF, maxF
2026-07-31, 859, 859,  1.0,  1.0        -- F = Price/Close = 1.0 cho TOÀN BỘ 859 mã
```

Diff BEFORE(lỗi) vs AFTER(sửa), khớp theo `ticker` (bộ mã giống hệt ở cả 4 file):

| File | Cột khác | Max |diff| |
|---|---|---|
| `rating_8l.csv` | `PE` (730 dòng), `earn_yield` (258) | 0,00499 / 0,0286 |
| `rating_8l_top30.csv` | `PE` (30), `earn_yield` (12) | 0,00483 / 0,0002 |
| `rating_8l_buynow.csv` | `PE` (72), `earn_yield` (25) | 0,00483 / 0,0002 |
| `rating_8l_screener.csv` | `value_score`/`ey_pct`/`value_pct`… (4-10 dòng) | 0,025 (value_score) |

**`rating`, `route`, `zone_v2`, `note`, `redflag`, `forensic`, `golden_cell` — IDENTICAL 100%.**
Vì F=1,0 tuyệt đối, toàn bộ chênh lệch còn lại chỉ do dòng lỗi có `.round(2)` trên PE (mã PE nhỏ như
PVV PE=0,386 bị làm tròn thành 0,39 ⇒ `earn_yield` lệch 0,0286). Đúng kỳ vọng "diff ≈ 0", không có
diff lớn bất ngờ.

*(Lưu ý phương pháp: lần so đầu tiên báo "note 392 dòng khác / redflag 767 dòng khác" — kiểm lại là
**artifact của bộ so sánh**: pandas 3 StringDtype trả `pd.NA` khi `astype(str)`, và `pd.NA != pd.NA`
→ `pd.NA` bị `.sum()` đếm là khác. So lại với sentinel `<NA>` ⇒ 0 khác. Ghi lại vì đây đúng là loại
tín hiệu "diff lớn bất ngờ" mà dispatch dặn phải DỪNG để kiểm, và nó **không** phải lỗi thật.)*

**(3b) Positive control dữ liệu cũ — PASS.** `rating_8l.py` chỉ đọc `ticker_1m` tại `MAX(time)`
(không có tham số as-of) nên **không chạy lùi lịch sử được**; thay vào đó tái lập **đúng công thức
yield đã đổi** (`ey_fix = 1/PE` vs `ey_bug = 1/round(PE·Price/Close, 2)`) trên `tav2_bq.ticker`:

| Ngày | n | F=Price/Close (trung vị) | ey lệch (trung vị) | Spearman(fix, bug) | Top-30 rẻ nhất đổi |
|---|---|---|---|---|---|
| 2014-06-30 | 511 | 2,517 | **60,3%** | 0,639 | **13/30** |
| 2015-06-30 | 539 | 2,241 | 55,4% | 0,645 | 10/30 |
| 2016-06-30 | 594 | 2,045 | 51,1% | 0,739 | 12/30 |

⇒ Code cũ **thực sự sai ở đúng chỗ cần sửa**: trên dữ liệu cũ nó bóp méo trục value tới mức đảo
1/3 danh sách rẻ nhất. Sửa xong ≈0 hôm nay **không phải** vì sửa vào chỗ vô hại.

**(3c) Production không bị ghi đè** — đã xác nhận ở trên.

## Bước 4 — ĐO (KHÔNG sửa): lens `ps` đang dùng `Close`

`rating_8l.py:530-532`: `ps = Close·OShares/Revenue_ttm`. Câu hỏi: `Close` hay `Price` mới đúng?
**Không giả định giống PE** — kiểm bằng phép định danh với đại lượng PIT đã lưu (`PS` trong
`ticker_financial`), cùng họ phương pháp "trong-kỳ-hằng-số" của job 054825 nhưng mạnh hơn vì đây là
đối chiếu trực tiếp:

```
n_rows = 7.321 (2014-01-01 → 2016-12-31, ticker_financial ⋈ ticker theo (ticker,time))
Price·OShares/Rev_ttm khớp PS lưu (sai số <2%):  99,7%   | sai số tương đối trung vị: 0,0000
Close·OShares/Rev_ttm khớp PS lưu (sai số <2%):  11,9%   | sai số tương đối trung vị: 0,5233
```

⇒ **`PS` lưu ở cơ sở `Price` thô** — nên lens `ps` tự tính bằng `Close` là **SAI cơ sở** (cùng hướng
lỗi với PE: `Close` là chuỗi đã điều chỉnh theo sự kiện xảy ra SAU ngày t, còn `OShares` là số cổ
phiếu PIT của kỳ ⇒ trộn 2 cơ sở khác nhau).

**Tác động đo được (chưa sửa):**
- **LIVE hôm nay: 0.** `Price == Close` cho 859/859 mã ⇒ 0 mã đổi, 0 rating đổi, 0 zone đổi.
- **Lịch sử (nếu tính lùi):** `sales_yield` lệch trung vị **90,6%–131,3%**; Spearman 0,887–0,909;
  **11–15 / 30** tên rẻ nhất theo trục PS bị đổi (2014/2015/2016).
- Phạm vi: `ps_pct` chỉ vào `value_score_v3` của screener; **không** đụng rating 8L 1-5, **không**
  đụng bất kỳ selector giao dịch nào (giống hệt `earn_yield`).

**Đề xuất (để Mike/user quyết riêng, KHÔNG tự sửa trong job này):** đổi `Close` → `Price` trong lens
`ps`. Rủi ro live = 0 (F≡1 hôm nay), lợi ích = mọi lần tính/nghiên cứu lùi lịch sử không còn dùng giá
đã điều chỉnh-tương-lai. Cùng lý do đó, mức ưu tiên là THẤP-nhưng-nên-làm, không khẩn cấp.

## Bước 5 — Quant-skeptic

Xem verdict trong event `verification` cùng `trace_id=Taylor_20260802_063752` trên bus.

## Bước 6 — Incident record

`mike/kb/incidents/2026-08/2026-08-02-pe-price-close-adjustment-saga.md`.

## Số không đổi
`1/PE` IC **+0,125** và R3 **27,60%** giữ nguyên (job này không đổi công thức mà 054825 đã đo — nó
gỡ một phép nhân chưa từng nằm trong đường tính R3). Không wire gì mới ⇒ không khai N-trials/DSR/PBO.
