# Đối chiếu file audit anh gửi ↔ số R3 pin hiện hành (bản KHÔNG lãi tiền gửi)

**Ngày:** 2026-09-28 · **Người soạn:** Mike · **Phạm vi:** đối chiếu số + đề xuất quy trình. Paper-only, không đụng đường tiền live.

---

## 1. File anh gửi là bản nào, ngày nào

Từ chính METADATA bên trong file (không suy đoán):

| Trường | Giá trị |
|---|---|
| `META,system` | **V2.3 go-live** (= V2.2 BAL\|LAG static + park + CAPIT v2 + LAG-allocator band) |
| `META,period` | 2014-01-02 → **2026-06-11** |
| `META,etf_parking_rule` | NEUTRAL: **70%** của (cash+ETF) park vào **E1VFVN30** |
| `META,cash_identity` | *"deposit interest = 0, no margin"* |
| Số dòng | 10.074 TX · 3.101 DAILY · **0 dòng CUSTOM_BASKET** |
| md5 | `84295bee6413153babacc3feb5876698` |

⇒ **Thời điểm: khoảng 11-12/06/2026.** Không tra được chính xác hơn, và lý do đáng lưu: **cả hai repo đều
bắt đầu ngày 2026-06-21** (commit đầu WorkingClaude + KB fleet v1), còn `data/results_registry.md` ra đời
**2026-06-19**. File anh cầm **có trước toàn bộ hệ thống lưu vết của chính chúng ta** — nên mốc duy nhất
còn đọc được là cửa sổ dữ liệu nằm trong file.

---

## 2. So sánh 3 mốc (mọi số đều do tôi recompute độc lập bằng `extract_peryear.py`, không đọc lại print cũ)

| | **(A) File anh gửi** | **(B) Cùng config, 14 ngày sau** | **(C) R3 pin hiện hành = `pin0%`** |
|---|---|---|---|
| Cửa sổ | →2026-06-11 | →2026-06-25 | **AUDIT_END=2026-06-19** (pin) |
| Hệ | V2.3A · park **E1VFVN30** 70% | V2.3A · park E1VFVN30 70% | **V2.4 · park custom30V 30%** |
| **CAGR** | **21,94%** | 22,68% | **23,37%** |
| IS 2014-19 / OOS 2020+ | 19,80 / 23,91 | 20,77 / 24,43 | 20,00 / **26,50** |
| Sharpe₂₅₂ | 1,593 | 1,691 | **1,878** |
| MaxDD | **−23,72%** | −17,88% | **−14,64%** |
| Calmar | 0,925 | 1,268 | **1,596** |
| Final NAV | 589,63B | 640,30B | **684,52B** |
| Lãi tiền gửi | **0%/năm** | 0%/năm | **0%/năm** ✅ |
| self-check | 0 VND | 0 VND | 0 VND |

**Chênh (A)→(C): +1,43pp CAGR · Sharpe +0,29 · MaxDD tốt hơn 9,1pp · Calmar +0,67.**

---

## 3. Vì sao khác — 4 nguyên nhân, xếp theo mức đóng góp

### 3.1 🔴 KHÁC HỆ, không phải khác cách đo (nguyên nhân lớn nhất)
File anh cầm park tiền nhàn rỗi vào **E1VFVN30** — nó có **0 dòng `CUSTOM_BASKET`**, tức rổ custom30V
**chưa tồn tại** ở thời điểm đó. Số hiện hành là **V2.4 = V2.3A + custom30V parking**, và tỉ lệ park cũng
đã đổi **70% → 30%** (anh chốt 15:48 ICT 2026-09-27). Đây là **thay đổi sản phẩm có chủ đích, đã được
duyệt**, không phải "số bị sửa".

### 3.2 🔴 Số 21,94% BẢN THÂN NÓ không tái lập được
Chạy **đúng config đó** 14 ngày sau ra 22,68%, và **MaxDD nhảy −23,72% → −17,88% = 5,8pp**. 10 phiên dữ
liệu mới **không thể** tạo ra 5,8pp MaxDD trên cửa sổ 12 năm — nên phần lớn chênh này là **nhiễu harness**,
không phải thị trường. Nguyên nhân đã ghi thành luật trong registry (rule 6): trước **2026-06-25** engine
chạy `BQ_CACHE_THREADS=4`, DuckDB trả rows **thứ tự ngẫu nhiên** khi query thiếu `ORDER BY` → cùng config,
cùng ngày vẫn ra số khác mỗi lần (spread ~0,2pp baseline, tới ~2,7pp ở config bull-park).
⇒ **21,94% là MỘT MẪU, không phải MỘT SỐ.** Đây đúng là bài học anh nhắc: "số tốt nhưng là số ảo".

