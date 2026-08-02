# 2026-08-02 — Hai lỗi fidelity thanh khoản sổ LAG: engine mô phỏng một đường live không đi được

**Job:** `Taylor_20260802_163657` (attempt 2/2) · **Trạng thái:** ĐÃ SỬA + ĐÃ ĐO
**Báo cáo đầy đủ:** `mike/agents/Taylor/research/liq_fidelity_and_adv_basis_20260802.md`
**Liên quan (KHÁC tầng, cùng họ cơ chế ở Việc 2):** `2026-08-02-pe-price-close-adjustment-saga.md`

---

## 0. Vì sao đây là incident RIÊNG, không phải "Phần 5" của saga Price/Close

Saga Price/Close (4 phần) xử lý cơ sở giá ở tầng **chọn rổ / định giá / trọng số**
(`custom_basket.py`, `rating_8l.py`). Incident này ở tầng **thanh khoản & khả năng khớp lệnh**:

- **Việc 1 KHÔNG liên quan gì tới Price/Close** — nó là lỗi fail-**open** trong nhánh trần %ADV.
- **Việc 2 cùng họ cơ chế** (Close đã điều chỉnh hồi tố bị dùng làm cơ sở tiền đồng) nhưng khác
  file, khác tầng, khác hệ quả (độ lớn trần + tốc độ fill, không phải chọn mã nào).

Gộp vào saga sẽ làm cả hai khó đọc. Cross-link hai chiều thay vì gộp.

---

## 1. Việc 1 — `liq<=0` được đối xử như "KHÔNG CÓ TRẦN" thay vì "KHÔNG MUA ĐƯỢC"

`simulate_holistic_nav.py` kiểm `if liq and liq > 0:` trước khi áp trần %ADV. Mã có
`Volume_3M_P50<=0` hoặc không đo được ADV rơi vào nhánh `else` ⇒ **không bị trần** ⇒ engine cho
**mua trọn size trong 1 phiên**. Đường live thì chặn nhóm này ở **CẢ HAI tầng**: tín hiệu
(`lag_filter_illiquid`, từ 07-21) và executor (`cap_lag_orders`, hard-gate fail-closed từ 07-22).

**Hình dạng lỗi:** một điều kiện phòng thủ viết theo hướng fail-**OPEN**. `liq` vắng mặt là dấu
hiệu *xấu nhất* (mã không có thanh khoản thật), nhưng code đọc nó thành *dễ dãi nhất* (miễn trần).

Root cause này **đã được phát hiện và ghi từ 2026-07-21** (`results_registry.md`, job
`Taylor_20260721_162243`) cùng bản vá `liquidity_require_positive`, nhưng để **mặc định TẮT** vì
2 điều kiện chưa thoả (vintage + giả định substitution). Job này đóng cả hai (§3) rồi bật mặc định.

---

## 2. Việc 2 — ADV tiền đồng nhân giá ĐÃ ĐIỀU CHỈNH

`ADV = Volume_3M_P50 × Close`. Nhưng `Volume_3M_P50` là **số lượng CP THÔ** — đo được
`Trading_Value == Volume × Price` khớp **100% số dòng**, `Volume × Close` thì không. Nhân `Close`
(đã điều chỉnh hồi tố) sai hai lần: **sai độ lớn** (ADV bị hạ ⇒ trần chặt oan, fill chậm oan) và
**look-ahead** (hệ số `Close/Price` tại ngày *t* phụ thuộc sự kiện quyền SAU *t*).

**Điểm quan trọng nhất về phạm vi — và là chỗ dispatch bắt phải kiểm trước khi sửa:** công thức
này nằm ở **3 điểm** phục vụ **cả live lẫn mô phỏng**, cố ý giữ giống hệt nhau:

| # | Vị trí | Vai |
|---|---|---|
| 1 | `lag_liquidity_filter.py` (SQL) | LIVE — lọc tầng tín hiệu (chỉ dùng phép thử `>0`) |
| 2 | `trading_bot/due_diligence.py:adv_vnd` | LIVE — **độ lớn trần** hard-gate `cap_lag_orders` |
| 3 | `pt_v23_audit_2014.py` (`liq_lag`) | MÔ PHỎNG — tốc độ fill sổ LAG |

