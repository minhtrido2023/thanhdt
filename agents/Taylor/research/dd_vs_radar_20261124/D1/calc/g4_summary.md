# G4 — Skeptic đối xứng: hướng tác động lên tâm × kết cục (đọc-chỉ; 2026-11-24)

Nguồn: 73 vòng skeptic (`agents/Taylor/research/**/skeptic/r*.json` + `r*_raw.md`) của 21 mã. Chi tiết từng finding: `g4_skeptic_findings.csv`.
Các file `r*.json` chỉ chứa verdict + tóm tắt; danh sách phản đối nằm ở khối `<<<VERDICT_JSON>>>` trong `r*_raw.md` (`checks.*`, `killer_objection`) — tôi đọc từ đó.
19 file `SKEPTIC_*.md` (vòng cũ dạng văn xuôi) và `skeptic_optimistic/pessimistic_r3.md` của PAT **KHÔNG** đưa vào N (ngoài phạm vi "file json").

## N (khai rõ)
- **N = 328 finding**, **21 mã** (BSR CSV CST DBC DCM GAS HHS LLM MSB PAT PNJ POW QTP SCL SZL TCH TTA VCB VCP VGS VLB), 73 vòng skeptic.
- Finding cùng mã/cùng vòng **không độc lập**: số đơn vị gần-độc-lập thực là ~21 mã (hoặc ~72 vòng), không phải 328. Đặc biệt CST/DCM/LLM/PNJ/VCB/VCP/HHS/... mỗi mã có 4-5 vòng, và cùng một phản đối thường tái xuất ở vòng sau.
- Một finding = một mục trong `missing_items` (đánh số 1,2,3...), một check fail (`optimistic_comp_sotp_bias`, `data_provenance`, `confirmation_bias_flipflop`...) hoặc `killer_objection`. Mục hai chiều được tách thành 2 dòng. **Việc tách/đặt ranh giới finding là quyết định của tôi** → số đếm có sai số ±10-15% tuỳ cách tách; không có double-annotator.
- Hướng (`direction`) do tôi gán thủ công từ câu chữ skeptic (không phải heuristic). `neutral/process` = lỗi nguồn/quy trình/không nêu hướng.
- `magnitude_pct` = **trị tuyệt đối** % tâm do skeptic nêu (hoặc, khi ghi "do tôi tính" trong evidence, tôi chia số đ/cp cho tâm của báo cáo). Có số ở 182/328 dòng; 146 dòng bỏ trống (skeptic ghi "chưa định lượng được"). Với khoảng (vd "-34% tới -72%") tôi lấy giá trị đầu/cận gần base, nên **median là ước lượng thô**.

## Định nghĩa kết cục (`outcome`)
- `applied_to_base`: báo cáo vòng sau đổi base/tâm theo finding (bảng "Đính chính" ghi "(a) VÀO BASE" hoặc có Δ tâm ≠ 0 trong cầu nối).
- `sensitivity_only`: chỉ đưa vào độ nhạy / kịch bản / dòng hiển thị, "0 (base)" nhưng có số độ nhạy đi kèm ("(b)").
- `rejected`: bảng ghi "0"/"giữ base"/"giữ r=13,5%" không kèm số độ nhạy, hoặc giải thích vì sao không đổi. **Lưu ý: gộp "bác bỏ" với "không áp, không lượng hoá"; nguồn không phân biệt hai trường hợp này.**
- `unknown`: không có bản sửa sau skeptic đó (vòng cuối / báo cáo không còn bản kế) hoặc dòng bảng ghi "—". **73 dòng nằm ở vòng cuối** (không có bản sau) nên bị `unknown` về cấu trúc.
- `process_fixed`: lỗi quy trình/nguồn đã khắc phục (không ảnh hưởng tâm).

## Bảng 1 — direction × outcome (TẤT CẢ 328 finding)
| direction | applied_to_base | sensitivity_only | rejected | unknown | process_fixed | Tổng | % applied |
|---|---|---|---|---|---|---|---|
| too_high | 53 | 59 | 27 | 72 | 1 | **212** (64,6%) | 25,0% |
| too_low | 28 | 21 | 5 | 18 | 0 | **72** (22,0%) | 38,9% |
| neutral/process | 5 | 2 | 17 | 12 | 8 | **44** (13,4%) | 11,4% |
| Tổng | 86 | 82 | 49 | 102 | 9 | 328 | 26,2% |

