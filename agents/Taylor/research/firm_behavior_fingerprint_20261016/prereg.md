# Pre-registration — firm behavior fingerprint GĐ0 (job Taylor_20261015_173117)

Viết 2026-10-16 ~00:50 ICT, SAU khi dựng bảng đặc trưng (`build_events.py`) và kiểm sanity căn
ngày, TRƯỚC khi tính bất kỳ IC/forward-return nào. Chỉ các con số mô tả (describe) đã được nhìn.

## Pre-flight (Step 0, `mike/bin/rnd_preflight_power.py`)
Per-event, obs/năm=4 (đợt công bố), N=50 đợt, n-trials=16, trần 12,5 năm:
- giả định spread quintile 100bps/đợt, sd 400bps → **NO-GO** (DSR tối đa 0,487)
- giả định 50bps → NO-GO (DSR 0,183)
- Sharpe năm tối thiểu phát hiện được: **1,008** ≈ t_đợt ≥ 3,5.
⇒ User đã duyệt GĐ0 như ĐO LƯỜNG. Ngưỡng GO khai trước bên dưới được đặt NGANG với yêu cầu này.

## Đơn vị N
1 quan sát độc lập = 1 **đợt công bố** (quý tài chính, ~50 đợt), KHÔNG phải 17.739 dòng sự kiện.
IC tính trong từng đợt (cross-section), thống kê t trên chuỗi IC theo đợt. Bổ sung block-bootstrap
theo ticker (B=1000) cho IC gộp — báo CẢ HAI.

## Mục tiêu đo
`fwdx_1m`, `fwdx_3m` = lợi nhuận vượt VNINDEX từ close t0+1 tới +21/+63 phiên.
Trực giao hoá: trong từng đợt, rank đặc trưng → phần dư sau hồi quy lên dummy rating 8L PIT (1..5,
as-of t0+1). Dòng thiếu rating bị loại khỏi phép trực giao.

## Dấu kỳ vọng (khoá trước)
| Đặc trưng | Dấu IC kỳ vọng | Lý do |
|---|---|---|
| lag_dev (trễ hơn thói quen của chính mã) | − | tin xấu bị trì hoãn |
| monday (proxy công bố cuối tuần) | − | chôn tin xấu ngoài giờ |
| late30 | − | như trên |
| near_deadline | − | như trên |
| car_m1p1 | + | PEAD |
| car_m5m1 | ? (hai phía) | rò rỉ vs momentum ngắn |
| leak_ratio | − | tin đã vào giá trước ⇒ ít drift, dấu hiệu bất cân xứng thông tin |
| vol_ratio (log) | + | high-volume return premium |
| amihud_log | + | phần bù kém thanh khoản |
| idio_vol60 | − | IVOL puzzle |
| limit_freq60 | − | lottery / đầu cơ |
| ins_netbuy_adv | + | insider mua ròng |
| ins_breadth | + | như trên |
| accr_q | − | Sloan |
| fp_* (dấu vân tay EB của chính mã) | ? (hai phía) | khám phá |

## Tiêu chí phán (mỗi đặc trưng × horizon)
- **GO**: |t_đợt toàn mẫu| ≥ 3,0 (HLZ) **và** OOS (2020+) cùng dấu với IS và |t_OOS| ≥ 2 **và**
  LOYO không đổi dấu **và** CI 95% bootstrap ticker không chứa 0 **và** dấu khớp kỳ vọng (nếu có).
- **INCONCLUSIVE**: 2 ≤ |t| < 3 với OOS cùng dấu, hoặc GO cơ học nhưng sai dấu kỳ vọng.
- **NO-GO**: còn lại.
Composite: chọn đặc trưng IS (2014-19) |t_IS| ≥ 2, dấu theo IS, trọng số bằng nhau; chấm OOS duy
nhất một lần. Nếu composite đạt GO ⇒ bắt buộc DSR/PBO trước khi đề xuất bất kỳ điều gì.

## Dữ liệu không có (khai trước)
- "Loại cổ đông": không có nguồn PIT; chỉ có dict tay 13 mã SOE (`soe_governance_screen.py`) ⇒
  EB chỉ kéo về trung bình **ngành ICB cấp 1**.
- Cuối tuần: Release_Date không bao giờ rơi T7/CN (vendor dồn sang thứ Hai: 5.777 sự kiện thứ Hai vs
  ~3.100 các ngày khác) ⇒ chỉ có proxy `monday` (≈ một nửa là công bố cuối tuần thật).
- Beneish: thiếu khấu hao, SG&A, AR kỳ trước ⇒ không tính được; chỉ Sloan accrual quý.
- Trần biên độ: không có cột sàn giao dịch ⇒ proxy |ret| ≥ 6,5%.
