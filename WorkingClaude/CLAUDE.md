# CLAUDE.md

Chỉ dẫn LUÔN được nạp cho mọi phiên và mọi agent trong repo này. Vì vậy nó chỉ chứa **LUẬT** —
thứ đổi việc bạn làm lần sau. Diễn giải, số liệu benchmark, changelog và schema chi tiết nằm ở
file được trỏ tới: đọc khi cần, không nạp mặc định.

## Code navigation — `srcwalk` để ĐỌC, `grep` để TÌM

Chia theo VIỆC, không theo sở thích. Đã đo, không phải phỏng đoán (N=200 symbol + N=150 file,
ground truth dựng độc lập bằng `ast`, bootstrap 95% CI). Số liệu đầy đủ + cách tái lập:
`mike/kb/projects/srcwalk-benchmark-20260803.md`.

| Việc | Dùng |
| --- | --- |
| Đọc / hiểu một file | `srcwalk <path>` — trả outline thay vì bytes, −89% token |
| Đọc một đoạn hoặc một symbol | `srcwalk <path>:120-160`, `--section <sym>` |
| Định hướng trong thư mục lạ | `srcwalk overview --scope <dir>` |
| **Tìm định nghĩa** | `grep -rnE "^\s*(def\|class) NAME\b"` |
| **Tìm call site** | `grep -rnE "\bNAME\s*\("` |
| Tìm tên RẤT phổ biến (`main`, `run`, `load`) | `srcwalk discover NAME --scope <dir>` |

`srcwalk` v1.3.0 ở `~/.local/bin`, skill `~/.claude/skills/srcwalk/`. Chạy `srcwalk guide` một
lần mỗi phiên trước khi dùng nghiêm túc. Ngôn ngữ có cấu trúc: Python, TS/JS, Go, Rust, Java,
C/C++, C#, Ruby, PHP, Swift, Markdown.

**grep vẫn là mặc định để TÌM.** Nó thắng cả hai tác vụ tìm kiếm với CI không chồng lấn, rẻ hơn
3-25× token, và — lý do quan trọng nhất — **chưa bao giờ trả rỗng một cách im lặng**.

**Ba cái bẫy, đều đo trên chính repo này:**
1. **Luôn `--scope` đúng thư mục chứa code. Đừng bao giờ tin `--scope .`** — `.gitignore:107`
   ẩn `WorkingClaude/mike/` (nested repo) = **44% file `.py` của repo, gồm TOÀN BỘ fleet**.
   Trên symbol nằm trong `mike/`: `--scope .` cho F1 **0,065**; `--scope mike` cho **0,978**.
   Đọc file tường minh (`srcwalk mike/foo.py`) không bị ảnh hưởng — chỉ lệnh discovery bị.
2. **Đừng bao giờ kết luận "không ai gọi hàm này" chỉ từ srcwalk.** Nó trả "no call sites" SAI
   cho **8,2%** symbol có caller thật (grep: 0%). Trả lời sai thì phát hiện được; trả lời rỗng
   thì không. Xác nhận sự vắng mặt bằng `grep`.
3. **`trace callers --depth 1` thôi**, bỏ qua khối "impact (2nd hop)" — từ hop 2 nó khớp theo
   TÊN chứ không resolve (`subprocess.run` bị tính là caller của `run`; một truy vấn trả 500
   cạnh / 121 file). Blast radius phải verify bằng `grep`.

**Không áp dụng cho:** bash (không hỗ trợ cấu trúc — `mike/bin/` có **63 `.sh` vs 46 `.py`**),
`.json`, `.sql`, `.csv`, `.md` ngắn → dùng `Read`. `srcwalk review` bỏ sót hàm MỚI THÊM (nó gán
hunk cho symbol chỉ khi hunk nằm GỌN trong symbol đó) → `git diff` mới là nguồn thay đổi chuẩn.

Output của srcwalk là bằng chứng **điều hướng cấu trúc**, không phải bằng chứng runtime — mang
theo dòng `confidence:` / `caveat:` nó in ra vào những gì bạn báo cáo.

## BigQuery (Google Cloud)

- **Project**: `lithe-record-440915-m9` · **Dataset**: `tav2_bq` (location `asia-southeast1`)
- **Auth**: `dtienthanh@gmail.com` (read-WRITE). Env nằm ở **`wc_env.sh`** — `source` nó, đừng
  tự đoán đường dẫn SDK.
- Luôn dùng `--use_legacy_sql=false`.

```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 'SELECT ...'
bq query --use_legacy_sql=false --dry_run --project_id=lithe-record-440915-m9 'SQL'   # ước phí trước khi chạy nặng
```

**Bảng** (schema cột đầy đủ: `bigquery_schema.md`; ngữ nghĩa từng cột: `bigquery_dictionary.json`
— luôn tra file này TRƯỚC khi viết filter):

