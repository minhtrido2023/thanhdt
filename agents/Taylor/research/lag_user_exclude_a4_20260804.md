# A4 — Exclude list IVS/TMG cho book LAG: còn hiệu lực không, và cần cơ chế gì?

**Job** `Taylor_20260804_155443` · 2026-08-04 · **BUILD XONG + SELFCHECK XONG, CHƯA WIRE**

---

## 0. Tóm tắt

| | |
|---|---|
| Câu hỏi dispatch | exclusion IVS/TMG còn hiệu lực? (window LAG 07-24 đã qua) → nếu hết thì đóng việc |
| **Trả lời** | **CHƯA hết hiệu lực — và tiền đề "window đã đóng" BỊ BÁC BỎ bằng số liệu hôm nay** |
| Đo được 2026-08-04 | **IVS VÀ TMG đều là ứng viên LAG TRỞ LẠI**, nằm trong rổ `qualify` của `live_lag_candidates()` |
| Nhưng | cả hai đang bị chặn — mỗi mã bởi **ĐÚNG MỘT** cổng **KHÔNG mang quyết định của user** |
| Đã build | 2 tầng gate, **1 patch duy nhất**, `git apply --check` sạch, **CHƯA áp** |
| Selfcheck | signal-tier **33/33**, order-tier **37/37** (`--live`) = **70/70**, đều nhau ở 4 cấu hình TZ |
| Production đụng tới | **0 file** — `git status` xác nhận sạch sau khi dựng patch |

Patch: `mike/agents/Taylor/research/lag_user_exclude_a4_20260804.patch`

---

## 1. Tiền đề của dispatch bị bác bỏ — đo, không suy luận

Dispatch giả định: *"cửa sổ LAG IVS/TMG đã đóng (quyết định bound tới phiên 07-24 đã qua) →
nếu không còn candidate nào liên quan thì không cần build."*

Đọc `data/golive_v23_status.json` (artifact production **hôm nay**, 2026-08-04):

| Mã | Xuất hiện ở | Nghĩa |
|---|---|---|
| **IVS** | `lag_rating_excluded` → `{"rating": 5, "reason": "RATING_FAIL 8L=5 (≥4)"}` | đã vào rổ ứng viên, **qua** được lọc thanh khoản, bị rating loại |
| **TMG** | `lag_liq_excluded` → `{"reason": "Volume_3M_P50=0.0 → ADV ≤ 0"}` | đã vào rổ ứng viên, bị lọc thanh khoản loại |

Có mặt trong danh sách *bị loại* chứng minh chúng **đã ở trong rổ ứng viên** tại thời điểm mỗi
filter chạy. Chạy trực tiếp `live_lag_candidates()` xác nhận lại: cả hai nằm trong tập `qualify`.

⇒ **Chu kỳ tái xuất hiện đo được là ~14 ngày**, không phải "một lần rồi hết". Đây là hệ quả cấu
trúc: ứng viên LAG sinh ra từ **sự kiện earnings**, nên mỗi quý công bố là một lần tái xuất hiện.
Mùa BCTC Q2/2026 đang diễn ra chính là lần tái xuất hiện đó.

---

## 2. Vì sao "đang bị chặn" KHÔNG PHẢI "đã có cơ chế"

Cả hai mã hôm nay đều không tới được plan. Nhưng lý do chặn **không phải** quyết định 07-21 của
user — mà là hai cổng khác, mỗi mã đúng một cổng:

| Mã | Cổng duy nhất đang chặn | Độ bền (đo trên BQ) | Điều gì mở cổng |
|---|---|---|---|
| **IVS** | 8L rating = 5 (≥4) | rating **5/tier E, 9/9 quý** liên tiếp 2024-07→2026-07 | rating cải thiện về ≤3 |
| **TMG** | `Volume_3M_P50 = 0` ⇒ ADV ≤ 0 | **0/228 phiên** có `P50>0`, `MAX(P50)=0` (12M gần nhất) | thanh khoản nhúc nhích trên 0 |

Hai điểm khiến đây là rủi ro thật, không phải giả thuyết:

