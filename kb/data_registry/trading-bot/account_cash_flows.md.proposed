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
deposit/withdraw. `date` sau hôm nay (giờ ICT) ⇒ bị từ chối (bắt gõ nhầm ngày); `amount_vnd` phải là số
hữu hạn (NaN/Infinity ⇒ bị từ chối). Schema đầy đủ + kiểm lỗi: `mike/bin/account_cash_flows.py`.
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
  chối. Chụp lại NAV ngày đó (`daily_nav_snapshot.py --date <ngày> --from-raw`) CHỈ làm được khi
  `dnse_raw_<ngày>.jsonl` có bản ghi balances sau giờ đóng cửa; **2026-08-24 không có** (mỗi TK đúng một
  bản ghi balances, lúc 04:49/04:50) ⇒ với các dòng đó chưa có lối ra, đường đính chính thuộc bước 3 của
  chính sách. Dòng của ngày KHÔNG có phiên (cuối tuần/nghỉ lễ) chụp giờ nào cũng là giá chốt phiên trước —
  không bị coi là chụp trước đóng cửa. Ví dụ đo: phiên +10%, nạp 22% NAV
  tối hôm đó mà nhận theo NAV chụp trước phiên thì tỉ suất ra +8,197% thay vì +10,0%, vĩnh viễn
  (`nav_unit_ledger_selfcheck.py` B8b).
- **nav_history THIẾU dòng của một phiên ⇒ tiền vào/ra từ giờ đóng cửa phiên đó trở đi bị từ chối** (nêu
  tên phiên thiếu) cho tới khi backfill dòng đó (`--from-raw`, cùng điều kiện balances ở trên). Không chặn
  thì dòng cho giá lùi về phiên trước nữa và giá chốt thiếu trọn biến động của phiên thiếu (đo: +8,197%
  thay vì +10,0%, không lỗi — `nav_unit_ledger_selfcheck.py` B13). Thật: cả hai TK thiếu dòng 2026-08-06
  (`dnse_raw_2026-08-06.jsonl` có balances tới 19:10, chưa backfill). Tiền vào TRONG chính phiên thiếu
  dòng vẫn được nhận (giá chốt phiên trước, đúng luật). "Phiên" = thứ Hai–Sáu không thuộc
  `trading_bot.vn_market.is_holiday` ⇒ **ngày nghỉ lễ chưa khai ở đó sẽ bị coi là phiên thiếu dòng**
  (từ chối oan, không sai số) — khai lịch nghỉ trước.
- **Luật gán so với `balance_ts` — kể cả `balance_ts` QUY ƯỚC của dòng ĐÃ ĐÍNH CHÍNH có thể là QUY ƯỚC, không phải giờ chụp thật** (từ 2026-10-14,
  nhánh feat/fund-history-lock-20261014). Dòng SpaceX 2026-07-02 sau đính chính mang
  `balance_ts = 2026-07-02T14:45:00` = "số dư TẠI GIỜ ĐÓNG CỬA" dựng lại (số dư chụp 09:46:35 trừ lệnh
  126631 bị khoá tiền sau lần chụp), KHÔNG phải lúc có bản ghi balances nào. 14:45:00 trùng đúng biên đóng
  cửa — cổng "chụp trước đóng cửa" của `nav_unit_ledger.py` so chặt `<` nên dòng này qua cổng KHÔNG cần
  `--accept-preclose`; đó là CHỦ ĐÍCH (giá trị dòng đã là số dư giờ đóng cửa), bằng chứng nằm ở
  `nav_history_corrections.jsonl` + file đính chính
  (`agents/Taylor/research/fund_history_lock_20261014/corrections/correction_SpaceX_AB.json`). Nhận
  diện: `nav_source` bắt đầu bằng `dinh chinh` và ngày có bản ghi trong nhật ký đính chính. Với luật gán: tiền vào/ra SAU 14:45:00 ngày 07-02 được gán cho dòng
  kế tiếp, đúng như khi dòng chụp sau đóng cửa thật. Đừng dùng
  `balance_ts` của dòng như vậy để suy "lúc đó bot đang chạy" hay để ghép với bản ghi dnse_raw cùng giờ.
- `balance_ts` phải tăng NGHIÊM NGẶT theo ngày của dòng (từ dòng liền trước dòng tiền đầu tiên trở đi);
  không thì bị từ chối — dòng sửa tay bằng số dư chụp muộn hơn dòng sau từng cho giá sai im lặng.
- `time_ict` trùng PHÚT với `balance_ts` của dòng đang xét mà không có giây ⇒ bị từ chối (khai `HH:MM:SS`).
- `timing` là tuỳ chọn: có khai mà khác kết quả suy ra ⇒ bị từ chối, thông điệp nêu cả hai.
- `market_only` gán theo NGÀY (dòng nav_history đầu tiên có ngày >= `date`), không có `timing`.
- Vốn khởi điểm KHÔNG ghi ở đây (nó ở [`account_inception.md`](account_inception.md)); bản ghi có ngày
  <= ngày khởi điểm bị loại và hiện ở `dropped_flows`.
- File rỗng nghĩa là "chưa ai GHI", không phải "chưa có nạp/rút" — khoản nhỏ hơn ~5% NAV lọt cả hai cổng.
