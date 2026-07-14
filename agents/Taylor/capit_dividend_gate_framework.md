# CAPIT dividend gate — framework & verdict

> Taylor, 2026-07-14/15 · job `Taylor_20260714_173435` · **VERDICT: NO-GO, không wire.**
> Đề xuất của user: thêm tiêu chí "cổ tức ổn định 3 năm" (`Dividend_Min3Y`) vào universe `golden`
> của CAPIT sleeve (`pt_v23_audit_2014.py::capit_basket()`).
> Số liệu pin: `data/results_registry.md` mục "CAPIT dividend gate (`CAPIT_DIV_GATE`)".

## 1. Vì sao bối cảnh CAPIT KHÁC custom30V (không suy diễn NO-GO từ đó sang đây)

Sáng 2026-07-14 đã bác một claim DY-floor trong bối cảnh **custom30V** (job `Taylor_20260714_140127`
/`152605`). Nghiên cứu này **không** phải phần đuôi của chuỗi đó, và **không** được kế thừa kết luận:

| | custom30V (đã bác) | CAPIT (nghiên cứu này) |
|---|---|---|
| Số tên | 30, đa dạng | **≤15 (thực tế 2–8)** |
| Thời điểm triển khai | liên tục (parking NEUTRAL) | **tập trung đúng lúc capitulation/washout** |
| DD cấp danh mục bị chi phối bởi | **beta thị trường chung** | ít hơn — đang mua đáy |
| Cơ chế kỳ vọng | tên phòng thủ pha loãng trong 30 tên | "khó giảm sâu hơn" của từng tên có thể chuyển thành DD nhóm-nhỏ tốt hơn |

Giả thuyết của user hợp lý **về nguyên lý** trong bối cảnh này, và phải đo lại từ đầu. Đã đo lại từ
đầu. Kết quả: tín hiệu cấp tên **có thật** (khác custom30V — xem §3), nhưng **không thu hoạch được**
vì lý do cấu trúc (§4) — một cơ chế thất bại **khác hẳn** custom30V.

## 2. Thiết kế test (đúng kỷ luật đã học, không lặp lỗi phương pháp)

Test **giả thuyết bất đối xứng** (ngưỡng chặn giảm sâu), KHÔNG test IC(dividend, forward return):
- Trong universe golden (đã qua quality+cheap gate) tại **mỗi sự kiện CAPIT lịch sử**, so nhóm dy3
  cao (trên trung vị **trong chính sự kiện đó**) vs nhóm thấp.
- Đo **độ sâu drawdown** (mdd) và **return** sau khi mua, khung 3M/6M.
- Bối cảnh mua đáy ⇒ đo **cả phục hồi**, không chỉ downside (khác custom30V).

**Inference (điểm mấu chốt — lỗi overlap sáng nay không được lặp):**
- Các sự kiện CAPIT **chồng lấn cửa sổ forward** ⇒ KHÔNG phải quan sát độc lập.
- Gom sự kiện cách nhau <180d thành **1 EPISODE** = 1 block độc lập → **18 sự kiện → 8 episode**.
- **N thật = 8 episode**, KHÔNG phải 18 sự kiện, KHÔNG phải 84 name-event. Mọi p-value dưới đây
  tính bằng **block-bootstrap trên 8 block** (20k lần), không phải t-test trên name-event.
- Khử confound rẻ: FE theo sự kiện + control `pbz`, **SE cluster theo episode**.

Script: `probe_capit_div/{p1_events_coverage,p2_forward,p3_infer}.py` (tái lập được, seed cố định).

## 3. Kết quả cấp tên — tín hiệu CÓ THẬT

18 sự kiện → 8 episode, 84 name-event. **Coverage `Dividend_Min3Y` = 84/84, KHÔNG null**, ở mọi
giai đoạn kể cả 2014-16 ⇒ **không có vấn đề độ phủ** (câu hỏi mở trong dispatch: đã trả lời, sạch).

