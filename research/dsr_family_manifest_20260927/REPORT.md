# 4 phát hiện phụ — reconcile egg · baseline ZaloPay · family_manifest · guard 15%

Job `Taylor_20260927_053033` (dispatch Mike) · 2026-09-27 · **CHƯA MERGE, chờ user sign-off.**
Nguồn: 3 phát hiện ngoài phạm vi của job `Taylor_20260927_045241` + 1 của `Taylor_20260927_043541`.

Branch / worktree:
| Repo | Branch | Worktree | Nội dung |
|---|---|---|---|
| `mike` | `fix/reconcile-egg-manifest` | `mike/agents/Taylor/wt-reconcile-egg` | (1) `bin/reconcile_equity.py` + selfcheck · report này |
| WorkingClaude | `fix/dsr-family-manifest` | `/home/trido/thanhdt/wt-dsr-manifest` | (3) `dsr_family_manifest.py` (mới) · `dsr_pbo_annex.py` · selfcheck |
| — (không sửa code) | — | — | (2) `data/account_inception.json.proposed` · (4) chỉ đề xuất |

---

## (1) CAO — `reconcile_equity.py` bỏ sót `egg.totalValue` ⇒ báo động giả ~10-12% NAV. **ĐÃ SỬA.**

`egg` là **sibling của `stock`** trong cùng payload `balances`; bản cũ chỉ đọc `bal_rec["payload"]["stock"]`
(`grep -c egg` = 0). Trứng vàng là vốn CHỦ SỞ HỮU thật nhưng KHÔNG nằm trong `totalCash` lẫn
`availableCash` (`coding_guidelines_ext.md` §25, chiều thứ BA) ⇒ tiền user chuyển cash→Trứng vàng làm
**vế phải co lại đúng bằng số đó** trong khi vế trái (vốn + P&L) không đổi ⇒ residual DƯƠNG GIẢ.

Đo thật, `dnse_raw` broker, **cả 2 TK (§12 — 2 kết quả KHÁC nhau)**:

| TK | ngày | egg.totalValue | dư sau diễn giải TRƯỚC | dư sau diễn giải SAU | kết luận đẳng thức |
|---|---|---:|---:|---:|---|
| SpaceX | 2026-09-25 | 85.449.493 | **+85.765.426 (+9,5782% NAV)** ⚠️ CHƯA GIẢI THÍCH ĐƯỢC | **+315.933 (+0,0322%)** | ❌ LỆCH → ✅ KHỚP |
| ZaloPay | 2026-09-25 | 102.121.977 | **+102.272.560 (+11,9649%)** ⚠️ | **+150.583 (+0,0157%)** | ❌ LỆCH → ✅ KHỚP |
| SpaceX | 2026-09-26 | 85.469.401 | (cùng lớp) | +296.025 (+0,0302%) | ✅ KHỚP |
| ZaloPay | 2026-09-26 | 102.145.882 | (cùng lớp) | +126.678 (+0,0132%) | ✅ KHỚP |

**Hệ quả đã hết:** cổng đối soát chặt nhất của pipeline §6 bước 3 trước đây in "CHƯA GIẢI THÍCH ĐƯỢC"
mỗi lần chạy và **mọi lệch < ~10% NAV bị chìm trong nhiễu egg** — tức nó không thể bắt được dòng tiền
nhỏ, đúng việc nó tồn tại để làm. Sau sửa, độ phân giải thật ≈ 0,02-0,03% NAV.

Không có double-count: `manual_offbook_assets_vnd` = **0 ở cả 2 TK** (`secrets/trading_bot_accounts.json`,
asof 07-20/07-22, user đã rút hết Trứng vàng off-book thời đó) và bản vá in cảnh báo stderr tường minh
nếu cả `egg` và `--offbook-assets` cùng > 0.

