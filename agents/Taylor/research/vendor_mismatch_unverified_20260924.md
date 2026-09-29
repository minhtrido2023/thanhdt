# Vendor mismatch ⇒ HẠ VỀ UNVERIFIED + raise warning — job `Taylor_20260923_235405`

**Ngày**: 2026-09-24 · **Nhánh**: `fix/vendor-mismatch-unverified` (worktree `mike/wt-vendor-mismatch`)
**Commit**: `c35e4925` (code) + `8989d80e` (ngưỡng đo thật + vỏ selfcheck)
**CHƯA LAND** — chạm số công bố cho nhà đầu tư (§21), chờ arch-review + Mike/user.

Chỉ đạo user 2026-09-24 06:5x: *"Nếu vendor mismatch thì hạ về unverified rồi raise warning lên
để tôi kêu Winston xử lý."*

---

## 1. Lỗ hổng (arch-review dựng, KHÔNG điều tra lại)

`resolve_dividends` dòng 963: nhánh `kind == "CASH_CONFIRMED"` thắng TRƯỚC `elif adj.vendor_stock > 0`
(dòng 977). Sau khi call-site 3 (`1608a267`) mở cho sự kiện VỪA-TIỀN-VỪA-CỔ-PHIẾU giải được cổ
tức tiền, một sự kiện như vậy đi vào nhánh đầu và nhãn `STOCK_CONFIRMED` của vendor bị TƯỚC.
`vendor_check="mismatch"` còn lại **chỉ là một ghi chú**, và `grep` toàn repo: **không một consumer
nào đọc `vendor_check`**. Hệ quả đo được trên ca công bố arch-reviewer dựng:

```
sau solve: CASH_CONFIRMED broker_solved per_share=1.000  vendor_cash lệch 50%
kind VẪN LÀ CASH_CONFIRMED  →  cash_per_share = 1.000    (qua cổng công bố)
PositionReturn.unverified   →  []                        (0 cảnh báo)
số CÔNG BỐ: −8,20%  (chỉ-giá −12,00%)
```

Tức: hai nguồn ĐỘC LẬP lệch 50% mà vẫn ra một tỉ suất công bố, im lặng.

## 2. Bản vá

### 2a. `bin/dividend_adjusted_return.py` — hạ cấp + lý do có số

`vendor_check == "mismatch"` ⇒ `kind = "UNVERIFIED"`. Hai hệ quả có sẵn trong file tự động bật:
`cash_per_share` trả 0 (chỉ nhả `CASH_CONFIRMED`) và `PositionReturn.unverified` nhặt sự kiện lên.
Lý do ghi vào `note` (consumer đọc `note`, không đọc `vendor_check`) với **đủ 3 số + đích danh
người xử lý** — §29, không phải câu chung chung:

```
LỆCH NGUỒN: broker giải 1,000đ/cp, vendor `corporate_action` khai 1,500đ/cp (lệch 50.0%)
⇒ HẠ VỀ UNVERIFIED, KHÔNG công bố tỉ suất cho mã này — cần Winston (data-ops) đối soát
nguồn vendor với sổ broker
```

Ngưỡng tách thành hằng số `VENDOR_MISMATCH_REL = 0.01` / `VENDOR_MISMATCH_ABS = 1.0` (giữ nguyên
giá trị đã chạy từ 2026-08-13, xem §4).

### 2b. `bin/report_return_gate.py` — kênh cảnh báo (lựa chọn + lý do)

**Chọn `report_return_gate`, KHÔNG chọn `report_delivery_gate`.** Lý do: `report_return_gate` là
nơi DUY NHẤT trong repo gọi `resolve_dividends` thật (`entitled_gross`), nên nó là chỗ duy nhất
biết được sự kiện nào lệch mà không phải query lại BQ; và output của nó đi thẳng vào đường giao
hàng (`report_delivery_gate.py:244` gọi nó), nên cảnh báo tới được user qua đúng kênh báo cáo
đang dùng. Đặt ở `report_delivery_gate` thì phải dựng lại toàn bộ ngữ cảnh (rổ mã, tài khoản,
cửa sổ ex-date) — vừa trùng lặp vừa thêm một nguồn có thể lệch với cái đang kiểm.

Ba điều chỉnh:

