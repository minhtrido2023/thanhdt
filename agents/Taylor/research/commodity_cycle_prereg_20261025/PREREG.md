# PREREG — "Pha đầu chu kỳ hàng hoá" → lợi suất mã phơi nhiễm (job Taylor_20261025_061240)

Viết **trước khi** chạy bất kỳ phép tính lợi suất nào (commit trước `run.py`). Mọi thứ dưới đây
là cố định; thay đổi sau khi thấy kết quả phải ghi ở mục "Lệch PREREG" của REPORT.md.

## Câu hỏi
Khi giá một hàng hoá bước vào pha tăng (PIT, chỉ dùng dữ liệu đã công bố), giỏ mã VN sản xuất
hàng hoá đó có vượt trội nhóm cùng ngành không phơi nhiễm trong 6 tháng tiếp theo không? Nếu có,
đây là kênh bắt sớm mà LAG (vào sau công bố KQKD) và cờ DCF/EQ_CFO_YEU không bắt được.

## Dữ liệu (đã tra `kb/data_registry/`)
- Giá hàng hoá: WB CMO monthly (`feeds/commodity_wb_cmo.md`, CANONICAL), file
  `data/_wb_cache/CMO-Historical-Data-Monthly.xlsx` (bản 2026-10-10, tới 2026M09).
- Giá cổ phiếu: `data/bq_cache/ticker/*.parquet` (DERIVED mirror của `tav2_bq.ticker`), cột `Close`
  (điều chỉnh). Universe: `data/bq_cache/universe_pit/*.parquet` (`in_universe`, CANONICAL, từ 2013).
  KHÔNG dùng `ticker_prune`, KHÔNG dùng `profit_*`.
- Bản đồ mã↔hàng hoá: `commodity_map.csv` (cột `in_primary`).

## Họ thử nghiệm chính (5 họ, 20 mã, cột `in_primary=Y`)
rubber (RSS3: DRI PHR DPR TRC GVR TNC DRG) · crude oil (Crude oil, average: PVS PVD PVC PVB GAS) ·
urea (DPM DCM) · DAP (DDV LAS) · sugar (Sugar, world: SBT LSS SLS QNS).
Ngoài thử nghiệm chính (thiếu chuỗi PIT hoặc phơi nhiễm không rõ/ngược): MSR (vonfram — KHÔNG có
chuỗi), PVT/VIP/GSP/VOS/VNA/HAH (cước — chỉ có quý dựng lại 2018+, không đăng ký), CSV (xút SYNTHETIC),
DGC (P4), thép, than, cá tra, heo (chỉ 2019+), lốp (chiều ngược).

## Tín hiệu (MỘT định nghĩa chính)
- `P_m` = giá tháng m của hàng hoá; `MA12_m` = trung bình `P_{m-11..m}`; `R_m = P_m / MA12_m`.
- **Sự kiện** tại tháng m ⇔ `R_m ≥ 1,10` VÀ `R_{m-1} < 1,10` (cắt lên từ dưới), và không có sự kiện
  nào cùng hàng hoá trong 12 tháng trước (thời gian chết 12 tháng ⇒ mỗi sự kiện = 1 pha).
- **PIT**: số tháng m chỉ coi là biết được từ ngày **11 của tháng m+1** (WB Pink Sheet ra đầu tháng,
  cron fleet kéo ngày 5 + 10). Vào lệnh = giá đóng cửa phiên giao dịch đầu tiên **sau** ngày 10 tháng m+1.
  Rủi ro tồn dư đã biết: dùng vintage WB hiện tại, không phải vintage tại thời điểm (WB hiếm khi sửa
  giá tháng; ghi nhận, không xử lý).
- Cửa sổ sự kiện: ngày vào ∈ [2014-01-01, 2026-03-31] (cần đủ 6 tháng lợi suất tới ~2026-10-23).

## Đo lường
- Chân phơi nhiễm: bình quân đều lợi suất `Close_{t+126}/Close_t − 1` các mã của họ đó có
  `in_universe` tại ngày vào (t). Thiếu giá tại t+126 (huỷ niêm yết) ⇒ dùng giá cuối có được.
