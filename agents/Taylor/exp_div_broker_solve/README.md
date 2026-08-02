# Cổ tức: đổi vai trò `Close/Price` từ NGUỒN SỐ LIỆU → chỉ còn PHÁT HIỆN

Job `Taylor_20260802_082124` · 2026-08-02 · phản biện của user

> ✅ **ĐÃ MERGE VÀO PRODUCTION** — `dividend_broker_solve.py` trong thư mục này là bản STAGED, giữ
> lại làm bằng chứng nghiên cứu. Code SỐNG nằm ở `mike/bin/dividend_adjusted_return.py`
> (`solve_from_broker` / `crosscheck_dividend_1y` / `resolve_dividends`, selfcheck 41/41).
> **Đừng chạy/sửa file staged này** — nó không còn là nguồn chuẩn tắc.

## Kết luận một dòng

Phương pháp MỚI (per_share lấy **từ tiền mặt broker thật**) cho ra **số y hệt** phương pháp cũ (suy
từ tỉ số `Close/Price`) trên **cả 6 sự kiện** tháng 7/2026 ⇒ **không phải sửa/gửi lại 3 báo cáo**,
chỉ đổi code + tài liệu. Cái thay đổi là **độ tin cậy của quy trình**, không phải con số.

## 1. Phản biện của user — đúng ở đâu

`Close/Price` chỉ nói **CÓ một sự kiện điều chỉnh giá**, không nói **loại gì**. Cổ tức tiền mặt, cổ
tức cổ phiếu, thưởng CP, chia tách, phát hành thêm — tất cả làm tỉ số nhảy y hệt nhau. Suy ngược ra
"đồng/cp" từ tỉ số là **áp một giả định** (sự kiện này là tiền mặt) mà chính dữ liệu đó không kiểm
chứng được. Đúng. Vai trò mới:

| Tầng | Nguồn | Vai trò |
|---|---|---|
| 1 · PHÁT HIỆN | `tav2_bq.ticker` `Close/Price` | "mã nào, ngày nào" + ước lượng thô để khoanh cửa sổ tra broker |
| 2 · ĐO LƯỜNG | `cashDividendReceiving` (DNSE) | **SỐ CHÍNH THỨC** (đồng/cp) |
| 3 · ĐỐI SOÁT | `ticker_financial.Dividend_1Y` delta | xác nhận độc lập, trễ theo quý |

## 2. Verify lại claim "BQ không có cột raw" — Mike **sai một phần**

BQ **CÓ** bảng đúng hình dạng cần tìm:

    tav2_bq.shares_outstanding_live
      ticker · ex_date · oshares · prev_oshares
      stock_div_ratio · cash_div_per_share · price_adj_factor · source · note · updated_at

Grep của Mike dùng chuỗi `'divid'` nên **bỏ sót** `cash_div_per_share` (chỉ chứa `div`). Bài học:
tìm cột theo `div` / `corp` / `ex_date`, đừng chỉ `divid`.

**Nhưng kết luận cuối của Mike vẫn đúng**: bảng chỉ có **4 dòng** (ACB, HDC, EVG, DDV — tháng
6/2026), do Winston chạy tay `update_shares_live.py` khi cần override `OShares`, **không phải chuỗi
lịch sử cổ tức**. **0 dòng** cho cả 6 mã tháng 7. Đã quét cả 5 dataset (`tav2_bq`, `tav2_mike`,
`tav2_pin`, `tav2_monitor`, `recommend_v23`) với regex rộng
(`divid|div_|_div|cash|corp|action|event|split|bonus|right|issue|adjust|ex_date|payout`) — ngoài ra
chỉ còn các cột **tổng trailing theo quý** trong `ticker_financial`.

→ Vẫn dùng bảng này làm **ưu tiên 1** khi có (đã phân loại sẵn tiền/cổ phiếu), nhưng không được coi
là nguồn có sẵn.

## 3. Phát hiện kỹ thuật quan trọng — KHÔNG chia được delta/qty

Dispatch đề xuất "lấy delta broker chia số lượng cổ phiếu". **Không làm được như vậy**:
`cashDividendReceiving` là số dư **của TOÀN TÀI KHOẢN**, delta của nó là **theo NGÀY, không tách
theo mã**. Nhiều mã cùng ngày chốt quyền rơi chung một delta (CTG và VCB đều ex-date 23/07).

Bài toán đúng là **hệ phương trình tuyến tính**:

    với mỗi (tài khoản a, ngày d):   delta(a,d) = Σ_mã  qty(a, mã) × per_share(mã)

Hai tài khoản có **tỉ lệ nắm giữ khác nhau** → hai phương trình độc lập → hệ 2×2 ngày 23/07 có
**nghiệm duy nhất**, suy hoàn toàn từ tiền thật, **không cần tỉ số**:

    2300·CTG + 1300·VCB = 1.620.000   (SpaceX)
    1050·CTG +  800·VCB =   832.500   (ZaloPay)
    ⇒ CTG = 450, VCB = 450

Giải theo từng **thành phần liên thông**. Vô định (chỉ giữ ở 1 tài khoản) hoặc dư số lớn ⇒ giữ
`UNVERIFIED`, **cấm vào báo cáo** — không lấp bằng ước lượng tỉ số.

