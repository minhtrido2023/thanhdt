# PREREG — Chỉ báo fundamental phân biệt lệnh vào tốt/xấu trong LAG và BAL (Giai đoạn 1, PAPER-ONLY)
Job `Taylor_20261025_123115` · viết 2026-10-25 TRƯỚC khi tính bất kỳ con số so sánh nào. Không sửa sau khi chạy;
mọi thay đổi ghi thành mục "Sửa đổi công khai" kèm lý do. Read-only: không đổi engine/filter/trading_rules/production,
không ghi pin registry, không replay NAV, không đề xuất wire.

## 0. Không lặp NO-GO đã đóng
| Đã thử | Kết luận cũ | Lần này |
|---|---|---|
| LAG SUE-tilt 3 tầng | NO-GO (−0,66pp, sizing theo SUE) | KHÔNG đo SUE lại. Chỉ đo tăng trưởng LN quý YoY + gia tốc như biến mô tả TRONG nhóm đã chọn (khác: không phải tilt sizing, là câu hỏi phân biệt cấp lệnh). Không có SUE PIT sạch trong cache cùng vintage ⇒ SUE "không đo". |
| Stability floor ROE_Min<0 | NO-GO (−0,45pp, cổng loại) | Không dùng ROE_Min. Dùng ROE_Trailing (mức) và ΔROA (thay đổi) — trục khác (mức hiện tại/động lượng chất lượng, không phải sàn 3 năm). |
| gq_score growth gate | −IC | Không dùng gq_score. Tăng trưởng doanh thu/LN đơn lẻ vẫn đo (họ (d)), ghi rõ khả năng trùng NO-GO này. |
| liq-tilt custom30 | REFUTED (custom30, không phải LAG/BAL) | ADV đo như biến mô tả cấp lệnh LAG/BAL; khác book. |
| composite v3 as entry-selector | NO | Không đo composite. 1/PE đo như BIẾN KIỂM SOÁT (factor trội), không phải ứng viên mới. |
| 8L rating | cổng nhị phân ≤3 | Không đo rating. |
| Cổ tức: sleeve payer thay cash (10-09) | không mở sleeve | Câu hỏi khác (sleeve vs cash). Ở đây: payout có phân biệt lệnh trong book không. |
| Cờ xu hướng A2/F3/F2 (10-25) | 0/6 | Không đo kỹ thuật. |

## 1. Dữ liệu
- Đơn vị = vị thế (holding_id), tái dùng NGUYÊN `../ta_trend_entry_filter_20261025/positions.csv` (ledger R3-park0-pin0pct-SAN md5
  `537e349b5589408c994f8aceafeb9a39`) và `positions_pin1M.csv` (md5 `a6ba34d83a4d374a73293d897c0b43d9`). Nhánh chính: loại
  ABANDONED_REFUND, MTM_UNREALIZED, không có lệnh bán. Kết quả `ret` = lợi suất ròng tới thoát thật. Tự kiểm lại ΣP&L = TX.
- `signal_date` = phiên liền trước entry (đã có trong positions.csv).
- Fundamental: `data/bq_cache_asof20260729_postrestate/ticker_financial.parquet` (cùng vintage engine). **PIT**: ngày hiệu lực
  của dòng quý = `max(time, Release_Date)`; thiếu Release_Date (11% dòng) ⇒ `time + 11 ngày` (11 = độ trễ Release−time lớn nhất
  quan sát được trong bảng; bảo thủ). Lấy dòng có ngày hiệu lực lớn nhất ≤ signal_date (merge_asof theo mã).
  Dòng của 4 quý trước (cho Δ cổ tức) = dòng hiệu lực có `quarter` lùi 4 quý, cũng phải hiệu lực ≤ signal_date.
- Giá/định giá tại signal_date: `.../ticker/*.parquet` (PE/PB/PCF/EVEB trên `Price` thô — registry `valuation_pe_pb_pcf_ps.md` (4)(6),
  KHÔNG nhân Price/Close). Dùng phiên gần nhất ≤ signal_date của mã.
- Ngành: `ICB_Code` (4 chữ số) tại signal_date. Nhóm đồng nhất G: BANK = 83xx · FINO (chứng khoán/bảo hiểm/DV tài chính) = 85xx,87xx ·
  RE (BĐS) = 86xx · NONFIN = còn lại. Thiếu ICB ⇒ NONFIN? KHÔNG — thiếu ⇒ loại khỏi chỉ báo phụ thuộc ngành (ghi số ca).
