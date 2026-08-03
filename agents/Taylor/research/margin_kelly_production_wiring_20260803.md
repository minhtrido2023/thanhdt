# Đòn bẩy margin sleeve CAPIT — TRIỂN KHAI vào production (DISABLED)

**Job**: `Taylor_20260803_133001` (resume của `Taylor_20260803_122554` bị cắt vì `--max-turns`)
**Ngày**: 2026-08-03 · **Tác giả**: Taylor · **Trạng thái**: wire xong, **`enabled: false`**, chờ 1 bước xác nhận riêng của user
**Loại**: triển khai (KHÔNG phải nghiên cứu thêm) — cơ sở là chuỗi p1–p5 cùng ngày, đã đóng

---

## 0. Tóm tắt một đoạn

Đã wire trọn đường đòn bẩy margin cho **riêng sleeve CAPIT** — từ tầng chính sách (`trading_rules.json`)
→ tầng tín hiệu (`golive_recommend_v23.py`) → tầng cascade plan (`plan.py::apply_capit_lever`) → tầng
broker (`brokers.py`, gói vay per-order) → lưới an toàn runtime (`executor.py::_lever_package_audit`).
Phạm vi **đúng bản user duyệt, không rộng hơn**: f=1,3 · cổng `dd52<=-20%` · gói DNSE 1840 "RocketX" ·
chỉ account SpaceX. Tính năng **ĐANG TẮT**: `capit_margin_lever.enabled = false`.

Bằng chứng "0 thay đổi hành vi sống": chạy cascade thật trên **50 lệnh của 24 plan LIVE có thật**
(SpaceX + ZaloPay, gồm cả plan 2026-07-21 có 5 lệnh CAPIT thật) → **0 thay đổi, 0 lệnh mang cờ vay**.

**Không có lệnh thật nào được đặt. Không có `loanPackageId` nào của tài khoản bị đổi qua API.**

---

## 1. Phạm vi user duyệt vs code thực tế

| Trục | User duyệt (2026-08-03) | Code thực tế | Ghim ở đâu |
|---|---|---|---|
| Sleeve | CHỈ CAPIT, chỉ lệnh MUA của sự kiện vừa fire | `_is_capit_buy(o)` = `book=="CAPIT" and side=="buy"` | `plan.py::apply_capit_lever` |
| Cổng | `dd52 <= -20%` (trục DUY NHẤT sống sót p1–p5) | `CAPIT_LEVER_DD52_PCT = -20.0`, **và** `capit_signal_today and capit_size>0.005 and basket` | `golive_recommend_v23.py` §6a |
| Hệ số | f = 1,3 cố định | `CAPIT_LEVER_APPROVED_F = 1.3` | hằng trong CODE (xem §2.1) |
| Gói vay | 1840 "RocketX", 12,5%/năm | `CAPIT_LEVER_APPROVED_PACKAGE = 1840`; gói default account **giữ nguyên 1841** | hằng trong CODE |
| Account | CHỈ SpaceX | `CAPIT_LEVER_APPROVED_ACCOUNTS = ["SpaceX"]` | hằng trong CODE |
| Trạng thái | **PHẢI tắt** | `enabled: false` | `data/trading_rules.json` |

Cổng **KHÔNG** dùng valuation (bác ở p1 §4.1) và **KHÔNG** dùng NEUTRAL-only (chưa đủ bằng chứng p3) —
đúng như phạm vi duyệt.

### 1.1 Một quyết định thiết kế đáng nêu: phạm vi ghim trong CODE, không chỉ trong JSON

`data/trading_rules.json` khớp `.gitignore` (`*.json`) ⇒ **không có diff, không blame, không backup**
nào canh nó. Nếu f và danh sách account chỉ sống trong JSON thì một lần sửa `f: 5.0` hoặc thêm
`"ZaloPay"` là thay đổi **tiền thật mà không để lại dấu vết**.

Vì vậy JSON chỉ giữ quyền **BẬT/TẮT** (công tắc vận hành); **nới phạm vi** thì phải sửa 3 hằng
`CAPIT_LEVER_APPROVED_*` trong `golive_recommend_v23.py` và đi qua review. JSON lệch khỏi 3 hằng đó ⇒
**coi như TẮT** (`capit_lever_policy()` trả `err`). Selfcheck A10 kiểm đúng 3 kịch bản nới lén
(f=5.0 / thêm ZaloPay / gói 9999) — cả 3 đều TẮT.

---

## 2. Từng file đổi

`git diff --stat` (10 file tracked, +531/−21) + 1 file mới untracked + 1 file gitignored:

| File | Δ | Việc |
|---|---|---|
| `data/trading_rules.json` | *(gitignored)* | Khối `capit_margin_lever` mới — `enabled:false`, f/gate/gói/scope/accounts + evidence p1–p5 + `known_limits` |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | +169 | `capit_lever_policy()`, 3 hằng phạm vi, §6a công bố khối `capit_lever` ra artifact, 1 dòng báo cáo |
| `trading_bot/plan.py` | +155 | `PlannedOrder.lever_f`/`.loan_package_id`; **`apply_capit_lever()`** — điểm thực thi DUY NHẤT |
| `trading_bot/brokers.py` | +82/−12 | `place_order(..., loan_package_id=)` cho cả 4 lớp broker; `DNSEBroker._validate_lever_package()`; `PaperBroker` ghi lại gói vay |
| `trading_bot/executor.py` | +106/−3 | **`_lever_package_audit()`** + nối vào `step()`; 3 call-site `place_order` truyền gói vay |
| `bot_execute.py` | +15/−2 | Gọi `apply_capit_lever` trong cascade + in log |
| `capit_lever_selfcheck.py` | +717 (mới) | 74 kiểm tra, 7 nhóm A–G |
| 5 selfcheck cũ | +25/−6 | Thêm kwarg `loan_package_id=None` vào FakeBroker; 1 assert quá chặt được nới (xem §5.2) |

**Không file nào khác bị chạm.** Các file `M` khác trong `git status` (`data/*.md`, `data/rank_8l.md`,
`data/lag_liq_ledger.csv`, …) là sản phẩm cron vận hành hằng ngày, **không** thuộc job này và
**không** được commit ở đây.

