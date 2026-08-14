# Việc E vòng 4 — vá lỗ hổng "phiên cron bị LỠ" của `corp_action_daily.py`

**Job** `Taylor_20260813_115210` · **2026-08-13** · trước đó: vòng 3 CONFIRMED (`Taylor_20260813_104511`,
commit `f844b800`). Đây là khuyến nghị **#5** của quant-skeptic (nêu vòng 2, nhắc lại vòng 3 là
*"the real remaining exposure"*). Crontab **VẪN CHƯA CÀI** — đây là vòng cuối trước khi trình Mike.

## Lỗ hổng

`triggered_today(asof)` chỉ hỏi BQ cho ĐÚNG ngày hôm nay. Vòng xác nhận (`confirm_prior_triggers`,
vòng 3) chỉ theo cái **ĐÃ được ghi**. Ghép lại: một lượt cron không chạy được (crash, timeout, máy
tắt) làm sự kiện của ngày đó **biến mất vĩnh viễn** khỏi hệ, không để lại dấu vết — và không có
đường nào quay lại.

Ca **M0** trong bộ selfcheck là bằng chứng lỗ hổng có thật, không phải suy diễn: cùng một snapshot,
`backfilled=None` (tức bản trước bản này) cho **đúng 0 dòng** cho sự kiện của phiên bị lỡ.

## Đã làm — LỚP 7, 3 hàm mới, tất cả nối vào bộ máy CŨ

| Hàm | Việc |
|---|---|
| `missed_trading_days(prev_asof, asof, deferred)` | ngày giao dịch nằm HẲN giữa 2 mốc, theo **lịch giao dịch** (`trading_bot.vn_market`), + hàng HOÃN của lượt trước |
| `backfill_missed(days, fetch, max_days)` | chạy lại **đúng `_events_on_sql`** (qua `_all_events_on`) cho từng ngày lỡ |
| `pending_items(..., backfilled=, asof=)` | thả kết quả vào **chính** danh sách chờ đã có |

**Không có nhánh phân loại thứ hai.** Sự kiện backfill đi qua nguyên bộ máy đã CONFIRMED ở vòng 3
(ghép theo `id` → khoá nội dung, CONFIRMED/CANCELLED/STILL_ANNOUNCED/VANISHED, đồng hồ `n_checks`,
`carry_forward`, ngưỡng `UNRESOLVED_TIMEOUT`). Giá phải trả: một truy vấn xác nhận thứ hai cho cùng
ngày (`include_cancelled=True`) — chỉ ở đúng nhánh hiếm "vừa lỡ phiên".

### Bốn quyết định thiết kế đáng soi

1. **Mốc là ARTIFACT (`prior_snapshot`), không phải `state.last_run`.** `stale_streak()` ghi
   `last_run` NGAY sau cổng freshness, tức **trước cả nhánh feed DEAD** ⇒ state nhận ngày của một
   lượt chạy không publish gì. Lấy state làm mốc = nhảy qua ngày đó vĩnh viễn — đúng cái lỗ hổng
   đang vá. Ca **M29** chứng minh bằng máy. Hệ quả tốt kèm theo: lượt chạy fail gate (ghi
   `*_FAILED.json`, mà `prior_snapshot` bỏ qua) **tự động** thành "phiên bị lỡ" của lượt sau,
   không cần cờ riêng.
2. **`include_cancelled=False` khi backfill.** Sự kiện đã HUỶ trong khoảng bị lỡ thì không có gì
   để ghi — ta chưa từng công bố nó. Đây là chỗ backfill **tốt hơn** một lượt chạy đúng ngày (lượt
   đúng ngày ghi bản `announced` rồi hôm sau phải rút lại).
3. **Trần `BACKFILL_MAX_DAYS = 10` + hàng HOÃN, không có cap im lặng.** 10 = 2 tuần giao dịch, dài
   hơn mọi kỳ nghỉ VN (Tết ≈ 5-6 phiên) nên nghỉ lễ không bao giờ chạm trần. Ngày vượt trần **hoặc
   truy vấn lỗi** vào `backfill_deferred_days` của snapshot → lượt sau nhặt lại (10/lượt) ⇒ hàng
   đợi tự rút. Ca M15/M16/M27/M28.