## 4. Đối soát đủ 6 sự kiện — tiền broker thật

| Mã | ex-date | Cũ (tỉ số) | **Mới (tiền broker)** | Hệ | Tầng 3 `Dividend_1Y` |
|---|---|---|---|---|---|
| MBB | 09/07 | 1.000 | **1.000** | 1pt/1ẩn | ✅ match (300→1.300, Δ+1.000) |
| BID | 17/07 | 450 | **450** | 2pt/1ẩn | ⏳ chưa có kỳ quý sau ex-date |
| CTG | 23/07 | 450 | **450** | 2pt/2ẩn | ✅ match (450→900, Δ+450) |
| VCB | 23/07 | 450 | **450** | 2pt/2ẩn | ✅ match (450→900, Δ+450) |
| NCT | 27/07 | 8.000 | **8.000** | 2pt/1ẩn | ⏳ chưa có kỳ quý sau ex-date |
| SAB | 28/07 | 3.000 | **3.000** | 2pt/1ẩn | ⏳ chưa có kỳ quý sau ex-date |

**0 sai lệch.** Tầng 3: match 3/6, unavailable 3/6 (độ trễ quý), **mismatch 0**.

Tổng khớp tiền thật từng tài khoản:
- SpaceX `2.400.000 + 855.000 + 1.035.000 + 585.000 + 4.000.000 + 3.300.000 = 12.175.000`
- ZaloPay `405.000 + 472.500 + 360.000 + 2.984.000 + 2.232.000 = 6.453.500`
  (ZaloPay **không** hưởng cổ tức MBB — mua sau ex-date 09/07)

## 5. Vì sao tầng 3 không bao giờ được ghi đè tầng 2

`Dividend_1Y` là **tổng TRAILING 1 năm**, cập nhật theo **chu kỳ báo cáo quý**:

- **Độ trễ**: kỳ gần nhất của SAB là 23/07, ex-date là 28/07 ⇒ chưa xuất hiện. Không kết luận được.
- **Delta có thể ÂM**: SAB `5.000 → 2.000` (Δ −3.000) — đó là một cổ tức **cũ rơi khỏi cửa sổ 1
  năm**, không liên quan cổ tức mới. Đọc delta này như "cổ tức mới" sẽ sai cả dấu.

## 6. Hai bug thật bắt được **khi chạy**, không phải khi đọc lại

1. **Cửa sổ 2 ngày làm một sự kiện bị đếm ở CẢ HAI ngày.** ex-date của NCT (27/07) **trùng**
   ngày-cuối-còn-quyền của SAB (27/07) ⇒ NCT bị cộng vào cả delta 24/07 lẫn 3.300.000 của 27/07 ⇒
   hệ mâu thuẫn, **hỏng cả hai mã** (selfcheck 23/25). Fix: mỗi sự kiện chỉ được gán vào **đúng một
   ngày** (ngày sớm nhất có delta dương).
2. **`bq --format=json` trả MỌI giá trị dưới dạng STRING** — `ValueError: Unknown format code 'f'`
   ngay lần chạy thật đầu tiên của tầng 3. Selfcheck offline không bắt được vì không chạm BQ.

Đúng bài học `verify-before-done`: cả hai chỉ lộ ra khi **chạy thật**, không phải khi đọc lại code.

## 7. Selfcheck

    python3 dividend_broker_solve.py --selfcheck      # 25/25 PASS, offline (không cần BQ/log)
    env -u TZ python3 dividend_broker_solve.py --selfcheck            # 25/25
    TZ=America/New_York python3 dividend_broker_solve.py --selfcheck  # 25/25

Bao gồm các ca âm tính bắt buộc: hệ vô định ⇒ `UNVERIFIED`; ước lượng tỉ số lệch xa ⇒ hạ về
`UNVERIFIED` (không im lặng nhận); số lượng CP đổi tại ex-date ⇒ `STOCK_SUSPECTED`; delta ÂM (chi
trả khoản phải thu) không bị coi là sự kiện mới.

End-to-end thật (BQ + log broker): `reconcile_july.txt` — 6/6 `CASH_CONFIRMED`.

## 8. Giới hạn còn lại (nói thẳng)

- **Không tách được khi hệ vô định.** Nhiều mã trùng ex-date mà chỉ 1 tài khoản nắm giữ ⇒ chịu, giữ
  `UNVERIFIED`. Đây là **giới hạn dữ liệu**, không phải thiếu sót cài đặt — DNSE không phát hành số
  dư cổ tức theo từng mã.
- **`STOCK_SUSPECTED` phát hiện bằng biến động `openQuantity` tại ex-date là dấu hiệu YẾU** — cổ
  phiếu thưởng thường về tài khoản sau ex-date vài tuần, không đúng ngày. Sự kiện thưởng CP có thể
  lọt qua thành `UNVERIFIED` (an toàn: không cộng như tiền) chứ không được gắn nhãn đúng.
- **Phụ thuộc độ phủ của `dnse_raw_*.jsonl`.** Sự kiện trước ngày bắt đầu ghi log (06/07/2026) không
  xác minh được bằng đường này.
