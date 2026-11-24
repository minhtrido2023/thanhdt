# SKEPTIC v4 — quant-skeptic vòng cuối (24/11/2026, Mike lưu nguyên kết luận)

**VERDICT: REFUTED · confidence medium.**

Xác nhận: md5 23/23 file LOCK khớp; run1=run2=run_dna (`d1540070…`); PREREG mtime 05:42 UTC < calc 06:03; tính lại từ panel_v4.csv khớp calc_out_v4.json (N=13, trung vị 1,49%, q25 −49,95%, q75 36,6%, LOO −4,7…5,6%, hull 26,31pp, 0% ở phân vị 0,452). Sửa OCH/OGC, GIC, LBM, GAS đúng cơ học, không còn double-count từ OCH/GAS.

## Lỗi
1. **BLOCKING (đổi dải >3pp): MSN thiếu look-through MSR/MML.** `inputs/stakes_all.csv` chỉ có MSN→MCH/TCB/VSN; `calc_ck_v4.py:249-257` dựng danh sách con chỉ từ file này. `raw/kbs_sh/MSR.json`: Tầm nhìn Masan 87,46% (30/10/2026); `MML.json`: Masan Agri 82,04%. MSR giá trị thị trường ≈54.475 tỷ vs sổ ≈15.504 tỷ (P/B 3,5). Mốc 20/11 14,4% = (MSN 9,8% + PAN 19,1%)/2 ⇒ MSN quyết định đầu trên. Thêm s·(MV−E): stake MSR 87,46% (+MML) → trung vị 11/2026 22,9%, 10/2026 19,7%; 43,7% → 20,3%; 25% → 18,0%. Hull đầu trên 14,4 → 18,2…22,9%. Các tháng 03–09, trung vị 1,49%, q75 36,6%, lưới (a) KHÔNG đổi. Chưa verify: MSN sở hữu Masan Horizon bao nhiêu (nhưng MSN hợp nhất MSR ⇒ hiệu dụng ≥ 50%). v3 từng ghi hạn chế này (REPORT_v3:215), v4 bỏ câu đó (REPORT_v4:210).
2. MINOR: lệch thời điểm F1 — con +tiền thu từ ex, mẹ E_p chưa có lãi pha loãng đến BCTC sau (`calc_ck_v4.py:69-80,275,290`). OGC 11/2026 CK 2,6 → 10,3%; trung vị tháng 11 +0,26pp.
3. MINOR: cộng tiền thu lên BCTC rất cũ (SDV 2020Q2, PTH 2015Q4) — tác động SNZ ~0,2%.
4. MINOR: quy tắc ambiguous rộng hơn PREREG (mọi dòng âm ⇒ cả (mã, ex)) — chưa khai trong "Khác PREREG"; chỉ VIC/GEG/HPA, không tác động.
5. MINOR: GIC chuyển sang số KBS từ ngày niêm yết 22/06 < update 30/06; bản chặt VSC 60,4%, đường không đổi.

## Đề xuất dải HHS
Base 0% (nhãn đầu lạc quan), +6%, +37%: trung thực. **+14% "hiện tại" thấp quá (chiều có lợi cho HHS) — nên ≈ +18…+23%.** Bỏ −12% chỉ khi đã kiểm HHS không có cấu trúc R1/R2. Dòng "4 mốc khớp số skeptic" (REPORT_v4:42) là vòng tròn, không phải bằng chứng.

## Rerun khuyến nghị
(1) thêm MSN→MSR/MML (verify stake PIT qua Masan Horizon/Masan Agri; giá/CP/BCTC VCI) rồi tính lại đường tháng/hull/mốc; (2) quét mọi holding trong N tìm con niêm yết thiếu trong stakes_all; (3) cộng lãi pha loãng của mẹ vào E_p khi không tham gia; (4) bỏ PROCEEDS_ADD khi BCTC con >4 quý; (5) khai quy tắc ambiguous; (6) khôi phục hạn chế MSR/MML.
