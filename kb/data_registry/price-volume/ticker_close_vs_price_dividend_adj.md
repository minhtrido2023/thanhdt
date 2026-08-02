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

## Bẫy (4) — `Close/Price` KHÔNG phân biệt loại sự kiện ⇒ **KHÔNG được dùng làm nguồn SỐ LIỆU**

*(nâng cấp 2026-08-02, phản biện của user, job `Taylor_20260802_082124`)*

Cổ tức tiền mặt, cổ tức cổ phiếu, thưởng CP, chia tách, phát hành thêm — **tất cả** làm `ratio` nhảy
y hệt nhau:

| | Số lượng CP | Tiền về tài khoản |
|---|---|---|
| Cổ tức tiền mặt | KHÔNG đổi | CÓ |
| Chia tách / thưởng CP | TĂNG | KHÔNG |

Suy ngược ra "đồng/cp" từ tỉ số là **áp một giả định** (rằng sự kiện này là tiền mặt) mà chính dữ
liệu đó **không kiểm chứng được**. Vì vậy `Close/Price` **chỉ còn vai trò PHÁT HIỆN**.

## Kiến trúc 3 tầng — mỗi tầng một vai trò, KHÔNG lẫn lộn

| Tầng | Nguồn | Vai trò |
|---|---|---|
| **1 · PHÁT HIỆN** | `tav2_bq.ticker` `Close/Price` | "mã nào, ngày nào có sự kiện" + ước lượng thô để khoanh cửa sổ ngày đi tra broker, và làm **lưới an toàn** phát hiện phương trình bị nhiễm. **Không bao giờ là con số vào báo cáo.** |
| **2 · ĐO LƯỜNG** | `cashDividendReceiving` (DNSE, `dnse_raw_*.jsonl`) | **SỐ CHÍNH THỨC** (đồng/cp) — tiền mặt thật đã về |
| **3 · ĐỐI SOÁT** | `ticker_financial.Dividend_1Y` delta | xác nhận độc lập, **trễ theo quý**, không bao giờ ghi đè tầng 2 |

### BigQuery KHÔNG có cột raw per-event (đã quét toàn bộ, 2026-08-02)

Có đúng **một** bảng đúng hình dạng cần tìm — `tav2_bq.shares_outstanding_live`
(`ex_date` + `cash_div_per_share` + `stock_div_ratio` + `price_adj_factor`) — nhưng nó chỉ có
**4 dòng** (ACB/HDC/EVG/DDV, tháng 6/2026), do Winston chạy tay `update_shares_live.py` khi cần
override `OShares`, **không phải chuỗi lịch sử cổ tức**; 0 dòng cho cả 6 sự kiện tháng 7/2026.
Dùng làm **ưu tiên 1 khi có** (đã phân loại sẵn tiền/cổ phiếu), nhưng không coi là nguồn có sẵn.

⚠️ Grep cột theo chuỗi `'divid'` sẽ **bỏ sót** `cash_div_per_share` (chỉ chứa `div`) — lỗi này đã
xảy ra thật. Tìm theo `div` / `corp` / `ex_date` / `split` / `payout`, quét **cả 5 dataset**
(`tav2_bq`, `tav2_mike`, `tav2_pin`, `tav2_monitor`, `recommend_v23`).

### Tầng 2 là một HỆ PHƯƠNG TRÌNH, không phải phép chia

`cashDividendReceiving` là số dư **của TOÀN TÀI KHOẢN** — delta của nó là **theo NGÀY, không tách
theo mã**. Nhiều mã cùng ngày chốt quyền rơi chung một delta ⇒ **không** chia được `delta / qty`:

    với mỗi (tài khoản a, ngày d):   delta(a,d) = Σ_mã  qty(a, mã) × per_share(mã)

