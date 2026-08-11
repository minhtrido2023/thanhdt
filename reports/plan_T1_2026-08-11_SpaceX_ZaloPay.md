# Plan giao dịch T+1 — phiên 2026-08-11 — SpaceX & ZaloPay

**Trạng thái: ĐÃ DUYỆT.** Anh đã duyệt cả 2 plan qua Discord 2026-08-11 (SpaceX 09:04:49 ICT,
ZaloPay 09:04:57 ICT, `approved_by="user (John) - Discord real-time 2026-08-11, duyệt sau khi xem
qua email+telegram"`). Trước khi ghi duyệt, phát hiện và vá 1 lỗ hổng thật trong script duyệt
(`approve_plan_simple.sh` không nhận field tiền của công cụ park-add mới, khiến gate "đủ tiền" tự
động PASS dù không tính đúng Σ mua/tiền mặt — xem mục 8) rồi verify lại bằng số liệu thật trước
khi ghi `approved_by`. Số lệnh/giá trị dưới đây khớp đúng plan đã thực thi, không đổi so với bản
chờ duyệt gửi trước đó.

| Hạng mục | SpaceX | ZaloPay |
| --- | --- | --- |
| Tài khoản DNSE | 0002023347 (có margin) | 0001743768 (cash-only) |
| Chiến lược | V2.4 | V2.4 |
| Trạng thái thị trường (DT5G) | 3 — NEUTRAL | 3 — NEUTRAL |
| NAV tổng | 974.278.258đ | 949.892.932đ |
| Active NAV (cơ sở tính tỷ trọng) | 974.278.258đ | 513.892.932đ\* |
| Số lệnh | 17 (toàn MUA) | 13 (toàn MUA) |
| Tổng giá trị lệnh | 196.055.000đ | 108.130.000đ |
| Phí ước tính | 147.042đ | 81.097đ |
| Tiền/NAV: trước → sau | 31,53% → 11,29% | 29,68% → 8,62% |
| Cổng tài trợ P0 | OK — dùng 34,7% sức mua | OK — dùng 74,1% sức mua |
| Duyệt | ✅ 09:04:49 ICT 08-11 | ✅ 09:04:57 ICT 08-11 |

\* ZaloPay có `excluded_tickers = ["DGC"]` (10.000cp ≈ 436tr) — mọi sizing V2.4 chạy trên
active_nav đã loại DGC, không phải NAV tổng.

---

## 1. Việc plan này làm, và vì sao

Chỉ đạo của anh tối 2026-08-10: *"tỷ trọng cash như vậy là quá lớn… đưa tỷ trọng cash về đúng theo
thiết kế của production… có thể đưa cash về tỷ lệ 10% bằng cách tăng tỷ lệ mua DRI và TV1 lên 5%
NAV. Cash còn dư giải ngân vào park."*

Plan thực hiện đúng hai việc đó và không làm gì khác: nâng TV1 + DRI lên 5% NAV mỗi mã (book
DISCRETIONARY_SPECIAL), rồi giải ngân phần tiền dư vào sổ PARK theo đúng rổ custom30V. Các sổ V2.4
BAL / LAG / CAPIT **không có lệnh mới nào** — không phải vì thiếu tiền, mà vì cơ chế chặn (mục 4).

**Một điểm cần nói rõ về con số 10%.** Luật production không quy định "tiền = 10% NAV". Nó quy định
PARK = 80% của *idle pool*, trong đó idle pool = tiền + PARK = NAV trừ đi CAPIT, BAL, LAG,
DISCRETIONARY. Suy ra tiền = 20% của idle pool — không phải 20% NAV. Tỷ lệ tiền/NAV mà luật này
sinh ra phụ thuộc phần NAV đang bị các sổ ngoài pool chiếm, và hai tài khoản đang nằm hai bên
ngưỡng đó:

