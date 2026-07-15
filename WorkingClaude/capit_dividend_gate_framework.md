# CAPIT sleeve — tiêu chí DIVIDEND ỔN ĐỊNH 3 NĂM (đề xuất user 2026-07-14)

**Job:** `Taylor_20260714_173435` · **Harness:** `pt_v23_audit_2014.py` (env `CAPIT_DIV_GATE`)
**Trạng thái:** research only — KHÔNG wire. Production `CAPIT_DIV_GATE=off` = byte-identical.

## 1. Vì sao bối cảnh CAPIT KHÁC custom30V (không suy diễn NO-GO từ đó sang đây)

Sáng 2026-07-14 (job `Taylor_20260714_140127` / `152605`) đã bác DY-floor **trong custom30V**. Lý do
bác ở đó KHÔNG áp dụng máy móc sang CAPIT — 3 khác biệt cơ chế:

| | custom30V | CAPIT golden |
|---|---|---|
| Số tên | 30, đa dạng ngành | **2–8** (đo thật, xem §3) |
| Thời điểm triển khai | liên tục (parking NEUTRAL) | chỉ tại washout (RSI-oversold ≥30% rổ) |
| DD cấp danh mục bị chi phối bởi | **beta thị trường chung** → tính chất từng tên bị nhòe | đang mua đáy — beta không chi phối như vậy |
| Trục lựa chọn | yieldcombo (1/PE + 1/PCF) | pb_z (rẻ vs CHÍNH lịch sử 5Y của nó) |

Điểm quan trọng về **pb_z ở đây KHÔNG dính lỗi thang đo chéo ngành** đã bắt sáng nay ở route BANK
của custom30V: CAPIT so pb_z **trong-tên theo thời gian**, không so chéo ngành. Phép đo hợp lệ.

Vì vậy giả thuyết được **đo lại từ đầu** trong đúng bối cảnh CAPIT, không tái sử dụng kết luận.

## 2. Test đúng dạng giả thuyết — BẤT ĐỐI XỨNG, không phải IC

Claim của user = "dividend ổn định 3 năm ⇒ ngưỡng chặn giảm sâu" → đo **độ sâu drawdown sau khi mua**
và **phục hồi**, KHÔNG đo IC(dividend, forward return).

**Inference (bài học sáng nay — hit-rate vẫn dính overlap):** 18 sự kiện CAPIT có cửa sổ forward
3–6M **chồng lấn nhau** (vd 2022-04-19 / 06-17 / 09-28 cùng một con bear). Gộp chúng thành
**8 EPISODE độc lập** (gap ≥180d) và block-bootstrap trên episode. N thật = **8**, không phải 84.

## 3. PHÁT HIỆN CẤU TRÚC QUYẾT ĐỊNH — golden KHÔNG CÓ ĐỘ DƯ ĐỂ CHỌN

Đo trên 18 sự kiện washout thật 2014→2026 (`probe_capit_div/events_coverage.csv`):

- **Pool sau quality-gate: 2–22 tên. Rổ được chọn: 2–8 tên. `nsmallest(15)` CHƯA BAO GIỜ ràng buộc.**
  Rổ = TOÀN BỘ tập hợp lệ sau cheap-gate, không phải "15 tên tốt nhất trong nhiều ứng viên".
- ⇒ Mọi thao tác dividend trên golden **chỉ có thể CẮT BỚT**, không thể "chọn khéo hơn".
  Tie-break trong rank = **vô hiệu hoàn toàn** (rổ < 15 nên rank không đổi kết quả).
- **Coverage `Dividend_Min3Y` = 84/84 name-event, KHÔNG null ở bất kỳ giai đoạn nào** (kể cả 2014-2016).
  Không có vấn đề độ phủ như lo ngại — báo cáo trung thực: dữ liệu đủ.
- **79/84 name-event (94%) ĐÃ trả cổ tức >0 liên tục 3 năm.** Gate cứng `Dividend_Min3Y>0` chỉ loại
  **5/84** name-event trong 12 năm — và 3/5 rơi vào đúng 1 sự kiện (2020-07-27: KSB/DPG/MWG).

