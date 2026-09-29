# aria-F2 — ZaloPay: vốn đầu kỳ + "+34,33tr ngày 07-10" (job Taylor_20260913_064536, 2026-09-13)

## c) +34,3tr ngày 07-10 — ĐÃ GIẢI THÍCH, KHÔNG phải nộp tiền
**Là 1 lệnh bán thật bot không thấy**: ZaloPay 10/07 bán VHC 600cp @57.500 = **34.500.000đ** (100+500cp) có trong
email khớp lệnh DNSE (msg 19f4b4977cc2786e) VÀ sao kê tiền T07 (11 dòng "Bán … VHC ngày 10/07" cộng 1.800cp), nhưng
dnse_raw + journal chỉ ghi 1.200cp. Bằng chứng không phải dòng tiền ngoài:
- Sao kê tiền T07 ZaloPay (chuỗi số dư khớp 369/369 dòng): **0 lệnh nộp/rút tiền cả tháng**. Dòng ngoài giao dịch duy nhất:
  "Chuyen tien TT Cho vay" −147.438.711 (17/07) ↔ "Hoàn trả TT Cho vay" +147.438.711 + lãi 72.710 (21/07) = Trứng vàng (đã có ở offbook).
- Replay totalCash API 06/07→13/07 theo fill EMAIL (T+0, trừ phí+thuế; `cash_replay.py`): lệch mỗi ngày −880đ..−74.000đ (phí UTTB/CKCK), gồm 10/07
  ⇒ totalCash của API ĐÃ có 34,5tr tiền bán; chỉ feed orders (dnse_raw) thiếu lệnh ⇒ reconcile cũ thấy "tiền thừa" không có fill.
- Tháng 06: 26/06 chuyển 1 tỷ ZaloPay→SpaceX (trước go-live) — không ảnh hưởng kỳ reconcile.
⇒ KHÔNG ghi "external cash flow UNVERIFIED". Fill thiếu được nạp vào `missing_fills_broker_confirmed`.
Việc treo cho Mafee/Winston: vì sao dnse_raw/journal 10/07 thiếu 1 order VHC (không ảnh hưởng tiền; ảnh hưởng mọi tính P&L từ raw).

## a+b) Vốn đầu kỳ — `data/account_seed_capital.json` (gitignored; bản sao ở thư mục này)
NAV 06/07/2026 = totalCash 4.919.567 − nợ 0 + MTM 982.946.000 = **987.865.567đ**
(balances+positions `dnse_raw_2026-07-06.jsonl` ts 21:45:43 lọc 0001743768; giá BQ `ticker.Price` 06/07 = DNSE marketPrice 7/7 mã).
| mã | KL | giá 06/07 | MTM |
|---|---|---|---|
| DGC | 10.000 | 46.250 | 462.500.000 |
| VPB | 7.500 | 27.450 | 205.875.000 |
| VIB | 9.200 | 16.100 | 148.120.000 |
| VHC | 1.800 | 57.600 | 103.680.000 |
| TCM | 2.310 | 20.100 | 46.431.000 |
| TLG | 200 | 49.000 | 9.800.000 |
| MSH | 200 | 32.700 | 6.540.000 |
**Giả định**: legacy không có giá vốn mua trước bot ⇒ giá vốn = MTM 06/07; realized/unrealized legacy đo từ go-live, không phải từ lúc user mua.
`reconcile_equity.py` không truyền `--starting-capital` ⇒ đọc file: nạp lô legacy trước replay fill, cộng legacy snapshot đã loại (DGC, VPB) vào
unrealized + MTM theo KL/giá broker ngày asof, kiểm KL replay = broker. Truyền `--starting-capital` ⇒ bỏ qua file (SpaceX y nguyên).

## d) Reconcile ZaloPay (snapshot aria-A1, offbook như A1)
| | residual trước (1B placeholder) | sau (seed) | dư sau diễn giải |
|---|---|---|---|
| 08-28 | +526,93tr (108,47%) | **+1,726tr (0,181%) ✅ KHỚP** | +0,300tr (0,032%) |
| 09-11 | +526,78tr (94,39%) | **+1,576tr (0,161%) ✅ KHỚP** | +0,149tr (0,015%) |
KL replay = broker cho DGC 10.000 / VPB 1.300 (không cảnh báo). Phần dư ~0,15–0,30tr là ước tính, khớp bậc với chi phí thật chưa mô hình:
phí UTTB (~0,2tr riêng T7), phí CKCK, phí lưu ký (~6k/tháng), trừ lãi tiền gửi + lãi Trứng vàng 72.710; phí UPCOM thấp hơn hằng số HOSE.
Không cần ép về 0.
