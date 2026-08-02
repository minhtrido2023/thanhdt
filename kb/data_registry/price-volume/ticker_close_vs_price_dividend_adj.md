---
kind: bigquery-column-pair
status: TRAP
source: tav2_bq.ticker — cặp cột Close (đã điều chỉnh) vs Price (thô)
group: price-volume
scope: mọi phép tính tỉ suất lợi nhuận có đi qua ngày chốt quyền (ex-date)
writer: Ingest ETL
---

# `Close` vs `Price` trong `tav2_bq.ticker` — điều chỉnh cổ tức / chia tách

**Status: TRAP** — dùng sai cặp cột này đã gây **2 lỗi thật, cùng lúc**, trong 3 báo cáo
client-facing tháng 7/2026 (đã sửa 2026-08-02, job `Taylor_20260802_060243`).

## Là gì

| Cột | Nội dung |
|---|---|
| `Price` | Giá **THÔ**, đúng giá thật khớp trên sàn phiên đó. Không hồi tố. |
| `Close` | Giá **ĐÃ ĐIỀU CHỈNH** cổ tức + chia tách, **hồi tố từ vintage HÔM NAY** về quá khứ (total-return-adjusted). |

Quan hệ giữa hai cột là **PHÉP NHÂN**, không phải phép trừ:

- Tỉ số `ratio = Close / Price` là **hằng số** giữa hai ex-date liên tiếp.
- `ratio` **nhảy về 1,0** đúng ngày ex-date của sự kiện gần nhất.
- Suy cổ tức/cp: `div_per_share = P_last_cum × (1 − ratio_last_cum / ratio_ex)`

## Bẫy (1) — suy cổ tức bằng HIỆU `Close − Price` → SAI SỐ

Hiệu số **biến thiên theo mức giá**, nên không phải mức cổ tức. Ca thật: SAB tháng 7/2026, hiệu số
chạy **−3.110 → −3.000** trong khi cổ tức thật là **đúng 3.000đ/cp**. Áp hiệu số tại ngày 24/07 cho
ra "2.990đ" — con số này đã lọt vào báo cáo tháng 7 bản đầu (Mục 10.2 cạm bẫy #2) trước khi bị bắt.
Hiệu số cũng cho **sai ngày ex-date** nếu đọc theo mắt thường (SAB thật là 28/07, không phải 27/07).

→ **Luôn dùng tỉ số, không dùng hiệu số.**

## Bẫy (2) — trộn hai hệ quy chiếu = PHẠT CỔ TỨC HAI LẦN

Lấy **thị giá đã điều chỉnh** (`Close`) trừ **giá vốn thô** (giá khớp thật đã trả) → trừ phần cổ tức
hai lần. Ca thật: báo cáo tuần 20–24/07 công bố SpaceX **−94.079.443 (−9,90%)**; số đúng là
**−86.790.443 (−9,13%)** theo giá thô, hoặc **−81.915.443 (−8,62%)** khi cộng cổ tức đã tách được.

**Quy tắc:** giá vốn thô ⇒ so với `Price` (thô) ⇒ **cộng cổ tức vào TỬ SỐ**:

    total_return = (P_end + D − cost) / cost

KHÔNG dùng `Close_end / Close_start` để so với **giá vốn**: chuỗi `Close` hồi tố theo vintage hôm nay
nên mức giá của nó không cùng hệ quy chiếu với một giá khớp thô. (`Close/Close` chỉ đúng khi so hai
NGÀY với nhau — "mã X tăng bao nhiêu trong tuần" — không phải để so với giá vốn.)

## Bẫy (3) — quên cộng cổ tức = BÁO LỖ OAN (lỗi gốc, nghiêm trọng nhất)

Ngày ex-date giá sàn giảm đúng bằng cổ tức; nếu chỉ tính `(Price_end − cost)/cost` thì mã trả cổ tức
cao bị báo lỗ nặng hơn thực tế. Ca thật tháng 7/2026: **NCT −11,6% → −3,1%** (8,5 điểm %),
**SAB −8,1% → −1,7%** (6,4 điểm %). Lỗi này **đảo dấu một kết luận attribution**: rổ CAPIT bị mô tả
là "chỉ gánh 2,6% mức lỗ" trong khi thực tế **LÃI +5.659.900đ**.

## Bẫy (4) — `Close/Price` KHÔNG phân biệt cổ tức tiền mặt vs chia tách/thưởng CP

Cả hai loại sự kiện đều làm `ratio` nhảy, nhưng ý nghĩa hoàn toàn khác nhau:

| | Số lượng CP | Tiền về tài khoản |
|---|---|---|
| Cổ tức tiền mặt | KHÔNG đổi | CÓ |
| Chia tách / thưởng CP | TĂNG | KHÔNG |

→ **Bắt buộc đối soát với sổ broker** trước khi đưa vào báo cáo. Ba nguồn kiểm chứng độc lập (đã
dùng thật 2026-08-02): (i) `openQuantity` của broker không đổi qua ex-date; (ii)
`cashDividendReceiving` của DNSE tăng đúng `KL × cổ tức`; (iii) `costPrice` broker báo đã bị trừ
đúng phần cổ tức.

## BẮT BUỘC DÙNG — `mike/bin/dividend_adjusted_return.py`

Mọi báo cáo (ngày/tuần/tháng) và mọi phép tính tỉ suất per-position **PHẢI** đi qua helper này, không
tự viết lại công thức:

```bash
python3 mike/bin/dividend_adjusted_return.py --ticker NCT --from 2026-07-21 --to 2026-07-31 \
    --cost 94360 --qty 500 --account SpaceX
python3 mike/bin/dividend_adjusted_return.py --selfcheck    # 16 phép thử
```

Helper tự phát hiện sự kiện từ BQ, gắn cờ trạng thái xác minh:

- `CASH_CONFIRMED` — khớp `cashDividendReceiving` của DNSE → **được phép** dùng trong báo cáo.
- `STOCK_SUSPECTED` — số lượng CP đổi tại ex-date → nghi chia tách, **không** cộng vào tử số.
- `UNVERIFIED` — chưa đối soát được với broker → **CẤM** đưa vào báo cáo gửi nhà đầu tư.

## Liên quan — lỗi NAV đếm hai lần cổ tức (khác lỗi trên, độc lập)

DNSE ghi `cashDividendReceiving` vào cuối **ngày cuối cùng còn hưởng quyền**, trong khi `mtm_stock`
ngày đó vẫn dùng giá **còn quyền**. `daily_nav_snapshot.py` lấy `cash = totalCash` (đã gồm cổ tức
phải thu) ⇒ **cộng hai lần**, tự triệt tiêu phiên sau. Ảnh hưởng NAV 5 dòng trong tháng 7/2026
(SpaceX 16/07, 24/07, 27/07; ZaloPay 16/07, 24/07) và tỉ suất TUẦN của 2 tuần cuối tháng; **không**
ảnh hưởng tỉ suất tháng. Chưa sửa chuỗi lịch sử — việc cần làm 5b, báo cáo tháng 7 Mục 8.5.

## Nguồn

- Job `Taylor_20260802_060243` (2026-08-02) — phát hiện + sửa 3 báo cáo.
- Bằng chứng độc lập thứ 2: Winston job 2026-07-31 (`cashDividendReceiving` jump 744 × 3.000 cho SAB).
- Báo cáo tháng 7/2026 Mục 8.4 / 8.5 / 10.2 (cạm bẫy #4, #5).

↩ [Về index nhóm](index.md)