| | Sổ ngoài pool (%NAV) | Idle pool (%NAV) | Tiền mục tiêu theo LUẬT | Tiền sau plan | Lệch so với mốc 10% anh nêu |
| --- | ---: | ---: | ---: | ---: | ---: |
| SpaceX | 44,86% | 55,15% | **11,03%** | 11,29% | +1,29pp (+12.513.169đ) |
| ZaloPay | 57,62% | 42,39% | **8,48%** | 8,62% | −1,38pp (−7.081.088đ) |

Plan bám luật production (11,03% và 8,48%) chứ không ép cả hai về đúng 10%. Nếu anh muốn ép đúng
10% cho cả hai, đó là một quyết định chính sách khác — cần anh chỉ đạo riêng, em không tự đổi.

---

## 2. Cơ cấu sổ trước và sau khi khớp lệnh

Số liệu dưới đây giả định **toàn bộ lệnh khớp ở đúng ref_price**. Giá thị trường biến động sẽ làm
số thực khác đôi chút.

### SpaceX — %active_nav

| Sổ | Trước (đ) | Trước (%) | Sau (đ) | Sau (%) | Thay đổi |
| --- | ---: | ---: | ---: | ---: | ---: |
| BAL | 0 | 0,00% | 0 | 0,00% | — |
| LAG | 35.100.000 | 3,62% | 35.100.000 | 3,62% | — |
| PARK | 317.548.000 | 32,76% | 424.963.000 | 43,85% | +11,09pp |
| CAPIT | 303.110.000 | 31,27% | 303.110.000 | 31,28% | — |
| DISCRETIONARY | 7.880.000 | 0,81% | 96.520.000 | 9,96% | +9,15pp |
| **TIỀN** | **305.627.008** | **31,53%** | **109.424.966** | **11,29%** | **−20,24pp** |

### ZaloPay — %active_nav

| Sổ | Trước (đ) | Trước (%) | Sau (đ) | Sau (%) | Thay đổi |
| --- | ---: | ---: | ---: | ---: | ---: |
| BAL | 0 | 0,00% | 0 | 0,00% | — |
| LAG | 63.845.000 | 12,43% | 63.845.000 | 12,43% | — |
| PARK | 116.256.650 | 22,63% | 173.436.650 | 33,76% | +11,13pp |
| CAPIT | 181.179.200 | 35,26% | 181.179.200 | 35,27% | — |
| DISCRETIONARY | 0 | 0,00% | 50.950.000 | 9,92% | +9,92pp |
| **TIỀN** | **152.499.982** | **29,68%** | **44.288.885** | **8,62%** | **−21,06pp** |

**Về cơ sở tiền — số cần đọc kỹ.** NAV dùng `totalCash − totalDebt`, không dùng `availableCash`.
Hai con số này khác nhau đáng kể hôm nay:

- **SpaceX**: cơ sở NAV 305,6tr, nhưng sức mua tức thì chỉ **158,4tr**. Chênh 147,2tr là tiền bán
  PARK phiên 08-10 đang settle T+2 cộng cổ tức phải thu.
- **ZaloPay**: cơ sở NAV 152,5tr, `availableCash` chỉ **1đ** — gần như toàn bộ tiền đang trong
  settle T+2. Sức mua thật đến từ `ppse.pp0Buy` (145,9tr), là hạn mức T+0 mà DNSE cấp trên tiền
  bán chưa về.

Đây không phải lỗi: cơ sở tính tỷ trọng được phép lớn hơn sức mua trong ngày. Việc chặn đặt quá tay
là của cổng tài trợ ở tầng thực thi, và cổng đó đã chạy thật (mục 5).

---

## 3. Danh sách lệnh

### 3.1 Hai lệnh discretionary — cùng logic trên cả hai tài khoản

