# L0 — Đồng bộ THÀNH VIÊN rổ PARK (custom30V): xác nhận lỗ hổng, cơ chế backtest, thiết kế

**Job** `Taylor_20260806_172148` · **asof** 2026-08-07 (dữ liệu giá/vị thế: phiên 2026-08-06)
**Trạng thái**: NGHIÊN CỨU + THIẾT KẾ. **Không code, không wire, không đụng file production nào.**
`git diff` trong `WorkingClaude` = rỗng (chỉ thêm 1 file report trong `mike/agents/Taylor/research/`).

---

## 0. TL;DR

1. **Lỗ hổng có thật, đúng như John mô tả** — và rộng hơn mô tả. SpaceX giữ **SHS 3,14tr** đã rớt rổ
   (không cơ chế nào bán được nó) và **thiếu 16/30 mã = 17,0% trọng số rổ**. ZaloPay không có mã rớt
   rổ nhưng **thiếu 21/30 mã = 27,9% trọng số**. Active share so với rổ mục tiêu: **SpaceX 15,5%,
   ZaloPay 24,6%**.
2. **Root cause rộng hơn `compute_park_trim.py`**. L1 pro-rata theo trọng số SỐNG là *một nửa* vấn đề
   (đường BÁN không đẩy được mã rớt rổ ra). Nửa còn lại: **đường MUA live không tồn tại dưới dạng
   code** — `golive_recommend_v23.py` chỉ phát *hàng advisory* (`status="PARK_ADVISORY"`, dòng 991-998),
   việc quy ra lệnh mua là phán đoán của DollarBill từng phiên. Đây đúng mẫu §22 coding_guidelines
   (luật sống trong văn xuôi ⇒ mỗi phiên áp một kiểu): live mua hết mã trọng số lớn rồi dừng — 15 mã
   giữ là **hạng 1-7, 9-12, 16-18 theo trọng số**, không phải một lựa chọn có chủ đích.
3. **Backtest làm gì khi rổ đổi thành viên — CÂU TRẢ LỜI DỨT KHOÁT (đọc code, không đoán):**
   engine **KHÔNG hề giữ từng mã**. PARK là **MỘT chứng khoán TỔNG HỢP** (`vn30_underlying = _lvl_d`,
   `pt_v23_audit_2014.py:923`), giá = level series của rổ. Việc đổi thành viên nằm **BÊN TRONG**
   level (`custom_basket.py:1135-1146`: mỗi ngày dùng `members[active_q(d)]`, mà `active_q` trả về
   **chính ngày rebal**). ⇒ Backtest **xoay 100% rổ NGAY trong phiên rebal, chi phí 0, không trần
   thanh khoản**. Không có chuyện "bán dần theo FIFO như các mã khác" — FIFO chỉ áp cho *lô của
   chứng khoán tổng hợp*, hoàn toàn trung tính với thành viên.
4. **Vì thế "port nguyên trạng" = rebalance PARK về đúng trọng số mục tiêu TỪNG MÃ ngay tại phiên
   rebal** (bán mã rớt rổ về 0, mua mã mới), chứ không phải "bán dần". Và L0 **không phải tầng mới**:
   nó là **tổng quát hoá đúng của L1** — chỉ đổi công thức phân bổ từ `w_live_i × trim_total` sang
   `target_i − mv_i`, **0 tham số mới**. L1 hiện tại thực ra là một port *chưa đúng* của cùng cơ chế
   (engine bán chứng khoán tổng hợp = bán pro-rata **theo trọng số MỤC TIÊU**, không phải theo trọng
   số sống đã trôi).
