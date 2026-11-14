# Giả định định giá MÙ GIÁ — PAT (CTCP Phốt pho Apatit Việt Nam), lập 14/11/2026

Người định giá không biết và không tìm giá cổ phiếu. Đơn vị: tỷ đồng (trừ khi ghi khác). 25.000.000 cp (TM17 Q3/26).
Ngày neo bảng cân đối: 30/09/2026. Ngày định giá: 14/11/2026 (đẩy PV từ 30/09 tới 14/11 theo r).

## A. Nền dữ liệu đã tự kiểm trên ảnh gốc
- KQKD Q3/26 (png_q326/p07): DT 440,032; LN gộp 63,604; DTTC 11,371; CPTC 1,467; CPBH 5,049; QLDN 4,711; LNTT 63,747; thuế 4,427; LNST 59,320. 9T26: DT 1.379,304; LN gộp 250,598; LNTT 230,384; LNST 215,713. Khớp facts.
- KQKD H1/26 (png_bn26/p09): DT 939,271; LN gộp 186,994; DTTC 20,938; CPTC 6,017; CPBH 27,239; QLDN 8,038; LNTT 166,638; LNST 156,393. H1 + Q3 = 9T (kiểm trong model).
- BCĐKT 30/09/26 (p05-p06): tiền 1,246; HTM 558,069; vay NH 67,218; quỹ KTPL 76,690; VCSH 708,446; tổng TS 942,190. Khớp facts (tiền BS 1,246; TM3 1,286 không kiểm lại — dùng số BS).
- TM4 (p20): cầm cố 70 tỷ BIDV (bảo lãnh tiền điện), 199 tỷ BIDV + 130 tỷ ACB (bảo đảm vay của Công ty), 40 tỷ + 100.000 USD Vietinbank (bảo đảm vay của Công ty **và các công ty thành viên**).
- TM16 (p26): trích quỹ KTPL 2025 = 20,713 / LNST 2025 343,21 = 6,0%; TM19 (p28): 9T26 tạm trích 12,943 = 6,0% LNST 9T.
- TM27 (p30): ưu đãi 10% 15 năm (2018–2032), miễn 4 năm 2018–2021, giảm 50% 9 năm 2022–2030 ⇒ 5% tới 2030, 10% 2031–2032, 20% từ 2033. Thu nhập tài chính (lãi tiền gửi) chịu 20% (cơ sở: ETR 9T26 6,4% ≈ 5%×LN HĐ + 20%×lãi tiền gửi).
- EY bản tin 07/2025 (đã đọc PDF): NĐ 199/2025 — phốt pho vàng HS 2804.70.00.10: 5% (08/07–31/12/2025), **10% từ 01/01/2026, 15% từ 01/01/2027**.
- TM13 (p24): thuế XK đã nộp 9T26 = 51,61 tỷ trên DT nước ngoài 9T 487,51 ⇒ ~10% (khớp mức 10%).
- BQ ticker_financial: LNST quý 2026 Q1 46,556 / Q2 109,837 / Q3 59,320 (tổng = 215,713 ✓); DT Q1 421,916 / Q2 517,355.

## B. Lợi nhuận hoạt động lõi (EBIT HĐ = LN gộp − CPBH − QLDN; KHÔNG gồm thu nhập tài chính)
| Kỳ | EBIT HĐ | Quy năm | Biên HĐ | P4 TQ TB (CNY/t, sunsirs) |
|---|---|---|---|---|
| 2024 | 248,8 | 248,8 | 14,5% | ~23.300 |
| 2025 | 339,1 | 339,1 | 17,6% | ~23.060 |
| Q3/25 | 105,8 | 423 | 20,9% | 22.592 |
| H1/26 | 151,7 | 303 | 16,2% | ~27.810 |
| Q3/26 | 53,8 | 215 | 12,2% | 27.606 |
| TTM (Q4/25+9T26) | 273,7 | 273,7 | 14,5% | — |