1. `entitled_gross` trả `(gross, mismatches)` thay vì chỉ `gross`. Trước đây sự kiện bị hạ cấp sẽ
   **lặng lẽ biến mất khỏi kỳ vọng** — và cổng kết luận từ SỰ VẮNG MẶT đó là "mã này không có cổ
   tức", đúng cái §28 cấm.
2. `run_gate` **LUÔN in khối `⚠️ LỆCH NGUỒN VENDOR`** kèm hai số + % lệch + câu "cần Winston
   (data-ops) đối soát", kể cả khi cổng PASS. Đây chính là "raise warning mà KHÔNG chặn báo cáo
   im lặng": báo cáo không công bố mã đó thì vẫn đi được, nhưng user vẫn thấy để gọi Winston.
3. **CHẶN (`rc=1`) chỉ khi mã đó đang được CÔNG BỐ tỉ suất** trong báo cáo (bảng hoặc văn xuôi) —
   nhất quán với triết lý sẵn có của cổng ("không công bố thì không sai được", khối `nocover`).
   Thông điệp chặn nằm ở **khối riêng**, không trộn vào `fails`, để không bị câu gợi ý sai nguyên
   nhân ("sai cơ sở giá" / "quên cộng cổ tức") dẫn người sửa đi lạc (§29).

### 2c. `bin/dividend_adjusted_return_selfcheck.py` (MỚI, 3 dòng)

Selfcheck của `dividend_adjusted_return.py` nhúng trong chính nó (`--selfcheck`) nên TÀNG HÌNH với
cả hai runner: `run_selfchecks.sh` tìm `-iname "*selfcheck*.py"`, `selfcheck_weekly_baseline_check.sh`
tìm `"*_selfcheck.py"`. Vỏ này chỉ để cái tên lọt vào hai mẫu đó.

## 3. Kiểm chứng (số THẬT)

| Hạng mục | Kết quả |
|---|---|
| `dividend_adjusted_return.py --selfcheck` | **137 PASS / 0 FAIL** (trước: 120) |
| `report_return_gate.py --selfcheck` | **60/60** (trước: 53/53) |
| 5 timezone (`env -u TZ`, UTC, America/New_York, Pacific/Kiritimati, Asia/Ho_Chi_Minh) | 137/0 và 60/60 ở CẢ 5 |
| Mutation | **5/5 CHẾT bằng assertion có tên** |
| Acceptance dữ liệu THẬT | gate master vs branch trên `SpaceX_daily_report_2026-09-23.md` và `ZaloPay_daily_report_2026-09-23.md`: **rc=0 cả 4 lượt, output BYTE-IDENTICAL** |
| Selfcheck theo phạm vi (§23) | `report_return_gate_selfcheck` PASS · `reconcile_equity_realized_selfcheck` 32/0 · `worktree_stale_check_selfcheck` PASS · `report_delivery_ledger_selfcheck` **FAIL 35/40 — TIỀN TỒN TẠI** (xem dưới) |

**5 mutation** (mỗi cái revert đúng một mảnh của bản vá, chạy `python3 -B` + xoá `__pycache__`):

| # | Mutation | Assertion giết |
|---|---|---|
| M1 | mismatch vẫn giữ `CASH_CONFIRMED` | `MUTATION-GUARD vendor_mismatch_downgrade` |
| M2 | lý do bỏ tên Winston | `MUTATION-GUARD vendor_mismatch_reason` |
| M3 | cổng không CHẶN mã đang công bố | `MUTATION-GUARD gate_vendor_mismatch_block` |
| M4 | cảnh báo thành câu chung chung (§29) | `MUTATION-GUARD gate_vendor_warning_always` |
| M5 | bỏ hẳn khối cảnh báo vendor | `MUTATION-GUARD gate_vendor_mismatch_block` |

Selfcheck mục 24 còn có **ca chống hồi quy**: vendor KHỚP (kể cả khi có chân cổ phiếu) ⇒ vẫn công
bố 1.000đ/cp bình thường; hai ca sát ngưỡng 0,9% (match) và 1,1% (mismatch); ba nhánh
`broker_only` / `CASH_VENDOR` / `STOCK_CONFIRMED` không đổi hành vi một chút nào.

