# VIỆC 2 — audit chiều `sort`/`rank` trong mọi `*_screen.py`

Job `Taylor_20260927_103434` · 2026-09-27 · branch `fix/screen-sort-direction-20260927` (CHƯA MERGE)

## Kết quả một dòng

Quét **20 file** `*_screen.py`, **107 lệnh sort/rank** có `by` + `ascending` đọc được từ literal.
Tìm ra **ĐÚNG MỘT lớp lỗi chắc chắn sai**, lặp ở **16/20 file**; **0** chỗ mơ hồ còn lại.

## Lỗi: "8L top-25" thật ra là 25 mã XẤU NHẤT

`sort_values(["rating","tv"], ascending=False).head(25)` → `ascending=[True, False]`

`fa_ratings_8l.rating` là thang **1–5 kiểu hãng xếp hạng tín nhiệm**, **1 = AAA = TỐT NHẤT**
(`rating_8l.py:2` "8L Quality Rating 1-5 (credit-agency-style)"; `:346`
`rating = 2 if s>=6 else 3 if s>=4 else 4` — điểm CAO cho số rating THẤP; cổng production là
`rating<=3`). Chính comment trong code nói rõ ý định: *"8L top-25 ASOF per rebal date …,
**tie-break by liquidity**"* — nên `tv` GIẢM dần là đúng, chỉ `rating` sai chiều.

| File | Dòng | File | Dòng |
|---|---|---|---|
| aviation_screen.py | 237 | logistics_port_screen.py | 227 |
| bank_compounder_screen.py | 272 | pharma_screen.py | 220 |
| compounder_screen.py | 202 | re_compounder_screen.py | 218 |
| construction_screen.py | 299 | retail_compounder_screen.py | 265 |
| energy_screen.py | 255 | securities_screen.py | 296 |
| fertchem_rubber_screen.py | 238 | steel_buildmat_screen.py | 243 |
| fnb_screen.py | 251 | tech_screen.py | 250 |
| livestock_screen.py | 283 | textile_screen.py | 269 |

### Delta ĐO THẬT trên rổ top-25 (146 kỳ rebal, 2014-08-29 → 2026-09-25)

| | rổ HIỆN TẠI | rổ SỬA |
|---|---|---|
| rating trung bình | **4,504** | **1,252** |
| rating tốt nhất trong rổ (trung bình) | 4,05 | 1,00 |
| overlap 2 rổ | **0,01 / 25** · 145/146 kỳ RỜI NHAU HOÀN TOÀN | |
| số kỳ rổ không có mã nào `rating<=3` | **145 / 146** | 0 |

Ví dụ kỳ cuối 2026-09-25 (n=192 mã đủ thanh khoản):
- **HIỆN TẠI** (rating {4:15, 5:10}): `APS CEO CII DCL EIB EVS GEX HAG HTN IDJ KDH MSN NLG NVL PDR PVD PVS SBT SHS SSB STB TCO VC3 VIC VPI`
- **SỬA** (rating {1:8, 2:17}): `ACB ACV BVH CTG FPT GAS GMD GVR HAH IDC MBB MBS MCH NNC PNJ PVT SSI TCB TLG TOS VCB VHM VIX VNM VRE`

Rổ hiện tại chứa cả **NVL, HAG** — nằm trong danh sách BANNED vĩnh viễn.

### Delta ĐO THẬT trên số ORTHOGONALITY mà screen in ra

| Screen | TRƯỚC | SAU | Δ |
|---|---|---|---|
| bank_compounder | 4,9% | **64,1%** | +59,2pp |
| tech (G_VN) | 0,0% | **83,3%** | +83,3pp |
| pharma | 0,0% | **69,0%** | +69,0pp |
| aviation (INFRA) | 0,0% | **53,4%** | +53,4pp |
| logistics (PORT) | 0,0% | **37,1%** | +37,1pp |
| compounder | 4,0% | **25,8%** | +21,8pp |
| retail_compounder | 0,0% | **21,1%** | +21,1pp |
| securities | 6,9% | 4,5% | −2,4pp |
| logistics (SHIP) | 1,6% | 2,3% | +0,7pp |

**Hệ quả nghiên cứu, không chỉ hệ quả code:** 7/9 screen từng được báo là "trực giao với 8L
top-25" (0–5%) thật ra **trùng 21–83%**. Kết luận "sleeve này bổ sung alpha mới, không lặp 8L"
KHÔNG được suy từ những con số cũ nữa.

## Những chỗ ĐÃ XEM và kết luận ĐÚNG — không sửa

