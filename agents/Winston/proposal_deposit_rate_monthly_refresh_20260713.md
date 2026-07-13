# ĐỀ XUẤT — Routine cập nhật THÁNG cho `deposit_rate_vn.py` (Big-4 12M deposit rate)
> Winston, 2026-07-13 · job `Winston_20260713_131255` · §2 của plan Pillar A′
> (`mike/agents/Taylor/plan_deposit_rate_signal_20260713.md`). **CHỈ LÀ ĐỀ XUẤT — CHƯA cài
> crontab, CHƯA sửa `deposit_rate_vn.py`/`rating_8l.py`.** Trình diff này cho Mike/user duyệt
> trước khi áp dụng bất kỳ phần nào.

## 0. Vì sao cần (độc lập với GO/NO-GO backtest Pillar A′)

`deposit_rate_vn.py` hiện là **1 lần calibrate hồi tố** (2026-06-19) — 26 mốc 2011→2026-06, không
có cơ chế nào thêm mốc mới. Đây là input **LIVE production** thật (không chỉ nghiên cứu):
`rating_8l.py` dùng `current_deposit_rate()` cho gentle NEUTRAL-only deposit tilt ±0.03 trên
`value_score_v3`, chạy MỖI NGÀY trong `pt_8l_daily.sh` (17:45 ICT). Không có refresh → chuỗi sẽ
đứng yên ở 6.8% (mốc 2026-06) vô thời hạn, rating sống sẽ dùng số cũ dần sai khi lãi suất thị
trường di chuyển tiếp — im lặng, không ai cảnh báo (chưa có freshness-check nào cho nguồn này).

## 1. Nguyên tắc thiết kế — APPEND-ONLY, không đụng 26 mốc lịch sử đã calibrate

Mirror đúng pattern đã dùng cho `fa_ratings`/`fa_ratings_8l` (frozen quá khứ, chỉ append tương
lai) — KHÔNG re-calibrate lại lịch sử, KHÔNG xoá/sửa `DEPOSIT_EVENTS` hiện có trong
`deposit_rate_vn.py`. Lý do: 26 mốc cũ là ước lượng có chủ đích (lending-spread reasoning), sửa
lại sẽ đổi số backtest đã dùng ở nhiều nơi (rating_8l tilt, deposit-gate floor) mà không ai yêu cầu.

**Thay đổi cấu trúc dữ liệu đề xuất:**
- Giữ nguyên `DEPOSIT_EVENTS` (list hardcode) làm phần LỊCH SỬ ĐÓNG BĂNG trong
  `deposit_rate_vn.py` — không sửa.
- Thêm 1 file CSV mới **`data/deposit_rate_vn_events.csv`** (append-only, con người/script mới
  ghi vào đây) với schema:

  | Cột | Ý nghĩa |
  |---|---|
  | `effective_date` | Ngày lãi suất có hiệu lực (posted rate ngân hàng công bố) |
  | `deposit_rate` | Big-4 12M %/năm (trung bình 4 ngân hàng — xem §3 cách tính) |
  | `collected_date` | Ngày THẬT thu thập số liệu (khác `effective_date`) — từ đây trở đi chuỗi
    là **point-in-time thật**, không còn hindsight cho các mốc tương lai |
  | `source` | `vcb_web` / `bidv_web` / `ctg_web` / `agribank_web` / `cafef` / `vietstock` /
    `manual_verify` |
  | `note` | tự do (vd "BIDV +0.2pp so tháng trước") |

- Sửa `deposit_events_df()` trong `deposit_rate_vn.py`: nếu file CSV tồn tại, `concat` các dòng
  có `effective_date` > mốc cuối cùng của `DEPOSIT_EVENTS` (2026-06-01) vào cuối chuỗi trước khi
  sort — không có CSV thì hành vi y hệt hiện tại (backward-compatible 100%, không phá gì đang chạy
  qua `merge_deposit`/`current_deposit_rate`/`rating_8l.py`).