| Khung | Chỉ tiêu | Episode-block | t | wins | p (boot) |
|---|---|---|---|---|---|
| 3M | **mdd** (DD nông hơn) | **+2.15pp** | 2.60 | **7/8** | **0.002** |
| 3M | ret | +1.80pp | 0.27 | 3/8 | 0.801 |
| 6M | **mdd** | **+3.37pp** | 2.10 | **7/8** | **0.001** |
| 6M | ret | +8.80pp | 1.13 | 6/8 | 0.218 |

Khử confound `pbz` (FE sự kiện, SE cluster episode): mdd **+2.84pp t=3.24** (3M), **+3.34pp t=3.20** (6M).

**Đọc đúng:** dy3 cao → **DD nông hơn thật**, sign-stable 7/8 episode, sống sót khử confound rẻ;
return **không xấu đi** (không có nghĩa thống kê ở cả 2 chiều). Đây là **khác biệt thật so với claim
custom30V sáng nay** (claim đó chết sau khi sửa overlap; claim này sống sau khi sửa overlap).
**Caveat trung thực:** N=8 block ⇒ p=0.002 chủ yếu do **nhất quán dấu** (7/8), không phải hiệu ứng
đo chính xác. Đừng đọc p này như p của một mẫu lớn.

## 4. Vì sao KHÔNG thu hoạch được — lý do CẤU TRÚC (đây mới là verdict)

Tín hiệu cấp tên thật, nhưng CAPIT **không có chỗ để dùng nó**:

1. **Không có độ dư lựa chọn.** Pool quality-gated = 2–22 tên; rổ chọn thực tế = **2–8 tên**;
   `nsmallest(15)` **chưa bao giờ ràng buộc**. ⇒ dividend chỉ **CẮT** được, **không CHỌN** được.
   Một tiêu chí xếp hạng chỉ có giá trị khi có nhiều ứng viên hơn số chỗ — ở đây thì không.
2. **Gate cứng ≈ NO-OP.** **79/84 name-event (94%) đã trả cổ tức >0 liên tục 3 năm** — vì chính
   quality-gate (ROE_Min5Y≥0.12 ∧ ROIC5Y≥0.10 ∧ FSCORE≥6) **đã hàm ý** điều đó. Doanh nghiệp đạt 3
   ngưỡng này gần như luôn trả cổ tức. Tiêu chí dividend **không mang thông tin mới** vào rổ.
3. Hệ quả: `pos` chỉ thực sự cắt ở **2/18 sự kiện** (2020-07-27 bỏ DPG/KSB/MWG; 2024-08-05 bỏ TLG) —
   2 sự kiện khác bị **fail-safe MINN=3 bỏ qua gate**.

## 5. Backtest cấp hệ (ablation anchor A0-relative, self-check **0 VND** cả 3 arm)

| Arm | FULL | Δ vs A0 | IS 2014-19 | OOS 2020-26 | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| **A0** golden (gate off) | 26.88% | — | 23.09% | 30.44% | 1.80 | −17.9 | 1.50 |
| **A1** `pos` | 26.56% | −0.32pp | 23.09% (**+0.00**) | 29.80% (−0.64) | 1.79 | **−17.9 (y hệt)** | 1.49 |
| **A2** `tilt` | 26.31% | −0.57pp | 22.88% (−0.21) | 29.51% (−0.93) | 1.79 | −17.6 | 1.49 |

**⚠️ Δ KHÔNG phải ước lượng chi phí đáng tin — đọc kỹ:**
- **A1 IS = A0 IS chính xác tới 2 chữ số thập phân (23.09%)** vì gate `pos` **không cắt gì trong toàn
  bộ IS 2014-19**. Toàn bộ −0.32pp của A1 = hệ quả của **4 lần bỏ tên ở đúng 2 sự kiện OOS**. Đó là
  **nhiễu path-dependent của 1-2 sự kiện**, KHÔNG phải bằng chứng gate có hại một cách hệ thống.
