# DCF RICH sâu có báo trước triển vọng lợi nhuận / drift không? — job Taylor_20261024_034455

R&D đọc-only, không wire gì, không sửa file production. Ngày 2026-10-24.

## Kết luận

1. **Lợi nhuận: SAI, RICH sâu KHÔNG báo trước lợi nhuận xấu đi, mà ngược lại.** So với nhóm FAIR+CHEAP,
   nhóm RICH sâu (MoS < −100%) có NP yoy quý Q+1 **cao hơn +12,1pp** (CI95 +6,9…+17,6) và Q+2 **cao hơn +9,8pp**
   (+5,5…+13,8). Xác suất NP Q+1 giảm yoy **thấp hơn −6,6pp** (−9,8…−3,3), xác suất giảm tốc thấp hơn −5,0pp.
   Kết quả đứng vững khi đã kiểm soát mức tăng trưởng hiện tại (+10,4pp), và đúng cả IS 2014-19 (+7,2pp) lẫn
   OOS 2020+ (+15,2pp). Nói cách khác, giá cao đang trả cho một phần tăng trưởng có thật.
2. **Drift sau cú bất ngờ lợi nhuận dương (đối tượng của LAG): ĐÚNG, nhưng chỉ ở nhóm ROE thấp.**
   - Toàn mẫu: BHAR60 của RICH sâu **thấp hơn −3,4…−3,8pp** so với đối chứng ghép ô. CI loại 0 ở cả 3 cách ghép,
     và đúng ở OOS (−3,9pp, CI −6,4…−1,6). BHAR20 chỉ −0,8…−1,2pp, CI chứa 0.
   - **ROE5Y < 25%: −4,5…−4,8pp** (CI −7,3…−2,1), đúng ở cả IS (−3,7pp) lẫn OOS (−4,9pp). Đây là phần
     mang thông tin thật.
   - **ROE5Y ≥ 25% (compounder kiểu MCH): +4,0…+4,6pp, CI chứa 0** (n=84 sự kiện / 44 quý) ⇒ **không kết luận
     được**. Ước lượng điểm nghiêng theo chiều *có lợi*, không phải bất lợi.
   - Hàng hoá chu kỳ (ICB 0xxx/1xxx, ví dụ MSR): −5,5pp (ghép lỏng: CI −10,4…−0,5; OOS −6,2pp). Kết quả cùng chiều
     với nhóm ROE thấp, nhưng là phân tích thăm dò.
   - Tiêu dùng: ≈0 (−0,5pp, CI −3,3…+2,2), không kết luận được.
   - RICH nhẹ (−100%…−20%): không khác đối chứng ở cả lợi nhuận lẫn drift (CI chứa 0).
3. **MCH: RICH chủ yếu do GIẢ ĐỊNH của mô hình, không phải do đà lợi nhuận đang gãy. Tuy vậy, đà lợi nhuận cũng
   chỉ ở mức trung bình chứ chưa mạnh** (xem §3).
4. **Đề xuất (CHƯA sửa code, cần user duyệt + quant-skeptic):** chỉ bắt buộc `dcf_override_reason` khi
   **RICH sâu (MoS < −100%) VÀ (ROE5Y < 25% HOẶC thuộc nhóm hàng hoá chu kỳ)**. Các ca RICH còn lại hạ xuống
   **WARNING** hiển thị, không đòi lý do. Quy tắc hiện hành coi `status=RICH` là MoS ≤ 0, tức gồm cả vùng
   "FAIR" −20…0% và RICH nhẹ, là hai vùng không cho thấy thông tin nào trong nghiên cứu này.

## 1. Thiết kế (đã đo)

- **Đánh giá DCF point-in-time**: dựng được. `dcf_valuation.fair_value(asof)` chỉ đọc các dòng
  `ticker_financial` có `time<=asof`, và `time` ≈ ngày công bố (chỉ 56/55.293 dòng có `Release_Date<time`).
  Panel tính lại DCF tại **ngày công bố của từng quý** bằng đúng code đang chạy (r = lãi huy động + ERP 6,5%,
  g_term cap_rf, shrink 0,5).
  OShares lấy từ `fiinprox_oshares_pit` vì `ticker_financial.OShares` là TRAP (bị restate). Giá dùng `Price`
  chưa điều chỉnh của phiên đầu tiên ≥ ngày công bố.
- **Mẫu**: các mã nằm trong `universe_pit` (in_universe tại phiên công bố), 2014-01 → 2026-10. Có 17.505 sự kiện;
  **7.510 sự kiện tính được DCF** (484 mã). Các ca DCF không tính được: tài chính, CF_OA_3Y ≤ 0, FCFE ≤ 0.
  **Số cụm độc lập N = 52 quý báo cáo**; mọi CI là bootstrap theo cụm quý, 2.000 lần lặp.