Hai tài khoản có **tỉ lệ nắm giữ khác nhau** → hai phương trình độc lập → hệ 2×2 ngày 23/07 (CTG và
VCB cùng ex-date) có **nghiệm duy nhất**, suy hoàn toàn từ tiền thật:

    2300·CTG + 1300·VCB = 1.620.000   (SpaceX)     ⇒ CTG = 450
    1050·CTG +  800·VCB =   832.500   (ZaloPay)    ⇒ VCB = 450

Giải theo từng **thành phần liên thông**. Vô định (nhiều mã trùng ex-date mà chỉ 1 tài khoản nắm
giữ) hoặc dư số lớn ⇒ giữ `UNVERIFIED`, **cấm vào báo cáo** — không lấp bằng ước lượng tỉ số.

⚠️ **Mỗi sự kiện chỉ được gán vào ĐÚNG MỘT ngày** trong cửa sổ `{ngày cuối còn quyền, ex-date}` —
khoản phải thu chỉ được ghi một lần. Bẫy thật: ex-date của NCT (27/07) **trùng** ngày-cuối-còn-quyền
của SAB (27/07); để cửa sổ rộng thì NCT bị đếm ở cả hai ngày, hệ mâu thuẫn, hỏng cả hai mã.

### Tầng 3 KHÔNG BAO GIỜ được ghi đè tầng 2

`Dividend_1Y` là **tổng TRAILING 1 năm**, cập nhật theo **chu kỳ báo cáo quý**:
- **Độ trễ**: kỳ gần nhất của SAB là 23/07 < ex-date 28/07 ⇒ chưa xuất hiện, không kết luận được.
- **Delta có thể ÂM**: SAB `5.000 → 2.000` (Δ −3.000) là một cổ tức **cũ rơi khỏi cửa sổ 1 năm**,
  không liên quan cổ tức mới. Đọc như "cổ tức mới" là sai cả dấu.

## Bẫy (5) — số broker là **GỘP**; thuế TNCN 5% trừ lúc **CHI TRẢ** (thêm 2026-08-02)

Cổ tức tiền mặt của **cá nhân cư trú** chịu thuế TNCN **5%**, khấu trừ **tại nguồn** bởi tổ chức chi
trả (nhà đầu tư không tự kê khai, không quyết toán lại theo biểu lũy tiến).
Căn cứ: **Thông tư 111/2013/TT-BTC Điều 10** (thuế suất 5% với thu nhập từ đầu tư vốn) + **Điều 25**
(khấu trừ tại nguồn); **Luật Thuế TNCN số 109/2025/QH15**, hiệu lực **01/07/2026** — tức ĐANG chi
phối chính các sự kiện tháng 7/2026 — **GIỮ NGUYÊN mức 5%** cho thu nhập từ đầu tư vốn.

**`cashDividendReceiving` của DNSE ghi số GỘP** theo mệnh giá công bố. Đây **KHÔNG phải suy đoán từ
thông lệ** — đo được bằng tiền thật trên ca chi trả MBB của SpaceX ngày **17/07/2026**:

| | 16/07 | 17/07 | Δ |
|---|---:|---:|---:|
| `cashDividendReceiving` | 3.255.000 | 855.000 | **−2.400.000** (= 2.400cp × 1.000đ, đúng mệnh giá ⇒ GỘP) |
| `availableCash` *(sau khi trừ khoản rút Trứng vàng 302.108.211)* | 2.925 | 2.282.925 | **+2.280.000** (RÒNG) |
| chênh lệch | | | **120.000 = 5,00% chính xác** |

Hằng đẳng thức dùng để tách: **`totalCash == availableCash + cashDividendReceiving + depositInterest`**
— khớp **từng đồng** cả 16/07, 17/07, 20/07. Không có nhiễu: `positions` 16/07 vs 17/07 **không đổi
một mã nào** (không lệnh khớp), lãi tiền gửi chỉ +37đ. Khoản rút 302.108.211đ **không phải giả định
ép cho khớp** — xác nhận độc lập bởi `data/execution_logs/nav_snapshot_SpaceX_2026-07-17.json`
(`offbook_assets`, chuyển Trứng vàng, job `Mafee_20260716_164743`) và bằng `withdrawableCash` 16/07 =
đúng 302.108.211.