- Chân đối chứng: bình quân đều cùng phép đo trên các mã `in_universe` tại t, **cùng 2 chữ số đầu
  ICB** (supersector), loại MỌI mã có trong `commodity_map.csv`; nếu < 5 mã ⇒ fallback = toàn bộ
  universe_pit tại t trừ mã trong bản đồ (ghi rõ sự kiện nào fallback).
- **Thống kê chính**: `X = r_exposed − r_control` ở chân trời **6 tháng (126 phiên)**.
- Mô tả phụ (không dùng để chọn): 3M (63 phiên), 12M (252 phiên); ngưỡng 1,05 và 1,20. Tổng 3×3 = 9
  biến thể ⇒ BÁO DSR-kiểu (số thử = 9) cho biến thể tốt nhất nếu nó được nêu ra; nhưng **chỉ biến thể
  chính (1,10 / 6M) được dùng cho kết luận**.
- **Đường nền vô điều kiện**: trung bình `X` của cùng họ đo ở MỌI ngày vào hàng tháng (ngày đầu tiên
  sau ngày 10) trong cùng cửa sổ — để tách hiệu ứng "pha đầu" khỏi chênh lệch trôi dài hạn của nhóm.

## N sự kiện độc lập (khai trước)
- Đơn vị độc lập = **cụm thời gian**: các sự kiện (khác hàng hoá) có ngày vào cách nhau < 126 phiên
  được gộp vào 1 cụm (siêu chu kỳ hàng hoá đẩy nhiều thứ cùng lúc ⇒ không độc lập). N_cluster là N
  thật. Ước lượng trước khi chạy (`ước lượng`, chưa đo): 15–25 sự kiện, 6–10 cụm.
- Với N cỡ đó: KHÔNG dùng t-test trên số dòng. Dùng: (a) trung bình/trung vị theo cụm (mỗi cụm = TB
  các sự kiện trong cụm), (b) sign test nhị thức một phía trên cụm, (c) bootstrap theo cụm 10.000 lần
  (seed 20261025) cho CI 90% của trung bình cụm, (d) leave-one-cluster-out (LOCO), (e) bỏ từng họ.
  Báo MDE xấp xỉ = 2,5 × SD_cụm / √N_cluster.

## Tiêu chí thành công (TẤT CẢ phải đạt — biến thể chính)
1. Trung bình cụm của X ≥ **+5pp** và trung vị cụm > 0.
2. Cận dưới CI 90% bootstrap cụm > 0.
3. ≥ 2/3 số cụm có X > 0 (và sign test p < 0,10).
4. IS (ngày vào 2014–2019) và OOS (2020+) đều có trung bình cụm > 0.
5. LOCO: bỏ bất kỳ 1 cụm nào, trung bình cụm còn > 0. Bỏ bất kỳ 1 họ nào, trung bình còn > 0.
6. Trung bình X sự kiện > đường nền vô điều kiện của chính các họ đó (chênh ≥ +3pp).

## Kịch bản thất bại / cách đọc
- Bất kỳ tiêu chí nào trượt ⇒ **"KHÔNG có edge dùng được"**; báo thẳng, không tìm biến thể khác cứu.
- Đạt 1–3 nhưng trượt 4/5 ⇒ "dấu hiệu tập trung ở 1 giai đoạn/1 họ" — không đủ để đề xuất wire.
- Đạt tất cả ⇒ vẫn chỉ là **ứng viên R&D**: cần quant-skeptic CONFIRMED + paper-trade trước mọi
  thay đổi production. Job này KHÔNG wire, KHÔNG sửa `trading_rules.json`, KHÔNG đặt lệnh.
- Không áp dụng NAV ⇒ không có self-check 0 VND; thay bằng kiểm tra tái lập: đếm sự kiện + tính lại
  X của 3 sự kiện ngẫu nhiên bằng tay từ parquet.

## Ca MSR (trả lời câu hỏi gốc)
MSR KHÔNG nằm trong thử nghiệm vì fleet không có chuỗi giá vonfram. REPORT sẽ nêu nguồn cần có
và mô tả (không kiểm định) đường giá MSR vs mốc LAG.
