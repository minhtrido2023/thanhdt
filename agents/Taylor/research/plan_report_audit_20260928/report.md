# Audit: `bin/send_plan_report.sh` — hardcode-drift + boilerplate lặp

**Job**: Taylor_20260928_162635 · **Phạm vi**: CHỈ `bin/send_plan_report.sh` (973 dòng, đọc đầy đủ)
· **Phương pháp**: đọc toàn bộ source, đối chiếu với plan JSON thật (`data/trade_plans/plan_*.json`,
15 ngày SpaceX + 15 ngày ZaloPay gần nhất, cộng 1 file lưu trữ 2026-08-07 làm ca FUNDED_BY_JIT
điển hình), tái dựng offline phần render đơn thuần bằng string-format (KHÔNG chạy script thật —
tránh side-effect ghi `data/dcf_lens_history.csv`, gọi DNSE live, hay `margin_day_approval` ghi
bản duyệt margin thật). KHÔNG sửa code, KHÔNG tạo worktree, KHÔNG commit.

---

## 1. Số liệu/tham số tĩnh có nguy cơ hardcode-drift

| # | Dòng | Trích | Đánh giá |
|---|------|-------|----------|
| 1 | 723 (ĐÃ SỬA, merge 98a9d633) | `f"...tuân thủ trần PARK {_o_tgt_s} (park-trim)..."` đọc `park_trim.get("target_park")` | ĐÃ FIX — bug gốc user báo (đã hardcode "80%" trần trụi). Còn lại: 1 bug **CÙNG LỚP** dưới đây **chưa sửa**. |
| 2 | **481-483** | `"⚠️ **Plan có dấu hiệu đã sizing theo ĐÒN BẨY nhưng phiên sẽ chạy bằng VỐN TỰ CÓ** — khối lượng tính cho **1,3× vốn** mà chỉ có **1,0× vốn**; triệu chứng sẽ là WAIT_CASH, không phải lỗi rõ."` | **CHẮC CHẮN BUG, CÙNG LỚP với ca 80%.** `1,3×` là literal gõ tay mô tả `_pv['lever_f']` — biến SỐ THẬT đã có sẵn trong scope (dùng đúng 10 dòng dưới, dòng 492: `f"(f={_pv['lever_f']}, gói {_pv['loan_package_id']})"`). Hằng số nguồn là `CAPIT_LEVER_APPROVED_F = 1.3` ở `trading_bot/plan.py:973` — **hôm nay đúng vì f=1.3 trùng khớp ngẫu nhiên**, nhưng đổi gói đòn bẩy (vd sang f=1.5 như V2.5 leverage đã có tiền lệ đặt tên, dù hiện DISABLED) thì dòng cảnh báo này lập tức sai mà không ai phát hiện — y hệt cơ chế bug PARK 80%. **Sửa 1 dòng**: thay `"1,3×"` → `f"{_pv['lever_f']:g}×"`, `"1,0×"` giữ nguyên (đúng nghĩa "vốn tự có", không phải tham số). |
| 3 | 284, 329, 342 | `PRICE_TOLERANCE = 0.03` | KHÔNG cùng lớp — hằng số **tự sở hữu** bởi chính gate này (không có bản sao ở nơi khác để lệch theo). Đã tự ghi chú rõ "chưa hiệu chỉnh kỹ" (dòng 278-283), coi là tham số cần tinh chỉnh chứ không phải hardcode-drift. |
| 4 | 406 | `if abs(_dev) > 0.10:` (ngưỡng lệch CAPIT sizing) | Tự sở hữu, cùng logic §3. |
| 5 | 815 | `abs(_pt_sum - _pt_eng) > max(1e5, 0.01 * _pt_eng)` | Tự sở hữu (ngưỡng đối chiếu nội bộ Σ lệnh vs Σ engine), không mô tả 1 config bên ngoài. |
| 6 | 216 | `STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}` | Khớp đúng 5-state canonical (CLAUDE.md). Rủi ro THẤP (đây là nhãn cấu trúc ổn định, không phải ngưỡng vận hành hay đổi) nhưng vẫn là 1 bản sao thủ công — nếu ai đổi tên state ở nguồn canonical mà quên sửa dict này, `state_verify_note` sẽ tự in ra dòng cảnh báo "hai field trong cùng plan mâu thuẫn" (dòng 252-255) — tức là bug loại này ĐÃ có lưới bắt sẵn, không im lặng như ca 80%. Không cần sửa, chỉ ghi nhận. |

