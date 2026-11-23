# SCL — DD rev6 (23/11/2026, job `Taylor_20261123_063646`) · cơ sở SAU QUYỀN · thay `SCL_r4.md` (sổ rev5)

Lõi kinh doanh r3 (doanh thu, biên chuẩn hoá, trọng số chế độ ngành 0,5/0,3/0,2, lưới g/ROE, thuế) **tái dùng nguyên, không re-tune**. Rev6 sửa phần **cấu trúc vốn / chủ sở hữu** mà skeptic r1 (22/11, INCONCLUSIVE) nêu, mỗi khoản đều có nguồn BCTC gốc.
- **Calc:** `rev6/calc/calc_rev6.py` (md5 `17e07b30…`) → `rev6/calc/calc_rev6_out.json` (`b63d6310…`). Chạy 2 lần trùng byte, threads=1.
- **Khoá:** `rev6/assumptions_SCL_rev6.json` (md5 **`f59e25ea086fb4a7262c6095fdd030e7`**). `dd_assumptions_lint` cho 0 vi phạm.
- **Thời điểm khoá:** `rev6/LOCK_rev6_md5.txt`, khoá lần đầu 13:45:18 ICT; giá SCL chỉ được đọc sau mốc này. Khoá lại sau skeptic r2 chỉ vì thêm biến thể; base, tham số và tâm không đổi.
- **Nguồn gốc:** BCTC gốc khôi phục từ git `0090c758e^` (lệnh TRIM 19/11 đã xoá `dd_SCL_20261029/src`) vào `rev6/src/`. Danh sách và md5 nằm trong file khoá.

## 0. Kết luận — **TRÊN vùng** (mạnh hơn r4); tâm **16.883** (−20,9% so với r4)

Bảng dưới tính trên cơ sở sau quyền, **45.516.815 cp**.

| Cỡ CK | Tâm | P10 | P50 | P90 | Giá ref | Giá / P90 | Giá / tâm | Nhãn |
|---|---|---|---|---|---|---|---|---|
| **CK 5 tỷ (cỡ ghi sổ, 4,454%)** | **16.883** | **13.652** | 16.510 | **20.415** | **25.100** (đóng cửa 20/11, DNSE ohlc) | **+22,9%** | +48,7% | **TRÊN vùng (>P90)** |
| Sleeve 40 tr (0,843%) | 17.521 | 14.168 | 17.134 | 21.187 | 25.100 | +18,5% | +43,3% | TRÊN |
| Giá DNSE 23/11 13:45 | | | | | 24.600 (KL 2.680 cp, tham chiếu 24.900) | +20,5% | | TRÊN |

- **Trước chiết khấu thanh khoản:** tâm 17.670.
- **Kết cục cao nhất** của lưới 108 điểm là 22.340 (5 tỷ), vẫn thấp hơn giá. Như vậy **100% trọng số nằm dưới giá** (khung headline).
- **Biến thể:** mọi biến thể ở §3 cho nhãn TRÊN, **trừ cận trên khung nợ** (P/E có đòn bẩy): P90 26.387 > giá ⇒ TRONG (§3). Ngoài cận trên, P90 cao nhất là 22.706 (bỏ hẳn KTPL).
- **Luật 0,85×tâm:** 14.351. Không đạt.
- **Hành động:** không có hành động mua; V8 (2–4% NAV/mã) không áp dụng khi giá còn TRÊN vùng.
- **Tham chiếu cơ sở cum (trước quyền, 38,84 tr cp):** tâm 17.942 (5 tỷ) / 18.620 (40 tr).

## 1. Đính chính so với rev trước (r4) — từng hạng mục skeptic r1

