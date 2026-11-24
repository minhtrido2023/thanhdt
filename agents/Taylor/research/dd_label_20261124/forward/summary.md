# DD forward outcome — chẩn đoán giá/tâm → lợi suất sau 63/126/252 phiên

_Sinh bởi `bin/dd_forward_outcome.py` ngày 2026-11-24 · lịch BQ tới 2026-11-23 · CHẨN ĐOÁN, không đổi luật, không wire._
**Mốc đánh giá chính thức: 2027-03-31.**

## Quy ước (đọc trước khi dùng số)
- Sổ `kb/dd_price_zones.json`: 133 entry thô → **40** (mã, dd_date) sau khi lấy entry CUỐI (rev cao nhất; hoà → recorded_at muộn nhất).
- r = price_ref / center tại lúc ghi sổ. Thiếu tâm ⇒ nhóm `KHONG_CO_TAM`.
- PIT/T+1: phiên vào = phiên giao dịch đầu tiên SAU max(ngày recorded_at ICT, price_date, dd_date); giá vào = Close phiên đó.
- Lợi suất h phiên giao dịch (lịch = ngày có dòng VNINDEX trong BQ). `Close` BQ hồi tố cổ tức+tách ⇒ **total-return gần đúng** (tầng phát hiện, chưa đối soát broker — không phải số §21).
- excess = lợi suất mã − VNINDEX **TR gộp** (`vnindex_tr_daily.csv`, 5 phiên cuối provisional). VNINDEX giá cũng có trong CSV.
- Nhãn vùng DƯỚI/TRONG/TRÊN suy cơ học từ zone_low/zone_high vs price_ref (không parse chữ).

## Độ phủ kết quả (trung thực)
| h | có kết quả / tổng entry | chưa đủ kỳ | chưa có phiên vào (neo ≥ phiên cuối BQ) | thiếu giá | ngày-DD độc lập có kết quả |
|---|---|---|---|---|---|
| 63 | 0 / 40 | 19 | 21 | 0 | 0 / 18 |
| 126 | 0 / 40 | 19 | 21 | 0 | 0 / 18 |
| 252 | 0 / 40 | 19 | 21 | 0 | 0 / 18 |

Phân bố ngày DD: 18 ngày-DD khác nhau, 36 mã, khoảng 2026-10-26 → 2026-11-22; số THÁNG lịch độc lập: 2.

## Nhóm theo r (luật 4: r ≤ 0,85)
| h | nhóm | n sổ | n mã | n ngày-DD | n có KQ | mã có KQ | ngày-DD có KQ | TB ret | TB excess | trung vị excess | tỉ lệ thắng VNI-TR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 63 | 0.85<r<=1.0 | 10 | 10 | 6 | 0 | 0 | 0 | — | — | — | — |
| 63 | KHONG_CO_TAM | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 63 | r<=0.85 (luat4) | 6 | 5 | 5 | 0 | 0 | 0 | — | — | — | — |
| 63 | r>1.0 | 23 | 22 | 14 | 0 | 0 | 0 | — | — | — | — |
| 126 | 0.85<r<=1.0 | 10 | 10 | 6 | 0 | 0 | 0 | — | — | — | — |
| 126 | KHONG_CO_TAM | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 126 | r<=0.85 (luat4) | 6 | 5 | 5 | 0 | 0 | 0 | — | — | — | — |
| 126 | r>1.0 | 23 | 22 | 14 | 0 | 0 | 0 | — | — | — | — |
| 252 | 0.85<r<=1.0 | 10 | 10 | 6 | 0 | 0 | 0 | — | — | — | — |
| 252 | KHONG_CO_TAM | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 252 | r<=0.85 (luat4) | 6 | 5 | 5 | 0 | 0 | 0 | — | — | — | — |
| 252 | r>1.0 | 23 | 22 | 14 | 0 | 0 | 0 | — | — | — | — |

## Nhóm theo nhãn vùng
| h | nhóm | n sổ | n mã | n ngày-DD | n có KQ | mã có KQ | ngày-DD có KQ | TB ret | TB excess | trung vị excess | tỉ lệ thắng VNI-TR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 63 | DUOI | 4 | 4 | 3 | 0 | 0 | 0 | — | — | — | — |
| 63 | KHONG_RO | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 63 | TREN | 11 | 11 | 8 | 0 | 0 | 0 | — | — | — | — |
| 63 | TRONG | 24 | 23 | 14 | 0 | 0 | 0 | — | — | — | — |
| 126 | DUOI | 4 | 4 | 3 | 0 | 0 | 0 | — | — | — | — |
| 126 | KHONG_RO | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 126 | TREN | 11 | 11 | 8 | 0 | 0 | 0 | — | — | — | — |
| 126 | TRONG | 24 | 23 | 14 | 0 | 0 | 0 | — | — | — | — |
| 252 | DUOI | 4 | 4 | 3 | 0 | 0 | 0 | — | — | — | — |
| 252 | KHONG_RO | 1 | 1 | 1 | 0 | 0 | 0 | — | — | — | — |
| 252 | TREN | 11 | 11 | 8 | 0 | 0 | 0 | — | — | — | — |
| 252 | TRONG | 24 | 23 | 14 | 0 | 0 | 0 | — | — | — | — |