**Kết luận mục 1**: đúng 1 bug hardcode-drift **chưa sửa, cùng lớp với ca 80% đã fix** — dòng
481-483 (`"1,3×"`). Đề xuất sửa cùng đợt.

---

## 2. Cụm từ/đoạn lặp lại không đổi thông tin quyết định

Bằng chứng lấy từ 2 nguồn thật: (a) đối chiếu `park_trim_proposal.notes` giữa các plan file
2026-09-14/15/16 và 2026-09-22/23/25 (số liệu ngày khác nhau, cấu trúc câu giống hệt); (b) tái
dựng offline đúng logic render (file `/tmp/render_offline.py`, không chạy script thật) cho
`data/trade_plans/plan_SpaceX_2026-09-29.json` (19 lệnh PARK_TRIM thật, hôm nay) và
`data/trade_plans/plan_SpaceX_2026-08-07.json` (ca FUNDED_BY_JIT điển hình, được chính comment
trong source dùng làm ví dụ chuẩn — dòng 513-515).

### 2a. Lặp NHIỀU LẦN TRONG CÙNG 1 report (không phải lặp giữa các ngày)

**Dòng 723-724** — mỗi lệnh BÁN PARK_TRIM thuần (không kèm JIT) đều in nguyên văn:
```
      ↳ ℹ️ Lý do: tuân thủ trần PARK 30% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này.
```
Plan SpaceX 2026-09-29 thật có **19/19 lệnh** là PARK_TRIM thuần ⇒ **câu này lặp NGUYÊN VĂN 19
LẦN** trong 1 report (chỉ số `30%` giống nhau vì cùng ngày, cùng target — không đổi giữa các
lệnh). Người đọc phải lướt qua ~19 dòng giống hệt nhau để tìm ra lệnh nào (nếu có) khác biệt.

### 2b. Lặp GIỮA CÁC NGÀY, không đổi format

- **`DCF_DISCLAIMER`** (`dcf_valuation.py:126`, ~100 từ) + **`DD_DISCLAIMER`**
  (`trading_bot/due_diligence.py:1048`, ~55 từ) — in nguyên văn (dòng 788-791) **mỗi ngày có ít
  nhất 1 lệnh MUA** (`dcf_shown`/`dd_shown`). Đây là disclaimer BẮT BUỘC theo §6b/quy chuẩn — giữ
  nội dung, nhưng đang render y hệt mỗi ngày trong phần thân report chính, không tách phụ lục.
- **Ngày HOLD (0 lệnh)** — plan `2026-09-14/15/16` (3 ngày liên tiếp thật, `buys=0, sells=0`)
  render **gần như identical**: `"🎯 Hành động: **GIỮ NGUYÊN (HOLD)** — không có lệnh nào ngày
  mai."` (dòng 793) + `"✅ Trạng thái: HOLD 0 lệnh — không cần duyệt, bot trực phiên đồng bộ trạng
  thái."` (dòng 891) — nguyên văn, chỉ khác ngày tháng và (đôi khi) dòng DT-gate clock.
