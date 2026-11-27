# R1 — "Value Radar ở đáy 10 năm" có thật sự là "thị trường rẻ"?

Job `Taylor_20261123_170313` · 24/11/2026 · dữ liệu tới **2026-11-23** (BQ `tav2_bq.ticker`) · NGHIÊN CỨU/CHẨN ĐOÁN — không wire, không đổi radar.
Mọi số dưới đây đọc từ `calc/out/summary.json` (trừ khi ghi khác). Tái lập: `calc/fetch_panel.py` → `calc/analyze_r1.py` (threads=1; chạy 2 lần, md5 5 file output trùng — `calc/OUTPUTS.md5`; đầu vào khoá ở `calc/INPUTS.md5`).

## Kết luận (đọc trước)

1. **Rẻ thật SO VỚI LỊCH SỬ, nhưng một phần ba độ rẻ là do lợi nhuận đang ở đỉnh.** Lợi nhuận TTM của rổ radar = **1,58× lợi nhuận TB 5 năm** (cao nhất trong 227 tháng từ 2008; trung vị 10 năm 1,27). Từ 30/06/2026, P/E giảm 13,30 → 9,66 gần như hoàn toàn nhờ **lợi nhuận tăng** (ln +0,221) chứ không do giá giảm (ln −0,086). 5 mã (VHM, VIC, BSR, HPG, VCB) chiếm 61% phần lợi nhuận tăng.
2. **Chuẩn hoá lợi nhuận vẫn chưa xoá được độ rẻ so với lịch sử:** P/E trên lợi nhuận TB 5 năm = 14,26, ở **p1,7** trong 10 năm (vì P/E chuẩn hoá thời trước cũng cao hơn). Nếu dựng lại radar bằng P/E chuẩn hoá + spread chuẩn hoá: điểm **16,0 (vẫn RẺ)**, thay vì 2,2.
3. **Phần lớn mâu thuẫn radar↔DD đến từ THƯỚC ĐO.** Radar so với P/E trung vị 10 năm = 14,74. Với r = 13,5% của DD, g = 6% và ROE hiện tại, P/E công bằng = **9,26** (8,10 nếu ROE về trung vị 10 năm). Như vậy P/E 9,66 hiện tại cao hơn mức công bằng theo DD **4–19%**, khớp với việc DD thấy giá ≈ tâm (trung vị giá/tâm hôm nay 1,057). P/E trung vị 2014–19 tương ứng r ngầm định chỉ **≈9,9%**. Khoảng cách giữa hai mốc neo (ln 0,60) chia ra: **≈78% do r** (lịch sử ngầm chấp nhận suất sinh lời ~10%, DD đòi 13,5%) và **≈22% do chuẩn hoá ROE/lợi nhuận**.
4. **Cấu trúc rổ không phải nguyên nhân chính.** Tách nhóm nào thì P/E vẫn thấp so với 10 năm: ngân hàng p9, phi ngân hàng bỏ Vingroup p0,8, top-100 trọng số đều p7,6. Riêng nhóm giống tập DD (phi ngân hàng, hạng vốn hoá 31–250, universe_pit) **chỉ ở p31–36 nếu trọng số đều**: ở nhóm vốn hoá vừa, độ "rẻ" yếu hơn rõ. Chính 36 mã DD có P/E TTM trung vị 6,03 (thấp nhất 10 năm của chúng), nhưng lợi nhuận của chúng cũng ở mức 1,46× TB 5 năm. Tâm DD hàm ý P/E trung vị 5,75.
5. **Dữ liệu đúng.** Cột PE tái lập chính xác bằng ΣNP_P0..P3 trên giá thô (sai số tương đối lớn nhất 1,9e-16). Top-100 hôm nay có 0 mã lỗ, 2 mã PB≤0 bị loại khỏi top-300. Bỏ các mã bị cấm, P/E còn 9,55. Bỏ VHM, P/E thành 10,29. Số liệu không đổi kết luận.

## Bảng kết luận R1