| Mẫu | Số chỗ | Vì sao đúng |
|---|---|---|
| `nlargest(K, "score")` · `sort_values("score", ascending=False)` | 23 chỗ gán `score` | `score` là tổng z-score với cấu phần định giá **đã đảo dấu** (`negz` / `-zc(s)`: PE/PB/PS/EVEB/pe_rel/pb_rel/Debt_Eq) và cấu phần chất lượng để dương (ROE/ROIC/GPM/CF_OA/DY/Revenue_YoY) ⇒ score cao = rẻ + tốt. Kiểm 23/23. |
| `sort_values("time")`, `sort_values("Release_Date")`, `sort_values("d")` | ~40 | TĂNG dần là **yêu cầu thuật toán**, không phải thẩm mỹ: `merge_asof` đòi khoá sort tăng, `groupby("ticker").tail(1)` chỉ lấy đúng bản ghi MỚI NHẤT khi time tăng. Đảo chiều = sai as-of. |
| `sorted(tickers)` / `sorted(dates)` | ~35 | thứ tự định danh để in hoặc lặp, không phải xếp hạng metric |
| `alldays.searchsorted(d, side="right")` | 12 | tra vị trí trong mảng đã sort, không phải sort |
| `a[m].rank().corr(b[m].rank())` | 7 | Spearman — hai vế cùng chiều TĂNG nên dấu tương quan giữ nguyên |
| `forensic_screen.py:39` `["susp","ar_rev"], ascending=False` | 1 | màn hình TÌM nghi vấn; chính script in `"susp score 0-5; higher = stronger 'earnings not cash' signature"` ⇒ giảm dần đúng |
| `cash_machine_screen.py:99/117/120` | 3 | `machine` là bool (False-desc ⇒ True trước), `med_ttm`/`roic5y` cao hơn tốt hơn ⇒ desc; `engine` là nhãn chuỗi ⇒ asc để nhóm |
| `holdco_sotp_screen.py` `pick_discount` | 1 | `v <= med` giữ nửa DƯỚI của coverage-z, khớp comment "coverage-z LOW = deep discount" |
| `soe_governance_screen.py:128` `["type","turnover"]` | 1 | **chỉ in bảng**, không cắt top-N ⇒ chiều là quy ước trình bày. Xem `DISPLAY_ONLY` trong selfcheck — khai TƯỜNG MINH đây là phán xét, không phải sự thật về cột. Ai cắt top-N trên `turnover` về sau phải đổi nó sang `HIGHER_BETTER`. |

**Không còn chỗ nào mơ hồ**: selfcheck báo `ambiguous=0` — mọi cột xuất hiện trong 107 lệnh
sort/rank đều đã được khai ngữ nghĩa tường minh (`LOWER_BETTER` / `HIGHER_BETTER` / `NEUTRAL` /
`DISPLAY_ONLY`).

## Kiểm chứng

`$DNA_PYEXE screen_sort_direction_selfcheck.py --mutations`

- Không phải scan text — **AST** (`ascending` viết xuống dòng / dạng list vẫn đọc đúng), phân biệt
  sort **có cắt top-N** (`.head()`/`.tail()` ⇒ quyết định CHỌN) với sort trình bày.
- **20 file · 107 lệnh sort/rank · 0 violation · 0 ambiguous · 0 behaviour-fail**, giống nhau
  trên **4 môi trường** TZ (`Asia/Ho_Chi_Minh`, `UTC`, `America/New_York`, TZ **gỡ hẳn**) —
  selfcheck tự so 4 kết quả và FAIL nếu chúng khác nhau.
- **7/7 mutation bị giết**, gồm mutation revert đúng bug gốc (bắt lại 16/16 file).
- **Bằng chứng mạnh nhất**: chạy chính selfcheck này trên bản **CHƯA SỬA** (copy từ main checkout)
  → `violations=16`, liệt kê đúng 16 `file:line` trong bảng trên. Selfcheck bắt được bug thật,
  không phải tautology.
- Test HÀNH VI riêng (không đọc file): trên frame tổng hợp, biểu thức đã sửa chọn
  `['BBB','AAA','FFF']` (rating 1,1,2 — `tv` tie-break giảm dần) còn biểu thức cũ chọn
  `['DDD','EEE','CCC']` (rating 5,5,3), hai rổ RỜI NHAU. Có cả assert "tie-break `tv` phải có
  tác dụng" để case test không vô nghĩa.
- `python -m py_compile` sạch trên cả 20 file.

## §8 — cảnh báo phải đọc trước khi merge

Chạy screen để đo delta đã **ghi đè** các file output pinned trong `data/results_registry.md`
(`data/*_verdict.json`, `data/*_monthly.csv`). Đã **PHỤC HỒI** bằng cách chạy lại bản GỐC
(chưa sửa) từ main checkout, và **đối soát lại `ortho_8l` khớp đúng giá trị trước khi sửa**
(aviation.infra 0,0 · pharma 0,0 · securities 6,9 · logistics port 0,0 / ship 1,6 · tech 0,0/0,0).
Các file pinned hiện đang chứa **con số ORTHOGONALITY SAI** (theo bug) — đúng như registry pin.

⇒ **Khi merge, PHẢI sinh lại toàn bộ 16 screen và cập nhật `data/results_registry.md`**; con số
`ortho_8l` trong mọi entry của 16 screen đó hiện không còn giá trị. Việc này KHÔNG làm trong job
này vì nó sửa registry pinned (cần user duyệt).