5. **KHẨN CẤP? — KHÔNG, xét theo P&L. NHƯNG có ràng buộc THỨ TỰ cần quyết trong vài phiên tới.**
   - Đo trên 459 sự kiện rớt rổ / 48 kỳ rebal (2014→nay): giữ tiếp mã rớt rổ thêm 1 quý cho
     **drag trung bình +0,13%/quý** (tức là *có lợi* nhẹ), CI95 bootstrap theo cụm rebal
     **[−2,01; +2,95] %/năm** ⇒ **không phân biệt được với 0**. Lý do cơ chế: mã bị loại vì **thứ
     hạng THANH KHOẢN + cổng rating 8L**, không phải vì tín hiệu lợi nhuận.
   - Thiếu mã (chỉ giữ nhóm trọng số lớn): chân top-15 phủ 88% trọng số cho **−0,15%/năm**,
     CI95 [−1,37; +1,07], **tracking error 1,08%/quý** ⇒ cũng không phân biệt được với 0 về kỳ vọng,
     nhưng **phân tán thật**.
   - **Việc thật sự gấp là THỨ TỰ, không phải P&L**: L1 **đang đề xuất bán 123,83tr (SpaceX) /
     50,99tr (ZaloPay) ngay hôm nay** theo pro-rata. Nếu chuỗi trim đó chạy vài phiên trước khi đổi
     công thức, ta tiêu phí giao dịch để **khoá lại đúng cấu trúc sai**, rồi lại phải mua ngược.
     ⇒ **Đề nghị: quyết công thức phân bổ TRƯỚC khi duyệt chuỗi park_trim tiếp theo.** Việc trim
     đằng nào cũng phải làm (PARK 99% pool vs target 80%) — làm nó "kèm sửa cấu trúc" gần như miễn phí.
6. **Chi phí thực hiện một lần (đo, không ước)**: SpaceX turnover 265,1tr (41,5% PARK), phí
   0,075% = **0,20tr**; ZaloPay 129,9tr (46,7%), phí **0,10tr**. Active share sau khi làm:
   **15,5% → 1,2%** (SpaceX), **24,6% → 5,0%** (ZaloPay). Rủi ro thật không nằm ở phí mà ở
   **1 lệnh mua HPG 35,0tr (SpaceX)** — trượt giá, cần chia phiên.

---

## A. Xác nhận bằng dữ liệu thật — cả 2 account

Nguồn: `mike/bin/park_holdings.py --account <X> --json` (sổ lô FIFO từ journal, đã đối soát
broker: `reconcile_ok = True` cho cả 2), rổ mục tiêu = `data/custom30v_8l_publish.csv`
`rebal_date = 2026-08-05` (30 mã), giá = `marketPrice` broker DNSE.

### A1. Rổ đổi gì ở kỳ rebal 2026-08-05

| | Mã |
|---|---|
| **RỚT** (5) | DBC, MBS, **PC1**, **SHS**, VGC — Σ trọng số cũ **2,63%** |
| **VÀO** (5) | DDV, **HPG**, PNJ, TCM, TNG |
| one-way turnover của rổ | **9,06%** (thấp so với lịch sử: trung bình 28,53%, trung vị 29,01%) |

### A2. SpaceX (DNSE 0002023347) — PARK 638,41tr, cash khả dụng 4,82tr

| Mã | MV (tr) | w sống | Trong rổ? | w mục tiêu |
|---|---|---|---|---|
| VHM | 77,10 | 12,1% | ✔ | 10,0% |
| VCB | 76,70 | 12,0% | ✔ | 10,0% |
| CTG | 72,11 | 11,3% | ✔ | 9,1% |
| BID | 72,01 | 11,3% | ✔ | 10,0% |
| TCB | 58,40 | 9,1% | ✔ | 7,7% |
| VPB | 57,84 | 9,1% | ✔ | 7,4% |
| MBB | 57,36 | 9,0% | ✔ | 7,2% |
| LPB | 46,80 | 7,3% | ✔ | 5,8% |
| HDB | 39,83 | 6,2% | ✔ | 4,9% |
| ACB | 33,23 | 5,2% | ✔ | 4,8% |
| SHB | 17,70 | 2,8% | ✔ | 2,3% |
| TPB | 11,60 | 1,8% | ✔ | 1,5% |
| VIX | 9,59 | 1,5% | ✔ | 1,3% |
| VND | 5,01 | 0,8% | ✔ | 0,9% |
| **SHS** | **3,14** | **0,5%** | **✘ RỚT RỔ 08-05** | **—** |