**Selfcheck `bin/reconcile_equity_egg_selfcheck.py` — 16/16 assertion PASS, 2/2 mutation BỊ GIẾT:**
- `bo-egg-khoi-ve-phai` → 4 assertion fail (unexplained SpaceX về lại +9,5782%).
- `egg-luon-0` → 7 assertion fail.
- Nhóm C (byte-identical): trên `dnse_raw_2026-08-01` (raw TRƯỚC khi DNSE expose `egg`) bản mới cho
  output **BYTE-IDENTICAL** với bản cũ ở cả 2 TK (34 và 37 dòng; so bằng bản `git show HEAD:` của chính
  file). `--no-egg` trên raw CÓ egg: khác bản cũ đúng **1 dòng thông tin**, mọi con số trùng.
- Selfcheck cố tình không dùng `datetime.now()` (§16) và copy snapshot sang tmpdir nên không ghi đè
  artifact canonical `data/execution_logs/reconcile_equity_*.json`.

`--no-egg` là lối thoát duy nhất được thêm; nó chỉ làm residual **TO HƠN** (không bao giờ nới cổng),
tồn tại để tái lập số của bản trước 2026-09-27 khi audit.

---

## (2) TRUNG BÌNH — ZaloPay 2 mốc baseline lệch 1.280.113đ. **ĐỀ XUẤT, KHÔNG TỰ SỬA.**

| File | mốc | số | định nghĩa file đó tự khai |
|---|---|---:|---|
| `data/account_inception.json` (dùng bởi `nav_period_returns.py`) | `starting_capital: null` ⇒ dòng `nav_history` đầu **2026-07-07** | 986.585.454 | "mốc KHỞI ĐIỂM thật… không phải dòng đầu tiên trong nav_history CSV" |
| `data/account_seed_capital.json` (dùng bởi `reconcile_equity.py`) | **2026-07-06** | 987.865.567 | "vốn đầu kỳ = NAV thật ngày go-live" |

Hai file tự khai **cùng một khái niệm** ("vốn khởi điểm") nhưng lấy 2 mốc cách nhau 1 phiên.
Chênh 1.280.113đ = 0,1298% — và nó **chính là P&L ngày go-live 07-07** (−1.280.113đ): dòng
`nav_history` đầu tiên là snapshot SAU phiên bot giao dịch đầu tiên. Đây **đúng lớp lỗi §31 đã sửa cho
SpaceX** (báo cáo tuần 09-14→09-18 dùng dòng đầu 07-02 làm baseline, sai 0,517pp) nhưng vẫn còn sống ở
ZaloPay: chú thích trong `nav_period_returns.py` viết "ZaloPay không bị lỗi này" là **không đúng** —
ZaloPay không có mốc "nạp tiền ngày 1" sạch, nhưng nó CÓ mốc go-live-eve đã đo và đã audit.

**Khuyến nghị: Option A** — `ZaloPay.starting_capital = 987865567`, `inception_date = 2026-07-06`
(lấy nguyên số của `account_seed_capital.json`: cash 4.919.567 + MTM 982.946.000 − debt 0; nguồn
`dnse_raw_2026-07-06` balances+positions ĐÃ lọc `account_no`, giá `BQ ticker.Price` trùng 7/7 với DNSE
`marketPrice` trong cùng bản ghi). Vì: (a) khớp định nghĩa mà CHÍNH `account_inception.json` tự khai;
(b) hết 2 mốc mâu thuẫn giữa 2 file; (c) không che P&L ngày đầu.

**Số công bố lệch bao nhiêu** (asof 2026-09-25, NAV 957.269.620 — chạy thật qua `nav_period_returns.py`
với `.proposed`, KHÔNG sửa file canonical):

| phương án | from_date | nav0 | "Từ khi bắt đầu hoạt động" | WTD | MTD |
|---|---|---:|---:|---:|---:|
| **A (đề xuất)** | 2026-07-06 | 987.865.567 | **−3,097%** | −0,153% | +0,515% |
| B (hiện tại) | 2026-07-07 | 986.585.454 | −2,971% | −0,153% | +0,515% |
| | | | **lệch −0,1257pp** | 0 | 0 |