- `universe_pit` không cần: vị thế là của chính engine (universe đã áp). Không dùng `ticker_prune`. `profit_*` KHÔNG đọc.

## 2. Chỉ báo CỐ ĐỊNH (25) — hướng kỳ vọng khai TRƯỚC; "+" = giá trị cao ⇒ ret cao
Ký hiệu: NP_ttm = ΣNP_P0..P3; Rev_ttm = ΣRevenue_P0..P3; CFO_ttm = ΣCF_OA_P0..P3 (VND thô). Phạm vi: ALL = mọi ngành (xếp hạng trong G);
NF = chỉ NONFIN (loại BANK/FINO/RE — PCF/CFO/nợ/tồn kho không so được với tài chính, BĐS tồn kho là sản phẩm).
| # | Tên | Công thức PIT | Phạm vi | Hướng | Giả thuyết kinh tế |
|---|---|---|---|---|---|
| a1 | payout1Y | Dividend_1Y·OShares / NP_ttm (NP_ttm>0) | ALL | + | Chi trả tiền mặt = LN thật, kỷ luật vốn; payer ít bị "kế toán đẹp" |
| a2 | payout3Y | (Dividend_3Y/3)·OShares / (ΣNP_P0..P7/2) (mẫu >0) | ALL | + | như a1, mượt hơn (chỉ có 8 quý NP ⇒ mẫu = TB năm của 2 năm) |
| a3 | DY | Dividend_1Y / Price(signal) | ALL | + | yield cao = rẻ + tiền mặt |
| a4 | div3y | Dividend_Min3Y > 0 (nhị phân: trả đều 3 năm) | ALL | + | chính sách cổ tức ổn định (cột ≈ "số năm liên tục"; không có chuỗi năm dài hơn) |
| a5 | div_chg | Dividend_1Y / Dividend_1Y(4 quý trước) − 1 (mẫu>0) | ALL | + | tăng cổ tức = tín hiệu tự tin của ban lãnh đạo |
| b1 | cfo_np | CFO_ttm / NP_ttm (NP_ttm>0) | NF | + | LN có tiền thật đi kèm ⇒ drift bền |
| b2 | accrual | (NP_ttm − CFO_ttm) / totalAsset_P0 | NF | − | Sloan: dồn tích cao ⇒ LN đảo chiều |
| b3 | gpm | GPM_P0 | NF | + | biên gộp cao = quyền định giá |
| b4 | d_gpm | GPM_P0 − GPM_P4 | NF | + | biên mở rộng ⇒ LN bất ngờ kéo dài |
| b5 | roe | ROE_Trailing | ALL | + | chất lượng/khả năng sinh lời |
| b6 | d_roa | ROA_P0 − ROA_P4 | ALL | + | cải thiện hiệu quả |
| c1 | de | Debt_Eq_P0 | NF | − | đòn bẩy cao ⇒ rủi ro |
| c2 | nd_ebitda | (StDebt_P0+LtDebt_P0−Cash_P0)/(4·EBITDA_P0) (EBITDA>0) | NF | − | khả năng trả nợ (IntCov LOẠI: hộp đen vendor, registry ticker_financial.md) |
| c3 | inv_rev | Inventory_P0 / Rev_ttm | NF | − | tồn kho phình ⇒ cầu yếu/rủi ro giảm giá |
| c4 | ar_rev | AR_P0 / Rev_ttm | NF | − | phải thu phình ⇒ LN chất lượng thấp |
| d1 | rev_yoy | Revenue_YoY_P0 | ALL | + | tăng trưởng doanh thu |
| d2 | np_yoy | NP_P0/NP_P4 − 1 (NP_P4>0) | ALL | + | bất ngờ LN lớn ⇒ drift (TRONG nhóm đã chọn) |
| d3 | np_accel | (NP_P0/NP_P4) − (NP_P1/NP_P5) (mẫu>0) | ALL | + | gia tốc LN |
| e1 | ey | 1/PE (PE≤0 ⇒ 0) tại signal | ALL | + | factor trội (kiểm soát) |
| e2 | by | 1/PB (PB≤0 ⇒ 0) | ALL | + | rẻ theo sổ sách |
| e3 | cfy | 1/PCF (PCF≤0 ⇒ 0) | NF | + | rẻ theo dòng tiền |
| e4 | ebitda_y | 1/EVEB (EVEB≤0 ⇒ 0) | NF | + | rẻ theo EV |
| e5 | adv | log(Volume_3M_P50 · Price) tại signal (cơ sở Price, registry (7)) | ALL | − | phần bù kém thanh khoản / ít bị phân tích |
| f1 | gap | số phiên (lịch VNINDEX) từ ngày hiệu lực BCTC mới nhất tới entry | ALL | − | vào càng sớm sau công bố càng ăn drift |
| f2 | react | Close(phiên hiệu lực+1)/Close(phiên trước hiệu lực)−1, chỉ khi phiên+1 ≤ signal | ALL | + | phản ứng giá công bố tốt ⇒ drift tiếp (PEAD) |