| Giả thuyết | Hướng ảnh hưởng tới "rẻ" của radar | Độ lớn đo được | Mức tin |
|---|---|---|---|
| **H1** lợi nhuận đỉnh chu kỳ | Làm "rẻ" **ÍT thật hơn** | EPS TTM/TB5Y 1,584 (p100, kỷ lục; trung vị 10Y 1,274); thực/CPI 1,487 (p100). ROE rổ 17,4% (p97,5 10Y; trung vị 14,0%), phi NH 18,5% (p99). Nếu tỷ lệ về trung vị ⇒ P/E tương đương 11,20 (p7,5) ⇒ **giải thích 35% độ lệch log so với trung vị 10Y**. P/E chuẩn hoá 5Y 14,26 vẫn p1,7 | **Cao** (đo trực tiếp). Caveat: lợi nhuận VHM/VIC theo đợt bàn giao, BSR theo crack spread |
| **H2** cấu trúc rổ | **Ít thật hơn ở nhóm vốn hoá vừa**, không đổi ở nhóm vốn hoá lớn | Ngân hàng P/E 7,54 p9,2; phi NH 10,81 p0; phi NH bỏ Vin 10,97 p0,8; top-100 trọng số đều 10,47 p7,6, trung vị 11,30 p4,2; **DD-like trọng số đều 9,22 p36, trung vị 9,98 p31**, cap-weight 9,97 p9,2; P/B DD-like trung vị 1,05 p6,7. Composite DD-like 14,6 | Trung bình |
| **H3** lãi suất/thước đo | **Phần lớn mâu thuẫn là do thước đo** | P/E công bằng (r 13,5%, g 6%) 9,26 / 8,10 (ROE hiện tại / chuẩn hoá) ⇒ thị trường **+4% / +19%** so với mức công bằng. g ngầm định ở P/E 9,66 = 6,7% (top-100), 6,2% (phi NH). Cùng mặt bằng lãi huy động 7,4% ±0,75pp trong 10Y (38 tháng: 2018–19, 10/2022–05/2023, 06–11/2026): P/E trung vị 16,24, thấp nhất chính là hôm nay. Spread trên EY chuẩn hoá 5Y = −0,39pp (p56, TRUNG TÍNH; spread thô +2,96pp ở mức hẹp hơn chỉ 4,2% lịch sử) | Trung bình (phụ thuộc g; xem lưới) |
| **H4** dữ liệu | Trung tính (số đúng) | PE = Price×OShares/ΣNP_P0..P3, sai số 1,9e-16; khớp cache radar 227 tháng, hôm nay khớp đúng; lệch lịch sử tối đa 0,39 (2011–13), tối đa 0,07 năm 2026, do dữ liệu cũ đã được restate; Price/Close trung vị 1,00. Mã bị cấm chiếm 3,96% trọng số cap, P/E bỏ chúng 9,55 | **Cao** |
| **H5** chế độ mới (FTSE 21/09/2026) | Không kết luận được | P/E p0,16 (rolling 10Y), p0,32 (5Y), p0,13 (3Y), **p10,1 (expanding 2008+)**; composite 2,3 (10Y) vs **9,4 (expanding)**, cả hai đều RẺ. P/E 2008–13 trung vị 10,88, thấp nhất 6,66 ⇒ 9,66 có tiền lệ. Sau FTSE mới 46 phiên: P/E 11,54 → 9,66 | **Thấp** (quá ngắn) |

**Radar sai bao nhiêu phần trong mâu thuẫn radar↔DD?** Gần như toàn bộ mâu thuẫn là do hai cách so khác nhau. Radar so tương đối với lịch sử, DD so tuyệt đối với (r, g), và cả hai đều đúng theo cách đo của mình. Radar có một điểm yếu riêng: **dùng P/E TTM khi lợi nhuận đang ở kỷ lục**, làm phóng đại độ rẻ. Sửa điểm này thì điểm radar từ 2,2 lên **16** (vẫn RẺ) và thành phần spread từ "rộng nhất 10 năm" về **trung tính**. Phần còn lại là mốc lịch sử ngầm định r ≈ 10%, thấp hơn DD 3,6pp. Đây là chuyện chọn chuẩn so sánh, không phải lỗi số liệu.

## Phương pháp