| # | Hạng mục skeptic r1 | Xử lý rev6 | Loại | Ảnh hưởng (5 tỷ, sau quyền) |
|---|---|---|---|---|
| 1 | `model_scl_r3_out.json` mất khỏi repo, không tái lập được | Khôi phục từ `/tmp/fpt_r3` vào `rev6/inputs/`. md5 **73a84983…** = md5 r3 công bố. Lõi `scl_r3_core_5Ffix.py` (d3a7d936) và `ddr2.py` (95d8fe38) khớp `LOCK_r3_md5.txt`. **Chân đối chứng B0 tái lập 21.339,47 của r4** | (a) | 0 |
| 2 | Cộng lại lãi dự án (~7%) không có cơ sở; giả định "nợ dự án = giá vốn" trái dữ liệu | **Đọc thuyết minh:** chính sách IV.13 (VAS 16) cho phép vốn hoá. Tuy vậy, XDCB V.9 không ghi khoản lãi vốn hoá nào. Lãi trên KQKD 9T là 15,547 tỷ, bằng đúng dòng LCTT mã 06; lãi đã trả 14,292 tỷ ≤ lãi đã ghi chi phí ⇒ không thấy lãi vốn hoá. **Bỏ khung r3, chuyển headline sang khung NỢ MỆNH GIÁ:** E không đòn bẩy (cộng lại lãi sau thuế của TOÀN BỘ nợ 416,46 tỷ, lãi P&L thực 4,96%) × bội số − toàn bộ vay + tiền 95,10 + XDCB theo giá vốn 205,5 (V4a). Khung này không cần giả định "nợ dự án = giá vốn". Chân đối chứng khớp biến thể `par_debt` r3 (21.673 / 22.492 cum) | (a) | **−968** |
| 3 | Tiền thu quyền cộng theo mệnh giá trong khi nợ định dưới mệnh giá | **NQ 1191/NQ-HĐQT Điều 2** (PDF gốc, tr.4): toàn bộ 75 tỷ dùng trả HĐTD BIDV 02/2026/1605829, giải ngân tháng 1–2/2027. Trong khung nợ mệnh giá, tiền vào và nợ giảm cùng mệnh giá nên nhất quán | (a) | nằm trong #2 |
| 4 | Quỹ khen thưởng phúc lợi chưa xét | **BCTC soát xét 6T/2026 V.19.1:** NQ 486/NQ-ĐHĐCĐ 24/04/2026 trích phúc lợi 3,214 + khen thưởng 3,214 = **10,0% LNST 2025**. Áp vào base theo ba phần: (i) 10% E hằng năm; (ii) trừ số dư quỹ 30/9 là 6,330 tỷ (mã 323); (iii) trừ phần trích tạm 10% × LNST 9T 94,36 tỷ chưa phân phối. **Độ nhạy:** TB 3 lần phân phối 2024–26 là 16,1% (BCTC KT2025 tr.27: 21,3% / 17,0% / 10,0%) | (a) | **−2.163** |
| 5 | ESOP "đợt 2" 2,1% chưa xác định được | **ĐÃ ĐÓNG bằng BCTC soát xét 6T/2026 V.19.1:** "Phát hành ESOP từ LNST 6.800.000.000", tức **680.000 cp** miễn phí. Tỷ lệ 680.000 / 32.407.875 cp đầu 2026 = **2,10%**, khớp dòng BQ ISS ratio 0,021. Đây là đợt RIÊNG, khác 920.000 cp ESOP trả tiền @10.000 (LCTT mã 31: thu 9,68 tỷ). NQ 1191 tr.2 (21/09) ghi đang lưu hành 38.836.815 cp ⇒ đợt này **chưa phát hành**. Cộng 680.000 cp vào mẫu số, không thu tiền. **Phần còn lại không kiểm chứng được:** thời điểm phát hành | (a) | **−272** |
| 6 | Hợp đồng nguồn tro/thạch cao Phả Lại (thời hạn, giá); skeptic r2: ảnh hưởng tới BIÊN LÕI, không chỉ XDCB | **KHÔNG KIỂM CHỨNG ĐƯỢC.** Không có trong BCTC Q3/6T/KT2025; WebSearch 23/11 không ra. Tham chiếu duy nhất tìm thấy: HĐ xử lý tro xỉ Vĩnh Tân 4 thời hạn 3 năm ([viettimes](https://viettimes.vn/doanh-nghiep-nao-trung-thau-xu-ly-tro-xi-tai-nha-may-nhiet-dien-vinh-tan-4-post208126.html)); ADDENDUM_5F cũng ghi HĐ đấu giá tro ~3 năm. Đất Phả Lại thuê tới 2059 (6T/2026 V.20.1). **Kịch bản** (không vào base, ước lượng; không gán xác suất vì không có dữ liệu thời hạn/giá HĐ): tái đấu giá làm mất lợi thế giá tro ⇒ biên ròng lõi −2 điểm (½ khoảng NPM TTM 12,7% − TB 2020–TTM 8,3%) ⇒ **14.018**; −4 điểm (toàn bộ khoảng) ⇒ **11.152**. Stress gộp (TROUGH 0,2 + biên −4 điểm + Phả Lại mất 100%) ⇒ **6.081** | (c) | −2.865 / −5.731 (stress −10.802) |
| 7 | Phả Lại còn ~72 tỷ capex chưa mô hình hoá | Dự án TĂNG TRƯỞNG, không phải capex tuân thủ ⇒ **V4a: NPV = 0** ở giá vốn; phần còn chi đối ứng giá trị tương đương. Nguồn vốn: HĐTD BIDV 01/2026 hạn mức 184 tỷ, 68 tháng (6T/2026 V.18 (2.3)). Không có tín hiệu cụ thể về trễ tiến độ hay vượt dự toán ⇒ suy giảm chỉ để ở kịch bản: mất 50% phần đã chi ⇒ 14.882 (−2.001); mất 100% ⇒ 12.880 (−4.003) | (b) | 0 trong base |
| 8 | CFO 9T 9,9 tỷ so với LNST 94,4 tỷ, chưa đọc LCTT | **Đã đọc** BCTC Q3 tr.5–6: CFO 9,862 tỷ. Vốn lưu động hút: phải thu +68,20, tồn kho +33,42, phải trả −15,02, chi phí trả trước +8,94. Capex 198,13; vay ròng +86,10 ⇒ FCFE 9T **−102,2 tỷ**. Để ở WARNING + mốc (§6), không trừ thêm vào base vì bội số dùng LN chuẩn hoá. Đánh dấu V6: chỉ dùng V_ngắn | (b) | 0 |
| 6b | (skeptic r2) Độ nhạy lỗ phải thu Vincons bị rơi khỏi rev6 | Khôi phục. Vincons 67,892 tỷ, dự phòng 0; kiểm toán 2025 và soát xét 6T không ngoại trừ ⇒ base = sổ sách. Lỗ 20/50/100% ⇒ 16.655 / 16.313 / 15.744. Trục [UL] r3 0/20/50% (0,75/0,2/0,05) ⇒ 16.809 | (b) | −228 / −570 / −1.140 |
| 6c | (skeptic r2) Thu nhập khác 9T 4,763 tỷ (thu hồi nợ đã xoá) nằm trong TTM | Bỏ khỏi E sau thuế ⇒ 16.311. Giữ trong base vì biên lõi đã chuẩn hoá về TB chu kỳ ở 80% trọng số (CYCLICAL + ADMIN_GATED); số tách riêng để đọc | (b) | −572 |
| 9 | Chi phí phát hành chưa trừ | Không có số công bố. Mỗi 0,1 tỷ chi phí ứng với **−2,1 đ/cp**; nếu chi phí ≤ 0,5% tiền thu thì < −10 đ/cp | (c) | < −10 |
| 10 | CK 4,45% ở cỡ 5 tỷ là ngoại suy (+3,8% nếu dùng 40 tr) | Giữ nguyên quy ước sổ: 5 tỷ để ghi sổ, 40 tr báo song song (+638 đ). Cả hai cỡ đều TRÊN | — | 0 |
| 11 | BQ `OShares` ghi trước 44,84 tr từ ngày cum 06/11; `Close` không điều chỉnh lùi | Rev6 **không dùng** `OShares` BQ; số cp lấy từ NQ 1191 + BCTC. Đã ghi vào bus để data-ops (Winston) theo dõi | — | 0 |
| — | **Không thuộc danh sách skeptic: D4 terminal NONE ⇒ RONIC = Ke** | 5F (ADDENDUM_5F 08/11, < 12 tháng ⇒ tái dùng): moat **NONE**. Rev6 dùng 5 năm tái đầu tư theo lưới ROE hiện hành, sau đó terminal E/r (không ép ROE ở giai đoạn dự báo — luật 08/11). Bội số một tầng của r3 để ở biến thể | luật | **−1.053** |

Loại xử lý: (a) đưa vào base, có nguồn độc lập; (b) để ở kịch bản/độ nhạy; (c) không kiểm chứng được.

**Bridge r4 → rev6** (cơ sở sau quyền, CK 5 tỷ; mỗi bước đổi một thứ):

| Bước | Tâm | Δ | P10 | P90 |
|---|---|---|---|---|
| B0 r4 (khung r3, k=0, 44,84 tr cp) — đối chứng | 21.339 | — | 17.445 | 25.681 |
| B1 khung nợ mệnh giá | 20.371 | −968 | 16.510 | 24.732 |
| B2 KTPL 10% + số dư + trích tạm 9T | 18.208 | −2.163 | 14.739 | 22.137 |
| B3 ESOP-2 680.000 cp | 17.936 | −272 | 14.519 | 21.806 |
| **B4 terminal RONIC = Ke (headline)** | **16.883** | −1.053 | 13.652 | 20.415 |

Tâm dịch −20,9% so với tâm skeptic đã đọc ⇒ theo B2 bắt buộc phản biện lại đầy đủ (đã chạy, xem `skeptic/`).

## 2. Sự kiện + số cổ phiếu
- **Quyền mua** (NQ 1191 + NQ 1363): 6.000.000 cp @12.500, tỷ lệ 100:15,4453, GDKHQ 09/11, nộp tiền 17/11–08/12.
  - Cổ phiếu dư được HĐQT phân phối lại cho đối tượng khác với giá không thấp hơn giá chào bán; phần không phân phối hết bị huỷ (NQ 1191 tr.3–4).
  - Base giả định bán đủ. Độ nhạy: bao phủ 50% ⇒ tâm 17.232; 0% ⇒ 17.633.
- **Số cp:** 38.836.815 + 6.000.000 + 680.000 = **45.516.815**.

## 3. Biến thể (không vào base) — tâm / P10 / P90, CK 5 tỷ

| Biến thể | Tâm | P10 | P90 | Nhãn @25.100 |
|---|---|---|---|---|
| **Headline** | **16.883** | 13.652 | 20.415 | TRÊN |
| Khung r3 có cộng lại lãi dự án (+KTPL, ESOP-2, RONIC=Ke) | 17.918 | 14.657 | 21.444 | TRÊN |
| Khung không cộng lại, dự án ròng 0 | 16.558 | 13.296 | 20.077 | TRÊN |
| Bội số một tầng (không RONIC=Ke) | 17.936 | 14.519 | 21.806 | TRÊN |
| KTPL 0% | 18.782 | 15.185 | 22.706 | TRÊN |
| KTPL TB 3 năm 16,1% | 15.723 | 12.715 | 19.016 | TRÊN |
| ESOP-2 đã nằm trong số cp | 17.139 | 13.859 | 20.725 | TRÊN |
| Đối xứng (+TROUGH 0,2) | 15.815 | 12.865 | 19.430 | TRÊN |
| Bao phủ quyền 50% / 0% | 17.232 / 17.633 | | 21.013 / 21.702 | TRÊN |
| Phả Lại suy giảm 50% / 100% (kịch bản mất nguồn tro) | 14.882 / 12.880 | | 18.414 / 16.412 | TRÊN |
| Dòng cộng lại lãi định như niên kim vĩnh viễn ở Ke, không tái đầu tư (skeptic r2) | 16.695 | 13.434 | 20.215 | TRÊN |
| Lỗ phải thu Vincons 50% / 100% | 16.313 / 15.744 | | 19.846 / 19.276 | TRÊN |
| Bỏ thu nhập khác 9T | 16.311 | 13.067 | 19.841 | TRÊN |
| Tái đấu giá tro: biên −2 / −4 điểm | 14.018 / 11.152 | | 17.540 / 14.664 | TRÊN |
| **Cận trên khung nợ: nợ chỉ hiện qua lãi P&L 4,96% vĩnh viễn (P/E có đòn bẩy) + tiền + XDCB theo giá vốn** | **22.868** | 19.606 | **26.387** | **TRONG** (25.100 < P90) |
| Chân đối chứng skeptic r1 (không cộng lại, cum, 40 tr, một tầng, k=0) | **21.901** | 17.195 | 27.150 | — (khớp số skeptic tới đồng) |

- **Năm khung định giá nợ:**
  - không cộng lại: 16.558;
  - niên kim không tái đầu tư: 16.695;
  - **nợ mệnh giá (headline): 16.883**;
  - r3 (nợ dự án = giá vốn): 17.918;
  - **cận trên P/E có đòn bẩy: 22.868** (P90 26.387 > giá ⇒ nhãn TRONG). **Nhãn KHÔNG bền ở cận trên.**
- **Vì sao cận trên không vào base:**
  - Khung này coi 4,96% là chi phí nợ vĩnh viễn (lãi Q3 ×4 / nợ cuối kỳ) mà không nâng Ke theo đòn bẩy, tức định 416 tỷ nợ ở ~1/3 mệnh giá. Lãi thực tế cao hơn: 9T 15,55 / nợ bình quân ≈ 5,6%; khoản vay dự án Vĩnh Tân 9,5%; vay bên liên quan 10%.
  - Nợ sẽ được trả bằng tiền thật: 75 tỷ tiền quyền mua trả BIDV tháng 1–2/2027 (NQ 1191).
- **Thiên lệch của headline:** khung nợ mệnh giá chiết khấu E không đòn bẩy ở Ke chứ không ở WACC, nên nghiêng thận trọng; cận trên nghiêng lạc quan. Base nằm gần đầu dưới của dải 16.558–22.868. Tôi chọn khung này vì là khung duy nhất nhất quán với V4a và với việc tiền thu quyền dùng trả nợ.

## 4. V1 chi phí vốn + D4
- **r = 13,5%** = 13,5% + 1,0 × (7,40% − 7,40%).
  - Lãi huy động 12T hiệu dụng là 7,40% (cctg_12m 02/11; Big-4 6,80%; `deposit_rate_vn` last_update 16/11), không đổi so với neo 03/11.
  - β = 1 là giả định.
- **Độ nhạy theo lãi huy động** (tâm, 5 tỷ):

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β = 1 | 18.514 (+9,7%) | 17.666 (+4,6%) | 16.158 (−4,3%) | 15.485 (−8,3%) |
| β = 0,5 | 17.666 | | | 16.158 |

- **Hai đầu dải Ke nội địa (D4):** 12,3% ⇒ 18.873; 13,4% ⇒ 17.035.
  - Cả hai đầu đều < P90 headline < giá.

## 5. V3 thanh khoản · V5 · V6 · V8
- **V3 — CK thanh khoản:** tái dùng r3 (ADV120 2,35 tỷ tới 06/11, `ddr2.liquidity`).
  - 5 tỷ: 4,454% (= 213% ADV, ngoại suy ngoài vùng √).
  - 40 tr: 0,843%.
  - KL 20 phiên gần nhất (DNSE ohlc) từ 21.100 đến 238.000 cp/ngày.
  - Nhãn tính trên giá trị SAU CK. Quy mô áp dụng: 5 tỷ (sổ) và 40 tr (sleeve).
- **V5 — 5F:** ADDENDUM_5F (08/11, < 12 tháng) ⇒ moat **NONE**, ứng viên COST/LOCATION (bán kính tro 150–300 km).
  - Kiểm nhanh 23/11: không có dữ kiện mới; HĐ nguồn tro vẫn không kiểm chứng được (#6).
  - Rủi ro số 1: tái đấu giá nguồn tro.
- **V6 — hai nền (chỉ hiển thị):** FCFE 9T = −102,2 tỷ ≤ 0 ⇒ chỉ dùng **V_ngắn** (= tâm mô hình).
  - FCFE âm vì capex tăng trưởng Phả Lại (198 tỷ/9T) cộng vốn lưu động tăng. Không đọc đây là cờ đắt.
- **V8:** chuẩn 2–4% NAV/mã. Không đề xuất mua: giá TRÊN vùng.

## 6. WARNING (không vào base) + mốc hai chiều
- Pha loãng: 17,3 tr cp (2023) → 45,5 tr sau quyền và ESOP-2. Năm 2026 có hai đợt ESOP (920k trả tiền + 680k miễn phí). ESOP lặp lại là rủi ro, chưa có kế hoạch 2027.
- Vay bên liên quan: CTCP CN-DV Cao Cường 28 tỷ @10% (30/06).
- Phải thu tập trung Vincons, chưa trích dự phòng.
- CFO yếu so với LN; nợ vay 416 tỷ.
- Chưa thấy tin xử phạt/khởi tố (WebSearch 05/11, 08/11, 23/11).

| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Quyền mua (hạn nộp 08/12) | Bán đủ; trả nợ BIDV tháng 1–2/2027 | Không bán hết |
| BCTC Q4/2026 | CFO ≥ LNST, phải thu giảm | Biên gộp TTM < 36%, FCFE âm tiếp |
| HĐ nguồn tro / Phả Lại vận hành | Công bố HĐ dài hạn + giá ⇒ đưa IRR vào lưới | Trễ, vượt 262,9 tỷ, mất nguồn tro |
| ĐHĐCĐ 2027 | KTPL ≤ 10%, không ESOP | KTPL > 15% hoặc ESOP mới |

- **Ngưỡng nhãn:** về TRONG vùng khi giá ≤ **20.415** (5 tỷ) hoặc ≤ 21.187 (40 tr).
- **Luật 0,85×tâm:** ≤ 14.351.
- **HARD ABANDON** giữ như r3: kiểm toán ngoại trừ về phải thu; lỗ Vincons > 50%; quyền bị huỷ hoặc đổi điều khoản.
- **Kiểm toán:** FY2025 AVA (245/BCKT-TC/AVA.NV5), chấp nhận toàn phần. Soát xét 6T/2026 AVA (590/BCKT-TC/AVA), kết luận không ngoại trừ ⇒ `audited_fy_missing = false`.

## 7. Còn mở
- HĐ nguồn tro/thạch cao Phả Lại (thời hạn, giá) — không kiểm chứng được; kịch bản biên lõi −2/−4 điểm ở §1 #6.
- Khung định giá nợ: nhãn TRÊN ở 4/5 khung, TRONG ở cận trên (§3).
- Thời điểm phát hành 680.000 cp ESOP-2.
- Chi phí phát hành quyền.
- NQ 486 bản gốc: chưa tải; số lấy qua BCTC soát xét.

## 8. Đính chính sau skeptic r2 (INCONCLUSIVE, `skeptic/r2.json`)
- Chỉ THÊM biến thể và độ nhạy theo `recommended_followups` của r2. Base, tham số và tâm 16.883 KHÔNG đổi (tâm dịch 0%, không đổi lớp nhãn).
- Đã thêm: kịch bản biên lõi khi tái đấu giá tro (#6), độ nhạy Vincons (#6b), bỏ thu nhập khác (#6c), dòng cộng lại lãi dạng niên kim và cận trên khung nợ (§3; cận trên đổi nhãn — nêu thẳng).
- Chưa làm: lãi Q4 / nợ bình quân (BCTC Q4 chưa có); capex còn lại của dây chuyền Vĩnh Tân (không công bố).

Không ghi `kb/dd_price_zones.json`, không email, không lệnh.