### 2.1 Kiến trúc — một chỗ cấp, một chỗ soi

```
trading_rules.json (BẬT/TẮT)  ──┐
                                ├─→ golive §6a ─→ golive_v23_status.json::capit_lever  (CÔNG BỐ)
3 hằng APPROVED_* trong code ───┘                          │
                                                           ▼
   bot_execute cascade:  filter_excluded → net → cap_capit → cap_lag → lag_rating
                                                → **apply_capit_lever** → approval     (CẤP + GỠ)
                                                           │
                                                           ▼
                       executor._place_slices → brokers.place_order(loan_package_id=)  (THỰC THI)
                                                           │
                       executor.step() → **_lever_package_audit(updates)**             (SOI SỔ BROKER)
```

Hai điểm cần nhấn:

**(a) `apply_capit_lever` là hàm HAI CHIỀU, và chiều thứ hai mới là lý do nó tồn tại.** Nó không chỉ
*cấp* cờ vay cho lệnh CAPIT hợp lệ — nó **GỠ SẠCH** `lever_f`/`loan_package_id` khỏi mọi lệnh khác,
kể cả khi plan tự ghi sẵn. Plan là JSON do LLM (DollarBill) sinh hoặc người sửa tay; một dòng
`"loan_package_id": 1840` viết thẳng vào plan mà không có hàm này sẽ đi tới broker và tạo **đòn bẩy
không ai duyệt**. Quyền không nằm ở nơi sinh plan — đúng tinh thần `coding_guidelines.md` §7
(`filter_excluded_tickers`/`cap_capit_orders`). Selfcheck C5/C6/C7 kiểm đúng kịch bản này.

**(b) Đặt CUỐI cascade** để nhìn thấy tập lệnh chung cuộc: lệnh đã bị các trần/gate ở trên loại thì
không cần và không được gắn cờ vay.

### 2.2 Trần VND — chặn hình dạng bug 07-21

"Được vay" mà không kèm trần khối lượng chính là hình dạng của bug CAPIT 2026-07-21 (nhân `capit_size`
hai lần, thiếu 87,1tr). Với gói 1840 (`initialRate` 0,5 ⇒ **sức mua gấp đôi**, Mafee đo 2026-08-03),
một sai số sizing của tầng sinh plan sẽ bị chặn bởi *2× sức mua* thay vì bởi tiền mặt — tức là muộn
hơn và đắt hơn. `cap_capit_orders` chỉ chặn %ADV/mã, **không** chặn mục tiêu vốn.

Nên `apply_capit_lever` tự soi giá trị lệnh so với `capit_slot_target_vnd_levered` (đệm 10% cho làm
tròn lô): **vượt trần ⇒ GỠ đòn bẩy, lệnh VẪN chạy bằng vốn tự có** (under-deploy là sai số lành; vay
quá mức là margin call). Artifact bật đòn bẩy mà **thiếu** trần ⇒ fail-closed, không cấp. Selfcheck
C14–C17.

### 2.3 f được nhân ĐÚNG MỘT LẦN

`golive` §6a: `capit_total_target_vnd_levered = capit_total_target_vnd × f`, và **trường gốc giữ
nguyên giá trị** (tầng dưới không đổi nghĩa — selfcheck B3). `apply_capit_lever` **không đụng
sizing/qty**, chỉ quyết định lệnh đi ra bằng gói vay nào. Trần %ADV `capit_adv_caps` **KHÔNG** nhân f
(trần đo tác động thị trường, độc lập nguồn vốn) — selfcheck B2.

---

## 3. Lưới an toàn runtime (`coding_guidelines.md` §5)

`_ghost_tickers()` trả lời "*có lệnh nào ở broker mà state không biết không*" (chống double-buy) — nó
đã phủ cả lệnh CAPIT vì xét theo mã. Cái nó **không** trả lời được, và là rủi ro MỚI mà đòn bẩy mang
vào: "*lệnh đó đi ra bằng gói vay NÀO*". Một lệnh **đúng mã, đúng KL**, nhưng mang gói 1840 trong khi
chính sách đang TẮT là đòn bẩy không ai duyệt — nợ thật, rủi ro margin call thật, mà **mọi phép đối
soát KL/mã đều PASS**.

`_lever_package_audit()` đọc `loanPackageId` thật trên sổ lệnh broker sống, so với tập mã mà cascade
đã cấp phép; lệch ⇒ **fail-safe-pause** mã đó qua đúng đường xử lý ghost order (`ghost_tickers |=
lever_pause`) + journal `LEVER_PACKAGE_UNAUTHORIZED` + bus event. **Không tự huỷ lệnh** (huỷ mù còn
rủi ro hơn: có thể đã khớp một phần).

**Guard vũ trang NGAY CẢ KHI tính năng tắt** (selfcheck E4) — đây là điểm arch-reviewer bắt được ở
vòng trước và đã sửa: nếu guard chỉ đọc khoá `capit_lever` của artifact thì nó **đang tắt trong
production**, vì artifact hôm nay (`signal_date 2026-08-03`) **chưa có khoá đó** (golive chưa chạy lại
với code mới) — tức lưới an toàn sẽ ngủ đúng giai đoạn tính năng mới vào và rủi ro sai sót cao nhất.
Sửa: đọc **hai nguồn** (`golive_v23_status.json` **và** `trading_rules.json`, hợp lại) — `trading_rules.json`
khai gói 1840 kể cả khi `enabled=false`, nên guard có gói để soi ngay từ bây giờ. Đã xác minh trực
tiếp trên đĩa:

```
'capit_lever' in artifact : False      (golive chưa chạy lại ⇒ nguồn 1 câm)
trading_rules.loan_package_id : 1840   (nguồn 2 vẫn cấp gói ⇒ guard VŨ TRANG)
```

---

## 4. Diễn tập (rehearsal) — trên CHÍNH source production, không phải bản chép

Hiện **không có sự kiện washout thật** nào đạt cổng để test sống (`capit_signal_today=False`,
`n_capit_basket=0`), nên diễn tập chạy bằng **sự kiện washout giả lập** `dd52=-25%`.