| | SpaceX | ZaloPay |
| --- | --- | --- |
| TV1 (PECC1, UPCOM) | 2.000cp @ 19.900đ LO = 39.800.000đ | 1.300cp @ 19.900đ LO = 25.870.000đ |
| DRI (Cao su Đắk Lắk) | 3.700cp @ 13.200đ LO = 48.840.000đ | 1.900cp @ 13.200đ LO = 25.080.000đ |
| Cộng | 88.640.000đ | 50.950.000đ |

**TV1 — lý do.** Nâng size lên 5% NAV/mã theo chỉ đạo của anh (trước đó 1,5%), cộng vào chương
trình TV1 gốc anh đã duyệt 2026-07-23. Gate chạy **lại ở size mới**, không giả định pass: DCF
CHEAP, biên an toàn +84,76% (robust); due-diligence 0 cờ đỏ.

> **Rủi ro chính của lệnh này là thanh khoản, không phải định giá.** ADV 3 tháng của TV1 chỉ
> 806tr/phiên. Lệnh SpaceX = 5% ADV, ZaloPay = 3% ADV, cộng hai tài khoản là 8,1% ADV cùng lúc.
> Dưới trần %ADV per-account (80,59tr) nhưng thực tế nhiều khả năng chỉ khớp một phần và phải rải
> nhiều phiên. Trần giá cứng 20.000đ chỉ cách giá chào bán 19.900đ đúng 0,5%, càng làm giảm xác
> suất khớp trọn. Em **không nới trần này** — nó là điều kiện anh đã duyệt cho chương trình TV1.

**DRI — lý do.** Nâng size lên 5% NAV/mã theo cùng chỉ đạo. Đây là quyết định **discretionary**,
không phải mở lại cửa sổ entry LAG (cửa sổ đó đã đóng đủ 3/3 phiên sau 08-10). Gate chạy lại ở size
mới: DCF CHEAP, biên an toàn +36,80% (robust); DD 0 cờ đỏ; 8L rating 2; thanh khoản rộng rãi (ADV
5,35 tỷ ⇒ lệnh chỉ 1% ADV ở SpaceX, 0,5% ở ZaloPay). Trần giá cứng 13.600đ.

> **Ghi chú thoát vị thế.** DRI nằm ở book DISCRETIONARY_SPECIAL, nên nếu DT5G chuyển BEAR thì cơ
> chế `w_LAG = 0` **không** bán nó tự động như với sổ LAG. Đổi lại, nó cũng không có lối thoát tự
> động nào — exit là quyết định của người.

> **Theo dõi ngành cao su.** Ngưỡng xét lại luận điểm PEAD nhóm cao su là RSS3 thủng 2,26 USD/kg.
> Giá hiện tại 2,694 USD/kg (2026-08-07) — **chưa kích hoạt**, còn cách ngưỡng khoảng 19%.

### 3.2 Lệnh PARK — đưa sổ PARK về đúng rổ custom30V

Toàn bộ lệnh PARK sinh từ công cụ park-add: nó lấy rổ custom30V tại kỳ tái cân bằng 2026-08-05,
tính khoảng cách giữa giá trị đang giữ và giá trị mục tiêu từng mã, rồi co đều theo trần tiền, trần
%ADV per-name và trần tổng/phiên. Không có mã nào được chọn bằng phán đoán.

**SpaceX — 15 lệnh, 107.415.000đ** (hệ số co 0,837; PARK sau lệnh = 79,5% idle pool, sát mục tiêu
80,0%)