**`report_delivery_ledger_selfcheck` FAIL là TIỀN TỒN TẠI, không phải hồi quy.** Chứng minh: chạy
đúng file đó (a) trên cây canonical ⇒ **40/40 PASS**; (b) từ worktree `agents/wt-treasury-table`
(nhánh `feat/treasury-share-events-table`, KHÔNG đụng file nào của tôi) ⇒ **35/40 FAIL, y hệt 5
test**. Tức selfcheck này hỏng khi chạy TỪ BẤT KỲ worktree nào — cùng lớp lỗi dirname-counting đã
ghi nhận ở `nav_cum_dividend_selfcheck.py:34`. Ngoài phạm vi job này, đã ghi lại.

## 4. K1 — bao nhiêu mã/sự kiện rơi vào mismatch trong 6 tháng?

**0 (không).** Đo THẬT bằng `agents/Taylor/exp_vendor_mismatch/measure_k1.py` — 39 mã hai tài
khoản từng nắm giữ (trích từ `positions` trong `dnse_raw_*.jsonl`), cửa sổ **2026-03-24 → 2026-09-24**:

| `kind` | `vendor_check` | n |
|---|---|---|
| CASH_CONFIRMED | match | **6** |
| CASH_VENDOR | vendor_only | 17 |
| STOCK_CONFIRMED | vendor_only | 14 |
| UNVERIFIED | unavailable | 25 |
| | **mismatch** | **0** |

Chỉ 6/62 sự kiện đủ điều kiện đối soát (broker giải được **và** vendor có số tiền), và **cả 6 khớp
đúng từng đồng**: MBB 09/07 1.000 · CTG 23/07 450 · VCB 23/07 450 · NCT 27/07 8.000 · SAB 28/07
3.000 · DGC 14/09 8.000.

⇒ **Không có cảnh báo nhiễu hàng ngày.** Cổng này chưa từng kêu một lần nào trong 6 tháng. Vì thế
tôi **KHÔNG nới ngưỡng** (1% tương đối, sàn 1đ/cp, giữ nguyên từ 2026-08-13): nới một cổng chưa
từng kêu là nới mù. Nếu về sau nó kêu đều thì đó mới là dữ liệu để bàn ngưỡng.

Lưu ý thêm (đáng chú ý cho arch-review): trong 6 tháng **không có sự kiện CASH_CONFIRMED nào có
`vendor_stock > 0`** — tức cái cửa mà call-site 3 mở ra hiện vẫn hoàn toàn LATENT. Ca đầu tiên có
thể rơi vào VPB 24/09 (ex-date hôm nay), nên vá TRƯỚC khi nó thành số công bố là đúng thời điểm.

## 5. K2 — có mã nào đang công bố bình thường mà sau bản vá sẽ MẤT số?

**Không có mã nào.** Hai bằng chứng độc lập:

1. Từ K1: 0 sự kiện mismatch ⇒ 0 sự kiện bị hạ cấp ⇒ 0 mã mất cổ tức khỏi kỳ vọng.
2. Acceptance end-to-end: `report_return_gate` chạy THẬT trên hai báo cáo daily 2026-09-23 của cả
   hai tài khoản, master vs branch — **rc=0 cả bốn lượt và output byte-identical**. Không một dòng
   nào đổi, không một `⚠️ LỆCH NGUỒN VENDOR` nào xuất hiện.

Nói cách khác: **bản vá hôm nay là NO-OP trên toàn bộ dữ liệu đang có**, nó chỉ đóng một cánh cửa
trước khi cái đầu tiên đi qua. Đây là điều kiện Mike hỏi để quyết land — và nó thuận.

## 6. K3 — bản vá có đóng được bus question `can-user-quyet-mo-cong-CASH_VENDOR` không?

**KHÔNG. Chỉ liên quan một phần, và nó đi NGƯỢC chiều.**

- Câu hỏi đó (2026-08-13, `kb/projects/cash-vendor-gate-tracking.md`, user chốt GIỮ ĐÓNG 2026-08-15)
  hỏi: *có MỞ cổng cho `CASH_VENDOR` — dùng số vendor khi broker KHÔNG giải được — vào báo cáo NĐT
  không?*
