# PAT — DD rev6 đầy đủ (đợt 4, 25/11/2026, job Taylor_20261125_063651) — sổ: dd_date 2026-11-17, rev 4

Báo cáo `REPORT_recheck_PAT.md` · khoá `assumptions_rev6.md` md5 `5207e413…` (trước khi chạy) · calc `calc/model_r6.py` (bọc model_r5 md5 f6cd2e0e, CONTROL 66.470,1 tái lập; run1=run2 md5 f40663ca) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` · proposal `LEDGER_PROPOSAL_PAT.json` (selfcheck sổ tạm 0 lỗi ×3 TZ; dry-run center_adj → rev5 OK). Mù giá khi dựng.

## Lệch luật đã xử lý
- **D4** (RONIC terminal = Ke): −1,44%. **Killer skeptic cũ** (ô H1/26 "sạch" → O2): bỏ, ô theo D như r4: −5,82%. Bước 0 khác đạt (r 13,5% Δ0, không holding, độ nhạy r tính từ mô hình).
- E15, E16 (nguyên văn), V3 (ADV tự đo: trung vị 0,588 tỷ, 64 phiên ⇒ giữ CK 10%), V5 (NARROW), V6 (D 0,46 < ln2, không cờ), V8, D3 (không có số ⇒ độ nhạy), D5 (FY2025 KT có) — đủ.

## Tâm / vùng (sau CK 10%)
| | rev3 sổ | rev6 | Δ |
|---|---|---|---|
| Tâm | 59.823 | **55.527** (trước CK 61.697) | **−7,18%** |
| P25–P75 | 41.000–74.900 | 40.485–67.228 | |
| Cổng 0,85×tâm | 50.850 | 47.198 | |
Tâm @ Ke 12,3%: 59.778 (+7,66%). **Nhãn:** giá 70.200 (17/11, kế thừa) **trên P75** (trước: trong vùng) ⇒ không biên an toàn, không mua — kết luận cũ giữ, nay đã kiểm lại sau khi làm đầy đủ (mọi biến thể chiều lên, kể cả E17 cao nhất 59.045 và Ke 12,3%, đều < 70.200).

## Skeptic r1 (DD_GENERAL, 0,89 USD): **INCONCLUSIVE / medium** — `skeptic/r1.json`
Tái lập mô hình đúng tới chữ số; xác nhận đọc lại cầm cố (130 ACB/199 BIDV là vay của chính PAT ⇒ ước −7,8% của skeptic cũ bị bác). Mở: hạn HĐ thuê đất, trách nhiệm pháp nhân Đ.235, capex môi trường, tăng trưởng không tái đầu tư (g=0 −8,47%). Đính chính chỉ văn bản (Phụ lục E), tâm 0% ⇒ xác nhận cơ học ⇒ **skeptic_final = REFUTED_OPEN**.

## Tâm kỳ vọng điều chỉnh (E17): **57.872** (dải 56.700–59.045; **+4,22%**), 2 hạng mục bậc B
#1 ô ở O2 (Q2/26 LNST% 21,2%) p0,5 × +6,18%; #2 giải phóng tồn kho 44,44 tỷ p0,5 × +2,27%; chạy tổ hợp mô hình. ⚠ Cả hai đều chiều lên; mọi rủi ro chiều xuống là C (có độ lớn, thiếu xác suất): **thuê đất hết ~2034 không gia hạn −28,7%** (2042: −11,5%), bảo đảm chéo 42,6 tỷ −2,76%, đình chỉ lò 6 tháng −2,72%, capex môi trường −36 đ/cp/tỷ. [LUẬT] r 12,3% +7,66%, g=0 −8,47%.
Bảng điều kiện đổi số (đầy đủ ở ADJ_CENTER): HĐ thuê đất/BCTC KT 2026 (tới −15.900) · BCTC Q4/2026 tồn kho+biên (+505/−515) · tố tụng pháp nhân (−1.500/6 tháng) · TM4 Q4 bảo đảm (0/−1.530) · NQ ĐHĐCĐ 2027 capex · tờ trình giá DLC · lãi huy động ±50bp (+3,0%/−2,8%).

## Rủi ro / việc mở
1. **Hạn HĐ thuê đất KCN Tằng Loỏng + quyền gia hạn** — lớn nhất; tra web 25/11 rỗng; cần BCTC KT 2026 thuyết minh hoặc CBTT/HĐ.
2. legal-vn: pháp nhân PAT có bị truy cứu Đ.235/Đ.76 BLHS không (chưa dispatch).
3. Đối chiếu BCTC Q3 gốc (PDF/ảnh p29/p31 không còn local).

## Khuyến nghị lớp: **REFUTED_OPEN + center_adj** — Mike ghi proposal rev4 rồi center_adj rev5. Không vị thế; nếu có ≤0,5% NAV (thanh khoản).