**Hệ quả bắt buộc:**
1. Tỉ suất per-position công bố phải cộng cổ tức **RÒNG**; luôn in kèm **GỘP + số thuế**, không thay
   số lặng lẽ (`--div-tax-rate`, mặc định `0.05`).
2. **Khoản còn ở dạng phải thu vẫn ghi GỘP** ⇒ `totalCash`/NAV đang **cao hơn thực tế đúng 5% của
   phần chưa chi trả** (31/07: SpaceX 488.750đ = 0,052% NAV; ZaloPay 322.675đ = 0,036% NAV). Nhỏ
   nhưng có thật — báo cáo phải nói ra.
3. Thuế suất là **tham số**, không hardcode: tài khoản tổ chức/quỹ có chế độ khác (Luật 109/2025 còn
   **giảm 50%** thuế cho lợi tức chia từ **quỹ đầu tư chứng khoán / bất động sản**, và miễn thuế
   chuyển nhượng chứng chỉ quỹ mở nắm giữ ≥2 năm). **SpaceX + ZaloPay đều là tài khoản CÁ NHÂN ⇒ 5%.**

⚠️ **Cơ sở thực nghiệm là n=1.** Tới 02/08/2026 mới đúng **một** sự kiện chi trả thật; 5 sự kiện còn
lại vẫn nằm ở khoản phải thu (SpaceX 9.775.000đ, ZaloPay 6.453.500đ — chưa hề giảm). Mức 5% có căn
cứ pháp lý vững và số đo khớp tuyệt đối, nhưng **sự kiện chi trả thứ hai phải được đối chiếu lại
theo đúng bảng trên** trước khi coi là quy luật đã đóng. Ghim ở `_selfcheck()` **mục 15**.

## BẮT BUỘC DÙNG — `mike/bin/dividend_adjusted_return.py`

Mọi báo cáo (ngày/tuần/tháng) và mọi phép tính tỉ suất per-position **PHẢI** đi qua helper này, không
tự viết lại công thức:

```bash
# Làm báo cáo: GIẢI CẢ RỔ — mới đủ phương trình tách những ngày nhiều mã cùng chốt quyền.
python3 mike/bin/dividend_adjusted_return.py --resolve MBB,BID,CTG,VCB,NCT,SAB \
    --from 2026-07-01 --to 2026-08-01
# Một vị thế:
python3 mike/bin/dividend_adjusted_return.py --ticker NCT --from 2026-07-21 --to 2026-07-31 \
    --cost 94360 --qty 500 --account SpaceX
python3 mike/bin/dividend_adjusted_return.py --selfcheck    # offline, không cần BQ/log
```

Helper gắn cờ trạng thái xác minh:

- `CASH_CONFIRMED` — `per_share` **giải ra từ tiền mặt broker thật** (số **GỘP**, xem Bẫy 5) →
  **được phép** dùng trong báo cáo, sau khi trừ thuế qua `PositionReturn`.
- `STOCK_SUSPECTED` — số lượng CP đổi tại ex-date → nghi chia tách, **không** cộng vào tử số.
- `UNVERIFIED` — chưa xác minh được → **CẤM** đưa vào báo cáo gửi nhà đầu tư. Nếu lý do là "hệ vô
  định", chạy lại bằng `--resolve` với **đủ rổ mã** thì thường tách được.