| Bảng | Nội dung | Phân vùng / cluster |
| --- | --- | --- |
| `ticker` | OHLCV ngày + chỉ báo phái sinh, ~15,2M dòng, 2000-07-28→2026-06-15, ~1.272 mã | part `time` / cluster `ticker` |
| `ticker_financial` | Tài chính theo QUÝ, ~63,6K dòng, ~1.255 mã | cluster `ticker` |
| `risk_rating` | Risk rating theo quý (Beta + Dev) | cluster `ticker` |
| `ticker_1m` | Ảnh chụp ~1 tháng gần nhất — screening/eval hằng ngày | part `time` / cluster `ticker` |
| `ticker_prune` | Universe đã lọc chất lượng — training + backtest | part `time` / cluster `ticker` |

**Quy ước tên cột**: `_P0` quý hiện tại → `_P7` 7 quý trước (`_P4` ≈ 1 năm) · `_T1` 1 phiên
trước, `_T1W` 1 tuần · `_Min3Y/5Y/10Y` sàn chất lượng · `_Trailing` tổng 4 quý gần nhất ·
`_MA/_SD/_P50/_P90` trung bình / độ lệch / phân vị.

**Bốn cái bẫy, đều đã cắn thật:**
1. **Cột forward-looking (`profit_2W/1M/2M/3M` + biến thể `_center_*`) CHỈ dùng để train. TUYỆT
   ĐỐI không dùng làm filter live** — đó là nhìn trộm tương lai.
2. **Tên bảng trùng tên cột.** `GROUP BY Risk_Rating` sẽ resolve vào *bảng* `risk_rating` và trả
   về STRUCT. Luôn đặt alias cho bảng và qualify cột: `FROM tav2_bq.risk_rating AS t ... t.Risk_Rating`.
3. **`risk_rating` có dòng TRÙNG** (cùng ticker + quarter xuất hiện 2 lần) → `GROUP BY` hoặc
   `SELECT DISTINCT` khi tổng hợp.
4. **`ticker_prune` backfill tới 2000 nhưng thị trường VN mỏng thời kỳ đầu** (2006≈19 mã,
   2008≈105, 2014≈203) → tín hiệu breadth/universe chỉ có nghĩa từ ~2008; trước 2007 gần như
   không đầu tư được.

## Kiến trúc codebase

Đây là workspace phân tích chứng khoán VN, không phải project phần mềm truyền thống: không build
system, không test suite, không package. Mọi thứ chạy như script Python độc lập.

**`filter.json` — nguồn sự thật duy nhất cho logic tín hiệu vào/ra.** Quy ước khoá:
`_TenChienLuoc` = filter mua · `~TenTinHieu` = tín hiệu bán · `$TenChienLuoc` = danh sách tín
hiệu bán áp cho chiến lược đó · `Init` = khoảng ngày nền, chèn vào mọi filter mua qua placeholder
`{Init}` · `MARKET_DICT_FILTER` = filter cấp thị trường (VNINDEX). Biểu thức dùng thẳng tên cột
BQ; `Inflation_7` là hằng số lạm phát 7%/năm để quy giá trị giao dịch về VND thực.

**`gen_sql.py`** đọc `filter.json`, đổi cú pháp Python→WHERE của BigQuery, ghi cặp `.sql`+`.csv`
vào `sql_queries/`. Nó tự expand `{Init}` và tự loại điều kiện chứa cột không có trong
`ticker_1m`/`ticker_prune`.

**File dữ liệu local**: `VNINDEX.csv` (lịch sử VNINDEX đầy đủ + chỉ báo + PE, cho phân tích
offline không cần chạm BQ) · `bigquery_dictionary.json` · `filter.json` · `sql_queries/*.csv`.

**Nhóm script**: `backtest_*` (backtest chiến lược) · `analyze_*` (chất lượng tín hiệu, pattern,
market phase) · `market_*` (timing, state machine, allocation) · `score_live_signals.py` /
`universe_scan.py` (chấm tín hiệu live) · `extract_deals.py`. Tất cả cùng một khuôn: nạp dữ liệu
từ BQ hoặc CSV local → tính bằng pandas/numpy → xuất `.png`/`.csv`.

⚠️ Một số script cũ hardcode `WORKDIR` theo đường dẫn Windows (`C:\Users\hotro\...`) — di sản từ
máy cũ, còn 11 file. Máy hiện tại là Linux; đừng chép lại mẫu đó vào script mới.

## VNINDEX 5-State — PRODUCTION = **DT5G** (`macro_state_live.py`)

**5 trạng thái**: CRISIS(0%), BEAR(20%), NEUTRAL(70%), BULL(100%), EX-BULL(130%).

