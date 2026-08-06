---
kind: local-file
status: CANONICAL
source: data/rubber_weekly.csv
group: feeds
cadence: NGÀY (T2-T6)
writer: rubber_weekly.py qua rubber_weekly.sh, cron 18:35 ICT T2-T6
note: chuỗi ngày THẬT chỉ bắt đầu 2026-06-19 — phần trước đó là wb_seed (trung bình tháng)
---

# data/rubber_weekly.csv

**Status: CANONICAL**

## Là gì
Chuỗi giá cao su RSS3 (USD/kg) theo ngày, nguồn `regionalert` (SGX SICOM) + `sunsirs`
(spot Trung Quốc). Cột `src` phân biệt nguồn từng dòng. Đây là input của
`rubber_weekly.py` để tính WoW / 4 tuần / 3 tháng / biên 52 tuần và bắn cảnh báo
WATCH/ALERT cho Taylor + DollarBill + Telegram.

## Ai ghi / cadence
`rubber_weekly.py` (qua `rubber_weekly.sh`), cron 18:35 ICT T2-T6. Append + dedupe theo `date`.

## Bẫy

**1. Chuỗi ngày THẬT chỉ bắt đầu 2026-06-19 — đừng coi độ dài file là độ dài lịch sử.**
Các dòng `src == "wb_seed"` là mồi gieo từ World Bank monthly (trung bình tháng, mốc giữa
tháng), KHÔNG phải quan sát ngày. Lọc `src != "wb_seed"` cho ra chuỗi thật, nhưng chuỗi thật
đó tính tới 2026-08-04 mới chỉ **33 dòng trải 46 ngày lịch** — tức 6,6 tuần, không phải 52 tuần.

**2. ĐẾM SỐ DÒNG ≠ ĐO ĐỘ PHỦ THỜI GIAN — đây là sự cố thật, không phải giả định.**
Ngày 2026-08-04 cổng biên 52 tuần trong `rubber_weekly.py` là `len(real) >= 30` (đếm dòng).
33 dòng vượt cổng, nên code so giá hiện tại với min của một cửa sổ 6,6 tuần mà min đó **chính
là giá hiện tại** → công bố "phá đáy 52 tuần" và bắn ALERT sai ra Telegram + DollarBill +
Taylor. Biên 52 tuần THẬT (WB monthly) là 2,00–2,92 USD/kg; giá bị gắn nhãn 2,596 nằm ~65% độ
cao của biên, không hề gần đáy. Đã sửa 2026-08-06 (commit `d2aeb9f`, job
`Winston_20260806_111121`): cổng đổi sang **độ phủ lịch** (`BAND_MIN_SPAN=330` ngày,
`BAND_MAX_GAP=45` ngày) + ghép WB monthly (`data/rubber_monthly.csv`, xem
[`commodity_wb_cmo.md`](commodity_wb_cmo.md)) vào phần cửa sổ chuỗi ngày chưa với tới.
→ **Bất kỳ code mới nào tính min/max/percentile trên file này phải kiểm tra ĐỘ PHỦ LỊCH của
phần `src != "wb_seed"`, không được tin số dòng.**

**3. Trộn WB monthly với giá ngày làm biên bị NÉN HẸP hơn thực tế ở CẢ HAI PHÍA.**
Một điểm WB monthly là TRUNG BÌNH THÁNG nên nằm bên trong biên độ ngày thật của tháng đó. Đo
trên 3 tháng có cả hai nguồn: trung bình tháng trải 2,69–2,81 trong khi ngày thật trải
2,60–2,92. Phép thử "phá biên" trên biên đã nén sẽ BẮN QUÁ NHIỀU. Vì vậy `band_52w()` đánh dấu
biên là **MỀM** khi cửa sổ còn chứa bất kỳ điểm monthly nào — phá biên mềm chỉ báo WATCH cho
Taylor, không tự nâng lên ALERT. Tự cứng lại 2027-06-16 (ngày cửa sổ 365d thoát khỏi điểm
monthly cuối). *Rủi ro tồn dư đã công bố:* cờ mềm bật khi có BẤT KỲ điểm monthly nào trong cửa
sổ, không phải chỉ khi cực trị đến từ điểm monthly — nên một cú trượt CHẬM xuyên đáy 52 tuần
thật mà không vượt `WoW>=12%` / `3 tháng>=25%` sẽ chỉ nằm ở WATCH tới ~2027-06.

**4. Nghi vấn chất lượng nguồn `regionalert`, CHƯA giải quyết.** Đúng ngày 2026-08-04, RSS3
in ra −6,95%/ngày trong khi spot Trung Quốc (`sunsirs`) cùng ngày +1,52%. Chưa truy được
nguyên nhân. Lớp phòng thủ đang có: ALERT phải lặp lại **2 phiên đo liên tiếp** mới gửi
Telegram/DollarBill (event bus cho Taylor vẫn bắn ngay phiên đầu). Nếu tái diễn → truy nguồn
`regionalert` trước khi tin con số.

## Kiểm chứng
`rubber_weekly_selfcheck.py` (repo root) — 60/60 PASS, bất biến qua TZ mặc định / `env -u TZ` /
`TZ=UTC` / `TZ=America/New_York`. Phát lại đúng CSV as-of 2026-08-04 cho `band=None tier=INFO`
sau fix so với `band=low tier=ALERT` trước fix. quant-skeptic CONFIRMED (high),
log `mike/logs/verify_20260806_115406_186144.log`.

## Liên quan
- [`rubber_alert_state.md`](rubber_alert_state.md) — state chống lặp alert của chính script này
- [`commodity_wb_cmo.md`](commodity_wb_cmo.md) — `data/rubber_monthly.csv`, nguồn ghép biên 52 tuần

↩ [Về index nhóm](index.md)