**Điểm khác biệt quan trọng nhất BCTC vs khung ngành:** giá P4 TQ Q3/26 cao hơn Q3/25 **+22%**, nhưng DT PAT −13%, LN gộp −51%.
Cùng lúc tỷ trọng bán cho mẹ DLC lên 85,5% DT quý (Q3/26) và mua NVL từ DLC 628 tỷ/9T. ⇒ Kinh tế của PAT trong 2026 **không còn
bám giá P4 TQ**; biên do giá chuyển nhượng nội bộ + thiếu quặng (từ T6/2026) + than cốc (+52% Q3/26 YoY) quyết định.
Mô hình KHÔNG suy EBIT từ giá P4; dùng mức EBIT HĐ theo kịch bản (cơ sở: run-rate quý thật).

## C. Kịch bản (EBIT HĐ năm 2027, danh nghĩa; từ 2028 tăng theo g)
| Kịch bản | EBIT HĐ 2027 | Q4/2026 | Xác suất | Điều kiện kinh tế | Cơ sở dữ liệu |
|---|---|---|---|---|---|
| Xấu | 160 | 45 | 0,30 | Quặng thiếu kéo dài qua 2027; P4 TQ về ~23–24k; giá chuyển nhượng DLC giữ PAT ở mức "gia công" biên HĐ ~9%; thuế XK 15% trên phần XK trực tiếp còn lại | Q3/26 quy năm 215 trừ P4 −13% & thuế XK +5pp × ~250 tỷ XK trực tiếp (−12,5); Bobby P(P4<23k sau 12T)=0,32 |
| Cơ sở | 245 | 54 | 0,50 | Quặng gỡ một phần (dùng quặng loại III tồn); P4 TQ ~25–26,5k; tỷ trọng bán DLC giữ ~80%+, biên HĐ ~13,5% trên DT ~1.800 | Trung bình Q3/26 quy năm (215) và 2024 (249) và TTM (274) ≈ 246; trừ đầu gió 2027 (thuế XK 15%, cốc +41%) bù bởi quặng gỡ một phần; Bobby trung vị F1/F2 −7…−12% |
| Tốt | 330 | 65 | 0,20 | Quặng bình thường hoá; P4 ≥ 28k (mùa khô khắc nghiệt / chống nội quyển); DLC trả giá ngang giá XK trừ thuế | 2025 = 339; Bobby F7 P(3 nhà máy tuyển ≥80%)=0,30, P(P4>32k)=0,10–0,12 ⇒ 0,20 |

Kỳ vọng EBIT 2027 = 0,3×160 + 0,5×245 + 0,2×330 = 236,5 (thấp hơn TTM 273,7 — nghiêng xuống có chủ đích vì điểm dữ liệu mới nhất Q3/26 là điểm yếu và đầu gió 2027 đã biết).

## D. Tham số dòng tiền
- Thuế TNDN trên EBIT HĐ: Q4/2026–2030 5%; 2031–2032 10%; từ 2033 20% (TM27).
- Quỹ KTPL: 6,0% LNST mỗi năm (cơ sở TM16: 2025 = 6,0%; 2024 = 5,1%) — trừ khỏi FCFE (dòng tiền cho người lao động, không cho cổ đông).
- Capex = khấu hao (~45 tỷ/năm, cơ sở KH 2025 44,82; 9T26 33,66) ⇒ FCFF HĐ = NOPAT − ΔVLĐ. Không dự án mới (NPV = 0).
- ΔVLĐ = g × VLĐ thuần phi tiền 53 tỷ (cơ sở BCĐKT 30/09/26: PT KH+trả trước+HTK+khác 143,2 − PTNB/NM trả trước/thuế/NLĐ/khác 89,8). Không giả định giải phóng/hấp thụ VLĐ một lần.
- Nợ vay 67,2 và tiền/HTM được xử lý trong tiền ròng ⇒ KHÔNG tính lãi vay và lãi tiền gửi vào dòng tiền HĐ (tránh đếm hai lần). Lãi/lỗ tỷ giá: loại (không định kỳ).
- Khoản một lần loại khỏi chuẩn hoá: truy thu thuế năm trước 6,79 tỷ trong Q4/25 (KT25); LN khác 0,19 (Q3/25).

