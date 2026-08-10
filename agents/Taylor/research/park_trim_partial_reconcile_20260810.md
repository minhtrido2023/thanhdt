# Đường cấp vốn phiên-1 LAG: vì sao hỏng ngày 08-06, và giải pháp nào thay cho việc nới trần giá

**Job** `Taylor_20260810_113500` · 2026-08-10 · Taylor
Tiếp nối `lag_entry_window_execution_20260810.md` §2 + `lag_anchor_widen_nav_backtest_20260810.md`.
**Trạng thái**: NGHIÊN CỨU + PATCH CHỜ DUYỆT. **0 dòng production bị sửa.**
Patch: `agents/Taylor/pending_park_trim_partial_reconcile_20260810/`.

---

## 0. Tóm tắt cho người quyết định

| Câu hỏi | Trả lời |
|---|---|
| Fix 08-05 có thật sự đóng gap không? | **CÓ — về CƠ CHẾ.** Replay `park_holdings` cho asof 08-06 với registry hôm nay: **✅ KHỚP cả 2 account.** `corp_action_split()` chạy đúng thời điểm, đúng lô hưởng quyền |
| Vậy sao 08-06 vẫn BLOCKED? | **Code kịp, DỮ LIỆU không kịp.** Fix commit **08-05 15:18**; pipeline plan chạy **08-05 19:05–19:11**; user ký `corp_actions.json` **08-05 22:24:51** — **sau pipeline 3h17m**. Cổng đọc một sổ vẫn rỗng |
| Nguyên nhân lệch đúng 2× | VHM cổ tức CP 1:1. `LotBook` chỉ có `buy()`/`sell()` theo journal, không có thao tác corp-action ⇒ sổ đứng 500, broker nhảy 1000 |
| Lỗ hổng nghiêm trọng nhất | **1 mã lệch ⇒ 0 lệnh cho CẢ tài khoản, ở CẢ HAI đường cấp vốn (L1 trim + L2 JIT).** Không riêng VHM — bất kỳ corp-action nào sau này |
| Sửa được bao nhiêu | Patch thu hồi **115,68tr / 130,98tr = 88,3%** sức mua ngày 08-06 (đo trên dữ liệu thật) |
| Có làm biến mất vấn đề "không fill" không? | **KHÔNG hết.** Nó cứu được **~1 slot LAG/account** ở phiên chuẩn, không phải cả 3. Phần dư là ràng buộc VỐN thật, không phải lỗi |
| Ưu tiên | **CHỈ Phần A.** Không đề xuất thêm hướng nghiên cứu nào ở mục B2 — xem §6 |

---

## PHẦN A — đường cấp vốn phiên-1

### 1. Fix 08-05 có đóng gap không? Có, về cơ chế — đã kiểm bằng replay

Retro 08-05 ghi *"ĐÃ SỬA cùng ngày, verify độc lập CHƯA đầy đủ"*. Kiểm lại bằng cách chạy lại
chính engine trên dữ liệu 08-06:

```
=== SpaceX  asof=2026-08-06 ===  đối soát broker: ✅ KHỚP (21 mã)
   ⚠ 2026-08-05 corp action VHM-2026-08-06-STOCK-DIVIDEND ×2.0 (ex 2026-08-06): 1 lô VHM nhân qty
=== ZaloPay asof=2026-08-06 ===  đối soát broker: ✅ KHỚP (16 mã)
   ⚠ ... 2 lô VHM nhân qty / chia giá vốn — tổng giá vốn không đổi
```

**Cơ chế đúng, kể cả ở chỗ phản trực giác nhất.** `corp_action_split` tách đúng ba mốc mà ca VHM
chứng minh là KHÔNG trùng nhau: `ex_date` (quyết định lô nào hưởng quyền: `entry_date < ex_date`)
· `broker_effective_ts` (quyết định ngày sổ nhảy) · `record_date` (chỉ tra cứu). Corp action đi
CHUNG dòng thời gian với fill, khoá sắp xếp `(ts, 0)=fill trước, (ts, 1)=corp action sau`. Có
fail-closed cho lô lẻ, có cờ "cửa sổ xám" (mua sau khi broker credit nhưng trước ex-date).

