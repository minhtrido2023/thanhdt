# Treasury-buyback OShares PIT overlay — thiết kế + chạy thử (2026-09-07)

Job `Taylor_20260907_160333`. Phạm vi: CHỈ lớp lỗi buyback/treasury trong `ticker_financial.OShares`
restatement đã được data-ops xác định. KHÔNG động vào EVF/SHB/TCB (3/5 ca gốc — 0 dòng
`treasury_news` bất kỳ loại nào, xác nhận lại độc lập ở dưới).

## 1. Verify độc lập (bước 1 của dispatch)

Đọc trực tiếp `tav2_bq.treasury_news` + `tav2_bq.ticker_financial` bằng `bq` CLI
(`--max_rows=200000` — mặc định 100 dòng cắt mất dữ liệu, đúng bẫy đã ghi ở CLAUDE.md).

| Mã | Quý trước→sau | OShares trước | OShares sau | Δ | Sự kiện `treasury_news` khớp | Ngày filed dòng quý | Ngày sự kiện thật |
|---|---|---:|---:|---:|---|---|---|
| VRE | 2019Q2→2019Q3 | 2.328.818.410 | 2.272.318.410 | −56.500.000 | `buy_done` 2019-12-19 | 2019-10-29 | **2019-12-19** (51 ngày SAU dòng quý, và SAU CẢ Nghị quyết HĐQT 2019-11-04) |
| HDB | 2019Q2→2019Q3 | 980.999.771 | 962.629.771 | −18.370.000 | `buy_done` 2020-01-14 (`shares_delta=18.000.000`, lệch 2,0%) | 2019-10-30 | **2020-01-14** (76 ngày sau) |
| DIG | 2019Q3→2019Q4 | 314.943.601 | 306.688.171 | −8.255.430 | `buy_done` 2020-04-28 | 2020-01-22 | **2020-04-28** (96 ngày sau) |
| DIG | 2020Q2→2020Q3 | 306.688.171 | 314.943.601 | +8.255.430 (khôi phục đúng) | `sell_done` 2020-12-04 | 2020-11-02 | **2020-12-04** (32 ngày sau) |
| GEX | 2019Q4→2020Q1 | 488.244.000 | 469.969.050 | −18.274.950 | `buy_done` 2020-05-27 | 2020-05-04 | **2020-05-27** (23 ngày sau) |

Cả 4/4 case data-ops đưa ra đều tái lập ĐÚNG bằng truy vấn độc lập — VRE khẳng định lại chính xác
độ lớn 56.500.000 (2,49%) và ngày restatement 2019-10-29 TRƯỚC CẢ Nghị quyết HĐQT (2019-11-04).

**Xác nhận EVF/SHB/TCB ngoài phạm vi**: `grep`/query `treasury_news WHERE ticker IN ('EVF','SHB','TCB')`
→ **0 dòng bất kỳ `action_type` nào** (tái xác nhận kết luận trong dispatch — luật TCTD hạn chế mua
lại CP quỹ). Không đụng tới 3 mã này.

## 2. Schema `treasury_news` — đo lại 2 giới hạn dispatch nêu

2.371 dòng. `action_type`: buy 833 · sell 569 · buy_done 369 · other 366 · sell_done 214 · cancel 20.
- `shares_delta` populate: **567/2.371 = 23,9%** (khớp con số dispatch "~24%").
- `ref_price`: **0/2.371 = 100% NULL** toàn bảng (khớp dispatch).
- Số mã có ≥1 `buy_done`/`sell_done`: **232** — khớp khít mẫu số "232 mã" trong dispatch.

## 3. Cơ chế overlay — `match_overlay.py`

