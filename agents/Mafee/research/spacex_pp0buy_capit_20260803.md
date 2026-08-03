# SpaceX `pp0Buy` thật cho rổ CAPIT — đo 2026-08-03 (READ-ONLY)

Job `Mafee_20260803_120648`. Mục đích: lấp GAP "pp0Buy SpaceX chưa hề có bản ghi thật" mà chuỗi
nghiên cứu margin/Kelly (Taylor, p1–p5, 2026-08-03) ghi là mở từ đầu.

**Read-only tuyệt đối**: chỉ `GET` (`/price/*`, `/accounts/{acc}/ppse`, `/accounts/{acc}/balances`,
`/accounts/{acc}/loan-packages`). KHÔNG đặt lệnh, KHÔNG đổi gói vay của tài khoản, KHÔNG sửa file
production. Không có trading-token trong phiên này (`⚠ chưa có trading-token (SpaceX) — inquiry OK,
đặt lệnh sẽ bị từ chối`) → về mặt kỹ thuật cũng không thể đặt lệnh.

- Tài khoản: **SpaceX `0002023347`** (DNSE, live).
- Hàm production dùng nguyên trạng: `DNSEBroker.get_buying_power(symbol, price)`
  (`trading_bot/brokers.py:430`) → `GET /accounts/{acc}/ppse` → field `pp0Buy`.
- Giá lấy qua `DNSEBroker.get_quote()` (đúng đường production, `Quote.last` đã chuẩn hoá VND).
- Script probe: `mike/agents/Mafee/probe_pp0buy_spacex_20260803.py` (mới, không nằm trong
  đường chạy production nào).
- Thời điểm gọi: **2026-08-03 19:09:44–19:09:47 ICT** (sau giờ khớp lệnh; giá = khớp cuối phiên
  hôm nay 14:45).

## Kết quả — 5 mã rổ CAPIT (episode CAPIT-2026-07-20)

NAV đối chiếu = **938.435.711 VND** (dòng cuối `data/execution_logs/nav_history_SpaceX.csv`,
2026-07-31 — NAV mới nhất có sẵn; không có dòng 08-03).

| Mã | Giá (VND) | `pp0Buy` (VND) | `pp0Buy`/NAV | `qmaxBuy` gói cấu hình 1841 | `qmaxBuy` gói 1840 (đối chứng) |
|----|-----------|----------------|--------------|------------------------------|-------------------------------|
| NCT | 83.400 | 425.209.429 | 45,31% | 5.093 | 10.177 |
| PVT | 18.600 | 425.209.429 | 45,31% | 22.838 | 45.632 |
| SAB | 44.800 | 425.209.429 | 45,31% | 9.482 | 18.945 |
| SIP | 49.650 | 425.209.429 | 45,31% | 8.555 | 17.095 |
| VNM | 60.300 | 425.209.429 | 45,31% | 7.044 | 14.075 |

**`pp0Buy` GIỐNG HỆT nhau ở cả 5 mã và ở CẢ HAI gói vay** → đây là con số **cấp tài khoản**, không
phải per-symbol. Cái thay đổi theo gói là `qmaxBuy`: gói 1840 cho đúng **2×** gói 1841, khớp
`initialRate` 0,5 vs 1,0 (xem bảng gói bên dưới). Nói cách khác:

- Giá trị mua tối đa gói **1841 "GD Tiền mặt"** ≈ `pp0Buy` ≈ **425,2 tr** (5.093 × 83.400 = 424,8tr).
- Giá trị mua tối đa gói **1840 "RocketX"** ≈ **2 × pp0Buy** ≈ **849 tr** (10.177 × 83.400 = 848,8tr).

## Raw JSON — bằng chứng

Ghi tự động bởi `_log_raw` vào `data/execution_logs/dnse_raw_2026-08-03.jsonl` (5 record `ppse`,
đều có `account_no: "0002023347"`). Trích nguyên văn 2 dòng đầu:

```json
{"ts": "2026-08-03T19:09:44", "kind": "ppse", "account_no": "0002023347", "account_label": "SpaceX", "payload": {"symbol": "NCT", "price": 83400.0, "resp": {"qmaxBuy": 5093, "qmaxSell": 500, "price": 83400, "pp0Buy": 425209429}}}
{"ts": "2026-08-03T19:09:45", "kind": "ppse", "account_no": "0002023347", "account_label": "SpaceX", "payload": {"symbol": "PVT", "price": 18600.0, "resp": {"qmaxBuy": 22838, "qmaxSell": 3500, "price": 18600, "pp0Buy": 425209429}}}
```

Các lần gọi đối chứng `loanPackageId=1840` KHÔNG đi qua `get_buying_power()` nên không có trong file
raw log; raw response từ stdout của probe (mẫu NCT):