**Không có khoảng hở thời điểm nào trong ENGINE.** Khoảng hở nằm ở **dữ liệu**.

### 2. Root cause thật: độ trễ ký duyệt, không phải logic

| Thời điểm | Sự kiện | Nguồn |
|---|---|---|
| 08-04 19:10 | broker còn 500cp | `dnse_raw_2026-08-04.jsonl` |
| 08-05 ~12:10 | park_trim đầu tiên thấy lệch ⇒ BLOCKED, báo bus | bus `DollarBill_20260805_120343` |
| 08-05 **15:18** | **code fix** `corp_action_split()` + registry loader | commit `15c4bc84` |
| 08-05 **19:07 / 19:11** | **pipeline sinh plan 08-06 → `BLOCKED_RECONCILE`, 0 lệnh** | mtime `park_trim_SpaceX_2026-08-06.json` |
| 08-05 21:00 | `send_plan_report` gửi plan RỖNG | cron |
| 08-05 **22:24:51** | **user ký `corp_actions.json`** | mtime file + `user_signoff_at` |
| 08-05 23:00 | second-chance — **RE-SEND, không REGENERATE** | cron `--second-chance` |
| 08-06 | phiên entry chuẩn: 0 lệnh cả 2 account | `plan_*_2026-08-06.json` |

> **Code shipped, data didn't.** Retro nói "đã fix cùng ngày" — đúng về code, sai về vận hành.
> Không có cơ chế nào chạy lại pipeline sau khi registry được ký.

Trích thẳng plan 08-06:
> SpaceX: `"decision": "ĐỦ ĐIỀU KIỆN vào lệnh nhưng THIẾU TIỀN → deferred_orders[]. Không phải SKIP."`
> ZaloPay: `"đường bán (L1 trim) hôm nay BLOCKED_RECONCILE do lệch sổ VHM"`

### 3. Ba lỗ hổng còn MỞ (fix 08-05 chỉ đóng cái thứ 0)

| # | Lỗ hổng | Bằng chứng | Ai đóng |
|---|---|---|---|
| **G1** | **Bán kính nổ**: 1 mã lệch ⇒ 0 lệnh cho CẢ tài khoản, ở CẢ HAI cổng cấp vốn (`compute_park_trim.py:254`, `compute_jit_unpark.py:322` — cùng một đoạn code) | 21 mã SpaceX / 16 mã ZaloPay khớp tuyệt đối, vẫn bị chặn sạch | **patch §4** |
| **G2** | **Độ trễ ký duyệt không có trần**, và không có trigger chạy lại pipeline khi registry đổi sau khi plan đã ghi | timeline §2 | ops (§5) |
| **G3** | **Không có phát hiện corp-action cho mã ĐANG GIỮ.** `data/corp_action_pending.json` = `{}` (mtime 08-07 18:40) — **chưa bao giờ gắn cờ VHM**, dù đây là đợt chia CP lớn nhất lịch sử TTCK VN (4,1 tỷ cp) trên mã giữ ở CẢ HAI account | file rỗng + `update_shares_live.py` phát hiện HẬU NGHIỆM qua cú nhảy tỉ số giá BQ tại ex-date (08-06) — **muộn hơn broker credit (08-05) một phiên**, về cấu trúc là không kịp | Winston (§5) |

### 4. Bản vá — để tầng lọc TỪNG MÃ vốn đã có làm việc của nó

**Phát hiện then chốt: cơ chế cần thiết ĐÃ TỒN TẠI.** Ngay dưới cổng 0 có sẵn tầng loại theo từng
mã — `unverified_tickers` → `blocked[]` (`sổ UNVERIFIED — cấm sinh lệnh (§21)`), và
`park_holdings` đã tự nạp mọi mã lệch vào đó. **Cổng 0 là một tầng thô chặn trước một tầng mịn
vốn đã làm đúng.** Không cần cơ chế mới.

**Trả lời câu hỏi "tái dùng `excluded_tickers` được không": KHÔNG, và không cần.**
`excluded_tickers` là **cấu hình người khai, vĩnh viễn** (§7 — vị thế legacy như DGC). Đây là
trạng thái **tạm thời, suy từ dữ liệu**. Trộn hai thứ sẽ làm bẩn một cấu hình mà `plan.py`
`filter_excluded_tickers()` đang dựa vào cho ràng buộc dài hạn. Đúng cơ chế là
`unverified_tickers` — đã có sẵn, đúng ngữ nghĩa (tạm thời), đúng vòng đời.