Điểm quan trọng về phương pháp: khối §6a trong `golive_recommend_v23.py` được kẹp giữa hai mốc
`# CAPIT_LEVER_BEGIN` / `# CAPIT_LEVER_END`, và selfcheck **cắt đúng đoạn source giữa hai mốc rồi
`exec` nó** với đầu vào giả lập. Diễn tập vì thế chạy **trên chính code production**, không phải một
bản chép tay sẽ trôi khỏi nó (bài học §17 extract-and-test — tuyên bố "đã kiểm" mà không có test neo
vào source thật đã hỏng 2 lần trong fleet này). Đổi/di chuyển hai mốc ⇒ selfcheck fail ngay, đó là
chủ đích.

**Kết quả `capit_lever_selfcheck.py` — 74 PASS / 0 FAIL**, tôi chạy lại **độc lập** dưới `env -u TZ`
(kỷ luật skill `verify-before-done`; log gốc `mike/logs/capit_lever_selfcheck_20260803.log`):

| Nhóm | n | Nội dung |
|---|---|---|
| A. Chính sách | 20 | Đọc `trading_rules.json`; **`enabled` phải là literal JSON `true`** (§4.1); f<1/scope lạ/thiếu gói ⇒ TẮT; A10 nới phạm vi lén ⇒ TẮT; A6/A7 file THẬT trên đĩa đang `enabled=false` |
| B. Tín hiệu §6a | 13 | Cổng đạt ⇒ `active=true` + slot levered = ×1,3; trường gốc giữ nguyên; ZaloPay không bị chạm; cổng chưa đạt / không có sự kiện CAPIT / `capit_size~0` ⇒ TẮT; **B8b sentinel −99,0 ⇒ TẮT** (§4.2); B8c −60% (sụp thật) ⇒ VẪN cấp |
| C. Cascade plan | 18 | Cấp cho CAPIT buy; **không** cho BAL/LAG/bán/ZaloPay/cash_only; **GỠ** cờ plan tự khai; ghi đè f=9,9→1,3; artifact thiếu/stale ⇒ fail-closed; C14–C17 trần VND |
| D. Broker | 6 | Gói 1840 hợp lệ ⇒ dùng; không hợp lệ / mạng lỗi ⇒ rơi về default 1841 (**KHÔNG bỏ trắng** — §4.3); lệnh thường ⇒ `None`, hành vi cũ nguyên vẹn |
| E. Lưới runtime | 8 | Gói lạ ⇒ tạm dừng mã; gói default ⇒ không báo động giả; **E4 guard vũ trang cả khi tắt**; E6 `step()` THẬT nối được sang tầng đặt lệnh; E7 ghi bus |
| F. **Diễn tập đầu–cuối** | 8 | **BẬT**: cả 5 lệnh CAPIT tới broker mang gói 1840 — cờ **không rớt ở lớp nào**; lệnh BAL cùng plan không mang gói; slot 50tr→65tr. **TẮT**: 0 lệnh mang gói, 0 trường levered, 0 dòng adj |
| G. Chốt chặn | 3 | File THẬT trên đĩa: `enabled==false`, `live_requires_user_approval==true`, phạm vi đúng bản duyệt |

Bằng chứng F2 (paper broker, cờ đi trọn đường khi BẬT):
`{'SAB': 1840, 'SIP': 1840, 'VNM': 1840, 'PVT': 1840, 'NCT': 1840}` — và F3: lệnh BAL cùng plan = `None`.
F6 (cấu hình production hôm nay, TẮT): `{'SAB': None, 'SIP': None, 'VNM': None, 'PVT': None, 'NCT': None, 'FPT': None}`.

### 4.1 `enabled` phải là literal JSON `true` — không `bool()`

Công tắc DUY NHẤT giữa "tắt" và tiền vay thật nằm trong một file JSON sửa tay/LLM sửa. `bool("false")`
là **True** — nghĩa là một lỗi gõ tầm thường (`"enabled": "false"`, có nháy) sẽ **BẬT** đòn bẩy. Code
dùng `raw_enabled is True`. Selfcheck A8 kiểm 7 biến thể (`"false"`,`"true"`,`"no"`,`"yes"`,`"0"`,`0`,`1`)
— tất cả đọc thành TẮT + báo lỗi; A9 xác nhận literal `true` thật thì vẫn bật được (sàn trên không
chặn nhầm).

### 4.2 Sàn tỉnh táo −95% — sự cố dữ liệu không được mở đường vay tiền

`dd52_now` rơi về sentinel **−99,0** khi chuỗi VNINDEX RỖNG — tức "KHÔNG CÓ DỮ LIỆU", nhưng đọc theo
nghĩa đen thì nó thoả cổng "≤ −20%" một cách ngoạn mục. Đúng hình dạng bẫy §14 (giá trị canh khuyết
bị tầng dưới hiểu thành tín hiệu cực đoan). Mọi `dd52` dưới −95% bị coi là HỎNG ⇒ TẮT. −95% chọn để
tách bạch sentinel: đáy tệ nhất lịch sử VNINDEX còn cách xa mức này — B8c xác nhận −60% (sụp thật)
**vẫn** được cấp.

### 4.3 Không lặp lại bug TV1 07-28

`kb/incidents/2026-07/2026-07-28-spacex-loanpackageid-order-reject.md`: **bỏ trắng** trường
`loanPackageId` ⇒ HTTP 400. `_validate_lever_package` khi gói 1840 không hợp lệ cho mã (hoặc không
kiểm được vì mạng lỗi) trả về **gói default của account**, không phải `None` — selfcheck D5 kiểm đúng
điều này. Chiều fail-safe cũng đúng: lệnh đi ra **ít** đòn bẩy hơn dự kiến chỉ làm sleeve under-deploy;
đi ra **nhiều** hơn duyệt là margin call bằng tiền thật.

---

## 5. Không hồi quy

### 5.1 Cascade thật trên plan LIVE có thật — 0 thay đổi