```json
{"qmaxBuy": 10177, "qmaxSell": 0, "price": 83400, "pp0Buy": 425209429}
```

## Bối cảnh tiền mặt — `GET /accounts/{acc}/balances` (cùng phiên, read-only)

```json
{"stock": {"totalCash": 14596244, "availableCash": 4821143, "depositInterest": 101,
 "totalDebt": 0, "depositFeeAmount": 762, "secureAmount": 0, "orderSecured": 0,
 "withdrawableCash": 4820381, "cashDividendReceiving": 9775000}}
```

`availableCash` chỉ **4,82 tr** trong khi `pp0Buy` = **425,2 tr** → `pp0Buy` KHÔNG phải tiền mặt
khả dụng; nó là sức mua broker tự tính, đã gồm hạn mức vay ký quỹ trên danh mục đang nắm
(`totalDebt` hiện = 0, tức chưa vay đồng nào). Cùng bản chất với đo ZaloPay 2026-07-28 (pp0Buy
25,54tr vs availableCash 5,68tr), nhưng độ lệch ở SpaceX lớn hơn hẳn vì có tài sản thế chấp lớn.

## Gói vay hợp lệ (GET `/loan-packages?symbol=NCT`, read-only)

```json
{"id": 1841, "name": "GD Tiền mặt", "initialRate": 1.0, "interestRate": 0.125, "liquidRate": 0.3, "maintenanceRate": 0.4, "type": "M", "brokerFirmBuyingFeeRate": 0.0007, "brokerFirmSellingFeeRate": 0.0007}
{"id": 1840, "name": "RocketX",     "initialRate": 0.5, "interestRate": 0.125, "liquidRate": 0.3, "maintenanceRate": 0.4, "type": "M", "brokerFirmBuyingFeeRate": 0.0007, "brokerFirmSellingFeeRate": 0.0007}
```

**Cấu hình bot hiện tại dùng gói 1841 "GD Tiền mặt"** (`secrets/trading_bot_accounts.json`,
SpaceX `loan_package_id: 1841`), KHÔNG phải 1840 "RocketX" như `data/results_registry.md` mô tả cho
V2.5. Đây đúng là hiện tượng "app đang chọn GD Tiền mặt" mà ảnh chụp màn hình của user cho thấy với
HPG — nhưng ở đây nó nằm trong **config của bot**, quan sát được trực tiếp, không phải suy diễn.
Hệ quả đo được: mọi lệnh bot đặt cho SpaceX đi kèm `loanPackageId=1841` → trần khối lượng = `pp0Buy`
(không đòn bẩy), dù tài khoản có quyền dùng 1840 (đòn bẩy 2×). Tôi KHÔNG đổi gì — chỉ ghi nhận.

## Đính chính giả định của bản dispatch

Dispatch ghi "chưa bao giờ chạy trên SpaceX". Thực tế `grep` toàn bộ `dnse_raw_*.jsonl` cho thấy
**đã có đúng 1 bản ghi `ppse` SpaceX trước hôm nay**, ngày 2026-07-29 13:00:02, cho mã **TV1**:

```json
{"ts": "2026-07-29T13:00:02", "kind": "ppse", "account_no": "0002023347", "account_label": "SpaceX", "payload": {"symbol": "TV1", "price": 19400, "resp": {"qmaxBuy": 0, "qmaxSell": 0, "price": 19400, "pp0Buy": 0}}}
```

`pp0Buy = 0` ở bản ghi đó **không** phải bằng chứng SpaceX hết sức mua: TV1 là mã UPCOM không hợp
lệ với gói 1841 (chính là sự cố `_resolve_loan_package_id` / bug TV1 07-28 trong `kb/INCIDENTS.md`).
Số 0 đó là "mã này không mua được bằng gói đang chọn", không phải "tài khoản không còn sức mua" —
đo hôm nay trên 5 mã mainboard cho 425,2 tr. Nếu ai đó từng dùng bản ghi TV1 làm cơ sở cho kết luận
"pp0Buy SpaceX ≈ 0", kết luận đó sai.

## Cảnh báo khi dùng số này

1. `pp0Buy` là ảnh chụp **19:09 ICT 2026-08-03**, sau phiên, tính trên giá đóng cửa hôm nay và
   danh mục hiện tại. Nó biến động theo giá thế chấp mỗi ngày — không phải hằng số.
2. NAV dùng làm mẫu số là của **2026-07-31**, không phải cùng ngày (`nav_history_SpaceX.csv` chưa
   có dòng 08-03) → tỷ lệ 45,31% có sai số theo biến động NAV 2 phiên.
3. Không có lỗi/exception nào trong toàn bộ phiên đo (5/5 mã trả `pp0Buy` hợp lệ, cả 5 lần đối
   chứng gói 1840 cũng thành công).
