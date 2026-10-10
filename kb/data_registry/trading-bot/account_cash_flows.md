---
kind: local-file
status: CANONICAL
source: data/account_cash_flows.json
group: trading-bot
role: dòng tiền ngoại sinh (nạp/rút vốn) theo account — đầu vào của sổ đơn vị quỹ và của cổng NAV-jump
writer: "tay (người ghi kèm bằng chứng); mẫu: mike/templates/account_cash_flows.json"
---

# data/account_cash_flows.json

**Status: CANONICAL** — nguồn DUY NHẤT của nạp/rút. DNSE OpenAPI không có sổ nạp/rút (đã quét
`dnse_api.py` + 86 file `dnse_raw_*.jsonl`, 2026-09-27) nên file này do người ghi.

## Là gì
`{"<account>": [{date, time_ict, amount_vnd, kind, evidence, timing?}, ...]}`. Người khai chỉ ghi NGÀY +
GIỜ + SỐ TIỀN (+ bằng chứng). `amount_vnd` dương = nạp, âm = rút. `kind` ∈ deposit | withdraw |
market_only. `time_ict` ("HH:MM" hoặc "HH:MM:SS", giờ ICT lúc tiền thật sự vào/ra) BẮT BUỘC với
deposit/withdraw. Schema đầy đủ + kiểm lỗi: `mike/bin/account_cash_flows.py`.
Đo 2026-10-11: cả SpaceX và ZaloPay đều 0 bản ghi.

## Ai đọc
`nav_unit_ledger.py`, `nav_period_returns.py` (thiếu file ⇒ từ chối), `report_delivery_gate.py` (cổng
bước nhảy NAV 5%), `daily_nav_snapshot.py` (cổng bước nhảy NAV 15%). Cả bốn gán bản ghi vào phiên bằng
MỘT hàm: `account_cash_flows.assign_flow`.

## Luật gán (code tự suy — không còn mặc định `eod`/`bod` nào, đổi 2026-10-11)
Tiền giao dịch ở giá đơn vị chốt GẦN NHẤT TRƯỚC thời điểm tiền vào/ra. R = dòng nav_history đầu tiên có
`balance_ts` >= thời điểm đó (dòng NAV đầu tiên đã chứa khoản tiền). Thời điểm >= giờ đóng cửa phiên R
(14:45, `SESSION_CLOSE_ICT`) ⇒ giá chốt của R (`eod`); ngược lại ⇒ giá chốt của dòng liền trước R (`bod`).
Chưa có R ⇒ TREO, hiện ở `pending_flows` của `nav_period_returns.py`.

## Bẫy
- **Giờ khai sai là sai giá vĩnh viễn.** Luật chỉ đúng khi `date` + `time_ict` là lúc tiền THẬT SỰ có trong
  số dư DNSE (không phải lúc bấm chuyển khoản ở ngân hàng). Chưa ai đối chiếu được độ trễ ngân hàng → DNSE;
  ghi theo sao kê DNSE.
- `balance_ts` thật KHÔNG cố định 19:10: 135 dòng (đo 2026-10-11) có 3 dòng chụp trước giờ đóng cửa
  (SpaceX 07-02 09:46; cả hai TK 08-24 04:49) và 1 dòng chụp sáng hôm sau (ZaloPay 07-27 → 07-28T09:15).
  Luật so với `balance_ts` thật nên ca "sáng hôm sau" vẫn đúng; dòng cần xét mà `balance_ts` thiếu/hỏng ⇒
  bị từ chối. **Dòng chụp TRƯỚC giờ đóng cửa của chính nó không cho được giá chốt**: mọi khoản tiền vào/ra
  từ sau lần chụp đó cho tới lần chụp của dòng kế tiếp (trong phiên đó, tối hôm đó, sáng phiên sau) ⇒ bị từ
  chối — chạy lại `daily_nav_snapshot.py` cho ngày đó (số dư sau đóng cửa). Ví dụ đo: phiên +10%, nạp 22% NAV
  tối hôm đó mà nhận theo NAV chụp trước phiên thì tỉ suất ra +8,197% thay vì +10,0%, vĩnh viễn
  (`nav_unit_ledger_selfcheck.py` B8b).
- `time_ict` trùng PHÚT với `balance_ts` của dòng đang xét mà không có giây ⇒ bị từ chối (khai `HH:MM:SS`).
- `timing` là tuỳ chọn: có khai mà khác kết quả suy ra ⇒ bị từ chối, thông điệp nêu cả hai.
- `market_only` gán theo NGÀY (dòng nav_history đầu tiên có ngày >= `date`), không có `timing`.
- Vốn khởi điểm KHÔNG ghi ở đây (nó ở [`account_inception.md`](account_inception.md)); bản ghi có ngày
  <= ngày khởi điểm bị loại và hiện ở `dropped_flows`.
- File rỗng nghĩa là "chưa ai GHI", không phải "chưa có nạp/rút" — khoản nhỏ hơn ~5% NAV lọt cả hai cổng.
