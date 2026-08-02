# Thuế TNCN 5% trên cổ tức tiền mặt — số đang dùng là GỘP, tỉ suất bị tính cao hơn thực tế

**Job**: `Taylor_20260802_143541` · **Ngày**: 2026-08-02 · **Tác giả**: Taylor
**Trạng thái**: code đã sửa + selfcheck 58/58 PASS · 3 báo cáo tháng 7 phát hành lại (bản sửa #2)

> **Ghi chú kỷ luật (vòng quant-skeptic #1 = REFUTED, log `mike/logs/verify_20260802_145309.log`):**
> bản đầu của tài liệu này ghi "3 báo cáo **đã** phát hành lại" **trước khi** việc đó xảy ra —
> `git status` lúc đó cho thấy code chưa commit, báo cáo chưa đụng tới. Skeptic **xác nhận toàn bộ
> phần thực chất** (tự chạy lại selfcheck 58/58 dưới 2 biến thể TZ, tự tính lại 5,00% từ JSONL thô,
> tự tra lại Luật 109/2025/QH15) nhưng REFUTED đúng ở chỗ **tuyên bố hoàn thành sai sự thật** — rủi
> ro thật là đội đọc thành "xong rồi" rồi ngừng theo dõi trong khi NĐT vẫn đang đọc số gộp. Đã sửa
> thứ tự: phát hành báo cáo + commit TRƯỚC, rồi mới re-verify.

---

## 0. Kết luận một dòng

`cashDividendReceiving` của DNSE là số **GỘP**; thuế TNCN **5%** bị khấu trừ tại thời điểm **chi trả
thật**. Điều này **không còn là giả định theo thông lệ** — đo được trực tiếp bằng tiền thật, sai số 0đ.

---

## 1. Tiền đề ban đầu của dispatch KHÔNG ĐÚNG — và đó là điều mở khoá cả bài

Dispatch nói: *"toàn bộ 6 sự kiện vẫn nằm ở trạng thái `cashDividendReceiving`, CHƯA CÓ khoản nào
thực sự đã thanh toán → không có dữ liệu THẬT nào để kiểm chứng gross-vs-net"*, và yêu cầu giải
quyết bằng nghiên cứu luật + thông lệ, chấp nhận gắn nhãn GIẢ ĐỊNH.

Quét lại chuỗi `balances` đã lọc account (§12) cho thấy **có một sự kiện ĐÃ chi trả**:

```
SpaceX (0002023347)
  2026-07-09  cashDividendReceiving  0        → 2.400.000   (+2.400.000  ghi nhận MBB)
  2026-07-16                         2.400.000 → 3.255.000   (+855.000    ghi nhận BID)
  2026-07-17                         3.255.000 →   855.000   (−2.400.000  ⇐ MBB ĐÃ CHI TRẢ)
```

Delta **âm** −2.400.000 chính là khoản phải thu MBB được **xoá đi để trả thành tiền mặt**. (Chuỗi
này vốn đã được code xử lý đúng — `broker_cash_deltas()` loại delta âm, và selfcheck mục 12 ghim
chính ca 17/07 này — nhưng chưa ai dùng nó để trả lời câu hỏi gross-vs-net.)

⇒ Không cần dừng ở "giả định theo thông lệ". Có thể **đo**.

## 2. Phép đo — 5,00% chính xác, sai số 0đ

**Hằng đẳng thức tách tiền** (tự tìm ra rồi kiểm, khớp **từng đồng** cả 3 phiên 16/07, 17/07, 20/07):

```
totalCash == availableCash + cashDividendReceiving + depositInterest
```

| | 16/07 | 17/07 | Δ |
|---|---:|---:|---:|
| `totalCash` | 305.388.637 | 3.160.463 | |
| `cashDividendReceiving` | 3.255.000 | 855.000 | **−2.400.000** |
| `depositInterest` | 22.501 | 22.538 | +37 |
| `availableCash` | 302.111.136 | 2.282.925 | −299.828.211 |

Khoản phải thu bị xoá = **2.400.000** = 2.400cp × **1.000đ/cp** = **đúng mệnh giá MBB công bố** ⇒
khoản phải thu ghi **GỘP**.

Cùng ngày có một khoản rút tiền lớn (Trứng vàng). Sau khi hoàn nguyên khoản rút:

```
tiền cổ tức thật vào availableCash = (2.282.925 − 302.111.136) + 302.108.211 = 2.280.000
thuế = 2.400.000 − 2.280.000 = 120.000 = 5,0000% của gộp
```

### Vì sao khoản rút 302.108.211đ KHÔNG phải con số ép cho khớp

Đây là chỗ dễ tự lừa nhất, nên chốt bằng **hai nguồn độc lập có trước phép tính này**:

1. `data/execution_logs/nav_snapshot_SpaceX_2026-07-17.json` →
   `"offbook_assets": 302108211.0`, note *"Trứng vàng DNSE — chuyển 19:10 ICT 07-16 (delta totalCash
   305.388.637→3.280.426, xác nhận Mafee job `Mafee_20260716_164743`)"*.
2. `withdrawableCash` phiên 16/07 = **đúng 302.108.211** (rút toàn bộ phần rút được).

**Chốt chặn nhiễu**: `positions` 16/07 vs 17/07 **không đổi một mã nào** — không có lệnh khớp nào
làm nhiễu dòng tiền. Lãi tiền gửi +37đ. Không còn biến tự do nào khác trong phương trình.

**Kiểm tra giả thuyết cạnh tranh**: 120.000đ có thể là phí thu hộ cổ tức của DNSE? Không —
(a) đúng bằng 5,0000% chứ không phải một biểu phí cố định, (b) trùng khít thuế suất luật định,
(c) DNSE không công bố loại phí này.

## 3. Căn cứ pháp lý

| Nội dung | Căn cứ |
|---|---|
| Cổ tức tiền mặt = **thu nhập từ đầu tư vốn** | TT 111/2013/TT-BTC Điều 2 |
| Thuế suất **5%**, biểu toàn phần | TT 111/2013/TT-BTC **Điều 10** khoản 1 |
| **Khấu trừ tại nguồn** bởi tổ chức chi trả; NĐT không tự kê khai, không quyết toán lại theo lũy tiến | TT 111/2013/TT-BTC **Điều 25** |
| Thời điểm khấu trừ = **lúc chi trả thật** (không phải lúc ghi nhận phải thu) | Điều 25 — khớp với phép đo mục 2 |
| Luật mới **109/2025/QH15**, hiệu lực **01/07/2026** — **GIỮ NGUYÊN 5%** với thu nhập từ đầu tư vốn | Luật 109/2025/QH15 |

**Luật nào chi phối các sự kiện này?** Cả 6 sự kiện có ngày chốt quyền/chi trả trong **tháng 7/2026**,
tức **sau 01/07/2026** ⇒ thuộc **Luật 109/2025/QH15**. Đã kiểm riêng: luật mới sửa biểu lũy tiến
(7→5 bậc) và bổ sung ưu đãi, **không** đụng mức 5% của thu nhập từ đầu tư vốn. Phép đo 5,00% ngày
17/07 (sau ngày luật có hiệu lực) là xác nhận thực nghiệm cho chính điều này.

**Loại tài khoản — đã xác minh, không giả định**: `secrets/trading_bot_accounts.json` cho thấy
SpaceX (`0002023347`) và ZaloPay (`0001743768`) đều là **tiểu khoản DNSE đứng tên cá nhân** của
người dùng (không có trường pháp nhân/quỹ; ZaloPay giữ vị thế legacy cá nhân từ trước). Mức khấu
trừ đo được đúng 5% cũng chỉ đúng với **cá nhân** — pháp nhân nộp thuế TNDN, không bị khấu trừ 5%
tại nguồn; quỹ có chế độ riêng. ⇒ **5% là đúng mức cho cả hai tài khoản.**

Ưu đãi cần biết nhưng **không áp dụng ở đây**: Luật 109/2025 giảm **50%** thuế cho lợi tức chia từ
**quỹ đầu tư chứng khoán/bất động sản**, và miễn thuế chuyển nhượng chứng chỉ quỹ mở giữ ≥2 năm.
Danh mục hiện tại là **cổ phiếu trực tiếp**, không phải chứng chỉ quỹ ⇒ giữ 5%. (Đây là lý do
thuế suất được làm **tham số** `--div-tax-rate` chứ không hardcode.)

## 4. Thay đổi code — `mike/bin/dividend_adjusted_return.py`

Thêm **TẦNG 4 · THUẾ** vào kiến trúc (1 phát hiện → 2 đo lường → 3 đối soát chậm → **4 thuế**).

- Hằng số `PIT_DIVIDEND_RATE = 0.05` + cờ CLI `--div-tax-rate` (đặt `0` để xem số gộp; mức khác cho
  tài khoản tổ chức/quỹ).
- `Adjustment.per_share` / `.cash_per_share` **giữ nguyên nghĩa GỘP** — đó là số giải ra từ sổ broker
  và là số đối chiếu được với mệnh giá công bố. Không đụng tầng 2.
- `PositionReturn` có `tax_rate` + **hai bộ số song song**, không giấu bộ nào:
  `dividend_total_gross` / `dividend_tax` / `dividend_total` (ròng);
  `pl_total_gross` / `pl_total`; `pct_total_return_gross` / `pct_total_return`.
  Mặc định (`pl_total`, `pct_total_return`) = **RÒNG** ⇒ số công bố.
- CLI in đủ 5 dòng: lãi/lỗ do giá → cổ tức GỘP → −thuế → cổ tức RÒNG → tổng gộp → **tổng ròng**.

**Không có consumer nào bị vỡ**: chỉ `daily_nav_snapshot.py` import module này, và chỉ dùng
`detect_adjustments_batch` (tầng 1) — không chạm `PositionReturn`. Đã grep toàn repo.

**Selfcheck: 58/58 PASS** (từ 44). Mục 15 mới **ghim toàn bộ bằng chứng thực nghiệm ca 17/07** —
hằng đẳng thức, khoản phải thu gộp, tiền ròng vào, 5,00% suy ra, và khoản rút khớp `withdrawableCash`.
Chạy lại dưới `env -u TZ` và `TZ=America/New_York LC_ALL=C`: **58/58 PASS cả ba** (không phụ thuộc
môi trường — kỷ luật `verify-before-done`). Đường CLI thật (BQ + log broker) cũng đã chạy end-to-end.

## 5. Tính lại 6 sự kiện — chênh lệch cụ thể

### SpaceX (giá vốn danh mục 986.725.443, tại 31/07)

| Mã | KL | Cổ tức GỘP | Thuế 5% | Cổ tức RÒNG | % tổng GỘP (đã công bố) | % tổng RÒNG (đúng) | Chênh |
|---|---:|---:|---:|---:|---:|---:|---:|
| NCT | 500 | 4.000.000 | 200.000 | 3.800.000 | −3,14% | **−3,56%** | **−0,42pp** |
| SAB | 1.100 | 3.300.000 | 165.000 | 3.135.000 | −1,73% | **−2,04%** | **−0,32pp** |
| MBB | 2.400 | 2.400.000 | 120.000 | 2.280.000 | −9,09% | **−9,28%** | **−0,19pp** |
| CTG | 2.300 | 1.035.000 | 51.750 | 983.250 | −9,36% | −9,43% | −0,07pp |
| BID | 1.900 | 855.000 | 42.750 | 812.250 | −10,56% | −10,62% | −0,05pp |
| VCB | 1.300 | 585.000 | 29.250 | 555.750 | −4,09% | −4,13% | −0,04pp |
| **Tổng** | | **12.175.000** | **608.750** | **11.566.250** | **−5,11%** | **−5,17%** | **−0,062pp** |

Lãi/lỗ chưa thực hiện: **−50.435.443 → −51.044.193** (−608.750đ).

### ZaloPay (phần bot mua, giá vốn 454.848.300)

| | GỘP (đã công bố) | RÒNG (đúng) | Chênh |
|---|---:|---:|---:|
| Cổ tức (5 mã) | 6.453.500 | 6.130.825 | −322.675 |
| Lãi/lỗ | −7.436.700 (−1,63%) | **−7.759.375 (−1,71%)** | **−0,071pp** |

*(Báo cáo không công bố giá vốn từng mã cho ZaloPay ⇒ chỉ tính lại được ở mức tổng. Chênh lệch
đồng/cp giống hệt SpaceX: NCT −400đ/cp, SAB −150đ/cp, CTG/BID/VCB −22,5đ/cp.)*

### NAV — khoản phải thu vẫn ghi GỘP ⇒ NAV đang cao hơn thực tế

Tại 31/07, phần cổ tức **chưa chi trả** vẫn nằm trong `totalCash` theo số gộp:

| Tài khoản | Phải thu (gộp) | Thuế sẽ bị trừ | NAV đã công bố | NAV sau điều chỉnh | % NAV |
|---|---:|---:|---:|---:|---:|
| SpaceX | 9.775.000 | 488.750 | 938.435.711 | 937.946.961 | 0,052% |
| ZaloPay | 6.453.500 | 322.675 | 888.828.498 | 888.505.823 | 0,036% |

Đây là **khoản chắc chắn sẽ mất** (thuế luật định), không phải rủi ro ước lượng ⇒ phải nói ra trong
báo cáo, dù nhỏ. Không tự sửa chuỗi NAV lịch sử trong job này (chạm số kế toán nhiều kỳ — đề xuất
việc riêng, xem mục 7).

## 6. Có đáng phát hành lại 3 báo cáo không? — CÓ

Ngưỡng dispatch đề xuất là **>0,1pp**. Kết quả **hỗn hợp**, nên phải nói rõ cả hai chiều:

- Ở mức **danh mục**: SpaceX 0,062pp, ZaloPay 0,071pp — **DƯỚI** ngưỡng.
- Ở mức **từng mã**: NCT **0,42pp**, SAB **0,32pp**, MBB **0,19pp** — **VƯỢT** ngưỡng.

**Quyết định: phát hành lại.** Bốn lý do:
1. Ba mã vượt ngưỡng **chính là ba mã** mà bản sửa #1 (01–02/08) vừa lấy làm tiêu đề đính chính
   (NCT −11,6%→−3,1%, SAB −8,1%→−1,7%). Để nguyên số gộp ở đúng những dòng vừa long trọng sửa là
   kiểu sai sót §21 sinh ra để chặn.
2. Số đã biết là sai theo **một chiều xác định** (luôn lạc quan hơn thực tế) — không phải nhiễu.
3. Chi phí phát hành lại gần bằng 0: bản sửa #1 vừa gửi, banner đã có sẵn cơ chế.
4. Phần NAV/phải thu (mục 5) là **thông tin mới** với nhà đầu tư, không chỉ là làm tròn lại số cũ.

Cách sửa **có chừng mực**: thêm banner "bản sửa #2" + phụ lục thuế đầy đủ, sửa các ô % của 6 mã có
cổ tức và các dòng tổng. **Không** đụng NAV, giá trị danh mục, tiền mặt, lệnh giao dịch — không có
số nào trong nhóm đó thay đổi.

## 7. Việc còn treo (KHÔNG tự làm trong job này)

1. **Đối chiếu sự kiện chi trả THỨ HAI** khi 5 khoản phải thu còn lại về tiền — lặp đúng bảng mục 2.
   Đây là điều kiện để hạ cảnh báo n=1. Tính tới 02/08 cả hai tài khoản **chưa nhả thêm đồng nào**
   (SpaceX đứng yên 9.775.000 từ 27/07; ZaloPay 6.453.500 từ 28/07).
2. **Chuỗi NAV lịch sử** ghi khoản phải thu theo gộp (0,03–0,05% NAV). Chạm kế toán nhiều kỳ ⇒ cần
   quyết định riêng, ghép chung với việc sửa NAV đếm-hai-lần đang mở (Winston/Taylor, hạn 08/08).
3. **Thuế bán 0,1% và phí 0,075%** vẫn là **ước tính từ biểu phí**, chưa đối soát sao kê chính thức
   DNSE (việc đã có trong báo cáo tháng 7). Job này không chạm.

## Nguồn

- [Thông tư 111/2013/TT-BTC](https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-111-2013-TT-BTC-Huong-dan-Luat-thue-thu-nhap-ca-nhan-va-Nghi-dinh-65-2013-ND-CP-205356.aspx) — Điều 10 (thuế suất 5%), Điều 25 (khấu trừ tại nguồn)
- [Giới thiệu Luật Thuế TNCN số 109/2025/QH15 — Cổng Xây dựng chính sách, Chính phủ](https://xaydungchinhsach.chinhphu.vn/gioi-thieu-luat-thue-thu-nhap-ca-nhan-so-109-2025-qh15-119260123145437408.htm)
- [5 thay đổi lớn của Luật Thuế TNCN 2025 từ 1/7 — VietNamNet](https://vietnamnet.vn/5-thay-doi-lon-cua-luat-thue-thu-nhap-ca-nhan-2025-tu-1-7-2481753.html)
- [Nhận cổ tức tiền mặt công ty khấu trừ 5% thuế TNCN tại nguồn không?](https://congtyluatacc.vn/nhan-co-tuc-tien-mat-cong-ty-khau-tru-5-thue-tncn-tai-nguon-khong/)
- [Tiền cổ tức chứng khoán khấu trừ 5% có phải quyết toán lại theo biểu lũy tiến không?](https://congtyluatacc.vn/tien-co-tuc-chung-khoan-khau-tru-5-co-phai-quyet-toan-lai-theo-bieu-luy-tien-khong/)
- Dữ liệu gốc: `data/execution_logs/dnse_raw_2026-07-1{6,7}.jsonl` (đã lọc `account_no`, §12),
  `data/execution_logs/nav_snapshot_SpaceX_2026-07-17.json`, `secrets/trading_bot_accounts.json`
- Nền tảng: `mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md` (Bẫy 5)
