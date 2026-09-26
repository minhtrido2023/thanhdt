# BƯỚC 1 — H3: nghiệm thu PIT `fiinprox_oshares_pit` + re-pin R3

Job `Taylor_20260926_164113` · Taylor · 2026-09-27
Nguồn: `mike/data/fiinprox_oshares_pit_20260926.csv` (6.404 dòng, 647 mã, 2013-01-02→2026-09-25)
Đối chiếu: `tav2_bq.corporate_action` qua `corp_action_lib.pricing_events` semantics
(`event_status != "not_executed"`, KHÔNG `executed_only`), codes `ISS` + `AIS`, 10.468 dòng.
Lịch phiên: `tav2_bq.ticker` ticker=VNINDEX, 3.674 phiên 2012-01-03→2026-09-25.

## 1. Khớp NGÀY

2.434 sự kiện `|delta / shares_before| ≥ 5%` (con số registry **tái lập đúng**; định nghĩa
`|delta/shares_after|` cho 2.379 — không phải con số đã pin).

| Lát cắt | ±0 | ±1 | ±3 | ±5 | ±10 |
|---|---|---|---|---|---|
| Tất cả 2.434 sự kiện | 75,8% | 80,5% | **85,7%** | 87,8% | 90,8% |
| `delta > 0` (2.337 sự kiện) | — | — | **89,2%** | 91,4% | 94,5% |
| `delta < 0` (97 sự kiện) | — | — | **4,1%** | — | — |

**`delta < 0` không thể khớp về mặt cấu trúc**: `ISS`/`AIS` chỉ mô tả CP TĂNG. 97 sự kiện giảm số
CP (mua lại/huỷ) không có event_code nào trong bảng để khớp — đó là giới hạn của `corporate_action`,
không phải lỗi của file PIT. Vì vậy con số đáng đọc là **89,2% trên nhánh tăng**.

**Cả hai đều DƯỚI ngưỡng prereg ≥90% ở ±3** ⇒ theo đúng tiêu chí đã khoá trong registry,
**KHÔNG nâng lên DERIVED**. (±5 cho 91,4% trên nhánh tăng, nhưng nới cửa sổ SAU khi thấy số là
nới ngưỡng hậu nghiệm — ghi lại để tham khảo, không dùng để phán.)

Phân bố lệch ngày (sự kiện đã khớp): `+0`:1.844 · `−1`:98 · `−2`:69 · `−3`:51 · `+1`:17 · `+2`:3 · `+3`:3.

## 2. Khớp TỶ LỆ — 98,5%

`exercise_ratio` đọc là **PHÂN SỐ** (1,0 = 100%): trong 1.874 sự kiện đã khớp ngày có
`exercise_ratio`, **1.846 (98,5%)** khớp `delta/shares_before` trong 2% + 0,2pp. 28 lệch, liệt kê ở
`h3_exratio_mismatch.csv` (đa số là `Phát hành riêng lẻ` / nhiều tranche cùng ngày).

Cột số lượng **không dùng được để đối chiếu rộng**: `shares_delta` phủ 0% dòng `ISS` (98% dòng
`AIS`), `shares_total_after` 0%/89%. Chỉ 44/2.085 sự kiện khớp-ngày có cột số lượng.

## 3. PHÁT HIỆN CẤU TRÚC — chuỗi này neo theo EX-RIGHT, KHÔNG theo ngày niêm yết bổ sung

Trong 2.085 sự kiện `delta>0` khớp ngày, **2.059 khớp `ISS.exright_date`**, chỉ 26 khớp
`AIS.effective_date`/`issue_date`. Khoảng cách `ISS exright → AIS effective` kế tiếp
(N=5.558): p25 = 47 ngày · **median 69 ngày** · p75 = 314 ngày.

Ca kiểm tay: **MBB 2016-10-24** — PIT `delta = 81.559.091` trên nền 1.631.181.818 = **5,0000%**,
trùng khít `ISS exercise_ratio = 0,05` (`Trả Cổ tức bằng Cổ phiếu`, ex-right **2016-10-24**) và
trùng khít `AIS.shares_delta = 81.559.091` — nhưng `AIS.effective_date` là **2016-12-05**, tức
**42 ngày SAU**.