| Mã | KL | Giá (đ) | Giá trị (đ) | Đang giữ (tr) | Mục tiêu (tr) | Mã mới? |
| --- | ---: | ---: | ---: | ---: | ---: | :--: |
| ACB | 100 | 22.650 | 2.265.000 | 18,1 | 21,3 | |
| BID | 100 | 39.500 | 3.950.000 | 39,5 | 44,5 | |
| CTG | 200 | 32.800 | 6.560.000 | 32,8 | 40,5 | |
| EVF | 100 | 12.500 | 1.250.000 | 0,0 | 1,6 | mới |
| HDB | 100 | 26.950 | 2.695.000 | 18,9 | 21,7 | |
| HPG | 1.200 | 22.100 | 26.520.000 | 0,0 | 30,4 | mới |
| LPB | 200 | 52.300 | 10.460.000 | 10,5 | 25,9 | |
| MBB | 300 | 20.200 | 6.060.000 | 25,6 | 32,0 | |
| MSB | 500 | 16.250 | 8.125.000 | 0,0 | 8,2 | mới |
| SHB | 700 | 12.000 | 8.400.000 | 1,2 | 10,3 | |
| VCB | 200 | 60.300 | 12.060.000 | 30,1 | 44,5 | |
| VIB | 500 | 14.850 | 7.425.000 | 0,0 | 8,2 | mới |
| VIX | 100 | 13.950 | 1.395.000 | 4,2 | 5,6 | |
| VPB | 100 | 25.850 | 2.585.000 | 28,4 | 33,1 | |
| VRE | 300 | 25.550 | 7.665.000 | 0,0 | 9,8 | mới |

**ZaloPay — 11 lệnh, 57.180.000đ** (hệ số co 0,783)

| Mã | KL | Giá (đ) | Giá trị (đ) | Đang giữ (tr) | Mục tiêu (tr) | Mã mới? |
| --- | ---: | ---: | ---: | ---: | ---: | :--: |
| ACB | 300 | 22.650 | 6.795.000 | 0,0 | 8,8 | mới |
| BID | 100 | 39.500 | 3.950.000 | 11,8 | 18,4 | |
| HPG | 500 | 22.100 | 11.050.000 | 0,0 | 12,6 | mới |
| MBB | 400 | 20.200 | 8.080.000 | 4,7 | 13,2 | |
| MSB | 200 | 16.250 | 3.250.000 | 0,0 | 3,4 | mới |
| SHB | 300 | 12.000 | 3.600.000 | 0,0 | 4,3 | mới |
| TPB | 100 | 14.750 | 1.475.000 | 0,0 | 2,8 | mới |
| VCB | 200 | 60.300 | 12.060.000 | 6,0 | 18,4 | |
| VIB | 200 | 14.850 | 2.970.000 | 0,0 | 3,4 | mới |
| VIX | 100 | 13.950 | 1.395.000 | 0,0 | 2,3 | mới |
| VRE | 100 | 25.550 | 2.555.000 | 0,0 | 4,1 | mới |

Sau khi chạy hết lệnh, PARK ở SpaceX vẫn còn thiếu 2,6tr so với mục tiêu (một phần vì TCB muốn mua
2,53tr nhưng dưới 1 lô nên bị bỏ) và rổ chỉ khả thi 19/30 mã do các mã còn lại vướng trần thanh
khoản hoặc danh sách cấm. Đây là hành vi đúng thiết kế, không phải lỗi.

**Không có lệnh BÁN nào trong cả hai plan.**

---

## 4. Vì sao V2.4 (BAL / LAG / CAPIT) không có lệnh mới

Cả hai tài khoản đều có tiền để mua. Việc không mua là do gate chặn, không phải bỏ sót.

| Ứng viên | Sổ | Kết luận | Lý do |
| --- | --- | --- | --- |
| PHR | LAG_HI | SKIP | DCF **RICH** — giá trị hợp lý ~47.948đ so với giá 58.600đ, biên an toàn −22,2% (robust). Cần lý do override, không có. Chặn phụ trợ độc lập: giá live 59.800đ > mốc neo 58.600đ (+2,05%) ⇒ không được mua đuổi. |
| SSI | LAG_LO | KHÔNG ĐẶT | Qua được lăng kính ngành (CHEAP, P/B 1,50, ROE_TTM 13,5%) và đủ tiền, nhưng giá live 25.100đ cao hơn mốc neo 24.450đ đúng 2,66% ⇒ vi phạm điều kiện giá tại thời điểm lập plan. |
| BAL | — | 0 ứng viên | Không có tín hiệu. |