**Không đo / chỉ mô tả**: vốn hoá (OShares TRAP — `ticker_financial_oshares.md`; a1/a2 cũng dùng OShares nhưng cùng kỳ với NP nên
tỉ lệ không phụ thuộc mốc OShares nếu cổ tức/sh cùng cơ sở — ghi caveat); free-float/room ngoại (không có cột); SUE (xem §0);
IntCov (hộp đen). Mùa vụ quý (Q của BCTC) và state DT5G engine (`state` dòng DAILY ledger tại signal_date) — CHỈ MÔ TẢ, ngoài họ kiểm định.
Breadth-tercile PIT — "không đo trong job này" (cần query universe_pit; chỉ là biến mô tả).

## 3. Phương pháp (mỗi chỉ báo × mỗi book)
- Xếp hạng phân vị TRONG (book × G) (chỉ báo NF chỉ có G=NONFIN), gộp lại, chia tertile T1/T2/T3 theo phân vị (≤1/3, ≤2/3, >2/3).
  Nhị phân (a4): T3 = có, T1 = không. NaN ⇒ loại khỏi chỉ báo đó (ghi coverage).
- Đo 1 (tertile): d = mean(ret|T3) − mean(ret|T1). Đo 2: Spearman ρ(phân vị, ret).
- p: bootstrap CỤM theo tháng entry, B=5000, seed 20261025, hai phía 2·min(P≤0,P≥0), sàn 1/B.
- **BH-FDR trên TOÀN họ: 25 chỉ báo × 2 book × 2 đo = 100 p** (khai N trial = 100).
- IS = entry ≤2019, OOS = 2020+. Leave-one-year-out: d khi bỏ từng năm (báo min/max + năm gánh nhất). Cắt 2% lệnh lãi lớn nhất của book.
- Ô: khai N vị thế có giá trị và N tháng; N<100 ⇒ "thiếu mẫu" (không được đạt).
- Kiểm soát value: OLS ret ~ phân vị(x) + phân vị(ey) (trong book), hệ số x và p bootstrap cụm tháng — MÔ TẢ "độc lập khỏi 1/PE".
- Tương quan Spearman giữa các chỉ báo đạt (trong book) — tránh đếm trùng.

## 4. Tiêu chí "ĐÁNG XÉT TIẾP" (phải đủ cả)
(a) sign(d) = hướng khai trước và |d| ≥ 2pp/vị thế; (b) d_IS và d_OOS cùng dấu đúng hướng; (c) q(tertile) < 0,10 và ρ cùng dấu;
(d) không đảo dấu khi bỏ 2021, khi cắt đuôi 2%; (e) cùng dấu đúng hướng, |d| ≥ 2pp trên ledger pin1M; (f) không "thiếu mẫu".
Đạt ⇒ "đủ điều kiện giai đoạn 2 (replay NAV, cần user duyệt + quant-skeptic)". Không đề xuất wire.
Chỉ báo đạt nhưng hệ số mất ý nghĩa khi kiểm soát 1/PE ⇒ ghi "proxy của value".
Báo riêng bảng tertile payout (a1, a2) bất kể đạt hay không.

## 5. Tự kiểm
- ΣP&L vị thế (positions.csv) = Σ(tiền bán ròng − tiền mua gồm phí) từ TX ledger, theo book.
- Tính tay độc lập (Python thuần, đọc parquet thô) 2 chỉ báo (payout1Y, cfo_np) cho 2 vị thế cụ thể ⇒ khớp engine.
- Chạy 2 lần + `env -u TZ`: results byte-identical.
