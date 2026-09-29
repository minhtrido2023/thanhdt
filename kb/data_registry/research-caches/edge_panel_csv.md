---
kind: local-file
status: DERIVED (RESEARCH-ONLY — refresh DAILY, KHÔNG có consumer production)
source: data/edge_panel.csv
group: research-caches
upstream: tav2_bq.ticker_prune (TRAP — xem price-volume/ticker_prune.md)
builder: edge_health_monitor.py::refresh_panel() (--refresh)
cadence: DAILY T2-T6 qua papertrade_daily.sh step [22], cron `30 8 * * 1-5` = 15:30 ICT
verified: 2026-09-10 (data-ops, job AMH #1 Taylor_20260910_131906)
---

# data/edge_panel.csv — panel THÁNG (signal + forward return) cho đo IC/edge-health

**Status: DERIVED, research-only. SỐNG (refresh mỗi phiên) — khác hẳn 3 file tĩnh còn lại
trong nhóm này.** Nhóm `research-caches/` có tiêu đề "đừng nhầm là sống"; file NÀY là ngoại lệ,
nó thật sự được ghi lại mỗi ngày giao dịch.

## Là gì
Panel cross-section theo THÁNG: mỗi dòng = (1 ticker, 1 tháng) với ~10 tín hiệu (value /
quality / momentum / flow) **cộng forward return 1M và 3M** đã tính sẵn bằng `LEAD(Close)` sạch
(KHÔNG dùng cột `profit_*` bẩn). Mục đích duy nhất: đo **Information Coefficient** của từng
lens 8L theo thời gian và theo super-sector (chu kỳ Adaptive-Markets: alive / fading / dead /
sign-flipped).

- Kích thước đo 2026-09-10: **30.843 dòng, 16 cột, 7,3 MB**.
- **440 ticker riêng biệt, 150 tháng, 2014-01-02 → 2026-06-11.**

## Ai ghi / cadence (đã xác minh, không suy từ tên)
- Writer DUY NHẤT: `edge_health_monitor.py::refresh_panel()` (dòng 196-207) — chạy
  `bq query --format=csv "$(cat data/edge_panel.sql)" > data/edge_panel.csv`.
- Kích hoạt: cờ `--refresh`, HOẶC tự động khi file không tồn tại (`main()` dòng 275-276).
- Lịch thật: `papertrade_daily.sh` dòng 90 — `run "[22] edge_health_monitor" edge_health_monitor.py --refresh`,
  crontab `30 8 * * 1-5` = **15:30 ICT T2-T6**. Không có dòng crontab trực tiếp nào tên
  `edge_panel`/`edge_health` — nó nằm TRONG chain (đúng như finding Winston 2026-07-12).
- Bằng chứng tươi: mtime `2026-09-10 15:37:38 +07` (host chạy UTC — `ls` hiện "08:37", phải
  quy ra ICT mới khớp cron 15:30).

## Downstream
`edge_panel.csv` → `load_panel()` → `main()` → `data/edge_health_status.json` +
`data/edge_health_block.md` + `edge_health_ic.png`/`edge_health_matrix.*`.
Consumer duy nhất của khối .md là `amh_cockpit.py` — **đã RETIRED khỏi cron 2026-07-07**
(step [23][24][25] của papertrade_daily). ⇒ **Không có đường tiền thật nào đọc file này.**
Các script nghiên cứu đọc trực tiếp: `fitness_matrix.py`, `biodiversity_test.py`,
`backtest_core_arch.py`, `value_sleeve_test.py`, `value_sleeve_gating_test.py`,
`value_quality_gate_test.py`, `value_book_realistic.py`, `value_book_profile.py`, và
`mike/agents/Taylor/research/amh_changepoint_fitness_20260910/*` — không script nào có cron.

## Universe / filter (nguyên văn từ `PANEL_SQL`)
`FROM tav2_bq.ticker_prune` với `WHERE rn_month = 1 AND time >= "2014-01-01"
AND fwd_3m IS NOT NULL AND ticker != "VNINDEX" AND liq >= 1e9`, trong đó
`rn_month = ROW_NUMBER() OVER (PARTITION BY ticker, YEAR(time), MONTH(time) ORDER BY time)`
và `liq = COALESCE(Price, Close) * Volume`.

## Schema (16 cột) — % NULL đo thật 2026-09-10
| Cột | Nghĩa | %NULL |
|---|---|---|
| `time` | ngày chụp (phiên đầu tháng CỦA TỪNG MÃ) | 0,00 |
| `ticker` | mã | 0,00 |
| `icb` | `ICB_Code` (map super-sector qua `map_sector()`) | 0,65 |
| `fwd_3m` | ⚠️ **FORWARD** `LEAD(Close,60)/Close − 1` | 0,00 |
| `fwd_1m` | ⚠️ **FORWARD** `LEAD(Close,20)/Close − 1` | 0,00 |
| `liq` | `COALESCE(Price,Close) * Volume` (VND) | 0,00 |
| `pb_z` | `(PB − PB_MA5Y) / PB_SD5Y` | 9,42 |
| `PB` | Price/Book | 0,72 |
| `PE` | Price/Earnings | 1,32 |
| `ROIC5Y` | ROIC 5 năm | 0,69 |
| `FSCORE` | Piotroski F-Score | 1,41 |
| `ROE_Min5Y` | sàn ROE 5 năm | 0,67 |
| `D_RSI` | RSI ngày | 0,00 |
| `D_CMF` | Chaikin Money Flow | 0,00 |
| `mom_200` | `Close/MA200 − 1` | 4,53 |
| `C_L1M` | Close / Low-1M | 0,00 |

## Bẫy

**(1) `fwd_3m` / `fwd_1m` là CỘT NHÌN TRỘM TƯƠNG LAI.** Cùng lớp với lệnh cấm `profit_*` ở
`CLAUDE.md` (bẫy #1) và `_universe-selection-rules.md`. Chỉ dùng làm BIẾN MỤC TIÊU khi đo
IC/train. **TUYỆT ĐỐI không đưa vào bất kỳ filter/gate/selector live nào.** Panel này khác các
nguồn khác ở chỗ cột forward nằm ngay cạnh cột tín hiệu trong CÙNG một dòng — rất dễ vô tình
`df.dropna()` hay `df.corr()` cả bảng rồi kéo nó vào feature set.

**(2) File LUÔN kết thúc trước hôm nay ~3 tháng — đó là THIẾT KẾ, không phải stale.**
`fwd_3m IS NOT NULL` đòi đủ `LEAD(Close, 60)` phiên. Đo 2026-09-10: `ticker_prune` và `ticker`
đều tươi tới **2026-09-10**, nhưng panel dừng ở **2026-06-11**. **Đừng mở incident freshness,
đừng ffill, đừng "sửa" cho nó chạm ngày hiện tại** — chạm được nghĩa là forward return đã bị
làm giả. (Cùng họ với bài học `lag_edge_health.csv` 2026-07-12: "dữ liệu dừng sớm" ≠ "pipeline chết".)

**(3) Panel theo THÁNG, và ngày chụp KHÔNG chung cho mọi mã.** `rn_month = 1` tính theo
`PARTITION BY ticker, năm, tháng` ⇒ mỗi mã lấy phiên giao dịch đầu tiên **của riêng nó** trong
tháng. Đo thật tháng 2026-06: 187 dòng ở `06-01` nhưng 1 dòng ở `06-11`. Phân bố ngày-trong-tháng
toàn panel: ngày 1 (16.361), 2 (4.592), 3 (4.526), 4 (2.627), 5 (1.311), rồi rải tới 7/12/18/21.
⇒ Một "tháng" trong panel có thể trộn các quan sát cách nhau vài phiên tới hơn tuần. Chấp nhận
được cho IC xếp hạng thô; **không dùng làm mốc event-time chính xác** và đừng giả định
`groupby(month)` là một lát cắt đồng thời.

**(4) Universe là `ticker_prune`, KHÔNG phải `universe_pit`.** `ticker_prune` đang có status
**TRAP** (`price-volume/ticker_prune.md`) — trôi dần khỏi `universe_pit`, không có tín hiệu tự
động báo lệch. Panel này ra đời TRƯỚC dự án migrate 2026-07-22 nên rơi vào ngoại lệ (b) của
`_universe-selection-rules.md` (không bắt buộc sửa ngay), **nhưng đừng coi số của nó là "đúng"
khi đối chiếu với kết quả tính trên `universe_pit`**. Đặc biệt: quy ước fleet 2026-08-22 (trục
breadth-tercile PIT) yêu cầu `universe_pit` — kết luận conditional dựng trên panel này KHÔNG
thoả quy ước đó.

**(5) `liq >= 1e9` lọc CỨNG ngay tại dòng snapshot.** Panel không phải toàn bộ `ticker_prune`:
~188-233 mã/tháng gần đây trên tổng ~215+ mã prune mỗi phiên. Đây là điều kiện hoá theo thanh
khoản TẠI thời điểm chụp — mọi phát biểu "toàn thị trường" rút ra từ panel đều phải kèm chữ
"trong rổ thanh khoản ≥1 tỷ/phiên".

**(6) File bị `.gitignore` (`*.csv`, dòng 57) ⇒ KHÔNG tái lập được một vintage cũ.** Chạy lại
`--refresh` hôm nay cho một panel KHÁC bản hôm qua, vì `ticker_prune` bị restate/backfill
(chính lý do tồn tại `bin/bq_monthly_pin.sh`). ⇒ Kết quả nghiên cứu pin trên panel này
**không byte-reproducible** về sau. Muốn pin thật thì copy panel ra tên riêng có ngày
(`_asof<YYYYMMDD>`) theo `coding_guidelines.md` §8, đừng trỏ registry vào `edge_panel.csv`.

**(7) Sửa `data/edge_panel.sql` KHÔNG có tác dụng gì.** `refresh_panel()` GHI ĐÈ file .sql đó từ
hằng số `PANEL_SQL` trong `edge_health_monitor.py` (dòng 198-199) mỗi lần chạy. `.sql` chỉ là
bản in ra để người đọc; nguồn sự thật của truy vấn nằm trong .py.

**(8) Ghi KHÔNG nguyên tử — `--refresh` thất bại sẽ XOÁ TRẮNG panel đang có.** Lệnh là
`bq query ... > data/edge_panel.csv`: shell truncate file đích TRƯỚC khi `bq` chạy. `bq` lỗi
(hết credential, BQ down, quota) ⇒ `refresh_panel()` `sys.exit(1)` nhưng file đã thành rỗng, và
không có bản backup nào (file bị gitignore, không có `.bak`, không có tmp+rename). Vi phạm
`coding_guidelines.md` §5 (atomic write). Chưa từng cắn thật tính tới 2026-09-10 — ghi ra đây để
ai chạy `--refresh` tay biết rủi ro. **Sửa = đụng code production, thuộc Taylor, không phải data-ops.**

**(9) Đừng nhầm với 2 file tên gần giống:** `data/lag_edge_health.csv` (do
`edge_health_monitor.py::lag_edge_health()` ghi, đọc `earnings_px.pkl` + `earnings_events_classified.csv`,
KHÔNG đọc panel này, có probe WARN riêng trong `bin/bq_freshness_check.sh`) và
`data/edge_health_status.json` (output IC, downstream của panel). `--refresh` chỉ refresh
`edge_panel.csv` — đây đúng là hiểu lầm đã gây job sai tiền đề 2026-07-12
(`kb/incidents/2026-07/2026-07-12-lag-edge-health-2-tien-de-sai.md`).

**(10) Không có freshness-gate nào cho chính file này.** `bin/bq_freshness_check.sh` có probe
mtime cho `lag_edge_health.csv` nhưng KHÔNG có cho `edge_panel.csv`. Nếu step [22] chết, panel
đóng băng im lặng; hiện chỉ phát hiện qua FAIL-alert cuối chain `papertrade_daily.sh`. Vì không
có consumer production nên chưa đề xuất thêm probe (§14 chỉ bắt buộc với cặp producer→consumer
thật) — nếu sau này có script quyết định nào đọc panel, PHẢI thêm probe cùng lúc.

## Cách kiểm nhanh
```bash
TZ='Asia/Ho_Chi_Minh' stat -c '%n %y' /home/trido/thanhdt/WorkingClaude/data/edge_panel.csv
# kỳ vọng: mtime = phiên gần nhất ~15:3x ICT; max(time) trong file ≈ hôm nay − ~3 tháng
```

↩ [Về index nhóm](index.md) · [Về index tổng](../index.md)
