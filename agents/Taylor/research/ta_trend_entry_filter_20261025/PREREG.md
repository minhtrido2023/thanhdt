# PREREG — Cờ xu hướng (A2/F3/F2) có lọc được chất lượng lệnh vào LAG/BAL? (Giai đoạn 1, PAPER-ONLY)
Job `Taylor_20261025_121521` · viết 2026-10-25 TRƯỚC khi tính bất kỳ con số so sánh nào. Không sửa sau khi chạy;
mọi thay đổi ghi thành mục "Sửa đổi công khai" kèm lý do.
Read-only: không đổi engine/filter/trading_rules/production, không ghi pin registry, không replay NAV.

## 1. Dữ liệu
- Sổ lệnh: ledger ghim **R3-park0-pin0pct-SAN**, `data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz`
  (md5 nội dung giải nén **537e349b5589408c994f8aceafeb9a39**, PINS.jsonl; registry mục "2026-10-08 — R3 ĐO Ở KNOB LIVE park=0").
  Kỳ 2014-01-02 → 2026-06-19. Chọn chân pin0% (sàn) — chân pin1M chỉ khác lãi tiền nhàn rỗi, không đổi lệnh cổ phiếu (kiểm: so tập holding_id 2 ledger, ghi vào REPORT).
- Giá để tính cờ: `data/bq_cache_asof20260729_postrestate/ticker/*.parquet` (ĐÚNG vintage engine dùng cho ledger), giá điều chỉnh `Open/High/Low/Close`, `Volume` thô.
  Không dùng `ticker_prune`. Không cần lọc universe cho cờ (vị thế là của chính book; universe đã do engine áp).

## 2. Đơn vị = vị thế (holding)
- Gộp mọi dòng `TX` theo `holding_id` (nhiều lần khớp chia nhiều phiên = 1 vị thế). Chỉ book `LAG`, `BAL`, mọi `play_type` của book.
- `entry_date` = ngày khớp mua ĐẦU TIÊN; `signal_date` = phiên giao dịch liền trước `entry_date` theo lịch VNINDEX.
- Loại: vị thế không có lệnh bán hoặc thoát bằng `MTM_UNREALIZED` (chưa đóng).
- **Nhánh CHÍNH loại vị thế có dòng `ABANDONED_REFUND`** (khớp dở rồi hoàn tiền — không chạy tới thoát thật của book;
  cùng quy ước D1 của `ccs_phase1`). **Nhánh độ nhạy** gộp cả chúng; kết luận đổi dấu giữa 2 nhánh = ô không sống.

## 3. Metric (2 metric, metric 1 là tiêu chí)
1. `ret` = lợi suất ròng/vị thế tới thoát thật = (Σsell_amount − Σfee_sell) / (Σbuy_amount + Σfee_buy) − 1.
2. `contrib` = P&L VND của vị thế / NAV book tại entry_date (`nav_lag_ref` hoặc `nav_bal_ref`, dòng DAILY), đơn vị bp. Mô tả + cùng kiểm định, KHÔNG là tiêu chí đạt.

## 4. Ba cờ (tính tại signal_date, chỉ dùng dữ liệu ≤ signal_date — PIT)
Cờ là TRẠNG THÁI (không phải sự kiện cắt đúng ngày — sự kiện trùng ngày quá hiếm để làm bộ lọc); công thức trích nguyên từ `ta_schools_vn_20261025/engine.py`:
- **A2** = Tenkan(9) > Kijun(26) VÀ Close > đỉnh mây max(SSA,SSB) (dịch 26) — trạng thái nền của tín hiệu A2.
- **F3** = có ít nhất 1 sự kiện F3 (Close > max Close 252 phiên trước VÀ Volume/MA20(Volume, trễ 1) > 1,5) trong 20 phiên giao dịch của mã kết thúc tại signal_date.
- **F2** = Close > MA50 VÀ MA50 > MA50 10 phiên trước (= `f2state` của engine).
- Thiếu lịch sử (NaN) ⇒ cờ TẮT (ghi số ca vào REPORT). Mã không có dòng giá đúng signal_date ⇒ dùng phiên gần nhất ≤ signal_date của mã.

## 5. So sánh & thống kê
- 6 so sánh = {A2,F3,F2} × {LAG,BAL}. d = mean(ret | BẬT) − mean(ret | TẮT).
- Bootstrap cụm theo **tháng của entry_date** (B=5000, seed 20261025, resample tháng có hoàn lại, tính lại d); p hai phía = 2·min(P(d*≤0), P(d*≥0)), sàn 1/B.
- BH-FDR trên đúng 6 p của nhánh chính.
- IS = entry ≤ 2019, OOS = 2020+.
- Khai báo mỗi ô: N vị thế BẬT/TẮT, N tháng độc lập (số tháng có ≥1 vị thế) BẬT/TẮT. Ô có N BẬT hoặc N TẮT < 100 ⇒ "thiếu mẫu" (không được đạt).

## 6. Tiêu chí ĐẠT (phải đủ cả)
(a) d_IS > 0 và d_OOS > 0 (cùng dấu dương); (b) q_BH < 0,10; (c) d toàn kỳ ≥ +1,0pp/vị thế;
(d) phần lệnh bị loại (= tỉ lệ TẮT) ≤ 40%; (e) không đổi dấu ở nhánh độ nhạy (gồm ABANDONED).
Nếu (a)-(c) đạt nhưng (d) hỏng ⇒ "hiệu có nhưng lọc quá nhiều — chi phí cơ hội vốn nhàn rỗi chưa xét", KHÔNG đạt.
Ô ĐẠT ⇒ chỉ ghi "đủ điều kiện mở giai đoạn 2 (replay NAV engine, cần user duyệt + quant-skeptic)". Không đề xuất wire.
Đa số không đạt ⇒ kết luận "không có tác dụng lọc" (kết quả hợp lệ).

## 7. Tự kiểm
- Đối soát tổng: Σ P&L mọi vị thế (gồm cả ABANDONED + MTM) theo book so với chênh tiền mặt từ TX (tự nhất quán trong ledger) — sai lệch phải ≈0 VND.
- Kiểm tay 1 vị thế chia nhiều lần khớp (vd AAM_20160722_504) và cờ của 1 mã trên 1 ngày bằng tính tay độc lập.
- Chạy 2 lần, chạy dưới `env -u TZ`: kết quả byte-identical.