- **Thiếu 16 mã** = 17,0% trọng số rổ: HPG (6,8%, hạng #8 — **mã mới, lỗ hổng lớn nhất**), VRE 2,2%,
  MSB 1,9%, VIB 1,9%, PNJ 0,7%, DCM 0,6%, DGC 0,6%, IDC 0,5%, VHC 0,4%, EVF 0,35%, PVT 0,35%,
  HAH 0,3%, HHV 0,2%, DDV 0,10%, TNG 0,09%, TCM 0,07%.
- **Active share vs rổ mục tiêu = 15,5%** (so với rổ đã chuẩn hoá trên tập khả thi: 15,5%; so với rổ
  thô 30 mã: 17,2%).
- ⚠️ **VRE/MSB/VIB/DCM/PVT… đã ở trong rổ TỪ KỲ 2026-05-05** — tức chúng chưa từng được mua, không
  phải hệ quả của rebal 08-05. Lỗ hổng đường MUA có trước, rebal chỉ làm nó lộ ra.

### A3. ZaloPay (DNSE 0001743768, cash-only) — PARK 278,21tr, cash khả dụng 5,82tr

9 mã: VCB 47,20tr (17,0%), VHM 46,26 (16,6%), BID 34,11 (12,3%), CTG 32,92 (11,8%), TCB 27,92 (10,0%),
VPB 27,66 (9,9%), MBB 26,34 (9,5%), LPB 18,30 (6,6%), HDB 17,50 (6,3%).

- **0 mã rớt rổ** đang giữ.
- **Thiếu 21 mã = 27,9% trọng số**, gồm HPG 6,8%, ACB 4,8%, SHB 2,3%, VRE 2,2%, MSB 1,9%, VIB 1,9%…
- **Active share = 24,6%.** DGC (0,57% rổ) nằm trong `excluded_tickers` ⇒ vĩnh viễn không mua được ở
  account này, phải xử lý tường minh trong thiết kế.

### A4. Vì sao L1 không bao giờ đẩy SHS ra — cơ chế, không phải cấu hình

`compute_park_trim.py:216-252`: `want_vnd = w_live_i × trim_total`. SHS chiếm 0,5% PARK ⇒ với trim
123,83tr hôm nay, phần của SHS là **609.030đ**, nhỏ hơn 1 lô (200cp × 15.700 ≈ 3,1tr) ⇒ rơi vào nhánh
`blocked: "trần/khả năng bán < 1 lô"`. Chạy thật hôm nay xác nhận đúng dòng đó. Kết luận: **pro-rata
theo trọng số sống KHÔNG BAO GIỜ tiêu diệt được một vị thế nhỏ**, dù trim bao nhiêu phiên — mỗi phiên
nó chỉ lấy 0,5% của phần trim, và luôn < 1 lô. Đây là bug thiết kế, không phải tham số cần chỉnh.

---

## B. Backtest làm gì khi rổ đổi thành viên — TRẢ LỜI CÂU HỎI CHÍNH

### B1. Cấu hình production đang chạy

`ETF_LIQ = "custompitg"` ⇒ `_PIT_PARAMS["custompitg"] = ("none", "q2m5", 3)`
(`pt_v23_audit_2014.py:202-206`) ⇒ **`rebal = "q2m5"`** (ngày giao dịch đầu tiên ≥ ngày 5 của tháng
thứ 2 mỗi quý: 02-05 / 05-05 / 08-05 / 11-05 — khớp đúng `park_rebal_date = 2026-08-05`),
`gate_rating = 3`, `top_n = 30`, `name_cap = 0,10`, `BASKET_SELECT = yieldcombo`.

### B2. PARK trong engine là MỘT chứng khoán tổng hợp, không phải 30 vị thế

```
pt_v23_audit_2014.py:913-923
    _lvl_d, _adv_d, _memdf, _bx = cb.build_pit(...)
    vn30_underlying = _lvl_d           # parking vehicle = synthetic basket level series
```
`simulate_holistic_nav.py` giữ `etf_lots` = **số "cổ phiếu" của chỉ số tổng hợp đó**, định giá bằng
`vn30_underlying.get(today)` (dòng 908-935). Nhãn giao dịch trong log là **một ticker duy nhất**
`CUSTOM_VN30EXVIC_PITG` (`pt_v23_audit_2014.py:975-978`). **Engine không biết SHS là gì.**

### B3. Đổi thành viên xảy ra Ở ĐÂU và NHANH THẾ NÀO

```
custom_basket.py:1133-1146
    def active_q(d):
        i = bisect.bisect_right(reb, d) - 1      # reb = danh sách rebal_date
        return reb[i] if i >= 0 else None
    for d in idx_dates:
        aq  = active_q(d)
        mem = members.get(aq, [])                # ← thành viên của kỳ ĐANG hiệu lực
        ... ret.loc[d] = Σ W_i × r_i             # lợi suất ngày d tính trên mem đó
```
`bisect_right(reb, d) - 1` với `d` **chính là** một rebal date ⇒ trả về `d`. ⇒ **Ngay phiên rebal,
lợi suất của PARK đã tính trên rổ MỚI với trọng số MỚI.** Không có giai đoạn chuyển tiếp, không có
"bán dần", không có carry-over.

### B4. Chi phí và trần thanh khoản của việc xoay rổ trong backtest = **0**

- `custom_basket.py` **không có bất kỳ số hạng chi phí/turnover nào** trong chuỗi lợi suất
  (`grep -nE "turnover|friction|slippage|TC\b"` → chỉ khớp 1 dòng *comment* ở header).
- Engine gọi với `etf_mgmt_fee_annual = 0.0`, `etf_tracking_drag_annual = 0.0`
  (`pt_v23_audit_2014.py:1946, 1999`).
- `etf_rebalance_friction = 0.0015` **chỉ tính khi ENGINE mua/bán ĐƠN VỊ rổ** (dòng 916, 1164, 1368,
  1421 của `simulate_holistic_nav.py`), tức dòng tiền vào/ra PARK — **không phải** việc xoay thành
  viên bên trong.
- Trần `ETF_LIQ_PCT = 0.20 × ADV_rổ` cũng chỉ áp cho dòng tiền vào/ra (`_etf_day_cap`), **không** áp
  cho việc xoay rổ.

> **⇒ Backtest ngầm giả định: xoay rổ hàng quý là MIỄN PHÍ và TỨC THÌ.** Đây là một điểm lạc quan đã
> biết của số R3 đã pin, và nó **có sẵn từ trước**, không phải do L0 tạo ra. Định cỡ:
> one-way turnover trung bình **28,53%/kỳ** × 4 kỳ × 2 chiều ⇒ **0,23%/năm @TC 0,10%**,
> **0,34%/năm @0,15%**, **0,69%/năm @0,30%** — tính trên phần vốn ĐANG PARK, không phải trên NAV.
> Không đề nghị re-pin gì ở đây; ghi lại để không ai trích 28,86% như thể đã trừ khoản này.

### B5. Hệ quả trực tiếp cho thiết kế

| Câu hỏi trong dispatch | Trả lời |
|---|---|
| rebal = `qstart` hay `q2m5`? | **`q2m5`** (custompitg) |
| Mã rớt rổ giữa 2 kỳ: bán ngay tại rebal, hay giữ tới khi cần tiền? | **Bán 100% NGAY tại phiên rebal.** Không có nhánh "giữ tới khi cần tiền" — khái niệm đó không tồn tại trong engine vì engine không giữ từng mã. |
| Có FIFO cho mã rớt rổ? | **Không.** FIFO trong engine chỉ áp cho lô của chứng khoán tổng hợp (rút tiền ra khỏi PARK), trung tính hoàn toàn với thành viên. |
| Xoay rổ có bị trần %ADV / phí không? | **Không, cả hai.** |

---

## C. Cái giá của việc lệch — ĐO, không phỏng đoán

Ba phép đo độc lập. Panel giá: `data/bq_cache/ticker/{2014..2026}.parquet`, cột `Close` (đã điều
chỉnh cổ tức — đúng vai "return leg" theo header `custom_basket.py` PRICE BASIS). Lịch sử thành viên:
48 kỳ rebal trong `custom30v_8l_publish.csv` (2014-08-05 → 2026-08-05).

### C1. Giữ tiếp mã ĐÃ RỚT RỔ thêm 1 quý tốn bao nhiêu?

n = **459 sự kiện rớt rổ / 48 kỳ**. Với mỗi sự kiện: lợi suất mã đó từ ngày rebal tới ngày rebal kế
tiếp, trừ lợi suất rổ MỚI (mua-và-giữ theo trọng số công bố) cùng cửa sổ.

| Chỉ tiêu | Giá trị |
|---|---|
| excess trung bình (mã rớt − rổ) | **−0,29%/quý** |
| trung vị | −3,12%/quý |
| bootstrap theo cụm (cụm = kỳ rebal), CI95 | **[−3,44%; +2,80%]** |
| % sự kiện mã rớt thua rổ | 57,3% |
| **drag mức DANH MỤC** (Σ w_prev × excess) | **+0,128%/quý** ⇒ **+0,51%/năm** |
| CI95 của drag danh mục (bootstrap theo kỳ) | **[−2,01%; +2,95%]/năm** |

**Đọc đúng**: dấu dương nghĩa là *giữ lại mã rớt rổ trung bình còn hơi CÓ LỢI*, nhưng CI ôm 0 rất
rộng ⇒ **không phân biệt được với 0**. Phân phối lệch mạnh (trung vị âm rõ, đuôi phải béo: một sự kiện
VHM 02-2026 đóng góp +6,0pp). **Không được trích cả dấu dương lẫn dấu âm như một edge.**

Cơ chế giải thích vì sao kỳ vọng ≈ 0: mã bị loại vì **tụt hạng thanh khoản top-30** hoặc **rating 8L
tụt quá cổng ≤3**, không vì dự báo lợi nhuận. "Rớt rổ" **không phải tín hiệu bán**.

*Giới hạn*: không tách được nhóm rớt-vì-thanh-khoản và nhóm rớt-vì-rating (file publish chỉ lưu
thành viên được chọn, không lưu lý do loại). Nếu muốn tách, phải chạy lại `build_pit` có log lý do —
chưa làm, và **không cần cho quyết định này**.

### C2. Chỉ giữ nhóm trọng số lớn (đúng hiện trạng live) tốn bao nhiêu?

49 quý. So chân "top-K theo trọng số, chuẩn hoá lại" với rổ đầy đủ:

| Chân | Phủ trọng số | Chênh/năm | CI95 | TE (sd)/quý | % quý thắng |
|---|---|---|---|---|---|
| top-14 | 86% | **−0,39%** | [−1,81; +1,01] | 1,26% | 47% |
| **top-15** (≈ SpaceX) | **88%** | **−0,15%** | [−1,37; +1,07] | **1,08%** | 51% |
| top-20 | 95% | +0,25% | [−0,33; +0,84] | 0,53% | 53% |

⇒ Kỳ vọng lệch **không phân biệt được với 0**; cái thật là **phân tán 1,1%/quý**. Nói cách khác:
live sẽ *khác* rổ đã backtest khoảng ±1%/quý một cách ngẫu nhiên — không phải thua nó một cách hệ thống.

### C3. Chi phí một lần để đồng bộ (đo trên giá và vị thế hôm nay)

Rebalance hai chiều về `target_i = 80% × pool × w_i` (chi tiết quy tắc ở §D):

| | SpaceX | ZaloPay |
|---|---|---|
| Σ BÁN | 190,9tr | 78,9tr |
| Σ MUA | 74,3tr | 51,1tr |
| Turnover | **265,1tr = 41,5% PARK** | **129,9tr = 46,7% PARK** |
| Phí @0,075% | **0,20tr** | **0,10tr** |
| Active share sau | **15,5% → 1,2%** | **24,6% → 5,0%** |
| Lệnh lớn nhất | **MUA HPG 35,0tr** | MUA HPG 15,3tr |

Turnover cao (41-47%) vì gộp **hai** việc: hạ mức PARK 638→515tr (việc của L1, đằng nào cũng phải làm)
+ sửa cấu trúc. Phần *thuần cấu trúc* = phần MUA (74,3tr / 51,1tr).

---

## D. Thiết kế L0

### D0. Nguyên tắc — L0 KHÔNG phải tầng thứ ba

L1 và L0 là **cùng một cơ chế engine**, chỉ khác chiều đo:
- Engine bán/mua **đơn vị** rổ ⇒ chỉ đổi **MỨC**; **CẤU TRÚC luôn đúng mục tiêu** (nó nằm bên trong
  chỉ số tổng hợp).
- Live giữ **hàng thật** ⇒ phải tự làm cả hai. L1 hiện chỉ làm mức, và làm bằng công thức
  (`w_live_i × trim_total`) **giữ nguyên cấu trúc sai** — tức bản thân L1 cũng là port *chưa đúng*
  của việc bán đơn vị rổ (bán đơn vị = bán pro-rata theo **trọng số MỤC TIÊU**, không phải trọng số
  đã trôi).

⇒ **Đề xuất chính: sửa công thức phân bổ trong `compute_park_trim.py`, không thêm script mới.**
**0 tham số mới.** Trigger, band 0,005, `_etf_day_cap`, trần %ADV per-name, FIFO trong mã, mọi ranh
giới cứng (§B5 của A5) **giữ nguyên 100%**.

### D1. Công thức

```
w_i        = trọng số rổ custom30V ở rebal_date ĐANG HIỆU LỰC      (custom30v_8l_publish.csv / BQ custom30v_8l)
tradable   = {i ∈ rổ : i ∉ excluded_tickers ∧ i ∉ unverified ∧ giá đọc được
                       ∧ w_i × target_park ≥ 1 lô}                  ← xem D3
w'_i       = w_i / Σ_{j ∈ tradable} w_j                             ← chuẩn hoá lại, GHI LOG phần bị loại
target_park = pool × PARK_TARGET                                    (y nguyên: pool = availableCash + park_mv)
tgt_i      = target_park × w'_i        (mã ngoài rổ ⇒ tgt_i = 0)
order_i    = tgt_i − mv_i                                           (>0 mua, <0 bán)
```
Sau đó **giữ NGUYÊN mọi tầng chặn đang có của L1** trên từng `order_i`:
trần TỔNG/phiên `_etf_day_cap` → trần per-name `LAG_ADV_PCT × adv_i × share` → làm tròn lô →
`min(qty, đang giữ, sellable)` → FIFO liệt kê lô. Phần bị cắt **carry-over sang phiên sau, không
phân bổ lại** (đúng §D2 của A5).

**Vì sao cái này tự động đóng case SHS**: `tgt_SHS = 0` ⇒ `order_SHS = −3,14tr` = bán sạch, không
còn phụ thuộc trọng số sống. Không cần luật riêng "bán mã rớt rổ".

### D2. Trigger và nhịp chạy

| | Đề xuất | Căn cứ |
|---|---|---|
| **Chiều BÁN** | Giữ **y nguyên** trigger L1: chạy **hằng ngày, vô điều kiện**, sinh lệnh khi `park_mv − target_park > 0,005 × pool` | port `PREFILL_STATE_REBAL` (`simulate_holistic_nav.py:900-916`) |
| **Chiều MUA** | Sinh lệnh khi `Σ_i max(0, tgt_i − mv_i) > 0,005 × pool` — **cùng band, cùng nhịp** | port đường sweep sau fill (`simulate_holistic_nav.py:1351-1390`), engine cũng chạy hằng ngày với cùng band |
| **Ngày rebal** | Không cần luật riêng. Ngày rổ đổi, `tgt_i` đổi ⇒ lệch vượt band ⇒ lệnh tự phát sinh phiên đó | engine xoay ngay tại rebal date (§B3) |

Không thêm "band cấu trúc" riêng ⇒ **không có tham số mới**. Hệ quả cần biết: mỗi ngày công thức đều
so `mv_i` với `tgt_i`, nhưng vì trần lô + band tổng, thực tế chỉ sinh lệnh khi lệch đủ lớn.

### D3. Ràng buộc lô — chỗ live KHÔNG THỂ trung thực, phải khai báo

Engine giữ **phần lẻ** của chỉ số tổng hợp; live phải mua theo lô 100. Ở quy mô PARK hiện tại,
các mã trọng số nhỏ **không mua nổi 1 lô**:

| Account | target_park | Mã không đạt 1 lô | Σ trọng số bị bỏ |
|---|---|---|---|
| SpaceX | 514,6tr | DGC 0,57%, IDC 0,51%, VHC 0,41%, HAH 0,32%, DDV 0,10%, TNG 0,09%, TCM 0,07% | **2,06%** |
| ZaloPay | 227,2tr | PNJ, DCM, DGC, IDC, VHC, EVF, PVT, HAH, HHV, DDV, TNG, TCM | **4,30%** |

⇒ Rổ khả thi thật: **23/30 mã (SpaceX)**, **18/30 (ZaloPay, đã trừ DGC excluded)**.
Đề xuất: **chuẩn hoá lại trọng số trên tập khả thi** (`w'_i` ở D1) và **in ra danh sách bị loại +
Σ trọng số** trong output (yêu cầu "no silent caps"). Đây là **lệch có ý thức so với backtest**, phải
ghi vào notes plan, không được im lặng.

### D4. Ranh giới cứng — giữ nguyên, thêm 2 mục

Giữ toàn bộ ranh giới của L1 (`excluded_tickers` không bao giờ đụng; CAPIT/LAG/BAL/DISCRETIONARY/
LEGACY không phải PARK; `UNVERIFIED` không sinh lệnh; sổ lệch ⇒ fail-closed; giá/tiền từ DNSE §6;
fail-closed per-name khi không đo được ADV). **Thêm:**

1. **Mã BANNED vĩnh viễn** (PC1, HVN, HSG, NKG, VJC, NVL…) **vẫn lọt vào rổ custom30V** — kiểm chứng:
   `PC1` là thành viên kỳ **2026-05-05**, `HVN` các kỳ 2025-05/2025-08, `HSG`+`PC1` kỳ 2025-11.
   Kỳ hiện tại 2026-08-05 **không có mã banned** ⇒ không chặn việc gì hôm nay, nhưng đường MUA tự
   động **bắt buộc** phải giao với danh sách banned trước khi đặt lệnh. Đây là **quyết định CHÍNH
   SÁCH cần user chốt** (backtest CÓ giữ chúng ⇒ lọc ra là lệch backtest có chủ đích, giống hệt tinh
   thần gate rating≤3 của LAG mà user đã chốt 2026-07-27).
2. **`excluded_tickers` ∩ rổ** (ZaloPay: DGC): `tgt_DGC = 0` và **không sinh lệnh bán** (DGC ở ZaloPay
   là vị thế legacy bị cấm đụng), trọng số của nó chuẩn hoá sang các mã còn lại. Ghi rõ trong notes.

### D5. Thứ tự thi công đề xuất (nếu user duyệt)

1. **P1 — sửa công thức phân bổ chiều BÁN** trong `compute_park_trim.py` (`w_live_i × trim_total`
   → `mv_i − tgt_i`). Nhỏ, khép kín, giải quyết ngay case SHS, **và làm cho chuỗi trim 123,83tr đang
   chờ chạy đúng cấu trúc**. Selfcheck theo `verify-before-done` + quant-skeptic.
2. **P2 — chiều MUA** (`compute_park_buy.py` gương của L1, hoặc thêm `orders` mua vào chính script).
   Đây là chỗ đóng lỗ hổng §22 (đường mua đang là phán đoán LLM). Cần thêm: ràng buộc nguồn tiền
   (ZaloPay cash-only, `ppse` T+0 từ tiền bán chờ về), chia phiên cho lệnh lớn (HPG 35tr).
3. **P3 — hiển thị** trong `send_plan_report.sh` (đã có mục park_trim/jit_unpark, thêm dòng "lệch
   thành viên rổ" + danh sách mã bị bỏ vì lô).

---

## E. Đánh giá mức độ khẩn — trả lời trực tiếp câu 4 của dispatch

**KHÔNG khẩn theo nghĩa P&L. CÓ ràng buộc thứ tự cần quyết trong vài phiên.**

| | Bằng chứng |
|---|---|
| Giữ SHS thêm 1 quý tốn bao nhiêu? | Kỳ vọng **không phân biệt được với 0** (C1). Riêng SHS: 3,14tr = **0,49% PARK** của SpaceX ⇒ dù giả định cực đoan mã rớt rổ thua rổ 10%/quý thì tác động = **0,05% PARK**. |
| Thiếu 16-21 mã tốn bao nhiêu? | Kỳ vọng ≈ 0 (**−0,15%/năm**, CI ôm 0), nhưng **TE 1,08%/quý** ⇒ live sẽ trôi khỏi số đã backtest theo cả hai chiều (C2). |
| Vậy tại sao vẫn phải làm? | (a) **Fidelity**: cả chương trình L1/L2 tồn tại để live == thứ đã mô phỏng; đây là lệch lớn nhất còn lại (active share 15-25%). (b) **Cơ học**: SHS *không có đường ra nào* — vấn đề sẽ tích tụ mỗi quý, mỗi kỳ trung bình rớt **9,6 mã** (lịch sử), kỳ này 5 mã. (c) **Chi phí sửa rất rẻ** (0,20tr + 0,10tr phí). |
| Vì sao vẫn có yếu tố thời gian? | **L1 đang đề xuất bán 123,83tr (SpaceX) / 50,99tr (ZaloPay) NGAY hôm nay**, pro-rata. Chạy chuỗi đó vài phiên = trả phí để **khoá lại cấu trúc sai**, rồi phải mua ngược. Đổi công thức trước ⇒ cùng số tiền trim đó **sửa luôn cấu trúc, gần như miễn phí**. |

**Khuyến nghị**: xếp vào hàng đợi **ưu tiên cao trong tuần này** (không phải hotfix trong ngày), và
**tạm hoãn duyệt chuỗi park_trim pro-rata mới** cho tới khi P1 xong — hoặc nếu cần trim gấp vì lý do
khác, chấp nhận và ghi rõ rằng phần trim đó sẽ phải sửa lại sau.

---

## F. Câu hỏi CHÍNH SÁCH cần user chốt (không phải quyết định kỹ thuật)

1. **Mã BANNED trong rổ PARK**: lọc ra hay mua theo rổ? (Backtest có giữ. Kỳ 08-05 hiện không dính,
   nhưng đường mua tự động cần luật trước khi bật.)
2. **Trọng số bị bỏ vì < 1 lô** (2,06% SpaceX / 4,30% ZaloPay): chuẩn hoá lại sang mã còn lại (đề
   xuất) hay để dư thành tiền mặt?
3. **Nhịp đồng bộ cấu trúc**: hằng ngày theo band 0,005 (đề xuất, = port đúng engine) hay **chỉ ở
   ngày rebal** (ít churn hơn, nhưng lệch engine và cần 1 luật mới)?
4. Có làm luôn cho **ZaloPay** không (không có mã rớt rổ, nhưng lệch cấu trúc **nặng hơn** SpaceX:
   24,6% vs 15,5%).

---

## G. Giới hạn của báo cáo này

- **Chưa chạy engine tier.** Mọi số ở §C là **position-tier** (lợi suất mua-và-giữ theo trọng số công
  bố), không phải NAV đầy đủ qua `simulate_holistic_nav`. Đủ để định cỡ và quyết ưu tiên; **không đủ**
  để tuyên bố tác động lên CAGR/Sharpe của R3. Nếu user muốn con số mức hệ, cần một lượt engine riêng
  (và khi đó phải khai N trials + DSR/PBO).
- **Rổ mục tiêu đọc từ CSV** `custom30v_8l_publish.csv` (do `custom30_history.py` phát trong
  `papertrade_daily.sh` bước [6b]); production `golive_recommend_v23.py` đọc **bảng BQ**
  `tav2_bq.custom30v_8l`. Hai nguồn *phải* giống nhau (cùng writer) — **chưa đối chiếu byte-level
  trong job này**; nếu thi công, đọc thẳng nguồn mà engine live đọc và thêm 1 phép so.
- **Không tách được lý do rớt rổ** (thanh khoản vs rating) — xem C1.
- Chuỗi C1/C2 dùng cache giá local `data/bq_cache/ticker/*.parquet` (không phải BQ live) — hợp lệ vì
  đây là câu hỏi **lịch sử**, không phải định giá same-day (§6).
- **Chưa qua quant-skeptic.** Bắt buộc trước khi bất kỳ dòng code nào vào production.
