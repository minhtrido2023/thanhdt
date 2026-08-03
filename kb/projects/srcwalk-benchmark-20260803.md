# Benchmark `srcwalk` vs `grep` — 2026-08-03

> Status: XONG. Kết luận đã wire vào `WorkingClaude/CLAUDE.md` § Code navigation,
> `kb/coding_guidelines.md` §18b, 8 file `agents/*/CLAUDE.md`.
> Script + dữ liệu thô tái lập được: `agents/Mike/srcwalk_bench/`.

## Vì sao có benchmark này
Sáng 2026-08-03 Mike wire srcwalk toàn fleet kèm kết luận "srcwalk thay Read/grep làm mặc định" —
dựa trên **N=1 symbol (`filter_lag_rating_orders`) và N=1 file (`risk_monitor.py`)**. User bác:
*"phải benchmark diện rộng, không có được kết luận sơ sài."* Đúng — đó là lỗi §18/`quant-research`
cấm (khai N là số sự kiện độc lập, không phải số dòng). Benchmark này thay thế kết luận đó.

## Thiết kế
- **Trọng tài độc lập**: ground truth dựng bằng `ast` của Python — không dùng srcwalk, không dùng
  grep. Call site phân giải theo **import thật** (`from m import x [as a]` → `a(...)`;
  `import m` → `m.x(...)`), tức mạnh hơn cả 2 công cụ đang đo. Sanity check: tái lập đúng 4 call
  site của `filter_lag_rating_orders` (khớp cả grep lẫn srcwalk depth-1).
- **Universe**: 2.337 file `.py` (2.321 parse được, 16 lỗi cú pháp), 2.975 tên top-level,
  **1.984 tên có định nghĩa duy nhất** → khung mẫu.
- **Mẫu**: N=200 symbol bốc ngẫu nhiên (seed 20260803) + N=150 file cho tác vụ đọc.
- **3 tác vụ**: tìm định nghĩa · tìm call site · đọc file. Chấm precision/recall/F1 ở 2 mức
  (exact `(file,dòng)` và file-level — chênh nhau <0,003 nên không phải vấn đề quy kết dòng).
- **Thống kê**: bootstrap 5.000 lần, CI 95%, so sánh GHÉP CẶP trên cùng symbol.
- **2 chế độ scope** để tách "lỗi công cụ" khỏi "cạm bẫy cách dùng": `--scope .` (dùng tự nhiên)
  vs `--scope <thư mục top-level chứa định nghĩa>` (dùng cẩn thận).

## Kết quả 1 — TÌM KIẾM: grep thắng, có ý nghĩa thống kê

| So sánh ghép cặp | Δ F1 (grep − srcwalk) | CI 95% | Kết luận |
|---|---|---|---|
| Call site, file srcwalk thấy được (N=154) | **+0,062** | [+0,010, +0,115] | grep thắng |
| Call site, `--scope .` như dùng tự nhiên (N=200) | **+0,238** | [+0,174, +0,302] | grep thắng |
| Tìm định nghĩa, file thấy được (N=154) | **+0,052** | [+0,015, +0,093] | grep thắng |

Chi phí kèm theo (tìm định nghĩa): grep **19 token / 0,053s** vs srcwalk **472 token / 0,304s**.

**Bỏ sót hoàn toàn (trả 0 dù có caller thật)** — chỉ số nghiêm trọng nhất:

| | tỉ lệ | CI 95% |
|---|---|---|
| srcwalk `--scope .` | 30,2% | [23,6%, 36,8%] |
| srcwalk scope đúng | **8,2%** | [4,4%, 12,6%] |
| grep | **0,0%** | [0,0%, 0,0%] |

Ca điển hình `build_obs` (`agents/Taylor/deal_quality_score_backtest.py`): call site nằm ở dòng 211
trong CÙNG file với định nghĩa dòng 148, không alias, không dynamic — srcwalk vẫn báo "no call sites
found". Trả lời sai thì phát hiện được; trả lời rỗng thì không.

## Kết quả 2 — Cạm bẫy `.gitignore` (phát hiện mới, tác động lớn nhất)
`.gitignore:107` ignore `WorkingClaude/mike/` (vì `mike/` là nested repo). srcwalk **tôn trọng
ignore file khi discovery** ⇒ **1.047/2.337 = 44% file `.py` vô hình**, gồm toàn bộ code fleet.
`srcwalk overview --scope .` không liệt kê `mike/`.

| 46 symbol thuộc `mike/` | F1 call site | F1 định nghĩa |
|---|---|---|
| srcwalk `--scope .` | **0,065** | **0,000** |
| srcwalk `--scope mike` | 0,978 | 1,000 |
| grep | 0,921 | 0,978 |

