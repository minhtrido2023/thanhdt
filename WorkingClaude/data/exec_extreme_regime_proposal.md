# Đề xuất thiết kế — Execution trong biến động bất thường (EXTREME regime gate)

> Tác giả: Taylor (Quant) · 2026-07-01 · job Taylor_20260701_051259
> **Trạng thái: ĐỀ XUẤT THIẾT KẾ để bàn với user — CHƯA phải lệnh sửa production.**
> Nguồn: tư liệu quốc tế Mike tổng hợp + kiến trúc thật `trading_bot/executor.py`, `trading_bot/config.py`.

## 0. Tóm tắt 1 dòng
Giữ nguyên regime NORMAL (cap tĩnh 1.5%/3% — tốt cho ngày thường), thêm **1 công tắc regime
EXTREME đo được** (khoảng cách tới trần/sàn + tốc độ move) để: (a) mở sàn chase bán xuống tận
**sàn sàn của mã** khi sập, (b) **tạm dừng mua** (không bắt dao rơi) khi mã lao về sàn, (c) rút ngắn
nhịp slice để đuổi kịp sổ lệnh. Neo vào **bài học VN-2022: phản ứng SỚM khi giá mới bắt đầu giảm
mạnh, không chờ chạm sàn cứng.**

---

## 1. Vấn đề (đã xác nhận ở file:line)

| # | Điểm yếu | Nơi trong code | Hệ quả |
|---|---|---|---|
| a | Sàn chase bán tĩnh −3% | `executor.py:259-266`, `config.py:48` (`max_chase_pct_sell=0.03`) | Sập >3%: lệnh bán nằm ở `ref×0.97`, KHÔNG đuổi sổ lệnh xuống → stop-loss thật không khớp |
| b | Guard limit-down chỉ nằm trong `gap_adaptive` (OFF live) | `executor.py:399-405` bên trong `_cache_gap_z`, gate bởi `gap_adaptive_enabled` (`config.py:66=False`) | Live không có guard bắt-dao-rơi; đồng thời adaptive DIP (`executor.py:234-241`) lại **cross MUA khi giá đang rơi** |
| c | Live không phản ứng biến động cực đoan | `executor.py:418-419` (`fill_timing_live_gate` → mult=1.0 ở live) | Toàn bộ lớp gap/fill-timing bị bypass ở live; cap tĩnh là logic DUY NHẤT |

**Điểm mấu chốt:** hạ tầng đã có sẵn (rvol_20d trong `_gap_ref`, px_hist + `_r15`, `q.floor/q.ceiling`,
vòng cancel-&-reprice trong `_cancel_stale`). Ta KHÔNG cần cỗ máy mới — chỉ cần **1 cổng regime
always-on** dùng lại các mảnh này.

---

## 2. Nguyên tắc thiết kế (map từ tư liệu quốc tế)

