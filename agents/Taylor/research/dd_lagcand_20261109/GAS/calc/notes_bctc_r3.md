# GAS r3 — phân loại ĐỦ từng dòng BCĐKT HN 30/09/2026 (tỷ đồng)
Nguồn: src/png/vn_p03.png, vn_p04.png (BCĐKT), vn_p21-p29, p37-p38 (TM5-23, TM38); src/ocr_h1/p50.txt (TM25 DP DH); src/dl_20261123/ocr (BCTC KT 2025).
Nhãn: FIN=cầu tiền ròng · FIN_LIKE=như nợ · GROWTH_BOOK=dự án tăng trưởng giá sổ (V4a) · RECOV=tài sản thu hồi · COMPLIANCE_OUT=chi bắt buộc (D3) · OP_NWC=vốn lưu động hoạt động (nằm trong NOPAT, conv=1) · OP_FIXED=tài sản hoạt động sinh NOPAT · NONOP_IN_NP=ngoài HĐ nhưng LN đã trong chuỗi LN · TAX_TIMING=chênh lệch tạm thời (độ nhạy)

## Tài sản
| Mã | Số | Nhãn | Ghi chú |
|---|---|---|---|
| 110 Tiền | 15,540.6 | FIN | cầu tiền ròng |
| 123 HTM ngắn hạn | 35,269.9 | FIN | cầu tiền ròng |
| 131 Phải thu KH | 20,288.3 | OP_NWC | TM5; trong đó bên liên quan 10.836,9 (PVPower 8.870,4) |
| 132 Trả trước người bán NH | 133.8 | OP_NWC |  |
| 135 Phải thu NH khác | 6,942.5 | OP_NWC | TM6: dự thu DT bán+vận chuyển khí 6.625,7; lãi dự thu tiền gửi 0; Bạc Liêu Tower 56,2; khác 260,6 |
| 136 DP phải thu khó đòi | -1,833.8 | OP_NWC | TM7: PVPower gốc 1.523,5 / thu hồi được 30,5 |
| 141 HTK | 2,763.6 | OP_NWC | TM8 |
| 142 DP giảm giá HTK | -192.3 | OP_NWC |  |
| 161 CP trả trước NH | 130.8 | OP_NWC | TM9 |
| 162 VAT được khấu trừ | 819.2 | OP_NWC |  |
| 163 Phải thu NN | 79.8 | OP_NWC | TM10 |
| 212 Trả trước người bán DH | 78.8 | OP_NWC |  |
| 215a Phải thu DH: góp vốn BCC Lô B | 1,395.7 | GROWTH_BOOK | TM38 p35 (CN PVN – Cty điều hành đường ống Tây Nam); BCTC KT 2025: 'Phải thu góp vốn theo BCC (i)' 1.022,1 @31/12/25, BCC 26a/2010, GAS 51% ⇒ V4(a) NPV0 giá sổ — MỚI r3 |
| 215b Phải thu DH khác (ký quỹ) | 30.9 | OP_NWC |  |
| 221+227 TSCĐ HH+VH | 14,467.9 | OP_FIXED | sinh NOPAT; capex duy trì ≈ khấu hao |
| 240 BĐS đầu tư | 28.0 | OP_FIXED |  |
| 252 XDCB | 5,916.4 | GROWTH_BOOK | TM13 (r2 E1) |
| 262 Đầu tư LDLK | 392.7 | NONOP_IN_NP | TM14 PVGAS South 334,7 + PVGAZROM 58,0; LN góp vốn đã nằm trong chuỗi LN ⇒ KHÔNG cộng thêm (tránh tính 2 lần) |
| 263+264 Góp vốn khác (sau DP) | 10.0 | NONOP_IN_NP | nhỏ, bỏ qua |
| 265 HTM DH | 7.0 | FIN | cầu tiền ròng |
| 271a Trả trước bao tiêu | 1,775.5 | RECOV | TM15 (r2 E6a) |
| 271b CP trả trước DH khác | 945.4 | OP_FIXED | phân bổ CP |
| 272 TS thuế hoãn lại | 29.7 | TAX_TIMING | độ nhạy cùng 342 |
| **Tổng** | **105,020.4** | | BCĐKT 280 = 105.020,5 |