4. **`first_seen_asof` = NGÀY CHẠY, không phải ngày sự kiện.** Đồng hồ `PENDING_MAX_CHECKS=5` đếm
   số LƯỢT ĐÃ KIỂM; lấy ngày sự kiện làm mốc thì món backfill của 6 phiên trước hết hạn ngay lượt
   đầu và không bao giờ được theo tới lúc ngã ngũ. Ca M20.

### Cảnh báo — TÁCH khỏi cảnh báo freshness

`⏭️ **CRON BỊ LỠ n PHIÊN**` (Telegram, vì đây là sự cố **hạ tầng của chính mình**) ≠ `🕒 corporate_action
không nạp thêm gì n ngày` (bảng nguồn im lặng). Gộp lại thì một sự cố của mình đọc ra như một ngày
yên ả của vendor. Bản render thật (chạy `alert=True`, `notify` bị chặn):

```
⏭️ **CRON BỊ LỠ 1 PHIÊN** (snapshot gần nhất 2026-08-13 → nay 2026-08-17): 2026-08-14.
   Đã backfill 1/1 ngày, 6 sự kiện; không mã nào đang giữ dính.
   Kiểm vì sao cron không chạy trước khi tin số của khoảng này.
🕒 `corporate_action` không nạp thêm gì 3 ngày liên tiếp …          ← dòng RIÊNG, vẫn còn
```

## Bằng chứng

**Selfcheck 127/127 hermetic** (từ 97 — **+30 ca**), **134/134** với `--live`. Không hồi quy: 4 cơ
chế đã CONFIRMED (khoá trùng theo từng sự kiện, carry-forward nhiều lượt, freshness gate, bất biến
số CP + đối soát bq_admin) đều xanh nguyên.

**4 ca đối chứng bắt buộc — đủ cả 4:**

| Ca | Yêu cầu | Ca selfcheck |
|---|---|---|
| (a) | không lỡ phiên nào ⇒ hành vi y hệt | M1, **M2** (T2 sau T6, cách 3 ngày lịch, 0 phiên lỡ), **M3** (qua lễ 02/09), M10 (0 truy vấn) |
| (b) | lỡ đúng 1 phiên ⇒ backfill đúng 1 ngày | M5, M11 |
| (c) | lỡ 3 phiên liên tiếp ⇒ đủ 3, không sót không thừa | M6, M7 (vắt qua cuối tuần), M12, M13, **M24** (đầu-cuối) |
| (d) | chạy lại 2 lần ⇒ không ghi trùng | M21, M22, M23, **M25** |

**Mutation 8/8 bị giết** (`agents/Taylor/mutate_missed_run.py`): đếm bằng ngày lịch (M-A →
M2,M3,M4,M6,M7,M24) · backfill hỏi ngày hôm nay (M-B → M13,M24,M25,M26) · bỏ hàng HOÃN (M-C →
M9,M16,M28) · nạp backfill trước hàng treo (M-D → M22) · `first_seen_asof` = ngày sự kiện (M-E →
M20,M22) · bỏ trần (M-F → M15,M16) · lỗi truy vấn ném ra ngoài (M-G) · bỏ nhãn `backfilled` (M-H).

**Chạm BigQuery THẬT (không bơm fixture):** `backfill_missed(missed_trading_days("2026-08-13",
"2026-08-17"))` moi lại đúng **6 sự kiện thật** của phiên 2026-08-14 (DQC/HRB/NQB/PSW/SGR/VSH),
khớp từng `id` với truy vấn trực tiếp ngày đó.

**Đầu-cuối, 2 lượt `run()` liên tiếp trên dữ liệu production** (`--asof 2026-08-17 --dry-run`):
`gate-5` báo 1 phiên lỡ → backfill 6 sự kiện → cả 6 chảy vào vòng xác nhận với nhãn
`backfilled=True`, mang sang lượt sau `n_checks=1`; 4 sự kiện của 08-13 đi đường CŨ (`backfilled=
False`) song song, không lẫn. Lượt 2: snapshot **giống hệt từng khoá** (`KHONG KHAC GI`, sau khi bỏ
`generated_at`/`stale_streak`/`selfcheck`).