Chạy `apply_capit_lever` trên **24 plan LIVE** (SpaceX + ZaloPay, 12 gần nhất mỗi bên), **50 lệnh thật**,
gồm cả `plan_SpaceX_2026-07-21.json` với **5 lệnh CAPIT thật** và các book `BAL`/`LAG`/`custom30V_parking`/
`DISCRETIONARY_SPECIAL`:

```
TỔNG: 50 lệnh THẬT qua cascade -> 0 thay đổi, 0 lệnh mang cờ vay.
```

Đây là bằng chứng mạnh hơn "đọc code thấy có `if enabled`": ngay cả trên plan có lệnh CAPIT thật, với
`enabled=false`, không gì được cấp.

### 5.2 13 selfcheck cũ

Chạy lại toàn bộ dưới `env -u TZ`:

| Selfcheck | Kết quả |
|---|---|
| `ghost_order` 13 · `churn_guard` 15 · `extreme_regime` 14 · `t2_settlement` 7 · `tick_retry` 15 | PASS |
| `excluded_tickers` 11 · `approval_gate` 19 · `capit_participation_cap` 17 · `concurrent_lock` 5 | PASS |
| `net_offsetting_orders` 35 · `lag_rating_order_gate` 14 · `lag_adv_cap` 29 · `netting_recon` 58 | PASS |
| `cash_only_loan_package` | **1 FAIL — PRE-EXISTING, không phải do job này** |

**Xác minh cái FAIL, không tin lời khai của phiên trước** (`verify-before-done`): `git stash push`
đúng 10 file tôi sửa → chạy lại tại HEAD → **fail y hệt** (`engine order cash_only=True
(decision=inactive)`) → `git stash pop`, xác nhận 5 file production đã khôi phục. Lỗi phụ thuộc
trạng thái discretionary engine sống, không liên quan đòn bẩy.

**1 assert được nới, có chủ đích** — `ghost_order_selfcheck.py` J1 từng assert `raw == {"symbol":
"PAPERGHOST"}` (đẳng thức nguyên dict). `PaperBroker.poll_orders` được thêm `loanPackageId` để guard
đòn bẩy **diễn tập được trên paper** (nếu không, E-nhóm không thể chạy) → assert đẳng thức fail dù
guard hoạt động đúng. Nới thành assert **tính chất** guard thực sự phụ thuộc (`raw.get("symbol")` giải
được), và **thêm** J1b assert `loanPackageId` có mặt. Đây là **tăng** độ phủ, không phải nới lỏng:
13 PASS (trước: 12).

---

## 6. Review bắt buộc

### 6.1 arch-reviewer

*(mục này điền sau khi review xong — xem §6.3)*

### 6.2 quant-skeptic

*(mục này điền sau khi review xong — xem §6.3)*

### 6.3 Ghi chú

Vòng review trước (trong phiên `_122554`) đã bắt được **2 lỗi thật** và cả hai đã được sửa trong
diff này: (1) lưới an toàn `_lever_package_audit` chỉ đọc artifact ⇒ **đang tắt trong production** vì
artifact hôm nay chưa có khoá `capit_lever` → sửa thành đọc hai nguồn (§3); (2) thiếu **trần VND**
cho quyền vay ⇒ hình dạng bug 07-21 → thêm `LEVER_VALUE_TOL` + fail-closed khi thiếu trần (§2.2).

---

## 7. Xác nhận ranh giới cứng

| Ranh giới | Trạng thái |
|---|---|
| `enabled: true`? | **KHÔNG.** `enabled = False` trên đĩa, xác minh lần cuối sau khi mọi test xong. Không bị sửa tạm thành `true` để test — selfcheck A/B nạp fixture ở tmpdir, không đụng file thật; G1–G3 assert trực tiếp file thật |
| Đặt lệnh thật? | **KHÔNG.** Chỉ `PaperBroker` + FakeBroker trong selfcheck |
| Đổi `loanPackageId` tài khoản qua API? | **KHÔNG.** Gói default account vẫn 1841; 1840 chỉ là override per-order trong logic code |
| Chạm file của agent khác? | **KHÔNG** |
| Lấn sang chiến lược/tín hiệu khác? | **KHÔNG.** BAL/LAG/ETF/custom30V/ZaloPay không đổi hành vi — chứng minh bằng §5.1, không bằng comment |

**Bật lên cần 1 bước xác nhận RIÊNG của user.** Không agent nào được tự bật —
`live_requires_user_approval: true` và câu này được ghi cả trong `status` của khối config.

---

## 8. Điều cần biết trước khi ai đó đề nghị BẬT

Không nằm trong phạm vi job này, nhưng phải nói rõ để lần bật không dựa trên số sai:

- Lợi ích đúng là **+0,663pp CAGR** (p5, tầng engine thật, quant-skeptic CONFIRMED-medium), **KHÔNG
  phải +1,82pp** của p4-proxy — p5 cho thấy proxy thổi phồng **cả hai chiều** (2,7× ở lợi ích, 12× ở
  MaxDD). Khối config ghi đúng con số p5 và đánh dấu p4 là SUPERSEDED.
- **N = 15 sự kiện độc lập.** DSR 1,0000 / PBO 0,10–0,14 tính trên 3.107 điểm NAV ngày **không** làm
  N to ra.
- Kênh truyền dẫn hẹp **do thiết kế**: đòn bẩy đáp xuống ~0,272 NAV-book của MỘT trong hai book
  (~13,6% NAV tổng) — đó là lý do hiệu ứng sleeve +4,52%/năm chỉ thành +0,663pp toàn danh mục. **Nới
  kênh là câu hỏi KHÁC, họ rủi ro KHÁC — chưa nghiên cứu, chưa duyệt.**
- p5 §4.2 **tự nhận chưa giải thích được** vì sao realized/predicted là 0,19× ở f=1,1 và 0,41× ở f=1,2
  (1,08× ở f=1,3). **f=1,3 được chọn vì là mức được giải thích tốt nhất, không phải vì tối ưu.**
- Quy mô thật khi bật (p5, f=1,3): sự kiện nặng nhất vay **25,9% NAV**, trung bình 6,8% — và đó là
  **CẬN DƯỚI**. Đỉnh nợ đồng thời 30,55B/50B book, 835 ngày có nợ, lãi trả 4,48B, **0 margin call**
  trong mẫu.