1. **TMG PASS cổng rating.** `fa_ratings_8l`: TMG rating **1** suốt 8 quý, **3** ở quý 2026-07 —
   `tier A`, `route COMPOUNDER`. Tức TMG **thoả** gate rating≤3; thứ duy nhất chặn nó là ADV=0.
   Một mã ADV=0 mà điểm chất lượng tốt là đúng hình dạng "cổng đơn lẻ": ngày nào `Volume_3M_P50`
   dương lên, TMG thành ứng viên LAG **hợp lệ theo mọi cổng đang có**.
2. **Cổng chặn IVS chính là cái mà lý do loại IVS dự đoán sẽ đổi.** User loại IVS vì
   *"surprise +136,7% phồng cơ học do nền lỗ"* — tức nền lợi nhuận thấp. Chính một quý hồi phục
   trên nền lỗ đó là cơ chế đẩy ROE/rating lên. Cổng đang giữ IVS phụ thuộc vào đúng biến số mà
   luận điểm loại nó nói là đang biến động.

**Và cổng mang quyết định của user thì chưa từng tồn tại**: `grep -rn "IVS\|TMG"` trong `.py`
production = 0 kết quả (ngoài comment). Danh sách chỉ sống ở **văn xuôi**
`mike/kb/context_planning_mini.md`. Đúng khuôn sự cố **2026-07-23**: DollarBill đưa IVS vào plan
LAG **cả 2 account** (SpaceX 1.800cp + ZaloPay 2.750cp) vì lớp phòng thủ duy nhất là **trí nhớ**
của người/LLM lập plan.

---

## 3. Cơ chế đã có sẵn — và vì sao KHÔNG dùng 2 nguồn có sẵn

Tin tốt: cơ chế exclude-list cho LAG **đã tồn tại** từ 2026-08-03 —
`lag_forensic_filter.lag_filter_forensic_banned()`, đã wire ở `golive_recommend_v23.py:~735`, với
2 nguồn: hằng số `BANNED` + `data/forensic_flags.csv` (severity=`exclude`). Nên A4 **không phải
xây cơ chế mới**, chỉ phải trả lời: IVS/TMG nên vào nguồn nào?

Đã kiểm cả hai nguồn có sẵn và **bác bỏ cả hai** — bằng grep consumer, không phải bằng cảm nhận:

**(a) KHÔNG thêm vào `data/forensic_flags.csv`.** File này có nhiều consumer NGOÀI LAG:

| Consumer | Làm gì với cờ |
|---|---|
| `rating_8l.py:465` | **ÉP rating = 5** cho mã bị cờ ⇒ đổi chính bảng 8L mà BAL/custom30V/CAPIT đọc |
| `custom_basket.py:307` | rổ custom30V |
| `pt_v22_dt5g.py:433`, `pt_v23_lagqual_research.py:1046`, `pt_v23_lagcap_research.py:1046`, `converge_fullharness_test.py:896`, `lag_dnpr_harness.py:784` | 5 engine backtest |

⇒ Thêm IVS/TMG vào đó sẽ đổi bảng rating **và** đổi hành vi engine ⇒ **số pin R3 không còn tái
lập được**. Cộng thêm sai ngữ nghĩa: IVS/TMG **không phải** ca forensic/kế toán (lý do loại là
thanh khoản mỏng + ngoài mô hình + chất lượng yếu) — ghi vào registry forensic là làm bẩn nguồn
phán quyết đó.

**(b) KHÔNG thêm vào `BANNED`.** Hằng số này nhân bản ở `mike/bin/build_universe_pit_quality.py:71`
và được ghi thành cột `banned` của bảng `universe_pit_quality` ⇒ chạm custom30V + toàn universe,
và phải rebuild lịch sử. User quyết *"không mua IVS/TMG cho LAG"*, **không** quyết cấm toàn hệ —
nới hộ phạm vi là tự ý mở rộng quyết định của user.

**⇒ Nguồn thứ 3, hằng số RIÊNG, phạm vi CHỈ LAG.**

---

## 4. Đã build — 2 tầng, 1 patch

### 4.1 Tầng TÍN HIỆU: `LAG_USER_EXCLUDED` trong `lag_forensic_filter.py`

Hằng số `{ticker: (ngày quyết định, lý do)}` — IVS và TMG, cùng ngày `2026-07-21`, kèm nguyên văn
lý do (ADV, ROE_Trailing, IC nhóm CTCK, `Volume_3M_P50=0`) để bản ghi drop tự giải thích được.