- **Panel**: phiên cuối mỗi tháng từ 2007-01 đến 2026-11-23, gồm MỌI mã của `tav2_bq.ticker` (176.838 dòng, 1.280 mã). Dùng `mcap = Price thô × OShares` (registry `fundamentals/valuation_pe_pb_pcf_ps.md`, Bẫy 4/7). Floor phân vị 2008-01-01 (`vnindex_pe_mirror_col.md`). Cờ `universe_pit.in_universe` dùng cho H2; phiên 23/11 chưa build nên lấy cờ tháng trước.
- **Rổ radar dựng lại theo tháng** đúng công thức `value_radar.py`: top-300 vốn hoá → lọc PB>0 → top-100, trọng số trần 10%, trung bình điều hoà, PE>0.
- **Lợi nhuận chuẩn hoá**: theo từng mã, trung bình NP_ttm tại t, t−12, …, t−48 (cần đủ 5 mốc). Bản 10Y cần ≥7/10 mốc. Bản thực deflate bằng CPI chain từ `cpi_vn.cpi_monthly_df()`; tháng thật cuối cùng là **2026-06**, các tháng 07–11 giữ YoY cuối. Tính ở cấp doanh nghiệp, không theo từng cổ phiếu, nên pha loãng được khử khi chia cho vốn hoá. Độ phủ trọng số: 94% (5Y), 90% (10Y).
- **Phân vị**: nhân quả, chỉ so với quá khứ trong cửa sổ, cùng hàm với radar. Bản tháng dùng cửa sổ 120 tháng (tối thiểu 24); H5 dùng chuỗi radar theo ngày.
- **N**: 227 tháng (2008-01 → 2026-11); cửa sổ 10Y = 120 tháng. Chuỗi định giá tự tương quan rất cao, nên **số quan sát độc lập hiệu dụng chỉ cỡ vài chu kỳ (ước lượng 3–5 trong 10 năm)**. Các phân vị là **mô tả vị trí, không phải kiểm định**. Không có p-value nào ở đây.
- **Tập DD**: 36 mã trong `kb/dd_price_zones.json`, lấy entry có dd_date mới nhất. Danh sách là danh sách hôm nay, nên lịch sử của nhóm này **có chọn mẫu hồi tố** và chỉ dùng để mô tả.

## Chi tiết số

**Phân rã thay đổi P/E** (tổng gồm cả mã lỗ, cùng mã chung ở hai mốc):

| Mốc | Số mã chung | ln Δ vốn hoá | ln Δ lợi nhuận | P/E cap10 từ → nay | 5 mã đóng góp lợi nhuận tăng nhiều nhất (nghìn tỷ) |
|---|---|---|---|---|---|
| 30/06/2026 | 95 | −0,086 | +0,221 | 13,30 → 9,66 | VHM 34,1 · VIC 31,4 · BSR 14,9 · HPG 6,3 · VCB 5,7 (61%) |
| 28/11/2025 | 87 | +0,043 | +0,413 | 14,37 → 9,66 | VHM 72,4 · VIC 34,1 · BSR 25,9 · HPG 13,1 · VPB 10,5 (61%) |
| 29/11/2024 | 83 | +0,345 | +0,648 | 14,01 → 9,66 | VHM 78,4 · VIC 33,5 · BSR 25,0 · CTG 20,9 · VPB 18,0 (51%) |

**Lưới P/E công bằng (H3)** `(1−g/ROE)(1+g)/(r−g)`, ROE top-100 = 17,4% (phi NH 18,5%); r 13,5% = neo DD 03/11, lãi huy động hiệu dụng neo = hôm nay = 7,4% ⇒ không điều chỉnh:

| r \ g (ROE top-100) | 4% | 6% | 8% |
|---|---|---|---|
| 12,3% | 9,65 | 11,02 | 13,57 |
| 13,4% | 8,52 | 9,38 | 10,80 |
| 13,5% | 8,43 | **9,26** | 10,61 |
| 14,5% | 7,63 | 8,17 | 8,98 |

Bản đầy đủ (gồm phi NH): `calc/out/h3_fair_pe_grid.csv`. Ở r = 12,3% (đầu dưới dải Ke) và g = 6%, P/E công bằng là 11,0. Khi đó thị trường **rẻ khoảng 12%** ⇒ kết luận H3 nhạy với Ke ±1pp.

**P/E theo giai đoạn (radar theo ngày)**: 2008–13 trung vị 10,88 (6,66–26,62) · 2014–19 trung vị 15,55 (10,80–23,30) · 2020–24 trung vị 13,95 (9,33–19,53) · 2025–26 trung vị 13,51 (9,62–16,59).

## Điều KHÔNG kết luận được / giới hạn

- **Chưa đo biên lợi nhuận gộp toàn rổ** — dùng ROE tổng (Σlợi nhuận/Σvốn chủ) thay thế; biên gộp chỉ có ở `ticker_financial` và không áp dụng cho ngân hàng.
- Bước nhảy lợi nhuận của VHM (64,8 → 98,9 nghìn tỷ TTM) và VIC (11,6 → 43,0) từ 06/2026 **chưa được đối chiếu với BCTC gốc** ở đây. Tuy vậy, bỏ VHM thì P/E chỉ thành 10,29, nên kết luận "rẻ so với lịch sử" không phụ thuộc vào một mã.
- Cờ universe_pit ngày 23/11 lấy theo tháng trước, nên chỉ ảnh hưởng nhóm DD-like ở tháng cuối.
- H5: protocol FTSE cấm đổi tham số. Dữ liệu sau sự kiện (46 phiên) không đủ để nói "chế độ mới". Nếu có rerating thì về lý thuyết nó đẩy P/E công bằng **lên**, tức càng làm "rẻ" thật hơn, nhưng điều này chưa đo được.