### 3.3 🟢 Mọi bản sửa đo lường từ đó tới nay đều kéo số XUỐNG
Nếu chỉ sửa cách đo mà giữ nguyên hệ, số sẽ **thấp hơn** chứ không cao hơn:
custom30V double-count **−4,48pp** · FAIL-C nhãn look-ahead 25 phiên **−0,06pp** · annualize theo LỊCH
(FAIL-F) · `universe_pit` thay `ticker_prune` · `LAG_ADV_BASIS` close→price. ⇒ +1,43pp **không phải** do
nới tay đo.

### 3.4 ⚪ Lãi tiền gửi: KHÔNG liên quan
Cả (A) và (C) đều `deposit interest = 0`. Đúng bản anh yêu cầu. Dải 2 số 23,37…25,71% chốt sáng nay
**không dính** vào chênh lệch này.

> ### ⚠️ Kết luận đọc số
> **KHÔNG được đọc +1,43pp là "hệ tốt lên".** Hai con số khác nhau **ít nhất 4 trục cùng lúc**
> (phương tiện park · tỉ lệ park · vintage dữ liệu · tính tất định của engine) ⇒ **không so trực tiếp được**.
> Muốn có một câu so sánh hợp lệ thì phải chạy A/B đổi **đúng 1 trục**.

---

## 4. Số hiện hành có audit được như file cũ không? — **CÓ, và giàu hơn**

`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_univpit.csv`
· md5 **`4707bcbeb7e801d49a4a851ffd91d5e7`** · 16.633 dòng

| record_type | file anh gửi | pin hiện hành |
|---|---|---|
| TX (từng lệnh, dò được về BQ thô) | 10.074 | 8.827 |
| DAILY (NAV/tiền/CP/ETF từng phiên) | 3.101 | 3.107 |
| METRIC / ANNUAL / META | 31 / 13 / 27 | 37 / 13 / 37 |
| **CUSTOM_BASKET** (giá trị rổ park từng phiên) | — | **3.114** |
| **CUSTOM_MEMBERS** (thành phần rổ từng kỳ) | — | **1.440** |

Tự kiểm tại chỗ hôm nay: `extract_peryear.py` recompute **FULL 23,37 / IS 20,00 / OOS 26,50** — khớp print
engine; self-check 0 VND cả 2 book; `cash_identity` + `nav_identity` + `allocator_replay` đều 0 VND.

---

## 5. 🔴 Lỗ hổng GỐC tôi tìm ra khi soi việc này

**`data/*.csv` nằm trong `.gitignore`** (dòng 57). Hệ quả đo thật:

1. **Tên canonical GHI ĐÈ ĐƯỢC.** Bằng chứng mạnh nhất chính là file anh cầm: cùng tên
   `v23_golive_audit_2014_now.csv`, nhưng md5 anh có là `84295bee…` còn trên đĩa hôm nay là `65e7bb04…`.
   **Hai bản khác nhau, một cái tên, không ai biết cái nào là "số đã công bố".**
2. **822 file audit / 2,1 GB** nằm ngoài version control — nhưng chỉ **679 md5 duy nhất** (143 file trùng nội dung khác tên).
3. **Truy vết md5 đã bắt đầu mục nát:** trong **28** tham chiếu md5 của registry (21 đầy đủ + 7 rút gọn)
   — **2 mất dấu hoàn toàn**: `a953d4bb06f7e429bd55837aebcdaefc` và `f30a5beadde2bc5e117eca47021aabef`.
   *(ĐÍNH CHÍNH bản đầu của báo cáo này: tôi đã viết "5 cái chỉ còn sống trong worktree TẠM" — **SAI**.
   Công cụ kiểm kê B0 chạy đầy đủ cho thấy cả 5 đều có bản canonical; bản đầu chỉ lấy hit ĐẦU TIÊN
   theo thứ tự duyệt thư mục, và hit đó tình cờ là đường dẫn worktree. Chính cái công cụ này bắt
   được lỗi của tôi — đó là lý do phải có cổng cơ học thay vì đếm tay.)*
4. **Đa số pin chỉ trích md5 rút gọn 8 ký tự** ⇒ máy không verify được, chỉ người đọc tin nhau.

