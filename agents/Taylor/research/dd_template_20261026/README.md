# dd_template_20261026 — khối "VỊ TRÍ TRONG CHU KỲ" cho mẫu DD sleeve discretionary

Job `Taylor_20261026_045054` (dispatch Mike, user duyệt 26/10/2026 11:50 ICT). READ-ONLY: không sửa production,
không sửa `kb/` hay `calculated_fear_state_backstop.md`.

| File | Nội dung |
|---|---|
| `TEMPLATE.md` | Mẫu DD đầy đủ: thứ tự làm việc + quy tắc mù, KHỐI CHU KỲ A–F (~1 trang), các mục DD cũ, mục H đối chiếu |
| `REGISTRY_FORMAT_PROPOSED.md` | Định dạng sổ chấm dự báo append-only (đề xuất `kb/data_registry/fundamentals/dd_cycle_reads.md`) — **chưa tạo** |
| `README.md` | Giả định, hạn chế, phụ lục 5 mã |

## 1. Vì sao cần khối này
Sáng 26/10, verdict của 4/5 mã (DDV, NNC, SAS, NT2) dựa vào vị trí chu kỳ hoặc cấu trúc ngành, không dựa vào
số quý. Mỗi báo cáo làm một kiểu: DDV so PB đáy cũ, NNC so giá đá với 2023–24, NT2 dùng PPA/Qc, SAS dùng lộ trình
Long Thành. Vì vậy không so được giữa các mã, và không ai chấm được sau này. Khối chu kỳ chuẩn hoá 6 câu hỏi
rút ra từ chính 5 báo cáo này và từ §2.5 (#1 chu kỳ/cấu trúc, #4 sàn tài sản, điều kiện loại "đáy chưa tới"):

| Mục | Câu hỏi | Rút ra từ |
|---|---|---|
| A | Biên hiện tại ở phân vị nào trong lịch sử chính mã | NNC (biên gộp Q3 57,9%, cao nhất từ khi chuyển sang mỏ Mũi Tàu), DDV (3,7%) |
| B | Giá đầu ra/đầu vào so 5–10 năm | DDV (DAP đỉnh nhiều năm, lưu huỳnh 3,6x), NNC (đá +50% so 2023–24) |
| C | Pha chu kỳ + cơ chế cú sốc (cầu hay chi phí) | DDV: đáy lần này do chi phí, khác 2 đáy cũ do cầu ⇒ PB đáy cũ không so được |
| D | Neo chính sách/cấu trúc có ngày | SAS (Long Thành 2027–28), NT2 (PPA ~2036, Qc theo năm), NNC (giấy phép 2043, trần công suất) |
| E | PE/PB trên LN chuẩn hoá, ex-cash | Cả 5 mã: PE trailing gây hiểu lầm (NT2 4,75x, SAS 5,4x, NNC 4,88x) |
| F | Một dự báo bác bỏ được, có ngày | Mới — chưa báo cáo nào có |

Trích số ở bảng trên lấy từ các `dd_<MÃ>_20261026/REPORT.md`, không đo lại trong job này.

## 2. Giả định và hạn chế (đọc trước khi dùng)
1. **Chưa có bằng chứng khối chu kỳ thêm alpha.** Backstop §9.5 (14 case nhóm b, N_eff ≈ 2 cú sốc độc lập) cho
   thấy discriminator §2.5 không phân biệt được người thắng ở 12M; chỉ #2 (sống sót) có tác dụng, và theo kiểu
   phòng thủ. Screen N-lớn §9 thấy commodity kém non-commodity. Không có lý do tin rằng "đọc pha chu kỳ" dự báo
   được lợi nhuận cổ phiếu. Mẫu này phục vụ **kỷ luật** (cùng câu hỏi, cùng thứ tự) và **so sánh/chấm** về sau.
2. **Quy tắc mù chỉ chống được một loại thiên lệch**: viết câu chuyện chu kỳ để hợp với số quý vừa đọc. Nó không
   chống được việc người viết đã biết giá cổ phiếu (giá là đầu vào hợp lệ của E), hay biết đồng thuận thị trường.
3. **Phân vị biên với 1–3 chu kỳ là mô tả, không phải thống kê.** Ngưỡng cơ học 80/20 ở mục C là quy ước để giảm
   tuỳ ý, chưa được kiểm định. Nếu sổ chấm cho thấy nó sai có hệ thống thì đổi, nhưng phải ghi lại.
4. **Thiếu feed cho đa số biến chi phối của 5 mã**: lưu huỳnh, NH3, đá xây dựng, Qc/Qm, khách quốc tế TSN đều
   không có chuỗi trong `data/`. Feed có sẵn (WB CMO từ 2006-04: DAP, urea, Brent, quặng sắt, cao su, ngô, khô đậu,
   đường, xút; ONI; BDI; giá heo; FX) chỉ phủ trực tiếp mặt đầu ra của DDV và một phần thủy văn của NT2. Mẫu buộc
   ghi `CHUỖI THIẾU` và cấm kết luận đáy/đỉnh khi thiếu, thay vì để người viết tự chọn nguồn báo chí.
5. **Hai bẫy dữ liệu BQ đã gặp trong 5 báo cáo** được ghi thẳng vào mẫu: `GPM_P0` không khớp biên gộp quý BCTC (DDV,
   SAS); `Cash_P0` thiếu tiền gửi có kỳ hạn (NT2, DDV). Đây là lệch quan sát trên 2–4 mã, chưa quét toàn universe —
   nên kiểm lại cho từng mã, không giả định đúng hay sai.
6. **Ranh giới bước 1/bước 2 không cơ học hoàn toàn.** "Không đọc BCTC quý Q" kiểm được qua thứ tự commit, nhưng
   "không đọc tin bình luận KQKD" thì chỉ tự khai. Vì vậy `blind` là tự khai + kiểm thứ tự commit, không phải bằng chứng.
7. **Mẫu không đổi tiêu chí §2/§2.5.** Khối chu kỳ chỉ cung cấp bằng chứng cho #1, #4 và điều kiện loại "đáy chưa tới".

## 3. Sổ chấm — tóm tắt đề xuất
Append-only, kiểu `livermore_reads.md`; Mike ghi, chấm tại `due_date` theo `source` đã khai; HIT/MISS/VOID + Brier;
so với persistence và về-trung-vị-5-năm; cổng sau ≥ 12 sự kiện độc lập `blind: yes`. Chi tiết:
`REGISTRY_FORMAT_PROPOSED.md`. **Cần Mike/user duyệt** đường dẫn và cổng trước khi tạo file.

## 4. Phụ lục — khối chu kỳ sẽ đổi hay khẳng định verdict 5 mã nào (nhận xét từ báo cáo cũ, CHƯA chạy lại)
> Cảnh báo: tôi viết cả 5 báo cáo lẫn phụ lục này, đã biết verdict ⇒ đây là nhận xét có thiên lệch hồi tưởng,
> không phải kết quả mù. Chạy lại mù phải giao phiên/agent chưa đọc 5 REPORT (job khác).

| Mã | Verdict cũ | Khối chu kỳ nhiều khả năng nói gì | Đổi / khẳng định | Ghi chú |
|---|---|---|---|---|
| **DDV** | NON (watchlist) | A: biên ở đáy lịch sử. B: DAP (đầu ra) đỉnh nhiều năm [`dap_monthly.csv`], lưu huỳnh không có feed. C: sốc **chi phí**, không phải sốc cầu như 2016/2019–20/2023 | **Khẳng định NON** | Mục C làm rõ vì sao PB 1,17 không so được với PB đáy cũ 0,68–0,76. Thiếu chuỗi S ⇒ theo luật mẫu chỉ được kết luận "KHÔNG XÁC ĐỊNH" về đáy, trùng với điều kiện loại "đáy chưa tới" |
| **NNC** | NON | A: biên gộp cao nhất từ khi chuyển mỏ. B: giá đá +50% so 2023–24 (nguồn thứ cấp AWM, không có feed). C: ĐỈNH theo luật 80/20 nếu đo được. D: giấy phép 2043, trần 1 tr m³/năm | **Khẳng định NON**; có thể **làm yếu nhận định phụ** "rẻ +32%, hợp value screen" | Định giá cũ gán 40% cho base "giá −12%" và 15% bull "giữ Q3". Nếu C kết luận ĐỈNH, trọng số nghiêng về deep/bear, giá trị trọng số giảm. Chưa tính lại |
| **SAS** | NON | D chi phối: chuyển bay quốc tế TSN→Long Thành 2027–28, suất kinh doanh mới phải đấu thầu. A/B/C gần như không áp dụng (không phải ngành hàng hoá) | **Khẳng định NON** | Khối giúp tách rủi ro cấu trúc có ngày khỏi câu chuyện "PE 5,4x rẻ". Dự báo F tự nhiên: SASCO có/không trúng suất miễn thuế Long Thành trước ngày X |
| **NT2** | NON | A: LN gần đỉnh (năm El Niño, Qc cao). B: ONI có trong `data/oni_index.csv`; Qc không có feed. D: PPA ~2036 (1 nguồn), Qc phân bổ hằng năm | **Khẳng định NON** | Báo cáo cũ đã dùng LN chuẩn hoá + dòng tiền có thời hạn; khối chuẩn hoá cách làm, không thêm thông tin mới |
| **SZL** | NON | Annuity hợp đồng (doanh thu thuê đất phân bổ 50 năm), không chu kỳ. B/C = N/A. D: quỹ đất KCN Long Thành ~91% đã lấp; Long Phước cho thuê từ 04/2027. E: loại cổ tức nhận lệch quý | **Khẳng định NON**, khối gần như không thêm gì | Lý do mẫu cho phép "không chu kỳ ⇒ B, C = N/A" thay vì ép đọc pha |

**Tổng:** nhiều khả năng **0/5 verdict đổi**. Khối chu kỳ có ích ở 2 chỗ: (i) DDV, NNC — làm rõ "PB/PE thấp ở pha
nào", đúng bẫy HPG §8 theo hai chiều; (ii) SAS, NNC, NT2 — buộc đưa rủi ro có thời hạn (Long Thành, giấy phép 2043,
PPA 2036) vào định giá. Cả 5 mã đều không ở trạng thái sợ hãi, nên đây không phải mẫu thử tốt: muốn biết khối chu
kỳ có đổi verdict hay không, cần mã có trigger thật (đáy chu kỳ).