**Hệ quả phải mang theo khi dùng file:** đây là con số đúng cho câu hỏi *"vốn hoá tại ngày t là bao
nhiêu"* (giá đã điều chỉnh tại ex-right thì số CP cũng phải đổi cùng ngày, mới giữ vốn hoá liên tục);
nó **KHÔNG** trả lời *"ngày t có bao nhiêu CP đã được NIÊM YẾT hợp pháp"* — câu đó phải hỏi
`AIS.shares_total_after`, trung vị muộn hơn 69 ngày.

## 4. Lớp KHÔNG khớp — 345 sự kiện (bằng chứng, không suy nguyên nhân §29)

| Lớp (phân loại bằng khoảng cách tới CA gần nhất + dấu delta) | n |
|---|---|
| `delta>0` · có CA cách 4-10 phiên | 122 |
| `delta>0` · có CA cách 11-60 phiên | 83 |
| `delta<0` · có CA cách 11-60 phiên | 58 |
| `delta>0` · mã có CA nhưng KHÔNG dòng ISS/AIS nào trong cùng năm | 27 |
| `delta<0` · mã có CA nhưng KHÔNG dòng ISS/AIS nào trong cùng năm | 23 |
| `delta>0` · CA gần nhất cách >60 phiên | 17 |
| `delta<0` · có CA cách 4-10 phiên | 4 |
| `delta<0` · CA gần nhất cách >60 phiên | 4 |
| `delta<0` · mã KHÔNG có dòng ISS/AIS nào | 4 |
| `delta>0` · mã KHÔNG có dòng ISS/AIS nào | 3 |

Theo năm: 2013:21 · 2014:44 · 2015:41 · 2016:28 · 2017:37 · 2018:35 · 2019:37 · 2020:23 · 2021:25 ·
2022:20 · 2023:7 · 2024:7 · 2025:9 · 2026:11. Theo độ lớn: 5-10%:102 · 10-25%:117 · 25-50%:61 ·
50-100%:30 · ≥100%:35. Chi tiết từng dòng: `h3_unmatched_classified.csv`.

**Không gán nguyên nhân.** Tôi chỉ đọc được: có/không có dòng CA trong cửa sổ, dấu delta, và độ phủ
CA của mã-năm. Không có bit nào trong dữ liệu đang cầm phân biệt được "provider ghi sai ngày" với
"`corporate_action` thiếu dòng" — hai giả thuyết đó cần nguồn thứ ba (bản cáo bạch / HOSE thông báo).

## 5. Tiêu chí (2) — đối chiếu 2.667 dòng restate: **0 vi phạm PIT chứng minh được**

Tái lập list restate bằng đúng định nghĩa registry (`ticker_financial.OShares` trùng khít <1 CP với
`AIS.shares_total_after` có `effective_date` SAU ngày dòng quý): **2.730 dòng** (pin 2026-08-13 là
2.667 — bảng đã lớn thêm; không phải mâu thuẫn).

| Lớp | n | Đọc thế nào |
|---|---|---|
| PIT cho số **CŨ** (lệch >0,1% so với dòng quý) | 478 | PIT đúng, rõ ràng |
| PIT = số dòng quý; **ISS ex-right ≤120 ngày TRƯỚC** ngày dòng quý | 918 | nhất quán với neo ex-right (§3): AIS chỉ là thủ tục niêm yết muộn |
| PIT = số mới; **có ex-right ≤ ngày dòng quý** (ca FPT trong registry) | 277 | dữ liệu sớm THẬT, không phải restate |
| PIT = số dòng quý; ISS ex-right gần nhất >120 ngày trước | 407 | **không xác định được** bằng CA |
| PIT = số dòng quý; mã không có ISS ex-right nào | 55 | **không xác định được** bằng CA |
| PIT không có số tại ngày đó (ngoài universe 647 mã / trước mẫu) | 595 | ngoài phạm vi |
| **Dòng PIT mang số TƯƠNG LAI mà không có ex-right nào trước đó ⇒ VI PHẠM** | **0** | — |