- Bản vá này xử lý tình huống ngược: broker **ĐÃ** giải được mà vendor **BẤT ĐỒNG** ⇒ siết chặt
  thêm. Nó không chạm dòng `cash_per_share` (vẫn chỉ nhả `CASH_CONFIRMED`), và selfcheck có ca
  chứng minh `CASH_VENDOR` vẫn bị chặn y nguyên.
- Phần LIÊN QUAN: nó bổ sung bằng chứng cho điều kiện mở lại. Điều kiện của user là **CẢ HAI**:
  (1) ≥1 sự kiện ISS/hỗn hợp mà vendor **và** broker cùng xác nhận; (2) ≥1 tháng kể từ 2026-08-13.
  Đo hôm nay: (2) **ĐÃ ĐẠT**; (1) **CHƯA** — trong rổ 39 mã hai tài khoản nắm giữ, số sự kiện hỗn
  hợp (DIV+ISS cùng mã, cùng ex-date, `executed`) kể từ 2026-08-13 là **0** (toàn thị trường có 8
  ca hỗn hợp và 56 ca ISS thuần, nhưng không ca nào rơi vào rổ nên broker không thể xác nhận).
  Mẫu đối soát cũng mới nhích từ n=6 (tháng 07) lên n=6 + DGC 14/09 — vẫn **toàn cổ tức tiền mặt
  thuần**, đúng cái giới hạn user nêu.

⇒ Đề nghị: giữ question MỞ, cập nhật `cash-vendor-gate-tracking.md` bằng số đo 09-24 ở trên.
Không tự đóng.

## 7. Chỗ chỉ đạo còn sai / tôi làm khác — nói thẳng

1. **"hạ về UNVERIFIED nghĩa là không công bố tỉ suất cho mã đó" — hạ cấp MỘT MÌNH nó KHÔNG làm
   được điều đó.** `kind="UNVERIFIED"` chỉ làm cổ tức về 0; báo cáo khi đó công bố con số **chỉ
   giá** (−12,00% trong ca gốc) trông hoàn toàn bình thường, và cổng vẫn PASS vì kỳ vọng của nó
   cũng tụt theo. Nghĩa là nếu chỉ làm đúng chữ của chỉ đạo thì ta đổi một con số SAI-vì-thừa
   (−8,20%) lấy một con số SAI-vì-thiếu (−12,00%), vẫn im lặng. Vì vậy tôi thêm nhánh CHẶN ở
   `report_return_gate` cho mã đang công bố — đó mới là cái thực thi được câu "không công bố tỉ
   suất cho mã đó".
2. **"raise warning ... KHÔNG chặn báo cáo im lặng" là hai yêu cầu có thể xung đột.** Tôi tách
   làm hai: cảnh báo IN RA luôn luôn (kể cả PASS) — không im lặng; CHẶN chỉ khi mã đó thực sự
   đang được công bố — không chặn thừa. Nếu user muốn "không bao giờ chặn, chỉ cảnh báo", gỡ đúng
   một dòng `vendor_fails.append(line)` là xong (mutation M3 chứng minh dòng đó là điểm duy nhất
   quyết định chặn/không).
3. **Ngưỡng: tôi KHÔNG nới và cũng không đề xuất nới** (mục 3 của dispatch cho phép đề xuất). Lý
   do đã nêu: 0/6 ca kêu trong 6 tháng, chưa có dữ liệu để chỉnh.
4. **Không đụng `PositionReturn` / `cash_per_share`**: hai hệ quả (chặn số, nổi cảnh báo) đã có
   sẵn trong file và tự bật khi `kind` đổi — thêm nhánh riêng chỉ làm tăng đường đi mà không tăng
   bảo vệ (§2/§3).

## 8. Việc còn mở sau job này

- **CHƯA LAND** — chờ arch-review + Mike/user duyệt (chạm §21).
- `report_delivery_ledger_selfcheck.py` FAIL từ MỌI worktree (35/40, pre-existing, cùng lớp
  `nav_cum_dividend_selfcheck.py:34`) — chưa ai nhận.
- Bus question `can-user-quyet-mo-cong-CASH_VENDOR` giữ MỞ; cần cập nhật số đo 09-24 vào
  `kb/projects/cash-vendor-gate-tracking.md` (file `kb/` ⇒ §13, ghi `.proposed` hoặc để Mike sửa).