## Nợ + CĐKKS
| Mã | Số | Nhãn | Ghi chú |
|---|---|---|---|
| 311 Phải trả NB | 6,713.3 | OP_NWC | TM16; PVN 3.582,6 |
| 312 Người mua trả trước | 201.9 | OP_NWC |  |
| 313 Cổ tức phải trả | 5,491.7 | FIN | cầu tiền ròng (lệch 540,7 vs 6.032,4 — mở) |
| 314 Thuế phải nộp | 2,467.3 | OP_NWC | TM17; TNDN 2.196,4 = thuế dồn tích của LN 9T (nằm trong NOPAT) |
| 315 Phải trả NLĐ | 1,049.5 | OP_NWC |  |
| 316 CP phải trả | 4,964.1 | OP_NWC | TM18: trích trước mua khí 4.050,5; phí thương hiệu PVN 163,4; lãi vay 66,8 |
| 318 Theo tiến độ HĐXD | 1.5 | OP_NWC |  |
| 319 DT chờ phân bổ NH | 35.7 | OP_NWC |  |
| 320 Phải trả NH khác | 382.1 | OP_NWC | TM19 |
| 321 Vay NH | 1,551.2 | FIN |  |
| 322 DP phải trả NH | 16.0 | OP_NWC |  |
| 323 Quỹ KT-PL | 875.6 | FIN_LIKE | r2 E6c |
| 337 DT chờ phân bổ DH | 21.5 | OP_NWC |  |
| 338 Phải trả DH khác | 101.4 | OP_NWC | TM21 ký quỹ 98,8 |
| 339 Vay DH | 2,710.4 | FIN | TM22 |
| 342 Thuế hoãn lại phải trả | 283.4 | TAX_TIMING | độ nhạy |
| 343 DP phải trả DH | 3,300.0 | COMPLIANCE_OUT | TM25 H1/26: thu dọn/hoàn nguyên công trình khí, dự toán BCT duyệt ⇒ D3 CASH_OUTFLOW 100% base — MỚI r3 |
| 344 Quỹ KH&CN | 235.9 | FIN_LIKE | MỚI r3: trừ như nợ |
| 429 CĐKKS | 1,409.5 | FIN | cầu tiền ròng |
| **Tổng** | **31,812.0** | | BCĐKT 300 = 30.402,3 + 429 1.409,5 = 31.811,8 |

## Tổng theo nhãn (TS − nợ)
| Nhãn | Tỷ |
|---|---|
| COMPLIANCE_OUT | -3,300.0 |
| FIN | 39,654.7 |
| FIN_LIKE | -1,111.5 |
| GROWTH_BOOK | 7,312.1 |
| NONOP_IN_NP | 402.7 |
| OP_FIXED | 15,441.3 |
| OP_NWC | 13,287.3 |
| RECOV | 1,775.5 |
| TAX_TIMING | -253.7 |

Kiểm: TS − nợ − CĐKKS = 73,208.4 ⇒ VCSH CĐ mẹ 74.618,1 − 1.409,5 = 73.208,6

Vốn lưu động HĐ 01/01/2026 (cùng phạm vi, 215b ước 35,5 theo KT2025 ký quỹ): 11,693.6; 30/09/2026: 13,287.3; Δ +1,593.7 (chủ yếu PVPower: phải thu KH 4.003,3→8.870,4; phải thu khác 2.566,2→2.980,5; phải trả NB giảm 11.925→6.713)

## Sự kiện mới r3 (nguồn)
- BCTC HN KT 2025: Deloitte VN, ngày 28/02/2026, CHẤP NHẬN TOÀN PHẦN, đoạn 'Vấn đề khác' chỉ nói số so sánh 2024 do hãng khác kiểm toán (chấp nhận toàn phần 20/02/2025) — ocr/k08.txt.
- Cam kết vốn 31/12/2025 (TM35, ocr/k60.txt): Lô B–Ô Môn 12.394,4 · mở rộng kho LNG Thị Vải 1→3 tr tấn 8.827,6 · ERP 16,7 · tổng 21.238,7 tỷ.
- Hợp đồng (TM35): mua khí Lô 05.2/05.3 0,2506 tỷ m³/năm đến 12/2026; Lô 102/106 0,204 đến hết bình ổn; Lô 05-1b/c 1,508 tỷ m³/năm đến 12/2026; LNG Shell 20,7 triệu MMBTU/năm 2027–2031; bán khí NCS cho NT2 0,6 tỷ m³/năm đến 12/2026. Giấy phép mỏ: KHÔNG có trong BCTC (không kiểm chứng được).
- Bên liên quan (TM38 Q3/26 p35-36): phải thu KH PVPower 8.870,4 (01/01: 4.003,3), phải thu khác PVPower 2.980,5; PVN: phải trả NB 3.582,6, CP phải trả 3.131,3, phải trả khác 13,0; tiền gửi PVComBank 1.783,6.