⇒ Trên 2.135 dòng kiểm được: **0 vi phạm**, 1.673 (78,4%) nhất quán tích cực, 462 (21,6%) **không
kết luận được** từ `corporate_action`. Tiêu chí "100% trên mẫu" của registry **không chứng minh được
100%** — nhưng cũng không có một ca ngược nào.

## 6. Kết luận status registry: **GIỮ `UNVERIFIED-PIT`**, cập nhật bằng chứng

Prereg nói ≥90% ở ±3 ⇒ 85,7% (toàn bộ) / 89,2% (nhánh tăng) = **FAIL**. Không hạ ngưỡng hậu nghiệm.
Cái đã thêm vào registry là 3 sự thật đo được: neo ex-right (median lệch 69 ngày so với AIS), khớp
tỷ lệ 98,5%, 0 vi phạm restate. Điều sẽ đóng được khoảng cách: một nguồn thứ ba cho 345 sự kiện
không khớp — **không** phải nới cửa sổ.

## 7. Re-pin R3 — |ΔCAGR| = 0,92pp > 0,3pp ⇒ **đã dừng + ghi finding riêng theo chỉ đạo** (giải thích ở §8)

Harness: `custom_basket.py` → `custom_basket_oshpit.py` (env `OSHARES_PIT=1`, ghi đè cột `OShares`
sau `ffill().bfill()`, giữ số cũ ở mã/ngày PIT không phủ) + `pt_v23_audit_2014.py` →
`engine_oshpit.py` (chỉ đổi 1 dòng import). Lệnh pin R3 nguyên văn, `EXP_TAG` mọi chân (§8).

**Chân control tái lập pin R3 BYTE-IDENTICAL**: CSV md5 `7d053e6201c9d107685ff4d1dd9d2d2a`
= đúng md5 đã pin; `28,86% / IS 27,09 / OOS 30,48 / Sharpe 1,90 / MaxDD −17,8% / Calmar 1,62 /
NAV 1.178,01B`; `self-check 0 VND` cả BAL và LAG ⇒ harness hợp lệ.

| Leg | CAGR (Δ) | IS 14-19 (Δ) | OOS 20+ (Δ) | Sharpe | MaxDD | Calmar | Final NAV | self-check |
|---|---|---|---|---|---|---|---|---|
| ctrl (= pin R3) | 28,86% | 27,09% | 30,48% | 1,90 | −17,8% | 1,62 | 1.178,01B | 0 VND |
| pit (both legs) | **29,78% (+0,92pp)** | 25,88% (**−1,21pp**) | 33,46% (**+2,98pp**) | 2,00 | −16,9% | 1,76 | 1.287,45B | 0 VND |

`[oshares_pit] n_rows=585.845 n_from_pit=582.132 (99,37%) n_kept_fin=3.713` — gần như toàn bộ panel
custom30V thực sự đổi nguồn, không phải một thay đổi bề mặt.

**KHÔNG đọc +0,92pp là alpha.** Hai lý do, cả hai đo được:
1. **IS và OOS TRÁI DẤU** (−1,21 / +2,98pp) — đúng chữ ký đã làm `t1abs`/`t1demean` bị NO-GO
   2026-09-06. Một cải thiện dữ liệu THẬT thì không có lý do gì đổi dấu giữa hai nửa mẫu.
2. **Nghi vấn cơ học chưa loại trừ**: `mcap = Close (ĐÃ ĐIỀU CHỈNH) × OShares` là chân RETURN.
   Close điều chỉnh đã hấp thụ sự kiện, nên **một bước nhảy của số CP trong chân này tạo ra một
   return GIẢ đúng bằng tỷ lệ phát hành**. Chuyển bước nhảy từ biên quý (control) về đúng ex-right
   (PIT) đổi NGÀY xuất hiện của return giả đó, và ex-right là ngày Close điều chỉnh KHÔNG rơi ⇒
   thiên lệch DƯƠNG có hệ thống trên 2.434 sự kiện ≥5%.

