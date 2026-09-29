# PREREG — Idle-pool redeploy sau khi park 0.80 → 0.30
Job `Taylor_20260927_085628` · viết 2026-09-27 ~16:0x ICT · **TRƯỚC khi đọc bất kỳ số mới nào**
(số DUY NHẤT đã biết khi viết file này = lưới park fraction vòng 1/2 đã pin hôm nay:
bootstrap 5th-pct MaxDD park=0.80 −32,0% vs park=0 −24,0%; đuôi CAGR 14,9–15,8% phẳng trên lưới).

## 0. Câu hỏi
User chốt 15:48 ICT 27/09 hạ park fraction 0.80 → 0.30. Việc đó giải phóng ~17,6pp NAV
(park share NAV 28,1% → 10,5%). Câu hỏi: **phần vốn đó nên ở đâu?**

## 1. Sai đã biết phải tránh (ràng buộc thiết kế, không phải lời khuyên)
Quyết định 0.80 ban đầu sai vì **đo tuần tự từng knob** (park fraction tối ưu hoá riêng, không
đo chung với các knob khác). Vì vậy:
- **R1.** Mọi ứng viên phải chấm trên CÙNG tiêu chí đã dùng để hạ park: bootstrap 5th-pct MaxDD
  **và** E[Calmar] **paired** (cùng resample, cùng block), KHÔNG phải mean CAGR.
- **R2.** Ứng viên equity phải đo **ĐỒNG THỜI với mức park** (grid 2 chiều park × sleeve), không
  đo "thêm sleeve vào cấu hình park=0.30 đã cố định".
- **R3.** Lý do hạ park là ĐUÔI DD. Nếu một ứng viên làm 5th-pct MaxDD **xấu hơn park=0.80
  (−32,0%)** thì nó tự động FAIL — dù CAGR trung vị cao hơn.

## 2. Ba ứng viên, khai trước
- **(a) Tiền + carry egg** — baseline. Backtest giả định 0%/năm; LIVE có lãi "Trứng vàng".
  Baseline ĐÚNG = 0% + carry đo được, không phải 0%.
- **(b) Tăng lại park custom30V** — đã có lưới, chỉ TRÍCH số, không chạy lại engine.
- **(c1) Sleeve TẬP TRUNG** (discretionary/AlphaLens, 4–6 tên, trần ≤5% NAV/tên, ≤10% NAV sleeve).
- **(c2) Rổ DIỆN RỘNG** (≥20 tên, có name cap) thay thế/bổ sung custom30V.

## 3. Cam kết đo — tiêu chí PASS khai TRƯỚC
| # | Đo gì | Nguồn | PASS nếu |
|---|---|---|---|
| M1 | Carry egg %/năm THỰC NHẬN | `data/execution_logs/dnse_raw_*.jsonl`, field egg/depositInterest/depositFee, 2 TK, 01/07→27/09 | tính được từ ≥2 mốc egg.totalValue cách nhau ≥14 ngày **và** không bị nhiễu bởi nạp/rút trong kỳ; nếu có nạp/rút không tách được ⇒ báo "không đo được", KHÔNG suy từ biểu lãi công bố |
| M2 | Δ CAGR LIVE-vs-backtest do carry | M1 × 17,6pp NAV | chỉ báo khi M1 PASS |
| M3 | AlphaLens N ĐÚNG NGHĨA | artifact/registry của DollarBill | N = số **sự kiện độc lập** (vào/ra vị thế), KHÔNG phải số phiên. N<20 ⇒ tuyên bố THẲNG "không đủ để quyết sizing" bất kể lợi suất |
| M4 | Đuôi DD c1 vs c2 vs custom30V cùng exposure | ledger hiện có | nếu ledger KHÔNG chứa daily return của sleeve ứng viên ⇒ nói rõ **cần job engine riêng**, KHÔNG ước lượng bằng vol/corr giả định |

## 4. Trần cứng khai trước
`kb/projects/discretionary-margin-policy-20260823.md`: sleeve discretionary ≤10% NAV.
⇒ c1 hấp thụ tối đa ~10pp / 17,6pp. **Phần dư ≥7,6pp phải được quy về một ứng viên tường minh**
(a hoặc b hoặc c2), không để trống.

## 5. Điều KHÔNG làm
- KHÔNG đổi `data/trading_rules.json`, KHÔNG wire, KHÔNG đặt lệnh. PAPER-ONLY.
- KHÔNG chạy lại engine park grid (tái dùng CSV đã pin) — engine A/B cho sleeve mới chỉ ĐỀ XUẤT.
- KHÔNG kết luận "nên làm sleeve" nếu M4 không có số.
