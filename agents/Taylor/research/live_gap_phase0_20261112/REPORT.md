# GĐ0 — thước đo "so với tiết kiệm" + kiểm kê thực thi (Taylor, job Taylor_20261112_104201, 2026-11-12)
Không đổi production. Mọi artifact trong thư mục này. Chạy lại: `/home/trido/thanhdt/wc_venv/bin/python <script>.py` (thứ tự: hurdle_pit → vs_savings_table → journal_book_attach → extract_fills_v2 → slippage_v2 → fill_vs_open_hybrid).

## 1. Hurdle PIT (`hurdle_pit.py`, `hurdle_pit.csv`)
- Nguồn: `deposit_rate_vn.effective_deposit_events_df()` = max(Big-4 12T online [26 mốc tay đóng băng + data/deposit_rate_vn_events.csv], CCTG [6T 7,5% từ 30/09, 12T 7,4% từ 05/10]). Cột tham chiếu `dep1m_big4_ref` = fiinprox 1T Big-4 (2019-02→2026-09, PIT T+1 tháng) — KHÔNG vào hurdle (khác kỳ hạn: 1,6–4,9% vs 5–7%).
- Quy ước: lãi đơn, act/365, bậc thang theo ngày hiệu lực. Đoạn: 2011→2018 = mốc tay (không có nguồn công bố theo ngày; độ tin cậy thấp, chỉ minh hoạ); 2019→2026-09-29 = Big-4 12T mốc tay; từ 2026-09-30 = max(Big-4, CCTG).
- **Selfcheck**: 7,4% hiện tại KHỚP. **+2,70% KHÔNG khớp kiểu PIT**: 01/07→11/11 (133 ngày) PIT = **2,548%**; 2,70% = 7,4% phẳng × 133/365 (2,696%). Hurdle PIT thấp hơn ~0,15pp vì 91 ngày đầu chỉ 6,8%.
## 2. Bảng vs tiết kiệm (`vs_savings_table.csv/.md`; TWR + VN-Index lấy từ `nav_period_returns.py`, VNI = giá, TR bị gate G5 chặn)
| TK | cửa sổ | live TWR | VNI | hurdle PIT | excess vs hurdle |
|---|---|---|---|---|---|
| SpaceX | 01/07→11/11 | −3,862 | −6,081 | 2,548 | **−6,41pp** |
| ZaloPay (cả TK) | 06/07→11/11 | −7,511 | −5,240 | 2,455 | **−9,97pp** |
| ZaloPay (sleeve bot, không DGC) | 06/07→11/11 | −2,609 | −5,240 | 2,455 | **−5,06pp** |
Theo tháng (SpaceX): T7 −6,16 / T8 +5,03 / T9 −0,41 / T10 −1,89 (hurdle ~0,56–0,61/tháng). Chỉ T8 thắng tiết kiệm. ZaloPay không có mốc 01/07 (inception 06/07) ⇒ cột "01/07→11/11" của ZaloPay = inception. SpaceX không có sleeve bot (sleeve_scope.json không có mục).
## 3. Gắn sổ book (`journal_book_attach.py` → `fills_booked.csv`, `book_summary.csv`, `book_certainty.csv`)
692 FILL (không trùng) từ 07-01. Book trống đúng 118 SpaceX + 75 ZaloPay (schema cũ không cột `book`) → suy: plan_id (id lệnh trong plan cùng ngày) 67 fill, plan_ticker_side 119, ticker_lineage 7 (độ chắc THẤP), 0 UNKNOWN. Bảng deal/notional/P&L theo book: xem `book_summary.csv`. **P&L FIFO là XẤP XỈ** (không điều chỉnh corp-action, chưa đối soát với verify_account_snapshot.py; sell không có lô mua trong cửa sổ — vị thế legacy — bị tách 'unmatched'; lô mua gán book của lệnh mua). Tổng thực hiện FIFO: SpaceX −104,5tr, ZaloPay −32,4tr. PARK chiếm phần lớn lỗ thực hiện (SpaceX −116tr / ZaloPay −37,5tr) — nhạy với T7 −6%.
## 4. Fill-vs-open sau HYBRID (`fill_vs_open_hybrid.py`, `fill_vs_open_stats.csv/json`)
- CONTROL (≤09-25): N=327 (so 326 gốc: +1 lệnh VPB 09-25 nay đã có bar), mean 5,06 (gốc 5,52), sd 94,37 (gốc 94,58) ⇒ tái lập.
- **Không có fill nào 08-26→09-13** (journal xác nhận, kỳ im lặng) ⇒ cửa sổ POST thực tế = 09-14→11-11: 357 order, 95 cụm (phiên×mã), 26 ngày.
- POST mean vs open = **−11,4 bps** (order), notional-weighted −18,4, cụm-mean −0,45 [CI95 −41,7;+19,6]; P(mean>22)=0,019. BUY: n=66/12 cụm, −26,8 (CI95 rộng [−107;+96]); SELL: 291/83 cụm, −7,9 [−37,6;+18,7]. **Không chạm ngưỡng +22bps; cận trên CI95 (+19,6 / notional-wtd +13,4) cũng dưới 22.**
- Cảnh báo diễn giải: dấu âm vs open lẫn drift giá trong ngày (fill muộn) chứ không hẳn alpha thực thi; BUY N độc lập chỉ 12 cụm — không kết luận gì về BUY. Khung 10 phiên cuối (10-30→11-11) mean −99,5 [−177;−5], 11 cụm — nhỏ, lệch có lợi.
## 5. Đề xuất: `PROPOSAL_savings_row.proposed.md`