**Đây là lời giải cơ chế:** quality-gate sẵn có (ROE_Min5Y≥0.12 ∧ ROIC5Y≥0.10 ∧ FSCORE≥6 ∧ thanh
khoản ≥2 tỷ) **đã hàm ý trả cổ tức đều** gần như chắc chắn. Tiêu chí dividend **trùng lặp** với cái
đã có, không thêm thông tin mới. Gate cứng = NO-OP về mặt cấu trúc, không cần backtest mới biết.

## 4. Tín hiệu cấp TÊN — CÓ THẬT, và sống sót phép đo nghiêm

Chia trong-từng-sự-kiện theo dy3 (=`Dividend_Min3Y`/Price) trên/dưới trung vị (khử confound regime):

| Khung | DD nông hơn (hi−lo) | t | wins | block-bootstrap p | FE-event + khử confound pb_z |
|---|---|---|---|---|---|
| 3M | **+2.15pp** | 2.60 | 7/8 episode | **0.002** | +2.84pp (t=3.24) |
| 6M | **+3.37pp** | 2.10 | 7/8 episode | **0.001** | +3.34pp (t=3.20) |
| ret 3M | +1.80pp | 0.27 | 3/8 | 0.801 (vô nghĩa) | −0.85pp (t=−0.26) |

**Khác sáng nay:** claim DY-floor custom30V CHẾT sau khi sửa overlap (p 0.011→0.067). Ở CAPIT nó
**SỐNG** (p=0.002 sau block-bootstrap 8 episode). Và nhóm dy3 cao **rẻ hơn nhẹ** (pb_z −1.06 vs
−0.94) → confound rẻ chạy **NGƯỢC** hướng claim, không giải thích được hiệu ứng.
Return **không xấu đi** (t≈0) ⇒ phòng thủ này "miễn phí" **ở cấp tên**.

⚠️ N=8 episode là RẤT NHỎ. 7/8 + CI bootstrap loại 0 là bằng chứng đáng kể nhưng KHÔNG mạnh tuyệt đối.

## 5. Nghịch lý phải giải — và vì sao vẫn phải chạy backtest cấp hệ

Tín hiệu cấp tên có thật, nhưng cách DUY NHẤT khai thác nó (§3: chỉ cắt được, không chọn được) là
**cắt rổ trung vị 5 tên → 2–3 tên**. Nên câu hỏi cấp hệ là:

> +2.15pp DD nông hơn mỗi tên có bù nổi mất phân tán khi rổ 5 tên còn 2–3 tên không?

Đây đúng là bài học custom30V vehicle hôm nay (proxy cấp nhóm có thể **đảo dấu** so với cấp hệ) —
nên KHÔNG suy diễn, phải đo cấp hệ thật. Kết quả §6.

## 6. Backtest cấp hệ — 3 arm, anchor vào arm LIỀN KỀ (không so baseline gộp)

Lệnh (`$DNA_PYEXE`, `BQ_CACHE_THREADS=1`, `AUDIT_END=2026-06-19`, self-check 0 VND):
```bash
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
AUDIT_END=2026-06-19 BQ_CACHE_THREADS=1 AUDIT_EXP_TAG=capdiv_a0 \
  $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge          # A0 baseline (gate off)
# A1: + CAPIT_DIV_GATE=pos  AUDIT_EXP_TAG=capdiv_a1
# A2: + CAPIT_DIV_GATE=tilt AUDIT_EXP_TAG=capdiv_a2
```
Self-check **0 VND** cả 3 arm (BAL+LAG). Anchor = A0 (arm liền kề), KHÔNG so baseline gộp.

| Arm | FULL | Δ vs A0 | IS 2014-19 | OOS 2020-26 | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| **A0** golden (gate off) | 26.88% | — | 23.09% | 30.44% | 1.80 | −17.9 | 1.50 |
| **A1** `pos` (Dividend_Min3Y>0) | 26.56% | **−0.32pp** | 23.09% (**+0.00**) | 29.80% (−0.64) | 1.79 | **−17.9 (Y HỆT)** | 1.49 |
| **A2** `tilt` (dy3 ≥ trung vị rổ) | 26.31% | **−0.57pp** | 22.88% (−0.21) | 29.51% (−0.93) | 1.79 | −17.6 (+0.3) | 1.49 |

