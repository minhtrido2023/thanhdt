# assumptions_PAT.md — giả định cốt lõi DD PAT (khoá 2026-11-14, trước khi tính giá trị)
Job: Taylor_20261114_120425. Mọi số "(ước lượng)" là giả định tự đặt, không phải số đo.

## A. Nguồn & cơ sở
- A1 Nguồn chính: BCTC RIÊNG Q3/2026 (PAT không có công ty con ⇒ không có hợp nhất), BCTC bán niên 2026 soát xét (UHY, ngoại trừ), BCTC 2025 kiểm toán (UHY, ngoại trừ) — tải từ cafef CDN (bản scan có chữ ký số của DN), lưu `src/`. Số đọc tay: `facts_extracted.md`.
- A2 BQ chỉ dùng: NP/Revenue quý 2023Q1–2026Q3 (Q4/25 thay bằng số kiểm toán 70,89 = 343,21 − 272,33), ADV, giá P4/than cốc sunsirs. Không dùng GPM/NPM/Cash_P0 của BQ.
- A3 Số cổ phiếu 25.000.000 (TM17). Ngày định giá 30/09/2026 (bảng cân đối gần nhất).
- A4 Trạng thái MÙ GIÁ: **mù một phần**. Brief của Mike có giá 13/11 (72.700); truy vấn BQ lịch sử NP lỡ kèm cột PE/PB. Đã khoá file này TRƯỚC khi tính giá trị; tham số dưới đây suy từ BCTC/ngành, không hiệu chỉnh theo giá.

## B. Lợi nhuận chuẩn hoá
- B1 LNST chuẩn hoá cho V_ngắn = trung vị TTM 12 quý (2024Q4…2026Q3 cửa sổ 3 năm) = **287,7 tỷ** (đo, chuỗi TTM trong REPORT §5). Không loại khoản một-lần (không có: LN khác ≈ 0; truy thu thuế 2025 6,79 tỷ nhỏ).
- B2 EBT HOẠT ĐỘNG (không gồm DT/CP tài chính) mốc cơ sở 2027+: **245 tỷ/năm** (ước lượng) = EBT TTM 306,4 − tài chính ròng ~35 (lãi tiền gửi + tỷ giá) − ~25 tác động bước thuế XK 10%→15% lên phần xuất khẩu (5pp × ~500 tỷ DT XK/năm, ước lượng theo run-rate 9T26 487,5 tỷ).
- B3 Tốt: EBT hoạt động 330 (≈ mức 2025: 372 − tài chính ròng 33 − bước thuế). Xấu: 150 cho 2027–2028 (thiếu quặng kéo dài + P4 về trung vị F2 của Bobby 25.000 CNY), 200 từ 2029.
- B4 Thuế TNDN theo TM27: 5% đến 2030 (10% × giảm 50%), 10% 2031–2032, 20% từ 2033.
- B5 Capex = khấu hao ở trạng thái ổn định (FCFE ≈ LNST). Capex thực 2024–9T26 ≤ 8 tỷ/năm < KH 45 ⇒ đang đầu tư dưới mức duy trì; giả định capex = KH (bảo thủ hơn lịch sử).
- B6 ΔVốn lưu động = 0 ở cơ sở (NWC 30/09 ≈ 53 tỷ, đo từ BCĐKT). Không giả định DLC lại cấp tín dụng thương mại 300 tỷ như cuối 2025.
- B7 g dài hạn danh nghĩa = **2%** (ước lượng; công suất cố định 20 kt, không có dự án mở rộng ⇒ chỉ tăng giá danh nghĩa). Tái đầu tư g/ROE ≈ 0,05 (ROE >> g, không chạm chặn 0,8).
- B8 Không có dự án đầu tư mới (XDCB dở 4,26 tỷ) ⇒ luật NPV=0 không phát sinh khoản nào.

## C. Chi phí vốn & thanh khoản
- C1 r = **13,5%** @ lãi huy động 12T hiệu dụng **7,40%** (`deposit_rate_vn.effective_deposit_rate('2026-11-14')` = cctg_12m 02/11; = điểm neo 03/11) ⇒ không điều chỉnh. β pass-through = 1 (giả định), độ nhạy β 0,5.
- C2 Chiết khấu thanh khoản cơ sở **10%** (ước lượng — không có mô hình Amihud/dữ liệu thực thi của quỹ), độ nhạy 5% / 20%. Cơ sở dữ liệu: ADV trung vị 6T 0,446 tỷ, 3T 0,602 tỷ, 17/129 phiên không khớp (BQ `ticker`); free float ≤ 32,28%.
- C3 Tiền ròng THẬT 30/09/2026 = tiền 1,25 + HTM 558,07 − vay 67,22 − quỹ KTPL 76,69 = **415,4 tỷ**. Ghi chú: 439 tỷ HTM đang cầm cố (bảo lãnh tiền điện + đảm bảo vay) — vẫn là tài sản của PAT. Kế hoạch cổ tức 2026 90% (225 tỷ) KHÔNG trừ (là phân phối cho chính cổ đông).

