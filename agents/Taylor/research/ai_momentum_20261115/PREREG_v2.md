# PREREG v2 — thay đổi so với v1 (md5 4ed34b38, commit 5d3284d0b)

Phiên bản: v2 · 2026-11-15 · Taylor (job `Taylor_20261115_154607`, P1-BUILD). v1 KHÔNG sửa tại chỗ. Commit v2 này TRƯỚC mọi lần chạy
paper-forward. Chưa có sự kiện forward nào được chấm trước v2 (P0 chỉ có dry-run hồi tố, không tính vào N). **Không đổi ngưỡng sự kiện**
(mom20/idio20/volr/liq/rating/cooldown giữ y v1). md5 các file khoá: `PREREG_v2.md5`.

## Thay đổi (mỗi mục: gì · vì sao)
1. **Prompt M1 → `prompt_M1_v2.md` (+ `prompt_M1_rebuttal_v2.md`), schema → `schema_M1_v2.json`.** Khoá `claim/source/date` đúng schema;
   `additionalProperties:false` (cấm trường thừa); `event_id` tuỳ chọn (script tự gán — M1 hay quên); vòng phản biện có thêm
   `rebuttal_accepted/rejected`. Vì sao: dry-run P0 lệch tên khoá 10/10 (`ref/note`), 1/10 thêm trường thừa. Kiểm chứng P1: chạy thật 2 sự kiện retro,
   0/2 lỗi schema sau khi bỏ `event_id` khỏi required (trước đó 2/2 lỗi lần đầu vì thiếu `event_id`).
2. **Gói có thêm `sector_context`** (return 20 phiên trung vị route 8L, `route_n`, phân vị của mã trong route, ICB + trung vị ICB, VNINDEX 20 phiên).
   Vì sao: P0 không bao giờ chọn được SECTOR_MACRO (gói không có dữ liệu ngành). Chỉ từ dữ liệu ≤ T.
3. **Lọc tin theo ngày NẠP, không chỉ ngày công bố**: `public_date ∈ [T−120, T]` ∧ `DATE(ingested_at, 'Asia/Ho_Chi_Minh') ≤ T`; ghi cả
   `public_date`, `public_datetime`, `ingested_date`. Vì sao: PREREG v1 §6 đã nói tin nạp sau T không dùng được, nhưng gói P0 chỉ lọc `public_date`.
   **Hệ quả đo thật**: ~98,8% tin stock_news có `ingested_at` = 2026-09-13 (backfill) ⇒ gói retro T < 2026-09-13 gần như KHÔNG có tin
   (retro 2026-08-05: `n_news=0` cho cả HII và VNZ). Retro vì vậy KHÔNG đại diện cho độ phủ tin của live — chỉ dùng gỡ prompt/quy trình.
4. **N của look = số sự kiện ĐÃ CHẤM có view_20s cuối CÓ HƯỚNG (CONT/REV)** (`N_dir_scored`), không phải mọi sự kiện. L1 = 80, L2 = 150 theo N_dir.
   FINAL = `N_scored ≥ 250` (mọi sự kiện) hoặc 24 tháng lịch sau sự kiện đầu. Vì sao: M1 dry-run NO_VIEW 5/10 @20s; sự kiện NO_VIEW không mang thông tin
   cho T1 nên đếm chúng làm N lạc quan (killer objection của quant-skeptic P0). Hệ quả thời gian — xem §Thời gian dưới. Mẫu của mỗi look ĐÓNG BĂNG =
   N_dir đầu tiên theo ngày T (không đổi khi N lớn thêm).