Nói thẳng: **luật "CSV là artifact đông cứng" (registry rule 2) hiện KHÔNG có cơ chế nào cưỡng chế.** Nó là
văn xuôi. Và đúng theo mandate của anh — bài học nào diễn đạt được thành mẫu cơ học thì phải thành cổng
chặn commit, không phải thêm một đoạn văn.

---

## 6. Quy trình đề xuất — 6 bước, xếp theo chi phí tăng dần

### B0 — Kiểm kê 1 lần *(rẻ, làm ngay, không cần duyệt)*
Quét mọi md5 registry trích dẫn → đánh dấu **ngay trong registry** cái nào KHÔNG còn tái lập được.
Đừng để một con số mất artifact vẫn im lặng làm neo kỳ vọng.

### B1 — Kho ledger BẤT BIẾN khoá bằng md5 *(lõi của cả đề xuất)*
```
data/pinned_ledgers/<YYYY-MM-DD>__<nhãn-pin>__<md5-8>.csv.gz
data/pinned_ledgers/PINS.jsonl      # 1 dòng/pin
```
Mỗi dòng `PINS.jsonl`: nhãn pin · **lệnh chạy đầy đủ** · `AUDIT_END` · md5 **32 ký tự** · dict config
(mọi trục) · 5 chỉ tiêu · IS/OOS · self-check · ngày pin · ai duyệt.
**Ghi-một-lần:** script từ chối nếu md5 đã tồn tại. Chỉ ~70 pin thật ⇒ vài trăm MB sau nén, **không phải 2,1 GB**.

### B2 — Cổng cơ học `bin/pin_artifact_gate.py` *(pre-commit trên `results_registry.md`)*
Mục mới có bảng chỉ tiêu ⇒ **BẮT BUỘC** có dòng `ledger_md5:` (32 ký tự), file tồn tại trong kho, md5
**tính lại khớp thật**. Thiếu/lệch ⇒ `rc=1`, chặn commit. Biến rule 2 + §8 từ văn xuôi thành cơ chế.

### B3 — Trích số phải mang provenance
Mọi nơi công bố (KB, Discord, báo cáo, email) viết
`23,37% (pin0%, md5 4707bcbe…, AUDIT_END=2026-06-19)`. **Cấm trích số trần.**

### B4 — Luật SO SÁNH 1 TRỤC *(chính là cái thiếu trong ca hôm nay)*
Một bảng so 2 số chỉ hợp lệ khi 2 ledger khác **đúng 1 trục đã khai tên**. Khác ≥2 trục ⇒ **bắt buộc**
in *"KHÔNG so trực tiếp được — đây là 2 hệ khác nhau"* + liệt kê trục. Cưỡng chế được: `PINS.jsonl` đã lưu
dict config ⇒ script tự diff, >1 khoá khác thì từ chối xuất bảng so sánh.

### B5 — Chân CONTROL bắt buộc mỗi lần re-pin
Chạy lại chân CŨ trên code MỚI. Byte-identical ⇒ delta đọc được. Không byte-identical ⇒ **phải giải thích
trước khi pin**. (Đã làm đúng ở custom30V và FAIL-C — cần thành luật, không tuỳ hứng.)

### B6 — Retention
**Không xoá ledger đã pin.** Thiếu dung lượng thì nén, không xoá. Ledger nằm trong worktree tạm ⇒ copy về
kho B1 trước khi worktree bị dọn.

---

## 7. Việc cần anh quyết

| # | Việc | Ghi chú |
|---|---|---|
| 1 | Duyệt **B0** (kiểm kê + đánh dấu md5 mất dấu) | rẻ, không đụng code, tôi làm được ngay |
| 2 | Duyệt **B1+B2** (kho bất biến + cổng pre-commit) | đây là phần thật sự đóng lỗ hổng |
| 3 | Duyệt **B3+B4** (provenance + luật 1 trục) | đổi cách viết, chi phí thấp, chặn đúng lỗi hôm nay |
| 4 | **B5+B6** | tôi đề nghị ghi thẳng vào `coding_guidelines` §8 |

---

## 8. Trạng thái thực thi (cập nhật 2026-09-28 15:xx ICT)

**B0 + B1 + B2 — user duyệt 14:58 ICT, ĐÃ LÀM XONG.** Chi tiết: `B0_pin_artifact_inventory_20260928.md`
và `mike/bin/pin_ledger.py` / `pin_artifact_gate.py` / `pin_artifact_inventory.py`.
B3–B6 vẫn CHỜ user duyệt.

Không việc nào chạm `trading_rules.json`, rails hay logic đặt lệnh.