---

## 9. Nguồn

- Chuỗi nghiên cứu: `margin_kelly_feardriven_washout_20260803.md` (p1) · `_p2.md` · `_p3_sizing.md` ·
  `margin_kelly_full_cycle_plan_20260803.md` · `margin_kelly_full_cycle_result_20260803.md` (p4-proxy) ·
  `margin_kelly_engine_confirmation_20260803.md` (p5)
- Verify p5: `mike/logs/verify_20260803_111110.log` (CONFIRMED-medium)
- Capacity: `mike/agents/Mafee/research/spacex_pp0buy_capit_20260803.md` (pp0Buy 425.209.429 VND;
  qmaxBuy gói 1840 = đúng 2× gói 1841, khớp `initialRate` 0,5)
- Selfcheck log: `mike/logs/capit_lever_selfcheck_20260803.log`
- Sự cố tham chiếu: `kb/incidents/2026-07/2026-07-28-spacex-loanpackageid-order-reject.md` ·
  `kb/projects/capit-sizing-bug-0721.md`

---

## 10. VÒNG 2 — arch-reviewer bắt 1 lỗ hổng CAO, đã sửa (2026-08-03, job `Taylor_20260803_141234`)

Vòng 1 kết thúc ở `APPROVE-WITH-FIXES` (F1–F8, đã sửa). Vòng 2 chạy lại arch-reviewer trên
diff SAU khi sửa, đúng theo tinh thần §19 `verify-before-done`: **fix chưa được review lại thì
chưa phải là fix**. Kết quả: `NEEDS_CHANGES`, và lỗ hổng chính là một lỗ hổng THẬT do chính
vòng 1 để lại.

### 10.1 Lỗ hổng CAO — trần VND đọc thẳng từ artifact không đáng tin

**Vấn đề.** F2 (vòng 1) ghim `f` / gói vay / account thành hằng trong CODE, với lý lẽ:
`data/golive_v23_status.json` và `data/trading_rules.json` đều khớp `.gitignore:12` (`*.json`)
nên **không có diff, không blame, không backup** — không được tin tuyệt đối. Nhưng F4 (trần VND,
cũng vòng 1) lại **đọc thẳng** `capit_*_target_vnd_levered` từ chính artifact đó.

Envelope code-pinned chỉ ép **tỷ lệ**, không ép **độ lớn**. arch-reviewer probe thật: giữ nguyên
`f: 1.3` (qua sạch mọi cổng envelope), chỉ sửa hai trường VND →

```
tổng VND được cấp đòn bẩy: 10.000.000.000
so với capit_total_target_vnd × f =  325.000.000     ← vượt 30,8 lần
adj: [('SAB','APPLIED'), ('SIP','APPLIED')]
```

F2 đóng cửa trước, F4 mở cửa sau, **cùng một file**.

**Sửa** (`trading_bot/plan.py`, `_anchored_cap()`): trần =
`min(số artifact tự khai, TRƯỜNG GỐC chưa nhân f × CAPIT_LEVER_APPROVED_F)`, nhân bằng hằng
**trong code** chứ không bằng `f` của artifact (dùng `f` artifact thì nó lại tự nhân cho chính
mình). Thiếu trường gốc ⇒ **fail-closed**. Ca kiểm mới: `C26` (thổi trần → DENIED), `C27` (lệnh
đúng cỡ vẫn được cấp — không chặn nhầm), `C28` (thiếu trường gốc → fail-closed).

### 10.2 Năm phát hiện còn lại — đều đã sửa

| # | Phát hiện | Sửa | Test |
|---|---|---|---|
| #2 | `ppse` đo sức mua bằng gói **default 1841** trong khi lệnh đi ra bằng **1840** (initialRate 0,5 ⇒ sức mua gấp đôi) → lệnh đòn bẩy kẹt `WAIT_CASH` trông y hệt thiếu tiền thường, **và** ghi `would_block=true` GIẢ vào `plan_buying_power_shadow_log.csv` (bộ dữ liệu đang tích luỹ để quyết P0→ACTIVE) | `get_max_buy_qty`/`get_buying_power` nhận `loan_package_id`; executor + shadow-log truyền gói của lệnh | — (PaperBroker không có `ppse`, xem 10.3) |
| #3a | Chính sách tắt SAU khi plan đã sizing 1,3× ⇒ `adj` rỗng ⇒ **0 dòng log**; hệ chạy vốn 1,0× với khối lượng 1,3× mà không ai được báo | Cảnh báo cấp-plan `PLAN_SIZED_LEVERED_BUT_OFF`, chỉ rõ `BOT_STOP` mới là công cụ dừng giữa phiên | `C30`, `C31` |
| #4 | Lệnh 1840 **đã huỷ, 0 khớp** vẫn treo mã cả ngày (không đối xứng với `_ghost_tickers`) | Bỏ qua lệnh chết chưa khớp; chỉ pause mã có trong plan (vẫn cảnh báo mã ngoài plan) | `E3b`, `E3c` |
| #5 | Đệm `1.10` áp cho cả trần TỔNG ⇒ envelope thực tế **1,43×** chứ không phải 1,3× | Tách: per-order `1.10` (làm tròn lô), tổng `1.02` | `C29` |
| #6 | Guard mở+parse 2 file JSON **mỗi chu kỳ** `step()`, mọi account kể cả ZaloPay cash-only | Cache 1 lần/phiên | — |

### 10.3 Giới hạn CÒN LẠI — không được đọc là "đã đóng"

quant-skeptic (`mike/logs/verify_20260803_143700.log`, **CONFIRMED-medium**) tự dựng lại đúng
exploit vòng 1 và xác nhận nó đã bị chặn trong code THẬT (không phải chỉ trong fixture). Nhưng
nó thu hẹp tuyên bố của tôi một cách chính đáng:

> Mốc neo dùng trường GỐC **của chính artifact đó**. Nó chỉ chặn ca sửa **một** trường. Một lần
> sửa **đồng bộ cả hai** (gốc ×3, levered = gốc ×3 ×1,3) vẫn qua, vì mọi tỷ lệ đều đúng.