5. **Làm rõ (v1 im lặng)**: (a) T3: `hit` của NO_VIEW = 0 (không trúng); p bằng sign-flip theo khối tháng trên chênh hit cặp (10.000 lần, seed 20261115);
   (b) sự kiện `m1_status=FAIL` (2 lần sai schema/lỗi gọi) loại khỏi T1–T3 nhưng ĐẾM và báo trong G-proc (tránh loại chọn lọc im lặng);
   (c) scorer giữa các mốc chỉ in N, N_dir và G-proc (không có khoá `effects` — selfcheck bắt);
   (d) hàng đợi áp **theo ngày, nhân quả**: mỗi ngày còn `10 − (số đã xử lý ở các ngày trước trong tuần ISO)` suất, chọn `liq_bn` giảm dần TRONG ngày;
   sự kiện đầu tuần thanh khoản thấp có thể chiếm suất của sự kiện thanh khoản cao cuối tuần (v1 ghi "ưu tiên liq giảm dần" cấp tuần — không làm được nhân quả);
   (e) lịch sử cooldown = `events.csv` R4 (< T) ∪ sổ JSONL (kể cả `skipped_capacity`).
6. **Thực thi**: M1 = Claude Sonnet (alias `sonnet`, ghi model resolve vào `usage.models`), effort medium, **phiên trần**: cwd tmp rỗng, `--setting-sources ""`,
   `--system-prompt <prompt>`, `--disable-slash-commands`, MCP rỗng, `--no-session-persistence`; `--tools ""` ở retro, `--tools WebSearch` ở live; thử lại 1 lần
   khi sai schema. `live` chỉ cho T == hôm nay (ICT); ngày bù/lùi → `retro` ledger riêng, không bao giờ gộp vào N chính (WebSearch sau T = rò rỉ).
7. **M2**: qua `m2_adapter(stage, packet, m1)` — hiện fail-open (`m2_status=FAIL`, `m2_reason=adapter_not_enabled`) cho tới khi Wags xong chế độ prompt riêng
   của `second_opinion.sh`. Sự kiện M2 FAIL vẫn chấm T1/T2, loại T3 (như v1 §3). **Toàn bộ N forward chạy trước khi M2 sống sẽ không có T3** — user cần biết.

## Thời gian tới look (đo bằng `power_sim_directional.py`, `power_sim_directional.out`; N = N_dir; +3 tháng chờ ex60)
Ở `p_dir`=40% (M1 dry-run: NO_VIEW 5/10 @20s — mẫu 10, ước lượng rất thô; chưa đo trên mẫu lớn):
| Nhịp sự kiện | N_dir=80 | N_dir=150 | FINAL N_scored=250 |
|---|---|---|---|
| chuẩn, TB 26 tháng (13,2/th) | 15,2 th | 28,4 th | 18,9 th |
| chuẩn, 6 tháng gần (6,3/th) | 31,7 th | 59,5 th | 39,7 th → trần 24 th chặn |
| nới ×2 (mom15/idio10/volr1,2/liq1; 21,5/th) | 9,3 th | 17,4 th | 11,6 th |
| nới ×2, 6 tháng gần (12,3/th) | 16,3 th | 30,5 th | 20,3 th |
Power ex20 T1 (Δ8pp / Δ12pp, nhóm A = CONT chiếm ~½ sự kiện có hướng): N_dir=80 → 0,75 / 0,98; N_dir=150 → 0,99 / 1,00 (p_dir=0,4).
Số này **lạc quan** về cấu trúc: mô hình giả định view độc lập với outcome và CONT 50% — M1 thực tế có thể nghiêng CONT/UNKNOWN. Đọc thẳng: với ngưỡng v1
và nhịp 6 tháng gần, FINAL 24 tháng sẽ kết thúc ở N_scored ≈ 150 (≈ N_dir 60, chưa tới L1) — **gần chắc chắn "không kết luận"**; cột FINAL = 250/nhịp (N_scored, mọi sự kiện), chưa trừ ~3 tháng chờ ex60.
## Đề xuất để USER quyết (tôi KHÔNG tự làm)
Nới ngưỡng sự kiện ×2 (mom15/idio10/volr1,2/liq1, đo ở P0 là 560 sự kiện/26 tháng) làm FINAL khả thi trong ~12–20 tháng thay vì không bao giờ,
đổi lại: sự kiện "yếu" hơn, nhiều mã lặp (cần cụm theo mã + tháng — chưa có trong §4), và PREREG sẽ là v3 với universe khác hẳn. Phải quyết TRƯỚC khi chạy forward.