**Đọc kết quả:**
- **A1 IS = +0.00 CHÍNH XÁC** → gate `pos` **không hề cắn** trong 2014-19; 100% tác động nằm ở OOS,
  và ở OOS nó **ÂM** (−0.64pp). Không phải "edge rớt OOS" — nó chưa từng có edge, chỉ có chi phí.
- **A1 MaxDD Y HỆT A0 (−17.9)** → gate được mua để phòng thủ nhưng **giao 0 phòng thủ**, chỉ lấy đi
  return. Đúng dạng thất bại của custom30V Arm A4 sáng nay, **nhưng vì lý do khác** (không phải
  beta chi phối — ở đây là §3 không có độ dư + sleeve quá nhỏ để dời DD cấp hệ).
- **A2 âm cả IS lẫn OOS** (−0.21 / −0.93) — nhất quán âm, không phải nhiễu một chiều.
- A2 đổi 0.3pp MaxDD lấy 0.57pp CAGR/năm → Calmar vẫn XẤU ĐI (1.50 → 1.49).

**Rổ thật bị A2 cắt** (9/18 sự kiện cắn, 7 sự kiện fail-safe SKIP vì <3 tên sống):
`2020-03-11: 6→3 (bỏ CVT,SAB,SCS)` · `2020-07-27: 8→4 (bỏ DPG,GIL,KSB,MWG)` ·
`2022-06-17: 5→3 (bỏ HPG,SAB)` · `2026-03-09: 6→3 (bỏ CTR,NTC,VGC)`.

## 8. VERDICT — **NO-GO cả 2 arm. Không wire. Production 0 chạm.**

Nghịch lý §5 đã được giải bằng số: tín hiệu cấp tên **CÓ THẬT** (+2.15pp DD nông hơn, p=0.002, sống
sót block-bootstrap — mạnh hơn hẳn claim custom30V sáng nay đã chết), **nhưng KHÔNG THU HOẠCH ĐƯỢC**.
Lý do là cấu trúc, không phải tham số: golden **không có độ dư để chọn** (§3), nên cách duy nhất tác
động lên nó là **cắt rổ 5 tên xuống 2–3 tên** — mất phân tán ăn hết phần DD nông hơn, và ở cấp hệ
sleeve CAPIT quá nhỏ để dời MaxDD. Tinh chỉnh ngưỡng/`CAPIT_DIV_MINN` **không cứu được** — vấn đề
không nằm ở ngưỡng.

**Bài học chuyển giao:** "tiêu chí đúng ≠ tiêu chí dùng được". Một tiêu chí **trùng lặp** với gate đã
có (quality-gate đã hàm ý trả cổ tức: 94% name-event) thì dù đo cấp tên có ý nghĩa thống kê thật,
nó vẫn không thêm thông tin — chỉ thêm ràng buộc. Kiểm tra **độ dư lựa chọn** (`nsmallest` có ràng
buộc không?) **TRƯỚC** khi backtest — 1 truy vấn đã trả lời được phần lớn câu hỏi này.

**Không route quant-skeptic:** cả 2 arm TỰ BÁC (âm return, DD không cải thiện) → không có ứng viên
wire nào để verify (nhất quán với `Taylor_20260714_152605`).

## 7. Ghi chú kỹ thuật — 2 điểm hạ tầng phát sinh

1. **`AUDIT_EXP_TAG` (mới, coding_guidelines §8).** Arm A0 có config TRÙNG baseline R3 pinned ⇒ tự
   resolve về đúng tên file canonical `..._etfliqcustompitg_wtnamecap.csv` và **sẽ ghi đè** CSV pinned
   (đúng lỗi 2026-07-06). `AUDIT_EXP_TAG` ép mọi arm thí nghiệm sang path `_exp_*`. Rỗng = production.
2. **BQ local cache đang FAIL verification** (`sync.log` 2026-07-14: `ticker` sync timeout 300s).
   Mọi arm chạy fallback real-BQ (authoritative, chậm hơn) ⇒ số vẫn đúng. **Cần Winston xem:**
   `ticker_financial` báo `count local=66387 vs BQ=65178` + `max_time local=2026-07-08 vs BQ=2026-05-04`
   — local NHIỀU hơn và MỚI hơn BQ, bất thường, không phải staleness thông thường.
