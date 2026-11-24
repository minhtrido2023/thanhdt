# SKEPTIC v5 — quant-skeptic rà phần thay đổi (24/11/2026, Mike lưu nguyên kết luận)

**VERDICT: CONFIRMED · confidence medium** (cho phần thay đổi v5; dùng làm thông số hiển thị cho DD, không phải tín hiệu).

Tính lại độc lập từ panel_v5.csv khớp 4 chữ số: N=12, trung vị −3,243%, LOO −8,06…+1,57%, q75 37,66%, đường tháng −16,81…19,71%, mốc 20/11 = PAN 19,71% (n=11); MSN 20/11 dựng lại từ giá × CP × tỷ lệ = 213.616 tỷ, CK 45,68%. Diff trial→chính chỉ ở MSN; không thay đổi code nào bị giấu ngoài S1–S4 + cờ posthoc.

## Đã kiểm, đứng vững
- MSN→MSR/MML/MCH/TCB khớp BCTN MSN 2025 (MCH 66,2/67,4; MML 91,2/94,3; MHT 94,9; TCB 19,7/19,8). Không đếm trùng (VSN/NET/VCF nằm dưới MML/MCH). s·(MV−E) đúng vì E_p không gồm NCI. MSN là R2 (phần sổ −25,7…−27,1 nghìn tỷ) hợp lý.
- MSR 87,46% (KBS 30/10/2026) áp ngược: sai chữ PIT, sai số bị chặn (CP MSR 1.099,2→1.105,0tr, +0,5%); s_MSR=0 vẫn cho trung vị −3,24% và mốc 19,7%.
- VSC rời N do VGR 74,35→54,35% (tự khớp: bán 12,65tr CP + cổ tức CP 30%); hiệu lực 28/10/2025 là thận trọng; không phải sửa-theo-kết-quả (15 ca ngoài N không ca nào vào N). Ca ngưỡng (VSC 2 tháng/ngưỡng 3). Biến thể S1_VSC_VGR_as_v4: trung vị +1,57%, mốc hiện tại 23,3%.
- Lãi pha loãng OGC đúng cơ học (tv 1.300 tỷ, gain 53,0 tỷ), không đếm trùng.
- NET loại đúng (HPC 66,2% = MCH). Holding quanh trung vị không thiếu con niêm yết nào.

## Lỗi nhỏ (không đổi dải (a)∪(d), trung vị, mốc hiện tại)
A. MSN có 74,58tr CP ưu đãi chuyển đổi 1:1 (CDPS, Bain) nằm trong E_p nhưng không trong MV_p: MSN 20/11 45,7→~42,9%.
B. `sweep_v5.py:55-56` bỏ trung gian niêm yết không có giá: GEX→GEL 79,1%→VGC 50,21% + PXL 65% bị sót; GEX 39,0→~43,3% (đã trên trung vị). Chỉ GEX dính trong 12 holding.
C. K1 khai thiếu: có 2 dòng POSTHOC (stakes_override MCH 66,2% + participation_override MCH 51,28%, mtime sau trial); report ghi nhầm 51,28% là "KBS" (nhãn code); "không đổi hull" chỉ đúng với (a)∪(d) — hull đúng chữ §C2 đổi −101,4…19,7 → −88,5…30,0 và c3_control N 9→10.
D. MSR áp ngược (xem trên) ≤0,5pp tỷ lệ.

## Về dải HHS
Base 0% (nhãn đầu lạc quan) trung thực; bỏ +6% đúng; bỏ −17% thận trọng (bất lợi cho HHS, chiều an toàn). **Mốc "hiện tại" báo KHOẢNG ~15–23%, không phải điểm 19,7%** (n=11: bỏ 1 holding dưới PAN → 23,3%, trên PAN → 15,0%; giữ VSC → 23,3%; PAN độ phủ 0,65 sát ngưỡng 0,60). Stress: 33,5% (PREREG) … 37,7% (POSTHOC), sau sửa A/B ước ~37–39%.
