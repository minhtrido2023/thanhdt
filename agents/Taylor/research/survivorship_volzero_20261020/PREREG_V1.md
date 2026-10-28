# PREREG V1 — Volume=0 trong pin cơ sở (job Taylor_20261020_122917, EXPLORATORY)

Không sửa pin/registry/pin_ledger, không sửa engine thật, không đề xuất đổi luật. Viết + md5 + commit TRƯỚC khi tính (a)/(c).

## 0. Nguồn dữ liệu (tra `mike/kb/data_registry/` trước)
- Ledger: 4 chân pin trích từ kho (`raw/pin_<md5_8>.csv`, md5 4707bcbe/bcd0469f/537e349b/a6ba34d8).
- Volume/OHLC: `data/bq_cache_asof20260729_postrestate/ticker/*.parquet` = đúng `BQ_LOCAL_CACHE` mà pin đã chạy
  (không dùng BQ sống — vintage khác pin là một trục ngoài lệnh).
- Ngữ nghĩa: **user xác nhận 2026-10-20 — `Volume = 0` = không có giao dịch khớp trong ngày.**
  "Ngày KL=0" = dòng (ticker, ngày khớp) có `Volume == 0` đúng bằng 0. Dòng thiếu / `Volume` NaN đếm RIÊNG, không gộp.

## 1. (a) Mô tả — 4 chân
TX (bỏ `play_type == ETF_PARK`; nhóm ETF_PARK báo riêng 1 dòng nếu ticker là cổ phiếu thật), ngày = `ymd` (ngày khớp):
- n lệnh, n lệnh KL=0, tỷ trọng GIÁ TRỊ (buy_amount / sell_amount) rơi vào ngày KL=0 — theo book (BAL/LAG) × phía (mua/bán),
  theo năm, theo `reason` phía bán.
- Kiểm giá carry trên các dòng KL=0 có lệnh: (i) `O=H=L=C` (adj); (ii) `Close == Close` phiên trước của chính mã (trong cache);
  (iii) cả hai. Báo % lệnh (và % giá trị) ở mỗi loại. "carry" = (iii). Còn lại = "giá khác phiên trước".
- 3 ví dụ lớn nhất mỗi phía (ticker, ngày, giá trị).

## 2. (b) Biến thể engine (BẢN SAO `eng/`, env `ZVF_MODE`; mặc định off phải byte-identical với pin)
- **V1A `block`** (biến thể CHÍNH — chỉ áp đúng ngữ nghĩa user đã xác nhận, không thêm giả định thanh khoản):
  - MUA: phiên KL=0 coi như "không có giá" ⇒ đi vào nhánh carry-over SẴN CÓ của engine (lệnh nằm lại, đếm vào cửa sổ
    `max_fill_days=5`; hết cửa sổ mà <`min_fill_pct` ⇒ bỏ như engine đang làm; có phần khớp ⇒ `_finalize_partial` như cũ).
    Đây là cơ chế hoãn có sẵn, KHÔNG phải "hoãn tới ngày có KL vô hạn": nếu 5 phiên liền KL=0 thì lệnh bị bỏ.
  - BÁN T+1 Open: phiên KL=0 ⇒ `still_pending` (nhánh sẵn có "không có giá Open"), thử lại mỗi phiên tới khi có KL>0.
  - Mark-to-market không đổi (engine vẫn mark theo Close kể cả ngày KL=0).
- **V1B `block_advbuy`** (giả định mô hình hoá): V1A + trần MUA/ngày = 20% × `Volume_ngày × Price_ngày` THAY trần
  20% × ADV 3M (`Volume_3M_P50 × Px`). 20% = đúng `liquidity_volume_pct` của engine.
- **V1C `block_advboth`** (giả định mô hình hoá): V1B + trần BÁN/ngày cùng công thức; phần dư nằm lại `pending_exits`,
  bán tiếp phiên sau (mỗi phần bán ghi 1 dòng sell, reason `<gốc>_ZVFCAP`). Engine gốc không có trần bán.
- Áp cho MỌI lệnh gọi `simulate()` (BAL, LAG, và 2 lượt base cho CAPIT) — cùng một luật khớp. Không đụng giỏ park
  custom30/ETF (cơ chế riêng, ngoài phạm vi; nếu (a) cho thấy ETF_PARK có lệnh KL=0 thì ghi là giới hạn).
- Ngoài phạm vi (đã kiểm không xuất hiện trong pin): EVICT, partial/soft-stop, force-delever (0 dòng trong 4707bcbe).

## 3. (c) Đo và nhãn
- Mỗi biến thể × 4 chân: `METRIC cagr / sharpe_252 / max_dd` từ CSV engine; Δ = biến thể − pin (pp cho CAGR/MaxDD).
- Nhãn theo |ΔCAGR| so sàn nhiễu **0,46pp** ở cả 4 chân: mọi chân <0,46 ⇒ "dưới sàn nhiễu"; mọi chân ≥0,46 ⇒ "vượt sàn
  nhiễu"; còn lại ⇒ "vượt sàn ở k/4 chân". Nhãn CHÍNH = V1A. V1B/V1C báo kèm nhãn "giả định mô hình hoá".
- Kèm số đếm từ engine: số lần mua bị chặn / bán bị hoãn / bị trần (`[ZVF]` trong log).

## 4. Control + self-check (bắt buộc, trước khi đọc Δ)
- Bản sao `eng/` với `ZVF_MODE=off` chạy 4 chân ⇒ md5 CSV phải = 4 md5 pin. Lệch ⇒ dừng, báo, không đọc Δ.
- Mọi run (control + biến thể): `[selfcheck BAL/LAG] cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`.
  V1C thêm dòng bán từng phần ⇒ nếu self-check vỡ thì báo "engine không cho biến thể sạch" cho V1C.

## 5. Giới hạn biết trước
- Trần theo KL ngày (V1B/V1C) dùng KL của CHÍNH phiên khớp, không biết được lúc mở cửa ⇒ là trần thực tế khả thi
  (participation), không phải luật nhân quả có thể chạy live.
- Lệnh hoãn khớp ở Open phiên sau (giá khác) — đây là hệ quả cơ học, không phải ước lượng slippage.
- Pin chỉ chứa mã có trong panel (survivorship để V2).