```python
# trong deposit_events_df(), sau khi build `ev` từ DEPOSIT_EVENTS:
_csv_path = os.path.join(os.path.dirname(__file__), "data", "deposit_rate_vn_events.csv")
if os.path.exists(_csv_path):
    extra = pd.read_csv(_csv_path, usecols=["effective_date", "deposit_rate"])
    extra = extra.rename(columns={"effective_date": "time"})
    extra["time"] = pd.to_datetime(extra["time"])
    ev = pd.concat([ev, extra[extra.time > ev.time.max()]], ignore_index=True)
return ev.sort_values("time").reset_index(drop=True)
```

## 2. Feasibility fetch tự động — ĐÃ THỬ, kết quả: không đủ tin cậy để tự-append

Trước khi đề xuất mức tự động hoá, đã thử fetch thật (2026-07-13):
- **CafeF lãi suất ngân hàng** (`cafef.vn/du-lieu/lai-suat-ngan-hang.chn`): bảng dữ liệu load
  **động qua JS/API riêng**, không nằm trong HTML tĩnh — fetch thô không lấy được số.
- **Vietcombank official site**: timeout 60s khi fetch — site chậm/có thể chặn bot, không đáng
  tin cậy cho 1 cron chạy vô người giám sát.

→ **Không đề xuất auto-parse-và-tự-ghi** kiểu `auto_update_commodity_wb.py` (World Bank có xlsx
tĩnh dễ parse; đây thì không). Đề xuất theo đúng tinh thần `check_sbv_weekly.sh` đã có sẵn trong
hệ thống: **best-effort fetch KHÔNG BẮT BUỘC, con người xác nhận số cuối cùng, không bao giờ tự
động ghi vào chuỗi sống.**

## 3. Thiết kế routine đề xuất — 2 lớp

**Lớp A (khuyến nghị chính, MVP rẻ và chắc): reminder-only + append thủ công có kiểm.**
- Script mới `refresh_deposit_rate_vn.sh` chạy đầu tháng (đề xuất ngày 3, 08:10 ICT — cùng khung
  `auto_update_commodity_wb.sh` ngày 5/10, lệch ra để không trùng phút):
  1. Đọc mốc cuối cùng hiện có (kể cả từ CSV append nếu đã có) qua `current_deposit_rate()`.
  2. Best-effort: thử fetch CafeF/VCB (script Python nhỏ, timeout ngắn 15s, không retry mạnh —
     đã biết tỉ lệ thành công thấp) — NẾU parse được số tin cậy (regex sát `12 tháng`), coi là
     gợi ý, KHÔNG tự ghi.
  3. Post Discord/Telegram (Trading Daily hoặc kênh Winston chọn) 1 tin nhắn ngắn: "Đầu tháng
     <YYYY-MM> — xin xác nhận lãi suất tiết kiệm 12T Big-4 hiện tại (VCB/BIDV/CTG/Agribank).
     [Gợi ý tự động nếu fetch được: X%]. Chạy `append_deposit_rate.py --rate X --date
     <collected_date>` để ghi." — con người xác nhận số trong ~30 giây (đúng effort thấp, tần
     suất tháng, không đáng để nuôi 4 scraper riêng).
  4. Script `append_deposit_rate.py --rate <X> --effective <date> --source <manual_verify|...>`
     — CLI nhỏ, append 1 dòng vào `deposit_rate_vn_events.csv` (atomic write), verify
     `deposit_events_df()` load lại đúng (giống selfcheck các script khác trong repo).
  5. Nếu KHÔNG ai chạy `append_deposit_rate.py` trong vòng ~10 ngày (giống pattern WARN staleness
     nơi khác) → WARN vào `bq_freshness_check.sh`/`ops_health_check.sh` (§4).