**Nhưng nới cổng KHÔNG được phép làm một mình.** Hai hướng lệch có hậu quả ngược nhau
(`tgt_i = w'_i × 0,8 × (cash + park_mv)`, `want_i = mv_i − tgt_i`):

- `diff > 0` (sổ nhiều hơn broker) → `park_mv` phồng → `tgt_i` phồng → `want_i` co → **trim ít
  hơn** = sai an toàn. Nhưng đây là chữ ký **kế toán hỏng**, không phải corp action ⇒ **giữ chặn cứng.**
- `diff < 0` (broker nhiều hơn — chữ ký corp action) → `park_mv` **thiếu** → `tgt_i` thiếu →
  `want_i` **phồng** → **OVER-TRIM trên CÁC MÃ KHÁC.** Tầng `unverified_tickers` **không** chặn
  được cái này (nó chỉ cấm bán *chính* mã lệch).

⇒ Patch hiệu chỉnh `park_mv` theo **số lượng của broker** (broker là nguồn sự thật về số lượng —
§6/§25). Bất định "phần cp thêm có thuộc PARK không" **không cần đoán đúng**: cộng nhầm ⇒ `park_mv`
phồng ⇒ rơi về nhánh `diff>0` = trim ít hơn. **Cả hai giả thuyết đều cho hướng sai an toàn.**

L2 (`compute_jit_unpark`) **không cần hiệu chỉnh mẫu số** — `park_mv_vnd` ở đó chỉ dùng để in ra;
cỡ lệnh suy từ nhu cầu tiền từng lệnh mua và số cp bán được từng mã. Nhưng **phải vá cùng lúc**:
hai cổng đọc cùng `h["reconcile"]`, vá mỗi L1 thì đường cấp vốn cho lệnh MUA vẫn chết.

#### A/B trên dữ liệu thật 08-06

Chân đối chứng = registry đã ký. Chân sự cố = `corp_actions=[]` (tái lập chính xác trạng thái lúc
19:07).

| Account | Chân | OLD | NEW |
|---|---|---|---|
| SpaceX | đối chứng | `TRIM` 14 · **100,34tr** | `TRIM` 14 · **100,34tr** ✅ |
| SpaceX | **ca thật 08-06** | `BLOCKED_RECONCILE` · **0đ** | `TRIM` 13 · **92,69tr** |
| ZaloPay | đối chứng | `TRIM` 6 · **30,64tr** | `TRIM` 6 · **30,64tr** ✅ |
| ZaloPay | **ca thật 08-06** | `BLOCKED_RECONCILE` · **0đ** | `TRIM` 5 · **22,99tr** |

- **Chân đối chứng trùng khớp tuyệt đối** ⇒ không đổi hành vi đường bình thường.
- Chênh đúng bằng chân bán VHM (`7,65tr` mỗi account) — không mã nào khác đổi.
- `pool` PARTIAL = **658,70tr / 292,58tr** = **đúng bằng** pool khi sổ đã đúng ⇒ hiệu chỉnh mẫu số
  chính xác, không còn dư địa over-trim.
- **Thu hồi 115,68tr / 130,98tr = 88,3%.**

**Selfcheck 6/6 PASS** (phạm vi §23 = mọi file import `park_holdings`/`compute_park_trim`, tra
bằng `grep -rln`, + 2 file đọc artifact). 8 ca mới, **mọi ca "chặn được" đều có ca chứng minh
NGƯỢC** — `T07c` chứng minh AAA THẬT SỰ bị bán khi sổ khớp, nên `T07b` là chặn thật chứ không phải
rổ rỗng vì lý do khác. Chi tiết + cách áp: README trong thư mục `pending_`.

⚠️ **Ngoài lề, không do patch này**: `send_plan_report_park_jit_selfcheck.py` **FAIL sẵn ở
baseline** (9 assertion chép cứng số đếm/số tiền đã mốc — §23 hệ luận 1). Cần chủ file xử lý riêng.