## E. Tiền ròng thật 30/09/2026
Tiền 1,246 + HTM 558,069 (gồm lãi dự thu 6,50) − vay NH 67,218 − quỹ KTPL 76,690 = **415,41 tỷ**.
- Cầm cố: 70 (bảo lãnh tiền điện) + 199 + 130 (bảo đảm vay của PAT, dư nợ chỉ 67,2) + 40 + 2,6 (100.000 USD × ~25.725, ước lượng; bảo đảm vay **cả công ty thành viên**) = 441,6 tỷ.
- Độ nhạy: (S1) trừ 42,6 tỷ cầm cố cho công ty thành viên; (S2) trừ toàn bộ 441,6 tỷ cầm cố (cực đoan).
- Không trừ cổ tức sau 30/09 (BCTC không ghi cổ tức phải trả; tin "cổ tức 2026 90%" chỉ là báo, chưa có nghị quyết) — ghi vào điều cần kiểm.

## F. Chi phí vốn và tăng trưởng
- Lãi huy động hiệu dụng 12T tại neo 03/11/2026 = 7,40% (đã chạy lại `effective_deposit_rate('2026-11-03')` = 7,40%); tại 14/11/2026 = 7,40% (CCTG 12T 02/11).
  ⇒ r = 13,5% + β×(7,40 − 7,40) = **13,5%** (β=1). Độ nhạy Δlãi huy động ±50/±100bp × β 0,5/1,0.
- **g = 2,0%** (cơ sở: công suất lò cố định ⇒ tăng trưởng khối lượng 0; giá P4 do TQ định, danh nghĩa VND chỉ chuyển một phần lạm phát:
  lạm phát VN ~4% đẩy chi phí điện/nhân công tương ứng ⇒ biên danh nghĩa tăng chậm hơn giá; cộng thêm đồng hồ cắt hào (thuế XK, thuế TNDN
  bậc thang, đất thuê). g = 2% ≪ GDP danh nghĩa dài hạn VN ~8–10%.) Độ nhạy g 0% / 3%.
- Ngang dự báo tường minh: Q4/2026 + 2027–2035; giá trị cuối tại cuối 2035 với thuế 20%.

## G. Moat
- ROIC HĐ (NOPAT HĐ / (TSCĐ ròng + VLĐ phi tiền)) ≫ Ke nhiều năm: 2024 ~248,8×0,95/~280 ≈ 84%; 2025 ~339×0,95/~200–300 > 100%;
  TTM ~260/270 ≈ 96%. Trên NGUYÊN GIÁ TSCĐ (573) vẫn ~40–55% ≫ 13,5%. BQ ROE5Y 72%, ROE3Y 51%, ROE TTM 43%.
- Cơ chế: tiếp cận quặng apatit Lào Cai qua tập đoàn mẹ (hào HÀNH CHÍNH ở cấp tập đoàn, PAT không giữ giấy phép mỏ — không có thuế tài nguyên
  trong TM13) + tài sản lò đã khấu hao gần hết. PAT là price-taker giá TQ; phần siêu lợi nhuận bị mẹ (51%) phân chia qua giá chuyển nhượng
  hai chiều (bằng chứng 2026: P4 +22% mà LN gộp Q3 −51%).
- Đồng hồ cắt hào: thuế XK 15% (01/01/2027), thuế TNDN 10% (2031) → 20% (2033), đất thuê (chi phí GPMB phân bổ 16 năm, còn ~8 năm),
  cổng quặng hành chính, vụ án môi trường/khai thác.
- **Phân loại: NARROW** ⇒ không thưởng, không trừ tham số (không dùng giai đoạn lợi thế cạnh tranh kéo dài, không ép fade về Ke). Độ nhạy moat:
  fade ROIC về Ke (TV với EBIT 2035 × 0,8) báo riêng.