→ **Luôn `--scope` vào thư mục chứa code.** Đọc file tường minh (`srcwalk mike/foo.py`) KHÔNG bị
ảnh hưởng — chỉ discovery bị.

## Kết quả 3 — Dose-response: srcwalk thắng ở tên mơ hồ

| Tên được nhắc ở | n | srcwalk P [CI] | grep P [CI] | sw tok | gp tok |
|---|---|---|---|---|---|
| 1 file | 115 | 0,913 [0,861–0,965] | **1,000** | 121 | **37** |
| 2–3 file | 18 | 0,944 [0,833–1,000] | **0,972** | 158 | **62** |
| 4–10 file | 10 | 0,708 [0,408–0,908] | 0,804 [0,588–0,980] | 158 | 173 |
| **>10 file** | 11 | **0,844 [0,623–1,000]** | **0,459 [0,223–0,715]** | **200** | **740** |

Precision grep sụp 1,00 → 0,46 khi tên phổ biến, chi phí nổ 37 → 740 token. Đó là dải duy nhất
srcwalk có lợi thế thật ở tìm kiếm — nhưng chỉ **11/154 = 7%** số symbol. Dải 4–10 srcwalk còn thua
(n=10, CI rộng, không đọc quá kỹ).

## Kết quả 4 — ĐỌC FILE: srcwalk thắng áp đảo, không ngoại lệ

| | Giá trị |
|---|---|
| Tiết kiệm token trung bình | **88,8%** CI[86,5%, 90,7%] |
| Trung vị | 92,3% |
| File srcwalk ĐẮT HƠN `Read` | **0/150** |
| Recall cấu trúc (top-level def còn trong outline) | **95,7%** CI[92,5%, 98,4%] |
| File giữ đủ 100% symbol | 141/150 (94%) |

Ổn định theo kích thước: <100 dòng tiết kiệm 76%, 100–300 → 91,5%, 300–1k → 94,0%, >1k → 95,4%.
150/150 file cho ra chế độ `[outline]` thật (không rơi về raw preview).

## Kết luận wire vào production

| Việc | Công cụ |
|---|---|
| Đọc / nắm cấu trúc file, đọc 1 đoạn, 1 hàm, orient thư mục | **`srcwalk`** |
| Tìm định nghĩa, tìm call site | **`grep`** |
| Tìm tên rất phổ biến (`main`/`run`/`load`) | `srcwalk discover --scope <dir>` |
| Bash, `.json`, `.sql`, `.csv` | `grep`/`Read` |

Giữ nguyên 3 cấm đoán từ pilot 2026-08-01 (đã verify lại trên v1.3.0, VẪN CÒN): `trace --depth ≥2`
+ khối "impact"; danh sách symbol của `review` (nguyên nhân: gắn hunk theo phép BAO HÀM, nên hunk
thêm hàm mới luôn vắt ngang biên symbol → `file-level`); bash không parse được.

## Giới hạn của benchmark này (khai báo, không giấu)
1. **Chỉ hàm/class top-level có định nghĩa duy nhất** (1.984/2.975 tên). Method bị loại vì phân giải
   `obj.method()` cần suy luận kiểu — ngoài tầm cả 2 công cụ VÀ `ast`; đưa vào sẽ biến ground truth
   thành phỏng đoán.
2. **16/2.337 file không parse được** — loại khỏi ground truth.
3. **grep đạt recall 1,000 nhờ call site chứa nguyên văn tên hàm.** Ở codebase dùng nhiều
   `from m import x as y`, recall grep sẽ thấp hơn — mẫu này gần như không có alias.
4. Ground truth không xử lý `import *`, dynamic dispatch, `__getattr__`, re-export nhiều tầng.
5. **Một repo, một ngôn ngữ (Python).** Bash không đo được (srcwalk không hỗ trợ). Không suy rộng
   sang repo khác mà không đo lại.
6. Chưa đo: `context`, `deps`, `compare`, `assess` — nằm ngoài 3 tác vụ chính.

## Tái lập
```bash
cd mike/agents/Mike/srcwalk_bench
python3 gt_build.py      # ~70s — dựng ground truth AST
python3 run_bench.py 200 # ~6 phút
python3 analyze.py       # bảng tổng hợp
python3 stats.py         # bootstrap CI + tác vụ đọc file
```
Khi lên version srcwalk mới: chạy lại TRƯỚC khi nới bất kỳ cấm đoán nào — đừng tin changelog.
