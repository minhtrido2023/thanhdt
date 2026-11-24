# quant-skeptic — CK holding v3 (24/11/2026, 1 vòng) — VERDICT: REFUTED / medium

Mike ghi lại từ hand-back của quant-skeptic (agentId ade53de970eca4d55). Read-only; chạy lại trong /tmp rồi xoá.

**Định tính ĐỨNG:** không có dải ≤20pp; 0% nằm trong dải. **Định lượng đầu trên SAI:** +23,0% (và mốc độ nhạy +23% gợi ý cho HHS) tựa vào lỗi double-count kiểu đòn 8 ở OGC/OCH chưa sửa. Sửa nhất quán ⇒ đầu trên ≈ **+14%**.

## Phát hiện chính — OCH phát hành riêng lẻ, OGC giữ tỷ lệ cũ
- OCH (con của OGC) phát hành riêng lẻ 130 tr CP (tỷ lệ 0,65, giá 10.000đ, 1,3E12), ex 07/10/2026; toàn lô về Leadvisors (39,39%). OGC giữ 111,19 tr ⇒ sở hữu thật còn **33,7%**.
- Calc: số CP OCH 330 tr từ 30/10 × tỷ lệ cũ 55,6% (KBS 31/12/2025) ⇒ SOTP OGC 580→1.164 tỷ ⇒ CK OGC 10–11/2026 +43%/+49% là ẢO.
- Sửa (33,7% + 1.300 tỷ vào VCSH OCH): CK OGC ≈ −14…−5% (10/2026), +3…+10% (11/2026). Trung vị tháng 10: 19,7→13,7%; 11: **23,0→14,4%**. Hull **−11,9…+14,4% (26,3pp)**, 0% ở phân vị 0,45. N và trung vị 1,49% không đổi.
- Báo cáo sai: §2d lấy OGC Δln SOTP +0,97 làm bằng chứng "mẹ giảm nhanh hơn rổ con" (chính là lỗi này); Hạn chế 4 "trên tập N không có ca nào" SAI — OCH(OGC), GIC(VSC, quyền mua 1:1), LBM(LHC) đều thuộc N; số CP GIC nhảy 25,45→13,33→NaN→25,45 tr.

## 6 câu hỏi
1. **PREREG có thật:** md5 khớp 7a7aef59…, viết 04:21:40 UTC trước lần calc đầu 04:24:02; LOCK 19/19. **5 chỗ làm khác PREREG chưa nêu:** (i) TREASURY_FIX không có trong PREREG (tác động −0,07pp); (ii) cộng tỷ lệ cùng ngày ex thay Π(1+r), đổi 04:48 SAU khi thấy kết quả ⇒ lỗi mới ở GAS (2 dòng Bonus 3% trùng thành ×1,06; ngoài N); (iii) ISS_FIX một chiều; (iv) §C2 "(c) N≥8 thì thay (a)" — code chỉ xét c1, c3 N=10 đạt đúng chữ (dải c3 −85,7…30,0 còn rộng hơn ⇒ kết luận không đổi); (v) LOO (d) dùng n≥10. Thiên lệch ngầm: PREREG viết sau khi biết số v2 và 5,63%; khung "HHS cần TRUNG TÂM" chọn đại lượng hẹp, trong khi định giá MỘT holding chịu cả phân tán riêng.
2. **Dải không bị chọn vì hẹp:** không ứng viên bị giấu/đổi. Hull không phải CI; bootstrap p5–p95 −26,9…+36,2% rộng hơn chính dải trung tâm. T_eff 0,20 đúng công thức (≈1 quan sát).
3. **4 lỗi:** PAN đã sửa đúng (41.778.416/0,2 = 208,89 tr; CP quỹ 7,40 tr) · T_eff đúng (ρ 0,956) · prescreen đã bỏ (stake KBS bị CŨ, không phải look-ahead) · con mỏng chạy độ nhạy đúng. Lỗi mới/còn sót: GAS cộng trùng, GLT TREASURY_FIX 9,17% khó là CP quỹ, SZL 0,76 tr chưa kiểm, OCH (trong N).
4. **KSF:** giữ theo quy tắc khai trước là đúng thủ tục. Bỏ KSF một mình (5,63%) là cắt một phía; bỏ cả hai mã tựa giá con mỏng (KSF đuôi dưới, CMX đuôi trên) thì trung vị vẫn **1,49%** ⇒ KSF không làm bẩn trung vị, nhưng kéo đầu thấp dải (03/2026: −11,9→−4,6% nếu bỏ). Trung vị đổi 1,5↔5,6% theo chẵn/lẻ N (CII chỉ cần thêm 1 tháng).
5. **Tái lập:** python3 (pandas 2.3.3) và $DNA_PYEXE (pandas 3) bit-exact (b8cf3c78 / a0ff4f43 / 8a06d01b); tính lại từ panel: N=13, 1,4946%, IQR −38,65…36,62, 9 điểm tháng khớp.
6. **Gợi ý HHS:** chiều "CK cao ⇒ giá trị HHS thấp" đúng. "Lạc quan rõ so với 23%" phóng đại (hiện tại đã sửa ≈14%). Đầu −12% là premium do tháng 03/2026 bị KSF kéo + mã cấu trúc (VIC/MVN/KSF/LHC), không giống HHS; nhóm giống HHS (c1, N=2) ở 11–49%. Dải −12/+23: sai đầu trên, nghiêng lạc quan.

## required_change (chưa làm — chờ user)
1. Tỷ lệ sở hữu PIT theo sự kiện phát hành riêng lẻ/quyền mua (OCH 33,7% từ 07/10/2026 + 1.300 tỷ VCSH OCH); kiểm số CP GIC/LBM; tính lại (d), hull, mốc độ nhạy.
2. Khử dòng trùng corporate_action trước khi cộng cùng ngày ex (GAS).
3. Ghi rõ 5 chỗ khác PREREG; áp (c) N≥8 đúng chữ.
4. Trình bày trung tâm "1,5–5,6% (theo chẵn/lẻ N)" + bootstrap. HHS: base 0% gắn nhãn đầu lạc quan; độ nhạy ≈ +6% / ≈ +14% (hiện tại, đang có xu hướng) / +37% (stress riêng một holding); bỏ đầu −12% trừ khi HHS có cấu trúc R1/R2.
5. Một vòng skeptic nữa sau khi sửa.