- Verdict NO-GO đứng trên **lý do cấu trúc §4** (không có độ dư lựa chọn + quality-gate đã hàm ý
  dividend ⇒ không có gì để thu hoạch), **KHÔNG** đứng trên con số −0.32pp.
- **Điều đáng chú ý nhất về mặt rủi ro: MaxDD KHÔNG cải thiện** (A1 −17.9 y hệt A0). Đây chính là
  metric mà tiêu chí dividend được đề xuất để cải thiện. Tín hiệu DD cấp tên thật (§3) **không**
  chuyển thành DD cấp hệ — cùng kết cục với custom30V A4 sáng nay, dù **qua cơ chế khác** (custom30V:
  beta thị trường át; CAPIT: gate gần như không bao giờ bấm).
- A2 `tilt` cắt mạnh hơn (9/18 sự kiện, thường 6→3, 8→4) = **ép tập trung** vào rổ vốn đã rất nhỏ →
  xấu đi đều ở mọi cửa sổ. Đây là bằng chứng có ý nghĩa hơn A1: khi gate **thật sự** bấm, nó làm
  rổ nhỏ đi chứ không làm rổ tốt lên.

**⚠️ A0 26.88% ≠ R3 pinned 27.84%**: A0 chạy fallback **real-BQ** (local cache FAIL verification
2026-07-14, `ticker` sync timeout) + data-drift `AUDIT_END`. Ablation là **A0-relative** nên kết luận
không phụ thuộc mức tuyệt đối. **KHÔNG dùng 26.88% để re-pin R3.**

## 6. Code (env-gated, production KHÔNG đụng)

`pt_v23_audit_2014.py`:
- `CAPIT_DIV_GATE` ∈ {`off` (default), `pos`, `tilt`}, `CAPIT_DIV_MINN` (default 3).
- Áp **SAU** pb_z cheap-gate trong `capit_basket()`. Fail-safe: <MINN tên sống sót ⇒ **bỏ qua gate**
  cho sự kiện đó (không bao giờ để gate làm rỗng rổ mà sleeve đã sizing để giải ngân vào).
- **Default off ⇒ byte-identical production**: `_div_tag=""` (tên file không đổi) + nhánh gate không
  chạy. Delta duy nhất = 2 cột thừa trong SELECT; `nsmallest(15)` không bao giờ ràng buộc nên **tập
  tên chọn ra bất biến** với thứ tự dòng.

**Hạ tầng mới `AUDIT_EXP_TAG`** (coding_guidelines §8 — bắt được trong lúc làm việc này): arm A0 có
config **TRÙNG** R3 pinned ⇒ tự resolve về đúng tên file canonical và **sẽ ghi đè CSV pinned** (đúng
lỗi 2026-07-06). Tag ép arm thí nghiệm sang path `_exp_*`; rỗng = production.

## 7. Điều kiện tái xét

Nghiên cứu này KHÔNG đóng vĩnh viễn tiêu chí dividend — nó đóng **trong cấu hình CAPIT hiện tại**.
Tái xét nếu **cấu trúc thay đổi** để tạo ra độ dư lựa chọn:
- Nới quality-gate (ROE_Min5Y/ROIC5Y/FSCORE) ⇒ pool lớn hơn, dividend hết bị hàm ý ⇒ có thể mang
  thông tin mới. (Nhưng nới quality-gate là thay đổi lớn hơn nhiều, cần scope riêng.)
- `CAPIT_BEAR_OVERFLOW` bật thường xuyên ⇒ rổ merge custom30V có thể chạm trần 15 ⇒ lúc đó tie-break
  mới có chỗ đứng.
- Tín hiệu cấp tên §3 (dy3 → DD nông hơn, 7/8 episode) **vẫn còn giá trị** — nếu tìm được vehicle có
  độ dư lựa chọn thật và DD không bị beta át.
</content>