Cross-check duy nhất trên trường gốc hiện nay là cổng WARN 07-21 ở `send_plan_report.sh` — chạy
lúc **duyệt plan (~21:00)**, không phải lúc **thực thi (~09:05 hôm sau)** ⇒ còn khe ~12h.

Tôi **không** vá vội trong vòng này. Thay vào đó:
- ghim thành ca kiểm **`C29b`** — test khẳng định hành vi ĐANG CÓ, để nếu ai đó về sau đóng khe
  này thì test FAIL và buộc phải đọc lại đoạn văn giải thích (không để nó chìm thành giả định êm ái);
- ghi vào `capit_margin_lever.known_limits` như **ĐIỀU KIỆN TIÊN QUYẾT trước khi `enabled=true`**,
  cùng hai hướng đóng: integrity-check artifact (hash đóng dấu lúc publish 19:03, verify lúc thực
  thi) hoặc recompute độc lập `capit_total_target_vnd` từ NAV sống.

Rủi ro **chưa hiện thực** vì tính năng đang TẮT. Đây là **mitigation, không phải closure** —
diễn đạt đúng như quant-skeptic yêu cầu.

Giới hạn thứ hai đã ghi vào `known_limits`: diễn tập paper **không phủ được** tầng `ppse`
(`PaperBroker` không có), nên "đã wire + đã diễn tập" chứng minh **cờ vay đi trọn đường**, KHÔNG
chứng minh **lệnh đặt được bằng tiền vay thật**. Phiên LIVE có đòn bẩy đầu tiên phải kiểm tay
`pp0Buy@1840` trước khi tin log.

### 10.4 Bằng chứng vòng 2

- `capit_lever_selfcheck.py` — **97/97 PASS, 0 FAIL**, tái lập giống hệt dưới `TZ=Asia/Ho_Chi_Minh`,
  `TZ=America/New_York`, `TZ=UTC` và `env -u TZ` (§16 TZ-trap: không lệch).
- Regression **7/7 rc=0**: `ghost_order`, `tick_retry`, `t2_settlement`, `churn_guard`,
  `extreme_regime`, `approval_gate`, `excluded_tickers`.
- `bin/shellcheck_gate.sh bin/send_plan_report.sh` → rc=0 (chỉ info SC1091/SC2012/SC2086 có sẵn).
- **INERT probe trên cấu hình THẬT** (không fixture): plan tự ghi sẵn `lever_f=9.9`,
  `loan_package_id=1840` trên 2 lệnh CAPIT → cả hai bị `STRIPPED`, residual `(None, None)` toàn bộ.
  Artifact hôm nay chưa có khoá `capit_lever`; `enabled=false`.
- quant-skeptic độc lập xác nhận: đường ghi `o.lever_f`/`o.loan_package_id` **duy nhất** nằm trong
  `apply_capit_lever()` (grep toàn repo) ⇒ `enabled=false` → 0 thay đổi hành vi là tính chất
  **cấu trúc**, không phải chỉ là một assertion trong test.

### 10.5 Việc còn lại trước khi ai đó đề nghị `enabled=true`

1. **Đóng khe artifact hai-trường** (10.3) — integrity-check hoặc recompute độc lập.
2. **Kiểm tay `pp0Buy@1840`** ở phiên LIVE có đòn bẩy đầu tiên; tới lúc đó, dòng shadow-log P0 của
   phiên có đòn bẩy **không hợp lệ** để promote P0 → ACTIVE.
3. User xác nhận riêng, tường minh. **Không agent nào được lật cờ này.**

---

## 11. VÒNG 3 — đóng 2 khe `known_limits` + CỔNG DUYỆT RIÊNG TỪNG NGÀY CÓ VAY (2026-08-03, job `Taylor_20260803_154258`)

User (John) duyệt 2 việc: **A** = đóng 2 khe đã ghi ở §10.5, **B** = *"khi DollarBill tạo plan
dùng margin tôi sẽ phải đồng ý duyệt thì hệ thống mới được phép vận hành"*.

Nguyên tắc thiết kế giữ nguyên xuyên suốt: **fail-safe luôn là KHÔNG đòn bẩy (chạy vốn tự có),
không bao giờ là chặn toàn bộ lệnh** — under-deploy là sai số lành, vay quá mức là margin call.

### 11.1 VIỆC B — cổng người THỨ HAI (`margin_day_approval`)

`capit_margin_lever.enabled=true` là công tắc TỔNG = điều kiện **CẦN, không đủ**. Mỗi NGÀY mà
`apply_capit_lever` thật sự cấp cờ vay cho ≥1 lệnh còn cần một bản ghi duyệt riêng cho **đúng ngày
đó**: `data/margin_approvals/margin_approval_<account>_<plan_date>.json`.

| Thành phần | Vai trò |
|---|---|
| `mike/bin/approve_margin_day.py` | Đường **DUY NHẤT** ghi bản duyệt. Mike chạy sau khi user xác nhận. Rổ mã + trần VND **không gõ tay** — lấy từ `preview_margin_day()`, đúng hàm mà báo cáo 21:00 dùng để hiển thị. |
| `trading_bot.plan.margin_day_approval()` | Đọc + kiểm: đúng account, đúng `plan_date`, `approved_by` là người thật, `lever_f`/`loan_package_id` khớp hằng trong code, có trần `max_lever_total_vnd` > 0, có danh sách `tickers` không rỗng, chưa `revoked`. |
| `_enforce_margin_day_approval()` | Áp cổng lên tập lệnh **vừa được cấp**, chạy **bên trong** `apply_capit_lever` ⇒ không đường nào ra khỏi hàm với cờ vay mà chưa qua cổng. Rổ đổi sau khi duyệt, hoặc Σ vượt trần ⇒ **gỡ SẠCH** (không cấp một phần — cấp một phần là tự quyết hộ user vay bao nhiêu). |
| `send_plan_report.sh` | Nêu **BẬT LOẠT** trong báo cáo 21:00: Σ tiền vay dự kiến + lệnh chính xác phải chạy để duyệt. Không lẫn vào dòng duyệt plan thường. |