- **`park_trim.notes` — wall-of-text ticker-by-ticker** (không phải lỗi của send_plan_report — nó
  chỉ echo `notes[:2]` truncate 300 ký tự, dòng 822-823/827-829 — nhưng nội dung do
  `compute_park_trim.py` sinh ra lặp cấu trúc gần như identical liên tiếp nhiều ngày). Ví dụ thật,
  3 ngày liên tiếp `2026-09-22/23/25`, câu mở đầu **giống hệt tới từng dấu câu**:
  > `"rổ mục tiêu kỳ 2026-08-05: 19/30 mã khả thi, bỏ 11 mã (Σ 4.44% trọng số) — trọng số đã CHUẨN
  > HOÁ LẠI trên tập khả thi: DCM 0.60% (target ...đ < 1 lô (100cp × ...đ)); DDV 0.10% (target
  > ...); ..."` — liệt kê đủ **11 mã** với công thức giống hệt, chỉ số VND (giá phiên) đổi. Đây
  > KHÔNG phải nội dung send_plan_report tự tạo, nhưng script vẫn CHỌN echo nguyên khối này vào
  > report duyệt hằng ngày thay vì tóm tắt ("11 mã dưới 1 lô, xem chi tiết ở artifact") — góp phần
  > trực tiếp vào cảm giác "loãng tín hiệu" user mô tả.
- **`state_verify_note`** (dòng 244-246) — `"✅ state=3 (NEUTRAL) khớp golive_state_today.json
  (as_of=...)"` in mỗi ngày market không đổi regime (đa số ngày, vì NEUTRAL kéo dài); nội dung
  đúng là compliance-provenance bắt buộc (§28 mandate), nhưng với CEO đọc mỗi tối, một dòng
  checkmark cố định lặp hàng chục ngày liền chiếm chỗ ngang với 1 lệnh cần duyệt thật.
- **`price_verify_note`** (dòng 333-338) — `"✅ giá đã xác minh N/N lệnh có giá so DNSE close hôm
  nay"` — tương tự, đúng compliance nhưng lặp dạng câu mỗi ngày có lệnh.

### 2c. Phân loại

| Đoạn | Loại | Đề xuất |
|---|---|---|
| DCF_DISCLAIMER, DD_DISCLAIMER | (a) BẮT BUỘC compliance | GIỮ nội dung — nhưng chuyển xuống PHỤ LỤC cuối report, in 1 LẦN/report (không lặp theo từng lệnh — hiện đã là 1 lần/report nên chỉ cần dời vị trí) |
| "✅ state=... khớp golive..." / "✅ giá đã xác minh..." | (a) BẮT BUỘC provenance (§28) | GIỮ nhưng RÚT GỌN thành 1 icon/dòng trong header, KHÔNG phải câu văn đầy đủ mỗi ngày — chỉ mở rộng thành câu đầy đủ khi có MISMATCH (⚠️/🛑) |
| "↳ ℹ️ Lý do: tuân thủ trần PARK X% (park-trim)..." lặp theo TỪNG lệnh | (b) RÚT GỌN — có thể condense | Gộp thành **1 dòng tổng** cho cả nhóm PARK_TRIM thay vì lặp theo lệnh (xem §4 mockup) |
| "🎯 Hành động: HOLD..." + "✅ Trạng thái: HOLD 0 lệnh..." | (b) RÚT GỌN | Gộp 2 dòng thành 1 dòng duy nhất cho ngày HOLD |
| park_trim.notes wall-of-text 11-13 mã | (c) XOÁ khỏi thân report | Thay bằng 1 dòng tóm tắt ("N mã dưới 1 lô, xem `compute_park_trim.py` output để biết chi tiết") — KHÔNG mất thông tin vì artifact gốc vẫn giữ đủ, chỉ không đẩy nguyên khối vào kênh duyệt |

**KHÔNG đề xuất xoá** (đều là an toàn bắt buộc, đã tồn tại vì sự cố thật): funding note "Tiền đâu
ra" (💧), cảnh báo BLOCKED_*, mismatch state/price (nhánh ⚠️/🛑), cảnh báo margin, cảnh báo Trứng
vàng cần rút, cảnh báo Σ CAPIT lệch >10%.

---

## 3. Đề xuất khung report mới

Nguyên tắc: (i) DANH SÁCH QUYẾT ĐỊNH lên đầu, mỗi lệnh 1 dòng (nhóm PARK_TRIM đồng nhất gộp 1
dòng); (ii) LÝ DO ngắn ngay cạnh, không lặp công thức; (iii) CẢNH BÁO nổi bật riêng; (iv) PHỤ LỤC
gấp gọn ở cuối cho compliance/provenance + chi tiết kỹ thuật.

