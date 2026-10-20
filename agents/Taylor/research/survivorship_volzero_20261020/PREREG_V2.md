# PREREG V2 — Enumerate có hệ thống mã hủy niêm yết từ 2014 (job Taylor_20261020_122917, EXPLORATORY)

Không sửa pin/registry/pin_ledger, không sửa engine, không đề xuất đổi luật. Viết + md5 + commit TRƯỚC khi dựng tập và
TRƯỚC khi tính phantom. Tái dùng NGUYÊN VĂN `survivorship_replay_20261020/svr_replay.py` + `svr_lib.py` và `simulate2` /
`phase_mask` / `book_fraction_fix` của `survivorship_followup_20261020/svr_followup.py` (PREREG_BC md5 d9a91be2).

## 1. Danh sách gốc (không chọn tay)
- `kb/projects/delisted-tickers-survivorship-20261020.csv` (Winston) với `in_data == False` (231 mã) ∩ có file giá
  `.d/prices_all/<tk>.csv` (VNDirect) ⇒ **U230**. Mã thiếu file giá (ví dụ DSH) liệt kê, không dựng được.
- Sàn gốc `orig` = `exch2` trong `agents/Winston/research/vanished_20261020/stats_all.csv`; nếu không phải HOSE/HNX/UPCOM
  ⇒ quy tắc mặc định của `R.Tk` (sàn ≠UPCOM xuất hiện nhiều nhất).

## 2. Quy tắc nhập tập (RULE-BASED, cố định trước khi chạy)
Mã tk ∈ U230 vào tập **A** nếu đủ CẢ hai:
1. `LT` (ngày khớp cuối có nmVolume>0 trên sàn gốc, theo `R.Tk`) ≥ **2014-03-03** (có ít nhất ~2 tháng trong cửa sổ backtest
   2014-01-02→2026-06-19);
2. có ≥ **60 phiên nmVolume>0** trên sàn gốc ≤ LT (đủ cửa sổ ADV 60 phiên của engine).
Không lọc theo thanh khoản ở bước này: **ngưỡng thanh khoản của engine áp NGAY trong replay, tại thời điểm vào** —
BAL: universe replica (median 60 phiên tv_real ≥1e9) ∧ `liq ≥ 1e9`; LAG/BAL: khớp ≤ cap×ADV60 mỗi phiên trong 5 phiên, bỏ
lệnh nếu < 30% mục tiêu; phiên vào phải có KL>0. Mã nào không sinh lô nào là do luật engine, không phải do tôi chọn.
- **N** = A \ (M ∪ {HVG}) (mã MỚI so với 14 mã M đã replay). Báo thêm **M∪N** (= A trừ HVG).
- Mã lỗi khi dựng (`R.Tk` ném lỗi, giá rỗng…) ⇒ liệt kê kèm lỗi, loại khỏi tập; KHÔNG sửa tay.

## 3. BCTC (MID/LIVE)
Tải VNDirect `financial_statements` (QUARTER, modelType 1/2/3; cùng endpoint/ITEMS với `svr_fetch.py`) cho mọi mã N,
ghi `data/fin_raw_v2.csv`; gộp với `fin_raw.csv` Winston (M) qua cùng pivot `R.load_fin`. Mã không có `npat_parent`
quý nào ⇒ MID/LIVE = không có lô (giống engine: không có sự kiện công bố ⇒ không có tín hiệu LAG); **liệt kê là GIỚI HẠN**
("không dựng được BCTC"), không coi là bằng chứng an toàn. Báo số mã N có / không có BCTC.

## 4. Replay
Mọi chân: 4 ledger pin (4707bcbe/bcd0469f/537e349b/a6ba34d8), kiểm tái tạo METRIC cagr ≤1e−9. Kịch bản **Z**, thoát X-liq,
trọng số **fixA** (`survivorship_sensitivity_v2_20261020/out_summary.json`, `book_fraction_fix`).
- **Cấu hình CHÍNH**: cap **5% trong pha bơm/xả** (`phase_mask`, 20% ngoài pha) + `exitval = nm` (chỉ khớp lệnh) + KL>0
  (sẵn trong `simulate2`).
- **Độ nhạy**: cap 20% mọi ngày + `exitval = ptin` (= cấu hình replay gốc).
- Biến thể UB / MID / LIVE; book BAL, LAG, MIX; tập M, N, M∪N. ALLOC (overlay_alloc) báo kèm, gắn \* "không phải nhãn chính".

## 5. Báo cáo + nhãn
- ΔCAGR / ΔSharpe / ΔMaxDD (MIX) dải 4 chân cho mỗi (tập × biến thể × cấu hình).
- Nhãn theo sàn nhiễu **0,46pp** (|ΔCAGR| MIX, 4 chân): mọi chân <0,46 ⇒ "dưới sàn"; mọi chân ≥0,46 ⇒ "vượt sàn"; còn lại
  ⇒ "cắt sàn (k/4)". Nhãn chính: N, cấu hình chính, MID và LIVE (UB = cận).
- **"Có thêm mã nào vượt sàn không"**: ΔCAGR MIX của TỪNG mã N chạy một mình (overlay chỉ lô của mã đó), cấu hình chính, mỗi
  biến thể; mã có |Δ| ≥0,46 ở ≥1 chân ⇒ liệt kê. Top 5 mã đóng góp |Δ| lớn nhất mỗi biến thể (p30_pin0 + dải 4 chân).
- Số mã N sinh ≥1 lô (BAL/LAG) mỗi biến thể; số lô kẹt (stuck).

## 6. Giới hạn biết trước
- Release date ước lượng (trễ trung vị theo quý), BCTC VNDirect chưa đối chiếu BCTC gốc; MID/LIVE là xấp xỉ cổng engine,
  không phải cổng thật. UB bỏ qua cạnh tranh slot. Giá `prices_all` chưa đối chiếu nguồn thứ hai (trừ GAB).
- `cat` mất tư cách đại chúng (UPCOM) ⇒ Z (xoá sổ) bi quan cho nhóm này; báo riêng phần đóng góp của nhóm `bat_buoc`.
- Tập Winston = sự kiện `SUSP` trong `corporate_action`; sáp nhập/đổi mã có thể thiếu (Winston đã ghi).