1. **2-regime, không nhị phân tham số** (Markov regime-switching, tư liệu #4): NORMAL = cap tĩnh giữ
   nguyên; EXTREME = logic thoát nhanh. Chuyển bằng **tín hiệu đo được**, không phải % tĩnh.
2. **Phản ứng SỚM, không chờ giá đẹp** (magnet effect #6 + VN-2022 #7): phần LỚN KL khớp XẢY RA
   TRƯỚC khi sàn khóa cứng (HPG/MBB/SHB 2022 còn dư bán sàn hàng chục triệu cp). ⇒ trigger phải nổ
   khi giá **đang tiến gần** sàn, không phải sau khi chạm sàn.
3. **Urgency ladder, không on/off** (post-and-wait-then-sweep #2 + Almgren-Chriss #1): vol cao → urgency
   cao → rút ngắn horizon, sẵn sàng cross. Vòng `_cancel_stale`→reprice sẵn có CHÍNH LÀ ladder này;
   chỉ cần nới sàn + rút interval để nó chạy nhanh.
4. **Offset co giãn theo vol thực** (ATR-scaled #3): VN có **biên độ cứng** nên "sàn của mã" (`q.floor`)
   ĐÃ là mức ATR-scaled tự nhiên. Bán xuống tới sàn = thoát chắc, gọn hơn tính ATR band có thể dừng non.
5. **Kill switch tách biệt** (#5): `BOT_STOP` (`executor.py:619-624`) chỉ **HỦY lệnh treo + thoát**, KHÔNG
   thanh lý. Nó là "dừng bot", không phải "bán sạch". Logic EXTREME-DOWN là bảo vệ tự động cho phần
   ĐANG bán theo plan — không tự khởi tạo lệnh bán mới. Panic-exit-all (nếu user muốn) là công cụ thủ
   công riêng, ngoài phạm vi này.

> **Lưu ý thời hằng — khác DT5G:** DT5G là regime CHIẾN LƯỢC, cố ý *chậm commit* (25 phiên vào CRISIS).
> EXTREME regime ở đây là lớp EXECUTION, phải *nhanh* (giây–phút). Khác lớp, khác time-constant — nêu rõ
> để tránh nhầm hai khái niệm regime.

---

## 3. PHƯƠNG ÁN KHUYẾN NGHỊ (một, cụ thể)

### 3c. Trigger (nền tảng — làm trước) — `_extreme_regime(ticker, q, now)`
Mỗi mã, mỗi tick, tính cờ EXTREME từ dữ liệu ĐÃ có trong vòng lặp. Bật khi **BẤT KỲ** điều kiện:

- **(i) Cận biên độ** *(chính, VN-specific, rẻ, robust)*: `last` nằm trong `extreme_band` (đề xuất **3%**)
  của **sàn** ngày → `EXTREME_DOWN`; trong 3% của **trần** → `EXTREME_UP`. Dùng `q.floor/q.ceiling` đã
  fetch (fallback `ref×(1∓0.07)` theo `gap_floor_band` khi broker không expose — mẫu có sẵn ở
  `executor.py:401-402`).
- **(ii) Tốc độ move bất thường** *(phụ, tổng quát)*: `|r15|` (đã có `_r15`, `executor.py:164-182`) vượt
  `extreme_move_z` (đề xuất **3.0**) × `rvol_20d` (đã có trong `_gap_ref`). Tức move 15' > 3σ ngày.

**Chống nhiễu:** cần **2 poll liên tiếp** xác nhận (~40s ở `poll_interval_sec=20`) + **cooldown**: đã bật
EXTREME thì giữ tối thiểu **N phút** (đề xuất 15') trước khi hạ, tránh whipsaw on/off.
**Fail-safe:** thiếu quote / thiếu `rvol_20d` / `day_volume` quá nhỏ (illiquid air-pocket) → **KHÔNG** bật
EXTREME (giữ NORMAL). Không bao giờ để một tick lỗi kích hoạt bán tháo.

### 3a. Sàn chase BÁN khi sập — chế độ "sell-to-exit"
Khi mã `EXTREME_DOWN` **và** parent là **SELL**, trong `_limit_price` (nhánh sell `executor.py:258-269`):
- **Nới sàn**: `floor_cap = q.floor` (bán tới tận sàn sàn) thay cho `ref×(1−0.03)`.
- **Luôn cross**: hit bid (`desired=q.bid`), không nằm passive chờ hồi.
- **Rút interval**: `slice_interval × extreme_slice_mult` (đề xuất **0.25** → ~2') để vòng
  `_cancel_stale`→reprice (`executor.py:321-337`) đuổi kịp sổ lệnh đang tụt.

⇒ Triển khai đúng bài học VN-2022 (#7): bán SỚM (trigger nổ khi mới cận sàn, #6) và sẵn sàng hạ giá tới
sàn để khớp trong lúc thanh khoản CÒN, thay vì kẹt ở −3% rồi mắc lại khi sàn khóa cứng.
*Thay thế bị loại:* ATR-band `k×rvol` — bỏ vì ở thị trường biên độ cứng, band mã đã là ATR tự nhiên;
tính riêng dễ dừng non hơn `q.floor`.

### 3b. Guard bắt-dao-rơi khi MUA — tách guard tối thiểu always-on
**Không** bật lại `gap_adaptive` ở live. Thay vào đó **tách 1 guard tối thiểu** trong cổng EXTREME
always-on: khi mã `EXTREME_DOWN` **và** parent là **BUY** → **tạm dừng đặt slice mua** (skip trong
`_place_slices`, `executor.py:443-499`).
- **Lý do chọn tách, không bật gap_adaptive:** phân tách trách nhiệm — `gap_adaptive` là **bộ tối ưu
  timing/return** (paper, chưa chứng minh live); guard limit-down là **kiểm soát rủi ro**, phải nằm ở
  đường always-on, không núp sau cờ optimizer.
- **Vì sao dừng hẳn (không mua passive thấp):** lệnh mua theo plan KHÔNG có urgency phải khớp giữa cơn
  sập — plan T+1 tự re-sync. Dừng là fail-safe: xấu nhất là lỡ 1 nhịp mua, mai mua lại. Tránh hẳn việc
  cross mua vào đà rơi mà adaptive DIP hiện đang làm (`executor.py:234-241`).

---

## 4. Tradeoff & điều kiện go-live (phải nói với user)

- **Thêm 4 param + 1 nhánh regime ⇒ cần validate paper trước live.** Đề xuất gate `extreme_regime_enabled`
  **default OFF**, giống pattern `gap_adaptive`. User duyệt live sau khi quan sát ≥1 ngày stress paper
  HOẶC replay tick-data crash 2022 (nếu có).
- **Khó backtest sạch:** regime cấp execution cần dữ liệu quote/sổ lệnh intraday lịch sử — ta có thể
  KHÔNG có đủ. ⇒ validation là **paper + replay 2022**, KHÔNG phải IS/OOS clean. (Nêu thẳng hạn chế này —
  không giả vờ có backtest auditable như các edge chiến lược.)
- **False-trigger trên mã illiquid** chạm biên do KL mỏng → bán vào air-pocket. Mitigate: (1) chỉ ACT
  sell trên phần plan ĐANG bán, không tự khởi tạo bán mới; (2) yêu cầu `day_volume` tối thiểu; (3) confirm
  2 poll + cooldown.
- **Buy-pause fail-safe an toàn**, không cần validate gắt như sell-mode (xấu nhất: lỡ nhịp mua).
- **Không có thanh lý cưỡng bức tự động** — cố ý (human-in-loop). Nếu user muốn nút "bán sạch khẩn cấp",
  đó là tool thủ công riêng, đề xuất bàn tách.

## 5. Bề mặt code dự kiến (khi user duyệt — chưa làm)
- `config.py`: `extreme_regime_enabled=False`, `extreme_band=0.03`, `extreme_move_z=3.0`,
  `extreme_slice_mult=0.25`, `extreme_cooldown_min=15`, `max_chase_pct_sell_extreme` (hoặc dùng thẳng `q.floor`).
- `executor.py`: hàm `_extreme_regime()`; nhánh trong `_limit_price` (sell floor + cross),
  `_place_slices` (buy-pause + interval mult). NORMAL path giữ nguyên byte-for-byte.

---
*Đề xuất này để user quyết. Không có thay đổi production nào được áp trước khi user duyệt.*