**Vì sao hằng số trong CODE, không phải file CSV** (đây là lựa chọn thiết kế chính, §2 simplicity):
- File CSV thêm **đúng một fail-mode mới**: thiếu/hỏng file ⇒ fail-open ⇒ **im lặng thôi loại**.
  Mà lỗ hổng ta đang vá chính là *"danh sách chỉ sống ở chỗ ai cũng có thể quên/xoá"*.
- Hằng số **không thể bị xoá âm thầm**, và muốn sửa phải qua version control + review — cùng lý
  lẽ đã ghim ở `trading_bot/plan.py::CAPIT_LEVER_APPROVED_*`.
- Không cần thêm entry `kb/data_registry/` (không sinh nguồn dữ liệu mới).

**KHÔNG có TTL, KHÔNG tự hết hạn.** Một cơ chế tự hết hạn sẽ âm thầm mở lại một quyết định của
user (coding_guidelines §20; cảnh báo arch-reviewer về việc để CRON tự đóng quyết định đang treo).
Muốn bỏ một mã: user ra chỉ đạo → sửa code → review.

**Tôn trọng ngày quyết định** (`date <= asof`, cùng mốc `asof` như cờ forensic): replay/backtest một
ngày **trước** 07-21 sẽ KHÔNG chặn ⇒ không mang hindsight vào quá khứ. Selfcheck ghim cả 2 biên.

**Bất biến với số pin R3**: selfcheck assert mọi mục có ngày **> `AUDIT_END=2026-06-19`** ⇒ drop 0
event trong cửa sổ backtest ⇒ **không đổi một chữ số nào** của R3. Đây là gate quản trị, không
phải tham số tối ưu ⇒ DSR/PBO không áp dụng.

### 4.2 Tầng LỆNH: `filter_lag_governance_orders()` trong `trading_bot/plan.py`

Tầng tín hiệu chặn IVS **trở thành ứng viên**; nó KHÔNG chặn được dòng
`{"ticker":"IVS","book":"LAG","side":"buy"}` viết thẳng vào plan JSON — **và đó chính là tầng mà
sự cố 07-23 xảy ra**. `lag_forensic_filter.py` tự ghi trong docstring rằng lưới tầng lệnh
**CHƯA có** và để làm việc mở; hàm này đóng nó, cho **cả 3 nguồn** (BANNED + user-loại + forensic).

- **Dùng lại nguyên** `lag_filter_forensic_banned` qua `_governance_gate_deps()` — không nhân bản
  danh sách. Selfcheck assert cơ học: thân hàm (sau khi bỏ chuỗi) **không chứa** `IVS`/`TMG`/
  `BANNED`/`frozenset`.
- **Phạm vi hẹp, có kiểm**: chỉ `side=buy` **và** `book=LAG`. Lệnh **BÁN** IVS **không** bị chặn
  (thoát vị thế phải luôn đi được); IVS ở book BAL/CAPIT/parking **không** bị chặn.
- **Fail-mode đồng bộ tầng tín hiệu**, không tự sáng tác: 2 hằng số fail-closed tuyệt đối; CSV
  forensic hỏng → fail-open **đúng nguồn đó** + bản ghi `FAIL_OPEN_FORENSIC` báo to (2 hằng số
  vẫn chặn); gate không import được → `FAIL_OPEN` + báo to.
- Vị trí cascade: `filter_excluded → net → cap_capit → cap_lag → rating → **governance** → lever
  → approval`.

---

## 5. Verify — bằng chứng chạy thật, không phải đọc code

| Kiểm | Kết quả |
|---|---|
| `lag_forensic_filter_selfcheck.py` (33 ca, +11 ca mới) | **33/33 PASS** |
| `lag_governance_order_gate_selfcheck.py --live` (37 ca) | **37/37 PASS** |
| Cả 2, ở `env -u TZ` / `UTC` / `America/New_York` / `Asia/Ho_Chi_Minh` | **giống nhau tuyệt đối** (§16) |
| **Rổ ứng viên LAG THẬT hôm nay** | IVS + TMG bị loại với `kind="user_exclude"`; 18 mã khác vẫn loại đúng nguồn cũ (banned/forensic) |
| **Replay 47 plan THẬT** (`data/trade_plans/`, 07+08) | **0 lệnh bị đổi ngoài ý muốn** |
| **Replay sự cố 07-23** | IVS 2.903cp (18M @6.200đ, dựng từ chính field note của plan thật) + 1.800cp SpaceX + 2.750cp ZaloPay → **CHẶN cả 3** |
| Hồi quy gate lân cận | `lag_rating_order_gate_selfcheck` 14/14, `excluded_tickers_selfcheck` all-pass |
| Patch tự đủ | áp patch từ repo sạch → **70/70 PASS**, `py_compile` OK |
| Production | `git status` **sạch** (0 file đổi) |