Cả hai tài khoản chạy trên **cùng một file tín hiệu** (signal_date 2026-08-10) và cho ra **cùng
danh sách** due_today = [PHR, SSI] — đã đối chiếu chéo, không có dấu hiệu sai tham số.

> **SSI hết hạn sau hôm nay.** 2026-08-11 là phiên cuối (ngày 3) của cửa sổ entry cho lô tín hiệu
> 08-07. Nếu SSI mở cửa ở mức ≤ 24.450đ thì về nguyên tắc đủ điều kiện mua, nhưng plan này không
> đặt sẵn lệnh chờ vì tại thời điểm lập plan giá đang vi phạm. **Nếu anh muốn đặt lệnh chờ đúng
> 24.450đ, cần anh chỉ đạo** — trần cứng sẽ tự chặn không cho mua đuổi. Em không tự thêm.

---

## 5. Kết quả các cổng kiểm soát

| Cổng | SpaceX | ZaloPay |
| --- | --- | --- |
| P0 tài trợ (`check_plan_funding`, ppse đo sống) | **OK** — cần 196.202.041đ / sức mua 565.026.657đ (34,7%) | **OK** — cần 108.211.098đ / sức mua 145.946.201đ (74,1%) |
| Chuỗi lọc thực thi | 0 lệnh bị loại, 0 KL bị đổi | 0 lệnh bị loại, 0 KL bị đổi |
| Trần giá cứng (`load_plan()` thật) | TV1 20.000đ, DRI 13.600đ — giữ nguyên | TV1 20.000đ, DRI 13.600đ — giữ nguyên |
| Due diligence | PASS toàn bộ 17 lệnh, 0 cờ đỏ | PASS toàn bộ 13 lệnh, 0 cờ đỏ |
| Trần %ADV | TV1 5% ADV (trần 80,59tr) · DRI 1% ADV · PARK dưới trần per-name | TV1 3% ADV · DRI 0,5% ADV · PARK dưới trần per-name |
| L1 park-trim | **NO_TRIM** — PARK 317,5tr dưới mục tiêu 498,5tr | **NO_TRIM** |
| L2 JIT-unpark | **NO_TRIGGER** — không có lệnh mua BAL/LAG | **NO_TRIGGER** |

Cổng tài trợ được chạy **thật** trên bản plan cuối cùng, không phải ước lượng: nạp qua `load_plan()`
thật rồi chạy đủ chuỗi lọc của bot. Trần giá cứng cũng kiểm bằng `load_plan()` chứ không đọc file
JSON — vì trường nào không có trong dataclass sẽ bị lọc mất im lặng.

Hai đề xuất L1 và L2 đều no-op hôm nay, và điều đó nhất quán: plan này **mua vào** PARK chứ không
bán PARK, nên không có khả năng hai đường đề xuất trùng cổ phiếu.

---

## 6. Hai việc cần anh quyết

### 6.1 Quyền mua MBB 10:1 — hạn chuyển nhượng 26/08/2026

MBB chốt quyền ngày 2026-08-11 với **hai** sự kiện cùng lúc:

1. **Cổ tức bằng cổ phiếu 15%** — tự động, đã vào sổ (SpaceX 1.100 → 1.265cp; ZaloPay 202 → 232cp).
2. **Chào bán quyền mua cho cổ đông hiện hữu, tỷ lệ 10:1, giá 10.000đ/cp** — **không** tự động.
   Muốn có cổ phiếu thì phải nộp tiền thực hiện quyền.

| | Số quyền | Tiền phải nộp nếu thực hiện |
| --- | ---: | ---: |
| SpaceX | ~110 quyền | ~1.100.000đ |
| ZaloPay | ~20 quyền | ~200.000đ |