**Vì sao là FILE RIÊNG, không phải field trong plan** (như `approved_by` của plan-approval-gate):
plan là JSON do LLM (DollarBill) sinh hoặc người sửa tay. Đặt cờ duyệt đòn bẩy vào đó = trao quyền
duyệt cho chính nơi sinh plan — đúng cái mà `apply_capit_lever` tồn tại để chặn.

`preview=True` (chế độ xem trước cho bước duyệt) bỏ qua **đúng** cổng này và chỉ cổng này, chạy trên
`deepcopy` và trả `(None, adj)` — hàm không trả ra đối tượng plan nào mang cờ vay.

### 11.2 VIỆC A1 — khe artifact hai-trường: **THU HẸP, chưa đóng hẳn**

Chọn hướng **(b) recompute độc lập** thay vì (a) hash, sau khi đọc kiến trúc: `trading_rules.json`
và `golive_v23_status.json` đều bị `.gitignore` — một chữ ký nằm cùng chỗ với thứ nó ký thì ai sửa
được file cũng sửa được chữ ký. Thay vào đó, **4 lớp, 4 nguồn khác nhau**:

1. **Số học nội tại** (`_verify_targets_integrity`) — golive công bố cả BA thừa số, nên có 3 đẳng
   thức miễn phí: `nav_basis × w_lag × capit_size → total → /n_slots → slot`.
2. **Bảng sizing ghim trong code** — `capit_size ≤ capit_base(state)`, `w_lag ≤ STATE_LAG_WEIGHT[state]`.
3. **Artifact state độc lập** — `state` được chốt bằng `golive_state_today.json` (file khác, bước
   khác, do `publish_gated_state.py` ghi).
4. **Sổ broker sống** (`lever_live_preflight`) — đo lại NAV theo đúng công thức `compute_active_nav.py`.

> ⚠️ **Đọc đúng mức độ.** arch-reviewer vòng 3 đo bằng probe thật: bản trần **PHẲNG** đầu tiên
> (`capit_size ≤ 1,0`) **không ràng buộc gì** trên ngày NEUTRAL thường lệ, vì 1,0 đúng bằng giá trị
> hợp lệ lớn nhất (CRISIS) trong khi ngày thường là 0,375. Sửa 3 trường nhất quán mà **không đụng**
> `nav_basis_vnd` cho lọt **2,67×** mục tiêu, envelope tối đa **111,6% NAV** (thiết kế: 13,6%) —
> và neo NAV sống MÙ hoàn toàn với ca này. Neo theo `state` cắt bậc tự do đó xuống phần dư trong
> CÙNG một state (NEUTRAL ≤2×). **Cổng thật sự chặn quy mô là VIỆC B**, không phải A1.
> Ghim thành ca kiểm `C30`/`C30b`/`C30c`. `known_limits` đã được **viết lại** kèm số đo, không xoá.

### 11.3 VIỆC A2 — preflight sống (`lever_live_preflight`)

Chạy **sau `connect()`** (cần sổ broker sống), **trước** shadow-log P0 và `run_session`. **Chỉ GỠ,
không bao giờ cấp.** Đọc thật `get_buying_power(symbol, price, loan_package_id=1840)` và ghi một
dòng log đọc được bằng mắt. Đây là lưới **tự động** chạy trước việc người xem phiên đầu, không thay
thế nó — nhưng nếu không ai xem thì hệ thống **không tự ý đoán**.

Phân biệt có chủ đích: **đọc không được** (`None`/exception) ⇒ GỠ; **đọc được nhưng =0 hoặc < Σ
lệnh** ⇒ chỉ CẢNH BÁO — gỡ đòn bẩy lúc thiếu tiền làm lệnh cần **nhiều** tiền hơn (gói 1840
`initialRate` 0,5 ⇒ sức mua gấp đôi), tức sai chiều fail-safe.

### 11.4 Lỗi CRITICAL do chính vòng 3 tạo ra, arch-reviewer bắt được — đã sửa

Bản đầu của `lever_live_preflight` **phá tính idempotent** (`coding_guidelines` §5) và tạo ra một
sự cố giả nghiêm trọng hơn thứ nó bảo vệ:

crontab thật có **hai** lượt `run_bot.sh --account SpaceX` mỗi phiên — 09:05 và **13:00 ICT**
("khởi động lại sau nghỉ trưa"). Lượt 13:00 là tiến trình MỚI chạy lại trọn cascade. Giữa lúc đang
giải ngân, `availableCash` đã trừ tiền giữ cho lệnh treo ⇒ NAV sống đo được **thấp hơn** cơ sở tối
qua (**−46%** ở sizing CRISIS, **−14,5%** ở NEUTRAL — ăn gần hết biên 15%), và `pp0Buy@1840` tụt về
~0 sau khi sleeve giải ngân xong. Preflight khi đó GỠ sạch cờ vay ⇒ `Executor._lever_package_audit`
suy tập cấp phép từ chính `o.loan_package_id` nên thấy **rỗng** ⇒ **PAUSE cả rổ CAPIT suốt buổi
chiều**, kèm journal + bus event tuyên bố "đòn bẩy KHÔNG ai duyệt" cho đúng những lệnh đã qua **cả
hai** cổng người sáng hôm đó — nội dung sự cố **nói sai**, người trực điều tra nhầm hướng.

Sửa bằng **hai lớp bổ trợ**:

- **Tách hai khái niệm.** `o.loan_package_id` = "lệnh này ĐI RA bằng gói nào" (preflight được phép
  hạ về `None`); sổ `plan._lever_authorized` = "hôm nay ai ĐÃ ĐƯỢC CẤP PHÉP vay" (chỉ
  `apply_capit_lever` ghi, sau khi qua mọi cổng kể cả duyệt-ngày). Audit hợp cả hai.
  Đặt trên đối tượng plan **runtime**, không phải field dataclass — `load_plan` lọc theo field khai
  báo, nên một plan JSON tự ghi `_lever_authorized` **không thể** chạm tới nó; để dạng field thì
  chính nó thành đường qua mặt lưới an toàn cuối cùng.
