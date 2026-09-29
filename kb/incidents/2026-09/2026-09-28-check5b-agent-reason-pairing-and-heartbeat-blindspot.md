# 2026-09-28 — Check 5b ghép NGƯỢC agent↔lý do, và mù ca bản bị chặn CHÍNH LÀ heartbeat

**Phát hiện:** `ops_health_check.sh --account ZaloPay` (01:20Z) báo 2 bản ghi cách ly trong
24h, `Agent: ['Taylor', 'Wags']. Lý do: ['nhận 7 tham số (tối đa 5) — word-split',
'payload bắt đầu bằng { nhưng KHÔNG phải JSON hợp lệ']`. Dispatch job
`Winston_20260928_012008`.

## Sự thật: KHÔNG mất event nào (ca 20/20 tự lành ≤60s)

| idx | ts bị chặn | agent | nguyên nhân THẬT | retry trên bus |
|---|---|---|---|---|
| 20 | 2026-09-27T03:25:54Z | Wags | word-split THẬT (argc=7) | `947cd7ea` +31s, cùng topic `cq-2026-09-27-wags-autodispatch` |
| 22 | 2026-09-27T08:58:12Z | Taylor | JSON viết tay THIẾU `}` cuối (argc=5) | `25c7f402` +10s, cùng trace |

Word-split của Wags tái dựng được chính xác từ argv: payload có 2 dấu `'` lẻ — dấu thứ nhất
đóng chuỗi ngay sau `kiểm` (⇒ `argv[4] == "tra"`), dấu thứ hai mở lại từ `auth/quota` đến hết.
Bản retry đã BỎ DẤU TIẾNG VIỆT nên không còn `'` ⇒ qua. Call site là lệnh Bash ad-hoc, không có
script committed để vá. Đã đánh dấu sidecar cả hai.

## Lỗi THẬT #1 — hai tập `sorted()` độc lập in cạnh nhau, người đọc ghép theo vị trí

`_who = sorted({agent})` và `_why = sorted({reason})` là 2 tập RỜI, sắp xếp bằng 2 khoá khác
nhau. Với ≥2 agent và ≥2 nguyên nhân, cặp mà người đọc suy ra gần như chắc chắn sai — hôm nay
sai CẢ HAI (Taylor↔word-split, Wags↔JSON-hỏng; thực tế ngược lại). Thông điệp còn tự dặn "đọc
đúng `Lý do` dưới đây, đừng mặc định là lỗi quote" ngay phía trên một cặp sai. Đây là §29: khẳng
định một quan hệ mà code chưa hề đo. Sửa: một dòng `"<agent>: <lý do>"` cho MỖI bản ghi.

## Lỗi THẬT #2 — loại mọi `event_type=="heartbeat"` làm mù ca heartbeat bị chặn

Bản vá 2026-09-17 (`e5825e11`) loại heartbeat để watcher không che mất bản retry thật. Nhưng
khi bản BỊ CHẶN chính là một heartbeat của agent (ca Taylor hôm nay), bộ lọc đó loại luôn bản
retry hợp lệ ⇒ nếu đó là bản ghi cách ly DUY NHẤT, checker sẽ in "khả năng cao event MẤT THẬT".
Hôm nay tai nạn không nổ ra chỉ vì bản ghi của Wags cũng nằm trong cùng cửa sổ 24h.

Sửa bằng bit ĐO ĐƯỢC chứ không suy từ `event_type`: heartbeat của watcher tự khai
`payload.source == "watcher"` — loại theo bit đó; còn `event_type=="heartbeat"` chỉ bị loại khi
bản bị chặn KHÔNG phải heartbeat.

## Verify

`bin/ops_health_check_rejected_selfcheck.py` +5 assertion, toàn bộ PASS dưới `$DNA_PYEXE` ở
`env -u TZ` / `America/New_York` / `UTC`. Mutation trên HEAD cũ giết 4/5 (assertion thứ 5 là
guard-rail chống hồi quy watcher, đúng là phải xanh ở cả hai bản). `ops_health_check.sh
--account ZaloPay` chạy thật: check 5b ✅. Commit `f126e397`.

## Bài học (lần 3 cùng khuôn với 55b3f34c, 498466d9, e5825e11)

Mọi dòng chẩn đoán checker in ra phải là **phép đo trên chính dữ liệu của ca đó**. Ở đây khuôn
lỗi mới là **trình bày**: dữ liệu per-record đúng, nhưng bị gộp thành 2 tập rời rồi in cạnh
nhau — mất quan hệ, và người đọc tự bịa lại quan hệ sai. Gộp/khử trùng lặp là một dạng khẳng
định chưa đo, ngang với văn xuôi đoán mò.