⇒ Đánh giá ban đầu "chỉ live, dọn dẹp rẻ và an toàn" là **SAI**. Sửa 1 điểm mà bỏ 2 điểm kia sẽ
**phá bất biến "trần live == trần đã mô phỏng"** — chính bất biến mà `cap_lag_orders` tồn tại để
giữ. Đã sửa **đồng thời cả 3**.

---

## 3. Hai điều kiện treo của pin 07-21 — nay ĐÃ ĐÓNG CẢ HAI

Pin 07-21 tự đánh dấu **PIN TẠM**. Job này đóng nốt:

| Điều kiện 07-21 | Trạng thái nay |
|---|---|
| **#1 Vintage** — phải chạy lại trên cache `verified:true`, không phải live BQ | **ĐÓNG** — chạy trên snapshot đóng cứng `bq_cache_asof20260729_postrestate` = đúng vintage số pin; chân đối chứng tái lập pin **chính xác** |
| **#2 Substitution** — engine cho vốn chảy ngay sang ứng viên kế tiếp, còn live (chỉ chặn ở executor) thì để tiền nằm im ⇒ 31,33% chỉ là **cận trên** | **ĐÓNG** — từ 07-21 live đã có lọc **tầng tín hiệu** `lag_filter_illiquid`, nên sổ live tự chọn ứng viên kế tiếp **đúng như engine**. Đây chính là "việc cần quyết #3" của 07-21 và nó đã làm rồi |

⇒ Khoảng `[~27,2%; ~31,3%]` ghi trong registry/current_ops **hết hiệu lực**: đó là khoảng *chưa
đo được* dựng từ pin tạm. Nay đo trực tiếp trên đúng vintage.

---

## 4. Số (A/B 4 chân, snapshot đóng cứng, threads=1)

| Chân | `LIQ_ZERO_BLOCK` | `LAG_ADV_BASIS` | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|
| **L0** đối chứng | off | close | **27,24%** | 1,81 | −18,4% | 1,48 |
| L1 chỉ Việc 1 | lag | close | 31,32% | 1,88 | −18,8% | 1,67 |
| L2 chỉ Việc 2 | off | price | 28,86% | 1,90 | −17,8% | 1,62 |
| **L3 cả hai** | lag | price | **32,71%** | 1,95 | −19,1% | 1,71 |

L0 tái lập số pin hiện hành **chính xác** (kể cả NAV cuối 1.006,33B) ⇒ A/B hợp lệ. Self-check
**0 VND** cả 4 chân. LOO trên Δ **dương 13/13** ở cả 3 cặp. DSR(L3) **1,0000**. Bootstrap MaxDD
5th-pct **−30,2%** ⇒ **anchor DD ~−30% GIỮ NGUYÊN**, không dùng −19,1% làm kỳ vọng.

Δ **không cộng tuyến tính** (4,08 + 1,62 = 5,70 > 5,47 thực đo) — hai bản sửa giao thoa vì cùng
tác động lên một cơ chế (khả năng/tốc độ fill sổ LAG). Vì vậy **phải chạy L3 thật**, không được
cộng L1+L2.

---

## 5. BÀI HỌC