### 5. Phòng ngừa tái diễn — 4 tầng, patch chỉ là tầng 2

| Tầng | Việc | Vì sao cần | Chủ |
|---|---|---|---|
| **L0** | **Lịch corp-action HƯỚNG TRƯỚC cho mã ĐANG GIỮ**: quét tuần, ghi record `PROPOSED` vào `corp_actions.json` **trước ex-date nhiều ngày** | Ex-date VHM là thông tin công khai từ nhiều tuần (chính `evidence` của record trích HOSE/cafef). Biến cuộc chạy đua trong ngày thành một chữ ký định kỳ. **Đây là tầng DUY NHẤT loại bỏ hẳn độ trễ**, các tầng dưới chỉ giảm thiệt hại | **Winston** |
| **L1** | **Patch §4** — chặn từng mã, không chặn cả tài khoản | Không cần người trong vòng lặp. Hoạt động kể cả khi L0 trượt | Taylor (chờ duyệt) |
| **L2** | **Trigger chạy lại pipeline** khi `corp_actions.json` đổi sau khi artifact plan T+1 đã ghi | Chính xác là khe 19:07 → 22:24. `--second-chance` 23:00 chỉ RE-SEND, không REGENERATE | ops (§11 — đổi cron cần cập nhật `cron_registry.md` cùng commit) |
| **L3** | **Escalate khi `deferred_orders` chứa mã LAG ở ĐÚNG phiên entry chuẩn** | Hôm 08-06 plan ghi đúng "THIẾU TIỀN → deferred" rồi **im**. Mất phiên chuẩn là mất **không phục hồi được** — đáng một cảnh báo riêng, không phải một dòng trong JSON | ops |

**Không tự suy corp action từ việc thấy qty lệch** — `corp_actions.py` đã cấm đúng chỗ, và patch
này **giữ nguyên** lệnh cấm đó: nó không sửa sổ, chỉ thôi không chặn các mã KHÔNG liên quan.

---

## PHẦN B — nếu không phải trần giá thì là gì?

### 6. Sửa Phần A xóa được bao nhiêu phần của vấn đề? Khoảng một phần ba — và phần dư KHÔNG phải lỗi

Đây là chỗ dễ overclaim nhất, nên đi bằng số:

| | SpaceX | ZaloPay |
|---|---:|---:|
| Cỡ 1 slot LAG (10%) | 102,69tr | 27,07tr |
| Mã LAG **sạch cửa** ở phiên chuẩn 08-06 | 3 (DRI, POW, SCL) | 1 (DRI) — còn lại DCF RICH / cờ đỏ DD / floor_fail |
| Nhu cầu vốn thật | **308,06tr** | **27,07tr** |
| Sức mua sau patch (trim + tiền sẵn có) | 92,69 + 4,82 = **97,51tr** | 22,99 + 5,82 = **28,81tr** |
| Che được | **≈0,95 slot / 3** | **1,06 slot / 1 — ĐỦ** |

⇒ **ZaloPay lẽ ra vào được DRI đúng phiên chuẩn, đúng giá thị trường.** SpaceX lẽ ra vào được 1
trong 3 mã. Theo bảng §3 báo cáo trước (phiên 1: `ret|fill` 4,06% / fill 100%; phiên 3 ANCHOR:
2,15% / fill 56,5% ⇒ 1,22% trên vốn), mỗi slot cứu được ở phiên chuẩn đáng **~2,8pp** so với rơi
xuống phiên 3.

**Phần dư không phải lỗi cần sửa.** L1 chỉ thu hoạch phần VƯỢT trần PARK 80%, lại bị chặn ADV mỗi
phiên (SpaceX "còn thiếu 17,74tr → phiên sau"). Muốn có 308tr trong một phiên thì phải bán sâu
xuống dưới trần PARK — tức đổi chính sách phân bổ, không phải vá bug. Và registry (audit H8) đã
ghi: **sổ LAG oversubscribe ~6×, bind 92% số entry** — thiếu vốn ở LAG là **trạng thái thường
trực đã biết**, không phải hệ quả của sự cố 08-06.

### 7. Có nên nghiên cứu thêm hướng nào ở mục B2 không? — KHÔNG

Dispatch gợi ý 2 hướng. Đánh giá thẳng, không chạy backtest mới (đúng ràng buộc):