WTD/MTD KHÔNG đổi (baseline 2 kỳ đó là dòng `nav_history` trước kỳ, đều ≥ `inception_date`). Không đổi
`report_delivery_gate.py` (cổng lệch-baseline chỉ áp SpaceX, ZaloPay là kênh nội bộ).

⚠️ Kiểm tra kèm, KHÔNG có đứt mạch nào khác: 147.473.247đ Trứng vàng off-book của ZaloPay **đã được
đếm liên tục** trong `nav_history` (cột `offbook_assets` các phiên 07-17→07-20; trước 07-17 nó vẫn là
`cash` — 07-16 `cash` 167.993.885 → 07-17 `cash` 22.465.980 + `offbook` 147.473.247). Nên chuỗi NAV
không có bước nhảy ảo tại các lần chuyển cash↔egg↔offbook.

Ghi ra: `data/account_inception.json.proposed` (chưa áp).

---

## (3) PBO không tái lập — **`family_manifest` ĐÃ IMPLEMENT + ĐO**

### 3.1 Bệnh
`dsr_pbo_annex.py::family_paths()` là **glob động** `data/v23_golive_audit_2014_now_*.csv`. Họ trial theo
định nghĩa BBLZ 2017 là tập cấu hình **đã được SO SÁNH với nhau khi chọn** config deploy — glob kéo
vào **mọi** backtest R&D chạy về sau. Đo trong CÙNG MỘT NGÀY:

| thời điểm | #CSV qua bộ lọc ≥2500 obs | **PBO** | cổng §18 "PBO ≥ 0,5 ⇒ chọn config robust-trung vị" |
|---|---:|---:|---|
| họ phục dựng 2026-07 (68 file) | 68 | **0,2085** | qua thoải mái |
| 2026-09-27 **sáng** (log `dsr_pbo_newR3.log`, 577 globbed) | 477 | 0,3993 | qua |
| 2026-09-27 **12:47** (586 globbed, +9 CSV trong vài giờ) | **486** | **0,5013** | ❌ **VƯỢT NGƯỠNG** |

**9 file CSV sinh ra trong vài giờ của cùng một ngày đã đẩy PBO qua mốc quyết định.** Nói thẳng: như
đang code, PBO **không phải thuộc tính của V2.4** mà là thuộc tính của *nội dung thư mục `data/` lúc
chạy*. Mọi số PBO đã pin trong registry đều không tái lập được, và "0,3993 < 0,5 ⇒ không red flag"
(registry :7177) là kết luận của một lần chụp thư mục, không phải của mô hình.

### 3.2 Phục dựng họ gốc — ĐƯỢC, và nó khớp số đã pin
Registry **không lưu danh sách file** nên không có danh sách gốc để đọc. Phục dựng bằng `mtime`
(< `2026-07-05T08:00` ICT — job annex là `Taylor_20260705_075644`, 07:56 ICT) cho **68 file**, và
thống kê của họ này khớp mục annex 2026-07 gần như từng số:

| chỉ số | registry 2026-07 | họ phục dựng 68 file (đo lại hôm nay) |
|---|---|---|
| #config | 71 ("80" ở bảng :7238) | 68 |
| mean ann-SR | 1,69 | **1,697** |
| sd ann-SR | 0,144 | **0,146** |
| Var(per-day SR) | 8,22e-5 | **8,488e-5** |
| SR0(ann) @N_csv | 0,35 | **0,350** |
| daily obs × combos | 3100 × 12.870 | **3100 × 12.870** |
| **PBO** | 0,198 (§3 mục 2026-07) / **0,2088** (bảng :7238) | **0,2085** |

⇒ phục dựng **không phải danh sách gốc nguyên bản** (đếm 68 vs 71/80, và mtime chỉ là chặn trên của
thời điểm tạo — file nào bị ghi lại sau 07-05 sẽ bị loại oan), nhưng nó **tái lập PBO đã pin tới 3 chữ
số thập phân** (0,2085 vs 0,2088). Đây là bằng chứng mạnh nhất có được; **số PBO đúng cho họ chọn V2.4
là ~0,21, không phải 0,40 hay 0,50.**