### 5.1. "Tác động = 0 vì Close ≈ Price hôm nay" là suy luận SAI khi hệ thống replay lịch sử
Bài học này đã được nêu ở saga Price/Close (#2) và incident này **định lượng nó**: median
`Close/Price` **đơn điệu** 0,443 (2014) → 1,000 (2026). Ở 2014 ADV bị hạ **2,26 lần**. Một hàm
"chỉ chạy live" vẫn sai nghiêm trọng ngay khi có ai đó replay nó qua lịch sử — và ở đây engine
backtest dùng **đúng công thức đó**.

Hệ quả tích cực: cùng con số này **giải thích** bất đối xứng IS/OOS của Việc 2 (IS +3,28pp, OOS
+0,02pp) — phần hơn **tỉ lệ thuận với độ lớn của chính lỗi đang sửa**, và ~0 đúng nơi lỗi ~0.
Chữ ký này **ngược hẳn** reshuffle-luck (bài học MOM/Wave1). Dose-response là cách rẻ nhất để
phân biệt "sửa lỗi thật" với "tinh chỉnh cho số đẹp".

### 5.2. Điều kiện phòng thủ phải fail-CLOSED; thiếu dữ liệu ≠ được miễn kiểm
`if liq and liq > 0:` đọc "không đo được thanh khoản" thành "miễn trần". Mọi gate mà dữ liệu vắng
mặt đưa tới nhánh **dễ dãi hơn** đều là lỗi chờ nổ, kể cả khi comment nói đúng ý định.

### 5.3. Khi một công thức là BẤT BIẾN PARITY giữa live và mô phỏng — sửa ĐỒNG THỜI mọi điểm
Trước khi sửa "một hàm live", phải trả lời: công thức này còn ai chép không? Ở đây là 3 điểm và
2 trong 3 nằm ngoài file đang mở. Sửa lệch pha sẽ phá đúng cái bất biến mà gate sinh ra để bảo vệ.

### 5.4. "Selfcheck PASS" mà không nói chạy ở chế độ nào là báo cáo THIẾU
`lag_liq_signal_filter_selfcheck.py` cho **13 PASS** khi chạy trần, **22 PASS** với `--live` —
và **toàn bộ positive control cơ sở giá nằm sau cờ `--live`**. Chạy mặc định rồi báo "PASS" sẽ
bỏ sót đúng phần kiểm chứng bản sửa này. Khớp `verify-before-done` §nêu tên phụ thuộc môi trường.

### 5.5. ⚠️ Cron auto-backup CUỐN việc R&D đang dở vào commit — lần này trúng CODE, không phải `kb/`
Attempt 1 hết lượt giữa chừng, để code chưa commit ở working tree. Cron `auto-backup` 17:00 UTC
`git add -A` **blanket** đã gói toàn bộ vào commit `11d28ca "auto-backup 2026-08-02T17:00:01Z"` —
một commit message vô nghĩa cho một thay đổi chạm đường live, và `git status` sạch làm attempt 2
suýt kết luận "attempt 1 không làm được gì" rồi làm lại từ đầu.

Đây là **cùng root cause** với `coding_guidelines.md §13` (viết cho `kb/`) nhưng §13 chỉ nói về
file `kb/`, nên không ai áp nó cho code R&D. Cách phòng đúng vẫn là của §13: việc dở có nguy cơ
bị cắt → **ghi `remember.sh` NGAY** + biết rằng working tree **không phải** nơi an toàn để "giữ
tạm chờ duyệt" trên repo này. Không đề xuất đổi cron (backup blanket là chủ ý, và mất backup
nguy hiểm hơn commit message xấu) — đề xuất là **đừng tin `git status` sạch = chưa ai làm gì**:
luôn `git log` khoảng thời gian của attempt trước.

---

## 6. Tác động LIVE (đo, không suy đoán)

Việc 2 nới trần `cap_lag_orders` theo hệ số `1/(Close/Price)`. Trên rổ ứng viên LAG thật
(asof 2026-07-31, 152 mã): **1 mã duy nhất (DNN, 0,7%)** có `Close≠Price`, và DNN **đã bị loại ở
tầng tín hiệu** ⇒ **0 lệnh thật đổi**. Đúng như dose-response dự báo (2026 ratio = 1,000).

Vẫn là **thay đổi chạm LIVE** (nới một hard-gate) ⇒ báo cáo tường minh cho user/Mike duyệt theo
mandate Taylor, không tự coi là dọn dẹp nội bộ.

---

## 7. Tham chiếu

- Báo cáo: `mike/agents/Taylor/research/liq_fidelity_and_adv_basis_20260802.md`
- Harness/log/CSV: `data/liqadv_ab_20260802/`
- Nguồn root cause Việc 1: `data/results_registry.md` §"2026-07-21 — RE-PIN R3 (SỬA ENGINE `liq<=0`)"
- Saga cùng họ cơ chế (khác tầng): `2026-08-02-pe-price-close-adjustment-saga.md`