## Kết luận
**KHÔNG KẾT LUẬN.** Ngày-DD độc lập có kết quả: h63=0, h126=0, h252=0 (cần ≥ 30, hoặc dùng khối tháng). Số trong bảng trên (nếu có) chỉ là mô tả, không phải bằng chứng.

## MDE và mốc dữ liệu đủ (ƯỚC LƯỢNG)
- h=63: σ(excess, ĐO từ lịch sử 36 mã DD, bước 5 phiên chồng lấn, 5821 mẫu — KHÔNG phải outcome sổ DD) = 18.2%. MDE 80% power α=0,05 hai phía, so 2 nhóm chia đôi 18 ngày-DD hiện có (**ước lượng**, coi mỗi ngày-DD là 1 đơn vị độc lập — lạc quan vì cùng mùa BCTC): ≈ 24.0 điểm %. Ngày-DD hiện có đủ kỳ h=63 **tới ~2027-03-04** (ước lượng, lịch xấp xỉ T2–T6 trừ Tết 4–12/02/2027). Cần ≥30 ngày-DD độc lập: hiện chỉ 18 ngày-DD ⇒ cần thêm ≥12 ngày-DD MỚI (DD mới) cộng thời gian chờ h phiên.
- h=126: σ(excess, ĐO từ lịch sử 36 mã DD, bước 5 phiên chồng lấn, 5356 mẫu — KHÔNG phải outcome sổ DD) = 26.6%. MDE 80% power α=0,05 hai phía, so 2 nhóm chia đôi 18 ngày-DD hiện có (**ước lượng**, coi mỗi ngày-DD là 1 đơn vị độc lập — lạc quan vì cùng mùa BCTC): ≈ 35.1 điểm %. Ngày-DD hiện có đủ kỳ h=126 **tới ~2027-06-01** (ước lượng, lịch xấp xỉ T2–T6 trừ Tết 4–12/02/2027). Cần ≥30 ngày-DD độc lập: hiện chỉ 18 ngày-DD ⇒ cần thêm ≥12 ngày-DD MỚI (DD mới) cộng thời gian chờ h phiên.
- h=252: σ(excess, ĐO từ lịch sử 36 mã DD, bước 5 phiên chồng lấn, 4457 mẫu — KHÔNG phải outcome sổ DD) = 41.1%. MDE 80% power α=0,05 hai phía, so 2 nhóm chia đôi 18 ngày-DD hiện có (**ước lượng**, coi mỗi ngày-DD là 1 đơn vị độc lập — lạc quan vì cùng mùa BCTC): ≈ 54.3 điểm %. Ngày-DD hiện có đủ kỳ h=252 **tới ~2027-11-24** (ước lượng, lịch xấp xỉ T2–T6 trừ Tết 4–12/02/2027). Cần ≥30 ngày-DD độc lập: hiện chỉ 18 ngày-DD ⇒ cần thêm ≥12 ngày-DD MỚI (DD mới) cộng thời gian chờ h phiên.
- Tại mốc 2027-03-31 (**ước lượng**, lịch phiên tương lai xấp xỉ): h=63: 40/40 entry đủ kỳ trước mốc; h=126: 0/40 entry đủ kỳ trước mốc; h=252: 0/40 entry đủ kỳ trước mốc.

## Kiểm look-ahead (mục 5)
- price_ref có dòng BQ `Price` thô tại price_date: 40/40 entry; khớp ≤0,5%: **39** (khớp = price_ref là giá thật phiên đó, không phải số điền sau).
- Không có dòng BQ tại price_date (mã/ngày thiếu): 0.
- Entry cuối có price_date SAU dd_date: 28/40 (đã cập nhật giá khi hiệu đính — chấp nhận được vì phiên vào được neo theo max(recorded_at, price_date, dd_date)).
- recorded_at (ngày ICT) TRƯỚC price_date: **0** (>0 = giá điền trước ngày giá — lỗi PIT).
- ⚠️ r dùng center ENTRY CUỐI: center có thể đã hiệu chỉnh sau phản biện/sau khi giá đã di chuyển (recorded_at trễ dd_date tới vài ngày; vd entry rev>1 ghi sau BCTC). Phiên vào neo theo recorded_at nên KHÔNG nhìn trước giá sau recorded_at, nhưng center cuối có thể phản ánh thông tin hiệu đính sau dd_date. 1 entry thiếu center, 0 entry thiếu recorded_at (dùng dd_date làm neo, cờ `recorded_at_missing`).
- ⚠️ Close hồi tố vintage hôm nay: lợi suất mỗi kỳ không bị double-count (một lần Close/Close), nhưng sự kiện cổ tức/tách chưa đối soát broker (§21).

## Tái lập
`python3 mike/bin/dd_forward_outcome.py` (đọc ledger live + BQ read-only). Selfcheck: `python3 mike/bin/dd_forward_outcome_selfcheck.py`.