### 5.1 Hai điều selfcheck bắt được (ghi lại vì đúng tinh thần verify-before-done)

1. **`--live` ban đầu "PASS vì không tìm thấy gì".** Glob của tôi trỏ `data/plan_*.json` trong khi
   plan thật ở `data/trade_plans/` ⇒ replay **0 file**. Bắt được vì có assert `>= 1`; đã thêm hẳn
   một ca `check("tìm được file plan THẬT để replay", len>=10)` để cái bẫy đó không tái diễn.
2. **Artifact của sự cố 07-23 KHÔNG CÒN trên đĩa.** `plan_SpaceX_2026-07-23.json` có
   `orders: []` + `regenerated_note` ("Regenerated 2026-07-23 sau khi user xác nhận…"); IVS chỉ
   còn trong `lag_upcoming_notes.entry_07_24.IVS` (`effective_buy_vnd: 18000000`, ref 6.200đ).
   ⇒ Đúng hiện tượng **re-plan ghi đè** mà việc **A2** đã nêu, quan sát được lần thứ hai ở một
   file khác. Nên `--live` **không** assert "chặn được IVS trên plan thật" (sẽ là assert sai sự
   thật); nó dựng lại đơn hàng từ chính các field note đó — số 2.903cp là **suy ra từ dữ liệu
   thật**, không bịa.

---

## 6. Quan sát KHÔNG sửa (để Mike quyết) — thứ tự cổng làm mờ audit trail

Cascade tầng tín hiệu hiện là `liq → rating → forensic/governance`. Vì gate quản trị chạy
**cuối**, hôm nay IVS bị `rating` loại trước, nên `status.json` sẽ ghi lý do
*"RATING_FAIL 8L=5"* — **đúng nhưng là lý do ngẫu nhiên**, không phải *"user đã loại 07-21"*.

- **An toàn không phụ thuộc thứ tự**: nếu `rating`/`liq` fail-open (nguồn hỏng), gate quản trị vẫn
  chặn. Phòng thủ nhiều lớp hoạt động ở mọi thứ tự.
- Giá trị của việc đổi thứ tự là **thuần audit trail**. Chi phí là đổi log của các mã khác.
- **KHÔNG tự đổi** (§3 surgical). Nêu ra để Mike quyết có muốn `governance` chạy trước `liq`
  không.

---

## 7. Trạng thái & việc cần Mike làm

**CHƯA WIRE.** Áp patch:

```bash
cd /home/trido/thanhdt/WorkingClaude
git apply mike/agents/Taylor/research/lag_user_exclude_a4_20260804.patch
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
$DNA_PYEXE lag_forensic_filter_selfcheck.py                       # kỳ vọng 33/33
$DNA_PYEXE lag_governance_order_gate_selfcheck.py --live           # kỳ vọng 37/37
```

Patch gồm 5 file: `lag_forensic_filter.py` (+67), `trading_bot/plan.py` (+94),
`bot_execute.py` (+13), `lag_forensic_filter_selfcheck.py` (+63),
`lag_governance_order_gate_selfcheck.py` (mới, 281).

**Cần quant-skeptic trước khi wire** (thay đổi production). Lưu ý cho vòng review: đây là **cổng
an toàn/quản trị**, không có ngưỡng nào dò từ dữ liệu ⇒ DSR/PBO không áp dụng; luận điểm "không
đổi số pin R3" là **kiểm được cơ học** (mọi mục có ngày > `AUDIT_END`, có assert trong selfcheck).

**Việc còn mở, KHÔNG làm trong job này**: nếu Mike muốn `governance` đứng trước `liq`/`rating` ở
tầng tín hiệu (§6) thì đó là một patch riêng, có blast radius log của mã khác.