### 3a. Case A — SpaceX 2026-09-29 thật (19 lệnh PARK_TRIM thuần, không có MUA)

**HIỆN TẠI** (trích 3/19 lệnh + dòng đầu, xem đầy đủ 19 lần lặp ở §2a — toàn văn ~1400 ký tự chỉ
cho phần lệnh, gần 40 dòng):
```
🎯 Hành động: **19 lệnh** (19 bán, 0 mua):
   ✅ Lệnh BÁN PARK L1 trim là LỆNH THẬT, đã gộp vào 19 lệnh ở trên (không liệt kê riêng để
   tránh đếm 2 lần) — sẽ đặt cùng lúc với lệnh mua, ĐỘC LẬP về lý do (tuân thủ trần PARK,
   không phải nguồn tiền cho lệnh mua trừ khi dòng 'Tiền đâu ra' bên dưới ghi rõ FUNDED_BY_JIT).
  • BÁN ACB 500cp @ ~21,100đ — BÁN PARK gộp: L1 500cp + L2 0cp = 500cp × 21,100đ = 10,550,000đ.
      ↳ ℹ️ Lý do: tuân thủ trần PARK 30% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này.
  • BÁN BID 700cp @ ~35,750đ — BÁN PARK gộp: L1 700cp + L2 0cp = 700cp × 35,750đ = 25,025,000đ.
      ↳ ℹ️ Lý do: tuân thủ trần PARK 30% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này.
  • BÁN CTG 700cp @ ~29,850đ — BÁN PARK gộp: L1 700cp + L2 0cp = 700cp × 29,850đ = 20,895,000đ.
      ↳ ℹ️ Lý do: tuân thủ trần PARK 30% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này.
  ... (16 lệnh nữa, cấu trúc y hệt)
```

**ĐỀ XUẤT** (dùng đúng số thật của cùng plan — Σ tính từ 19 order value ở JSON = 217.570.000đ,
khớp `park_trim_proposal.trim_proposed_vnd`):
```
📋 Kế hoạch 2026-09-29 — SpaceX · NEUTRAL · CẦN DUYỆT: 19 lệnh BÁN PARK (không có MUA)

🅿️ BÁN PARK TRIM — 19 mã, Σ 217,6tr (đưa PARK 384,7tr/pool 476,7tr về trần 30%)
   ACB 500 · BID 700 · CTG 700 · EVF 100 · HDB 400 · HPG 600 · LPB 200 · MBB 900 · MSB 400 ·
   SHB 400 · TCB 600 · TPB 300 · VCB 400 · VHM 300 · VIB 300 · VIX 200 · VND 300 · VPB 800 ·
   VRE 100 (cp mỗi mã) — giá tham chiếu & giá trị chi tiết: xem phụ lục.
   Lý do (áp dụng CHUNG cho cả 19 lệnh): tuân thủ trần PARK 30%, KHÔNG liên quan tài trợ mua.

⏳ Trạng thái: CHỜ DUYỆT — preflight 08:45 sẽ RED nếu chưa duyệt.

▸ Phụ lục (giá/giá trị từng mã, provenance state/price/park compliance) — xem cuối report.
```
→ Từ ~40 dòng/1400 ký tự xuống 7 dòng chính, KHÔNG mất ticker/qty/Σ VND/lý do nào — chỉ gộp câu
"Lý do" lặp 19 lần thành 1 câu áp dụng chung (đúng bản chất: cùng lý do, cùng target %, cùng
ngày).

### 3b. Case B — SpaceX 2026-08-07 thật (ca FUNDED_BY_JIT: 1 MUA + 14 BÁN PARK tài trợ)

