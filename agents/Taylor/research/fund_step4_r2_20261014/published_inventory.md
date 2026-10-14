# Kiểm kê ô VN-Index "từ khi bắt đầu" trong báo cáo ĐÃ GỬI (B1 vòng 2, job Taylor_20261014_091148)

MEASURED 2026-10-14 trên `mike/reports/` (cây canonical, chỉ ĐỌC — không sửa báo cáo nào). Mốc đúng theo
user duyệt 16:11 ICT 14/10: **SpaceX = đóng cửa 30/06/2026 (1.860,01)**, **ZaloPay = đóng cửa 06/07/2026**.
Số đúng = chỉ số GIÁ VN-Index (cột `vnindex` của chuỗi `vnindex_tr_daily.csv`, bản sao
`/tmp/tr2_sbx/data/benchmark/`, md5 9688236e…) — các báo cáo cũ đều so với chỉ số GIÁ. Cột "chênh đúng" =
tỉ suất tài khoản ĐÃ CÔNG BỐ trong cùng báo cáo − chỉ số đúng (không tính lại tỉ suất tài khoản; một số báo
cáo trước 27/09 của ZaloPay dùng mốc vốn gốc cũ — việc đó đã đính chính riêng).

Phạm vi quét: 34 file weekly/monthly (`SpaceX_*`, `ZaloPay_*`, `SpaceX_ZaloPay_*`) + 127 daily (daily không
có ô VN-Index "từ khi bắt đầu" — chỉ có "Từ go-live: … VND (…%)" của tài khoản). File `.bak_sent_20261010`
cùng số với bản chính, không liệt kê riêng. Các ô MTD tháng 8 (1.735,78 → 1.832,12) không phải kỳ "từ khi
bắt đầu", ngoài phạm vi.

Mốc mà ô đã công bố thực dùng được XÁC ĐỊNH bằng cách khớp số với 5 mốc ứng viên:

| kết thúc | 30/06 | 01/07 | 03/07 | 06/07 | 07/07 |
|---|---:|---:|---:|---:|---:|
| 31/07 | −6,679 | −7,039 | −6,783 | −5,843 | −6,085 |
| 18/09 | −2,384 | −2,761 | −2,493 | −1,510 | −1,763 |
| 25/09 | −4,027 | −4,397 | −4,134 | −3,167 | −3,416 |
| 30/09 | −4,913 | −5,280 | −5,019 | −4,062 | −4,308 |
| 02/10 | −6,575 | −6,935 | −6,679 | −5,739 | −5,981 |
| 09/10 | −6,716 | −7,076 | −6,820 | −5,881 | −6,123 |

## Cần đính chính (mốc sai)

| # | File (mike/reports/) | Dòng | Ô đã công bố | Mốc thực dùng | Số đúng | Chênh đã công bố → đúng |
|---|---|---|---|---|---|---|
| 1 | `SpaceX_weekly_report_2026-09-14_to_2026-09-18.md` | 80 | VN-Index −2,76% | 01/07 | **−2,38%** | +1,10pp → **+0,72pp** |
| 2 | `SpaceX_weekly_report_2026-09-21_to_2026-09-25.md` | 83 | −4,40% | 01/07 | **−4,03%** | +2,70pp → **+2,33pp** |
| 3 | `SpaceX_weekly_report_2026-09-28_to_2026-10-02.md` | 86 (+ dòng 167 "VN-Index so sánh tại cùng mốc") | −6,94% | 01/07 | **−6,58%** | +4,61pp → **+4,25pp** |
| 4 | `SpaceX_weekly_report_2026-10-05_to_2026-10-09.md` | 85 (+ dòng 171 "đóng cửa 01/07/2026: 1.867,21") | −7,08% | 01/07 | **−6,72%** | +5,75pp → **+5,39pp** |
| 5 | `ZaloPay_weekly_report_2026-09-14_to_2026-09-18.md` | 94 | −1,76% | 07/07 | **−1,51%** | −1,06pp → **−1,31pp** |
| 6 | `ZaloPay_weekly_report_2026-09-21_to_2026-09-25.md` | 95 | −3,42% | 07/07 | **−3,17%** | +0,45pp → **+0,20pp** |
| 7 | `ZaloPay_weekly_report_2026-09-28_to_2026-10-02.md` | 86 (+ dòng 88 "mốc = đóng cửa 03/07") | −6,68% | 03/07 | **−5,74%** | +2,89pp → **+1,95pp** |
| 8 | `ZaloPay_weekly_report_2026-10-05_to_2026-10-09.md` | 86 (+ dòng 88 "mốc = đóng cửa 03/07") | −6,82% | 03/07 | **−5,88%** | +1,91pp → **+0,97pp** |
| 9 | `ZaloPay_monthly_report_2026-09.md` | 29 (+ đoạn 82-83 giải thích mốc 03/07) | −5,02% | 03/07 | **−4,06%** | +2,06pp → **+1,10pp** |
| 10 | `SpaceX_ZaloPay_monthly_report_2026-07.md` | 113-114 (cột VN-Index chung 2 TK) | −6,68% (MTD = QTD) | 30/06 cho CẢ HAI TK | SpaceX −6,68% ✓ · **ZaloPay −5,84%** | ZaloPay: tỉ suất TK lúc đó còn tính từ 01/07 (mốc vốn gốc null) — đã đính chính riêng 27/09 |

Hướng sai: mọi ca SpaceX (#1–4) **thổi chênh so chỉ số lên ~+0,37pp** (có lợi cho mình). Ca ZaloPay #5–6
(mốc 07/07) thổi chênh lên ~+0,25pp; #7–9 (mốc 03/07) thổi lên ~+0,94pp.

## Đúng mốc (không cần đính chính)

| File | Dòng | Ô | Mốc |
|---|---|---|---|
| `SpaceX_monthly_report_2026-09.md` | 28, 70 | −4,91%, chênh +3,07pp | 30/06 ✓ (CLI nhánh: −4,913%) |
| `SpaceX_weekly_report_2026-07-03.md` | 59 | 30/06 → 03/07 +0,11% | 30/06 ✓ |
| `SpaceX_ZaloPay_monthly_report_2026-07.md` (cột SpaceX) | 113-114 | −6,68% | 30/06 ✓ |

## Chưa kiểm
- Ảnh biểu đồ `assets/*_cumret.png` (đường VN-Index "cùng mốc" vẽ từ mốc nào) — không đọc ảnh.
- Bản đã GỬI thật (email/Discord) giả định = file `.md` cùng tên; không đối chiếu proof hash của
  `report_delivery_gate`.