**Đọc trạng thái qua `get_gated_state()`, không đọc bảng thẳng.** Đó là wrapper fail-safe: chỉ
trả DT5G khi `data/macro_health.json` còn tươi (<1440 phút) và báo feed đáng tin; ngược lại
fail CLOSED về **DT4** (base + DT 4-gate, không có macro cap). Dùng cột `state`.

> ⚠️ **BẪY NGHIÊN CỨU — nhãn bảng.** Bảng không hậu tố `tav2_bq.vnindex_5state` **KHÔNG PHẢI
> DT5G**. Nó là **v3.4b BASE** (~153 transition, không DT-gate, không macro cap) và giống hệt
> từng byte `vnindex_5state_tam_quan_v34b_clean`. DT5G thật (49 transition) chỉ nằm ở
> **`tav2_bq.vnindex_5state_dt5g_live`**. Nhiều script nghiên cứu đọc bảng trống hậu tố và
> tưởng là DT5G — đây là lỗi đã xảy ra thật, không phải giả định.

**Kiến trúc, 4 tầng** (đừng đổi nếu không có chỉ đạo rõ ràng):
1. **Base** = v3.4b "Định Tâm", đọc từ BQ, warm-up từ 2014.
2. **DT 4-gate** (`DT_10_25_25`) — bộ làm mượt chính. Cam kết bất đối xứng: cần 25 phiên để VÀO
   CRISIS/EX-BULL, chỉ 10 phiên để RA. Chậm hoảng loạn, chậm hưng phấn.
3. **Macro gate** — hợp 3 họ luật thành MỘT trần causal: tiền tệ trong nước (SBV refi 6m) + hoảng
   loạn Mỹ (VIX/SPX drawdown) + bypass khi VN đang bull xác nhận. Hành động phòng thủ duy nhất là
   **CAP** trần trạng thái; **re-risk thuần theo GIÁ** qua base (floor nới lỏng tiền tệ đã tắt).
4. **Breadth-decoupling guard** trên trụ Mỹ — chỉ chặn cap khi breadth VN thực sự khoẻ. Fail-safe:
   breadth yếu/thiếu/universe nhỏ → KHÔNG chặn. Nguồn breadth = `tav2_mike.universe_pit`
   (point-in-time), hằng số `BREADTH_SOURCE="pit"`; đổi thành `"prune"` là rollback một từ.

**Kết luận phải nhớ: DT5G là CHỐT RỦI RO FAIL-SAFE (bảo hiểm), không phải công cụ tăng lợi
nhuận.** Toàn bộ edge ròng đến từ một lần siết 2023; năm bull 2025 nó làm TỐN −0,89pp. Deploy qua
`get_gated_state()`, **đừng re-tune theo lịch sử** (tham số đang ở vùng bình ổn).

Kiến trúc chi tiết, số liệu audit, changelog, và lineage các bản cũ (Cổ Điển → Tinh Tế → v3.4b →
DT5G): **`vnindex_5state_registry.md`**.

⚠️ `state_transition_logic.py` giải thích pipeline **Cổ Điển đã archive**, KHÔNG phải chuỗi DT5G
đang chạy. Giữ làm tư liệu lịch sử; muốn hiểu trạng thái production thì đọc `macro_state_live.py`.

## Backtest

`backtest_workflow.py` là explainer tự chứa — chạy nó để xem đầy đủ cơ chế NAV và 7 chiều đánh
giá; không chép lại ở đây. Ba điều cần nhớ khi đọc bất kỳ con số backtest nào:

- NAV đơn luồng, vốn 1 tỷ, **thực thi trễ T+1** (không nhìn trước), ramp 3 phiên tới tỷ trọng đích.
- **Quy ước chi phí dùng chung** (`backtest_fundamental_rating.py`, `simulate_holistic_nav.py`…
  trích dẫn thẳng "per CLAUDE.md" — đổi ở đây là đổi giả định của chúng): TC **0,1%** mỗi chiều
  trên phần vốn thực giao dịch · lãi tiền gửi nhàn rỗi **0%/năm** · lãi vay margin **10%/năm**.
- Metric tính trên **thời gian lịch**, không phải số phiên (VN có giai đoạn tuần 3 phiên trước 2007).
- **Quy đổi thực tế: CAGR thật ≈ CAGR backtest − 1,5%** (phí + slippage + thuế). Backtest không
  mô hình hoá slippage lẫn thuế, và dùng VNINDEX làm proxy chứ không phải danh mục thật.

## Tài liệu tham chiếu

`market_timing_final_system.md` (backtest các hệ timing VNINDEX) · `market_rule.md` (luật cho
`MarketEvaluation` trong `webui/utils.py`, codebase ngoài) · `market_overheat.md` (logic
overbuy/oversell).