- **Nhóm**: RICH_DEEP < −100% (1.617 sự kiện) · RICH_MILD −100…−20% (1.062) · FAIR −20…+20% (1.019) ·
  CHEAP > +20% (3.812). Đối chứng = FAIR+CHEAP.
- **(a) Lợi nhuận**: yoy = NP_P0/NP_P4 − 1, cắt về [−1, 2], lấy từ dòng **công bố sau** của quý Q+1 và Q+2.
- **(b) Drift**: lọc các sự kiện có SUE mùa vụ > 0 và yoy0 > 0 (3.720 sự kiện; trong đó 837 RICH_DEEP).
  BHAR = lợi suất Close điều chỉnh tính từ close T+1 trừ VNINDEX, ở các mốc 20/40/60 phiên. Excess = BHAR trừ
  trung bình đối chứng **trong cùng ô**. Có 3 cách ghép ô:
  - chặt: quý × ngành 2 số × tercile cỡ × tercile SUE (ghép được 313/837 sự kiện);
  - lỏng: quý × ngành 1 số × tercile cỡ (651/837);
  - rank-RICH: quintile MoS giàu nhất **trong từng quý** so với Q3-5, dùng để tránh phụ thuộc vào mức r lịch sử.
- `profit_*` không được dùng ở bất kỳ bước nào. Kết quả chỉ tính từ giá và số công bố sau ngày đánh giá.

## 2. Bảng chính

Bảng (a), mô tả theo trung vị:

| nhóm | n | yoy0 | yoy Q+1 | yoy Q+2 | P(NP Q+1 giảm) | P(giảm tốc) | P/E trung vị |
|---|---|---|---|---|---|---|---|
| RICH_DEEP | 1617 | 8,4% | 12,3% | 10,6% | 41,2% | 45,3% | 15,3 |
| RICH_MILD | 1062 | 10,0% | 7,0% | 5,5% | 44,1% | 49,8% | 12,5 |
| FAIR | 1019 | 10,3% | 5,6% | 3,9% | 43,7% | 53,2% | 10,5 |
| CHEAP | 3812 | 2,4% | 1,4% | 0,8% | 48,9% | 49,6% | 8,7 |

Tương quan rank giữa MoS và 1/PE trong cùng quý là +0,31. RICH đi kèm P/E cao nhưng không trùng với P/E.

Bảng (b), BHAR60 excess của RICH_DEEP sau surprise dương:

| tập con | chặt | lỏng | rank-RICH | lỏng IS | lỏng OOS |
|---|---|---|---|---|---|
| ALL | −3,8 [−6,3; −1,2] | −3,4 [−5,5; −1,5] | −2,8 [−4,8; −0,8] | −2,3 [−5,7; +0,7] | −3,9 [−6,4; −1,6] |
| ROE5Y<25% | −4,8 [−7,3; −2,1] | −4,5 [−6,5; −2,7] | −3,8 [−5,7; −1,9] | −3,7 [−7,2; −0,6] | −4,9 [−7,4; −2,6] |
| ROE5Y≥25% | +4,6 [−4,4; +14,1] | +4,0 [−2,9; +10,6] | +4,5 [−3,0; +12,4] | +4,3 [−5,3; +14,2] | +3,7 [−5,7; +12,3] |
| Hàng hoá | −5,5 [−11,6; 0,0] | −5,5 [−10,4; −0,5] | −4,1 [−10,3; +3,7] | n=11 | −6,2 [−11,4; −1,2] |
| Tiêu dùng | +4,1 [−1,9; +12,6] | −0,5 [−3,3; +2,2] | −0,8 [−3,9; +2,3] | +1,5 | −1,3 |

Đơn vị: pp; ngoặc là CI95. File: `drift_matched.csv`, `drift_robust.csv`, `outlook_diffs.csv`,
`outlook_robust.csv`.

## 3. Case MCH (as-of 2026-10-23, giá 141.900đ)

**Control tái lập tay**: `fair_value('MCH','2026-10-23',price=141900)` cho FV **59.588đ, MoS −138,1%**, khớp số
của gói DD. Trong panel PIT, sự kiện 2026Q3 cho MoS −136,6% (giá phiên 22/10). Hai cách tính chênh nhau ~1,5pp.

**Giả định DCF**:
- base FCFE = trung bình 3 năm (CFO+CFI) = **5.114 tỷ/năm**, tức **0,70× NP TTM** (7.257 tỷ);
- g_trailing +3,5% (ba điểm tăng trưởng năm: +4,9%, −10,7%, +16,4%), co về **g_exp 5,5%**;
- r = **13,9%**; g_term = **7,4%** (cap_rf).