## H. V_ngắn
LNST chuẩn hoá = trung vị TTM của 12 quý gần nhất (TTM kết thúc Q4/23 … Q3/26), dùng LNST quý BQ, Q4/25 thay bằng số kiểm toán 70,88
(343,21 − 272,33) rồi cộng lại 6,79 truy thu thuế. ROE = LNST TTM / VCSH bình quân (31/12/25, 30/09/26). Tỷ lệ tái đầu tư = g/ROE chặn [0; 0,8].
V_ngắn = LNST_cn × (1 − b) × (1+g)/(r−g). (V_ngắn đã gồm lãi tiền gửi trong LNST ⇒ KHÔNG cộng tiền ròng.)

## I. Rủi ro pháp lý — CHỈ WARNING, kịch bản độ nhạy riêng (không nằm trong base)
BN26 soát xét NGOẠI TRỪ (khởi tố nguyên lãnh đạo chủ chốt 17/03/2026 và Chủ tịch đương nhiệm 23/07/2026: vi phạm kế toán, khai thác tài nguyên,
gây ô nhiễm môi trường). KT25 ngoại trừ. Độ nhạy L1: thu hồi ưu đãi thuế (20% từ Q4/2026) + truy thu ưu đãi 2022–9T2026 ~15%×EBIT HĐ ~(1.400) ≈ 210 tỷ
(ước lượng) + nghĩa vụ môi trường/hoàn nguyên 100 tỷ (ước lượng). Không gắn xác suất vào tâm.

## J. Thanh khoản
Không áp chiết khấu bằng đồng. Báo giá trị trước CK + bảng CK 5/10/20%; khối lượng khớp trung vị 6T/3T + số phiên không khớp
(lịch: ngày làm việc trừ nghỉ lễ `trading_bot.vn_market.is_holiday`; phiên không có dòng hoặc Volume=0 = không khớp).

## K. Đất thuê hữu hạn (độ nhạy, không phải base)
Nếu hợp đồng đất KCN không gia hạn khi chi phí GPMB phân bổ hết (~2034): dòng tiền tới hết 2034, không TV, thu hồi VLĐ, trừ chi phí hoàn nguyên 50 tỷ (ước lượng).

```json
{
  "shares_mn": 25.0,
  "val_anchor": "2026-09-30",
  "val_date": "2026-11-14",
  "net_cash": {"cash": 1.246, "htm": 558.069, "debt": 67.218, "ktpl_fund": 76.690},
  "pledged": {"member_cos": 42.6, "total": 441.6},
  "scenarios": {
    "bear": {"ebit_2027": 160.0, "ebit_q4_2026": 45.0, "p": 0.30},
    "base": {"ebit_2027": 245.0, "ebit_q4_2026": 54.0, "p": 0.50},
    "bull": {"ebit_2027": 330.0, "ebit_q4_2026": 65.0, "p": 0.20}
  },
  "tax": {"to_2030": 0.05, "y2031_2032": 0.10, "from_2033": 0.20},
  "ktpl_rate": 0.06,
  "nwc": 53.0,
  "r_anchor": 0.135, "dep_anchor": 0.074, "dep_now": 0.074, "beta": 1.0,
  "g": 0.02,
  "last_explicit_year": 2035,
  "vshort": {"np_q": {"2023Q1": 72.693, "2023Q2": 77.217, "2023Q3": 83.543, "2023Q4": 52.138,
                       "2024Q1": 60.830, "2024Q2": 55.723, "2024Q3": 67.382, "2024Q4": 81.007,
                       "2025Q1": 84.727, "2025Q2": 77.633, "2025Q3": 109.967, "2025Q4": 70.882,
                       "2026Q1": 46.556, "2026Q2": 109.837, "2026Q3": 59.320},
             "one_off_addback": {"2025Q4": 6.79},
             "equity_open": 585.946, "equity_close": 708.446},
  "legal": {"tax_rate": 0.20, "back_tax": 210.0, "env_liab": 100.0},
  "lease_end_year": 2034, "restoration_cost": 50.0,
  "liq_discounts": [0.05, 0.10, 0.20]
}
```