## D. Kịch bản & trọng số
- D1 Xấu 0,30 / Cơ sở 0,50 / Tốt 0,20 (ước lượng; nghiêng xấu vì: P4 đang ở p90 chế độ 2023+, Bobby P(giảm 12T)=0,66; nguồn quặng ADMIN_GATED; biên Q1/Q3 2026 13,6–14,5%).
- D2 Kịch bản xấu thêm: hợp đồng thuê đất hết ~2034–2035 KHÔNG gia hạn ⇒ đời dự án hữu hạn tới hết 2034, giá trị thanh lý = NWC. Cơ sở dữ liệu: chi phí GPMB phân bổ 16 năm còn 13,16 tỷ, phân bổ ~1,63 tỷ/năm ⇒ ~8,1 năm còn lại (TM9); cam kết thuê >5 năm 1,67 tỷ (TM33.3). Cơ sở & tốt: hoạt động liên tục (gia hạn thuê KCN là thông lệ — ước lượng).
- D3 Pháp lý (vụ án DGC/PAT): KHÔNG đưa vào base (luật user 27/09) — chỉ WARNING + độ nhạy.

## E. Moat (5F tầng b)
- E1 moat_tier = **NARROW**, moat_type = CAPTIVE_SUPPLY/PERMIT (ore access qua công ty mẹ + giấy phép lò/môi trường), có đồng hồ cắt hào (thuê đất ~2034, ưu đãi thuế hết 2030/2032, quặng ADMIN_GATED, thuế XK tăng). ⇒ KHÔNG thêm tham số moat; RONIC = Ke ngầm (g nhỏ, tái đầu tư ~0).

## REV2 (14/11/2026, job Taylor_20261114_122249) — áp đính chính fundamental-skeptic; các mục B2/B3/B5/D1 ở trên được THAY bởi mục này (bản rev1 lưu `rev1/assumptions_PAT.md` md5 d8783c94)
Cơ sở chọn theo dữ liệu BCTC quý 2026, TRƯỚC khi so với giá 72.700; không hiệu chỉnh theo giá.
- R2.1 (thay B5) **FCFE = LNST × (1 − 5,5%)**: trích quỹ KTPL hằng năm 5,1–6,0% LNST (20,71/343,21 = 6,0%; 13,49/264,94 = 5,1%; TM16). Net cash giữ nguyên (đã trừ số dư quỹ 76,69); dòng trích tương lai trừ trong FCFE ⇒ không trừ hai lần. V_ngắn cũng nhân (1 − 5,5%).
- R2.2 (thay B2) **EBT cơ sở = run-rate Q3/26 hoạt động − bước thuế XK**: 4 × (LNTT 63,747 − (DTTC 11,371 − CPTC 1,467)) = **215,4**; trừ bước thuế XK 10%→15% = 5pp × XK Q3 quy năm (4 × (DT 440,03 − bán DLC 376,29) = 255,0, cận trên vì gồm bán nội địa không-DLC) = **12,7** ⇒ **202,6**. Run-rate Q3 đã chịu thuế XK 10% nên chỉ trừ 5pp (không trừ hai lần). Lý do bỏ 245: là 9T quy năm bị Q2 ngoại lai kéo; Q1 ~160/năm (P4 24,5k), Q3 ~215/năm (P4 27,6k) (skeptic). Tốt 330 giữ (gắn: quặng thông lại, mốc M5). Xấu 150/200 giữ. Trọng số 0,3/0,5/0,2 giữ (không có cơ sở dữ liệu độc lập để đổi).
- R2.3 M1 nhánh: xấu (GPM Q4 ≤ 15%) 0,50/0,35/0,15; trung gian (15% < GPM < 22% hoặc DT < 500) 0,30/0,50/0,20; tốt (GPM ≥ 22% và DT ≥ 500) 0,20/0,45/0,35.
- R2.4 (thay A4) Mù giá: cột PE (6,2) hiện ra lúc truy vấn BQ; giả định khoá 1 lần trước khi chạy mô hình; skeptic kiểm không thấy dấu hiệu hiệu chỉnh theo giá (hai lỗi rev1 — thiếu quỹ KTPL, EBT 245 — đều đẩy giá trị LÊN).
- R2.5 Cầm cố Vietinbank 40 tỷ + 100k USD (~42,6 tỷ) cho vay "của Công ty và các công ty thành viên": KHÔNG đổi base (thiếu dư nợ nhóm), chỉ độ nhạy.