**HIỆN TẠI** (trích, xem toàn văn tái dựng ở trên — 15 dòng lệnh + phần "MỤC RIÊNG 2" L2/JIT lặp
lại DANH SÁCH 11 mã BÁN JIT một lần nữa với format khác, ~25-30 dòng tổng):
```
🎯 Hành động: **15 lệnh** (14 bán, 1 mua):
   ✅ Lệnh BÁN PARK L1 trim + L2 JIT là LỆNH THẬT, đã gộp vào 15 lệnh ở trên (không liệt kê
   riêng để tránh đếm 2 lần) — ...
  • BÁN ACB 400cp @ ~22,150đ — BÁN PARK gộp: 300cp L1 park_trim (tuân thủ trần PARK 80%) +
    100cp L2 jit_unpark (tài trợ lệnh mua DRI). Tổng 400cp × 22,150đ = 8,860,000đ.
  • BÁN BID 500cp @ ~37,900đ — BÁN PARK gộp: 400cp L1 park_trim (tuân thủ trần PARK 80%) +
    100cp L2 jit_unpark (tài trợ lệnh mua DRI). Tổng 500cp × 37,900đ = 18,950,000đ.
  ... (12 lệnh BÁN nữa, note dài lặp cấu trúc "BÁN PARK gộp: Xcp L1 park_trim (tuân thủ trần
      PARK 80%) + Ycp L2 jit_unpark (tài trợ lệnh mua DRI). Tổng...")
  • MUA DRI 3500cp @ ~13,100đ
      ↳ 💧 Tiền đâu ra: lệnh này được tài trợ bằng cách bán 11 mã PARK tổng 42.0tr (thu ròng
        41.9tr) ⇒ mua NGUYÊN lệnh 3500cp (tiền mặt 4.8tr → 0.9tr). Chi tiết ở mục L2 bên dưới...
💧 ĐỀ XUẤT BÁN PARK TÀI TRỢ LỆNH MUA (L2/JIT) — 11 lệnh BÁN, Σ ... — CẦN DUYỆT RIÊNG
   Tài trợ cho: DRI
   BÁN: ACB 100cp (...) · BID 100cp (...) · CTG 100cp (...) · ... (11 mã, LẶP LẠI 11/14 mã
   đã liệt kê ở trên trong orders[], chỉ khác đơn vị hiển thị — cùng 1 lượng bán được mô tả
   2 LẦN trong report)
```

**ĐỀ XUẤT**:
```
📋 Kế hoạch 2026-08-07 — SpaceX · NEUTRAL · CẦN DUYỆT: 1 lệnh MUA (tài trợ bởi 14 lệnh BÁN PARK)

🟢 MUA DRI 3.500cp @ ~13.100đ (~45,9tr)
   💧 Tiền đâu ra: bán 11 mã PARK (Σ 42,0tr, thu ròng 41,9tr) + tiền mặt sẵn có 4,8tr
   → đủ mua NGUYÊN lệnh. Tiền mặt sau: 0,9tr.

🅿️ BÁN PARK (đi kèm, CẦN DUYỆT CÙNG) — 14 mã, Σ [X]tr:
   · 11 mã tài trợ MUA DRI ở trên (ACB, BID, CTG, HDB, LPB, MBB, SHB, TCB, VCB, VHM, VPB)
   · 3 mã trim thuần theo trần PARK 80% (SHS, TPB, VIX) — không liên quan tài trợ MUA
   Chi tiết qty/giá từng mã: xem phụ lục.

⏳ Trạng thái: CHỜ DUYỆT.
```
→ Loại bỏ việc liệt kê 14 mã BÁN **2 lần** (1 lần trong orders[], 1 lần trong khối L2 JIT) —
gộp thành 1 khối theo VAI TRÒ (tài trợ-MUA vs trim-thuần), giữ đủ tên mã + tổng tiền + lý do,
tách chi tiết qty/giá riêng lẻ sang phụ lục cho ai cần đối chiếu.

---

## 4. Ghi chú phạm vi

Đây là **audit + đề xuất**, không phải implementation. `bin/send_plan_report.sh` KHÔNG bị sửa,
không có worktree/commit nào tạo ra từ job này. 2 mockup ở §3 dùng SỐ THẬT trích từ
`data/trade_plans/plan_SpaceX_2026-09-29.json` và `plan_SpaceX_2026-08-07.json` (đã lưu trữ) —
không phải số giả định.
