# Đối chiếu NP quý 4/2025: STB, EIB, SSB (19/11/2026)

**Kết luận: không phải lỗi nguồn. STB và EIB là lỗ thật do trích lập dự phòng. SSB khớp nội bộ với PBT cả năm. Rating 5 của cả 3 mã là đúng, không cần sửa BQ.**

## 1. Hàng BQ (tav2_bq.ticker_financial, NP tỷ VND, Release_Date)
| Mã | 25Q1 | 25Q2 | 25Q3 | **25Q4** (rel. 2026-02-02) | 26Q1 | 26Q2 | 26Q3 | ROE_Trailing 26Q3 |
|---|---|---|---|---|---|---|---|---|
| STB | 2.897 | 2.894 | 2.901 | **−2.752** | 1.584 | 1.347 | 1.347 | 2,2% |
| EIB | 658 | 506 | 445 | **−472** | 269 | 250 | 144 | 0,7% |
| SSB | 3.492 | 1.133 | 779 | **104** | 1.111 | 991 | 1.052 | 7,7% |

Peer 2025Q4 không hệ thống âm: đa số ngân hàng Q4 > Q3 (BID, CTG, MBB, MSB, TPB tăng). Chỉ NVB cũng âm (−652 tỷ). Vì vậy đây không phải lỗi ingest chung.

## 2. Đối chiếu nguồn công khai (WebSearch + đọc bài báo; KHÔNG đọc được BCTC PDF gốc)
- **STB: KHỚP, sự kiện thật.** Kết quả sơ bộ 8/1/2026: PBT hợp nhất FY2025 7.628 tỷ (52% kế hoạch 14.650), 9M PBT 10.988 tỷ ⇒ Q4 PBT ≈ −3.360 tỷ (số suy ra). Nguyên nhân: trích lập dự phòng cả năm ~11.160–11.300 tỷ, riêng Q4 tăng hơn 9.000 tỷ, ban lãnh đạo mới xử lý nợ xấu tồn đọng. NP −2.752 tỷ trong BQ phù hợp mức lỗ trước thuế này. Hạn chế: bài báo là số sơ bộ chưa kiểm toán, không nêu LNST nên chưa đối chiếu được số tuyệt đối sau thuế.
- **EIB: KHỚP, sự kiện thật.** Báo chí: Q4/2025 lỗ sau thuế 472 tỷ (trùng đúng −472,482 tỷ trong BQ); lỗ trước thuế ~537 tỷ; PBT cả năm ~1.511 tỷ (−64% YoY). Nguyên nhân: tăng trích lập dự phòng. Tôi chưa xác nhận số này là sau kiểm toán.
- **SSB: KHÔNG ĐỌC ĐƯỢC BCTC GỐC, nhưng khớp nội bộ.** Công văn giải trình biến động LNST Q4/2025 (30/01/2026) có tồn tại, nhưng PDF không trích được nội dung (đĩa đầy cắt dở). Kiểm tra gián tiếp: PBT FY2025 = 6.868 tỷ (+13,7% YoY, 106% kế hoạch); tổng NP 4 quý trong BQ = 3.492+1.133+779+104 = 5.508 tỷ ≈ 80,2% PBT, hợp lý với thuế ~20%. Tổng cả năm đúng ⇒ không có dấu hiệu lỗi dấu/đơn vị. Phân bổ theo quý (Q1 3.492 tỷ rất cao, Q4 chỉ 104 tỷ) CHƯA đối chiếu được với BCTC quý gốc; xếp **không xác định ở mức từng quý**, nhưng ROE_Trailing 26Q3 chỉ phụ thuộc tổng 4 quý gần nhất (26Q1..26Q3 + 25Q4) nên ít nhạy với cách phân bổ Q1-Q4/2025.

## 3. Phân loại
| Mã | Phân loại | Hành động BQ |
|---|---|---|
| STB | Khớp (sự kiện thật: trích lập đột biến) | Không |
| EIB | Khớp (sự kiện thật: trích lập) | Không |
| SSB | Tổng năm khớp PBT; chia quý không xác định | Không; nếu muốn chắc, mở công văn SSB 30/01/2026 |

## 4. Rating 8L
Không có lỗi nguồn nên không tính lại ROE_Trailing; không chạy rating_8l.py (đĩa đầy, và không cần). ROE_Trailing 26Q3 = 2,2% / 0,7% / 7,7% (<8%) là số thật ⇒ **rating 5 đúng, 3 mã không bị chặn oan.** Cờ cảnh báo: STB/EIB lợi nhuận đã hồi lại +1.347 / +144 tỷ Q3/2026 nhưng trailing còn bị Q4/2025 âm kéo; Q4/2025 rời cửa sổ 4 quý ở BCTC 2026Q4 (công bố ~tháng 1-2/2027) ⇒ ROE_Trailing sẽ tự bật lên lúc đó (STB ≈ (1.584+1.347+1.347+Q4/26)/vốn). Nên rà lại rating 3 mã khi 2026Q4 ra, không cần can thiệp trước.

## 5. Hạn chế
Không truy cập được BCTC hợp nhất gốc/kiểm toán (chỉ báo chí + số sơ bộ); không có FiinPro bank ratios; không chạy rating_8l.py; ổ đĩa gốc đầy 100% làm dừng việc trích PDF SSB.