Số quyền tính trên lượng nắm giữ **trước** chia (1.100 và 202), vì quyền mua và cổ tức cổ phiếu
cùng chốt một mốc, không cộng dồn lên nhau.

**Cần anh quyết: thực hiện hay bỏ quyền.** Thời gian chuyển nhượng quyền là **18–26/08/2026** — sau
26/08 quyền hết hiệu lực và phần vốn đó mất đi không lấy lại được. Khoản tiền này **chưa** nằm trong
plan hôm nay; nếu anh quyết thực hiện thì đó là một khoản chi riêng, em sẽ lập lệnh riêng.

> Một chi tiết kỹ thuật liên quan: cổ phiếu thưởng 15% **chưa bán được** — DNSE vẫn giữ
> `tradeQuantity` ở số cũ trong khi `openQuantity` đã tăng. Mọi lệnh bán trong các phiên tới phải
> neo theo lượng bán được, không theo số dư sổ. Plan hôm nay không có lệnh bán nên chưa chạm.

### 6.2 Sự kiện corp-action MBB đang ghi `decided_by = "agent"`

Sự kiện `MBB-2026-08-11-STOCK-DIVIDEND` (hệ số ×1,15) đang ghi trong `data/corp_actions.json` với
`decided_by: "agent"` — nghĩa là **do agent kết luận, chưa có xác nhận trực tiếp của anh**. Em nêu
ra vì nó đã tác động thật lên sổ vị thế của cả hai tài khoản, không chỉ nằm trên giấy.

Bằng chứng đứng sau kết luận đó gồm ba nguồn độc lập với nhau và độc lập với sổ của mình:

1. **Công bố sàn/lưu ký**: VSD + Vietstock + VnEconomy — GDKHQ 11/08, ĐKCC 12/08, phát hành ~1,21
   tỷ cp trả cổ tức 15%, đồng thời chào bán ~805,5 triệu cp giá 10.000đ. Kiểm chéo bằng số tuyệt
   đối: 805,5tr / 8,07 tỷ ≈ 10,0% ⇒ đúng tỷ lệ quyền mua 10:1.
2. **Giá tham chiếu chính thức của sàn** (trường giá, hoàn toàn độc lập với trường số lượng đang
   lệch): sáng 11/08 DNSE trả giá tham chiếu 20.200đ, trong khi đóng cửa 10/08 là 24.250đ. Công
   thức điều chỉnh chuẩn HOSE cho ca gộp cổ tức CP + quyền mua: (24.250 + 10.000×0,10) / 1,25 =
   **20.200đ** — khớp tới đồng, và trần/sàn ±7% cũng khớp. Đây là hệ một phương trình một nghiệm:
   chỉ đúng cặp (15%, 10:1 @10.000đ) mới cho ra 20.200 từ 24.250.
3. **Số dư broker**: SpaceX 1.100 → 1.265 (đúng ×1,15); ZaloPay 202 → 232 (= làm tròn xuống của
   232,3, khớp cách broker làm tròn ở mức vị thế), và tổng giá vốn cũ khớp tuyệt đối sau khi hạ giá
   vốn theo 232.

Sự kiện này cũng giải thích được một dữ kiện mà giả thuyết khác không giải thích nổi: **cả hai tài
khoản cùng lệch đúng ~+15%** dù lịch sử giao dịch hoàn toàn độc lập nhau.

Em vẫn muốn anh xác nhận, vì theo quy ước nội bộ chỉ khi có xác nhận thật của người thì mới được
đánh dấu `decided_by = "user"` — và đây là một sự kiện đã đổi số lượng cổ phiếu thật.

---

## 7. Rủi ro và bối cảnh cần biết khi duyệt

- **Thanh khoản TV1 là rủi ro thực thi lớn nhất của plan này.** Nhiều khả năng lệnh chỉ khớp một
  phần trong phiên 08-11 và phải rải nhiều phiên. Đây là hệ quả trực tiếp của việc nâng size lên
  5% NAV trên một mã UPCOM có ADV 806tr — đã biết trước, không phải bất ngờ.