Ghi chú provenance còn hở: "PBO 0,2088 (họ 80)" ở bảng :7238 không truy được về lệnh/ngày nào trong
registry (mục 2026-07 ghi 0,198 / 71 config). Cả hai đều ~0,20 nên kết luận không đổi, nhưng đó là một
con số đang được trích dẫn mà không có nguồn.

Phát hiện phụ (đã ghi ở registry :7189, xác nhận lại): `DSR_R3_CSV` mặc định
`..._etfliqcustompitg_wtnamecap.csv` có **mtime 2026-07-14** — file đó bị ghi lại SAU khi annex 2026-07
chạy, nên nó cũng không nằm trong họ phục dựng.

### 3.3 Cơ chế đã implement
- **`dsr_family_manifest.py` (mới)** — `build` ghi `data/dsr_family_manifest_<date>.json`: mỗi entry
  `{path, md5, size, mtime_ict, n_obs, reason}` + khối `criterion` khai tường minh tiêu chí
  (`glob`, `mtime_before_ict`, `min_obs`, `reason`) và `skipped` đếm theo từng lý do. `verify` kiểm lại.
  `build` **không tự quyết** file nào thuộc họ — nó ghi lại tiêu chí người dùng khai + bằng chứng đo
  được, để người sau audit.
- **`dsr_pbo_annex.py`** — `DSR_FAMILY_MANIFEST=<file>` ⇒ `family_paths()` đọc manifest, **fail-CLOSED**:
  thiếu file **hoặc** md5 lệch ⇒ `RuntimeError` → `main()` trả rc=2, in đúng path nào thiếu / md5 nào
  lệch (§29: thông điệp trích bằng chứng vừa đọc, không đoán). Không set manifest ⇒ giữ glob động
  **nhưng in cảnh báo** rằng số không tái lập được.
- 2 manifest đã dựng (bản committed ở `research/dsr_family_manifest_20260927/`, bản làm việc ở
  `data/dsr_family_manifest_{2026-07-05_recon,2026-09-27}.json` — `data/*.json` bị `.gitignore` của
  repo WC nên không commit được vào đó, giống mọi artifact data khác).

**Selfcheck `dsr_family_manifest_selfcheck.py` — 8/8 assertion PASS** (chạy trong tmpdir có `data/`
toàn symlink ⇒ không chạm `data/` canonical, không copy 1,5GB):

| test | kết quả đo |
|---|---|
| manifest hợp lệ | N=8, PBO=0,426 |
| **+1 CSV lạ vào thư mục, CÓ manifest** | N=8, **PBO=0,426 — KHÔNG ĐỔI** |
| đối chứng: cùng thư mục đó, KHÔNG manifest | N=**9**, PBO=**0,1518** (glob động đổi hẳn kết luận) |
| manifest thiếu 1 file | **rc=2**, stderr nêu đúng path `THIẾU` |
| md5 lệch (file bị ghi lại, tên giữ nguyên) | **rc=2**, stderr nêu `MD5 LỆCH` + 2 md5 |

### 3.4 Việc cần user/Mike quyết (KHÔNG tự làm)
1. Họ trial CHÍNH THỨC của V2.4 là họ nào? Khuyến nghị: pin
   `data/dsr_family_manifest_2026-07-05_recon.json` (68 file) làm họ chọn-V2.4, **kèm caveat phục dựng
   bằng mtime** ở trên. Sau đó registry sửa PBO về **0,2085** và ghi rõ nó gắn với manifest nào.
2. Số 0,3993 / 0,5013 nên được ghi là **"PBO trên họ đã nở tới ngày X"** — một chỉ báo *sức ép
   multiple-testing tích luỹ của toàn bộ R&D*, KHÁC câu hỏi "chọn R3 ra khỏi họ có overfit không".
   Đừng gộp 2 số vào cùng một ô bảng như bảng SUPERSEDED :7238 đang làm.