## Bảng 2 — chỉ các vòng ĐÃ có bản sửa sau (loại 73 dòng vòng cuối; N=255, 19 mã)
| direction | applied_to_base | sensitivity_only | rejected | unknown | process_fixed | Tổng | % base | % base+sens | % rejected |
|---|---|---|---|---|---|---|---|---|---|
| too_high | 53 | 59 | 27 | 20 | 1 | 160 | 33,1% | 70,0% | 16,9% |
| too_low | 28 | 21 | 5 | 2 | 0 | 56 | 50,0% | 87,5% | 8,9% |
| neutral/process | 5 | 2 | 17 | 7 | 8 | 39 | 12,8% | 17,9% | 43,6% |

## Trung vị độ lớn (|%| tâm, chỉ dòng có số)
| direction | n có số (toàn bộ) | median | n applied_to_base có số | median applied | (answered-only) median |
|---|---|---|---|---|---|
| too_high | 128 | 7,3% | 43 | 7,1% | 7,1% (n=89) |
| too_low | 49 | 10,4% | 22 | 10,2% | 12,0% (n=37) |
| neutral/process | 5 | 8,5% | 1 | 8,4% | — |
Độ lớn too_low lớn hơn too_high ~1,4-1,7 lần (bất kể áp hay không). Cỡ mẫu nhỏ, không có CI; không dùng làm bằng chứng thống kê.

## Số mã có ≥1 too_low applied_to_base
**16/21 mã** (BSR CSV DBC DCM GAS LLM MSB PNJ POW QTP SCL SZL TTA VCB VCP VLB). 5 mã còn lại: CST, HHS, TCH, VGS, PAT — trong đó VGS/TCH/PAT/HHS chủ yếu ít vòng/không có bản sửa, CST có finding too_low nhưng chỉ ở mức độ nhạy/hiển thị.
Để so sánh: ≥1 too_high applied_to_base = **17/21 mã** (16 mã trên + CST).
Có ≥1 finding too_low (bất kể kết cục) ở 20/21 mã; trong 72 vòng-theo-mã, 49 vòng có ≥1 too_low, 71 vòng có ≥1 too_high.

## Đọc kết quả — và giới hạn
1. **Skeptic nêu too_high nhiều gấp ~2,9 lần too_low** (212 vs 72). Nhưng skeptic ở chế độ DD_GENERAL bị buộc "hai chiều" (attack 8), và nhiều "missing_items" mặc định là khoản trừ (nghĩa vụ bỏ sót) nên mất cân bằng đầu vào là một phần do cấu trúc checklist, không nhất thiết do mô hình thiên cao.
2. **Khi được nêu, too_low được sửa VÀO BASE thường hơn too_high** (50,0% vs 33,1% ở vòng có bản sửa; 38,9% vs 25,0% toàn bộ). Tức quy trình sửa **không** có dấu hiệu "chỉ nhận phản biện hạ tâm". Phát hiện này phụ thuộc vào cách tôi phân hướng; nhiều "too_low" applied là lỗi mô hình có thể kiểm chứng (đếm trùng, thiếu lá chắn thuế, bảo hành trừ kép), dễ được nhận hơn "thiếu bằng chứng".
3. Về **số tuyệt đối base-adjustment**: too_high applied 53 > too_low applied 28, nên tổng thể tâm bị kéo xuống nhiều lần hơn lên (chưa đo tổng Δ đ/cp, chỉ đếm số lần). Không dựng được "tổng Δ% tâm" vì cầu nối mỗi mã có cơ sở khác nhau.
4. `rejected` thấp ở too_low (8,9%) vs too_high (16,9%) — nhưng n=5/27, chênh không đáng tin.
5. `sensitivity_only` chiếm 70% (too_high) / 87,5% (too_low) khi cộng với base: phần lớn finding too_high "chưa lượng hoá / không có cơ sở độc lập" vào độ nhạy chứ không vào tâm — đúng luật V4a/"điều chỉnh GIẢM cần cơ sở độc lập" trong KB. Luật này tạo bất đối xứng có chủ đích: điều chỉnh giảm cần bằng chứng độc lập; điều chỉnh tăng (theo skeptic) hầu hết là lỗi tính toán nên qua dễ hơn.
6. Không phát hiện bằng chứng cho giả thuyết "tâm của fleet bị phản biện kéo thấp có hệ thống"; cũng KHÔNG đủ để bác bỏ — N độc lập ~21 mã, hướng gán thủ công, ranh giới finding chủ quan.

