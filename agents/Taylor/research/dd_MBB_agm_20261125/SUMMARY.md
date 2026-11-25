# MBB rev6' (25/11/2026, job Taylor_20261125_082754) — thay bản rev6 (job 080251)

**Tâm base 17.925 (vùng 12.719–23.215), k = 11,59%** (KTPL 9,03% + quỹ khác 2,56%). So với rev6 18.595 là −3,60%, so với sổ rev5 21.069 là −14,92%. Nhãn @19.250 vẫn **TRONG** (giá > tâm +7,4%). **Tâm điều chỉnh E17: 18.059 (17.709–18.678)**, dải đối xứng theo k.

- **Killer skeptic r2 "Quỹ khác: sử dụng" ĐÓNG, bậc A.** Dòng "Sử dụng các quỹ" làm giảm TỔNG VCSH ở cả 3 kỳ: 348.289 (2024), 620.313 (2025), 460.531 (9T26). Nguồn: KT HN 2025 TM26.1; Q3/26 TM22.1 HN + riêng, cân tổng. Không có đối ứng trong VCSH, không qua P&L. Chính sách TM4.24.4: quỹ từ LNST do ĐHĐCĐ duyệt.
- **Cả hai số:** không gồm quỹ khác = 18.595, có gồm = **17.925 (CHỌN)**.
- **Đã tính lại mọi độ nhạy trên rev6'** (REPORT_v2 §2):
  - ROE_T ±2pp: 15.979 / 19.871
  - RONIC>Ke: 19.913
  - HARD ABANDON: 16.163
  - Ke 12,3%: 20.095
  - Lãi huy động ±50bp: −790 / +853
  - Bỏ chênh terminal: 17.070
- **k thấp/cao:** 9,78% ⇒ 18.396; 12,56% ⇒ 17.674.
- **CAR 30/09: không có nguồn gốc** (thứ cấp: HN Q2 ~10,7%) ⇒ để ngoài Σ. Pháp lý sau 05/11: không thấy tin mới, chỉ WARNING.
- **Calc** `calc/calc_agm_v2.py`: run1 = run2 (md5 5ed5af00). CONTROL tái lập 21.069, vùng rev5, 18.595, 25.317, 18.969, 18.742/23.396.
- **Sổ tạm** = master + proposal, chạy với gốc nguồn chép thật vào /tmp:
  - 180 entry, 0 lỗi ×3 TZ;
  - dry-run center_adj → rev7 18.059, 181 entry, 0 lỗi ×3 TZ.
- **Trạng thái:** giữ REFUTED_OPEN. skeptic_verdict_path = skeptic/r2.json. CHƯA ghi sổ master, CHƯA merge.