**Giới hạn còn lại (nói thẳng):** hệ vô định không tách được là **giới hạn dữ liệu** — DNSE không
phát hành số dư cổ tức theo từng mã. `STOCK_SUSPECTED` dò bằng biến động `openQuantity` tại ex-date
là dấu hiệu **yếu** (cổ phiếu thưởng thường về sau ex-date vài tuần) — sự kiện thưởng CP có thể lọt
thành `UNVERIFIED` (an toàn: không cộng như tiền) chứ không được gắn nhãn đúng. **Ngược lại cũng có
dương tính giả**: một lệnh **mua/bán thật** khớp đúng cửa sổ ex-date cũng làm `openQuantity` đổi ⇒
cổ tức tiền mặt thật bị gắn `STOCK_SUSPECTED` và **nén xuống 0**. Cả hai chiều đều sai theo hướng
**thiếu, không bao giờ thừa** (fail-closed) — chấp nhận được cho báo cáo gửi NĐT, nhưng khi thấy một
mã "mất" cổ tức thì kiểm tra xem hôm đó có giao dịch không trước khi nghi code hỏng
(selfcheck mục 13 ghim ca này). Đường xác minh này
chỉ phủ từ ngày bắt đầu ghi `dnse_raw_*.jsonl` (06/07/2026).

## Liên quan — lỗi NAV đếm hai lần cổ tức (khác lỗi trên, độc lập)

DNSE ghi `cashDividendReceiving` vào cuối **ngày cuối cùng còn hưởng quyền**, trong khi `mtm_stock`
ngày đó vẫn dùng giá **còn quyền**. `daily_nav_snapshot.py` lấy `cash = totalCash` (đã gồm cổ tức
phải thu) ⇒ **cộng hai lần**, tự triệt tiêu phiên sau. Ảnh hưởng NAV 5 dòng trong tháng 7/2026
(SpaceX 16/07, 24/07, 27/07; ZaloPay 16/07, 24/07) và tỉ suất TUẦN của 2 tuần cuối tháng; **không**
ảnh hưởng tỉ suất tháng. Chưa sửa chuỗi lịch sử — việc cần làm 5b, báo cáo tháng 7 Mục 8.5.

## Nguồn

- Job `Taylor_20260802_060243` (2026-08-02) — phát hiện + sửa 3 báo cáo.
- Job `Taylor_20260802_082124` (2026-08-02) — phản biện của user: đổi vai trò `Close/Price` thành
  **chỉ phát hiện**, số chính thức lấy từ tiền broker qua hệ phương trình. Bằng chứng + đối soát đủ
  6 sự kiện: `mike/agents/Taylor/exp_div_broker_solve/` (`README.md`, `reconcile_july.txt`).
  **Số liệu KHÔNG đổi** (6/6 khớp phương pháp cũ) ⇒ 3 báo cáo tháng 7 không phải phát hành lại.
- Bằng chứng độc lập thứ 2: Winston job 2026-07-31 (`cashDividendReceiving` jump 744 × 3.000 cho SAB).
- Báo cáo tháng 7/2026 Mục 8.4 / 8.5 / 10.2 (cạm bẫy #4, #5).
- Job `Taylor_20260802_143541` (2026-08-02) — **Bẫy (5), thuế TNCN 5%**: user phát hiện số đang dùng
  là GỘP. Tiền đề ban đầu ("chưa sự kiện nào settle, chỉ suy được từ thông lệ") **SAI** — ca MBB
  17/07 ĐÃ chi trả và cho phép đo trực tiếp 5,00%. Báo cáo:
  `mike/agents/Taylor/research/dividend_tax_5pct_20260802.md`.
  Luật: [TT 111/2013/TT-BTC](https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-111-2013-TT-BTC-Huong-dan-Luat-thue-thu-nhap-ca-nhan-va-Nghi-dinh-65-2013-ND-CP-205356.aspx)
  Đ.10+Đ.25; [Luật TNCN 109/2025/QH15](https://xaydungchinhsach.chinhphu.vn/gioi-thieu-luat-thue-thu-nhap-ca-nhan-so-109-2025-qh15-119260123145437408.htm)
  (hiệu lực 01/07/2026, giữ nguyên 5%).

↩ [Về index nhóm](index.md)