## Ví dụ trích nguyên văn (killer_objection / check trong `r*_raw.md`)
### too_high → applied_to_base
1. CST r1 (`dd_CST_20261111/skeptic/r1_raw.md`): "N trong mô hình là LNST gộp, nhưng mỗi năm 46–92 tỷ (trung bình ~37%, gần đây ~79% LNST) rời VCSH vào quỹ khen thưởng phúc lợi/khoản không thuộc cổ đông. Phần lãi thật thuộc cổ đông chỉ bằng một phần nhỏ của 75 tỷ ⇒ tâm có lẽ ở ~4.000–8.600 chứ không phải 13.084." → REPORT_rev2: 13.084 → 4.563.
2. BSR r1: "The 39.004,5 bn Dung Quất expansion is booked as NPV-zero growth capex with no growth-vs-compliance classification. If it is mainly a compliance/upgrade project, the ~35.900 bn still to be spent is a value outflow under the 22/11 rule and the centre falls by up to ~40% — the QTP failure mode" → REPORT_rev3: −1.885 đ/cp.
3. SZL r3: "Tỷ lệ trích quỹ KTPL năm 2026 là 20% theo chính thuyết minh EPS Q3/2026 (13,979/69,897), không phải 11,215% như mô hình. Khoản thiếu này kéo tâm xuống 1.688 (−6,5%), vượt ngưỡng trọng yếu 5%." → REPORT_rev5: −1.766.
4. VCB r2: "The model treats 100% of net profit as accruing to shareholders' book value, yet the audited 2025 equity roll-forward shows ≈9–12% of profit leaving equity (most likely the bonus/welfare fund)... the base falls 15–21% to ≈37.600–40.400" → REPORT_rev3: "(a) vào base, có nguồn".
5. PNJ r1: "The valuation divides post-raise firm value by 511.72m + 550m shares while assuming the full 8,000 bn goes to settling obligations... the 6,370–7,640 per-share range exists only if new investors overpay ~2.3× the model's own value" → REPORT_rev3: "(a) base".

### too_low → applied_to_base
1. TTA r1: "Tâm 6.342 dựa trên giả định chưa khai báo: doanh thu thuỷ điện cố định danh nghĩa 34 năm trong khi chi phí lạm phát 3%/năm... Chỉ cần chỉ số hoá giá 2%/năm cho thuỷ điện là tâm +22% (7.728)" → REPORT_r4: +937 (K1), +602 (K3).
2. LLM r2: "Base NOPAT counts warranty twice: historical GPM 4,5% is already net of warranty accruals... at any accrual rate ≥1% of revenue the centre is >5% too low." → REPORT_rev4: +3.616 (28.760 → 32.376).
3. PNJ r3: "Branch O2 assumes simultaneously that the company has NO capital (plan downgraded one notch) and that it HAS borrowed the full 8.000 (deducting 8.640). That is a double penalty, pinning O2 to 219 and the centre ~30% too low." → REPORT_rev5: 4.205 → 5.490.
4. DBC r3: "Rev3 strips the real-estate segment's profit from historical ROE but keeps its capital (about 1,186 bn real-estate WIP) inside operating equity, valued at 0.70× book and dragging ROE_op down — the centre is understated by +5% to +29% (estimate)" → REPORT_rev4: +20,3%.
5. SCL r3: "khung nợ mệnh giá thiếu lá chắn thuế: +643 đ ... +1.748 đ, tức +3,8% đến +10,4%" (check missing_items, chiều RẺ) → REPORT_rev7: +644.

### too_high → chỉ sensitivity/rejected (để đối chiếu)
- CST r3: "The +1.459 in the base assumes the 130,66 bn goes 100% to dividends... at a 49,95% fund rate the centre falls to ~5.290 (−12%)" → REPORT_rev4 r3-1: "0 (base); dải độ nhạy −1.946…0".
### too_low → chỉ sensitivity/rejected (để đối chiếu)
- QTP r1: "Nếu đi qua được, tâm lên khoảng 10.000 (+30%), vượt trên toàn bộ vùng biến thể đơn lẻ" → rev4: legal-vn Đ18 ⇒ phải sửa PPA ⇒ chỉ độ nhạy.
- MSB r2: "Ke 13,5% nằm ngoài dải nội địa 12,3–13,4% (+1,2% đến +16%)" → rev4 E.2 #5: "0".

## Hạn chế bổ sung
- Kết cục đối chiếu qua bảng "Đính chính so với rev trước" trong báo cáo kế tiếp (do Taylor viết) — là **tự khai báo của người được phản biện**, không phải audit độc lập về việc tâm có đổi hay không. Dòng cụ thể được ghi `file:dòng`/hàng bảng trong `outcome_evidence`; số dòng báo cáo có thể trượt nếu file bị sửa.
- Hầu hết finding "too_high" lớn không lượng hoá (`unknown` 72 + `sensitivity_only` 59) nên median của chúng bị chọn lọc theo "skeptic dám ghi số".
- Sai số phân loại hướng của tôi chưa kiểm bởi người thứ hai. Đề nghị người dùng spot-check ~20 dòng ngẫu nhiên trước khi dựa vào tỷ lệ.