**(a) Ưu tiên vốn phiên chuẩn cho tín hiệu mạnh nhất.** — **Đã là hành vi hiện tại, không phải
thay đổi.** Khi cash ≥ 1 slot, allocator cấp theo priority. Ngày 08-06 câu hỏi này **chưa từng
phát sinh**: cash 4,82tr < 1 slot nên mọi mã rơi vào `deferred`. Sửa Phần A làm câu hỏi này sống
lại một cách tự nhiên — nhưng cơ chế trả lời nó đã có. **Việc cần làm là XÁC MINH thứ tự ưu tiên
thật sự neo vào cường độ tín hiệu, không phải xây cái mới** — một lần đọc code, không phải một dự
án nghiên cứu.

**(b) Cỡ lệnh nhỏ hơn cho nhiều mã hơn (dàn mỏng).** — **Không đề xuất.** Số học thô có vẻ ủng hộ
(dàn mỏng 3 mã × phiên 1 = 4,06% vs 1 mã × 4,06% + 2 mã × 1,22% ≈ 2,10%), nhưng nó **đứng trên
đúng cái sự cố vừa sửa**: khi Phần A đã chạy, ràng buộc vốn phiên chuẩn nhẹ hơn hẳn và phép so
sánh này đổi hoàn toàn. Ngoài ra nó động vào **cỡ slot 10% đã hiệu chuẩn** của V2.4 — một thay đổi
chiến lược cần backtest NAV đầy đủ + DSR/PBO + quant-skeptic, và nó **chồng lấn** với đề xuất
nới trần anchor đang chờ user quyết. Chạy song song hai thay đổi vào cùng một cơ chế entry là cách
chắc chắn nhất để không quy được kết quả cho ai.

> **Ưu tiên: CHỈ Phần A.** Nó sửa một **lỗi**, có bằng chứng trực tiếp, hướng sai an toàn, rollback
> một dòng, và không tiêu một bậc tự do nào của mô hình. Mọi thứ khác là tối ưu hoá trên phần dư
> nhỏ, và nên đợi ít nhất một phiên dữ liệu THẬT sau khi Phần A chạy.

### 8. Thứ tự làm

1. **L1 patch** (§4) — quant-skeptic → user duyệt → 1 phiên shadow → wire.
2. **L0 lịch corp-action hướng trước** — dispatch **Winston**. Độc lập, làm song song được.
3. **L3 escalate mất-phiên-chuẩn** — rẻ, độc lập.
4. **L2 trigger chạy lại pipeline** — cần đổi cron (§11), làm sau khi L0 chạy (L0 giảm hẳn tần suất cần tới nó).
5. `send_plan_report_park_jit_selfcheck.py` FAIL baseline — giao chủ file.
6. Nới trần anchor `×1,03` — **giữ nguyên trạng chờ user**, KHÔNG gộp vào đợt này.

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source wc_env.sh
# 1) Fix 08-05 có đóng gap không (replay với registry hôm nay):
python3 mike/bin/park_holdings.py --account SpaceX  --asof 2026-08-06
python3 mike/bin/park_holdings.py --account ZaloPay --asof 2026-08-06
# 2) Trim lẽ ra có được ngày 08-06:
python3 mike/bin/compute_park_trim.py --account SpaceX  --asof 2026-08-06
python3 mike/bin/compute_park_trim.py --account ZaloPay --asof 2026-08-06
# 3) A/B OLD vs NEW (harness: /tmp/ab_partial.py trong job này; chân sự cố = corp_actions=[]).
#    Module vá PHẢI nằm ở mike/bin/ khi chạy — WC_ROOT suy từ __file__, đặt chỗ khác thì
#    BASKET_CSV/STATE_FILE trỏ sai và mọi ca ra BLOCKED_BASKET (đã cắn thật trong job này).
```

⚠️ **`data/corp_actions.json` bị `.gitignore` nuốt** (`*.json` dòng 12) — sổ đăng ký corp-action
**không nằm trong version control**, không có lịch sử thay đổi, không có audit trail cho một file
mà chữ ký của user là điều kiện để sổ lô đúng. Phát hiện phụ trong job này, nên xử lý riêng.