- **CAPIT episode CAPIT-2026-07-20 vẫn mở** (15 phiên). Năm mã NCT/PVT/SAB/SIP/VNM chiếm 31,11% NAV
  SpaceX, được miễn stop-loss và miễn giới hạn slot, và **plan này không đụng tới**. Thoát vị thế là
  quyết định của người.
- **Nếu DT5G chuyển BEAR**, allocator đặt `w_LAG = 0` và toàn bộ sổ LAG bị bán theo cơ chế sẵn có
  (SpaceX hiện chỉ có SCL 34,95tr; ZaloPay 63,85tr). Hai vị thế TV1/DRI ở book
  DISCRETIONARY_SPECIAL **không** nằm trong cơ chế đó.
- **Sau plan này PARK chiếm 43,85% NAV ở SpaceX và 33,76% ở ZaloPay.** PARK là rổ cổ phiếu
  (custom30V), không phải tiền gửi — nó chịu rủi ro thị trường đầy đủ. Việc hạ tiền từ ~30% xuống
  ~10% là hạ đúng phần đệm phòng thủ, theo đúng chỉ đạo của anh, nhưng cần nói thẳng ra chứ không
  để ngầm hiểu.
- **DGC (ZaloPay, 436tr)** nằm ngoài mọi tính toán sizing như thường lệ.
- Một lỗi trình bày trong file plan SpaceX: trường `approval_required.why` còn ghi *"plan này 0
  lệnh"* — đó là văn bản cũ sót lại từ bản HOLD ALL trước khi thêm lệnh, không phản ánh nội dung
  thật (17 lệnh). Số liệu và danh sách lệnh trong plan đều đúng; em không tự sửa file đang chờ duyệt,
  đã báo lên bus.

---

## 8. Cập nhật sau khi duyệt (2026-08-11)

1. **Duyệt** — ✅ đã duyệt cả 2 plan (xem banner đầu file). Bot sẽ tự nhận ở lần retry/khởi động
   kế tiếp; không cần thao tác thêm.
2. **Quyền mua MBB** — vẫn CHỜ Ý KIẾN, hạn 26/08 (SpaceX ~1,10tr, ZaloPay ~0,20tr).
3. **Xác nhận corp-action MBB 15%** — vẫn CHỜ Ý KIẾN để chuyển `decided_by` từ `agent` sang `user`.
4. **SSI** — không đặt lệnh chờ (giữ mặc định).
5. **Lỗi phát hiện lúc duyệt (đã vá, commit `6404fead`)**: `approve_plan_simple.sh` chưa nhận
   field `estimated_cost_vnd`/`fee_est_vnd` (quy ước của công cụ park-add mới `compute_park_add.py`)
   và tên field NAV cũ `available_cash_before_vnd` đã đổi thành `total_cash_minus_debt_vnd` —
   trước khi vá, script tính Σ mua và tiền mặt đều ra 0, khiến gate "đủ tiền" tự PASS bất kể thiếu
   bao nhiêu. Đã sửa + verify lại bằng số liệu thật (SpaceX dư +109,4tr, ZaloPay dư +44,3tr) trước
   khi ghi `approved_by` thật — không có lệnh nào được duyệt qua lỗ hổng này.

---

*Báo cáo lập bởi Dollar Bill (Portfolio Manager) — 2026-08-11. Mọi giá tham chiếu và số dư tiền đọc
trực tiếp từ DNSE API tại thời điểm lập plan, không dùng dữ liệu kho lưu trữ qua đêm. Cơ cấu sổ "sau"
là kết quả mô phỏng với giả định khớp toàn bộ ở ref_price; kết quả thực tế phụ thuộc mức khớp lệnh
và biến động giá trong phiên. Tài liệu này phục vụ mục đích ra quyết định nội bộ, không phải khuyến
nghị đầu tư.*