Để ra giá 141.900đ, FCFE phải tăng **27,6%/năm trong 5 năm**; nếu cho FCFE = NP thì vẫn cần 18,3%/năm. Ngay cả khi
nới cả hai giả định (FCFE = NP và g = 15%), FV cũng chỉ lên 124.796đ. Đổi riêng r = 12% thì FV là 83.973đ. Như vậy
mô hình (shrink 0,5, r 13,9%) **về cấu trúc không thể định giá một mã P/E 25,6 là FAIR**. RICH sâu ở MCH chủ yếu do
giả định.

**Quỹ đạo thực 8 quý (2024Q4→2026Q3)**:
- NP yoy: +2%, −4%, −25%, −19%, −11%, +12%, +11%, +15%. Đây là đà hồi phục từ nền thấp của 2025. NP TTM
  7.257 tỷ **vẫn dưới đỉnh 7.749 tỷ** (TTM 2024Q3). 5 năm NP: 5.619 → 6.660 → 7.749 → 6.917 → 7.257 tỷ.
- **Biên co lại**: NPM 25,6% → 21,8%; GPM 46,6% → 45,5%. ROE trailing 50% → 39%.
- Vốn lưu động: DIO 54 → 63 ngày (tăng), cash cycle 176 → 131 ngày (giảm). CFO/NP biến động mạnh
  (2025Q2 −0,62; 2025Q3 0,19; 2026Q3 1,38). Hai quý CFO yếu năm 2025 là thứ kéo base FCFE xuống 0,70× NP.
- Kết luận cho MCH: lợi nhuận không suy yếu theo nghĩa "đang gãy" (Q3 +15%, phải thu ổn định). Nhưng tăng trưởng
  nền 3 năm gần như phẳng và biên đang co. Giá hiện tại ngầm định ~18-28%/năm, một mức mà quỹ đạo 3 năm qua chưa
  từng cho thấy. MCH thuộc nhóm ROE≥25% tiêu dùng, là nhóm mà nghiên cứu **không kết luận được** về drift
  (ước lượng điểm dương). Vì vậy cờ RICH ở MCH **không phải bằng chứng thống kê chống lại lệnh**; rủi ro thật nằm ở
  định giá, tức mức kỳ vọng tăng trưởng đã cài sẵn trong giá.

## 4. Giới hạn

- **Lãi suất chiết khấu có hindsight** (26 mốc huy động được hiệu chỉnh trên một ngày duy nhất). Đã kiểm tra bằng
  biến thể rank-RICH trong từng quý: kết quả cùng chiều, độ lớn nhỏ hơn một chút.
- OShares lấy từ `fiinprox_oshares_pit`, nguồn ở trạng thái UNVERIFIED-PIT (khớp ex-date 85,7%). Báo cáo tài chính
  có thể đã bị restate về sau (vintage không rõ).
- Surprise ở đây là **SUE mùa vụ tự dựng**, không phải định nghĩa LAG thật trong `earnings_surprise_data.pkl`.
  BHAR tính so với VNINDEX giá, không phải total return.
- Kiểm định nhiều lần: 6 tập con × 3 kỳ hạn × 2 nhóm. Chỉ hai kết quả ALL và ROE<25% ở BHAR60 đứng vững qua 3 cách
  ghép và cả IS/OOS. Hàng hoá và tiêu dùng là thăm dò. Nhóm ROE≥25% chỉ có 84 sự kiện / 44 quý, nên **power
  thấp**: "không kết luận được" ở đây không đồng nghĩa "an toàn".
- Mẫu chỉ gồm các mã DCF tính được (FCFE > 0). Bỏ qua tài chính và các mã capex nặng. Cửa sổ 60 phiên của các quý
  liền kề chồng lên nhau một phần.
- Chưa chạy quant-skeptic. Đề xuất ở mục 4 của phần kết luận **cần quant-skeptic CONFIRMED + user duyệt** trước khi
  đổi `lag_dd_pack.py`.

## Tái lập

```
cd mike/agents/Taylor/research/dcf_rich_outlook_20261024
/home/trido/thanhdt/wc_venv/bin/python build_panel.py   # ~4 phút, ghi panel.csv
/home/trido/thanhdt/wc_venv/bin/python analyze.py       # outlook_*.csv, drift_matched.csv, summary.json
/home/trido/thanhdt/wc_venv/bin/python robust.py        # drift_robust.csv, outlook_robust.csv
/home/trido/thanhdt/wc_venv/bin/python mch_case.py      # case MCH + control
```