**KHÔNG sửa `ticker_financial`** (dữ liệu vendor). **KHÔNG sửa `oshares_live.py`/`corp_action_lib.py`**
(theo đúng ranh giới #7 của dispatch — chờ quant-skeptic review). Overlay độc lập, đọc 2 CSV export
từ BQ (`oshares_timeseries.csv`, `treasury_events.csv`), sinh `overlay_results.csv`.

**Thuật toán** (nguồn hỗn hợp CÓ GHI RÕ trong code — độ lớn từ `ticker_financial` delta liên-quý,
ngày hiệu lực + hướng từ `treasury_news`):
1. Với mỗi mã, tính Δ liên-quý của `OShares` (bỏ qua |Δ|<1.000 cp — nhiễu làm tròn).
2. Hướng: Δ<0 → tìm `buy_done`; Δ>0 → tìm `sell_done`. Cửa sổ tìm kiếm
   `[ngày_filed_quý_trước − 10, ngày_filed_quý_sau + 150]` (đo thực nghiệm: độ trễ sự kiện thật
   sau ngày filed quý restated là 23–96 ngày trên 5 ca xác nhận tay ở mục 1; p75 toàn mẫu = 68 ngày,
   p99 ≈ 146 ngày → cận 150 ngày phủ gần hết đuôi mà không mở toang).
3. **Gộp trùng lặp báo chí trước khi match**: nhiều dòng `treasury_news` cùng
   `(ticker, public_date, action_type)` là NHIỀU NGUỒN TIN cho CÙNG MỘT sự kiện thật (bắt được ở
   CTD 2018-02-06: 2 dòng `sell_done` cùng ngày, 1 có `shares_delta=-448.500`, 1 không) — gộp thành
   1 "sự kiện logic" trước khi vào bộ so khớp, nếu không 2 Δ liên-quý KHÁC NHAU sẽ cùng "dùng" 2 dòng
   trùng lặp của MỘT sự kiện (self-check (a) bắt đúng lỗi này ở vòng chạy đầu, đã sửa).
4. **2 pha, ưu tiên độ lớn xác nhận được**:
   - Pha 1 (`HIGH`): trong các sự kiện có `shares_delta`, chọn khớp |Δ_OShares| trong dung sai
     ±25% trước (theo THỨ TỰ khớp gần nhất), tiêu thụ sự kiện ngay — tránh 1 Δ không liên quan
     "cướp" mất sự kiện đã có bằng chứng độ lớn của 1 Δ khác (ca thật: CTD 2017Q2→Q3 Δ=+1.305.000
     suýt khớp nhầm vào đúng sự kiện 448.500cp mà lẽ ra thuộc về Δ=+448.500 kế tiếp).
   - Pha 2 (`MEDIUM`): sau khi Pha 1 tiêu thụ xong, Δ còn lại chỉ được khớp nếu cửa sổ của nó còn
     ĐÚNG 1 sự kiện chưa dùng (không đoán khi có ≥2 ứng viên — để trống).
5. **Trần nghi ngờ hậu-kiểm (`SUSPECT`)**: match `MEDIUM` (không có `shares_delta` xác nhận) mà
   |Δ| > 15% tổng CP trước đó → hạ xuống `SUSPECT`, không tin thẳng. Phát hiện được NHỜ ca thật:
   **MCH** Δ=+237.755.604 (22,6% CP) khớp nhầm vào `sell_done` 2026-06-24 (ESOP), trong khi nguyên
   nhân thật là sự kiện 2025-12-25 "dùng CP quỹ chia cho cổ đông + phát hành ~227tr CP thưởng" —
   bị gắn `action_type='other'`, NGOÀI bộ lọc `buy_done`/`sell_done` nên không vào được pool ứng
   viên; Pha 2 tìm được đúng 1 ứng viên "hợp lệ theo luật" nhưng SAI về bản chất. Chương trình mua
   lại CP quỹ thật thường ≤15% tổng CP trong 1 quý — bất kỳ Δ lớn hơn đều đáng ngờ là bị gắn nhãn
   sai loại sự kiện, không phải buyback thật.

## 4. Kết quả chạy toàn bộ 232 mã candidate

- 205/232 mã có ≥1 Δ liên-quý không nhiễu (27 mã còn lại: có `buy_done`/`sell_done` trên
  `treasury_news` nhưng KHÔNG có Δ OShares nào ≥1.000cp trong `ticker_financial` — chương trình có
  thể chưa từng đổi số CP ghi nhận, hoặc quy mô dưới ngưỡng lọc nhiễu).
- **161 mã ĐÃ xử lý được** (≥1 Δ khớp `HIGH`/`MEDIUM`, tổng 314 Δ khớp: 73 `HIGH`, 209 `MEDIUM`,
  32 bị hạ `SUSPECT`) — danh sách đầy đủ: `tickers_handled.txt`.
- **13 mã CHỈ có match `SUSPECT`** (không mã nào cứu được bằng match tốt hơn) — cần điều tra tay,
  nghi vấn cùng lớp lỗi MCH (sự kiện thật bị gắn `action_type='other'`): `tickers_suspect.txt`
  (EIB, LHG, MCH, PAC, PC1, PHR, SJS, TNB, TTF, TV2, VC1, VC2, VNM).
- **28 mã CÒN lệch, KHÔNG giải thích được bằng cơ chế này** — 0 sự kiện `buy_done`/`sell_done` nào
  rơi vào cửa sổ hợp lý cho BẤT KỲ Δ nào của mã đó. Để TRỐNG, không suy đoán nguyên nhân:
  `tickers_unexplained.txt` (APH, CID, CKV, DBD, FMC, FOC, GAS, GLT, HCM, IPA, KBC, KLB, MSB, MSN,
  NAF, NDX, PIT, SAC, SBV, SGP, SGR, SIP, THW, TL4, TVS, VCR, VNI, VSA).
- Chi tiết từng Δ (khớp + chưa khớp), toàn bộ 1.980 dòng: `overlay_results.csv`.

## 5. Self-check (mục 4 của dispatch)

| # | Điều kiện | Kết quả |
|---|---|---|
| (a) | Không mã nào bị áp 2 lần cùng 1 sự kiện | **PASS** (0 dupe, sau khi gộp trùng báo chí — vòng chạy đầu FAIL trên CTD, đã sửa mục 3.3) |
| (b) | Tổng CP trước+sau khớp đúng dấu (buy giảm, sell tăng) | **PASS** (0 vi phạm trên toàn bộ 314 match) |
| (c) | VRE chạy ra đúng ngày hiệu lực 2019-12-19 | **PASS** (không phải 2019-10-29) |

## 6. Giới hạn đã biết, KHÔNG tự vá thêm trong job này

- **Bỏ sót lớp `action_type='other'`**: ca MCH cho thấy một số sự kiện thay đổi CP lưu hành thật
  (chia CP quỹ kèm phát hành mới) bị gắn `other`, không vào được pool `buy_done`/`sell_done`. Trần
  `SUSPECT` chỉ CHẶN kết luận sai, KHÔNG tự sửa được — 13 mã trong `tickers_suspect.txt` cần review
  tay `action_type='other'` riêng cho từng mã trước khi tin bất kỳ ngày hiệu lực nào.
  Vietnamese "sử dụng cổ phiếu quỹ để chia cổ tức/thưởng" là một loại sự kiện lai (vừa `sell` treasury
  vừa `ISS` phát hành mới) không khớp gọn vào taxonomy 6 `action_type` hiện có.
- **28 mã unexplained** có thể do: (i) chương trình buyback đăng ký nhưng huỷ/không hoàn tất
  (`cancel`, 20 dòng toàn bảng — chưa kiểm từng ca); (ii) Δ OShares thật ra đến từ nguyên nhân khác
  hoàn toàn không liên quan buyback (ESOP/PP/M&A trùng thời điểm, giống pattern DIG/HDB/GEX các Δ
  lớn không khớp ở mục "Δ còn lại"); (iii) cửa sổ 150 ngày chưa đủ rộng cho một số ca. KHÔNG đoán
  — để nguyên trong danh sách unexplained.
- Chưa kiểm tra `cancel` (20 dòng) — nếu một chương trình bị huỷ mà Δ OShares vẫn đổi (do nguyên
  nhân khác trùng thời điểm), thuật toán hiện tại đúng đắn bỏ qua nó (không tìm `cancel`).
- **Cửa sổ 150 ngày là số đo thực nghiệm trên mẫu quan sát được (p99≈146d), không phải hằng số lý
  thuyết** — nếu áp cho mã/giai đoạn khác có thể cần nới, quant-skeptic nên kiểm tra độ nhạy tham
  số này trước khi bất kỳ ai coi kết quả là final.

## 7. KHÔNG wire production (đúng ranh giới #7 dispatch)

Không đụng `oshares_live.py`/`corp_action_lib.py`/`corp_action_daily.py`. Đây là bằng chứng đủ để
Mike gọi `bin/verify_finding.sh` / dispatch quant-skeptic trước khi cân nhắc wire — đổi diễn giải
OShares chạm PIT backtest + report §21, cần review độc lập.

## File đính kèm
- `match_overlay.py` — script overlay (chạy: `python3 match_overlay.py` trong thư mục này).
- `treasury_events.csv` / `oshares_timeseries.csv` — export BQ dùng làm input (snapshot 2026-09-07).
- `overlay_results.csv` — 1.980 dòng, mọi Δ liên-quý của 232 mã candidate, khớp hoặc không.
- `tickers_handled.txt` / `tickers_suspect.txt` / `tickers_unexplained.txt`.
- `threshold_sensitivity.py` — sweep §8.2 (chạy: `python3 threshold_sensitivity.py`).

---

## 8. Vá theo quant-skeptic verify (job `Taylor_20260907_170327`, 2026-09-08)

### 8.1. Bug đếm — CON SỐ ĐÚNG là **162 / 14 / 29**, không phải 161/13/28

`tickers_handled.txt`/`tickers_suspect.txt`/`tickers_unexplained.txt` thiếu newline ở dòng cuối
cùng ⇒ `wc -l` (đếm bằng số ký tự `\n`) đếm thiếu đúng 1 dòng mỗi file. `awk 'END{print NR}'`
(đếm bằng số record) cho đúng: **162 handled / 14 suspect / 29 unexplained** (tổng 205, khớp
"205/232 mã có ≥1 Δ liên-quý không nhiễu" ở mục 4). Xác nhận độc lập bằng cách recompute
classification thẳng từ `overlay_results.csv` (không đọc lại 3 file .txt) — tập mã 3 nhóm
**giống hệt** bản cũ, chỉ thiếu newline chứ không sai mã nào.

Nguyên nhân: 3 file `.txt` này KHÔNG do `match_overlay.py` ghi ra ở bản gốc (chỉ có
`overlay_results.csv` được script ghi) — chúng được tạo thủ công bằng lệnh ad-hoc ở phiên trước,
lệnh đó dùng `"\n".join(...)` không kèm `\n` cuối. Đã sửa tận gốc: `main()` giờ tự phân loại
(logic giống hệt §4: handled = ≥1 Δ khớp HIGH/MEDIUM; suspect = có khớp nhưng TOÀN BỘ bị hạ
SUSPECT; unexplained = 0 Δ khớp) và ghi cả 3 file có `\n` cuối, in ra ngay trong log chạy —
`python3 match_overlay.py` giờ là nguồn tái lập DUY NHẤT cho cả `overlay_results.csv` lẫn 3 file
`.txt`, không còn bước thủ công tách rời có thể lệch.

### 8.2. Sensitivity sweep `SUSPECT_RATIO_PCT` — {10, 12, 15, 18, 20}%

Script `threshold_sensitivity.py`, chạy trên đúng `overlay_results.csv` đã pin (không chạy lại
matcher — chỉ áp lại luật hạ-cấp ở ngưỡng khác cho các dòng đã là MEDIUM/SUSPECT ở bản gốc).

**Số mã đổi tầng so với baseline 15%:**

| Ngưỡng | handled | suspect | unexplained | Mã đổi tầng |
|---|---:|---:|---:|---|
| 10% | 157 | 19 | 29 | CTI, ICG, MCG, SBT, UDJ → suspect |
| 12% | 159 | 17 | 29 | CTI, ICG, UDJ → suspect |
| **15% (baseline)** | **162** | **14** | **29** | — |
| 18% | 164 | 12 | 29 | EIB, TV2 → handled |
| 20% | 165 | 11 | 29 | EIB, TV2, VNM → handled |

**Không có khe hở tự nhiên (natural break) gần 15%.** Phân phối tỷ lệ khớp của mọi dòng
MEDIUM/SUSPECT dày đặc và liên tục trong khoảng 8–20% (8.0, 8.0, 8.4, …, 13.0, 15.0, 15.1, …,
16.1, 18.0, …) — khoảng trống lớn nhất trong toàn phân phối nằm ở đuôi xa (61pp giữa 100% và
161%, 14.8pp giữa 51.8% và 66.6%), KHÔNG nằm gần vùng 10–20% đang tranh cãi. Kết luận: **bất kỳ
ngưỡng nào trong 10–20% đều là lựa chọn TUỲ Ý xét thuần theo hình dạng phân phối.**

**Nhưng tra tay `treasury_news` cho từng mã đổi tầng (không đoán) cho bằng chứng ĐỊNH TÍNH ủng
hộ giữ 15% — không chỉ dựa 1 ca MCH như bản v1:**

- **5 mã đổi tầng ở ngưỡng thấp hơn (10-12%) — tất cả là khớp THẬT, hạ ngưỡng sẽ tạo false-negative:**
  - **CTI** 2020Q2 Δ=13,0% buy_done 2020-06-25: khớp đúng chương trình mua CP quỹ công khai
    ("muốn mua 18,9 triệu CP quỹ, tỷ lệ **30% vốn**" — công ty tự công bố quy mô lớn, 13% nằm
    trong phạm vi đã đăng ký). CTI 2025Q1 Δ=15,0% sell_done 2025-07-01: khớp lại đúng sự kiện bán
    CP quỹ 2025, không có `other` cạnh tranh trong cửa sổ.
  - **ICG** 12,1% buy_done 2019-04-03: sự kiện DUY NHẤT trong toàn lịch sử `treasury_news` của
    mã này, không mơ hồ.
  - **MCG** 10,5% sell_done 2026-05-14: sự kiện gần nhất (2026), không có `other` tranh chấp.
  - **SBT** 2018Q1 Δ=11,1% buy_done 2018-05-18: khớp đúng đợt mua công khai "hơn 1.000 tỷ đồng"
    2018 (báo chí xác nhận cùng thời điểm).
  - **UDJ** 12,9% sell_done 2021-03-29: công ty con Becamex bán "toàn bộ CP quỹ" — khớp đúng quy
    mô một lần bán dứt điểm.
- **3 mã đổi tầng ở ngưỡng cao hơn (18-20%) — cả 3 đều là khớp SAI kiểu MCH, nới ngưỡng sẽ tạo
  false-positive (đây là bằng chứng MẠNH để KHÔNG nới lên 18-20%):**
  - **EIB** 18,0% sell_done 2024-02-20: chính `treasury_news` có dòng NGAY HÔM SAU (2024-02-21)
    "**EIB chưa bán được bất kỳ cổ phiếu quỹ nào**" — MÂU THUẪN TRỰC TIẾP với việc gán event này
    giải thích cho Δ=265,5tr CP (18%). Δ thật gần như chắc chắn đến từ nguyên nhân khác.
  - **TV2** 15,9% sell_done 2016-10-31: `matched_shares_delta=-40.500` trong khi Δ liên-quý thật
    là 700.264 CP — lệch **17 LẦN**, một trong những case rõ ràng nhất toàn tập rằng sự kiện
    khớp được là ĐÚNG NGÀY/HƯỚNG nhưng SAI QUY MÔ hoàn toàn (không lọt qua Pha 1 HIGH vì lệch
    magnitude quá xa dung sai 25%, đúng theo thiết kế).
  - **VNM** 20,0% sell_done 2021-02-01: Δ=348,3tr CP (20% tổng CP) lớn hơn ~19× so với lượng CP
    quỹ mà Vinamilk thực có (chương trình mua lại lịch sử của VNM chỉ ~17-18tr CP) — sai lệch quy
    mô rõ ràng, cùng lớp lỗi MCH (Δ thật nhiều khả năng đến từ nguyên nhân khác, bị gán nhầm vào
    sự kiện `sell_done` gần nhất trong cửa sổ).

  → **15% phân tách đúng cả 8/8 ca đã tra tay** (5 ca <15% genuine ở lại handled, 3 ca ≥15,9%
  sai ở lại suspect) — bằng chứng thực nghiệm mạnh hơn hẳn 1 anecdote MCH của bản v1, dù về mặt
  thống kê thuần (hình dạng phân phối) ngưỡng vẫn là lựa chọn tuỳ ý.

**Mã có ≥1 dòng riêng lẻ nằm trong ±3pp quanh 15% (kể cả khi tầng CHUNG của mã không đổi, vì mã
đó có dòng khác cứu — vẫn cần review tay riêng dòng đó):** ICG 12,1 · CII 12,6 (dòng khác 0,6-5,3%
đã cứu tầng) · UDJ 12,9 · CTI 13,0/15,0 · KDH 15,1 (SUSPECT, dòng 3,6% khác cứu tầng) · SBT 15,8
(SUSPECT, dòng 11,1% khác cứu tầng) · TV2 15,9 · HDC 16,0 (SUSPECT, dòng khác cứu tầng) · NBB 16,1
(SUSPECT, dòng 7,0% khác cứu tầng) · EIB 18,0 · IDV 18,0 (SUSPECT, dòng HIGH 2,0% khác cứu tầng).

**Khuyến nghị:** giữ `SUSPECT_RATIO_PCT=15%` — không đổi code. Danh sách ±3pp ở trên nên được gắn
cờ review tay định kỳ (không phải vì ngưỡng sai, mà vì ĐÂY LÀ VÙNG BIÊN thực sự mong manh — bằng
chứng định tính chỉ tra được 8/11 mã trong sweep, KDH/HDC/NBB/IDV/CII chưa tra tay từng dòng biên).

### 8.3. 24 mã có event nhưng 0 dòng trong `ticker_financial`/`oshares_timeseries` — DATA GAP thật, không phải lỗi join

Query trực tiếp `tav2_bq.ticker_financial` cho cả 24 mã: **23/24 mã KHÔNG có bất kỳ dòng nào**
trong `ticker_financial` (0 rows) — hoàn toàn vắng mặt khỏi bảng vendor, không phải bị lọc mất bởi
`match_overlay.py` hay export CSV (script chỉ đọc CSV export thẳng từ BQ, không tự lọc ticker).
**1/24 (RCD)** CÓ 46 dòng trong `ticker_financial` (2015-02-06 → 2026-05-04) nhưng cột `OShares`
**NULL toàn bộ** — dữ liệu ticker có tồn tại, chỉ riêng cột OShares bị thiếu (data gap ở cấp cột,
không phải cấp ticker). Cả 24 mã đều là tên nhỏ/thanh khoản thấp (không có mã nào thuộc
`ticker_prune`/blue-chip) — khớp với mô tả đã biết ở `bigquery_dictionary.json`/`CLAUDE.md` về
độ phủ dữ liệu vendor mỏng với nhóm này. **Kết luận: DATA GAP thật của nguồn vendor, không sửa
được bằng cách vá logic overlay — nêu rõ số 24 trong report thay vì im lặng, đúng yêu cầu dispatch.**

### 8.4. Vẫn KHÔNG wire production

Không đụng `oshares_live.py`/`corp_action_lib.py`/`corp_action_daily.py`. Chờ quant-skeptic verify
lại bản v2 (bug đếm đã sửa + threshold đã sensitivity-test bằng bằng chứng, không chỉ 1 anecdote)
trước khi Mike cân nhắc wire.