**Lớp B (tuỳ chọn, làm sau nếu Lớp A chứng minh hữu ích và cần bớt việc tay):** viết parser riêng
cho 1 nguồn ổn định hơn nếu tìm được (vd trang lãi suất tổng hợp có bảng tĩnh, hoặc API công khai
của 1 trong 4 ngân hàng) — KHÔNG làm ngay, chưa đủ bằng chứng đáng đầu tư thời gian.

## 4. Freshness / cảnh báo (WARN-only, không BLOCK — theo đúng nguyên tắc H2/breadth-probe đã có)

Thêm 1 check nhỏ vào `bq_freshness_check.sh` hoặc `ops_health_check.sh` (chọn 1, đề xuất
`ops_health_check.sh` vì đây không phải BQ): mốc cuối `deposit_rate_vn_events.csv` (hoặc
`DEPOSIT_EVENTS` nếu CSV chưa tồn tại) quá **45 ngày** kể từ `collected_date`/mốc cứng cuối →
WARN "deposit-rate proxy đã X ngày chưa refresh, dùng cho rating_8l tilt sống + Pillar A′ nếu
được wire". WARN-only vì đây là input tilt nhỏ (±0.03), không phải money-path trực tiếp.

## 5. Trả lời "4 câu hỏi" của `cron_registry.md` (chuẩn bị sẵn cho khi duyệt cài)

1. **Đọc gì, vintage nào?** Web external (best-effort, có thể fail) + xác nhận người — KHÔNG
   phải BQ/cache.
2. **Nguồn tươi lúc nào?** Big-4 posted rate đổi bất thường (không lịch cố định), thường đầu
   tháng — routine chạy đầu tháng là hợp lý, không cần T thật trong ngày.
3. **Job cần T hay T-1?** Không cần T chính xác — đây là input tilt tần suất tháng, sai lệch vài
   ngày không ảnh hưởng (khác SBV/DT5G cần T).
4. **Ai tiêu thụ, deadline?** `rating_8l.py` (tilt sống 17:45 ICT hàng ngày, đọc giá trị BẤT KỲ
   lúc nào có sẵn — không có "deadline" cứng, chỉ càng mới càng đúng) + Pillar A′ nếu được wire
   sau này (đọc `dep_chg6m` — cần chuỗi liên tục, không được có lỗ hổng dài).

## 6. Không làm gì trong đề xuất này

- KHÔNG tự cài crontab.
- KHÔNG sửa `deposit_rate_vn.py`/`rating_8l.py` ngay (chỉ diff đề xuất ở §1, chờ duyệt).
- KHÔNG tự dựng scraper 4 ngân hàng (Lớp B) — Lớp A đủ cho nhu cầu hiện tại (tilt nhỏ + input
  Pillar A′ đang ở giai đoạn pre-registered, chưa GO).
- KHÔNG động vào `top10` ngoài Big-4 — đúng kết luận đã chốt trong plan gốc (§2.3): không có
  dữ liệu per-bank lịch sử, không đáng dựng lại.

## 7. Bonus — CPI: đã có sẵn `cpi_vn.py`, cùng gap vận hành

Trong lúc làm §2/§3, phát hiện `cpi_vn.py` (repo root) đã tồn tại từ 2026-07-06 — CPI YoY Việt
Nam 2 tầng (Tier 1 THẬT từ NSO chart-embed 2025-06→2026-06, Tier 2 proxy nội suy trước đó). Đã
báo trong finding chính + thêm registry entry. Cùng vấn đề: fetch tay 1 lần, không cron. Nếu
Taylor cần "lãi suất huy động thực" (deposit − CPI) cho Pillar A′/nghiên cứu khác, CPI này dùng
được ngay — không cần tự dựng lại. Routine tháng ở đây (§3) có thể mở rộng thêm 1 bước fetch NSO
chart-embed (đã có code mẫu ngay trong `cpi_vn.py` docstring) nếu muốn gộp chung — đề xuất riêng
sau nếu Taylor xác nhận cần, KHÔNG mở rộng phạm vi job này thêm.