Đã chạy 2 chân phân rã để tách: `OSHARES_PIT_SCOPE=weight` (PIT chỉ vào `mcapw`, chân trọng số) và
`=return` (PIT chỉ vào `mcap`). Kết quả ở §8.

## 8. Phân rã weight/return — +0,92pp là ARTIFACT, hiệu ứng thật của PIT là **+0,04pp**

5 chân, cùng lệnh pin R3, chỉ khác `OSHARES_PIT` / `OSHARES_PIT_SCOPE`. `self-check 0 VND` (BAL và
LAG) ở **cả 5**.

| Leg | `mcap` (chân RETURN) | `mcapw` (chân WEIGHT) | CAGR | IS 14-19 | OOS 20+ | Sharpe | MaxDD | NAV |
|---|---|---|---|---|---|---|---|---|
| `h3ctrl`/`h3ctrl2` | fin, theo thời gian | fin | 28,86% | 27,09% | 30,48% | 1,90 | −17,8% | 1.178,01B |
| `h3pitW` | fin, theo thời gian | **PIT** | 29,69% | 27,92% | 31,31% | 1,95 | −17,2% | 1.275,88B |
| `h3pitR` | **PIT** | fin | 29,78% | 25,88% | **33,44%** | 2,00 | −16,9% | 1.286,68B |
| `h3pit` (both) | **PIT** | **PIT** | 29,78% | 25,88% | 33,46% | 2,00 | −16,9% | 1.287,45B |
| `h3ctrl3` (flat) | **hằng số**, fin | fin | 24,38% | 19,26% | 29,24% | 1,69 | −18,8% | 757,61B |
| `h3flat` | **hằng số**, PIT | **PIT** | 24,42% | 19,32% | 29,26% | 1,69 | −18,8% | 760,74B |

**Kết quả quyết định — khi bỏ bước nhảy số CP khỏi chân RETURN, hiệu ứng PIT gần như tắt:**

| So sánh | ΔCAGR | ΔIS | ΔOOS |
|---|---|---|---|
| PIT − control, chân return CÓ bước nhảy (`h3pit` − `h3ctrl`) | **+0,92pp** | −1,21pp | +2,98pp |
| PIT − control, chân return KHÔNG bước nhảy (`h3flat` − `h3ctrl3`) | **+0,04pp** | +0,06pp | +0,02pp |

⇒ Nghi vấn cơ học ở §7 được **xác nhận bằng số**: gần như toàn bộ +0,92pp là hiệu ứng của việc
CHUYỂN NGÀY bước nhảy số CP trong một chuỗi return dùng `Close` đã điều chỉnh, không phải dữ liệu
tốt hơn. Chân weight một mình (`h3pitW`) cho +0,83pp **đều trên cả hai nửa** (+0,83 IS / +0,83 OOS)
— đó là phần duy nhất có hình dạng của một cải thiện thật, nhưng nó biến mất khi chân return sạch
(`h3flat` − `h3ctrl3` = +0,04pp) ⇒ **không đứng độc lập được**, không kết luận là alpha.

**Kết luận H3 phần re-pin: Δ thật ≈ 0 đúng như kỳ vọng dispatch.** +0,92pp đã kích ngưỡng 0,3pp và
buộc dừng-ghi-finding (§7) là ĐÚNG quy trình — nó dẫn tới một phát hiện khác, ở §9.

**Chân `h3ctrl3` bản đầu (chạy không có `OSHARES_PIT_SCOPE`) tái lập md5
`7d053e6201c9d107685ff4d1dd9d2d2a`** = byte-identical với pin R3 ⇒ chứng minh code mới thêm là
**no-op tuyệt đối** khi không bật env. (Log `eng_h3ctrl3.log` chứa 2 dòng `EXIT=` vì chân flat ghi
đè cùng tên tag; dòng thứ hai là chân flat.) `h3flat` chạy 2 lần cho cùng md5
`afe6834dd3f536d480a89790d09847f7` ⇒ deterministic.