3. Có nên thêm `DSR_FAMILY_MANIFEST` bắt buộc (fail nếu không set) không? Hiện để mặc định glob +
   cảnh báo, chưa chặn — đổi thành chặn là một quyết định vận hành.

---

## (4) THẤP — guard 15% của `daily_nav_snapshot.py:1281`: **chỉ đề xuất, chưa sửa**

Hiện tại: `|Δnav ngày| > NAV_SANITY_MAX_PCT (15%)` ⇒ `return 3`, không ghi `nav_history`, và lối thoát
duy nhất là *"nếu là nạp/rút tiền thật → chạy lại với NAV_SANITY_MAX_PCT lớn hơn"*. Tức đường thoát hợp
lệ là **nâng ngưỡng rồi ghi NAV** — nạp/rút thật bị ghi vào `nav_history` **không có dấu vết gì** rằng
đó là dòng tiền chứ không phải lãi/lỗ. Đó đúng là dữ liệu mà FAIL-H cần: `nav_period_returns.py` sau
bản vá TWR đọc `data/account_cash_flows.json` để tách số hạng dòng tiền, nhưng KHÔNG có gì buộc bản ghi
đó tồn tại **tại thời điểm NAV được ghi**.

**Đề xuất (chưa code, cần merge `fix/nav-flow-term` trước vì `bin/account_cash_flows.py` nằm trên đó):**
1. Trong nhánh vượt ngưỡng, TRƯỚC khi `return 3`: gọi `account_cash_flows.load_flows(account)` +
   `flow_dates(flows)`. Có bản ghi cho `args.date` ⇒ **ghi NAV bình thường** (dòng tiền đã được khai,
   có `evidence`) và in ra bản ghi đã dùng. Không có ⇒ giữ `return 3` như hiện nay.
2. Đổi thông điệp: thay "chạy lại với `NAV_SANITY_MAX_PCT` lớn hơn" bằng "khai dòng tiền vào
   `data/account_cash_flows.json` (kèm `evidence`) rồi chạy lại" — đường thoát ĐÚNG là *khai dữ liệu
   còn thiếu*, không phải *nâng ngưỡng*. Giữ `NAV_SANITY_MAX_PCT` cho ca bug dữ liệu thật.
3. Ngưỡng: guard này 15%, cổng `report_delivery_gate._check_nav_flow_records()` của FAIL-H là **5,0%**
   (đo từ 113 cặp phiên thật, max 4,148%). Hai ngưỡng khác nhau là hợp lý (một chặn GHI, một chặn GỬI)
   nhưng phải nói rõ: dòng tiền 5-15% NAV sẽ được `daily_nav_snapshot` ghi im lặng rồi mới bị cổng gửi
   bắt sau. Nếu muốn bắt sớm, hạ guard xuống cùng 5,0% và dùng chung hằng số `NAV_JUMP_BLOCK_PCT`.
4. Không đụng `report_return_gate.py` / `dividend_adjusted_return.py` (ngoài phạm vi job này).

---

## Lệnh tái lập

```bash
# (1)
cd /home/trido/thanhdt/WorkingClaude
python3 mike/agents/Taylor/wt-reconcile-egg/bin/reconcile_equity_egg_selfcheck.py --mutations
# (2)
python3 -c "import sys,datetime;sys.path.insert(0,'mike/bin');import nav_period_returns as n;\
r=n.load_nav_history('ZaloPay');print(n.compute_period_returns('ZaloPay',datetime.date(2026,9,25),r,\
n.load_inception('ZaloPay','data/account_inception.json.proposed')))"
# (3)
WT=/home/trido/thanhdt/wt-dsr-manifest/WorkingClaude; P=/home/trido/thanhdt/wc_venv/bin/python
$P $WT/dsr_family_manifest_selfcheck.py
R3=data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_c30vmain_univpit.csv
DSR_R3_CSV=$R3 DSR_FAMILY_MANIFEST=data/dsr_family_manifest_2026-07-05_recon.json $P $WT/dsr_pbo_annex.py
```