- **Preflight chỉ GỠ khi phiên CHƯA đặt lệnh nào** (đọc `exec_<account>_<date>_state.json`, đúng file
  `Executor` sẽ load). Đã đặt rồi ⇒ hạ xuống CẢNH BÁO. Lớp bảo vệ chính **không mất**: lượt 09:05
  (phiên sạch) vẫn GỠ đầy đủ — ca kiểm `J14` ghim đúng điều đó.

### 11.5 Toàn bộ phát hiện vòng 3 và cách xử lý

| # | Mức | Nội dung | Xử lý |
|---|---|---|---|
| 1 | CRITICAL | Lượt cron 13:00 gỡ đòn bẩy đã duyệt → audit dựng sự cố giả, treo rổ CAPIT | Sửa (§11.4). Ca kiểm `J13`–`J17b` |
| 2 | HIGH | Trần phẳng `capit_size ≤ 1,0` không ràng buộc (lọt 2,67×) | Neo theo `state` + chốt state bằng nguồn độc lập; `known_limits` viết lại kèm số đo. `C30`/`C30b`/`C30c` |
| 3 | MED-HIGH | `revoked` kiểm bằng `is True` ⇒ thu hồi viết tay (`"true"`/`1`) fail-OPEN im lặng | Đảo chiều: mọi giá trị lạ ⇒ THU HỒI. `I5[revoked='true'/1/'yes']` |
| 4 | MEDIUM | Thiếu ADV20 của 1 mã ⇒ tắt đòn bẩy cả phiên, báo "artifact TỰ MÂU THUẪN" | Đối chiếu `n_capit_basket` thay vì số khoá `capit_adv_caps`. `C31`/`C31b` |
| 5 | MEDIUM | `_bus`/`_notify` nuốt lỗi im lặng; `decided_by:"user"` hard-code (§20) | Kiểm `returncode` + exit 3; thêm cờ `--decided-by` mặc định `agent`. `I16`–`I18` |
| 6 | MED-LOW | Đường `--revoke` ghi không nguyên tử (§5) | `tmp` + `os.replace`. `I19` |
| 7 | LOW-MED | Báo cáo 21:00 vứt `_pv["reasons"]` ⇒ ca "sizing 1,3× nhưng chạy vốn tự có" im lặng | Thêm nhánh `else`. `L6`/`L7` |
| 8 | LOW | Docstring `preview` nói mạnh hơn thực tế (không làm sạch plan caller truyền vào) | Sửa docstring |
| 9 | LOW | `APPROVAL_PLACEHOLDERS` tạo cảm giác an toàn sai ("system-auto"/"Claude"/"yes" lọt) | Ghi thẳng đó là **quy ước mềm**, không phải bộ lọc; lá chắn thật là dấu vết |
| 10 | LOW | `known_limits` + §10.5 lệch khỏi code | Viết lại (không xoá) + mục này |

**Không tìm được (arch-reviewer kết luận SẠCH sau khi tự viết 6 probe phản chứng):** đường bypass
cổng duyệt riêng; `apply_capit_lever` vẫn là nơi **duy nhất** trong repo gán `lever_f`/
`loan_package_id` (grep toàn repo); công thức NAV trong preflight **khớp** `compute_active_nav.py`
(đối chiếu số thật: lệch 1,03%); hợp đồng ghi↔đọc bản duyệt đủ khoá; bash quoting an toàn (khối
margin nằm trong heredoc `<<'PY'` nên `\"` là escape của Python, không phải bash); thứ tự cascade
không đổi; `preview_margin_day` chạy trên plan thô chỉ tạo **cận trên** nên trần trong bản duyệt
không chặn oan.

> **Caveat trung thực** (arch-reviewer nêu, giữ nguyên): cả `lever_live_preflight` lẫn
> `compute_active_nav.py` đều **không trừ `totalDebt`**, trong khi NAV chuẩn tắc của fleet
> (`daily_nav_snapshot.py`) có trừ. Khi đòn bẩy chạy, "NAV sống" bị thổi đúng bằng nợ margin ⇒ neo
> **lỏng dần** theo mức vay. Không sai chiều (nó chỉ làm cổng dễ dãi hơn, không chặt hơn), nhưng
> đừng mô tả con số đó là "NAV".

### 11.6 Bằng chứng vòng 3

- `capit_lever_selfcheck.py` — **170/170 PASS, 0 FAIL** (vòng 2: 97; đầu vòng 3: 150), tái lập
  **giống hệt** trên **5 môi trường**: `TZ=Asia/Ho_Chi_Minh`, `env -u TZ`, `TZ=America/New_York`,
  `TZ=UTC`, `TZ=Pacific/Kiritimati`.
- Test **không còn phụ thuộc regime của ngày chạy**: nguồn `state` độc lập được trỏ vào fixture
  (`_STATE_FIX`), không đọc `golive_state_today.json` production — nếu không, mọi ca `C*` sẽ đổi
  kết quả theo state hôm chạy (đúng loại phụ thuộc môi trường mà skill `verify-before-done` bắt
  phải khai và loại bỏ).
- `bin/shellcheck_gate.sh bin/send_plan_report.sh` → rc=0; `bash -n` OK.
- `data/trading_rules.json` → `capit_margin_lever.enabled` = **`false`**, không đổi.
  `data/margin_approvals/` **chưa tồn tại** (không bản duyệt nào bị tạo ra trong lúc làm việc này).
- **Không** đặt lệnh thật, **không** gọi API DNSE đổi `loanPackageId`.

### 11.7 Việc còn lại trước khi ai đó đề nghị `enabled=true`

1. **Kiểm tay `pp0Buy@1840`** ở phiên LIVE có đòn bẩy đầu tiên (nay đã có lưới tự động chạy trước,
   nhưng vẫn cần người xem phiên đầu). Tới lúc đó, dòng shadow-log P0 của phiên có đòn bẩy **không
   hợp lệ** để promote P0 → ACTIVE.
2. Hiểu rằng **A1 chỉ thu hẹp** khe artifact (§11.2) — cổng chặn quy mô là **người duyệt từng ngày**.
3. User xác nhận riêng, tường minh, cho **công tắc tổng**; rồi vẫn phải duyệt **từng ngày có vay**.
   **Không agent nào được lật cờ này.**