## 9. PHÁT HIỆN KÈM — chuỗi return của index custom30V cộng cả TĂNG TRƯỞNG SỐ CP vào lợi nhuận

Đây KHÔNG phải chuyện của file PIT; nó ở trong `custom_basket.py` production và đo được nhờ chân
`flat`.

**Bằng chứng, 3 dòng code:**
- Header module `custom_basket.py:19` khai công thức: `mcap_i,t = adjusted Close_i,t * OShares_i`
  — `OShares_i` **không có chỉ số t**, tức số CP là hằng số theo tên.
- Cài đặt `custom_basket.py:220` và `:1125`: `bx["mcap"] = bx["Close"] * bx["OShares"]` — `OShares`
  là cột **thay đổi theo thời gian** (as-of theo quý).
- `custom_basket.py:301`: `r = piv / piv.shift() - 1` với `piv` = pivot của `mcap`.

⇒ Mỗi lần số CP bước nhảy, chuỗi return nhận một return bằng `Sh_new/Sh_old − 1`. Vì `Close` ĐÃ
điều chỉnh (chính header, dòng 29, khai vậy), phần thưởng cổ phiếu/chia tách đã nằm trong giá ⇒
**đếm hai lần**. Còn phát hành thu tiền (rights/riêng lẻ) thì người giữ phải BỎ TIỀN thêm, cũng
không phải lợi nhuận của họ. Cả hai loại đều sai khi đưa vào một chuỗi return.

**Độ lớn đo được, không mô hình hoá:** bỏ bước nhảy khỏi chân return (giữ mọi thứ khác y nguyên,
kể cả chân weight) hạ R3 từ **28,86% → 24,38% CAGR (−4,48pp)**, NAV 1.178,01B → 757,61B,
Sharpe 1,90 → 1,69, MaxDD −17,8% → −18,8%. Kênh truyền: `level_dict` của `build_pit` chính là
chuỗi giá của **xe park custom30V** (`engine:914`, `PARK_TICKER=CUSTOM_VN30G`), và KB ghi parking
NEUTRAL đóng góp +7,4pp Full ⇒ phần lớn đóng góp đó nằm cùng kênh với artifact này.

**Kiểm tra độ lớn độc lập** (khác nguồn, khác phép tính): tăng trưởng số CP CAGR từ file PIT
2014-2026, 220 mã có ≥8 năm — median **13,53%/năm** (p25 8,42 · p75 19,97); riêng 16 mã trong rổ
đang giữ: median 16,93%. Một chuỗi return cộng thêm ~13%/năm khi đang park, nhân với tỷ lệ thời
gian park × tỷ trọng park, ra cùng cỡ với −4,48pp CAGR trên NAV tổng. Hai phép đo độc lập nhất
quán về DẤU và CỠ.

**Chưa kiểm tra, KHÔNG suy diễn (§29):** (a) park LIVE có mua 30 mã thật hay không — nếu có, NAV
thật chỉ hưởng price return, còn backtest hưởng price return + tăng trưởng CP, và khoảng cách đó
sẽ xuất hiện đúng ở kênh park; (b) bao nhiêu trong 13,53%/năm là thưởng CP (đã nằm trong `Close`)
so với phát hành thu tiền — cần `corporate_action` tách loại; (c) mọi con số pin dùng
`custom_basket` đều đi qua chân này, chưa kiểm kê. **Không sửa gì trong job này.**

**Quan hệ với bản sửa price-basis 2026-08-02** (`Taylor_20260802_083624`, `basket_price_basis_selfcheck.py`):
lần đó tách `Close` (return) khỏi `Price` (weight) — đúng và vẫn đúng. Nhưng nó **không xét** số CP
trong chân return; `basket_price_basis_selfcheck.py:199` chốt luôn kỳ vọng `mcap == Close*OShares`.
Vì vậy đây là lỗ hổng mới, không phải hồi quy của bản sửa cũ.