## Phát hiện ngoài phạm vi được giao — 1 mục, đã tự xử lý

**Bẫy harness mutation: pyc cũ được dùng lại ⇒ chấm điểm nhầm mutation TRƯỚC đó.** Mutation M-A và
M-B tình cờ cho file **đúng bằng nhau (78.290 byte)** và được ghi trong **cùng một giây** — Python
coi `.pyc` là còn hợp lệ theo `(mtime giây, kích thước)` nên lượt M-B nạp lại bytecode của M-A.
Harness in ra "8/8 bị giết" (đúng) nhưng **quy sai ca đỏ** cho M-B. Phát hiện vì hai mutation khác
nhau cho danh sách ca đỏ y hệt nhau — dấu hiệu duy nhất. Thêm một lớp: `inspect.getsource()`
**KHÔNG** phát hiện được (nó đọc file NGUỒN, không phải code đang chạy) — dùng nó để "xác minh
mutation đã vào" cho kết quả xanh giả. Đã vá: dọn `__pycache__` + `PYTHONDONTWRITEBYTECODE=1` giữa
các mutation, chạy lại → attribution đúng, vẫn 8/8. Bài học đúng họ với §23/`verify-before-done`,
đáng cân nhắc đưa vào `coding_guidelines` nếu có bộ mutation thứ hai.

## Rủi ro tồn dư — công bố, KHÔNG tự nhận đã đóng

1. **Backfill KHÔNG dựng lại `cash_dividend_today` của ngày đã lỡ.** Khối đó mang
   `holders_qty`/`accrual_gross_vnd`, mà `read_positions` chỉ đọc được artifact MỚI NHẤT ⇒ dựng
   accrual quá khứ bằng vị thế hôm nay là gán tiền cho một danh mục không phải danh mục lúc chốt
   quyền. **Cố ý không làm** (sai lặng lẽ tệ hơn không có); cái được ghi là SỰ KIỆN, đủ để
   `dividend_adjusted_return.py` (nguồn chuẩn tắc §21) tính đúng sau, cộng dòng cảnh báo liệt kê mã
   **đang giữ** dính sự kiện trong khoảng lỡ. Nếu muốn accrual đúng cho ngày quá khứ thì cần vị thế
   point-in-time — việc riêng, chưa làm.
2. **`FEED_DEAD_DAYS=5` và phân tầng alert vẫn CHƯA kiểm chứng được** (bảng chỉ có 1 ngày
   `ingested_at`) — nguyên văn rủi ro tồn dư đã nêu vòng 2, không đổi.
3. **`BACKFILL_MAX_DAYS=10` chọn theo lập luận (dài hơn kỳ nghỉ dài nhất), không theo số đo** —
   chưa từng có ca cron chết dài ngày để hiệu chỉnh. Đây là ngưỡng CẢNH BÁO/tải, không phải ngưỡng
   tiền: sai thì chỉ đổi số lượt để hàng đợi rút cạn.

## Khi Mike cài crontab (giữ nguyên yêu cầu vòng 3, thêm 1)

- **alert-only 5-10 phiên** trước khi coi là chốt, log `MAX(ingested_at)` mỗi lượt.
- **Mới:** phiên đầu tiên sau khi cài, kiểm `missed_runs.days_missed` phải **RỖNG**. Nếu không rỗng
  (vì snapshot gần nhất là `corp_action_daily_2026-08-13.json` do chạy tay), đó là backfill ĐÚNG
  chứ không phải lỗi — nhưng phải đọc dòng `⏭️` để xác nhận số ngày khớp với thực tế.

## File

- `mike/bin/corp_action_daily.py` — LỚP 7 (+159/−9)
- `mike/bin/corp_action_daily_selfcheck.py` — `t_missed_runs()`, 30 ca mới
- `mike/agents/Taylor/mutate_missed_run.py` — harness mutation (chạy tay, không phải cron)
